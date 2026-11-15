---
id: T103
titulo: 'Propuesta: sumar cultivos al esquema (trigo de primavera, durum, girasol, canola, cebada, maíz para silo)'
estado: tomada
plan_minimo: pro
maquina: pro-4
estados: []
depende_de: []
rama: null
creada: 2026-11-15T07:25
actualizada: 2026-11-15 07:34
---

## Qué hacer

`para_decidir.md` #29 y `docs/research/cuarta_tanda_decision.md` piden cultivos que el esquema de hoy no tiene:
maíz para silo (WI), trigo de primavera y girasol (SD, ND), durum, canola, cebada y frijol seco (ND). Escribí
`docs/research/propuesta_cultivos.md` con, por cultivo: `commodity_desc` y `short_desc` exactos de NASS
(rendimiento, superficie sembrada y cosechada, producción) y su unidad, factor de conversión a kg/ha con su
fuente, códigos del CDL, si Crop Progress lo publica y en qué estados, y en qué estados del Corn Belt (los 10 de
`config.yaml` más ND) pesa. Proponé los cambios exactos a `config/config.yaml`, `config/cultivos.csv`,
`data/reference/clases_cdl.csv` y `src/common` (conversiones), **sin aplicarlos**: es un cambio de esquema que
decide el humano. Formato de research de la sección 8 del CLAUDE.md.

## Terminada cuando

La propuesta en un PR.

## Notas
- 2026-11-15 07:34 · pro-4: tomada
