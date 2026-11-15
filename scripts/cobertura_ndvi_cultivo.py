"""Cobertura de ndvi_maiz / ndvi_soja por estado y año, y cuánto se ganaría con otro umbral de pureza.

Script de análisis (T085): solo lee, no escribe en data/ ni cambia el pipeline.

1. Con data/processed/vegetacion/vegetacion_16d.csv: % de condado-fechas con ndvi_maiz y con ndvi_soja,
   por estado (2 primeros dígitos de fips) y año, 2008–2025.
2. Con --umbral (necesita data/raw/vegetacion/mod13q1/ y data/reference/mascara_<cultivo>_<anio>.tif):
   cuenta, para cada condado-fecha, si hay al menos un píxel MODIS válido con fracción del cultivo
   >= 0,75 (umbral actual) y >= el umbral alternativo. Usa las mismas funciones que
   src/vegetacion/process.py (misma grilla, mismo filtro de calidad, misma fracción del CDL), así que
   la columna "_075" tiene que coincidir con el CSV procesado.

Uso:
  .venv/bin/python -X utf8 scripts/cobertura_ndvi_cultivo.py                   # solo la tabla 1
  .venv/bin/python -X utf8 scripts/cobertura_ndvi_cultivo.py --umbral 0.5      # tabla 1 + propuesta
  (con --anios 2012,2020 se limita la parte 2 a esos años; es la parte lenta)
Salida: tablas markdown por pantalla, listas para pegar en docs/datasets/vegetacion.md.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

ESTADOS = {"17": "IL", "18": "IN", "19": "IA", "20": "KS", "27": "MN", "31": "NE", "39": "OH"}
CULTIVOS = ("maiz", "soja")


def tabla_cobertura() -> pd.DataFrame:
    ruta = REPO / "data" / "processed" / "vegetacion" / "vegetacion_16d.csv"
    if not ruta.exists():
        sys.exit(f"no está {ruta.relative_to(REPO)}: bajá el release de tus estados primero")
    d = pd.read_csv(ruta, dtype={"fips": str}, usecols=["fips", "anio", "ndvi_maiz", "ndvi_soja"])
    d = d[(d["anio"] >= 2008) & (d["anio"] <= 2025)]
    d["estado"] = d["fips"].str[:2].map(ESTADOS)
    g = d.groupby(["estado", "anio"]).agg(n=("fips", "size"),
                                          maiz=("ndvi_maiz", lambda s: 100 * s.notna().mean()),
                                          soja=("ndvi_soja", lambda s: 100 * s.notna().mean()))
    return g.round(1).reset_index()


def tabla_umbral(umbral: float, anios: set[int] | None) -> pd.DataFrame:
    from src.vegetacion import process as P  # mismas funciones que el pipeline
    import rasterio

    zonas = P.Zonas(P.condados())
    cult = P.Cultivos()
    fips = zonas.gdf["fips"].to_numpy()
    # por (fecha): conteo de píxeles válidos con fracción >= 0,75 y >= umbral, por condado
    acc = defaultdict(lambda: defaultdict(lambda: np.zeros(zonas.n + 1)))
    ultimo = {}
    for p in sorted((P.RAW / "mod13q1").rglob("*.tif"), key=lambda x: x.name):
        ultimo[(P.fecha_item(p.name), P.tesela(p.name))] = p
    anio_prev = None
    for p in sorted(ultimo.values(), key=lambda x: x.name):
        f = P.fecha_item(p.name)
        if f.year < 2008 or (anios and f.year not in anios):
            continue
        if anio_prev is not None and f.year != anio_prev:
            cult.liberar(anio_prev)
        anio_prev = f.year
        with rasterio.open(p) as src:
            z = zonas.get(src)
            valido, _ = P.validos_mod13(src.read())
            base = valido & (z > 0)
            for c in CULTIVOS:
                fr = cult.frac(c, f.year, src)
                if fr is None:
                    continue
                for nombre, u in (("075", P.UMBRAL_CULTIVO), ("alt", umbral)):
                    m = base & (fr >= u)
                    acc[f][f"{c}_{nombre}"] += np.bincount(z[m], minlength=zonas.n + 1)
    filas = []
    for f, a in acc.items():
        d = pd.DataFrame({"fips": fips, "anio": f.year})
        for c in CULTIVOS:
            for nombre in ("075", "alt"):
                k = f"{c}_{nombre}"
                d[k] = (a[k][1:] > 0) if k in a else False
        filas.append(d)
    if not filas:
        sys.exit("no hay compuestos de MOD13Q1 o máscaras del CDL: no se pudo medir el umbral alternativo")
    d = pd.concat(filas, ignore_index=True)
    d["estado"] = d["fips"].str[:2].map(ESTADOS)
    cols = [f"{c}_{n}" for c in CULTIVOS for n in ("075", "alt")]
    g = d.groupby(["estado", "anio"])[cols].sum().astype(int)
    g.insert(0, "n", d.groupby(["estado", "anio"]).size())
    for c in CULTIVOS:
        g[f"{c}_ganados"] = g[f"{c}_alt"] - g[f"{c}_075"]
    return g.reset_index()


def a_markdown(d: pd.DataFrame) -> str:
    cab = "| " + " | ".join(d.columns) + " |\n|" + "---|" * len(d.columns) + "\n"
    return cab + "\n".join("| " + " | ".join(str(v) for v in fila) + " |" for fila in d.itertuples(index=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--umbral", type=float, help="umbral alternativo de pureza, por ejemplo 0.5")
    ap.add_argument("--anios", help="años para la parte 2, separados por coma")
    a = ap.parse_args()
    print("## % de condado-fechas con ndvi_maiz / ndvi_soja (vegetacion_16d.csv)\n")
    print(a_markdown(tabla_cobertura()))
    if a.umbral is not None:
        anios = {int(x) for x in a.anios.split(",")} if a.anios else None
        print(f"\n## Condado-fechas con al menos un píxel válido: umbral 0,75 contra {a.umbral}\n")
        print(a_markdown(tabla_umbral(a.umbral, anios)))


if __name__ == "__main__":
    main()
