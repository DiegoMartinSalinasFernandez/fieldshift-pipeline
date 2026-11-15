"""Riego por condado y año desde LANID (T127; research: docs/research/riego_mascaras.md y riego_ne_ks.md).

LANID (Landsat-based Irrigation Dataset, Xie y Lark): mapas binarios de riego de 30 m para todo
EE.UU. La versión 3.0 de Zenodo (DOI 10.5281/zenodo.5548555, CC BY 4.0) trae 1997–2017; una
extensión del USGS (Martin y Brandt, 2024, DOI 10.5066/P9YWR0OJ) agrega 2018, 2019 y 2020.

Descarga (`python src/cultivos/riego.py bajar`):
- De Zenodo, a data/raw/cultivos/lanid/: los tres zips anuales, `irrFreqAndChange.zip` (trae
  `maxIrrExt`) y `Metadata.docx` (~1,7 GB). Reanudable, con control de md5 y fila en manifest.csv.
- La extensión 2018–2020 está en ScienceBase, que suele pedir un desafío de Cloudflare a los
  clientes automáticos. Se intenta por la API JSON de ScienceBase; si no responde, se avisa y se
  sigue. Los TIF (`lanid2018.tif`, `lanid2019.tif`, `lanid2020.tif`, `maxIrrExt_0020.tif`) se pueden
  bajar a mano a data/raw/cultivos/lanid/ y registrarlos con `python src/cultivos/riego.py registrar`.

Proceso (`python src/cultivos/riego.py procesar`), sobre la grilla de
data/reference/mascara_agricola.tif (EPSG:5070, 30 m; LANID se lleva a esa grilla con vecino más
cercano):
- data/processed/cultivos/riego_anual.csv: fips, anio, frac_riego_lanid, frac_maiz_regado,
  frac_soja_regada, frac_pixeles_validos. Solo los años que cubre LANID (no se rellena el resto).
- data/reference/mascara_riego_max.tif: 1 = píxel regado en algún año de LANID (`maxIrrExt`).
"""
from __future__ import annotations

import csv
import hashlib
import re
import shutil
import sys
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.common.config import cargar_config, estados_config  # noqa: E402
from src.common.manifest import asegurar_manifest  # noqa: E402

RAW = REPO / "data" / "raw" / "cultivos" / "lanid"
INTERIM = REPO / "data" / "interim" / "cultivos"
OUT = REPO / "data" / "processed" / "cultivos"
REFERENCIA = REPO / "data" / "reference"
MANIFEST = REPO / "manifest.csv"

ZENODO_API = "https://zenodo.org/api/records/5548555"
ZENODO_ARCHIVOS = ["Metadata.docx", "lanid2011-2017.zip", "lanid2004-2010.zip", "lanid1997-2003.zip",
                   "irrFreqAndChange.zip"]
SCIENCEBASE_ITEM = "https://www.sciencebase.gov/catalog/item/639a11b9d34e0de3a1f0ddde?format=json"
USGS_ARCHIVOS = ["lanid2018.tif", "lanid2019.tif", "lanid2020.tif", "maxIrrExt_0020.tif"]
LIMITE_BYTES = 5e9  # regla 6 del CLAUDE.md

REGADO = 1  # valor de "regado" en los rasters anuales de LANID y en maxIrrExt (0 = no regado)
SIN_DATO = 255  # relleno fuera de la cobertura de LANID al llevarlo a la grilla (LANID es binario)


# ---------------------------------------------------------------- descarga

