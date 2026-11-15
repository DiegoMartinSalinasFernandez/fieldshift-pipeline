# Eventos extremos 2000–2025 en KY

Pregunta: ¿Qué eventos climáticos conocidos de 2000 a 2025 tienen que verse en los datos de Kentucky? Para cada
uno: región o condados, año y meses, tipo, señal esperada en nuestros CSV y fuente. Sirve para que el humano
decida una cuarta tanda de estados (`docs/research/cuarta_tanda.md`) y, si KY entra, para el control de calidad.

Mismo formato que `docs/research/eventos_extremos_mi_nd.md`. **KY no está en `config/config.yaml`**: nada de esto
cambia el pipeline hoy.

**Sin rendimientos de NASS calculados.** La máquina no tiene la base completa de Quick Stats y la tarea pide no
bajar datasets grandes. Las cifras de rendimiento de abajo son las que publican las fuentes citadas (AP con datos
de NASS, la Universidad de Kentucky). Para tener la serie completa, basta con sumar `KY` a `ESTADOS` en
`docs/research/eventos_extremos_rend_estado.py` y correrlo en una máquina que tenga `qs.crops_<fecha>.txt.gz`.

Respuesta corta:

| Año | Evento | Región | Meses | Tipo | Efecto conocido | Señal esperada en nuestros CSV |
|---|---|---|---|---|---|---|
| 2007 | Helada tardía de abril | todo el estado (trigo); daño desparejo | 6–9 abr (extracto) | helada tardía | trigo: de ≈360.000 ac que se esperaba cosechar para grano se cosecharon ≈240.000; rindes de 30 a 70 bu/ac; promedio estatal 48 bu/ac (UK) | `dias_tmin_le0` y `dias_tmin_le_m2` de abr; `doy_ultima_helada` tardío; `sup_cosechada_ac` y `ratio_cosechada` de trigo de invierno muy bajos; `rend_bu_ac` de trigo bajo |
| 2007 | Sequía | todo el estado; maíz peor en el sur | feb – oct; peor may–ago | sequía y calor | el 3.er may–ago más seco en 113 años; maíz del sur ≈−40 % (agosto); en octubre, soja 53 % y pasturas 82 % pobres o muy pobres; zona de desastre del USDA | `spi3` y `spi6` de jul–ago muy negativos; `deficit_temporada_mm`; `vhi` y `ndvi_anom_z` bajos; `rend_bu_ac` de maíz y soja bajo |
| 2011 | Lluvias de abril e inundación del Ohio y del Misisipi | oeste (Purchase y Pennyrile; Paducah, Hickman, Mayfield) | 22 abr – 2 may; crestas a principios de mayo | lluvia extrema e inundación de río | Paducah: 15,91 in en abril, el mes más lluvioso registrado; crestas récord del Ohio en Cairo (IL); en Paducah la 2.ª más alta. Sin cifra agrícola de KY | `prec_*` de abr muy altos; `prec_max5d_mm` de abr–may; `sm_rootzone_anom_z` alto; `doy_50_sembrado` tardío; CDL y `ratio_cosechada` en condados ribereños |
| 2012 | Sequía | todo el estado; extrema en el oeste | abr – ago; peor jul–ago | sequía | maíz 77 % pobre o muy pobre (15-jul); rinde estatal 68 bu/ac, 71 menos que en 2011; Graves ≈50 bu/ac; Henderson 80–110 contra 156 normales; soja y tabaco se recuperaron con lluvias de fines de verano | `spi1`/`spi3` muy negativos en jun–jul; `prec_jul_mm` bajo; `vhi` y `ndvi_anom_z` bajos; `rend_bu_ac` de maíz el más bajo del período |
| 2012 | Ola de calor | todo el estado | 28 jun – 15 jul | calor extremo | Paducah: 108 °F el 29-jun (iguala el récord absoluto), julio el mes más cálido registrado (84,5 °F de media), 18 días ≥ 100 °F (récord); Bowling Green 110 °F; 2.º año más cálido para KY | `dias_tmax_gt35` y `tmax_jul_c` altos; `anom_tmed_c` positivo; `lst_dia_c` alto; calor en la floración del maíz (`dias_tmax_gt30_jul`) |
| 2012 | Helada de primavera en el trigo | estado (sin región en la fuente) | primavera | helada tardía | trigo 63 bu/ac de promedio estatal, bajo por una helada (UK, 2017) | `rend_bu_ac` de trigo de invierno bajo; ver advertencia sobre 2012 |
| 2019 | Año muy húmedo e inundación larga del Ohio | oeste (Paducah) | Ohio feb–jul (récord de duración en Cairo); Misisipi mar–ago; sequía relámpago fines de ago – principios de oct | exceso de agua, después sequía relámpago | entre los 6 años más lluviosos en las 3 estaciones de NWS Paducah. Sin cifra agrícola de KY | `prec_*` altos en el invierno y la primavera; `sm_rootzone_anom_z` alto; `doy_50_sembrado` tardío; `spi1` de sep negativo |
| 2021 | Inundación repentina del 28 de febrero | sur del oeste: Fulton, Murray (Calloway), Hopkinsville (Christian), Elkton (Todd), Graves | 28 feb – 1 mar | lluvia extrema | 4–7 in en el corredor; emergencia por inundación repentina en Todd; el 1-mar, 16 puntos de ríos con alerta (Green, Ohio y otros). Año: sur del Pennyrile 6–12 in sobre lo normal; Mayfield 61,70 in | `prec_max1d_mm` y `prec_invierno_previo_mm` altos; marzo y julio húmedos, mayo y junio secos |
| 2022 | Inundación repentina del 17 de febrero | oeste: Mayfield (Graves), McCracken, Lyon, Marshall, Ballard | 17 feb | lluvia extrema | 2–5 in en pocas horas | `prec_max1d_mm` de feb; `prec_invierno_previo_mm` alto |
| 2022 | Sequía de verano | oeste, sobre todo la región de Jackson Purchase; de Fulton a Christian en sequía severa | jun – jul (alivio en agosto); otra vez en otoño | sequía | maíz proyectado 149 bu/ac, −22 % contra el récord de 2021 (NASS vía UK); ≈66 % del maíz con estrés hídrico en la floración; fines de noviembre: casi toda la región en sequía severa a extrema; ríos Ohio y Misisipi en mínimos récord | `spi1`/`spi3` de jun–jul negativos en el oeste; `prec_jul_mm` bajo; `ndvi_anom_z` bajo en el oeste y no en el este; `rend_bu_ac` de maíz bajo |

