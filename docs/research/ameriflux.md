# Sitios AmeriFlux del Corn Belt para validar la ET

Pregunta: ¿qué torres de flujo de AmeriFlux hay sobre cultivos en IA, IL, IN, OH, NE, MN y KS? Para cada una:
qué cultivo tiene por año, en qué años hay datos, qué variables (LE, ET, GPP) y en qué versión (BASE o
FLUXNET), cómo se bajan y con qué licencia, en qué condado (`fips`) está y contra qué columnas de nuestros CSV
se puede comparar. Sale de T030 (`docs/research/agua_por_cultivo.md`), que propone validar la ET de MODIS,
ECOSTRESS y NLDAS con torres.

Respuesta corta:

- **Hay 72 sitios AmeriFlux en los 7 estados** con cobertura de cultivo (CRO, 53), pastizal (GRA, 16) o
  mosaico (CVM, 3). De los de cultivo, **40 tienen datos publicados** (BASE o FLUXNET). 16 de los 72 no publicaron nada todavía.
- **Los mejores para validar la ET de 2000 a 2025 son los tres de Mead, Nebraska (US-Ne1, US-Ne2 y US-Ne3, en
  el condado 31155).** Tienen BASE de 2001 a 2025 y FLUXNET-1F de 2001 a 2024, licencia CC-BY-4.0 y una
  rotación conocida año por año. Ne1 y Ne2 se riegan con pivote y Ne3 es de secano.
- Los siguen, en orden: **US-Ro1, US-Ro2, US-Ro5 y US-Ro6** (Rosemount, MN, condado 27037), **US-UiC y US-UiG**
  (Champaign, IL, 17019), **US-MN1, US-MN2 y US-MN3** (Morris, MN, 27149), **US-IAB y US-IAC** (Boone, IA,
  19015) y **US-Bo1** (Bondville, IL, 17019; solo BASE, de 1996 a 2008).
- **No hay ninguna torre agrícola con datos en Kansas.** Las 8 torres de Kansas que entran en el filtro son de pastizal. En Ohio hay
  una sola agrícola, US-CRT (Lucas, 39095), con soja y trigo de 2011 a 2013.
- **Variables:** FLUXNET-1F trae el calor latente **LE_F_MDS** (rellenado, en W/m²), sus versiones con el
  balance de energía corregido (**LE_CORR**) y **GPP_NT_VUT_REF** / GPP_DT_VUT_REF, en resolución horaria,
  diaria, semanal, mensual y anual. **Ningún producto trae la ET en mm**: se calcula a partir de LE con el
  calor latente de vaporización. BASE trae LE y H2O medidos, sin rellenar y sin partición de GPP.
- **Descarga:** pide una **cuenta personal de AmeriFlux** (registro gratuito). Antes de cada descarga hay que
  aceptar la política de uso y declarar el uso previsto, que se manda a los responsables del sitio y se
  publica en el registro de descargas. La mayoría de los sitios usan **CC-BY-4.0**. US-Br1, US-Br3, US-CLN y
  US-CLS siguen con la **Legacy Policy**, más restrictiva. La descarga la hace el humano.

## Detalle

### 1. Cómo se armó la lista

Con la API pública de AmeriFlux, que no pide login para los metadatos:

- `https://amfcdn.lbl.gov/api/v1/site_display/AmeriFlux`: 858 sitios, con ID, nombre, estado, IGBP,
  coordenadas y años de la torre.
- `https://amfcdn.lbl.gov/api/v1/data_availability/AmeriFlux/<producto>/<política>`: años publicados por
  sitio, con `<producto>` = `BASE-BADM` o `FLUXNET` y `<política>` = `CCBY4.0` o `LEGACY`. La lista
  `LEGACY` incluye también los sitios CC-BY-4.0, porque esos se pueden usar bajo cualquiera de las dos.
  Si un sitio aparece solo en `LEGACY`, su política es Legacy. Para FLUXNET, `LEGACY` vuelve vacía: el
  procesamiento ONEFlux solo se aplica a datos CC-BY-4.0, como dice la página de la política.
- Filtro: `STATE` en IA, IL, IN, OH, NE, MN o KS e `IGBP` en CRO, GRA o CVM.
- **Condado:** el `fips` sale del geocodificador del Census (`geocoding.geo.census.gov`, capa Counties,
  vintage actual), consultado con las coordenadas de cada torre. No se usó `condados.csv`, que esta copia del
  repo no tiene.
- **Cultivo y manejo:** salen de la descripción de la página de cada sitio
  (`ameriflux.lbl.gov/sites/siteinfo/<ID>`). Leí 27 páginas, las de los sitios agrícolas con datos y algunos
  más. **El cultivo de cada año está en los metadatos BADM** (`GRP_CROP` y similares), pero esos archivos
  solo se bajan con cuenta y no los bajé. Donde la descripción no da el año, la tabla dice "sin dato".

Consulta hecha el 2026-11-15. Los años publicados cambian con cada versión de BASE y FLUXNET.

### 2. Todos los sitios encontrados

