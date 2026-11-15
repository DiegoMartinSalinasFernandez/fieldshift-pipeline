"""Paquete clima — baja NASA POWER diario (comunidad AG) en el centroide de cada condado.

Idempotente y reanudable: si data/raw/clima/power/power_diario_<fips>.csv ya existe no se
vuelve a bajar. Cada descarga va a data/interim/clima/power/*.part y se mueve a raw cuando está
completa (se verifica que tenga el último día pedido). Registra cada archivo en manifest.csv.

GPM IMERG: sin credencial de Earthdata se baja IMERG_PRECTOT desde la misma API de POWER, una
consulta por celda de 0,1° (data/raw/clima/imerg_power/). `python src/clima/download.py imerg`
baja solo IMERG.
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import cargar_config  # noqa: E402
from src.clima.celdas import celda_de_nombre, celdas_imerg, nombre_celda  # noqa: E402

RAW = REPO / "data" / "raw" / "clima" / "power"
INTERIM = REPO / "data" / "interim" / "clima" / "power"
MANIFEST = REPO / "manifest.csv"
CONDADOS = REPO / "data" / "reference" / "condados.csv"

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "WS2M",
          "ALLSKY_SFC_SW_DWN", "GWETTOP", "GWETROOT", "GWETPROF"]

# Versión de la API (T123). La respuesta en CSV no la trae en el texto, pero sí en el encabezado HTTP
# `x-app-version` (p. ej. "v2.10.3"); en JSON viene en header.api.version. Ver docs/research/power_version.md.
# Si un archivo ya estaba en raw sin fila en el manifest, la versión con la que se bajó no se conoce.
VERSION_DESCONOCIDA = "v2 (API, versión no registrada)"


def version_api(r) -> str:
    """Texto de la columna `version` del manifest a partir de la respuesta HTTP de POWER."""
    v = (r.headers.get("x-app-version") or "").strip()
    return f"POWER API {v}" if v else VERSION_DESCONOCIDA


def rango_fechas():
    cfg = cargar_config()["periodo"]
    ini = pd.Timestamp(cfg["power_climatologia_desde"]).strftime("%Y%m%d")
    fin = f"{int(cfg['anio_fin'])}1231"
    return ini, fin


def consulta(lat, lon, ini, fin):
    return {"parameters": ",".join(PARAMS), "community": "AG", "longitude": f"{lon:.5f}",
            "latitude": f"{lat:.5f}", "start": ini, "end": fin, "format": "CSV"}


def bajar(fips, lat, lon, ini, fin):
    """Devuelve (fips, estado, url, version); url y version son None si no se bajó."""
    dest = RAW / f"power_diario_{fips}.csv"
    if dest.exists():
        return fips, "ya estaba", None, None
    INTERIM.mkdir(parents=True, exist_ok=True)
    part = INTERIM / f"power_diario_{fips}.csv.part"
    q = consulta(lat, lon, ini, fin)
    ultimo = f"{fin[:4]},{pd.Timestamp(fin).day_of_year},"
    for intento in range(5):
        try:
            r = requests.get(URL, params=q, timeout=180)
            if r.status_code == 429:
                time.sleep(10 * (intento + 1))
                continue
            r.raise_for_status()
            txt = r.text
            if "-END HEADER-" not in txt or ultimo not in txt:
                raise ValueError("respuesta incompleta")
            part.write_bytes(r.content)
            RAW.mkdir(parents=True, exist_ok=True)
            os.replace(part, dest)
            url = requests.Request("GET", URL, params=q).prepare().url
            return fips, "bajado", url, version_api(r)
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(3 * (intento + 1))
    return fips, f"error: {err}", None, None


def asegurar_manifest(man: Path) -> None:
    """En una máquina nueva no hay manifest.csv (no va en git): lo crea con el encabezado (CLAUDE.md §7)."""
    if not man.exists() or man.stat().st_size == 0:
        man.write_text("paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n", encoding="utf-8")


def registrar(filas):
    asegurar_manifest(MANIFEST)
    existentes = set()
    if MANIFEST.exists():
        with open(MANIFEST, encoding="utf-8", newline="") as f:
            existentes = {row["archivo"] for row in csv.DictReader(f)}
    nuevas = [f for f in filas if f[1] not in existentes]
    if not nuevas:
        return
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerows(nuevas)


def main():
    cond = pd.read_csv(CONDADOS, dtype={"fips": str})
    ini, fin = rango_fechas()
    hoy = dt.date.today().isoformat()
    filas, errores = [], []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(bajar, r.fips, r.lat_centroide, r.lon_centroide, ini, fin)
                for r in cond.itertuples()]
        for i, fu in enumerate(as_completed(futs), 1):
            fips, estado, url, version = fu.result()
            if url:
                filas.append(["clima", f"data/raw/clima/power/power_diario_{fips}.csv", "NASA POWER",
                              "POWER daily point API, community AG (" + ",".join(PARAMS) + ")",
                              version, hoy, url])
            if estado.startswith("error"):
                errores.append((fips, estado))
            print(f"[{i}/{len(futs)}] {fips} {estado}", flush=True)
            if len(filas) >= 20:
                registrar(filas)
                filas = []
    registrar(filas)
    # Archivos en raw sin fila en el manifest (p. ej. si se cortó antes de registrar)
    pend = []
    for p in sorted(RAW.glob("power_diario_*.csv")):
        fips = p.stem.split("_")[-1]
        r = cond.loc[cond.fips == fips].iloc[0]
        url = requests.Request("GET", URL, params=consulta(r.lat_centroide, r.lon_centroide, ini, fin)).prepare().url
        pend.append(["clima", p.relative_to(REPO).as_posix(), "NASA POWER",
                     "POWER daily point API, community AG (" + ",".join(PARAMS) + ")",
                     VERSION_DESCONOCIDA, dt.date.fromtimestamp(p.stat().st_mtime).isoformat(), url])
    registrar(pend)
    print(f"errores: {len(errores)} {errores[:5]}")
    bajar_imerg()


# --------------------------------------------------------------------------- IMERG vía POWER

RAW_IM = REPO / "data" / "raw" / "clima" / "imerg_power"
INTERIM_IM = REPO / "data" / "interim" / "clima" / "imerg_power"
LOG_IM = REPO / "data" / "interim" / "clima" / "imerg_power.log"
PRODUCTO_IM = ("POWER daily point API, community AG, parameter IMERG_PRECTOT (GPM IMERG, 0.1 deg native "
               "resolution, time-standard UTC)")


def consulta_imerg(lat, lon):
    cfg = cargar_config()["periodo"]
    return {"parameters": "IMERG_PRECTOT", "community": "AG", "longitude": f"{lon:.2f}",
            "latitude": f"{lat:.2f}", "start": f"{int(cfg['anio_inicio'])}0101",
            "end": f"{int(cfg['anio_fin'])}1231", "format": "CSV", "time-standard": "UTC"}


def bajar_celda(lat, lon):
    """Devuelve (destino, estado, version); version es None si no se bajó."""
    dest = RAW_IM / nombre_celda(lat, lon)
    if dest.exists():
        return dest, "ya estaba", None
    INTERIM_IM.mkdir(parents=True, exist_ok=True)
    part = INTERIM_IM / (dest.name + ".part")
    q = consulta_imerg(lat, lon)
    ultimo = f"{q['end'][:4]},{pd.Timestamp(q['end']).day_of_year},"
    err = None
    for intento in range(5):
        try:
            r = requests.get(URL, params=q, timeout=180)
            if r.status_code == 429:
                time.sleep(10 * (intento + 1))
                continue
            r.raise_for_status()
            txt = r.text
            if "-END HEADER-" not in txt or ultimo not in txt or "IMERG_PRECTOT" not in txt:
                raise ValueError("respuesta incompleta")
            part.write_bytes(r.content)
            RAW_IM.mkdir(parents=True, exist_ok=True)
            os.replace(part, dest)
            return dest, "bajado", version_api(r)
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(3 * (intento + 1))
    return dest, f"error: {err}", None


def fila_manifest_imerg(p: Path, version: str | None = None):
    lat, lon = celda_de_nombre(p.name)
    url = requests.Request("GET", URL, params=consulta_imerg(lat, lon)).prepare().url
    return ["clima", p.relative_to(REPO).as_posix(), "NASA POWER (GPM IMERG)", PRODUCTO_IM,
            version or VERSION_DESCONOCIDA, dt.date.fromtimestamp(p.stat().st_mtime).isoformat(), url]


def bajar_imerg(hilos: int = 8):
    """Una consulta por celda de 0,1° de IMERG cuyo centro cae en un condado (ver celdas.py)."""
    celdas = celdas_imerg()[["lat", "lon"]].drop_duplicates().sort_values(["lat", "lon"])
    pend = [(r.lat, r.lon) for r in celdas.itertuples() if not (RAW_IM / nombre_celda(r.lat, r.lon)).exists()]
    print(f"IMERG: {len(celdas)} celdas, {len(pend)} por bajar", flush=True)
    errores, versiones = [], {}
    LOG_IM.parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=hilos) as ex, open(LOG_IM, "a", encoding="utf-8") as log:
        futs = [ex.submit(bajar_celda, la, lo) for la, lo in pend]
        for i, fu in enumerate(as_completed(futs), 1):
            dest, estado, version = fu.result()
            if version:
                versiones[dest.name] = version
            if estado.startswith("error"):
                errores.append((dest.name, estado))
            if i % 50 == 0 or estado.startswith("error"):
                log.write(f"{dt.datetime.now():%H:%M:%S} [{i}/{len(futs)}] {dest.name} {estado}\n")
                log.flush()
                print(f"IMERG [{i}/{len(futs)}] {estado}", flush=True)
    registrar([fila_manifest_imerg(p, versiones.get(p.name)) for p in sorted(RAW_IM.glob("imerg_*.csv"))])
    print(f"IMERG errores: {len(errores)} {errores[:5]}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "imerg":
        bajar_imerg()
    else:
        main()
