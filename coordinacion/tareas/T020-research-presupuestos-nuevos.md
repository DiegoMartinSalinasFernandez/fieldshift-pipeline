---
id: T020
titulo: 'Research: presupuestos por cultivo de las universidades de OH, NE, MN y KS'
estado: tomada
plan_minimo: pro
maquina: pro-1
estados:
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-15 01:40
actualizada: 2026-11-15 02:36
---

## Qué hacer

Para IA e IL usamos los presupuestos de Iowa State (Ag Decision Maker) y de farmdoc
(`docs/research/precios_margenes.md`). Para los estados nuevos buscá lo equivalente de la universidad de cada
estado (extensión de Ohio State, Nebraska-Lincoln, Minnesota y Kansas State, o FINBIN para Minnesota):

- qué publican (costos por acre de maíz, soja, trigo de invierno, avena; con y sin riego en NE y KS), desde qué
  año, en qué formato y dónde;
- cómo se comparan con los costos regionales del ERS que ya tenemos (`docs/research/regiones_ers.md`);
- si conviene usarlos o quedarse solo con ERS para que los 7 estados sean comparables.

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets ni toques `src/` o `data/`.

Escribí `docs/research/presupuestos_estados_nuevos.md`.

## Terminada cuando

El research en un PR, con una recomendación.

## Notas
- 2026-11-15 02:36 · pro-1: tomada