Las columnas BASE y FLUXNET-1F dan el primer y el último año publicado. "—" quiere decir que no hay nada
publicado. La política es la de la página del sitio.

| Sitio | Nombre | Estado | IGBP | Lat, lon | fips (condado) | Torre (inicio–fin) | BASE | FLUXNET-1F | Política |
|---|---|---|---|---|---|---|---|---|---|
| US-Br1 | Brooks Field Site 10- Ames | IA | CRO | 41.9749, -93.6906 | 19169 (Story) | 2001–2025 | 2005–2011 | — | Legacy |
| US-Br2 | Brooks Field Site 1011- Ames | IA | CRO | 41.9757, -93.6925 | 19169 (Story) | 2005–2025 | — | — | — |
| US-Br3 | Brooks Field Site 11- Ames | IA | CRO | 41.9747, -93.6936 | 19169 (Story) | 2001–2025 | 2005–2011 | — | Legacy |
| US-CLN | Coles Farm North | IA | CRO | 42.4886, -93.5227 | 19079 (Hamilton) | 2016– | 2021–2023 | — | Legacy |
| US-CLS | Coles Farm South | IA | CRO | 42.4826, -93.5249 | 19079 (Hamilton) | 2016– | 2025–2025 | — | Legacy |
| US-IAA | Iowa State University NW tower | IA | CRO | 42.0004, -93.7068 | 19015 (Boone) | 2019– | — | — | — |
| US-IAB | Iowa State University NE tower | IA | CRO | 42.0001, -93.7016 | 19015 (Boone) | 2019– | 2019–2024 | 2019–2024 | CC-BY-4.0 |
| US-IAC | Iowa State University SE tower | IA | CRO | 41.9984, -93.7016 | 19015 (Boone) | 2019– | 2019–2024 | 2019–2024 | CC-BY-4.0 |
| US-IAM | Iowa State University Miscanthus | IA | CRO | 41.9994, -93.7042 | 19015 (Boone) | 2019– | 2019–2024 | 2019–2024 | CC-BY-4.0 |
| US-NPR | Neil Smith Prairie | IA | GRA | 41.5586, -93.2929 | 19099 (Jasper) | 2004– | — | — | — |
| US-AMS | Argonne Testbed for Multiscale Observational Science (ATMOS) | IL | GRA | 41.7018, -87.9963 | 17043 (DuPage) | 2021– | 2022–2023 | — | CC-BY-4.0 |
| US-Bo1 | Bondville | IL | CRO | 40.0062, -88.2904 | 17019 (Champaign) | 1996– | 1996–2008 | — | CC-BY-4.0 |
| US-Bo2 | Bondville (companion site) | IL | CRO | 40.0090, -88.2900 | 17019 (Champaign) | 2004–2008 | 2004–2008 | — | CC-BY-4.0 |
| US-IB1 | Fermi National Accelerator Laboratory- Batavia (Agricultural site) | IL | CRO | 41.8593, -88.2227 | 17043 (DuPage) | 2005– | 2005–2018 | — | CC-BY-4.0 |
| US-IB2 | Fermi National Accelerator Laboratory- Batavia (Prairie site) | IL | GRA | 41.8406, -88.2410 | 17043 (DuPage) | 2004– | 2004–2018 | — | CC-BY-4.0 |
| US-IS1 | Illinois SmartFarm - Pesotum Eddy Covariance Site | IL | CRO | 39.8900, -88.2100 | 17019 (Champaign) | 2021– | — | — | — |
| US-IS2 | Illinois SmartFarm - Villa Grove Eddy Covariance Site | IL | CRO | 39.8800, -88.1500 | 17019 (Champaign) | 2021– | — | — | — |
| US-IS3 | Illinois SmartFarm - Bondville Eddy Covariance Site | IL | CRO | 40.0100, -88.2900 | 17019 (Champaign) | 2020– | — | — | — |
| US-UiA | University of Illinois Switchgrass | IL | CRO | 40.0646, -88.1961 | 17019 (Champaign) | 2008– | 2008–2024 | 2008–2024 | CC-BY-4.0 |
| US-UiB | University of Illinois Miscanthus | IL | CRO | 40.0628, -88.1984 | 17019 (Champaign) | 2008– | 2008–2024 | 2008–2024 | CC-BY-4.0 |
| US-UiC | University of Illinois Maize-Soy | IL | CRO | 40.0628, -88.1961 | 17019 (Champaign) | 2008– | 2008–2024 | 2008–2024 | CC-BY-4.0 |
| US-UiD | University of Illinois Restored Native Prairie | IL | GRA | 40.0646, -88.1985 | 17019 (Champaign) | 2008– | 2008–2024 | 2008–2024 | CC-BY-4.0 |
| US-UiE | University of Illinois Sorghum-Soy | IL | CRO | 40.0629, -88.2033 | 17019 (Champaign) | 2018– | 2018–2024 | 2018–2024 | CC-BY-4.0 |
| US-UiF | University of Illinois Miscanthus 2 | IL | CRO | 40.0665, -88.2015 | 17019 (Champaign) | 2017– | 2018–2023 | 2018–2023 | CC-BY-4.0 |
| US-UiG | University of Illinois Maize-Soy 2 | IL | CRO | 40.0629, -88.2009 | 17019 (Champaign) | 2017– | 2018–2023 | 2018–2023 | CC-BY-4.0 |
| US-ZF1 | Zumwalt Farm Treatment | IL | CRO | 40.7976, -87.5355 | 17075 (Iroquois) | 2024– | 2024–2026 | 2024–2025 | CC-BY-4.0 |
| US-ZF2 | Zumwalt Farm Control | IL | CRO | 40.7939, -87.5355 | 17075 (Iroquois) | 2024– | 2024–2026 | 2024–2025 | CC-BY-4.0 |
| US-BRG | Bayles Road Grassland Tower | IN | GRA | 39.2167, -86.5406 | 18105 (Monroe) | 2016–2021 | 2016–2020 | 2017–2020 | CC-BY-4.0 |
| US-INd | INFLUX - Agricultural Site East near Pittsboro | IN | CRO | 39.8645, -86.5005 | 18063 (Hendricks) | 2017–2018 | 2017–2018 | — | CC-BY-4.0 |
| US-INe | INFLUX - Agricultural Site West near Pittsboro | IN | CRO | 39.8632, -86.5083 | 18063 (Hendricks) | 2017–2019 | 2017–2019 | — | CC-BY-4.0 |
| US-INi | INFLUX - Agricultural Site East of Indianapolis (Site-9a) | IN | CRO | 39.8167, -85.7005 | 18059 (Hancock) | 2019–2022 | 2019–2022 | — | CC-BY-4.0 |
| US-INj | INFLUX - Agricultural Site East of Indianapolis (Site-9b) | IN | CRO | 39.8766, -85.7066 | 18059 (Hancock) | 2020– | 2020–2023 | — | CC-BY-4.0 |
| US-INn | INFLUX - Agricultural Site West of Indianapolis (Site-14a) | IN | CRO | 39.9468, -86.7880 | 18107 (Montgomery) | 2019–2021 | 2019–2021 | — | CC-BY-4.0 |
| US-INp | INFLUX - Agricultural Site West of Indianapolis (Site-14b) | IN | CRO | 39.9477, -86.7821 | 18107 (Montgomery) | 2021–2021 | 2020–2021 | — | CC-BY-4.0 |
| US-OK1 | ECB: Site A1 - North Field | IN | CRO | 41.5348, -84.8068 | 18151 (Steuben) | 2020– | — | — | — |
| US-OK2 | ECB: Site A3 - South Field | IN | CRO | 41.7660, -111.8550 | 49005 (Cache) | 2020– | — | — | — |
| US-SD1 | Shatto Ditch Paired Cropland - Site 1 (Corn/Soy; No Cover Crops) | IN | CRO | 41.2048, -86.0296 | 18085 (Kosciusko) | 2023– | 2023–2025 | 2023–2025 | CC-BY-4.0 |
| US-SD2 | Shatto Ditch Paired Cropland - Site 2 (Corn/Soy; Cover Crops) | IN | CRO | 41.1785, -85.9977 | 18085 (Kosciusko) | 2023– | 2023–2025 | 2023–2025 | CC-BY-4.0 |
| US-VT1 | Vermillion Tributary Paired Cropland – Site 1 (Corn/Soy; No Cover Crops) | IN | CRO | 40.4064, -87.5214 | 18171 (Warren) | 2023– | 2023–2025 | 2023–2025 | CC-BY-4.0 |
| US-VT2 | Vermillion Tributary Paired Cropland – Site 2 (Corn/Soy; Cover Crops) | IN | CRO | 40.4018, -87.5213 | 18171 (Warren) | 2023– | 2023–2025 | 2023–2025 | CC-BY-4.0 |
| US-A31 | ARM-SGP-Anthony | KS | GRA | 37.1509, -98.3620 | 20007 (Barber) | 2019– | — | — | — |
| US-KFB | Konza Prairie LTER (4B) | KS | GRA | 39.0745, -96.5951 | 20161 (Riley) | 2006– | — | — | — |
| US-KFS | Kansas Field Station | KS | GRA | 39.0561, -95.1907 | 20087 (Jefferson) | 2007– | 2007–2019 | 2007–2019 | CC-BY-4.0 |
| US-KLS | Kansas Land Institute | KS | GRA | 38.7745, -97.5684 | 20169 (Saline) | 2012– | 2012–2019 | 2012–2019 | CC-BY-4.0 |
| US-Kon | Konza Prairie LTER (KNZ) | KS | GRA | 39.0824, -96.5603 | 20161 (Riley) | 2006– | 2004–2019 | 2004–2019 | CC-BY-4.0 |
| US-Wlr | Walnut River Watershed (Smileyburg) | KS | GRA | 37.5208, -96.8550 | 20015 (Butler) | 2001–2004 | 2001–2004 | — | CC-BY-4.0 |
| US-xKA | NEON Konza Prairie Biological Station - Relocatable (KONA) | KS | GRA | 39.1104, -96.6129 | 20161 (Riley) | 2017– | 2017–2024 | 2019–2024 | CC-BY-4.0 |
| US-xKZ | NEON Konza Prairie Biological Station (KONZ) | KS | GRA | 39.1008, -96.5631 | 20161 (Riley) | 2017– | 2017–2024 | 2019–2024 | CC-BY-4.0 |
| US-KCM | KCMP Tall Tower | MN | CRO | 44.6886, -93.0728 | 27037 (Dakota) | 2007– | — | — | — |
| US-KUT | KUOM Turfgrass Field | MN | GRA | 44.9950, -93.1863 | 27123 (Ramsey) | 2005–2009 | 2005–2009 | — | CC-BY-4.0 |
| US-MDE | Morris Dairy East | MN | CRO | 45.4954, -96.0198 | 27149 (Stevens) | 2008–2016 | — | — | — |
| US-MDS | Morris Dairy Southeast | MN | CRO | 45.4883, -95.9993 | 27149 (Stevens) | 2011–2016 | — | — | — |
| US-MDW | Morris Dairy West | MN | CRO | 45.4953, -96.0300 | 27149 (Stevens) | 2008–2016 | — | — | — |
| US-MN1 | Morris: Corn-Soybean with Cover Crops, Strip Tillage | MN | CRO | 45.6168, -96.1269 | 27149 (Stevens) | 2017– | 2017–2024 | 2017–2024 | CC-BY-4.0 |
| US-MN2 | Morris: Corn-Soybean-Wheat with Cover Crops, Minimal Tillage | MN | CRO | 45.6270, -96.1271 | 27149 (Stevens) | 2017– | 2017–2024 | 2017–2024 | CC-BY-4.0 |
| US-MN3 | Morris: Corn-Soybean, Conventional Tillage | MN | CRO | 45.6091, -96.1265 | 27149 (Stevens) | 2020– | 2020–2024 | 2020–2024 | CC-BY-4.0 |
| US-RSI | Rosemount I10 Field | MN | CRO | 44.7059, -93.0673 | 27037 (Dakota) | 2020– | — | — | — |
| US-RSV | Rosemount V8 Field | MN | CRO | 44.7158, -93.0755 | 27037 (Dakota) | 2020– | — | — | — |
| US-Ro1 | Rosemount- G21 | MN | CRO | 44.7143, -93.0898 | 27037 (Dakota) | 2003–2017 | 2004–2016 | 2004–2016 | CC-BY-4.0 |
| US-Ro2 | Rosemount- C7 | MN | CRO | 44.7288, -93.0888 | 27037 (Dakota) | 2003–2017 | 2008–2016 | 2008–2016 | CC-BY-4.0 |
| US-Ro3 | Rosemount- G19 | MN | CRO | 44.7217, -93.0893 | 27037 (Dakota) | 2003–2010 | 2004–2007 | 2004–2007 | CC-BY-4.0 |
| US-Ro4 | Rosemount Prairie | MN | GRA | 44.6781, -93.0723 | 27037 (Dakota) | 2014– | 2014–2026 | 2014–2025 | CC-BY-4.0 |
| US-Ro5 | Rosemount I18_South | MN | CRO | 44.6910, -93.0576 | 27037 (Dakota) | 2017– | 2017–2026 | 2017–2024 | CC-BY-4.0 |
| US-Ro6 | Rosemount I18_North | MN | CRO | 44.6946, -93.0578 | 27037 (Dakota) | 2017– | 2017–2026 | 2017–2024 | CC-BY-4.0 |
| US-Ne1 | Mead - irrigated continuous maize site | NE | CRO | 41.1651, -96.4766 | 31155 (Saunders) | 2001– | 2001–2025 | 2001–2024 | CC-BY-4.0 |
| US-Ne2 | Mead - irrigated maize-soybean rotation site | NE | CRO | 41.1649, -96.4701 | 31155 (Saunders) | 2001– | 2001–2025 | 2001–2024 | CC-BY-4.0 |
| US-Ne3 | Mead - rainfed maize-soybean rotation site | NE | CRO | 41.1797, -96.4397 | 31155 (Saunders) | 2001– | 2001–2025 | 2001–2024 | CC-BY-4.0 |
| US-SdH | Nebraska SandHills Dry Valley | NE | GRA | 42.0693, -101.4072 | 31091 (Hooker) | 2004– | 2004–2009 | — | CC-BY-4.0 |
| US-CRT | Curtice Walter-Berger cropland | OH | CRO | 41.6285, -83.3471 | 39095 (Lucas) | 2011–2013 | 2011–2013 | 2011–2013 | CC-BY-4.0 |
| US-Mi1 | LTAR UCB (Upper Chesapeake Bay) Miscanthus 1 | OH | CVM | 41.7727, -80.6313 | 39007 (Ashtabula) | 2015–2019 | 2015–2019 | — | CC-BY-4.0 |
| US-Mi2 | LTAR UCB (Upper Chesapeake Bay) Miscanthus 2 | OH | CVM | 41.5479, -80.8550 | 39007 (Ashtabula) | 2015–2017 | 2015–2017 | — | CC-BY-4.0 |
| US-Mi3 | LTAR UCB (Upper Chesapeake Bay) Miscanthus 3 | OH | CVM | 41.8222, -80.6370 | 39007 (Ashtabula) | 2015–2019 | 2015–2019 | — | CC-BY-4.0 |

