# Estructura de los CSV de Field Shift (Corn Belt)

Cómo llegan los datos al equipo de machine learning. Sale de las reglas que verifica el research agent
(`loop/spec/entregables.yaml`, aprobado con `loop/aprobar_checks.py`), así que lo que dice acá es lo que se controla.

## Resumen

- **Dos tablas para entrenar**, en `data/processed/`:
  - `tabla_anual.csv`: una fila por **condado × año × cultivo** (las filas de `produccion_anual.csv`). Es la tabla principal: target, clima del año, rotación, fenología, suelo y terreno, precios y costos, aptitud (GAEZ), paisaje (NLCD) y cobertura del suelo a 30 m. 106 columnas además de las claves.
  - `tabla_mensual.csv`: una fila por **condado × mes**, con clima, vegetación, agua, validación (PRISM, CoCoRaHS), ECOSTRESS, NLDAS y napa y caudales (USGS). 65 columnas además de las claves.
- **Zona:** Iowa (IA, FIPS 19, 99 condados), Illinois (IL, FIPS 17, 102 condados), Indiana (IN, FIPS 18, 92 condados). Total: 293 condados. Está pendiente de confirmación.
- **Período:** 2000 a 2025. Rotaciones desde 2008 (el CDL cubre todo el país desde ese año).
- **Cultivos:** `maiz`, `soja`, `trigo_invierno`, `avena`, `alfalfa`, `heno`.
- **Tamaño máximo:** 293 × 26 × 6 = 45.708 filas en la anual (NASS no publica todos los condados ni todos los cultivos, así que habrá menos) y 293 × 26 × 12 = 91.416 filas en la mensual.

## De dónde sale cada tabla

| Fuente | Archivos | Granularidad |
|---|---|---|
| USDA NASS Quick Stats (encuesta por condado) | `produccion_anual` | condado, año y cultivo |
| NASS Crop Progress (por estado) | `fenologia_estado` | estado, año y cultivo (maíz y soja) |
| NASS Censo Agropecuario 2012, 2017, 2022 | `practicas_censo` | condado y año de censo |
| Cropland Data Layer (CDL) | `rotacion_anual`, máscaras en `data/reference/` | condado y año (2008+) |
| Crop Sequence Boundaries (CSB) | `rotacion_secuencia` | condado y ventana de 8 años |
| NASA POWER, GPM IMERG | `clima_diario`, `clima_mensual`, `clima_anual` | condado y día / mes / año |
| MODIS (NDVI, LST, ET) | `vegetacion_16d`, `vegetacion_mensual`, `fenologia_anual` | condado y 16 días / mes / año |
| SMAP L4, GRACE-DA-DM | `agua_diario`, `agua_mensual`, `agua_semanal` | condado y día / mes / semana |
| gSSURGO, SRTM / NASADEM | `suelo_terreno_estatico` | condado (fijo) |
| US Census (TIGER/Line) | `data/reference/condados.csv` | condado (fijo) |
| NASS precio recibido, USDA ERS costos y retornos | `economia_anual`, `economia_forrajes_anual` | estado, año y cultivo |
| FAO GAEZ v4 | `aptitud_estatico` | condado (fijo; clima 1981–2010 y 2041–2070) |
| USGS NLCD | `paisaje_anual` | condado y año |
| Landsat, Sentinel-2 (o HLS) | `teledeteccion_anual` | condado y año (2008+) |
| PRISM, CoCoRaHS (validación; no son de la NASA) | `validacion_mensual` | condado y mes |
| ECOSTRESS | `ecostress_mensual` | condado y mes (2018+) |
| NLDAS-2 | `nldas_mensual` | condado y mes |
| USGS NWIS (pozos y aforos) | `hidrologia_mensual` | condado y mes |

- `tabla_anual.csv` junta todos los archivos anuales y estáticos. Los que son por estado (`fenologia_estado`, `economia_*`) se unen por los dos primeros dígitos de `fips`.
- `tabla_mensual.csv` junta todos los `*_mensual.csv`.
- `rotacion_secuencia.csv` (ventanas de 8 años) y `practicas_censo.csv` (solo años de censo) quedan aparte porque tienen otra granularidad.

## `tabla_anual.csv`

Claves: `fips`, `anio`, `cultivo`. El target es `rend_bu_ac` (o `rend_kgha`). Las columnas son las de estos archivos (el diccionario está más abajo):

| Bloque | Archivo de origen | Varía por |
|---|---|---|
| Producción y target (NASS) | `produccion_anual.csv` | condado, año y cultivo |
| Clima del año (POWER, IMERG) | `clima_anual.csv` | condado y año |
| Rotación del año (CDL) | `rotacion_anual.csv` | condado y año (2008+) |
| Fenología por satélite (MODIS) | `fenologia_anual.csv` | condado y año |
| Fechas reales de siembra, floración y cosecha (Crop Progress) | `fenologia_estado.csv` | estado, año y cultivo |
| Suelo y terreno (gSSURGO, DEM) | `suelo_terreno_estatico.csv` | condado (fijo) |
| Precios y costos (NASS, ERS) | `economia_anual.csv`, `economia_forrajes_anual.csv` | estado, año y cultivo |
| Aptitud y rendimiento alcanzable (GAEZ) | `aptitud_estatico.csv` | condado (fijo) |
| Cobertura del suelo (NLCD) | `paisaje_anual.csv` | condado y año |
| Suelo desnudo y cobertura invernal a 30 m (Landsat, Sentinel-2) | `teledeteccion_anual.csv` | condado y año (2008+) |

## `tabla_mensual.csv`

