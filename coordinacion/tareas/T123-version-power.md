---
id: T123
titulo: Registrar la versión real de la API de NASA POWER en manifest.csv
estado: hecha
plan_minimo: pro
maquina: pro-5
estados: []
depende_de: []
rama: null
creada: 2026-11-15T08:55
actualizada: 2026-11-15 09:08
---

## Qué hacer

`docs/demo/pendientes_humano.md` (T118): en `manifest.csv` los pedidos de meteorología a POWER dicen "v2 (API)"
(escrito fijo en `src/clima/download.py`, líneas ~113 y ~129), y solo los de `IMERG_PRECTOT` dicen
"POWER API v2.10.3" (línea ~184, también fijo). Para citar bien la fuente hace falta la versión real.

1. Mirá qué devuelve la API de POWER en la respuesta (JSON `header`, campos de versión o `api`) para un pedido
   diario por punto chico (un punto, un mes). Documentalo en `docs/research/power_version.md` (formato §8).
2. Si la respuesta trae la versión, cambiá `src/clima/download.py` para escribir en `manifest.csv` la versión que
   devuelve la API, en vez del texto fijo, para las bajadas nuevas. No reescribas las filas viejas del manifest ni
   vuelvas a bajar nada (`data/raw/` no se toca). Prueba sin red con una respuesta de ejemplo.
3. Data card de `clima`: qué versión se usó y cómo saberla.

## Terminada cuando

El research, el cambio y la prueba en un PR, con CI en verde.

## Notas
- 2026-11-15 09:05 · pro-5: tomada
- 2026-11-15 09:08 · pro-5: terminada por el trabajador: PR #115, falta la revisión de max-1
