# Humedad del suelo: SMAP L4 (Crop-CASMA) contra NLDAS-2 Noah en OH, NE y MN, 2015–2025

Pregunta: con el release `datos-oh-ne-mn`, ¿cuánto se parecen por condado y mes `sm_rootzone_m3m3` (SMAP L4,
`agua_mensual.csv`) y `sm_0_100cm_m3m3` (NLDAS-2 Noah, `nldas_mensual.csv`), y sus anomalías
(`sm_rootzone_anom_z`, `sm_0_100cm_anom_z`)? ¿Dónde difieren más? ¿Qué conviene darle a ML antes y después de
2015, y son redundantes?

Respuesta corta:
- **En el tiempo se parecen mucho; en el espacio, no.** Mediana sobre los 268 condados: correlación de los
  niveles mensuales r = 0,87, de las anomalías z r = 0,80, y de la anomalía media de abril–septiembre por
  condado-año r = 0,89. El sesgo medio (SMAP − NLDAS) es chico en la mediana (+0,009 m³/m³), pero va de −0,12 a
  +0,10 según el condado. SMAP separa los condados entre sí 2 a 3 veces más que NLDAS: el desvío entre medias
  de condado es 0,035 contra 0,014 en OH y 0,056 contra 0,022 en MN.
- **Donde más difieren:**
  1. El **centro-norte de MN, con suelos arenosos y turba**. Ahí SMAP es 0,05–0,12 más seco y las anomalías
     se parecen poco (r 0,04–0,50). Los casos son Anoka, Wadena, Pine, Crow Wing, Morrison, Carlton, Otter
     Tail, y los condados con turba Koochiching, Beltrami, Aitkin, Lake of the Woods y St. Louis. En los 13
     condados con turba de `smap_costas.md` la mediana de r de anomalía z es 0,61, contra 0,81 en el resto.
  2. El **noroeste de OH (llanura del lago Erie / Great Black Swamp)**. Ahí SMAP es 0,07–0,10 más húmedo
     (Ottawa, Paulding, Putnam, Defiance, Sandusky, Van Wert), pero las anomalías coinciden bien (r 0,7–0,86).
     Es un sesgo de nivel, no de dinámica.
  3. **OH en invierno y primavera** (enero–abril): la mediana de r de anomalía z baja a 0,56–0,64. En el
     resto del año está entre 0,8 y 0,9.
- **Las dos anomalías z del release no son intercambiables:** SMAP usa como base 2015–2025 y NLDAS usa
  1991–2020. En 2015–2025 la z de NLDAS tiene media −0,15 (MN) y −0,45 (NE y OH): ese período es más seco que
  la normal de 1991–2020 del modelo. Con NLDAS recalculada sobre la misma base 2015–2025, la r de anomalías
  sube de 0,80 a 0,83.
- **Recomendación para ML (solo descriptiva):**
  - **NLDAS como variable principal de humedad en todo el período (2000–2025).** Es la única que cubre
    antes de 2015, es una sola serie homogénea y su z tiene base climatológica de 30 años.
  - **SMAP opcional y solo desde 2015**, como complemento por su contraste espacial entre condados. No hay
    que empalmar SMAP después de 2015 con NLDAS antes: el sesgo por condado llega a ±0,1 m³/m³ y el desvío
    también cambia, así que el empalme metería un salto artificial en 2015.
  - **Como anomalía temporal son casi redundantes** (r ≈ 0,8–0,9). **Como nivel absoluto no lo son**, porque
    difieren en el patrón espacial (r espacial 0,22 en OH y 0,61 en MN).

Detalle:

## 1. Datos y método

- `datos-oh-ne-mn_agua.zip` y `datos-oh-ne-mn_nldas.zip` del release `datos-oh-ne-mn`, bajados con `curl -L`.
  El sha256 coincide con los `.sha256` del release (tienen fin de línea CRLF: hay que sacar el `\r` antes de
  `sha256sum -c`). Se descomprimieron en `data/interim/t092/`, fuera de git.
