"""Procesa MODIS (data/raw/vegetacion/) a CSV por condado.

Salidas en data/processed/vegetacion/:
- vegetacion_16d.csv     fips, anio, fecha, ndvi, evi, ndvi_maiz, ndvi_soja, frac_pixeles_validos
- vegetacion_mensual.csv fips, anio, mes, ndvi, evi, ndvi_maiz, ndvi_soja, lst_dia_c, lst_noche_c,
                         et_mm, pet_mm, et_pet_ratio, ndvi_anom_z, vci, tci, vhi
- fenologia_anual.csv    fips, anio, doy_inicio, doy_pico, doy_fin, ndvi_max, duracion_dias,
                         ndvi_integral, n_ciclos, ndvi_max_maiz, ndvi_max_soja, dias_ndvi_lt03_invierno

Calidad: un píxel cuenta si su valor está en el rango válido del producto, no toca (3x3) un píxel
sin dato o fuera de rango (los overviews del COG remuestrean y dejan artefactos en los bordes)
y, en MOD13Q1, si pixel reliability es 0 (bueno) o 1 (marginal).
Uso: python src/vegetacion/process.py
"""
from __future__ import annotations

import datetime as dt
import sys
import time
from collections import defaultdict
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.features import rasterize
from rasterio.warp import reproject
from scipy.ndimage import binary_erosion
from scipy.signal import find_peaks, savgol_filter

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

RAW = REPO / "data" / "raw" / "vegetacion"
OUT = REPO / "data" / "processed" / "vegetacion"

# Umbrales de fenología (documentados en el data card)
SG_VENTANA, SG_ORDEN = 5, 2          # Savitzky-Golay sobre la serie de 16 días
UMBRAL_AMPLITUD = 0.5                # inicio/fin: cruce del 50 % de la amplitud (mín. a máx. del año)
PROMINENCIA_CICLO = 0.1              # un ciclo es un pico con prominencia >= 0.1 de NDVI
UMBRAL_INVIERNO = 0.3                # dias_ndvi_lt03_invierno: NDVI < 0.3 entre nov (anio-1) y mar
EST = np.ones((3, 3), bool)
UMBRAL_CULTIVO = 0.75                # NDVI de maíz/soja: el píxel MODIS cuenta si >= 75 % de su área es del cultivo
LAMBDA_VAP = 2.501e6                 # J/kg, calor latente de vaporización (constante del modelo Noah) para PET W m-2 -> mm
INTERIM = REPO / "data" / "interim" / "vegetacion"
REF = REPO / "data" / "reference"


def condados() -> gpd.GeoDataFrame:
    g = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg")
    return g.sort_values("fips").reset_index(drop=True)


class Zonas:
    """Raster de índice de condado (1..N) por grilla (crs, transform, forma), cacheado en memoria."""

    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf, self.cache, self.n = gdf, {}, len(gdf)

    def get(self, src) -> np.ndarray:
        k = (src.crs.to_wkt(), tuple(src.transform)[:6], src.shape)
        if k not in self.cache:
            g = self.gdf.to_crs(src.crs)
            self.cache[k] = rasterize(((geom, i + 1) for i, geom in enumerate(g.geometry)),
                                      out_shape=src.shape, transform=src.transform, fill=0, dtype="int32")
        return self.cache[k]


def tesela(nombre: str) -> str:
    return nombre.split(".")[2]  # h10v04


