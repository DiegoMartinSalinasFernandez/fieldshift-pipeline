---
id: T062
titulo: Bajar y procesar MO, WI y SD (tercera tanda) y publicar sus zips
estado: hecha
plan_minimo: max
maquina: max-1
estados:
- MO
- WI
- SD
depende_de: []
rama: null
creada: 2026-11-15 04:42
actualizada: 2026-11-15 10:47
auto: false
---

## Qué hacer

Tercera tanda de estados, aprobada por el humano el 2026-11-15. En max-1 (carpeta propia, rama
`tarea/T062-mo-wi-sd`): base, todos los `download.py` con `FIELDSHIFT_ESTADOS=MO,WI,SD` (NASS nacional y
GRACE-DA-DM copiados de OH/NE/MN con sus filas del manifest), CDL, todos los `process.py`, data cards,
`scripts/verificar_entrega.py` y publicar con `scripts/entregar.py` (release `datos-mo-wi-sd`).

## Terminada cuando

El release `datos-mo-wi-sd` con todos los paquetes APTO, y los problemas anotados acá.

## Notas
- 2026-11-15 10:47 · max-1: terminada: Publicado el release datos-mo-wi-sd (253 condados): 8 paquetes + base, con notas y problemas conocidos. verificar_entrega: 8 APTO; cultivos NO APTO solo por rango: 12 rendimientos 0 de NASS sin cosecha para grano en el oeste de SD (tarea T148) y 6 rendimientos reales bajos de sequía (para_decidir #24 / PR 143). Anotado en docs/datasets/cultivos.md del zip.
