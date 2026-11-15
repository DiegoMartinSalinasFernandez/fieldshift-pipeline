"""Pruebas de scripts/tareas.py (el tablero) con un remoto git local, nunca contra GitHub.

Cada prueba arma en una carpeta temporal un remoto `git init --bare` con un tablero chico, y una o más
"máquinas" (clones de ese remoto con su propia copia de scripts/tareas.py). El script se corre como lo corre
una máquina: `python scripts/tareas.py --maquina X <comando>`, en un subproceso.

Correr:  python -X utf8 -m unittest tests/test_tareas.py   (o con pytest, si está instalado)
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "tareas.py"

MAQUINAS_YAML = """maquinas:
  max-1: {plan: max, estados: [IA]}
  pro-1: {plan: pro, estados: [OH, MN]}
  pro-2: {plan: pro, estados: [KS]}
"""


def tarea(tid: str, titulo: str, plan: str = "pro", depende: list[str] | None = None) -> str:
    meta = {"id": tid, "titulo": titulo, "estado": "libre", "plan_minimo": plan, "maquina": None,
            "estados": [], "depende_de": depende or [], "rama": None,
            "creada": "2026-11-15 00:00", "actualizada": "2026-11-15 00:00"}
    enc = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{enc}\n---\n\n## Qué hacer\n\nAlgo.\n\n## Notas\n"


TAREAS = {
    "T001-base.md": tarea("T001", "Base"),
    "T002-depende-de-base.md": tarea("T002", "Depende de base", depende=["T001"]),
    "T003-solo-max.md": tarea("T003", "Solo Max", plan="max"),
}


def entorno_git() -> dict[str, str]:
    """Entorno aislado: sin la configuración git del usuario (hooks, firma, credenciales) y sin máquina."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FIELDSHIFT_"))}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0",
               GIT_AUTHOR_NAME="prueba", GIT_AUTHOR_EMAIL="prueba@example.invalid",
               GIT_COMMITTER_NAME="prueba", GIT_COMMITTER_EMAIL="prueba@example.invalid")
    return env


