# Eventos extremos 2000–2025 en MO, WI y SD

Pregunta: ¿Qué eventos climáticos conocidos de 2000 a 2025 tienen que verse en los datos de Missouri,
Wisconsin y Dakota del Sur? Para cada uno: estado, región o condados, año y meses, tipo, señal esperada en
nuestros CSV y fuente. Sirve para el control de calidad (como T007) de la tercera tanda de estados (MO, WI y SD,
aprobada el 2026-11-15) y para que ML entienda los años raros.

Mismo formato que `docs/research/eventos_extremos.md` y `docs/research/eventos_extremos_nuevos.md`. El documento
base ya menciona a MO solo de pasada: la inundación del Missouri de 2011 (con KS y MO entre paréntesis) y el
calor de julio de 2011 ("desde el oeste de MO"). Acá no se repiten.

**Rendimientos finales de NASS.** Todas las cifras "NASS" de este documento salen de la base completa de Quick
Stats (`qs.crops_20261114.txt.gz`, SURVEY, nivel estado, ALL PRODUCTION PRACTICES, año completo) con
`docs/research/eventos_extremos_mo_wi_sd_rend.py`. La salida está en `docs/research/eventos_extremos_mo_wi_sd_rend.csv`
(2000–2025, maíz para grano, soja y trigo de invierno, con la media de los 5 años anteriores). La media de 5 años
es una referencia simple, **no** una tendencia.

Respuesta corta:

