# Riego por condado en Nebraska y Kansas: qué fuente usar para `frac_riego`

Pregunta: ¿Qué fuentes dan el área regada por condado y por año (NASS SURVEY `IRRIGATED` / `NON-IRRIGATED`,
MIrAD-US, LANID, USGS Water Use), con qué resolución, años, formato y licencia, si cubren también IA, IL, IN, OH
y MN, cuál conviene para una columna anual `frac_riego` por condado y cómo separar el rendimiento de riego y de
secano en `produccion_anual.csv`?

Respuesta corta: Para una columna **anual** `frac_riego` por condado la mejor fuente es **LANID** (30 m, binario
regado / no regado, todo el país, así que cubre los 7 estados): la versión de Zenodo trae **1997–2017** y una
publicación posterior del USGS (Martin y Brandt, 2024, DOI 10.5066/P9YWR0OJ) agrega **2018, 2019 y 2020** con el
mismo método. Eso da 2000–2020 sin huecos. Para 2021–2025 no hay producto anual abierto: queda el Censo 2022
(`pct_riego` de `practicas_censo.csv`) o la capa de extensión máxima de LANID, y es decisión de ML cuál usar.
Las otras fuentes no son anuales o no son por condado: el **Censo Agropecuario** y el **USGS Water Use** (acres
regados por condado, `IR-IrTot`) son cada 5 años; **MIrAD-US** es cada 5 años, a 250 m / 1 km, provisional y
calibrado con el censo. **NASS SURVEY por práctica** es la única fuente con **rendimiento** de riego y de secano,
pero solo hasta 2018 (maíz y soja) o 2019 (trigo de invierno) y, en lo que está verificado, para NE y KS
(no verifiqué si existe para IA, IL, IN, OH y MN). Separar el rendimiento en `produccion_anual.csv` requiere
**columnas nuevas** (la Opción A de `docs/research/riego_nass.md`): es un cambio de esquema y lo decide el humano.

Detalle:

Este documento resume y completa dos research anteriores:
- `docs/research/riego_nass.md` (T004): NASS por práctica en NE y KS, con conteos sobre el archivo completo de Quick Stats.
- `docs/research/riego_mascaras.md` (T018): productos de mapas de riego (LANID, AIM-HPA, MIrAD, IrrMapper, LGRIP30, estatales).

Lo nuevo en esta tarea es: (1) la extensión **LANID 2018–2020** del USGS, que T018 no había encontrado (decía
"no encontré ninguna extensión publicada"); (2) el **USGS Water Use** por condado, con sus columnas de acres
regados; (3) los metadatos oficiales de MIrAD-US v4; (4) la recomendación para `frac_riego`.

## 1. Comparación de fuentes

| Fuente | Qué mide | Unidad espacial | Años | Formato | Licencia / uso | IA, IL, IN, OH, MN |
|---|---|---|---|---|---|---|
| NASS Quick Stats SURVEY, `IRRIGATED` / `NON-IRRIGATED` | sembrada, cosechada, producción y **rendimiento** por práctica | condado (con fila 998 por distrito) | maíz y soja 2000–2018; trigo de invierno 2000–2019; alfalfa y sorgo 2000–2009 (NE y KS) | API o archivo `qs.crops_*.txt.gz` | dominio público (USDA) | **no verificado** (ver §2) |
| Censo Agropecuario (`SOURCE_DESC=CENSUS`) | tierra regada total (`AG LAND, IRRIGATED`) y cosechada con riego por cultivo | condado, con `(D)` | 1997, 2002, 2007, 2012, 2017, 2022 | ídem | dominio público | sí (es nacional; `pct_riego` ya está para los 7 estados en `practicas_censo.csv`) |
| **LANID-US** v3.0 (Xie, Gibbs y Lark) | píxel regado / no regado | 30 m, Albers | **1997–2017** anual | GeoTIFF en zips, 1,8 GB (Zenodo) | CC BY 4.0 | sí (CONUS) |
| **LANID 2018–20** (USGS, Martin y Brandt) | píxel regado (1) / no regado (0) | 30 m, Albers Conical Equal Area, NAD83 | **2018, 2019, 2020** anual | `lanid2018.tif`, `lanid2019.tif`, `lanid2020.tif`, `maxIrrExt_0020.tif` | sin restricción de uso; se puede redistribuir sin editar y citándolo; "no warranty" | sí (CONUS) |
| MIrAD-US v4 (USGS EROS) | píxel regado | 250 m y 1 km, Lambert Azimuthal Equal Area | 2002, 2007, 2012, 2017 | raster (`mirad1km_(xx)v4`, `mirad250_…`) | sin restricción de uso indicada; "no guarantee of warranty" | sí (CONUS) |
| USGS Water Use, compilación por condado | acres regados (`IR-IrTot`, por aspersión, micro y superficie) y extracciones (Mgal/d) | condado (`FIPS`) | cada 5 años, 1985–2015 | CSV / XLSX y TXT | "none" en restricciones de uso | sí (nacional) |
| USGS, reanálisis mensual de riego por HUC12 | ETa, consumo, área regada | HUC12 (no condado) | 2000–2020 mensual | no visto | no visto | sí (CONUS) |