- Se comparan los meses con dato en las dos tablas: 34.304 pares condado-mes, 268 condados (MN 87, NE 93,
  OH 88), de 2015-04 a 2025-12.
  **2016-12 está vacío en SMAP para todos los condados.** `process.py` deja el mes vacío si falta un día y,
  según parece, falta al menos un día de diciembre de 2016 en Crop-CASMA. No lo verifiqué en `raw/`.
- Ninguna de las dos usa la máscara agrícola: las dos son medias del condado ponderadas por área (celdas de
  9 km en SMAP y de 0,125° en NLDAS). En profundidad son comparables: la "rootzone" de SMAP L4 llega a ~1 m y
  NLDAS va de 0 a 100 cm.
- Por condado se calcula sesgo (media de SMAP − NLDAS), RMSE, desvíos, r de niveles, r de anomalías en
  m³/m³ (restando la media del mes calendario con base común 2015–2025), r de las z del release y r de la z de
  SMAP contra una z de NLDAS recalculada con base 2015–2025. Las r usan al menos 24 meses. Por mes
  calendario, al menos 8 años.
- Script: `docs/research/smap_vs_nldas.py` (`python -X utf8 docs/research/smap_vs_nldas.py data/interim/t092`).
  Deja la tabla por condado en `data/interim/t092/smap_vs_nldas_condados.csv`.

## 2. Resumen por estado (mediana sobre condados)

| Estado | SMAP media | NLDAS media | sesgo | RMSE | sd SMAP | sd NLDAS | r nivel | r anom m³/m³ | r anom z (release) | r anom z (base común) |
|---|---|---|---|---|---|---|---|---|---|---|
| MN | 0,256 | 0,255 | −0,002 | 0,040 | 0,029 | 0,030 | 0,82 | 0,82 | 0,80 | 0,83 |
| NE | 0,211 | 0,210 | −0,001 | 0,043 | 0,025 | 0,050 | 0,87 | 0,87 | 0,88 | 0,90 |
| OH | 0,308 | 0,276 | +0,034 | 0,045 | 0,049 | 0,034 | 0,90 | 0,73 | 0,72 | 0,76 |
| Todos | 0,279 | 0,259 | +0,009 | 0,043 | 0,038 | 0,040 | 0,87 | 0,81 | 0,80 | 0,83 |

Entre los condados, el percentil 10–90 del sesgo va de −0,064 a +0,063. El de r de anomalía z va de 0,63 a
0,90. Hay 12 condados con r de anomalía z < 0,5, todos en MN.

- En **NE**, NLDAS varía el doble que SMAP en el tiempo (sd 0,050 contra 0,025). Aun así es el estado donde
  más coinciden, con r de anomalía 0,88 y r espacial 0,95. El gradiente oeste-este (Sandhills secos y este
  húmedo) aparece en los dos.
- En **OH** la r de niveles es alta (0,90) porque las dos tienen el mismo ciclo estacional. Sin el ciclo, la
  r de anomalías baja a 0,73. SMAP es más húmedo en 77 de los 88 condados.

## 3. Patrón espacial de las medias de condado

| Estado | sd entre condados SMAP | sd entre condados NLDAS | rango SMAP | rango NLDAS | r espacial |
|---|---|---|---|---|---|
| MN | 0,056 | 0,022 | 0,106–0,328 | 0,196–0,302 | 0,61 |
| NE | 0,081 | 0,045 | 0,065–0,330 | 0,131–0,277 | 0,95 |
| OH | 0,035 | 0,014 | 0,212–0,402 | 0,226–0,317 | 0,22 |

- **NO de OH:** SMAP marca los condados de la antigua llanura lacustre del Erie como los más húmedos del
  estado: Ottawa 0,40, Paulding 0,39, Putnam 0,38, Defiance 0,38, Van Wert 0,37 y Sandusky 0,36. NLDAS les da
  0,27–0,32, casi lo mismo que al resto del estado. Los más secos de SMAP en OH son Lake (0,21) y los
  condados de las colinas del sureste (Hocking, Jackson, Vinton, Athens; 0,24–0,26), donde NLDAS da
  0,27–0,29.
