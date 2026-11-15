# NASS por condado y Crop Progress en Kentucky

Pregunta: Para Kentucky (FIPS 21), ¿qué cultivos y años tiene NASS por condado (rendimiento, superficie, producción de maíz, soja, trigo de invierno y heno; superficie de tabaco), si están 2024 y 2025, cómo vienen los condados combinados y qué publica Crop Progress? ¿Cuántos condados tiene, cuánta superficie de maíz y soja suma, y cuántos de sus 120 condados casi no tienen agricultura (este de KY)?

Respuesta corta: KY tiene **120 condados** (Census 2020). Hay rendimiento, superficie y producción de condado de **maíz grano y soja de 2000 a 2025, 2024 incluido**, y de **trigo de invierno de 2000 a 2025 salvo 2024** (igual que en los demás estados). El **heno (alfalfa y otros) y el tabaco solo tienen condado hasta 2018**; desde 2019 son solo dato de estado. Cobertura de maíz grano en 2025: **60 de 120 condados (50 %)**, que suman el 81–82 % de la superficie del estado; soja 2025: 58 condados, 82 % de la superficie. Superficie sembrada del estado (2020–2025): **maíz 1,37–1,6 M acres y soja 1,8–2,05 M**, más 0,49–0,61 M de trigo de invierno, ~2 M de heno no alfalfa y 29–46 mil de tabaco. Desde 2020 hay **una sola fila "OTHER COUNTIES"** por cultivo y año (distrito `99`); antes, una por distrito agrícola. En maíz, soja y trigo **no aparece ningún `(D)`**; en heno sí, solo en 2013 (142 filas). **32 de los 120 condados** sembraban menos de 1.000 acres de maíz + soja en 2000–2006 (26 de ellos en el distrito EASTERN OR MOUNTAIN), y **15 no tienen ni un año de rendimiento de maíz o soja en 2020–2025**. En Crop Progress nacional **KY solo está en maíz y soja** (todas las etapas, 1998–2026) y en las tablas de condición, humedad y días aptos; **no está en trigo de invierno** ni hay tablas de tabaco o heno. Mediana 2000–2018 del 50 % sembrado: maíz día 117, soja 151; cosechado: 269 y 295. El hueco de octubre–noviembre de 2025 también afecta a KY.

Detalle:

## Método

Es el mismo método que `nass_mi_nd.md` (T067), con copias de sus scripts.

- **NASS por condado.** No se bajó la base completa ni se usó `NASS_API_KEY`. `docs/research/nass_ky_conteo.py` pide a la interfaz web pública de Quick Stats un CSV por cultivo y variable. Los cultivos son `CORN, SOYBEANS, WHEAT, OATS, BARLEY, HAY, HAYLAGE, SORGHUM, TOBACCO, RYE, CANOLA, SUNFLOWER`. Las variables son `YIELD, AREA PLANTED, AREA HARVESTED, PRODUCTION`. Filtros: `source_desc=SURVEY`, `agg_level_desc=COUNTY` (y `STATE` para la superficie sembrada y cosechada), `freq_desc=ANNUAL`, `reference_period_desc=YEAR`. Cuenta las filas **2000–2026** (en T067 eran 2018–2026) con `Domain=TOTAL` y sin "IRRIGATED" en el `Data Item`. Bajó 72 CSV (~40 MB) a `/tmp/t077/qs`, fuera del repo. Una fila con `County = OTHER COUNTIES` cuenta como combinada. Respecto de T067 se agregó la superficie **cosechada** del estado, porque el tabaco y el heno no tienen sembrada.
  ```
  .venv/bin/python -X utf8 docs/research/nass_ky_conteo.py /tmp/t077/qs > conteo_ky.csv
  ```
- **Condados sin agricultura.** `docs/research/nass_ky_condados.py` lee los mismos CSV y la lista de condados del Census 2020 (`st21_ky_cou2020.txt`). Para cada condado promedia la superficie sembrada de maíz + soja en 2000–2006 (años en que los condados publicados suman el 99–100 % del estado, así que un condado sin fila tiene muy poca superficie) y en 2020–2025, y cuenta en cuántos años 2020–2025 tiene rendimiento.
  ```
  .venv/bin/python -X utf8 docs/research/nass_ky_condados.py /tmp/t077/qs /tmp/t077/st21_ky_cou2020.txt
  ```
- **Crop Progress.** `docs/research/nass_ky_bajar_cp.py` baja los reportes de texto del archivo ESMIS a `/tmp/t077/txt` y `docs/research/nass_ky_crop_progress.py` toma la fila de Kentucky de cada tabla "<Cultivo> <Etapa> - Selected States". A la lista de cultivos de T067 se le agregó tabaco, heno y maní.

## Condados con rendimiento publicado (Quick Stats, encuesta)

