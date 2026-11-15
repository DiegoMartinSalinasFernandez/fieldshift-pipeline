# NASS por condado y Crop Progress en Michigan y Dakota del Norte

Pregunta: Para MI (FIPS 26) y ND (38), ¿qué cultivos y años tiene NASS por condado (rendimiento, superficie, producción), si están 2024 y 2025, y cómo vienen los condados combinados? ¿Qué publica Crop Progress por estado? ¿Qué pasa con el frijol seco y la remolacha en MI, y con el trigo de primavera, el girasol, la canola y la cebada en ND? ¿Cuántos condados y cuánta superficie de maíz y soja suma cada uno?

Respuesta corta: MI tiene **83 condados** y ND **53**. Hay rendimiento de condado de **maíz grano y soja en los dos estados de 2018 a 2025, 2024 incluido**. Trigo de invierno (MI), avena, cebada, trigo de primavera y durum (ND) tienen condado 2018–2025 **salvo 2024**, igual que en los demás estados. En ND hay además canola, frijol seco, girasol aceitero, lino, arveja, maíz para silo, **alfalfa y otros henos por condado hasta 2025, 2024 incluido**: es lo contrario de MO, WI y SD, donde el heno de condado se corta en 2018. En MI, el **frijol seco y la remolacha solo tienen condado en 2018**; después solo hay dato de estado. Como en los otros estados, **no aparece ningún `(D)`**: desde 2020 hay una sola fila "OTHER COUNTIES" por estado, cultivo y año. La cobertura de maíz grano en 2025 es de 44 de 83 condados en MI (53 %) y 31 de 53 en ND (58 %). Superficie sembrada del estado (2021–2025, Quick Stats): **MI, unos 2,3 M acres de maíz y 2,0–2,25 M de soja; ND, 3,95–4,7 M de maíz y 5,7–7,25 M de soja** (ND 2020: 1,95 M de maíz). En Crop Progress, MI y ND están en maíz y soja, con todas las etapas, de 2000 a 2026. MI aparece además en trigo de invierno y remolacha. ND aparece en trigo de primavera, cebada, avena, remolacha y girasol. **No hay tablas de canola, frijol seco ni lino** en el reporte nacional. MI no aparece en avena y ND no aparece en trigo de invierno. El hueco de octubre–noviembre de 2025 también los afecta.

Detalle:

## Método

Es el mismo método que `nass_mo_wi_sd.md` (T063), con copias de sus scripts.

- **NASS por condado.** No se bajó la base completa ni se usó `NASS_API_KEY`. `docs/research/nass_mi_nd_conteo.py` pide a la interfaz web pública de Quick Stats un CSV por estado, cultivo y variable. Los cultivos son `CORN, SOYBEANS, WHEAT, OATS, BARLEY, HAY, HAYLAGE, SUNFLOWER, CANOLA, BEANS, SUGARBEETS, SORGHUM, FLAXSEED, PEAS, LENTILS, POTATOES`. Las variables son `YIELD, AREA PLANTED, AREA HARVESTED, PRODUCTION`. Los filtros son `source_desc=SURVEY`, `agg_level_desc=COUNTY` (y `STATE` para la superficie sembrada), `freq_desc=ANNUAL` y `reference_period_desc=YEAR`. Cuenta las filas 2018–2026 con `Domain=TOTAL` y sin "IRRIGATED" en el `Data Item`. Bajó 160 CSV (100 MB) a `/tmp/t067/qs`, fuera del repo. Una fila con `County = OTHER COUNTIES` cuenta como combinada.
  ```
  .venv/bin/python -X utf8 docs/research/nass_mi_nd_conteo.py /tmp/t067/qs > conteo_mind.csv
  ```