- **Centro-norte de MN:** SMAP da 0,11–0,17 en Anoka, Wadena, Morrison, Crow Wing y Pine, y NLDAS da
  0,20–0,26. Esos condados están en planicies arenosas de origen glacial (Anoka Sand Plain y llanuras de
  outwash del centro de MN). **Hipótesis, sin verificar:** los dos productos usan mapas de textura del suelo
  distintos, y el de SMAP L4 resuelve mejor las arenas. No leí la documentación de los parámetros de suelo de
  ninguno de los dos.

## 4. Condados con turba (lista de `smap_costas.md`)

| Condado | SMAP | NLDAS | sesgo | r nivel | r anom z |
|---|---|---|---|---|---|
| Aitkin (27001) | 0,206 | 0,270 | −0,064 | 0,60 | 0,46 |
| Beltrami (27007) | 0,178 | 0,240 | −0,062 | 0,45 | 0,43 |
| Hennepin (27053) | 0,224 | 0,255 | −0,031 | 0,61 | 0,55 |
| Itasca (27061) | 0,214 | 0,253 | −0,039 | 0,78 | 0,61 |
| Koochiching (27071) | 0,256 | 0,300 | −0,044 | 0,49 | 0,39 |
| Lake of the Woods (27077) | 0,231 | 0,254 | −0,023 | 0,33 | 0,37 |
| Le Sueur (27079) | 0,304 | 0,259 | +0,045 | 0,88 | 0,86 |
| St. Louis (27137) | 0,201 | 0,268 | −0,067 | 0,71 | 0,58 |
| Waseca (27161) | 0,301 | 0,276 | +0,025 | 0,83 | 0,82 |
| Allen, OH (39003) | 0,347 | 0,271 | +0,075 | 0,85 | 0,69 |
| Auglaize, OH (39011) | 0,350 | 0,266 | +0,084 | 0,88 | 0,71 |
| Darke, OH (39037) | 0,296 | 0,268 | +0,028 | 0,90 | 0,72 |
| Shelby, OH (39149) | 0,334 | 0,270 | +0,064 | 0,92 | 0,76 |

Mediana de los 13 condados con turba contra los otros 255: sesgo −0,023 contra +0,009, r de nivel 0,78
contra 0,88, r de anomalía z 0,61 contra 0,81.

En las turberas del norte de MN, SMAP es más seco que NLDAS **aunque la turba es lo más húmedo del
paisaje**. Esto es consistente con lo que midió `smap_costas.md`: `process.py` descarta las celdas
> 0,60 m³/m³ (en Koochiching, el 65 % del área), así que la media de SMAP queda solo con las celdas
minerales y más secas. NLDAS no tiene ese filtro. Cuando la mayor parte del condado está excluida, la
dinámica de las celdas que quedan también se parece menos a la del modelo. En los condados con turba
agrícolas del sur de MN (Le Sueur y Waseca) y del oeste de OH se excluye una parte menor del área, y ahí las
dos series coinciden bien.

## 5. Por mes calendario (mediana sobre condados de la r de anomalía z, 2015–2025)

| Mes | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MN | 0,78 | 0,79 | 0,76 | 0,80 | 0,86 | 0,86 | 0,89 | 0,89 | 0,87 | 0,88 | 0,76 | 0,80 |
| NE | 0,94 | 0,93 | 0,92 | 0,91 | 0,88 | 0,88 | 0,86 | 0,88 | 0,91 | 0,93 | 0,90 | 0,93 |
| OH | 0,56 | 0,64 | 0,56 | 0,59 | 0,79 | 0,89 | 0,90 | 0,87 | 0,92 | 0,84 | 0,89 | 0,81 |

En los meses críticos (julio y agosto) coinciden bien en los tres estados (0,86–0,90). El sesgo de OH es
máximo de enero a mayo (+0,04 a +0,07) y mínimo en verano (+0,01 a +0,03). En los meses en que OH tiene el
suelo cerca de saturación, los dos productos difieren más: el exceso de agua de primavera que retrasa la
siembra es justo lo que menos coincide. Con 11 años por mes calendario, cada r tiene bastante incertidumbre.

