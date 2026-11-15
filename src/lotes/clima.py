"""Clima del lote: NASA POWER diario (comunidad AG) en el centroide de cada lote y la precipitación IMERG
(parámetro IMERG_PRECTOT de la misma API, celda de 0,1° que cubre el centroide). Mismas variables, nombres y
cálculos que src/clima (ETo FAO-56, GDD 10/30). SMAP L4 diario de Crop-CASMA desde los GeoTIFF que bajó el paquete agua.

Descarga: python src/lotes/download.py clima → data/raw/lotes/clima/power_<id_lote>.csv e imerg_<id_lote>.csv
"""
from __future__ import annotations

import datetime as dt
import io
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "lotes" / "clima"
INTERIM = RAIZ / "data" / "interim" / "lotes"
URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
sys.path.insert(0, str(RAIZ))
from src.clima.download import PARAMS  # noqa: E402
from src.clima.process import FILL, RENOMBRE, eto_fao56  # noqa: E402

INICIO, FIN = "19991101", "20251231"
CLAVES = ["fips", "id_lote", "anio", "fecha"]


def _consultas(lat: float, lon: float) -> dict[str, dict]:
    return {
        "power": {"parameters": ",".join(PARAMS), "community": "AG", "longitude": f"{lon:.5f}",
                  "latitude": f"{lat:.5f}", "start": INICIO, "end": FIN, "format": "CSV"},
        "imerg": {"parameters": "IMERG_PRECTOT", "community": "AG", "longitude": f"{lon:.2f}",
                  "latitude": f"{lat:.2f}", "start": "20000601", "end": FIN, "format": "CSV", "time-standard": "UTC"},
    }


def bajar(upsert) -> None:
    lotes = pd.read_csv(RAIZ / "data/processed/lotes/lotes.csv", dtype={"fips": str})
    filas, hoy = [], dt.date.today().isoformat()
    for r in lotes.itertuples():
        for tipo, q in _consultas(r.lat_centroide, r.lon_centroide).items():
            dest = RAW / f"{tipo}_{r.id_lote}.csv"
            url = requests.Request("GET", URL, params=q).prepare().url
            if not dest.exists():
                for intento in range(5):
                    rr = requests.get(URL, params=q, timeout=300)
                    if rr.status_code == 429:
                        time.sleep(10 * (intento + 1))
                        continue
                    rr.raise_for_status()
                    if "-END HEADER-" not in rr.text or "2025,365," not in rr.text:
                        raise ValueError(f"respuesta incompleta {dest.name}")
                    part = INTERIM / "parciales" / (dest.name + ".part")
                    part.parent.mkdir(parents=True, exist_ok=True)
                    part.write_bytes(rr.content)
                    RAW.mkdir(parents=True, exist_ok=True)
                    os.replace(part, dest)
                    break
            filas.append({"paquete": "lotes", "archivo": dest.relative_to(RAIZ).as_posix(), "fuente": "NASA POWER",
                          "producto": ("POWER daily point API, community AG (" + ",".join(PARAMS) + ")") if tipo == "power"
                          else "POWER daily point API, IMERG_PRECTOT (GPM IMERG Final, celda 0,1°)",
                          "version": "POWER v2 (API temporal/daily/point)", "fecha_descarga": hoy, "consulta_o_url": url})
    upsert(filas)


SMAP = RAIZ / "data" / "raw" / "agua" / "smap"
SM_MAX = 0.60  # mismo corte que el paquete agua (suelos orgánicos fuera del rango físico)


