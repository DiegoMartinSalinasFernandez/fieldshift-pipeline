"""Prueba de src/merge.py con CSV chicos e inventados de dos estados (Nebraska 31 y Kansas 20).

No usa datos reales: arma en una carpeta temporal un `data/processed/` falso y apunta `merge.PROC` ahí.

Correr:  python -X utf8 -m unittest tests/test_merge.py   (o con pytest, si está instalado)
"""
from __future__ import annotations

import csv
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import merge  # noqa: E402

# Dos condados por estado. 20001 empieza con 0 en la parte del condado: el texto no se tiene que perder.
NE = ["31001", "31003"]
KS = ["20001", "20003"]
FIPS = NE + KS
ANIOS = ["2020", "2021"]

ARCHIVOS = {
    # Base de tabla_anual: fips × anio × cultivo. 20003 no tiene soja en 2021 (falta la fila).
    "cultivos/produccion_anual.csv": (
        "fips,anio,cultivo,rend_bu_ac,flag_nass\n"
        + "".join(
            f"{f},{a},{c},{150 + i},\n"
            for i, f in enumerate(FIPS) for a in ANIOS for c in ("maiz", "soja")
            if not (f == "20003" and a == "2021" and c == "soja")
        )
    ),
    # Por fips × anio. 31003 no tiene 2021 (faltante → vacío). 20001/2020 trae una celda vacía de origen.
    "clima/clima_anual.csv": (
        "fips,anio,prec_temporada_mm\n"
        + "".join(
            f"{f},{a},{'' if (f, a) == ('20001', '2020') else f'{500 + i}.10'}\n"
            for i, f in enumerate(FIPS) for a in ANIOS if (f, a) != ("31003", "2021")
        )
    ),
    "cultivos/rotacion_anual.csv": (
        "fips,anio,pct_maiz\n" + "".join(f"{f},{a},40.0\n" for f in FIPS for a in ANIOS)
    ),
    # Columna que colisiona con clima_anual: tiene que renombrarse vegetacion_prec_temporada_mm.
    "vegetacion/fenologia_anual.csv": (
        "fips,anio,ndvi_max,prec_temporada_mm\n" + "".join(f"{f},{a},0.80,1\n" for f in FIPS for a in ANIOS)
    ),
    # Por estado: solo maíz, con valores distintos en cada estado para ver que se une por fips[:2].
    "cultivos/fenologia_estado.csv": (
        "fips_estado,anio,cultivo,doy_50_sembrado\n"
        "31,2020,maiz,120\n31,2021,maiz,121\n20,2020,maiz,110\n20,2021,maiz,111\n"
    ),
    # Estático por fips: 31003 no está (faltante → vacío en todos sus años).
    "suelo_terreno/suelo_terreno_estatico.csv": (
        "fips,aws0_100\n31001,180\n20001,150\n20003,0\n"
    ),
    # Mensuales: clima tiene 2020-07 y 2020-08; vegetación solo 2020-07; agua solo 2020-08 para KS.
    "clima/clima_mensual.csv": (
        "fips,anio,mes,tmax_c\n" + "".join(f"{f},2020,{m},30.5\n" for f in FIPS for m in ("2020-07", "2020-08"))
    ),
    "vegetacion/vegetacion_mensual.csv": (
        "fips,anio,mes,ndvi\n" + "".join(f"{f},2020,2020-07,0.75\n" for f in FIPS)
    ),
    "agua/agua_mensual.csv": (
        "fips,anio,mes,sm_rootzone_m3m3\n" + "".join(f"{f},2020,2020-08,0.30\n" for f in KS)
    ),
    # El paquete lotes tiene otra granularidad y no tiene que entrar en ninguna tabla.
    "lotes/lotes_anual.csv": "fips,id_lote,anio,pct_px_cultivo_principal\n31001,31001_1,2020,95\n",
    "lotes/clima_lote_mensual.csv": "fips,id_lote,anio,mes,prec_lote_mm\n31001,31001_1,2020,2020-07,80\n",
}


