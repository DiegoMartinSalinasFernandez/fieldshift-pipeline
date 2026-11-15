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

---

# Estados nuevos (OH, NE, MN, KS): verificación de los `short_desc` por condado

Pregunta: ¿Existen por condado en Ohio, Nebraska, Minnesota y Kansas los mismos `short_desc` de prácticas del Censo (2012, 2017, 2022)? ¿Cuántos condados quedan con `(D)`? ¿Conviene sumar en NE y KS la superficie regada por cultivo?

Respuesta corta: Sí. Los cinco `short_desc` de la tabla de arriba (cobertura, labranza cero, tile, riego y el denominador `AG LAND, CROPLAND - ACRES`) existen por condado en los cuatro estados, con el mismo patrón que IA/IL/IN: 2017 y 2022 completos, 2012 solo riego y cropland (las tres prácticas de 2012 están únicamente a nivel estado y país). Los `(D)` son pocos (0–5 por estado y práctica) salvo en **tile de NE y KS**, donde además faltan muchos condados sin fila. No hay filas `county_code` 998. En NE y KS sí conviene agregar la superficie regada **por cultivo** (`CORN, GRAIN, IRRIGATED - ACRES HARVESTED` y `SOYBEANS, IRRIGATED - ACRES HARVESTED` sobre su total cosechado): en Nebraska ~53 % del maíz grano y ~44 % de la soja cosechados son regados, y en Kansas ~25 % del maíz; `pct_riego` sobre cropland (8–10 % en KS) subestima mucho lo que pesa el riego en el rendimiento de maíz.

Detalle:

**Cómo se verificó.** Igual que la sección anterior: se escanearon los archivos completos `qs.census2012.txt.gz`, `qs.census2017.txt.gz` y `qs.census2022.txt.gz` (bajados el 2026-11-15 con `src/cultivos/download.py`), filtrando `AGG_LEVEL_DESC = COUNTY`, `DOMAIN_DESC = TOTAL` y los siete estados. Como control, los conteos de IA+IL+IN reproducen exactamente los de la sección anterior (p. ej. riego 2017: 287 filas, 45 `(D)`). Condados por estado: OH 88, NE 93, MN 87, KS 105 (373 en total), los mismos que aparecen en `AG LAND, CROPLAND - ACRES` los tres años.

**Filas por condado (`domain_desc=TOTAL`); entre paréntesis, cuántas son `(D)`.** "—" = 0 filas de condado (solo estado y país).

| `short_desc` | Año | OH (88) | NE (93) | MN (87) | KS (105) |
|---|---|---|---|---|---|
| `AG LAND, CROPLAND - ACRES` | 2012 | 88 (0) | 93 (0) | 87 (0) | 105 (0) |
|  | 2017 | 88 (0) | 93 (0) | 87 (0) | 105 (0) |
|  | 2022 | 88 (0) | 93 (0) | 87 (0) | 105 (0) |
| `AG LAND, IRRIGATED - ACRES` | 2012 | 88 (3) | 93 (0) | 87 (13) | 105 (5) |
|  | 2017 | 88 (5) | 93 (0) | 87 (13) | 105 (5) |
|  | 2022 | 88 (2) | 93 (0) | 86 (10) | 104 (5) |
| `PRACTICES, LAND USE, CROPLAND, COVER CROP PLANTED, (EXCL CRP) - ACRES` | 2012 | — | — | — | — |
|  | 2017 | 88 (2) | 93 (3) | 87 (2) | 105 (2) |
|  | 2022 | 88 (2) | 93 (4) | 87 (0) | 103 (2) |
| `PRACTICES, LAND USE, CROPLAND, CONSERVATION TILLAGE, NO-TILL - ACRES` | 2012 | — | — | — | — |
|  | 2017 | 88 (0) | 93 (3) | 87 (2) | 105 (0) |
|  | 2022 | 88 (0) | 93 (2) | 87 (2) | 105 (0) |
| `PRACTICES, LAND USE, DRAINED BY TILE - ACRES` | 2012 | — | — | — | — |
|  | 2017 | 88 (0) | **78 (23)** | 85 (5) | **85 (27)** |
|  | 2022 | 88 (0) | **73 (22)** | 86 (5) | **75 (23)** |