Eventos que aparecieron al buscar y no pedía la tarea (fuente abierta, menos detalle):

| Año | Evento | Región | Meses | Efecto conocido |
|---|---|---|---|---|
| 2004 | Inundaciones del Ohio | Henderson (5.000–6.000 ac) y Daviess (≈4.000 ac) | fines de may – jun (maíz perdido, resembrado con soja) y sep | soja tardía con pérdidas de 5 a 40 bu/ac |
| 2008 | Inundación del Ohio y del Misisipi | Union, Ballard, Carlisle | jun (Misisipi: cresta de 44 ft en Cairo el 22-jun) | siembra atrasada y resiembra; lotes bajos bajo agua |
| 2025 | Lluvias récord de abril | oeste, de Hickman a Hodgenville; Muhlenberg, Webster, Marshall | 1–7 abr | > 10 in en gran parte del oeste, > 15 in en Marshall, hasta 17 in en Muhlenberg; ríos Green, Mud y Pond desbordados por el remanso del Ohio; siembra de maíz y soja atrasada |

Lo que **no** encontré con fuente, o no busqué:
- **Rendimientos finales de NASS** de KY: no se calcularon (ver arriba). Los 68 bu/ac de maíz de 2012 vienen de AP
  citando a NASS; los 149 bu/ac de 2022 son una proyección de NASS, no el valor final.
- **2007, temperaturas y fechas de la helada:** los datos de 6 a 9 de abril, máximas de 27–29 °F y mínimas cerca
  de 15 °F, con el trigo en Feekes 7–10, son de un extracto del buscador (boletín del UKREC de Princeton); no lo
  abrí. El índice de documentos de la UK sobre la helada sí abrió, y su primer documento es del 6 de abril
  ("Management Options for Damaged Corn"): la helada también tocó maíz ya sembrado, sin cifras.
- **2007, efecto de la helada en la fruta y la sequía por región:** el informe de la UK sobre 2007
  (`uky.edu/Ag/research/2007/extension/martin.html`) falló por certificado TLS.
- **2011, efecto agrícola en KY:** el PDF de NWS Paducah no da cifras agrícolas. Birds Point (130.000 ac
  inundados a propósito) está en Misuri, no en KY; la página de NASA de la confluencia del Ohio y el Misisipi
  falló.