class BaseMerge(unittest.TestCase):
    archivos = ARCHIVOS

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.proc = Path(self._tmp.name) / "data" / "processed"
        for rel, txt in self.archivos.items():
            p = self.proc / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(txt, encoding="utf-8")
        self._proc_original = merge.PROC
        merge.PROC = self.proc

    def tearDown(self) -> None:
        merge.PROC = self._proc_original
        self._tmp.cleanup()

    def correr(self) -> tuple[list[dict[str, str]], list[dict[str, str]], list[str], list[str]]:
        """Corre merge.main() y devuelve las filas y encabezados de los CSV escritos (leídos como texto)."""
        with redirect_stdout(io.StringIO()):
            self.assertEqual(merge.main(), 0)
        out = []
        for nombre in ("tabla_anual.csv", "tabla_mensual.csv"):
            with open(self.proc / nombre, encoding="utf-8", newline="") as f:
                r = csv.DictReader(f)
                out.append((list(r), r.fieldnames))
        (anual, cols_a), (mensual, cols_m) = out
        return anual, mensual, cols_a, cols_m


class TestTablaAnual(BaseMerge):
    def setUp(self) -> None:
        super().setUp()
        self.anual, _, self.cols, _ = self.correr()
        self.por_clave = {(r["fips"], r["anio"], r["cultivo"]): r for r in self.anual}

    def test_una_fila_por_clave_y_mismas_filas_que_produccion(self) -> None:
        # merge.py arma tabla_anual con una fila por fips × anio × cultivo (la base es produccion_anual,
        # que es formato largo). Por fips × anio hay una fila por cultivo.
        claves = [(r["fips"], r["anio"], r["cultivo"]) for r in self.anual]
        self.assertEqual(len(claves), len(set(claves)))
        self.assertEqual(len(self.anual), 15)  # 4 fips × 2 años × 2 cultivos − 1 fila faltante
        self.assertNotIn(("20003", "2021", "soja"), self.por_clave)
        self.assertEqual(self.cols[:3], ["fips", "anio", "cultivo"])

    def test_columnas_de_todos_los_paquetes(self) -> None:
        for col in ("rend_bu_ac", "flag_nass", "prec_temporada_mm", "pct_maiz", "ndvi_max",
                    "doy_50_sembrado", "aws0_100"):
            self.assertIn(col, self.cols)
        self.assertNotIn("fips_estado", self.cols)

    def test_colision_de_nombres_se_renombra(self) -> None:
        self.assertIn("vegetacion_prec_temporada_mm", self.cols)
        r = self.por_clave[("31001", "2020", "maiz")]
        self.assertEqual(r["prec_temporada_mm"], "500.10")
        self.assertEqual(r["vegetacion_prec_temporada_mm"], "1")

    def test_archivo_por_estado_se_une_por_dos_primeros_digitos(self) -> None:
        for f in NE:
            self.assertEqual(self.por_clave[(f, "2020", "maiz")]["doy_50_sembrado"], "120")
            self.assertEqual(self.por_clave[(f, "2021", "maiz")]["doy_50_sembrado"], "121")
        for f in KS:
            self.assertEqual(self.por_clave[(f, "2020", "maiz")]["doy_50_sembrado"], "110")
            self.assertEqual(self.por_clave[(f, "2021", "maiz")]["doy_50_sembrado"], "111")
        # Soja no está en fenologia_estado: vacío.
        self.assertEqual(self.por_clave[("31001", "2020", "soja")]["doy_50_sembrado"], "")

    def test_estatico_se_repite_en_todos_los_anios(self) -> None:
        for a in ANIOS:
            self.assertEqual(self.por_clave[("31001", a, "maiz")]["aws0_100"], "180")
        # Un 0 real del origen se conserva como 0.
        self.assertEqual(self.por_clave[("20003", "2020", "maiz")]["aws0_100"], "0")

    def test_faltantes_quedan_vacios(self) -> None:
        # Fila que falta en clima_anual, condado que falta en suelo y celda vacía de origen.
        self.assertEqual(self.por_clave[("31003", "2021", "maiz")]["prec_temporada_mm"], "")
        self.assertEqual(self.por_clave[("31003", "2020", "soja")]["aws0_100"], "")
        self.assertEqual(self.por_clave[("20001", "2020", "maiz")]["prec_temporada_mm"], "")
        for r in self.anual:
            for c, v in r.items():
                self.assertNotIn(v.strip().lower(), ("nan", "none", "<na>", "-999", "-9999"), (c, r))
        # Ningún vacío se convirtió en 0: los 0 que hay vienen del origen (solo aws0_100 de 20003).
        ceros = {(r["fips"], c) for r in self.anual for c, v in r.items() if v in ("0", "0.0")}
        self.assertEqual(ceros, {("20003", "aws0_100")})

    def test_valores_se_copian_como_texto(self) -> None:
        r = self.por_clave[("20001", "2021", "maiz")]
        self.assertEqual(r["fips"], "20001")
        self.assertEqual(r["prec_temporada_mm"], "502.10")  # no "502.1"
        self.assertEqual(r["pct_maiz"], "40.0")             # no "40"

    def test_no_entra_lotes(self) -> None:
        self.assertNotIn("id_lote", self.cols)
        self.assertNotIn("pct_px_cultivo_principal", self.cols)

    def test_orden_por_fips_y_anio(self) -> None:
        claves = [(r["fips"], int(r["anio"]), r["cultivo"]) for r in self.anual]
        self.assertEqual(claves, sorted(claves))


