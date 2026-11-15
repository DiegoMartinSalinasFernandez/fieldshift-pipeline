---
id: T076
titulo: 'Comparar OH/NE/MN con IA/IL/IN: qué cambia para el modelo'
estado: tomada
plan_minimo: pro
maquina: pro-3
estados:
- IA
- IL
- IN
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15 05:59
actualizada: 2026-11-15 06:02
---

## Qué hacer

Con `datos-oh-ne-mn` y la descripción de IA/IL/IN en los data cards (`docs/datasets/*.md`, `merge.md`), escribí
para el equipo de ML qué cambia entre los dos grupos: rango de rendimientos, lluvia de temporada, GDD, riego (NE),
fechas de siembra (`fenologia_estado.csv`), suelos (`suelo_terreno_estatico.csv`) y proporción de maíz tras maíz.
Una tabla por variable con mediana y percentiles 10 y 90 por grupo, calculados con un script chico
(`docs/research/comparar_grupos.py`) sobre los CSV del release. **No entrenes modelos ni calcules tendencias**:
solo describir.

Los zips son públicos: si `gh release download` no anda en tu máquina, bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/datos-oh-ne-mn/<archivo>` (el dueño y el repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256` de cada zip. Los zips van a `data/` (fuera de git), nunca al repo.

Escribí `docs/research/comparar_grupos.md`.

## Terminada cuando

El documento y el script en un PR.

## Notas
- 2026-11-15 06:02 · pro-3: tomada
