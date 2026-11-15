---
id: T088
titulo: Data coverage page in English for the Space Apps submission
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T06:33
actualizada: 2026-11-15T06:33
---

## Qué hacer

Escribí `docs/demo/coverage.md` **en inglés**: qué datos hay publicados hoy, con números reales sacados de los
releases (`gh release list` o la página de releases): por release, los estados, condados, años, paquetes,
filas por archivo principal y tamaño. Contá las filas y los años con un script chico
(`docs/demo/coverage.py`) que lea los zips bajados; no copies números a mano. Agregá una tabla de qué productos
de la NASA entran (sale de `docs/research/citas_nasa.md`) y enlazá la página desde `docs/demo/project_page.md`.
Los releases que todavía no estén (KS, MO/WI/SD) se listan como "in progress", sin números.

Los zips de los releases son públicos: bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/<release>/<archivo>` (dueño y repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256`. Van a `data/` (fuera de git), nunca al repo.

## Terminada cuando

La página y el script en un PR.

## Notas
