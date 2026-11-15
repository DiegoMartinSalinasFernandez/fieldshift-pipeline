---
id: T019
titulo: 'Research: NASS Crop Progress en los estados nuevos'
estado: libre
plan_minimo: pro
maquina: null
estados:
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-15 01:40
actualizada: 2026-11-15 01:40
---

## Qué hacer

`fenologia_estado.csv` sale de Crop Progress (nivel estado, semanal). Para OH, NE, MN y KS averiguá en Quick
Stats (`source_desc=SURVEY`, `statisticcat_desc=PROGRESS`):

- qué etapas hay para maíz, soja, trigo de invierno y avena (`short_desc` exactos: PLANTED, EMERGED, SILKING,
  BLOOMING, HEADED, HARVESTED…), desde qué año y si hay huecos;
- si en Kansas y Nebraska el trigo de invierno tiene etapas distintas (siembra en otoño, año de la cosecha);
- si `src/cultivos/process.py` arma bien `doy_50_*` para esas etapas, o qué supone de IA/IL/IN (leelo, no lo
  cambies).

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets ni toques `src/` o `data/`.

Escribí `docs/research/crop_progress_estados_nuevos.md`. La consulta a Quick Stats sí podés hacerla (API con
`NASS_API_KEY` si la hay, o la base `qs.crops_*` si está en tu máquina); no guardes los datos en el repo.

## Terminada cuando

El research en un PR, con una tabla por estado y cultivo de etapas y años.

## Notas
