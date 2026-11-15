# Data card — paisaje

Cobertura del suelo por condado desde USGS Annual NLCD (National Land Cover Database anual,
Collection 1 versión 1, 30 m): % del área en cultivos, pasturas y heno, bosque, humedales, urbano y
agua, y la superficie impermeable media.

## Archivos

- `data/processed/paisaje/paisaje_anual.csv` — `fips, anio, ...`, una fila por condado y año. Cobertura real: 7325 filas, 293 condados, años 2000-2024.

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| paisaje_anual.csv | pct_cultivos_nlcd | % del área del condado en Cultivated Crops (clase NLCD 82) | % | USGS Annual NLCD C1V1 LndCov (30 m) |  | 2000 | 2024 | 0.00 |
| paisaje_anual.csv | pct_pasturas_heno_nlcd | % del área del condado en Pasture/Hay (clase NLCD 81) | % | USGS Annual NLCD C1V1 LndCov (30 m) |  | 2000 | 2024 | 0.00 |
| paisaje_anual.csv | pct_bosque_nlcd | % del área del condado en bosque (clases NLCD 41, 42 y 43) | % | USGS Annual NLCD C1V1 LndCov (30 m) |  | 2000 | 2024 | 0.00 |
| paisaje_anual.csv | pct_humedales_nlcd | % del área del condado en humedales (clases NLCD 90 y 95) | % | USGS Annual NLCD C1V1 LndCov (30 m) |  | 2000 | 2024 | 0.00 |
| paisaje_anual.csv | pct_urbano_nlcd | % del área del condado en desarrollo urbano (clases NLCD 21 a 24) | % | USGS Annual NLCD C1V1 LndCov (30 m) |  | 2000 | 2024 | 0.00 |
| paisaje_anual.csv | pct_agua_nlcd | % del área del condado en agua abierta (clase NLCD 11) | % | USGS Annual NLCD C1V1 LndCov (30 m) |  | 2000 | 2024 | 0.00 |
| paisaje_anual.csv | impermeable_pct | Superficie impermeable media del condado (media de Annual NLCD FctImp, 0-100 % por píxel) | % | USGS Annual NLCD C1V1 FctImp (30 m) |  | 2000 | 2024 | 0.00 |

## Fuentes y acceso

- USGS EROS / MRLC, Annual NLCD Collection 1 v1 (1985-2024): mosaicos CONUS `Annual_NLCD_LndCov_<anio>_CU_C1V1.tif`
  y `Annual_NLCD_FctImp_<anio>_CU_C1V1.tif` (COG). Originales en `s3://usgs-landcover/annual-nlcd/c1/v1/cu/mosaic/`
  (requester-pays); se leen sin login desde el mirror público de Source Cooperative
  `https://data.source.coop/kylebarron/usgs-landcover/annual-nlcd/c1/v1/cu/mosaic/`.
- `src/paisaje/download.py` lee por ventana solo el bbox de cada estado (IA, IL, IN) y lo guarda tal cual
  (mismos valores, misma grilla de 30 m) en `data/raw/paisaje/Annual_NLCD_<producto>_<anio>_<estado>_C1V1.tif`.

## Supuestos

- Fuente: Annual NLCD (una capa por año) en lugar de las ediciones clásicas de NLCD. Acceso por el mirror
  de Source Cooperative (copia de `s3://usgs-landcover`, que es requester-pays), no por el sitio de MRLC:
  el bucket público `s3-us-west-2.amazonaws.com/mrlc` devuelve 403 o un archivo de 42 bytes para estos nombres.
- La grilla de NLCD está en Albers CONUS con datum WGS84 (`AEA WGS84`); los condados se reproyectan a ese CRS.
  La diferencia con EPSG:5070 (NAD83) es de alrededor de 1 m, despreciable a 30 m.
- Cada píxel se asigna al condado que contiene su centro (rasterización sin `all_touched`); cada recorte de
  estado se usa solo para los condados de ese estado.
- El % es sobre todos los píxeles del condado con dato (incluye agua abierta), no sobre la máscara agrícola.
  Valor 250 = sin dato, se excluye del denominador.
- `impermeable_pct` es la media de FctImp (0-100 %) sobre los píxeles del condado con dato.
- Annual NLCD C1V1 llega hasta 2024: 2025 queda sin filas hasta que USGS lo publique.
- No hay ID del catálogo para estas columnas (el catálogo es de la versión argentina): `id_catalogo` vacío.

## Problemas conocidos

- 2025 no existe todavía en Annual NLCD (C1V1 cubre 1985-2024).
- Si una ronda de descarga se cortó, algunos años o estados pueden faltar: sus celdas quedan vacías
  (ver desde/hasta y faltantes_pct en la tabla) hasta volver a correr `download.py`.
- La clase 82 de NLCD (Cultivated Crops) no separa cultivos; el CDL del paquete `cultivos` da el detalle.
