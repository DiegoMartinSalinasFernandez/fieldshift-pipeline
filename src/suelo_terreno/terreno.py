"""Terreno por condado desde NASADEM (teselas de 1°, 1 arcsec ≈ 30 m, EPSG:4326).

Por tesela:
- Elevación y pendiente (%) a resolución nativa; la pendiente con diferencias centradas y el
  tamaño real del píxel en metros (dx = 1" · cos(lat)).
- TWI = ln(a / tan β) a 3 arcsec (≈ 90 m, media de bloques de 3 x 3): relleno de depresiones,
  dirección de flujo D8 y acumulación con pysheds dentro de cada tesela; a = área aportante
  por ancho de celda (m), tan β con mínimo 0,001.
- Cada píxel se asigna a un condado rasterizando condados.gpkg en la grilla de la tesela.
Se acumulan sumas y un histograma de TWI por condado; el umbral del decil superior es el
percentil 90 del TWI de todos los condados juntos. La reducción va en orden fijo de teselas.
"""
from __future__ import annotations

import math
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
RAW_DEM = REPO / "data" / "raw" / "suelo_terreno" / "nasadem"
GRADO_M = 111320.0 / 3600  # metros por arcsec en el ecuador
TWI_BINS = np.arange(0, 30.0001, 0.05)
PENDIENTE_UMBRAL = 2.0
AGREGADO_TWI = 3


def _condados():
    import geopandas as gpd

    g = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg").to_crs(4326)
    g = g.sort_values("fips").reset_index(drop=True)
    return g


