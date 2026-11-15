"""Descarga de recortes por lote de Landsat C2 L2 y HLS v2 S30 (Microsoft Planetary Computer, sin login).

Por cada escena STAC (1 de marzo a 30 de noviembre, 2000-2025) que cubre el centroide de un lote se lee la
ventana de origen de cada banda (con 2 px de margen), se reproyecta en memoria por vecino más cercano a la
grilla de 30 m de data/reference/mascara_agricola.tif (EPSG:5070) en el recuadro del lote (+1 píxel) y se
guarda tal cual (DN uint16) en un .npz por escena: data/raw/lotes/<producto>/<anio>/<id>.npz, con una
clave por lote (bandas apiladas en el orden de BANDAS) y "<id_lote>__x0y0" (esquina superior izquierda).

Uso: python src/lotes/download.py landsat [hls]
Reanudable: saltea las escenas que ya están en raw; escribe .part en interim y renombra al final.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import rasterio.errors
import requests
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject, transform_bounds
from rasterio.windows import Window, from_bounds
from shapely.geometry import Point, shape

RAIZ = Path(__file__).resolve().parents[2]
INTERIM = RAIZ / "data" / "interim" / "lotes"
RAW = RAIZ / "data" / "raw" / "lotes"
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
PASO = 30.0
CRS_GRILLA = CRS.from_epsg(5070)
NUBES_MAX = 80
PRODUCTOS = {
    "landsat": {"coleccion": "landsat-c2-l2", "anios": range(2000, 2026),
                "bandas": ["blue", "green", "red", "nir08", "swir16", "swir22", "qa_pixel"]},
    "hls_s30": {"coleccion": "hls2-s30", "anios": range(2015, 2026),
                "bandas": ["B02", "B03", "B04", "B8A", "B11", "B12", "Fmask"]},
}

os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "4")
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "2")
os.environ.setdefault("GDAL_HTTP_MERGE_CONSECUTIVE_RANGES", "YES")
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".TIF,.tif")
# HLS S30 v2.0 de 2015-2019 no está en Planetary Computer: se lee de LP DAAC (Earthdata; GDAL toma el login de
# las credenciales del usuario y guarda la cookie de sesión en interim)
CMR_STAC = "https://cmr.earthdata.nasa.gov/stac/LPCLOUD/search"
HLS_LPDAAC_HASTA = 2019
os.environ.setdefault("GDAL_HTTP_COOKIEFILE", str(INTERIM / "edl_cookies.txt"))
os.environ.setdefault("GDAL_HTTP_COOKIEJAR", str(INTERIM / "edl_cookies.txt"))


def _lpdaac(prod: str, anio: int) -> bool:
    return prod == "hls_s30" and anio <= HLS_LPDAAC_HASTA


def _cache(prod: str, anio: int) -> Path:
    return INTERIM / "stac" / (f"hls_s30_lpdaac_{anio}.json" if _lpdaac(prod, anio) else f"{prod}_{anio}.json")

_tok: dict[str, tuple[float, str]] = {}
_lock = threading.Lock()


def log(msg: str) -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    linea = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(linea, flush=True)
    with open(INTERIM / "landsat.log", "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def token(coleccion: str) -> str:
    with _lock:
        t, tok = _tok.get(coleccion, (0.0, ""))
        if time.time() - t > 600:
            r = requests.get(f"https://planetarycomputer.microsoft.com/api/sas/v1/token/{coleccion}", timeout=60)
            r.raise_for_status()
            tok = r.json()["token"]
            _tok[coleccion] = (time.time(), tok)
        return tok


def recuadros() -> pd.DataFrame:
    """Recuadro de cada lote en la grilla de 30 m (centros múltiplos de 30 m) con 1 píxel de margen."""
    px = pd.read_csv(RAIZ / "data/processed/lotes/pixeles.csv", dtype={"fips": str})
    g = px.groupby("id_lote").agg(fips=("fips", "first"), xmin=("x_m", "min"), xmax=("x_m", "max"),
                                  ymin=("y_m", "min"), ymax=("y_m", "max"), lon=("lon", "mean"), lat=("lat", "mean"))
    g["x0"] = g["xmin"] - PASO - PASO / 2
    g["y0"] = g["ymax"] + PASO + PASO / 2
    g["ancho"] = ((g["xmax"] - g["xmin"]) / PASO).round().astype(int) + 3
    g["alto"] = ((g["ymax"] - g["ymin"]) / PASO).round().astype(int) + 3
    return g.reset_index()


def buscar(prod: str, anio: int, bbox: list[float]) -> list[dict]:
    cache = _cache(prod, anio)
    if cache.exists():
        return json.load(open(cache, encoding="utf-8"))
    cfg = PRODUCTOS[prod]
    body = {"collections": [cfg["coleccion"]], "bbox": bbox,
            "datetime": f"{anio}-03-01T00:00:00Z/{anio}-11-30T23:59:59Z",
            "query": {"eo:cloud_cover": {"lt": NUBES_MAX}}, "limit": 500}
    feats, url, metodo = [], STAC, "POST"
    if _lpdaac(prod, anio):
        # CMR-STAC no tiene la extensión query: el filtro de nubes se aplica abajo
        body = {"collections": ["HLSS30_2.0"], "bbox": bbox, "datetime": body["datetime"], "limit": 250}
        url = CMR_STAC
    while url:
        r = (requests.post(url, json=body, timeout=180) if metodo == "POST" else requests.get(url, timeout=180))
        r.raise_for_status()
        j = r.json()
        feats += j["features"]
        nxt = [l for l in j.get("links", []) if l.get("rel") == "next"]
        if nxt:
            url, metodo = nxt[0]["href"], nxt[0].get("method", "GET")
            body = nxt[0].get("body", body)
        else:
            url = None
    slim = [{"id": f["id"], "fecha": f["properties"]["datetime"][:10], "nubes": f["properties"]["eo:cloud_cover"],
             "plataforma": f["properties"].get("platform", ""), "geometry": f["geometry"],
             "hrefs": {b: f["assets"][b]["href"] for b in cfg["bandas"]}} for f in feats
            if all(b in f["assets"] for b in cfg["bandas"]) and f["properties"].get("eo:cloud_cover", 100) < NUBES_MAX]
    slim.sort(key=lambda e: e["id"])
    cache.parent.mkdir(parents=True, exist_ok=True)
    json.dump(slim, open(cache, "w", encoding="utf-8"))
    return slim


def bajar_escena(prod: str, anio: int, esc: dict, lotes: pd.DataFrame) -> str:
    destino = RAW / prod / str(anio) / f"{esc['id']}.npz"
    if destino.exists():
        return "ya"
    cfg = PRODUCTOS[prod]
    lp = _lpdaac(prod, anio)
    tok = "" if lp else token(cfg["coleccion"])
    plataforma: list[str] = []
    salida: dict[str, np.ndarray] = {}
    arr = {r.id_lote: np.zeros((len(cfg["bandas"]), r.alto, r.ancho), np.uint16) for r in lotes.itertuples()}
    def leer(ib: int, b: str) -> None:
        with rasterio.open(esc["hrefs"][b] + ("" if lp else "?" + tok)) as src:
            escena = Window(0, 0, src.width, src.height)
            if lp and b == "Fmask":
                plataforma.append(src.tags().get("SPACECRAFT_NAME", ""))
            for r in lotes.itertuples():
                dst_tr = from_origin(r.x0, r.y0, PASO, PASO)
                bounds = (r.x0, r.y0 - r.alto * PASO, r.x0 + r.ancho * PASO, r.y0)
                sb = transform_bounds(CRS_GRILLA, src.crs, *bounds)
                sw = from_bounds(*sb, transform=src.transform).round_offsets().round_lengths()
                sw = Window(sw.col_off - 2, sw.row_off - 2, sw.width + 4, sw.height + 4)
                try:
                    sw = sw.intersection(escena)
                except rasterio.errors.WindowError:
                    continue
                reproject(src.read(1, window=sw), arr[r.id_lote][ib], src_transform=src.window_transform(sw),
                          src_crs=src.crs, dst_transform=dst_tr, dst_crs=CRS_GRILLA,
                          resampling=Resampling.nearest, src_nodata=0, dst_nodata=0)

    with ThreadPoolExecutor(max_workers=len(cfg["bandas"])) as ex:
        list(ex.map(lambda t: leer(*t), enumerate(cfg["bandas"])))
    for r in lotes.itertuples():
        salida[r.id_lote] = arr[r.id_lote]
        salida[f"{r.id_lote}__x0y0"] = np.array([r.x0, r.y0])
    if lp:
        salida["__plataforma"] = np.array(plataforma[0] if plataforma else "")
    tmp = INTERIM / "parciales" / f"{prod}_{esc['id']}.part.npz"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(tmp, **salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    os.replace(tmp, destino)
    return "ok"


def tareas(prod: str, rec: pd.DataFrame) -> list[tuple]:
    """(rango, anio, escena, lotes que cubre). El rango ordena la bajada: primero la escena más despejada de cada
    lote-año (en todos los años), después la segunda, etc., para que lo parcial ya cubra todos los años."""
    bbox = [rec.lon.min() - 0.05, rec.lat.min() - 0.05, rec.lon.max() + 0.05, rec.lat.max() + 0.05]
    pts = [(r.id_lote, Point(r.lon, r.lat)) for r in rec.itertuples()]
    out = []
    for anio in PRODUCTOS[prod]["anios"]:
        escenas = buscar(prod, anio, bbox)
        cubre: dict[str, list[str]] = {}
        for e in escenas:
            g = shape(e["geometry"])
            cubre[e["id"]] = [i for i, p in pts if g.contains(p)]
        rango: dict[str, int] = {}
        for i, _ in pts:
            cand = sorted((e for e in escenas if i in cubre[e["id"]]), key=lambda e: (e["nubes"], e["id"]))
            for k, e in enumerate(cand):
                rango[e["id"]] = min(rango.get(e["id"], 10 ** 6), k)
        for e in escenas:
            if cubre[e["id"]]:
                out.append((rango[e["id"]], anio, e, cubre[e["id"]]))
        log(f"{prod} {anio}: {len(escenas)} escenas STAC, {sum(1 for e in escenas if cubre[e['id']])} cubren lotes")
    out.sort(key=lambda t: (t[0], t[1], t[2]["id"]))
    return out


def registrar(prod: str, upsert) -> None:
    cfg = PRODUCTOS[prod]
    filas = []
    for anio in cfg["anios"]:
        cache = _cache(prod, anio)
        if not cache.exists():
            continue
        por_id = {e["id"]: e for e in json.load(open(cache, encoding="utf-8"))}
        for p in sorted((RAW / prod / str(anio)).glob("*.npz")):
            e = por_id.get(p.stem)
            url = e["hrefs"][cfg["bandas"][0]].rsplit("/", 1)[0] + "/" if e else ""
            filas.append({"paquete": "lotes", "archivo": p.relative_to(RAIZ).as_posix(),
                          "fuente": "NASA LP DAAC (Earthdata)" if _lpdaac(prod, anio) else "USGS/NASA vía Microsoft Planetary Computer",
                          "producto": f"{cfg['coleccion']} {p.stem} (recortes por lote, bandas {','.join(cfg['bandas'])})",
                          "version": "Collection 2 Level-2" if prod == "landsat" else "HLS v2.0",
                          "fecha_descarga": dt.date.today().isoformat(), "consulta_o_url": url})
    upsert(filas)


def bajar(prod: str, upsert, workers: int = 24) -> None:
    rec = recuadros()
    lista = tareas(prod, rec)
    pend = [t for t in lista if not (RAW / prod / str(t[1]) / f"{t[2]['id']}.npz").exists()]
    # varios procesos en paralelo (LOTES_SHARD="i/n"): con un solo proceso y muchos hilos GDAL se traba (~0,1
    # escenas/s); cada proceso toma una de cada n escenas y el manifest se registra al final con "manifest"
    shard = os.environ.get("LOTES_SHARD")
    if shard:
        i, n = (int(v) for v in shard.split("/"))
        pend = pend[i::n]
        workers = int(os.environ.get("LOTES_WORKERS", "4"))
    log(f"{prod}: {len(lista)} escenas, {len(pend)} pendientes")
    t0, hechas = time.time(), 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(bajar_escena, prod, a, e, rec[rec.id_lote.isin(ls)]): e["id"] for _, a, e, ls in pend}
        for fu in as_completed(futs):
            hechas += 1
            try:
                fu.result()
            except Exception as ex_:  # se reintenta en la próxima corrida
                log(f"{prod} {futs[fu]} ERROR {type(ex_).__name__}: {str(ex_)[:150]}")
            if hechas % 100 == 0:
                log(f"{prod}: {hechas}/{len(pend)} en {time.time() - t0:.0f} s")
                if not shard:
                    registrar(prod, upsert)
    if not shard:
        registrar(prod, upsert)
    log(f"{prod}: listo en {time.time() - t0:.0f} s")