Observaciones sobre la tabla:

- **US-OK2** figura en Indiana, pero sus coordenadas (41,766, −111,855) caen en Cache County, Utah (49005). Es
  un error en los metadatos de AmeriFlux. No tiene datos publicados.
- **US-Mi1, US-Mi2 y US-Mi3** se llaman "LTAR UCB (Upper Chesapeake Bay)", pero están cargados en Ohio y sus
  coordenadas caen en Ashtabula (39007). Son de miscanthus (CVM) y solo tienen BASE. No sirven para maíz y
  soja.
- **US-KCM** es una torre alta (240 m) de concentraciones en un paisaje agrícola: no mide el flujo de un lote.
  **US-AMS**, **US-IB2**, **US-KUT** y los sitios de Konza son de pastizal, pradera o césped.
- **Los sitios INFLUX de Indiana** (US-INd a US-INp) miden CO₂ para un estudio urbano y tienen pocos años de
  BASE. En la página de US-INe figuran H y H2O como medidos.

### 3. Sitios agrícolas con datos: cultivo, manejo y variables

"FLX" es FLUXNET-1F, versión `v1.3_r1`. La versión de BASE es la que figura en la cita de la página del sitio.
Los gases medidos se copiaron del campo "Flux Species Measured" de cada página.

| Sitio | fips | Años BASE / FLX | Versión BASE | Cultivo y manejo (de la descripción del sitio) | Gases medidos | Riego |
|---|---|---|---|---|---|---|
| US-Ne1 | 31155 | 2001–2025 / 2001–2024 | 20-5 | Maíz continuo desde 2001. Sin labranza hasta la cosecha de 2005, después labranza conservacionista hasta 2022. Desde 2022, maíz-soja sin labranza (maíz en años impares, soja en pares) | CO2 (la página no lista H2O, pero FLUXNET-1F trae LE) | Sí, pivote |
| US-Ne2 | 31155 | 2001–2025 / 2001–2024 | 20-5 | Maíz-soja sin labranza (maíz en años impares, soja en pares). En 2010 y 2012 hubo maíz en lugar de soja, con labranza de otoño (2010–2013). Volvió a la rotación sin labranza después de 2014 | CO2 (ídem) | Sí, pivote |
| US-Ne3 | 31155 | 2001–2025 / 2001–2024 | 20-5 | Maíz-soja estricto sin labranza desde 2001: maíz en años impares, soja en pares | CO2 (ídem) | No |
| US-Bo1 | 17019 | 1996–2008 / — | 2-1 | Sin labranza desde 1986, maíz y soja en años alternos: maíz en 2005 y 2007, soja en 2006 y 2008. Los años anteriores no figuran | CO2 | No dice |
| US-Br1 | 19169 | 2005–2011 / — (Legacy) | 1-1 | Maíz-soja típico del centro de Iowa. No da el cultivo por año | CO2 | No dice |
| US-Br3 | 19169 | 2005–2011 / — (Legacy) | 1-1 | Ídem US-Br1 | CO2 | No dice |
| US-CLN | 19079 | 2021–2023 / — (Legacy) | 1-5 | Maíz-soja. Labranza convencional hasta 2015; desde 2016, labranza en franjas y cultivos de cobertura | CO2, H, H2O | No dice |
| US-IAB | 19015 | 2019–2024 / 2019–2024 | 1-5 | Rotación de cultivos en un lote de 4 ha (granja SABR, ISU). No da el cultivo por año | CO2, H, H2O | No dice |
| US-IAC | 19015 | 2019–2024 / 2019–2024 | 1-5 | Sorgo-maíz-soja, lote de 4 ha (SABR) | CO2, H, H2O | No dice |
| US-IB1 | 17043 | 2005–2018 / — | 8-5 | Maíz-soja (Fermilab) | CO2 | No dice |
| US-UiC | 17019 | 2008–2024 / 2008–2024 | 2-5 | Maíz-maíz-soja; la primera soja fue en 2010. Basalto aplicado desde 2017 (dato de la página de US-UiG). Siembra en mayo y cosecha en octubre | CO2, H, H2O | No dice |
| US-UiG | 17019 | 2018–2023 / 2018–2023 | 1-5 | Maíz-maíz-soja, control de US-UiC; la primera soja fue en 2019 | CO2, H, H2O | No dice |
| US-ZF1 / ZF2 | 17075 | 2024–2026 / 2024–2025 | 1-5 | La página no tiene descripción (tratamiento y control) | CO2, CH4, H2O, N2O | No dice |
| US-SD1 / SD2 | 18085 | 2023–2025 / 2023–2025 | 1-5 | Maíz-soja sin labranza en campos de productores. SD2 tiene cultivos de cobertura y suelo más arenoso | CO2, H, H2O | No dice |
| US-VT1 / VT2 | 18171 | 2023–2025 / 2023–2025 | 4-5 | Maíz-soja sin labranza en campos de productores. VT2 tiene cultivos de cobertura | CO2, H, H2O | No dice |
| US-INd…INp | 18063, 18059, 18107 | 2–4 años entre 2017 y 2023 / — | 1-5 | Agrícola, sin detalle | CO2, H, H2O (US-INe) | No dice |
| US-MN1 | 27149 | 2017–2024 / 2017–2024 | 2-5 | Maíz-soja, labranza en franjas, centeno de cobertura en invierno, drenaje con caños | CO2, H, H2O | No dice |
| US-MN2 | 27149 | 2017–2024 / 2017–2024 | 2-5 | Maíz-soja-trigo, cobertura de camelina y pennycress en invierno, labranza mínima, drenaje con caños | CO2, H, H2O | No dice |
| US-MN3 | 27149 | 2020–2024 / 2020–2024 | 2-5 | Maíz-soja con labranza convencional (dato del nombre del sitio; la página no tiene descripción) | CO2, H, H2O | No dice |
| US-Ro1 | 27037 | 2004–2016 / 2004–2016 | 5-5 | Maíz-soja, cincel en otoño tras el maíz y en primavera tras la soja | CO2, H, H2O | No dice |
| US-Ro2 | 27037 | 2008–2016 / 2008–2016 | 2-5 | Maíz-soja-trébol, con cincel | CO2, H, H2O | No dice |
| US-Ro3 | 27037 | 2004–2007 / 2004–2007 | 4-5 | Maíz-soja, con cincel | CO2, H, H2O | No dice |
| US-Ro5 | 27037 | 2017–2026 / 2017–2024 | 32-5 | Maíz-soja, con cincel (manejo típico de la región) | CO2, H, H2O | No dice |
| US-Ro6 | 27037 | 2017–2026 / 2017–2024 | 32-5 | Maíz-soja con trébol (mulch vivo o cobertura), con cincel | CO2, H, H2O | No dice |
| US-CRT | 39095 | 2011–2013 / 2011–2013 | 5-5 | Soja y trigo de invierno, secano, drenaje con caños (Great Black Swamp) | CO2, H, H2O, CH4 | No |

