"""Pruebas sin red de src/cultivos/sorgo.py (T137) con arrays y rasters chicos inventados.

Correr:  python -X utf8 -m pytest -q tests/test_sorgo_rotacion.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.cultivos import sorgo  # noqa: E402

W, S, F, M, P, D = 24, 4, 61, 1, 176, 236  # trigo, sorgo, barbecho, maíz, pastizal, doble trigo/sorgo


class Nucleo(unittest.TestCase):
    def test_porcentajes_y_transiciones(self):
        # 6 píxeles, todos del condado 1
        ids = np.ones(6, np.int32)
        previo = np.array([W, W, S, F, P, M], np.uint8)
        actual = np.array([S, D, F, W, S, S], np.uint8)
        acc = {}
        sorgo.acumular_anio(ids, actual, previo, 1, acc)
        c = sorgo.porcentajes_anio(acc, hay_previo=True)
        # agrícolas en el año actual: los 6 (176 no está en `actual`)
        self.assertAlmostEqual(c["pct_sorgo"][0], 100 * 4 / 6)          # S, D, S, S
        self.assertAlmostEqual(c["pct_doble_trigo_sorgo"][0], 100 / 6)
        # sorgo actual con año anterior agrícola: S(W), D(W), S(M); el de pastizal no cuenta
        self.assertAlmostEqual(c["pct_sorgo_tras_trigo"][0], 100 * 2 / 3)
        self.assertAlmostEqual(c["pct_sorgo_tras_sorgo"][0], 0.0)
        self.assertAlmostEqual(c["pct_barbecho_tras_sorgo"][0], 100.0)
        self.assertAlmostEqual(c["pct_trigo_tras_barbecho"][0], 100.0)

    def test_sin_denominador_queda_vacio(self):
        ids = np.array([1, 1, 2], np.int32)
        acc = {}
        sorgo.acumular_anio(ids, np.array([M, M, P], np.uint8), np.array([M, M, P], np.uint8), 2, acc)
        c = sorgo.porcentajes_anio(acc, hay_previo=True)
        self.assertEqual(c["pct_sorgo"][0], 0.0)
        self.assertTrue(np.isnan(c["pct_sorgo"][1]))           # condado 2 sin área agrícola
        self.assertTrue(np.isnan(c["pct_sorgo_tras_trigo"][0]))  # sin sorgo: vacío, no 0

    def test_primer_anio_sin_transiciones(self):
        acc = {}
        sorgo.acumular_anio(np.ones(2, np.int32), np.array([S, W], np.uint8), None, 1, acc)
        c = sorgo.porcentajes_anio(acc, hay_previo=False)
        self.assertEqual(c["pct_sorgo"][0], 50.0)
        for col in sorgo.TRANS_SORGO:
            self.assertTrue(np.isnan(c[col][0]))

    def test_secuencia_trigo_sorgo_barbecho(self):
        pila = np.array([
            [W, S, F, W, S, F, W, S],  # WSF
            [M, M, M, M, W, S, F, W],  # WSF al final
            [W, F, W, F, W, F, W, F],  # trigo-barbecho, sin sorgo
            [S, F, W, M, S, F, W, P],  # pastizal el último año: fuera del denominador
            [M, D, F, W, M, M, M, M],  # doble trigo/sorgo cuenta como sorgo, no como trigo
        ], np.uint8).T
        v = sorgo.indicadores_secuencia(pila)
        self.assertEqual(v["base"].tolist(), [True, True, True, False, True])
        self.assertEqual(v["trigo_sorgo_barbecho"].tolist(), [True, True, False, False, False])
        self.assertEqual(v["sorgo"].tolist(), [True, True, False, True, True])

    def test_sumar_columnas_idempotente(self):
        base = pd.DataFrame({"fips": ["20001", "31001"], "anio": [2020, 2020], "pct_maiz": [10.0, 50.0]})
        nuevas = pd.DataFrame({"fips": ["20001"], "anio": [2020], "pct_sorgo": [30.0]})
        una = sorgo.sumar_columnas(base, nuevas, ["fips", "anio"])
        dos = sorgo.sumar_columnas(una, nuevas, ["fips", "anio"])
        pd.testing.assert_frame_equal(una, dos)
        self.assertEqual(list(una.columns), ["fips", "anio", "pct_maiz", "pct_sorgo"])
        self.assertTrue(np.isnan(una.loc[1, "pct_sorgo"]))  # Nebraska: vacío
        self.assertEqual(una.loc[0, "pct_sorgo"], 30.0)


class Rasters(unittest.TestCase):
    """Una tesela de 10 × 10 píxeles de 30 m (EPSG:5070) con un condado que la cubre entera."""

    def setUp(self):
        import geopandas as gpd
        import rasterio
        from rasterio.transform import from_origin
        from shapely.geometry import box

        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        lado = 300
        x0, ytop = 0, 300
        clave = f"{x0}_{ytop - 30}_{lado}"
        # columnas 0-4: trigo-sorgo-barbecho desfasado; 5-9: maíz siempre
        ciclo = [W, S, F]
        self.tes = {}
        for k, a in enumerate(range(2010, 2019)):
            arr = np.full((10, 10), M, np.uint8)
            arr[:, :5] = ciclo[k % 3]
            ruta = d / f"{a}_30m_cdls_{clave}.tif"
            with rasterio.open(ruta, "w", driver="GTiff", width=10, height=10, count=1, dtype="uint8",
                               crs="EPSG:5070", transform=from_origin(x0, ytop, 30, 30)) as dst:
                dst.write(arr, 1)
            self.tes[a] = {clave: ruta}
        self.cond = gpd.GeoDataFrame({"fips": ["20071"]}, geometry=[box(1, 1, lado - 1, ytop - 1)],
                                     crs=5070)

    def tearDown(self):
        self.tmp.cleanup()

    def test_anual(self):
        df = sorgo.rotacion_sorgo_anual(self.cond, self.tes)
        self.assertEqual(df["anio"].tolist(), list(range(2010, 2019)))
        self.assertEqual(df.columns[:2].tolist(), ["fips", "anio"])
        f = df.set_index("anio")
        self.assertEqual(f.loc[2011, "pct_sorgo"], 50.0)        # 2011: sorgo en la mitad
        self.assertEqual(f.loc[2011, "pct_sorgo_tras_trigo"], 100.0)
        self.assertEqual(f.loc[2012, "pct_barbecho_tras_sorgo"], 100.0)
        self.assertEqual(f.loc[2013, "pct_trigo_tras_barbecho"], 100.0)
        self.assertTrue(np.isnan(f.loc[2010, "pct_sorgo_tras_trigo"]))  # primer año
        self.assertEqual(f.loc[2010, "pct_sorgo"], 0.0)

    def test_secuencia(self):
        df = sorgo.rotacion_sorgo_secuencia(self.cond, self.tes)
        self.assertEqual(df["ventana"].tolist(), ["2010-2017", "2011-2018"])
        self.assertTrue((df["pct_trigo_sorgo_barbecho"] == 50.0).all())
        self.assertTrue((df["pct_rotacion_sorgo"] == 50.0).all())


if __name__ == "__main__":
    unittest.main()
