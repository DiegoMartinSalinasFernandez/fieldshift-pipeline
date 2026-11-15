---
id: T003
titulo: Procesar OH, NE y MN y publicar sus zips
estado: libre
plan_minimo: max
maquina: null
estados:
- OH
- NE
- MN
depende_de:
- T001
- T002
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-15 01:25
auto: false
---

## Qué hacer

En la máquina que tiene los crudos: correr los `process.py` de cada paquete por estado o grupo de estados,
validar con `validar_csv()` y publicar con `scripts/entregar.py` (un zip por grupo de estados en los Releases).
Anotar en la tarea los paquetes que fallan y por qué. No cambiar el esquema de los CSV.

## Terminada cuando

Un release `datos-<estados>` por grupo, con todos los paquetes que procesan, y los data cards actualizados
con la cobertura real de cada estado.

## Notas
- 2026-11-15 01:15 · max-1: no la toma el trabajador automático: necesita los crudos que están en max-1
- 2026-11-15 01:25 · max-1: Kansas pasa a T013 (max-2, de punta a punta); esta queda para OH, NE y MN en max-1
