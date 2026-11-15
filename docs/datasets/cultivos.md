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
| produccion_anual.csv | fila_nass | 1 = la fila viene de NASS; 0 = NASS no publicó ese condado, año y cultivo y la fila se completó vacía (T138) | 0/1 | Derivada de NASS Quick Stats |  | 2000 | 2025 | 0.0 |
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

## Riego desde LANID (`riego_anual.csv`, T127)

Fuente: **LANID** (Landsat-based Irrigation Dataset; Xie, Gibbs y Lark), mapas binarios de riego de
30 m para todo EE.UU. (1 = regado, 0 = no regado, según `Metadata.docx`):
- versión 3.0 de Zenodo (DOI 10.5281/zenodo.5548555, CC BY 4.0): `lanid1997-2003.zip`,
  `lanid2004-2010.zip`, `lanid2011-2017.zip` (un `lanidYYYY.tif` por año) e `irrFreqAndChange.zip`
  (`maxIrrExt`: regado al menos una vez en 1997–2017), ~1,7 GB;
- extensión del USGS (Martin y Brandt, 2024, DOI 10.5066/P9YWR0OJ): `lanid2018.tif`, `lanid2019.tif`,
  `lanid2020.tif` y `maxIrrExt_0020.tif`, en ScienceBase. ScienceBase responde con un desafío de
  Cloudflare a los clientes automáticos: si `riego.py bajar` no los puede bajar, avisa y sigue; se
  bajan a mano a `data/raw/cultivos/lanid/` y se registran con `riego.py registrar`.

Bajada y proceso: `python src/cultivos/riego.py bajar` y `python src/cultivos/riego.py procesar`
(necesita `data/reference/mascara_agricola.tif`, `condados.gpkg` y, para maíz y soja, las máscaras
`mascara_maiz_<anio>.tif` / `mascara_soja_<anio>.tif` de `process.py`). Research:
`docs/research/riego_mascaras.md` (T018) y `docs/research/riego_ne_ks.md`.

| columna | descripcion | unidad | fuente |
|---|---|---|---|
| `frac_riego_lanid` | píxeles agrícolas (`mascara_agricola.tif`) regados según LANID del `anio` / píxeles agrícolas con dato de LANID | fracción 0–1 | LANID |
| `frac_maiz_regado` | lo mismo dentro de `mascara_maiz_<anio>.tif` (maíz del CDL de ese año); vacío si no hay máscara de ese año o el condado no tiene maíz | fracción 0–1 | LANID + CDL |
| `frac_soja_regada` | lo mismo dentro de `mascara_soja_<anio>.tif` | fracción 0–1 | LANID + CDL |
| `frac_pixeles_validos` | píxeles agrícolas con dato de LANID / píxeles agrícolas del condado | fracción 0–1 | LANID |

Además: `data/reference/mascara_riego_max.tif` (1 bit, grilla de `mascara_agricola.tif`): 1 = regado
al menos una vez según `maxIrrExt_0020` (2000–2020) o, si no está, `maxIrrExt` (1997–2017). Es para
que `vegetacion` calcule `ndvi_secano` en otra tarea.

Supuestos:
- LANID se lleva a la grilla de `mascara_agricola.tif` (EPSG:5070, 30 m) con vecino más cercano;
  si ya está alineado, es una copia. LANID se usa tal cual, sin recalibrarlo contra NASS.
- En LANID el 0 es "no regado": si el TIF declara `nodata = 0`, no se respeta. Fuera de la extensión
  del raster el píxel no es válido (baja `frac_pixeles_validos`).
- Solo hay filas para los años que cubre LANID (2000–2017 con Zenodo; 2000–2020 si están los TIF
  del USGS). Después no hay producto anual: las filas no existen (no son "sin riego"). Para
  2021–2025 quedan el Censo 2022 (`pct_riego` de `practicas_censo.csv`) o la máscara máxima; lo
  decide ML.
