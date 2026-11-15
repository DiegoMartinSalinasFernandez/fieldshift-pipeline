# Eventos extremos 2000–2025 en los 7 estados (control de calidad)

Pregunta: ¿Qué eventos climáticos movieron el rendimiento o la siembra de maíz, soja y trigo de invierno en IA,
IL, IN, OH, NE, MN y KS entre 2000 y 2025? Para cada uno: estados y condados afectados, meses, efecto en el
rendimiento del estado y en qué variable de nuestros CSV debería verse. Sirve para la tarea T007 (control de
calidad) y para que ML entienda los años raros.

Respuesta corta:

| Año | Evento | Estados | Meses | Efecto conocido | Dónde mirar en nuestros CSV |
|---|---|---|---|---|---|
| 2002 | Sequía en las Grandes Llanuras | NE, KS (sobre todo secano) | jun–ago | NE maíz de secano 60 bu/ac (84 en 2000) | `spi3` y `deficit_mm` jun–ago; `rend_bu_ac` de NE/KS |
| 2005 | Sequía en Illinois (norte) | IL | may–ago | IL maíz 145 bu/ac proyectado (180 en 2004) | `spi3`, `prec_temporada_mm` en el norte de IL |
| 2008 | Inundaciones de junio | IA (y partes de IL, IN) | jun | 83 de 99 condados de IA con emergencia | `prec_max5d_mm`, `dias_lluvia_gt50` jun; `ratio_cosechada` |
| 2011 | Inundación del río Missouri | IA oeste, NE este (KS, MO) | jun–sep | ~255.000 acres de cultivo dañados en IA | `ratio_cosechada` en condados ribereños; `frac_pixeles_validos`/CDL agua |
| 2011 | Helada temprana | MN | sep (mediados) | soja −10 %; hasta 25 % del maíz con −10 % (estimación) | `doy_primera_helada` temprano en MN |
| 2012 | Sequía y calor | los 7 (peor IL, IN, KS) | jun–ago | maíz IN 99, IL 105, IA 137, KS 96 bu/ac | `spi3` muy negativo jul; `dias_tmax_gt35`, `tmax_jul_c`, `vhi`, `ndvi_anom_z` |
| 2013 | Primavera muy húmeda y fría | IA, MN | abr–jun | siembra atrasada; abril más lluvioso en IA | `prec_*` abr–may altos; `doy_50_sembrado` tardío |
| 2014 | Sequía y helada en el trigo | KS | invierno–may | trigo de invierno KS 28 bu/ac, el más bajo desde 1995 | `prec_invierno_previo_mm` bajo; `rend_bu_ac` trigo KS |
| 2019 | Inundación de marzo (bomb cyclone) | NE, IA oeste | mar | 81 de 93 condados de NE y 56 de IA con declaración federal | `prec_*` mar; `sm_rootzone_anom_z` alto |
| 2019 | Primavera húmeda y siembra prevenida récord | OH, IL, IN (y el resto) | abr–jun | OH 1,49 M acres prevenidos, IL 1,50 M, IN 0,94 M | `prec_temporada_mm` alto, `doy_50_sembrado` tardío, `sup_sembrada_ac` baja |
| 2020 | Derecho | IA (centro y este), IL | 10 de ago | 57 condados de IA en la trayectoria, 36 los más golpeados | `ndvi_anom_z` ago–sep; `rend_bu_ac` por condado; no se ve en clima |
| 2022 | Sequía en el oeste | NE, KS | jun–sep | maíz NE −25 y KS −21 bu/ac respecto de la tendencia | `spi3`/`spi6` jul–ago; `deficit_temporada_mm` |
| 2023 | Sequía relámpago de junio | IA, MN, IL | may–jun | IL 206 bu/ac (sobre tendencia); MN ~6 % bajo tendencia | `spi1` jun muy negativo; rendimiento normal en IL: no confundir con error |

Lo que **no** encontré con fuente: lista de granizadas grandes con efecto en el rendimiento estatal (el granizo es
local y no mueve el promedio del estado); heladas tardías de primavera con efecto estatal; la tormenta de nieve de
abril de 2017 en el oeste de KS (no llegué a buscarla); rendimientos estatales finales de NE, OH y MN en 2012 y de
NE y KS en 2022 (solo desvíos respecto de la tendencia). Esos números salen del script de abajo.

