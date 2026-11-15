---
id: T051
titulo: Actualizar estructura_csv.md y guia_tablas.md a 7 estados
estado: tomada
plan_minimo: pro
maquina: pro-5
estados: []
depende_de: []
rama: null
creada: 2026-11-15 04:17
actualizada: 2026-11-15 04:24
---

## Qué hacer

`docs/estructura_csv.md` y `docs/guia_tablas.md` todavía hablan de 3 estados (IA, IL, IN). Actualizalos a los
7 estados de `config/config.yaml` (IA, IL, IN, OH, NE, MN, KS):

- condados por estado (contalos en `data/reference/condados.csv` si está en la máquina; si no, usá los data
  cards y decí de dónde sale cada número);
- cómo se publican los datos por grupo de estados (`scripts/entregar.py`, releases `datos-<estados>`) y cómo
  se unen (`scripts/unir_estados.py`);
- qué cambia para ML: los estados nuevos tienen riego (NE, KS) y trigo de invierno (KS).

Solo documentación. No inventes cifras: si un número no está en el repo, no va.

## Terminada cuando

Los dos documentos en un PR.

## Notas
- 2026-11-15 04:24 · pro-5: tomada