def _md5(ruta: Path) -> str:
    h = hashlib.md5()
    with open(ruta, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def _bajar(url: str, destino: Path, total: int, md5: str | None = None) -> bool:
    """Baja con Range a interim/<nombre>.part y lo mueve a raw al completar. True si quedó bien."""
    INTERIM.mkdir(parents=True, exist_ok=True)
    part = INTERIM / (destino.name + ".part")
    for _ in range(20):
        hecho = part.stat().st_size if part.exists() else 0
        if total and hecho >= total:
            break
        with requests.get(url, headers={"Range": f"bytes={hecho}-"}, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(part, "ab" if r.status_code == 206 else "wb") as f:
                for bloque in r.iter_content(1 << 20):
                    f.write(bloque)
        print(f"{destino.name}: {part.stat().st_size / 1e6:.0f} / {total / 1e6:.0f} MB", flush=True)
        if not total:
            break
    if md5 and _md5(part) != md5:
        print(f"AVISO: md5 de {destino.name} no coincide; se borra el parcial", flush=True)
        part.unlink()
        return False
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(part), destino)
    return True




def registrar(ruta: Path, url: str, man: Path | None = None) -> None:
    """Fila de manifest.csv para un archivo de LANID (una sola vez por archivo)."""
    man = man or MANIFEST
    asegurar_manifest(man)
    try:
        rel = ruta.relative_to(REPO).as_posix()
    except ValueError:
        rel = ruta.as_posix()
    with open(man, encoding="utf-8") as f:
        if any(rel == fila.get("archivo") for fila in csv.DictReader(f)):
            return
    if ruta.name in USGS_ARCHIVOS:
        fuente, producto, version = "USGS", "LANID: Landsat-based irrigation dataset for CONUS 2018-20", "2024"
    else:
        fuente, producto, version = "Zenodo (Xie y Lark)", "LANID-US: Landsat-based Irrigation Dataset", "3.0"
    with open(man, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(["cultivos", rel, fuente, producto, version, date.today().isoformat(), url])


def bajar_zenodo() -> None:
    meta = requests.get(ZENODO_API, timeout=60).json()
    archivos = {f["key"]: f for f in meta["files"]}
    faltan = [n for n in ZENODO_ARCHIVOS if not (RAW / n).exists()]
    total = sum(archivos[n]["size"] for n in faltan if n in archivos)
    if total > LIMITE_BYTES:
        raise RuntimeError(f"LANID pesa {total / 1e9:.1f} GB (> 5 GB): pedir el OK al humano (regla 6)")
    for n in ZENODO_ARCHIVOS:
        destino = RAW / n
        if n not in archivos:
            print(f"AVISO: {n} no está en el registro de Zenodo (versión {meta['metadata'].get('version')})")
            continue
        f = archivos[n]
        url = f["links"]["self"]
        if destino.exists():
            print(f"ya está: {destino.relative_to(REPO)}")
        elif not _bajar(url, destino, f["size"], f.get("checksum", "").removeprefix("md5:") or None):
            continue
        registrar(destino, url)


def bajar_usgs() -> None:
    """Extensión 2018–2020 desde ScienceBase. Si ScienceBase no da JSON (Cloudflare), avisa y sigue."""
    faltan = [n for n in USGS_ARCHIVOS if not (RAW / n).exists()]
    if not faltan:
        return
    try:
        r = requests.get(SCIENCEBASE_ITEM, timeout=60, headers={"Accept": "application/json"})
        item = r.json()
    except (requests.RequestException, ValueError):
        print("AVISO: ScienceBase no respondió con JSON (desafío de Cloudflare). LANID 2018–2020 queda sin "
              f"bajar; bajar a mano {faltan} a {RAW.relative_to(REPO)} y correr `riego.py registrar`.")
        return
    archivos = {f["name"]: f for f in item.get("files", [])}
    for n in faltan:
        if n not in archivos:
            print(f"AVISO: {n} no está en el ítem de ScienceBase")
            continue
        url = archivos[n]["url"]
        if _bajar(url, RAW / n, int(archivos[n].get("size") or 0)):
            registrar(RAW / n, url)


def registrar_manuales() -> None:
    """Registra en el manifest los TIF del USGS bajados a mano."""
    for n in USGS_ARCHIVOS:
        if (RAW / n).exists():
            registrar(RAW / n, "https://doi.org/10.5066/P9YWR0OJ")


# ---------------------------------------------------------------- lectura de LANID

def _tifs_en_zip(z: Path) -> list[str]:
    with zipfile.ZipFile(z) as f:
        return [n for n in f.namelist() if n.lower().endswith(".tif")]


def fuentes_lanid(raw: Path = RAW) -> tuple[dict[int, str], str | None]:
    """({anio: ruta GDAL del raster anual}, ruta de maxIrrExt) a partir de lo que hay en raw.

    Los TIF sueltos (extensión del USGS) tienen prioridad sobre los de los zips. Para la extensión
    máxima se prefiere `maxIrrExt_0020` (2000–2020) a `maxIrrExt` de Zenodo (1997–2017).
    """
    anuales: dict[int, str] = {}
    maximos: dict[str, str] = {}
    candidatos = [(p.name, p.as_posix()) for p in sorted(raw.glob("*.tif"))]
    for z in sorted(raw.glob("*.zip")):
        candidatos += [(Path(n).name, f"/vsizip/{z.as_posix()}/{n}") for n in _tifs_en_zip(z)]
    for nombre, ruta in candidatos:
        m = re.fullmatch(r"lanid(\d{4})\.tif", nombre, re.I)
        if m:
            anuales.setdefault(int(m.group(1)), ruta)
        elif re.fullmatch(r"maxIrrExt(_\d+)?\.tif", nombre, re.I):
            maximos.setdefault(nombre.lower(), ruta)
    maximo = maximos.get("maxirrext_0020.tif") or next(iter(sorted(maximos.values())), None)
    return anuales, maximo


class _Grilla:
    """LANID (u otro raster) llevado a la grilla de `ref` con vecino más cercano, leído por ventanas.

    Válido = dentro de la cobertura del raster y distinto de su nodata. Si el nodata declarado es 0,
    no se respeta: en LANID 0 es "no regado" (Metadata.docx de Zenodo), no "sin dato".
    """

    def __init__(self, ruta: str, ref):
        import rasterio
        from rasterio.enums import Resampling
        from rasterio.vrt import WarpedVRT

        self.src = rasterio.open(ruta)
        nod = self.src.nodata if self.src.nodata not in (None, 0) else None
        self.fuera = nod if nod is not None else SIN_DATO
        self.vrt = WarpedVRT(self.src, crs=ref.crs, transform=ref.transform, width=ref.width,
                             height=ref.height, resampling=Resampling.nearest, src_nodata=nod,
                             nodata=self.fuera)

    def leer(self, ventana=None) -> tuple[np.ndarray, np.ndarray]:
        a = self.vrt.read(1, window=ventana)
        return a, a != self.fuera

    def cerrar(self) -> None:
        self.vrt.close()
        self.src.close()


def _a_grilla(ruta: str, ref) -> tuple[np.ndarray, np.ndarray]:
    """(valores, válido) del raster entero en la grilla de `ref`."""
    g = _Grilla(ruta, ref)
    try:
        return g.leer()
    finally:
        g.cerrar()


# ---------------------------------------------------------------- proceso

FILAS_FRANJA = 2048  # filas de la grilla por franja (la memoria no depende del tamaño de la zona)


def _contar(ids: np.ndarray, sel: np.ndarray, n: int) -> np.ndarray:
    return np.bincount(ids[sel], minlength=n + 1)[1:]


def _frac(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / np.maximum(den, 1), np.nan)


def riego_anual(mascara: Path, condados, anuales: dict[int, str], anios: list[int],
                referencia: Path | None = None, filas_franja: int = FILAS_FRANJA) -> pd.DataFrame:
    """Fracciones de riego por condado y año sobre la grilla de `mascara` (agrícola = 1).

    - frac_riego_lanid = píxeles agrícolas regados / píxeles agrícolas con dato de LANID.
    - frac_maiz_regado / frac_soja_regada: lo mismo dentro de mascara_maiz_<anio>.tif /
      mascara_soja_<anio>.tif (vacío si no está la máscara de ese año o no hay píxeles del cultivo).
    - frac_pixeles_validos = píxeles agrícolas con dato de LANID / píxeles agrícolas.

    Recorre la grilla por franjas de filas: en cada una rasteriza los condados y lee todos los años.
    """
    import rasterio
    from rasterio.features import rasterize
    from rasterio.windows import Window
    from rasterio.windows import transform as transform_ventana

    referencia = referencia or mascara.parent
    anios = [a for a in anios if a in anuales]
    cols = ["fips", "anio", "frac_riego_lanid", "frac_maiz_regado", "frac_soja_regada", "frac_pixeles_validos"]
    if not anios:
        return pd.DataFrame(columns=cols)
    with rasterio.open(mascara) as ref:
        cond = condados.to_crs(ref.crs).reset_index(drop=True)
        fips = cond["fips"].astype(str).str.zfill(5).tolist()
        formas = [(g, i + 1) for i, g in enumerate(cond.geometry)]
        n = len(fips)
        lanid = {a: _Grilla(anuales[a], ref) for a in anios}
        cultivos = {}
        for a in anios:
            for nom in ("maiz", "soja"):
                p = referencia / f"mascara_{nom}_{a}.tif"
                if p.exists():
                    mc = rasterio.open(p)
                    if (mc.transform, mc.shape) != (ref.transform, ref.shape):
                        raise ValueError(f"{p.name} no está en la grilla de {mascara.name}")
                    cultivos[(a, nom)] = mc
        n_agri = np.zeros(n, np.int64)
        cuenta = {(a, k): np.zeros(n, np.int64) for a in anios
                  for k in ("val", "reg", "maiz_val", "maiz_reg", "soja_val", "soja_reg")}
        try:
            for f0 in range(0, ref.height, filas_franja):
                win = Window(0, f0, ref.width, min(filas_franja, ref.height - f0))
                ids = rasterize(formas, out_shape=(int(win.height), int(win.width)),
                                transform=transform_ventana(win, ref.transform), fill=0, dtype="int32")
                if not ids.any():
                    continue
                agri = (ref.read(1, window=win) == 1) & (ids > 0)
                n_agri += _contar(ids, agri, n)
                for a in anios:
                    v, valido = lanid[a].leer(win)
                    regado = valido & (v == REGADO)
                    cuenta[(a, "val")] += _contar(ids, agri & valido, n)
                    cuenta[(a, "reg")] += _contar(ids, agri & regado, n)
                    for nom in ("maiz", "soja"):
                        if (a, nom) in cultivos:
                            cult = (cultivos[(a, nom)].read(1, window=win) == 1) & (ids > 0)
                            cuenta[(a, nom + "_val")] += _contar(ids, cult & valido, n)
                            cuenta[(a, nom + "_reg")] += _contar(ids, cult & regado, n)
        finally:
            for g in lanid.values():
                g.cerrar()
            for mc in cultivos.values():
                mc.close()
    filas = []
    for a in anios:
        df = pd.DataFrame({"fips": fips, "anio": a,
                           "frac_riego_lanid": _frac(cuenta[(a, "reg")], cuenta[(a, "val")])})
        for col, nom in (("frac_maiz_regado", "maiz"), ("frac_soja_regada", "soja")):
            df[col] = (_frac(cuenta[(a, nom + "_reg")], cuenta[(a, nom + "_val")])
                       if (a, nom) in cultivos else np.nan)
        df["frac_pixeles_validos"] = _frac(cuenta[(a, "val")], n_agri)
        filas.append(df)
    out = pd.concat(filas, ignore_index=True)[cols]
    # condados sin píxeles agrícolas: sin fila (no hay área agrícola sobre la que medir)
    out = out[out["fips"].isin([f for f, k in zip(fips, n_agri) if k > 0])]
    for c in cols[2:]:
        out[c] = out[c].astype(float).round(4)
    return out.sort_values(["fips", "anio"]).reset_index(drop=True)


def mascara_riego_max(mascara: Path, maximo: str, salida: Path, filas_franja: int = FILAS_FRANJA) -> float:
    """maxIrrExt de LANID en la grilla de `mascara` (1 bit). Devuelve la fracción regada de la grilla."""
    import rasterio
    from rasterio.windows import Window

    with rasterio.open(mascara) as ref:
        perfil = {"driver": "GTiff", "dtype": "uint8", "count": 1, "width": ref.width, "height": ref.height,
                  "crs": ref.crs, "transform": ref.transform, "nodata": None, "compress": "deflate",
                  "nbits": 1, "tiled": True, "blockxsize": 512, "blockysize": 512}
        g = _Grilla(maximo, ref)
        salida.parent.mkdir(parents=True, exist_ok=True)
        regados = 0
        try:
            with rasterio.open(salida, "w", **perfil) as dst:
                for f0 in range(0, ref.height, filas_franja):
                    win = Window(0, f0, ref.width, min(filas_franja, ref.height - f0))
                    v, valido = g.leer(win)
                    m = (valido & (v == REGADO)).astype("uint8")
                    regados += int(m.sum())
                    dst.write(m, 1, window=win)
        finally:
            g.cerrar()
        return regados / (ref.width * ref.height)


def procesar() -> None:
    import geopandas as gpd

    mascara = REFERENCIA / "mascara_agricola.tif"
    gpkg = REFERENCIA / "condados.gpkg"
    if not mascara.exists() or not gpkg.exists():
        print("falta data/reference/mascara_agricola.tif o condados.gpkg (paquete 0 y cultivos/process.py)")
        return
    anuales, maximo = fuentes_lanid()
    if not anuales:
        print(f"no hay rasters de LANID en {RAW.relative_to(REPO)}: correr `riego.py bajar`")
        return
    per = cargar_config()["periodo"]
    anios = list(range(int(per["anio_inicio"]), int(per["anio_fin"]) + 1))
    cond = gpd.read_file(gpkg)
    cond["fips"] = cond["fips"].astype(str).str.zfill(5)
    cond = cond[cond["fips"].str[:2].isin({e["fips"] for e in estados_config().values()})]
    df = riego_anual(mascara, cond, anuales, anios)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "riego_anual.csv", index=False, encoding="utf-8")
    print(f"riego_anual.csv: {len(df)} filas, años {sorted(df['anio'].unique().tolist())}")
    if maximo:
        frac = mascara_riego_max(mascara, maximo, REFERENCIA / "mascara_riego_max.tif")
        print(f"mascara_riego_max.tif desde {Path(maximo).name}: {100 * frac:.2f} % de la grilla regada")


def main() -> None:
    orden = sys.argv[1] if len(sys.argv) > 1 else "todo"
    if orden in ("bajar", "todo"):
        bajar_zenodo()
        bajar_usgs()
    if orden == "registrar":
        registrar_manuales()
    if orden in ("procesar", "todo"):
        procesar()


if __name__ == "__main__":
    main()