**Cultivo por año.** Solo los tres sitios de Mead (y US-Bo1 de 2005 a 2008) lo dan en la descripción. Para los
demás hay que leer el BADM que viene con cada descarga, o cruzar las coordenadas de la torre con el CDL de cada
año (`data/raw/cultivos/`), que ya tenemos. Esto segundo es una propuesta: no se hizo.

DOI de los datos de los sitios recomendados, copiados de su página (la cita completa, con autores, figura en
la página y en la descarga):

| Sitio | DOI BASE | DOI FLUXNET-1F |
|---|---|---|
| US-Ne1 | 10.17190/AMF/1246084 | 10.17190/AMF/1871140 |
| US-Ne2 | 10.17190/AMF/1246085 | 10.17190/AMF/2574638 |
| US-Ne3 | 10.17190/AMF/1246086 | 10.17190/AMF/3028954 |
| US-Ro1 | 10.17190/AMF/1246092 | 10.17190/AMF/1881588 |
| US-Ro2 | 10.17190/AMF/1418683 | 10.17190/AMF/2204876 |
| US-Ro5 | 10.17190/AMF/1419508 | 10.17190/AMF/1818371 |
| US-Ro6 | 10.17190/AMF/1419509 | 10.17190/AMF/1881590 |
| US-UiC | 10.17190/AMF/1846665 | 10.17190/AMF/3027338 |
| US-UiG | 10.17190/AMF/2574375 | 10.17190/AMF/3027352 |
| US-MN1 | 10.17190/AMF/2407204 | 10.17190/AMF/2571145 |
| US-MN2 | 10.17190/AMF/2407205 | 10.17190/AMF/2571146 |
| US-MN3 | 10.17190/AMF/2407206 | 10.17190/AMF/2571147 |
| US-IAB | 10.17190/AMF/2567982 | 10.17190/AMF/3027372 |
| US-IAC | 10.17190/AMF/2586672 | 10.17190/AMF/3027373 |
| US-Bo1 | 10.17190/AMF/1246036 | — |
| US-CRT | 10.17190/AMF/1246156 | 10.17190/AMF/2006974 |