- **Crop Progress.** `docs/research/nass_mi_nd_bajar_cp.py` baja los 1.120 reportes de texto del archivo ESMIS (1995–2026, 45 MB) a `/tmp/t067/txt`. Después, `docs/research/nass_mi_nd_crop_progress.py` toma de cada tabla "<Cultivo> <Etapa> - Selected States" el valor de la semana actual de MI y ND. A la lista de cultivos de T063 le agrega durum, canola, frijol seco, remolacha, lino, arveja, lenteja y papa. Hay 7 reportes que no se leyeron porque no traen la fecha "Released"; son los mismos casos que en T063.
- **Total de condados**: según las listas de códigos del Census 2020 (`st26_mi_cou2020.txt`, `st38_nd_cou2020.txt`), MI tiene 83 y ND 53.

## Condados con rendimiento publicado (Quick Stats, encuesta)

"0" = ninguna fila de condado con dato ese año (puede haber una fila combinada). No hay filas de 2026.

**Michigan (83 condados)**

| Año | Maíz grano | Soja | Trigo de invierno | Avena | Frijol seco | Remolacha |
|---|---|---|---|---|---|---|
| 2018 | 48 | 41 | 39 | 9 | 5 | 12 |
| 2019 | 49 | 40 | 36 | 31 | 0 | 0 |
| 2020 | 60 | 49 | 47 | 36 | 0 | 0 |
| 2021 | 57 | 47 | 44 | 28 | 0 | 0 |
| 2022 | 59 | 50 | 43 | 26 | 0 | 0 |
| 2023 | 57 | 48 | 42 | 24 | 0 | 0 |
| 2024 | 50 | 45 | 0 | 0 | 0 | 0 |
| 2025 | 44 | 33 | 38 | 23 | 0 | 0 |

En MI no hay filas de condado de cebada, heno, alfalfa, canola, girasol, sorgo, lino, arveja ni lenteja en 2018–2025. El maíz para silo solo aparece como fila combinada en 2022, sin condados.

**Dakota del Norte (53 condados)**

| Año | Maíz grano | Maíz silo | Soja | Trigo prim. (sin durum) | Durum | Trigo inv. | Cebada | Avena | Canola | Girasol aceitero | Frijol seco | Lino | Arveja | Lenteja | Alfalfa | Otro heno |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 24 | 21 | 35 | 40 | 9 | 1 | 21 | 13 | 15 | 11 | 15 | 8 | 10 | 2 | 17 | 15 |
| 2019 | 21 | 11 | 34 | 30 | 5 | 1 | 18 | 6 | 13 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| 2020 | 45 | 35 | 48 | 50 | 18 | 0 | 27 | 26 | 27 | 33 | 25 | 17 | 15 | 2 | 51 | 46 |
| 2021 | 45 | 36 | 46 | 47 | 18 | 5 | 24 | 17 | 25 | 27 | 21 | 8 | 12 | 2 | 48 | 46 |
| 2022 | 44 | 27 | 45 | 48 | 12 | 11 | 25 | 14 | 31 | 25 | 18 | 14 | 8 | 3 | 45 | 49 |
| 2023 | 48 | 22 | 42 | 42 | 14 | 12 | 20 | 15 | 26 | 17 | 19 | 8 | 9 | 2 | 37 | 30 |
| 2024 | 42 | 12 | 40 | 0 | 0 | 0 | 0 | 0 | 25 | 10 | 11 | 3 | 6 | 3 | 44 | 33 |
| 2025 | 31 | 13 | 35 | 36 | 11 | 0 | 16 | 8 | 19 | 10 | 16 | 4 | 6 | 0 | 19 | 12 |

- El frijol seco de 2018 es "INCL CHICKPEAS" y desde 2020 es "(EXCL CHICKPEAS)". Son dos `Data Item` distintos.
- La remolacha de ND tiene 6 condados en 2018 y ninguno después. El girasol confitero (NON-OIL) solo aparece en una fila combinada de 2018.
- El sorgo de ND no tiene filas de condado.
- 2019 es un año flojo en ND: no hay girasol, frijol, lino ni heno de condado.
- **Ojo:** a diferencia de los granos chicos, en 2024 sí hay canola, girasol, frijol, lino, arveja, alfalfa y heno de condado. Lo que falta en 2024 son los trigos, la cebada y la avena, igual que en los demás estados.

