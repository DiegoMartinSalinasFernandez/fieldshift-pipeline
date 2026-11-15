# Data card — vegetacion

Paquete `vegetacion` de Field Shift (CLAUDE.md §6.3): MODIS por condado del Corn Belt.

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| vegetacion_16d.csv | ndvi | NDVI medio del condado (compuesto de 16 días; fecha = inicio del compuesto) | adim. | MODIS MOD13Q1 v061 (Planetary Computer) | M01 | 2000-02-18 | 2025-12-19 | 4.9 |
| vegetacion_16d.csv | evi | EVI medio del condado | adim. | MODIS MOD13Q1 v061 (Planetary Computer) | M02 | 2000-02-18 | 2025-12-19 | 4.9 |
| vegetacion_16d.csv | ndvi_maiz | NDVI medio de los píxeles con >= 75 % de maíz (CDL del año) | adim. | MODIS MOD13Q1 v061 (Planetary Computer) | M01 | 2008-01-01 | 2025-12-19 | 43.4 |
| vegetacion_16d.csv | ndvi_soja | NDVI medio de los píxeles con >= 75 % de soja (CDL del año) | adim. | MODIS MOD13Q1 v061 (Planetary Computer) | M01 | 2008-01-01 | 2025-12-19 | 43.7 |
| vegetacion_16d.csv | frac_pixeles_validos | Píxeles que pasan el filtro de calidad sobre los píxeles del condado | 0-1 | MODIS MOD13Q1 v061 (Planetary Computer) | M03 | 2000-02-18 | 2025-12-19 | 0.0 |
| vegetacion_mensual.csv | ndvi | Media de los compuestos de 16 días que empiezan en el mes | adim. | MODIS MOD13Q1 v061 (Planetary Computer) | M01 | 2000-02 | 2025-12 | 2.2 |
| vegetacion_mensual.csv | evi | Media de los compuestos de 16 días que empiezan en el mes | adim. | MODIS MOD13Q1 v061 (Planetary Computer) | M02 | 2000-02 | 2025-12 | 2.2 |
| vegetacion_mensual.csv | ndvi_maiz | Media mensual del NDVI de maíz (CDL >= 75 %) | adim. | MODIS MOD13Q1 v061 (Planetary Computer) | M01 | 2008-01 | 2025-12 | 40.7 |
| vegetacion_mensual.csv | ndvi_soja | Media mensual del NDVI de soja (CDL >= 75 %) | adim. | MODIS MOD13Q1 v061 (Planetary Computer) | M01 | 2008-01 | 2025-12 | 41.0 |
| vegetacion_mensual.csv | lst_dia_c | LST diurna media (compuestos de 8 días que empiezan en el mes) | °C | MODIS MOD11A2 v061 (Planetary Computer) | M04 | 2000-02 | 2025-12 | 0.0 |
| vegetacion_mensual.csv | lst_noche_c | LST nocturna media | °C | MODIS MOD11A2 v061 (Planetary Computer) | M05 | 2000-02 | 2025-12 | 0.0 |
| vegetacion_mensual.csv | et_mm | ET real total del mes (Evap de NLDAS-2 Noah, media ponderada del condado) | mm | NLDAS-2 Noah mensual v2.0 (NASA GES DISC, sustituye a MOD16A2) | M06 | 2000-02 | 2025-12 | 0.0 |
| vegetacion_mensual.csv | pet_mm | ET potencial total del mes (PotEvap de NLDAS-2 Noah, W m-2 × 86400 × días / 2,501e6) | mm | NLDAS-2 Noah mensual v2.0 (NASA GES DISC, sustituye a MOD16A2) | M07 | 2000-02 | 2025-12 | 0.0 |
| vegetacion_mensual.csv | et_pet_ratio | et_mm / pet_mm | adim. | NLDAS-2 Noah mensual v2.0 (NASA GES DISC, sustituye a MOD16A2) |  | 2000-02 | 2025-12 | 0.0 |
| vegetacion_mensual.csv | ndvi_anom_z | (ndvi − media del mes calendario) / desvío, por condado, todos los años | adim. | Derivada de MOD13Q1 | F10 | 2000-02 | 2025-12 | 2.2 |
| vegetacion_mensual.csv | vci | VCI = 100 (ndvi − mín) / (máx − mín) del mes calendario, por condado | 0-100 | Derivada de MOD13Q1 | F11 | 2000-02 | 2025-12 | 2.2 |
| vegetacion_mensual.csv | tci | TCI = 100 (máx − lst_dia_c) / (máx − mín) del mes calendario, por condado | 0-100 | Derivada de MOD11A2 + MOD13Q1 | F12 | 2000-02 | 2025-12 | 0.0 |
| vegetacion_mensual.csv | vhi | VHI = 0,5 VCI + 0,5 TCI | 0-100 | Derivada de MOD11A2 + MOD13Q1 | F13 | 2000-02 | 2025-12 | 2.3 |
| fenologia_anual.csv | doy_inicio | Día del año en que el NDVI suavizado sube al 50 % de la amplitud del año | DOY | Derivada de MOD13Q1 | F01 | 2000 | 2025 | 2.0 |
| fenologia_anual.csv | doy_pico | Día del año del máximo NDVI suavizado (inicio del compuesto + 8 días) | DOY | Derivada de MOD13Q1 | F02 | 2000 | 2025 | 2.0 |
| fenologia_anual.csv | doy_fin | Día del año en que el NDVI suavizado baja al 50 % de la amplitud | DOY | Derivada de MOD13Q1 | F04 | 2000 | 2025 | 2.1 |
| fenologia_anual.csv | ndvi_max | Máximo del NDVI suavizado del año | adim. | Derivada de MOD13Q1 | F03 | 2000 | 2025 | 2.0 |
| fenologia_anual.csv | duracion_dias | doy_fin − doy_inicio | días | Derivada de MOD13Q1 | F05 | 2000 | 2025 | 2.1 |
| fenologia_anual.csv | ndvi_integral | Integral del NDVI suavizado entre doy_inicio y doy_fin | NDVI·día | Derivada de MOD13Q1 | F06 | 2000 | 2025 | 2.1 |
| fenologia_anual.csv | n_ciclos | Picos del NDVI suavizado con prominencia >= 0,1 | n | Derivada de MOD13Q1 | F07 | 2000 | 2025 | 2.0 |
| fenologia_anual.csv | ndvi_max_maiz | Máximo NDVI de maíz del año (compuestos de 16 días) | adim. | Derivada de MOD13Q1 | F03 | 2008 | 2025 | 38.5 |
| fenologia_anual.csv | ndvi_max_soja | Máximo NDVI de soja del año (compuestos de 16 días) | adim. | Derivada de MOD13Q1 | F03 | 2008 | 2025 | 38.6 |
| fenologia_anual.csv | dias_ndvi_lt03_invierno | Días con NDVI diario interpolado < 0,3 entre 1-nov (anio−1) y 31-mar | días | Derivada de MOD13Q1 | F09 | 2001 | 2025 | 3.8 |

