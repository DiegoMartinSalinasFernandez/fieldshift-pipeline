"""Relleno desde LP DAAC de los compuestos de MODIS que faltan en Planetary Computer (T119, para T100).

`docs/research/modis_fechas.md` (T090, MOD13Q1) y `docs/research/lst_fechas.md` (T105, MOD11A2) encontraron
compuestos que están en CMR (LP DAAC) y no en Planetary Computer (PC). Este módulo, llamado desde
`download.py` después de la búsqueda en PC, hace por producto y año:

1. busca en CMR los gránulos de las teselas de los estados de FIELDSHIFT_ESTADOS (los mismos bbox por grupo
   de estados que usa download.py; no hay una lista fija de compuestos);
2. resta lo que PC ya tiene (compuesto, tesela): queda lo que hay que rellenar;
3. baja cada HDF4 de LP DAAC con el login de Earthdata de ~/.netrc (no se imprime nada de la credencial),
   lee las capas que usa process.py, las reduce a la misma resolución que el overview del COG de PC que baja
   download.py y recorta la misma ventana;
4. guarda `data/raw/vegetacion/<producto>/<año>/<granulo>.lpdaac.tif` (el sufijo dice que viene de LP DAAC;
   process.py lee la fecha y la tesela de las partes 2 y 3 del nombre, igual que en los de PC) y anota una
   fila por archivo en manifest.csv. El HDF original no se guarda (como en PC, raw guarda la ventana leída).

Remuestreo: los overviews de los COG de PC están hechos con GDAL `cubic`, cada nivel a partir del anterior
(factor 2 por nivel). Se comprobó el 2026-11-15 contra MOD11A2.A2023201.h11v04 (LST_Day_1km, overview 0:
diferencia 0) y MOD13Q1.A2023193.h11v04 (NDVI, overview 1: hasta 1 unidad de redondeo; pixel reliability:
diferencia 0). Acá se hace lo mismo con rasterio/GDAL. Las QC de MOD11A2 (`QC_Day`, `QC_Night`, campos de
bits) no se pueden promediar: se toman por vecino más cercano y van como bandas 3 y 4 (process.py no las usa;
los GeoTIFF de PC solo tienen las dos LST).

Sin ~/.netrc con `urs.earthdata.nasa.gov`: se avisa y no se rellena nada (download.py sigue como antes).
Lectura de HDF4: pyhdf (rasterio no trae el driver HDF4); se importa solo al bajar.
"""
from __future__ import annotations

import csv
import datetime as dt
import netrc
import os
import shutil
import tempfile
from pathlib import Path

import numpy as np
import requests

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "raw" / "vegetacion"
INTERIM = REPO / "data" / "interim" / "vegetacion"
CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
URS = "urs.earthdata.nasa.gov"
SUFIJO = "lpdaac"
FUENTE = "NASA LP DAAC (Earthdata, HDF4)"

# Grilla sinusoidal de MODIS: tesela de 1111950,52 m, origen en (-20015109,354, 10007554,677)
SINU = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +R=6371007.181 +units=m +no_defs"
TESELA_M = 1111950.5197665233
X0, Y0 = -20015109.355798, 10007554.677899

# capas por producto: (nombre del SDS en el HDF, descripción de la banda como en los GeoTIFF de PC, remuestreo)
CAPAS = {
    "mod13q1": [("250m 16 days NDVI", "250m_16_days_NDVI", "cubic"),
                ("250m 16 days EVI", "250m_16_days_EVI", "cubic"),
                ("250m 16 days pixel reliability", "250m_16_days_pixel_reliability", "cubic")],
    "mod11a2": [("LST_Day_1km", "LST_Day_1km", "cubic"),
                ("LST_Night_1km", "LST_Night_1km", "cubic"),
                ("QC_Day", "QC_Day", "nearest"),
                ("QC_Night", "QC_Night", "nearest")],
}


# ---------------------------------------------------------------- CMR y diferencia con PC

