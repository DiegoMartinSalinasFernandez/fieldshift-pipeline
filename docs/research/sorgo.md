# Sorgo granífero en Kansas y Nebraska

Pregunta: ¿Conviene sumar el sorgo granífero a los cultivos de `config.yaml`? Superficie por estado en los 7 estados (2015–2025) frente a soja y trigo de invierno; si NASS publica rendimiento de sorgo por condado (años, condados por año, filas 998, `short_desc` exactos); código y precisión del sorgo en el CDL de KS y NE; y qué haría falta para sumarlo.

Respuesta corta: En **Kansas** el sorgo es un cultivo grande: entre 2,6 y 3,6 millones de acres sembrados por año en 2015–2025 (3,0 M en 2025), o sea entre el 50 % y el 87 % de la superficie de soja y entre el 34 % y el 49 % de la de trigo de invierno. En **Nebraska** es chico: 180.000 a 340.000 acres, menos del 7 % de la soja. En Illinois NASS dejó de estimarlo a nivel estado después de 2018 (15.000 a 38.000 acres hasta ahí) y en IA, IN, MN y OH no hay estimación de sorgo en ningún año de 2015–2025. NASS **sí** publica el rendimiento por condado (`SORGHUM, GRAIN - YIELD, MEASURED IN BU / ACRE`), pero en los últimos años solo para una minoría de condados: en Kansas, 24 de 105 en 2025 (entre 19 y 73 por año desde 2015), con el 61 % de la superficie cosechada del estado escondida en la fila "OTHER (COMBINED) COUNTIES" (998); en Nebraska, entre 2 y 13 condados por año desde 2015, con el 65–96 % de la superficie en la 998. En el CDL el sorgo es el **código 4** (y 236, doble cultivo trigo de invierno/sorgo); en el CDL 2023 su precisión es aceptable en Kansas (81,0 % del productor, 81,9 % del usuario) y mala en Nebraska (56,8 % y 72,3 %). El bushel de sorgo es de 56 lb, igual que el de maíz: 1 bu/ac = 62,77 kg/ha.

**Recomendación (la decisión es del humano):** sumar el sorgo **como clase de rotación** (CDL y CSB) en Kansas, y **no** como cultivo objetivo de rendimiento. Sin el sorgo, los porcentajes de rotación de Kansas dejan afuera la rotación trigo–sorgo–barbecho, que es la rotación de secano típica del oeste del estado. Como target de rendimiento por condado no sirve: después de 2017 NASS publica menos de la mitad de los condados de Kansas en casi todos los años, y en Nebraska casi ninguno. En Nebraska y en los estados del este no vale la pena.

Detalle:

**Método.** El script `docs/research/sorgo_conteo.py` recorre la base completa de Quick Stats bajada el 2026-11-14 (`data/raw/cultivos/nass/qs.crops_20261114.txt.gz`, 90 s) y escribe dos tablas: superficie por estado (2015–2025, `source_desc=SURVEY`, `domain_desc=TOTAL`, `reference_period_desc=YEAR`) y cobertura por condado (2000–2025, mismos filtros más `agg_level_desc=COUNTY`). Una fila con `county_code` 998 cuenta como combinada; las demás, como condado con dato (no hay ninguna fila de condado con código entre paréntesis, igual que con maíz y soja en `nass_2024_2025.md`). Se corre así:

```
.venv/bin/python -X utf8 docs/research/sorgo_conteo.py > sorgo_conteo.csv
```

Las fechas de Crop Progress de abajo salen de la misma base (filas de `SORGHUM` a nivel estado), interpolando el día en que cada serie semanal cruza el 50 %.

**1. Superficie por estado (miles de acres; `short_desc` usados abajo).** Sorgo sembrado = `SORGHUM - ACRES PLANTED` (grano + silaje: NASS no publica la siembra solo de grano en estos años); sorgo cosechado = `SORGHUM, GRAIN - ACRES HARVESTED`; soja = `SOYBEANS - ACRES PLANTED`; trigo de invierno = `WHEAT, WINTER - ACRES PLANTED`; maíz = `CORN - ACRES PLANTED`.

Kansas:

| Año | Sorgo sembrado | Sorgo cosechado (grano) | Soja sembrada | Trigo inv. sembrado | Maíz sembrado | Sorgo / soja | Sorgo / trigo |
|---|---|---|---|---|---|---|---|
| 2015 | 3.400 | 3.200 | 3.900 | 9.200 | 4.150 | 87 % | 37 % |
| 2016 | 3.100 | 2.950 | 4.050 | 8.500 | 5.100 | 77 % | 36 % |
| 2017 | 2.600 | 2.450 | 5.150 | 7.600 | 5.500 | 50 % | 34 % |
| 2018 | 2.800 | 2.650 | 4.750 | 7.700 | 5.450 | 59 % | 36 % |
| 2019 | 2.600 | 2.400 | 4.550 | 7.100 | 6.400 | 57 % | 37 % |
| 2020 | 3.000 | 2.800 | 4.800 | 6.600 | 6.100 | 63 % | 45 % |
| 2021 | 3.600 | 3.400 | 4.850 | 7.300 | 5.700 | 74 % | 49 % |
| 2022 | 3.300 | 2.700 | 5.050 | 7.300 | 5.500 | 65 % | 45 % |
| 2023 | 3.600 | 3.250 | 4.430 | 8.100 | 5.750 | 81 % | 44 % |
| 2024 | 3.000 | 2.800 | 4.550 | 7.600 | 6.300 | 66 % | 39 % |
| 2025 | 3.000 | 2.800 | 4.100 | 7.300 | 6.800 | 73 % | 41 % |

Nebraska:

| Año | Sorgo sembrado | Sorgo cosechado (grano) | Soja sembrada | Trigo inv. sembrado | Maíz sembrado | Sorgo / soja |
|---|---|---|---|---|---|---|
| 2015 | 270 | 240 | 5.300 | 1.490 | 9.400 | 5 % |
| 2016 | 200 | 175 | 5.200 | 1.370 | 9.850 | 4 % |
| 2017 | 180 | 130 | 5.700 | 1.120 | 9.550 | 3 % |
| 2018 | 230 | 170 | 5.650 | 1.100 | 9.600 | 4 % |
| 2019 | 200 | 130 | 4.900 | 1.070 | 10.100 | 4 % |
| 2020 | 195 | 150 | 5.200 | 900 | 10.200 | 4 % |
| 2021 | 320 | 230 | 5.600 | 920 | 9.900 | 6 % |
| 2022 | 320 | 125 | 5.750 | 980 | 9.600 | 6 % |
| 2023 | 340 | 225 | 5.250 | 1.130 | 9.950 | 6 % |
| 2024 | 290 | 260 | 5.300 | 1.000 | 10.050 | 5 % |
| 2025 | 250 | 205 | 4.850 | 950 | 10.700 | 5 % |

Otros estados: Illinois tiene sorgo sembrado de 38.000 (2015), 18.000 (2016), 17.000 (2017) y 18.000 acres (2018), y ninguna fila de estado desde 2019. Iowa, Indiana, Minnesota y Ohio no tienen ninguna fila de superficie de sorgo a nivel estado en 2015–2025.

En Kansas la diferencia entre sembrado y cosechado como grano (100.000 a 600.000 acres) es silaje, pastoreo o abandono; el silaje cosechado (`SORGHUM, SILAGE - ACRES HARVESTED`) fue de 45.000 a 140.000 acres por año.

**2. Rendimiento por condado.** `short_desc` exactos a nivel `COUNTY` (todos con `source_desc=SURVEY`):

- `SORGHUM, GRAIN - YIELD, MEASURED IN BU / ACRE` (rendimiento, `prodn_practice_desc=ALL PRODUCTION PRACTICES`)
- `SORGHUM, GRAIN - ACRES HARVESTED`
- `SORGHUM, GRAIN - PRODUCTION, MEASURED IN BU`
- `SORGHUM - ACRES PLANTED` (grano + silaje; `util_practice_desc=ALL UTILIZATION PRACTICES`)
- Con riego y sin riego: `SORGHUM, GRAIN, IRRIGATED - ...` y `SORGHUM, GRAIN, NON-IRRIGATED - ...`. En Kansas el último año con rendimiento por condado separado por riego es 2009 y en Nebraska, 2008.
- `SORGHUM, GRAIN - ACRES PLANTED, NET` y `... YIELD, MEASURED IN BU / NET PLANTED ACRE` solo existen por condado en los años 70 y 80; no sirven para 2000–2025.
- Silaje: `SORGHUM, SILAGE - YIELD, MEASURED IN TONS / ACRE` (no se contó).