## Fuentes y acceso

- **DOI de los productos de la NASA:**
  - MOD13Q1 V061: https://doi.org/10.5067/MODIS/MOD13Q1.061
  - MOD11A2 V061: https://doi.org/10.5067/MODIS/MOD11A2.061
  - NLDAS-2 Noah mensual V2.0 (`NLDAS_NOAH0125_M`, para `et_mm`, `pet_mm` y `et_pet_ratio`):
    https://doi.org/10.5067/WB224IA3PVOJ
- Citas completas: `docs/research/citas_nasa.md`.

- **MOD13Q1 v061** (Terra, índices de vegetación 16 días, 250 m) y **MOD11A2 v061** (Terra, LST 8 días,
  1 km), COGs públicos de Microsoft Planetary Computer (colecciones `modis-13Q1-061` y
  `modis-11A2-061`), firmados con el token SAS anónimo. Teselas h10v04, h10v05, h11v04, h11v05.
- `src/vegetacion/download.py` lee solo la ventana de cada tesela que cubre los condados y la guarda
  tal cual en `data/raw/vegetacion/<producto>/<anio>/<item>.tif` (una fila por archivo en `manifest.csv`).
- `src/vegetacion/process.py` rasteriza los condados en la grilla sinusoidal de cada tesela, filtra
  calidad y promedia por condado (suma de todas las teselas que tocan el condado).
