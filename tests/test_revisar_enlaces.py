"""Pruebas sin red de scripts/revisar_enlaces.py (tarea T109): extracción y enlaces relativos.

Arman un repo chico en un directorio temporal; no llaman a curl (con_red=False) ni a git.

Correr:  python -X utf8 -m unittest tests/test_revisar_enlaces.py   (o con pytest)
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("revisar_enlaces", REPO / "scripts" / "revisar_enlaces.py")
re_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = re_mod  # @dataclass lo busca en sys.modules
_spec.loader.exec_module(re_mod)

MD_DEMO = """# Demo

Ver [`limitations.md`](limitations.md) y [la página](project_page.md#quick-links).
![mapa](fig/mapa.png)
![falta](fig/no_esta.png)
<img src="fig/mapa.png" width="300">
[roto](../datasets/no_existe.md)
[carpeta](../datasets)
[ancla](#arriba) [mail](mailto:x@example.org)
[espacio](fig/con%20espacio.png)

Código inline que no cuenta: `[x](no_cuenta.md)` y `https://no.cuenta.example`.

```
[dentro de bloque](tampoco.md)
```

Externa: [NASA](https://doi.org/10.5067/X) y suelta https://quickstats.nass.usda.gov.
Release: [zip](https://github.com/o/r/releases/download/v1/a.zip)
"""


class TestExtraer(unittest.TestCase):
    def test_saltea_codigo_y_toma_imagenes(self):
        enlaces = re_mod.extraer_enlaces(MD_DEMO, "docs/demo/x.md")
        destinos = [e.destino for e in enlaces]
        self.assertIn("limitations.md", destinos)
        self.assertIn("project_page.md#quick-links", destinos)
        self.assertIn("https://quickstats.nass.usda.gov", destinos)  # sin el punto final
        self.assertNotIn("no_cuenta.md", destinos)
        self.assertNotIn("tampoco.md", destinos)
        self.assertFalse(any("no.cuenta" in d for d in destinos))
        imagenes = [e.destino for e in enlaces if e.imagen]
        self.assertEqual(imagenes, ["fig/mapa.png", "fig/no_esta.png", "fig/mapa.png"])
        self.assertEqual(destinos.count("https://doi.org/10.5067/X"), 1)  # no se cuenta dos veces

    def test_es_release(self):
        self.assertTrue(re_mod.es_release("https://github.com/o/r/releases/download/v1/a.zip"))
        self.assertTrue(re_mod.es_release("https://github.com/o/r/releases/tag/datos-oh-ne-mn"))
        self.assertTrue(re_mod.es_release("https://github.com/o/r/releases"))
        self.assertFalse(re_mod.es_release("https://github.com/o/r/blob/main/README.md"))
        self.assertFalse(re_mod.es_release("https://doi.org/10.5067/X"))


class TestRelativos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name).resolve()
        demo = self.repo / "docs" / "demo"
        (demo / "fig").mkdir(parents=True)
        (self.repo / "docs" / "datasets").mkdir()
        (demo / "limitations.md").write_text("# L\n", encoding="utf-8")
        (demo / "project_page.md").write_text("# P\n", encoding="utf-8")
        (demo / "fig" / "mapa.png").write_bytes(b"\x89PNG")
        (demo / "fig" / "con espacio.png").write_bytes(b"\x89PNG")
        (demo / "x.md").write_text(MD_DEMO, encoding="utf-8")
        (self.repo / "README.md").write_text(
            "[demo](docs/demo/x.md) [rel](../../releases) [falta](docs/falta.md)\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_sin_red_solo_relativos(self):
        res = re_mod.revisar(re_mod.archivos_por_defecto(self.repo), repo=self.repo, con_red=False,
                             base_github="https://github.com/o/r")
        self.assertTrue(all(r.tipo == "relativo" for r in res))
        rotos = sorted((r.enlace.archivo, r.enlace.destino) for r in res if not r.ok)
        self.assertEqual(rotos, [
            ("README.md", "docs/falta.md"),
            ("docs/demo/x.md", "../datasets/no_existe.md"),
            ("docs/demo/x.md", "fig/no_esta.png"),
        ])
        buenos = {r.enlace.destino for r in res if r.ok}
        self.assertTrue({"limitations.md", "project_page.md#quick-links", "fig/mapa.png", "../datasets",
                         "fig/con%20espacio.png", "docs/demo/x.md"} <= buenos)

    def test_ruta_github_fuera_del_repo(self):
        e = re_mod.Enlace("README.md", 1, "../../releases", False)
        self.assertEqual(re_mod.clasificar(e, self.repo, "https://github.com/o/r"),
                         ("release", "https://github.com/o/r/releases"))
        e2 = re_mod.Enlace("docs/demo/x.md", 1, "../../../../releases/tag/v1", False)
        self.assertEqual(re_mod.clasificar(e2, self.repo, "https://github.com/o/r"),
                         ("release", "https://github.com/o/r/releases/tag/v1"))
        # sin remoto conocido igual es de GitHub (con red, curl falla y se informa)
        self.assertEqual(re_mod.clasificar(e, self.repo, None)[0], "release")
        # un ../ de más que no es ruta de GitHub queda como relativo roto
        e3 = re_mod.Enlace("README.md", 1, "../otro_repo/README.md", False)
        self.assertEqual(re_mod.clasificar(e3, self.repo, "https://github.com/o/r")[0], "relativo")

    def test_paginas_reales_sin_relativos_rotos(self):
        res = re_mod.revisar(re_mod.archivos_por_defecto(), con_red=False)
        rotos = [f"{r.enlace.archivo}:{r.enlace.linea} {r.enlace.destino}" for r in res if not r.ok]
        self.assertEqual(rotos, [])


if __name__ == "__main__":
    unittest.main()
