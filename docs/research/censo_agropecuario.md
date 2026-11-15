# Censo Agropecuario: short_desc de prácticas por condado (2012, 2017, 2022)

Pregunta: Censo Agropecuario: short_desc de cultivos de cobertura, labranza cero, drenaje con caños y riego por condado (2012, 2017, 2022).

Respuesta corta: En Quick Stats (`source_desc=CENSUS`, `sector_desc=ECONOMICS`, `group_desc=FARMS & LAND & ASSETS`, `agg_level_desc=COUNTY`, `domain_desc=TOTAL`) los cuatro `short_desc` son: cultivos de cobertura `PRACTICES, LAND USE, CROPLAND, COVER CROP PLANTED, (EXCL CRP) - ACRES`; labranza cero `PRACTICES, LAND USE, CROPLAND, CONSERVATION TILLAGE, NO-TILL - ACRES`; drenaje con caños `PRACTICES, LAND USE, DRAINED BY TILE - ACRES`; riego `AG LAND, IRRIGATED - ACRES`. El denominador natural para los porcentajes es `AG LAND, CROPLAND - ACRES`. Los cuatro están por condado para 2017 y 2022 en los 293 condados de IA, IL e IN. **Para 2012, Quick Stats solo trae por condado el riego y el cropland**: las tres prácticas de 2012 están solo a nivel nacional y estatal. Los valores de condado de 2012 sí están publicados en la Tabla 41 ("Land Use Practices: 2017 and 2012") del informe del Censo 2017 por condado (PDF por estado). Las preguntas de cobertura, labranza y tile se hicieron en 2012, 2017 y 2022.

Detalle:

**Cómo se verificó.** Los nombres salen de escanear los archivos completos de Quick Stats del censo que ya bajó el paquete `cultivos` (`data/raw/cultivos/nass/qs.census2012.txt.gz`, `qs.census2017.txt.gz`, `qs.census2022.txt.gz`, de `https://www.nass.usda.gov/sites/default/files/datasets/`), filtrando condados de IA, IL e IN con `DOMAIN_DESC = TOTAL`. Estos archivos pesan 111–309 MB y no sirven como cita verificable: las citas de abajo son de páginas HTML/PDF que describen las mismas preguntas del censo.

**Campos que forman cada `short_desc`** (fila de 2022; `short_desc` es la concatenación de `commodity_desc`, `class_desc`, `prodn_practice_desc`, `util_practice_desc`, `statisticcat_desc` y `unit_desc`, ver research `nass_quickstats`):

| Práctica | `commodity_desc` | `class_desc` | `prodn_practice_desc` | `statisticcat_desc` / `unit_desc` | `short_desc` |
|---|---|---|---|---|---|
| Cultivos de cobertura | PRACTICES | LAND USE, CROPLAND | COVER CROP PLANTED, (EXCL CRP) | AREA / ACRES | `PRACTICES, LAND USE, CROPLAND, COVER CROP PLANTED, (EXCL CRP) - ACRES` |
| Labranza cero | PRACTICES | LAND USE, CROPLAND | CONSERVATION TILLAGE, NO-TILL | AREA / ACRES | `PRACTICES, LAND USE, CROPLAND, CONSERVATION TILLAGE, NO-TILL - ACRES` |
| Drenaje con caños (tile) | PRACTICES | LAND USE | DRAINED BY TILE | AREA / ACRES | `PRACTICES, LAND USE, DRAINED BY TILE - ACRES` |
| Riego | AG LAND | IRRIGATED | — | AREA / ACRES | `AG LAND, IRRIGATED - ACRES` |
| Denominador | AG LAND | CROPLAND | — | AREA / ACRES | `AG LAND, CROPLAND - ACRES` |

