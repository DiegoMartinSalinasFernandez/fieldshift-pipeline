# NASS por condado y Crop Progress en Missouri, Wisconsin y Dakota del Sur

Pregunta: Para MO (FIPS 29), WI (55) y SD (46), ¿qué cultivos y años tiene NASS por condado (rendimiento, superficie, producción), si están 2024 y 2025, y cómo vienen los distritos y los condados combinados? ¿Qué publica Crop Progress por estado (maíz, soja, trigo de invierno, avena y otros: etapas y años)? ¿Qué particularidades hay (doble cultivo en MO, silo y alfalfa en WI, trigo de primavera y girasol en SD)?

Respuesta corta: Hay datos de condado de **maíz grano, soja y trigo de invierno en los tres estados hasta 2025**; **2024 está para maíz y soja, pero no para trigo ni avena** (igual que en los 7 estados, `nass_2024_2025.md`). La avena de condado está en WI y SD (no en MO, ningún año desde 2018). WI tiene **maíz para silo** por condado 2018–2025 (50–63 de 72 condados), y SD tiene **trigo de primavera** por condado 2018–2025 salvo 2024. **Alfalfa, otros henos y girasol por condado solo llegan hasta 2018**: después no hay filas de condado. Como en los otros estados, no hay ningún `(D)`: desde 2020 hay **una sola fila "OTHER COUNTIES"** por estado, cultivo y año (en 2018–2019, una por distrito agrícola). Lo más flojo es MO y SD: en 2025 el rendimiento de maíz grano tiene dato en 44 de 115 condados de MO (38 %) y 37 de 66 de SD (56 %); WI, en cambio, tiene 60 de 72 (83 %). En Crop Progress los tres estados están en maíz y soja todas las etapas 2000–2026; trigo de invierno en MO y SD (no WI); avena en WI y SD (MO solo hasta 2020 y con huecos); trigo de primavera y girasol solo en SD; sorgo en SD todo el período y en MO hasta 2018. El hueco de octubre–noviembre de 2025 (cierre del gobierno) también los afecta.

Detalle:

## Método

- **NASS por condado.** No se bajó la base completa `qs.crops_*.txt.gz` (1,1 GB; la tarea pide no bajar datasets grandes) ni se usó `NASS_API_KEY`. El script `docs/research/nass_mo_wi_sd_conteo.py` pide a la interfaz web pública de Quick Stats (el mismo mecanismo del botón "Get Data": POST a `/row_counts` y `/uuid/encode`, GET a `/data/spreadsheet/<uuid>.csv`) un CSV por estado, cultivo (`CORN, SOYBEANS, WHEAT, OATS, HAY, HAYLAGE, SUNFLOWER, SORGHUM`) y variable (`YIELD, AREA PLANTED, AREA HARVESTED, PRODUCTION`), con `source_desc=SURVEY`, `agg_level_desc=COUNTY` (y `STATE` para la superficie sembrada), `freq_desc=ANNUAL`, `reference_period_desc=YEAR`. Cuenta filas 2018–2026 con `Domain=TOTAL`. Bajó 90 CSV (80 MB) a `/tmp/t063/qs`, fuera del repo; tarda unos 12 minutos. Una fila con `County = OTHER COUNTIES` (sin `County ANSI`) cuenta como combinada.
  ```
  .venv/bin/python -X utf8 docs/research/nass_mo_wi_sd_conteo.py /tmp/qs_mowisd > conteo_mowisd.csv
  ```
  Ojo: el CSV de la interfaz web no trae `prodn_practice_desc` como columna aparte. El `Data Item` sin "IRRIGATED" / "NON-IRRIGATED" es el de todas las prácticas; los conteos de abajo usan solo esos.
- **Crop Progress.** El script `docs/research/nass_mo_wi_sd_crop_progress.py` lee los 1.099 reportes semanales de texto (1995–2026) de ESMIS, bajados a `/tmp/t063/txt` (45 MB, fuera del repo). Toma de cada tabla "<Cultivo> <Etapa> - Selected States" (o "<Cultivo>: Percent <Etapa>" en el formato viejo) el valor de la semana actual para MO, WI y SD. Es el mismo método de `crop_progress_estados_nuevos.md`. No leyó 9 de los 1.099 reportes, porque no traen la fecha "Released" (por ejemplo, 30-10-1995, 28-10-2012 y 04-04-2016).
- **Total de condados** (Census TIGER; no se volvió a contar en esta tarea): MO 115 (114 condados más la ciudad independiente de St. Louis, 29510), WI 72, SD 66.

