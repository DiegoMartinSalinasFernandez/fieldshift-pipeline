---
id: T155
titulo: Prueba real de `scripts/unir_estados.py` con `datos-oh-ne-mn` y `datos-mo-wi-sd` (fuera de git)
estado: hecha
plan_minimo: pro
maquina: max-1
estados: []
depende_de: []
rama: null
creada: 2026-11-15T14:14Z
actualizada: 2026-11-15 12:08
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
- 2026-11-15 12:03 · max-1: La toma max-1 a pedido del humano: además de probar unir_estados.py, que todos los nombres de columna coincidan entre la v3 (IA/IL/IN, loop) y los releases por paquete.
- 2026-11-15 12:08 · max-1: terminada: Hecha por max-1 a pedido del humano. Los 19 archivos por paquete que están en la v3 (IA/IL/IN) y en datos-oh-ne-mn y datos-mo-wi-sd tienen columnas idénticas (nombre y orden). Con el src/merge.py de la v3 salen tabla_anual (110 col.) y tabla_mensual (68) iguales a la v3 para los 6 estados; unidas, son 9 estados y 814 condados (68.720 y 253.968 filas), sin claves repetidas. Van en el zip local fieldshift_datos_todo_20261115.zip (ResearchAgent-entregas, carpeta unido_9_estados). 37 columnas tienen dato solo en IA/IL/IN (aptitud, teledeteccion, validacion, ecostress, hidrologia): T156. No se probó scripts/unir_estados.py: para este cruce se usó el merge de la v3.
