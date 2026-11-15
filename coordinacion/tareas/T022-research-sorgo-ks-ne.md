---
id: T022
titulo: 'Research: ¿sumar sorgo granífero para Kansas y Nebraska?'
estado: libre
plan_minimo: pro
maquina: null
estados:
- KS
- NE
depende_de: []
rama: null
creada: 2026-11-15 02:50
actualizada: 2026-11-15 02:50
---

## Qué hacer

En Kansas el sorgo granífero ocupa unos 2,5 millones de acres (la tabla del Handbook 628 de 2009) y no está en
los cultivos de `config.yaml`. Antes de que el humano decida si sumarlo, averiguá:

- superficie sembrada y cosechada de sorgo granífero por estado en los 7 estados, 2015–2025 (NASS, nivel
  estado), y qué tan grande es frente a soja y trigo de invierno en KS y NE;
- si NASS publica rendimiento de sorgo por condado (años, cuántos condados por año, filas 998), con los
  `short_desc` exactos;
- el código de sorgo en el CDL y su precisión en KS y NE (metadatos de precisión del CDL por estado);
- qué haría falta para sumarlo (fila en `config/cultivos.csv`, conversión de bushel de 56 lb, rotaciones
  sorgo–trigo típicas de KS).

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets grandes ni toques `src/` o `data/`.

Escribí `docs/research/sorgo.md`. La consulta a Quick Stats podés hacerla con la API (si hay `NASS_API_KEY`) o
con la base completa si está en tu máquina.

## Terminada cuando

El research en un PR, con una recomendación (sumar o no, y por qué). La decisión es del humano.

## Notas
