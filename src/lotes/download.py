"""Descargas del paquete lotes (CLAUDE.md §6.6).

Paso 1 (CSB): el CSB nacional 2018-2025 de NASS es una file geodatabase de 3,76 GB dentro de un zip
(no hay archivos por estado). Se baja a data/interim/lotes/csb/ con pedidos por rangos en paralelo
(reanudable: cada trozo es un .part que se renombra al terminar), y de ahí se extraen con GDAL los
polígonos de los condados candidatos a data/raw/lotes/csb/ (filtro espacial en origen, como la ruta
GeoParquet que sugiere el plan). El zip completo no entra en raw: es una caché regenerable.

Uso: python src/lotes/download.py [csb]
"""
from __future__ import annotations

import concurrent.futures as cf
import csv
import datetime as dt
import os
import sys
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[2]
INTERIM = RAIZ / "data" / "interim" / "lotes"
RAW = RAIZ / "data" / "raw" / "lotes"
MANIFEST = RAIZ / "manifest.csv"

CSB_VENTANA = "2018-2025"
CSB_URL = ("https://www.nass.usda.gov/sites/default/files/Research_and_Science/Crop-Sequence-Boundaries/"
           f"datasets/NationalCSB_{CSB_VENTANA}_rev23.zip")
CSB_ZIP = INTERIM / "csb" / f"NationalCSB_{CSB_VENTANA}_rev23.zip"
CSB_CAPA = "CSB1825.gdb"
TROZO = 64 * 1024 * 1024

# Condados candidatos por paisaje (CLAUDE.md §6.6). Indiana: Tippecanoe (18157), llanura de till
# del centro-norte con maíz-soja y poco riego; elegido a mano y documentado en el data card.
CONDADOS = ["19169", "19079", "19197", "19047", "19165", "17019", "18157"]


