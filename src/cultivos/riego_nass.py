"""Riego y secano de NASS por condado (T134; propuesta 1 de coordinacion/para_decidir.md).

Agrega a `produccion_anual.csv` 11 columnas con `PRODN_PRACTICE_DESC` = `IRRIGATED` y `NON-IRRIGATED`
de la encuesta de condado (research: docs/research/riego_nass.md), más `flag_nass_riego`:

    sup_sembrada_riego_ac, sup_sembrada_secano_ac, sup_cosechada_riego_ac, sup_cosechada_secano_ac,
    produccion_riego_bu, produccion_secano_bu, rend_riego_bu_ac, rend_secano_bu_ac,
    rend_riego_kgha, rend_secano_kgha, pct_sembrada_riego

Solo maíz (grano), soja y trigo de invierno. NASS lo publica en NE y KS de 2000 a 2018 (trigo de invierno
hasta 2019); en el resto de los estados, años y cultivos las columnas quedan vacías. Vacío quiere decir
"no publicado o juntado en OTHER (COMBINED) COUNTIES", no "sin riego".

Las filas y columnas que ya produce `process.produccion()` no cambian: esto solo agrega columnas al final.
`flag_nass` tampoco cambia: los códigos ocultos de las columnas por práctica van en `flag_nass_riego`.

Uso (desde process.py):  prod = agregar_riego(produccion(crops), crops)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.common.conversiones import bu_ac_a_kgha  # noqa: E402

# Mismos filtros de clase y uso que process.NASS_CULTIVOS, solo los tres cultivos con dato por práctica.
CULTIVOS_RIEGO = {
    "maiz": ("CORN", "ALL CLASSES", "GRAIN"),
    "soja": ("SOYBEANS", "ALL CLASSES", "ALL UTILIZATION PRACTICES"),
    "trigo_invierno": ("WHEAT", "WINTER", "ALL UTILIZATION PRACTICES"),
}
# Secano = NON-IRRIGATED. Las subdivisiones del trigo ("NON-IRRIGATED, CONTINUOUS CROP",
# "NON-IRRIGATED, FOLLOWING SUMMER FALLOW") no se usan.
PRACTICAS = {"riego": "IRRIGATED", "secano": "NON-IRRIGATED"}
VARIABLES = {  # base -> (STATISTICCAT_DESC, UNIT_DESC, usa el UTIL de cosecha, sufijo de unidad)
    "sup_sembrada": ("AREA PLANTED", "ACRES", False, "ac"),
    "sup_cosechada": ("AREA HARVESTED", "ACRES", True, "ac"),
    "produccion": ("PRODUCTION", "BU", True, "bu"),
    "rend": ("YIELD", "BU / ACRE", True, "bu_ac"),
}
CODIGOS_OCULTOS = {"(D)", "(Z)", "(NA)", "(X)", "(S)", "(L)", "(H)"}

COLUMNAS = [
    "sup_sembrada_riego_ac", "sup_sembrada_secano_ac",
    "sup_cosechada_riego_ac", "sup_cosechada_secano_ac",
    "produccion_riego_bu", "produccion_secano_bu",
    "rend_riego_bu_ac", "rend_secano_bu_ac",
    "rend_riego_kgha", "rend_secano_kgha",
    "pct_sembrada_riego",
]
COLUMNA_FLAG = "flag_nass_riego"
CLAVES = ["fips", "anio", "cultivo"]


def _col(base: str, practica: str, sufijo: str) -> str:
    return f"{base}_{practica}_{sufijo}"


def _valor(s: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Igual que process.valor(): VALUE -> (número o NaN, código oculto o "")."""
    v = s.astype(str).str.strip()
    flag = v.where(v.isin(CODIGOS_OCULTOS), "")
    num = pd.to_numeric(v.str.replace(",", "", regex=False), errors="coerce")
    return num, flag


