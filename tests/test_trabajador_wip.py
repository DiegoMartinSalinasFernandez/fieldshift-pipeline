"""El commit WIP del trabajador no tiene que llevarse datos (zips, data/, archivos grandes) a los PR."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import trabajador  # noqa: E402


def _git(d: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(d), *args], capture_output=True, text=True, check=True).stdout


class WipSinDatos(unittest.TestCase):
    def test_saca_datos_y_deja_codigo(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            _git(d, "init", "-q")
            (d / "docs").mkdir()
            (d / "docs" / "nota.md").write_text("hola\n", encoding="utf-8")
            (d / "data" / "releases").mkdir(parents=True)
            (d / "data" / "releases" / "x.csv").write_text("fips\n19169\n", encoding="utf-8")
            (d / "paquete.zip").write_bytes(b"PK")
            (d / "grande.bin").write_bytes(b"0" * 6_000_000)
            with mock.patch.object(trabajador, "REPO", d):
                trabajador.git("add", "-A")
                fuera = trabajador.sacar_datos_del_indice()
            en_indice = set(_git(d, "diff", "--cached", "--name-only").split())
            self.assertEqual(en_indice, {"docs/nota.md"})
            self.assertEqual(set(fuera), {"data/releases/x.csv", "paquete.zip", "grande.bin"})
            self.assertTrue((d / "paquete.zip").exists())   # quedan en disco


if __name__ == "__main__":
    unittest.main()
