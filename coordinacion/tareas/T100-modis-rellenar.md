---
id: T100
titulo: Rellenar los 11 compuestos de MOD13Q1 que faltan en Planetary Computer (LP DAAC)
estado: libre
plan_minimo: max
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T07:02
actualizada: 2026-11-15T07:02
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

## Terminada cuando

El cambio y la prueba en un PR; después, cada máquina Max reprocesa vegetación de sus estados y republica.

## Notas