| Año | Evento | Estado | Región | Meses | Tipo | Efecto conocido | Señal esperada en nuestros CSV |
|---|---|---|---|---|---|---|---|
| 2002 | Sequía (solo NASS) | SD | sin dato | sin dato | sequía | NASS: maíz 95 bu/ac (−14 % vs 5 años), trigo de invierno 30 (−23 %), soja 31 (−12 %) | `spi3`/`spi6` negativos; `rend_bu_ac` de SD bajo |
| 2006 | Sequía en el centro de SD | SD | centro y centro-norte | verano | sequía | NASS: maíz 97 bu/ac (−14 %), trigo de invierno 36 (−7 %) | `spi3` jun–ago negativo; `prec_temporada_mm` bajo; `rend_bu_ac` de maíz de SD |
| 2007 | Helada de Pascua | MO | todo el estado; maíz del sureste (Bootheel) y trigo del sur, los más dañados | fin de mar cálido; 4 días de helada a principios de abr | helada tardía | ≥ USD 400 M; trigo esperado −20 a −30 %. NASS: trigo de invierno 43 bu/ac (−19 %) | `anom_tmed_c` de mar positivo; `dias_tmin_le0` y `dias_tmin_le_m2` de abr; `doy_ultima_helada` tardío; `rend_bu_ac` de trigo de MO |
| 2008 | Inundaciones de junio | WI | sur (ríos Baraboo, Kickapoo, Crawfish, Rock); Dodge y Jefferson | 7–21 jun | inundación | récords en 21 estaciones del USGS. NASS: soja 35 bu/ac (−8 %); maíz 137 (−1 %) | `prec_max5d_mm` y `dias_lluvia_gt50` de jun; `sm_rootzone_anom_z` alto; `ratio_cosechada` en el sur de WI |
| 2011 | Voladura del dique de Birds Point | MO | condado de Mississippi (Bootheel) | 2–3 may, agua ≥ 6 semanas | inundación (intencional, río Mississippi) | ≈130.000 ac de campo inundados (cifra de prensa); trigo y maíz ya sembrados | `ratio_cosechada` y superficie sembrada del condado 29133; CDL con agua o sin cultivo en 2011. **No** se ve en la lluvia local |
| 2011 | Inundación del río Missouri | SD | Pierre y Fort Pierre (Hughes y Stanley), condado de Lyman, Dakota Dunes (Union) | jun–sep | inundación (descargas de las represas) | daño sobre todo urbano e infraestructura; sin cifra de campos de SD | casi nada en clima local; tierras ribereñas en el CDL; no mueve el rendimiento estatal (NASS maíz 132, +4 %) |
| 2012 | Sequía | MO | todo el estado salvo el sureste regado | jun–ago | sequía y calor | NASS: maíz 75 bu/ac (−44 %), soja 30 (−24 %). MU: 7 de 8 regiones con pérdida > 40 %; sureste −9 % (riego) | `spi3` jul muy negativo; `dias_tmax_gt35`; `vhi` y `ndvi_anom_z` bajos; `rend_bu_ac` de MO, con el sureste (Bootheel) normal |
| 2012 | Sequía | SD | todo el estado | jun–ago | sequía y calor | NASS: maíz 101 bu/ac (−25 %; 132 en 2011), soja 30,5 (−21 %) | igual que MO |
| 2012 | Sequía | WI | sur y centro | jun–ago | sequía y calor | NASS: maíz 120 bu/ac (−19 %); soja casi normal (42, −1 %) | `spi3` jul negativo en el sur; `rend_bu_ac` de maíz de WI |
| 2017 | Sequía relámpago de las Grandes Llanuras del norte | SD | peor al oeste del río Missouri | may–oct | sequía relámpago | Fed de Minneapolis: trigo de invierno −61 %, de primavera −32 %, maíz −16 %, soja −6 % (proyecciones vs 2016). NASS: trigo de invierno 40 bu/ac (−19 %); maíz 145 (+3 %) | `spi1`/`spi3` de may–jul muy negativos en el oeste; `ndvi_anom_z` negativo; `rend_bu_ac` de trigo; el maíz del este casi no se mueve |
| 2018 | Sequía en el norte de Missouri | MO | condados al norte del río Missouri; el suroeste después | verano | sequía | 72 % del estado en D1, 17 % en D3; heno 5,2 M t (el menor desde 1988). NASS: maíz 140 bu/ac (−12 %); soja normal | `spi3` jun–ago negativo en el norte de MO; `rend_bu_ac` de maíz del norte; contraste norte–sur |
| 2019 | Inundación del río Missouri en el noroeste de MO | MO | Atchison y Holt | mar a otoño (partes bajo agua hasta 8 meses) | inundación (diques rotos) | siembra prevenida: Atchison 55.971 ac (18 % del área agrícola), Holt ≈60.000 (extracto). Sin efecto en el rendimiento estatal (NASS maíz 155, −3 %) | `prec_*` de mar; `sm_rootzone_anom_z` alto; `ratio_cosechada` y superficie sembrada bajas en 29005 y 29087; CDL con agua o barbecho |
| 2019 | Siembra prevenida récord (primavera húmeda) | SD | este; peor en el sureste y noreste | mar–jun; otra inundación a mediados de sep | exceso de agua | 3,9 M ac de siembra prevenida, la mayor de los estados (2,9 M de maíz, 867 mil de soja). NASS: maíz 144 bu/ac (−7 %) | `prec_*` de abr–jun altos; `sm_rootzone_anom_z` alto; `doy_50_sembrado` tardío; `sup_sembrada_ac` muy baja (más que el rendimiento) |
| 2019 | Primavera húmeda y fría | WI | todo el estado | abr–jun | exceso de agua | maíz sembrado 96 % recién el 30 de jun, 3 semanas tarde (extracto). NASS: maíz 166 bu/ac (−2 %); trigo de invierno 64 (−10 %) | `prec_*` de may altos; `doy_50_sembrado` tardío; `sup_sembrada_ac` baja |
| 2021 | Sequía en SD | SD | peor al oeste del río Missouri y en el norte (Edmunds, Campbell) | verano | sequía y calor | gira de DTN (ago): maíz 142,7 bu/ac (−19 vs 2020). NASS: maíz 134 (−13 %), soja 40 (−12 %), trigo de invierno 38 (−26 %) | `spi3` jun–ago negativo; `ndvi_anom_z`; gradiente sureste (bien) – norte (mal) |
| 2023 | Sequía de mayo–junio | WI | casi todo el estado, muy desparejo | may–jul | sequía | tercer mayo–junio más seco (3,5 pulgadas, 46 % de lo normal). NASS: maíz 176 bu/ac (+1 %), soja 51 (0 %) | `spi1`/`spi3` de may–jun negativos; **sin** caída del rendimiento estatal |

