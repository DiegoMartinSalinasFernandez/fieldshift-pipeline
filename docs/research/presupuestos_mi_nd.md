# Presupuestos por cultivo, precios de NASS y regiones ERS de MI y ND

Tarea T075 (pro-3), 2026-11-15.

Pregunta: Para un posible paquete `economia` en Michigan (MI, FIPS 26) y Dakota del Norte (ND, 38):
(1) ¿qué presupuestos por cultivo publican MSU Extension y NDSU Extension (por región)? Costos por acre de
maíz, soja, trigo de invierno y de primavera y otros cultivos importantes: desde qué año, en qué formato y
dónde. (2) ¿Hay precios recibidos de NASS por estado? (3) ¿En qué región ERS (Farm Resource Region) cae cada
condado y hay cambios de código de condado en `reglink.xls`? Mismo planteo que `presupuestos_mo_wi_sd.md`
(T066). MI y ND **no están** en `config/config.yaml`: esto es research para que el humano decida.

Respuesta corta:

| estado | quién | qué es | cultivos | riego | desde | formato |
|---|---|---|---|---|---|---|
| MI | MSU Extension, Farm Management ("Projected Cost of Production") | herramienta proyectada de costo de producción, un caso para todo el estado con 3 escenarios; **las páginas de MSU no se pudieron leer** | maíz y soja verificados (por artículos de farms.com); trigo, porotos y remolacha: no se encontró presupuesto de MSU | maíz sí (3 escenarios regados); soja no | no verificado | Excel según los artículos (no se pudo bajar) |
| ND | NDSU Extension, "Projected Crop Budgets" (EC1652 a EC1660), Ron Haugen | presupuesto proyectado por **9 regiones** de 3 a 13 condados | 14 a 18 cultivos por región: trigo de primavera (HRSW), durum, cebada, maíz, soja, poroto, girasol (aceitero y confitero), canola, lino, arveja, avena, lenteja, mostaza, trigo sarraceno, mijo, trigo de invierno, centeno | secano; presupuestos regados aparte solo 2022–2023 (3 zonas) | PDF desde 2004 (algunas regiones 2005), Excel desde 2006, hasta 2026 | Excel (`.xls`) + PDF, un archivo por región y año |

- **Precios de NASS:** *Crop Values 2025 Summary* (NASS, febrero de 2026) trae el precio medio del año
  comercial (MYA) por estado de 2023 a 2025 para maíz, soja, trigo, avena, cebada, heno y porotos en los dos
  estados, y además trigo de primavera, durum, centeno, lino, girasol, canola, arveja y lenteja en ND. La
  remolacha azucarera solo trae 2023–2024. No se pudo consultar Quick Stats para la serie 2000–2025 (punto 4).
- **Regiones ERS** (`reglink.xls`): **MI** es entera Northern Crescent (83 condados) y **ND** entera
  Northern Great Plains (53 condados). **No hay cambios de código de condado**: los 83 y 53 FIPS de
  `reglink.xls` coinciden uno a uno con la lista de condados del Census 2020.

Recomendación: igual que T020 y T066, **quedarse con ERS como serie de costos de `economia`** y dejar los
presupuestos universitarios como referencia. En ND, NDSU es la mejor fuente universitaria de las revisadas
hasta ahora (serie 2006–2026 en Excel con formato estable y regiones con lista de condados). Detalle en el
punto 6.

Detalle:

**1. Michigan State University (MI) — MSU Extension, Projected Cost of Production.**

**No se pudo abrir ninguna página de MSU.** `www.canr.msu.edu` responde a curl con una página de bloqueo de
Incapsula ("Request unsuccessful") y al cliente web automático con HTTP 200 sin texto (2026-11-15). El
formulario de trigo del Michigan Wheat Program (`miwheat.org`) devolvió HTTP 403. Lo que sigue sale de dos
artículos de farms.com que reproducen las notas de MSU (sí se leyeron) y de los resultados del buscador:

- **Maíz 2026** (artículo del 14/4/2026, Jon LaPorte): herramienta en "a single downloadable Excel file",
  enlazada desde `https://www.canr.msu.edu/resources/2026-corn-projected-cost-of-production`. Tres escenarios
  para secano y tres para riego: Base Projection (rinde objetivo 165 bu/ac en secano, 215 regado; fertilidad
  por extracción de nutrientes según el boletín Tri-State), Build-Up (la base más fertilización para subir el
  nivel de análisis de suelo) y Push Production (195 bu/ac en secano, 240 regado). El artículo **no da
  precios, costo por acre ni precio de equilibrio**, y no dice si incluye la tierra.
