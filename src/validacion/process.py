"""validacion: PRISM mensual y CoCoRaHS por condado, y tabla de sesgo/correlación de POWER.

Lee data/raw/validacion/ (PRISM zips mensuales 4 km y exports diarios de CoCoRaHS por estado y
mes) y escribe data/processed/validacion/validacion_mensual.csv y docs/datasets/validacion.md.
"""
from __future__ import annotations

import glob
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
from src.common.config import cargar_config  # noqa: E402

RAW = RAIZ / "data" / "raw" / "validacion"
OUT = RAIZ / "data" / "processed" / "validacion" / "validacion_mensual.csv"
CARD = RAIZ / "docs" / "datasets" / "validacion.md"
CONDADOS = RAIZ / "data" / "reference" / "condados.gpkg"
CLIMA = RAIZ / "data" / "processed" / "clima" / "clima_mensual.csv"

PRISM_COL = {"ppt": "prec_prism_mm", "tmax": "tmax_prism_c", "tmin": "tmin_prism_c", "tmean": "tmed_prism_c"}
MIN_DIAS = 25
PULG_MM = 25.4
COCO_DESDE = 2008


def meses(cfg) -> list[str]:
    p = cfg["periodo"]
    return [f"{y}-{m:02d}" for y in range(int(p["anio_inicio"]), int(p["anio_fin"]) + 1) for m in range(1, 13)]


def esqueleto(cfg, fips: list[str]) -> pd.DataFrame:
    ms = meses(cfg)
    df = pd.DataFrame([(f, m) for f in fips for m in ms], columns=["fips", "mes"])
    df["anio"] = df["mes"].str[:4].astype(int)
    return df[["fips", "anio", "mes"]]


# ------------------------------------------------------------------ PRISM
def prism(gdf) -> pd.DataFrame:
    import rasterio
    from rasterio.features import rasterize
    from rasterio.windows import from_bounds

    archivos = sorted(glob.glob(str(RAW / "prism" / "*" / "*.zip")))
    if not archivos:
        return pd.DataFrame(columns=["fips", "mes"])
    etiquetas = None
    filas = {}
    for a in archivos:
        nombre = Path(a).stem  # prism_ppt_us_25m_202007
        m = re.match(r"prism_(\w+?)_us_25m_(\d{4})(\d{2})$", nombre)
        if not m:
            continue
        var, y, mm = m.group(1), m.group(2), m.group(3)
        with rasterio.open(f"/vsizip/{Path(a).as_posix()}/{nombre}.tif") as src:
            if etiquetas is None:
                g = gdf.to_crs(src.crs)
                win = from_bounds(*g.total_bounds, transform=src.transform).round_offsets().round_lengths()
                win = rasterio.windows.Window(win.col_off - 2, win.row_off - 2, win.width + 4, win.height + 4)
                tr = src.window_transform(win)
                codigos = np.arange(1, len(g) + 1)
                etiquetas = rasterize(zip(g.geometry, codigos), out_shape=(int(win.height), int(win.width)),
                                      transform=tr, fill=0, dtype="int32")
                n_cod = len(g) + 1
                fips_cod = list(g["fips"])
                ventana, nd = win, src.nodata
            arr = src.read(1, window=ventana).astype("float64")
        ok = (etiquetas > 0) & np.isfinite(arr)
        if nd is not None:
            ok &= arr != nd
        ok &= arr > -9000  # relleno de PRISM (-9999)
        s = np.bincount(etiquetas[ok], weights=arr[ok], minlength=n_cod)
        n = np.bincount(etiquetas[ok], minlength=n_cod)
        with np.errstate(invalid="ignore", divide="ignore"):
            media = np.where(n > 0, s / np.maximum(n, 1), np.nan)
        for i, f in enumerate(fips_cod, start=1):
            filas.setdefault((f, f"{y}-{mm}"), {})[PRISM_COL[var]] = media[i]
    df = pd.DataFrame([{"fips": k[0], "mes": k[1], **v} for k, v in filas.items()])
    return df