**Totales estatales (suma de condados con valor publicado; no incluye `(D)`), en millones de acres**, para dimensionar:

| | OH | NE | MN | KS |
|---|---|---|---|---|
| Cropland 2022 | 10,5 | 21,2 | 21,5 | 28,3 |
| Regado (`AG LAND, IRRIGATED`) 2022 | 0,07 | 7,97 | 0,62 | 2,34 |
| Cobertura 2022 | 0,75 | 0,93 | 0,76 | 0,77 |
| Labranza cero 2022 | 4,14 | 10,10 | 1,19 | 11,75 |
| Tile 2022 | 5,09 | 0,62 | 8,24 | 0,30 |

**Por estado.**

- **Ohio.** Todo completo en 2017 y 2022 (88/88 en las cuatro prácticas); solo 2 `(D)` en cobertura y 2–5 en riego. Tile cubre ~48 % del cropland, como Indiana. El riego es despreciable (< 1 % del cropland, 0,2–0,4 % del maíz grano): `pct_riego` alcanza, no hace falta el riego por cultivo.
- **Nebraska.** Cobertura y labranza cero completas (2–4 `(D)`). Riego: 93/93 sin ningún `(D)` en los tres censos. **Tile**: en 2017 faltan 15 condados (sin ninguna fila de tile, ni de acres ni de número de explotaciones) y 23 de los 78 con fila son `(D)`; en 2022 faltan 20 y hay 22 `(D)`. Los 20 condados sin fila de 2022 suman el 13,8 % del cropland del estado. El tile en Nebraska es marginal (0,6 M acres, ~3 % del cropland), así que `pct_drenaje_tile` va a quedar vacío en ~45 % de los condados de NE pero casi sin información perdida. Riego por cultivo (2022): maíz grano regado 52,7 % del cosechado en el estado, soja 43,8 %; en 49 de los 88 condados con dato publicado, más de la mitad del maíz es regado.
- **Minnesota.** Todo completo (85–87 de 87). `(D)`: 0–2 en cobertura y labranza, 5 en tile, 10–13 en riego (el estado con más `(D)` de riego, por ser poco regado y concentrado). Tile es la práctica dominante (8,2 M acres, ~38 % del cropland). Riego por cultivo: 3,9 % del maíz y 1,6 % de la soja; solo 2–3 condados (arenales del centro del estado) superan el 50 % de maíz regado.
- **Kansas.** Cobertura (103–105, 2 `(D)`) y labranza cero (105/105, 0 `(D)`) completas. **Tile**: en 2017 faltan 20 condados y hay 27 `(D)` entre los 85 con fila; en 2022 faltan 30 y hay 23 `(D)`, o sea que **solo 52 de 105 condados tienen valor de tile en 2022**. Los 30 sin fila suman el 35,8 % del cropland de KS (son del oeste, secano o regado por pivote, donde no se drena). Riego por cultivo (2022): maíz grano 25,3 % regado en el estado, soja 7,8 %; 15–18 condados con más de la mitad del maíz regado (oeste del estado, acuífero Ogallala), mientras el cropland regado total es solo 9 %.

**Condados sin fila.** Igual que con riego en IA/IL/IN: un condado sin fila no se puede rellenar con 0 (regla 1 y §4 del CLAUDE.md). En tile de NE y KS lo más probable es que la ausencia signifique "nadie declaró tile" (no hay ni fila de número de explotaciones, y son condados del oeste), pero eso es un supuesto: va vacío y se anota en el data card. Si ML prefiere tratarlo como 0, que lo decida al modelar.

**Riego por cultivo en NE y KS: conviene agregarlo.** `pct_riego = AG LAND, IRRIGATED / AG LAND, CROPLAND` mezcla pasturas regadas y todos los cultivos. Para explicar rendimientos de maíz y soja (`ALL PRODUCTION PRACTICES` mezcla riego y secano, ver tarea T004) lo útil es la fracción regada de cada cultivo. Los `short_desc` existen por condado los tres años (incluido 2012):

