# Data card — cultivos

Paquete `cultivos` (CLAUDE.md §6.2). Fuente: base completa de USDA NASS Quick Stats
(`https://www.nass.usda.gov/datasets`), archivos `qs.crops_<fecha>.txt.gz` (encuesta y Crop
Progress) y `qs.census<anio>.txt.gz` (Censo Agropecuario), guardados tal cual en
`data/raw/cultivos/nass/`.

- Bajada: `python src/cultivos/download.py` (reanudable, registra en `manifest.csv`).
- Proceso: `python src/cultivos/process.py` (filtra cada archivo a IA, IL, IN una vez y guarda
  el filtrado en `data/interim/cultivos/*.filtrado.tsv`).
- Este data card: `python src/cultivos/data_card.py`.

## Columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| produccion_anual.csv | sup_sembrada_ac | Superficie sembrada (AREA PLANTED, todos los usos) | acres | USDA NASS Quick Stats (SURVEY, condado) | Y01 | 2000 | 2025 | 24.2 |
| produccion_anual.csv | sup_cosechada_ac | Superficie cosechada (AREA HARVESTED; maíz: grano) | acres | USDA NASS Quick Stats (SURVEY, condado) | Y02 | 2000 | 2025 | 1.5 |
| produccion_anual.csv | produccion_bu | Producción (PRODUCTION en BU; maíz: grano). Alfalfa y heno se miden en toneladas: vacía | bu | USDA NASS Quick Stats (SURVEY, condado) | Y03 | 2000 | 2025 | 24.2 |
| produccion_anual.csv | rend_bu_ac | Rendimiento (YIELD en BU / ACRE; maíz: grano). Alfalfa y heno: vacía | bu/ac | USDA NASS Quick Stats (SURVEY, condado) | Y04 | 2000 | 2025 | 24.2 |
| produccion_anual.csv | rend_kgha | rend_bu_ac × factor de config.yaml (bu_ac_a_kgha) | kg/ha | Derivada de NASS Quick Stats | Y04 | 2000 | 2025 | 24.2 |
| produccion_anual.csv | sup_sembrada_ha | sup_sembrada_ac × 0,4047 (acres_a_ha) | ha | Derivada de NASS Quick Stats | Y01 | 2000 | 2025 | 24.2 |
| produccion_anual.csv | ratio_cosechada | sup_cosechada_ac / sup_sembrada_ac | fracción | Derivada de NASS Quick Stats | Y05 | 2000 | 2025 | 24.2 |
| produccion_anual.csv | flag_nass | Código original de NASS cuando el valor está oculto: (D), (Z), (NA)… (separados por ;) | texto | USDA NASS Quick Stats (SURVEY, condado) |  | 2013 | 2013 | 98.5 |
| fenologia_estado.csv | doy_50_sembrado | Día del año en que se cruza el 50 % sembrado (PCT PLANTED, interpolado) | día del año | USDA NASS Quick Stats Crop Progress (SURVEY, estado) | CT03 | 2000 | 2025 | 0.6 |
| fenologia_estado.csv | doy_50_emergido | Día del año en que se cruza el 50 % emergido (PCT EMERGED) | día del año | USDA NASS Quick Stats Crop Progress (SURVEY, estado) |  | 2000 | 2025 | 1.3 |
| fenologia_estado.csv | doy_50_floracion | Día del año del 50 % en floración (maíz PCT SILKING, soja PCT BLOOMING) | día del año | USDA NASS Quick Stats Crop Progress (SURVEY, estado) | CT05 | 2000 | 2025 | 0.0 |
| fenologia_estado.csv | doy_50_cosechado | Día del año del 50 % cosechado (maíz: grano) | día del año | USDA NASS Quick Stats Crop Progress (SURVEY, estado) | CT04 | 2000 | 2025 | 0.0 |
| rotacion_anual.csv | pct_maiz | % del área agrícola del condado con maíz (CDL 1) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R04 | 2008 | 2025 | 0.0 |
| rotacion_anual.csv | pct_soja | % del área agrícola con soja (CDL 5) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R04 | 2008 | 2025 | 0.0 |
| rotacion_anual.csv | pct_trigo | % del área agrícola con trigo de invierno, solo o en doble cultivo con soja (CDL 24 y 26) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R04 | 2008 | 2025 | 0.0 |
| rotacion_anual.csv | pct_alfalfa | % del área agrícola con alfalfa (CDL 36) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R04 | 2008 | 2025 | 0.0 |
| rotacion_anual.csv | pct_heno | % del área agrícola con otro heno (CDL 37) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R04 | 2008 | 2025 | 0.0 |
| rotacion_anual.csv | pct_doble_trigo_soja | % del área agrícola con doble cultivo trigo/soja (CDL 26) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R09 | 2008 | 2025 | 0.0 |
| rotacion_anual.csv | pct_barbecho | % del área agrícola en barbecho (CDL 61) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R14 | 2008 | 2025 | 0.0 |
| rotacion_anual.csv | pct_maiz_tras_soja | % de los píxeles de maíz del anio que tenían soja en anio−1 (sobre los que en anio−1 tenían clase agrícola) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R03 | 2009 | 2025 | 5.6 |
| rotacion_anual.csv | pct_maiz_tras_maiz | % de los píxeles de maíz del anio que tenían maíz en anio−1 (sobre los que en anio−1 tenían clase agrícola) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R03 | 2009 | 2025 | 5.6 |
| rotacion_anual.csv | pct_soja_tras_maiz | % de los píxeles de soja del anio que tenían maíz en anio−1 (sobre los que en anio−1 tenían clase agrícola) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R03 | 2009 | 2025 | 5.6 |
| rotacion_anual.csv | pct_soja_tras_soja | % de los píxeles de soja del anio que tenían soja en anio−1 (sobre los que en anio−1 tenían clase agrícola) | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R03 | 2009 | 2025 | 5.6 |
| rotacion_secuencia.csv | pct_maiz_soja_alternado | % de los píxeles agrícolas los 8 años con maíz y soja alternados todos los años | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) |  | 2008-2015 | 2018-2025 | 0.0 |
| rotacion_secuencia.csv | pct_maiz_continuo | % de los píxeles agrícolas los 8 años con maíz 3 o más años seguidos | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R13 | 2008-2015 | 2018-2025 | 0.0 |
| rotacion_secuencia.csv | pct_soja_continua | % de los píxeles agrícolas los 8 años con soja 3 o más años seguidos | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R13 | 2008-2015 | 2018-2025 | 0.0 |
| rotacion_secuencia.csv | pct_rotacion_trigo | % de los píxeles agrícolas los 8 años con trigo (solo o en doble cultivo) al menos un año | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) |  | 2008-2015 | 2018-2025 | 0.0 |
| rotacion_secuencia.csv | pct_rotacion_alfalfa | % de los píxeles agrícolas los 8 años con alfalfa (CDL 36) al menos un año | % | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R10 | 2008-2015 | 2018-2025 | 0.0 |
| rotacion_secuencia.csv | cultivos_por_anio | N° de cultivos de la secuencia / 8 años (doble cultivo = 2, barbecho = 0), media de los píxeles | cultivos/año | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R05 | 2008-2015 | 2018-2025 | 0.0 |
| rotacion_secuencia.csv | diversidad_shannon | Índice de Shannon (ln) sobre las clases del CDL de la secuencia de 8 años, media de los píxeles | índice | USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025) | R11 | 2008-2015 | 2018-2025 | 0.0 |
| practicas_censo.csv | pct_cobertura | COVER CROP PLANTED, (EXCL CRP) / AG LAND, CROPLAND × 100 | % | USDA NASS Censo Agropecuario (Quick Stats CENSUS) |  | 2017 | 2022 | 33.6 |
| practicas_censo.csv | pct_labranza_cero | CONSERVATION TILLAGE, NO-TILL / AG LAND, CROPLAND × 100 | % | USDA NASS Censo Agropecuario (Quick Stats CENSUS) |  | 2017 | 2022 | 33.3 |
| practicas_censo.csv | pct_drenaje_tile | DRAINED BY TILE / AG LAND, CROPLAND × 100 | % | USDA NASS Censo Agropecuario (Quick Stats CENSUS) |  | 2017 | 2022 | 34.2 |
| practicas_censo.csv | pct_riego | AG LAND, IRRIGATED / AG LAND, CROPLAND × 100 | % | USDA NASS Censo Agropecuario (Quick Stats CENSUS) |  | 2012 | 2022 | 15.8 |

