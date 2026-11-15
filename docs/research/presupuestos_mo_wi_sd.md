# Presupuestos por cultivo, precios de NASS y regiones ERS de MO, WI y SD

Tarea T066 (pro-3), 2026-11-15.

Pregunta: Para el paquete `economia` en Missouri (MO, FIPS 29), Wisconsin (WI, 55) y Dakota del Sur (SD, 46):
(1) ¿qué presupuestos por cultivo publican University of Missouri, University of Wisconsin y South Dakota
State? Costos por acre de maíz, soja, trigo de invierno y avena; desde qué año, en qué formato y dónde.
(2) ¿Hay precios recibidos de NASS por estado para los seis cultivos? (3) ¿En qué región ERS (Farm Resource
Region) cae cada condado? Mismo planteo que `presupuestos_estados_nuevos.md` (T020) y `regiones_ers.md` (T005).

Respuesta corta:

| estado | quién | qué es | cultivos | riego | desde | formato |
|---|---|---|---|---|---|---|
| MO | University of Missouri Extension | presupuesto proyectado ("planning budget"); **sitio con 403, nada verificado** | según el buscador: maíz de secano (G651), maíz regado (G652, G658), soja de segunda (G655, G660), trigo del sudeste (G657) | según el buscador, sí | no verificado | según el buscador: guías PDF + planilla `crop-budgets.xlsx` |
| WI | UW–Madison Division of Extension, "UW Crop Enterprise Budget Tool" | presupuesto proyectado, un solo caso para todo el estado | maíz grano y silo, soja, cereal de invierno (trigo), henos y forrajes, centeno de cobertura, avena con arveja | no (hay una línea de riego en blanco) | 2020 según el equipo de UW (no verificado); la página enlaza solo la de 2025 | Excel (`.xlsx`) |
| SD | SDSU Extension, "Crop Production Budgets" (P-00138) | presupuesto proyectado; costos de maquinaria y gestión de tendencias de FINBIN | maíz, soja, trigo de primavera, trigo de invierno (3 zonas de productividad); **sin avena** | no | archivo en Open PRAIRIE desde 2005–2006 | Excel (`.xlsx`) |

- **Precios de NASS:** el informe *Crop Values 2025 Summary* (NASS, febrero de 2026) trae el precio medio del
  año comercial (MYA) por estado de 2023 a 2025 para maíz, soja, trigo de invierno, avena, heno de alfalfa y
  "all other hay" en los tres estados, con dos huecos: **avena de Missouri discontinuada desde 2024** y
  Wisconsin fuera del programa mensual de trigo. No se pudo consultar Quick Stats para la serie 2000–2025
  (ver punto 4).
- **Regiones ERS** (`reglink.xls`): **WI** es enteramente Northern Crescent (72 condados); **MO** se reparte
  en Heartland (88) y Eastern Uplands (27); **SD** en Northern Great Plains (47) y Heartland (19).

Recomendación: igual que T020, **quedarse con ERS como serie de costos de `economia`** para los tres estados
y dejar los presupuestos universitarios como referencia. Detalle en el punto 6.

Detalle:

**1. University of Missouri (MO) — MU Extension, planning budgets.**

**No se pudo abrir ninguna página ni archivo de MU.** `extension.missouri.edu` (páginas de publicaciones,
PDF y la planilla) y `mospace.umsystem.edu` devolvieron **HTTP 403** a curl y al cliente web automático
(2026-11-15, varios intentos). `agebb.missouri.edu/mgt/budget/`, la dirección vieja, devuelve 404. Lo que
sigue sale **solo de los resultados del buscador** (títulos y fragmentos), no de los documentos, y hay que
confirmarlo en un navegador:

- Guías "planning budget" del año 2026, en Extension Publications (Agricultural Economics): G651 maíz de
  secano (según el fragmento: 176 bu/ac, 30.000 semillas y 120 lb de N por acre), G652 maíz regado (norte,
  centro y sudoeste de Missouri), G658 maíz regado por surcos (sudeste), G655 y G660 soja de segunda (G660:
  soja OGM con pivote en el sudeste, precios según los pronósticos de octubre de 2025), G657 trigo (sudeste).
  También aparecen G653 y G664, sin título visible.
- Una planilla común: `https://extension.missouri.edu/media/wysiwyg/Extensiondata/Pro/AgBusinessPolicyExtension/Docs/crop-budgets.xlsx`
  (403).