Lo que **no** encontré con fuente, o no busqué:
- **Heladas en WI y SD.** No encontré ni busqué heladas tempranas o tardías propias de esos estados. La única
  helada con fuente es la de 2007 en MO. La helada temprana de 2004 en MN (`eventos_extremos_nuevos.md`) puede
  haber alcanzado el norte de WI, pero no lo verifiqué.
- **Olas de calor propias de estos estados:** solo el calor de 2012 (dentro de la sequía) y el de julio de 2011,
  que ya está en el documento base. No busqué otras.
- **SD 2002 y SD 2022:** la caída del rendimiento sale de NASS (2002: maíz −14 %, trigo −23 %; 2022: maíz −11 %,
  soja −12 %), pero no abrí ninguna fuente sobre el evento. Los dejo como "años raros" sin descripción.
- **SD 2006:** solo extractos del buscador (comunicado del gobernador Rounds y del climatólogo estatal). La
  página del gobernador dio 404. La caída del rendimiento sí está en NASS.
- **MO 2019:** las cifras de Atchison y Holt son extractos (la página de MU Extension dio 403 y la de Farms.com
  404). Hay un memo de RMA sobre diques rotos en MO (30-9-2019) que no abrí.
- **WI 2012 y 2019:** las fuentes de prensa dieron 403 o 404; el rendimiento es de NASS.
- **Superficie inundada de Birds Point (130.000 ac):** solo prensa (extracto); la nota que abrí no da el total.
- **Superficie de campo afectada en SD en 2011:** no la encontré. El "más de 1 millón de acres" que aparece en
  el resumen del NWS es de la inundación de **junio de 1984**, no de 2011.
- **Siembra prevenida de MO y WI en 2019 por estado:** no la encontré con fuente. Sale de los datos de FSA de
  `docs/research/siembra_prevenida.md`.

Detalle:

**Cómo usarlo.** Igual que el documento base: si un CSV procesado *no* muestra la señal esperada en el año, el
estado y los meses del evento, hay que revisar el proceso. Un valor extremo en un año sin evento listado no es un
error por sí mismo.

**Advertencias:**
- **Tercera tanda:** MO, WI y SD están en `config/config.yaml` desde el 2026-11-15, pero el CLAUDE.md todavía
  habla de 7 estados.
- **Las inundaciones de río (MO 2011 y 2019, SD 2011) no se ven en la lluvia del condado:** en Birds Point y en
  el Missouri el agua vino de río arriba (y en 2011 de las represas). La señal está en `ratio_cosechada`, en la
  superficie sembrada y en el CDL, no en `prec_*`. En 2019 sí hubo lluvia y nieve locales en marzo.
- **Siembra prevenida (SD 2019, WI 2019, MO 2019):** NASS da el rendimiento por acre cosechado, así que lo que se
  pierde se ve en `sup_sembrada_ac`, no en `rend_bu_ac`. En SD el rendimiento del maíz bajó solo 7 %.
- **Sureste de MO (Bootheel):** tiene mucho riego. En 2012 la pérdida fue de 9 % contra más de 40 % en el resto
  (MU). El promedio estatal mezcla los dos, como pasa en NE y KS.
- **SD 2017 y 2021:** el daño fue al oeste del río Missouri (pasturas y trigo). El maíz y la soja están sobre
  todo en el este, que recibió más lluvia: el rendimiento estatal de maíz casi no se movió en 2017.
