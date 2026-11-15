# Productos NASA: nombres exactos de SMAP L4, GRACE-DA-DM e IMERG en Earth Engine

Pregunta: Nombres exactos de productos y capas: SMAP L4, GRACE-DA-DM (global o EE.UU.; variables y fecha de inicio), IDs de IMERG en Earth Engine.

Respuesta corta: **SMAP L4**: el producto es `SPL4SMGP` ("SMAP L4 Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture Geophysical Data"), versión vigente **8** (`008`, DOI 10.5067/T5RUATAQREF8), desde el **2015-03-31**, cada 3 h, 9 km en EASE-Grid 2.0 (EPSG:6933); las capas que pide el plan son `sm_surface` (0–5 cm) y `sm_rootzone` (0–100 cm), en fracción volumétrica (m³/m³). En Earth Engine es `NASA/SMAP/SPL4SMGP/008` (la `007` quedó reemplazada). **GRACE-DA-DM**: hay dos productos en GES DISC con las mismas tres variables, `gws_inst` (percentil de agua subterránea), `rtzsm_inst` (percentil de humedad de la zona radicular) y `sfsm_inst` (percentil de humedad superficial), en %: la versión global `GRACEDADM_CLSM025GL_7D` V3.0 (0,25°, desde el **2003-02-03**) y la de EE.UU. `GRACEDADM_CLSM0125US_7D` V4.0 (0,125°, desde el **2002-04-01**, CONUS 25–53° N, 125–67° O). Para el Corn Belt conviene la de **EE.UU.**: el doble de resolución, forzada con NLDAS-2 y un año más de serie. Los datos son semanales (lunes). **IMERG en Earth Engine**: `NASA/GPM_L3/IMERG_V07` (cada 30 min, banda `precipitation` en mm/h, desde 1998-01-01) y `NASA/GPM_L3/IMERG_MONTHLY_V07` (mensual); `NASA/GPM_L3/IMERG_V06` está obsoleta. Earth Engine **no tiene un IMERG diario**: el `GPM_3IMERGDF` del plan (Final diario V07, 0,1°, variable `precipitation` en mm/día) solo está en GES DISC, con login de Earthdata; en Earth Engine habría que sumar las 48 medias horas del día (mm/h × 0,5 h).

Detalle:

**1. SMAP L4 (`SPL4SMGP`).**

| Atributo | Valor | Fuente |
|---|---|---|
| Nombre corto (NSIDC / CMR) | `SPL4SMGP` | NSIDC, CMR |
| Título | SMAP L4 Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture Geophysical Data, Version 8 | NSIDC |
| Versión vigente | 8 (`008` en CMR) | NSIDC, CMR |
| DOI | 10.5067/T5RUATAQREF8 | NSIDC, CMR |
| Cobertura temporal | 31 de marzo de 2015 al presente | NSIDC ("31 March 2015 to present"); CMR `BeginningDateTime` 2015-03-31 |
| Resolución | 3 h (medias de 3 horas), 9 km | NSIDC |
| Grilla | WGS 84 / NSIDC EASE-Grid 2.0 Global (EPSG:6933) | NSIDC |
| Formato | HDF5 | NSIDC |
| Capas | `sm_surface` (0–5 cm), `sm_rootzone` (0–100 cm), `sm_profile` (perfil hasta la roca), `sm_surface_wetness`, entre otras | Catálogo de Earth Engine |
| Unidad | fracción volumétrica (rango del catálogo 0–0,9) | Catálogo de Earth Engine |
| Earth Engine | `ee.ImageCollection("NASA/SMAP/SPL4SMGP/008")`, cada 3 h, píxel declarado de 11.000 m; `NASA/SMAP/SPL4SMGP/007` está marcado "superseded by NASA/SMAP/SPL4SMGP/008" | Catálogo de Earth Engine |

