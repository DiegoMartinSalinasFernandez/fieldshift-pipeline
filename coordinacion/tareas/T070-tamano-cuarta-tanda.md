---
id: T070
titulo: 'Research: cuánto pesa y cuánto tarda una cuarta tanda (MI, ND, KY)'
estado: hecha
plan_minimo: pro
maquina: pro-4
estados:
- MI
- ND
- KY
depende_de: []
rama: null
creada: 2026-11-15 05:42
actualizada: 2026-11-15 06:13
---

## Qué hacer

Para que el humano decida si suma una cuarta tanda, estimá por estado (MI, ND y KY) y por paquete el tamaño de
la descarga y el tiempo, escalando desde lo medido en el repo (T001: OH+NE+MN = 21 GB; T002: KS = 11 GB; los
`du` por paquete que figuran en las notas de T003, T013 y T062): CDL, MODIS (teselas nuevas: ND toca h10v04 y
h11v04, ¿alguna más?), SMAP, SSURGO, NLDAS, paisaje. Decí qué teselas MODIS o celdas de grilla nuevas hacen
falta y si algún paquete no cubre ese estado (por ejemplo Crop-CASMA o GRACE-DA-DM de EE.UU.).

Formato de research de la sección 8 del CLAUDE.md. Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes datasets grandes ni toques `data/`. MI, ND y KY **no** están en `config/config.yaml`: es research para que el humano decida una cuarta tanda.

Escribí `docs/research/cuarta_tanda.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 05:56 · pro-4: tomada
- 2026-11-15 06:13 · pro-4: terminada por el trabajador: PR #69, falta la revisión de max-1
