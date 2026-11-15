# Eventos extremos 2000–2025 en MI y ND

Pregunta: ¿Qué eventos climáticos conocidos de 2000 a 2025 tienen que verse en los datos de Michigan y Dakota del
Norte? Para cada uno: estado, región o condados, año y meses, tipo, señal esperada en nuestros CSV y fuente. Sirve
para que el humano decida una cuarta tanda de estados y, si entran, para el control de calidad (como T007).

Mismo formato que `docs/research/eventos_extremos_mo_wi_sd.md`. **MI y ND no están en `config/config.yaml`**:
nada de esto cambia el pipeline hoy.

**Sin rendimientos de NASS.** A diferencia del documento de MO, WI y SD, acá no hay rendimientos finales de NASS:
la máquina no tenía la base completa de Quick Stats (`qs.crops_20261114.txt.gz`, 1,1 GB) y la tarea pide no bajar
datasets grandes. El script `docs/research/eventos_extremos_mi_nd_rend.py` queda listo (MI y ND; maíz, soja, trigo
de invierno y trigo de primavera sin durum) para correrlo en una máquina que ya la tenga. Las cifras de producción
de abajo son de las fuentes citadas (casi siempre proyecciones del año del evento), no finales.

Respuesta corta:

| Año | Evento | Estado | Región | Meses | Tipo | Efecto conocido | Señal esperada en nuestros CSV |
|---|---|---|---|---|---|---|---|
| 2009 | Inundación del río Red (récord en Fargo) | ND | valle del Red (este: Cass, Grand Forks y aguas abajo) | fin de mar – may | inundación por deshielo | Fargo: 40,84 ft, el máximo desde 1902 (USGS). Sin cifra agrícola con fuente abierta | `prec_*` y nieve del invierno previo; `sm_rootzone_anom_z` alto en abr–may; `doy_50_sembrado` tardío; **poco** en la lluvia de primavera |
| 2011 | Siembra prevenida récord | ND | sobre todo el **noroeste** (36 % en seis condados del rincón noroeste) | primavera | exceso de agua (nieve, lluvia, ríos) | ≈6,3 M ac sin sembrar (NDSU) o 5,3–5,6 M (RMA y FSA); récord previo 3,9 M en 1999; promedio 2000–2009 ≈1 M. Cebada −62 % y durum −72 % de producción | `prec_*` y `sm_rootzone_anom_z` altos en abr–jun; `sup_sembrada_ac` muy baja en el noroeste; CDL con barbecho; `rend_bu_ac` casi no se mueve |
| 2011 | Inundación del río Souris (Minot) | ND | Ward (Minot) y valle del Souris | jun (pico 25–26 jun) | inundación de río | cresta récord 1.561,72 ft s.n.m. (récord previo de 1881). Sin cifra agrícola de ND | casi nada en clima local; CDL ribereño; `ratio_cosechada` de Ward y McHenry |
| 2011 | Helada temprana | ND | "la mayor parte de ND" | 2.ª semana de sep | helada temprana | maíz: ≈65 % en dent sin madurar y 15 % antes de dent; pérdida > USD 180 M; −23 % de rendimiento si mató hojas en dent | `doy_primera_helada` temprano; `dias_tmin_le0` de sep; `rend_bu_ac` de maíz de ND |
| 2012 | Helada de primavera tras marzo cálido | MI | noroeste (Traverse City, cerezas) y fruticultura de todo el estado | calor a fines de mar; > 12 noches de helada mar–may | helada tardía | cereza ácida > 90 % perdida (PBS) o de 157,5 a ≈5,5 M lb (USDA vía FreshPlaza); USD 210 M. **Fruta, no granos** | `anom_tmed_c` de mar muy positivo; `dias_tmin_le0` de abr–may; `doy_ultima_helada` tardío. No toca nuestros cultivos |
| 2012 | Sequía | MI | todo el estado; primero el sur (Branch, Cass, Hillsdale, St. Joseph) | desde mar; peor jun–ago | sequía y calor | 82 % del estado de anormalmente seco a sequía extrema (25-jul); los 83 condados en desastre (29-ago) | `spi3` jul negativo; `dias_tmax_gt35`; `vhi` y `ndvi_anom_z` bajos; `rend_bu_ac` de maíz y soja de MI |
| 2013 | Siembra prevenida | ND | norte de la ruta 200: Ward y Bottineau (> 300.000 ac cada uno), Cavalier, Renville y Towner (> 200.000) | primavera | exceso de agua | ≈3,75 M ac; USD 627 M directo (NDSU) | `sup_sembrada_ac` baja en el norte; `sm_rootzone_anom_z` alto |
| 2017 | Sequía relámpago de las Grandes Llanuras del norte | ND | todo menos el sureste (Richland y Sargent); empezó en el suroeste | may – sep | sequía relámpago | proyecciones vs 2016: trigo de invierno −74 %, durum −56 %, primavera −31 %, alfalfa −21 %, maíz −17 %, soja +1 % | `spi1`/`spi3` de may–jul muy negativos en el oeste; `ndvi_anom_z` negativo; gradiente oeste–sureste |
| 2019 | Primavera húmeda y siembra prevenida | MI | todo el estado | abr – jun | exceso de agua | 31-may: un tercio del maíz y un cuarto de la soja sembrados, la siembra de maíz más lenta registrada; ≈900.000 ac sin sembrar; producción esperada maíz −9 %, soja −31 % (USDA, oct) | `prec_*` de may altos; `doy_50_sembrado` tardío; `sup_sembrada_ac` baja; `rend_bu_ac` poco afectado |
| 2019 | Inundación del río Red | ND | valle del Red (Fargo) | abr (cresta ≈7-abr, ≈35 ft) | inundación por deshielo | inundación mayor; 35 ft se había superado solo 7 veces desde 1902 (USGS). Sin cifra agrícola | igual que 2009 |
| 2021 | Sequía | ND | todo el estado; peor en el centro y oeste | oct 2020 – ago 2021 | sequía | oct–jun: 3.er período más seco; 22-jul: 100 % en D1, 97 % D2, 49 % D3, 8 % D4 (NDSU); pasturas 71 % pobres o muy pobres; más de la mitad del trigo de primavera pobre o muy pobre (mediados de jul) | `spi6` muy negativo desde el invierno; `prec_invierno_previo_mm` bajo; `ndvi_anom_z` y `vhi` bajos; `rend_bu_ac` bajo |
| 2022 | Primavera húmeda y siembra prevenida | ND | este y norte (extracto) | abr – jun | exceso de agua (nieve de abril, lluvia) | ≈2,3–2,4 M ac, ≈40 % del total de EE.UU. (maíz 1,19 M, trigo 0,60 M, soja 0,52 M; extractos de FSA). 23-jun: maíz 90 % y soja 92 % de la superficie de 2021 sembrados (DTN) | `prec_*` de abr–may altos; `doy_50_sembrado` tardío; `sup_sembrada_ac` baja |

