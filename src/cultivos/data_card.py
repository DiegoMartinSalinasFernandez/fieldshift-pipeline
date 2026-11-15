"""Genera docs/datasets/cultivos.md a partir de los CSV procesados (desde, hasta y % de faltantes reales).

Uso: python src/cultivos/data_card.py  (después de process.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.zona_texto import lista_estados  # noqa: E402
from src.cultivos.riego_nass import COLS_DATA_CARD as RIEGO_COLS, SECCION_DATA_CARD as RIEGO_SECCION  # noqa: E402  T134
OUT = REPO / "data" / "processed" / "cultivos"
CARD = REPO / "docs" / "datasets" / "cultivos.md"

QS = "USDA NASS Quick Stats (SURVEY, condado)"
CP = "USDA NASS Quick Stats Crop Progress (SURVEY, estado)"
CE = "USDA NASS Censo Agropecuario (Quick Stats CENSUS)"
D = "Derivada de NASS Quick Stats"
LANID = "LANID (Xie y Lark, Zenodo v3.0; USGS 2018-20)"
CDL = "USDA NASS Cropland Data Layer 30 m (Planetary Computer usda-cdl 2008-2021; CroplandCROS 2022-2025)"

COLS = {
    "produccion_anual.csv": [
        ("sup_sembrada_ac", "Superficie sembrada (AREA PLANTED, todos los usos)", "acres", QS, "Y01"),
        ("sup_cosechada_ac", "Superficie cosechada (AREA HARVESTED; maíz: grano)", "acres", QS, "Y02"),
        ("produccion_bu", "Producción (PRODUCTION en BU; maíz: grano). Alfalfa y heno se miden en toneladas: vacía", "bu", QS, "Y03"),
        ("rend_bu_ac", "Rendimiento (YIELD en BU / ACRE; maíz: grano). Alfalfa y heno: vacía", "bu/ac", QS, "Y04"),
        ("rend_kgha", "rend_bu_ac × factor de config.yaml (bu_ac_a_kgha)", "kg/ha", D, "Y04"),
        ("sup_sembrada_ha", "sup_sembrada_ac × 0,4047 (acres_a_ha)", "ha", D, "Y01"),
        ("ratio_cosechada", "sup_cosechada_ac / sup_sembrada_ac", "fracción", D, "Y05"),
        ("flag_nass", "Código original de NASS cuando el valor está oculto: (D), (Z), (NA)… (separados por ;)", "texto", QS, ""),
    ],
    "fenologia_estado.csv": [
        ("doy_50_sembrado", "Día del año en que se cruza el 50 % sembrado (PCT PLANTED, interpolado)", "día del año", CP, "CT03"),
        ("doy_50_emergido", "Día del año en que se cruza el 50 % emergido (PCT EMERGED)", "día del año", CP, ""),
        ("doy_50_floracion", "Día del año del 50 % en floración (maíz PCT SILKING, soja PCT BLOOMING)", "día del año", CP, "CT05"),
        ("doy_50_cosechado", "Día del año del 50 % cosechado (maíz: grano)", "día del año", CP, "CT04"),
    ],
    "rotacion_anual.csv": [
        ("pct_maiz", "% del área agrícola del condado con maíz (CDL 1)", "%", CDL, "R04"),
        ("pct_soja", "% del área agrícola con soja (CDL 5)", "%", CDL, "R04"),
        ("pct_trigo", "% del área agrícola con trigo de invierno, solo o en doble cultivo con soja (CDL 24 y 26)", "%", CDL, "R04"),
        ("pct_alfalfa", "% del área agrícola con alfalfa (CDL 36)", "%", CDL, "R04"),
        ("pct_heno", "% del área agrícola con otro heno (CDL 37)", "%", CDL, "R04"),
        ("pct_doble_trigo_soja", "% del área agrícola con doble cultivo trigo/soja (CDL 26)", "%", CDL, "R09"),
        ("pct_barbecho", "% del área agrícola en barbecho (CDL 61)", "%", CDL, "R14"),
        ("pct_maiz_tras_soja", "% de los píxeles de maíz del anio que tenían soja en anio−1 (sobre los que en anio−1 tenían clase agrícola)", "%", CDL, "R03"),
        ("pct_maiz_tras_maiz", "% de los píxeles de maíz del anio que tenían maíz en anio−1 (sobre los que en anio−1 tenían clase agrícola)", "%", CDL, "R03"),
        ("pct_soja_tras_maiz", "% de los píxeles de soja del anio que tenían maíz en anio−1 (sobre los que en anio−1 tenían clase agrícola)", "%", CDL, "R03"),
        ("pct_soja_tras_soja", "% de los píxeles de soja del anio que tenían soja en anio−1 (sobre los que en anio−1 tenían clase agrícola)", "%", CDL, "R03"),
    ],
    "rotacion_secuencia.csv": [
        ("pct_maiz_soja_alternado", "% de los píxeles agrícolas los 8 años con maíz y soja alternados todos los años", "%", CDL, ""),
        ("pct_maiz_continuo", "% de los píxeles agrícolas los 8 años con maíz 3 o más años seguidos", "%", CDL, "R13"),
        ("pct_soja_continua", "% de los píxeles agrícolas los 8 años con soja 3 o más años seguidos", "%", CDL, "R13"),
        ("pct_rotacion_trigo", "% de los píxeles agrícolas los 8 años con trigo (solo o en doble cultivo) al menos un año", "%", CDL, ""),
        ("pct_rotacion_alfalfa", "% de los píxeles agrícolas los 8 años con alfalfa (CDL 36) al menos un año", "%", CDL, "R10"),
        ("cultivos_por_anio", "N° de cultivos de la secuencia / 8 años (doble cultivo = 2, barbecho = 0), media de los píxeles", "cultivos/año", CDL, "R05"),
        ("diversidad_shannon", "Índice de Shannon (ln) sobre las clases del CDL de la secuencia de 8 años, media de los píxeles", "índice", CDL, "R11"),
    ],
    "practicas_censo.csv": [
        ("pct_cobertura", "COVER CROP PLANTED, (EXCL CRP) / AG LAND, CROPLAND × 100", "%", CE, ""),
        ("pct_labranza_cero", "CONSERVATION TILLAGE, NO-TILL / AG LAND, CROPLAND × 100", "%", CE, ""),
        ("pct_drenaje_tile", "DRAINED BY TILE / AG LAND, CROPLAND × 100", "%", CE, ""),
        ("pct_riego", "AG LAND, IRRIGATED / AG LAND, CROPLAND × 100", "%", CE, ""),
        ("pct_maiz_regado", "CORN, GRAIN, IRRIGATED / CORN, GRAIN - ACRES HARVESTED × 100", "%", CE, ""),
        ("pct_soja_regada", "SOYBEANS, IRRIGATED / SOYBEANS - ACRES HARVESTED × 100", "%", CE, ""),
        ("pct_cosechado_regado", "AG LAND, CROPLAND, HARVESTED, IRRIGATED / AG LAND, CROPLAND, HARVESTED × 100", "%", CE, ""),
        ("flag_nass", "Valores ocultos de las tres columnas de riego por cultivo: `columna=(D)` separados por `;` (numerador o denominador)", "texto", CE, ""),
    ],
    "riego_anual.csv": [
        ("frac_riego_lanid", "Píxeles agrícolas regados según LANID / píxeles agrícolas con dato", "fracción", LANID, ""),
        ("frac_maiz_regado", "Píxeles de maíz del CDL regados según LANID / con dato", "fracción", LANID, ""),
        ("frac_soja_regada", "Píxeles de soja del CDL regados según LANID / con dato", "fracción", LANID, ""),
        ("frac_pixeles_validos", "Píxeles agrícolas con dato de LANID / píxeles agrícolas", "fracción", LANID, ""),
    ],
}
TIEMPO = {"riego_anual.csv": "anio", "produccion_anual.csv": "anio", "fenologia_estado.csv": "anio", "rotacion_anual.csv": "anio",
          "rotacion_secuencia.csv": "ventana", "practicas_censo.csv": "anio_censo"}

TEXTO = """# Data card — cultivos

