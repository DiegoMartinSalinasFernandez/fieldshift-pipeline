"""Rendimiento de condado implícito en el Censo Agropecuario (producción / superficie cosechada).

Solo lee los archivos completos del Censo que ya están en data/raw/cultivos/nass/ (qs.census<anio>.txt.gz) y
escribe a stdout un CSV con el mínimo, el percentil 1, la mediana y el máximo por estado, cultivo y año censal.
No escribe nada en data/. Es una referencia para la propuesta de rangos (T048), no un CSV del contrato.

Uso:
    .venv/bin/python -X utf8 docs/research/rangos_estados_nuevos_censo.py [--min-acres 500] > /tmp/rangos_censo.csv

Advertencias:
- El Censo cuenta todas las explotaciones (no la muestra de la encuesta SURVEY): el rendimiento implícito no es el
  `rend_bu_ac` de Quick Stats SURVEY, aunque debería caer en el mismo orden.
- Mezcla riego y secano: el Censo de condado trae superficie regada, pero no producción regada.
- Condados con muy poca superficie dan rendimientos ruidosos: por eso el umbral --min-acres.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ESTADOS = {"IA", "IL", "IN", "OH", "NE", "MN", "KS"}
CULTIVOS = {  # cultivo: (short_desc producción, short_desc superficie cosechada)
    "maiz": ("CORN, GRAIN - PRODUCTION, MEASURED IN BU", "CORN, GRAIN - ACRES HARVESTED"),
    "soja": ("SOYBEANS - PRODUCTION, MEASURED IN BU", "SOYBEANS - ACRES HARVESTED"),
    "trigo_invierno": ("WHEAT, WINTER - PRODUCTION, MEASURED IN BU", "WHEAT, WINTER - ACRES HARVESTED"),
    "avena": ("OATS - PRODUCTION, MEASURED IN BU", "OATS - ACRES HARVESTED"),
}
RIEGO = {  # superficie regada, para la fracción regada del condado
    "maiz": "CORN, GRAIN, IRRIGATED - ACRES HARVESTED",
    "soja": "SOYBEANS, IRRIGATED - ACRES HARVESTED",
    "trigo_invierno": "WHEAT, WINTER, IRRIGATED - ACRES HARVESTED",
    "avena": "OATS, IRRIGATED - ACRES HARVESTED",
}


def _num(v: str) -> float | None:
    v = v.strip().replace(",", "")
    try:
        return float(v)
    except ValueError:  # (D), (Z), etc.
        return None


def leer(anio: int) -> dict:
    p = REPO / "data" / "raw" / "cultivos" / "nass" / f"qs.census{anio}.txt.gz"
    if not p.exists():
        print(f"falta {p}", file=sys.stderr)
        return {}
    buscados = {d for par in CULTIVOS.values() for d in par} | set(RIEGO.values())
    datos: dict = {}
    with gzip.open(p, "rt", encoding="utf-8", errors="replace") as f:
        r = csv.reader(f, delimiter="\t")
        h = next(r)
        i = {c: h.index(c) for c in ("SHORT_DESC", "DOMAIN_DESC", "AGG_LEVEL_DESC", "STATE_ALPHA",
                                     "STATE_FIPS_CODE", "COUNTY_CODE", "COUNTY_NAME", "YEAR", "VALUE")}
        for row in r:
            if (row[i["AGG_LEVEL_DESC"]] != "COUNTY" or row[i["DOMAIN_DESC"]] != "TOTAL"
                    or row[i["STATE_ALPHA"]] not in ESTADOS or row[i["SHORT_DESC"]] not in buscados
                    or row[i["YEAR"]] != str(anio) or row[i["COUNTY_CODE"]] == "998"):
                continue
            fips = row[i["STATE_FIPS_CODE"]].zfill(2) + row[i["COUNTY_CODE"]].zfill(3)
            datos[(row[i["STATE_ALPHA"]], fips, row[i["COUNTY_NAME"]], row[i["SHORT_DESC"]])] = _num(row[i["VALUE"]])
    return datos


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-acres", type=float, default=500)
    ap.add_argument("--anios", default="2012,2017,2022")
    a = ap.parse_args()
    w = csv.writer(sys.stdout)
    w.writerow(["anio", "estado", "cultivo", "n_condados", "min_bu_ac", "condado_min", "frac_riego_min",
                "p01_bu_ac", "mediana_bu_ac", "max_bu_ac", "condado_max", "frac_riego_max"])
    for anio in [int(x) for x in a.anios.split(",")]:
        d = leer(anio)
        for est in sorted(ESTADOS):
            for cult, (dprod, dsup) in CULTIVOS.items():
                filas = []
                for (e, fips, nom, desc), sup in d.items():
                    if e != est or desc != dsup or not sup or sup < a.min_acres:
                        continue
                    prod = d.get((e, fips, nom, dprod))
                    if prod is None:
                        continue
                    riego = d.get((e, fips, nom, RIEGO[cult])) or 0.0
                    filas.append((prod / sup, f"{nom} ({fips})", riego / sup))
                if not filas:
                    continue
                filas.sort()
                rends = [f[0] for f in filas]
                p01 = rends[max(0, int(round(0.01 * (len(rends) - 1))))]
                w.writerow([anio, est, cult, len(filas), round(filas[0][0], 1), filas[0][1], round(filas[0][2], 2),
                            round(p01, 1), round(statistics.median(rends), 1), round(filas[-1][0], 1),
                            filas[-1][1], round(filas[-1][2], 2)])


if __name__ == "__main__":
    main()
