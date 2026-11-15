---
name: correr-loop
description: Lanzar, retomar, frenar y revisar una corrida del research agent de Field Shift (loop/run.py, método autoresearch). Usar cuando el humano pide correr el loop, ver cómo va o revisar lo que hizo.
disable-model-invocation: true
---

# Correr el research agent

El orquestador `loop/run.py` trabaja por rondas: elige una tarea, lanza un agente nuevo
(`claude -p`) con `loop/program.md` y una tarjeta, corre los checks bloqueados y guarda la
ronda con un commit solo si el puntaje sube sin que baje nada de lo que ya sumaba.

## Antes de la primera corrida

1. Credenciales (las crea el humano, nunca el agente):
   - Earthdata: `~/.netrc` con `machine urs.earthdata.nasa.gov login <usuario> password <clave>`.
   - NASS Quick Stats: `.env` en la raíz con `NASS_API_KEY=<clave>`.
   Sin ellas el loop igual corre: usa accesos públicos o marca esas partes como bloqueadas.
2. Revisar los checks en palabras simples: `python loop/aprobar_checks.py --resumen`.
3. Aprobarlos (los bloquea con hashes y hace commit): `python loop/aprobar_checks.py --aprobar`.

## Lanzar, frenar, retomar

- Lanzar en una terminal propia (no dentro de una sesión de Claude): `python loop/run.py --hours 8`.
  Prueba corta: `python loop/run.py --hours 0.5 --max-rounds 1 --only base`.
- Frenar sin cortar una ronda a la mitad: crear el archivo `loop/STOP`.
- Retomar: `python loop/run.py --resume <tag> --hours 4`.

## Revisar

- `loop/reports/<tag>.md`: puntaje inicial y final, rondas, decisiones pendientes, hábitos.
- `loop/runs/<tag>/results.tsv`: una fila por ronda (resultado, delta, motivo, costo).
- `loop/runs/<tag>/run.log`: el log en vivo.
- `git log --oneline autoresearch/<tag>`: cada ronda guardada es un commit.
- `loop/notes/decisiones.md`: lo que los agentes necesitan que decida el humano.
- Antes de usar los datos, leer los data cards (`docs/datasets/`), sobre todo "Supuestos".
