---
id: T115
titulo: 'How to add a new state: English guide for judges (scalability)'
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T08:11
actualizada: 2026-11-15 08:21
---

## Qué hacer

Escribí `docs/demo/add_a_state.md` **en inglés**: cómo se suma un estado nuevo de EE.UU. al pipeline, con los
pasos que de verdad se usaron para OH/NE/MN y MO/WI/SD (variable `FIELDSHIFT_ESTADOS`, `src/base`, orden de
`download.py` y `process.py` por paquete, `scripts/entregar.py`, `scripts/verificar_entrega.py`,
`scripts/qa_release.py`), cuánto pesa y cuánto tarda por estado (sacalo de `docs/research/cuarta_tanda.md` o del
research de T070, y de las notas de T003 y T062 en `coordinacion/tareas/`), y qué hay que mirar a mano (research
de NASS, CDL, eventos extremos, presupuestos: los de T077–T080 son el ejemplo). Corto, con una lista numerada y
una tabla de tiempos y tamaños. Solo números que estén en el repo, citando de dónde salen. Enlazala desde
`docs/demo/project_page.md` (criterio de escalabilidad) y comprobá los enlaces con
`python -X utf8 scripts/revisar_enlaces.py --sin-red`.

## Terminada cuando

La página en un PR.

## Notas
- 2026-11-15 08:20 · pro-3: tomada
- 2026-11-15 08:20 · pro-3: corte por el límite de uso de Claude; 0 commits guardados en tarea/T115-auto. El trabajador sigue cuando se renueve.
- 2026-11-15 08:21 · pro-3: soltada: pro-3 sin cuota de Claude hasta 15/11 10:50