## Supuestos

- **Sin clave de la API de Quick Stats** (`NASS_API_KEY` no configurada): se usa la descarga
  pública de la base completa de Quick Stats, que tiene los mismos registros que la API. Los
  filtros son los del CLAUDE.md §6.2 aplicados sobre el archivo: `SOURCE_DESC=SURVEY`,
  `AGG_LEVEL_DESC=COUNTY`, estados de `config.yaml`, `PRODN_PRACTICE_DESC=ALL PRODUCTION
  PRACTICES`, `DOMAIN_DESC=TOTAL`, `FREQ_DESC=ANNUAL`, `REFERENCE_PERIOD_DESC=YEAR`
  (se descartan los pronósticos mensuales), años 2000-2025.
- Correspondencia de cultivos (`COMMODITY_DESC` / `CLASS_DESC`): maíz CORN / ALL CLASSES,
  soja SOYBEANS, trigo de invierno WHEAT / WINTER, avena OATS, alfalfa HAY / ALFALFA,
  heno HAY / (EXCL ALFALFA).
- Maíz: superficie sembrada para todos los usos; cosechada, producción y rendimiento de grano
  (`UTIL_PRACTICE_DESC=GRAIN`), así que `ratio_cosechada` del maíz excluye el silaje.
- Alfalfa y heno: NASS los mide en toneladas, no en bushels; `produccion_bu`, `rend_bu_ac` y
  `rend_kgha` quedan vacías para esos cultivos. NASS no publica superficie sembrada de heno.
