---
id: T053
titulo: Glosario en inglés de las columnas (CSV para el frontend)
estado: hecha
plan_minimo: pro
maquina: pro-5
estados: []
depende_de: []
rama: null
creada: 2026-11-15 04:17
actualizada: 2026-11-15 04:32
---

## Qué hacer

El frontend y los jueces necesitan los nombres de las columnas en inglés. Escribí
`docs/datasets/glosario_en.csv` con `paquete, archivo, columna, descripcion_en, unidad, fuente, id_catalogo`,
una fila por columna de cada data card de `docs/datasets/*.md` (las tablas `| archivo | columna | ...`).
Un script chico `docs/datasets/glosario_en.py` que lo arme leyendo los data cards, para poder regenerarlo;
la traducción de cada descripción la escribís vos en un diccionario dentro del script.

No inventes columnas: solo las que están en los data cards. Si una descripción no se entiende, dejala marcada.

## Terminada cuando

El CSV y el script en un PR, con una prueba chica en `tests/` que controle que cada columna de los data cards
está en el glosario.

## Notas
- 2026-11-15 04:28 · pro-5: tomada
- 2026-11-15 04:32 · pro-5: terminada por el trabajador: PR #49, falta la revisión de max-1