## Condados con rendimiento publicado (Quick Stats, encuesta)

Las cuatro variables (rendimiento, sembrada, cosechada y producción) no se cruzaron una por una como en `nass_2024_2025.md`. La tabla usa el rendimiento. "—" = ninguna fila de condado ese año.

**Missouri (115 condados)**

| Año | Maíz grano | Soja | Trigo de invierno | Avena | Sorgo | Alfalfa | Otro heno |
|---|---|---|---|---|---|---|---|
| 2018 | 50 | 55 | 45 | — | 5 | 14 | 77 |
| 2019 | 47 | 51 | 46 | — | — | — | — |
| 2020 | 89 | 90 | 50 | — | — | — | — |
| 2021 | 65 | 71 | 46 | — | — | — | — |
| 2022 | 67 | 75 | 46 | — | — | — | — |
| 2023 | 74 | 76 | 45 | — | — | — | — |
| 2024 | 53 | 57 | — | — | — | — | — |
| 2025 | 44 | 54 | 43 | — | — | — | — |

**Wisconsin (72 condados)**

| Año | Maíz grano | Maíz silo | Soja | Trigo de invierno | Avena | Alfalfa | Otro heno |
|---|---|---|---|---|---|---|---|
| 2018 | 51 | 31 | 43 | 32 | 40 | 20 | 4 |
| 2019 | 53 | 25 | 47 | 27 | 34 | — | — |
| 2020 | 64 | 62 | 64 | 40 | 53 | — | — |
| 2021 | 64 | 63 | 64 | 38 | 48 | — | — |
| 2022 | 64 | 63 | 63 | 33 | 41 | — | — |
| 2023 | 62 | 58 | 61 | 36 | 34 | — | — |
| 2024 | 59 | 58 | 57 | — | — | — | — |
| 2025 | 60 | 50 | 62 | 39 | 32 | — | — |

**Dakota del Sur (66 condados)**

| Año | Maíz grano | Soja | Trigo de invierno | Trigo de primavera (sin durum) | Avena | Sorgo | Girasol | Alfalfa | Otro heno |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | 44 | 40 | 20 | 18 | 28 | 3 | 7 aceitero, 1 confitero | 34 | 25 |
| 2019 | 24 | 20 | 14 | 14 | 16 | 2 | — | — | — |
| 2020 | 58 | 53 | 20 | 29 | 26 | 5 | — | — | — |
| 2021 | 48 | 37 | 26 | 23 | 20 | 10 | — | — | — |
| 2022 | 52 | 41 | 30 | 26 | 32 | 8 | — | — | — |
| 2023 | 39 | 31 | 16 | 13 | 11 | 5 | — | — | — |
| 2024 | 41 | 36 | — | — | — | 8 | — | — | — |
| 2025 | 37 | 29 | 11 | 12 | 15 | 2 | — | — | — |

No hay filas de 2026. En las filas de condado de los tres estados, 2018–2025, **no aparece ningún valor entre paréntesis** (`(D)`, `(Z)`, `(NA)`): el condado oculto no tiene fila.

**Condados combinados y distritos.** En 2018 y 2019 hay una fila "OTHER COUNTIES" por distrito agrícola: hasta 9 por cultivo (MO 9 en maíz; WI 7–9; SD 5–9). Desde 2020 hay **una sola** por estado, cultivo y año, con código de distrito 99. Los condados que no aparecen están sumados ahí, y desde Quick Stats no se puede saber cuáles son.

**Superficie sembrada del estado en condados publicados** (%; el resto está en la fila combinada; 0 = hay total de estado pero no hay filas de condado):

| Estado | Cultivo | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| MO | Maíz (todos los usos) | 95 | 58 | 72 | 81 | 64 | 58 |
| MO | Soja | 97 | 65 | 80 | 83 | 64 | 70 |
| MO | Trigo inv. | 79 | 76 | 66 | 76 | 0 | 64 |
| MO | Avena | 0 | 0 | 0 | 0 | — | — |
| WI | Maíz (todos los usos) | 100 | 100 | 100 | 98 | 95 | 98 |
| WI | Soja | 100 | 100 | 98 | 93 | 89 | 99 |
| WI | Trigo inv. | 83 | 85 | 77 | 83 | 0 | 85 |
| WI | Avena | 88 | 84 | 67 | 58 | 0 | 54 |
| SD | Maíz (todos los usos) | 98 | 78 | 93 | 69 | 69 | 71 |
| SD | Soja | 98 | 77 | 94 | 65 | 68 | 63 |
| SD | Trigo inv. | 74 | 70 | 73 | 41 | 0 | 47 |
| SD | Avena | 37 | 33 | 59 | 12 | 0 | 17 |

