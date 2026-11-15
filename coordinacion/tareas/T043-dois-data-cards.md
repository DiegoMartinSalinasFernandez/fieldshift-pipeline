---
id: T043
titulo: DOIs de la NASA en los data cards y versiones pendientes
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15 03:45
actualizada: 2026-11-15 03:42
auto: false
---

## Qué hacer

T039 (`docs/research/citas_nasa.md`, PR 32) dejó pendientes:

- qué versión de SPL4SMGP (V7 o V8) usa Crop-CASMA, para citar el DOI correcto;
- si los últimos meses de IMERG que trae POWER (después de 2025-09-30, fin de la Final V07 en CMR) son Late o
  Early, según la documentación de POWER;
- las citas sin verificar (3DEP, ERS, Census, CoCoRaHS, el paper de Crop-CASMA de 2022).

Resolvé lo que puedas con fuentes oficiales y actualizá `citas_nasa.md`. Después agregá el DOI en la sección
"Fuentes" de los data cards de `agua`, `clima`, `vegetacion`, `nldas`, `ecostress` y `suelo_terreno`.
**Ojo:** si el data card lo genera `src/<paquete>/data_card.py`, el cambio va ahí (si no, se pisa en la próxima
corrida); no toques `src/common/`. Si IMERG de POWER resulta ser Late o Early en los últimos meses, anotalo en el
data card de `clima` como problema conocido.

## Terminada cuando

Los cambios en un PR.

## Notas
- 2026-11-15 03:30 · pro-2: tomada
- 2026-11-15 03:30 · pro-2: intento sin cambios (You've hit your weekly limit · resets Nov 16, 9am (America/Argentina/Buenos_Aires)); reintento
- 2026-11-15 03:30 · pro-2: bloqueada: el trabajador no logró cambios en 2 intentos. You've hit your weekly limit · resets Nov 16, 9am (America/Argentina/Buenos_Aires)
- 2026-11-15 03:42 · max-1: liberada y en pausa (auto: false): pro-2 llegó al límite semanal y el trabajador no lo reconoce, así que bloquea cada tarea que toma. Se reactiva cuando pro-2 pare.
- 2026-11-15 03:42 · max-1: liberada y en pausa (auto: false): pro-2 llegó al límite semanal y el trabajador no lo reconoce, así que bloquea cada tarea que toma. Se reactiva cuando pro-2 pare.