- **Soja 2026** (artículo del 6/4/2026, Jon LaPorte y Eric Anderson): mismo formato, tres escenarios, Base
  (50 bu/ac), Build-Up y Push Production (75 bu/ac); sin escenario regado. Tampoco da costos. Según el
  fragmento del buscador (no verificado en el archivo), el precio de equilibrio de Push Production es
  $8,98/bu o un rinde de equilibrio de 61,19 bu/ac.
- **Trigo, porotos, remolacha:** el buscador no encontró presupuestos de MSU. Un episodio de podcast (solo el
  resultado del buscador) menciona una calculadora de trigo de MSU y un "2026 Wheat Cost of Production
  Worksheet" en el sitio del Michigan Wheat Program, que dio 403. **No verificado.**
- **Cobertura histórica, regiones, definición de costos (tierra, gestión): no verificados.** Son proyecciones
  de un solo caso estatal, sin regiones.

**2. North Dakota State (ND) — NDSU Extension, Projected Crop Budgets.**

- Página: `https://www.ndsu.edu/agriculture/extension/ag-topics/farm-management/crop-economics/projected-crop-budgets`
  (la dirección vieja `.../ag-hub/...` redirige ahí). "North Dakota regional crop budgets are created
  annually". Un PDF y un Excel por región y año. Autor de 2026: Ron Haugen, Farm Management Specialist.
- **Nueve regiones**, con su lista de condados en la primera página de cada PDF 2026 (FIPS cruzados con la
  lista del Census 2020; los 53 condados quedan cubiertos una sola vez):

  | región (publicación) | condados | FIPS |
  |---|---|---|
  | South West (EC1652) | Adams, Billings, Bowman, Dunn, Golden Valley, Grant, Hettinger, Mercer, Morton, Oliver, Sioux, Slope, Stark | 38001, 38007, 38011, 38025, 38033, 38037, 38041, 38057, 38059, 38065, 38085, 38087, 38089 |
  | South Central (EC1653) | Burleigh, Emmons, Kidder, Logan, McIntosh, Sheridan | 38015, 38029, 38043, 38047, 38051, 38083 |
  | North Central (EC1654) | Benson, Bottineau, McHenry, McLean, Pierce, Renville, Rolette, Ward | 38005, 38009, 38049, 38055, 38069, 38075, 38079, 38101 |
  | North East (EC1655) | Cavalier, Nelson, Ramsey, Towner | 38019, 38063, 38071, 38095 |
  | North Valley (EC1656; en el Excel "North Red River Valley") | Grand Forks, Pembina, Walsh | 38035, 38067, 38099 |
  | North West (EC1657) | Burke, Divide, McKenzie, Mountrail, Williams | 38013, 38023, 38053, 38061, 38105 |
  | East Central (EC1658) | Eddy, Foster, Griggs, Stutsman, Wells | 38027, 38031, 38039, 38093, 38103 |
  | South East (EC1659) | Barnes, Dickey, LaMoure, Ransom, Sargent, Steele | 38003, 38021, 38045, 38073, 38081, 38091 |
  | South Valley (EC1660; en el Excel "South Red River Valley") | Cass, Richland, Traill | 38017, 38077, 38097 |

  Las regiones se tomaron de los PDF de 2026; **no se verificó que las listas de condados sean las mismas en
  años anteriores**.
- **Cobertura** (según los títulos de los enlaces de la página): Excel de **2006 a 2026** en las nueve
  regiones, sin huecos; PDF de 2004 (East Central desde 2005) a 2026, con huecos: North Valley 2007, South
  Valley 2008, y los PDF 2026 de North East, North Valley, South Central y South West no figuran con ese
  título (sí están `ec1655.pdf`, `ec1656.pdf`, `ec1653.pdf` y `ec1652.pdf` en `2026-02/`, que son los que se
  leyeron acá). Ojo: en `2026-01/` hay además un `NW_25Bud_1.xls`; el Excel de North West 2026 es
  `2026-02/NW_26Bud_0.xls`.
