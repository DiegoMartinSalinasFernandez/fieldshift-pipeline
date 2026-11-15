"""Pruebas de los costos ERS por condado en src/economia/process.py (T141). Sin red.

Usa tablas inventadas chicas (no son datos reales): dos condados de regiones distintas y costos
regionales de juguete.

Correr:  python -X utf8 -m unittest tests/test_economia_condado.py   (o con pytest)
"""
from __future__ import annotations

import importlib.util
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def cargar():
    spec = importlib.util.spec_from_file_location("t141_economia_process", REPO / "src/economia/process.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


proc = cargar()
COLS = ["valor_produccion_usd_ac", "costo_operativo_usd_ac", "costo_total_usd_ac", "margen_operativo_usd_ac"]

REGIONES = pd.DataFrame({"fips": ["39001", "39003"], "estado": ["OH", "OH"],
                         "region_ers": ["Heartland", "Eastern Uplands"]})


def reg_juguete() -> pd.DataFrame:
    """Costos regionales: Heartland tiene maíz 2000 y 2001; Eastern Uplands solo maíz 2000."""
    filas = [("Heartland", 2000, "maiz", 100.0), ("Heartland", 2001, "maiz", 110.0),
             ("Eastern Uplands", 2000, "maiz", 80.0)]
    d = pd.DataFrame(filas, columns=["region_ers", "anio", "cultivo", "base"])
    for i, c in enumerate(COLS):
        d[c] = d["base"] + i
    return d.drop(columns="base")


class TestCostosCondado(unittest.TestCase):
    def setUp(self):
        self.out = proc.costos_condado(REGIONES, reg_juguete(), range(2000, 2002))

    def test_grilla_completa(self):
        self.assertEqual(list(self.out.columns), ["fips", "anio", "cultivo", "region_ers"] + COLS)
        # 2 condados x 2 años x 4 cultivos de ERS
        self.assertEqual(len(self.out), 2 * 2 * len(proc.ERS))
        self.assertFalse(self.out.duplicated(["fips", "anio", "cultivo"]).any())

    def test_cada_condado_toma_su_region(self):
        o = self.out.set_index(["fips", "anio", "cultivo"])
        self.assertEqual(o.at[("39001", 2000, "maiz"), "costo_total_usd_ac"], 102.0)
        self.assertEqual(o.at[("39003", 2000, "maiz"), "costo_total_usd_ac"], 82.0)
        self.assertEqual(o.at[("39003", 2000, "maiz"), "region_ers"], "Eastern Uplands")

    def test_region_sin_dato_queda_vacia_sin_reponderar(self):
        o = self.out.set_index(["fips", "anio", "cultivo"])
        # Eastern Uplands no tiene 2001: vacío, no el valor de Heartland
        self.assertTrue(math.isnan(o.at[("39003", 2001, "maiz"), "costo_total_usd_ac"]))
        self.assertTrue(o.loc[("39001", 2000, "soja"), COLS].isna().all())


class TestTablaRegiones(unittest.TestCase):
    def correr(self, condados: pd.DataFrame, reglink: pd.DataFrame):
        with tempfile.TemporaryDirectory() as d:
            cpath = Path(d) / "condados.csv"
            condados.to_csv(cpath, index=False)
            ref = Path(d) / "ref" / "regiones_ers.csv"
            with mock.patch.object(proc, "CONDADOS", cpath), mock.patch.object(proc, "REF_REGIONES", ref), \
                    mock.patch.object(proc, "regiones_condado", return_value=reglink):
                t = proc.tabla_regiones({"OH": {"fips": 39}})
                guardada = pd.read_csv(ref, dtype={"fips": str})
        return t, guardada

    def test_filtra_estados_y_guarda(self):
        condados = pd.DataFrame({"fips": ["39001", "27001"], "estado": ["OH", "MN"]})
        reglink = pd.DataFrame({"fips_condado": ["39001", "27001"], "region_ers": ["Heartland", "Northern Crescent"]})
        t, guardada = self.correr(condados, reglink)
        self.assertEqual(list(t["fips"]), ["39001"])
        self.assertEqual(list(guardada.columns), ["fips", "estado", "region_ers"])
        self.assertEqual(guardada.loc[0, "region_ers"], "Heartland")

    def test_condado_sin_region_falla(self):
        condados = pd.DataFrame({"fips": ["39001", "39003"], "estado": ["OH", "OH"]})
        reglink = pd.DataFrame({"fips_condado": ["39001"], "region_ers": ["Heartland"]})
        with self.assertRaises(SystemExit):
            self.correr(condados, reglink)


class TestBorde(unittest.TestCase):
    def test_tabla_borde_diferencia_con_el_estado(self):
        cond = proc.costos_condado(REGIONES, reg_juguete(), range(2000, 2002))
        anual = pd.DataFrame({"fips_estado": ["39"], "anio": [2001], "cultivo": ["maiz"],
                              "costo_total_usd_ac": [105.0]})
        with tempfile.TemporaryDirectory() as d:
            cpath = Path(d) / "condados.csv"
            pd.DataFrame({"fips": ["39001", "39003"], "condado": ["A", "B"]}).to_csv(cpath, index=False)
            with mock.patch.object(proc, "CONDADOS", cpath):
                filas = proc.tabla_borde(anual, cond, REGIONES, [("39001", "39003")])
        # último año con dato de maíz: 2001; 39003 no tiene dato ese año y no aparece
        self.assertEqual(len(filas), 1)
        self.assertIn("| 2001 | 39001 | A | Heartland | 112.00 | 105.00 | +7.00 |", filas[0])

    def test_condados_de_borde_vecinos_de_regiones_distintas(self):
        import geopandas as gpd
        from shapely.geometry import box
        g = gpd.GeoDataFrame({"fips": ["39001", "39003", "39005"]},
                             geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1), box(5, 5, 6, 6)], crs="EPSG:4326")
        regiones = pd.DataFrame({"fips": ["39001", "39003", "39005"], "estado": ["OH"] * 3,
                                 "region_ers": ["Heartland", "Eastern Uplands", "Northern Crescent"]})
        with tempfile.TemporaryDirectory() as d:
            gp = Path(d) / "condados.gpkg"
            g.to_file(gp, driver="GPKG")
            with mock.patch.object(proc, "GPKG", gp):
                pares = proc.condados_de_borde(regiones)
        self.assertEqual(pares, [("39001", "39003")])

    def test_sin_gpkg_no_hay_pares(self):
        with mock.patch.object(proc, "GPKG", Path("/no/existe.gpkg")):
            self.assertEqual(proc.condados_de_borde(REGIONES), [])


if __name__ == "__main__":
    unittest.main()