- `frac_maiz_regado` y `frac_soja_regada` solo existen desde que hay CDL (2008).
- Condados sin píxeles agrícolas: sin fila.
- La máscara máxima como proxy del riego después de 2020 es un supuesto: los pivotes nuevos quedan
  como secano.

Problemas conocidos:
- En el oeste LANID fijó sus umbrales de entrenamiento con el área regada del Censo por condado:
  comparar con el Censo no es un control independiente allí. El control independiente es la
  superficie sembrada `IRRIGATED / ALL` de NASS por cultivo (2000–2018, NE y KS).
- `pct_riego` del Censo usa como denominador `AG LAND, CROPLAND` (incluye pasturas en rotación) y
  como numerador toda la tierra regada (incluye pasturas regadas); `frac_riego_lanid` usa la
  máscara agrícola del CDL. No son iguales por definición.
- **Prueba en Nebraska 2017** (T127; recorte con una máscara agrícola provisoria hecha con las
  clases agrícolas del CDL 2017, no con la Cultivated Layer; 93 condados, 2011–2017 en 37 s):
  - `frac_maiz_regado` contra NASS: encuesta, maíz sembrado `IRRIGATED / ALL`, n = 49, r = 0,973,
    sesgo −0,05 y MAE 0,06; Censo 2017, maíz grano cosechado `IRRIGATED / ALL`, n = 87, r = 0,970,
    sesgo −0,03 y MAE 0,05.
  - `frac_soja_regada` **sobreestima**: contra la encuesta (n = 22) r = 0,92 pero sesgo +0,20; contra
    el Censo 2017 (n = 77) r = 0,92 y sesgo +0,16 (mediana 0,81 contra 0,54). Ordena bien los
    condados, pero el nivel de la soja regada de LANID no es confiable. No se corrigió: ML decide
    si usarla.
  - `frac_riego_lanid`: mediana de los condados 0,49 (2012) a 0,60 (2015); `frac_pixeles_validos` = 1
    en todos (LANID cubre todo el estado y no declara nodata).
- La grilla de LANID está alineada con la del CDL (EPSG:5070, 30 m; origen −2354955, 3165615, a un
  número entero de píxeles del origen del CDL), así que el vecino más cercano no mueve píxeles.
- **Prueba completa con Zenodo en NE** (2000–2017, 93 condados, 1674 filas): mediana de
  `frac_riego_lanid` entre 0,44 (2002) y 0,60 (2015). `mascara_riego_max.tif` (`maxIrrExt` 1997–2017)
  se arma en 6 s: marca el 73 % de los píxeles agrícolas de NE como regados alguna vez (es el máximo de
  21 años, no un año típico), y el 15 % de sus píxeles regados cae fuera de la máscara agrícola
  (pasturas y heno regados del oeste). La máscara cubre todo el rectángulo de la grilla, también
  fuera de los condados: hay que cruzarla con `mascara_agricola.tif` al usarla.

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

## Riego por cultivo del Censo (T132)

Tres columnas nuevas en `practicas_censo.csv`, después de `pct_riego` (las existentes no cambian), del Censo
2012, 2017 y 2022 (`DOMAIN_DESC=TOTAL`, nivel condado), con los `short_desc` de
`docs/research/censo_agropecuario.md`. Esquema nuevo: espera el OK de `coordinacion/para_decidir.md` #2.

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct (NE+KS) |
|---|---|---|---|---|---|---|---|---|
| practicas_censo.csv | pct_maiz_regado | CORN, GRAIN, IRRIGATED / CORN, GRAIN - ACRES HARVESTED × 100 | % | USDA NASS Censo Agropecuario (Quick Stats CENSUS) |  | 2012 | 2022 | 13.3 |
| practicas_censo.csv | pct_soja_regada | SOYBEANS, IRRIGATED / SOYBEANS - ACRES HARVESTED × 100 | % | USDA NASS Censo Agropecuario (Quick Stats CENSUS) |  | 2012 | 2022 | 24.2 |
| practicas_censo.csv | pct_cosechado_regado | AG LAND, CROPLAND, HARVESTED, IRRIGATED / AG LAND, CROPLAND, HARVESTED × 100 | % | USDA NASS Censo Agropecuario (Quick Stats CENSUS) |  | 2012 | 2022 | 23.9 |
| practicas_censo.csv | flag_nass | Valores ocultos de las tres columnas de riego por cultivo: `columna=(D)` separados por `;` (numerador o denominador) | texto | USDA NASS Censo Agropecuario (Quick Stats CENSUS) |  |  |  |  |

