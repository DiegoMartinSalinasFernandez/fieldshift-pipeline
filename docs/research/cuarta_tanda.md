# Cuarta tanda: cuánto pesa y cuánto tarda bajar Míchigan, Dakota del Norte y Kentucky

Pregunta: si el humano suma una cuarta tanda con MI, ND y KY, ¿cuánto pesa y cuánto tarda la descarga de cada
estado y de cada paquete? ¿Hacen falta teselas MODIS o celdas de grilla nuevas? ¿Hay algún paquete que no cubra
alguno de los tres estados?

Respuesta corta:

- **Peso estimado: MI 8–11 GB, ND 4–5 GB y KY 4–5 GB.** Son 16–20 GB para los tres, más ~5,8 GB de archivos
  nacionales (NASS y GRACE-DA-DM). Esos se copian de una máquina que ya los tenga, como en T001. No se bajó
  nada de los tres estados: CDL, NASADEM y SMAP salen de tamaños reales leídos con HEAD o de un día de
  muestra. MODIS, paisaje y el total se escalan desde lo medido en T001, T002 y T013.
- **MI pesa el doble que ND o KY con menos tierra.** El bbox de sus condados (Península Superior más Península
  Inferior) cubre 471.000 km², contra 147.000 km² de tierra. La mayor parte es lago Míchigan y lago Superior.
  MODIS y paisaje bajan todo el bbox. Si se parte MI en dos bboxes, la descarga baja mucho (propuesta abajo).
- Los tres pasan el umbral de 5 GB de la regla 6 (ND y KY quedan justo en el borde), así que **cada uno necesita
  el OK del humano**.
- **Tiempo estimado: 0,5–1 h de descarga para ND y para KY, y 1–2 h para MI**, en una máquina Max con los dos
  carriles de §9. El procesamiento tarda otras 2–3 h para el grupo, si va como en T003. Es un escalado del
  tablero, no una medición.
- **Teselas MODIS: ninguna nueva.** MI cae en h11v04 y h12v04, ND en h10v04 y h11v04 (ninguna más) y KY en h10v05
  y h11v05. Las seis ya se bajan para los 7 estados actuales.
- **Cobertura:** los tres estados están cubiertos por Crop-CASMA (SMAP), GRACE-DA-DM de EE.UU., NASADEM y CDL. No
  encontré ningún paquete que deje afuera a alguno. Lo de NLDAS y paisaje se infiere de la documentación de
  esos productos, no lo probé.

Detalle:

## 1. Cómo se midió

- **Geometría:** `docs/research/cuarta_tanda_geometria.py` lee los condados del Census
  (`cb_2023_us_county_500k`, el mismo archivo que `src/base/download.py`). Lo bajé a `/tmp`, fuera del repo
  y de `data/`. Por estado calcula los condados, la tierra (`ALAND`) y el bbox con el margen de
  `src/vegetacion/download.py` (0,05°). También cuenta las teselas MODIS: puntos cada 0,02° dentro de los
  condados, pasados a la grilla sinusoidal, así que es aproximado en los bordes. Con la regla de
  `src/suelo_terreno/download.py` saca las teselas NASADEM de 1°, y cuenta las celdas IMERG de 0,1° que
  tocan algún condado. Para el CDL repite la búsqueda STAC de `teselas_cdl()` de `src/cultivos/download.py`
  (colección `usda-cdl` de Planetary Computer, año 2020) y suma el `Content-Length` de cada tesela. Al
  NASADEM le pide lo mismo con un HEAD. No baja los archivos.
- **SMAP:** pedí al WPS de Crop-CASMA las dos capas (`SUB` y `TOP`) de un solo día (2023-07-15), con
  `GetFileByFips` y los FIPS 26, 38, 21 y 20 (KS, de control), como hace `src/agua/download.py`. Los
  archivos quedaron en `/tmp`.
