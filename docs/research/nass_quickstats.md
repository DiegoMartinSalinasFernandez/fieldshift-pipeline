# NASS Quick Stats: short_desc, condados combinados, (D) y años 2024–2025

Pregunta: NASS Quick Stats: short_desc exactos de rendimiento, superficie y producción por cultivo; cómo vienen los condados combinados y los valores (D); si están publicados los datos de condado de 2024 y 2025.

Respuesta corta: `short_desc` es la concatenación de seis campos (`commodity_desc`, `class_desc`, `prodn_practice_desc`, `util_practice_desc`, `statisticcat_desc`, `unit_desc`). Con fuente verificada: `CORN, GRAIN - YIELD, MEASURED IN BU / ACRE`, `SOYBEANS - YIELD, MEASURED IN BU / ACRE`, `WHEAT, WINTER - YIELD, MEASURED IN BU / ACRE` y `CORN - ACRES PLANTED`. Los de superficie cosechada y producción, avena y heno siguen la misma regla, pero no encontré una página pública sin login que los liste: hay que confirmarlos con `get_param_values` cuando esté `NASS_API_KEY`. Los condados combinados vienen con `county_code` = 998 ("Other (Combined) Counties"): no son un condado y hay que dejarlos afuera. `(D)` quiere decir "Withheld to avoid disclosing data for individual operations": va vacío y el código se guarda en `flag_nass`. Los datos de condado de 2024 están publicados: NASS había suspendido las estimaciones de condado desde la cosecha 2024 (aviso del 9 de abril de 2024) y las repuso el 19 de marzo de 2025 para maíz y soja de 2024 (los cereales finos, recién desde 2025). Los de 2025 de maíz, soja y trigo de invierno salieron en la primavera de 2026 (farmdoc daily, mayo de 2026), con menos condados con dato que en 2024.

Detalle:

**Cómo se arma `short_desc`.** La documentación de la API define `short_desc` ("Data Item") como la concatenación de seis columnas: `commodity_desc, class_desc, prodn_practice_desc, util_practice_desc, statisticcat_desc, unit_desc`. Los campos vacíos o "ALL ..." no aparecen en el texto. Por eso el rendimiento de maíz lleva la utilización ("GRAIN") y la superficie sembrada no (se siembra maíz para todos los usos).

| Cultivo | Variable | `short_desc` | Estado |
|---|---|---|---|
| Maíz | rendimiento | `CORN, GRAIN - YIELD, MEASURED IN BU / ACRE` | verificado (KBS LTER, extracto de Quick Stats) |
| Maíz | sup. sembrada | `CORN - ACRES PLANTED` | verificado (ejemplo de la página de la API) |
| Soja | rendimiento | `SOYBEANS - YIELD, MEASURED IN BU / ACRE` | verificado (KBS LTER) |
| Trigo de invierno | rendimiento | `WHEAT, WINTER - YIELD, MEASURED IN BU / ACRE` | verificado (KBS LTER) |
| Maíz | sup. cosechada, producción | `CORN, GRAIN - ACRES HARVESTED`, `CORN, GRAIN - PRODUCTION, MEASURED IN BU` | sin verificar: confirmar con `get_param_values` |
| Soja | sembrada, cosechada, producción | `SOYBEANS - ACRES PLANTED`, `SOYBEANS - ACRES HARVESTED`, `SOYBEANS - PRODUCTION, MEASURED IN BU` | sin verificar |
| Trigo de invierno, avena | sembrada, cosechada, producción | mismo patrón con `WHEAT, WINTER` y `OATS` | sin verificar |
| Alfalfa y otro heno | rendimiento y producción | se miden en toneladas (`TONS / ACRE`, `TONS`), no en bushels; nombres exactos sin verificar | sin verificar |

Para no depender del texto de `short_desc`, el pedido puede filtrar por los campos que lo forman: `commodity_desc` (CORN, SOYBEANS, WHEAT, OATS, HAY), `statisticcat_desc` (YIELD, AREA PLANTED, AREA HARVESTED, PRODUCTION), `unit_desc` y `prodn_practice_desc=ALL PRODUCTION PRACTICES`. Que `statisticcat_desc` de la superficie sembrada es "AREA PLANTED" y `unit_desc` "ACRES" sale del ejemplo de respuesta de la propia página de la API. La API devuelve como máximo 50.000 filas por pedido ("exceeds limit = 50000"); `get_counts` sirve para medir antes.

**Condados combinados.** En la tabla de campos de la API, `county_code` son los códigos de condado de NASS de 3 dígitos, que coinciden con los ANSI salvo el 998, reservado para "Other (Combined) Counties" (y los códigos de Alaska). Esas filas agrupan los condados con pocos informantes de un distrito agrícola (`asd_code`) y no tienen FIPS válido: se descartan en `produccion_anual.csv` y se anota en el data card. Para el FIPS de 5 dígitos conviene usar `state_ansi` + `county_ansi`, no `county_code`.

**(D) y otros códigos.** Las publicaciones de NASS usan la misma nota al pie: "- Represents zero. (D) Withheld to avoid disclosing data for individual operations. (NA) Not available." En Quick Stats el código viene en la columna `Value` en lugar del número. Según el CLAUDE.md §4, `(D)` y `(Z)` van como celda vacía con el código original en `flag_nass`. No encontré en esta ronda una fuente HTML que defina `(Z)` (la definición habitual, "menos de la mitad de la unidad", es la del CLAUDE.md).

