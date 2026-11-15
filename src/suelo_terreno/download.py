"""Descarga de suelo_terreno: tablas de SSURGO por Soil Data Access (SDA, USDA NRCS, sin login).

Por cada estado de config.yaml y cada tabla se arma una consulta SQL al servicio REST de SDA
(https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest), filtrando por las áreas de
relevamiento del estado (`legend.areasymbol`, casi siempre una por condado: IA169 = 19169; las
excepciones, solo en MN, están en `AREAS_ESPECIALES` de process.py).
Para no pasar el límite de filas de SDA se consulta en tandas de áreas y se concatena.

Tablas (una por estado, en data/raw/suelo_terreno/sda/<tabla>_<estado>.csv):
- mapunit:  areasymbol, mukey, muacres + muaggatt (aws0100wta, aws0150wta, drclassdcd,
            hydgrpdcd, wtdepannmin)
- component: mukey, cokey, comppct_r, majcompflag
- chorizon: cokey, profundidades, arena/limo/arcilla, om_r, ph1to1h2o_r, kwfact,
            dbthirdbar_r y volumen de fragmentos (suma de chfrags.fragvol_r)
- restricciones: cokey, reskind, resdept_r (corestrictions)
- nccpi: cokey, rulename, interphr (cointerp, NCCPI ver. 3.0 general, maíz y soja)

Idempotente: si el archivo ya está en raw no se vuelve a bajar. Escribe en interim (.part)
y mueve a raw al terminar. Registra cada archivo en manifest.csv.
"""
from __future__ import annotations

import csv
import shutil
import sys
import time
import urllib.parse
from datetime import date
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.common.config import estados_config  # noqa: E402

RAW = REPO / "data" / "raw" / "suelo_terreno" / "sda"
INTERIM = REPO / "data" / "interim" / "suelo_terreno"
MANIFEST = REPO / "manifest.csv"
URL = "https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest"
TANDA = 10  # áreas de relevamiento por consulta

JOIN = ("INNER JOIN mapunit m ON m.mukey = c.mukey "
        "INNER JOIN legend l ON l.lkey = m.lkey ")

CONSULTAS = {
    "mapunit": (
        "SELECT l.areasymbol, m.mukey, m.muacres, a.aws0100wta, a.aws0150wta, a.drclassdcd, "
        "a.hydgrpdcd, a.wtdepannmin FROM mapunit m INNER JOIN legend l ON l.lkey = m.lkey "
        "LEFT JOIN muaggatt a ON a.mukey = m.mukey WHERE l.areasymbol IN ({areas})"
    ),
    "component": (
        "SELECT c.mukey, c.cokey, c.comppct_r, c.majcompflag FROM component c " + JOIN +
        "WHERE l.areasymbol IN ({areas})"
    ),
    "chorizon": (
        "SELECT h.cokey, h.chkey, h.hzdept_r, h.hzdepb_r, h.sandtotal_r, h.silttotal_r, "
        "h.claytotal_r, h.om_r, h.ph1to1h2o_r, h.kwfact, h.dbthirdbar_r, "
        "(SELECT SUM(f.fragvol_r) FROM chfrags f WHERE f.chkey = h.chkey) AS fragvol_r "
        "FROM chorizon h INNER JOIN component c ON c.cokey = h.cokey " + JOIN +
        "WHERE l.areasymbol IN ({areas})"
    ),
    "restricciones": (
        "SELECT r.cokey, r.reskind, r.resdept_r FROM corestrictions r "
        "INNER JOIN component c ON c.cokey = r.cokey " + JOIN +
        "WHERE l.areasymbol IN ({areas})"
    ),
    "nccpi": (
        "SELECT i.cokey, i.rulename, i.interphr FROM cointerp i "
        "INNER JOIN component c ON c.cokey = i.cokey " + JOIN +
        "WHERE l.areasymbol IN ({areas}) "
        "AND i.mrulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)' "
        "AND i.rulename IN ('NCCPI - National Commodity Crop Productivity Index (Ver 3.0)', "
        "'NCCPI - NCCPI Corn Submodel (I)', 'NCCPI - NCCPI Soybeans Submodel (I)')"
    ),
}


def sda(sql: str) -> list[list]:
    for intento in range(4):
        try:
            r = requests.post(URL, data={"query": sql, "format": "JSON+COLUMNNAME"}, timeout=600)
            r.raise_for_status()
            return r.json().get("Table", [])
        except Exception as e:  # noqa: BLE001
            print(f"  reintento {intento + 1}: {str(e)[:120]}", flush=True)
            time.sleep(5 * (intento + 1))
    raise RuntimeError("SDA no respondió")


def areas_estado(alfa: str) -> list[str]:
    t = sda(f"SELECT areasymbol FROM legend WHERE areasymbol LIKE '{alfa}%' ORDER BY areasymbol")
    return [f[0] for f in t[1:]]


