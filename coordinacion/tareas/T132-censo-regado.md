---
id: T132
titulo: Riego por cultivo del Censo en `practicas_censo.csv` (código listo, espera OK)
estado: hecha
plan_minimo: pro
maquina: pro-2
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:24
actualizada: 2026-11-15 09:51
---

## Qué hacer

Fila 2 de `para_decidir.md` y `docs/research/censo_agropecuario.md` (T012): agregar a `practicas_censo.csv`
`pct_maiz_regado`, `pct_soja_regada` y `pct_cosechado_regado` (con `flag_nass` para `(D)`/`(Z)`), de los Censos
2012, 2017 y 2022, con los `short_desc` exactos del research. Va en el módulo de `src/cultivos/` que ya arma
`practicas_censo.csv`; T127 (riego de LANID) trabaja en `src/cultivos/riego.py`, así que no lo toques y, si los
dos cambian `docs/datasets/cultivos.md`, agregá tu sección al final para que el conflicto sea fácil.
Pruebas sin red con filas de Quick Stats de ejemplo. Probalo con NE (o el estado que tengas).

**El PR no se une hasta que el humano diga que sí** a la fila 2 de `coordinacion/para_decidir.md` (esquema
nuevo). Escribí al principio del cuerpo del PR: "Espera el OK de para_decidir #2; no unir antes".
No cambies ninguna columna que ya existe; no toques `src/common/` ni `config/`.

## Terminada cuando

El código, las pruebas sin red y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:44 · pro-2: tomada
- 2026-11-15 09:51 · pro-2: terminada por el trabajador: PR #123, falta la revisión de max-1