- **GRACE-DA-DM:** bajé un nc4 semanal a `/tmp` (`GRACEDADM_CLSM0125US_7D.A20240701.030.nc4`, 780 KB). Leí la
  extensión de la grilla y el valor de `gws_inst` en un punto de cada estado.
- **Referencias del tablero:** T001 (OH+NE+MN = 21 GB, de 23:59 a 03:03), T002 (KS = 11 GB, de 23:59 a 01:31,
  en la misma máquina y a la vez que T001), T013 (clima de KS = 385 MB en 20 min, 2.193 celdas IMERG) y T003
  (procesar OH/NE/MN, de 03:03 a 05:46). **En las notas de T003, T013 y T062 no hay `du` por paquete.** El único
  medido es el clima de KS (T013). T062 (MO/WI/SD) todavía no anotó tamaños. Los demás tamaños por paquete
  salen de los data cards: ~4,7 GB de MODIS para el bbox de IA+IL+IN (`vegetacion.md`), ~160 KB por mes de
  NLDAS (`nldas.md`) y ~5 MB por semana de GRACE antes de 2020 (`agua.md`).

## 2. Geometría por estado (medido)

| Estado | Condados | Tierra (km²) | bbox ±0,05° (km²) | bbox / tierra | Teselas MODIS | Teselas NASADEM | Celdas IMERG 0,1° | Teselas CDL 2020 |
|---|---|---|---|---|---|---|---|---|
| **MI** | 83 | 146.620 | 471.159 | 3,2 | h11v04, h12v04 | 37 | 1.997 | 43 |
| **ND** | 53 | 178.694 | 201.260 | 1,1 | h10v04, h11v04 | 37 | 2.271 | 31 |
| **KY** | 120 | 102.267 | 206.881 | 2,0 | h10v05, h11v05 | 23 | 1.187 | 27 |
| KS (ref.) | 105 | 211.754 | 227.519 | 1,1 | h09v05, h10v04, h10v05 | 44 | 2.365 | 36 |
| OH (ref.) | 88 | 105.824 | 152.824 | 1,4 | h11v04, h11v05, h12v04 | 19 | 1.242 | 25 |
| NE (ref.) | 93 | 198.950 | 254.016 | 1,3 | h10v04 | 31 | 2.230 | 40 |
| MN (ref.) | 87 | 206.245 | 400.436 | 1,9 | h11v04, h12v04 | 45 | 2.720 | 42 |
| IA+IL+IN (ref.) | 293 | 381.224 | 746.617 | 2,0 | | | | |

- Para KS el script da h10v04, que `proximos_estados.md` no listaba. El borde norte de KS está justo en 40° N, el
  límite entre v04 y v05, así que es un efecto de borde del método de puntos. De IA+IL+IN calculé solo el bbox: la
  parte del CDL del script no terminó a tiempo (cientos de HEAD) y la corté.
- El conteo de celdas IMERG da 2.365 en KS, contra 2.193 en T013. La diferencia viene del método: acá cuento
  toda celda que toca un condado.
- **MI:** el bbox de sus condados va de la Península Superior (hasta ~48,3° N y ~90,4° O) a la frontera con OH e
  IN, e incluye el lago Míchigan, el norte del lago Hurón y parte del lago Superior. **KY** es largo y angosto
  (de ~89,6° O a ~82° O), así que su bbox también duplica su tierra. **ND** es casi un rectángulo.
- Si la cuarta tanda corre junta en una máquina, los bboxes de MI, ND y KY no se tocan y `grupos_bbox()` los deja
  separados. No se baja nada entre ellos.

## 3. Teselas MODIS y grillas nuevas

- **MODIS: ninguna tesela nueva.** Las seis del total (h11v04, h12v04, h10v04, h10v05, h11v05) ya están entre las de
  los 7 estados (h09v05, h10v04, h10v05, h11v04, h11v05, h12v04). ND toca solo h10v04 y h11v04. Coincide con
  `proximos_estados.md` para MI y ND. KY no estaba en ese research: cae en v05 entero, porque su punto más al
  norte está en ~39,15° N.
