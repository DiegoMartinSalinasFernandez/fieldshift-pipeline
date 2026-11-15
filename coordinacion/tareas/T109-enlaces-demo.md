---
id: T109
titulo: Check every link in the submission pages (docs/demo, README)
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T07:46
actualizada: 2026-11-15T07:46
---

## Qué hacer

Antes del cierre (2026-11-15 23:59) los jueces van a abrir `README.md` y todo `docs/demo/`. Escribí
`scripts/revisar_enlaces.py`: recorre esos `.md`, comprueba que cada enlace relativo apunte a un archivo que
existe en el repo, que cada imagen exista, y que cada URL de release (`/releases/download/...` o `/releases/tag/...`)
responda 200 con `curl -I -L` (sin bajar el archivo). Las URL externas (NASA, USDA) solo con HEAD y un timeout
corto; si fallan, avisá pero no rompas. Corrélo, arreglá los enlaces rotos que sean del repo, y anotá en las Notas
los que no puedas arreglar (por ejemplo, un release que todavía no existe). Agregá una prueba sin red para la
parte de enlaces relativos.

## Terminada cuando

El script, la prueba y los arreglos en un PR.

## Notas
