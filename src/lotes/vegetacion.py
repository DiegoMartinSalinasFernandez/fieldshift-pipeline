"""Observaciones despejadas por píxel (Landsat C2 L2 y HLS S30) desde los recortes de data/raw/lotes/<producto>/,
resúmenes anuales (solo Landsat; _s2 desde HLS S30) y suelo desnudo."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "lotes"
STAC = RAIZ / "data" / "interim" / "lotes" / "stac"
CLAVES = ["fips", "id_lote", "px_id", "anio", "fecha", "producto", "sensor"]
REFL = ["refl_blue", "refl_green", "refl_red", "refl_nir", "refl_swir1", "refl_swir2"]
# QA_PIXEL de Collection 2: 0 relleno, 1 nube dilatada, 2 cirro, 3 nube, 4 sombra, 5 nieve, 6 despejado, 7 agua
QA_MALO = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 7)
QA_DESPEJADO = 1 << 6
# Fmask de HLS v2: 0 cirro, 1 nube, 2 adyacente a nube o sombra, 3 sombra, 4 nieve/hielo, 5 agua (6-7 aerosol)
FMASK_MALO = 0b111111
SENSOR_LS = {"LT05": "L5", "LE07": "L7", "LC08": "L8", "LC09": "L9"}
SENSOR_S2 = {"sentinel-2a": "S2A", "sentinel-2b": "S2B", "sentinel-2c": "S2C"}


def _plataformas(prod: str) -> dict[str, str]:
    out = {}
    for p in sorted(STAC.glob(f"{prod}_*.json")):
        for e in json.load(open(p, encoding="utf-8")):
            out[e["id"]] = e["plataforma"]
    return out


def _escenas(prod: str) -> list[tuple[str, str, str, Path]]:
    """(fecha, sensor, id, ruta) ordenadas; Landsat 4 queda afuera (el contrato no lo lista)."""
    out = []
    plat = _plataformas(prod) if prod == "hls_s30" else {}
    for p in sorted((RAW / prod).glob("*/*.npz")):
        i = p.stem
        if prod == "landsat":
            sensor = SENSOR_LS.get(i[:4])
            f = i.split("_")[3]
            fecha = f"{f[:4]}-{f[4:6]}-{f[6:8]}"
        else:
            pl = plat.get(i, "")
            if not pl:  # HLS de LP DAAC: la plataforma viene del SPACECRAFT_NAME del Fmask, guardado en el npz
                with np.load(p) as z:
                    pl = str(z["__plataforma"]) if "__plataforma" in z.files else ""
            sensor = SENSOR_S2.get(pl.lower())
            f = i.split(".")[3][:7]
            fecha = (pd.Timestamp(f"{f[:4]}-01-01") + pd.Timedelta(days=int(f[4:]) - 1)).strftime("%Y-%m-%d")
        if sensor:
            out.append((fecha, sensor, i, p))
    # T1 antes que T2: en escenas repetidas (filas solapadas de la misma pasada) queda la primera
    out.sort(key=lambda t: (t[0], t[1], t[2].endswith("_T2"), t[2]))
    return out


def observaciones(px: pd.DataFrame, prod: str) -> pd.DataFrame:
    por_lote = {l: d for l, d in px.groupby("id_lote")}
    partes = []
    for fecha, sensor, i, p in _escenas(prod):
        with np.load(p) as z:
            for lote in sorted(k for k in z.files if "__" not in k):
                d = por_lote.get(lote)
                if d is None:
                    continue
                a = z[lote].astype(np.int64)
                x0, y0 = z[f"{lote}__x0y0"]
                col = np.rint((d["x_m"].values - x0 - 15) / 30).astype(int)
                fil = np.rint((y0 - 15 - d["y_m"].values) / 30).astype(int)
                v = a[:, fil, col]  # (7, n)
                dn, qa = v[:6], v[6]
                if prod == "landsat":
                    ok = ((qa & QA_MALO) == 0) & ((qa & QA_DESPEJADO) != 0) & ((dn >= 7273) & (dn <= 43636)).all(0)
                    refl = dn * 0.0000275 - 0.2
                else:
                    ok = ((qa & FMASK_MALO) == 0) & (qa != 255) & ((dn >= 1) & (dn <= 16000)).all(0)
                    refl = dn * 0.0001
                if not ok.any():
                    continue
                e = pd.DataFrame({"fips": d["fips"].values[ok], "id_lote": lote, "px_id": d["px_id"].values[ok]})
                e["anio"] = int(fecha[:4])
                e["fecha"] = fecha
                e["producto"] = "landsat_c2_l2" if prod == "landsat" else "hls_s30"
                e["sensor"] = sensor
                for k, c in enumerate(REFL):
                    e[c] = refl[k][ok]
                e["qa_valor"] = qa[ok]
                e["slc_off"] = int(sensor == "L7" and fecha >= "2003-05-31")
                partes.append(e)
    cols = CLAVES + REFL + ["ndvi", "evi2", "gcvi", "ndmi", "slc_off", "qa_valor"]
    if not partes:
        return pd.DataFrame(columns=cols)
    o = pd.concat(partes, ignore_index=True)
    o = o.drop_duplicates(subset=CLAVES, keep="first")
    b, g, r, n, s1 = (o[c].values for c in REFL[:5])
    with np.errstate(divide="ignore", invalid="ignore"):
        o["ndvi"] = (n - r) / (n + r)
        o["evi2"] = 2.5 * (n - r) / (n + 2.4 * r + 1)
        o["gcvi"] = n / g - 1
        o["ndmi"] = (n - s1) / (n + s1)
    for c in REFL + ["ndvi", "evi2", "gcvi", "ndmi"]:
        o[c] = o[c].replace([np.inf, -np.inf], np.nan).round(4)
    return o[cols]


def anual(obs: pd.DataFrame, px: pd.DataFrame, anios_bajados: dict[str, set[int]]) -> pd.DataFrame:
    """Una fila por píxel y año con al menos una escena Landsat bajada que cubre el lote."""
    base = [(f, l, int(p), a) for f, l, p in px[["fips", "id_lote", "px_id"]].itertuples(index=False)
            for a in sorted(anios_bajados.get(l, ()))]
    out = pd.DataFrame(base, columns=["fips", "id_lote", "px_id", "anio"])
    k = ["fips", "id_lote", "px_id", "anio"]
    ls = obs[obs["producto"] == "landsat_c2_l2"].copy()
    ls["doy"] = pd.to_datetime(ls["fecha"]).dt.dayofyear
    ls["mes"] = ls["fecha"].str[5:7].astype(int)
    srt = ls.sort_values(k + ["fecha"])
    for ind in ("ndvi", "evi2"):
        idx = srt.dropna(subset=[ind]).groupby(k)[ind].idxmax()
        m = srt.loc[idx, k + [ind, "doy"]].rename(columns={ind: f"{ind}_max", "doy": f"doy_{ind}_max"})
        out = out.merge(m, on=k, how="left")
    ja = ls[ls["mes"].isin([7, 8])]
    out = out.merge(ja.groupby(k)["ndvi"].mean().round(4).rename("ndvi_media_jul_ago").reset_index(), on=k, how="left")
    for nom, meses in (("n_obs_mar_nov", range(3, 12)), ("n_obs_may_jun", [5, 6]), ("n_obs_jul_ago", [7, 8])):
        c = ls[ls["mes"].isin(list(meses))].groupby(k).size().rename(nom).reset_index()
        out = out.merge(c, on=k, how="left")
        out[nom] = out[nom].fillna(0).astype(int)
    s2 = obs[obs["producto"] == "hls_s30"]
    if len(s2):
        out = out.merge(s2.groupby(k)["ndvi"].max().rename("ndvi_max_s2").reset_index(), on=k, how="left")
        j2 = s2[s2["fecha"].str[5:7].isin(["07", "08"])].groupby(k).size().rename("n_obs_jul_ago_s2").reset_index()
        out = out.merge(j2, on=k, how="left")
        hls_anios = set(s2["anio"].unique())
        out.loc[out["anio"].isin(hls_anios), "n_obs_jul_ago_s2"] = out.loc[out["anio"].isin(hls_anios),
                                                                            "n_obs_jul_ago_s2"].fillna(0)
        out["n_obs_jul_ago_s2"] = out["n_obs_jul_ago_s2"].astype("Int64")
    for c in ("doy_ndvi_max", "doy_evi2_max"):
        out[c] = out[c].astype("Int64")
    return out.sort_values(k).reset_index(drop=True)


def _desnudo(ls: pd.DataFrame, k: list[str], suf: str) -> pd.DataFrame:
    cols = ["refl_blue", "refl_red", "refl_nir", "refl_swir1", "refl_swir2"]
    m = ls.groupby(k)[cols].median()
    m["nbr2"] = (m["refl_swir1"] - m["refl_swir2"]) / (m["refl_swir1"] + m["refl_swir2"])
    m = m.round(4)
    m["n_obs"] = ls.groupby(k).size()
    return m.rename(columns={c: f"{c}{suf}" for c in m.columns}).reset_index()


def suelo_desnudo(obs: pd.DataFrame, px: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ls = obs[(obs["producto"] == "landsat_c2_l2") & (obs["ndvi"] < 0.25)]
    md = ls["fecha"].str[5:10]
    prim = ls[(md >= "03-15") & (md <= "05-15")]
    oto = ls[(md >= "10-01") & (md <= "11-30")]
    k = ["fips", "id_lote", "px_id", "anio"]
    a = _desnudo(prim, k, "_mar_may").merge(_desnudo(oto, k, "_oct_nov"), on=k, how="outer")
    for c in ("n_obs_mar_may", "n_obs_oct_nov"):
        a[c] = a[c].fillna(0).astype(int)
    a = a.sort_values(k).reset_index(drop=True)
    comp = _desnudo(pd.concat([prim, oto]), ["fips", "id_lote", "px_id"], "")
    comp = px[["fips", "id_lote", "px_id"]].merge(comp, how="left")
    comp["n_obs"] = comp["n_obs"].fillna(0).astype(int)
    return a, comp.sort_values(["fips", "id_lote", "px_id"]).reset_index(drop=True)
