# Eventos extremos 2000–2025 en OH, NE, MN y KS (complemento)

Pregunta: ¿Qué eventos climáticos conocidos de 2000 a 2025 tienen que verse en los datos de los estados nuevos
(OH, NE, MN y KS)? Para cada uno: estado, condados o región, año y meses, tipo, señal esperada en nuestros CSV y
fuente. Sirve para el control de calidad de T007.

Este documento **complementa** a `docs/research/eventos_extremos.md` y no repite lo que ya está ahí. Para los
estados nuevos, ese archivo ya cubre: 2002 (sequía en NE y KS), 2011 (inundación del Missouri en NE y helada
temprana en MN), 2012 (sequía en los 7 estados), 2013 (primavera húmeda en MN), 2014 (trigo de KS), 2019
(inundación de marzo en NE y siembra prevenida en OH) y 2022 (sequía de verano en NE y KS).

Respuesta corta:

| Año | Evento | Estado | Región | Meses | Tipo | Efecto conocido | Señal esperada en nuestros CSV |
|---|---|---|---|---|---|---|---|
| 2002 | Sequía en Ohio | OH | todo el estado, muy desparejo | jun–ago | sequía | maíz 88 bu/ac (138 en 2001), el más bajo desde 1988; soja 30 bu/ac (41 en 2001) | `spi3` jul–ago negativo; `prec_jul_mm` bajo; `rend_bu_ac` de maíz y soja de OH muy bajo |
| 2004 | Helada temprana de agosto | MN | sobre todo el norte (al norte de la I-94); manchones en el sur | 19–21 ago | helada temprana | soja con 64 % buena–excelente el 8 de ago y 44 % el 29 de ago; −10 % de rendimiento estimado en las zonas afectadas | `doy_primera_helada` en ago (muy temprano); `dias_tmin_le0` en ago; `tmin_c` de ago bajo |
| 2007 | Helada de abril sobre el trigo adelantado | KS | todo el estado | 4–10 abr (tras un marzo cálido) | helada tardía | encuesta de USDA a mediados de abril: 31 % del trigo sin daño, 25 % leve, 26 % moderado y 18 % severo | `anom_tmed_c` de mar positivo y `dias_tmin_le_m2` de abr alto; `doy_ultima_helada` tardío; `rend_bu_ac` de trigo de KS |
| 2011 | Sequía en el sur de las Grandes Llanuras | KS | suroeste y centro-sur (Finney, Haskell) | otoño 2010 a may 2011 | sequía (trigo) | gira de mayo: 37,4 bu/ac (45 en 2010); Finney y Haskell 25,1 bu/ac (61 en 2010) | `prec_invierno_previo_mm` bajo; `spi6` de mar–may negativo; `rend_bu_ac` de trigo bajo en el suroeste |
| 2011 | Ola de calor en floración | todo el Midwest; récord de punto de rocío en MN | MN (Moorhead, condado de Clay), oeste de OH y el resto | 18–24 jul | calor | mínimas 8–12 °F sobre lo normal; 994 récords de mínima alta; punto de rocío de 88 °F en Moorhead (récord de MN) | `tmin_c` y `tmed_c` de jul altos; `dias_tmax_gt30_jul`; `hr_pct` (diario) alto; `anom_tmed_c` de jul positivo |
| 2012 | Sequía (detalle de Ohio) | OH | empezó en el noroeste | jun–ago | sequía y calor | pronóstico de USDA (ago y sep): 126 bu/ac (158 en 2011); gira de Pro Farmer: 110,5 | igual que 2012 en el documento base; el noroeste de OH debería ser peor que el sureste |
| 2017 | Ventisca de fines de abril | KS | oeste y suroeste (≈40 % de la superficie de trigo) | 28 abr – 1 may | nieve y helada | más de 15 pulgadas en partes del oeste; trigo acostado y tallos quebrados; mayores pérdidas esperadas en el suroeste | `tmin_c` y `dias_tmin_le0` a fines de abr; `prec_*` de abr alto (nieve); `rend_bu_ac` de trigo del oeste de KS |
| 2018 | Sequía y frío de primavera en el trigo | KS | todo el estado (la ruta de la gira: centro, noroeste y sur) | otoño 2017 a may 2018 | sequía (trigo) | gira de mayo: 37,0 bu/ac (48 en 2017) y 243 M bu, la cosecha más chica desde 1989 si se confirmaba | `prec_invierno_previo_mm` bajo; `spi6` de mar–may negativo; `rend_bu_ac` de trigo de KS |
| 2021 | Sequía en Minnesota | MN | norte (Beltrami en D3 a mediados de jul) y oeste (D2); suelos arenosos | jun–ago | sequía | maíz 178 bu/ac (191 en 2020, proyección de oct); poco heno de calidad; otoño cálido y sin helada hasta fines de oct | `spi3` de jul–ago negativo en el norte; `ndvi_anom_z` negativo; `rend_bu_ac` de maíz y heno de MN bajo; `doy_primera_helada` tardío |
| 2023 | Sequía en el trigo de Kansas | KS | todo el estado, peor en el oeste | otoño 2022 a may 2023 | sequía (trigo) | USDA (estimación del 1 de ago): 208 M bu, 32 bu/ac en 6,5 M ac, la cosecha más chica desde 1966; abandono estimado en 18,5 % en mayo | `prec_invierno_previo_mm` bajo; `spi6` muy negativo; `ratio_cosechada` de trigo bajo (abandono); `rend_bu_ac` de trigo bajo |