Condados con rendimiento publicado (el número es el mismo para superficie cosechada, superficie sembrada y producción en todos los años) y filas 998:

| Año | KS condados (de 105) | KS filas 998 | KS % cosechado en 998 | NE condados (de 93) | NE filas 998 | NE % cosechado en 998 | IL condados (de 102) |
|---|---|---|---|---|---|---|---|
| 2000 | 105 | 0 | 0,0 | 57 | 5 | 0,5 | 23 |
| 2005 | 99 | 3 | 0,2 | 48 | 6 | 1,6 | 12 |
| 2008 | 44 | 8 | 48,2 | 24 | 5 | 13,7 | 7 |
| 2010 | 82 | 5 | 4,1 | 24 | 5 | 21,0 | 8 |
| 2012 | 71 | 7 | 12,4 | 15 | 5 | 28,6 | 8 |
| 2015 | 46 | 9 | 45,5 | 9 | 5 | 74,4 | 1 |
| 2016 | 50 | 9 | 36,2 | 13 | 4 | 64,5 | 1 |
| 2017 | 41 | 9 | 45,5 | 5 | 4 | 79,1 | — |
| 2018 | 21 | 7 | 73,3 | 2 | 3 | 96,2 | — |
| 2019 | 19 | 9 | 71,8 | 6 | 2 | 75,1 | — |
| 2020 | 73 | 1 | 7,7 | 8 | 1 | 69,0 | — |
| 2021 | 56 | 1 | 31,3 | 5 | 1 | 96,4 | — |
| 2022 | 46 | 1 | 32,1 | 8 | 1 | 91,9 | — |
| 2023 | 42 | 1 | 39,3 | 6 | 1 | 74,8 | — |
| 2024 | 38 | 1 | 52,2 | 8 | 1 | 81,9 | — |
| 2025 | 24 | 1 | 61,3 | 6 | 1 | 84,1 | — |

Los años intermedios (2001–2004, 2006–2007, 2009, 2011, 2013–2014) están en la salida del script. Iowa, Indiana, Minnesota y Ohio no tienen ninguna fila de sorgo por condado en 2000–2025; Illinois, ninguna desde 2017. Hasta 2019 la 998 viene una vez por distrito agrícola (`asd_code`); desde 2020, una sola vez por estado (`asd_code` 99), igual que con maíz y soja. El "% cosechado en 998" es la superficie cosechada de la 998 sobre la suma de condados + 998.

Comparado con el maíz y la soja de Kansas en 2025 (50 % y 46 % de los condados, `nass_2024_2025.md`), el sorgo tiene menos de la cuarta parte (23 %), aunque en Kansas su superficie es del mismo orden.

**3. CDL: código y precisión.** En la lista de categorías de los metadatos del CDL, `"4" Sorghum` y `"236" Dbl Crop WinWht/Sorghum` (también existen 234 durum/sorgo y 235 cebada/sorgo). Precisión del productor y del usuario contra los datos de validación de la FSA, de los metadatos FGDC por estado (`metadata-ks23`, `-ne23`, `-ks22`, `-ne22`, `-ks21`, `-ne21`). Los metadatos de 2024 y 2025 (`metadata-ks24`, `-ks25`, `-ne24`, `-ne25`) devuelven 404 en esta corrida.

