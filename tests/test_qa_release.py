"""Prueba de scripts/qa_release.py con un release chico armado a mano (estados, condados y datos inventados).

Correr:  python -X utf8 -m unittest tests/test_qa_release.py   (o con pytest, si está instalado)
"""
from __future__ import annotations

import contextlib
import gzip
import io
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import qa_release as qa  # noqa: E402

# Dos estados inventados (XA = 91, XB = 92) con 4 condados cada uno, en una grilla de 0,5°.
FIPS = [f"91{i:03d}" for i in (1, 3, 5, 7)] + [f"92{i:03d}" for i in (1, 3, 5, 7)]
EST = {"91": "XA", "92": "XB"}
ANIOS = [2019, 2020, 2021]


def condados() -> str:
    filas = [f"{f},{EST[f[:2]]},C{f},{40 + (k // 4) * 0.5:.1f},{-95 + (k % 4) * 0.5:.1f},1000"
             for k, f in enumerate(FIPS)]
    return "fips,estado,condado,lat_centroide,lon_centroide,area_km2\n" + "\n".join(filas) + "\n"


def produccion() -> str:
    """Maíz: 100 bu/ac en XA y 110 en XB, salvo 91007 en 2021 (10 bu/ac: outlier contra sus vecinos)."""
    filas = []
    for f in FIPS:
        for a in ANIOS:
            rend = 100.0 if f[:2] == "91" else 110.0
            if f == "91007" and a == 2021:
                rend = 10.0
            filas.append(f"{f},{a},maiz,1000,1000,{rend * 1000:.0f},{rend},")
    return ("fips,anio,cultivo,sup_sembrada_ac,sup_cosechada_ac,produccion_bu,rend_bu_ac,flag_nass\n"
            + "\n".join(filas) + "\n")


def clima_mensual() -> str:
    """Lluvia de julio: 10 mm por condado en XA y 30 en XB; agosto 0 en todos."""
    filas = [f"{f},{a},{a}-{m:02d},{(10 if f[:2] == '91' else 30) if m == 7 else 0}"
             for f in FIPS for a in ANIOS for m in (7, 8)]
    return "fips,anio,mes,prec_power_mm\n" + "\n".join(filas) + "\n"


def quick_stats() -> bytes:
    """Base de Quick Stats mínima: total de estado XA maíz 2020 = 5000 ac y una fila 998 de 1000 ac."""
    cab = ["SOURCE_DESC", "AGG_LEVEL_DESC", "STATE_ALPHA", "COUNTY_CODE", "COMMODITY_DESC",
           "STATISTICCAT_DESC", "UNIT_DESC", "REFERENCE_PERIOD_DESC", "CLASS_DESC", "PRODN_PRACTICE_DESC",
           "UTIL_PRACTICE_DESC", "YEAR", "VALUE"]
    base = ["SURVEY", "", "XA", "", "CORN", "AREA PLANTED", "ACRES", "YEAR", "ALL CLASSES",
            "ALL PRODUCTION PRACTICES", "ALL UTILIZATION PRACTICES", "2020", ""]
    filas = []
    for nivel, cc, v in [("STATE", "", "5,000"), ("COUNTY", "998", "1,000"), ("COUNTY", "001", "1,000")]:
        f = list(base)
        f[1], f[3], f[12] = nivel, cc, v
        filas.append(f)
    return "\n".join("\t".join(r) for r in [cab] + filas).encode() + b"\n"


