#!/usr/bin/env python
"""Hook PreToolUse del research agent.

Lo instala el orquestador (loop/run.py) solo durante una corrida, desde su copia bloqueada,
con --settings. En sesiones normales (sin RA_RUN_ID) no hace nada.

Bloquea:
  - escribir fuera de las rutas de la tarea de la ronda (RA_ALLOWED)
  - tocar archivos bloqueados (RA_LOCKED: loop/, .claude/, CLAUDE.md, config/config.yaml...)
  - modificar o borrar archivos que ya existen en data/raw/
  - leer o imprimir credenciales (.netrc, _netrc, .env)
  - comandos de git que cambian el repo (el orquestador maneja git)

  - correr el orquestador o la aprobación de checks, y cambiar permisos en data/raw/

Sale con código 2 y el motivo en stderr, que Claude recibe como respuesta de la herramienta.
Si algo falla adentro del hook durante una corrida, bloquea (fail closed).
Es una primera barrera: el orquestador además verifica los hashes de los archivos bloqueados
y el alcance del diff después de cada ronda.
"""
import json
import os
import re
import shlex
import sys

GIT_OK = {"status", "diff", "log", "show", "blame", "ls-files", "rev-parse", "describe", "shortlog",
          "grep", "cat-file", "ls-tree", "help", "version", "--version", "reflog"}

BORRAR = r"(rm|rmdir|del|erase|rd|unlink|shred|truncate|remove-item|ri|clear-content)"
ESCRIBIR = (r"(rm|rmdir|del|erase|rd|unlink|shred|truncate|touch|mkdir|md|mv|move|ren|rename|cp|copy|xcopy|robocopy|tee|"
            r"chmod|chown|attrib|icacls|dd|install|ln|remove-item|ri|move-item|mi|rename-item|rni|copy-item|cpi|"
            r"set-content|sc|add-content|ac|out-file|clear-content|new-item|ni|set-itemproperty)")


def denegar(msg: str):
    texto = "BLOQUEADO por el orquestador del research agent: " + msg + "\n"
    try:
        sys.stderr.buffer.write(texto.encode("utf-8", "replace"))
        sys.stderr.flush()
    except Exception:
        pass
    sys.exit(2)


def normalizar(p: str, cwd: str) -> str:
    p = str(p).strip().strip('"').strip("'").replace("\\", "/")
    m = re.match(r"^/([a-zA-Z])/(.*)$", p)
    if m:
        p = f"{m.group(1)}:/{m.group(2)}"
    if p.startswith("~"):
        p = os.path.expanduser(p).replace("\\", "/")
    if not re.match(r"^[a-zA-Z]:/", p) and not p.startswith("/"):
        p = cwd.replace("\\", "/").rstrip("/") + "/" + p
    p = os.path.normpath(p).replace("\\", "/")
    return p


def relativo(p_abs: str, repo: str):
    a, r = p_abs.lower(), repo.lower().rstrip("/")
    if a == r:
        return ""
    if a.startswith(r + "/"):
        return p_abs[len(r) + 1:]
    return None


def coincide(rel: str, regla: str) -> bool:
    rel_l, regla_l = rel.lower(), regla.lower()
    if regla_l.endswith("/"):
        return rel_l.startswith(regla_l) or rel_l + "/" == regla_l
    return rel_l == regla_l


def es_secreto(ruta: str) -> bool:
    base = ruta.replace("\\", "/").rstrip("/").split("/")[-1].lower()
    return base in (".netrc", "_netrc", ".env") or base.startswith(".env.")


def decidir_escritura(rel, p_abs, permitidas, bloqueadas):
    if rel is None:
        denegar(f"no se puede escribir fuera del repo ({p_abs}).")
    if es_secreto(rel):
        denegar("las credenciales no se tocan.")
    mejor_perm = max((len(x) for x in permitidas if coincide(rel, x)), default=-1)
    mejor_bloq = max((len(x) for x in bloqueadas if coincide(rel, x)), default=-1)
    if mejor_bloq > mejor_perm:
        denegar(f"'{rel}' está bloqueado durante la corrida (checks, orquestador, configuración). "
                "Si hace falta un cambio ahí, anotalo en loop/notes/decisiones.md.")
    if rel.lower().startswith("data/raw/") and os.path.exists(p_abs):
        denegar(f"data/raw/ es inmutable: '{rel}' ya existe y no se modifica (regla 2 del CLAUDE.md).")
    if mejor_perm < 0:
        denegar(f"'{rel}' está fuera de las rutas de esta ronda. Podés escribir en: {', '.join(permitidas)}")


def segmentos(cmd: str):
    return [s.strip() for s in re.split(r"&&|\|\||;|\||\n", cmd) if s.strip()]


def tokens(seg: str):
    try:
        return shlex.split(seg, posix=True)
    except ValueError:
        return seg.split()


def subcomando_git(toks):
    for i, t in enumerate(toks):
        if t.lower() in ("git", "git.exe") or t.lower().endswith("/git") or t.lower().endswith("/git.exe"):
            j = i + 1
            while j < len(toks):
                x = toks[j]
                if x in ("-c", "-C", "--git-dir", "--work-tree", "--namespace"):
                    j += 2
                    continue
                if x.startswith("-"):
                    j += 1
                    continue
                return x.lower()
            return None
    return None


