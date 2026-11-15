# Máscaras de riego para Nebraska y Kansas

Pregunta: ¿Qué productos dan el área regada por píxel o por condado en Nebraska y Kansas (resolución, años,
método, dónde se bajan, licencia), cuáles tienen serie anual y cómo se podrían usar en el pipeline (% del área
agrícola regada por condado y año, o una máscara para sacar los píxeles regados del NDVI y del suelo)?

Respuesta corta: El único producto **anual, a 30 m y para todo el país** (es decir, que cubre NE y KS
completos) es **LANID-US** (Xie y Lark): mapas binarios de riego de **1997 a 2017**, en Albers, CC BY 4.0,
1,8 GB en Zenodo, con capas derivadas de frecuencia y de extensión máxima regada. Para el oeste de los dos
estados está además **AIM-HPA** (Deines et al., 2019): 30 m, anual, **1984–2017**, solo el área del acuífero
High Plains, EPSG:5070, CC BY 4.0, 0,9 GB en HydroShare y como asset de Earth Engine. **MIrAD-US** (USGS) cubre
el país, pero solo 2002, 2007, 2012 y 2017, a 250 m y 1 km, es provisional y según el paper de LANID omite
mucho riego en el este. **IrrMapper** no sirve: cubre "11 estados del oeste" y, en las fuentes que abrí, el
estado más al este que se nombra es Colorado. **LGRIP30** (NASA LP DAAC) es de un solo año nominal (2015). De
los organismos estatales: Kansas tiene una máscara binaria de riego "ca. 2007" (KARS, para 2003–2012),
calibrada contra NASS; Nebraska publica las superficies con derecho a riego (permitted/certified acres, 2023),
que dicen dónde *se puede* regar, no dónde se regó. **Ningún producto abierto que haya encontrado da una serie
anual de riego por píxel en NE y KS después de 2017.** Propuesta: usar LANID cruzado con el CDL y la máscara
agrícola para calcular por condado y año (2008–2017) el % regado del área agrícola, del maíz y de la soja, en
una tabla nueva del paquete `cultivos`, y una máscara estática "regado alguna vez 1997–2017" para calcular NDVI
de secano en `vegetacion`. Cambia esquemas: **necesita el OK del humano.**

Detalle:

## 1. Productos encontrados

| Producto | Cobertura | Resolución | Años | Serie anual | Licencia | Dónde |
|---|---|---|---|---|---|---|
| **LANID-US** v3.0 | CONUS (NE y KS completos) | 30 m | 1997–2017 | sí | CC BY 4.0 | Zenodo, DOI 10.5281/zenodo.5548555 |
| **AIM-HPA** | acuífero High Plains (oeste y centro de NE, oeste de KS) | 30 m | 1984–2017 | sí | CC BY 4.0 | HydroShare, DOI 10.4211/hs.a371fd69d41b4232806d81e17fe4efcb; asset GEE |
| **AIM-RRB** | cuenca del río Republican (NE, KS, CO) | 30 m | 1999–2016 | sí | no lo vi | HydroShare, DOI 10.4211/hs.55331a41d5f34c97baf90beb910af070 |
| **MIrAD-US** v4 | CONUS | 250 m y 1 km | 2002, 2007, 2012, 2017 | no (cada 5 años, con el censo) | dominio público según la búsqueda; la ficha de data.gov no lo dice | USGS, DOI 10.5066/P9NA3EO8 |
| **IrrMapper** v1.2 | 11 estados del oeste (no NE ni KS; ver abajo) | 30 m | 1986–2024 | sí | CC BY 4.0 | GEE `UMT/Climate/IrrMapper_RF/v1_2` |
| **LGRIP30** v001 (NASA) | global | 30 m | nominal 2015 (Landsat 8, 2014–2017) | no | abierto, sin restricción | LP DAAC, DOI 10.5067/Community/LGRIP/LGRIP30.001 |
| **Kansas Irrigation Mask ca. 2007** (KARS) | Kansas | 30 m | uso 2003–2012 | no (una sola capa) | "as is", sin garantía; cita obligatoria | ImageServer de KARS |
| **Statewide Permitted Acres** (NE DWEE) | Nebraska | polígonos | 2023 | no | no lo vi | FeatureServer de `dweegis.nebraska.gov` |

