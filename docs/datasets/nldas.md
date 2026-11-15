# Data card — nldas

NLDAS-2 (North American Land Data Assimilation System, fase 2), modelo de superficie Noah, producto
mensual `NLDAS_NOAH0125_M` versión 2.0 (NASA GES DISC, colección CMR `C1887990023-GES_DISC`),
grilla de 0,125°, desde 1979-01. Completa a SMAP (paquete `agua`), que empieza en 2015-03.

## Archivos

- `data/processed/nldas/nldas_mensual.csv` → `fips, anio, mes, ...` (`anio` = año calendario del mes),
  2000-01 a 2025-12, una fila por condado y mes.

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| nldas_mensual.csv | sm_0_10cm_m3m3 | Humedad volumétrica 0-10 cm: SoilM_0_10cm (kg m-2) / 100 mm, media ponderada del condado | m3/m3 | NLDAS-2 Noah mensual v2.0 (NLDAS_NOAH0125_M, NASA GES DISC por Harmony) | G01 | 2000-01 | 2025-12 | 0.00 |
| nldas_mensual.csv | sm_0_100cm_m3m3 | Humedad volumétrica 0-100 cm: SoilM_0_100cm (kg m-2) / 1000 mm, media ponderada del condado | m3/m3 | NLDAS-2 Noah mensual v2.0 (NLDAS_NOAH0125_M, NASA GES DISC por Harmony) | G02 | 2000-01 | 2025-12 | 0.00 |
| nldas_mensual.csv | sm_0_100cm_anom_z | Anomalía z de sm_0_100cm_m3m3 por condado y mes calendario, base 1991-2020 | adim. | NLDAS-2 Noah mensual v2.0 (NLDAS_NOAH0125_M, NASA GES DISC por Harmony) |  | 2000-01 | 2025-12 | 0.00 |
| nldas_mensual.csv | et_nldas_mm | Evapotranspiración total del mes (Evap, suma mensual) | mm | NLDAS-2 Noah mensual v2.0 (NLDAS_NOAH0125_M, NASA GES DISC por Harmony) | G03 | 2000-01 | 2025-12 | 0.00 |
| nldas_mensual.csv | escorrentia_nldas_mm | Escorrentía total del mes: superficial (Qs) + subsuperficial (Qsb) | mm | NLDAS-2 Noah mensual v2.0 (NLDAS_NOAH0125_M, NASA GES DISC por Harmony) | G04 | 2000-01 | 2025-12 | 0.00 |
| nldas_mensual.csv | swe_nldas_mm | Equivalente en agua de la nieve, media del mes (SWE) | mm | NLDAS-2 Noah mensual v2.0 (NLDAS_NOAH0125_M, NASA GES DISC por Harmony) |  | 2000-01 | 2025-12 | 0.00 |

## Fuentes y acceso

- **DOI:** NLDAS Noah Land Surface Model L4 Monthly 0.125 x 0.125 degree V2.0 (`NLDAS_NOAH0125_M`,
  GES DISC): https://doi.org/10.5067/WB224IA3PVOJ
- Citas completas: `docs/research/citas_nasa.md`.

- Descarga: `src/nldas/download.py`. Harmony (`harmony.earthdata.nasa.gov`, OGC API Coverages) con
  recorte en origen por bbox de la zona (condados ± 0,05°), por mes y por variable (`SoilM_0_10cm`,
  `SoilM_0_100cm`, `Evap`, `Qs`, `Qsb`, `SWE`). Un NetCDF4 de ~160 KB por mes en
  `data/raw/nldas/nldas_noah_m/<anio>/`. Se baja 1991-2025: 1991-1999 solo sirve de base para la
  anomalía z (1991-2020); el CSV cubre el período del proyecto (2000-2025).
- Procesamiento: `src/nldas/process.py` (también genera esta tabla).

## Supuestos

- **Acceso con login (Earthdata).** No se encontró un acceso público sin login al mismo producto:
  NLDAS-2 solo se distribuye por GES DISC (HTTPS, OPeNDAP, Harmony, todos con Earthdata); el OPeNDAP de
  hydro1 devuelve 410 (retirado, ver bitácora de `vegetacion`). Se usó Harmony con la credencial de
  Earthdata disponible. No hay copia en Planetary Computer ni en AWS Open Data sin login que se haya
  verificado en esta ronda.
- **Conversión a m³/m³.** NLDAS da la humedad como masa de agua por área de cada capa (kg m-2 = mm). Se
  divide por el espesor de la capa: 100 mm (0-10 cm) y 1000 mm (0-100 cm). `SoilM_0_100cm` es la capa
  acumulada 0-100 cm del propio producto.
- **Agregación espacial:** media del condado ponderada por la fracción de área de cada celda de 0,125°
  (~12 km) dentro del condado (supermuestreo 10x en grados). No se usa la máscara agrícola del CDL: a
  12 km casi todas las celdas mezclan usos y el producto es un modelo con vegetación propia, así que no
  se agrega `frac_pixeles_validos`. Celdas sin dato (agua, por ejemplo el lago Michigan) no cuentan.
- **Escorrentía total** = `Qs` (superficial) + `Qsb` (subsuperficial/drenaje de base), sumas mensuales.
  Si falta cualquiera de las dos en una celda, la celda no cuenta para ese mes.
- **ET** = `Evap` (evapotranspiración total, suma mensual). Puede ser apenas negativa en invierno
  (condensación/escarcha neta del modelo): se deja el valor del modelo, no se recorta.
- **Anomalía z:** por condado y mes calendario, con media y desvío (n − 1) de 1991-2020 de
  `sm_0_100cm_m3m3`. Se calcula sobre la media del condado, no por celda.
- **Redundancia:** `et_mm` del paquete `vegetacion` sale del mismo `Evap` de NLDAS-2 Noah (sustituto de
  MOD16A2): `et_nldas_mm` y `et_mm` son la misma magnitud con la misma fuente. Anotado en
  `loop/notes/decisiones.md`.

## Problemas conocidos

- NLDAS-2 Noah no simula riego ni drenaje con caños (tile): en condados muy drenados del Corn Belt
  la humedad y la escorrentía del modelo pueden diferir de lo observado.
- Las salidas de NLDAS-2 mensual se publican con algunos meses de retraso; si un mes no estaba al
  bajar, queda vacío hasta volver a correr `download.py`.
