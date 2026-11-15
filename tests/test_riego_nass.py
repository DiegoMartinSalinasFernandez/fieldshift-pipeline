"""Pruebas sin red de src/cultivos/riego_nass.py (T134) con filas de Quick Stats armadas a mano.

Los valores son de ejemplo (no son datos de NASS): solo prueban filtros, pivoteo, conversión y vacíos.

Correr:  python -X utf8 -m pytest -q tests/test_riego_nass.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.cultivos import riego_nass as rn  # noqa: E402
from src.common.conversiones import bu_ac_a_kgha  # noqa: E402

BASE = {"SOURCE_DESC": "SURVEY", "AGG_LEVEL_DESC": "COUNTY", "DOMAIN_DESC": "TOTAL",
        "FREQ_DESC": "ANNUAL", "REFERENCE_PERIOD_DESC": "YEAR", "WEEK_ENDING": "",
        "STATE_FIPS_CODE": "31", "STATE_ALPHA": "NE", "SHORT_DESC": ""}
STAT = {"sembrada": ("AREA PLANTED", "ACRES"), "cosechada": ("AREA HARVESTED", "ACRES"),
        "produccion": ("PRODUCTION", "BU"), "rend": ("YIELD", "BU / ACRE")}
CULT = {"maiz": ("CORN", "ALL CLASSES", "GRAIN"), "soja": ("SOYBEANS", "ALL CLASSES", "ALL UTILIZATION PRACTICES"),
        "trigo_invierno": ("WHEAT", "WINTER", "ALL UTILIZATION PRACTICES"),
        "avena": ("OATS", "ALL CLASSES", "ALL UTILIZATION PRACTICES")}


def fila(cultivo, practica, var, valor, anio="2010", condado="001", estado="31", **extra):
    com, clase, util_cos = CULT[cultivo]
    stat, unidad = STAT[var]
    util = "ALL UTILIZATION PRACTICES" if var == "sembrada" else util_cos
    f = dict(BASE, COMMODITY_DESC=com, CLASS_DESC=clase, PRODN_PRACTICE_DESC=practica,
             UTIL_PRACTICE_DESC=util, STATISTICCAT_DESC=stat, UNIT_DESC=unidad,
             COUNTY_CODE=condado, STATE_FIPS_CODE=estado, YEAR=anio, VALUE=valor)
    f.update(extra)
    return f


def crops_ejemplo() -> pd.DataFrame:
    I, N, A = "IRRIGATED", "NON-IRRIGATED", "ALL PRODUCTION PRACTICES"
    filas = [
        # Maíz 31001 2010: completo.
        fila("maiz", I, "sembrada", "60,000"), fila("maiz", N, "sembrada", "40,000"),
        fila("maiz", I, "cosechada", "59,000"), fila("maiz", N, "cosechada", "38,000"),
        fila("maiz", I, "produccion", "11,800,000"), fila("maiz", N, "produccion", "5,700,000"),
        fila("maiz", I, "rend", "200"), fila("maiz", N, "rend", "150"),
        fila("maiz", A, "rend", "180.4"),  # total: no entra en las columnas por práctica
        # Maíz para silo con riego: otro UTIL, no tiene que entrar en la cosecha de grano.
        dict(fila("maiz", I, "cosechada", "999"), UTIL_PRACTICE_DESC="SILAGE"),
        # Soja 31001 2010: rendimiento de secano oculto.
        fila("soja", I, "rend", "60"), fila("soja", N, "rend", "(D)"),
        fila("soja", I, "sembrada", "10,000"), fila("soja", N, "sembrada", "20,000"),
        # Trigo: la subdivisión del secano no se usa; NON-IRRIGATED sí.
        fila("trigo_invierno", N, "rend", "45"),
        fila("trigo_invierno", "NON-IRRIGATED, FOLLOWING SUMMER FALLOW", "rend", "50"),
        # Avena: no se usa aunque venga con práctica.
        fila("avena", I, "rend", "90"),
        # Condados combinados (998) y fuera del período: afuera.
        fila("maiz", I, "rend", "210", condado="998"),
        fila("maiz", I, "rend", "190", anio="1999"),
        # Censo: afuera.
        fila("maiz", I, "cosechada", "70,000", SOURCE_DESC="CENSUS"),
    ]
    return pd.DataFrame(filas).astype(str)


def prod_ejemplo() -> pd.DataFrame:
    """Como la salida de process.produccion(): claves y columnas de ALL PRODUCTION PRACTICES."""
    return pd.DataFrame({
        "fips": ["31001", "31001", "31001", "19169"],
        "anio": [2010, 2010, 2010, 2010],
        "cultivo": ["maiz", "soja", "trigo_invierno", "maiz"],
        "sup_sembrada_ac": [100000.0, 30000.0, 5000.0, 150000.0],
        "sup_cosechada_ac": [97000.0, 29500.0, 4800.0, 148000.0],
        "produccion_bu": [17500000.0, np.nan, np.nan, 28000000.0],
        "rend_bu_ac": [180.4, 55.0, 45.0, 189.0],
        "rend_kgha": [11323.7, 3698.8, 3026.2, 11863.5],
        "sup_sembrada_ha": [40470.0, 12141.0, 2023.5, 60705.0],
        "ratio_cosechada": [0.97, 0.9833, 0.96, 0.9867],
        "flag_nass": [np.nan, np.nan, np.nan, "(D)"],
    })


class PruebaRiegoNass(unittest.TestCase):
    def setUp(self):
        self.prod = prod_ejemplo()
        self.out = rn.agregar_riego(self.prod, crops_ejemplo(), 2000, 2025).set_index(["fips", "cultivo"])

    def test_columnas_existentes_no_cambian(self):
        out = rn.agregar_riego(self.prod, crops_ejemplo(), 2000, 2025)
        self.assertEqual(list(out.columns[:len(self.prod.columns)]), list(self.prod.columns))
        self.assertEqual(list(out.columns[len(self.prod.columns):]), rn.COLUMNAS + [rn.COLUMNA_FLAG])
        self.assertEqual(len(rn.COLUMNAS), 11)
        pd.testing.assert_frame_equal(out[self.prod.columns], self.prod)

    def test_maiz_completo(self):
        m = self.out.loc[("31001", "maiz")]
        self.assertEqual(m["sup_sembrada_riego_ac"], 60000)
        self.assertEqual(m["sup_sembrada_secano_ac"], 40000)
        self.assertEqual(m["sup_cosechada_riego_ac"], 59000)  # no el silo
        self.assertEqual(m["produccion_secano_bu"], 5700000)
        self.assertEqual(m["rend_riego_bu_ac"], 200)
        self.assertEqual(m["rend_secano_bu_ac"], 150)
        self.assertAlmostEqual(m["rend_riego_kgha"], round(200 * bu_ac_a_kgha("maiz"), 1))
        self.assertAlmostEqual(m["pct_sembrada_riego"], 60.0)
        self.assertEqual(m["flag_nass_riego"], "")

    def test_oculto_va_vacio_con_flag(self):
        s = self.out.loc[("31001", "soja")]
        self.assertEqual(s["rend_riego_bu_ac"], 60)
        self.assertTrue(np.isnan(s["rend_secano_bu_ac"]))
        self.assertTrue(np.isnan(s["rend_secano_kgha"]))
        self.assertEqual(s["flag_nass_riego"], "(D)")
        self.assertAlmostEqual(s["pct_sembrada_riego"], round(100 * 10000 / 30000, 2))
        self.assertAlmostEqual(s["rend_riego_kgha"], round(60 * bu_ac_a_kgha("soja"), 1))

    def test_trigo_solo_non_irrigated(self):
        t = self.out.loc[("31001", "trigo_invierno")]
        self.assertEqual(t["rend_secano_bu_ac"], 45)
        self.assertTrue(np.isnan(t["rend_riego_bu_ac"]))
        self.assertTrue(np.isnan(t["pct_sembrada_riego"]))

    def test_sin_dato_queda_vacio(self):
        ia = self.out.loc[("19169", "maiz")]
        self.assertTrue(ia[rn.COLUMNAS].isna().all())
        self.assertEqual(ia["flag_nass_riego"], "")

    def test_filtros(self):
        r = rn.produccion_riego(crops_ejemplo(), 2000, 2025)
        self.assertNotIn("avena", set(r["cultivo"]))
        self.assertNotIn("31998", set(r["fips"]))
        self.assertEqual(set(r["anio"]), {2010})
        m = r[(r["fips"] == "31001") & (r["cultivo"] == "maiz")].iloc[0]
        self.assertEqual(m["rend_riego_bu_ac"], 200)  # ni el 998 (210) ni 1999 (190)
        self.assertEqual(m["sup_cosechada_riego_ac"], 59000)  # ni silo ni censo

    def test_no_agrega_filas(self):
        crops = pd.concat([crops_ejemplo(), pd.DataFrame([fila("maiz", "IRRIGATED", "rend", "205",
                                                                condado="003")]).astype(str)])
        out = rn.agregar_riego(self.prod, crops, 2000, 2025)
        self.assertEqual(len(out), len(self.prod))

    def test_sin_filas_por_practica(self):
        crops = crops_ejemplo()
        crops = crops[~crops["PRODN_PRACTICE_DESC"].isin(["IRRIGATED", "NON-IRRIGATED"])]
        out = rn.agregar_riego(self.prod, crops, 2000, 2025)
        self.assertTrue(out[rn.COLUMNAS].isna().all().all())
        self.assertTrue((out["flag_nass_riego"] == "").all())

    def test_coherencia(self):
        out = rn.agregar_riego(self.prod, crops_ejemplo(), 2000, 2025)
        self.assertEqual(len(rn.chequear_coherencia(out)), 0)  # 60.000 + 40.000 = 100.000; 10 + 20 = 30 mil
        out.loc[out["cultivo"] == "maiz", "sup_sembrada_ac"] = 90000.0
        self.assertEqual(len(rn.chequear_coherencia(out)), 1)

    def test_data_card(self):
        nombres = [c[0] for c in rn.COLS_DATA_CARD]
        self.assertEqual(nombres, rn.COLUMNAS + [rn.COLUMNA_FLAG])
        card = (REPO / "docs" / "datasets" / "cultivos.md").read_text(encoding="utf-8")
        self.assertIn("## Riego y secano (T134", card)


if __name__ == "__main__":
    unittest.main()
