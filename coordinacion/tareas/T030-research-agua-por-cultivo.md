---
id: T030
titulo: 'Research: consumo de agua por cultivo y rotación en el Corn Belt'
estado: hecha
plan_minimo: pro
maquina: pro-1
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
actualizada: 2026-11-15 02:55
---

## Qué hacer

La herramienta compara rotaciones, y lo que el modelo no predice (suelo, nitrógeno, carbono, erosión,
agua) sale de reglas con fuente (skill de ML, sección 8). Este research arma una de esas reglas.

Buscá mediciones (lisímetros, eddy covariance, balances) de la evapotranspiración de la temporada y su
variación entre años para maíz, soja, trigo de invierno, avena, alfalfa y heno en los 7 estados, y cómo cambia
el agua del suelo que deja cada cultivo para el siguiente (por ejemplo alfalfa antes del maíz). Compará con
los Kc de FAO-56 que ya están en `config/cultivos.csv`.

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets grandes ni toques `src/` o `data/`.

Escribí `docs/research/agua_por_cultivo.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 02:51 · pro-1: tomada
- 2026-11-15 02:55 · pro-1: terminada por el trabajador: PR #22, falta la revisión de max-1
