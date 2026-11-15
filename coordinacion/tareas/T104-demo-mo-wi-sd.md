---
id: T104
titulo: Actualizar coverage, mapa y láminas cuando se publique datos-mo-wi-sd
estado: libre
plan_minimo: pro
maquina: null
estados:
- MO
- WI
- SD
depende_de:
- T062
rama: null
creada: 2026-11-15T07:25
actualizada: 2026-11-15T07:25
---

## Qué hacer

Cuando T062 esté hecha y el release `datos-mo-wi-sd` publicado: volvé a correr `docs/demo/coverage.py` y
`docs/demo/figuras.py --mapa` (el mapa marca MO/WI/SD como publicados), y actualizá en `docs/demo/slides.md`,
`docs/demo/project_page.md` y `docs/demo/video.md` los números de cobertura (condados y estados publicados), solo
con lo que digan los releases. Lo mismo con KS si `datos-ks` ya está.

## Terminada cuando

Los documentos y el mapa actualizados en un PR.

## Notas