def clave(granulo: str) -> tuple[str, str]:
    """'MOD13Q1.A2025185.h10v04.061.2025203...' -> ('A2025185', 'h10v04')."""
    p = granulo.split(".")
    return p[1], p[2]


def url_datos(entry: dict) -> str | None:
    for l in entry.get("links", []):
        h = l.get("href", "")
        if l.get("rel", "").endswith("/data#") and h.startswith("https://") and h.endswith(".hdf"):
            return h
    return None


def cmr_granulos(prefijo: str, bbox: list[float], anio: int, get=None) -> dict[tuple[str, str], dict]:
    """Gránulos v061 de CMR que empiezan en `anio` y tocan el bbox: {(compuesto, tesela): {id, url, bytes}}."""
    get = get or requests.get
    out, page = {}, 1
    while True:
        r = get(CMR, params={"short_name": prefijo, "version": "061", "bounding_box": ",".join(map(str, bbox)),
                             "temporal": f"{anio}-01-01T00:00:00Z,{anio}-12-31T23:59:59Z",
                             "page_size": 2000, "page_num": page}, timeout=120)
        r.raise_for_status()
        es = r.json()["feed"]["entry"]
        for e in es:
            gid = e.get("producer_granule_id") or e.get("title", "")
            gid = gid.removesuffix(".hdf")
            if not gid.startswith(prefijo + ".") or not clave(gid)[0].startswith(f"A{anio}"):
                continue  # la búsqueda temporal trae también el compuesto que cruza el año
            k = clave(gid)
            previo = out.get(k)
            if previo is None or gid > previo["id"]:  # si hay dos producciones, la más reciente
                out[k] = {"id": gid, "url": url_datos(e), "mb": e.get("granule_size")}
        if len(es) < 2000:
            return out
        page += 1


def pc_claves(items: list[dict]) -> set[tuple[str, str]]:
    return {clave(it["id"]) for it in items}


def faltantes(cmr: dict[tuple[str, str], dict], pc: set[tuple[str, str]]) -> list[tuple[str, str]]:
    """Lo que está en CMR y no en PC, ordenado por compuesto y tesela."""
    return sorted(set(cmr) - set(pc))


def faltantes_grupos(prefijo: str, grupos: list, anio: int, items_pc: list[dict], get=None
                     ) -> list[tuple[dict, list[float]]]:
    """[(gránulo de CMR, bbox)] a rellenar, con la unión de los bbox de los grupos que tocan cada tesela."""
    from src.vegetacion.download import union_bbox
    por_clave: dict[tuple[str, str], tuple[dict, list]] = {}
    for _, bbox in grupos:
        for k, g in cmr_granulos(prefijo, bbox, anio, get=get).items():
            por_clave.setdefault(k, (g, []))[1].append(bbox)
    falta = faltantes({k: v[0] for k, v in por_clave.items()}, pc_claves(items_pc))
    return [(por_clave[k][0], union_bbox(por_clave[k][1])) for k in falta]


# ---------------------------------------------------------------- nombres y rutas

def nombre_salida(granulo: str) -> str:
    return f"{granulo.removesuffix('.hdf')}.{SUFIJO}.tif"


def ruta_salida(prod_key: str, granulo: str, raw: Path | None = None) -> Path:
    anio = clave(granulo)[0][1:5]
    return (raw or RAW) / prod_key / anio / nombre_salida(granulo)


# ---------------------------------------------------------------- Earthdata

def credenciales(ruta: Path | None = None) -> tuple[str, str] | None:
    """(usuario, clave) de urs.earthdata.nasa.gov en ~/.netrc (o $NETRC), o None. No se imprime nunca."""
    if ruta is None:
        if os.environ.get("NETRC"):
            ruta = Path(os.environ["NETRC"])
        else:
            casa = Path.home()
            ruta = next((p for p in (casa / ".netrc", casa / "_netrc") if p.exists()), casa / ".netrc")
    if not Path(ruta).exists():
        return None
    try:
        a = netrc.netrc(str(ruta)).authenticators(URS)
    except (netrc.NetrcParseError, OSError):
        return None
    return (a[0], a[2]) if a and a[0] and a[2] else None