- **2021–2022, inundaciones del Ohio y del Misisipi en el oeste:** no encontré crecidas de esos ríos con fuente en
  2021 o 2022. Lo que hay son inundaciones repentinas de lluvia local (28-feb-2021 y 17-feb-2022) y, en el
  otoño de 2022, lo contrario: **niveles mínimos récord** del Ohio y del Misisipi por la sequía. El parte de
  cultivos de NASS del 18-abr-2022 dio 404 y la nota de AgWeb sobre el tornado, la sequía y la inundación de
  diciembre de 2021 dio 403.
- **El tornado EF-4 del 10–11 de diciembre de 2021** (165 millas en el oeste de KY, NWS Paducah) no es una
  variable de nuestros CSV; lo nombro porque la nota de AgWeb lo liga a pérdidas de cultivos.
- **Heladas tempranas de otoño, granizo, derechos:** no busqué.
- **2017:** la helada de marzo (mínimas cerca de 15 °F el 15 y 16 de marzo, trigo en Feekes 6–8) causó poco daño:
  promedio estatal 77 bu/ac (UK). No la incluyo como evento.

Detalle:

**Cómo usarlo.** Igual que los documentos anteriores: si un CSV procesado *no* muestra la señal esperada en el año,
la región y los meses del evento, hay que revisar el proceso. Un valor extremo en un año sin evento listado no es
un error por sí mismo.

**Advertencias:**
- **KY es un estado de trigo de invierno y soja de segunda.** En el oeste, el trigo de invierno va seguido de soja
  de segunda. Una helada de abril que mata el trigo hace que se corte para heno o silo y se resiembre con maíz o
  soja (UK, 2007). La señal está en `sup_cosechada_ac` y `ratio_cosechada` del trigo, y en la mezcla de clases del
  CDL (menos clase 26, doble trigo/soja; más maíz o soja sola), no solo en `rend_bu_ac`. NASS da el rinde por
  acre cosechado, y la UK aclara que el rinde estatal de 2007 habría sido más bajo si no se hubiera abandonado
  parte del trigo.
- **2012 tiene tres eventos:** sequía, calor y una helada de primavera en el trigo (según la UK, 2017). El maíz cae
  por la sequía y el calor en la floración; el trigo, por la helada. No confundirlos al leer `doy_ultima_helada`.
- **2007 junta la helada de abril con la sequía de verano.** Las fuentes de prensa mezclan las pérdidas de las
  dos (pasturas y forraje USD 200–500 M "por la helada y la sequía").
- **El oeste y el este se comportan distinto.** En 2012 el oeste estaba en sequía hidrológica extrema; en 2022 la
  sequía se concentró en la región de Jackson Purchase, mientras partes del Pennyrile estuvieron más húmedas de
  lo normal (20,25 in en el verano cerca de Greenville, Muhlenberg). Un promedio estatal esconde el contraste.
- **Las inundaciones de ríos grandes (2011, 2019) vienen de río arriba.** La lluvia local de abril de 2011 fue
  récord en Paducah, pero la cresta del Ohio en Cairo depende de toda la cuenca, y en 2019 la duración (feb–jul)
  importa más que la lluvia de un mes. Esperar la señal en la humedad del suelo, la fecha de siembra y el CDL de
  los condados ribereños.
- **2012 en KY no fue un mal año agropecuario en todo:** la AP (dic-2012) informa ingresos récord, y la soja y el
  tabaco se recuperaron con lluvias de fines de verano. La señal de 2012 es sobre todo de maíz.

### 2007 — Helada tardía de abril

| Campo | Valor |
|---|---|
| Región | todo el estado; daño desparejo |
| Meses | abril (6 a 9 de abril según un extracto; el índice de la UK fecha documentos del 6 al 25 de abril) |
| Efecto | se sembraron 440.000 ac de trigo y se esperaba cosechar ≈360.000 para grano; se cosecharon ≈240.000 (NASS, 29-jun). El resto se destruyó o se cortó para heno o silo y se resembró con maíz o soja. Rindes de 30 bu/ac (tallos muy dañados) a 70 (daño leve); "among the smallest in nearly three decades". Promedio estatal 48 bu/ac; las variedades en Feekes 8–9 sufrieron mucho más que las de Feekes 6–7 |
| Variables | `dias_tmin_le0` y `dias_tmin_le_m2` de abr; `doy_ultima_helada`; `sup_cosechada_ac` y `ratio_cosechada` de trigo de invierno; CDL con menos doble trigo/soja |
| Fuentes | UK College News, "Diminished Wheat Crop Harvested", 2007-07-06 (abierta); UK Grain Crops, "April Freeze Damage, 2007" (índice, abierta); Bruening y Shields, "Kentucky wheat variety testing and 2017 freeze damage", UK (abierta, PDF) |