class Tablero(unittest.TestCase):
    """Remoto bare + clones. `self.maquina(nombre)` devuelve la carpeta de un clon."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="test_tareas_")
        self.tmp = Path(self._tmp.name)
        self.env = entorno_git()
        self.remoto = self.tmp / "remoto.git"
        self.git("init", "-q", "--bare", "-b", "main", str(self.remoto))

        semilla = self.tmp / "semilla"
        self.git("init", "-q", "-b", "main", str(semilla))
        (semilla / "scripts").mkdir()
        shutil.copy(SCRIPT, semilla / "scripts" / "tareas.py")
        (semilla / ".gitignore").write_text(".tablero/\n", encoding="utf-8")
        (semilla / "coordinacion" / "tareas").mkdir(parents=True)
        (semilla / "coordinacion" / "maquinas.yaml").write_text(MAQUINAS_YAML, encoding="utf-8")
        for nombre, txt in TAREAS.items():
            (semilla / "coordinacion" / "tareas" / nombre).write_text(txt, encoding="utf-8", newline="\n")
        self.git("-C", str(semilla), "add", "-A")
        self.git("-C", str(semilla), "commit", "-q", "-m", "tablero inicial")
        self.git("-C", str(semilla), "remote", "add", "origin", str(self.remoto))
        self.git("-C", str(semilla), "push", "-q", "origin", "main")
        self._clones: dict[str, Path] = {}

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # ---------- ayudas ----------

    def git(self, *args: str) -> str:
        r = subprocess.run(["git", *args], capture_output=True, text=True, env=self.env)
        if r.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} falló:\n{r.stderr}")
        return r.stdout

    def maquina(self, nombre: str) -> Path:
        """Clon del remoto para esa máquina (uno por máquina, se crea la primera vez)."""
        if nombre not in self._clones:
            d = self.tmp / nombre
            self.git("clone", "-q", str(self.remoto), str(d))
            self._clones[nombre] = d
        return self._clones[nombre]

    def tareas(self, nombre: str, *args: str, ok: bool = True) -> subprocess.CompletedProcess:
        d = self.maquina(nombre)
        r = subprocess.run([sys.executable, "-X", "utf8", str(d / "scripts" / "tareas.py"),
                            "--maquina", nombre, *args], capture_output=True, text=True, env=self.env,
                           cwd=d)
        if ok and r.returncode != 0:
            raise AssertionError(f"tareas.py {' '.join(args)} ({nombre}) falló:\n{r.stdout}\n{r.stderr}")
        if not ok and r.returncode == 0:
            raise AssertionError(f"tareas.py {' '.join(args)} ({nombre}) debía fallar:\n{r.stdout}")
        return r

    def en_remoto(self, tid: str) -> tuple[dict, str]:
        """Encabezado y cuerpo de la tarea tal como está en main del remoto."""
        nombres = self.git(f"--git-dir={self.remoto}", "ls-tree", "--name-only", "main",
                           "coordinacion/tareas/").split()
        ruta = next(n for n in nombres if Path(n).name.startswith(tid + "-"))
        txt = self.git(f"--git-dir={self.remoto}", "show", f"main:{ruta}")
        _, enc, cuerpo = txt.split("---\n", 2)
        return yaml.safe_load(enc), cuerpo

    def log_remoto(self) -> list[str]:
        return self.git(f"--git-dir={self.remoto}", "log", "--format=%s", "main").splitlines()

    def archivos_remoto(self) -> set[str]:
        return set(self.git(f"--git-dir={self.remoto}", "ls-tree", "-r", "--name-only", "main").split())


class Comandos(Tablero):
    """Cada comando cambia el estado y las notas como dice MAQUINAS.md."""

    def test_nueva(self) -> None:
        r = self.tareas("max-1", "nueva", "Riego en Kansas", "--plan", "pro", "--estados", "ks",
                        "--depende", "t001, T002")
        self.assertIn("coordinacion/tareas/T004-riego-en-kansas.md", r.stdout)
        meta, cuerpo = self.en_remoto("T004")
        self.assertEqual(meta["id"], "T004")
        self.assertEqual(meta["titulo"], "Riego en Kansas")
        self.assertEqual(meta["estado"], "libre")
        self.assertEqual(meta["plan_minimo"], "pro")
        self.assertIsNone(meta["maquina"])
        self.assertEqual(meta["estados"], ["KS"])
        self.assertEqual(meta["depende_de"], ["T001", "T002"])
        for seccion in ("## Qué hacer", "## Terminada cuando", "## Notas"):
            self.assertIn(seccion, cuerpo)
        self.assertEqual(self.log_remoto()[0], "tarea T004: nueva (max-1)")

    def test_tomar(self) -> None:
        self.tareas("pro-1", "tomar", "t001")          # el id no distingue mayúsculas
        meta, cuerpo = self.en_remoto("T001")
        self.assertEqual(meta["estado"], "tomada")
        self.assertEqual(meta["maquina"], "pro-1")
        self.assertNotEqual(meta["actualizada"], "2026-11-15 00:00")
        self.assertRegex(cuerpo, r"## Notas\n- \d{4}-\d\d-\d\d \d\d:\d\d · pro-1: tomada\n$")
        self.assertEqual(self.log_remoto()[0], "tarea T001: tomada por pro-1")

    def test_tomar_no_libre(self) -> None:
        self.tareas("pro-1", "tomar", "T001")
        r = self.tareas("pro-2", "tomar", "T001", ok=False)
        self.assertIn("no está libre", r.stderr)
        self.assertEqual(self.en_remoto("T001")[0]["maquina"], "pro-1")

    def test_tomar_con_dependencia_sin_terminar(self) -> None:
        r = self.tareas("pro-1", "tomar", "T002", ok=False)
        self.assertIn("depende de tareas sin terminar", r.stderr)
        self.assertEqual(self.en_remoto("T002")[0]["estado"], "libre")
        # con T001 tomada (no hecha) tampoco
        self.tareas("pro-1", "tomar", "T001")
        self.tareas("pro-2", "tomar", "T002", ok=False)
        # con T001 hecha, sí
        self.tareas("pro-1", "terminar", "T001", "listo")
        self.tareas("pro-2", "tomar", "T002")
        self.assertEqual(self.en_remoto("T002")[0]["maquina"], "pro-2")

    def test_tomar_max_desde_pro(self) -> None:
        r = self.tareas("pro-1", "tomar", "T003", ok=False)
        self.assertIn("plan Max", r.stderr)
        self.tareas("max-1", "tomar", "T003")
        self.assertEqual(self.en_remoto("T003")[0]["maquina"], "max-1")

    def test_nota_no_cambia_estado(self) -> None:
        self.tareas("pro-1", "nota", "T001", "un avance")       # libre sigue libre
        meta, cuerpo = self.en_remoto("T001")
        self.assertEqual((meta["estado"], meta["maquina"]), ("libre", None))
        self.assertIn("· pro-1: un avance\n", cuerpo)
        self.assertEqual(self.log_remoto()[0], "tarea T001: nota (pro-1)")

        self.tareas("pro-1", "tomar", "T001")
        self.tareas("pro-2", "nota", "T001", "dato para pro-1")  # cualquiera puede anotar
        meta, cuerpo = self.en_remoto("T001")
        self.assertEqual((meta["estado"], meta["maquina"]), ("tomada", "pro-1"))
        notas = cuerpo.split("## Notas\n", 1)[1].splitlines()
        self.assertEqual([n.split(" · ", 1)[1] for n in notas],
                         ["pro-1: un avance", "pro-1: tomada", "pro-2: dato para pro-1"])

    def test_soltar(self) -> None:
        self.tareas("pro-1", "tomar", "T001")
        r = self.tareas("pro-2", "soltar", "T001", "no es mía", ok=False)
        self.assertIn("es de pro-1", r.stderr)
        self.tareas("pro-1", "soltar", "T001", "se acabó el uso")
        meta, cuerpo = self.en_remoto("T001")
        self.assertEqual((meta["estado"], meta["maquina"]), ("libre", None))
        self.assertIn("· pro-1: soltada: se acabó el uso\n", cuerpo)
        self.assertEqual(self.log_remoto()[0], "tarea T001: libre (pro-1)")
        self.tareas("pro-2", "tomar", "T001")                     # vuelve a poder tomarse

    def test_bloquear(self) -> None:
        self.tareas("pro-1", "tomar", "T001")
        self.tareas("max-1", "bloquear", "T001", "falta decidir")  # cualquiera puede bloquear
        meta, cuerpo = self.en_remoto("T001")
        self.assertEqual((meta["estado"], meta["maquina"]), ("bloqueada", "pro-1"))
        self.assertIn("· max-1: bloqueada: falta decidir\n", cuerpo)
        r = self.tareas("pro-2", "tomar", "T001", ok=False)
        self.assertIn("no está libre", r.stderr)

    def test_terminar(self) -> None:
        self.tareas("pro-1", "tomar", "T001")
        r = self.tareas("pro-2", "terminar", "T001", "no es mía", ok=False)
        self.assertIn("es de pro-1", r.stderr)
        self.tareas("pro-1", "terminar", "T001", "PR #1")
        meta, cuerpo = self.en_remoto("T001")
        self.assertEqual((meta["estado"], meta["maquina"]), ("hecha", "pro-1"))
        self.assertIn("· pro-1: terminada: PR #1\n", cuerpo)
        self.assertEqual(self.log_remoto()[0], "tarea T001: hecha (pro-1)")

    def test_tarea_inexistente(self) -> None:
        r = self.tareas("pro-1", "tomar", "T999", ok=False)
        self.assertIn("No existe la tarea T999", r.stderr)

    def test_bitacora(self) -> None:
        self.tareas("pro-1", "bitacora", "primera")
        self.tareas("pro-1", "bitacora", "segunda")
        txt = self.git(f"--git-dir={self.remoto}", "show", "main:coordinacion/bitacora/pro-1.md")
        self.assertTrue(txt.startswith("# Bitácora de pro-1\n"))
        self.assertEqual(txt.count("\n## "), 1)                   # un solo encabezado por día
        self.assertRegex(txt, r"- \d\d:\d\d primera\n- \d\d:\d\d segunda\n$")

    def test_sin_git_no_publica(self) -> None:
        d = self.maquina("pro-1")
        antes = self.log_remoto()
        r = subprocess.run([sys.executable, "-X", "utf8", str(d / "scripts" / "tareas.py"), "--maquina",
                            "pro-1", "--sin-git", "tomar", "T001"], capture_output=True, text=True,
                           env=self.env, cwd=d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(sin git)", r.stdout)
        self.assertEqual(self.log_remoto(), antes)
        self.assertIn("estado: tomada", (d / "coordinacion/tareas/T001-base.md").read_text(encoding="utf-8"))
        self.assertFalse((d / ".tablero").exists())


def instalar_pre_push(clon: Path, comando: list[str], env: dict[str, str]) -> None:
    """Hook pre-push que, la primera vez, corre `comando` (otra máquina publicando) antes de que este push
    llegue al remoto. Así el push de esta máquina se rechaza siempre, sin depender de tiempos."""
    marca = clon / ".git" / "ya_corrio"
    linea = " ".join(f"'{c}'" for c in comando)
    hook = clon / ".git" / "hooks" / "pre-push"
    hook.write_text(
        "#!/bin/sh\n"
        f"[ -e '{marca}' ] && exit 0\n"
        f"touch '{marca}'\n"
        "unset $(git rev-parse --local-env-vars)\n"   # que la otra máquina no use el GIT_DIR de esta
        f"{linea} >/dev/null 2>&1\n"
        "exit 0\n", encoding="utf-8")
    hook.chmod(hook.stat().st_mode | stat.S_IEXEC)


class Carrera(Tablero):
    """Dos máquinas publican casi a la vez."""

    def comando(self, nombre: str, *args: str) -> list[str]:
        return [sys.executable, "-X", "utf8", str(self.maquina(nombre) / "scripts" / "tareas.py"),
                "--maquina", nombre, *args]

    def test_misma_tarea_push_rechazado(self) -> None:
        # pro-1 ya leyó T001 libre; justo antes de su push, pro-2 la toma y publica.
        instalar_pre_push(self.maquina("pro-1"), self.comando("pro-2", "tomar", "T001"), self.env)
        r = self.tareas("pro-1", "tomar", "T001", ok=False)
        self.assertIn("Otra máquina cambió el mismo archivo", r.stderr)
        self.assertTrue((self.maquina("pro-1") / ".git" / "ya_corrio").exists())
        meta, cuerpo = self.en_remoto("T001")
        self.assertEqual((meta["estado"], meta["maquina"]), ("tomada", "pro-2"))
        self.assertNotIn("pro-1", cuerpo)
        self.assertEqual(self.log_remoto().count("tarea T001: tomada por pro-2"), 1)
        self.assertNotIn("tarea T001: tomada por pro-1", self.log_remoto())
        # la copia del tablero de pro-1 quedó limpia e igual a main, sin el commit descartado
        tablero = self.maquina("pro-1") / ".tablero"
        self.assertEqual(self.git("-C", str(tablero), "status", "--porcelain"), "")
        self.assertEqual(self.git("-C", str(tablero), "rev-parse", "HEAD"),
                         self.git(f"--git-dir={self.remoto}", "rev-parse", "main"))
        # y al reintentar, el script dice que ya no está libre
        r = self.tareas("pro-1", "tomar", "T001", ok=False)
        self.assertIn("no está libre", r.stderr)

    def test_tareas_distintas_rebase_y_reintento(self) -> None:
        # Si la otra máquina tocó otro archivo, el rebase sale bien y el push se reintenta.
        instalar_pre_push(self.maquina("pro-1"), self.comando("max-1", "tomar", "T003"), self.env)
        self.tareas("pro-1", "tomar", "T001")
        self.assertEqual(self.en_remoto("T001")[0]["maquina"], "pro-1")
        self.assertEqual(self.en_remoto("T003")[0]["maquina"], "max-1")
        self.assertEqual(self.log_remoto()[:2], ["tarea T001: tomada por pro-1", "tarea T003: tomada por max-1"])

    def test_misma_tarea_en_paralelo(self) -> None:
        # Sin hook: dos procesos a la vez. Pase lo que pase con los tiempos, gana exactamente una.
        for m in ("pro-1", "pro-2"):
            self.maquina(m)
        procs = {m: subprocess.Popen(self.comando(m, "tomar", "T001"), stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, env=self.env) for m in ("pro-1", "pro-2")}
        res = {m: (p.wait(timeout=60), p.stderr.read()) for m, p in procs.items()}
        for p in procs.values():
            p.stdout.close(); p.stderr.close()
        ganadoras = [m for m, (rc, _) in res.items() if rc == 0]
        self.assertEqual(len(ganadoras), 1, res)
        perdedora = next(m for m in res if m not in ganadoras)
        self.assertRegex(res[perdedora][1], "no está libre|Otra máquina cambió el mismo archivo")
        meta, _ = self.en_remoto("T001")
        self.assertEqual((meta["estado"], meta["maquina"]), ("tomada", ganadoras[0]))


class CopiaAparte(Tablero):
    """El tablero se publica desde .tablero/ sin arrastrar la rama de trabajo."""

    def test_no_arrastra_rama_ni_cambios_sin_commit(self) -> None:
        d = self.maquina("pro-1")
        self.git("-C", str(d), "switch", "-q", "-c", "tarea/T001-algo")
        (d / "src").mkdir()
        (d / "src" / "codigo.py").write_text("x = 1\n", encoding="utf-8")
        self.git("-C", str(d), "add", "src/codigo.py")
        self.git("-C", str(d), "commit", "-q", "-m", "código de la tarea")
        rama_antes = self.git("-C", str(d), "rev-parse", "HEAD")
        # cambios sin commit, incluso en el propio archivo de la tarea en la rama
        (d / "src" / "codigo.py").write_text("x = 2\n", encoding="utf-8")
        tarea_rama = d / "coordinacion" / "tareas" / "T001-base.md"
        tarea_rama.write_text(tarea_rama.read_text(encoding="utf-8") + "borrador local\n", encoding="utf-8")

        self.tareas("pro-1", "tomar", "T001")
        self.tareas("pro-1", "nota", "T001", "avance")
        self.tareas("pro-1", "bitacora", "trabajé en T001")

        # main del remoto: solo commits del tablero, sin el código de la rama
        self.assertNotIn("src/codigo.py", self.archivos_remoto())
        self.assertNotIn("código de la tarea", self.log_remoto())
        self.assertEqual(self.log_remoto(), ["bitácora de pro-1", "tarea T001: nota (pro-1)",
                                             "tarea T001: tomada por pro-1", "tablero inicial"])
        self.assertNotIn("borrador local", self.en_remoto("T001")[1])
        # la carpeta de trabajo sigue en su rama, con su commit y sus cambios sin commit
        self.assertEqual(self.git("-C", str(d), "branch", "--show-current").strip(), "tarea/T001-algo")
        self.assertEqual(self.git("-C", str(d), "rev-parse", "HEAD"), rama_antes)
        self.assertEqual((d / "src" / "codigo.py").read_text(encoding="utf-8"), "x = 2\n")
        self.assertTrue(tarea_rama.read_text(encoding="utf-8").endswith("borrador local\n"))
        estado = self.git("-C", str(d), "status", "--porcelain").splitlines()
        self.assertEqual(sorted(estado), [" M coordinacion/tareas/T001-base.md", " M src/codigo.py"])
        # .tablero es un worktree de main al día, sin la rama
        tablero = d / ".tablero"
        self.assertEqual(self.git("-C", str(tablero), "rev-parse", "HEAD"),
                         self.git(f"--git-dir={self.remoto}", "rev-parse", "main"))
        self.assertFalse((tablero / "src" / "codigo.py").exists())

    def test_lee_main_aunque_la_rama_este_vieja(self) -> None:
        # pro-2 toma T001; la rama de pro-1 sigue viendo T001 libre, pero el script lee main.
        self.maquina("pro-1")
        self.tareas("pro-2", "tomar", "T001")
        r = self.tareas("pro-1", "tomar", "T001", ok=False)
        self.assertIn("no está libre: tomada (pro-2)", r.stderr)
        r = self.tareas("pro-1", "listar", "--libres")
        ids = [linea.split()[0] for linea in r.stdout.splitlines()[1:]]
        self.assertEqual(ids, ["T002", "T003"])
        self.assertIn("(espera T001)", r.stdout)                  # T001 tomada, no hecha


if __name__ == "__main__":
    unittest.main()