En las filas de condado de los dos estados, 2018–2025, **no aparece ningún valor entre paréntesis** (`(D)`, `(Z)`, `(NA)`): el condado oculto directamente no tiene fila.

**Condados combinados.** En 2018 y 2019 hay varias filas "OTHER COUNTIES" por cultivo, una por distrito agrícola: en el maíz, MI tiene 3 y 7, y ND 9 y 9. Desde 2020 hay **una sola** por estado, cultivo y año. Desde Quick Stats no se puede saber qué condados suma.

**Superficie sembrada del estado en condados publicados** (% de la fila de estado; vacío = no hay filas de condado ese año):

| Estado | Cultivo | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| MI | Maíz (todos los usos) | 94 | 90 | 95 | 92 | 81 | 78 |
| MI | Soja | 95 | 90 | 98 | 94 | 91 | 66 |
| MI | Trigo inv. | 95 | 95 | 92 | 88 | — | 85 |
| MI | Avena | 68 | 54 | 39 | 41 | — | 50 |
| ND | Maíz (todos los usos) | 97 | 95 | 97 | 98 | 87 | 77 |
| ND | Soja | 99 | 99 | 98 | 97 | 97 | 88 |
| ND | Trigo prim. (sin durum) | 97 | 90 | 90 | 83 | — | 70 |
| ND | Durum | 72 | 80 | 54 | 67 | — | 64 |
| ND | Cebada | 60 | 51 | 59 | 48 | — | 35 |
| ND | Canola | 94 | 92 | 96 | 92 | 83 | 79 |
| ND | Girasol aceitero | 77 | 82 | 70 | 38 | 23 | 17 |
| ND | Frijol seco | 93 | 92 | 87 | 90 | 50 | 70 |

**Superficie sembrada total del estado** (miles de acres, fila de estado de Quick Stats, encuesta):

| Estado | Cultivo | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| MI | Maíz (todos los usos) | 2.350 | 2.350 | 2.300 | 2.400 | 2.300 | 2.350 | 2.300 |
| MI | Soja | 2.200 | 2.150 | 2.250 | 2.040 | 2.230 | 2.080 | 2.200 |
| MI | Frijol seco (excl. garbanzo) | 255 | 210 | 215 | 210 | 255 | 250 | 225 |
| MI | Remolacha | 157 | 155 | 139 | 133 | 135 | 134 | 137 |
| ND | Maíz (todos los usos) | 1.950 | 4.100 | 2.950 | 4.050 | 3.950 | 4.700 | 4.750 |
| ND | Soja | 5.750 | 7.250 | 5.700 | 6.200 | 6.600 | 6.550 | 6.850 |
| ND | Trigo (todos) | 6.650 | 6.470 | 6.195 | 6.610 | 6.575 | 6.430 | 5.510 |
| ND | Canola | 1.520 | 1.750 | 1.800 | 1.930 | 2.140 | 1.810 | 2.330 |
| ND | Girasol (todos) | 733 | 494 | 717 | 575 | 305 | 575 | 626 |
| ND | Cebada | 530 | 580 | 730 | 690 | 370 | 450 | 415 |
| ND | Frijol seco (excl. garbanzo) | 820 | 660 | 570 | 530 | 730 | 580 | 455 |
| ND | Remolacha | 221 | 226 | 251 | 229 | 216 | 213 | 205 |

El dato de maíz de ND en 2020 (1.950.000 acres) se verificó en el CSV de Quick Stats. No investigué la causa: no la busqué y no la supongo.

## Crop Progress (reportes semanales, nivel estado)

