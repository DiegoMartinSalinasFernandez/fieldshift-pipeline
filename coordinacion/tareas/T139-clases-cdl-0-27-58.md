---
id: T139
titulo: Sumar las clases 0, 27 y 58 del CDL a `clases_cdl.csv` (código listo, espera OK)
estado: tomada
plan_minimo: pro
maquina: pro-4
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:51
actualizada: 2026-11-15 10:03
---

## Qué hacer

Fila 19 de `para_decidir.md` y `docs/research/cdl_csb.md`: sumar las clases 0 (sin dato / fondo), 27 (centeno) y
58 (trébol / flores silvestres) a `data/reference/clases_cdl.csv` con el nombre oficial y el grupo que proponga el
research, y revisar qué cambia en las máscaras y en `rotacion_anual.csv` (por ejemplo, si el 0 deja de contar como
píxel válido o si el centeno pasa a "cultivo de cobertura"). Documentá el efecto: con un recorte del CDL de
cualquier estado, cuánto cambia `pct_*` y `frac_pixeles_validos` antes y después. Pruebas sin red.

**El PR no se une hasta que el humano diga que sí** a la fila 19 de `coordinacion/para_decidir.md`. Escribí
al principio del cuerpo del PR: "Espera el OK de para_decidir #19; no unir antes". No toques `src/common/` ni
`config/`. Otras tareas retenidas tocan `src/cultivos/` y `docs/datasets/cultivos.md` (T127, T132, T133, T134,
T135): trabajá en tu propia función o módulo y agregá tu sección al final del data card.

## Terminada cuando

El código, las pruebas sin red y la documentación en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 10:00 · pro-5: tomada
- 2026-11-15 10:01 · pro-5: corte por el límite de uso de Claude; 0 commits guardados en tarea/T139-auto. El trabajador sigue cuando se renueve.
- 2026-11-15 10:01 · pro-5: soltada: pro-5 sin cuota de Claude hasta 15/11 13:00
- 2026-11-15 10:01 · pro-4: tomada
- 2026-11-15 10:03 · pro-4: corte por el límite de uso de Claude; 1 commits guardados en tarea/T139-auto. El trabajador sigue cuando se renueve.
