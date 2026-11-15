"""Análogos climáticos Argentina ↔ Corn Belt: qué departamentos y provincias se parecen a los condados con los
que se entrenan los modelos.

Fuente única: NASA POWER mensual (AG), 2001-2024, en el centroide de cada departamento (Georef) y de cada condado
(los 10 estados de unido_10_estados). La temporada se alinea por hemisferio: abril-septiembre en EE.UU. con
octubre-marzo en Argentina (mes de temporada 1 a 6; el 4 es julio en EE.UU. y enero en Argentina, la floración
del maíz). El invierno previo es noviembre-marzo en EE.UU. y mayo-septiembre en Argentina.

Variables de similitud por punto (media 2001-2024 salvo las de variabilidad), 16 en total, elegidas entre las
que usan los modelos de rendimiento (temperatura, calor, lluvia y su variabilidad):
- temperatura media (T2M) y lluvia de cada mes de temporada (mm del mes: PRECTOTCORR en mm/día × días del mes);
- máxima absoluta del mes 4 (T2M_MAX mensual de POWER es la máxima del mes, no la media de las máximas): calor
  en floración;
- lluvia del invierno previo (mm), desvío estándar entre años de la lluvia de la temporada (mm) y de la tmax
  absoluta media de la temporada (°C).

La radiación (ALLSKY_SFC_SW_DWN) y la mínima absoluta del mes 1 (helada de primavera) no entran en la distancia:
en la región pampeana están fuera del rango de los 919 condados en casi todos los departamentos (más radiación
por la menor latitud y primaveras sin heladas fuertes). Van aparte, como diferencia contra el condado análogo
(dif_rad_temporada, dif_tmin_abs_t1), para que el equipo de ML entrene sin esas variables o las trate aparte.

Se estandarizan con la media y el desvío de los 919 condados. Medidas:
- d_vecino: distancia (RMS por variable, en desvíos) al condado más parecido; para cada condado se calcula lo
  mismo contra los otros condados.
- mahal: distancia de Mahalanobis a la nube de condados, en las componentes principales que explican el 95 %.
- n_fuera_rango y vars_fuera_rango: variables del departamento fuera del rango (mín-máx) de los 919 condados. Un
  modelo de árboles no extrapola fuera de ese rango.
- dentro_dominio: ninguna variable fuera de rango y mahal ≤ percentil 99 de los condados. Es el criterio para usar
  ahí un modelo entrenado en el Corn Belt sin extrapolar el clima.

Bloque aparte de clima + suelo: si existe data/processed/analogos/suelo_sg.csv (src/analogos/suelo.py, SoilGrids en
los dos lados), se repiten las mismas medidas con las 16 variables de clima y 4 de suelo 0-30 cm (arcilla, arena,
carbono orgánico y pH) para los departamentos de las 5 provincias pampeanas. Columnas con sufijo _cs y
n_fuera_rango_suelo. El clima solo no cambia.

Salidas en data/processed/analogos/: analogos_departamento.csv, analogos_provincia.csv, analogos_condado_ref.csv y
analogos_meta.json.
Uso: python src/analogos/process.py
"""
from __future__ import annotations

import calendar
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "analogos"
OUT = RAIZ / "data" / "processed" / "analogos"
TEMP_US, TEMP_AR = [4, 5, 6, 7, 8, 9], [10, 11, 12, 1, 2, 3]
INV_US, INV_AR = [11, 12, 1, 2, 3], [5, 6, 7, 8, 9]
INICIO, FIN = 2001, 2024
RELLENO = -999
SUELO = ["arcilla_sg_pct", "arena_sg_pct", "soc_sg_g_kg", "ph_sg"]