### LANID 2018–2020 (nuevo)

Verificado en el XML de metadatos oficial (`data.usgs.gov/datacatalog/metadata/USGS.63b5dbd9d34e92aad3caa517.xml`).
La ficha de ScienceBase (a la que lleva el DOI) devolvió HTTP 403 / Cloudflare, así que **no vi los tamaños de
los archivos ni los enlaces directos**.
- Título: "LANID: Landsat-based irrigation dataset for CONUS 2018-20". Autores: Donald J. Martin y Justin T. Brandt (USGS), 2024-09-26.
- Cita: "Annual LANID maps for 2018 -20 were created using the same techniques in Xie and others, 2021, and Xie and Lark, 2021."
- Cita: "Maps have 30-meter resolution and each pixel has a value of one for irrigated land and a value of zero for non-irrigated land."
- Entidades del archivo: `lanid2020.tif`, `lanid2019.tif`, `lanid2018.tif` y `maxIrrExt_0020.tif`. Raster de 95.128 filas × 153.749 columnas (CONUS a 30 m), proyección Albers Conical Equal Area, datum NAD83.
- `maxIrrExt_0020.tif`: por el nombre, la extensión máxima regada en 2000–2020, pero **los metadatos no lo dicen explícitamente**; hay que verificarlo al bajarlo.
- Es parte de un reanálisis mensual de uso de agua de riego 2000–2020 por HUC12 (SSEBop / OpenET + National Hydrologic Model). Las tablas por HUC12 no figuran entre las entidades de este XML; no sé si están en otra publicación hija.
- Restricciones: "This dataset may be redistributed if it is not edited and is properly referenced." No hay tasa ni licencia CC explícita; como producto del USGS es de dominio público, pero eso es mi lectura, no una frase de la ficha.
- Faltan por verificar: si la grilla de LANID está alineada con la del CDL (EPSG:5070); el EPSG exacto (el XML solo dice "Albers Conical Equal Area" y NAD83, sin parámetros en el campo `mapprojp`).

### USGS Water Use por condado (nuevo)

Verificado en dos XML de metadatos oficiales; las páginas de `usgs.gov` no cargaron (timeout) y ScienceBase devolvió 403.
- **2015** (Dieter y Linsey, v2.0, 2018; `USGS.5af3311be4b0da30c1b245d8`): archivo `usco2015v2.0.csv` y `.xlsx`, una fila por condado (`STATEFIPS`, `COUNTYFIPS`, `FIPS`). Columnas de acres regados en miles de acres: `IR-IrSpr` (aspersión), `IR-IrMic` (microrriego), `IR-IrSur` (superficie), `IR-IrTot` (total); separadas en cultivos (`IC-IrTot`, "Irrigation-Crop") y golf (`IG-IrTot`). Restricciones de uso: "none".
- **1985–2015** (Luukkonen et al., 2021; DOI 10.5066/P9TA1DI9; `USGS.607607ffd34e018b3201cb92`): `IRRIGATION_FinalTable.txt` con las estimaciones de condado de las compilaciones quinquenales (1985, 1990, …, 2015), con columnas `IR.IrSpr`, `IR.IrMic`, `IR.IrSur` y el código de método de cada valor (`*.M`).
- **2020:** no encontré una compilación por condado. Lo único de 2020 que vi es el reanálisis modelado por HUC12 (arriba). Confianza media: puede existir y no la encontré.
- Uso posible: control de LANID y del censo, y solo cada 5 años. Los acres regados del USGS suelen salir del censo o de agencias estatales (cada valor trae su código de método), así que no es una fuente independiente.

