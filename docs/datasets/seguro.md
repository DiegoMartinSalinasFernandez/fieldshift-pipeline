# Data card — paquete `seguro`

Seguro agrícola federal de EE.UU. (USDA Risk Management Agency, RMA) por condado, año de cosecha y
cultivo: participación (superficie asegurada, responsabilidad, prima), indemnizaciones y su
causa, y el mes de la pérdida. Implementa la propuesta de `docs/research/rma_causa_perdida.md`
(T016). Generado por `src/seguro/process.py`: no editar a mano, se reescribe en cada corrida.

**Esquema nuevo, pendiente de OK del humano** (`coordinacion/para_decidir.md`, fila 6). No está
en `loop/spec/entregables.yaml` ni en `src/merge.py`.

## Fuentes

| Archivo en `data/raw/seguro/` | Producto | URL |
|---|---|---|
| `colsom_<AAAA>.zip` (2000–2025) | Cause of Loss Summary of Business with Month of Loss | https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/ |
| `sobtpu_<AAAA>.zip` (2000–2025) | Summary of Business por tipo, práctica y estructura de unidad | https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop/ |
| `COL_Summary_of_Business_with_Month_All_Years.pdf`, `Stage_Code_Listing.pdf`, `SOBTPU_External_All_Years.pdf` | diccionarios oficiales | mismos directorios |

Licencia: CC0 1.0 (data.gov). Los zips son nacionales; el filtro por estado
(`FIELDSHIFT_ESTADOS`) y por cultivo se hace al procesar. Formato verificado al bajar: un `.txt`
por zip, separador `|`, **sin encabezado**, 30 columnas (colsom) y 27 (sobtpu), campos de texto
rellenos con espacios; colsom termina las líneas con CRLF y sobtpu con CR solo.

## Cultivos

| `cultivo` | Código RMA | Nota |
|---|---|---|
| `maiz` | 0041 CORN | todos los tipos (Grain, High Amylose, White, Waxy...); no incluye 0042 sweet corn, 0043 popcorn ni 0062 semilla híbrida |
| `soja` | 0081 SOYBEANS | |
| `trigo` | 0011 WHEAT | **invierno y primavera juntos**: el archivo de causas no tiene tipo. `trigo_frac_invierno` (de sobtpu) dice qué parte de la superficie asegurada es de invierno |
| `avena` | 0016 OATS | poco asegurada: muchos condados sin filas |

## Archivos y columnas

Claves: `fips, anio, cultivo` (anual) y `fips, anio, mes, cultivo` (mensual).