Lo que **no** encontré con fuente, o no busqué:
- **Ningún evento nuevo propio de Nebraska.** Los grandes (2002, 2011, 2012, 2019, 2022) ya están en el documento
  base. No busqué la sequía de 2023 en NE ni la de 2006.
- **Rendimientos finales de NASS** para el trigo de KS en 2011, 2017, 2018 y 2023, para el maíz de OH en 2012 y
  para MN en 2021. Las cifras de la tabla son pronósticos de mitad de temporada o estimaciones de la gira de
  trigo, salvo OH 2002, que es el valor anual de USDA según la prensa. Se confirman con el script del documento
  base (`docs/research/eventos_extremos_rend_estado.py`).
- **Pérdida de rendimiento por la helada de abril de 2007 en KS:** solo encontré el daño (encuesta de USDA), no el
  rendimiento.
- **Condados afectados:** solo para Finney y Haskell (KS 2011), Beltrami y Polk (MN 2021) y Clay (MN, punto de
  rocío 2011). El resto es "región".
- **Siembra prevenida de MN en 2019** (1,00 M ac de maíz) y **de KS en 2025** (256 mil ac de soja): ya están en
  `docs/research/siembra_prevenida.md`, sacados de FSA. No los repito como eventos aparte.

Detalle:

**Cómo usarlo en T007.** Igual que el documento base: si un CSV procesado *no* muestra la señal esperada en el
año, el estado y los meses del evento, hay que revisar el proceso. Un valor extremo en un año sin evento listado
no es un error por sí mismo.

**Advertencias:**
- **Cuatro de los diez eventos son de trigo de invierno de KS** (2007, 2011, 2018 y 2023). La señal está en el
  invierno previo y la primavera (`prec_invierno_previo_mm`, `spi6` de marzo a mayo), no en la temporada de
  abril a septiembre. Un `prec_temporada_mm` normal en esos años no indica un error.
- **2023 en KS:** la sequía hizo abandonar trigo. El rendimiento de NASS es por acre **cosechado**, así que
  el abandono no se ve en `rend_bu_ac` sino en `ratio_cosechada`. En 2023 también hubo lluvia fuerte a
  principios de julio, que atrasó la cosecha: julio puede verse húmedo en un año de sequía.
- **2021 en MN:** el maíz bajó 13 bu/ac a nivel estado, pero la prensa dice que la cosecha fue "mejor que lo
  esperado". El daño se concentró en el norte y en suelos arenosos: mirar por condado, no por estado.
- **Heladas (2004 en MN, 2007 y 2017 en KS):** POWER es una media de celda de 0,5°; las heladas locales de bajos
  pueden no llegar a 0 °C en la celda. Si `dias_tmin_le0` no aparece en agosto de 2004 en el sur de MN, es
  esperable (allí la helada fue en manchones); en el norte sí debería verse.
- **2011, calor de julio:** el récord fue de **mínimas** altas y de humedad, no de máximas. Va a verse más en
  `tmin_c` y `hr_pct` (diario) que en `dias_tmax_gt35`.

### 2002 — Sequía en Ohio

