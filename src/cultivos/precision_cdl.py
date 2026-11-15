"""Tabla de referencia de la precisión del CDL por estado, año y clase (T133, para_decidir #13).

Junta en `data/reference/cdl_precision.csv` lo que ya sacaron los extractores de research de las fuentes
oficiales de NASS (metadatos FGDC en HTML para 2008–2023 y `CDL_<año>_accuracy_assessments.zip` para
2024–2025):

  docs/research/cdl_precision_extraer.py          IA, IL, IN, OH, NE, MN, KS  (T024) -> cdl_precision.csv
  docs/research/cdl_precision_mo_wi_sd_extraer.py MO, WI, SD                  (T064) -> cdl_precision_mo_wi_sd.csv
  docs/research/cdl_precision_mi_nd_extraer.py    MI, ND                      (T068) -> cdl_precision_mi_nd.csv
  docs/research/cdl_precision_ky_extraer.py       KY                          (T078) -> cdl_precision_ky.csv

No inventa nada: renombra, pone `fips_estado` y el corte metodológico de la validación, y controla claves y
rangos. Las clases sin fila en la tabla de NASS de ese estado y año quedan con los valores vacíos.

Uso:
  python -X utf8 src/cultivos/precision_cdl.py                  # arma la tabla con los CSV de docs/research/
  python -X utf8 src/cultivos/precision_cdl.py --rehacer <dir>  # antes corre los 4 extractores (baja de NASS
                                                                # a <dir>, fuera del repo; ~1.000 HTML y 2 zip
                                                                # de ~75 MB; necesita openpyxl)
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
RESEARCH = REPO / "docs" / "research"
SALIDA = REPO / "data" / "reference" / "cdl_precision.csv"

# (CSV de research, extractor que lo arma). El orden es el de las tareas de research.
FUENTES = [
    ("cdl_precision.csv", "cdl_precision_extraer.py"),
    ("cdl_precision_mo_wi_sd.csv", "cdl_precision_mo_wi_sd_extraer.py"),
    ("cdl_precision_mi_nd.csv", "cdl_precision_mi_nd_extraer.py"),
    ("cdl_precision_ky.csv", "cdl_precision_ky_extraer.py"),
]

# Códigos FIPS de estado (U.S. Census Bureau). config.yaml solo trae los 7 del proyecto; research cubre 13.
FIPS_ESTADO = {"IA": "19", "IL": "17", "IN": "18", "OH": "39", "NE": "31", "MN": "27", "KS": "20",
               "MO": "29", "WI": "55", "SD": "46", "MI": "26", "ND": "38", "KY": "21"}

# Nombre en research -> nombre en la tabla de referencia.
RENOMBRES = {
    "codigo_cdl": "clase_cdl",
    "cultivo": "nombre",
    "precision_productor_pct": "exactitud_productor_pct",
    "precision_usuario_pct": "exactitud_usuario_pct",
    "px_correctos": "px_correctos_validacion",
    "global_cultivos_fsa_pct": "exactitud_global_cultivos_fsa_pct",
    "kappa_global_fsa": "kappa_global_cultivos_fsa",
}
COLUMNAS = ["fips_estado", "anio", "clase_cdl", "estado", "nombre", "exactitud_productor_pct",
            "exactitud_usuario_pct", "px_correctos_validacion", "exactitud_global_cultivos_fsa_pct",
            "kappa_global_cultivos_fsa", "metodo_validacion", "fuente"]
CLAVES = ["fips_estado", "anio", "clase_cdl"]
PCTS = ["exactitud_productor_pct", "exactitud_usuario_pct", "exactitud_global_cultivos_fsa_pct"]


def metodo_validacion(anio: int) -> str:
    """Corte metodológico de la validación de NASS (docs/research/cdl_precision.md, sección 2)."""
    if anio <= 2016:
        return "buffer_30m"          # polígonos FSA con buffer interno de 30 m: precisión algo inflada
    if anio <= 2023:
        return "sin_buffer"          # sin buffer: ~6–7 puntos menos de precisión global que 2016
    return "muestreo_2024"           # CDL a 10 m y muestreo proporcional (cultivo/no cultivo, tamaño)


def armar(research: Path = RESEARCH, fuentes=FUENTES) -> pd.DataFrame:
    """Une los CSV de research en la tabla de referencia. Corta si falta un CSV o si algo no cierra."""
    partes = []
    for csv_, _ in fuentes:
        ruta = research / csv_
        if not ruta.exists():
            raise FileNotFoundError(f"falta {ruta} (correr su extractor o usar --rehacer)")
        partes.append(pd.read_csv(ruta, dtype={"estado": str, "cultivo": str, "fuente": str}))
    df = pd.concat(partes, ignore_index=True).rename(columns=RENOMBRES)
    sin_fips = sorted(set(df["estado"]) - set(FIPS_ESTADO))
    if sin_fips:
        raise ValueError(f"estados sin código FIPS: {sin_fips}")
    df["fips_estado"] = df["estado"].map(FIPS_ESTADO)
    df["anio"] = df["anio"].astype(int)
    df["clase_cdl"] = df["clase_cdl"].astype(int)
    df["px_correctos_validacion"] = df["px_correctos_validacion"].astype("Int64")
    df["metodo_validacion"] = df["anio"].map(metodo_validacion)
    df = df[COLUMNAS].sort_values(CLAVES).reset_index(drop=True)
    errores = validar(df)
    if errores:
        raise ValueError("; ".join(errores))
    return df


def validar(df: pd.DataFrame) -> list[str]:
    """Claves únicas, fips_estado de 2 dígitos y porcentajes entre 0 y 100."""
    errores = []
    dup = df.duplicated(CLAVES)
    if dup.any():
        errores.append(f"{int(dup.sum())} claves repetidas, p. ej. {df.loc[dup, CLAVES].iloc[0].tolist()}")
    if not df["fips_estado"].str.fullmatch(r"\d{2}").all():
        errores.append("fips_estado que no son de 2 dígitos")
    for c in PCTS:
        v = df[c].dropna()
        if ((v < 0) | (v > 100)).any():
            errores.append(f"{c} fuera de 0–100")
    k = df["kappa_global_cultivos_fsa"].dropna()
    if ((k < -1) | (k > 1)).any():
        errores.append("kappa_global_cultivos_fsa fuera de −1–1")
    return errores


def de_estados(df: pd.DataFrame, estados) -> pd.DataFrame:
    """Solo las filas de esos estados (códigos de 2 letras), para el zip de base de cada release."""
    pedidos = {e.upper() for e in estados}
    return df[df["estado"].isin(pedidos)].reset_index(drop=True)


def escribir(df: pd.DataFrame, destino: Path = SALIDA) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False, lineterminator="\n", encoding="utf-8")
    return destino


def leer_html(ruta: Path, estado: str, anio: int, clases: dict[int, str]) -> tuple:
    """Lee un HTML de metadatos FGDC ya bajado con el extractor de research (sin red).

    Usa `de_html` de `cdl_precision_mo_wi_sd_extraer.py` (acepta "n/a"). Carga una copia nueva de los
    módulos en cada llamada, porque los extractores eligen estados y clases con variables globales.
    Devuelve (global, {clase: (px_correctos, productor_pct, usuario_pct)}), como el extractor.
    """
    ruta = Path(ruta)
    esperado = f"metadata-{estado.lower()}{anio % 100:02d}.html"
    if ruta.name != esperado:
        raise ValueError(f"el extractor busca {esperado}, no {ruta.name}")
    spec = importlib.util.spec_from_file_location("_t064", RESEARCH / "cdl_precision_mo_wi_sd_extraer.py")
    t064 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t064)
    t064.base.CULTIVOS = dict(clases)
    return t064.de_html(estado, anio, ruta.parent)   # `bajar` no baja nada si el archivo ya existe


def rehacer(dir_trabajo: Path, research: Path = RESEARCH) -> None:
    """Corre los extractores de research (con red). Reescriben los CSV de docs/research/."""
    dir_trabajo = Path(dir_trabajo).resolve()
    if dir_trabajo.is_relative_to(REPO):
        sys.exit(f"{dir_trabajo}: el directorio de trabajo tiene que estar fuera del repo")
    for _, script in FUENTES:
        print(f"-> {script}")
        subprocess.run([sys.executable, "-X", "utf8", str(research / script), str(dir_trabajo)], check=True)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rehacer", metavar="DIR", help="correr antes los extractores, bajando a DIR")
    a = ap.parse_args(argv)
    if a.rehacer:
        rehacer(Path(a.rehacer))
    df = armar()
    destino = escribir(df)
    print(f"{len(df)} filas, {df['estado'].nunique()} estados, {df['anio'].min()}–{df['anio'].max()} "
          f"-> {destino.relative_to(REPO)}")


if __name__ == "__main__":
    main()
