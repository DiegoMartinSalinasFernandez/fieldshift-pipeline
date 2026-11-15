"""Descarga PRISM mensual 4 km (ppt, tmax, tmin, tmean) y CoCoRaHS diario por estado.

PRISM: directorio HTTP público de Oregon State (data.prism.oregonstate.edu/time_series), un zip
por variable y mes. Reanudable: baja a data/interim/validacion/ como .part y mueve a raw al final.
CoCoRaHS: export público de reportes diarios por estado y mes (data.cocorahs.org).

Uso: python src/validacion/download.py [prism|cocorahs|manifest]
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
import yaml

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "validacion"
INTERIM = RAIZ / "data" / "interim" / "validacion"
LOG = INTERIM / "download.log"
sys.path.insert(0, str(RAIZ))
from src.common.config import cargar_config  # noqa: E402  (filtra por FIELDSHIFT_ESTADOS)

CFG = cargar_config()

PRISM_BASE = "https://data.prism.oregonstate.edu/time_series/us/an/4km/{var}/monthly/{y}/prism_{var}_us_25m_{y}{m:02d}.zip"
PRISM_VARS = ["ppt", "tmax", "tmin", "tmean"]
COCO_URL = ("https://data.cocorahs.org/export/exportreports.aspx?ReportType=Daily&dtf=1&Format=CSV"
            "&State={st}&ReportDateType=reportdate&StartDate={ini}&EndDate={fin}")


def log(msg: str) -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")


def periodo() -> tuple[int, int]:
    p = CFG["periodo"]
    return int(p["anio_inicio"]), int(p["anio_fin"])


def bajar(url: str, destino: Path, timeout: int = 120) -> bool:
    if destino.exists():
        return True
    part = INTERIM / "part" / (destino.name + ".part")
    part.parent.mkdir(parents=True, exist_ok=True)
    for intento in range(2):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200 and len(r.content) > 0:
                part.write_bytes(r.content)
                destino.parent.mkdir(parents=True, exist_ok=True)
                os.replace(part, destino)
                log(f"ok {destino.name} {len(r.content)}")
                return True
            log(f"http {r.status_code} {url}")
            if r.status_code < 500:
                return False
        except requests.RequestException as e:
            log(f"error {url} {type(e).__name__}")
        time.sleep(5)
    return False


def tareas_prism() -> list[tuple[str, Path]]:
    ini, fin = periodo()
    out = []
    for y in range(fin, ini - 1, -1):
        for m in range(1, 13):
            for v in PRISM_VARS:
                url = PRISM_BASE.format(var=v, y=y, m=m)
                out.append((url, RAW / "prism" / v / f"prism_{v}_us_25m_{y}{m:02d}.zip"))
    return out


def tareas_cocorahs() -> list[tuple[str, Path]]:
    ini, fin = periodo()
    out = []
    for st in CFG["zona"]["estados"]:
        for y in range(max(ini, 2008), fin + 1):
            for m in range(1, 13):
                a = dt.date(y, m, 1)
                b = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1))
                url = COCO_URL.format(st=st, ini=f"{a.month}/{a.day}/{a.year}", fin=f"{b.month}/{b.day}/{b.year}")
                out.append((url, RAW / "cocorahs" / st / f"cocorahs_daily_{st}_{y}{m:02d}.csv"))
    return out


def correr(tareas, hilos: int) -> None:
    pend = [t for t in tareas if not t[1].exists()]
    log(f"inicio {len(pend)} pendientes de {len(tareas)}")
    with ThreadPoolExecutor(hilos) as ex:
        list(ex.map(lambda t: bajar(*t), pend))
    log("fin")


def manifest() -> None:
    """Upsert por archivo en manifest.csv (conserva filas y fin de línea existentes)."""
    mpath = RAIZ / "manifest.csv"
    texto = mpath.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in texto else "\n"
    existentes = {row["archivo"] for row in csv.DictReader(texto.splitlines())}
    nuevas = []
    hoy = dt.date.today().isoformat()
    for url, p in tareas_prism():
        rel = p.relative_to(RAIZ).as_posix()
        if p.exists() and rel not in existentes:
            v = p.parent.name
            nuevas.append(["validacion", rel, "PRISM Climate Group, Oregon State University",
                           f"PRISM {v} mensual 4 km (AN81m/AN91m)", "time_series us an 4km 25m", hoy, url])
    for url, p in tareas_cocorahs():
        rel = p.relative_to(RAIZ).as_posix()
        if p.exists() and rel not in existentes:
            nuevas.append(["validacion", rel, "CoCoRaHS", "Daily precipitation reports (export)", "export CSV",
                           hoy, url])
    if not nuevas:
        return
    import io
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator=eol)
    w.writerows(nuevas)
    if not texto.endswith(("\n", "\r")):
        texto += eol
    mpath.write_bytes((texto + buf.getvalue()).encode("utf-8"))
    print(f"manifest: {len(nuevas)} filas nuevas")


if __name__ == "__main__":
    que = sys.argv[1] if len(sys.argv) > 1 else "todo"
    if que in ("prism", "todo"):
        correr(tareas_prism(), 3)
    if que in ("cocorahs", "todo"):
        correr(tareas_cocorahs(), 2)
    manifest()
