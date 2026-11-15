# USDA RMA: causas de pérdida del seguro agrícola (Cause of Loss) y Summary of Business por condado

Pregunta: ¿Dónde y cómo se bajan los datos de "Cause of Loss" y "Summary of Business" del USDA Risk Management
Agency (RMA) por condado, cultivo y año? ¿Sirven para maíz, soja, trigo de invierno y avena en los 7 estados
(IA, IL, IN, OH, NE, MN, KS)? ¿Qué licencia y qué limitaciones tienen? ¿Qué columnas convendría bajar?

Respuesta corta:
- **Cause of Loss** (indemnizaciones por causa, con mes de pérdida): un zip anual por año de cosecha,
  `colsom_<AAAA>.zip`, de 1989 a 2026, en
  `https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/`. Texto separado por `|`,
  sin encabezado documentado, 30 columnas con diccionario oficial (PDF y DOC, versión del 2026-05-28). Claves:
  FIPS de estado (2) y de condado (3) por separado, código de cultivo RMA (4 dígitos), plan de seguro, categoría
  de cobertura, etapa, código de causa (2 dígitos), mes y año de la pérdida.
- **Summary of Business** por condado (el denominador), en
  `https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop/`, en dos versiones:
  - `sobcov_<AAAA>.zip`, de 1989 a 2027: por condado, cultivo, plan y nivel de cobertura (28 columnas);
  - `sobtpu_<AAAA>.zip`, de 1999 a 2027: suma además tipo, **práctica (riego o secano)** y estructura de unidad
    (27 columnas).

  Las dos traen superficie asegurada, responsabilidad (`liability`), primas, subsidio e indemnización.
- Códigos de cultivo de RMA: maíz `0041`, soja `0081`, trigo `0011` (invierno y primavera juntos), avena
  `0016`. El de causa sale del Exhibit 10 del manual FCIC-25010 de 2026: sequía 11, calor 12, granizo 21,
  exceso de humedad 31, helada 41, congelamiento 42, etc. (tabla abajo).
- Licencia: data.gov la lista como CC0 1.0 (dominio público). No encontré ninguna regla de ocultamiento por
  confidencialidad parecida al `(D)` de NASS.
- Sirve para riesgo y para validar el clima, pero hay que tener en cuenta tres cosas:
  - el archivo de causas **no separa riego de secano** ni el trigo de invierno del de primavera;
  - la causa "baja de precio" (01) no tiene que ver con el clima;
  - la participación en el seguro cambia mucho con los años. Por eso conviene normalizar por la
    responsabilidad (`loss cost` = indemnización / responsabilidad) y no usar montos absolutos.
- **No bajé los datos**, así que no pude medir qué tan completo está cada condado. Queda como primer paso de
  la descarga (ver "Propuesta").

## Detalle

### 1. Cause of Loss: archivos y formato

Directorio actual (lo abrí el 2026-11-15): `https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/`

- `colsom_1989.zip` … `colsom_2026.zip`, entre 1,8 y 6,2 MB comprimidos cada uno. Los de 2022 a 2026 se
  actualizaron el 2026-11-09, el de 2021 el 2025-11-24 y los anteriores el 2025-04-09. Los años recientes se
  van revisando a medida que entran reclamos, así que el último año completo y cerrado es, como mucho, 2025.
  No encontré una fecha oficial de cierre ni la frecuencia de actualización.
- Diccionario: `COL_Summary_of_Business_with_Month_All_Years.pdf` (y `.doc`) en el mismo directorio, "As of
  5/28/2026". Lo leí entero. Dice: "The files are created in a pipe (|) delimited format".
- Etapas: `Stage_Code_Listing.pdf` / `.xlsx` (actualizado el 24-Feb-2026), con la historia de los códigos de
  etapa desde 1989.
- La página vieja de RMA (`https://www.rma.usda.gov/legacy/data/cause.html`) ofrecía además "Indemnities
  Only" e "Indemnities with Month of Loss" (zips de 1989 a 2018, otros diseños de registro) y avisaba de un
  "technical problem with the COL Summary of Business with Month of Loss online data files" ya resuelto para
  2001–2016. **El directorio `pubfs` actual sirve como fuente única**: tiene todos los años en un diseño
  uniforme.