class SesionEarthdata(requests.Session):
    """Mantiene el login solo en las redirecciones hacia o desde URS (el patrón de NASA para LP DAAC)."""

    def __init__(self, usuario: str, clave_: str):
        super().__init__()
        self.auth = (usuario, clave_)

    def rebuild_auth(self, prepared_request, response):
        if "Authorization" in prepared_request.headers:
            de = requests.utils.urlparse(response.request.url).hostname
            a = requests.utils.urlparse(prepared_request.url).hostname
            if de != a and URS not in (de, a):
                del prepared_request.headers["Authorization"]


def sesion_earthdata(ruta: Path | None = None) -> SesionEarthdata | None:
    c = credenciales(ruta)
    return SesionEarthdata(*c) if c else None


# ---------------------------------------------------------------- lectura y remuestreo

def transform_tesela(tesela: str, n: int):
    from rasterio.transform import Affine
    h, v = int(tesela[1:3]), int(tesela[4:6])
    px = TESELA_M / n
    return Affine(px, 0.0, X0 + h * TESELA_M, 0.0, -px, Y0 - v * TESELA_M)


def leer_hdf(path: Path, capas: list[tuple[str, str, str]]) -> list[tuple[str, np.ndarray, float | None, dict]]:
    from pyhdf.SD import SD, SDC
    sd = SD(str(path), SDC.READ)
    try:
        out = []
        for sds, banda, _ in capas:
            ds = sd.select(sds)
            at = ds.attributes()
            a, nd = ds.get(), at.get("_FillValue")
            if a.dtype == np.int8:  # pixel reliability: int8 con relleno -1 en el HDF, uint8 con 255 en los COG de PC
                a, nd = a.view(np.uint8), (None if nd is None else int(nd) % 256)
            out.append((banda, a, nd,
                        {"scale_factor": str(at.get("scale_factor", "")), "add_offset": str(at.get("add_offset", ""))}))
            ds.endaccess()
        return out
    finally:
        sd.end()


def reducir(a: np.ndarray, nodata, niveles: int, metodo: str, crs: str, transform):
    """Reduce a la mitad `niveles` veces con GDAL (como los overviews de PC). Devuelve (array, transform)."""
    from rasterio.enums import Resampling
    from rasterio.io import MemoryFile
    rs = Resampling[metodo]
    for _ in range(niveles):
        h, w = a.shape[0] // 2, a.shape[1] // 2
        perfil = {"driver": "GTiff", "width": a.shape[1], "height": a.shape[0], "count": 1, "dtype": a.dtype,
                  "crs": crs, "transform": transform, "nodata": nodata}
        with MemoryFile() as mf:
            with mf.open(**perfil) as d:
                d.write(a, 1)
            with mf.open() as d:
                a = d.read(1, out_shape=(h, w), resampling=rs)
        transform = transform * transform.scale(2, 2)
    return a, transform


def ventana(bbox: list[float], transform, shape: tuple[int, int]):
    """La misma ventana que download.bajar_item: bbox (EPSG:4326) llevado a la grilla, recortado y redondeado."""
    from rasterio.transform import array_bounds
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds
    xb = transform_bounds("EPSG:4326", SINU, *bbox, densify_pts=50)
    l, b_, r, t = array_bounds(shape[0], shape[1], transform)
    xb = (max(xb[0], l), max(xb[1], b_), min(xb[2], r), min(xb[3], t))
    if xb[0] >= xb[2] or xb[1] >= xb[3]:
        return None
    return from_bounds(*xb, transform=transform).round_offsets().round_lengths()


