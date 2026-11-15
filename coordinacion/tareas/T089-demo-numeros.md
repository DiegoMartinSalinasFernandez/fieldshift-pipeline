---
id: T089
titulo: Poner números y figuras reales en las láminas y la página del proyecto
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

`docs/demo/slides.md` y `docs/demo/project_page.md` (PR 51 y 52) se escribieron antes de los releases. Revisalos
y reemplazá cada número que no salga de un release o de un documento del repo por el valor real (cantidad de
estados, condados, años, variables, productos NASA), citando de dónde sale. Usá las figuras reales de
`docs/demo/fig/` (T074) donde el borrador dice "figura". Lo que no se pueda verificar, sacalo o marcalo como
pendiente. No inventes resultados de modelos: el modelo lo hace otro equipo.

Los zips de los releases son públicos: bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/<release>/<archivo>` (dueño y repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256`. Van a `data/` (fuera de git), nunca al repo.

## Terminada cuando

Las láminas y la página corregidas en un PR, con la lista de números cambiados y su fuente.

## Notas
