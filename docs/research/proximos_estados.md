# Próximos estados: Dakota del Sur, Wisconsin, Misuri, Míchigan (y Dakota del Norte)

Pregunta: Si el humano suma estados a los 7 actuales (IA, IL, IN, OH, NE, MN, KS), ¿cuál conviene primero? Para
cada candidato: condados, superficie de maíz y soja, cobertura de rendimientos de condado en NASS, qué cambia
respecto de los 7 (riego, doble cultivo, cultivos nuevos, teselas MODIS, gSSURGO), cuánto pesa la descarga y
cuánto aporta para que el modelo generalice a zonas nuevas.

Respuesta corta:

Si el humano suma estados, el orden recomendado es **1) Dakota del Sur, 2) Misuri, 3) Wisconsin**, con
Dakota del Norte y Míchigan después. **SD** es el que más maíz y soja agrega (11,0 M ac sembrados por año en
2020–2024, el 10 % de lo que suman los 7 actuales). Además es maíz de secano en el borde oeste y seco: casi
no se riega (3,5 % del maíz grano en el Censo 2022, contra 53 % en NE). **MO** suma el sur caluroso, con doble
cultivo de soja (9 % de la soja en promedio, hasta 16 % en 2024), y es lo que más le falta al modelo. A cambio,
su cobertura de rendimientos es la peor: el 29 % de la superficie de maíz de condado de 2020–2025 está en
"OTHER (COMBINED) COUNTIES". **WI** tiene los datos más limpios (solo 1–4 % de la superficie en la fila 998) y
aporta el extremo frío y lechero, pero el 22 % de su maíz es para silaje. Ninguno necesita teselas MODIS nuevas.
Todos tienen SSURGO completo. Cada uno pesa entre 5 y 12 GB (estimado, no medido), así que todos necesitan
el OK del humano por la regla de los 5 GB. En los datos de encuesta por condado de NASS no hay ningún `(D)`:
lo oculto va a la fila 998.

Detalle:

## 1. Cómo se verificó

- **Condados y superficie de tierra:** Census Gazetteer 2024 de condados (`2024_Gaz_counties_national.zip`,
  columna `ALAND_SQMI` pasada a km²).
- **Teselas MODIS:** límites de estados del Census (`cb_2023_us_state_20m.zip`), grilla de puntos cada 0,02°
  dentro de cada estado y fórmula de la grilla sinusoidal de MODIS (radio 6.371.007,181 m, tesela de
  1.111.950,52 m). Es aproximado en los bordes: una tesela que toca el estado en menos de 0,02° puede faltar.
- **SSURGO:** consulta a Soil Data Access (`sacatalog`), cantidad de áreas de levantamiento por estado y fecha de
  la versión publicada (`saverest`). Además, una consulta de unidades `NOTCOM` (sin levantar) en los candidatos.
- **NASS:** base completa de Quick Stats `qs.crops_20261114.txt.gz` (1,05 GB según la página de datasets),
  bajada a `/tmp` (fuera del repo y de `data/`) y recorrida con `docs/research/proximos_estados_conteo.py`.
  Filtros: `SOURCE_DESC=SURVEY`, `DOMAIN_DESC=TOTAL`, `REFERENCE_PERIOD_DESC=YEAR`; para condados,
  `PRODN_PRACTICE_DESC=ALL PRODUCTION PRACTICES`. El primer intento en streaming se cortó al 95 % (conexión
  rota); el segundo se bajó con `curl -C -`.
  Riego del Censo 2022 y soja de segunda: `docs/research/proximos_estados_riego.py`, sobre el mismo archivo.
- **Tamaño de descarga:** no se bajó nada de los candidatos. Se escaló desde las dos referencias medidas en el
  tablero (T001: OH+NE+MN = 21 GB y 35.486 archivos; T002: KS = 11 GB), por condado y por km².

## 2. NASS: superficie sembrada y cobertura de rendimientos

### 2.1 Superficie sembrada, nivel estado, promedio 2020–2024 (SURVEY, miles de acres)

Maíz y soja: `CORN - ACRES PLANTED` y `SOYBEANS - ACRES PLANTED` (maíz de todos los usos). Riego: Censo
Agropecuario 2022, `CORN, GRAIN, IRRIGATED - ACRES HARVESTED` sobre `CORN, GRAIN - ACRES HARVESTED`, y lo mismo
para soja. Doble cultivo: `SOYBEANS, FOLLOWING ANOTHER CROP (DOUBLE CROPPED) - AREA PLANTED, MEASURED IN PCT`.

