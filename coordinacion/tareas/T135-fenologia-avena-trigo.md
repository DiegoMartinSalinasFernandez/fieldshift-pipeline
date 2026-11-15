---
id: T135
titulo: '`fenologia_estado.csv`: avena y trigo de invierno, año del trigo y marca de calidad (código listo, espera
  OK)'
estado: hecha
plan_minimo: pro
maquina: pro-4
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:33
actualizada: 2026-11-15 09:57
---

## Qué hacer

Fila 8 de `para_decidir.md` y `docs/research/crop_progress_estados_nuevos.md` (T019): en `fenologia_estado.csv`
sumar avena y trigo de invierno (con la etapa HEADED), asignar el trigo sembrado en otoño al `anio` de su cosecha
(documentarlo), y agregar una columna de calidad que marque los cruces del 50 % interpolados sobre huecos de más
de 2 semanas (por ejemplo, el cierre del gobierno de octubre de 2025). Las filas y columnas de maíz y soja no
cambian. Pruebas sin red: un cruce normal, uno sobre un hueco de 3 semanas y el trigo de otoño.

**El PR no se une hasta que el humano diga que sí** a la fila 8 de `coordinacion/para_decidir.md`. Escribí
al principio del cuerpo del PR: "Espera el OK de para_decidir #8; no unir antes". No cambies ninguna columna
que ya existe; no toques `src/common/` ni `config/`. Varias tareas retenidas tocan `src/cultivos/` y
`docs/datasets/cultivos.md` (T127 `riego.py`, T132 censo): trabajá en tu propio módulo o función y agregá tu
sección al final del data card, para que los conflictos sean fáciles.

## Terminada cuando

El código, las pruebas sin red y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:52 · pro-4: tomada
- 2026-11-15 09:57 · pro-4: terminada por el trabajador: PR #126, falta la revisión de max-1
