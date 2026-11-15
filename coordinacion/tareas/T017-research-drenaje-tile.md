---
id: T017
titulo: 'Research: dónde hay drenaje con caños (tile) por condado y por píxel'
estado: tomada
plan_minimo: pro
maquina: pro-1
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
creada: 2026-11-15 01:40
actualizada: 2026-11-15 02:22
---

## Qué hacer

El drenaje con caños cambia mucho cómo responde un lote al exceso de agua en primavera. Hoy solo lo tenemos
del Censo Agropecuario (por condado, 2012/2017/2022). Averiguá qué más hay para los 7 estados:

- mapas de drenaje por píxel publicados (por ejemplo los de 30 m derivados de suelo, pendiente y uso), con su
  método, año, resolución, dónde se bajan y licencia;
- cómo se comparan con el Censo y qué precisión reportan;
- si alguno sirve para el paquete `lotes` (por píxel de 30 m) o solo para el nivel de condado.

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets ni toques `src/` o `data/`.

Escribí `docs/research/drenaje_tile.md`.

## Terminada cuando

El research en un PR, con una recomendación de cuál usar (o ninguno) y por qué.

## Notas
- 2026-11-15 02:22 · pro-1: tomada
