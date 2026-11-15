# Presupuestos por cultivo, precios de NASS y regiones ERS de Kentucky

Tarea T080 (pro-1), 2026-11-15.

Pregunta: Para un posible paquete `economia` en Kentucky (KY, FIPS 21): (1) ¿qué presupuestos por cultivo
publica la University of Kentucky (Agricultural Economics) para maíz, soja, trigo y doble cultivo trigo/soja,
desde qué año, en qué formato y dónde? (2) ¿Hay precios recibidos de NASS por estado? (3) ¿En qué región ERS
(Farm Resource Region) cae cada condado y hay cambios de código de condado en `reglink.xls`? Mismo planteo
que `presupuestos_mi_nd.md` (T075). KY **no está** en `config/config.yaml`: esto es research para que el
humano decida una cuarta tanda (`cuarta_tanda.md`).

Respuesta corta:

| quién | qué es | cultivos | regiones | desde | formato |
|---|---|---|---|---|---|
| UK Agricultural Economics, Greg Halich ("Corn and Soybean Budgets", "Wheat Double-Crop Soybean Budget") | presupuesto proyectado (decision aid editable), un caso por región | maíz (siembra directa y labranza convencional), soja de siembra directa, trigo de siembra directa, trigo + soja de segunda (doble cultivo) | maíz y soja: **Western** y **Central Kentucky** (sin lista de condados); trigo: un solo archivo estatal | en línea hoy: maíz/soja 2025 ("Advanced Options", estatal), 2026 y 2027 por región; trigo 2026–2027. Años viejos (hay listados de 2019) **no se encontraron en línea** | Excel `.xlsx`, un archivo por año (y región) |
| UK, Kentucky Farm Business Management (KFBM), "QuickFacts" | costos **ocurridos** de granjas del programa (143–207 granjas), por toda la granja, no por cultivo | rindes medios de maíz, soja de primera, soja de segunda y trigo; costos por acre de toda la granja | estatal + 4 áreas (Purchase, Pennyroyal, Ohio Valley, Lincoln Trail) | QuickFacts 2022–2025 en la página (cada uno con 5 años: el de 2025 trae 2021–2025) | Excel `.xlsx` (2022 Lincoln Trail en PDF) |

- **Precios de NASS:** *Crop Values 2025 Summary* trae el precio medio del año comercial (MYA) de KY de 2023
  a 2025 para maíz, soja, trigo (todo de invierno), heno (alfalfa y otros) y tabaco. **No** hay precio de KY
  para avena, cebada ni sorgo en ese informe. KY entra en el programa mensual de precios solo para maíz, soja
  y heno (no para trigo). La serie 2000–2025 de Quick Stats no se consultó (punto 4).
- **Regiones ERS** (`reglink.xls`): KY tiene 120 condados: **Heartland 26** (el oeste: Purchase, Pennyroyal
  occidental y Ohio Valley) y **Eastern Uplands 94**. **No hay cambios de código**: los 120 FIPS de
  `reglink.xls` coinciden uno a uno con la lista de condados del Census 2020.

Recomendación: igual que T020, T066 y T075, **quedarse con ERS como serie de costos de `economia`** y dejar
los presupuestos de UK como referencia. UK no sirve como serie (solo 2025–2027 en línea, un caso por región
sin condados), y KFBM es costo real pero por granja, no por cultivo. Ojo con ERS en KY: Eastern Uplands
**no tiene serie de trigo** y su avena solo cubre 2023–2025 (`regiones_ers.md`). Detalle en el punto 6.

Detalle:

**1. University of Kentucky — presupuestos de maíz y soja (Greg Halich).**

- Índice: `https://agecon.mgcafe.uky.edu/extension/publications-budgets-decision-aids` (la dirección vieja
  `agecon.ca.uky.edu/budgets` da 404 y redirige al dominio `agecon.mgcafe.uky.edu`). Los archivos siguen bajo
  `.../sites/agecon.ca.uky.edu/files/`.