def smap(lotes: pd.DataFrame) -> pd.DataFrame:
    """SMAP L4 diario de Crop-CASMA ya bajado por el paquete agua (GeoTIFF 9 km por estado, EPSG:5070): valor de
    la celda que contiene el centroide del lote. SUB = zona radicular, TOP = superficie."""
    import rasterio
    from pyproj import Transformer
    a5070 = Transformer.from_crs(4326, 5070, always_xy=True)
    lotes = lotes.sort_values("id_lote")
    xs, ys = a5070.transform(lotes["lon_centroide"].values, lotes["lat_centroide"].values)
    pts: dict[str, list] = {}
    for lid, f, x, y in zip(lotes["id_lote"], lotes["fips"], xs, ys):
        pts.setdefault(f[:2], []).append((lid, f, x, y))
    filas = []
    for ruta in sorted(SMAP.glob("*/SMAP-9KM-DAILY-*_FIPS_*.tif")):
        partes = ruta.stem.split("_")
        capa, fecha, est = partes[0].split("-")[-1], partes[1].replace(".", "-"), partes[-1]
        if est not in pts:
            continue
        with rasterio.open(ruta) as src:
            vals = [float(v[0]) for v in src.sample([(x, y) for _, _, x, y in pts[est]])]
            nod = src.nodata
        for (lid, f, _, _), v in zip(pts[est], vals):
            if (nod is not None and v == nod) or not np.isfinite(v) or v < 0 or v > SM_MAX:
                v = np.nan
            filas.append((f, lid, fecha, capa, v))
    df = pd.DataFrame(filas, columns=["fips", "id_lote", "fecha", "capa", "v"])
    df = df.pivot_table(index=["fips", "id_lote", "fecha"], columns="capa", values="v", aggfunc="first",
                        dropna=False).reset_index()
    df = df.rename(columns={"SUB": "sm_rootzone_m3m3", "TOP": "sm_surface_m3m3"})
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df[["fips", "id_lote", "fecha", "sm_rootzone_m3m3", "sm_surface_m3m3"]]


def _leer(p: Path) -> tuple[pd.DataFrame, float, float]:
    txt = p.read_text(encoding="utf-8")
    cab, cuerpo = txt.split("-END HEADER-", 1)
    m = re.search(r"=\s*([-\d.]+)\s*meters", cab)
    elev = float(m.group(1)) if m else np.nan
    lat = float(re.search(r"latitude\s+([-\d.]+)", cab).group(1))
    df = pd.read_csv(io.StringIO(cuerpo.strip())).replace(FILL, np.nan)
    df["fecha"] = pd.to_datetime(df["YEAR"].astype(str), format="%Y") + pd.to_timedelta(df["DOY"] - 1, unit="D")
    return df.drop(columns=["YEAR", "DOY"]), elev, lat


def diario(lotes: pd.DataFrame) -> pd.DataFrame:
    partes = []
    for r in lotes.sort_values("id_lote").itertuples():
        d, elev, lat = _leer(RAW / f"power_{r.id_lote}.csv")
        d = d.rename(columns=RENOMBRE)
        d["elev_m"], d["lat"] = elev, lat
        im, _, _ = _leer(RAW / f"imerg_{r.id_lote}.csv")
        d = d.merge(im.rename(columns={"IMERG_PRECTOT": "prec_imerg_mm"}), on="fecha", how="left")
        d["eto_pm_mm"] = eto_fao56(d)
        d.insert(0, "id_lote", r.id_lote)
        d.insert(0, "fips", r.fips)
        partes.append(d)
    d = pd.concat(partes, ignore_index=True)
    d["deficit_mm"] = d["prec_power_mm"] - d["eto_pm_mm"]
    d = d.merge(smap(lotes), on=["fips", "id_lote", "fecha"], how="left")
    d["anio"] = d["fecha"].dt.year
    return d


