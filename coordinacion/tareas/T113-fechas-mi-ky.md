---
id: T113
titulo: 'Research: calendario de siembra y cosecha de Michigan y Kentucky (para cultivos_estado.csv)'
estado: hecha
plan_minimo: pro
maquina: pro-4
estados:
- MI
- KY
depende_de: []
rama: null
creada: 2026-11-15T08:11
actualizada: 2026-11-15 08:18
---

## Qué hacer

Lo mismo que T108 (`docs/research/fechas_nd.md`) para MI y KY: tablas del USDA Agricultural Handbook 628 de cada
estado (copiá las filas tal cual y la página impresa), filas propuestas para `config/cultivos_estado.csv` **sin
aplicarlas** (MI y KY no están en `config/config.yaml`), y comparación con el promedio de 5 años de Crop Progress
de cada estado. Reusá `docs/research/fechas_nd_cp.py` con el estado como argumento, sin cambiar lo que hace por
defecto. Si algún cultivo necesita un código nuevo, decilo y remití a T103.

Formato de research de la sección 8 del CLAUDE.md. Escribí `docs/research/fechas_mi_ky.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 08:13 · pro-4: tomada
- 2026-11-15 08:18 · pro-4: terminada por el trabajador: PR #105, falta la revisión de max-1
