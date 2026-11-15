# Costos por acre de maíz y soja con riego y en secano (UNL, K-State) y FINBIN/KFMA

Tarea T142 (pro-2), 2026-11-15. Fila 22 de `coordinacion/para_decidir.md`. **Solo referencia**: no cambia
ningún CSV de `data/processed/` ni el paquete `economia` (que sigue con ERS, ver `presupuestos_estados_nuevos.md`).

Pregunta: ¿Cuánto cuesta por acre producir maíz y soja con riego y en secano en Nebraska y Kansas, según los
presupuestos de la Universidad de Nebraska-Lincoln (UNL) y de Kansas State (K-State), año por año? ¿Qué
publican FINBIN y KFMA como referencia de costos reales?

Respuesta corta: Con riego de pivote, el costo total por acre de maíz es **≈ 1,4 a 2,0 veces** el de secano
(UNL, mediana de los presupuestos del estado, 2010–2026) y **≈ 2,0 a 2,2 veces** en K-State (Centro-Norte,
2016–2027). En soja la relación es ≈ 1,4–2,0 (UNL) y ≈ 1,6–2,2 (K-State). La diferencia está más en los
costos fijos y la tierra (pivote, pozo, alquiler o valor de la tierra regada) que en los insumos. Todos son
**presupuestos proyectados**, no costos ocurridos. El detalle por presupuesto está en `costos_riego.csv`
(499 filas: 452 de UNL y 47 de K-State), extraído de los PDF con `costos_riego_extraer.py`.

## Detalle

### 1. Cómo se armó

