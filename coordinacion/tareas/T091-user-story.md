---
id: T091
titulo: User story in English with real county examples for the demo
estado: tomada
plan_minimo: pro
maquina: pro-3
estados: []
depende_de: []
rama: null
creada: 2026-11-15T06:44
actualizada: 2026-11-15 06:48
---

## Qué hacer

Escribí `docs/demo/user_story.md` **en inglés**: 2 o 3 historias cortas de un productor que compara rotaciones,
cada una con un condado real y números reales de los releases (por ejemplo, un condado de IA en la sequía de 2012,
uno de secano de NE como Boyd, uno de OH con siembra prevenida en 2019): rendimiento, lluvia de la temporada,
`spi3`, NDVI y proporción de maíz tras soja. Sacá los números con un script chico (`docs/demo/user_story.py`)
que lea los zips; no copies números a mano. **No inventes predicciones**: el modelo lo arma otro equipo; decí
qué mostraría la herramienta y qué parte es dato.

Los zips de los releases son públicos: bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/<release>/<archivo>` (dueño y repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256`. Van a `data/` (fuera de git), nunca al repo.

## Terminada cuando

La historia y el script en un PR.

## Notas
- 2026-11-15 06:48 · pro-3: tomada