Claves: `fips`, `anio`, `mes` (`anio` es el año calendario del mes). Para usarla junto a la anual, pivotear los meses a columnas:

```python
import pandas as pd
anual = pd.read_csv("data/processed/tabla_anual.csv", dtype={"fips": str})
mens = pd.read_csv("data/processed/tabla_mensual.csv", dtype={"fips": str})
mens["m"] = mens["mes"].str[5:7]
ancho = mens[mens["m"].isin(["04", "05", "06", "07", "08", "09"])].pivot_table(
    index=["fips", "anio"], columns="m", values=["prec_power_mm", "tmax_c", "ndvi"])
ancho.columns = [f"{v}_{m}" for v, m in ancho.columns]
X = anual.merge(ancho.reset_index(), on=["fips", "anio"], how="left")
```

## Reglas de todos los CSV

- UTF-8, separador `,`, decimal `.`, encabezado en la primera fila.
- **Claves primero:** `fips` (texto de 5 dígitos: 2 del estado y 3 del condado, ej. `19169`), `anio` (entero, año de la cosecha), y después `cultivo`, `fecha` (AAAA-MM-DD) o `mes` (AAAA-MM). Leer `fips` con `dtype=str` para no perder los ceros.
- En los archivos diarios, de 8/16 días, semanales y mensuales, `anio` es el año calendario de la fecha o del mes.
- Los datos que solo existen por estado (Crop Progress, precios y costos) usan `fips_estado` (2 dígitos).
- **Faltantes:** celda vacía. Nunca 0, -999 ni -9999. En NASS, `(D)` (oculto para no revelar productores) y `(Z)` (menos de la mitad de la unidad) también van vacíos, con el código en `flag_nass`.
- **Unidades de EE.UU.:** se guarda el valor original (`rend_bu_ac`, `sup_sembrada_ac`, `produccion_bu`) y la conversión en otra columna: maíz 1 bu/ac = 62,77 kg/ha; soja y trigo 67,25; avena 35,87; 1 acre = 0,4047 ha.
- **Ventanas de los archivos anuales:** temporada = abril a septiembre del `anio`; invierno previo = noviembre del `anio − 1` a marzo del `anio`; meses críticos = julio (floración del maíz) y agosto (llenado de la soja).
- **Agregación espacial:** media sobre el condado; con la máscara agrícola del CDL, solo píxeles agrícolas (columna `frac_pixeles_validos`).

## Desde cuándo hay datos

| Fuente | Desde |
|---|---|
| NASS Quick Stats por condado | 2000 (los de 2024 y 2025 están por verificar) |
| NASA POWER | 1981 (radiación desde 1984) |
| GPM IMERG | junio de 2000 |
| MODIS MOD13Q1 / MOD11A2 | 2000 |
| MODIS MOD16A2 (ET) | 2001 |
| GRACE-DA-DM | 2003 (a verificar) |
| SMAP L4 | marzo de 2015 |
| CDL (todo el país) | 2008 |
| Crop Sequence Boundaries | ventanas de 8 años, de 2008–2015 a 2018–2025 |
| Censo Agropecuario | 2012, 2017, 2022 |
| gSSURGO, SRTM / NASADEM | fijo |
| NASS precio recibido por estado | 2000 (trigo de Iowa hasta 2019, avena de Indiana hasta 2015) |
| FAO GAEZ v4 | fijo (clima 1981–2010 y 2041–2070) |
| Annual NLCD | 1985 (a verificar hasta qué año) |
| Landsat (en este pipeline) | 2008 |
| Sentinel-2 L2A | 2017 |
| PRISM mensual | 1981 |
| CoCoRaHS (en este pipeline) | 2008 |
| ECOSTRESS | julio de 2018 |
| NLDAS-2 | 1979 |
| USGS NWIS | según el pozo o la estación |

## Para quien arme el modelo

- **No se sacó la tendencia del rendimiento.** Lo decide el equipo de ML, para no filtrar información del futuro.
- Las tendencias de clima (`tend_*`) solo usan años hasta el `anio` de la fila.
- Partir por año (entrenar con años viejos, validar con los nuevos), no al azar.
- Cada columna tiene su descripción, fuente, cobertura real y % de faltantes en `docs/datasets/<paquete>.md`. Leer "Supuestos" y "Problemas conocidos" antes de usarla.

## A confirmar

- Estados y condados exactos (hoy: todos los condados de Iowa, Illinois e Indiana).
- Los nombres marcados *(nombre propuesto)*: el CLAUDE.md no los fija.
- Los paquetes `economia`, `aptitud`, `paisaje`, `teledeteccion`, `validacion`, `ecostress`, `nldas` e `hidrologia` usan los recursos del desafío y no están en el CLAUDE.md §6.
- `anio` en los archivos diarios y mensuales como año calendario (el CLAUDE.md lo fija para los mensuales).

## Diccionario

### Archivos de `tabla_anual.csv`

