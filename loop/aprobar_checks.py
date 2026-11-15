#!/usr/bin/env python
"""Revisión y aprobación de los checks del research agent. La corre el humano, no los agentes.

    python loop/aprobar_checks.py --resumen     # qué se va a medir, en palabras (no cambia nada)
    python loop/aprobar_checks.py --aprobar     # congela los checks en loop/spec/LOCK.json y hace commit

Antes de cualquiera de las dos, valida los YAML (paquetes, IDs del catálogo, marcadores de
program.md) y corre el scorer una vez sin red: si algo falla, no aprueba.
Mientras LOCK.json coincida con los archivos, loop/run.py acepta correr; si alguien cambia un
check, el scorer, el hook, los prompts o las reglas fijas de program.md, hay que volver a aprobar.
Si falta pyyaml, se relanza solo con uv (Python 3.11).
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
PLACEHOLDERS_REFLEXION = ["{resultados}", "{reportes}", "{puntaje}", "{habitos_salida}", "{como_trabajar_salida}"]


def cargar_run():
    """Importa loop/run.py (sin efectos al importar) para usar las mismas funciones de LOCK y git."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("ra_run", AQUI / "run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lista(x):
    if x is None or x == "":
        return []
    if isinstance(x, (list, tuple)):
        return [str(v).strip() for v in x if str(v).strip()]
    return [s.strip() for s in str(x).split(",") if s.strip()]


def leer_ids_catalogo():
    p = REPO / "loop" / "spec" / "catalogo.csv"
    with open(p, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    return {r["id"].strip(): r for r in filas if r.get("id")}


def validar(run, ent, res, cat):
    errores, avisos = [], []
    paquetes = ent.get("paquetes") or {}
    if not paquetes:
        errores.append("entregables.yaml no tiene paquetes.")

    def chequear_ids(donde, valor):
        for cid in lista(valor):
            if cid not in cat:
                errores.append(f"{donde}: el ID de catálogo '{cid}' no existe en loop/spec/catalogo.csv.")

    for pkg, p in paquetes.items():
        for k in ("escribe", "process", "salidas"):
            if not p.get(k):
                errores.append(f"paquete {pkg}: falta '{k}'.")
        for r in p.get("requiere") or []:
            if r not in paquetes:
                errores.append(f"paquete {pkg}: requiere '{r}', que no es un paquete.")
        for a in p.get("archivos") or []:
            if not a.get("ruta"):
                errores.append(f"paquete {pkg}: hay un archivo sin 'ruta'.")
                continue
            for c in a.get("columnas") or []:
                nombre = c.get("nombre") or c.get("patron")
                if not nombre:
                    errores.append(f"{a['ruta']}: hay una columna sin 'nombre' ni 'patron'.")
                    continue
                if c.get("patron"):
                    try:
                        re.compile(c["patron"])
                    except re.error as e:
                        errores.append(f"{a['ruta']}: el patrón '{c['patron']}' no es una regex válida ({e}).")
                chequear_ids(f"{a['ruta']}: columna {nombre}", c.get("catalogo"))
        ids_esp = set()
        for e in p.get("especiales") or []:
            if not e.get("id"):
                errores.append(f"paquete {pkg}: hay un check especial sin 'id'.")
                continue
            if e["id"] in ids_esp:
                errores.append(f"paquete {pkg}: el check especial '{e['id']}' está repetido.")
            ids_esp.add(e["id"])
            chequear_ids(f"paquete {pkg}: especial {e['id']}", e.get("catalogo"))
    if "base" in paquetes and "zona_config" not in {e.get("id") for e in paquetes["base"].get("especiales") or []}:
        avisos.append("base no tiene el especial 'zona_config': run.py va a considerar lista la base cuando sume algún punto.")

    temas = res.get("temas") or []
    vistos = set()
    for t in temas:
        for k in ("id", "archivo", "pregunta", "escribe"):
            if not t.get(k):
                errores.append(f"research.yaml: el tema {t.get('id', '?')} no tiene '{k}'.")
        if t.get("id") in vistos:
            errores.append(f"research.yaml: el tema '{t.get('id')}' está repetido.")
        vistos.add(t.get("id"))
    C = res.get("cultivos") or {}
    for at in C.get("atributos") or []:
        chequear_ids(f"research.yaml: atributo {at.get('nombre', '?')}", at.get("catalogo"))
    if C and C.get("archivo") and not any(C["archivo"] in (t.get("escribe") or []) for t in temas):
        avisos.append(f"research.yaml: ningún tema escribe {C['archivo']}.")

    tareas = list(paquetes) + [f"research:{t.get('id')}" for t in temas]
    nuevas = [t for t in tareas if t not in run.ORDEN]
    if nuevas:
        avisos.append("tareas que no están en el orden de run.py (van al final): " + ", ".join(nuevas))
    viejas = [t for t in run.ORDEN if t not in tareas]
    if viejas:
        avisos.append("tareas del orden de run.py que ya no existen en las specs (se ignoran): " + ", ".join(viejas))

    prog_p = REPO / "loop" / "program.md"
    if not prog_p.exists():
        errores.append("falta loop/program.md.")
    else:
        prog = prog_p.read_text(encoding="utf-8")
        for nombre in ("REGLAS-FIJAS", "COMO-TRABAJAR"):
            if prog.count(f"<!-- {nombre}:INICIO -->") != 1 or prog.count(f"<!-- {nombre}:FIN -->") != 1:
                errores.append(f"loop/program.md: tiene que tener una sola sección <!-- {nombre}:INICIO/FIN -->.")
    refl = REPO / "loop" / "prompts" / "reflexion.md"
    if not refl.exists():
        errores.append("falta loop/prompts/reflexion.md.")
    else:
        txt = refl.read_text(encoding="utf-8")
        faltan = [ph for ph in PLACEHOLDERS_REFLEXION if ph not in txt]
        if faltan:
            avisos.append("loop/prompts/reflexion.md no usa: " + ", ".join(faltan))
    for rel in ("loop/hooks/guard.py", "loop/checks/score.py", "loop/checks/requirements.txt"):
        if not (REPO / rel).exists():
            errores.append(f"falta {rel}.")
    return errores, avisos


def correr_scorer(run):
    uv = shutil.which("uv")
    if not uv:
        sys.exit("Falta uv (https://docs.astral.sh/uv/).")
    checks = REPO / "loop" / "checks"
    with tempfile.TemporaryDirectory(prefix="ra_aprobar_") as tmp:
        salida = Path(tmp) / "score.json"
        cmd = [uv, "run", "--no-project", "--quiet", "--python", "3.11", "--with-requirements",
               str(checks / "requirements.txt"), "python", "-I", "-X", "utf8", str(checks / "score.py"),
               "--repo", str(REPO), "--spec", str(REPO / "loop" / "spec"), "--cache", str(Path(tmp) / "cache"),
               "--json", str(salida), "--sin-red"]
        try:
            r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               env=run.entorno_limpio(), stdin=subprocess.DEVNULL, timeout=1800)
        except subprocess.TimeoutExpired:
            sys.exit("El scorer tardó más de 30 min. No se aprueba.")
        if r.returncode != 0 or not salida.exists():
            sys.exit("El scorer falló. No se aprueba.\n" + ((r.stdout or "") + (r.stderr or ""))[-3000:])
        return json.loads(salida.read_text(encoding="utf-8"))