| Archivo | Columna | Descripción | Unidad | Fuente | Desde | Hasta | % faltantes |
|---|---|---|---|---|---|---|---|
| seguro_anual.csv | sup_asegurada_ac | Superficie asegurada neta (Net Reporting Level Amount × participación), solo filas con Reporting Level Type = Acres; suma de planes, coberturas, tipos y prácticas | acres | USDA RMA Summary of Business (sobtpu) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | sup_asegurada_secano_ac | Parte de sup_asegurada_ac en prácticas de secano (Non-Irrigated, Summerfallow, Continuous Cropping y variantes) | acres | USDA RMA Summary of Business (sobtpu) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | sup_asegurada_riego_ac | Parte de sup_asegurada_ac en prácticas con riego (Irrigated, Irr., Limited Irrigation) | acres | USDA RMA Summary of Business (sobtpu) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | responsabilidad_usd | Responsabilidad (liability): monto máximo asegurado, todos los planes (incluidos los endosos de área) | USD | USDA RMA Summary of Business (sobtpu) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | prima_total_usd | Prima total antes de subsidios | USD | USDA RMA Summary of Business (sobtpu) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indemnizacion_usd | Indemnización total | USD | USDA RMA Summary of Business (sobtpu) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | loss_ratio | indemnizacion_usd / prima_total_usd (vacío si la prima es 0) | proporción | USDA RMA Summary of Business (sobtpu) | 2000 | 2025 | 14.1 |
| seguro_anual.csv | loss_cost | indemnizacion_usd / responsabilidad_usd (vacío si la responsabilidad es 0) | proporción | USDA RMA Summary of Business (sobtpu) | 2000 | 2025 | 14.1 |
| seguro_anual.csv | sup_con_perdida_ac | Superficie con pérdida (Net Determined Quantity), suma de todas las causas | acres | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_causas_usd | Indemnización total del archivo de causas (suma de los grupos) | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_sequia_usd | Indemnización por sequía (causa 11) | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_exceso_agua_usd | Indemnización por exceso de humedad o lluvia e inundación (31, 51) | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_calor_usd | Indemnización por calor y viento caliente (12, 62) | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_granizo_usd | Indemnización por granizo (21) | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_helada_usd | Indemnización por helada, congelamiento e invierno frío (41, 42, 43) | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_frio_humedo_usd | Indemnización por tiempo frío y húmedo (44) | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_viento_usd | Indemnización por viento, ciclón, tornado y huracán (61, 63, 64, 92) | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_enfermedad_plagas_usd | Indemnización por roya asiática, insectos, enfermedades y micotoxinas (09, 71, 81, 82) | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_precio_usd | Indemnización por baja de precio (01; seguros de ingreso). No es clima | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_area_usd | Indemnización de planes de área (55: ARPI, SCO, ECO, STAX, MP...). Sin causa física | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | indem_otras_usd | Indemnización por el resto de las causas (riego 13-15, incendio, fauna, 99, XX 'All Other Causes', códigos no listados) | USD | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 6.2 |
| seguro_anual.csv | frac_indem_clima | (sequía + exceso de agua + calor + granizo + helada + frío húmedo + viento) / indem_causas_usd; vacío si el total es ≤ 0 | proporción | USDA RMA Cause of Loss (colsom) | 2000 | 2025 | 23.1 |
| seguro_anual.csv | trigo_frac_invierno | Solo cultivo = trigo: fracción de sup_asegurada_ac con Type Name = Winter | proporción | USDA RMA Summary of Business (sobtpu) | 2000 | 2025 | 75.1 |
| seguro_mensual.csv | indem_sequia_usd | Indemnización por sequía (11) con pérdida en ese mes | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_exceso_agua_usd | Ídem, exceso de agua (31, 51) | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_calor_usd | Ídem, calor (12, 62) | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_granizo_usd | Ídem, granizo (21) | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_helada_usd | Ídem, helada (41, 42, 43) | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_frio_humedo_usd | Ídem, frío húmedo (44) | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_viento_usd | Ídem, viento (61, 63, 64, 92) | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_enfermedad_plagas_usd | Ídem, enfermedad y plagas (09, 71, 81, 82) | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_precio_usd | Ídem, baja de precio (01) | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_area_usd | Ídem, planes de área (55) | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_otras_usd | Ídem, resto de las causas | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | indem_total_usd | Suma de los grupos | USD | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |
| seguro_mensual.csv | sup_con_perdida_ac | Superficie con pérdida en ese mes (Net Determined Quantity) | acres | USDA RMA Cause of Loss (colsom) | 2002 | 2025 | 0.0 |

## Causas → grupos

Códigos del Exhibit 10 del manual FCIC-25010 (2026). Se agrupa por el código (columna 12), no
por la descripción.

| Código | Causa (RMA) | Grupo (`indem_<grupo>_usd`) |
|---|---|---|
| 01 | Decline in Price | precio |
| 09 | Asian Soybean Rust | enfermedad_plagas |
| 11 | Drought | sequia |
| 12 | Heat | calor |
| 13, 14, 15 | Failure of Irrigation Supply / Equipment, Inability to prepare land for irrigation | otras |
| 21 | Hail | granizo |
| 31 | Excess Moisture/Precipitation/Rain | exceso_agua |
| 41 | Frost | helada |
| 42 | Freeze | helada |
| 43 | Cold Winter | helada |
| 44 | Cold Wet Weather | frio_humedo |
| 51 | Flood | exceso_agua |
| 55 | ARPI/SCO/ECO/STAX/MP/HIP-WI/PACE Crops Only | area |
| 61 | Wind/Excess Wind | viento |
| 62 | Hot Wind | calor |
| 63 | Cyclone | viento |
| 64 | Tornado | viento |
| 71 | Insects | enfermedad_plagas |
| 81 | Plant Disease | enfermedad_plagas |
| 82 | Mycotoxin | enfermedad_plagas |
| 92 | Hurricane / Tropical Storm | viento |
| 85, 87, 91, 93, 97, 98, 99 | Ordered Destruction, Falling Numbers, Fire, Wildlife, Earthquake, Volcano, Other | otras |
| XX | All Other Causes | otras |
| cualquier otro | códigos viejos o nuevos no listados | otras |