### 4. Variables

Según la página del producto FULLSET de FLUXNET2015 (el producto AmeriFlux FLUXNET usa las mismas definiciones):

- `LE_F_MDS`: calor latente rellenado con el método MDS, en W/m². Viene en HH (semihorario), DD (media diaria
  de los semihorarios) y WW a YY (medias de los diarios). `LE_F_MDS_QC` es la calidad: en HH, 0 = medido,
  1 = buen relleno, 2 = medio y 3 = malo; en DD, la fracción de datos medidos o de relleno bueno.
- `LE_CORR`, `LE_CORR25` y `LE_CORR75`: LE con el balance de energía corregido.
- `H_F_MDS`: calor sensible, con el mismo esquema.
- `GPP_NT_VUT_REF`: GPP con la partición nocturna, en µmol CO₂/m²/s en HH.
- `TIMESTAMP` y `TIMESTAMP_START`/`_END`, en formato `YYYYMMDDHHMM`.

**ET en mm:** `ET_mm_dia = LE (W/m², media diaria) × 86 400 / λ`, con λ ≈ 2,45 × 10⁶ J/kg. Es la conversión
física estándar; no la saqué de una página de AmeriFlux. Conviene comparar con `LE_F_MDS` y con `LE_CORR`,
porque las torres suelen no cerrar el balance de energía y eso subestima la ET. Hay que documentar cuál se usa.

