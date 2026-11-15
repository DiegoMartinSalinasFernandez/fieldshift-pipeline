"""paisaje: % del área de cada condado por clase de Annual NLCD y superficie impermeable media.

Lee los recortes por estado de data/raw/paisaje/ (Annual NLCD C1V1, 30 m), asigna cada píxel a un
condado por su centro (rasterización de condados.gpkg en la grilla del recorte) y cuenta píxeles por
clase. El % es sobre todos los píxeles del condado con dato (incluye agua), no sobre la máscara
agrícola. Escribe data/processed/paisaje/paisaje_anual.csv y la tabla de docs/datasets/paisaje.md.

Uso: python src/paisaje/process.py
"""
import re
import sys
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.zona_texto import lista_estados  # noqa: E402
RAW = ROOT / "data/raw/paisaje"
OUT = ROOT / "data/processed/paisaje"
CARD = ROOT / "docs/datasets/paisaje.md"
NODATA = 250
FILAS = 2048

CLASES = {
    "pct_cultivos_nlcd": [82],
    "pct_pasturas_heno_nlcd": [81],
    "pct_bosque_nlcd": [41, 42, 43],
    "pct_humedales_nlcd": [90, 95],
    "pct_urbano_nlcd": [21, 22, 23, 24],
    "pct_agua_nlcd": [11],
}
COLS = list(CLASES) + ["impermeable_pct"]
PAT = re.compile(r"Annual_NLCD_(LndCov|FctImp)_(\d{4})_([A-Z]{2})_C1V1\.tif$")


def indice_condados(src, cond):
    """Raster int16 con el índice (posición en cond) del condado de cada píxel; -1 fuera."""
    g = cond.to_crs(src.crs)
    shapes = ((geom, i) for i, geom in zip(g.index, g.geometry))
    return rasterize(shapes, out_shape=(src.height, src.width), transform=src.transform,
                     fill=-1, dtype="int16", all_touched=False)


def histograma(path, idx, n):
    cuentas = np.zeros((n, 256), dtype=np.int64)
    with rasterio.open(path) as src:
        for r in range(0, src.height, FILAS):
            h = min(FILAS, src.height - r)
            v = src.read(1, window=rasterio.windows.Window(0, r, src.width, h))
            ii = idx[r:r + h]
            m = ii >= 0
            k = ii[m].astype(np.int64) * 256 + v[m]
            cuentas += np.bincount(k, minlength=n * 256).reshape(n, 256)
    return cuentas


def main():
    t0 = time.time()
    cond = gpd.read_file(ROOT / "data/reference/condados.gpkg")
    cond["fips"] = cond["fips"].astype(str).str.zfill(5)
    cond = cond.sort_values("fips").reset_index(drop=True)
    archivos = sorted(p for p in RAW.glob("*.tif") if PAT.search(p.name))
    filas = {}
    idx_cache = {}
    for p in archivos:
        prod, anio, est = PAT.search(p.name).groups()
        anio = int(anio)
        sub = cond[cond["estado"] == est]
        with rasterio.open(p) as src:
            clave = (est, src.width, src.height, tuple(src.transform)[:6])
            if clave not in idx_cache:
                local = sub.reset_index(drop=True)
                idx_cache[clave] = (indice_condados(src, local), local)
        idx, local = idx_cache[clave]
        c = histograma(p, idx, len(local))
        validos = c[:, :NODATA].sum(axis=1) + c[:, NODATA + 1:].sum(axis=1)
        for i, fips in enumerate(local["fips"]):
            fila = filas.setdefault((fips, anio), {})
            if validos[i] == 0:
                continue
            if prod == "LndCov":
                for col, cl in CLASES.items():
                    fila[col] = 100.0 * c[i, cl].sum() / validos[i]
            else:
                vals = np.arange(101)
                tot = c[i, :101].sum()
                if tot > 0:
                    fila["impermeable_pct"] = float((c[i, :101] * vals).sum() / tot)
        print(f"{p.name} {time.time()-t0:.0f}s", flush=True)
    df = pd.DataFrame([{"fips": k[0], "anio": k[1], **v} for k, v in filas.items()], columns=["fips", "anio"] + COLS)
    df = df.sort_values(["fips", "anio"]).reset_index(drop=True)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "paisaje_anual.csv", index=False, float_format="%.4f", encoding="utf-8", lineterminator="\n")
    escribir_card(df)
    print(f"listo: {len(df)} filas, {time.time()-t0:.0f}s")


