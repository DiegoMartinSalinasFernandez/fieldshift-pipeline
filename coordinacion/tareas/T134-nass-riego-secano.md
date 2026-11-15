---
id: T134
titulo: Rendimiento y superficie con riego y en secano de NASS en `produccion_anual.csv` (NE y KS, código listo,
  espera OK)
estado: hecha
plan_minimo: pro
maquina: pro-5
estados:
- NE
- KS
depende_de: []
rama: null
creada: 2026-11-15T09:33
actualizada: 2026-11-15 09:54
---

## Qué hacer

Fila 1 de `para_decidir.md` y `docs/research/riego_nass.md` (T004): las 11 columnas de riego y secano que propone
el research (`sup_sembrada_riego_ac`, `rend_riego_bu_ac`, `rend_secano_bu_ac`, `pct_sembrada_riego`…), con
`prodn_practice_desc` = `IRRIGATED` y `NON-IRRIGATED`, solo maíz, soja y trigo de invierno, donde NASS lo publica
(NE y KS, 2000–2018), con `flag_nass` para `(D)`/`(Z)` y celdas vacías donde no hay dato. Las filas de "ALL
PRODUCTION PRACTICES" no cambian. Mirá cómo lee hoy `src/cultivos` el archivo de Quick Stats y agregá una
función aparte. Pruebas sin red con filas de ejemplo. Probalo con NE si tenés el archivo.

**El PR no se une hasta que el humano diga que sí** a la fila 1 de `coordinacion/para_decidir.md`. Escribí
al principio del cuerpo del PR: "Espera el OK de para_decidir #1; no unir antes". No cambies ninguna columna
que ya existe; no toques `src/common/` ni `config/`. Varias tareas retenidas tocan `src/cultivos/` y
`docs/datasets/cultivos.md` (T127 `riego.py`, T132 censo): trabajá en tu propio módulo o función y agregá tu
sección al final del data card, para que los conflictos sean fáciles.

## Terminada cuando

El código, las pruebas sin red y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:34 · pro-5: tomada
- 2026-11-15 09:54 · pro-5: terminada por el trabajador: PR #125, falta la revisión de max-1
