---
id: T005
titulo: Costos de ERS por región para los estados nuevos
estado: hecha
plan_minimo: pro
maquina: pro-2
estados:
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-15 00:51
---

## Qué hacer

`src/economia/process.py` usa la región Heartland de ERS para todos los estados. Ohio, Nebraska, Minnesota y
Kansas caen en parte en otras Farm Resource Regions (por ejemplo Northern Crescent, Northern Great Plains o
Prairie Gateway: verificar). Investigar qué región conviene por estado (o por condado, si ERS publica la
tabla condado → región), escribir `docs/research/regiones_ers.md` y proponer el cambio en `economia`.

## Terminada cuando

Research con la región de cada estado (o condado) y la fuente oficial; cambio en `economia` en una rama con PR.

## Notas
- 2026-11-15 00:37 · pro-2: tomada
- 2026-11-15 00:39 · pro-2: reglink.xls de ERS (condado→región): IA/IL/IN 100% Heartland; KS 100% Prairie Gateway; OH 48 HL/22 NC/18 EU; NE 37 PG/29 HL/27 NGP; MN 41 HL/35 NC/11 NGP condados. Propuesta: ponderar costos ERS por área sembrada de cada condado (NASS).
- 2026-11-15 00:51 · pro-2: terminada: PR #2 (tarea/T005-regiones-ers). Research en docs/research/regiones_ers.md. Sin release de datos: el cambio es de código; max-1 regenera economia al unir.
