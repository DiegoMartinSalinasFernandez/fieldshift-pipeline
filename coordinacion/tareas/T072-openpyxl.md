---
id: T072
titulo: Agregar openpyxl a requirements.txt y probar los scripts que leen .xlsx
estado: hecha
plan_minimo: pro
maquina: pro-3
estados: []
depende_de: []
rama: null
creada: 2026-11-15 05:42
actualizada: 2026-11-15 06:09
---

## Qué hacer

Dos PRs (CDL 2024–2025 y siembra prevenida, ver `coordinacion/para_decidir.md` #13 y #17) necesitan `openpyxl`
para leer `.xlsx`, y no está en `requirements.txt`. Agregalo con la versión mínima que haga falta, buscá en
`src/` y `docs/research/*.py` los usos de `read_excel` con `.xlsx` y corré cada uno (o su parte de lectura) con
un archivo chico de prueba. Anotá en el PR qué scripts lo usan. Marcá #13 y #17 de `para_decidir.md` como
resueltos solo en lo que toca a `openpyxl`.

## Terminada cuando

El cambio en un PR, con la lista de scripts probados.

## Notas
- 2026-11-15 06:08 · pro-3: tomada
- 2026-11-15 06:09 · pro-3: terminada por el trabajador: PR #67, falta la revisión de max-1
