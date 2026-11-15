"""La versión de la API de POWER que va a manifest.csv sale de la respuesta, no de un texto fijo (T123).

Sin red: se reemplaza `requests.get` por una respuesta de ejemplo con el encabezado HTTP `x-app-version`, igual
al que devuelve POWER (ver docs/research/power_version.md). Todo se escribe en una carpeta temporal.

Correr:  python -X utf8 -m pytest -q tests/test_clima_version.py
"""
from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

CSV_EJEMPLO = """-BEGIN HEADER-
NASA/POWER Source Native Resolution Daily Data
Dates (month/day/year): 12/30/2025 through 12/31/2025 in LST
-END HEADER-
YEAR,DOY,T2M,PRECTOTCORR
2025,364,-3.1,0.0
2025,365,-5.2,1.3
"""


def cargar():
    spec = importlib.util.spec_from_file_location("t123_clima_download", REPO / "src/clima/download.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Encabezados(dict):
    """requests usa un dict sin distinción de mayúsculas: se imita con claves en minúscula."""

    def get(self, k, d=None):
        return super().get(k.lower(), d)


class Respuesta:
    """Lo mínimo de requests.Response que usa download.py."""

    def __init__(self, texto: str, headers: dict):
        self.text = texto
        self.content = texto.encode("utf-8")
        self.status_code = 200
        self.headers = Encabezados({k.lower(): v for k, v in headers.items()})

    def raise_for_status(self):
        pass


class VersionPower(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        raiz = Path(self._tmp.name)
        self.m = cargar()
        self.m.REPO = raiz
        self.m.RAW = raiz / "data/raw/clima/power"
        self.m.INTERIM = raiz / "data/interim/clima/power"
        self.m.MANIFEST = raiz / "manifest.csv"

    def tearDown(self):
        self._tmp.cleanup()

    def falsa(self, headers):
        def get(url, params=None, timeout=None):
            return Respuesta(CSV_EJEMPLO, headers)
        self.m.requests.get = get

    def test_version_api(self):
        self.assertEqual(self.m.version_api(Respuesta("", {"X-App-Version": "v2.10.3"})), "POWER API v2.10.3")
        self.assertEqual(self.m.version_api(Respuesta("", {})), self.m.VERSION_DESCONOCIDA)

    def test_bajar_devuelve_version_de_la_respuesta(self):
        original = self.m.requests.get
        try:
            self.falsa({"X-App-Version": "v9.99.1", "Content-Type": "text/csv"})
            fips, estado, url, version = self.m.bajar("19169", 42.0, -93.5, "20251230", "20251231")
        finally:
            self.m.requests.get = original
        self.assertEqual(estado, "bajado")
        self.assertEqual(version, "POWER API v9.99.1")
        self.assertTrue((self.m.RAW / "power_diario_19169.csv").exists())
        # Lo que main() escribe en el manifest con esa versión
        self.m.registrar([["clima", "data/raw/clima/power/power_diario_19169.csv", "NASA POWER", "p",
                           version, "2026-11-15", url]])
        with open(self.m.MANIFEST, encoding="utf-8", newline="") as f:
            filas = list(csv.DictReader(f))
        self.assertEqual(filas[0]["version"], "POWER API v9.99.1")

    def test_sin_encabezado_no_inventa_version(self):
        original = self.m.requests.get
        try:
            self.falsa({"Content-Type": "text/csv"})
            *_, version = self.m.bajar("19169", 42.0, -93.5, "20251230", "20251231")
        finally:
            self.m.requests.get = original
        self.assertEqual(version, self.m.VERSION_DESCONOCIDA)

    def test_ya_estaba_no_baja(self):
        self.m.RAW.mkdir(parents=True)
        (self.m.RAW / "power_diario_19169.csv").write_text("x", encoding="utf-8")
        self.assertEqual(self.m.bajar("19169", 42.0, -93.5, "20251230", "20251231"),
                         ("19169", "ya estaba", None, None))


if __name__ == "__main__":
    unittest.main()