def serie(pid: str) -> pd.DataFrame:
    """Mensual por año y mes: tmax, tmin, prec_mm, rad. Valores de relleno de POWER a vacío."""
    j = json.loads((RAW / "power" / f"{pid}.json").read_text(encoding="utf-8"))
    par = j["properties"]["parameter"]
    filas = []
    for k in par["T2M_MAX"]:
        anio, mes = int(k[:4]), int(k[4:])
        if mes == 13:
            continue
        v = {n: par[n][k] for n in ("T2M_MAX", "T2M_MIN", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN")}
        v = {n: (np.nan if x is None or x <= RELLENO else x) for n, x in v.items()}
        tm = par["T2M"][k]
        filas.append({"anio": anio, "mes": mes, "tmed": np.nan if tm is None or tm <= RELLENO else tm,
                      "tmax": v["T2M_MAX"], "tmin": v["T2M_MIN"],
                      "prec": v["PRECTOTCORR"] * calendar.monthrange(anio, mes)[1], "rad": v["ALLSKY_SFC_SW_DWN"]})
    return pd.DataFrame(filas)


def variables(df: pd.DataFrame, temp: list[int], inv: list[int], sur: bool) -> dict:
    out = {}
    clim = df.groupby("mes")[["tmed", "tmax", "tmin", "prec", "rad"]].mean()
    for i, m in enumerate(temp, start=1):
        out[f"tmed_t{i}"] = clim.loc[m, "tmed"]
        out[f"prec_t{i}"] = clim.loc[m, "prec"]
    out["tmax_abs_t4"] = clim.loc[temp[3], "tmax"]
    d = df.copy()
    # año de temporada: en el sur, octubre-diciembre pertenecen a la campaña que termina el año siguiente
    d["anio_t"] = d["anio"] + ((d["mes"] >= 10) if sur else 0)
    t = d[d["mes"].isin(temp)].groupby("anio_t").agg(prec=("prec", "sum"), tmax=("tmax", "mean"), n=("mes", "size"))
    t = t[t["n"] == 6]
    out["prec_temp_sd"] = t["prec"].std()
    out["tmax_temp_sd"] = t["tmax"].std()
    d["anio_i"] = d["anio"] + ((d["mes"] >= 11) if not sur else 0)
    w = d[d["mes"].isin(inv)].groupby("anio_i").agg(prec=("prec", "sum"), n=("mes", "size"))
    out["prec_invierno"] = w.loc[w["n"] == len(inv), "prec"].mean()
    # aparte (no entran en la distancia)
    out["x_rad_temporada"] = clim.loc[temp, "rad"].mean()
    out["x_tmin_abs_t1"] = clim.loc[temp[0], "tmin"]
    return out


def medir(us: pd.DataFrame, ar: pd.DataFrame) -> dict:
    """Distancias de cada departamento (filas de ar) a la nube de condados (filas de us), con las columnas dadas.

    Estandariza con la media y el desvío de los condados. Devuelve fuera (variables fuera del rango de los
    condados), orden (los 3 condados más parecidos), d_ar y d_us (distancia RMS al vecino), m_ar y m_us
    (Mahalanobis en las componentes que explican el 95 %), lim_m (percentil 99 de m_us) y q (componentes).
    """
    mu, sd = us.mean(), us.std(ddof=0)
    zu, za = ((us - mu) / sd).to_numpy(), ((ar - mu) / sd).to_numpy()
    fuera = ~(ar.ge(us.min()) & ar.le(us.max()))
    k = us.shape[1]

    def dist(a, b):  # RMS por variable
        return np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1) / k)

    duu = dist(zu, zu)
    np.fill_diagonal(duu, np.inf)
    dau = dist(za, zu)
    orden = np.argsort(dau, axis=1)[:, :3]
    u, s, vt = np.linalg.svd(zu - zu.mean(0), full_matrices=False)
    var = s ** 2 / (len(zu) - 1)
    q = int(np.searchsorted(np.cumsum(var) / var.sum(), 0.95) + 1)
    proy = lambda z: ((z - zu.mean(0)) @ vt[:q].T) / np.sqrt(var[:q])
    m_us = np.sqrt((proy(zu) ** 2).sum(1))
    return {"fuera": fuera, "orden": orden, "d_ar": dau[np.arange(len(za)), orden[:, 0]], "d_us": duu.min(1),
            "m_ar": np.sqrt((proy(za) ** 2).sum(1)), "m_us": m_us, "lim_m": float(np.percentile(m_us, 99)), "q": q}