Los otros dos productos L4_SM son `SPL4SMAU` (actualizaciones del análisis, instantáneos, diagnósticos de asimilación) y `SPL4SMLM` (constantes del modelo, por ejemplo porosidad); para el paquete `agua` alcanza con `SPL4SMGP`. NSIDC avisa en la página del producto que los datos estándar y de tiempo casi real tuvieron un problema de geolocalización del 14 de mayo al 28 de julio de 2026 (fuera del período 2000–2025 del proyecto).

**2. GRACE-DA-DM (GRACE Data Assimilation for Drought Monitoring).**

| Atributo | Global | EE.UU. |
|---|---|---|
| Nombre corto | `GRACEDADM_CLSM025GL_7D` | `GRACEDADM_CLSM0125US_7D` |
| Versión | 3.0 | 4.0 (reemplaza a la 2.0) |
| Título | Groundwater and Soil Moisture Conditions from GRACE and GRACE-FO Data Assimilation L4 7-days 0.25 x 0.25 degree Global V3.0 | … 7-days 0.125 x 0.125 degree U.S. V4.0 |
| Resolución | 0,25° | 0,125° |
| Extensión | 60° S–90° N, global | 25–53° N, 125–67° O (CONUS) |
| Inicio | 2003-02-03 (CMR; "February 2003" en el resumen) | 2002-04-01 |
| Paso | 7 días: dato diario, publicado un día (lunes) por semana | ídem |
| Forzante meteorológico | ECMWF (deriva de `GLDAS_CLSM025_DA1_D`) | NLDAS-2 |
| Modelo | Catchment (CLSM) Fortuna 2.5, asimilación de GRACE/GRACE-FO RL06 (mascons de la UT Austin) | ídem |
| Variables | `gws_inst`, `rtzsm_inst`, `sfsm_inst` (%) | `gws_inst`, `rtzsm_inst`, `sfsm_inst` (%) |
| Climatología del percentil | 1948–2014 | 1948–2014 |
| Formato | netCDF (`.nc4`) | netCDF (`.nc4`), ejemplo `GRACEDADM_CLSM0125US_7D.A20020401.040.nc4` |
| Latencia (archivo final GES DISC) | 3 a 6 meses | 3 a 6 meses |
| Landing page | `https://disc.gsfc.nasa.gov/datacollection/GRACEDADM_CLSM025GL_7D_3.0.html` | `https://disc.gsfc.nasa.gov/datacollection/GRACEDADM_CLSM0125US_7D_4.0.html` |

Recomendación: **versión EE.UU. (`GRACEDADM_CLSM0125US_7D`)**. Cubre todo el Corn Belt, tiene celdas de 0,125° (≈ 14 km, unas 4 veces más celdas por condado que la global) y la meteorología de NLDAS-2, más densa en EE.UU. que la de ECMWF. La global solo tendría sentido para comparar con otras regiones.

Variables: en el README de las dos versiones la tabla de variables es `gws_inst` (Groundwater [Storage] Percentile, %), `rtzsm_inst` (Root Zone Soil Moisture Percentile, %) y `sfsm_inst` (Surface Soil Moisture Percentile, %). Los archivos que ya bajó el paquete `agua` desde el servidor público del proyecto (`nasagrace.unl.edu`) tienen esas mismas tres variables, pero el atributo `version` dice `030` y el nombre termina en `.030.nc4`; los de GES DISC V4.0 terminan en `.040.nc4`. O sea: la copia operativa de la UNL (2 a 9 días de latencia) no es necesariamente idéntica al archivo final V4.0 de GES DISC (que se regenera cuando llegan los datos finales de GRACE-FO). Además, en esos archivos el relleno es `missing_value = -999.0` (hay que pasarlo a vacío).

**3. IMERG en Google Earth Engine.**