- **NASADEM:** 37 teselas de 1° en MI, 37 en ND y 23 en KY, todas con HEAD 200 en Planetary Computer.
- **CDL:** 43 teselas de 90 km en MI, 31 en ND y 27 en KY en 2020. Todas existen en la colección `usda-cdl`.
- **IMERG, NLDAS, GRACE y SMAP** son grillas fijas: crece la ventana, pero no hay "celdas nuevas" que habilitar.

## 4. Cobertura por paquete

| Paquete / fuente | MI | ND | KY | Cómo lo verifiqué |
|---|---|---|---|---|
| `agua` SMAP (Crop-CASMA `GetFileByFips`) | sí | sí | sí | Un día bajado por estado: GeoTIFF EPSG:5070 9 km con 1.809 (MI), 2.223 (ND) y 1.291 (KY) celdas válidas. En MI, `SUB` llega a 0,89 m³/m³, sobre el rango físico de 0–0,6 de §7. Probablemente son celdas de costa o de lago: el filtro de `validar_csv()` y la media del condado lo tienen que absorber. Revisarlo al procesar. |
| `agua` GRACE-DA-DM EE.UU. (`GRACEDADM_CLSM0125US_7D`) | sí | sí | sí | La grilla del nc4 va de 25,06 a 52,94° N y de 124,94 a 67,06° O (224 × 464 celdas). `gws_inst` tiene valor en Minot (ND), Lansing y Marquette (MI) y Bowling Green (KY). |
| `suelo_terreno` NASADEM | sí | sí | sí | HEAD 200 en las 97 teselas. |
| `suelo_terreno` SSURGO (SDA) | sí | sí | — | En `proximos_estados.md`, MI y ND tienen todas sus áreas publicadas y ninguna `NOTCOM`. **KY no lo consulté**: queda para la tarea que lo baje. |
| `cultivos` CDL | sí | sí | sí | Teselas 2020 en la colección `usda-cdl`. 2022–2025 salen del ImageServer CROS de NASS (CONUS). No lo probé para estos estados. |
| `vegetacion` MODIS | sí | sí | sí | Las teselas ya se bajan (sección 3). |
| `nldas` (NLDAS-2 Noah, Harmony) | probable | probable | probable | No lo probé (necesita Earthdata). NLDAS-2 cubre CONUS en 0,125°, la misma grilla que GRACE-DA-DM de EE.UU., que usa su meteorología (`productos_nasa.md`). Ninguno de los tres estados sale de 25–53° N. |
| `paisaje` Annual NLCD (CONUS) | probable | probable | probable | No lo probé: es un mosaico CONUS (`paisaje.md`). |
| `clima` POWER / IMERG | sí | sí | sí | Son globales. No lo probé con estos estados. |

No encontré ningún paquete que no cubra alguno de los tres estados.

## 5. Peso estimado por estado y por paquete

Lo **medido** son los tamaños reales del CDL de 2020 y de NASADEM (con HEAD) y del SMAP de un día. El resto
está **escalado**. Supuestos:

- El CDL de 2020 se multiplica por los 18 años (2008–2025). En 2022–2025 el CDL viene de CROS, en LZW, y no
  medí cuánto pesa.
- SMAP: el archivo de un día × 2 capas × 3.929 días (2015-03-31 a 2025-12-31).
- Clima: proporcional a las celdas IMERG, desde KS (385 MB, T013).
- MODIS: 4,7 GB / 746.617 km² del bbox de IA+IL+IN = 6,3 MB cada 1.000 km² de bbox.
- NLDAS: 160 KB × 420 meses (1991–2025) para el bbox de IA+IL+IN, escalado por bbox.
- Paisaje: no hay ninguna medición en el repo. Es lo que sobra de KS al restar lo demás (sección 5.1), unos
  7,5 MB cada 1.000 km² de bbox. Es la cifra más floja.

