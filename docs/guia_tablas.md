# Guía de las tablas unidas (para el equipo de ML)

Esta guía explica cómo leer `data/processed/tabla_anual.csv` y `data/processed/tabla_mensual.csv`, las dos
tablas que arma `src/merge.py`. No repite el diccionario de cada columna: ese está en el data card de cada
paquete (`docs/datasets/<paquete>.md`). Acá está lo que hay que saber para usarlas sin sorpresas.

Fuentes de esta guía: `src/merge.py`, `loop/spec/entregables.yaml`, `docs/datasets/*.md`,
`docs/estructura_csv.md` y la sección 4 del `CLAUDE.md`. Si una columna no figura en el spec o en un data
card, no la damos por existente.

> **Aviso: qué une `merge.py` hoy y qué prevé el spec.** El spec (`loop/spec/entregables.yaml`, paquete
> `merge`) pide que las tablas incluyan **todos** los archivos anuales, estáticos y mensuales de todos los
> paquetes. Pero el `src/merge.py` de este repo todavía tiene una lista fija:
>
> - `tabla_anual`: `produccion_anual` + `clima_anual`, `rotacion_anual`, `fenologia_anual`,
>   `fenologia_estado` y `suelo_terreno_estatico`.
> - `tabla_mensual`: `clima_mensual`, `vegetacion_mensual` y `agua_mensual`.
>
> Los bloques de las secciones 3 y 4 marcados **(prevista)** (economía, aptitud, paisaje, teledetección,
> validación, ECOSTRESS, NLDAS, hidrología) están en el spec y en `docs/estructura_csv.md`, pero no entran en
> las tablas hasta que `merge.py` se actualice. Antes de entrenar, mirá el encabezado real del CSV que te
> llegó: `head -1 data/processed/tabla_anual.csv`.

---

## 1. Qué es una fila

| Tabla | Una fila es | Claves (únicas, sin duplicados) |
|---|---|---|
| `tabla_anual.csv` | un condado, un año de cosecha y un cultivo | `fips`, `anio`, `cultivo` |
| `tabla_mensual.csv` | un condado y un mes | `fips`, `anio`, `mes` |

- `fips`: texto de 5 dígitos, 2 del estado y 3 del condado, con ceros a la izquierda (`19169` es Story, Iowa).
  **Leelo siempre como texto**: `pd.read_csv(..., dtype={"fips": str})`. Como número se pierde el cero
  inicial de los códigos que lo tengan y deja de servir para cruzar con otras tablas.
- **El estado** se reconoce por los dos primeros dígitos: `fips.str[:2]`. Zona de estudio (7 estados, 666
  condados según el `CLAUDE.md` §2): IA `19`, IL `17`, IN `18`, OH `39`, NE `31`, MN `27`, KS `20`.
- `anio`: año de la cosecha en la anual. En la mensual es el **año calendario del mes** (el mes `2023-11`
  tiene `anio = 2023`).
- `cultivo` (solo anual): `maiz`, `soja`, `trigo_invierno`, `avena`, `alfalfa`, `heno`.
- `mes`: texto `AAAA-MM`.
- Período: 2000 a 2025. La rotación (CDL) existe desde 2008.

### Qué filas hay (y cuáles no)

- `tabla_anual` es un *left join* sobre `produccion_anual.csv`: **solo existen las combinaciones condado ×
  año × cultivo que NASS publicó**. Un condado sin dato de NASS para un año no aparece, aunque haya clima ese
  año. Por eso el tamaño máximo teórico (condados × años × cultivos) es solo un techo.
- `tabla_mensual` es un *outer join*: un mes aparece si está en cualquiera de los paquetes que se unen.
- Los valores se copian como texto, sin reformatear. Al leer con pandas, el tipo de cada columna lo infiere
  pandas.

---

## 2. Qué se repite y dónde

Esto importa para no contar de más al entrenar o evaluar:

- **Por condado y año (clima, rotación, fenología MODIS, paisaje, teledetección):** el mismo valor se repite
  en la fila de cada cultivo de ese condado y año. Un condado con maíz y soja en 2019 tiene dos filas con el
  mismo `prec_temporada_mm`.
