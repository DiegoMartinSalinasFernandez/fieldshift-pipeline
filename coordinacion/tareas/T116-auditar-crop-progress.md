---
id: T116
titulo: Revisar los scripts de Crop Progress por el error de lectura que corrigió T113
estado: libre
plan_minimo: pro
maquina: null
estados:
- KY
- MI
- ND
- MO
- WI
- SD
depende_de: []
rama: null
creada: 2026-11-15T08:23
actualizada: 2026-11-15T08:23
---

## Qué hacer

En T113 (PR 105) apareció un error en `docs/research/fechas_nd_cp.py`: cuando el estado no figuraba en una tabla
de un reporte de Crop Progress, el script tomaba su fila de la tabla siguiente (así salían para KY un trigo de
invierno y para MI una "cebada" que no existen). Revisá si los scripts anteriores que leen esos reportes tienen
el mismo error: `nass_ky_crop_progress.py`, `nass_mi_nd_crop_progress.py`, `nass_mo_wi_sd_crop_progress.py`,
`ventanas_por_estado.py`, `propuesta_cultivos_cp.py` y `comparar_grupos.py` (en `docs/research/`).

Para cada uno: si lee reportes (no la API de Quick Stats), probalo con un estado que falte en alguna tabla. Si
tiene el error, corregilo sin cambiar lo que hace en los casos buenos, volvé a correrlo y corregí los números del
`.md` que cambien, diciendo en el `.md` qué cambió y por qué. Si no lo tiene, anotalo en las Notas.
Aprovechá para corregir en `fechas_nd.md` la fracción de julio de la floración de ND (0,75 → 0,82 con la
convención de días continuos que usa la ventana de la soja; lo señaló T113).

No toques `src/`: `src/cultivos` usa la API de Quick Stats, no los reportes.

## Terminada cuando

Los arreglos (o la constancia de que no hacían falta) en un PR.

## Notas
