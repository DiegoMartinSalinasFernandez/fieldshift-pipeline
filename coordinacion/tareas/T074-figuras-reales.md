---
id: T074
titulo: Figuras de la demo con los datos publicados de OH, NE y MN
estado: tomada
plan_minimo: pro
maquina: pro-2
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15 05:59
actualizada: 2026-11-15 06:04
---

## Qué hacer

`docs/demo/figuras.py` (PR 53) baja los zips con `gh`, que en algunas máquinas no anda. Agregale una opción que
los baje con `urllib` desde la URL pública del release (sin `gh` ni token) y controle el `.sha256`. Después
corrélo con `datos-oh-ne-mn` y subí los PNG que salgan a `docs/demo/fig/`, con el pie aclarando que son solo
OH, NE y MN. **Solo datos reales del release**: nada de datos de prueba en los PNG que se suben.

Los zips son públicos: si `gh release download` no anda en tu máquina, bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/datos-oh-ne-mn/<archivo>` (el dueño y el repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256` de cada zip. Los zips van a `data/` (fuera de git), nunca al repo.

## Terminada cuando

El cambio en el script y los PNG reales en un PR.

## Notas
- 2026-11-15 06:04 · pro-2: tomada
