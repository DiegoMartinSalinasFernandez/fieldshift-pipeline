"""Relleno de MODIS desde LP DAAC (T119), sin red.

- la diferencia CMR − PC, con una respuesta de CMR de ejemplo guardada acá (gránulos reales de MOD11A2 de 2025,
  docs/research/lst_fechas.md: A2025177 está en PC, A2025185 no; más un compuesto de 2024 que cruza el año
  y dos producciones del mismo gránulo);
- el nombre y la ruta de salida, y que process.py lea la fecha y la tesela igual que en los de PC;
- sin ~/.netrc no se rellena y download.main() no falla;
- con un HDF4 sintético (si está pyhdf): las bandas, la grilla del overview de PC y el relleno de reliability.

Correr:  python -X utf8 -m pytest -q tests/test_vegetacion_lpdaac.py
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.vegetacion import lpdaac  # noqa: E402

URL = "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/{g}/{g}.hdf"


def entrada(g: str, mb: float = 7.3) -> dict:
    return {"producer_granule_id": g + ".hdf", "granule_size": mb,
            "links": [{"rel": "http://esipfed.org/ns/fedsearch/1.1/data#", "href": URL.format(g=g)},
                      {"rel": "http://esipfed.org/ns/fedsearch/1.1/data#", "href": "s3://x/" + g + ".hdf"},
                      {"rel": "http://esipfed.org/ns/fedsearch/1.1/browse#", "href": "https://x/" + g + ".jpg"}]}


CMR_EJEMPLO = {"feed": {"entry": [
    entrada("MOD11A2.A2024361.h10v04.061.2025006040253"),  # cruza el año: no es de 2025
    entrada("MOD11A2.A2025177.h10v04.061.2025186035311"),
    entrada("MOD11A2.A2025177.h11v04.061.2025186035410"),
    entrada("MOD11A2.A2025185.h10v04.061.2025195164941"),
    entrada("MOD11A2.A2025185.h11v04.061.2025195165012"),
    entrada("MOD11A2.A2025185.h11v04.061.2025300000000"),  # reproceso: gana la producción más reciente
]}}
PC_EJEMPLO = [{"id": "MOD11A2.A2025177.h10v04.061.2025186035311"},
              {"id": "MOD11A2.A2025177.h11v04.061.2025186035410"}]


def get_falso(*_a, **_k):
    r = mock.Mock()
    r.json.return_value = CMR_EJEMPLO
    return r


class Diferencia(unittest.TestCase):
    def test_cmr_granulos(self):
        g = lpdaac.cmr_granulos("MOD11A2", [-100, 40, -95, 43], 2025, get=get_falso)
        self.assertEqual(sorted(g), [("A2025177", "h10v04"), ("A2025177", "h11v04"),
                                     ("A2025185", "h10v04"), ("A2025185", "h11v04")])
        self.assertEqual(g[("A2025185", "h11v04")]["id"], "MOD11A2.A2025185.h11v04.061.2025300000000")
        self.assertTrue(g[("A2025185", "h10v04")]["url"].startswith("https://"))

    def test_faltantes_cmr_menos_pc(self):
        cmr = lpdaac.cmr_granulos("MOD11A2", [-100, 40, -95, 43], 2025, get=get_falso)
        self.assertEqual(lpdaac.faltantes(cmr, lpdaac.pc_claves(PC_EJEMPLO)),
                         [("A2025185", "h10v04"), ("A2025185", "h11v04")])
        self.assertEqual(lpdaac.faltantes(cmr, set(cmr)), [])

    def test_faltantes_grupos_une_bbox(self):
        a, b = [-100, 40, -95, 43], [-90, 38, -85, 42]
        f = lpdaac.faltantes_grupos("MOD11A2", [(("NE",), a), (("OH",), b)], 2025, PC_EJEMPLO, get=get_falso)
        self.assertEqual([g["id"] for g, _ in f], ["MOD11A2.A2025185.h10v04.061.2025195164941",
                                                   "MOD11A2.A2025185.h11v04.061.2025300000000"])
        self.assertEqual(f[0][1], [-100, 38, -85, 43])


class Nombres(unittest.TestCase):
    def test_nombre_y_ruta(self):
        g = "MOD13Q1.A2025185.h10v04.061.2025203123456"
        self.assertEqual(lpdaac.nombre_salida(g + ".hdf"), g + ".lpdaac.tif")
        raw = Path("/tmp/raw")
        self.assertEqual(lpdaac.ruta_salida("mod13q1", g, raw), raw / "mod13q1" / "2025" / (g + ".lpdaac.tif"))

    def test_process_lee_fecha_y_tesela(self):
        spec = importlib.util.spec_from_file_location("t119_process", REPO / "src/vegetacion/process.py")
        try:
            pr = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pr)
        except ImportError as e:  # scipy u otra dependencia de process.py
            self.skipTest(str(e))
        n = lpdaac.nombre_salida("MOD11A2.A2025185.h10v04.061.2025195164941")
        self.assertEqual(str(pr.fecha_item(n)), "2025-07-04")
        self.assertEqual(pr.tesela(n), "h10v04")


class SinEarthdata(unittest.TestCase):
    def test_credenciales_sin_netrc(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(lpdaac.credenciales(Path(d) / "no_existe"))
            otro = Path(d) / "netrc"
            otro.write_text("machine otro.host login a password b\n", encoding="utf-8")
            self.assertIsNone(lpdaac.sesion_earthdata(otro))
            bien = Path(d) / "netrc2"
            bien.write_text("machine urs.earthdata.nasa.gov login usuario password clave\n", encoding="utf-8")
            s = lpdaac.sesion_earthdata(bien)
            self.assertIsNotNone(s)
            self.assertNotIn("clave", repr(s))

    def test_download_main_sin_netrc_no_falla(self):
        spec = importlib.util.spec_from_file_location("t119_download", REPO / "src/vegetacion/download.py")
        dl = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dl)
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            token = mock.Mock()
            token.json.return_value = {"token": "t"}
            rellenar = mock.Mock(side_effect=AssertionError("sin netrc no se rellena"))
            with mock.patch.object(dl, "RAW", tmp / "raw"), mock.patch.object(dl, "INTERIM", tmp / "interim"), \
                    mock.patch.object(dl, "grupos_bbox", return_value=[(("NE",), [-100, 40, -95, 43])]), \
                    mock.patch.object(dl, "buscar", return_value=[{"id": "MOD11A2.A2025177.h10v04.061.1"}]), \
                    mock.patch.object(dl, "bajar_item", return_value="ok"), \
                    mock.patch.object(dl, "registrar_manifest"), \
                    mock.patch.object(dl, "rellenar_lpdaac", rellenar), \
                    mock.patch.object(dl.lpdaac, "credenciales", return_value=None), \
                    mock.patch.object(dl.requests, "get", return_value=token), \
                    mock.patch.object(sys, "argv", ["download.py", "mod11a2", "2025", "2025"]):
                dl.main()  # no levanta SystemExit
                log = (tmp / "interim" / "download.log").read_text(encoding="utf-8")
            self.assertIn("sin login de Earthdata", log)
            rellenar.assert_not_called()


class Conversion(unittest.TestCase):
    """HDF4 sintético de una tesela entera: la grilla de salida tiene que ser la del overview de PC."""

    def setUp(self):
        try:
            from pyhdf.SD import SD, SDC  # noqa: F401
        except ImportError:
            self.skipTest("pyhdf no instalado")
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def hdf(self, capas: dict) -> Path:
        from pyhdf.SD import SD, SDC
        p = self.tmp / "g.hdf"
        sd = SD(str(p), SDC.WRITE | SDC.CREATE)
        tipos = {np.dtype("int16"): SDC.INT16, np.dtype("uint16"): SDC.UINT16,
                 np.dtype("int8"): SDC.INT8, np.dtype("uint8"): SDC.UINT8}
        for nombre, (a, fill) in capas.items():
            ds = sd.create(nombre, tipos[a.dtype], a.shape)
            ds[:] = a
            if fill is not None:
                ds.attr("_FillValue").set(tipos[a.dtype], fill)
            ds.endaccess()
        sd.end()
        return p

    def test_mod11a2_overview0(self):
        import rasterio
        n = 1200
        lst = np.full((n, n), 15000, np.uint16)
        lst[:10, :10] = 0
        qc = np.zeros((n, n), np.uint8)
        p = self.hdf({"LST_Day_1km": (lst, 0), "LST_Night_1km": (lst, 0), "QC_Day": (qc, None), "QC_Night": (qc, None)})
        g = "MOD11A2.A2025185.h11v04.061.2025195165012"
        dest = lpdaac.ruta_salida("mod11a2", g, self.tmp / "raw")
        with mock.patch.object(lpdaac, "INTERIM", self.tmp / "interim"):
            r = lpdaac.convertir(p, "mod11a2", 0, g, [-180, -89, 180, 89], dest)
        self.assertEqual(r, "ok")
        with rasterio.open(dest) as s:
            self.assertEqual(s.count, 4)
            self.assertEqual(s.shape, (600, 600))
            self.assertEqual(s.descriptions[:2], ("LST_Day_1km", "LST_Night_1km"))
            # transform del overview 0 del COG de PC de h11v04 (leído de PC el 2026-11-15)
            np.testing.assert_allclose(tuple(s.transform)[:6],
                                       (1853.2508662783323, 0, -7783653.638366, 0, -1853.250866278334, 5559752.598833),
                                       atol=1e-2)
            a = s.read(1)
            self.assertEqual(a[300, 300], 15000)
            self.assertEqual(a[0, 0], 0)  # sin dato sigue sin dato
            self.assertEqual(s.tags()["fuente"], lpdaac.FUENTE)

    def test_mod13q1_overview1_y_reliability(self):
        import rasterio
        n = 4800
        ndvi = np.full((n, n), 7000, np.int16)
        rel = np.zeros((n, n), np.int8)
        rel[:40, :40] = -1
        p = self.hdf({"250m 16 days NDVI": (ndvi, -3000), "250m 16 days EVI": (ndvi, -3000),
                      "250m 16 days pixel reliability": (rel, -1)})
        g = "MOD13Q1.A2025185.h10v04.061.2025203123456"
        dest = lpdaac.ruta_salida("mod13q1", g, self.tmp / "raw")
        with mock.patch.object(lpdaac, "INTERIM", self.tmp / "interim"):
            lpdaac.convertir(p, "mod13q1", 1, g, [-180, -89, 180, 89], dest)
        with rasterio.open(dest) as s:
            self.assertEqual((s.count, s.shape), (3, (1200, 1200)))
            self.assertAlmostEqual(s.transform.a, 926.6254330558338, places=4)
            b = s.read()
            self.assertEqual(b[0, 600, 600], 7000)
            self.assertEqual(b[2, 0, 0], 255)  # relleno -1 (int8) -> 255, como en los COG de PC
            self.assertEqual(b[2, 600, 600], 0)

    def test_fuera_del_bbox(self):
        n = 1200
        lst = np.full((n, n), 15000, np.uint16)
        qc = np.zeros((n, n), np.uint8)
        p = self.hdf({"LST_Day_1km": (lst, 0), "LST_Night_1km": (lst, 0), "QC_Day": (qc, None), "QC_Night": (qc, None)})
        g = "MOD11A2.A2025185.h11v04.061.2025195165012"
        dest = lpdaac.ruta_salida("mod11a2", g, self.tmp / "raw")
        self.assertEqual(lpdaac.convertir(p, "mod11a2", 0, g, [10, 10, 11, 11], dest), "fuera")
        self.assertFalse(dest.exists())


class Manifest(unittest.TestCase):
    def test_una_fila_por_archivo(self):
        with tempfile.TemporaryDirectory() as d:
            raw = Path(d) / "raw"
            f = lpdaac.ruta_salida("mod11a2", "MOD11A2.A2025185.h10v04.061.2025195164941", raw)
            f.parent.mkdir(parents=True)
            f.write_bytes(b"x")
            (f.parent / "MOD11A2.A2025177.h10v04.061.2025186035311.tif").write_bytes(b"x")  # de PC: no va
            man = Path(d) / "manifest.csv"
            self.assertEqual(lpdaac.registrar_manifest("mod11a2", "MOD11A2", raw, man), 1)
            self.assertEqual(lpdaac.registrar_manifest("mod11a2", "MOD11A2", raw, man), 0)  # idempotente
            txt = man.read_text(encoding="utf-8")
            self.assertIn("LP DAAC", txt)
            self.assertIn("granulo=MOD11A2.A2025185.h10v04.061.2025195164941.hdf", txt)


if __name__ == "__main__":
    unittest.main()