**LANID-US** (Landsat-based Irrigation Dataset). Lo verifiqué en Zenodo y en el artículo de ESSD.
- Archivos: `lanid1997-2003.zip` (350 MB), `lanid2004-2010.zip` (358 MB), `lanid2011-2017.zip` (361 MB), `irrFreqAndChange.zip` (593 MB), `irrFreqPasture_West.tif`, `groundReference_eastCONUS.zip`, `Metadata.docx` y una descripción del método en PDF. Total: 1,8 GB, por debajo del límite de 5 GB de la regla 6.
- Capas: `lanidYYYY` (binaria anual), `irrFreq` (cantidad de años regados en 1997–2017) y `maxIrrExt` (regado al menos una vez en 1997–2017), más capas de cambio y de áreas que dejaron de regarse o se riegan de forma intermitente.
- Método: random forest por condado en Google Earth Engine, con composiciones Landsat de GI, EVI y NDWI, EVI y LST de MODIS desde 2001, clima, relieve, humedad del suelo y distancia a ríos. Después, filtros lógicos y espaciales. Las estadísticas de riego del Censo Agropecuario por condado (1997–2017) se usaron para fijar umbrales de entrenamiento en el oeste. En el este, las muestras se interpretaron a ojo (unas 5.000 regadas y 5.000 de secano).
- Precisión: global mayor a 90 % en todos los años y regiones; 94,4 % en el este, donde los otros productos dan menos de 60 %. En el área del High Plains, LANID da 95,9 % contra 93,2 % de AIM-HPA (kappa 0,89 contra 0,82).
- La versión 2 sumó pasturas y heno regados en el oeste (máscara de NLCD + "other hay" del CDL).
- Proyección: Albers de igual área, 30 m. El EPSG exacto y si la grilla coincide con la del CDL no figuran en las páginas que abrí. Hay que verificarlo en `Metadata.docx` al bajarlo.
- Zenodo muestra la versión 3.0 (modificada en julio de 2024), sin versiones más nuevas. El artículo dice que el método "se puede extender" después de 2017, pero no encontré ninguna extensión publicada.

**AIM-HPA** (Annual Irrigation Maps – High Plains Aquifer). Lo verifiqué en HydroShare.
- EPSG:5070, 30 m. Valores: 0 = sin dato (fuera del área), 1 = regado, 2 = no regado.
- Random forest único aplicado cada año sobre Landsat en GEE, más el algoritmo BULC para llenar huecos y bajar errores de comisión.
- Precisión: alrededor de 91 %. Explica el 85 % de la variación del área regada por condado de NASS.
- Asset GEE: `projects/h2yo/IrrigationMaps/AIM/AIM-HPA/AIM-HPA_Deines_etal_RSE_v01_1984-2017`.
- Cobertura: 608.260 km², caja de 31,5–43,9° N y 106,2–96,1° O. Cubre el oeste y el centro de Nebraska y el oeste de Kansas, pero **no el este de Kansas** (el estado llega hasta 94,6° O) ni el extremo este de Nebraska. No sirve sola para todo NE+KS. Sí sirve como control de LANID donde está la mayor parte del riego.

**AIM-RRB.** El antecesor de AIM-HPA, solo en la cuenca del Republican (141.603 km² entre CO, KS y NE), 1999–2016, 30 m. Lo reemplaza AIM-HPA. Solo vi la descripción en los resultados de búsqueda, no la página.

**MIrAD-US** (MODIS Irrigated Agriculture Dataset), versión 4. Lo verifiqué en la noticia del USGS y en la ficha de data.gov.
- Años 2002, 2007, 2012 y 2017; 250 m y 1 km; CONUS.
- Combina la superficie regada por condado del censo, el NDVI pico anual de eMODIS (Aqua C6) y una máscara agrícola del NLCD. Reparte el área del censo en los píxeles más verdes de cada condado.
- El USGS lo llama "provisional hasta que se complete una evaluación formal de precisión".
- El paper de LANID le encuentra más de 80 % de omisión en el este y artefactos en los límites de condado.
- Tanto la ficha del catálogo de USGS (`data.usgs.gov`, HTTP 403) como el DOI no los pude abrir. No verifiqué los nombres de archivo ni la licencia exacta.