**Supuestos**

- Superficie **cosechada** regada sobre cosechada total del mismo cultivo y condado; el maíz es grano (sin
  silaje). `pct_cosechado_regado` es sobre todo el cropland cosechado. A diferencia de cobertura, labranza
  cero y tile, estas tres columnas sí existen por condado en 2012.
- Si el numerador o el denominador es `(D)`, `(Z)` u otro código oculto, la celda va vacía y `flag_nass`
  guarda `columna=código`. `flag_nass` solo cubre estas tres columnas; las cuatro anteriores siguen sin flag.
- Condado sin fila: vacío y sin flag (no se asume 0). Porcentajes fuera de 0-100: vacíos (no hubo ninguno en
  NE y KS).

**Cobertura en NE y KS** (corrida del 2026-11-15; condados con valor y, entre paréntesis, mediana en %):

| estado | censo | `pct_riego` | `pct_maiz_regado` | `pct_soja_regada` | `pct_cosechado_regado` |
|---|---|---|---|---|---|
| NE (93) | 2012 | 93 (35,3) | 86 (60,5) | 72 (60,4) | 75 (45,6) |
|  | 2017 | 93 (35,2) | 87 (53,0) | 77 (54,1) | 74 (45,2) |
|  | 2022 | 93 (33,3) | 88 (52,5) | 81 (50,8) | 77 (45,5) |
| KS (105) | 2012 | 100 (4,1) | 85 (31,3) | 77 (16,2) | 75 (5,5) |
|  | 2017 | 100 (3,3) | 87 (19,5) | 71 (12,1) | 81 (5,0) |
|  | 2022 | 99 (3,7) | 82 (15,3) | 72 (9,6) | 70 (5,1) |

- Celdas con flag, por columna (NE 2012/2017/2022; KS 2012/2017/2022): maíz 5/5/4 y 11/7/16; soja 13/10/7 y
  18/21/21; cosechado 18/19/16 y 30/24/34. El resto de los vacíos son condados sin fila.
- `pct_riego` (sobre todo el cropland) subestima el peso del riego en maíz y soja: en KS la mediana es 3-4 %,
  pero la del maíz regado es 15-31 %. En OH, MN, IA, IL e IN se esperan muchas celdas vacías (poco riego).
- Pendiente: `loop/spec/entregables.yaml` no tiene todavía los rangos de las tres columnas (no se toca sin OK).
## Tabla de referencia: precisión del CDL (`data/reference/cdl_precision.csv`)

