"""Procesamiento del paquete lotes (CLAUDE.md §6.6). No baja nada: lee data/raw y data/reference.

Salidas en data/processed/lotes/: lotes.csv, lotes.gpkg, pixeles.csv, lotes_anual.csv,
cultivo_px_anual.csv, y la tabla del data card (docs/datasets/lotes.md).

Uso: python src/lotes/process.py
"""
from __future__ import annotations

import math
import re
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import shapely
from pyproj import Transformer
from rasterio.windows import from_bounds

import terreno

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw"
REF = RAIZ / "data" / "reference"
OUT = RAIZ / "data" / "processed" / "lotes"
CARD = RAIZ / "docs" / "datasets" / "lotes.md"

CSB_VENTANA = "2018-2025"
ANIOS_CSB = list(range(2018, 2026))
ANIOS_CDL = list(range(2008, 2026))
ANIOS_10M = (2024, 2025)  # CDL nativo de 10 m: clase mayoritaria del bloque 3×3 y su fracción
PASO = 30.0

# Paisajes del plan (CLAUDE.md §6.6). Wright (19197) queda afuera: no tiene pct_riego en el censo 2022.
PAISAJES = {
    "depresiones": {"lotes": 3, "condados": ["19169", "19079"], "relieve_min": 3.0, "orden": "relieve_mediana"},
    "lomas_loess": {"lotes": 3, "condados": ["19047", "19165"], "relieve_min": 3.0, "orden": "relieve_mediana"},
    "llanura_control": {"lotes": 2, "condados": ["17019"], "relieve_min": None, "orden": "relieve_asc"},
    "indiana": {"lotes": 2, "condados": ["18157"], "relieve_min": None, "orden": "compacidad_desc"},
}
AREA_HA = (30.0, 120.0)
COMPACIDAD_MIN = 0.6
N_PX_INT_MIN = 300
N_ANIOS_MS_MIN = 6
RIEGO_MAX = 5.0

A_4326 = Transformer.from_crs(5070, 4326, always_xy=True)


def t(msg: str, t0: list[float]) -> None:
    ahora = time.time()
    print(f"[{ahora - t0[0]:6.1f} s] {msg}", flush=True)


# ---------------------------------------------------------------- entradas

def leer_csb() -> gpd.GeoDataFrame:
    partes = []
    for f in sorted((RAW / "lotes" / "csb").glob(f"csb_{CSB_VENTANA}_*.gpkg")):
        g = gpd.read_file(f)
        if g.crs is None or g.crs.to_epsg() != 5070:
            g = g.to_crs(5070)
        partes.append(g)
    g = pd.concat(partes, ignore_index=True)
    g["fips"] = g["STATEFIPS"].astype(str).str.zfill(2) + g["CNTYFIPS"].astype(str).str.zfill(3)
    g["CSBID"] = g["CSBID"].astype(str)
    return gpd.GeoDataFrame(g, geometry="geometry", crs=5070)


def riego_por_condado() -> pd.DataFrame:
    c = pd.read_csv(RAIZ / "data" / "processed" / "cultivos" / "practicas_censo.csv", dtype={"fips": str})
    c = c[c["anio_censo"] == c["anio_censo"].max()][["fips", "anio_censo", "pct_riego"]]
    return c.set_index("fips")


class Dem:
    """NASADEM 1" (EPSG:4326) de data/raw/suelo_terreno/nasadem, con muestreo bilineal."""

    def __init__(self):
        self.dir = RAW / "suelo_terreno" / "nasadem"
        self.cache: dict[str, rasterio.io.DatasetReader] = {}

    def _tesela(self, lon: float, lat: float) -> str:
        return f"NASADEM_HGT_n{int(math.floor(lat)):02d}w{int(math.ceil(-lon)):03d}.tif"

    def muestrear(self, lon: np.ndarray, lat: np.ndarray) -> np.ndarray:
        out = np.full(len(lon), np.nan)
        nombres = np.array([self._tesela(a, b) for a, b in zip(lon, lat)])
        for n in np.unique(nombres):
            if n not in self.cache:
                p = self.dir / n
                if not p.exists():
                    continue
                self.cache[n] = rasterio.open(p)
            ds = self.cache[n]
            m = nombres == n
            fil, col = ~ds.transform * (lon[m], lat[m])
            fil, col = np.asarray(col) - 0.5, np.asarray(fil) - 0.5  # fila, columna en centros de píxel
            r0, c0 = np.floor(fil).astype(int), np.floor(col).astype(int)
            r0, c0 = np.clip(r0, 0, ds.height - 2), np.clip(c0, 0, ds.width - 2)
            win = rasterio.windows.Window(c0.min(), r0.min(), c0.max() - c0.min() + 2, r0.max() - r0.min() + 2)
            a = ds.read(1, window=win).astype(float)
            if ds.nodata is not None:
                a[a == ds.nodata] = np.nan
            rr, cc = r0 - win.row_off, c0 - win.col_off
            fy, fx = fil - r0, col - c0
            v = (a[rr, cc] * (1 - fy) * (1 - fx) + a[rr, cc + 1] * (1 - fy) * fx
                 + a[rr + 1, cc] * fy * (1 - fx) + a[rr + 1, cc + 1] * fy * fx)
            out[m] = v
        return out


COLS_TERRENO = ["elevacion_m", "pendiente_pct", "aspecto_grados", "curv_plan", "curv_perfil", "tpi_90m_m",
                "tpi_300m_m", "twi", "prof_depresion_m"]


def teselas_dem(lon: np.ndarray, lat: np.ndarray) -> list[Path]:
    d = RAW / "suelo_terreno" / "nasadem"
    m = 0.04
    rutas = set()
    for a in (lon.min() - m, lon.max() + m):
        for b in (lat.min() - m, lat.max() + m):
            p = d / f"NASADEM_HGT_n{int(math.floor(b)):02d}w{int(math.ceil(-a)):03d}.tif"
            if p.exists():
                rutas.add(p)
    return sorted(rutas)


# ---------------------------------------------------------------- píxeles

def pixeles_de(geom) -> pd.DataFrame:
    """Centros de la grilla de 30 m (múltiplos de 30) que caen dentro del polígono."""
    x0, y0, x1, y1 = geom.bounds
    cx0, cx1 = math.ceil(x0 / PASO) * PASO, math.floor(x1 / PASO) * PASO
    cy0, cy1 = math.ceil(y0 / PASO) * PASO, math.floor(y1 / PASO) * PASO
    xs = np.arange(cx0, cx1 + 1, PASO)
    ys = np.arange(cy1, cy0 - 1, -PASO)  # filas de norte a sur
    X, Y = np.meshgrid(xs, ys)
    fila, col = np.meshgrid(np.arange(len(ys)), np.arange(len(xs)), indexing="ij")
    X, Y, fila, col = X.ravel(), Y.ravel(), fila.ravel(), col.ravel()
    shapely.prepare(geom)
    dentro = shapely.contains_xy(geom, X, Y)
    df = pd.DataFrame({"x_m": X[dentro], "y_m": Y[dentro],
                       "px_id": (fila[dentro] * len(xs) + col[dentro]).astype(int)})
    return df