### 2007 — Sequía

| Campo | Valor |
|---|---|
| Región | todo el estado ("severe to extreme drought"); el maíz del sur, peor |
| Meses | desde febrero; mayo a agosto, el 3.er más seco en 113 años; en octubre seguía y atrasaba la siembra del trigo |
| Efecto | agosto: maíz del sur ≈40 % bajo el promedio; ganaderos liquidando hacienda. Octubre: zona de desastre del USDA; soja 53 % pobre o muy pobre; pasturas 82 % pobres o muy pobres; pérdidas de pasturas, heno y forraje USD 200–500 M (estimación de julio, con la helada). En 2012 el estado destinó USD 8,15 M a la recuperación de la helada y la sequía de 2007 |
| Variables | `spi3` y `spi6` de jul–sep muy negativos; `deficit_temporada_mm`; `vhi` y `ndvi_anom_z` bajos; `rend_bu_ac` de maíz y soja bajo |
| Fuentes | Insurance Journal (Oficina del Gobernador), "Gov. Fletcher Requests Federal Help for Ky. Farmers", 2007-08-31 (abierta); Insurance Journal / AP, "Feds Declare Ky. a Natural Disaster Area Because of Drought", 2007-10-04 (abierta); NWS Louisville, "Top Ten Heat Events" (abierta); Smiley Pete, "Over $8 Million in Drought Relief", 2012-03-02 (abierta) |

### 2011 — Lluvias de abril e inundación del Ohio y del Misisipi

| Campo | Valor |
|---|---|
| Región | oeste: totales del 22-abr al 3-may de 17,05 in en Paducah, 14,12 en Hickman, 13,93 en Benton, 13,24 en Mayfield, 13,88 en Greenville, 12,57 en Madisonville, 11,28 en Owensboro |
| Meses | lluvias del 23-feb al 14-mar (9,43 in en Paducah) y del 22-abr al 2-may; crestas a principios de mayo |
| Efecto | Paducah: abril con 15,91 in, el abril y el mes más lluvioso registrado; primavera más lluviosa (28,24 in al 3-may). Crestas récord del Ohio en Cairo (IL), por encima de 1937; en Paducah, la 2.ª más alta. El 2 de mayo se abrió el floodway de Birds Point–New Madrid (Misuri). Las represas Kentucky y Barkley retuvieron niveles récord. Sin cifras agrícolas de KY |
| Variables | `prec_*` de abr muy altos; `prec_max5d_mm`; `sm_rootzone_anom_z` alto en abr–may; `doy_50_sembrado` tardío; CDL y `ratio_cosechada` en los condados del Ohio y el Misisipi |
| Fuentes | NWS Paducah, "April/May 2011 River Flooding" (abierta, PDF) |

### 2012 — Sequía y ola de calor