class TestTablaMensual(BaseMerge):
    def setUp(self) -> None:
        super().setUp()
        _, self.mensual, _, self.cols = self.correr()
        self.por_clave = {(r["fips"], r["anio"], r["mes"]): r for r in self.mensual}

    def test_una_fila_por_fips_anio_mes(self) -> None:
        claves = [(r["fips"], r["anio"], r["mes"]) for r in self.mensual]
        self.assertEqual(len(claves), len(set(claves)))
        self.assertEqual(set(claves), {(f, "2020", m) for f in FIPS for m in ("2020-07", "2020-08")})
        self.assertEqual(self.cols[:3], ["fips", "anio", "mes"])

    def test_columnas_de_los_tres_paquetes(self) -> None:
        self.assertEqual(self.cols, ["fips", "anio", "mes", "tmax_c", "ndvi", "sm_rootzone_m3m3"])

    def test_union_externa_con_faltantes_vacios(self) -> None:
        self.assertEqual(self.por_clave[("31001", "2020", "2020-07")]["ndvi"], "0.75")
        self.assertEqual(self.por_clave[("31001", "2020", "2020-08")]["ndvi"], "")
        self.assertEqual(self.por_clave[("31001", "2020", "2020-08")]["sm_rootzone_m3m3"], "")
        self.assertEqual(self.por_clave[("20001", "2020", "2020-08")]["sm_rootzone_m3m3"], "0.30")
        for r in self.mensual:
            for v in r.values():
                self.assertNotIn(v.strip().lower(), ("nan", "none", "<na>", "0", "0.0"))

    def test_no_entra_lotes(self) -> None:
        self.assertNotIn("id_lote", self.cols)
        self.assertNotIn("prec_lote_mm", self.cols)


class TestMesSoloEnVegetacion(BaseMerge):
    """Un mes que no está en clima pero sí en vegetación también aparece (unión externa, no izquierda)."""

    archivos = {**ARCHIVOS, "vegetacion/vegetacion_mensual.csv": "fips,anio,mes,ndvi\n31001,2020,2020-09,0.5\n"}

    def test_mes_extra(self) -> None:
        _, mensual, _, _ = self.correr()
        r = [x for x in mensual if x["mes"] == "2020-09"]
        self.assertEqual(len(r), 1)
        self.assertEqual((r[0]["fips"], r[0]["ndvi"], r[0]["tmax_c"]), ("31001", "0.5", ""))