| Estado y año | Global cultivos FSA (kappa) | Sorgo (4): píxeles validación | Productor | Usuario | Doble trigo/sorgo (236): productor / usuario |
|---|---|---|---|---|---|
| KS 2023 | 81,5 % (0,780) | 65.629 | 81,0 % | 81,9 % | 32,3 / 56,8 % |
| KS 2022 | no leído | 59.185 | 76,1 % | 82,8 % | no leído |
| KS 2021 | 83,8 % (0,806) | 71.854 | 84,1 % | 85,7 % | no leído |
| NE 2023 | 90,1 % (0,834) | 5.816 | 56,8 % | 72,3 % | 0 píxeles |
| NE 2022 | no leído | 3.982 | 41,1 % | 64,2 % | no leído |
| NE 2021 | 90,2 % (0,838) | 6.067 | 56,2 % | 78,2 % | no leído |

Para comparar, en KS 2023: maíz 90,6 / 92,8 %, soja 87,0 / 88,8 %, trigo de invierno 88,5 / 87,4 %. En Kansas el sorgo está unos 8 puntos por debajo de los otros cultivos grandes, pero sirve para porcentajes por condado. En Nebraska se pierde casi la mitad del sorgo real (omisión 43 %), que se confunde con otras clases. ("No leído": el regex sobre el texto del metadato no encontró la línea; no se revisó a mano.)

**4. Calendario (Crop Progress, día del 50 %, mediana 2015–2025 y rango).**

| Estado | Sembrado | Panojado (headed) | Madurez | Cosechado |
|---|---|---|---|---|
| KS | 10 de junio (DOY 157–166) | 6 de agosto (214–225) | 28 de septiembre (267–278) | 21 de octubre (290–309) |
| NE | 29 de mayo (144–160) | 1 de agosto (209–220) | 24 de septiembre (264–274) | 21 de octubre (287–312) |

`short_desc`: `SORGHUM - PROGRESS, MEASURED IN PCT PLANTED`, `... PCT HEADED`, `... PCT MATURE` y `SORGHUM, GRAIN - PROGRESS, MEASURED IN PCT HARVESTED`. La emergencia (`PCT EMERGED`) tiene muy pocas filas. La siembra en Kansas es de 4 a 6 semanas posterior a la del maíz, por eso entra bien después de un barbecho que empieza con la cosecha del trigo de julio del año anterior.

**5. Rotaciones típicas en Kansas.** La rotación de secano del oeste de Kansas que se estudia en la estación de Tribune es trigo–sorgo–barbecho (WSF, 3 años: trigo de invierno, sorgo al año siguiente sobre el rastrojo y después unos 11 meses de barbecho hasta la siembra del trigo). Según K-State, "the traditional wheat-fallow system is being replaced by wheat-summer crop-fallow rotations" (Schlegel, Holman y Burnett, 2020). También se estudian rotaciones de 4 años (trigo–trigo–sorgo–barbecho y trigo–sorgo–sorgo–barbecho) y la labranza ocasional en WSF (Holman, Obour y Haag, 2025; Schlegel y Holman, 2018). Para el pipeline esto significa que en Kansas hacen falta transiciones que hoy no se calculan: `pct_sorgo_tras_trigo`, `pct_trigo_tras_barbecho` (barbecho del CDL, código 61) y la secuencia WSF en el CSB.

Lo que **no** se averiguó: la tabla de fechas del Handbook 628 (no se abrió en esta corrida; la cifra de 2,5 M acres de la tarea sale de ahí); los parámetros FAO-56 del sorgo (Kc, duración de etapas), la temperatura base de GDD, la tolerancia a sequía y el resto de las columnas de `config/cultivos.csv`; la proporción del sorgo de Kansas que se riega en los años recientes (NASS no la publica por condado desde 2009; el Censo podría tenerla).

**6. Qué haría falta para sumarlo.**

