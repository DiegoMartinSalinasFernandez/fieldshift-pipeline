"""Procesa las ventanas Landsat C2 L2 de data/raw/teledeteccion/landsat/ → teledeteccion_anual.csv.

Por condado y año, sobre los píxeles agrícolas (mascara_agricola.tif) de las ventanas de muestreo
dentro del condado, con píxeles despejados según QA_PIXEL:
- pct_suelo_desnudo_abr_may / _oct_nov: % de píxeles con mediana de NDVI < 0,25 en el período
- pct_cobertura_verde_mar_abr: % con mediana de NDVI >= 0,3 entre el 15-03 y el 30-04
- bsi_abr_may: media de la mediana por píxel del BSI de abril–mayo
- ndvi_max_30m: media del NDVI máximo por píxel de abril–septiembre
- n_escenas_validas: escenas con al menos 10 % de los píxeles agrícolas despejados
- frac_pixeles_validos: observaciones despejadas / observaciones agrícolas leídas
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import Window

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src/teledeteccion"))
from data_card import escribir_card  # noqa: E402

RAW = REPO / "data/raw/teledeteccion/landsat"
INTERIM = REPO / "data/interim/teledeteccion"
OUT = REPO / "data/processed/teledeteccion"
LADO = 40
COLS = ["pct_suelo_desnudo_abr_may", "pct_suelo_desnudo_oct_nov", "pct_cobertura_verde_mar_abr",
        "bsi_abr_may", "ndvi_max_30m", "n_escenas_validas", "frac_pixeles_validos"]
# QA_PIXEL de Collection 2: 0 relleno, 1 nube dilatada, 2 cirro, 3 nube, 4 sombra, 5 nieve, 6 despejado, 7 agua
QA_MALO = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 7)
QA_DESPEJADO = 1 << 6
MIN_FRAC_ESCENA = 0.10


def mascaras_ventanas() -> dict[str, np.ndarray]:
    """Píxeles agrícolas y dentro del condado de cada ventana (clave fips_k)."""
    v = pd.read_csv(INTERIM / "ventanas.csv", dtype={"fips": str})
    cond = gpd.read_file(REPO / "data/reference/condados.gpkg")
    fcol = "fips" if "fips" in cond.columns else cond.columns[0]
    out = {}
    with rasterio.open(REPO / "data/reference/mascara_agricola.tif") as m:
        geo = dict(zip(cond[fcol].astype(str).str.zfill(5), cond.to_crs(m.crs).geometry))
        for r in v.itertuples():
            w = Window(r.col, r.row, LADO, LADO)
            a = m.read(1, window=w, boundless=True, fill_value=0)
            dentro = ~geometry_mask([geo[r.fips]], out_shape=a.shape, transform=m.window_transform(w))
            out[f"{r.fips}_{r.k}"] = ((a == 1) & dentro).ravel()
    return out


def indices(arr: np.ndarray, sel: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # 5 bandas (blue, red, nir08, swir16, qa_pixel) o 3 (red, nir08, qa_pixel: escenas fuera de
    # abril–mayo bajadas desde la ronda 2, sin BSI)
    if arr.shape[0] == 5:
        blue, red, nir, swir, qa = (arr[i].ravel()[sel] for i in range(5))
        dns = (blue, red, nir, swir)
    else:
        red, nir, qa = (arr[i].ravel()[sel] for i in range(3))
        dns = (red, nir)
    ok = ((qa & QA_MALO) == 0) & ((qa & QA_DESPEJADO) != 0)
    for dn in dns:
        ok &= (dn >= 7273) & (dn <= 43636)
    r, n = (x.astype(np.float64) * 2.75e-5 - 0.2 for x in (red, nir))
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (n - r) / (n + r)
        if arr.shape[0] == 5:
            b, s = (x.astype(np.float64) * 2.75e-5 - 0.2 for x in (blue, swir))
            bsi = ((s + r) - (n + b)) / ((s + r) + (n + b))
            ok &= np.isfinite(bsi)
        else:
            bsi = np.full_like(ndvi, np.nan)
    ok &= np.isfinite(ndvi)
    ndvi[~ok] = np.nan
    bsi[~ok] = np.nan
    return ndvi, bsi, ok


def metricas(obs: list[tuple[str, str, np.ndarray, np.ndarray, np.ndarray]], anio: int) -> dict:
    fechas = np.array([o[1] for o in obs])
    nd = np.stack([o[2] for o in obs])
    bs = np.stack([o[3] for o in obs])
    ok = np.stack([o[4] for o in obs])
    res = {}

    def periodo(ini, fin):
        return (fechas >= f"{anio}-{ini}") & (fechas <= f"{anio}-{fin}")

    def mediana(x, p):
        if not p.any():
            return None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            med = np.nanmedian(x[p], axis=0)
        med = med[np.isfinite(med)]
        return med if len(med) else None

    for col, ini, fin in [("pct_suelo_desnudo_abr_may", "04-01", "05-31"),
                          ("pct_suelo_desnudo_oct_nov", "10-01", "11-30")]:
        med = mediana(nd, periodo(ini, fin))
        res[col] = round(100 * float(np.mean(med < 0.25)), 2) if med is not None else None
    med = mediana(nd, periodo("03-15", "04-30"))
    res["pct_cobertura_verde_mar_abr"] = round(100 * float(np.mean(med >= 0.3)), 2) if med is not None else None
    med = mediana(bs, periodo("04-01", "05-31"))
    res["bsi_abr_may"] = round(float(np.mean(med)), 4) if med is not None else None
    p = periodo("04-01", "09-30")
    if p.any():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            mx = np.nanmax(nd[p], axis=0)
        mx = mx[np.isfinite(mx)]
        res["ndvi_max_30m"] = round(float(np.mean(mx)), 4) if len(mx) else None
    else:
        res["ndvi_max_30m"] = None
    res["n_escenas_validas"] = int((ok.mean(axis=1) >= MIN_FRAC_ESCENA).sum())
    res["frac_pixeles_validos"] = round(float(ok.mean()), 4)
    return res


def main() -> None:
    t0 = time.time()
    masc = mascaras_ventanas()
    print(f"máscaras de ventanas: {time.time() - t0:.0f} s", flush=True)
    filas = []
    for dir_anio in sorted(p for p in RAW.glob("*") if p.is_dir()):
        anio = int(dir_anio.name)
        obs: dict[str, dict[str, list]] = {}
        for f in sorted(dir_anio.glob("*.npz")):
            fecha_raw = f.stem.split("_")[3]
            fecha = f"{fecha_raw[:4]}-{fecha_raw[4:6]}-{fecha_raw[6:]}"
            with np.load(f) as z:
                for clave in sorted(z.files):
                    sel = masc.get(clave)
                    if sel is None or not sel.any():
                        continue
                    fips = clave.split("_")[0]
                    obs.setdefault(fips, {}).setdefault(f.stem, []).append(indices(z[clave], sel))
        for fips in sorted(obs):
            lista = []
            for esc in sorted(obs[fips]):
                partes = obs[fips][esc]
                fecha_raw = esc.split("_")[3]
                fecha = f"{fecha_raw[:4]}-{fecha_raw[4:6]}-{fecha_raw[6:]}"
                lista.append((esc, fecha, *(np.concatenate([p[i] for p in partes]) for i in range(3))))
            # todas las escenas de un condado tienen que tener las mismas ventanas
            n = {len(o[2]) for o in lista}
            if len(n) != 1:
                maxn = max(n)
                lista = [o for o in lista if len(o[2]) == maxn]
            filas.append({"fips": fips, "anio": anio, **metricas(lista, anio)})
        print(f"{anio}: {len(obs)} condados, {time.time() - t0:.0f} s", flush=True)
    df = pd.DataFrame(filas, columns=["fips", "anio"] + COLS)
    df["n_escenas_validas"] = df["n_escenas_validas"].astype("Int64")
    OUT.mkdir(parents=True, exist_ok=True)
    df.sort_values(["fips", "anio"]).to_csv(OUT / "teledeteccion_anual.csv", index=False,
                                            float_format="%.4f", lineterminator="\n")
    escribir_card(OUT / "teledeteccion_anual.csv")
    print(f"listo: {len(df)} filas en {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
