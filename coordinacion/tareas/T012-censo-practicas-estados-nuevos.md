---
id: T012
titulo: 'Research: prácticas del Censo Agropecuario en los estados nuevos'
estado: tomada
plan_minimo: pro
maquina: pro-1
estados:
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-15 01:15
actualizada: 2026-11-15 02:17
---

## Qué hacer

`practicas_censo.csv` (paquete `cultivos`) usa `short_desc` del Censo (2012, 2017, 2022) para cultivos de
cobertura, labranza cero, drenaje con caños y riego, investigados para IA, IL e IN
(`docs/research/censo_agropecuario.md`). Verificar que esos mismos `short_desc` existen por condado en OH,
NE, MN y KS, cuántos condados quedan con `(D)` y si en NE y KS conviene sumar la superficie regada por
cultivo. Actualizar `docs/research/censo_agropecuario.md` con una sección por estado nuevo.

## Terminada cuando

El research actualizado en un PR, con lo que T003 tiene que tener en cuenta.

## Notas
- 2026-11-15 02:17 · pro-1: tomada
