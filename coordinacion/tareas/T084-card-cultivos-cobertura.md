---
id: T084
titulo: 'Data cards de cultivos y clima: cobertura de NASS por año y límites de POWER'
estado: tomada
plan_minimo: pro
maquina: pro-4
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15T06:27
actualizada: 2026-11-15 06:28
---

## Qué hacer

De `docs/qa/oh_ne_mn.md` (T073), problemas 1 y 5:

- En `docs/datasets/cultivos.md`, una sección "Cobertura de condados de NASS por estado y año": condados con
  `sup_sembrada_ac` de maíz y de soja por estado y año (los 7 estados que tengan release o datos en el repo), y
  el % de la superficie del estado que NASS junta en "OTHER (COMBINED) COUNTIES" (fila 998). Aviso claro: no
  hacer totales de estado sumando condados en 2018–2025; para superficie, usar `rotacion_anual.csv` (CDL).
  Calculalo con un script chico en `docs/datasets/` sobre los CSV publicados y la base de Quick Stats.
- En `docs/datasets/clima.md`: `doy_primera_helada` no ve heladas locales de los bajos (ejemplo: 20-8-2004 en
  el norte de MN, celda de POWER de 0,5°), y la razón IMERG/POWER de lluvia anual por estado (OH 1,18; MN y NE
  1,07).

Los zips de los releases son públicos (`curl -L` desde la URL del release; dueño y repo de
`git remote get-url origin`); van a `data/`, nunca al repo.

## Terminada cuando

El cambio en los data cards en un PR. No cambies código ni esquema.

## Notas
- 2026-11-15 06:28 · pro-4: tomada
