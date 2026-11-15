"""Paquete 0 — Base: arma data/reference/condados.gpkg, condados.csv y anios.csv.

Se corre desde la raíz como `python src/base/process.py`, sin argumentos. Lee solo de
data/raw/base/ y de config/config.yaml; no baja nada. Idempotente.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import geopandas as gpd  # noqa: E402
import pandas as pd  # noqa: E402

from src.common.config import cargar_config, estados_config  # noqa: E402

RAW = REPO / "data" / "raw" / "base"
REF = REPO / "data" / "reference"
ANIO_CB = 2024
ZIP = RAW / f"cb_{ANIO_CB}_us_county_500k.zip"


def condados() -> pd.DataFrame:
    cfg = cargar_config()
    estados = estados_config()
    alfa_por_fips = {e["fips"]: alfa for alfa, e in estados.items()}
    gdf = gpd.read_file(f"zip://{ZIP.as_posix()}")
    gdf = gdf[gdf["STATEFP"].isin(alfa_por_fips)].copy()
    gdf["fips"] = gdf["STATEFP"].str.zfill(2) + gdf["COUNTYFP"].str.zfill(3)
    gdf["estado"] = gdf["STATEFP"].map(alfa_por_fips)
    gdf["condado"] = gdf["NAME"]
    gdf = gdf.sort_values("fips").reset_index(drop=True)

    # Área y centroide en Albers CONUS (EPSG:5070); centroide devuelto a EPSG:4326.
    albers = gdf.to_crs(cfg["crs"]["areas"])
    gdf["area_km2"] = (albers.geometry.area / 1e6).round(3)
    cent = albers.geometry.centroid.to_crs(cfg["crs"]["guardar"])
    gdf["lat_centroide"] = cent.y.round(5)
    gdf["lon_centroide"] = cent.x.round(5)

    salida = gdf[["fips", "estado", "condado", "lat_centroide", "lon_centroide", "area_km2", "geometry"]]
    salida = salida.to_crs(cfg["crs"]["guardar"])
    gpkg = REF / "condados.gpkg"
    REF.mkdir(parents=True, exist_ok=True)
    if gpkg.exists():
        gpkg.unlink()
    salida.to_file(gpkg, layer="condados", driver="GPKG")

    tabla = pd.DataFrame(salida.drop(columns="geometry"))
    tabla.to_csv(REF / "condados.csv", index=False, encoding="utf-8", lineterminator="\n")
    return tabla


def anios() -> pd.DataFrame:
    cfg = cargar_config()
    v = cfg["ventanas"]
    t, inv = v["temporada"], v["invierno_previo"]
    filas = [{"anio": y,
              "inicio_temporada": f"{y}-{t['desde']}",
              "fin_temporada": f"{y}-{t['hasta']}",
              "inicio_invierno_previo": f"{y - 1}-{inv['desde']}",
              "fin_invierno_previo": f"{y}-{inv['hasta']}"}
             for y in range(int(cfg["periodo"]["anio_inicio"]), int(cfg["periodo"]["anio_fin"]) + 1)]
    df = pd.DataFrame(filas)
    df.to_csv(REF / "anios.csv", index=False, encoding="utf-8", lineterminator="\n")
    return df


def main() -> int:
    if not ZIP.exists():
        print(f"falta {ZIP.relative_to(REPO)}: correr primero src/base/download.py")
        return 1
    tc = condados()
    ta = anios()
    print(f"condados.csv: {len(tc)} filas; anios.csv: {len(ta)} filas")
    print(tc.groupby("estado").size().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