| Estado | Maíz | Soja | Maíz + soja | % de los 7 | Maíz silaje (cosech.) | % maíz grano con riego (2022) | % soja con riego (2022) | % soja de segunda 2020–2024 |
|---|---|---|---|---|---|---|---|---|
| IA | 13.080 | 9.930 | 23.010 | | 342 | 1,2 | 0,9 | no publicado |
| IL | 11.020 | 10.570 | 21.590 | | 98 | 3,3 | 2,1 | 4–9 |
| IN | 5.340 | 5.710 | 11.050 | | 118 | 6,3 | 3,5 | 2–5 |
| OH | 3.500 | 4.960 | 8.460 | | 170 | 0,5 | 0,3 | 1–3 |
| NE | 9.940 | 5.420 | 15.360 | | 302 | 52,7 | 43,9 | no publicado |
| MN | 8.230 | 7.460 | 15.690 | | 410 | 3,9 | 1,6 | no publicado |
| KS | 5.870 | 4.736 | 10.606 | | 310 | 25,4 | 8,0 | 7–23 |
| **7 actuales** | **56.980** | **48.786** | **105.766** | 100 | | | | |
| SD | 5.800 | 5.210 | 11.010 | 10,4 | 468 | 3,5 | 2,4 | no publicado |
| WI | 3.910 | 2.114 | 6.024 | 5,7 | 844 | 4,7 | 3,2 | no publicado |
| MO | 3.550 | 5.840 | 9.390 | 8,9 | 104 | 9,4 | 10,4 | 6–16 |
| MI | 2.340 | 2.174 | 4.514 | 4,3 | 333 | 13,3 | 6,2 | no publicado |
| ND | 3.400 | 6.300 | 9.700 | 9,2 | 217 | 2,8 | 0,7 | no publicado |

"No publicado" quiere decir que NASS no publica esa serie para el estado. Es probable que el doble cultivo
sea marginal ahí, pero no lo verifiqué. Con el CDL (clase 26) se mediría.

Otros cultivos de los candidatos (miles de acres, promedio 2020–2024; alfalfa y heno son cosechados, el resto
sembrado):

| Estado | Cultivos que no están entre los 6 de `config/` o que pesan mucho |
|---|---|
| SD | trigo de primavera 728, girasol 514, sorgo 311, alfalfa 1.617, heno total 2.831, trigo de invierno 808 |
| WI | maíz silaje 844 (22 % del maíz sembrado), alfalfa 1.576, papa 67, cebada 15 |
| MO | algodón 341, arroz 201 (Bootheel, con riego), heno total 3.228, trigo de invierno 642 |
| MI | poroto seco 229, remolacha azucarera 144, papa 50, trigo de invierno 512, alfalfa 724 |
| ND | trigo de primavera 5.480, canola 1.828, trigo durum 917, poroto seco 662, cebada 580, girasol 565, remolacha 229, papa 74 |

### 2.2 Rendimiento de condado, maíz grano y soja, 2000–2025

`SURVEY`, `AGG_LEVEL_DESC=COUNTY`, `ALL PRODUCTION PRACTICES`, `CORN, GRAIN - YIELD, MEASURED IN BU / ACRE` y
`SOYBEANS - YIELD, MEASURED IN BU / ACRE`. "Cobertura" = condado-año con rendimiento sobre condados × 26 años.
"% área en 998" = superficie cosechada en las filas `county_code` 998 sobre la cosechada de todas las filas de
condado del estado.

