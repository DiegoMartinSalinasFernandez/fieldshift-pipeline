"""SEETileDrain (Wan, Kendall, Rapp y Hyndman 2024) por píxel de los lotes (T131, para_decidir #5).

Fuente: HydroShare, recurso 4c8af0c89d2b4686808bcf9c6f7c0da3 (CC BY 4.0), `SEETileDrain_maps.zip`
(3.119.442.255 bytes). Adentro hay dos GeoTIFF en EPSG:4326 (celda de 0,000269495°, ~30 m, la grilla
de exportación de Google Earth Engine), 93.431 × 41.466 celdas, en tiras de una fila **sin compresión
interna**; el zip los comprime con deflate:

- `SEETileDrain_maps/probability_tile_mosaic.tif`: probabilidad de drenaje con caños (float, 0-1),
  3,06 GB comprimido y ~15,5 GB descomprimido.
- `SEETileDrain_maps/SEETileDrain.tif`: clase publicada (int32, 0/1), 58 MB comprimido y ~15,5 GB
  descomprimido.

Un miembro deflate no admite acceso aleatorio: para recortar hay que inflarlo desde el principio. Este
módulo lo infla **en flujo** (desde el zip local o pidiendo rangos HTTP al zip remoto), se queda solo con
las filas que cubren el recuadro de cada lote y corta antes de la última fila necesaria. Nunca escribe
el TIFF entero: las filas útiles van a un archivo disperso del mismo tamaño lógico que el TIFF (no ocupa
disco) y de ahí rasterio corta cada recuadro a `data/raw/lotes/seetiledrain/<capa>_<id_lote>.tif`, en la
grilla original y sin remuestrear.

`process.py` toma, para cada píxel de 30 m del lote (EPSG:5070), la celda SEETileDrain que contiene su
centro (vecino más cercano, como con AgTile-US).
"""
from __future__ import annotations

import datetime as dt
import struct
import tempfile
import zlib
from pathlib import Path
from typing import Callable, Iterable, Iterator

import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.windows import Window

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "lotes" / "seetiledrain"
INTERIM = RAIZ / "data" / "interim" / "lotes" / "seetiledrain"

URL = ("https://www.hydroshare.org/resource/4c8af0c89d2b4686808bcf9c6f7c0da3/data/contents/"
       "SEETileDrain_maps/SEETileDrain_maps.zip")
BYTES = 3119442255
MD5 = "0200fe57a8540d89118dbfc935a65bc9"  # checksum que publica la API de archivos de HydroShare
ZIP = RAW / "SEETileDrain_maps.zip"
DOI = "10.4211/hs.4c8af0c89d2b4686808bcf9c6f7c0da3"

# capa -> miembro del zip
CAPAS = {
    "prob": "SEETileDrain_maps/probability_tile_mosaic.tif",
    "clase": "SEETileDrain_maps/SEETileDrain.tif",
}
MARGEN_GRADOS = 0.0015  # ~5 celdas alrededor del recuadro del lote
COLUMNAS = {"prob": "tile_prob_seetiledrain", "clase": "tile_seetiledrain"}

Rangos = Callable[[int, int], Iterator[bytes]]  # (inicio, fin inclusive) -> trozos de bytes


# ----------------------------------------------------------------------------------------------- fuentes de bytes

def rangos_local(ruta: Path, trozo: int = 8 << 20) -> Rangos:
    def leer(ini: int, fin: int) -> Iterator[bytes]:
        with open(ruta, "rb") as f:
            f.seek(ini)
            quedan = fin - ini + 1
            while quedan > 0:
                b = f.read(min(trozo, quedan))
                if not b:
                    return
                quedan -= len(b)
                yield b
    return leer


def rangos_http(url: str = URL, trozo: int = 8 << 20) -> Rangos:
    import requests

    def leer(ini: int, fin: int) -> Iterator[bytes]:
        # HydroShare redirige a una URL firmada de Google Cloud Storage (vence en 1 h): se resuelve en cada pedido
        with requests.get(url, headers={"Range": f"bytes={ini}-{fin}"}, stream=True, timeout=120) as r:
            if r.status_code != 206:
                raise RuntimeError(f"SEETileDrain: el servidor no respetó el rango ({r.status_code})")
            yield from r.iter_content(trozo)
    return leer