- No abrí el contenido de ningún zip. No sé si la primera fila trae encabezado ni cómo se llama el `.txt`
  de adentro: hay que verificarlo al bajar.

**Columnas** (las 30 del diccionario oficial; formato `9` = numérico, `X` = texto, `V` = decimales):

| # | Columna | Formato | Nota |
|---|---|---|---|
| 1 | Commodity Year Identifier | 9(04) | año de cosecha / de la póliza → `anio` |
| 2 | State Code | 9(02) | FIPS de estado |
| 3 | State Abbreviation | X(02) | |
| 4 | County Code | 9(03) | FIPS de condado → `fips` = estado + condado, con ceros a la izquierda |
| 5 | County Name | X(30) | |
| 6 | Commodity Code | 9(04) | código de cultivo RMA |
| 7 | Commodity Name | X(30) | |
| 8 | Insurance Plan Code | 9(02) | APH, RP, YP, ARP, SCO… |
| 9 | Insurance Plan Name Abbreviation | X(05) | |
| 10 | Coverage Category | X(01) | A = Buyup, C = CAT, E = Existing, L = Limited |
| 11 | Stage Code | X(02) | ver Stage Code Listing (p. ej. `H` cosechado, `FL` pago final) |
| 12 | Cause of Loss Code | 9(02) | ver tabla de causas |
| 13 | Cause of Loss Description | X(35) | |
| 14 | Month of Loss | 9(02) | |
| 15 | Month of Loss Name | X(03) | |
| 16 | Year of Loss | 9(04) | puede ser distinto del año de cosecha (p. ej., el trigo de invierno dañado en otoño) |
| 17 | Policies Earning Premium | 9(09) | sin conteo para el plan CLIP |
| 18 | Policies Indemnified | 9(09) | |
| 19 | Net Planted Quantity | 9(12)V9(02) | acres (o la unidad del cultivo) × participación del asegurado |
| 20 | Net Endorsed Acres | 9(12)V9(02) | acres bajo endosos (SCO, STAX, Margin Protection) |
| 21 | Liability | 9(12) | USD, monto máximo asegurado |
| 22 | Total Premium | 9(12) | USD, prima antes de subsidios |
| 23 | Producer Paid Premium | 9(12) | USD |
| 24 | Subsidy | 9(12) | USD |
| 25 | State/Private Subsidy | 9(12) | USD |
| 26 | Additional Subsidy | 9(12) | USD; en 2021–2022 es el Pandemic Cover Crop Program |
| 27 | EFA Premium Discount | 9(12) | USD |
| 28 | Net Determined Quantity | 9(12)V9(02) | **acres con pérdida** (o la unidad del cultivo) × participación |
| 29 | Indemnity Amount | S9(12) | USD, puede ser negativo (ajustes) |
| 30 | Loss Ratio | 9(5)V9(02) | indemnización / prima total |

Ojo: cada fila es una combinación condado × cultivo × plan × categoría × etapa × causa × mes. Las columnas
de participación (19–27) vienen repetidas en las filas de distintas causas o meses del mismo grupo, o
asignadas de una forma que el diccionario no explica. **No hay que sumar `Liability` ni `Total Premium` del
archivo de causas para sacar un denominador.** Para eso está el Summary of Business (sección 2). Esto es una
inferencia del diseño de las filas y hay que comprobarlo al bajar los datos.

**Códigos de causa** (Exhibit 10 del Loss Adjustment Standards Handbook FCIC-25010, enero de 2026; solo los
que pueden aplicar a cultivos extensivos):