Lo que **no** encontré con fuente, o no busqué:
- **Rendimientos finales de NASS** de MI y ND: no se calcularon (ver arriba). Todas las cifras de producción son
  proyecciones del año del evento.
- **ND 2019 (siembra prevenida):** la tarea la menciona, pero no abrí ninguna fuente con la cifra de ND. Puede
  salir de los datos de FSA de `docs/research/siembra_prevenida.md`.
- **ND 2022:** la nota de AgWeb (40 % del total) dio 403 y los resúmenes de FSA de ND dieron timeout. Las cifras
  por cultivo son extractos del buscador. Tampoco confirmé si fue récord estatal (no lo es: 2011 fue mayor).
- **MI 2019, siembra prevenida oficial:** solo los ≈900.000 ac de la nota de WCMU (sin fuente primaria) y una
  estimación de productores de 600–700 mil ac de maíz (extracto).
- **Río Red, efecto agrícola:** el informe del USGS sobre 2009 (SIR 2010-5225) dio 403 y la nota de MPR falló.
  Solo tengo el nivel récord. No busqué las crecidas de 2010 y 2011 del Red (USGS las lista como mayores).
- **Heladas tempranas fuera de ND 2011:** la de 2004 en ND aparece en extractos contradictorios (otro extracto
  habla de un septiembre sin heladas); no la incluyo. En MI no encontré heladas tempranas de otoño con fuente.
