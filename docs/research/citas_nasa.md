# Citas y DOIs de los productos que usamos

Pregunta: Para la entrega de Space Apps, ¿cuál es el nombre oficial, la versión, el DOI, la cita recomendada y la
licencia de cada producto de la NASA que usa el pipeline, y qué columnas de nuestros CSV salen de cada uno?
¿Cuáles de nuestras fuentes **no** son de la NASA y cómo se citan?

Respuesta corta: El pipeline usa **12 productos de la NASA** con DOI, más NASA POWER (que no tiene DOI y se
cita con un texto de reconocimiento). Los productos son GPM IMERG Final diario V07 (a través de POWER),
SMAP L4 `SPL4SMGP` (a través de Crop-CASMA), GRACE-DA-DM EE.UU. V4.0, MODIS MOD13Q1 y MOD11A2 V061, NLDAS-2
Noah mensual V2.0, NASADEM V001, ECOSTRESS L2T_LSTE, L3T_JET y L4T_ESI V002, y HLS S30 V2.0. Landsat C2 L2 es de
USGS y NASA, pero lo distribuye y cita USGS. **MOD16A2 y MCD12Q1 no se usaron**: en su lugar entraron NLDAS-2 y
la máscara del CDL. Todos los productos de la NASA están bajo la política de datos abiertos de EOSDIS, sin
restricciones y con la cita como única obligación. Las fuentes que no son de la NASA son USDA NASS (Quick Stats,
Crop Progress, Censo, CDL y CSB), USDA ERS, USDA NRCS (SSURGO), USGS (Landsat, 3DEP y Annual NLCD), el US Census
Bureau, PRISM (Oregon State), CoCoRaHS, AgTile-US y Crop-CASMA (USDA NASS con GMU). Hay tres puntos que
necesitan atención: la **versión de SMAP** que sirve Crop-CASMA no está confirmada; los archivos de **GRACE-DA-DM**
traen `030` en el nombre, pero la colección vigente en CMR es la V4.0; y la **corrida de IMERG** que usa POWER
cambia en los meses recientes. La documentación de POWER confirma que usa la Final Run hasta donde llega y desde ahí
la **Late Run** (no la Early): en nuestros CSV, del 2025-10-01 al 2025-12-31 es Late V07
(`10.5067/GPM/IMERGDL/DAY/07`). La versión de SMAP sigue sin confirmar en Crop-CASMA, pero nuestros datos llegan a
2025-12-31 y la V7 termina el 2025-07-03, así que al menos el último semestre tiene que ser V8: se recomienda citar
la **V8** (actualización T043, 2026-11-15).

Detalle:

Método. Recorrí los diccionarios de columnas de `docs/datasets/*.md` (columna `fuente`) y los `download.py` de
`src/`. El `manifest.csv` de esta máquina tiene una sola fila (NASS Quick Stats), así que no sirvió para armar la
lista. Para cada producto de la NASA consulté su colección en CMR
(`cmr.earthdata.nasa.gov/search/collections.umm_json?short_name=…&version=…`), de donde salen el `concept-id`, el
DOI, `CollectionCitations` y `UseConstraints`. La cita en formato APA es la que devuelve doi.org por negociación
de contenido (`Accept: text/x-bibliography; style=apa`), que toma los metadatos que el DAAC registró en DataCite.
Todo se consultó el 2026-11-15.

## 1. Productos de la NASA