- **Formato estable.** Se abrieron los Excel 2026 de las nueve regiones y `EastCent_2006Bud.xls`: una hoja por
  cultivo con las mismas filas (Market Yield, Market Price, Market Revenue; costos directos: semilla,
  herbicidas, fungicidas, insecticidas, fertilizante, seguro, combustible, reparaciones, secado, varios,
  interés operativo; indirectos: gastos generales, depreciación e interés de la maquinaria, **cargo por la
  tierra**; total; "Return to labor & mgmt"). En 2006 la fila del precio dice "Market Price + LDP". En las
  regiones del oeste (North West, South West) las hojas se llaman `Soy` y `HRWW` en lugar de `Soyb` y
  `Wint.Wht`.
- **Supuestos 2026** (PDF EC1658, "Primary Assumptions"): secano sobre rastrojo ("dryland recrop ground");
  precio = mejor estimación de los economistas de NDSU (el mayor entre precio proyectado y tasa del préstamo
  de comercialización); **rinde = promedio 2018–2024 sacando el año más bajo y el más alto**; fertilizante
  según análisis de suelo (N $0,58/lb, P $0,68/lb, K $0,38/lb); seguro Revenue Protection al 75 %; interés
  operativo 7 % por 6 meses; tierra = **alquiler medio en efectivo** de la región; interés real del 4 % sobre
  la inversión media en maquinaria. Excluyen los pagos de PLC y ARC.
- Valores 2026 (USD/ac; leídos de los Excel el 2026-11-15 en `/tmp`, fuera del repo). Precio supuesto: maíz
  $3,75 en todas las regiones; soja $9,60–9,87; trigo de primavera $5,67–5,88; trigo de invierno $4,89–5,19;
  avena $2,46–2,64.

  | región | cultivo | rinde (bu/ac) | costos directos | tierra | total | retorno a mano de obra y gestión |
  |---|---|---|---|---|---|---|
  | South Valley | maíz | 170 | 439,85 | 142 | 675,40 | −37,90 |
  | South Valley | soja | 41 | 175,67 | 142 | 373,93 | 30,74 |
  | South Valley | trigo de primavera | 63 | 254,43 | 142 | 456,88 | −86,44 |
  | South East | maíz | 168 | 424,43 | 108 | 623,98 | 6,02 |
  | South East | soja | 41 | 174,51 | 108 | 337,07 | 65,96 |
  | South East | trigo de primavera | 58 | 226,89 | 108 | 391,76 | −51,88 |
  | North Valley | maíz | 142 | 387,99 | 98 | 576,22 | −43,72 |
  | North Valley | soja | 34 | 164,06 | 98 | 317,46 | 14,72 |
  | North Valley | trigo de primavera | 63 | 252,07 | 98 | 410,52 | −44,49 |
  | East Central | maíz | 149 | 402,55 | 75 | 570,87 | −12,12 |
  | East Central | soja | 36 | 173,77 | 75 | 303,63 | 47,37 |
  | East Central | trigo de primavera | 55 | 230,35 | 75 | 361,85 | −42,30 |
  | North East | maíz | 121 | 367,79 | 64 | 521,78 | −68,03 |
  | North East | soja | 32 | 188,18 | 64 | 310,76 | −0,36 |
  | North East | trigo de primavera | 59 | 246,32 | 64 | 367,31 | −26,29 |
  | South Central | maíz | 122 | 344,73 | 61 | 488,15 | −30,65 |
  | South Central | soja | 33 | 158,44 | 61 | 270,09 | 50,01 |
  | South Central | trigo de primavera | 48 | 208,68 | 61 | 320,69 | −43,73 |
  | North Central | maíz | 111 | 326,00 | 57 | 467,95 | −51,70 |
  | North Central | soja | 31 | 152,90 | 57 | 258,62 | 38,98 |
  | North Central | trigo de primavera | 53 | 218,02 | 57 | 330,84 | −28,74 |
  | South West | maíz | 82 | 247,79 | 41 | 358,08 | −50,58 |
  | South West | soja | 28 | 133,00 | 41 | 222,34 | 46,46 |
  | South West | trigo de primavera | 43 | 181,66 | 41 | 269,08 | −24,84 |
  | North West | maíz | 84 | 260,95 | 39 | 369,48 | −54,48 |
  | North West | soja | 22 | 141,67 | 39 | 228,26 | −17,06 |
  | North West | trigo de primavera | 43 | 192,12 | 39 | 277,54 | −33,73 |

  Trigo de invierno y avena 2026 (rinde bu/ac / total USD/ac): South Valley 69 / 448,02 y 100 / 404,95;
  South East 64 / 389,13 y 73 / 318,45; North Valley 69 / 399,38 y 107 / 371,79; East Central 60 / 355,07 y
  81 / 307,73; North East 64 / 357,52 y 93 / 320,85; South Central 53 / 310,53 y 68 / 277,20; North Central
  59 / 330,97 y 93 / 308,28; South West 47 / 268,47 y 70 / 250,71; North West 47 / 277,86 y 69 / 256,87.
  La avena da retorno negativo en las nueve regiones (−77 a −141 USD/ac).