| Paquete | MI | ND | KY | Base |
|---|---|---|---|---|
| `cultivos` CDL (18 años) | ~1,3 GB | ~1,2 GB | ~1,2 GB | medido 2020: 71 / 64 / 67 MB por año |
| `cultivos` NASS | (copia) | (copia) | (copia) | base nacional `qs.crops_*`, 1,05–1,1 GB, una vez por máquina |
| `vegetacion` MODIS | ≤ 3,0 GB | ~1,3 GB | ~1,3 GB | escalado por bbox; en MI sobreestima, porque los lagos son nodata y comprimen |
| `paisaje` NLCD | ≤ 3,5 GB | ~1,5 GB | ~1,6 GB | residuo de KS, escalado por bbox; confianza baja |
| `clima` (POWER + IMERG) | ~0,33 GB | ~0,37 GB | ~0,2 GB | escalado de T013 |
| `suelo_terreno` NASADEM | 0,21 GB | 0,29 GB | 0,29 GB | medido (HEAD) |
| `suelo_terreno` SSURGO (SDA) | chico | chico | chico | tablas de texto. No medido |
| `agua` SMAP | 0,18 GB | 0,08 GB | 0,08 GB | medido un día × 7.858 archivos |
| `agua` GRACE | (copia) | (copia) | (copia) | nacional, ~4,7 GB; no conviene rebajarlo: el servidor da ~50 KB/s por conexión (`agua.md`) |
| `nldas` | ~0,04 GB | ~0,02 GB | ~0,02 GB | escalado por bbox |
| `economia`, `validacion` | chico | chico | chico | no medido |
| **Total del estado** | **~8,6 GB** | **~4,8 GB** | **~4,7 GB** | suma de las filas |
| **Total por escalado (sección 5.1)** | **9,0–10,8 GB** | **3,8–4,6 GB** | **3,9–4,8 GB** | |

**Rango que propongo: MI 8–11 GB, ND 4–5 GB, KY 4–5 GB; los tres juntos, 16–20 GB, más ~5,8 GB nacionales si
la máquina no los tiene.** `proximos_estados.md` daba 6–9 GB para MI y 4–9 GB para ND, escalando por condado y
por tierra. Acá MI sube porque se escala por el bbox, que es lo que de verdad se baja.

### 5.1 Escalado del total

Supuse que las copias de T001 y de T002 incluyen los dos archivos nacionales, NASS (1,1 GB) y GRACE (~4,7 GB:
~885 semanas de 2003 a 2019 a ~5 MB, más ~313 de 2020 a 2025 a ~0,8 MB). Sin ellos, lo que depende del estado
es:

- KS: 11 − 5,8 = 5,2 GB en un bbox de 227.519 km², o sea **0,023 GB cada 1.000 km²**.
- OH+NE+MN: 21 − 5,8 = 15,2 GB en 807.276 km² de bbox, o sea **0,019 GB cada 1.000 km²**.

Las dos cifras son parecidas, así que el modelo "fijo nacional + proporcional al bbox" explica bien las dos
mediciones. Aplicado a los bboxes de la sección 2 da la última fila de la tabla. Con KS, el desglose de la
tabla suma unos 2,1 GB de CDL, clima, SMAP, NASADEM y NLDAS, y 1,4 GB de MODIS. Los ~1,7 GB que sobran los
asigné a paisaje.

## 6. Tiempo estimado

No hay mediciones de tiempo por paquete en el tablero. Lo que se puede escalar:

- T002 bajó KS (11 GB) en ≤ 1 h 32 min y T001 bajó OH+NE+MN (21 GB) en 3 h 04 min, las dos a la vez en max-1. Da
  unos **6–9 min por GB**, contando los nacionales.
- T013 bajó el clima de KS (385 MB, 105 condados) en ~20 min. POWER va por condado e IMERG por celda, así que el
  clima tarda más de lo que pesa: ~15 min en MI y ND y ~20 min en KY (120 condados).
