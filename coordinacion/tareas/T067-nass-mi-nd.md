---
id: T067
titulo: 'Research: cobertura de NASS y Crop Progress en Michigan y Dakota del Norte'
estado: hecha
plan_minimo: pro
maquina: pro-2
estados:
- MI
- ND
depende_de: []
rama: null
creada: 2026-11-15 05:42
actualizada: 2026-11-15 06:04
---

## Qué hacer

Igual que `docs/research/nass_mo_wi_sd.md`, para Michigan (26) y Dakota del Norte (38): cultivos y años por
condado en NASS (rendimiento, superficie, producción), 2024 y 2025, condados combinados (fila 998), y qué publica
Crop Progress. Particularidades: frijol seco y remolacha en MI; trigo de primavera, girasol, canola y cebada en
ND. Cuántos condados y cuánta superficie de maíz y soja suma cada uno.

Formato de research de la sección 8 del CLAUDE.md. Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes datasets grandes ni toques `data/`. MI y ND **no** están en `config/config.yaml`: es research para que el humano decida una cuarta tanda.

Escribí `docs/research/nass_mi_nd.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 05:56 · pro-2: tomada
- 2026-11-15 06:04 · pro-2: terminada por el trabajador: PR #64, falta la revisión de max-1
