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
import verificar_entrega as ve  # noqa: E402

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


class EntornoEntregar(unittest.TestCase):
    """Repo temporal con datos inventados; sin pruebas propias."""

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
        p.write_bytes(txt.encode("utf-8"))  # bytes: en Windows write_text pasaría LF a CRLF

    def correr(self, *args: str) -> str:
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["entregar.py", "--solo-zip", *args]), \
                contextlib.redirect_stdout(out):
            en.main()
        return out.getvalue()

    def zip_de(self, paquete: str) -> Path:
        return self.repo / "data" / "entregas" / f"datos-oh-ks_{paquete}.zip"


class TestEntregarSoloZip(EntornoEntregar):

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

    def test_sha256_sale_con_lf(self):
        # bytes, no read_text: read_text convierte CRLF a LF y la prueba no vería el CR.
        # sha256sum -c de Linux rechaza el .sha256 con CR (pasó en el release datos-oh-ne-mn).
        self.correr("clima")
        z = self.zip_de("clima")
        crudo = z.with_name(z.name + ".sha256").read_bytes()
        self.assertNotIn(b"\r", crudo)
        self.assertTrue(crudo.endswith(b"\n"))
        self.assertEqual(crudo.count(b"\n"), 1)
        esperado = hashlib.sha256(z.read_bytes()).hexdigest()
        self.assertEqual(crudo, f"{esperado}  {z.name}\n".encode("utf-8"))

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

    def test_manifest_solo_filas_del_paquete(self):
        self.correr("clima")
        with zipfile.ZipFile(self.zip_de("clima")) as zf, zf.open("manifest.csv") as f:
            man = pd.read_csv(f, dtype=str, keep_default_na=False)
        self.assertEqual(set(man["paquete"]), {"clima"})

    def test_manifest_mismo_encabezado_orden_y_fin_de_linea(self):
        self.correr("clima")
        lineas = MANIFEST.splitlines(keepends=True)
        esperado = lineas[0] + "".join(l for l in lineas[1:] if l.startswith("clima,"))
        with zipfile.ZipFile(self.zip_de("clima")) as zf:
            crudo = zf.read("manifest.csv")
        self.assertNotIn(b"\r", crudo)
        self.assertEqual(crudo.decode("utf-8"), esperado)

    def test_manifest_paquete_sin_filas_solo_encabezado(self):
        self.escribir("data/processed/agua/agua_mensual.csv", MENSUAL)
        self.correr("agua")
        with zipfile.ZipFile(self.zip_de("agua")) as zf:
            self.assertEqual(zf.read("manifest.csv").decode("utf-8"), MANIFEST.splitlines(keepends=True)[0])

    def test_clave_en_manifest_corta_sin_mostrarla(self):
        secreto = "INVENTADO123secreto"
        for param in ("key", "api_key", "apikey", "token", "API_KEY", "access_token"):
            with self.subTest(param=param):
                self.escribir("manifest.csv", MANIFEST
                              + f"clima,data/raw/clima/d.json,NASA,POWER,v2,2026-11-15,"
                                f"https://power.example/d?x=1&{param}={secreto}\n")
                out, err = io.StringIO(), io.StringIO()
                with self.assertRaises(SystemExit) as e, contextlib.redirect_stderr(err):
                    self.correr("clima")
                msg = str(e.exception.code)
                self.assertIn("clima", msg)
                self.assertIn("consulta_o_url", msg)
                self.assertNotIn(secreto, msg)
                self.assertNotIn(secreto, err.getvalue())
                self.assertFalse(self.zip_de("clima").exists())

    def test_clave_de_otro_paquete_no_frena(self):
        # solo se revisan las filas del paquete que se entrega; la del otro tampoco entra al zip
        self.escribir("manifest.csv", MANIFEST
                      + "cultivos,data/raw/cultivos/e.json,USDA NASS,Quick Stats,1,2026-11-15,"
                        "https://nass.example/e?key=INVENTADO\n")
        self.correr("clima")
        with zipfile.ZipFile(self.zip_de("clima")) as zf:
            self.assertNotIn("INVENTADO", zf.read("manifest.csv").decode("utf-8"))

    def test_parametros_parecidos_no_son_clave(self):
        self.escribir("manifest.csv", MANIFEST
                      + "clima,data/raw/clima/f.json,NASA,POWER,v2,2026-11-15,"
                        "https://power.example/f?monkey=1&keyword=maiz&tokens_n=3\n")
        self.correr("clima")
        self.assertTrue(self.zip_de("clima").exists())

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