- T003 procesó OH/NE/MN en 2 h 43 min, con una segunda bajada del CDL y dos arreglos de código.

| Estado | Descarga estimada | Comentario |
|---|---|---|
| MI | 1–1,5 h (hasta 2 h) | el bbox con lagos alarga MODIS y paisaje |
| ND | 0,5–0,7 h | |
| KY | 0,5–0,7 h | 120 condados: POWER tarda más que en ND |
| Los tres en una máquina | 2–3 h de descarga + 2–3 h de proceso | con los nacionales copiados. Si hay que bajar GRACE de cero, sumar horas por el límite de ~50 KB/s |

## 7. Propuestas (necesitan al humano)

1. **OK por la regla de los 5 GB** para cada estado que se sume. ND y KY quedan justo en el borde y MI pasa con
   claridad.
2. **Partir MI en dos bboxes** (Península Superior e Inferior) en `grupos_bbox()` (`src/vegetacion/download.py`,
   que también usa `src/nldas/download.py`) y en `ventanas_estado()` de `src/paisaje/download.py`. El
   rectángulo de la Inferior (~41,7–45,9° N, ~86,6–82,4° O) más el de la Superior (~45,1–48,3° N, ~90,4–83,4° O)
   evitan buena parte del lago Míchigan. No medí cuánto ahorra. Es un cambio de código, en su propia tarea.
3. **Copiar NASS y GRACE** de una máquina que ya los tenga, con sus filas del manifest, como en T001.
4. Antes de procesar MI, ver si las celdas de SMAP sobre 0,6 m³/m³ en la costa son agua. Si lo son, enmascararlas
   o anotarlo en el data card.
5. Consultar SSURGO en SDA para KY (áreas y `NOTCOM`). En este research no lo hice.

Fuentes:
- [Census Cartographic Boundary Files 2023, counties 1:500k](https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip), consultado 2026-11-15
- [Planetary Computer STAC, colección usda-cdl](https://planetarycomputer.microsoft.com/api/stac/v1/search) (búsqueda y HEAD de las teselas `cropland` de 2020), consultado 2026-11-15
- [NASADEM COG en Planetary Computer](https://nasademeuwest.blob.core.windows.net/nasadem-cog/v001/) (HEAD de 97 teselas), consultado 2026-11-15
- [Crop-CASMA WPS, GetFileByFips](https://cloud.csiss.gmu.edu/smap_service) (capas `SMAP-9KM-DAILY-SUB/TOP_2023.07.15_013000`, FIPS 26, 38, 21 y 20), consultado 2026-11-15
- [GRACE-DA-DM EE.UU., NDMC](https://nasagrace.unl.edu/data/20240701/GRACEDADM_CLSM0125US_7D.A20240701.030.nc4), consultado 2026-11-15
- Del repo: notas de T001, T002, T003 y T013; `docs/datasets/vegetacion.md`, `nldas.md`, `agua.md`, `paisaje.md`; `docs/research/proximos_estados.md` y `productos_nasa.md`.

Confianza: **alta** en la geometría, las teselas MODIS, CDL y NASADEM y la cobertura de SMAP y GRACE (medidas).
**Media** en el peso del CDL, SMAP y NASADEM y en el total por escalado. **Baja** en MODIS y paisaje por estado
y en los tiempos: no hay `du` ni tiempos por paquete en el tablero.

Impacto: ninguno en `config/` por ahora. Si se aprueba la cuarta tanda: `config/config.yaml` (estados MI, ND y
KY, a decidir por el humano), `coordinacion/maquinas.yaml` (qué máquina los baja) y, de forma opcional, el bbox
partido de MI en `src/vegetacion/download.py` y `src/paisaje/download.py`. Para ND rigen además los cambios de
cultivos de `proximos_estados.md`. KY es un estado nuevo en el research y nadie miró todavía sus cultivos ni su
cobertura en NASS.