No verifiqué el contenido de los archivos de BASE de cada sitio (piden cuenta). Según la página de cada uno,
los sitios de Mead solo listan CO2 como especie medida, pero tienen FLUXNET-1F con LE.

### 5. Descarga y licencia

- **Cuenta:** hace falta una cuenta personal de AmeriFlux. El registro está en
  `https://ameriflux-data.lbl.gov/Pages/RequestAccount.aspx` (documentación de `amerifluxr`).
- **Al bajar:** el portal pide el uso previsto, que se manda a los responsables de cada sitio y se publica en
  el *AmeriFlux Data Download Log*.
- **Por programa:** el paquete de R `amerifluxr` (`amf_download_base()`, `amf_download_fluxnet()`,
  `amf_download_bif()`) pide `user_id`, `user_email`, `data_policy` (`"CCBY4.0"` o `"LEGACY"`),
  `agree_policy = TRUE`, `intended_use` (por ejemplo `"remote_sensing"` o `"synthesis"`) e
  `intended_use_text`. **Credenciales:** si se automatiza, el usuario y el mail van en `.env`, nunca en el
  repo.
- **CC-BY-4.0** (desde agosto de 2021, revisada en diciembre de 2025). Hay que citar el DOI de cada sitio en
  las referencias y poner en los agradecimientos "Funding for the AmeriFlux data service was provided by the
  U.S. Department of Energy Office of Science". Para FLUXNET hay un texto adicional sobre ONEFlux y ERA5. Si
  el trabajo tiene sección de disponibilidad de datos, va la fecha de acceso. Las citas del procesamiento son
  Chu et al. 2023 (BASE) y Pastorello et al. 2020 (FLUXNET).