Detalle:

**Cómo se consiguieron los números.** La base completa de Quick Stats no se pudo bajar desde esta máquina (el índice
`https://www.nass.usda.gov/datasets/` devolvió 404 el 2026-11-15) y no hay `NASS_API_KEY`. Las cifras de
rendimiento de este documento vienen de las fuentes citadas, no de NASS directo. Para el control de calidad
(T007), en una máquina que ya tenga `data/raw/cultivos/nass/qs.crops_*.txt.gz`, correr:

```
.venv/bin/python -X utf8 docs/research/eventos_extremos_rend_estado.py > /tmp/rend_estado.csv
```

Da el rendimiento de nivel estado de maíz para grano, soja y trigo de invierno, 2000–2025, con el promedio de los
5 años anteriores y la diferencia en %. Es solo una referencia para encontrar años raros: **no** es una tendencia ni
se usa en los CSV (la tendencia la decide ML). El script se probó con un archivo sintético, no con el real.

**Cómo se usa para control de calidad.** Si un CSV procesado *no* muestra la señal esperada en el año y los meses
del evento (por ejemplo, `spi3` de julio de 2012 cerca de 0 en Illinois), hay que revisar el proceso. Al revés, un
valor extremo en un año sin evento listado no es necesariamente un error, pero conviene mirarlo.

**Advertencia para ML.** Algunos eventos no aparecen en ninguna variable climática: el derecho de 2020 es viento
(no hay viento a 10 m de ráfagas en nuestros CSV; `WS2M` de POWER es media diaria) y las inundaciones de ríos
(2008, 2011, 2019) dependen del caudal, no de la lluvia local. Otros mezclan riego y secano: en NE y KS el
rendimiento `ALL PRODUCTION PRACTICES` amortigua la sequía (2002, 2012, 2022) porque el maíz regado casi no cae
(en NE 2012: 190 bu/ac regado vs 59 secano). Y 2023 tuvo sequía fuerte en junio pero rendimiento récord en IL:
una sequía temprana no implica mal rendimiento.

### 2002 — Sequía en las Grandes Llanuras

| Campo | Valor |
|---|---|
| Estados | NE (casi todo el estado en sequía severa a excepcional), KS (2/3 en sequía moderada a excepcional) |
| Condados | no hay lista; el oeste de KS (Hays, Colby) tuvo ensayos de secano abandonados |
| Meses | verano (los informes de NOAA de ago y sep de 2002) |
| Rendimiento | NE maíz de secano: 60 bu/ac (84 en 2000, −29 %). Rendimiento total del estado: falta (script) |
| Variables | `spi3`, `spi6`, `deficit_mm` jun–ago; `prec_temporada_mm` bajo; diferencia grande entre condados regados y de secano |
| Fuentes | UNL CropWatch, "What 2002, 2009 and 2012 Yields Tell Us About Drought Years"; K-State, "Drought.pdf"; NOAA NCEI, U.S. Drought Highlights ago 2002 |

### 2005 — Sequía en Illinois

| Campo | Valor |
|---|---|
| Estados | IL (sobre todo el norte) |
| Condados | Kane, LaSalle y Will con pérdidas proyectadas de 60–80 % a mitad de temporada (proyección, no cosecha); distrito noreste con la caída mayor (−55 bu/ac vs 2004) |
| Meses | primavera y verano |
| Rendimiento | IL maíz 145 bu/ac proyectado en nov 2005 (180 en 2004). Un artículo de Changnon dice que el rendimiento estatal fue "sobre el promedio": las fuentes no coinciden, verificar con el script |
| Variables | `spi3` y `prec_temporada_mm` en el norte de IL; `rend_bu_ac` por condado |
| Fuentes | farmdoc, "How bad were 2005 corn yields"; Illinois State Academy of Science (Changnon); MRCC climate summaries |

### 2008 — Inundaciones de junio en Iowa