- Publicaciones en línea (leídas el 2026-11-15; los Excel se abrieron en `/tmp`, fuera del repo):

  | publicación | fecha | archivo | hojas de presupuesto |
  |---|---|---|---|
  | Corn and Soybean Budgets, 2025 Advanced Options (estatal) | 24/3/2025 | `2025 CornSoybeanBudgets(KY).xlsx` | `Corn`, `Soybeans` (+ `Summary(...)`); la página dice que evalúa también labranza convencional y "customized", pero el archivo trae una sola hoja por cultivo con menús desplegables |
  | Corn and Soybean Budgets, 2026 Western Kentucky | 27/4/2026 | `CornSoybeanBudgets(WestKY2026).xlsx` | `No-Till Corn`, `Conv. Tillage Corn`, `No-Till Soybeans` |
  | Corn and Soybean Budgets, 2026 Central Kentucky | 27/4/2026 | `CornSoybeanBudgets(CentralKY2026).xlsx` | ídem |
  | Corn and Soybean Budgets, 2027 Western Kentucky | 8/10/2026 | `cornsoybeanbudgets-westky2027-.xlsx` | ídem |
  | Corn and Soybean Budgets, 2027 Central Kentucky | 8/10/2026 | `cornsoybeanbudgets-centralky2027-.xlsx` | ídem |

- **Años anteriores: no encontrados.** El buscador muestra que una página de UK (decision aids de ANR)
  listaba "Corn and Soybean Budgets – Western Kentucky – 2019" y "Central Kentucky – 2019" (marzo de 2019) y
  "Wheat and Wheat Double-Crop Soybean Budgets 2018–2019", pero esa página hoy no los enlaza y no se encontró
  el archivo. El listado de Halich y el tema "Grains" del sitio solo tienen 2025–2027. El Wayback Machine
  estaba fuera de servicio ("Temporarily Offline") al intentarlo. **Cobertura histórica: no verificada;** lo
  único seguro en línea es 2025–2027.
- **Regiones:** "Western" y "Central" Kentucky, **sin lista de condados** en los archivos ni en las páginas.
  Entre las dos versiones cambian solo algunos precios (N y grano, por la base) y la maquinaria; los rindes,
  la semilla, los herbicidas y el alquiler son iguales.
- **Formato** (2026 y 2027 iguales; 2025 distinto): planilla por acre con ingresos (grano, pago de seguro,
  pago de programas del gobierno: $25/ac), costos variables (semilla, N, P₂O₅, K₂O, cal, herbicidas,
  insecticidas, fungicidas, combustible, reparaciones, mano de obra contratada y del operador, alquiler de
  maquinaria, trabajo contratado, secado, seguro, **alquiler de la tierra en efectivo dentro de los
  variables**, otros, interés operativo 7 %), costos fijos (mano de obra fija, depreciación y gastos de
  maquinaria, impuestos y seguros $10, otros $15) y puntos de equilibrio. El alquiler es $200/ac con la nota
  "Cash rent varies substantially by productivity level and region in Kentucky". En 2025 la tierra se elige
  entre alquiler en efectivo o aparcería (25 %).
- Valores (USD/ac; rinde en bu/ac; "variables" incluye los $200 de alquiler; "resultado" = "Return Above All
  Specified Costs", con $25/ac de pago del gobierno en el ingreso):

  | año | región | cultivo | rinde | precio | variables | maquinaria (dep. y gastos) | resultado |
  |---|---|---|---|---|---|---|---|
  | 2025 | estatal | maíz, siembra directa | 175 | 4,35 | 758,50 | 63,00 | −55,25 |
  | 2025 | estatal | soja, siembra directa | 56 | 10,20 | 522,56 | 46,64 | 6,99 |
  | 2026 | Western | maíz, siembra directa | 175 | 4,75 | 787,03 | 68,11 | −23,88 |
  | 2026 | Western | maíz, convencional | 175 | 4,75 | 768,05 | 94,41 | −31,20 |
  | 2026 | Western | soja, siembra directa | 56 | 11,75 | 541,08 | 40,75 | 76,17 |
  | 2026 | Central | maíz, siembra directa | 175 | 4,70 | 823,68 | 63,48 | −64,66 |
  | 2026 | Central | maíz, convencional | 175 | 4,70 | 803,92 | 89,78 | −71,20 |
  | 2026 | Central | soja, siembra directa | 56 | 11,40 | 546,10 | 41,88 | 50,43 |
  | 2027 | Western | maíz, siembra directa | 175 | 5,00 | 812,51 | 70,73 | −8,25 |
  | 2027 | Western | maíz, convencional | 175 | 5,00 | 794,76 | 95,93 | −15,69 |
  | 2027 | Western | soja, siembra directa | 56 | 12,25 | 550,24 | 44,56 | 91,20 |
  | 2027 | Central | maíz, siembra directa | 175 | 5,00 | 859,40 | 65,33 | −49,73 |
  | 2027 | Central | maíz, convencional | 175 | 5,00 | 840,66 | 90,53 | −56,18 |
  | 2027 | Central | soja, siembra directa | 56 | 12,25 | 556,83 | 45,69 | 83,48 |

  El N cambia entre regiones: 2026 $0,50/unidad (Western) y $0,65 (Central); 2027 $0,57 y $0,76.

**2. University of Kentucky — trigo y doble cultivo trigo/soja.**

- "Wheat Double-Crop Soybean Budget | 2026-2027" (Halich, 8/10/2026), archivo
  `wheatbudgets-2026-2027ky-.xlsx` ("Wheat and Wheat Double-Crop Soybean Budgets 2026-2027", actualizado
  28/9/2026). Un solo caso estatal, dos hojas: `No-Till Wheat` y `No-Till Wheat 2X Soybean` (trigo de
  siembra directa con soja de segunda). Mismo formato que maíz y soja; el alquiler figura como "Cash Rent (Pro
  Rate if Double Cropped)" en la hoja del trigo solo y $200 en la del doble cultivo.

  | hoja | rinde | precio | ingreso total | variables | maquinaria | resultado |
  |---|---|---|---|---|---|---|
  | trigo solo | trigo 80 | 7,00 | 575,00 | 630,54 | 68,08 | −133,62 |
  | trigo + soja de segunda | trigo 80, soja 52 | 7,00 y 12,25 | 1222,00 | 951,31 | 117,16 | 128,53 |