- **Legacy:** antes de un análisis que lleve a una publicación, hay que contactar a los autores para
  ofrecerles participar como coautores, y avisarles antes de publicar. **Si un trabajo mezcla datos
  CC-BY-4.0 y Legacy, todo pasa a regirse por Legacy.** Por eso conviene dejar afuera US-Br1, US-Br3, US-CLN y
  US-CLS.
- **Redistribución:** la CC-BY-4.0 permite compartir y adaptar con atribución. Igual, por la regla 8 del
  CLAUDE.md, los datos de torre no van en git. Si se procesan, se publican en un Release con las citas.

### 6. Columnas nuestras que se pueden comparar

Las torres miden un lote de algunas hectáreas y nuestros CSV dan medias de condado sobre píxeles agrícolas.
La comparación sirve para **sesgo y estacionalidad**, no para validar píxel por píxel. Es más justa en
condados muy agrícolas y con un cultivo dominante.

| Torre (variable) | Nuestro CSV y columna | Cómo |
|---|---|---|
| ET de LE_F_MDS / LE_CORR, suma mensual | `vegetacion_mensual.csv`: `et_mm` (MOD16A2) | Mismo `fips` y `mes`, en mm/mes |
| Ídem | `nldas_mensual.csv`: `et_nldas_mm` | Ídem |
| ET diaria media del mes | `ecostress_mensual.csv`: `et_ecostress_mm_dia` (por ahora solo 2025-04 a 2025-10) | mm/día. Con FLUXNET hasta 2024 casi no se superponen; habría que usar BASE 2025 |
| ET / ETo | `clima_mensual.csv`: `eto_pm_mm` | Kc real de la torre contra el Kc de FAO-56 (es lo que pide T030) |
| ET / PET | `vegetacion_mensual.csv`: `et_pet_ratio`; `ecostress_mensual.csv`: `esi_ecostress` | Ratio |
| SWC_F_MDS (humedad del suelo) | `agua_mensual.csv`: `sm_surface_m3m3`, `sm_rootzone_m3m3`; `nldas_mensual.csv`: `sm_0_10cm_m3m3`; `clima_mensual.csv`: `gwettop` | No verifiqué qué sitios miden SWC |
| P_F, TA_F, SW_IN_F | `clima_mensual.csv`: `prec_power_mm`, `prec_imerg_mm`, `tmed_c`, `rad_mj_m2` | Control de forzantes |
| GPP_NT_VUT_REF | No tenemos GPP en los CSV. Sirve contra `ndvi` y `evi` de `vegetacion_mensual.csv`, o para un futuro MOD17 | — |

