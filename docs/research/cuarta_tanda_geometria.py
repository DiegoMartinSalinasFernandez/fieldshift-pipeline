"""T070: geometría de MI, ND y KY (y de los estados ya bajados, como referencia para escalar).

No toca data/ ni config/. Lee los condados del Census (cb_2023_us_county_500k, el mismo archivo que
src/base/download.py) desde una carpeta fuera del repo y calcula por estado:
- condados y superficie de tierra (ALAND),
- bbox con el mismo margen que src/vegetacion/download.py (0,05°) y su área aproximada en km²,
- teselas MODIS (grilla sinusoidal) que tocan algún condado,
- teselas NASADEM de 1° (misma regla que src/suelo_terreno/download.py) y celdas IMERG de 0,1°,
- teselas CDL de Planetary Computer (colección usda-cdl, un año) que tocan algún condado, y el tamaño
  real de cada tesela y de cada NASADEM con HEAD (Content-Length): no baja los archivos.

Uso: .venv/bin/python -X utf8 docs/research/cuarta_tanda_geometria.py <carpeta_con_el_shp> [anio_cdl]
"""
import math
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import requests
from shapely.geometry import box, shape

MARGEN = 0.05
SIN = "+proj=sinu +R=6371007.181 +nadgrids=@null +wktext"
TESELA = 1111950.5197665233
GRUPOS = {"MI": ["26"], "ND": ["38"], "KY": ["21"], "KS": ["20"], "OH": ["39"], "NE": ["31"],
          "MN": ["27"], "IA+IL+IN": ["19", "17", "18"]}
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"


def token(url):
    return requests.get(url, timeout=60).json()["token"]


def head(url):
    r = requests.head(url, timeout=60)
    return int(r.headers.get("Content-Length", 0)) if r.ok else None


def main():
    carpeta = Path(sys.argv[1])
    anio = int(sys.argv[2]) if len(sys.argv) > 2 else 2020
    c = gpd.read_file(next(carpeta.glob("cb_2023_us_county_500k.shp"))).to_crs(4326)
    tok_cdl = token("https://planetarycomputer.microsoft.com/api/sas/v1/token/landcoverdata/usda-cdl")
    tok_dem = token("https://planetarycomputer.microsoft.com/api/sas/v1/token/nasadem")
    print("grupo,condados,tierra_km2,bbox_km2,modis,nasadem_n,nasadem_mb,imerg_celdas,"
          f"cdl_teselas_{anio},cdl_mb_{anio}")
    for nombre, fips in GRUPOS.items():
        sub = c[c["STATEFP"].isin(fips)]
        union = sub.union_all()
        # bbox por estado con margen (los de IA+IL+IN se juntan en uno, como grupos_bbox)
        bb = [sub.total_bounds[0] - MARGEN, sub.total_bounds[1] - MARGEN,
              sub.total_bounds[2] + MARGEN, sub.total_bounds[3] + MARGEN]
        bbox_km2 = gpd.GeoSeries([box(*bb)], crs=4326).to_crs(5070).area.iloc[0] / 1e6
        # MODIS: puntos cada 0,02° dentro de los condados → tesela sinusoidal
        xs = np.arange(bb[0], bb[2], 0.02)
        ys = np.arange(bb[1], bb[3], 0.02)
        pts = gpd.GeoSeries(gpd.points_from_xy(*[a.ravel() for a in np.meshgrid(xs, ys)]), crs=4326)
        pts = pts[pts.within(union)]
        ps = pts.to_crs(SIN)
        h = np.floor((ps.x + 18 * TESELA) / TESELA).astype(int)
        v = np.floor((9 * TESELA - ps.y) / TESELA).astype(int)
        modis = sorted({f"h{a:02d}v{b:02d}" for a, b in zip(h, v)})
        # NASADEM
        dem = []
        for lat in range(math.floor(bb[1]), math.ceil(bb[3])):
            for lon in range(math.floor(bb[0]), math.ceil(bb[2])):
                if union.intersects(box(lon, lat, lon + 1, lat + 1)):
                    dem.append(f"n{lat:02d}w{-lon:03d}")
        dem_mb = 0
        for t in dem:
            s = head("https://nasademeuwest.blob.core.windows.net/nasadem-cog/v001/"
                     f"NASADEM_HGT_{t}.tif?{tok_dem}")
            dem_mb += (s or 0) / 1e6
        # IMERG 0,1°: centros de celda dentro del bbox que caen en algún condado (aprox.)
        cx = np.arange(math.floor(bb[0] * 10) / 10 + 0.05, bb[2], 0.1)
        cy = np.arange(math.floor(bb[1] * 10) / 10 + 0.05, bb[3], 0.1)
        cel = gpd.GeoSeries([box(x - 0.05, y - 0.05, x + 0.05, y + 0.05) for x in cx for y in cy], crs=4326)
        n_imerg = int(cel.intersects(union).sum())
        # CDL: búsqueda STAC por bbox, se queda la tesela si toca algún condado
        # (misma consulta que src/cultivos/download.py: teselas_cdl, siguiendo `next`)
        items, url, cuerpo = [], STAC, {"collections": ["usda-cdl"], "bbox": [float(x) for x in sub.total_bounds],
                                        "datetime": f"{anio}-01-01T00:00:00Z/{anio}-12-31T23:59:59Z",
                                        "limit": 500}
        while url:
            j = requests.post(url, json=cuerpo, timeout=120).json()
            items += j["features"]
            nxt = [lk for lk in j.get("links", []) if lk.get("rel") == "next"]
            url, cuerpo = (nxt[0]["href"], nxt[0].get("body", cuerpo)) if nxt else (None, cuerpo)
        teselas, mb = 0, 0.0
        for it in {i["id"]: i for i in items}.values():
            if "cropland" not in it["assets"] or not shape(it["geometry"]).intersects(union):
                continue
            teselas += 1
            s = head(it["assets"]["cropland"]["href"] + "?" + tok_cdl)
            mb += (s or 0) / 1e6
        print(f"{nombre},{len(sub)},{sub['ALAND'].sum() / 1e6:.0f},{bbox_km2:.0f},{' '.join(modis)},"
              f"{len(dem)},{dem_mb:.0f},{n_imerg},{teselas},{mb:.0f}", flush=True)


if __name__ == "__main__":
    main()