- **NLDAS-2 Noah mensual v2.0** (`NLDAS_NOAH0125_M`, NASA GES DISC, 0,125°, CMR
  `C1887990023-GES_DISC`), variables `Evap` (kg m-2, suma del mes) y `PotEvap` (W m-2, media del mes),
  recortadas al rectángulo de los condados con Harmony (`harmony.earthdata.nasa.gov`, login Earthdata).
  `src/vegetacion/download_nldas.py` guarda un NetCDF por mes en `data/raw/vegetacion/nldas_noah_m/<anio>/`.

## Supuestos

- Sin credencial de Earthdata no se usó AppEEARS: se usaron los mismos productos v061 desde
  Planetary Computer (acceso público sin login).
- **Resolución reducida.** La tesela completa a 250 m baja a ~1 MB/s y el período completo pasaría de
  5 GB, así que MOD13Q1 se lee del overview 1 del COG (factor 4, ~927 m) y MOD11A2 del overview 0
  (factor 2, ~2 km). Los overviews los genera Planetary Computer remuestreando la banda (no es
  vecino más cercano): la media del condado es comparable, pero el filtro de calidad es aproximado.
- **Filtro de calidad MOD13Q1:** NDVI y EVI dentro del rango válido (−2000 a 10000), pixel reliability
  remuestreado igual a 0 (bueno) o 1 (marginal), y el píxel no toca (vecindad 3x3) ningún píxel sin
  dato o fuera de rango (los bordes del remuestreo dejan artefactos). `frac_pixeles_validos` es la
  fracción de píxeles del condado que pasan el filtro.
- **Filtro de calidad MOD11A2:** LST día y noche >= 7500 (valid_range, escala 0,02 K) en el mismo
  píxel, con la misma erosión 3x3. No se bajaron las bandas QC (en el overview no son interpretables).
- `ndvi`/`evi` son la media de todo el condado (no se aplicó `mascara_agricola.tif`).
- **NDVI de maíz y soja** (desde 2008): con `data/reference/mascara_<cultivo>_<anio>.tif` (CDL, 30 m,
  EPSG:5070) se calcula la fracción exacta del cultivo en bloques de 8x8 (240 m) y se reproyecta con
  promedio a la grilla MODIS de cada tesela. Un píxel MODIS cuenta si >= 75 % de su área es del
  cultivo de ese año (umbral pedido para 250 m, aplicado al píxel del overview de ~927 m). Cache en
  `data/interim/vegetacion/frac_cultivos/` (se regenera si falta).
- `ndvi_max_maiz`/`ndvi_max_soja`: máximo de los compuestos del año que pasan el filtro (sin
  suavizar), solo si hay >= 10 compuestos con dato en el año.
- `anio` es el año calendario de la fecha (16d) o del mes (mensual). La fecha del compuesto es su
  primer día. En el mensual, cada compuesto se asigna al mes de su primer día.
- Anomalía z, VCI y TCI usan como referencia todos los años disponibles del mismo condado y mes.
- Fenología: serie de 16 días del año calendario, huecos interpolados linealmente, Savitzky-Golay
  (ventana 5, orden 2); inicio y fin = cruce del 50 % de la amplitud (mín. a máx. del año) antes y
  después del pico; se exige >= 15 compuestos válidos en el año. `n_ciclos` = picos con prominencia
  >= 0,1. `dias_ndvi_lt03_invierno`: NDVI diario interpolado entre compuestos (centro = inicio + 8 d),
  umbral 0,3, solo si la serie cubre todo el invierno previo.
