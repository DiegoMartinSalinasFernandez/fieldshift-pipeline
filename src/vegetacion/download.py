"""Descarga de MODIS (MOD13Q1, MOD11A2) para la zona de estudio desde Microsoft Planetary Computer.

Acceso público sin login (no hay credencial de Earthdata): COGs de la colección 6.1 en
Planetary Computer, firmados con un token SAS anónimo. Para cada tesela/fecha se lee solo la
ventana que cubre los condados y se guarda tal cual como GeoTIFF en data/raw/vegetacion/.

- MOD13Q1: NDVI, EVI y pixel reliability, leídos del overview 1 del COG (factor 4, ~927 m)
  porque la tesela completa a 250 m baja a ~1 MB/s y no entra en el tiempo ni en 5 GB.
- MOD11A2: LST día y noche, overview 0 del COG (factor 2, ~2 km) para no pasar los 5 GB; el
  overview promedia los píxeles válidos (los sin dato, 0, quedan como nodata).

Relleno (T119): los compuestos que están en CMR de LP DAAC y no en PC se bajan de LP DAAC con el login de
Earthdata de ~/.netrc (src/vegetacion/lpdaac.py) y quedan como <granulo>.lpdaac.tif. Solo corre con
FIELDSHIFT_RELLENO_LPDAAC=1: son ~8-14 GB de transferencia para los 10 estados, más de los 5 GB que necesitan
el OK del humano (CLAUDE.md, regla 6; tarea T100). Sin esa variable, o sin ~/.netrc, se sigue solo con PC.

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
from src.vegetacion import lpdaac  # noqa: E402

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


MARGEN = 0.05  # grados alrededor de cada estado


def bbox_zona() -> list[float]:
    """Un solo bbox para todos los condados (lo usaba todo antes de T023; queda por compatibilidad)."""
    g = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg")
    b = g.total_bounds
    return [float(b[0]) - MARGEN, float(b[1]) - MARGEN, float(b[2]) + MARGEN, float(b[3]) + MARGEN]


def _se_tocan(a: list[float], b: list[float]) -> bool:
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def grupos_bbox(gpkg: Path | None = None) -> list[tuple[tuple[str, ...], list[float]]]:
    """[(estados, bbox)] con un bbox (oeste, sur, este, norte; EPSG:4326) por estado de condados.gpkg.

    Los bbox de estados vecinos que se tocan (con el margen) se juntan en uno: así una tesela o una
    ventana no se baja dos veces y, con estados contiguos como IA, IL e IN, queda un único grupo cuyo
    bbox es exactamente el de bbox_zona() (min y max de los mismos números, con el mismo margen).
    Con estados lejanos (OH y NE, OH y MN) cada uno queda con su bbox y no se bajan los del medio.
    """
    g = gpd.read_file(gpkg or REPO / "data" / "reference" / "condados.gpkg")
    if g.crs is not None and g.crs.to_epsg() != 4326:
        g = g.to_crs(4326)
    est = g["fips"].astype(str).str.zfill(5).str[:2]
    alfa = g["estado"].astype(str) if "estado" in g else est
    grupos = []
    for e, sub in sorted(g.groupby(est)):
        b = sub.total_bounds
        grupos.append(((str(alfa[sub.index[0]]),), [float(b[0]) - MARGEN, float(b[1]) - MARGEN,
                                                   float(b[2]) + MARGEN, float(b[3]) + MARGEN]))
    junto = True
    while junto:
        junto = False
        for i in range(len(grupos)):
            for j in range(i + 1, len(grupos)):
                (ei, bi), (ej, bj) = grupos[i], grupos[j]
                if _se_tocan(bi, bj):
                    grupos[i] = (tuple(sorted(ei + ej)), [min(bi[0], bj[0]), min(bi[1], bj[1]),
                                                          max(bi[2], bj[2]), max(bi[3], bj[3])])
                    del grupos[j]
                    junto = True
                    break
            if junto:
                break
    return sorted(grupos)


def union_bbox(bboxes: list[list[float]]) -> list[float]:
    return [min(b[0] for b in bboxes), min(b[1] for b in bboxes),
            max(b[2] for b in bboxes), max(b[3] for b in bboxes)]


def buscar_grupos(coleccion: str, prefijo: str, grupos: list, anio: int) -> list[tuple[dict, list[float]]]:
    """Items de todos los grupos sin repetir, cada uno con la ventana que le toca.

    Si una tesela cae en más de un grupo se baja una sola vez, con la unión de los bbox de esos
    grupos. Con un solo grupo (IA, IL, IN) la ventana es la misma de antes.
    """
    por_id: dict[str, tuple[dict, list[list[float]]]] = {}
    for _, bbox in grupos:
        for it in buscar(coleccion, prefijo, bbox, anio):
            por_id.setdefault(it["id"], (it, []))[1].append(bbox)
    return [(it, union_bbox(bbs)) for _, (it, bbs) in sorted(por_id.items())]


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


def asegurar_manifest(man: Path) -> None:
    """En una máquina nueva no hay manifest.csv (no va en git): lo crea con el encabezado (CLAUDE.md §7)."""
    if not man.exists() or man.stat().st_size == 0:
        man.write_text("paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n", encoding="utf-8")


def registrar_manifest(prod_key: str) -> None:
    prod = PRODUCTOS[prod_key]
    man = REPO / "manifest.csv"
    asegurar_manifest(man)
    with open(man, encoding="utf-8") as f:
        ya = {r["archivo"] for r in csv.DictReader(f)}
    filas = []
    for p in sorted((RAW / prod["prefijo"].lower()).rglob("*.tif")):
        if p.name.endswith(f".{lpdaac.SUFIJO}.tif"):  # los de LP DAAC los anota lpdaac.registrar_manifest
            continue
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


def rellenar_lpdaac(pk: str, anio: int, grupos: list, items_pc: list[dict], sesion) -> int:
    """Baja de LP DAAC lo que está en CMR y no en PC para ese año. Devuelve la cantidad de errores."""
    prod = PRODUCTOS[pk]
    try:
        falta = lpdaac.faltantes_grupos(prod["prefijo"], grupos, anio, items_pc)
    except Exception as e:  # CMR caído: se reintenta en la próxima corrida
        log(f"ERROR CMR {pk} {anio}: {type(e).__name__}: {str(e)[:200]}")
        return 1
    pend = [(g, bb) for g, bb in falta if not lpdaac.ruta_salida(pk, g["id"], RAW).exists()]
    log(f"{pk} {anio}: {len(falta)} granulos en CMR y no en PC, {len(pend)} pendientes (LP DAAC)")
    errores = 0
    with ThreadPoolExecutor(4) as ex:
        futs = {ex.submit(lpdaac.bajar_granulo, g, pk, prod["overview"], bb, sesion, RAW): g["id"] for g, bb in pend}
        for fu in as_completed(futs):
            try:
                fu.result()
            except Exception as e:
                errores += 1
                log(f"ERROR LP DAAC {futs[fu]}: {type(e).__name__}: {str(e)[:200]}")
    lpdaac.registrar_manifest(pk, prod["prefijo"], RAW)
    return errores


def main() -> None:
    prods = [sys.argv[1]] if len(sys.argv) > 1 else list(PRODUCTOS)
    cfg = cargar_config()
    a0 = int(sys.argv[2]) if len(sys.argv) > 2 else int(cfg["periodo"]["anio_inicio"])
    a1 = int(sys.argv[3]) if len(sys.argv) > 3 else int(cfg["periodo"]["anio_fin"])
    grupos = grupos_bbox()
    log("grupos de estados: " + "; ".join(f"{'+'.join(e)} {[round(v, 2) for v in b]}" for e, b in grupos))
    errores = 0
    sesion = None
    if os.environ.get("FIELDSHIFT_RELLENO_LPDAAC") != "1":
        log("relleno desde LP DAAC apagado (FIELDSHIFT_RELLENO_LPDAAC=1 para prenderlo; necesita el OK de T100)")
    else:
        sesion = lpdaac.sesion_earthdata()
    if os.environ.get("FIELDSHIFT_RELLENO_LPDAAC") == "1" and sesion is None:
        msg = ("AVISO: sin login de Earthdata (urs.earthdata.nasa.gov en ~/.netrc): no se rellenan desde LP DAAC "
               "los compuestos que faltan en Planetary Computer (T119). Se sigue solo con PC.")
        print(msg, file=sys.stderr)
        log(msg)
    for pk in prods:
        prod = PRODUCTOS[pk]
        for anio in range(max(a0, prod["desde"]), a1 + 1):
            items = buscar_grupos(prod["coleccion"], prod["prefijo"], grupos, anio)
            pend = [(it, bb) for it, bb in items
                    if not (RAW / prod["prefijo"].lower() / str(anio) / f"{it['id']}.tif").exists()]
            log(f"{pk} {anio}: {len(items)} items, {len(pend)} pendientes")
            # el token SAS anónimo vence a los ~45 min: se pide uno nuevo por año (si no, todo da 403)
            token = requests.get(SAS, timeout=60).json()["token"] if pend else ""
            with ThreadPoolExecutor(12) as ex:
                futs = {ex.submit(bajar_item, it, prod, bb, token): it["id"] for it, bb in pend}
                for fu in as_completed(futs):
                    try:
                        fu.result()
                    except Exception as e:  # se reintenta en la próxima corrida
                        errores += 1
                        log(f"ERROR {futs[fu]}: {type(e).__name__}: {str(e)[:200]}")
            registrar_manifest(pk)
            if sesion is not None:
                errores += rellenar_lpdaac(pk, anio, grupos, [it for it, _ in items], sesion)
            log(f"{pk} {anio}: listo")
    if errores:
        log(f"terminó con {errores} archivos sin bajar: volver a correr")
        sys.exit(1)


if __name__ == "__main__":
    main()