class Cultivos:
    """Fracción de cada píxel MODIS cubierta por maíz o soja según las máscaras del CDL (30 m).

    La máscara se agrega primero a bloques de 8x8 (240 m, fracción exacta) y después se reproyecta
    con promedio a la grilla de cada tesela. Se cachea en data/interim/vegetacion/ (regenerable).
    """

    def __init__(self):
        self.mem = {}

    def frac(self, cultivo: str, anio: int, src) -> np.ndarray | None:
        ruta = REF / f"mascara_{cultivo}_{anio}.tif"
        if not ruta.exists():
            return None
        k = (cultivo, anio, src.crs.to_wkt(), tuple(src.transform)[:6], src.shape)
        if k in self.mem:
            return self.mem[k]
        h = abs(hash((tuple(round(x, 3) for x in tuple(src.transform)[:6]), src.shape))) % 10**8
        cache = INTERIM / "frac_cultivos" / f"{cultivo}_{anio}_{h:08d}.npy"
        if cache.exists():
            out = np.load(cache)
        else:
            if (cultivo, anio) not in self.mem:
                with rasterio.open(ruta) as m:
                    a = m.read(1)
                    H, W = a.shape[0] // 8, a.shape[1] // 8
                    f = (a[:H * 8, :W * 8] == 1).reshape(H, 8, W, 8).sum(axis=(1, 3), dtype=np.uint16)
                    f = (f / 64.0).astype("float32")
                    self.mem[(cultivo, anio)] = (f, m.transform * m.transform.scale(8, 8), m.crs)
            f, tr, crs = self.mem[(cultivo, anio)]
            out = np.full(src.shape, np.nan, "float32")
            reproject(f, out, src_transform=tr, src_crs=crs, dst_transform=src.transform, dst_crs=src.crs,
                      resampling=Resampling.average, src_nodata=None, dst_nodata=np.nan)
            cache.parent.mkdir(parents=True, exist_ok=True)
            np.save(cache, out)
        self.mem[k] = out
        return out

    def liberar(self, anio: int) -> None:
        for c in ("maiz", "soja"):
            self.mem.pop((c, anio), None)


def fecha_item(nombre: str) -> dt.date:
    a = nombre.split(".")[1]  # A2025161
    return dt.date(int(a[1:5]), 1, 1) + dt.timedelta(days=int(a[5:8]) - 1)


def sumar(acc, z, valido, dentro, valores: dict, n: int) -> None:
    acc["dentro"] += np.bincount(z[dentro], minlength=n + 1)
    zv = z[valido]
    acc["validos"] += np.bincount(zv, minlength=n + 1)
    for k, v in valores.items():
        acc[k] += np.bincount(zv, weights=v[valido].astype("float64"), minlength=n + 1)


def zonal_producto(carpeta: str, zonas: Zonas, fn_validos, claves: list[str], cultivos: Cultivos | None = None) -> pd.DataFrame:
    acc = defaultdict(lambda: defaultdict(lambda: np.zeros(zonas.n + 1)))
    anio_prev = None
    # si hay más de una versión de producción del mismo compuesto y tesela, se usa la más reciente
    ultimo = {}
    for p in sorted((RAW / carpeta).rglob("*.tif"), key=lambda x: x.name):
        ultimo[(fecha_item(p.name), tesela(p.name))] = p
    for p in sorted(ultimo.values(), key=lambda x: x.name):
        f = fecha_item(p.name)
        if cultivos is not None and anio_prev is not None and f.year != anio_prev:
            cultivos.liberar(anio_prev)
        anio_prev = f.year
        with rasterio.open(p) as src:
            z = zonas.get(src)
            bandas = src.read()
            valido, valores = fn_validos(bandas)
            dentro = z > 0
            sumar(acc[f], z, valido & dentro, dentro, valores, zonas.n)
            if cultivos is not None:
                for c in ("maiz", "soja"):
                    fr = cultivos.frac(c, f.year, src)
                    if fr is None:
                        continue
                    vc = valido & dentro & (fr >= UMBRAL_CULTIVO)
                    acc[f][f"n_{c}"] += np.bincount(z[vc], minlength=zonas.n + 1)
                    acc[f][f"ndvi_{c}"] += np.bincount(z[vc], weights=valores["ndvi"][vc], minlength=zonas.n + 1)
    filas = []
    fips = zonas.gdf["fips"].to_numpy()
    for f in sorted(acc):
        a = acc[f]
        d = pd.DataFrame({"fips": fips, "fecha": f, "dentro": a["dentro"][1:], "validos": a["validos"][1:]})
        for k in claves:
            with np.errstate(invalid="ignore", divide="ignore"):
                d[k] = np.where(d["validos"] > 0, a[k][1:] / np.maximum(a["validos"][1:], 1), np.nan)
        if cultivos is not None:
            for c in ("maiz", "soja"):
                n = a[f"n_{c}"][1:] if f"n_{c}" in a else np.zeros(zonas.n)
                s_ = a[f"ndvi_{c}"][1:] if f"ndvi_{c}" in a else np.zeros(zonas.n)
                d[f"ndvi_{c}"] = np.where(n > 0, s_ / np.maximum(n, 1), np.nan)
        filas.append(d)
    return pd.concat(filas, ignore_index=True) if filas else pd.DataFrame()


