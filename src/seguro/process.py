"""Paquete seguro — seguro agrícola federal (USDA RMA) por condado, año y cultivo.

Entradas (data/raw/seguro/, de src/seguro/download.py; zips nacionales, se filtran acá):
- colsom_<AAAA>.zip: Cause of Loss Summary of Business with Month of Loss. Texto separado por `|`,
  sin encabezado, 30 columnas (diccionario COL_Summary_of_Business_with_Month_All_Years.pdf).
- sobtpu_<AAAA>.zip: Summary of Business por condado, cultivo, plan, cobertura, tipo, práctica y
  estructura de unidad. Texto separado por `|`, sin encabezado, 27 columnas, fin de línea CR
  (diccionario SOBTPU_External_All_Years.pdf).

Se usan los estados de config.yaml (filtrados por FIELDSHIFT_ESTADOS) y los cultivos de
CULTIVOS (códigos RMA de docs/research/rma_causa_perdida.md).

Salidas (data/processed/seguro/):
- seguro_anual.csv: fips, anio, cultivo, superficie asegurada (total, riego, secano),
  responsabilidad, prima, indemnización, loss_ratio, loss_cost, superficie con pérdida e
  indemnización por grupo de causa.
- seguro_mensual.csv: fips, anio, mes, cultivo, indemnización por grupo de causa según el mes de
  la pérdida (Year of Loss + Month of Loss).
- docs/datasets/seguro.md (tablas generadas: columnas con cobertura y % de faltantes, filas
  descartadas por condado fuera de condados.csv).

Uso: python src/seguro/process.py
"""
from __future__ import annotations

import io
import re
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import cargar_config, estados_config  # noqa: E402
from src.common.validacion import validar_csv  # noqa: E402

RAW = REPO / "data" / "raw" / "seguro"
INTERIM = REPO / "data" / "interim" / "seguro"
OUT = REPO / "data" / "processed" / "seguro"
CARD = REPO / "docs" / "datasets" / "seguro.md"
CONDADOS = REPO / "data" / "reference" / "condados.csv"

# Código de cultivo RMA (4 dígitos) -> código del proyecto. El trigo (0011) de RMA junta invierno y
# primavera y el archivo de causas no tiene columna de tipo: va como `trigo` (todo el trigo), con
# `trigo_frac_invierno` sacada de sobtpu.
CULTIVOS = {"0041": "maiz", "0081": "soja", "0011": "trigo", "0016": "avena"}

# Columnas de colsom (1-30) y de sobtpu (1-27) según los diccionarios oficiales.
COL_COLS = ["anio", "st", "st_abrev", "cty", "cty_nombre", "cod_cultivo", "cultivo_nombre",
            "plan", "plan_abrev", "categoria", "etapa", "cod_causa", "causa", "mes_perdida",
            "mes_nombre", "anio_perdida", "polizas_prima", "polizas_indem", "cant_plantada",
            "acres_endosados", "liability", "prima_total", "prima_productor", "subsidio",
            "subsidio_estatal", "subsidio_adicional", "efa", "cant_determinada", "indemnizacion",
            "loss_ratio"]
SOB_COLS = ["anio", "st", "st_nombre", "st_abrev", "cty", "cty_nombre", "cod_cultivo",
            "cultivo_nombre", "plan", "plan_abrev", "categoria", "nivel_cobertura", "entrega",
            "cod_tipo", "tipo", "cod_practica", "practica", "cod_unidad", "unidad", "cantidad",
            "tipo_cantidad", "liability", "prima_total", "subsidio", "indemnizacion", "loss_ratio",
            "endosado"]

# Código de causa (Exhibit 10 de FCIC-25010, 2026) -> grupo. Lo que no está acá va a `otras`
# (riego 13-15, incendio, fauna, "All Other Causes" XX, 99 y códigos viejos o nuevos).
GRUPOS_CAUSA = {
    "11": "sequia",
    "12": "calor", "62": "calor",
    "31": "exceso_agua", "51": "exceso_agua",
    "21": "granizo",
    "41": "helada", "42": "helada", "43": "helada",
    "44": "frio_humedo",
    "61": "viento", "63": "viento", "64": "viento", "92": "viento",
    "09": "enfermedad_plagas", "71": "enfermedad_plagas", "81": "enfermedad_plagas",
    "82": "enfermedad_plagas",
    "01": "precio",
    "55": "area",
}
GRUPOS = ["sequia", "exceso_agua", "calor", "granizo", "helada", "frio_humedo", "viento",
          "enfermedad_plagas", "precio", "area", "otras"]
GRUPOS_CLIMA = ["sequia", "exceso_agua", "calor", "granizo", "helada", "frio_humedo", "viento"]
COLS_INDEM = [f"indem_{g}_usd" for g in GRUPOS]

