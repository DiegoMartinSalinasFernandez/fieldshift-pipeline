# Data card — agua

Paquete `agua` de Field Shift (CLAUDE.md §6.4): humedad del suelo y agua subterránea por condado del Corn Belt.

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| agua_diario.csv | sm_surface_m3m3 | Humedad volumétrica del suelo superficial (0-5 cm), media del condado ponderada por área | m3/m3 | NASA SMAP L4 SPL4SMGP 9 km, capas diarias de Crop-CASMA (USDA NASS / GMU) | S02 | 2015-03-31 | 2025-12-31 | 0.0 |
| agua_diario.csv | sm_rootzone_m3m3 | Humedad volumétrica de la zona radicular (0-100 cm), media del condado ponderada por área | m3/m3 | NASA SMAP L4 SPL4SMGP 9 km, capas diarias de Crop-CASMA (USDA NASS / GMU) | S03 | 2015-03-31 | 2025-12-31 | 0.0 |
| agua_mensual.csv | sm_surface_m3m3 | Media mensual de sm_surface diaria (solo meses completos) | m3/m3 | NASA SMAP L4 SPL4SMGP 9 km, capas diarias de Crop-CASMA (USDA NASS / GMU) | S02 | 2015-04 | 2025-12 | 0.8 |
| agua_mensual.csv | sm_rootzone_m3m3 | Media mensual de sm_rootzone diaria (solo meses completos) | m3/m3 | NASA SMAP L4 SPL4SMGP 9 km, capas diarias de Crop-CASMA (USDA NASS / GMU) | S03 | 2015-04 | 2025-12 | 0.8 |
| agua_mensual.csv | sm_surface_min_m3m3 | Mínimo mensual de sm_surface diaria | m3/m3 | NASA SMAP L4 SPL4SMGP 9 km, capas diarias de Crop-CASMA (USDA NASS / GMU) | S02 | 2015-04 | 2025-12 | 0.8 |
| agua_mensual.csv | sm_rootzone_min_m3m3 | Mínimo mensual de sm_rootzone diaria | m3/m3 | NASA SMAP L4 SPL4SMGP 9 km, capas diarias de Crop-CASMA (USDA NASS / GMU) | S03 | 2015-04 | 2025-12 | 0.8 |
| agua_mensual.csv | sm_rootzone_anom_z | (sm_rootzone del mes − media del mes calendario) / desvío, por condado, 2015-2025 | adim. | Derivada de SMAP L4 (Crop-CASMA) | D25 | 2015-04 | 2025-12 | 0.8 |
| agua_mensual.csv | dias_sm_saturado | Días del mes con sm_rootzone diaria del condado >= 0,40 m3/m3 | días | Derivada de SMAP L4 (Crop-CASMA) | D26 | 2015-04 | 2025-12 | 0.8 |
| agua_semanal.csv | gws_pctl | Percentil de almacenamiento de agua subterránea (media ponderada por área del condado) | percentil 0-100 | GRACE-DA-DM US (GRACEDADM_CLSM0125US_7D v030, nasagrace.unl.edu) | W01 | 2003-01-06 | 2025-12-29 | 0.0 |
| agua_semanal.csv | rtzsm_pctl | Percentil de humedad del suelo en la zona radicular (media ponderada por área) | percentil 0-100 | GRACE-DA-DM US (GRACEDADM_CLSM0125US_7D v030, nasagrace.unl.edu) | W02 | 2003-01-06 | 2025-12-29 | 0.0 |
| agua_semanal.csv | sfsm_pctl | Percentil de humedad del suelo superficial (media ponderada por área) | percentil 0-100 | GRACE-DA-DM US (GRACEDADM_CLSM0125US_7D v030, nasagrace.unl.edu) | W03 | 2003-01-06 | 2025-12-29 | 0.0 |

## Fuentes y acceso

