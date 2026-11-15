---
id: T026
titulo: 'Research: efecto rotación en el rendimiento (maíz tras soja vs. maíz tras maíz)'
estado: tomada
plan_minimo: pro
maquina: pro-4
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
creada: 2026-11-15 02:50
actualizada: 2026-11-15 02:45
---

## Qué hacer

La herramienta compara rotaciones, y una parte de la comparación sale de reglas (no del modelo). Buscá en
ensayos de largo plazo del Corn Belt (universidades de los 7 estados, revistas con revisión):

- cuánto rinde menos el maíz tras maíz que el maíz tras soja (en % y bu/ac), con el rango y de qué depende
  (dosis de N, clima, labranza, años desde el inicio del ensayo);
- el efecto en la soja tras soja y el beneficio de sumar trigo, avena o alfalfa a la rotación;
- si el efecto cambia entre estados (por ejemplo NE regado frente a IA secano).

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets grandes ni toques `src/` o `data/`.

Escribí `docs/research/efecto_rotacion.md`, con una tabla de ensayos (lugar, años, rotaciones, efecto, fuente).

## Terminada cuando

El research en un PR, con valores citados que se puedan usar como reglas y su incertidumbre.

## Notas
- 2026-11-15 02:45 · pro-4: tomada
