---
id: T137
titulo: Sorgo granífero como clase de rotación en Kansas (código listo, espera OK)
estado: tomada
plan_minimo: pro
maquina: pro-2
estados:
- KS
depende_de: []
rama: null
creada: 2026-11-15T09:51
actualizada: 2026-11-15 09:52
---

## Qué hacer

Fila 11 de `para_decidir.md` y `docs/research/sorgo.md` (T022): sumar sorgo (CDL 4 y doble cultivo 236) **solo
como clase de rotación**: en `rotacion_anual.csv`, `pct_sorgo` y las transiciones sorgo–trigo que proponga el
research; en `rotacion_secuencia.csv` (si existe en tu rama), la secuencia trigo–sorgo–barbecho. No como cultivo
con rendimiento en `produccion_anual.csv`. Las columnas de hoy no cambian. Pruebas sin red con un raster chico.
Probalo con un recorte de KS si tenés el CDL; si no, decilo.

**El PR no se une hasta que el humano diga que sí** a la fila 11 de `coordinacion/para_decidir.md`. Escribí
al principio del cuerpo del PR: "Espera el OK de para_decidir #11; no unir antes". No toques `src/common/` ni
`config/`. Otras tareas retenidas tocan `src/cultivos/` y `docs/datasets/cultivos.md` (T127, T132, T133, T134,
T135): trabajá en tu propia función o módulo y agregá tu sección al final del data card.

## Terminada cuando

El código, las pruebas sin red y la documentación en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:52 · pro-2: tomada