def produccion_riego(crops: pd.DataFrame, anio_inicio: int, anio_fin: int) -> pd.DataFrame:
    """Columnas por práctica (riego / secano) en formato ancho, clave fips × anio × cultivo.

    `crops` es la tabla de Quick Stats ya filtrada por `process.filtrar()` (todo texto). Solo devuelve las
    combinaciones con al menos un valor o código por práctica. Sin `pct_sembrada_riego` (necesita el total).
    """
    d = crops[(crops["SOURCE_DESC"] == "SURVEY") & (crops["AGG_LEVEL_DESC"] == "COUNTY")
              & (crops["PRODN_PRACTICE_DESC"].isin(PRACTICAS.values()))
              & (crops["DOMAIN_DESC"] == "TOTAL") & (crops["FREQ_DESC"] == "ANNUAL")
              & (crops["REFERENCE_PERIOD_DESC"] == "YEAR")
              & (crops["COUNTY_CODE"] != "998") & (crops["COUNTY_CODE"] != "")]
    d = d.assign(anio=pd.to_numeric(d["YEAR"], errors="coerce"))
    d = d[(d["anio"] >= anio_inicio) & (d["anio"] <= anio_fin)]
    filas = []
    for cultivo, (com, clase, util_cos) in CULTIVOS_RIEGO.items():
        dc = d[(d["COMMODITY_DESC"] == com) & (d["CLASS_DESC"] == clase)]
        for practica, prodn in PRACTICAS.items():
            dp = dc[dc["PRODN_PRACTICE_DESC"] == prodn]
            for base, (stat, unidad, cos, sufijo) in VARIABLES.items():
                util = util_cos if cos else "ALL UTILIZATION PRACTICES"
                dv = dp[(dp["STATISTICCAT_DESC"] == stat) & (dp["UNIT_DESC"] == unidad)
                        & (dp["UTIL_PRACTICE_DESC"] == util)]
                if dv.empty:
                    continue
                num, flag = _valor(dv["VALUE"])
                filas.append(pd.DataFrame({
                    "fips": (dv["STATE_FIPS_CODE"].str.zfill(2) + dv["COUNTY_CODE"].str.zfill(3)).values,
                    "anio": dv["anio"].astype(int).values, "cultivo": cultivo,
                    "variable": _col(base, practica, sufijo), "valor": num.values, "flag": flag.values}))
    cols_base = [c for c in COLUMNAS if c not in ("rend_riego_kgha", "rend_secano_kgha", "pct_sembrada_riego")]
    if not filas:
        return pd.DataFrame(columns=CLAVES + cols_base + [COLUMNA_FLAG])
    largo = pd.concat(filas, ignore_index=True).drop_duplicates(CLAVES + ["variable"])
    ancho = largo.pivot(index=CLAVES, columns="variable", values="valor").reindex(columns=cols_base)
    flags = (largo[largo["flag"] != ""].groupby(CLAVES)["flag"]
             .agg(lambda x: ";".join(sorted(set(x)))))
    ancho = ancho.join(flags.rename(COLUMNA_FLAG)).reset_index()
    ancho.columns.name = None
    return ancho


def agregar_riego(prod: pd.DataFrame, crops: pd.DataFrame,
                  anio_inicio: int | None = None, anio_fin: int | None = None) -> pd.DataFrame:
    """`prod` (salida de process.produccion) con las 11 columnas de riego y `flag_nass_riego` al final.

    No agrega ni saca filas: un dato por práctica sin fila de "ALL PRODUCTION PRACTICES" se descarta
    (con la grilla de NASS eso no pasa: riego + secano = total). Las columnas de `prod` quedan iguales.
    """
    if anio_inicio is None or anio_fin is None:
        from src.common.config import cargar_config
        per = cargar_config()["periodo"]
        anio_inicio = per["anio_inicio"] if anio_inicio is None else anio_inicio
        anio_fin = per["anio_fin"] if anio_fin is None else anio_fin
    riego = produccion_riego(crops, anio_inicio, anio_fin)
    riego = riego.astype({"fips": str, "cultivo": str})
    riego["anio"] = riego["anio"].astype(int)
    base = prod.copy()
    orden = list(base.columns)
    out = base.merge(riego, on=CLAVES, how="left", validate="one_to_one")
    for practica in PRACTICAS:
        out[f"rend_{practica}_kgha"] = np.nan
        for cultivo in CULTIVOS_RIEGO:
            m = out["cultivo"] == cultivo
            out.loc[m, f"rend_{practica}_kgha"] = (
                out.loc[m, f"rend_{practica}_bu_ac"] * bu_ac_a_kgha(cultivo)).round(1)
    total = out["sup_sembrada_ac"].where(out["sup_sembrada_ac"] > 0)
    out["pct_sembrada_riego"] = (100 * out["sup_sembrada_riego_ac"] / total).round(2)
    out[COLUMNA_FLAG] = out[COLUMNA_FLAG].fillna("")
    return out[orden + COLUMNAS + [COLUMNA_FLAG]]


def chequear_coherencia(prod: pd.DataFrame, tolerancia: float = 0.01) -> pd.DataFrame:
    """Filas donde riego + secano se aleja más de `tolerancia` (fracción) de la superficie sembrada total.

    No corrige nada: devuelve las filas para revisarlas. En el research dio 0 sobre 4.316 (NE y KS).
    """
    m = prod[["sup_sembrada_riego_ac", "sup_sembrada_secano_ac", "sup_sembrada_ac"]].notna().all(axis=1)
    p = prod[m]
    suma = p["sup_sembrada_riego_ac"] + p["sup_sembrada_secano_ac"]
    dif = (suma - p["sup_sembrada_ac"]).abs() / p["sup_sembrada_ac"].where(p["sup_sembrada_ac"] > 0)
    return p[dif > tolerancia]