| Código | Causa | Grupo propuesto |
|---|---|---|
| 00 | No Indemnity | — |
| 01 | Decline of Price (revenue protection: precio de cosecha menor al proyectado) | precio |
| 09 | Asian Soybean Rust (solo soja) | enfermedad |
| 11 | Drought (no se puede declarar en práctica bajo riego) | sequía |
| 12 | Heat | calor |
| 13 | Failure of Irrigation Supply | riego |
| 14 | Failure of Irrigation Equipment | riego |
| 15 | Inability to prepare land for irrigation | riego |
| 21 | Hail | granizo |
| 31 | Excess Moisture/Precip/Rain | exceso de agua |
| 41 | Frost | helada |
| 42 | Freeze | helada |
| 43 | Cold Winter | invierno (trigo de invierno) |
| 44 | Cold Wet Weather | frío húmedo |
| 51 | Flood | exceso de agua |
| 55 | ARPI Crops Only (planes de área: ARP, SCO, STAX, MP…) | sin causa física |
| 61 | Wind/Excess Wind | viento |
| 62 | Hot Wind | calor |
| 63 | Cyclone | viento |
| 64 | Tornado | viento |
| 71 | Insects | plagas |
| 81 | Plant Disease | enfermedad |
| 82 | Mycotoxins (Aflatoxin, Vomitoxin) | enfermedad |
| 85 | Federal or State Ordered Destruction | otros |
| 87 | Falling Numbers (solo trigo) | otros |
| 91 | Fire | otros |
| 92 | Hurricane / Tropical Depression / Tropical Storm | viento |
| 93 | Wildlife | otros |
| 97, 98 | Earthquake, Volcanic Eruption | otros |
| 99 | Other (Snow, Lightning, Etc.) | otros |

La nota 2/ del Exhibit 10 dice que cuando la póliza cubre "adverse weather", RMA exige desglosarlo en la causa
específica (sequía, etc.) con fines estadísticos. Esta es la versión de 2026: los códigos de años viejos
pueden diferir (en 2000 ya existían 01, 21 y 31, según el Exhibit 21-2 de FCIC-M13). Conviene leer siempre la
descripción (columna 13) y no solo el código, y revisar en los datos si en 2000–2025 aparecen códigos que no
están en esta tabla.

### 2. Summary of Business por condado (el denominador)

Directorio: `https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop/` (lo abrí el 2026-11-15).

**a) `sobcov_<AAAA>.zip`, de 1989 a 2027** (entre 0,5 y 3,3 MB por año). Diccionario:
`SOB_State_County_Crop_with_Coverage_Level_1989_Forward.pdf` (5/28/2026). Separado por `|`. Son 28 columnas:
- claves y nombres: Commodity Year, Location State Code (FIPS), State Abbreviation, Location County Code
  (FIPS), County Name, Commodity Code/Name, Insurance Plan Code/Abbreviation, Coverage Category, Delivery Type
  (RCAT/RBUP/FCAT/FBUP), Coverage Level (decimal);
- conteos: Policies Sold, Policies Earning Premium, Policies Indemnified, Units Earning Premium, Units
  Indemnified;
- cantidades: **Quantity Type** (Acres, Tons…), **Net Reported Quantity** (acres asegurados × participación),
  Endorsed/Companion Acres;
- montos en USD: **Liability**, **Total Premium**, Subsidy, State/Private Subsidy, Additional Subsidy, EFA
  Premium Discount, **Indemnity**, Loss Ratio.

**b) `sobtpu_<AAAA>.zip`, de 1999 a 2027** (entre 3 y 9 MB por año). Diccionario: `SOBTPU_External_All_Years.pdf`.
Separado por `|`. Tiene 27 columnas: las mismas claves que (a) más Type Code/Name, **Practice Code/Name**
("irrigated, non-irrigated, no practice specified"), Unit Structure Code/Name, Net Reporting Level Amount,
Reporting Level Type, Liability, Total Premium, Subsidy, Indemnity, Loss Ratio y Endorsed Commodity Reporting
Level Amount.

**Para Nebraska y Kansas, `sobtpu` es la única de estas fuentes que separa riego de secano**, y también la
única que separa trigo de invierno de trigo de primavera (por `Type Name`). Pero no tiene causa de pérdida.
No pude confirmar en una fuente actual los códigos numéricos de tipo y práctica. El memo R&D-99-023 de RMA
(1999) usa en sus ejemplos tipo `011` para trigo de invierno, `012` para trigo de primavera y `016` para maíz
grano; práctica `002` = riego, `003` = secano, `004` = cultivo continuo y `005` = barbecho de verano; y `NTS`/`NPS`
= sin tipo o sin práctica especificados (trigo de Kansas). Ojo: en Kansas existen las prácticas de cultivo
continuo y de barbecho, que no son "riego" ni "secano" a secas. Como el archivo trae los nombres, conviene filtrar por
`Type Name` y `Practice Name` y no por código.