**IrrMapper.** Lo verifiqué en el catálogo de GEE (v1.2: `UMT/Climate/IrrMapper_RF/v1_2`, 1986–2024, banda `classification`, 1 = regado, CC BY 4.0), en la página de la Universidad de Montana y en el resumen del paper (Ketchum et al., 2020: 97,8 % binario, r² 0,90 por condado contra el censo). Todas dicen "11 western states" sin nombrarlos. El único estado de las llanuras que se nombra es Colorado ("plains of eastern Colorado"). **No pude abrir la lista exacta de estados** (MDPI devolvió 403). Los "11 estados del oeste" son por convención AZ, CA, CO, ID, MT, NV, NM, OR, UT, WA y WY. La comparación del paper de LANID trata a IrrMapper como "11 western states" frente a LANID "CONUS", lo que es coherente con que no incluya NE ni KS. Confianza media en la exclusión: hay que verificarlo con la geometría del asset antes de descartarlo del todo.

**LGRIP30** (NASA, LP DAAC). Lo verifiqué en el catálogo de Earthdata.
- Tierra de cultivo de secano, regada, no cultivada y agua. 30 m, GeoTIFF en teselas de 10°.
- Año nominal 2015, con Landsat 8 de 2014–2017. Una sola capa, sin serie.
- La página no da la precisión para EE.UU. (está en el ATBD, que no abrí).
- Es el único producto NASA. Sirve, como mucho, de comparación para un año.

**LRIP30 CONUS 2020.** Producto de riego y secano para EE.UU. del año 2020 (Teluguntla et al.). Solo lo vi como título en ResearchGate: no abrí la publicación ni encontré dónde se baja. Un solo año.

**Kansas Irrigation Mask ca. 2007** (Kansas Applied Remote Sensing Program, 2014). Lo verifiqué en el ImageServer de KARS (`services.kars.geoplatform.ku.edu/.../KansasIrrigationMaskCirca2007/ImageServer`, 30 m, U8, wkid 102039 = USA Contiguous Albers USGS).
- Binaria: 1 = regado, 0 = no regado. "Aplicable a 2003–2012 junto con el uso del suelo anual".
- Método: se restringe a los "Place of Use" con permiso de riego de la Division of Water Resources de Kansas. Árboles de decisión con NDVI de MODIS entrenados con registros de la FSA de 2003–2007, el CDL para el cultivo y lotes digitalizados sobre NAIP.
- Después **se ajusta por condado hasta igualar las cifras de NASS** de 2007 (sorgo y trigo) y pone toda la soja dentro de los Place of Use como regada. La coincidencia con NASS es calibración, no validación, y no hay una evaluación de precisión independiente.
- Una sola capa y solo para Kansas. Queda por debajo de LANID.

**Statewide Permitted Acres** (Nebraska Department of Water, Energy and Environment, ex-DNR). Según la descripción que muestra la búsqueda, son polígonos de superficie con permiso de riego (de agua subterránea, superficial o mixta) para la campaña 2023. Los datos de agua subterránea vienen de los NRD. "No necesariamente regada en el año". El servicio `dweegis.nebraska.gov` **no respondió** en esta corrida (timeout con curl, conexión rechazada con WebFetch). No pude verificar los campos ni si se puede exportar. Sirve para acotar dónde *puede* haber riego, igual que los Place of Use en Kansas, pero no como serie.

**Kansas WIMAS** (KGS, para la Division of Water Resources). Uso de agua declarado por derecho de agua y punto de toma, actualizado seguido. Un servicio de KU publica una capa de puntos de toma para riego. Son puntos, no superficies regadas por año. Solo leí descripciones; no lo abrí.

## 2. Cuáles tienen serie anual

