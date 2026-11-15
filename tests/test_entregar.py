"""Prueba de scripts/entregar.py en modo --solo-zip, en una carpeta temporal con datos inventados.

Nunca sube nada: `subir` se reemplaza por una función que hace fallar la prueba si alguien la llama, y
`REPO`, `PROC` y `SALIDA` del módulo apuntan a la carpeta temporal (el script no se modifica).

Correr:  python -X utf8 -m unittest tests/test_entregar.py   (o con pytest, si está instalado)
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import entregar as en  # noqa: E402
import unir_estados as ue  # noqa: E402

# Condados inventados de Ohio (39) y Kansas (20), con ceros a la izquierda.
FIPS = ["39001", "39003", "20005"]
CONDADOS = "fips,estado,condado,lat_centroide,lon_centroide,area_km2\n" + "".join(
    f"{f},XX,C{f},40.0,-90.0,1000.0\n" for f in FIPS)
ANIOS = ("anio,inicio_temporada,fin_temporada,inicio_invierno_previo,fin_invierno_previo\n"
         "2020,2020-04-01,2020-09-30,2019-11-01,2020-03-31\n")
MANIFEST = ("paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n"
            "clima,data/raw/clima/a.json,NASA,POWER,v2,2026-11-15,https://power.example/a\n"
            "cultivos,data/raw/cultivos/b.gz,USDA NASS,Quick Stats,1,2026-11-15,https://nass.example/b\n"
            "clima,data/raw/clima/c.nc4,NASA GES DISC,GPM_3IMERGDF,07,2026-11-15,https://disc.example/c\n")
ANUAL = "fips,anio,prec_temporada_mm\n" + "".join(f"{f},2020,{400 + i}\n" for i, f in enumerate(FIPS))
MENSUAL = "fips,anio,mes,tmax_c\n" + "".join(f"{f},2020,2020-07,30.5\n" for f in FIPS)
CARD = "# Data card — clima\n\n## Supuestos\n\n- inventado para la prueba\n"


class TestEntregarSoloZip(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        r = self.repo
        self.escribir("data/processed/clima/clima_anual.csv", ANUAL)
        self.escribir("data/processed/clima/clima_mensual.csv", MENSUAL)
        self.escribir("data/processed/cultivos/produccion_anual.csv",
                      "fips,anio,cultivo,rend_bu_ac,flag_nass\n39001,2020,maiz,180,\n")
        self.escribir("docs/datasets/clima.md", CARD)
        self.escribir("docs/datasets/cultivos.md", "# Data card — cultivos\n")
        self.escribir("data/reference/condados.csv", CONDADOS)
        self.escribir("data/reference/anios.csv", ANIOS)
        self.escribir("manifest.csv", MANIFEST)
        # basura de referencia que no debe entrar al zip
        self.escribir("data/reference/mascara_agricola.tif", "no es un tif")
        self.escribir("data/raw/clima/a.json", "{}")

        def subir_prohibido(*a, **k):
            raise AssertionError("entregar.subir() no se debe llamar en --solo-zip")

        self.parches = [
            mock.patch.object(en, "REPO", r),
            mock.patch.object(en, "PROC", r / "data" / "processed"),
            mock.patch.object(en, "SALIDA", r / "data" / "entregas"),
            mock.patch.object(en, "subir", subir_prohibido),
            mock.patch.object(en, "gh", subir_prohibido),
            mock.patch.dict(os.environ, {"FIELDSHIFT_ESTADOS": "OH,KS"}),
        ]
        for p in self.parches:
            p.start()

    def tearDown(self):
        for p in reversed(self.parches):
            p.stop()
        self.tmp.cleanup()

    def escribir(self, rel: str, txt: str) -> None:
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(txt.encode("utf-8"))  # sin pasar 
 a 
 en Windows

    def correr(self, *args: str) -> str:
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["entregar.py", "--solo-zip", *args]), \
                contextlib.redirect_stdout(out):
            en.main()
        return out.getvalue()

    def zip_de(self, paquete: str) -> Path:
        return self.repo / "data" / "entregas" / f"datos-oh-ks_{paquete}.zip"

    # ---------------------------------------------------------------- nombre y contenido

    def test_nombre_del_zip_y_sha(self):
        self.correr("clima")
        z = self.zip_de("clima")
        self.assertTrue(z.exists(), f"no está {z.name}")
        sha = z.with_name(z.name + ".sha256")
        self.assertTrue(sha.exists())
        # mismo formato que `sha256sum`: "<hash>  <nombre>\n"
        texto = sha.read_text(encoding="utf-8")
        esperado = hashlib.sha256(z.read_bytes()).hexdigest()
        self.assertEqual(texto, f"{esperado}  {z.name}\n")
        # solo el paquete pedido
        self.assertFalse(self.zip_de("cultivos").exists())

    def test_contenido_del_zip(self):
        self.correr("clima")
        with zipfile.ZipFile(self.zip_de("clima")) as zf:
            nombres = set(zf.namelist())
            self.assertEqual(nombres, {
                "data/processed/clima/clima_anual.csv",
                "data/processed/clima/clima_mensual.csv",
                "docs/datasets/clima.md",
                "data/reference/condados.csv",
                "data/reference/anios.csv",
                "manifest.csv",
            })
            # los archivos van tal cual
            self.assertEqual(zf.read("data/processed/clima/clima_anual.csv").decode("utf-8"), ANUAL)
            self.assertEqual(zf.read("data/processed/clima/clima_mensual.csv").decode("utf-8"), MENSUAL)
            self.assertEqual(zf.read("docs/datasets/clima.md").decode("utf-8"), CARD)
            self.assertEqual(zf.read("data/reference/condados.csv").decode("utf-8"), CONDADOS)
            self.assertEqual(zf.read("data/reference/anios.csv").decode("utf-8"), ANIOS)
            self.assertTrue(all(i.compress_type == zipfile.ZIP_DEFLATED for i in zf.infolist()))

    def test_manifest_trae_las_filas_del_paquete(self):
        self.correr("clima")
        with zipfile.ZipFile(self.zip_de("clima")) as zf, zf.open("manifest.csv") as f:
            man = pd.read_csv(f, dtype=str, keep_default_na=False)
        self.assertEqual(list(man.columns),
                         ["paquete", "archivo", "fuente", "producto", "version", "fecha_descarga",
                          "consulta_o_url"])
        clima = man[man["paquete"] == "clima"]
        self.assertEqual(sorted(clima["archivo"]), ["data/raw/clima/a.json", "data/raw/clima/c.nc4"])

    @unittest.expectedFailure
    def test_manifest_solo_filas_del_paquete(self):
        # La tarea pide "las filas de manifest.csv del paquete"; entregar.py mete el manifest.csv entero
        # (con las filas de todos los paquetes). Ver "Para decidir" en el PR de T036.
        self.correr("clima")
        with zipfile.ZipFile(self.zip_de("clima")) as zf, zf.open("manifest.csv") as f:
            man = pd.read_csv(f, dtype=str, keep_default_na=False)
        self.assertEqual(set(man["paquete"]), {"clima"})

    def test_subcarpetas_de_processed(self):
        self.escribir("data/processed/clima/por_estado/clima_anual_oh.csv", ANUAL)
        self.correr("clima")
        with zipfile.ZipFile(self.zip_de("clima")) as zf:
            self.assertIn("data/processed/clima/por_estado/clima_anual_oh.csv", zf.namelist())

    def test_sin_data_card_igual_arma_el_zip(self):
        (self.repo / "docs/datasets/clima.md").unlink()
        self.correr("clima")
        with zipfile.ZipFile(self.zip_de("clima")) as zf:
            self.assertNotIn("docs/datasets/clima.md", zf.namelist())
            self.assertIn("data/processed/clima/clima_anual.csv", zf.namelist())

    # ---------------------------------------------------------------- modos y errores

    def test_sin_paquetes_arma_todos(self):
        salida = self.correr()
        self.assertTrue(self.zip_de("clima").exists())
        self.assertTrue(self.zip_de("cultivos").exists())
        self.assertIn("datos-oh-ks_clima.zip", salida)
        with zipfile.ZipFile(self.zip_de("cultivos")) as zf:
            self.assertIn("data/processed/cultivos/produccion_anual.csv", zf.namelist())
            self.assertNotIn("data/processed/clima/clima_anual.csv", zf.namelist())

    def test_paquete_vacio_corta(self):
        (self.repo / "data/processed/vacio").mkdir()
        with self.assertRaises(SystemExit) as e:
            self.correr("vacio")
        self.assertIn("vacio", str(e.exception.code))
        self.assertFalse(self.zip_de("vacio").exists())

    def test_sin_estados_corta(self):
        with mock.patch.dict(os.environ, {"FIELDSHIFT_ESTADOS": ""}), self.assertRaises(SystemExit) as e:
            self.correr("clima")
        self.assertIn("FIELDSHIFT_ESTADOS", str(e.exception.code))
        self.assertFalse(self.zip_de("clima").exists())

    def test_etiqueta_en_el_orden_de_la_variable(self):
        with mock.patch.dict(os.environ, {"FIELDSHIFT_ESTADOS": "ks"}):
            self.correr("clima")
        self.assertTrue((self.repo / "data/entregas/datos-ks_clima.zip").exists())

    def test_volver_a_correr_reemplaza(self):
        self.correr("clima")
        self.escribir("data/processed/clima/clima_anual.csv", ANUAL + "39005,2020,999\n")
        self.correr("clima")
        z = self.zip_de("clima")
        with zipfile.ZipFile(z) as zf:
            self.assertIn("39005,2020,999", zf.read("data/processed/clima/clima_anual.csv").decode("utf-8"))
        sha = z.with_name(z.name + ".sha256").read_text(encoding="utf-8").split()[0]
        self.assertEqual(sha, hashlib.sha256(z.read_bytes()).hexdigest())

    # ---------------------------------------------------------------- mismo formato que unir_estados

    def test_unir_estados_lee_el_zip(self):
        self.correr("clima")
        base = self.repo / "data" / "entregas"
        # unir_estados espera <base>/<release>/<release>_<paquete>.zip
        rel = base / "datos-oh-ks"
        rel.mkdir()
        for p in (self.zip_de("clima"), base / "datos-oh-ks_clima.zip.sha256"):
            p.rename(rel / p.name)
        salida = Path(self.tmp.name) / "unido"
        r = ue.unir(["datos-oh-ks"], base, salida, bajar_releases=False)
        self.assertEqual(r["clima/clima_anual.csv"], {"39": 2, "20": 1})
        df = pd.read_csv(salida / "clima" / "clima_anual.csv", dtype={"fips": str})
        self.assertEqual(sorted(df["fips"]), sorted(FIPS))


if __name__ == "__main__":
    unittest.main()