- Umbral para NDVI de maíz/soja (cuando se calcule): un píxel cuenta si >= 75 % de su área es del
  cultivo según la máscara del CDL de ese año.
- **ET y PET de NLDAS-2 Noah en lugar de MOD16A2 (sustitución de fuente).** MOD16A2 (8 días, 500 m)
  no está en Planetary Computer, a 500 m el período completo no entra en el límite de 5 GB del paquete
  (que ya usa ~4,7 GB) y el OPeNDAP de GES DISC está retirado (410). NLDAS-2 es un modelo de superficie
  (Noah) forzado con observaciones, no una estimación satelital: `et_mm` es la ET total simulada y
  `pet_mm` la evaporación potencial de Noah (Penman, típicamente más alta que la PET de MOD16, por eso
  `et_pet_ratio` es más bajo que con MOD16). No mezclar con valores de MOD16A2. Resolución 0,125°
  (~12 km): la media del condado pondera cada celda por su fracción dentro del condado (supermuestreo
  10x de la grilla); se exige que >= 50 % del área del condado tenga dato. Conversión de PET:
  mm/mes = W m-2 × 86400 × días del mes / 2,501e6 J/kg. Media de todo el condado (sin máscara agrícola).
  `anio` = año calendario del mes. Se bajaron 2000–2025 (el contrato pide ET desde 2001).
  Ojo: el paquete `nldas` (si se arma) entrega `et_nldas_mm` del mismo modelo; en la tabla unida las dos
  columnas serían redundantes (no usar ambas como variables independientes en ML).

## Cobertura de ndvi_maiz y ndvi_soja por estado

Viene del QA de OH, NE y MN (`docs/qa/oh_ne_mn.md`, T073, problema 3). `ndvi_maiz` y `ndvi_soja` tienen
muchos más faltantes en OH (maíz) y en la soja de los tres estados nuevos que en IA/IL/IN.

**% de faltantes por columna (todo el período 2000–2025, incluye los 8 años sin CDL):**

| archivo | columna | IA/IL/IN | OH | NE | MN |
|---|---|---|---|---|---|
| vegetacion_16d.csv | ndvi_maiz | 43,4 | 70,0 | 43,9 | 61,8 |
| vegetacion_16d.csv | ndvi_soja | 43,7 | 63,2 | 63,2 | 63,2 |
| vegetacion_mensual.csv | ndvi_maiz | 40,7 | 68,2 | 42,7 | 59,7 |
| vegetacion_mensual.csv | ndvi_soja | 41,0 | 61,6 | 62,1 | 61,0 |
| fenologia_anual.csv | ndvi_max_maiz | 38,5 | 66,4 | 40,2 | 51,6 |
| fenologia_anual.csv | ndvi_max_soja | 38,6 | 59,7 | 60,1 | 52,5 |

**% de condado-fechas con dato, 2008–2025 (rango entre años, `vegetacion_16d.csv`):**

| estado | ndvi_maiz | ndvi_soja |
|---|---|---|
| OH | 30–49 | 41–66 |
| NE | 73–88 | 41–66 |
| MN | 47–69 | 41–66 |

**OH, NE y MN, año por año** (% de condado-fechas de `vegetacion_16d.csv` con dato, calculado por max-1 con
`scripts/cobertura_ndvi_cultivo.py` sobre `datos-oh-ne-mn` corregido el 2026-11-15, con enero–abril de 2014
completos; OH 88, NE 93 y MN 87 condados):

