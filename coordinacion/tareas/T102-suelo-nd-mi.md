---
id: T102
titulo: 'Research: SSURGO y NASADEM en Dakota del Norte y Michigan'
estado: libre
plan_minimo: pro
maquina: null
estados:
- ND
- MI
depende_de: []
rama: null
creada: 2026-11-15T07:25
actualizada: 2026-11-15T07:25
---

## Qué hacer

Igual que `docs/research/suelo_ky.md` (podés reusar `suelo_ky_sda.py`), para ND y MI: áreas de levantamiento
publicadas o `NOTCOM`, condados con menos de 90 % del área con `mukey`, dato en las columnas de `Valu1`,
`muaggatt` y `chorizon` que usa `suelo_terreno`, y HEAD de las teselas NASADEM (37 en cada uno, según
`cuarta_tanda.md`). Formato de research de la sección 8 del CLAUDE.md. ND y MI **no** están en
`config/config.yaml`. No bajes datasets grandes ni toques `data/`.

Escribí `docs/research/suelo_nd_mi.md`.

## Terminada cuando

El research en un PR.

## Notas
