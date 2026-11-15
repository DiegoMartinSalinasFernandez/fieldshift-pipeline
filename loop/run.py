#!/usr/bin/env python
"""Orquestador del research agent de Field Shift.

Método de Karpathy (autoresearch) + el "auto loop" de AI LABS:
  - Cada ronda: elige una tarea, lanza un agente nuevo (claude -p) con program.md y una tarjeta,
    y al terminar corre los checks bloqueados con su copia privada del scorer.
  - Si el puntaje total sube y nada de lo que sumaba baja, hace commit. Si no, git reset.
  - Cada N rondas (o cuando una tarea se traba) corre la reflexión, que reescribe solo la
    sección "Cómo trabajar" de program.md a partir de los resultados.

Uso (en una terminal común, no adentro de una ronda):
    python loop/run.py --hours 8
    python loop/run.py --resume <tag> --hours 4
    python loop/run.py --hours 0.5 --max-rounds 1 --only base        # prueba corta

Para frenar sin cortar una ronda a la mitad: crear el archivo loop/STOP.
Todo queda en loop/runs/<tag>/ (resultados, prompts, logs) y el reporte final en loop/reports/.
Si falta pyyaml, se relanza solo con uv (Python 3.11).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOOP = REPO / "loop"
ES_WINDOWS = os.name == "nt"

# Rutas que ningún agente puede tocar durante la corrida (el hook las bloquea y el orquestador
# lo verifica después de cada ronda).
BLOQUEADAS = ["loop/", ".claude/", ".git/", "CLAUDE.md", "config/config.yaml", ".gitignore", ".gitattributes"]
# Lo que aprueba el humano: sus hashes van a loop/spec/LOCK.json.
APROBADOS = ["loop/spec", "loop/checks", "loop/hooks", "loop/prompts", "loop/run.py", "loop/puntaje.py",
             "loop/aprobar_checks.py", "loop/registro.py"]
# Lo que se compara contra la copia privada después de cada ronda (y se restaura si cambió).
INTEGRIDAD = APROBADOS + ["loop/README.md", "CLAUDE.md", "config/config.yaml", ".claude", ".gitignore",
                          ".gitattributes", ".git/config", ".git/info"]
LOCK_REL = "loop/spec/LOCK.json"
SETTINGS_LOCAL = ".claude/settings.local.json"   # fuera de INTEGRIDAD: se restaura aparte, ronda a ronda
BORRADOR = "data/interim/_tmp/"                    # borrador: siempre permitido, no se versiona
LIMITE_RAW_BYTES = 5e9                             # regla 6 del CLAUDE.md

ORDEN = ["base", "vegetacion", "agua", "research:cultivos_zona", "clima", "cultivos", "suelo_terreno",
         "research:nass_quickstats", "research:cdl_csb", "research:productos_nasa", "research:gssurgo",
         "research:censo_agropecuario", "research:precios_margenes", "research:recursos_desafio", "economia", "lotes",
         "paisaje", "aptitud", "validacion", "hidrologia", "teledeteccion", "nldas", "ecostress",
         "research:ag_data_commons", "merge"]
# Con Earthdata, estas tienen una ronda temprana para dejar pedidos en cola (AppEEARS).
TEMPRANAS = ["vegetacion", "agua", "ecostress"]
# Las tablas unidas dependen de todos los paquetes: cuando una ronda de otra tarea suma o cambia un archivo,
# los checks de merge bajan. Eso no cuenta como regresión de esa ronda: merge vuelve a la cola.
TAREA_MERGE = "merge"
MERGE_ANTES_DEL_FIN_MIN = 45   # con menos tiempo que esto, un merge desactualizado pasa adelante

RE_LIMITE = re.compile(r"(usage limit|rate.?limit|limit reached|hit your limit|\bresets?\s+(at\s+|in\s+)?\d|"
                       r"\b429\b|overloaded|quota|too many requests)", re.I)
RE_AUTH = re.compile(r"(invalid api key|please run /login|not logged in|log ?in again|authenticat|"
                     r"unauthori[sz]ed|\b401\b|oauth token|credentials? (are )?(missing|invalid|expired))", re.I)
RE_CRED_EARTHDATA = re.compile(r"earthdata|netrc|appeears|urs\.earthdata", re.I)
RE_CRED_NASS = re.compile(r"\bnass\b|quick ?stats|api.?key", re.I)

# Variables de la sesión de Claude Code que lanzó la corrida: no pasan a los agentes.
VARS_SESION = {"CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT", "CLAUDE_PREVIEW_CLASSIFIER_FLOOR"}
PREFIJOS_SESION = ("CLAUDE_CODE_", "CLAUDE_AGENT_SDK_", "RA_")
# Configuración del usuario con esos prefijos que sí se conserva.
CONSERVAR = {"CLAUDE_CODE_GIT_BASH_PATH", "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX",
             "CLAUDE_CODE_SKIP_BEDROCK_AUTH", "CLAUDE_CODE_SKIP_VERTEX_AUTH", "CLAUDE_CODE_MAX_OUTPUT_TOKENS",
             "CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CODE_SHELL", "CLAUDE_CODE_TMPDIR", "CLAUDE_CODE_USE_POWERSHELL_TOOL"}

TRAILER = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
IDENTIDAD_RESPALDO = ["-c", "user.name=Field Shift research agent", "-c", "user.email=research-agent@localhost"]


# --------------------------------------------------------------------------- utilidades

def ahora():
    return dt.datetime.now()


def limpiar(texto) -> str:
    return re.sub(r"\s+", " ", str(texto or "")).strip()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def archivos_de(rutas, base: Path = REPO):
    out = []
    for r in rutas:
        p = base / r
        if p.is_file():
            out.append(p)
        elif p.is_dir():
            out.extend(sorted(x for x in p.rglob("*") if x.is_file() and "__pycache__" not in x.parts))
    return out


def hashes(rutas, base: Path = REPO, excluir=()):
    out = {}
    for p in archivos_de(rutas, base):
        rel = p.relative_to(base).as_posix()
        if rel not in excluir:
            out[rel] = sha256(p)
    return out


def hashes_aprobados(base: Path = REPO):
    return hashes(APROBADOS, base, excluir={LOCK_REL})


def hashes_integridad(base: Path = REPO):
    return hashes(INTEGRIDAD, base, excluir={SETTINGS_LOCAL})


def seccion(texto: str, nombre: str) -> str:
    m = re.search(rf"<!-- {nombre}:INICIO -->(.*?)<!-- {nombre}:FIN -->", texto, re.S)
    return m.group(1) if m else ""


def hash_reglas_fijas(base: Path = REPO) -> str:
    texto = (base / "loop" / "program.md").read_text(encoding="utf-8")
    return hashlib.sha256(seccion(texto, "REGLAS-FIJAS").encode("utf-8")).hexdigest()


def verificar_lock(base: Path = REPO):
    """None si no hay LOCK.json; si no, la lista de diferencias con lo aprobado (vacía = coincide)."""
    lp = base / LOCK_REL
    if not lp.exists():
        return None
    lock = json.loads(lp.read_text(encoding="utf-8"))
    actuales = hashes_aprobados(base)
    aprobados = lock.get("archivos", {})
    dif = sorted(k for k in set(actuales) | set(aprobados) if actuales.get(k) != aprobados.get(k))
    if hash_reglas_fijas(base) != lock.get("program_reglas_fijas"):
        dif.append("loop/program.md (reglas fijas)")
    return dif


def escribir_lock(base: Path = REPO) -> dict:
    lock = {"aprobado": ahora().isoformat(timespec="seconds"), "archivos": hashes_aprobados(base),
            "program_reglas_fijas": hash_reglas_fijas(base)}
    with open(base / LOCK_REL, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(lock, ensure_ascii=False, indent=1) + "\n")
    return lock


def coincide(rel: str, regla: str) -> bool:
    r, g = rel.lower(), regla.lower()
    return r.startswith(g) if g.endswith("/") else r == g


def quitar_solo_lectura(p: Path):
    try:
        if p.exists() and not os.access(p, os.W_OK):
            os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
    except OSError:
        pass


def _al_borrar(func, ruta, _info):
    try:
        os.chmod(ruta, stat.S_IWRITE | stat.S_IREAD)
        func(ruta)
    except OSError:
        pass


def borrar_arbol(p: Path):
    if p.exists():
        shutil.rmtree(p, onerror=_al_borrar)


def limpiar_dirs_vacios(raiz: Path):
    if not raiz.exists():
        return
    for d, _subdirs, _archivos in sorted(os.walk(raiz), key=lambda x: -len(x[0])):
        dp = Path(d)
        if dp == raiz:
            continue
        try:
            if not any(dp.iterdir()):
                dp.rmdir()
        except OSError:
            pass


def escribir_texto(p: Path, texto: str):
    """UTF-8 con fin de línea LF (write_text en Windows escribiría CRLF y ensuciaría los diffs)."""
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def leer_json(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        return d if isinstance(d, dict) else {"resumen": "(el reporte no es un objeto JSON)"}
    except Exception:
        return {"resumen": "(reporte con JSON inválido)"}


def cola(p: Path, n=600) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")[-n:]
    except OSError:
        return ""


# --------------------------------------------------------------------------- git

_GIT_C = ["-c", "core.quotepath=false", "-c", "core.fsmonitor=false", "-c", "core.autocrlf=false"]
_GIT_HOOKS: list = []          # -c core.hooksPath=<carpeta vacía privada>, lo fija la corrida
_IDENTIDAD: dict = {}


def git(*args, check=True, cwd: Path | None = None) -> str:
    cmd = ["git", *_GIT_C, *_GIT_HOOKS, *args]
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    r = subprocess.run(cmd, cwd=cwd or REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=env)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} falló: {(r.stderr or r.stdout or '').strip()[:500]}")
    return r.stdout


def identidad(cwd: Path | None = None) -> list:
    clave = str(cwd or REPO)
    if clave not in _IDENTIDAD:
        email = git("config", "user.email", check=False, cwd=cwd).strip()
        _IDENTIDAD[clave] = [] if email else list(IDENTIDAD_RESPALDO)
    return _IDENTIDAD[clave]


def git_commit(mensaje: str, rutas=None, cwd: Path | None = None, excluir=()):
    """Commit con el trailer de atribución. Devuelve el hash corto, o None si no había nada.
    `excluir`: archivos que quedan en disco pero fuera de git (los de más de max_mb_archivo_git)."""
    if excluir:
        tr = trackeadas(cwd)
        sacar = [r for r in excluir if r in tr]
        if sacar:
            git("rm", "-q", "--cached", "--", *sacar, cwd=cwd)
    if rutas:
        git("add", "-A", "--", *rutas, cwd=cwd)
    elif excluir:
        git("add", "-A", "--", ".", *[f":(exclude,literal){r}" for r in excluir], cwd=cwd)
    else:
        git("add", "-A", cwd=cwd)
    staged = subprocess.run(["git", *_GIT_C, "diff", "--cached", "--quiet"], cwd=cwd or REPO,
                            capture_output=True).returncode
    if staged == 0:
        return None
    fd, msg_p = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(mensaje.rstrip() + "\n\n" + TRAILER + "\n")
    try:
        git(*identidad(cwd), "commit", "-q", "-F", msg_p, cwd=cwd)
    finally:
        os.unlink(msg_p)
    return git("rev-parse", "--short", "HEAD", cwd=cwd).strip()


def cambios_git(cwd: Path | None = None, excluir=()):
    """Rutas cambiadas o nuevas (no ignoradas) respecto de HEAD, sin las de `excluir`."""
    out = git("status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames",
              "--ignore-submodules=all", cwd=cwd)
    return sorted({item[3:] for item in out.split("\0") if len(item) > 3} - set(excluir))


def trackeadas(cwd: Path | None = None) -> set:
    """Archivos de HEAD (vacío si todavía no hay commits)."""
    return set(x for x in git("ls-tree", "-r", "--name-only", "-z", "HEAD", cwd=cwd, check=False).split("\0") if x)


# --------------------------------------------------------------------------- data/raw

def foto_raw():
    d = REPO / "data" / "raw"
    out = {}
    if d.exists():
        for raiz, _dirs, archivos in os.walk(d):
            for nombre in archivos:
                if nombre == ".gitkeep":
                    continue
                p = Path(raiz) / nombre
                try:
                    st = p.stat()
                except OSError:
                    continue
                out[p.relative_to(REPO).as_posix()] = (st.st_size, st.st_mtime_ns)
    return out


def proteger_raw() -> int:
    """Deja de solo lectura todo lo que hay en data/raw/ (los datos bajados no se tocan)."""
    n = 0
    for rel in foto_raw():
        p = REPO / rel
        try:
            if p.stat().st_mode & stat.S_IWRITE:
                os.chmod(p, stat.S_IREAD)
                n += 1
        except OSError:
            pass
    return n


def tamanio_raw(pkg: str) -> int:
    d = REPO / "data" / "raw" / pkg
    if not d.exists():
        return 0
    total = 0
    for p in d.rglob("*"):
        try:
            if p.is_file():
                total += p.stat().st_size
        except OSError:
            pass
    return total


def archivos_salida_existen(pspec) -> bool:
    for s in pspec.get("salidas", []):
        p = REPO / s
        if p.is_file() or (p.is_dir() and any(p.rglob("*.csv"))):
            return True
    return False


# --------------------------------------------------------------------------- entorno y procesos

def entorno_limpio(extra=None) -> dict:
    """El entorno sin las variables de la sesión de Claude Code que lanzó la corrida."""
    env = {}
    for k, v in os.environ.items():
        ku = k.upper()
        if ku in VARS_SESION or (ku.startswith(PREFIJOS_SESION) and ku not in CONSERVAR):
            continue
        env[k] = v
    env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "DISABLE_AUTOUPDATER": "1"})
    if extra:
        env.update(extra)
    return env


def _crear_job():
    import ctypes
    from ctypes import wintypes

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateJobObjectW.restype = wintypes.HANDLE
    k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    k32.SetInformationJobObject.restype = wintypes.BOOL
    k32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    k32.AssignProcessToJobObject.restype = wintypes.BOOL
    k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k32.TerminateJobObject.restype = wintypes.BOOL
    k32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    k32.CloseHandle.restype = wintypes.BOOL
    k32.CloseHandle.argtypes = [wintypes.HANDLE]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [(n, ctypes.c_ulonglong) for n in ("ReadOperationCount", "WriteOperationCount",
                                                      "OtherOperationCount", "ReadTransferCount",
                                                      "WriteTransferCount", "OtherTransferCount")]

    class BASIC(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class EXTENDED(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", BASIC), ("IoInfo", IO_COUNTERS),
                    ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

    job = k32.CreateJobObjectW(None, None)
    if not job:
        raise OSError(ctypes.get_last_error(), "CreateJobObjectW")
    info = EXTENDED()
    # KILL_ON_JOB_CLOSE (0x2000): al cerrar el job mueren todos. BREAKAWAY_OK (0x800): un proceso
    # que pide explícitamente salir del job puede hacerlo (si no, su CreateProcess fallaría).
    info.BasicLimitInformation.LimitFlags = 0x2000 | 0x800
    if not k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
        err = ctypes.get_last_error()
        k32.CloseHandle(job)
        raise OSError(err, "SetInformationJobObject")
    return k32, job


class Arbol:
    """Un proceso y todos sus descendientes; matar() los termina a todos (Job Object en Windows)."""

    def __init__(self):
        self.k32 = None
        self.job = None
        self.procs = []
        if ES_WINDOWS:
            try:
                self.k32, self.job = _crear_job()
            except Exception:
                self.k32, self.job = None, None

    def popen(self, cmd, **kw):
        if ES_WINDOWS:
            kw["creationflags"] = kw.get("creationflags", 0) | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kw["start_new_session"] = True
        p = subprocess.Popen(cmd, **kw)
        self.procs.append(p)
        if self.job is not None:
            try:
                self.k32.AssignProcessToJobObject(self.job, int(p._handle))
            except Exception:
                pass
        return p

    def matar(self):
        if self.job is not None:
            try:
                self.k32.TerminateJobObject(self.job, 1)
            except Exception:
                pass
        for p in self.procs:
            if p.poll() is None:
                try:
                    if ES_WINDOWS:
                        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
                    else:
                        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass
        if self.job is not None:
            try:
                self.k32.CloseHandle(self.job)
            except Exception:
                pass
            self.job = None


def sin_suspender(activar: bool):
    """Evita que Windows se suspenda durante la corrida."""
    if not ES_WINDOWS:
        return
    try:
        import ctypes
        es_continuous, es_system_required = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(es_continuous | (es_system_required if activar else 0))
    except Exception:
        pass


def earthdata_disponible() -> bool:
    casa = Path.home()
    return ((casa / ".netrc").exists() or (casa / "_netrc").exists()
            or bool(os.environ.get("EARTHDATA_TOKEN")) or bool(os.environ.get("EARTHDATA_USERNAME")))


def nass_disponible() -> bool:
    """¿Hay clave de NASS Quick Stats? (variable NASS_API_KEY o línea en .env). Nunca la imprime."""
    if os.environ.get("NASS_API_KEY", "").strip():
        return True
    try:
        for linea in (REPO / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
            clave, _, valor = linea.partition("=")
            clave = clave.strip()
            if clave.startswith("export "):
                clave = clave[len("export "):].strip()
            if clave == "NASS_API_KEY" and valor.strip().strip('"').strip("'"):
                return True
    except OSError:
        pass
    return False


def encontrar_claude(arg):
    if arg:
        return arg
    cand = Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
    if cand.exists():
        return str(cand)
    for nombre in ("claude.exe", "claude"):
        w = shutil.which(nombre)
        if w and not w.lower().endswith((".cmd", ".ps1", ".bat")):
            return w
    return shutil.which("claude")


def python_proyecto() -> Path:
    return REPO / ".venv" / ("Scripts/python.exe" if ES_WINDOWS else "bin/python")


def python_base() -> str:
    base = getattr(sys, "_base_executable", None)
    if base and Path(base).exists():
        return base
    return sys.executable


def parse_reinicio(texto: str):
    """Hora de reinicio del límite de uso, si el mensaje la trae."""
    m = re.search(r"\|(\d{10})\b", texto)
    if m:
        return dt.datetime.fromtimestamp(int(m.group(1)))
    m = re.search(r"resets?\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*([ap])\.?\s?m\b", texto, re.I)
    if m:
        h = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "p" else 0)
        cand = ahora().replace(hour=h, minute=int(m.group(2) or 0), second=0, microsecond=0)
        if cand <= ahora():
            cand += dt.timedelta(days=1)
        return cand
    m = re.search(r"resets?\s+in\s+(?:(\d+)\s*h(?:ours?)?)?\s*(?:(\d+)\s*m(?:in(?:utes?)?)?)?", texto, re.I)
    if m and (m.group(1) or m.group(2)):
        return ahora() + dt.timedelta(hours=int(m.group(1) or 0), minutes=int(m.group(2) or 0))
    return None


# --------------------------------------------------------------------------- orquestador

class Corrida:
    CAMPOS = ["ronda", "inicio", "tarea", "resultado", "antes", "despues", "delta", "minutos", "costo_usd",
              "turnos", "denegados", "bloqueos_hook", "commit", "motivo", "notas", "resumen", "estado_agente"]

    def __init__(self, a):
        self.a = a
        self.tag = a.resume or a.tag or ahora().strftime("%Y%m%d-%H%M")
        self.rama = f"autoresearch/{self.tag}"
        self.dir = LOOP / "runs" / self.tag
        base_priv = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / ".cache"))
        clave_repo = hashlib.sha1(str(REPO).lower().encode()).hexdigest()[:8]
        self.priv = base_priv / "ResearchAgent" / f"{REPO.name}-{clave_repo}" / self.tag
        self.integ = self.priv / "integridad"
        self.inicio = ahora()
        self.fin = self.inicio + dt.timedelta(hours=a.hours)
        self.ronda = 0
        self.resultados = []
        self.tareas = {}
        self.puntaje = None               # último puntaje aceptado (dict del scorer)
        self.puntaje_inicial = None       # resumen {total, max, tareas} del comienzo de la corrida
        self.desde_reflexion = 0
        self.reflexion_pendiente = False
        self.program = ""
        self.claude = None
        self.uv = None
        self._ajuste_merge = 0.0          # pts de merge que la ronda en evaluación dejó viejos (no cuentan)
        self.integridad = {}              # rel -> sha256 de lo bloqueado al empezar
        self.bytes_integridad = {}        # rel -> contenido (para restaurar sin depender del disco)
        self.settings_local_inicio = None
        self.ent = None
        self.res = None
        self.log_f = None
        self.costo = 0.0
        self.n_limite = 0
        self.fallas_arranque = 0
        self.excepciones = 0
        self.ultima_tarea = None
        self.seguidas = 0
        self.descartados = []
        self.git_env = {}
        self.req_hash = None
        self.aviso_requirements = ""
        self._raw_ronda = None
        self.repro_final = None
        self.grandes = {}                 # rel -> [tamaño, mtime_ns] de la versión aceptada (fuera de git)
        self.adoptar = []                 # archivos grandes sin trackear que ya estaban al empezar

    # ----------------------------------------------------------------- log

    def log(self, msg: str):
        linea = f"[{ahora():%H:%M:%S}] {msg}"
        print(linea, flush=True)
        if self.log_f:
            self.log_f.write(linea + "\n")
            self.log_f.flush()

    # ----------------------------------------------------------------- preparación

    def preflight(self):
        a = self.a
        if not (REPO / ".git").exists():
            sys.exit("Este repo todavía no está en git. Revisá los checks y aprobalos con:\n"
                     "    python loop/aprobar_checks.py --resumen\n    python loop/aprobar_checks.py --aprobar")
        self.chequear_lock()
        if not git("rev-parse", "--verify", "-q", "HEAD", check=False).strip():
            sys.exit("El repo no tiene commits. Aprobá los checks: python loop/aprobar_checks.py --aprobar")
        sucios = cambios_git()
        if sucios:
            # Los archivos grandes sin trackear (de una corrida anterior) se adoptan: quedan fuera de git.
            import yaml
            spec = yaml.safe_load((REPO / "loop" / "spec" / "entregables.yaml").read_text(encoding="utf-8"))
            max_mb = float((spec.get("contrato") or {}).get("max_mb_archivo_git", 50))
            tr = trackeadas()
            self.adoptar = [c for c in sucios if c not in tr and (REPO / c).is_file()
                            and (REPO / c).stat().st_size > max_mb * 1e6]
            sucios = [c for c in sucios if c not in self.adoptar]
        if sucios:
            sys.exit("Hay cambios sin commitear (el orquestador necesita el árbol limpio):\n  " + "\n  ".join(sucios[:20]))
        self.uv = shutil.which("uv")
        if not self.uv:
            sys.exit("Falta uv (https://docs.astral.sh/uv/).")
        if not a.agent_cmd:
            self.claude = encontrar_claude(a.claude_bin)
            if not self.claude:
                sys.exit("No encuentro el CLI de Claude Code (claude).")

    def chequear_lock(self):
        dif = verificar_lock()
        if dif is None:
            sys.exit("Los checks no están aprobados. Corré: python loop/aprobar_checks.py --aprobar")
        if dif:
            sys.exit("Los checks cambiaron desde la última aprobación:\n  " + "\n  ".join(dif[:20]) +
                     "\nRevisalos y aprobalos de nuevo: python loop/aprobar_checks.py --aprobar")

    def rama_de_trabajo(self):
        actual = git("rev-parse", "--abbrev-ref", "HEAD").strip()
        existe = bool(git("branch", "--list", self.rama).strip())
        if self.a.resume:
            if not existe:
                sys.exit(f"No existe la rama {self.rama} para retomar.")
            if actual != self.rama:
                git("switch", "-q", self.rama)
                self.chequear_lock()
        else:
            if existe:
                sys.exit(f"Ya existe la rama {self.rama}. Usá --resume {self.tag} o elegí otro --tag.")
            git("switch", "-q", "-c", self.rama)
        self.log(f"Rama de trabajo: {self.rama} (desde {actual})")

    def copia_privada(self):
        """Copia de lo bloqueado fuera del repo (en memoria y en disco): de ahí corren scorer, hook y prompts."""
        self.priv.mkdir(parents=True, exist_ok=True)
        self.integridad = hashes_integridad()
        self.bytes_integridad = {rel: (REPO / rel).read_bytes() for rel in self.integridad}
        p_local = REPO / SETTINGS_LOCAL
        self.settings_local_inicio = p_local.read_bytes() if p_local.exists() else None
        borrar_arbol(self.integ)
        self.asegurar_copia()
        sin_hooks = self.priv / "sin_hooks"
        sin_hooks.mkdir(exist_ok=True)
        _GIT_HOOKS[:] = ["-c", f"core.hooksPath={sin_hooks.as_posix()}"]
        self.git_env = {"GIT_CONFIG_COUNT": "3",
                        "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": sin_hooks.as_posix(),
                        "GIT_CONFIG_KEY_1": "core.fsmonitor", "GIT_CONFIG_VALUE_1": "false",
                        "GIT_CONFIG_KEY_2": "core.quotepath", "GIT_CONFIG_VALUE_2": "false",
                        "GIT_TERMINAL_PROMPT": "0"}
        (self.priv / "cache").mkdir(exist_ok=True)
        import yaml
        self.ent = yaml.safe_load(self.bytes_integridad["loop/spec/entregables.yaml"].decode("utf-8"))
        self.res = yaml.safe_load(self.bytes_integridad["loop/spec/research.yaml"].decode("utf-8"))

    def asegurar_copia(self):
        """Reescribe la copia privada (y la configuración del agente) si algo la cambió."""
        for rel, contenido in self.bytes_integridad.items():
            p = self.integ / rel
            if not p.exists() or sha256(p) != self.integridad[rel]:
                p.parent.mkdir(parents=True, exist_ok=True)
                quitar_solo_lectura(p)
                p.write_bytes(contenido)
        guard = (self.integ / "loop" / "hooks" / "guard.py").as_posix()
        settings = {
            "hooks": {"PreToolUse": [{"matcher": "*", "hooks": [
                {"type": "command", "command": f'"{Path(python_base()).as_posix()}" -I "{guard}"', "timeout": 30}]}]},
            "permissions": {"deny": ["Read(~/.netrc)", "Read(~/_netrc)", "Read(./.env)", "Read(./.env.*)"]},
        }
        (self.priv / "settings.runtime.json").write_text(json.dumps(settings, indent=1), encoding="utf-8")
        (self.priv / "mcp.json").write_text(json.dumps({"mcpServers": {}}), encoding="utf-8")

    def chequear_auth(self):
        """Prueba barata de que Claude Code responde fuera de la app (con el entorno limpio)."""
        if self.a.agent_cmd:
            return
        # El prompt va por stdin: --mcp-config acepta varios archivos y se comería un prompt posicional.
        cmd = [self.claude, "-p", "--output-format", "json", "--model", "haiku", "--no-session-persistence",
               "--strict-mcp-config", "--mcp-config", str(self.priv / "mcp.json")]
        try:
            r = subprocess.run(cmd, cwd=REPO, env=entorno_limpio(), input="Respondé solo con la palabra OK.",
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
        except subprocess.TimeoutExpired:
            self.log("AVISO: el chequeo de Claude Code tardó más de 4 min; sigo igual.")
            return
        except OSError as e:
            sys.exit(f"No pude ejecutar Claude Code ({self.claude}): {e}")
        texto = (r.stdout or "") + "\n" + (r.stderr or "")
        ok = False
        try:
            d = json.loads((r.stdout or "").strip())
            ok = r.returncode == 0 and not d.get("is_error")
            texto = str(d.get("result") or "") + "\n" + (r.stderr or "")
        except Exception:
            pass
        if ok:
            self.log("Claude Code responde fuera de la app (prueba con haiku): OK.")
            return
        if RE_LIMITE.search(texto):
            self.log("AVISO: Claude Code está en el límite de uso; la corrida va a esperar el reinicio.")
            return
        if RE_AUTH.search(texto):
            sys.exit("Claude Code no está autenticado para correr fuera de la app.\n"
                     "Abrí una terminal, corré `claude` y entrá con /login. Después volvé a lanzar la corrida.\n"
                     "Detalle: " + limpiar(texto)[:300])
        self.log("AVISO: el chequeo de Claude Code falló (" + limpiar(texto)[:300] +
                 "). Sigo: si los agentes no arrancan, la corrida se corta sola.")

    def preparar_entorno(self):
        py = python_proyecto()
        if not py.exists():
            self.log("Creando el entorno del proyecto (.venv, Python 3.11)...")
            r = subprocess.run([self.uv, "venv", "--python", "3.11", str(REPO / ".venv")], cwd=REPO,
                               capture_output=True, text=True, encoding="utf-8", errors="replace",
                               env=entorno_limpio())
            if r.returncode != 0:
                self.log("AVISO: no se pudo crear .venv: " + limpiar(r.stderr or r.stdout)[-400:])
        self.instalar_requirements()

    def instalar_requirements(self):
        req = REPO / "requirements.txt"
        py = python_proyecto()
        if not req.exists() or not py.exists():
            return
        h = sha256(req)
        if h == self.req_hash:
            return
        self.log("Instalando requirements.txt en .venv...")
        try:
            r = subprocess.run([self.uv, "pip", "install", "--python", str(py), "-r", str(req)], cwd=REPO,
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
                               env=entorno_limpio())
            if r.returncode != 0:
                self.aviso_requirements = limpiar(r.stderr or r.stdout)[-300:]
                self.log("AVISO: no se pudo instalar requirements.txt: " + self.aviso_requirements)
            else:
                self.aviso_requirements = ""
        except subprocess.TimeoutExpired:
            self.aviso_requirements = "la instalación tardó más de 30 min"
            self.log("AVISO: " + self.aviso_requirements)
        self.req_hash = h

    # ----------------------------------------------------------------- integridad

    def tocados_integridad(self):
        actuales = hashes_integridad()
        return sorted(k for k in set(actuales) | set(self.integridad) if actuales.get(k) != self.integridad.get(k))

    def restaurar_bloqueados(self):
        """Descarta todo y deja lo bloqueado exactamente como al empezar. Si no puede, corta la corrida."""
        self.descartar()
        for rel, contenido in self.bytes_integridad.items():
            p = REPO / rel
            if not p.exists() or sha256(p) != self.integridad[rel]:
                p.parent.mkdir(parents=True, exist_ok=True)
                quitar_solo_lectura(p)
                p.write_bytes(contenido)
        for rel in hashes_integridad():
            if rel not in self.integridad:
                p = REPO / rel
                quitar_solo_lectura(p)
                try:
                    p.unlink()
                except FileNotFoundError:
                    pass
        self.restaurar_settings_local(self.settings_local_inicio)
        quedan = self.tocados_integridad()
        if quedan:
            raise RuntimeError("no se pudieron restaurar los archivos bloqueados: " + ", ".join(quedan[:5]))

    @staticmethod
    def leer_settings_local():
        p = REPO / SETTINGS_LOCAL
        return p.read_bytes() if p.exists() else None

    def restaurar_settings_local(self, antes) -> bool:
        """Deja .claude/settings.local.json como estaba (podría desactivar el hook en la ronda siguiente)."""
        p = REPO / SETTINGS_LOCAL
        actual = p.read_bytes() if p.exists() else None
        if actual == antes:
            return False
        quitar_solo_lectura(p)
        if antes is None:
            p.unlink()
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(antes)
        return True

    @staticmethod
    def es_bloqueada(rel: str, permitidas) -> bool:
        if rel == SETTINGS_LOCAL or any(coincide(rel, r) for r in permitidas):
            return False
        return any(coincide(rel, b) for b in BLOQUEADAS)

    # ----------------------------------------------------------------- archivos grandes (fuera de git)
    # Los archivos de más de contrato.max_mb_archivo_git (ej. clima_diario.csv) no van a git: GitHub no
    # los acepta. Quedan en disco para el scorer, y el orquestador guarda una copia de la versión
    # aceptada en la carpeta privada para poder volver atrás cuando descarta una ronda.

    def max_mb(self) -> float:
        return float((self.ent.get("contrato") or {}).get("max_mb_archivo_git", 50))

    @staticmethod
    def _stat(rel):
        try:
            st = (REPO / rel).stat()
            return [st.st_size, st.st_mtime_ns]
        except OSError:
            return None

    def cambios(self):
        return cambios_git(excluir=self.grandes)

    def respaldar_grande(self, rel):
        if not (REPO / rel).is_file():
            self.grandes.pop(rel, None)
            try:
                (self.priv / "grandes" / rel).unlink()
            except OSError:
                pass
            return
        dst = self.priv / "grandes" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        quitar_solo_lectura(dst)
        shutil.copy2(REPO / rel, dst)
        self.grandes[rel] = self._stat(rel)

    def grandes_cambiados(self):
        return sorted(r for r, st in self.grandes.items() if self._stat(r) != st)

    def restaurar_grandes(self, rutas=None):
        """Vuelve los archivos grandes a la versión aceptada (si una ronda descartada los cambió)."""
        for rel in (rutas if rutas is not None else self.grandes_cambiados()):
            src, dst = self.priv / "grandes" / rel, REPO / rel
            if not src.exists():
                self.log(f"  AVISO: no hay copia de {rel}; queda como está.")
                self.grandes[rel] = self._stat(rel)
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            quitar_solo_lectura(dst)
            shutil.copy2(src, dst)
            self.grandes[rel] = self._stat(rel)

    def adoptar_grandes(self):
        """Al empezar: copia de respaldo de los archivos grandes (de esta corrida si se retoma, o sueltos)."""
        for rel in list(self.grandes) + [r for r in self.adoptar if r not in self.grandes]:
            if not (REPO / rel).is_file():
                self.grandes.pop(rel, None)
                continue
            if rel in self.adoptar and rel not in self.grandes:
                self.log(f"Archivo grande sin trackear: {rel} ({(REPO / rel).stat().st_size / 1e6:.0f} MB); queda fuera de git.")
            if self._stat(rel) != self.grandes.get(rel) or not (self.priv / "grandes" / rel).exists():
                self.respaldar_grande(rel)

    # ----------------------------------------------------------------- git y raw de la ronda

    def descartar(self):
        git("reset", "-q", "--hard", "HEAD")
        excl = []
        for r in self.grandes:
            excl += ["-e", "/" + r]
        git("clean", "-q", "-fd", *excl)
        self.restaurar_grandes()

    def revertir_rutas(self, rutas):
        if not rutas:
            return
        tr = trackeadas()
        restaurar = [r for r in rutas if r in tr]
        for i in range(0, len(restaurar), 100):
            git("checkout", "-q", "HEAD", "--", *restaurar[i:i + 100])
        for r in rutas:
            if r not in tr:
                p = REPO / r
                quitar_solo_lectura(p)
                try:
                    p.unlink()
                except (FileNotFoundError, IsADirectoryError, PermissionError):
                    pass

    def apartar_raw(self, rutas, n_txt: str, motivo: str):
        """Mueve archivos de data/raw que no se quedan a data/interim/<pkg>/_descartados/<ronda>/."""
        rutas = [r for r in rutas if (REPO / r).exists()]
        if not rutas:
            return
        paquetes = set(self.paquetes())
        grupos = {}
        for rel in rutas:
            partes = rel.split("/")
            pkg = partes[2] if len(partes) > 3 and partes[2] in paquetes else ""
            base = f"data/interim/{pkg}/_descartados/{n_txt}/" if pkg else f"data/interim/_descartados/{n_txt}/"
            sub = "/".join(partes[3:]) if pkg else "/".join(partes[2:])
            destino = REPO / base / sub
            destino.parent.mkdir(parents=True, exist_ok=True)
            if destino.exists():
                destino = destino.with_name(destino.name + f".{int(time.time())}")
            try:
                os.replace(REPO / rel, destino)
            except OSError:
                shutil.move(str(REPO / rel), str(destino))
            g = grupos.setdefault(base, {"ronda": n_txt, "paquete": pkg, "destino": base, "archivos": 0, "mb": 0.0,
                                         "motivo": motivo})
            g["archivos"] += 1
            try:
                g["mb"] += destino.stat().st_size / 1e6
            except OSError:
                pass
        limpiar_dirs_vacios(REPO / "data" / "raw")
        for g in grupos.values():
            g["mb"] = round(g["mb"], 1)
            self.descartados.append(g)
            self.log(f"  {g['archivos']} archivos de data/raw apartados en {g['destino']} ({motivo}).")

    def limpiar_ronda(self, raw_antes, n_txt: str, motivo: str, tamper=False):
        """Deja el repo en HEAD y aparta los raw nuevos de la ronda."""
        if tamper:
            self.restaurar_bloqueados()
        else:
            self.descartar()
        nuevos = [k for k in foto_raw() if k not in raw_antes]
        self.apartar_raw(nuevos, n_txt, motivo)

    # ----------------------------------------------------------------- puntaje

    def puntuar(self, nombre: str, reproducir=()):
        """Corre el scorer de la copia privada. Devuelve (puntaje, error)."""
        self.asegurar_copia()
        salida = self.dir / f"{nombre}.score.json"
        try:
            salida.unlink()
        except FileNotFoundError:
            pass
        checks = self.integ / "loop" / "checks"
        cmd = [self.uv, "run", "--no-project", "--quiet", "--python", "3.11", "--with-requirements",
               str(checks / "requirements.txt"), "python", "-I", "-X", "utf8", str(checks / "score.py"),
               "--repo", str(REPO), "--spec", str(self.integ / "loop" / "spec"), "--cache", str(self.priv / "cache"),
               "--json", str(salida), "--repro-timeout", str(self.a.repro_timeout)]
        if python_proyecto().exists():
            cmd += ["--python", str(python_proyecto())]
        rep = sorted(reproducir) if (reproducir and not self.a.skip_repro) else []
        if rep:
            cmd += ["--reproducir", ",".join(rep)]
        if self.a.scorer_sin_red:
            cmd.append("--sin-red")
        limite = 1800 + self.a.repro_timeout * max(1, len(rep))
        log_p = self.dir / f"{nombre}.score.log"
        arbol = Arbol()
        try:
            with open(log_p, "wb") as fo:
                p = arbol.popen(cmd, cwd=REPO, env=entorno_limpio(self.git_env), stdin=subprocess.DEVNULL,
                                stdout=fo, stderr=subprocess.STDOUT)
                try:
                    p.wait(timeout=limite)
                except subprocess.TimeoutExpired:
                    return None, f"el scorer tardó más de {limite // 60} min"
        finally:
            arbol.matar()
        if p.returncode != 0 or not salida.exists():
            return None, "el scorer falló: " + cola(log_p)
        try:
            return json.loads(salida.read_text(encoding="utf-8")), ""
        except Exception as e:
            return None, f"el scorer dejó un JSON inválido: {e}"

    @staticmethod
    def regresiones(antes, despues, ignorar_tareas=()):
        out = []
        for cid, c in antes["checks"].items():
            if c.get("tarea") in ignorar_tareas:
                continue
            d = despues["checks"].get(cid)
            pts_d = d["pts"] if d else 0.0
            if c["pts"] - pts_d > max(0.01, 0.02 * c["max"]):
                out.append(f"{cid} ({c['pts']:.2f} → {pts_d:.2f})")
        return out

    @staticmethod
    def pts_tarea(P, tid) -> float:
        return float(((P or {}).get("tareas") or {}).get(tid, {}).get("pts", 0.0))

    def repuntuar_base(self, n_txt: str):
        nuevo, err = self.puntuar(f"{n_txt}.base")
        if nuevo is None:
            self.log("  No se pudo recalcular el puntaje base: " + limpiar(err)[:200])
            return
        self.log(f"  Puntaje base recalculado: {self.puntaje['total']:.2f} → {nuevo['total']:.2f}")
        self.puntaje = nuevo

    # ----------------------------------------------------------------- tareas

    def paquetes(self):
        return list(self.ent["paquetes"].keys())

    def orden_tareas(self):
        tareas = list(self.puntaje["tareas"].keys())
        return [t for t in ORDEN if t in tareas] + [t for t in tareas if t not in ORDEN]

    def info_tarea(self, tid):
        if tid.startswith("research:"):
            tema = next(t for t in self.res["temas"] if t["id"] == tid.split(":", 1)[1])
            return {"tipo": "research", "tema": tema, "escribe": list(tema["escribe"])}
        p = self.ent["paquetes"][tid]
        return {"tipo": "datos", "pkg": tid, "spec": p,
                "escribe": list(p["escribe"]) + list(self.ent.get("rutas_comunes", []))}

    def estado(self, tid):
        st = self.tareas.setdefault(tid, {})
        for k, v in {"rondas": 0, "sin_mejora": 0, "enfriamientos": 0, "enfriar_hasta": 0, "no_antes_de": "",
                     "motivo_espera": "", "bloqueos": 0, "credencial": [], "neutras": 0}.items():
            st.setdefault(k, v)
        return st

    def base_lista(self):
        c = self.puntaje["checks"].get("esp:base:zona_config")
        if c is None:
            return self.puntaje["tareas"].get("base", {}).get("pts", 0) > 0
        return bool(c["ok"])

    def requisitos_ok(self, t):
        if t.startswith("research:") or t == "base":
            return True
        spec = self.ent["paquetes"].get(t, {})
        for r in spec.get("requiere", []) or []:
            if r == "base":
                if not self.base_lista():
                    return False
            elif self.puntaje["tareas"].get(r, {}).get("pts", 0) <= 0:
                return False
        if t == "merge":
            con_datos = sum(1 for p in self.paquetes() if p not in ("base", "merge")
                            and self.puntaje["tareas"].get(p, {}).get("pts", 0) > 0)
            if con_datos < int(spec.get("requiere_paquetes_con_datos", 2)):
                return False
        return True

    def elegir_tarea(self):
        """Devuelve (tarea, None), (None, hora hasta la que conviene esperar) o (None, None) si no queda nada."""
        P = self.puntaje
        orden = self.orden_tareas()
        if self.a.only:
            pedidas = [x.strip() for x in self.a.only.split(",") if x.strip()]
            orden = [t for t in orden if t in pedidas]
        ed, nd = earthdata_disponible(), nass_disponible()
        activas, enfriadas, esperando = [], [], []
        for t in orden:
            if P["tareas"][t].get("ok"):
                continue
            st = self.estado(t)
            cred = st.get("credencial") or []
            if cred and all((c == "earthdata" and ed) or (c == "nass" and nd) for c in cred):
                self.log(f"  Apareció la credencial que esperaba {t} ({', '.join(cred)}): vuelve a la cola.")
                st["credencial"], st["no_antes_de"], st["motivo_espera"] = [], "", ""
            if not self.requisitos_ok(t):
                continue
            if st.get("no_antes_de"):
                try:
                    nad = dt.datetime.fromisoformat(st["no_antes_de"])
                except ValueError:
                    nad = None
                if nad and ahora() < nad:
                    esperando.append((nad, t))
                    continue
                st["no_antes_de"], st["motivo_espera"] = "", ""
            if self.ronda < st.get("enfriar_hasta", 0):
                enfriadas.append((st["enfriar_hasta"], orden.index(t), t))
                continue
            activas.append(t)
        if activas:
            if "base" in activas and not self.base_lista():
                return "base", None
            # Las tablas unidas tienen que quedar al día al final de la corrida (antes que la racha de otra tarea).
            if TAREA_MERGE in activas and (self.fin - ahora()).total_seconds() / 60 < MERGE_ANTES_DEL_FIN_MIN:
                return TAREA_MERGE, None
            if self.ultima_tarea in activas and 0 < self.seguidas < self.a.max_seguidas:
                return self.ultima_tarea, None
            if ed:
                for t in TEMPRANAS:
                    if t in activas and self.estado(t)["rondas"] == 0:
                        return t, None

            def prioridad(t):
                info = P["tareas"][t]
                return (info["max"] - info["pts"]) / (1 + self.estado(t)["rondas"]), -orden.index(t)
            return max(activas, key=prioridad), None
        if enfriadas:
            enfriadas.sort()
            return enfriadas[0][2], None
        if esperando:
            esperando.sort()
            return None, esperando[0][0]
        return None, None

    def paquetes_tocados(self, rutas):
        """Paquetes cuyos CSV pueden cambiar por estas rutas (para verificar reproducibilidad)."""
        paquetes = self.ent["paquetes"]
        reglas = [(r, pkg) for pkg, p in paquetes.items() for r in (p.get("escribe") or [])]
        pk = set()
        for ruta in rutas:
            rl = ruta.lower()
            if rl.startswith("src/common/"):
                pk |= set(paquetes)
                continue
            if rl.startswith("data/processed/tabla_"):
                pk.add("merge")
                continue
            mejor = max(((len(r), pkg) for r, pkg in reglas if coincide(ruta, r)), default=None)
            if mejor:
                pk.add(mejor[1])
        return {p for p in pk if p in paquetes and archivos_salida_existen(paquetes[p])}

    # ----------------------------------------------------------------- prompt

    def tarjeta(self, tid, n, limite, reporte_rel, permitidas):
        info = self.info_tarea(tid)
        P = self.puntaje
        t = P["tareas"][tid]
        fallas = sorted(((c["max"] - c["pts"], c["msg"] or cid) for cid, c in P["checks"].items()
                         if c["tarea"] == tid and not c["ok"]), key=lambda x: -x[0])
        ed, nd = earthdata_disponible(), nass_disponible()
        slug = tid.replace("research:", "research_")
        mins = int((limite - ahora()).total_seconds() // 60)
        L = [f"# Tarjeta de la ronda {n} — tarea `{tid}`\n"]
        L.append(f"- Inicio: {ahora():%Y-%m-%d %H:%M}. Tenés hasta las **{limite:%H:%M}** ({mins} min). A esa hora el "
                 "orquestador corta la ronda: escribí el reporte antes. Mirá la hora con `date` cada tanto.")
        L.append(f"- Puntaje total: {P['total']:.1f} / {P['max']:.1f}. Esta tarea: {t['pts']:.1f} / {t['max']:.1f}.")
        L.append("- Credenciales: Earthdata " + ("disponible (`~/.netrc`)" if ed else "**no configurada**") +
                 "; clave de NASS Quick Stats (`NASS_API_KEY`) " +
                 ("disponible (en el entorno o en `.env`)" if nd else "**no configurada**") + ".")
        if not (ed and nd):
            L.append("  Sin credencial: buscá un acceso público sin login al mismo producto (documentalo como supuesto "
                     "y en el manifest), o reportá esa parte como `bloqueada` y seguí con lo demás.")
        L.append(f"- Python del proyecto: `{python_proyecto().relative_to(REPO).as_posix()}` (Python 3.11). "
                 f"Raíz del repo: `{REPO.as_posix()}`.")
        if self.aviso_requirements:
            L.append(f"- La última instalación de `requirements.txt` falló: {self.aviso_requirements[:200]}")
        L.append("- `data/raw/` es de solo lectura: lo que ya está ahí no se puede modificar ni borrar (ni cambiarle los "
                 "permisos). Cada descarga va a un archivo nuevo: bajá a `data/interim/<paquete>/` y mové el archivo a "
                 "`data/raw/<paquete>/` cuando esté completo.")
        L.append("- Al cortar la ronda se matan todos los procesos, también los que dejes en segundo plano: las descargas "
                 "largas tienen que ser reanudables (saltear lo que ya está, escribir en `.part` y renombrar al final).")
        L.append(f"- Borrador: `{BORRADOR}` (scripts de prueba, salidas temporales). No se versiona.")
        mios = [g for g in self.grandes if any(coincide(g, r) for r in permitidas)]
        L.append(f"- Los archivos de más de {self.max_mb():.0f} MB no van a git (GitHub no los acepta): quedan en disco, el "
                 "scorer los lee igual y el orquestador guarda una copia de la versión aceptada."
                 + (" Ahora: " + ", ".join(f"`{g}`" for g in mios[:5]) + "." if mios else ""))
        L.append("")
        L.append("## Qué hay que hacer\n")
        if info["tipo"] == "datos":
            p = info["spec"]
            sc = str(p.get("seccion_claude", "") or "")
            ref = f"CLAUDE.md {sc}" if sc.startswith("§") else (sc or "recurso del desafío")
            L.append(f"**{p.get('titulo', tid)}** ({ref}).\n")
            if not sc.startswith("§"):
                L.append("Este paquete no está en la tabla del CLAUDE.md §6: lo sumó el humano para usar los recursos "
                         "del desafío (pestaña Resources). Valen las mismas reglas y el mismo contrato de CSV (§1 y §4).\n")
            L.append(" ".join(str(p.get("descripcion", "")).split()))
            L.append("")
            L.append(f"Archivos, columnas, rangos e IDs del catálogo: `loop/spec/entregables.yaml`, paquete `{tid}`. "
                     "Detalle de cada variable (fuente, unidad, cálculo): `loop/spec/catalogo.csv`.")
            mb = tamanio_raw(tid) / 1e6
            L.append(f"\nTamaño actual de `data/raw/{tid}/`: {mb:,.0f} MB (límite 5 GB por paquete; pasarlo descarta la "
                     "ronda y deja la tarea esperando al humano).")
            L.append(f"Cuando subas un archivo nuevo, `process.py` tiene que poder regenerarlo: el orquestador corre "
                     f"`python {p.get('process')}` y compara.")
            desc = [d for d in self.descartados if d.get("paquete") == tid and (REPO / d["destino"]).exists()]
            if desc:
                L.append("")
                L.append("### Descargas de rondas descartadas\n")
                for d in desc[-6:]:
                    L.append(f"- `{d['destino']}`: {d['archivos']} archivos ({d['mb']:.0f} MB), ronda {d['ronda']} "
                             f"({d['motivo']}).")
                L.append(f"\nSi sirven, movelos de vuelta a `data/raw/{tid}/` con `mv` (sin copiarlos) y registralos en "
                         "`manifest.csv`; así no se bajan de nuevo. Si no sirven, ignoralos.")
        else:
            tema = info["tema"]
            L.append(f"**Research {tema.get('orden', '')}: {tema['id']}** (CLAUDE.md §8). Pregunta:\n")
            L.append("> " + " ".join(str(tema.get("pregunta", "")).split()))
            L.append("")
            L.append(f"Respuesta en `{tema.get('archivo')}` con el formato del CLAUDE.md §8 y una sección `Citas:` "
                     "con líneas `> \"texto copiado tal cual\" — [título](URL)`. Formato y checks: `loop/spec/research.yaml`.")
            C = self.res.get("cultivos") or {}
            if C and C.get("archivo") in tema.get("escribe", []):
                L.append(f"\nCompletá `{C['archivo']}` (una fila por cultivo: {', '.join(C.get('filas', []))}) y por "
                         f"cada celda una fila en `{C.get('evidencia')}` con columnas "
                         f"`{','.join(C.get('columnas_evidencia', []))}`. Atributos y rangos en `loop/spec/research.yaml`. "
                         "Fechas como MM-DD, números con punto decimal. Una celda sin evidencia verificable no suma: "
                         "mejor vacía que inventada.")
        L.append("")
        L.append(f"## Checks que fallan en esta tarea ({len(fallas)}; los primeros 25 por lo que suman)\n")
        for gan, msg in fallas[:25]:
            L.append(f"- +{gan:.2f} {msg}")
        if not fallas:
            L.append("- (ninguno)")
        L.append("")
        L.append("## Rutas que podés escribir\n")
        for r in permitidas:
            if r in ("loop/notes/", reporte_rel, BORRADOR):
                continue
            L.append(f"- `{r}`")
        L.append(f"- `loop/notes/` — tu bitácora es `loop/notes/{slug}.md`; las propuestas para el humano van en "
                 "`loop/notes/decisiones.md`")
        L.append(f"- `{BORRADOR}` — borrador")
        L.append(f"- `{reporte_rel}` — tu reporte de esta ronda")
        L.append("\nLo que escribas fuera de estas rutas se revierte al final de la ronda.")
        previas = [r for r in self.resultados if r.get("tarea") == tid][-6:]
        if previas:
            L.append("")
            L.append("## Rondas anteriores en esta tarea\n")
            L.append("| ronda | resultado | Δ puntaje | motivo y notas | resumen |")
            L.append("|---|---|---|---|---|")
            for r in previas:
                mot = "; ".join(x for x in (r.get("motivo", ""), r.get("notas", "")) if x)
                L.append(f"| {r['ronda']} | {r['resultado']} | {float(r.get('delta') or 0):+.2f} | "
                         f"{mot[:160].replace('|', '/')} | {str(r.get('resumen', ''))[:140].replace('|', '/')} |")
        notas = REPO / "loop" / "notes" / f"{slug}.md"
        if notas.exists():
            n_lineas = len(notas.read_text(encoding="utf-8", errors="replace").splitlines())
            L.append(f"\nTu bitácora (`loop/notes/{slug}.md`) tiene {n_lineas} líneas: leela primero.")
        L.append("")
        L.append(f"## Al terminar\n\nEscribí el reporte JSON en `{reporte_rel}` (formato en program.md).")
        return "\n".join(L)

    # ----------------------------------------------------------------- agente

    def lanzar(self, prompt: str, permitidas, n_txt: str, minutos: float, modelo: str):
        self.asegurar_copia()
        env = entorno_limpio({"RA_RUN_ID": f"{self.tag}-{n_txt}", "RA_REPO": str(REPO),
                              "RA_ALLOWED": json.dumps(permitidas), "RA_LOCKED": json.dumps(BLOQUEADAS),
                              **self.git_env})
        log_p = self.dir / f"{n_txt}.log.jsonl"
        err_p = self.dir / f"{n_txt}.stderr.txt"
        if self.a.agent_cmd:
            cmd, shell = self.a.agent_cmd, True
        else:
            cmd = [self.claude, "-p", "--output-format", "stream-json", "--verbose",
                   "--model", modelo, "--effort", self.a.effort,
                   "--permission-mode", self.a.permission_mode, "--permission-prompts", "none",
                   "--settings", str(self.priv / "settings.runtime.json"),
                   "--strict-mcp-config", "--mcp-config", str(self.priv / "mcp.json"),
                   "--no-session-persistence"]
            if self.a.fallback_model and self.a.fallback_model != modelo:
                cmd += ["--fallback-model", self.a.fallback_model]
            if self.a.setting_sources:
                cmd += ["--setting-sources", self.a.setting_sources]
            shell = False
        res = {"timeout": False, "rc": None, "minutos": 0.0, "costo": 0.0, "turnos": 0, "error": False, "texto": "",
               "limite": False, "denegados": 0, "bloqueos_hook": 0, "hubo_resultado": False, "arranque_fallido": False}
        # El prompt va por stdin desde un archivo: un pipe podría trabar al orquestador si el agente no lo lee.
        prompt_p = self.dir / f"{n_txt}.prompt.md"
        prompt_p.write_bytes(prompt.encode("utf-8"))
        t0 = time.time()
        arbol = Arbol()
        try:
            with open(log_p, "wb") as fo, open(err_p, "wb") as fe, open(prompt_p, "rb") as fi:
                try:
                    proc = arbol.popen(cmd, cwd=REPO, env=env, stdin=fi, stdout=fo, stderr=fe, shell=shell)
                except OSError as e:
                    res.update(arranque_fallido=True, error=True, texto=f"no se pudo lanzar el agente: {e}")
                    return res
                try:
                    proc.wait(timeout=max(60, minutos * 60 + 90))
                except subprocess.TimeoutExpired:
                    res["timeout"] = True
        finally:
            arbol.matar()     # el agente y todo lo que haya dejado corriendo
        try:
            proc.wait(timeout=30)
        except Exception:
            pass
        res["rc"] = proc.returncode
        res["minutos"] = (time.time() - t0) / 60
        try:
            marca = "BLOQUEADO por el orquestador"
            for linea in log_p.read_text(encoding="utf-8", errors="replace").splitlines():
                if not linea.startswith("{") or ('"result"' not in linea and marca not in linea):
                    continue
                try:
                    m = json.loads(linea)
                except Exception:
                    continue
                if m.get("type") == "user":
                    contenido = (m.get("message") or {}).get("content")
                    if isinstance(contenido, list):
                        res["bloqueos_hook"] += sum(
                            1 for b in contenido if isinstance(b, dict) and b.get("type") == "tool_result"
                            and marca in json.dumps(b.get("content"), ensure_ascii=False))
                elif m.get("type") == "result":
                    res["hubo_resultado"] = True
                    res["costo"] = float(m.get("total_cost_usd") or 0)
                    res["turnos"] = int(m.get("num_turns") or 0)
                    res["error"] = bool(m.get("is_error"))
                    res["texto"] = str(m.get("result") or m.get("subtype") or "")[:2000]
                    res["denegados"] = len(m.get("permission_denials") or [])
        except Exception:
            pass
        stderr = cola(err_p, 3000)
        problema = res["error"] or res["rc"] not in (0, None) or not res["hubo_resultado"]
        if problema and not res["timeout"] and RE_LIMITE.search(res["texto"] + "\n" + stderr):
            res["limite"] = True
            res["texto"] = limpiar(res["texto"] + " " + stderr[-500:])
        elif res["rc"] not in (0, None) and not res["hubo_resultado"] and not res["timeout"]:
            res["arranque_fallido"] = True
            res["texto"] = limpiar(res["texto"] or stderr[-500:] or f"código de salida {res['rc']}")
        return res

    def dormir_hasta(self, hasta, motivo: str):
        hasta = min(hasta, self.fin - dt.timedelta(minutes=11))
        seg = (hasta - ahora()).total_seconds()
        if seg <= 0:
            return
        self.log(f"Espero hasta las {hasta:%H:%M} ({seg / 60:.0f} min): {motivo}.")
        self.guardar_estado()
        while ahora() < hasta:
            if (LOOP / "STOP").exists():
                return
            time.sleep(max(1.0, min(30.0, (hasta - ahora()).total_seconds())))

    def esperar_limite(self, texto: str):
        hasta = parse_reinicio(texto)
        if hasta is None or hasta <= ahora() or hasta > ahora() + dt.timedelta(hours=6):
            self.n_limite += 1
            hasta = ahora() + dt.timedelta(minutes=[15, 30, 60][min(self.n_limite, 3) - 1])
        else:
            hasta += dt.timedelta(minutes=2)
        self.dormir_hasta(hasta, "límite de uso de Claude")

    # ----------------------------------------------------------------- una ronda

    def ronda_de_trabajo(self, tid):
        self.ronda += 1
        n = self.ronda
        n_txt = f"r{n:03d}"
        st = self.estado(tid)
        info = self.info_tarea(tid)
        es_datos = info["tipo"] == "datos"
        restante = (self.fin - ahora()).total_seconds() / 60
        minutos = max(10.0, min(float(self.a.round_minutes), restante - 5))
        limite = ahora() + dt.timedelta(minutes=minutos)
        reporte_rel = f"loop/runs/{self.tag}/{n_txt}.report.json"
        permitidas = list(dict.fromkeys(info["escribe"] + ["loop/notes/", reporte_rel, BORRADOR]))
        prompt = self.program + "\n\n---\n\n" + self.tarjeta(tid, n, limite, reporte_rel, permitidas)
        (REPO / BORRADOR).mkdir(parents=True, exist_ok=True)
        self.log(f"Ronda {n} · {tid} · hasta {limite:%H:%M} · puntaje {self.puntaje['total']:.2f}")
        antes_total = self.puntaje["total"]
        raw_antes = foto_raw()
        self._raw_ronda = raw_antes
        local_antes = self.leer_settings_local()
        t_inicio = ahora()

        res = self.lanzar(prompt, permitidas, n_txt, minutos, self.a.model)
        self.costo += res["costo"]
        reporte = leer_json(REPO / reporte_rel)
        resumen = limpiar(reporte.get("resumen") or (res["texto"][:200] if res["texto"] else "sin reporte"))
        estado_ag = limpiar(reporte.get("estado", "")).lower()
        notas = []
        if self.restaurar_settings_local(local_antes):
            notas.append(f"{SETTINGS_LOCAL} cambió durante la ronda y se restauró")

        raw_desp = foto_raw()
        nuevos_raw = sorted(k for k in raw_desp if k not in raw_antes)
        mod_raw = sorted(k for k, v in raw_antes.items() if k in raw_desp and raw_desp[k] != v)
        borr_raw = sorted(k for k in raw_antes if k not in raw_desp)
        cambios = self.cambios()
        integ = self.tocados_integridad()
        bloq = [c for c in cambios if self.es_bloqueada(c, permitidas)]
        g_mod = self.grandes_cambiados()          # archivos grandes (fuera de git) que cambiaron
        nuevos_grandes = []

        resultado, motivo, despues, delta, commit = "", "", None, 0.0, ""
        contada = True
        if not (cambios or nuevos_raw or mod_raw or borr_raw or integ or g_mod):
            if res["arranque_fallido"]:
                resultado, motivo, contada = "error_arranque", "el agente no arrancó: " + res["texto"][:300], False
            elif res["limite"]:
                resultado, motivo, contada = "limite_uso", "límite de uso de Claude", False
            elif res["error"]:
                resultado, motivo = "error_agente", res["texto"][:300] or "el agente terminó con error"
            else:
                resultado = "sin_cambios"
                motivo = "el agente no cambió nada" + (" (se cortó por tiempo)" if res["timeout"] else "")
        elif integ or bloq:
            resultado = "tamper"
            motivo = "tocó archivos bloqueados: " + ", ".join(sorted(set(integ + bloq))[:6])
            self.limpiar_ronda(raw_antes, n_txt, "ronda descartada por tocar archivos bloqueados", tamper=True)
        elif mod_raw or borr_raw:
            resultado = "raw_modificado"
            motivo = "modificó o borró archivos de data/raw: " + ", ".join((mod_raw + borr_raw)[:6])
            self.limpiar_ronda(raw_antes, n_txt, "ronda descartada (modificó data/raw)")
            self.repuntuar_base(n_txt)
        else:
            fuera = [c for c in cambios if not any(coincide(c, r) for r in permitidas)]
            raw_ajenos = [k for k in nuevos_raw if not (es_datos and k.startswith(f"data/raw/{tid}/"))]
            if fuera:
                self.revertir_rutas(fuera)
                notas.append(f"se revirtieron {len(fuera)} rutas fuera de alcance: " + ", ".join(fuera[:5]))
            if raw_ajenos:
                self.apartar_raw(raw_ajenos, n_txt, "fuera del paquete de la tarea")
                notas.append(f"se apartaron {len(raw_ajenos)} archivos de data/raw de otro paquete")
                nuevos_raw = [k for k in nuevos_raw if k not in raw_ajenos]
            if fuera:
                cambios = self.cambios()
            g_fuera = [g for g in g_mod if not any(coincide(g, r) for r in permitidas)]
            if g_fuera:
                self.restaurar_grandes(g_fuera)
                notas.append(f"se restauraron {len(g_fuera)} archivos grandes de otro paquete: " + ", ".join(g_fuera[:3]))
                g_mod = [g for g in g_mod if g not in g_fuera]
            max_mb = self.max_mb()
            for c in cambios:
                p = REPO / c
                if p.is_file() and p.stat().st_size > max_mb * 1e6:
                    nuevos_grandes.append(c)
            if nuevos_grandes:
                notas.append(f"{len(nuevos_grandes)} archivos de más de {max_mb:.0f} MB quedan fuera de git (el "
                             "orquestador guarda una copia): " + ", ".join(nuevos_grandes[:3]))
            grandes = g_fuera
            if es_datos and tamanio_raw(tid) > LIMITE_RAW_BYTES:
                resultado = "limite_5gb"
                motivo = (f"data/raw/{tid} supera 5 GB (regla 6 del CLAUDE.md): hace falta el visto bueno del humano; "
                          "la tarea espera 8 h")
                self.limpiar_ronda(raw_antes, n_txt, "superaba 5 GB en data/raw (no volver a mover sin el humano)")
                st["no_antes_de"] = (ahora() + dt.timedelta(hours=8)).isoformat(timespec="minutes")
                st["motivo_espera"] = "superó 5 GB en data/raw: espera la decisión del humano"
            elif not cambios and not nuevos_raw and not g_mod:
                resultado = "fuera_de_alcance" if (fuera or raw_ajenos or grandes) else "sin_cambios"
                motivo = ("todo lo que cambió estaba fuera de sus rutas"
                          if resultado == "fuera_de_alcance" else "el agente no cambió nada")
            else:
                resultado, motivo, despues = self.evaluar(tid, n_txt, cambios + g_mod, nuevos_raw, permitidas, notas,
                                                          estado_ag, st, res, raw_antes)
                if despues is not None:
                    # sin los puntos de merge que esta ronda dejó viejos (ver evaluar)
                    delta = despues["total"] - antes_total - self._ajuste_merge

        if resultado in ("guardada", "guardada_espera"):
            fuera_git = list(self.grandes) + [c for c in nuevos_grandes if c not in self.grandes]
            commit = git_commit(f"ronda {n:03d} [{tid}] {delta:+.2f} pts: {resumen[:120]}", excluir=fuera_git) or ""
            for g in nuevos_grandes + g_mod:
                self.respaldar_grande(g)
            self.puntaje = despues
            self.instalar_requirements()
            st["neutras"] = 0 if resultado == "guardada" else st["neutras"] + 1
        elif resultado in ("descartada", "error_scorer"):
            self.limpiar_ronda(raw_antes, n_txt, f"ronda {resultado}")
        proteger_raw()

        # Estado de la tarea
        if contada:
            st["rondas"] += 1
            if resultado == "guardada":
                st["sin_mejora"], st["bloqueos"] = 0, 0
            elif resultado != "guardada_espera" and not estado_ag.startswith("esper"):
                st["sin_mejora"] += 1
            self.actualizar_estado_agente(tid, st, estado_ag, reporte, resumen)
            if st["sin_mejora"] >= 3:
                st["enfriamientos"] += 1
                st["enfriar_hasta"] = self.ronda + min(32, 4 * (2 ** (st["enfriamientos"] - 1)))
                st["sin_mejora"] = 0
                self.reflexion_pendiente = True
                self.log(f"  La tarea {tid} se trabó: descansa hasta la ronda {st['enfriar_hasta']}.")
            self.desde_reflexion += 1
        if resultado == "guardada" and delta > 0:
            self.seguidas = self.seguidas + 1 if self.ultima_tarea == tid else 1
        else:
            self.seguidas = 0
        self.ultima_tarea = tid

        fila = {"ronda": n, "inicio": f"{t_inicio:%Y-%m-%d %H:%M}", "tarea": tid, "resultado": resultado,
                "antes": f"{antes_total:.3f}", "despues": f"{despues['total']:.3f}" if despues else "",
                "delta": f"{delta:.3f}", "minutos": f"{res['minutos']:.1f}", "costo_usd": f"{res['costo']:.2f}",
                "turnos": res["turnos"], "denegados": res["denegados"], "bloqueos_hook": res["bloqueos_hook"],
                "commit": commit, "motivo": limpiar(motivo)[:400], "notas": limpiar("; ".join(notas))[:400],
                "resumen": resumen[:400], "estado_agente": estado_ag[:40]}
        self.resultados.append(fila)
        self._raw_ronda = None
        self.log(f"  → {resultado} ({delta:+.2f}) {limpiar(motivo)[:160]}" + (f" | {fila['notas'][:160]}" if notas else ""))
        self.guardar_estado()

        if resultado == "error_arranque":
            self.fallas_arranque += 1
            if self.fallas_arranque < 6:
                espera = min(60, 2 ** self.fallas_arranque)
                self.dormir_hasta(ahora() + dt.timedelta(minutes=espera),
                                  f"el agente no arrancó ({self.fallas_arranque} veces seguidas)")
        else:
            self.fallas_arranque = 0
        if res["limite"]:
            self.esperar_limite(res["texto"])
        else:
            self.n_limite = 0

    def evaluar(self, tid, n_txt, cambios, nuevos_raw, permitidas, notas, estado_ag, st, res, raw_antes):
        """Corre el scorer sobre lo que quedó de la ronda. Devuelve (resultado, motivo, puntaje o None)."""
        self._ajuste_merge = 0.0
        info = self.info_tarea(tid)
        tocados = self.paquetes_tocados(cambios + nuevos_raw)
        if info["tipo"] == "datos" and archivos_salida_existen(self.ent["paquetes"][tid]):
            tocados.add(tid)
        raw_pre = foto_raw()
        cambios_pre = set(cambios)
        local_pre = self.leer_settings_local()
        despues, err = self.puntuar(n_txt, tocados)
        # process.py del agente corrió adentro del scorer: se controla lo mismo que después de la ronda.
        if self.restaurar_settings_local(local_pre):
            notas.append(f"{SETTINGS_LOCAL} cambió al reproducir y se restauró")
        integ = self.tocados_integridad()
        if integ:
            self.limpiar_ronda(raw_antes, n_txt, "ronda descartada (tamper al reproducir)", tamper=True)
            return "tamper", "el código del agente tocó archivos bloqueados al reproducir: " + ", ".join(integ[:5]), None
        raw_post = foto_raw()
        mod = sorted(k for k, v in raw_pre.items() if k in raw_post and raw_post[k] != v)
        borr = sorted(k for k in raw_pre if k not in raw_post)
        if mod or borr:
            self.limpiar_ronda(raw_antes, n_txt, "ronda descartada (process.py modificó data/raw)")
            self.repuntuar_base(n_txt)
            return "raw_modificado", "process.py modificó o borró archivos de data/raw al reproducir: " + ", ".join((mod + borr)[:5]), None
        nuevos_durante = [k for k in raw_post if k not in raw_pre]
        if nuevos_durante:
            self.apartar_raw(nuevos_durante, n_txt, "bajados por process.py al reproducir")
            notas.append(f"process.py bajó {len(nuevos_durante)} archivos al reproducir (se apartaron): process.py no baja datos")
        extra = sorted(set(self.cambios()) - cambios_pre)
        extra_fuera = [c for c in extra if not any(coincide(c, r) for r in permitidas)]
        if extra_fuera:
            self.limpiar_ronda(raw_antes, n_txt, "ronda descartada (process.py escribió fuera de sus rutas)")
            return "fuera_de_alcance", "al reproducir, process.py escribió fuera de sus rutas: " + ", ".join(extra_fuera[:5]), None
        if despues is None:
            return "error_scorer", limpiar(err)[:300], None
        # Si la ronda de otra tarea dejó viejas las tablas unidas, los checks de merge bajan: eso no es una
        # regresión de esta ronda ni le resta (ni le suma). merge vuelve a la cola y las rehace.
        ignorar = () if tid == TAREA_MERGE else (TAREA_MERGE,)
        regs = self.regresiones(self.puntaje, despues, ignorar)
        if tid != TAREA_MERGE:
            self._ajuste_merge = self.pts_tarea(despues, TAREA_MERGE) - self.pts_tarea(self.puntaje, TAREA_MERGE)
            if self._ajuste_merge < -1e-6:
                notas.append(f"las tablas unidas quedaron desactualizadas ({self._ajuste_merge:+.2f} pts de merge, que "
                             "no cuentan en esta ronda): merge vuelve a la cola")
        delta = despues["total"] - self.puntaje["total"] - self._ajuste_merge
        if regs:
            return "descartada", "regresión: " + "; ".join(regs[:4]), despues
        if delta > 1e-6:
            return "guardada", "", despues
        if estado_ag.startswith("esper") and delta > -1e-6 and st["neutras"] < 2:
            return "guardada_espera", "sin cambio de puntaje; queda esperando un pedido externo", despues
        return "descartada", "el puntaje no subió" + (" (se cortó por tiempo)" if res["timeout"] else ""), despues

    def actualizar_estado_agente(self, tid, st, estado_ag, reporte, resumen):
        if estado_ag.startswith("bloq"):
            st["bloqueos"] += 1
            espera = min(480, 60 * (2 ** (st["bloqueos"] - 1)))
            st["no_antes_de"] = (ahora() + dt.timedelta(minutes=espera)).isoformat(timespec="minutes")
            st["motivo_espera"] = "bloqueada: " + resumen[:200]
            texto = json.dumps(reporte, ensure_ascii=False)
            cred = []
            if RE_CRED_EARTHDATA.search(texto) and not earthdata_disponible():
                cred.append("earthdata")
            if RE_CRED_NASS.search(texto) and not nass_disponible():
                cred.append("nass")
            st["credencial"] = cred
            self.log(f"  {tid} quedó bloqueada ({', '.join(cred) or 'sin credencial pendiente'}): "
                     f"no vuelve antes de las {st['no_antes_de'][11:16]}.")
        elif estado_ag.startswith("esper"):
            hasta = None
            try:
                if reporte.get("esperar_hasta"):
                    hasta = dt.datetime.fromisoformat(str(reporte["esperar_hasta"]).strip()[:16])
            except ValueError:
                hasta = None
            if hasta is None or hasta <= ahora():
                hasta = ahora() + dt.timedelta(minutes=60)
            hasta = min(hasta, ahora() + dt.timedelta(hours=3))
            st["no_antes_de"] = hasta.isoformat(timespec="minutes")
            st["motivo_espera"] = "esperando un pedido externo"
        elif estado_ag.startswith("termin") and not self.puntaje["tareas"][tid].get("ok"):
            st["enfriar_hasta"] = max(st.get("enfriar_hasta", 0), self.ronda + 6)
            st["motivo_espera"] = "se reportó terminada sin el puntaje completo"

    # ----------------------------------------------------------------- reflexión

    def reflexionar(self):
        n_txt = f"x{self.ronda:03d}"
        self.log(f"Reflexión después de la ronda {self.ronda}...")
        estado_dir = LOOP / "state"
        estado_dir.mkdir(exist_ok=True)
        salida_ct = estado_dir / "how_to_work.next.md"
        salida_h = estado_dir / "habits.next.md"
        for p in (salida_ct, salida_h):
            if p.exists():
                p.unlink()
        self.guardar_estado()
        ultimos = sorted(self.dir.glob("r*.report.json"))[-12:]
        texto = (self.integ / "loop" / "prompts" / "reflexion.md").read_text(encoding="utf-8")
        texto = (texto.replace("{resultados}", f"loop/runs/{self.tag}/results.tsv")
                 .replace("{reportes}", ", ".join(f"loop/runs/{self.tag}/{p.name}" for p in ultimos) or "(todavía no hay)")
                 .replace("{puntaje}", f"loop/runs/{self.tag}/ultimo.score.json")
                 .replace("{habitos_salida}", "loop/state/habits.next.md")
                 .replace("{como_trabajar_salida}", "loop/state/how_to_work.next.md"))
        (self.dir / "ultimo.score.json").write_text(json.dumps(self.puntaje, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")
        permitidas = ["loop/state/how_to_work.next.md", "loop/state/habits.next.md", "loop/notes/decisiones.md", BORRADOR]
        raw_antes = foto_raw()
        self._raw_ronda = raw_antes
        local_antes = self.leer_settings_local()
        res = self.lanzar(texto, permitidas, n_txt, 15, self.a.reflect_model or self.a.model)
        self.costo += res["costo"]
        self.restaurar_settings_local(local_antes)
        integ = self.tocados_integridad()
        cambios = self.cambios()
        bloq = [c for c in cambios if self.es_bloqueada(c, permitidas)]
        raw_desp = foto_raw()
        raw_tocado = [k for k, v in raw_antes.items() if raw_desp.get(k) != v]
        resultado, motivo, commit = "reflexion", "", ""
        if integ or bloq or raw_tocado:
            self.limpiar_ronda(raw_antes, n_txt, "reflexión descartada", tamper=bool(integ or bloq))
            resultado = "reflexion_descartada"
            motivo = "tocó archivos bloqueados o de data/raw: " + ", ".join((integ + bloq + raw_tocado)[:5])
        else:
            if cambios:
                self.revertir_rutas(cambios)
                motivo = f"se revirtieron {len(cambios)} rutas fuera de sus salidas; "
            nuevos = [k for k in raw_desp if k not in raw_antes]
            self.apartar_raw(nuevos, n_txt, "bajados durante la reflexión")
            self.restaurar_grandes()
            if not salida_ct.exists() or not salida_ct.read_text(encoding="utf-8", errors="replace").strip():
                if res["limite"]:
                    resultado, motivo = "limite_uso", motivo + "límite de uso de Claude"
                elif res["arranque_fallido"]:
                    resultado, motivo = "error_arranque", motivo + "el agente no arrancó: " + res["texto"][:200]
                else:
                    resultado, motivo = "reflexion_vacia", motivo + "no escribió el nuevo 'Cómo trabajar'"
            else:
                nuevo = salida_ct.read_text(encoding="utf-8", errors="replace").strip()
                nuevo = re.sub(r"^#+\s*C[oó]mo trabajar\s*\n", "", nuevo, flags=re.I).strip()
                lineas = nuevo.splitlines()
                if len(lineas) > 90 or "<!--" in nuevo or "REGLAS-FIJAS" in nuevo or "COMO-TRABAJAR" in nuevo:
                    resultado = "reflexion_invalida"
                    motivo += f"el texto nuevo no cumple el formato ({len(lineas)} líneas)"
                else:
                    prog_p = LOOP / "program.md"
                    fijas_antes = hash_reglas_fijas()
                    prog = prog_p.read_bytes().decode("utf-8")      # sin traducir fines de línea
                    nl = "\r\n" if "\r\n" in prog else "\n"
                    bloque = ("<!-- COMO-TRABAJAR:INICIO -->\n## Cómo trabajar\n\n" + nuevo +
                              "\n<!-- COMO-TRABAJAR:FIN -->").replace("\n", nl)
                    prog = re.sub(r"<!-- COMO-TRABAJAR:INICIO -->.*?<!-- COMO-TRABAJAR:FIN -->", lambda _m: bloque,
                                  prog, flags=re.S)
                    prog_p.write_bytes(prog.encode("utf-8"))
                    if hash_reglas_fijas() != fijas_antes:
                        git("checkout", "-q", "HEAD", "--", "loop/program.md")
                        resultado, motivo = "reflexion_invalida", motivo + "el reemplazo cambiaba las reglas fijas"
                    else:
                        rutas = ["loop/program.md"]
                        if salida_h.exists() and salida_h.read_text(encoding="utf-8", errors="replace").strip():
                            escribir_texto(LOOP / "habits.md", "# Hábitos detectados por la reflexión\n\n" +
                                           salida_h.read_text(encoding="utf-8", errors="replace").strip() + "\n")
                            rutas.append("loop/habits.md")
                        commit = git_commit(f"reflexión después de la ronda {self.ronda:03d}: nuevo 'Cómo trabajar'",
                                            rutas=rutas) or ""
                        self.program = prog.replace("\r\n", "\n")
                        motivo += f"commit {commit}" if commit else "sin cambios en program.md"
        self.resultados.append({
            "ronda": self.ronda, "inicio": f"{ahora():%Y-%m-%d %H:%M}", "tarea": "reflexion", "resultado": resultado,
            "antes": f"{self.puntaje['total']:.3f}", "despues": "", "delta": "0", "minutos": f"{res['minutos']:.1f}",
            "costo_usd": f"{res['costo']:.2f}", "turnos": res["turnos"], "denegados": res["denegados"],
            "bloqueos_hook": res["bloqueos_hook"], "commit": commit, "motivo": limpiar(motivo)[:400], "notas": "",
            "resumen": "", "estado_agente": ""})
        self._raw_ronda = None
        self.log(f"  → {resultado} {limpiar(motivo)[:200]}")
        if resultado not in ("limite_uso", "error_arranque"):
            self.desde_reflexion = 0
            self.reflexion_pendiente = False
        self.guardar_estado()
        if resultado == "error_arranque":
            self.fallas_arranque += 1
            self.dormir_hasta(ahora() + dt.timedelta(minutes=min(60, 2 ** self.fallas_arranque)), "el agente no arrancó")
        if res["limite"]:
            self.esperar_limite(res["texto"])

    # ----------------------------------------------------------------- estado y reporte

    def guardar_estado(self):
        with open(self.dir / "results.tsv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=self.CAMPOS, delimiter="\t", extrasaction="ignore", lineterminator="\n")
            w.writeheader()
            for r in self.resultados:
                w.writerow(r)
        estado = {"tag": self.tag, "ronda": self.ronda, "tareas": self.tareas, "resultados": self.resultados,
                  "costo": self.costo, "inicio": self.inicio.isoformat(), "desde_reflexion": self.desde_reflexion,
                  "puntaje_inicial": self.puntaje_inicial, "ultima_tarea": self.ultima_tarea, "seguidas": self.seguidas,
                  "descartados": self.descartados, "grandes": self.grandes, "fallas_arranque": self.fallas_arranque}
        (self.dir / "state.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
        self.actualizar_registro()

    def actualizar_registro(self):
        """Rehace loop/runs/registro_rondas.xlsx con la copia privada de loop/registro.py. Nunca corta la corrida."""
        script = self.integ / "loop" / "registro.py"
        if not self.uv or not script.exists():
            return
        cmd = [self.uv, "run", "--no-project", "--quiet", "--python", "3.11", "--with", "openpyxl==3.1.5",
               "--with", "pyyaml==6.0.2", "python", "-I", "-X", "utf8", str(script), "--repo", str(REPO)]
        arbol = Arbol()
        try:
            p = arbol.popen(cmd, cwd=REPO, env=entorno_limpio(self.git_env), stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                _, err = p.communicate(timeout=180)
            except subprocess.TimeoutExpired:
                self.log("  El registro de rondas (Excel) tardó más de 3 min: se saltea esta vez.")
                return
            if p.returncode == 3:
                self.log("  loop/runs/registro_rondas.xlsx está abierto (Excel): se actualiza en la próxima ronda.")
            elif p.returncode != 0:
                self.log("  No se pudo actualizar registro_rondas.xlsx: "
                         + limpiar((err or b"").decode("utf-8", "replace"))[-200:])
        except Exception as e:
            self.log(f"  No se pudo actualizar registro_rondas.xlsx: {e}")
        finally:
            arbol.matar()

    def cargar_estado(self):
        p = self.dir / "state.json"
        if not p.exists():
            return
        e = json.loads(p.read_text(encoding="utf-8"))
        self.ronda = e.get("ronda", 0)
        self.tareas = e.get("tareas", {})
        self.resultados = e.get("resultados", [])
        self.costo = e.get("costo", 0.0)
        self.desde_reflexion = e.get("desde_reflexion", 0)
        pi = e.get("puntaje_inicial")
        self.puntaje_inicial = pi if isinstance(pi, dict) else None
        self.ultima_tarea = e.get("ultima_tarea")
        self.seguidas = e.get("seguidas", 0)
        self.descartados = e.get("descartados", [])
        self.grandes = {k: v for k, v in (e.get("grandes") or {}).items() if isinstance(v, list)}

    @staticmethod
    def resumen_puntaje(P):
        return {"total": P["total"], "max": P["max"],
                "tareas": {t: {"pts": v["pts"], "max": v["max"]} for t, v in P["tareas"].items()}}

    @staticmethod
    def listar_csv():
        filas = []
        for base in ("data/processed", "data/reference"):
            d = REPO / base
            if not d.exists():
                continue
            for p in sorted(d.rglob("*.csv")):
                rel = p.relative_to(REPO).as_posix()
                try:
                    with open(p, encoding="utf-8", errors="replace", newline="") as f:
                        r = csv.reader(f)
                        enc = next(r, [])
                        n = sum(1 for _ in r)
                    filas.append((rel, n, len(enc), p.stat().st_size / 1e6))
                except Exception:
                    filas.append((rel, None, None, p.stat().st_size / 1e6))
        return filas

    def fase_final(self, motivo_fin: str):
        if not self.a.skip_repro:
            con_salidas = sorted(p for p in self.paquetes() if archivos_salida_existen(self.ent["paquetes"][p]))
            if con_salidas:
                self.log("Verificación final de reproducibilidad: " + ", ".join(con_salidas))
                raw_antes = foto_raw()
                final, err = self.puntuar("final", set(con_salidas))
                if self.tocados_integridad():
                    self.restaurar_bloqueados()
                else:
                    self.descartar()
                self.apartar_raw([k for k in foto_raw() if k not in raw_antes], "final",
                                 "bajados por process.py en la verificación final")
                if final:
                    self.repro_final = final.get("reproducible", {})
                else:
                    self.log("  La verificación final falló: " + limpiar(err)[:200])
        return self.reporte_final(motivo_fin)

    def reporte_final(self, motivo_fin: str):
        P = self.puntaje
        I = self.puntaje_inicial or self.resumen_puntaje(P)
        rep = LOOP / "reports" / f"{self.tag}.md"
        rep.parent.mkdir(exist_ok=True)
        cuenta = {}
        for r in self.resultados:
            cuenta[r["resultado"]] = cuenta.get(r["resultado"], 0) + 1
        L = [f"# Corrida {self.tag} del research agent", ""]
        L.append(f"- Rama: `{self.rama}`")
        L.append(f"- Inicio: {self.inicio:%Y-%m-%d %H:%M} · fin: {ahora():%Y-%m-%d %H:%M} · motivo de fin: {motivo_fin}")
        L.append(f"- Puntaje: **{I['total']:.2f} → {P['total']:.2f}** de {P['max']:.2f}")
        L.append(f"- Rondas: {sum(1 for r in self.resultados if r['tarea'] not in ('reflexion', '-'))} · "
                 + ", ".join(f"{k}: {v}" for k, v in sorted(cuenta.items())))
        L.append(f"- Costo estimado informado por Claude Code: USD {self.costo:.2f}")
        L.append(f"- Credenciales: Earthdata {'disponible' if earthdata_disponible() else 'no configurada'}; "
                 f"NASS Quick Stats {'disponible' if nass_disponible() else 'no configurada'}")
        L.append("")
        L.append("## Puntaje por tarea\n")
        L.append("| tarea | inicio | fin | máximo | reproduce (verificación final) |")
        L.append("|---|---:|---:|---:|---|")
        for t, v in P["tareas"].items():
            rep_txt = ""
            if self.repro_final and t in self.repro_final:
                r = self.repro_final[t]
                rep_txt = {True: "sí", False: "NO: " + limpiar(r.get("msg"))[:80], None: ""}.get(r.get("ok"), "")
            L.append(f"| {t} | {I['tareas'].get(t, {}).get('pts', 0):.2f} | {v['pts']:.2f} | {v['max']:.2f} | {rep_txt} |")
        csvs = self.listar_csv()
        L.append("")
        L.append("## CSV generados\n")
        if csvs:
            L.append("| archivo | filas | columnas | MB |")
            L.append("|---|---:|---:|---:|")
            for rel, nf, nc, mb in csvs:
                L.append(f"| `{rel}` | {nf if nf is not None else '?'} | {nc if nc is not None else '?'} | {mb:.1f} |")
        else:
            L.append("(ninguno todavía)")
        if self.grandes:
            L.append("")
            L.append(f"## Archivos fuera de git (más de {self.max_mb():.0f} MB)\n")
            L.append("Están en disco pero no en los commits: hay que compartirlos por otro medio o regenerarlos con process.py.\n")
            for g, st in self.grandes.items():
                L.append(f"- `{g}` ({(st or [0])[0] / 1e6:.0f} MB)")
        L.append("")
        L.append("## Rondas\n")
        L.append("| ronda | tarea | resultado | Δ | min | motivo / resumen |")
        L.append("|---:|---|---|---:|---:|---|")
        for r in self.resultados:
            texto = " — ".join(x for x in (r.get("resumen"), r.get("motivo"), r.get("notas")) if x)
            L.append(f"| {r['ronda']} | {r['tarea']} | {r['resultado']} | {float(r.get('delta') or 0):+.2f} | "
                     f"{r.get('minutos', '')} | {texto[:220].replace('|', '/')} |")
        dec = LOOP / "notes" / "decisiones.md"
        L.append("")
        L.append("## Decisiones pendientes para el humano\n")
        L.append(dec.read_text(encoding="utf-8", errors="replace").strip() if dec.exists() else "(ninguna)")
        hab = LOOP / "habits.md"
        if hab.exists():
            L.append("")
            L.append("## Hábitos que aprendió la reflexión\n")
            L.append(hab.read_text(encoding="utf-8", errors="replace").replace("# Hábitos detectados por la reflexión", "").strip())
        esperando = {t: s for t, s in self.tareas.items() if s.get("motivo_espera")}
        if esperando:
            L.append("")
            L.append("## Tareas bloqueadas o esperando\n")
            for t, s in esperando.items():
                cred = f" (falta: {', '.join(s['credencial'])})" if s.get("credencial") else ""
                L.append(f"- **{t}**: {s['motivo_espera']}{cred}")
        if self.descartados:
            L.append("")
            L.append("## Descargas apartadas de rondas descartadas\n")
            for d in self.descartados[-30:]:
                L.append(f"- `{d['destino']}`: {d['archivos']} archivos, {d['mb']:.0f} MB ({d['motivo']})")
        estados = {}
        for v in P.get("variables", {}).values():
            estados[v["estado"]] = estados.get(v["estado"], 0) + 1
        L.append("")
        L.append("## Variables del catálogo\n")
        L.append(", ".join(f"{k}: {v}" for k, v in sorted(estados.items())) +
                 f". Detalle en `loop/reports/{self.tag}_estado_catalogo.csv` (para pegar en la columna Estado de la planilla).")
        L.append("")
        L.append("## Cómo revisar\n")
        L.append(f"- `git log --oneline {self.rama}` muestra cada ronda guardada; `git diff main...{self.rama}` todo junto.")
        L.append(f"- `loop/runs/{self.tag}/` tiene el prompt, el log y el reporte de cada ronda; "
                 f"`loop/reports/{self.tag}_rondas.tsv` la tabla de rondas.")
        L.append("- Antes de usar los datos, revisar los data cards (`docs/datasets/`) y sus secciones de supuestos.")
        escribir_texto(rep, "\n".join(L) + "\n")
        cat = {}
        cat_p = self.integ / "loop" / "spec" / "catalogo.csv"
        if cat_p.exists():
            with open(cat_p, encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    cat[r["id"]] = r
        with open(LOOP / "reports" / f"{self.tag}_estado_catalogo.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["id", "variable", "prioridad", "estado", "paquete", "puntos", "maximo"])
            for cid, v in P.get("variables", {}).items():
                c = cat.get(cid, {})
                w.writerow([cid, c.get("variable", ""), c.get("prioridad", ""), v["estado"], v.get("paquete", "") or "",
                            v.get("pts", 0), v.get("max", 0)])
        if (self.dir / "results.tsv").exists():
            shutil.copy2(self.dir / "results.tsv", LOOP / "reports" / f"{self.tag}_rondas.tsv")
        try:
            git_commit(f"reporte de la corrida {self.tag}",
                       rutas=[f"loop/reports/{self.tag}.md", f"loop/reports/{self.tag}_estado_catalogo.csv",
                              f"loop/reports/{self.tag}_rondas.tsv"])
        except Exception as e:
            self.log(f"No se pudo commitear el reporte: {e}")
        return rep

    # ----------------------------------------------------------------- principal

    def recuperar(self):
        """Después de un error inesperado: repo en HEAD, bloqueados intactos y raw nuevo apartado."""
        if self.tocados_integridad() or any(self.es_bloqueada(c, []) for c in self.cambios()):
            self.restaurar_bloqueados()
        else:
            self.descartar()
        if self._raw_ronda is not None:
            nuevos = [k for k in foto_raw() if k not in self._raw_ronda]
            self.apartar_raw(nuevos, f"r{self.ronda:03d}", "ronda cortada por un error del orquestador")
            self._raw_ronda = None

    def correr(self):
        self.preflight()
        self.dir.mkdir(parents=True, exist_ok=True)
        self.log_f = open(self.dir / "run.log", "a", encoding="utf-8")
        self.log(f"Research agent · corrida {self.tag} · {self.a.hours} h · hasta {self.fin:%Y-%m-%d %H:%M}")
        self.rama_de_trabajo()
        if self.a.resume:
            self.cargar_estado()
        self.copia_privada()
        self.adoptar_grandes()
        self.chequear_auth()
        self.preparar_entorno()
        self.program = (LOOP / "program.md").read_text(encoding="utf-8")
        sin_suspender(True)
        if (LOOP / "STOP").exists():
            (LOOP / "STOP").unlink()
        n = proteger_raw()
        if n:
            self.log(f"{n} archivos de data/raw quedaron de solo lectura.")
        motivo_fin = "tiempo cumplido"
        try:
            self.log("Puntaje inicial (con verificación de reproducibilidad de lo que ya existe)...")
            con_salidas = {p for p in self.paquetes() if archivos_salida_existen(self.ent["paquetes"][p])}
            raw0 = foto_raw()
            self.puntaje, err = self.puntuar("r000", con_salidas)
            if self.tocados_integridad():
                self.restaurar_bloqueados()
            else:
                self.descartar()
            self.apartar_raw([k for k in foto_raw() if k not in raw0], "r000", "bajados por process.py al reproducir")
            if self.puntaje is None:
                sys.exit("No se pudo calcular el puntaje inicial: " + err)
            if self.puntaje_inicial is None:
                self.puntaje_inicial = self.resumen_puntaje(self.puntaje)
            self.log(f"Puntaje inicial: {self.puntaje['total']:.2f} / {self.puntaje['max']:.2f}")
            if not self.a.resume:
                self.resultados.append({"ronda": 0, "inicio": f"{ahora():%Y-%m-%d %H:%M}", "tarea": "-",
                                        "resultado": "inicio", "antes": f"{self.puntaje['total']:.3f}", "despues": "",
                                        "delta": "0", "minutos": "0", "costo_usd": "0", "turnos": 0, "denegados": 0,
                                        "bloqueos_hook": 0, "commit": git("rev-parse", "--short", "HEAD").strip(),
                                        "motivo": "", "notas": "", "resumen": "", "estado_agente": ""})
            self.guardar_estado()
            intentos = 0
            while True:
                if (LOOP / "STOP").exists():
                    motivo_fin = "archivo loop/STOP"
                    break
                if (self.fin - ahora()).total_seconds() < 12 * 60:
                    motivo_fin = "tiempo cumplido"
                    break
                if self.a.max_rounds and intentos >= self.a.max_rounds:
                    motivo_fin = f"--max-rounds {self.a.max_rounds}"
                    break
                if self.fallas_arranque >= 6:
                    motivo_fin = "el agente no arrancó 6 veces seguidas (ver los .stderr.txt de las últimas rondas)"
                    break
                if (not self.a.no_reflect and self.ronda > 0 and self.desde_reflexion > 0
                        and (self.reflexion_pendiente or self.desde_reflexion >= self.a.reflect_every)):
                    try:
                        self.reflexionar()
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        if not self.manejar_excepcion(e):
                            motivo_fin = "demasiados errores inesperados del orquestador"
                            break
                        self.desde_reflexion, self.reflexion_pendiente = 0, False
                    continue
                tid, espera = self.elegir_tarea()
                if tid is None:
                    if espera is not None:
                        self.dormir_hasta(espera, "todas las tareas que quedan están esperando o bloqueadas")
                        continue
                    motivo_fin = "no quedan tareas que se puedan avanzar (todas terminadas o sin requisitos)"
                    break
                intentos += 1
                try:
                    self.ronda_de_trabajo(tid)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    if not self.manejar_excepcion(e):
                        motivo_fin = "demasiados errores inesperados del orquestador"
                        break
        except KeyboardInterrupt:
            motivo_fin = "interrumpida con Ctrl+C"
            self.log("Interrumpida: descarto la ronda en curso.")
            try:
                self.recuperar()
            except Exception as e:
                self.log(f"No pude limpiar la ronda interrumpida: {e}")
        finally:
            sin_suspender(False)
            if self.puntaje is not None:
                try:
                    self.guardar_estado()
                    rep = self.fase_final(motivo_fin)
                    ini = (self.puntaje_inicial or {}).get("total", self.puntaje["total"])
                    self.log(f"Fin ({motivo_fin}). Puntaje {ini:.2f} → {self.puntaje['total']:.2f}. "
                             f"Reporte: {rep.relative_to(REPO).as_posix()}")
                except KeyboardInterrupt:
                    self.log("Fase final interrumpida.")
                except Exception as e:
                    self.log(f"Error en la fase final: {type(e).__name__}: {e}")
                    if self.log_f:
                        self.log_f.write(traceback.format_exc())
            if self.log_f:
                self.log_f.close()
                self.log_f = None

    def manejar_excepcion(self, e) -> bool:
        """Registra un error inesperado y deja el repo limpio. False si ya hubo demasiados."""
        self.excepciones += 1
        self.log(f"ERROR inesperado del orquestador ({self.excepciones}): {type(e).__name__}: {e}")
        if self.log_f:
            self.log_f.write(traceback.format_exc())
            self.log_f.flush()
        self.recuperar()   # si esto falla, la excepción corta la corrida (más seguro que seguir)
        self.guardar_estado()
        return self.excepciones <= 3


# --------------------------------------------------------------------------- arranque

def asegurar_yaml(script: Path):
    """Si falta pyyaml, se relanza el mismo script con uv (Python 3.11 + pyyaml) y sale con su código."""
    try:
        import yaml  # noqa: F401
        return
    except ImportError:
        pass
    if os.environ.get("RA_RELANZADO"):
        sys.exit("No pude cargar pyyaml ni relanzando con uv. Instalalo con: python -m pip install pyyaml")
    uv = shutil.which("uv")
    if not uv:
        sys.exit("Falta pyyaml y no encuentro uv (https://docs.astral.sh/uv/). Instalá uno de los dos.")
    cmd = [uv, "run", "--no-project", "--quiet", "--python", "3.11", "--with", "pyyaml==6.0.2", "python",
           str(script), *sys.argv[1:]]
    p = subprocess.Popen(cmd, env=dict(os.environ, RA_RELANZADO="1"))
    while True:
        try:
            sys.exit(p.wait())
        except KeyboardInterrupt:
            continue      # el hijo también recibe el Ctrl+C y cierra la corrida ordenadamente


def parsear_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hours", type=float, default=8.0, help="duración de la corrida (default 8)")
    ap.add_argument("--tag", default=None, help="nombre de la corrida (default: fecha y hora)")
    ap.add_argument("--resume", default=None, help="retomar la corrida con este tag")
    ap.add_argument("--round-minutes", type=float, default=45, help="tiempo máximo por ronda (default 45)")
    ap.add_argument("--reflect-every", type=int, default=5, help="reflexión cada N rondas (default 5)")
    ap.add_argument("--no-reflect", action="store_true")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--reflect-model", default=None)
    ap.add_argument("--fallback-model", default="sonnet")
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--permission-mode", default="auto", choices=["auto", "acceptEdits", "bypassPermissions", "dontAsk"])
    ap.add_argument("--setting-sources", default="project,local",
                    help="fuentes de settings para los agentes (default: sin las del usuario, para no cargar sus hooks ni plugins)")
    ap.add_argument("--max-rounds", type=int, default=0, help="cortar después de N rondas (0 = sin límite)")
    ap.add_argument("--max-seguidas", type=int, default=3, help="rondas seguidas en la misma tarea mientras mejora (default 3)")
    ap.add_argument("--only", default=None, help="limitar a estas tareas (separadas por coma)")
    ap.add_argument("--repro-timeout", type=int, default=1800, help="segundos para que process.py reproduzca (default 1800)")
    ap.add_argument("--skip-repro", action="store_true", help="no verificar reproducibilidad (solo pruebas)")
    ap.add_argument("--scorer-sin-red", action="store_true", help="el scorer no baja fuentes de research (solo pruebas)")
    ap.add_argument("--claude-bin", default=None)
    ap.add_argument("--agent-cmd", default=None, help="(pruebas) comando que reemplaza a claude; recibe el prompt por stdin")
    return ap.parse_args(argv)


def main():
    if os.environ.get("RA_RUN_ID"):
        sys.exit("loop/run.py no se corre desde adentro de una ronda: el orquestador lo maneja solo el humano.")
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    a = parsear_args()
    asegurar_yaml(Path(__file__).resolve())
    Corrida(a).correr()


if __name__ == "__main__":
    main()
