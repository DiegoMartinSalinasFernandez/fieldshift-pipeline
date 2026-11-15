"""Celdas de 0,1° de GPM IMERG por condado (las usan download.py y process.py).

Una celda pertenece a un condado si su centro (lat/lon terminados en .x5) cae dentro del polígono
de data/reference/condados.gpkg. Si un condado no tiene ninguno (condados chicos o angostos), se usa
la celda que contiene su centroide. En IA, IL e IN todos tenían al menos 3 centros; para otros
estados, `resumen_celdas()` dice cuántos usan la celda del centroide.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
GPKG = REPO / "data" / "reference" / "condados.gpkg"
RES = 0.1


def _centro(v: float) -> float:
    return round(np.floor(v / RES) * RES + RES / 2, 2)


def celdas_imerg() -> pd.DataFrame:
    """fips, lat, lon (centro de la celda), ordenado."""
    return _celdas()[0]


def resumen_celdas() -> dict:
    """Para el data card: celdas distintas, mínimo y máximo de celdas por condado y condados que usan
    la celda de su centroide porque ningún centro cae adentro."""
    out, sin_centro = _celdas()
    n = out.groupby("fips").size()
    return {"n_celdas": len(out[["lat", "lon"]].drop_duplicates()), "min": int(n.min()),
            "max": int(n.max()), "sin_centro": sorted(sin_centro)}


def _celdas() -> tuple[pd.DataFrame, list[str]]:
    g = gpd.read_file(GPKG)[["fips", "lat_centroide", "lon_centroide", "geometry"]]
    g["fips"] = g["fips"].astype(str).str.zfill(5)
    x0, y0, x1, y1 = g.total_bounds
    xs = np.round(np.arange(_centro(x0), x1 + RES, RES), 2)
    ys = np.round(np.arange(_centro(y0), y1 + RES, RES), 2)
    X, Y = np.meshgrid(xs, ys)
    pts = gpd.GeoDataFrame({"lon": X.ravel(), "lat": Y.ravel()},
                           geometry=gpd.points_from_xy(X.ravel(), Y.ravel()), crs=g.crs)
    j = gpd.sjoin(pts, g[["fips", "geometry"]], predicate="within")[["fips", "lat", "lon"]]
    faltan = g.loc[~g["fips"].isin(j["fips"])]
    extra = pd.DataFrame({"fips": faltan["fips"],
                          "lat": [_centro(v) for v in faltan["lat_centroide"]],
                          "lon": [_centro(v) for v in faltan["lon_centroide"]]})
    out = pd.concat([j, extra], ignore_index=True)
    out["lat"] = out["lat"].round(2)
    out["lon"] = out["lon"].round(2)
    out = out.drop_duplicates().sort_values(["fips", "lat", "lon"]).reset_index(drop=True)
    return out, list(faltan["fips"])


def nombre_celda(lat: float, lon: float) -> str:
    return f"imerg_{lat:.2f}_{lon:.2f}.csv"


def celda_de_nombre(nombre: str) -> tuple[float, float]:
    _, la, lo = Path(nombre).stem.split("_")
    return float(la), float(lo)