Códigos de causa que aparecieron en los datos procesados, con su indemnización total:

| Código | Descripción en los datos | Grupo | Filas | Indemnización (USD) |
|---|---|---|---|---|
| 01 | Decline in Price | precio | 18225 | 334,560,689 |
| 09 | Asian Soybean Rust | enfermedad_plagas | 20 | 122,034 |
| 11 | Drought | sequia | 84045 | 6,937,888,418 |
| 12 | Heat | calor | 20629 | 1,087,733,442 |
| 13 | Failure Of Irrigation Supply; Failure of Irrigation Supply | otras | 445 | 8,249,075 |
| 14 | Failure Of Irrigation Equipment; Failure of Irrigation Equipment | otras | 136 | 3,300,258 |
| 15 | Inability to Prepare Land for Irrigation | otras | 24 | 268,542 |
| 21 | Hail | granizo | 19327 | 1,105,757,679 |
| 31 | Excess Moisture/Precipitation/Rain | exceso_agua | 37837 | 782,184,216 |
| 41 | Frost | helada | 1632 | 15,908,214 |
| 42 | Freeze | helada | 10288 | 495,160,003 |
| 43 | Cold Winter | helada | 7794 | 165,498,623 |
| 44 | Cold Wet Weather | frio_humedo | 2642 | 20,990,425 |
| 51 | Flood | exceso_agua | 4782 | 74,335,422 |
| 55 | ARPI Crops Only; ARPI/SCO/ECO/STAX/MP/HIP WI Crops Only; ARPI/SCO/ECO/STAX/MP/HIP-WI/PACE Crops Only; ARPI/SCO/ECO/STAX/MP/PACE Crops Only; ARPI/SCO/STAX Crops Only; ARPI/SCO/STAX/MP Crops Only; ARPI/SCO/STAX/MP/HIP WI Crops Only; GRP/GRIP  Crops Only; GRP/Grip Crops | area | 1653 | 201,014,998 |
| 61 | Wind/Excess Wind | viento | 5849 | 163,556,958 |
| 62 | Hot Wind | calor | 8862 | 275,113,298 |
| 63 | Cyclone | viento | 65 | 322,309 |
| 64 | Tornado | viento | 157 | 1,200,063 |
| 71 | Insects | enfermedad_plagas | 1239 | 5,500,706 |
| 81 | Plant Disease | enfermedad_plagas | 3543 | 49,560,547 |
| 82 | Mycotoxin; Mycotoxin (Aflatoxin) | enfermedad_plagas | 501 | 44,173,028 |
| 87 | Falling Numbers | otras | 6 | 46,278 |
| 91 | Fire | otras | 117 | 530,803 |
| 92 | Hurricane/Tropical Depression | viento | 9 | 21,771 |
| 93 | Wildlife | otras | 966 | 3,311,262 |
| 97 | Earthquake | otras | 23 | 63,772 |
| 98 | Volcanic Eruption | otras | 2 | 17,391 |
| 99 | Other (Snow, Lightning, Etc.); Other (Snow,Lightning,etc) | otras | 2182 | 14,775,651 |
| XX | All Other Causes | otras | 1407 | 24,373,284 |

## Cobertura de esta corrida

- Estados: KS.
- Filas: `seguro_anual.csv` 10,920 (grilla completa condado × año × cultivo), de las cuales
  10,241 tienen participación o pérdidas; `seguro_mensual.csv` 49,297.
- Años con datos: 2000–2025.
- Archivos que faltaban en raw: ninguno.

Condados con superficie asegurada > 0, por estado, cultivo y algunos años:

| Estado | Cultivo | 2000 | 2005 | 2010 | 2015 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| KS | avena | 61 | 63 | 40 | 40 | 32 | 46 | 35 |
| KS | maiz | 104 | 105 | 105 | 105 | 105 | 105 | 105 |
| KS | soja | 103 | 103 | 105 | 101 | 102 | 100 | 98 |
| KS | trigo | 104 | 105 | 105 | 105 | 105 | 104 | 104 |

Comparación entre las dos fuentes (indemnización total de los estados procesados, todos los años):
sobtpu 11,818,805,956 USD, colsom 11,815,539,159 USD.

