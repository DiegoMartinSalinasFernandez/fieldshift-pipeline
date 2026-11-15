---
id: T086
titulo: 'Data card de agua: área que saca el filtro de 0,6 m³/m³ por condado'
estado: hecha
plan_minimo: pro
maquina: pro-1
estados:
- MN
- OH
depende_de: []
rama: null
creada: 2026-11-15T06:27
actualizada: 2026-11-15 06:37
---

## Qué hacer

De `docs/research/smap_costas.md` (T082), opción (a): en `docs/datasets/agua.md`, explicar que el filtro de
`process.py` (`0 ≤ v ≤ 0,60`) descarta siempre las mismas celdas de SMAP (turberas y suelos orgánicos), que en
46 de 87 condados de MN saca alguna celda (Koochiching 65 % del área, Le Sueur 49 %, Aitkin 46 %), y que por eso
`sm_rootzone_m3m3` sale más bajo y `dias_sm_saturado` cuenta de menos en esos condados. Incluí la tabla de
condados de la sección 3 de ese research. La opción (b), una columna nueva, queda en `para_decidir.md` #31.

## Terminada cuando

El cambio en los data cards en un PR. No cambies código ni esquema.

## Notas
- 2026-11-15 06:36 · pro-1: tomada
- 2026-11-15 06:37 · pro-1: terminada por el trabajador: PR #78, falta la revisión de max-1
