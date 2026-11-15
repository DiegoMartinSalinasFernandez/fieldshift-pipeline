---
id: T090
titulo: 'Research: fechas de MOD13Q1 que faltan en 2023–2025 (Planetary Computer vs. LP DAAC)'
estado: hecha
plan_minimo: pro
maquina: pro-1
estados: []
depende_de: []
rama: null
creada: 2026-11-15T06:44
actualizada: 2026-11-15 06:58
---

## Qué hacer

En `vegetacion_16d.csv` hay 22 fechas en 2023, 21 en 2024 y 15 en 2025 (lo normal son 23), tanto en IA/IL/IN como
en OH/NE/MN, y la tesela h09v05 no aparece en 2023–2024. Con la búsqueda STAC de `src/vegetacion/download.py`
(colección `modis-13Q1-061` de Planetary Computer) listá qué fechas y teselas faltan por año, y comparalo con
lo que publica LP DAAC (CMR, `short_name=MOD13Q1`, `version=061`, búsqueda sin login). Decí si faltan en la
fuente (por ejemplo, por un problema del satélite Terra) o solo en Planetary Computer, y si se pueden bajar de
otro lado sin Earthdata. No bajes los archivos.

Formato de research de la sección 8 del CLAUDE.md. Escribí `docs/research/modis_fechas.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 06:47 · pro-1: tomada
- 2026-11-15 06:58 · pro-1: terminada por el trabajador: PR #88, falta la revisión de max-1