## Condados que no están en `condados.csv`

RMA usa códigos FIPS de estado y condado. Las filas cuyo `fips` no está en
`data/reference/condados.csv` se **descartan** (no hay a qué condado asignarlas). Son sobre todo
el código 999 "All Other Counties" (agrupa condados con poca actividad, como el 998 de NASS).
Lo descartado en esta corrida:

| Archivo | fips | Condado (RMA) | Filas | Indemnización (USD) |
|---|---|---|---|---|
| — | — | ninguna fila descartada en esta corrida | 0 | 0 |

## Faltantes y ceros

- Celda vacía = no hay dato (CLAUDE.md §4).
- En `seguro_anual.csv`, si el condado no tiene filas en sobtpu **ni** en colsom para ese año y
  cultivo, toda la fila queda vacía (sin participación en el seguro).
- **Excepción al "nunca 0"**: si el condado tiene filas en sobtpu o en colsom, la indemnización de
  los grupos de causa sin filas es **0**. Es un dato real (no hubo pérdidas por esa causa), no un
  relleno: el archivo de causas solo lista las combinaciones que existen. Lo mismo para
  `sup_con_perdida_ac`.
- `sup_asegurada_*`, `responsabilidad_usd`, `prima_total_usd` e `indemnizacion_usd` quedan vacías
  cuando no hay filas en sobtpu (aunque haya pérdidas en colsom).
- `loss_ratio`, `loss_cost` y `frac_indem_clima` quedan vacías cuando el denominador es 0 o
  vacío. `trigo_frac_invierno` está vacía salvo en `trigo`.
- `seguro_mensual.csv` solo tiene los meses con alguna pérdida registrada; un mes que no está
  significa que no hubo indemnizaciones con pérdida en ese mes.

## Supuestos

- `anio` (anual) = Commodity Year de RMA, el año de cosecha de la póliza.
- En `seguro_mensual.csv`, `mes` = Year of Loss + Month of Loss y `anio` es el año de ese mes. Si
  un mes recibe pérdidas de dos años de cosecha (trigo de invierno dañado en otoño), se suman. Se
  descartaron las filas sin mes o sin año de pérdida válidos (36428 filas, 567,750,452
  USD). En los años de cosecha 2000, 2001, 2002 el archivo de RMA trae el mes pero deja vacío el
  Year of Loss en todas las filas: esos años no tienen filas en el mensual (no se adivina el año
  de un mes que puede ser del otoño anterior). También se descartaron las que tienen un
  año de pérdida a más de un año del de cosecha (511 filas, 2,370,162 USD; p. ej.
  trigo de 2023 con pérdida en 2003, errores evidentes de carga). En el anual sí cuentan.
- La superficie asegurada suma todos los planes; los endosos y planes de área (SCO, ECO, MP...)
  vienen con 0 acres en sobtpu y no la duplican, pero su responsabilidad, prima e indemnización
  sí se suman.
- Práctica → riego/secano por el nombre (Practice Name), no por el código: "Non-Irr..." es
  secano, "...Irr..." es riego, "Summerfallow" y "Continuous Cropping" (trigo de las Grandes
  Llanuras) son secano; "No Practice Specified" y otras quedan solo en el total. Por eso
  riego + secano puede ser menor que el total.
- Las columnas de participación del archivo de causas (17, 19–27) no se usan: el denominador sale
  de sobtpu (research T016).
- No se quita la tendencia de la participación ni se calculan percentiles o z-scores (lo decide
  ML).

## Problemas conocidos

- El archivo de causas no separa riego de secano: en NE y KS la indemnización por sequía de un
  condado se diluye en una responsabilidad que incluye superficie regada.
- `trigo` junta invierno y primavera (en MN es sobre todo trigo de primavera).
- RMA revisa los años recientes (2022–2026 se actualizaron el 2026-11-09); la fecha
  Last-Modified de cada zip queda en `manifest.csv`. Para tomar una revisión nueva, borrar el zip
  de `data/raw/seguro/` y volver a bajar.
- Montos en dólares corrientes, sin deflactar.
- La participación en el seguro creció mucho desde 2000: comparar entre años con `loss_cost` o
  con `sup_con_perdida_ac / sup_asegurada_ac`, no con montos absolutos.
