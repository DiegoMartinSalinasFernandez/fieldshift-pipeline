---
id: T050
titulo: 'Propuesta: qué paquetes y columnas le faltan a merge.py'
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15 04:17
actualizada: 2026-11-15 04:17
---

## Qué hacer

`src/merge.py` une solo una parte de los paquetes. Según la bitácora de pro-5, no une economía, aptitud, paisaje,
teledetección, validación, ECOSTRESS, NLDAS ni hidrología. Sin cambiar `src/merge.py`, escribí
`docs/research/merge_faltantes.md` con:

- una tabla por paquete: archivos `*_anual.csv`, `*_estatico.csv` y `*_mensual.csv` que produce (según su
  `process.py` y su data card) y si `merge.py` los une hoy;
- los choques de nombres de columna entre paquetes (la misma columna en dos archivos) y cómo resolverlos;
- los archivos que no tienen la granularidad de las tablas unidas (por estado, por lote, por censo) y cómo
  entrarían (por los dos primeros dígitos de `fips`, por `anio_censo`, o afuera);
- el orden propuesto de los cambios.

**No cambies `src/merge.py`**: hay que sincronizarlo antes con la versión de ResearchAgent (T008). Es una
propuesta para el humano.

## Terminada cuando

La propuesta en un PR.

## Notas