| Estado | Cultivo | Etapas | Años con valor (2000–2026) |
|---|---|---|---|
| MI, ND | Maíz | PLANTED, EMERGED, SILKING, DOUGH, DENTED, MATURE, HARVESTED | 27 de 27 |
| MI, ND | Soja | PLANTED, EMERGED, BLOOMING, SETTING PODS, DROPPING LEAVES, HARVESTED | 27 de 27 |
| MI | Trigo de invierno | PLANTED, EMERGED (otoño previo), HEADED, HARVESTED | 27 de 27 |
| MI | Remolacha | PLANTED (26 años, desde 2001), HARVESTED (27) | casi completo |
| ND | Trigo de primavera | PLANTED, EMERGED, HEADED, HARVESTED | 27 de 27 |
| ND | Cebada | PLANTED, EMERGED, HEADED, HARVESTED | 27 de 27 |
| ND | Avena | PLANTED, EMERGED, HEADED, HARVESTED | 27 de 27 |
| ND | Remolacha | PLANTED, HARVESTED | 27 de 27 |
| ND | Girasol | PLANTED (23 años), HARVESTED (22) | con huecos |
| MI | Avena | — (MI no está en la tabla) | — |
| ND | Trigo de invierno | — (ND no está en la tabla) | — |
| — | Canola, frijol seco, lino, durum | no hay tablas en el reporte nacional (ningún reporte tiene "Canola …" ni "Dry Edible Beans … - Selected States") | — |

No miré los reportes estatales (*Michigan Crop Progress & Condition*, *North Dakota Crop Progress & Condition*). Es posible que traigan canola, frijol, durum o lino, pero no lo verifiqué.

**Día del año típico del 50 %** (mediana 2000–2018, interpolación lineal entre semanas; trigo de invierno sembrado y emergido = otoño previo a la cosecha):

| Estado | Cultivo | Sembrado | Emergido | Floración / espigado | Cosechado |
|---|---|---|---|---|---|
| MI | maíz | 132 | 145 | 206 | 306 |
| MI | soja | 146 | 155 | 199 | 289 |
| MI | trigo inv. | 282 | 295 | 153 | 200 |
| MI | remolacha | 116 | — | — | 301 |
| ND | maíz | 131 | 145 | 206 | 298 |
| ND | soja | 142 | 155 | 199 | 277 |
| ND | trigo prim. | 126 | 139 | 184 | 231 |
| ND | cebada | 130 | 140 | 184 | 228 |
| ND | avena | 128 | 141 | 185 | 228 |
| ND | remolacha | 123 | — | — | 282 |
| ND | girasol | 150 | — | — | 301 |

Cada mediana se calculó sobre 19 años, salvo la remolacha de MI (16 sembrado, 18 cosechado), la remolacha de ND (17 cosechado) y el girasol (13 sembrado, 14 cosechado).

**Hueco de 2025.** No hay datos entre la semana al 28-09-2025 y la semana al 16-11-2025. Cosecha del 28-09 al 16-11: maíz MI 7 → 82 % y ND 0 → 80 %; soja MI 14 → 95 % y ND 8 → 97 %; remolacha MI 13 → 99 % y ND 18 → 99 %; girasol ND 0 → 80 %. Todos los cruces del 50 % de la cosecha de 2025 caen dentro del hueco.

## Particularidades

- **MI, frijol seco y remolacha:** son cultivos importantes del estado (unos 210–255 mil acres de frijol y 133–157 mil de remolacha), pero **no tienen condado después de 2018**. La lista de PDF de *County Estimates* de NASS Michigan solo trae maíz, soja, trigo de invierno, avena, ganado y alquileres. En una rotación por condado, para estos cultivos solo sirve el CDL (clase 42 frijol seco y 41 remolacha; no verificadas en esta tarea contra `clases_cdl.csv`) o el Censo.
- **ND, trigo de primavera, cebada, canola y girasol:** todos tienen condado, pero con cobertura muy dispar. El trigo de primavera llega al 70–97 % de la superficie en condados publicados. La canola, al 79–96 %. La cebada, al 35–60 %. El girasol aceitero se cae del 77 % en 2020 al 17 % en 2025. El trigo de primavera y la cebada no tienen 2024, la canola y el girasol sí. La lista de *County Estimates* de NASS North Dakota trae mapas 2023 de trigo de invierno, de primavera y durum, cebada, avena, maíz silo y grano, soja, canola, lino, girasol aceitero, frijol, arveja, heno y lenteja, lo que coincide con Quick Stats.
- **ND, superficie:** tiene 5,7–7,25 M acres de soja y una superficie de maíz que varía mucho entre años (1,95–4,75 M). El maíz y la soja tienen condado para el 87–99 % de la superficie en 2020–2024, y bajan en 2025 (77 y 88 %).
- **Riego:** no se contó. Los conteos usan solo los `Data Item` de todas las prácticas.