Esta tabla no es igual a la de `nass_2024_2025.md`: ahí los porcentajes son de condados con rendimiento de grano.

## Crop Progress (reportes semanales, nivel estado)

Años con al menos un valor (2000–2026; "sem." = mediana de reportes con valor por año):

| Estado | Cultivo | Etapas | Años |
|---|---|---|---|
| MO, WI, SD | Maíz | PLANTED, EMERGED, SILKING, DOUGH, DENTED, MATURE, HARVESTED | 2000–2026 completos (8–11 sem.) |
| MO, WI, SD | Soja | PLANTED, EMERGED, BLOOMING, SETTING PODS, DROPPING LEAVES, HARVESTED | 2000–2026 completos (8–9 sem.) |
| MO, SD | Trigo de invierno | PLANTED y EMERGED (otoño previo), HEADED, HARVESTED | 2000–2026 completos (10–11 sem.) |
| WI | Trigo de invierno | — (WI no está en las tablas ningún año) | — |
| WI, SD | Avena | PLANTED, EMERGED, HEADED, HARVESTED | 2000–2026 completos (8–9 sem.) |
| MO | Avena | PLANTED solo hasta 2009; EMERGED hasta 2020; HEADED y HARVESTED hasta 2026, con años faltantes (22–27 de 27) | parcial |
| SD | Trigo de primavera | PLANTED, EMERGED, HEADED, HARVESTED | 2000–2026 completos |
| SD | Girasol | PLANTED, HARVESTED | 2000–2026 sin 2005/2006–2009 |
| SD | Sorgo | PLANTED, HEADED, COLORING, MATURE, HARVESTED | 2000–2026 |
| MO | Sorgo | ídem | 2000–2018 (después MO sale de la tabla) |
| MO | Algodón y arroz | todas las etapas | 2000–2026 (arroz desde 2002) |

En los reportes nacionales **no hay** tablas de alfalfa, heno ni maíz para silo. No miré si los reportes estatales de NASS, como el *Wisconsin Crop Progress & Condition*, informan los cortes de alfalfa.

**Día del año típico del 50 %** (mediana 2000–2018, interpolación lineal entre semanas; trigo de invierno sembrado y emergido = otoño previo a la cosecha):

| Estado | Cultivo | Sembrado | Emergido | Floración / espigado | Cosechado |
|---|---|---|---|---|---|
| MO | maíz | 114 | 130 | 188 | 270 |
| MO | soja | 145 | 156 | 203 | 295 |
| MO | trigo inv. | 293 | 305 | 128 | 174 |
| MO | sorgo | 146 | — | 209 | 282 |
| WI | maíz | 133 | 147 | 209 | 303 |
| WI | soja | 144 | 155 | 202 | 289 |
| WI | avena | 120 | 132 | 176 | 221 |
| SD | maíz | 131 | 146 | 207 | 299 |
| SD | soja | 145 | 157 | 198 | 281 |
| SD | trigo inv. | 267 | 282 | 157 | 203 |
| SD | trigo prim. | 113 | 127 | 174 | 220 |
| SD | avena | 113 | 130 | 173 | 211 |
| SD | girasol | 158 | — | — | 296 |
| SD | sorgo | 154 | — | 213 | 290 |

En algunos años no se calculó el cruce (primer dato ya ≥ 50 % o serie cortada): maíz emergido MO 16/19, trigo espigado MO 18/19, trigo de primavera SD (emergido 18/19, espigado y cosechado 14/19), girasol SD (13–14 de 14–15).

**Hueco de 2025.** Igual que en los otros estados, entre el reporte del 29-09-2025 (semana al 28-09) y el del 17-11-2025 (semana al 16-11) no hay datos. Cosecha del 28-09 al 16-11: maíz MO 40 → 92 %, WI 4 → 86 %, SD 5 → 90 %; soja MO 11 → 89 %, WI 6 → 98 %, SD 12 → 100 %; girasol SD 0 → 75 %. Siembra del trigo de invierno: MO 5 → 82 %, SD 60 → 100 %. Todos los cruces del 50 % de la cosecha de 2025 caen dentro del hueco.

## Particularidades