Licencia común: [NASA EOSDIS Data Use Policy](https://earthdata.nasa.gov/earth-observation-data/data-use-policy).
Los datos son abiertos, sin restricciones de uso ni de redistribución, y se pide citar el DOI. Los DAAC agregan su
propia guía: LP DAAC (MODIS, NASADEM, ECOSTRESS, HLS), GES DISC (IMERG, GRACE-DA-DM, NLDAS:
[data-guidelines](https://disc.gsfc.nasa.gov/data-guidelines)) y NSIDC (SMAP:
[use_copyright](https://nsidc.org/about/use_copyright.html)).

### 1.1 NASA POWER (sin DOI)

| | |
|---|---|
| Nombre oficial | NASA Prediction Of Worldwide Energy Resources (POWER), API diaria por punto, comunidad AG |
| Versión | API v2.x (la versión exacta no está en el data card; anotarla al citar) |
| DOI | no tiene |
| DAAC / proyecto | NASA Langley Research Center (LaRC) |
| Licencia | La página de referencias no declara licencia. Pide avisar a `larc-power-project@mail.nasa.gov` cuando se publica o se redistribuye |

Cita recomendada (de [POWER Referencing](https://power.larc.nasa.gov/docs/referencing/)), con las dos partes:
> "The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research Center's
> Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science Division."
> "The data was obtained from the POWER Project's Daily 2.x.x version on YYYY/MM/DD." (la página da el ejemplo con "Hourly"; usamos la API diaria)

Columnas:
- `clima_diario` y `clima_mensual`: `tmed_c`, `tmax_c`, `tmin_c`, `prec_power_mm`, `hr_pct`, `viento_ms`,
  `rad_mj_m2`, `gwettop`, `gwetroot` y `gwetprof`.
- Derivadas: `eto_pm_mm`, `deficit_mm`, los días con umbral, los GDD, los índices de lluvia, `spi1/3/6` y
  `anom_tmed_c` del mensual, y todo `clima_anual`.
- `lotes`: `clima_lote_diario` y `clima_lote_anual`, en el centroide del lote.

Nota: POWER no produce las variables, las redistribuye. La meteorología viene de MERRA-2 (GMAO) y la radiación de
CERES/GEWEX. Si el jurado pide fuentes primarias, convendría agregar MERRA-2; eso no se verificó en esta tarea.

### 1.2 GPM IMERG Final diario V07 (a través de POWER)

| | |
|---|---|
| Nombre oficial | GPM IMERG Final Precipitation L3 1 day 0.1 degree x 0.1 degree V07 (`GPM_3IMERGDF`) |
| Versión | 07 |
| DOI | [10.5067/GPM/IMERGDF/DAY/07](https://doi.org/10.5067/GPM/IMERGDF/DAY/07) |
| CMR | `C2723754864-GES_DISC`, de 1998-01-01 a 2025-09-30 (según CMR al 2026-11-15) |
| DAAC | GES DISC |

Cita (DataCite / GES DISC):
> Huffman, G. J., Stocker, E. F., Bolvin, D. T., Nelkin, E. J., Tan, J. (2023). *GPM IMERG Final Precipitation
> L3 1 day 0.1 degree x 0.1 degree V07* [Dataset]. Ed. A. Savtchenko. NASA Goddard Earth Sciences Data and
> Information Services Center. https://doi.org/10.5067/GPM/IMERGDF/DAY/07

Columnas: `prec_imerg_mm` (`clima_diario` y `clima_mensual`); en `lotes`, `clima_lote_diario:prec_imerg_mm` y las
`*_imerg*` de `clima_lote_anual`.

Ojo: no lo bajamos de GES DISC. Viene del parámetro `IMERG_PRECTOT` de POWER. Hay que citar las dos fuentes,
POWER y el DOI de IMERG.

**Final y Late (resuelto en T043).** La página de metodología meteorológica de POWER
([sources_meteorology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/), sección IMERG)
tiene esta tabla de fuentes: "IMERG Final Run | June 1, 1998 | 3.5 Months Behind Near Real Time" e "IMERG Late Run
| End of IMERG Final Run | Near Real Time | 14 hours". También avisa: "The time series will include both Late and
Final Run data within a few months of NRT; end the analysis 3.5 months behind NRT when assessing trends." No
menciona la Early Run. En CMR, el último gránulo de `GPM_3IMERGDF` V07 es del 2025-09-30, así que en nuestros CSV
(que llegan hasta el 2025-12-31) **del 2025-10-01 al 2025-12-31 los datos son de la Late Run**. Cuando la Final avance, POWER
reemplaza esos días; la respuesta de la API (v2.10.3) no dice qué corrida trae cada fecha (`header.sources` =
`["IMERG"]`). La Late usa un ajuste climatológico con pluviómetros, no el mensual de GPCC, y le pueden faltar
pasadas de microondas.

| | |
|---|---|
| Nombre oficial | GPM IMERG Late Precipitation L3 1 day 0.1 degree x 0.1 degree V07 (`GPM_3IMERGDL`) |
| DOI | [10.5067/GPM/IMERGDL/DAY/07](https://doi.org/10.5067/GPM/IMERGDL/DAY/07) (`C2723754859-GES_DISC`) |

> Huffman, G. J., Stocker, E. F., Bolvin, D. T., Nelkin, E. J., Tan, J. (2023). *GPM IMERG Late Precipitation
> L3 1 day 0.1 degree x 0.1 degree V07* [Dataset]. Ed. A. Savtchenko. NASA Goddard Earth Sciences Data and
> Information Services Center. https://doi.org/10.5067/GPM/IMERGDL/DAY/07

### 1.3 SMAP L4 `SPL4SMGP` (a través de Crop-CASMA)

| | |
|---|---|
| Nombre oficial | SMAP L4 Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture Geophysical Data |
| Versión | **sin confirmar en Crop-CASMA**; se recomienda citar la **V008** (ver abajo). La V007 está retirada (CMR: 2015-03-31 a 2025-07-03); la V008 va de 2015-03-31 en adelante |
| DOI V008 | [10.5067/T5RUATAQREF8](https://doi.org/10.5067/T5RUATAQREF8) (`C3480440870-NSIDC_CPRD`) |
| DOI V007 | [10.5067/EVKPQZ4AFC4D](https://doi.org/10.5067/EVKPQZ4AFC4D) (`C2938665761-NSIDC_CPRD`) |
| DAAC | NSIDC DAAC |
| Licencia | CMR: "freely, openly, and fully available to use without restrictions, provided that you cite the data" |

Cita (NSIDC, [página de la V8](https://nsidc.org/data/spl4smgp/versions/8)):
> Reichle, R., De Lannoy, G., Koster, R. D., Crow, W. T., Kimball, J. S., Liu, Q. & Bechtold, M. (2025). SMAP L4
> Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture Geophysical Data. (SPL4SMGP, Version 8).
> [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center.
> https://doi.org/10.5067/T5RUATAQREF8. [describe subset used if applicable]. Date Accessed MM-DD-YYYY.

Para la V7 la cita es la misma, con año 2022, "Version 7" y el DOI 10.5067/EVKPQZ4AFC4D.

**Qué versión usa Crop-CASMA (revisado en T043).** Ninguna página oficial de Crop-CASMA dice qué versión usa. Los
[metadatos FGDC de NASS](https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_cropcasma.htm)
(publicados el 2025-01-31) y la [guía de usuario](https://nassgeo.csiss.gmu.edu/Crop-CASMA-User/user/data/) solo
dicen "NASA SMAP level 4 data", y la [revisión de la guía de desarrollador](https://nassgeo.csiss.gmu.edu/Crop-CASMA-Developer/about/revision/)
solo tiene la 1.0 de 2020. El `GetCapabilities` del WCS (`cloud.csiss.gmu.edu/smap_server`) no respondió el
2026-11-15, y los GeoTIFF crudos no están en esta máquina (pro-3), así que tampoco se pudieron revisar sus
metadatos. Hay una deducción firme: `agua_diario` tiene datos hasta el 2025-12-31, y NSIDC solo produce la V007
hasta el 2025-07-03, así que **desde el 2025-07-04 el dato es V008**. Lo anterior puede ser V007 o la V008
reprocesada. **Recomendación:** citar la V008, que cubre todo el período (2015-03-31 en adelante), y aclarar que
Crop-CASMA no informa la versión. Para confirmarlo, conviene abrir un GeoTIFF crudo de `data/raw/agua/smap/` en la
máquina que lo tiene (`gdalinfo -mdd all`) o escribirle al contacto de Crop-CASMA.

Columnas:
- `agua_diario` y `agua_mensual`: `sm_surface_m3m3` y `sm_rootzone_m3m3`; en el mensual también `*_min_m3m3`.
- Derivadas: `sm_rootzone_anom_z` y `dias_sm_saturado`.
- `lotes`: `clima_lote_diario:sm_*` y `clima_lote_anual:sm_rootzone_temporada_m3m3`.

Las capas diarias salieron de Crop-CASMA, que también se cita (ver §2).

### 1.4 GRACE-DA-DM, versión EE.UU.

| | |
|---|---|
| Nombre oficial | Groundwater and Soil Moisture Conditions from GRACE and GRACE-FO Data Assimilation L4 7-days 0.125 x 0.125 degree U.S. V4.0 (`GRACEDADM_CLSM0125US_7D`) |
| Versión | En CMR, 4.0 (`C1993409520-GES_DISC`, desde 2002-04-01). Nuestros archivos: `.030` en el nombre y `version=040` adentro. La 3.0 no figura en CMR |
| DOI | [10.5067/UH653SEZR9VQ](https://doi.org/10.5067/UH653SEZR9VQ) |
| DAAC | GES DISC; nosotros bajamos la copia pública del NDMC (nasagrace.unl.edu) |

Cita (CMR `CollectionCitations`):
> Beaudoing, H., M. Rodell, A. Getirana, and B. Li, NASA/GSFC/HSL (2021). *Groundwater and Soil Moisture
> Conditions from GRACE and GRACE-FO Data Assimilation L4 7-days 0.125 x 0.125 degree U.S. V4.0*. Greenbelt, MD,
> USA, Goddard Earth Sciences Data and Information Services Center (GES DISC). https://doi.org/10.5067/UH653SEZR9VQ

DataCite lista como autores a "Matthew Rodell and Hiroko Kato Beaudoing", así que no coincide con CMR. Usé la de
CMR porque es la que publica el DAAC.

Columnas: `agua_semanal`: `gws_pctl`, `rtzsm_pctl` y `sfsm_pctl`.

### 1.5 MODIS MOD13Q1 V061

| | |
|---|---|
| Nombre oficial | MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061 |
| DOI | [10.5067/MODIS/MOD13Q1.061](https://doi.org/10.5067/MODIS/MOD13Q1.061) (`C1748066515-LPCLOUD`) |
| DAAC | LP DAAC; nosotros lo bajamos de Microsoft Planetary Computer (`modis-13Q1-061`) |

> Didan, K. (2021). *MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061* [Dataset]. NASA Land
> Processes Distributed Active Archive Center. https://doi.org/10.5067/MODIS/MOD13Q1.061

Columnas:
- `vegetacion_16d`: `ndvi`, `evi`, `ndvi_maiz`, `ndvi_soja` y `frac_pixeles_validos`.
- `vegetacion_mensual`: `ndvi`, `evi`, `ndvi_maiz`, `ndvi_soja`, `ndvi_anom_z` y `vci`. `tci` y `vhi` combinan
  MOD13Q1 con MOD11A2.
- Todo `fenologia_anual`.

### 1.6 MODIS MOD11A2 V061

| | |
|---|---|
| Nombre oficial | MODIS/Terra Land Surface Temperature/Emissivity 8-Day L3 Global 1km SIN Grid V061 |
| DOI | [10.5067/MODIS/MOD11A2.061](https://doi.org/10.5067/MODIS/MOD11A2.061) (`C2269056084-LPCLOUD`) |
| DAAC | LP DAAC; bajado de Planetary Computer (`modis-11A2-061`) |

> Wan, Z., Hook, S., & Hulley, G. (2021). *MODIS/Terra Land Surface Temperature/Emissivity 8-Day L3 Global 1km
> SIN Grid V061* [Dataset]. NASA Land Processes Distributed Active Archive Center.
> https://doi.org/10.5067/MODIS/MOD11A2.061

Columnas: `vegetacion_mensual`: `lst_dia_c`, `lst_noche_c`, `tci` y `vhi`.

### 1.7 NLDAS-2 Noah mensual V2.0

| | |
|---|---|
| Nombre oficial | NLDAS Noah Land Surface Model L4 Monthly 0.125 x 0.125 degree V2.0 (`NLDAS_NOAH0125_M`) |
| DOI | [10.5067/WB224IA3PVOJ](https://doi.org/10.5067/WB224IA3PVOJ) (`C1887990023-GES_DISC`, desde 1979-01-01) |
| DAAC | GES DISC (por Harmony) |

Cita (CMR):
> NLDAS project (2022). *NLDAS Noah Land Surface Model L4 Monthly 0.125 x 0.125 degree V2.0*. Ed. David M. Mocko,
> NASA/GSFC/HSL. Greenbelt, Maryland, USA, Goddard Earth Sciences Data and Information Services Center (GES DISC).
> https://doi.org/10.5067/WB224IA3PVOJ

En CMR la fecha de publicación es 2022-01-08; DataCite pone 2020.

Columnas:
- `nldas_mensual`: `sm_0_10cm_m3m3`, `sm_0_100cm_m3m3`, `sm_0_100cm_anom_z`, `et_nldas_mm`,
  `escorrentia_nldas_mm` y `swe_nldas_mm`.
- `vegetacion_mensual`: `et_mm`, `pet_mm` y `et_pet_ratio` (reemplazan a MOD16A2).

### 1.8 NASADEM V001

| | |
|---|---|
| Nombre oficial | NASADEM Merged DEM Global 1 arc second V001 (`NASADEM_HGT`) |
| DOI | [10.5067/MEASURES/NASADEM/NASADEM_HGT.001](https://doi.org/10.5067/MEASURES/NASADEM/NASADEM_HGT.001) (`C2763264762-LPCLOUD`) |
| DAAC | LP DAAC; bajado de Planetary Computer |

> NASA JPL (2020). *NASADEM Merged DEM Global 1 arc second V001* [Dataset]. NASA Land Processes Distributed
> Active Archive Center. https://doi.org/10.5067/MEASURES/NASADEM/NASADEM_HGT.001

En CMR el autor es "Sean Buckley"; en DataCite, "NASA JPL".

Columnas:
- `suelo_terreno_estatico`: `elevacion_media_m`, `elevacion_desvio_m`, `pendiente_media_pct`,
  `pendiente_gt2_pct`, `twi_medio` y `twi_decil_sup_pct`.
- `lotes`: `lotes:relieve_m` y, en `terreno_px`, `elevacion_m`, `pendiente_pct`, `aspecto_grados`, `curv_plan`,
  `curv_perfil`, `tpi_90m_m`, `tpi_300m_m`, `twi` y `prof_depresion_m`.

### 1.9 ECOSTRESS colección 2 (V002)

| Producto | Nombre oficial | DOI | CMR |
|---|---|---|---|
| ECO_L2T_LSTE | ECOSTRESS Tiled Land Surface Temperature and Emissivity Instantaneous L2 Global 70 m V002 | [10.5067/ECOSTRESS/ECO_L2T_LSTE.002](https://doi.org/10.5067/ECOSTRESS/ECO_L2T_LSTE.002) | C2076090826-LPCLOUD |
| ECO_L3T_JET | ECOSTRESS Tiled Evapotranspiration Instantaneous and Daytime L3 Global 70 m V002 | [10.5067/ECOSTRESS/ECO_L3T_JET.002](https://doi.org/10.5067/ECOSTRESS/ECO_L3T_JET.002) | C2076106409-LPCLOUD |
| ECO_L4T_ESI | ECOSTRESS Tiled Evaporative Stress Index PT-JPL Instantaneous L4 Global 70 m V002 | [10.5067/ECOSTRESS/ECO_L4T_ESI.002](https://doi.org/10.5067/ECOSTRESS/ECO_L4T_ESI.002) | C2076104650-LPCLOUD |

> Hook, S., & Hulley, G. (2022). *ECOSTRESS Tiled Land Surface Temperature and Emissivity Instantaneous L2
> Global 70 m v002* [Dataset]. NASA Land Processes Distributed Active Archive Center.
> https://doi.org/10.5067/ECOSTRESS/ECO_L2T_LSTE.002
>
> Hook, S., & Halverson, G. (2024). *ECOSTRESS Tiled Evapotranspiration Instantaneous and Daytime L3 Global 70 m
> v002* [Dataset]. NASA Land Processes Distributed Active Archive Center.
> https://doi.org/10.5067/ECOSTRESS/ECO_L3T_JET.002
>
> Hook, S., & Halverson, G. (2024). *ECOSTRESS Tiled Evaporative Stress Index PT-JPL Instantaneous L4 Global 70 m
> v002* [Dataset]. NASA Land Processes Distributed Active Archive Center.
> https://doi.org/10.5067/ECOSTRESS/ECO_L4T_ESI.002

Columnas: `ecostress_mensual`: `lst_ecostress_c` (LSTE), `et_ecostress_mm_dia` (JET), `esi_ecostress` (ESI) y
`n_pasadas_ecostress`.

### 1.10 HLS Sentinel-2 (HLSS30) V2.0

| | |
|---|---|
| Nombre oficial | HLS Sentinel-2 Multi-spectral Instrument Surface Reflectance Daily Global 30m v2.0 |
| DOI | [10.5067/HLS/HLSS30.002](https://doi.org/10.5067/HLS/HLSS30.002) (`C2021957295-LPCLOUD`) |
| DAAC | LP DAAC: 2015–2019 de LP DAAC y desde 2020 de Planetary Computer (`hls2-s30`) |

> Neigh, C., Ju, J., Roger, J.-C., Skakun, S., Vermote, E., Claverie, M., Dungan, J., Yin, Z., Freitag, B., &
> Justice, C. (2021). *HLS Sentinel-2 Multi-spectral Instrument Surface Reflectance Daily Global 30m v2.0*
> [Dataset]. NASA Land Processes Distributed Active Archive Center. https://doi.org/10.5067/HLS/HLSS30.002

Columnas: en `lotes`, las filas de `vegetacion_px_obs` con `producto` HLS (`refl_*`, `ndvi`, `evi2`, `gcvi`,
`ndmi`, `qa_valor`) y su aporte a `vegetacion_px_anual`.

HLSL30 (HLS Landsat, [10.5067/HLS/HLSL30.002](https://doi.org/10.5067/HLS/HLSL30.002)) **no se usa**: para Landsat
usamos C2 L2 de USGS.

### 1.11 No se usaron (están en el plan, pero no en los CSV)

| Producto | DOI | Por qué no |
|---|---|---|
| MOD16A2 V061 | [10.5067/MODIS/MOD16A2.061](https://doi.org/10.5067/MODIS/MOD16A2.061) | Lo reemplazó NLDAS-2 Noah (`docs/datasets/vegetacion.md`, Supuestos) |
| MCD12Q1 V061 | [10.5067/MODIS/MCD12Q1.061](https://doi.org/10.5067/MODIS/MCD12Q1.061) | La máscara agrícola sale del CDL |
| GRACEDADM_CLSM025GL_7D V3.0 (global) | [10.5067/SZYMDFZ7TJ4H](https://doi.org/10.5067/SZYMDFZ7TJ4H) | Se eligió la versión de EE.UU. |

No hay que citarlos, salvo que la entrega los mencione.

## 2. Fuentes que no son de la NASA

| Fuente | Organismo | Cita recomendada | Licencia | Columnas |
|---|---|---|---|---|
| Landsat 4-5 TM, 7 ETM+ y 8-9 OLI/TIRS Collection 2 Level-2 | **USGS** (misión USGS–NASA; lo distribuye USGS EROS) | Earth Resources Observation and Science (EROS) Center. (2020). *Landsat 4-5 Thematic Mapper Level-2, Collection 2* [Dataset]. U.S. Geological Survey. https://doi.org/10.5066/P9IAXOVV · (1999). *Landsat 7 Enhanced Thematic Mapper Plus Level-2, Collection 2*. https://doi.org/10.5066/P9C7I13B · (2013). *Landsat 8-9 Operational Land Imager / Thermal Infrared Sensor Level-2, Collection 2*. https://doi.org/10.5066/P9OGBGM6 | dominio público (USGS) | `teledeteccion_anual` (todas); en `lotes`, `vegetacion_px_obs` y `vegetacion_px_anual` (filas Landsat), `suelo_desnudo_px*` |
| USGS 3D Elevation Program (3DEP), DEM a 1/3" o lidar a 1 m, remuestreado a 10 m | **USGS** | USGS no exige un formato: pide autor (U.S. Geological Survey), año de publicación y título del producto (p. ej. *3DEP 1-Meter Resolution Digital Elevation Model* o *1/3rd arc-second DEM*), versión de los metadatos, fecha de acceso y URL. No hay DOI por producto. Fuente: [FAQ de The National Map](https://www.usgs.gov/faqs/how-should-i-cite-datasets-and-services-national-map) (vía buscador; la página devuelve 403 a descargas automáticas) | dominio público (USGS) | `lotes:relieve_3dep_m`; en `terreno_px`, `*_3dep*` |
| Annual NLCD Collection 1 (LndCov, FctImp) | **USGS** | United States Geological Survey. (2024). *Annual National Land Cover Database (NLCD) Collection 1 Products (ver. 1.2, June 2026)* [Dataset]. U.S. Geological Survey. https://doi.org/10.5066/P94UXNTS | dominio público (USGS) | `paisaje_anual` (todas) |
| NASS Quick Stats (SURVEY): rendimiento, superficie, producción y precios | **USDA NASS** | USDA National Agricultural Statistics Service, Quick Stats (https://quickstats.nass.usda.gov), consultado AAAA-MM-DD. No hay DOI | dominio público (gobierno de EE.UU.) | `produccion_anual`; precios en `economia_anual` y `economia_forrajes_anual` |
| NASS Crop Progress (Quick Stats) | **USDA NASS** | igual que Quick Stats | dominio público | `fenologia_estado` |
| Censo Agropecuario 2012, 2017 y 2022 (Quick Stats CENSUS) | **USDA NASS** | USDA NASS, Census of Agriculture (año), vía Quick Stats, consultado AAAA-MM-DD | dominio público | `practicas_censo`; `lotes:pct_riego_condado` |
| Cropland Data Layer (CDL) 30 m y 10 m | **USDA NASS** | "United States Department of Agriculture (USDA) National Agricultural Statistics Service (NASS), 20260227, Cropland Data Layer: USDA NASS, USDA NASS Marketing and Information Services Office, Washington, D.C." (metadatos FGDC del CDL) | "public domain and free to redistribute" | `rotacion_anual`; en `lotes`, `cultivo_px_anual` y `lotes_anual:cultivo_principal…`; máscaras agrícolas |
| Crop Sequence Boundaries (CSB) 2018–2025 | **USDA NASS** | La página de NASS no da cita. Código: Hunt, K. A., & Beeson, P. C. (2024). *Crop Sequence Boundaries* (v2024) [Software]. Zenodo. https://doi.org/10.5281/zenodo.14004209 | la página no declara licencia (obra del gobierno de EE.UU.) | `rotacion_secuencia`; en `lotes`, la geometría y `cultivo_csb` |
| Commodity Costs and Returns | **USDA ERS** | "U.S. Department of Agriculture, Economic Research Service. Commodity Costs and Returns data." (Recommended Citation de la [documentación de ERS](https://www.ers.usda.gov/data-products/commodity-costs-and-returns/documentation)); agregar fecha de acceso | dominio público | `economia_anual`: `valor_produccion_usd_ac`, `costo_*`, `margen_operativo_usd_ac` |
| SSURGO, vía Soil Data Access | **USDA NRCS** | "Soil Survey Staff, Natural Resources Conservation Service, United States Department of Agriculture. Soil Survey Geographic (SSURGO) Database. Available online at https://sdmdataaccess.sc.egov.usda.gov. Accessed [month/day/year]." | dominio público | `suelo_terreno_estatico` (salvo las del DEM); en `lotes`, `suelo_px` y `suelo_mukey` |
| Cartographic Boundary Files 2024, 1:500k | **US Census Bureau** | No se encontró una cita propia de los Cartographic Boundary Files. La [documentación técnica de TIGER/Line 2024](https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2024/TGRSHP2024_TechDoc.pdf) sugiere "2024 TIGER/Line Shapefiles (machine-readable data files) / prepared by the U.S. Census Bureau, 2024"; por analogía: "2024 Cartographic Boundary Files, 1:500,000 (machine-readable data files) / prepared by the U.S. Census Bureau, 2024" (adaptación nuestra) | dominio público | `condados.csv`, `condados.gpkg` |
| Crop-CASMA (servicio de SMAP L4 diario) | **USDA NASS** y George Mason University CSISS (con financiamiento de la NASA) | Zhang, C., Yang, Z., Zhao, H., Sun, Z., Di, L., Bindlish, R., Liu, P.-W., Colliander, A., Mueller, R., Crow, W., Reichle, R. H., Bolten, J., & Yueh, S. (2022). Crop-CASMA: A web geoprocessing and map service based architecture and implementation for serving soil moisture and crop vegetation condition data over U.S. Cropland. *International Journal of Applied Earth Observation and Geoinformation*, 112, 102902. https://doi.org/10.1016/j.jag.2022.102902 (verificado por doi.org/Crossref) | servicio público | el mismo dato que §1.3 |
| PRISM AN, mensual, 4 km | **Oregon State University** | "PRISM Group, Oregon State University, https://prism.oregonstate.edu, accessed DD Mon YYYY." | libre reproducción y distribución, con copyright de PRISM Group | `validacion_mensual`: `*_prism_*` |
| CoCoRaHS | **Colorado Climate Center** (red de voluntarios) | No hay formato fijo: la [Data Usage Policy](https://www.cocorahs.org/content.aspx?page=datausagepolicy) pide "acknowledge its source when displaying it". Propuesta: Community Collaborative Rain, Hail and Snow Network (CoCoRaHS), Colorado Climate Center, https://www.cocorahs.org, consultado AAAA-MM-DD | CC BY 4.0 ("Unless otherwise noted, all CoCoRaHS content and data are released under a Creative Commons Attribution 4.0 License") | `validacion_mensual`: `prec_cocorahs_mm` y `n_estaciones_cocorahs` |
| AgTile-US | académica (NCAR / Univ. of Kentucky) | Valayamkunnath, P., Barlage, M., Chen, F., Gochis, D., & Franz, K. (2020). *AgTile-US* [Dataset]. figshare. https://doi.org/10.6084/m9.figshare.11825742 | según figshare (no verificada) | en `lotes`, `drenaje_px:drenado_canos` |

Fuentes:
- CMR, colecciones de cada producto: [cmr.earthdata.nasa.gov/search](https://cmr.earthdata.nasa.gov/search/collections.umm_json), consultado 2026-11-15
- Citas APA por negociación de contenido en [doi.org](https://doi.org) (DataCite), consultado 2026-11-15
- [NASA EOSDIS Data Use Policy](https://earthdata.nasa.gov/earth-observation-data/data-use-policy), consultado 2026-11-15
- [POWER Referencing](https://power.larc.nasa.gov/docs/referencing/), consultado 2026-11-15
- [NSIDC SPL4SMGP V8](https://nsidc.org/data/spl4smgp/versions/8), consultado 2026-11-15
- [GES DISC data guidelines](https://disc.gsfc.nasa.gov/data-guidelines), consultado 2026-11-15 (citado desde CMR)
- [Metadatos FGDC del CDL / FAQ](https://www.nass.usda.gov/Research_and_Science/Cropland/sarsfaqs2.php), consultado 2026-11-15
- [NASS Crop Sequence Boundaries](https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php) y [Zenodo 14004209](https://zenodo.org/records/14004209), consultado 2026-11-15
- [Soil Data Access, Citation](https://sdmdataaccess.sc.egov.usda.gov/Citation.htm), consultado 2026-11-15
- [PRISM Terms of Use](https://prism.oregonstate.edu/terms/), consultado 2026-11-15
- [Crop-CASMA, metadatos NASS](https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_cropcasma.htm), consultado 2026-11-15 (vía buscador)
- Data cards del repo: `docs/datasets/*.md`
- Agregadas en T043, consultadas el 2026-11-15:
  - [POWER, metodología meteorológica (IMERG)](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/)
  - CMR: gránulos de `GPM_3IMERGDF`/`GPM_3IMERGDL` V07 y colecciones `SPL4SMGP` V007/V008
  - [Crop-CASMA, guía de usuario](https://nassgeo.csiss.gmu.edu/Crop-CASMA-User/user/data/) y [revisiones](https://nassgeo.csiss.gmu.edu/Crop-CASMA-Developer/about/revision/)
  - [Zhang et al. 2022, DOI](https://doi.org/10.1016/j.jag.2022.102902)
  - [ERS, documentación de Commodity Costs and Returns](https://www.ers.usda.gov/data-products/commodity-costs-and-returns/documentation)
  - [CoCoRaHS, Data Usage Policy](https://www.cocorahs.org/content.aspx?page=datausagepolicy)
  - [TIGER/Line 2024, documentación técnica](https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2024/TGRSHP2024_TechDoc.pdf)
  - [USGS, cómo citar The National Map](https://www.usgs.gov/faqs/how-should-i-cite-datasets-and-services-national-map), vía buscador

Confianza:
- **Alta** para los DOIs, títulos y versiones de los productos de la NASA (salen de CMR y DataCite), y para las
  citas de POWER, SMAP V8, SSURGO, CDL, PRISM, Landsat y NLCD (página oficial o DOI).
- **Alta** para la corrida de IMERG (Final hasta 2025-09-30 y Late después), que sale de la documentación de
  POWER y de CMR, y para el DOI del paper de Crop-CASMA y la cita de ERS.
- **Media** para la versión de SMAP (V008 seguro desde 2025-07-04; antes, sin confirmar) y de GRACE-DA-DM.
- **Media** para 3DEP y CoCoRaHS: la guía oficial no fija un formato. **Baja** para Census: es una adaptación de la
  cita de TIGER/Line.

Impacto:
- Ningún archivo de `config/` ni de `src/`.
- Sirve para la sección de fuentes de la entrega de Space Apps y para el frontend (paneles de fuentes NASA).
- T043 agregó los DOI a los data cards de `agua`, `clima`, `vegetacion`, `nldas`, `ecostress` y `suelo_terreno`
  (y a los generadores `src/<paquete>/data_card.py` o `process.py`), y el uso de la IMERG Late como problema
  conocido de `clima`.
