# Qué paquetes y columnas le faltan a `src/merge.py`

Pregunta: ¿qué archivos anuales, estáticos y mensuales de los paquetes no une hoy `src/merge.py`? ¿Qué
choques de nombres de columna aparecerían al sumarlos? ¿Cómo entran los archivos con otra granularidad? ¿En
qué orden conviene hacer los cambios?

Respuesta corta: `merge.py` une 6 archivos anuales o estáticos y 3 mensuales. El spec
(`loop/spec/entregables.yaml`, paquete `merge`) pide **todos**, así que faltan 4 anuales o estáticos
(`economia_anual`, `economia_forrajes_anual`, `paisaje_anual` y `teledeteccion_anual`), uno estático sin
código en este repo (`aptitud_estatico`), 3 mensuales con código (`validacion`, `ecostress` y `nldas`) y uno
mensual sin código (`hidrologia`). Hay un solo choque exacto de nombres, `flag_nass` (en producción y en los
dos archivos de economía), y **con el renombrado actual termina en `economia_flag_nass_x` y
`economia_flag_nass_y`**. Hay además un duplicado de contenido: `et_mm` de `vegetacion_mensual` y
`et_nldas_mm` de `nldas_mensual` salen los dos de NLDAS-2 Noah `Evap`. Propuesta: primero sincronizar con
ResearchAgent (T008), después cambiar el renombrado, sacar la lista de archivos del spec y sumar los paquetes
de a uno.

Esta es una propuesta: `src/merge.py` no se tocó.

---

## Detalle

### Fuentes que se revisaron

- `src/merge.py` (la versión de este repo, commit `fe7a8aa`), `tests/test_merge.py`.
- `src/<paquete>/process.py` de economia, paisaje, teledeteccion, validacion, ecostress, nldas, vegetacion,
  agua, clima, cultivos y suelo_terreno (archivos que escriben y columnas).
- `loop/spec/entregables.yaml` (rutas, claves y columnas de cada archivo, y la descripción del paquete
  `merge`).
- `docs/datasets/*.md`, `docs/estructura_csv.md` y `docs/guia_tablas.md`.

En esta máquina no hay `data/processed/`, así que las columnas salen del código y del spec, no de los CSV
reales. Antes de cambiar `merge.py`, comparalas con `head -1` de cada CSV publicado en los Releases.

### 1. Archivos por paquete y si `merge.py` los une hoy

"Hoy" quiere decir la lista fija `ANUALES` / `MENSUALES` de `src/merge.py`.

