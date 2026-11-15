---
id: T155
titulo: Prueba real de `scripts/unir_estados.py` con `datos-oh-ne-mn` y `datos-mo-wi-sd` (fuera de git)
estado: tomada
plan_minimo: pro
maquina: max-1
estados: []
depende_de: []
rama: null
creada: 2026-11-15T14:14Z
actualizada: 2026-11-15 12:03
---

## Qué hacer

Bajá los zips de los dos releases publicados a `data/entregas/` (fuera de git) y corré `scripts/unir_estados.py`
con los dos. Revisá el resultado:

- que no haya claves repetidas;
- que las columnas y los tipos sean los mismos en los dos;
- que `fips` tenga 5 dígitos y que los 521 condados estén.

Después corré `src/merge.py` sobre lo unido, si se puede.

Anotá cada diferencia que rompa o ensucie la unión: columnas que están en un release y no en el otro, cambios de
unidades o nombres. Arreglá en `scripts/unir_estados.py` lo que sea del script y dejá en el PR, como hallazgo, lo
que sea de los datos. Esto prepara T008, que va a juntar todos los estados para ML.

## Terminada cuando

PR con CI en verde y lo que se encontró en el cuerpo del PR.

## Notas
- 2026-11-15 12:03 · max-1: tomada