**Condado 2024 y 2025.**
- 9 de abril de 2024: NASS suspende las "County Estimates for Crops and Livestock beginning with the 2024 production year" por presupuesto.
- 19 de marzo de 2025: NASS las repone. Para los cultivos en surco (maíz, soja, sorgo, algodón, maní, arroz) desde la cosecha 2024; para los cereales finos (cebada, avena, trigo) desde la cosecha 2025. Maíz, sorgo y soja de 2024 se programaron para el 6 de mayo de 2025.
- 28 de agosto de 2025: hubo otra baja de programas, pero el aviso solo nombra la encuesta de visones y la de mano de obra agrícola; no toca las estimaciones de condado.
- Mayo de 2026: farmdoc daily informa que NASS publicó los rendimientos de condado de 2025 de maíz, soja y trigo de invierno, con menos condados con dato que en 2024 por la caída de respuestas a las encuestas. El trigo de invierno de 2024 por condado solo existe para Illinois.
- 22 de junio de 2026: NASS agrega condados a las estimaciones de algodón de 2025 en Quick Stats (indica que el programa de condado de 2025 está cargado en Quick Stats).

Consecuencias para `cultivos`: 2024 de avena y trigo por condado va a faltar (salvo trigo en Illinois); 2025 existe pero con más faltantes. Hay que bajar con la API (o la base completa) y medir la cobertura real por cultivo y año, sin rellenar.

Fuentes: [Quick Stats API – documentación (USDA NASS)](https://quickstats.nass.usda.gov/api), consultado 2026-11-14; [NASS reinstates select data collection programs and reports (aviso del 2025-03-19)](https://www.nass.usda.gov/newsroom/notices/2025/03-19-2025), consultado 2026-11-14; [NASS discontinues select 2024 data collection programs and reports (aviso del 2024-04-09)](https://www.nass.usda.gov/newsroom/notices/2024/04-09-2024), consultado 2026-11-14; [NASS discontinues select data collection programs and reports (aviso del 2025-08-28)](https://www.nass.usda.gov/newsroom/notices/2025/08-28-2025), consultado 2026-11-14; [NASS Adds Additional Counties to the 2025 Cotton County-level Estimates (2026-06-22)](https://www.nass.usda.gov/newsroom/notices/2026/06-22-2026), consultado 2026-11-14; [2025 NASS County Corn, Soybean, and Winter Wheat Yields (farmdoc daily, mayo 2026)](https://farmdocdaily.illinois.edu/2026/05/2025-nass-county-corn-soybean-and-winter-wheat-yields.html), consultado 2026-11-14; [Agronomic Yields – County, State and Regional (KBS LTER)](https://lter.kbs.msu.edu/datatables/85), consultado 2026-11-14; [Cotton Ginnings, NASS (nota al pie de (D))](https://esmis.nal.usda.gov/sites/default/release-files/796115/ctgn4326.txt), consultado 2026-11-14

Confianza: media (alta para condados combinados, (D) y la situación de 2024–2025; media para los `short_desc` de superficie cosechada, producción, avena y heno, que siguen la regla documentada pero no se verificaron uno por uno).

Impacto: paquete `cultivos` (`src/cultivos/download.py` y `process.py`, `produccion_anual.csv`): filtrar `county_code` 998, armar `fips` con `state_ansi` + `county_ansi`, mapear `(D)`/`(Z)` a vacío con `flag_nass`, pedir por estado y cultivo con `get_counts` antes, y esperar faltantes en avena y trigo de 2024 y en 2025 en general. Data card `docs/datasets/cultivos.md` (Supuestos y Problemas conocidos).

Citas:
> "county_code 3 NASS 3-digit county codes; includes 998 for Other (Combined) Counties and Alaska county codes; otherwise match ANSI codes." — [Quick Stats API – documentación (USDA NASS)](https://quickstats.nass.usda.gov/api)
> "The county estimate reinstatement is effective for the 2024 crop season for the row crops (corn, cotton, peanuts, rice, sorghum, soybeans) and for the 2025 crop season for the small grain crops (barley, oats, wheat)." — [NASS reinstates select data collection programs and reports](https://www.nass.usda.gov/newsroom/notices/2025/03-19-2025)
> "a concatenation of six columns: commodity_desc, class_desc, prodn_practice_desc, util_practice_desc, statisticcat_desc, and unit_desc." — [Quick Stats API – documentación (USDA NASS)](https://quickstats.nass.usda.gov/api)
> "(D) Withheld to avoid disclosing data for individual operations." — [Cotton Ginnings, NASS](https://esmis.nal.usda.gov/sites/default/release-files/796115/ctgn4326.txt)
> "recently released 2025 county yield estimates for corn, soybeans, and winter wheat." — [2025 NASS County Corn, Soybean, and Winter Wheat Yields (farmdoc daily)](https://farmdocdaily.illinois.edu/2026/05/2025-nass-county-corn-soybean-and-winter-wheat-yields.html)
> "corn, grain - yield, measured in bu / acre" — [Agronomic Yields – County, State and Regional (KBS LTER)](https://lter.kbs.msu.edu/datatables/85)
