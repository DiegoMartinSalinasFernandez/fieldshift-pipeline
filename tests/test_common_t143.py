"""T143: `asegurar_manifest()` y `zona_texto` en `src/common/`, sin efecto en los datos.

- La función común escribe exactamente lo mismo que la copia que había en cada `download.py` (copiada abajo tal
  cual): manifest nuevo, vacío y con filas.
- Ningún `download.py` vuelve a definir su propia copia, y todos usan la de `src/common/`.
- `src/zona_texto.py` sigue andando como alias de `src/common/zona_texto.py`.

Correr:  python -X utf8 -m unittest tests/test_common_t143.py   (sin red)
"""
from __future__ import annotations

import ast
import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.common.manifest import CAMPOS_MANIFEST, asegurar_manifest  # noqa: E402

DOWNLOADS = ["src/agua/download.py", "src/clima/download.py", "src/cultivos/download.py",
             "src/economia/download.py", "src/ecostress/download.py", "src/lotes/download.py",
             "src/nldas/download.py", "src/paisaje/download.py", "src/suelo_terreno/download.py",
             "src/teledeteccion/download.py", "src/validacion/download.py", "src/vegetacion/download.py",
             "src/vegetacion/download_nldas.py"]


def asegurar_manifest_vieja(man: Path) -> None:
    """Copia literal de la versión que estaba repetida en los 13 download.py antes de T143."""
    if not man.exists() or man.stat().st_size == 0:
        man.write_text("paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n", encoding="utf-8")


class AsegurarManifestIgual(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def comparar(self, previo: bytes | None):
        salidas = []
        for nombre, fn in (("vieja", asegurar_manifest_vieja), ("nueva", asegurar_manifest)):
            man = self.dir / nombre / "manifest.csv"
            man.parent.mkdir()
            if previo is not None:
                man.write_bytes(previo)
            fn(man)
            salidas.append(man.read_bytes())
        self.assertEqual(salidas[0], salidas[1])
        return salidas[1]

    def test_sin_manifest(self):
        b = self.comparar(None)
        with open(self.dir / "nueva" / "manifest.csv", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            self.assertEqual(r.fieldnames, CAMPOS_MANIFEST)
            self.assertEqual(list(r), [])
        self.assertTrue(b.endswith(b"\n") and b"\r" not in b)

    def test_manifest_vacio(self):
        self.comparar(b"")

    def test_manifest_con_filas_lf_y_crlf(self):
        for eol in (b"\n", b"\r\n"):
            with self.subTest(eol=eol):
                previo = eol.join([",".join(CAMPOS_MANIFEST).encode(),
                                   "base,data/raw/base/y.zip,f,p,v,2025-01-01,\"u, con coma\"".encode(),
                                   "clima,data/raw/clima/ñ.csv,f,p,v,2025-01-02,u".encode("utf-8"), b""])
                self.assertEqual(self.comparar(previo), previo)
                for d in ("vieja", "nueva"):
                    (self.dir / d / "manifest.csv").unlink()
                    (self.dir / d).rmdir()

    def test_acepta_str(self):
        man = self.dir / "manifest.csv"
        asegurar_manifest(str(man))
        self.assertEqual(man.read_text(encoding="utf-8"), ",".join(CAMPOS_MANIFEST) + "\n")


class DownloadsUsanLaComun(unittest.TestCase):
    def test_sin_copias_locales(self):
        con_def = []
        for p in (REPO / "src").rglob("*.py"):
            if "common" in p.parts:
                continue
            arbol = ast.parse(p.read_text(encoding="utf-8"))
            if any(isinstance(n, ast.FunctionDef) and n.name == "asegurar_manifest" for n in ast.walk(arbol)):
                con_def.append(p.relative_to(REPO).as_posix())
        self.assertEqual(con_def, [])

    def test_cada_download_importa_la_comun(self):
        for rel in DOWNLOADS:
            with self.subTest(rel):
                arbol = ast.parse((REPO / rel).read_text(encoding="utf-8"))
                imps = [n for n in arbol.body if isinstance(n, ast.ImportFrom) and n.module == "src.common.manifest"
                        and any(a.name == "asegurar_manifest" for a in n.names)]
                self.assertEqual(len(imps), 1)

    def test_modulo_cargado_usa_la_comun(self):
        for rel in ("src/economia/download.py", "src/lotes/download.py"):  # los dos sin otras dependencias pesadas
            with self.subTest(rel):
                spec = importlib.util.spec_from_file_location("t143_" + rel.replace("/", "_")[:-3], REPO / rel)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self.assertIs(mod.asegurar_manifest, asegurar_manifest)


class ZonaTextoAlias(unittest.TestCase):
    def test_alias_es_el_mismo_codigo(self):
        import src.common.zona_texto as nuevo
        import src.zona_texto as viejo
        for nombre in ("unir", "lista_estados", "n_estados", "n_condados"):
            self.assertIs(getattr(viejo, nombre), getattr(nuevo, nombre))

    def test_unir(self):
        from src.common.zona_texto import unir
        self.assertEqual(unir([]), "")
        self.assertEqual(unir(["KS"]), "KS")
        self.assertEqual(unir(["NE", "KS"]), "NE y KS")
        self.assertEqual(unir(["IA", "IL", "IN"]), "IA, IL e IN")

    def test_nadie_importa_el_alias(self):
        usan = [p.relative_to(REPO).as_posix() for d in ("src", "scripts", "tests") for p in (REPO / d).rglob("*.py")
                if "from src.zona_texto import" in p.read_text(encoding="utf-8") and p != Path(__file__).resolve() and p != REPO / "src" / "zona_texto.py"]
        self.assertEqual(usan, [])


if __name__ == "__main__":
    unittest.main()
