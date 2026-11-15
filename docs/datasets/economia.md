# Data card — economia

Precios recibidos por el productor (USDA NASS) y costos y retornos por acre sembrado (USDA ERS)
por estado, año de cosecha y cultivo, para comparar rotaciones en el Corn Belt (los estados de
`config/config.yaml`). Paquete sumado por el humano (recursos del desafío); research de base en
`docs/research/precios_margenes.md` y, para las regiones de ERS, `docs/research/regiones_ers.md`.

## Archivos

- `data/processed/economia/economia_anual.csv`: `fips_estado, anio, cultivo, precio_usd_bu,
  valor_produccion_usd_ac, costo_operativo_usd_ac, costo_total_usd_ac, margen_operativo_usd_ac,
  flag_nass`. Cultivos: maiz, soja, trigo_invierno, avena. 2000–2025.
- `data/processed/economia/economia_forrajes_anual.csv`: `fips_estado, anio, cultivo,
  precio_usd_ton, flag_nass`. Cultivos: alfalfa, heno. 2000–2025.

Los datos solo existen por estado (NASS) o por región (ERS): la clave es `fips_estado`
(2 dígitos), como en Crop Progress.

## Fuentes

- **NASS Quick Stats**, volcado público `data/raw/cultivos/nass/qs.crops_20261113.txt.gz` (bajado
  por el paquete `cultivos`, registrado en `manifest.csv` con paquete `cultivos`; se lee desde
  ahí, sin copiarlo). Filtros: `SOURCE_DESC=SURVEY`, `STATISTICCAT_DESC=PRICE RECEIVED`,
  `AGG_LEVEL_DESC=STATE`, `FREQ_DESC=ANNUAL`, `REFERENCE_PERIOD_DESC=MARKETING YEAR`,
  `DOMAIN_DESC=TOTAL`. `short_desc`: maiz `CORN, GRAIN - PRICE RECEIVED, MEASURED IN $ / BU`;
  soja `SOYBEANS - PRICE RECEIVED, MEASURED IN $ / BU`; trigo_invierno `WHEAT, WINTER - PRICE
  RECEIVED, MEASURED IN $ / BU`; avena `OATS - PRICE RECEIVED, MEASURED IN $ / BU`; alfalfa
  `HAY, ALFALFA - PRICE RECEIVED, MEASURED IN $ / TON`; heno `HAY, (EXCL ALFALFA) - PRICE
  RECEIVED, MEASURED IN $ / TON`.
