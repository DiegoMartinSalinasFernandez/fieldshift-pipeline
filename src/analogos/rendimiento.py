"""Análogos Argentina ↔ Corn Belt: rendimientos por departamento del MAGyP y comparación con los condados
análogos.

Fuente: Estimaciones agrícolas del MAGyP (datos.magyp.gob.ar), CSV consolidado de 2026-03, tal cual se bajó en
data/raw/analogos/magyp/. Campos: cultivo, anio, campania, provincia, provincia_id, departamento,
departamento_id, superficie_sembrada_ha, superficie_cosechada_ha, produccion_tm, rendimiento_kgxha.

Proceso:
- Cultivos: "maíz" → maiz, "soja total" → soja (1.ª + 2.ª), "trigo total" → trigo. Campañas 2000/01 en adelante.
- anio = año de cosecha = segundo año de la campaña (2023/2024 → 2024). Es el mismo corrimiento de 6 meses que el
  clima: la temporada octubre-marzo de Argentina termina en el anio. Para el trigo (siembra mayo-julio, cosecha
  noviembre-enero) la cosecha cae a fin del primer año o en enero del segundo; se usa igual el segundo, para que
  el anio sea el mismo en los tres cultivos y coincida con el invierno previo (mayo-septiembre del anio − 1).
- Las filas "sin definir" (departamento_id terminado en 000) no son un departamento: afuera.
- Chascomús viene con el código 06217, anterior a la creación de Lezama (2009). Georef usa 06218. Se recodifica
  a 06218 y se deja `flag_magyp` = `codigo_06217`: el área incluye Lezama.
- Rendimiento 0 (no hubo cosecha, casi siempre superficie cosechada 0): vacío, con `flag_magyp` =
  `0_sin_cosecha`. Es la misma regla que NASS en el paquete cultivos (T148).
- rend_kgha = rendimiento_kgxha del MAGyP (producción / superficie cosechada, comprobado: diferencia ≤ 50 kg/ha).

Comparación con EE.UU.: por departamento y cultivo, la mediana 2001-2024 del rendimiento argentino contra la
distribución de los rendimientos (rend_kgha de NASS, 2001-2024) de sus 3 condados análogos de clima
(analogos_departamento.csv). trigo se compara con trigo_invierno de NASS. Es una comparación de niveles, no
una validación de un modelo: los rendimientos dependen también del manejo, la genética y los precios.

Salidas en data/processed/analogos/:
- rendimiento_ar.csv: id_depto_indec, anio, cultivo, sup_sembrada_ha, sup_cosechada_ha, produccion_t, rend_kgha,
  ratio_cosechada, campania, flag_magyp;
- rendimiento_comparacion.csv: id_depto_indec, cultivo, n_anios_ar, rend_ar_mediana_kgha, n_obs_us,
  rend_us_p10_kgha, rend_us_mediana_kgha, rend_us_p90_kgha, ratio_ar_us, pctl_ar_en_us.
Uso: python src/analogos/rendimiento.py <tabla_anual.csv de unido_10_estados>
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "analogos" / "magyp" / "estimaciones-agricolas-2026-03.csv"
OUT = RAIZ / "data" / "processed" / "analogos"
CULTIVOS = {"maíz": "maiz", "soja total": "soja", "trigo total": "trigo"}
CULTIVO_US = {"maiz": "maiz", "soja": "soja", "trigo": "trigo_invierno"}
RECODIFICAR = {"06217": "06218"}
COMP_DESDE, COMP_HASTA = 2001, 2024


def limpiar(d: pd.DataFrame) -> pd.DataFrame:
    d = d[d["cultivo"].isin(CULTIVOS) & (d["anio"] >= 2000)].copy()
    d = d[~d["departamento_id"].str.endswith("000")]
    d["flag_magyp"] = ""
    rec = d["departamento_id"].isin(RECODIFICAR)
    d.loc[rec, "flag_magyp"] = "codigo_" + d.loc[rec, "departamento_id"]
    d["id_depto_indec"] = d["departamento_id"].replace(RECODIFICAR)
    d["cultivo"] = d["cultivo"].map(CULTIVOS)
    d["anio"] = d["anio"].astype(int) + 1
    d["rend_kgha"] = d["rendimiento_kgxha"].astype(float)
    cero = d["rend_kgha"] == 0
    d.loc[cero, "rend_kgha"] = np.nan
    d.loc[cero, "flag_magyp"] = (d.loc[cero, "flag_magyp"] + ";0_sin_cosecha").str.lstrip(";")
    d = d.rename(columns={"superficie_sembrada_ha": "sup_sembrada_ha", "superficie_cosechada_ha": "sup_cosechada_ha",
                          "produccion_tm": "produccion_t"})
    with np.errstate(invalid="ignore", divide="ignore"):
        d["ratio_cosechada"] = np.where(d["sup_sembrada_ha"] > 0, d["sup_cosechada_ha"] / d["sup_sembrada_ha"], np.nan)
    cols = ["id_depto_indec", "anio", "cultivo", "sup_sembrada_ha", "sup_cosechada_ha", "produccion_t", "rend_kgha",
            "ratio_cosechada", "campania", "flag_magyp"]
    d = d[cols].sort_values(["id_depto_indec", "anio", "cultivo"]).reset_index(drop=True)
    if d.duplicated(["id_depto_indec", "anio", "cultivo"]).any():
        raise SystemExit("claves repetidas en el MAGyP")
    return d


def comparar(ar: pd.DataFrame, us: pd.DataFrame, analogos: pd.DataFrame) -> pd.DataFrame:
    ar = ar[ar["anio"].between(COMP_DESDE, COMP_HASTA)].dropna(subset=["rend_kgha"])
    us = us[us["anio"].between(COMP_DESDE, COMP_HASTA)].dropna(subset=["rend_kgha"])
    filas = []
    for r in analogos.dropna(subset=["fips_analogo"]).itertuples():
        vec = {r.fips_analogo, r.fips_analogo_2, r.fips_analogo_3}
        for c_ar, c_us in CULTIVO_US.items():
            a = ar[(ar["id_depto_indec"] == r.id_depto) & (ar["cultivo"] == c_ar)]["rend_kgha"]
            if a.empty:
                continue
            u = us[us["fips"].isin(vec) & (us["cultivo"] == c_us)]["rend_kgha"].to_numpy()
            med = float(a.median())
            fila = {"id_depto_indec": r.id_depto, "cultivo": c_ar, "n_anios_ar": int(a.size),
                    "rend_ar_mediana_kgha": round(med), "n_obs_us": int(u.size)}
            if u.size >= 10:
                fila.update(rend_us_p10_kgha=round(float(np.percentile(u, 10))),
                            rend_us_mediana_kgha=round(float(np.median(u))),
                            rend_us_p90_kgha=round(float(np.percentile(u, 90))),
                            ratio_ar_us=round(med / float(np.median(u)), 3),
                            pctl_ar_en_us=round(100 * float(np.mean(u <= med)), 1))
            filas.append(fila)
    return pd.DataFrame(filas)


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit("uso: rendimiento.py <tabla_anual.csv de unido_10_estados>")
    OUT.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(RAW, dtype={"provincia_id": str, "departamento_id": str}, encoding="utf-8")
    ar = limpiar(d)
    ar.to_csv(OUT / "rendimiento_ar.csv", index=False, encoding="utf-8", lineterminator="\n", float_format="%.4g")
    us = pd.read_csv(sys.argv[1], usecols=["fips", "anio", "cultivo", "rend_kgha"], dtype={"fips": str})
    an = pd.read_csv(OUT / "analogos_departamento.csv", dtype={"id_depto": str, "fips_analogo": str,
                                                               "fips_analogo_2": str, "fips_analogo_3": str})
    comp = comparar(ar, us, an)
    comp.to_csv(OUT / "rendimiento_comparacion.csv", index=False, encoding="utf-8", lineterminator="\n")
    print(len(ar), "filas MAGyP;", ar["id_depto_indec"].nunique(), "departamentos;",
          int(ar["flag_magyp"].str.contains("0_sin_cosecha").sum()), "sin cosecha")
    print(comp.groupby("cultivo")[["ratio_ar_us", "pctl_ar_en_us"]].median().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
