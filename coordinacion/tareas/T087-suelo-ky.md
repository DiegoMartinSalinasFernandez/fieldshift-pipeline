---
id: T087
titulo: 'Research: SSURGO y NASADEM en Kentucky'
estado: hecha
plan_minimo: pro
maquina: pro-2
estados:
- KY
depende_de: []
rama: null
creada: 2026-11-15T06:33
actualizada: 2026-11-15 06:46
---

## Qué hacer

`docs/research/cuarta_tanda.md` no consultó SSURGO para KY. Con Soil Data Access (consultas chicas, como
`src/suelo_terreno/`), decí qué áreas de levantamiento de KY están publicadas y si alguna es `NOTCOM`, cuántos
condados quedan con menos de 90 % del área con `mukey`, y si las columnas que usa `suelo_terreno` (`Valu1`,
`muaggatt`, `chorizon`) tienen dato en KY. Para NASADEM, confirmá las 23 teselas con un HEAD.

Formato de research de la sección 8 del CLAUDE.md. KY **no** está en `config/config.yaml`: es research para que
el humano decida. No bajes datasets grandes ni toques `data/`.

Escribí `docs/research/suelo_ky.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 06:40 · pro-2: tomada
- 2026-11-15 06:46 · pro-2: terminada por el trabajador: PR #82, falta la revisión de max-1