Variantes que también existen por condado en 2017 y 2022 (útiles si el equipo las quiere): `... - AREA, MEASURED IN ACRES / OPERATION` y `... - NUMBER OF OPERATIONS` para cada práctica; `PRACTICES, LAND USE, CROPLAND, CONSERVATION TILLAGE, (EXCL NO-TILL) - ACRES` (labranza reducida); `PRACTICES, LAND USE, CROPLAND, CONVENTIONAL TILLAGE - ACRES` (labranza intensiva); `PRACTICES, LAND USE, DRAINED BY ARTIFICIAL DITCHES - ACRES` (drenaje por zanjas); `SEEDS, FOR COVER CROPS - EXPENSE, MEASURED IN $`.

**Filas por condado (IA + IL + IN, `domain_desc=TOTAL`) en los archivos de Quick Stats:**

| `short_desc` | 2012 | 2017 | 2022 |
|---|---|---|---|
| `AG LAND, CROPLAND - ACRES` | 293 (0 con `(D)`) | 293 (0) | 293 (0) |
| `AG LAND, IRRIGATED - ACRES` | 291 (39 `(D)`) | 287 (45 `(D)`) | 289 (43 `(D)`) |
| `PRACTICES, LAND USE, CROPLAND, COVER CROP PLANTED, (EXCL CRP) - ACRES` | 0 (solo estado y país) | 293 (0) | 293 (2 `(D)`) |
| `PRACTICES, LAND USE, CROPLAND, CONSERVATION TILLAGE, NO-TILL - ACRES` | 0 (solo estado y país) | 293 (0) | 293 (0) |
| `PRACTICES, LAND USE, DRAINED BY TILE - ACRES` | 0 (solo estado y país) | 293 (4 `(D)`) | 293 (4 `(D)`) |

- 293 = 99 condados de Iowa + 102 de Illinois + 92 de Indiana. No hay filas con `county_code` 998 en estos ítems del censo.
- En riego faltan algunos condados (291, 287 y 289 de 293): no tienen fila. No se puede asumir 0: va vacío.
- `(D)` (dato oculto) va vacío con `flag_nass`, como dice el CLAUDE.md §4.

**2012 por condado.** El archivo `qs.census2012.txt.gz` trae las tres prácticas solo con `agg_level_desc` NATIONAL y STATE (por ejemplo, `DRAINED BY TILE - ACRES` aparece para IA, IL e IN a nivel estado con varios dominios, pero ninguna fila COUNTY). La ruta pública para 2012 es la Tabla 41 del Censo 2017, volumen 1, capítulo 2 (nivel condado), un PDF por estado, que tiene para cada condado las columnas 2017 y 2012 de "Land drained by tile", "Cropland on which no-till practices were used" y "Cropland planted to a cover crop (excluding CRP)". Ejemplo Iowa: `https://www.nass.usda.gov/sites/default/files/publications/agcensus/2017/Full_Report/Volume_1,_Chapter_2_County_Level/Iowa/st19_2_0041_0041.pdf` (Illinois `Illinois/st17_2_0041_0041.pdf` e Indiana `Indiana/st18_2_0041_0041.pdf`, misma ruta; los dos responden con PDF). Hay que leer el PDF y parsear la tabla: más trabajo y más riesgo que Quick Stats, pero es dato oficial de NASS. Los enlaces viejos (`www.nass.usda.gov/Publications/AgCensus/...`) dan 404; los nuevos están bajo `/sites/default/files/publications/agcensus/`.

**Qué mide cada pregunta.**
- Cobertura: la pregunta fue la misma en 2012, 2017 y 2022 (acres de cropland plantados con un cultivo de cobertura, excluyendo CRP). Puede ser un cultivo sembrado después de la cosecha o el único uso del lote en el año.
- Labranza: tres categorías mutuamente excluyentes sobre cropland (no-till, reducida excluyendo no-till, intensiva/convencional). La suma de las tres es menor que el cropland total.
- Tile: "acres drenados con caños" sobre el total de acres de la explotación (no solo cropland), así que `pct_drenaje_tile` sobre cropland puede pasar levemente el 100 % en condados con mucho tile en pasturas: conviene documentarlo o usar `AG LAND - ACRES` como alternativa.
- Riego: tierra regada de la explotación (`AG LAND, IRRIGATED`), no solo cropland regado (existe también `AG LAND, CROPLAND, HARVESTED, IRRIGATED - ACRES`).

