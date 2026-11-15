"""Derivadas del terreno de NASADEM para los lotes (CLAUDE.md §6.6).

Todo se calcula en la grilla original de NASADEM (1", EPSG:4326) sobre una ventana del lote más 2,5 km
de margen, y recién después se remuestrea con interpolación bilineal a los centros de 30 m del lote.
"""
from __future__ import annotations

import heapq
import math

import numpy as np
import rasterio
from rasterio.merge import merge
from scipy import ndimage

MARGEN_M = 2500.0
SIGMA_CELDAS = 1.0
M_POR_GRADO = 111320.0


def ventana_dem(rutas, lon0, lat0, lon1, lat1):
    dlat = MARGEN_M / M_POR_GRADO
    dlon = MARGEN_M / (M_POR_GRADO * math.cos(math.radians((lat0 + lat1) / 2)))
    bounds = (lon0 - dlon, lat0 - dlat, lon1 + dlon, lat1 + dlat)
    dss = [rasterio.open(r) for r in rutas]
    try:
        a, tr = merge(dss, bounds=bounds, nodata=-32768, dtype="float64")
    finally:
        for d in dss:
            d.close()
    a = a[0]
    a[a == -32768] = np.nan
    return a, tr


def priority_flood(z: np.ndarray, epsilon: float = 0.0) -> np.ndarray:
    """Relleno de depresiones (Barnes et al. 2014). Con epsilon > 0 deja pendiente mínima en los planos."""
    h, w = z.shape
    f = z.copy()
    visto = np.zeros(z.shape, bool)
    pq: list = []
    for i in range(h):
        for j in (0, w - 1):
            if not visto[i, j]:
                heapq.heappush(pq, (f[i, j], i, j)); visto[i, j] = True
    for j in range(w):
        for i in (0, h - 1):
            if not visto[i, j]:
                heapq.heappush(pq, (f[i, j], i, j)); visto[i, j] = True
    vec = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    while pq:
        e, i, j = heapq.heappop(pq)
        for di, dj in vec:
            a, b = i + di, j + dj
            if 0 <= a < h and 0 <= b < w and not visto[a, b]:
                visto[a, b] = True
                if f[a, b] <= e + epsilon:
                    f[a, b] = e + epsilon
                heapq.heappush(pq, (f[a, b], a, b))
    return f


