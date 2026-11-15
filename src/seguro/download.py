"""Paquete seguro — descarga de USDA RMA: Cause of Loss y Summary of Business por condado.

Baja, para cada año del período de config.yaml (2000 a 2025):
- `colsom_<AAAA>.zip` (Cause of Loss Summary of Business with Month of Loss), de
  https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/
- `sobtpu_<AAAA>.zip` (Summary of Business por condado, cultivo, plan, nivel de cobertura, tipo,
  práctica y estructura de unidad), de .../Summary_of_Business/state_county_crop/
y los diccionarios oficiales (PDF) de los dos archivos y el listado de códigos de etapa.

Los zips son nacionales (todos los estados): el filtro por estado (FIELDSHIFT_ESTADOS) y por
cultivo se hace en process.py, no acá. Si el archivo ya está en data/raw/seguro/, no se vuelve a
bajar (RMA revisa los años recientes; para tomar una revisión nueva hay que borrar el zip a mano).
Registra cada archivo en manifest.csv (la `version` es la fecha Last-Modified del servidor).

Uso: python src/seguro/download.py [--anios 2023 2024]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import sys
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import cargar_config  # noqa: E402
from src.common.manifest import asegurar_manifest  # noqa: E402

RAW = REPO / "data" / "raw" / "seguro"
INTERIM = REPO / "data" / "interim" / "seguro"
MANIFEST = REPO / "manifest.csv"

BASE = "https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business"
COL_URL = BASE + "/cause_of_loss/colsom_{anio}.zip"
SOB_URL = BASE + "/state_county_crop/sobtpu_{anio}.zip"
DOCS = {
    "COL_Summary_of_Business_with_Month_All_Years.pdf":
        (BASE + "/cause_of_loss/COL_Summary_of_Business_with_Month_All_Years.pdf",
         "Cause of Loss Summary of Business with Month of Loss - record layout"),
    "Stage_Code_Listing.pdf":
        (BASE + "/cause_of_loss/Stage_Code_Listing.pdf", "History of Stage Codes 1989 Forward"),
    "SOBTPU_External_All_Years.pdf":
        (BASE + "/state_county_crop/SOBTPU_External_All_Years.pdf",
         "Summary of Business - Type Practice Unit Structure - record layout"),
}
UA = "fieldshift-pipeline/1.0"




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


def bajar(url: str, destino: Path) -> str | None:
    """Baja url a destino (vía .part). Devuelve la fecha Last-Modified (YYYY-MM-DD) o None si falla."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=(15, 300))
    except requests.RequestException as e:
        print(f"falló {url}: {e}")
        return None
    if r.status_code != 200:
        print(f"falló {url}: HTTP {r.status_code}")
        return None
    INTERIM.mkdir(parents=True, exist_ok=True)
    part = INTERIM / (destino.name + ".part")
    part.write_bytes(r.content)
    part.replace(destino)
    print(f"bajado {destino.name} ({len(r.content) / 1e6:.1f} MB)")
    return fecha_modificacion(r.headers.get("Last-Modified"))


def fecha_modificacion(h: str | None) -> str:
    if not h:
        return ""
    try:
        return parsedate_to_datetime(h).date().isoformat()
    except (TypeError, ValueError):
        return ""


def version_remota(url: str) -> str:
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=(15, 60), allow_redirects=True)
        return fecha_modificacion(r.headers.get("Last-Modified")) if r.ok else ""
    except requests.RequestException:
        return ""


def fila(destino: Path, producto: str, url: str, version: str, hoy: str) -> dict:
    return {
        "paquete": "seguro",
        "archivo": destino.relative_to(REPO).as_posix(),
        "fuente": "USDA RMA",
        "producto": producto,
        "version": f"Last-Modified {version}" if version else "",
        "fecha_descarga": hoy,
        "consulta_o_url": url,
    }


def main() -> None:
    cfg = cargar_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("--anios", type=int, nargs="*",
                    default=list(range(int(cfg["periodo"]["anio_inicio"]), int(cfg["periodo"]["anio_fin"]) + 1)))
    args = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    hoy = dt.date.today().isoformat()
    existentes = set()
    if MANIFEST.exists():
        existentes = {r["archivo"] for r in csv.DictReader(io.StringIO(MANIFEST.read_text(encoding="utf-8")))}
    pedidos = [(n, u, p) for n, (u, p) in DOCS.items()]
    for a in args.anios:
        pedidos.append((f"colsom_{a}.zip", COL_URL.format(anio=a),
                        f"Cause of Loss Summary of Business with Month of Loss {a}"))
        pedidos.append((f"sobtpu_{a}.zip", SOB_URL.format(anio=a),
                        f"Summary of Business by Type, Practice and Unit Structure {a}"))
    filas, fallas = [], []
    for nombre, url, producto in pedidos:
        destino = RAW / nombre
        if destino.exists():
            if destino.relative_to(REPO).as_posix() not in existentes:
                filas.append(fila(destino, producto, url, version_remota(url), hoy))
            continue
        version = bajar(url, destino)
        if version is None:
            fallas.append(nombre)
            continue
        filas.append(fila(destino, producto, url, version, hoy))
    upsert_manifest(filas)
    if fallas:
        print(f"no se pudieron bajar ({len(fallas)}): {', '.join(fallas)}")


if __name__ == "__main__":
    main()