### MIrAD-US v4

Verificado en el XML de metadatos oficial (`USGS.5db08e84e4b0b0c58b56e04f`, publicado 2019-10-31). Confirma lo
de T018: 2002, 2007, 2012 y 2017; 250 m y 1 km; reparte el área regada del censo por condado en los píxeles con
NDVI pico más alto dentro de una máscara agrícola del NLCD ("should be considered provisional until a formal
accuracy assessment can be completed"). Nuevo: la proyección es Lambert Azimuthal Equal Area (hay que
reproyectar a EPSG:5070) y la restricción de uso es solo "no guarantee of warranty". Como está forzado a
coincidir con el censo por condado, por condado no agrega nada al `pct_riego` del censo.

## 2. NASS por práctica en los otros estados

En NE y KS está verificado con el archivo completo (T004, `riego_nass.md`). Para IA, IL, IN, OH y MN **no lo
verifiqué**: en esta máquina no está `qs.crops_*.txt.gz`, no hay `NASS_API_KEY` y la tarea pide no bajar
datasets grandes (el archivo pesa 1,13 GB). La cuenta se hace con el mismo filtro de T004 (`SOURCE_DESC=SURVEY`,
`AGG_LEVEL_DESC=COUNTY`, `PRODN_PRACTICE_DESC` en `IRRIGATED` / `NON-IRRIGATED`) en cualquier máquina que ya
tenga el archivo, o con `get_counts` de la API. De todos modos, cualquier dato que exista termina en 2018 o 2019
(la discontinuación del Federal Register es nacional).

## 3. Recomendación para `frac_riego` anual

**Fuente: LANID** (Zenodo 1997–2017 + USGS 2018–2020), para los 7 estados.

- Cálculo por condado y año: `frac_riego = píxeles de la máscara agrícola regados según LANID / píxeles de la máscara agrícola`, en la grilla de `data/reference/mascara_agricola.tif` (EPSG:5070, 30 m; vecino más cercano si LANID no está alineado).
- Con el CDL del año (2008–2020) también `frac_riego_maiz` y `frac_riego_soja` (píxeles de maíz o soja regados / píxeles de maíz o soja).
- **Años:** 2000–2020 con dato. **2021–2025 vacíos** (no hay producto, no "sin riego"). Si ML necesita un valor para esos años, hay dos opciones, ambas supuestos que tendría que elegir ML: `frac_riego` de 2020 arrastrado, o la fracción de `maxIrrExt` (regado alguna vez) como columna estática aparte.
- **Controles (no van en el CSV):** `IRRIGATED / ALL` de la superficie sembrada de NASS en NE y KS (2000–2018) para maíz y soja, y `pct_riego` del censo en 2002, 2007, 2012 y 2017. Ojo: en el oeste LANID calibró sus umbrales de entrenamiento con el área regada del censo por condado, así que el control con el censo no es independiente allí; el de NASS por cultivo sí lo es.
- **Descarga:** 1,8 GB (Zenodo) + los tres TIF de 2018–2020 (tamaño no visto, porque ScienceBase no abrió). Hay que confirmar que el total quede por debajo de 5 GB antes de bajar (regla 6).
- **Nombre:** la tarea pide `frac_riego` (0 a 1). El resto de las columnas de riego ya existentes usa `pct_` (0 a 100: `pct_riego` del censo, y la propuesta de T018 era `pct_agricola_riego_lanid`). Conviene elegir uno solo; propongo `frac_riego_lanid` (0–1), con el sufijo de la fuente para que no se confunda con el `pct_riego` del censo.
- **Dónde:** tabla nueva `riego_anual.csv` (`fips, anio, frac_riego_lanid, frac_riego_maiz_lanid, frac_riego_soja_lanid, frac_pixeles_validos`) en el paquete `cultivos`, o columnas al final de `rotacion_anual.csv`. Cualquiera de las dos cambia o agrega un esquema: **decide el humano.**

Por qué no las otras: el censo, MIrAD y el USGS Water Use son cada 5 años (interpolar entre censos sería
inventar la serie); NASS por práctica termina en 2018 y no tiene todos los condados; AIM-HPA no cubre el este de
KS ni los otros estados.

