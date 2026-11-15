# Riego y secano en NASS por condado (Nebraska y Kansas)

Pregunta: ¿Qué datos de `prodn_practice_desc` `IRRIGATED` y `NON-IRRIGATED` tiene NASS por condado en NE y KS (qué años, qué cultivos, cuánto ocultan con `(D)`) y cómo agregarlos a `produccion_anual.csv`?

Respuesta corta: En la encuesta (`source_desc=SURVEY`) hay rendimiento, superficie sembrada, superficie cosechada y producción por condado separados en `IRRIGATED` y `NON-IRRIGATED` para **maíz grano y soja de 2000 a 2018** y para **trigo de invierno de 2000 a 2019** (cosecha 2019, sembrada en 2018). Desde la cosecha 2019 no hay más: NASS dejó de publicar estimaciones de condado por práctica de riego porque el RMA retiró la financiación (Federal Register, 15/11/2019). En los datos de encuesta por condado **no aparece ni un `(D)`**: NASS no oculta celda por celda, sino que junta los condados con poca muestra en una fila "OTHER (COMBINED) COUNTIES" (`county_code` 998) por distrito. Por eso la cobertura por práctica es menor que la del total: maíz, 2.122 condado-año con rendimiento de riego sobre 3.223 con rendimiento total (2000–2018). La cobertura cae mucho desde 2008. Los datos son coherentes: riego + secano = total en el 100 % de los casos de superficie sembrada, y el rendimiento ponderado por superficie cosechada difiere del total en 0,03 bu/ac (mediana). Para después de 2018, el Censo Agropecuario (2002, 2007, 2012, 2017 y 2022) da la **superficie cosechada con riego por cultivo y condado** (sin rendimiento), con 7 % a 28 % de `(D)`. Propuesta: agregar columnas `*_riego_*` y `*_secano_*` al formato ancho de `produccion_anual.csv` (ver "Propuesta"), sin cambiar las claves. **Necesita el OK del humano.**

Detalle:

**Cómo se verificó.** Escaneé el archivo completo de Quick Stats `qs.crops_20261114.txt.gz` (1,13 GB, bajado con `src/cultivos/download.py` y filtrado a NE y KS con `filtrar()` de `src/cultivos/process.py`). Filtros: `SOURCE_DESC=SURVEY`, `AGG_LEVEL_DESC=COUNTY`, `DOMAIN_DESC=TOTAL`, `FREQ_DESC=ANNUAL`, `REFERENCE_PERIOD_DESC=YEAR`, años desde 2000. Para el censo: `SOURCE_DESC=CENSUS`, el mismo archivo. Kansas tiene 105 condados y Nebraska 93.

**Valores de `PRODN_PRACTICE_DESC`** en los condados de NE y KS: `ALL PRODUCTION PRACTICES`, `IRRIGATED`, `NON-IRRIGATED`, `NON-IRRIGATED, CONTINUOUS CROP` y `NON-IRRIGATED, FOLLOWING SUMMER FALLOW` (los dos últimos solo en trigo, 2000–2008: subdivisión del secano).

**Qué series hay por práctica (condado, desde 2000):**

| Cultivo (filtros) | Variables | Años |
|---|---|---|
| Maíz (`CORN`, `ALL CLASSES`; util `GRAIN` para cosecha, producción y rendimiento; `ALL UTILIZATION PRACTICES` para sembrada) | sembrada, cosechada, producción (BU), rendimiento (BU / ACRE) | 2000–2018 |
| Maíz silaje (util `SILAGE`) | cosechada, producción y rendimiento (TONS) | 2000–2008 |
| Soja (`SOYBEANS`, `ALL CLASSES`) | sembrada, cosechada, producción, rendimiento | 2000–2018 (KS: sin dato por práctica en 2010–2013 ni en 2017–2018) |
| Trigo de invierno (`WHEAT`, `WINTER`) | sembrada, cosechada, producción, rendimiento | 2000–2019 |
| Trigo, todas las clases (`WHEAT`, `ALL CLASSES`) | ídem, más la subdivisión del secano | 2000–2007 |
| Alfalfa (`HAY`, `ALFALFA`) | cosechada, producción, rendimiento (TONS) | 2000–2009 |
| Sorgo | ídem | 2000–2009 |

Avena: no tiene datos por práctica en NE ni en KS.

**Condados con rendimiento publicado por año** (sin la fila 998):

