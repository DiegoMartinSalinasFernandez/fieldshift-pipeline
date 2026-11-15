---
id: T138
titulo: '`produccion_anual.csv` con la grilla completa condado × año × cultivo (código listo, espera OK)'
estado: hecha
plan_minimo: pro
maquina: pro-4
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:51
actualizada: 2026-11-15 10:01
---

## Qué hacer

Fila 7 de `para_decidir.md` y `docs/research/nass_2024_2025.md` (T011): que `produccion_anual.csv` tenga una fila
por cada `fips` de `condados.csv` × `anio` del período × cultivo, con celdas vacías donde NASS no publica (en
2024–2025 falta el rendimiento del 35–40 % de los condados). Agregá una columna que diga si la fila viene de NASS
o se completó (por ejemplo `fila_nass` 1/0); `flag_nass` sigue como está. Las columnas de hoy no cambian. Pruebas
sin red. Contá en el PR cuántas filas suma por estado y año con el release de OH/NE/MN.

**El PR no se une hasta que el humano diga que sí** a la fila 7 de `coordinacion/para_decidir.md`. Escribí
al principio del cuerpo del PR: "Espera el OK de para_decidir #7; no unir antes". No toques `src/common/` ni
`config/`. Otras tareas retenidas tocan `src/cultivos/` y `docs/datasets/cultivos.md` (T127, T132, T133, T134,
T135): trabajá en tu propia función o módulo y agregá tu sección al final del data card.

## Terminada cuando

El código, las pruebas sin red y la documentación en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:57 · pro-4: tomada
- 2026-11-15 10:01 · pro-4: terminada por el trabajador: PR #129, falta la revisión de max-1