COLS_ANUAL = (["sup_asegurada_ac", "sup_asegurada_secano_ac", "sup_asegurada_riego_ac",
               "responsabilidad_usd", "prima_total_usd", "indemnizacion_usd", "loss_ratio",
               "loss_cost", "sup_con_perdida_ac", "indem_causas_usd"] + COLS_INDEM
              + ["frac_indem_clima", "trigo_frac_invierno"])
COLS_MENSUAL = COLS_INDEM + ["indem_total_usd", "sup_con_perdida_ac"]


# ---------------------------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------------------------

def leer_lineas(texto: str, n_cols: int, fips_estados: set[str], cols: list[str]) -> pd.DataFrame:
    """Texto `|` sin encabezado -> DataFrame (todo texto, sin espacios) de los estados pedidos.

    Acepta fin de línea LF, CRLF o CR. Filtra por el código de estado (2.ª columna) antes de
    parsear, para no armar la tabla nacional entera.
    """
    filas = []
    for linea in re.split(r"\r\n|\r|\n", texto):
        if not linea.strip():
            continue
        partes = linea.split("|")
        if partes[1].strip().zfill(2) not in fips_estados:
            continue
        if len(partes) != n_cols:
            raise ValueError(f"se esperaban {n_cols} columnas y hay {len(partes)}: {linea[:120]}")
        filas.append([p.strip() for p in partes])
    return pd.DataFrame(filas, columns=cols)


def leer_zip(ruta: Path, n_cols: int, fips_estados: set[str], cols: list[str]) -> pd.DataFrame:
    with zipfile.ZipFile(ruta) as z:
        nombres = [n for n in z.namelist() if n.lower().endswith(".txt")]
        if len(nombres) != 1:
            raise ValueError(f"{ruta.name}: se esperaba un .txt adentro y hay {nombres}")
        texto = z.read(nombres[0]).decode("latin-1")
    return leer_lineas(texto, n_cols, fips_estados, cols)


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.str.replace(",", "", regex=False), errors="coerce")


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    """Claves comunes: fips (5 dígitos), anio, cultivo; deja solo los cultivos de CULTIVOS."""
    df = df.copy()
    df["cod_cultivo"] = df["cod_cultivo"].str.zfill(4)
    df = df[df["cod_cultivo"].isin(CULTIVOS)].copy()
    df["cultivo"] = df["cod_cultivo"].map(CULTIVOS)
    df["fips"] = df["st"].str.zfill(2) + df["cty"].str.zfill(3)
    df["anio"] = df["anio"].astype(int)
    return df


def practica_grupo(nombre: str) -> str:
    """Practice Name de sobtpu -> riego / secano / sin_especificar.

    "Non-Irrigated", "Non-Irr", "Nfac (Non-Irrigated)" -> secano; "Irrigated", "Irr.",
    "Limited Irrigation" -> riego; "Summerfallow" y "Continuous Cropping" (trigo de las Grandes
    Llanuras, sin riego) -> secano; "No Practice Specified" y el resto -> sin_especificar.
    """
    s = nombre.lower().replace(" ", "")
    if "non-irr" in s or "nonirr" in s:
        return "secano"
    if "irr" in s:
        return "riego"
    if "summerfallow" in s or "continuouscropping" in s:
        return "secano"
    return "sin_especificar"


def grupo_causa(cod: str) -> str:
    return GRUPOS_CAUSA.get(cod.strip().zfill(2) if cod.strip().isdigit() else cod.strip(), "otras")


# ---------------------------------------------------------------------------------------------
# Agregación
# ---------------------------------------------------------------------------------------------

def resumir_sob(sob: pd.DataFrame) -> pd.DataFrame:
    """sobtpu (ya preparado) -> fips, anio, cultivo con superficie, responsabilidad, prima, indemnización.

    Suma todos los planes, niveles de cobertura, tipos, prácticas y unidades. La superficie solo
    cuenta donde Reporting Level Type = Acres (los endosos de área como SCO o ECO vienen con 0 acres
    y no duplican la superficie, pero sí suman responsabilidad, prima e indemnización).
    """
    s = sob.copy()
    acres = s["tipo_cantidad"].str.lower() == "acres"
    s["sup"] = _num(s["cantidad"]).where(acres, 0.0)
    pg = s["practica"].map(practica_grupo)
    s["sup_secano"] = s["sup"].where(pg == "secano", 0.0)
    s["sup_riego"] = s["sup"].where(pg == "riego", 0.0)
    s["sup_invierno"] = s["sup"].where(s["tipo"].str.lower() == "winter", 0.0)
    for c in ("liability", "prima_total", "indemnizacion"):
        s[c] = _num(s[c])
    g = s.groupby(["fips", "anio", "cultivo"], as_index=False)[
        ["sup", "sup_secano", "sup_riego", "sup_invierno", "liability", "prima_total",
         "indemnizacion"]].sum(min_count=1)
    g = g.rename(columns={"sup": "sup_asegurada_ac", "sup_secano": "sup_asegurada_secano_ac",
                          "sup_riego": "sup_asegurada_riego_ac", "liability": "responsabilidad_usd",
                          "prima_total": "prima_total_usd", "indemnizacion": "indemnizacion_usd"})
    trigo = g["cultivo"] == "trigo"
    g["trigo_frac_invierno"] = np.where(trigo & (g["sup_asegurada_ac"] > 0),
                                        g["sup_invierno"] / g["sup_asegurada_ac"].where(g["sup_asegurada_ac"] > 0),
                                        np.nan)
    return g.drop(columns="sup_invierno")