| Paquete | Archivo | Claves | Va a | ¿Lo une hoy? | Código en este repo |
|---|---|---|---|---|---|
| cultivos | `produccion_anual.csv` | `fips, anio, cultivo` | `tabla_anual` (base) | sí, es la base | `src/cultivos/process.py` |
| cultivos | `rotacion_anual.csv` | `fips, anio` | `tabla_anual` | sí | ídem |
| cultivos | `fenologia_estado.csv` | `fips_estado, anio, cultivo` | `tabla_anual` | sí, por `fips[:2]` | ídem |
| cultivos | `rotacion_secuencia.csv` | `fips, ventana` | afuera (ver §3) | no, a propósito | ídem |
| cultivos | `practicas_censo.csv` | `fips, anio_censo` | afuera (ver §3) | no, a propósito | ídem |
| clima | `clima_anual.csv` | `fips, anio` | `tabla_anual` | sí | `src/clima/process.py` |
| clima | `clima_mensual.csv` | `fips, anio, mes` | `tabla_mensual` | sí | ídem |
| vegetacion | `fenologia_anual.csv` | `fips, anio` | `tabla_anual` | sí | `src/vegetacion/process.py` |
| vegetacion | `vegetacion_mensual.csv` | `fips, anio, mes` | `tabla_mensual` | sí | ídem |
| agua | `agua_mensual.csv` | `fips, anio, mes` | `tabla_mensual` | sí | `src/agua/process.py` |
| suelo_terreno | `suelo_terreno_estatico.csv` | `fips` | `tabla_anual` | sí | `src/suelo_terreno/process.py` |
| **economia** | `economia_anual.csv` | `fips_estado, anio, cultivo` | `tabla_anual` | **no** | `src/economia/process.py` |
| **economia** | `economia_forrajes_anual.csv` | `fips_estado, anio, cultivo` | `tabla_anual` | **no** | ídem |
| **paisaje** | `paisaje_anual.csv` | `fips, anio` | `tabla_anual` | **no** | `src/paisaje/process.py` |
| **teledeteccion** | `teledeteccion_anual.csv` | `fips, anio` | `tabla_anual` | **no** | `src/teledeteccion/process.py` |
| **aptitud** | `aptitud_estatico.csv` | `fips` | `tabla_anual` | **no** | **no hay** `src/aptitud/` (solo en el spec) |
| **validacion** | `validacion_mensual.csv` | `fips, anio, mes` | `tabla_mensual` | **no** | `src/validacion/process.py` |
| **ecostress** | `ecostress_mensual.csv` | `fips, anio, mes` | `tabla_mensual` | **no** | `src/ecostress/process.py` |
| **nldas** | `nldas_mensual.csv` | `fips, anio, mes` | `tabla_mensual` | **no** | `src/nldas/process.py` |
| **hidrologia** | `hidrologia_mensual.csv` | `fips, anio, mes` | `tabla_mensual` | **no** | **no hay** `src/hidrologia/` (solo en el spec) |

Columnas de los archivos que faltan (según `process.py` y el spec; coinciden en los que tienen código):

| Archivo | Columnas no clave |
|---|---|
| `economia_anual.csv` | `precio_usd_bu`, `valor_produccion_usd_ac`, `costo_operativo_usd_ac`, `costo_total_usd_ac`, `margen_operativo_usd_ac`, `flag_nass` |
| `economia_forrajes_anual.csv` | `precio_usd_ton`, `flag_nass` |
| `paisaje_anual.csv` | `pct_cultivos_nlcd`, `pct_pasturas_heno_nlcd`, `pct_bosque_nlcd`, `pct_humedales_nlcd`, `pct_urbano_nlcd`, `pct_agua_nlcd`, `impermeable_pct` |
| `teledeteccion_anual.csv` | `pct_suelo_desnudo_abr_may`, `pct_suelo_desnudo_oct_nov`, `pct_cobertura_verde_mar_abr`, `bsi_abr_may`, `ndvi_max_30m`, `n_escenas_validas`, `frac_pixeles_validos` |
| `aptitud_estatico.csv` (solo spec) | `aptitud_<maiz,soja,trigo,avena,alfalfa>_<1981_2010,2041_2070>`, `rend_alcanzable_<maiz,soja,trigo>_kgha_<1981_2010,2041_2070>` |
| `validacion_mensual.csv` | `prec_prism_mm`, `tmax_prism_c`, `tmin_prism_c`, `tmed_prism_c`, `prec_cocorahs_mm`, `n_estaciones_cocorahs` |
| `ecostress_mensual.csv` | `lst_ecostress_c`, `et_ecostress_mm_dia`, `esi_ecostress`, `n_pasadas_ecostress` |
| `nldas_mensual.csv` | `sm_0_10cm_m3m3`, `sm_0_100cm_m3m3`, `sm_0_100cm_anom_z`, `et_nldas_mm`, `escorrentia_nldas_mm`, `swe_nldas_mm` |
| `hidrologia_mensual.csv` (solo spec) | `napa_prof_m`, `n_pozos`, `caudal_pctl`, `n_estaciones_aforo` |

Cobertura que dicen los data cards (para saber qué columnas van a quedar casi vacías):

