"""Prueba de scripts/unir_estados.py con zips chicos armados a mano (dos "estados" falsos, sin datos reales).

Correr:  python -X utf8 -m unittest tests/test_unir_estados.py   (o con pytest, si está instalado)
"""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import unir_estados as ue  # noqa: E402

MANIFEST = "paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n"
ANIOS = "anio,inicio_temporada,fin_temporada\n2020,2020-04-01,2020-09-30\n2021,2021-04-01,2021-09-30\n"


def condados(fips: list[str]) -> str:
    return "fips,estado,condado\n" + "".join(f"{f},XX,C{f}\n" for f in fips)


def anual(fips: list[str], extra_col: str = "prec_temporada_mm") -> str:
    filas = "".join(f"{f},{a},{100 + i}\n" for i, f in enumerate(fips) for a in (2020, 2021))
    return f"fips,anio,{extra_col}\n" + filas


def armar(base: Path, release: str, paquete: str, archivos: dict[str, str], fips: list[str],
          manifest_filas: str = "", romper_sha: bool = False) -> None:
    d = base / release
    d.mkdir(parents=True, exist_ok=True)
    z = d / f"{release}_{paquete}.zip"
    with zipfile.ZipFile(z, "w") as zf:
        for nombre, txt in archivos.items():
            zf.writestr(f"data/processed/{paquete}/{nombre}", txt)
        zf.writestr(f"docs/datasets/{paquete}.md", f"# {paquete} ({release})\n")
        zf.writestr("data/reference/condados.csv", condados(fips))
        zf.writestr("data/reference/anios.csv", ANIOS)
        zf.writestr("manifest.csv", MANIFEST + manifest_filas)
    h = hashlib.sha256(z.read_bytes()).hexdigest()
    if romper_sha:
        h = "0" * 64
    z.with_suffix(".zip.sha256").write_text(f"{h}  {z.name}\n", encoding="utf-8")


# Estados falsos: "01" (3 condados) y "02" (2 condados). Ceros a la izquierda para ver que fips quede texto.
F1 = ["01001", "01003", "01005"]
F2 = ["02010", "02020"]


