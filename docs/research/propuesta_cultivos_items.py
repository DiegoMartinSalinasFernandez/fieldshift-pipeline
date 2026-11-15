"""Data Items exactos de NASS para los cultivos propuestos en T103 (copia del mecanismo de nass_mi_nd_conteo.py).

Pide a la interfaz web pública de Quick Stats (sin clave) un CSV por estado, cultivo y variable, de encuesta,
2000–2025, a nivel condado y estado. Los CSV quedan en la carpeta que se le pasa (fuera del repo) y no se vuelven
a bajar. Después resume, por estado y Data Item (= short_desc) con Domain TOTAL:
  - nivel condado: años con al menos un condado (sin OTHER COUNTIES), primer y último año, máximo de condados;
  - nivel estado (solo superficie sembrada y cosechada): media 2020–2025, el peso del cultivo en el estado.
El nivel condado se pide solo en ND, SD, MN y WI (más KS girasol y NE silo, frijol y girasol).

Uso:
  .venv/bin/python -X utf8 docs/research/propuesta_cultivos_items.py <carpeta_csv> > items.csv
"""
import csv
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests

QS = "https://quickstats.nass.usda.gov"
ESTADOS = {"IA": "IOWA", "IL": "ILLINOIS", "IN": "INDIANA", "OH": "OHIO", "NE": "NEBRASKA",
           "MN": "MINNESOTA", "KS": "KANSAS", "MO": "MISSOURI", "WI": "WISCONSIN", "SD": "SOUTH DAKOTA",
           "ND": "NORTH DAKOTA"}
# CORN se pide solo con util SILAGE (el grano ya está en el esquema)
COMMODITIES = {"CORN": {"util_practice_desc": "SILAGE"}, "WHEAT": {}, "SUNFLOWER": {}, "CANOLA": {},
               "BARLEY": {}, "BEANS": {}}
STATS = ["YIELD", "AREA PLANTED", "AREA HARVESTED", "PRODUCTION"]
ANIOS = [str(a) for a in range(2000, 2026)]
# Condado: solo donde el cultivo pesa (en el resto basta la superficie del estado), para que entre en el tiempo.
CONDADO = {"ND", "SD", "MN", "WI"}
CONDADO_EXTRA = {("KS", "SUNFLOWER"), ("NE", "BEANS"), ("NE", "CORN"), ("NE", "SUNFLOWER")}
UA = {"User-Agent": "Mozilla/5.0 (fieldshift-research)"}


def bajar(carpeta: Path, est: str, com: str, stat: str, nivel: str) -> Path:
    destino = carpeta / f"{est}_{com}_{stat.replace(' ', '_')}_{nivel}.csv"
    if destino.exists():
        return destino
    form = {"source_desc": "SURVEY", "sector_desc": "CROPS", "commodity_desc": com, "statisticcat_desc": stat,
            "agg_level_desc": nivel, "state_name": ESTADOS[est], "freq_desc": "ANNUAL",
            "reference_period_desc": "YEAR", **COMMODITIES[com]}
    form = list(form.items()) + [("year", a) for a in ANIOS]
    n = requests.post(QS + "/row_counts", data=form, headers=UA, timeout=120).json()["rowcnt"]
    if n == 0:
        destino.write_text("")
        return destino
    if n > 50000:
        raise RuntimeError(f"{destino.name}: {n} filas (> 50.000)")
    uuid = requests.post(QS + "/uuid/encode", data=form, headers=UA, timeout=120).json()
    r = requests.get(f"{QS}/data/spreadsheet/{uuid}.csv", headers=UA, timeout=300)
    r.raise_for_status()
    destino.write_bytes(r.content)
    time.sleep(0.3)
    return destino


def main() -> None:
    carpeta = Path(sys.argv[1])
    carpeta.mkdir(parents=True, exist_ok=True)
    cond = defaultdict(lambda: defaultdict(set))  # (est, item) -> anio -> condados
    estado = defaultdict(list)  # (est, item) -> valores 2020–2025
    for est in ESTADOS:
        for com in COMMODITIES:
            for stat in STATS:
                for nivel in ("COUNTY", "STATE"):
                    if nivel == "COUNTY" and est not in CONDADO and (est, com) not in CONDADO_EXTRA:
                        continue
                    if nivel == "STATE" and stat not in ("AREA PLANTED", "AREA HARVESTED"):
                        continue
                    try:
                        p = bajar(carpeta, est, com, stat, nivel)
                    except Exception as e:  # se anota y se sigue
                        print(f"# error {est} {com} {stat} {nivel}: {e}", file=sys.stderr)
                        continue
                    if p.stat().st_size == 0:
                        continue
                    with open(p, encoding="utf-8") as f:
                        for fila in csv.DictReader(f):
                            if fila["Domain"] != "TOTAL":
                                continue
                            item, val = fila["Data Item"], fila["Value"].strip()
                            if nivel == "COUNTY":
                                if fila["County"].startswith("OTHER") or fila["County ANSI"] == "":
                                    continue
                                if val.startswith("("):
                                    continue
                                cond[(est, item)][fila["Year"]].add(fila["County ANSI"])
                            elif fila["Year"] >= "2020" and not val.startswith("("):
                                estado[(est, item)].append(float(val.replace(",", "")))
    w = csv.writer(sys.stdout)
    w.writerow(["estado", "short_desc", "anios_condado", "desde", "hasta", "max_condados", "sin_2024",
                "media_estado_2020_2025"])
    for clave in sorted(set(cond) | set(estado)):
        est, item = clave
        anios = sorted(a for a, c in cond[clave].items() if c) if clave in cond else []
        vals = estado.get(clave, [])
        w.writerow([est, item, len(anios), anios[0] if anios else "", anios[-1] if anios else "",
                    max((len(c) for c in cond[clave].values()), default=0) if clave in cond else 0,
                    "si" if anios and "2024" not in anios else "",
                    round(sum(vals) / len(vals)) if vals else ""])


if __name__ == "__main__":
    main()