| Campo | Valor |
|---|---|
| Región | todo el estado; oeste en sequía extrema en julio y agosto. Condados con cifras: Lyon, Graves, Henderson |
| Meses | sequía desde abril; calor del 28-jun al 15-jul (del 8 al 15 de julio, 100 °F en todas las estaciones principales, según la búsqueda; NWS Louisville da el 28-jun al 8-jul) |
| Efecto | NWS Paducah: la sequía "decimated the corn crop in many areas" y llevó los ríos a mínimos récord; lluvia anual de Paducah, la 2.ª más baja. Paducah: 108 °F el 29-jun (iguala el récord absoluto de 1942), junio con 0,90 in (5.º más seco), julio el mes más cálido registrado (84,5 °F), 18 días ≥ 100 °F (récord; antes 14 en 1954) y 81 días ≥ 90 °F. Louisville 106 °F el 7-jul; Bowling Green 110 °F el 29-jun; 2.º año más cálido de KY. Maíz (semana al 15-jul): 77 % pobre o muy pobre, 90 % panojado, 76 % con estigmas; Princeton 8,45 in desde marzo, 14,39 bajo lo normal; pasturas 73 % pobres o muy pobres. Fin de julio: Graves "lucky to average 50 bushels", soja temprana −50 %; Henderson 80–110 bu/ac contra 156; se sembraron 1,6 M ac de maíz, la mayor superficie desde 1986. Diciembre: rinde estatal 68 bu/ac, 71 menos que en 2011; seguros USD 200–250 M por maíz; soja y tabaco se recuperaron |
| Variables | `spi1`/`spi3` de jun–jul muy negativos; `prec_jul_mm` bajo; `dias_tmax_gt35`, `tmax_jul_c` y `dias_tmax_gt30_jul` altos; `anom_tmed_c` positivo; `lst_dia_c` alto; `vhi` y `ndvi_anom_z` bajos; `rend_bu_ac` de maíz mínimo del período |
| Fuentes | NWS Paducah, "Top 10 of 2012" (abierta) y "2012 Record Summer Heat Wave" (abierta, PDF); NWS Louisville, "Top Ten Heat Events" (abierta); UKNow, "Kentucky Corn Crops Suffering From Drought; Vineyards Facing Challenges", 2012-07-24 (abierta); UK College News, "Drought forces farmers to rethink plans for corn crop", 2012-07-19 (abierta); Insurance Journal / AP, "Facing Paltry Yields, Kentucky Farmers Hope Insurance Will Cover Costs", 2012-07-31 (abierta); Yahoo / AP, "Record-high cash receipts expected despite drought", 2012-12-07 (abierta) |

### 2019 — Año muy húmedo en el oeste

| Campo | Valor |
|---|---|
| Región | área de NWS Paducah (oeste de KY, sur de IL, sureste de MO, suroeste de IN) |
| Meses | Ohio en inundación mayor con récord de duración en Cairo de febrero a julio; Misisipi de marzo a agosto; sequía relámpago de fines de agosto a principios de octubre (uno de los septiembres más secos) |
| Efecto | entre los 6 años más lluviosos en las 3 estaciones de NWS Paducah. Sin cifras agrícolas de KY |
| Variables | `prec_invierno_previo_mm` y `prec_*` de primavera altos; `sm_rootzone_anom_z` alto; `doy_50_sembrado` tardío; después `spi1` de sep negativo |
| Fuentes | NWS Paducah, "A review of the 10 biggest weather events in 2019" (abierta) |

### 2021 — Inundación repentina del 28 de febrero y año húmedo

| Campo | Valor |
|---|---|
| Condados | Calloway (Murray), Christian (Hopkinsville), Todd (Elkton), Fulton, Graves |
| Meses | 28 de febrero – 1 de marzo |
| Efecto | 4–7 in en el corredor (Elkton 6,60 in, Murray 5,64 in en 48 h); emergencia por inundación repentina en Todd; el South Fork Little River en Hopkinsville quedó a 0,2 ft de su récord. El 1-mar, 16 puntos con alerta de inundación de río (Green, Ohio, Wabash y otros). Año: sur del Pennyrile 6–12 in sobre lo normal; lo más lluvioso en Calloway y Graves (Mayfield 61,70 in); meses más húmedos marzo y julio; más secos mayo, junio y noviembre; diciembre, el más cálido registrado en muchas estaciones |
| Variables | `prec_max1d_mm` de feb; `prec_invierno_previo_mm` alto para el `anio` 2021; `prec_*` de mar y jul altos |
| Fuentes | NWS Paducah, "February 28, 2021 Flooding" (abierta), "2021 Annual Climate Summary" (abierta) y "A review of weather events of 2021" (abierta) |

### 2022 — Inundación repentina de febrero y sequía de verano y otoño

