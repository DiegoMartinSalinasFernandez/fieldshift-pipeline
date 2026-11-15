"""SSURGO por píxel: polígonos de data/raw/lotes/ssurgo rasterizados a 10 m (grilla alineada con la de 30 m:
3 × 3 subceldas por píxel) → fracción de cada mukey en cada píxel (suelo_px.csv); atributos de cada mukey con
los mismos cálculos que src/suelo_terreno/process.py (suelo_mukey.csv)."""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from rasterio.features import rasterize
from rasterio.transform import from_origin
from shapely import wkt as swkt

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "lotes" / "ssurgo"
sys.path.insert(0, str(RAIZ))
from src.suelo_terreno.process import NCCPI, horizontes_a_componente, media_pond  # noqa: E402

INUNDACION = {"None": "nula", "Very rare": "muy_rara", "Rare": "rara", "Occasional": "ocasional",
              "Frequent": "frecuente", "Very frequent": "muy_frecuente"}


def poligonos(id_lote: str) -> gpd.GeoDataFrame:
    df = pd.read_csv(RAW / f"poligonos_{id_lote}.csv", dtype={"mukey": str, "mupolygonkey": str})
    g = gpd.GeoDataFrame(df[["mupolygonkey", "mukey"]], geometry=[swkt.loads(w) for w in df["wkt"]], crs=4326)
    return g.to_crs(5070)


def suelo_px(px: pd.DataFrame, rec: pd.DataFrame) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    partes, capas = [], []
    for r in rec.sort_values("id_lote").itertuples():
        g = poligonos(r.id_lote)
        g = g[~g.geometry.is_empty]
        capas.append(g.assign(fips=r.fips, id_lote=r.id_lote))
        tr = from_origin(r.x0, r.y0, 10.0, 10.0)
        ras = rasterize(((geo, int(m)) for geo, m in zip(g.geometry, g["mukey"])), out_shape=(3 * r.alto, 3 * r.ancho),
                        transform=tr, fill=0, dtype="int64")
        d = px[px["id_lote"] == r.id_lote]
        col = np.rint((d["x_m"].values - r.x0 - 15) / 30).astype(int)
        fil = np.rint((r.y0 - 15 - d["y_m"].values) / 30).astype(int)
        sub = np.stack([ras[3 * fil + i, 3 * col + j] for i in range(3) for j in range(3)], axis=1)
        for k in range(len(d)):
            vals, cuenta = np.unique(sub[k][sub[k] > 0], return_counts=True)
            for v, c in zip(vals, cuenta):
                partes.append((r.fips, r.id_lote, int(d["px_id"].values[k]), str(v), round(c / 9, 4)))
    out = pd.DataFrame(partes, columns=["fips", "id_lote", "px_id", "mukey", "frac_mukey"])
    out = out.sort_values(["fips", "id_lote", "px_id", "mukey"]).reset_index(drop=True)
    capa = pd.concat(capas, ignore_index=True)
    return out, gpd.GeoDataFrame(capa, geometry="geometry", crs=5070)


def suelo_mukey(mukeys: list[str]) -> pd.DataFrame:
    # keep_default_na=False en los textos: "None" es un valor de SSURGO (p. ej. flodfreqdcd), no un faltante
    leer = lambda t, txt=False: pd.read_csv(RAW / f"{t}.csv", dtype={"mukey": str, "cokey": str, "chkey": str},  # noqa: E731
                                            keep_default_na=not txt, na_values=[""] if txt else None)
    mu, co = leer("mapunit", True), leer("component", True)
    h, r = leer("chorizon"), leer("restricciones")
    nc = pd.concat([leer("nccpi"), leer("nccpi_submodelos")]).drop_duplicates()
    for c in ("aws0100wta", "aws0150wta", "hydclprs", "pondfreqprs", "wtdepannmin", "slopegraddcp", "slopegradwta"):
        mu[c] = pd.to_numeric(mu[c], errors="coerce")
    co["comppct_r"] = pd.to_numeric(co["comppct_r"], errors="coerce")
    comp = horizontes_a_componente(h, r)
    nc = nc[nc["rulename"].isin(NCCPI)]
    nc = nc.assign(col=nc["rulename"].map(NCCPI)).pivot_table(index="cokey", columns="col", values="interphr",
                                                              aggfunc="mean")
    comp = comp.join(nc, how="outer")
    vars_comp = list(comp.columns)
    co = co.merge(comp, left_on="cokey", right_index=True, how="left")
    agg = media_pond(co, "mukey", "comppct_r", vars_comp)
    dom = (co.sort_values(["mukey", "comppct_r", "cokey"], ascending=[True, False, True])
           .groupby("mukey").head(1).set_index("mukey"))
    mu = mu.set_index("mukey")
    out = pd.DataFrame(index=pd.Index(sorted(set(mukeys)), name="mukey"))
    out["muname"] = mu["muname"]
    out["aws0_100_mm"] = mu["aws0100wta"] * 10  # muaggatt en cm
    out["aws0_150_mm"] = mu["aws0150wta"] * 10
    out["soc0_30_gm2"] = agg["soc0_30_gm2"]
    for c in ("nccpi_general", "nccpi_maiz", "nccpi_soja"):
        out[c] = agg[c]
    out["clase_drenaje"] = mu["drclassdcd"]
    out["clase_drenaje_mas_humeda"] = mu["drclasswettest"]
    out["grupo_hidrologico"] = mu["hydgrpdcd"]
    out["pct_componentes_hidricos"] = mu["hydclprs"]
    out["pct_encharcamiento"] = mu["pondfreqprs"]
    out["frec_inundacion"] = mu["flodfreqdcd"].map(INUNDACION)
    out["napa_min_cm"] = mu["wtdepannmin"]
    out["pendiente_dcd_pct"] = mu["slopegraddcp"]
    out["pendiente_comp_pct"] = mu["slopegradwta"]
    out["clase_erosion"] = dom["erocl"].str.replace("None", "nula", regex=False)
    out["pct_comp_dominante"] = dom["comppct_r"]
    out["materia_organica_pct"] = agg["om_r"]
    out["arcilla_pct"] = agg["claytotal_r"]
    out["arena_pct"] = agg["sandtotal_r"]
    out["limo_pct"] = agg["silttotal_r"]
    out["ph_agua"] = agg["ph1to1h2o_r"]
    out["factor_k_rusle"] = agg["kwfact"]
    dec = {"aws0_100_mm": 1, "aws0_150_mm": 1, "soc0_30_gm2": 0, "nccpi_general": 4, "nccpi_maiz": 4,
           "nccpi_soja": 4, "napa_min_cm": 1, "pendiente_dcd_pct": 2, "pendiente_comp_pct": 2,
           "pct_componentes_hidricos": 1, "pct_encharcamiento": 1, "pct_comp_dominante": 1,
           "materia_organica_pct": 3, "arcilla_pct": 2, "arena_pct": 2, "limo_pct": 2, "ph_agua": 2,
           "factor_k_rusle": 4}
    for c, d in dec.items():
        out[c] = pd.to_numeric(out[c], errors="coerce").round(d)
    return out.reset_index()