1. `config/config.yaml`: agregar `sorgo` a la lista de cultivos (decisión del humano). Si se quiere solo para rotaciones, agregarlo a los grupos de clases del CDL y no a la lista de cultivos de NASS.
2. `data/reference/clases_cdl.csv`: grupo `sorgo` para el código 4, y decidir qué hacer con el 236 (doble cultivo trigo/sorgo; lo más simple es contarlo en `doble_cultivo`, como el 26).
3. `src/cultivos/`: en `produccion_anual.csv`, el sorgo entraría con `commodity_desc=SORGHUM`, `util_practice_desc=GRAIN` para rendimiento, cosechada y producción, y `ALL UTILIZATION PRACTICES` para sembrada (que incluye silaje: hay que anotarlo en el data card, porque `ratio_cosechada` va a salir más bajo que en los otros cultivos). En `rotacion_anual.csv`, sumar `pct_sorgo` y las transiciones de sorgo. En `rotacion_secuencia.csv`, sumar WSF.
4. `src/common/` (conversiones; cambiarlo requiere el OK del humano): `bu_ac_a_kgha('sorgo')` con el bushel de 56 lb, igual que el maíz: 56 lb × 0,45359237 kg/lb ÷ 0,40468564 ha/ac = **62,77 kg/ha por bu/ac**.
5. `config/cultivos.csv`: una fila `sorgo,Sorgo granífero,...` con siembra y cosecha por estado (se pueden usar las medianas de Crop Progress de arriba), período crítico (alrededor de la floración, cerca del 50 % panojado), Kc y etapas de FAO-56, temperatura base (hay que buscarla), raíces, rastrojo, familia `Poaceae`, tolerancia a sequía. Necesita su propio research.
6. `loop/spec/entregables.yaml` y `validar_csv()`: un rango físico para el rendimiento del sorgo (no se fijó acá; hay que sacarlo de los datos y de la literatura).

Fuentes:
- Base completa de NASS Quick Stats, `qs.crops_20261114.txt.gz` (bajada por `src/cultivos/download.py` de [Quick Stats](https://www.nass.usda.gov/datasets/)), leída el 2026-11-15 con `docs/research/sorgo_conteo.py`.
- [2023 Kansas Cropland Data Layer, metadatos](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ks23), consultado 2026-11-15.
- [2023 Nebraska Cropland Data Layer, metadatos](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ne23), consultado 2026-11-15.
- Metadatos CDL [KS 2022](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ks22), [KS 2021](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ks21), [NE 2022](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ne22), [NE 2021](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ne21), consultados 2026-11-15.
- Schlegel, A.; Holman, J.; Burnett, A. (2020), [Wheat and Grain Sorghum in Four-Year Rotations](https://journals.newprairiepress.org/kaesrr/article/11128/galley/11021/download/), Kansas Agricultural Experiment Station Research Reports 6(8), doi:10.4148/2378-5977.7953, consultado 2026-11-15.
- Holman, J.; Obour, A.; Haag, L. (2025), [Occasional Tillage in a Wheat-Sorghum-Fallow Rotation](https://journals.newprairiepress.org/kaesrr/article/6722/galley/6661/download/), KAES Research Reports 11(4), doi:10.4148/2378-5977.8717, consultado 2026-11-15.
- Schlegel, A.; Holman, J. D. (2018), [Occasional Tillage in a Wheat-Sorghum-Fallow Rotation](https://journals.newprairiepress.org/kaesrr/article/11401/galley/11291/download/), KAES Research Reports 4(8), doi:10.4148/2378-5977.7629, consultado 2026-11-15.
- Bean, B. (2025-10-22), [Sorghum test weight—an odd but necessary measurement](https://hpj.com/?p=170405), High Plains Journal: "Grain sorghum is sold in the United States either in 100-pound increments or in bushels using a standard weight of 56 pounds." Consultado 2026-11-15. (El Handbook 697 del USDA y el apéndice del Censo 1997 con la tabla de pesos no se pudieron abrir: 404 o redirección a HTML.)

Confianza: alta para la superficie, la cobertura por condado y la precisión del CDL (salen directo de la base de NASS y de los metadatos); media para el bushel de 56 lb (fuente secundaria de la industria, aunque coincide con el uso de NASS de rendimiento en bu/ac); media para las rotaciones (reportes de una sola estación experimental, Tribune y Garden City).

Impacto: `config/config.yaml` (lista de cultivos), `config/cultivos.csv` (fila nueva), `data/reference/clases_cdl.csv` (código 4 y 236), `src/common/` (conversión de bushel), paquete `cultivos` (`produccion_anual.csv`, `rotacion_anual.csv`, `rotacion_secuencia.csv`, `fenologia_estado.csv`). Todo eso requiere la decisión del humano; este research no cambia nada.