"0" = ninguna fila de condado con dato ese año. Entre paréntesis, filas "OTHER COUNTIES". El heno y el tabaco no tienen rendimiento de condado después de 2018; para ellos se cuenta la superficie cosechada. No hay filas de condado de 2026.

| Año | Maíz grano | Soja | Trigo de invierno | Alfalfa (sup. cosechada) | Otro heno (sup. cosechada) | Tabaco burley (sup. cosechada) |
|---|---|---|---|---|---|---|
| 2000 | 97 (2) | 78 (4) | 65 (4) | 87 | 115 | 111 |
| 2005 | 89 (3) | 80 (4) | 47 (4) | 86 | 115 | 104 |
| 2008 | 85 (4) | 74 (4) | 63 (6) | 71 | 71 | 83 |
| 2010 | 86 (4) | 75 (4) | 48 (6) | 57 | 106 | 78 |
| 2012 | 89 (4) | 76 (5) | 46 (6) | 39 | 104 | 62 |
| 2013 | 75 (5) | 58 (6) | 50 (6) | 7 + 109 `(D)` | 87 + 33 `(D)` | 65 |
| 2015 | 75 (6) | 74 (6) | 39 (6) | 17 | 98 | 48 |
| 2017 | 74 (6) | 67 (6) | 35 (6) | 13 | 99 | 40 |
| 2018 | 70 (5) | 58 (6) | 28 (6) | 9 | 100 | 36 |
| 2019 | 58 (6) | 63 (6) | 31 (6) | 0 | 0 | 0 |
| 2020 | 83 (1) | 82 (1) | 39 (1) | 0 | 0 | 0 |
| 2021 | 84 (1) | 75 (1) | 33 (1) | 0 | 0 | 0 |
| 2022 | 79 (1) | 68 (1) | 39 (1) | 0 | 0 | 0 |
| 2023 | 73 (1) | 62 (1) | 36 (1) | 0 | 0 | 0 |
| 2024 | 59 (1) | 54 (1) | 0 (0) | 0 | 0 | 0 |
| 2025 | 60 (1) | 58 (1) | 23 (1) | 0 | 0 | 0 |

- Los años que faltan en la tabla (2001–2004, 2006–2007, 2009, 2011, 2014, 2016) están en `conteo_ky.csv`; siguen la misma tendencia. 2007 es un año flojo: soja 57, trigo 33, heno 62.
- La superficie sembrada, la cosechada y la producción del maíz grano y de la soja tienen **exactamente los mismos condados** que el rendimiento todos los años. En el trigo de invierno, la sembrada tiene un condado más en 2022 (40 contra 39).
- **Producción y rendimiento de heno** de condado: solo hasta 2018. El "HAY" total (sin separar) solo hasta 2008.
- **Tabaco**: la superficie, la producción y el rendimiento de condado van hasta 2018. Hasta 2004 se publica por tipo (31 burley, 22 y 23 fire-cured, 35 y 36 dark air-cured); de 2005 a 2018, burley (tipo 31), fire-cured (clase 2) y dark air-cured (clase 3B). Los dos tipos oscuros tienen muy pocos condados (2–19). Desde 2019, solo el estado (tabaco total y por clase, hasta 2026).
- **Maíz para silo**: solo filas combinadas, ningún condado.
- **Sorgo y cebada**: condado solo hasta 2008 (3–13 condados). **Avena y centeno**: solo estado, sin años 2000–2026 en la encuesta. **Canola y girasol**: nada.
- Las series de condado empiezan en 1929 (maíz) y 1972 (soja, trigo, heno, tabaco), según el primer año de los CSV.

**Valores entre paréntesis.** En maíz, soja y trigo de invierno, 2000–2025, no aparece ninguno: el condado oculto no tiene fila. En heno hay `(D)` solo en 2013: 109 filas de alfalfa y 33 de otro heno (superficie cosechada; también en producción).

**Condados combinados.** Hasta 2019 hay una fila "OTHER COUNTIES" por distrito agrícola (hasta 6: BLUEGRASS 50, CENTRAL 40, EASTERN OR MOUNTAIN 60, MIDWESTERN 20, NORTHERN 30, PURCHASE 10, con `Ag District Code` entre paréntesis). Desde 2020 hay **una sola**, con `Ag District Code = 99`, sin nombre de distrito y con `County ANSI` vacío. El CSV de la interfaz web no trae la columna `county_code`, así que no pude ver si es `998` como en la API; se identifica por el nombre "OTHER COUNTIES" y el `County ANSI` vacío. Desde Quick Stats no se puede saber qué condados suma.

**Superficie del estado en condados publicados** (% de la fila de estado; — = sin filas de condado):