Paquete `cultivos` (CLAUDE.md §6.2). Fuente: base completa de USDA NASS Quick Stats
(`https://www.nass.usda.gov/datasets`), archivos `qs.crops_<fecha>.txt.gz` (encuesta y Crop
Progress) y `qs.census<anio>.txt.gz` (Censo Agropecuario), guardados tal cual en
`data/raw/cultivos/nass/`.

- Bajada: `python src/cultivos/download.py` (reanudable, registra en `manifest.csv`).
- Proceso: `python src/cultivos/process.py` (filtra cada archivo a {estados} una vez y guarda
  el filtrado en `data/interim/cultivos/*.filtrado.tsv`).
- Este data card: `python src/cultivos/data_card.py`.

## Columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
{tabla}

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
  heno, barbecho, pastizal; el resto `otro`).

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
  parecían venir de pasto, caminos o bosque: la mediana de los 293 condados de la primera tanda (IA, IL e IN) del % de maíz que
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

## Riego por cultivo del Censo (T132)

- `pct_maiz_regado`, `pct_soja_regada` y `pct_cosechado_regado` de `practicas_censo.csv` salen del Censo
  2012, 2017 y 2022 (`DOMAIN_DESC=TOTAL`, nivel condado), con los `short_desc` de
  `docs/research/censo_agropecuario.md`: numerador `CORN, GRAIN, IRRIGATED - ACRES HARVESTED`,
  `SOYBEANS, IRRIGATED - ACRES HARVESTED` y `AG LAND, CROPLAND, HARVESTED, IRRIGATED - ACRES`; denominador, la
  superficie cosechada total del mismo cultivo (`CORN, GRAIN - ACRES HARVESTED`,
  `SOYBEANS - ACRES HARVESTED`) o de todo el cropland (`AG LAND, CROPLAND, HARVESTED - ACRES`), del mismo
  condado y censo. A diferencia del resto de prácticas, estas tres sí existen por condado en 2012.