- **WI 2023:** la sequía fue fuerte en mayo y junio, pero el rendimiento estatal salió normal. Es un buen caso
  para ver que una anomalía climática no siempre baja el rendimiento.
- **MO 2007:** el maíz del Bootheel se resembró en parte. La caída de 2007 está en el trigo (−19 %), no en el maíz
  (140 bu/ac, +12 %).

### 2007 — Helada de Pascua en Missouri

| Campo | Valor |
|---|---|
| Estado | MO (todo el estado con declaración federal de desastre) |
| Región | maíz del sureste (Bootheel), sembrado antes; trigo del sur, más avanzado. El norte sufrió menos (extractos) |
| Meses | fines de marzo muy cálidos; cuatro días seguidos de helada fuerte a principios de abril (≈7 de abril) |
| Efecto | al menos USD 400 M en el agro (climatólogo estatal Pat Guinan); trigo de invierno −20 a −30 % esperado; frutales y viñedos casi perdidos; alfalfa y pasturas de estación fría dañadas. NASS: trigo de invierno 43 bu/ac (−19 % vs 5 años); maíz 140 (+12 %) |
| Variables | `anom_tmed_c` de mar positivo; `dias_tmin_le0` y `dias_tmin_le_m2` de abr; `doy_ultima_helada` tardío; `rend_bu_ac` de trigo de MO |
| Fuentes | Missourinet, "Hard freeze in April hit Missouri agriculture hard", 2007-07-10 (abierta); Southeast Missourian, "Easter freeze cost Missouri agriculture at least $400 million" (403; extracto) |

### 2008 — Inundaciones de junio en el sur de Wisconsin

| Campo | Valor |
|---|---|
| Estado | WI |
| Región | sur: ríos Baraboo, Kickapoo, Crawfish y Rock; Reedsburg, Gays Mills, Jefferson, Fort Atkinson, Janesville y Beloit. Condados de Dodge (> 45.000 ac dañados) y Jefferson (≈51.000 ac de maíz y soja perdidos) según extractos |
| Meses | 7 a 21 de junio, sobre suelos saturados por las inundaciones de agosto de 2007 y > 100 pulgadas de nieve en el invierno 2007–08 |
| Efecto | récords de altura y caudal en 21 estaciones del USGS; 30 condados en emergencia estatal (extractos de NASS Wisconsin). NASS: soja 35 bu/ac (−8 %); maíz 137 (−1 %) |
| Variables | `prec_max5d_mm` y `dias_lluvia_gt50` de jun; `sm_rootzone_anom_z` alto; `ratio_cosechada` en el sur de WI |
| Fuentes | USGS, "Flood of June 2008 in Southern Wisconsin" (SIR 2008-5235; abierta); NASS Wisconsin, Crop Progress 2008-06-23 (404; extracto); eFeedLink 2008-07-29 (extracto) |

### 2011 — Voladura del dique de Birds Point (Missouri)

| Campo | Valor |
|---|---|
| Estado | MO |
| Condados | Mississippi (29133), en el floodway Birds Point–New Madrid |
| Meses | voladura la noche del 2 al 3 de mayo de 2011, para bajar el río en Cairo (IL); un productor esperaba ≥ 6 semanas de agua |
| Efecto | ≈130.000 ac de campo inundados (cifra repetida por la prensa; extracto). Había trigo y maíz sembrados; parte del maíz no se podría sembrar a tiempo |
| Variables | `ratio_cosechada`, `sup_sembrada_ac` del condado 29133 en 2011; CDL de 2011 con agua o sin cultivo en el floodway |
| Fuentes | St. Louis Public Radio, "Mississippi Co. farmers brace for the worst after levee detonation", 2011-05-03 (abierta) |

### 2011 — Inundación del río Missouri en Dakota del Sur

