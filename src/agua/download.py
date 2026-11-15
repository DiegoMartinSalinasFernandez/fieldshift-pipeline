"""Descarga del paquete agua.

GRACE-DA-DM (versión solo EE.UU., GRACEDADM_CLSM0125US_7D, 0,125°, semanal) desde el
servidor público del National Drought Mitigation Center (nasagrace.unl.edu), sin login.
Un nc4 por semana con gws_inst, rtzsm_inst y sfsm_inst (percentiles).

SMAP L4 (SPL4SMGP) diario, 9 km, desde el servicio WPS público de Crop-CASMA (USDA NASS / GMU):
GetFileByFips devuelve un GeoTIFF (EPSG:5070, m3/m3) recortado al estado.

Uso: python src/agua/download.py [--workers 8] [--producto grace|smap|todo] [--solo-manifest]
Reanudable: saltea lo que ya está en data/raw/agua/grace/; baja a .part en interim y
mueve a raw cuando está completo.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import cargar_config  # noqa: E402

BASE = "https://nasagrace.unl.edu/data/"
RAW = REPO / "data" / "raw" / "agua" / "grace"
INTERIM = REPO / "data" / "interim" / "agua" / "grace"
LOG = REPO / "data" / "interim" / "agua" / "download_grace.log"
MANIFEST = REPO / "manifest.csv"
PRODUCTO = "GRACE-DA-DM US 0.125 deg weekly drought indicators (GRACEDADM_CLSM0125US_7D)"


def semanas(anio_fin: int) -> list[str]:
    r = requests.get(BASE, timeout=60)
    r.raise_for_status()
    fechas = sorted(set(re.findall(r'/data/(\d{8})/', r.text)))
    # 2002 queda afuera: antes del inicio del contrato (2003-02-01) y los nc4 viejos pesan ~5 MB
    return [f for f in fechas if 2003 <= int(f[:4]) <= anio_fin]


def archivo_de_semana(f: str) -> str | None:
    r = requests.get(f"{BASE}{f}/", timeout=60)
    r.raise_for_status()
    m = re.findall(r'(GRACEDADM_CLSM0125US_7D\.A\d{8}\.\d{3}\.nc4)"', r.text)
    return sorted(set(m))[-1] if m else None


def bajar(f: str) -> tuple[str, str | None, str]:
    ya = list(RAW.glob(f"GRACEDADM_CLSM0125US_7D.A{f}.*.nc4"))
    if ya:
        return f, ya[0].name, "ya estaba"
    for intento in range(3):
        try:
            nombre = archivo_de_semana(f)
            if nombre is None:
                return f, None, "sin nc4 en el directorio"
            url = f"{BASE}{f}/{nombre}"
            part = INTERIM / (nombre + ".part")
            with requests.get(url, timeout=120, stream=True) as r:
                r.raise_for_status()
                with open(part, "wb") as fh:
                    for chunk in r.iter_content(1 << 16):
                        fh.write(chunk)
            esperado = int(r.headers.get("Content-Length", part.stat().st_size))
            if part.stat().st_size != esperado:
                raise IOError("tamaño incompleto")
            part.replace(RAW / nombre)
            return f, nombre, "bajado"
        except Exception as e:  # noqa: BLE001
            err = str(e)
            time.sleep(2 * (intento + 1))
    return f, None, f"error: {err}"


SMAP_WPS = "https://cloud.csiss.gmu.edu/smap_service"
SMAP_RAW = REPO / "data" / "raw" / "agua" / "smap"
SMAP_INTERIM = REPO / "data" / "interim" / "agua" / "smap"
SMAP_LOG = REPO / "data" / "interim" / "agua" / "download_smap.log"
SMAP_PRODUCTO = ("SMAP L4 SPL4SMGP 9 km, capas diarias de Crop-CASMA (USDA NASS / GMU): "
                 "SMAP-9KM-DAILY-TOP (superficie) y SMAP-9KM-DAILY-SUB (zona radicular), recorte por estado")
SMAP_INICIO = date(2015, 3, 31)


def bajar_smap(capa: str, dia: date, fips_estado: str) -> tuple[str, str]:
    layer = f"SMAP-9KM-DAILY-{capa}_{dia:%Y.%m.%d}_013000"
    nombre = f"{layer}_FIPS_{fips_estado}.tif"
    destino = SMAP_RAW / str(dia.year) / nombre
    if destino.exists():
        return nombre, "ya estaba"
    err = ""
    for intento in range(3):
        try:
            r = requests.get(SMAP_WPS, timeout=120, params={
                "service": "WPS", "version": "1.0.0", "request": "Execute", "identifier": "GetFileByFips",
                "DataInputs": f"layer={layer};fips={fips_estado}"})
            r.raise_for_status()
            m = re.search(r'dataType="string">(https://[^<]+?\.tif)<', r.text)
            if not m:
                return nombre, "sin tif: " + re.sub(r"\s+", " ", r.text)[-200:]
            g = requests.get(m.group(1), timeout=120)
            g.raise_for_status()
            if not g.content.startswith((b"II*", b"MM\x00*")):
                raise IOError("no es un GeoTIFF")
            part = SMAP_INTERIM / (nombre + ".part")
            part.write_bytes(g.content)
            destino.parent.mkdir(parents=True, exist_ok=True)
            part.replace(destino)
            return nombre, "bajado"
        except Exception as e:  # noqa: BLE001
            err = str(e)
            time.sleep(2 * (intento + 1))
    return nombre, f"error: {err}"


def main_smap(workers: int, reverso: bool = False) -> None:
    from datetime import timedelta

    from src.common.config import estados_config

    SMAP_INTERIM.mkdir(parents=True, exist_ok=True)
    anio_fin = int(cargar_config()["periodo"]["anio_fin"])
    fin = min(date(anio_fin, 12, 31), date.today() - timedelta(days=7))
    dias = [SMAP_INICIO + timedelta(days=i) for i in range((fin - SMAP_INICIO).days + 1)]
    estados = sorted(v["fips"] for v in estados_config().values())
    tareas = [(c, d, e) for d in dias for c in ("SUB", "TOP") for e in estados]
    if reverso:
        tareas = tareas[::-1]
    print(f"smap: {len(tareas)} archivos", flush=True)
    hechos = 0
    with ThreadPoolExecutor(workers) as ex, open(SMAP_LOG, "a", encoding="utf-8") as log:
        futs = [ex.submit(bajar_smap, *t) for t in tareas]
        for fu in as_completed(futs):
            nombre, estado = fu.result()
            hechos += 1
            if estado != "ya estaba":
                log.write(f"{nombre},{estado}\n")
                log.flush()
            if hechos % 500 == 0:
                print(f"{hechos}/{len(tareas)}", flush=True)


def asegurar_manifest(man: Path) -> None:
    """En una máquina nueva no hay manifest.csv (no va en git): lo crea con el encabezado (CLAUDE.md §7)."""
    if not man.exists() or man.stat().st_size == 0:
        man.write_text("paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n", encoding="utf-8")


def registrar_manifest_smap() -> None:
    asegurar_manifest(MANIFEST)
    with open(MANIFEST, encoding="utf-8", newline="") as fh:
        ya = {r[1] for r in csv.reader(fh) if len(r) > 1}
    nuevas = []
    for p in sorted(SMAP_RAW.glob("*/*.tif")):
        rel = p.relative_to(REPO).as_posix()
        if rel in ya:
            continue
        m = re.match(r"(SMAP-9KM-DAILY-\w+_[\d.]+_\d+)_FIPS_(\d+)\.tif", p.name)
        url = (f"{SMAP_WPS}?service=WPS&version=1.0.0&request=Execute&identifier=GetFileByFips"
               f"&DataInputs=layer={m.group(1)};fips={m.group(2)}")
        nuevas.append(["agua", rel, "USDA NASS / George Mason University, Crop-CASMA (datos NASA SMAP L4)",
                       SMAP_PRODUCTO, "Crop-CASMA SMAP-9KM-DAILY",
                       date.fromtimestamp(p.stat().st_mtime).isoformat(), url])
    if nuevas:
        with open(MANIFEST, "a", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerows(nuevas)
    print(f"manifest smap: {len(nuevas)} filas nuevas")


def registrar_manifest() -> None:
    asegurar_manifest(MANIFEST)
    with open(MANIFEST, encoding="utf-8", newline="") as fh:
        filas = list(csv.reader(fh))
    ya = {r[1] for r in filas[1:] if r}
    nuevas = []
    for p in sorted(RAW.glob("*.nc4")):
        rel = p.relative_to(REPO).as_posix()
        if rel in ya:
            continue
        f = re.search(r"\.A(\d{8})\.", p.name).group(1)
        ver = re.search(r"\.(\d{3})\.nc4$", p.name).group(1)
        nuevas.append(["agua", rel, "NASA GSFC / National Drought Mitigation Center (nasagrace.unl.edu)",
                       PRODUCTO, ver, date.fromtimestamp(p.stat().st_mtime).isoformat(),
                       f"{BASE}{f}/{p.name}"])
    if nuevas:
        with open(MANIFEST, "a", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerows(nuevas)
    print(f"manifest: {len(nuevas)} filas nuevas")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--producto", choices=["grace", "smap", "todo"], default="todo")
    ap.add_argument("--solo-manifest", action="store_true")
    ap.add_argument("--reverso", action="store_true", help="bajar SMAP desde la fecha más reciente")
    a = ap.parse_args()
    if a.solo_manifest:
        registrar_manifest()
        registrar_manifest_smap()
        return
    if a.producto in ("smap", "todo"):
        main_smap(a.workers, a.reverso)
        registrar_manifest_smap()
    if a.producto == "smap":
        return
    RAW.mkdir(parents=True, exist_ok=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    anio_fin = int(cargar_config()["periodo"]["anio_fin"])
    lista = semanas(anio_fin)
    print(f"{len(lista)} semanas hasta {anio_fin}")
    hechos = 0
    with ThreadPoolExecutor(a.workers) as ex, open(LOG, "a", encoding="utf-8") as log:
        futs = [ex.submit(bajar, f) for f in lista]
        for fu in as_completed(futs):
            f, nombre, estado = fu.result()
            hechos += 1
            log.write(f"{f},{nombre},{estado}\n")
            log.flush()
            if hechos % 100 == 0:
                print(f"{hechos}/{len(lista)}", flush=True)
    registrar_manifest()


if __name__ == "__main__":
    main()
