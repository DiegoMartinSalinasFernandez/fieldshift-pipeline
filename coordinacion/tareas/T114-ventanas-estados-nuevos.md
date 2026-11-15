---
id: T114
titulo: 'Research: ventanas de floración del maíz y llenado de la soja en MO, WI, SD, ND, MI y KY'
estado: libre
plan_minimo: pro
maquina: null
estados:
- MO
- WI
- SD
- ND
- MI
- KY
depende_de: []
rama: null
creada: 2026-11-15T08:11
actualizada: 2026-11-15T08:11
---

## Qué hacer

`docs/research/ventanas_por_estado.md` midió, para los 7 primeros estados, la ventana de floración del maíz (25–75 %
*silking*) y de llenado de la soja (50 % *setting pods* → 25 % *dropping leaves*) con Crop Progress de NASS,
mediana 2008–2025 y rango. Extendelo a MO, WI, SD, ND, MI y KY con el mismo método (reusá
`ventanas_por_estado.py`; la clave de NASS está en `.env`, nunca la imprimas). Decí en cuántos estado-años la
ventana cae menos del 80 % dentro de julio o de agosto, y si con estos estados cambia la recomendación de esa
página (ventanas fijas de mes contra ventanas por estado y año). Agregá las filas a `ventanas_por_estado.csv`
sin cambiar las que ya están.

Formato de research de la sección 8 del CLAUDE.md, en una sección nueva de `ventanas_por_estado.md`.

## Terminada cuando

El research en un PR.

## Notas
