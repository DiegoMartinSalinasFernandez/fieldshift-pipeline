---
id: T054
titulo: 'Research: eventos extremos conocidos en OH, NE, MN y KS (2000–2025)'
estado: tomada
plan_minimo: pro
maquina: pro-2
estados:
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-15 04:17
actualizada: 2026-11-15 04:18
---

## Qué hacer

Para el control de calidad de los estados nuevos (T007) sirve saber qué tiene que verse en los datos. Armá una
tabla de eventos conocidos en OH, NE, MN y KS entre 2000 y 2025: sequías (2002, 2011–2012, 2022–2023 en KS),
inundaciones (2011 y 2019 en NE, 2019 en OH, con siembra prevenida), heladas tardías o tempranas, olas de
calor en floración. Por evento: estado, condados o región, año y meses, tipo, señal esperada en nuestros CSV
(por ejemplo `spi3` < −1,5, `ndvi_anom_z` negativo en julio, rendimiento de maíz bajo, `sm_rootzone` alto en
mayo), y fuente (US Drought Monitor, NOAA NCEI, informes de NASS o de las universidades).

Ya existe `docs/research/eventos_extremos.md` para IA, IL e IN: seguí su formato y no repitas lo que ya tiene.

Formato de research de la sección 8 del CLAUDE.md. Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes datasets grandes ni toques `data/`.

Escribí `docs/research/eventos_extremos_nuevos.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 04:18 · pro-2: tomada