## Lo que no cubre

No se contaron las prácticas `IRRIGATED` / `NON-IRRIGATED`, los años anteriores a 2018 ni el Censo. No se cruzaron por condado las cuatro variables: las tablas de condados usan el rendimiento, y la de superficie usa la sembrada. No se miraron los reportes estatales de Crop Progress. Los conteos son del 2026-11-15 y cambian si NASS revisa.

Fuentes:
- [USDA NASS Quick Stats, interfaz web](https://quickstats.nass.usda.gov/), consultas del 2026-11-15 con `nass_mi_nd_conteo.py` (160 CSV).
- [Crop Progress, publicación semanal (USDA NASS, archivo ESMIS)](https://esmis.nal.usda.gov/publication/crop-progress), consultado 2026-11-15: 1.120 reportes de texto 1995–2026, por ejemplo [prog4526.txt](https://esmis.nal.usda.gov/sites/default/release-files/796141/prog4526.txt).
- [County Estimates de NASS Michigan](https://www.nass.usda.gov/statistics-by-state/michigan/publications/county-estimates) y [North Dakota](https://www.nass.usda.gov/statistics-by-state/north-dakota/publications/county-estimates), consultados 2026-11-15 (solo la lista de PDF).
- [Códigos de condado del Census 2020, MI](https://www2.census.gov/geo/docs/reference/codes2020/cou/st26_mi_cou2020.txt) y [ND](https://www2.census.gov/geo/docs/reference/codes2020/cou/st38_nd_cou2020.txt), consultados 2026-11-15.
- `docs/research/nass_mo_wi_sd.md` y `docs/research/nass_2024_2025.md`, de este repo.

Confianza:
- **Alta:** conteos de condado, filas combinadas, superficie de estado y tablas de Crop Progress (salen directo de NASS).
- **Media:** días típicos del 50 % (interpolación propia) y % de superficie en condados.
- **Sin verificar:** reportes estatales de Crop Progress, causa del dato de maíz de ND en 2020 y códigos del CDL para frijol y remolacha.

Impacto:
- Si se suman MI y ND (decisión del humano), el paquete `cultivos` sirve tal cual para maíz, soja, trigo de invierno (solo MI) y avena: se descartan las "OTHER COUNTIES", el faltante es una fila ausente y 2024 no tiene granos chicos.
- Cambios que habría que proponer al humano:
  - En ND, `produccion_anual.csv` dejaría afuera trigo de primavera, durum, cebada, canola y girasol, que juntos ocupan más superficie que el maíz. Agregarlos cambia la lista de cultivos y el esquema.
  - En MI, el frijol seco y la remolacha solo se pueden ver en el CDL (`rotacion_anual.csv`), no en el rendimiento.
  - En ND, la alfalfa y el heno sí tienen condado después de 2018, a diferencia del resto de los estados.
  - En `fenologia_estado.csv`, maíz y soja salen sin cambios. Para ND convendría sumar trigo de primavera, cebada y girasol; para MI, trigo de invierno y remolacha.
- Para ML: ND está en el borde norte, con una temporada corta (cosecha de soja hacia el día 277). La cobertura de condado de 2025 en maíz es del 53 % en MI y del 58 % en ND.
