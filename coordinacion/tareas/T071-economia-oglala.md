---
id: T071
titulo: 'Arreglo: Oglala Lakota (SD) en las regiones del ERS de economia'
estado: tomada
plan_minimo: pro
maquina: pro-2
estados:
- SD
depende_de: []
rama: null
creada: 2026-11-15 05:42
actualizada: 2026-11-15 06:07
---

## Qué hacer

`reglink.xls` del ERS (regiones de recursos agrícolas por condado) tiene a Oglala Lakota con el código viejo
46113 (Shannon County); el Census usa 46102 desde 2015 (ver `docs/research/presupuestos_mo_wi_sd.md`). En
`src/economia/process.py`, mapeá 46113 → 46102 al leer `reglink.xls`, con un comentario y la fuente, y escribí
una prueba chica en `tests/` con un `reglink` inventado de dos filas. Buscá si hay otros cambios de código de
condado en los 10 estados de `config.yaml` (por ejemplo, Bedford City VA no aplica; revisá la lista del Census
de "substantial changes to counties") y aplicá lo mismo solo si afectan a esos estados. No cambies el esquema.

## Terminada cuando

El arreglo y la prueba en un PR, que pasen en Windows y en Linux.

## Notas
- 2026-11-15 06:07 · pro-2: tomada