| ID de la colección | Paso | Disponibilidad (catálogo, consultado 2026-11-14) | Estado |
|---|---|---|---|
| `NASA/GPM_L3/IMERG_V07` | 30 min | desde 1998-01-01 (hasta días antes de la consulta) | vigente |
| `NASA/GPM_L3/IMERG_MONTHLY_V07` | mensual | 1998-01-01 a 2025-09-01 | vigente |
| `NASA/GPM_L3/IMERG_V06` | 30 min | 2000-06-01 a 2024-06-02 | obsoleta: "superseded by NASA/GPM_L3/IMERG_V07" |

Bandas de `IMERG_V07`: `precipitation` (mm/h, "snapshot precipitation - calibrated"), `precipitationUncal`, `MWprecipitation`, `IRprecipitation`, `IRinfluence`, `probabilityLiquidPrecipitation`, `MWprecipSource`, entre otras; resolución nominal 11.132 m (0,1°).

En Earth Engine no hay una colección diaria de IMERG: para replicar `GPM_3IMERGDF` hay que agregar `IMERG_V07` por día (media de `precipitation` en mm/h × 24, que es lo que hace el producto diario de GES DISC), con cuidado de usar el día UTC. Esta colección de Earth Engine mezcla corridas: el catálogo dice que los productos se actualizan de provisorios a permanentes; no se pudo confirmar si los datos recientes son Final o Late.

**4. IMERG Final diario en GES DISC (`GPM_3IMERGDF`).** Título "GPM IMERG Final Precipitation L3 1 day 0.1 degree x 0.1 degree V07"; versión 07 (las anteriores ya no están disponibles); variable `precipitation` en mm/día, calculada como la media de las medias horas válidas (mm/h) multiplicada por 24. CMR registra la cobertura 1998-01-01 a 2025-09-30 (al 2026-11-14; la latencia del Final diario es de unos 4 meses, porque depende de que salga el Final de media hora). Para completar octubre–diciembre de 2025 habría que usar la corrida Late diaria (`GPM_3IMERGDL`) o esperar. Requiere login de Earthdata; esta corrida no tiene esa credencial, así que no se probó la descarga.