- El presupuesto de trigo **2025–2026 no figura** en las páginas actuales (el buscador mostró una
  "Wheat Double-Crop Soybean Budget | 2024-2025" en el tema "Grains", que hoy ya no aparece). Igual que en
  maíz y soja, solo está el año corriente.
- Complemento: el artículo anual **"Fall <año> Wheat Planting Decision"** (Halich) compara doble cultivo
  trigo/soja con soja de primera en dos regiones: el **Southwest tier** ("roughly between I-24 and I-65",
  mucho doble cultivo) y el **Northwest tier** ("Ohio Valley region", mejores rindes de maíz y soja, menos
  trigo), con alquiler de $200/ac (tierra media) y $250/ac (la mejor). El buscador mostró PDF de 2020 a 2024
  (`Fall 2020 Wheat Planting Decision.pdf` …); se leyeron 2025 y 2026:

  | campaña (artículo) | región, tierra | trigo / soja 2.ª / soja 1.ª (bu/ac) | resultado doble cultivo | resultado soja de primera |
  |---|---|---|---|---|
  | 2026 (sept. 2025) | Southwest, media | 72 / 42 / 50 | −165 | −62 |
  | 2026 (sept. 2025) | Southwest, mejor | 90 / 51 / 60 | −35 | −13 |
  | 2026 (sept. 2025) | Northwest, media | 65 / 42 / 50 | −201 | −62 |
  | 2027 (sept. 2026) | Southwest, media | 77 / 46 / 55 | +39 | +76 |
  | 2027 (sept. 2026) | Southwest, mejor | 95 / 53 / 62 | +191 | +109 |
  | 2027 (sept. 2026) | Northwest, media | 70 / 46 / 55 | −7 | +76 |
  | 2027 (sept. 2026) | Northwest, mejor | 80 / 53 / 62 | +92 | +109 |

  Los signos de 2025 se deducen del texto ("$103 difference in favor of full-season soybeans" con 165 y 62:
  son pérdidas); la página los muestra como viñetas "- $165". Precios supuestos: 2026 trigo $5,60 y soja
  $10,50; 2027 trigo $7,15 y soja $12,65.

**3. Kentucky Farm Business Management (KFBM): costos ocurridos, no presupuestos.**

- Página `https://kfbm.mgcafe.uky.edu/resources/analysis-reporting`: "QuickFacts" anuales (dos hojas de
  Excel) estatales y por área (Purchase, Pennyroyal, Ohio Valley, Lincoln Trail), con enlaces de 2022 a 2025;
  y un "E01 All Farms by Association – 2023" (no abierto).
- Se abrió el estatal 2025 (`2025-ky-quickfacts-ada-compliant_0.xlsx`, publicado 12/11/2026). Trae 2021–2025
  de 207, 199, 192, 155 y 143 granjas: rindes medios (maíz 191,8; soja de primera 46,8; soja de segunda 37;
  trigo 87 bu/ac en 2025), precios recibidos por las granjas (maíz nuevo $4,26, soja $10,62, trigo $5,59 en
  2025) y costos **por acre de toda la granja**: semilla + químicos + fertilizante $286–417, maquinaria
  $202–241, secado $3–7, seguros $40–50 y alquiler en efectivo $197–211 por acre alquilado.
