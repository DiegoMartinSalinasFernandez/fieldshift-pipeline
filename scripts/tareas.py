"""Tablero de tareas compartido entre las máquinas (coordinacion/tareas/*.md).

Cada tarea es un archivo con un encabezado YAML (entre líneas ---) y un cuerpo en Markdown. Las máquinas
se coordinan solo por git: tomar una tarea es editar su archivo, hacer commit y push a main. Si otra
máquina la tomó antes, el script lo ve al traer lo nuevo y avisa. Ver MAQUINAS.md.

La máquina sale de la variable FIELDSHIFT_MAQUINA (max-1, max-2, pro-1, pro-2) o de --maquina.

Uso:
  python scripts/tareas.py listar [--libres] [--plan pro|max]
  python scripts/tareas.py ver T003
  python scripts/tareas.py tomar T003
  python scripts/tareas.py nota T003 "texto"
  python scripts/tareas.py soltar T003 "motivo"          # vuelve a libre (por ejemplo, se acabó el uso de Pro)
  python scripts/tareas.py bloquear T003 "motivo"
  python scripts/tareas.py terminar T003 "qué quedó y dónde"
  python scripts/tareas.py nueva "Título" --plan pro [--estados KS] [--depende T001,T002]
  python scripts/tareas.py bitacora "qué hice hoy"       # agrega una línea a coordinacion/bitacora/<maquina>.md
Opciones comunes: --maquina NOMBRE, --sin-git (trabaja sobre la carpeta actual sin pull, commit ni push).

Todo se lee y se publica desde .tablero/, una copia de main aparte de tu carpeta de trabajo: podés estar en
cualquier rama y el tablero se actualiza igual. Lo que ves en coordinacion/ de tu rama puede estar viejo.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
DIR = REPO / "coordinacion" / "tareas"           # usar_base() los apunta a .tablero
MAQUINAS = REPO / "coordinacion" / "maquinas.yaml"
ESTADOS = ("libre", "tomada", "bloqueada", "hecha")
PLANES = ("pro", "max")


def ahora() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


# ---------- git ----------
# El tablero se lee y se escribe en una copia aparte de main (REPO/.tablero, un git worktree), nunca en la
# carpeta de trabajo: así anotar en una tarea no arrastra la rama de código en la que esté la máquina, y
# descartar un cambio que chocó con otra máquina no toca nada más.

TABLERO = REPO / ".tablero"
BASE = REPO          # carpeta de donde se leen las tareas: REPO con --sin-git, TABLERO con git


def git(*args: str, donde: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(donde or BASE), *args], capture_output=True, text=True, check=check)


def usar_base(base: Path) -> None:
    global BASE, DIR, MAQUINAS
    BASE, DIR, MAQUINAS = base, base / "coordinacion" / "tareas", base / "coordinacion" / "maquinas.yaml"


def traer(sin_git: bool) -> None:
    """Deja .tablero igual a origin/main (lo crea la primera vez)."""
    if sin_git:
        usar_base(REPO)
        return
    if git("fetch", "-q", "origin", "main", donde=REPO, check=False).returncode != 0:
        sys.exit("git fetch falló: ¿hay conexión y acceso al repo? (gh auth status)")
    if not (TABLERO / ".git").exists():
        r = git("worktree", "add", "-q", "--detach", str(TABLERO), "origin/main", donde=REPO, check=False)
        if r.returncode != 0:
            sys.exit("No pude crear la copia del tablero en .tablero: " + r.stderr.strip())
    usar_base(TABLERO)
    git("reset", "-q", "--hard", "origin/main")


def publicar(rutas: list[Path], mensaje: str, sin_git: bool) -> None:
    """Commit solo de esos archivos en .tablero y push a main. Si otra máquina empujó antes, rebase y reintento."""
    if sin_git:
        print(f"(sin git) {mensaje}")
        return
    rel = [str(p.relative_to(BASE)) for p in rutas]
    git("add", "--", *rel)
    git("commit", "-q", "-m", mensaje, "--", *rel)
    for _ in range(4):
        if git("push", "-q", "origin", "HEAD:main", check=False).returncode == 0:
            print(f"publicado: {mensaje}")
            return
        git("fetch", "-q", "origin", "main")
        if git("rebase", "-q", "origin/main", check=False).returncode != 0:
            git("rebase", "--abort", check=False)
            git("reset", "-q", "--hard", "origin/main")
            sys.exit("Otra máquina cambió el mismo archivo al mismo tiempo y se descartó tu cambio. "
                     "Corré 'listar' y volvé a intentar.")
    sys.exit("No pude hacer push después de 4 intentos.")


# ---------- archivos de tarea ----------

def leer(p: Path) -> tuple[dict, str]:
    t = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", t, re.S)
    if not m:
        sys.exit(f"{p.name}: falta el encabezado YAML entre líneas ---")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def escribir(p: Path, meta: dict, cuerpo: str) -> None:
    enc = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=110).strip()
    p.write_text(f"---\n{enc}\n---\n{cuerpo}", encoding="utf-8", newline="\n")


def todas() -> list[tuple[Path, dict, str]]:
    return [(p, *leer(p)) for p in sorted(DIR.glob("T*.md"))]


def buscar(tid: str) -> tuple[Path, dict, str]:
    tid = tid.upper()
    for p, meta, cuerpo in todas():
        if str(meta.get("id", "")).upper() == tid:
            return p, meta, cuerpo
    sys.exit(f"No existe la tarea {tid}")


def agregar_nota(cuerpo: str, maquina: str, texto: str) -> str:
    if "## Notas" not in cuerpo:
        cuerpo = cuerpo.rstrip("\n") + "\n\n## Notas\n"
    return cuerpo.rstrip("\n") + f"\n- {ahora()} · {maquina}: {texto}\n"


def plan_de(maquina: str) -> str | None:
    if not MAQUINAS.exists():
        return None
    datos = yaml.safe_load(MAQUINAS.read_text(encoding="utf-8")) or {}
    return (datos.get("maquinas", {}).get(maquina) or {}).get("plan")


# ---------- comandos ----------

def cmd_listar(a) -> None:
    traer(a.sin_git)
    filas = todas()
    hechas = {str(m.get("id")) for _, m, _ in filas if m.get("estado") == "hecha"}
    print(f"{'id':5} {'estado':9} {'plan':4} {'máquina':8} {'estados':12} título")
    for _, m, _ in filas:
        if a.libres and m.get("estado") != "libre":
            continue
        if a.plan and m.get("plan_minimo") == "max" and a.plan == "pro":
            continue
        dep = [d for d in (m.get("depende_de") or []) if d not in hechas]
        espera = f"  (espera {', '.join(dep)})" if dep and m.get("estado") == "libre" else ""
        est = ",".join(m.get("estados") or []) or "-"
        print(f"{m.get('id',''):5} {m.get('estado',''):9} {m.get('plan_minimo',''):4} "
              f"{m.get('maquina') or '-':8} {est:12} {m.get('titulo','')}{espera}")


def cmd_ver(a) -> None:
    traer(a.sin_git)
    p, _, _ = buscar(a.id)
    print(p.read_text(encoding="utf-8"))


def cmd_tomar(a) -> None:
    traer(a.sin_git)
    p, m, cuerpo = buscar(a.id)
    if m.get("estado") != "libre":
        sys.exit(f"{m['id']} no está libre: {m.get('estado')} ({m.get('maquina') or '-'})")
    hechas = {str(x.get("id")) for _, x, _ in todas() if x.get("estado") == "hecha"}
    falta = [d for d in (m.get("depende_de") or []) if d not in hechas]
    if falta:
        sys.exit(f"{m['id']} depende de tareas sin terminar: {falta}")
    plan = plan_de(a.maquina)
    if m.get("plan_minimo") == "max" and plan == "pro":
        sys.exit(f"{m['id']} pide plan Max y {a.maquina} es Pro")
    m.update(estado="tomada", maquina=a.maquina, actualizada=ahora())
    escribir(p, m, agregar_nota(cuerpo, a.maquina, "tomada"))
    publicar([p], f"tarea {m['id']}: tomada por {a.maquina}", a.sin_git)


def cambiar(a, estado: str | None, texto: str, exigir_propia: bool = True) -> None:
    """estado=None deja el estado como está (solo agrega una nota)."""
    traer(a.sin_git)
    p, m, cuerpo = buscar(a.id)
    if exigir_propia and m.get("maquina") not in (None, a.maquina):
        sys.exit(f"{m['id']} es de {m.get('maquina')}, no de {a.maquina}")
    if estado:
        m["estado"] = estado
    m["actualizada"] = ahora()
    if estado == "libre":
        m["maquina"] = None
    escribir(p, m, agregar_nota(cuerpo, a.maquina, texto))
    publicar([p], f"tarea {m['id']}: {estado or 'nota'} ({a.maquina})", a.sin_git)


def cmd_nueva(a) -> None:
    traer(a.sin_git)
    nums = [int(re.sub(r"\D", "", str(m.get("id", "0"))) or 0) for _, m, _ in todas()]
    tid = f"T{max(nums, default=0) + 1:03d}"
    slug = re.sub(r"[^a-z0-9]+", "-", a.titulo.lower()).strip("-")[:40]
    p = DIR / f"{tid}-{slug}.md"
    meta = {"id": tid, "titulo": a.titulo, "estado": "libre", "plan_minimo": a.plan, "maquina": None,
            "estados": [s.strip().upper() for s in a.estados.split(",") if s.strip()],
            "depende_de": [s.strip().upper() for s in a.depende.split(",") if s.strip()],
            "rama": None, "creada": ahora(), "actualizada": ahora()}
    cuerpo = "\n## Qué hacer\n\n(completar)\n\n## Terminada cuando\n\n(completar)\n\n## Notas\n"
    DIR.mkdir(parents=True, exist_ok=True)
    escribir(p, meta, cuerpo)
    publicar([p], f"tarea {tid}: nueva ({a.maquina})", a.sin_git)
    print(p.relative_to(BASE))


def cmd_bitacora(a) -> None:
    traer(a.sin_git)
    p = BASE / "coordinacion" / "bitacora" / f"{a.maquina}.md"
    NL = "\n"
    t = p.read_text(encoding="utf-8") if p.exists() else f"# Bitácora de {a.maquina}{NL}"
    hoy = f"## {dt.date.today().isoformat()}"
    if hoy not in t:
        t = t.rstrip(NL) + NL + NL + hoy + NL
    p.parent.mkdir(parents=True, exist_ok=True)
    linea = f"- {dt.datetime.now():%H:%M} {a.texto}"
    p.write_text(t.rstrip(NL) + NL + linea + NL, encoding="utf-8", newline=NL)
    publicar([p], f"bitácora de {a.maquina}", a.sin_git)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--maquina", default=os.environ.get("FIELDSHIFT_MAQUINA", ""))
    ap.add_argument("--sin-git", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("listar"); s.add_argument("--libres", action="store_true"); s.add_argument("--plan", choices=PLANES)
    sub.add_parser("ver").add_argument("id")
    sub.add_parser("tomar").add_argument("id")
    for c in ("nota", "soltar", "bloquear", "terminar"):
        s = sub.add_parser(c); s.add_argument("id"); s.add_argument("texto")
    sub.add_parser("bitacora").add_argument("texto")
    s = sub.add_parser("nueva"); s.add_argument("titulo"); s.add_argument("--plan", choices=PLANES, default="pro")
    s.add_argument("--estados", default=""); s.add_argument("--depende", default="")
    a = ap.parse_args()
    if a.cmd not in ("listar", "ver") and not a.maquina:
        sys.exit("Falta la máquina: definí FIELDSHIFT_MAQUINA o pasá --maquina")
    if a.cmd == "listar":
        cmd_listar(a)
    elif a.cmd == "ver":
        cmd_ver(a)
    elif a.cmd == "tomar":
        cmd_tomar(a)
    elif a.cmd == "nota":
        cambiar(a, None, a.texto, exigir_propia=False)
    elif a.cmd == "soltar":
        cambiar(a, "libre", f"soltada: {a.texto}")
    elif a.cmd == "bloquear":
        cambiar(a, "bloqueada", f"bloqueada: {a.texto}", exigir_propia=False)
    elif a.cmd == "terminar":
        cambiar(a, "hecha", f"terminada: {a.texto}")
    elif a.cmd == "nueva":
        cmd_nueva(a)
    elif a.cmd == "bitacora":
        cmd_bitacora(a)


if __name__ == "__main__":
    main()
