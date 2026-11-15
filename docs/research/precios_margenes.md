# Precios y márgenes: NASS precios recibidos, ERS costos y retornos, presupuestos de farmdoc

Pregunta: Precios y márgenes: precios recibidos de NASS por estado, costos y retornos del USDA ERS, y presupuestos por cultivo de Iowa State (Ag Decision Maker) o Illinois (farmdoc).

Respuesta corta: (1) **Precios recibidos de NASS por estado**: están en Quick Stats (`source_desc=SURVEY`, `statisticcat_desc=PRICE RECEIVED`, `agg_level_desc=STATE`) para IA, IL e IN, anuales por año comercial (`reference_period_desc=MARKETING YEAR`) y mensuales. Los `short_desc` son `CORN, GRAIN - PRICE RECEIVED, MEASURED IN $ / BU`, `SOYBEANS - PRICE RECEIVED, MEASURED IN $ / BU`, `WHEAT, WINTER - PRICE RECEIVED, MEASURED IN $ / BU`, `OATS - PRICE RECEIVED, MEASURED IN $ / BU`, `HAY, ALFALFA - PRICE RECEIVED, MEASURED IN $ / TON` y `HAY, (EXCL ALFALFA) - PRICE RECEIVED, MEASURED IN $ / TON`. Cubren 2000–2025 en los tres estados, salvo trigo en Iowa (hasta 2019) y avena en Indiana (hasta 2015). No existen por condado. (2) **Costos y retornos del USDA ERS**: un CSV por cultivo (maíz, soja, trigo, avena; no hay heno ni alfalfa) en dólares por acre sembrado, por región ERS. El Corn Belt cae en la región `Heartland`. Maíz y soja tienen la serie actual desde 1996 y 1997 hasta 2025, más un pronóstico 2026F–2027F que solo trae el total de EE.UU. (3) **Presupuestos**: farmdoc (Universidad de Illinois) publica presupuestos anuales para cuatro zonas de Illinois (norte, centro de alta productividad, centro de baja productividad y sur), separados por rotación (maíz después de soja, maíz después de maíz, soja después de maíz, soja después de soja, trigo, soja de segunda). Sirven directamente para comparar rotaciones. Los de Iowa State (Ag Decision Maker A1-20) no se pudieron leer de forma automática: el sitio pide una prueba antirobots (Anubis) y devuelve 403.

Detalle:

**1. Precios recibidos de NASS (Quick Stats, nivel estado).**

Cómo se verificó: se escaneó el volcado completo de cultivos de Quick Stats que ya bajó el paquete `cultivos` (`data/raw/cultivos/nass/qs.crops_20261113.txt.gz`, de `https://www.nass.usda.gov/sites/default/files/datasets/`), filtrando `STATISTICCAT_DESC = PRICE RECEIVED`, `DOMAIN_DESC = TOTAL` y los estados IA, IL, IN y US. El archivo pesa 1,1 GB y no sirve como cita verificable: las citas de abajo son de la página del programa de precios de NASS.

Filas anuales (`freq_desc=ANNUAL`, `reference_period_desc=MARKETING YEAR`, `agg_level_desc=STATE`):

| `short_desc` | IA | IL | IN |
|---|---|---|---|
| `CORN, GRAIN - PRICE RECEIVED, MEASURED IN $ / BU` | 1867–2025 | 1909–2025 | 1909–2025 |
| `SOYBEANS - PRICE RECEIVED, MEASURED IN $ / BU` | 1924–2025 | 1940–2025 | 1940–2025 |
| `WHEAT - PRICE RECEIVED, MEASURED IN $ / BU` | 1949–2019 | 1949–2025 | 1949–2025 |
| `WHEAT, WINTER - PRICE RECEIVED, MEASURED IN $ / BU` | 1949–2019 | 1949–2025 | 1949–2025 |
| `OATS - PRICE RECEIVED, MEASURED IN $ / BU` | 1866–2025 | 1949–2025 | 1949–2015 |
| `HAY - PRICE RECEIVED, MEASURED IN $ / TON` | 1949–2025 | 1949–2025 | 1949–2025 |
| `HAY, ALFALFA - PRICE RECEIVED, MEASURED IN $ / TON` | 1989–2025 | 1989–2025 | 1989–2025 |
| `HAY, (EXCL ALFALFA) - PRICE RECEIVED, MEASURED IN $ / TON` | 1989–2025 | 1989–2025 | 1989–2025 |

