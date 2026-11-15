"""Procesa el paquete agua → data/processed/agua/.

agua_semanal.csv: percentiles de GRACE-DA-DM (US, 0,125°) por condado, media ponderada por la
fracción del condado que cae en cada celda (fracciones calculadas rasterizando los condados a
una grilla 10 veces más fina). Lee solo data/raw/agua/grace/*.nc4.

SMAP L4 (agua_diario.csv, agua_mensual.csv) no se procesa: sin Earthdata no hay acceso
(ver docs/datasets/agua.md).

Uso: python src/agua/process.py
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

RAW = REPO / "data" / "raw" / "agua" / "grace"
OUT = REPO / "data" / "processed" / "agua"
CONDADOS = REPO / "data" / "reference" / "condados.gpkg"

# Grilla de GRACEDADM_CLSM0125US_7D (atributos del archivo: SOUTH_WEST_CORNER_LAT/LON, DX, DY).
SW_LAT, SW_LON, DX = 25.0625, -124.9375, 0.125
NLAT, NLON = 224, 464
VARS = {"gws_inst": "gws_pctl", "rtzsm_inst": "rtzsm_pctl", "sfsm_inst": "sfsm_pctl"}
FINO = 10  # subdivisiones por celda para calcular fracciones


def pesos_condados():
    """Devuelve fips (lista), índices planos de celda y matriz de pesos (condado x celda)."""
    import geopandas as gpd
    from rasterio import features
    from rasterio.transform import from_origin

    gdf = gpd.read_file(CONDADOS).to_crs("EPSG:4326").sort_values("fips").reset_index(drop=True)
    # Ventana de la grilla que cubre los condados (en índices de celda; fila 0 = sur).
    xmin, ymin, xmax, ymax = gdf.total_bounds
    c0 = int(np.floor((xmin - (SW_LON - DX / 2)) / DX)) - 1
    c1 = int(np.ceil((xmax - (SW_LON - DX / 2)) / DX)) + 1
    r0 = int(np.floor((ymin - (SW_LAT - DX / 2)) / DX)) - 1
    r1 = int(np.ceil((ymax - (SW_LAT - DX / 2)) / DX)) + 1
    nr, nc = r1 - r0, c1 - c0
    oeste = SW_LON - DX / 2 + c0 * DX
    norte = SW_LAT - DX / 2 + r1 * DX
    tr = from_origin(oeste, norte, DX / FINO, DX / FINO)
    shapes = ((g.__geo_interface__, i + 1) for i, g in enumerate(gdf.geometry))
    ids = features.rasterize(shapes, out_shape=(nr * FINO, nc * FINO), transform=tr, fill=0,
                             dtype="int32")
    # filas del raster fino van de norte a sur: invertir para que la fila 0 sea el sur
    ids = ids[::-1]
    W = np.zeros((len(gdf), nr * nc), dtype="float64")
    rr, cc = np.nonzero(ids)
    celda = (rr // FINO) * nc + (cc // FINO)
    np.add.at(W, (ids[rr, cc] - 1, celda), 1.0)
    # índice plano en la grilla completa
    filas = np.arange(nr * nc) // nc + r0
    cols = np.arange(nr * nc) % nc + c0
    usadas = W.sum(axis=0) > 0
    return list(gdf["fips"]), filas[usadas], cols[usadas], W[:, usadas]


def leer(p: Path, filas, cols) -> dict[str, np.ndarray]:
    import h5py

    out = {}
    with h5py.File(p, "r") as h:
        for v in VARS:
            d = h[v]
            a = d[0] if d.ndim == 3 else d[()]
            a = a[filas, cols].astype("float64")
            fill = [d.attrs.get(k) for k in ("_FillValue", "missing_value")]
            for f in fill:
                if f is not None:
                    a[a == np.asarray(f).ravel()[0]] = np.nan
            a[(a < 0) | (a > 100) | ~np.isfinite(a)] = np.nan
            out[v] = a
    return out


def semanal() -> pd.DataFrame:
    t = time.time()
    fips, filas, cols, W = pesos_condados()
    archivos = sorted(RAW.glob("GRACEDADM_CLSM0125US_7D.A*.nc4"))
    bloques = []
    for p in archivos:
        f = re.search(r"\.A(\d{8})\.", p.name).group(1)
        fecha = f"{f[:4]}-{f[4:6]}-{f[6:]}"
        datos = leer(p, filas, cols)
        df = pd.DataFrame({"fips": fips, "anio": int(f[:4]), "fecha": fecha})
        for v, col in VARS.items():
            a = datos[v]
            ok = np.isfinite(a)
            num = W @ np.where(ok, a, 0.0)
            den = W @ ok.astype("float64")
            with np.errstate(invalid="ignore", divide="ignore"):
                df[col] = np.where(den > 0, num / den, np.nan)
        bloques.append(df)
    out = pd.concat(bloques, ignore_index=True).sort_values(["fips", "fecha"]).reset_index(drop=True)
    print(f"semanal: {len(archivos)} semanas, {len(out)} filas, {time.time() - t:.1f} s")
    return out


SMAP_RAW = REPO / "data" / "raw" / "agua" / "smap"
SMAP_CAPAS = {"TOP": "sm_surface_m3m3", "SUB": "sm_rootzone_m3m3"}
UMBRAL_SATURADO = 0.40  # m3/m3 de sm_rootzone (media diaria del condado); ver data card
SM_MAX = 0.60  # celdas por encima (suelos orgánicos o agua en el modelo) se excluyen; ver data card


def pesos_smap(gdf_estado, shape, transform):
    """Matriz (condados del estado x celdas) con la fracción del condado en cada celda de 9 km."""
    from rasterio import features
    from rasterio.transform import Affine

    fino = Affine(transform.a / FINO, transform.b, transform.c, transform.d, transform.e / FINO, transform.f)
    shapes = ((g.__geo_interface__, i + 1) for i, g in enumerate(gdf_estado.geometry))
    ids = features.rasterize(shapes, out_shape=(shape[0] * FINO, shape[1] * FINO), transform=fino,
                             fill=0, dtype="int32")
    W = np.zeros((len(gdf_estado), shape[0] * shape[1]), dtype="float64")
    rr, cc = np.nonzero(ids)
    np.add.at(W, (ids[rr, cc] - 1, (rr // FINO) * shape[1] + (cc // FINO)), 1.0)
    return W


def diario_smap() -> pd.DataFrame:
    import geopandas as gpd
    import rasterio

    t = time.time()
    gdf = gpd.read_file(CONDADOS).to_crs("EPSG:5070").sort_values("fips").reset_index(drop=True)
    gdf["fips_estado"] = gdf["fips"].str[:2]
    patron = re.compile(r"SMAP-9KM-DAILY-(TOP|SUB)_(\d{4})\.(\d{2})\.(\d{2})_\d+_FIPS_(\d{2})\.tif")
    archivos = {}
    for p in sorted(SMAP_RAW.glob("*/*.tif")):
        m = patron.fullmatch(p.name)
        if m:
            archivos[(m.group(5), f"{m.group(2)}-{m.group(3)}-{m.group(4)}", m.group(1))] = p
    cache = {}
    filas = []
    for (est, fecha, capa), p in sorted(archivos.items()):
        sub = gdf[gdf["fips_estado"] == est]
        with rasterio.open(p) as src:
            a = src.read(1).astype("float64")
            nd = src.nodata
            clave = (est, src.shape, tuple(src.transform)[:6])
            if clave not in cache:
                cache[clave] = pesos_smap(sub, src.shape, src.transform)
            W = cache[clave]
        a = a.ravel()
        ok = np.isfinite(a) & (a != nd) & (a >= 0) & (a <= SM_MAX)
        num = W @ np.where(ok, a, 0.0)
        den = W @ ok.astype("float64")
        with np.errstate(invalid="ignore", divide="ignore"):
            v = np.where(den > 0, num / den, np.nan)
        filas.append(pd.DataFrame({"fips": sub["fips"].to_numpy(), "fecha": fecha, "capa": capa, "v": v}))
    if not filas:
        return pd.DataFrame(columns=["fips", "anio", "fecha", *SMAP_CAPAS.values()])
    largo = pd.concat(filas, ignore_index=True)
    df = largo.pivot_table(index=["fips", "fecha"], columns="capa", values="v", dropna=False).reset_index()
    df = df.rename(columns=SMAP_CAPAS)
    for c in SMAP_CAPAS.values():
        if c not in df:
            df[c] = np.nan
    df.insert(1, "anio", df["fecha"].str[:4].astype(int))
    df = df[["fips", "anio", "fecha", *SMAP_CAPAS.values()]].sort_values(["fips", "fecha"]).reset_index(drop=True)
    print(f"smap diario: {len(archivos)} archivos, {len(df)} filas, {time.time() - t:.1f} s")
    return df


def mensual_smap(d: pd.DataFrame) -> pd.DataFrame:
    d = d[d["fecha"] >= "2015-04-01"].copy()  # SMAP L4 empieza el 2015-03-31: marzo no está completo
    d["mes"] = d["fecha"].str[:7]
    g = d.groupby(["fips", "mes"])
    m = g.agg(sm_surface_m3m3=("sm_surface_m3m3", "mean"), sm_rootzone_m3m3=("sm_rootzone_m3m3", "mean"),
              sm_surface_min_m3m3=("sm_surface_m3m3", "min"),
              sm_rootzone_min_m3m3=("sm_rootzone_m3m3", "min"),
              n_surf=("sm_surface_m3m3", "count"), n_root=("sm_rootzone_m3m3", "count"),
              dias_sm_saturado=("sm_rootzone_m3m3", lambda s: int((s >= UMBRAL_SATURADO).sum()))).reset_index()
    dias_mes = pd.to_datetime(m["mes"] + "-01").dt.days_in_month
    # Solo meses completos (todos los días con dato); si no, la celda queda vacía.
    inc_s = m["n_surf"] < dias_mes
    inc_r = m["n_root"] < dias_mes
    m.loc[inc_s, ["sm_surface_m3m3", "sm_surface_min_m3m3"]] = np.nan
    m.loc[inc_r, ["sm_rootzone_m3m3", "sm_rootzone_min_m3m3"]] = np.nan
    m["dias_sm_saturado"] = m["dias_sm_saturado"].astype("float64").where(~inc_r)
    # Anomalía z de la zona radicular por condado y mes calendario (todos los años con mes completo).
    m["mes_cal"] = m["mes"].str[5:7]
    gr = m.groupby(["fips", "mes_cal"])["sm_rootzone_m3m3"]
    media, desvio, n = gr.transform("mean"), gr.transform("std"), gr.transform("count")
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (m["sm_rootzone_m3m3"] - media) / desvio
    m["sm_rootzone_anom_z"] = z.where((n >= 3) & (desvio > 0))
    m.insert(1, "anio", m["mes"].str[:4].astype(int))
    cols = ["fips", "anio", "mes", "sm_surface_m3m3", "sm_rootzone_m3m3", "sm_surface_min_m3m3",
            "sm_rootzone_min_m3m3", "sm_rootzone_anom_z", "dias_sm_saturado"]
    return m[cols].sort_values(["fips", "mes"]).reset_index(drop=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = semanal()
    df.to_csv(OUT / "agua_semanal.csv", index=False, float_format="%.2f", encoding="utf-8",
              lineterminator="\n")
    d = diario_smap()
    d.to_csv(OUT / "agua_diario.csv", index=False, float_format="%.4f", encoding="utf-8", lineterminator="\n")
    m = mensual_smap(d)
    m["dias_sm_saturado"] = m["dias_sm_saturado"].astype("Int64")
    m.to_csv(OUT / "agua_mensual.csv", index=False, float_format="%.4f", encoding="utf-8", lineterminator="\n")
    from src.agua import data_card

    data_card.main()


if __name__ == "__main__":
    main()
