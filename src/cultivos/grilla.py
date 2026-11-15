"""Grilla completa de `produccion_anual.csv`: una fila por fips × anio × cultivo (T138).

NASS solo publica los condados con dato: el resto lo saca de la tabla y lo suma a "OTHER (COMBINED)
COUNTIES" (docs/research/nass_2024_2025.md). En 2024–2025 falta el rendimiento del 35–40 % de los
condados. Este módulo completa la grilla con filas de celdas vacías y agrega la columna `fila_nass`:

- `fila_nass` = 1: la fila viene de NASS (tiene al menos una variable o un `flag_nass`).
- `fila_nass` = 0: NASS no publicó nada para ese condado, año y cultivo; la fila se completó vacía.

Las columnas de antes no cambian (`flag_nass` sigue igual); `fila_nass` va al final.
Retenido hasta el OK del humano a la fila 7 de coordinacion/para_decidir.md.

Uso, sobre un `produccion_anual.csv` ya hecho (lo reescribe; es idempotente):

    .venv/bin/python -X utf8 src/cultivos/grilla.py [ruta_csv] [--condados ruta_condados_csv]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

CLAVES = ["fips", "anio", "cultivo"]


def completar_grilla(prod: pd.DataFrame, fips: list[str], anios: list[int],
                     cultivos: list[str]) -> pd.DataFrame:
    """Devuelve `prod` con una fila por cada fips × anio × cultivo y la columna `fila_nass` (1/0).

    Si `prod` ya trae `fila_nass` (corrida anterior), se descartan las filas completadas y se rearma.
    Filas de `prod` fuera de la grilla (otro fips, año o cultivo) se conservan tal cual.
    """
    prod = prod.copy()
    prod["fips"] = prod["fips"].astype(str).str.zfill(5)
    prod["anio"] = prod["anio"].astype(int)
    if "fila_nass" in prod.columns:
        prod = prod[prod["fila_nass"].astype(int) == 1].drop(columns="fila_nass")
    cols = list(prod.columns)
    if prod.duplicated(CLAVES).any():
        raise ValueError("produccion_anual.csv tiene claves fips, anio, cultivo duplicadas")
    grilla = pd.MultiIndex.from_product(
        [sorted({str(f).zfill(5) for f in fips}), sorted({int(a) for a in anios}), sorted(set(cultivos))],
        names=CLAVES).to_frame(index=False)
    prod["fila_nass"] = 1
    out = grilla.merge(prod, on=CLAVES, how="outer")
    out["fila_nass"] = out["fila_nass"].fillna(0).astype(int)
    if "flag_nass" in out.columns:
        out["flag_nass"] = out["flag_nass"].astype("string")
    out = out[cols + ["fila_nass"]]
    return out.sort_values(CLAVES).reset_index(drop=True)


def resumen(out: pd.DataFrame) -> pd.DataFrame:
    """Filas completadas (fila_nass = 0) por estado y año, y el total de filas."""
    d = out.assign(estado=out["fips"].str[:2])
    g = d.groupby(["estado", "anio"])["fila_nass"]
    return pd.DataFrame({"filas": g.size(), "de_nass": g.sum(),
                         "completadas": g.size() - g.sum()}).reset_index()


def completar_desde_config(prod: pd.DataFrame, condados: str | Path | None = None) -> pd.DataFrame:
    """`completar_grilla` con los fips de condados.csv (estados de config.yaml), el período y los cultivos."""
    from src.common.config import cargar_config, estados_config

    cfg = cargar_config()
    per = cfg["periodo"]
    fips_estados = {str(v["fips"]).zfill(2) for v in estados_config().values()}
    cond = pd.read_csv(condados or REPO / "data" / "reference" / "condados.csv", dtype={"fips": str})
    fips = [f for f in cond["fips"].str.zfill(5) if f[:2] in fips_estados]
    anios = list(range(int(per["anio_inicio"]), int(per["anio_fin"]) + 1))
    return completar_grilla(prod, fips, anios, list(cfg["cultivos"]))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("csv", nargs="?", default=str(REPO / "data" / "processed" / "cultivos"
                                                  / "produccion_anual.csv"))
    ap.add_argument("--condados", default=str(REPO / "data" / "reference" / "condados.csv"))
    ap.add_argument("--resumen", help="CSV donde guardar las filas completadas por estado y año")
    a = ap.parse_args(argv)
    prod = pd.read_csv(a.csv, dtype={"fips": str, "flag_nass": str}, keep_default_na=False,
                       na_values=[""])
    out = completar_desde_config(prod, a.condados)
    tmp = Path(a.csv).with_suffix(".part")
    out.to_csv(tmp, index=False, encoding="utf-8")
    tmp.replace(a.csv)
    r = resumen(out)
    if a.resumen:
        r.to_csv(a.resumen, index=False, encoding="utf-8")
    print(f"{a.csv}: {len(out)} filas ({int((out['fila_nass'] == 0).sum())} completadas)")


if __name__ == "__main__":
    main()