| Cultivo | 2000–06 | 2012 | 2015 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Maíz (sembrada, todos los usos) | 99–100 | 98 | 83 | 90 | 70 | 96 | 84 | 90 | 86 | 82 | 81 |
| Soja (sembrada) | 100 | 96 | 91 | 78 | 79 | 98 | 88 | 89 | 79 | 84 | 82 |
| Trigo de invierno (sembrada) | 82–90 | 84 | 84 | 80 | 84 | 85 | 81 | 87 | 82 | — | 59 |
| Alfalfa (cosechada) | 97–98 | 56 | 22 | 11 | — | — | — | — | — | — | — |
| Otro heno (cosechada) | 100 | 96 | 93 | 89 | — | — | — | — | — | — | — |
| Tabaco burley (cosechada) | 100 | 80 | 69 | 59 | — | — | — | — | — | — | — |

**Superficie total del estado** (miles de acres, fila de estado de Quick Stats, encuesta):

| Cultivo | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| Maíz sembrado (todos los usos) | 1.330 | 1.550 | 1.470 | 1.530 | 1.420 | 1.600 | 1.370 | 1.520 | 1.530 |
| Maíz grano cosechado | 1.220 | 1.450 | 1.360 | 1.420 | 1.330 | 1.500 | 1.280 | 1.420 | 1.425 |
| Soja sembrada | 1.950 | 1.700 | 1.850 | 1.850 | 1.950 | 1.830 | 2.050 | 1.800 | 1.850 |
| Trigo de invierno sembrado | 450 | 460 | 510 | 510 | 530 | 610 | 560 | 490 | 420 |
| Alfalfa cosechada | 145 | 145 | 145 | 100 | 110 | 90 | 100 | 95 | 100 |
| Otro heno cosechado | 1.750 | 1.750 | 2.000 | 1.970 | 1.800 | 1.980 | 2.000 | 2.200 | 2.150 |
| Tabaco cosechado (todos) | 63,2 | 53,3 | 46,1 | 46,0 | 43,0 | 36,6 | 32,3 | 29,4 | 32,8 |

Maíz + soja suman **3,2–3,4 M acres sembrados por año** en 2020–2025. Quick Stats trae además el **% de la soja sembrada como doble cultivo** (después de trigo) del estado, 2013–2026: entre 17 y 41 % (41 en 2013, 21–29 en 2018–2023, 18 en 2024, 22 en 2025). Es mucho más que en el Corn Belt y conviene tenerlo en cuenta en `rotacion_anual.csv` (clase 26 del CDL).

## Condados con poca agricultura

Superficie sembrada media de maíz + soja por condado (acres por año) y por distrito agrícola de NASS:

| Distrito | Condados | Con < 1.000 ac en 2000–06 | Maíz + soja 2000–06 (ac/año, suma) | Maíz + soja 2020–25 en condados publicados (ac/año, suma) |
|---|---|---|---|---|
| MIDWESTERN (oeste) | 15 | 0 | 1.247.000 | 1.336.000 |
| PURCHASE (extremo oeste) | 11 | 0 | 627.000 | 623.000 |
| CENTRAL | 24 | 0 | 392.000 | 670.000 |
| BLUEGRASS | 23 | 2 | 126.000 | 203.000 |
| NORTHERN | 12 | 4 | 34.000 | 32.000 |
| EASTERN OR MOUNTAIN | 35 | 26 | 42.000 | 62.000 |
| **Total** | **120** | **32** | | |

- Los distritos MIDWESTERN y PURCHASE (26 condados) concentran ~2/3 de la superficie de maíz y soja.
- **32 condados** promedian menos de 1.000 acres de maíz + soja en 2000–2006. **20 de ellos no tienen ni una fila de condado en 2000–2006** (0 acres publicados), todos en EASTERN OR MOUNTAIN salvo Robertson (BLUEGRASS): Bell, Boyd, Breathitt, Elliott, Floyd, Harlan, Jackson, Johnson, Knott, Lawrence, Lee, Leslie, Letcher, McCreary, Magoffin, Martin, Owsley, Perry, Pike, Robertson.
- **15 condados no tienen rendimiento de maíz ni de soja en ningún año 2020–2025**: Bell, Boyd, Floyd, Harlan, Knott, Lawrence, Lee, Leslie, Letcher, McCreary, Martin, Perry, Pike, Robertson y Wolfe. Otros 9 de la lista de menos de 1.000 acres tienen solo 1 o 2 años (Anderson, Breathitt, Campbell, Elliott, Johnson, Magoffin, Menifee, Owsley y Whitley).
- Los 26 condados de montaña con poca superficie suman juntos menos de 3.000 acres de maíz + soja por año (2.800 en 2000–2006 y 1.600 en 2020–2025, en lo publicado). En una tabla por condado tendrían rendimiento vacío casi siempre, y una máscara agrícola del CDL con muy pocos píxeles. **No miré el CDL ni el Censo** para medir su superficie agrícola real (heno y pasturas incluidas): queda para quien arme la tanda.
- El umbral de 1.000 acres es mío, para el conteo. La lista completa sale de `nass_ky_condados.py`.

