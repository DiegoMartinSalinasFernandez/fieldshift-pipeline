"""Une los CSV procesados de todos los paquetes (CLAUDE.md §7).

- tabla_anual.csv: una fila por fips × anio × cultivo (las filas de produccion_anual.csv), con
  las columnas de clima_anual, rotacion_anual, fenologia_anual (por fips, anio),
  fenologia_estado (por fips_estado = fips[:2], anio, cultivo) y suelo_terreno_estatico (por fips).
- tabla_mensual.csv: unión externa de todos los *_mensual.csv por fips × anio × mes.

rotacion_secuencia.csv y practicas_censo.csv quedan aparte (otra granularidad).
Los valores se leen y escriben como texto para no cambiar su formato.

Uso: python src/merge.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "processed"

BASE_ANUAL = "cultivos/produccion_anual.csv"
# (archivo, claves de unión en el archivo, claves equivalentes en la tabla)
ANUALES = [
    ("clima/clima_anual.csv", ["fips", "anio"], ["fips", "anio"]),
    ("cultivos/rotacion_anual.csv", ["fips", "anio"], ["fips", "anio"]),
    ("vegetacion/fenologia_anual.csv", ["fips", "anio"], ["fips", "anio"]),
    ("cultivos/fenologia_estado.csv", ["fips_estado", "anio", "cultivo"], ["fips_estado", "anio", "cultivo"]),
    ("suelo_terreno/suelo_terreno_estatico.csv", ["fips"], ["fips"]),
]
MENSUALES = [
    "clima/clima_mensual.csv",
    "vegetacion/vegetacion_mensual.csv",
    "agua/agua_mensual.csv",
]
CLAVES_ANUAL = ["fips", "anio", "cultivo"]
CLAVES_MENSUAL = ["fips", "anio", "mes"]


def leer(rel: str) -> pd.DataFrame | None:
    p = PROC / rel
    if not p.exists():
        print(f"  aviso: falta {rel}, se omite")
        return None
    return pd.read_csv(p, dtype=str, keep_default_na=False, na_filter=False, encoding="utf-8")


def sin_duplicados(df: pd.DataFrame, claves: list[str], nombre: str) -> None:
    dup = df.duplicated(subset=claves)
    if dup.any():
        raise SystemExit(f"{nombre}: {int(dup.sum())} claves duplicadas en {claves}")


def renombrar_colisiones(df: pd.DataFrame, claves: list[str], existentes: set[str], paquete: str) -> pd.DataFrame:
    """Si una columna no clave ya está en la tabla, se le antepone el paquete."""
    ren = {c: f"{paquete}_{c}" for c in df.columns if c not in claves and c in existentes}
    if ren:
        print(f"  {paquete}: columnas renombradas por colisión {ren}")
    return df.rename(columns=ren)


def ordenar(df: pd.DataFrame, claves: list[str]) -> pd.DataFrame:
    tmp = df.assign(_anio=df["anio"].astype(int))
    orden = ["fips", "_anio"] + [c for c in claves if c not in ("fips", "anio")]
    return tmp.sort_values(orden, kind="mergesort").drop(columns="_anio").reset_index(drop=True)


def escribir(df: pd.DataFrame, nombre: str) -> None:
    salida = PROC / nombre
    tmp = salida.with_suffix(".csv.part")
    df.to_csv(tmp, index=False, encoding="utf-8", lineterminator="\n")
    tmp.replace(salida)
    print(f"  {nombre}: {len(df)} filas × {df.shape[1]} columnas")


def tabla_anual() -> pd.DataFrame:
    base = leer(BASE_ANUAL)
    if base is None:
        raise SystemExit(f"falta {BASE_ANUAL}: es la base de tabla_anual")
    sin_duplicados(base, CLAVES_ANUAL, BASE_ANUAL)
    n_base = len(base)
    tabla = base.assign(fips_estado=base["fips"].str[:2])
    for rel, claves, _ in ANUALES:
        df = leer(rel)
        if df is None:
            continue
        sin_duplicados(df, claves, rel)
        df = renombrar_colisiones(df, claves, set(tabla.columns), rel.split("/")[0])
        tabla = tabla.merge(df, on=claves, how="left", validate="many_to_one")
    if len(tabla) != n_base:
        raise SystemExit("tabla_anual cambió de cantidad de filas al unir")
    tabla = tabla.drop(columns="fips_estado").fillna("")
    sin_duplicados(tabla, CLAVES_ANUAL, "tabla_anual")
    return ordenar(tabla, CLAVES_ANUAL)


def tabla_mensual() -> pd.DataFrame:
    tabla = None
    for rel in MENSUALES:
        df = leer(rel)
        if df is None:
            continue
        sin_duplicados(df, CLAVES_MENSUAL, rel)
        if tabla is None:
            tabla = df
            continue
        df = renombrar_colisiones(df, CLAVES_MENSUAL, set(tabla.columns), rel.split("/")[0])
        tabla = tabla.merge(df, on=CLAVES_MENSUAL, how="outer", validate="one_to_one")
    if tabla is None:
        raise SystemExit("no hay archivos mensuales para unir")
    tabla = tabla.fillna("")
    sin_duplicados(tabla, CLAVES_MENSUAL, "tabla_mensual")
    return ordenar(tabla, CLAVES_MENSUAL)


def main() -> int:
    t0 = time.time()
    escribir(tabla_anual(), "tabla_anual.csv")
    escribir(tabla_mensual(), "tabla_mensual.csv")
    print(f"listo en {time.time() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