- **Anuales:** LANID (1997–2017, todo NE y KS), AIM-HPA (1984–2017, solo el High Plains), AIM-RRB (1999–2016, solo la cuenca del Republican) e IrrMapper (1986–2024, pero no cubre NE ni KS).
- **Un año o cada 5 años:** MIrAD-US (2002, 2007, 2012 y 2017), LGRIP30 (ca. 2015), LRIP30 (2020), la máscara de Kansas (ca. 2007) y los permitted acres de NE (2023).
- **Hueco 2018–2025:** no encontré una serie anual abierta por píxel. Lo que queda es el Censo Agropecuario 2017 y 2022 por condado (ya está en `docs/research/riego_nass.md` y en `practicas_censo.csv`: `pct_riego`) y la estimación por práctica de NASS hasta 2018 o 2019 (T004).

## 3. Cómo se podría usar

**a) % regado por condado y año (2008–2017; 2000–2017 sin cruzar con el CDL).**
- Pasar `lanidYYYY` a la grilla de `data/reference/mascara_agricola.tif` (EPSG:5070, 30 m) con vecino más cercano, si no está ya alineado.
- Por condado y año: `pct_agricola_riego = 100 × píxeles agrícolas regados / píxeles agrícolas`.
- Con el CDL del año (2008–2017): `pct_maiz_riego` y `pct_soja_riego` = píxeles de maíz (o soja) regados / píxeles de maíz (o soja).
- **Control:** esos porcentajes se pueden comparar con `IRRIGATED / ALL` de la superficie sembrada de NASS por condado (T004, 2008–2018). Es un control independiente (LANID no usó NASS por cultivo).

**b) Máscara para NDVI y suelo.**
- `mascara_riego_max.tif` = `maxIrrExt` de LANID (regado al menos una vez en 1997–2017), en la grilla de `mascara_agricola.tif`.
- Para el NDVI de MODIS de 250 m, aplicar el mismo criterio que con las máscaras de cultivo (§6.3: un píxel cuenta si 75 % o más de su área es del tipo). Así se calculan `ndvi_secano`, `ndvi_maiz_secano` y `ndvi_soja_secano`.
- En `suelo_terreno` no hace falta excluir: el suelo no cambia con el riego. Si acaso, sirve un `frac_riego_max` estático por condado para que ML pondere.
- Usar la máscara *máxima* y no la anual evita el hueco posterior a 2017: un píxel que se regó alguna vez en 21 años tiene equipo de riego (pivote) y muy probablemente se sigue regando. **Esto es un supuesto**; los pivotes nuevos posteriores a 2017 quedan como secano.

## 4. Propuesta (pendiente de aprobación del humano)

**Producto:** LANID-US v3.0 (Zenodo 10.5281/zenodo.5548555), para NE y KS, y para todos los estados si se quiere
comparar el Corn Belt completo (también cubre IA, IL, IN, OH y MN, donde el riego es marginal). AIM-HPA, solo
como control en el oeste de NE y KS (no entra en los CSV).

**Paquete:** `cultivos` (ya tiene el CDL, la máscara agrícola y NASS). Descarga de 1,8 GB a `data/raw/riego_lanid/`.

**Tabla nueva `riego_anual.csv`** (`fips, anio`; 2000–2017; vacía desde 2018):

| Columna | Descripción | Años |
|---|---|---|
| `pct_agricola_riego_lanid` | % de píxeles de la máscara agrícola regados según LANID | 2000–2017 |
| `pct_maiz_riego_lanid` | % de píxeles de maíz del CDL regados | 2008–2017 |
| `pct_soja_riego_lanid` | % de píxeles de soja del CDL regados | 2008–2017 |
| `frac_pixeles_validos` | como en el contrato (§4) | — |

**Columna estática:** `pct_agricola_riego_max_lanid` (`maxIrrExt` sobre la máscara agrícola) en `cultivos`
(o en `suelo_terreno_estatico.csv`, si el humano prefiere tener lo estático junto).

**Referencia:** `data/reference/mascara_riego_max.tif` (EPSG:5070, grilla de `mascara_agricola.tif`), para que
`vegetacion` pueda sumar `ndvi_secano` en otra tarea.

Alternativa más chica, sin tabla nueva: agregar solo `pct_agricola_riego_lanid` a `rotacion_anual.csv`. Igual
cambia el esquema.

