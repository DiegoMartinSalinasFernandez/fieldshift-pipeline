---
id: T107
titulo: Pruebas sin red de los scripts de la demo (coverage, user_story, figuras)
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T07:32
actualizada: 2026-11-15T07:32
---

## Qué hacer

`docs/demo/coverage.py`, `docs/demo/user_story.py` y `docs/demo/figuras.py` bajan zips y reescriben partes de
los `.md` entre marcas. Agregá pruebas en `tests/` sin red: con un zip chico inventado (solo para la prueba,
creado en un directorio temporal) que imite la estructura de un release, comprobá que cada script cuenta bien
filas y años, que reemplaza solo lo que está entre sus marcas y que falla con un mensaje claro si el `.sha256` no
coincide. Si para probarlos hace falta separar una función, hacelo sin cambiar lo que escriben.

## Terminada cuando

Las pruebas en un PR, que pasen en Windows y en Linux.

## Notas