| Columna | Qué es | Unidad | ID · prioridad | Rango aceptado | Desde |
|---|---|---|---|---|---|
| **produccion_anual.csv** | claves: `fips`, `anio`, `cultivo` | | | | |
| `sup_sembrada_ac` | Superficie sembrada (NASS) | acres | Y01 · Alta | 0 a 1.000.000 | 2000 |
| `sup_cosechada_ac` | Superficie cosechada (NASS) | acres | Y02 · Alta | 0 a 1.000.000 | 2000 |
| `produccion_bu` | Producción (NASS) | bu | Y03 · Alta | 0 a 300.000.000 | 2000 |
| `rend_bu_ac` | Rendimiento (NASS), sin sacar tendencia | bu/acre | Y04 · Alta | 0 a 320 | 2000 |
| `rend_kgha` | Rendimiento convertido con el factor del cultivo | kg/ha | Y04 · Alta | 0 a 20.000 | 2000 |
| `sup_sembrada_ha` | Superficie sembrada en ha | ha | Y01 · Alta | 0 a 405.000 | 2000 |
| `ratio_cosechada` | Cosechada / sembrada | fracción | Y05 · Alta | 0 a 1,05 | 2000 |
| `flag_nass` | Código original de NASS cuando el valor está oculto: (D), (Z) | código | — | — | 2000 |
| **clima_anual.csv** | claves: `fips`, `anio` | | | | |
| `doy_ultima_helada` | Fecha de última helada de primavera | día del año | D12 · Alta | 1 a 366 | 2000 |
| `doy_primera_helada` | Fecha de primera helada de otoño | día del año | D13 · Alta | 1 a 366 | 2000 |
| `periodo_libre_heladas_dias` | Período libre de heladas | días | D14 · Alta | 0 a 366 | 2000 |
| `prec_temporada_mm` | Lluvia abril–septiembre | mm | D19 · Alta | 0 a 2.500 | 2000 |
| `gdd_temporada` | Grados-día abril–septiembre | °C·día | D08 · Alta | 0 a 4.000 | 2000 |
| `prec_invierno_previo_mm` | Lluvia noviembre (anio−1) a marzo | mm | D20 · Alta | 0 a 2.000 | 2000 |
| `prec_jul_mm` | Lluvia de julio | mm | D19 · Alta | 0 a 800 | 2000 |
| `tmax_jul_c` | Tmax media de julio | °C | D10 · Alta | 10 a 45 | 2000 |
| `dias_tmax_gt30_jul` | Días de julio con Tmax > 30 °C | días | D10 · Alta | 0 a 31 | 2000 |
| `prec_ago_mm` | Lluvia de agosto | mm | D19 · Alta | 0 a 800 | 2000 |
| `deficit_temporada_mm` | Lluvia − ETo, abril–septiembre | mm | D04 · Alta | −2.000 a 2.000 | 2000 |
| `tend_prec_mm_decada` *(nombre propuesto)* | Tendencia de la lluvia (solo años hasta anio) | por década | D24 · Media | −1.000 a 1.000 | 2000 |
| `tend_tmed_c_decada` *(nombre propuesto)* | Tendencia de la temperatura (solo años hasta anio) | por década | D24 · Media | −5 a 5 | 2000 |
| **rotacion_anual.csv** | claves: `fips`, `anio` | | | | |
| `pct_maiz` *(nombre propuesto)* | % del área agrícola con maíz (CDL) | % | R04 · Alta | 0 a 100 | 2008 |
| `pct_soja` *(nombre propuesto)* | % con soja | % | R04 · Alta | 0 a 100 | 2008 |
| `pct_trigo` *(nombre propuesto)* | % con trigo | % | R04 · Alta | 0 a 100 | 2008 |
| `pct_alfalfa` *(nombre propuesto)* | % con alfalfa | % | R04 · Alta | 0 a 100 | 2008 |
| `pct_heno` *(nombre propuesto)* | % con heno | % | R04 · Alta | 0 a 100 | 2008 |
| `pct_doble_trigo_soja` *(nombre propuesto)* | % con doble cultivo trigo/soja | % | R09 · Alta | 0 a 100 | 2008 |
| `pct_barbecho` *(nombre propuesto)* | % en barbecho | % | R14 · Alta | 0 a 100 | 2008 |
| `pct_maiz_tras_soja` | % maíz que el año anterior fue soja (por píxel, sobre los que el año anterior eran agrícolas) | % | R03 · Alta | 0 a 100 | 2009 |
| `pct_maiz_tras_maiz` | % maíz sobre maíz (ídem) | % | R03 · Alta | 0 a 100 | 2009 |
| `pct_soja_tras_maiz` | % soja sobre maíz (ídem) | % | R03 · Alta | 0 a 100 | 2009 |
| `pct_soja_tras_soja` | % soja sobre soja (ídem) | % | R03 · Alta | 0 a 100 | 2009 |
| **fenologia_estado.csv** | claves: `fips_estado`, `anio`, `cultivo` | | | | |
| `doy_50_sembrado` | Día del año con 50 % sembrado (Crop Progress) | día del año | CT03 · Alta | 1 a 366 | 2000 |
| `doy_50_emergido` | Día con 50 % emergido | día del año | — | 1 a 366 | 2000 |
| `doy_50_floracion` | Día con 50 % en floración (silking / blooming) | día del año | CT05 · Alta | 1 a 366 | 2000 |
| `doy_50_cosechado` | Día con 50 % cosechado | día del año | CT04 · Alta | 1 a 366 | 2000 |
| **suelo_terreno_estatico.csv** | claves: `fips` | | | | |
| `aws0_100_mm` *(nombre propuesto)* | Agua disponible 0–100 cm (Valu1) | mm | L12 · Alta | 0 a 600 | fijo |
| `aws0_150_mm` *(nombre propuesto)* | Agua disponible 0–150 cm (Valu1) | mm | L12 · Alta | 0 a 800 | fijo |
| `soc0_30_gm2` *(nombre propuesto)* | Carbono orgánico 0–30 cm (Valu1) | g C/m² | L10 · Alta | 0 a 100.000 | fijo |
| `soc0_100_gm2` *(nombre propuesto)* | Carbono orgánico 0–100 cm (Valu1) | g C/m² | L04 · Alta | 0 a 300.000 | fijo |
| `nccpi_*` *(nombre propuesto)* | Índice de productividad NCCPI (maíz/soja y general) | índice 0–1 | L15 · Alta | 0 a 1 | fijo |
| `prof_raices_cm` *(nombre propuesto)* | Profundidad de la zona de raíces (Valu1) | cm | — | 0 a 300 | fijo |
| `clase_drenaje` *(nombre propuesto)* | Clase de drenaje dominante (muaggatt) | categoría | L17 · Media | — | fijo |
| `grupo_hidrologico` *(nombre propuesto)* | Grupo hidrológico dominante (muaggatt) | A, B, C, D, A/D, B/D, C/D | — | lista fija | fijo |
| `napa_min_cm` *(nombre propuesto)* | Profundidad mínima anual de la napa (muaggatt) | cm | — | 0 a 300 | fijo |
| `arcilla_pct` *(nombre propuesto)* | Arcilla | % | L01 · Alta | 0 a 100 | fijo |
| `arena_pct` *(nombre propuesto)* | Arena | % | L02 · Alta | 0 a 100 | fijo |
| `limo_pct` *(nombre propuesto)* | Limo | % | L03 · Media | 0 a 100 | fijo |
| `materia_organica_pct` *(nombre propuesto)* | Materia orgánica 0–30 cm (chorizon) | % | L04 · Alta | 0 a 100 | fijo |
| `ph_agua` *(nombre propuesto)* | pH en agua | pH | L06 · Media | 3 a 10 | fijo |
| `clase_textural_usda` *(nombre propuesto)* | Clase textural | categoría | L11 · Media | lista fija | fijo |
| `factor_k_rusle` *(nombre propuesto)* | Factor K de erodabilidad (RUSLE) | ver data card | L13 · Media | 0 a 0,8 | fijo |
| `elevacion_media_m` *(nombre propuesto)* | Elevación | m | T01 · Media | −10 a 2.000 | fijo |
| `elevacion_desvio_m` *(nombre propuesto)* | Elevación | m | T01 · Media | 0 a 300 | fijo |
| `pendiente_media_pct` *(nombre propuesto)* | Pendiente | % | T02 · Media | 0 a 60 | fijo |
| `pendiente_gt2_pct` *(nombre propuesto)* | Pendiente | % | T02 · Media | 0 a 100 | fijo |
| `twi_medio` *(nombre propuesto)* | TWI – índice topográfico de humedad | índice | T06 · Alta | 0 a 30 | fijo |
| `twi_decil_sup_pct` *(nombre propuesto)* | TWI – índice topográfico de humedad | % | T06 · Alta | 0 a 100 | fijo |
| **fenologia_anual.csv** | claves: `fips`, `anio` | | | | |
| `doy_inicio` | Inicio de temporada (SOS) | día del año | F01 · Media | 1 a 366 | 2000 |
| `doy_pico` | Fecha del pico (POS) | día del año | F02 · Alta | 1 a 366 | 2000 |
| `doy_fin` | Fin de temporada (EOS) | día del año | F04 · Media | 1 a 366 | 2000 |
| `ndvi_max` | NDVI máximo | índice −1 a 1 | F03 · Alta | −1 a 1 | 2000 |
| `duracion_dias` | Duración de la temporada | días | F05 · Media | 0 a 366 | 2000 |
| `ndvi_integral` | Integral de NDVI | NDVI·día | F06 · Alta | 0 a 400 | 2000 |
| `n_ciclos` | Ciclos de crecimiento por campaña | ciclos | F07 · Alta | 0 a 4 | 2000 |
| `ndvi_max_maiz` | NDVI máximo de los píxeles de maíz | índice −1 a 1 | F03 · Alta | −1 a 1 | 2008 |
| `ndvi_max_soja` | NDVI máximo de los píxeles de soja | índice −1 a 1 | F03 · Alta | −1 a 1 | 2008 |
| `dias_ndvi_lt03_invierno` | Días con NDVI < 0,3 en el invierno previo | días | F09 · Alta | 0 a 152 | 2000 |
| **economia_anual.csv** | claves: `fips_estado`, `anio`, `cultivo` | | | | |
| `precio_usd_bu` *(nombre propuesto)* | Precio recibido del año comercial (NASS, por estado) | USD/bu | MK01 · Media | 0,5 a 40 | 2000 |
| `valor_produccion_usd_ac` *(nombre propuesto)* | Valor de la producción por acre sembrado (ERS, región Heartland) | USD/acre sembrado | — | 0 a 3.000 | 2000 |
| `costo_operativo_usd_ac` *(nombre propuesto)* | Costos operativos por acre sembrado (ERS, Heartland) | USD/acre sembrado | MK03 · Baja | 10 a 1.500 | 2000 |
| `costo_total_usd_ac` *(nombre propuesto)* | Costos totales listados por acre sembrado (ERS, Heartland) | USD/acre sembrado | MK03 · Baja | 20 a 2.500 | 2000 |
| `margen_operativo_usd_ac` *(nombre propuesto)* | Valor de la producción − costos operativos (ERS, Heartland) | USD/acre sembrado | MK02 · Media | −1.500 a 2.500 | 2000 |
| `flag_nass` | Código original de NASS cuando el valor está oculto: (D), (Z) | código | — | — | 2000 |
| **economia_forrajes_anual.csv** | claves: `fips_estado`, `anio`, `cultivo` | | | | |
| `precio_usd_ton` *(nombre propuesto)* | Precio recibido del año comercial (NASS, por estado) | USD/tonelada corta | MK01 · Media | 10 a 700 | 2000 |
| `flag_nass` | Código original de NASS cuando el valor está oculto: (D), (Z) | código | — | — | 2000 |
| **aptitud_estatico.csv** | claves: `fips` | | | | |
| `aptitud_maiz_1981_2010` *(nombre propuesto)* | Índice de aptitud agroclimática por cultivo | índice 0–100 | Z01 · Media | 0 a 100 | fijo |
| `aptitud_soja_1981_2010` *(nombre propuesto)* | Índice de aptitud agroclimática por cultivo | índice 0–100 | Z01 · Media | 0 a 100 | fijo |
| `aptitud_trigo_1981_2010` *(nombre propuesto)* | Índice de aptitud agroclimática por cultivo | índice 0–100 | Z01 · Media | 0 a 100 | fijo |
| `aptitud_avena_1981_2010` *(nombre propuesto)* | Índice de aptitud agroclimática por cultivo | índice 0–100 | Z01 · Media | 0 a 100 | fijo |
| `aptitud_alfalfa_1981_2010` *(nombre propuesto)* | Índice de aptitud agroclimática por cultivo | índice 0–100 | Z01 · Media | 0 a 100 | fijo |
| `aptitud_maiz_2041_2070` *(nombre propuesto)* | Aptitud bajo escenarios de clima futuro | índice 0–100 | Z04 · Baja | 0 a 100 | fijo |
| `aptitud_soja_2041_2070` *(nombre propuesto)* | Aptitud bajo escenarios de clima futuro | índice 0–100 | Z04 · Baja | 0 a 100 | fijo |
| `aptitud_trigo_2041_2070` *(nombre propuesto)* | Aptitud bajo escenarios de clima futuro | índice 0–100 | Z04 · Baja | 0 a 100 | fijo |
| `aptitud_avena_2041_2070` *(nombre propuesto)* | Aptitud bajo escenarios de clima futuro | índice 0–100 | Z04 · Baja | 0 a 100 | fijo |
| `aptitud_alfalfa_2041_2070` *(nombre propuesto)* | Aptitud bajo escenarios de clima futuro | índice 0–100 | Z04 · Baja | 0 a 100 | fijo |
| `rend_alcanzable_maiz_kgha_1981_2010` *(nombre propuesto)* | Rendimiento alcanzable por cultivo | kg MS/ha | Z02 · Media | 0 a 25.000 | fijo |
| `rend_alcanzable_maiz_kgha_2041_2070` *(nombre propuesto)* | Rendimiento alcanzable por cultivo | kg MS/ha | Z02 · Media | 0 a 25.000 | fijo |
| `rend_alcanzable_soja_kgha_1981_2010` *(nombre propuesto)* | Rendimiento alcanzable por cultivo | kg MS/ha | Z02 · Media | 0 a 10.000 | fijo |
| `rend_alcanzable_soja_kgha_2041_2070` *(nombre propuesto)* | Rendimiento alcanzable por cultivo | kg MS/ha | Z02 · Media | 0 a 10.000 | fijo |
| `rend_alcanzable_trigo_kgha_1981_2010` *(nombre propuesto)* | Rendimiento alcanzable por cultivo | kg MS/ha | Z02 · Media | 0 a 15.000 | fijo |
| `rend_alcanzable_trigo_kgha_2041_2070` *(nombre propuesto)* | Rendimiento alcanzable por cultivo | kg MS/ha | Z02 · Media | 0 a 15.000 | fijo |
| **paisaje_anual.csv** | claves: `fips`, `anio` | | | | |
| `pct_cultivos_nlcd` *(nombre propuesto)* | % del condado en cultivos (NLCD 82) | % | — | 0 a 100 | 2000 |
| `pct_pasturas_heno_nlcd` *(nombre propuesto)* | % en pasturas y heno (NLCD 81) | % | — | 0 a 100 | 2000 |
| `pct_bosque_nlcd` *(nombre propuesto)* | % en bosque (NLCD 41–43) | % | — | 0 a 100 | 2000 |
| `pct_humedales_nlcd` *(nombre propuesto)* | % en humedales (NLCD 90 y 95) | % | — | 0 a 100 | 2000 |
| `pct_urbano_nlcd` *(nombre propuesto)* | % urbano (NLCD 21–24) | % | — | 0 a 100 | 2000 |
| `pct_agua_nlcd` *(nombre propuesto)* | % en agua (NLCD 11) | % | — | 0 a 100 | 2000 |
| `impermeable_pct` *(nombre propuesto)* | Superficie impermeable media (NLCD) | % | — | 0 a 100 | 2000 |
| **teledeteccion_anual.csv** | claves: `fips`, `anio` | | | | |
| `pct_suelo_desnudo_abr_may` *(nombre propuesto)* | % de píxeles agrícolas desnudos (NDVI < 0,25), mediana abril–mayo, 30 m | % | F08 · Alta | 0 a 100 | 2008 |
| `pct_suelo_desnudo_oct_nov` *(nombre propuesto)* | % de píxeles agrícolas desnudos, mediana octubre–noviembre, 30 m | % | F08 · Alta | 0 a 100 | 2008 |
| `pct_cobertura_verde_mar_abr` *(nombre propuesto)* | % de píxeles agrícolas verdes (NDVI ≥ 0,3), 15 de marzo a 30 de abril | % | — | 0 a 100 | 2008 |
| `bsi_abr_may` *(nombre propuesto)* | Índice de suelo desnudo (BSI) medio, abril–mayo | índice −1 a 1 | H05 · Media | −1 a 1 | 2008 |
| `ndvi_max_30m` *(nombre propuesto)* | NDVI máximo abril–septiembre a 30 m | índice −1 a 1 | H02 · Media | −1 a 1 | 2008 |
| `n_escenas_validas` *(nombre propuesto)* | Escenas Landsat / Sentinel-2 usadas | escenas | — | 0 a 5.000 | 2008 |
| `frac_pixeles_validos` | Máscara de nubes (Fmask) | fracción 0–1 | H06 · Media | 0 a 1 | 2008 |

