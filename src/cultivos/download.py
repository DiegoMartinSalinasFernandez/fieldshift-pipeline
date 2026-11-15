"""Descarga de cultivos: base completa de NASS Quick Stats (sin clave) y estadísticas del CDL.

Sin NASS_API_KEY se usan los archivos de la base completa de Quick Stats
(https://www.nass.usda.gov/datasets): `qs.crops_<fecha>.txt.gz` (encuesta: rendimiento,
superficie, producción y Crop Progress) y `qs.census<anio>.txt.gz` (Censo Agropecuario).

Reanudable: baja a data/interim/cultivos/<archivo>.part con Range y lo mueve a
data/raw/cultivos/nass/ cuando el tamaño coincide con Content-Length. Si el archivo ya está
en raw no se vuelve a bajar. Registra cada archivo en manifest.csv.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
import time
from datetime import date
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.common.config import cargar_config  # noqa: E402
from src.common.manifest import asegurar_manifest  # noqa: E402

RAW = REPO / "data" / "raw" / "cultivos" / "nass"
INTERIM = REPO / "data" / "interim" / "cultivos"
MANIFEST = REPO / "manifest.csv"
BASE = "https://www.nass.usda.gov"
INDICE = BASE + "/datasets"


def archivos_a_bajar() -> list[str]:
    """Nombres de la base completa: el crops más reciente y los censos de config.yaml."""
    existentes = sorted(p.name for p in RAW.glob("qs.crops_*.txt.gz"))
    censos = [f"qs.census{a}.txt.gz" for a in cargar_config()["periodo"]["censos"]]
    if existentes:
        return [existentes[-1]] + censos
    html = requests.get(INDICE, timeout=60).text
    crops = sorted(set(re.findall(r"qs\.crops_\d{8}\.txt\.gz", html)))
    if not crops:
        raise RuntimeError("no se encontró qs.crops_<fecha>.txt.gz en " + INDICE)
    return [crops[-1]] + censos


RAW_CDL = REPO / "data" / "raw" / "cultivos" / "cdl"
CDL_BASE = BASE + "/sites/default/files/Research_and_Science/Cropland/Release/datasets/"
# Capa nacional de tierra cultivada del CDL (base de la máscara agrícola)
CDL_CULTIVADA = "2025_cultivated_layer.zip"
# Metadatos oficiales del CDL con la tabla de clases (código y nombre; las clases son nacionales)
CDL_META = "metadata_wa23.htm"
CDL_META_URL = BASE + "/sites/default/files/Research_and_Science/Cropland/metadata/" + CDL_META


def bajar(nombre: str, url: str | None = None, raw: Path = RAW) -> Path:
    destino = raw / nombre
    if destino.exists():
        print(f"ya está: {destino.relative_to(REPO)}")
        return destino
    url = url or f"{BASE}/sites/default/files/datasets/{nombre}"
    total = int(requests.head(url, timeout=60, allow_redirects=True).headers.get("Content-Length", 0))
    part = INTERIM / (nombre + ".part")
    INTERIM.mkdir(parents=True, exist_ok=True)
    while True:
        hecho = part.stat().st_size if part.exists() else 0
        if hecho >= total and (total or hecho):
            break
        headers = {"Range": f"bytes={hecho}-"}
        with requests.get(url, headers=headers, stream=True, timeout=120) as r:
            r.raise_for_status()
            modo = "ab" if r.status_code == 206 else "wb"
            with open(part, modo) as f:
                for bloque in r.iter_content(1 << 20):
                    f.write(bloque)
        print(f"{nombre}: {part.stat().st_size / 1e6:.0f} / {total / 1e6:.0f} MB", flush=True)
    raw.mkdir(parents=True, exist_ok=True)
    shutil.move(str(part), destino)
    registrar(destino, url)
    return destino


def registrar(ruta: Path, url: str) -> None:
    asegurar_manifest(MANIFEST)
    rel = ruta.relative_to(REPO).as_posix()
    with open(MANIFEST, encoding="utf-8") as f:
        if any(rel == fila.get("archivo") for fila in csv.DictReader(f)):
            return
    m = re.search(r"(\d{8}|census\d{4})", ruta.name)
    version = m.group(1) if m else ""
    if ruta.name.startswith("metadata_"):
        producto, version = "Cropland Data Layer - metadatos FGDC (tabla de clases)", "2023"
    elif "cultivated" in ruta.name:
        producto, version = "Cropland Data Layer - Cultivated Layer (nacional, 30 m)", ruta.name[:4]
    elif "crops" in ruta.name:
        producto = "Quick Stats bulk file - Crops sector (SURVEY y CENSUS)"
    else:
        producto = f"Quick Stats bulk file - Census of Agriculture {version[-4:]}"
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(["cultivos", rel, "USDA NASS", producto, version,
                                date.today().isoformat(), url])


PC_STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
PC_TOKEN = "https://planetarycomputer.microsoft.com/api/sas/v1/token/landcoverdata/usda-cdl"
RAW_TESELAS = RAW_CDL / "teselas"


def buscar_stac(cuerpo: dict) -> list[dict]:
    """Todos los items de una búsqueda STAC, siguiendo el link `next` (no depende de `limit`)."""
    items, url, cuerpo = [], PC_STAC, dict(cuerpo)
    while url:
        r = requests.post(url, json=cuerpo, timeout=120)
        r.raise_for_status()
        j = r.json()
        items += j["features"]
        nxt = [l for l in j.get("links", []) if l.get("rel") == "next"]
        url, cuerpo = (nxt[0]["href"], nxt[0].get("body", cuerpo)) if nxt else (None, cuerpo)
    return items


def teselas_cdl(anio: int, gpkg: Path | None = None) -> list[tuple[str, str]]:
    """(id, href) de las teselas `cropland` del CDL en Planetary Computer que tocan los condados.

    Una búsqueda por estado (bbox de sus condados), sin repetir teselas. El bbox solo preselecciona:
    la tesela se queda si toca algún condado, así que con un estado o con todos juntos el resultado
    es el mismo conjunto (el de antes de T023 para IA, IL e IN).
    """
    import geopandas as gpd
    from shapely.geometry import shape

    cond = gpd.read_file(gpkg or REPO / "data" / "reference" / "condados.gpkg").to_crs(4326)
    zona = cond.union_all() if hasattr(cond, "union_all") else cond.unary_union
    por_id = {}
    for _, sub in sorted(cond.groupby(cond["fips"].astype(str).str.zfill(5).str[:2])):
        cuerpo = {"collections": ["usda-cdl"], "bbox": [float(v) for v in sub.total_bounds],
                  "datetime": f"{anio}-01-01T00:00:00Z/{anio}-12-31T23:59:59Z", "limit": 500}
        for it in buscar_stac(cuerpo):
            por_id.setdefault(it["id"], it)
    out = []
    for it in por_id.values():
        a = it["assets"].get("cropland")
        if a and shape(it["geometry"]).intersects(zona):
            out.append((it["id"], a["href"]))
    return sorted(out)


def bajar_teselas_cdl(anios: list[int] | None = None) -> None:
    """CDL anual 30 m por teselas de 90 km (COG) de Planetary Computer, sin login.

    Reanudable: cada tesela es un archivo; las que ya están en raw se saltean.
    """
    RAW_TESELAS.mkdir(parents=True, exist_ok=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    token = requests.get(PC_TOKEN, timeout=60).json()["token"]
    # la colección usda-cdl de Planetary Computer llega hasta 2021
    for anio in anios or range(cargar_config()["periodo"]["rotaciones_desde"], 2022):
        try:
            teselas = teselas_cdl(anio)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR búsqueda {anio}: {e}", flush=True)
            continue
        nuevas = 0
        for _id, href in teselas:
            destino = RAW_TESELAS / href.rsplit("/", 1)[1]
            if destino.exists():
                continue
            part = INTERIM / (destino.name + ".part")
            try:
                r = requests.get(f"{href}?{token}", timeout=180)
                if r.status_code == 403:  # token vencido
                    token = requests.get(PC_TOKEN, timeout=60).json()["token"]
                    r = requests.get(f"{href}?{token}", timeout=180)
                r.raise_for_status()
                part.write_bytes(r.content)
                shutil.move(str(part), destino)
                registrar_tesela(destino, href)
                nuevas += 1
            except Exception as e:  # noqa: BLE001
                print(f"ERROR {destino.name}: {e}", flush=True)
        print(f"CDL {anio}: {len(teselas)} teselas, {nuevas} nuevas", flush=True)


def registrar_tesela(ruta: Path, href: str) -> None:
    asegurar_manifest(MANIFEST)
    rel = ruta.relative_to(REPO).as_posix()
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(["cultivos", rel, "USDA NASS (vía Microsoft Planetary Computer)",
                                "Cropland Data Layer 30 m (colección usda-cdl, tesela cropland)",
                                ruta.name[:4], date.today().isoformat(), href])


# CroplandCROS (USDA NASS / ARS SCINet): ImageServer con los CDL nacionales 1997-2025, sin login.
CROS = "https://pdi.scinet.usda.gov/image/rest/services/CDL_WM/ImageServer"
LADO_TESELA = 90000


def rasters_cros() -> dict[int, tuple[int, str]]:
    """{anio: (OBJECTID, nombre)} de los CDL nacionales del ImageServer de CroplandCROS."""
    r = requests.get(CROS + "/query", params={"where": "1=1", "outFields": "OBJECTID,Name,Year",
                                              "returnGeometry": "false", "f": "json"}, timeout=120)
    r.raise_for_status()
    return {f["attributes"]["Year"]: (f["attributes"]["OBJECTID"], f["attributes"]["Name"])
            for f in r.json()["features"]}


def bajar_teselas_cros(anios: list[int] | None = None) -> None:
    """CDL 2022-2025 (Planetary Computer llega a 2021) recortado en la misma grilla de teselas.

    `exportImage` del ImageServer en EPSG:5070, 30 m, vecino más cercano, un raster fijo por año
    (lockRaster) y TIFF LZW. Mismo nombre que las teselas de Planetary Computer para que
    process.py las lea igual. Reanudable: las que ya están en raw se saltean.
    """
    asegurar_manifest(MANIFEST)
    INTERIM.mkdir(parents=True, exist_ok=True)
    claves = sorted({"_".join(p.stem.split("_")[3:]) for p in RAW_TESELAS.glob("2021_30m_cdls_*.tif")})
    rasters = rasters_cros()
    for anio in anios or [2022, 2023, 2024, 2025]:
        if anio not in rasters:
            print(f"CROS sin CDL {anio}", flush=True)
            continue
        oid, nombre = rasters[anio]
        nuevas = 0
        for clave in claves:
            destino = RAW_TESELAS / f"{anio}_30m_cdls_{clave}.tif"
            if destino.exists():
                continue
            x, y, lado = (int(v) for v in clave.split("_"))
            top = y + 30
            params = {"bbox": f"{x},{top - lado},{x + lado},{top}", "bboxSR": 5070,
                      "imageSR": 5070, "size": f"{lado // 30},{lado // 30}", "format": "tiff",
                      "pixelType": "U8", "interpolation": "RSP_NearestNeighbor",
                      "compression": "LZ77",
                      "mosaicRule": json.dumps({"mosaicMethod": "esriMosaicLockRaster",
                                                "lockRasterIds": [oid]}),
                      "f": "image"}
            url = requests.Request("GET", CROS + "/exportImage", params=params).prepare().url
            part = INTERIM / (destino.name + ".part")
            try:
                for intento in range(3):
                    r = requests.get(url, timeout=300)
                    if r.ok and r.headers.get("Content-Type", "").startswith("image/tiff"):
                        break
                    time.sleep(5 * (intento + 1))
                else:
                    raise RuntimeError(f"HTTP {r.status_code} {r.headers.get('Content-Type')}")
                part.write_bytes(r.content)
                shutil.move(str(part), destino)
                with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
                    csv.writer(f).writerow(["cultivos", destino.relative_to(REPO).as_posix(),
                                            "USDA NASS (vía CroplandCROS, ImageServer de USDA ARS SCINet)",
                                            f"Cropland Data Layer ({nombre}) exportado a 30 m",
                                            str(anio), date.today().isoformat(), url])
                nuevas += 1
            except Exception as e:  # noqa: BLE001
                print(f"ERROR {destino.name}: {e}", flush=True)
        print(f"CDL CROS {anio}: {len(claves)} teselas, {nuevas} nuevas", flush=True)


def main() -> None:
    for nombre in archivos_a_bajar():
        try:
            bajar(nombre)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR {nombre}: {e}", flush=True)
    try:
        bajar(CDL_CULTIVADA, CDL_BASE + CDL_CULTIVADA, RAW_CDL)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR {CDL_CULTIVADA}: {e}", flush=True)
    try:
        bajar(CDL_META, CDL_META_URL, RAW_CDL)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR {CDL_META}: {e}", flush=True)
    # archivos en raw sin fila en el manifest (corte entre mover y registrar)
    for p in RAW.glob("qs.*.txt.gz"):
        registrar(p, f"{BASE}/sites/default/files/datasets/{p.name}")
    asegurar_manifest(MANIFEST)
    with open(MANIFEST, encoding="utf-8") as f:
        en_manifest = {fila["archivo"] for fila in csv.DictReader(f)}
    for p in sorted(RAW_TESELAS.glob("*.tif")):
        if p.relative_to(REPO).as_posix() not in en_manifest:
            carpeta = p.name.split("_")[3]
            registrar_tesela(p, f"https://landcoverdata.blob.core.windows.net/usda-cdl/tiles/{carpeta}/{p.name}")
    bajar_teselas_cdl()
    bajar_teselas_cros()


if __name__ == "__main__":
    main()