- **DOI de los productos de la NASA:**
  - SMAP L4 `SPL4SMGP` Version 8 (NSIDC DAAC): https://doi.org/10.5067/T5RUATAQREF8. Crop-CASMA no
    informa la versión. Desde el 2025-07-04 es V8 seguro, porque la V7 termina el 2025-07-03 en CMR. Antes
    de esa fecha puede ser V7 (https://doi.org/10.5067/EVKPQZ4AFC4D) o la V8 reprocesada.
  - Servicio Crop-CASMA: Zhang et al. (2022), https://doi.org/10.1016/j.jag.2022.102902
  - GRACE-DA-DM EE.UU. V4.0 (`GRACEDADM_CLSM0125US_7D`, GES DISC): https://doi.org/10.5067/UH653SEZR9VQ
- Citas completas: `docs/research/citas_nasa.md`.

- **GRACE-DA-DM, versión solo EE.UU.** (`GRACEDADM_CLSM0125US_7D`, versión 030 en el nombre del
  archivo; atributo `version` = 040 dentro del archivo), 0,125°, semanal. NASA GSFC Hydrological Sciences
  Lab, modelo Catchment con asimilación de GRACE/GRACE-FO. Se bajó del servidor público del National
  Drought Mitigation Center, `https://nasagrace.unl.edu/data/<AAAAMMDD>/GRACEDADM_CLSM0125US_7D.A<AAAAMMDD>.030.nc4`
  (sin login). Un archivo por semana con `gws_inst`, `rtzsm_inst` y `sfsm_inst`.
- `src/agua/download.py` lista los directorios semanales hasta el `anio_fin` de `config/config.yaml`,
  baja a `.part` en `data/interim/agua/grace/` y mueve a `data/raw/agua/grace/` (reanudable). Una fila
  por archivo en `manifest.csv`.
- `src/agua/process.py` recorta la grilla a los condados y promedia cada variable por condado.

## Supuestos

- **SMAP L4 por Crop-CASMA.** Sin Earthdata no se usó AppEEARS/NSIDC: se usó el servicio WPS
  público de Crop-CASMA (USDA NASS con George Mason University y NASA), proceso `GetFileByFips`, capas
  `SMAP-9KM-DAILY-TOP_<AAAA.MM.DD>_013000` (superficie) y `SMAP-9KM-DAILY-SUB_<AAAA.MM.DD>_013000`
  (zona radicular), recortadas por estado (FIPS 17, 18, 19). GeoTIFF en EPSG:5070, 9 km, m3/m3.
  Se guardan tal cual en `data/raw/agua/smap/<anio>/`.
- Media diaria por condado ponderada por la fracción de área del condado en cada celda de 9 km
  (rasterizado a una grilla 10 veces más fina); cada condado usa el recorte de su propio estado.
  **No se aplicó la máscara agrícola** (celdas de 9 km mezclan usos).
- Se excluyen celdas con valores fuera de 0-0,60 m3/m3 (rango físico de la definición de terminado
  del plan) antes de promediar; afecta ~1,5 % de las filas diarias (en la primera tanda: suelos
  orgánicos del NE de Indiana y DuPage, IL).
- Mensual: solo meses con todos los días con dato; si falta un día, las columnas del mes quedan vacías.
  `anio` = año calendario del mes. El mes 2015-03 se omite (SMAP L4 empieza el 2015-03-31).
- `sm_rootzone_anom_z`: z por condado y mes calendario con todos los años 2015-2025 disponibles
  (desvío muestral, mínimo 3 años).
- **Umbral de saturación:** `dias_sm_saturado` cuenta días con `sm_rootzone_m3m3` (media diaria del
  condado) >= 0,40 m3/m3. Umbral fijo y provisorio, cercano al percentil 90 de la serie diaria del
  Corn Belt en 2015; en el Corn Belt el exceso de agua en primavera retrasa la siembra.

- Sin credencial de Earthdata no se usó GES DISC: se usó la copia pública de nasagrace.unl.edu del
  mismo producto. Se eligió la versión solo EE.UU. (0,125°) en lugar de la global
  (`GRACEDADM_CLSM025GL_7D`, 0,25°) porque tiene el doble de resolución y es la que publica el NDMC.
- `fecha` = fecha del nombre del archivo y del directorio (lunes de la semana del mapa del NDMC).
  La coordenada `time` interna del archivo es unos días anterior (ej. archivo A20240101 →
  `time` = 2023-12-26); se usó la del nombre porque es la que identifica el producto semanal.
- `anio` = año calendario de `fecha`.
- **Se omite 2002** (desde 2002-04-01 hay datos): los nc4 anteriores a 2020 pesan ~5 MB y el paquete
  quedaba sobre el límite de 5 GB en `data/raw/`. La serie empieza en 2003-01 (el contrato pide desde
  2003-02-01). Los archivos de 2002 quedaron en `data/interim/agua/grace_2002_fuera_de_raw/`.
- Media por condado ponderada por la fracción de área del condado en cada celda de 0,125°
  (rasterizando los polígonos de `data/reference/condados.gpkg` a una grilla 10 veces más fina).
  Celdas sin dato (`-999`, fuera de 0-100) se excluyen. **No se aplicó la máscara agrícola**: con
  celdas de ~14 km x 11 km casi todas mezclan usos y la máscara de 30 m no cambia el promedio.
- Los percentiles son relativos a la climatología del modelo (período de referencia sin verificar:
  queda para research `productos_nasa`); el promedio de percentiles entre celdas no es un percentil en sentido estricto, es un índice medio.

## Problemas conocidos

- **SMAP L4 no viene de NSIDC/AppEEARS** (requieren Earthdata Login, no configurada): se usó la copia
  de Crop-CASMA. No se pudo confirmar si la capa `SMAP-9KM-DAILY-*_<fecha>_013000` es la media
  diaria o el campo de las 01:30 UTC (el sufijo sugiere la hora); a validar contra `SPL4SMGP` cuando
  haya Earthdata. No es el producto 3-horario: no hay ciclo diario.
- Primera tanda: celdas de 9 km con valores > 0,60 m3/m3 (hasta ~0,92) en el noreste de Indiana (Allen, Whitley,
  Steuben, Jay, Miami) y DuPage (IL): suelos orgánicos o fracción de agua alta en el modelo. Se
  excluyen celda a celda (ver Supuestos); en esos condados la media usa menos celdas o queda vacía.
- `dias_sm_saturado` con umbral fijo de 0,40 m3/m3 (provisorio): en suelos con porosidad alta cuenta
  más días que en suelos arenosos. Mejor sería porosidad del modelo (`SPL4SMLM`) menos 0,05 m3/m3,
  que requiere Earthdata.
- SMAP 2015-03-31 a 2025-12-31 completo salvo **2016-12-15**: el WPS de Crop-CASMA responde
  `bad request` para las dos capas en IA, IL e IN (probado 3 veces en dos rondas; en otros estados, revisar
  si el día está en `agua_diario.csv`). Ese día queda
  sin fila en `agua_diario.csv` y diciembre de 2016 queda vacío en `agua_mensual.csv` (los meses
  incompletos no se agregan).
- `python src/agua/download.py` es reanudable: si una descarga se corta, completa lo que falta.
- El servidor de nasagrace.unl.edu limita la velocidad por conexión (~50 KB/s).