- MOspace (repositorio de la universidad) guarda copias de "Corn (dryland) planning budget" con la leyenda
  "for historical documentation only": podría ser el archivo histórico, pero no se pudo ver qué años tiene.
- Una noticia de 2025 en farms.com ("MU Extension releases enterprise budgets for 2025") indica que el año
  anterior también se publicó. **Cobertura histórica, regiones, costos por acre, la definición de costos y si
  hay avena: no verificados.**
- No hay que confundirlos con FAPRI (también de Mizzou): FAPRI publica proyecciones de precios nacionales,
  no presupuestos por acre.

**2. University of Wisconsin (WI) — UW Crop Enterprise Budget Tool.**

- Página: `https://cropsandsoils.extension.wisc.edu/economics-budgets-and-financials` (sección "Tools"). Enlaza
  un solo archivo, `2025-UW-Crop-enterprise-budget-spreadsheets-3-17-25-Final.xlsx` (actualizado el 17/3/2025),
  una versión imprimible en blanco y el "Cover Crop Budget Analyzer" (2022). Al 2026-11-15 **la página no
  enlaza una versión 2026**.
- Hojas: `Corn`, `Corn Silage`, `Soybeans`, `Small Grain`, `Seeding Year Haylage`, `Established Haylage`,
  `Seeding Year Hay`, `Established Hay`, `Annual Forage Crop`, `Winter Cereal Rye`, `Cool Season Cocktail Mix`,
  `Summer Warm Season Cocktail Mix`, `Late-Summer Seeded Oats & Peas`. La hoja `Small Grain` viene cargada con
  trigo de invierno; **no hay un presupuesto de avena para grano** (solo avena con arveja como forraje).
- Es una plantilla para que el productor cargue sus números: un solo caso para Wisconsin, sin regiones ni
  riego (la línea "Irrigation" está vacía). Según un resultado del buscador (página de UW Extension Outagamie County, que no se pudo abrir: 404), los valores salen de
  entrevistas con productores, consultores, semilleros y cooperativas de Wisconsin; el artículo de Farm
  Management (`farms.extension.wisc.edu/articles/using-the-crop-enterprise-budget-tool`) describe la
  estructura (ingresos, costos variables y fijos, costo por bushel).
- Valores de la planilla 2025 (USD/ac; leída el 2026-11-15 en `/tmp`, fuera del repo):

  | ítem | maíz grano | soja | trigo de invierno |
  |---|---|---|---|
  | Rendimiento (bu/ac) | 176 | 51 | 76 |
  | Precio supuesto ($/bu) | 4,11 | 9,36 | 4,89 |
  | Ingreso por acre | 723,36 | 477,36 | 371,64 |
  | Total Direct Production Inputs (incluye tierra) | 574,84 | 450,79 | 499,60 |
  | de los cuales Land Rent / Ownership Cost | 185,00 | 185,00 | 185,00 |
  | Costo total por acre (ingreso − retorno neto) | 924,36 | 652,37 | 703,56 |
  | Net Return / Acre | −201,00 | −175,01 | −227,02 |
  | Cost per Bushel (Breakeven) | 5,25 | 12,79 | 9,26 |

  El costo total del maíz y la soja se calculó como ingreso − retorno neto (la planilla no trae una celda de
  "total"); para el trigo es la celda `Grain Expenses per acre`. El maíz incluye semilla de cultivo de
  cobertura ($37,50/ac), secado ($63,36/ac) y almacenaje ($42,24/ac), y mano de obra contratada
  (1,5 h × $25).
