---
id: T002
titulo: Bajar los crudos de KS
estado: hecha
plan_minimo: max
maquina: max-1
estados:
- KS
depende_de: []
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-15 01:31
---

## Qué hacer

Lo mismo que T001 con `FIELDSHIFT_ESTADOS=KS`, en una copia aparte: MODIS, NLDAS y el paisaje recortan una
ventana que sale de los condados, y si se suma Kansas a la copia de T001 el sur de Kansas queda afuera.

## Terminada cuando

Igual que T001.

## Notas
- 2026-11-14 23:59 · max-1: tomada (en curso en esta máquina)
- 2026-11-15 01:31 · max-1: terminada: crudos de KS completos en max-1 (11 GB, copia local ResearchAgent-kansas): clima, IMERG (los 9 errores del primer pase se recuperaron en el segundo), suelo_terreno, cultivos (NASS y CDL), economia, agua, MODIS, NLDAS y paisaje. Falta validacion (PRISM, opcional): el script no estaba en el commit de la copia. Quedan de respaldo: T013 en max-2 los baja de nuevo de punta a punta.
