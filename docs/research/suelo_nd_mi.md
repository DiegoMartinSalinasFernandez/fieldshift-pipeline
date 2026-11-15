# SSURGO y NASADEM en Dakota del Norte y Míchigan

Pregunta: ¿qué áreas de levantamiento de SSURGO están publicadas en ND y MI? ¿Alguna es `NOTCOM`? ¿Cuántos
condados quedan con menos del 90 % del área con `mukey`? ¿Las columnas que usa `suelo_terreno` (`Valu1`,
`muaggatt`, `chorizon`) tienen dato? ¿Existen las 37 teselas NASADEM de cada estado?

Respuesta corta:

- **ND está completo y es el caso fácil.** Hay 53 áreas de levantamiento, una por condado y con el código del
  condado (`ND001` = Adams, …), todas publicadas en SDA (versiones del 1 al 17 de septiembre de 2026). No hay
  unidades `NOTCOM`, Σ `muacres` = `areaacres` en las 53 áreas y, según `laoverlap`/`muaoverlap`, **los 53
  condados tienen el 100 % del área con `mukey`**. `fips_de_area()` de `src/suelo_terreno/process.py` los
  convierte bien sin cambios.
- **MI tiene 82 áreas para 83 condados, todas publicadas** (25 de agosto al 1 de septiembre de 2026) y **sin
  `NOTCOM`**. Pero 4 áreas no son "un condado con su código": `MI600` (Lake y Wexford), `MI614` (Benzie y
  Manistee), `MI605` (Keweenaw County Area) y `MI606` (Isle Royale National Park, que es parte de Keweenaw). Con
  el `fips_de_area()` de hoy darían FIPS que no existen (`26600`, `26605`, `26606`, `26614`) y **5 condados
  quedarían sin suelo: Benzie, Keweenaw, Lake, Manistee y Wexford**. Es el mismo problema que KY, en chico.
- **Condados con menos del 90 % del área con `mukey`: ninguno en ND; en MI, solo Keweenaw "en los papeles".**
  En `muaoverlap`, la parte de Isle Royale (`MI606`, 141.926 ac) tiene las 77 unidades pero con `areaovacres`
  vacío, así que la cuenta por condado da 62,6 % para Keweenaw. No es un hueco del levantamiento: `MI606` tiene
  sus `mukey` (y 408.506 ac de "Water (Lake Superior)"). Además, MI tiene 9 unidades "Area not surveyed, access
  denied" (`ANS`, 11.731 ac en total, la mayor 3.603 ac en Otsego): tienen `mukey` pero no datos, y el filtro de
  `NOTCOM` no las agarra. En ningún condado llegan al 2 % del área.
- **Las columnas tienen dato.** ND: agua disponible 100 %, drenaje 99,3 %, grupo hidrológico 99,0 %, NCCPI
  95,5 % y textura 0–30 cm 99,7 % de los horizontes. MI un poco menos: 99,1 %, 98,5 %, 98,5 %, NCCPI 92,9 %,
  textura 93,1 % y factor K 85,1 % de los horizontes (el más bajo de los estados medidos hasta ahora).
- **NASADEM: las 37 teselas de ND y las 37 de MI responden HEAD 200** en Planetary Computer: 288,3 MB (ND) y
  205,8 MB (MI). Coincide con `cuarta_tanda.md`.

Detalle:

### Cómo lo verifiqué

`docs/research/suelo_nd_mi_sda.py` repite las consultas de `suelo_ky_sda.py` (T087) con el estado como
parámetro y en paralelo (SDA tardaba ~1 min por consulta), más los condados del Census para comparar. Son
consultas chicas a Soil Data Access (`post.rest`), agregadas en el servidor y sin bajar tablas. Los HEAD de
NASADEM usan la misma regla de teselas que `src/suelo_terreno/download.py`. Los condados salen de
`cb_2023_us_county_500k` del Census, en `/tmp` (fuera del repo). Hice cuatro consultas más a mano para MI:
unidades `ANS`, `laoverlap` de las 4 áreas raras y las unidades de `MI606`. No toca `data/` ni `config/`. Se
corrió el 2026-11-15:

```
.venv/bin/python -X utf8 docs/research/suelo_nd_mi_sda.py ND,MI /tmp/t102cb
```

### Áreas de levantamiento

| | ND | MI |
|---|---|---|
| Áreas en `sacatalog` | 53 | 82 |
| Condados del Census | 53 | 83 |
| Versión publicada (`saverest`) | 2026-09-01 a 2026-09-17 | 2026-08-25 a 2026-09-01 |
| Unidades `NOTCOM` | 0 | 0 |
| Unidades `ANS` ("Area not surveyed, access denied") | 0 | 9 (11.731 ac) |
| Áreas de un solo condado con su código | 53 | 78 |
| Áreas con otro código | — | `MI600` Lake+Wexford, `MI614` Benzie+Manistee, `MI605` Keweenaw County Area, `MI606` Isle Royale NP (Keweenaw) |
| Áreas con Σ `muacres` ≠ `areaacres` | 0 | 1 (`MI606`: 550.432 contra 141.926 ac, por 408.506 ac de agua del lago Superior) |