| Campo | Valor |
|---|---|
| Estado | OH |
| Condados | sin lista; muy desparejo según la lluvia ("algunos tuvieron el mejor rendimiento, otros el peor", OSU) |
| Meses | verano; floración del maíz en julio con lluvias "de a manchones" (OSU, fines de julio) |
| Rendimiento | maíz 88 bu/ac, 50 menos que en 2001 y el más bajo desde 1988 (85); producción 252,6 M bu, −42 %. Soja 30 bu/ac, 11 menos que en 2001 (Farm and Dairy, 2003-01-16, con datos de USDA) |
| Variables | `spi3` y `prec_jul_mm` bajos; `deficit_temporada_mm`; `rend_bu_ac` de OH |
| Fuentes | Farm and Dairy, "Ohio corn, soybean yields below normal" (abierta); OSU CFAES, "Rains arrive too late to help corn crop" (extracto del buscador) |

### 2004 — Helada temprana de agosto en Minnesota

| Campo | Valor |
|---|---|
| Estado | MN (también ND y el norte de IA en manchones) |
| Condados | sin lista. Estaciones con récord: Embarrass 20 °F (21 ago), Tower 25 °F, St. Cloud 33 °F (empata el récord de agosto), International Falls 32 °F, Crookston 37 °F |
| Meses | 19 a 21 de agosto, tras un verano frío y una siembra tardía |
| Efecto | soja de MN: 64 % buena–excelente el 8 de ago y 44 % el 29 de ago (resumen del MRCC); estimación de un agrónomo: −10 % del rendimiento potencial en las zonas afectadas. Sin dato final de NASS |
| Variables | `doy_primera_helada` en agosto en el norte; `dias_tmin_le0` de ago; `tmin_c` de ago bajo; `gdd_temporada` bajo (verano frío) |
| Fuentes | Minnesota DNR, "Frosty August 20-21, 2004" (abierta); MRCC, resumen climático (extracto); Claims Journal 2004-09-01 (extracto) |

### 2007 — Helada de abril en el trigo de Kansas

| Campo | Valor |
|---|---|
| Estado | KS |
| Condados | sin lista; el trigo sembrado temprano y de ciclo corto sufrió más |
| Meses | marzo muy cálido que adelantó el trigo; mínimas "en los teens" (°F) del 4 al 10 de abril |
| Efecto | encuesta de NASS Kansas de mediados de abril: 31 % sin daño, 25 % leve, 26 % moderado, 18 % severo. Una fuente de Missouri dice que el clima posterior ayudó a la recuperación. Sin rendimiento final |
| Variables | `anom_tmed_c` de mar positivo seguido de `dias_tmin_le_m2` de abr; `doy_ultima_helada` tardío; `rend_bu_ac` de trigo de KS |
| Fuentes | NASS Kansas, Crop Progress semanales de abril de 2007 (wkly0415.pdf, wkly0422.pdf; extracto del buscador); Claims Journal 2007-05-02 (extracto) |

### 2011 — Sequía y trigo en el suroeste de Kansas

| Campo | Valor |
|---|---|
| Estado | KS |
| Condados | suroeste y centro-sur; Finney y Haskell con 25,1 bu/ac en la gira (61,0 en 2010; promedio de 5 años ≈ 42,5) |
| Meses | invierno 2010–11 a mayo; a fines de mayo ≈60 % de KS en sequía moderada a excepcional (US Drought Monitor) |
| Efecto | gira del Wheat Quality Council (mayo): 37,4 bu/ac y 256,7 M bu (45 bu/ac en 2010); USDA, 2 de mayo: 21 % bueno–excelente, 45 % malo–muy malo. La cosecha final salió mejor que la gira (sin número) |
| Variables | `prec_invierno_previo_mm` bajo; `spi6` negativo en mar–may en el suroeste; `rend_bu_ac` de trigo por condado |
| Fuentes | Reuters vía SEJ, "Farm States Suffer Expanded Drought, Wheat Suffers", 2011-05-20 (abierta); eFeedLink 2011-05-09 y 2011-05-30 (extracto); Baking Business, gira 2011 (extracto; la página dio 403) |

### 2011 — Ola de calor de julio (floración)