def revisar_comando(cmd: str, repo: str, bloqueadas, permitidas, cwd: str = ""):
    c = cmd.replace("\\", "/")
    cl = c.lower()
    # Las rutas absolutas del repo se tratan como relativas.
    r = repo.replace("\\", "/").rstrip("/").lower()
    variantes = {r, "/" + r[0] + r[2:] if re.match(r"^[a-z]:/", r) else r}
    for v in sorted(variantes, key=len, reverse=True):
        cl = cl.replace(v + "/", "./")
    # Las rutas permitidas que viven dentro de una bloqueada (loop/notes/, el reporte) no cuentan.
    for p in sorted(permitidas, key=len, reverse=True):
        pl = p.lower()
        if any(pl.startswith(b.lower()) and pl != b.lower() for b in bloqueadas):
            cl = cl.replace(pl, "__permitido__/")
    if re.search(r"(\.netrc|_netrc)", cl) or re.search(r"(^|[\s/'\"=])\.env(\.[a-z0-9_]+)?(?=$|[\s'\"])", cl):
        denegar("no leas ni toques credenciales (.netrc/.env). Las librerías (requests, earthaccess) las leen solas.")
    if re.search(r"(^|[\s;|&(])(printenv|env|set)\s*($|[|;&>])", cl) or re.search(r"(get-childitem|gci|ls|dir)\s+env:", cl):
        denegar("no listes variables de entorno (pueden tener tokens).")
    if re.search(r"loop/(run|aprobar_checks)\.py", cl):
        denegar("el orquestador y la aprobación de checks los corre solo el humano.")
    # loop/STOP frena la corrida: lo crea solo el humano (también con cd loop, o con el cwd en loop/).
    msg_stop = "loop/STOP lo crea solo el humano para frenar la corrida: no lo toques."
    if re.search(r"loop/+stop\b", cl):
        denegar(msg_stop)
    cw = (cwd or "").replace("\\", "/").rstrip("/").lower()
    en_loop = any(cw == v + "/loop" or cw.startswith(v + "/loop/") for v in variantes)
    if re.search(r"(^|[\s;&|(])(cd|pushd|set-location|sl)\s+['\"]?(\./)?loop(/|['\"\s;&|]|$)", cl):
        en_loop = True
    if en_loop and re.search(r"(^|[\s'\"=/])stop($|[\s'\";|&])", cl):
        denegar(msg_stop)
    for seg in segmentos(cl):
        toks = tokens(seg)
        sub = subcomando_git(toks)
        if sub is not None and sub not in GIT_OK:
            denegar(f"'git {sub}' no está permitido: el orquestador maneja git (commit/reset). Podés usar git status, diff y log.")
        for b in bloqueadas:
            bl = b.lower()
            patron = r"(^|[\s'\"=(./])" + re.escape(bl)
            if not re.search(patron, seg):
                continue
            if (re.search(r"(^|\s)" + ESCRIBIR + r"(\s|$)", seg) or re.search(r">{1,2}\s*['\"]?[^\s]*" + re.escape(bl), seg)
                    or re.search(r"sed\s+-i|perl\s+-i", seg)
                    or re.search(r"open\([^)]*" + re.escape(bl) + r"[^)]*['\"]\s*,\s*['\"][wax]", seg)
                    or re.search(r"(write_text|write_bytes|unlink|rmtree|remove|rename|replace|touch|mkdir|makedirs|copy|"
                                 r"copyfile|copy2|copytree|move|symlink_to|hardlink_to)\(", seg)):
                denegar(f"el comando modifica '{b}', que está bloqueado durante la corrida. Para leerlo usá la herramienta Read.")
        if re.search(r"(^|[\s'\"=(./])data/raw/", seg) and re.search(r"(^|\s)" + BORRAR + r"(\s|$)", seg):
            denegar("data/raw/ es inmutable: no se borran archivos bajados (regla 2 del CLAUDE.md).")
        if re.search(r"(^|[\s'\"=(./])data/raw/", seg) and (
                re.search(r"(^|\s)(attrib|chmod|icacls|takeown|set-itemproperty|sp)(\s|$)", seg) or "chmod(" in seg):
            denegar("los archivos de data/raw/ quedan de solo lectura a propósito: no se les cambian los permisos.")


def main():
    if not os.environ.get("RA_RUN_ID"):
        sys.exit(0)
    try:
        # Claude Code manda el JSON en UTF-8; se lee en bytes para no depender de la consola.
        data = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
        revisar(data)
    except SystemExit:
        raise
    except Exception as e:
        # Durante una corrida, ante un error inesperado se bloquea (fail closed).
        denegar(f"error interno del guardián ({type(e).__name__}: {e}). Probá de otra forma.")
    sys.exit(0)


def revisar(data):
    repo = normalizar(os.environ.get("RA_REPO", "."), os.getcwd())
    permitidas = json.loads(os.environ.get("RA_ALLOWED", "[]"))
    bloqueadas = json.loads(os.environ.get("RA_LOCKED", "[]"))
    cwd = data.get("cwd") or repo
    tool = data.get("tool_name", "") or ""
    ti = data.get("tool_input", {}) or {}

    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        ruta = ti.get("file_path") or ti.get("notebook_path") or ""
        if not ruta:
            sys.exit(0)
        p_abs = normalizar(ruta, cwd)
        decidir_escritura(relativo(p_abs, repo), p_abs, permitidas, bloqueadas)
    elif tool in ("Read", "Grep", "Glob"):
        for k in ("file_path", "path", "pattern", "glob"):
            v = ti.get(k)
            if v and es_secreto(str(v)):
                denegar("las credenciales no se leen.")
    elif tool in ("Bash", "PowerShell"):
        revisar_comando(ti.get("command", "") or "", repo, bloqueadas, permitidas, cwd)


if __name__ == "__main__":
    main()
