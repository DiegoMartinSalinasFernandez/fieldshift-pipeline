"""Cobertura de condados de NASS por estado y año (tarea T084; problema 1 de docs/qa/oh_ne_mn.md).

Solo lee. Para maíz y soja (`<CULTIVO> - ACRES PLANTED`, SURVEY, año completo, dominio TOTAL), por estado y año:
- condados con superficie sembrada publicada en Quick Stats (sin la fila 998 ni los `(D)`);
- % de la superficie sembrada del estado que NASS junta en "OTHER (COMBINED) COUNTIES" (county_code 998);
- % de la superficie del estado que suman los condados publicados;
- si se pasa una carpeta con `produccion_anual.csv` (zips de los releases descomprimidos), los condados con
  `sup_sembrada_ac` en ese CSV, para comparar con Quick Stats.

Uso:
  .venv/bin/python -X utf8 docs/datasets/cobertura_nass.py data/entregas/nass_qa/qs.crops_<fecha>.txt.gz \
      [--csv data/entregas/.../produccion_anual.csv ...] [--salida data/entregas/cobertura_nass.csv]

Imprime las tablas en Markdown (las que se copian a docs/datasets/cultivos.md).
"""
from __future__ import annotations

import argparse
import gzip
from collections import defaultdict
from pathlib import Path

import pandas as pd

# Los 7 estados con release o datos en el repo (CLAUDE.md §2), en el orden del config.
ESTADOS = {"IA": "19", "IL": "17", "IN": "18", "OH": "39", "NE": "31", "MN": "27", "KS": "20"}
CULTIVOS = {"CORN - ACRES PLANTED": "maiz", "SOYBEANS - ACRES PLANTED": "soja"}
ANIOS = range(2000, 2026)


def numero(texto: str) -> float | None:
    t = texto.strip().replace(",", "")
    try:
        return float(t)
    except ValueError:
        return None  # (D), (Z), (NA), etc.


def leer_quickstats(ruta: Path) -> pd.DataFrame:
    filas = []
    with gzip.open(ruta, "rt", encoding="utf-8", errors="replace") as f:
        cab = f.readline().rstrip("\n").split("\t")
        i = {c: cab.index(c) for c in cab}
        for linea in f:
            if "ACRES PLANTED" not in linea or not linea.startswith("SURVEY"):
                continue
            c = linea.rstrip("\n").split("\t")
            if c[i["SHORT_DESC"]] not in CULTIVOS or c[i["STATE_ALPHA"]] not in ESTADOS:
                continue
            if c[i["DOMAIN_DESC"]] != "TOTAL" or c[i["REFERENCE_PERIOD_DESC"]] != "YEAR":
                continue
            nivel = c[i["AGG_LEVEL_DESC"]]
            if nivel not in ("COUNTY", "STATE"):
                continue
            anio = int(c[i["YEAR"]])
            if anio not in ANIOS:
                continue
            filas.append({
                "estado": c[i["STATE_ALPHA"]], "cultivo": CULTIVOS[c[i["SHORT_DESC"]]], "anio": anio,
                "nivel": nivel, "county_code": c[i["COUNTY_CODE"]], "valor": numero(c[i["VALUE"]]),
                "crudo": c[i["VALUE"]].strip(),
            })
    return pd.DataFrame(filas).drop_duplicates(["estado", "cultivo", "anio", "nivel", "county_code"])


def resumen(qs: pd.DataFrame, csvs: list[Path]) -> pd.DataFrame:
    cond = qs[qs.nivel == "COUNTY"]
    est = qs[qs.nivel == "STATE"].set_index(["estado", "cultivo", "anio"])["valor"]
    pub = cond[(cond.county_code != "998") & cond.valor.notna()]
    otros = cond[cond.county_code == "998"].set_index(["estado", "cultivo", "anio"])["valor"]
    g = pub.groupby(["estado", "cultivo", "anio"])
    r = pd.DataFrame({"n_condados_qs": g.size(), "suma_condados_ac": g.valor.sum()})
    ocultos = cond[(cond.county_code != "998") & cond.valor.isna()].groupby(["estado", "cultivo", "anio"]).size()
    r = r.reindex(pd.MultiIndex.from_product([list(ESTADOS), list(CULTIVOS.values()), list(ANIOS)],
                                             names=["estado", "cultivo", "anio"]))
    r["n_ocultos_qs"] = ocultos.reindex(r.index).fillna(0).astype(int)
    r["estado_ac"] = est.reindex(r.index)
    r["otros_998_ac"] = otros.reindex(r.index)
    r["pct_998"] = 100 * r.otros_998_ac.fillna(0) / r.estado_ac
    r["pct_suma_condados"] = 100 * r.suma_condados_ac / r.estado_ac
    if csvs:
        fips_a_estado = {v: k for k, v in ESTADOS.items()}
        p = pd.concat(pd.read_csv(c, dtype={"fips": str}) for c in csvs)
        p = p[p.cultivo.isin(["maiz", "soja"]) & p.sup_sembrada_ac.notna()]
        p["estado"] = p.fips.str[:2].map(fips_a_estado)
        n = p.groupby(["estado", "cultivo", "anio"]).fips.nunique()
        r["n_condados_csv"] = n.reindex(r.index)
    return r.reset_index()


def tablas_md(r: pd.DataFrame) -> str:
    out = []
    for cultivo in ("maiz", "soja"):
        s = r[r.cultivo == cultivo]
        n = s.pivot(index="anio", columns="estado", values="n_condados_qs")[list(ESTADOS)]
        p = s.pivot(index="anio", columns="estado", values="pct_998")[list(ESTADOS)]
        out.append(f"\n{cultivo}: condados publicados (% de la superficie del estado en la fila 998)\n")
        out.append("| anio | " + " | ".join(ESTADOS) + " |")
        out.append("|---|" + "---|" * len(ESTADOS))
        for anio in n.index:
            celdas = []
            for e in ESTADOS:
                nn, pp = n.at[anio, e], p.at[anio, e]
                if pd.isna(nn):
                    celdas.append("—")
                else:
                    celdas.append(f"{int(nn)} ({pp:.1f})".replace(".", ",") if pd.notna(pp) else f"{int(nn)}")
            out.append(f"| {anio} | " + " | ".join(celdas) + " |")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("quickstats", type=Path)
    ap.add_argument("--csv", type=Path, nargs="*", default=[])
    ap.add_argument("--salida", type=Path)
    a = ap.parse_args()
    r = resumen(leer_quickstats(a.quickstats), a.csv)
    if a.salida:
        r.to_csv(a.salida, index=False)
    print(tablas_md(r))
    if "n_condados_csv" in r:
        d = r[r.n_condados_csv.notna() & (r.n_condados_csv != r.n_condados_qs)]
        print(f"\nfilas con distinto número de condados entre el CSV y Quick Stats: {len(d)}")
        if len(d):
            print(d.to_string(index=False))
    print("\nmín. % suma de condados / estado, 2018-2025:")
    print(r[r.anio >= 2018].groupby(["estado", "cultivo"]).pct_suma_condados.min().round(1).unstack().to_string())


if __name__ == "__main__":
    main()