- **MI 2012, efecto en granos:** no encontré el rendimiento; la nota del MSU del suroeste (12-jul-2012) cargó vacía.
- **Olas de calor, granizo, derechos:** no busqué.

Detalle:

**Cómo usarlo.** Igual que el documento base: si un CSV procesado *no* muestra la señal esperada en el año, el
estado y los meses del evento, hay que revisar el proceso. Un valor extremo en un año sin evento listado no es un
error por sí mismo.

**Advertencias:**
- **ND es un estado de exceso de agua de primavera.** El promedio 2000–2009 ya era ≈1 M ac de siembra prevenida
  por año (NDSU), y 2011, 2013 y 2022 lo multiplican. La señal fuerte está en `sup_sembrada_ac`, no en
  `rend_bu_ac` (NASS da el rendimiento por acre cosechado).
- **Las inundaciones del Red y del Souris vienen del deshielo y de río arriba** (en el Souris, también desde
  Canadá). La lluvia local de primavera puede ser normal: la señal está en la nieve y la lluvia del invierno
  previo, en la humedad del suelo y en la fecha de siembra.
- **ND 2017 y 2021 golpean más al trigo y las pasturas que al maíz y la soja**: el sureste (Richland, Sargent),
  donde hay más maíz y soja, quedó fuera de la sequía de 2017 y del haying de emergencia de 2021. Si entran
  cultivos nuevos (trigo de primavera, durum, cebada), este es el estado donde más se ven.
- **MI 2012 tiene dos eventos en el mismo año**: la helada de primavera (frutales) y la sequía de verano
  (granos). No confundirlos al leer `doy_ultima_helada`.
- **Junio de 2021 fue el 3.er junio más frío** en ND (NDSU) dentro de la sequía: no esperar `dias_tmax_gt35`
  altos en todos los meses.

### 2009 y 2019 — Inundaciones del río Red en Dakota del Norte

| Campo | Valor |
|---|---|
| Estado | ND (también MN en la otra orilla) |
| Región | valle del Red: Fargo (Cass) y aguas abajo |
| Meses | 2009: fines de marzo a mayo (deshielo). 2019: cresta pronosticada ≈7 de abril, ≈35 ft |
| Efecto | 2009: 40,84 ft en Fargo, el nivel más alto desde que se mide (1902). Sobre 35 ft solo siete veces hasta 2019; años de inundación mayor: 1969, 1989, 1997, 2001, 2009, 2010 y 2011. Sin cifras agrícolas con fuente abierta |
| Variables | nieve y lluvia del invierno previo (`prec_invierno_previo_mm`); `sm_rootzone_anom_z` alto; `doy_50_sembrado` tardío en el este de ND |
| Fuentes | USGS, "Media Advisory: USGS Crews Measure Record Flooding in Fargo", 2019-04-05 (abierta); USGS SIR 2010-5225 sobre 2009 (403) |

### 2011 — Siembra prevenida récord en Dakota del Norte