def con_suelo(us: pd.DataFrame, ar_ok: pd.DataFrame, cols: list[str], cond: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clima + suelo (SoilGrids, suelo_sg.csv): las mismas medidas con las 16 variables de clima y las 4 de suelo."""
    sg = pd.read_csv(OUT / "suelo_sg.csv", dtype={"id": str})
    us_s = sg[sg["lado"] == "us"].set_index("id")[SUELO]
    ar_s = sg[sg["lado"] == "ar"].set_index("id")[SUELO].dropna()
    if us_s.reindex(us.index).isna().any().any():
        raise SystemExit("condados sin suelo en suelo_sg.csv")
    U = us[cols].join(us_s)
    A = ar_ok[cols].join(ar_s, how="inner")
    r = medir(U, A)
    fips = U.index.to_numpy()
    fuera_s = ~(ar_s.ge(us_s.min()) & ar_s.le(us_s.max()))
    filas = []
    for i, idd in enumerate(A.index):
        vf = [c for c in U.columns if r["fuera"].loc[idd, c]]
        j0 = r["orden"][i, 0]
        filas.append({"id_depto": idd, **{c: round(float(A.loc[idd, c]), 2) for c in SUELO},
                      "n_fuera_rango_suelo": int(fuera_s.loc[idd].sum()),
                      "fips_analogo_cs": fips[j0], "estado_analogo_cs": cond.loc[fips[j0], "estado"],
                      "d_vecino_cs": round(r["d_ar"][i], 3), "mahal_cs": round(r["m_ar"][i], 3),
                      "n_fuera_rango_cs": len(vf), "vars_fuera_rango_cs": ";".join(vf),
                      "dentro_dominio_cs": bool(not vf and r["m_ar"][i] <= r["lim_m"])})
    meta = {"variables_suelo": SUELO, "componentes_cs": r["q"], "limite_mahal_p99_cs": round(r["lim_m"], 3),
            "rango_suelo_condados": {c: [round(float(us_s[c].min()), 2), round(float(us_s[c].max()), 2)] for c in SUELO}}
    return pd.DataFrame(filas), meta


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    deptos = json.loads((RAW / "georef_departamentos.json").read_text(encoding="utf-8"))["departamentos"]
    cond = pd.read_csv(RAIZ / "data" / "reference" / "condados_cornbelt_10.csv", dtype={"fips": str})
    us = pd.DataFrame([{"fips": r.fips, **variables(serie(f"us_{r.fips}"), TEMP_US, INV_US, False)}
                       for r in cond.itertuples()]).set_index("fips")
    ar = pd.DataFrame([{"id_depto": d["id"], **variables(serie(f"ar_{d['id']}"), TEMP_AR, INV_AR, True)}
                       for d in deptos]).set_index("id_depto")
    extra = [c for c in us.columns if c.startswith("x_")]
    cols = [c for c in us.columns if c not in extra]
    if us.isna().any().any():
        raise SystemExit(f"condados con variables vacías: {us[us.isna().any(axis=1)].index.tolist()[:10]}")
    ar_ok = ar.dropna()
    r = medir(us[cols], ar_ok[cols])
    fuera, orden, d_ar, d_us, m_ar, m_us, lim_m, q = (r[k] for k in ("fuera", "orden", "d_ar", "d_us", "m_ar", "m_us",
                                                                     "lim_m", "q"))

    fips = us.index.to_numpy()
    est = cond.set_index("fips")
    filas = []
    info = {d["id"]: d for d in deptos}
    for i, idd in enumerate(ar_ok.index):
        d = info[idd]
        j0 = orden[i, 0]
        vf = [c for c in cols if fuera.loc[idd, c]]
        filas.append({"id_depto": idd, "departamento": d["nombre"], "id_provincia": d["provincia"]["id"],
                      "provincia": d["provincia"]["nombre"], "lat_centroide": round(d["centroide"]["lat"], 5),
                      "lon_centroide": round(d["centroide"]["lon"], 5),
                      "fips_analogo": fips[j0], "condado_analogo": est.loc[fips[j0], "condado"],
                      "estado_analogo": est.loc[fips[j0], "estado"],
                      "fips_analogo_2": fips[orden[i, 1]], "fips_analogo_3": fips[orden[i, 2]],
                      "d_vecino": round(d_ar[i], 3), "mahal": round(m_ar[i], 3),
                      "n_fuera_rango": len(vf), "vars_fuera_rango": ";".join(vf),
                      "dentro_dominio": bool(not vf and m_ar[i] <= lim_m),
                      "dif_rad_temporada": round(ar_ok.loc[idd, "x_rad_temporada"] - us.loc[fips[j0], "x_rad_temporada"], 2),
                      "dif_tmin_abs_t1": round(ar_ok.loc[idd, "x_tmin_abs_t1"] - us.loc[fips[j0], "x_tmin_abs_t1"], 2)})
    dep = pd.DataFrame(filas)
    sin = sorted(set(ar.index) - set(ar_ok.index))
    for idd in sin:
        d = info[idd]
        dep.loc[len(dep)] = {"id_depto": idd, "departamento": d["nombre"], "id_provincia": d["provincia"]["id"],
                             "provincia": d["provincia"]["nombre"], "lat_centroide": d["centroide"]["lat"],
                             "lon_centroide": d["centroide"]["lon"]}
    meta_cs = {}
    if (OUT / "suelo_sg.csv").exists():
        cs, meta_cs = con_suelo(us, ar_ok, cols, est)
        dep = dep.merge(cs, on="id_depto", how="left")
        for c in ("n_fuera_rango_suelo", "n_fuera_rango_cs"):
            dep[c] = dep[c].astype("Int64")
    dep = dep.sort_values(["id_provincia", "id_depto"])
    dep.to_csv(OUT / "analogos_departamento.csv", index=False, encoding="utf-8", lineterminator="\n")

    ok = dep.dropna(subset=["d_vecino"])
    prov = (ok.groupby(["id_provincia", "provincia"])
            .agg(n_departamentos=("id_depto", "size"), n_dentro_dominio=("dentro_dominio", "sum"),
                 d_vecino_mediana=("d_vecino", "median"), mahal_mediana=("mahal", "median"),
                 n_fuera_rango_mediana=("n_fuera_rango", "median"),
                 dif_rad_temporada_mediana=("dif_rad_temporada", "median"),
                 estado_analogo_mas_comun=("estado_analogo", lambda x: x.mode().iat[0]))
            .reset_index())
    if meta_cs:
        cs_prov = ok.dropna(subset=["d_vecino_cs"]).groupby("id_provincia").agg(
            n_con_suelo=("id_depto", "size"), n_dentro_dominio_cs=("dentro_dominio_cs", "sum"),
            n_fuera_rango_cs_mediana=("n_fuera_rango_cs", "median"))
        prov = prov.merge(cs_prov.reset_index(), on="id_provincia", how="left")
        prov[["n_con_suelo", "n_dentro_dominio_cs"]] = prov[["n_con_suelo", "n_dentro_dominio_cs"]].astype("Int64")
    prov["pct_dentro_dominio"] = (100 * prov["n_dentro_dominio"] / prov["n_departamentos"]).round(1)
    prov = prov.sort_values(["pct_dentro_dominio", "d_vecino_mediana"], ascending=[False, True])
    prov.round(3).to_csv(OUT / "analogos_provincia.csv", index=False, encoding="utf-8", lineterminator="\n")

    ref = pd.DataFrame({"fips": fips, "d_vecino": d_us.round(3), "mahal": m_us.round(3)})
    ref.to_csv(OUT / "analogos_condado_ref.csv", index=False, encoding="utf-8", lineterminator="\n")
    meta = {"variables": cols, "aparte": extra, "componentes": q, "limite_mahal_p99": round(float(lim_m), 3),
            "d_vecino_condados_p50_p99": [round(float(np.percentile(d_us, 50)), 3), round(float(np.percentile(d_us, 99)), 3)],
            "departamentos_sin_dato": sin,
            "periodo": [INICIO, FIN], **meta_cs}
    (OUT / "analogos_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))
    print(prov.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
