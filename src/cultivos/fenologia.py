"""fenologia_estado.csv desde NASS Crop Progress (nivel estado, semanal).

Por estado, año de cosecha (`anio`) y cultivo: día del año en que cada etapa cruza el 50 %
(interpolación lineal entre las dos semanas que lo rodean).

- Maíz y soja: sembrado, emergido, floración (SILKING / BLOOMING) y cosechado, igual que antes.
- Avena y trigo de invierno (T135, para_decidir #8): sembrado, emergido, espigado (HEADED) y
  cosechado. El espigado va en `doy_50_espigado`; `doy_50_floracion` queda vacía para ellos.
- Trigo de invierno: se siembra y emerge en otoño para la cosecha del año siguiente. Esas dos
  etapas van a la fila del `anio` de la cosecha, en `doy_50_sembrado_otono` y
  `doy_50_emergido_otono` (día del año calendario del otoño, es decir, de `anio − 1`). Sus
  `doy_50_sembrado` y `doy_50_emergido` quedan vacías: no hay siembra de primavera.
  El año se toma de `WEEK_ENDING` (agosto–diciembre → año + 1), no de `YEAR`, porque no se
  verificó qué `YEAR` pone Quick Stats a esas filas de otoño.
- `flag_hueco_50`: etapas (separadas por `;`) cuyo cruce del 50 % se interpoló entre dos semanas
  separadas por más de 14 días (p. ej., el cierre del gobierno de octubre de 2025). Vacía si
  ninguna.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

HUECO_MAX_DIAS = 14
MES_INICIO_OTONO = 8  # semanas de trigo de invierno desde agosto: siembra para la cosecha siguiente

# etapa -> {cultivo: (COMMODITY_DESC, CLASS_DESC o None, UNIT_DESC)}
ETAPAS = {
    "sembrado": {"maiz": ("CORN", None, "PCT PLANTED"), "soja": ("SOYBEANS", None, "PCT PLANTED"),
                 "avena": ("OATS", None, "PCT PLANTED")},
    "emergido": {"maiz": ("CORN", None, "PCT EMERGED"), "soja": ("SOYBEANS", None, "PCT EMERGED"),
                 "avena": ("OATS", None, "PCT EMERGED")},
    "floracion": {"maiz": ("CORN", None, "PCT SILKING"), "soja": ("SOYBEANS", None, "PCT BLOOMING")},
    "cosechado": {"maiz": ("CORN", None, "PCT HARVESTED"), "soja": ("SOYBEANS", None, "PCT HARVESTED"),
                  "avena": ("OATS", None, "PCT HARVESTED"),
                  "trigo_invierno": ("WHEAT", "WINTER", "PCT HARVESTED")},
    "espigado": {"avena": ("OATS", None, "PCT HEADED"),
                 "trigo_invierno": ("WHEAT", "WINTER", "PCT HEADED")},
    "sembrado_otono": {"trigo_invierno": ("WHEAT", "WINTER", "PCT PLANTED")},
    "emergido_otono": {"trigo_invierno": ("WHEAT", "WINTER", "PCT EMERGED")},
}
OTONO = {"sembrado_otono", "emergido_otono"}
# el maíz se cosecha para grano o silaje: el % cosechado es el de grano
UTIL = {("CORN", "PCT HARVESTED"): "GRAIN"}
COLUMNAS = [f"doy_50_{e}" for e in
            ["sembrado", "emergido", "floracion", "cosechado", "espigado", "sembrado_otono", "emergido_otono"]]


def pct_valor(s: pd.Series) -> pd.Series:
    """VALUE de NASS a número; códigos como (NA) o (D) quedan vacíos."""
    return pd.to_numeric(s.str.replace(",", "", regex=False).str.strip(), errors="coerce")


def cruce_50(g: pd.DataFrame) -> tuple[float, bool]:
    """(día en que el % acumulado cruza 50, si se interpoló sobre un hueco > HUECO_MAX_DIAS).

    `g` tiene `doy` (puede ser > 366 o negativo si se cuenta desde otro año) y `pct`.
    """
    g = g.sort_values("doy")
    x, y = g["doy"].to_numpy(float), g["pct"].to_numpy(float)
    if len(y) == 0 or y.max() < 50:
        return np.nan, False
    i = int(np.argmax(y >= 50))
    if i == 0:
        return (float(x[0]) if y[0] == 50 else np.nan), False
    doy = round(float(x[i - 1] + (50 - y[i - 1]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1])), 1)
    hueco = (x[i] - x[i - 1]) > HUECO_MAX_DIAS and y[i] != 50
    return doy, bool(hueco)


def fenologia_estado(crops: pd.DataFrame, anio_inicio: int, anio_fin: int) -> pd.DataFrame:
    d = crops[(crops["SOURCE_DESC"] == "SURVEY") & (crops["AGG_LEVEL_DESC"] == "STATE")
              & (crops["STATISTICCAT_DESC"] == "PROGRESS") & (crops["DOMAIN_DESC"] == "TOTAL")
              & (crops["WEEK_ENDING"] != "")]
    filas = []
    for etapa, por_cultivo in ETAPAS.items():
        for cultivo, (com, clase, unidad) in por_cultivo.items():
            m = ((d["COMMODITY_DESC"] == com) & (d["UNIT_DESC"] == unidad)
                 & (d["UTIL_PRACTICE_DESC"] == UTIL.get((com, unidad), "ALL UTILIZATION PRACTICES")))
            if clase is not None:
                m &= d["CLASS_DESC"] == clase
            dv = d[m].copy()
            if dv.empty:
                continue
            fecha = pd.to_datetime(dv["WEEK_ENDING"].str[:10])
            dv["doy"] = fecha.dt.day_of_year
            dv["anio"] = fecha.dt.year
            if etapa in OTONO:
                otono = fecha.dt.month >= MES_INICIO_OTONO
                dv = dv[otono.to_numpy()].copy()
                dv["anio"] = dv["anio"] + 1  # año de la cosecha
            dv["pct"] = pct_valor(dv["VALUE"])
            dv = dv.dropna(subset=["pct"]).drop_duplicates(["STATE_FIPS_CODE", "anio", "doy"])
            dv = dv[(dv["anio"] >= anio_inicio) & (dv["anio"] <= anio_fin)]
            for (est, anio), g in dv.groupby(["STATE_FIPS_CODE", "anio"]):
                doy, hueco = cruce_50(g)
                filas.append({"fips_estado": str(est).zfill(2), "anio": int(anio), "cultivo": cultivo,
                              "etapa": etapa, "doy": doy, "hueco": hueco})
    claves = ["fips_estado", "anio", "cultivo"]
    if not filas:
        return pd.DataFrame(columns=claves + COLUMNAS + ["flag_hueco_50"])
    largo = pd.DataFrame(filas)
    ancho = largo.pivot(index=claves, columns="etapa", values="doy")
    ancho.columns = [f"doy_50_{c}" for c in ancho.columns]
    ancho = ancho.reindex(columns=COLUMNAS)
    orden = {e: k for k, e in enumerate(ETAPAS)}
    flag = (largo[largo["hueco"]].assign(k=lambda t: t["etapa"].map(orden)).sort_values("k")
            .groupby(claves)["etapa"].agg(";".join))
    ancho["flag_hueco_50"] = flag.reindex(ancho.index)
    return ancho.reset_index().sort_values(claves).reset_index(drop=True)
