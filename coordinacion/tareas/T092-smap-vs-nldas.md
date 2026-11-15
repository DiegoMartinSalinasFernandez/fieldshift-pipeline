---
id: T092
titulo: 'Research: humedad del suelo de SMAP contra NLDAS-2 en OH, NE y MN (2015–2025)'
estado: hecha
plan_minimo: pro
maquina: pro-1
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15T06:44
actualizada: 2026-11-15 06:47
---

## Qué hacer

Con el release `datos-oh-ne-mn` (`agua_mensual.csv` y `nldas_mensual.csv`), compará por condado y mes
`sm_rootzone_m3m3` (SMAP) con `sm_0_100cm_m3m3` (NLDAS-2 Noah) y las anomalías (`sm_rootzone_anom_z` y
`sm_0_100cm_anom_z`): correlación por condado, sesgo medio y dónde difieren más (por ejemplo, condados con turba,
ver `docs/research/smap_costas.md`). Decí qué conviene usar como entrada para ML antes de 2015 y después, y si
son redundantes. Solo describir: no entrenar modelos. Script chico en `docs/research/smap_vs_nldas.py`.

Los zips de los releases son públicos: bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/<release>/<archivo>` (dueño y repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256`. Van a `data/` (fuera de git), nunca al repo.

Escribí `docs/research/smap_vs_nldas.md` (formato de la sección 8 del CLAUDE.md).

## Terminada cuando

El research y el script en un PR.

## Notas
- 2026-11-15 06:44 · pro-1: tomada
- 2026-11-15 06:47 · pro-1: terminada por el trabajador: PR #83, falta la revisión de max-1