def escribir_gpkg(ruta: Path, fips_estado: list[tuple[str, str]], crs: int = 4326) -> None:
    """GeoPackage chico como el de src/base/process.py: un cuadrado por condado, capa `condados`."""
    import geopandas as gpd
    from shapely.geometry import box

    filas = [{"fips": f, "estado": e, "condado": f"C{f}", "lat_centroide": 40.5, "lon_centroide": -89.5 + i,
              "area_km2": 1000.0, "geometry": box(-90 + i, 40, -89 + i, 41)} for i, (f, e) in enumerate(fips_estado)]
    ruta.parent.mkdir(parents=True, exist_ok=True)
    gpd.GeoDataFrame(filas, crs="EPSG:4326").to_crs(crs).to_file(ruta, layer="condados", driver="GPKG")


class TestZipBase(EntornoEntregar):
    """`<etiqueta>_base.zip`: polígonos y referencia de los estados del release (OH y KS en estas pruebas)."""

    def setUp(self):
        super().setUp()
        # El gpkg y el csv traen además un condado de Indiana: no es de este release y no tiene que entrar.
        escribir_gpkg(self.repo / "data/reference/condados.gpkg",
                      [("39001", "OH"), ("39003", "OH"), ("20005", "KS"), ("18001", "IN")])
        self.escribir("data/reference/condados.csv",
                      "fips,estado,condado,lat_centroide,lon_centroide,area_km2\n"
                      "39001,OH,C39001,40.5,-89.5,1000.0\n39003,OH,C39003,40.5,-88.5,1000.0\n"
                      "20005,KS,C20005,40.5,-87.5,1000.0\n18001,IN,C18001,40.5,-86.5,1000.0\n")

    def test_arma_base_con_sha_y_contenido(self):
        salida = self.correr("clima")
        z = self.zip_de("base")
        self.assertTrue(z.exists())
        self.assertIn("datos-oh-ks_base.zip", salida)
        crudo = z.with_name(z.name + ".sha256").read_bytes()
        self.assertEqual(crudo, f"{hashlib.sha256(z.read_bytes()).hexdigest()}  {z.name}\n".encode("utf-8"))
        with zipfile.ZipFile(z) as zf:
            self.assertEqual(set(zf.namelist()), {"data/reference/condados.gpkg", "data/reference/condados.csv",
                                                  "data/reference/anios.csv", "README.md"})
            self.assertEqual(zf.read("data/reference/anios.csv").decode("utf-8"), ANIOS)
            cond = pd.read_csv(io.BytesIO(zf.read("data/reference/condados.csv")), dtype={"fips": str})
            self.assertEqual(sorted(cond["fips"]), ["20005", "39001", "39003"])
            readme = zf.read("README.md").decode("utf-8")
            self.assertIn("EPSG:4326", readme)
            self.assertIn("datos-oh-ks", readme)

    def test_gpkg_filtrado_a_los_estados_y_en_4326(self):
        import geopandas as gpd

        self.correr("clima")
        with zipfile.ZipFile(self.zip_de("base")) as zf:
            destino = Path(self.tmp.name) / "leido.gpkg"
            destino.write_bytes(zf.read("data/reference/condados.gpkg"))
        g = gpd.read_file(destino, layer="condados")
        self.assertEqual(g.crs.to_epsg(), 4326)
        self.assertEqual(sorted(g["fips"]), ["20005", "39001", "39003"])
        self.assertEqual(set(g["estado"]), {"OH", "KS"})
        self.assertTrue(g.geometry.notna().all())

    def test_gpkg_solo_de_estos_estados_va_tal_cual(self):
        gpkg = self.repo / "data/reference/condados.gpkg"
        gpkg.unlink()
        escribir_gpkg(gpkg, [("39001", "OH"), ("20005", "KS")])
        self.correr("clima")
        with zipfile.ZipFile(self.zip_de("base")) as zf:
            self.assertEqual(zf.read("data/reference/condados.gpkg"), gpkg.read_bytes())

    def test_los_zips_de_paquete_no_cambian(self):
        self.correr("clima")
        with zipfile.ZipFile(self.zip_de("clima")) as zf:
            self.assertNotIn("data/reference/condados.gpkg", zf.namelist())
            self.assertIn("data/reference/condados.csv", zf.namelist())

    def test_solo_base(self):
        self.correr("base")
        self.assertTrue(self.zip_de("base").exists())
        self.assertFalse(self.zip_de("clima").exists())

    def test_sin_gpkg_avisa_y_sigue(self):
        (self.repo / "data/reference/condados.gpkg").unlink()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.correr("clima")
        self.assertTrue(self.zip_de("clima").exists())
        self.assertFalse(self.zip_de("base").exists())
        self.assertIn("condados.gpkg", err.getvalue())

    def test_gpkg_sin_un_estado_corta(self):
        gpkg = self.repo / "data/reference/condados.gpkg"
        gpkg.unlink()
        escribir_gpkg(gpkg, [("39001", "OH")])
        with self.assertRaises(SystemExit) as e:
            self.correr("clima")
        self.assertIn("KS", str(e.exception.code))

    def test_gpkg_en_otro_crs_corta(self):
        gpkg = self.repo / "data/reference/condados.gpkg"
        gpkg.unlink()
        escribir_gpkg(gpkg, [("39001", "OH"), ("20005", "KS")], crs=5070)
        with self.assertRaises(SystemExit) as e:
            self.correr("clima")
        self.assertIn("4326", str(e.exception.code))

    def test_verificar_entrega_da_apto_al_zip_de_base(self):
        self.correr("clima")
        informes = ve.verificar([self.zip_de("base")])
        self.assertEqual(len(informes), 1)
        self.assertTrue(informes[0].apto, informes[0].markdown())
        self.assertEqual(informes[0].paquete, "base")

    def test_unir_estados_ignora_el_zip_de_base(self):
        self.correr("clima")
        base = self.repo / "data" / "entregas"
        rel = base / "datos-oh-ks"
        rel.mkdir()
        for p in base.glob("datos-oh-ks_*"):
            p.rename(rel / p.name)
        self.assertEqual(set(ue.zips_de("datos-oh-ks", rel)), {"clima"})
        r = ue.unir(["datos-oh-ks"], base, Path(self.tmp.name) / "unido", bajar_releases=False)
        self.assertIn("clima/clima_anual.csv", r)
        self.assertFalse(any(k.startswith("base/") for k in r))