Unidades `ANS` de MI, por área: `MI137` Otsego 3.603 ac, `MI614` 1.939, `MI007` Alpena 1.924, `MI135` Oscoda
1.469, `MI119` Montmorency 877, `MI143` Roscommon 791, `MI069` Iosco 743, `MI079` Kalkaska 269 y `MI077`
Kalamazoo 116. Son unidades con `mukey` y un componente "AREA NOT SURVEYED" sin horizontes: `suelo_terreno`
las dejaría vacías en la media ponderada, como el agua o la zona urbana.

### Cobertura por condado

- **Por área de levantamiento:** Σ `muacres` = `areaacres` y sin acres `NOTCOM` en las 53 áreas de ND y en 81
  de las 82 de MI (la excepción es `MI606`, arriba). El agua suma 1.049.900 ac en ND (máximo 146.875 ac en
  `ND055` McLean, que bordea el lago Sakakawea) y 1.609.799 ac en MI.
- **Por condado** (`laoverlap` con `areatypename = 'County or Parish'` + `muaoverlap`): en ND hay 53 filas,
  una por condado, todas con el 100 % del área con `mukey`. En MI hay 84 filas para los 83 condados (Keweenaw
  aparece dos veces, por `MI605` y `MI606`). Todos dan 100 % salvo la fila de `MI606`, que tiene las 77
  unidades en `muaoverlap` pero sin `areaovacres`. Si se toma literal, Keweenaw queda con 237.453 de 379.379 ac
  (62,6 %). Es un dato que falta en la tabla de superposición, no un hueco del levantamiento. Isle Royale es
  parque nacional, sin agricultura.
- **Los acres de `laoverlap` incluyen el agua interior.** Dan entre 1,00 y 1,10 veces la tierra del Census
  (`ALAND`) en ND (más en McLean, Ramsey y Mercer, por los lagos) y hasta 1,14 en MI. No incluyen los Grandes
  Lagos, que el Census cuenta en `AWATER`.
- **Límite:** igual que en KY, es la superficie tabular de SDA, no conté píxeles con `mukey` en el raster de
  gSSURGO o gNATSGO.

### Columnas que usa `suelo_terreno`

Unidades sin agua ni `NOTCOM`: ND 9.374 `mukey` (44.202.220 ac ≈ 178.880 km²; el Census da 178.694 km² de
tierra), MI 10.581 `mukey` (36.256.124 ac ≈ 146.723 km²; Census 146.620 km²).

| Tabla | Columna | ND: `mukey` o filas con dato | ND: % del área | MI: `mukey` o filas con dato | MI: % del área |
|---|---|---|---|---|---|
| `muaggatt` | `aws0100wta` / `aws0150wta` | 9.353 / 9.374 | 100,0 % | 10.281 / 10.581 | 99,1 % |
| `muaggatt` | `drclassdcd` | 9.265 / 9.374 | 99,3 % | 10.191 / 10.581 | 98,5 % |
| `muaggatt` | `hydgrpdcd` | 9.172 / 9.374 | 99,0 % | 10.178 / 10.581 | 98,5 % |
| `muaggatt` | `wtdepannmin` | 5.401 / 9.374 | 58,7 % (vacío = napa a más de 200 cm) | 5.305 / 10.581 | 57,0 % |
| `cointerp` (NCCPI general, maíz y soja; componentes mayores) | `interphr` | — | 95,5 % | — | 92,9 % |
| `chorizon` (horizontes de componentes mayores que empiezan a menos de 30 cm) | `sandtotal_r` / `claytotal_r` | 34.958 / 34.966 de 35.076 | 99,7 % de los horizontes | 32.849 / 32.847 de 35.267 | 93,1 % |
| | `om_r` | 35.034 / 35.076 | 99,9 % | 34.952 / 35.267 | 99,1 % |
| | `ph1to1h2o_r` | 35.034 / 35.076 | 99,9 % | 33.305 / 35.267 | 94,4 % |
| | `dbthirdbar_r` | 35.034 / 35.076 | 99,9 % | 34.905 / 35.267 | 99,0 % |
| | `kwfact` | 34.932 / 35.076 | 99,6 % | 29.997 / 35.267 | 85,1 % |

- Las tres reglas NCCPI tienen el mismo número de valores: 59.342 de 60.271 filas en ND y 35.066 de 36.240 en
  MI (contando también los componentes menores).
- **Componentes mayores sin horizontes:** ND 319 de 16.636 (3,3 % del área): agua (1.048.602 ac), zona urbana,
  escombreras (*dumps*, de la minería de lignito), afloramiento rocoso y cauces. MI 492 de 14.461 (4,9 % del
  área): agua (1.238.299 ac), zona urbana (188.750), canteras (*pits*), afloramiento rocoso, dunas, roca
  caliza, *slickens* (relaves de minería), `ANS`, rellenos y playas. No son suelos agrícolas.