def validos_mod13(b):
    ndvi, evi, rel = b[0].astype("int32"), b[1].astype("int32"), b[2].astype("int32")
    rango = (ndvi >= -2000) & (ndvi <= 10000) & (evi >= -2000) & (evi <= 10000)
    v = binary_erosion(rango, EST, border_value=0) & np.isin(rel, (0, 1))
    return v, {"ndvi": ndvi / 10000.0, "evi": evi / 10000.0}


def validos_mod11(b):
    dia, noche = b[0].astype("int32"), b[1].astype("int32")
    # LST valid_range 7500-65535 (escala 0.02 K); se exige además que el día y la noche sean válidos
    rango = (dia >= 7500) & (noche >= 7500)
    v = binary_erosion(rango, EST, border_value=0)
    return v, {"lst_dia_c": dia * 0.02 - 273.15, "lst_noche_c": noche * 0.02 - 273.15}


def fenologia(g: pd.DataFrame) -> list[dict]:
    """g: serie 16d de un condado (todas las fechas). Devuelve una fila por año."""
    g = g.sort_values("fecha")
    t = np.array([(pd.Timestamp(x) + pd.Timedelta(days=8)).toordinal() for x in g["fecha"]], float)
    y = g["ndvi"].to_numpy(float)
    ok = np.isfinite(y)
    filas = []
    if ok.sum() < 6:
        return filas
    # serie diaria interpolada (solo dentro del rango con datos)
    dias = np.arange(t[ok].min(), t[ok].max() + 1)
    diaria = np.interp(dias, t[ok], y[ok])
    anios = sorted({pd.Timestamp(x).year for x in g["fecha"]})
    for anio in anios:
        fila = {"anio": anio}
        sel = np.array([pd.Timestamp(x).year == anio for x in g["fecha"]])
        for c in ("maiz", "soja"):  # máximo de los compuestos (filtrados por calidad) del año
            vc = g[f"ndvi_{c}"].to_numpy(float)[sel]
            if np.isfinite(vc).sum() >= 10:
                fila[f"ndvi_max_{c}"] = float(np.nanmax(vc))
        ys, ts = y[sel], t[sel]
        if np.isfinite(ys).sum() >= 15:
            yi = np.interp(ts, ts[np.isfinite(ys)], ys[np.isfinite(ys)])
            sm = savgol_filter(yi, SG_VENTANA, SG_ORDEN)
            ipk = int(np.argmax(sm))
            base, mx = float(np.min(sm)), float(sm[ipk])
            umbral = base + UMBRAL_AMPLITUD * (mx - base)
            doy = np.array([dt.date.fromordinal(int(x)).timetuple().tm_yday for x in ts], float)
            ini = fin = np.nan
            for i in range(ipk, 0, -1):
                if sm[i - 1] < umbral <= sm[i]:
                    ini = doy[i - 1] + (umbral - sm[i - 1]) / (sm[i] - sm[i - 1]) * (doy[i] - doy[i - 1])
                    break
            for i in range(ipk, len(sm) - 1):
                if sm[i] >= umbral > sm[i + 1]:
                    fin = doy[i] + (sm[i] - umbral) / (sm[i] - sm[i + 1]) * (doy[i + 1] - doy[i])
                    break
            fila.update(doy_pico=doy[ipk], ndvi_max=mx, doy_inicio=ini, doy_fin=fin)
            if np.isfinite(ini) and np.isfinite(fin):
                fila["duracion_dias"] = fin - ini
                xs = np.arange(np.ceil(ini), np.floor(fin) + 1)
                fila["ndvi_integral"] = float(np.trapezoid(np.interp(xs, doy, sm), xs))
            pk, _ = find_peaks(np.r_[-np.inf, sm, -np.inf], prominence=PROMINENCIA_CICLO)
            fila["n_ciclos"] = len(pk)
        # invierno previo: 1 de noviembre de anio-1 a 31 de marzo de anio, NDVI diario interpolado
        i0, i1 = dt.date(anio - 1, 11, 1).toordinal(), dt.date(anio, 3, 31).toordinal()
        if dias.size and i0 >= dias[0] and i1 <= dias[-1]:
            w = diaria[(dias >= i0) & (dias <= i1)]
            fila["dias_ndvi_lt03_invierno"] = int((w < UMBRAL_INVIERNO).sum())
        filas.append(fila)
    return filas


