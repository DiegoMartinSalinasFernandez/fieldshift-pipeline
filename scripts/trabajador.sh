#!/usr/bin/env bash
# Lanzador del trabajador automático (scripts/trabajador.py) en segundo plano, para Linux y macOS.
# (En Windows: scripts/trabajador.ps1.)
#
#   bash scripts/trabajador.sh iniciar [horas] [tarea] [minutos_por_tarea]   # ej.: iniciar 7  o  iniciar 7 T013 400
#   bash scripts/trabajador.sh estado
#   bash scripts/trabajador.sh parar [ya]
#
# La primera vez crea una copia del repo solo para el trabajador, al lado de esta (<repo>-trabajador), con su
# propio .venv: nunca toca la carpeta donde trabajás vos. Antes tienen que estar definidas FIELDSHIFT_MAQUINA y
# FIELDSHIFT_ESTADOS (por ejemplo en ~/.bashrc) y Claude Code con la sesión iniciada.
# Modelo y esfuerzo: variables FIELDSHIFT_MODELO (opus) y FIELDSHIFT_EFFORT (medium).
set -euo pipefail

accion="${1:-estado}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
trab="${repo}-trabajador"
dir="$trab/.trabajador"
if [ -x "$trab/.venv/bin/python" ]; then py="$trab/.venv/bin/python"; else py="$trab/.venv/Scripts/python"; fi
pidf="$dir/pid.txt"

corriendo() { [ -f "$pidf" ] && kill -0 "$(cat "$pidf")" 2>/dev/null; }

case "$accion" in
  estado)
    if [ ! -d "$trab/.git" ]; then echo "El trabajador todavía no se instaló ($trab)."; exit 0; fi
    if corriendo; then echo "Corriendo (pid $(cat "$pidf"))."; else echo "No está corriendo."; fi
    "$py" -X utf8 "$trab/scripts/trabajador.py" estado
    ;;
  parar)
    if [ ! -d "$trab/.git" ]; then echo "El trabajador todavía no se instaló: no hay nada que parar."; exit 0; fi
    mkdir -p "$dir"; echo "parado a mano" > "$dir/STOP"
    if [ "${2:-}" = "ya" ] && corriendo; then
      kill -TERM -- "-$(cat "$pidf")" 2>/dev/null || kill -TERM "$(cat "$pidf")"
      echo "Trabajador cortado ya. La tarea en curso queda tomada: soltala con scripts/tareas.py soltar."
    else
      echo "Listo: el trabajador termina la tarea en curso y se detiene."
    fi
    ;;
  iniciar)
    horas="${2:-7}"; solo="${3:-}"; minutos="${4:-}"
    : "${FIELDSHIFT_MAQUINA:?Falta FIELDSHIFT_MAQUINA (ver MAQUINAS.md, sección 1)}"
    : "${FIELDSHIFT_ESTADOS:?Falta FIELDSHIFT_ESTADOS (ver MAQUINAS.md, sección 1)}"
    if corriendo; then echo "Ya hay un trabajador corriendo (pid $(cat "$pidf")). Usá 'parar' primero."; exit 1; fi
    if [ ! -d "$trab/.git" ]; then
      # una carpeta sin .git que solo tiene .trabajador/ (quedó de un 'parar' viejo) se puede reemplazar
      if [ -d "$trab" ]; then
        rm -rf "$trab/.trabajador"
        rmdir "$trab" 2>/dev/null || { echo "Ya existe $trab y no es la copia del trabajador: movela o borrala."; exit 1; }
      fi
      echo "-> Creo la copia del trabajador en $trab"
      git clone -q "$(git -C "$repo" remote get-url origin)" "$trab"
    fi
    git -C "$trab" config user.name "trabajador $FIELDSHIFT_MAQUINA"
    git -C "$trab" config user.email "trabajador-$FIELDSHIFT_MAQUINA@fieldshift.invalid"
    echo "-> Actualizo la copia desde GitHub"
    git -C "$trab" fetch -q origin
    git -C "$trab" switch -q main
    git -C "$trab" reset -q --hard origin/main
    if [ ! -d "$trab/.venv" ]; then echo "-> Creo el entorno de Python 3.11"; (cd "$trab" && uv venv -q --python 3.11); fi
    if [ -x "$trab/.venv/bin/python" ]; then py="$trab/.venv/bin/python"; else py="$trab/.venv/Scripts/python"; fi
    echo "-> Instalo dependencias"
    (cd "$trab" && uv pip install -q -r requirements.txt)
    if [ -f "$repo/.env" ] && [ ! -f "$trab/.env" ]; then cp "$repo/.env" "$trab/.env"; fi
    # el proceso en segundo plano tiene que encontrar claude aunque no herede el PATH de la terminal
    case "$(uname -s)" in
      Linux|Darwin)
        if [ -z "${FIELDSHIFT_CLAUDE:-}" ] && command -v claude >/dev/null; then export FIELDSHIFT_CLAUDE="$(command -v claude)"; fi ;;
    esac
    mkdir -p "$dir"; rm -f "$dir/STOP"
    args=(-X utf8 "$trab/scripts/trabajador.py" correr --horas "$horas"
          --modelo "${FIELDSHIFT_MODELO:-opus}" --effort "${FIELDSHIFT_EFFORT:-medium}")
    [ -n "$solo" ] && args+=(--solo "$solo")
    [ -n "$minutos" ] && args+=(--minutos-tarea "$minutos")
    # que la máquina no se suspenda mientras trabaja (si hay systemd)
    pre=()
    if command -v systemd-inhibit >/dev/null; then
      pre=(systemd-inhibit --what=sleep:idle --who=fieldshift --why="trabajador automático" --mode=block)
    fi
    lanzar=(nohup)
    command -v setsid >/dev/null && lanzar=(setsid nohup)
    cd "$trab"
    "${lanzar[@]}" ${pre[@]+"${pre[@]}"} "$py" "${args[@]}" > "$dir/salida.txt" 2> "$dir/errores.txt" < /dev/null &
    echo $! > "$pidf"
    echo "-> Trabajador iniciado en segundo plano (pid $(cat "$pidf")) por $horas h como $FIELDSHIFT_MAQUINA."
    echo "   Ver qué hace:  bash scripts/trabajador.sh estado"
    echo "   Pararlo:       bash scripts/trabajador.sh parar"
    echo "   Podés cerrar la terminal: el trabajador sigue."
    ;;
  *)
    echo "Uso: bash scripts/trabajador.sh iniciar|estado|parar"; exit 2 ;;
esac
