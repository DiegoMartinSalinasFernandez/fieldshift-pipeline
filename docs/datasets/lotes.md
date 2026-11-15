# Data card — lotes (datos por píxel de 30 m en 10 lotes de demostración)

Pedido del equipo de ML (CLAUDE.md §6.6, aprobado por el humano el 2026-11-14). Entrega aparte
(`fieldshift_lotes_v1`): no entra en `tabla_anual.csv` ni en `tabla_mensual.csv`.

Scripts: `src/lotes/download.py` (descargas) y `src/lotes/process.py` (regenera todos los CSV, el
GeoPackage y la tabla de abajo desde `data/raw` y `data/reference`, sin bajar nada).

## Fuentes

- **USDA NASS Crop Sequence Boundaries (CSB), ventana 2018-2025, rev23**: `NationalCSB_2018-2025_rev23.zip`
  (file geodatabase nacional, 3,76 GB). Se baja a `data/interim/lotes/csb/` (caché) y se extraen los polígonos
  de los condados candidatos a `data/raw/lotes/csb/csb_2018-2025_<fips>.gpkg`, con todas sus columnas y en
  EPSG:5070.
- **USDA NASS Cropland Data Layer**: las teselas de 30 m ya bajadas por el paquete `cultivos`
  (`data/raw/cultivos/cdl/teselas/`, 2008-2025).
- **NASA NASADEM** 1": las teselas ya bajadas por `suelo_terreno` (`data/raw/suelo_terreno/nasadem/`).
- **USGS 3DEP** (bare earth, ImageServer `3DEPElevation`): recortes de 10 m por lote en `data/raw/lotes/3dep/`.
- **AgTile-US** (Valayamkunnath et al. 2020): `data/raw/lotes/agtile/AgTile-US-TIFF.zip` (figshare, CC BY 4.0).
- **SEETileDrain** (Wan, Kendall, Rapp y Hyndman 2024, *Sci. Total Environ.*, DOI 10.1016/j.scitotenv.2024.175283;
  T131, pendiente del OK de `para_decidir.md` #5): `SEETileDrain_maps.zip` de HydroShare (DOI
  10.4211/hs.4c8af0c89d2b4686808bcf9c6f7c0da3, 3.119.442.255 bytes, MD5 `0200fe57a8540d89118dbfc935a65bc9`),
  **CC BY 4.0** (citar a los autores y el DOI de HydroShare). Recortes por lote en
  `data/raw/lotes/seetiledrain/{prob,clase}_<id_lote>.tif` con `src/lotes/drenaje.py` (o
  `python src/lotes/download.py seetiledrain`; `seetiledrain_zip` baja antes el zip entero).
- **HLS S30 v2.0 2015-2019**: NASA LP DAAC (CMR-STAC `LPCLOUD`, Earthdata), mismos recortes que los de Planetary Computer.
- **Censo Agropecuario (riego)**: `data/processed/cultivos/practicas_censo.csv`, censo 2022.

## Selección de lotes (regla determinística)

1. Polígonos del CSB 2018-2025 de los condados candidatos.
2. Filtros: superficie 30-120 ha (geometría en EPSG:5070); compacidad de Polsby-Popper (4πA/P²) ≥ 0,6;
   maíz (1) o soja (5) en al menos 6 de las 8 columnas `CDL2018`-`CDL2025` del CSB; `pct_riego` del censo 2022
   del condado < 5 %; al menos 300 píxeles interiores; en depresiones y lomas, relieve NASADEM > 3 m.
3. Orden dentro de cada paisaje: depresiones (Story 19169, Hamilton 19079) y lomas (Crawford 19047,
   Shelby 19165) por relieve más cercano a la mediana de los candidatos del paisaje (lote típico; el máximo
   elegía lotes cortados por barrancas de arroyos); control (Champaign 17019) por menor relieve; Indiana (Tippecanoe 18157)
   por mayor compacidad. Empates por `CSBID`. Se toman los primeros 3, 3, 2 y 2.
4. `n_candidatos` = polígonos que cumplían todos los filtros en el paisaje; `motivo` = regla y puesto.

## Supuestos

- **Wright (19197) queda afuera de los candidatos**: no tiene `pct_riego` en el censo 2022 (celda vacía en
  `practicas_censo.csv`), así que no se puede verificar el criterio de riego.
- **Condado de Indiana: Tippecanoe (18157)**, llanura de till del centro-norte con maíz-soja y riego 3,65 %
  (censo 2022). Elegido a mano: el plan deja el condado a elección.
- **Umbral de compacidad 0,6 (Polsby-Popper)** para "forma compacta": el plan no fija un número.
- **CSB por zip nacional y no por GeoParquet**: el GeoParquet de Source Cooperative (`fiboa/us-usda-cropland`)
  es la ventana 2016-2023, con polígonos fusionados por el cultivo de 2023 y sin las columnas `CDL<año>`; la
  ventana más reciente publicada es 2018-2025 y solo está en el zip nacional de NASS (sin archivos por estado).
  El zip queda en `data/interim/lotes/csb/` (caché) y a raw van solo los polígonos de los condados candidatos.
- **Relieve (`relieve_m`)**: NASADEM muestreado con interpolación bilineal en los centros de píxel de 30 m del
  lote (EPSG:5070 → 4326), máxima menos mínima.
- **Píxeles**: centros de la grilla de `mascara_agricola.tif` (múltiplos de 30 m en EPSG:5070) que caen dentro
  del polígono; `interior` = centro dentro del polígono achicado 30 m; `px_id` = fila × n_columnas + columna en
  el recuadro de centros del lote (filas de norte a sur); `frac_en_lote` = área del cuadrado de 30 m dentro del
  polígono / 900 m².
- **Cultivo por píxel**: clase de la tesela del CDL de 30 m que contiene el centro. Clase 0 (background) va
  vacía. Grupos según `data/reference/clases_cdl.csv`. `cultivo_principal` = grupo más frecuente entre los
  píxeles interiores (empates por orden alfabético); `cdl_clase_principal` = clase más frecuente dentro de ese
  grupo; `pct_px_cultivo_principal` = % de píxeles interiores con ese grupo; `lote_partido` = 1 si es < 90.