class TestQaRelease(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name) / "ext"
        for paq, archivos in {"cultivos": {"produccion_anual.csv": produccion()},
                              "clima": {"clima_mensual.csv": clima_mensual()}}.items():
            d = self.base / f"prueba_{paq}"
            (d / "data" / "processed" / paq).mkdir(parents=True)
            (d / "data" / "reference").mkdir(parents=True)
            (d / "data" / "reference" / "condados.csv").write_text(condados(), encoding="utf-8")
            for n, txt in archivos.items():
                (d / "data" / "processed" / paq / n).write_text(txt, encoding="utf-8")
        self.rel = qa.Release(self.base)

    def tearDown(self):
        self.tmp.cleanup()

    def test_estados_y_paquetes_salen_del_release(self):
        self.assertEqual(self.rel.estados, ["XA", "XB"])
        self.assertEqual(sorted(self.rel.paquetes), ["clima", "cultivos"])
        df = self.rel.leer("clima", "clima_mensual.csv")
        self.assertEqual(set(df.estado), {"XA", "XB"})
        self.assertEqual(df.fips.str.len().unique().tolist(), [5])

    def test_eventos(self):
        s = qa.serie_evento(self.rel, {"paquete": "clima", "archivo": "clima_mensual.csv",
                                       "columna": "prec_power_mm", "meses": [7]})
        self.assertEqual(s.loc[2020, "XA"], 10)
        self.assertEqual(s.loc[2020, "XB"], 30)
        s = qa.serie_evento(self.rel, {"tipo": "suma_meses", "paquete": "clima", "archivo": "clima_mensual.csv",
                                       "columna": "prec_power_mm", "meses": [7, 8]})
        self.assertEqual(s.loc[2021, "XB"], 30)
        r = qa.serie_evento(self.rel, {"tipo": "rend_implicito", "cultivo": "maiz"})
        self.assertAlmostEqual(r.loc[2021, "XA"], (100 * 3 + 10) / 4)
        self.assertEqual(r.loc[2021, "XB"], 110)
        s = qa.serie_evento(self.rel, {"tipo": "suma_condados", "paquete": "cultivos",
                                       "archivo": "produccion_anual.csv", "cultivo": "maiz",
                                       "columna": "sup_sembrada_ac", "escala": 1000})
        self.assertEqual(s.loc[2019, "XA"], 4)

    def test_evento_con_fips(self):
        s = qa.serie_evento(self.rel, {"paquete": "cultivos", "archivo": "produccion_anual.csv", "cultivo": "maiz",
                                       "columna": "rend_bu_ac", "fips": [91007]})
        self.assertEqual(s.loc[2021, "XA"], 10)
        self.assertEqual(list(s.columns), ["XA"])

    def test_eventos_por_estado(self):
        """Un evento de estados que no están en el release se saltea con aviso; si alguno está, solo se muestra ese."""
        eventos = [
            {"titulo": "solo KS", "estados": ["KS"], "paquete": "clima", "archivo": "clima_mensual.csv",
             "columna": "prec_power_mm", "meses": [7], "anios": [2020]},
            {"titulo": "MO y XB", "estados": ["MO", "XB"], "paquete": "clima", "archivo": "clima_mensual.csv",
             "columna": "prec_power_mm", "meses": [7], "anios": [2020], "esperado": "alta", "fuente": "sección X"},
            {"titulo": "columna que no está", "estados": ["XA"], "paquete": "clima", "archivo": "clima_mensual.csv",
             "columna": "spi6", "anios": [2020]},
        ]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            qa.seccion_eventos(self.rel, eventos)
        txt = out.getvalue()
        self.assertIn("_solo KS: KS no está en el release (XA, XB): se saltea._", txt)
        self.assertIn("| anio | XB |", txt)
        self.assertIn("| 2020 | 30.00 |", txt)
        self.assertNotIn("| 2020 | 10.00 |", txt)
        self.assertIn("Esperado: alta (sección X)", txt)
        self.assertIn("no está la columna `spi6`", txt)

    def test_yaml_de_t117_se_saltean_sin_error(self):
        """Las listas de KS y de MO/WI/SD corren sobre un release sin esos estados: todo se saltea con aviso."""
        args = [str(self.base)]
        for n in ("eventos_ks.yaml", "eventos_mo_wi_sd.yaml"):
            args += ["--eventos", str(REPO / "docs" / "qa" / n)]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            qa.main(args)
        ev = out.getvalue().split("## Eventos")[1].split("## Rangos")[0]
        bloques = [b for b in ev.split("\n\n")[1:] if b.strip()]
        self.assertTrue(bloques)
        self.assertTrue(all("se saltea" in b for b in bloques), bloques)

    def test_outlier_contra_vecinos(self):
        vec = qa.vecinos(self.rel.condados)
        pa = self.rel.leer("cultivos", "produccion_anual.csv")
        o = qa.outliers(pa, "rend_bu_ac", vec, 5)
        self.assertIn(("91007", 2021), set(zip(o.fips, o.anio)))

    def test_faltantes_card(self):
        card = Path(self.tmp.name) / "card.md"
        card.write_text("| archivo | columna | a | b | c | d | e | f | faltantes |\n"
                        "| x.csv | col_mm | | | | | | | 12,5 |\n", encoding="utf-8")
        self.assertEqual(qa.faltantes_card(card), {("x.csv", "col_mm"): 12.5})

    def test_main_de_punta_a_punta(self):
        ev = Path(self.tmp.name) / "eventos.yaml"
        ev.write_text("eventos:\n"
                      "  - {titulo: lluvia de julio, paquete: clima, archivo: clima_mensual.csv,\n"
                      "     columna: prec_power_mm, meses: [7], anios: [2020]}\n"
                      "  - {titulo: ndvi, paquete: vegetacion, archivo: vegetacion_mensual.csv,\n"
                      "     columna: ndvi_anom_z, anios: [2020]}\n", encoding="utf-8")
        qs = Path(self.tmp.name) / "qs.txt.gz"
        qs.write_bytes(gzip.compress(quick_stats()))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            qa.main([str(self.base), "--eventos", str(ev), "--qs", str(qs)])
        txt = out.getvalue()
        self.assertIn("# QA de `ext`: XA, XB", txt)
        self.assertIn("| 2020 | 10.00 | 30.00 |", txt)
        self.assertIn("no está `vegetacion/vegetacion_mensual.csv`", txt)
        self.assertIn("No está `clima/clima_diario.csv`", txt)
        # XA maíz 2020: 4000 ac de condados de 5000 de estado (80 %); con la fila 998, 100 %
        self.assertIn("- XA maiz 2020: 4,000 de 5,000 ac (80.0 %); con OTHER (COMBINED) 100.0 %", txt)


if __name__ == "__main__":
    unittest.main()
