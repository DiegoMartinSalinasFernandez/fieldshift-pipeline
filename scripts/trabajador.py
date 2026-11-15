"""Trabajador automático: toma tareas del tablero y las hace con Claude, solo y en segundo plano.

Corre en una copia del repo dedicada a él (la crea scripts/trabajador.ps1: <repo>-trabajador), nunca en la
carpeta donde trabaja la persona, así la máquina y Claude siguen libres para otras cosas. Por cada tarea:

  1. toma la próxima tarea libre para su plan (scripts/tareas.py), con preferencia por sus estados;
  2. crea la rama tarea/<id>-auto desde main (o sigue la que dejó un intento anterior);
  3. lanza Claude sin intervención (claude -p) con coordinacion/prompt_trabajador.md y un tope de tiempo;
  4. sube la rama, abre el PR y marca la tarea como hecha (o la suelta con una nota si quedó incompleta);
  5. si se acabó el uso de Claude, espera a que se renueve y sigue con la misma tarea.

Nunca une PRs: eso lo revisa max-1. Todo va a .trabajador/ (logs), nada a la consola.

Uso (normalmente desde scripts/trabajador.ps1):
  python scripts/trabajador.py correr [--horas 24] [--minutos-tarea 60] [--modelo opus] [--effort medium]
                                      [--solo T004] [--max-tareas N] [--sin-pr]
  python scripts/trabajador.py estado
Para pararlo: crear .trabajador/STOP (termina la tarea en curso y sale) o `trabajador.ps1 parar`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import tareas  # noqa: E402
import yaml  # noqa: E402

DIR = REPO / ".trabajador"
LOG = DIR / "trabajador.log"
STOP = DIR / "STOP"
ESTADO = DIR / "estado.json"
ES_WINDOWS = os.name == "nt"

RE_LIMITE = re.compile(r"(usage limit|rate.?limit|limit reached|hit your (\w+ )?limit|weekly limit|"
                       r"\bresets?\s+(on\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d|\bresets?\s+(at\s+|in\s+)?\d|"
                       r"\b429\b|overloaded|quota|too many requests)", re.I)
RE_AUTH = re.compile(r"(invalid api key|please run /login|not logged in|log ?in again|unauthori[sz]ed|\b401\b)", re.I)
# Variables de una sesión de Claude Code que haya lanzado al trabajador: no pasan al agente.
VARS_SESION = {"CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT"}
PREFIJOS_SESION = ("CLAUDE_CODE_", "CLAUDE_AGENT_SDK_")
CONSERVAR = {"CLAUDE_CODE_GIT_BASH_PATH", "CLAUDE_CODE_MAX_OUTPUT_TOKENS"}
# El agente no publica ni cambia de rama: eso lo hace el trabajador.
PROHIBIDAS = ["Bash(git push:*)", "Bash(git switch:*)", "Bash(git checkout:*)", "Bash(git reset:*)",
              "Bash(git rebase:*)", "Bash(git merge:*)", "Bash(gh:*)", "Bash(*scripts/tareas.py*)"]


def ahora() -> dt.datetime:
    return dt.datetime.now()


def log(msg: str) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ahora():%Y-%m-%d %H:%M:%S}] {msg}\n")


def guardar_estado(**kw) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps({"actualizado": f"{ahora():%Y-%m-%d %H:%M:%S}", **kw}, ensure_ascii=False,
                                 indent=1), encoding="utf-8")


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=check)


def sin_suspender(activar: bool) -> None:
    """Que Windows no se duerma mientras el trabajador corre (la pantalla sí se puede apagar)."""
    if not ES_WINDOWS:
        return
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | (0x00000001 if activar else 0))
    except Exception:
        pass


def encontrar_claude() -> str:
    if os.environ.get("FIELDSHIFT_CLAUDE"):
        return os.environ["FIELDSHIFT_CLAUDE"]
    cand = Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
    if ES_WINDOWS and cand.exists():
        return str(cand)
    for c in (Path.home() / ".local" / "bin" / "claude", Path.home() / ".claude" / "local" / "claude"):
        if not ES_WINDOWS and c.exists():
            return str(c)     # un proceso en segundo plano puede no tener el PATH de la terminal
    for nombre in ("claude.exe", "claude"):
        w = shutil.which(nombre)
        if w and not w.lower().endswith((".cmd", ".ps1", ".bat")):
            return w
    w = shutil.which("claude")
    if not w:
        sys.exit("No encuentro el CLI de Claude Code (claude). Instalalo y entrá con tu cuenta.")
    return w


def entorno() -> dict:
    env = {k: v for k, v in os.environ.items()
           if not (k.upper() in VARS_SESION or (k.upper().startswith(PREFIJOS_SESION) and k.upper() not in CONSERVAR))}
    env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "DISABLE_AUTOUPDATER": "1"})
    return env


def parse_reinicio(texto: str):
    """Hora en que se renueva el límite de uso, si el mensaje la trae."""
    m = re.search(r"\|(\d{10})\b", texto)
    if m:
        return dt.datetime.fromtimestamp(int(m.group(1)))
    # "resets Nov 16, 9am": límite semanal, con fecha
    m = re.search(r"resets?\s+(?:on\s+)?([a-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*([ap])\.?\s?m\b",
                  texto, re.I)
    meses = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    if m and m.group(1).lower() in meses:
        h = int(m.group(3)) % 12 + (12 if m.group(5).lower() == "p" else 0)
        c = dt.datetime(ahora().year, meses.index(m.group(1).lower()) + 1, int(m.group(2)), h, int(m.group(4) or 0))
        return c.replace(year=c.year + 1) if c < ahora() - dt.timedelta(days=1) else c
    m = re.search(r"resets?\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*([ap])\.?\s?m\b", texto, re.I)
    if m:
        h = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "p" else 0)
        c = ahora().replace(hour=h, minute=int(m.group(2) or 0), second=0, microsecond=0)
        return c + dt.timedelta(days=1) if c <= ahora() else c
    m = re.search(r"resets?\s+in\s+(?:(\d+)\s*h(?:ours?)?)?\s*(?:(\d+)\s*m(?:in(?:utes?)?)?)?", texto, re.I)
    if m and (m.group(1) or m.group(2)):
        return ahora() + dt.timedelta(hours=int(m.group(1) or 0), minutes=int(m.group(2) or 0))
    return None


def dormir(hasta: dt.datetime, fin: dt.datetime, motivo: str) -> None:
    hasta = min(hasta, fin)
    if hasta <= ahora():
        return
    log(f"espero hasta las {hasta:%H:%M}: {motivo}")
    guardar_estado(estado="esperando", hasta=f"{hasta:%H:%M}", motivo=motivo)
    while ahora() < hasta and not STOP.exists():
        time.sleep(min(30.0, max(1.0, (hasta - ahora()).total_seconds())))


def matar_arbol(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if ES_WINDOWS:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    else:
        import signal
        try:
            os.killpg(proc.pid, signal.SIGKILL)   # el agente y todo lo que lanzó (sesión propia)
        except (ProcessLookupError, PermissionError):
            proc.kill()


# ---------- tablero ----------

def ns(**kw) -> argparse.Namespace:
    return argparse.Namespace(sin_git=False, **kw)


def llamar(fn, *a) -> str | None:
    """Corre una función de tareas.py; devuelve el mensaje de error si terminó con sys.exit."""
    try:
        fn(*a)
        return None
    except SystemExit as e:
        return str(e.code)


CODIGO = ("scripts/trabajador.py", "scripts/tareas.py")
SIN_CAMBIOS = [0]   # tareas seguidas que terminaron sin cambios
HASH_INICIO: dict[str, str] = {}


def hash_codigo(ref: str | None) -> dict[str, str]:
    """Blob de git de cada archivo de CODIGO: en disco (ref None) o en `ref`."""
    out = {}
    for f in CODIGO:
        r = git("hash-object", f, check=False) if ref is None else git("rev-parse", f"{ref}:{f}", check=False)
        out[f] = r.stdout.strip()
    return out


def relanzar_si_cambio(fin: dt.datetime) -> None:
    """Si main trae otro trabajador.py o tareas.py, actualiza la copia y se vuelve a lanzar con las horas que quedan."""
    git("fetch", "-q", "origin", "main", check=False)
    nuevo = hash_codigo("origin/main")
    if not HASH_INICIO or not all(nuevo.values()) or nuevo == HASH_INICIO:
        return
    log("hay una versión nueva del trabajador en main: me actualizo y sigo")
    bitacora(os.environ.get("FIELDSHIFT_MAQUINA", ""), "trabajador actualizado desde main")
    git("switch", "-q", "main", check=False)
    git("reset", "-q", "--hard", "origin/main", check=False)
    argv = list(sys.argv)
    horas = max(0.5, (fin - ahora()).total_seconds() / 3600)
    if "--horas" in argv:
        argv[argv.index("--horas") + 1] = f"{horas:.2f}"
    else:
        argv[argv.index("correr") + 1:argv.index("correr") + 1] = ["--horas", f"{horas:.2f}"]
    nuevo_cmd = [sys.executable, "-X", "utf8"] + argv
    sin_suspender(False)
    if ES_WINDOWS:
        sys.exit(subprocess.call(nuevo_cmd))   # en Windows execv cambia de proceso: el padre espera al hijo
    os.execv(sys.executable, nuevo_cmd)       # en Linux y macOS sigue el mismo proceso (el pid no cambia)


def pausada(maquina: str) -> bool:
    """`pausada: true` en coordinacion/maquinas.yaml (del tablero actualizado): la máquina no toma tareas."""
    tareas.traer(False)
    try:
        datos = yaml.safe_load(tareas.MAQUINAS.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return False
    return bool((datos.get("maquinas", {}).get(maquina) or {}).get("pausada"))


def elegir_y_tomar(maquina: str, plan: str, estados: list[str], solo: str | None) -> tuple[str, dict, str] | None:
    tareas.traer(False)
    filas = tareas.todas()
    hechas = {str(m.get("id")) for _, m, _ in filas if m.get("estado") == "hecha"}
    cands = []
    for _, m, _ in filas:
        tid = str(m.get("id"))
        if solo and tid != solo.upper():
            continue
        if m.get("estado") != "libre" or m.get("auto") is False:
            continue
        if m.get("plan_minimo") == "max" and plan == "pro":
            continue
        if any(d not in hechas for d in (m.get("depende_de") or [])):
            continue
        propios = bool(set(m.get("estados") or []) & set(estados))
        # Max deja las tareas Pro para las Pro: primero las que solo puede hacer una Max
        de_otro_plan = plan == "max" and m.get("plan_minimo") != "max"
        cands.append((de_otro_plan, not propios, tid))
    for *_, tid in sorted(cands):
        err = llamar(tareas.cmd_tomar, ns(id=tid, maquina=maquina))
        if err is None:
            p, meta, cuerpo = tareas.buscar(tid)
            return tid, meta, p.read_text(encoding="utf-8")
        log(f"no pude tomar {tid}: {err}")
    return None


def anotar(tid: str, maquina: str, estado: str | None, texto: str) -> None:
    err = llamar(tareas.cambiar, ns(id=tid, maquina=maquina), estado, texto)
    if err:
        log(f"no pude anotar en {tid}: {err}")


def bitacora(maquina: str, texto: str) -> None:
    err = llamar(tareas.cmd_bitacora, ns(maquina=maquina, texto=texto))
    if err:
        log(f"no pude escribir la bitácora: {err}")


# ---------- una tarea ----------

def preparar_rama(rama: str) -> bool:
    """Deja la copia en la rama de la tarea, limpia. True si la rama ya existía en GitHub (continuación)."""
    git("fetch", "-q", "--prune", "origin")
    existe = git("rev-parse", "--verify", "-q", f"origin/{rama}", check=False).returncode == 0
    git("reset", "-q", "--hard")
    git("clean", "-q", "-fd")          # sin -x: data/ y .trabajador/ (ignorados) no se tocan
    git("switch", "-q", "-C", rama, f"origin/{rama}" if existe else "origin/main")
    return existe


def lanzar_agente(claude: str, prompt: str, tid: str, minutos: float, a) -> dict:
    marca = f"{tid}-{ahora():%Y%m%d-%H%M}"
    prompt_p, log_p, err_p = DIR / f"{marca}.prompt.md", DIR / f"{marca}.log.jsonl", DIR / f"{marca}.stderr.txt"
    prompt_p.write_text(prompt, encoding="utf-8")
    cmd = [claude, "-p", "--output-format", "stream-json", "--verbose", "--model", a.modelo, "--effort", a.effort,
           "--permission-mode", a.permisos, "--permission-prompts", "none", "--no-session-persistence",
           "--disallowedTools", *PROHIBIDAS]
    res = {"rc": None, "timeout": False, "texto": "", "error": False, "hubo_resultado": False, "limite": False,
           "costo": 0.0, "minutos": 0.0, "log": log_p.name}
    t0 = time.time()
    extra = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if ES_WINDOWS else {"start_new_session": True}
    with open(prompt_p, "rb") as fi, open(log_p, "wb") as fo, open(err_p, "wb") as fe:
        try:
            proc = subprocess.Popen(cmd, cwd=REPO, env=entorno(), stdin=fi, stdout=fo, stderr=fe, **extra)
        except OSError as e:
            res.update(error=True, no_arranca=True, texto=f"no se pudo lanzar Claude: {e}")
            return res
        try:
            while proc.poll() is None:
                if time.time() - t0 > minutos * 60 + 90:
                    res["timeout"] = True
                    break
                time.sleep(5)
        finally:
            matar_arbol(proc)
    res["rc"] = proc.wait()
    res["minutos"] = (time.time() - t0) / 60
    for linea in log_p.read_text(encoding="utf-8", errors="replace").splitlines():
        if linea.startswith("{") and '"result"' in linea:
            try:
                m = json.loads(linea)
            except Exception:
                continue
            if m.get("type") == "result":
                res.update(hubo_resultado=True, error=bool(m.get("is_error")), costo=float(m.get("total_cost_usd") or 0),
                           texto=str(m.get("result") or m.get("subtype") or "")[:2000])
    stderr = err_p.read_text(encoding="utf-8", errors="replace")[-3000:]
    problema = res["error"] or res["rc"] not in (0, None) or not res["hubo_resultado"]
    if problema and not res["timeout"]:
        junto = res["texto"] + "\n" + stderr
        if RE_LIMITE.search(junto):
            res["limite"] = True
        elif RE_AUTH.search(junto):
            res["auth"] = True
        if not res["texto"]:
            res["texto"] = stderr.strip()[-500:] or f"código de salida {res['rc']}"
    return res


def commits_nuevos() -> int:
    r = git("rev-list", "--count", "origin/main..HEAD", check=False)
    return int(r.stdout.strip() or 0) if r.returncode == 0 else 0


MAX_MB_WIP = 5   # un archivo nuevo más grande que esto no entra en el commit WIP


def sacar_datos_del_indice() -> list[str]:
    """Saca del índice los archivos nuevos que son datos: bajo data/, .zip o de más de MAX_MB_WIP.

    El commit WIP junta todo lo que quedó en la carpeta; sin esto, zips y CSV bajados de los releases
    terminaban en los PR (PR 66 y 68). Los archivos quedan en disco, sin seguimiento.
    """
    nuevos = git("diff", "--cached", "--name-only", "--diff-filter=A", check=False).stdout.splitlines()
    fuera = []
    for f in nuevos:
        ruta = REPO / f
        grande = ruta.is_file() and ruta.stat().st_size > MAX_MB_WIP * 1e6
        if f.startswith("data/") or f.lower().endswith(".zip") or grande:
            fuera.append(f)
    for i in range(0, len(fuera), 100):
        git("reset", "-q", "--", *fuera[i:i + 100], check=False)
    return fuera


def guardar_sin_commit(maquina: str) -> None:
    if git("status", "--porcelain").stdout.strip():
        git("add", "-A")
        fuera = sacar_datos_del_indice()
        if fuera:
            log(f"WIP sin {len(fuera)} archivos de datos (quedan en disco): {', '.join(fuera[:5])}")
        git("-c", f"user.name=trabajador {maquina}", "-c", "user.email=trabajador@fieldshift.invalid",
            "commit", "-q", "-m", "WIP (trabajador): cambios sin commit al cortar la sesión", check=False)


def abrir_pr(tid: str, titulo: str, rama: str, cuerpo: str, maquina: str, sin_pr: bool) -> str:
    r = git("push", "-q", "--force-with-lease", "-u", "origin", rama, check=False)
    if r.returncode != 0:
        return f"push falló: {r.stderr.strip()[:300]}"
    if sin_pr:
        return f"rama {rama} subida (sin PR, modo prueba)"
    gh = ["gh", "pr", "list", "--head", rama, "--state", "open", "--json", "number,url"]
    hay = subprocess.run(gh, cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    lista = json.loads(hay.stdout or "[]") if hay.returncode == 0 else []
    if lista:
        return f"PR #{lista[0]['number']} actualizado"
    pie = (f"\n\n---\nAbierto por el trabajador automático de `{maquina}` (tarea {tid}). "
           "Lo revisa y lo une `max-1`.\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n")
    body = DIR / f"{tid}.pr.md"
    body.write_text(cuerpo + pie, encoding="utf-8")
    c = subprocess.run(["gh", "pr", "create", "--base", "main", "--head", rama, "--title", f"{tid}: {titulo}",
                        "--body-file", str(body)], cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    if c.returncode != 0:
        return f"gh pr create falló: {c.stderr.strip()[:300]}"
    m = re.search(r"/pull/(\d+)", c.stdout)
    return f"PR #{m.group(1)}" if m else c.stdout.strip()


def minutos_para(meta: dict, a, fin: dt.datetime) -> float:
    # tope: el de la línea de comandos si se pasó; si no, el campo `minutos` de la tarea; si no, el del plan
    tope = a.minutos_tarea if a.minutos_cli else float(meta.get("minutos") or a.minutos_tarea)
    return max(10.0, min(tope, (fin - ahora()).total_seconds() / 60 - 5))


def hacer_tarea(claude: str, tid: str, meta: dict, texto_tarea: str, maquina: str, plan: str, estados: list[str],
                fin: dt.datetime, a) -> None:
    rama = f"tarea/{tid}-auto"
    resultado_p = DIR / f"{tid}.resultado.md"
    intentos_fallidos = 0
    while True:
        if fin - ahora() < dt.timedelta(minutes=15):
            # no alcanza para un intento: la tarea vuelve a la cola en vez de lanzar a Claude pasado el fin
            anotar(tid, maquina, "libre", f"soltada: {maquina} llegó al fin de su turno")
            return
        continua = preparar_rama(rama)
        resultado_p.unlink(missing_ok=True)
        minutos = minutos_para(meta, a, fin)
        python = ".venv/Scripts/python" if ES_WINDOWS else ".venv/bin/python"   # sirve en PowerShell y Git Bash
        plantilla = git("show", "origin/main:coordinacion/prompt_trabajador.md").stdout
        prompt = (plantilla.replace("{maquina}", maquina).replace("{plan}", plan).replace("{minutos}", f"{minutos:.0f}")
                  .replace("{id}", tid).replace("{tarea}", texto_tarea).replace("{rama}", rama)
                  .replace("{python}", python).replace("{estados}", ",".join(estados) or "ninguno")
                  .replace("{resultado}", resultado_p.as_posix())
                  .replace("{continuacion}", "Un intento anterior ya dejó commits en esta rama: mirá `git log "
                           "origin/main..HEAD` y el resultado anterior en la tarea, y seguí desde ahí." if continua
                           else "La rama sale de `main` actualizado."))
        log(f"{tid}: lanzo Claude ({a.modelo}, {a.effort}, {minutos:.0f} min){' — continuación' if continua else ''}")
        guardar_estado(estado="trabajando", tarea=tid, desde=f"{ahora():%H:%M}", minutos=round(minutos))
        res = lanzar_agente(claude, prompt, tid, minutos, a)
        log(f"{tid}: terminó en {res['minutos']:.0f} min rc={res['rc']} timeout={res['timeout']} "
            f"límite={res['limite']} error={res['error']} costo≈{res['costo']:.2f} USD")
        guardar_sin_commit(maquina)
        n = commits_nuevos()
        cuerpo = resultado_p.read_text(encoding="utf-8").strip() if resultado_p.exists() else ""
        if res.get("auth") or res.get("no_arranca"):
            motivo = ("Claude no tiene la sesión iniciada en esta máquina" if res.get("auth")
                      else f"no se pudo lanzar Claude ({res['texto'][:200]})")
            anotar(tid, maquina, "libre", f"soltada: {motivo}")
            log(f"{motivo}: paro el trabajador")
            STOP.write_text(motivo, encoding="utf-8")
            return
        if res["limite"]:
            if n:
                abrir_pr(tid, meta.get("titulo", ""), rama, "", maquina, sin_pr=True)   # solo guarda la rama
            anotar(tid, maquina, None, f"corte por el límite de uso de Claude; {n} commits guardados en {rama}. "
                                       "El trabajador sigue cuando se renueve.")
            hasta = parse_reinicio(res["texto"]) or (ahora() + dt.timedelta(minutes=30))
            if hasta - ahora() > dt.timedelta(hours=1):
                # límite largo (semanal): la tarea vuelve a la cola para otra máquina
                anotar(tid, maquina, "libre", f"soltada: {maquina} sin cuota de Claude hasta {hasta:%d/%m %H:%M}")
                dormir(hasta + dt.timedelta(minutes=2), fin, "límite de uso de Claude")
                return
            dormir(hasta + dt.timedelta(minutes=2), fin, "límite de uso de Claude")
            if STOP.exists() or ahora() >= fin:
                anotar(tid, maquina, "libre", f"soltada: el trabajador paró con la tarea a medias (rama {rama})")
                return
            continue
        if n == 0:
            intentos_fallidos += 1
            detalle = (cuerpo or res["texto"] or "sin detalle")[:400].replace("\n", " ")
            if intentos_fallidos >= 2 or ahora() >= fin - dt.timedelta(minutes=15) or STOP.exists():
                SIN_CAMBIOS[0] += 1
                if SIN_CAMBIOS[0] >= 2:
                    # la tarea anterior tampoco avanzó: el problema es de esta máquina, no de la tarea
                    anotar(tid, maquina, "libre", f"soltada: {maquina} no logra cambios en ninguna tarea; espera 30 min. {detalle}")
                    bitacora(maquina, f"{tid}: devuelta; la máquina espera 30 min ({detalle[:120]})")
                    dormir(ahora() + dt.timedelta(minutes=30), fin, "dos tareas seguidas sin cambios")
                    return
                anotar(tid, maquina, "bloqueada", f"bloqueada: el trabajador no logró cambios en 2 intentos. {detalle}")
                bitacora(maquina, f"{tid}: bloqueada sin cambios ({detalle[:120]})")
                return
            anotar(tid, maquina, None, f"intento sin cambios ({detalle}); reintento")
            continue
        SIN_CAMBIOS[0] = 0
        incompleta = (not cuerpo) or cuerpo.upper().startswith("INCOMPLETA") or res["timeout"]
        if not cuerpo:
            cuerpo = ("INCOMPLETA: el agente no dejó resultado.\n\nÚltimo mensaje del agente:\n\n"
                      + (res["texto"] or "(ninguno)"))
        donde = abrir_pr(tid, meta.get("titulo", ""), rama, cuerpo, maquina, a.sin_pr)
        log(f"{tid}: {donde}")
        if "falló" in donde:
            anotar(tid, maquina, "bloqueada", f"bloqueada: el trabajo quedó en la rama {rama} pero {donde}")
            bitacora(maquina, f"{tid}: no pude publicar ({donde[:120]})")
            return
        if incompleta:
            primera = cuerpo.splitlines()[0][:300]
            anotar(tid, maquina, "libre", f"soltada: quedó a medias, {donde}. {primera}")
            bitacora(maquina, f"{tid}: a medias, {donde}")
        else:
            anotar(tid, maquina, "hecha", f"terminada por el trabajador: {donde}, falta la revisión de max-1")
            bitacora(maquina, f"{tid}: terminada, {donde}")
        return


# ---------- comandos ----------

def correr(a) -> None:
    maquina = os.environ.get("FIELDSHIFT_MAQUINA", "").strip()
    if not maquina:
        sys.exit("Falta FIELDSHIFT_MAQUINA (max-1, max-2, pro-1 a pro-4)")
    estados = [s.strip().upper() for s in os.environ.get("FIELDSHIFT_ESTADOS", "").split(",") if s.strip()]
    tareas.traer(False)
    plan = tareas.plan_de(maquina) or ("max" if maquina.startswith("max") else "pro")
    a.minutos_cli = a.minutos_tarea is not None
    if a.minutos_tarea is None:
        a.minutos_tarea = 150 if plan == "max" else 60
    claude = encontrar_claude()
    DIR.mkdir(parents=True, exist_ok=True)
    STOP.unlink(missing_ok=True)
    HASH_INICIO.update(hash_codigo(None))
    # una tarea tomada por esta máquina al arrancar quedó de una corrida cortada (parar ya, corte de luz): vuelve a la cola
    for _, m, _ in tareas.todas():
        if m.get("estado") == "tomada" and m.get("maquina") == maquina:
            anotar(str(m.get("id")), maquina, "libre", "soltada al arrancar: quedó tomada de una corrida anterior de esta máquina")
    fin = ahora() + dt.timedelta(hours=a.horas)
    log(f"arranca {maquina} (plan {plan}, estados {','.join(estados) or '-'}) hasta las {fin:%H:%M}; "
        f"{a.modelo}/{a.effort}, {a.minutos_tarea} min por tarea")
    sin_suspender(True)
    hechas = 0
    try:
        while ahora() < fin - dt.timedelta(minutes=15) and not STOP.exists():
            if a.max_tareas and hechas >= a.max_tareas:
                log(f"llegué al tope de {a.max_tareas} tareas")
                break
            relanzar_si_cambio(fin)
            if pausada(maquina):
                dormir(ahora() + dt.timedelta(minutes=15), fin, "pausada en coordinacion/maquinas.yaml")
                continue
            elegida = elegir_y_tomar(maquina, plan, estados, a.solo)
            if not elegida:
                if a.solo:
                    log(f"{a.solo} no está disponible: termino")
                    break
                dormir(ahora() + dt.timedelta(minutes=15), fin, "no hay tareas libres para mí")
                continue
            tid, meta, texto = elegida
            log(f"tomé {tid}: {meta.get('titulo')}")
            bitacora(maquina, f"{tid}: tomada por el trabajador")
            hacer_tarea(claude, tid, meta, texto, maquina, plan, estados, fin, a)
            hechas += 1
            if a.solo:
                break
    finally:
        sin_suspender(False)
        git("reset", "-q", "--hard", check=False)
        git("switch", "-q", "main", check=False)
        guardar_estado(estado="parado", tareas=hechas)
        log(f"fin: {hechas} tareas")


def estado(_a) -> None:
    if ESTADO.exists():
        print(ESTADO.read_text(encoding="utf-8"))
    if LOG.exists():
        print("".join(LOG.read_text(encoding="utf-8").splitlines(keepends=True)[-25:]))
    else:
        print("El trabajador no corrió todavía en esta copia.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("correr")
    c.add_argument("--horas", type=float, default=24)
    c.add_argument("--minutos-tarea", type=float, default=None, help="por defecto 60 en Pro y 150 en Max")
    c.add_argument("--modelo", default="opus")
    c.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    c.add_argument("--permisos", default="auto", choices=["auto", "acceptEdits", "dontAsk"])
    c.add_argument("--solo", default=None, help="hacer solo esta tarea (por ejemplo T009)")
    c.add_argument("--max-tareas", type=int, default=0)
    c.add_argument("--sin-pr", action="store_true", help="sube la rama pero no abre el PR (para probar)")
    sub.add_parser("estado")
    a = ap.parse_args()
    correr(a) if a.cmd == "correr" else estado(a)


if __name__ == "__main__":
    main()
