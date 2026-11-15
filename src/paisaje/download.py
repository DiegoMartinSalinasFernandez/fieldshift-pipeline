"""Baja Annual NLCD (USGS, Collection 1 v1) por ventana sobre cada estado.

Fuente: mirror público sin login de los COG de USGS (s3://usgs-landcover, requester-pays) en
Source Cooperative (kylebarron/usgs-landcover). Lee solo la ventana del bbox de cada estado de
config.yaml (EPSG:5070 de condados.gpkg) y la guarda como GeoTIFF comprimido en
data/raw/paisaje/. Reanudable: saltea lo que ya está en raw; escribe en interim y mueve al final.

Uso: python src/paisaje/download.py [--productos LndCov,FctImp] [--anios 2000-2024] [--hilos 8]
"""
import argparse
import datetime as dt
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "5")
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "2")

import geopandas as gpd
import numpy as np
import rasterio
import yaml
from rasterio.windows import Window, from_bounds

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/paisaje"
INTERIM = ROOT / "data/interim/paisaje"
LOG = INTERIM / "download.log"
BASE_URL = "https://data.source.coop/kylebarron/usgs-landcover/annual-nlcd/c1/v1/cu/mosaic"
VERSION = "C1V1"
PRODUCTOS = {"LndCov": "Annual NLCD Land Cover", "FctImp": "Annual NLCD Fractional Impervious Surface"}
ULTIMO_ANIO = 2024  # último año publicado en Annual NLCD C1V1 (listado del bucket, 2026-11-14)


def log(msg):
    INTERIM.mkdir(parents=True, exist_ok=True)
    line = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def url_de(producto, anio):
    return f"{BASE_URL}/Annual_NLCD_{producto}_{anio}_CU_{VERSION}.tif"

def _cargar_config():
    """config.yaml filtrado por FIELDSHIFT_ESTADOS (src/common/config.py)."""
    sys.path.insert(0, str(ROOT))
    from src.common.config import cargar_config
    return cargar_config()


def nombre_raw(producto, anio, estado):
    return f"Annual_NLCD_{producto}_{anio}_{estado}_{VERSION}.tif"


def ventanas_estado(src):
    cfg = _cargar_config()
    g = gpd.read_file(ROOT / "data/reference/condados.gpkg").to_crs(src.crs)
    col = "estado" if "estado" in g.columns else None
    if col is None:
        g["estado"] = g["fips"].str[:2]
    out = {}
    for est, sub in g.groupby("estado"):
        b = sub.total_bounds
        w = from_bounds(*b, transform=src.transform)
        c0 = int(np.floor(w.col_off)) - 2
        r0 = int(np.floor(w.row_off)) - 2
        c1 = int(np.ceil(w.col_off + w.width)) + 2
        r1 = int(np.ceil(w.row_off + w.height)) + 2
        out[est] = Window(c0, r0, c1 - c0, r1 - r0)
    return out


def leer_ventana(url, win, hilos, alto=1024):
    arr = np.empty((int(win.height), int(win.width)), dtype="uint8")
    partes = [(r, min(alto, int(win.height) - r)) for r in range(0, int(win.height), alto)]

    def leer(parte):
        r, h = parte
        with rasterio.open("/vsicurl/" + url) as s:
            arr[r:r + h, :] = s.read(1, window=Window(win.col_off, win.row_off + r, win.width, h))

    with ThreadPoolExecutor(hilos) as ex:
        list(ex.map(leer, partes))
    return arr


def asegurar_manifest(man: Path) -> None:
    """En una máquina nueva no hay manifest.csv (no va en git): lo crea con el encabezado (CLAUDE.md §7)."""
    if not man.exists() or man.stat().st_size == 0:
        man.write_text("paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n", encoding="utf-8")


def upsert_manifest(filas):
    man = ROOT / "manifest.csv"
    asegurar_manifest(man)
    data = man.read_bytes()
    eol = b"\r\n" if b"\r\n" in data else b"\n"
    existentes = set()
    for line in data.decode("utf-8").splitlines()[1:]:
        partes = line.split(",")
        if len(partes) > 1:
            existentes.add(partes[1])
    nuevas = [f for f in filas if f[1] not in existentes]
    if not nuevas:
        return 0
    txt = b""
    if not data.endswith(eol):
        txt += eol
    for f in nuevas:
        txt += (",".join(f)).encode("utf-8") + eol
    with open(man, "ab") as fh:
        fh.write(txt)
    return len(nuevas)


def filas_manifest():
    filas = []
    for p in sorted(RAW.glob("Annual_NLCD_*.tif")):
        _, _, prod, anio, est, _ = p.stem.split("_")
        meta = INTERIM / (p.name + ".fecha")
        fecha = meta.read_text().strip() if meta.exists() else dt.date.today().isoformat()
        filas.append([
            "paisaje", p.relative_to(ROOT).as_posix(), "USGS EROS / MRLC (mirror Source Cooperative)",
            PRODUCTOS[prod], VERSION, fecha,
            url_de(prod, anio) + f" (ventana bbox estado {est}; EPSG:5070 AEA)",
        ])
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--productos", default="LndCov,FctImp")
    ap.add_argument("--anios", default=f"2000-{ULTIMO_ANIO}")
    ap.add_argument("--hilos", type=int, default=8)
    a = ap.parse_args()
    a0, a1 = (int(x) for x in a.anios.split("-"))
    RAW.mkdir(parents=True, exist_ok=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    for prod in a.productos.split(","):
        for anio in range(a0, a1 + 1):
            url = url_de(prod, anio)
            pendientes = None
            with rasterio.open("/vsicurl/" + url) as src:
                wins = ventanas_estado(src)
                prof = src.profile
                transform = src.transform
                pendientes = {e: w for e, w in wins.items() if not (RAW / nombre_raw(prod, anio, e)).exists()}
            for est, win in pendientes.items():
                t0 = time.time()
                arr = leer_ventana(url, win, a.hilos)
                part = INTERIM / (nombre_raw(prod, anio, est) + ".part")
                p = dict(driver="GTiff", dtype="uint8", count=1, width=int(win.width), height=int(win.height),
                         crs=prof["crs"], transform=rasterio.windows.transform(win, transform),
                         nodata=prof.get("nodata"), compress="deflate", predictor=2, tiled=True,
                         blockxsize=512, blockysize=512, zlevel=6, num_threads="ALL_CPUS")
                with rasterio.open(part, "w", **p) as dst:
                    dst.write(arr, 1)
                destino = RAW / nombre_raw(prod, anio, est)
                shutil.move(str(part), str(destino))
                (INTERIM / (destino.name + ".fecha")).write_text(dt.date.today().isoformat())
                log(f"ok {destino.name} {win.width}x{win.height} {destino.stat().st_size/1e6:.1f} MB {time.time()-t0:.0f}s")
                upsert_manifest(filas_manifest())
    n = upsert_manifest(filas_manifest())
    log(f"manifest: {n} filas nuevas")


if __name__ == "__main__":
    sys.exit(main())