def causas_largo(col: pd.DataFrame) -> pd.DataFrame:
    """colsom (ya preparado) -> filas con grupo de causa, indemnización y acres con pérdida."""
    c = col.copy()
    c["grupo"] = c["cod_causa"].map(grupo_causa)
    c["indem"] = _num(c["indemnizacion"])
    c["sup_perdida"] = _num(c["cant_determinada"])
    return c


def pivot_grupos(c: pd.DataFrame, claves: list[str]) -> pd.DataFrame:
    p = c.pivot_table(index=claves, columns="grupo", values="indem", aggfunc="sum", fill_value=0.0)
    p = p.reindex(columns=GRUPOS, fill_value=0.0)
    p.columns = [f"indem_{g}_usd" for g in p.columns]
    p["sup_con_perdida_ac"] = c.groupby(claves)["sup_perdida"].sum()
    return p.reset_index()


def armar_anual(sob: pd.DataFrame, col: pd.DataFrame, fips_validos: list[str],
                anios: list[int]) -> pd.DataFrame:
    """Grilla completa fips × anio × cultivo (condados de condados.csv, años del período).

    Sin participación en sobtpu ni filas de causa, todo queda vacío. Con participación o con filas
    de causa, la indemnización de los grupos sin filas es 0 (dato real: no hubo pérdida).
    """
    grilla = pd.MultiIndex.from_product([sorted(fips_validos), anios, list(CULTIVOS.values())],
                                        names=["fips", "anio", "cultivo"]).to_frame(index=False)
    s = resumir_sob(sob)
    c = causas_largo(col)
    p = pivot_grupos(c, ["fips", "anio", "cultivo"]) if len(c) else pd.DataFrame(
        columns=["fips", "anio", "cultivo"] + COLS_INDEM + ["sup_con_perdida_ac"])
    out = grilla.merge(s, on=["fips", "anio", "cultivo"], how="left")
    out = out.merge(p, on=["fips", "anio", "cultivo"], how="left")
    tiene = out["fips"].notna() & False
    if len(s):
        tiene |= out.set_index(["fips", "anio", "cultivo"]).index.isin(
            s.set_index(["fips", "anio", "cultivo"]).index)
    if len(p):
        tiene |= out.set_index(["fips", "anio", "cultivo"]).index.isin(
            p.set_index(["fips", "anio", "cultivo"]).index)
    for col_ in COLS_INDEM + ["sup_con_perdida_ac"]:
        out[col_] = out[col_].astype(float).where(~tiene | out[col_].notna(), 0.0)
    out["indem_causas_usd"] = out[COLS_INDEM].sum(axis=1, min_count=1)
    out.loc[~tiene, "indem_causas_usd"] = np.nan
    prima = out["prima_total_usd"].where(out["prima_total_usd"] > 0)
    resp = out["responsabilidad_usd"].where(out["responsabilidad_usd"] > 0)
    out["loss_ratio"] = out["indemnizacion_usd"] / prima
    out["loss_cost"] = out["indemnizacion_usd"] / resp
    total = out["indem_causas_usd"].where(out["indem_causas_usd"] > 0)
    out["frac_indem_clima"] = out[[f"indem_{g}_usd" for g in GRUPOS_CLIMA]].sum(axis=1) / total
    out = out[["fips", "anio", "cultivo"] + COLS_ANUAL]
    return out.sort_values(["fips", "anio", "cultivo"]).reset_index(drop=True)


