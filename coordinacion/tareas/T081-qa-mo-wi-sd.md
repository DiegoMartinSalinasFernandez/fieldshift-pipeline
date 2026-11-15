---
id: T081
titulo: Control de calidad de MO, WI y SD con el release publicado
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
creada: 2026-11-15T06:18
actualizada: 2026-11-15T06:18
---

## Qué hacer

Cuando T062 esté hecha, el release `datos-mo-wi-sd` va a estar publicado. Hacé el mismo control que T073
(`docs/qa/oh_ne_mn.md`), para MO, WI y SD:

- `scripts/verificar_entrega.py` sobre los zips bajados;
- eventos de `docs/research/eventos_extremos_mo_wi_sd.md` (¿se ven en `spi3`, `ndvi_anom_z`, `sm_rootzone`,
  el rendimiento?), precisión del CDL de `cdl_precision_mo_wi_sd.md`, totales de superficie de maíz y soja por
  estado contra NASS a nivel estado;
- outliers por condado, % de faltantes por columna y por estado contra IA/IL/IN y OH/NE/MN. Ojo con los condados
  de WI sobre los lagos Míchigan y Superior (SMAP) y con Oglala Lakota (46102) en SD.

Los zips son públicos: bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/datos-mo-wi-sd/<archivo>`
(el dueño y el repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256`.
Los zips van a `data/` (fuera de git), nunca al repo.

Escribí `docs/qa/mo_wi_sd.md` con APTO / NO APTO por paquete y abrí una tarea nueva por cada problema de código.

## Terminada cuando

El informe en un PR.

## Notas
