---
id: T100
titulo: Rellenar MODIS (MOD13Q1 y MOD11A2) desde LP DAAC con el código de T119 y reprocesar vegetación
estado: libre
plan_minimo: max
maquina: null
estados: []
depende_de:
- T119
rama: null
creada: 2026-11-15T07:02
actualizada: 2026-11-15 09:09
---

## Qué hacer

`docs/research/modis_fechas.md` (T090): en Planetary Computer faltan 11 compuestos de MOD13Q1 v061 en todo el
mundo (2023: `A2023049`; 2024: `A2024225`, `A2024353`; 2025: `A2025193` a `A2025305`), y LP DAAC los tiene.
Lo más grave es julio–noviembre de 2025: sin ellos no hay pico de NDVI de 2025.

1. En `src/vegetacion/download.py`, después de la búsqueda en Planetary Computer, completar con CMR/LP DAAC
   (login de Earthdata en `~/.netrc`) los compuestos que falten para las teselas de los estados de
   `FIELDSHIFT_ESTADOS`: bajar el HDF, leer NDVI, EVI y la confiabilidad del píxel con las mismas escalas que
   los COG de PC, y guardarlo en `data/raw/vegetacion/mod13q1/<año>/` con un nombre que diga de dónde vino.
   Registrar cada archivo en `manifest.csv`. Sin Earthdata, avisar y seguir como hoy (no fallar).
2. Prueba chica en `tests/` (sin red) de la parte que decide qué compuestos faltan.
3. Data card de `vegetacion`: fuente mixta (PC + LP DAAC) y qué compuestos vienen de cada una.

No cambies el esquema de los CSV. Más de 5 GB: preguntá antes (deberían ser ~66 archivos por grupo de estados).

**Desde 2026-11-15:** el código lo escribe T119 (Pro), que también cubre MOD11A2 (LST, `docs/research/lst_fechas.md`). Esta tarea queda para las máquinas Max con Earthdata: correr la bajada para sus estados, reprocesar `vegetacion`, revisar con `verificar_entrega.py` y republicar.

## Terminada cuando

El cambio y la prueba en un PR; después, cada máquina Max reprocesa vegetación de sus estados y republica.

## Notas
- 2026-11-15 07:51 · max-1: Ampliar a MOD11A2 (LST) según docs/research/lst_fechas.md (T105, PR 98): 20 compuestos enteros y 3 parciales en 2022–2025, ~0,9 GB para los 10 estados. Mejor calcular CMR − PC por producto, tesela y compuesto en el momento que usar una lista fija.
- 2026-11-15 09:09 · max-1: Desde PR 110 (T119) el relleno desde LP DAAC solo corre con FIELDSHIFT_RELLENO_LPDAAC=1 (además de ~/.netrc). Son ~8-14 GB para los 10 estados: necesita el OK del humano (regla 6) antes de prenderlo.
