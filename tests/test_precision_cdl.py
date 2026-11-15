"""Pruebas sin red de src/cultivos/precision_cdl.py (T133) y del agregado al zip de base de entregar.py.

El HTML es un pedacito real de los metadatos FGDC de Ohio 2015
(https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-oh15, bajado el 2026-11-15).

Correr:  python -X utf8 -m pytest -q tests/test_precision_cdl.py
"""
from __future__ import annotations

import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src" / "cultivos"))
sys.path.insert(0, str(REPO / "tests"))
import precision_cdl as pc  # noqa: E402
from test_entregar import EntornoEntregar  # noqa: E402

HTML_OH15 = """<html><body><div>
<pre tabindex="0" role="region" aria-label="Preformatted data">
USDA, National Agricultural Statistics Service, 2015 Ohio Cropland Data Layer
STATEWIDE AGRICULTURAL ACCURACY REPORT

Crop-specific covers only  *Correct  Accuracy   Error   Kappa
-------------------------   -------  --------  ------   -----
OVERALL ACCURACY**          562,206     94.0%    6.0%   0.895


Cover                    Attribute  *Correct  Producer's  Omission            User's  Commission  Cond'l
Type                          Code    Pixels   Accuracy     Error   Kappa   Accuracy      Error    Kappa
----                          ----    ------   --------     -----   -----   --------      -----    -----
Corn                             1    218380     96.60%     3.40%   0.956     97.19%      2.81%    0.964
Sorghum                          4         3      4.11%    95.89%   0.041     23.08%     76.92%    0.231
Soybeans                         5    309521     97.77%     2.23%   0.967     97.03%      2.97%    0.956
Sunflower                        6         0      0.00%   100.00%   0.000       n/a        n/a      n/a
Millet                          29         0       n/a       n/a     n/a       0.00%    100.00%    0.000
</pre></div></body></html>
"""

ENCABEZADO = ("estado,anio,cultivo,codigo_cdl,px_correctos,precision_productor_pct,precision_usuario_pct,"
              "global_cultivos_fsa_pct,kappa_global_fsa,fuente\n")
CSV_A = ENCABEZADO + ("OH,2015,maiz,1,218380,96.6,97.19,94.0,0.895,metadatos_fgdc_html\n"
                      "KS,2024,soja,5,1000,88.1,90.2,79.8,0.75,accuracy_assessments_xlsx\n"
                      "OH,2017,avena,28,,,,84.2,0.8,metadatos_fgdc_html\n")
CSV_B = ENCABEZADO + "KY,2010,alfalfa,36,0,0.0,,70.4,0.6,metadatos_fgdc_html\n"


