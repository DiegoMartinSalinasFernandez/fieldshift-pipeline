# Data card — economia

Precios recibidos por el productor (USDA NASS) y costos y retornos por acre sembrado (USDA ERS)
por estado, año de cosecha y cultivo, para comparar rotaciones en el Corn Belt (IA, IL, IN).
Paquete sumado por el humano (recursos del desafío); research de base en
`docs/research/precios_margenes.md`.

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
  `data/raw/economia/ers/` (corn, soybeans, wheat, oats). Región `Heartland`, unidad
  `dollars per planted acre`. Ítems: `Total, gross value of production` →
  `valor_produccion_usd_ac`; `Total, operating costs` → `costo_operativo_usd_ac`;
  `Total, costs listed` → `costo_total_usd_ac`; `Value of production less operating costs` →
  `margen_operativo_usd_ac` (tal como lo publica ERS, no recalculado).

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| economia_anual.csv | precio_usd_bu | Precio recibido por el productor, promedio del año comercial (NASS PRICE RECEIVED, MARKETING YEAR, estado) | USD/bu | USDA NASS Quick Stats (volcado qs.crops) | MK01 | 2000 | 2025 | 5.4 |
| economia_anual.csv | valor_produccion_usd_ac | Valor bruto de la producción por acre sembrado (ERS 'Total, gross value of production', Heartland) | USD/ac | USDA ERS Commodity Costs and Returns |  | 2000 | 2025 | 4.8 |
| economia_anual.csv | costo_operativo_usd_ac | Costos operativos por acre sembrado (ERS 'Total, operating costs', Heartland) | USD/ac | USDA ERS Commodity Costs and Returns | MK03 | 2000 | 2025 | 4.8 |
| economia_anual.csv | costo_total_usd_ac | Costos totales listados por acre sembrado (ERS 'Total, costs listed', Heartland) | USD/ac | USDA ERS Commodity Costs and Returns | MK03 | 2000 | 2025 | 4.8 |
| economia_anual.csv | margen_operativo_usd_ac | Valor de la producción menos costos operativos (ERS 'Value of production less operating costs', Heartland) | USD/ac | USDA ERS Commodity Costs and Returns | MK02 | 2000 | 2025 | 4.8 |
| economia_anual.csv | flag_nass | Código original de NASS cuando el precio no se publica ((D), (S), (NA)); vacío si hay valor | texto | USDA NASS Quick Stats (volcado qs.crops) |  | 2019 | 2019 | 99.7 |
| economia_forrajes_anual.csv | precio_usd_ton | Precio recibido por el productor, promedio del año comercial (NASS PRICE RECEIVED, MARKETING YEAR, estado) | USD/ton corta | USDA NASS Quick Stats (volcado qs.crops) | MK01 | 2000 | 2025 | 0.0 |
| economia_forrajes_anual.csv | flag_nass | Código original de NASS cuando el precio no se publica ((D), (S), (NA)); vacío si hay valor | texto | USDA NASS Quick Stats (volcado qs.crops) |  |  |  | 100.0 |

`desde`, `hasta` y `faltantes_pct` se calculan de los CSV al final de `process.py`.

## Supuestos

- **Precio del año comercial.** Se usa la fila `MARKETING YEAR` del `anio` de cosecha (para maíz
  y soja, el año comercial empieza el 1 de septiembre del año de cosecha). Los precios mensuales
  no se entregan; cuál precio usar en el modelo lo decide el equipo de ML.
- **Unidad original.** Granos en USD por bushel y forrajes en USD por tonelada corta (2000 lb),
  como los publica NASS. No se convierte a USD/t métrica.
- **Región Heartland para los tres estados.** ERS no publica costos por estado: IA, IL e IN
  reciben el mismo valor de la región Heartland (Farm Resource Regions del ERS, que se definen por
  condado). Algunos condados de los bordes de los tres estados pueden caer en otras regiones ERS;
  no se verificó condado por condado y se usa Heartland para todo el estado.
- **Trigo.** ERS publica costos de trigo en general (no separa el de invierno). Se asignan a
  `trigo_invierno`, que es el trigo que se siembra en el Corn Belt. El precio sí es el de
  `WHEAT, WINTER`.
- **Avena.** La serie de ERS de avena (región Heartland) empieza en 2005: 2000–2004 quedan vacíos.
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
  distintos por cultivo); no reflejan diferencias entre estados ni entre rotaciones. Los
  presupuestos de farmdoc por rotación (ver research) no se incorporaron.
- USDA AMS Market News (opcional) no se incorporó.