Supuestos para el data card: celdas vacías desde 2018 (no hay producto, no "sin riego"); la máscara máxima
como proxy de riego después de 2017; LANID se usa tal cual, sin recalibrarlo contra NASS.

Fuentes:
- [Zenodo, "LANID-US: Landsat-based Irrigation Dataset for the United States", v3.0](https://zenodo.org/records/5548555), consultado 2026-11-15.
- [Xie, Y., et al. (2021), "Landsat-based Irrigation Dataset (LANID): 30 m resolution maps of irrigation distribution, frequency, and change for the US, 1997–2017", ESSD 13, 5689–5710](https://essd.copernicus.org/articles/13/5689/2021/), consultado 2026-11-15.
- [HydroShare, "Annual Irrigation Maps – High Plains Aquifer (AIM-HPA, Deines et al. 2019)"](https://www.hydroshare.org/resource/a371fd69d41b4232806d81e17fe4efcb/), consultado 2026-11-15.
- [HydroShare, AIM-RRB (Deines et al. 2017)](https://hydroshare.org/resource/55331a41d5f34c97baf90beb910af070/), consultado 2026-11-15 (solo la descripción en los resultados de búsqueda).
- [USGS, "MIrAD Version 4 250-meter resolution and 1-kilometer resolution dataset released"](https://www.usgs.gov/news/mirad-version-4-250-meter-resolution-and-1-kilometer-resolution-dataset-released), consultado 2026-11-15.
- [data.gov, MIrAD-US](https://catalog.data.gov/dataset/moderate-resolution-imaging-spectroradiometer-modis-irrigated-agriculture-datasets-for-the), consultado 2026-11-15.
- [Google Earth Engine, "IrrMapper Irrigated Lands, Version 1.2"](https://developers.google.com/earth-engine/datasets/catalog/UMT_Climate_IrrMapper_RF_v1_2), consultado 2026-11-15.
- [Montana Climate Office, IrrMapper](https://climate.umt.edu/research/irrmapper/), consultado 2026-11-15.
- [NSF PAR, Ketchum et al. (2020), "IrrMapper: A Machine Learning Approach for High Resolution Mapping of Irrigated Agriculture Across the Western U.S."](https://par.nsf.gov/biblio/10192099), consultado 2026-11-15.
- [NASA Earthdata, "Landsat-Derived Global Rainfed and Irrigated-Cropland Product 30 m V001" (LGRIP30)](https://www.earthdata.nasa.gov/data/catalog/lpdaac-ecs-lgrip30-001), consultado 2026-11-15.
- [KARS, "Kansas Irrigation Mask ca. 2007", ImageServer y metadatos](https://services.kars.geoplatform.ku.edu/arcgis/rest/services/KansasLandCover/KansasIrrigationMaskCirca2007/ImageServer/info/iteminfo), consultado 2026-11-15.
- [Nebraska DWEE, Statewide Permitted Acres (FeatureServer)](https://dweegis.nebraska.gov/weegis/rest/services/Statewide_Permitted_Acres/FeatureServer/0), consultado 2026-11-15: no respondió; la descripción sale del resultado de búsqueda.
- No abiertos (solo los vi en resultados de búsqueda): LRIP30 CONUS 2020 (ResearchGate), ficha de MIrAD en `data.usgs.gov` (HTTP 403), WIMAS de Kansas.

Confianza: alta en LANID y AIM-HPA (años, resolución, licencia, archivos y precisión, vistos en las páginas
oficiales); alta en que no hay serie anual abierta después de 2017 entre los productos revisados, pero media en
que no exista ninguna (puede haber trabajos recientes que no encontré); media en que IrrMapper excluya NE y KS
(no vi la lista de estados); baja en los productos estatales de Nebraska (servicio caído).

Impacto: paquete `cultivos` (descarga nueva de LANID, 1,8 GB; tabla nueva `riego_anual.csv` o columnas en
`rotacion_anual.csv`; data card), `data/reference/mascara_riego_max.tif`, y después `vegetacion`
(`ndvi_secano`). Complementa la propuesta de `docs/research/riego_nass.md` (T004).
