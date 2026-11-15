---
id: T039
titulo: Citas y DOIs de los productos de la NASA que usamos
estado: hecha
plan_minimo: pro
maquina: pro-2
estados: []
depende_de: []
rama: null
creada: 2026-11-15 03:20
actualizada: 2026-11-15 03:24
---

## Qué hacer

Para la entrega de Space Apps hay que citar bien los datos de la NASA. Recorré `docs/datasets/*.md` y
`manifest.csv` (si no lo tenés, `src/*/download.py`) y armá `docs/research/citas_nasa.md`: por cada producto
(POWER, GPM IMERG, MODIS MOD13Q1 / MOD11A2 / MOD16A2 / MCD12Q1, SMAP L4, GRACE-DA-DM, NASADEM, ECOSTRESS, NLDAS,
HLS, Landsat C2 L2 y los que aparezcan), nombre oficial, versión, DOI, cita recomendada por el DAAC, licencia y
qué columnas de nuestros CSV salen de ahí. Marcá también los que **no** son de la NASA (USDA, USGS, NRCS), con su
cita.

Solo fuentes oficiales (páginas del DAAC, CMR, DOI). Formato de research de la sección 8.

## Terminada cuando

El documento en un PR.

## Notas
- 2026-11-15 03:16 · pro-2: tomada
- 2026-11-15 03:24 · pro-2: terminada por el trabajador: PR #32, falta la revisión de max-1