- **Riego:** página aparte (`.../crop-economics/irrigated-crop-budgets`) con presupuestos regados para el
  este, el centro y el oeste de ND, **solo 2022 y 2023** (`.xlsx`; no se abrieron).

**3. Otros cultivos importantes.** En ND, NDSU cubre también durum, cebada, poroto, girasol, canola, lino,
arveja, lenteja (solo en North Central, North West, South Central y South West), mostaza, trigo sarraceno,
mijo y centeno; el poroto falta en North West y South West, y South Valley solo trae 9 cultivos (sin durum,
canola, lino ni arveja). Remolacha azucarera y papa: **no hay** presupuesto de NDSU en esta página. En MI,
los cultivos con precio de NASS además del maíz y la soja son trigo (todo de invierno), poroto, remolacha
azucarera, papa, avena, cebada y heno (punto 4), pero no se encontró presupuesto de MSU para ninguno.

**4. Precios recibidos de NASS por estado.**

- **No se pudo consultar Quick Stats** (mismo motivo que en T066: sin clave de NASS en este trabajador y sin
  el volcado `qs.crops_*.txt.gz`). La cobertura 2000–2025 en MI y ND **no está verificada**.
- Lo verificado, en *Crop Values 2025 Summary* (`https://release.nass.usda.gov/reports/cpvl0226.txt`,
  leído el 2026-11-15). Precio MYA por estado (2025 preliminar):

  | cultivo (unidad) | MI 2023 / 2024 / 2025 | ND 2023 / 2024 / 2025 | EE.UU. 2025 |
  |---|---|---|---|
  | maíz grano ($/bu) | 4,19 / 4,16 / 3,90 | 4,14 / 3,96 / 3,80 | 4,10 |
  | soja ($/bu) | 12,80 / 10,50 / 10,40 | 12,00 / 9,53 / 9,65 | 10,20 |
  | trigo, todo ($/bu) | 6,28 / 5,55 / 5,05 | 7,27 / 5,71 / 5,15 | 4,90 |
  | trigo de invierno ($/bu) | 6,28 / 5,55 / 5,05 | 6,63 / 5,18 / 4,50 | 4,75 |
  | trigo de primavera, otro ($/bu) | — | 6,97 / 5,55 / 5,05 | 5,20 |
  | durum ($/bu) | — | 9,38 / 6,82 / 6,15 | 6,40 |
  | avena ($/bu) | 5,34 / 3,89 / 3,40 | 3,99 / 3,43 / 3,10 | 3,20 |
  | cebada ($/bu) | 4,50 / 4,00 / 3,60 | 6,67 / 5,80 / 4,65 | 5,40 |
  | centeno ($/bu) | — | 6,20 / 5,50 / 4,25 | 4,75 |
  | heno de alfalfa ($/t corta) | 195 / 173 / 158 | 120 / 95 / 92 | 170 |
  | otros henos ($/t corta) | 138 / 138 / 129 | 88 / 79 / 68 | 138 |
  | poroto seco ($/cwt) | 44,00 / 39,40 / 34,70 | 38,60 / 32,10 / 24,60 | 30,20 |
  | papa ($/cwt) | 13,30 / 16,50 / 15,50 | 15,30 / 13,40 / 12,70 | 11,20 |
  | remolacha azucarera ($/t) | 59,70 / 57,00 / (no publicado) | 89,60 / 83,50 / (no publicado) | — |
  | girasol, todo ($/cwt) | — | 22,20 / 23,70 / 23,20 | 22,90 |
  | canola ($/cwt) | — | 24,40 / 20,30 / 20,40 | 20,50 |
  | lino ($/bu) | — | 12,10 / 12,50 / 13,00 | 13,00 |
  | arveja seca ($/cwt) | — | 15,50 / 13,70 / 11,40 | 11,30 |
  | lenteja ($/cwt) | — | 38,00 / 34,40 / 22,00 | 24,90 |

  - "—" = el estado no figura en la tabla de ese cultivo. En MI el trigo de invierno y el trigo "todo" son
    iguales. La remolacha 2025 sale en "Crop Values" de febrero de 2027 según el informe.
  - Estados del programa mensual de precios (páginas 6 y 7): **MI** entra en maíz, avena, trigo, soja, heno y
    poroto; **ND** en maíz, avena, cebada, trigo, soja, lino, girasol, canola, heno, poroto, garbanzo, arveja y
    lenteja. Los precios mensuales de cebada no existen para MI.
  - Año comercial (MYA, definiciones 2025): maíz de **octubre a septiembre** en MI y ND ("all other States",
    distinto de IA, IL e IN, que van de septiembre a agosto); soja, girasol y poroto de septiembre a agosto;
    trigo, avena, cebada, canola, lino, arveja y lenteja de julio a junio; heno de junio a mayo.