def en_claude(nombre: str, texto: str) -> bool:
    return re.search(r"(?<![A-Za-z0-9_])" + re.escape(nombre) + r"(?![A-Za-z0-9_])", texto) is not None


def resumen(ent, res, P, cat):
    claude = (REPO / "CLAUDE.md").read_text(encoding="utf-8") if (REPO / "CLAUDE.md").exists() else ""
    L = []
    L.append(f"Puntaje máximo: {P['max']:.1f} puntos. Puntaje actual del repo: {P['total']:.1f}.")
    L.append("Cada tarea reparte sus puntos entre datos (archivos, columnas, rangos, checks especiales, "
             "reproducibilidad, manifest) y documentación (data card). Una ronda se guarda solo si el total sube "
             "y nada de lo que ya sumaba baja.\n")
    L.append("Puntos por tarea:")
    for t, v in P["tareas"].items():
        L.append(f"  {t:32} {v['pts']:6.1f} / {v['max']:6.1f}")
    propuestos = set()
    for pkg, p in (ent.get("paquetes") or {}).items():
        L.append("")
        L.append(f"== {pkg}: {p.get('titulo', '')} ({p.get('seccion_claude', '')})")
        if p.get("requiere"):
            L.append(f"   requiere: {', '.join(p['requiere'])}"
                     + (f" y al menos {p['requiere_paquetes_con_datos']} paquetes con datos" if p.get("requiere_paquetes_con_datos") else ""))
        L.append(f"   puede escribir: {', '.join(p.get('escribe') or [])}")
        for a in p.get("archivos") or []:
            claves = ", ".join(a.get("claves") or [])
            L.append(f"   {a['ruta']}  (claves: {claves or '-'}; {a.get('temporal', '')})")
            for c in a.get("columnas") or []:
                if c.get("patron"):
                    txt = f"patrón {c['patron']}"
                    marca = "  [patrón]"
                else:
                    txt = c["nombre"]
                    marca = ""
                    if not en_claude(c["nombre"], claude):
                        marca = "  [nombre propuesto]"
                        propuestos.add(c["nombre"])
                extra = []
                if c.get("catalogo"):
                    ids = lista(c["catalogo"])
                    extra.append("cat. " + ", ".join(f"{i} {cat.get(i, {}).get('variable', '')}".strip() for i in ids))
                if c.get("rango"):
                    extra.append(f"rango {c['rango']}")
                if c.get("tipo"):
                    extra.append(str(c["tipo"]))
                if c.get("login"):
                    extra.append("requiere login")
                L.append(f"      - {txt}{marca}" + (f"  ({'; '.join(extra)})" if extra else ""))
            if a.get("nota"):
                L.append(f"      nota: {' '.join(str(a['nota']).split())}")
        for e in p.get("especiales") or []:
            L.append(f"   check especial {e['id']} (peso {e.get('peso', 1)}): {' '.join(str(e.get('descripcion', '')).split())}")
    L.append("")
    L.append("== Research (docs/research/)")
    for t in res.get("temas") or []:
        L.append(f"   {t.get('orden', '')}. {t['id']} → {t.get('archivo')}")
        L.append(f"      {' '.join(str(t.get('pregunta', '')).split())[:400]}")
    C = res.get("cultivos") or {}
    if C:
        L.append(f"   Tabla {C.get('archivo')}: {len(C.get('filas') or [])} cultivos × {len(C.get('atributos') or [])} "
                 f"atributos; cada celda necesita una cita verificable en {C.get('evidencia')}.")
    L.append("")
    L.append(f"Columnas con [nombre propuesto] (no aparecen literalmente en CLAUDE.md): {len(propuestos)}. "
             "Si alguna no te gusta, cambiala en loop/spec/entregables.yaml antes de aprobar.")
    if P.get("avisos"):
        L.append("")
        L.append("Avisos del scorer:")
        for a in P["avisos"][:30]:
            L.append(f"   - {a}")
    return "\n".join(L)