def _juntar(it: Iterable[bytes]) -> bytes:
    return b"".join(it)


# ----------------------------------------------------------------------------------------------- zip

def miembros_zip(leer: Rangos, tamanio: int) -> dict[str, tuple[int, int, int]]:
    """Directorio central del zip: nombre -> (método, bytes comprimidos, offset del encabezado local)."""
    cola = _juntar(leer(max(0, tamanio - 65536), tamanio - 1))
    i = cola.rfind(b"PK\x05\x06")
    if i < 0:
        raise ValueError("no encuentro el fin del directorio central del zip")
    _, _, _, _, _, cd_tam, cd_off, _ = struct.unpack("<4s4H2LH", cola[i:i + 22])
    j = cola.rfind(b"PK\x06\x06")
    if j >= 0:  # zip64
        cd_tam, cd_off = struct.unpack("<2Q", cola[j + 40:j + 56])
    cd = _juntar(leer(cd_off, cd_off + cd_tam - 1))
    out, p = {}, 0
    while cd[p:p + 4] == b"PK\x01\x02":
        (_, _, _, _, met, _, _, _, comp, desc, nl, el, cl, _, _, _, off) = struct.unpack("<4s6H3L5H2L", cd[p:p + 46])
        nombre = cd[p + 46:p + 46 + nl].decode("utf-8")
        extra = cd[p + 46 + nl:p + 46 + nl + el]
        # campos zip64 (0x0001): en orden, los que valen 0xFFFFFFFF
        k = 0
        while k + 4 <= len(extra):
            hid, hl = struct.unpack("<2H", extra[k:k + 4])
            if hid == 1:
                vals = list(struct.unpack(f"<{hl // 8}Q", extra[k + 4:k + 4 + (hl // 8) * 8]))
                if desc == 0xFFFFFFFF:
                    desc = vals.pop(0)
                if comp == 0xFFFFFFFF:
                    comp = vals.pop(0)
                if off == 0xFFFFFFFF:
                    off = vals.pop(0)
            k += 4 + hl
        out[nombre] = (met, comp, off)
        p += 46 + nl + el + cl
    return out


def flujo_miembro(leer: Rangos, met: int, comp: int, off: int) -> Iterator[bytes]:
    """Bytes descomprimidos de un miembro del zip, en orden."""
    enc = _juntar(leer(off, off + 29))
    if enc[:4] != b"PK\x03\x04":
        raise ValueError("encabezado local del zip inválido")
    nl, el = struct.unpack("<2H", enc[26:30])
    ini = off + 30 + nl + el
    trozos = leer(ini, ini + comp - 1)
    if met == 0:
        yield from trozos
        return
    if met != 8:
        raise ValueError(f"método de compresión {met} no soportado")
    d = zlib.decompressobj(-15)
    for c in trozos:
        b = d.decompress(c)
        if b:
            yield b
    b = d.flush()
    if b:
        yield b


# ----------------------------------------------------------------------------------------------- TIFF

def tiras_tiff(cab: bytes) -> tuple[np.ndarray, np.ndarray]:
    """Offsets y largos de las tiras de un TIFF o BigTIFF little-endian, desde los primeros bytes del archivo."""
    if cab[:2] != b"II":
        raise ValueError("solo TIFF little-endian")
    ver = struct.unpack("<H", cab[2:4])[0]
    big = ver == 43
    ifd = struct.unpack("<Q", cab[8:16])[0] if big else struct.unpack("<L", cab[4:8])[0]
    n = struct.unpack("<Q" if big else "<H", cab[ifd:ifd + (8 if big else 2)])[0]
    p = ifd + (8 if big else 2)
    tam = {3: 2, 4: 4, 16: 8}
    fmt = {3: "H", 4: "L", 16: "Q"}
    tags = {}
    for _ in range(n):
        if big:
            t, typ, c = struct.unpack("<HHQ", cab[p:p + 12])
            val, p_sig, ancho = cab[p + 12:p + 20], p + 20, 8
        else:
            t, typ, c = struct.unpack("<HHL", cab[p:p + 8])
            val, p_sig, ancho = cab[p + 8:p + 12], p + 12, 4
        if t in (273, 279, 259):
            nb = tam[typ] * c
            datos = val[:nb] if nb <= ancho else cab[struct.unpack("<Q" if big else "<L", val)[0]:][:nb]
            if len(datos) < nb:
                raise ValueError("la cabecera del TIFF no entra en los bytes leídos")
            tags[t] = np.frombuffer(datos, dtype=f"<{fmt[typ]}" if typ != 16 else "<u8").astype(np.int64)
        p = p_sig
    if int(tags.get(259, [1])[0]) != 1:
        raise ValueError("el TIFF tiene compresión interna: este recorte en flujo no sirve")
    return tags[273], tags[279]


def _filas_necesarias(ds_transform, alto: int, recuadros: dict[str, tuple[float, float, float, float]]) -> dict[str, Window]:
    from rasterio.windows import from_bounds
    out = {}
    for k, (x0, y0, x1, y1) in recuadros.items():
        w = from_bounds(x0 - MARGEN_GRADOS, y0 - MARGEN_GRADOS, x1 + MARGEN_GRADOS, y1 + MARGEN_GRADOS, ds_transform)
        w = w.round_offsets("floor").round_lengths("ceil")
        out[k] = w
    return out


def recortar_miembro(leer: Rangos, tamanio_zip: int, miembro: str,
                     recuadros: dict[str, tuple[float, float, float, float]], destino: Callable[[str], Path],
                     cabecera_max: int = 4 << 20) -> dict[str, Path]:
    """Infla `miembro` en flujo y escribe un GeoTIFF por recuadro (lon/lat EPSG:4326) en `destino(clave)`.

    Para apenas pasa la última fila que necesita. Devuelve clave -> ruta escrita."""
    met, comp, off = miembros_zip(leer, tamanio_zip)[miembro]
    flujo = flujo_miembro(leer, met, comp, off)
    with tempfile.TemporaryDirectory(dir=INTERIM if INTERIM.exists() else None) as tmp:
        disperso = Path(tmp) / "miembro.tif"
        cab = bytearray()
        pos = 0
        resto = b""
        for b in flujo:
            cab += b
            pos += len(b)
            if len(cab) >= cabecera_max:
                break
        offs, largos = tiras_tiff(bytes(cab))
        h0 = int(offs.min())
        fin_tiff = int((offs + largos).max())
        with open(disperso, "wb") as f:
            f.write(bytes(cab[:h0]))
            f.truncate(fin_tiff)  # archivo disperso: el resto no ocupa disco
        # georreferencia desde la cabecera (rasterio lee solo el IFD)
        with rasterio.open(disperso) as ds:
            ventanas = _filas_necesarias(ds.transform, ds.height, recuadros)
            alto = ds.height
        ventanas = {k: w for k, w in ventanas.items() if w.row_off < alto and w.row_off + w.height > 0}
        if not ventanas:
            return {}
        fila_ini = max(0, min(int(w.row_off) for w in ventanas.values()))
        fila_fin = min(alto - 1, max(int(w.row_off + w.height) - 1 for w in ventanas.values()))
        ini_b, fin_b = int(offs[fila_ini]), int(offs[fila_fin] + largos[fila_fin])
        # bytes ya inflados en la cabecera + el resto del flujo, escritos solo dentro de [ini_b, fin_b)
        with open(disperso, "r+b") as f:
            def escribir(bloque: bytes, inicio: int) -> None:
                a, z = max(inicio, ini_b), min(inicio + len(bloque), fin_b)
                if a < z:
                    f.seek(a)
                    f.write(bloque[a - inicio:z - inicio])
            escribir(bytes(cab), 0)
            pos = len(cab)
            if pos < fin_b:
                for b in flujo:
                    escribir(b, pos)
                    pos += len(b)
                    if pos >= fin_b:
                        break
        flujo.close()
        if pos < fin_b:
            raise RuntimeError(f"{miembro}: el flujo terminó antes de la fila {fila_fin}")
        escritos = {}
        with rasterio.open(disperso) as ds:
            for k, w in ventanas.items():
                w = w.intersection(Window(0, 0, ds.width, ds.height))
                arr = ds.read(1, window=w)
                perfil = ds.profile.copy()
                perfil.update(width=int(w.width), height=int(w.height), transform=ds.window_transform(w),
                              tiled=False, compress="deflate", blockysize=1)
                ruta = destino(k)
                ruta.parent.mkdir(parents=True, exist_ok=True)
                with rasterio.open(ruta, "w", **perfil) as o:
                    o.write(arr, 1)
                escritos[k] = ruta
    return escritos


# ----------------------------------------------------------------------------------------------- descarga

def recuadros_lotes(gpkg: Path) -> dict[str, tuple[float, float, float, float]]:
    import geopandas as gpd
    g = gpd.read_file(gpkg, layer="lote").to_crs(4326)
    return {r.id_lote: tuple(r.geometry.bounds) for r in g.itertuples()}


def ruta_recorte(capa: str, clave: str) -> Path:
    return RAW / f"{capa}_{clave}.tif"


def bajar(upsert_manifest, recuadros: dict[str, tuple[float, float, float, float]], completo: bool = False,
          log=print) -> None:
    """Recortes de SEETileDrain para cada recuadro.

    completo=False (por defecto): infla el zip remoto por rangos HTTP sin guardarlo; baja del servidor
    hasta la fila más al sur que haga falta (para lotes en IA, ~60 % de cada miembro).
    completo=True: baja el zip entero (3,1 GB, reanudable) a data/raw/lotes/seetiledrain/ y recorta desde ahí.
    """
    faltan = {c: {k: v for k, v in recuadros.items() if not ruta_recorte(c, k).exists()} for c in CAPAS}
    if not any(faltan.values()):
        log("SEETileDrain: recortes ya presentes")
    if completo:
        bajar_zip(log)
        leer = rangos_local(ZIP)
        consulta = f"{URL} (zip completo, md5 {MD5})"
    else:
        leer = rangos_http()
        consulta = f"{URL} (rangos HTTP, inflado en flujo sin guardar el zip)"
    for capa, miembro in CAPAS.items():
        if faltan[capa]:
            log(f"SEETileDrain {capa}: recortando {len(faltan[capa])} recuadros de {miembro}")
            recortar_miembro(leer, BYTES, miembro, faltan[capa], lambda k, c=capa: ruta_recorte(c, k))
    filas = []
    for capa, miembro in CAPAS.items():
        for k in recuadros:
            ruta = ruta_recorte(capa, k)
            if ruta.exists():
                filas.append({"paquete": "lotes", "archivo": ruta.relative_to(RAIZ).as_posix(),
                              "fuente": "Wan et al. 2024 (HydroShare, CC BY 4.0)",
                              "producto": f"SEETileDrain 2017 30 m, recorte de {miembro.split('/')[-1]}",
                              "version": f"DOI {DOI}", "fecha_descarga": dt.date.today().isoformat(),
                              "consulta_o_url": consulta})
    if completo and ZIP.exists():
        filas.append({"paquete": "lotes", "archivo": ZIP.relative_to(RAIZ).as_posix(),
                      "fuente": "Wan et al. 2024 (HydroShare, CC BY 4.0)", "producto": "SEETileDrain_maps.zip",
                      "version": f"DOI {DOI}", "fecha_descarga": dt.date.today().isoformat(), "consulta_o_url": URL})
    if filas:
        upsert_manifest(filas)


def bajar_zip(log=print) -> Path:
    """Zip entero (3.119.442.255 bytes), reanudable con Range; verifica tamaño y MD5."""
    import hashlib
    import requests
    if ZIP.exists() and ZIP.stat().st_size == BYTES:
        return ZIP
    INTERIM.mkdir(parents=True, exist_ok=True)
    part = INTERIM / (ZIP.name + ".part")
    hecho = part.stat().st_size if part.exists() else 0
    if hecho < BYTES:
        with requests.get(URL, headers={"Range": f"bytes={hecho}-"}, stream=True, timeout=600) as r:
            if r.status_code not in (200, 206):
                raise RuntimeError(f"SEETileDrain: HTTP {r.status_code}")
            modo = "ab" if r.status_code == 206 else "wb"
            with open(part, modo) as f:
                for c in r.iter_content(16 << 20):
                    f.write(c)
    if part.stat().st_size != BYTES:
        raise RuntimeError(f"SEETileDrain: tamaño {part.stat().st_size} != {BYTES}")
    h = hashlib.md5()
    with open(part, "rb") as f:
        for c in iter(lambda: f.read(64 << 20), b""):
            h.update(c)
    if h.hexdigest() != MD5:
        raise RuntimeError("SEETileDrain: el MD5 no coincide con el de HydroShare")
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    part.rename(ZIP)
    log(f"SEETileDrain: {BYTES} bytes, MD5 ok")
    return ZIP


# ----------------------------------------------------------------------------------------------- muestreo

def muestrear(ruta: Path, x_5070: np.ndarray, y_5070: np.ndarray) -> np.ndarray:
    """Valor de la celda que contiene cada centro (EPSG:5070); NaN fuera del recorte o en nodata."""
    out = np.full(len(x_5070), np.nan)
    with rasterio.open(ruta) as d:
        lon, lat = Transformer.from_crs(5070, d.crs, always_xy=True).transform(np.asarray(x_5070, float),
                                                                               np.asarray(y_5070, float))
        fil, col = rasterio.transform.rowcol(d.transform, lon, lat)
        fil, col = np.asarray(fil), np.asarray(col)
        ok = (fil >= 0) & (fil < d.height) & (col >= 0) & (col < d.width)
        a = d.read(1).astype(float)
        if d.nodata is not None:
            a[a == d.nodata] = np.nan
        a[~np.isfinite(a)] = np.nan
        out[ok] = a[fil[ok], col[ok]]
    return out


def columnas_lote(id_lote: str, x_5070: np.ndarray, y_5070: np.ndarray) -> dict[str, np.ndarray]:
    """`tile_prob_seetiledrain` (0-1) y `tile_seetiledrain` (0/1) por píxel; NaN si falta el recorte."""
    out = {}
    for capa, col in COLUMNAS.items():
        ruta = ruta_recorte(capa, id_lote)
        v = muestrear(ruta, x_5070, y_5070) if ruta.exists() else np.full(len(x_5070), np.nan)
        if capa == "prob":
            v = np.where((v >= 0) & (v <= 1), v, np.nan)
        else:
            v = np.where(np.isin(v, (0, 1)), v, np.nan)
        out[col] = v
    return out


if __name__ == "__main__":
    import argparse
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from download import log, upsert_manifest

    ap = argparse.ArgumentParser(description="Recortes de SEETileDrain para los lotes")
    ap.add_argument("--completo", action="store_true", help="bajar el zip entero (3,1 GB) y recortar desde ahí")
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("LON0", "LAT0", "LON1", "LAT1"),
                    help="recortar un recuadro de prueba en lugar de los lotes de lotes.gpkg")
    ap.add_argument("--id", default="prueba", help="clave del recuadro de --bbox")
    ap.add_argument("--capas", default="prob,clase")
    a = ap.parse_args()
    CAPAS = {c: CAPAS[c] for c in a.capas.split(",")}
    rec = {a.id: tuple(a.bbox)} if a.bbox else recuadros_lotes(RAIZ / "data" / "processed" / "lotes" / "lotes.gpkg")
    bajar(upsert_manifest, rec, completo=a.completo, log=log)
