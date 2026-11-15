---
id: T038
titulo: 'Propuesta: ventanas críticas por estado (floración y llenado)'
estado: tomada
plan_minimo: pro
maquina: pro-3
estados:
- IA
- IL
- IN
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-15 03:20
actualizada: 2026-11-15 03:13
---

## Qué hacer

El CLAUDE.md fija las ventanas para todos los estados: temporada abril–septiembre, julio (floración del maíz) y
agosto (llenado de la soja). Con 7 estados, Kansas y Minnesota están a semanas de distancia. Usando
`config/cultivos_estado.csv` (Handbook 628), `docs/research/crop_progress_estados_nuevos.md` y las fechas de
Crop Progress (`fenologia_estado.csv` si tenés datos, o la publicación semanal), proponé:

- para cada estado, la ventana de floración del maíz (por ejemplo del 25 % al 75 % *silking*) y la de llenado de
  la soja, en días del año, con la mediana 2008–2025 y el rango;
- si conviene pasar de "julio" y "agosto" a ventanas por estado, y qué columnas de `clima_anual.csv` cambiarían
  (por ejemplo `prec_jul_mm` → `prec_floracion_mm`).

Escribí `docs/research/ventanas_por_estado.md` con el formato de research (sección 8). **No cambies código ni
esquemas:** es una propuesta para el humano.

## Terminada cuando

La propuesta en un PR.

## Notas
- 2026-11-15 03:13 · pro-3: tomada