- **Sin textura en MI:** el 6,9 % de los horizontes de 0–30 cm no tiene arena, limo ni arcilla. No lo
  desglosé por componente. Lo más probable es que sean suelos orgánicos (como Lupton y Cathro, que aparecen
  en `MI606`: turbas o *mucks*, donde SSURGO deja la textura mineral vacía), pero **no lo verifiqué**. Si es
  así, `clase_textural()` los dejaría vacíos, y eso está bien.
- **`Valu1`:** igual que en KY, `suelo_terreno` no lo baja: el agua disponible sale de `muaggatt` y el SOC se
  calcula de `chorizon`. Probé `SELECT TOP 1 * FROM valu1` en SDA y no respondió en 60 s, así que no sé si
  la tabla está publicada en SDA. No hace falta para el paquete.

### Qué pasaría hoy con `suelo_terreno`

- **ND:** las 53 áreas dan su FIPS (`38001`…`38105`) y no hace falta tocar nada.
- **MI:** 78 condados salen bien. `MI600`, `MI605`, `MI606` y `MI614` darían FIPS inexistentes y quedarían sin
  fila de suelo Benzie (26019), Keweenaw (26083), Lake (26085), Manistee (26101) y Wexford (26165). No
  medí cuánta agricultura tiene cada uno.

**Propuesta para `suelo_terreno`** (no la hice: es código de otro paquete y MI no está en `config.yaml`):

1. Lo mejor es lo que propone `suelo_ky.md`: ponderar por `laoverlap`/`muaoverlap` del condado. Así se
   resuelven KY, MI y los `AREAS_ESPECIALES` de MN con una sola regla. En MI hay que tratar `MI606`, que tiene
   `areaovacres` vacío: o se lo deja afuera (Isle Royale no es agrícola) o se usa `muacres` sin el agua del
   lago Superior.
2. Alternativa mínima para MI: agregar a `AREAS_ESPECIALES` `"MI605": "26083"` y `"MI606": None` (o
   `"26083"`). Para `MI600` y `MI614`, que son dos condados cada una, el diccionario de hoy no alcanza (asigna
   un área a un solo FIPS). Habría que repartirlas por `laoverlap` o duplicar el área en los dos condados, y
   así se pierde la diferencia de suelos entre ellos.
3. Las unidades `ANS` conviene tratarlas como `NOTCOM` (sin dato) en el filtro de `process.py`. Hoy no tienen
   horizontes, así que ya quedan vacías, pero sus `muaggatt` vacíos bajan la cobertura de esas columnas.

### NASADEM

- **ND:** las 37 teselas de 1° (`n45w097`–`n45w105`, `n46w097`–`n46w105`, `n47w097`–`n47w105`,
  `n48w098`–`n48w105`, `n49w098`, `n49w099`) responden **HEAD 200** y suman 288,3 MB.
- **MI:** las 37 teselas (`n41w084`–`n41w087`, `n42w083`–`n42w087`, `n43w083`–`n43w087`, `n44w083`–`n44w087`,
  `n45w084`–`n45w089`, `n46w084`–`n46w091`, `n47w088`–`n47w090`, `n48w089`) responden **HEAD 200** y suman
  205,8 MB. Pesan menos que las de ND porque muchas son casi todo lago.

Fuentes:
- [Soil Data Access (USDA NRCS), servicio `post.rest`, tablas `sacatalog`, `legend`, `mapunit`, `muaggatt`, `component`, `chorizon`, `cointerp`, `laoverlap` y `muaoverlap`](https://sdmdataaccess.sc.egov.usda.gov/), consultado 2026-11-15
- [NASADEM COG en Planetary Computer](https://planetarycomputer.microsoft.com/dataset/nasadem) (HEAD de 74 teselas), consultado 2026-11-15
- [US Census Cartographic Boundary, condados 1:500k 2023](https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip), consultado 2026-11-15

Confianza: **alta** en las áreas publicadas, la ausencia de `NOTCOM`, la relación entre áreas y condados, las
unidades `ANS`, el dato por columna y NASADEM (todo consultado y contado). **Media** en "100 % del área con
`mukey`" (superficie tabular de SDA, no medida en el raster) y en Keweenaw (el 62,6 % viene de un campo vacío
en `muaoverlap`, no de un hueco). **Baja** en el motivo de la textura faltante en MI (no verificado).

Impacto: ND entra en `suelo_terreno` sin cambios. Para MI hay que adaptar el reparto por condado de
`src/suelo_terreno/process.py` antes de procesarlo (propuesta arriba, sería una tarea nueva, idealmente la
misma que la de KY). `config/config.yaml` no cambia por este research. Completa la fila de SSURGO de
`docs/research/cuarta_tanda.md` para MI y ND.