- `paisaje`: 293 condados (IA, IL, IN), 2000–2024. 2025 queda vacío.
- `teledeteccion`: varias columnas solo desde 2019; cobertura parcial de escenas.
- `ecostress`: 83 condados (ventana de muestra), abril a octubre, desde 2018-08.
- `validacion`: 2000-01 a 2025-12; CoCoRaHS desde 2008.
- `nldas`: desde 1979; en la tabla, desde 2000.
- `economia`: por estado, con huecos en los precios (trigo de invierno en IA después de 2019, avena en IN
  después de 2015).

`aptitud` e `hidrologia` no tienen código ni data card en este repo, solo la entrada en el spec (y la
descripción de `docs/estructura_csv.md`). Hasta que alguien los traiga de ResearchAgent o los haga, no hay
nada que unir. Que `merge.py` los saltee con el "aviso: falta" que ya tiene `leer()`.

### 2. Choques de nombres de columna

Se buscó cada columna no clave en todos los archivos que irían a la misma tabla (anuales y estáticos por un
lado, mensuales por el otro).

**Choques exactos (mismo nombre en dos archivos de la misma tabla):**

| Columna | Archivos | Qué pasa con el `merge.py` de hoy | Propuesta |
|---|---|---|---|
| `flag_nass` | `produccion_anual`, `economia_anual`, `economia_forrajes_anual` | `renombrar_colisiones` antepone el **paquete**, y los dos archivos de economía son del mismo paquete: los dos se renombran a `economia_flag_nass`, ese nombre choca otra vez y pandas lo parte en `economia_flag_nass_x` y `economia_flag_nass_y`. Probado con CSV inventados en una carpeta temporal (ver §5). | (a) Unir antes `economia_anual` y `economia_forrajes_anual` en un solo bloque: tienen las mismas claves y cultivos que no se pisan (granos y forrajes). Queda un solo `flag_nass`, que se renombra a `economia_flag_nass`. (b) Además, que el prefijo salga del **nombre del archivo** sin `.csv` (`economia_forrajes_anual_flag_nass`) y no del paquete, y que `merge.py` corte con error si el nombre nuevo ya existe, en lugar de dejar que pandas agregue `_x` / `_y`. Recomiendo (a) + el error de (b). |

**Mismo nombre en tablas distintas (no chocan, pero confunden):**

- `frac_pixeles_validos`: está en `teledeteccion_anual` (va a `tabla_anual`) y en `vegetacion_16d` (no entra
  en ninguna tabla). Hoy no choca. Si algún día otro archivo anual la agrega (por ejemplo `fenologia_anual`),
  el choque va a ser real. Se podría renombrar a `frac_pixeles_validos_landsat` en `teledeteccion`, pero eso
  cambia el esquema de un CSV procesado y lo decide el humano. Mientras tanto, que la regla de §2 lo resuelva.
- Las columnas de `clima_diario` / `clima_mensual`, `vegetacion_16d` / `vegetacion_mensual` y `agua_diario` /
  `agua_mensual` se repiten a propósito (la misma variable con otra resolución). No hay problema porque los
  diarios y los de 16 días no entran.

**Duplicados de contenido con distinto nombre (no son choques, pero conviene que ML los conozca):**

| Columnas | Por qué | Propuesta |
|---|---|---|
| `et_mm` (`vegetacion_mensual`) y `et_nldas_mm` (`nldas_mensual`) | Las dos son NLDAS-2 Noah `Evap` sumado en el mes (`src/vegetacion/process.py` l. 261–297 y `src/nldas/process.py`). Podrían diferir solo por cómo se pondera cada celda en el condado. | Unir las dos y anotarlo en `docs/datasets/merge.md` y `docs/guia_tablas.md`. Si se confirma que son iguales, que el humano decida si `vegetacion` deja de calcularla (cambio de esquema). |
| `prec_imerg_mm`, `prec_power_mm`, `prec_prism_mm`, `prec_cocorahs_mm` | Cuatro medidas de la lluvia del mes; PRISM y CoCoRaHS no son de la NASA y están para validar. | Unir las cuatro y aclarar en la guía que `validacion` no es una fuente más para el modelo. |
| `sm_rootzone_m3m3` (SMAP, 2015+) y `sm_0_100cm_m3m3` (NLDAS, 2000+) | Humedad de suelo de dos fuentes, profundidades distintas. | Unir las dos (son complementarias en el tiempo). |
| `napa_min_cm` (gSSURGO, estático) y `napa_prof_m` (USGS, mensual) | Una es la profundidad mínima de la napa según el suelo y la otra la medida en pozos. | Sin cambios: nombres y unidades ya las distinguen. |

