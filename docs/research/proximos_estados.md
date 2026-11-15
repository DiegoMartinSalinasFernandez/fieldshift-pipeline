# Próximos estados: Dakota del Sur, Wisconsin, Misuri, Míchigan (y Dakota del Norte)

Pregunta: Si el humano suma estados a los 7 actuales (IA, IL, IN, OH, NE, MN, KS), ¿cuál conviene primero? Para
cada candidato: condados, superficie de maíz y soja, cobertura de rendimientos de condado en NASS, qué cambia
respecto de los 7 (riego, doble cultivo, cultivos nuevos, teselas MODIS, gSSURGO), cuánto pesa la descarga y
cuánto aporta para que el modelo generalice a zonas nuevas.

Respuesta corta:

__RESPUESTA_CORTA__

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
- **Tamaño de descarga:** no se bajó nada de los candidatos. Se escaló desde las dos referencias medidas en el
  tablero (T001: OH+NE+MN = 21 GB y 35.486 archivos; T002: KS = 11 GB), por condado y por km².

__NASS__

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

__CAMBIOS__

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

__GENERALIZAR__

## 7. Orden recomendado

__ORDEN__

Fuentes:
- [Census Gazetteer Files 2024, counties](https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_counties_national.zip), consultado 2026-11-15
- [Census Cartographic Boundary Files 2023, states 1:20M](https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_20m.zip), consultado 2026-11-15
- [USDA NASS Quick Stats, base completa (`qs.crops_20261114.txt.gz`)](https://www.nass.usda.gov/datasets), consultado 2026-11-15
- [Soil Data Access (USDA NRCS), servicio `post.rest`, tablas `sacatalog`, `legend` y `mapunit`](https://sdmdataaccess.sc.egov.usda.gov/), consultado 2026-11-15
- [Microsoft Planetary Computer, colección `gnatsgo-rasters` (STAC)](https://planetarycomputer.microsoft.com/api/stac/v1/collections/gnatsgo-rasters), consultado 2026-11-15
- Tamaños medidos: `coordinacion/tareas/T001-crudos-oh-ne-mn.md` y `T002-crudos-ks.md`; riego por condado: `docs/research/riego_nass.md`.

Confianza: __CONFIANZA__

Impacto: ninguno hasta que el humano decida. Si se suma un estado: `config/config.yaml` (lista de estados y,
según el estado, cultivos nuevos), `coordinacion/maquinas.yaml` (qué máquina lo tiene), un release nuevo en
`scripts/entregar.py` y el paquete `cultivos` (filtros de NASS para los cultivos que se agreguen).