| Año | KS total | KS riego | KS secano | NE total | NE riego | NE secano |
|---|---|---|---|---|---|---|
| Maíz 2000 | 105 | 65 | 66 | 91 | 91 | 88 |
| Maíz 2007 | 97 | 57 | 57 | 90 | 87 | 83 |
| Maíz 2008 | 52 | 7 | 7 | 85 | 70 | 70 |
| Maíz 2012 | 87 | 34 | 37 | 85 | 71 | 71 |
| Maíz 2015 | 58 | 14 | 14 | 78 | 52 | 51 |
| Maíz 2018 | 58 | 20 | 24 | 72 | 31 | 31 |
| Maíz 2019 en adelante | 46–90 | 0 | 0 | 46–83 | 0 | 0 |
| Soja 2000 | 105 | 34 | 35 | 79 | 75 | 72 |
| Soja 2012 | 73 | 0 | 0 | 73 | 49 | 49 |
| Soja 2018 | 53 | 0 | 0 | 54 | 14 | 14 |
| Trigo inv. 2000 | 105 | 44 | 105 | 64 | 28 | 64 |
| Trigo inv. 2012 | 96 | 15 | 15 | 56 | 12 | 12 |
| Trigo inv. 2019 | 64 | 4 | 4 | 31 | 3 | 3 |

Totales 2000–2018/2019 (rendimiento): maíz KS 723 condado-año con riego y 746 con secano, NE 1.400 y 1.350; soja KS 344 y 364, NE 1.040 y 974; trigo de invierno KS 507 y 991, NE 432 y 656. La serie por práctica sirve sobre todo para Nebraska. En Kansas es despareja desde 2008.

**`(D)` y condados combinados.** En las filas de encuesta por condado de maíz, soja y trigo de NE y KS no hay ningún `(D)` ni otro código: todos los `VALUE` son números. Lo que NASS no puede publicar lo suma en "OTHER (COMBINED) COUNTIES" (`county_code` 998) de cada distrito, que se descarta como en el resto del paquete. Por práctica, esas filas son más: en el rendimiento de maíz de KS hay 147 filas 998 con riego, contra 118 con el total. Así que "cuánto ocultan" se mide como condados sin dato, no como `(D)`. `flag_nass` va a quedar vacío en las columnas nuevas.

**Coherencia.** En los 2.072 condado-año de maíz con las tres superficies sembradas, `IRRIGATED + NON-IRRIGATED = ALL` exacto en todos (en soja, 1.307 de 1.307; en trigo de invierno, 937 de 937). El rendimiento ponderado por superficie cosechada reproduce el total: diferencia mediana de 0,03 bu/ac en maíz y 0,04 en soja, y p99 menor que 1 bu/ac (redondeo).

**Cuánto pesa el riego** (mediana del % sembrado con riego, en los condados con dato):

| | Maíz 2000–07 | Maíz 2008–18 | Soja 2000–07 | Soja 2008–18 | Trigo inv. 2000–07 | Trigo inv. 2008–18 |
|---|---|---|---|---|---|---|
| KS | 51 % | 32 % | 27 % | 13 % | 7 % | 12 % |
| NE | 66 % | 64 % | 67 % | 57 % | 12 % | 16 % |

La muestra del período 2008–18 está sesgada hacia los condados que siguieron publicando. Brecha mediana de rendimiento (riego menos secano): maíz, 103 bu/ac en KS y 81 en NE; soja, 26 y 17; trigo de invierno, 14 y 24. Comparar el rendimiento `ALL` de NE y KS con el de Iowa sin separar el riego mezcla dos sistemas productivos distintos.

**Después de 2018: Censo Agropecuario.** El mismo archivo trae por condado (`SOURCE_DESC=CENSUS`, `DOMAIN_DESC=TOTAL`) `CORN, GRAIN, IRRIGATED - ACRES HARVESTED`, `SOYBEANS, IRRIGATED - ACRES HARVESTED` y `WHEAT, WINTER, IRRIGATED - ACRES HARVESTED` (trigo desde 2002), para 1997, 2002, 2007, 2012, 2017 y 2022. Hay 185–195 filas de condado de maíz por censo en NE+KS. De ellos, entre 12 y 24 tienen `(D)` (6–13 %); en soja, 24–32 (15–18 %); en trigo de invierno, 31–42 (23–28 %). Sirve para la fracción con riego de cada cultivo en años de censo. **No trae rendimiento por práctica.**

**Otra fuente posible para después de 2018 (no verificada en esta tarea).** El RMA publica el Summary of Business por estado, condado, cultivo, tipo, práctica y unidad. El código de práctica separa riego y secano en superficie asegurada, pero no da un rendimiento comparable al de NASS. No lo bajé ni lo revisé.

