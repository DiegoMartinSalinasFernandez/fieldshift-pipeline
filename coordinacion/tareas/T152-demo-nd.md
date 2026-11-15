---
id: T152
titulo: Actualizar coverage, mapa y láminas con ND (11 estados en `config.yaml`) y `datos-nd` cuando salga
estado: libre
plan_minimo: pro
maquina: null
estados:
- ND
depende_de:
- T149
rama: null
creada: 2026-11-15T14:14Z
actualizada: 2026-11-15T14:14Z
---

## Qué hacer

ND entró a `config/config.yaml`: ahora son 11 estados y 972 condados planeados. Cuando T149 publique `datos-nd`,
hacé lo mismo que T104 (PR 144):

- `docs/demo/coverage.py` → `coverage.md`;
- `figuras.py --mapa --solo-mapa` → `fig0_mapa.png`;
- los números de `slides.md`, `project_page.md` y `video.md`.

Todos los números salen de los releases publicados, nunca a mano.

## Terminada cuando

PR con CI en verde y lo que se encontró en el cuerpo del PR.

## Notas