def acumulacion_d8(f: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Área aportante (celdas, incluida la propia) con D8 sobre el DEM rellenado con epsilon."""
    h, w = f.shape
    acc = np.ones(f.shape)
    orden = np.argsort(-f, axis=None, kind="stable")
    diag = math.hypot(dx, dy)
    vec = [(-1, -1, diag), (-1, 0, dy), (-1, 1, diag), (0, -1, dx), (0, 1, dx), (1, -1, diag), (1, 0, dy), (1, 1, diag)]
    for k in orden:
        i, j = divmod(int(k), w)
        mejor, destino = 0.0, None
        for di, dj, d in vec:
            a, b = i + di, j + dj
            if 0 <= a < h and 0 <= b < w:
                s = (f[i, j] - f[a, b]) / d
                if s > mejor:
                    mejor, destino = s, (a, b)
        if destino is not None:
            acc[destino] += acc[i, j]
    return acc


def derivadas(z: np.ndarray, tr, dx: float | None = None, dy: float | None = None) -> dict[str, np.ndarray]:
    """Derivadas en la grilla del DEM. Sin dx/dy, la grilla es geográfica (NASADEM); con dx/dy, proyectada (3DEP)."""
    if dx is None:
        lat_c = tr.f + tr.e * z.shape[0] / 2
        dy = abs(tr.e) * M_POR_GRADO
        dx = abs(tr.a) * M_POR_GRADO * math.cos(math.radians(lat_c))
    zz = np.where(np.isfinite(z), z, np.nanmean(z))
    # NASADEM viene en metros enteros: en el llano deja escalones y planos exactos. Las derivadas se calculan
    # sobre el DEM suavizado con un filtro gaussiano de sigma = 1 celda (~30 m); la elevación queda sin suavizar.
    zz = ndimage.gaussian_filter(zz, sigma=SIGMA_CELDAS, mode="nearest")
    dz_dfila, dz_dcol = np.gradient(zz, dy, dx)
    p = dz_dcol            # dz/d(este)
    q = -dz_dfila          # dz/d(norte); las filas crecen hacia el sur
    pend = np.hypot(p, q)
    out = {"elevacion_m": z, "pendiente_pct": 100 * pend}
    # aspecto: dirección de máxima bajada, grados desde el norte en sentido horario; vacío con pendiente 0
    asp = (np.degrees(np.arctan2(-p, -q)) + 360) % 360
    out["aspecto_sin"] = np.where(pend > 0, np.sin(np.radians(asp)), np.nan)
    out["aspecto_cos"] = np.where(pend > 0, np.cos(np.radians(asp)), np.nan)
    # curvaturas (Zevenbergen y Thorne 1987, en 1/m): perfil en la dirección de la pendiente, plan perpendicular
    r = np.gradient(p, dx, axis=1)
    t = -np.gradient(q, dy, axis=0)
    s = np.gradient(p, dy, axis=0) * -1
    g2 = p * p + q * q
    with np.errstate(divide="ignore", invalid="ignore"):
        out["curv_perfil"] = np.where(g2 > 0, -(p * p * r + 2 * p * q * s + q * q * t) / (g2 * (1 + g2) ** 1.5), np.nan)
        out["curv_plan"] = np.where(g2 > 0, -(q * q * r - 2 * p * q * s + p * p * t) / (g2 ** 1.5), np.nan)
    # TPI: elevación menos la media de las celdas a <= radio (sin la celda central)
    for radio, nombre in ((90.0, "tpi_90m_m"), (300.0, "tpi_300m_m")):
        ri, rj = int(radio // dy), int(radio // dx)
        ii, jj = np.mgrid[-ri:ri + 1, -rj:rj + 1]
        k = ((ii * dy) ** 2 + (jj * dx) ** 2 <= radio ** 2).astype(float)
        k[ri, rj] = 0
        media = ndimage.convolve(zz, k / k.sum(), mode="nearest")
        out[nombre] = zz - media
    # depresiones y TWI
    lleno = priority_flood(zz)
    out["prof_depresion_m"] = lleno - zz
    f_eps = priority_flood(zz, epsilon=1e-5)
    acc = acumulacion_d8(f_eps, dx, dy)
    sca = acc * dx * dy / dx
    tanb = np.maximum(pend, 1e-3)
    out["twi"] = np.log(sca / tanb)
    return out


def bilineal(a: np.ndarray, tr, lon: np.ndarray, lat: np.ndarray) -> np.ndarray:
    col, fila = ~tr * (lon, lat)
    fila, col = np.asarray(fila) - 0.5, np.asarray(col) - 0.5
    r0 = np.clip(np.floor(fila).astype(int), 0, a.shape[0] - 2)
    c0 = np.clip(np.floor(col).astype(int), 0, a.shape[1] - 2)
    fy, fx = fila - r0, col - c0
    return (a[r0, c0] * (1 - fy) * (1 - fx) + a[r0, c0 + 1] * (1 - fy) * fx
            + a[r0 + 1, c0] * fy * (1 - fx) + a[r0 + 1, c0 + 1] * fy * fx)


def terreno_lote(rutas, lon: np.ndarray, lat: np.ndarray) -> dict[str, np.ndarray]:
    z, tr = ventana_dem(rutas, lon.min(), lat.min(), lon.max(), lat.max())
    d = derivadas(z, tr)
    out = {k: bilineal(v, tr, lon, lat) for k, v in d.items() if k not in ("aspecto_sin", "aspecto_cos")}
    s, c = bilineal(d["aspecto_sin"], tr, lon, lat), bilineal(d["aspecto_cos"], tr, lon, lat)
    out["aspecto_grados"] = (np.degrees(np.arctan2(s, c)) + 360) % 360
    out["prof_depresion_m"] = np.maximum(out["prof_depresion_m"], 0)
    return out


COLS_3DEP = {"elevacion_m": "elevacion_3dep_m", "pendiente_pct": "pendiente_3dep_pct", "tpi_90m_m": "tpi_90m_3dep_m",
             "twi": "twi_3dep", "prof_depresion_m": "prof_depresion_3dep_m"}


def terreno_3dep_lote(ruta, x: np.ndarray, y: np.ndarray) -> dict[str, np.ndarray]:
    """USGS 3DEP a 10 m (EPSG:5070, bordes alineados con la grilla de 30 m): derivadas en la grilla de 10 m
    (mismo método que NASADEM, gauss sigma 1 celda = 10 m) y media de las 3 × 3 celdas de cada píxel de 30 m."""
    with rasterio.open(ruta) as d:
        z = d.read(1).astype("float64")
        tr = d.transform
        if d.nodata is not None:
            z[z == d.nodata] = np.nan
    z[(z < -1000) | (z > 10000)] = np.nan
    dv = derivadas(z, tr, dx=abs(tr.a), dy=abs(tr.e))
    c0 = np.rint((x - 15 - tr.c) / tr.a).astype(int)
    f0 = np.rint((y + 15 - tr.f) / tr.e).astype(int)
    out = {}
    for k, nombre in COLS_3DEP.items():
        a = dv[k]
        v = np.zeros(len(x))
        for di in range(3):
            for dj in range(3):
                v += a[f0 + di, c0 + dj]
        out[nombre] = v / 9
    out["prof_depresion_3dep_m"] = np.maximum(out["prof_depresion_3dep_m"], 0)
    return out