class NotasRelease(unittest.TestCase):
    """Notas del release (T122): paquetes y declaración de IA leída del README, sin red."""

    README = ("# Repo\n\n## Use of AI\n\nWritten by AI agents (see [`MAQUINAS.md`](MAQUINAS.md)).\n"
              "**The data are not generated by AI**.\n\n---\n\n# Repo (castellano)\n\n"
              "## Uso de IA\n\nLo escribieron agentes de IA.\nLos datos no los genera la IA.\n\n## Otra\n\nnada\n")

    def test_arma_notas_bilingues_con_paquetes(self):
        n = en.notas_release(["OH", "NE"], ["cultivos", "clima"], self.README)
        self.assertIn("## Use of AI\n\nWritten by AI agents (see `MAQUINAS.md`). **The data are not generated "
                      "by AI**.", n)
        self.assertIn("## Uso de IA\n\nLo escribieron agentes de IA. Los datos no los genera la IA.\n", n)
        self.assertIn("- `clima`\n- `cultivos`", n)
        self.assertIn("OH, NE", n)
        self.assertNotIn("nada", n)       # corta en el encabezado siguiente
        self.assertNotIn("castellano", n)  # y en el `---`

    def test_sigue_al_readme(self):
        otro = self.README.replace("Written by AI agents", "Texto nuevo")
        self.assertIn("Texto nuevo", en.notas_release(["KS"], ["clima"], otro))

    def test_falta_seccion_corta(self):
        with self.assertRaises(SystemExit):
            en.notas_release(["KS"], ["clima"], self.README.replace("## Uso de IA", "## Otra cosa"))

    def test_readme_real_tiene_las_dos_secciones(self):
        n = en.notas_release(["KS"], [], (REPO / "README.md").read_text(encoding="utf-8"))
        self.assertIn("Anthropic Claude", n.split("## Uso de IA")[0])
        self.assertIn("Anthropic Claude", n.split("## Uso de IA")[1])

    def test_notas_con_atribucion_de_lotes_y_validacion(self):
        from src.common.atribuciones import COCORAHS_CC_BY, COPERNICUS_HLS
        n = en.notas_release(["IA"], ["lotes", "validacion", "clima"], self.README)
        self.assertIn("## Attribution / Atribución", n)
        self.assertIn(f"- `lotes`: {COPERNICUS_HLS}", n)
        self.assertIn(f"- `validacion`: {COCORAHS_CC_BY}", n)
        self.assertLess(n.index("## Attribution"), n.index("## Use of AI"))

    def test_notas_sin_atribucion(self):
        self.assertNotIn("Attribution", en.notas_release(["KS"], ["clima", "agua"], self.README))

    def test_paquetes_de_assets(self):
        nombres = ["datos-oh-ne-mn_clima.zip", "datos-oh-ne-mn_clima.zip.sha256", "datos-oh-ne-mn_agua.zip",
                   "otro_suelo.zip"]
        self.assertEqual(en.paquetes_de_assets("datos-oh-ne-mn", nombres), ["agua", "clima"])
        self.assertFalse(en.tiene_base("datos-oh-ne-mn", nombres))

    def test_paquetes_de_assets_sin_base(self):
        nombres = ["datos-ks_clima.zip", "datos-ks_base.zip", "datos-ks_base.zip.sha256"]
        self.assertEqual(en.paquetes_de_assets("datos-ks", nombres), ["clima"])
        self.assertTrue(en.tiene_base("datos-ks", nombres))

    def test_notas_con_y_sin_base(self):
        sin = en.notas_release(["KS"], ["clima"], self.README)
        self.assertNotIn("_base.zip", sin)
        con = en.notas_release(["KS"], ["clima"], self.README, "datos-ks_base.zip")
        self.assertIn("## Reference / Referencia\n\n`datos-ks_base.zip`", con)
        self.assertIn("condados.gpkg", con)
        self.assertNotIn("`base`", con)           # no aparece como paquete
        self.assertLess(con.index("## Reference"), con.index("## Use of AI"))

    def test_subir_crea_y_edita_notas(self):
        llamadas = []

        def falso_gh(*args, check=True):
            llamadas.append(args)
            out = "datos-ks_agua.zip\ndatos-ks_agua.zip.sha256\n" if args[:2] == ("release", "view") and \
                "--json" in args else ""
            rc = 1 if args[:2] == ("release", "view") and "--json" not in args else 0
            return mock.Mock(returncode=rc, stdout=out, stderr="")

        with mock.patch.object(en, "gh", falso_gh), contextlib.redirect_stdout(io.StringIO()):
            en.subir("datos-ks", [Path("/tmp/datos-ks_clima.zip")], ["KS"])
        crear = next(a for a in llamadas if a[:2] == ("release", "create"))
        editar = next(a for a in llamadas if a[:2] == ("release", "edit"))
        self.assertIn("## Use of AI", crear[crear.index("--notes") + 1])
        notas = editar[editar.index("--notes") + 1]
        self.assertIn("- `agua`\n- `clima`", notas)
        self.assertIn("## Uso de IA", notas)
        self.assertNotIn("_base.zip", notas)

    def test_subir_con_base_la_nombra_en_las_notas(self):
        llamadas = []

        def falso_gh(*args, check=True):
            llamadas.append(args)
            out = "datos-ks_agua.zip\ndatos-ks_base.zip\n" if "--json" in args else ""
            return mock.Mock(returncode=0, stdout=out, stderr="")

        with mock.patch.object(en, "gh", falso_gh), contextlib.redirect_stdout(io.StringIO()):
            en.subir("datos-ks", [Path("/tmp/datos-ks_base.zip")], ["KS"])
        subida = next(a for a in llamadas if a[:2] == ("release", "upload"))
        self.assertIn(str(Path("/tmp/datos-ks_base.zip.sha256")), subida)
        editar = next(a for a in llamadas if a[:2] == ("release", "edit"))
        notas = editar[editar.index("--notes") + 1]
        self.assertIn("- `agua`", notas)
        self.assertNotIn("- `base`", notas)
        self.assertIn("`datos-ks_base.zip`", notas)


if __name__ == "__main__":
    unittest.main()