| Campo | Valor |
|---|---|
| Estados | IA (el más afectado); también IL e IN por el Mississippi y sus afluentes |
| Condados | 83 de 99 condados de IA con proclamación de desastre del gobernador; 70 con declaración presidencial (fines de junio). Cedar Rapids (Linn) es el caso conocido |
| Meses | junio |
| Rendimiento | estimaciones tempranas: 1,3 M acres de maíz y 2 M de soja perdidos en IA (Farm Bureau); Chicago Fed: 2–3 M acres de maíz inundados. Rendimiento estatal: falta (script) |
| Variables | `prec_max5d_mm`, `dias_lluvia_gt50` en jun; `sm_rootzone` no existe (SMAP desde 2015); `ratio_cosechada` y `sup_cosechada_ac` en condados ribereños |
| Fuentes | Chicago Fed, Midwest Economy Blog 2008; CRS RL34583 (jul 2008); NOAA NCEI Global Hazards jun 2008 |

### 2011 — Inundación del río Missouri

| Campo | Valor |
|---|---|
| Estados | IA (oeste), NE (este), KS y MO |
| Condados | NE: 14 condados con pérdidas (estudio del Nebraska Farm Bureau), Burt con 20.000 acres afectados. IA: condados sobre el río Missouri; la lista está en el informe de HSEMD, que no abrí entero |
| Meses | junio a septiembre (más de 100 días) |
| Rendimiento | IA: 255.000 acres de cultivo dañados (HSEMD) o 233.269 acres (Decision Innovation Solutions); NE: USD 105 M de pérdidas en cultivos. No mueve el promedio estatal |
| Variables | no se ve en la lluvia local (el agua viene de aguas arriba). Mirar `ratio_cosechada` y la clase agua/no cultivo del CDL en esos condados |
| Fuentes | Iowa HSEMD, After Action Report Missouri River 2011; Decision Innovation Solutions, Missouri River flooding; Insurance Journal, 2011-12-15 y 2012-10-22 |

### 2011 — Helada temprana en Minnesota

| Campo | Valor |
|---|---|
| Estados | MN |
| Condados | todo el estado (sin lista) |
| Meses | mediados de septiembre |
| Rendimiento | estimación de un agrónomo: soja −10 %; hasta 25 % del maíz con −10 %. No es dato de NASS |
| Variables | `doy_primera_helada` más temprano de lo normal; `dias_tmin_le0` en sep |
| Fuentes | Star Tribune, "Early frosty grip on crops" |

### 2012 — Sequía y calor

| Campo | Valor |
|---|---|
| Estados | los 7; los rendimientos más bajos respecto de la tendencia en IN e IL (farmdoc) |
| Condados | todo el Corn Belt; UNL CropWatch tiene rendimientos por condado de NE |
| Meses | junio a agosto; julio es el mes clave (floración) |
| Rendimiento (maíz) | IN 99 bu/ac (146 en 2011, NASS Indiana); IL 105 (157 en 2011, State Climatologist); IA 137 (172), KS 96 (107) (KBIA); NE regado 190 y secano 59 (UNL). EE.UU. 123,4 (147,2 en 2011, NASS). Soja KS 23 bu/ac (DTN, citando USDA) |
| Variables | `spi3` y `spi1` muy negativos en jul; `dias_tmax_gt35`, `tmax_jul_c`, `deficit_temporada_mm`; `vhi` bajo y `ndvi_anom_z` negativo en jul–ago; `gwetroot` bajo |
| Fuentes | NASS Indiana Annual Statistical Bulletin 2012-13 p. 26; NASS, Crop Production 2012 Summary (2013-01-11); Illinois State Climatologist; KBIA 2013-01-15; UNL CropWatch 2013-06-28; farmdoc daily, "Locating the 2012 drought" |

### 2013 — Primavera muy húmeda y fría

| Campo | Valor |
|---|---|
| Estados | IA, MN (también el resto del Corn Belt) |
| Condados | Howard (IA): 44.446 de 252.000 acres en siembra prevenida (FSA local) |
| Meses | abril a junio |
| Rendimiento | sin caída grande a nivel estado según la prensa; no encontré el récord nacional de siembra prevenida de 2013 |
| Variables | `prec_imerg_mm` y `prec_power_mm` de abr–may altos (abril más lluvioso registrado en IA, MRCC); `doy_50_sembrado` tardío en `fenologia_estado.csv` |
| Fuentes | Christian Science Monitor 2013-07-05; Iowa State University News 2013-05-07; MRCC climate summaries; MPR News 2013-05-10 |

### 2014 — Trigo de invierno de Kansas (sequía y helada)