- **Terreno (NASADEM)**: se lee de `data/raw/suelo_terreno/nasadem/` (registrado en el manifest por
  `suelo_terreno`). Ventana del lote + 2,5 km en la grilla original (1", EPSG:4326; dx = 30,9 m × cos(lat)).
  NASADEM viene en metros enteros, así que las derivadas se calculan sobre el DEM suavizado con un filtro
  gaussiano de sigma = 1 celda (~30 m); `elevacion_m` es el DEM sin suavizar. Pendiente y curvaturas con
  diferencias centrales (curvaturas de Zevenbergen y Thorne, 1/m); aspecto = dirección de máxima bajada,
  remuestreado por sus componentes seno y coseno; TPI = elevación − media de las celdas a ≤ 90 m y ≤ 300 m;
  `prof_depresion_m` = DEM suavizado relleno (priority-flood, Barnes 2014) − DEM suavizado; TWI = ln(a / tan β)
  con a = área aportante D8 (sobre el relleno con épsilon 1e-5 m) / ancho de celda y tan β ≥ 0,001. Después,
  interpolación bilineal a los centros de 30 m.
- **2024-2025 (CDL de 10 m)**: `data/raw/lotes/cdl10m/cdl10m_<anio>_<id_lote>.tif`, exportados del ImageServer
  `CDL_WM` de CroplandCROS (raster fijo de 10 m de cada año, vecino más cercano a 10 m, recuadro alineado con los
  bordes de la grilla de 30 m más 30 m de margen). Cada píxel de 30 m es un bloque de 3 × 3 celdas de 10 m:
  `cdl_clase` = clase más frecuente (empates: código más bajo) y `frac_clase` = celdas de esa clase / 9. Antes de
  2024 `frac_clase` queda vacía (el CDL es nativo de 30 m).
- **Grupos del CSB**: `cultivo_csb` traduce la columna `CDL<anio>` del polígono con `clases_cdl.csv`;
  `pct_px_igual_csb` = % de píxeles interiores cuya clase CDL (2024-2025: la de 10 m) es igual a la del CSB.

- **Landsat C2 L2 y HLS S30 por Planetary Computer (sin login)**: STAC `landsat-c2-l2` y `hls2-s30`, escenas
  del 1 de marzo al 30 de noviembre con `eo:cloud_cover` < 80 % (las de más nubes casi nunca dejan píxeles
  despejados en un lote de 50 ha; documentado como recorte de la descarga) que contienen el centroide del lote.
  Por escena se lee la ventana de origen de cada banda (UTM, 2 px de margen) y se reproyecta por vecino más cercano
  al recuadro del lote en la grilla de 30 m (EPSG:5070) + 1 píxel; se guarda el DN uint16 tal cual en
  `data/raw/lotes/<landsat|hls_s30>/<anio>/<id>.npz`. Landsat 4 no se usa (el contrato no lo lista).
- **QA Landsat**: igual que `teledeteccion`: se descartan píxeles con QA_PIXEL de relleno, nube dilatada, cirro,
  nube, sombra, nieve o agua, sin el bit de despejado, o con alguna banda fuera de DN 7273–43636. Reflectancia =
  DN × 0,0000275 − 0,2. **QA HLS**: Fmask con los bits 0–5 en cero (cirro, nube, adyacente, sombra, nieve, agua) y
  distinto de 255; reflectancia = DN × 0,0001 con DN entre 1 y 16000. Los valores negativos de HLS (int16) quedan
  en 0 al pasar a uint16 y se descartan como relleno.
- **Escenas repetidas**: si dos escenas de la misma pasada (filas WRS-2 o teselas MGRS solapadas) dan el mismo
  píxel, fecha y sensor, queda la primera en orden (T1 antes que T2, después por id).
- **vegetacion_px_anual.csv**: una fila por píxel y año con al menos una escena Landsat bajada que cubre el lote;
  `n_obs_*` cuentan observaciones despejadas entre las escenas bajadas. `doy_*_max`: el primero si hay empate.
  `ndvi_max_s2` y `n_obs_jul_ago_s2` desde HLS S30 (años con escenas HLS bajadas).
- **Suelo desnudo**: observaciones Landsat con NDVI < 0,25 del 15 de marzo al 15 de mayo y de octubre-noviembre;
  mediana por banda y NBR2 calculado con las medianas de swir1 y swir2. El compuesto multianual usa **todos los
  años** y ambas ventanas juntas.
- **SSURGO por Soil Data Access**: polígonos `mupolygon` que cortan el recuadro del lote + 60 m, recortados en
  origen (`STIntersection`); rasterizados a 10 m en una grilla alineada con la de 30 m (3 × 3 subceldas por píxel,
  centro de subcelda dentro del polígono). `frac_mukey` = subceldas del mukey / 9. Atributos con los mismos
  cálculos que `suelo_terreno` (0–30 cm por espesor, componente → mukey por `comppct_r`; aws = muaggatt × 10, en mm,
  porque SDA no tiene Valu1). `pendiente_dcd_pct` = `slopegraddcp` (`slopegraddcd` no existe en SDA);
  `pendiente_comp_pct` = `slopegradwta`; `clase_erosion` = `erocl` del componente dominante ("None - deposition" →
  "nula - deposition"). NCCPI de maíz y soja: los submodelos están en `ruledepth` > 0
  (`nccpi_submodelos.csv`).
- **Clima del lote**: POWER diario (comunidad AG) en el centroide del lote, desde 1999-11 para el invierno previo
  de 2000; IMERG Final diario vía el parámetro `IMERG_PRECTOT` de la misma API (sin Earthdata, como en `clima`),
  desde 2000-06. SMAP L4 diario (`SUB` = zona radicular, `TOP` = superficie) leído de los GeoTIFF de 9 km de
  Crop-CASMA que bajó el paquete `agua` (registrados por ese paquete en el manifest), celda que contiene el
  centroide; `sm_rootzone_temporada_m3m3` = media abril-septiembre con al menos 150 días. ETo FAO-56 y GDD 10/30
  con las funciones de `src/clima`. Totales mensuales y de temporada solo
  con todos los días presentes.
- **USGS 3DEP (extra aprobado, no es de la NASA)**: `exportImage` del ImageServer público `3DEPElevation` de The
  National Map (mosaico dinámico bare earth: lidar de 1 m donde existe, si no 1/3"), pedido a **10 m** en EPSG:5070
  con interpolación bilineal, recuadro del lote alineado con los bordes de la grilla de 30 m más **2.520 m** de margen
  (ventana ≥ 2 km para el TWI) → `data/raw/lotes/3dep/3dep_10m_<id_lote>.tif`. Se pidió 10 m y no 1 m para que la
  ventana de 5-6 km entre en un pedido y el priority-flood en Python tarde ~2 s por lote; el detalle submétrico del
  lidar se pierde. Las derivadas se calculan en la grilla de 10 m con el mismo método que NASADEM (gauss sigma 1
  celda = 10 m para la pendiente, el TPI, el relleno y el TWI; elevación sin suavizar) y cada columna `_3dep` es la
  **media de las 3 × 3 celdas de 10 m** del píxel de 30 m. `relieve_3dep_m` = máxima menos mínima de
  `elevacion_3dep_m` en los píxeles del lote.
- **Drenaje con caños**: AgTile-US (Valayamkunnath et al. 2020, Scientific Data 7:257; figshare
  10.6084/m9.figshare.11825742, CC BY 4.0), GeoTIFF binario de 30 m leído dentro del zip tal cual se bajó
  (`data/raw/lotes/agtile/AgTile-US-TIFF.zip`). Su Albers tiene `lat_0` = 37,5 (no 23 como EPSG:5070) y la grilla
  está corrida ~11 m en x y ~8 m en y respecto de la nuestra: `drenado_canos` es el valor de la celda AgTile que
  contiene el centro del píxel (vecino más cercano, sin fracción). Es un mapa modelado a partir de suelo, pendiente
  y uso agrícola (no una observación del lote): sirve como indicio, no como verdad de campo.
- **SEETileDrain** (T131): el zip trae `probability_tile_mosaic.tif` (probabilidad, float, 0-1) y
  `SEETileDrain.tif` (clase publicada, int32, 0/1), los dos en **EPSG:4326** con celda de 0,000269495° (la "30 m" de Google
  Earth Engine: ~30 m norte-sur y ~22 m este-oeste a 42° N), 93.431 × 41.466
  celdas, en tiras de una fila sin compresión interna (~15,5 GB cada uno al descomprimir). Como el zip usa deflate y
  no admite acceso aleatorio, `drenaje.py` infla cada miembro **en flujo** y guarda solo las filas del recuadro de
  cada lote (más ~5 celdas de margen) en la grilla original, **sin remuestrear**: nunca se escribe el TIFF entero.
  Sin el zip local, lo infla pidiendo rangos HTTP a HydroShare y corta en la última fila necesaria (para lotes en
  IA, ~60 % de cada miembro: ~35 MB de la clase y ~1,8 GB de la probabilidad). **Remuestreo**: cada píxel de 30 m
  (centro en EPSG:5070) toma la celda SEETileDrain que contiene su centro (vecino más cercano), igual que
  `drenado_canos` con AgTile-US; no se promedian celdas ni se reproyecta el raster. Como las dos grillas no
  coinciden, una celda SEETileDrain puede repetirse en dos píxeles vecinos o quedar sin usar.
  `tile_prob_seetiledrain` es la probabilidad del random forest (redondeada a 4 decimales; vacía fuera de 0-1 o en
  nodata). `tile_seetiledrain` es la **capa binaria publicada** por los autores, no un umbral nuestro sobre la
  probabilidad; el paper usa 0,5 como corte y los controles de calidad muestran cuánto coincide con
  `prob >= 0,5`. Es una **estimación de modelo de 2017** (una sola fecha), no una observación: los puntos "sin tile"
  del entrenamiento salen de AgTile-US, y a nivel condado sobreestima en los condados muy drenados (Des Moines Lobe,
  donde están 3 lotes) (`docs/research/drenaje_tile.md`). Con la clase, la celda vale 0 también fuera de las zonas
  agrícolas: 0 no prueba "sin caños". La probabilidad es float32 sin etiqueta de nodata y vale NaN fuera de lo
  agrícola (ahí `tile_prob_seetiledrain` queda vacía y `tile_seetiledrain` en 0). En un recuadro de prueba de
  ~1,2 × 1,1 km en Story (IA), las dos capas comparten la grilla y la clase coincide con `prob >= 0,5` en el
  99,75 % de las celdas con probabilidad.
- **HLS S30 2015-2019 desde LP DAAC**: Planetary Computer no tiene `hls2-s30` antes de 2020 en la zona; esos años se
  buscan en CMR-STAC (`LPCLOUD`, colección `HLSS30_2.0`, filtro de nubes < 80 % del lado del cliente) y se leen los
  COG de `data.lpdaac.earthdatacloud.nasa.gov` con Earthdata. Mismo recorte, mismas bandas y mismo Fmask que en PC
  (el producto es el mismo HLS v2.0). Como CMR-STAC no trae la plataforma, se guarda el `SPACECRAFT_NAME` del Fmask
  en el npz (`__plataforma`) para el `sensor` (S2A/S2B).

## Problemas conocidos

- **Descarga de Landsat y HLS parcial**: se baja primero la escena más despejada de cada lote-año, después la
  segunda, etc.; las observaciones, los `n_obs_*` y el suelo desnudo van a crecer en las próximas rondas
  (`python src/lotes/download.py landsat hls`, reanudable).
- 3DEP a 10 m (no 1 m): ver Supuestos. Un lote de control de Champaign (17019_171825005511042) tiene 1,6 m de
  relieve 3DEP (< 2 m) y 4,0 m en NASADEM: el relieve de NASADEM en el llano está inflado por el ruido del DEM de
  radar en metros enteros.
- SMAP L4 sale de las capas diarias de Crop-CASMA del paquete `agua` (ver sus dudas en `loop/notes/decisiones.md`:
  campo de las 01:30 UTC o media diaria), no de `SPL4SMGP`; celdas > 0,60 m³/m³ quedan vacías como en `agua`.
- HLS v2 S30 en Planetary Computer (`hls2-s30`) solo tiene escenas desde 2020 en la zona; 2015-2019 sale de LP
  DAAC (Supuestos) y la descarga de esos años es parcial (primero la escena más despejada de cada lote-año). CMR-STAC
  no tiene escenas S30 de marzo a noviembre de 2015 en el recuadro.
- **SEETileDrain** (T131): columnas nuevas de `drenaje_px.csv` pendientes del OK de `para_decidir.md` #5; hasta que se
  bajen los recortes de los 10 lotes quedan vacías. Una sola fecha (2017) para toda la serie 2000-2025.
- `napa_min_cm` vacío en las unidades sin napa dentro de los 200 cm (`wtdepannmin` nulo en SSURGO).

## Diccionario de columnas

<!-- TABLA:INICIO -->
| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| lotes.csv | paisaje | paisaje del plan (depresiones, lomas_loess, llanura_control, indiana) | adimensional | CLAUDE.md §6.6 |  |  |  | 0.00 |
| lotes.csv | csb_ventana | ventana de 8 años del CSB de donde sale el polígono | adimensional | USDA NASS CSB |  |  |  | 0.00 |
| lotes.csv | area_ha | superficie del polígono (EPSG:5070) | ha | USDA NASS CSB |  |  |  | 0.00 |
| lotes.csv | area_ac | superficie del polígono | ac | USDA NASS CSB |  |  |  | 0.00 |
| lotes.csv | lat_centroide | latitud del centroide | grados | USDA NASS CSB |  |  |  | 0.00 |
| lotes.csv | lon_centroide | longitud del centroide | grados | USDA NASS CSB |  |  |  | 0.00 |
| lotes.csv | compacidad | Polsby-Popper 4πA/P² | adimensional | USDA NASS CSB |  |  |  | 0.00 |
| lotes.csv | n_px | píxeles de 30 m con centro dentro del lote | píxeles | grilla mascara_agricola.tif |  |  |  | 0.00 |
| lotes.csv | n_px_interior | píxeles con centro dentro del lote achicado 30 m | píxeles | grilla mascara_agricola.tif |  |  |  | 0.00 |
| lotes.csv | n_anios_maiz_soja | años de la ventana CSB con maíz o soja (CDL<año> del CSB) | años | USDA NASS CSB |  |  |  | 0.00 |
| lotes.csv | pct_riego_condado | % de tierras de cultivo con riego, censo más reciente | % | USDA NASS Censo (practicas_censo.csv) |  |  |  | 0.00 |
| lotes.csv | relieve_3dep_m | máxima menos mínima de elevacion_3dep_m en los píxeles del lote | m | USGS 3DEP |  |  |  | 0.00 |
| lotes.csv | relieve_m | máxima menos mínima de NASADEM (bilineal en la grilla de 30 m) dentro del lote | m | NASA NASADEM |  |  |  | 0.00 |
| lotes.csv | motivo | regla de selección y puesto | adimensional | este paquete |  |  |  | 0.00 |
| lotes.csv | n_candidatos | polígonos que cumplían todos los criterios en ese paisaje | lotes | USDA NASS CSB |  |  |  | 0.00 |
| pixeles.csv | x_m | x del centro del píxel (EPSG:5070) | m | grilla mascara_agricola.tif |  |  |  | 0.00 |
| pixeles.csv | y_m | y del centro del píxel (EPSG:5070) | m | grilla mascara_agricola.tif |  |  |  | 0.00 |
| pixeles.csv | lon | longitud del centro | grados | grilla mascara_agricola.tif |  |  |  | 0.00 |
| pixeles.csv | lat | latitud del centro | grados | grilla mascara_agricola.tif |  |  |  | 0.00 |
| pixeles.csv | dist_borde_m | distancia del centro al borde del polígono | m | USDA NASS CSB |  |  |  | 0.00 |
| pixeles.csv | interior | 1 si el centro cae en el lote achicado 30 m | adimensional | USDA NASS CSB |  |  |  | 0.00 |
| pixeles.csv | frac_en_lote | fracción del píxel de 30 m dentro del polígono | adimensional | USDA NASS CSB |  |  |  | 0.00 |
| terreno_px.csv | elevacion_m | elevación NASADEM (sin suavizar), bilineal a 30 m | m | NASA NASADEM |  |  |  | 0.00 |
| terreno_px.csv | pendiente_pct | pendiente sobre el DEM suavizado (gauss sigma 1 celda) | % | NASA NASADEM |  |  |  | 0.00 |
| terreno_px.csv | aspecto_grados | dirección de máxima bajada desde el norte, horario; vacío con pendiente 0 | grados | NASA NASADEM |  |  |  | 0.00 |
| terreno_px.csv | curv_plan | curvatura en planta (Zevenbergen y Thorne) | 1/m | NASA NASADEM |  |  |  | 0.00 |
| terreno_px.csv | curv_perfil | curvatura de perfil (Zevenbergen y Thorne) | 1/m | NASA NASADEM |  |  |  | 0.00 |
| terreno_px.csv | tpi_90m_m | elevación menos la media en un radio de 90 m | m | NASA NASADEM |  |  |  | 0.00 |
| terreno_px.csv | tpi_300m_m | elevación menos la media en un radio de 300 m | m | NASA NASADEM |  |  |  | 0.00 |
| terreno_px.csv | twi | ln(área específica aportante / tan pendiente), D8 en ventana lote + 2,5 km | adimensional | NASA NASADEM |  |  |  | 0.00 |
| terreno_px.csv | elevacion_3dep_m | elevación USGS 3DEP (10 m, media de 3 × 3 celdas en el píxel de 30 m) | m | USGS 3DEP |  |  |  | 0.00 |
| terreno_px.csv | pendiente_3dep_pct | pendiente 3DEP a 10 m (gauss sigma 10 m), media en el píxel de 30 m | % | USGS 3DEP |  |  |  | 0.00 |
| terreno_px.csv | tpi_90m_3dep_m | elevación menos la media a <= 90 m, 3DEP 10 m, media en el píxel | m | USGS 3DEP |  |  |  | 0.00 |
| terreno_px.csv | twi_3dep | TWI D8 sobre 3DEP 10 m en ventana lote + 2,52 km, media en el píxel | adimensional | USGS 3DEP |  |  |  | 0.00 |
| terreno_px.csv | prof_depresion_3dep_m | relleno priority-flood menos DEM, 3DEP 10 m, media en el píxel | m | USGS 3DEP |  |  |  | 0.00 |
| terreno_px.csv | prof_depresion_m | DEM con depresiones rellenas (priority-flood) menos DEM | m | NASA NASADEM |  |  |  | 0.00 |
| lotes_anual.csv | cultivo_principal | grupo de cultivo más frecuente en los píxeles interiores | adimensional | USDA NASS CDL |  | 2008 | 2025 | 0.00 |
| lotes_anual.csv | cdl_clase_principal | clase CDL más frecuente dentro del grupo principal | código | USDA NASS CDL |  | 2008 | 2025 | 0.00 |
| lotes_anual.csv | pct_px_cultivo_principal | % de píxeles interiores con el grupo principal | % | USDA NASS CDL |  | 2008 | 2025 | 0.00 |
| lotes_anual.csv | lote_partido | 1 si pct_px_cultivo_principal < 90 | adimensional | USDA NASS CDL |  | 2008 | 2025 | 0.00 |
| lotes_anual.csv | cultivo_csb | grupo del cultivo que el CSB asigna al lote ese año (solo 2018-2025) | adimensional | USDA NASS CSB |  | 2018 | 2025 | 55.56 |
| lotes_anual.csv | pct_px_igual_csb | % de píxeles interiores cuya clase CDL es la del CSB | % | USDA NASS CDL y CSB |  | 2018 | 2025 | 55.56 |
| cultivo_px_anual.csv | cdl_clase | clase CDL del píxel (teselas de 30 m de data/raw/cultivos) | código | USDA NASS CDL |  | 2008 | 2025 | 0.00 |
| cultivo_px_anual.csv | cultivo | grupo de la clase según data/reference/clases_cdl.csv | adimensional | USDA NASS CDL |  | 2008 | 2025 | 0.00 |
| cultivo_px_anual.csv | frac_clase | fracción del píxel con la clase mayoritaria (CDL de 10 m, 2024-2025) | adimensional | USDA NASS CDL 10 m |  | 2024 | 2025 | 88.89 |
| suelo_px.csv | frac_mukey | fracción de las 9 subceldas de 10 m del píxel con ese mukey (polígonos SSURGO rasterizados) | adimensional | USDA NRCS SSURGO (SDA) |  |  |  | 0.00 |
| suelo_mukey.csv | muname | nombre de la unidad cartográfica | adimensional | USDA NRCS SSURGO mapunit |  |  |  | 0.00 |
| suelo_mukey.csv | aws0_100_mm | agua disponible 0-100 cm (aws0100wta × 10) | mm | USDA NRCS SSURGO muaggatt |  |  |  | 1.82 |
| suelo_mukey.csv | aws0_150_mm | agua disponible 0-150 cm (aws0150wta × 10) | mm | USDA NRCS SSURGO muaggatt |  |  |  | 1.82 |
| suelo_mukey.csv | soc0_30_gm2 | carbono orgánico 0-30 cm: Σ espesor · MO · 0,58 · densidad · (1 − fragmentos), media por comppct_r | g C/m² | USDA NRCS SSURGO chorizon |  |  |  | 1.82 |
| suelo_mukey.csv | nccpi_general | NCCPI v3 general, media por comppct_r | adimensional | USDA NRCS SSURGO cointerp |  |  |  | 1.82 |
| suelo_mukey.csv | nccpi_maiz | NCCPI submodelo maíz, media por comppct_r | adimensional | USDA NRCS SSURGO cointerp |  |  |  | 1.82 |
| suelo_mukey.csv | nccpi_soja | NCCPI submodelo soja, media por comppct_r | adimensional | USDA NRCS SSURGO cointerp |  |  |  | 1.82 |
| suelo_mukey.csv | clase_drenaje | clase de drenaje del componente dominante (drclassdcd) | adimensional | USDA NRCS SSURGO muaggatt |  |  |  | 1.82 |
| suelo_mukey.csv | clase_drenaje_mas_humeda | clase de drenaje más húmeda (drclasswettest) | adimensional | USDA NRCS SSURGO muaggatt |  |  |  | 1.82 |
| suelo_mukey.csv | grupo_hidrologico | grupo hidrológico dominante (hydgrpdcd) | adimensional | USDA NRCS SSURGO muaggatt |  |  |  | 1.82 |
| suelo_mukey.csv | pct_componentes_hidricos | % de componentes hídricos (hydclprs) | % | USDA NRCS SSURGO muaggatt |  |  |  | 0.00 |
| suelo_mukey.csv | pct_encharcamiento | % de componentes con encharcamiento (pondfreqprs) | % | USDA NRCS SSURGO muaggatt |  |  |  | 0.00 |
| suelo_mukey.csv | frec_inundacion | frecuencia de inundación dominante (flodfreqdcd traducida) | adimensional | USDA NRCS SSURGO muaggatt |  |  |  | 1.82 |
| suelo_mukey.csv | napa_min_cm | profundidad mínima anual de la napa (wtdepannmin) | cm | USDA NRCS SSURGO muaggatt |  |  |  | 36.36 |
| suelo_mukey.csv | pendiente_dcd_pct | pendiente del componente dominante (slopegraddcp) | % | USDA NRCS SSURGO muaggatt |  |  |  | 1.82 |
| suelo_mukey.csv | pendiente_comp_pct | pendiente media ponderada de los componentes (slopegradwta) | % | USDA NRCS SSURGO muaggatt |  |  |  | 1.82 |
| suelo_mukey.csv | clase_erosion | clase de erosión (erocl) del componente dominante | adimensional | USDA NRCS SSURGO component |  |  |  | 1.82 |
| suelo_mukey.csv | pct_comp_dominante | comppct_r del componente dominante | % | USDA NRCS SSURGO component |  |  |  | 0.00 |
| suelo_mukey.csv | materia_organica_pct | materia orgánica 0-30 cm (por espesor y comppct_r) | % | USDA NRCS SSURGO chorizon |  |  |  | 1.82 |
| suelo_mukey.csv | arcilla_pct | arcilla 0-30 cm | % | USDA NRCS SSURGO chorizon |  |  |  | 1.82 |
| suelo_mukey.csv | arena_pct | arena 0-30 cm | % | USDA NRCS SSURGO chorizon |  |  |  | 1.82 |
| suelo_mukey.csv | limo_pct | limo 0-30 cm | % | USDA NRCS SSURGO chorizon |  |  |  | 1.82 |
| suelo_mukey.csv | ph_agua | pH 1:1 en agua 0-30 cm | pH | USDA NRCS SSURGO chorizon |  |  |  | 1.82 |
| suelo_mukey.csv | factor_k_rusle | factor K (kwfact) del horizonte superficial | t·ha·h/(ha·MJ·mm) | USDA NRCS SSURGO chorizon |  |  |  | 1.82 |
| vegetacion_px_obs.csv | producto | landsat_c2_l2 o hls_s30 | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | sensor | L5, L7, L8, L9, S2A, S2B o S2C | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | refl_blue | reflectancia azul | reflectancia | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | refl_green | reflectancia verde | reflectancia | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | refl_red | reflectancia roja | reflectancia | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | refl_nir | reflectancia NIR (Landsat nir08, HLS B8A) | reflectancia | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | refl_swir1 | reflectancia SWIR 1,6 µm | reflectancia | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | refl_swir2 | reflectancia SWIR 2,2 µm | reflectancia | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | ndvi | (nir − red) / (nir + red) | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | evi2 | 2,5 (nir − red) / (nir + 2,4 red + 1) | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | gcvi | nir / green − 1 | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | ndmi | (nir − swir1) / (nir + swir1) | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | slc_off | 1 si Landsat 7 desde 2003-05-31 | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_obs.csv | qa_valor | valor crudo de QA_PIXEL (Landsat) o Fmask (HLS) | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000-03-04 | 2025-11-26 | 0.00 |
| vegetacion_px_anual.csv | ndvi_max | NDVI máximo del año (Landsat, mar-nov) | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000 | 2025 | 0.00 |
| vegetacion_px_anual.csv | doy_ndvi_max | día del año del NDVI máximo | día | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000 | 2025 | 0.00 |
| vegetacion_px_anual.csv | evi2_max | EVI2 máximo del año (Landsat) | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000 | 2025 | 0.00 |
| vegetacion_px_anual.csv | doy_evi2_max | día del año del EVI2 máximo | día | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000 | 2025 | 0.00 |
| vegetacion_px_anual.csv | ndvi_media_jul_ago | NDVI medio de las observaciones de julio-agosto (Landsat) | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000 | 2025 | 14.50 |
| vegetacion_px_anual.csv | n_obs_mar_nov | observaciones despejadas Landsat de marzo a noviembre | obs | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000 | 2025 | 0.00 |
| vegetacion_px_anual.csv | n_obs_may_jun | observaciones despejadas Landsat de mayo-junio | obs | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000 | 2025 | 0.00 |
| vegetacion_px_anual.csv | n_obs_jul_ago | observaciones despejadas Landsat de julio-agosto | obs | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2000 | 2025 | 0.00 |
| vegetacion_px_anual.csv | ndvi_max_s2 | NDVI máximo del año con HLS S30 | adimensional | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2016 | 2025 | 61.54 |
| vegetacion_px_anual.csv | n_obs_jul_ago_s2 | observaciones despejadas HLS S30 de julio-agosto | obs | USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer) |  | 2016 | 2025 | 61.54 |
| suelo_desnudo_px.csv | refl_blue_mar_may | mediana de refl_blue con NDVI < 0,25, 15 mar-15 may (Landsat) | reflectancia | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 17.50 |
| suelo_desnudo_px.csv | refl_red_mar_may | mediana de refl_red con NDVI < 0,25, 15 mar-15 may (Landsat) | reflectancia | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 17.50 |
| suelo_desnudo_px.csv | refl_nir_mar_may | mediana de refl_nir con NDVI < 0,25, 15 mar-15 may (Landsat) | reflectancia | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 17.50 |
| suelo_desnudo_px.csv | refl_swir1_mar_may | mediana de refl_swir1 con NDVI < 0,25, 15 mar-15 may (Landsat) | reflectancia | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 17.50 |
| suelo_desnudo_px.csv | refl_swir2_mar_may | mediana de refl_swir2 con NDVI < 0,25, 15 mar-15 may (Landsat) | reflectancia | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 17.50 |
| suelo_desnudo_px.csv | nbr2_mar_may | (swir1 − swir2)/(swir1 + swir2) de las medianas, 15 mar-15 may | adimensional | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 17.50 |
| suelo_desnudo_px.csv | n_obs_mar_may | observaciones con NDVI < 0,25, 15 mar-15 may | obs | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 0.00 |
| suelo_desnudo_px.csv | refl_blue_oct_nov | mediana de refl_blue con NDVI < 0,25, oct-nov (Landsat) | reflectancia | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 15.87 |
| suelo_desnudo_px.csv | refl_red_oct_nov | mediana de refl_red con NDVI < 0,25, oct-nov (Landsat) | reflectancia | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 15.87 |
| suelo_desnudo_px.csv | refl_nir_oct_nov | mediana de refl_nir con NDVI < 0,25, oct-nov (Landsat) | reflectancia | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 15.87 |
| suelo_desnudo_px.csv | refl_swir1_oct_nov | mediana de refl_swir1 con NDVI < 0,25, oct-nov (Landsat) | reflectancia | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 15.87 |
| suelo_desnudo_px.csv | refl_swir2_oct_nov | mediana de refl_swir2 con NDVI < 0,25, oct-nov (Landsat) | reflectancia | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 15.87 |
| suelo_desnudo_px.csv | nbr2_oct_nov | (swir1 − swir2)/(swir1 + swir2) de las medianas, oct-nov | adimensional | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 15.87 |
| suelo_desnudo_px.csv | n_obs_oct_nov | observaciones con NDVI < 0,25, oct-nov | obs | USGS/NASA Landsat C2 L2 |  | 2000 | 2025 | 0.00 |
| suelo_desnudo_px_compuesto.csv | refl_blue | mediana multianual (todos los años) de refl_blue con NDVI < 0,25 en ambas ventanas | reflectancia | USGS/NASA Landsat C2 L2 |  |  |  | 0.02 |
| suelo_desnudo_px_compuesto.csv | refl_red | mediana multianual (todos los años) de refl_red con NDVI < 0,25 en ambas ventanas | reflectancia | USGS/NASA Landsat C2 L2 |  |  |  | 0.02 |
| suelo_desnudo_px_compuesto.csv | refl_nir | mediana multianual (todos los años) de refl_nir con NDVI < 0,25 en ambas ventanas | reflectancia | USGS/NASA Landsat C2 L2 |  |  |  | 0.02 |
| suelo_desnudo_px_compuesto.csv | refl_swir1 | mediana multianual (todos los años) de refl_swir1 con NDVI < 0,25 en ambas ventanas | reflectancia | USGS/NASA Landsat C2 L2 |  |  |  | 0.02 |
| suelo_desnudo_px_compuesto.csv | refl_swir2 | mediana multianual (todos los años) de refl_swir2 con NDVI < 0,25 en ambas ventanas | reflectancia | USGS/NASA Landsat C2 L2 |  |  |  | 0.02 |
| suelo_desnudo_px_compuesto.csv | nbr2 | NBR2 de las medianas multianuales | adimensional | USGS/NASA Landsat C2 L2 |  |  |  | 0.02 |
| suelo_desnudo_px_compuesto.csv | n_obs | observaciones de suelo desnudo de todos los años | obs | USGS/NASA Landsat C2 L2 |  |  |  | 0.00 |
| clima_lote_diario.csv | prec_power_mm | precipitación PRECTOTCORR | mm | NASA POWER (AG), en el centroide del lote |  | 2000-01-01 | 2025-12-31 | 0.00 |
| clima_lote_diario.csv | tmax_c | temperatura máxima a 2 m | °C | NASA POWER (AG), en el centroide del lote |  | 2000-01-01 | 2025-12-31 | 0.00 |
| clima_lote_diario.csv | tmin_c | temperatura mínima a 2 m | °C | NASA POWER (AG), en el centroide del lote |  | 2000-01-01 | 2025-12-31 | 0.00 |
| clima_lote_diario.csv | tmed_c | temperatura media a 2 m | °C | NASA POWER (AG), en el centroide del lote |  | 2000-01-01 | 2025-12-31 | 0.00 |
| clima_lote_diario.csv | hr_pct | humedad relativa a 2 m | % | NASA POWER (AG), en el centroide del lote |  | 2000-01-01 | 2025-12-31 | 0.00 |
| clima_lote_diario.csv | viento_ms | viento a 2 m | m/s | NASA POWER (AG), en el centroide del lote |  | 2000-01-01 | 2025-12-31 | 0.00 |
| clima_lote_diario.csv | rad_mj_m2 | radiación global ALLSKY_SFC_SW_DWN | MJ/m²/día | NASA POWER (AG), en el centroide del lote |  | 2000-01-01 | 2025-12-31 | 0.00 |
| clima_lote_diario.csv | eto_pm_mm | ETo FAO-56 Penman-Monteith | mm | NASA POWER (AG), en el centroide del lote |  | 2000-01-01 | 2025-12-31 | 0.00 |
| clima_lote_diario.csv | deficit_mm | prec_power_mm − eto_pm_mm | mm | NASA POWER (AG), en el centroide del lote |  | 2000-01-01 | 2025-12-31 | 0.00 |
| clima_lote_diario.csv | prec_imerg_mm | precipitación IMERG de la celda de 0,1° del centroide | mm | GPM IMERG Final vía POWER (IMERG_PRECTOT) |  | 2000-06-01 | 2025-12-31 | 1.60 |
| clima_lote_diario.csv | sm_rootzone_m3m3 | SMAP L4 zona radicular, celda de 9 km del centroide | m³/m³ | NASA SMAP L4 vía USDA Crop-CASMA (paquete agua) |  | 2015-03-31 | 2025-12-31 | 58.64 |
| clima_lote_diario.csv | sm_surface_m3m3 | SMAP L4 superficial, celda de 9 km del centroide | m³/m³ | NASA SMAP L4 vía USDA Crop-CASMA (paquete agua) |  | 2015-03-31 | 2025-12-31 | 58.64 |
| clima_lote_anual.csv | prec_temporada_mm | lluvia abril-septiembre | mm | NASA POWER (AG), en el centroide del lote |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | prec_abr_mm | lluvia de abril | mm | NASA POWER (AG), en el centroide del lote |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | prec_may_mm | lluvia de mayo | mm | NASA POWER (AG), en el centroide del lote |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | prec_jul_mm | lluvia de julio | mm | NASA POWER (AG), en el centroide del lote |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | prec_ago_mm | lluvia de agosto | mm | NASA POWER (AG), en el centroide del lote |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | deficit_temporada_mm | Σ (prec − ETo) abril-septiembre | mm | NASA POWER (AG), en el centroide del lote |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | dias_tmax_gt30_jul | días de julio con tmax > 30 °C | días | NASA POWER (AG), en el centroide del lote |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | tmax_jul_c | tmax media de julio | °C | NASA POWER (AG), en el centroide del lote |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | gdd_temporada | grados día 10/30 °C abril-septiembre | °C·día | NASA POWER (AG), en el centroide del lote |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | prec_invierno_previo_mm | lluvia noviembre del año anterior a marzo | mm | NASA POWER (AG), en el centroide del lote |  | 2001 | 2025 | 3.85 |
| clima_lote_anual.csv | dias_lluvia_gt50_abr_may | días de abril-mayo con lluvia > 50 mm | días | NASA POWER (AG), en el centroide del lote |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | prec_temporada_imerg_mm | lluvia IMERG abril-septiembre | mm | GPM IMERG Final vía POWER (IMERG_PRECTOT) |  | 2001 | 2025 | 3.85 |
| clima_lote_anual.csv | prec_abr_imerg_mm | lluvia IMERG de abril | mm | GPM IMERG Final vía POWER (IMERG_PRECTOT) |  | 2001 | 2025 | 3.85 |
| clima_lote_anual.csv | prec_may_imerg_mm | lluvia IMERG de mayo | mm | GPM IMERG Final vía POWER (IMERG_PRECTOT) |  | 2001 | 2025 | 3.85 |
| clima_lote_anual.csv | prec_jul_imerg_mm | lluvia IMERG de julio | mm | GPM IMERG Final vía POWER (IMERG_PRECTOT) |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | prec_ago_imerg_mm | lluvia IMERG de agosto | mm | GPM IMERG Final vía POWER (IMERG_PRECTOT) |  | 2000 | 2025 | 0.00 |
| clima_lote_anual.csv | dias_lluvia_gt50_abr_may_imerg | días de abril-mayo con IMERG > 50 mm | días | GPM IMERG Final vía POWER (IMERG_PRECTOT) |  | 2001 | 2025 | 3.85 |
| clima_lote_anual.csv | sm_rootzone_temporada_m3m3 | SMAP zona radicular media abril-septiembre, celda de 9 km del centroide | m³/m³ | NASA SMAP L4 vía USDA Crop-CASMA (paquete agua) |  | 2015 | 2025 | 57.69 |
| drenaje_px.csv | drenado_canos | 1 si la celda AgTile-US que contiene el centro del píxel está drenada con caños | adimensional | Valayamkunnath et al. 2020 (AgTile-US) |  |  |  | 0.00 |
| drenaje_px.csv | tile_prob_seetiledrain | probabilidad de drenaje con caños de la celda SEETileDrain (2017, ~30 m, EPSG:4326) que contiene el centro del píxel | adimensional | Wan et al. 2024 (SEETileDrain) |  |  |  |  |
| drenaje_px.csv | tile_seetiledrain | clase publicada de SEETileDrain (1 = drenado con caños) de la celda que contiene el centro del píxel | adimensional | Wan et al. 2024 (SEETileDrain) |  |  |  |  |
<!-- TABLA:FIN -->

## Controles de calidad

<!-- CONTROLES:INICIO -->
### Píxeles por lote

| id_lote | paisaje | n_px | n_px_interior | relieve_m |
|---|---|---|---|---|
| 17019_171825005060041 | llanura_control | 531 | 435 | 4.07 |
| 17019_171825005511042 | llanura_control | 435 | 349 | 4.00 |
| 18157_181825000203707 | indiana | 685 | 581 | 10.20 |
| 18157_181825001116483 | indiana | 445 | 365 | 4.43 |
| 19047_191825002083543 | lomas_loess | 516 | 419 | 31.01 |
| 19079_191825000600003 | depresiones | 917 | 795 | 11.45 |
| 19079_191825001174693 | depresiones | 1212 | 1071 | 11.46 |
| 19079_191825002094751 | depresiones | 646 | 549 | 11.45 |
| 19165_191825001638480 | lomas_loess | 490 | 399 | 31.03 |
| 19165_191825002368896 | lomas_loess | 453 | 371 | 31.01 |

### Pureza del cultivo por lote y año

- Lotes-año con lote_partido = 1 (menos de 90 % del grupo principal): 9 de 180.
- 17019_171825005060041: pureza mínima 98.2 %, años partidos: ninguno
- 17019_171825005511042: pureza mínima 83.1 %, años partidos: [2008, 2010]
- 18157_181825000203707: pureza mínima 93.1 %, años partidos: ninguno
- 18157_181825001116483: pureza mínima 93.4 %, años partidos: ninguno
- 19047_191825002083543: pureza mínima 93.1 %, años partidos: ninguno
- 19079_191825000600003: pureza mínima 61.8 %, años partidos: [2008, 2010, 2015]
- 19079_191825001174693: pureza mínima 96.7 %, años partidos: ninguno
- 19079_191825002094751: pureza mínima 97.6 %, años partidos: ninguno
- 19165_191825001638480: pureza mínima 61.1 %, años partidos: [2008, 2009, 2010, 2011]
- 19165_191825002368896: pureza mínima 98.9 %, años partidos: ninguno

### Alineación CSB–CDL

- Años de la ventana CSB 2018-2025: lotes-año donde el grupo CSB coincide con el principal del CDL: 80 de 80; % medio de píxeles interiores con la clase del CSB: 99.7.

### Relieve

- Lotes con menos de 2 m de relieve NASADEM: 0 (ninguno).
- Lotes con menos de 2 m de relieve USGS 3DEP: 1 (17019_171825005511042).
- Correlación NASADEM–3DEP de la elevación por píxel (todos los lotes): 1.000; diferencia media 3DEP − NASADEM: 0.30 m.

| id_lote | relieve_m | relieve_3dep_m | pct_px_drenado_canos |
|---|---|---|---|
| 17019_171825005060041 | 4.07 | 2.68 | 98.3 |
| 17019_171825005511042 | 4.00 | 1.60 | 99.5 |
| 18157_181825000203707 | 10.20 | 8.28 | 58.7 |
| 18157_181825001116483 | 4.43 | 2.47 | 82.7 |
| 19047_191825002083543 | 31.01 | 26.12 | 37.0 |
| 19079_191825000600003 | 11.45 | 7.35 | 71.1 |
| 19079_191825001174693 | 11.46 | 7.71 | 63.1 |
| 19079_191825002094751 | 11.45 | 9.13 | 39.6 |
| 19165_191825001638480 | 31.03 | 31.18 | 14.5 |
| 19165_191825002368896 | 31.01 | 27.06 | 5.7 |

### Observaciones despejadas

- Filas de vegetacion_px_obs.csv: Landsat 1483118, HLS S30 1474898 (descarga parcial: ver Problemas conocidos).
- Píxeles-año (con escenas Landsat bajadas) con menos de 3 observaciones despejadas en julio-agosto: 128063 de 164580 (77.8 %).
- Mediana de observaciones despejadas Landsat mar-nov por píxel-año: 9.

### 2012 y SLC-off

- 2012: observaciones despejadas por sensor {'L7': 47103} (Landsat 5 terminó en 2011 y Landsat 8 empezó en 2013: 2012 solo tiene Landsat 7 con SLC-off).
- Observaciones con slc_off = 1: 515749 de 1483118.
- Escenas L7 SLC-off con algún píxel despejado: % medio de píxeles del lote sin dato (franjas, nubes o borde) 29.3 %.

### Coherencia Landsat–Sentinel-2

- Pares mismo píxel con fechas a 3 días o menos: 343925; NDVI Landsat − HLS S30: media -0.0173, desvío 0.0477.

### Cobertura de SSURGO

- 17019_171825005060041: 100.0 % del lote con mukey, 3 mukeys
- 17019_171825005511042: 100.0 % del lote con mukey, 4 mukeys
- 18157_181825000203707: 100.0 % del lote con mukey, 9 mukeys
- 18157_181825001116483: 100.0 % del lote con mukey, 6 mukeys
- 19047_191825002083543: 100.0 % del lote con mukey, 5 mukeys
- 19079_191825000600003: 100.0 % del lote con mukey, 9 mukeys
- 19079_191825001174693: 100.0 % del lote con mukey, 10 mukeys
- 19079_191825002094751: 100.0 % del lote con mukey, 9 mukeys
- 19165_191825001638480: 100.0 % del lote con mukey, 10 mukeys
- 19165_191825002368896: 100.0 % del lote con mukey, 5 mukeys
<!-- CONTROLES:FIN -->