| `short_desc` (numerador / denominador) | Filas de condado 2012 / 2017 / 2022 (`(D)`) |
|---|---|
| `CORN, GRAIN, IRRIGATED - ACRES HARVESTED` / `CORN, GRAIN - ACRES HARVESTED` | NE 91 (5) / 92 (5) / 90 (2); KS 96 (11) / 94 (7) / 98 (16); MN 66 (19) / 64 (14) / 64 (14); OH 40 (28) / 25 (15) / 47 (19) |
| `SOYBEANS, IRRIGATED - ACRES HARVESTED` / `SOYBEANS - ACRES HARVESTED` | NE 84 (12) / 84 (7) / 88 (7); KS 93 (16) / 91 (20) / 93 (21); MN 61 (26) / 54 (18) / 66 (22); OH 28 (23) / 30 (23) / 52 (24) |
| `AG LAND, CROPLAND, HARVESTED, IRRIGATED - ACRES` / `AG LAND, CROPLAND, HARVESTED - ACRES` | todos los condados; `(D)` NE 13–19, KS 24–34, MN 27–35, OH 31–34 |

También hay por condado trigo regado (`WHEAT, WINTER, IRRIGATED - ACRES HARVESTED`, 51–89 condados en NE y KS) y heno/alfalfa regados (`HAY, ALFALFA, IRRIGATED - ACRES HARVESTED`, 77–93 condados). El nombre es `CORN, GRAIN, IRRIGATED` (no existe `CORN, IRRIGATED - ACRES HARVESTED`). En OH, MN, IA, IL e IN estas columnas quedan casi vacías o con muchos `(D)`, pero agregarlas no cuesta nada y mantiene el mismo esquema en los siete estados.

Pendiente (no verificado acá): la encuesta anual (`source_desc=SURVEY`) de NASS publica rendimiento y superficie por condado separando `IRRIGATED` y `NON-IRRIGATED` en `prodn_practice_desc` para estados como NE y KS; eso está en `qs.crops_<fecha>.txt.gz`, que no se bajó en esta tarea. Si existe, es mejor que el censo para T004 porque es anual.

Fuentes: [Quick Stats – archivos completos (USDA NASS)](https://www.nass.usda.gov/datasets), consultado 2026-11-15 (archivos `qs.census2012.txt.gz`, `qs.census2017.txt.gz`, `qs.census2022.txt.gz`); [Quick Stats API – documentación (USDA NASS)](https://quickstats.nass.usda.gov/api), consultado 2026-11-14.

Confianza: alta para la existencia de los `short_desc`, los conteos de filas y `(D)` y los totales (leídos de los archivos completos de NASS y validados contra los conteos ya publicados de IA/IL/IN); media para la interpretación de los condados sin fila de tile como "sin tile" (supuesto, no confirmado por NASS).

Impacto (lo que T003 tiene que tener en cuenta en `practicas_censo.csv`, paquete `cultivos`):
1. Los `short_desc` de `CENSO_NUM` y `CENSO_DEN` de `src/cultivos/process.py` sirven sin cambios para OH, NE, MN y KS.
2. 2012 sigue igual que en IA/IL/IN: solo `pct_riego` por condado; las otras tres prácticas, vacías o desde la Tabla 41 del Censo 2017 (PDF por estado: `Ohio/st39_2_0041_0041.pdf`, `Nebraska/st31_2_0041_0041.pdf`, `Minnesota/st27_2_0041_0041.pdf`, `Kansas/st20_2_0041_0041.pdf`; rutas armadas con el mismo patrón que Iowa, no probadas).
3. `pct_drenaje_tile` en NE y KS: ~45–50 % de los condados vacíos (sin fila o `(D)`). Anotarlo en "Problemas conocidos" del data card con los números de arriba; no rellenar con 0.
4. Propuesta (cambia el esquema del CSV, decide el humano): agregar `pct_maiz_regado` (= `CORN, GRAIN, IRRIGATED - ACRES HARVESTED` / `CORN, GRAIN - ACRES HARVESTED`), `pct_soja_regada` (ídem con `SOYBEANS`) y `pct_cosechado_regado` (= `AG LAND, CROPLAND, HARVESTED, IRRIGATED` / `AG LAND, CROPLAND, HARVESTED`), con su `flag_nass`. Son clave en NE y KS y existen también para 2012.
5. Ningún `pct_riego` supera 100 % en los cuatro estados (2017 y 2022).
