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
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-14 23:59
sugerida_para: max-1
---

## Qué hacer

Juntar los CSV procesados de todos los releases (los archivos de cada paquete se apilan por filas: las
claves son por condado), correr `src/merge.py` sobre el conjunto y armar la entrega para ML con su
`LEEME.md`, como las entregas de ResearchAgent.

## Terminada cuando

Tablas unidas de los 7 estados validadas, y la entrega publicada para el equipo de ML.

## Notas