def detalle_pixeles(geom, df: pd.DataFrame) -> pd.DataFrame:
    interior_geom = geom.buffer(-PASO)
    pts = shapely.points(df["x_m"].values, df["y_m"].values)
    df = df.copy()
    df["interior"] = shapely.contains(interior_geom, pts).astype(int) if not interior_geom.is_empty else 0
    df["dist_borde_m"] = shapely.distance(geom.boundary, pts)
    h = PASO / 2
    cajas = shapely.box(df["x_m"] - h, df["y_m"] - h, df["x_m"] + h, df["y_m"] + h)
    df["frac_en_lote"] = shapely.area(shapely.intersection(cajas, geom)) / (PASO * PASO)
    lon, lat = A_4326.transform(df["x_m"].values, df["y_m"].values)
    df["lon"], df["lat"] = lon, lat
    return df


# ---------------------------------------------------------------- selección

def candidatos(csb: gpd.GeoDataFrame, riego: pd.DataFrame, dem: Dem, t0) -> pd.DataFrame:
    g = csb.copy()
    g["area_ha"] = g.geometry.area / 1e4
    g["compacidad"] = 4 * math.pi * g.geometry.area / g.geometry.length ** 2
    cols = [f"CDL{a}" for a in ANIOS_CSB]
    g["n_anios_maiz_soja"] = g[cols].apply(pd.to_numeric, errors="coerce").isin([1, 5]).sum(axis=1)
    g["pct_riego_condado"] = g["fips"].map(riego["pct_riego"])
    g["anio_censo_riego"] = g["fips"].map(riego["anio_censo"])
    m = (g["area_ha"].between(*AREA_HA) & (g["compacidad"] >= COMPACIDAD_MIN)
         & (g["n_anios_maiz_soja"] >= N_ANIOS_MS_MIN) & (g["pct_riego_condado"] < RIEGO_MAX))
    g = g[m].copy()
    t(f"candidatos por área, forma, rotación y riego: {len(g)}", t0)
    n_px, n_int, relieve = [], [], []
    for geom in g.geometry:
        px = pixeles_de(geom)
        inter = geom.buffer(-PASO)
        n_px.append(len(px))
        n_int.append(int(shapely.contains_xy(inter, px["x_m"].values, px["y_m"].values).sum()) if len(px) else 0)
        lon, lat = A_4326.transform(px["x_m"].values, px["y_m"].values)
        z = dem.muestrear(np.asarray(lon), np.asarray(lat))
        relieve.append(float(np.nanmax(z) - np.nanmin(z)) if np.isfinite(z).any() else np.nan)
    g["n_px"], g["n_px_interior"], g["relieve_m"] = n_px, n_int, relieve
    g = g[g["n_px_interior"] >= N_PX_INT_MIN]
    t(f"candidatos con >= {N_PX_INT_MIN} píxeles interiores: {len(g)}", t0)
    return g


def elegir(cand: pd.DataFrame) -> gpd.GeoDataFrame:
    elegidos = []
    for paisaje, p in PAISAJES.items():
        s = cand[cand["fips"].isin(p["condados"])].copy()
        if p["relieve_min"] is not None:
            s = s[s["relieve_m"] > p["relieve_min"]]
        if p["orden"] == "relieve_mediana":
            s["_dist"] = (s["relieve_m"] - s["relieve_m"].median()).abs().round(6)
            s = s.sort_values(["_dist", "CSBID"], ascending=[True, True])
            regla = f"relieve NASADEM más cercano a la mediana de los candidatos ({s['relieve_m'].median():.2f} m)"
        elif p["orden"] == "relieve_asc":
            s = s.sort_values(["relieve_m", "CSBID"], ascending=[True, True])
            regla = "menor relieve NASADEM (máx − mín), llanura plana"
        else:
            s = s.sort_values(["compacidad", "CSBID"], ascending=[False, True])
            regla = "mayor compacidad (Polsby-Popper)"
        n = len(s)
        s = s.head(p["lotes"]).copy()
        s["paisaje"] = paisaje
        s["n_candidatos"] = n
        s["motivo"] = [f"{paisaje}: puesto {i + 1} por {regla} entre {n} candidatos de {'/'.join(p['condados'])} "
                       f"que cumplen 30-120 ha, compacidad >= {COMPACIDAD_MIN}, >= {N_PX_INT_MIN} píxeles interiores, "
                       f"maíz o soja >= {N_ANIOS_MS_MIN} de 8 años, riego < {RIEGO_MAX:g} %"
                       + (f" y relieve > {p['relieve_min']:g} m" if p["relieve_min"] is not None else "")
                       for i in range(len(s))]
        elegidos.append(s)
    out = pd.concat(elegidos, ignore_index=True)
    out["id_lote"] = out["fips"] + "_" + out["CSBID"].map(lambda v: re.sub(r"[^0-9A-Za-z]", "", v))
    return gpd.GeoDataFrame(out, geometry="geometry", crs=5070)


# ---------------------------------------------------------------- CDL por píxel

def indice_cdl() -> dict[int, list[tuple[Path, tuple]]]:
    idx: dict[int, list] = {}
    for f in sorted((RAW / "cultivos" / "cdl" / "teselas").glob("*_30m_cdls_*.tif")):
        anio = int(f.name[:4])
        with rasterio.open(f) as ds:
            idx.setdefault(anio, []).append((f, tuple(ds.bounds)))
    return idx


def cdl_pixeles(px: pd.DataFrame, idx) -> pd.DataFrame:
    grupos = pd.read_csv(REF / "clases_cdl.csv").set_index("codigo")["grupo"]
    filas = []
    for anio in ANIOS_CDL:
        clase = np.full(len(px), -1, dtype=int)
        for f, (x0, y0, x1, y1) in idx.get(anio, []):
            m = (px["x_m"].values > x0) & (px["x_m"].values < x1) & (px["y_m"].values > y0) & (px["y_m"].values < y1)
            if not m.any():
                continue
            with rasterio.open(f) as ds:
                xs, ys = px["x_m"].values[m], px["y_m"].values[m]
                win = from_bounds(xs.min() - 15, ys.min() - 15, xs.max() + 15, ys.max() + 15, ds.transform)
                win = win.round_offsets().round_lengths()
                a = ds.read(1, window=win)
                tr = ds.window_transform(win)
                c, r = ~tr * (xs, ys)
                clase[m] = a[np.floor(r).astype(int), np.floor(c).astype(int)]
        d = px[["fips", "id_lote", "px_id"]].copy()
        d["anio"] = anio
        d["cdl_clase"] = clase
        d["frac_clase"] = np.nan
        if anio in ANIOS_10M:
            for lid in d["id_lote"].unique():
                f10 = RAW / "lotes" / "cdl10m" / f"cdl10m_{anio}_{lid}.tif"
                if not f10.exists():
                    continue
                m = (d["id_lote"] == lid).values
                with rasterio.open(f10) as ds:
                    a = ds.read(1)
                    c, r = ~ds.transform * (px["x_m"].values[m], px["y_m"].values[m])
                r0, c0 = np.round(r - 1.5).astype(int), np.round(c - 1.5).astype(int)  # esquina del bloque 3×3
                bloques = np.stack([a[r0 + i, c0 + j] for i in range(3) for j in range(3)], axis=1)
                mayor, frac = [], []
                for b in bloques:
                    v, n = np.unique(b, return_counts=True)
                    k = int(np.argmax(n))  # empates: el código más bajo (np.unique ordena)
                    mayor.append(int(v[k]))
                    frac.append(n[k] / 9.0)
                d.loc[m, "cdl_clase"] = mayor
                d.loc[m, "frac_clase"] = np.round(frac, 4)
        filas.append(d)
    out = pd.concat(filas, ignore_index=True)
    out.loc[out["cdl_clase"] <= 0, "cdl_clase"] = -1  # 0 = background (sin dato) → vacío
    out["cultivo"] = out["cdl_clase"].map(grupos).where(out["cdl_clase"] > 0)
    out["cultivo"] = out["cultivo"].fillna("")
    out["cdl_clase"] = out["cdl_clase"].astype("Int64").where(out["cdl_clase"] > 0)
    return out


