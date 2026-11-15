---
id: T052
titulo: 'Research: cómo marcar riego por condado en Nebraska y Kansas'
estado: tomada
plan_minimo: pro
maquina: pro-4
estados:
- NE
- KS
depende_de: []
rama: null
creada: 2026-11-15 04:17
actualizada: 2026-11-15 04:17
---

## Qué hacer

En NE y KS una parte grande del maíz y la soja es de riego, y el rendimiento de riego no responde al clima como
el de secano. Hoy tenemos `pct_riego` del Censo (2012, 2017 y 2022) en `practicas_censo.csv`. Averiguá:

- qué otras fuentes dan el área regada por condado y por año: NASS Quick Stats SURVEY con
  `prodn_practice_desc = IRRIGATED / NON-IRRIGATED` (qué cultivos, condados y años trae para NE y KS), USGS
  MIrAD-US, LANID (Landsat-based irrigation dataset), USGS Water Use;
- para cada una: resolución, años, formato, licencia y si cubre IA, IL, IN, OH y MN también;
- cuál conviene para una columna anual `frac_riego` por condado, y cómo separar rendimiento de riego y secano
  en `produccion_anual.csv` sin cambiar su esquema (o qué cambio de esquema haría falta, para el humano).

Formato de research de la sección 8 del CLAUDE.md. Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes datasets grandes ni toques `data/`.

Escribí `docs/research/riego_ne_ks.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 04:17 · pro-4: tomada
