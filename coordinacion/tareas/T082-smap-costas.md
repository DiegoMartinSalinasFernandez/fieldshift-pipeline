---
id: T082
titulo: 'Research: SMAP de Crop-CASMA en condados con costa de lago (MN, WI, MI, OH)'
estado: hecha
plan_minimo: pro
maquina: pro-1
estados:
- MN
- WI
- OH
depende_de: []
rama: null
creada: 2026-11-15T06:18
actualizada: 2026-11-15 06:25
---

## Qué hacer

`docs/research/cuarta_tanda.md` encontró celdas de SMAP (Crop-CASMA, capa `SUB`) de hasta 0,89 m³/m³ en MI,
por encima del rango físico 0–0,6 de §7. Con el release `datos-oh-ne-mn` (`agua_diario.csv`, `agua_mensual.csv`)
fijate si en los condados de MN y OH con costa sobre el lago Superior o el Erie las medias de condado se acercan
al límite, y qué dice la documentación de Crop-CASMA sobre la máscara de agua. Para un día de muestra, pedí
al WPS (como `src/agua/download.py`) el recorte de MN y contá las celdas > 0,6 y dónde están. Decí si hace falta
enmascarar agua en `src/agua/process.py` antes de promediar (no lo cambies: es research).

Los zips son públicos: bajalos con `curl -L` desde la URL del release (dueño y repo salen de
`git remote get-url origin`); a `data/`, nunca al repo.

Escribí `docs/research/smap_costas.md` (formato de la sección 8 del CLAUDE.md).

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 06:20 · pro-1: tomada
- 2026-11-15 06:25 · pro-1: terminada por el trabajador: PR #73, falta la revisión de max-1
