---
id: T136
titulo: '`src/merge.py`: sumar economía, paisaje, NLDAS, ECOSTRESS, teledetección, censo y secuencias (código listo,
  espera OK)'
estado: tomada
plan_minimo: pro
maquina: pro-5
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:51
actualizada: 2026-11-15 09:54
---

## Qué hacer

Fila 27 de `para_decidir.md` y `docs/research/merge_faltantes.md` (T050): hoy `merge.py` une solo los paquetes del
principio. Implementá lo que propone el research:

- sumar los `*_anual.csv`, `*_estatico.csv` y `*_mensual.csv` de `economia`, `paisaje`, `nldas`, `ecostress` y
  `teledeteccion` (los que existan en la máquina; si un paquete no está, seguir sin él y avisar);
- `practicas_censo.csv` con el último censo ≤ `anio` (y una columna con el año del censo usado);
- `rotacion_secuencia.csv` según diga el research;
- los choques de nombres (`et_mm`, `frac_pixeles_validos` y los que encuentres): prefijo por paquete solo en las
  columnas que chocan, documentado.

Las columnas que hoy salen en `tabla_anual.csv` y `tabla_mensual.csv` no cambian de nombre. Extendé
`tests/test_merge.py` (sin red). Probalo con los CSV de un release publicado (`datos-oh-ne-mn`) y contá en el PR
cuántas columnas tiene cada tabla antes y después. Actualizá `docs/guia_tablas.md` y `docs/estructura_csv.md`
si listan las columnas.

**El PR no se une hasta que el humano diga que sí** a la fila 27 de `coordinacion/para_decidir.md`. Escribí
al principio del cuerpo del PR: "Espera el OK de para_decidir #27; no unir antes". No toques `src/common/` ni
`config/`. Otras tareas retenidas tocan `src/cultivos/` y `docs/datasets/cultivos.md` (T127, T132, T133, T134,
T135): trabajá en tu propia función o módulo y agregá tu sección al final del data card.

## Terminada cuando

El código, las pruebas sin red y la documentación en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:54 · pro-5: tomada