- Valores ocultos de NASS (`(D)`, `(Z)`, `(NA)`, etc.) quedan vacíos con el código en
  `flag_nass`. La tendencia del rendimiento no se saca.
- Las filas OTHER (COMBINED) COUNTIES (`COUNTY_CODE` 998) quedan afuera; también todo fips que
  no esté en `data/reference/condados.csv`.
- Crop Progress: semanas con `WEEK_ENDING`; el 50 % se interpola linealmente entre las dos
  semanas que lo rodean. Si el primer informe del año ya supera 50 %, o el último no llega,
  la celda queda vacía. Maíz cosechado = grano (`UTIL_PRACTICE_DESC=GRAIN`).
- Censo: porcentajes sobre `AG LAND, CROPLAND - ACRES` del mismo condado y censo. Valores
  ocultos con (D) quedan vacíos; porcentajes fuera de 0-100 se dejan vacíos.
- **Máscara agrícola** (`data/reference/mascara_agricola.tif`): sale de la *2025 Cultivated
  Layer* oficial del CDL (`data/raw/cultivos/cdl/2025_cultivated_layer.zip`), que marca como
  cultivado (valor 2) lo que el CDL clasificó como cultivo en los años 2021-2025, y no de
  "cultivo en al menos un año 2008-2025" como pide el plan: los CDL anuales nacionales pesan
  ~1,8 GB por año y no entran en el límite de 5 GB. Se recorta al rectángulo de los condados
  de `config.yaml`, en EPSG:5070 y 30 m (1 = cultivado, 0 = no cultivado o fuera de los
  condados), GeoTIFF de 1 bit con compresión deflate (~18 MB).
- **Clases del CDL** (`data/reference/clases_cdl.csv`): códigos y nombres copiados de la
  tabla "Categorization Code / Land Cover" de los metadatos FGDC oficiales del CDL publicados
  por NASS (`metadata_wa23.htm`, el único archivo de metadatos por estado accesible en la
  página de NASS al momento de bajar; la tabla de clases es nacional). `grupo` es la
  clasificación del proyecto (maiz, soja, trigo_invierno, doble_trigo_soja, avena, alfalfa,
  heno, barbecho, pastizal, centeno, trebol y sin_dato para el 0; el resto `otro`).

- **CDL anual** (`rotacion_anual.csv`): CropScape no respondió y la descarga nacional pesa
  ~1,8 GB por año, así que se usan las teselas COG de 90 km × 90 km (EPSG:5070, 30 m) de la
  colección `usda-cdl` de Microsoft Planetary Computer (acceso público con token SAS anónimo,
  sin login), que son el CDL de NASS recortado en teselas. Se bajan solo las 69 teselas por
  año que tocan los condados (`data/raw/cultivos/cdl/teselas/`, ~2,3 MB cada una).
