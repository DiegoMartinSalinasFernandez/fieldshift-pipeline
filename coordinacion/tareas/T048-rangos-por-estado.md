---
id: T048
titulo: 'Propuesta: rangos físicos de los checks para los estados nuevos'
estado: tomada
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
creada: 2026-11-15 04:05
actualizada: 2026-11-15 04:04
---

## Qué hacer

Los rangos de `validar_csv()` y de `loop/spec/entregables.yaml` se pensaron para IA, IL e IN. Con NASS Quick Stats
(o los documentos de `docs/research/`), mirá para OH, NE, MN y KS, 2000–2025:

- rendimiento mínimo y máximo de condado de maíz, soja, trigo de invierno y avena (secano y riego si está);
- lluvia anual y de temporada, temperaturas extremas y GDD esperables (POWER o NOAA, en un research);
- si algún rango del spec dejaría afuera datos reales (por ejemplo maíz de secano de Kansas en 2012 debajo de
  20 bu/ac).

Escribí `docs/research/rangos_estados_nuevos.md` con una tabla rango actual → rango propuesto por variable.
**No cambies el spec ni `src/common/`**: es una propuesta para el humano.

Formato de research de la sección 8 del CLAUDE.md. Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes datasets grandes ni toques `data/`.

## Terminada cuando

La propuesta en un PR.

## Notas
- 2026-11-15 04:04 · pro-1: tomada