| Campo | Valor |
|---|---|
| Estado | SD (también NE, IA y MO, ya en el documento base) |
| Condados | Pierre (Hughes) y Fort Pierre (Stanley): ≈3.000 evacuados el 1 de junio; Lyman; Dakota Dunes (Union) |
| Meses | evacuaciones desde el 1 de junio, pico ≈21 de junio, agua alta hasta septiembre |
| Efecto | Pierre USD 13–15 M, Fort Pierre USD 5–10 M, Dakota Dunes ≈USD 25 M; 140 sitios de rutas. No encontré superficie de campo afectada en SD. NASS: maíz 132 bu/ac (+4 %), sin efecto estatal |
| Variables | casi ninguna en clima local; CDL ribereño; `ratio_cosechada` de los condados del río |
| Fuentes | NWS, "South Dakota Flood Events" (abierta); Fed de Minneapolis, "After the flood", 2011-10-14 (abierta) |

### 2012 — Sequía en MO, SD y WI

| Campo | Valor |
|---|---|
| Estados | MO, SD, WI |
| Región | MO: todo menos el sureste regado (MU por región: NO −48 %, NC −60 %, NE −62 %, O −65 %, C −56 %, E −46 %, SO −44 %, SE −9 % vs tendencia). SD y WI: sin detalle por región con fuente abierta |
| Meses | junio a agosto |
| Efecto (NASS) | MO: maíz 75 bu/ac (−44 % vs 5 años; 114 en 2011), soja 30 (−24 %). SD: maíz 101 (−25 %; 132 en 2011), soja 30,5 (−21 %); 7.ª cosecha de maíz más grande igual, por la superficie (SD Corn). WI: maíz 120 (−19 %), soja 42 (−1 %) |
| Variables | las de 2012 en el documento base; en MO, contraste del sureste (Bootheel) con el resto |
| Fuentes | MU IPM, Wiebold, "Comparison of the 2012 drought to other droughts for yield reductions", 2012-10-02 (abierta); SD Corn, "South Dakota produces 7th largest corn crop" (abierta, ≈2013-01-11) |

### 2017 — Sequía relámpago en Dakota del Sur

| Campo | Valor |
|---|---|
| Estado | SD (con ND y MT) |
| Región | peor al oeste del río Missouri; el este (maíz y soja) recibió más lluvia |
| Meses | empezó en mayo; a fines de octubre casi todo SD seguía en sequía |
| Efecto | Fed de Minneapolis (proyecciones vs 2016): trigo de invierno −61 %, de primavera −32 %, maíz −16 %, soja −6 %, alfalfa −13 %. NASS: trigo de invierno 40 bu/ac (−19 % vs 5 años); maíz 145 (+3 %); soja 43 (+2 %) |
| Variables | `spi1` y `spi3` de may–jul muy negativos al oeste; `ndvi_anom_z` negativo; `rend_bu_ac` de trigo de SD |
| Fuentes | Fed de Minneapolis, "The worst they've ever seen", 2017-11-08 (abierta); NIDIS, informe de la sequía relámpago de 2017 (extracto) |

### 2018 — Sequía en el norte de Missouri

| Campo | Valor |
|---|---|
| Estado | MO |
| Región | condados del norte (al norte del río Missouri), los primeros y más afectados; el suroeste después; el centro-este de los Ozarks, casi normal |
| Meses | verano |
| Efecto | 72 % del estado en D1 y 17 % en D3 (en 2012, 90 % en D3–D4); heno 5,2 M t, el menor desde 1988; 72 % de las pasturas malas o muy malas. NASS: maíz 140 bu/ac (−12 %); soja 44,5 (+1 %) |
| Variables | `spi3` jun–ago negativo en el norte de MO; `rend_bu_ac` de maíz por condado del norte; `ndvi_anom_z` en pasturas |
| Fuentes | High Plains Journal / MU Extension, "2018 drought differs from 2012 in varied impact, says MU economist", 2018-09-02 (abierta) |

### 2019 — Inundación del Missouri en el noroeste de Missouri

