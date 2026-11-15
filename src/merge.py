"""Une los CSV procesados de todos los paquetes (CLAUDE.md §7).

- tabla_anual.csv: una fila por fips × anio × cultivo (las filas de produccion_anual.csv), con
  las columnas de clima_anual, rotacion_anual, fenologia_anual, paisaje_anual, teledeteccion_anual
  (por fips, anio), fenologia_estado y economia_anual + economia_forrajes_anual (por
  fips_estado = fips[:2], anio, cultivo), suelo_terreno_estatico (por fips) y practicas_censo (el
  último censo con anio_censo <= anio, más la columna anio_censo_ref; antes del primer censo, vacío).
- tabla_mensual.csv: unión externa de clima, vegetacion, agua, nldas y ecostress *_mensual.csv por
  fips × anio × mes.

Si un archivo no está en data/processed/ se avisa y se sigue sin él.
rotacion_secuencia.csv queda aparte (ventanas de 8 años; docs/research/merge_faltantes.md §3).

Choques de nombres (docs/datasets/merge.md): las columnas que ya existen en la tabla no cambian;
la columna nueva que choca lleva el paquete adelante (`economia_flag_nass`). Si ese nombre también
choca, se usa el nombre del archivo (`economia_forrajes_anual_flag_nass`) y, si aun así choca, error.
Las columnas de NOMBRES_GENERICOS (`frac_pixeles_validos`) llevan siempre el prefijo del paquete,
porque solas no dicen de qué fuente son.
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
    # T136 (para_decidir #27): paquetes nuevos, siempre después de los de arriba para que las columnas
    # que ya salían no cambien de nombre ni de lugar.
    (("economia/economia_anual.csv", "economia/economia_forrajes_anual.csv"),
     ["fips_estado", "anio", "cultivo"], ["fips_estado", "anio", "cultivo"]),
    ("paisaje/paisaje_anual.csv", ["fips", "anio"], ["fips", "anio"]),
    ("teledeteccion/teledeteccion_anual.csv", ["fips", "anio"], ["fips", "anio"]),
]
# Unión "as-of": cada anio toma el último censo con anio_censo <= anio (sin datos del futuro).
CENSO = "cultivos/practicas_censo.csv"
COL_CENSO_REF = "anio_censo_ref"
MENSUALES = [
    "clima/clima_mensual.csv",
    "vegetacion/vegetacion_mensual.csv",
    "agua/agua_mensual.csv",
    "nldas/nldas_mensual.csv",
    "ecostress/ecostress_mensual.csv",
]
# Columnas que no dicen de qué fuente son: en los paquetes nuevos llevan siempre el prefijo del paquete.
NOMBRES_GENERICOS = {"frac_pixeles_validos"}
N_ANUALES_ORIGINALES = 5  # los de antes de T136: sus columnas no cambian de nombre
N_MENSUALES_ORIGINALES = 3
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


def leer_bloque(rels: tuple[str, ...], claves: list[str]) -> pd.DataFrame | None:
    """Apila por filas archivos con las mismas claves (economia_anual + economia_forrajes_anual).

    Así `flag_nass` queda en una sola columna y no se parte en `_x` / `_y`. Las claves no se pueden
    repetir entre los archivos (se chequea después con sin_duplicados).
    """
    partes = []
    for rel in rels:
        df = leer(rel)
        if df is not None:
            sin_duplicados(df, claves, rel)
            partes.append(df)
    if not partes:
        return None
    return pd.concat(partes, ignore_index=True, sort=False).fillna("")


def renombrar_colisiones(df: pd.DataFrame, claves: list[str], existentes: set[str], paquete: str,
                         archivo: str | None = None, genericos: set[str] = frozenset()) -> pd.DataFrame:
    """Si una columna no clave ya está en la tabla (o es genérica), se le antepone el paquete.

    Las columnas que ya están en la tabla nunca cambian. Si `<paquete>_<col>` también existe, se usa
    `<archivo>_<col>` (nombre del archivo sin .csv); si también existe, corta con error.
    """
    ren = {}
    for c in df.columns:
        if c in claves or (c not in existentes and c not in genericos):
            continue
        for pref in (paquete, archivo):
            if pref and f"{pref}_{c}" not in existentes and f"{pref}_{c}" not in df.columns:
                ren[c] = f"{pref}_{c}"
                break
        else:
            raise SystemExit(f"{paquete}: la columna {c} choca y no se encontró un nombre libre")
    if ren:
        print(f"  {paquete}: columnas renombradas {ren}")
    return df.rename(columns=ren)


def unir_censo(tabla: pd.DataFrame) -> pd.DataFrame:
    """Suma practicas_censo.csv: para cada fila, el último censo del condado con anio_censo <= anio."""
    censo = leer(CENSO)
    if censo is None:
        return tabla
    sin_duplicados(censo, ["fips", "anio_censo"], CENSO)
    censo = censo.rename(columns={"anio_censo": COL_CENSO_REF})
    censo = renombrar_colisiones(censo, ["fips", COL_CENSO_REF], set(tabla.columns), "cultivos",
                                 "practicas_censo")
    izq = tabla.assign(_fila=range(len(tabla)), _anio=tabla["anio"].astype(int)).sort_values("_anio")
    der = censo.assign(_anio=censo[COL_CENSO_REF].astype(int)).sort_values("_anio")
    unida = pd.merge_asof(izq, der, on="_anio", by="fips", direction="backward", allow_exact_matches=True)
    return unida.sort_values("_fila").drop(columns=["_fila", "_anio"]).reset_index(drop=True)


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
    for i, (rel, claves, _) in enumerate(ANUALES):
        rels = rel if isinstance(rel, tuple) else (rel,)
        df = leer_bloque(rels, claves)
        if df is None:
            continue
        nombre = " + ".join(rels)
        sin_duplicados(df, claves, nombre)
        paquete = rels[0].split("/")[0]
        nuevo = i >= N_ANUALES_ORIGINALES
        df = renombrar_colisiones(df, claves, set(tabla.columns), paquete,
                                  Path(rels[-1]).stem if nuevo else None,
                                  NOMBRES_GENERICOS if nuevo else set())
        tabla = tabla.merge(df, on=claves, how="left", validate="many_to_one")
    tabla = unir_censo(tabla)
    if len(tabla) != n_base:
        raise SystemExit("tabla_anual cambió de cantidad de filas al unir")
    tabla = tabla.drop(columns="fips_estado").fillna("")
    sin_duplicados(tabla, CLAVES_ANUAL, "tabla_anual")
    return ordenar(tabla, CLAVES_ANUAL)


def tabla_mensual() -> pd.DataFrame:
    tabla = None
    for i, rel in enumerate(MENSUALES):
        df = leer(rel)
        if df is None:
            continue
        sin_duplicados(df, CLAVES_MENSUAL, rel)
        if tabla is None:
            tabla = df
            continue
        nuevo = i >= N_MENSUALES_ORIGINALES
        df = renombrar_colisiones(df, CLAVES_MENSUAL, set(tabla.columns), rel.split("/")[0],
                                  Path(rel).stem if nuevo else None, NOMBRES_GENERICOS if nuevo else set())
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