- **No hay costos por cultivo** ni por condado, y la muestra es chica y cambia cada año. Sirve para
  contrastar el orden de magnitud de los presupuestos, no como serie de `economia`. Las áreas de KFBM no
  traen lista de condados en lo que se leyó.

**4. Precios recibidos de NASS por estado.**

- **No se pudo consultar Quick Stats** (sin clave de NASS en este trabajador ni el volcado
  `qs.crops_*.txt.gz`; KY no es un estado del pipeline). La cobertura 2000–2025 **no está verificada**.
- Lo verificado, en *Crop Values 2025 Summary* (`https://release.nass.usda.gov/reports/cpvl0226.txt`, leído
  el 2026-11-15). Precio MYA de KY (2025 preliminar):

  | cultivo (unidad) | KY 2023 / 2024 / 2025 | EE.UU. 2025 |
  |---|---|---|
  | maíz grano ($/bu) | 4,75 / 4,55 / 4,55 | 4,10 |
  | soja ($/bu) | 12,80 / 10,50 / 10,90 | 10,20 |
  | trigo, todo ($/bu) | 6,70 / 5,55 / 5,50 | 4,90 |
  | trigo de invierno ($/bu) | 6,70 / 5,55 / 5,50 | 4,75 |
  | heno, todo ($/t corta) | 191 / 184 / 197 | 160 |
  | heno de alfalfa ($/t corta) | 225 / 219 / 233 | 170 |
  | otros henos ($/t corta) | 178 / 176 / 182 | 138 |
  | tabaco, todo ($/lb) | 2,556 / 2,620 / 2,648 | 2,319 |

  - En KY el trigo "todo" y el de invierno son iguales. El tabaco también viene por clase y tipo (tres filas
    de KY en la tabla "by Class and Type": 2,96–3,03, 2,39–2,56 y 2,72–2,76 $/lb; no se identificó qué tipo
    es cada fila).
  - **Avena, cebada y sorgo: KY no figura** en las tablas de precio de ese informe.
  - Estados del programa mensual de precios (página de "States Included"): **KY entra en maíz, soja y heno**;
    no en trigo, avena, cebada ni sorgo. Sin precios mensuales de trigo, el MYA de trigo de KY sale de otra
    estimación de NASS (no se verificó cuál).
  - Año comercial (MYA, definiciones 2025) para KY: maíz de **septiembre a agosto** (igual que IA, IL, IN y
    OH); soja de septiembre a agosto; **trigo de junio a mayo** (no de julio a junio como MI y ND); **heno de
    mayo a abril**.
- Consulta para completar la serie cuando haya clave (igual que en `precios_margenes.md`):
  `source_desc=SURVEY&statisticcat_desc=PRICE RECEIVED&agg_level_desc=STATE&state_alpha=KY&commodity_desc=CORN&freq_desc=ANNUAL&year__GE=2000`.

**5. Región ERS de cada condado y cambios de código.**