### Archivos de `tabla_mensual.csv`

| Columna | Qué es | Unidad | ID · prioridad | Rango aceptado | Desde |
|---|---|---|---|---|---|
| **clima_mensual.csv** | claves: `fips`, `anio`, `mes` | | | | |
| `prec_imerg_mm` | Lluvia GPM IMERG | mm | P01 · Alta | 0 a 1.500 | 2000 |
| `prec_power_mm` | Lluvia NASA POWER (PRECTOTCORR) | mm | C08 · Alta | 0 a 1.500 | 2000 |
| `tmax_c` | T2M_MAX – temperatura máxima | °C | C02 · Alta | −30 a 45 | 2000 |
| `tmin_c` | T2M_MIN – temperatura mínima | °C | C03 · Alta | −40 a 35 | 2000 |
| `tmed_c` | T2M – temperatura media a 2 m | °C | C01 · Alta | −35 a 40 | 2000 |
| `rad_mj_m2` | Radiación solar | MJ/m² | C09 · Alta | 0 a 1.100 | 2000 |
| `eto_pm_mm` | ETo FAO-56 Penman-Monteith | mm | D01 · Alta | 0 a 400 | 2000 |
| `deficit_mm` | Lluvia − ETo | mm | D04 · Alta | −400 a 1.500 | 2000 |
| `dias_tmax_gt30` | Días con Tmax > 30 °C | días | D09 · Media | 0 a 31 | 2000 |
| `dias_tmax_gt35` | Días con Tmax > 35 °C en período crítico | días | D10 · Alta | 0 a 31 | 2000 |
| `dias_tmin_le0` | Días con Tmin ≤ 0 °C | días | D11 · Alta | 0 a 31 | 2000 |
| `dias_tmin_le_m2` | Días con Tmin ≤ −2 °C | días | D11 · Alta | 0 a 31 | 2000 |
| `gdd_10_30` | Grados-día del maíz (base 10 °C, tope 30 °C) | °C·día | D08 · Alta | 0 a 650 | 2000 |
| `gdd_base0` | Grados-día base 0 °C | °C·día | D08 · Alta | 0 a 1.100 | 2000 |
| `dias_lluvia_ge1` | Días con lluvia | días | D18 · Baja | 0 a 31 | 2000 |
| `prec_max1d_mm` | Lluvia máxima en 1 y 5 días (Rx1day, Rx5day) | mm | D16 · Media | 0 a 500 | 2000 |
| `prec_max5d_mm` | Lluvia máxima en 1 y 5 días (Rx1day, Rx5day) | mm | D16 · Media | 0 a 800 | 2000 |
| `dias_lluvia_gt50` | Días con lluvia > 50 mm | días | D15 · Media | 0 a 31 | 2000 |
| `racha_seca_max_dias` | Racha seca máxima | días | D17 · Alta | 0 a 31 | 2000 |
| `spi1` | SPI-1, SPI-3, SPI-6 | z | D06 · Alta | −5 a 5 | 2000 |
| `spi3` | SPI-1, SPI-3, SPI-6 | z | D06 · Alta | −5 a 5 | 2000 |
| `spi6` | SPI-1, SPI-3, SPI-6 | z | D06 · Alta | −5 a 5 | 2000 |
| `anom_tmed_c` | Anomalía de temperatura | °C | D23 · Media | −20 a 20 | 2000 |
| `gwettop` | GWETTOP – humedad del suelo superficial | fracción 0–1 | C11 · Media | 0 a 1 | 2000 |
| `gwetroot` | GWETROOT – humedad zona radicular | fracción 0–1 | C12 · Alta | 0 a 1 | 2000 |
| `gwetprof` | GWETPROF – humedad del perfil | fracción 0–1 | C13 · Media | 0 a 1 | 2000 |
| **vegetacion_mensual.csv** | claves: `fips`, `anio`, `mes` | | | | |
| `ndvi` | NDVI | índice −1 a 1 | M01 · Alta | −1 a 1 | 2000 |
| `evi` | EVI | índice −1 a 1 | M02 · Media | −1 a 1 | 2000 |
| `ndvi_maiz` | NDVI solo de píxeles de maíz de ese año | índice −1 a 1 | M01 · Alta | −1 a 1 | 2008 |
| `ndvi_soja` | NDVI solo de píxeles de soja | índice −1 a 1 | M01 · Alta | −1 a 1 | 2008 |
| `lst_dia_c` | Temperatura de superficie diurna | °C | M04 · Media | −40 a 75 | 2000 |
| `lst_noche_c` | Temperatura de superficie nocturna | °C | M05 · Baja | −50 a 45 | 2000 |
| `et_mm` | Evapotranspiración real | mm | M06 · Media | 0 a 300 | 2001 |
| `pet_mm` | Evapotranspiración potencial | mm | M07 · Media | 0 a 500 | 2001 |
| `et_pet_ratio` | ET / PET | fracción | — | 0 a 2 | 2001 |
| `ndvi_anom_z` | Anomalía de NDVI | z | F10 · Alta | −6 a 6 | 2000 |
| `vci` | VCI – condición de la vegetación | 0–100 | F11 · Media | 0 a 100 | 2000 |
| `tci` | TCI – condición térmica | 0–100 | F12 · Media | 0 a 100 | 2000 |
| `vhi` | VHI – salud de la vegetación | 0–100 | F13 · Media | 0 a 100 | 2000 |
| **agua_mensual.csv** | claves: `fips`, `anio`, `mes` | | | | |
| `sm_surface_m3m3` *(nombre propuesto)* | Humedad superficial (modelo L4) | m³/m³ | S02 · Media | 0 a 0,6 | 2015 |
| `sm_rootzone_m3m3` | Humedad zona radicular 0–100 cm (L4) | m³/m³ | S03 · Alta | 0 a 0,6 | 2015 |
| `sm_surface_min_m3m3` *(nombre propuesto)* | Humedad superficial (modelo L4) | m³/m³ | S02 · Media | 0 a 0,6 | 2015 |
| `sm_rootzone_min_m3m3` *(nombre propuesto)* | Humedad zona radicular 0–100 cm (L4) | m³/m³ | S03 · Alta | 0 a 0,6 | 2015 |
| `sm_rootzone_anom_z` | Anomalía de humedad del suelo | z | D25 · Alta | −6 a 6 | 2015 |
| `dias_sm_saturado` *(nombre propuesto)* | Días sobre el umbral de saturación | días | D26 · Media | 0 a 31 | 2015 |
| **validacion_mensual.csv** | claves: `fips`, `anio`, `mes` | | | | |
| `prec_prism_mm` *(nombre propuesto)* | Lluvia PRISM (validación) | mm | — | 0 a 1.000 | 2000 |
| `tmax_prism_c` *(nombre propuesto)* | Tmax media PRISM | °C | — | −30 a 45 | 2000 |
| `tmin_prism_c` *(nombre propuesto)* | Tmin media PRISM | °C | — | −40 a 35 | 2000 |
| `tmed_prism_c` *(nombre propuesto)* | Temperatura media PRISM | °C | — | −35 a 40 | 2000 |
| `prec_cocorahs_mm` *(nombre propuesto)* | Lluvia media de los pluviómetros CoCoRaHS | mm | — | 0 a 1.000 | 2008 |
| `n_estaciones_cocorahs` *(nombre propuesto)* | Estaciones CoCoRaHS con al menos 25 días en el mes | estaciones | — | 0 a 500 | 2008 |
| **ecostress_mensual.csv** | claves: `fips`, `anio`, `mes` | | | | |
| `lst_ecostress_c` *(nombre propuesto)* | Temperatura de superficie ECOSTRESS (70 m) | °C | X01 · Media | −40 a 75 | 2018 |
| `et_ecostress_mm_dia` *(nombre propuesto)* | ET diaria ECOSTRESS (JET) | mm/día | X02 · Media | 0 a 15 | 2018 |
| `esi_ecostress` *(nombre propuesto)* | Índice de estrés evaporativo ECOSTRESS | fracción (ET / ET potencial) | X03 · Media | 0 a 2 | 2018 |
| `n_pasadas_ecostress` *(nombre propuesto)* | Pasadas de ECOSTRESS usadas | pasadas | — | 0 a 300 | 2018 |
| **nldas_mensual.csv** | claves: `fips`, `anio`, `mes` | | | | |
| `sm_0_10cm_m3m3` *(nombre propuesto)* | Humedad del suelo 0–10 cm (NLDAS-2 Noah) | m³/m³ | G01 · Media | 0 a 0,6 | 2000 |
| `sm_0_100cm_m3m3` *(nombre propuesto)* | Humedad del suelo 0–100 cm (NLDAS-2 Noah) | m³/m³ | G02 · Media | 0 a 0,6 | 2000 |
| `sm_0_100cm_anom_z` *(nombre propuesto)* | Anomalía de la humedad 0–100 cm (base 1991–2020) | z | — | −6 a 6 | 2000 |
| `et_nldas_mm` *(nombre propuesto)* | Evapotranspiración (NLDAS-2) | mm | G03 · Media | 0 a 300 | 2000 |
| `escorrentia_nldas_mm` *(nombre propuesto)* | Escorrentía superficial + subsuperficial (NLDAS-2) | mm | G04 · Baja | 0 a 600 | 2000 |
| `swe_nldas_mm` *(nombre propuesto)* | Agua equivalente en nieve (NLDAS-2) | mm | — | 0 a 1.500 | 2000 |
| **hidrologia_mensual.csv** | claves: `fips`, `anio`, `mes` | | | | |
| `napa_prof_m` *(nombre propuesto)* | Mediana de la profundidad a la napa en pozos USGS | m bajo la superficie | — | 0 a 300 | 2000 |
| `n_pozos` *(nombre propuesto)* | Pozos con dato en el mes | pozos | — | 0 a 1.000 | 2000 |
| `caudal_pctl` *(nombre propuesto)* | Percentil del caudal mensual (contra 1991–2020 de cada estación) | percentil 0–100 | — | 0 a 100 | 2000 |
| `n_estaciones_aforo` *(nombre propuesto)* | Estaciones de aforo USGS | estaciones | — | 0 a 300 | 2000 |