class TestDuplicados(BaseMerge):
    archivos = {**ARCHIVOS, "clima/clima_anual.csv": "fips,anio,prec_temporada_mm\n31001,2020,1\n31001,2020,2\n"}

    def test_clave_duplicada_corta(self) -> None:
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            merge.tabla_anual()


NUEVOS = {
    **ARCHIVOS,
    # Economía, por estado: granos y forrajes en dos archivos con flag_nass cada uno (choca con produccion).
    "economia/economia_anual.csv": (
        "fips_estado,anio,cultivo,precio_usd_bu,flag_nass\n"
        "31,2020,maiz,4.50,\n31,2021,maiz,5.00,(D)\n20,2020,maiz,4.40,\n20,2020,soja,10.10,\n"
    ),
    "economia/economia_forrajes_anual.csv": "fips_estado,anio,cultivo,precio_usd_ton,flag_nass\n31,2020,alfalfa,180,(D)\n",
    "paisaje/paisaje_anual.csv": "fips,anio,pct_bosque_nlcd\n" + "".join(f"{f},{a},5.0\n" for f in FIPS for a in ANIOS),
    # Teledetección trae frac_pixeles_validos: nombre genérico, lleva siempre el prefijo del paquete.
    "teledeteccion/teledeteccion_anual.csv": "fips,anio,ndvi_max_30m,frac_pixeles_validos\n31001,2020,0.85,0.9\n",
    # Censo: 31001 tiene 2017 y 2022 → 2020 y 2021 toman 2017. 20001 solo 2022 → 2020/2021 vacíos.
    "cultivos/practicas_censo.csv": (
        "fips,anio_censo,pct_cobertura,pct_riego\n31001,2017,3.0,40.0\n31001,2022,4.0,41.0\n"
        "31001,2012,1.0,30.0\n20001,2022,2.0,10.0\n"
    ),
    # Rotación por ventanas de 8 años: queda afuera (merge_faltantes.md §3).
    "cultivos/rotacion_secuencia.csv": "fips,ventana,pct_maiz_continuo\n31001,2013-2020,12.0\n",
    "nldas/nldas_mensual.csv": "fips,anio,mes,et_nldas_mm\n" + "".join(f"{f},2020,2020-07,90.0\n" for f in FIPS),
    # ECOSTRESS: frac_pixeles_validos también es genérico acá; tmax_c choca con clima → ecostress_tmax_c.
    "ecostress/ecostress_mensual.csv": "fips,anio,mes,lst_ecostress_c,tmax_c,frac_pixeles_validos\n31001,2020,2020-07,31.0,99,0.5\n",
}


