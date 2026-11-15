"""Análogos Argentina ↔ Corn Belt: clima anual por campaña de los departamentos de Buenos Aires, con las mismas
columnas que clima_anual.csv del paquete clima, para correr ahí los modelos entrenados en el Corn Belt.

Fuente: NASA POWER diario (AG), 1981-2025, en el centroide de cada departamento (data/raw/analogos/power_diario/,
lo baja `download.py diario`). Mismos 10 parámetros, la misma ETo FAO-56 y los mismos GDD que src/clima/process.py
(se importan de ahí). No hay IMERG: prec es PRECTOTCORR de POWER, como prec_temporada_mm en EE.UU.

Corrimiento de 6 meses (hemisferio sur). Cada mes real se cuenta como el mes 6 posiciones después, y julio a
diciembre pasan al año siguiente:

    real:      jul ago sep oct nov dic | ene feb mar abr may jun
    corrido:   ene feb mar abr may jun | jul ago sep oct nov dic   (anio = año de enero real)

Así, con anio = 2024:
- temporada (abril-septiembre corridos) = octubre de 2023 a marzo de 2024;
- invierno previo (noviembre-marzo) = mayo a septiembre de 2023;
- "jul" (floración del maíz) = enero de 2024; "ago" (llenado de la soja) = febrero de 2024.

Los nombres de columna son los de EE.UU. (prec_jul_mm, tmax_jul_c, ...) y se refieren al mes corrido. Los días del
año (doy_ultima_helada, doy_primera_helada) se cuentan desde el 1 de julio real del anio − 1 (día 1 = 1 de julio):
última helada de primavera = la última con tmin ≤ 0 °C entre julio y enero reales; primera de otoño = la primera
entre febrero y junio reales. La diferencia con un día del año de EE.UU. es de 0 a 3 días según el mes (julio a
diciembre suman 184 días; enero a junio, 181 o 182). Las tendencias por década usan años corridos (julio a junio)
completos, con la misma ventana de 30 años que el paquete clima.

Salida: data/processed/analogos/clima_anual_ba.csv con id_depto_indec, anio y las columnas de clima_anual.csv,
años 2000 a 2025 (el anio 2000 es julio de 1999 a junio de 2000).
Uso: python src/analogos/clima_ba.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
from src.clima.process import UMBRAL_HELADA, eto_fao56, leer_power, mensual, tendencia  # noqa: E402
from src.common.config import cargar_config  # noqa: E402

RAW = RAIZ / "data" / "raw" / "analogos" / "power_diario"
OUT = RAIZ / "data" / "processed" / "analogos"
COLS = ["doy_ultima_helada", "doy_primera_helada", "periodo_libre_heladas_dias", "prec_temporada_mm", "gdd_temporada",
        "prec_invierno_previo_mm", "prec_jul_mm", "tmax_jul_c", "dias_tmax_gt30_jul", "prec_ago_mm",
        "deficit_temporada_mm", "tend_prec_mm_decada", "tend_tmed_c_decada"]


def correr(fecha: pd.Series) -> pd.DataFrame:
    """anio, mes (1-12) y doy en el calendario corrido 6 meses."""
    y, m = fecha.dt.year, fecha.dt.month
    anio = y + (m >= 7).astype(int)
    mes = (m + 5) % 12 + 1
    inicio = pd.to_datetime((anio - 1).astype(str) + "-07-01")
    doy = (fecha - inicio).dt.days + 1
    return pd.DataFrame({"anio_c": anio, "mes_c": mes, "doy_c": doy}, index=fecha.index)


def diario(archivos: list[Path]) -> pd.DataFrame:
    d = pd.concat([leer_power(p) for p in archivos], ignore_index=True).sort_values(["fips", "fecha"])
    d = d.reset_index(drop=True)
    # todo lo que depende de la fecha real (geometría solar, ventanas móviles) se calcula antes de correr
    d["eto_pm_mm"] = eto_fao56(d)
    tx = d["tmax_c"].clip(upper=30)
    tn = d["tmin_c"].clip(lower=10, upper=30)
    d["gdd_10_30"] = ((tx.clip(lower=10) + tn) / 2 - 10).clip(lower=0)
    d["gdd_base0"] = d["tmed_c"].clip(lower=0)
    d["prec5d"] = d.groupby("fips")["prec_power_mm"].transform(lambda s: s.rolling(5, min_periods=5).sum())
    d["prec_imerg_mm"] = np.nan
    d = d.join(correr(d["fecha"]))
    d["mes"] = d["anio_c"].astype(str) + "-" + d["mes_c"].map("{:02d}".format)
    return d


def anual(d: pd.DataFrame, m: pd.DataFrame) -> pd.DataFrame:
    """La misma lógica que src/clima/process.anual, con el calendario corrido."""
    hel = d["tmin_c"] <= UMBRAL_HELADA
    ult = d[hel & (d["mes_c"] <= 7)].groupby(["fips", "anio_c"])["doy_c"].max()
    pri = d[hel & (d["mes_c"] >= 8)].groupby(["fips", "anio_c"])["doy_c"].min()
    for s in (ult, pri):
        s.index.names = ["fips", "anio"]
    m = m.copy()
    m["mesn"] = m["mes_ts"].dt.month
    temp = m[m["mesn"].between(4, 9)].groupby(["fips", "anio"])
    a = pd.DataFrame({
        "prec_temporada_mm": temp["prec_power_mm"].sum(min_count=6),
        "gdd_temporada": temp["gdd_10_30"].sum(min_count=6),
        "deficit_temporada_mm": temp["deficit_mm"].sum(min_count=6),
    })
    inv = m[(m["mesn"] >= 11) | (m["mesn"] <= 3)].copy()
    inv["anio_inv"] = np.where(inv["mesn"] >= 11, inv["anio"] + 1, inv["anio"])
    pinv = inv.groupby(["fips", "anio_inv"])["prec_power_mm"].sum(min_count=5)
    pinv.index.names = ["fips", "anio"]
    a["prec_invierno_previo_mm"] = pinv
    jul = m[m["mesn"] == 7].set_index(["fips", "anio"])
    ago = m[m["mesn"] == 8].set_index(["fips", "anio"])
    a["prec_jul_mm"] = jul["prec_power_mm"]
    a["tmax_jul_c"] = jul["tmax_c"]
    a["dias_tmax_gt30_jul"] = jul["dias_tmax_gt30"]
    a["prec_ago_mm"] = ago["prec_power_mm"]
    a["doy_ultima_helada"] = ult
    a["doy_primera_helada"] = pri
    a["periodo_libre_heladas_dias"] = a["doy_primera_helada"] - a["doy_ultima_helada"] - 1
    a = a.reset_index()
    gy = d.groupby(["fips", "anio_c"])
    tot = pd.DataFrame({"prec": gy["prec_power_mm"].sum(min_count=365), "tmed": gy["tmed_c"].mean(),
                        "n": gy.size()}).reset_index().rename(columns={"anio_c": "anio"})
    tot.loc[tot["n"] < 365, ["prec", "tmed"]] = np.nan
    tot["tend_prec_mm_decada"] = tendencia(tot, "prec")
    tot["tend_tmed_c_decada"] = tendencia(tot, "tmed")
    return a.merge(tot[["fips", "anio", "tend_prec_mm_decada", "tend_tmed_c_decada"]], on=["fips", "anio"], how="left")


def main() -> int:
    cfg = cargar_config()
    y0, y1 = int(cfg["periodo"]["anio_inicio"]), int(cfg["periodo"]["anio_fin"])
    archivos = sorted(RAW.glob("ar_*.csv"))
    if not archivos:
        raise SystemExit("no hay POWER diario: correr python src/analogos/download.py diario")
    d = diario(archivos)
    m = mensual(d, cfg)
    a = anual(d, m)
    a = a[a["anio"].between(y0, y1)].sort_values(["fips", "anio"]).rename(columns={"fips": "id_depto_indec"})
    for c in ("doy_ultima_helada", "doy_primera_helada", "periodo_libre_heladas_dias", "dias_tmax_gt30_jul"):
        a[c] = a[c].astype("Int64")
    a = a[["id_depto_indec", "anio", *COLS]]
    for c in COLS:
        if pd.api.types.is_float_dtype(a[c]):
            a[c] = a[c].round(3)
    OUT.mkdir(parents=True, exist_ok=True)
    a.to_csv(OUT / "clima_anual_ba.csv", index=False, encoding="utf-8", lineterminator="\n", float_format="%.3f")
    print(f"clima_anual_ba.csv: {len(a)} filas, {a['id_depto_indec'].nunique()} departamentos, "
          f"{a['anio'].min()}-{a['anio'].max()}")
    print(a[COLS].describe().T[["count", "mean", "min", "max"]].round(1).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
