"""Paquete seguro — descarga de USDA FSA Crop Acreage Data (siembra prevenida por condado).

Baja el archivo **final** de cada año (2009–2025) de la página de FSA "Crop Acreage Data"
(docs/research/siembra_prevenida.md, T032) a data/raw/seguro/fsa/. Cada zip trae un .xlsx nacional
(unos 20 MB) con la hoja por condado; el filtro por estado se hace en fsa_process.py.

Los nombres de los archivos no siguen un patrón: las URLs van fijas en FINALES, copiadas de la
página el 2026-11-15. Algunos enlaces de la página (/documents/<id>) devuelven un HTML que apunta
al zip real: `resolver()` lo sigue. Si el zip ya está en raw/, no se vuelve a bajar. Una fila por
archivo en manifest.csv, con la fecha de corte ("as of ...") en `version`.

Los años 2007 y 2008 solo tienen resúmenes por estado: no se bajan.

Uso: python src/seguro/fsa_download.py [--anios 2019 2025]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import re
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import cargar_config  # noqa: E402
from src.common.manifest import asegurar_manifest  # noqa: E402

RAW = REPO / "data" / "raw" / "seguro" / "fsa"
INTERIM = REPO / "data" / "interim" / "seguro"
MANIFEST = REPO / "manifest.csv"
PAGINA = ("https://www.fsa.usda.gov/tools/informational/freedom-information-act-foia/"
          "electronic-reading-room/frequently-requested/crop-acreage-data")
SITIO = "https://www.fsa.usda.gov"
UA = "fieldshift-pipeline/1.0"
PRIMER_ANIO = 2009  # antes solo hay resúmenes por estado

# año -> (ruta en el sitio de FSA, texto del enlace con la fecha de corte). Archivo final de cada
# año según la página (consultada 2026-11-15).
FINALES = {
    2009: ("/sites/default/files/documents/2009_fsa_acres_detail_final_7.zip", "2009 by crop by county"),
    2010: ("/sites/default/files/documents/2010_fsa_acres_detail_final_5.zip", "2010 by crop by county"),
    2011: ("/sites/default/files/documents/2011_fsa_acres_detail_jan2012.zip",
           "2011 by crop by county as of Jan 2012 FINAL"),
    2012: ("/sites/default/files/documents/2012_fsa_acres_jan_2013.zip", "as of January 2013"),
    2013: ("/sites/default/files/documents/2013_fsa_acres_jan_2014.zip", "as of January 2014"),
    2014: ("/sites/default/files/documents/2014_fsa_acres_Jan2014.zip", "as of January 2015"),
    2015: ("/sites/default/files/documents/2015_fsa_acres_Jan2016_sq19.zip", "as of January 1, 2016"),
    2016: ("/sites/default/files/documents/2016_fsa_acres_jan2017_edr32.zip", "as of January 1, 2017"),
    2017: ("/sites/default/files/documents/2017_fsa_acres_jan2018.zip", "as of January 16, 2018"),
    2018: ("/sites/default/files/documents/2018_fsa_acres_Jan-2019-kgcr.zip", "as of January 28, 2019"),
    2019: ("/sites/default/files/documents/2019_fsa_acres_jan2020_stlno1.zip", "as of January 1, 2020"),
    2020: ("/sites/default/files/documents/2020_fsa_acres_as_of_010521-BbO60I.zip", "as of January 5, 2021"),
    2021: ("/sites/default/files/documents/2021_fsa_acres_web_as_of_010322.zip", "as of January 3, 2022"),
    2022: ("/sites/default/files/documents/vc8Jn1nR42.zip", "as of January 3, 2023"),
    2023: ("/sites/default/files/documents/3QPVeIgPizDl.zip", "as of January 2, 2024"),
    2024: ("/documents/FnNg0ix5oKdi", "as of January 2, 2025"),
    2025: ("/documents/doisjehvqfz9zip", "as of January 12, 2026"),
}




def upsert_manifest(filas: list[dict], man: Path = MANIFEST) -> None:
    """Agrega filas nuevas al final; las existentes (por archivo) quedan como estaban."""
    asegurar_manifest(man)
    data = man.read_bytes()
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
    man.write_bytes(data + buf.getvalue().encode("utf-8"))


def enlace_zip(html: str) -> str | None:
    """Del HTML intermedio de /documents/<id>, el enlace al zip real (o None)."""
    m = re.search(r'href="([^"]+\.zip)"', html, flags=re.IGNORECASE)
    if not m:
        return None
    u = m.group(1)
    return u if u.startswith("http") else SITIO + u


def resolver(ruta: str) -> str | None:
    """URL directa del zip. Las rutas /documents/<id> pasan por una página HTML intermedia."""
    url = SITIO + ruta
    if re.search(r"\.zip$", ruta, flags=re.IGNORECASE):
        return url
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=(15, 60))
    except requests.RequestException as e:
        print(f"falló {url}: {e}")
        return None
    if r.status_code != 200:
        print(f"falló {url}: HTTP {r.status_code}")
        return None
    if r.content[:2] == b"PK":  # ya es el zip
        return url
    return enlace_zip(r.text)


def bajar(url: str, destino: Path) -> bool:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=(15, 600))
    except requests.RequestException as e:
        print(f"falló {url}: {e}")
        return False
    if r.status_code != 200 or r.content[:2] != b"PK":
        print(f"falló {url}: HTTP {r.status_code}, {len(r.content)} bytes, no es un zip")
        return False
    INTERIM.mkdir(parents=True, exist_ok=True)
    part = INTERIM / (destino.name + ".part")
    part.write_bytes(r.content)
    part.replace(destino)
    print(f"bajado {destino.name} ({len(r.content) / 1e6:.1f} MB)")
    return True


def fila(destino: Path, anio: int, corte: str, url: str, hoy: str) -> dict:
    return {
        "paquete": "seguro",
        "archivo": destino.relative_to(REPO).as_posix(),
        "fuente": "USDA FSA",
        "producto": f"Crop Acreage Data {anio} (archivo final, por condado)",
        "version": corte,
        "fecha_descarga": hoy,
        "consulta_o_url": url,
    }


def main() -> None:
    cfg = cargar_config()
    a0 = max(PRIMER_ANIO, int(cfg["periodo"]["anio_inicio"]))
    a1 = int(cfg["periodo"]["anio_fin"])
    ap = argparse.ArgumentParser()
    ap.add_argument("--anios", type=int, nargs="*", default=list(range(a0, a1 + 1)))
    args = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    hoy = dt.date.today().isoformat()
    filas, fallas = [], []
    for a in args.anios:
        if a not in FINALES:
            print(f"{a}: sin archivo final por condado en FINALES (ver {PAGINA})")
            fallas.append(str(a))
            continue
        ruta, corte = FINALES[a]
        destino = RAW / f"fsa_acres_{a}_final.zip"
        if destino.exists():
            filas.append(fila(destino, a, corte, SITIO + ruta, hoy))
            continue
        url = resolver(ruta)
        if url is None or not bajar(url, destino):
            fallas.append(str(a))
            continue
        filas.append(fila(destino, a, corte, url, hoy))
    upsert_manifest(filas)
    if fallas:
        print(f"no se pudieron bajar ({len(fallas)}): {', '.join(fallas)}")


if __name__ == "__main__":
    main()
