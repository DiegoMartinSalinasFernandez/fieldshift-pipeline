"""Paquete economia — precios recibidos (NASS) y costos y retornos (ERS) por estado y año.

Entradas:
- data/raw/cultivos/nass/qs.crops_*.txt.gz (volcado público de Quick Stats que bajó el paquete
  cultivos; se lee desde ahí, sin copiarlo): PRICE RECEIVED, MARKETING YEAR, nivel estado.
- data/raw/economia/ers/{corn,soybeans,wheat,oats}.csv (USDA ERS Commodity Costs and Returns),
  región Heartland, dólares por acre sembrado. El mismo valor para todos los estados.

Salidas (data/processed/economia/):
- economia_anual.csv: fips_estado, anio, cultivo, precio_usd_bu, valor_produccion_usd_ac,
  costo_operativo_usd_ac, costo_total_usd_ac, margen_operativo_usd_ac, flag_nass
- economia_forrajes_anual.csv: fips_estado, anio, cultivo, precio_usd_ton, flag_nass
- docs/datasets/economia.md (tabla de columnas generada desde los CSV)

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
REGION = "Heartland"
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
        return pd.read_csv(cache, dtype=str, keep_default_na=False)
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


def costos_ers(anios: range) -> pd.DataFrame:
    partes = []
    for cultivo, archivo in ERS.items():
        d = pd.read_csv(ERS_DIR / archivo)
        d = d[(d["Region"] == REGION) & d["Item"].isin(ITEMS)
              & (d["Units"] == "dollars per planted acre")].copy()
        d["anio"] = pd.to_numeric(d["Year"], errors="coerce")
        d = d[d["anio"].isin(list(anios))]
        dup = d.duplicated(["anio", "Item"], keep=False)
        if dup.any():
            raise SystemExit(f"{archivo}: ítems duplicados por año en {REGION}")
        w = d.pivot(index="anio", columns="Item", values="Value").rename(columns=ITEMS)
        w = w.apply(pd.to_numeric, errors="coerce").reset_index()
        w["cultivo"] = cultivo
        partes.append(w)
    return pd.concat(partes, ignore_index=True)


def fmt(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    df["anio"] = df["anio"].astype(int)
    for c in cols:
        df[c] = df[c].round(2)
    return df


TEXTO = """# Data card — economia

Precios recibidos por el productor (USDA NASS) y costos y retornos por acre sembrado (USDA ERS)
por estado, año de cosecha y cultivo, para comparar rotaciones en el Corn Belt (IA, IL, IN).
Paquete sumado por el humano (recursos del desafío); research de base en
`docs/research/precios_margenes.md`.

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
  `data/raw/economia/ers/` (corn, soybeans, wheat, oats). Región `Heartland`, unidad
  `dollars per planted acre`. Ítems: `Total, gross value of production` →
  `valor_produccion_usd_ac`; `Total, operating costs` → `costo_operativo_usd_ac`;
  `Total, costs listed` → `costo_total_usd_ac`; `Value of production less operating costs` →
  `margen_operativo_usd_ac` (tal como lo publica ERS, no recalculado).

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
{tabla}

`desde`, `hasta` y `faltantes_pct` se calculan de los CSV al final de `process.py`.

## Supuestos

- **Precio del año comercial.** Se usa la fila `MARKETING YEAR` del `anio` de cosecha (para maíz
  y soja, el año comercial empieza el 1 de septiembre del año de cosecha). Los precios mensuales
  no se entregan; cuál precio usar en el modelo lo decide el equipo de ML.
- **Unidad original.** Granos en USD por bushel y forrajes en USD por tonelada corta (2000 lb),
  como los publica NASS. No se convierte a USD/t métrica.
- **Región Heartland para los tres estados.** ERS no publica costos por estado: IA, IL e IN
  reciben el mismo valor de la región Heartland (Farm Resource Regions del ERS, que se definen por
  condado). Algunos condados de los bordes de los tres estados pueden caer en otras regiones ERS;
  no se verificó condado por condado y se usa Heartland para todo el estado.
- **Trigo.** ERS publica costos de trigo en general (no separa el de invierno). Se asignan a
  `trigo_invierno`, que es el trigo que se siembra en el Corn Belt. El precio sí es el de
  `WHEAT, WINTER`.
- **Avena.** La serie de ERS de avena (región Heartland) empieza en 2005: 2000–2004 quedan vacíos.
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
  distintos por cultivo); no reflejan diferencias entre estados ni entre rotaciones. Los
  presupuestos de farmdoc por rotación (ver research) no se incorporaron.
- USDA AMS Market News (opcional) no se incorporó.
"""

DESC = {
    "economia_anual.csv": [
        ("precio_usd_bu", "Precio recibido por el productor, promedio del año comercial (NASS PRICE RECEIVED, MARKETING YEAR, estado)", "USD/bu", "USDA NASS Quick Stats (volcado qs.crops)", "MK01"),
        ("valor_produccion_usd_ac", "Valor bruto de la producción por acre sembrado (ERS 'Total, gross value of production', Heartland)", "USD/ac", "USDA ERS Commodity Costs and Returns", ""),
        ("costo_operativo_usd_ac", "Costos operativos por acre sembrado (ERS 'Total, operating costs', Heartland)", "USD/ac", "USDA ERS Commodity Costs and Returns", "MK03"),
        ("costo_total_usd_ac", "Costos totales listados por acre sembrado (ERS 'Total, costs listed', Heartland)", "USD/ac", "USDA ERS Commodity Costs and Returns", "MK03"),
        ("margen_operativo_usd_ac", "Valor de la producción menos costos operativos (ERS 'Value of production less operating costs', Heartland)", "USD/ac", "USDA ERS Commodity Costs and Returns", "MK02"),
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
    CARD.parent.mkdir(parents=True, exist_ok=True)
    CARD.write_text(TEXTO.replace("{tabla}", "\n".join(filas)), encoding="utf-8", newline="\n")


def main() -> None:
    t0 = time.time()
    cfg = cargar_config()
    estados = cfg["zona"]["estados"]
    anios = range(int(cfg["periodo"]["anio_inicio"]), int(cfg["periodo"]["anio_fin"]) + 1)
    OUT.mkdir(parents=True, exist_ok=True)

    granos = precios(estados, anios, GRANOS, "precio_usd_bu")
    print(f"precios granos: {granos['precio_usd_bu'].notna().sum()} valores ({time.time() - t0:.0f} s)")
    costos = costos_ers(anios)
    anual = granos.merge(costos, on=["anio", "cultivo"], how="left")
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
