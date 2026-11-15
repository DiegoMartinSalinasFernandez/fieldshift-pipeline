---
id: T001
titulo: Bajar los crudos de OH, NE y MN
estado: tomada
plan_minimo: max
maquina: max-1
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-14 23:59
---

## Qué hacer

Correr los `download.py` de todos los paquetes con `FIELDSHIFT_ESTADOS=OH,NE,MN`. Los archivos nacionales
(base completa de NASS, GRACE-DA-DM de EE.UU.) se copian de una máquina que ya los tenga, con sus filas de
`manifest.csv`, en lugar de bajarlos otra vez.

## Terminada cuando

Todos los `download.py` terminaron sin errores pendientes, y lo que falló está anotado acá con el motivo.

## Notas
- 2026-11-14 23:59 · max-1: tomada (en curso en esta máquina)