def _tesela(args):
    ruta, geoms = args
    import rasterio
    from rasterio import features

    with rasterio.open(ruta) as ds:
        z = ds.read(1).astype("float64")
        tr = ds.transform
        nodata = ds.nodata
    z[z == nodata] = np.nan
    # la última fila y columna de cada tesela repiten el borde de la vecina: se descartan
    a = AGREGADO_TWI
    h, w = ((z.shape[0] - 1) // a) * a, ((z.shape[1] - 1) // a) * a
    z = z[:h, :w]
    n = len(geoms)
    shapes = [(geom, i + 1) for i, geom in enumerate(geoms)]
    ids = features.rasterize(shapes, out_shape=z.shape, transform=tr, fill=0, dtype="int32")

    ok = (ids > 0) & np.isfinite(z)
    k = ids[ok]
    res = {
        "n": np.bincount(k, minlength=n + 1),
        "z": np.bincount(k, weights=z[ok], minlength=n + 1),
        "z2": np.bincount(k, weights=z[ok] ** 2, minlength=n + 1),
    }

    # pendiente y TWI a 3" (~90 m): media de bloques de 3 x 3 (reduce el ruido del DEM)
    zc = np.nanmean(z.reshape(h // a, a, w // a, a), axis=(1, 3))
    trc = tr * tr.scale(a, a)
    idc = features.rasterize(shapes, out_shape=zc.shape, transform=trc, fill=0, dtype="int32")
    pend = _pendiente(zc, trc)
    okp = (idc > 0) & np.isfinite(pend)
    kp = idc[okp]
    res["np"] = np.bincount(kp, minlength=n + 1)
    res["p"] = np.bincount(kp, weights=pend[okp], minlength=n + 1)
    res["pgt"] = np.bincount(kp, weights=(pend[okp] > PENDIENTE_UMBRAL).astype(float), minlength=n + 1)

    twi = _twi(zc, trc)
    okt = (idc > 0) & np.isfinite(twi)
    hist = np.zeros((n + 1, len(TWI_BINS) - 1))
    if okt.any():
        kt = idc[okt]
        b = np.clip(np.digitize(twi[okt], TWI_BINS) - 1, 0, len(TWI_BINS) - 2)
        np.add.at(hist, (kt, b), 1)
        res["nt"] = np.bincount(kt, minlength=n + 1)
        res["t"] = np.bincount(kt, weights=twi[okt], minlength=n + 1)
    else:
        res["nt"] = np.zeros(n + 1)
        res["t"] = np.zeros(n + 1)
    res["hist"] = hist
    return res


def _pendiente(z, tr):
    """Pendiente (%) con diferencias centradas y el tamaño real del píxel en metros."""
    filas = np.arange(z.shape[0])
    lat = tr.f + (filas + 0.5) * tr.e
    dy = abs(tr.e) * 3600 * GRADO_M
    dx = (abs(tr.a) * 3600 * GRADO_M * np.cos(np.radians(lat)))[:, None]
    gy, gx = np.gradient(z)
    return 100 * np.hypot(gx / dx, gy / dy)


def _twi(z, tr):
    from pysheds.grid import Grid
    from pysheds.sview import Raster, ViewFinder

    if not hasattr(np, "in1d"):  # pysheds 0.5 usa np.in1d, que numpy 2 quitó
        np.in1d = np.isin
    nod = -9999.0
    zz = np.where(np.isfinite(z), z, nod)
    vf = ViewFinder(affine=tr, shape=zz.shape, crs="EPSG:4326", nodata=nod)
    dem = Raster(zz, viewfinder=vf)
    grid = Grid(viewfinder=vf)
    dem = grid.fill_pits(dem)
    dem = grid.fill_depressions(dem)
    dem = grid.resolve_flats(dem)
    fdir = grid.flowdir(dem, nodata_out=np.int64(0))
    acc = np.asarray(grid.accumulation(fdir, nodata_out=np.float64(0)), dtype="float64")

    filas = np.arange(z.shape[0])
    lat = tr.f + (filas + 0.5) * tr.e
    dy = abs(tr.e) * 3600 * GRADO_M
    dx = (abs(tr.a) * 3600 * GRADO_M * np.cos(np.radians(lat)))[:, None]
    tanb = np.maximum(_pendiente(z, tr) / 100, 0.001)
    ancho = np.sqrt(dx * dy)
    a_esp = np.maximum(acc, 1) * dx * dy / ancho
    twi = np.log(a_esp / tanb)
    twi[~np.isfinite(z)] = np.nan
    return twi


def terreno_por_condado() -> pd.DataFrame:
    g = _condados()
    rutas = sorted(RAW_DEM.glob("NASADEM_HGT_*.tif"))
    import rasterio
    from shapely.geometry import box

    tareas = []
    for ruta in rutas:
        with rasterio.open(ruta) as ds:
            b = box(*ds.bounds)
        sel = g.geometry.intersects(b)
        # geometrías de todos los condados (índices globales); solo las que tocan la tesela
        geoms = [geom if s else None for geom, s in zip(g.geometry, sel)]
        if sel.any():
            tareas.append((ruta, geoms))
    n = len(g)
    tot = None
    workers = max(1, min(8, (os.cpu_count() or 2) - 1))
    tareas_ok = [(r, [geo if geo is not None else _vacio() for geo in gs]) for r, gs in tareas]
    with ProcessPoolExecutor(workers) as ex:
        for res in ex.map(_tesela, tareas_ok):  # orden fijo
            if tot is None:
                tot = {k: np.zeros_like(v, dtype="float64") for k, v in res.items()}
            for k, v in res.items():
                tot[k] += v
    if tot is None:
        return pd.DataFrame({"fips": g["fips"].astype(str)})
    s = slice(1, n + 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        media = tot["z"][s] / tot["n"][s]
        desvio = np.sqrt(np.maximum(tot["z2"][s] / tot["n"][s] - media ** 2, 0))
        pend = tot["p"][s] / tot["np"][s]
        pgt = 100 * tot["pgt"][s] / tot["np"][s]
        twi = tot["t"][s] / tot["nt"][s]
        hist = tot["hist"][s]
        acum = np.cumsum(hist.sum(axis=0))
        corte = int(np.searchsorted(acum, 0.9 * acum[-1]))  # bin del percentil 90 global
        dec = 100 * hist[:, corte + 1:].sum(axis=1) / hist.sum(axis=1)
    out = pd.DataFrame({
        "fips": g["fips"].astype(str).str.zfill(5),
        "elevacion_media_m": media, "elevacion_desvio_m": desvio,
        "pendiente_media_pct": pend, "pendiente_gt2_pct": pgt,
        "twi_medio": twi, "twi_decil_sup_pct": dec,
    })
    # condados con cobertura incompleta de teselas quedan vacíos
    out.attrs["umbral_twi_p90"] = float(TWI_BINS[corte + 1])
    return out


def _vacio():
    from shapely.geometry import Point

    return Point(1000, 1000).buffer(0.0001)  # fuera de toda tesela: no rasteriza


if __name__ == "__main__":
    print(terreno_por_condado().describe())
