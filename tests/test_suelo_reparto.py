"""Reparto por condado de las áreas de levantamiento de SSURGO (T120), sin red.

`repartir_por_condado()` de `src/suelo_terreno/process.py`:
- en las áreas `XX` + código de condado (y las de `AREAS_ESPECIALES` de MN) da lo mismo que el
  reparto anterior con `fips_de_area()` y `muacres`;
- reparte un área de dos condados (`KY603`-like) y un área especial (`KY648`, Mammoth Cave) con el
  `areaovacres` de `muaoverlap`.

Correr:  python -X utf8 -m pytest -q tests/test_suelo_reparto.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def cargar():
    spec = importlib.util.spec_from_file_location("t120_suelo_process", REPO / "src/suelo_terreno/process.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pr = cargar()
ESTADOS = {"IA": "19", "MN": "27", "KY": "21"}


def mapunit(filas):
    return pd.DataFrame(filas, columns=["areasymbol", "mukey", "muacres", "aws0100wta", "drclassdcd"])


def agregar(mu, peso):
    """La agregación de process.main(): media ponderada y clase dominante."""
    cond = pr.media_pond(mu, "fips", peso, ["aws0100wta"])
    v = mu.dropna(subset=["drclassdcd", peso])
    cond["clase"] = (v.groupby(["fips", "drclassdcd"])[peso].sum().reset_index()
                     .sort_values(["fips", peso, "drclassdcd"], ascending=[True, False, True])
                     .groupby("fips").head(1).set_index("fips")["drclassdcd"])
    return cond.sort_index()


class TestReparto(unittest.TestCase):
    def test_identico_en_areas_de_un_condado(self):
        mu = mapunit([
            ("IA169", 1, 100.0, 20.0, "Well drained"),
            ("IA169", 2, 300.0, 25.0, "Poorly drained"),
            ("IA169", 3, np.nan, 99.0, "Well drained"),  # sin muacres: no pesa
            ("IA015", 4, 50.0, np.nan, "Well drained"),
            ("MN613", 5, 80.0, 18.0, "Moderately well drained"),  # St. Louis
            ("MN615", 6, 20.0, 30.0, "Well drained"),             # St. Louis
            ("MN627", 7, 500.0, 10.0, "Very poorly drained"),     # Voyageurs: afuera
        ])
        validos = {"19169", "19015", "27137", "27071"}
        # reparto anterior
        viejo = mu.assign(fips=mu["areasymbol"].map(lambda a: pr.fips_de_area(a, ESTADOS))).dropna(subset=["fips"])
        # solape presente pero no debe usarse para estas áreas
        solape = pd.DataFrame({"areasymbol": ["IA169", "MN627"], "condado": ["IA169", "MN071"],
                               "mukey": [1, 7], "areaovacres": [1.0, 500.0]})
        for sol in (None, solape):
            nuevo, sin = pr.repartir_por_condado(mu, sol, validos, ESTADOS)
            self.assertEqual(sin, [])
            pd.testing.assert_frame_equal(agregar(viejo, "muacres"), agregar(nuevo, "peso"))
            self.assertEqual(sorted(nuevo["fips"].unique()), ["19015", "19169", "27137"])

    def test_area_de_dos_condados(self):
        mu = mapunit([
            ("KY601", 10, 1000.0, 20.0, "Well drained"),
            ("KY601", 11, 1000.0, 10.0, "Poorly drained"),
        ])
        solape = pd.DataFrame({"areasymbol": ["KY601"] * 3, "condado": ["KY003", "KY003", "KY213"],
                               "mukey": [10, 11, 11], "areaovacres": [300.0, 100.0, 900.0]})
        nuevo, sin = pr.repartir_por_condado(mu, solape, {"21003", "21213"}, ESTADOS)
        self.assertEqual(sin, [])
        c = agregar(nuevo, "peso")
        self.assertAlmostEqual(c.loc["21003", "aws0100wta"], (20 * 300 + 10 * 100) / 400)
        self.assertEqual(c.loc["21003", "clase"], "Well drained")
        self.assertAlmostEqual(c.loc["21213", "aws0100wta"], 10.0)  # la unidad 10 no está en 21213
        self.assertEqual(c.loc["21213", "clase"], "Poorly drained")
        self.assertNotIn("21601", c.index)

    def test_area_especial_y_condado_partido(self):
        # Barren (21009) = KY646 (área con código propio) + parte de KY648 (Mammoth Cave)
        mu = mapunit([
            ("KY646", 20, 3000.0, 15.0, "Well drained"),
            ("KY648", 21, 500.0, 40.0, "Moderately well drained"),
            ("KY001", 22, 200.0, 12.0, "Well drained"),
            ("KY999", 23, 10.0, 12.0, "Well drained"),  # sin solape: queda afuera y se avisa
        ])
        solape = pd.DataFrame({"areasymbol": ["KY646", "KY648", "KY648", "KY648"],
                               "condado": ["KY009", "KY009", "KY061", "KY099"],
                               "mukey": [20, 21, 21, 21], "areaovacres": [3000.0, 100.0, 300.0, 100.0]})
        validos = {"21001", "21009", "21061", "21099"}
        nuevo, sin = pr.repartir_por_condado(mu, solape, validos, ESTADOS)
        self.assertEqual(sin, ["KY999"])
        c = agregar(nuevo, "peso")
        self.assertAlmostEqual(c.loc["21009", "aws0100wta"], (15 * 3000 + 40 * 100) / 3100)
        self.assertAlmostEqual(c.loc["21061", "aws0100wta"], 40.0)
        self.assertAlmostEqual(c.loc["21001", "aws0100wta"], 12.0)  # área propia: por muacres
        self.assertEqual(set(c.index), validos)
        # el peso total de KY648 es su superficie en los condados, no se duplica muacres
        self.assertAlmostEqual(nuevo.loc[nuevo["areasymbol"] == "KY648", "peso"].sum(), 500.0)

    def test_fips_de_condado(self):
        self.assertEqual(pr.fips_de_condado("KY015", ESTADOS), "21015")
        self.assertTrue(pd.isna(pr.fips_de_condado("TN015", ESTADOS)))
        self.assertTrue(pd.isna(pr.fips_de_condado("KY6A1", ESTADOS)))


if __name__ == "__main__":
    unittest.main()