De `reglink.xls` de ERS (`https://www.ers.usda.gov/sites/default/files/images/reglink.xls`, "Aggregating
counties to ERS resource regions", última modificación del archivo 2017-10-25; leído el 2026-11-15 en `/tmp`):

| estado | condados en reglink | regiones (condados) |
|---|---|---|
| KY (21) | 120 | Heartland 26, Eastern Uplands 94 |

- **KY, Heartland** (oeste del estado): Ballard (21007), Caldwell (21033), Calloway (21035), Carlisle (21039),
  Christian (21047), Crittenden (21055), Daviess (21059), Fulton (21075), Graves (21083), Hancock (21091),
  Henderson (21101), Hickman (21105), Hopkins (21107), Livingston (21139), Logan (21141), Lyon (21143),
  McCracken (21145), McLean (21149), Marshall (21157), Muhlenberg (21177), Ohio (21183), Simpson (21213),
  Todd (21219), Trigg (21221), Union (21225), Webster (21233).
- **KY, Eastern Uplands**: los otros 94 condados (centro y este, incluidos Warren, Barren, Hardin, Fayette y
  los Apalaches).
- **Cambios de código: ninguno.** Se compararon los FIPS de `reglink.xls` con la lista del Census 2020
  (`st21_ky_cou2020.txt`): 120 y 120 condados, los mismos códigos.
- ERS (`regiones_ers.md`): Heartland tiene maíz 1996–2025, soja 1997–2025, trigo 1998–2025 y avena
  2005–2025; **Eastern Uplands tiene maíz y soja, no tiene trigo y su avena es solo 2023–2025**. En KY el trigo
  se ponderaría solo con Heartland (la regla de cobertura mínima del 50 % de `process.py` lo permite si el
  oeste pesa más de la mitad del área de trigo, que es lo esperable).
- **Pesos por área sembrada no calculados**: requieren `ACRES PLANTED` de NASS por condado (no disponible acá,
  punto 4). Por cantidad de condados KY es 22 % Heartland, pero el maíz, la soja y el trigo se concentran en
  el oeste (Purchase, Pennyroyal, Ohio Valley), así que el peso de Heartland por área será mucho mayor.
- Comparación de regiones: el "Western Kentucky" de los presupuestos de UK y los tiers de "Wheat Planting
  Decision" (Southwest entre la I-24 y la I-65, Northwest = Ohio Valley) se parecen a la parte Heartland de
  ERS, pero ninguno trae lista de condados: **no se puede cruzar condado por condado**.
- Ojo con Eastern Uplands: según `reglink.xls` abarca 410 condados de 13 estados (KY 94, TN 62, WV 55, AR 40,
  VA 37, MO 27, OK 25, AL 21, OH 18, NC 17, PA 13, GA 11, MD 2), así que su serie ERS no es de KY; su soja 2025 tiene rinde
  44 bu/ac (`presupuestos_estados_nuevos.md`), contra 56 bu/ac en los presupuestos de UK y 46,8 en KFBM 2025.

**6. ¿Usarlos o quedarse con ERS?**

1. **Los presupuestos de UK son proyecciones**, no costos ocurridos; ERS (ARMS) y KFBM sí lo son.
2. **Sin serie**: en línea solo 2025–2027 (maíz/soja) y 2026–2027 (trigo). Los años viejos existieron (2019
   al menos) pero no se encontraron.
3. **Regiones sin condados**: Western/Central Kentucky no se pueden asignar a FIPS sin una definición que no
   publican.
4. **Definición distinta**: UK mete el alquiler de la tierra ($200/ac fijo) en los costos variables y suma
   $25/ac de pagos del gobierno al ingreso; ERS separa operativos y propiedad y no cuenta pagos.
5. **Lo que UK sí aporta y ERS no**: el **doble cultivo trigo/soja** como unidad (en KY es la forma normal del
   trigo, ver `cdl_precision_ky.md`) y una referencia de cuánto cambia el resultado frente a soja de primera.
   Si `economia` quiere un margen del doble cultivo, la forma más simple sería trigo (ERS Heartland) + soja
   (ERS) con un descuento de rinde de la soja de segunda; los números de UK sirven para documentar ese
   supuesto.

Comparación indicativa con ERS 2025 (valores de `presupuestos_estados_nuevos.md`; años y definiciones
distintos): maíz de Heartland, operativos 474,71 y total 963,43 USD/ac con 214 bu/ac; UK 2026 Western, maíz
de siembra directa, variables 787,03 con alquiler (≈ 587 sin los $200) y 175 bu/ac. Soja de Eastern Uplands,
operativos 292,55 y total 640,68 con 44 bu/ac; UK 2026 Central, soja, variables 546,10 (≈ 346 sin alquiler)
con 56 bu/ac. Los variables de UK sin la tierra quedan por encima de los operativos de ERS (UK carga mano de
obra del operador, seguro y otros dentro de los variables); no se comparó ítem por ítem.

Fuentes:
- [Publications, Budgets & Decision Aids — UK Agricultural Economics](https://agecon.mgcafe.uky.edu/extension/publications-budgets-decision-aids), consultado 2026-11-15
- [Corn and Soybean Budgets | 2025 Advanced Options — UK](https://agecon.mgcafe.uky.edu/budget/corn-and-soybean-budgets-2025-advanced-options) y su [Excel](https://agecon.ca.uky.edu/sites/agecon.ca.uky.edu/files/2025%20CornSoybeanBudgets%28KY%29.xlsx), consultado 2026-11-15
- [Corn and Soybean Budgets | 2026 Western Kentucky — UK](https://agecon.mgcafe.uky.edu/articles/corn-and-soybean-budgets-2026-western-kentucky) y su [Excel](https://agecon.mgcafe.uky.edu/sites/agecon.ca.uky.edu/files/CornSoybeanBudgets%28WestKY2026%29.xlsx), consultado 2026-11-15
- [Corn and Soybean Budgets | 2026 Central Kentucky — UK](https://agecon.mgcafe.uky.edu/budget/corn-and-soybean-budgets-2026-central-kentucky) y su [Excel](https://agecon.mgcafe.uky.edu/sites/agecon.ca.uky.edu/files/CornSoybeanBudgets%28CentralKY2026%29.xlsx), consultado 2026-11-15
- [Corn and Soybean Budgets | 2027 Western Kentucky — UK](https://agecon.mgcafe.uky.edu/articles/corn-and-soybean-budgets-2027-western-kentucky) y su [Excel](https://agecon.mgcafe.uky.edu/sites/agecon.ca.uky.edu/files/cornsoybeanbudgets-westky2027-.xlsx), consultado 2026-11-15
- [Corn and Soybean Budgets | 2027 Central Kentucky — UK](https://agecon.mgcafe.uky.edu/articles/corn-and-soybean-budgets-2027-central-kentucky) y su [Excel](https://agecon.mgcafe.uky.edu/sites/agecon.ca.uky.edu/files/cornsoybeanbudgets-centralky2027-.xlsx), consultado 2026-11-15
- [Wheat Double-Crop Soybean Budget | 2026-2027 — UK](https://agecon.mgcafe.uky.edu/articles/wheat-double-crop-soybean-budget-2026-2027) y su [Excel](https://agecon.mgcafe.uky.edu/sites/agecon.ca.uky.edu/files/wheatbudgets-2026-2027ky-.xlsx), consultado 2026-11-15
- [Fall 2025 Wheat Planting Decision — UK](https://agecon.mgcafe.uky.edu/articles/fall-2025-wheat-planting-decision) y [Fall 2026 Wheat Planting Decision — UK](https://agecon.mgcafe.uky.edu/articles/fall-2026-wheat-planting-decision), consultado 2026-11-15
- [Decision Aids, Budgets & Calculators — UK ANR](https://anr.ca.uky.edu/agent-resources/decision-aids), consultado 2026-11-15 (la página abrió, pero ya no lista los presupuestos de 2019 que mostraba el buscador)
- [Analysis Reporting (QuickFacts) — Kentucky Farm Business Management](https://kfbm.mgcafe.uky.edu/resources/analysis-reporting) y el [QuickFacts 2025 estatal (xlsx)](https://kfbm.mgcafe.uky.edu/sites/kfbm.ca.uky.edu/files/2025-ky-quickfacts-ada-compliant_0.xlsx), consultado 2026-11-15
- [Crop Values 2025 Summary, febrero 2026 (txt) — USDA NASS](https://release.nass.usda.gov/reports/cpvl0226.txt), consultado 2026-11-15
- [Aggregating counties to ERS resource regions, reglink.xls — USDA ERS](https://www.ers.usda.gov/sites/default/files/images/reglink.xls), consultado 2026-11-15
- [County codes 2020, Kentucky — US Census Bureau](https://www2.census.gov/geo/docs/reference/codes2020/cou/st21_ky_cou2020.txt), consultado 2026-11-15

Confianza: alta para los precios de NASS 2023–2025, las regiones ERS, la ausencia de cambios de código, y los
valores y el formato de los presupuestos de UK 2025–2027 (Excel abiertos). Media para KFBM (solo se abrió el
estatal 2025). Baja para la cobertura histórica de UK: solo se sabe que hubo presupuestos de 2019 (por el
buscador); no se encontraron archivos anteriores a 2025.

Impacto: no cambia `config/` ni el esquema de `economia`. Para sumar KY a `economia` hace falta: (a) que el
humano agregue el estado (hoy no está en `config/config.yaml`); (b) nada de código nuevo en
`region_por_condado()` más allá de leer `reglink.xls` (Heartland 26 y Eastern Uplands 94; códigos iguales al
Census); (c) aceptar que el trigo de KY se pondere solo con Heartland (Eastern Uplands no tiene serie de
trigo) y que la avena de Eastern Uplands sea solo 2023–2025; (d) usar el año comercial de **junio a mayo**
para el trigo de KY si se calculan precios por campaña desde los mensuales (y recordar que KY no tiene precios
mensuales de trigo); (e) opcional: decidir si `economia` agrega un margen de doble cultivo trigo/soja, que en
KY importa más que el trigo solo.
