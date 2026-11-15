---
id: T105
titulo: 'Research: ¿MOD11A2 (LST) también tiene huecos en Planetary Computer?'
estado: hecha
plan_minimo: pro
maquina: pro-3
estados: []
depende_de: []
rama: null
creada: 2026-11-15T07:32
actualizada: 2026-11-15 07:49
---

## Qué hacer

`docs/research/modis_fechas.md` encontró 11 compuestos de MOD13Q1 que faltan en Planetary Computer en todo el
mundo. Hacé lo mismo (reusá `modis_fechas.py`) para MOD11A2 v061 (LST de 8 días, colección `modis-11A2-061`),
que usa `vegetacion` para `lst_dia_c` y `lst_noche_c`: qué compuestos de 2000–2025 faltan en PC contra CMR de LP
DAAC, para las teselas de los 10 estados. Sumá a la tabla de T100 lo que haga falta rellenar. No bajes archivos.

Formato de research de la sección 8 del CLAUDE.md. Escribí `docs/research/lst_fechas.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 07:39 · pro-3: tomada
- 2026-11-15 07:49 · pro-3: terminada por el trabajador: PR #98, falta la revisión de max-1