| Campo | Valor |
|---|---|
| Región | inundación: Graves (Mayfield), McCracken, Lyon, Marshall, Ballard, Caldwell. Sequía: Jackson Purchase; de Fulton a Christian en sequía severa a fines de julio |
| Meses | inundación 17-feb; sequía jun–jul (alivio en agosto en el oeste) y otra vez en otoño |
| Efecto | 17-feb: 2–5 in en pocas horas (Lone Oak 4,79 in, Calvert City 4,15, Eddyville 4,10). Verano: junio el mes más seco respecto de lo normal; el verano más seco desde 2012 en muchos lugares; Paducah con 31 días de índice de calor > 100 °F. 18-jul: maíz 28 % y soja 32 % pobres o muy pobres (estatal); Chad Lee (UK): "We'll probably have 25% yield in some of those fields". UK (oct): del 8-jun al 15-jul faltaron hasta 3 in; el maíz del oeste floreció a principios de julio; ≈66 % del maíz sufrió estrés hídrico en la floración; NASS proyecta 149 bu/ac, −22 % contra el récord de 2021. Fines de noviembre: casi toda la región en sequía severa a extrema; incendios en octubre; Ohio y Misisipi en mínimos récord |
| Variables | `prec_max1d_mm` de feb; `spi1`/`spi3` de jun–jul negativos en el oeste; `prec_jul_mm` bajo; `ndvi_anom_z` y `vhi` bajos en el oeste; contraste con el Pennyrile; `rend_bu_ac` de maíz bajo |
| Fuentes | NWS Paducah, "February 17, 2022, Flooding Event" (abierta), "Summer 2022 Climate Summary" (abierta) y "A Review of Weather Events of 2022" (abierta); WKMS, "Severe drought shriveling corn for some western Ky. farmers", 2022-07-24 (abierta); UK Corn & Soybean News, vol. 4, n.º 9, octubre 2022 (abierta, PDF) |