- **USDA ERS Commodity Costs and Returns**
  (https://www.ers.usda.gov/data-products/commodity-costs-and-returns), CSV por cultivo en
  `data/raw/economia/ers/` (corn, soybeans, wheat, oats). Farm Resource Regions `Heartland`,
  `Northern Crescent`, `Northern Great Plains`, `Prairie Gateway` y `Eastern Uplands` (las que
  tocan los estados de la zona), unidad `dollars per planted acre`. Ítems: `Total, gross value of production` →
  `valor_produccion_usd_ac`; `Total, operating costs` → `costo_operativo_usd_ac`;
  `Total, costs listed` → `costo_total_usd_ac`; `Value of production less operating costs` →
  `margen_operativo_usd_ac` (tal como lo publica ERS para cada región; el promedio ponderado de
  los márgenes regionales es igual a la diferencia de los promedios ponderados).
- **USDA ERS Farm Resource Regions**, `data/raw/economia/ers/reglink.xls`
  (https://www.ers.usda.gov/sites/default/files/images/reglink.xls, enlazada desde
  https://www.ers.usda.gov/data-products/commodity-costs-and-returns/documentation): región de
  cada condado por FIPS (códigos 1 a 9, con la clave en la misma planilla).
- **NASS Quick Stats**, mismo volcado, área sembrada por condado para los pesos: `SOURCE_DESC=SURVEY`,
  `AGG_LEVEL_DESC=COUNTY`, `FREQ_DESC=ANNUAL`, `REFERENCE_PERIOD_DESC=YEAR`, `DOMAIN_DESC=TOTAL`;
  `short_desc` `CORN - ACRES PLANTED`, `SOYBEANS - ACRES PLANTED`, `WHEAT, WINTER - ACRES
  PLANTED`, `OATS - ACRES PLANTED`.

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| economia_anual.csv | precio_usd_bu | Precio recibido por el productor, promedio del año comercial (NASS PRICE RECEIVED, MARKETING YEAR, estado) | USD/bu | USDA NASS Quick Stats (volcado qs.crops) | MK01 | 2000 | 2025 | 0.0 |
| economia_anual.csv | valor_produccion_usd_ac | Valor bruto de la producción por acre sembrado (ERS 'Total, gross value of production', regiones ponderadas por área sembrada) | USD/ac | USDA ERS Commodity Costs and Returns |  | 2000 | 2025 | 7.7 |
| economia_anual.csv | costo_operativo_usd_ac | Costos operativos por acre sembrado (ERS 'Total, operating costs', regiones ponderadas por área sembrada) | USD/ac | USDA ERS Commodity Costs and Returns | MK03 | 2000 | 2025 | 7.7 |
| economia_anual.csv | costo_total_usd_ac | Costos totales listados por acre sembrado (ERS 'Total, costs listed', regiones ponderadas por área sembrada) | USD/ac | USDA ERS Commodity Costs and Returns | MK03 | 2000 | 2025 | 7.7 |
| economia_anual.csv | margen_operativo_usd_ac | Valor de la producción menos costos operativos (ERS 'Value of production less operating costs', regiones ponderadas por área sembrada) | USD/ac | USDA ERS Commodity Costs and Returns | MK02 | 2000 | 2025 | 7.7 |
| economia_anual.csv | flag_nass | Código original de NASS cuando el precio no se publica ((D), (S), (NA)); vacío si hay valor | texto | USDA NASS Quick Stats (volcado qs.crops) |  |  |  | 100.0 |
| economia_forrajes_anual.csv | precio_usd_ton | Precio recibido por el productor, promedio del año comercial (NASS PRICE RECEIVED, MARKETING YEAR, estado) | USD/ton corta | USDA NASS Quick Stats (volcado qs.crops) | MK01 | 2000 | 2025 | 0.0 |
| economia_forrajes_anual.csv | flag_nass | Código original de NASS cuando el precio no se publica ((D), (S), (NA)); vacío si hay valor | texto | USDA NASS Quick Stats (volcado qs.crops) |  |  |  | 100.0 |

`desde`, `hasta` y `faltantes_pct` se calculan de los CSV al final de `process.py`.

## Pesos de las regiones ERS por estado

Participación de cada región en el área sembrada del cultivo en el estado (suma de ACRES PLANTED
por condado en el período). Se guardan también en `data/interim/economia/pesos_region_ers.csv`.

| fips_estado | cultivo | region_ers | acres | base | peso |
|---|---|---|---|---|---|
| 20 | avena | Prairie Gateway | 118,800 | acres_sembrados | 1.000 |
| 20 | maiz | Prairie Gateway | 92,894,900 | acres_sembrados | 1.000 |
| 20 | soja | Prairie Gateway | 86,408,000 | acres_sembrados | 1.000 |
| 20 | trigo_invierno | Prairie Gateway | 198,429,100 | acres_sembrados | 1.000 |

## Supuestos

- **Precio del año comercial.** Se usa la fila `MARKETING YEAR` del `anio` de cosecha (para maíz
  y soja, el año comercial empieza el 1 de septiembre del año de cosecha). Los precios mensuales
  no se entregan; cuál precio usar en el modelo lo decide el equipo de ML.
- **Unidad original.** Granos en USD por bushel y forrajes en USD por tonelada corta (2000 lb),
  como los publica NASS. No se convierte a USD/t métrica.
- **Costos ponderados por región.** ERS no publica costos por estado ni por condado, sino por
  Farm Resource Region, que se definen por condado (`reglink.xls`). Cada estado recibe el
  promedio de los valores regionales ponderado por la participación de cada región en el área
  sembrada del cultivo en el estado, sumando `ACRES PLANTED` de NASS por condado en todo el
  período (pesos fijos, no cambian por año, para que un condado suprimido un año no mueva el
  costo). IA, IL e IN son 100 % Heartland y KS 100 % Prairie Gateway; OH, NE y MN se reparten
  entre varias regiones (tabla de pesos arriba).
- **Regiones sin dato.** Si una región del estado no tiene serie ERS ese año (Eastern Uplands no
  tiene trigo y su avena empieza en 2023; la avena de Prairie Gateway termina en 2022), se
  repondera entre las regiones con dato, siempre que cubran al menos el 50 % del peso del
  estado; si no, los costos del año quedan vacíos.
- **Sin área por condado.** Si NASS no publica `ACRES PLANTED` por condado de un cultivo en un
  estado (avena en IN), el peso de cada región es su proporción de condados (`base = condados`
  en la tabla de pesos; la columna `acres` trae entonces la cantidad de condados).
- **Códigos de condado viejos en `reglink.xls`.** La planilla de ERS trae a Oglala Lakota (SD)
  con el código de Shannon County (46113); el Census lo cambió a 46102 en 2015 (Census Bureau,
  "Substantial Changes to Counties and County Equivalent Entities: 2010-present"). Al leerla se
  pasa 46113 → 46102. Es el único cambio de código desde 2000 en los estados de la zona.
- **Condados combinados.** Las filas de NASS de `OTHER (COMBINED) COUNTIES` no tienen condado
  y no entran en los pesos. Los códigos `(D)` y similares cuentan como sin dato.
- **Trigo.** ERS publica costos de trigo en general (no separa el de invierno). Se asignan a
  `trigo_invierno`, que es el trigo que se siembra en el Corn Belt. El precio sí es el de
  `WHEAT, WINTER`.
- **Avena.** La serie de ERS de avena empieza en 2005 en todas las regiones: 2000–2004 quedan vacíos.
- **Costos de forrajes.** ERS no tiene costos y retornos de alfalfa ni de heno: el archivo de
  forrajes solo trae el precio.
- **Ventana.** 2000–2025, de `config/config.yaml`. Los pronósticos ERS 2026F–2027F (solo total
  EE.UU.) no se usan.
- **Códigos NASS.** `(D)`, `(S)`, `(NA)` y los demás códigos entre paréntesis van como celda
  vacía, con el código en `flag_nass`. Un año sin fila en el volcado queda con precio y
  `flag_nass` vacíos.
- **Manifest.** El volcado de Quick Stats está registrado en `manifest.csv` por el paquete
  `cultivos`. No se le agrega una fila con paquete `economia` porque el control del manifest
  exige que las filas de cada paquete apunten a `data/raw/<paquete>/`.

## Problemas conocidos

- NASS dejó de publicar el precio del trigo de invierno en Iowa después de 2019 y el de la avena
  en Indiana después de 2015: esas celdas quedan vacías (con `(NA)` en `flag_nass` cuando NASS
  publica el código).
- Los costos de ERS son estimaciones regionales de la encuesta ARMS (años base de encuesta
  distintos por cultivo); la ponderación por área solo refleja en qué regiones se siembra cada
  cultivo, no diferencias dentro de una región ni entre rotaciones. En NE no separa riego y
  secano (ver T004). Los
  presupuestos de farmdoc por rotación (ver research) no se incorporaron.
- USDA AMS Market News (opcional) no se incorporó.