def log(msg: str) -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    linea = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(linea, flush=True)
    with open(INTERIM / "download.log", "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def asegurar_manifest(man: Path) -> None:
    """En una máquina nueva no hay manifest.csv (no va en git): lo crea con el encabezado (CLAUDE.md §7)."""
    if not man.exists() or man.stat().st_size == 0:
        man.write_text("paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n", encoding="utf-8")


def upsert_manifest(filas: list[dict]) -> None:
    asegurar_manifest(MANIFEST)
    campos = ["paquete", "archivo", "fuente", "producto", "version", "fecha_descarga", "consulta_o_url"]
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        actuales = list(csv.DictReader(f))
    por_archivo = {r["archivo"]: r for r in actuales}
    orden = [r["archivo"] for r in actuales]
    for fila in filas:
        if fila["archivo"] not in por_archivo:
            orden.append(fila["archivo"])
        else:
            fila = {**fila, "fecha_descarga": por_archivo[fila["archivo"]]["fecha_descarga"]}
        por_archivo[fila["archivo"]] = fila
    with open(MANIFEST, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        w.writeheader()
        for a in orden:
            w.writerow({k: por_archivo[a].get(k, "") for k in campos})


def _bajar_trozo(i: int, ini: int, fin: int, dir_trozos: Path) -> Path:
    destino = dir_trozos / f"{i:04d}.bin"
    if destino.exists() and destino.stat().st_size == fin - ini + 1:
        return destino
    part = destino.with_suffix(".part")
    for intento in range(5):
        try:
            r = requests.get(CSB_URL, headers={"Range": f"bytes={ini}-{fin}"}, timeout=120, stream=True)
            r.raise_for_status()
            with open(part, "wb") as f:
                for b in r.iter_content(1 << 20):
                    f.write(b)
            if part.stat().st_size == fin - ini + 1:
                os.replace(part, destino)
                return destino
        except requests.RequestException as e:
            log(f"trozo {i} intento {intento}: {e}")
    raise RuntimeError(f"no se pudo bajar el trozo {i}")


def bajar_zip_csb(n_hilos: int = 12) -> Path:
    if CSB_ZIP.exists():
        return CSB_ZIP
    total = int(requests.head(CSB_URL, timeout=60).headers["Content-Length"])
    dir_trozos = CSB_ZIP.parent / "trozos"
    dir_trozos.mkdir(parents=True, exist_ok=True)
    rangos = [(i, a, min(a + TROZO, total) - 1) for i, a in enumerate(range(0, total, TROZO))]
    log(f"CSB {CSB_VENTANA}: {total} bytes en {len(rangos)} trozos")
    hechos = 0
    with cf.ThreadPoolExecutor(n_hilos) as ex:
        for _ in cf.as_completed([ex.submit(_bajar_trozo, i, a, b, dir_trozos) for i, a, b in rangos]):
            hechos += 1
            if hechos % 5 == 0:
                log(f"CSB trozos {hechos}/{len(rangos)}")
    part = CSB_ZIP.with_suffix(".zip.part")
    with open(part, "wb") as f:
        for i, _, _ in rangos:
            f.write((dir_trozos / f"{i:04d}.bin").read_bytes())
    os.replace(part, CSB_ZIP)
    for p in dir_trozos.glob("*.bin"):
        p.unlink()
    log("CSB zip completo")
    return CSB_ZIP


def extraer_csb_condados() -> None:
    """Polígonos del CSB de cada condado candidato, tal como vienen (todas las columnas, EPSG:5070)."""
    import pyogrio

    import zipfile

    import geopandas as gpd

    destino_dir = RAW / "csb"
    destino_dir.mkdir(parents=True, exist_ok=True)
    gdb = INTERIM / "csb" / CSB_CAPA
    faltan = [f for f in CONDADOS if not (destino_dir / f"csb_{CSB_VENTANA}_{f}.gpkg").exists()]
    if faltan and not (gdb / "a00000010.spx").exists():
        # descomprimir la gdb (5,3 GB) para usar su índice espacial (.spx) en vez de recorrer el zip entero
        with zipfile.ZipFile(CSB_ZIP) as z:
            for n in z.namelist():
                if n.startswith(CSB_CAPA + "/"):
                    z.extract(n, INTERIM / "csb")
        log("CSB gdb descomprimida")
    condados = gpd.read_file(RAIZ / "data" / "reference" / "condados.gpkg").to_crs(5070)
    condados["fips"] = condados["fips"].astype(str).str.zfill(5)
    filas = []
    for fips in CONDADOS:
        destino = destino_dir / f"csb_{CSB_VENTANA}_{fips}.gpkg"
        consulta = f"STATEFIPS = '{fips[:2]}' AND CNTYFIPS = '{fips[2:]}'"
        if not destino.exists():
            caja = tuple(condados.loc[condados["fips"] == fips].total_bounds)
            df = pyogrio.read_dataframe(gdb, bbox=caja)
            df = df[(df["STATEFIPS"].astype(str).str.zfill(2) == fips[:2])
                    & (df["CNTYFIPS"].astype(str).str.zfill(3) == fips[2:])]
            tmp = INTERIM / "csb" / destino.name
            if tmp.exists():
                tmp.unlink()
            pyogrio.write_dataframe(df, tmp, layer="csb", driver="GPKG")
            os.replace(tmp, destino)
            log(f"CSB {fips}: {len(df)} polígonos")
        filas.append({
            "paquete": "lotes", "archivo": destino.relative_to(RAIZ).as_posix(), "fuente": "USDA NASS",
            "producto": "Crop Sequence Boundaries (CSB)", "version": f"{CSB_VENTANA} rev23",
            "fecha_descarga": dt.date.today().isoformat(),
            "consulta_o_url": f"{CSB_URL} -> {CSB_CAPA} where {consulta}",
        })
    upsert_manifest(filas)


CROS = "https://pdi.scinet.usda.gov/image/rest/services/CDL_WM/ImageServer"


def bajar_cdl_10m(anios=(2024, 2025)) -> None:
    """CDL nativo de 10 m de la ventana de cada lote (recuadro alineado con los bordes de la grilla de 30 m,
    más 30 m de margen), por exportImage del ImageServer de CroplandCROS, vecino más cercano a 10 m."""
    import json
    import math

    import geopandas as gpd
    import pandas as pd

    lotes = pd.read_csv(RAIZ / "data" / "processed" / "lotes" / "lotes.csv", dtype={"fips": str, "csbid": str})
    r = requests.get(CROS + "/query", params={"where": "1=1", "outFields": "OBJECTID,Name,Year",
                                              "returnGeometry": "false", "f": "json"}, timeout=120)
    r.raise_for_status()
    rasters = [f["attributes"] for f in r.json()["features"]]
    destino_dir = RAW / "cdl10m"
    destino_dir.mkdir(parents=True, exist_ok=True)
    filas = []
    for fips, s in lotes.groupby("fips"):
        csb = gpd.read_file(RAW / "csb" / f"csb_{CSB_VENTANA}_{fips}.gpkg").to_crs(5070)
        for _, l in s.iterrows():
            x0, y0, x1, y1 = csb.loc[csb["CSBID"] == l["csbid"]].total_bounds
            x0 = math.floor((x0 - 15) / 30) * 30 + 15 - 30
            y0 = math.floor((y0 - 15) / 30) * 30 + 15 - 30
            x1 = math.ceil((x1 - 15) / 30) * 30 + 15 + 30
            y1 = math.ceil((y1 - 15) / 30) * 30 + 15 + 30
            for anio in anios:
                cand = [a for a in rasters if a["Year"] == anio and "10m" in str(a["Name"])]
                if not cand:
                    log(f"CROS sin CDL 10 m {anio}")
                    continue
                oid = cand[0]["OBJECTID"]
                destino = destino_dir / f"cdl10m_{anio}_{l['id_lote']}.tif"
                params = {"bbox": f"{x0},{y0},{x1},{y1}", "bboxSR": 5070, "imageSR": 5070,
                          "size": f"{int((x1 - x0) / 10)},{int((y1 - y0) / 10)}", "format": "tiff",
                          "pixelType": "U8", "interpolation": "RSP_NearestNeighbor", "compression": "LZ77",
                          "mosaicRule": json.dumps({"mosaicMethod": "esriMosaicLockRaster", "lockRasterIds": [oid]}),
                          "f": "image"}
                url = requests.Request("GET", CROS + "/exportImage", params=params).prepare().url
                if not destino.exists():
                    rr = requests.get(url, timeout=300)
                    if not (rr.ok and rr.headers.get("Content-Type", "").startswith("image/tiff")):
                        log(f"CDL 10 m {anio} {l['id_lote']}: HTTP {rr.status_code}")
                        continue
                    part = INTERIM / "cdl10m" / (destino.name + ".part")
                    part.parent.mkdir(parents=True, exist_ok=True)
                    part.write_bytes(rr.content)
                    os.replace(part, destino)
                    log(f"CDL 10 m {anio} {l['id_lote']}: {len(rr.content)} bytes")
                filas.append({"paquete": "lotes", "archivo": destino.relative_to(RAIZ).as_posix(),
                              "fuente": "USDA NASS (CroplandCROS ImageServer)",
                              "producto": f"Cropland Data Layer 10 m {anio}", "version": str(cand[0]["Name"]),
                              "fecha_descarga": dt.date.today().isoformat(), "consulta_o_url": url})
    upsert_manifest(filas)


TNM_3DEP = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer"
MARGEN_3DEP_M = 2520  # >= 2 km para el TWI; múltiplo de 30 para mantener la alineación con la grilla


def bajar_3dep() -> None:
    """USGS 3DEP (mosaico dinámico bare earth: lidar 1 m donde hay, si no 1/3") a 10 m en EPSG:5070, recuadro del
    lote alineado con los bordes de la grilla de 30 m (múltiplos de 30 m + 15) más 2.520 m de margen, bilineal."""
    import math

    import geopandas as gpd
    import pandas as pd

    lotes = pd.read_csv(RAIZ / "data" / "processed" / "lotes" / "lotes.csv", dtype={"fips": str, "csbid": str})
    destino_dir = RAW / "3dep"
    destino_dir.mkdir(parents=True, exist_ok=True)
    filas = []
    for fips, s in lotes.groupby("fips"):
        csb = gpd.read_file(RAW / "csb" / f"csb_{CSB_VENTANA}_{fips}.gpkg").to_crs(5070)
        for _, l in s.iterrows():
            x0, y0, x1, y1 = csb.loc[csb["CSBID"] == l["csbid"]].total_bounds
            x0 = math.floor((x0 - 15) / 30) * 30 + 15 - MARGEN_3DEP_M
            y0 = math.floor((y0 - 15) / 30) * 30 + 15 - MARGEN_3DEP_M
            x1 = math.ceil((x1 - 15) / 30) * 30 + 15 + MARGEN_3DEP_M
            y1 = math.ceil((y1 - 15) / 30) * 30 + 15 + MARGEN_3DEP_M
            destino = destino_dir / f"3dep_10m_{l['id_lote']}.tif"
            params = {"bbox": f"{x0},{y0},{x1},{y1}", "bboxSR": 5070, "imageSR": 5070,
                      "size": f"{int((x1 - x0) / 10)},{int((y1 - y0) / 10)}", "format": "tiff", "pixelType": "F32",
                      "interpolation": "RSP_BilinearInterpolation", "f": "image"}
            url = requests.Request("GET", TNM_3DEP + "/exportImage", params=params).prepare().url
            if not destino.exists():
                rr = requests.get(url, timeout=300)
                if not (rr.ok and rr.headers.get("Content-Type", "").startswith("image/tiff")):
                    log(f"3DEP {l['id_lote']}: HTTP {rr.status_code} {rr.headers.get('Content-Type')}")
                    continue
                part = INTERIM / "3dep" / (destino.name + ".part")
                part.parent.mkdir(parents=True, exist_ok=True)
                part.write_bytes(rr.content)
                os.replace(part, destino)
                log(f"3DEP {l['id_lote']}: {len(rr.content)} bytes")
            filas.append({"paquete": "lotes", "archivo": destino.relative_to(RAIZ).as_posix(),
                          "fuente": "USGS The National Map (3DEPElevation ImageServer)",
                          "producto": "3DEP bare earth DEM (lidar 1 m o 1/3 arcsec), exportado a 10 m",
                          "version": "datos publicados al 2026-10-26",
                          "fecha_descarga": dt.date.today().isoformat(), "consulta_o_url": url})
    upsert_manifest(filas)


AGTILE_URL = "https://ndownloader.figshare.com/files/23079140"
AGTILE_BYTES = 125793805


def bajar_agtile() -> None:
    """AgTile-US (Valayamkunnath et al. 2020, Scientific Data 7:257), mapa CONUS de 30 m de drenaje con caños,
    figshare 10.6084/m9.figshare.11825742 (CC BY 4.0), versión GeoTIFF zipeada."""
    destino = RAW / "agtile" / "AgTile-US-TIFF.zip"
    if not destino.exists():
        part = INTERIM / "agtile" / (destino.name + ".part")
        part.parent.mkdir(parents=True, exist_ok=True)
        if not (part.exists() and part.stat().st_size == AGTILE_BYTES):
            with requests.get(AGTILE_URL, stream=True, timeout=600) as r:
                r.raise_for_status()
                with open(part, "wb") as f:
                    for trozo in r.iter_content(1 << 20):
                        f.write(trozo)
        if part.stat().st_size != AGTILE_BYTES:
            log(f"AgTile-US: tamaño {part.stat().st_size} != {AGTILE_BYTES}")
            return
        destino.parent.mkdir(parents=True, exist_ok=True)
        os.replace(part, destino)
        log(f"AgTile-US: {AGTILE_BYTES} bytes")
    upsert_manifest([{"paquete": "lotes", "archivo": destino.relative_to(RAIZ).as_posix(),
                      "fuente": "Valayamkunnath et al. 2020 (figshare)", "producto": "AgTile-US 30 m (GeoTIFF)",
                      "version": "v1 (10.6084/m9.figshare.11825742.v1)",
                      "fecha_descarga": dt.date.today().isoformat(), "consulta_o_url": AGTILE_URL}])


def main(pasos: list[str]) -> None:
    if not pasos or "drenaje" in pasos:
        bajar_agtile()
        if pasos == ["drenaje"]:
            return
    if not pasos or "csb" in pasos:
        bajar_zip_csb()
        extraer_csb_condados()
    if not pasos or "cdl10" in pasos:
        bajar_cdl_10m()
    if not pasos or "3dep" in pasos:
        bajar_3dep()
        if pasos == ["3dep"]:
            return
    import threading
    import landsat
    if "ssurgo" in pasos or not pasos:
        import ssurgo
        ssurgo.bajar(upsert_manifest)
    lock = threading.Lock()

    def upsert(filas):
        with lock:
            upsert_manifest(filas)
    if "clima" in pasos or not pasos:
        import clima
        clima.bajar(upsert_manifest)
    if "manifest" in pasos:
        for prod in ("landsat", "hls_s30"):
            landsat.registrar(prod, upsert)
        return
    hilos = [threading.Thread(target=landsat.bajar, args=(prod, upsert)) for prod, paso in
             (("landsat", "landsat"), ("hls_s30", "hls")) if not pasos or paso in pasos]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()


if __name__ == "__main__":
    main(sys.argv[1:])