# ------------------------------------------------------------------ CoCoRaHS
def cocorahs(gdf) -> pd.DataFrame:
    import geopandas as gpd

    archivos = sorted(glob.glob(str(RAW / "cocorahs" / "*" / "*.csv")))
    if not archivos:
        return pd.DataFrame(columns=["fips", "mes"])
    partes = []
    for a in archivos:
        try:
            d = pd.read_csv(a, skipinitialspace=True, dtype=str,
                            usecols=["ObservationDate", "StationNumber", "Latitude", "Longitude", "TotalPrecipAmt"])
        except (pd.errors.EmptyDataError, ValueError):
            continue
        partes.append(d)
    d = pd.concat(partes, ignore_index=True)
    d["TotalPrecipAmt"] = d["TotalPrecipAmt"].str.strip()
    p = d["TotalPrecipAmt"].replace({"T": "0"})  # T = traza (< 0,01 in)
    d["prec_in"] = pd.to_numeric(p, errors="coerce")
    d = d[d["prec_in"].notna() & (d["prec_in"] >= 0)]
    d["fecha"] = pd.to_datetime(d["ObservationDate"], errors="coerce")
    d = d[d["fecha"].notna()]
    d = d.sort_values(["StationNumber", "fecha"]).drop_duplicates(["StationNumber", "fecha"], keep="first")
    d["mes"] = d["fecha"].dt.strftime("%Y-%m")
    # Ubicación de cada estación: la mediana de las coordenadas reportadas
    est = d.groupby("StationNumber")[["Latitude", "Longitude"]].agg(
        lambda s: pd.to_numeric(s, errors="coerce").median()).dropna()
    pts = gpd.GeoDataFrame(est, geometry=gpd.points_from_xy(est["Longitude"], est["Latitude"]), crs="EPSG:4326")
    j = gpd.sjoin(pts, gdf[["fips", "geometry"]].to_crs("EPSG:4326"), how="inner", predicate="within")
    j = j[~j.index.duplicated(keep="first")]
    d = d.merge(j[["fips"]], left_on="StationNumber", right_index=True, how="inner")
    em = d.groupby(["fips", "StationNumber", "mes"]).agg(dias=("prec_in", "size"), prec_in=("prec_in", "sum")).reset_index()
    em = em[em["dias"] >= MIN_DIAS]
    em["prec_mm"] = em["prec_in"] * PULG_MM
    out = em.groupby(["fips", "mes"]).agg(prec_cocorahs_mm=("prec_mm", "mean"),
                                          n_estaciones_cocorahs=("prec_mm", "size")).reset_index()
    return out


# ------------------------------------------------------------------ data card
def dic_columnas() -> list[tuple[str, str, str, str]]:
    return [
        ("prec_prism_mm", "Lluvia total del mes, media de las celdas PRISM de 4 km cuyo centro cae en el condado",
         "mm", "PRISM AN monthly 4 km (Oregon State University)"),
        ("tmax_prism_c", "Temperatura máxima media del mes, media por condado", "°C",
         "PRISM AN monthly 4 km (Oregon State University)"),
        ("tmin_prism_c", "Temperatura mínima media del mes, media por condado", "°C",
         "PRISM AN monthly 4 km (Oregon State University)"),
        ("tmed_prism_c", "Temperatura media del mes (tmean de PRISM = (tmax + tmin) / 2), media por condado", "°C",
         "PRISM AN monthly 4 km (Oregon State University)"),
        ("prec_cocorahs_mm", f"Lluvia del mes: media entre las estaciones del condado con al menos {MIN_DIAS} "
         "reportes diarios en el mes (suma de los días reportados, pulgadas × 25,4)", "mm",
         "CoCoRaHS daily reports (export público)"),
        ("n_estaciones_cocorahs", f"Estaciones CoCoRaHS del condado con al menos {MIN_DIAS} reportes diarios en el mes "
         "(0 = ninguna; vacío antes de 2008)", "estaciones", "CoCoRaHS daily reports (export público)"),
    ]


