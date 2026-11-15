---
id: T045
titulo: Resumen en inglés de los datos para la entrega de Space Apps
estado: hecha
plan_minimo: pro
maquina: pro-1
estados: []
depende_de: []
rama: null
creada: 2026-11-15 04:05
actualizada: 2026-11-15 04:29
---

## Qué hacer

Los jueces de Space Apps leen en inglés. Escribí `docs/datasets/README_en.md`: qué datos hay, de qué productos de
la NASA salen (POWER, IMERG, MODIS, SMAP, GRACE-DA-DM, NASADEM, ECOSTRESS, NLDAS, HLS, Landsat) y cuáles no son de
la NASA (USDA NASS, CDL, CSB, gSSURGO, USGS 3DEP), la unidad espacial y temporal, los 7 estados, cómo se arma la
tabla anual y qué controles de calidad pasa. Usá `docs/datasets/*.md`, `docs/research/citas_nasa.md` y el
CLAUDE.md. Una tabla por paquete con las columnas principales (nombre, descripción en inglés, unidad, fuente).

No inventes columnas ni cifras: si un número no está en los data cards, no va. Solo documentación.

## Terminada cuando

El documento en un PR.

## Notas
- 2026-11-15 04:11 · pro-1: tomada
- 2026-11-15 04:11 · pro-1: corte por el límite de uso de Claude; 0 commits guardados en tarea/T045-auto. El trabajador sigue cuando se renueve.
- 2026-11-15 04:26 · pro-1: soltada al arrancar: quedó tomada de una corrida anterior de esta máquina
- 2026-11-15 04:26 · pro-1: tomada
- 2026-11-15 04:29 · pro-1: terminada por el trabajador: PR #46, falta la revisión de max-1