| Campo | Valor |
|---|---|
| Estados | KS |
| Condados | oeste y suroeste de KS |
| Meses | invierno 2013–14 a mayo; helada a mediados de abril |
| Rendimiento | trigo de invierno 28 bu/ac (38 en 2013), el más bajo desde 1995; producción 246,4 M bu, la menor desde 1989 (resumen anual de USDA citado por la prensa) |
| Variables | `prec_invierno_previo_mm` bajo; `dias_tmin_le_m2` en abr; `rend_bu_ac` de trigo de invierno en KS |
| Fuentes | Tonganoxie Mirror 2014-10-01 ("Report: Kansas wheat production lowest since 1989"); Washington Times / AP 2014-05-09 |

### 2019 — Inundación de marzo (bomb cyclone)

| Campo | Valor |
|---|---|
| Estados | NE, IA (oeste) |
| Condados | declaración federal en 81 de 93 condados de NE y 56 de 99 de IA (NWS Omaha, AMS 2020) |
| Meses | marzo (lluvia sobre nieve y suelo helado) |
| Rendimiento | NE: USD 440 M en cultivos y USD 400 M en ganado (estimación estatal). Más de 1 M de acres inundados en 9 estados (Reuters, satélite) |
| Variables | `prec_*` de mar; `sm_rootzone_anom_z` y `sm_surface` altos en mar–abr (SMAP); lluvia de invierno previo alta |
| Fuentes | NPR 2019-03-19 y 2019-03-21; Zapotocny, NWS Omaha, AMS 2020 (handout) |

### 2019 — Primavera húmeda y siembra prevenida récord

| Campo | Valor |
|---|---|
| Estados | OH, IL, IN los más afectados entre los nuestros; también los demás |
| Condados | sin lista; el dato por condado está en FSA (crop acreage data) |
| Meses | abril a junio (se extendió el plazo de declaración de superficie al 22 de julio en IL, IN y OH) |
| Siembra prevenida (FSA, ago 2019) | OH 1.485.919 acres; IL 1.501.731; IN 944.215. EE.UU. 19,3 M (récord desde 2007) |
| Variables | `prec_temporada_mm` alto; `prec_*` de may; `doy_50_sembrado` muy tardío; `sup_sembrada_ac` baja; `sm_rootzone_anom_z` alto en may |
| Fuentes | OSU Extension Henry County, "Prevented Planting Acres Announced For 2019"; DTN 2019-08-12; CRS R46180 (2020-01-15) |

### 2020 — Derecho del 10 de agosto

| Campo | Valor |
|---|---|
| Estados | IA (centro y este), también IL |
| Condados | 57 de IA en la trayectoria (RMA); 36 los más golpeados (IDALS). Vientos de 100–130 mph de Benton a Linn, Jones, Cedar y Clinton (NWS, citado). NASS publicó un mapa de ráfagas cruzado con el CDL 2019 |
| Meses | 10 de agosto |
| Rendimiento | en los 36 condados: ~3,57 M acres de maíz y 2,5 M de soja; McKinsey (satélite): 3,1–3,8 M acres con daño físico. Rendimiento estatal: falta (script) |
| Variables | **no** se ve en clima. `ndvi_anom_z` negativo en ago–sep en esos condados; `rend_bu_ac` por condado bajo con clima normal |
| Fuentes | USDA NASS Disaster Analysis, "2020 Event - Iowa Derecho Wind Damage"; Iowa Soybean Association, "Picking up the pieces"; McKinsey, "How the Iowa derecho has affected 2020 crops" |

### 2022 — Sequía en el oeste

| Campo | Valor |
|---|---|
| Estados | NE, KS |
| Condados | sin lista |
| Meses | verano |
| Rendimiento | maíz: NE −25 y KS −21 bu/ac respecto de la tendencia de farmdoc; soja: NE −8, KS −13 (estimaciones de NASS de dic 2022) |
| Variables | `spi3`, `spi6` jul–ago; `deficit_temporada_mm`; `dias_tmax_gt35` |
| Fuentes | farmdoc daily, "Corn and Soybean Yields in 2022" (2022-12) |

### 2023 — Sequía relámpago de junio