Agregada en T133 (para_decidir #13). No es un CSV procesado ni entra en `tabla_anual.csv`: es una tabla de
referencia para ML, en `data/reference/` y en el zip de base de cada release (`<release>_base.zip`, solo las
filas de los estados del release; la suma `scripts/entregar.py` si el archivo existe).

**Qué es.** La precisión del Cropland Data Layer publicada por NASS para cada estado, año y clase: de los
píxeles de validación de la FSA, cuántos acierta el CDL. Una fila por `fips_estado, anio, clase_cdl`.

**De dónde sale.** `python -X utf8 src/cultivos/precision_cdl.py` junta los CSV que ya armaron los extractores
de research (`docs/research/cdl_precision*_extraer.py`, T024, T064, T068 y T078) a partir de las fuentes
oficiales: los metadatos FGDC de cada estado y año en HTML (2008–2023, tabla "STATEWIDE AGRICULTURAL ACCURACY
REPORT") y `CDL_<año>_accuracy_assessments.zip` (2024–2025, hoja "Summary Table" del xlsx de cada estado).
Con `--rehacer <dir>` vuelve a correr los extractores antes (baja de NASS a `<dir>`, fuera del repo). El script
solo renombra columnas, agrega `fips_estado` y `metodo_validacion`, y corta si hay claves repetidas o
porcentajes fuera de 0–100. Detalle y lectura de los valores: `docs/research/cdl_precision.md`,
`cdl_precision_mo_wi_sd.md`, `cdl_precision_mi_nd.md` y `cdl_precision_ky.md`.

**Cobertura.** 13 estados (los 7 del proyecto más MO, WI, SD, MI, ND y KY), 2008–2025, 1.962 filas. Clases:
maíz (1), soja (5), trigo de invierno (24), avena (28), alfalfa (36) y otro heno (37) en los 13; además doble
trigo/soja (26), barbecho (61), pastura/pasto (62) y pastizal/pastura (176) en MO, WI, SD, MI, ND y KY;
girasol (6), trigo de primavera (23) y canola (31) en MI y ND; tabaco (11) en KY. En OH, NE, MN y KS, maíz y
soja tienen precisión del productor de 85,8 a 99,1 % y del usuario de 87,2 a 98,8 % en todos los años.

| Columna | Descripción | Unidad | Nombre en la fuente / en research |
|---|---|---|---|
| `fips_estado` | Código FIPS del estado, 2 dígitos | — | (se agrega desde `estado`) |
| `anio` | Año del CDL | — | `anio` |
| `clase_cdl` | Código de la clase del CDL (ver `data/reference/clases_cdl.csv`) | — | "Attribute Code" / `codigo_cdl` |
| `estado` | Estado, 2 letras | — | `estado` |
| `nombre` | Nombre corto de la clase que usó research | — | `cultivo` |
| `exactitud_productor_pct` | Precisión del productor = 100 − error de omisión: de los píxeles que son esa clase en el terreno, % que el CDL acierta | % | "Producer's Accuracy" / `precision_productor_pct` |
| `exactitud_usuario_pct` | Precisión del usuario = 100 − error de comisión: de los píxeles que el CDL marca con esa clase, % que lo son | % | "User's Accuracy" / `precision_usuario_pct` |
| `px_correctos_validacion` | Píxeles de validación bien clasificados (da una idea del tamaño de la muestra) | píxeles | "*Correct Pixels" / `px_correctos` |
| `exactitud_global_cultivos_fsa_pct` | Precisión global de las clases de cultivo de la FSA en ese estado y año (igual en todas las clases) | % | "OVERALL ACCURACY" o "FSA Crops" / `global_cultivos_fsa_pct` |
| `kappa_global_cultivos_fsa` | Kappa de esa precisión global | — | "Kappa" / `kappa_global_fsa` |
| `metodo_validacion` | `buffer_30m` (2008–2016), `sin_buffer` (2017–2023) o `muestreo_2024` (2024–2025) | — | (de `cdl_precision.md`, sección 2) |
| `fuente` | `metadatos_fgdc_html` o `accuracy_assessments_xlsx` | — | `fuente` |

**Faltantes.** Celda vacía cuando la clase no tiene fila en la tabla de NASS de ese estado y año (por ejemplo
pastizal/pastura antes de 2023), o cuando NASS publica "n/a" en la precisión del usuario (clase que el CDL no
asignó nunca). En toda la tabla: 11,9 % vacía la precisión del productor, 12,5 % la del usuario y 11,1 % los
píxeles correctos; casi todo en las clases menores de los 6 estados de research que no son del proyecto. Nunca
se rellena con 0.

**Cómo la usaría ML.**
- Ponderar o filtrar las transiciones de `rotacion_anual.csv` (`pct_maiz_tras_soja`, etc.) por la confiabilidad
  del par de años: una transición entre dos CDL arrastra el error de los dos, así que un peso posible es el
  producto de las precisiones de la clase en `anio − 1` y en `anio` (decisión de ML, no de este repo).
- Saber qué clases no sirven para rotaciones en cada estado (por ejemplo trigo de invierno en IA y MN, avena y
  otro heno en casi todos lados, otro heno en 2024–2025 con precisión del usuario muy baja).
- Como covariable o para estratificar la validación por año, sabiendo que `metodo_validacion` marca cortes:
  **no comparar la precisión entre cortes** (la caída de 2016 a 2017 es un cambio de método, no un CDL peor).

**Supuestos.**
- Los códigos FIPS de los 6 estados fuera del proyecto (MO 29, WI 55, SD 46, MI 26, ND 38, KY 21) están fijos
  en `src/cultivos/precision_cdl.py`, porque `config/config.yaml` solo trae los 7 del proyecto.
- Se supone, como research, que la tabla del HTML de 2016 es la versión con buffer (ver `cdl_precision.md`).
- La tabla mezcla CDL de 30 m (hasta 2023) y la evaluación de 2024–2025 publicada con el CDL de 10 m; research
  no separó si la de 2024–2025 corresponde a la versión de 10 m o a la de 30 m.
## Riego y secano (T134, propuesta 1 de `para_decidir.md`)

Columnas agregadas al final de `produccion_anual.csv` por `src/cultivos/riego_nass.py`
(research: `docs/research/riego_nass.md`). Las columnas anteriores no cambian.

- **Fuente:** la misma encuesta de condado de Quick Stats (`SOURCE_DESC=SURVEY`, `DOMAIN_DESC=TOTAL`,
  `FREQ_DESC=ANNUAL`, `REFERENCE_PERIOD_DESC=YEAR`), con `PRODN_PRACTICE_DESC` = `IRRIGATED` (riego) y
  `NON-IRRIGATED` (secano). Mismos `CLASS_DESC` y `UTIL_PRACTICE_DESC` que las columnas totales (maíz: grano
  para cosechada, producción y rendimiento; sembrada con todos los usos).
- **Cultivos:** maíz, soja y trigo de invierno. Avena, alfalfa y heno quedan vacíos (avena no tiene dato por
  práctica en NE ni KS; alfalfa está en toneladas y solo hasta 2009).
- **Cobertura esperada:** NE y KS, 2000–2018 (trigo de invierno hasta 2019). Desde la cosecha 2019 NASS
  dejó de publicar estimaciones de condado por práctica (Federal Register 2019-24789). En los otros cinco
  estados todo queda vacío. En KS la serie es despareja desde 2008 y la soja no tiene dato en 2010–2013 ni
  2017–2018.

### Supuestos

- **Vacío no es "sin riego":** quiere decir que NASS no lo publicó para ese condado o lo juntó en
  "OTHER (COMBINED) COUNTIES" (`county_code` 998, que se descarta como en el resto del paquete).
- **Secano = `NON-IRRIGATED`.** Las subdivisiones del trigo (`NON-IRRIGATED, CONTINUOUS CROP`,
  `NON-IRRIGATED, FOLLOWING SUMMER FALLOW`, 2000–2008) no se usan.
- `pct_sembrada_riego` usa como denominador `sup_sembrada_ac` (ALL PRODUCTION PRACTICES) y queda vacío si
  falta alguno de los dos o el total es 0.
- `flag_nass` no cambia: los códigos ocultos de las columnas por práctica van en `flag_nass_riego`. En la
  encuesta de NE y KS el research no encontró ningún `(D)`, así que se espera vacía.
- Un dato por práctica sin fila de ALL PRODUCTION PRACTICES para el mismo condado, año y cultivo no se
  agrega (el archivo no suma filas).

### Problemas conocidos

- Comparar `rend_bu_ac` de NE y KS con el de IA, IL o IN mezcla riego y secano; desde 2019 solo queda el
  Censo (superficie cosechada con riego, sin rendimiento; propuesta 2 de `para_decidir.md`).
- La muestra de 2008–2018 está sesgada hacia los condados que siguieron publicando por práctica.
- **Rendimientos de secano muy bajos o 0:** NASS publica `0` en el secano de algunos condados del oeste en
  sequías (maíz: NE Dawes, Loup, Garfield, Morrill 2002, Dawes y Cherry 2004, Dawes, Blaine y Rock 2007; KS Clark 2000; soja:
  KS Harper 2002, Gray 2003, Rooks 2002) y maíz de secano entre 7 y 19 bu/ac en 2002 y 2012. Son valores
  publicados (pérdida casi total), no faltantes: quedan como vienen. Están por debajo del rango de
  `validar_csv()` para el maíz (20–300), que hoy solo mira `rend_bu_ac`.
- Control de coherencia: `chequear_coherencia()` lista las filas donde riego + secano se aleja más de 1 %
  de la superficie sembrada total (el research dio 0 casos).
## Fenología de avena y trigo de invierno (T135)

Pendiente del OK de `coordinacion/para_decidir.md` #8. Código: `src/cultivos/fenologia.py`.

- `fenologia_estado.csv` suma las filas `cultivo = avena` (`OATS`; Crop Progress la informa en
  OH, NE y MN, y en IA/IL/IN si viene en el archivo) y `cultivo = trigo_invierno` (`WHEAT` /
  `CLASS_DESC=WINTER`; OH, NE y KS, no MN). Etapas: PLANTED, EMERGED, HEADED y HARVESTED, todas
  con `UTIL_PRACTICE_DESC=ALL UTILIZATION PRACTICES` (supuesto: no se pudo mirar el archivo crudo
  al escribir el código; si alguna etapa no aparece, revisar ese filtro).
- Las filas y columnas de maíz y soja no cambian. Se agregan cuatro columnas al final, vacías
  donde no corresponden:
  - `doy_50_espigado`: 50 % espigado (HEADED) de avena y trigo. Para ellos `doy_50_floracion`
    queda vacía (las dos etapas no son lo mismo).
  - `doy_50_sembrado_otono` y `doy_50_emergido_otono`: solo trigo de invierno.
  - `flag_hueco_50`: ver abajo.
- **Año del trigo de invierno**: `anio` es el año de la **cosecha**, como en el resto del
  proyecto. Las semanas de siembra y emergencia con `WEEK_ENDING` de agosto a diciembre van al
  `anio` siguiente; sus días se guardan como día del año calendario del otoño (de `anio − 1`)
  en las columnas `_otono`, para no mezclarlos con días de primavera ni usar días negativos
  (el rango 1–366 y la coherencia sembrado ≤ emergido ≤ floración ≤ cosechado del spec siguen
  valiendo). Para el trigo, `doy_50_sembrado` y `doy_50_emergido` quedan vacías. El año se
  toma de `WEEK_ENDING` y no de `YEAR`, porque no se verificó qué `YEAR` pone Quick Stats a las
  filas de otoño. La siembra del otoño de 2025 (cosecha 2026) queda fuera del período.
- **`flag_hueco_50`**: lista de etapas (`sembrado`, `emergido`, `floracion`, `cosechado`,
  `espigado`, `sembrado_otono`, `emergido_otono`, separadas por `;`) cuyo cruce del 50 % se
  interpoló entre dos semanas con dato separadas por más de 14 días. Las semanas `(NA)` cuentan
  como faltantes. Caso conocido: el cierre del gobierno federal de 2025, sin reportes de las
  semanas del 5 de octubre al 9 de noviembre (cosecha de maíz y soja, siembra y emergencia del
  trigo para 2026). Si el 50 % cae justo en una semana con dato, no se marca. Vacía si ninguna.
- Avena de Nebraska: algunos años el primer reporte ya supera el 50 % (siembra y cosecha), y la
  celda queda vacía, igual que en maíz y soja.
- Fuente de las etapas por estado: `docs/research/crop_progress_estados_nuevos.md` (T019).

Columnas nuevas de `fenologia_estado.csv` (cobertura y faltantes: se completan al regenerar este
data card con `python src/cultivos/data_card.py` después de correr `process.py`):

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| fenologia_estado.csv | doy_50_espigado | Avena y trigo de invierno: día del año del 50 % espigado (PCT HEADED) | día del año | USDA NASS Quick Stats Crop Progress (SURVEY, estado) |  |  |  |  |
| fenologia_estado.csv | doy_50_sembrado_otono | Trigo de invierno: día del año (de anio − 1) del 50 % sembrado en otoño | día del año | USDA NASS Quick Stats Crop Progress (SURVEY, estado) |  |  |  |  |
| fenologia_estado.csv | doy_50_emergido_otono | Trigo de invierno: día del año (de anio − 1) del 50 % emergido en otoño | día del año | USDA NASS Quick Stats Crop Progress (SURVEY, estado) |  |  |  |  |
| fenologia_estado.csv | flag_hueco_50 | Etapas (separadas por ;) cuyo 50 % se interpoló entre semanas separadas por más de 14 días | texto | Derivada de NASS Quick Stats |  |  |  |  |
## Sorgo granífero como clase de rotación en Kansas (T137, retenido hasta el OK de `para_decidir` #11)

Código en `src/cultivos/sorgo.py`; se corre después de `process.py`
(`.venv/bin/python -X utf8 src/cultivos/sorgo.py`). Agrega columnas **al final** de `rotacion_anual.csv` y
`rotacion_secuencia.csv`; las columnas que ya existen no cambian. El sorgo **no** entra en
`produccion_anual.csv` (`docs/research/sorgo.md`: NASS publica su rendimiento en pocos condados de Kansas).
Solo se calcula para los condados de Kansas (FIPS 20); en los demás estados las columnas quedan vacías y, si la
máquina no tiene Kansas, el script no hace nada. Si las columnas ya están, se reemplazan (idempotente).

| Archivo | Columna | Descripción | Unidad | Fuente | ID catálogo |
|---|---|---|---|---|---|
| rotacion_anual.csv | pct_sorgo | % del área agrícola del condado con sorgo, solo o en doble cultivo con trigo de invierno (CDL 4 y 236) | % | USDA NASS Cropland Data Layer 30 m | R04 |
| rotacion_anual.csv | pct_doble_trigo_sorgo | % del área agrícola con doble cultivo trigo de invierno/sorgo (CDL 236) | % | Cropland Data Layer | R09 |
| rotacion_anual.csv | pct_sorgo_tras_trigo | % de los píxeles de sorgo (4, 236) del anio que tenían trigo de invierno (24, 26) en anio−1 | % | Cropland Data Layer | R03 |
| rotacion_anual.csv | pct_sorgo_tras_sorgo | % de los píxeles de sorgo del anio que tenían sorgo en anio−1 | % | Cropland Data Layer | R03 |
| rotacion_anual.csv | pct_barbecho_tras_sorgo | % de los píxeles de barbecho (61) del anio que tenían sorgo en anio−1 | % | Cropland Data Layer | R03 |
| rotacion_anual.csv | pct_trigo_tras_barbecho | % de los píxeles de trigo de invierno (24, 26) del anio que tenían barbecho en anio−1 | % | Cropland Data Layer | R03 |
| rotacion_secuencia.csv | pct_trigo_sorgo_barbecho | % de los píxeles agrícolas en los 8 años de la ventana con la secuencia trigo–sorgo–barbecho en tres años seguidos al menos una vez | % | Cropland Data Layer | R13 |
| rotacion_secuencia.csv | pct_rotacion_sorgo | % de los píxeles agrícolas en los 8 años de la ventana con sorgo en algún año | % | Cropland Data Layer | R13 |

Los IDs del catálogo son los de las columnas parecidas de maíz y soja (R03 transiciones, R04 % por cultivo,
R09 doble cultivo, R13 secuencia); el catálogo no tiene IDs propios del sorgo.

**Supuestos**
- Sorgo = CDL 4 (Sorghum) y 236 (Dbl Crop WinWht/Sorghum). Trigo = 24 y 26, como `pct_trigo`: el 236 no cuenta
  como trigo, así que `pct_trigo` no cambia y un 236 seguido de sorgo cuenta como sorgo tras sorgo. No se usan
  234 (durum/sorgo) ni 235 (cebada/sorgo): no son trigo de invierno.
- Denominador de las transiciones: píxeles de la clase del año actual que en anio−1 tenían una clase agrícola
  (incluye el barbecho 61), igual que las transiciones maíz–soja. Sin píxeles en el denominador, celda vacía.
- Primer año completo de la serie: transiciones vacías (no hay año anterior).
- La secuencia trigo–sorgo–barbecho se busca en años calendario del CDL: el trigo se cosecha en julio del año
  t, el sorgo se siembra en junio de t+1 y el barbecho dura hasta la siembra del trigo en septiembre de t+2,
  así que la secuencia esperada es 24 → 4 → 61 en tres CDL seguidos.

**Problemas conocidos**
- Precisión del sorgo en el CDL de Kansas: 76–84 % del productor y 82–86 % del usuario (2021–2023), unos
  8 puntos menos que maíz, soja y trigo; el 236 tiene 32 % y 57 % en 2023 (`docs/research/sorgo.md`).
- En los años de transición entre CDL de 30 m y de 10 m remuestreado (2024) puede haber más cambios de clase
  en bordes de lote: lo absorbe el denominador agrícola, como en las demás transiciones.

**Prueba con un recorte real de Kansas** (2026-11-15): 4 teselas de 90 km del CDL 2010–2021 de Planetary
Computer, bajadas fuera del repo, con Greeley (20071), Hamilton (20075), Wallace (20199) y Wichita (20203),
oeste de Kansas. Corrió en 20 s. Medias 2010–2021: `pct_sorgo` 11–15 %, `pct_sorgo_tras_trigo` 45–78 %,
`pct_trigo_tras_barbecho` 72–82 %; `pct_trigo_sorgo_barbecho` 21–49 % según condado y ventana (Greeley
38–45 %). Muestra la rotación de secano trigo–sorgo–barbecho que describe el research. No se corrió sobre todo
Kansas: esta máquina solo tiene el CDL 2017 en `data/raw/`.
## Grilla completa de `produccion_anual.csv` (T138)

> Retenido hasta el OK del humano a la fila 7 de `coordinacion/para_decidir.md`.

- `produccion_anual.csv` tiene **una fila por cada `fips` de `condados.csv` × `anio` del período ×
  cultivo de `config.yaml`** (`src/cultivos/grilla.py`, llamado desde `process.py`). Donde NASS no publica
  el condado (lo suma a "OTHER (COMBINED) COUNTIES", ver la sección de cobertura), la fila va con todas las
  variables vacías. No se rellena nada: una celda vacía es "NASS no publicó", nunca un 0.
- **`fila_nass`** (última columna): 1 si la fila viene de NASS (tiene al menos una variable o un
  `flag_nass`), 0 si se completó. `flag_nass` y el resto de las columnas no cambian.
- Se completan también los cultivos que NASS no estima en todo un estado (por ejemplo trigo de invierno en
  Minnesota e Iowa, ningún año): quedan como filas con `fila_nass` = 0.
- Para entrenar con el rendimiento, filtrar `rend_bu_ac` no vacío (como antes). Para saber qué falta,
  filtrar `fila_nass` = 0. Las filas completadas no tienen dato del cultivo: no sirven para saber si el
  condado lo sembró (para eso está `rotacion_anual.csv`).
- `src/merge.py` arma `tabla_anual.csv` con las filas de `produccion_anual.csv`: con la grilla, la tabla
  unida también tiene una fila por condado × año × cultivo.
- Sobre un `produccion_anual.csv` ya hecho (por ejemplo, el de un release) se corre solo la grilla, que
  reescribe el archivo y es idempotente:
  `FIELDSHIFT_ESTADOS=OH,NE,MN .venv/bin/python -X utf8 src/cultivos/grilla.py <csv> --condados <condados.csv>`.
- Con el release `datos-oh-ne-mn` (268 condados, 26 años, 6 cultivos): de 23.016 filas pasa a 41.808
  (18.792 completadas: OH 6.893, NE 5.786, MN 6.113). Por año, las completadas van de 439 (2013) a 1.248
  (2024). `validar_csv()` pasa sin errores.
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
