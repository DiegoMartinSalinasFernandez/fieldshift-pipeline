---
id: T029
titulo: 'Research: carbono del suelo y erosión según la rotación'
estado: tomada
plan_minimo: pro
maquina: pro-2
estados:
- IA
- IL
- IN
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-15 03:00
actualizada: 2026-11-15 02:50
---

## Qué hacer

La herramienta compara rotaciones, y lo que el modelo no predice (suelo, nitrógeno, carbono, erosión,
agua) sale de reglas con fuente (skill de ML, sección 8). Este research arma una de esas reglas.

Buscá:

- factores C de RUSLE/RUSLE2 para maíz continuo, maíz–soja, maíz–soja–trigo y rotaciones con alfalfa, con y
  sin labranza cero (guías del NRCS o publicaciones);
- tasas de cambio del carbono orgánico del suelo (t C/ha/año) según la rotación y la labranza en ensayos de
  largo plazo del Corn Belt;
- cuánto aporta cada cultivo de rastrojo (relación con `config/cultivos.csv`, columnas de rastrojo y C:N).

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets grandes ni toques `src/` o `data/`.

Escribí `docs/research/carbono_erosion.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 02:50 · pro-2: tomada
