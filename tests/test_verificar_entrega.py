"""Prueba de scripts/verificar_entrega.py con zips chicos armados a mano (estados y datos inventados).

Correr:  python -X utf8 -m unittest tests/test_verificar_entrega.py   (o con pytest, si está instalado)
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

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import verificar_entrega as ve  # noqa: E402

# Condados de Kansas (20) y Nebraska (31) con ceros a la izquierda; no hace falta que existan de verdad.
FIPS = ["20001", "20003", "31005"]
CONDADOS = "fips,estado,condado\n" + "".join(f"{f},XX,C{f}\n" for f in FIPS)
ANIOS = "anio,inicio_temporada,fin_temporada\n2020,2020-04-01,2020-09-30\n2021,2021-04-01,2021-09-30\n"
MANIFEST = "paquete,archivo,fuente,producto,version,fecha_descarga,consulta_o_url\n"

ANUAL = "fips,anio,prec_temporada_mm,ndvi\n" + "".join(
    f"{f},{a},{400 + i},0.{5 + i}\n" for i, f in enumerate(FIPS) for a in (2020, 2021))
MENSUAL = "fips,anio,mes,tmax_c\n" + "".join(f"{f},2020,2020-0{m},2{m}.5\n" for f in FIPS for m in (6, 7))
PRODUCCION = "fips,anio,cultivo,rend_bu_ac,flag_nass\n" + "".join(
    f"{f},2020,{c},{r},\n" for f in FIPS for c, r in (("maiz", 180), ("soja", 55))) + "20001,2021,maiz,,(D)\n"
FENOLOGIA = "fips_estado,anio,cultivo,doy_50_sembrado\n20,2020,maiz,120\n31,2020,maiz,118\n"


def card(paquete: str, filas: list[tuple[str, str]]) -> str:
    cuerpo = "".join(f"| {a} | {c} | algo | u | fuente | X01 | 2020 | 2021 | 0.0 |\n" for a, c in filas)
    return (f"# Data card — {paquete}\n\n## Columnas\n\n"
            "| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |\n"
            "|---|---|---|---|---|---|---|---|---|\n" + cuerpo + "\n## Supuestos\n\n- ninguno\n")


CARD_CLIMA = card("clima", [("clima_anual.csv", "prec_temporada_mm"), ("clima_anual.csv", "ndvi"),
                            ("clima_mensual.csv", "tmax_c")])
CARD_CULTIVOS = card("cultivos", [("produccion_anual.csv", "rend_bu_ac"), ("produccion_anual.csv", "flag_nass"),
                                  ("fenologia_estado.csv", "doy_50_sembrado")])


def armar(carpeta: Path, paquete: str, archivos: dict[str, str | bytes], *, data_card: str | None = None,
          condados: str | None = CONDADOS, sha: str = "ok", nombre: str | None = None) -> Path:
    """Arma un zip como el de entregar.py. sha: 'ok', 'malo' o 'no' (sin .sha256)."""
    carpeta.mkdir(parents=True, exist_ok=True)
    z = carpeta / (nombre or f"datos-ks-ne_{paquete}.zip")
    with zipfile.ZipFile(z, "w") as zf:
        for n, txt in archivos.items():
            zf.writestr(f"data/processed/{paquete}/{n}", txt)
        if data_card is not None:
            zf.writestr(f"docs/datasets/{paquete}.md", data_card)
        if condados is not None:
            zf.writestr("data/reference/condados.csv", condados)
        zf.writestr("data/reference/anios.csv", ANIOS)
        zf.writestr("manifest.csv", MANIFEST)
    if sha == "no":
        z.with_suffix(".zip.sha256").unlink(missing_ok=True)
    else:
        h =hashlib.sha256(z.read_bytes()).hexdigest() if sha == "ok" else "0" * 64
        z.with_suffix(".zip.sha256").write_text(f"{h}  {z.name}\n", encoding="utf-8")
    return z


def armar_base(carpeta: Path, fips: list[str] = FIPS, *, fips_csv: list[str] | None = None, crs: int = 4326,
               con_gpkg: bool = True, sha: str = "ok", nombre: str = "datos-ks-ne_base.zip") -> Path:
    """Zip de base como el de entregar.py: condados.gpkg (un cuadrado por condado), condados.csv y anios.csv."""
    import geopandas as gpd
    from shapely.geometry import box

    carpeta.mkdir(parents=True, exist_ok=True)
    z = carpeta / nombre
    gpkg = carpeta / "tmp_condados.gpkg"
    gpd.GeoDataFrame({"fips": fips, "estado": ["XX"] * len(fips)},
                     geometry=[box(-90 + i, 40, -89 + i, 41) for i in range(len(fips))],
                     crs="EPSG:4326").to_crs(crs).to_file(gpkg, layer="condados", driver="GPKG")
    with zipfile.ZipFile(z, "w") as zf:
        if con_gpkg:
            zf.write(gpkg, "data/reference/condados.gpkg")
        zf.writestr("data/reference/condados.csv",
                    "fips,estado,condado\n" + "".join(f"{f},XX,C{f}\n" for f in (fips_csv or fips)))
        zf.writestr("data/reference/anios.csv", ANIOS)
        zf.writestr("README.md", "# base\n")
    gpkg.unlink()
    h = hashlib.sha256(z.read_bytes()).hexdigest() if sha == "ok" else "0" * 64
    z.with_suffix(".zip.sha256").write_text(f"{h}  {z.name}\n", encoding="utf-8")
    return z


class TestZipBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def uno(self, z: Path) -> ve.Informe:
        informes = ve.verificar([z])
        self.assertEqual(len(informes), 1)
        return informes[0]

    def test_base_bueno(self):
        inf = self.uno(armar_base(self.dir))
        self.assertTrue(inf.apto, inf.markdown())
        self.assertEqual(inf.paquete, "base")
        self.assertIn(("condados.gpkg", 3, 3), inf.archivos)

    def test_base_junto_a_paquetes(self):
        zips = [armar_base(self.dir), armar(self.dir, "clima", {"clima_anual.csv": ANUAL,
                                                               "clima_mensual.csv": MENSUAL}, data_card=CARD_CLIMA)]
        informes = ve.verificar(zips)
        self.assertEqual([i.paquete for i in informes], ["base", "clima"])
        self.assertTrue(all(i.apto for i in informes), [i.markdown() for i in informes])

    def test_base_sin_gpkg(self):
        inf = self.uno(armar_base(self.dir, con_gpkg=False))
        self.assertFalse(inf.apto)
        self.assertIn("falta data/reference/condados.gpkg", "\n".join(inf.problemas))

    def test_base_otro_crs(self):
        inf = self.uno(armar_base(self.dir, crs=5070))
        self.assertIn("EPSG:4326", "\n".join(inf.problemas))

    def test_base_fips_distintos_del_csv(self):
        inf = self.uno(armar_base(self.dir, fips_csv=FIPS[:2] + ["31999"]))
        todo = "\n".join(inf.problemas)
        self.assertIn("no tienen los mismos fips", todo)
        self.assertIn("31005", todo)

    def test_base_fips_mal_escrito_y_repetido(self):
        inf = self.uno(armar_base(self.dir, fips=["20001", "20001", "2003"]))
        todo = "\n".join(inf.problemas)
        self.assertIn("5 dígitos", todo)
        self.assertIn("repetidos", todo)

    def test_base_sha_malo(self):
        inf = self.uno(armar_base(self.dir, sha="malo"))
        self.assertIn("sha256 no coincide", "\n".join(inf.problemas))


class TestVerificarEntrega(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def clima(self, **cambios) -> Path:
        archivos = {"clima_anual.csv": ANUAL, "clima_mensual.csv": MENSUAL}
        archivos.update(cambios.pop("archivos", {}))
        return armar(self.dir, "clima", archivos, data_card=cambios.pop("data_card", CARD_CLIMA), **cambios)

    def uno(self, z: Path) -> ve.Informe:
        informes = ve.verificar([z])
        self.assertEqual(len(informes), 1)
        return informes[0]

    def assertNoApto(self, z: Path, *textos: str) -> ve.Informe:
        inf = self.uno(z)
        self.assertFalse(inf.apto, inf.markdown())
        todo = "\n".join(inf.problemas)
        for t in textos:
            self.assertIn(t, todo)
        return inf

    # --- entregas buenas ---

    def test_zip_bueno(self):
        inf = self.uno(self.clima())
        self.assertTrue(inf.apto, inf.markdown())
        self.assertEqual(inf.paquete, "clima")
        self.assertEqual(inf.archivos, [("clima_anual.csv", 6, 4), ("clima_mensual.csv", 6, 4)])
        self.assertIn("APTO", inf.markdown().splitlines()[0])

    def test_formato_largo_con_flag_nass_y_fips_estado(self):
        z = armar(self.dir, "cultivos", {"produccion_anual.csv": PRODUCCION, "fenologia_estado.csv": FENOLOGIA},
                  data_card=CARD_CULTIVOS)
        inf = self.uno(z)
        self.assertTrue(inf.apto, inf.markdown())  # (D) en flag_nass es válido; cultivo es clave

    def test_no_depende_de_los_estados_de_la_maquina(self):
        # Una máquina con FIELDSHIFT_ESTADOS=OH controla una entrega de KS y NE.
        previo = os.environ.get("FIELDSHIFT_ESTADOS")
        os.environ["FIELDSHIFT_ESTADOS"] = "OH"
        try:
            z = armar(self.dir, "cultivos", {"fenologia_estado.csv": FENOLOGIA}, data_card=CARD_CULTIVOS)
            self.assertTrue(self.uno(z).apto)
            self.assertEqual(os.environ["FIELDSHIFT_ESTADOS"], "OH")
        finally:
            if previo is None:
                os.environ.pop("FIELDSHIFT_ESTADOS", None)
            else:
                os.environ["FIELDSHIFT_ESTADOS"] = previo

    def test_carpeta_unida(self):
        unido = self.dir / "unido"
        (unido / "clima").mkdir(parents=True)
        (unido / "clima" / "clima_anual.csv").write_text(ANUAL, encoding="utf-8")
        (unido / "clima" / "datos-ks-ne.md").write_text(CARD_CLIMA, encoding="utf-8")
        (unido / "condados.csv").write_text(CONDADOS, encoding="utf-8")
        inf = self.uno(unido / "clima")
        self.assertTrue(inf.apto, inf.markdown())
        self.assertEqual(inf.paquete, "clima")

    # --- un zip por tipo de error ---

    def test_no_utf8(self):
        latin = ANUAL.replace("prec_temporada_mm", "precipitación_mm").encode("latin-1")
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": latin}), "no es UTF-8")

    def test_bom(self):
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": b"\xef\xbb\xbf" + ANUAL.encode()}), "BOM")

    def test_separador_punto_y_coma(self):
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": ANUAL.replace(",", ";")}), "separador")

    def test_sin_encabezado(self):
        sin = "\n".join(ANUAL.splitlines()[1:]) + "\n"
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": sin}), "encabezado")

    def test_no_snake_case(self):
        malo = ANUAL.replace("prec_temporada_mm", "PrecTemporada mm")
        card_malo = CARD_CLIMA.replace("prec_temporada_mm", "PrecTemporada mm")
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": malo}, data_card=card_malo), "snake_case")

    def test_claves_no_primero(self):
        malo = "anio,fips,prec_temporada_mm,ndvi\n" + "".join(
            f"{a},{f},400,0.5\n" for f in FIPS for a in (2020, 2021))
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": malo}), "primeras columnas")

    def test_fips_sin_ceros(self):
        malo = ANUAL.replace("20001,", "2001,")
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": malo}), "5 dígitos")

    def test_anio_no_entero(self):
        malo = ANUAL.replace(",2020,", ",2020.0,")
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": malo}), "años enteros")

    def test_fecha_y_mes_mal_escritos(self):
        diario = "fips,anio,fecha,tmax_c\n20001,2020,15/07/2020,30\n"
        card_d = CARD_CLIMA + card("clima", [("clima_diario.csv", "tmax_c")])
        self.assertNoApto(self.clima(archivos={"clima_diario.csv": diario}, data_card=card_d), "YYYY-MM-DD")
        mensual = MENSUAL.replace("2020-06", "2020-6")
        self.assertNoApto(self.clima(archivos={"clima_mensual.csv": mensual}), "YYYY-MM")

    def test_faltantes_como_texto(self):
        for relleno in ("-999", "-9999", "NaN", "nan", "None", "(D)"):
            with self.subTest(relleno=relleno):
                malo = ANUAL.replace(",0.5\n", f",{relleno}\n", 1)
                inf = self.assertNoApto(self.clima(archivos={"clima_anual.csv": malo}), "faltantes escritos")
                self.assertIn(relleno, "\n".join(inf.problemas))

    def test_claves_duplicadas(self):
        malo = ANUAL + "20001,2020,999,0.1\n"
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": malo}), "duplicada")

    def test_fips_que_no_esta_en_condados(self):
        malo = ANUAL + "19169,2020,500,0.4\n"
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": malo}), "19169", "condados.csv")

    def test_sin_condados(self):
        self.assertNoApto(self.clima(condados=None), "falta condados.csv")

    def test_fuera_de_rango_fisico(self):
        malo = ANUAL.replace(",0.5\n", ",1.7\n", 1).replace(",400,", ",-3,", 1)
        self.assertNoApto(self.clima(archivos={"clima_anual.csv": malo}), "ndvi", "prec_temporada_mm", "rango")

    def test_decimal_con_coma(self):
        malo = MENSUAL.replace("26.5", '"26,5"')
        self.assertNoApto(self.clima(archivos={"clima_mensual.csv": malo}), "coma")

    def test_columna_sin_fila_en_data_card(self):
        malo = ANUAL.replace("ndvi\n", "ndvi,evi\n", 1).replace("\n", ",0.3\n").replace("ndvi,0.3", "ndvi")
        inf = self.assertNoApto(self.clima(archivos={"clima_anual.csv": malo}), "data card", "evi")
        self.assertNotIn("fips", "\n".join(p for p in inf.problemas if "data card" in p))

    def test_sin_data_card(self):
        self.assertNoApto(self.clima(data_card=None), "falta el data card")

    def test_sha256_malo(self):
        self.assertNoApto(self.clima(sha="malo"), "sha256")
        self.assertTrue(self.uno(self.clima(sha="no")).apto)  # sin .sha256 al lado no se controla

    def escribir_sha(self, z: Path, fin: bytes, h: str | None = None) -> None:
        """Escribe el .sha256 en bytes (write_text en Windows pasaría LF a CRLF)."""
        h = h or hashlib.sha256(z.read_bytes()).hexdigest()
        z.with_suffix(".zip.sha256").write_bytes(f"{h}  {z.name}".encode("utf-8") + fin)

    def test_sha256_con_lf_y_con_crlf(self):
        # El release datos-oh-ne-mn tiene .sha256 con CRLF (hechos en Windows); los nuevos salen con LF.
        for nombre, fin in (("LF", b"\n"), ("CRLF", b"\r\n")):
            with self.subTest(fin=nombre):
                z = self.clima()
                self.escribir_sha(z, fin)
                self.assertEqual(z.with_suffix(".zip.sha256").read_bytes().endswith(b"\r\n"), nombre == "CRLF")
                inf = self.uno(z)
                self.assertTrue(inf.apto, inf.markdown())
                self.assertNotIn("sha256", "\n".join(inf.problemas))

    def test_sha256_malo_con_crlf_igual_se_detecta(self):
        z = self.clima()
        self.escribir_sha(z, b"\r\n", h="0" * 64)
        self.assertNoApto(z, "sha256")

    def test_sha256_en_mayusculas_con_crlf(self):
        z = self.clima()
        self.escribir_sha(z, b"\r\n", h=hashlib.sha256(z.read_bytes()).hexdigest().upper())
        self.assertTrue(self.uno(z).apto)

    # --- línea de comandos ---

    def test_main_codigo_de_salida_e_informes(self):
        bueno = self.clima(nombre="datos-ks-ne_clima.zip")
        malo = armar(self.dir, "cultivos", {"produccion_anual.csv": PRODUCCION + "20001,2020,maiz,180,\n"},
                     data_card=CARD_CULTIVOS)
        salida = self.dir / "informes"
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(ve.main([str(bueno), "--salida", str(salida)]), 0)
            self.assertEqual(ve.main([str(bueno), str(malo), "--salida", str(salida)]), 1)
        self.assertIn("1 APTO, 1 NO APTO", out.getvalue())
        self.assertIn("NO APTO", (salida / "datos-ks-ne_cultivos.md").read_text(encoding="utf-8"))
        self.assertIn("— APTO", (salida / "datos-ks-ne_clima.md").read_text(encoding="utf-8"))

    def test_ruta_inexistente(self):
        self.assertFalse(self.uno(self.dir / "no_existe.zip").apto)


if __name__ == "__main__":
    unittest.main()