| Campo | Valor |
|---|---|
| Estado | MO |
| Condados | Atchison (29005) y Holt (29087) |
| Meses | desde mediados de marzo; partes de Atchison bajo agua 8 meses |
| Efecto | Atchison: 55.971 ac de siembra prevenida (18 % del área agrícola), 14 a 19 roturas de dique según la fuente, 85.000 ac bajo agua en el pico; Holt: ≈60.000 ac de siembra prevenida; MO 4.º estado en siembra prevenida (todo extracto). NASS: maíz 155 bu/ac (−3 %) |
| Variables | `ratio_cosechada` y `sup_sembrada_ac` de 29005 y 29087; CDL con agua o barbecho; `sm_rootzone_anom_z` alto en primavera |
| Fuentes | MU Extension, "After the deluge" (403; extracto); Farms.com, "Continued flooding keeps NW MO farmland underwater" (404; extracto); USDA RMA, "Actuarial rates resulting from breached levees in Missouri", 2019-09-30 (no abierta) |

### 2019 — Siembra prevenida récord en Dakota del Sur

| Campo | Valor |
|---|---|
| Estado | SD |
| Región | este (Ethan, Gayville, Volga); el detalle por condado está en FSA (ver `siembra_prevenida.md`) |
| Meses | primavera; segunda inundación a mediados de septiembre con casi un pie de lluvia en partes del este |
| Efecto | 3,9 M ac de siembra prevenida, el estado con más (maíz > 2,9 M, soja 867 mil); casi 20 M ac en EE.UU. (Farm Bureau, con datos de FSA de agosto). UPI: "casi 4 millones" según USDA. NASS: maíz 144 bu/ac (−7 %), soja 42,5 (−7 %) |
| Variables | `prec_*` de abr–jun altos; `sm_rootzone_anom_z` alto; `doy_50_sembrado` tardío; `sup_sembrada_ac` muy baja; `prec_max5d_mm` de sep |
| Fuentes | American Farm Bureau, "Prevent plantings set record in 2019 at 20 million acres" (abierta); UPI, "South Dakota farmers reeling from year's second record-breaking flood", 2019-09-17 (abierta) |

### 2019 — Primavera húmeda en Wisconsin

| Campo | Valor |
|---|---|
| Estado | WI |
| Región | todo el estado |
| Meses | abril a junio; cosecha también atrasada |
| Efecto | maíz sembrado 96 % recién el 30 de junio, 18 días detrás de 2018 y 3 semanas detrás del promedio; récord de superficie sin sembrar a la fecha del seguro (extractos de NASS Wisconsin y WPR). NASS: maíz 166 bu/ac (−2 %); trigo de invierno 64 (−10 %) |
| Variables | `prec_*` de may altos; `doy_50_sembrado` tardío; `sup_sembrada_ac` baja |
| Fuentes | NASS Wisconsin, Annual Crop Progress 2019 (404; extracto); WPR, "After challenging year, 2019 stakes are high for 2020 crops" (extracto) |

### 2021 — Sequía en Dakota del Sur

| Campo | Valor |
|---|---|
| Estado | SD |
| Condados | casi nada bien al oeste del río Missouri; al este, Edmunds 81 bu/ac de maíz y Hamlin 185,5 (proyecciones); soja: Campbell 31,3, Union 55,9 |
| Meses | verano |
| Efecto | gira digital de DTN (9 de agosto): maíz 142,7 bu/ac (−19,3 vs 2020), soja 44,6. NASS: maíz 134 (−13 %), soja 40 (−12 %), trigo de invierno 38 (−26 %) |
| Variables | `spi3` jun–ago negativo; `ndvi_anom_z` negativo en el norte y oeste; gradiente sureste–norte en `rend_bu_ac` por condado |
| Fuentes | DTN, "2021 DTN Digital Yield Tour – Day 1", 2021-08-09 (abierta) |

### 2023 — Sequía de primavera en Wisconsin

