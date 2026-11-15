---
id: T106
titulo: Data quality page in English for the submission
estado: hecha
plan_minimo: pro
maquina: pro-3
estados: []
depende_de: []
rama: null
creada: 2026-11-15T07:32
actualizada: 2026-11-15 07:51
---

## Qué hacer

Escribí `docs/demo/data_quality.md` **en inglés**, para los jueces (criterio de validez): cómo se controlan los
datos (`validar_csv()`, `scripts/verificar_entrega.py`, `scripts/qa_release.py`), qué dio el QA de OH/NE/MN
(`docs/qa/oh_ne_mn.md`: eventos extremos que se ven en los datos, totales de NASS que cierran, rangos), y los
problemas conocidos que no se esconden (`docs/demo/limitations.md`, `docs/research/modis_fechas.md`,
`docs/datasets/agua.md` sobre el filtro de 0,6). Corto, una tabla de eventos y otra de controles. Solo lo que
digan esos documentos; enlazala desde `docs/demo/project_page.md`.

## Terminada cuando

La página en un PR.

## Notas
- 2026-11-15 07:49 · pro-3: tomada
- 2026-11-15 07:51 · pro-3: terminada por el trabajador: PR #99, falta la revisión de max-1