| Campo | Valor |
|---|---|
| Estados | IA (83 % en sequía moderada o peor), IL (99 % seco o en sequía a mediados de junio), MN |
| Condados | sin lista |
| Meses | mayo–junio |
| Rendimiento | EE.UU. 177,3 bu/ac (récord). IL 206 bu/ac (+2,6 sobre la tendencia); MN un poco más de 6 % bajo la tendencia |
| Variables | `spi1` de jun muy negativo, sin caída del rendimiento en IL: caso útil para ML |
| Fuentes | farmdoc daily, "Dry Weather and Drought in the Midwest, Middle-June 2023"; farmdoc daily, "Should We Have Been Surprised by the U.S. Average Yield of Corn in 2023?" (2024-04) |

### Pendientes (sin fuente todavía)

- **Granizo grande:** no busqué un listado. La fuente sería NOAA Storm Events Database (por condado, con daño a
  cultivos en USD) y las causas de pérdida de RMA (`docs/research/rma_causa_perdida.md`, código de causa granizo),
  que ya dan la señal por condado y año. Recomiendo usar RMA en lugar de una lista a mano.
- **Heladas tardías de primavera:** no encontré ninguna con efecto estatal. Se pueden detectar con
  `doy_ultima_helada` de `clima_anual.csv`.
- **Abril de 2017, tormenta de nieve en el oeste de KS (trigo):** no lo busqué.
- **2009 y 2004:** años fríos y de cosecha tardía, sin fuente abierta.

