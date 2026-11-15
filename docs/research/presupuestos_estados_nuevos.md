# Presupuestos por cultivo de las universidades de OH, NE, MN y KS

Tarea T020 (pro-1), 2026-11-15.

Pregunta: Para IA e IL tenemos los presupuestos de Iowa State (Ag Decision Maker) y de farmdoc
(`precios_margenes.md`). ¿Qué publican las universidades de Ohio (Ohio State), Nebraska (UNL), Minnesota
(UMN / FINBIN) y Kansas (K-State)? Costos por acre de maíz, soja, trigo de invierno y avena, con y sin riego
en NE y KS; desde qué año, en qué formato y dónde. ¿Cómo se comparan con los costos regionales del ERS
(`regiones_ers.md`)? ¿Conviene usarlos o quedarse solo con ERS para que los 7 estados sean comparables?

Respuesta corta: Los cuatro estados tienen fuente propia, pero **no son la misma cosa** y no se pueden poner
en una sola serie comparable:

| estado | quién | qué es | cultivos | riego | desde | formato |
|---|---|---|---|---|---|---|
| OH | Ohio State, Farm Office | presupuesto proyectado (planificación) | maíz, soja, trigo; avena solo orgánica 2024 | no (Ohio es de secano) | 2003 | Excel (`.xlsx` desde 2009, `.xls` antes) |
| NE | UNL, Center for Agricultural Profitability | presupuesto proyectado, solo costos (sin ingresos) | 15 cultivos, 84 presupuestos: maíz, soja, trigo de invierno y de primavera, avena (#55), etc. | sí: secano, pivote y gravedad | 2009 (falta 2013) | PDF generado con el Agricultural Budget Calculator (ABC) |
| KS | K-State, AgManager.info | presupuesto proyectado ("Farm Management Guides") | maíz, soja, trigo, sorgo, girasol, alfalfa, canola, algodón; **sin avena** | sí: secano (6 regiones) y pivote (NW, SW, NC, SC) | proyecciones históricas desde 2016 | PDF por cultivo y región + planilla `.xlsm` |
| KS | KFMA (Kansas Farm Management Association) | costos **reales** de fincas | no verificado | no verificado | selector de años desde 1995 | formulario web, no se pudo leer |
| MN | UMN, Center for Farm Financial Management, FINBIN | costos **reales** de fincas (registros contables) | maíz, soja, trigo de primavera, avena, alfalfa, etc. | no aplica (casi todo secano) | no verificado (el blog de Extension cita 25 años de FINBIN) | informes PDF generados a pedido |

Recomendación: **quedarse con ERS como única serie de costos del paquete `economia`** (ya ponderada por
estado en T005) y usar los presupuestos universitarios solo como referencia documentada, no como columnas.
Razones en "Detalle", punto 6.

Detalle:

**1. Ohio State (OH) — Farm Office, Enterprise Budgets.**

- Página: `https://farmoffice.osu.edu/farm-management/enterprise-budgets`. Lista presupuestos de 2027 (ya
  publicados, archivos del 17 de octubre) hacia atrás hasta 2003. Convencionales: maíz, soja y trigo (y maíz
  para silo hasta 2025; alfalfa hasta 2022). Orgánicos 2026: maíz, soja, trigo, alfalfa y girasol (también en
  `https://offer.osu.edu/resources/enterprise-budgets-and-other-decision-tools`). Avena: solo "Organic Oats
  Production Budget 2024" y un `oats.xls` viejo sin año visible.
- Archivos 2026: `.../enterprisebudgets/corn-con2026%20May27.xlsx`, `soy-con2026%20May27.xlsx`,
  `wheat-con%202026%20May27.xlsx`; 2027: `corn-con2027%20Oct17_0.xlsx`, `soy-con2027%20Oct17.xlsx`,
  `wheat-con%202027%20Oct17.xlsx` (todos bajo
  `https://farmoffice.osu.edu/sites/aglaw/files/site-library/farmmgtpdf/enterprisebudgets/`).
- Un solo presupuesto para todo el estado, sin regiones ni rotaciones explícitas (supone rotación maíz-soja
  con labranza conservacionista, 2000 acres). Tres niveles de rendimiento: tendencia de NASS Ohio −20 %, la
  tendencia y +25 %.
- Se abrió el Excel de maíz 2026 (hoja `corn-cons`, actualizado el 27/5/2026). Columna del rendimiento
  medio (192,5 bu/ac, precio $4,65/bu = futuros CME de diciembre menos $0,25 de base):

  | ítem (USD/ac) | 154 bu | 192,5 bu | 240,6 bu |
  |---|---|---|---|
  | Total variable costs | 534,15 | 593,61 | 679,81 |
  | Total fixed costs | 431,11 | 488,31 | 562,16 |
  | de los cuales Land Charge | 187,00 | 235,00 | 293,00 |
  | Total costs | 965,26 | 1081,93 | 1241,97 |
  | Return above total costs | −184,16 | −116,80 | −48,07 |

  Los costos variables incluyen semilla, fertilizantes, químicos, secado, flete, combustible, reparaciones,
  seguro, trabajos contratados e interés. Los fijos: mano de obra del operador (horas de FINBIN), gestión
  (5 % del ingreso), maquinaria, tierra (alquiler medio del oeste de Ohio) y varios. Los ingresos incluyen un
  pago ARC/PLC estimado ($70/ac).
- Soja y trigo 2026 no se abrieron.

**2. Nebraska (NE) — UNL Center for Agricultural Profitability, Nebraska Crop Budgets.**

- Página: `https://cap.unl.edu/cropbudgets`; metodología en `https://cap.unl.edu/cropbudgets/about`;
  resumen 2026 en `https://agecon.unl.edu/2026-nebraska-crop-budgets-summary-and-key-insights` (redirige a
  `sassa.unl.edu`, 28/1/2026); archivo en `https://cap.unl.edu/cropbudgets/archive/` ("published by the
  University of Nebraska-Lincoln since 2009"): 2009 a 2026 en PDF, **sin 2013**.
- 84 presupuestos de 15 cultivos más un presupuesto de cultivo de cobertura nuevo en 2026. Regiones: Estado,
  Panhandle, Este de Nebraska y Sudoeste. Separados por manejo (labranza, rotación) y por riego: 37 de secano
  y 47 regados (pivote eléctrico o diésel, gravedad). Maíz regado #26–41, soja regada #62–66, trigo de
  invierno de secano #75–79 y regado #80–81, avena #55 (secano, estado, 85 bu).
- **Solo costos**: "The Nebraska budgets provide cost estimates only." No traen precio ni ingreso. Separan
  costo en efectivo (cash) y costo económico (incluye depreciación y costo de oportunidad de la tierra, como
  si el productor fuera dueño).
- Costo por unidad (tabla 6 de la página "about", 2026; efectivo / económico, USD por bushel):

  | # | presupuesto | rinde | efectivo | económico |
  |---|---|---|---|---|
  | 23 | maíz, secano, estado | 145 bu | 3,10 | 4,58 |
  | 30 | maíz, pivote eléctrico, estado | 245 bu | 3,21 | 4,82 |
  | 33 | maíz, pivote eléctrico, estado | 275 bu | 2,94 | 4,38 |
  | 26 | maíz, gravedad (pozo diésel), estado | 245 bu | 3,05 | 4,63 |
  | 60 | soja, secano, estado | 50 bu | 6,01 | 9,85 |
  | 62 | soja, pivote diésel, estado | 67 bu | 7,25 | 13,24 |
  | 75 | trigo de invierno, secano, sudoeste | 55 bu | 4,50 | 6,02 |
  | 80 | trigo de invierno, pivote diésel, Panhandle | 105 bu | 3,48 | 5,34 |

  El resumen 2026 habla del "irrigated soybean budget #60", pero la tabla 6 lista el #60 como de secano: no
  se resolvió.
- El PDF completo 2026 (`2026-nebraska-crop-budgets.pdf`) pesa más de 10 MB y no se pudo abrir con el cliente
  automático: no hay valores por acre verificados para NE.

**3. Kansas (KS) — K-State, AgManager.info, Farm Management Guides.**

- Índice: `https://www.agmanager.info/farm-budgets`. Lista "2027 Non-Irrigated Crops", "2027 Irrigated
  Crops" (PDF fechados el 1/11/2026) y "Historical Farm Budget Projections" de 2016 a 2026. Planilla
  "Spreadsheet Version of 2026 Budgets" (`.xlsm`).
- Secano (`https://agmanager.info/node/34291`): Sudoeste, Noroeste, Centro-Sur, Centro-Norte, Sudeste y
  Noreste. Maíz, sorgo, soja (incluida soja de segunda), trigo HRW continuo y en rotación, alfalfa, girasol,
  canola, algodón. **No hay avena.**
- Regado (`https://www.agmanager.info/farm-budgets/2027-farm-management-guides-irrigated-crops`): maíz,
  soja y sorgo con pivote en NW, SW, Centro-Norte y Centro-Sur; trigo con riego limitado (oeste), alfalfa,
  girasol, canola, algodón.
- Cada PDF trae tres rendimientos (bajo, medio, alto; en los regados con 11,5 / 13,5 / 15,5 pulgadas de agua)
  y tablas de sensibilidad al precio. La tierra se carga como alquiler en efectivo. Se abrieron tres (2027,
  Centro-Norte, rendimiento medio, precio de maíz $4,72 y de soja $12,38):

  | ítem (USD/ac) | maíz secano 120 bu | maíz pivote 240 bu | soja secano 45 bu |
  |---|---|---|---|
  | Total direct expenses | 370,44 | 575,39 | 220,29 |
  | Cash rent | 73,00 | 272,00 | 73,00 |
  | Capital recovery | 57,79 | 256,67 | 56,53 |
  | Total fixed expenses | 130,79 | 528,67 | 129,53 |
  | Total (directos + fijos) | 501,23 | 1104,06 | 349,82 |
  | Returns above total specified expenses | 65,17 | 28,74 | 207,28 |

- La página de proyecciones históricas aclara: "These budgets are a projection of returns and expenses at
  that particular point in time." y "THESE BUDGETS DO NOT REPRESENT ACTUAL RETURNS FOR THAT YEAR"; los
  rendimientos son "best case yields". Para costos reales remite a KFMA: "The KFMA enterprise reports are
  based on real farmer data".
- KFMA (`https://www.agmanager.info/kfma/kfma-enterprise-reports`): la página solo trae un selector de año
  (1995 a 2025) y los informes aparecen al enviar el formulario, cosa que no se pudo hacer. Cultivos,
  regiones y separación por riego **no verificados**.

**4. Minnesota (MN) — UMN Extension y FINBIN.**

- La página de presupuestos de Extension (`https://extension.umn.edu/farm-finance/crop-budgets`) y el informe
  anual del sudoeste del CFFM devolvieron 403 al cliente automático: no se verificó qué cultivos, años ni
  formato tienen. Según el resultado del buscador, se arman con datos de FINBIN; no se pudo confirmar en la
  página.
- FINBIN (`https://finbin.umn.edu/`): "The Farm Financial Management Database", de la Universidad de
  Minnesota (CFFM). Son registros contables reales de los programas de gestión agropecuaria de Minnesota
  (FINBIN "represents ten percent of all Minnesota crop producers", según el blog de Extension del
  4/2/2026). Ya tiene 2025 cargado. En 2025 (todos los estados) hay 3098 fincas; maíz 5701 empresas, soja
  4908, trigo de primavera 736, alfalfa 619, avena 163, **trigo de invierno solo 73**. Los informes se
  generan a pedido por cultivo, tenencia de la tierra y año.
- Ejemplo verificado, informe `https://finbin.umn.edu/Output/908060.pdf` ("Crop Enterprise Analysis",
  maíz en tierra alquilada, Minnesota, creado el 13/9/2025):

  | USD/ac | 2022 | 2023 | 2024 |
  |---|---|---|---|
  | Rendimiento (bu/ac) | 186,75 | 177,67 | 159,75 |
  | Total direct expenses | 718,79 | 783,60 | 681,64 |
  | Total overhead expenses | 81,64 | 109,43 | 105,18 |
  | Total direct & overhead | 800,43 | 893,03 | 786,82 |
  | Net return | 395,35 | 91,83 | 46,78 |

  (Se supone que en este informe de tierra alquilada los "direct expenses" incluyen el alquiler; no se
  verificó la línea en el PDF.)
- "Minnesota Cost and Price Summary" (agosto de 2025,
  `https://finpack.umn.edu/wp-content/uploads/MinnesotaPriceAndCostSummary2025.pdf`): costo de producción
  por unidad, de FINBIN. 2024 / promedio 2022–2024 (USD por bushel): maíz 4,71 / 4,83; soja 11,02 / 11,30;
  trigo de primavera 6,26 / 7,27; avena 3,42 / 3,74. Incluye mano de obra no pagada y gestión, y tierra al
  alquiler medio.

**5. Comparación con ERS.**

ERS 2025 (CSV de maíz y soja del ERS, leídos el 2026-11-15 en `/tmp`, fuera del repo; USD por acre
sembrado; "operativos" = `Total, operating costs`, "total" = `Total, costs listed`):

| región ERS | maíz: rinde | maíz: operativos | maíz: total | soja: rinde | soja: operativos | soja: total |
|---|---|---|---|---|---|---|
| Heartland | 214 | 474,71 | 963,43 | 60 | 255,55 | 703,28 |
| Northern Crescent | 178 | 482,46 | 896,82 | 57 | 250,10 | 616,15 |
| Northern Great Plains | 208 | 417,55 | 786,53 | 44 | 176,51 | 523,55 |
| Prairie Gateway | 168 | 401,25 | 789,28 | 74 | 258,51 | 627,54 |
| Eastern Uplands | 176 | 476,28 | 875,40 | 44 | 292,55 | 640,68 |

Comparación indicativa (años y definiciones distintos; no es un control de calidad):

- **OH maíz** (OSU 2026, 192,5 bu): variables 593,61 contra operativos de Heartland 474,71 (+25 %); total
  1081,93 contra 963,43 (+12 %). Parte de la diferencia puede ser de definición (OSU mete en variables secado, flete y
  seguro de cosecha); no se comparó ítem por ítem.
- **KS maíz secano** (K-State 2027, Centro-Norte, 120 bu): directos 370,44 contra operativos de Prairie
  Gateway 401,25. El total de K-State (501,23) es mucho menor que el de ERS (789,28) porque K-State no carga
  mano de obra ni gastos generales y usa el alquiler en efectivo ($73) en lugar del costo de oportunidad de la
  tierra de ERS ($141). **Maíz regado**: directos 575,39 y total 1104,06, muy por encima de Prairie Gateway.
  ERS no separa riego: su región mezcla secano y riego (la soja de Prairie Gateway rinde 74 bu, más que en
  Heartland).
- **MN maíz** (FINBIN 2024, alquilado, 159,75 bu): 786,82 de directos + generales (con alquiler) contra
  ERS Heartland 2025, 963,43 en total. Los años no coinciden y FINBIN es real, no proyectado.
- **NE**: solo hay costos por bushel (el maíz regado y el de secano tienen un costo en efectivo parecido,
  3,05–3,21 contra 3,10 USD/bu), así que no se pudo comparar por acre.

**6. ¿Usarlos o quedarse con ERS?**

Quedarse con ERS para la serie del pipeline, por estas razones:

1. **Mezclan dos cosas distintas.** OSU, UNL y K-State son presupuestos proyectados ("do not represent
   actual returns"); FINBIN y KFMA son costos reales. ERS también es real (encuesta ARMS). Mezclar
   proyecciones con costos reales en una misma columna `anio` filtraría expectativas del año en vez de
   costos ocurridos.
2. **Definiciones distintas.** Cada universidad separa costos a su manera (variables/fijos, directos/fijos,
   efectivo/económico, con o sin mano de obra del operador y gestión; tierra como alquiler o costo de
   oportunidad). Para que sean comparables entre sí habría que armar una correspondencia ítem por ítem, a mano.
3. **Cobertura despareja.** Desde 2003 (OH), 2009 (NE, sin 2013), 2016 (KS en la web) y FINBIN a pedido;
   avena falta en KS y en OH (salvo orgánica), y el trigo de invierno de MN casi no tiene datos. ERS cubre
   1996–2025 en las 5 regiones con la misma definición.
4. **Formato.** Excel de un solo año por archivo (OH), PDF grandes (NE, KS), un formulario web (KFMA) y una
   página que bloquea clientes automáticos (UMN). Bajarlos de forma reproducible e idempotente cuesta mucho
   más que los CSV de ERS.
5. **IA e IL tampoco usan la serie universitaria** en el pipeline (`precios_margenes.md` deja farmdoc como
   referencia), así que agregarla solo para los estados nuevos rompería la comparabilidad de los 7 estados.

Lo que sí aportan y ERS no tiene:

- **Riego (NE y KS).** UNL y K-State separan secano de pivote y gravedad; ERS no. Para comparar productores
  regados y de secano (§2 del CLAUDE.md, tarea T004) es la única fuente. Propuesta: una tabla de referencia
  chica en `docs/` (no un CSV del pipeline) con el cociente costo regado / costo de secano de cada
  universidad para el último año, para que ML decida si lo usa.
- **Efecto de la rotación**: como en farmdoc, UNL tiene presupuestos por rotación (por ejemplo, #018 maíz de
  secano en rotación maíz-soja y #024 maíz sin labranza tras soja). Sirven de referencia para validar el
  efecto de la rotación que aprenda el modelo.

Fuentes:
- [Enterprise Budgets — Ohio State University Farm Office](https://farmoffice.osu.edu/farm-management/enterprise-budgets), consultado 2026-11-15
- [Corn Production Budget 2026 (xlsx) — OSU Farm Office](https://farmoffice.osu.edu/sites/aglaw/files/site-library/farmmgtpdf/enterprisebudgets/corn-con2026%20May27.xlsx), consultado 2026-11-15
- [Enterprise budgets and other decision tools — OSU OFFER](https://offer.osu.edu/resources/enterprise-budgets-and-other-decision-tools), consultado 2026-11-15
- [Nebraska Crop Budgets — UNL CAP](https://cap.unl.edu/cropbudgets), consultado 2026-11-15
- [About the Nebraska Crop Budgets — UNL CAP](https://cap.unl.edu/cropbudgets/about), consultado 2026-11-15
- [Crop budgets archive — UNL CAP](https://cap.unl.edu/cropbudgets/archive/), consultado 2026-11-15
- [2026 Nebraska Crop Budgets: Summary and Key Insights — UNL](https://agecon.unl.edu/2026-nebraska-crop-budgets-summary-and-key-insights), consultado 2026-11-15
- [2026 Nebraska Crop Budgets (PDF) — UNL CAP](https://cap.unl.edu/sites/unl.edu.ianr.agecon.center-for-ag-profitability/files/media/file/2026-nebraska-crop-budgets.pdf), consultado 2026-11-15 (más de 10 MB; no se pudo leer)
- [Farm Budgets — K-State AgManager.info](https://www.agmanager.info/farm-budgets), consultado 2026-11-15
- [2027 Farm Management Guides for Non-Irrigated Crops — AgManager.info](https://agmanager.info/node/34291), consultado 2026-11-15
- [2027 Farm Management Guides for Irrigated Crops — AgManager.info](https://www.agmanager.info/farm-budgets/2027-farm-management-guides-irrigated-crops), consultado 2026-11-15
- [2024 Historical Budget Projections - Irrigated Crops — AgManager.info](https://agmanager.info/node/39788), consultado 2026-11-15
- [Corn Cost-Return Budget in North Central Kansas, 2027 (PDF)](https://agmanager.info/sites/default/files/wysiwyg/Corn%20Cost-Return%20Budget%20in%20North%20Central%20Kansas__Nov-01-2026_1.pdf), consultado 2026-11-15
- [Irrigated Corn (center-pivot) Cost-Return Budget, North Central Kansas, 2027 (PDF)](https://www.agmanager.info/sites/default/files/wysiwyg/Irrigated%20Corn%20%28center-pivot%29%20Cost-Return%20Budget_North%20Central%20Kansas_Nov-01-2026.pdf), consultado 2026-11-15
- [Soybean Cost-Return Budget in North Central Kansas, 2027 (PDF)](https://agmanager.info/sites/default/files/wysiwyg/Soybean%20Cost-Return%20Budget%20in%20North%20Central%20Kansas__Nov-01-2026.pdf), consultado 2026-11-15
- [KFMA Enterprise Reports — AgManager.info](https://www.agmanager.info/kfma/kfma-enterprise-reports), consultado 2026-11-15 (formulario; sin datos visibles)
- [FINBIN — University of Minnesota](https://finbin.umn.edu/), consultado 2026-11-15
- [FINBIN — About the Data](https://finbin.umn.edu/Home/AboutTheData), consultado 2026-11-15
- [FINBIN Crop Enterprise Analysis, informe 908060 (PDF)](https://finbin.umn.edu/Output/908060.pdf), consultado 2026-11-15
- [Minnesota Cost and Price Summary, agosto 2025 (PDF)](https://finpack.umn.edu/wp-content/uploads/MinnesotaPriceAndCostSummary2025.pdf), consultado 2026-11-15
- [Strategic Farming: Let's talk crops — UMN Extension Crop News](https://blog-crop-news.extension.umn.edu/2026/02/strategic-farming-lets-talk-crops.html), consultado 2026-11-15
- [Crop budgets — UMN Extension](https://extension.umn.edu/farm-finance/crop-budgets), consultado 2026-11-15 (403; no verificado)
- [Commodity Costs and Returns — USDA ERS](https://www.ers.usda.gov/data-products/commodity-costs-and-returns), CSV de maíz y soja, consultado 2026-11-15

Confianza: alta para qué publica cada universidad, el formato y los valores citados de OSU (Excel), K-State
(PDF 2027), FINBIN (informe 908060 y Cost and Price Summary) y ERS 2025. Media para la cobertura histórica
(OSU desde 2003 sale de un índice que se leyó en parte; NE desde 2009 sale de la página del archivo) y para
los costos por bushel de UNL (tabla de la página, no el PDF). Baja o nula para los presupuestos de UMN
Extension y para KFMA (no se pudieron leer).

Impacto: no cambia `config/` ni el esquema de `economia`. Confirma que `economia` siga con los costos de ERS
ponderados por región (T005) para los 7 estados. Propuestas para el humano: (a) si se quiere el efecto del
riego en los costos de NE y KS, armar una tabla de referencia a mano en `docs/` desde UNL y K-State; (b) si
algún día se quieren costos reales por estado, FINBIN (MN) y KFMA (KS) los tienen, pero solo para esos dos
estados y bajarlos requiere generar informes a mano en un navegador.
