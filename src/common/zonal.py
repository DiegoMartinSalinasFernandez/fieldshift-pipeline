"""Estadísticas zonales por condado (media, opcionalmente solo píxeles de una máscara)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def zonal_mean(raster, condados=None, nodata=None, mascara=None, columna_id: str = "fips",
               all_touched: bool = False) -> pd.DataFrame:
    """Media de un raster por condado.

    raster: ruta a un GeoTIFF (una banda).
    condados: GeoDataFrame o ruta a un vector; por defecto data/reference/condados.gpkg.
    nodata: valor de relleno a ignorar (si no, el del raster).
    mascara: ruta opcional a un raster 0/1 alineado con `raster` (ej. mascara_agricola.tif);
             solo se promedian los píxeles con máscara = 1.
    Devuelve DataFrame con `fips`, `media` y `frac_pixeles_validos` (píxeles válidos sobre los
    píxeles del condado). La media es NaN si no hay píxeles válidos.
    """
    import geopandas as gpd
    import rasterio
    from rasterio.mask import mask as rio_mask

    from src.common.config import REPO

    if condados is None:
        condados = REPO / "data" / "reference" / "condados.gpkg"
    gdf = condados if isinstance(condados, gpd.GeoDataFrame) else gpd.read_file(condados)
    filas = []
    with rasterio.open(raster) as src:
        nd = src.nodata if nodata is None else nodata
        gdf = gdf.to_crs(src.crs)
        msrc = rasterio.open(mascara) if mascara is not None else None
        try:
            for _, r in gdf.iterrows():
                geom = [r.geometry.__geo_interface__]
                try:
                    datos, _ = rio_mask(src, geom, crop=True, filled=False, all_touched=all_touched)
                except ValueError:  # el polígono no cae en el raster
                    filas.append({columna_id: r[columna_id], "media": np.nan, "frac_pixeles_validos": 0.0})
                    continue
                arr = datos[0].astype("float64")
                dentro = ~np.ma.getmaskarray(datos[0])
                validos = dentro & np.isfinite(arr.filled(np.nan))
                if nd is not None:
                    validos &= arr.filled(np.nan) != nd
                if msrc is not None:
                    m, _ = rio_mask(msrc, geom, crop=True, filled=True, nodata=0, all_touched=all_touched)
                    validos &= m[0] == 1
                n = int(dentro.sum())
                v = arr.filled(np.nan)[validos]
                filas.append({columna_id: r[columna_id],
                              "media": float(v.mean()) if v.size else np.nan,
                              "frac_pixeles_validos": (v.size / n) if n else 0.0})
        finally:
            if msrc is not None:
                msrc.close()
    return pd.DataFrame(filas)