def resumen_anual(cp: pd.DataFrame, px: pd.DataFrame, lotes: pd.DataFrame) -> pd.DataFrame:
    grupos = pd.read_csv(REF / "clases_cdl.csv").set_index("codigo")["grupo"]
    inter = px.loc[px["interior"] == 1, ["id_lote", "px_id"]]
    c = cp[cp["cultivo"] != ""].merge(inter, on=["id_lote", "px_id"])
    filas = []
    for (fips, lote, anio), s in c.groupby(["fips", "id_lote", "anio"], sort=True):
        cuenta = s["cultivo"].value_counts()
        maxc = cuenta.max()
        principal = sorted(cuenta[cuenta == maxc].index)[0]
        clases = s.loc[s["cultivo"] == principal, "cdl_clase"].astype(int).value_counts()
        clase = int(sorted(clases[clases == clases.max()].index)[0])
        pct = 100.0 * maxc / len(s)
        fila = {"fips": fips, "id_lote": lote, "anio": int(anio), "cultivo_principal": principal,
                "cdl_clase_principal": clase, "pct_px_cultivo_principal": round(pct, 2),
                "lote_partido": int(pct < 90), "cultivo_csb": "", "pct_px_igual_csb": np.nan}
        if anio in ANIOS_CSB:
            csb_clase = pd.to_numeric(lotes.loc[lotes["id_lote"] == lote, f"CDL{anio}"].iloc[0], errors="coerce")
            if pd.notna(csb_clase):
                fila["cultivo_csb"] = grupos.get(int(csb_clase), "otro")
                fila["pct_px_igual_csb"] = round(100.0 * (s["cdl_clase"].astype(int) == int(csb_clase)).mean(), 2)
        filas.append(fila)
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- data card