| Campo | Valor |
|---|---|
| Estado | WI |
| Región | casi todo el estado, desparejo (tormentas locales); algunos condados con designación de desastre del USDA (sin lista) |
| Meses | desde mayo; peor a fines de julio que en junio; floración del maíz afectada |
| Efecto | 3.er mayo–junio más seco: 3,5 pulgadas, 46 % de lo normal (solo 2005 y 2012 tan secos desde 2000); Arlington ≈11 pulgadas desde el 1 de abril. NASS: maíz 176 bu/ac (+1 %), soja 51 (0 %), trigo de invierno 76 (+6 %) |
| Variables | `spi1` y `spi3` de may–jun negativos; `deficit_mm` de jun; **sin** caída del rendimiento estatal |
| Fuentes | UW–Madison Extension, "Wisconsin drought resources for 2023, episode 2" (resumen del webinar del 2023-07-28; abierta) |

### SD 2002, 2006 y 2022 — años raros solo en NASS

| Año | NASS (vs media de 5 años) | Fuente del evento |
|---|---|---|
| 2002 | maíz 95 (−14 %), soja 31 (−12 %), trigo de invierno 30 (−23 %) | no busqué |
| 2006 | maíz 97 (−14 %), trigo de invierno 36 (−7 %); soja 34 (+7 %) | extractos: comunicado del gobernador Rounds (trigo del centro y centro-norte perdido; un condado con 589 productores con pérdidas de 90–100 %) y el climatólogo estatal Dennis Todey ("peor que el Dust Bowl" en algunas zonas). Página del gobernador: 404 |
| 2022 | maíz 132 (−11 %), soja 38 (−12 %) | no busqué |