- Se bajaron los 17 PDF del archivo de UNL (`https://cap.unl.edu/cropbudgets/archive/`) y los 49 PDF de
  maíz y soja del Centro-Norte de Kansas de AgManager.info (presupuestos 2027 y "Historical Farm Budget
  Projections" 2016–2026). Los PDF quedaron fuera del repo (`/tmp`); se convirtieron con `pdftotext -layout`
  y se leyeron con `docs/research/costos_riego_extraer.py` (cómo correrlo, en el encabezado del script).
- Cada número del CSV sale del PDF cuya URL está en la columna `url` (consultado 2026-11-15).
- `anio` es el año del presupuesto (el que figura en el título), no el de publicación: K-State publica en
  octubre/noviembre el presupuesto del año siguiente.
- Controles a mano: UNL 2025 #30 (maíz, pivote eléctrico, 245 bu) total 1.097,93 USD/ac, igual al PDF;
  K-State 2027 Centro-Norte coincide con los valores ya citados en `presupuestos_estados_nuevos.md`
  (maíz secano 501,23; maíz pivote 1.104,06; soja secano 349,82).

### 2. Definiciones (no son comparables entre fuentes)

| fuente | `costo_operativo_usd_ac` | `costo_total_usd_ac` | tierra |
|---|---|---|---|
| UNL 2010–2025 | "Total Operating and Use Related Ownership Costs" (incluye depreciación e interés de la maquinaria usada) — solo desde 2015 en el PDF | "Total Cost per Acre Including Overhead" | costo de oportunidad del valor de la tierra (≈ 3 %) + impuesto inmobiliario; la tierra regada vale más |
| UNL 2026 (Agricultural Budget Calculator) | "Total Operating Costs" | "Total Economic Cost" | "Land Opportunity Cost" + impuestos |
| K-State | "Total direct expenses" | directos + "Total fixed expenses" (sin mano de obra del operador ni gastos generales) | alquiler en efectivo (`alquiler_usd_ac`) |

UNL también da costo por bushel en efectivo (`costo_efectivo_usd_bu`, 2020–2025) y económico
(`costo_total_usd_bu`). K-State trae el precio supuesto (`precio_usd_bu`).

### 3. Nebraska (UNL), mediana de `costo_total_usd_ac` de los presupuestos de cada tipo

Todas las regiones juntas (estado, Este, Panhandle, Sudoeste) y todos los manejos; entre paréntesis, la
cantidad de presupuestos. "gravedad" = riego por surcos.

| año | maíz secano | maíz pivote | maíz gravedad | soja secano | soja pivote | soja gravedad | maíz pivote/secano | soja pivote/secano |
|---|---|---|---|---|---|---|---|---|
| 2010 | 346 (4) | 697 (5) | 695 (2) | 214 (3) | 388 (4) | 389 (1) | 2,0 | 1,8 |
| 2011 | 396 (4) | 788 (5) | 811 (2) | 238 (3) | 459 (4) | 468 (1) | 2,0 | 1,9 |
| 2012 | 476 (3) | 918 (5) | 942 (1) | 276 (3) | 512 (4) | 539 (1) | 1,9 | 1,9 |
| 2013 | sin presupuesto (UNL no publicó) | | | | | | | |
| 2014 | 475 (2) | 945 (5) | 825 (2) | 333 (3) | 655 (4) | 647 (1) | 2,0 | 2,0 |
| 2015 | 509 (5) | 984 (6) | 955 (3) | 371 (3) | 656 (4) | 661 (1) | 1,9 | 1,8 |
| 2016 | 501 (7) | 936 (6) | 895 (3) | 366 (3) | 631 (4) | 631 (1) | 1,9 | 1,7 |
| 2017 | 562 (6) | 893 (6) | 831 (3) | 352 (3) | 595 (4) | 599 (1) | 1,6 | 1,7 |
| 2018 | 444 (6) | 759 (5) | 760 (3) | 315 (3) | 534 (4) | 516 (1) | 1,7 | 1,7 |
| 2019 | 468 (11) | 802 (8) | 772 (4) | 336 (3) | 545 (4) | 537 (1) | 1,7 | 1,6 |
| 2020 | 525 (10) | 794 (10) | 794 (4) | 374 (3) | 567 (6) | 566 (1) | 1,5 | 1,5 |
| 2021 | 522 (10) | 775 (10) | 761 (4) | 389 (3) | 557 (6) | 554 (1) | 1,5 | 1,4 |
| 2022 | 598 (10) | 944 (11) | 890 (4) | 428 (3) | 639 (6) | 626 (1) | 1,6 | 1,5 |
| 2023 | 745 (10) | 1182 (11) | 1135 (4) | 494 (3) | 763 (6) | 758 (1) | 1,6 | 1,5 |
| 2024 | 713 (10) | 1147 (11) | 1067 (4) | 513 (3) | 794 (6) | 790 (1) | 1,6 | 1,5 |
| 2025 | 696 (10) | 1113 (11) | 1060 (4) | 490 (3) | 798 (4) | 777 (1) | 1,6 | 1,6 |
| 2026 | 866 (6) | 1194 (10) | 1134 (3) | 493 (1) | 859 (3) | — | 1,4 | 1,7 |

Ojo:

- Las medianas mezclan regiones y rendimientos distintos (el maíz de secano va de ≈ 85 bu en el oeste a
  195 bu en el este); son para ver el orden de magnitud y la relación riego/secano, no para usar como dato.
- 2009: el PDF (`Crop-Budgets-ec09-872.pdf`) tiene otro formato (planillas en blanco para completar) y el
  extractor no lo lee: **sin datos de 2009**.
- 2026: el PDF del archivo trae el detalle completo solo de una parte de los presupuestos (por ejemplo, no
  están las hojas de #023, #027, #032 ni #062); de esos solo está el costo por bushel en la tabla resumen del
  PDF, que no se cargó al CSV. Por eso 2026 tiene menos presupuestos.
- 29 filas de UNL tienen `riego = sin_dato`: el título no dice si es secano o riego (por ejemplo, "Corn, Ridge-Till
  ... 230 bu" en 2012, o el maíz "Ecofallow" del Sudoeste, que es de secano). No se completaron a mano.
- El costo económico de UNL incluye el costo de oportunidad de la tierra: buena parte de la diferencia
  pivote/secano viene de que la tierra regada vale más.

### 4. Kansas (K-State), Centro-Norte, rendimiento medio

USD/ac. Total = directos + fijos (incluye el alquiler). Fuente: un PDF por fila, URL en `costos_riego.csv`.

| año | maíz secano (bu) | maíz secano total | maíz pivote (bu) | maíz pivote total | soja secano (bu) | soja secano total | soja pivote (bu) | soja pivote total | maíz pivote/secano | soja pivote/secano |
|---|---|---|---|---|---|---|---|---|---|---|
| 2016 | 107 | 385,35 | 213 | 757,06 | 36 | 304,72 | 61 | 494,66 | 2,0 | 1,6 |
| 2017 | 107 | 375,97 | 213 | 771,80 | 36 | 319,27 | 61 | 532,99 | 2,1 | 1,7 |
| 2018 | 120 | 390,26 | 240 | 810,11 | 41 | 301,50 | 65 | 590,06 | 2,1 | 2,0 |
| 2019 | 120 | 396,05 | 240 | 833,13 | 41 | 301,67 | 65 | 595,92 | 2,1 | 2,0 |
| 2020 | 120 | 403,50 | 240 | 814,49 | 41 | 303,58 | 65 | 571,47 | 2,0 | 1,9 |
| 2021 | 120 | 378,05 | 240 | 793,05 | 41 | 268,47 | — | no encontrado | 2,1 | — |
| 2022 | 120 | 440,43 | 240 | 936,05 | 41 | 328,75 | 75 | 650,35 | 2,1 | 2,0 |
| 2023 | 120 | 561,14 | 240 | 1159,28 | 41 | 412,17 | 75 | 785,67 | 2,1 | 1,9 |
| 2024 | 120 | 500,40 | 240 | 1017,53 | 45 | 400,73 | 75 | 733,12 | 2,0 | 1,8 |
| 2025 | 120 | 495,63 | 240 | 1014,01 | 45 | 390,85 | 75 | 742,82 | 2,0 | 1,9 |
| 2026 | 120 | 457,84 | 240 | 990,27 | 45 | 334,41 | 75 | 698,97 | 2,2 | 2,1 |
| 2027 | 120 | 501,23 | 240 | 1104,06 | 45 | 349,82 | 75 | 779,33 | 2,2 | 2,2 |

Ojo:

- 2021, soja con pivote: la página "2021 Historical Budget Projections - Irrigated Crops" no tiene el PDF de
  soja del Centro-Norte (solo el de maíz). **No encontrado.**
- 2016 (pivote): el extractor leyó `alquiler_usd_ac = 0` en los dos PDF regados de 2016
  (`Irrigated_Corn_NC.pdf`, `Irrigated_Soybeans_NC.pdf`); no se revisó a mano si el formato de ese año pone el
  alquiler en otra línea. El total (directos + fijos) sí sale de las líneas "TOTAL".
- 2018: hay además dos PDF de enero de 2018 (KFMG, escenarios bajo/medio/alto) que el extractor no lee; se
  usaron los de octubre de 2017 (presupuesto 2018).
- Solo se extrajo el Centro-Norte (la única región con secano y pivote para los dos cultivos en todos los
  años). K-State publica también NW, SW y Centro-Sur con pivote y seis regiones de secano: el mismo
  extractor sirve cambiando el patrón "North Central KS".
- K-State advierte: "THESE BUDGETS DO NOT REPRESENT ACTUAL RETURNS FOR THAT YEAR".

### 5. FINBIN y KFMA (costos reales, como referencia)

**FINBIN** (Universidad de Minnesota, Center for Farm Financial Management, `https://finbin.umn.edu/`):

- Qué publica: registros contables reales de fincas que participan de programas de gestión (sobre todo
  Minnesota, más otros estados que aportan datos). Informes "Crop Enterprise Analysis" por cultivo, tenencia
  (propia, alquilada), año y región, con rendimiento, costos directos y generales por acre y retorno neto. Ya
  tiene 2025 (ver `presupuestos_estados_nuevos.md`, punto 4).
- Acceso: web gratuita; los informes se generan a pedido con un formulario y salen como PDF
  (`https://finbin.umn.edu/Output/<n>.pdf`). No hay API ni descarga masiva documentada: no es reproducible
  desde un script sin automatizar el formulario.
- Riego: FINBIN permite filtrar por estado; no se verificó en esta tarea si hay suficientes fincas regadas de
  NE o KS para un informe de riego.
- Licencia: no se encontró una licencia abierta explícita en la página; los informes son agregados para
  proteger a los productores. **No verificado**: antes de redistribuir números habría que preguntar al CFFM.

**KFMA** (Kansas Farm Management Association, a través de K-State,
`https://www.agmanager.info/kfma/kfma-enterprise-reports`):

- Qué publica: "enterprise reports" con costos e ingresos reales de las fincas socias de KFMA ("based on real
  farmer data", según AgManager), con un selector de años de 1995 a 2025.
- Acceso: la página carga los informes con un formulario; en T020 y en esta tarea el cliente automático no
  pudo enviarlo. Cultivos, regiones y separación riego/secano **no verificados**.
- Licencia: no indicada en la página consultada. **No verificado.**

Para comparar costos proyectados (UNL, K-State) con reales, KFMA sería la referencia natural en KS (mismos
autores, mismas regiones); hace falta que una persona baje los informes desde un navegador.

Fuentes:
- [Crop budgets archive — UNL CAP](https://cap.unl.edu/cropbudgets/archive/), consultado 2026-11-15 (los 17 PDF, URL por fila en `costos_riego.csv`)
- [About the Nebraska Crop Budgets — UNL CAP](https://cap.unl.edu/cropbudgets/about), consultado 2026-11-15
- [Farm Budgets — K-State AgManager.info](https://www.agmanager.info/farm-budgets), consultado 2026-11-15
- [Historical Farm Budget Projections — AgManager.info](https://www.agmanager.info/farm-budgets/historical-farm-budget-projections-2016-2024), consultado 2026-11-15 (páginas por año 2016–2026; URL de cada PDF en `costos_riego.csv`)
- [2027 Farm Management Guides, Irrigated Crops — AgManager.info](https://www.agmanager.info/farm-budgets/2027-farm-management-guides-irrigated-crops), consultado 2026-11-15
- [2027 Farm Management Guides, Non-Irrigated Crops — AgManager.info](https://agmanager.info/node/34291), consultado 2026-11-15
- [KFMA Enterprise Reports — AgManager.info](https://www.agmanager.info/kfma/kfma-enterprise-reports), consultado 2026-11-15 (formulario; sin datos visibles)
- [FINBIN — University of Minnesota](https://finbin.umn.edu/), consultado 2026-11-15 (según T020; no se volvió a abrir)

Confianza: alta para los números del CSV (salen tal cual de los PDF, con dos controles a mano); media para
las medianas de UNL (mezclan regiones y manejos) y para la clasificación riego/secano por título; baja para
el acceso y la licencia de FINBIN y KFMA (no se pudieron verificar).

Impacto: ninguno en `config/` ni en `data/processed/`. Es una tabla de referencia para el equipo de ML y para
la herramienta (comparar productores regados y de secano en NE y KS, §2 del CLAUDE.md). Si el humano quiere
usarla en el pipeline, sería una tarea aparte con su propio esquema.