| año | maíz OH | maíz NE | maíz MN | soja OH | soja NE | soja MN |
|---|---|---|---|---|---|---|
| 2008 | 30 | 74 | 51 | 50 | 46 | 51 |
| 2009 | 42 | 82 | 50 | 51 | 51 | 50 |
| 2010 | 36 | 73 | 47 | 47 | 41 | 47 |
| 2011 | 42 | 83 | 54 | 47 | 43 | 50 |
| 2012 | 49 | 84 | 67 | 51 | 52 | 57 |
| 2013 | 46 | 84 | 53 | 50 | 46 | 43 |
| 2014 | 42 | 81 | 45 | 51 | 54 | 46 |
| 2015 | 46 | 81 | 56 | 52 | 58 | 56 |
| 2016 | 48 | 82 | 55 | 60 | 52 | 54 |
| 2017 | 49 | 88 | 62 | 60 | 64 | 60 |
| 2018 | 44 | 84 | 53 | 54 | 57 | 49 |
| 2019 | 39 | 82 | 47 | 51 | 52 | 46 |
| 2020 | 48 | 84 | 57 | 59 | 55 | 57 |
| 2021 | 46 | 82 | 58 | 55 | 59 | 62 |
| 2022 | 45 | 86 | 58 | 57 | 64 | 56 |
| 2023 | 49 | 80 | 57 | 56 | 62 | 55 |
| 2024 | 44 | 82 | 69 | 59 | 56 | 66 |
| 2025 | 41 | 86 | 62 | 52 | 58 | 58 |

Fechas de 16 días por año: 23, salvo 2000 (20, MOD13Q1 empieza el 18-2-2000), 2023 (22), 2024 (21) y 2025
(15). Pasa igual en IA/IL/IN: son fechas que no devuelve la búsqueda de Planetary Computer (se investiga en
T090). Hasta el 2026-11-15 el release `datos-oh-ne-mn` tampoco tenía enero–abril de 2014 (la descarga retomada
arrancó en 2015); el zip de vegetación se republicó corregido ese día.

Para recalcularla en otra máquina que tenga el CSV:

```
.venv/bin/python -X utf8 scripts/cobertura_ndvi_cultivo.py
```

**Referencia para comparar: IA, IL e IN, año por año.** % de condado-fechas de `vegetacion_16d.csv` con
dato, 2008–2025, misma cuenta que hace el script. Sale de la entrega v1.3 (IA 99, IL 102 e IN 92 condados).
Con esta tabla se ve la distancia con los rangos de OH, NE y MN de arriba: IA e IL quedan entre 73 y 95 % en
maíz y entre 66 y 94 % en soja; IN, con lotes más chicos, ya baja a 65–82 % y 58–86 %.

| año | maíz IA | maíz IL | maíz IN | soja IA | soja IL | soja IN |
|---|---|---|---|---|---|---|
| 2008 | 73 | 83 | 71 | 66 | 79 | 72 |
| 2009 | 81 | 78 | 69 | 73 | 82 | 69 |
| 2010 | 75 | 78 | 65 | 71 | 79 | 58 |
| 2011 | 90 | 87 | 75 | 84 | 82 | 72 |
| 2012 | 90 | 88 | 80 | 84 | 87 | 74 |
| 2013 | 91 | 84 | 76 | 85 | 83 | 70 |
| 2014 | 86 | 81 | 68 | 81 | 82 | 65 |
| 2015 | 89 | 84 | 72 | 80 | 84 | 75 |
| 2016 | 83 | 86 | 81 | 82 | 92 | 78 |
| 2017 | 95 | 89 | 74 | 90 | 94 | 83 |
| 2018 | 90 | 86 | 75 | 88 | 94 | 78 |
| 2019 | 86 | 82 | 69 | 80 | 89 | 78 |
| 2020 | 87 | 86 | 82 | 87 | 92 | 80 |
| 2021 | 86 | 86 | 75 | 80 | 90 | 83 |
| 2022 | 85 | 84 | 76 | 86 | 89 | 76 |
| 2023 | 91 | 87 | 82 | 85 | 89 | 86 |
| 2024 | 93 | 87 | 80 | 92 | 92 | 81 |
| 2025 | 92 | 85 | 74 | 85 | 88 | 80 |

**Por qué pasa.** Un píxel MODIS cuenta para `ndvi_maiz` o `ndvi_soja` si al menos el 75 % de su área es de
ese cultivo según el CDL del año (ver Supuestos). Como MOD13Q1 se lee del overview de ~927 m y no del
original de 250 m, cada píxel abarca unas 86 ha: para que cuente hacen falta unas 64 ha seguidas del mismo
cultivo dentro del píxel. Pasa lo siguiente:

