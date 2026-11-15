"""Paquete economia — precios recibidos (NASS) y costos y retornos (ERS) por estado y año.

Entradas:
- data/raw/cultivos/nass/qs.crops_*.txt.gz (volcado público de Quick Stats que bajó el paquete
  cultivos; se lee desde ahí, sin copiarlo): PRICE RECEIVED, MARKETING YEAR, nivel estado.
- data/raw/economia/ers/{corn,soybeans,wheat,oats}.csv (USDA ERS Commodity Costs and Returns),
  por Farm Resource Region, dólares por acre sembrado.
- data/raw/economia/ers/reglink.xls (ERS): Farm Resource Region de cada condado (FIPS).
- Del mismo volcado de Quick Stats: ACRES PLANTED por condado, para ponderar las regiones.

Costos por estado: ERS no publica costos por estado. Cada estado recibe el promedio de los
valores regionales de ERS ponderado por la participación de cada región en el área sembrada
del cultivo en el estado (suma de ACRES PLANTED de sus condados en el período). En IA, IL e IN
todos los condados son Heartland y el resultado es exactamente el valor de Heartland.

Salidas (data/processed/economia/):
- economia_anual.csv: fips_estado, anio, cultivo, precio_usd_bu, valor_produccion_usd_ac,
  costo_operativo_usd_ac, costo_total_usd_ac, margen_operativo_usd_ac, flag_nass
- economia_forrajes_anual.csv: fips_estado, anio, cultivo, precio_usd_ton, flag_nass
- docs/datasets/economia.md (tabla de columnas y de pesos por región, generadas)
- data/interim/economia/pesos_region_ers.csv: fips_estado, cultivo, region_ers, acres, base, peso

El escaneo del volcado (1,1 GB comprimido) se cachea en data/interim/economia/ (regenerable:
se rehace si cambia el nombre o el tamaño del volcado).

Uso: python src/economia/process.py
"""
from __future__ import annotations

import gzip
import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import cargar_config  # noqa: E402

NASS_DIR = REPO / "data" / "raw" / "cultivos" / "nass"
ERS_DIR = REPO / "data" / "raw" / "economia" / "ers"
INTERIM = REPO / "data" / "interim" / "economia"
OUT = REPO / "data" / "processed" / "economia"
CARD = REPO / "docs" / "datasets" / "economia.md"

GRANOS = {
    "maiz": "CORN, GRAIN - PRICE RECEIVED, MEASURED IN $ / BU",
    "soja": "SOYBEANS - PRICE RECEIVED, MEASURED IN $ / BU",
    "trigo_invierno": "WHEAT, WINTER - PRICE RECEIVED, MEASURED IN $ / BU",
    "avena": "OATS - PRICE RECEIVED, MEASURED IN $ / BU",
}
FORRAJES = {
    "alfalfa": "HAY, ALFALFA - PRICE RECEIVED, MEASURED IN $ / TON",
    "heno": "HAY, (EXCL ALFALFA) - PRICE RECEIVED, MEASURED IN $ / TON",
}
ERS = {"maiz": "corn.csv", "soja": "soybeans.csv", "trigo_invierno": "wheat.csv", "avena": "oats.csv"}
REGLINK = ERS_DIR / "reglink.xls"
# códigos de reglink.xls ("Key to ERS regions" de la misma planilla)
REGIONES = {1: "Heartland", 2: "Northern Crescent", 3: "Northern Great Plains",
            4: "Prairie Gateway", 5: "Eastern Uplands", 6: "Southern Seaboard",
            7: "Fruitful Rim", 8: "Basin and Range", 9: "Mississippi Portal"}