DESCR = {
    ("lotes.csv", "paisaje"): ("paisaje del plan (depresiones, lomas_loess, llanura_control, indiana)", "", "CLAUDE.md §6.6"),
    ("lotes.csv", "csb_ventana"): ("ventana de 8 años del CSB de donde sale el polígono", "", "USDA NASS CSB"),
    ("lotes.csv", "area_ha"): ("superficie del polígono (EPSG:5070)", "ha", "USDA NASS CSB"),
    ("lotes.csv", "area_ac"): ("superficie del polígono", "ac", "USDA NASS CSB"),
    ("lotes.csv", "lat_centroide"): ("latitud del centroide", "grados", "USDA NASS CSB"),
    ("lotes.csv", "lon_centroide"): ("longitud del centroide", "grados", "USDA NASS CSB"),
    ("lotes.csv", "compacidad"): ("Polsby-Popper 4πA/P²", "", "USDA NASS CSB"),
    ("lotes.csv", "n_px"): ("píxeles de 30 m con centro dentro del lote", "píxeles", "grilla mascara_agricola.tif"),
    ("lotes.csv", "n_px_interior"): ("píxeles con centro dentro del lote achicado 30 m", "píxeles", "grilla mascara_agricola.tif"),
    ("lotes.csv", "n_anios_maiz_soja"): ("años de la ventana CSB con maíz o soja (CDL<año> del CSB)", "años", "USDA NASS CSB"),
    ("lotes.csv", "pct_riego_condado"): ("% de tierras de cultivo con riego, censo más reciente", "%", "USDA NASS Censo (practicas_censo.csv)"),
    ("lotes.csv", "relieve_3dep_m"): ("máxima menos mínima de elevacion_3dep_m en los píxeles del lote", "m", "USGS 3DEP"),
    ("lotes.csv", "relieve_m"): ("máxima menos mínima de NASADEM (bilineal en la grilla de 30 m) dentro del lote", "m", "NASA NASADEM"),
    ("lotes.csv", "motivo"): ("regla de selección y puesto", "", "este paquete"),
    ("lotes.csv", "n_candidatos"): ("polígonos que cumplían todos los criterios en ese paisaje", "lotes", "USDA NASS CSB"),
    ("lotes_anual.csv", "cultivo_principal"): ("grupo de cultivo más frecuente en los píxeles interiores", "", "USDA NASS CDL"),
    ("lotes_anual.csv", "cdl_clase_principal"): ("clase CDL más frecuente dentro del grupo principal", "código", "USDA NASS CDL"),
    ("lotes_anual.csv", "pct_px_cultivo_principal"): ("% de píxeles interiores con el grupo principal", "%", "USDA NASS CDL"),
    ("lotes_anual.csv", "lote_partido"): ("1 si pct_px_cultivo_principal < 90", "", "USDA NASS CDL"),
    ("lotes_anual.csv", "cultivo_csb"): ("grupo del cultivo que el CSB asigna al lote ese año (solo 2018-2025)", "", "USDA NASS CSB"),
    ("lotes_anual.csv", "pct_px_igual_csb"): ("% de píxeles interiores cuya clase CDL es la del CSB", "%", "USDA NASS CDL y CSB"),
    ("pixeles.csv", "x_m"): ("x del centro del píxel (EPSG:5070)", "m", "grilla mascara_agricola.tif"),
    ("pixeles.csv", "y_m"): ("y del centro del píxel (EPSG:5070)", "m", "grilla mascara_agricola.tif"),
    ("pixeles.csv", "lon"): ("longitud del centro", "grados", "grilla mascara_agricola.tif"),
    ("pixeles.csv", "lat"): ("latitud del centro", "grados", "grilla mascara_agricola.tif"),
    ("pixeles.csv", "dist_borde_m"): ("distancia del centro al borde del polígono", "m", "USDA NASS CSB"),
    ("pixeles.csv", "interior"): ("1 si el centro cae en el lote achicado 30 m", "", "USDA NASS CSB"),
    ("pixeles.csv", "frac_en_lote"): ("fracción del píxel de 30 m dentro del polígono", "", "USDA NASS CSB"),
    ("terreno_px.csv", "elevacion_m"): ("elevación NASADEM (sin suavizar), bilineal a 30 m", "m", "NASA NASADEM"),
    ("terreno_px.csv", "pendiente_pct"): ("pendiente sobre el DEM suavizado (gauss sigma 1 celda)", "%", "NASA NASADEM"),
    ("terreno_px.csv", "aspecto_grados"): ("dirección de máxima bajada desde el norte, horario; vacío con pendiente 0", "grados", "NASA NASADEM"),
    ("terreno_px.csv", "curv_plan"): ("curvatura en planta (Zevenbergen y Thorne)", "1/m", "NASA NASADEM"),
    ("terreno_px.csv", "curv_perfil"): ("curvatura de perfil (Zevenbergen y Thorne)", "1/m", "NASA NASADEM"),
    ("terreno_px.csv", "tpi_90m_m"): ("elevación menos la media en un radio de 90 m", "m", "NASA NASADEM"),
    ("terreno_px.csv", "tpi_300m_m"): ("elevación menos la media en un radio de 300 m", "m", "NASA NASADEM"),
    ("terreno_px.csv", "twi"): ("ln(área específica aportante / tan pendiente), D8 en ventana lote + 2,5 km", "", "NASA NASADEM"),
    ("drenaje_px.csv", "drenado_canos"): ("1 si la celda AgTile-US que contiene el centro del píxel está drenada con caños", "", "Valayamkunnath et al. 2020 (AgTile-US)"),
    ("terreno_px.csv", "elevacion_3dep_m"): ("elevación USGS 3DEP (10 m, media de 3 × 3 celdas en el píxel de 30 m)", "m", "USGS 3DEP"),
    ("terreno_px.csv", "pendiente_3dep_pct"): ("pendiente 3DEP a 10 m (gauss sigma 10 m), media en el píxel de 30 m", "%", "USGS 3DEP"),
    ("terreno_px.csv", "tpi_90m_3dep_m"): ("elevación menos la media a <= 90 m, 3DEP 10 m, media en el píxel", "m", "USGS 3DEP"),
    ("terreno_px.csv", "twi_3dep"): ("TWI D8 sobre 3DEP 10 m en ventana lote + 2,52 km, media en el píxel", "", "USGS 3DEP"),
    ("terreno_px.csv", "prof_depresion_3dep_m"): ("relleno priority-flood menos DEM, 3DEP 10 m, media en el píxel", "m", "USGS 3DEP"),
    ("terreno_px.csv", "prof_depresion_m"): ("DEM con depresiones rellenas (priority-flood) menos DEM", "m", "NASA NASADEM"),
    ("cultivo_px_anual.csv", "cdl_clase"): ("clase CDL del píxel (teselas de 30 m de data/raw/cultivos)", "código", "USDA NASS CDL"),
    ("cultivo_px_anual.csv", "cultivo"): ("grupo de la clase según data/reference/clases_cdl.csv", "", "USDA NASS CDL"),
    ("cultivo_px_anual.csv", "frac_clase"): ("fracción del píxel con la clase mayoritaria (CDL de 10 m, 2024-2025)", "", "USDA NASS CDL 10 m"),
    ("suelo_px.csv", "frac_mukey"): ("fracción de las 9 subceldas de 10 m del píxel con ese mukey (polígonos SSURGO rasterizados)", "", "USDA NRCS SSURGO (SDA)"),
    ("suelo_mukey.csv", "muname"): ("nombre de la unidad cartográfica", "", "USDA NRCS SSURGO mapunit"),
    ("suelo_mukey.csv", "aws0_100_mm"): ("agua disponible 0-100 cm (aws0100wta × 10)", "mm", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "aws0_150_mm"): ("agua disponible 0-150 cm (aws0150wta × 10)", "mm", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "soc0_30_gm2"): ("carbono orgánico 0-30 cm: Σ espesor · MO · 0,58 · densidad · (1 − fragmentos), media por comppct_r", "g C/m²", "USDA NRCS SSURGO chorizon"),
    ("suelo_mukey.csv", "nccpi_general"): ("NCCPI v3 general, media por comppct_r", "", "USDA NRCS SSURGO cointerp"),
    ("suelo_mukey.csv", "nccpi_maiz"): ("NCCPI submodelo maíz, media por comppct_r", "", "USDA NRCS SSURGO cointerp"),
    ("suelo_mukey.csv", "nccpi_soja"): ("NCCPI submodelo soja, media por comppct_r", "", "USDA NRCS SSURGO cointerp"),
    ("suelo_mukey.csv", "clase_drenaje"): ("clase de drenaje del componente dominante (drclassdcd)", "", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "clase_drenaje_mas_humeda"): ("clase de drenaje más húmeda (drclasswettest)", "", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "grupo_hidrologico"): ("grupo hidrológico dominante (hydgrpdcd)", "", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "pct_componentes_hidricos"): ("% de componentes hídricos (hydclprs)", "%", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "pct_encharcamiento"): ("% de componentes con encharcamiento (pondfreqprs)", "%", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "frec_inundacion"): ("frecuencia de inundación dominante (flodfreqdcd traducida)", "", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "napa_min_cm"): ("profundidad mínima anual de la napa (wtdepannmin)", "cm", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "pendiente_dcd_pct"): ("pendiente del componente dominante (slopegraddcp)", "%", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "pendiente_comp_pct"): ("pendiente media ponderada de los componentes (slopegradwta)", "%", "USDA NRCS SSURGO muaggatt"),
    ("suelo_mukey.csv", "clase_erosion"): ("clase de erosión (erocl) del componente dominante", "", "USDA NRCS SSURGO component"),
    ("suelo_mukey.csv", "pct_comp_dominante"): ("comppct_r del componente dominante", "%", "USDA NRCS SSURGO component"),
    ("suelo_mukey.csv", "materia_organica_pct"): ("materia orgánica 0-30 cm (por espesor y comppct_r)", "%", "USDA NRCS SSURGO chorizon"),
    ("suelo_mukey.csv", "arcilla_pct"): ("arcilla 0-30 cm", "%", "USDA NRCS SSURGO chorizon"),
    ("suelo_mukey.csv", "arena_pct"): ("arena 0-30 cm", "%", "USDA NRCS SSURGO chorizon"),
    ("suelo_mukey.csv", "limo_pct"): ("limo 0-30 cm", "%", "USDA NRCS SSURGO chorizon"),
    ("suelo_mukey.csv", "ph_agua"): ("pH 1:1 en agua 0-30 cm", "pH", "USDA NRCS SSURGO chorizon"),
    ("suelo_mukey.csv", "factor_k_rusle"): ("factor K (kwfact) del horizonte superficial", "t·ha·h/(ha·MJ·mm)", "USDA NRCS SSURGO chorizon"),
    ("vegetacion_px_obs.csv", "producto"): ("landsat_c2_l2 o hls_s30", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "sensor"): ("L5, L7, L8, L9, S2A, S2B o S2C", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "refl_blue"): ("reflectancia azul", "reflectancia", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "refl_green"): ("reflectancia verde", "reflectancia", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "refl_red"): ("reflectancia roja", "reflectancia", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "refl_nir"): ("reflectancia NIR (Landsat nir08, HLS B8A)", "reflectancia", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "refl_swir1"): ("reflectancia SWIR 1,6 µm", "reflectancia", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "refl_swir2"): ("reflectancia SWIR 2,2 µm", "reflectancia", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "ndvi"): ("(nir − red) / (nir + red)", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "evi2"): ("2,5 (nir − red) / (nir + 2,4 red + 1)", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "gcvi"): ("nir / green − 1", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "ndmi"): ("(nir − swir1) / (nir + swir1)", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "slc_off"): ("1 si Landsat 7 desde 2003-05-31", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_obs.csv", "qa_valor"): ("valor crudo de QA_PIXEL (Landsat) o Fmask (HLS)", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_anual.csv", "ndvi_max"): ("NDVI máximo del año (Landsat, mar-nov)", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_anual.csv", "doy_ndvi_max"): ("día del año del NDVI máximo", "día", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_anual.csv", "evi2_max"): ("EVI2 máximo del año (Landsat)", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_anual.csv", "doy_evi2_max"): ("día del año del EVI2 máximo", "día", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_anual.csv", "ndvi_media_jul_ago"): ("NDVI medio de las observaciones de julio-agosto (Landsat)", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_anual.csv", "n_obs_mar_nov"): ("observaciones despejadas Landsat de marzo a noviembre", "obs", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_anual.csv", "n_obs_may_jun"): ("observaciones despejadas Landsat de mayo-junio", "obs", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_anual.csv", "n_obs_jul_ago"): ("observaciones despejadas Landsat de julio-agosto", "obs", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_anual.csv", "ndvi_max_s2"): ("NDVI máximo del año con HLS S30", "", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("vegetacion_px_anual.csv", "n_obs_jul_ago_s2"): ("observaciones despejadas HLS S30 de julio-agosto", "obs", "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)"),
    ("suelo_desnudo_px.csv", "refl_blue_mar_may"): ("mediana de refl_blue con NDVI < 0,25, 15 mar-15 may (Landsat)", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "refl_red_mar_may"): ("mediana de refl_red con NDVI < 0,25, 15 mar-15 may (Landsat)", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "refl_nir_mar_may"): ("mediana de refl_nir con NDVI < 0,25, 15 mar-15 may (Landsat)", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "refl_swir1_mar_may"): ("mediana de refl_swir1 con NDVI < 0,25, 15 mar-15 may (Landsat)", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "refl_swir2_mar_may"): ("mediana de refl_swir2 con NDVI < 0,25, 15 mar-15 may (Landsat)", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "nbr2_mar_may"): ("(swir1 − swir2)/(swir1 + swir2) de las medianas, 15 mar-15 may", "", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "n_obs_mar_may"): ("observaciones con NDVI < 0,25, 15 mar-15 may", "obs", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "refl_blue_oct_nov"): ("mediana de refl_blue con NDVI < 0,25, oct-nov (Landsat)", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "refl_red_oct_nov"): ("mediana de refl_red con NDVI < 0,25, oct-nov (Landsat)", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "refl_nir_oct_nov"): ("mediana de refl_nir con NDVI < 0,25, oct-nov (Landsat)", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "refl_swir1_oct_nov"): ("mediana de refl_swir1 con NDVI < 0,25, oct-nov (Landsat)", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "refl_swir2_oct_nov"): ("mediana de refl_swir2 con NDVI < 0,25, oct-nov (Landsat)", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "nbr2_oct_nov"): ("(swir1 − swir2)/(swir1 + swir2) de las medianas, oct-nov", "", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px.csv", "n_obs_oct_nov"): ("observaciones con NDVI < 0,25, oct-nov", "obs", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px_compuesto.csv", "refl_blue"): ("mediana multianual (todos los años) de refl_blue con NDVI < 0,25 en ambas ventanas", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px_compuesto.csv", "refl_red"): ("mediana multianual (todos los años) de refl_red con NDVI < 0,25 en ambas ventanas", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px_compuesto.csv", "refl_nir"): ("mediana multianual (todos los años) de refl_nir con NDVI < 0,25 en ambas ventanas", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px_compuesto.csv", "refl_swir1"): ("mediana multianual (todos los años) de refl_swir1 con NDVI < 0,25 en ambas ventanas", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px_compuesto.csv", "refl_swir2"): ("mediana multianual (todos los años) de refl_swir2 con NDVI < 0,25 en ambas ventanas", "reflectancia", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px_compuesto.csv", "nbr2"): ("NBR2 de las medianas multianuales", "", "USGS/NASA Landsat C2 L2"),
    ("suelo_desnudo_px_compuesto.csv", "n_obs"): ("observaciones de suelo desnudo de todos los años", "obs", "USGS/NASA Landsat C2 L2"),
    ("clima_lote_diario.csv", "prec_power_mm"): ("precipitación PRECTOTCORR", "mm", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_diario.csv", "tmax_c"): ("temperatura máxima a 2 m", "°C", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_diario.csv", "tmin_c"): ("temperatura mínima a 2 m", "°C", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_diario.csv", "tmed_c"): ("temperatura media a 2 m", "°C", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_diario.csv", "hr_pct"): ("humedad relativa a 2 m", "%", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_diario.csv", "viento_ms"): ("viento a 2 m", "m/s", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_diario.csv", "rad_mj_m2"): ("radiación global ALLSKY_SFC_SW_DWN", "MJ/m²/día", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_diario.csv", "eto_pm_mm"): ("ETo FAO-56 Penman-Monteith", "mm", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_diario.csv", "deficit_mm"): ("prec_power_mm − eto_pm_mm", "mm", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_diario.csv", "prec_imerg_mm"): ("precipitación IMERG de la celda de 0,1° del centroide", "mm", "GPM IMERG Final vía POWER (IMERG_PRECTOT)"),
    ("clima_lote_diario.csv", "sm_rootzone_m3m3"): ("SMAP L4 zona radicular, celda de 9 km del centroide", "m³/m³", "NASA SMAP L4 vía USDA Crop-CASMA (paquete agua)"),
    ("clima_lote_diario.csv", "sm_surface_m3m3"): ("SMAP L4 superficial, celda de 9 km del centroide", "m³/m³", "NASA SMAP L4 vía USDA Crop-CASMA (paquete agua)"),
    ("clima_lote_anual.csv", "prec_temporada_mm"): ("lluvia abril-septiembre", "mm", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "prec_abr_mm"): ("lluvia de abril", "mm", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "prec_may_mm"): ("lluvia de mayo", "mm", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "prec_jul_mm"): ("lluvia de julio", "mm", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "prec_ago_mm"): ("lluvia de agosto", "mm", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "deficit_temporada_mm"): ("Σ (prec − ETo) abril-septiembre", "mm", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "dias_tmax_gt30_jul"): ("días de julio con tmax > 30 °C", "días", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "tmax_jul_c"): ("tmax media de julio", "°C", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "gdd_temporada"): ("grados día 10/30 °C abril-septiembre", "°C·día", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "prec_invierno_previo_mm"): ("lluvia noviembre del año anterior a marzo", "mm", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "dias_lluvia_gt50_abr_may"): ("días de abril-mayo con lluvia > 50 mm", "días", "NASA POWER (AG), en el centroide del lote"),
    ("clima_lote_anual.csv", "prec_temporada_imerg_mm"): ("lluvia IMERG abril-septiembre", "mm", "GPM IMERG Final vía POWER (IMERG_PRECTOT)"),
    ("clima_lote_anual.csv", "prec_abr_imerg_mm"): ("lluvia IMERG de abril", "mm", "GPM IMERG Final vía POWER (IMERG_PRECTOT)"),
    ("clima_lote_anual.csv", "prec_may_imerg_mm"): ("lluvia IMERG de mayo", "mm", "GPM IMERG Final vía POWER (IMERG_PRECTOT)"),
    ("clima_lote_anual.csv", "prec_jul_imerg_mm"): ("lluvia IMERG de julio", "mm", "GPM IMERG Final vía POWER (IMERG_PRECTOT)"),
    ("clima_lote_anual.csv", "prec_ago_imerg_mm"): ("lluvia IMERG de agosto", "mm", "GPM IMERG Final vía POWER (IMERG_PRECTOT)"),
    ("clima_lote_anual.csv", "dias_lluvia_gt50_abr_may_imerg"): ("días de abril-mayo con IMERG > 50 mm", "días", "GPM IMERG Final vía POWER (IMERG_PRECTOT)"),
    ("clima_lote_anual.csv", "sm_rootzone_temporada_m3m3"): ("SMAP zona radicular media abril-septiembre, celda de 9 km del centroide", "m³/m³", "NASA SMAP L4 vía USDA Crop-CASMA (paquete agua)"),
}


def _rango(df: pd.DataFrame, col: str, temporal: str) -> tuple[str, str, str]:
    lleno = df[col].notna() & (df[col].astype(str) != "")
    falt = f"{100.0 * (1 - lleno.mean()):.2f}"
    if "fecha" in df.columns and lleno.any():
        return str(df.loc[lleno, "fecha"].min()), str(df.loc[lleno, "fecha"].max()), falt
    if temporal == "anual" and lleno.any():
        return str(int(df.loc[lleno, "anio"].min())), str(int(df.loc[lleno, "anio"].max())), falt
    return "", "", falt


def escribir_card(tablas: dict[str, tuple[pd.DataFrame, str]], resumen: list[str]) -> None:
    texto = CARD.read_text(encoding="utf-8") if CARD.exists() else ""
    filas = ["| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |",
             "|---|---|---|---|---|---|---|---|---|"]
    for arch, (df, temporal) in tablas.items():
        for (a, col), (desc, unidad, fuente) in DESCR.items():
            if a != arch or col not in df.columns:
                continue
            d, h, f = _rango(df, col, temporal)
            unidad = unidad or ("texto" if df[col].dtype == object else "adimensional")
            filas.append(f"| {arch} | {col} | {desc} | {unidad} | {fuente} |  | {d} | {h} | {f} |")
    bloque = "<!-- TABLA:INICIO -->\n" + "\n".join(filas) + "\n<!-- TABLA:FIN -->"
    ctrl = "<!-- CONTROLES:INICIO -->\n" + "\n".join(resumen) + "\n<!-- CONTROLES:FIN -->"
    for marca, nuevo in (("TABLA", bloque), ("CONTROLES", ctrl)):
        patron = re.compile(f"<!-- {marca}:INICIO -->.*?<!-- {marca}:FIN -->", re.S)
        if patron.search(texto):
            texto = patron.sub(lambda _: nuevo, texto)
        else:
            texto += "\n" + nuevo + "\n"
    CARD.write_text(texto, encoding="utf-8")



def controles_obs(obs: pd.DataFrame, va: pd.DataFrame, spx: pd.DataFrame, px: pd.DataFrame) -> list[str]:
    ls = obs[obs["producto"] == "landsat_c2_l2"]
    res = ["", "### Observaciones despejadas", "",
           f"- Filas de vegetacion_px_obs.csv: Landsat {int((obs['producto'] == 'landsat_c2_l2').sum())}, "
           f"HLS S30 {int((obs['producto'] == 'hls_s30').sum())} (descarga parcial: ver Problemas conocidos).",
           f"- Píxeles-año (con escenas Landsat bajadas) con menos de 3 observaciones despejadas en julio-agosto: "
           f"{int((va['n_obs_jul_ago'] < 3).sum())} de {len(va)} ({100 * (va['n_obs_jul_ago'] < 3).mean():.1f} %).",
           f"- Mediana de observaciones despejadas Landsat mar-nov por píxel-año: {va['n_obs_mar_nov'].median():.0f}."]
    s12 = ls[ls["anio"] == 2012]
    por_sensor = s12.groupby("sensor").size().to_dict()
    res += ["", "### 2012 y SLC-off", "",
            f"- 2012: observaciones despejadas por sensor {por_sensor if por_sensor else 'ninguna'} "
            "(Landsat 5 terminó en 2011 y Landsat 8 empezó en 2013: 2012 solo tiene Landsat 7 con SLC-off).",
            f"- Observaciones con slc_off = 1: {int(ls['slc_off'].sum())} de {len(ls)}."]
    l7 = ls[ls["slc_off"] == 1]
    if len(l7):
        # % de píxeles del lote sin dato en cada escena L7 SLC-off que tuvo al menos un píxel despejado
        n = px.groupby("id_lote").size()
        f = l7.groupby(["id_lote", "fecha"]).size().reset_index(name="n")
        f["pct_vacio"] = 100 * (1 - f["n"] / f["id_lote"].map(n))
        res.append(f"- Escenas L7 SLC-off con algún píxel despejado: % medio de píxeles del lote sin dato (franjas, "
                   f"nubes o borde) {f['pct_vacio'].mean():.1f} %.")
    k = ["fips", "id_lote", "px_id"]
    a = ls[k + ["fecha", "ndvi"]].assign(f=pd.to_datetime(ls["fecha"]))
    b = obs[obs["producto"] == "hls_s30"][k + ["fecha", "ndvi"]]
    b = b.assign(f=pd.to_datetime(b["fecha"]))
    res += ["", "### Coherencia Landsat–Sentinel-2", ""]
    if len(a) and len(b):
        m = pd.merge_asof(a.sort_values("f"), b.sort_values("f"), on="f", by=k, direction="nearest",
                          tolerance=pd.Timedelta(days=3), suffixes=("_ls", "_s2")).dropna(subset=["ndvi_s2"])
        dif = m["ndvi_ls"] - m["ndvi_s2"]
        res.append(f"- Pares mismo píxel con fechas a 3 días o menos: {len(m)}; NDVI Landsat − HLS S30: media "
                   f"{dif.mean():.4f}, desvío {dif.std():.4f}.")
    else:
        res.append("- Sin pares Landsat–HLS S30 todavía.")
    cub = spx.groupby("id_lote")["frac_mukey"].sum() / px.groupby("id_lote").size()
    nmu = spx.groupby("id_lote")["mukey"].nunique()
    res += ["", "### Cobertura de SSURGO", ""]
    res += [f"- {l}: {100 * cub.get(l, 0):.1f} % del lote con mukey, {int(nmu.get(l, 0))} mukeys" for l in sorted(px["id_lote"].unique())]
    return res

# ---------------------------------------------------------------- main

def main() -> None:
    t0 = [time.time()]
    OUT.mkdir(parents=True, exist_ok=True)
    csb = leer_csb()
    t(f"CSB: {len(csb)} polígonos en {csb['fips'].nunique()} condados", t0)
    dem = Dem()
    cand = candidatos(csb, riego_por_condado(), dem, t0)
    lotes = elegir(cand)
    t(f"lotes elegidos: {len(lotes)}", t0)

    # píxeles
    partes = []
    for _, l in lotes.iterrows():
        d = detalle_pixeles(l.geometry, pixeles_de(l.geometry))
        d.insert(0, "id_lote", l["id_lote"])
        d.insert(0, "fips", l["fips"])
        partes.append(d)
    px = pd.concat(partes, ignore_index=True).sort_values(["fips", "id_lote", "px_id"]).reset_index(drop=True)
    n_px = px.groupby("id_lote").size()
    n_int = px[px["interior"] == 1].groupby("id_lote").size()

    # terreno USGS 3DEP (10 m agregado a 30 m); vacío si falta el recorte del lote
    t3 = []
    for lid, d in px.groupby("id_lote", sort=True):
        e = d[["id_lote", "px_id"]].copy()
        ruta = RAW / "lotes" / "3dep" / f"3dep_10m_{lid}.tif"
        o = terreno.terreno_3dep_lote(ruta, d["x_m"].values.astype(float), d["y_m"].values.astype(float)) if ruta.exists() else {}
        for k in terreno.COLS_3DEP.values():
            e[k] = np.round(o[k], 4) if k in o else np.nan
        t3.append(e)
    ter3 = pd.concat(t3, ignore_index=True)
    rel3 = ter3.groupby("id_lote")["elevacion_3dep_m"].agg(lambda v: v.max() - v.min() if v.notna().any() else np.nan)
    t("terreno 3DEP", t0)

    # tabla de lotes
    cent = lotes.geometry.centroid
    lon, lat = A_4326.transform(cent.x.values, cent.y.values)
    tab = pd.DataFrame({
        "fips": lotes["fips"], "id_lote": lotes["id_lote"], "paisaje": lotes["paisaje"],
        "csb_ventana": CSB_VENTANA, "csbid": lotes["CSBID"],
        "area_ha": lotes["area_ha"].round(4), "area_ac": (lotes["area_ha"] / 0.40468564224).round(4),
        "lat_centroide": np.round(lat, 6), "lon_centroide": np.round(lon, 6),
        "compacidad": lotes["compacidad"].round(4),
        "n_px": lotes["id_lote"].map(n_px).astype(int), "n_px_interior": lotes["id_lote"].map(n_int).fillna(0).astype(int),
        "n_anios_maiz_soja": lotes["n_anios_maiz_soja"].astype(int),
        "pct_riego_condado": lotes["pct_riego_condado"].round(2),
        "anio_censo_riego": lotes["anio_censo_riego"].astype(int),
        "relieve_m": lotes["relieve_m"].round(2), "relieve_3dep_m": lotes["id_lote"].map(rel3).astype(float).round(2),
        "motivo": lotes["motivo"], "n_candidatos": lotes["n_candidatos"].astype(int),
    }).sort_values(["fips", "id_lote"]).reset_index(drop=True)
    tab.to_csv(OUT / "lotes.csv", index=False, float_format="%.6f", lineterminator="\n")

    px_out = px[["fips", "id_lote", "px_id", "x_m", "y_m", "lon", "lat", "dist_borde_m", "interior", "frac_en_lote"]].copy()
    px_out["x_m"] = px_out["x_m"].round().astype(int)
    px_out["y_m"] = px_out["y_m"].round().astype(int)
    px_out["lon"] = px_out["lon"].round(6)
    px_out["lat"] = px_out["lat"].round(6)
    px_out["dist_borde_m"] = px_out["dist_borde_m"].round(2)
    px_out["frac_en_lote"] = px_out["frac_en_lote"].round(4)
    px_out.to_csv(OUT / "pixeles.csv", index=False, lineterminator="\n")
    t(f"pixeles.csv: {len(px_out)} píxeles", t0)

    # GeoPackage (EPSG:4326)
    gp = OUT / "lotes.gpkg"
    if gp.exists():
        gp.unlink()
    g_lote = gpd.GeoDataFrame(tab[["fips", "id_lote", "paisaje"]], geometry=lotes.set_index("id_lote").loc[tab["id_lote"]].geometry.values, crs=5070)
    g_int = g_lote.copy()
    g_int["geometry"] = g_int.geometry.buffer(-PASO)
    g_lote.to_crs(4326).to_file(gp, layer="lote", driver="GPKG")
    g_int.to_crs(4326).to_file(gp, layer="lote_interior", driver="GPKG")

    # terreno (NASADEM)
    tt = []
    for lid, d in px.groupby("id_lote", sort=True):
        lon, lat = d["lon"].values, d["lat"].values
        rutas = teselas_dem(lon, lat)
        o = terreno.terreno_lote(rutas, lon, lat)
        e = d[["fips", "id_lote", "px_id"]].copy()
        for k in COLS_TERRENO:
            e[k] = np.round(o[k], 6 if k.startswith("curv") else 4)
        tt.append(e)
    ter = pd.concat(tt, ignore_index=True).merge(ter3, on=["id_lote", "px_id"], how="left", validate="1:1")
    ter = ter.sort_values(["fips", "id_lote", "px_id"])
    ter.to_csv(OUT / "terreno_px.csv", index=False, lineterminator="\n")
    t(f"terreno_px.csv: {len(ter)} filas", t0)

    # CDL por píxel y resumen anual
    cp = cdl_pixeles(px, indice_cdl())
    cp = cp.sort_values(["fips", "id_lote", "px_id", "anio"]).reset_index(drop=True)
    cp.to_csv(OUT / "cultivo_px_anual.csv", index=False, lineterminator="\n")
    t(f"cultivo_px_anual.csv: {len(cp)} filas", t0)
    la = resumen_anual(cp, px, lotes)
    la.to_csv(OUT / "lotes_anual.csv", index=False, lineterminator="\n")

    # suelo (SSURGO) y capa de polígonos en el GeoPackage
    import landsat
    import suelo
    import vegetacion
    rec = landsat.recuadros()
    spx, capa = suelo.suelo_px(px, rec)
    spx.to_csv(OUT / "suelo_px.csv", index=False, lineterminator="\n")
    smu = suelo.suelo_mukey(sorted(spx["mukey"].unique()))
    smu.to_csv(OUT / "suelo_mukey.csv", index=False, lineterminator="\n")
    capa[["fips", "id_lote", "mupolygonkey", "mukey", "geometry"]].sort_values(["id_lote", "mupolygonkey"]).to_crs(4326).to_file(
        gp, layer="suelo_poligonos", driver="GPKG")
    t(f"suelo_px.csv: {len(spx)} filas, {spx['mukey'].nunique()} mukeys", t0)

    # vegetación (Landsat C2 L2 y HLS S30)
    obs = pd.concat([vegetacion.observaciones(px, "landsat"), vegetacion.observaciones(px, "hls_s30")],
                    ignore_index=True).sort_values(vegetacion.CLAVES).reset_index(drop=True)
    obs.to_csv(OUT / "vegetacion_px_obs.csv", index=False, lineterminator="\n")
    t(f"vegetacion_px_obs.csv: {len(obs)} filas", t0)
    anios_bajados: dict[str, set[int]] = {}
    for fecha, sensor, i, ruta in vegetacion._escenas("landsat"):
        with np.load(ruta) as z:
            for k in z.files:
                if "__" not in k:
                    anios_bajados.setdefault(k, set()).add(int(fecha[:4]))
    va = vegetacion.anual(obs, px, anios_bajados)
    va.to_csv(OUT / "vegetacion_px_anual.csv", index=False, lineterminator="\n")
    sda_, sdc = vegetacion.suelo_desnudo(obs, px)
    sda_.to_csv(OUT / "suelo_desnudo_px.csv", index=False, lineterminator="\n")
    sdc.to_csv(OUT / "suelo_desnudo_px_compuesto.csv", index=False, lineterminator="\n")
    t(f"vegetacion_px_anual.csv: {len(va)} filas; suelo_desnudo_px.csv: {len(sda_)}", t0)

    # clima del lote (POWER e IMERG por POWER)
    import clima
    cd_ = clima.diario(tab)
    cla = clima.anual(cd_)
    cdo = clima.salida_diaria(cd_)
    cdo.to_csv(OUT / "clima_lote_diario.csv", index=False, lineterminator="\n")
    cla.to_csv(OUT / "clima_lote_anual.csv", index=False, lineterminator="\n")
    t(f"clima_lote_diario.csv: {len(cdo)} filas", t0)

    # drenaje con caños (AgTile-US, 30 m, Albers con lat_0 = 37,5: se toma la celda que contiene el centro del píxel)
    dren = px[["fips", "id_lote", "px_id"]].copy()
    zip_ag = RAW / "lotes" / "agtile" / "AgTile-US-TIFF.zip"
    dren["drenado_canos"] = np.nan
    if zip_ag.exists():
        with rasterio.open("/vsizip/{" + zip_ag.as_posix() + "}/AgTile-US-TIFF/AgTile-US.tif") as d:
            xa, ya = Transformer.from_crs(5070, d.crs, always_xy=True).transform(px["x_m"].values.astype(float),
                                                                               px["y_m"].values.astype(float))
            v = np.array([s_[0] for s_ in d.sample(zip(xa, ya))]).astype(float)
        dren["drenado_canos"] = np.where(np.isin(v, (0, 1)), v, np.nan)
    dren["drenado_canos"] = dren["drenado_canos"].astype("Int64")
    dren = dren.sort_values(["fips", "id_lote", "px_id"])
    dren.to_csv(OUT / "drenaje_px.csv", index=False, lineterminator="\n")
    t(f"drenaje_px.csv: {len(dren)} filas", t0)

    # controles de calidad
    res = ["### Píxeles por lote", "", "| id_lote | paisaje | n_px | n_px_interior | relieve_m |", "|---|---|---|---|---|"]
    res += [f"| {r.id_lote} | {r.paisaje} | {r.n_px} | {r.n_px_interior} | {r.relieve_m:.2f} |" for r in tab.itertuples()]
    res += ["", "### Pureza del cultivo por lote y año", "",
            f"- Lotes-año con lote_partido = 1 (menos de 90 % del grupo principal): {int(la['lote_partido'].sum())} de {len(la)}."]
    for lid, s in la.groupby("id_lote"):
        part = s.loc[s["lote_partido"] == 1, "anio"].tolist()
        res.append(f"- {lid}: pureza mínima {s['pct_px_cultivo_principal'].min():.1f} %, años partidos: {part if part else 'ninguno'}")
    al = la[la["cultivo_csb"] != ""]
    res += ["", "### Alineación CSB–CDL", "",
            f"- Años de la ventana CSB {CSB_VENTANA}: lotes-año donde el grupo CSB coincide con el principal del CDL: "
            f"{int((al['cultivo_csb'] == al['cultivo_principal']).sum())} de {len(al)}; "
            f"% medio de píxeles interiores con la clase del CSB: {al['pct_px_igual_csb'].mean():.1f}."]
    res += ["", "### Relieve", "", f"- Lotes con menos de 2 m de relieve NASADEM: {int((tab['relieve_m'] < 2).sum())} "
            f"({', '.join(tab.loc[tab['relieve_m'] < 2, 'id_lote']) or 'ninguno'})."]
    res += [f"- Lotes con menos de 2 m de relieve USGS 3DEP: {int((tab['relieve_3dep_m'] < 2).sum())} "
            f"({', '.join(tab.loc[tab['relieve_3dep_m'] < 2, 'id_lote']) or 'ninguno'}).",
            f"- Correlación NASADEM–3DEP de la elevación por píxel (todos los lotes): "
            f"{ter['elevacion_m'].corr(ter['elevacion_3dep_m']):.3f}; diferencia media 3DEP − NASADEM: "
            f"{(ter['elevacion_3dep_m'] - ter['elevacion_m']).mean():.2f} m.",
            "", "| id_lote | relieve_m | relieve_3dep_m | pct_px_drenado_canos |", "|---|---|---|---|"]
    pdren = dren.groupby("id_lote")["drenado_canos"].mean() * 100
    res += [f"| {r.id_lote} | {r.relieve_m:.2f} | {r.relieve_3dep_m:.2f} | {pdren.get(r.id_lote, np.nan):.1f} |" for r in tab.itertuples()]
    res += controles_obs(obs, va, spx, px)
    escribir_card({"lotes.csv": (tab, "estatico"), "pixeles.csv": (px_out, "estatico"), "terreno_px.csv": (ter, "estatico"),
                   "lotes_anual.csv": (la, "anual"), "cultivo_px_anual.csv": (cp, "anual"),
                   "suelo_px.csv": (spx, "estatico"), "suelo_mukey.csv": (smu, "estatico"),
                   "vegetacion_px_obs.csv": (obs, "diario"), "vegetacion_px_anual.csv": (va, "anual"),
                   "suelo_desnudo_px.csv": (sda_, "anual"), "suelo_desnudo_px_compuesto.csv": (sdc, "estatico"),
                   "clima_lote_diario.csv": (cdo, "diario"), "clima_lote_anual.csv": (cla, "anual"),
                   "drenaje_px.csv": (dren, "estatico")}, res)
    t("listo", t0)


if __name__ == "__main__":
    main()
