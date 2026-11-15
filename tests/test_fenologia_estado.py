"""Pruebas sin red de src/cultivos/fenologia.py (T135)."""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cultivos.fenologia import COLUMNAS, fenologia_estado  # noqa: E402


def fila(com, unidad, fecha, valor, clase="ALL CLASSES", util="ALL UTILIZATION PRACTICES", est="31"):
    return {"SOURCE_DESC": "SURVEY", "AGG_LEVEL_DESC": "STATE", "STATISTICCAT_DESC": "PROGRESS",
            "DOMAIN_DESC": "TOTAL", "COMMODITY_DESC": com, "CLASS_DESC": clase, "UNIT_DESC": unidad,
            "UTIL_PRACTICE_DESC": util, "STATE_FIPS_CODE": est, "WEEK_ENDING": fecha,
            "VALUE": valor, "YEAR": fecha[:4]}


def serie(com, unidad, puntos, **kw):
    return [fila(com, unidad, f, v, **kw) for f, v in puntos]


def correr(filas, desde=2000, hasta=2025):
    return fenologia_estado(pd.DataFrame(filas).astype(str), desde, hasta)


class FenologiaEstado(unittest.TestCase):
    def test_cruce_normal(self):
        # 2023-05-07 = doy 127 (30 %), 2023-05-14 = doy 134 (70 %): cruce en 130,5
        r = correr(serie("CORN", "PCT PLANTED", [("2023-04-30", "10"), ("2023-05-07", "30"),
                                                   ("2023-05-14", "70"), ("2023-05-21", "90")]))
        self.assertEqual(len(r), 1)
        f = r.iloc[0]
        self.assertEqual((f["fips_estado"], f["anio"], f["cultivo"]), ("31", 2023, "maiz"))
        self.assertAlmostEqual(f["doy_50_sembrado"], 130.5)
        self.assertTrue(pd.isna(f["flag_hueco_50"]))
        self.assertEqual(list(r.columns), ["fips_estado", "anio", "cultivo"] + COLUMNAS + ["flag_hueco_50"])

    def test_columnas_viejas_primero(self):
        r = correr(serie("SOYBEANS", "PCT PLANTED", [("2023-05-07", "30"), ("2023-05-14", "70")]))
        self.assertEqual(list(r.columns[:7]), ["fips_estado", "anio", "cultivo", "doy_50_sembrado",
                                               "doy_50_emergido", "doy_50_floracion", "doy_50_cosechado"])

    def test_hueco_tres_semanas(self):
        # maíz cosechado 2025: 2025-09-28 (doy 271) 30 %, semanas del cierre faltan o vienen (NA),
        # 2025-10-19 (doy 292) 72 %: 21 días de hueco
        filas = serie("CORN", "PCT HARVESTED", [("2025-09-21", "15"), ("2025-09-28", "30"),
                                                ("2025-10-05", "(NA)"), ("2025-10-19", "72"),
                                                ("2025-10-26", "85")], util="GRAIN")
        filas += serie("CORN", "PCT PLANTED", [("2025-05-04", "40"), ("2025-05-11", "60")])
        r = correr(filas)
        f = r.iloc[0]
        self.assertAlmostEqual(f["doy_50_cosechado"], 271 + 20 * 21 / 42, places=1)
        self.assertEqual(f["flag_hueco_50"], "cosechado")
        self.assertAlmostEqual(f["doy_50_sembrado"], 127.5)  # 2025-05-04 = doy 124

    def test_hueco_sin_cruce_no_marca(self):
        # el hueco existe pero el 50 % se cruza en semanas seguidas: no se marca
        r = correr(serie("CORN", "PCT HARVESTED", [("2025-09-07", "10"), ("2025-09-28", "40"),
                                                   ("2025-10-05", "60")], util="GRAIN"))
        self.assertTrue(pd.isna(r.iloc[0]["flag_hueco_50"]))

    def test_trigo_de_otono_va_al_anio_de_cosecha(self):
        w = {"clase": "WINTER"}
        filas = (serie("WHEAT", "PCT PLANTED", [("2022-09-25", "30"), ("2022-10-02", "60")], **w)
                 + serie("WHEAT", "PCT EMERGED", [("2022-10-09", "40"), ("2022-10-16", "60")], **w)
                 + serie("WHEAT", "PCT HEADED", [("2023-05-14", "20"), ("2023-05-21", "80")], **w)
                 + serie("WHEAT", "PCT HARVESTED", [("2023-07-02", "40"), ("2023-07-09", "60")], **w)
                 # trigo de primavera: no entra
                 + serie("WHEAT", "PCT PLANTED", [("2023-04-23", "30"), ("2023-04-30", "70")],
                         clase="SPRING, (EXCL DURUM)"))
        r = correr(filas)
        self.assertEqual(len(r), 1)
        f = r.iloc[0]
        self.assertEqual((f["anio"], f["cultivo"]), (2023, "trigo_invierno"))
        # 2022-09-25 = doy 268; 30 → 60 en 7 días: 268 + 20/30·7
        self.assertAlmostEqual(f["doy_50_sembrado_otono"], 272.7)
        self.assertAlmostEqual(f["doy_50_emergido_otono"], 285.5)  # 2022-10-09 = 282
        self.assertAlmostEqual(f["doy_50_espigado"], 137.5)  # 2023-05-14 = doy 134
        self.assertAlmostEqual(f["doy_50_cosechado"], 186.5)
        for c in ["doy_50_sembrado", "doy_50_emergido", "doy_50_floracion"]:
            self.assertTrue(pd.isna(f[c]))

    def test_trigo_de_otono_fuera_del_periodo(self):
        # sembrado en otoño de 2025: cosecha 2026, fuera de 2000–2025
        r = correr(serie("WHEAT", "PCT PLANTED", [("2025-09-28", "30"), ("2025-10-05", "60")],
                         clase="WINTER"))
        self.assertTrue(r.empty)

    def test_avena_espigado(self):
        r = correr(serie("OATS", "PCT HEADED", [("2021-06-13", "40"), ("2021-06-20", "60")]))
        f = r.iloc[0]
        self.assertEqual(f["cultivo"], "avena")
        self.assertAlmostEqual(f["doy_50_espigado"], 167.5)  # 2021-06-13 = doy 164
        self.assertTrue(pd.isna(f["doy_50_floracion"]))


if __name__ == "__main__":
    unittest.main()
