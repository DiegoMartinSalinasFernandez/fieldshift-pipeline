---
id: T097
titulo: QA genérico para cualquier release (para reusar en KS y MO/WI/SD)
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T06:55
actualizada: 2026-11-15T06:55
---

## Qué hacer

`docs/qa/oh_ne_mn_qa.py` (T073) tiene fijos los estados y algunas rutas. Pasalo a `scripts/qa_release.py`, que
reciba el nombre del release (o la carpeta de zips descomprimidos) y saque los estados de `condados.csv`; que
genere las mismas secciones (faltantes contra IA/IL/IN, eventos de un archivo de eventos que se pase por
argumento, rangos, outliers por vecinos, totales de NASS). Probalo con `datos-oh-ne-mn` y comprobá que da los
mismos números que `docs/qa/oh_ne_mn.md`. Agregá una prueba chica en `tests/` con datos inventados (solo para la
prueba, en `tests/`).

Los zips de los releases son públicos: bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/<release>/<archivo>` (dueño y repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256`. Van a `data/` (fuera de git), nunca al repo. **Solo datos reales del release** en las figuras.

## Terminada cuando

El script y la prueba en un PR.

## Notas
