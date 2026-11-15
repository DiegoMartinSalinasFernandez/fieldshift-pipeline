---
id: T073
titulo: Control de calidad de OH, NE y MN con el release publicado
estado: libre
plan_minimo: pro
maquina: null
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15 05:59
actualizada: 2026-11-15 05:59
---

## Qué hacer

`datos-oh-ne-mn` ya está publicado (8 zips, todos APTO en `scripts/verificar_entrega.py`). Hacé el control de
calidad que pide T007, solo para estos 3 estados y sin esperar a Kansas:

- correr `scripts/verificar_entrega.py` sobre los zips bajados;
- comparar con lo esperable: los eventos de `docs/research/eventos_extremos_nuevos.md` (¿se ven 2012, 2019, etc.
  en `spi3`, `ndvi_anom_z`, `sm_rootzone`, el rendimiento?), rangos de `docs/research/rangos_estados_nuevos.md`,
  totales de superficie de maíz y soja por estado contra los de NASS a nivel estado;
- outliers por condado (por ejemplo, lluvia o rendimiento muy distinto de sus vecinos) y % de faltantes por
  columna y por estado comparado con IA/IL/IN (`docs/datasets/*.md`).

Los zips son públicos: si `gh release download` no anda en tu máquina, bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/datos-oh-ne-mn/<archivo>` (el dueño y el repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256` de cada zip. Los zips van a `data/` (fuera de git), nunca al repo.

Escribí `docs/qa/oh_ne_mn.md` con APTO / NO APTO por paquete y la lista de problemas, y abrí una tarea nueva
(`scripts/tareas.py nueva`) por cada problema que haya que arreglar en el código.

## Terminada cuando

El informe en un PR.

## Notas