def tabla_validacion(df: pd.DataFrame) -> list[str]:
    if not CLIMA.exists():
        return ["No se encontró data/processed/clima/clima_mensual.csv: tabla no calculada."]
    c = pd.read_csv(CLIMA, dtype={"fips": str}, usecols=["fips", "mes", "prec_power_mm", "prec_imerg_mm",
                                                           "tmax_c", "tmin_c", "tmed_c"])
    m = df.merge(c, on=["fips", "mes"], how="inner")
    pares = [("prec_power_mm", "prec_prism_mm", "Lluvia POWER vs PRISM", "mm/mes"),
             ("prec_imerg_mm", "prec_prism_mm", "Lluvia IMERG vs PRISM", "mm/mes"),
             ("prec_power_mm", "prec_cocorahs_mm", "Lluvia POWER vs CoCoRaHS", "mm/mes"),
             ("prec_imerg_mm", "prec_cocorahs_mm", "Lluvia IMERG vs CoCoRaHS", "mm/mes"),
             ("tmax_c", "tmax_prism_c", "Tmax POWER vs PRISM", "°C"),
             ("tmin_c", "tmin_prism_c", "Tmin POWER vs PRISM", "°C"),
             ("tmed_c", "tmed_prism_c", "Tmed POWER vs PRISM", "°C")]
    out = ["| comparacion | unidad | n_condado_mes | sesgo_medio | rmse | correlacion_pearson |",
           "|---|---|---|---|---|---|"]
    for a, b, titulo, u in pares:
        x = m[[a, b]].dropna()
        if len(x) < 3:
            out.append(f"| {titulo} | {u} | {len(x)} |  |  |  |")
            continue
        dif = x[a] - x[b]
        out.append(f"| {titulo} | {u} | {len(x)} | {dif.mean():.2f} | {np.sqrt((dif ** 2).mean()):.2f} | "
                   f"{x[a].corr(x[b]):.3f} |")
    out.append("")
    out.append("Sesgo = fuente NASA − referencia de superficie, sobre todos los pares condado-mes con dato en las dos.")
    return out


def data_card(df: pd.DataFrame, n_prism: int, n_coco: int) -> None:
    filas = ["| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |",
             "|---|---|---|---|---|---|---|---|---|"]
    for col, desc, u, fuente in dic_columnas():
        s = df[col]
        llenos = df.loc[s.notna(), "mes"]
        desde = llenos.min() if len(llenos) else ""
        hasta = llenos.max() if len(llenos) else ""
        falt = 100.0 * s.isna().mean()
        filas.append(f"| validacion_mensual.csv | {col} | {desc} | {u} | {fuente} |  | {desde} | {hasta} | {falt:.2f} |")
    txt = f"""# Data card — validacion

Datos de superficie (no NASA) para validar la lluvia y la temperatura de NASA POWER y GPM IMERG
del paquete `clima`: PRISM (Oregon State University) y CoCoRaHS (red de pluviómetros voluntarios).

## Archivos

- `data/processed/validacion/validacion_mensual.csv` → `fips, anio, mes, prec_prism_mm, tmax_prism_c, tmin_prism_c, tmed_prism_c, prec_cocorahs_mm, n_estaciones_cocorahs`.
  Una fila por condado y mes, {df['mes'].min()} a {df['mes'].max()} ({len(df)} filas).
- Insumos en raw: {n_prism} zips mensuales de PRISM y {n_coco} exports mensuales de CoCoRaHS.

## Diccionario de columnas

{chr(10).join(filas)}

## Validación de POWER e IMERG (mensual, por condado)

{chr(10).join(tabla_validacion(df))}

## Supuestos

- PRISM: se usa el directorio HTTP público `https://data.prism.oregonstate.edu/time_series/us/an/4km/<var>/monthly/<anio>/`
  (mismos archivos que el servicio web `services.nacse.org/prism/data/get/us/4km/...`, que limita a dos descargas por
  archivo por día). Serie AN (todas las estaciones), 4 km (`25m` = 2,5 minutos de arco), un zip por variable y mes,
  bajados de a tres a la vez. PRISM es de uso no comercial y pide cita: PRISM Group, Oregon State University,
  https://prism.oregonstate.edu.
- Media por condado de las celdas de 4 km cuyo centro cae dentro del polígono (rasterización de `condados.gpkg`
  en la grilla de PRISM). No se aplica la máscara agrícola: es una referencia del clima del condado, comparable con
  el centroide de POWER y la media de IMERG. Los meses de 2025 pueden ser provisionales en PRISM.
- `tmed_prism_c` es la variable `tmean` de PRISM (que PRISM define como (tmax + tmin) / 2).
- CoCoRaHS: export público `data.cocorahs.org/export/exportreports.aspx` (ReportType=Daily, CSV) por estado y mes,
  desde 2008 (como pide el contrato). Las estaciones se ubican por la mediana de sus coordenadas y se asignan al
  condado por unión espacial con `condados.gpkg` (solo estaciones de los estados del config).
- CoCoRaHS: `T` (traza) = 0; `NA` = sin dato. Un reporte por estación y fecha de observación (se queda el primero si
  hay duplicados). Los informes de varios días (Multi-Day) no se bajaron: esos días cuentan como no reportados.
- Lluvia mensual de una estación = suma de sus reportes diarios del mes, sin escalar por los días faltantes; solo
  estaciones con al menos {MIN_DIAS} reportes. La del condado es la media de esas estaciones. Sin estaciones válidas:
  `prec_cocorahs_mm` vacío y `n_estaciones_cocorahs` = 0. Antes de 2008, ambas vacías.
- La tabla de validación usa `data/processed/clima/clima_mensual.csv` (paquete `clima`, dueño Persona 1).

## Problemas conocidos

- La lluvia de CoCoRaHS subestima el total del mes en las estaciones con 25 a 30 reportes (días sin reporte no se
  rellenan). La nieve se mide como equivalente en agua cuando el observador lo carga: en invierno hay más huecos.
- POWER es un valor puntual en el centroide (grilla de 0,5°), PRISM una media areal a 4 km y CoCoRaHS la media de
  pocos pluviómetros: las diferencias mezclan error de cada fuente y de representatividad espacial.
"""
    CARD.parent.mkdir(parents=True, exist_ok=True)
    CARD.write_text(txt, encoding="utf-8", newline="\n")


