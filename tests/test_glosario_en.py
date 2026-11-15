"""Prueba de docs/datasets/glosario_en.csv: cada columna de los data cards está en el glosario y traducida.

Correr:  python -X utf8 -m unittest tests/test_glosario_en.py   (o con pytest, si está instalado)
"""
from __future__ import annotations

import csv
import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DIR = REPO / "docs" / "datasets"

_spec = importlib.util.spec_from_file_location("glosario_en", DIR / "glosario_en.py")
glosario_en = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(glosario_en)


def leer_glosario() -> list[dict]:
    with open(DIR / "glosario_en.csv", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class TestGlosarioEn(unittest.TestCase):
    def test_encabezado(self):
        with open(DIR / "glosario_en.csv", encoding="utf-8") as fh:
            self.assertEqual(fh.readline().strip().split(","), glosario_en.COLUMNAS)

    def test_cada_columna_de_los_data_cards_esta(self):
        cards = {(f["paquete"], f["archivo"], f["columna"]) for f in glosario_en.leer_todos(DIR)}
        self.assertTrue(cards, "no se leyó ninguna tabla de los data cards")
        glosario = {(f["paquete"], f["archivo"], f["columna"]) for f in leer_glosario()}
        faltan = sorted(cards - glosario)
        sobran = sorted(glosario - cards)
        self.assertEqual(faltan, [], "columnas de los data cards que faltan en el glosario (regenerarlo)")
        self.assertEqual(sobran, [], "columnas del glosario que ya no están en los data cards (regenerarlo)")

    def test_todas_traducidas(self):
        sin = [f"{f['paquete']}/{f['archivo']}/{f['columna']}" for f in leer_glosario()
               if not f["descripcion_en"] or f["descripcion_en"].startswith(glosario_en.SIN_TRADUCCION)]
        self.assertEqual(sin, [], "agregar la traducción en DESCRIPCIONES de glosario_en.py")

    def test_csv_al_dia(self):
        salida, _ = glosario_en.armar(glosario_en.leer_todos(DIR))
        self.assertEqual(salida, leer_glosario(), "glosario_en.csv desactualizado: correr glosario_en.py")


if __name__ == "__main__":
    unittest.main()
