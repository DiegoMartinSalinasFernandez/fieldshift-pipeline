"""Ventanas de floración del maíz y llenado de la soja por estado y año en clima_anual.csv (T128).

Sin red: una serie diaria armada a mano y ventanas conocidas; se comprueba la suma diaria dentro de la
ventana, que un estado-año sin cruce quede vacío (nunca la ventana de otro año) y la interpolación de los
cruces de Crop Progress.

Correr:  python -X utf8 -m pytest -q tests/test_clima_ventanas.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.clima import ventanas as V  # noqa: E402


def diario(fips: str, anios: list[int]) -> pd.DataFrame:
    """Lluvia = día del año / 10 mm, tmax = 25 + (doy % 15) °C, ETo = 4 mm, para cada año."""
    partes = []
    for a in anios:
        f = pd.date_range(f"{a}-01-01", f"{a}-12-31", freq="D")
        doy = f.day_of_year.to_numpy()
        partes.append(pd.DataFrame({"fips": fips, "fecha": f, "prec_power_mm": doy / 10,
                                    "tmax_c": 25.0 + doy % 15, "eto_pm_mm": 4.0}))
    return pd.concat(partes, ignore_index=True)


class Cruce(unittest.TestCase):
    def test_interpola_entre_semanas(self):
        # 10 % el día 190, 40 % el 197: el 25 % cae a mitad de camino
        self.assertAlmostEqual(V.cruce([183, 190, 197, 204], [0, 10, 40, 80], 25), 193.5)
        self.assertAlmostEqual(V.cruce([183, 190, 197, 204], [0, 10, 40, 80], 75), 197 + 35 / 40 * 7)

    def test_sin_cruce_si_arranca_arriba_o_no_llega(self):
        self.assertTrue(np.isnan(V.cruce([190, 197], [30, 60], 25)))
        self.assertTrue(np.isnan(V.cruce([190, 197], [5, 20], 25)))

    def test_semanas_quickstats(self):
        crops = pd.DataFrame({
            "SOURCE_DESC": "SURVEY", "AGG_LEVEL_DESC": "STATE", "STATISTICCAT_DESC": "PROGRESS",
            "DOMAIN_DESC": "TOTAL", "UTIL_PRACTICE_DESC": "ALL UTILIZATION PRACTICES", "STATE_FIPS_CODE": "19",
            "COMMODITY_DESC": "CORN", "UNIT_DESC": "PCT SILKING",
            "WEEK_ENDING": ["2023-07-02", "2023-07-09", "2023-07-16", "2023-07-23"],
            "VALUE": ["2", "18", "53", "85"]})
        v = V.ventanas_desde_semanas(V.semanas_quickstats(crops))
        self.assertEqual(len(v), 1)
        r = v.iloc[0]
        self.assertEqual(r["fips_estado"], "19")
        self.assertAlmostEqual(r["doy_ini_floracion_maiz"], 190 + 7 / 35 * 7)   # 9 jul = día 190
        self.assertAlmostEqual(r["doy_fin_floracion_maiz"], 197 + 22 / 32 * 7)
        self.assertTrue(np.isnan(r["doy_ini_llenado_soja"]))   # sin semanas de soja: vacío

    def test_csv_research(self):
        v = V.ventanas_research()
        r = v[(v["fips_estado"] == "39") & (v["anio"] == 2019)].iloc[0]
        self.assertGreater(r["doy_fin_floracion_maiz"], r["doy_ini_floracion_maiz"])
        self.assertTrue(set(v["fips_estado"]) <= set(V.ALFA_FIPS.values()))


class ColumnasVentanas(unittest.TestCase):
    def setUp(self):
        self.d = diario("19169", [2022, 2023])
        # 2023: ventanas armadas a mano. 2022: sin cruce de silking ni de soja (como IA 2008 en setting pods)
        self.v = pd.DataFrame({"fips_estado": ["19", "19"], "anio": [2022, 2023],
                               "doy_ini_floracion_maiz": [np.nan, 192.4], "doy_fin_floracion_maiz": [np.nan, 204.6],
                               "doy_ini_llenado_soja": [np.nan, 210.0], "doy_fin_llenado_soja": [np.nan, 255.0]})
        self.a = V.columnas_ventanas(self.d, self.v).set_index("anio")

    def test_suma_diaria_dentro_de_la_ventana(self):
        r = self.a.loc[2023]
        dias = np.arange(192, 206)          # round(192,4)=192 .. round(204,6)=205, inclusive
        self.assertEqual((r["doy_ini_floracion_maiz"], r["doy_fin_floracion_maiz"]), (192, 205))
        self.assertAlmostEqual(r["prec_floracion_maiz_mm"], (dias / 10).sum())
        tmax = 25.0 + dias % 15
        self.assertAlmostEqual(r["tmax_floracion_maiz_c"], tmax.mean())
        self.assertEqual(r["dias_tmax_gt30_floracion_maiz"], int((tmax > 30).sum()))
        self.assertEqual(r["dias_tmax_gt35_floracion_maiz"], int((tmax > 35).sum()))
        soja = np.arange(210, 256)
        self.assertAlmostEqual(r["prec_llenado_soja_mm"], (soja / 10).sum())
        self.assertAlmostEqual(r["deficit_llenado_soja_mm"], (soja / 10 - 4).sum())
        self.assertAlmostEqual(r["tmax_llenado_soja_c"], (25.0 + soja % 15).mean())

    def test_sin_cruce_queda_vacio(self):
        r = self.a.loc[2022]
        for c in V.COLS_NUEVAS:
            if c != "prec_ago_sep15_mm":
                self.assertTrue(pd.isna(r[c]), c)

    def test_ago_sep15_no_depende_de_la_fenologia(self):
        # 2022 no es bisiesto: 1 ago = día 213, 15 sep = día 258
        self.assertAlmostEqual(self.a.loc[2022, "prec_ago_sep15_mm"], (np.arange(213, 259) / 10).sum())

    def test_falta_un_dia_dentro_de_la_ventana(self):
        d = self.d.copy()
        d.loc[(d["fecha"] == "2023-07-15"), "prec_power_mm"] = np.nan
        a = V.columnas_ventanas(d, self.v).set_index("anio")
        self.assertTrue(pd.isna(a.loc[2023, "prec_floracion_maiz_mm"]))
        self.assertFalse(pd.isna(a.loc[2023, "tmax_floracion_maiz_c"]))
        self.assertFalse(pd.isna(a.loc[2023, "prec_llenado_soja_mm"]))

    def test_estado_sin_ventanas_y_columnas(self):
        d = pd.concat([self.d, diario("39049", [2023])], ignore_index=True)
        a = V.columnas_ventanas(d, self.v)
        self.assertEqual(list(a.columns), ["fips", "anio", *V.COLS_NUEVAS])
        oh = a[a["fips"] == "39049"].iloc[0]
        self.assertTrue(pd.isna(oh["prec_floracion_maiz_mm"]))   # Ohio no tiene filas: nunca la de Iowa
        self.assertFalse(pd.isna(oh["prec_ago_sep15_mm"]))

    def test_no_pisa_columnas_existentes(self):
        existentes = {"doy_ultima_helada", "doy_primera_helada", "periodo_libre_heladas_dias", "prec_temporada_mm",
                      "gdd_temporada", "prec_invierno_previo_mm", "prec_jul_mm", "tmax_jul_c", "dias_tmax_gt30_jul",
                      "prec_ago_mm", "deficit_temporada_mm", "tend_prec_mm_decada", "tend_tmed_c_decada"}
        self.assertFalse(existentes & set(V.COLS_NUEVAS))


if __name__ == "__main__":
    unittest.main()