| Estado | Condados | Cobertura maíz | Cobertura soja | % área maíz en 998 (2000–2025) | % área maíz en 998 (2020–2025) | % área soja en 998 (2020–2025) | Filas `(D)` |
|---|---|---|---|---|---|---|---|
| IA | 99 | 96,0 % | 94,7 % | 3,4 | 12,5 | 19,2 | 0 |
| IL | 102 | 91,1 % | 91,2 % | 5,2 | 16,6 | 18,4 | 0 |
| IN | 92 | 89,5 % | 90,3 % | 6,0 | 14,9 | 15,3 | 0 |
| OH | 88 | 89,6 % | 85,3 % | 3,5 | 9,8 | 11,6 | 0 |
| NE | 93 | 85,6 % | 71,6 % | 8,1 | 25,7 | 23,6 | 0 |
| MN | 87 | 82,5 % | 82,4 % | 4,8 | 13,9 | 15,6 | 0 |
| KS | 105 | 76,6 % | 69,6 % | 23,1 | 30,7 | 18,3 | 0 |
| SD | 66 | 79,4 % | 65,7 % | 10,6 | 20,8 | 22,7 | 0 |
| WI | 72 | 84,2 % | 81,9 % | 1,5 | 1,2 | 3,5 | 0 |
| MO | 115 | 65,8 % | 67,7 % | 17,8 | 28,7 | 23,3 | 0 |
| MI | 83 | 68,8 % | 55,4 % | 5,3 | 11,1 | 10,7 | 0 |
| ND | 53 | 76,5 % | 68,1 % | 11,0 | 8,4 | 3,6 | 0 |

Condados con rendimiento de maíz por año (de la misma corrida, sin la 998):

| Año | SD | WI | MO | MI | ND |
|---|---|---|---|---|---|
| 2000 | 66 | 63 | 95 | 47 | 51 |
| 2005 | 64 | 63 | 90 | 59 | 42 |
| 2010 | 57 | 62 | 92 | 63 | 45 |
| 2015 | 40 | 57 | 54 | 57 | 36 |
| 2019 | 24 | 53 | 47 | 49 | 21 |
| 2020 | 58 | 64 | 89 | 60 | 45 |
| 2022 | 52 | 64 | 67 | 59 | 44 |
| 2023 | 39 | 62 | 74 | 57 | 48 |
| 2024 | 41 | 59 | 53 | 50 | 42 |
| 2025 | 37 | 60 | 44 | 44 | 31 |

Lecturas:
- **No hay `(D)` en los rendimientos de condado de la encuesta**, en ningún estado ni año: la columna `filas_codigo`
  dio 0 siempre. Coincide con `riego_nass.md`. NASS junta los condados con poca muestra en una fila 998 por
  distrito agrícola (por eso hay más de una fila 998 por año). En los candidatos, `flag_nass` solo va a tener
  valores en el Censo.
- La cobertura cae en todos los estados desde 2015, con pozos en 2019 y en 2024–2025 (ver `nass_2024_2025.md`).
  En SD y MO cae más que en los 7. 2025 ya está publicado para los cinco candidatos.
- La cobertura de WI y MI es baja en número de condados porque el norte de los dos estados casi no tiene maíz.
  Por superficie, WI es el mejor de los 12: casi nada cae en la 998.
- MO y SD son los peores por superficie (21–29 % del maíz de 2020–2025 sin condado), parecidos a KS y NE.

## 3. Condados, área y teselas MODIS

| Estado | Condados (Gazetteer 2024) | Tierra (km²) | Teselas MODIS | Áreas SSURGO (SDA) | Versión SSURGO publicada |
|---|---|---|---|---|---|
| IA | 99 | 144.660 | h10v04, h11v04 | 99 | 2026-09 |
| IL | 102 | 143.778 | h10v04, h10v05, h11v04, h11v05 | 102 | 2026-08 |
| IN | 92 | 92.787 | h11v04, h11v05 | 92 | 2026-08/09 |
| OH | 88 | 105.824 | h11v04, h11v05, h12v04 | 88 | 2026-08/09 |
| NE | 93 | 198.950 | h10v04 | 93 | 2026-09 |
| MN | 87 | 206.245 | h11v04, h12v04 | 92 | 2026-09 |
| KS | 105 | 211.754 | h09v05, h10v05 | 105 | 2026-08 |
| **7 actuales** | **666** | **1.103.798** | h09v05, h10v04, h10v05, h11v04, h11v05, h12v04 | | |
| SD | 66 | 196.342 | h10v04, h11v04 | 67 | 2026-08 a 2026-10 |
| WI | 72 | 140.295 | h11v04 | 72 | 2026-08/09 |
| MO | 115 | 178.053 | h10v04, h10v05, h11v04 | 114 | 2026-08/09 |
| MI | 83 | 146.622 | h11v04, h12v04 | 82 | 2026-08/09 |
| ND | 53 | 178.694 | h10v04, h11v04 | 53 | 2026-09 |

- MO tiene 114 condados más la ciudad independiente de St. Louis (FIPS 29510), que cuenta como equivalente de
  condado en el Gazetteer: 115.
