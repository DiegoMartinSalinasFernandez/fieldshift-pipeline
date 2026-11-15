"""Análogos climáticos Argentina ↔ Corn Belt: descarga.

- Departamentos de Argentina con su código INDEC y centroide, de la API Georef del Estado argentino
  (apis.datos.gob.ar). Quedan en data/raw/analogos/georef_departamentos.json.
- NASA POWER mensual (comunidad AG) en el centroide de cada departamento y de cada condado del Corn Belt
  (data/reference/condados_cornbelt_9.csv). Es la misma fuente y el mismo período en los dos lados.
  Va un JSON por punto en data/raw/analogos/power/<id>.json. Si el archivo ya está, no se vuelve a bajar.

Cada archivo bajado suma una fila a manifest.csv.

Uso: python src/analogos/download.py
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "analogos"
POWER_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
GEOREF_URL = "https://apis.datos.gob.ar/georef/api/departamentos"
PARAMS = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN,RH2M"
INICIO, FIN = 2001, 2024  # años completos en POWER mensual
MANIFEST = RAIZ / "manifest.csv"
CAMPOS = ["paquete", "archivo", "fuente", "producto", "version", "fecha_descarga", "consulta_o_url"]


def manifest(filas: list[list[str]]) -> None:
    nuevo = not MANIFEST.exists()
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if nuevo:
            w.writerow(CAMPOS)
        w.writerows(filas)


def georef() -> list[dict]:
    p = RAW / "georef_departamentos.json"
    if not p.exists():
        q = {"max": 5000, "campos": "id,nombre,provincia.id,provincia.nombre,centroide"}
        r = requests.get(GEOREF_URL, params=q, timeout=120)
        r.raise_for_status()
        RAW.mkdir(parents=True, exist_ok=True)
        p.write_text(r.text, encoding="utf-8")
        manifest([["analogos", p.relative_to(RAIZ).as_posix(), "Georef (datos.gob.ar)", "departamentos", "API v2",
                    dt.date.today().isoformat(), r.url]])
    return json.loads(p.read_text(encoding="utf-8"))["departamentos"]


def bajar_punto(pid: str, lat: float, lon: float) -> list[str] | None:
    p = RAW / "power" / f"{pid}.json"
    if p.exists():
        return None
    q = {"parameters": PARAMS, "community": "AG", "latitude": round(lat, 4), "longitude": round(lon, 4),
         "start": INICIO, "end": FIN, "format": "JSON"}
    for intento in range(5):
        try:
            r = requests.get(POWER_URL, params=q, timeout=180)
            if r.status_code == 200:
                j = r.json()
                p.write_text(json.dumps(j), encoding="utf-8")
                version = j.get("header", {}).get("api", {}).get("version", "")
                return ["analogos", p.relative_to(RAIZ).as_posix(), "NASA POWER", "monthly point (AG)", version,
                        dt.date.today().isoformat(), r.url]
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(10 * (intento + 1))
                continue
            print(f"{pid}: HTTP {r.status_code}", file=sys.stderr)
            return None
        except requests.RequestException as e:
            print(f"{pid}: {e}", file=sys.stderr)
            time.sleep(10 * (intento + 1))
    print(f"{pid}: falló después de 5 intentos", file=sys.stderr)
    return None


def main() -> int:
    (RAW / "power").mkdir(parents=True, exist_ok=True)
    puntos = [(f"ar_{d['id']}", d["centroide"]["lat"], d["centroide"]["lon"]) for d in georef()]
    with open(RAIZ / "data" / "reference" / "condados_cornbelt_9.csv", encoding="utf-8", newline="") as f:
        puntos += [(f"us_{r['fips']}", float(r["lat_centroide"]), float(r["lon_centroide"])) for r in csv.DictReader(f)]
    print(f"{len(puntos)} puntos")
    filas, hechos = [], 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for fila in ex.map(lambda t: bajar_punto(*t), puntos):
            hechos += 1
            if fila:
                filas.append(fila)
            if len(filas) >= 50:
                manifest(filas)
                filas = []
            if hechos % 100 == 0:
                print(f"  {hechos}/{len(puntos)}", flush=True)
    manifest(filas)
    faltan = [pid for pid, _, _ in puntos if not (RAW / "power" / f"{pid}.json").exists()]
    print(f"listo; faltan {len(faltan)}: {faltan[:10]}")
    return 1 if faltan else 0


if __name__ == "__main__":
    sys.exit(main())
