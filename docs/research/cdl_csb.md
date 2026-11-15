# CDL y CSB: clases, descarga por estado, precisión y campos del CSB

Pregunta: CDL y CSB: tabla oficial de clases, forma más rápida de bajar por estado (servicio de CropScape), precisión por estado y estructura de los campos del CSB.

Respuesta corta: La tabla oficial de clases del Cropland Data Layer (CDL) es la página "CDL legend colors" de NASS (código, nombre y color RGB) y se repite en los metadatos de cada estado. Los códigos del CLAUDE.md coinciden con la tabla oficial: maíz 1, soja 5, trigo de invierno 24, doble cultivo trigo de invierno/soja 26, avena 28, alfalfa 36, otro heno/no alfalfa 37, barbecho/cultivo ocioso 61 y pastizal 176 (en la leyenda "grass/pasture", en los metadatos "grassland/pasture"); 0 es "background" (sin dato). CropScape (`nassgeodata.gmu.edu`) fue reemplazado por **CroplandCROS** (`croplandcros.scinet.usda.gov`); la forma más rápida de bajar solo IA, IL e IN, sin login, es el ImageServer público que usa CroplandCROS (`https://pdi.scinet.usda.gov/image/rest/services/CDL_WM/ImageServer`, `exportImage` por tesela en EPSG:5070), en lugar de los zip nacionales (1,6 a 2,0 GB por año a 30 m; 9,0 y 9,8 GB los de 10 m de 2024 y 2025). Desde 2024 el CDL se produce a 10 m, con una versión remuestreada a 30 m para mantener la serie. Precisión del CDL 2023 (la última con metadatos por estado publicados): precisión global de cultivos 90,5 % en Iowa, 90,2 % en Illinois y 89,6 % en Indiana; maíz y soja con precisión del productor de 92 a 94 % y del usuario de 96 a 97,5 %; avena, alfalfa y otro heno, mucho peor (6 a 55 % del productor). El CSB es una geodatabase nacional (Albers, la misma de NLCD) por ventana de 8 años, con los campos `CSBID`, `CSBACRES`, `CDL<año>` (8 columnas, cultivo mayoritario del polígono cada año), `STATEFIPS`, `STATEASD`, `ASD`, `CNTY`, `CNTYFIPS`, `INSIDE_X`, `INSIDE_Y`, `Shape_Length` y `Shape_Area`.

Detalle:

**1. Tabla oficial de clases.** NASS publica la leyenda en `https://www.nass.usda.gov/research-and-science/cropland/docs/cdl-legend-colors` (código, nombre, R G B y hex) y la misma lista de categorías en la sección "attribute" de los metadatos FGDC de cada estado y año (por ejemplo, `metadata-ia23`). Las clases que usa el paquete `cultivos`:

| Código | Nombre oficial | Grupo para Field Shift |
|---|---|---|
| 0 | background | sin dato (vacío) |
| 1 | corn | maíz |
| 5 | soybeans | soja |
| 24 | winter wheat | trigo de invierno |
| 26 | dbl crop winwht/soybeans | doble cultivo trigo/soja |
| 27 | rye | centeno |
| 28 | oats | avena |
| 36 | alfalfa | alfalfa |
| 37 | other hay/non alfalfa | heno |
| 58 | clover/wildflowers | trébol (cobertura/forraje) |
| 61 | fallow/idle cropland | barbecho |
| 176 | grassland/pasture (leyenda: grass/pasture) | pastizal |

Otros dobles cultivos que aparecen en la tabla de precisión del Corn Belt: 225 dbl crop winwht/corn, 226 dbl crop oats/corn, 228 dbl crop triticale/corn, 236 dbl crop winwht/sorghum, 240 dbl crop soybeans/oats. Según los metadatos, la precisión global solo cubre los cultivos de la FSA (códigos 1–61, 66–80, 92 y 200–255); los pastizales muestreados por la FSA y las categorías no agrícolas o del NLCD (códigos 62–65, 81–91 y 93–199: bosque, arbustal, agua, urbano, humedales) quedan afuera, y su precisión depende enteramente del NLCD.

