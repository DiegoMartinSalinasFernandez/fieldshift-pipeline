"""Pruebas sin red de docs/demo/coverage.py, docs/demo/user_story.py y docs/demo/figuras.py.

Arman en un directorio temporal un release chico inventado (dos estados ficticios, XA = 91 y XB = 92, con
números inventados solo para la prueba) con la misma estructura que los zips de `scripts/entregar.py`:
`data/processed/<paquete>/<archivo>.csv` y `data/reference/condados.csv`, cada zip con su `.sha256` al lado.

Correr:  python -X utf8 -m unittest tests/test_demo_scripts.py   (o con pytest, si está instalado)
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def cargar_script(nombre: str):
    """Importa docs/demo/<nombre>.py por ruta, con otro nombre: `coverage` choca con el paquete de pytest-cov."""
    spec = importlib.util.spec_from_file_location(f"demo_{nombre}", REPO / "docs" / "demo" / f"{nombre}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cov = cargar_script("coverage")
fig = cargar_script("figuras")
us = cargar_script("user_story")

FIPS = ["91001", "91003", "92001"]
ANIOS = [2011, 2012, 2013]


def csv(filas: list[list], cols: list[str]) -> str:
    return ",".join(cols) + "\n" + "".join(",".join("" if v is None else str(v) for v in f) + "\n" for f in filas)


def condados() -> str:
    return csv([[f, "XA" if f.startswith("91") else "XB", f"C{f}", 40.0, -95.0, 1000] for f in FIPS],
               ["fips", "estado", "condado", "lat_centroide", "lon_centroide", "area_km2"])


def produccion() -> str:
    filas = []
    for i, f in enumerate(FIPS):
        for a in ANIOS:
            filas.append([f, a, "maiz", 1000 + i, 900 + i, 150000, 100 + i + (a - 2011) * 10, ""])
            filas.append([f, a, "soja", 2000 + i, 1900 + i, 90000, 40 + i, ""])
    return csv(filas, ["fips", "anio", "cultivo", "sup_sembrada_ac", "sup_cosechada_ac", "produccion_bu",
                       "rend_bu_ac", "flag_nass"])


def clima_anual() -> str:
    return csv([[f, a, 500 + a - 2011, 80 + 10 * i, 29.5] for i, f in enumerate(FIPS) for a in ANIOS],
               ["fips", "anio", "prec_temporada_mm", "prec_jul_mm", "tmax_jul_c"])


def clima_mensual() -> str:
    return csv([[f, a, f"{a}-{m:02d}", 0.5] for f in FIPS for a in ANIOS for m in range(1, 13)],
               ["fips", "anio", "mes", "spi3"])


def fenologia_estado() -> str:
    return csv([[e, a, c, 120] for e in ("91", "92") for a in ANIOS for c in ("maiz", "soja")],
               ["fips_estado", "anio", "cultivo", "doy_50_sembrado"])


def secuencia() -> str:
    return csv([[f, v, 40.0] for f in FIPS for v in ("2008-2015", "2009-2016")],
               ["fips", "ventana", "pct_maiz_soja"])


def hacer_zip(destino: Path, archivos: dict[str, str]) -> Path:
    with zipfile.ZipFile(destino, "w") as z:
        for nombre, texto in archivos.items():
            z.writestr(nombre, texto)
    suma = hashlib.sha256(destino.read_bytes()).hexdigest()
    destino.with_name(destino.name + ".sha256").write_text(f"{suma}  {destino.name}\n")
    return destino


def release(carpeta: Path, tag: str = "datos-xa-xb") -> list[Path]:
    """Dos zips (cultivos y clima) en `carpeta`, como los de un release."""
    carpeta.mkdir(parents=True, exist_ok=True)
    ref = {"data/reference/condados.csv": condados()}
    return [
        hacer_zip(carpeta / f"{tag}_cultivos.zip", {
            **ref,
            "data/processed/cultivos/produccion_anual.csv": produccion(),
            "data/processed/cultivos/fenologia_estado.csv": fenologia_estado(),
            "data/processed/cultivos/rotacion_secuencia.csv": secuencia(),
        }),
        hacer_zip(carpeta / f"{tag}_clima.zip", {
            **ref,
            "data/processed/clima/clima_anual.csv": clima_anual(),
            "data/processed/clima/clima_mensual.csv": clima_mensual(),
        }),
    ]


def romper(z: Path) -> None:
    """Cambia el .sha256 para que no coincida con el zip."""
    z.with_name(z.name + ".sha256").write_text("0" * 64 + f"  {z.name}\n")


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()


# --------------------------------------------------------------------------- coverage.py

class TestCoverage(Base):
    def bajar(self, tag: str = "datos-xa-xb") -> list[Path]:
        """`cov.bajar` con --sin-bajar sobre zips ya puestos en <tmp>/<tag>/: no toca la red."""
        assets = [{"name": z.name, "size": z.stat().st_size} for z in release(self.tmp / tag, tag)]
        viejo = cov.ZIPS
        cov.ZIPS = self.tmp
        try:
            return cov.bajar("dueño/repo", {"tag_name": tag, "assets": assets}, sin_bajar=True)
        finally:
            cov.ZIPS = viejo

    def test_cuenta_filas_anios_y_condados(self):
        s = cov.resumir(self.bajar())
        self.assertEqual(set(s["paquetes"]), {"cultivos", "clima"})
        self.assertEqual(s["fips"], set(FIPS))
        self.assertEqual(s["estados"], ["91 (2)", "92 (1)"])   # estados ficticios: sin sigla en FIPS_ESTADO
        self.assertEqual(s["anios"], set(ANIOS))
        por_archivo = {f["archivo"]: f for d in s["paquetes"].values() for f in d["csv"]}
        self.assertEqual(por_archivo["produccion_anual.csv"]["filas"], len(FIPS) * len(ANIOS) * 2)
        self.assertEqual(por_archivo["produccion_anual.csv"]["columnas"], 8)
        self.assertEqual(por_archivo["produccion_anual.csv"]["anios"], (2011, 2013, 3))
        self.assertEqual(por_archivo["clima_mensual.csv"]["filas"], len(FIPS) * len(ANIOS) * 12)
        self.assertEqual(por_archivo["fenologia_estado.csv"]["unidad"], "fips_estado")
        self.assertEqual(por_archivo["fenologia_estado.csv"]["n_geo"], 2)
        self.assertEqual(por_archivo["rotacion_secuencia.csv"]["ventanas"], ["2008-2015", "2009-2016"])

    def test_seccion_lista_lo_publicado_y_lo_que_falta(self):
        r = {"tag_name": "datos-xa-xb", "published_at": "2026-11-15T00:00:00Z"}
        texto = cov.seccion("dueño/repo", [r], {"datos-xa-xb": cov.resumir(self.bajar())})
        self.assertTrue(texto.startswith(cov.INICIO) and texto.endswith(cov.FIN))
        self.assertIn("| `datos-xa-xb` | 91 (2), 92 (1) | 3 | 2011–2013 | 2 |", texto)
        self.assertIn("| `datos-ks` | Kansas | | | | | | in progress |", texto)
        self.assertIn("| `produccion_anual.csv` | 18 | 8 | fips | 3 | 2011–2013 (3 years) |", texto)
        self.assertIn("2 8-year windows, 2008-2015 to 2009-2016", texto)

    def test_reemplaza_solo_entre_marcas(self):
        pagina = f"# Título\n\nantes a mano\n\n{cov.INICIO}\nviejo\n{cov.FIN}\n\ndespués a mano\n"
        nuevo = cov.reemplazar(pagina, f"{cov.INICIO}\nNUEVO\n{cov.FIN}")
        self.assertEqual(nuevo, f"# Título\n\nantes a mano\n\n{cov.INICIO}\nNUEVO\n{cov.FIN}\n\ndespués a mano\n")

    def test_sin_marcas_falla_con_mensaje(self):
        with self.assertRaises(SystemExit) as e:
            cov.reemplazar("# sin marcas\n", "x")
        self.assertIn("faltan las marcas", str(e.exception.code))

    def test_sha256_que_no_coincide(self):
        tag = "datos-xa-xb"
        zips = release(self.tmp / tag, tag)
        romper(zips[0])
        assets = [{"name": z.name, "size": z.stat().st_size} for z in zips]
        viejo = cov.ZIPS
        cov.ZIPS = self.tmp
        try:
            with self.assertRaises(SystemExit) as e:
                cov.bajar("dueño/repo", {"tag_name": tag, "assets": assets}, sin_bajar=True)
        finally:
            cov.ZIPS = viejo
        self.assertEqual(e.exception.code, f"{zips[0].name}: el sha256 no coincide")


# --------------------------------------------------------------------------- user_story.py

class TestUserStory(Base):
    HISTORIA = {"id": "prueba", "fips": "91003", "anios": ANIOS}

    def test_carga_y_cuenta(self):
        release(self.tmp / "datos-xa-xb")
        t, cond, origen = us.cargar(self.tmp)
        self.assertEqual(origen, ["datos-xa-xb_clima.zip", "datos-xa-xb_cultivos.zip"])
        self.assertEqual(len(t["produccion_anual"]), len(FIPS) * len(ANIOS) * 2)
        self.assertEqual(len(t["clima_mensual"]), len(FIPS) * len(ANIOS) * 12)
        self.assertEqual(sorted(t["produccion_anual"]["anio"].unique()), ANIOS)
        self.assertEqual(len(cond), len(FIPS))   # condados.csv viene en los dos zips: no se duplica

    def test_tabla_con_valores_del_zip(self):
        release(self.tmp / "datos-xa-xb")
        t, cond, _ = us.cargar(self.tmp)
        tabla = us.tabla(t, cond, self.HISTORIA)
        self.assertIn("**C91003 County, XA** (FIPS 91003)", tabla)
        self.assertIn("| Variable — source | 2011 | 2012 | 2013 |", tabla)
        self.assertIn("| Corn yield (bu/ac) — NASS | 101.0 | 111.0 | 121.0 |", tabla)
        self.assertIn("| July rain (mm) — POWER | 90 | 90 | 90 |", tabla)
        self.assertIn("| SPI-3 ending July (May–Jul) — POWER | 0.50 | 0.50 | 0.50 |", tabla)
        self.assertIn("| Peak NDVI, all cropland — MODIS | n/a | n/a | n/a |", tabla)   # sin vegetacion
        self.assertIn("corn 2011: 120, 2012: 120, 2013: 120", tabla)

    def test_reemplaza_solo_entre_marcas(self):
        texto = ("Intro a mano. Zips: <!-- zips -->`viejo.zip`<!-- /zips -->.\n\n"
                 "<!-- tabla:a -->\nvieja A\n<!-- /tabla:a -->\n\ntexto en el medio\n\n"
                 "<!-- tabla:b -->\nvieja B\n<!-- /tabla:b -->\nfinal a mano\n")
        nuevo = us.reemplazar(texto, {"a": "NUEVA A"}, ["x_clima.zip", "x_cultivos.zip"])
        self.assertEqual(nuevo,
                         "Intro a mano. Zips: <!-- zips -->`x_clima.zip`, `x_cultivos.zip`<!-- /zips -->.\n\n"
                         "<!-- tabla:a -->\nNUEVA A\n<!-- /tabla:a -->\n\ntexto en el medio\n\n"
                         "<!-- tabla:b -->\nvieja B\n<!-- /tabla:b -->\nfinal a mano\n")

    def test_sin_marcas_falla_con_mensaje(self):
        with self.assertRaises(SystemExit) as e:
            us.reemplazar("sin marcas", {"a": "x"}, [])
        self.assertEqual(e.exception.code, "user_story.md no tiene los marcadores de la tabla a")

    def test_sha256_que_no_coincide(self):
        zips = release(self.tmp / "datos-xa-xb")
        romper(zips[1])
        with self.assertRaises(SystemExit) as e:
            us.cargar(self.tmp)
        self.assertEqual(e.exception.code, f"{zips[1].name}: el sha256 NO coincide; volvé a bajarlo")

    def test_sin_sha256_falla_con_mensaje(self):
        zips = release(self.tmp / "datos-xa-xb")
        zips[0].with_name(zips[0].name + ".sha256").unlink()
        with self.assertRaises(SystemExit) as e:
            us.cargar(self.tmp)
        self.assertIn(f"falta {zips[0].name}.sha256", e.exception.code)


# --------------------------------------------------------------------------- figuras.py

class TestFiguras(Base):
    def test_lee_y_une_los_zips(self):
        d = self.tmp / "datos-xa-xb"
        release(d)
        prod = fig.leer([d], "produccion_anual.csv")
        self.assertEqual(len(prod), len(FIPS) * len(ANIOS) * 2)
        self.assertEqual(sorted(prod["anio"].unique()), ANIOS)
        self.assertEqual(prod["fips"].iloc[0], "91001")   # fips como texto, con sus ceros
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertIsNone(fig.leer([d], "agua_mensual.csv"))
        self.assertIn("agua_mensual.csv no está en ningún zip", err.getvalue())

    def test_dos_releases_no_duplican_filas(self):
        release(self.tmp / "a", "datos-xa-xb")
        release(self.tmp / "b", "datos-xa-xb-otra")   # mismas claves: se queda una fila por clave
        clima = fig.leer([self.tmp / "a", self.tmp / "b"], "clima_anual.csv")
        self.assertEqual(len(clima), len(FIPS) * len(ANIOS))

    def test_sha256_que_no_coincide_se_descarta(self):
        d = self.tmp / "datos-xa-xb"
        zips = release(d)
        romper(zips[0])
        with contextlib.redirect_stderr(io.StringIO()) as err, contextlib.redirect_stdout(io.StringIO()):
            fig.controlar_sha256(d)
        self.assertIn(f"AVISO: {zips[0].name}: el sha256 NO coincide; se descarta", err.getvalue())
        self.assertFalse(zips[0].exists())
        self.assertTrue(zips[0].with_name(zips[0].name + ".malo").exists())
        self.assertTrue(zips[1].exists())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertIsNone(fig.leer([d], "produccion_anual.csv"))   # el zip descartado ya no se lee

    def test_dibuja_con_los_datos_del_zip(self):
        d = self.tmp / "datos-xa-xb"
        release(d)
        salida = self.tmp / "fig"
        prod, clima = fig.leer([d], "produccion_anual.csv"), fig.leer([d], "clima_anual.csv")
        with contextlib.redirect_stdout(io.StringIO()):
            fig.fig_lluvia_julio(prod, clima, salida)
            fig.fig_rend_por_anio(prod, salida)
        self.assertEqual(sorted(p.name for p in salida.iterdir()),
                         ["fig1_corn_yield_july_rain.png", "fig5_corn_yield_by_year.png"])

    def test_figura_sin_columnas_se_saltea(self):
        salida = self.tmp / "fig"
        with contextlib.redirect_stderr(io.StringIO()) as err:
            fig.fig_lluvia_julio(None, None, salida)
        self.assertIn("se saltea (falta el archivo)", err.getvalue())
        self.assertFalse(salida.exists())

    def test_serie_de_un_condado(self):
        import pandas as pd
        meses = [f"{a}-{m:02d}" for a in (2020, 2021, 2022) for m in range(1, 13)]
        agua = pd.DataFrame({"fips": "91001", "mes": meses, "sm_rootzone_m3m3": [0.2 + 0.001 * i for i in range(36)]})
        clima_m = pd.DataFrame({"fips": "91001", "mes": meses, "prec_imerg_mm": [50.0 + i for i in range(36)]})
        salida = self.tmp / "fig"
        with contextlib.redirect_stdout(io.StringIO()):
            fig.fig_serie_condado(agua, clima_m, salida, fips="91001", evento=("2021-05", "2021-08", "evento"),
                                  desde="2020-01", hasta="2022-12", nombre_condado="C91001")
        self.assertEqual([p.name for p in salida.iterdir()], ["fig8_county_monthly_smap_imerg.png"])
        with contextlib.redirect_stderr(io.StringIO()) as err:
            fig.fig_serie_condado(agua, clima_m, self.tmp / "otra", fips="92001")
        self.assertIn("el condado 92001 no tiene SMAP o IMERG", err.getvalue())
        self.assertFalse((self.tmp / "otra").exists())

    def test_nombre_de_condado_sale_del_zip(self):
        d = self.tmp / "datos-xa-xb"
        release(d)
        self.assertEqual(fig.nombre_de_condado([d], "92001"), "C92001")
        self.assertIsNone(fig.nombre_de_condado([d], "99999"))

    def test_mapas_por_condado_con_poligonos_inventados(self):
        import geopandas as gpd
        import pandas as pd
        from shapely.geometry import box
        pol = gpd.GeoDataFrame({"fips": FIPS}, geometry=[box(i, 0, i + 1, 1) for i in range(len(FIPS))],
                               crs=5070)
        rot = pd.DataFrame({"fips": FIPS, "anio": 2013, "pct_maiz_tras_maiz": [10.0, None, 60.0]})
        clima_m = pd.DataFrame({"fips": FIPS, "mes": "2013-07", "prec_imerg_mm": [80.0, 95.0, 120.0]})
        salida = self.tmp / "fig"
        with contextlib.redirect_stdout(io.StringIO()):
            fig.fig_mapas_condado(rot, clima_m, pol, salida)
        self.assertEqual([p.name for p in salida.iterdir()], ["fig7_county_maps_corn_after_corn_imerg.png"])
        with contextlib.redirect_stderr(io.StringIO()) as err:
            fig.fig_mapas_condado(rot, clima_m.assign(mes="2013-06"), pol, self.tmp / "otra")
        self.assertIn("no hay prec_imerg_mm de 2013-07", err.getvalue())
        with contextlib.redirect_stderr(io.StringIO()) as err:
            fig.fig_mapas_condado(rot, clima_m, None, self.tmp / "otra")
        self.assertIn("no hay polígonos", err.getvalue())
        self.assertFalse((self.tmp / "otra").exists())


if __name__ == "__main__":
    unittest.main()