- **Teselas MODIS: ningún candidato necesita teselas nuevas.** Todas las de SD, WI, MO, MI y ND ya están en las 6
  que cubren los 7 actuales. La descarga de MODIS (Planetary Computer, ventana por condados) crece por el área
  leída, no por teselas nuevas.
- **gSSURGO / SSURGO:** los cinco candidatos tienen todas sus áreas de levantamiento publicadas en SDA en la
  versión de agosto a octubre de 2026, y la consulta de unidades `NOTCOM` (sin levantar) en SD, WI, MO, MI y ND
  no devolvió filas. La página del gSSURGO del NRCS no respondió en 40 s (igual que en `gssurgo.md`), así que no
  verifiqué el tamaño del geodatabase por estado. El paquete `suelo_terreno` usa SDA (tabular) y gNATSGO de
  Planetary Computer (colección `gnatsgo-rasters`, cobertura de todo EE.UU. según su STAC), así que no depende
  de esa página.

## 4. Qué cambia respecto de los 7

| Tema | SD | WI | MO | MI | ND |
|---|---|---|---|---|---|
| Riego | bajo (3,5 % maíz); no es un segundo NE | bajo (4,7 %), arenas centrales con papa | medio (9–10 %); Bootheel con arroz y soja regada | **el más alto de los candidatos (13 % maíz)**, sudoeste arenoso | muy bajo |
| Doble cultivo trigo/soja | no publicado | no publicado | **sí, 6–16 % de la soja** | no publicado | no publicado |
| Cultivos a sumar en `config/cultivos.csv` | trigo de primavera, girasol; sorgo (ver `sorgo.md`) | maíz silaje como uso aparte (22 %); papa opcional | algodón y arroz solo como clases de máscara (no como target) | poroto seco, remolacha | trigo de primavera, durum, canola, girasol, cebada, poroto seco |
| Clases CDL (ya están en `clases_cdl.csv` con grupo `otro`; habría que darles grupo propio) | 23 (trigo de primavera), 6 (girasol), 4 (sorgo) | 43 (papa) | 2 (algodón), 3 (arroz) | 42 (poroto seco), 41 (remolacha) | 23, 22 (durum), 31 (canola), 6, 21 (cebada) |
| Ventanas fijas (abr–sep, jul/ago) | sirven | la temporada empieza más tarde; julio sigue siendo floración | la siembra empieza antes; con doble cultivo la soja florece en septiembre | sirven | la temporada es más corta |
| Crop Progress | existe para maíz y soja (verificar en `crop_progress_estados_nuevos.md`) | ídem | ídem | ídem | ídem |
| Teselas MODIS | sin nuevas | sin nuevas | sin nuevas | sin nuevas | sin nuevas |
| SSURGO | completo (67 áreas) | completo | completo | completo | completo |

No verifiqué en esta tarea que Crop Progress publique maíz y soja para los cinco candidatos: queda para el
paquete `cultivos` si se suma el estado. Los códigos de clase CDL los comprobé contra
`data/reference/clases_cdl.csv`: los 11 ya están, todos con grupo `otro`.

## 5. Tamaño estimado de la descarga

Escalado desde lo medido (no es una medición): KS = 11 GB / 105 condados / 211.754 km² (0,105 GB por condado,
0,052 GB por 1.000 km²); OH+NE+MN = 21 GB / 268 condados / 510.019 km² (0,078 GB por condado, 0,041 GB por
1.000 km²). El CDL, MODIS e IMERG crecen con el área; POWER, NLDAS y las consultas de NASS, con los condados.
El rango va del menor al mayor de las cuatro estimaciones.

| Estado | Por condado (GB) | Por área (GB) | Rango estimado |
|---|---|---|---|
| SD | 5,2–6,9 | 8,1–10,2 | **5–10 GB** |
| WI | 5,6–7,6 | 5,8–7,3 | **6–8 GB** |
| MO | 9,0–12,1 | 7,3–9,2 | **7–12 GB** |
| MI | 6,5–8,7 | 6,0–7,6 | **6–9 GB** |
| ND | 4,1–5,6 | 7,4–9,3 | **4–9 GB** |
| SD+WI+MO+MI | | | **24–39 GB** |

Todos pasan el umbral de 5 GB de la regla 6 del CLAUDE.md: cualquier estado nuevo necesita el OK del humano para
la descarga, además de la decisión de sumarlo. Para máquinas con poco disco (max-2 tenía 7,5 GB libres en T013),
conviene trabajar por paquete: bajar, procesar, publicar y borrar el crudo.