- **Estáticas por condado (suelo y terreno, aptitud):** el mismo valor en todos los años y cultivos del
  condado.
- **Por estado (Crop Progress, economía):** se unen por `fips_estado = fips[:2]` (y por `cultivo`). Todos los
  condados de un estado comparten el valor del mismo año y cultivo. Esa columna auxiliar no se guarda en la
  tabla.
- **Por cultivo:** solo `produccion_anual` (el target), `fenologia_estado` y la economía varían por cultivo.
  `fenologia_estado` tiene solo **maíz y soja**: en los demás cultivos las columnas `doy_50_*` quedan vacías.
- Consecuencia práctica: al dividir en folds, agrupá por condado (o por año) y no por fila, o los valores
  repetidos se filtran entre entrenamiento y validación.

---

## 3. `tabla_anual.csv`: de dónde sale cada bloque

El target es `rend_bu_ac` (o `rend_kgha`). Alfalfa y heno se miden en toneladas: sus `rend_bu_ac` y
`produccion_bu` están vacíos.

| Bloque | Columnas | Varía por | Data card |
|---|---|---|---|
| Producción y target (NASS) | `sup_sembrada_ac`, `sup_cosechada_ac`, `produccion_bu`, `rend_bu_ac`, `rend_kgha`, `sup_sembrada_ha`, `ratio_cosechada`, `flag_nass` | condado, año, cultivo | [cultivos](datasets/cultivos.md) |
| Clima del año | `doy_ultima_helada`, `doy_primera_helada`, `periodo_libre_heladas_dias`, `prec_temporada_mm`, `gdd_temporada`, `prec_invierno_previo_mm`, `prec_jul_mm`, `tmax_jul_c`, `dias_tmax_gt30_jul`, `prec_ago_mm`, `deficit_temporada_mm`, `tend_prec_mm_decada`, `tend_tmed_c_decada` | condado, año | [clima](datasets/clima.md) |
| Rotación (CDL) | `pct_maiz`, `pct_soja`, `pct_trigo`, `pct_alfalfa`, `pct_heno`, `pct_doble_trigo_soja`, `pct_barbecho`, `pct_maiz_tras_soja`, `pct_maiz_tras_maiz`, `pct_soja_tras_maiz`, `pct_soja_tras_soja` | condado, año (2008+) | [cultivos](datasets/cultivos.md) |
| Fenología por satélite (MODIS) | `doy_inicio`, `doy_pico`, `doy_fin`, `ndvi_max`, `duracion_dias`, `ndvi_integral`, `n_ciclos`, `ndvi_max_maiz`, `ndvi_max_soja`, `dias_ndvi_lt03_invierno` | condado, año | [vegetacion](datasets/vegetacion.md) |
| Fechas reales de siembra, emergencia, floración y cosecha (Crop Progress) | `doy_50_sembrado`, `doy_50_emergido`, `doy_50_floracion`, `doy_50_cosechado` | estado, año, cultivo (solo maíz y soja) | [cultivos](datasets/cultivos.md) |
| Suelo y terreno (gSSURGO, NASADEM) | `aws0_100_mm`, `aws0_150_mm`, `soc0_30_gm2`, `soc0_100_gm2`, `patron`, `prof_raices_cm`, `clase_drenaje`, `grupo_hidrologico`, `napa_min_cm`, `arcilla_pct`, `arena_pct`, `limo_pct`, `materia_organica_pct`, `ph_agua`, `clase_textural_usda`, `factor_k_rusle`, `elevacion_media_m`, `elevacion_desvio_m`, `pendiente_media_pct`, `pendiente_gt2_pct`, `twi_medio`, `twi_decil_sup_pct` | condado (fijo) | [suelo_terreno](datasets/suelo_terreno.md) |
| **(prevista)** Precios y costos (NASS, ERS) | `precio_usd_bu`, `valor_produccion_usd_ac`, `costo_operativo_usd_ac`, `costo_total_usd_ac`, `margen_operativo_usd_ac`, `flag_nass`; forrajes: `precio_usd_ton` | estado, año, cultivo | [economia](datasets/economia.md) |
| **(prevista)** Aptitud agroclimática y rendimiento alcanzable (FAO GAEZ) | `aptitud_<cultivo>_1981_2010`, `aptitud_<cultivo>_2041_2070`, `rend_alcanzable_<cultivo>_kgha_<período>` | condado (fijo) | sin data card propio; ver [estructura_csv](estructura_csv.md) |
| **(prevista)** Cobertura del suelo (NLCD) | `pct_cultivos_nlcd`, `pct_pasturas_heno_nlcd`, `pct_bosque_nlcd`, `pct_humedales_nlcd`, `pct_urbano_nlcd`, `pct_agua_nlcd`, `impermeable_pct` | condado, año | [paisaje](datasets/paisaje.md) |
| **(prevista)** Suelo desnudo y cobertura invernal a 30 m (Landsat) | `pct_suelo_desnudo_abr_may`, `pct_suelo_desnudo_oct_nov`, `pct_cobertura_verde_mar_abr`, `bsi_abr_may`, `ndvi_max_30m`, `n_escenas_validas`, `frac_pixeles_validos` | condado, año | [teledeteccion](datasets/teledeteccion.md) |