Los archivos de 2026 y 2027 están en curso (son pólizas de la campaña actual y la próxima): no usarlos.

### 3. Cultivos y estados

Códigos verificados en el listado oficial `CommodityCode2014.pdf` de RMA:

| Cultivo del proyecto | Código RMA | Nombre RMA | Nota |
|---|---|---|---|
| maíz | 0041 | CORN | aparte: 0062 HYBRID CORN SEED, 0042 SWEET CORN, 0043 POPCORN (no incluir) |
| soja | 0081 | SOYBEANS | |
| trigo de invierno | 0011 | WHEAT | invierno y primavera juntos; en Cause of Loss **no hay columna de tipo** |
| avena | 0016 | OATS | |
| alfalfa / heno | 0033 FORAGE PRODUCTION, 0032 FORAGE SEEDING; 0088 PRF (pasturas, por índice) | | PRF es un seguro por índice de lluvia: sus indemnizaciones no son pérdidas observadas |
| centeno | 0094 | RYE | |

Los 7 estados del proyecto usan los mismos códigos FIPS de estado y condado que el resto del repo (los dos
diccionarios dicen que son FIPS). Cobertura:
- **Maíz y soja**: el seguro está muy extendido en el Corn Belt, así que es razonable esperar datos en casi
  todos los condados y años. **No lo verifiqué con datos.**
- **Trigo**: en MN el trigo es sobre todo de primavera, así que el trigo de Cause of Loss de MN no sirve como
  "trigo de invierno" sin repartirlo con `sobtpu`. En KS, NE, IL, IN, OH e IA casi todo el trigo es de invierno
  (conocimiento general, confianza media; se puede comprobar con `sobtpu`).
- **Avena**: superficie chica y poco asegurada. Hay que esperar muchos condados sin filas, o con filas solo en
  algunos años.

### 4. Licencia y limitaciones

- **Licencia**: el registro de data.gov "Cause of Loss Historical Files" (USDA) dice CC0 1.0, acceso
  `public`. Son datos del gobierno federal de EE.UU.
- **Datos ocultos**: ninguno de los dos diccionarios menciona supresión por confidencialidad. Que falte un
  condado probablemente significa que no hubo pólizas o que no hubo pérdidas (en el archivo de causas solo
  aparecen las combinaciones que existen). **No es un faltante**: si hay participación (en SOB) y no hay fila
  de causa, la indemnización es 0. Esto es una inferencia y hay que confirmarlo con los datos.
- **Cambios entre años**:
  - los códigos de etapa cambian mucho entre años: en 1989–1994 hay códigos que después no existen (ver Stage
    Code Listing);
  - aparecen causas nuevas (09 roya asiática, 55 planes de área, 87 falling numbers, 89 humo);
  - los planes de seguro cambiaron: de APH/CRC/RA/IP/GRP a YP/RP/RP-HPE y ARP/SCO/STAX/ECO desde 2011.
  Si se agrega por cultivo y causa, sumando todos los planes, se evita casi todo el problema.
- **Revenue Protection**: desde 2011 (y antes con CRC/RA) una parte de la indemnización viene de la baja de
  precio (causa 01). No es clima: se separa.
- **Planes de área** (causa 55): pagan según el rendimiento o el ingreso del condado, sin causa física. Se
  separan.
- **Participación variable**: la superficie asegurada y el nivel de cobertura subieron mucho desde 2000 (ley
  ARPA). Los montos absolutos no se comparan entre años: hay que usar `loss cost` (indemnización / liability)
  o acres con pérdida / acres asegurados.
- **Año de cosecha y año de pérdida**: `Commodity Year` es el año de cosecha (coincide con `anio`), y
  `Year of Loss` + `Month of Loss` dan la fecha real del daño. Para el trigo de invierno puede ser el otoño
  anterior.
- **Riego**: en el archivo de causas, la sequía (11) no puede ser la causa en lotes bajo riego. En NE y KS, el
  porcentaje de indemnización por sequía de un condado se diluye con la superficie regada (denominador de SOB
  con riego incluido). Para comparar con Iowa, usar el denominador de secano de `sobtpu` (aproximado, porque
  el numerador de causas no se puede separar).
