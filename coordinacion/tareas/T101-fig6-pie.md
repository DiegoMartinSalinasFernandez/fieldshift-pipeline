---
id: T101
titulo: 'Pie de fig6: IMERG viene por la API de POWER'
estado: libre
plan_minimo: pro
maquina: null
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15T07:02
actualizada: 2026-11-15 07:04
---

## Qué hacer

El pie de `docs/demo/fig/fig6_lluvia_oh_ne_mn.png` (PR 89) dice "NASA GPM IMERG Final V07 daily (county mean)".
Según `docs/datasets/clima.md`, `prec_imerg_mm` es IMERG servido por la API de NASA POWER (`IMERG_PRECTOT`,
0,1°), que sale de IMERG Final V07. Corregí el pie en `docs/demo/figuras.py` ("GPM IMERG Final V07, served by
the NASA POWER API (IMERG_PRECTOT)"), regenerá el PNG con los datos del release y revisá que la lámina 6 y
`docs/demo/fig/README.md` digan lo mismo.

## Terminada cuando

El PNG y el texto en un PR.

## Notas
- 2026-11-15 07:03 · pro-1: tomada
- 2026-11-15 07:04 · pro-1: corte por el límite de uso de Claude; 2 commits guardados en tarea/T101-auto. El trabajador sigue cuando se renueve.
- 2026-11-15 07:04 · pro-1: soltada: pro-1 sin cuota de Claude hasta 15/11 09:20
