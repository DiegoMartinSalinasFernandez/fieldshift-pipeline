#!/usr/bin/env python
"""Muestra el puntaje actual y qué checks fallan. Es de solo lectura sobre el repo.

    python loop/puntaje.py                       # todo
    python loop/puntaje.py --tarea clima         # solo lo que falla en clima
    python loop/puntaje.py --tarea research      # todas las tareas de research
    python loop/puntaje.py --tarea clima --reproducir clima   # además corre process.py y compara

Corre loop/checks/score.py en un entorno aislado (uv, Python 3.11) con su propia caché
(loop/state/cache_agente). El orquestador usa su propia copia bloqueada del scorer.
"""
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent


def main():
    req = AQUI / "checks" / "requirements.txt"
    cmd = ["uv", "run", "--no-project", "--quiet", "--python", "3.11", "--with-requirements", str(req),
           "python", "-I", "-X", "utf8", str(AQUI / "checks" / "score.py"), "--repo", str(REPO), "--resumen"]
    cmd += sys.argv[1:]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    sys.exit(subprocess.call(cmd, env=env))


if __name__ == "__main__":
    main()