- **Revisiones**: los archivos de años recientes se reemplazan (2022–2026 se actualizaron el 2026-11-09).
  Hay que registrar la fecha de descarga en `manifest.csv`.
- **Tamaño**: de 2000 a 2025, `colsom` suma unos 125 MB comprimidos, `sobcov` unos 65 MB y `sobtpu` unos
  150 MB (suma aproximada de los tamaños del listado). Muy por debajo del límite de 5 GB.
- **Alternativa**: AgRisk Viewer (NMSU, `https://agrisk.jornada.nmsu.edu/`) usa las mismas fuentes de RMA de
  1989 a 2025 y deja bajar texto filtrado por estado, condado, cultivo y causa. No hace falta: los zips de RMA
  son chicos y oficiales.

### 5. Propuesta concreta de qué bajar (sin bajarlo)

Paquete nuevo `seguro`. **Necesita el OK del humano**, porque agrega un paquete y un esquema de CSV. También
podría ir como un archivo más de `cultivos`.

**Bajar** (`src/seguro/download.py`, idempotente, a `data/raw/seguro/`):
1. `colsom_2000.zip` … `colsom_2025.zip`, más el diccionario y el Stage Code Listing.
2. `sobtpu_2000.zip` … `sobtpu_2025.zip`, más el diccionario. Con `sobtpu` alcanza: es más detallado que
   `sobcov` y se agrega igual.
3. Filtrar en el proceso, no en la descarga: State Code ∈ {19, 17, 18, 39, 31, 27, 20} (o los de
   `FIELDSHIFT_ESTADOS`), Commodity Code ∈ {0041, 0081, 0011, 0016}.

**Columnas a usar de `colsom`**: 1, 2, 4, 6, 8, 10, 12, 13, 14, 16, 18, 28, 29. Las de participación (17,
19–27) se ignoran: el denominador sale de `sobtpu`.

**Columnas a usar de `sobtpu`**: 1, 2, 5, 7, 9, 11, 15 (Type Name), 17 (Practice Name), 20, 21, 22, 23, 25.

**CSV propuestos** (contrato de la sección 4; `cultivo` = `maiz` | `soja` | `trigo` | `avena`):

`seguro_anual.csv` → `fips, anio, cultivo, ...`
- `sup_asegurada_ac` (Net Reporting Level Amount, solo donde Reporting Level Type = Acres)
- `sup_asegurada_secano_ac`, `sup_asegurada_riego_ac` (por Practice Name)
- `responsabilidad_usd`, `prima_total_usd`, `indemnizacion_usd`
- `loss_cost` = indemnizacion / responsabilidad; `loss_ratio` = indemnizacion / prima
- `sup_con_perdida_ac` (Net Determined Quantity sumado de `colsom`)
- `indem_sequia_usd` (11), `indem_calor_usd` (12, 62), `indem_exceso_agua_usd` (31, 51),
  `indem_granizo_usd` (21), `indem_helada_usd` (41, 42, 43), `indem_frio_humedo_usd` (44),
  `indem_viento_usd` (61, 63, 64, 92), `indem_enfermedad_plagas_usd` (09, 71, 81, 82),
  `indem_precio_usd` (01), `indem_area_usd` (55), `indem_otras_usd` (el resto)
- `frac_indem_clima` = (sequía + calor + exceso de agua + granizo + helada + frío húmedo + viento) / total
- `trigo_frac_invierno` (de `sobtpu`, por Type Name; solo cuando `cultivo` = `trigo`)

`seguro_mensual.csv` → `fips, anio, mes, cultivo, indem_sequia_usd, indem_exceso_agua_usd, indem_granizo_usd,
indem_helada_usd, indem_calor_usd, indem_total_usd, sup_con_perdida_ac`, donde `mes` = Year of Loss + Month
of Loss y `anio` = año calendario del mes (como pide el contrato). Sirve para validar contra `clima_mensual`
(SPI, `prec_max5d_mm`, días > 35 °C).

