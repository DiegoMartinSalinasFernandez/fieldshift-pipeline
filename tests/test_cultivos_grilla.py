"""Prueba de src/cultivos/grilla.py (T138) con un `produccion_anual.csv` chico e inventado. Sin red.

Correr:  python -X utf8 -m unittest tests/test_cultivos_grilla.py   (o con pytest)
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.cultivos import grilla  # noqa: E402

COLS = ["fips", "anio", "cultivo", "sup_sembrada_ac", "sup_cosechada_ac", "produccion_bu",
        "rend_bu_ac", "rend_kgha", "sup_sembrada_ha", "ratio_cosechada", "flag_nass"]


def prod_chico() -> pd.DataFrame:
    return pd.DataFrame([
        ["31001", 2024, "maiz", 1000.0, 900.0, 180000.0, 200.0, 12554.0, 404.7, 0.9, np.nan],
        ["31001", 2025, "soja", 500.0, 490.0, 29400.0, 60.0, 4035.0, 202.4, 0.98, np.nan],
        ["20001", 2024, "maiz", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, "(D)"],
    ], columns=COLS)


class TestCompletarGrilla(unittest.TestCase):
    FIPS = ["31001", "31003", "20001"]
    ANIOS = [2024, 2025]
    CULTIVOS = ["maiz", "soja"]

    def test_grilla_completa_y_fila_nass(self):
        out = grilla.completar_grilla(prod_chico(), self.FIPS, self.ANIOS, self.CULTIVOS)
        self.assertEqual(len(out), 3 * 2 * 2)
        self.assertEqual(list(out.columns), COLS + ["fila_nass"])
        self.assertFalse(out.duplicated(["fips", "anio", "cultivo"]).any())
        self.assertEqual(int(out["fila_nass"].sum()), 3)
        # la fila con solo (D) viene de NASS y conserva el flag
        d = out[(out.fips == "20001") & (out.anio == 2024) & (out.cultivo == "maiz")].iloc[0]
        self.assertEqual(d["fila_nass"], 1)
        self.assertEqual(d["flag_nass"], "(D)")
        # las completadas tienen todas las variables vacías
        comp = out[out.fila_nass == 0]
        self.assertTrue(comp[COLS[3:]].isna().all().all())
        # las de NASS no cambian
        orig = out[(out.fips == "31001") & (out.anio == 2024) & (out.cultivo == "maiz")].iloc[0]
        self.assertEqual(orig["rend_bu_ac"], 200.0)
        # orden por claves
        self.assertTrue(out.equals(out.sort_values(["fips", "anio", "cultivo"]).reset_index(drop=True)))

    def test_idempotente(self):
        uno = grilla.completar_grilla(prod_chico(), self.FIPS, self.ANIOS, self.CULTIVOS)
        dos = grilla.completar_grilla(uno, self.FIPS, self.ANIOS, self.CULTIVOS)
        pd.testing.assert_frame_equal(uno, dos)

    def test_conserva_filas_fuera_de_grilla(self):
        out = grilla.completar_grilla(prod_chico(), ["31001"], [2024], ["maiz"])
        self.assertEqual(len(out), 3)  # 1 de la grilla + 2 que ya estaban fuera
        self.assertEqual(int(out["fila_nass"].sum()), 3)

    def test_duplicados_fallan(self):
        p = pd.concat([prod_chico(), prod_chico().iloc[:1]], ignore_index=True)
        with self.assertRaises(ValueError):
            grilla.completar_grilla(p, self.FIPS, self.ANIOS, self.CULTIVOS)

    def test_resumen(self):
        out = grilla.completar_grilla(prod_chico(), self.FIPS, self.ANIOS, self.CULTIVOS)
        r = grilla.resumen(out).set_index(["estado", "anio"])
        self.assertEqual(r.loc[("31", 2024), "completadas"], 3)
        self.assertEqual(r.loc[("20", 2024), "de_nass"], 1)
        self.assertEqual(int(r["filas"].sum()), 12)


class TestMainCsv(unittest.TestCase):
    def test_reescribe_csv_idempotente(self):
        cfg = {"periodo": {"anio_inicio": 2024, "anio_fin": 2025},
               "cultivos": {"maiz": "Maíz", "soja": "Soja"}}
        estados = {"NE": {"fips": "31"}, "KS": {"fips": "20"}}
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            pd.DataFrame({"fips": ["31001", "31003", "20001", "19001"]}).to_csv(tmp / "c.csv", index=False)
            ruta = tmp / "produccion_anual.csv"
            prod_chico().to_csv(ruta, index=False)
            with mock.patch("src.common.config.cargar_config", return_value=cfg), \
                 mock.patch("src.common.config.estados_config", return_value=estados), \
                 redirect_stdout(StringIO()):
                grilla.main([str(ruta), "--condados", str(tmp / "c.csv")])
                primero = ruta.read_bytes()
                grilla.main([str(ruta), "--condados", str(tmp / "c.csv")])
            self.assertEqual(primero, ruta.read_bytes())
            out = pd.read_csv(ruta, dtype={"fips": str, "flag_nass": str})
            self.assertEqual(len(out), 12)  # 19001 no es de los estados
            self.assertEqual(out.columns[-1], "fila_nass")
            self.assertEqual(out.loc[out.fips == "20001", "flag_nass"].dropna().tolist(), ["(D)"])


if __name__ == "__main__":
    unittest.main()
