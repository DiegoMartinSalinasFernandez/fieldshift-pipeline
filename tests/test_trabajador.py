"""Pruebas de scripts/trabajador.py en las partes que no lanzan a Claude: qué tarea toma y con cuánto tiempo.

Se importa el script en el mismo proceso y se apunta el tablero (tareas.py) a una carpeta temporal con tareas
inventadas. No se usa git ni GitHub: `tareas.traer` y `tareas.publicar` se reemplazan durante cada prueba.

Correr:  python -X utf8 -m unittest tests/test_trabajador.py   (o con pytest, si está instalado)
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import tareas  # noqa: E402
import trabajador  # noqa: E402

MAQUINAS_YAML = """maquinas:
  max-1: {plan: max, estados: [IA]}
  pro-1: {plan: pro, estados: [OH, MN]}
"""


def tarea(tid: str, estado: str = "libre", plan: str = "pro", estados: list[str] | None = None,
          depende: list[str] | None = None, **extra) -> str:
    meta = {"id": tid, "titulo": f"Tarea {tid}", "estado": estado, "plan_minimo": plan,
            "maquina": None if estado == "libre" else "otra", "estados": estados or [],
            "depende_de": depende or [], "rama": None,
            "creada": "2026-11-15 00:00", "actualizada": "2026-11-15 00:00", **extra}
    enc = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{enc}\n---\n\n## Qué hacer\n\nAlgo.\n\n## Notas\n"


class Tablero(unittest.TestCase):
    """Tablero inventado en una carpeta temporal; `self.poner(...)` agrega tareas."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="test_trabajador_")
        self.base = Path(self._tmp.name)
        (self.base / "coordinacion" / "tareas").mkdir(parents=True)
        (self.base / "coordinacion" / "maquinas.yaml").write_text(MAQUINAS_YAML, encoding="utf-8")
        self.publicado: list[str] = []
        self.logs: list[str] = []
        viejo = tareas.BASE
        self.addCleanup(tareas.usar_base, viejo)
        for parche in (
            mock.patch.object(tareas, "traer", lambda sin_git: tareas.usar_base(self.base)),
            mock.patch.object(tareas, "publicar", lambda rutas, msj, sin_git: self.publicado.append(msj)),
            mock.patch.object(trabajador, "log", self.logs.append),
        ):
            parche.start()
            self.addCleanup(parche.stop)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def poner(self, tid: str, crlf: bool = False, **kw) -> None:
        txt = tarea(tid, **kw)
        # newline="\n": que en Windows no se conviertan los saltos; con crlf=True se escriben \r\n a propósito
        (self.base / "coordinacion" / "tareas" / f"{tid}-x.md").write_text(
            txt.replace("\n", "\r\n") if crlf else txt, encoding="utf-8", newline="\n")

    def orden(self, maquina: str, plan: str, estados: list[str], solo: str | None = None) -> list[str]:
        """Orden en que el trabajador intentaría tomar las tareas (todas las tomas fallan a propósito)."""
        intentos: list[str] = []

        def tomar_falla(a: argparse.Namespace) -> None:
            intentos.append(a.id)
            sys.exit("ocupada (prueba)")

        with mock.patch.object(tareas, "cmd_tomar", tomar_falla):
            self.assertIsNone(trabajador.elegir_y_tomar(maquina, plan, estados, solo))
        return intentos


class OrdenDeCandidatas(Tablero):

    def setUp(self) -> None:
        super().setUp()
        self.poner("T001")
        self.poner("T002", estados=["IA"])
        self.poner("T003", plan="max")
        self.poner("T004", plan="max", estados=["IA"])
        self.poner("T005", estados=["OH"])

    def test_max_prefiere_max_despues_estados_despues_numero(self) -> None:
        self.assertEqual(self.orden("max-1", "max", ["IA"]), ["T004", "T003", "T002", "T001", "T005"])

    def test_pro_no_toma_max_y_prefiere_sus_estados(self) -> None:
        self.assertEqual(self.orden("pro-1", "pro", ["OH", "MN"]), ["T005", "T001", "T002"])

    def test_sin_estados_va_por_numero(self) -> None:
        self.assertEqual(self.orden("pro-1", "pro", []), ["T001", "T002", "T005"])

    def test_solo_una_tarea(self) -> None:
        self.assertEqual(self.orden("max-1", "max", ["IA"], solo="t002"), ["T002"])

    def test_si_una_toma_falla_prueba_la_siguiente(self) -> None:
        self.assertEqual(self.orden("pro-1", "pro", ["OH"]), ["T005", "T001", "T002"])
        self.assertTrue(any("no pude tomar T005" in x for x in self.logs))

    def test_toma_la_primera_y_la_deja_tomada(self) -> None:
        tid, meta, texto = trabajador.elegir_y_tomar("pro-1", "pro", ["OH"], None)
        self.assertEqual(tid, "T005")
        self.assertEqual(meta["estado"], "tomada")
        self.assertEqual(meta["maquina"], "pro-1")
        self.assertIn("pro-1: tomada", texto)
        self.assertEqual(self.publicado, ["tarea T005: tomada por pro-1"])


