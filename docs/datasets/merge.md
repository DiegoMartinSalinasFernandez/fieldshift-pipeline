# merge — tablas unidas

Generado por `python src/merge.py` (CLAUDE.md §7). No baja nada: lee solo `data/processed/`.
Tarda ~1 s y es determinista (mismo md5 en dos corridas).

## Salidas

| archivo | claves | filas (2026-11-14) | columnas | contenido |
|---|---|---|---|---|
| `data/processed/tabla_anual.csv` | `fips, anio, cultivo` | 25070 | 73 | filas de `produccion_anual.csv` + columnas de `clima_anual`, `rotacion_anual`, `fenologia_anual` (por `fips, anio`), `fenologia_estado` (por `fips[:2], anio, cultivo`) y `suelo_terreno_estatico` (por `fips`) |
| `data/processed/tabla_mensual.csv` | `fips, anio, mes` | 91416 | 48 | unión externa de `clima_mensual`, `vegetacion_mensual` y `agua_mensual` |

El diccionario de cada columna está en el data card de su paquete (`docs/datasets/<paquete>.md`):
los nombres no cambian al unir.

## Supuestos

- `tabla_anual` usa *left join* sobre `produccion_anual.csv`: los años de clima/vegetación sin
  fila de producción (y los condados sin datos NASS) no aparecen. Las variables de clima,
  rotación, fenología y suelo se repiten en las filas de cada cultivo del mismo condado y año.
- `fenologia_estado` se une por estado (`fips_estado = fips[:2]`), año y cultivo: solo tiene
  maíz y soja, así que en alfalfa, avena, heno y trigo de invierno las columnas `doy_50_*`
  quedan vacías. La columna `fips_estado` no se guarda (es `fips[:2]`).
- `tabla_mensual` usa *outer join*: un mes aparece si está en cualquiera de los tres paquetes;
  SMAP empieza en 2015-04, así que antes las columnas de `agua` quedan vacías.
- Los valores se copian como texto, sin reformatear. Si dos paquetes tuvieran una columna con
  el mismo nombre, la segunda se renombra `<paquete>_<columna>` (ver la sección T136).
- `rotacion_secuencia.csv` (por ventana de 8 años) queda aparte por tener otra granularidad.
  `practicas_censo.csv` entra desde T136 (abajo).

## Problemas conocidos

- Las tablas reflejan el estado de los CSV de cada paquete al correr `merge.py`: si un paquete
  se reprocesa, hay que volver a correrlo.
- `rotacion_anual` empieza en 2008 (CDL nacional): de 2000 a 2007 esas columnas están vacías.

## T136: paquetes nuevos (espera el OK de `para_decidir.md` #27)

Implementa `docs/research/merge_faltantes.md` (T050). **Todavía no es la versión aprobada:** el PR
queda retenido hasta que el humano diga que sí a la fila 27.

**Qué se suma** (si el archivo no está en `data/processed/`, se avisa y se sigue sin él):

| tabla | archivo | se une por | columnas nuevas |
|---|---|---|---|
| anual | `economia_anual.csv` + `economia_forrajes_anual.csv` (apilados en un solo bloque: granos y forrajes no se pisan) | `fips[:2], anio, cultivo` | `precio_usd_bu`, `valor_produccion_usd_ac`, `costo_operativo_usd_ac`, `costo_total_usd_ac`, `margen_operativo_usd_ac`, `economia_flag_nass`, `precio_usd_ton` |
| anual | `paisaje_anual.csv` | `fips, anio` | `pct_*_nlcd`, `impermeable_pct` |
| anual | `teledeteccion_anual.csv` | `fips, anio` | sus columnas; `frac_pixeles_validos` → `teledeteccion_frac_pixeles_validos` |
| anual | `practicas_censo.csv` | `fips` y el último `anio_censo` ≤ `anio` | `anio_censo_ref` (año del censo usado), `pct_cobertura`, `pct_labranza_cero`, `pct_drenaje_tile`, `pct_riego` |
| mensual | `nldas_mensual.csv` | `fips, anio, mes` (externa) | `sm_0_10cm_m3m3`, `sm_0_100cm_m3m3`, `sm_0_100cm_anom_z`, `et_nldas_mm`, `escorrentia_nldas_mm`, `swe_nldas_mm` |
| mensual | `ecostress_mensual.csv` | `fips, anio, mes` (externa) | `lst_ecostress_c`, `et_ecostress_mm_dia`, `esi_ecostress`, `n_pasadas_ecostress` |

Los bloques nuevos van **después** de los de antes: las columnas que ya salían en las dos tablas
conservan su nombre, su orden y sus valores (verificado con el release `datos-oh-ne-mn`).

**Censo "as-of".** Cada fila toma el último censo del condado con `anio_censo <= anio`: 2012–2016 →
2012, 2017–2021 → 2017, 2022–2025 → 2022. De 2000 a 2011 las columnas quedan vacías (no se usa un
censo posterior, para no meter datos del futuro). `anio_censo_ref` dice qué censo se usó. En el
censo 2012 faltan las prácticas salvo riego (ver [cultivos](cultivos.md)).

**`rotacion_secuencia.csv` queda afuera**, como recomienda el research (§3, opción 1): qué ventana de 8
años corresponde a cada año es una decisión de modelado. Se puede unir a mano por la ventana que
termina en `anio − 1`.

**Choques de nombres.** Regla de `renombrar_colisiones()`:

1. Una columna que ya está en la tabla no cambia nunca.
2. La columna nueva que choca lleva el paquete adelante (`flag_nass` de economía →
   `economia_flag_nass`).
3. Si ese nombre también existe, se usa el nombre del archivo (`<archivo>_<columna>`); si también
   existe, `merge.py` corta con error (antes pandas dejaba `_x` / `_y`).
4. `frac_pixeles_validos` (lista `NOMBRES_GENERICOS`) lleva siempre el prefijo del paquete en los
   paquetes nuevos, aunque hoy no choque: sola no dice de qué sensor es.

Choques encontrados con los CSV de `datos-oh-ne-mn`: solo `flag_nass`. `teledeteccion` y `ecostress`
no están en ese release.

**Duplicados de contenido (no chocan de nombre, pero ML los tiene que conocer):** `et_mm`
(`vegetacion_mensual`) y `et_nldas_mm` (`nldas_mensual`) salen los dos de NLDAS-2 Noah `Evap`;
quedan las dos. Lo mismo con las humedades de suelo de SMAP (`sm_rootzone_m3m3`, 2015+) y NLDAS
(`sm_0_100cm_m3m3`, 2000+): son complementarias.

**No entran (fuera de esta tarea):** `validacion_mensual` (PRISM y CoCoRaHS, no son de la NASA; es
para validar), `aptitud_estatico` e `hidrologia_mensual` (no tienen código en este repo).

**Prueba con `datos-oh-ne-mn`** (OH, NE, MN; zips bajados del release y verificados con su
`.sha256`, 2026-11-15):

| tabla | filas | columnas antes | columnas después |
|---|---|---|---|
| `tabla_anual.csv` | 23016 | 73 | 92 (+7 economía, +7 paisaje, +5 censo) |
| `tabla_mensual.csv` | 83616 | 48 | 54 (+6 NLDAS) |
