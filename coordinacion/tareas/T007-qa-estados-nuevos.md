---
id: T007
titulo: Control de calidad de los estados nuevos
estado: libre
plan_minimo: pro
maquina: null
estados:
- OH
- NE
- MN
- KS
depende_de:
- T003
- T013
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-14 23:59
---

## Qué hacer

Bajar los zips de T003 de los Releases y auditarlos contra la sección 4 del CLAUDE.md: claves, `fips` de
`condados.csv`, rangos físicos, faltantes, unidades, y comparar con IA, IL e IN (un condado de Kansas no
puede tener el triple de lluvia que uno de Iowa sin explicación). Escribir `docs/qa/<estados>.md` con APTO o
NO APTO por paquete y los problemas encontrados.

## Terminada cuando

Un informe de QA por grupo de estados, y una tarea nueva por cada problema que haya que arreglar.

## Notas
