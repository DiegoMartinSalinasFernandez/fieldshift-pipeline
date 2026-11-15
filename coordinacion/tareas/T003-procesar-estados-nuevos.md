---
id: T003
titulo: Procesar OH, NE y MN y publicar sus zips
estado: hecha
plan_minimo: max
maquina: max-1
estados:
- OH
- NE
- MN
depende_de:
- T001
- T002
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-15 05:46
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
- 2026-11-15 02:58 · max-1: CDL de OH/NE/MN incompleto (bug de T023, PR 17): en ResearchAgent-6estados hay 59 teselas en 2008 y 2021-2024 en lugar de 107, y 41 en 2025. Antes de procesar, volver a correr la descarga del CDL con el código de main (después de que terminen las otras descargas, para no escribir el manifest a la vez).
- 2026-11-15 03:03 · max-1: tomada
- 2026-11-15 05:46 · max-1: terminada: release datos-oh-ne-mn publicado: 8 paquetes APTO (verificar_entrega.py). Rama tarea/T003-procesar con los data cards de OH/NE/MN. Arreglos en main: PR 39 (token de MODIS) y PR 61 (NLDAS duplicado). Pendiente para ML: unir con los otros grupos (T008).