## 4. Rendimiento de riego y de secano en `produccion_anual.csv`

No hay forma de separarlos **sin** cambiar el esquema: las claves son `fips, anio, cultivo`, y una fila por
práctica agregaría una clave. La única fuente de rendimiento por práctica es NASS SURVEY (NE y KS: maíz y soja
2000–2018, trigo de invierno 2000–2019).

Cambio mínimo que propongo (es la Opción A de `riego_nass.md`, con el detalle de las columnas ahí): **agregar
columnas al final, mismas claves**: `sup_sembrada_riego_ac`, `sup_sembrada_secano_ac`, `sup_cosechada_riego_ac`,
`sup_cosechada_secano_ac`, `produccion_riego_bu`, `produccion_secano_bu`, `rend_riego_bu_ac`,
`rend_secano_bu_ac`, `rend_riego_kgha`, `rend_secano_kgha`, `pct_sembrada_riego`. Vacías donde NASS no publica
(después de 2018/2019, condados combinados en la fila 998, avena, alfalfa y heno, y los otros estados si no
tienen dato). Las filas existentes no cambian, así que `merge.py` y lo que ya consume el CSV siguen funcionando.

Para 2019–2025 no hay rendimiento por práctica en ninguna fuente abierta que haya visto. Lo que ML puede hacer es
usar `frac_riego_lanid` (o el censo) como covariable del rendimiento total, no separarlo.

Fuentes:
- [USGS, metadatos "LANID: Landsat-based irrigation dataset for CONUS 2018-20" (Martin y Brandt, 2024), XML](https://data.usgs.gov/datacatalog/metadata/USGS.63b5dbd9d34e92aad3caa517.xml), consultado 2026-11-15.
- [data.gov, "LANID: Landsat-based irrigation dataset for CONUS 2018-20"](https://catalog.data.gov/dataset/lanid-landsat-based-irrigation-dataset-for-conus-2018-20), consultado 2026-11-15. El DOI [10.5066/P9YWR0OJ](https://doi.org/10.5066/P9YWR0OJ) lleva a ScienceBase, que devolvió 403.
- [USGS, metadatos "Estimated Use of Water in the United States County-Level Data for 2015" (v2.0), XML](https://data.usgs.gov/datacatalog/metadata/USGS.5af3311be4b0da30c1b245d8.xml), consultado 2026-11-15.
- [USGS, metadatos "Public supply, self-supplied domestic, irrigation, and thermoelectric water-use data from 5-year compilation datasets from 1985 to 2015…" (Luukkonen et al., 2021), XML](https://data.usgs.gov/datacatalog/metadata/USGS.607607ffd34e018b3201cb92.xml), consultado 2026-11-15.
- [USGS, metadatos "MODIS Irrigated Agriculture Datasets for the Conterminous United States (MIrAD-US)", XML](https://data.usgs.gov/datacatalog/metadata/USGS.5db08e84e4b0b0c58b56e04f.xml), consultado 2026-11-15; ficha en [data.gov](https://catalog.data.gov/dataset/moderate-resolution-imaging-spectroradiometer-modis-irrigated-agriculture-datasets-for-the).
- Las fuentes de NASS, el Federal Register 2019-24789, LANID en Zenodo, AIM-HPA e IrrMapper están citadas en `docs/research/riego_nass.md` y `docs/research/riego_mascaras.md` (consultadas el 2026-11-15); no las volví a abrir.
- No cargaron: las páginas de `usgs.gov` sobre water use (timeout) y las fichas de ScienceBase (403 / Cloudflare).

Confianza: alta en la existencia, años, resolución y archivos de LANID 2018–2020 y en las columnas de acres
regados del USGS Water Use (metadatos oficiales); media en que no haya compilación por condado del USGS para 2020
y en el significado de `maxIrrExt_0020`; sin verificar la cobertura de NASS por práctica en IA, IL, IN, OH y MN y
el tamaño de los TIF de 2018–2020.

Impacto: paquete `cultivos` (descarga nueva de LANID 1997–2020 a `data/raw/riego_lanid/`; tabla nueva
`riego_anual.csv` o columnas en `rotacion_anual.csv`; columnas nuevas en `produccion_anual.csv`; data card
`docs/datasets/cultivos.md`). Actualiza `docs/research/riego_mascaras.md`, que daba LANID como terminado en 2017.