class TestUnirEstados(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name) / "entregas"
        self.salida = Path(self.tmp.name) / "unido"

    def tearDown(self):
        self.tmp.cleanup()

    def correr(self, releases=("datos-aa", "datos-bb"), **kw):
        return ue.unir(list(releases), self.base, self.salida, bajar_releases=False, **kw)

    def armar_ok(self):
        m = "clima,data/raw/clima/x.json,NASA,POWER,v2,2026-11-15,https://power\n"
        armar(self.base, "datos-aa", "clima", {"clima_anual.csv": anual(F1)}, F1, m)
        armar(self.base, "datos-bb", "clima", {"clima_anual.csv": anual(F2)}, F2, m)
        fen1 = "fips_estado,anio,cultivo,doy_50_sembrado\n01,2020,maiz,120\n01,2020,soja,135\n"
        fen2 = "fips_estado,anio,cultivo,doy_50_sembrado\n02,2020,maiz,118\n"
        prod = lambda fs: "fips,anio,cultivo,rend_bu_ac,flag_nass\n" + "".join(  # noqa: E731
            f"{f},2020,{c},150,\n" for f in fs for c in ("maiz", "soja"))
        armar(self.base, "datos-aa", "cultivos",
              {"fenologia_estado.csv": fen1, "produccion_anual.csv": prod(F1)}, F1,
              "cultivos,data/raw/cultivos/a.gz,USDA NASS,QS,1,2026-11-15,https://nass\n")
        armar(self.base, "datos-bb", "cultivos",
              {"fenologia_estado.csv": fen2, "produccion_anual.csv": prod(F2)}, F2)

    def test_union_correcta(self):
        self.armar_ok()
        r = self.correr()
        self.assertEqual(r["clima/clima_anual.csv"], {"01": 6, "02": 4})
        self.assertEqual(r["cultivos/produccion_anual.csv"], {"01": 6, "02": 4})
        self.assertEqual(r["cultivos/fenologia_estado.csv"], {"01": 2, "02": 1})

        df = pd.read_csv(self.salida / "clima" / "clima_anual.csv", dtype={"fips": str})
        self.assertEqual(sorted(df["fips"].unique()), F1 + F2)
        texto = (self.salida / "cultivos" / "fenologia_estado.csv").read_text(encoding="utf-8")
        self.assertIn("\n01,2020,maiz,120", texto)  # fips_estado conserva el cero
        # la celda vacía de flag_nass sigue vacía, no "nan"
        self.assertNotIn("nan", (self.salida / "cultivos" / "produccion_anual.csv").read_text(encoding="utf-8"))

        cond = pd.read_csv(self.salida / "condados.csv", dtype={"fips": str})
        self.assertEqual(list(cond["fips"]), F1 + F2)  # sin repetir, aunque viene en cada zip
        man = pd.read_csv(self.salida / "manifest.csv")
        self.assertEqual(len(man), 2)  # la fila de clima repetida en los dos releases queda una vez
        self.assertEqual(len(pd.read_csv(self.salida / "anios.csv")), 2)
        self.assertTrue((self.salida / "clima" / "datos-aa.md").exists())

    def test_encabezado_distinto(self):
        armar(self.base, "datos-aa", "clima", {"clima_anual.csv": anual(F1)}, F1)
        armar(self.base, "datos-bb", "clima", {"clima_anual.csv": anual(F2, "prec_temp_mm")}, F2)
        with self.assertRaises(ue.ErrorUnion) as e:
            self.correr()
        msg = str(e.exception)
        self.assertIn("prec_temporada_mm", msg)
        self.assertIn("prec_temp_mm", msg)

    def test_fips_en_dos_releases(self):
        armar(self.base, "datos-aa", "clima", {"clima_anual.csv": anual(F1)}, F1)
        armar(self.base, "datos-bb", "clima", {"clima_anual.csv": anual(F2 + ["01003"])}, F2 + ["01003"])
        with self.assertRaises(ue.ErrorUnion) as e:
            self.correr()
        self.assertIn("01003", str(e.exception))
        self.assertIn("más de un release", str(e.exception))

    def test_clave_duplicada_dentro_de_un_release(self):
        txt = anual(F1) + "01001,2020,999\n"
        armar(self.base, "datos-aa", "clima", {"clima_anual.csv": txt}, F1)
        armar(self.base, "datos-bb", "clima", {"clima_anual.csv": anual(F2)}, F2)
        with self.assertRaises(ue.ErrorUnion) as e:
            self.correr()
        self.assertIn("duplicada", str(e.exception))

    def test_sha256_malo(self):
        armar(self.base, "datos-aa", "clima", {"clima_anual.csv": anual(F1)}, F1, romper_sha=True)
        armar(self.base, "datos-bb", "clima", {"clima_anual.csv": anual(F2)}, F2)
        with self.assertRaises(ue.ErrorUnion) as e:
            self.correr()
        self.assertIn("sha256", str(e.exception))

    def test_paquete_que_falta_en_un_release(self):
        self.armar_ok()
        armar(self.base, "datos-aa", "agua", {"agua_mensual.csv": "fips,anio,mes,sm_m3m3\n01001,2020,2020-07,0.3\n"},
              F1)
        r = self.correr()
        self.assertEqual(r["agua/agua_mensual.csv"], {"01": 1})

    def test_claves(self):
        self.assertEqual(ue.claves(["fips", "anio", "cultivo", "rend_bu_ac"]), ["fips", "anio", "cultivo"])
        self.assertEqual(ue.claves(["fips", "anio", "mes", "tmax_c", "anio_censo"]), ["fips", "anio", "mes"])


if __name__ == "__main__":
    unittest.main()