- Cobertura histórica: el resultado del buscador cita una grabación de UW ("Spring 2026 Ag Economics
  Outlook") que dice que los presupuestos "go back to 2020 for our major crops, corn, soybeans, wheat and
  oats". No se encontraron enlaces a las versiones anteriores a 2025: **no verificado**.

**3. South Dakota State (SD) — SDSU Extension, Crop Production Budgets.**

- Página: `https://extension.sdstate.edu/crop-budgets` (actualizada el 25/2/2026, Sarah Sellars). Enlaza
  `P-00138-2026.xlsx` ("2026 Crop Production Budgets") y `P-00138-2025.xlsx`. Años anteriores en el archivo
  de Open PRAIRIE, `https://openprairie.sdstate.edu/sd_crops_budget/`: un ítem por año de **2005–2006 a 2024**
  (no se abrieron los ítems; no se verificó el formato ni si hay huecos).
- La planilla 2026 tiene tres hojas de presupuesto: "East & Central High Production", "East & Central Mid
  Production" y "Central & West Low Production", cada una con maíz, soja, trigo de primavera y trigo de
  invierno. **No hay avena, alfalfa ni riego.** Según la hoja "Read Me", combustible, reparaciones, costos de
  propiedad de la maquinaria y cargo de gestión se estiman "using FINBIN trends for similar farms and crops
  then are adjusted for expected changes for 2026", y los totales son **antes del cargo por la tierra**
  ("Return to Land" es el resultado).
- Valores 2026 (USD/ac; precios supuestos: maíz $4,15, soja $10,30, trigo de primavera $5,50, trigo de
  invierno $5,20):

  | zona | cultivo | rinde (bu/ac) | costos directos | maquinaria | gestión | total antes de la tierra | retorno a la tierra |
  |---|---|---|---|---|---|---|---|
  | Este y centro, alta | maíz | 190 | 544,34 | 87,00 | 66,00 | 697,34 | 91,16 |
  | Este y centro, alta | soja | 48 | 299,14 | 87,00 | 66,00 | 452,14 | 42,26 |
  | Este y centro, alta | trigo de invierno | 61 | 350,31 | 69,00 | 66,00 | 485,31 | −168,11 |
  | Este y centro, media | maíz | 165 | 472,84 | 89,26 | 61,50 | 623,60 | 61,15 |
  | Este y centro, media | soja | 44 | 270,40 | 89,00 | 62,00 | 421,40 | 31,80 |
  | Este y centro, media | trigo de invierno | 59 | 288,79 | 67,00 | 62,00 | 417,79 | −110,99 |
  | Centro y oeste, baja | maíz | 94 | 379,81 | 82,00 | 51,00 | 512,81 | −122,71 |
  | Centro y oeste, baja | soja | 30 | 244,96 | 82,00 | 51,00 | 377,96 | −68,96 |
  | Centro y oeste, baja | trigo de invierno | 47 | 264,44 | 69,00 | 51,00 | 384,44 | −140,04 |

  Los costos directos incluyen semilla, fertilizante, agroquímicos, seguro, combustible, reparaciones,
  trabajos contratados, secado e interés operativo.

**4. Precios recibidos de NASS por estado.**

- **No se pudo consultar Quick Stats**: la API respondió `{"error":["unauthorized"]}` sin clave, la clave no
  estaba disponible para este trabajador, y el volcado completo (`qs.crops_*.txt.gz`, 1,1 GB) no está en esta
  máquina y la tarea pide no bajar datasets grandes. Los `short_desc` deberían ser los mismos que para IA, IL
  e IN (`precios_margenes.md`), pero **la cobertura 2000–2025 en MO, WI y SD no está verificada**.
- Lo que sí se verificó, en *Crop Values 2025 Summary* (NASS, febrero de 2026,
  `https://release.nass.usda.gov/reports/cpvl0226.txt`). Precio MYA por estado (2025 preliminar):

  | cultivo (unidad) | MO 2023 / 2024 / 2025 | WI 2023 / 2024 / 2025 | SD 2023 / 2024 / 2025 | EE.UU. 2025 |
  |---|---|---|---|---|
  | maíz grano ($/bu) | 4,60 / 4,19 / 4,15 | 4,29 / 4,13 / 4,05 | 4,29 / 4,00 / 3,80 | 4,10 |
  | soja ($/bu) | 12,40 / 10,10 / 10,40 | 12,40 / 9,95 / 9,90 | 12,00 / 9,67 / 9,60 | 10,20 |
  | trigo de invierno ($/bu) | 6,66 / 5,64 / 5,20 | 5,90 / 4,75 / 4,35 | 6,73 / 5,05 / 4,20 | 4,75 |
  | avena ($/bu) | 4,80 / (NA) / (NA) | 3,88 / 3,22 / 3,60 | 3,72 / 3,21 / 3,00 | 3,20 |
  | heno de alfalfa ($/t corta) | 175 / 177 / 169 | 170 / 155 / 129 | 162 / 108 / 96 | 170 |
  | otros henos ($/t corta) | 135 / 121 / 114 | 127 / 105 / 85 | 131 / 91 / 88 | 138 |

  - Avena de Missouri: nota 2/ del informe, "Estimates discontinued in 2024". En `economia`, la avena de MO
    quedaría vacía desde 2024.
  - Estados del programa mensual de precios (páginas 6 y 7 del informe): MO entra en maíz, trigo, arroz, soja
    y maní; WI en maíz, avena y soja (**no en trigo**: su precio de trigo es solo anual); SD en maíz, avena,
    trigo y soja. Los tres entran en heno. Es decir, los precios **mensuales** de avena no existen para MO y
    los de trigo no existen para WI.
  - Año comercial (MYA): maíz de septiembre a agosto en MO y SD, pero **de octubre a septiembre en WI**
    ("all other States"); soja de septiembre a agosto en los tres; avena de julio a junio; heno de mayo a
    abril en MO y de junio a mayo en WI y SD.
- Consulta para completar la serie cuando haya clave (igual que en `precios_margenes.md`):
  `source_desc=SURVEY&statisticcat_desc=PRICE RECEIVED&agg_level_desc=STATE&state_alpha=MO&commodity_desc=CORN&freq_desc=ANNUAL&year__GE=2000`,
  o el volcado `qs.crops_*.txt.gz` que ya lee `src/economia/process.py`.

**5. Región ERS de cada condado.**

De `reglink.xls` de ERS (`https://www.ers.usda.gov/sites/default/files/images/reglink.xls`, "Aggregating
counties to ERS resource regions", última modificación del archivo 2017; leído el 2026-11-15 en `/tmp`):

| estado | condados en reglink | regiones (condados) |
|---|---|---|
| MO (29) | 115 | Heartland 88, Eastern Uplands 27 |
| WI (55) | 72 | Northern Crescent 72 |
| SD (46) | 66 | Northern Great Plains 47, Heartland 19 |

- **MO, Eastern Uplands** (sur, Ozarks): 29009, 29011, 29017, 29035, 29043, 29057, 29065, 29067, 29077,
  29091, 29093, 29097, 29109, 29119, 29123, 29145, 29149, 29153, 29179, 29181, 29203, 29209, 29213, 29215,
  29223, 29225, 29229. El resto, incluida la ciudad de St. Louis (29510), es Heartland. Ojo: el sudeste de
  Missouri (Bootheel, arroz, algodón y soja regada) cae en Heartland y no en Mississippi Portal.
- **SD, Heartland** (este del estado): 46009, 46011, 46023, 46027, 46035, 46043, 46061, 46067, 46077, 46079,
  46083, 46087, 46097, 46099, 46101, 46111, 46125, 46127, 46135. El resto es Northern Great Plains.
- **Problema de códigos en SD**: `reglink.xls` usa **46113 (Shannon County)**, que en 2015 pasó a llamarse
  Oglala Lakota County con el código **46102**. Si `condados.csv` sale del TIGER actual, 46102 no va a
  encontrar región. Propuesta: mapear 46102 → la región de 46113 (Northern Great Plains) y anotarlo en el
  data card. (El cambio de código es conocido del Census; no se abrió la página del Census en esta tarea.)
- ERS no tiene serie de trigo para Eastern Uplands y la de avena solo cubre 2023–2025 (`regiones_ers.md`):
  el trigo y la avena de MO se ponderarían solo con Heartland en esos años (la regla de cobertura mínima del
  50 % de `process.py` lo permite si Heartland pesa más de la mitad del área).
- Los pesos por área sembrada (como en T005) **no se calcularon**: requieren `ACRES PLANTED` por condado de
  NASS, que no estuvo disponible (punto 4). Por cantidad de condados, MO es 77 % Heartland y SD 29 %
  Heartland, pero el área agrícola está concentrada en el norte de MO y el este de SD, así que los pesos por
  área serán mayores para Heartland en ambos.

**6. ¿Usarlos o quedarse con ERS?**

Las mismas razones de T020 valen acá, y algunas pesan más:

1. **Los tres son proyecciones** (planning budgets / plantillas), no costos ocurridos. ERS (ARMS) sí lo es.
2. **Definiciones distintas.** SDSU deja la tierra afuera ("before land charge") y carga gestión; UW mete la
   tierra en "direct production inputs" y no carga gestión; MU separa operativos y propiedad (ver punto 1).
3. **Cobertura despareja.** SD tiene un archivo largo (2005–2026); WI solo enlaza 2025; MU solo publica el
   año actual en su página. Avena: no hay presupuesto de grano en ninguna de las tres.
4. **Formato.** Planillas de un año por archivo (SD, WI) y un sitio (MU Extension) que devuelve 403 a los
   clientes automáticos.
5. **Comparabilidad con los otros 7 estados**, que tampoco usan presupuestos universitarios en el pipeline.

Comparación indicativa con ERS 2025 (valores de ERS tomados de `presupuestos_estados_nuevos.md`; años y
definiciones distintos):

- **SD maíz** (SDSU 2026, este y centro, media, 165 bu): directos 472,84 contra operativos de Heartland
  474,71 y de Northern Great Plains 417,55. Total sin tierra 623,60; ERS carga además la tierra, así que su
  total (963,43 Heartland, 786,53 NGP) no es comparable directo.
- **SD soja** (44 bu, media): directos 270,40 contra operativos de Heartland 255,55 y de NGP 176,51.
- **WI maíz** (UW 2025, 176 bu): total 924,36 con tierra a $185 contra total de Northern Crescent 2025
  896,82 (rinde ERS 178 bu). **WI soja**: 652,37 contra 616,15.

Lo que aportan y ERS no tiene: SDSU separa tres zonas de productividad dentro de SD (útil porque el oeste de
SD es Northern Great Plains con rindes de la mitad), y MU tiene presupuestos de maíz regado y de soja de
segunda para el sudeste de MO.

Fuentes:
- [Economics, Budgets and Financials — UW–Madison Extension, Crops and Soils](https://cropsandsoils.extension.wisc.edu/economics-budgets-and-financials), consultado 2026-11-15
- [2025 UW Crop Enterprise Budget spreadsheets (xlsx)](https://cropsandsoils.extension.wisc.edu/files/2025/03/2025-UW-Crop-enterprise-budget-spreadsheets-3-17-25-Final.xlsx), consultado 2026-11-15
- [Using the Crop Enterprise Budget Tool — UW–Madison Extension, Farm Management](https://farms.extension.wisc.edu/articles/using-the-crop-enterprise-budget-tool), consultado 2026-11-15
- [Crop Budgets — SDSU Extension](https://extension.sdstate.edu/crop-budgets), consultado 2026-11-15
- [2026 Crop Production Budgets, P-00138-2026 (xlsx) — SDSU Extension](https://extension.sdstate.edu/sites/default/files/2026-02/P-00138-2026.xlsx), consultado 2026-11-15
- [SDSU Extension Crop Budgets Archive — Open PRAIRIE](https://openprairie.sdstate.edu/sd_crops_budget/), consultado 2026-11-15
- [Crop Values 2025 Summary, febrero 2026 (txt) — USDA NASS](https://release.nass.usda.gov/reports/cpvl0226.txt), consultado 2026-11-15
- [Aggregating counties to ERS resource regions, reglink.xls — USDA ERS](https://www.ers.usda.gov/sites/default/files/images/reglink.xls), consultado 2026-11-15
- [G651 Corn (dryland) planning budget — MU Extension](https://extension.missouri.edu/publications/g651), consultado 2026-11-15 (403; no se pudo leer)
- [Missouri crop budgets workbook (xlsx) — MU Extension](https://extension.missouri.edu/media/wysiwyg/Extensiondata/Pro/AgBusinessPolicyExtension/Docs/crop-budgets.xlsx), consultado 2026-11-15 (403; no se pudo leer)
- [Corn (dryland) planning budget — MOspace](https://mospace.umsystem.edu/items/10cb2c36-ed28-483d-9cf3-ff57428588fb), consultado 2026-11-15 (403; no se pudo leer)
- [Quick Stats API — USDA NASS](https://quickstats.nass.usda.gov/api), consultado 2026-11-15 (sin clave: "unauthorized")

Confianza: alta para los precios de NASS 2023–2025, las regiones ERS por condado y los valores leídos de las
planillas de SDSU 2026 y UW 2025. Media para la cobertura histórica de SDSU (lista de ítems de Open PRAIRIE,
sin abrirlos). Baja para la cobertura histórica de UW (solo un resultado del buscador) y **nula para todo lo
de MU** (403; solo hay fragmentos del buscador).

Impacto: no cambia `config/` ni el esquema de `economia`. Para sumar MO, WI y SD a `economia` hace falta:
(a) que el humano agregue los estados (hoy no están en `config/config.yaml`); (b) mapear 46102 → 46113 en
`region_por_condado()` de `src/economia/process.py`; (c) la avena de MO desde 2024 y el trigo mensual de WI
quedan vacíos.
