"""Prueba sin red del riego por cultivo de `practicas_censo.csv` (src/cultivos/process.py, T132).

Usa filas de Quick Stats armadas a mano con el formato del archivo completo del Censo (no son datos reales):
dos condados de Nebraska (31001, 31003) y uno de Kansas (20001). Apunta `process.REPO` a una carpeta temporal
con un `data/reference/condados.csv` falso.

Correr:  python -X utf8 -m unittest tests/test_censo_riego.py   (o con pytest)
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.cultivos import process  # noqa: E402

FIPS = ["20001", "31001", "31003"]
COLS_VIEJAS = ["fips", "anio_censo", "pct_cobertura", "pct_labranza_cero", "pct_drenaje_tile", "pct_riego"]
COLS_NUEVAS = ["pct_maiz_regado", "pct_soja_regada", "pct_cosechado_regado", "flag_nass"]


def fila(fips: str, desc: str, valor: str, anio: int = 2022, nivel: str = "COUNTY",
         dominio: str = "TOTAL", condado: str | None = None) -> dict:
    return {"SOURCE_DESC": "CENSUS", "SHORT_DESC": desc, "DOMAIN_DESC": dominio, "AGG_LEVEL_DESC": nivel,
            "STATE_FIPS_CODE": fips[:2], "STATE_ALPHA": {"20": "KS", "31": "NE"}[fips[:2]],
            "COUNTY_CODE": condado if condado is not None else fips[2:], "YEAR": str(anio), "VALUE": valor}


def censo_2022() -> pd.DataFrame:
    f = []
    # 31001: todo publicado.
    f += [fila("31001", "AG LAND, CROPLAND - ACRES", "200,000"),
          fila("31001", "AG LAND, IRRIGATED - ACRES", "50,000"),
          fila("31001", "CORN, GRAIN, IRRIGATED - ACRES HARVESTED", "60,000"),
          fila("31001", "CORN, GRAIN - ACRES HARVESTED", "100,000"),
          fila("31001", "SOYBEANS, IRRIGATED - ACRES HARVESTED", "20,000"),
          fila("31001", "SOYBEANS - ACRES HARVESTED", "50,000"),
          fila("31001", "AG LAND, CROPLAND, HARVESTED, IRRIGATED - ACRES", "80,000"),
          fila("31001", "AG LAND, CROPLAND, HARVESTED - ACRES", "160,000")]
    # 31003: maíz regado oculto (D); denominador de soja oculto (D); cosechado regado (Z).
    f += [fila("31003", "AG LAND, CROPLAND - ACRES", "100,000"),
          fila("31003", "CORN, GRAIN, IRRIGATED - ACRES HARVESTED", "(D)"),
          fila("31003", "CORN, GRAIN - ACRES HARVESTED", "40,000"),
          fila("31003", "SOYBEANS, IRRIGATED - ACRES HARVESTED", "1,000"),
          fila("31003", "SOYBEANS - ACRES HARVESTED", "(D)"),
          fila("31003", "AG LAND, CROPLAND, HARVESTED, IRRIGATED - ACRES", "(Z)"),
          fila("31003", "AG LAND, CROPLAND, HARVESTED - ACRES", "90,000")]
    # 20001: sin filas de riego por cultivo (no se rellena con 0); maíz regado mayor que el total (fuera de rango).
    f += [fila("20001", "AG LAND, CROPLAND - ACRES", "300,000"),
          fila("20001", "CORN, GRAIN, IRRIGATED - ACRES HARVESTED", "11,000"),
          fila("20001", "CORN, GRAIN - ACRES HARVESTED", "10,000")]
    # Ruido que tiene que quedar afuera: otro dominio, nivel estado, condado 998 y otro año.
    f += [fila("31001", "CORN, GRAIN, IRRIGATED - ACRES HARVESTED", "1", dominio="AREA HARVESTED: (1.0 TO 24.9 ACRES)"),
          fila("31001", "CORN, GRAIN, IRRIGATED - ACRES HARVESTED", "9,999,999", nivel="STATE", condado=""),
          fila("31001", "CORN, GRAIN, IRRIGATED - ACRES HARVESTED", "5", condado="998"),
          fila("31001", "CORN, GRAIN, IRRIGATED - ACRES HARVESTED", "99,000", anio=2017)]
    return pd.DataFrame(f)


class PracticasRiego(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        ref = Path(self.tmp.name) / "data" / "reference"
        ref.mkdir(parents=True)
        pd.DataFrame({"fips": FIPS}).to_csv(ref / "condados.csv", index=False)
        with mock.patch.object(process, "REPO", Path(self.tmp.name)):
            self.df = process.practicas([(2022, censo_2022())]).set_index("fips")

    def tearDown(self):
        self.tmp.cleanup()

    def test_columnas_viejas_intactas_y_nuevas_al_final(self):
        cols = ["fips"] + list(self.df.columns)
        self.assertEqual(cols, COLS_VIEJAS + COLS_NUEVAS)

    def test_porcentajes(self):
        r = self.df.loc["31001"]
        self.assertAlmostEqual(r["pct_maiz_regado"], 60.0)
        self.assertAlmostEqual(r["pct_soja_regada"], 40.0)
        self.assertAlmostEqual(r["pct_cosechado_regado"], 50.0)
        self.assertAlmostEqual(r["pct_riego"], 25.0)  # columna existente, sin cambios
        self.assertEqual(r["flag_nass"], "")

    def test_ocultos_vacios_con_flag(self):
        r = self.df.loc["31003"]
        self.assertTrue(pd.isna(r["pct_maiz_regado"]))
        self.assertTrue(pd.isna(r["pct_soja_regada"]))
        self.assertTrue(pd.isna(r["pct_cosechado_regado"]))
        self.assertEqual(r["flag_nass"],
                         "pct_maiz_regado=(D);pct_soja_regada=(D);pct_cosechado_regado=(Z)")

    def test_sin_fila_queda_vacio_y_fuera_de_rango_vacio(self):
        r = self.df.loc["20001"]
        self.assertTrue(pd.isna(r["pct_maiz_regado"]))  # 110 % -> vacío
        self.assertTrue(pd.isna(r["pct_soja_regada"]))  # sin fila: no es 0
        self.assertTrue(pd.isna(r["pct_cosechado_regado"]))
        self.assertEqual(r["flag_nass"], "")

    def test_csv_flag_vacio_es_celda_vacia(self):
        texto = self.df.reset_index().to_csv(index=False)
        linea = next(l for l in texto.splitlines() if l.startswith("31001,"))
        self.assertTrue(linea.endswith(","))


if __name__ == "__main__":
    unittest.main()