| Campo | Valor |
|---|---|
| Estado | ND (SD tuvo 1,2–1,4 M ac, ya en `eventos_extremos_mo_wi_sd.md` por el río Missouri) |
| Región | la mayoría en el cuarto noroeste; 36 % en seis condados del rincón noroeste (sin nombres). Históricamente el problema era el noreste y el sureste |
| Meses | primavera; deshielo, lluvias e inundaciones del Missouri y del Souris |
| Efecto | NDSU (27-jun-2011): ≈6,3 M ac sin sembrar, 5,2 M sobre el promedio 2000–2009 (≈1 M); USD 1,1 mil M directo, 2,9 mil M total. AP (may-2012): 5,3 M (RMA) a 5,6 M (FSA), récord previo 3,9 M en 1999; producción de cebada −62 % y durum −72 %. NDSU (2013) cita 5,6 M como récord |
| Variables | `prec_*` y `sm_rootzone_anom_z` altos en abr–jun; `sup_sembrada_ac` muy baja en el noroeste; CDL con barbecho o sin cultivo |
| Fuentes | NDSU, "Prevented Planting Impact in N.D. at $1.1 Billion", 2011-06-27 (abierta); NBC News / AP, "Dakotas farmers rebound after historic flood", 2012-05-12 (abierta) |

### 2011 — Inundación del río Souris en Minot

| Campo | Valor |
|---|---|
| Estado | ND |
| Condados | Ward (Minot) y el valle del Souris |
| Meses | junio; cresta récord la noche del 25 al 26 de junio |
| Efecto | 1.561,72 ft s.n.m. contra el récord de 1.558 ft de 1881. La página no da efecto agrícola |
| Variables | casi ninguna en clima local; CDL y `ratio_cosechada` de los condados ribereños |
| Fuentes | NASA Earth Observatory, "Flooding in Minot, North Dakota", 2011-06-30 (abierta) |

### 2011 — Helada temprana en Dakota del Norte

| Campo | Valor |
|---|---|
| Estado | ND |
| Región | "la mayor parte de ND" (sin condados) |
| Meses | la semana anterior al 19 de septiembre de 2011 |
| Efecto | maíz: 20 % maduro, ≈65 % en dent sin madurar, ≈15 % antes de dent. Pérdida −23 % si la helada mató hojas y tallos en dent; peso hectolítrico < 45 lb/bu antes de dent; pérdida estimada > USD 180 M (Joel Ransom) |
| Variables | `doy_primera_helada` temprano; `periodo_libre_heladas_dias` corto; `dias_tmin_le0` de sep; `rend_bu_ac` de maíz de ND |
| Fuentes | NDSU, "Corn Losses Due to Frost Could Exceed $180 Million in N.D.", 2011-09-19 (abierta) |

### 2012 — Helada de primavera en Michigan

| Campo | Valor |
|---|---|
| Estado | MI |
| Región | fruticultura, sobre todo el noroeste (Traverse City, ≈75 % de la cereza ácida del país) |
| Meses | marzo con días de 80 °F y la fruta 5,5 semanas adelantada; más de una docena de noches bajo cero entre marzo y mayo (19 heladas) |
| Efecto | > 90 % de la cereza ácida perdida, USD 210 M (PBS); USDA: MI de 157,5 M lb en 2011 a ≈5,5 M lb proyectadas (FreshPlaza). También uva, durazno y manzana |
| Variables | `anom_tmed_c` de mar muy positivo; `dias_tmin_le0` y `dias_tmin_le_m2` de abr–may; `doy_ultima_helada`. No afecta a maíz ni soja |
| Fuentes | PBS NewsHour, "Shifting Seasons Lead to Sour Year for Michigan Cherry Farmers", 2012-08-16 (abierta); FreshPlaza, "US: Tart cherry production down significantly", 2012-07-23 (abierta) |

### 2012 — Sequía en Michigan

| Campo | Valor |
|---|---|
| Estado | MI |
| Región | todo el estado; el 25 de julio se sumaron Branch, Cass, Hillsdale y St. Joseph (sur), 38 condados en total |
| Meses | sequía y calor desde marzo; 82 % del estado de anormalmente seco a sequía extrema al 25 de julio |
| Efecto | 29 de agosto: los 83 condados declarados zona de desastre primaria. Sin rendimientos con fuente abierta |
| Variables | las de 2012 en el documento base; `spi3` jul negativo; `ndvi_anom_z` y `vhi` bajos |
| Fuentes | Michigan Public, "USDA responds to spreading drought with more help for farmers", 2012-07-25 (abierta); WNMU / AP, "Michigan declared a natural disaster area", 2012-08-30 (abierta) |