- **CDL 2022-2025**: Planetary Computer llega a 2021. Esos años salen del ImageServer público
  de CroplandCROS (la herramienta de NASS que reemplaza a CropScape, alojada en USDA ARS
  SCINet: `https://pdi.scinet.usda.gov/image/rest/services/CDL_WM/ImageServer`, sin login),
  que publica los CDL nacionales 1997-2025 (`2022_30m_cdls`, `2023_30m_cdls`,
  `2024_10m_cdls`, `2025_10m_cdls`). Se pide con `exportImage` cada tesela de la misma grilla
  de 90 km (bbox en EPSG:5070, 3000 × 3000 píxeles de 30 m, vecino más cercano, un solo raster
  por año con `esriMosaicLockRaster`, TIFF LZW) y se guarda tal cual la devuelve el servidor
  con el mismo nombre que las teselas de Planetary Computer. Control: la tesela 2021
  exportada así coincidió en el 100 % de los píxeles con la de Planetary Computer.
  **2024 y 2025 se publicaron a 10 m**: el servidor los remuestrea a 30 m por vecino más
  cercano (un píxel de cada bloque de 3 × 3), así que los % de esos años son una muestra de
  1/9 de los píxeles de 10 m, comparable con la serie de 30 m pero no idéntica a agregar a 10 m.
- Área agrícola del condado (denominador de los `pct_*`): píxeles del CDL dentro del polígono
  del condado con clases de cultivo 1-61 (incluye barbecho 61), 66-77 y 204-254; no incluye
  pasturas (62, 176) ni clases no agrícolas. Píxel asignado al condado si su centro cae dentro.
- Transiciones: proporción condicional, por píxel, entre el CDL de anio−1 y el de anio,
  sobre los píxeles del cultivo del anio que en anio−1 tenían una clase agrícola (la misma
  lista del área agrícola): ej. `pct_maiz_tras_soja` = píxeles soja→maíz / píxeles de maíz en
  anio con clase agrícola en anio−1 × 100. Solo si los dos años están completos.
- **Denominador de las transiciones (cambio del 2026-11-14, entrega v1.1 para ML)**: antes
  eran todos los píxeles del cultivo del anio. En 2024-2025 el CDL de 10 m llevado a 30 m no
  tiene los bordes de lote donde los tiene el de 30 m de 2023, y muchos píxeles de borde
  parecían venir de pasto, caminos o bosque: la mediana de los 293 condados del % de maíz que
  venía de maíz o soja caía de 96,9 % (2023) a 91,3 % (2024). Con el denominador nuevo queda
  en 98,0 %, como en 2015-2023 (97,3-98,5 %), salvo 2020, que sigue más bajo con las dos
  definiciones (94,4 % con la nueva). Las cuatro columnas suben 0,7-2,8 puntos en promedio en
  2009-2023. Contra una muestra independiente de puntos del CDL (McLean, IL y Story, IA;
  2017-2025) la diferencia media baja de 1,3-1,6 a 0,6 puntos (en 2024, de 3,3-3,9 a
  0,7-1,0). Remuestrear 2024 por mayoría (`RSP_Majority`) en lugar de vecino más cercano
  empeora los bordes, así que el corrimiento es del producto de 10 m y no del remuestreo.
- Un año entra a `rotacion_anual.csv` solo cuando están en raw todas sus teselas (la grilla
  esperada se calcula con los polígonos de los condados).

- **Secuencias de 8 años** (`rotacion_secuencia.csv`): no se bajaron las Crop Sequence
  Boundaries (CSB). Se calculan las mismas secuencias directamente por píxel del CDL (el CSB
  es un derivado del CDL), en ventanas de 8 años (`ventana` = `AAAA-AAAA`) con todos sus años
  completos en raw. Denominador: píxeles del condado con clase agrícola (misma lista que
  `rotacion_anual.csv`) en los 8 años. Definiciones: alternado = solo maíz (1) y soja (5) y
  distinto cultivo cada año; maíz continuo / soja continua = el mismo cultivo 3 o más años
  seguidos (definición R13 del catálogo), así que un píxel puede contar en las dos;
  trigo = clases 22, 23, 24, 26, 225, 230, 234, 236 y 238 en al menos un año; alfalfa = clase
  36 en al menos un año; `cultivos_por_anio` = cultivos de la secuencia / 8, con las clases
  "Dbl Crop" de `clases_cdl.csv` valiendo 2 y el barbecho (61) 0; `diversidad_shannon` =
  −Σ p ln p sobre las clases de la secuencia del píxel (máximo ln 8 ≈ 2,08), promediado.
- **Máscaras de maíz y soja** (`data/reference/mascara_maiz_<anio>.tif`,
  `mascara_soja_<anio>.tif`): misma grilla que `mascara_agricola.tif` (EPSG:5070, 30 m,
  GeoTIFF de 1 bit, deflate, ~16 MB); 1 = píxel con maíz (1) o soja (5) en el CDL de ese año y
  dentro de los condados. Se arman con las teselas del CDL de raw para los años completos;
  `process.py` no rehace las que ya existen.

## Problemas conocidos