## Crop Progress (reportes semanales, nivel estado)

Se leyeron los 1.120 reportes de texto del archivo ESMIS (1995–2026), los mismos que en T067. Los que no traen la fecha "Released" no se leen (ver `nass_mi_nd.md`).

| Cultivo | Etapas | Años con valor |
|---|---|---|
| Maíz | PLANTED, EMERGED, SILKING, DOUGH, DENTED, MATURE, HARVESTED | 1998–2026, todos los años (EMERGED desde 1999) |
| Soja | PLANTED, EMERGED, BLOOMING, SETTING PODS, DROPPING LEAVES, HARVESTED | 1998–2026, todos los años (EMERGED desde 1999) |
| Trigo de invierno | — | **KY no está** en las tablas de trigo de invierno (sembrado, espigado, cosechado): son 18 estados, entre ellos IL, IN, OH, MI y NC, pero no KY. Tampoco en las de condición del trigo. |
| Tabaco, heno, sorgo | — | No hay tablas de tabaco ni de heno en los reportes leídos; KY no está en las de sorgo. |

KY sí aparece en las tablas de **condición** de maíz, soja y pasturas, de **humedad del suelo** (superficial y subsuelo) y de **días aptos para trabajo de campo** (verificado en un reporte de 2020). El parser no extrae las tablas de condición.

**Día del año típico del 50 %** (mediana 2000–2018, interpolación lineal entre semanas; 19 años salvo maíz emergido, 18):

| Cultivo | Sembrado | Emergido | Floración (silking / blooming) | Cosechado |
|---|---|---|---|---|
| Maíz | 117 | 133 | 186 | 269 |
| Soja | 151 | 162 | 204 | 295 |

El maíz de KY se siembra ~2 semanas antes que en Iowa y se cosecha ~1 mes antes; la soja se siembra tarde porque buena parte va después del trigo (doble cultivo).

**Hueco de 2025.** No hay reportes entre la semana al 28-09-2025 y la semana al 16-11-2025 (igual que en los otros estados). Cosecha: maíz 53 → 95 % y soja 28 → 81 %. El 50 % del maíz cae antes del hueco (entre el 21 y el 28-09); el de la soja cae dentro.

No miré los reportes estatales (*Kentucky Crop Progress & Condition*, NASS Eastern Mountain Region). Es posible que traigan trigo de invierno, tabaco y heno, pero no lo verifiqué.

## Particularidades de KY frente al Corn Belt

- **Heno y tabaco sin condado desde 2019.** El heno es el cultivo de mayor superficie del estado (~2,1 M acres con la alfalfa), pero en una rotación por condado solo sirve el CDL (clases 36 y 37) o el Censo. El tabaco, igual (clase 11 del CDL, no verificada en esta tarea contra `clases_cdl.csv`).
- **Doble cultivo trigo/soja** frecuente (17–41 % de la soja, dato de estado).
- **Trigo de invierno sin 2024 y con 59 % de la superficie en 2025**: el más flojo de los tres granos.
- **Riego:** no se contó. Los conteos usan solo los `Data Item` de todas las prácticas.

## Lo que no cubre

No se contaron las prácticas `IRRIGATED` / `NON-IRRIGATED`, el Censo ni el CDL. No se miraron los reportes estatales (*Kentucky Crop Progress & Condition*). No se miró la lista de *County Estimates* de NASS Kentucky. Los conteos son del 2026-11-15 y cambian si NASS revisa.

Fuentes:
- [USDA NASS Quick Stats, interfaz web](https://quickstats.nass.usda.gov/), consultas del 2026-11-15 con `nass_ky_conteo.py` (72 CSV).
- [Census Bureau, códigos de condado 2020 de Kentucky](https://www2.census.gov/geo/docs/reference/codes2020/cou/st21_ky_cou2020.txt), consultado 2026-11-15.
- [Crop Progress, publicación semanal (USDA NASS, archivo ESMIS)](https://esmis.nal.usda.gov/publication/crop-progress), consultado 2026-11-15: 1.120 reportes de texto 1995–2026.

Confianza: alta para los conteos de Quick Stats (salen de los CSV); media para la lista de condados con poca agricultura (depende del umbral y de usar maíz + soja como indicador).

Impacto: decisión de la cuarta tanda (`docs/research/cuarta_tanda.md`, `config/config.yaml` si el humano suma KY). Paquete `cultivos`: con KY, `produccion_anual.csv` tendría ~15–30 condados casi sin filas de maíz y soja, y el heno y el tabaco solo por CDL. `rotacion_anual.csv`: el doble cultivo pesa más que en el Corn Belt.