- El rango indica el primer y el último año con fila; puede haber años sueltos sin fila adentro del rango.
- También hay filas mensuales (`freq_desc=MONTHLY`, `reference_period_desc` = `JAN` ... `DEC`) por estado para los mismos `short_desc`, hasta 2026. En Indiana, el heno mensual termina en 2019.
- Códigos que aparecen en `VALUE`: `(D)` en avena y trigo mensual de IL e IN; `(S)` en avena mensual de IL; `(NA)` en trigo anual de IA y en heno mensual de IN. Según el CLAUDE.md §4 van vacíos, con `flag_nass`.
- Clave de unión: estos datos solo existen por estado (`fips_estado`), como Crop Progress.
- El año comercial del maíz y la soja empieza el 1 de septiembre del año de cosecha. Para un margen por año de cosecha corresponde usar la fila `MARKETING YEAR` de ese `anio`. Cuál precio usar (año comercial o un mes en particular) lo decide el equipo de modelo.
- Consulta por API (requiere `NASS_API_KEY`): `source_desc=SURVEY&statisticcat_desc=PRICE RECEIVED&agg_level_desc=STATE&state_alpha=IA&commodity_desc=CORN&freq_desc=ANNUAL&year__GE=2000`. Sin clave sirve el mismo volcado `qs.crops_*.txt.gz`.

**2. USDA ERS Commodity Costs and Returns.**

- Página: `https://www.ers.usda.gov/data-products/commodity-costs-and-returns` (actualizada el 11/10/2026). Hay un CSV y un XLSX por cultivo. Por ejemplo, maíz `https://www.ers.usda.gov/media/4962/corn.csv` y soja `https://www.ers.usda.gov/media/4976/soybeans.csv` (con el parámetro `?v=` de la página). La versión de los CSV es del 10/1/2026 y la próxima sale el 5/3/2027.
- Columnas del CSV: `Commodity, Category, Item, Units, Size, Region, Country, Year, Value, Survey base year`.
- Regiones: `U.S. total`, `Heartland`, `Northern Crescent`, `Northern Great Plains`, `Prairie Gateway`, `Eastern Uplands`, `Southern Seaboard`. IA, IL e IN están en la región `Heartland` de las Farm Resource Regions del ERS. Esta asignación sale de la definición de regiones del ERS y no se verificó con una cita en esta ronda. No hay datos por estado ni por condado.
- Ítems útiles (unidad `dollars per planted acre`, salvo que se indique otra): `Total, gross value of production`; `Total, operating costs` (incluye `Seed`, `Fertilizer`, `Chemicals`, `Custom services`, `Fuel, lube, and electricity`, `Repairs`, `Interest on operating capital`); `Total, allocated overhead` (incluye `Opportunity cost of land`, `Opportunity cost of unpaid labor`, `Capital recovery of machinery and equipment`, `Taxes and insurance`, `General farm overhead`, `Hired labor`); `Total, costs listed`; `Value of production less operating costs`; `Value of production less total costs listed`; `Price` (`dollars per bushel at harvest`); `Yield` (`bushels per planted acre`).
- Ejemplo, Heartland 2025, del CSV bajado el 2026-11-14:

| Ítem | Maíz | Soja |
|---|---|---|
| Yield (bu/acre sembrado) | 214.00 | 60.00 |
| Price (USD/bu en cosecha) | 3.92 | 9.80 |
| Total, gross value of production | 839.24 | 587.36 |
| Total, operating costs | 474.71 | 255.55 |
| Value of production less operating costs | 364.53 | 331.81 |
| Total, costs listed | 963.43 | 703.28 |
| Value of production less total costs listed | −124.19 | −115.92 |

- Rango de años de la serie actual: maíz 1996–2025, soja 1997–2025. Trigo y avena tienen archivos con la misma estructura.
- Pronóstico: `cost-of-production-forecasts-for-major-us-field-crops-2026f-2027f.csv` (`Commodity, Category, Item, Units, Region, Year, Value`; `Year` = `2026F`, `2027F`). Trae maíz, soja, trigo, avena y otros, pero en las filas revisadas la región es solo `U.S. total`.
- Las estimaciones salen de la encuesta ARMS y de los precios de NASS. Son cuentas "históricas" de costos reales, no presupuestos.

**3. Presupuestos por cultivo.**

