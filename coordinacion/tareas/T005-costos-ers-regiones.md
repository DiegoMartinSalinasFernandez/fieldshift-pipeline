---
id: T005
titulo: Costos de ERS por región para los estados nuevos
estado: libre
plan_minimo: pro
maquina: null
estados:
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-14 23:59
---

## Qué hacer

`src/economia/process.py` usa la región Heartland de ERS para todos los estados. Ohio, Nebraska, Minnesota y
Kansas caen en parte en otras Farm Resource Regions (por ejemplo Northern Crescent, Northern Great Plains o
Prairie Gateway: verificar). Investigar qué región conviene por estado (o por condado, si ERS publica la
tabla condado → región), escribir `docs/research/regiones_ers.md` y proponer el cambio en `economia`.

## Terminada cuando

Research con la región de cada estado (o condado) y la fuente oficial; cambio en `economia` en una rama con PR.

## Notas