- **OH:** lotes más chicos y más mezclados con monte, pasturas y zonas urbanas. Pocos píxeles llegan al 75 %
  de maíz (no se midió en qué zonas del estado se pierden más).
- **Soja en el oeste (NE, MN y también OH):** la soja ocupa menos superficie que el maíz en NE y el oeste de
  MN, y comparte el paisaje con maíz, trigo y pasturas. Hay menos píxeles puros de soja que de maíz.
- **2000–2007:** siempre vacíos (no hay CDL nacional). Son 8 de los 26 años, cerca del 31 % de las filas.

No es un error: es el efecto del umbral documentado. Pero el modelo va a tener mucho menos `ndvi_maiz`
en OH que en IA. Si se usa el NDVI por cultivo como variable, conviene filtrar o ponderar por estado.

**Propuesta, sin aplicar: umbral del 50 %.** No se pudo medir cuántos condado-fechas se ganarían:
esta máquina no tiene las máscaras del CDL de OH, NE ni MN (`data/reference/mascara_<cultivo>_<anio>.tif`)
ni los compuestos de MOD13Q1 de esos estados. Para medirlo, en la máquina que tenga esos datos:

```
.venv/bin/python -X utf8 scripts/cobertura_ndvi_cultivo.py --umbral 0.5 [--anios 2012,2020]
```

El script usa la misma grilla, el mismo filtro de calidad y la misma fracción del CDL que
`src/vegetacion/process.py`. Cuenta, por estado y año, los condado-fechas con al menos un píxel válido
con fracción ≥ 0,75 y ≥ 0,50, y la diferencia (`*_ganados`). La columna `*_075` tiene que dar lo mismo que
el CSV procesado; si da distinto, el script tiene un error. Si se aprueba, lo prudente es entregar el NDVI
al 50 % **en columnas aparte** (por ejemplo `ndvi_maiz_p50`, `ndvi_soja_p50`), sin reemplazar las
actuales: con 50 % la señal mezcla más de otros cultivos. Agregar columnas cambia el esquema: lo decide
el humano.

## Problemas conocidos

- NDVI de maíz/soja vacío en condados sin píxeles de ~927 m con >= 75 % del cultivo (zonas de
  lotes chicos o mezclados).
- Invierno: nieve y nubes dejan meses sin píxeles que pasen el filtro (faltantes en `ndvi`, `lst_*`).
- La regla `lst_noche_c <= lst_dia_c` falla en < 0,1 % de las filas (meses de invierno con pocos
  compuestos válidos); los valores se dejan como vienen.
- `et_mm`, `pet_mm` y `et_pet_ratio` no son MOD16A2 sino NLDAS-2 Noah (ver Supuestos). Para tener
  MOD16A2 hace falta AppEEARS (Earthdata) y liberar espacio: a 500 m no entra en 5 GB. Rutas probadas
  para MOD16A2: Planetary Computer (solo MOD16A3GF anual) y el MODIS Web Service de ORNL DAAC
  (`modis.ornl.gov/rst/api/v1`, ~57 s por pedido de 10 fechas y por punto, errores 502: inviable).
- NLDAS trae valores fuera del rango del contrato en muy pocas filas y se dejan como vienen: ET y PET
  apenas negativas (hasta −0,5 mm) en enero de 2006 en el noroeste de Iowa (condensación/escarcha neta
  en el modelo) y PET > 500 mm en julio de 2012 (sequía) en 5 condados. `et_pet_ratio` queda vacío
  cuando `pet_mm` <= 1 mm.- MCD12Q1 no se bajó (la máscara agrícola del CDL ya existe).
- 2025 incompleto en origen: Planetary Computer no tiene los compuestos de mediados de 2025
  (MOD13Q1 entre A2025193 y A2025305; MOD11A2 entre A2025185 y A2025321; revisado el 2026-11-14).
  Todos los demás compuestos que lista el STAC para la zona están bajados.