def nldas_mensual(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """ET y PET mensuales de NLDAS-2 Noah por condado: media ponderada por la fracción de cada
    celda de 0,125° dentro del condado (supermuestreo 10x de la grilla). Sustituye a MOD16A2."""
    import xarray as xr
    from rasterio.transform import from_origin

    archivos = sorted((RAW / "nldas_noah_m").rglob("*.nc"))
    if not archivos:
        return pd.DataFrame(columns=["fips", "mes", "et_mm", "pet_mm"])
    with xr.open_dataset(archivos[0]) as d0:
        lat, lon = d0["lat"].values.astype(float), d0["lon"].values.astype(float)
    ny, nx, k = len(lat), len(lon), 10
    paso = 0.125
    tr = from_origin(lon.min() - paso / 2, lat.max() + paso / 2, paso / k, paso / k)
    g = gdf.to_crs("EPSG:4326")
    fino = rasterize(((geom, i + 1) for i, geom in enumerate(g.geometry)), out_shape=(ny * k, nx * k),
                     transform=tr, fill=0, dtype="int32")
    filas_f, cols_f = np.nonzero(fino)
    celda = (filas_f // k) * nx + (cols_f // k)   # índice de celda en la grilla norte-arriba
    zona = fino[filas_f, cols_f] - 1
    w = np.zeros((len(g), ny * nx))
    np.add.at(w, (zona, celda), 1.0)
    salida = []
    for p in archivos:
        with xr.open_dataset(p) as d:
            mes = pd.Timestamp(d["time"].values[0]).strftime("%Y-%m")
            dias = pd.Timestamp(d["time"].values[0]).days_in_month
            if not np.allclose(d["lat"].values, lat) or not np.allclose(d["lon"].values, lon):
                raise ValueError(f"grilla distinta en {p.name}")
            vals = {}
            for var in ["Evap", "PotEvap"]:
                a = d[var].values[0].astype(float)
                a = np.where(np.isfinite(a) & (a > -9000), a, np.nan)
                if d["lat"].values[0] < d["lat"].values[-1]:
                    a = a[::-1]                        # a norte-arriba, como el raster fino
                vals[var] = a.ravel()
        for var, col, fac in [("Evap", "et_mm", 1.0),                               # kg m-2 (suma del mes) = mm
                              ("PotEvap", "pet_mm", 86400 * dias / LAMBDA_VAP)]:    # W m-2 (media) -> mm/mes
            v = vals[var]
            ok = np.isfinite(v)
            num = w[:, ok] @ v[ok]
            den = w[:, ok].sum(axis=1)
            frac = den / np.maximum(w.sum(axis=1), 1)
            res = np.where(frac >= 0.5, num / np.maximum(den, 1e-9), np.nan) * fac
            vals[col] = res
        salida.append(pd.DataFrame({"fips": g["fips"].values, "mes": mes,
                                    "et_mm": vals["et_mm"], "pet_mm": vals["pet_mm"]}))
    return pd.concat(salida, ignore_index=True)


def escribir(df: pd.DataFrame, nombre: str, dec: dict) -> None:
    df = df.copy()
    for c, d in dec.items():
        if c in df:
            df[c] = df[c].map(lambda v, d=d: "" if pd.isna(v) else f"{v:.{d}f}")
    df.to_csv(OUT / nombre, index=False, encoding="utf-8", lineterminator="\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    gdf = condados()
    zonas = Zonas(gdf)

    v16 = zonal_producto("mod13q1", zonas, validos_mod13, ["ndvi", "evi"], Cultivos())
    print(f"mod13q1 zonal: {time.time() - t0:.0f}s, {len(v16)} filas")
    v16["frac_pixeles_validos"] = np.where(v16["dentro"] > 0, v16["validos"] / v16["dentro"].clip(lower=1), np.nan)
    v16["anio"] = pd.to_datetime(v16["fecha"]).dt.year
    v16["fecha"] = pd.to_datetime(v16["fecha"]).dt.strftime("%Y-%m-%d")
    v16 = v16[["fips", "anio", "fecha", "ndvi", "evi", "ndvi_maiz", "ndvi_soja", "frac_pixeles_validos"]]
    v16 = v16.sort_values(["fips", "fecha"]).reset_index(drop=True)
    escribir(v16, "vegetacion_16d.csv", {"ndvi": 4, "evi": 4, "ndvi_maiz": 4, "ndvi_soja": 4,
                                         "frac_pixeles_validos": 4})

    t1 = time.time()
    lst = zonal_producto("mod11a2", zonas, validos_mod11, ["lst_dia_c", "lst_noche_c"])
    print(f"mod11a2 zonal: {time.time() - t1:.0f}s, {len(lst)} filas")

    # mensual: media de los compuestos cuya fecha de inicio cae en el mes
    m = v16.assign(mes=v16["fecha"].str[:7]).groupby(["fips", "mes"], as_index=False)[
        ["ndvi", "evi", "ndvi_maiz", "ndvi_soja"]].mean()
    if len(lst):
        lst["mes"] = pd.to_datetime(lst["fecha"]).dt.strftime("%Y-%m")
        ml = lst.groupby(["fips", "mes"], as_index=False)[["lst_dia_c", "lst_noche_c"]].mean()
        m = m.merge(ml, on=["fips", "mes"], how="outer")
    else:
        m["lst_dia_c"] = np.nan
        m["lst_noche_c"] = np.nan
    t3 = time.time()
    et = nldas_mensual(gdf)
    print(f"nldas et/pet: {time.time() - t3:.0f}s, {len(et)} filas")
    if len(et):
        m = m.merge(et, on=["fips", "mes"], how="left")
    else:
        m["et_mm"] = np.nan
        m["pet_mm"] = np.nan
    m["et_pet_ratio"] = (m["et_mm"] / m["pet_mm"]).where(m["pet_mm"] > 1)  # con PET ~0 el cociente no tiene sentido
    m["anio"] = m["mes"].str[:4].astype(int)
    m["mm"] = m["mes"].str[5:7]
    grp = m.groupby(["fips", "mm"])
    mu, sd = grp["ndvi"].transform("mean"), grp["ndvi"].transform("std")
    m["ndvi_anom_z"] = ((m["ndvi"] - mu) / sd).where(sd > 0)
    nmin, nmax = grp["ndvi"].transform("min"), grp["ndvi"].transform("max")
    m["vci"] = (100 * (m["ndvi"] - nmin) / (nmax - nmin)).where(nmax > nmin)
    tmin, tmax = grp["lst_dia_c"].transform("min"), grp["lst_dia_c"].transform("max")
    m["tci"] = (100 * (tmax - m["lst_dia_c"]) / (tmax - tmin)).where(tmax > tmin)
    m["vhi"] = 0.5 * m["vci"] + 0.5 * m["tci"]
    cols = ["fips", "anio", "mes", "ndvi", "evi", "ndvi_maiz", "ndvi_soja", "lst_dia_c", "lst_noche_c",
            "et_mm", "pet_mm", "et_pet_ratio", "ndvi_anom_z", "vci", "tci", "vhi"]
    m = m[cols].sort_values(["fips", "mes"]).reset_index(drop=True)
    escribir(m, "vegetacion_mensual.csv", {**{c: 4 for c in ["ndvi", "evi", "ndvi_maiz", "ndvi_soja", "et_pet_ratio",
                                                            "ndvi_anom_z"]},
                                          **{c: 2 for c in ["lst_dia_c", "lst_noche_c", "et_mm", "pet_mm",
                                                            "vci", "tci", "vhi"]}})

    t2 = time.time()
    filas = []
    for f, g in v16.groupby("fips", sort=True):
        for r in fenologia(g):
            filas.append({"fips": f, **r})
    fen = pd.DataFrame(filas)
    cols = ["fips", "anio", "doy_inicio", "doy_pico", "doy_fin", "ndvi_max", "duracion_dias", "ndvi_integral",
            "n_ciclos", "ndvi_max_maiz", "ndvi_max_soja", "dias_ndvi_lt03_invierno"]
    for c in cols:
        if c not in fen:
            fen[c] = np.nan
    fen = fen[cols].sort_values(["fips", "anio"]).reset_index(drop=True)
    fen["n_ciclos"] = fen["n_ciclos"].astype("Int64")
    fen["dias_ndvi_lt03_invierno"] = fen["dias_ndvi_lt03_invierno"].astype("Int64")
    escribir(fen, "fenologia_anual.csv", {"doy_inicio": 1, "doy_pico": 0, "doy_fin": 1, "ndvi_max": 4,
                                          "duracion_dias": 1, "ndvi_integral": 2, "ndvi_max_maiz": 4,
                                          "ndvi_max_soja": 4})
    print(f"fenologia: {time.time() - t2:.0f}s; total {time.time() - t0:.0f}s")

    import data_card  # mismo directorio: tabla del data card desde los CSV recién escritos
    data_card.main()


if __name__ == "__main__":
    main()
