"""Descarga de Landsat Collection 2 Level-2 (Planetary Computer, sin login) por ventanas.

Método: por condado se eligen N_VENT ventanas de LADO x LADO píxeles de 30 m en la grilla de
data/reference/mascara_agricola.tif (EPSG:5070), centradas en píxeles agrícolas al azar (semilla =
fips). Por cada escena seleccionada se leen solo esas ventanas (WarpedVRT a EPSG:5070, vecino más
cercano) de las bandas blue, red, nir08, swir16 y qa_pixel, y se guardan tal cual (DN uint16) en un
.npz por escena en data/raw/teledeteccion/landsat/<anio>/.

Uso: python src/teledeteccion/download.py [anio ...]   (por defecto, del más reciente hacia atrás)
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
import requests
import yaml
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
import rasterio.errors
from rasterio.warp import reproject, transform_bounds
from rasterio.windows import Window, from_bounds
from shapely.geometry import Point, shape

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.manifest import asegurar_manifest  # noqa: E402
RAW = REPO / "data/raw/teledeteccion/landsat"
INTERIM = REPO / "data/interim/teledeteccion"
MASCARA = REPO / "data/reference/mascara_agricola.tif"
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
TOKEN_URL = "https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2"
BANDAS = ["blue", "red", "nir08", "swir16", "qa_pixel"]
BANDAS_NDVI = ["red", "nir08", "qa_pixel"]
N_VENT = 2
LADO = 40
M_W = M_H = 0
INTERNOS = int(os.environ.get("TD_INTERNOS", "16"))
NUBES_MAX = 60
# períodos de selección de escenas: (nombre, mes-día inicio, mes-día fin, escenas por condado)
PERIODOS = [
    ("mar", "03-15", "03-31", 1),
    ("abr", "04-01", "04-30", 2),
    ("may", "05-01", "05-31", 2),
    ("jul_ago", "07-01", "08-31", 3),
    ("oct_nov", "10-01", "11-30", 3),
]

os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "4")
os.environ.setdefault("GDAL_HTTP_MERGE_CONSECUTIVE_RANGES", "YES")
os.environ.setdefault("GDAL_HTTP_VERSION", "2")
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "2")
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".TIF,.tif")


def log(msg: str) -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    linea = f"{dt.datetime.now():%H:%M:%S} {msg}"
    print(linea, flush=True)
    with open(INTERIM / "download.log", "a", encoding="utf-8") as f:
        f.write(linea + "\n")

def _cargar_config():
    """config.yaml filtrado por FIELDSHIFT_ESTADOS (src/common/config.py)."""
    sys.path.insert(0, str(REPO))
    from src.common.config import cargar_config
    return cargar_config()


def config() -> dict:
    return _cargar_config()


def ventanas() -> list[dict]:
    """Ventanas fijas por condado (deterministas). Se cachean en interim."""
    ruta = INTERIM / "ventanas.csv"
    if ruta.exists():
        return [dict(r, k=int(r["k"]), col=int(r["col"]), row=int(r["row"]),
                     lon=float(r["lon"]), lat=float(r["lat"])) for r in csv.DictReader(open(ruta))]
    cond = gpd.read_file(REPO / "data/reference/condados.gpkg")
    fcol = "fips" if "fips" in cond.columns else cond.columns[0]
    out = []
    with rasterio.open(MASCARA) as m:
        c5070 = cond.to_crs(m.crs)
        c4326 = cond.to_crs(4326)
        for i, row in c5070.sort_values(fcol).iterrows():
            fips = str(row[fcol]).zfill(5)
            win = rasterio.windows.from_bounds(*row.geometry.bounds, transform=m.transform)
            win = win.round_offsets().round_lengths()
            a = m.read(1, window=win)
            tr = m.window_transform(win)
            dentro = ~geometry_mask([row.geometry], out_shape=a.shape, transform=tr)
            rr, cc = np.nonzero((a == 1) & dentro)
            rng = np.random.default_rng(int(fips))
            if len(rr) == 0:
                continue
            for k, j in enumerate(rng.choice(len(rr), size=N_VENT, replace=False)):
                col = int(win.col_off + cc[j] - LADO // 2)
                rw = int(win.row_off + rr[j] - LADO // 2)
                x, y = m.xy(rw + LADO // 2, col + LADO // 2)
                p = gpd.GeoSeries([Point(x, y)], crs=m.crs).to_crs(4326).iloc[0]
                out.append({"fips": fips, "k": k, "col": col, "row": rw, "lon": p.x, "lat": p.y})
    with open(ruta, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["fips", "k", "col", "row", "lon", "lat"])
        w.writeheader()
        w.writerows(out)
    return out


def buscar(anio: int, bbox: list[float]) -> list[dict]:
    cache = INTERIM / f"stac_{anio}.json"
    if cache.exists():
        return json.load(open(cache))
    feats = []
    body = {"collections": ["landsat-c2-l2"], "bbox": bbox,
            "datetime": f"{anio}-03-15T00:00:00Z/{anio}-11-30T23:59:59Z",
            "query": {"eo:cloud_cover": {"lt": NUBES_MAX}}, "limit": 500}
    url, metodo = STAC, "POST"
    while url:
        r = requests.post(url, json=body, timeout=120) if metodo == "POST" else requests.get(url, timeout=120)
        r.raise_for_status()
        j = r.json()
        feats += j["features"]
        nxt = [l for l in j.get("links", []) if l.get("rel") == "next"]
        if nxt:
            url, metodo = nxt[0]["href"], nxt[0].get("method", "GET")
            body = nxt[0].get("body", body)
        else:
            url = None
    # Landsat 7 después de 2003 tiene bandeado (SLC-off): se usa solo si no hay otra
    slim = [{"id": f["id"], "fecha": f["properties"]["datetime"][:10], "nubes": f["properties"]["eo:cloud_cover"],
             "plataforma": f["properties"]["platform"], "geometry": f["geometry"],
             "hrefs": {b: f["assets"][b]["href"] for b in BANDAS}} for f in feats
            if all(b in f["assets"] for b in BANDAS)]
    json.dump(slim, open(cache, "w"))
    return slim


def seleccionar(anio: int, escenas: list[dict], vents: list[dict], rango_max: int = 99) -> dict[str, list[dict]]:
    """Por condado y período, las escenas más despejadas que cubren sus ventanas.

    rango_max limita cuántas escenas por condado y período se toman (las primeras del orden de
    preferencia): la selección con rango_max=1 es un subconjunto de la completa, así que se puede
    bajar primero la escena más despejada de cada período en todos los años y completar después."""
    geoms = [(e, shape(e["geometry"])) for e in escenas]
    por_cond: dict[str, list[dict]] = {}
    for v in vents:
        por_cond.setdefault(v["fips"], []).append(v)
    tareas: dict[str, list[dict]] = {}
    pref = {"landsat-9": 0, "landsat-8": 0, "landsat-5": 0, "landsat-4": 1, "landsat-7": 2}
    for fips, vs in por_cond.items():
        pts = [Point(v["lon"], v["lat"]) for v in vs]
        cubren = [e for e, g in geoms if all(g.contains(p) for p in pts)]
        for _, ini, fin, n in PERIODOS:
            cand = [e for e in cubren if f"{anio}-{ini}" <= e["fecha"] <= f"{anio}-{fin}"]
            cand.sort(key=lambda e: (pref.get(e["plataforma"], 1), e["nubes"], e["id"]))
            for e in cand[:min(n, rango_max)]:
                tareas.setdefault(e["id"], []).extend(vs)
    return tareas


def token() -> str:
    return requests.get(TOKEN_URL, timeout=60).json()["token"]


def bandas_escena(fecha: str) -> list[str]:
    """El BSI (blue y swir16) solo se usa en abril–mayo; las escenas de otras fechas bajan
    red, nir08 y qa_pixel (npz de 3 bandas). Las escenas de 2025 de la ronda 1 tienen las 5."""
    return BANDAS if fecha[5:7] in ("04", "05") else BANDAS_NDVI


def bajar_escena(anio: int, esc: dict, vs: list[dict], tok: str, m_crs, m_tr) -> str:
    destino = RAW / str(anio) / f"{esc['id']}.npz"
    if destino.exists():
        return "ya"
    # se lee en paralelo por banda y por bloques de ventanas. Desde la ronda 2 se lee la ventana de
    # origen (UTM, con 2 px de margen, recortada a la escena) y se reproyecta en memoria: WarpedVRT
    # bajaba ~4x más bytes. Difiere de WarpedVRT en ~0,3 % de los píxeles (vecino más cercano).
    def leer(b: str, bloque: list[dict]) -> list[tuple[str, str, np.ndarray]]:
        res = []
        with rasterio.open(esc["hrefs"][b] + "?" + tok) as src:
            escena = Window(0, 0, src.width, src.height)
            for v in bloque:
                ventana = Window(v["col"], v["row"], LADO, LADO)
                a = np.zeros((LADO, LADO), np.uint16)
                sb = transform_bounds(m_crs, src.crs, *rasterio.windows.bounds(ventana, m_tr))
                sw = from_bounds(*sb, transform=src.transform).round_offsets().round_lengths()
                sw = Window(sw.col_off - 2, sw.row_off - 2, sw.width + 4, sw.height + 4)
                try:
                    sw = sw.intersection(escena)
                except rasterio.errors.WindowError:  # ventana fuera de la escena
                    res.append((f"{v['fips']}_{v['k']}", b, a))
                    continue
                reproject(src.read(1, window=sw), a, src_transform=src.window_transform(sw), src_crs=src.crs,
                          dst_transform=rasterio.windows.transform(ventana, m_tr), dst_crs=m_crs,
                          resampling=Resampling.nearest, src_nodata=0, dst_nodata=0)
                res.append((f"{v['fips']}_{v['k']}", b, a))
        return res

    bandas = bandas_escena(esc["fecha"])
    trozos = [(b, vs[i:i + 8]) for b in bandas for i in range(0, len(vs), 8)]
    arr: dict[str, dict[str, np.ndarray]] = {}
    with ThreadPoolExecutor(max_workers=INTERNOS) as ex:
        for res in ex.map(lambda t: leer(*t), trozos):
            for clave, b, a in res:
                arr.setdefault(clave, {})[b] = a
    tmp = INTERIM / "parciales" / f"{esc['id']}.part.npz"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(tmp, **{k: np.stack([a[b] for b in bandas]) for k, a in sorted(arr.items())})
    destino.parent.mkdir(parents=True, exist_ok=True)
    os.replace(tmp, destino)
    return "ok"


def registrar_manifest(anio: int, escenas: dict[str, dict]) -> None:
    man = REPO / "manifest.csv"
    asegurar_manifest(man)
    filas = list(csv.DictReader(open(man, encoding="utf-8")))
    campos = ["paquete", "archivo", "fuente", "producto", "version", "fecha_descarga", "consulta_o_url"]
    idx = {f["archivo"]: i for i, f in enumerate(filas)}
    hoy = dt.date.today().isoformat()
    for p in sorted((RAW / str(anio)).glob("*.npz")):
        rel = p.relative_to(REPO).as_posix()
        esc = escenas.get(p.stem)
        with np.load(p) as z:
            nb = z[z.files[0]].shape[0] if z.files else len(BANDAS)
        bandas = ",".join(BANDAS if nb == len(BANDAS) else BANDAS_NDVI)
        url = esc["hrefs"]["red"].rsplit("/", 1)[0] + f"/ (ventanas de {bandas})" if esc else ""
        fila = {"paquete": "teledeteccion", "archivo": rel, "fuente": "USGS/NASA vía Microsoft Planetary Computer",
                "producto": f"Landsat Collection 2 Level-2 SR {p.stem} (ventanas {LADO}x{LADO} px por condado)",
                "version": "Collection 2", "fecha_descarga": hoy, "consulta_o_url": url}
        if rel in idx:
            fila["fecha_descarga"] = filas[idx[rel]]["fecha_descarga"]
            filas[idx[rel]] = fila
        else:
            filas.append(fila)
    # escritura atómica: si el proceso muere a mitad, el manifest queda intacto
    tmp = INTERIM / "manifest.csv.part"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    os.replace(tmp, man)


def main() -> None:
    cfg = config()
    anios = [int(a) for a in sys.argv[1:]] or list(range(2025, 2007, -1))
    rango_max = int(os.environ.get("TD_RANGO_MAX", "99"))
    vents = ventanas()
    lons = [v["lon"] for v in vents]
    lats = [v["lat"] for v in vents]
    bbox = [min(lons) - 0.1, min(lats) - 0.1, max(lons) + 0.1, max(lats) + 0.1]
    with rasterio.open(MASCARA) as m:
        m_crs, m_tr = m.crs, m.transform
        global M_W, M_H
        M_W, M_H = m.width, m.height
    for anio in anios:
        escenas = buscar(anio, bbox)
        tareas = seleccionar(anio, escenas, vents, rango_max)
        por_id = {e["id"]: e for e in escenas}
        log(f"{anio}: {len(escenas)} escenas STAC, {len(tareas)} seleccionadas (rango_max={rango_max})")
        tok, t0, hechas = token(), time.time(), 0
        with ThreadPoolExecutor(max_workers=int(os.environ.get("TD_WORKERS", "8"))) as ex:
            futs = {ex.submit(bajar_escena, anio, por_id[i], vs, tok, m_crs, m_tr): i
                    for i, vs in sorted(tareas.items())}
            for fu in as_completed(futs):
                hechas += 1
                try:
                    fu.result()
                except Exception as e:  # se reintenta en la próxima corrida
                    log(f"{anio} {futs[fu]} ERROR {type(e).__name__}: {str(e)[:150]}")
                if hechas % 10 == 0:
                    log(f"{anio}: {hechas}/{len(tareas)} escenas en {time.time() - t0:.0f} s")
                    registrar_manifest(anio, por_id)
        registrar_manifest(anio, por_id)
        log(f"{anio}: listo en {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