| Campo | Valor |
|---|---|
| Estados | todo el Midwest; récord de humedad en MN; temperaturas medias más altas desde el oeste de MO hasta el oeste de OH |
| Condados | Clay (MN): punto de rocío de 88 °F en Moorhead el 19 de julio, récord estatal (antes 86 °F en 2005) |
| Meses | 18 a 24 de julio |
| Efecto | temperaturas 5–10 °F sobre lo normal; mínimas 8–12 °F sobre lo normal; 994 récords de mínima alta frente a 318 de máxima. El maíz empezaba a florecer. Sin cifra de rendimiento por estado |
| Variables | `tmin_c` de jul alto; `hr_pct` (diario) alto; `anom_tmed_c` de jul positivo; `dias_tmax_gt30_jul` |
| Fuentes | MRCC, resumen semanal del 18 al 24 de julio de 2011 (abierta); MPR News 2011-07-18 y 2011-07-20 (extracto); UNL CropWatch 2011-07-14 (extracto) |

### 2012 — Sequía: detalle de Ohio

| Campo | Valor |
|---|---|
| Estado | OH |
| Condados | la sequía empezó en el noroeste; en el oeste hubo maíz de hasta 30 bu/ac (OSU) |
| Meses | junio a agosto |
| Rendimiento | USDA, pronósticos de agosto y septiembre: 126 bu/ac (158 en 2011). Gira de Pro Farmer: 110,5. Sin valor final (lo da el script del documento base) |
| Variables | las de 2012 en el documento base; gradiente noroeste–sureste dentro de OH |
| Fuentes | OSU CFAES, "USDA: Ongoing drought causes significant crop yield declines" (extracto; la página redirige a la portada); AgWeb, Evening Report 2012-08-24 (extracto) |

### 2017 — Ventisca de fines de abril en Kansas

| Campo | Valor |
|---|---|
| Estado | KS |
| Condados | oeste y suroeste; Dodge City (Ford) con su nevada más tardía registrada (2,5 pulgadas el 30 de abril); la I-70 cerrada en el oeste |
| Meses | 28 de abril a 1 de mayo |
| Efecto | más de 15 pulgadas de nieve en partes del oeste, sobre ≈40 % de la superficie de trigo del estado; K-State esperaba las mayores pérdidas en el suroeste. El departamento de agricultura de KS: al menos 40 % del trigo con algún daño. También hubo heladas antes y roya amarilla. Sin rendimiento final |
| Variables | `prec_*` de abr alto (equivalente en agua de la nieve); `tmin_c` y `dias_tmin_le0` a fines de abr; `rend_bu_ac` de trigo del oeste de KS |
| Fuentes | NOAA Climate.gov, "Tornadoes and blizzards: it's spring across the Great Plains" (abierta); K-State Agronomy eUpdate, "Kansas weather summary April 2017: epic blizzard" (extracto; la página redirige); Sunflower State Radio 2017-05-03 (extracto) |

### 2018 — Sequía y frío en el trigo de Kansas

| Campo | Valor |
|---|---|
| Estado | KS |
| Condados | sin lista; la gira (Manhattan–Colby–Wichita) encontró el cultivo atrasado y seco; las lluvias del centro llegaron tarde |
| Meses | sequía desde el otoño de 2017; frío de primavera |
| Efecto | gira del Wheat Quality Council (3 de mayo): 37,0 bu/ac y 243,3 M bu, frente a 48,0 bu/ac y 333,6 M bu de USDA en 2017; sería la más chica desde 1989. Pronóstico de USDA: 37 bu/ac y 270,1 M bu. Sin valor final |
| Variables | `prec_invierno_previo_mm` bajo; `spi6` de mar–may negativo; `rend_bu_ac` de trigo de KS |
| Fuentes | Western Producer / Reuters, "Drought to shrink Kansas wheat crop to smallest since 1989" (abierta); Baking Business, "USDA forecasts smallest winter wheat crop since 2002" (extracto) |

### 2021 — Sequía en Minnesota