## 6. Qué aporta cada uno para generalizar

Es un juicio sobre los datos de arriba, no un experimento. Lo que el modelo ya ve con los 7: el núcleo húmedo
(IA, IL, IN, OH), el norte frío (MN), el oeste con mucho riego (NE) y el sur seco con trigo y sorgo (KS).

- **SD:** llena el hueco entre MN y NE con maíz y soja **de secano** a la misma latitud y con menos lluvia. Hoy
  el secano seco del oeste aparece solo en KS, mezclado con trigo, y en el oeste de NE, mezclado con riego. Es
  la mejor prueba para que el modelo separe el efecto del clima del efecto del riego. Es el más grande de los
  candidatos y el que menos cambia `config/`.
- **MO:** es la única forma de que el modelo vea el sur húmedo y caluroso (no medí acá los días de calor ni los suelos:
  sale de `clima` y `suelo_terreno` una vez bajado) y el doble cultivo en serio. Es lo que más extrapolación evita si la herramienta
  se usa al sur del Corn Belt. En contra: la peor cobertura de rendimientos de condado y el Bootheel, que parece
  otro sistema (arroz, algodón, riego).
- **WI:** extremo frío y húmedo, con mucha alfalfa y silaje (rotaciones maíz–alfalfa que casi no hay en los 7).
  Tiene los rendimientos más completos. Su maíz grano es una parte menor del maíz total.
- **ND:** el extremo frío y seco, pero el maíz y la soja compiten con trigo de primavera y canola. Para
  `rotacion_*` cambia mucho: habría que sumar 4 a 6 cultivos.
- **MI:** el más chico y con más riego entre los candidatos. Aporta clima de los Grandes Lagos, pero poca
  superficie.

## 7. Orden recomendado

1. **Dakota del Sur.** Es el que más superficie suma (10 % de los 7), con secano en el borde oeste. Necesita pocos
   cambios en `config/` (trigo de primavera y girasol como clases) y pesa 5–10 GB.
2. **Misuri.** Suma el sur caluroso y el doble cultivo. Hay que avisar a ML de que el 29 % de la superficie de
   maíz de 2020–2025 queda en la 998 y conviene enmascarar el Bootheel (algodón y arroz). Pesa 7–12 GB.
3. **Wisconsin.** Suma el norte frío con los datos más limpios. Hay que definir si el silaje entra como cultivo.
   Pesa 6–8 GB.
4. **Dakota del Norte**, solo si se quiere el extremo noroeste: necesita varios cultivos nuevos.
5. **Míchigan**, al final: poco maíz y soja, más riego y cultivos especiales.

Con los tres primeros, la descarga estimada es de 18 a 30 GB. Conviene hacerlo de a un estado por máquina.

Fuentes:
- [Census Gazetteer Files 2024, counties](https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_counties_national.zip), consultado 2026-11-15
- [Census Cartographic Boundary Files 2023, states 1:20M](https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_20m.zip), consultado 2026-11-15
- [USDA NASS Quick Stats, base completa (`qs.crops_20261114.txt.gz`)](https://www.nass.usda.gov/datasets), consultado 2026-11-15
- [Soil Data Access (USDA NRCS), servicio `post.rest`, tablas `sacatalog`, `legend` y `mapunit`](https://sdmdataaccess.sc.egov.usda.gov/), consultado 2026-11-15
- [Microsoft Planetary Computer, colección `gnatsgo-rasters` (STAC)](https://planetarycomputer.microsoft.com/api/stac/v1/collections/gnatsgo-rasters), consultado 2026-11-15
- Tamaños medidos: `coordinacion/tareas/T001-crudos-oh-ne-mn.md` y `T002-crudos-ks.md`; riego por condado: `docs/research/riego_nass.md`.

Confianza: alta para los conteos de NASS, Censo, Gazetteer y SDA (se corrieron sobre los archivos completos); media para los tamaños de descarga (escalados, no medidos); media para la sección 6 y el orden (es un juicio).

Impacto: ninguno hasta que el humano decida. Si se suma un estado: `config/config.yaml` (lista de estados y,
según el estado, cultivos nuevos), `coordinacion/maquinas.yaml` (qué máquina lo tiene), un release nuevo en
`scripts/entregar.py` y el paquete `cultivos` (filtros de NASS para los cultivos que se agreguen).
