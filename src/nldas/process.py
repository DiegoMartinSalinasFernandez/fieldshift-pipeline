"""Procesa NLDAS-2 Noah mensual (NLDAS_NOAH0125_M v2.0) a medias mensuales por condado.

Salida: data/processed/nldas/nldas_mensual.csv (fips, anio, mes, ...) y la tabla de
docs/datasets/nldas.md (desde, hasta y % de faltantes reales).

- Media del condado ponderada por la fracción de cada celda de 0,125° dentro del condado
  (supermuestreo 10x de la grilla); las celdas sin dato (lagos) no cuentan.
- Humedad: SoilM_0_10cm / 100 mm y SoilM_0_100cm / 1000 mm (kg m-2 = mm de agua) -> m3/m3.
- ET = Evap (kg m-2, suma del mes = mm). Escorrentía = Qs + Qsb (sumas del mes, mm).
  SWE = media del mes (kg m-2 = mm).
- sm_0_100cm_anom_z: (valor − media) / desvío del mes calendario en 1991-2020, por condado.

Uso: python src/nldas/process.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from rasterio.features import rasterize
from rasterio.transform import from_origin

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import cargar_config  # noqa: E402

RAW = REPO / "data" / "raw" / "nldas" / "nldas_noah_m"
OUT = REPO / "data" / "processed" / "nldas"
CARD = REPO / "docs" / "datasets" / "nldas.md"
VARS = ["SoilM_0_10cm", "SoilM_0_100cm", "Evap", "Qs", "Qsb", "SWE"]
COLS = ["sm_0_10cm_m3m3", "sm_0_100cm_m3m3", "sm_0_100cm_anom_z", "et_nldas_mm",
        "escorrentia_nldas_mm", "swe_nldas_mm"]
DEC = {"sm_0_10cm_m3m3": 4, "sm_0_100cm_m3m3": 4, "sm_0_100cm_anom_z": 3, "et_nldas_mm": 2,
       "escorrentia_nldas_mm": 2, "swe_nldas_mm": 2}


def pesos(gdf: gpd.GeoDataFrame, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Matriz (condados x celdas, grilla norte-arriba) con la fracción de cada celda en el condado."""
    ny, nx, k, paso = len(lat), len(lon), 10, 0.125
    tr = from_origin(lon.min() - paso / 2, lat.max() + paso / 2, paso / k, paso / k)
    fino = rasterize(((geom, i + 1) for i, geom in enumerate(gdf.geometry)), out_shape=(ny * k, nx * k),
                     transform=tr, fill=0, dtype="int32")
    f, c = np.nonzero(fino)
    w = np.zeros((len(gdf), ny * nx))
    np.add.at(w, (fino[f, c] - 1, (f // k) * nx + (c // k)), 1.0)
    return w


def grupos_archivos(archivos: list[Path], gdf: gpd.GeoDataFrame) -> list[tuple[gpd.GeoDataFrame, list[Path]]]:
    """Separa los NetCDF por recorte (sufijo del nombre) con los condados que le tocan.

    "_zona.nc" cubre todos los condados (un solo grupo de estados, como IA, IL e IN). Con varios
    grupos (T023) el sufijo trae los estados, por ejemplo "_KS-NE.nc", y cada grilla se usa solo
    para los condados de esos estados.
    """
    por_sufijo: dict[str, list[Path]] = {}
    for p in archivos:
        por_sufijo.setdefault(p.stem.rsplit("_", 1)[1], []).append(p)
    out = []
    for suf, arch in sorted(por_sufijo.items()):
        sub = gdf if suf == "zona" else gdf[gdf["estado"].isin(suf.split("-"))]
        if len(sub):
            out.append((sub.reset_index(drop=True), arch))
    return out


def leer(p: Path, lat: np.ndarray, lon: np.ndarray) -> tuple[str, dict]:
    with xr.open_dataset(p) as d:
        mes = pd.Timestamp(d["time"].values[0]).strftime("%Y-%m")
        if not np.allclose(d["lat"].values, lat) or not np.allclose(d["lon"].values, lon):
            raise ValueError(f"grilla distinta en {p.name}")
        sur_arriba = d["lat"].values[0] < d["lat"].values[-1]
        vals = {}
        for v in VARS:
            a = d[v].values[0].astype(float)
            a = np.where(np.isfinite(a) & (a > -9000), a, np.nan)   # -9999 = sin dato
            vals[v] = (a[::-1] if sur_arriba else a).ravel()
    return mes, vals


def media(w: np.ndarray, a: np.ndarray) -> np.ndarray:
    ok = np.isfinite(a)
    num = w[:, ok] @ a[ok]
    den = w[:, ok].sum(axis=1)
    return np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)


def tabla_card(df: pd.DataFrame) -> str:
    fuente = "NLDAS-2 Noah mensual v2.0 (NLDAS_NOAH0125_M, NASA GES DISC por Harmony)"
    desc = {
        "sm_0_10cm_m3m3": ("Humedad volumétrica 0-10 cm: SoilM_0_10cm (kg m-2) / 100 mm, media ponderada del condado", "m3/m3", "G01"),
        "sm_0_100cm_m3m3": ("Humedad volumétrica 0-100 cm: SoilM_0_100cm (kg m-2) / 1000 mm, media ponderada del condado", "m3/m3", "G02"),
        "sm_0_100cm_anom_z": ("Anomalía z de sm_0_100cm_m3m3 por condado y mes calendario, base 1991-2020", "adim.", ""),
        "et_nldas_mm": ("Evapotranspiración total del mes (Evap, suma mensual)", "mm", "G03"),
        "escorrentia_nldas_mm": ("Escorrentía total del mes: superficial (Qs) + subsuperficial (Qsb)", "mm", "G04"),
        "swe_nldas_mm": ("Equivalente en agua de la nieve, media del mes (SWE)", "mm", ""),
    }
    filas = ["| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |",
             "|---|---|---|---|---|---|---|---|---|"]
    for c in COLS:
        llenos = df.loc[df[c].notna(), "mes"]
        desde, hasta = (llenos.min(), llenos.max()) if len(llenos) else ("", "")
        falt = 100 * df[c].isna().mean()
        d, u, i = desc[c]
        filas.append(f"| nldas_mensual.csv | {c} | {d} | {u} | {fuente} | {i} | {desde} | {hasta} | {falt:.2f} |")
    return "\n".join(filas)


TEXTO = """# Data card — nldas

NLDAS-2 (North American Land Data Assimilation System, fase 2), modelo de superficie Noah, producto
mensual `NLDAS_NOAH0125_M` versión 2.0 (NASA GES DISC, colección CMR `C1887990023-GES_DISC`),
grilla de 0,125°, desde 1979-01. Completa a SMAP (paquete `agua`), que empieza en 2015-03.
Se baja un recorte por mes y grupo de estados contiguos (`..._zona.nc` si hay un solo grupo, como IA,
IL e IN; si no, `..._KS-NE.nc`, `..._MN.nc`, `..._OH.nc`); cada condado usa el recorte de su grupo.

## Archivos

- `data/processed/nldas/nldas_mensual.csv` → `fips, anio, mes, ...` (`anio` = año calendario del mes),
  2000-01 a 2025-12, una fila por condado y mes.

## Diccionario de columnas

{tabla}

## Fuentes y acceso

- Descarga: `src/nldas/download.py`. Harmony (`harmony.earthdata.nasa.gov`, OGC API Coverages) con
  recorte en origen por bbox de la zona (condados ± 0,05°), por mes y por variable (`SoilM_0_10cm`,
  `SoilM_0_100cm`, `Evap`, `Qs`, `Qsb`, `SWE`). Un NetCDF4 de ~160 KB por mes en
  `data/raw/nldas/nldas_noah_m/<anio>/`. Se baja 1991-2025: 1991-1999 solo sirve de base para la
  anomalía z (1991-2020); el CSV cubre el período del proyecto (2000-2025).
- Procesamiento: `src/nldas/process.py` (también genera esta tabla).

## Supuestos

- **Acceso con login (Earthdata).** No se encontró un acceso público sin login al mismo producto:
  NLDAS-2 solo se distribuye por GES DISC (HTTPS, OPeNDAP, Harmony, todos con Earthdata); el OPeNDAP de
  hydro1 devuelve 410 (retirado, ver bitácora de `vegetacion`). Se usó Harmony con la credencial de
  Earthdata disponible. No hay copia en Planetary Computer ni en AWS Open Data sin login que se haya
  verificado en esta ronda.
- **Conversión a m³/m³.** NLDAS da la humedad como masa de agua por área de cada capa (kg m-2 = mm). Se
  divide por el espesor de la capa: 100 mm (0-10 cm) y 1000 mm (0-100 cm). `SoilM_0_100cm` es la capa
  acumulada 0-100 cm del propio producto.
- **Agregación espacial:** media del condado ponderada por la fracción de área de cada celda de 0,125°
  (~12 km) dentro del condado (supermuestreo 10x en grados). No se usa la máscara agrícola del CDL: a
  12 km casi todas las celdas mezclan usos y el producto es un modelo con vegetación propia, así que no
  se agrega `frac_pixeles_validos`. Celdas sin dato (agua, por ejemplo el lago Michigan) no cuentan.
- **Escorrentía total** = `Qs` (superficial) + `Qsb` (subsuperficial/drenaje de base), sumas mensuales.
  Si falta cualquiera de las dos en una celda, la celda no cuenta para ese mes.
- **ET** = `Evap` (evapotranspiración total, suma mensual). Puede ser apenas negativa en invierno
  (condensación/escarcha neta del modelo): se deja el valor del modelo, no se recorta.
- **Anomalía z:** por condado y mes calendario, con media y desvío (n − 1) de 1991-2020 de
  `sm_0_100cm_m3m3`. Se calcula sobre la media del condado, no por celda.
- **Redundancia:** `et_mm` del paquete `vegetacion` sale del mismo `Evap` de NLDAS-2 Noah (sustituto de
  MOD16A2): `et_nldas_mm` y `et_mm` son la misma magnitud con la misma fuente. Anotado en
  `loop/notes/decisiones.md`.

## Problemas conocidos

- NLDAS-2 Noah no simula riego ni drenaje con caños (tile): en condados muy drenados del Corn Belt
  la humedad y la escorrentía del modelo pueden diferir de lo observado.
- Las salidas de NLDAS-2 mensual se publican con algunos meses de retraso; si un mes no estaba al
  bajar, queda vacío hasta volver a correr `download.py`.
"""


def main() -> None:
    t0 = time.time()
    cfg = cargar_config()
    y0, y1 = int(cfg["periodo"]["anio_inicio"]), int(cfg["periodo"]["anio_fin"])
    b0, b1 = (int(str(x)[:4]) for x in cfg["periodo"]["anomalias_base"])
    gdf = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg").sort_values("fips").reset_index(drop=True)
    gdf = gdf.to_crs("EPSG:4326")
    archivos = sorted(RAW.rglob("*.nc"))
    if not archivos:
        raise SystemExit("no hay archivos en data/raw/nldas/")
    fips = gdf["fips"].astype(str).str.zfill(5).values
    partes = []
    for sub, arch in grupos_archivos(archivos, gdf):
        with xr.open_dataset(arch[0]) as d0:
            lat, lon = d0["lat"].values.astype(float), d0["lon"].values.astype(float)
        w = pesos(sub, lat, lon)
        fips_g = sub["fips"].astype(str).str.zfill(5).values
        for p in arch:
            mes, v = leer(p, lat, lon)
            q = v["Qs"] + v["Qsb"]
            partes.append(pd.DataFrame({
                "fips": fips_g, "mes": mes,
                "sm_0_10cm_m3m3": media(w, v["SoilM_0_10cm"]) / 100.0,
                "sm_0_100cm_m3m3": media(w, v["SoilM_0_100cm"]) / 1000.0,
                "et_nldas_mm": media(w, v["Evap"]),
                "escorrentia_nldas_mm": media(w, q),
                "swe_nldas_mm": media(w, v["SWE"]),
            }))
    m = pd.concat(partes, ignore_index=True)
    print(f"lectura y medias: {time.time() - t0:.0f}s, {len(archivos)} meses")
    m["anio"] = m["mes"].str[:4].astype(int)
    m["mm"] = m["mes"].str[5:7]
    base = m[(m["anio"] >= b0) & (m["anio"] <= b1)]
    clim = base.groupby(["fips", "mm"])["sm_0_100cm_m3m3"].agg(mu="mean", sd="std", n="count").reset_index()
    m = m.merge(clim, on=["fips", "mm"], how="left")
    m["sm_0_100cm_anom_z"] = ((m["sm_0_100cm_m3m3"] - m["mu"]) / m["sd"]).where((m["sd"] > 0) & (m["n"] >= 20))
    m = m[(m["anio"] >= y0) & (m["anio"] <= y1)]
    # grilla completa condado x mes del período: los meses que no estén en raw quedan vacíos
    meses = pd.period_range(f"{y0}-01", f"{y1}-12", freq="M").strftime("%Y-%m")
    full = pd.MultiIndex.from_product([sorted(fips), meses], names=["fips", "mes"]).to_frame(index=False)
    m = full.merge(m.drop(columns=["anio"]), on=["fips", "mes"], how="left")
    m["anio"] = m["mes"].str[:4].astype(int)
    m = m[["fips", "anio", "mes"] + COLS].sort_values(["fips", "mes"]).reset_index(drop=True)
    OUT.mkdir(parents=True, exist_ok=True)
    s = m.copy()
    for c, d in DEC.items():
        s[c] = s[c].map(lambda x, d=d: "" if pd.isna(x) else f"{x:.{d}f}")
    s.to_csv(OUT / "nldas_mensual.csv", index=False, encoding="utf-8", lineterminator="\n")
    CARD.parent.mkdir(parents=True, exist_ok=True)
    CARD.write_text(TEXTO.replace("{tabla}", tabla_card(m)), encoding="utf-8", newline="\n")
    print(f"nldas_mensual.csv: {len(m)} filas; total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