### Otros archivos

| Columna | Qué es | Unidad | ID · prioridad | Rango aceptado | Desde |
|---|---|---|---|---|---|
| **condados.csv** | claves: `fips` | | | | |
| `estado` | Código de dos letras del estado | código | K02 · Alta | — | fijo |
| `condado` | Nombre del condado | texto | — | — | fijo |
| `lat_centroide` | geometría / centroide (lat, lon) | grados | K06 · Alta | 35 a 50 | fijo |
| `lon_centroide` | geometría / centroide (lat, lon) | grados | K06 · Alta | −105 a −80 | fijo |
| `area_km2` | Área del condado | km² | — | 1 a 20.000 | fijo |
| **anios.csv** | claves: `anio` | | | | |
| `inicio_temporada` | 1 de abril del anio | AAAA-MM-DD | K04 · Alta | — | 2000 |
| `fin_temporada` | 30 de septiembre del anio | AAAA-MM-DD | K04 · Alta | — | 2000 |
| `inicio_invierno_previo` | 1 de noviembre del anio − 1 | AAAA-MM-DD | K04 · Alta | — | 2000 |
| `fin_invierno_previo` | 31 de marzo del anio | AAAA-MM-DD | K04 · Alta | — | 2000 |
| **clima_diario.csv** | claves: `fips`, `anio`, `fecha` | | | | |
| `tmed_c` | T2M – temperatura media a 2 m | °C | C01 · Alta | −45 a 45 | 2000 |
| `tmax_c` | T2M_MAX – temperatura máxima | °C | C02 · Alta | −40 a 50 | 2000 |
| `tmin_c` | T2M_MIN – temperatura mínima | °C | C03 · Alta | −50 a 40 | 2000 |
| `prec_power_mm` | Lluvia NASA POWER (PRECTOTCORR) | mm | C08 · Alta | 0 a 500 | 2000 |
| `prec_imerg_mm` | Lluvia GPM IMERG | mm | P01 · Alta | 0 a 500 | 2000 |
| `hr_pct` *(nombre propuesto)* | Humedad relativa | % | C06 · Media | 0 a 100 | 2000 |
| `viento_ms` *(nombre propuesto)* | Viento a 2 m | m/s | C07 · Media | 0 a 40 | 2000 |
| `rad_mj_m2` | Radiación solar | MJ/m² | C09 · Alta | 0 a 45 | 1984 |
| `gwettop` | GWETTOP – humedad del suelo superficial | fracción 0–1 | C11 · Media | 0 a 1 | 2000 |
| `gwetroot` | GWETROOT – humedad zona radicular | fracción 0–1 | C12 · Alta | 0 a 1 | 2000 |
| `gwetprof` | GWETPROF – humedad del perfil | fracción 0–1 | C13 · Media | 0 a 1 | 2000 |
| `eto_pm_mm` | ETo FAO-56 Penman-Monteith | mm | D01 · Alta | 0 a 20 | 2000 |
| **rotacion_secuencia.csv** | claves: `fips`, `ventana` | | | | |
| `pct_maiz_soja_alternado` *(nombre propuesto)* | % del área en maíz-soja alternado (CSB, 8 años) | % | — | 0 a 100 | 2000 |
| `pct_maiz_continuo` *(nombre propuesto)* | % en maíz continuo | % | R13 · Media | 0 a 100 | 2000 |
| `pct_soja_continua` *(nombre propuesto)* | % en soja continua | % | R13 · Media | 0 a 100 | 2000 |
| `pct_rotacion_trigo` *(nombre propuesto)* | % en rotaciones con trigo | % | — | 0 a 100 | 2000 |
| `pct_rotacion_alfalfa` *(nombre propuesto)* | % en rotaciones con alfalfa | % | R10 · Media | 0 a 100 | 2000 |
| `cultivos_por_anio` *(nombre propuesto)* | Cultivos por año | cultivos/año | R05 · Alta | 0 a 3 | 2000 |
| `diversidad_shannon` *(nombre propuesto)* | Diversidad de la secuencia (Shannon) | índice | R11 · Media | 0 a 3 | 2000 |
| **practicas_censo.csv** | claves: `fips`, `anio_censo` | | | | |
| `pct_cobertura` | % con cultivos de cobertura (Censo) | % | — | 0 a 100 | 2000 |
| `pct_labranza_cero` | % con labranza cero | % | — | 0 a 100 | 2000 |
| `pct_drenaje_tile` | % con drenaje por caños (tile) | % | — | 0 a 100 | 2000 |
| `pct_riego` | % bajo riego | % | — | 0 a 100 | 2000 |
| **vegetacion_16d.csv** | claves: `fips`, `anio`, `fecha` | | | | |
| `ndvi` | NDVI | índice −1 a 1 | M01 · Alta | −1 a 1 | 2000 |
| `evi` | EVI | índice −1 a 1 | M02 · Media | −1 a 1 | 2000 |
| `ndvi_maiz` | NDVI solo de píxeles de maíz de ese año | índice −1 a 1 | M01 · Alta | −1 a 1 | 2008 |
| `ndvi_soja` | NDVI solo de píxeles de soja | índice −1 a 1 | M01 · Alta | −1 a 1 | 2008 |
| `frac_pixeles_validos` | Calidad de píxel NDVI | fracción 0–1 | M03 · Alta | 0 a 1 | 2000 |
| **agua_diario.csv** | claves: `fips`, `anio`, `fecha` | | | | |
| `sm_surface_m3m3` *(nombre propuesto)* | Humedad superficial (modelo L4) | m³/m³ | S02 · Media | 0 a 0,6 | 2015 |
| `sm_rootzone_m3m3` | Humedad zona radicular 0–100 cm (L4) | m³/m³ | S03 · Alta | 0 a 0,6 | 2015 |
| **agua_semanal.csv** | claves: `fips`, `anio`, `fecha` | | | | |
| `gws_pctl` *(nombre propuesto)* | Percentil de agua subterránea | percentil 0–100 | W01 · Media | 0 a 100 | 2003 |
| `rtzsm_pctl` *(nombre propuesto)* | Percentil de humedad zona radicular | percentil 0–100 | W02 · Media | 0 a 100 | 2003 |
| `sfsm_pctl` *(nombre propuesto)* | Percentil de humedad superficial | percentil 0–100 | W03 · Baja | 0 a 100 | 2003 |