### 2013 — Siembra prevenida en el norte de Dakota del Norte

| Campo | Valor |
|---|---|
| Estado | ND |
| Condados | Ward y Bottineau (> 300.000 ac cada uno); Cavalier, Renville y Towner (> 200.000 cada uno); casi todo al norte de la ruta 200 |
| Meses | primavera |
| Efecto | ≈3,75 M ac; USD 626,9 M directo, 1,6 mil M total |
| Variables | `sup_sembrada_ac` baja en esos condados; `sm_rootzone_anom_z` alto |
| Fuentes | NDSU, "Prevented-planting Impacts 3.75-million N.D. Acres", 2013-09-16 (abierta) |

### 2017 — Sequía relámpago en Dakota del Norte

| Campo | Valor |
|---|---|
| Estado | ND (con SD y MT) |
| Región | empezó en el suroeste en la primera semana de mayo; a mediados de septiembre más de la mitad de ND en sequía severa o extrema; solo el sureste (Richland y Sargent) se salvó |
| Meses | mayo a septiembre |
| Efecto | Fed de Minneapolis (proyecciones vs 2016; maíz y soja al 1-sep, el resto al 1-ago): trigo de invierno −74 %, durum −56 %, trigo de primavera −31 % (186 M bu), alfalfa −21 %, maíz −17 %, soja +1 %. Heno +70 % de precio en junio |
| Variables | `spi1` y `spi3` de may–jul muy negativos; `ndvi_anom_z` negativo; contraste con el sureste |
| Fuentes | Fed de Minneapolis, "The worst they've ever seen", 2017-11-08 (abierta); NIDIS, resumen de la sequía relámpago de 2017 (extracto) |

### 2019 — Primavera húmeda en Michigan

| Campo | Valor |
|---|---|
| Estado | MI |
| Región | todo el estado |
| Meses | abril a junio, tras 12 meses húmedos y fríos |
| Efecto | al 31 de mayo, un tercio del maíz y un cuarto de la soja sembrados: la siembra de maíz más lenta registrada y la 5.ª más lenta de soja (Farm Bureau de MI). Octubre: ≈900.000 ac sin sembrar; producción esperada maíz −9 %, soja −31 %, poroto −15 % (USDA) |
| Variables | `prec_*` de abr–may altos; `sm_rootzone_anom_z` alto; `doy_50_sembrado` tardío; `sup_sembrada_ac` baja |
| Fuentes | Michigan Public, "Many Michigan farmers are plagued with fields too wet to plant", 2019-05-31 (abierta); WCMU, "Michigan farmers face significant declines in crop production, according to USDA", 2019-10-15 (abierta) |

### 2021 — Sequía en Dakota del Norte

| Campo | Valor |
|---|---|
| Estado | ND |
| Región | todo el estado; el haying de emergencia del CRP se habilitó en todos los condados menos Richland, Sargent y Ransom (sureste) |
| Meses | octubre 2020 a marzo 2021, el período más seco registrado (NDSU Hettinger); siguió en verano. Lluvias de fines de agosto y septiembre, tarde |
| Efecto | NDSU (22-jul): oct–jun 3.er período más seco; abr–jun 14.º; junio 3.er más frío; 100 % del estado en D1, 97 % D2, 49 % D3, 8 % D4. Bismarck y Grand Forks, 3.er año hidrológico más seco. Mediados de julio: pasturas 71 % pobres o muy pobres, más de la mitad del trigo de primavera y más de dos tercios de la alfalfa pobres o muy pobres |
| Variables | `spi6` muy negativo desde el invierno; `prec_invierno_previo_mm` bajo; `ndvi_anom_z` y `vhi` bajos; `rend_bu_ac` bajo |
| Fuentes | NDSU State Climate Office, "Bi-Weekly Drought Update", 2021-07-22 (abierta, PDF); Bismarck Tribune vía InsuranceNewsNet, "2021 drought unprecedented for many North Dakota ag producers", 2021-07-19 (abierta) |

