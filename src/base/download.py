"""Paquete 0 — Base: baja los condados del US Census (Cartographic Boundary 1:500k).

Idempotente: si el archivo ya está en data/raw/base/ no se vuelve a bajar. Baja a
data/interim/base/*.part y mueve a raw cuando la descarga está completa. Registra cada archivo
en manifest.csv.
"""
from __future__ import annotations

import csv
import datetime as dt
import shutil
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "raw" / "base"
INTERIM = REPO / "data" / "interim" / "base"
MANIFEST = REPO / "manifest.csv"
CAMPOS = ["paquete", "archivo", "fuente", "producto", "version", "fecha_descarga", "consulta_o_url"]

ANIO_CB = 2024
URL = f"https://www2.census.gov/geo/tiger/GENZ{ANIO_CB}/shp/cb_{ANIO_CB}_us_county_500k.zip"


def registrar(archivo: Path, fuente: str, producto: str, version: str, url: str) -> None:
    rel = archivo.relative_to(REPO).as_posix()
    filas = []
    if MANIFEST.exists():
        with open(MANIFEST, encoding="utf-8", newline="") as f:
            filas = list(csv.DictReader(f))
    if any(r["archivo"] == rel for r in filas):
        return
    nuevo = not MANIFEST.exists() or MANIFEST.stat().st_size == 0
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if nuevo:
            w.writeheader()
        w.writerow({"paquete": "base", "archivo": rel, "fuente": fuente, "producto": producto,
                    "version": version, "fecha_descarga": dt.date.today().isoformat(),
                    "consulta_o_url": url})


def bajar(url: str, destino: Path) -> None:
    if destino.exists():
        print(f"ya está: {destino.relative_to(REPO)}")
        return
    INTERIM.mkdir(parents=True, exist_ok=True)
    part = INTERIM / (destino.name + ".part")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(part, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    RAW.mkdir(parents=True, exist_ok=True)
    shutil.move(str(part), str(destino))
    print(f"bajado: {destino.relative_to(REPO)}")


def main() -> int:
    destino = RAW / Path(URL).name
    bajar(URL, destino)
    registrar(destino, "US Census Bureau", "Cartographic Boundary Files - Counties 1:500,000",
              f"cb_{ANIO_CB}", URL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