Notas del bloque de producción: la columna `flag_nass` guarda el código original cuando NASS oculta el dato
(`(D)`, `(Z)`); en esos casos el valor numérico va vacío.

La clave que une estos bloques y el nombre de cada columna no cambian al unir. Si dos paquetes tuvieran una
columna con el mismo nombre, la segunda se renombra `<paquete>_<columna>` (hoy no hay colisiones).

---

## 4. `tabla_mensual.csv`: de dónde sale cada bloque

`anio` es el año calendario del mes. Para usar la mensual junto con la anual hay que pivotear los meses a
columnas; el ejemplo está en [estructura_csv.md](estructura_csv.md).

| Bloque | Columnas | Data card |
|---|---|---|
| Clima (POWER, IMERG) | `prec_imerg_mm`, `prec_power_mm`, `tmax_c`, `tmin_c`, `tmed_c`, `rad_mj_m2`, `eto_pm_mm`, `deficit_mm`, `dias_tmax_gt30`, `dias_tmax_gt35`, `dias_tmin_le0`, `dias_tmin_le_m2`, `gdd_10_30`, `gdd_base0`, `dias_lluvia_ge1`, `prec_max1d_mm`, `prec_max5d_mm`, `dias_lluvia_gt50`, `racha_seca_max_dias`, `spi1`, `spi3`, `spi6`, `anom_tmed_c`, `gwettop`, `gwetroot`, `gwetprof` | [clima](datasets/clima.md) |
| Vegetación (MODIS) | `ndvi`, `evi`, `ndvi_maiz`, `ndvi_soja`, `lst_dia_c`, `lst_noche_c`, `et_mm`, `pet_mm`, `et_pet_ratio`, `ndvi_anom_z`, `vci`, `tci`, `vhi` | [vegetacion](datasets/vegetacion.md) |
| Agua (SMAP) | `sm_surface_m3m3`, `sm_rootzone_m3m3`, `sm_surface_min_m3m3`, `sm_rootzone_min_m3m3`, `sm_rootzone_anom_z`, `dias_sm_saturado` | [agua](datasets/agua.md) |
| **(prevista)** Validación (PRISM, CoCoRaHS) | `prec_prism_mm`, `tmax_prism_c`, `tmin_prism_c`, `tmed_prism_c`, `prec_cocorahs_mm`, `n_estaciones_cocorahs` | [validacion](datasets/validacion.md) |
| **(prevista)** ECOSTRESS | `lst_ecostress_c`, `et_ecostress_mm_dia`, `esi_ecostress`, `n_pasadas_ecostress` | [ecostress](datasets/ecostress.md) |
| **(prevista)** NLDAS-2 | `sm_0_10cm_m3m3`, `sm_0_100cm_m3m3`, `sm_0_100cm_anom_z`, `et_nldas_mm`, `escorrentia_nldas_mm`, `swe_nldas_mm` | [nldas](datasets/nldas.md) |
| **(prevista)** Hidrología (USGS NWIS) | `napa_prof_m`, `n_pozos`, `caudal_pctl`, `n_estaciones_aforo` | sin data card propio; ver [estructura_csv](estructura_csv.md) |

