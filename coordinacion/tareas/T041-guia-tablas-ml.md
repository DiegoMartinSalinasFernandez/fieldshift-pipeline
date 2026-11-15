---
id: T041
titulo: Guía de las tablas unidas para el equipo de ML (docs/guia_tablas.md)
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15 04:00
actualizada: 2026-11-15 03:42
auto: false
---

## Qué hacer

El equipo de ML usa `data/processed/tabla_anual.csv` y `tabla_mensual.csv`. Escribí `docs/guia_tablas.md`, en
castellano llano, leyendo `src/merge.py`, `loop/spec/entregables.yaml`, `docs/datasets/*.md` y la sección 4 del
CLAUDE.md:

- qué es una fila de cada tabla (claves: `fips`, `anio`, `cultivo`, `mes`) y cómo se reconoce el estado por los
  dos primeros dígitos de `fips`;
- de qué paquete sale cada grupo de columnas, con un enlace a su data card, y qué columnas se repiten por
  cultivo o por estado;
- qué queda afuera de las tablas y dónde está (`rotacion_secuencia`, `practicas_censo`, los diarios, `lotes`);
- convenciones: unidades en el nombre, faltantes vacíos, `flag_nass`, ventanas fijas (abril–septiembre, invierno
  previo, julio y agosto);
- advertencias que ya están en los data cards (por ejemplo el sesgo del CDL 2024 en los bordes, los rendimientos
  de 2025, cobertura de SMAP desde 2015) y lo que **no** se hace acá (sacar la tendencia, z-scores) porque va
  dentro de cada fold.

No inventes columnas: si dudás de una, mirá el spec. Solo documentación: no toques `src/` ni `data/`.

## Terminada cuando

La guía en un PR.

## Notas
- 2026-11-15 03:29 · pro-2: tomada
- 2026-11-15 03:29 · pro-2: intento sin cambios (You've hit your weekly limit · resets Nov 16, 9am (America/Argentina/Buenos_Aires)); reintento
- 2026-11-15 03:29 · pro-2: bloqueada: el trabajador no logró cambios en 2 intentos. You've hit your weekly limit · resets Nov 16, 9am (America/Argentina/Buenos_Aires)
- 2026-11-15 03:42 · max-1: liberada y en pausa (auto: false): pro-2 llegó al límite semanal y el trabajador no lo reconoce, así que bloquea cada tarea que toma. Se reactiva cuando pro-2 pare.
- 2026-11-15 03:42 · max-1: liberada y en pausa (auto: false): pro-2 llegó al límite semanal y el trabajador no lo reconoce, así que bloquea cada tarea que toma. Se reactiva cuando pro-2 pare.