def asegurar_manifest(man: Path) -> None:
    """En una máquina nueva no hay manifest.csv (no va en git): lo crea con el encabezado (CLAUDE.md §7)."""
    if not man.exists() or man.stat().st_size == 0:
        man.write_text("paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n", encoding="utf-8")


def registrar(archivo: Path, tabla: str, alfa: str) -> None:
    asegurar_manifest(MANIFEST)
    rel = archivo.relative_to(REPO).as_posix()
    with open(MANIFEST, encoding="utf-8") as f:
        if any(rel in linea for linea in f):
            return
    consulta = URL + "?query=" + urllib.parse.quote(CONSULTAS[tabla].format(areas=f"<areasymbol LIKE '{alfa}%'>"))
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(["suelo_terreno", rel, "USDA NRCS Soil Data Access",
                                f"SSURGO ({tabla})", "SDA (SSURGO vigente)",
                                date.today().isoformat(), consulta])


def bajar(alfa: str, tabla: str) -> None:
    destino = RAW / f"{tabla}_{alfa}.csv"
    if destino.exists():
        registrar(destino, tabla, alfa)
        return
    areas = areas_estado(alfa)
    part = INTERIM / f"{tabla}_{alfa}.csv.part"
    encabezado = None
    with open(part, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for i in range(0, len(areas), TANDA):
            lista = ",".join(f"'{a}'" for a in areas[i:i + TANDA])
            t = sda(CONSULTAS[tabla].format(areas=lista))
            if not t:
                continue
            if encabezado is None:
                encabezado = t[0]
                w.writerow(encabezado)
            w.writerows(t[1:])
            print(f"{tabla} {alfa} {i + TANDA}/{len(areas)}", flush=True)
    shutil.move(part, destino)
    registrar(destino, tabla, alfa)


RAW_DEM = REPO / "data" / "raw" / "suelo_terreno" / "nasadem"
PC_TOKEN = "https://planetarycomputer.microsoft.com/api/sas/v1/token/nasadem"
PC_BLOB = "https://nasademeuwest.blob.core.windows.net/nasadem-cog/v001/NASADEM_HGT_{tesela}.tif"


def teselas_nasadem() -> list[str]:
    """Teselas de 1° x 1° de NASADEM que tocan algún condado de condados.gpkg."""
    import math

    import geopandas as gpd
    from shapely.geometry import box

    condados = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg").to_crs(4326)
    union = condados.union_all()
    xmin, ymin, xmax, ymax = union.bounds
    teselas = []
    for lat in range(math.floor(ymin), math.ceil(ymax)):
        for lon in range(math.floor(xmin), math.ceil(xmax)):
            if union.intersects(box(lon, lat, lon + 1, lat + 1)):
                ns = f"n{lat:02d}" if lat >= 0 else f"s{-lat:02d}"
                ew = f"w{-lon:03d}" if lon < 0 else f"e{lon:03d}"
                teselas.append(ns + ew)
    return teselas


def registrar_dem(archivo: Path, tesela: str) -> None:
    asegurar_manifest(MANIFEST)
    rel = archivo.relative_to(REPO).as_posix()
    with open(MANIFEST, encoding="utf-8") as f:
        if any(rel in linea for linea in f):
            return
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(["suelo_terreno", rel, "NASA (Microsoft Planetary Computer)",
                                "NASADEM HGT 1 arc-second (COG)", "v001",
                                date.today().isoformat(), PC_BLOB.format(tesela=tesela)])


def bajar_tesela(tesela: str, token: str) -> bool:
    destino = RAW_DEM / f"NASADEM_HGT_{tesela}.tif"
    if destino.exists():
        return True
    part = INTERIM / f"NASADEM_HGT_{tesela}.tif.part"
    r = requests.get(PC_BLOB.format(tesela=tesela) + "?" + token, timeout=600)
    if r.status_code == 404:
        print(f"{tesela}: no existe", flush=True)
        return False
    r.raise_for_status()
    part.write_bytes(r.content)
    shutil.move(part, destino)
    print(f"{tesela}: {len(r.content) / 1e6:.1f} MB", flush=True)
    return True


def bajar_nasadem() -> None:
    from concurrent.futures import ThreadPoolExecutor

    RAW_DEM.mkdir(parents=True, exist_ok=True)
    teselas = teselas_nasadem()
    token = requests.get(PC_TOKEN, timeout=60).json()["token"]
    with ThreadPoolExecutor(8) as ex:
        ok = list(ex.map(lambda t: bajar_tesela(t, token), teselas))
    for tesela, bien in zip(teselas, ok):
        if bien:
            registrar_dem(RAW_DEM / f"NASADEM_HGT_{tesela}.tif", tesela)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    tablas = sys.argv[1:] or list(CONSULTAS) + ["nasadem"]
    for tabla in tablas:
        if tabla == "nasadem":
            bajar_nasadem()
            continue
        for alfa in estados_config():
            bajar(alfa, tabla)


if __name__ == "__main__":
    main()