Ojo con la lluvia: `prec_imerg_mm` y `prec_power_mm` son dos medidas distintas de lo mismo, y `prec_prism_mm`
(cuando entre) es de superficie y **no es de la NASA**: sirve para validar, no como segunda fuente
independiente del modelo.

---

## 5. Qué queda afuera de las tablas y dónde está

| Qué | Archivo | Por qué no entra | Dónde está |
|---|---|---|---|
| Secuencia de 8 años (maíz-soja alternado, continuo, diversidad) | `rotacion_secuencia.csv` | claves `fips` + `ventana` de 8 años | `data/processed/cultivos/`; [cultivos](datasets/cultivos.md) |
| Prácticas del Censo (cobertura, labranza cero, drenaje con caños, riego) | `practicas_censo.csv` | solo existe en años de censo (2012, 2017, 2022); en 2012 faltan las prácticas salvo riego | `data/processed/cultivos/`; [cultivos](datasets/cultivos.md) |
| Series diarias y de 8/16 días | `clima_diario`, `vegetacion_16d`, `agua_diario`, `agua_semanal` | otra granularidad temporal | cada carpeta de `data/processed/<paquete>/` |
| Datos por lote y píxel (30 m) | paquete `lotes` | claves `fips`, `id_lote`, `px_id`; es una entrega aparte (`fieldshift_lotes_v1`) | `data/processed/lotes/`; [lotes](datasets/lotes.md) |

Se pueden unir a mano a la tabla que corresponda cuando haga falta. Por ejemplo, `practicas_censo` se asocia
al censo más cercano por condado, y eso es una decisión de modelado (ver sección 7).

---

## 6. Convenciones

- **Formato:** UTF-8, separador `,`, decimal `.`, encabezado en la primera fila.
- **Unidades en el nombre:** `rend_bu_ac`, `tmax_c`, `prec_power_mm`, `sm_rootzone_m3m3`. Los `bu/ac` y
  `acres` originales se guardan tal cual; las conversiones van en otra columna (`rend_kgha`,
  `sup_sembrada_ha`): maíz 62,77 kg/ha por bu/ac, soja y trigo 67,25, avena 35,87.
- **Faltantes:** celda vacía. **Nunca** `0`, `-999` ni `-9999`. Un vacío significa "no hay dato", no "cero".
  Al leer con pandas, cuidá de no tratar las celdas vacías como texto en columnas numéricas.
- **`flag_nass`:** código original de NASS cuando el valor está oculto (`(D)`: dato reservado para no revelar
  productores; `(Z)`: menos de la mitad de la unidad). El valor numérico va vacío.
- **Ventanas fijas de los archivos anuales** (las mismas en todos los paquetes):
  - temporada de crecimiento: abril a septiembre del `anio`;
  - invierno previo: noviembre del `anio − 1` a marzo del `anio`;
  - meses críticos: julio (floración del maíz) y agosto (llenado de la soja).

  Todavía no hay ventanas fenológicas por cultivo: esas se arman cuando `config/cultivos.csv` esté
  completo.
- **Agregación espacial:** media sobre el condado, con píxeles agrícolas cuando existe la máscara
  (`data/reference/mascara_agricola.tif`). Las columnas `frac_pixeles_validos` dicen qué parte de los
  píxeles se usó.
- **Anomalías z:** `spi*`, `anom_tmed_c`, `ndvi_anom_z`, `sm_rootzone_anom_z` y similares ya vienen calculadas
  por cada paquete contra su propia base (por ejemplo 1991–2020 para la temperatura). Son parte del dato
  entregado; no son lo que se prohíbe en la sección 7.

---

## 7. Lo que no se hace acá y lo que hay que tener en cuenta

**No se hace en el pipeline (lo decide ML, dentro de cada fold):**

- Sacar la **tendencia del rendimiento**. Los rendimientos vienen crudos, para no filtrar información del
  futuro al entrenar.
- Normalizar o estandarizar columnas, o calcular z-scores o percentiles nuevos sobre toda la tabla.
- Rellenar faltantes. Si imputás, hacelo dentro de cada fold.
- Armar ventanas por cultivo, sectores o umbrales.

**Advertencias que ya están en los data cards** (resumen; el detalle está en la sección "Problemas conocidos"
de cada uno):

