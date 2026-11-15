# SSURGO y NASADEM en Kentucky

Pregunta: ¿qué áreas de levantamiento de SSURGO están publicadas en Kentucky? ¿Alguna es `NOTCOM`? ¿Cuántos
condados quedan con menos del 90 % del área con `mukey`? ¿Las columnas que usa `suelo_terreno` (`Valu1`,
`muaggatt`, `chorizon`) tienen dato en KY? ¿Existen las 23 teselas NASADEM?

Respuesta corta:

- **SSURGO está completo en KY.** Hay 84 áreas de levantamiento, todas publicadas en SDA (versión del 3 y el
  4 de septiembre de 2026), y **ninguna unidad `NOTCOM`**. La suma de `muacres` es igual a `areaacres` en las
  84 áreas, y en `laoverlap`/`muaoverlap` **los 120 condados tienen el 100 % del área con `mukey`**. Ninguno
  queda por debajo del 90 %. Ojo: es una cuenta tabular de SDA, no sale de contar píxeles del raster (ver
  Detalle).
- **Las columnas tienen dato**, con una cobertura parecida a la de KS: agua disponible el 99,4 % del área
  (sin contar agua), drenaje el 99,0 %, grupo hidrológico el 97,9 %, NCCPI el 95,4 % del área de componentes
  mayores (KS: 98,9 %), y arena, limo y arcilla 0–30 cm el 98,2 % de los horizontes.
- **Problema para `suelo_terreno`: en KY las áreas de levantamiento no coinciden con los condados.** Solo 45 de
  las 84 áreas son `KY` + código de un condado. Las otras 39 (`KY601`–`KY645`, `KY646`–`KY648`, `KY709`) juntan
  dos o tres condados o son áreas especiales (Mammoth Cave). `fips_de_area()` de `src/suelo_terreno/process.py`
  las convertiría en FIPS que no existen (`21601`, …, `21709`), así que **75 de los 120 condados quedarían sin
  suelo**. Antes de procesar KY hay que cambiar el reparto por condado (propuesta abajo).
- **NASADEM: las 23 teselas responden HEAD 200** en Planetary Computer: 0,29 GB en total, igual que en
  `cuarta_tanda.md`.

Detalle:

### Cómo lo verifiqué

`docs/research/suelo_ky_sda.py` hace consultas chicas a Soil Data Access (`post.rest`), agregadas en el
servidor, sin bajar tablas, y los HEAD de NASADEM con la misma regla de teselas que
`src/suelo_terreno/download.py`. Para los condados usa `cb_2023_us_county_500k` del Census, bajado en `/tmp`
(fuera del repo). No toca `data/` ni `config/`. Se corrió el 2026-11-15.

### Áreas de levantamiento

| | Cantidad |
|---|---|
| Áreas en `sacatalog` (`KY%`) | 84 |
| Versión publicada (`saverest`) | 83 del 2026-09-03 y 1 del 2026-09-04 (`KY646`, Barren County Area) |
| Unidades `NOTCOM` (`musym = 'NOTCOM'` o `muname` "Not complete…") | 0 |
| Áreas de un solo condado con su código (`KY001` = Adair, …) | 45 |
| Áreas de varios condados (`KY601`–`KY645` salvo `KY630`, más `KY648` y `KY709`) | 36 (33 de 2 condados y 3 de 3: `KY603` Boone/Campbell/Kenton, `KY612` Carroll/Gallatin/Owen, `KY648` Mammoth Cave, que toca Barren, Edmonson y Hart) |
| Áreas de un condado con código propio (`KY646` Barren County Area, `KY647` Hart County Area) | 2 |
| Área especial (`KY630` McCreary-Whitley Area) | 1 (toca McCreary y Whitley) |

Cuatro condados reparten su área entre dos levantamientos (según `laoverlap`): Barren (21009: `KY646`
318.673 ac + `KY648` 1.410 ac), Edmonson (21061: `KY709` 151.780 ac + `KY648` 45.264 ac), Hart (21099: `KY647`
261.645 ac + `KY648` 5.779 ac) y Whitley (21235: `KY627` 145.980 ac + `KY630` 138.903 ac).

### Cobertura por condado

- **Por área de levantamiento:** en las 84 áreas, Σ `muacres` = `areaacres`, sin acres `NOTCOM`. Las unidades
  de agua suman entre 128 y 4.697 ac por área (son `mukey` válidos y `suelo_terreno` las promedia como al
  resto).
- **Por condado** (`laoverlap` con `areatypename = 'County or Parish'` + `muaoverlap`): hay 124 filas para los
  120 condados (los 4 condados partidos de arriba). En todos, Σ `areaovacres` de las unidades = acres del
  condado: **100 % con `mukey`, 0 condados por debajo del 90 %**.
- **Límite:** SDA arma esas superficies con los polígonos de SSURGO, así que dan 100 % casi por construcción.
  No conté píxeles con `mukey` en el raster de gSSURGO o gNATSGO de KY (pesa varios GB y la tarea pedía
  consultas chicas). Como no hay `NOTCOM` ni áreas sin publicar, no espero huecos, pero no lo medí.

### Columnas que usa `suelo_terreno`

