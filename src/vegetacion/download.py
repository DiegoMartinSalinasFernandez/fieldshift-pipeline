"""Descarga de MODIS (MOD13Q1, MOD11A2) para la zona de estudio desde Microsoft Planetary Computer.

Acceso público sin login (no hay credencial de Earthdata): COGs de la colección 6.1 en
Planetary Computer, firmados con un token SAS anónimo. Para cada tesela/fecha se lee solo la
ventana que cubre los condados y se guarda tal cual como GeoTIFF en data/raw/vegetacion/.

- MOD13Q1: NDVI, EVI y pixel reliability, leídos del overview 1 del COG (factor 4, ~927 m)
  porque la tesela completa a 250 m baja a ~1 MB/s y no entra en el tiempo ni en 5 GB.
- MOD11A2: LST día y noche, overview 0 del COG (factor 2, ~2 km) para no pasar los 5 GB; el
  overview promedia los píxeles válidos (los sin dato, 0, quedan como nodata).

Reanudable: si el GeoTIFF ya existe en raw no se vuelve a bajar. Se escribe en interim (.part)
y se mueve a raw al terminar. Uso: python src/vegetacion/download.py [mod13q1|mod11a2] [anio_desde anio_hasta]
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import shutil
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
import requests
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import cargar_config  # noqa: E402

RAW = REPO / "data" / "raw" / "vegetacion"
INTERIM = REPO / "data" / "interim" / "vegetacion"
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token/modiseuwest/modis-061-cogs"

PRODUCTOS = {
    "mod13q1": {"coleccion": "modis-13Q1-061", "prefijo": "MOD13Q1",
                "bandas": ["250m_16_days_NDVI", "250m_16_days_EVI", "250m_16_days_pixel_reliability"],
                "overview": 1, "desde": 2000},
    "mod11a2": {"coleccion": "modis-11A2-061", "prefijo": "MOD11A2",
                "bandas": ["LST_Day_1km", "LST_Night_1km"],
                "overview": 0, "desde": 2000},
}

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "4")
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "2")

_lock = threading.Lock()


def log(msg: str) -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    with _lock, open(INTERIM / "download.log", "a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")


def bbox_zona() -> list[float]:
    g = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg")
    b = g.total_bounds
    return [float(b[0]) - 0.05, float(b[1]) - 0.05, float(b[2]) + 0.05, float(b[3]) + 0.05]


def buscar(coleccion: str, prefijo: str, bbox: list[float], anio: int) -> list[dict]:
    body = {"collections": [coleccion], "bbox": bbox,
            "datetime": f"{anio}-01-01T00:00:00Z/{anio}-12-31T23:59:59Z", "limit": 500}
    items, url = [], STAC
    while url:
        r = requests.post(url, json=body, timeout=120)
        r.raise_for_status()
        j = r.json()
        items += [f for f in j["features"] if f["id"].startswith(prefijo + ".")]
        nxt = [l for l in j.get("links", []) if l.get("rel") == "next"]
        if nxt:
            url, body = nxt[0]["href"], nxt[0].get("body", body)
        else:
            url = None
    return items


def bajar_item(item: dict, prod: dict, bbox: list[float], token: str) -> str:
    anio = item["id"].split(".")[1][1:5]
    destino = RAW / prod["prefijo"].lower() / anio / f"{item['id']}.tif"
    if destino.exists():
        return "ya"
    arrs, perfil = [], None
    for banda in prod["bandas"]:
        href = item["assets"][banda]["href"] + "?" + token
        kw = {"overview_level": prod["overview"]} if prod["overview"] is not None else {}
        with rasterio.open("/vsicurl/" + href, **kw) as src:
            xb = transform_bounds("EPSG:4326", src.crs, *bbox, densify_pts=50)
            l, b_, r, t = src.bounds
            xb = (max(xb[0], l), max(xb[1], b_), min(xb[2], r), min(xb[3], t))
            if xb[0] >= xb[2] or xb[1] >= xb[3]:
                return "fuera"
            win = from_bounds(*xb, transform=src.transform).round_offsets().round_lengths()
            a = src.read(1, window=win)
            if perfil is None:
                perfil = {"driver": "GTiff", "width": a.shape[1], "height": a.shape[0],
                          "crs": src.crs, "transform": src.window_transform(win),
                          "compress": "deflate", "predictor": 2, "tiled": False}
                dtype = a.dtype
            arrs.append((banda, a, src.nodata, src.tags()))
    dtype = np.result_type(*[a.dtype for _, a, _, _ in arrs])
    tmp = INTERIM / "_part" / (item["id"] + ".tif.part")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(tmp, "w", count=len(arrs), dtype=dtype, **perfil) as dst:
        for i, (banda, a, nd, tags) in enumerate(arrs, start=1):
            dst.write(a.astype(dtype), i)
            dst.set_band_description(i, banda)
            dst.update_tags(i, nodata=str(nd), scale_factor=tags.get("scale_factor", ""),
                            add_offset=tags.get("add_offset", ""))
        dst.update_tags(item_id=item["id"], start_datetime=item["properties"].get("start_datetime", ""),
                        overview_level=str(prod["overview"]))
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp), str(destino))
    return "ok"


def registrar_manifest(prod_key: str) -> None:
    prod = PRODUCTOS[prod_key]
    man = REPO / "manifest.csv"
    with open(man, encoding="utf-8") as f:
        ya = {r["archivo"] for r in csv.DictReader(f)}
    filas = []
    for p in sorted((RAW / prod["prefijo"].lower()).rglob("*.tif")):
        rel = p.relative_to(REPO).as_posix()
        if rel in ya:
            continue
        fecha = dt.date.fromtimestamp(p.stat().st_mtime).isoformat()
        ov = f"overview_level={prod['overview']}" if prod["overview"] is not None else "nativo"
        filas.append(["vegetacion", rel, "Microsoft Planetary Computer (NASA LP DAAC)", prod["prefijo"], "061",
                      fecha, f"{STAC} collection={prod['coleccion']} item={p.stem} bandas={'+'.join(prod['bandas'])} "
                             f"ventana=condados ({ov})"])
    if filas:
        with open(man, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(filas)


def main() -> None:
    prods = [sys.argv[1]] if len(sys.argv) > 1 else list(PRODUCTOS)
    cfg = cargar_config()
    a0 = int(sys.argv[2]) if len(sys.argv) > 2 else int(cfg["periodo"]["anio_inicio"])
    a1 = int(sys.argv[3]) if len(sys.argv) > 3 else int(cfg["periodo"]["anio_fin"])
    bbox = bbox_zona()
    token = requests.get(SAS, timeout=60).json()["token"]
    for pk in prods:
        prod = PRODUCTOS[pk]
        for anio in range(max(a0, prod["desde"]), a1 + 1):
            items = buscar(prod["coleccion"], prod["prefijo"], bbox, anio)
            pend = [it for it in items
                    if not (RAW / prod["prefijo"].lower() / str(anio) / f"{it['id']}.tif").exists()]
            log(f"{pk} {anio}: {len(items)} items, {len(pend)} pendientes")
            with ThreadPoolExecutor(12) as ex:
                futs = {ex.submit(bajar_item, it, prod, bbox, token): it["id"] for it in pend}
                for fu in as_completed(futs):
                    try:
                        fu.result()
                    except Exception as e:  # se reintenta en la próxima corrida
                        log(f"ERROR {futs[fu]}: {type(e).__name__}: {str(e)[:200]}")
            registrar_manifest(pk)
            log(f"{pk} {anio}: listo")


if __name__ == "__main__":
    main()
