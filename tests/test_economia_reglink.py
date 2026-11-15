"""Prueba de la lectura de reglink.xls en src/economia/process.py (T071).

reglink.xls de ERS trae a Oglala Lakota (SD) con el código viejo 46113 (Shannon County); el Census usa
46102 desde 2015. Se usa un reglink inventado de dos filas, sin datos reales.

Correr:  python -X utf8 -m unittest tests/test_economia_reglink.py   (o con pytest)
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def cargar():
    spec = importlib.util.spec_from_file_location("t071_economia_process", REPO / "src/economia/process.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


proc = cargar()

# Dos filas como las de reglink.xls (FIPS numérico, código de región 1 a 9) más un encabezado de texto.
REGLINK = pd.DataFrame({"fips": ["County FIPS", 46113, 46011], "codigo": ["Region", 3, 1]})


class TestReglink(unittest.TestCase):
    def test_shannon_pasa_a_oglala_lakota(self):
        r = proc.limpiar_reglink(REGLINK.copy())
        self.assertEqual(list(r.columns), ["fips_condado", "region_ers"])
        self.assertEqual(dict(zip(r["fips_condado"], r["region_ers"])),
                         {"46102": "Northern Great Plains", "46011": "Heartland"})
        self.assertNotIn("46113", set(r["fips_condado"]))

    def test_si_ya_trae_el_codigo_nuevo_no_duplica(self):
        r = pd.DataFrame({"fips": [46113, 46102], "codigo": [3, 3]})
        out = proc.limpiar_reglink(r)
        self.assertEqual(list(out["fips_condado"]), ["46102"])

    def test_regiones_condado_lee_la_planilla(self):
        with tempfile.TemporaryDirectory() as d:
            falso = Path(d) / "reglink.xls"
            falso.write_bytes(b"")  # solo tiene que existir: read_excel se reemplaza
            with mock.patch.object(proc, "REGLINK", falso), \
                    mock.patch.object(proc.pd, "read_excel", return_value=REGLINK.copy()):
                r = proc.regiones_condado()
        self.assertEqual(sorted(r["fips_condado"]), ["46011", "46102"])


if __name__ == "__main__":
    unittest.main()
