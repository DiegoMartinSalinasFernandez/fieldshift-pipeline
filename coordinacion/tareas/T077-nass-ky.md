---
id: T077
titulo: 'Research: cobertura de NASS y Crop Progress en Kentucky'
estado: hecha
plan_minimo: pro
maquina: pro-1
estados:
- KY
depende_de: []
rama: null
creada: 2026-11-15T06:18
actualizada: 2026-11-15 06:36
---

## Qué hacer

Igual que `docs/research/nass_mi_nd.md` (podés reusar sus scripts), para Kentucky (21): cultivos y años por
condado en NASS (rendimiento, superficie, producción de maíz, soja, trigo de invierno, heno; tabaco solo para
contar superficie), 2024 y 2025, condados combinados (fila 998) y qué publica Crop Progress. Cuántos condados y
cuánta superficie de maíz y soja suma; cuántos de los 120 condados casi no tienen agricultura (este de KY).

Formato de research de la sección 8 del CLAUDE.md. Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes datasets grandes ni toques `data/`. KY **no** está en `config/config.yaml`: es research para que el humano decida una cuarta tanda (ver `docs/research/cuarta_tanda.md`).

Escribí `docs/research/nass_ky.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 06:25 · pro-1: tomada
- 2026-11-15 06:36 · pro-1: terminada por el trabajador: PR #77, falta la revisión de max-1
