"""Ventanas de floración del maíz y llenado de la soja por estado y año (T128, propuesta de T038).

Las fechas salen de Crop Progress (NASS, nivel estado, semanal):
- floración del maíz: del 25 % al 75 % de *silking*;
- llenado de la soja: del 50 % de *setting pods* al 25 % de *dropping leaves*.

El día de cada cruce se interpola linealmente entre las dos semanas que lo rodean (semana fechada en su
domingo de cierre, `WEEK_ENDING`), igual que `docs/research/ventanas_por_estado.py`. Si el primer reporte
del año ya está en el porcentaje buscado o más, o si nunca se llega, no hay cruce y la ventana queda vacía:
nunca se usa la de otro año ni la mediana.

Fuentes de los cruces, en este orden:
1. la base completa de Quick Stats (`data/raw/cultivos/nass/qs.crops_*.txt.gz`, la misma que usa
   `src/cultivos/process.py` para `fenologia_estado.csv`);
2. si no está, `docs/research/ventanas_por_estado.csv` (cruces de los reportes de ESMIS 2008-2025 para los
   7 estados, script `docs/research/ventanas_por_estado.py` con el arreglo de T116).

Se guarda una copia de las ventanas en `data/interim/clima/ventanas_estado.csv` (con la columna `fuente`).
Este archivo no es una salida del paquete: `fenologia_estado.csv` no cambia.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

RAW_NASS = REPO / "data" / "raw" / "cultivos" / "nass"
RESEARCH = REPO / "docs" / "research" / "ventanas_por_estado.csv"
INTERIM = REPO / "data" / "interim" / "clima" / "ventanas_estado.csv"

ALFA_FIPS = {"IA": "19", "IL": "17", "IN": "18", "OH": "39", "NE": "31", "MN": "27", "KS": "20",
             "MO": "29", "WI": "55", "SD": "46", "ND": "38", "MI": "26", "KY": "21"}

# etapa -> (COMMODITY_DESC, UNIT_DESC) en Quick Stats
ETAPAS_QS = {
    "maiz_silking": ("CORN", "PCT SILKING"),
    "soja_setting_pods": ("SOYBEANS", "PCT SETTING PODS"),
    "soja_dropping_leaves": ("SOYBEANS", "PCT DROPPING LEAVES"),
}
# ventana -> ((etapa, % de inicio), (etapa, % de fin))
VENTANAS = {
    "floracion_maiz": (("maiz_silking", 25), ("maiz_silking", 75)),
    "llenado_soja": (("soja_setting_pods", 50), ("soja_dropping_leaves", 25)),
}
COLS_VENTANA = ["doy_ini_floracion_maiz", "doy_fin_floracion_maiz", "doy_ini_llenado_soja", "doy_fin_llenado_soja"]
COLS_NUEVAS = ["doy_ini_floracion_maiz", "doy_fin_floracion_maiz", "prec_floracion_maiz_mm",
               "tmax_floracion_maiz_c", "dias_tmax_gt30_floracion_maiz", "dias_tmax_gt35_floracion_maiz",
               "doy_ini_llenado_soja", "doy_fin_llenado_soja", "prec_llenado_soja_mm", "tmax_llenado_soja_c",
               "deficit_llenado_soja_mm", "prec_ago_sep15_mm"]


def cruce(doy, pct, p: float) -> float:
    """Día del año en que el % acumulado cruza p: primer par de semanas con y[i-1] < p <= y[i]."""
    orden = np.argsort(np.asarray(doy, float))
    x, y = np.asarray(doy, float)[orden], np.asarray(pct, float)[orden]
    for i in range(1, len(y)):
        if y[i - 1] < p <= y[i]:
            return float(x[i - 1] + (p - y[i - 1]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1]))
    return np.nan


def ventanas_desde_semanas(prog: pd.DataFrame) -> pd.DataFrame:
    """prog: fips_estado, anio, etapa, doy, pct (una fila por semana) -> una fila por estado y año."""
    filas = []
    for (est, anio), g in prog.groupby(["fips_estado", "anio"]):
        r = {"fips_estado": est, "anio": int(anio)}
        for nombre, ((e0, p0), (e1, p1)) in VENTANAS.items():
            g0, g1 = g[g["etapa"] == e0], g[g["etapa"] == e1]
            r[f"doy_ini_{nombre}"] = cruce(g0["doy"], g0["pct"], p0) if len(g0) else np.nan
            r[f"doy_fin_{nombre}"] = cruce(g1["doy"], g1["pct"], p1) if len(g1) else np.nan
        filas.append(r)
    return pd.DataFrame(filas, columns=["fips_estado", "anio", *COLS_VENTANA])


def semanas_quickstats(crops: pd.DataFrame) -> pd.DataFrame:
    """Semanas de Crop Progress de la base de Quick Stats ya filtrada (src/cultivos/process.filtrar)."""
    d = crops[(crops["SOURCE_DESC"] == "SURVEY") & (crops["AGG_LEVEL_DESC"] == "STATE")
              & (crops["STATISTICCAT_DESC"] == "PROGRESS") & (crops["DOMAIN_DESC"] == "TOTAL")
              & (crops["WEEK_ENDING"] != "")]
    partes = []
    for etapa, (com, unidad) in ETAPAS_QS.items():
        dv = d[(d["COMMODITY_DESC"] == com) & (d["UNIT_DESC"] == unidad)
               & (d["UTIL_PRACTICE_DESC"] == "ALL UTILIZATION PRACTICES")].copy()
        if dv.empty:
            continue
        fecha = pd.to_datetime(dv["WEEK_ENDING"].str[:10])
        partes.append(pd.DataFrame({
            "fips_estado": dv["STATE_FIPS_CODE"].str.zfill(2).to_numpy(), "anio": fecha.dt.year.to_numpy(),
            "etapa": etapa, "doy": fecha.dt.day_of_year.to_numpy(),
            "pct": pd.to_numeric(dv["VALUE"].str.replace(",", "").str.strip(), errors="coerce").to_numpy()}))
    if not partes:
        return pd.DataFrame(columns=["fips_estado", "anio", "etapa", "doy", "pct"])
    s = pd.concat(partes, ignore_index=True).dropna(subset=["pct"])
    return s.drop_duplicates(["fips_estado", "anio", "etapa", "doy"])


def ventanas_research(ruta: Path = RESEARCH) -> pd.DataFrame:
    """Ventanas desde los cruces ya calculados de docs/research/ventanas_por_estado.csv."""
    c = pd.read_csv(ruta)
    c["fips_estado"] = c["estado"].map(ALFA_FIPS)
    piv = {}
    for nombre, ((e0, p0), (e1, p1)) in VENTANAS.items():
        piv[f"doy_ini_{nombre}"] = c[c["etapa"] == e0].set_index(["fips_estado", "anio"])[f"doy{p0}"]
        piv[f"doy_fin_{nombre}"] = c[c["etapa"] == e1].set_index(["fips_estado", "anio"])[f"doy{p1}"]
    v = pd.DataFrame(piv).reset_index()
    return v[["fips_estado", "anio", *COLS_VENTANA]]


def cargar_ventanas() -> pd.DataFrame:
    """Ventanas por estado y año (Quick Stats si está bajado; si no, el CSV del research)."""
    crops_raw = sorted(RAW_NASS.glob("qs.crops_*.txt.gz"))
    if crops_raw:
        from src.cultivos.process import filtrar
        v = ventanas_desde_semanas(semanas_quickstats(filtrar(crops_raw[-1])))
        v["fuente"] = f"NASS Quick Stats ({crops_raw[-1].name})"
    elif RESEARCH.exists():
        v = ventanas_research()
        v["fuente"] = "docs/research/ventanas_por_estado.csv (ESMIS)"
    else:
        return pd.DataFrame(columns=["fips_estado", "anio", *COLS_VENTANA, "fuente"])
    INTERIM.parent.mkdir(parents=True, exist_ok=True)
    v.sort_values(["fips_estado", "anio"]).to_csv(INTERIM, index=False, encoding="utf-8", lineterminator="\n",
                                                   float_format="%.1f")
    return v


def _sumas(d: pd.DataFrame, dentro: pd.Series) -> pd.DataFrame:
    """Agregados por fips y anio de los días marcados; vacío si a la ventana le falta algún día."""
    n_vent = dentro.groupby([d["fips"], d["anio"]]).sum()
    s = d[dentro]
    g = s.groupby(["fips", "anio"])
    out = pd.DataFrame({
        "n": g.size(),
        "prec": g["prec_power_mm"].sum(min_count=1), "n_prec": g["prec_power_mm"].count(),
        "tmax": g["tmax_c"].mean(), "n_tmax": g["tmax_c"].count(),
        "gt30": g["tmax_c"].apply(lambda x: (x > 30).sum()), "gt35": g["tmax_c"].apply(lambda x: (x > 35).sum()),
        "deficit": (s["prec_power_mm"] - s["eto_pm_mm"]).groupby([s["fips"], s["anio"]]).sum(min_count=1),
        "n_def": (s["prec_power_mm"] - s["eto_pm_mm"]).groupby([s["fips"], s["anio"]]).count(),
    })
    out = out.reindex(n_vent[n_vent > 0].index)
    out.loc[out["n_prec"] < out["n"], "prec"] = np.nan
    out.loc[out["n_tmax"] < out["n"], ["tmax", "gt30", "gt35"]] = np.nan
    out.loc[out["n_def"] < out["n"], "deficit"] = np.nan
    return out


def columnas_ventanas(d: pd.DataFrame, ventanas: pd.DataFrame) -> pd.DataFrame:
    """Columnas nuevas de clima_anual.csv por fips y anio.

    d: diario con fips, fecha, prec_power_mm, tmax_c, eto_pm_mm. ventanas: fips_estado, anio, doy_*.
    Días incluidos: de round(doy_ini) a round(doy_fin), ambos inclusive. Las ventanas faltantes dejan vacías
    todas las columnas de esa ventana. prec_ago_sep15_mm no depende de la fenología (1 ago - 15 sep).
    """
    d = d[["fips", "fecha", "prec_power_mm", "tmax_c", "eto_pm_mm"]].copy()
    d["anio"] = d["fecha"].dt.year
    d["doy"] = d["fecha"].dt.day_of_year
    d["fips_estado"] = d["fips"].str[:2]
    claves = d[["fips", "anio"]].drop_duplicates().set_index(["fips", "anio"])
    a = pd.DataFrame(index=claves.index)

    v = ventanas[["fips_estado", "anio", *COLS_VENTANA]].copy()
    for c in COLS_VENTANA:
        v[c] = v[c].round().astype("Int64")
    dv = d.merge(v, on=["fips_estado", "anio"], how="left")
    dv.index = d.index
    vent_por_fy = dv[["fips", "anio", *COLS_VENTANA]].drop_duplicates(["fips", "anio"]).set_index(["fips", "anio"])
    for c in COLS_VENTANA:
        a[c] = vent_por_fy[c].reindex(a.index)

    for nombre in VENTANAS:
        ini, fin = dv[f"doy_ini_{nombre}"], dv[f"doy_fin_{nombre}"]
        ok = ini.notna() & fin.notna() & (fin >= ini)
        dentro = ok & (dv["doy"] >= ini.fillna(0)) & (dv["doy"] <= fin.fillna(-1))
        r = _sumas(d, dentro.astype(bool))
        if nombre == "floracion_maiz":
            a["prec_floracion_maiz_mm"] = r["prec"]
            a["tmax_floracion_maiz_c"] = r["tmax"]
            a["dias_tmax_gt30_floracion_maiz"] = r["gt30"]
            a["dias_tmax_gt35_floracion_maiz"] = r["gt35"]
        else:
            a["prec_llenado_soja_mm"] = r["prec"]
            a["tmax_llenado_soja_c"] = r["tmax"]
            a["deficit_llenado_soja_mm"] = r["deficit"]

    mes, dia = d["fecha"].dt.month, d["fecha"].dt.day
    ago_sep = (mes == 8) | ((mes == 9) & (dia <= 15))
    r = _sumas(d, ago_sep)
    a["prec_ago_sep15_mm"] = r["prec"].where(r["n"] == 46)
    for c in ("dias_tmax_gt30_floracion_maiz", "dias_tmax_gt35_floracion_maiz", *COLS_VENTANA):
        a[c] = a[c].astype("Int64")
    return a.reset_index()[["fips", "anio", *COLS_NUEVAS]]