def armar_mensual(col: pd.DataFrame, anios: list[int]) -> tuple[pd.DataFrame, dict]:
    """Indemnización por mes calendario de la pérdida.

    `mes` = Year of Loss + Month of Loss; `anio` = año del mes (contrato §4). Se suman todos los
    años de cosecha que tienen pérdidas en ese mes (p. ej., trigo de invierno dañado en otoño).
    Se descartan las filas sin mes válido y aquellas cuyo año de pérdida está a más de un año del
    año de cosecha (errores evidentes de carga); se cuentan en `descartes`.
    """
    c = causas_largo(col)
    mes = pd.to_numeric(c["mes_perdida"], errors="coerce")
    anio_p = pd.to_numeric(c["anio_perdida"], errors="coerce")
    sin_mes = mes.isna() | ~mes.between(1, 12) | anio_p.isna()
    lejos = ~sin_mes & ((anio_p - c["anio"]).abs() > 1)
    descartes = {
        "filas_sin_mes": int(sin_mes.sum()),
        "anios_sin_anio_perdida": sorted(int(a) for a, g in anio_p.isna().groupby(c["anio"]) if g.all()),
        "indem_sin_mes_usd": float(c.loc[sin_mes, "indem"].sum()),
        "filas_anio_perdida_lejano": int(lejos.sum()),
        "indem_anio_perdida_lejano_usd": float(c.loc[lejos, "indem"].sum()),
    }
    c = c[~sin_mes & ~lejos].copy()
    c["anio_mes"] = anio_p[c.index].astype(int)
    c = c[c["anio_mes"].isin(anios)]
    c["mes"] = c["anio_mes"].astype(str) + "-" + mes[c.index].astype(int).astype(str).str.zfill(2)
    if c.empty:
        return pd.DataFrame(columns=["fips", "anio", "mes", "cultivo"] + COLS_MENSUAL), descartes
    p = pivot_grupos(c.rename(columns={"anio": "anio_cosecha", "anio_mes": "anio"}),
                     ["fips", "anio", "mes", "cultivo"])
    p["indem_total_usd"] = p[COLS_INDEM].sum(axis=1)
    p = p[["fips", "anio", "mes", "cultivo"] + COLS_MENSUAL]
    return p.sort_values(["fips", "mes", "cultivo"]).reset_index(drop=True), descartes


def separar_fuera(df: pd.DataFrame, validos: set[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa las filas cuyo fips no está en condados.csv (p. ej., 999 "All Other Counties")."""
    fuera = ~df["fips"].isin(validos)
    return df[~fuera], df[fuera]


# ---------------------------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------------------------

def guardar(df: pd.DataFrame, ruta: Path) -> None:
    out = df.copy()
    out["anio"] = out["anio"].astype(int)
    tmp = ruta.with_suffix(".part")
    out.to_csv(tmp, index=False, float_format="%.6g", lineterminator="\n")
    tmp.replace(ruta)


def main() -> None:
    t0 = time.time()
    cfg = cargar_config()
    estados = estados_config()
    fips_estados = {e["fips"] for e in estados.values()}
    anios = list(range(int(cfg["periodo"]["anio_inicio"]), int(cfg["periodo"]["anio_fin"]) + 1))
    if not CONDADOS.exists():
        raise SystemExit(f"falta {CONDADOS}: correr src/base/")
    cond = pd.read_csv(CONDADOS, dtype={"fips": str})
    validos = set(cond.loc[cond["fips"].str[:2].isin(fips_estados), "fips"])

    cols, sobs, faltan = [], [], []
    for a in anios:
        for nombre, n, nombres_cols, lista in ((f"colsom_{a}.zip", 30, COL_COLS, cols),
                                               (f"sobtpu_{a}.zip", 27, SOB_COLS, sobs)):
            ruta = RAW / nombre
            if not ruta.exists():
                faltan.append(nombre)
                continue
            lista.append(preparar(leer_zip(ruta, n, fips_estados, nombres_cols)))
        print(f"{a} leído ({time.time() - t0:.0f} s)")
    if faltan:
        print(f"faltan en raw ({len(faltan)}): {', '.join(faltan)} — correr src/seguro/download.py")
    col = pd.concat(cols, ignore_index=True) if cols else preparar(pd.DataFrame(columns=COL_COLS))
    sob = pd.concat(sobs, ignore_index=True) if sobs else preparar(pd.DataFrame(columns=SOB_COLS))

    col_ok, col_fuera = separar_fuera(col, validos)
    sob_ok, sob_fuera = separar_fuera(sob, validos)
    anual = armar_anual(sob_ok, col_ok, sorted(validos), anios)
    mensual, descartes = armar_mensual(col_ok, anios)

    OUT.mkdir(parents=True, exist_ok=True)
    guardar(anual, OUT / "seguro_anual.csv")
    guardar(mensual, OUT / "seguro_mensual.csv")
    for f in ("seguro_anual.csv", "seguro_mensual.csv"):
        errores = validar_csv(OUT / f)
        print(f"{f}: {'validar_csv OK' if not errores else errores}")
    from src.seguro.data_card import escribir  # noqa: E402
    escribir(anual, mensual, col_fuera, sob_fuera, descartes, faltan, col_ok, sob_ok, estados)
    print(f"seguro_anual.csv: {len(anual)} filas; seguro_mensual.csv: {len(mensual)} filas "
          f"({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