class TestLeerHtml(unittest.TestCase):
    """El extractor de research lee el HTML local sin bajar nada."""

    def test_oh_2015(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "metadata-oh15.html"
            ruta.write_text(HTML_OH15, encoding="utf-8")
            glob, filas = pc.leer_html(ruta, "OH", 2015, {1: "maiz", 5: "soja", 6: "girasol", 29: "mijo"})
        self.assertEqual(glob, (94.0, 0.895))
        self.assertEqual(filas[1], (218380, 96.6, 97.19))
        self.assertEqual(filas[5], (309521, 97.77, 97.03))
        self.assertEqual(filas[6], (0, 0.0, None))      # usuario "n/a" -> vacío, nunca 0
        self.assertNotIn(4, filas)                      # sorgo no se pidió
        self.assertNotIn(29, filas)                     # productor "n/a": el extractor no la toma

    def test_coincide_con_el_csv_de_research(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "metadata-oh15.html"
            ruta.write_text(HTML_OH15, encoding="utf-8")
            _, filas = pc.leer_html(ruta, "OH", 2015, {1: "maiz", 5: "soja"})
        ref = pc.armar()
        oh = ref[(ref["estado"] == "OH") & (ref["anio"] == 2015)].set_index("clase_cdl")
        for clase in (1, 5):
            px, prod, usu = filas[clase]
            self.assertEqual(oh.loc[clase, "px_correctos_validacion"], px)
            self.assertAlmostEqual(oh.loc[clase, "exactitud_productor_pct"], prod)
            self.assertAlmostEqual(oh.loc[clase, "exactitud_usuario_pct"], usu)

    def test_nombre_que_no_coincide_corta(self):
        with self.assertRaises(ValueError):
            pc.leer_html(Path("/no/existe/metadata-ks15.html"), "OH", 2015, {1: "maiz"})


class TestArmar(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        (self.d / "a.csv").write_text(CSV_A, encoding="utf-8")
        (self.d / "b.csv").write_text(CSV_B, encoding="utf-8")
        self.fuentes = [("a.csv", "a.py"), ("b.csv", "b.py")]

    def tearDown(self):
        self.tmp.cleanup()

    def test_columnas_claves_y_metodo(self):
        df = pc.armar(self.d, self.fuentes)
        self.assertEqual(list(df.columns), pc.COLUMNAS)
        self.assertEqual(list(df.columns[:3]), ["fips_estado", "anio", "clase_cdl"])
        fila = df[(df["estado"] == "OH") & (df["anio"] == 2015)].iloc[0]
        self.assertEqual(fila["fips_estado"], "39")
        self.assertEqual(fila["nombre"], "maiz")
        self.assertEqual(fila["metodo_validacion"], "buffer_30m")
        self.assertEqual(df.loc[df["estado"] == "KS", "metodo_validacion"].item(), "muestreo_2024")
        self.assertEqual(df.loc[df["anio"] == 2017, "metodo_validacion"].item(), "sin_buffer")
        self.assertEqual(df.loc[df["estado"] == "KY", "fips_estado"].item(), "21")

    def test_vacios_quedan_vacios(self):
        destino = pc.escribir(pc.armar(self.d, self.fuentes), self.d / "out" / "cdl_precision.csv")
        texto = destino.read_text(encoding="utf-8")
        self.assertIn("39,2017,28,OH,avena,,,,84.2,0.8,sin_buffer,metadatos_fgdc_html", texto)
        self.assertIn("21,2010,36,KY,alfalfa,0.0,,0,70.4,0.6,buffer_30m,metadatos_fgdc_html", texto)
        self.assertNotIn("\r", texto)

    def test_clave_repetida_corta(self):
        (self.d / "b.csv").write_text(ENCABEZADO + CSV_A.splitlines()[1] + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            pc.armar(self.d, self.fuentes)

    def test_porcentaje_fuera_de_rango_corta(self):
        (self.d / "b.csv").write_text(CSV_B.replace(",0.0,,", ",120.0,,"), encoding="utf-8")
        with self.assertRaises(ValueError):
            pc.armar(self.d, self.fuentes)

    def test_falta_un_csv_corta(self):
        with self.assertRaises(FileNotFoundError):
            pc.armar(self.d, self.fuentes + [("c.csv", "c.py")])

    def test_de_estados(self):
        df = pc.de_estados(pc.armar(self.d, self.fuentes), ["oh", "KY"])
        self.assertEqual(set(df["estado"]), {"OH", "KY"})

    def test_rehacer_no_acepta_dir_en_el_repo(self):
        with self.assertRaises(SystemExit):
            pc.rehacer(REPO / "data" / "tmp_cdl")


class TestTablaDelRepo(unittest.TestCase):
    """Los CSV de docs/research/ (versionados) arman la tabla sin errores."""

    def test_trece_estados(self):
        df = pc.armar()
        self.assertEqual(df["estado"].nunique(), 13)
        self.assertEqual((df["anio"].min(), df["anio"].max()), (2008, 2025))
        self.assertFalse(df.duplicated(pc.CLAVES).any())
        for st in ("OH", "NE", "MN", "KS", "IA", "IL", "IN"):
            sub = df[(df["estado"] == st) & df["clase_cdl"].isin([1, 5])]
            self.assertEqual(len(sub), 36, st)                         # 18 años x maíz y soja
            self.assertTrue(sub["exactitud_productor_pct"].notna().all(), st)


class TestZipDeBase(EntornoEntregar):

    def setUp(self):
        super().setUp()
        from test_entregar import escribir_gpkg
        escribir_gpkg(self.repo / "data/reference/condados.gpkg", [("39001", "OH"), ("20005", "KS")])

    def test_con_precision_va_filtrada(self):
        self.escribir("data/reference/cdl_precision.csv",
                      "fips_estado,anio,clase_cdl,estado,nombre,exactitud_productor_pct\n"
                      "39,2015,1,OH,maiz,96.6\n20,2015,5,KS,soja,\n19,2015,1,IA,maiz,97.0\n")
        self.correr("base")
        with zipfile.ZipFile(self.zip_de("base")) as zf:
            prec = pd.read_csv(io.BytesIO(zf.read("data/reference/cdl_precision.csv")), dtype=str,
                               keep_default_na=False)
            readme = zf.read("README.md").decode("utf-8")
        self.assertEqual(sorted(prec["estado"]), ["KS", "OH"])
        self.assertEqual(prec.loc[prec["estado"] == "KS", "exactitud_productor_pct"].item(), "")
        self.assertEqual(prec.loc[prec["estado"] == "OH", "fips_estado"].item(), "39")
        self.assertIn("cdl_precision.csv", readme)
        self.assertIn("2 rows", readme)

    def test_sin_precision_no_cambia(self):
        self.correr("base")
        with zipfile.ZipFile(self.zip_de("base")) as zf:
            self.assertNotIn("data/reference/cdl_precision.csv", zf.namelist())
            self.assertNotIn("cdl_precision", zf.read("README.md").decode("utf-8"))

    def test_sin_columna_estado_corta(self):
        self.escribir("data/reference/cdl_precision.csv", "fips_estado,anio\n39,2015\n")
        with self.assertRaises(SystemExit):
            self.correr("base")


if __name__ == "__main__":
    unittest.main()
