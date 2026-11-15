"""Paquete clima — procesa NASA POWER diario a clima_diario.csv, clima_mensual.csv y clima_anual.csv.

Se corre desde la raíz: python src/clima/process.py (sin argumentos, no baja nada).
Lee data/raw/clima/power/power_diario_<fips>.csv (1981 en adelante: la base para SPI,
anomalías y tendencias) y escribe solo el período de config.yaml.

IMERG (prec_imerg_mm): data/raw/clima/imerg_power/imerg_<lat>_<lon>.csv (IMERG_PRECTOT de POWER,
una celda de 0,1° por archivo); la media del condado es el promedio de sus celdas (src/clima/celdas.py).
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import cargar_config  # noqa: E402
from src.clima.celdas import celdas_imerg, nombre_celda  # noqa: E402

RAW = REPO / "data" / "raw" / "clima" / "power"
RAW_IM = REPO / "data" / "raw" / "clima" / "imerg_power"
OUT = REPO / "data" / "processed" / "clima"
CONDADOS = REPO / "data" / "reference" / "condados.csv"

RENOMBRE = {"T2M": "tmed_c", "T2M_MAX": "tmax_c", "T2M_MIN": "tmin_c", "PRECTOTCORR": "prec_power_mm",
            "RH2M": "hr_pct", "WS2M": "viento_ms", "ALLSKY_SFC_SW_DWN": "rad_mj_m2",
            "GWETTOP": "gwettop", "GWETROOT": "gwetroot", "GWETPROF": "gwetprof"}
FILL = -999.0
UMBRAL_LLUVIA = 1.0   # mm: día de lluvia y racha seca
UMBRAL_HELADA = 0.0   # °C: helada (tmin <= 0 °C, 32 °F)


# --------------------------------------------------------------------------- lectura

def leer_power(p: Path) -> pd.DataFrame:
    txt = p.read_text(encoding="utf-8")
    cab, cuerpo = txt.split("-END HEADER-", 1)
    elev = float(re.search(r"=\s*([-\d.]+)\s*meters", cab).group(1))
    lat = float(re.search(r"latitude\s+([-\d.]+)", cab).group(1))
    df = pd.read_csv(io.StringIO(cuerpo.strip()))
    df = df.replace(FILL, np.nan)
    df["fecha"] = pd.to_datetime(df["YEAR"].astype(str), format="%Y") + pd.to_timedelta(df["DOY"] - 1, unit="D")
    df = df.rename(columns=RENOMBRE).drop(columns=["YEAR", "DOY"])
    df["fips"] = p.stem.split("_")[-1]
    df["elev_m"] = elev
    df["lat"] = lat
    return df


def leer_imerg_celda(p: Path) -> pd.DataFrame:
    cuerpo = p.read_text(encoding="utf-8").split("-END HEADER-", 1)[1]
    df = pd.read_csv(io.StringIO(cuerpo.strip()))
    return df


def imerg_condado() -> pd.DataFrame:
    """fips, fecha, prec_imerg_mm: media diaria (día UTC) de las celdas de 0,1° de cada condado."""
    cel = celdas_imerg()
    unicas = cel[["lat", "lon"]].drop_duplicates().sort_values(["lat", "lon"]).reset_index(drop=True)
    fechas, cols, pos = None, [], {}
    for r in unicas.itertuples():
        p = RAW_IM / nombre_celda(r.lat, r.lon)
        if not p.exists():
            continue
        df = leer_imerg_celda(p)
        f = pd.to_datetime(df["YEAR"].astype(str), format="%Y") + pd.to_timedelta(df["DOY"] - 1, unit="D")
        if fechas is None:
            fechas = f
        elif not f.equals(fechas):
            raise ValueError(f"fechas distintas en {p.name}")
        v = df["IMERG_PRECTOT"].to_numpy(dtype="float64", copy=True)
        v[v == FILL] = np.nan
        pos[(r.lat, r.lon)] = len(cols)
        cols.append(v)
    if not cols:
        return pd.DataFrame(columns=["fips", "fecha", "prec_imerg_mm"])
    A = np.vstack(cols)
    out = []
    for fips, g in cel.groupby("fips", sort=True):
        idx = [pos[k] for k in zip(g["lat"], g["lon"]) if k in pos]
        if not idx:
            continue
        sub = A[idx]
        n = np.sum(~np.isnan(sub), axis=0)
        media = np.where(n > 0, np.nansum(sub, axis=0) / np.maximum(n, 1), np.nan)
        out.append(pd.DataFrame({"fips": fips, "fecha": fechas.to_numpy(), "prec_imerg_mm": media}))
    return pd.concat(out, ignore_index=True)


# --------------------------------------------------------------------------- ETo FAO-56

def eto_fao56(d: pd.DataFrame) -> pd.Series:
    """ETo Penman-Monteith FAO-56 diario (mm/día), G = 0, ea desde HR media (ec. 19)."""
    tmax, tmin, rs, u2, hr = d["tmax_c"], d["tmin_c"], d["rad_mj_m2"], d["viento_ms"], d["hr_pct"]
    z = d["elev_m"]
    t = (tmax + tmin) / 2
    p = 101.3 * ((293 - 0.0065 * z) / 293) ** 5.26
    gamma = 0.000665 * p

    def e0(x):
        return 0.6108 * np.exp(17.27 * x / (x + 237.3))

    es = (e0(tmax) + e0(tmin)) / 2
    ea = hr / 100 * es
    delta = 4098 * e0(t) / (t + 237.3) ** 2
    phi = np.deg2rad(d["lat"])
    j = d["fecha"].dt.day_of_year
    dr = 1 + 0.033 * np.cos(2 * np.pi * j / 365)
    dec = 0.409 * np.sin(2 * np.pi * j / 365 - 1.39)
    ws = np.arccos(-np.tan(phi) * np.tan(dec))
    ra = 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(phi) * np.sin(dec) + np.cos(phi) * np.cos(dec) * np.sin(ws))
    rso = (0.75 + 2e-5 * z) * ra
    rns = 0.77 * rs
    sigma = 4.903e-9
    ratio = (rs / rso).clip(upper=1.0)
    rnl = sigma * ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2 * (0.34 - 0.14 * np.sqrt(ea)) * (1.35 * ratio - 0.35)
    rn = rns - rnl
    eto = (0.408 * delta * rn + gamma * 900 / (t + 273) * u2 * (es - ea)) / (delta + gamma * (1 + 0.34 * u2))
    return eto.clip(lower=0)


# --------------------------------------------------------------------------- mensual

def racha_seca_mensual(d: pd.DataFrame) -> pd.Series:
    """Racha más larga de días con prec < 1 mm dentro de cada mes (por fips, mes)."""
    seco = (d["prec_power_mm"] < UMBRAL_LLUVIA) & d["prec_power_mm"].notna()
    clave = d["fips"] + "_" + d["mes"]
    corte = (seco != seco.shift()) | (clave != clave.shift())
    grupo = corte.cumsum()
    largo = seco.groupby(grupo).transform("size").where(seco, 0)
    return largo.groupby([d["fips"], d["mes"]]).max()


def spi(serie_mm: pd.DataFrame, k: int) -> pd.Series:
    """SPI-k con gamma ajustada por condado y mes calendario sobre todo el registro POWER.

    serie_mm: columnas fips, mes (Timestamp), prec. Probabilidad de cero mixta (H = q + (1-q)G).
    """
    out = []
    for fips, g in serie_mm.groupby("fips", sort=True):
        g = g.sort_values("mes")
        acc = g["prec"].rolling(k, min_periods=k).sum()
        res = pd.Series(np.nan, index=g.index)
        meses = g["mes"].dt.month
        for m in range(1, 13):
            sel = (meses == m) & acc.notna()
            x = acc[sel].to_numpy()
            if len(x) < 20:
                continue
            q = np.mean(x <= 0)
            pos = x[x > 0]
            a, _, scale = stats.gamma.fit(pos, floc=0)
            h = q + (1 - q) * stats.gamma.cdf(np.where(x > 0, x, 0), a, loc=0, scale=scale)
            h = np.where(x > 0, h, q if q > 0 else 0.5 / len(x))
            res[sel] = stats.norm.ppf(np.clip(h, 1e-6, 1 - 1e-6))
        out.append(res)
    return pd.concat(out).reindex(serie_mm.index).clip(-5, 5)


def mensual(d: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    gb = d.groupby(["fips", "mes"], sort=True)
    m = pd.DataFrame({
        "prec_power_mm": gb["prec_power_mm"].sum(min_count=1),
        "tmax_c": gb["tmax_c"].mean(),
        "tmin_c": gb["tmin_c"].mean(),
        "tmed_c": gb["tmed_c"].mean(),
        "rad_mj_m2": gb["rad_mj_m2"].sum(min_count=1),
        "eto_pm_mm": gb["eto_pm_mm"].sum(min_count=1),
        "dias_tmax_gt30": gb["tmax_c"].apply(lambda s: (s > 30).sum()),
        "dias_tmax_gt35": gb["tmax_c"].apply(lambda s: (s > 35).sum()),
        "dias_tmin_le0": gb["tmin_c"].apply(lambda s: (s <= 0).sum()),
        "dias_tmin_le_m2": gb["tmin_c"].apply(lambda s: (s <= -2).sum()),
        "gdd_10_30": gb["gdd_10_30"].sum(min_count=1),
        "gdd_base0": gb["gdd_base0"].sum(min_count=1),
        "dias_lluvia_ge1": gb["prec_power_mm"].apply(lambda s: (s >= UMBRAL_LLUVIA).sum()),
        "prec_max1d_mm": gb["prec_power_mm"].max(),
        "prec_max5d_mm": gb["prec5d"].max(),
        "dias_lluvia_gt50": gb["prec_power_mm"].apply(lambda s: (s > 50).sum()),
        "racha_seca_max_dias": racha_seca_mensual(d),
        "gwettop": gb["gwettop"].mean(),
        "gwetroot": gb["gwetroot"].mean(),
        "gwetprof": gb["gwetprof"].mean(),
    })
    # meses incompletos de rad / eto: vacío (los totales no serían comparables)
    n_rad = gb["rad_mj_m2"].count()
    n_dias = gb.size()
    m.loc[n_rad < n_dias, ["rad_mj_m2", "eto_pm_mm"]] = np.nan
    m["deficit_mm"] = m["prec_power_mm"] - m["eto_pm_mm"]
    m = m.reset_index()
    m["mes_ts"] = pd.to_datetime(m["mes"] + "-01")
    # IMERG mensual: solo meses con todos los días (si no, el total no es comparable)
    n_im = gb["prec_imerg_mm"].count()
    im = gb["prec_imerg_mm"].sum(min_count=1).where(n_im == n_dias)
    m["prec_imerg_mm"] = im.to_numpy()

    base = m[["fips", "mes_ts", "prec_power_mm"]].rename(columns={"mes_ts": "mes", "prec_power_mm": "prec"})
    for k in (1, 3, 6):
        m[f"spi{k}"] = spi(base, k)

    b0, b1 = (pd.Timestamp(x) for x in cfg["periodo"]["anomalias_base"])
    enbase = m[(m["mes_ts"] >= b0) & (m["mes_ts"] <= b1)]
    clim = enbase.groupby(["fips", enbase["mes_ts"].dt.month])["tmed_c"].mean()
    idx = pd.MultiIndex.from_arrays([m["fips"], m["mes_ts"].dt.month])
    m["anom_tmed_c"] = m["tmed_c"].to_numpy() - clim.reindex(idx).to_numpy()
    m["anio"] = m["mes_ts"].dt.year
    return m


# --------------------------------------------------------------------------- anual

def tendencia(anual: pd.DataFrame, col: str, ventana: int = 30, minimo: int = 20) -> pd.Series:
    """Pendiente MCO por década con los años anio-ventana+1..anio (nunca años posteriores)."""
    res = pd.Series(np.nan, index=anual.index)
    for fips, g in anual.groupby("fips"):
        g = g.sort_values("anio")
        anios, vals = g["anio"].to_numpy(), g[col].to_numpy()
        for i, idx in enumerate(g.index):
            sel = (anios <= anios[i]) & (anios > anios[i] - ventana) & ~np.isnan(vals)
            if sel.sum() >= minimo:
                res[idx] = np.polyfit(anios[sel], vals[sel], 1)[0] * 10
    return res


def anual(d: pd.DataFrame, m: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["anio"] = d["fecha"].dt.year
    d["mesn"] = d["fecha"].dt.month
    d["doy"] = d["fecha"].dt.day_of_year
    hel = d["tmin_c"] <= UMBRAL_HELADA
    ult = d[hel & (d["mesn"] <= 7)].groupby(["fips", "anio"])["doy"].max()
    pri = d[hel & (d["mesn"] >= 8)].groupby(["fips", "anio"])["doy"].min()

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
    ginv = inv.groupby(["fips", "anio_inv"])["prec_power_mm"]
    pinv = ginv.sum(min_count=5)
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

    # Totales anuales calendario para tendencias (años completos)
    gy = d.groupby(["fips", "anio"])
    tot = pd.DataFrame({"prec": gy["prec_power_mm"].sum(min_count=365), "tmed": gy["tmed_c"].mean(),
                        "n": gy.size()}).reset_index()
    tot.loc[tot["n"] < 365, ["prec", "tmed"]] = np.nan
    tot["tend_prec_mm_decada"] = tendencia(tot, "prec")
    tot["tend_tmed_c_decada"] = tendencia(tot, "tmed")
    a = a.merge(tot[["fips", "anio", "tend_prec_mm_decada", "tend_tmed_c_decada"]], on=["fips", "anio"], how="left")
    return a


# --------------------------------------------------------------------------- main

def escribir(df: pd.DataFrame, cols: list[str], ruta: Path, decimales: int = 3):
    df = df[cols].copy()
    for c in cols:
        if pd.api.types.is_float_dtype(df[c]):
            df[c] = df[c].round(decimales)
    # decimales fijos: un valor real como -99.0 no se confunde con un código de relleno
    df.to_csv(ruta, index=False, encoding="utf-8", lineterminator="\n", float_format=f"%.{decimales}f")
    print(f"{ruta.relative_to(REPO).as_posix()}: {len(df)} filas")


def main():
    cfg = cargar_config()
    y0, y1 = int(cfg["periodo"]["anio_inicio"]), int(cfg["periodo"]["anio_fin"])
    fips_ok = set(pd.read_csv(CONDADOS, dtype={"fips": str})["fips"])
    archivos = sorted(RAW.glob("power_diario_*.csv"))
    d = pd.concat([leer_power(p) for p in archivos], ignore_index=True)
    d = d[d["fips"].isin(fips_ok)].sort_values(["fips", "fecha"]).reset_index(drop=True)

    d["eto_pm_mm"] = eto_fao56(d)
    tx = d["tmax_c"].clip(upper=30)
    tn = d["tmin_c"].clip(lower=10, upper=30)
    d["gdd_10_30"] = ((tx.clip(lower=10) + tn) / 2 - 10).clip(lower=0)
    d["gdd_base0"] = d["tmed_c"].clip(lower=0)
    d["prec5d"] = d.groupby("fips")["prec_power_mm"].transform(lambda s: s.rolling(5, min_periods=5).sum())
    d["mes"] = d["fecha"].dt.strftime("%Y-%m")
    im = imerg_condado()
    d = d.merge(im, on=["fips", "fecha"], how="left")

    m = mensual(d, cfg)
    a = anual(d, m)

    OUT.mkdir(parents=True, exist_ok=True)
    dd = d[d["fecha"].dt.year.between(y0, y1)].copy()
    dd["anio"] = dd["fecha"].dt.year
    dd["fecha"] = dd["fecha"].dt.strftime("%Y-%m-%d")
    escribir(dd, ["fips", "anio", "fecha", "tmed_c", "tmax_c", "tmin_c", "prec_power_mm", "prec_imerg_mm",
                  "hr_pct", "viento_ms", "rad_mj_m2", "gwettop", "gwetroot", "gwetprof", "eto_pm_mm"],
             OUT / "clima_diario.csv", 2)
    mm = m[m["anio"].between(y0, y1)]
    escribir(mm, ["fips", "anio", "mes", "prec_imerg_mm", "prec_power_mm", "tmax_c", "tmin_c", "tmed_c",
                  "rad_mj_m2", "eto_pm_mm", "deficit_mm", "dias_tmax_gt30", "dias_tmax_gt35", "dias_tmin_le0",
                  "dias_tmin_le_m2", "gdd_10_30", "gdd_base0", "dias_lluvia_ge1", "prec_max1d_mm",
                  "prec_max5d_mm", "dias_lluvia_gt50", "racha_seca_max_dias", "spi1", "spi3", "spi6",
                  "anom_tmed_c", "gwettop", "gwetroot", "gwetprof"], OUT / "clima_mensual.csv", 3)
    aa = a[a["anio"].between(y0, y1)].sort_values(["fips", "anio"])
    for c in ("doy_ultima_helada", "doy_primera_helada", "periodo_libre_heladas_dias", "dias_tmax_gt30_jul"):
        aa[c] = aa[c].astype("Int64")
    escribir(aa, ["fips", "anio", "doy_ultima_helada", "doy_primera_helada", "periodo_libre_heladas_dias",
                  "prec_temporada_mm", "gdd_temporada", "prec_invierno_previo_mm", "prec_jul_mm", "tmax_jul_c",
                  "dias_tmax_gt30_jul", "prec_ago_mm", "deficit_temporada_mm", "tend_prec_mm_decada",
                  "tend_tmed_c_decada"], OUT / "clima_anual.csv", 3)


if __name__ == "__main__":
    main()
