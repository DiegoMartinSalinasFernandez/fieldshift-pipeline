"""Descarga ECOSTRESS colección 2 (LP DAAC) recortada a una ventana agrícola por condado.

Para cada pasada diurna (granulo ECO_L3T_JET.002) que cubre el bbox de los estados, lee de los COG
de LP DAAC (lectura por rango, sin bajar la tesela entera) la ventana de 32x32 píxeles de 70 m
(2,24 km) alrededor del punto agrícola de cada condado, en las capas:
  ECO_L2T_LSTE.002: LST, QC, cloud · ECO_L3T_JET.002: ETdaily · ECO_L4T_ESI.002: ESI
y guarda por condado y pasada las estadísticas de los píxeles agrícolas, de buena calidad y sin nube.
Las teselas completas pasarían varios TB: lo que queda en raw es esa extracción, un CSV por mes.

Reanudable: un mes ya presente en data/raw/ecostress/ no se vuelve a bajar; el mes en curso se
escribe en data/interim/ecostress/ y se mueve a raw cuando está completo.

Uso: python src/ecostress/download.py [--meses 2025-07,2025-06] [--workers 24] [--max-minutos 30]
Auth: token de Earthdata pedido por requests (lee ~/.netrc solo); nunca se imprime.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import requests
from pyproj import Transformer
from rasterio.mask import mask as rmask
from rasterio.windows import Window

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import estados_config  # noqa: E402
from src.common.manifest import asegurar_manifest  # noqa: E402

RAW = REPO / "data/raw/ecostress"
INTERIM = REPO / "data/interim/ecostress"
MANIFEST = REPO / "manifest.csv"
CMR = "https://cmr.earthdata.nasa.gov/search/granules.umm_json"
LPDAAC = "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected"
# Primera tanda (IA, IL, IN): hasta r006 el bbox era "-91.6,37.0,-84.8,43.5" y dejaba afuera el oeste de
# Iowa (83 condados). Los meses que quedaron en raw con ese bbox se completan con un suplemento
# ecostress_extraccion_<mes>_oeste.csv (solo las escenas que no estaban en escenas_hechas_<mes>.txt).
# Solo aplica a una máquina que tenga IA: los demás estados se bajan siempre con el bbox completo.
MESES_BBOX_ESTE = (["2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10"]
                   if "IA" in estados_config() else [])
MITAD = 16  # ventana de 32x32 píxeles de 70 m
COLS = ["fips", "granulo", "tesela", "fecha_hora_utc", "n_px_agricolas", "n_px_lst", "lst_k_media",
        "n_px_et", "et_daily_media", "n_px_esi", "esi_media"]

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "3")
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "2")


def log(msg: str) -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    linea = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(linea, flush=True)
    with open(INTERIM / "download.log", "a", encoding="utf-8") as fh:
        fh.write(linea + "\n")


def bboxes_cmr(margen: float = 0.1) -> list[str]:
    """Un bbox de CMR (oeste,sur,este,norte) por estado de condados.gpkg, con margen en grados.

    Antes era uno solo fijo, "-96.7,37.0,-84.7,43.6" (IA, IL, IN). Ahora sale de los estados en uso, uno
    por estado para que dos estados lejanos (por ejemplo OH y MN) no traigan las pasadas de los del medio.
    """
    global _BBOXES
    if _BBOXES is None:
        g = gpd.read_file(REPO / "data/reference/condados.gpkg").to_crs(4326)
        g["est"] = g["fips"].astype(str).str.zfill(5).str[:2]
        _BBOXES = []
        for _, sub in sorted(g.groupby("est")):
            b = sub.total_bounds
            _BBOXES.append(",".join(f"{v:.1f}" for v in (b[0] - margen, b[1] - margen,
                                                           b[2] + margen, b[3] + margen)))
    return _BBOXES


_BBOXES: list[str] | None = None


# ---------- puntos agrícolas por condado ----------
def puntos_condados() -> pd.DataFrame:
    """Píxel agrícola (CDL, al menos un año) más cercano al centroide agrícola de cada condado."""
    out = INTERIM / "puntos_condados.csv"
    if out.exists():
        return pd.read_csv(out, dtype={"fips": str})
    g = gpd.read_file(REPO / "data/reference/condados.gpkg")
    filas = []
    with rasterio.open(REPO / "data/reference/mascara_agricola.tif") as src:
        g = g.to_crs(src.crs)
        for _, c in g.sort_values("fips").iterrows():
            arr, tr = rmask(src, [c.geometry], crop=True, filled=True, nodata=0)
            fil, col = np.nonzero(arr[0] == 1)
            if len(fil) == 0:
                continue
            xs, ys = rasterio.transform.xy(tr, fil, col)
            xs, ys = np.asarray(xs), np.asarray(ys)
            i = int(np.argmin((xs - xs.mean()) ** 2 + (ys - ys.mean()) ** 2))
            filas.append({"fips": c.fips, "x_5070": round(float(xs[i]), 1), "y_5070": round(float(ys[i]), 1)})
    df = pd.DataFrame(filas)
    t = Transformer.from_crs(5070, 4326, always_xy=True)
    df["lon"], df["lat"] = t.transform(df.x_5070.values, df.y_5070.values)
    df.to_csv(out, index=False)
    return df


# ---------- CMR ----------
def granulos_mes(producto: str, mes: str) -> list[dict]:
    a, m = map(int, mes.split("-"))
    fin = date(a + (m == 12), m % 12 + 1, 1)
    params = {"short_name": producto, "version": "002", "bounding_box[]": bboxes_cmr(),
              "options[bounding_box][or]": "true", "page_size": 2000,
              "temporal": f"{mes}-01T00:00:00Z,{fin.isoformat()}T00:00:00Z"}
    res, after = [], None
    while True:
        h = {"CMR-Search-After": after} if after else {}
        r = requests.get(CMR, params=params, headers=h, timeout=120)
        r.raise_for_status()
        items = r.json()["items"]
        for it in items:
            u = it["umm"]
            rects = u["SpatialExtent"]["HorizontalSpatialDomain"]["Geometry"].get("BoundingRectangles", [])
            pols = u["SpatialExtent"]["HorizontalSpatialDomain"]["Geometry"].get("GPolygons", [])
            if pols:
                pts = pols[0]["Boundary"]["Points"]
                lons, lats = [p["Longitude"] for p in pts], [p["Latitude"] for p in pts]
                bb = (min(lons), min(lats), max(lons), max(lats))
            elif rects:
                b = rects[0]
                bb = (b["WestBoundingCoordinate"], b["SouthBoundingCoordinate"],
                      b["EastBoundingCoordinate"], b["NorthBoundingCoordinate"])
            else:
                bb = None
            res.append({"ur": u["GranuleUR"], "bbox": bb})
        after = r.headers.get("CMR-Search-After")
        if not items or not after or len(items) < params["page_size"]:
            break
    return res


def clave(ur: str) -> tuple[str, str, str]:
    """(orbita_escena_tesela, tesela, fecha_hora) desde ECOv002_L3T_JET_00406_004_14SPJ_20180801T222125_0712_01."""
    m = re.match(r"ECOv002_L\w+?_(?:LSTE|JET|ESI)_(\d+)_(\d+)_(\w{5})_(\d{8}T\d{6})_", ur)
    return f"{m.group(1)}_{m.group(2)}_{m.group(3)}", m.group(3), m.group(4)


# ---------- lectura ----------
_local = threading.local()
_cache_ag: dict = {}
_lock = threading.Lock()


def sesion(token: str) -> requests.Session:
    if not hasattr(_local, "s"):
        _local.s = requests.Session()
        _local.s.headers["Authorization"] = "Bearer " + token
    return _local.s


def firmada(token: str, url: str) -> str:
    for intento in range(4):
        try:
            r = sesion(token).get(url, allow_redirects=False, timeout=60)
            if r.status_code in (301, 302, 303, 307):
                return r.headers["Location"]
            r.raise_for_status()
        except requests.RequestException:
            time.sleep(2 * (intento + 1))
    raise RuntimeError(f"sin redirección firmada: {url.rsplit('/', 1)[-1]}")


def ventanas(ds, tesela: str, puntos: pd.DataFrame) -> list[tuple]:
    """Ventana y máscara agrícola (a 70 m) de cada condado cuyo punto cae dentro de la tesela."""
    k = (tesela, ds.crs.to_string(), tuple(ds.transform)[:6])
    with _lock:
        if k in _cache_ag:
            return _cache_ag[k]
    t = Transformer.from_crs(4326, ds.crs, always_xy=True)
    x, y = t.transform(puntos.lon.values, puntos.lat.values)
    inv = ~ds.transform
    res = []
    with rasterio.open(REPO / "data/reference/mascara_agricola.tif") as m:
        t2 = Transformer.from_crs(ds.crs, m.crs, always_xy=True)
        for fips, xi, yi in zip(puntos.fips, x, y):
            c, f = inv * (xi, yi)
            c0, f0 = int(c) - MITAD, int(f) - MITAD
            if c0 < 0 or f0 < 0 or c0 + 2 * MITAD > ds.width or f0 + 2 * MITAD > ds.height:
                continue
            w = Window(c0, f0, 2 * MITAD, 2 * MITAD)
            cc, ff = np.meshgrid(np.arange(c0, c0 + 2 * MITAD) + 0.5, np.arange(f0, f0 + 2 * MITAD) + 0.5)
            px, py = ds.transform * (cc.ravel(), ff.ravel())
            mx, my = t2.transform(px, py)
            vals = np.array([v[0] for v in m.sample(zip(mx, my))]).reshape(cc.shape)
            res.append((fips, w, vals == 1))
    with _lock:
        _cache_ag[k] = res
    return res


def leer(token: str, url: str, wins: list[tuple]) -> list[np.ndarray] | None:
    try:
        with rasterio.open("/vsicurl/" + firmada(token, url)) as ds:
            return [ds.read(1, window=w) for _, w, _ in wins]
    except Exception:
        return None


def procesar_escena(token: str, jet_ur: str, lste_ur: str, esi_ur: str | None, puntos: pd.DataFrame):
    k, tesela, fh = clave(jet_ur)
    base = f"{LPDAAC}/ECO_L2T_LSTE.002/{lste_ur}/{lste_ur}"
    with rasterio.open("/vsicurl/" + firmada(token, base + "_LST.tif")) as ds:
        wins = ventanas(ds, tesela, puntos)
        if not wins:
            return []
        lst = [ds.read(1, window=w) for _, w, _ in wins]
    qc = leer(token, base + "_QC.tif", wins)
    nube = leer(token, base + "_cloud.tif", wins)
    if qc is None or nube is None:
        raise RuntimeError(f"faltan QC/cloud de {lste_ur}")
    # QC bits 0-1: 00 mejor calidad, 01 nominal; 10 nube, 11 sin producir. cloud: 1 = nube.
    buenos = [ag & ((qc[i] & 0b11) <= 1) & (nube[i] == 0) for i, (_, _, ag) in enumerate(wins)]
    if any(b.any() for b in buenos):
        et = leer(token, f"{LPDAAC}/ECO_L3T_JET.002/{jet_ur}/{jet_ur}_ETdaily.tif", wins)
        esi = leer(token, f"{LPDAAC}/ECO_L4T_ESI.002/{esi_ur}/{esi_ur}_ESI.tif", wins) if esi_ur else None
    else:
        # ningún píxel bueno en la pasada: ETdaily y ESI darían 0 píxeles válidos, no hace falta leerlas
        vacio = [np.zeros(b.shape, dtype="float32") for b in buenos]
        et, esi = vacio, (vacio if esi_ur else None)
    filas = []
    for i, (fips, _, ag) in enumerate(wins):
        bueno = buenos[i]
        fila = {"fips": fips, "granulo": k, "tesela": tesela, "fecha_hora_utc": fh,
                "n_px_agricolas": int(ag.sum())}
        for nom, arr, rng in (("lst", lst, (200, 350)), ("et", et, (0, 30)), ("esi", esi, (0, 2))):
            if arr is None:
                fila[f"n_px_{nom}"] = ""
                fila[{"lst": "lst_k_media", "et": "et_daily_media", "esi": "esi_media"}[nom]] = ""
                continue
            v = arr[i][bueno]
            v = v[np.isfinite(v) & (v >= rng[0]) & (v <= rng[1])]
            fila[f"n_px_{nom}"] = int(v.size)
            fila[{"lst": "lst_k_media", "et": "et_daily_media", "esi": "esi_media"}[nom]] = (
                f"{float(v.mean()):.4f}" if v.size else "")
        filas.append(fila)
    return filas


def bajar_mes(token: str, mes: str, puntos: pd.DataFrame, workers: int, limite: float, sufijo: str = "") -> bool:
    dest = RAW / f"ecostress_extraccion_{mes}{sufijo}.csv"
    if dest.exists():
        return True
    jet = granulos_mes("ECO_L3T_JET", mes)
    lste = {clave(g["ur"])[0]: g["ur"] for g in granulos_mes("ECO_L2T_LSTE", mes)}
    esi = {clave(g["ur"])[0]: g["ur"] for g in granulos_mes("ECO_L4T_ESI", mes)}
    # solo escenas cuyo bbox contiene algún punto de condado
    lon, lat = puntos.lon.values, puntos.lat.values
    escenas = []
    for g in sorted(jet, key=lambda g: g["ur"]):
        k = clave(g["ur"])[0]
        bb = g["bbox"]
        if k not in lste or bb is None:
            continue
        if ((lon >= bb[0]) & (lon <= bb[2]) & (lat >= bb[1]) & (lat <= bb[3])).any():
            escenas.append((g["ur"], lste[k], esi.get(k)))
    part = INTERIM / f"ecostress_extraccion_{mes}{sufijo}.csv.part"
    lista = INTERIM / f"escenas_hechas_{mes}{sufijo}.txt"
    hechas = set()
    if sufijo:
        # suplemento: las escenas del archivo principal (ya en raw) no se repiten
        hechas = set((INTERIM / f"escenas_hechas_{mes}.txt").read_text().split())
    if part.exists():
        # una escena cuenta como hecha solo si quedó anotada después de escribir sus filas
        if lista.exists():
            hechas |= set(lista.read_text().split())
    else:
        with open(part, "w", encoding="utf-8", newline="") as fh:
            csv.DictWriter(fh, COLS).writeheader()
    pend = [e for e in escenas if clave(e[0])[0] not in hechas]
    log(f"{mes}{sufijo}: {len(jet)} JET, {len(escenas)} escenas con condados, {len(pend)} pendientes")
    errores = 0
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(procesar_escena, token, *e, puntos): e for e in pend}
        for n, (f, e) in enumerate(futs.items(), 1):
            try:
                filas = f.result()
            except Exception as err:  # noqa: BLE001
                errores += 1
                log(f"  error {e[0]}: {type(err).__name__}")
                continue
            with open(part, "a", encoding="utf-8", newline="") as fh:
                csv.DictWriter(fh, COLS).writerows(filas)
            with open(lista, "a", encoding="utf-8") as fh:
                fh.write(clave(e[0])[0] + "\n")
            if n % 50 == 0:
                log(f"  {mes}: {n}/{len(pend)}")
            if time.time() > limite:
                log("  límite de tiempo: corto (se retoma)")
                ex.shutdown(wait=False, cancel_futures=True)
                return False
    if errores:
        log(f"{mes}: {errores} escenas con error, queda en interim para reintentar")
        return False
    df = pd.read_csv(part, dtype=str, on_bad_lines="skip").dropna(subset=["n_px_agricolas"])
    df = df.drop_duplicates(["fips", "granulo"], keep="last")
    df.sort_values(["fecha_hora_utc", "granulo", "fips"]).to_csv(part, index=False)
    RAW.mkdir(parents=True, exist_ok=True)
    shutil.move(part, dest)
    registrar(dest, mes)
    log(f"{mes}{sufijo}: completo -> {dest.name} ({len(df)} filas)")
    return True


def registrar(p: Path, mes: str) -> None:
    asegurar_manifest(MANIFEST)
    with open(MANIFEST, encoding="utf-8", newline="") as fh:
        filas = list(csv.reader(fh))
    rel = p.relative_to(REPO).as_posix()
    cajas = "&".join(f"bounding_box[]={b}" for b in bboxes_cmr())
    nueva = ["ecostress", rel, "NASA JPL / LP DAAC (Earthdata Cloud)",
             "ECO_L2T_LSTE.002 (LST, QC, cloud) + ECO_L3T_JET.002 (ETdaily) + ECO_L4T_ESI.002 (ESI)",
             "002", date.today().isoformat(),
             f"{CMR}?short_name=ECO_L3T_JET&version=002&{cajas}&options[bounding_box][or]=true&temporal={mes} ; "
             f"COG por rango en {LPDAAC}/<producto>/<granulo>/<granulo>_<capa>.tif, ventana 32x32 px por condado"]
    filas = [f for f in filas if not (len(f) > 1 and f[1] == rel)] + [nueva]
    with open(MANIFEST, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerows(filas)


def meses_todos() -> list[str]:
    """Abril a octubre (temporada con superficie sin nieve) de 2018-08 a 2025-10, más recientes primero."""
    ms = [f"{a}-{m:02d}" for a in range(2018, 2026) for m in range(4, 11) if (a, m) >= (2018, 8)]
    return sorted(ms, reverse=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meses", default="")
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--max-minutos", type=float, default=600)
    a = ap.parse_args()
    limite = time.time() + a.max_minutos * 60
    puntos = puntos_condados()
    token = requests.post("https://urs.earthdata.nasa.gov/api/users/find_or_create_token", timeout=60).json()["access_token"]
    for mes in (a.meses.split(",") if a.meses else meses_todos()):
        if time.time() > limite:
            break
        if mes in MESES_BBOX_ESTE and (RAW / f"ecostress_extraccion_{mes}.csv").exists():
            bajar_mes(token, mes, puntos, a.workers, limite, "_oeste")
        else:
            bajar_mes(token, mes, puntos, a.workers, limite)


if __name__ == "__main__":
    main()