# Para src/cultivos/data_card.py: (columna, descripción, unidad, fuente, ID del catálogo).
_QS = "USDA NASS Quick Stats (SURVEY, condado, por práctica)"
_D = "Derivada de NASS Quick Stats"
COLS_DATA_CARD = [
    ("sup_sembrada_riego_ac", "Superficie sembrada con riego (AREA PLANTED, PRODN_PRACTICE_DESC = IRRIGATED)", "acres", _QS, "Y01"),
    ("sup_sembrada_secano_ac", "Superficie sembrada en secano (AREA PLANTED, NON-IRRIGATED)", "acres", _QS, "Y01"),
    ("sup_cosechada_riego_ac", "Superficie cosechada con riego (AREA HARVESTED; maíz: grano)", "acres", _QS, "Y02"),
    ("sup_cosechada_secano_ac", "Superficie cosechada en secano (AREA HARVESTED; maíz: grano)", "acres", _QS, "Y02"),
    ("produccion_riego_bu", "Producción con riego (PRODUCTION en BU; maíz: grano)", "bu", _QS, "Y03"),
    ("produccion_secano_bu", "Producción en secano (PRODUCTION en BU; maíz: grano)", "bu", _QS, "Y03"),
    ("rend_riego_bu_ac", "Rendimiento con riego (YIELD en BU / ACRE; maíz: grano)", "bu/ac", _QS, "Y04"),
    ("rend_secano_bu_ac", "Rendimiento en secano (YIELD en BU / ACRE; maíz: grano)", "bu/ac", _QS, "Y04"),
    ("rend_riego_kgha", "rend_riego_bu_ac × factor de config.yaml (bu_ac_a_kgha)", "kg/ha", _D, "Y04"),
    ("rend_secano_kgha", "rend_secano_bu_ac × factor de config.yaml (bu_ac_a_kgha)", "kg/ha", _D, "Y04"),
    ("pct_sembrada_riego", "100 × sup_sembrada_riego_ac / sup_sembrada_ac", "%", _D, ""),
    ("flag_nass_riego", "Código original de NASS en las columnas por práctica: (D), (Z)… (separados por ;)", "texto", _QS, ""),
]

SECCION_DATA_CARD = """
## Riego y secano (T134, propuesta 1 de `para_decidir.md`)

Columnas agregadas al final de `produccion_anual.csv` por `src/cultivos/riego_nass.py`
(research: `docs/research/riego_nass.md`). Las columnas anteriores no cambian.

- **Fuente:** la misma encuesta de condado de Quick Stats (`SOURCE_DESC=SURVEY`, `DOMAIN_DESC=TOTAL`,
  `FREQ_DESC=ANNUAL`, `REFERENCE_PERIOD_DESC=YEAR`), con `PRODN_PRACTICE_DESC` = `IRRIGATED` (riego) y
  `NON-IRRIGATED` (secano). Mismos `CLASS_DESC` y `UTIL_PRACTICE_DESC` que las columnas totales (maíz: grano
  para cosechada, producción y rendimiento; sembrada con todos los usos).
- **Cultivos:** maíz, soja y trigo de invierno. Avena, alfalfa y heno quedan vacíos (avena no tiene dato por
  práctica en NE ni KS; alfalfa está en toneladas y solo hasta 2009).
- **Cobertura esperada:** NE y KS, 2000–2018 (trigo de invierno hasta 2019). Desde la cosecha 2019 NASS
  dejó de publicar estimaciones de condado por práctica (Federal Register 2019-24789). En los otros cinco
  estados todo queda vacío. En KS la serie es despareja desde 2008 y la soja no tiene dato en 2010–2013 ni
  2017–2018.

### Supuestos

- **Vacío no es "sin riego":** quiere decir que NASS no lo publicó para ese condado o lo juntó en
  "OTHER (COMBINED) COUNTIES" (`county_code` 998, que se descarta como en el resto del paquete).
- **Secano = `NON-IRRIGATED`.** Las subdivisiones del trigo (`NON-IRRIGATED, CONTINUOUS CROP`,
  `NON-IRRIGATED, FOLLOWING SUMMER FALLOW`, 2000–2008) no se usan.
- `pct_sembrada_riego` usa como denominador `sup_sembrada_ac` (ALL PRODUCTION PRACTICES) y queda vacío si
  falta alguno de los dos o el total es 0.
- `flag_nass` no cambia: los códigos ocultos de las columnas por práctica van en `flag_nass_riego`. En la
  encuesta de NE y KS el research no encontró ningún `(D)`, así que se espera vacía.
- Un dato por práctica sin fila de ALL PRODUCTION PRACTICES para el mismo condado, año y cultivo no se
  agrega (el archivo no suma filas).

### Problemas conocidos

- Comparar `rend_bu_ac` de NE y KS con el de IA, IL o IN mezcla riego y secano; desde 2019 solo queda el
  Censo (superficie cosechada con riego, sin rendimiento; propuesta 2 de `para_decidir.md`).
- La muestra de 2008–2018 está sesgada hacia los condados que siguieron publicando por práctica.
- Control de coherencia: `chequear_coherencia()` lista las filas donde riego + secano se aleja más de 1 %
  de la superficie sembrada total (el research dio 0 casos).
"""
