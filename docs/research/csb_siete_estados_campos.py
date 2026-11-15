"""Lee, sin bajar los zip, los campos de cada ventana publicada del CSB de NASS.

GDAL lee por HTTP (rangos) solo el directorio del zip y la cabecera de la tabla de la file geodatabase, así
que cada ventana cuesta unos pocos MB y no los 3,5-4,6 GB del zip. También mide el tamaño de cada zip con un
HEAD. Escribe un CSV en la salida estándar: ventana, bytes_zip, capa, n_poligonos, campos (nombre:tipo).

Uso: .venv/bin/python -I docs/research/csb_siete_estados_campos.py > /tmp/csb_campos.csv
"""
import csv
import os
import struct
import sys
from concurrent.futures import ThreadPoolExecutor

os.environ.setdefault("GDAL_HTTP_USERAGENT", "Mozilla/5.0")
import pyogrio  # noqa: E402
import requests  # noqa: E402

BASE = ("https://www.nass.usda.gov/sites/default/files/Research_and_Science/Crop-Sequence-Boundaries/"
        "datasets/NationalCSB_{v}_rev23.zip")
VENTANAS = [f"{a}-{a + 7}" for a in range(2008, 2019)]
UA = {"User-Agent": "Mozilla/5.0"}


def gdb_en_zip(url: str, total: int) -> str:
    """Nombre de la carpeta .gdb, leyendo el directorio central del zip (ZIP64) con rangos."""
    cola = requests.get(url, headers={**UA, "Range": f"bytes={total - 65536}-{total - 1}"}, timeout=60).content
    i = cola.rfind(b"PK\x06\x06")  # registro de fin de directorio ZIP64
    if i >= 0:
        tam_dir, ini_dir = struct.unpack("<QQ", cola[i + 40:i + 56])
    else:
        i = cola.rfind(b"PK\x05\x06")
        tam_dir, ini_dir = struct.unpack("<II", cola[i + 12:i + 20])
    fin = min(ini_dir + tam_dir, ini_dir + 200_000) - 1
    d = requests.get(url, headers={**UA, "Range": f"bytes={ini_dir}-{fin}"}, timeout=60).content
    # recorre las entradas del directorio central (cabecera fija de 46 bytes + nombre + extra + comentario)
    p = 0
    while d[p:p + 4] == b"PK\x01\x02" and p + 46 <= len(d):
        n, e, c = struct.unpack("<HHH", d[p + 28:p + 34])
        nombre = d[p + 46:p + 46 + n].decode("latin1")
        if ".gdb/" in nombre:
            return nombre[:nombre.index(".gdb/") + 4]
        p += 46 + n + e + c
    raise ValueError("no hay .gdb en el zip")


def ventana(v: str) -> list:
    try:
        return _ventana(v)
    except Exception as e:  # se registra y se sigue con las demás
        return [v, "", "", "", f"ERROR: {type(e).__name__}: {e}"]


def _ventana(v: str) -> list:
    url = BASE.format(v=v)
    total = int(requests.head(url, headers=UA, timeout=60).headers["Content-Length"])
    gdb = gdb_en_zip(url, total)
    ruta = f"/vsizip//vsicurl/{url}/{gdb}"
    capas = pyogrio.list_layers(ruta)
    capa = str(capas[0][0])
    info = pyogrio.read_info(ruta, layer=capa)
    campos = ";".join(f"{n}:{t}" for n, t in zip(info["fields"], info["dtypes"]))
    return [v, total, f"{gdb}/{capa}", info["features"], campos]


if __name__ == "__main__":
    w = csv.writer(sys.stdout)
    w.writerow(["ventana", "bytes_zip", "capa", "n_poligonos", "campos"])
    with ThreadPoolExecutor(4) as ex:
        for fila in ex.map(ventana, VENTANAS):
            w.writerow(fila)
            sys.stdout.flush()
