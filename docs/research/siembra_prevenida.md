# Superficie con siembra prevenida (prevented planting) por condado: FSA Crop Acreage Data y USDA RMA

Pregunta: ¿Dónde y en qué formato están los datos de superficie con siembra prevenida (*prevented planting*,
PP) por condado y cultivo del USDA Farm Service Agency (FSA, "Crop Acreage Data")? ¿Qué agrega el USDA Risk
Management Agency (RMA) frente a FSA (causa de pérdida, tipo de cobertura)? ¿Sirve como target de riesgo por
exceso de agua en los 7 estados (IA, IL, IN, OH, NE, MN, KS) y cómo se une por `fips, anio`?

Respuesta corta:
- **FSA Crop Acreage Data**: un zip por año y por fecha de corte, con un `.xlsx` adentro (unos 20 MB), en la
  página de FSA "Crop Acreage Data". La hoja `county_data` trae, por condado × cultivo × tipo × uso ×
  riego/secano, `Planted Acres`, `Volunteer Acres`, `Failed Acres`, **`Prevented Acres`**, `Not Planted Acres`
  y `Planted and Failed Acres`. Hay datos por condado de **2009 a 2025**. Para 2007 y 2008 solo hay resúmenes
  por estado. El archivo final de cada año sale en enero del año siguiente (el de 2025, "as of January 12,
  2026").
- Abrí los archivos finales de 2019 y 2025, y el de 2009. Los tres tienen la hoja por condado con PP.
  - **2019** (récord), en los 7 estados: 4,73 millones de acres de maíz y 1,67 millones de soja con siembra
    prevenida. Los estados con más PP de maíz fueron IL (1,15 M ac), MN (1,00 M) y OH (0,93 M).
  - **2025**: 0,41 millones de acres de maíz y 0,38 millones de soja. El estado con más PP fue KS (256 mil ac
    de soja).
- **Ojo con los condados**: FSA usa **códigos de condado administrativos**, y unos pocos no son FIPS del
  Census. En 2025 encontré 19156 West Pottawattamie (IA), 27112 West Otter Tail, 27120 West Polk y 27138
  South St. Louis (MN), y 39094 East Lucas (OH). Hay que sumarlos al condado FIPS que tiene al lado (19155,
  27111, 27119, 27137 y 39095) antes de unir por `fips`. Esa asignación es una inferencia por el nombre y hay
  que confirmarla.
- **RMA** (archivo `colsom` de Cause of Loss, ya descripto en `rma_causa_perdida.md`): la PP no es una causa,
  sino una **etapa** (`Stage Code`): `P2` (PP sin opción adicional), `PF` (PP con la opción de +5 %) y `PT`
  (PP con la opción de +10 %, vigente desde 1998). `P` no es PP: es "Uninsured Loss". Comparado con FSA, RMA
  agrega:
  - la **causa** (exceso de humedad 31, frío húmedo 44, inundación 51, sequía 11);
  - el **mes de la pérdida**;
  - la **indemnización en USD**;
  - el **plan de seguro y la categoría de cobertura**.

  Además va desde 1989, no desde 2009. Pero solo incluye la superficie **asegurada**, y los acres van
  multiplicados por la participación del asegurado.
- En 2019, en los 7 estados, la PP de maíz de RMA (P2 + PF + PT) dio 4,14 millones de acres, frente a 4,73 de
  FSA. En soja dio 1,83 frente a 1,67. Por condado, la correlación entre las dos fuentes fue **r = 0,99 en
  maíz y 0,98 en soja** (cálculo mío, abajo). Casi el 100 % de esos acres de RMA (5,97 de 5,97 millones) tiene como causa el exceso de agua
  (31, 44 o 51), y el 89 % de las pérdidas son de mayo y junio.
- **Sirve como target de riesgo por exceso de agua en primavera**, mejor que el rendimiento: el lote que no se
  siembra no aparece en el rendimiento de NASS. Propongo `frac_prevenida = prevenida / (sembrada + prevenida)`
  por condado, año y cultivo. FSA es la fuente principal (2009–2025, toda la superficie). RMA queda para la
  causa y para tener 2000–2008. **Necesita el OK del humano** (esquema nuevo; ver "Propuesta").

## Detalle

### 1. FSA Crop Acreage Data: dónde y qué años

Página (la abrí el 2026-11-15):
`https://www.fsa.usda.gov/tools/informational/freedom-information-act-foia/electronic-reading-room/frequently-requested/crop-acreage-data`
(con la herramienta de fetch dio timeout; con `curl` cargó bien).

Qué dice la página, textual: los productores deben "self report all cropland on each farm to FSA annually.
FSA uses these data to determine payment eligibility [...] and to calculate losses for various disaster
programs. Data are reported in the following categories: planted; prevented planted; and failed." También
dice que NASS usa la superficie sembrada de FSA para complementar sus encuestas.

Archivos que lista la página:

| Años | Qué hay | Nombre de ejemplo |
|---|---|---|
| 2007, 2008 | solo por estado ("by crop by state for selected crops") | `2008_fsa_acres_sum_final.zip` |
| 2009, 2010 | por condado ("by crop by county"), un archivo final, más un resumen por estado | `2009_fsa_acres_detail_final_7.zip` |
| 2011 | por condado y por estado, con cortes mensuales de agosto a enero | `2011_fsa_acres_detail_jan2012.zip` ("FINAL") |
| 2012–2025 | un zip por corte mensual (agosto … enero del año siguiente) | `2019_fsa_acres_jan2020_stlno1.zip` |
| 2026 | en curso: cortes del 12 de agosto, 11 de septiembre, 9 de octubre, 10 de noviembre y 10 de diciembre de 2026 | — |

- Los nombres de los archivos no siguen ningún patrón (`.../documents/2019_fsa_acres_jan2020_stlno1.zip`,
  `.../documents/vc8Jn1nR42.zip`, `.../2026-01/DoISjehvQfz9.ZIP`). **No se pueden armar a partir del año**:
  hay que sacar las URLs de la página (scraping del `href` con el texto "<año> acreage data as of ...") o
  fijarlas en una tabla dentro de `download.py`.
- El enlace de la página para 2025 (`/documents/doisjehvqfz9zip`) devuelve un HTML que apunta al zip real,
  `https://www.fsa.usda.gov/sites/default/files/2026-01/DoISjehvQfz9.ZIP`.
- **2025**: según la página, los cortes de octubre y noviembre de 2025 "were not released due to the
  Government Shutdown". El final ("as of January 12, 2026") sí está. Lo bajé: es
  `2025_fsa_acres_web_010526.xlsx`, con fecha interna 2026-01-05.
- Notas de la página que importan:
  - 2023 y 2024: el archivo de agosto llega hasta el 9 de agosto, no hasta el 1.º. Para 2024 dice:
    "A small number of county revisions are in process".
  - Desde 2019, para trigo, cebada, avena, centeno y triticale, "the acre would be counted twice when a
    producer intends to use the same acre for both grazing and grain". Hay que filtrar por `Intended Use`.
- Tamaño: unos 20–22 MB por zip. Con un archivo final por año, 2009–2025 suma unos 300 MB. Bien por debajo
  del límite de 5 GB.

### 2. FSA: formato y columnas (verificado en los archivos)

**2012 en adelante** (abrí 2019 y 2025; los dos con las mismas 6 hojas):
`plant_and_fail`, `prevent` (tablas dinámicas por estado), `county_summary`, `crop_summary`,
**`county_data`** y `all_farm_count` (cantidad de explotaciones por condado).

Columnas de `county_data` (iguales en 2019 y 2025; 185.028 y 185.978 filas en todo el país):

| Columna | Ejemplo | Nota |
|---|---|---|
| State Code | `19` | FIPS de estado, texto con cero a la izquierda |
| County Code | `169` | código de condado **de FSA** (ver §4) |
| Crop Code | `0041` | maíz 0041, soja 0081, trigo 0011, avena 0016 (los mismos códigos que RMA) |
| State, County | `Iowa`, `Story` | nombres (hay entidades HTML: `O&#39;Brien`) |
| State County Code | `19169` | estado + condado |
| Crop | `CORN` | |
| Crop Type | `YELLOW`, `POPCORN`, `SWEET, BICOLOR`… | el código 0041 incluye pochoclo, maíz dulce y ornamental |
| Intended Use | `Grain`, `Silage`, `Seed`, `Fresh`, `Forage`, `Grazing`, `Left Standing`, `Processed`… | |
| Irrigation Practice | `I` / `N` | riego / secano (a veces vacío) |
| Planted Acres | | |
| Volunteer Acres | | |
| Failed Acres | | |
| **Prevented Acres** | | siembra prevenida |
| Not Planted Acres | | |
| Planted and Failed Acres | | |

- En 2025 la hoja trae una fila de título antes del encabezado, y en 2019 no. Además, **las celdas vacías no
  vienen en el XML**, así que el lector tiene que ubicar cada celda por su referencia de columna. Con
  `pandas.read_excel(..., sheet_name="county_data", header=<fila del encabezado>, dtype=str)` y `openpyxl`
  (que hoy no está en el `.venv`) no debería haber problema. Lo que verifiqué fue con un lector XML propio.
- No hay ocultamiento tipo `(D)`. Las combinaciones sin superficie no aparecen, o aparecen con 0.
- Lo que no tiene: causa, fecha y montos.

**2009 (y probablemente 2010–2011)**: un `.xlsx` con `Sheet1` y estas columnas: `State Code, County Code,
State Name, County Name, Crop Code, Crop Name, Crop Type Name, Crop Type, Intended Use, Planted Acres,
Prevented Acres, Failed Acres`. **No tiene `Irrigation Practice`**, y `Intended Use` viene en código (`FG`,
`SD`, …). No abrí los de 2010–2013: hay que comprobar su formato al bajarlos.

### 3. FSA en los 7 estados (cálculo mío sobre los archivos finales)

`Prevented Acres` sumados sobre todos los tipos, usos y prácticas, en acres:

| Estado | Maíz 2019 | Soja 2019 | Trigo 2019 | Maíz 2025 | Soja 2025 | Trigo 2025 |
|---|---|---|---|---|---|---|
| IL (17) | 1.145.385 | 331.247 | 27.073 | 136.423 | 51.116 | 1.249 |
| IN (18) | 710.038 | 229.628 | 3.532 | 91.668 | 22.228 | 3 |
| IA (19) | 380.992 | 82.237 | 1 | 838 | 1.095 | 0 |
| KS (20) | 224.014 | 163.728 | 188.345 | 93.852 | 255.955 | 67.364 |
| MN (27) | 1.000.683 | 161.246 | 7.557 | 7.967 | 3.525 | 611 |
| NE (31) | 344.407 | 71.958 | 1.584 | 4.978 | 261 | 349 |
| OH (39) | 928.742 | 629.815 | 6.057 | 71.698 | 49.902 | 221 |

- Avena: menos de 700 acres por estado en los dos años. No sirve.
- Casi toda la PP de maíz y soja está en `Intended Use = Grain`: en 2019, 4,712 de los 4,734 millones de acres
  de maíz.
- Esto es solo para dimensionar. No es un producto ni se guarda en `data/`.

### 4. FSA: códigos de condado que no son FIPS

En `county_data` de 2025, los 7 estados tienen estos códigos con número par (los FIPS del Census de estos
estados son impares):

| Código FSA | Nombre FSA | FIPS propuesto |
|---|---|---|
| 19156 | West Pottawattamie | 19155 Pottawattamie |
| 27112 | West Otter Tail | 27111 Otter Tail |
| 27120 | West Polk | 27119 Polk |
| 27138 | South St. Louis | 27137 St. Louis |
| 39094 | East Lucas | 39095 Lucas |

Son condados divididos en dos oficinas de FSA. La correspondencia es una inferencia por el nombre (confianza
media). Hay que confirmarla: por ejemplo, viendo que el código impar del mismo condado también aparece y que
la suma de los dos se parece a la superficie sembrada de NASS. Minnesota tiene 88 códigos en el archivo para
87 condados más 3 divisiones: hay 2 condados de MN sin ninguna fila de maíz, soja, trigo ni avena (no vi
cuáles). `validar_csv()` va a rechazar los códigos pares si no se convierten antes.

### 5. RMA: qué agrega sobre la siembra prevenida

Lo general de `colsom` y `sobtpu` (URLs, columnas, códigos de causa, participación) está en
`docs/research/rma_causa_perdida.md`. Acá va solo lo propio de la PP.

**Etapas de PP** (`History of Stage Codes 1989 Forward`, "Last Updated: 24-Feb-2026"; lo leí con
`pdftotext`):

| Stage | Descripción textual | Vigencia |
|---|---|---|
| `P2` | "Prevented Planting Option 2 (Unplanted Acres-98)" | todos los años del listado hasta 2026 |
| `PF` | "Prevented Planting - Unplanted Acreage with 5% buyup option" | hasta 2026 |
| `PT` | "Prevented Planting - Insured Crop Planted (Unplanted Acreage with 10% buy up option - 1998)" | hasta 2026, con huecos |
| `P1`, `P3`, `P4`, `PP` ("FCIC Reform Act of 1994"), `NP` ("Insured Crop NOT Planted") | | solo años viejos (no los usé) |
| `H3`, `U3` | "Prevented Planting Option 3 - Harvested / Unharvested Acres" | `H3` reaparece en 2025–2026 |
| `PU` | "Prevented Planting - Uninsured Loss" | algunos años |
| `P` | "Uninsured Loss" | **no es PP** |

No pude leer con certeza qué años marca cada código: la tabla del PDF tiene una columna por año y el texto
extraído no deja asignar cada `X` a su año. El rango exacto de vigencia hay que tomarlo del `.xlsx` del
mismo listado (`Stage_Code_Listing.xlsx`), que no abrí. **Propuesta**: tomar como PP todas las etapas cuya
descripción empiece con "Prevented Planting" (columna 11 de `colsom`, cruzada con el listado), salvo `PU`.

**`colsom_2019`, en los 7 estados, maíz (0041) y soja (0081), etapas P2/PF/PT** (cálculo mío; bajé el zip de
6 MB a una carpeta temporal, no a `data/`):
- `Net Determined Quantity` (acres con pérdida × participación): maíz P2 2.900.030 + PF 1.236.470, soja
  P2 1.268.804 + PF 564.695. No hubo filas `PT`.
- Indemnización: P2 1.149 millones de USD y PF 514 millones de USD (maíz y soja juntos).
- Causas, en acres:
  - 31 Excess Moisture: 5,52 millones;
  - 44 Cold Wet Weather: 0,28 millones;
  - 51 Flood: 0,17 millones;
  - 11 Drought: 406 acres.

  En el Corn Belt, la PP es casi solo exceso de agua.
- Mes de la pérdida: junio 2,89 millones de acres, mayo 2,40 millones, abril 0,44 millones, marzo 0,09
  millones y julio 0,09 millones.

**Comparación por condado con FSA (2019)**: sumé `Prevented Acres` de FSA (todos los usos) y P2 + PF + PT de
RMA para cada código estado + condado. La unión de las dos fuentes dio 666 códigos con maíz y 659 con soja.

| Cultivo | FSA total (ac) | RMA total (ac) | r de Pearson | Condados con FSA > 0 y sin RMA | Condados con RMA > 0 y sin FSA |
|---|---|---|---|---|---|
| maíz | 4.734.261 | 4.136.500 | 0,991 | 21 | 9 |
| soja | 1.669.859 | 1.833.499 | 0,984 | 22 | 14 |

En esta comparación los códigos partidos de FSA (§4) no se convirtieron.

Por qué no coinciden (en parte es inferencia):
- RMA cubre solo lo asegurado y multiplica por la participación;
- FSA registra lo que el productor declaró;
- la FAQ de RMA aclara que los productores "file claims for their 'intended' plantings; however, actual
  payments are based on the number of eligible acres", y que los datos de FSA y RMA "will not match, nor are
  they required to match".
- En soja RMA da más que FSA. Una posible explicación: el maíz que no se pudo sembrar y se pasó a soja, o la
  soja sembrada después de la fecha límite. No lo verifiqué.

**Lo que RMA agrega frente a FSA**, en resumen:
1. Causa de la pérdida: permite separar el exceso de agua (31, 44, 51) de la sequía (11), que también puede
   causar PP ("Prevented planting covers drought", FAQ de RMA). Esto importa en KS en años secos.
2. Mes y año de la pérdida: fecha real del impedimento.
3. Monto: indemnización en USD, normalizable por la `liability` de `sobtpu`.
4. Opción de cobertura: `P2` frente a `PF`/`PT` (+5 % o +10 % de cobertura comprada). Esto es una decisión del
   productor, no una señal de clima.
5. Años: desde 1989, o sea 2000–2008 en el período del proyecto, que FSA no tiene por condado.
6. Riego: el archivo de causas no separa riego de secano (ya dicho en el research de RMA). FSA sí, desde 2012.

Reglas de la póliza que afectan la PP (FAQ de RMA, noviembre de 2025):
- la superficie tiene que estar "physically available for planting";
- tiene que haberse sembrado y cosechado "in at least 1 out of the previous 4 years" (regla 1 de 4);
- el pago es un porcentaje de la garantía que "varies by crop" y está en el Actuarial Information Browser;
- si después se siembra un segundo cultivo, el pago del primero baja al 35 %.

No abrí el Actuarial Information Browser: los porcentajes por cultivo (los típicos 55 % para maíz y 60 % para
soja) **no los verifiqué**.

### 6. ¿Sirve como target de riesgo por exceso de agua?

Sí, con algunos cuidados:
- **Señal fuerte y espacialmente coherente**: 2019 resalta en IL, IN, OH y MN, y las dos fuentes coinciden
  con r ≈ 0,99. Es el impacto directo del exceso de agua en primavera que pide la sección 6.4 del CLAUDE.md:
  el rendimiento de NASS no lo ve, porque solo cuenta lo sembrado.
- **Denominador**: `frac_prevenida = Prevented / (Planted + Prevented)`, en el mismo archivo de FSA. Así no
  depende de cuánto se sembró. Los `Failed Acres` (sembrado y perdido) son otra señal y van aparte.
- **Ceros reales**: si el condado tiene superficie del cultivo en FSA y no tiene PP, el valor es 0 (no
  faltante). Es la misma excepción que en `rma_causa_perdida.md` y va en el data card.
- **Cuidados**:
  - la PP depende también de reglas (fecha final de siembra por condado, regla 1 de 4, precios: con buen
    precio conviene sembrar tarde) y no solo del clima;
  - en KS una parte es por sequía: con RMA se puede separar;
  - la distribución tiene muchos años casi en cero y pocos años extremos (2019).
- **Cómo se une**:
  - `fips` = `State County Code` de FSA, después de convertir los códigos de §4;
  - `anio` = año del archivo (crop year), que en RMA coincide con `Commodity Year`;
  - `cultivo` con la misma lista que `produccion_anual.csv` (maíz 0041 con `Crop Type` ≠ pochoclo/dulce/
    ornamental, soja 0081 y trigo 0011 con `Crop Type` de invierno);
  - formato largo `fips, anio, cultivo`, igual que `produccion_anual.csv`.

### 7. Propuesta concreta (decide el humano)

Un archivo nuevo, dentro de `cultivos` o del paquete `seguro` propuesto en `rma_causa_perdida.md`:
**`siembra_prevenida_anual.csv`** → `fips, anio, cultivo, ...`

| Columna | Fuente | Nota |
|---|---|---|
| `sup_sembrada_fsa_ac` | FSA `Planted Acres` | solo `Intended Use` = Grain (o Grain + Silage para maíz, a decidir) |
| `sup_prevenida_fsa_ac` | FSA `Prevented Acres` | todos los usos (casi todo es Grain) |
| `sup_fallida_fsa_ac` | FSA `Failed Acres` | |
| `frac_prevenida` | prevenida / (sembrada + prevenida) | vacío si el denominador es 0 |
| `sup_prevenida_fsa_secano_ac`, `sup_prevenida_fsa_riego_ac` | FSA por `Irrigation Practice` | desde 2012 (en 2009–2011 no existe la columna) |
| `sup_prevenida_rma_ac` | `colsom` etapas PP, `Net Determined Quantity` | 2000–2025 |
| `sup_prevenida_rma_exceso_agua_ac` | ídem, causas 31, 44 y 51 | |
| `sup_prevenida_rma_sequia_ac` | ídem, causa 11 | |
| `indem_prevenida_rma_usd` | ídem, `Indemnity Amount` | |

Descarga (`download.py`, a `data/raw/<paquete>/fsa_acreage/`):
- solo el archivo **final** de cada año, de 2009 a 2025, unos 17 zips de alrededor de 20 MB;
- tabla fija año → URL, sacada de la página;
- una fila por archivo en `manifest.csv`, con la fecha de corte ("as of …").

El `colsom` ya lo baja la propuesta de RMA.

Procesamiento:
- filtrar `State Code` por `FIELDSHIFT_ESTADOS`;
- convertir los códigos de condado de FSA (§4) con una tabla documentada en el data card;
- agrupar por `fips, anio, cultivo`.

No sacar tendencias ni calcular percentiles: eso lo decide ML.

Hace falta agregar `openpyxl` a `requirements.txt`, porque `pandas.read_excel` lo necesita para `.xlsx`.

## Lo que no encontré o no verifiqué

- El formato de los archivos de 2010 a 2013 (solo abrí 2009, 2019 y 2025).
- Si FSA revisa los archivos finales después de publicarlos (la página no lo dice).
- Los 2 condados de MN sin filas en 2025, y si la tabla de códigos partidos cambia entre años.
- Los años exactos de vigencia de cada etapa de PP de RMA (está en el `.xlsx` del listado, que no abrí).
- Los porcentajes de cobertura de PP por cultivo y las fechas finales de siembra por condado (Actuarial
  Information Browser, no lo abrí).
- El documento de NASS sobre la superficie de FSA
  (`https://www.nass.usda.gov/Education_and_Outreach/Understanding_Statistics/FSA_Acreage.pdf`) devolvió 404.
- No comparé con `sup_sembrada_ac` de NASS.

Fuentes:
- [USDA FSA – Crop Acreage Data](https://www.fsa.usda.gov/tools/informational/freedom-information-act-foia/electronic-reading-room/frequently-requested/crop-acreage-data), consultado 2026-11-15
- [FSA – 2019 acreage data as of January 1, 2020 (zip, `2019_fsa_acres_web_010220.xlsx`)](https://www.fsa.usda.gov/sites/default/files/documents/2019_fsa_acres_jan2020_stlno1.zip), consultado 2026-11-15
- [FSA – 2025 acreage data as of January 12, 2026 (zip, `2025_fsa_acres_web_010526.xlsx`)](https://www.fsa.usda.gov/sites/default/files/2026-01/DoISjehvQfz9.ZIP), consultado 2026-11-15
- [FSA – 2009 by crop by county (zip, `2009_fsa_acres_detail_final_7.xlsx`)](https://www.fsa.usda.gov/sites/default/files/documents/2009_fsa_acres_detail_final_7.zip), consultado 2026-11-15
- [USDA RMA – History of Stage Codes 1989 Forward (24-Feb-2026)](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/Stage_Code_Listing.pdf), consultado 2026-11-15
- [USDA RMA – colsom_2019.zip (Cause of Loss 2019)](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/colsom_2019.zip), consultado 2026-11-15
- [USDA RMA – Prevented Planting Coverage (FAQ, noviembre de 2025)](https://rma.usda.gov/News-Room/Frequently-Asked-Questions/Prevented-Planting-Coverage), consultado 2026-11-15
- `docs/research/rma_causa_perdida.md` (este repo), para las columnas de `colsom` y `sobtpu`

Confianza:
- **alta** en la ubicación, los años y las columnas de FSA (abrí los archivos), en los códigos de etapa de PP
  de RMA y en los números de 2019 y 2025 (cálculo directo sobre los archivos oficiales);
- **media** en la conversión de los códigos de condado partidos de FSA y en el formato de 2010–2013;
- **media** en que `frac_prevenida` refleje sobre todo el clima: también influyen las reglas del seguro y los
  precios.

Impacto:
- un archivo nuevo `siembra_prevenida_anual.csv` (esquema nuevo: OK del humano), en `cultivos` o en `seguro`;
- `openpyxl` en `requirements.txt`;
- en ML, un target de riesgo por exceso de agua en primavera que se puede validar con `agua_mensual`
  (SMAP, días sobre saturación) y `clima_mensual` (lluvia de abril a junio);
- no cambia `config/` ni `src/common/`.