DESC = {
    "pct_cultivos_nlcd": "% del área del condado en Cultivated Crops (clase NLCD 82)",
    "pct_pasturas_heno_nlcd": "% del área del condado en Pasture/Hay (clase NLCD 81)",
    "pct_bosque_nlcd": "% del área del condado en bosque (clases NLCD 41, 42 y 43)",
    "pct_humedales_nlcd": "% del área del condado en humedales (clases NLCD 90 y 95)",
    "pct_urbano_nlcd": "% del área del condado en desarrollo urbano (clases NLCD 21 a 24)",
    "pct_agua_nlcd": "% del área del condado en agua abierta (clase NLCD 11)",
    "impermeable_pct": "Superficie impermeable media del condado (media de Annual NLCD FctImp, 0-100 % por píxel)",
}
FUENTE = {c: "USGS Annual NLCD C1V1 LndCov (30 m)" for c in CLASES}
FUENTE["impermeable_pct"] = "USGS Annual NLCD C1V1 FctImp (30 m)"


def escribir_card(df):
    filas = ["| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |",
             "|---|---|---|---|---|---|---|---|---|"]
    for c in COLS:
        llenos = df.loc[df[c].notna(), "anio"]
        desde, hasta = (int(llenos.min()), int(llenos.max())) if len(llenos) else ("", "")
        falt = 100 * df[c].isna().mean() if len(df) else 100.0
        filas.append(f"| paisaje_anual.csv | {c} | {DESC[c]} | % | {FUENTE[c]} |  | {desde} | {hasta} | {falt:.2f} |")
    tabla = "\n".join(filas)
    anios = sorted(df["anio"].unique()) if len(df) else []
    cobertura = f"{len(df)} filas, {df['fips'].nunique() if len(df) else 0} condados, años {anios[0] if anios else ''}-{anios[-1] if anios else ''}"
    CARD.write_text(TEXTO.format(tabla=tabla, cobertura=cobertura, estados=lista_estados()), encoding="utf-8")


TEXTO = """# Data card — paisaje

Cobertura del suelo por condado desde USGS Annual NLCD (National Land Cover Database anual,
Collection 1 versión 1, 30 m): % del área en cultivos, pasturas y heno, bosque, humedales, urbano y
agua, y la superficie impermeable media.

## Archivos

- `data/processed/paisaje/paisaje_anual.csv` — `fips, anio, ...`, una fila por condado y año. Cobertura real: {cobertura}.

## Diccionario de columnas

{tabla}

## Fuentes y acceso

- USGS EROS / MRLC, Annual NLCD Collection 1 v1 (1985-2024): mosaicos CONUS `Annual_NLCD_LndCov_<anio>_CU_C1V1.tif`
  y `Annual_NLCD_FctImp_<anio>_CU_C1V1.tif` (COG). Originales en `s3://usgs-landcover/annual-nlcd/c1/v1/cu/mosaic/`
  (requester-pays); se leen sin login desde el mirror público de Source Cooperative
  `https://data.source.coop/kylebarron/usgs-landcover/annual-nlcd/c1/v1/cu/mosaic/`.
- `src/paisaje/download.py` lee por ventana solo el bbox de cada estado ({estados}) y lo guarda tal cual
  (mismos valores, misma grilla de 30 m) en `data/raw/paisaje/Annual_NLCD_<producto>_<anio>_<estado>_C1V1.tif`.

## Supuestos

- Fuente: Annual NLCD (una capa por año) en lugar de las ediciones clásicas de NLCD. Acceso por el mirror
  de Source Cooperative (copia de `s3://usgs-landcover`, que es requester-pays), no por el sitio de MRLC:
  el bucket público `s3-us-west-2.amazonaws.com/mrlc` devuelve 403 o un archivo de 42 bytes para estos nombres.
- La grilla de NLCD está en Albers CONUS con datum WGS84 (`AEA WGS84`); los condados se reproyectan a ese CRS.
  La diferencia con EPSG:5070 (NAD83) es de alrededor de 1 m, despreciable a 30 m.
- Cada píxel se asigna al condado que contiene su centro (rasterización sin `all_touched`); cada recorte de
  estado se usa solo para los condados de ese estado.
- El % es sobre todos los píxeles del condado con dato (incluye agua abierta), no sobre la máscara agrícola.
  Valor 250 = sin dato, se excluye del denominador.
- `impermeable_pct` es la media de FctImp (0-100 %) sobre los píxeles del condado con dato.
- Annual NLCD C1V1 llega hasta 2024: 2025 queda sin filas hasta que USGS lo publique.
- No hay ID del catálogo para estas columnas (el catálogo es de la versión argentina): `id_catalogo` vacío.

## Problemas conocidos

- 2025 no existe todavía en Annual NLCD (C1V1 cubre 1985-2024).
- Si una ronda de descarga se cortó, algunos años o estados pueden faltar: sus celdas quedan vacías
  (ver desde/hasta y faltantes_pct en la tabla) hasta volver a correr `download.py`.
- La clase 82 de NLCD (Cultivated Crops) no separa cultivos; el CDL del paquete `cultivos` da el detalle.
"""

if __name__ == "__main__":
    main()