def main():
    if os.environ.get("RA_RUN_ID"):
        sys.exit("La aprobación de checks la corre solo el humano, no un agente de una ronda.")
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resumen", action="store_true", help="mostrar qué se mide (no cambia nada)")
    ap.add_argument("--aprobar", action="store_true", help="congelar los checks en LOCK.json y hacer commit")
    a = ap.parse_args()
    run = cargar_run()
    run.asegurar_yaml(Path(__file__).resolve())
    import yaml

    spec_dir = REPO / "loop" / "spec"
    ent = yaml.safe_load((spec_dir / "entregables.yaml").read_text(encoding="utf-8")) or {}
    res = yaml.safe_load((spec_dir / "research.yaml").read_text(encoding="utf-8")) or {}
    cat = leer_ids_catalogo()
    errores, avisos = validar(run, ent, res, cat)
    for x in avisos:
        print("AVISO:", x)
    if errores:
        print("\nLas specs tienen errores (no se aprueba):")
        for x in errores:
            print("  -", x)
        sys.exit(1)
    print("Specs válidas. Corriendo el scorer una vez (sin red)...")
    P = correr_scorer(run)
    print(f"Scorer OK: {len(P.get('checks', {}))} checks, puntaje {P['total']:.1f} / {P['max']:.1f}.\n")

    if a.resumen or not a.aprobar:
        print(resumen(ent, res, P, cat))
    if not a.aprobar:
        dif = run.verificar_lock(REPO)
        if dif is None:
            print("\nTodavía no hay checks aprobados. Para aprobar: python loop/aprobar_checks.py --aprobar")
        elif dif:
            print("\nCambió desde la última aprobación: " + ", ".join(dif[:10]) +
                  "\nPara aprobar de nuevo: python loop/aprobar_checks.py --aprobar")
        else:
            print("\nLos checks aprobados coinciden con los archivos (LOCK.json al día).")
        return

    lock = run.escribir_lock(REPO)
    print(f"LOCK.json escrito: {len(lock['archivos'])} archivos y las reglas fijas de program.md.")
    if not (REPO / ".git").exists():
        r = subprocess.run(["git", "init", "-q", "-b", "main"], cwd=REPO, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("No pude crear el repo git: " + (r.stderr or r.stdout).strip())
        print("Repo git creado (rama main).")
    rama = run.git("symbolic-ref", "--short", "-q", "HEAD", check=False).strip() or "(sin rama)"
    msg = (f"checks aprobados\n\nPuntaje máximo {P['max']:.1f} en {len(P['tareas'])} tareas "
           f"({len(P.get('checks', {}))} checks). Puntaje del repo al aprobar: {P['total']:.1f}.")
    max_mb = float((ent.get("contrato") or {}).get("max_mb_archivo_git", 50))
    grandes = [c for c in run.cambios_git() if (REPO / c).is_file() and (REPO / c).stat().st_size > max_mb * 1e6]
    if grandes:
        print(f"Quedan fuera del commit por pesar más de {max_mb:.0f} MB: " + ", ".join(grandes))
    h = run.git_commit(msg, excluir=grandes)
    if h:
        print(f"Commit {h} en la rama {rama}: checks aprobados.")
    else:
        print(f"No había nada nuevo para commitear (rama {rama}); LOCK.json ya estaba al día.")
    print("Para lanzar la corrida: python loop/run.py --hours 8")


if __name__ == "__main__":
    main()
