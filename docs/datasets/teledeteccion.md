# Data card — teledeteccion

Paquete `teledeteccion` de Field Shift: Landsat a 30 m por condado del Corn Belt (lotes desnudos y cobertura invernal).

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| teledeteccion_anual.csv | pct_suelo_desnudo_abr_may | % de píxeles agrícolas muestreados con mediana de NDVI < 0,25 en abril–mayo | % | Landsat C2 L2 (USGS/NASA) vía Planetary Computer | F08 | 2019 | 2025 | 1.5 |
| teledeteccion_anual.csv | pct_suelo_desnudo_oct_nov | % de píxeles agrícolas muestreados con mediana de NDVI < 0,25 en octubre–noviembre | % | Landsat C2 L2 (USGS/NASA) vía Planetary Computer | F08 | 2019 | 2025 | 1.6 |
| teledeteccion_anual.csv | pct_cobertura_verde_mar_abr | % de píxeles agrícolas muestreados con mediana de NDVI >= 0,3 del 15-03 al 30-04 | % | Landsat C2 L2 (USGS/NASA) vía Planetary Computer |  | 2019 | 2025 | 2.9 |
| teledeteccion_anual.csv | bsi_abr_may | Media de la mediana por píxel del Bare Soil Index de abril–mayo | adim. | Landsat C2 L2 (USGS/NASA) vía Planetary Computer | H05 | 2019 | 2025 | 1.5 |
| teledeteccion_anual.csv | ndvi_max_30m | Media de los píxeles del NDVI máximo de abril–septiembre (30 m) | adim. | Landsat C2 L2 (USGS/NASA) vía Planetary Computer | H02 | 2019 | 2025 | 0.0 |
| teledeteccion_anual.csv | n_escenas_validas | Escenas leídas con al menos 10 % de los píxeles agrícolas muestreados despejados | escenas | Landsat C2 L2 (USGS/NASA) vía Planetary Computer |  | 2019 | 2025 | 0.0 |
| teledeteccion_anual.csv | frac_pixeles_validos | Observaciones despejadas / observaciones de píxeles agrícolas leídas en el año | fracción | Landsat C2 L2 (USGS/NASA) vía Planetary Computer | H06 | 2019 | 2025 | 0.0 |

## Método

- Fuente: Landsat Collection 2 Level-2 (reflectancia de superficie, 30 m), colección `landsat-c2-l2`
  del STAC de Microsoft Planetary Computer (sin login; token SAS anónimo). Escenas con
  `eo:cloud_cover` < 60 %. Se prefiere Landsat 8/9 (y 5); Landsat 7 (bandeado SLC-off desde 2003)
  solo entra si no hay otra escena en el período.
- Muestreo: por condado, 2 ventanas de 40 x 40 píxeles (1,2 x 1,2 km) en la grilla de
  `data/reference/mascara_agricola.tif` (EPSG:5070, 30 m), centradas en píxeles agrícolas elegidos al
  azar con semilla = fips (`data/interim/teledeteccion/ventanas.csv`). Hasta 3.200 píxeles por condado;
  solo cuentan los agrícolas y dentro del condado. Resolución efectiva: 30 m (Landsat reproyectado a
  EPSG:5070 con vecino más cercano). Hasta la ronda 1 (parte de 2025) se leyó con WarpedVRT; desde
  la ronda 2, leyendo la ventana UTM de origen (con 2 px de margen) y reproyectando en memoria,
  que baja 4 veces menos bytes. Las dos lecturas difieren en ~0,3 % de los píxeles (empates del
  vecino más cercano), sin efecto apreciable en las medias por condado.
- Escenas por condado y año (las más despejadas que cubren las dos ventanas): 1 del 15 al 31 de
  marzo, 2 de abril, 2 de mayo, 3 de julio–agosto y 3 de octubre–noviembre. Para cubrir antes
  todos los años, la descarga va por rangos: primero la escena más despejada de cada condado y
  período en todos los años (`TD_RANGO_MAX=1`, ~136 escenas por año) y después el resto.
- Se guardan en `data/raw/teledeteccion/landsat/<anio>/<escena>.npz` los DN originales (uint16) de
  las ventanas de blue, red, nir08, swir16 y qa_pixel. Desde la ronda 2, las escenas fuera de
  abril–mayo guardan solo red, nir08 y qa_pixel (el BSI solo se calcula en abril–mayo).
- Calidad: se descartan píxeles con QA_PIXEL de relleno, nube dilatada, cirro, nube, sombra, nieve
  o agua, sin el bit de despejado, o con reflectancia fuera del rango válido (DN 7273–43636).
  Escala: reflectancia = DN x 0,0000275 − 0,2.
- NDVI = (NIR − Rojo) / (NIR + Rojo). BSI = ((SWIR1 + Rojo) − (NIR + Azul)) / ((SWIR1 + Rojo) + (NIR + Azul)).
- Umbrales: suelo desnudo NDVI < 0,25; cobertura verde NDVI >= 0,3; escena válida si >= 10 % de los
  píxeles agrícolas muestreados están despejados.

## Supuestos

- Se usó Landsat C2 L2 de Planetary Computer en lugar de HLS (LP DAAC pide Earthdata, no
  configurada). Sentinel-2 todavía no se usa.
- Píxeles agrícolas = `mascara_agricola.tif` (cultivo agrícola en al menos un año del CDL), no el
  CDL de cada año: no hay máscara agrícola anual en `data/reference/`. Incluye lotes que en un año
  dado pudieron no estar cultivados.
- El muestreo por 2 ventanas por condado (no todo el condado) es una aproximación: representa
  ~2,9 km² por condado. Con más rondas se puede aumentar la cantidad de ventanas.
- Las medianas por período usan solo las escenas seleccionadas (no todas las disponibles); con
  `TD_RANGO_MAX=1` hay una sola escena por período y condado.
  `ndvi_max_30m` usa las escenas de abril, mayo y julio–agosto.
- `anio` es el año calendario de las escenas.

## Problemas conocidos

- Cobertura parcial: se bajan primero los años recientes (2025 hacia atrás); las filas de los años
  sin bajar no están en el CSV. Mientras un año no termine de bajarse, sus filas usan solo las
  escenas ya bajadas (en muchos años, solo la más despejada por período) y pueden cambiar cuando
  se completen: las medianas con una sola escena son el valor de esa escena.
- Nubes y nieve dejan períodos sin píxeles despejados: esas celdas van vacías.
- Landsat 7 SLC-off (2003+) deja franjas sin datos cuando es la única escena.