| Campo | Valor |
|---|---|
| Estado | MN |
| Condados | Beltrami en D3 (extrema) a mediados de julio, el oeste en D2; Polk proyectado en 89,4 bu/ac en la gira digital de DTN de agosto (proyección); Isanti con pérdidas de 50–60 % en algunas zonas |
| Meses | verano; mejoras en el oeste recién con lluvias de fines de septiembre a octubre (NWS) |
| Efecto | maíz 178 bu/ac proyectado en octubre (191 en 2020 y 173 en 2019); maíz de suelos arenosos cosechado como silo; faltó heno de calidad. Otoño cálido: a mediados de octubre todavía no había helado en el centro y sur de MN |
| Variables | `spi3` de jul–ago negativo en el norte y oeste; `ndvi_anom_z` negativo en jul–ago; `rend_bu_ac` de maíz por condado; `doy_primera_helada` tardío |
| Fuentes | Minnesota Corn, "Harvest 2021: Drought across Upper Midwest…", 2021-10-22 (abierta); NWS Twin Cities, Drought Update 2021-10-14 (abierta; PDF, sin cifras de rendimiento legibles); MPR News 2022-04-05 (abierta); DTN Digital Yield Tour 2021-08-11 (extracto); NDMC Drought Impact Reporter (extracto) |

### 2023 — Sequía en el trigo de Kansas

| Campo | Valor |
|---|---|
| Estado | KS |
| Condados | sin lista; en Sumner, rendimientos de 5 a 48 bu/ac y abandono local de 10–15 % |
| Meses | sequía hasta mayo; lluvia fuerte a principios de julio que atrasó la cosecha |
| Efecto | USDA (última estimación antes del 1 de agosto de 2023): 208 M bu, 32 bu/ac, 6,5 M ac, la cosecha más chica desde 1966. El pronóstico de USDA del 1 de mayo: 191 M bu, 29 bu/ac y 18,5 % de abandono; la gira: 178 M bu. El valor final (Small Grains Summary del 30 de septiembre de 2023) no lo encontré |
| Variables | `prec_invierno_previo_mm` bajo; `spi6` muy negativo en mar–may; `ratio_cosechada` de trigo bajo; `rend_bu_ac` de trigo bajo |
| Fuentes | Kansas Wheat vía KSAL, "Harvest Finally Draws to Close", 2023-08-01 (abierta); DTN, "Wheat Tour Yield Average Hits 30 BPA", 2023-05-18 (extracto); Oklahoma Farm Report 2023-05-18 (extracto) |