**Faltantes**: si el condado tiene participación en `sobtpu` y no tiene filas de causa, la indemnización por
causa es **0**, no vacía: ahí 0 es un dato real y no un relleno. Hay que documentarlo como excepción en el
data card. Sin participación, todo va vacío.

**Primer check al bajar** (para responder lo que este research no pudo): por estado y cultivo, contar los
condados con `sup_asegurada_ac` > 0 en cada año de 2000 a 2025, y compararlos con los condados con
`sup_sembrada_ac` de NASS en `produccion_anual.csv`. Anotar la cobertura en el data card.

**No hacer en el pipeline**: no quitar la tendencia de la participación ni calcular percentiles o z-scores
(los decide ML, como en el rendimiento).

## Lo que no encontré o no verifiqué

- Cuántos condados y años tienen datos (no bajé los datos).
- Si los `.txt` dentro de los zips traen encabezado, y cómo se llaman.
- La frecuencia oficial de actualización y la fecha de cierre de cada año.
- Si los códigos de tipo y práctica de 1999 siguen vigentes (en una fuente actual). Se usan los nombres.
- Si existen códigos de condado especiales (como el 998 de NASS) en los archivos de RMA.
- Cómo se reparten exactamente las columnas de participación entre las filas del archivo de causas.

Fuentes:
- [Directory Tree – pub/Web_Data_Files/Summary_of_Business/cause_of_loss/](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/index.html), consultado 2026-11-15
- [Cause of Loss Information – Summary of Business Data (record layout, As of 5/28/2026)](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/COL_Summary_of_Business_with_Month_All_Years.pdf), consultado 2026-11-15
- [History of Stage Codes 1989 Forward (24-Feb-2026)](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/Stage_Code_Listing.pdf), consultado 2026-11-15
- [Directory Tree – pub/Web_Data_Files/Summary_of_Business/state_county_crop/](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop/index.html), consultado 2026-11-15
- [Crop Insurance Experience with Coverage Level – 1989 Forward (record layout, 5/28/2026)](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop/SOB_State_County_Crop_with_Coverage_Level_1989_Forward.pdf), consultado 2026-11-15
- [Crop Insurance Experience – Coverage Level Type Practice Unit Structure (record layout)](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop/SOBTPU_External_All_Years.pdf), consultado 2026-11-15
- [2026 FCIC-25010 Loss Adjustment Standards Handbook, Exhibit 10 "Causes of Loss"](https://www.rma.usda.gov/sites/default/files/2026-01/2026-25010-Loss-Adjustment-Standards-Handbook.pdf), consultado 2026-11-15
- [RMA Commodity Code listing 2014](https://public.rma.usda.gov/apps/ReportShare//Extranet/SOB/Listings/CommodityCode2014.pdf), consultado 2026-11-15
- [RMA – Cause of Loss Historical Data Files (página vieja)](https://www.rma.usda.gov/legacy/data/cause.html), consultado 2026-11-15
- [data.gov – Cause of Loss Historical Files (licencia CC0)](https://catalog.data.gov/dataset/cause-of-loss-historical-files), consultado 2026-11-15
- [RMA Informational Memorandum R&D-99-023 (ejemplos con códigos de tipo y práctica)](https://legacy.rma.usda.gov/news/r-and-d/1999/html/rd99023.html), consultado 2026-11-15
- [AgRisk Viewer (NMSU)](https://agrisk.jornada.nmsu.edu/), consultado 2026-11-15

Confianza:
- **alta** en las URLs, los años disponibles, el formato y las columnas (diccionarios oficiales de 2026), y
  en los códigos de causa y de cultivo;
- **media** en cómo tratar los faltantes y el denominador (inferencias del diseño, sin datos a la vista);
- **baja / sin verificar** en qué tan completo está cada condado.

Impacto:
- un paquete nuevo `seguro` (`src/seguro/`, `docs/datasets/seguro.md`) o un archivo más en `cultivos`
  (necesita el OK del humano por el esquema nuevo);
- `loop/spec/entregables.yaml` si se agrega como entregable;
- en ML, un target de riesgo (`loss_cost`, la fracción por sequía o por exceso de agua) y una validación
  cruzada con `clima_mensual`;
- no cambia `config/`.