- **CDL de dos accesos**: 2008-2021 de Planetary Computer y 2022-2025 de CroplandCROS (ver
  Supuestos). Si falta alguna tesela de un año, ese año no entra (ver `hasta`).
- NASS no publica todos los condados todos los años (confidencialidad, encuestas que se
  dejaron de hacer para avena y heno en muchos condados).
- **Censo 2012 sin prácticas**: el archivo `qs.census2012.txt.gz` no trae cultivos de
  cobertura, labranza cero ni drenaje con caños por condado (solo `AG LAND, CROPLAND` y riego),
  y los archivos de 2017 y 2022 no repiten 2012. Esas columnas quedan vacías en 2012.
- Los rendimientos de condado de 2024 se publicaron tarde; ver la columna `hasta`.
- **CDL de 10 m en 2024-2025**: sus bordes de lote no coinciden con los de la serie de 30 m.
  Las transiciones lo corrigen con su denominador (ver Supuestos), pero los % de área
  (`pct_maiz`, `pct_soja`, …) y las máscaras `mascara_maiz_<anio>` / `mascara_soja_<anio>`
  de esos años pueden diferir algo de lo que daría un CDL de 30 m.

## Cobertura de condados de NASS por estado y año

> **Aviso: no hagas totales ni promedios de estado sumando condados de `produccion_anual.csv` en 2018–2025.**
> En esos años NASS publica cada vez menos condados y junta el resto en "OTHER (COMBINED) COUNTIES"
> (`county_code` 998), que este paquete deja afuera (no es un condado). Sumando los condados publicados se
> llega a solo 48–81 % de la superficie sembrada del estado en el peor año de 2018–2025 (tabla de abajo).
> Para superficie por condado o por estado usá `rotacion_anual.csv` (CDL), que cubre todos los condados todos
> los años. Un rendimiento "de estado" armado con los condados publicados también queda sesgado.

Condados con `sup_sembrada_ac` publicada (valor numérico, sin la fila 998) y, entre paréntesis, el % de la
superficie sembrada del estado que NASS junta en las filas 998 (una por distrito agrícola; se suman). Fuente:
base completa de Quick Stats `qs.crops_20261114.txt.gz`; SURVEY, `<CULTIVO> - ACRES PLANTED`, año completo,
dominio TOTAL (es `ALL PRODUCTION PRACTICES`). Condados de cada estado: IA 99, IL 102, IN 92, OH 88, NE 93,
MN 87, KS 105. Script: `docs/datasets/cobertura_nass.py` (solo lee; la tabla es su salida tal cual).

**Maíz** (`CORN - ACRES PLANTED`): condados publicados (% de la superficie del estado en la fila 998)