def convertir(hdf: Path, prod_key: str, overview: int, granulo: str, bbox: list[float], destino: Path,
              url: str = "") -> str:
    """HDF4 de LP DAAC -> GeoTIFF con las mismas bandas, escala y ventana que los de PC."""
    import rasterio
    from rasterio.windows import transform as win_transform
    tes = clave(granulo)[1]
    arrs, perfil, win = [], None, None
    for banda, a, nd, tags in leer_hdf(hdf, CAPAS[prod_key]):
        metodo = next(m for _, b, m in CAPAS[prod_key] if b == banda)
        r, tr = reducir(a, nd if metodo == "cubic" else None, overview + 1, metodo, SINU,
                        transform_tesela(tes, a.shape[0]))
        if win is None:
            win = ventana(bbox, tr, r.shape)
            if win is None:
                return "fuera"
            perfil = {"driver": "GTiff", "crs": SINU, "transform": win_transform(win, tr),
                      "compress": "deflate", "predictor": 2, "tiled": False}
        sub = r[win.row_off:win.row_off + win.height, win.col_off:win.col_off + win.width]
        arrs.append((banda, sub, nd, tags))
    dtype = np.result_type(*[a.dtype for _, a, _, _ in arrs])
    h, w = arrs[0][1].shape
    tmp = INTERIM / "_part" / (destino.name + ".part")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(tmp, "w", count=len(arrs), dtype=dtype, width=w, height=h, **perfil) as dst:
        for i, (banda, a, nd, tags) in enumerate(arrs, start=1):
            dst.write(a.astype(dtype), i)
            dst.set_band_description(i, banda)
            dst.update_tags(i, nodata=str(nd), **tags)
        dst.update_tags(item_id=granulo, fuente=FUENTE, url=url, overview_level=str(overview),
                        remuestreo="GDAL cubic, factor 2 por nivel (como los overviews de PC); QC: nearest")
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp), str(destino))
    return "ok"


def bajar_granulo(g: dict, prod_key: str, overview: int, bbox: list[float], sesion: requests.Session,
                  raw: Path | None = None) -> str:
    destino = ruta_salida(prod_key, g["id"], raw)
    if destino.exists():
        return "ya"
    if not g.get("url"):
        raise RuntimeError(f"{g['id']}: CMR no trae el enlace de datos")
    INTERIM.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=INTERIM) as d:
        hdf = Path(d) / (g["id"] + ".hdf")
        with sesion.get(g["url"], stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(hdf, "wb") as f:
                for trozo in r.iter_content(1 << 20):
                    f.write(trozo)
        return convertir(hdf, prod_key, overview, g["id"], bbox, destino, url=g["url"])


# ---------------------------------------------------------------- manifest

def registrar_manifest(prod_key: str, prefijo: str, raw: Path | None = None, man: Path | None = None) -> int:
    raw = raw or RAW
    man = man or REPO / "manifest.csv"
    if not man.exists() or man.stat().st_size == 0:
        man.write_text("paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n", encoding="utf-8")
    with open(man, encoding="utf-8") as f:
        ya = {r["archivo"] for r in csv.DictReader(f)}
    filas = []
    for p in sorted((raw / prod_key).rglob(f"*.{SUFIJO}.tif")):
        try:
            rel = p.relative_to(REPO).as_posix()
        except ValueError:
            rel = p.as_posix()
        if rel in ya:
            continue
        granulo = p.name.removesuffix(f".{SUFIJO}.tif")
        fecha = dt.date.fromtimestamp(p.stat().st_mtime).isoformat()
        bandas = "+".join(b for _, b, _ in CAPAS[prod_key])
        filas.append(["vegetacion", rel, FUENTE, prefijo, "061", fecha,
                      f"{CMR}?short_name={prefijo}&version=061 granulo={granulo}.hdf bandas={bandas} "
                      f"ventana=condados (remuestreo cubic como el overview de PC)"])
    if filas:
        with open(man, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(filas)
    return len(filas)