# Códigos de condado viejos de reglink.xls -> código actual del Census. Fuente: Census Bureau,
# "Substantial Changes to Counties and County Equivalent Entities: 2010-present"
# (https://www.census.gov/programs-surveys/geography/technical-documentation/county-changes/2010.html,
# consultado 2026-11-15): Shannon County, SD (46113) pasó a Oglala Lakota County (46102) el
# 2015-05-01. Es el único cambio de código desde 2000 en los 10 estados de config.yaml (la página
# de 2000-2009 solo tiene en ellos la corrección de nombre de LaSalle, IL, sin cambio de código).
CODIGOS_NUEVOS = {"46113": "46102"}
# área sembrada por condado (NASS SURVEY) con la que se pondera cada región
AREA = {
    "maiz": "CORN - ACRES PLANTED",
    "soja": "SOYBEANS - ACRES PLANTED",
    "trigo_invierno": "WHEAT, WINTER - ACRES PLANTED",
    "avena": "OATS - ACRES PLANTED",
}
# mínimo del peso del estado que debe tener dato ERS en el año; si no, queda vacío
COBERTURA_MIN = 0.5
ITEMS = {
    "Total, gross value of production": "valor_produccion_usd_ac",
    "Total, operating costs": "costo_operativo_usd_ac",
    "Total, costs listed": "costo_total_usd_ac",
    "Value of production less operating costs": "margen_operativo_usd_ac",
}
FLAGS = {"(D)", "(S)", "(NA)", "(Z)", "(X)", "(L)", "(H)"}


def volcado() -> Path:
    archivos = sorted(NASS_DIR.glob("qs.crops_*.txt.gz"))
    if not archivos:
        raise SystemExit(f"falta el volcado qs.crops_*.txt.gz en {NASS_DIR}")
    return archivos[-1]