| anio | IA | IL | IN | OH | NE | MN | KS |
|---|---|---|---|---|---|---|---|
| 2000 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 86 (0,0) | 91 (0,0) | 79 (0,0) | 105 (0,0) |
| 2001 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 86 (0,0) | 90 (0,0) | 79 (0,0) | 103 (0,1) |
| 2002 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 84 (0,1) | 90 (0,0) | 79 (0,1) | 105 (0,0) |
| 2003 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 86 (0,0) | 90 (0,0) | 79 (0,0) | 103 (0,0) |
| 2004 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 82 (0,2) | 90 (0,0) | 71 (0,5) | 105 (0,0) |
| 2005 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 86 (0,0) | 90 (0,0) | 75 (0,2) | 101 (0,5) |
| 2006 | 99 (0,0) | 102 (0,0) | 86 (0,5) | 80 (0,3) | 91 (0,0) | 75 (0,3) | 101 (0,2) |
| 2007 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 80 (0,3) | 90 (0,0) | 76 (0,0) | 97 (0,8) |
| 2008 | 99 (0,0) | 98 (0,1) | 90 (0,1) | 75 (0,8) | 85 (0,4) | 71 (1,8) | 52 (46,4) |
| 2009 | 99 (0,0) | 100 (0,1) | 88 (0,4) | 73 (1,3) | 83 (0,7) | 72 (0,6) | 74 (16,7) |
| 2010 | 99 (0,0) | 98 (0,2) | 92 (0,0) | 80 (0,3) | 87 (0,1) | 75 (0,2) | 88 (7,3) |
| 2011 | 99 (0,0) | 97 (0,2) | 83 (8,0) | 80 (3,0) | 87 (0,2) | 72 (0,7) | 85 (11,2) |
| 2012 | 99 (0,0) | 90 (3,9) | 84 (4,3) | 80 (2,3) | 85 (0,9) | 73 (0,9) | 87 (6,8) |
| 2013 | 99 (0,0) | 90 (4,3) | 75 (9,2) | 80 (0,8) | 81 (2,0) | 75 (1,0) | 75 (20,0) |
| 2014 | 99 (0,0) | 96 (1,7) | 87 (2,4) | 84 (0,9) | 83 (1,4) | 71 (0,6) | 72 (23,5) |
| 2015 | 95 (1,9) | 91 (3,3) | 85 (3,2) | 81 (2,4) | 78 (4,5) | 72 (1,5) | 58 (38,1) |
| 2016 | 99 (0,0) | 92 (5,6) | 81 (9,2) | 78 (1,1) | 81 (2,2) | 76 (1,1) | 66 (30,5) |
| 2017 | 95 (1,2) | 98 (0,1) | 85 (2,2) | 80 (1,8) | 73 (10,8) | 71 (2,4) | 71 (31,3) |
| 2018 | 93 (3,8) | 84 (6,1) | 80 (8,6) | 75 (6,8) | 72 (8,1) | 58 (13,7) | 58 (50,7) |
| 2019 | 88 (7,3) | 78 (16,7) | 69 (23,5) | 68 (13,3) | 69 (11,7) | 60 (11,8) | 55 (51,6) |
| 2020 | 95 (4,8) | 99 (0,1) | 89 (0,4) | 83 (0,5) | 83 (3,1) | 77 (2,2) | 90 (9,8) |
| 2021 | 84 (13,1) | 79 (18,3) | 73 (24,2) | 78 (9,0) | 55 (40,5) | 71 (13,1) | 75 (25,0) |
| 2022 | 97 (0,8) | 94 (5,0) | 81 (8,2) | 79 (2,0) | 70 (13,8) | 73 (9,1) | 79 (25,1) |
| 2023 | 87 (10,6) | 91 (6,2) | 74 (16,5) | 72 (12,0) | 69 (20,9) | 64 (14,5) | 74 (27,8) |
| 2024 | 73 (25,6) | 62 (35,0) | 71 (18,4) | 66 (17,2) | 60 (28,6) | 61 (21,3) | 59 (43,2) |
| 2025 | 79 (20,8) | 64 (35,6) | 60 (22,1) | 69 (18,9) | 46 (46,4) | 62 (21,2) | 52 (51,4) |

**Soja** (`SOYBEANS - ACRES PLANTED`): condados publicados (% de la superficie del estado en la fila 998)