### 3. Archivos con otra granularidad

| Archivo | Unidad | Cómo entraría | Recomendación |
|---|---|---|---|
| `fenologia_estado.csv` | estado × año × cultivo | por `fips_estado = fips[:2]`, `anio`, `cultivo` (ya lo hace) | dejar como está |
| `economia_anual.csv` + `economia_forrajes_anual.csv` | estado × año × cultivo | igual que `fenologia_estado`: por `fips[:2]`, `anio`, `cultivo`, `validate="many_to_one"`. Los valores de `cultivo` coinciden con los de `produccion_anual` (`maiz`, `soja`, `trigo_invierno`, `avena`, `alfalfa`, `heno`; verificado en `src/economia/process.py`) | unir, como un solo bloque (§2) |
| `aptitud_estatico.csv` | condado, fijo | por `fips`, como `suelo_terreno_estatico` | unir cuando exista |
| `practicas_censo.csv` | condado × año de censo (2012, 2017, 2022) | tres opciones: (1) afuera, como hoy; (2) unión "as-of": cada `anio` toma el último censo con `anio_censo <= anio` (2012–2016 → 2012, 2017–2021 → 2017, 2022+ → 2022; antes de 2012, vacío), más una columna `anio_censo_ref`; (3) pivotear a columnas fijas `pct_riego_2012`, `pct_riego_2017`... | **(2)** si el humano lo aprueba, porque no usa datos del futuro. La (3) le pasa al año 2012 el censo de 2022. Como la (2) agrega una columna nueva a la tabla, es un cambio de esquema: decide el humano o ML. Mientras no se decida, (1). |
| `rotacion_secuencia.csv` | condado × ventana de 8 años (2008–2015 a 2018–2025) | (1) afuera, como hoy; (2) "as-of" por la ventana que termina en `anio − 1` (sin datos del año de cosecha), con `ventana_ref`: cubre 2016–2026 | **(1)** por ahora. La (2) es una decisión de modelado (qué ventana corresponde a cada año) y la puede hacer ML con dos líneas de pandas. |
| `clima_diario`, `vegetacion_16d`, `agua_diario`, `agua_semanal` | día, 8/16 días o semana | no entran: `tabla_mensual` es mensual | afuera (ya lo dice `docs/guia_tablas.md` §5) |
| `data/processed/lotes/*` | lote y píxel | no entran (`fuera_de_tablas: true` en el spec) | afuera; que `merge.py` saltee los paquetes con esa marca |
| `data/interim/economia/pesos_region_ers.csv`, `data/interim/ecostress/*` | intermedios | no están en `processed/` | no aplica |

**Por estado y entre máquinas.** Cada máquina publica sus estados en su propio release. `merge.py` lee solo
`data/processed/` local, así que la máquina coordinadora primero tiene que bajar los releases de todos los
estados y concatenar, archivo por archivo, las filas de cada estado (los `fips` no se pisan porque empiezan
con el código del estado). Eso no está en `merge.py`: se propone un paso previo o una función
`juntar_estados()` en `merge.py` (o en `scripts/entregar.py`) que concatene y verifique que no haya claves
duplicadas. Esto también es parte de T008.

### 4. Orden propuesto de los cambios