Unidades cartográficas de KY sin agua ni `NOTCOM`: 4.830 `mukey`, que suman 25.262.581 ac (≈ 102.235 km²; el
Census da 102.267 km² de tierra).

| Tabla | Columna | `mukey` o filas con dato | % del área |
|---|---|---|---|
| `muaggatt` | `aws0100wta` / `aws0150wta` | 4.631 / 4.830 | 99,4 % |
| `muaggatt` | `drclassdcd` | 4.564 / 4.830 | 99,0 % |
| `muaggatt` | `hydgrpdcd` | 4.517 / 4.830 | 97,9 % |
| `muaggatt` | `wtdepannmin` | 1.647 / 4.830 | 28,4 % (vacío = napa a más de 200 cm, como en los otros estados) |
| `cointerp` (NCCPI general, maíz, soja; componentes mayores) | `interphr` | 5.667 / 6.274 componentes | 95,4 % (KS: 98,9 %) |
| `chorizon` (horizontes de componentes mayores que empiezan a menos de 30 cm) | `sandtotal_r`, `silttotal_r`, `claytotal_r` | 11.084 / 11.287 | — |
| | `om_r`, `ph1to1h2o_r`, `dbthirdbar_r` | 11.270 / 11.287 | — |
| | `kwfact` | 11.066 / 11.287 | — |

- Las tres reglas NCCPI (general, maíz y soja) tienen el mismo número de valores: 11.275 de 22.229 filas
  contando también componentes menores.
- **Componentes mayores sin horizontes:** 596 de 6.274, el 4,6 % del área (KS: 1,0 %). Son agua (551.908 ac),
  afloramiento rocoso (197.094 ac), zona urbana (156.738 ac), Udorthents, escombreras (*dumps*) y canteras
  (*pits*). Eso viene de la minería de carbón del este de KY y de Louisville. No son suelos agrícolas: quedan
  vacíos en la media ponderada, igual que en los otros estados.
- **`Valu1`:** `suelo_terreno` no lo baja. Saca el agua disponible de `muaggatt` y el SOC lo calcula de
  `chorizon` (ver la cabecera de `src/suelo_terreno/process.py`). Por eso no consulté `Valu1` en SDA.

### Qué pasaría hoy con `suelo_terreno` en KY

`fips_de_area()` arma el FIPS como `fips del estado + los 3 dígitos del área`. En KY:

1. 45 condados salen bien (área propia y única).
2. Las 39 áreas restantes darían FIPS inexistentes (`21601`…`21648`, `21709`): `validar_csv()` los rechazaría
   o, si pasan, serían filas falsas.
3. 75 condados quedarían sin fila de suelo, entre ellos condados agrícolas del oeste (Daviess, Hancock, McLean,
   Muhlenberg, Union y Webster, que van en `KY615`, `KY631` y `KY635`) y del Bluegrass.

**Propuesta para `suelo_terreno`** (no la hice, porque es código de otro paquete y KY todavía no está en
`config.yaml`): bajar también `laoverlap` y `muaoverlap` por estado (`SELECT lo.areasymbol, mo.mukey,
mo.areaovacres FROM laoverlap lo JOIN muaoverlap mo ON …  WHERE lo.areatypename = 'County or Parish'`) y
ponderar por `areaovacres` del condado en lugar de `muacres` del área. Así se resuelven KY y también los casos
de `AREAS_ESPECIALES` de MN sin escribirlos a mano. Alternativa mínima: agregar a `AREAS_ESPECIALES` una regla
de KY que reparta cada área entre sus condados, pero perdería la diferencia de suelos entre los condados del
mismo levantamiento.

### NASADEM

Las 23 teselas de 1° que tocan KY (`n36w083`–`n36w090`, `n37w082`–`n37w090`, `n38w083`–`n38w087`, `n39w085`)
responden **HEAD 200** en `nasademeuwest.blob.core.windows.net/nasadem-cog/v001/` y suman 285,7 MB
(0,29 GB). Coincide con `cuarta_tanda.md`.

Fuentes:
- [Soil Data Access (USDA NRCS), servicio `post.rest`, tablas `sacatalog`, `legend`, `mapunit`, `muaggatt`, `component`, `chorizon`, `cointerp`, `laoverlap` y `muaoverlap`](https://sdmdataaccess.sc.egov.usda.gov/), consultado 2026-11-15
- [NASADEM COG en Planetary Computer](https://planetarycomputer.microsoft.com/dataset/nasadem) (HEAD de 23 teselas), consultado 2026-11-15
- [US Census Cartographic Boundary, condados 1:500k 2023](https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip), consultado 2026-11-15

Confianza: **alta** en las áreas publicadas, la ausencia de `NOTCOM`, la relación entre áreas y condados, el
dato por columna y NASADEM (todo consultado y contado). **Media** en "100 % del área con `mukey`": es la
superficie tabular de SDA y no la medí en el raster.

Impacto: si el humano suma KY, primero hay que adaptar `src/suelo_terreno/download.py` y `process.py` para
repartir por `laoverlap`/`muaoverlap` (sería una tarea nueva). `config/config.yaml` no cambia por este research.
Actualiza la fila de SSURGO de KY en `docs/research/cuarta_tanda.md` (punto 5 de "Para decidir"), que ahora
dice "no lo consulté".