Fuentes: [NASA/GPM_L3/IMERG_V07 – Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07), consultado 2026-11-14; [NASA/GPM_L3/IMERG_MONTHLY_V07 – Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_MONTHLY_V07), consultado 2026-11-14; [NASA/GPM_L3/IMERG_V06 (deprecated) – Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V06), consultado 2026-11-14; [NASA/SMAP/SPL4SMGP/008 – Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_SMAP_SPL4SMGP_008), consultado 2026-11-14; [SMAP L4 Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture Geophysical Data, Version 8 (NSIDC)](https://nsidc.org/data/spl4smgp/versions/8), consultado 2026-11-14; [README GRACE-DA-DM Global V3.0 (GES DISC)](https://docserver.gesdisc.eosdis.nasa.gov/public/project/hydrology/README_GRACEDADM3GL.pdf), consultado 2026-11-14; [README GRACE-DA-DM U.S. V4.0 (GES DISC)](https://docserver.gesdisc.eosdis.nasa.gov/public/project/hydrology/README_GRACEDADM4.pdf), consultado 2026-11-14; [CMR: GRACEDADM_CLSM025GL_7D](https://cmr.earthdata.nasa.gov/search/collections.umm_json?short_name=GRACEDADM_CLSM025GL_7D), consultado 2026-11-14; [CMR: GRACEDADM_CLSM0125US_7D](https://cmr.earthdata.nasa.gov/search/collections.umm_json?short_name=GRACEDADM_CLSM0125US_7D), consultado 2026-11-14; [CMR: SPL4SMGP](https://cmr.earthdata.nasa.gov/search/collections.umm_json?short_name=SPL4SMGP), consultado 2026-11-14; [CMR: GPM_3IMERGDF](https://cmr.earthdata.nasa.gov/search/collections.umm_json?short_name=GPM_3IMERGDF), consultado 2026-11-14

Confianza: alta (nombres, versiones, variables y fechas de inicio salen de los metadatos oficiales: NSIDC, CMR, READMEs de GES DISC y catálogo de Earth Engine). Media para la recomendación de usar GRACE-DA-DM EE.UU. (es un criterio, no un dato de la fuente) y para la diferencia entre la versión `030` de nasagrace.unl.edu y la V4.0 de GES DISC (no hay un documento que la explique).

Impacto: paquete `agua` (SMAP `SPL4SMGP` v008 con `sm_surface` y `sm_rootzone`; GRACE-DA-DM EE.UU. `GRACEDADM_CLSM0125US_7D` con `gws_inst`, `rtzsm_inst`, `sfsm_inst`, como ya usa el data card; documentar que la copia de la UNL es versión `030`). Paquete `clima` (`prec_imerg_mm`: `GPM_3IMERGDF` V07 en GES DISC requiere Earthdata; la alternativa en Earth Engine es `NASA/GPM_L3/IMERG_V07` agregada por día, porque no hay colección diaria). CLAUDE.md §6.1 y §6.4 (los nombres de producto del plan son correctos; agregar que GRACE-DA-DM conviene en su versión EE.UU.).

Citas:
> "gws_inst Groundwater Storage Percentile % rtzsm_inst Root Zone Soil Moisture Percentile % sfsm_inst Surface Soil Moisture Percentile %" — [README GRACE-DA-DM Global V3.0 (GES DISC)](https://docserver.gesdisc.eosdis.nasa.gov/public/project/hydrology/README_GRACEDADM3GL.pdf)
> "0.125 degree over North America and range from April 1, 2002 to present" — [README GRACE-DA-DM U.S. V4.0 (GES DISC)](https://docserver.gesdisc.eosdis.nasa.gov/public/project/hydrology/README_GRACEDADM4.pdf)
> "Filename example: GRACEDADM_CLSM0125US_7D.A20020401.040.nc4" — [README GRACE-DA-DM U.S. V4.0 (GES DISC)](https://docserver.gesdisc.eosdis.nasa.gov/public/project/hydrology/README_GRACEDADM4.pdf)
> "temporal range from February 2003 to present (with a 3-6 month latency)" — [CMR: GRACEDADM_CLSM025GL_7D](https://cmr.earthdata.nasa.gov/search/collections.umm_json?short_name=GRACEDADM_CLSM025GL_7D)
> "Temporal Coverage: 31 March 2015 to present" — [SMAP L4 Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture Geophysical Data, Version 8 (NSIDC)](https://nsidc.org/data/spl4smgp/versions/8)
> "sm_rootzone Volume fraction 0 0.9 11000 meters Root zone soil moisture (0-100 cm)" — [NASA/SMAP/SPL4SMGP/008 – Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_SMAP_SPL4SMGP_008)
> "sm_surface Volume fraction 0 0.9 11000 meters Top layer soil moisture (0-5 cm)" — [NASA/SMAP/SPL4SMGP/008 – Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_SMAP_SPL4SMGP_008)
> "ee.ImageCollection("NASA/GPM_L3/IMERG_V07")" — [NASA/GPM_L3/IMERG_V07 – Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07)
> "Dataset Availability 1998-01-01T00:00:00Z" — [NASA/GPM_L3/IMERG_V07 – Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07)
> "ee.ImageCollection("NASA/GPM_L3/IMERG_MONTHLY_V07")" — [NASA/GPM_L3/IMERG_MONTHLY_V07 – Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_MONTHLY_V07)
> "This dataset has been superseded by NASA/GPM_L3/IMERG_V07" — [NASA/GPM_L3/IMERG_V06 (deprecated) – Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V06)
> "The daily mean rate (mm/day) is derived by first computing the mean precipitation rate (mm/hour) in a grid cell for the data day, and then multiplying the result by 24." — [CMR: GPM_3IMERGDF](https://cmr.earthdata.nasa.gov/search/collections.umm_json?short_name=GPM_3IMERGDF)