Fuentes: [Quick Stats – archivos completos (USDA NASS)](https://www.nass.usda.gov/datasets), consultado 2026-11-14; [Quick Stats API – documentación (USDA NASS)](https://quickstats.nass.usda.gov/api), consultado 2026-11-14; [2017 Census of Agriculture, Iowa County Data, Table 41. Land Use Practices: 2017 and 2012 (USDA NASS)](https://www.nass.usda.gov/sites/default/files/publications/agcensus/2017/Full_Report/Volume_1,_Chapter_2_County_Level/Iowa/st19_2_0041_0041.pdf), consultado 2026-11-14; [Cover Crops and Covered Cropland, 2022 US Census of Agriculture (farmdoc daily)](https://farmdocdaily.illinois.edu/2024/02/cover-crops-and-covered-cropland-2022-us-census-of-agriculture.html), consultado 2026-11-14; [Use of Tile, 2017 US Census of Agriculture (farmdoc daily)](https://farmdocdaily.illinois.edu/2019/08/use-of-tile-2017-us-census-of-agriculture.html), consultado 2026-11-14; [Tillage Practices, 2017 US Census of Agriculture (farmdoc daily)](https://farmdocdaily.illinois.edu/?p=24354), consultado 2026-11-14; [Tile-drained acreage is increasing in northern areas of the United States (USDA ERS)](https://www.ers.usda.gov/data-products/charts-of-note/115570), consultado 2026-11-14

Confianza: alta para los `short_desc` y su cobertura por condado en 2017 y 2022 (verificados en los archivos completos de NASS); alta para la ausencia de prácticas de 2012 por condado en Quick Stats; media para la ruta de 2012 por la Tabla 41 (verificada solo para Iowa; falta probar el parseo).

Impacto: paquete `cultivos`, `practicas_censo.csv` (`pct_cobertura`, `pct_labranza_cero`, `pct_drenaje_tile`, `pct_riego`, con denominador `AG LAND, CROPLAND - ACRES`): 2017 y 2022 completos desde Quick Stats; 2012 solo `pct_riego` desde Quick Stats y el resto desde la Tabla 41 del Censo 2017 (PDF) o vacío. Data card `docs/datasets/cultivos.md` (Supuestos: denominador y tile sobre el total de la explotación; Problemas conocidos: 2012 de prácticas por condado y `(D)` en riego).

Citas:
> "cropland planted to a cover crop (excluding CRP)" — [2017 Census of Agriculture, Iowa County Data, Table 41 (USDA NASS)](https://www.nass.usda.gov/sites/default/files/publications/agcensus/2017/Full_Report/Volume_1,_Chapter_2_County_Level/Iowa/st19_2_0041_0041.pdf)
> "considering the cropland acres on this operation, how many acres were planted to a cover crop?" — [Cover Crops and Covered Cropland, 2022 US Census of Agriculture (farmdoc daily)](https://farmdocdaily.illinois.edu/2024/02/cover-crops-and-covered-cropland-2022-us-census-of-agriculture.html)
> "a total of 56 million US acres were reported as being drained by tile in the 2017 Census" — [Use of Tile, 2017 US Census of Agriculture (farmdoc daily)](https://farmdocdaily.illinois.edu/2019/08/use-of-tile-2017-us-census-of-agriculture.html)
> "No till was used on 37% of US acres for which a tillage system was reported, up from 35% in the 2012 Census of Agriculture" — [Tillage Practices, 2017 US Census of Agriculture (farmdoc daily)](https://farmdocdaily.illinois.edu/?p=24354)
> "Respondents to the 2022 Census of Agriculture reported the amount of their farm acreage that was drained by tile." — [Tile-drained acreage is increasing in northern areas of the United States (USDA ERS)](https://www.ers.usda.gov/data-products/charts-of-note/115570)
> "Census program includes the Census of Ag as well as follow up projects." — [Quick Stats API – documentación (USDA NASS)](https://quickstats.nass.usda.gov/api)