Fuentes:
- [Federal Register 2019-24789, Notice of Intent to Revise a Currently Approved Information Collection (NASS Field Crops docket)](https://federalregister.gov/d/2019-24789) (PDF de inspección pública: https://s3.amazonaws.com/public-inspection.federalregister.gov/2019-24789.pdf), consultado 2026-11-15. Cita: "Historically, the data collection costs for these two surveys has been partially funded through a cooperative agreement between NASS and the USDA Risk Management Agency (RMA). Due to program changes, RMA withdrew from this cooperative agreement this year. […] In addition, NASS will discontinue county estimates based on irrigated/non-irrigated practices."
- [USDA NASS Quick Stats – archivos completos (`qs.crops_20261114.txt.gz`)](https://www.nass.usda.gov/sites/default/files/datasets/qs.crops_20261114.txt.gz), consultado 2026-11-15. Todas las cifras de este documento salen de acá.
- [farmdoc daily, "2025 NASS County Corn, Soybean, and Winter Wheat Yields" (mayo 2026)](https://farmdocdaily.illinois.edu/2026/05/2025-nass-county-corn-soybean-and-winter-wheat-yields.html), consultado 2026-11-15: los rendimientos de condado actuales son de "all" production, sin separar riego.
- [AgWeb, "USDA Reveals Cause of Data Error That Skewed September Corn Estimates"](https://www.agweb.com/news/usda-reveals-cause-data-error-skewed-september-corn-estimates), consultado 2026-11-15: a nivel estado, NASS sigue combinando observaciones con riego y sin riego para NE y KS (error de ponderación en septiembre de 2026). Contexto, no se usa para datos.
- [RMA, Summary of Business – State/County/Crop/Type/Practice/Unit](https://public.rma.usda.gov/apps/ReportShare//Extranet/SOB/DataFiles/State_County_Crop_Coverage_Type_Practice_Unit/SOBTPU%20External%20All%20Years.pdf), consultado 2026-11-15 (solo se vio la descripción del archivo).

Confianza: alta en la cobertura, `(D)` y coherencia (conteos sobre el archivo oficial completo); alta en el corte de 2019 (Federal Register y datos coinciden); media en la utilidad del RMA (no revisado).

Impacto: `src/cultivos/process.py` (función `produccion`), `produccion_anual.csv` y su data card (`docs/datasets/cultivos.md`); opcionalmente `practicas_censo.csv`. Comparación de rendimiento NE/KS contra IA/IL/IN en ML.

## Propuesta (pendiente de aprobación del humano)

Cambia el esquema de `produccion_anual.csv`, así que no está implementada.

**Opción A (recomendada): columnas nuevas, mismas claves (`fips, anio, cultivo`).** Se agregan al final, vacías donde no hay dato (IA, IL, IN, OH, MN; NE y KS desde 2019; avena, alfalfa y heno):

| Columna | Origen (`PRODN_PRACTICE_DESC`) | Unidad |
|---|---|---|
| `sup_sembrada_riego_ac`, `sup_sembrada_secano_ac` | `AREA PLANTED`, `IRRIGATED` / `NON-IRRIGATED` | acres |
| `sup_cosechada_riego_ac`, `sup_cosechada_secano_ac` | `AREA HARVESTED` (mismo `UTIL` que el total) | acres |
| `produccion_riego_bu`, `produccion_secano_bu` | `PRODUCTION` | bu |
| `rend_riego_bu_ac`, `rend_secano_bu_ac` | `YIELD` | bu/ac |
| `rend_riego_kgha`, `rend_secano_kgha` | conversión con `bu_ac_a_kgha(cultivo)` | kg/ha |
| `pct_sembrada_riego` | `100 × sup_sembrada_riego_ac / sup_sembrada_ac` | % |

- Solo maíz grano, soja y trigo de invierno (para alfalfa hay 2000–2009, pero en TONS; se puede sumar si el equipo de ML lo pide).
- Trigo de invierno: el secano es `NON-IRRIGATED` (no las subdivisiones de barbecho).
- `flag_nass` sigue como está; las columnas nuevas no traen códigos en estos estados.
- Validación: `riego + secano ≈ total` en la superficie sembrada (tolerancia 1 %) y rangos de rendimiento iguales a los del total.
- Supuesto para el data card: "vacío" en las columnas por práctica quiere decir "no publicado o combinado en el distrito", no "sin riego".

**Opción B: formato largo con una columna `practica` (`todas`/`riego`/`secano`).** Agrega una clave más y triplica filas. Rompe la unión con `merge.py` por `fips, anio` y obliga a filtrar en todos lados. No la recomiendo.

**Complemento después de 2018 (opcional, otra tarea):** agregar a `practicas_censo.csv` `pct_maiz_riego`, `pct_soja_riego` y `pct_trigo_inv_riego` (superficie cosechada con riego del censo / superficie cosechada del cultivo en el censo × 100), años 2002–2022, `(D)` vacío con `flag_nass`. Así ML tiene una fracción con riego por cultivo para 2019–2025 (la del censo 2017 o 2022 como aproximación). Esto es un supuesto que tendría que decidir ML.