### 2022 — Primavera húmeda en Dakota del Norte

| Campo | Valor |
|---|---|
| Estado | ND |
| Región | sin detalle por condado con fuente abierta; un productor de Wahpeton (sureste) con 4 % sin sembrar |
| Meses | abril (nieve tardía) a junio; fecha final de siembra tardía de maíz: 19 de junio |
| Efecto | DTN (23-jun): maíz sembrado ≈90 % de la superficie de 2021 (≈3,4 M ac), solo 68 % emergido al 19 de junio; soja 92 % (≈6,2 M ac). Extractos de FSA: ≈2,31–2,37 M ac de siembra prevenida, casi 40 % de EE.UU. (maíz 1,19 M, trigo 0,60 M, soja 0,52 M) |
| Variables | `prec_*` de abr–may altos; `doy_50_sembrado` tardío; `sup_sembrada_ac` baja |
| Fuentes | DTN, "Stressful Planting Season Ending in Northern Plains, But Better Than Expected", 2022-06-23 (abierta); AgWeb, "North Dakota Claims Nearly 40% of 2022 Prevent Plant Acres" (403; extracto); FSA ND, 2022 Acreage Report Summary (timeout) |

Fuentes (consultadas el 2026-11-15; "abierta" = página leída; el resto, extractos del buscador o fallidas):
- [USGS, "Media Advisory: USGS Crews Measure Record Flooding in Fargo" (2019-04-05)](https://www.usgs.gov/news/media-advisory-usgs-crews-measure-record-flooding-fargo) — abierta
- [USGS, "2009 Spring floods in North Dakota, western Minnesota, and northeastern South Dakota" (SIR 2010-5225)](https://pubs.usgs.gov/publication/sir20105225) — 403
- [NDSU, "Prevented Planting Impact in N.D. at $1.1 Billion" (2011-06-27)](https://www.ag.ndsu.edu/news/newsreleases/2011/june-27-2011/prevented-planting-impact-in-n-d-at-1-1-billion) — abierta
- [NBC News / AP, "Dakotas farmers rebound after historic flood" (2012-05-12)](https://www.nbcnews.com/news/amp/wbna47400276) — abierta
- [NASA Earth Observatory, "Flooding in Minot, North Dakota" (2011-06-30)](https://earthobservatory.nasa.gov/images/51239/flooding-in-minot-north-dakota) — abierta
- [NDSU, "Corn Losses Due to Frost Could Exceed $180 Million in N.D." (2011-09-19)](https://www.ag.ndsu.edu/news/newsreleases/2011/sept-19-2011/corn-losses-due-to-frost-could-exceed-180-million-in-n-d) — abierta
- [PBS NewsHour, "Shifting Seasons Lead to Sour Year for Michigan Cherry Farmers" (2012-08-16)](https://www.pbs.org/newshour/show/a-sour-year-for-michigan-cherry-farmers) — abierta
- [FreshPlaza, "US: Tart cherry production down significantly" (2012-07-23)](https://www.freshplaza.com/north-america/article/2098881/us-tart-cherry-production-down-significantly/) — abierta
- [Michigan Public, "USDA responds to spreading drought with more help for farmers" (2012-07-25)](https://www.michiganpublic.org/environment-science/2012-07-25/usda-responds-to-spreading-drought-with-more-help-for-farmers) — abierta
- [WNMU / AP, "Michigan declared a natural disaster area" (2012-08-30)](https://www.wnmufm.org/environment/2012-08-30/michigan-declared-a-natural-disaster-area) — abierta
- [MSU Extension, "Southwest regional report on Michigan field crops – July 12, 2012"](https://canr.msu.edu/news/southwest_regional_report_on_michigan_field_crops_july_12_2012) — cargó vacía
- [NDSU, "Prevented-planting Impacts 3.75-million N.D. Acres" (2013-09-16)](https://www.ag.ndsu.edu/news/newsreleases/2013/sept-16-2013/prevented-planting-impacts-3-75-million-n-d-acres) — abierta
- [Fed de Minneapolis, "The worst they've ever seen" (2017-11-08)](https://minneapolisfed.org/article/2017/the-worst-theyve-ever-seen) — abierta
- [NIDIS, resumen ejecutivo de la sequía relámpago de 2017](https://www.drought.gov/sites/default/files/2020-10/NIDIS_LL_FlashDrought_2017_Executive_Summary_high-res_Final_0.pdf) — extracto
- [Michigan Public, "Many Michigan farmers are plagued with fields too wet to plant" (2019-05-31)](https://www.michiganpublic.org/weather/2019-05-31/many-michigan-farmers-are-plagued-with-fields-too-wet-to-plant) — abierta
- [WCMU, "Michigan farmers face significant declines in crop production, according to USDA" (2019-10-15)](https://www.wcmu.org/health-science-and-environment/2019-10-15/michigan-farmers-face-significant-declines-in-crop-production-according-to-usda) — abierta
- [Farm Progress, "Michigan governor asks for disaster designation"](https://www.farmprogress.com/farm-operations/michigan-governor-asks-for-disaster-designation) — 403
- [NDSU State Climate Office, "Bi-Weekly Drought Update" (2021-07-22)](https://www.ndsu.edu/agriculture/sites/default/files/2021-07/20_Drought%20Update%20%28July%2022%2C%202021%29.pdf) — abierta (PDF)
- [InsuranceNewsNet / Bismarck Tribune, "2021 drought unprecedented for many North Dakota ag producers" (2021-07-19)](https://insurancenewsnet.com/oarticle/parched-plains-2021-drought-unprecedented-for-many-north-dakota-ag-producers) — abierta
- [US Soy, "Ground work: 2021 North Dakota soybean yields lower than expected"](https://ussoy.org/ground-work-2021-north-dakota-soybean-yields-lower-than-expected) — devolvió la portada, no la nota
- [DTN, "Stressful Planting Season Ending in Northern Plains, But Better Than Expected" (2022-06-23)](https://www.dtnpf.com/agriculture/web/ag/crops/article/2022/06/23/stressful-planting-season-ending) — abierta
- [AgWeb, "North Dakota Claims Nearly 40% of 2022 Prevent Plant Acres"](https://www.agweb.com/news/crops/crop-production/north-dakota-claims-nearly-40-2022-prevent-plant-acres) — 403
- [USDA FSA ND, 2022 Acreage Report Summary](https://dts.fsa.usda.gov/Assets/USDA-FSA-Public/usdafiles/State-Offices/North-Dakota/pdfs/2022-Acreage-Report-Summary.pdf) — timeout

Confianza: **media**. Alta para la existencia, el estado y las fechas de los eventos con fuente abierta (ND 2009,
2011, 2013, 2017, 2021; MI 2012 y 2019). Media para las magnitudes: casi todas son proyecciones del año del evento
o estimaciones de universidades y prensa, no valores finales de NASS. Baja para ND 2022 (cifras por cultivo solo
en extractos) y para el efecto agrícola de las inundaciones del Red. ND 2019 (siembra prevenida) quedó sin fuente.

Impacto: ninguno hoy (MI y ND no están en `config/config.yaml`). Si el humano los suma en una cuarta tanda:
agregar estos eventos a los chequeos de control de calidad de `clima`, `agua`, `vegetacion` y `cultivos`, y correr
`eventos_extremos_mi_nd_rend.py` para tener los rendimientos de NASS. ML puede marcar como años raros: ND 2009,
2011, 2013, 2017, 2019, 2021 y 2022; MI 2012 y 2019. No cambia `config/` ni el esquema de ningún CSV.