- Consulta para completar la serie cuando haya clave (igual que en `precios_margenes.md`):
  `source_desc=SURVEY&statisticcat_desc=PRICE RECEIVED&agg_level_desc=STATE&state_alpha=ND&commodity_desc=CORN&freq_desc=ANNUAL&year__GE=2000`.

**5. Región ERS de cada condado y cambios de código.**

De `reglink.xls` de ERS (`https://www.ers.usda.gov/sites/default/files/images/reglink.xls`, "Aggregating
counties to ERS resource regions", última modificación del archivo 2017-10-25; leído el 2026-11-15 en `/tmp`):

| estado | condados en reglink | regiones (condados) |
|---|---|---|
| MI (26) | 83 | Northern Crescent 83 |
| ND (38) | 53 | Northern Great Plains 53 |

- **Cambios de código: ninguno.** Se compararon los FIPS de `reglink.xls` con las listas de condados del
  Census 2020 (`st26_mi_cou2020.txt` y `st38_nd_cou2020.txt`): 83 y 53 condados, los mismos códigos en los
  dos archivos. No hace falta un mapeo como el 46102 → 46113 de SD.
- Como cada estado cae entero en una sola región, **no hace falta ponderar por área**: el costo de ERS de MI
  es directamente el de Northern Crescent y el de ND el de Northern Great Plains. ERS tiene las cuatro series
  (maíz, soja, trigo, avena) para las dos regiones (`regiones_ers.md`).
- Ojo con la representatividad: la serie de Northern Great Plains de ERS mezcla ND con SD, MN, NE y MT, y su
  maíz 2025 tiene un rinde de 208 bu/ac (`presupuestos_estados_nuevos.md`), muy por encima de los 82–170 bu/ac
  de las regiones de NDSU. En ND, el maíz de ERS va a sobrestimar rinde y costo.

**6. ¿Usarlos o quedarse con ERS?**

1. **Los dos son proyecciones**, no costos ocurridos. ERS (ARMS) sí lo es.
2. **MSU no se pudo leer** y solo publica maíz y soja (según los artículos), un caso estatal sin regiones.
   No sirve como serie.
3. **NDSU sí podría servir como serie** para ND: 2006–2026 en Excel con las mismas filas todos los años, 9
   regiones con condados definidos, tierra al alquiler medio incluida, y muchos más cultivos que ERS (trigo de
   primavera, durum, cebada, girasol, canola, poroto). Contras: son proyecciones de principio de año, el
   rinde es un promedio olímpico de 7 años (no el del año), y las listas de condados por región no se
   verificaron antes de 2026.
4. **Comparabilidad con los otros estados**, que no usan presupuestos universitarios en el pipeline.

Comparación indicativa con ERS 2025 (valores de `presupuestos_estados_nuevos.md`; años y definiciones
distintos): maíz de Northern Great Plains, operativos 417,55 y total 786,53 USD/ac con 208 bu/ac; NDSU 2026
South Valley 439,85 directos y 675,40 total con 170 bu/ac. Soja de Northern Great Plains 176,51 operativos y
523,55 total; NDSU South Valley 175,67 y 373,93. Los costos directos se parecen; el total de ERS es bastante
mayor (ERS carga mano de obra no pagada y una tierra más cara).

Fuentes:
- [Projected Crop Budgets — NDSU Extension](https://www.ndsu.edu/agriculture/extension/ag-topics/farm-management/crop-economics/projected-crop-budgets), consultado 2026-11-15
- [2026 Projected Crop Budgets, Excel de las 9 regiones — NDSU](https://www.ndsu.edu/agriculture/sites/default/files/2026-02/SE_26Bud.xls) (y `EC_26Bud.xls`, `NC_26Bud.xls`, `NE_26Bud.xls`, `NW_26Bud_0.xls`, `SW_26Bud.xls` en `2026-02/`; `NV_26Bud.xls`, `SC_26Bud.xls`, `SE_26Bud.xls`, `SV_26Bud.xls` en `2026-01/`), consultado 2026-11-15
- [Projected 2026 Crop Budgets, EC1652 a EC1660 (PDF) — NDSU](https://www.ndsu.edu/agriculture/sites/default/files/2026-02/ec1658.pdf), consultado 2026-11-15
- [East Central 2006 budget (xls) — NDSU](https://www.ndsu.edu/agriculture/sites/default/files/2021-10/EastCent_2006Bud.xls), consultado 2026-11-15
- [Irrigated Crop Budgets — NDSU Extension](https://www.ndsu.edu/agriculture/extension/ag-topics/farm-management/crop-economics/irrigated-crop-budgets), consultado 2026-11-15
- [Corn cost of production projection tool for 2026 now available — farms.com (nota de MSU Extension)](https://www.farms.com/news/corn-cost-of-production-projection-tool-for-2026-now-available-240685.aspx), consultado 2026-11-15
- [Projected cost of production for soybeans tool for 2026 available — farms.com (nota de MSU Extension)](https://www.farms.com/news/projected-cost-of-production-for-soybeans-tool-for-2026-available-240357.aspx), consultado 2026-11-15
- [2026 corn projected cost of production — MSU Extension](https://www.canr.msu.edu/resources/2026-corn-projected-cost-of-production), consultado 2026-11-15 (bloqueado; no se pudo leer)
- [2026 soybean projected cost of production — MSU Extension](https://www.canr.msu.edu/resources/2026-soybean-projected-cost-of-production), consultado 2026-11-15 (bloqueado; no se pudo leer)
- [MI Wheat Program Budget Form 2026 (PDF)](https://miwheat.org/wp-content/uploads/MI-Wheat-Program-Budget-Form-2026.pdf), consultado 2026-11-15 (403; no se pudo leer)
- [Crop Values 2025 Summary, febrero 2026 (txt) — USDA NASS](https://release.nass.usda.gov/reports/cpvl0226.txt), consultado 2026-11-15
- [Aggregating counties to ERS resource regions, reglink.xls — USDA ERS](https://www.ers.usda.gov/sites/default/files/images/reglink.xls), consultado 2026-11-15
- [County codes 2020, North Dakota — US Census Bureau](https://www2.census.gov/geo/docs/reference/codes2020/cou/st38_nd_cou2020.txt) y [Michigan](https://www2.census.gov/geo/docs/reference/codes2020/cou/st26_mi_cou2020.txt), consultado 2026-11-15

Confianza: alta para los precios de NASS 2023–2025, las regiones ERS y la ausencia de cambios de código, y
los valores, supuestos y regiones de NDSU 2026. Media para la cobertura histórica de NDSU (títulos de enlaces;
solo se abrió un Excel viejo, el de 2006). Baja para MSU: solo dos artículos de farms.com con rindes y
escenarios, sin costos; páginas y archivos de MSU no leídos.

Impacto: no cambia `config/` ni el esquema de `economia`. Para sumar MI y ND a `economia` hace falta:
(a) que el humano agregue los estados (hoy no están en `config/config.yaml`); (b) nada en
`region_por_condado()`: cada estado es una sola región ERS y los códigos coinciden con el Census; (c) para el
maíz de MI y ND usar el año comercial de octubre a septiembre si se calculan precios por campaña desde los
mensuales; (d) opcional: si se quiere una serie de costos propia de ND por región, NDSU 2006–2026 (Excel) es
viable, pero sería un cambio de diseño de `economia` que decide el humano.