def main() -> None:
    import geopandas as gpd

    t0 = time.time()
    cfg = cargar_config()
    gdf = gpd.read_file(CONDADOS)
    gdf["fips"] = gdf["fips"].astype(str).str.zfill(5)
    gdf = gdf.sort_values("fips").reset_index(drop=True)
    base = esqueleto(cfg, list(gdf["fips"]))
    pr = prism(gdf)
    print(f"prism {time.time() - t0:.0f}s")
    co = cocorahs(gdf)
    print(f"cocorahs {time.time() - t0:.0f}s")
    df = base.merge(pr, on=["fips", "mes"], how="left").merge(co, on=["fips", "mes"], how="left")
    for c in PRISM_COL.values():
        if c not in df:
            df[c] = np.nan
    for c in ("prec_cocorahs_mm", "n_estaciones_cocorahs"):
        if c not in df:
            df[c] = np.nan
    desde_coco = df["anio"] >= COCO_DESDE
    meses_coco = set(co["mes"]) if len(co) else set()
    # estado y mes con export bajado: los condados de ese estado sin estación válida cuentan 0
    alpha_fips = {a: str(v["fips"]).zfill(2) for a, v in cfg["zona"]["estados"].items()}
    bajados = set()
    for a in glob.glob(str(RAW / "cocorahs" / "*" / "*.csv")):
        st, y, m = re.search(r"cocorahs_daily_([A-Z]{2})_(\d{4})(\d{2})\.csv$", a.replace("\\", "/")).groups()
        bajados.add(f"{alpha_fips.get(st, '')}|{y}-{m}")
    clave = df["fips"].str[:2] + "|" + df["mes"]
    llenar0 = desde_coco & clave.isin(bajados) & df["n_estaciones_cocorahs"].isna()
    df.loc[llenar0, "n_estaciones_cocorahs"] = 0
    df.loc[~desde_coco, ["prec_cocorahs_mm", "n_estaciones_cocorahs"]] = np.nan
    # coherencia: si falta alguna temperatura del trío, se deja el mes de PRISM-temp vacío
    trio = ["tmin_prism_c", "tmed_prism_c", "tmax_prism_c"]
    df.loc[df[trio].isna().any(axis=1), trio] = np.nan
    df = df[["fips", "anio", "mes", "prec_prism_mm", "tmax_prism_c", "tmin_prism_c", "tmed_prism_c",
             "prec_cocorahs_mm", "n_estaciones_cocorahs"]].sort_values(["fips", "mes"])
    for c in ["prec_prism_mm", "tmax_prism_c", "tmin_prism_c", "tmed_prism_c", "prec_cocorahs_mm"]:
        df[c] = df[c].round(3)
    df["n_estaciones_cocorahs"] = df["n_estaciones_cocorahs"].astype("Int64")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, float_format="%.3f", lineterminator="\n")
    n_prism = len(glob.glob(str(RAW / "prism" / "*" / "*.zip")))
    n_coco = len(glob.glob(str(RAW / "cocorahs" / "*" / "*.csv")))
    data_card(df, n_prism, n_coco)
    print(f"listo {len(df)} filas {time.time() - t0:.0f}s; meses cocorahs con dato {len(meses_coco)}")


if __name__ == "__main__":
    main()
