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


class TestPaquetesNoListados(BaseMerge):
    """CLAUDE.md §7: merge.py une *todos* los *_anual.csv, *_estatico.csv y *_mensual.csv (salvo lotes).

    merge.py tiene la lista de archivos fija (ANUALES, MENSUALES) y deja afuera los paquetes nuevos que ya
    tienen entregable en loop/spec/entregables.yaml (paisaje_anual, teledeteccion_anual, aptitud_estatico,
    nldas_mensual, ecostress_mensual, hidrologia_mensual, validacion_mensual...). Ver "Para decidir" del PR.
    """

    archivos = {
        **ARCHIVOS,
        "paisaje/paisaje_anual.csv": "fips,anio,pct_bosque\n" + "".join(f"{f},{a},5\n" for f in FIPS for a in ANIOS),
        "aptitud/aptitud_estatico.csv": "fips,aptitud_maiz\n" + "".join(f"{f},0.7\n" for f in FIPS),
        "nldas/nldas_mensual.csv": "fips,anio,mes,tmax_nldas_c\n"
        + "".join(f"{f},2020,2020-07,29.0\n" for f in FIPS),
    }

    @unittest.expectedFailure
    def test_anual_y_estatico_de_paquetes_nuevos(self) -> None:
        _, _, cols, _ = self.correr()
        self.assertIn("pct_bosque", cols)
        self.assertIn("aptitud_maiz", cols)

    @unittest.expectedFailure
    def test_mensual_de_paquetes_nuevos(self) -> None:
        _, _, _, cols = self.correr()
        self.assertIn("tmax_nldas_c", cols)


if __name__ == "__main__":
    unittest.main()