Fuentes (consultadas el 2026-11-15; "abierta" = página leída; el resto, extractos del buscador):
- [USDA NASS Quick Stats, base completa `qs.crops_20261114.txt.gz`](https://www.nass.usda.gov/datasets/) — leída con `eventos_extremos_mo_wi_sd_rend.py`
- [Missourinet, "Hard freeze in April hit Missouri agriculture hard" (2007-07-10)](https://www.missourinet.com/2007/07/10/hard-freeze-in-april-hit-missouri-agriculture-hard/) — abierta
- [Southeast Missourian, "Easter freeze cost Missouri agriculture at least $400 million"](https://www.semissourian.com/news/easter-freeze-cost-missouri-agriculture-at-least-400-million-1222299) — 403
- [USGS, "Flood of June 2008 in Southern Wisconsin"](https://www.usgs.gov/publications/flood-june-2008-southern-wisconsin) — abierta
- [NASS Wisconsin, Crop Progress 2008-06-23](https://data.nass.usda.gov/Statistics_by_State/Wisconsin/Publications/Crop_Progress_&_Condition/2008/cw0623.pdf) — 404
- [eFeedLink, 2008-07-29](https://www.efeedlink.com/contents/07-29-2008/c3d9f5cc-3e51-4079-a4f3-2eb1891cc6ed-a181.html)
- [St. Louis Public Radio, "Mississippi Co. farmers brace for the worst after levee detonation" (2011-05-03)](https://www.stlpr.org/health-science-environment/2011-05-03/mississippi-co-farmers-brace-for-the-worst-after-levee-detonation) — abierta
- [NWS, "South Dakota Flood Events"](https://weather.gov/safety/flood-states-sd) — abierta
- [Fed de Minneapolis, "After the flood" (2011-10-14)](https://www.minneapolisfed.org/article/2011/after-the-flood-20111014) — abierta
- [MU IPM, Wiebold, "Comparison of the 2012 drought to other droughts for yield reductions" (2012-10-02)](https://ipm.missouri.edu/croppest/2012/10/Comparison-of-the-2012-Drought-to-other-Droughts-for-Yield-Reductions/index.cfm) — abierta
- [SD Corn, "South Dakota produces 7th largest corn crop"](https://www.sdcorn.org/news/south-dakota-produces-7th-largest-corn-crop) — abierta
- [The Monroe Times, "Yields shine brightly for area farmers"](https://themonroetimes.com/local-news/yields-shine-brightly-for-area-farmers) — 403
- [Fed de Minneapolis, "The worst they've ever seen" (2017-11-08)](https://minneapolisfed.org/article/2017/the-worst-theyve-ever-seen) — abierta
- [NIDIS, resumen ejecutivo de la sequía relámpago de 2017](https://www.drought.gov/sites/default/files/2020-10/NIDIS_LL_FlashDrought_2017_Executive_Summary_high-res_Final_0.pdf)
- [High Plains Journal / MU Extension, "2018 drought differs from 2012 in varied impact" (2018-09-02)](https://hpj.com/?p=38057) — abierta
- [MU Extension, "After the deluge"](https://extension.missouri.edu/news/after-the-deluge) — 403
- [Farms.com, "Continued flooding keeps NW MO farmland underwater"](https://farms.com/news/continued-flooding-keeps-nw-mo-farmland-underwater-151109.aspx) — 404
- [USDA RMA, "Actuarial rates resulting from breached levees in Missouri" (2019-09-30)](https://www.rma.usda.gov/sites/default/files/underwriting-guidelines/Actuarial-Rates-Resulting-from-Breached-Levees-in-Missouri-9-30-2019.pdf) — no abierta
- [American Farm Bureau, "Prevent plantings set record in 2019 at 20 million acres"](https://www.fb.org/market-intel/prevent-plantings-set-record-in-2019-at-20-million-acres) — abierta
- [UPI, "South Dakota farmers reeling from year's second record-breaking flood" (2019-09-17)](https://www.upi.com/Top_News/US/2019/09/17/South-Dakota-farmers-reeling-from-years-second-record-breaking-flood/1861568739212/) — abierta
- [NASS Wisconsin, Annual Crop Progress 2019](https://nass.usda.gov/Statistics_by_State/Wisconsin/Publications/Crop_Progress_&_Condition/2019/WI-Annual-Crop-Progress-2019.pdf) — 404
- [WPR, "After challenging year, 2019 stakes are high for 2020 crops"](https://wpr.org/after-challenging-year-2019-stakes-are-high-2020-crops)
- [DTN, "2021 DTN Digital Yield Tour – Day 1" (2021-08-09)](https://www.dtnpf.com/agriculture/web/ag/crops/article/2021/08/09/drought-drags-production-dakotas) — abierta
- [UW–Madison Extension, "Wisconsin drought resources for 2023, episode 2"](https://cropsandsoils.extension.wisc.edu/articles/wisconsin-drought-resources-for-2023-episode-2) — abierta
- [Vote Smart, comunicado del gobernador Rounds sobre la sequía de 2006](https://votesmart.org/public-statement/198196/gov-rounds-proposes-science-based-drought-assistance-at-field-hearing-on-2007-farm-bill) — 404

Confianza: **media**. Alta para los rendimientos (valores finales de NASS leídos de la base completa) y para la
existencia, el estado y las fechas de los eventos con fuente abierta (MO 2007, 2011, 2012 y 2018; WI 2008 y 2023;
SD 2011, 2012, 2017, 2019 y 2021). Baja para MO 2019, WI 2012 y 2019 y SD 2006: solo extractos del buscador. Las
superficies afectadas por condado (Atchison, Holt, Dodge, Jefferson, Birds Point) son de prensa, no oficiales.

Impacto: control de calidad de `clima`, `agua`, `vegetacion` y `cultivos` en MO, WI y SD (como T007): sumar estos
eventos a la lista de chequeos. ML puede marcar como años raros: MO 2007 (trigo), 2012 y
2018; WI 2008, 2012 y 2019; SD 2002, 2006, 2012, 2017 (trigo), 2019, 2021 y 2022. No cambia `config/` ni el
esquema de ningún CSV.
