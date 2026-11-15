"""Las funciones que registran en manifest.csv no fallan en una máquina nueva, sin manifest.csv (T021).

Cada función se llama en una carpeta temporal vacía (sin manifest.csv) con un archivo chico inventado, sin bajar
datos. Después se controla que el manifest tenga el encabezado de CLAUDE.md §7 y una fila para ese archivo.

Correr:  python -X utf8 -m unittest tests/test_manifest_nuevo.py   (o con pytest, si está instalado)
"""
from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
CAMPOS = ["paquete", "archivo", "fuente", "producto", "version", "fecha_descarga", "consulta_o_url"]


def cargar(rel: str):
    nombre = "t021_" + rel.replace("/", "_").removesuffix(".py")
    spec = importlib.util.spec_from_file_location(nombre, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def chico(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x")
    return p


class ManifestNuevo(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        self.man = self.raiz / "manifest.csv"

    def tearDown(self):
        self._tmp.cleanup()

    def controlar(self, *archivos: Path):
        with open(self.man, encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            self.assertEqual(r.fieldnames, CAMPOS)
            filas = list(r)
        for a in archivos:
            rel = a.relative_to(self.raiz).as_posix()
            self.assertEqual(sum(f["archivo"] == rel for f in filas), 1, rel)

    def test_cultivos(self):
        m = cargar("src/cultivos/download.py")
        m.REPO, m.MANIFEST = self.raiz, self.man
        a = chico(self.raiz / "data/raw/cultivos/nass/qs.crops_20250101.txt.gz")
        m.registrar(a, "https://ejemplo/qs")
        b = chico(self.raiz / "data/raw/cultivos/cdl_teselas/2020_30m_cdls_x.tif")
        self.man.unlink()
        m.registrar_tesela(b, "https://ejemplo/tesela")
        self.controlar(b)

    def test_clima(self):
        m = cargar("src/clima/download.py")
        m.MANIFEST = self.man
        a = chico(self.raiz / "data/raw/clima/power_diario_19001.csv")
        m.registrar([["clima", a.relative_to(self.raiz).as_posix(), "NASA POWER", "p", "v", "2026-01-01", "u"]])
        self.controlar(a)

    def test_suelo_terreno(self):
        m = cargar("src/suelo_terreno/download.py")
        m.REPO, m.MANIFEST = self.raiz, self.man
        a = chico(self.raiz / "data/raw/suelo_terreno/sda/x.csv")
        m.registrar(a, next(iter(m.CONSULTAS)), "IA")
        b = chico(self.raiz / "data/raw/suelo_terreno/nasadem/n42w094.tif")
        self.man.unlink()
        m.registrar_dem(b, "n42w094")
        self.controlar(b)

    def test_ecostress(self):
        m = cargar("src/ecostress/download.py")
        m.REPO, m.MANIFEST = self.raiz, self.man
        m.bboxes_cmr = lambda margen=0.1: ["-96,40,-95,41"]
        a = chico(self.raiz / "data/raw/ecostress/ecostress_2020-06.csv")
        m.registrar(a, "2020-06")
        self.controlar(a)

    def test_agua(self):
        m = cargar("src/agua/download.py")
        m.REPO, m.MANIFEST = self.raiz, self.man
        m.RAW, m.SMAP_RAW = self.raiz / "data/raw/agua/grace", self.raiz / "data/raw/agua/smap"
        a = chico(m.SMAP_RAW / "2020/SMAP-9KM-DAILY-SUB_2020.06.01_000000_FIPS_19001.tif")
        m.registrar_manifest_smap()
        self.controlar(a)
        self.man.unlink()
        b = chico(m.RAW / "GRACEDADM_CLSM0125US_7D.A20200601.030.nc4")
        m.registrar_manifest()
        self.controlar(b)

    def test_validacion(self):
        m = cargar("src/validacion/download.py")
        m.RAIZ = self.raiz
        a = chico(self.raiz / "data/raw/validacion/prism/ppt/prism_ppt_2020.zip")
        m.tareas_prism = lambda: [("https://ejemplo/prism", a)]
        m.tareas_cocorahs = lambda: []
        m.manifest()
        self.controlar(a)

    def test_nldas(self):
        for rel in ("src/nldas/download.py", "src/vegetacion/download_nldas.py"):
            with self.subTest(rel):
                m = cargar(rel)
                m.REPO, m.RAW = self.raiz, self.raiz / "data/raw" / rel
                a = chico(m.RAW / "2020" / m.nombre(2020, 6))
                if self.man.exists():
                    self.man.unlink()
                m.registrar_manifest({"zona": [-97.0, 40.0, -89.0, 44.0]})  # desde T023: un bbox por grupo
                self.controlar(a)

    def test_vegetacion(self):
        m = cargar("src/vegetacion/download.py")
        m.REPO, m.RAW = self.raiz, self.raiz / "data/raw/vegetacion"
        a = chico(m.RAW / "mod13q1/2020/MOD13Q1.A2020161.h10v04.061.tif")
        m.registrar_manifest("mod13q1")
        self.controlar(a)

    def test_teledeteccion(self):
        m = cargar("src/teledeteccion/download.py")
        m.REPO, m.RAW, m.INTERIM = self.raiz, self.raiz / "data/raw/landsat", self.raiz / "data/interim"
        m.INTERIM.mkdir(parents=True)
        a = m.RAW / "2020/LC08_L2SP_026031_20200601_02_T1.npz"
        a.parent.mkdir(parents=True)
        np.savez(a, x=np.zeros((len(m.BANDAS), 1, 1)))
        m.registrar_manifest(2020, {})
        self.controlar(a)

    def test_paisaje(self):
        m = cargar("src/paisaje/download.py")
        m.ROOT = self.raiz
        a = chico(self.raiz / "data/raw/paisaje/x.tif")
        m.upsert_manifest([["paisaje", a.relative_to(self.raiz).as_posix(), "f", "p", "v", "2026-01-01", "u"]])
        self.controlar(a)

    def test_economia_y_lotes(self):
        for rel, paquete in (("src/economia/download.py", "economia"), ("src/lotes/download.py", "lotes")):
            with self.subTest(rel):
                m = cargar(rel)
                m.MANIFEST = self.man
                if self.man.exists():
                    self.man.unlink()
                a = chico(self.raiz / f"data/raw/{paquete}/x.csv")
                m.upsert_manifest([dict(zip(CAMPOS, [paquete, a.relative_to(self.raiz).as_posix(), "f", "p", "v",
                                                     "2026-01-01", "u"]))])
                self.controlar(a)

    def test_manifest_existente_no_cambia(self):
        """Con un manifest que ya tiene filas, el encabezado no se vuelve a escribir y las filas quedan igual."""
        m = cargar("src/lotes/download.py")
        m.MANIFEST = self.man
        previo = ",".join(CAMPOS) + "\nbase,data/raw/base/y.zip,f,p,v,2025-01-01,u\n"
        self.man.write_text(previo, encoding="utf-8")
        m.asegurar_manifest(self.man)
        self.assertEqual(self.man.read_text(encoding="utf-8"), previo)


if __name__ == "__main__":
    unittest.main()