Fuentes (consultadas el 2026-11-15; "abierta" = página leída; el resto, extractos del buscador o fallidas):
- [UK College News, "Diminished Wheat Crop Harvested" (2007-07-06)](https://news.mgcafe.uky.edu/article/diminished-wheat-crop-harvested) — abierta
- [UK Grain Crops, "April Freeze Damage, 2007"](https://graincrops.mgcafe.uky.edu/april-freeze-damage-2007) — abierta (índice, sin cifras)
- [Bruening y Shields, "Kentucky wheat variety testing and 2017 freeze damage", UK](https://wheatscience.ca.uky.edu/sites/wheatscience.ca.uky.edu/files/bill_b_-_rr_2017_final_wheat_variety_testing_and_2017_freeze_damage_002.pdf) — abierta (PDF)
- [UKREC, boletín sobre la helada de 2007 (archivo de la UNT)](https://webarchive.library.unt.edu/eot2008/20081204190629/http:/www.ca.uky.edu/ukrec/newsltrs/News07freeze.pdf) — extracto
- [UK, informe de extensión 2007 (Martin)](https://uky.edu/Ag/research/2007/extension/martin.html) — falló (certificado TLS)
- [Insurance Journal, "Gov. Fletcher Requests Federal Help for Ky. Farmers" (2007-08-31)](https://www.insurancejournal.com/news/southeast/2007/08/31/83125.htm) — abierta
- [Insurance Journal / AP, "Feds Declare Ky. a Natural Disaster Area Because of Drought" (2007-10-04)](https://www.insurancejournal.com/news/southeast/2007/10/04/84013.htm) — abierta
- [Smiley Pete, "Over $8 Million in Drought Relief" (2012-03-02)](https://smileypete.com/business/2012-03-02-over-8-million-in-drought-relief/) — abierta
- [NWS Louisville, "Top Ten Heat Events"](https://www.weather.gov/lmk/top10heat) — abierta
- [NWS Paducah, "April/May 2011 River Flooding"](https://www.weather.gov/media/pah/Top10Events/2011/April%20and%20May%20flooding%202011.pdf) — abierta (PDF)
- [NASA, "Flooding at the Junction of the Mississippi and Ohio Rivers"](https://www.naturalhazards.nasa.gov/images/50475/flooding-at-the-junction-of-the-mississippi-and-ohio-rivers) — falló
- [NWS Paducah, "Top 10 of 2012"](https://www.weather.gov/pah/Top10of2012) — abierta
- [NWS Paducah, "2012 Record Summer Heat Wave"](https://www.weather.gov/media/pah/Top10Events/2012/2012%20Record%20Summer%20Heat%20Wave.pdf) — abierta (PDF)
- [UKNow, "Kentucky Corn Crops Suffering From Drought; Vineyards Facing Challenges" (2012-07-24)](https://uknow.uky.edu/campus-news/kentucky-corn-crops-suffering-drought-vineyards-facing-challenges) — abierta
- [UK College News, "Drought forces farmers to rethink plans for corn crop" (2012-07-19)](https://news.mgcafe.uky.edu/article/drought-forces-farmers-rethink-plans-corn-crop) — abierta
- [Insurance Journal / AP, "Facing Paltry Yields, Kentucky Farmers Hope Insurance Will Cover Costs" (2012-07-31)](https://amp.insurancejournal.com/news/southeast/2012/07/31/257645.htm) — abierta
- [Yahoo / AP, "Record-high cash receipts expected despite drought" (2012-12-07)](https://www.yahoo.com/news/record-high-cash-receipts-expected-153425609.html) — abierta
- [NWS Paducah, "A review of the 10 biggest weather events in 2019"](https://www.weather.gov/pah/Top10of2019) — abierta
- [NWS Paducah, "February 28, 2021 Flooding"](https://www.weather.gov/pah/Feb28_2021Flooding) — abierta
- [NWS Paducah, "2021 Annual Climate Summary"](https://www.weather.gov/pah/2021AnnualClimateSummary) — abierta
- [NWS Paducah, "A review of weather events of 2021"](https://www.weather.gov/pah/2021YearInReview) — abierta
- [AgWeb, "Tornado to Drought to Now Severe Flooding: Kentucky Farmers Face More Crop Losses from Weather Extremes"](https://www.agweb.com/news/crops/crop-production/tornado-drought-now-severe-flooding-kentucky-farmers-face-more-crop-losses-weather-extremes) — 403
- [NWS Paducah, "February 17, 2022, Flooding Event"](https://www.weather.gov/pah/2022Feb17Flooding) — abierta
- [NASS Kentucky, Crop Progress & Condition, 18-abr-2022](https://data.nass.usda.gov/Statistics_by_State/Kentucky/Publications/Crop_Progress_&_Condition/cw22/CW041822.pdf) — 404
- [NWS Paducah, "Summer 2022 Climate Summary"](https://www.weather.gov/pah/Summer2022ClimateSummary) — abierta
- [NWS Paducah, "A Review of Weather Events of 2022"](https://www.weather.gov/pah/2022YearInReview) — abierta
- [WKMS, "Severe drought shriveling corn for some western Ky. farmers" (2022-07-24)](https://www.wkms.org/agriculture/2022-07-24/severe-drought-shriveling-corn-for-some-western-ky-farmers) — abierta
- [UK Corn & Soybean News, vol. 4, n.º 9 (octubre 2022)](https://graincrops.ca.uky.edu/files/cornsoynewsletter2022_vol4_iss9_oct.pdf) — abierta (PDF)
- [UK College News, "Grain Harvest Moving Along, Ohio River Damages Some Fields" (2004-09-29)](https://news.mgcafe.uky.edu/article/grain-harvest-moving-along-ohio-river-damages-some-fields) — abierta
- [UK College News, "Rising rivers could threaten crops in western Kentucky" (2008-06-20)](https://news.mgcafe.uky.edu/article/rising-rivers-could-threaten-crops-western-kentucky-0) — abierta
- [Kentucky Farm Bureau, "Kentuckians Weathering the Storms, Once Again" (2025-05-12)](https://www.kyfb.com/federation/newsroom/kentuckians-weathering-the-storms-once-again) — abierta

Confianza: **media**. Alta para la existencia, la región y las fechas de los eventos con fuente abierta (2007,
2011, 2012, 2019, 2021, 2022), y para los datos de estaciones de NWS. Media para las magnitudes agrícolas: son
proyecciones del año del evento o cifras de universidad y prensa, no valores finales de NASS (salvo los 68 bu/ac de
2012, que la AP atribuye a NASS). Baja para las fechas y temperaturas de la helada de 2007 (solo extracto) y para
el efecto agrícola de las inundaciones de 2011 y 2019 en KY (no encontré cifras). Las inundaciones de los ríos Ohio
y Misisipi en 2021–2022 que menciona la tarea quedaron sin fuente: lo que encontré fueron inundaciones repentinas
de lluvia local y, a fines de 2022, ríos en mínimos récord.

Impacto: ninguno hoy (KY no está en `config/config.yaml`). Si el humano lo suma en una cuarta tanda: agregar estos
eventos a los chequeos de control de calidad de `clima`, `agua`, `vegetacion` y `cultivos`, y correr
`eventos_extremos_rend_estado.py` con KY para tener los rendimientos de NASS. ML puede marcar como años raros: 2007
(helada y sequía), 2011 y 2019 (exceso de agua en el oeste), 2012 (sequía, calor y helada del trigo) y 2022 (sequía
del oeste). Para KY conviene mirar el trigo de invierno y el doble cultivo trigo/soja, además del maíz y la soja.
No cambia `config/` ni el esquema de ningún CSV.
