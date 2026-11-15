"""SEETileDrain por píxel en el paquete lotes (T131), sin red.

Arma un GeoTIFF chico en EPSG:4326 con la misma estructura que los de SEETileDrain (tiras de una fila, sin
compresión interna), lo mete en un zip con deflate (también zip64) y comprueba que:
- `recortar_miembro()` infla en flujo y corta exactamente la ventana del recuadro, sin leer el resto;
- `muestrear()` toma la celda que contiene el centro del píxel de 30 m (EPSG:5070);
- `columnas_lote()` da NaN si falta el recorte y filtra valores fuera de rango.

Correr:  python -X utf8 -m pytest -q tests/test_lotes_seetiledrain.py
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.transform import from_origin

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src" / "lotes"))

CELDA = 0.00026949458523585647
LON0, LAT0 = -93.60, 42.10
ANCHO, ALTO = 400, 300


def cargar():
    spec = importlib.util.spec_from_file_location("t131_drenaje", REPO / "src/lotes/drenaje.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def escribir_tif(ruta: Path, arr: np.ndarray, nodata=None, bigtiff: bool = True) -> None:
    perfil = dict(driver="GTiff", width=arr.shape[1], height=arr.shape[0], count=1, dtype=arr.dtype.name,
                  crs="EPSG:4326", transform=from_origin(LON0, LAT0, CELDA, CELDA), tiled=False,
                  blockysize=1, compress="none", BIGTIFF="YES" if bigtiff else "NO")
    if nodata is not None:
        perfil["nodata"] = nodata
    with rasterio.open(ruta, "w", **perfil) as d:
        d.write(arr, 1)


def zipear(zip_ruta: Path, miembros: dict[str, Path], zip64: bool = False) -> None:
    with zipfile.ZipFile(zip_ruta, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("SEETileDrain_maps/", b"")
        for nombre, ruta in miembros.items():
            with z.open(zipfile.ZipInfo(nombre), "w", force_zip64=zip64) as o:
                o.write(ruta.read_bytes())


class TestSEETileDrain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = cargar()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        rng = np.random.default_rng(131)
        cls.prob = rng.random((ALTO, ANCHO)).astype("float32")
        cls.prob[:5, :] = -1.0  # nodata
        cls.clase = (cls.prob >= 0.5).astype("int32")
        escribir_tif(cls.dir / "prob.tif", cls.prob, nodata=-1.0)
        escribir_tif(cls.dir / "clase.tif", cls.clase, bigtiff=False)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _recortar(self, zip64: bool, capa: str, recuadros: dict) -> dict:
        z = self.dir / f"maps_{zip64}.zip"
        zipear(z, {"SEETileDrain_maps/probability_tile_mosaic.tif": self.dir / "prob.tif",
                   "SEETileDrain_maps/SEETileDrain.tif": self.dir / "clase.tif"}, zip64=zip64)
        leidos = []
        base = self.m.rangos_local(z, trozo=4096)

        def leer(ini, fin):
            leidos.append((ini, fin))
            return base(ini, fin)
        out = self.m.recortar_miembro(leer, z.stat().st_size, self.m.CAPAS[capa], recuadros,
                                      lambda k: self.dir / f"rec_{zip64}_{capa}_{k}.tif", cabecera_max=1 << 16)
        return out

    def test_recorte_igual_a_la_ventana(self):
        # recuadro en lon/lat con filas 100-120 y columnas 50-80 (antes del margen)
        x0, x1 = LON0 + 50 * CELDA, LON0 + 80 * CELDA
        y1, y0 = LAT0 - 100 * CELDA, LAT0 - 120 * CELDA
        for zip64 in (False, True):
            for capa, ref in (("prob", self.prob), ("clase", self.clase)):
                out = self._recortar(zip64, capa, {"L1": (x0, y0, x1, y1)})
                with rasterio.open(out["L1"]) as d:
                    a = d.read(1)
                    c0 = int(round((d.transform.c - LON0) / CELDA))
                    f0 = int(round((LAT0 - d.transform.f) / CELDA))
                    self.assertEqual(str(d.crs), "EPSG:4326")
                    self.assertAlmostEqual(d.transform.a, CELDA)
                np.testing.assert_array_equal(a, ref[f0:f0 + a.shape[0], c0:c0 + a.shape[1]])
                self.assertLessEqual(f0, 100)
                self.assertGreaterEqual(f0 + a.shape[0], 120)

    def test_varios_recuadros_una_pasada(self):
        rec = {"A": (LON0 + 10 * CELDA, LAT0 - 40 * CELDA, LON0 + 20 * CELDA, LAT0 - 30 * CELDA),
               "B": (LON0 + 300 * CELDA, LAT0 - 250 * CELDA, LON0 + 320 * CELDA, LAT0 - 230 * CELDA),
               "C": (LON0 + 5 * CELDA, LAT0 - 12 * CELDA, LON0 + 15 * CELDA, LAT0 - 1 * CELDA),
               "fuera": (LON0 - 1, LAT0 + 1, LON0 - 0.9, LAT0 + 1.1)}
        for capa, ref in (("clase", self.clase), ("prob", self.prob)):
            out = self._recortar(False, capa, rec)
            self.assertEqual(sorted(out), ["A", "B", "C"])
            for k, ruta in out.items():  # "C" toca las filas de nodata, que GDAL escribe al final del archivo
                with rasterio.open(ruta) as d:
                    a = d.read(1)
                    c0 = int(round((d.transform.c - LON0) / CELDA))
                    f0 = int(round((LAT0 - d.transform.f) / CELDA))
                np.testing.assert_array_equal(a, ref[f0:f0 + a.shape[0], c0:c0 + a.shape[1]])

    def test_muestreo_celda_que_contiene_el_centro(self):
        ruta = self.dir / "prob.tif"
        a5070 = Transformer.from_crs(4326, 5070, always_xy=True)
        filas, cols = np.array([10, 150, 299, 2]), np.array([0, 200, 399, 7])
        lon = LON0 + (cols + 0.5) * CELDA
        lat = LAT0 - (filas + 0.5) * CELDA
        x, y = a5070.transform(lon, lat)
        v = self.m.muestrear(ruta, np.array(x), np.array(y))
        np.testing.assert_allclose(v[:3], self.prob[filas[:3], cols[:3]], rtol=1e-6)
        self.assertTrue(np.isnan(v[3]))  # nodata
        xf, yf = a5070.transform([LON0 - 0.01], [LAT0 + 0.01])
        self.assertTrue(np.isnan(self.m.muestrear(ruta, np.array(xf), np.array(yf))[0]))

    def test_columnas_lote(self):
        raw_antes = self.m.RAW
        try:
            self.m.RAW = self.dir / "raw"
            self.m.RAW.mkdir(exist_ok=True)
            a5070 = Transformer.from_crs(4326, 5070, always_xy=True)
            x, y = a5070.transform(LON0 + 20.5 * CELDA, LAT0 - 20.5 * CELDA)
            x, y = np.array([x]), np.array([y])
            vacio = self.m.columnas_lote("L9", x, y)
            self.assertEqual(set(vacio), {"tile_prob_seetiledrain", "tile_seetiledrain"})
            self.assertTrue(all(np.isnan(v).all() for v in vacio.values()))
            escribir_tif(self.m.RAW / "prob_L9.tif", self.prob)
            mala = self.clase.copy()
            mala[20, 20] = 7
            escribir_tif(self.m.RAW / "clase_L9.tif", mala)
            o = self.m.columnas_lote("L9", x, y)
            self.assertAlmostEqual(o["tile_prob_seetiledrain"][0], float(self.prob[20, 20]), places=6)
            self.assertTrue(np.isnan(o["tile_seetiledrain"][0]))  # fuera de {0, 1}
        finally:
            self.m.RAW = raw_antes

    def test_tiras_tiff_clasico_y_big(self):
        for nombre in ("prob.tif", "clase.tif"):
            b = (self.dir / nombre).read_bytes()
            offs, largos = self.m.tiras_tiff(b)
            self.assertEqual(len(offs), ALTO)
            self.assertTrue((largos == ANCHO * 4).all())
            # las tiras cubren un bloque continuo, aunque GDAL escriba al final las que son todo nodata
            orden = np.sort(offs)
            self.assertTrue((np.diff(orden) == ANCHO * 4).all())


class TestControles(unittest.TestCase):
    def test_controles_seetiledrain(self):
        import pandas as pd
        spec = importlib.util.spec_from_file_location("t131_lotes_process", REPO / "src/lotes/process.py")
        proc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(proc)
        vacio = pd.DataFrame({"id_lote": ["a", "a"], "drenado_canos": pd.array([1, 0], dtype="Int64"),
                              "tile_prob_seetiledrain": [np.nan, np.nan],
                              "tile_seetiledrain": pd.array([pd.NA, pd.NA], dtype="Int64")})
        self.assertIn("Sin recortes", "\n".join(proc.controles_seetiledrain(vacio)))
        d = pd.DataFrame({"id_lote": ["a"] * 4, "drenado_canos": pd.array([1, 0, 1, pd.NA], dtype="Int64"),
                          "tile_prob_seetiledrain": [0.9, 0.2, 0.4, np.nan],
                          "tile_seetiledrain": pd.array([1, 0, 0, pd.NA], dtype="Int64")})
        fila = [r for r in proc.controles_seetiledrain(d) if r.startswith("| a |")][0]
        # 75 % con prob, media 0,5, 33,3 % clase 1, 33,3 % prob >= 0,5, acuerdo con AgTile 2 de 3
        self.assertEqual(fila, "| a | 75.0 | 0.500 | 33.3 | 33.3 | 66.7 |")


if __name__ == "__main__":
    unittest.main()
