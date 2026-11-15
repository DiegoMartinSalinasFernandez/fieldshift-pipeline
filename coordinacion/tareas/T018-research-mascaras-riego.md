---
id: T018
titulo: 'Research: máscaras de riego para Nebraska y Kansas'
estado: tomada
plan_minimo: pro
maquina: pro-2
estados:
- NE
- KS
depende_de: []
rama: null
creada: 2026-11-15 01:40
actualizada: 2026-11-15 02:27
---

## Qué hacer

En Nebraska y Kansas una parte grande del maíz y la soja es regada, y el clima explica mucho menos su
rendimiento. T004 separa riego y secano con NASS; esto busca dónde está el riego en el mapa:

- productos con área regada por píxel o por condado que cubran NE y KS (por ejemplo LANID, MIrAD-US,
  IrrMapper, o los de los organismos de agua de cada estado), con resolución, años, método, dónde se bajan y
  licencia;
- cuáles tienen serie anual y cuáles son de un solo año;
- cómo se podría usar: % del área agrícola regada por condado y año, o una máscara para excluir píxeles
  regados de NDVI y suelo.

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets ni toques `src/` o `data/`.

Escribí `docs/research/riego_mascaras.md`. Si T004 ya tiene notas, leelas para no repetir.

## Terminada cuando

El research en un PR, con una propuesta concreta (qué producto, qué columna nueva y en qué paquete). La
decisión de cambiar un esquema queda para el humano.

## Notas
- 2026-11-15 02:27 · pro-2: tomada
