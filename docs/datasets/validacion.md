# Data card — validacion

Datos de superficie (no NASA) para validar la lluvia y la temperatura de NASA POWER y GPM IMERG
del paquete `clima`: PRISM (Oregon State University) y CoCoRaHS (red de pluviómetros voluntarios).

<!-- ATRIBUCION:INICIO -->
## Atribución

Texto obligatorio al distribuir o mostrar estos datos (copiar tal cual; ver `docs/research/licencias_fuentes.md`):

> Community Collaborative Rain, Hail and Snow Network (CoCoRaHS), Colorado Climate Center, https://www.cocorahs.org. Licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Data aggregated to county-month by the team.
<!-- ATRIBUCION:FIN -->

## Archivos

- `data/processed/validacion/validacion_mensual.csv` → `fips, anio, mes, prec_prism_mm, tmax_prism_c, tmin_prism_c, tmed_prism_c, prec_cocorahs_mm, n_estaciones_cocorahs`.
  Una fila por condado y mes, 2000-01 a 2025-12 (91416 filas).
- Insumos en raw: 1248 zips mensuales de PRISM y 648 exports mensuales de CoCoRaHS.

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| validacion_mensual.csv | prec_prism_mm | Lluvia total del mes, media de las celdas PRISM de 4 km cuyo centro cae en el condado | mm | PRISM AN monthly 4 km (Oregon State University) |  | 2000-01 | 2025-12 | 0.00 |
| validacion_mensual.csv | tmax_prism_c | Temperatura máxima media del mes, media por condado | °C | PRISM AN monthly 4 km (Oregon State University) |  | 2000-01 | 2025-12 | 0.00 |
| validacion_mensual.csv | tmin_prism_c | Temperatura mínima media del mes, media por condado | °C | PRISM AN monthly 4 km (Oregon State University) |  | 2000-01 | 2025-12 | 0.00 |
| validacion_mensual.csv | tmed_prism_c | Temperatura media del mes (tmean de PRISM = (tmax + tmin) / 2), media por condado | °C | PRISM AN monthly 4 km (Oregon State University) |  | 2000-01 | 2025-12 | 0.00 |
| validacion_mensual.csv | prec_cocorahs_mm | Lluvia del mes: media entre las estaciones del condado con al menos 25 reportes diarios en el mes (suma de los días reportados, pulgadas × 25,4) | mm | CoCoRaHS daily reports (export público) |  | 2008-01 | 2025-12 | 53.18 |
| validacion_mensual.csv | n_estaciones_cocorahs | Estaciones CoCoRaHS del condado con al menos 25 reportes diarios en el mes (0 = ninguna; vacío antes de 2008) | estaciones | CoCoRaHS daily reports (export público) |  | 2008-01 | 2025-12 | 30.77 |

## Validación de POWER e IMERG (mensual, por condado)

| comparacion | unidad | n_condado_mes | sesgo_medio | rmse | correlacion_pearson |
|---|---|---|---|---|---|
| Lluvia POWER vs PRISM | mm/mes | 91416 | -3.54 | 18.65 | 0.944 |
| Lluvia IMERG vs PRISM | mm/mes | 91416 | 5.62 | 20.81 | 0.932 |
| Lluvia POWER vs CoCoRaHS | mm/mes | 42798 | -1.50 | 24.02 | 0.907 |
| Lluvia IMERG vs CoCoRaHS | mm/mes | 42798 | 7.63 | 27.08 | 0.890 |
| Tmax POWER vs PRISM | °C | 91416 | -0.07 | 0.96 | 0.996 |
| Tmin POWER vs PRISM | °C | 91416 | 0.41 | 0.93 | 0.996 |
| Tmed POWER vs PRISM | °C | 91416 | 0.06 | 0.74 | 0.998 |

Sesgo = fuente NASA − referencia de superficie, sobre todos los pares condado-mes con dato en las dos.

## Supuestos

- PRISM: se usa el directorio HTTP público `https://data.prism.oregonstate.edu/time_series/us/an/4km/<var>/monthly/<anio>/`
  (mismos archivos que el servicio web `services.nacse.org/prism/data/get/us/4km/...`, que limita a dos descargas por
  archivo por día). Serie AN (todas las estaciones), 4 km (`25m` = 2,5 minutos de arco), un zip por variable y mes,
  bajados de a tres a la vez. PRISM es de uso no comercial y pide cita: PRISM Group, Oregon State University,
  https://prism.oregonstate.edu.
- Media por condado de las celdas de 4 km cuyo centro cae dentro del polígono (rasterización de `condados.gpkg`
  en la grilla de PRISM). No se aplica la máscara agrícola: es una referencia del clima del condado, comparable con
  el centroide de POWER y la media de IMERG. Los meses de 2025 pueden ser provisionales en PRISM.
- `tmed_prism_c` es la variable `tmean` de PRISM (que PRISM define como (tmax + tmin) / 2).
- CoCoRaHS: export público `data.cocorahs.org/export/exportreports.aspx` (ReportType=Daily, CSV) por estado y mes,
  desde 2008 (como pide el contrato). Las estaciones se ubican por la mediana de sus coordenadas y se asignan al
  condado por unión espacial con `condados.gpkg` (solo estaciones de los estados del config).
- CoCoRaHS: `T` (traza) = 0; `NA` = sin dato. Un reporte por estación y fecha de observación (se queda el primero si
  hay duplicados). Los informes de varios días (Multi-Day) no se bajaron: esos días cuentan como no reportados.
- Lluvia mensual de una estación = suma de sus reportes diarios del mes, sin escalar por los días faltantes; solo
  estaciones con al menos 25 reportes. La del condado es la media de esas estaciones. Sin estaciones válidas:
  `prec_cocorahs_mm` vacío y `n_estaciones_cocorahs` = 0. Antes de 2008, ambas vacías.
- La tabla de validación usa `data/processed/clima/clima_mensual.csv` (paquete `clima`, dueño Persona 1).

## Problemas conocidos

- La lluvia de CoCoRaHS subestima el total del mes en las estaciones con 25 a 30 reportes (días sin reporte no se
  rellenan). La nieve se mide como equivalente en agua cuando el observador lo carga: en invierno hay más huecos.
- POWER es un valor puntual en el centroide (grilla de 0,5°), PRISM una media areal a 4 km y CoCoRaHS la media de
  pocos pluviómetros: las diferencias mezclan error de cada fuente y de representatividad espacial.
