---
id: T006
titulo: Calendario de siembra y cosecha de los estados nuevos
estado: hecha
plan_minimo: pro
maquina: pro-1
estados:
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-15 00:37
---

## Qué hacer

Completar para OH, NE, MN y KS lo que `docs/research/cultivos_zona.md` y `config/cultivos.csv` tienen para
IA, IL e IN: fechas habituales de siembra y cosecha por cultivo (USDA Agricultural Handbook 628 y Crop
Progress). No inventar: lo que no se encuentre queda vacío y anotado.

## Terminada cuando

`config/cultivos.csv` y el research actualizados en una rama con PR (cambiar `config/` se consulta con el humano).

## Notas
- 2026-11-15 00:34 · pro-1: tomada
- 2026-11-15 00:37 · pro-1: terminada: PR #1: OH, NE, MN y KS del Handbook 628 en el research; cultivos.csv con el rango de 7 estados (13 celdas). Falta OK del humano por tocar config/.