| anio | IA | IL | IN | OH | NE | MN | KS |
|---|---|---|---|---|---|---|---|
| 2000 | 99 (0,0) | 102 (0,0) | 87 (0,4) | 79 (0,1) | 79 (0,0) | 74 (0,0) | 105 (0,0) |
| 2001 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 80 (0,1) | 80 (0,0) | 74 (0,0) | 94 (0,5) |
| 2002 | 99 (0,0) | 102 (0,0) | 87 (0,4) | 80 (0,1) | 78 (0,0) | 79 (0,0) | 95 (0,4) |
| 2003 | 99 (0,0) | 102 (0,0) | 87 (0,4) | 77 (0,1) | 75 (0,0) | 79 (0,0) | 93 (0,6) |
| 2004 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 79 (0,1) | 79 (0,0) | 76 (0,2) | 94 (1,4) |
| 2005 | 99 (0,0) | 102 (0,0) | 87 (0,4) | 80 (0,1) | 77 (0,0) | 76 (0,1) | 98 (1,2) |
| 2006 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 79 (0,1) | 77 (0,1) | 76 (0,2) | 92 (1,7) |
| 2007 | 99 (0,0) | 102 (0,0) | 87 (0,3) | 81 (0,0) | 76 (0,0) | 74 (0,1) | 92 (0,5) |
| 2008 | 99 (0,0) | 98 (0,3) | 90 (0,1) | 72 (3,7) | 72 (0,3) | 70 (1,3) | 50 (18,2) |
| 2009 | 99 (0,0) | 98 (0,3) | 90 (0,1) | 70 (1,5) | 74 (0,2) | 73 (0,1) | 65 (8,0) |
| 2010 | 99 (0,0) | 100 (0,1) | 89 (0,1) | 77 (0,4) | 73 (0,5) | 76 (0,0) | 86 (2,8) |
| 2011 | 99 (0,0) | 97 (0,3) | 85 (6,2) | 75 (2,1) | 75 (0,3) | 74 (0,1) | 81 (5,9) |
| 2012 | 99 (0,0) | 96 (0,9) | 86 (5,8) | 76 (3,4) | 73 (0,6) | 73 (1,3) | 73 (5,5) |
| 2013 | 99 (0,0) | 91 (3,6) | 74 (11,3) | 79 (0,5) | 71 (1,9) | 73 (0,3) | 70 (7,7) |
| 2014 | 99 (0,0) | 95 (1,5) | 88 (1,7) | 79 (0,5) | 68 (2,3) | 70 (1,8) | 65 (12,1) |
| 2015 | 97 (1,7) | 93 (4,1) | 87 (1,4) | 77 (0,7) | 62 (7,6) | 66 (5,3) | 54 (24,5) |
| 2016 | 99 (0,0) | 93 (4,7) | 82 (5,8) | 74 (1,1) | 66 (4,7) | 71 (0,7) | 59 (17,2) |
| 2017 | 96 (1,5) | 97 (0,6) | 88 (1,3) | 75 (2,0) | 55 (7,3) | 72 (0,8) | 67 (13,6) |
| 2018 | 96 (3,8) | 88 (5,4) | 83 (5,2) | 72 (5,4) | 54 (9,6) | 58 (15,1) | 53 (34,3) |
| 2019 | 82 (14,0) | 75 (19,5) | 72 (19,9) | 68 (10,2) | 44 (22,9) | 60 (15,3) | 47 (35,5) |
| 2020 | 86 (14,4) | 99 (0,9) | 88 (1,4) | 82 (3,1) | 69 (4,9) | 79 (2,3) | 75 (2,6) |
| 2021 | 76 (23,8) | 78 (23,5) | 73 (20,6) | 73 (11,6) | 47 (35,3) | 71 (12,6) | 71 (12,2) |
| 2022 | 97 (1,4) | 93 (5,2) | 83 (7,7) | 77 (2,6) | 61 (9,6) | 74 (11,4) | 70 (9,2) |
| 2023 | 82 (17,2) | 89 (7,4) | 74 (15,8) | 67 (12,2) | 61 (12,7) | 69 (17,9) | 58 (16,0) |
| 2024 | 68 (31,4) | 61 (34,1) | 73 (16,1) | 63 (16,8) | 50 (33,9) | 60 (29,2) | 45 (38,5) |
| 2025 | 73 (26,9) | 62 (38,9) | 58 (31,4) | 61 (23,7) | 36 (47,6) | 67 (20,7) | 48 (36,2) |

- **Condados + fila 998 = total de estado** en todos los años: 96,2–100,7 % (los mínimos son NE soja
  2017–2019, 96,2–96,8 %, y KS soja 2008–2009, 97,2–97,5 %; el resto, 99–100,7 %). El proceso no pierde
  superficie: lo que falta en los condados es lo que NASS juntó en 998.
- **% del estado que suman los condados publicados, peor año de 2018–2025:** maíz IA 74,4, IL 64,4, IN 75,8,
  OH 81,1, NE 54,1, MN 78,7, KS 48,4; soja IA 68,6, IL 61,1, IN 68,6, OH 76,3, NE 52,4, MN 70,8, KS 61,5.
- Antes de 2018 la fila 998 pesa poco (máximo de 2000–2017: IA ≤ 1,9 %, OH ≤ 3,7, MN ≤ 5,3, IL ≤ 5,6,
  NE ≤ 10,8, IN ≤ 11,3), salvo **KS, que ya desde 2008 junta mucho** (maíz hasta 46,4 % en 2008).
- Los peores años son 2019, 2021 y 2024–2025 (NE 2025: 46,4 % del maíz y 47,6 % de la soja en 998; KS maíz
  2018–2019 y 2025: más de 50 %). 2020 y 2022 vuelven a tener casi todos los condados en IA, IL y OH.
- Ningún condado publicado tiene `(D)` en la superficie sembrada de maíz o soja: los ocultos no aparecen
  como fila propia, van a 998.
- En OH, NE y MN, el número de condados con `sup_sembrada_ac` de maíz y soja de `produccion_anual.csv`
  (release `datos-oh-ne-mn`) coincide con el de Quick Stats en todos los años. IA, IL, IN y KS no tienen
  release de `cultivos` en este repo: sus columnas salen solo de Quick Stats.

## Clases 0, 27 y 58 del CDL (T139, para_decidir #19)