- Son superficie **cosechada** regada, no sembrada: el maíz es grano (no incluye silaje).
- Si el numerador o el denominador es `(D)`, `(Z)` u otro código oculto, la celda va vacía y `flag_nass`
  guarda `columna=código` (varias separadas por `;`). `flag_nass` solo cubre estas tres columnas; las
  cuatro anteriores (`pct_cobertura` … `pct_riego`) siguen sin flag, como antes.
- Un condado sin fila de riego por cultivo queda vacío y sin flag: no se asume 0. En OH, MN, IA, IL e IN
  faltan muchos condados (poco riego; ver research), en NE y KS casi todos tienen dato.
- Porcentajes fuera de 0-100 (numerador mayor que el total) quedan vacíos, igual que las otras columnas.
"""


def main():
    filas = []
    for archivo, cols in COLS.items():
        ruta = OUT / archivo
        if not ruta.exists():
            continue
        df = pd.read_csv(ruta, dtype={"fips": str, "fips_estado": str, "flag_nass": str})
        t = df[TIEMPO[archivo]].astype(str)
        if archivo == "produccion_anual.csv":  # T134: riego y secano, solo si el CSV ya las tiene
            cols = cols + [c for c in RIEGO_COLS if c[0] in df.columns]
        for nombre, desc, unidad, fuente, cid in cols:
            s = df[nombre]
            falt = 100 * s.isna().mean()
            llenos = t[s.notna()]
            desde = llenos.min() if len(llenos) else ""
            hasta = llenos.max() if len(llenos) else ""
            filas.append(f"| {archivo} | {nombre} | {desc} | {unidad} | {fuente} | {cid} | {desde} | {hasta} | {falt:.1f} |")
    CARD.parent.mkdir(parents=True, exist_ok=True)
    texto = TEXTO.replace("{tabla}", "\n".join(filas)).replace("{estados}", lista_estados())
    texto = texto.rstrip("\n") + "\n" + RIEGO_SECCION  # T134: sección de riego al final
    CARD.write_text(texto, encoding="utf-8", newline="\n")
    print(f"escrito {CARD.relative_to(REPO).as_posix()} ({len(filas)} columnas)")


if __name__ == "__main__":
    main()