- **farmdoc (Illinois)**: "2025 Budgets for All Regions" (`https://farmdoc.illinois.edu/handbook/2025-budgets-for-all-regions`), PDF `https://farmdoc.illinois.edu/assets/management/crop-budgets/crop_budgets_2025_v3.pdf` (Schnitkey y Paulson; publicado en septiembre de 2024 y revisado en mayo de 2025). Columnas: corn-after-soybeans, corn-after-corn, soybeans-after-corn, soybeans-after-soybeans, wheat y double-crop soybeans. Filas: rendimiento, precio, ingreso, pagos ARC/PLC, costos directos (fertilizantes, pesticidas, semilla, secado, almacenamiento, seguro), costos de maquinaria (power), gastos generales (overhead), costos totales sin tierra, `operator and land return`, costo de la tierra, `farmer return` y precios de equilibrio. Rendimientos del PDF de 2025 (bu/acre; maíz tras soja / maíz tras maíz / soja tras maíz / soja tras soja / trigo / soja de segunda): Tabla 1, norte de Illinois: 236 / 226 / 75 / 73 / 88 / 48. Tabla 2, centro, alta productividad: 225 / 215 / 68 / 66 / 86 / 48. Tabla 3, centro, baja productividad: 197 / 187 / 61 / 59 / 83 / 48. Precios supuestos: maíz $4.20/bu, soja $10.25/bu, trigo $5.30/bu. Es la única de las tres fuentes que separa explícitamente el efecto de la rotación sobre rendimiento y costos (por ejemplo, el maíz tras maíz rinde 10 bu menos en estas tablas). El enlace `https://farmdoc.illinois.edu/handbook/crop-budgets` da 404; los presupuestos están en la sección "Illinois Crop Budgets and Historic Returns" del Illinois Farm Management Handbook. No se revisó si ya está publicado el presupuesto de 2026.
- **Iowa State Ag Decision Maker**: "Estimated Costs of Crop Production in Iowa" (A1-20), `https://www.extension.iastate.edu/agdm/crops/html/a1-20.html`. El 2026-11-14, con un cliente automático, tanto el HTML como el PDF (`.../crops/pdf/a1-20.pdf`) devolvieron 403 con una página antirobots (Anubis). No se verificó su contenido, así que no se cita ningún valor. Hay que bajarlo a mano desde un navegador.

**Recomendación para el pipeline.** Si el equipo quiere márgenes, la forma más simple y reproducible es un paquete `economia` con `precios_estado_anual.csv` (`fips_estado, anio, cultivo, precio_usd_bu` o `precio_usd_ton`, `flag_nass`) del mismo volcado de Quick Stats, y `costos_ers_anual.csv` (región Heartland, por cultivo y año). El paquete no existe en el CLAUDE.md §6: queda como propuesta para el humano.

Fuentes:
- [Agriculture Prices Program — USDA NASS](https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Prices/index.php), consultado 2026-11-14
- [Commodity Costs and Returns — USDA ERS](https://www.ers.usda.gov/data-products/commodity-costs-and-returns), consultado 2026-11-14
- [Commodity Costs and Returns: Documentation — USDA ERS](https://www.ers.usda.gov/data-products/commodity-costs-and-returns/documentation), consultado 2026-11-14
- [2025 Budgets for All Regions — farmdoc, University of Illinois](https://farmdoc.illinois.edu/handbook/2025-budgets-for-all-regions), consultado 2026-11-14
- [Crop Budgets 2025 v3 (PDF) — farmdoc](https://farmdoc.illinois.edu/assets/management/crop-budgets/crop_budgets_2025_v3.pdf), consultado 2026-11-14
- [NASS Quick Stats API](https://quickstats.nass.usda.gov/api), consultado 2026-11-14
- [Estimated Costs of Crop Production in Iowa (A1-20) — Iowa State Ag Decision Maker](https://www.extension.iastate.edu/agdm/crops/html/a1-20.html), consultado 2026-11-14 (403 para clientes automáticos; no verificado)

Confianza: alta para los `short_desc` y la cobertura de los precios de NASS (salen del volcado oficial), la estructura y los valores de los CSV del ERS y los presupuestos de farmdoc 2025. Media para que IA, IL e IN caen en la región Heartland del ERS (no citado). Baja o nula para Ag Decision Maker (no se pudo leer).

Impacto: no cambia `config/`. Sirve para un paquete nuevo de economía (precios por estado y costos por región), que hoy no está en el CLAUDE.md §6: propuesta en `loop/notes/decisiones.md`. Para `cultivos`, los precios por estado se pueden sacar del mismo volcado `qs.crops_*.txt.gz` que ya está en `data/raw/cultivos/nass/`, sin bajar nada nuevo. Los presupuestos de farmdoc por rotación sirven de referencia para validar el efecto de la rotación (maíz tras soja contra maíz tras maíz) que aprenda el modelo.

Citas:
> "Cost and return estimates are reported for the United States and major production regions for corn, soybeans, wheat, cotton, grain sorghum, rice, peanuts, oats, barley, milk, hogs, and cow-calf." — [Commodity Costs and Returns — USDA ERS](https://www.ers.usda.gov/data-products/commodity-costs-and-returns)
> "Agricultural Prices - contains prices received by producers for principal crops, livestock and livestock products" — [Agriculture Prices Program — USDA NASS](https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Prices/index.php)
> "This publication presents crop budgets for three regions in Illinois: northern, central, and southern Illinois." — [Crop Budgets 2025 v3 (PDF) — farmdoc](https://farmdoc.illinois.edu/assets/management/crop-budgets/crop_budgets_2025_v3.pdf)