**2. Descarga por estado.** La página de anuncios del CDL ya se titula "CroplandCROS and Cropland Data Layer": CroplandCROS (`https://croplandcros.scinet.usda.gov/`) reemplazó a CropScape. `nassgeodata.gmu.edu` no respondió en esta corrida (timeout en el servicio y en la página de ejemplos de la API `GetCDLFile`), así que el servicio `GetCDLFile?year=&fips=` de CropScape no se pudo verificar. Opciones, de más rápida a más lenta para tres estados:
- **ImageServer de CroplandCROS** (sin login, verificado en esta corrida con `?f=json`): `https://pdi.scinet.usda.gov/image/rest/services/CDL_WM/ImageServer`, `maxImageWidth` 4097. El paquete `cultivos` ya lo usa con `exportImage` por tesela de 90 km en EPSG:5070 (`imageSR=5070`, `format=tiff`, `pixelType=U8`, `interpolation=RSP_NearestNeighbor`, `mosaicRule` con `lockRasterIds` = OBJECTID del año). Detalle en `loop/notes/cultivos.md`.
- **Microsoft Planetary Computer**, colección STAC `usda-cdl` (COG, sin login, token anónimo): solo hasta 2021.
- **Descarga nacional** (`https://www.nass.usda.gov/research-and-science/cropland/release`): un zip por año, 1,6–2,0 GB a 30 m; 2024 y 2025 también a 10 m (9,0 y 9,8 GB). Para tres estados es mucho más de lo que hace falta y superaría el límite de 5 GB del paquete.
- Los metadatos también nombran el Geospatial Data Gateway del NRCS (`https://datagateway.nrcs.usda.gov/`) como canal de descarga.

**3. Resolución.** Desde 2024 el CDL es de 10 m; NASS publica además una versión a 30 m por vecino más cercano "for consistency with historical CDL data". Para la serie 2008–2025 conviene usar la de 30 m en todos los años.

**4. Precisión por estado (CDL 2023, metadatos FGDC de cada estado).** Precisión del productor (1 − omisión) y del usuario (1 − comisión) contra los datos de validación de la FSA. Columnas en la fuente: píxeles, producer's accuracy, omission error, kappa, user's accuracy, commission error, conditional kappa.

| Estado | Global cultivos (kappa) | Maíz prod./usuario | Soja prod./usuario | Trigo inv. prod./usuario | Avena prod./usuario | Alfalfa prod./usuario | Otro heno prod./usuario |
|---|---|---|---|---|---|---|---|
| Iowa | 90,5 % (0,828) | 94,3 / 97,5 % | 94,3 / 96,7 % | 36,8 / 67,6 % | 35,6 / 67,2 % | 50,1 / 71,7 % | 7,2 / 35,7 % |
| Illinois | 90,2 % (0,829) | 93,1 / 96,6 % | 92,3 / 96,0 % | 61,4 / 74,4 % | 55,2 / 91,8 % | 40,9 / 67,3 % | 5,9 / 34,8 % |
| Indiana | 89,6 % (0,822) | 92,8 / 96,5 % | 92,5 / 96,0 % | 79,8 / 83,2 % | 6,3 / 27,3 % | 54,6 / 70,5 % | 15,1 / 43,5 % |

En la página de metadatos solo aparecen por estado los años hasta 2023 (`metadata-ia23`, `metadata-il23`, `metadata-in23`); para 2024 y 2025 hay metadatos nacionales. Los archivos viejos `metadata_ia23.htm` dan 404: las URL nuevas usan guion (`/research-and-science/cropland/metadata/metadata-ia23`). Consecuencia: las fracciones de maíz y soja del CDL son confiables; las de avena, alfalfa y heno son ruidosas (el heno se subestima mucho) y conviene avisarlo al equipo de ML.

**5. Estructura del CSB.** Fuente: metadatos FGDC "2025 Crop Sequence Boundaries" (versión rev23). Formato "geodatabase", proyección Albers cónica equivalente "as used by MRLC.gov (NLCD)". Un archivo nacional por ventana de 8 años (2008–2015 a 2018–2025; `NationalCSB_<inicio>-<fin>_rev23.zip`); no hay archivos por estado y el de 2018–2025 pesa 3,76 GB (medido por el paquete `cultivos`). Campos:

| Campo | Tipo | Definición (metadatos) |
|---|---|---|
| `OBJECTID` | entero | identificador interno |
| `Shape` | polígono | geometría |
| `CSBID` | texto | dígitos 1–2 = FIPS del estado; 3–4 = últimos dos dígitos del año inicial; 5–6 = del año final; los nueve restantes, secuenciales |
| `CSBACRES` | entero | área del polígono en acres |
| `CDL2018` … `CDL2025` | entero | cultivo mayoritario dentro del polígono según el CDL de ese año (códigos del CDL) |
| `STATEFIPS` | texto | FIPS del estado |
| `STATEASD` | texto | FIPS del estado + distrito agrícola (ASD) de NASS |
| `ASD` | texto | distrito agrícola de NASS |
| `CNTY` | texto | nombre del condado |
| `CNTYFIPS` | texto | FIPS del condado (3 dígitos; el `fips` de 5 dígitos = `STATEFIPS` + `CNTYFIPS`) |
| `INSIDE_X`, `INSIDE_Y` | real | coordenadas del centro del polígono |
| `Shape_Length`, `Shape_Area` | real | perímetro (m) y área (m²) calculados |

