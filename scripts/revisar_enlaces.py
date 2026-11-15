"""Revisa los enlaces de las páginas que ven los jueces: `README.md` y todo `docs/demo/*.md` (tarea T109).

Para cada `.md`:
- enlaces e imágenes relativos (`[x](ruta)`, `![x](ruta)`, `<img src="ruta">`): la ruta, resuelta desde la
  carpeta del `.md`, tiene que existir en el repo. Error si no existe.
- rutas de GitHub relativas que salen del repo (`../../releases`, `../../issues`, ...), como las que usa el
  README: se arman con el remoto `origin` y se tratan como URL de GitHub.
- URL de release (`/releases/download/...` o `/releases/tag/...`, y la página `/releases`): tienen que
  responder 200 con `curl -I -L` (solo encabezados, no baja el archivo). Error si no.
- el resto de las URL externas (NASA, USDA, DOI): HEAD con timeout corto. Si fallan, solo aviso.

Se ignoran los enlaces dentro de bloques de código (```) y de código inline (`...`). Las anclas (`#...`) se
sacan antes de buscar el archivo.

Uso:
  .venv/bin/python -X utf8 scripts/revisar_enlaces.py            # todo, con red
  .venv/bin/python -X utf8 scripts/revisar_enlaces.py --sin-red  # solo los enlaces relativos e imágenes
  .venv/bin/python -X utf8 scripts/revisar_enlaces.py README.md docs/demo/slides.md

Sale con código 1 si hay errores (enlaces relativos rotos o releases que no responden 200); los avisos de
URL externas no cambian el código de salida.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]

# [texto](destino) e ![alt](destino); el destino puede llevar un título: (ruta "título")
RE_MD = re.compile(r"(!?)\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
RE_IMG_HTML = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)
RE_AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")
RE_URL_SUELTA = re.compile(r"(?<![(<\"'])\bhttps?://[^\s)<>`\"'\]]+")
RE_CODIGO_INLINE = re.compile(r"(`+)(?:(?!\1).)+?\1")
RUTAS_GITHUB = ("releases", "issues", "pulls", "wiki", "actions", "tree", "blob")


@dataclass
class Enlace:
    archivo: str  # relativo al repo
    linea: int
    destino: str
    imagen: bool


@dataclass
class Resultado:
    enlace: Enlace
    tipo: str  # relativo | release | externa
    ok: bool
    detalle: str


def extraer_enlaces(texto: str, archivo: str) -> list[Enlace]:
    """Enlaces de un markdown, sin los de bloques de código ni código inline."""
    enlaces: list[Enlace] = []
    en_bloque = False
    for n, linea in enumerate(texto.splitlines(), start=1):
        if linea.lstrip().startswith(("```", "~~~")):
            en_bloque = not en_bloque
            continue
        if en_bloque:
            continue
        # el código inline se tapa con espacios (el texto de `[`x`](y)` queda vacío, pero el enlace se sigue viendo)
        limpia = RE_CODIGO_INLINE.sub(lambda m: " " * len(m.group(0)), linea)
        usados: list[tuple[int, int]] = []
        for m in RE_MD.finditer(limpia):
            enlaces.append(Enlace(archivo, n, m.group(2), m.group(1) == "!"))
            usados.append(m.span())
        for m in RE_IMG_HTML.finditer(limpia):
            enlaces.append(Enlace(archivo, n, m.group(1), True))
            usados.append(m.span())
        for m in RE_AUTOLINK.finditer(limpia):
            enlaces.append(Enlace(archivo, n, m.group(1), False))
            usados.append(m.span())
        for m in RE_URL_SUELTA.finditer(limpia):
            if any(a <= m.start() < b for a, b in usados):
                continue
            enlaces.append(Enlace(archivo, n, m.group(0).rstrip(".,;:"), False))
    return enlaces


def url_repo_github(repo: Path = REPO) -> str | None:
    """`https://github.com/<dueño>/<repo>` desde el remoto `origin`, o None si no hay."""
    try:
        url = subprocess.run(["git", "-C", str(repo), "remote", "get-url", "origin"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)
    return f"https://github.com/{m.group(1)}/{m.group(2)}" if m else None


def clasificar(enlace: Enlace, repo: Path, base_github: str | None) -> tuple[str, str]:
    """Devuelve (tipo, destino): tipo es relativo, release, externa, ancla u otro; destino es ruta o URL."""
    d = enlace.destino
    if d.startswith("#"):
        return "ancla", d
    if re.match(r"^(mailto|tel):", d):
        return "otro", d
    if re.match(r"^https?://", d):
        return ("release" if es_release(d) else "externa"), d
    ruta = unquote(d.split("#", 1)[0].split("?", 1)[0])
    origen = (repo / enlace.archivo).parent
    destino = (origen / ruta).resolve()
    try:
        destino.relative_to(repo.resolve())
    except ValueError:
        # sale del repo: en GitHub `../../releases` desde la raíz es la página de releases del repo
        rel_raiz = Path(*[p for p in Path(enlace.archivo).parent.parts])
        partes = Path(ruta).parts
        subidas = sum(1 for p in partes if p == "..")
        resto = [p for p in partes if p not in ("..", ".")]
        profundidad = len(rel_raiz.parts)
        if resto and resto[0] in RUTAS_GITHUB and subidas == profundidad + 2:
            base = base_github or "https://github.com/<sin-remoto-origin>"
            return "release" if resto[0] == "releases" else "externa", base + "/" + "/".join(resto)
        return "relativo", str(destino)
    return "relativo", str(destino)


def es_release(url: str) -> bool:
    return bool(re.search(r"github\.com/[^/]+/[^/]+/releases(?:/(?:download|tag)/.+)?/?$", url))


def revisar_relativo(destino: str) -> tuple[bool, str]:
    p = Path(destino)
    if p.exists():
        return True, "existe"
    return False, "no existe en el repo"


def revisar_url(url: str, timeout: int) -> tuple[bool, str]:
    """HEAD con `curl -I -L`: ok si el código final es 200 (no baja el cuerpo)."""
    cmd = ["curl", "-sS", "-I", "-L", "-o", os.devnull, "-w", "%{http_code}",
           "--max-time", str(timeout), "-A", "fieldshift-revisar-enlaces", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, f"curl falló: {e}"
    codigo = r.stdout.strip() or "000"
    if codigo == "200":
        return True, "200"
    return False, f"HTTP {codigo}" + (f" ({r.stderr.strip()})" if r.stderr.strip() else "")


def archivos_por_defecto(repo: Path = REPO) -> list[Path]:
    return [repo / "README.md", *sorted((repo / "docs" / "demo").glob("**/*.md"))]


def revisar(archivos: list[Path], repo: Path = REPO, con_red: bool = True, timeout_externa: int = 20,
            timeout_release: int = 30, base_github: str | None = None) -> list[Resultado]:
    if base_github is None:
        base_github = url_repo_github(repo)
    resultados: list[Resultado] = []
    cache: dict[str, tuple[bool, str]] = {}
    for f in archivos:
        rel = f.resolve().relative_to(repo.resolve()).as_posix()  # mismo informe en Windows y Linux
        for e in extraer_enlaces(f.read_text(encoding="utf-8"), rel):
            tipo, destino = clasificar(e, repo, base_github)
            if tipo in ("ancla", "otro"):
                continue
            if tipo == "relativo":
                ok, det = revisar_relativo(destino)
                if not ok:
                    det += f": {Path(destino).relative_to(repo.resolve()).as_posix() if destino.startswith(str(repo.resolve())) else destino}"
                resultados.append(Resultado(e, tipo, ok, det))
                continue
            if not con_red:
                continue
            if destino not in cache:
                cache[destino] = revisar_url(destino, timeout_release if tipo == "release" else timeout_externa)
            ok, det = cache[destino]
            if destino != e.destino:
                det += f" ({destino})"
            resultados.append(Resultado(e, tipo, ok, det))
    return resultados


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("archivos", nargs="*", help="(por defecto README.md y docs/demo/**/*.md)")
    ap.add_argument("--sin-red", action="store_true", help="solo enlaces relativos e imágenes")
    ap.add_argument("--timeout", type=int, default=20, help="segundos por URL externa (por defecto 20: algunos DOI tardan más de 10)")
    args = ap.parse_args(argv)

    archivos = [Path(a).resolve() for a in args.archivos] or archivos_por_defecto()
    res = revisar(archivos, con_red=not args.sin_red, timeout_externa=args.timeout)

    errores = [r for r in res if not r.ok and r.tipo in ("relativo", "release")]
    avisos = [r for r in res if not r.ok and r.tipo == "externa"]
    for r in errores:
        print(f"ERROR {r.enlace.archivo}:{r.enlace.linea} [{r.tipo}] {r.enlace.destino} -> {r.detalle}")
    for r in avisos:
        print(f"AVISO {r.enlace.archivo}:{r.enlace.linea} [externa] {r.enlace.destino} -> {r.detalle}")
    por_tipo = {t: sum(1 for r in res if r.tipo == t) for t in ("relativo", "release", "externa")}
    print(f"\n{len(archivos)} archivos, {len(res)} enlaces revisados "
          f"({por_tipo['relativo']} relativos, {por_tipo['release']} de release, {por_tipo['externa']} externos"
          f"{'; sin red: solo relativos' if args.sin_red else ''}): "
          f"{len(errores)} errores, {len(avisos)} avisos.")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
