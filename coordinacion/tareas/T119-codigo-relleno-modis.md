---
id: T119
titulo: Código para rellenar desde LP DAAC los compuestos de MODIS que faltan en Planetary Computer (MOD13Q1 y MOD11A2)
estado: tomada
plan_minimo: pro
maquina: pro-5
estados: []
depende_de: []
rama: null
creada: 2026-11-15T08:45
actualizada: 2026-11-15 08:50
---

## Qué hacer

Es la parte de código de T100, para que las máquinas Max solo tengan que correrlo. Leé `docs/research/modis_fechas.md`
(MOD13Q1, T090) y `docs/research/lst_fechas.md` (MOD11A2, T105).

1. En `src/vegetacion/download.py` (o un módulo nuevo en `src/vegetacion/`), después de la búsqueda en Planetary
   Computer: calcular, por producto, tesela y compuesto, **lo que está en CMR y no en PC** para las teselas de los
   estados de `FIELDSHIFT_ESTADOS` (no una lista fija; reusá la lógica de `docs/research/modis_fechas.py`).
2. Bajar esos gránulos de LP DAAC (login de Earthdata en `~/.netrc`; nunca imprimas credenciales), leer las capas
   que ya usa `process.py` (MOD13Q1: NDVI, EVI, confiabilidad del píxel; MOD11A2: `LST_Day_1km`, `LST_Night_1km`,
   `QC_Day`, `QC_Night`) con las mismas escalas y la misma resolución que los COG de PC (`download.py` usa la
   overview 0; remuestreá igual), y guardarlos en `data/raw/vegetacion/<producto>/<año>/` con un nombre que diga
   que vienen de LP DAAC. Cada archivo con su fila en `manifest.csv`.
3. Sin Earthdata configurado: avisar y seguir como hoy, sin fallar.
4. Pruebas sin red en `tests/`: la diferencia CMR − PC (con respuestas de ejemplo guardadas en la prueba), el
   nombre y la ruta de salida, y que sin `~/.netrc` no falle.
5. Data card de `vegetacion`: fuente mixta (PC + LP DAAC), y que `A2001169`, parte de `A2001177`, `A2022289` y
   ene–feb de 2000 no existen en ninguna fuente.

No cambies el esquema de los CSV. Si tu máquina tiene Earthdata, probá la bajada de **un** gránulo de cada producto
y contá el resultado en las Notas; si no, decilo. El volumen total es de ~7–13 GB (MOD13Q1) + ~0,9 GB (MOD11A2)
para los 10 estados: no bajes todo, eso lo hacen las Max en T100.

## Terminada cuando

El código, las pruebas y el data card en un PR, con CI en verde.

## Notas
- 2026-11-15 08:50 · pro-5: tomada