Fuentes (consultadas el 2026-11-15, a través de los resultados del buscador; los extractos se leyeron en el
buscador, las páginas no se abrieron enteras):
- [NASS Indiana, Annual Statistical Bulletin 2012-13, p. 26](https://data.nass.usda.gov/Statistics_by_State/Indiana/Publications/Annual_Statistical_Bulletin/1213/pg26.pdf)
- [NASS, Crop Production 2012 Summary, 2013-01-11](https://www.nass.usda.gov/Newsroom/printable/2013/01_11_13.pdf)
- [Illinois State Climatologist](https://stateclimatologist.web.illinois.edu/?p=3101)
- [KBIA, "Corn, soybean production took hit in 2012"](https://www.kbia.org/environment/2013-01-15/corn-soybean-production-took-hit-in-2012)
- [UNL CropWatch, "How Corn and Soybean Yields Fared by County in 2012"](https://cropwatch.unl.edu/how-corn-and-soybean-yields-fared-county-2012-unl-cropwatch-june-28-2013)
- [farmdoc daily, "Locating the 2012 drought"](https://farmdocdaily.illinois.edu/2013/02/locating-the-2012-drought.html)
- [DTN, "Kansas corn yields tumble" (2022)](https://www.dtnpf.com/agriculture/web/ag/crops/article/2022/08/11/kansas-corn-yields-tumble-lowest)
- [UNL CropWatch, "What 2002, 2009 and 2012 Yields Tell Us About Drought Years"](https://cropwatch.unl.edu/what-2002-2009-and-2012-yields-tell-us-about-drought-years/)
- [K-State, Drought.pdf](https://www.k-state.edu/irrigate/reports/Drought.pdf)
- [NOAA NCEI, U.S. Drought Highlights, agosto 2002](https://www.ncei.noaa.gov/sotc/drought/2002/aug)
- [farmdoc, "How bad were 2005 corn yields"](https://farmdoc.illinois.edu/publications/how-bad-were-2005-corn-yields)
- [Illinois State Academy of Science, Changnon](https://ilacadofsci.com/wp-content/uploads/2013/03/099-04MS2602-print.pdf)
- [Chicago Fed, Midwest Economy Blog 2008](https://www.chicagofed.org/publications/blogs/midwest-economy/2008/assessing-the-midwest)
- [CRS RL34583 (2008)](https://www.everycrsreport.com/files/20080716_RL34583_3f74f7dcd953b257a02decc67d927b769d3528aa.html)
- [NOAA NCEI, Global Hazards junio 2008](https://www.ncei.noaa.gov/sotc/hazards/200806)
- [Iowa HSEMD, After Action Report Missouri River 2011](https://publications.iowa.gov/17694/1/HSEMD_AAR_MissouriRiverTF_2011.pdf)
- [Decision Innovation Solutions, Missouri River flooding](https://www.decision-innovation.com/case-study/missouri-river-flooding/)
- [Insurance Journal, 2011-12-15](https://www.insurancejournal.com/news/midwest/2011/12/15/227585.htm)
- [Insurance Journal, 2012-10-22](https://www.insurancejournal.com/news/midwest/2012/10/22/267484.htm)
- [Star Tribune, "Early frosty grip on crops"](https://www.startribune.com/early-frosty-grip-on-crops/129962988)
- [Christian Science Monitor, 2013-07-05](https://csmonitor.com/USA/2013/0705/Year-after-drought-wettest-Midwest-spring-in-40-years-delays-crop-planting)
- [Iowa State University News, 2013-05-07](https://www.news.iastate.edu/news/2013/05/07/planting2013)
- [MPR News, 2013-05-10](https://www.mprnews.org/story/2013/05/10/business/farmers-behind-schedule)
- [Tonganoxie Mirror, 2014-10-01](https://www.tonganoxiemirror.com/news/2014/oct/01/report-kansas-wheat-production-lowest-1989/)
- [Washington Times / AP, 2014-05-09](https://www.washingtontimes.com/news/2014/may/9/kansas-wheat-forecast-to-be-smallest-since-1996/)
- [NPR, 2019-03-19](https://www.npr.org/2019/03/19/704737942/nebraska-floods-74-cities-65-counties-declare-state-of-emergency)
- [NPR, 2019-03-21](https://www.npr.org/2019/03/21/705408364/nebraska-faces-over-1-3-billion-in-flood-losses%EF%BB%BF)
- [Zapotocny, NWS Omaha, AMS 2020](https://ams.confex.com/ams/2020Annual/webprogram/Handout/Paper366519/Zapotocny_OAX_AMS2020Final.pdf)
- [OSU Extension Henry County, "Prevented Planting Acres Announced For 2019"](https://u.osu.edu/henryag/?p=1356)
- [DTN, "FSA: 19.3 Million Acres Unplanted", 2019-08-12](https://www.dtnpf.com/agriculture/web/ag/news/article/2019/08/12/farm-service-agency-cites-record)
- [CRS R46180, 2020-01-15](https://www.everycrsreport.com/files/20200115_R46180_5ab8cbed776972e75daaa50be04b6d3e91e6e328.html)
- [USDA NASS Disaster Analysis, 2020 Iowa Derecho](https://www.nass.usda.gov/Research_and_Science/Disaster-Analysis/2020/Iowa_Derecho/Derecho_Iowa_082520_2019CDL_metadata.htm)
- [Iowa Soybean Association, "Picking up the pieces"](https://www.iasoybeans.com/newsroom/article/picking-up-the-pieces)
- [McKinsey, "How the Iowa derecho has affected 2020 crops"](https://www.mckinsey.com/industries/agriculture/our-insights/how-the-iowa-derecho-has-affected-2020-crops)
- [farmdoc daily, "Corn and Soybean Yields in 2022"](https://farmdocdaily.illinois.edu/2022/12/corn-and-soybean-yields-in-2022.html)
- [farmdoc daily, "Dry Weather and Drought in the Midwest, Middle-June 2023"](https://farmdocdaily.illinois.edu/2023/06/dry-weather-and-drought-in-the-midwest-middle-june-2023.html)
- [farmdoc daily, "Should We Have Been Surprised by the U.S. Average Yield of Corn in 2023?"](https://farmdocdaily.illinois.edu/2024/04/should-we-have-been-surprised-by-the-u-s-average-yield-of-corn-in-2023.html)

Confianza: **media**. Alta para la existencia, los estados y los meses de cada evento (varias fuentes coinciden).
Media a baja para las cifras: muchas son de prensa o proyecciones de mitad de temporada, se leyeron en extractos del
buscador y no se contrastaron con Quick Stats. Los rendimientos de NASS se confirman con
`eventos_extremos_rend_estado.py`.

Impacto: T007 (control de calidad de `clima`, `agua`, `vegetacion` y `cultivos`): usar la tabla de arriba como lista
de chequeos de señal esperada. ML: marcar como años raros 2012 (todos), 2019 (siembra), 2020 (IA, viento),
2002 y 2022 (NE, KS) y separar riego de secano en NE y KS. No cambia `config/` ni el esquema de ningún CSV.
