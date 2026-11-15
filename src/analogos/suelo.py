"""Análogos Argentina ↔ Corn Belt: suelo con la misma fuente en los dos lados (SoilGrids v2.0).

Lee las ventanas de SoilGrids de data/raw/analogos/soilgrids/ (1 km, Homolosine ESRI:54052, las baja
`download.py suelo`) y calcula la media por polígono:
- departamentos de Buenos Aires, La Pampa, Córdoba, Santa Fe y Entre Ríos (Georef, departamentos.geojson);
- los condados de data/reference/condados_cornbelt_10.csv (Census, Cartographic Boundary 1:500k 2023).

Cada propiedad se pondera por espesor de 0 a 30 cm: (5 × 0-5 + 10 × 5-15 + 15 × 15-30) / 30. Se promedia primero
cada profundidad en el polígono y después se pondera. Unidades de SoilGrids → unidades de salida:
- clay y sand en g/kg → % (÷ 10): arcilla_sg_pct, arena_sg_pct;
- soc en dg/kg → g/kg (÷ 10): soc_sg_g_kg;
- phh2o en pH × 10 → pH (÷ 10): ph_sg.
El sufijo _sg separa estas columnas de las de gSSURGO del paquete suelo_terreno (otra fuente, otros valores).
Los píxeles sin dato (-32768) no cuentan; frac_pixeles_validos es la fracción de píxeles del polígono con dato en
las 12 capas.

Salida: data/processed/analogos/suelo_sg.csv (id, lado, arcilla_sg_pct, arena_sg_pct, soc_sg_g_kg, ph_sg,
n_pixeles, frac_pixeles_validos). id es el código INDEC del departamento (lado = ar) o el fips (lado = us).
Uso: python src/analogos/suelo.py
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "analogos"
OUT = RAIZ / "data" / "processed" / "analogos"
PROVINCIAS = ("06", "14", "30", "42", "82")  # Buenos Aires, Córdoba, Entre Ríos, La Pampa, Santa Fe
PROPS = {"clay": "arcilla_sg_pct", "sand": "arena_sg_pct", "soc": "soc_sg_g_kg", "phh2o": "ph_sg"}
PROF = {"0-5cm": 5, "5-15cm": 10, "15-30cm": 15}
NODATA = -32768


def poligonos_ar() -> gpd.GeoDataFrame:
    g = gpd.read_file(RAW / "poligonos" / "departamentos.geojson")
    g["prov"] = g["provincia"].apply(lambda p: p["id"] if isinstance(p, dict) else str(p)[:2])
    g = g[g["prov"].isin(PROVINCIAS)]
    return g[["id", "geometry"]].assign(lado="ar")


def poligonos_us() -> gpd.GeoDataFrame:
    z = RAW / "poligonos" / "cb_2023_us_county_500k.zip"
    with zipfile.ZipFile(z) as f:
        shp = next(n for n in f.namelist() if n.endswith(".shp"))
    g = gpd.read_file(f"zip://{z.as_posix()}!{shp}")
    fips = set(pd.read_csv(RAIZ / "data" / "reference" / "condados_cornbelt_10.csv", dtype={"fips": str})["fips"])
    g = g[g["GEOID"].isin(fips)].rename(columns={"GEOID": "id"})
    faltan = fips - set(g["id"])
    if faltan:
        raise SystemExit(f"condados sin polígono en el Census: {sorted(faltan)[:10]}")
    return g[["id", "geometry"]].assign(lado="us")


def medias_region(pol: gpd.GeoDataFrame, region: str) -> pd.DataFrame:
    """Media por polígono de cada capa (prop × profundidad) y fracción de píxeles con dato en todas."""
    capas = {}
    ref = None
    for prop in PROPS:
        for prof in PROF:
            with rasterio.open(RAW / "soilgrids" / f"{prop}_{prof}_mean_1000_{region}.tif") as s:
                a = s.read(1).astype("float64")
                if ref is None:
                    ref = (s.transform, s.shape, s.crs)
                elif (s.transform, s.shape) != ref[:2]:
                    raise SystemExit(f"grilla distinta en {prop}_{prof} {region}")
                a[a == NODATA] = np.nan
                capas[(prop, prof)] = a
    transform, shape, crs = ref
    pol = pol.to_crs(crs).reset_index(drop=True)
    # cada píxel va al polígono que contiene su centro (all_touched=False); los polígonos chicos sin ningún
    # centro quedan sin dato
    etiqueta = rasterize(((geom, i + 1) for i, geom in enumerate(pol.geometry)), out_shape=shape,
                         transform=transform, fill=0, dtype="int32")
    lab = etiqueta.ravel()
    n_pol = len(pol)
    n_px = np.bincount(lab, minlength=n_pol + 1)[1:]
    validos = np.all([~np.isnan(a) for a in capas.values()], axis=0).ravel()
    n_val = np.bincount(lab, weights=validos, minlength=n_pol + 1)[1:]
    out = pd.DataFrame({"id": pol["id"].to_numpy(), "lado": pol["lado"].to_numpy(), "n_pixeles": n_px})
    for prop, col in PROPS.items():
        acum = np.zeros(n_pol)
        for prof, peso in PROF.items():
            a = capas[(prop, prof)].ravel()
            ok = ~np.isnan(a)
            s = np.bincount(lab[ok], weights=a[ok], minlength=n_pol + 1)[1:]
            c = np.bincount(lab[ok], minlength=n_pol + 1)[1:]
            with np.errstate(invalid="ignore", divide="ignore"):
                acum += peso * np.where(c > 0, s / c, np.nan)
        out[col] = acum / sum(PROF.values()) / 10
    with np.errstate(invalid="ignore", divide="ignore"):
        out["frac_pixeles_validos"] = np.where(n_px > 0, n_val / n_px, np.nan)
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.concat([medias_region(poligonos_ar(), "pampa"), medias_region(poligonos_us(), "cornbelt")],
                   ignore_index=True)
    df = df[["id", "lado", *PROPS.values(), "n_pixeles", "frac_pixeles_validos"]]
    df.round(3).to_csv(OUT / "suelo_sg.csv", index=False, encoding="utf-8", lineterminator="\n")
    print(df.groupby("lado")[list(PROPS.values())].describe().T.round(2).to_string())
    print("sin dato:", df[df[list(PROPS.values())].isna().any(axis=1)][["id", "lado", "n_pixeles"]].to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
