# Paquete 0 — Base

Condados de la zona de estudio (estados de `config/config.yaml`: IA, IL, IN), tabla de años con
las ventanas fijas de los archivos anuales y funciones comunes de `src/common/`.

- Descarga: `python src/base/download.py` (idempotente; registra en `manifest.csv`).
- Proceso: `python src/base/process.py` (sin argumentos; regenera `data/reference/condados.gpkg`,
  `condados.csv` y `anios.csv` desde `data/raw/base/` y `config/config.yaml`).

## Fuente

- US Census Bureau, Cartographic Boundary Files, Counties 1:500,000, vintage 2024
  (`cb_2024_us_county_500k.zip`, shapefile en NAD83 / EPSG:4269).
  https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip — sin login.

## Salidas

- `data/reference/condados.gpkg`: capa `condados`, un polígono por condado, EPSG:4326, con las
  mismas columnas que `condados.csv`.
- `data/reference/condados.csv`: una fila por condado (293: IA 99, IL 102, IN 92).
- `data/reference/anios.csv`: una fila por año de 2000 a 2025.

## En los releases

`scripts/entregar.py` sube a cada release `datos-<estados>` un `datos-<estados>_base.zip` (con su `.sha256`)
con `data/reference/condados.gpkg` (filtrado a los estados del release si trae más), `condados.csv` (las
mismas filas), `anios.csv` y un `README.md`. Los zips de cada paquete siguen trayendo `condados.csv` y
`anios.csv`, sin polígonos. Los releases publicados antes de T126 no tienen el zip de base.

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| condados.csv | fips | Código FIPS del condado: 2 dígitos del estado + 3 del condado, texto con ceros a la izquierda | código | US Census CB 2024 1:500k (STATEFP + COUNTYFP) | K01 | | | 0 |
| condados.csv | estado | Código postal de dos letras del estado, según config.yaml | código | config/config.yaml + STATEFP del Census | K02 | | | 0 |
| condados.csv | condado | Nombre del condado (campo NAME del Census) | texto | US Census CB 2024 1:500k | | | | 0 |
| condados.csv | lat_centroide | Latitud del centroide del polígono, calculado en EPSG:5070 y llevado a EPSG:4326 | grados | US Census CB 2024 1:500k (cálculo propio) | K06 | | | 0 |
| condados.csv | lon_centroide | Longitud del centroide del polígono, calculado en EPSG:5070 y llevado a EPSG:4326 | grados | US Census CB 2024 1:500k (cálculo propio) | K06 | | | 0 |
| condados.csv | area_km2 | Área total del polígono (tierra + agua interior) en Albers CONUS (EPSG:5070) | km2 | US Census CB 2024 1:500k (cálculo propio) | | | | 0 |
| anios.csv | anio | Año de la cosecha | año | config/config.yaml (periodo) | K03 | 2000 | 2025 | 0 |
| anios.csv | inicio_temporada | Inicio de la temporada de crecimiento (1 de abril del anio) | fecha YYYY-MM-DD | config/config.yaml (ventanas) | K04 | 2000 | 2025 | 0 |
| anios.csv | fin_temporada | Fin de la temporada de crecimiento (30 de septiembre del anio) | fecha YYYY-MM-DD | config/config.yaml (ventanas) | K04 | 2000 | 2025 | 0 |
| anios.csv | inicio_invierno_previo | Inicio del invierno previo (1 de noviembre del anio − 1) | fecha YYYY-MM-DD | config/config.yaml (ventanas) | K04 | 2000 | 2025 | 0 |
| anios.csv | fin_invierno_previo | Fin del invierno previo (31 de marzo del anio) | fecha YYYY-MM-DD | config/config.yaml (ventanas) | K04 | 2000 | 2025 | 0 |

## Funciones comunes (`src/common/`)

- `fecha_a_anio(fecha) -> int`: año calendario de una fecha (`YYYY-MM-DD`, `YYYY-MM`, date).
- `zonal_mean(raster, condados=None, nodata=None, mascara=None)`: media por condado de un
  raster de una banda; ignora nodata; con `mascara` (raster 0/1 alineado) usa solo píxeles = 1.
  Devuelve `fips, media, frac_pixeles_validos`.
- `bu_ac_a_kgha(cultivo) -> float`: factor bu/ac → kg/ha de `config.yaml` (maíz 62,77; soja y
  trigo 67,25; avena 35,87).
- `acres_a_ha(acres)`: acres × 0,4047.
- `validar_csv(ruta) -> list[str]`: claves primero y con formato, sin duplicados (incluye
  `cultivo` si está), `fips` existentes en `condados.csv`, `anio` coherente con `fecha`/`mes`,
  sin decimales con coma ni valores de relleno, rangos físicos (lluvia ≥ 0, NDVI −1 a 1,
  humedad 0–0,6, rendimiento de maíz 20–300 y soja 5–100 bu/ac, etc.). Lista vacía si está bien.

## Supuestos

- Se usa el Cartographic Boundary 1:500k de 2024 (no TIGER/Line): el CLAUDE.md permite cualquiera
  de los dos y el 1:500k es más liviano (11 MB para todo el país). Los límites de condado de
  IA, IL e IN no cambiaron en el período 2000–2025, así que un único vintage sirve para todo.
- `area_km2` es el área total del polígono (incluye agua interior), calculada en EPSG:5070. No
  es `ALAND` del Census.
- El centroide es el centroide geométrico del polígono (calculado en EPSG:5070), no el punto
  interno (`INTPTLAT/INTPTLON`) del Census; en condados convexos coinciden casi siempre dentro
  del polígono.
- `estado` es el código de dos letras de `config.yaml`, asignado por los 2 primeros dígitos
  del FIPS.
- Los polígonos se guardan en EPSG:4326 (reproyectados desde NAD83 / EPSG:4269).

## Problemas conocidos

- El 1:500k está generalizado: los bordes no son exactos a 30 m. Para estadísticas zonales con
  rasters de 30 m (CDL) la diferencia en el borde es mínima, pero existe.
- La zona (estados) está pendiente de confirmación por el equipo (`zona.confirmada: false`).
