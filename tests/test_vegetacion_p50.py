"""NDVI de maíz/soja con umbral de pureza de 50 % (columnas *_p50, T130), sin red.

Un píxel MODIS con 60 % de maíz entra en `ndvi_maiz_p50` y no en `ndvi_maiz` (umbral 75 %). Se prueba la
función de suma, la tesela entera con `zonal_producto` (un GeoTIFF sintético en una carpeta temporal, con
zonas y fracciones del CDL falsas) y `fenologia` (`ndvi_max_maiz_p50`).

Correr:  python -X utf8 -m unittest tests/test_vegetacion_p50.py   (o con pytest)
"""
from __future__ import annotations

import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.vegetacion import process as P  # noqa: E402


class Umbrales(unittest.TestCase):
    def test_constantes(self):
        self.assertEqual(P.UMBRAL_CULTIVO, 0.75)          # la columna original no cambia
        self.assertEqual(P.UMBRAL_CULTIVO_P50, 0.50)
        self.assertEqual(P.COLS_CULTIVO, ["ndvi_maiz", "ndvi_soja", "ndvi_maiz_p50", "ndvi_soja_p50"])

    def test_pixel_60_entra_solo_en_p50(self):
        n = 1
        z = np.array([[1, 1, 1]])
        base = np.array([[True, True, False]])            # el tercero no pasa el filtro de calidad
        fr = np.array([[0.60, 0.80, 0.90]], "float32")
        ndvi = np.array([[0.40, 0.80, 0.10]])
        acc = {k: np.zeros(n + 1) for k in ("n_maiz", "ndvi_maiz", "n_maiz_p50", "ndvi_maiz_p50")}
        P.sumar_cultivo(acc, z, base, fr, ndvi, "maiz", n)
        self.assertEqual(acc["n_maiz"][1], 1)              # solo el de 80 %
        self.assertEqual(acc["n_maiz_p50"][1], 2)          # el de 60 % y el de 80 %
        m = P.medias_cultivo(acc, n)
        self.assertAlmostEqual(m["ndvi_maiz"][0], 0.80)
        self.assertAlmostEqual(m["ndvi_maiz_p50"][0], 0.60)
        self.assertTrue(np.isnan(m["ndvi_soja"][0]) and np.isnan(m["ndvi_soja_p50"][0]))

    def test_solo_60_deja_vacia_la_de_75(self):
        acc = {k: np.zeros(2) for k in ("n_maiz", "ndvi_maiz", "n_maiz_p50", "ndvi_maiz_p50")}
        P.sumar_cultivo(acc, np.array([1]), np.array([True]), np.array([0.6]), np.array([0.5]), "maiz", 1)
        m = P.medias_cultivo(acc, 1)
        self.assertTrue(np.isnan(m["ndvi_maiz"][0]))
        self.assertAlmostEqual(m["ndvi_maiz_p50"][0], 0.5)

    def test_borde_50_entra(self):
        acc = {k: np.zeros(2) for k in ("n_maiz", "ndvi_maiz", "n_maiz_p50", "ndvi_maiz_p50")}
        P.sumar_cultivo(acc, np.array([1, 1]), np.array([True, True]), np.array([0.5, 0.49]),
                        np.array([0.7, 0.2]), "maiz", 1)
        self.assertEqual(acc["n_maiz_p50"][1], 1)          # >= 50 %, no > 50 %
        self.assertEqual(acc["n_maiz"][1], 0)


class ZonalTesela(unittest.TestCase):
    """zonal_producto con un MOD13Q1 sintético de 6x6 píxeles y dos condados."""

    def test_zonal(self):
        import rasterio
        from rasterio.transform import from_origin

        H = W = 6
        ndvi = np.full((H, W), 6000, "int16")
        ndvi[2, 2], ndvi[2, 3] = 4000, 8000
        evi = np.full((H, W), 3000, "int16")
        rel = np.zeros((H, W), "int16")
        z = np.zeros((H, W), "int32")
        z[1:5, 1:3], z[1:5, 3:5] = 1, 2                     # condado 1 a la izquierda, 2 a la derecha
        fr_maiz = np.zeros((H, W), "float32")
        fr_maiz[2, 2] = 0.60                               # condado 1: solo un píxel de 60 %
        fr_maiz[2, 3] = 0.80                               # condado 2: un píxel de 80 %
        fr_soja = np.zeros((H, W), "float32")

        class Zon:
            n = 2
            gdf = pd.DataFrame({"fips": ["39001", "39003"]})

            def get(self, src):
                return z

        class Cult:
            def frac(self, c, anio, src):
                return fr_maiz if c == "maiz" else fr_soja

            def liberar(self, anio):
                pass

        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "mod13q1" / "2012"
            d.mkdir(parents=True)
            with rasterio.open(d / "MOD13Q1.A2012193.h11v04.061.tif", "w", driver="GTiff", height=H, width=W,
                               count=3, dtype="int16", crs="EPSG:5070",
                               transform=from_origin(0, 0, 927, 927)) as dst:
                dst.write(np.stack([ndvi, evi, rel]))
            with mock.patch.object(P, "RAW", Path(tmp)):
                out = P.zonal_producto("mod13q1", Zon(), P.validos_mod13, ["ndvi", "evi"], Cult())
        out = out.set_index("fips")
        self.assertTrue(np.isnan(out.loc["39001", "ndvi_maiz"]))            # 60 % no llega a 75 %
        self.assertAlmostEqual(out.loc["39001", "ndvi_maiz_p50"], 0.40)
        self.assertAlmostEqual(out.loc["39003", "ndvi_maiz"], 0.80)
        self.assertAlmostEqual(out.loc["39003", "ndvi_maiz_p50"], 0.80)
        self.assertTrue(out[["ndvi_soja", "ndvi_soja_p50"]].isna().all().all())


class Fenologia(unittest.TestCase):
    def test_ndvi_max_p50(self):
        fechas = [dt.date(2012, 1, 1) + dt.timedelta(days=16 * i) for i in range(23)]
        y = 0.3 + 0.5 * np.sin(np.linspace(0, np.pi, 23))
        g = pd.DataFrame({"fecha": fechas, "ndvi": y, "ndvi_maiz": np.nan, "ndvi_soja": np.nan,
                          "ndvi_maiz_p50": y + 0.01, "ndvi_soja_p50": np.nan})
        fila = P.fenologia(g)[0]
        self.assertNotIn("ndvi_max_maiz", fila)                             # sin datos al 75 %
        self.assertAlmostEqual(fila["ndvi_max_maiz_p50"], float(np.max(y)) + 0.01)
        self.assertNotIn("ndvi_max_soja_p50", fila)

    def test_sin_columnas_p50_sigue_andando(self):
        fechas = [dt.date(2012, 1, 1) + dt.timedelta(days=16 * i) for i in range(23)]
        y = 0.3 + 0.5 * np.sin(np.linspace(0, np.pi, 23))
        g = pd.DataFrame({"fecha": fechas, "ndvi": y, "ndvi_maiz": y, "ndvi_soja": np.nan})
        fila = P.fenologia(g)[0]
        self.assertIn("ndvi_max_maiz", fila)
        self.assertNotIn("ndvi_max_maiz_p50", fila)


if __name__ == "__main__":
    unittest.main()