**Cuidado con el riego en Mead.** Ne1 y Ne2 se riegan y Saunders (31155) es mitad riego y mitad secano. Para
validar una media de condado, la que más se parece es Ne3, la de secano. Ne1 y Ne2 sirven si se usa la máscara
de riego de T004 o para ver el efecto del riego.

## Propuesta: qué sitios usar

1. **Núcleo (FLUXNET-1F, CC-BY-4.0, varios años de MODIS y NLDAS):** US-Ne3, US-Ne2 y US-Ne1 (31155),
   US-Ro1 y US-Ro5 (27037), US-UiC (17019), US-MN1 y US-MN3 (27149) y US-IAB (19015). Son 9 torres en 5
   condados de 4 estados, con 2001 a 2024 en Mead.
2. **Complementarios:** US-Ro2, US-Ro6 y US-MN2 (rotaciones con trébol, cobertura o trigo), US-UiG, US-IAC,
   US-SD1/SD2 y US-VT1/VT2 (Indiana, 2023–2025) y US-CRT (Ohio, soja y trigo, 2011–2013).
3. **Dejar afuera:** los sitios Legacy (US-Br1, US-Br3, US-CLN y US-CLS), para que todo quede en CC-BY-4.0; los
   de pastizal, pradera o miscanthus; US-KCM (torre alta); los INFLUX (pocos años y otro objetivo) y US-OK2
   (coordenadas erróneas).
4. **Kansas** queda sin validación de torre agrícola. Para el centro y el oeste de NE y KS, Mead es lo más
   cercano.

**Pasos que siguen (otra tarea, no hecha acá):** el humano crea la cuenta y baja FLUXNET-1F (archivos DD y
MM) de los sitios del núcleo, que van a `data/raw/ameriflux/`. Después se cruza el cultivo de cada año con el
BADM o con el CDL, se calcula la ET en mm desde LE y se arma una tabla `fips, mes, sitio, cultivo,
et_torre_mm` para compararla con `et_mm`, `et_nldas_mm` y `et_ecostress_mm_dia`. No sé cuánto pesan los
archivos; el FULLSET semihorario de 24 años puede ser grande, así que conviene pedir solo DD y MM si el portal
lo permite.

## Fuentes

- [AmeriFlux API: site_display](https://amfcdn.lbl.gov/api/v1/site_display/AmeriFlux), consultado 2026-11-15
- [AmeriFlux API: data_availability BASE-BADM CCBY4.0](https://amfcdn.lbl.gov/api/v1/data_availability/AmeriFlux/BASE-BADM/CCBY4.0), [LEGACY](https://amfcdn.lbl.gov/api/v1/data_availability/AmeriFlux/BASE-BADM/LEGACY) y [FLUXNET CCBY4.0](https://amfcdn.lbl.gov/api/v1/data_availability/AmeriFlux/FLUXNET/CCBY4.0), consultados 2026-11-15
- Páginas de los sitios, `https://ameriflux.lbl.gov/sites/siteinfo/<ID>`, para US-Ne1, Ne2, Ne3, Bo1, Br1, Br3, CLN, IAB, IAC, IB1, UiC, UiG, ZF1, INe, SD1, VT1, MN1, MN2, MN3, Ro1, Ro2, Ro3, Ro5, Ro6, CRT, KCM y MDW (por ejemplo, [US-Ne1](https://ameriflux.lbl.gov/sites/siteinfo/US-Ne1)), consultadas 2026-11-15
- [AmeriFlux Data Policy](https://ameriflux.lbl.gov/data/data-policy/), consultado 2026-11-15
- [amerifluxr: amf_download_base](https://chuhousen.github.io/amerifluxr/reference/amf_download_base.html), consultado 2026-11-15
- [FLUXNET2015 FULLSET Data Product](https://fluxnet.org/data/fluxnet2015-dataset/fullset-data-product/), consultado 2026-11-15
- [Census Geocoder, geographies/coordinates](https://geocoding.geo.census.gov/geocoder/geographies/coordinates), consultado 2026-11-15
- No pude leer [Download Data](https://ameriflux.lbl.gov/data/download-data/) ni [Data Variables](https://ameriflux.lbl.gov/data/aboutdata/data-variables/): el contenido se arma con JavaScript y el HTML vino vacío.

Confianza: **alta** para la lista de sitios, los años publicados, la política, los DOI y el `fips` (salen de
la API y del Census). **Media** para el cultivo y el manejo, que salen de descripciones libres y no del BADM.
**Media** para las variables, que salen de la documentación de FLUXNET2015 y no de los archivos.

Impacto: no cambia `config/` ni ningún paquete existente. Habilita una tarea nueva de validación (bajar
FLUXNET-1F de los sitios del núcleo y compararlos con `vegetacion`, `nldas`, `ecostress` y `clima`), que
completa lo pendiente de `docs/research/agua_por_cultivo.md` (§4 y Fuentes).
