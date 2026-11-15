---
id: T023
titulo: Descargas con un bbox por estado (vegetacion, nldas y CDL)
estado: libre
plan_minimo: pro
maquina: null
estados:
- OH
- NE
- MN
- KS
depende_de:
- T021
rama: null
creada: 2026-11-15 02:50
actualizada: 2026-11-15 02:50
---

## Qué hacer

T010 (PR 5) encontró que `vegetacion`, `nldas` y la búsqueda del CDL en `src/cultivos/download.py` usan **un
solo bbox** para todos los estados de la máquina. Con estados lejanos (OH y NE, o OH y MN) eso baja teselas
o ventanas de estados que no se usan. Además, la búsqueda STAC del CDL tiene `limit` 500 y no pagina.

1. Que cada una de esas descargas use un bbox por estado, sacado de `data/reference/condados.gpkg` (como hizo
   T010 en `src/ecostress/download.py` con `bboxes_cmr()`), y que no baje dos veces lo mismo.
2. Que la búsqueda STAC del CDL pagine (siga el link `next`) en lugar de depender de `limit`.
3. **Para IA, IL e IN no puede cambiar nada de lo que ya está en `data/raw/`**: los nombres de archivo y el
   contenido tienen que ser los mismos. Explicá en el PR por qué (o probalo con un `condados.gpkg` de prueba y
   las búsquedas STAC/CMR, sin bajar datos grandes).
4. No toques `src/common/` ni el esquema de ningún CSV.

Espera a T021 porque las dos tocan los `download.py`.

## Terminada cuando

Las tres descargas con un bbox por estado y la paginación del CDL, en un PR con la prueba descrita.

## Notas
