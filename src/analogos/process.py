"""Análogos climáticos Argentina ↔ Corn Belt: qué departamentos y provincias se parecen a los condados con los
que se entrenan los modelos.

Fuente única: NASA POWER mensual (AG), 2001-2024, en el centroide de cada departamento (Georef) y de cada condado
(los 9 estados de unido_9_estados). La temporada se alinea por hemisferio: abril-septiembre en EE.UU. con
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
en la región pampeana están fuera del rango de los 814 condados en casi todos los departamentos (más radiación
por la menor latitud y primaveras sin heladas fuertes). Van aparte, como diferencia contra el condado análogo
(dif_rad_temporada, dif_tmin_abs_t1), para que el equipo de ML entrene sin esas variables o las trate aparte.

Se estandarizan con la media y el desvío de los 814 condados. Medidas:
- d_vecino: distancia (RMS por variable, en desvíos) al condado más parecido; para cada condado se calcula lo
  mismo contra los otros condados.
- mahal: distancia de Mahalanobis a la nube de condados, en las componentes principales que explican el 95 %.
- n_fuera_rango y vars_fuera_rango: variables del departamento fuera del rango (mín-máx) de los 814 condados. Un
  modelo de árboles no extrapola fuera de ese rango.
- dentro_dominio: ninguna variable fuera de rango y mahal ≤ percentil 99 de los condados. Es el criterio para usar
  ahí un modelo entrenado en el Corn Belt sin extrapolar el clima.

No hay datos de rendimiento ni de suelo de Argentina todavía: esto mide solo el clima.

Salidas en data/processed/analogos/: analogos_departamento.csv, analogos_provincia.csv y analogos_condado_ref.csv.
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


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    deptos = json.loads((RAW / "georef_departamentos.json").read_text(encoding="utf-8"))["departamentos"]
    cond = pd.read_csv(RAIZ / "data" / "reference" / "condados_cornbelt_9.csv", dtype={"fips": str})
    us = pd.DataFrame([{"fips": r.fips, **variables(serie(f"us_{r.fips}"), TEMP_US, INV_US, False)}
                       for r in cond.itertuples()]).set_index("fips")
    ar = pd.DataFrame([{"id_depto": d["id"], **variables(serie(f"ar_{d['id']}"), TEMP_AR, INV_AR, True)}
                       for d in deptos]).set_index("id_depto")
    extra = [c for c in us.columns if c.startswith("x_")]
    cols = [c for c in us.columns if c not in extra]
    if us.isna().any().any():
        raise SystemExit(f"condados con variables vacías: {us[us.isna().any(axis=1)].index.tolist()[:10]}")
    ar_ok = ar.dropna()
    mu, sd = us[cols].mean(), us[cols].std(ddof=0)
    zu, za = ((us[cols] - mu) / sd).to_numpy(), ((ar_ok[cols] - mu) / sd).to_numpy()
    lo, hi = us[cols].min(), us[cols].max()
    fuera = ~(ar_ok[cols].ge(lo) & ar_ok[cols].le(hi))
    k = len(cols)

    def dist(a, b):  # RMS por variable
        return np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1) / k)

    duu = dist(zu, zu)
    np.fill_diagonal(duu, np.inf)
    d_us = duu.min(1)
    dau = dist(za, zu)
    orden = np.argsort(dau, axis=1)[:, :3]
    d_ar = dau[np.arange(len(za)), orden[:, 0]]

    # Mahalanobis en componentes principales (95 % de la varianza de los condados)
    u, s, vt = np.linalg.svd(zu - zu.mean(0), full_matrices=False)
    var = s ** 2 / (len(zu) - 1)
    q = int(np.searchsorted(np.cumsum(var) / var.sum(), 0.95) + 1)
    proy = lambda z: ((z - zu.mean(0)) @ vt[:q].T) / np.sqrt(var[:q])
    m_us = np.sqrt((proy(zu) ** 2).sum(1))
    m_ar = np.sqrt((proy(za) ** 2).sum(1))
    lim_m = np.percentile(m_us, 99)

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
    prov["pct_dentro_dominio"] = (100 * prov["n_dentro_dominio"] / prov["n_departamentos"]).round(1)
    prov = prov.sort_values(["pct_dentro_dominio", "d_vecino_mediana"], ascending=[False, True])
    prov.round(3).to_csv(OUT / "analogos_provincia.csv", index=False, encoding="utf-8", lineterminator="\n")

    ref = pd.DataFrame({"fips": fips, "d_vecino": d_us.round(3), "mahal": m_us.round(3)})
    ref.to_csv(OUT / "analogos_condado_ref.csv", index=False, encoding="utf-8", lineterminator="\n")
    meta = {"variables": cols, "aparte": extra, "componentes": q, "limite_mahal_p99": round(float(lim_m), 3),
            "d_vecino_condados_p50_p99": [round(float(np.percentile(d_us, 50)), 3), round(float(np.percentile(d_us, 99)), 3)],
            "departamentos_sin_dato": sin,
            "periodo": [INICIO, FIN]}
    (OUT / "analogos_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))
    print(prov.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