## 6. Antes de 2015 y la base de las anomalías

- Antes de 2015 solo hay NLDAS en el release (2000–2025). SMAP L4 empieza el 2015-03-31.
- Media regional anual de NLDAS (m³/m³): el año más seco del período es 2012 (MN 0,211, NE 0,168,
  OH 0,268). Ese año no está en SMAP. 2022 y 2023 en NE (0,167 y 0,174) están al nivel de 2012.
- En 2015–2025 la z de NLDAS con base 1991–2020 tiene media −0,15 (MN), −0,45 (NE) y −0,44 (OH). La z de SMAP,
  con base 2015–2025, tiene media 0 por construcción. **El mismo valor de z significa cosas distintas en una
  y otra**: un SMAP z = 0 en NE equivale más o menos a un NLDAS z de −0,45. Entre las dos z de NLDAS (base
  1991–2020 y base 2015–2025) la r es 0,96, así que la base cambia sobre todo la media, no el orden.

## 7. Qué conviene para ML (descriptivo, sin entrenar)

1. **2000–2025: `sm_0_100cm_m3m3` y `sm_0_100cm_anom_z` de NLDAS como entrada de humedad del suelo.** Es una
   sola fuente para todo el período, la base es climatológica y en los condados del Corn Belt agrícola su
   dinámica coincide con SMAP (r ≈ 0,85–0,9).
2. **2015–2025: SMAP como entrada adicional, no como reemplazo.** Lo que agrega es contraste espacial entre
   condados: la llanura del Erie, las arenas de MN, los Sandhills. Si el modelo entrena con años anteriores a
   2015, SMAP queda vacío en ese período. No hay que rellenarlo con NLDAS ni empalmar las dos series.
3. **No usar las dos z como si fueran la misma variable**, porque tienen bases distintas (sección 6). Si se
   quiere una z comparable de SMAP, solo puede tener base 2015–2025: SMAP no tiene 30 años.
4. **Cuidado con SMAP en las turberas del norte de MN** (Koochiching, Beltrami, Aitkin, Lake of the Woods,
   St. Louis, Itasca) y en Anoka (r de nivel 0,08). Ahí la media de condado de SMAP está sesgada por el filtro
   de 0,6 y la correlación con NLDAS es baja. Son pocos condados agrícolas, pero conviene marcarlos.
5. **Redundancia:** como anomalía temporal son casi redundantes. Si ML usa las dos para 2015–2025, la
   información nueva de SMAP está en el nivel medio de cada condado, no en la variación de un año a otro.

## Supuestos

- La lista de condados con turba sale de `smap_costas.md`: son los que tienen celdas > 0,6 en días de muestra.
  No es un mapa de turba.
- La interpretación de los sesgos (textura del suelo, filtro de 0,6) es una hipótesis compatible con los datos.
  No la verifiqué con la documentación de los parámetros de suelo de SMAP L4 ni de Noah.
- Las dos son medias ponderadas por el área de todo el condado, sin máscara agrícola. En condados forestales
  del norte de MN, ninguna de las dos representa el suelo agrícola.

Fuentes:
- Release `datos-oh-ne-mn` del repo (`agua_mensual.csv`, `nldas_mensual.csv` y sus data cards `agua.md` y
  `nldas.md` dentro de los zips), consultado 2026-11-15.
- `docs/research/smap_costas.md` (celdas > 0,6 y área excluida por condado), consultado 2026-11-15.

Confianza: alta para los números (calculados con el script sobre el release). Media para la interpretación de
por qué difieren (textura y filtro de 0,6). Baja para las r por mes calendario (11 años).

Impacto: ninguno sobre `config/` ni sobre el esquema. Afecta cómo arma `merge.py`/ML las entradas de humedad:
NLDAS para todo el período, SMAP solo como extra desde 2015 y sin mezclar las z. Propuesta para `agua`: anotar
en el data card que diciembre de 2016 está vacío en todos los condados de la tanda OH-NE-MN y que la z de SMAP
tiene una base distinta de la de NLDAS.