- **Riego (Nebraska y Kansas).** Una parte grande del maíz y la soja se riega. El rendimiento de
  `ALL PRODUCTION PRACTICES` mezcla riego y secano, y no es comparable de forma directa con Iowa
  (tarea T004). El riego por condado está en `practicas_censo.csv`, solo en años de censo. Los costos de ERS
  tampoco separan riego y secano en Nebraska. NLDAS-2 no simula riego ni drenaje con caños.
- **Rendimientos de 2024 y 2025.** NASS publicó tarde los rendimientos de condado de 2024, y los de 2025
  pueden estar incompletos. Revisá la columna `hasta` del data card de cultivos y cuántas filas tiene cada
  año antes de usarlos para validar.
- **CDL de 2024 y 2025.** Viene a 10 m y sus bordes de lote no coinciden con los de la serie de 30 m. Los
  porcentajes de área (`pct_maiz`, `pct_soja`, etc.) de esos años pueden diferir algo de lo que daría un CDL
  de 30 m. Las transiciones (`pct_maiz_tras_soja`, etc.) lo corrigen con su denominador.
- **Rotación antes de 2008.** `rotacion_anual` empieza en 2008: de 2000 a 2007 esas columnas están vacías.
- **SMAP desde 2015.** Las columnas de `agua` están vacías antes de 2015-04. Además falta el día 2016-12-15,
  así que diciembre de 2016 queda vacío en `agua_mensual`. Para años anteriores a 2015, NLDAS-2
  (**prevista**) ofrece humedad de suelo desde 2000.
- **Valores de humedad de SMAP.** En algunas celdas del noreste de Indiana y en DuPage (IL) se excluyen
  celdas con humedad mayor a 0,60 m3/m3; en esos condados la media usa menos celdas o queda vacía.
  `dias_sm_saturado` usa un umbral fijo de 0,40 m3/m3, provisorio.
- **MODIS.** `et_mm`, `pet_mm` y `et_pet_ratio` de `vegetacion_mensual` **no** son MOD16A2: vienen de NLDAS-2
  Noah. El NDVI de maíz y soja queda vacío en condados sin píxeles con al menos 75 % del cultivo, y en invierno
  nubes y nieve dejan meses sin dato. Los compuestos de mediados de 2025 no están en origen
  (Planetary Computer): 2025 queda incompleto.
- **Clima.** POWER trae un punto por condado, así que condados vecinos dentro de la misma celda MERRA-2 tienen
  series idénticas. La radiación empieza en 1984 y el resto de la meteorología en 1981. IMERG viene de POWER,
  no de GES DISC.
- **Suelo y terreno.** Sin máscara agrícola, los promedios incluyen bosque, urbano y agua. `pendiente_gt2_pct`
  probablemente sobreestima el área con pendiente.
- **Paisaje (prevista).** NLCD anual llega hasta 2024: 2025 queda sin filas.
- **Teledetección (prevista).** Cobertura parcial de años y escenas (mirá `desde` y `hasta` en el data card):
  hay filas que pueden cambiar si se baja más escenas.
- **ECOSTRESS (prevista).** Solo abril a octubre, desde 2018-08, sobre una ventana de muestra y no el condado
  entero. Fuera de ese rango las columnas van vacías.
- **Economía (prevista).** NASS dejó de publicar el precio del trigo de invierno en Iowa después de 2019 y el
  de la avena en Indiana después de 2015.
- **Tablas viejas.** Las tablas reflejan los CSV de cada paquete al momento de correr `merge.py`. Si un
  paquete se reprocesa o se suma uno nuevo, hay que volver a correrlo: `python src/merge.py` (tarda poco y
  es determinista).

---

## 8. Cómo empezar

```python
import pandas as pd

anual = pd.read_csv("data/processed/tabla_anual.csv", dtype={"fips": str})
anual["estado"] = anual["fips"].str[:2]

# Maíz, con rendimiento publicado
maiz = anual[(anual["cultivo"] == "maiz") & anual["rend_bu_ac"].notna()]

# Agrupá por condado o por año al partir en folds (ver sección 2)
```

Para sumar los meses de la temporada como columnas, usá el ejemplo de `docs/estructura_csv.md`.