class TestPaquetesNuevos(BaseMerge):
    """T136: economía, paisaje, teledetección, censo (as-of), NLDAS y ECOSTRESS."""

    archivos = NUEVOS

    def setUp(self) -> None:
        super().setUp()
        self.anual, self.mensual, self.cols_a, self.cols_m = self.correr()
        self.pa = {(r["fips"], r["anio"], r["cultivo"]): r for r in self.anual}
        self.pm = {(r["fips"], r["anio"], r["mes"]): r for r in self.mensual}

    def test_columnas_viejas_no_cambian(self) -> None:
        # Mismas columnas y en el mismo orden que sin los paquetes nuevos, y después las nuevas.
        self.assertEqual(self.cols_a[:9], ["fips", "anio", "cultivo", "rend_bu_ac", "flag_nass",
                                           "prec_temporada_mm", "pct_maiz", "ndvi_max",
                                           "vegetacion_prec_temporada_mm"])
        self.assertEqual(self.cols_m[:6], ["fips", "anio", "mes", "tmax_c", "ndvi", "sm_rootzone_m3m3"])
        self.assertEqual(len(self.anual), 15)

    def test_economia_un_solo_flag_y_por_estado(self) -> None:
        self.assertIn("economia_flag_nass", self.cols_a)
        self.assertFalse([c for c in self.cols_a if c.endswith(("_x", "_y"))])
        for f in NE:
            self.assertEqual(self.pa[(f, "2021", "maiz")]["precio_usd_bu"], "5.00")
            self.assertEqual(self.pa[(f, "2021", "maiz")]["economia_flag_nass"], "(D)")
        self.assertEqual(self.pa[("20003", "2020", "soja")]["precio_usd_bu"], "10.10")
        self.assertEqual(self.pa[("31001", "2020", "soja")]["precio_usd_bu"], "")
        self.assertIn("precio_usd_ton", self.cols_a)

    def test_paisaje_y_teledeteccion(self) -> None:
        self.assertEqual(self.pa[("20003", "2021", "maiz")]["pct_bosque_nlcd"], "5.0")
        self.assertIn("teledeteccion_frac_pixeles_validos", self.cols_a)
        self.assertNotIn("frac_pixeles_validos", self.cols_a)
        self.assertEqual(self.pa[("31001", "2020", "soja")]["teledeteccion_frac_pixeles_validos"], "0.9")
        self.assertEqual(self.pa[("31003", "2020", "maiz")]["ndvi_max_30m"], "")

    def test_censo_ultimo_menor_o_igual(self) -> None:
        r = self.pa[("31001", "2020", "maiz")]
        self.assertEqual((r["anio_censo_ref"], r["pct_riego"], r["pct_cobertura"]), ("2017", "40.0", "3.0"))
        self.assertEqual(self.pa[("31001", "2021", "soja")]["anio_censo_ref"], "2017")
        # Sin censo anterior: vacío (no se usa el de 2022, sería del futuro).
        r = self.pa[("20001", "2020", "maiz")]
        self.assertEqual((r["anio_censo_ref"], r["pct_riego"]), ("", ""))
        self.assertEqual(self.pa[("31003", "2020", "maiz")]["anio_censo_ref"], "")
        self.assertNotIn("anio_censo", self.cols_a)

    def test_rotacion_secuencia_queda_afuera(self) -> None:
        self.assertNotIn("ventana", self.cols_a)
        self.assertNotIn("pct_maiz_continuo", self.cols_a)

    def test_mensuales_nuevos(self) -> None:
        self.assertEqual(self.pm[("20003", "2020", "2020-07")]["et_nldas_mm"], "90.0")
        r = self.pm[("31001", "2020", "2020-07")]
        self.assertEqual((r["tmax_c"], r["ecostress_tmax_c"]), ("30.5", "99"))
        self.assertEqual(r["ecostress_frac_pixeles_validos"], "0.5")
        self.assertEqual(self.pm[("31001", "2020", "2020-08")]["lst_ecostress_c"], "")

    def test_orden_de_filas(self) -> None:
        claves = [(r["fips"], int(r["anio"]), r["cultivo"]) for r in self.anual]
        self.assertEqual(claves, sorted(claves))


class TestFaltanPaquetesNuevos(BaseMerge):
    """Sin los archivos nuevos, merge.py avisa y da las mismas tablas que antes."""

    def test_aviso_y_misma_salida(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            merge.main()
        for rel in ("economia/economia_anual.csv", "nldas/nldas_mensual.csv", "cultivos/practicas_censo.csv"):
            self.assertIn(f"falta {rel}", buf.getvalue())
        with open(self.proc / "tabla_anual.csv", encoding="utf-8") as f:
            self.assertEqual(f.readline().strip().split(",")[-1], "aws0_100")


class TestChoqueSinNombreLibre(unittest.TestCase):
    def test_error_en_vez_de_x_y(self) -> None:
        import pandas as pd
        df = pd.DataFrame({"fips": ["1"], "a": ["1"]})
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            merge.renombrar_colisiones(df, ["fips"], {"a", "p_a", "arch_a"}, "p", "arch")


if __name__ == "__main__":
    unittest.main()
