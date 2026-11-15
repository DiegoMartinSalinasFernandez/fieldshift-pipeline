"""Rendimiento 0 de NASS sin cosecha para grano (T148), sin red y con un caso armado a mano.

Correr:  python -X utf8 -m unittest tests/test_cultivos_rend_cero.py   (o con pytest)
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.cultivos import process  # noqa: E402

# Tres condados inventados de Dakota del Sur, maíz 2003.
SIN_SUP, SUP_CERO, BAJO = "46063", "46081", "46055"


def fila(condado: str, stat: str, unidad: str, util: str, valor: str) -> dict:
    return {"SOURCE_DESC": "SURVEY", "COMMODITY_DESC": "CORN", "CLASS_DESC": "ALL CLASSES",
            "PRODN_PRACTICE_DESC": "ALL PRODUCTION PRACTICES", "UTIL_PRACTICE_DESC": util,
            "STATISTICCAT_DESC": stat, "UNIT_DESC": unidad, "SHORT_DESC": "", "DOMAIN_DESC": "TOTAL",
            "AGG_LEVEL_DESC": "COUNTY", "STATE_FIPS_CODE": "46", "STATE_ALPHA": "SD",
            "COUNTY_CODE": condado[2:], "YEAR": "2003", "FREQ_DESC": "ANNUAL",
            "REFERENCE_PERIOD_DESC": "YEAR", "WEEK_ENDING": "", "VALUE": valor}


def crops() -> pd.DataFrame:
    filas = []
    for c in (SIN_SUP, SUP_CERO, BAJO):
        filas.append(fila(c, "AREA PLANTED", "ACRES", "ALL UTILIZATION PRACTICES", "1,200"))
    # 1) rendimiento 0 y NASS no publica superficie cosechada para grano (todo fue a silo)
    filas.append(fila(SIN_SUP, "YIELD", "BU / ACRE", "GRAIN", "0"))
    # 2) rendimiento 0 con superficie cosechada 0
    filas.append(fila(SUP_CERO, "YIELD", "BU / ACRE", "GRAIN", "0"))
    filas.append(fila(SUP_CERO, "AREA HARVESTED", "ACRES", "GRAIN", "0"))
    filas.append(fila(SUP_CERO, "PRODUCTION", "BU", "GRAIN", "(D)"))
    # 3) rendimiento bajo pero real, con superficie: queda como está
    filas.append(fila(BAJO, "YIELD", "BU / ACRE", "GRAIN", "4.5"))
    filas.append(fila(BAJO, "AREA HARVESTED", "ACRES", "GRAIN", "800"))
    return pd.DataFrame(filas)


class RendCeroSinCosecha(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        ref = Path(self.tmp.name) / "data" / "reference"
        ref.mkdir(parents=True)
        pd.DataFrame({"fips": [SIN_SUP, SUP_CERO, BAJO]}).to_csv(ref / "condados.csv", index=False)
        self.repo_orig, process.REPO = process.REPO, Path(self.tmp.name)
        self.out = process.produccion(crops()).set_index("fips")

    def tearDown(self):
        process.REPO = self.repo_orig
        self.tmp.cleanup()

    def test_sin_superficie_queda_vacio_con_flag(self):
        r = self.out.loc[SIN_SUP]
        self.assertTrue(pd.isna(r["rend_bu_ac"]))
        self.assertTrue(pd.isna(r["rend_kgha"]))
        self.assertEqual(r["flag_nass"], process.FLAG_SIN_COSECHA)
        self.assertEqual(r["sup_sembrada_ac"], 1200)  # el resto de la fila no cambia

    def test_superficie_cero_queda_vacio_con_flag(self):
        r = self.out.loc[SUP_CERO]
        self.assertTrue(pd.isna(r["rend_bu_ac"]))
        self.assertTrue(pd.isna(r["rend_kgha"]))
        self.assertEqual(r["flag_nass"], "(D);" + process.FLAG_SIN_COSECHA)
        self.assertEqual(r["sup_cosechada_ac"], 0)

    def test_rendimiento_bajo_real_queda(self):
        r = self.out.loc[BAJO]
        self.assertEqual(r["rend_bu_ac"], 4.5)
        self.assertAlmostEqual(r["rend_kgha"], 282.5)
        self.assertTrue(pd.isna(r["flag_nass"]))


if __name__ == "__main__":
    unittest.main()