class TareasQueNoSeToman(Tablero):

    def test_estados_no_libres(self) -> None:
        for i, estado in enumerate(("espera", "tomada", "hecha", "bloqueada"), start=1):
            self.poner(f"T00{i}", estado=estado)
        self.poner("T009")
        self.assertEqual(self.orden("max-1", "max", []), ["T009"])

    def test_auto_false(self) -> None:
        self.poner("T001", auto=False)
        self.poner("T002", auto=True)
        self.assertEqual(self.orden("pro-1", "pro", []), ["T002"])

    def test_dependencias(self) -> None:
        self.poner("T001", estado="hecha")
        self.poner("T002", estado="tomada")
        self.poner("T003", depende=["T001"])            # su dependencia está hecha: se puede
        self.poner("T004", depende=["T002"])            # tomada no es hecha
        self.poner("T005", depende=["T001", "T002"])    # falta una
        self.poner("T006", depende=["T099"])            # no existe
        self.assertEqual(self.orden("pro-1", "pro", []), ["T003"])

    def test_sin_candidatas_no_intenta_nada(self) -> None:
        self.poner("T001", plan="max")
        self.poner("T002", estado="hecha")
        self.assertEqual(self.orden("pro-1", "pro", ["OH"]), [])

    def test_archivo_con_crlf(self) -> None:
        # una copia en Windows con core.autocrlf deja las tareas con \r\n
        self.poner("T001", crlf=True, estado="hecha")
        self.poner("T002", crlf=True, depende=["T001"])
        self.assertEqual(self.orden("pro-1", "pro", []), ["T002"])


class TopeDeMinutos(unittest.TestCase):
    AHORA = dt.datetime(2026, 11, 15, 12, 0)

    def minutos(self, meta: dict, quedan_min: float, cli: float | None = None, plan_min: float = 60) -> float:
        a = argparse.Namespace(minutos_tarea=cli if cli is not None else plan_min, minutos_cli=cli is not None)
        fin = self.AHORA + dt.timedelta(minutes=quedan_min)
        with mock.patch.object(trabajador, "ahora", lambda: self.AHORA):
            return trabajador.minutos_para(meta, a, fin)

    def test_sin_minutos_usa_el_del_plan(self) -> None:
        self.assertEqual(self.minutos({}, 300), 60)
        self.assertEqual(self.minutos({}, 300, plan_min=150), 150)

    def test_minutos_de_la_tarea_mandan(self) -> None:
        self.assertEqual(self.minutos({"minutos": 200}, 300), 200)
        self.assertEqual(self.minutos({"minutos": 20}, 300, plan_min=150), 20)

    def test_linea_de_comandos_gana_a_la_tarea(self) -> None:
        self.assertEqual(self.minutos({"minutos": 200}, 300, cli=45), 45)
        self.assertEqual(self.minutos({}, 300, cli=400), 295)

    def test_nunca_mas_que_lo_que_queda_menos_5(self) -> None:
        self.assertEqual(self.minutos({"minutos": 200}, 100), 95)
        self.assertEqual(self.minutos({}, 40), 35)

    def test_nunca_menos_de_10(self) -> None:
        self.assertEqual(self.minutos({"minutos": 3}, 300), 10)
        self.assertEqual(self.minutos({}, 300, cli=1), 10)

    def test_poco_tiempo_gana_el_minimo_de_10(self) -> None:
        # con menos de 15 min hasta el fin las dos reglas chocan: hoy gana el mínimo de 10 (ver el PR)
        self.assertEqual(self.minutos({}, 12), 10)
        self.assertEqual(self.minutos({}, -30), 10)


if __name__ == "__main__":
    unittest.main()
