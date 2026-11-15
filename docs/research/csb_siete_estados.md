# Crop Sequence Boundaries (CSB) para los 7 estados

Pregunta: Para `rotacion_secuencia.csv` y el paquete `lotes`: qué ventanas del CSB hay publicadas y si la
última cubre 2025; cómo se baja por estado (archivo nacional o por estado, formato, tamaño para OH, NE, MN y
KS); si los campos (`CSBID`, `CSBACRES`, `CDL<año>`, etc.) son iguales en todas las ventanas; y problemas
conocidos (lotes con riego de pivote en NE y KS, lotes partidos por límites de condado).

Respuesta corta: NASS publica **11 ventanas de 8 años, de 2008–2015 a 2018–2025** (`NationalCSB_<inicio>-<fin>_rev23.zip`).
La última, 2018–2025, **sí cubre 2025** (columna `CDL2025`) y salió el 27 de marzo de 2026. La página también ofrece
una ventana de 16 años 2008–2023, pero su enlace da **404**. **No hay archivos por estado**: cada ventana es un
único zip nacional con una file geodatabase de ESRI (una capa `national<aa><aa>` de multipolígonos, en Albers
NAD83). Pesan de 3,5 a 4,6 GB cada uno, y las 11 suman 44,1 GB. No se encontró el tamaño de cada estado (ver
Detalle 2: se puede leer solo un estado a distancia sin bajar el zip). Los campos **no coinciden del todo con los
metadatos**: la capa 2018–2025 trae además `CSBYEARS` y `ORIG_FID`, que los metadatos no documentan, y `CSBACRES`
es real (float), no entero. Abajo, la comparación de las 11 ventanas. Límites de condado: según el paper de NASS,
las subregiones de proceso se cortan por la red de rutas y vías justamente para **no partir lotes en los límites
de estado o condado**. Por eso un polígono puede cruzar el límite y tener un solo `CNTYFIPS`; el método exacto
para asignar el condado no está documentado. Pivotes: **ninguna fuente oficial que abrí habla de riego ni de
pivotes**. Lo que sigue sobre ellos sale del método, no de una prueba.

Detalle:

**1. Ventanas publicadas.** La página del CSB (modificada el 26/03/2026) enumera, con enlace de descarga:
2008–2015, 2009–2016, 2010–2017, 2011–2018, 2012–2019, 2013–2020, 2014–2021, 2015–2022, 2016–2023, 2017–2024
y 2018–2025. Dice además "The 2018-2025 released March 27, 2026". Los metadatos FGDC ("2025 Crop Sequence
Boundaries", rev23) repiten la misma lista de 11 períodos. La página tiene además un bloque "Sixteen-year time
frame covering 2008-2023 (a single 16-year window)" con enlace a `NationalCSB_2008-2023_rev23.zip`, que dio
**HTTP 404** el 2026-11-15. Los metadatos no lo nombran. Una ventana de 8 años con 2026 recién podría salir
después del CDL 2026 (el patrón es: CDL de un año → CSB que termina en ese año, en marzo del año siguiente; es
una inferencia de una sola fecha publicada).

Tamaño de cada zip (cabecera `Content-Length` del servidor de NASS, 2026-11-15). Todos tienen
`Last-Modified` del 05/10/2026: los archivos se volvieron a subir en octubre de 2026, siempre como `rev23`:

| Ventana | Bytes | GB (10⁹) |
|---|---|---|
| 2008–2015 | 4.320.760.313 | 4,32 |
| 2009–2016 | 4.594.365.035 | 4,59 |
| 2010–2017 | 4.478.476.364 | 4,48 |
| 2011–2018 | 4.292.777.817 | 4,29 |
| 2012–2019 | 3.831.809.504 | 3,83 |
| 2013–2020 | 4.149.313.479 | 4,15 |
| 2014–2021 | 3.676.937.745 | 3,68 |
| 2015–2022 | 3.890.557.522 | 3,89 |
| 2016–2023 | 3.505.346.935 | 3,51 |
| 2017–2024 | 3.568.216.747 | 3,57 |
| 2018–2025 | 3.758.023.527 | 3,76 |
| **Total** | 44.066.584.988 | **44,1** |
| 2008–2023 (16 años) | — | 404 |

**2. Cómo se baja por estado.** No hay archivos por estado ni servicio de consulta por estado:
- La página solo tiene los zip nacionales. Dentro de cada zip hay una file geodatabase de ESRI. La ruta interna
  cambia entre ventanas: en 2018–2025 la `.gdb` está en la raíz (`CSB1825.gdb`), y en 2008–2015 está dentro de
  una carpeta (`NationalCSB_2008-2015_rev23/CSB0815.gdb`). Así lo leyó del directorio central de cada zip el script
  `docs/research/csb_siete_estados_campos.py`. Un script que abra todas las ventanas no puede dar la ruta por
  supuesta.
- El "Interactive Map" (CSB Viewer 2.5) es una app de Google Earth Engine (`nass-csb.projects.earthengine.app`)
  que muestra solo 2018–2025. No tiene descarga.
- El registro de Zenodo `14004209` ("Crop Sequence Boundaries GitHub Repository", v2024) es el **código** del
  algoritmo, no los datos. El repositorio de GitHub (`USDA-REE-NASS/crop-sequence-boundaries`) arma ventanas
  propias a partir del CDL, pero requiere ArcGIS Pro ("ArcGIS pro 3.1 tested").
- GeoParquet de Source Cooperative (`fiboa/us-usda-cropland`): según `docs/datasets/lotes.md`, es la ventana
  2016–2023, con los polígonos fusionados por el cultivo de 2023 y sin las columnas `CDL<año>`. No sirve para
  secuencias. No lo volví a abrir en esta corrida.
- **Leer un estado sin bajar el zip.** GDAL (con pyogrio) abre la geodatabase a distancia con
  `/vsizip//vsicurl/<url>/<ruta>.gdb` y lee por rangos HTTP solo lo que pide. Para la ventana 2018–2025, listar la
  capa tardó 13 s y leer la cabecera (campos, CRS, número de polígonos) 63 s. Una lectura con `bbox` de un
  recorte de 5 × 5 km **no terminó en 150 s** (sección 6). Si funcionara, permitiría bajar solo
  los polígonos de OH, NE, MN y KS (filtrando por `bbox` y después por `STATEFIPS`), sin pasar el zip entero de
  3,8 GB por el disco. No está medido cuánto tráfico genera un estado entero.
- **Tamaño por estado: no encontrado.** Ninguna fuente publica polígonos ni MB por estado. La ventana 2018–2025
  tiene **15.973.095 polígonos** en todo el país (cabecera de la capa). El tamaño de OH, NE, MN y KS solo se puede
  medir después de bajar un zip (que el paquete `lotes` ya baja a
  `data/interim/lotes/csb/` en la máquina que lo corrió).

**3. Campos de cada ventana.** Los metadatos FGDC (escritos para 2018–2025) documentan `OBJECTID`, `SHAPE`,
`CSBID` (texto: 2 dígitos del FIPS del estado + 2 del año inicial + 2 del año final + 9 secuenciales),
`CSBACRES` ("Integer"), `CDL2018`…`CDL2025` (entero, "Majority crop type within the CSB polygon"),
`STATEFIPS`, `STATEASD`, `ASD`, `CNTY`, `CNTYFIPS`, `INSIDE_X`, `INSIDE_Y`, `Shape_Length` y `Shape_Area`.
Lo que trae la capa real, leído a distancia con `docs/research/csb_siete_estados_campos.py`:

CAMPOS_TABLA

Diferencias con los metadatos, en la capa 2018–2025 leída a distancia:
- `CSBYEARS` (texto) y `ORIG_FID` (entero) existen pero **no están en los metadatos**. Por el nombre, `CSBYEARS`
  sería la ventana y `ORIG_FID` el FID de la capa de origen antes de la unión nacional. Es una suposición: no
  encontré documentación de ninguno de los dos.
- `CSBACRES` es `float64`, no entero como dicen los metadatos. Para pesar por área conviene usar `Shape_Area`
  (m², EPSG del Albers de NLCD) o el área recalculada en EPSG:5070, y guardar `CSBACRES` solo como dato original.
- La capa se llama `national<aa><aa>` (por ejemplo `national1825`) y es `MultiPolygon`.
- El CRS es Albers cónica equivalente sobre NAD83 (centro 23° N, −96°; paralelos 29,5° y 45,5°), equivalente a
  EPSG:5070 aunque el WKT no trae el código.

**4. Lotes partidos por límites de condado.** El paper de NASS (Hunt et al. 2024, *Statistical Journal of the
IAOS*) dice que cada CDL se divide en subregiones (86 en todo el país) "defined using the transportation network
features. This avoids the problem of splitting CSBs along administrative boundaries (e.g., states and/or counties
lines)". Al final, el paso "Repopulating" llena la tabla con la mayoría zonal del CDL "as well as county and state
locations". Consecuencias:
- Los polígonos **no se cortan** en el límite de condado ni de estado. Un lote que cruza el límite queda entero,
  con **un solo** `STATEFIPS`/`CNTYFIPS`. Cómo se elige ese condado (centroide, punto interior `INSIDE_X/Y` o
  mayor superficie) **no está documentado** en las fuentes que abrí.
- En la práctica, los límites de condado del Corn Belt suelen ir por caminos, y los caminos cortan los
  polígonos, así que los lotes partidos deberían ser pocos. Es una inferencia: no está medido.
- Para `rotacion_secuencia.csv` hay dos caminos posibles. (a) Asignar cada polígono a su `CNTYFIPS`, simple y
  coherente con NASS. (b) Intersecar con `condados.gpkg` y pesar por el área dentro de cada condado, que es
  exacto para el área. Si se usa (a), conviene medir y anotar en el data card cuántos polígonos cortan un límite.
- `CSBID` empieza con el FIPS del estado, así que un lote del límite NE–KS queda contado en un solo estado.
  Cuando cada máquina procese solo sus estados, ese lote no se repite ni se pierde, siempre que el filtro sea
  por `STATEFIPS` y no por intersección con el estado.

**5. Riego por pivote (NE y KS).** Ni la página del CSB, ni los metadatos, ni el paper, ni el repositorio y el
registro de Zenodo mencionan riego, pivotes ni lotes circulares. **No hay información oficial.** Del método
descrito sí se deduce lo siguiente (no verificado con datos):
- El CSB solo tiene el cultivo mayoritario por año. **No dice si el lote se riega.** Las columnas `CDL<año>` no
  separan riego de secano.
- Las esquinas de un pivote (fuera del círculo) suelen tener otro uso: pastizal, barbecho o un cultivo distinto.
  Como el método combina las 8 secuencias del CDL, en un pivote el círculo y las esquinas deberían salir como
  polígonos distintos cuando sus secuencias difieren. Cuando las esquinas tienen la misma secuencia, quedan en
  el mismo polígono. Además, la simplificación Wang-Müller con tolerancia de 60 m y la forma de grilla que deja
  pasar de raster a polígono (que el paper reconoce como limitación) deforman el círculo.
- Los polígonos de menos de 1 ha con dos o más años de cultivo se disuelven en el vecino más grande, así que las
  esquinas chicas se pegan al círculo o al lote vecino.
- Para el paquete `lotes` (que pide "nada de riego") y para comparar con Iowa (tarea T004), el riego tiene que
  salir de otra fuente: Censo 2022, `pct_riego` (ya usado en `lotes`), o una máscara de riego (ver
  `docs/research/riego_mascaras.md`). En NE y KS, un criterio de forma (compacidad alta de un círculo de
  aproximadamente 50–65 ha) no prueba riego y no debería usarse solo.

**6. Prueba de lectura por recorte.** Se pidió a GDAL, a distancia, un recorte de 5 × 5 km en el sudoeste de
Kansas (Albers x = −480.000 m, y = 1.680.000 m, con `bbox`) de la capa 2018–2025. **No terminó en 150 s** y se
cortó. Lo más probable es que los archivos de la `.gdb` estén comprimidos con deflate dentro del zip: para
llegar a un trozo intermedio, `/vsizip/` tiene que descomprimir desde el principio de ese archivo, y el índice
espacial no ayuda. No está verificado (no medí el método de compresión de cada entrada). Conclusión práctica:
leer a distancia sirve para la cabecera (campos, CRS, número de polígonos), pero **no para recortar estados**.
Para extraer OH, NE, MN y KS hay que bajar el zip de cada ventana, como ya hace `src/lotes/download.py`.

**7. Otras limitaciones documentadas (paper de NASS).**
- El CSB hereda los errores del CDL. Quedan "false islands and bands in otherwise continuous fields". Las
  fracciones de avena, alfalfa y heno heredan la baja precisión del CDL (`docs/research/cdl_csb.md`).
- La superficie de maíz y soja del CSB **sobreestima** a Quick Stats, porque la eliminación de polígonos
  expande los lotes sobre píxeles mezclados. Con los años el error crece para el maíz. Para superficies,
  conviene NASS (`produccion_anual.csv`) y no la suma de `CSBACRES`.
- Los polígonos no son parcelas ni unidades de manejo: "these are polygons of continuous cropping sequences as
  seen in the CDL, not field boundaries". Dos lotes vecinos con la misma secuencia de 8 años quedan unidos en
  uno (inferencia del método de combinación de secuencias).
- Desde 2024 el CDL es de 10 m. Los metadatos dicen que el proceso remuestrea a 10 m todas las capas antes de
  apilarlas, así que las ventanas que incluyen 2024 y 2025 mezclan años de 30 m y de 10 m remuestreados.

Fuentes: [Crop Sequence Boundaries (USDA NASS)](https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php), consultado 2026-11-15;
[Metadata – 2025 Crop Sequence Boundaries (USDA NASS)](https://www.nass.usda.gov/research-and-science/crop-sequence-boundaries/metadata-crop-sequence-boundaries-2025), consultado 2026-11-15;
[Zips nacionales `NationalCSB_<ventana>_rev23.zip` (cabeceras HTTP y directorio central)](https://www.nass.usda.gov/sites/default/files/Research_and_Science/Crop-Sequence-Boundaries/datasets/NationalCSB_2018-2025_rev23.zip), consultado 2026-11-15;
[Hunt et al. 2024, Crop sequence boundaries using USDA NASS historic cropland data layers, Statistical Journal of the IAOS 40: 237–246, doi 10.3233/SJI-230078 (PDF en NASS)](https://www.nass.usda.gov/sites/default/files/Education_and_Outreach/Reports,_Presentations_and_Conferences/Journal_Articles/Crop%20sequence%20boundaries%20using%20USDA%20National%20Agriculural%20Statistics%20Service%20historic%20cropland%20data%20layers.pdf), consultado 2026-11-15;
[crop-sequence-boundaries (GitHub, USDA-REE-NASS)](https://github.com/USDA-REE-NASS/crop-sequence-boundaries), consultado 2026-11-15;
[Crop Sequence Boundaries GitHub Repository, v2024 (Zenodo 14004209)](https://zenodo.org/records/14004209), consultado 2026-11-15;
[CSB Viewer (USDA NASS)](https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/Viewer/index.php), consultado 2026-11-15.
No se pudo abrir: el PDF de ICAS-2023 sobre el CSB (404 en la URL de los metadatos).

Confianza: alta para las ventanas, los tamaños, la falta de archivos por estado y los campos leídos de las capas
(salen directo del servidor de NASS). Alta para el método de subregiones por rutas (paper oficial). Baja para
todo lo de pivotes (no hay fuente; es inferencia del método) y para cómo se asigna `CNTYFIPS` (no documentado).

Impacto: paquete `cultivos`, `rotacion_secuencia.csv`. Hoy se calcula por píxel del CDL (`docs/datasets/cultivos.md`).
Si se pasa al CSB, son 11 zips nacionales, 44 GB en total (más de 5 GB: decide el humano). La lectura a
distancia por `bbox` no resultó práctica (sección 6). Cada zip se puede bajar, extraer los estados y borrar, de
a uno por vez, para no tener más de unos 4,6 GB en disco al mismo tiempo. Habría que pesar por área recalculada y no por `CSBACRES`, resolver la ruta
de la `.gdb` dentro de cada zip y leer las columnas `CDL<año>` según la ventana. Paquete `lotes`
(`src/lotes/download.py`): la ventana 2018–2025 ya cubre 2025; `CSBYEARS` y `ORIG_FID` se pueden guardar en raw
tal cual. El riego tiene que salir del censo o de una máscara, no del CSB. Data cards `docs/datasets/cultivos.md`
y `docs/datasets/lotes.md`, sección "Problemas conocidos": lotes que cruzan límites de condado, sobreestimación
de superficie y campos no documentados.

Citas:
> "The 2018-2025 released March 27, 2026." — [Crop Sequence Boundaries (USDA NASS)](https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php)
> "Sixteen-year time frame covering 2008-2023 (a single 16-year window)" — [Crop Sequence Boundaries (USDA NASS)](https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php)
> "This avoids the problem of splitting CSBs along administrative boundaries (e.g., states and/or counties lines)" — [Hunt et al. 2024](https://www.nass.usda.gov/sites/default/files/Education_and_Outreach/Reports,_Presentations_and_Conferences/Journal_Articles/Crop%20sequence%20boundaries%20using%20USDA%20National%20Agriculural%20Statistics%20Service%20historic%20cropland%20data%20layers.pdf)
> "Repopulating the attribute table uses zonal majority of CDL classes as well as county and state locations." — [Hunt et al. 2024](https://www.nass.usda.gov/sites/default/files/Education_and_Outreach/Reports,_Presentations_and_Conferences/Journal_Articles/Crop%20sequence%20boundaries%20using%20USDA%20National%20Agriculural%20Statistics%20Service%20historic%20cropland%20data%20layers.pdf)
> "Nationally the CSB values for corn and soybean acreage are consistently greater the official estimates from Quick Stats" — [Hunt et al. 2024](https://www.nass.usda.gov/sites/default/files/Education_and_Outreach/Reports,_Presentations_and_Conferences/Journal_Articles/Crop%20sequence%20boundaries%20using%20USDA%20National%20Agriculural%20Statistics%20Service%20historic%20cropland%20data%20layers.pdf)
> "Small polygons under 1 hectare with two or more years of crops within the 8-year windows are eliminated into the next largest neighboring polygon" — [Metadata – 2025 CSB](https://www.nass.usda.gov/research-and-science/crop-sequence-boundaries/metadata-crop-sequence-boundaries-2025)
> "simplified to retain critical bends (Wang-Müller algorithm) at a 60 meter tolerance" — [Metadata – 2025 CSB](https://www.nass.usda.gov/research-and-science/crop-sequence-boundaries/metadata-crop-sequence-boundaries-2025)