Los nombres de las columnas `CDL<año>` cambian con la ventana (en 2008–2015 serán `CDL2008`…`CDL2015`). Los polígonos son "fully synthetic": lotes de cultivo estimados, no parcelas catastrales. El código del algoritmo está en `https://github.com/USDA-REE-NASS/crop-sequence-boundaries` y permite armar ventanas propias.

Fuentes: [CDL legend colors (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/docs/cdl-legend-colors), consultado 2026-11-14; [2023 Iowa Cropland Data Layer – metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ia23), consultado 2026-11-14; [2023 Illinois Cropland Data Layer – metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-il23), consultado 2026-11-14; [2023 Indiana Cropland Data Layer – metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-in23), consultado 2026-11-14; [CroplandCROS and Cropland Data Layer – announcements (USDA NASS)](https://www.nass.usda.gov/Research_and_Science/Cropland/SARS1a.php), consultado 2026-11-14; [Cropland Data Layer – national download (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/release), consultado 2026-11-14; [CDL_WM ImageServer (CroplandCROS, USDA SCINet)](https://pdi.scinet.usda.gov/image/rest/services/CDL_WM/ImageServer?f=json), consultado 2026-11-14; [Crop Sequence Boundaries (USDA NASS)](https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php), consultado 2026-11-14; [Metadata – Crop Sequence Boundaries 2025 (USDA NASS)](https://www.nass.usda.gov/research-and-science/crop-sequence-boundaries/metadata-crop-sequence-boundaries-2025), consultado 2026-11-14; [crop-sequence-boundaries (GitHub, USDA-REE-NASS)](https://github.com/USDA-REE-NASS/crop-sequence-boundaries), consultado 2026-11-14

Confianza: alta (clases, precisión 2023 por estado, campos del CSB y resolución de 10 m salen de páginas oficiales de NASS; media para la parte de CropScape, que no respondió y no se pudo verificar directamente).

Impacto: paquete `cultivos`: `data/reference/clases_cdl.csv` (los códigos del CLAUDE.md quedan confirmados; agregar 0 = sin dato y, si se quiere, 27 centeno y 58 trébol); `src/cultivos/download.py` (ImageServer de CroplandCROS para 2022–2025, versión de 30 m); `rotacion_secuencia.csv` (si se usa el CSB: `fips` = `STATEFIPS` + `CNTYFIPS`, peso por `CSBACRES`, columnas `CDL<año>` según la ventana; el archivo nacional de 3,76 GB necesita decisión del humano por el límite de 5 GB); data card `docs/datasets/cultivos.md` (Problemas conocidos: precisión baja de avena, alfalfa y heno en el CDL).

Citas:
> "the CDL spatial resolution has been increased from 30-meter to 10-meter beginning in 2024." — [CroplandCROS and Cropland Data Layer – announcements (USDA NASS)](https://www.nass.usda.gov/Research_and_Science/Cropland/SARS1a.php)
> "majority crop type within the CSB polygon as identified in 2018 Cropland Data Layer" — [Metadata – Crop Sequence Boundaries 2025 (USDA NASS)](https://www.nass.usda.gov/research-and-science/crop-sequence-boundaries/metadata-crop-sequence-boundaries-2025)
> "first 2 places of the identifier are the state FIPS" — [Metadata – Crop Sequence Boundaries 2025 (USDA NASS)](https://www.nass.usda.gov/research-and-science/crop-sequence-boundaries/metadata-crop-sequence-boundaries-2025)
> "corn 1 340,138 94.3% 5.7% 0.912 97.5% 2.5% 0.960" — [2023 Iowa Cropland Data Layer – metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ia23)
> "FSA crops 593,834 90.2% 9.8% 0.829" — [2023 Illinois Cropland Data Layer – metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-il23)
> "FSA crops 588,721 89.6% 10.4% 0.822" — [2023 Indiana Cropland Data Layer – metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-in23)
> "36 alfalfa 255 168 227 #ffa8e3 37 other hay/non alfalfa" — [CDL legend colors (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/docs/cdl-legend-colors)
> "the data is available free for download through CroplandCROS" — [2023 Iowa Cropland Data Layer – metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ia23)