def anual(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    tx = d["tmax_c"].clip(upper=30)
    tn = d["tmin_c"].clip(lower=10, upper=30)
    d["gdd"] = ((tx.clip(lower=10) + tn) / 2 - 10).clip(lower=0)
    d["mes"] = d["fecha"].dt.month
    # invierno previo: noviembre-diciembre cuentan para el año siguiente
    d["anio_inv"] = d["anio"] + (d["mes"] >= 11).astype(int)
    k = ["fips", "id_lote", "anio"]
    d = d[d["anio"] >= 2000]
    temp = d[d["mes"].between(4, 9)]
    g = temp.groupby(k)
    out = pd.DataFrame({"prec_temporada_mm": g["prec_power_mm"].sum(min_count=183),
                        "deficit_temporada_mm": g["deficit_mm"].sum(min_count=183),
                        "gdd_temporada": g["gdd"].sum(min_count=183),
                        "prec_temporada_imerg_mm": g["prec_imerg_mm"].sum(min_count=183)})
    for nom, mes, dias in (("abr", 4, 30), ("may", 5, 31), ("jul", 7, 31), ("ago", 8, 31)):
        s = d[d["mes"] == mes].groupby(k)
        out[f"prec_{nom}_mm"] = s["prec_power_mm"].sum(min_count=dias)
        out[f"prec_{nom}_imerg_mm"] = s["prec_imerg_mm"].sum(min_count=dias)
    jul = d[d["mes"] == 7].groupby(k)
    out["dias_tmax_gt30_jul"] = jul["tmax_c"].apply(lambda s: (s > 30).sum() if s.notna().all() else np.nan)
    out["tmax_jul_c"] = jul["tmax_c"].mean()
    am = d[d["mes"].isin([4, 5])].groupby(k)
    out["dias_lluvia_gt50_abr_may"] = am["prec_power_mm"].apply(lambda s: (s > 50).sum() if s.notna().all() else np.nan)
    out["dias_lluvia_gt50_abr_may_imerg"] = am["prec_imerg_mm"].apply(
        lambda s: (s > 50).sum() if s.notna().all() else np.nan)
    inv = d.drop(columns="anio").rename(columns={"anio_inv": "anio"})
    inv = inv[inv["mes"].isin([11, 12, 1, 2, 3])].groupby(k)["prec_power_mm"].sum(min_count=150)
    out["prec_invierno_previo_mm"] = inv
    out["sm_rootzone_temporada_m3m3"] = g["sm_rootzone_m3m3"].mean().where(g["sm_rootzone_m3m3"].count() >= 150)
    out = out.reset_index()
    out = out[out["anio"].between(2000, 2025)]
    cols = ["prec_temporada_mm", "prec_abr_mm", "prec_may_mm", "prec_jul_mm", "prec_ago_mm", "deficit_temporada_mm",
            "dias_tmax_gt30_jul", "tmax_jul_c", "gdd_temporada", "prec_invierno_previo_mm", "dias_lluvia_gt50_abr_may",
            "prec_temporada_imerg_mm", "prec_abr_imerg_mm", "prec_may_imerg_mm", "prec_jul_imerg_mm",
            "prec_ago_imerg_mm", "dias_lluvia_gt50_abr_may_imerg", "sm_rootzone_temporada_m3m3"]
    out = out[k + cols].sort_values(k).reset_index(drop=True)
    for c in ("dias_tmax_gt30_jul", "dias_lluvia_gt50_abr_may", "dias_lluvia_gt50_abr_may_imerg"):
        out[c] = out[c].astype("Int64")
    for c in cols:
        if not c.startswith("dias"):
            out[c] = out[c].round(3)
    return out


def salida_diaria(d: pd.DataFrame) -> pd.DataFrame:
    d = d[d["anio"] >= 2000].copy()
    d["fecha"] = d["fecha"].dt.strftime("%Y-%m-%d")
    cols = ["prec_power_mm", "tmax_c", "tmin_c", "tmed_c", "hr_pct", "viento_ms", "rad_mj_m2", "eto_pm_mm",
            "deficit_mm", "prec_imerg_mm", "sm_rootzone_m3m3", "sm_surface_m3m3"]
    for c in cols:
        d[c] = d[c].round(3)
    return d[CLAVES + cols].sort_values(CLAVES).reset_index(drop=True)
