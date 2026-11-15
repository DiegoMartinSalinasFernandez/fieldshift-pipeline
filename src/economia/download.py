"""Paquete economia — descarga de USDA ERS Commodity Costs and Returns.

Baja los CSV por cultivo (maíz, soja, trigo, avena) de la página de ERS a
data/raw/economia/ers/. Los links se leen del HTML de la página (llevan un `?v=` que cambia
con cada versión). Baja también `reglink.xls`, la tabla oficial de ERS que asigna cada condado
(FIPS) a una Farm Resource Region. Si el archivo ya está en raw, no se vuelve a bajar.
Registra cada archivo en manifest.csv.

Los precios recibidos de NASS no se bajan: process.py los lee del volcado de Quick Stats
que ya bajó el paquete cultivos (data/raw/cultivos/nass/qs.crops_*.txt.gz).

Uso: python src/economia/download.py
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import re
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "raw" / "economia" / "ers"
INTERIM = REPO / "data" / "interim" / "economia"
MANIFEST = REPO / "manifest.csv"

PAGINA = "https://www.ers.usda.gov/data-products/commodity-costs-and-returns"
BASE = "https://www.ers.usda.gov"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0 Safari/537.36")
# nombre del CSV en la página de ERS -> producto
CSVS = {
    "corn.csv": "Commodity Costs and Returns - Corn",
    "soybeans.csv": "Commodity Costs and Returns - Soybeans",
    "wheat.csv": "Commodity Costs and Returns - Wheat",
    "oats.csv": "Commodity Costs and Returns - Oats",
}
# tabla condado -> Farm Resource Region (enlazada desde la documentación de Commodity Costs and Returns)
REGLINK = "reglink.xls"
REGLINK_URL = BASE + "/sites/default/files/images/reglink.xls"
REGLINK_DOC = PAGINA + "/documentation"


def links_pagina() -> dict[str, str]:
    r = requests.get(PAGINA, headers={"User-Agent": UA}, timeout=(15, 60))
    r.raise_for_status()
    out = {}
    for href in re.findall(r'href="(/media/\d+/[^"]+\.csv[^"]*)"', r.text):
        nombre = href.split("?")[0].rsplit("/", 1)[-1]
        if nombre in CSVS:
            out[nombre] = BASE + href.replace("&amp;", "&")
    return out


def asegurar_manifest(man: Path) -> None:
    """En una máquina nueva no hay manifest.csv (no va en git): lo crea con el encabezado (CLAUDE.md §7)."""
    if not man.exists() or man.stat().st_size == 0:
        man.write_text("paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n", encoding="utf-8")


def upsert_manifest(filas: list[dict]) -> None:
    """Agrega filas nuevas al final; las existentes (por archivo) quedan como estaban."""
    asegurar_manifest(MANIFEST)
    data = MANIFEST.read_bytes()
    eol = b"\r\n" if b"\r\n" in data[:2000] else b"\n"
    existentes = {r["archivo"] for r in csv.DictReader(io.StringIO(data.decode("utf-8")))}
    nuevas = [f for f in filas if f["archivo"] not in existentes]
    if not nuevas:
        return
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["paquete", "archivo", "fuente", "producto", "version",
                                        "fecha_descarga", "consulta_o_url"],
                       lineterminator=eol.decode())
    for f in nuevas:
        w.writerow(f)
    if not data.endswith(eol):
        data += eol
    MANIFEST.write_bytes(data + buf.getvalue().encode("utf-8"))


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    hoy = dt.date.today().isoformat()
    faltan = [n for n in CSVS if not (RAW / n).exists()]
    links = links_pagina() if faltan else {}
    filas = []
    for nombre, producto in CSVS.items():
        destino = RAW / nombre
        url = links.get(nombre)
        if not destino.exists():
            if not url:
                print(f"no se encontró el link de {nombre} en {PAGINA}")
                continue
            r = requests.get(url, headers={"User-Agent": UA}, timeout=(15, 120))
            r.raise_for_status()
            part = INTERIM / (nombre + ".part")
            part.write_bytes(r.content)
            part.replace(destino)
            print(f"bajado {nombre} ({len(r.content)} bytes)")
        version = re.search(r"\?v=(\d+)", url).group(1) if url and "?v=" in url else ""
        filas.append({
            "paquete": "economia",
            "archivo": destino.relative_to(REPO).as_posix(),
            "fuente": "USDA ERS",
            "producto": producto,
            "version": f"v={version}" if version else "",
            "fecha_descarga": hoy,
            "consulta_o_url": url or PAGINA,
        })
    destino = RAW / REGLINK
    if not destino.exists():
        r = requests.get(REGLINK_URL, headers={"User-Agent": UA}, timeout=(15, 120))
        r.raise_for_status()
        part = INTERIM / (REGLINK + ".part")
        part.write_bytes(r.content)
        part.replace(destino)
        print(f"bajado {REGLINK} ({len(r.content)} bytes)")
    filas.append({
        "paquete": "economia",
        "archivo": destino.relative_to(REPO).as_posix(),
        "fuente": "USDA ERS",
        "producto": "Farm Resource Regions - county to region link (reglink)",
        "version": "",
        "fecha_descarga": hoy,
        "consulta_o_url": REGLINK_URL,
    })
    upsert_manifest(filas)


if __name__ == "__main__":
    main()