def escanear_precios(estados: list[str]) -> pd.DataFrame:
    """Filas PRICE RECEIVED anuales (año comercial) por estado de los short_desc buscados."""
    src = volcado()
    cache = INTERIM / f"precios_{src.name.split('.txt')[0]}_{src.stat().st_size}.csv"
    if cache.exists():
        # la caché puede venir de una corrida con otros estados (FIELDSHIFT_ESTADOS)
        df = pd.read_csv(cache, dtype=str, keep_default_na=False)
        if set(estados) <= set(df["STATE_ALPHA"]):
            return df[df["STATE_ALPHA"].isin(estados)].reset_index(drop=True)
    buscados = set(GRANOS.values()) | set(FORRAJES.values())
    filas = []
    with gzip.open(src, "rt", encoding="utf-8", errors="replace") as f:
        h = f.readline().rstrip("\n").split("\t")
        ix = {c: i for i, c in enumerate(h)}
        for line in f:
            if "PRICE RECEIVED" not in line:
                continue
            r = line.rstrip("\n").split("\t")
            if (r[ix["SHORT_DESC"]] in buscados and r[ix["SOURCE_DESC"]] == "SURVEY"
                    and r[ix["AGG_LEVEL_DESC"]] == "STATE" and r[ix["STATE_ALPHA"]] in estados
                    and r[ix["FREQ_DESC"]] == "ANNUAL"
                    and r[ix["REFERENCE_PERIOD_DESC"]] == "MARKETING YEAR"
                    and r[ix["DOMAIN_DESC"]] == "TOTAL"):
                filas.append({k: r[ix[k]] for k in ("STATE_ALPHA", "STATE_FIPS_CODE", "YEAR",
                                                     "SHORT_DESC", "VALUE")})
    df = pd.DataFrame(filas).sort_values(["STATE_ALPHA", "SHORT_DESC", "YEAR"]).reset_index(drop=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    tmp = cache.with_suffix(".part")
    df.to_csv(tmp, index=False)
    tmp.replace(cache)
    return df


def precios(estados: dict, anios: range, mapa: dict, col: str) -> pd.DataFrame:
    crudo = escanear_precios(list(estados))
    inv = {v: k for k, v in mapa.items()}
    crudo = crudo[crudo["SHORT_DESC"].isin(inv)].copy()
    crudo["cultivo"] = crudo["SHORT_DESC"].map(inv)
    crudo["anio"] = crudo["YEAR"].astype(int)
    crudo["fips_estado"] = crudo["STATE_ALPHA"].map({k: v["fips"] for k, v in estados.items()})
    dup = crudo.duplicated(["fips_estado", "anio", "cultivo"], keep=False)
    if dup.any():
        raise SystemExit(f"filas de precio duplicadas en el volcado: {crudo[dup].head()}")
    v = crudo["VALUE"].str.strip().str.replace(",", "", regex=False)
    crudo["flag_nass"] = v.where(v.isin(FLAGS), "")
    crudo[col] = pd.to_numeric(v.where(~v.isin(FLAGS)), errors="coerce")
    grilla = pd.MultiIndex.from_product(
        [sorted(v["fips"] for v in estados.values()), list(anios), list(mapa)],
        names=["fips_estado", "anio", "cultivo"]).to_frame(index=False)
    out = grilla.merge(crudo[["fips_estado", "anio", "cultivo", col, "flag_nass"]],
                       on=["fips_estado", "anio", "cultivo"], how="left")
    out["flag_nass"] = out["flag_nass"].fillna("")
    return out


def escanear_area(estados: list[str]) -> pd.DataFrame:
    """Filas ACRES PLANTED anuales por condado (encuesta) de los cultivos de AREA."""
    src = volcado()
    cache = INTERIM / f"area_condado_{src.name.split('.txt')[0]}_{src.stat().st_size}.csv"
    if cache.exists():
        df = pd.read_csv(cache, dtype=str, keep_default_na=False)
        if set(estados) <= set(df["STATE_ALPHA"]):
            return df[df["STATE_ALPHA"].isin(estados)].reset_index(drop=True)
    buscados = set(AREA.values())
    filas = []
    with gzip.open(src, "rt", encoding="utf-8", errors="replace") as f:
        h = f.readline().rstrip("\n").split("\t")
        ix = {c: i for i, c in enumerate(h)}
        for line in f:
            if "ACRES PLANTED" not in line:
                continue
            r = line.rstrip("\n").split("\t")
            if (r[ix["SHORT_DESC"]] in buscados and r[ix["SOURCE_DESC"]] == "SURVEY"
                    and r[ix["AGG_LEVEL_DESC"]] == "COUNTY" and r[ix["STATE_ALPHA"]] in estados
                    and r[ix["FREQ_DESC"]] == "ANNUAL" and r[ix["REFERENCE_PERIOD_DESC"]] == "YEAR"
                    and r[ix["DOMAIN_DESC"]] == "TOTAL"):
                filas.append({k: r[ix[k]] for k in ("STATE_ALPHA", "STATE_FIPS_CODE", "COUNTY_ANSI",
                                                     "YEAR", "SHORT_DESC", "VALUE")})
    df = pd.DataFrame(filas, columns=["STATE_ALPHA", "STATE_FIPS_CODE", "COUNTY_ANSI", "YEAR",
                                      "SHORT_DESC", "VALUE"])
    df = df.sort_values(["STATE_ALPHA", "SHORT_DESC", "COUNTY_ANSI", "YEAR"]).reset_index(drop=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    tmp = cache.with_suffix(".part")
    df.to_csv(tmp, index=False)
    tmp.replace(cache)
    return df


def regiones_condado() -> pd.DataFrame:
    """fips_condado (5 dígitos) -> region_ers, de reglink.xls de ERS."""
    if not REGLINK.exists():
        raise SystemExit(f"falta {REGLINK}: correr src/economia/download.py")
    r = pd.read_excel(REGLINK, header=None, usecols=[0, 1], names=["fips", "codigo"])
    return limpiar_reglink(r)


def limpiar_reglink(r: pd.DataFrame) -> pd.DataFrame:
    """Columnas fips y codigo de reglink.xls -> fips_condado (5 dígitos), region_ers.

    Descarta los encabezados y la clave de regiones (filas no numéricas) y pasa los códigos de
    condado viejos de reglink.xls a los actuales del Census (CODIGOS_NUEVOS).
    """
    r = r[pd.to_numeric(r["fips"], errors="coerce").notna()
          & pd.to_numeric(r["codigo"], errors="coerce").notna()]
    r = r.astype(int)
    r["fips_condado"] = r["fips"].astype(str).str.zfill(5)
    # si la planilla ya trae el código nuevo, la fila con el viejo sobra
    viejos = r["fips_condado"].isin(CODIGOS_NUEVOS) & r["fips_condado"].map(CODIGOS_NUEVOS).isin(
        r["fips_condado"])
    r = r[~viejos].copy()
    r["fips_condado"] = r["fips_condado"].replace(CODIGOS_NUEVOS)
    r["region_ers"] = r["codigo"].map(REGIONES)
    if r["region_ers"].isna().any() or r["fips_condado"].duplicated().any():
        raise SystemExit(f"{REGLINK.name}: códigos de región desconocidos o condados duplicados")
    return r[["fips_condado", "region_ers"]]


def pesos_region(estados: dict, anios: range) -> pd.DataFrame:
    """Peso de cada región ERS por estado y cultivo: participación en el ACRES PLANTED del período."""
    a = escanear_area(list(estados))
    a = a[a["YEAR"].astype(int).isin(list(anios)) & (a["COUNTY_ANSI"] != "")].copy()
    a["acres"] = pd.to_numeric(a["VALUE"].str.strip().str.replace(",", "", regex=False),
                               errors="coerce")
    a["cultivo"] = a["SHORT_DESC"].map({v: k for k, v in AREA.items()})
    a["fips_estado"] = a["STATE_FIPS_CODE"].str.zfill(2)
    a["fips_condado"] = a["fips_estado"] + a["COUNTY_ANSI"].str.zfill(3)
    regiones = regiones_condado()
    a = a.merge(regiones, on="fips_condado", how="left")
    sin = a[a["region_ers"].isna()]["fips_condado"].unique()
    if len(sin):
        raise SystemExit(f"condados de NASS sin región en {REGLINK.name}: {sorted(sin)}")
    p = a.groupby(["fips_estado", "cultivo", "region_ers"], as_index=False)["acres"].sum()
    p = p[p["acres"] > 0]
    p["base"] = "acres_sembrados"
    # sin área por condado (p. ej. avena en IN): peso = proporción de condados de cada región
    falta = [(f, c) for f in sorted(str(e["fips"]).zfill(2) for e in estados.values())
             for c in AREA if not ((p["fips_estado"] == f) & (p["cultivo"] == c)).any()]
    for f, c in falta:
        n = regiones[regiones["fips_condado"].str[:2] == f].groupby("region_ers").size()
        p = pd.concat([p, pd.DataFrame({"fips_estado": f, "cultivo": c, "region_ers": n.index,
                                        "acres": n.values, "base": "condados"})], ignore_index=True)
    p["peso"] = p["acres"] / p.groupby(["fips_estado", "cultivo"])["acres"].transform("sum")
    p = p.sort_values(["fips_estado", "cultivo", "peso"], ascending=[True, True, False])
    INTERIM.mkdir(parents=True, exist_ok=True)
    p.round({"peso": 4}).to_csv(INTERIM / "pesos_region_ers.csv", index=False, lineterminator="\n")
    return p.reset_index(drop=True)


def costos_region(anios: range) -> pd.DataFrame:
    """anio, cultivo, region_ers y los ítems de ITEMS, en dólares por acre sembrado."""
    partes = []
    for cultivo, archivo in ERS.items():
        d = pd.read_csv(ERS_DIR / archivo)
        d = d[d["Region"].isin(REGIONES.values()) & d["Item"].isin(ITEMS)
              & (d["Units"] == "dollars per planted acre")].copy()
        d["anio"] = pd.to_numeric(d["Year"], errors="coerce")
        d = d[d["anio"].isin(list(anios))]
        dup = d.duplicated(["Region", "anio", "Item"], keep=False)
        if dup.any():
            raise SystemExit(f"{archivo}: ítems duplicados por región y año")
        w = d.pivot(index=["Region", "anio"], columns="Item", values="Value").rename(columns=ITEMS)
        w = w.apply(pd.to_numeric, errors="coerce").reset_index().rename(columns={"Region": "region_ers"})
        w["cultivo"] = cultivo
        partes.append(w)
    return pd.concat(partes, ignore_index=True)


def costos_ers(estados: dict, anios: range) -> pd.DataFrame:
    """Costos ERS por estado: promedio de las regiones ponderado por pesos_region.

    Si una región del estado no tiene dato ese año, se repondera entre las que sí tienen,
    siempre que cubran al menos COBERTURA_MIN del peso; si no, el año queda vacío.
    """
    pesos = pesos_region(estados, anios)
    reg = costos_region(anios)
    cols = list(ITEMS.values())
    m = pesos.merge(reg, on=["cultivo", "region_ers"], how="inner")
    m = m.dropna(subset=cols, how="any")
    for c in cols:
        m[c] = m[c] * m["peso"]
    g = m.groupby(["fips_estado", "anio", "cultivo"], as_index=False)[cols + ["peso"]].sum()
    for c in cols:
        g[c] = g[c] / g["peso"]
    g.loc[g["peso"] < COBERTURA_MIN, cols] = float("nan")
    g["anio"] = g["anio"].astype(int)
    return g.drop(columns="peso")


def fmt(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    df["anio"] = df["anio"].astype(int)
    for c in cols:
        df[c] = df[c].round(2)
    return df


TEXTO = """# Data card — economia

Precios recibidos por el productor (USDA NASS) y costos y retornos por acre sembrado (USDA ERS)
por estado, año de cosecha y cultivo, para comparar rotaciones en el Corn Belt (los estados de
`config/config.yaml`). Paquete sumado por el humano (recursos del desafío); research de base en
`docs/research/precios_margenes.md` y, para las regiones de ERS, `docs/research/regiones_ers.md`.

## Archivos

- `data/processed/economia/economia_anual.csv`: `fips_estado, anio, cultivo, precio_usd_bu,
  valor_produccion_usd_ac, costo_operativo_usd_ac, costo_total_usd_ac, margen_operativo_usd_ac,
  flag_nass`. Cultivos: maiz, soja, trigo_invierno, avena. 2000–2025.
- `data/processed/economia/economia_forrajes_anual.csv`: `fips_estado, anio, cultivo,
  precio_usd_ton, flag_nass`. Cultivos: alfalfa, heno. 2000–2025.

Los datos solo existen por estado (NASS) o por región (ERS): la clave es `fips_estado`
(2 dígitos), como en Crop Progress.

## Fuentes

- **NASS Quick Stats**, volcado público `data/raw/cultivos/nass/qs.crops_20261113.txt.gz` (bajado
  por el paquete `cultivos`, registrado en `manifest.csv` con paquete `cultivos`; se lee desde
  ahí, sin copiarlo). Filtros: `SOURCE_DESC=SURVEY`, `STATISTICCAT_DESC=PRICE RECEIVED`,
  `AGG_LEVEL_DESC=STATE`, `FREQ_DESC=ANNUAL`, `REFERENCE_PERIOD_DESC=MARKETING YEAR`,
  `DOMAIN_DESC=TOTAL`. `short_desc`: maiz `CORN, GRAIN - PRICE RECEIVED, MEASURED IN $ / BU`;
  soja `SOYBEANS - PRICE RECEIVED, MEASURED IN $ / BU`; trigo_invierno `WHEAT, WINTER - PRICE
  RECEIVED, MEASURED IN $ / BU`; avena `OATS - PRICE RECEIVED, MEASURED IN $ / BU`; alfalfa
  `HAY, ALFALFA - PRICE RECEIVED, MEASURED IN $ / TON`; heno `HAY, (EXCL ALFALFA) - PRICE
  RECEIVED, MEASURED IN $ / TON`.
- **USDA ERS Commodity Costs and Returns**
  (https://www.ers.usda.gov/data-products/commodity-costs-and-returns), CSV por cultivo en
  `data/raw/economia/ers/` (corn, soybeans, wheat, oats). Farm Resource Regions `Heartland`,
  `Northern Crescent`, `Northern Great Plains`, `Prairie Gateway` y `Eastern Uplands` (las que
  tocan los estados de la zona), unidad `dollars per planted acre`. Ítems: `Total, gross value of production` →
  `valor_produccion_usd_ac`; `Total, operating costs` → `costo_operativo_usd_ac`;
  `Total, costs listed` → `costo_total_usd_ac`; `Value of production less operating costs` →
  `margen_operativo_usd_ac` (tal como lo publica ERS para cada región; el promedio ponderado de
  los márgenes regionales es igual a la diferencia de los promedios ponderados).
- **USDA ERS Farm Resource Regions**, `data/raw/economia/ers/reglink.xls`
  (https://www.ers.usda.gov/sites/default/files/images/reglink.xls, enlazada desde
  https://www.ers.usda.gov/data-products/commodity-costs-and-returns/documentation): región de
  cada condado por FIPS (códigos 1 a 9, con la clave en la misma planilla).
- **NASS Quick Stats**, mismo volcado, área sembrada por condado para los pesos: `SOURCE_DESC=SURVEY`,
  `AGG_LEVEL_DESC=COUNTY`, `FREQ_DESC=ANNUAL`, `REFERENCE_PERIOD_DESC=YEAR`, `DOMAIN_DESC=TOTAL`;
  `short_desc` `CORN - ACRES PLANTED`, `SOYBEANS - ACRES PLANTED`, `WHEAT, WINTER - ACRES
  PLANTED`, `OATS - ACRES PLANTED`.

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
{tabla}

`desde`, `hasta` y `faltantes_pct` se calculan de los CSV al final de `process.py`.

## Pesos de las regiones ERS por estado

Participación de cada región en el área sembrada del cultivo en el estado (suma de ACRES PLANTED
por condado en el período). Se guardan también en `data/interim/economia/pesos_region_ers.csv`.

| fips_estado | cultivo | region_ers | acres | base | peso |
|---|---|---|---|---|---|
{pesos}

## Supuestos

- **Precio del año comercial.** Se usa la fila `MARKETING YEAR` del `anio` de cosecha (para maíz
  y soja, el año comercial empieza el 1 de septiembre del año de cosecha). Los precios mensuales
  no se entregan; cuál precio usar en el modelo lo decide el equipo de ML.
- **Unidad original.** Granos en USD por bushel y forrajes en USD por tonelada corta (2000 lb),
  como los publica NASS. No se convierte a USD/t métrica.
- **Costos ponderados por región.** ERS no publica costos por estado ni por condado, sino por
  Farm Resource Region, que se definen por condado (`reglink.xls`). Cada estado recibe el
  promedio de los valores regionales ponderado por la participación de cada región en el área
  sembrada del cultivo en el estado, sumando `ACRES PLANTED` de NASS por condado en todo el
  período (pesos fijos, no cambian por año, para que un condado suprimido un año no mueva el
  costo). IA, IL e IN son 100 % Heartland y KS 100 % Prairie Gateway; OH, NE y MN se reparten
  entre varias regiones (tabla de pesos arriba).
- **Regiones sin dato.** Si una región del estado no tiene serie ERS ese año (Eastern Uplands no
  tiene trigo y su avena empieza en 2023; la avena de Prairie Gateway termina en 2022), se
  repondera entre las regiones con dato, siempre que cubran al menos el 50 % del peso del
  estado; si no, los costos del año quedan vacíos.
- **Sin área por condado.** Si NASS no publica `ACRES PLANTED` por condado de un cultivo en un
  estado (avena en IN), el peso de cada región es su proporción de condados (`base = condados`
  en la tabla de pesos; la columna `acres` trae entonces la cantidad de condados).
- **Códigos de condado viejos en `reglink.xls`.** La planilla de ERS trae a Oglala Lakota (SD)
  con el código de Shannon County (46113); el Census lo cambió a 46102 en 2015 (Census Bureau,
  "Substantial Changes to Counties and County Equivalent Entities: 2010-present"). Al leerla se
  pasa 46113 → 46102. Es el único cambio de código desde 2000 en los estados de la zona.
- **Condados combinados.** Las filas de NASS de `OTHER (COMBINED) COUNTIES` no tienen condado
  y no entran en los pesos. Los códigos `(D)` y similares cuentan como sin dato.
- **Trigo.** ERS publica costos de trigo en general (no separa el de invierno). Se asignan a
  `trigo_invierno`, que es el trigo que se siembra en el Corn Belt. El precio sí es el de
  `WHEAT, WINTER`.
- **Avena.** La serie de ERS de avena empieza en 2005 en todas las regiones: 2000–2004 quedan vacíos.
- **Costos de forrajes.** ERS no tiene costos y retornos de alfalfa ni de heno: el archivo de
  forrajes solo trae el precio.
- **Ventana.** 2000–2025, de `config/config.yaml`. Los pronósticos ERS 2026F–2027F (solo total
  EE.UU.) no se usan.
- **Códigos NASS.** `(D)`, `(S)`, `(NA)` y los demás códigos entre paréntesis van como celda
  vacía, con el código en `flag_nass`. Un año sin fila en el volcado queda con precio y
  `flag_nass` vacíos.
- **Manifest.** El volcado de Quick Stats está registrado en `manifest.csv` por el paquete
  `cultivos`. No se le agrega una fila con paquete `economia` porque el control del manifest
  exige que las filas de cada paquete apunten a `data/raw/<paquete>/`.

## Problemas conocidos

- NASS dejó de publicar el precio del trigo de invierno en Iowa después de 2019 y el de la avena
  en Indiana después de 2015: esas celdas quedan vacías (con `(NA)` en `flag_nass` cuando NASS
  publica el código).
- Los costos de ERS son estimaciones regionales de la encuesta ARMS (años base de encuesta
  distintos por cultivo); la ponderación por área solo refleja en qué regiones se siembra cada
  cultivo, no diferencias dentro de una región ni entre rotaciones. En NE no separa riego y
  secano (ver T004). Los
  presupuestos de farmdoc por rotación (ver research) no se incorporaron.
- USDA AMS Market News (opcional) no se incorporó.
"""

DESC = {
    "economia_anual.csv": [
        ("precio_usd_bu", "Precio recibido por el productor, promedio del año comercial (NASS PRICE RECEIVED, MARKETING YEAR, estado)", "USD/bu", "USDA NASS Quick Stats (volcado qs.crops)", "MK01"),
        ("valor_produccion_usd_ac", "Valor bruto de la producción por acre sembrado (ERS 'Total, gross value of production', regiones ponderadas por área sembrada)", "USD/ac", "USDA ERS Commodity Costs and Returns", ""),
        ("costo_operativo_usd_ac", "Costos operativos por acre sembrado (ERS 'Total, operating costs', regiones ponderadas por área sembrada)", "USD/ac", "USDA ERS Commodity Costs and Returns", "MK03"),
        ("costo_total_usd_ac", "Costos totales listados por acre sembrado (ERS 'Total, costs listed', regiones ponderadas por área sembrada)", "USD/ac", "USDA ERS Commodity Costs and Returns", "MK03"),
        ("margen_operativo_usd_ac", "Valor de la producción menos costos operativos (ERS 'Value of production less operating costs', regiones ponderadas por área sembrada)", "USD/ac", "USDA ERS Commodity Costs and Returns", "MK02"),
        ("flag_nass", "Código original de NASS cuando el precio no se publica ((D), (S), (NA)); vacío si hay valor", "texto", "USDA NASS Quick Stats (volcado qs.crops)", ""),
    ],
    "economia_forrajes_anual.csv": [
        ("precio_usd_ton", "Precio recibido por el productor, promedio del año comercial (NASS PRICE RECEIVED, MARKETING YEAR, estado)", "USD/ton corta", "USDA NASS Quick Stats (volcado qs.crops)", "MK01"),
        ("flag_nass", "Código original de NASS cuando el precio no se publica ((D), (S), (NA)); vacío si hay valor", "texto", "USDA NASS Quick Stats (volcado qs.crops)", ""),
    ],
}


def data_card() -> None:
    filas = []
    for archivo, cols in DESC.items():
        df = pd.read_csv(OUT / archivo, dtype={"fips_estado": str, "flag_nass": str})
        t = df["anio"].astype(str)
        for nombre, desc, unidad, fuente, cid in cols:
            s = df[nombre]
            falt = 100 * s.isna().mean()
            llenos = t[s.notna()]
            desde = llenos.min() if len(llenos) else ""
            hasta = llenos.max() if len(llenos) else ""
            filas.append(f"| {archivo} | {nombre} | {desc} | {unidad} | {fuente} | {cid} | {desde} | {hasta} | {falt:.1f} |")
    p = pd.read_csv(INTERIM / "pesos_region_ers.csv", dtype={"fips_estado": str})
    tabla_pesos = [f"| {r.fips_estado} | {r.cultivo} | {r.region_ers} | {r.acres:,.0f} | {r.base} | {r.peso:.3f} |"
                   for r in p.itertuples()]
    CARD.parent.mkdir(parents=True, exist_ok=True)
    texto = TEXTO.replace("{tabla}", "\n".join(filas)).replace("{pesos}", "\n".join(tabla_pesos))
    CARD.write_text(texto, encoding="utf-8", newline="\n")


def main() -> None:
    t0 = time.time()
    cfg = cargar_config()
    estados = cfg["zona"]["estados"]
    anios = range(int(cfg["periodo"]["anio_inicio"]), int(cfg["periodo"]["anio_fin"]) + 1)
    OUT.mkdir(parents=True, exist_ok=True)

    granos = precios(estados, anios, GRANOS, "precio_usd_bu")
    print(f"precios granos: {granos['precio_usd_bu'].notna().sum()} valores ({time.time() - t0:.0f} s)")
    costos = costos_ers(estados, anios)
    anual = granos.merge(costos, on=["fips_estado", "anio", "cultivo"], how="left")
    cols = ["precio_usd_bu", "valor_produccion_usd_ac", "costo_operativo_usd_ac",
            "costo_total_usd_ac", "margen_operativo_usd_ac"]
    anual = fmt(anual, cols)[["fips_estado", "anio", "cultivo"] + cols + ["flag_nass"]]
    anual = anual.sort_values(["fips_estado", "anio", "cultivo"]).reset_index(drop=True)
    anual.to_csv(OUT / "economia_anual.csv", index=False, float_format="%.2f", lineterminator="\n")

    forr = precios(estados, anios, FORRAJES, "precio_usd_ton")
    forr = fmt(forr, ["precio_usd_ton"])[["fips_estado", "anio", "cultivo", "precio_usd_ton", "flag_nass"]]
    forr = forr.sort_values(["fips_estado", "anio", "cultivo"]).reset_index(drop=True)
    forr.to_csv(OUT / "economia_forrajes_anual.csv", index=False, float_format="%.2f", lineterminator="\n")

    data_card()
    print(f"economia_anual.csv: {len(anual)} filas; economia_forrajes_anual.csv: {len(forr)} filas "
          f"({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
