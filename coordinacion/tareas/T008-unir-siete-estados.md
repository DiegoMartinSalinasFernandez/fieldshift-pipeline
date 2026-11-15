---
id: T008
titulo: Unir los siete estados y armar la entrega para ML
estado: libre
plan_minimo: max
maquina: null
estados:
- IA
- IL
- IN
- OH
- NE
- MN
- KS
depende_de:
- T003
- T007
- T013
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-15 02:23
sugerida_para: max-1
auto: false
---

## Qué hacer

Juntar los CSV procesados de todos los releases (los archivos de cada paquete se apilan por filas: las
claves son por condado), correr `src/merge.py` sobre el conjunto y armar la entrega para ML con su
`LEEME.md`, como las entregas de ResearchAgent.

## Terminada cuando

Tablas unidas de los 7 estados validadas, y la entrega publicada para el equipo de ML.

## Notas
- 2026-11-15 01:15 · max-1: no la toma el trabajador automático: la hace max-1, que coordina
- 2026-11-15 02:23 · max-1: De T010 (PR 5): twi_decil_sup_pct usa el p90 de TWI de los condados que procesa cada máquina, así que no es comparable entre estados. Antes de unir: decidir con el humano (a) umbral fijo de la primera tanda en config, (b) recalcular con histogramas de todas las máquinas, o (c) percentil por condado. También revisar en T003 el aviso de áreas de SSURGO sin condado y las teselas MODIS h09v04/h09v05 de NE y KS.