1. **T008: sincronizar `src/merge.py` con la versión de ResearchAgent.** Es lo que pide la tarea antes de
   cualquier cambio. La versión de ResearchAgent puede tener ya la lista dinámica que pide el spec. Comparar
   después de sincronizar con esta propuesta y quedarse con lo que falte.
2. **Arreglar el renombrado por colisión** (§2): prefijo con el nombre del archivo, error si el nombre nuevo
   ya existe y nunca `_x` / `_y`. Sumar a `tests/test_merge.py` un caso con dos archivos del mismo paquete que
   tengan `flag_nass`.
3. **Sacar la lista de archivos de `loop/spec/entregables.yaml`** (las rutas `*_anual.csv`, `*_estatico.csv`
   y `*_mensual.csv` de los paquetes sin `fuera_de_tablas`) en lugar de las listas fijas `ANUALES` /
   `MENSUALES`, como pide el spec. Las claves de cada archivo salen de `claves`; si incluye `fips_estado`, se
   une por `fips[:2]`. Excluir `rotacion_secuencia` y `practicas_censo` por nombre (o por clave que no sea
   `fips`, `fips_estado`, `anio`, `cultivo`, `mes`). Los archivos que no estén en disco se saltean con aviso,
   como hoy.
4. **Sumar los paquetes que ya tienen código**, de a uno y corriendo el test cada vez: `paisaje`,
   `teledeteccion` y `nldas` (sin choques); `validacion` y `ecostress` (sin choques; documentar que son de
   validación o de muestra); `economia` al final, juntando sus dos archivos en un bloque (§2).
5. **Actualizar `docs/datasets/merge.md` y `docs/guia_tablas.md`**: sacar el "(prevista)" de lo que entre,
   anotar `economia_flag_nass` y el duplicado `et_mm` / `et_nldas_mm`.
6. **`aptitud` e `hidrologia`**: entran solos con el paso 3 cuando alguien los traiga o los haga; no hace
   falta tocar `merge.py`.
7. **Decisiones del humano o de ML** (no hacer sin OK): unión "as-of" de `practicas_censo` y de
   `rotacion_secuencia` (§3), y renombrar `frac_pixeles_validos` o sacar `et_mm` de `vegetacion` (§2).
8. **Juntar estados** antes de unir (§3), en la máquina coordinadora.

### 5. Cómo se probó el choque de `flag_nass`

Con `.venv/bin/python`, en una carpeta temporal: un `produccion_anual.csv` con `flag_nass`, un
`economia_anual.csv` y un `economia_forrajes_anual.csv` con `fips_estado, anio, cultivo, ..., flag_nass`. Se
apuntó `merge.PROC` a esa carpeta y se reemplazó `merge.ANUALES` en memoria por los dos archivos de economía
(sin editar `src/merge.py`). `merge.tabla_anual()` devolvió las columnas
`fips, anio, cultivo, rend_bu_ac, flag_nass, precio_usd_bu, economia_flag_nass_x, precio_usd_ton,
economia_flag_nass_y`.

---

Fuentes: archivos del repo `src/merge.py`, `src/*/process.py`, `loop/spec/entregables.yaml`,
`docs/datasets/*.md`, `docs/estructura_csv.md`, `docs/guia_tablas.md`, consultados 2026-11-15. No se usaron
fuentes externas.

Confianza: alta para la lista de archivos y columnas (código y spec coinciden) y para el choque de
`flag_nass` (probado). Media para el duplicado `et_mm` / `et_nldas_mm` (mismo producto y variable según el
código; no se compararon valores porque no hay CSV en esta máquina). Baja para lo que pueda traer la versión
de ResearchAgent de `merge.py` (no se vio).

Impacto: `src/merge.py`, `tests/test_merge.py`, `docs/datasets/merge.md`, `docs/guia_tablas.md`; nada en
`config/` ni en `src/common/`. Los cambios de esquema (§2 y §3) quedan para el humano.