Fuentes (consultadas el 2026-11-15; "abierta" = página leída; el resto, extractos del buscador):
- [Farm and Dairy, "Ohio corn, soybean yields below normal" (2003-01-16)](https://www.farmanddairy.com/?p=4241) — abierta
- [OSU CFAES, "Rains arrive too late to help corn crop"](https://news-archive.cfaes.ohio-state.edu/news-release/rains-arrive-too-late-help-corn-crop)
- [Minnesota DNR, "Frosty August 20-21, 2004"](https://climateapps.dnr.state.mn.us/doc/journal/frosty040820_21.htm) — abierta
- [MRCC, resumen climático de agosto de 2004](https://mrcc.purdue.edu/climatesummaries/461)
- [Claims Journal, 2004-09-01](https://amp.claimsjournal.com/news/midwest/2004/09/01/45462.htm)
- [NASS Kansas, Crop Progress 2007-04-15](https://data.nass.usda.gov/Statistics_by_State/Kansas/Publications/Crop_Progress_and_Condition/2007/wkly0415.pdf)
- [NASS Kansas, Crop Progress 2007-04-22](https://data.nass.usda.gov/Statistics_by_State/Kansas/Publications/Crop_Progress_and_Condition/2007/wkly0422.pdf)
- [Claims Journal, 2007-05-02](https://www.claimsjournal.com/news/midwest/2007/05/02/79285.htm)
- [Reuters vía SEJ, "Farm States Suffer Expanded Drought, Wheat Suffers" (2011-05-20)](https://sej.org/print/headlines/farm-states-suffer-expanded-drought-wheat-suffers) — abierta
- [eFeedLink, 2011-05-09](https://www.efeedlink.com/contents/05-09-2011/c1b83917-e1e4-4cb1-8011-caecaea53f2d-a181.html)
- [eFeedLink, 2011-05-30](https://www.efeedlink.com/contents/05-30-2011/51ff904a-ee2d-4de4-a105-93d9d329307b-a181.html)
- [Baking Business, "Tour forecasts the smallest Kansas wheat crop since 1996"](https://www.bakingbusiness.com/articles/36180-tour-forecasts-the-smallest-kansas-wheat-crop-since-1996) — 403 al abrirla
- [MRCC, resumen del 18 al 24 de julio de 2011](https://mrcc.purdue.edu/climatesummaries/894) — abierta
- [MPR News, "Uncharted Heat Index values" (2011-07-18)](https://www.mprnews.org/story/2011/07/18/uncharted-heat-index-values)
- [UNL CropWatch, 2011-07-14](https://cropwatch.unl.edu/high-winds-sweep-corn-belt-heat-wave-likely-hit-pollination-unl-cropwatch-july-14-2011)
- [OSU CFAES, "USDA: Ongoing drought causes significant crop yield declines" (2012)](https://news-archive.cfaes.ohio-state.edu/news-release/usda-ongoing-drought-causes-significant-crop-yield-declines-0) — redirige a la portada
- [AgWeb, Evening Report 2012-08-24](https://www.agweb.com/news/machinery/100-ideas/evening-report-vip-august-24-2012)
- [NOAA Climate.gov, "Tornadoes and blizzards: it's spring across the Great Plains" (2017)](https://www.climate.gov/news-features/event-tracker/tornadoes-and-blizzards-its-spring-across-great-plains) — abierta
- [K-State Agronomy eUpdate, "Kansas weather summary April 2017: epic blizzard"](https://eupdate.agronomy.ksu.edu/article/kansas-weather-summary-april-2017-epic-blizzard-632-13) — redirige
- [Sunflower State Radio, 2017-05-03](https://sunflowerstateradio.com/2017/05/03/kansas-wheat-commission-chief-we-lost-the-western-kansas-wheat-crop/)
- [Western Producer / Reuters, "Drought to shrink Kansas wheat crop to smallest since 1989" (2018-05-03)](https://www.producer.com/daily/drought-to-shrink-kansas-wheat-crop-to-smallest-since-1989) — abierta
- [Baking Business, "USDA forecasts smallest winter wheat crop since 2002" (2018)](https://www.bakingbusiness.com/articles/46223-usda-forecasts-smallest-winter-wheat-crop-since-2002)
- [Minnesota Corn, "Harvest 2021: Drought across Upper Midwest…" (2021-10-22)](https://www.mncorn.org/?p=18087) — abierta
- [NWS Twin Cities, Drought Update (2021-10-14)](https://www.weather.gov/media/mpx/MPXdroughtpacket.pdf) — abierta
- [MPR News, "Despite drought Minnesota farmers fared well in 2021" (2022-04-05)](https://www.mprnews.org/story/2022/04/05/despite-drought-minnesota-farmers-fared-well-in-2021) — abierta
- [DTN, 2021 Digital Yield Tour, día 3 (2021-08-11)](https://www.dtnpf.com/agriculture/web/ag/crops/article/2021/08/11/drought-trims-minnesota-yields-iowa)
- [Kansas Wheat vía KSAL, "Harvest Finally Draws to Close" (2023-08-01)](https://www.ksal.com/harvest-finally-draws-to-close/) — abierta
- [DTN, "Wheat Tour Yield Average Hits 30 BPA" (2023-05-18)](https://www.dtnpf.com/agriculture/web/ag/crops/article/2023/05/18/final-day-2023-winter-wheat-tour-30)
- [Oklahoma Farm Report, 2023-05-18](https://www.oklahomafarmreport.com/2023/05/18/abandoned-fields-and-low-yields-result-in-prediction-of-178-million-bushel-kansas-wheat-crop/)

Confianza: **media**. Alta para la existencia, el estado y las fechas de cada evento (las fuentes abiertas
coinciden). Media a baja para las cifras de rendimiento: salvo OH 2002, son pronósticos de mitad de temporada,
giras de campo o estimaciones de prensa, no valores finales de NASS. Las cifras marcadas como extracto no se
leyeron en la página original.

Impacto: T007 (control de calidad de `clima`, `agua`, `vegetacion` y `cultivos` en OH, NE, MN y KS): sumar estos
eventos a la lista de chequeos del documento base. Para el trigo de KS, el chequeo va en el invierno previo y la
primavera, no en la temporada de verano. ML: sumar como años raros 2002 (OH), 2021 (MN) y 2007, 2011, 2017, 2018
y 2023 (trigo de KS). No cambia `config/` ni el esquema de ningún CSV.