- **MO, doble cultivo trigo/soja:** **No lo verifiqué.** No busqué en Quick Stats un `Data Item` de soja después de otro cultivo, y el CSV de la interfaz web no separa la práctica. Lo que sí se ve: el maíz de MO se siembra y se cosecha antes que en el resto (día 114 y 270), y la soja después (145 y 295), lo que es compatible con soja de segunda tras trigo (el trigo se cosecha el día 174). En la rotación sigue sirviendo la clase 26 del CDL (doble trigo/soja).
- **MO, bottomlands del río:** **No lo investigué.** NASS no las separa. Para detectarlas haría falta suelo y terreno (gSSURGO, inundabilidad) o el CDL. La cobertura de condado más baja (38–58 % de la superficie de maíz en condados publicados en 2021 y 2025) no se cruzó con la geografía.
- **WI, lechería:** el maíz para silo tiene rendimiento por condado (TONS / ACRE) en 50–63 condados en 2020–2025, más que el maíz grano en algunos años. La superficie sembrada de maíz "todos los usos" de condado cubre el 95–100 % del estado, porque incluye el silo. La alfalfa y el heno por condado se cortan en 2018, igual que en MO y SD. Para la alfalfa después de 2018 solo queda el dato de estado o el Censo (2022).
- **SD:** el trigo de primavera (sin durum) tiene condado 2018–2025 salvo 2024. El girasol (aceitero y confitero) solo tiene condado en 2018. El sorgo tiene 2–10 condados por año, también en 2024. Es el estado con más superficie oculta en la fila combinada en 2023–2025 (31–37 % de la soja, 29–31 % del maíz).

## Lo que no cubre

No se contaron prácticas `IRRIGATED` / `NON-IRRIGATED`, años anteriores a 2018, ni el Censo. Tampoco se verificó qué `YEAR` les pone Quick Stats a las etapas de otoño del trigo de invierno, ni si Quick Stats cargó después las semanas de octubre de 2025. Los conteos son del 2026-11-15 y cambian si NASS revisa.

Fuentes:
- [USDA NASS Quick Stats, interfaz web](https://quickstats.nass.usda.gov/), consultas del 2026-11-15 con `nass_mo_wi_sd_conteo.py` (90 CSV, por ejemplo maíz / YIELD / COUNTY / MISSOURI: 13.028 filas).
- [Crop Progress, publicación semanal (USDA NASS, archivo ESMIS)](https://esmis.nal.usda.gov/publication/crop-progress), consultado 2026-11-15: 1.099 reportes de texto 1995–2026, por ejemplo [prog2526.txt (22-06-2026)](https://esmis.nal.usda.gov/sites/default/release-files/795947/prog2526.txt) y [CropProg-05-05-2003.txt](https://esmis.nal.usda.gov/sites/default/release-files/8336h188j/2514nm797/7w62f9710/CropProg-05-05-2003.txt).
- [County Estimates de NASS Missouri](https://www.nass.usda.gov/Statistics_by_State/Missouri/Publications/County_Estimates/index.php), [Wisconsin](https://www.nass.usda.gov/Statistics_by_State/Wisconsin/Publications/County_Estimates/index.php) y [South Dakota](https://www.nass.usda.gov/Statistics_by_State/South_Dakota/Publications/County_Estimates/index.php), consultados 2026-11-15. Solo se miró la lista de PDF: WI publica maíz para silo por condado y SD trigo de primavera y sorgo, lo que coincide con Quick Stats.
- `docs/research/nass_2024_2025.md` y `docs/research/crop_progress_estados_nuevos.md`, de este repo.

Confianza:
- **Alta:** conteos de condado, filas combinadas y tablas de Crop Progress por estado (salen directo de NASS).
- **Media:** días típicos del 50 % (interpolación propia) y % de superficie en condados.
- **Sin verificar:** doble cultivo y bottomlands en MO, y los cortes de alfalfa en WI.

Impacto:
- Si se suman MO, WI y SD (decisión del humano), el paquete `cultivos` sirve tal cual para maíz, soja, trigo de invierno y avena: el faltante es una fila ausente, se descartan las "OTHER COUNTIES" y 2024 no tiene trigo ni avena.
- Cambios que habría que proponer al humano:
  - `produccion_anual.csv` no tiene maíz para silo ni trigo de primavera. Agregarlos (WI, SD) cambia el esquema.
  - La alfalfa y el heno no tienen condado después de 2018 en ningún estado.
  - En `fenologia_estado.csv`, maíz y soja salen sin cambios. Para SD convendría sumar trigo de primavera y girasol.
- Para ML: MO 2025 tiene rendimiento de maíz en el 38 % de los condados, y el faltante no es al azar.
