---
id: T068
titulo: 'Research: precisión del CDL en Michigan y Dakota del Norte'
estado: hecha
plan_minimo: pro
maquina: pro-3
estados:
- MI
- ND
depende_de: []
rama: null
creada: 2026-11-15 05:42
actualizada: 2026-11-15 06:02
---

## Qué hacer

Igual que `docs/research/cdl_precision_mo_wi_sd.md` (podés reusar su script de extracción), para MI y ND,
2008–2025: precisión del productor y del usuario de maíz, soja, trigo (invierno y primavera), avena, alfalfa,
heno, pastizal, barbecho, girasol y canola. Señalá las clases donde el CDL no sirve para rotaciones.

Formato de research de la sección 8 del CLAUDE.md. Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes datasets grandes ni toques `data/`. MI y ND **no** están en `config/config.yaml`: es research para que el humano decida una cuarta tanda.

Escribí `docs/research/cdl_precision_mi_nd.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 05:56 · pro-3: tomada
- 2026-11-15 06:02 · pro-3: terminada por el trabajador: PR #62, falta la revisión de max-1