`docs/research/cdl_csb.md` propone grupos propios para tres clases que en `clases_cdl.csv` estaban en `otro`.
Los nombres oficiales son los de los metadatos del CDL que ya tenía la tabla:

| Código | Nombre oficial | Grupo antes | Grupo ahora |
|---|---|---|---|
| 0 | Background | otro | `sin_dato` |
| 27 | Rye | otro | `centeno` |
| 58 | Clover/Wildflowers | otro | `trebol` |

Los grupos también están en `GRUPOS_CDL` de `src/cultivos/process.py`, así no se pierden si `process.py` vuelve a
generar la tabla desde los metadatos. `python -m src.cultivos.clases_extra --escribir` aplica los grupos sin
cambiar nada más: conserva el fin de línea CRLF del archivo y falla si falta un código o si el nombre no coincide.

**Qué cambia en los productos:**
- `rotacion_anual.csv`, máscaras (`mascara_agricola.tif`, `mascara_maiz_<anio>.tif`, `mascara_soja_<anio>.tif`) y
  `rotacion_secuencia.csv`: **nada**. Usan listas de códigos (`AGRICOLA`, `PCT_CLASES`, 1 y 5) o la Cultivated Layer,
  no la columna `grupo`. 27 y 58 ya cuentan como área agrícola (códigos 1–61) y el 0 nunca entró al denominador.
- `lotes` (`cultivo_px_anual.csv` y el resumen anual por lote): **sí**. La columna `cultivo` sale de `grupo`, así
  que los píxeles de centeno o trébol pasan de `otro` a `centeno` o `trebol`, y `cultivo_principal` puede cambiar en
  un lote donde el centeno era mayoría dentro de `otro`. El 0 ya iba vacío. Esta máquina no tiene datos de `lotes`
  para medirlo; hay que volver a correr `src/lotes/process.py` después de unir.

**Efecto medido** con `python -m src.cultivos.clases_extra --efecto data/raw/cultivos/cdl/teselas/*.tif --sumar`:
las 69 teselas del CDL 2017 de KS y NE (198 condados completos, 459 millones de píxeles). Escenarios:
- `actual`: como hoy.
- `A_grupos` (la propuesta): solo cambia `grupo`. Las columnas nuevas `pct_centeno`, `pct_trebol` y
  `frac_pixeles_validos` se calculan aparte y **no** se agregan a `rotacion_anual.csv` sin el OK del humano (es un
  cambio de esquema).
- `B_cobertura` (alternativa): 27 y 58 salen del área agrícola, como cultivos de cobertura o forraje.

Resultados:
- **Clase 0:** ningún píxel dentro de los condados (el fondo solo aparece fuera de EE.UU.). Por eso
  `frac_pixeles_validos` = 1 en los 198 condados, y que el 0 deje de contar como válido no cambia nada.
- **Escenario A:** todos los `pct_*` quedan **idénticos** (diferencia 0 en los 198 condados).
- **Centeno (27):** 0,32 % del área agrícola en KS y 0,16 % en NE (mediana por condado 0,02 %). Llega a 13,3 % en
  Thomas (NE), 9,1 % en Arthur (NE), 7,1 % en Kiowa (KS) y 6,9 % en Stafford (KS): son zonas de Sandhills o de
  trigo, donde el centeno es más forraje que cobertura.
- **Trébol (58):** casi nulo (0,009 % en KS y 0,001 % en NE; máximo por condado 0,4 %).
- **Escenario B:** los `pct_*` suben porque el denominador es menor. La mediana del cambio por columna no pasa de 0,01 puntos;
  el máximo es 4,3 puntos de `pct_maiz` (Arthur, NE, de 42,6 a 46,9 %), 8,1 de `pct_alfalfa` y 3,0 de `pct_trigo`.
  Solo 14 combinaciones de condado y columna `pct_*` cambian más de 1 punto (7 de `pct_maiz`, 4 de `pct_trigo`,
  2 de `pct_alfalfa` y 1 de `pct_barbecho`).

**Supuestos:**
- 2017 es el único año con teselas en esta máquina. El centeno varía de un año a otro y podría pesar más en IA, IL e
  IN, donde se usa como cultivo de cobertura. Para repetir la medición con otro año o estado, correr el comando de
  arriba con sus teselas.
- El CDL clasifica el cultivo principal del año. El centeno de cobertura sembrado en otoño, que se mata antes del
  maíz o la soja, casi nunca aparece como clase 27. Por eso `centeno` en el CDL no mide la práctica de cobertura;
  para eso está `pct_cobertura` del Censo (`practicas_censo.csv`).
