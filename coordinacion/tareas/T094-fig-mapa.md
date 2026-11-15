---
id: T094
titulo: 'Figura de la demo: mapa de condados del Corn Belt con el estado de cada release'
estado: tomada
plan_minimo: pro
maquina: pro-3
estados: []
depende_de: []
rama: null
creada: 2026-11-15T06:55
actualizada: 2026-11-15 07:08
---

## Qué hacer

La lámina 1 (`docs/demo/slides.md`) pide un mapa que no existe. Agregá a `docs/demo/figuras.py` una figura
`fig0_mapa.png`: los condados de los 10 estados de `config/config.yaml` (Census cartographic boundary 1:500k,
como `src/base/download.py`, bajado a `data/`), coloreados por grupo (IA/IL/IN, OH/NE/MN, KS, MO/WI/SD) y con
el estado de su release (publicado o en proceso, según la página de releases). Leyenda en inglés, colores aptos
para daltónicos. Subí el PNG a `docs/demo/fig/` y ponelo en la lámina 1.

## Terminada cuando

El script y el PNG en un PR.

## Notas
- 2026-11-15 07:08 · pro-3: tomada
