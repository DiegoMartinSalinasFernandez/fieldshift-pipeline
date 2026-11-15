# Tabla de cultivos para el Corn Belt (IA, IL, IN, OH, NE, MN, KS)

Pregunta: Tabla de cultivos para el Corn Belt → completar config/cultivos.csv: fechas habituales de siembra y cosecha por estado (USDA Agricultural Handbook 628 y Crop Progress), ventana de período crítico, Kc inicial/medio/final y duración de etapas (FAO-56), temperatura base y método de GDD, umbral de daño por calor, sensibilidad a helada, profundidad de raíces, fijación de N, rastrojo y C:N, familia botánica, tolerancia a sequía y a anegamiento, valor forrajero. Incluir cultivos de cobertura (centeno, avena, trébol).

Respuesta corta: `config/cultivos.csv` quedó completo en parte, con 194 celdas respaldadas por una cita textual cada una (`docs/research/cultivos_fuentes.csv`). Las fechas de siembra y cosecha salen del USDA Agricultural Handbook 628 (edición 2010), tomando el rango más amplio entre los siete estados (Iowa, Illinois, Indiana, Ohio, Nebraska, Minnesota y Kansas; los cuatro últimos se sumaron en T006); la siembra de primavera de alfalfa y heno, de Iowa State. Los Kc, la duración de las etapas y la profundidad máxima de raíces salen de FAO-56 (tablas 11, 12 y 22). La temperatura base y el tope de GDD salen de Wikipedia y del Oklahoma Mesonet (alfalfa 5/30 °C, pasto para heno 10/30 °C, soja 10/35 °C, trigo tope 30 °C). El período crítico sale de notas de extensión de Purdue (maíz: fines de junio a fines de julio), Iowa State (soja: fines de julio y principios de agosto) e Illinois (trigo: floración de fines de abril a la cuarta semana de mayo). La helada mortal del maíz y la soja es −2 °C; el rastrojo, 7,5 t/ha en maíz, 4,3 en trigo y 3,1 en soja (sur de Ontario). Los rasgos de los cultivos de cobertura salen de SARE (*Managing Cover Crops Profitably*) y la familia botánica de Wikipedia. La soja fija en promedio 111 kg N/ha (revisión de Salvagiotti et al. 2008) y su rastrojo tiene C:N 65:1 (Manitoba). El centeno sobrevive hasta −25 °C, llega a 2 m de raíz, se siembra hasta octubre y florece en mayo–junio (Yara). Maíz, trigo y heno son gramíneas que no fijan N. Quedan vacíos por falta de una fuente verificable: período crítico de avena, alfalfa, heno y trébol, rastrojo en t/ha de alfalfa, heno y trébol (las fuentes de EE.UU. dan lb/acre), N fijado en kg/ha de los no fijadores (ninguna fuente da "0 kg/ha"), calor de avena, centeno, heno y trébol, y etapas y temperatura base del trébol.

Detalle:

**Fechas habituales (Handbook 628, NASS, octubre de 2010).** Para cada estado y cultivo la tabla trae el inicio, el período más activo y el fin, tanto de la siembra como de la cosecha. Con el PDF pasado a texto, las tablas por estado quedan por columnas: primero la columna "begin" de todos los cultivos, después "most active" y después "end". En `cultivos.csv` va el inicio más temprano y el fin más tardío de los siete estados.

| Cultivo | Estado | Siembra inicio | Siembra fin | Cosecha inicio | Cosecha fin |
|---|---|---|---|---|---|
| Maíz grano | IA | Apr 19 | May 26 | Sep 21 | Nov 21 |
| Maíz grano | IL | Apr 14 | Jun 5 | Sep 14 | Nov 20 |
| Maíz grano | IN | Apr 20 | Jun 10 | Sep 15 | Nov 25 |
| Soja | IA | May 2 | Jun 16 | Sep 21 | Oct 31 |
| Soja | IL | May 2 | Jun 24 | Sep 19 | Nov 7 |
| Soja | IN | May 1 | Jun 25 | Sep 20 | Nov 10 |
| Trigo de invierno | IA | Sep 6 | Oct 30 | Jun 24 | Aug 7 |
| Trigo de invierno | IL | Sep 28 | Nov 9 | Jun 15 | Jul 19 |
| Trigo de invierno | IN | Sep 25 | Nov 5 | Jun 15 | Jul 25 |
| Avena de primavera | IA | Mar 25 | May 13 | Jul 9 | Aug 11 |
| Avena de primavera | IL | Mar 20 | May 12 | Jul 4 | Aug 13 |
| Avena de primavera | IN | Apr 1 | May 10 | Jul 10 | Aug 10 |
| Heno de alfalfa | IA / IL / IN | (na) | (na) | May 24 / May 9 / May 15 | Sep 29 / Sep 21 / Sep 20 |
| Otro heno | IA / IL / IN | (na) | (na) | Jun 5 / May 11 / May 15 | Sep 3 / Jul 17 / Sep 20 |
| Maíz grano | OH | Apr 18 | May 30 | Sep 27 | Dec 1 |
| Maíz grano | NE | Apr 19 | May 21 | Sep 18 | Nov 20 |
| Maíz grano | MN | Apr 22 | May 29 | Sep 27 | Nov 23 |
| Maíz grano | KS | Apr 5 | May 25 | Sep 1 | Nov 10 |
| Soja | OH | Apr 26 | Jun 10 | Sep 23 | Nov 12 |
| Soja | NE | May 5 | Jun 8 | Sep 23 | Nov 2 |
| Soja | MN | May 2 | Jun 13 | Sep 20 | Oct 31 |
| Soja | KS | May 5 | Jul 1 | Sep 20 | Nov 15 |
| Trigo de invierno | OH | Sep 26 | Nov 6 | Jun 28 | Jul 20 |
| Trigo de invierno | NE | Sep 3 | Oct 12 | Jun 28 | Jul 27 |
| Trigo de invierno | MN | Aug 25 | Sep 25 | Jul 20 | Sep 10 |
| Trigo de invierno | KS | Sep 10 | Nov 1 | Jun 15 | Jul 15 |
| Avena de primavera | OH | Apr 4 | May 13 | Jul 13 | Aug 11 |
| Avena de primavera | NE | Mar 26 | May 3 | Jul 4 | Aug 7 |
| Avena de primavera | MN | Apr 11 | May 26 | Jul 21 | Sep 4 |
| Avena de primavera | KS | Feb 20 | May 1 | Jul 10 | Aug 10 |
| Heno de alfalfa | OH / NE / MN / KS | (na) | (na) | May 17 / May 19 / May 25 / May 10 | Sep 24 / Oct 15 / Sep 24 / Nov 1 |
| Otro heno | OH / NE / MN / KS | (na) | (na) | May 20 / Jun 5 / Jun 5 / May 25 | Oct 13 / Sep 20 / Aug 30 / Sep 15 |

Resultado en `cultivos.csv` con los siete estados: maíz 04-05 a 06-10 y 09-01 a 12-01; soja 04-26 a 07-01 y 09-19 a 11-15; trigo de invierno 08-25 a 11-09 y 06-15 a 09-10; avena 02-20 a 05-26 y 07-04 a 09-04; alfalfa (cortes) 05-09 a 11-01; heno 05-11 a 10-13.

**Estados nuevos (T006, 2026-11-15).** Las tablas de Ohio (pág. 45), Nebraska (42), Minnesota (41) y Kansas (39) del mismo Handbook 628. Con ellas cambian 13 celdas, todas por un extremo de Kansas, Minnesota u Ohio. Antes, con IA/IL/IN, los valores eran: maíz 04-14 a 06-10 y 09-14 a 11-25; soja 05-01 a 06-25 y 09-19 a 11-10; trigo de invierno 09-06 a 11-09 y 06-15 a 08-07; avena 03-20 a 05-13 y 07-04 a 08-13; alfalfa 05-09 a 09-29; heno 05-11 a 09-20. Quién fija cada extremo nuevo:
- **Kansas** (el más al sur): siembra más temprana de maíz (Apr 5) y avena (Feb 20), cosecha más temprana de maíz (Sep 1), fin de siembra de soja (Jul 1) y fin de cosecha de soja (Nov 15) y de alfalfa (Nov 1).
- **Minnesota** (el más al norte): el trigo de invierno se siembra antes (Aug 25) y se cosecha más tarde (hasta Sep 10); la avena se siembra y cosecha más tarde (May 26, Sep 4).
- **Ohio:** fin de cosecha de maíz (Dec 1) y de otro heno (Oct 13), e inicio de siembra de soja (Apr 26).

En la evidencia (`cultivos_fuentes.csv`) cada celda nueva cita la columna de la tabla del estado que la fija (inicio, fin de siembra o de cosecha), como sale del PDF pasado a texto; las 20 citas del Handbook se verificaron con `cita_en_texto` y `numero_en_cita` de `loop/checks/score.py`.

**Kc y etapas (FAO-56).** Tabla 12: maíz grano 0,3 / 1,20 / 0,35 (Kc ini del grupo de cereales; para el Kc final elegí 0,35, el extremo de cosecha seca del rango 0,60–0,35); soja 0,4 / 1,15 / 0,50 (Kc ini del grupo de leguminosas); trigo de invierno con suelo congelado 0,4 / 1,15 / 0,25; avena 0,3 / 1,15 / 0,25; alfalfa para heno (promedio de cortes) 0,40 / 0,95 / 0,90; trébol (berseem para heno) 0,40 / 0,90 / 0,85; heno como raigrás para heno 0,95 / 1,05 / 1,00. Tabla 11 (días ini/des/med/fin): maíz grano 30/40/50/50 (Idaho, EE.UU., la fila de clima templado del norte de EE.UU.); soja 20/30/60/25 (Central USA, y se usó 30 del valor "30/35"); trigo de invierno 160/75/75/25 (Idaho, con dormancia invernal); avena 20/25/60/30 (fila "barley/oats/wheat", siembra marzo/abril a 35–45 °N); alfalfa, primer ciclo de corte, 10/30/25/10 (Idaho). Tabla 22 (máximo del rango de profundidad efectiva de raíces): maíz 1,7 m, soja 1,3 m, trigo de invierno 1,8 m, avena 1,5 m, alfalfa 2,0 m, trébol (berseem) 0,9 m, heno (raigrás) 1,0 m.

**GDD.** Wikipedia ("Growing degree-day"): el maíz arranca a 10 °C y deja de crecer a 30 °C, que es el método 50/86 °F del CLAUDE.md. La soja usa base 10 °C y los cereales de invierno (trigo, avena, centeno), 4,5 °C, con el cálculo simple (Tmax + Tmin)/2 − Tbase.

**Helada (FAO-56, nota de la tabla 11).** La temporada de la alfalfa va de la última helada de −4 °C en primavera a la primera de −4 °C en otoño. La de los pastos (usada para heno) arranca 7 días antes de esa helada en primavera y termina 7 días después en otoño.

**Calor y frío (Wikipedia).** Por encima de 40 °C la soja frena mucho su crecimiento (`tcalor_c` = 40). A la avena la daña el frío sostenido por debajo de −7 °C (`helada_temp_c` = −7).

**Calor, helada y anegamiento (FAO Paper 66 y Bayer).** Maíz: 37,8 °C o más causan estrés térmico extremo que puede desecar el polen (`tcalor_c` = 37.8, Bayer Crop Science Canadá); sigue sin cita en °C la helada del maíz. Trigo de invierno: arriba de 34 °C en el llenado se acelera la senescencia (`tcalor_c` = 34); en etapas tempranas algunos cultivares sobreviven hasta −20 °C, pero en espigazón y floración la helada hace perder espiguillas; el anegamiento en la etapa vegetativa reduce mucho el rendimiento (`baja`). Soja: muy sensible a la helada en la emergencia y en el llenado de vainas; tolera el anegamiento hasta 7 días, pero pierde más de 40 % si se prolonga en floración (`media`). Trébol rojo: prefiere suelos bien drenados pero tolera los menos drenados (`media`, SARE).

**Relación C:N del rastrojo (tabla del NRCS de Dakota del Norte, en un documento de UC Davis).** Paja de centeno 82:1, de trigo 80:1, de avena 70:1, rastrojo de maíz 57:1, centeno de cobertura en antesis 37:1 y alfalfa joven para heno 13:1. Para el centeno se usó el valor del cultivo de cobertura (37), porque es su uso en la tabla; para la alfalfa, el del heno joven (no hay valor de rastrojo). Soja y heno quedan vacíos.

**N fijado (Saskatchewan Forage Council).** La fijación de la alfalfa subió de 174 kg/ha en el primer año a 466 kg/ha en el tercero (Manitoba); se usa el valor del primer año (`fija_n_kgha` = 174), porque el del tercero queda fuera del rango del check y del primer año de una rotación.

**Período crítico.** Las notas de extensión lo dan como rangos de calendario aproximados ("fines de junio", "principios de agosto"); los pasé a fechas con la regla: "principios" = días 1–10, "fines" = días 21 a fin de mes, "cuarta semana" = días 22–28. Maíz (Purdue, Indiana): polinización y emergencia de estigmas entre fines de junio y fines de julio → 06-21 a 07-31. Soja (Iowa State): "fines de julio y principios de agosto hacen la soja" → 07-21 a 08-10. Trigo de invierno (farmdoc, Illinois): la floración empieza a fines de abril en el sur y en la tercera o cuarta semana de mayo en el norte → 04-21 a 05-28. Avena, alfalfa y heno quedan vacíos (la guía de avena de Wisconsin dice que es muy sensible al calor entre espigazón y madurez, sin fechas). Por año, las fechas reales salen de `fenologia_estado.csv` (Crop Progress, `doy_50_floracion`).

**GDD por cultivo (Oklahoma Mesonet).** Método de corte: Tmax se recorta al tope del cultivo antes de promediar y los valores negativos van a cero. Alfalfa 41 °F (5 °C) / 86 °F (30 °C); pasto para heno 50 °F (10 °C) / 86 °F (30 °C); soja 50 °F (10 °C) / 95 °F (35 °C); trigo 32 °F (0 °C) / 86 °F (30 °C). Para avena y centeno se usa el tope genérico de 30 °C de Wikipedia ("usually capped at 30 °C"). La base del trigo sigue en 4,5 °C (Wikipedia); el Mesonet usa 0 °C.

**Helada (Sylvite, Ontario).** Una helada mortal es de −2 °C o menos: en maíz y soja mata tallo, hojas y vainas o espigas y corta el llenado de grano (`helada_temp_c` = −2 en los dos; `helada_etapa` del maíz = llenado de grano).

**Rastrojo (Nkoa, Kendall y Deen 2014, sur de Ontario, sistemas maíz-soja-trigo).** Rastrojo de maíz 7,5 t/ha/año, paja de trigo 4,3 t/ha/año y paja de soja 3,1 t/ha/año.

**Tolerancias y forraje (ronda 8).** Maíz: un día de anegamiento en V6 baja ~10 % el rendimiento y siete días, 36 % (Purdue) → anegamiento `baja`. Alfalfa: tolera el anegamiento menos que las gramíneas forrajeras (FAO 66) → `baja`. Soja: el crecimiento vegetativo es muy sensible al déficit hídrico (FAO 66) → sequía `baja`. Trigo: ajusta osmóticamente mejor que el maíz (FAO 66) → sequía `media`. Avena: necesita más humedad que la cebada (SARE) → sequía `baja`. Trigo como pastura: forraje de alta calidad hasta 6 meses del año (Arkansas). Soja: tres cuartas partes se usan para alimentar ganado (Wikipedia).

**Cultivos de cobertura (SARE).** Centeno: más tolerante al frío y a la sequía que el trigo, crece en suelos mal drenados y muchos cultivares toleran el anegamiento; maduro es poco palatable, pero en bota hace heno o henolaje de buena calidad. Avena: tolera el suelo húmedo mejor que la cebada. Trébol rojo: fija de 70 a 150 lb de N por acre (no se convirtió a kg/ha porque la regla de verificación pide que el número aparezca en la cita) y alcanza su mejor valor forrajero de 5 a 15 días después de la primera flor.

**Ronda 20.** Alfalfa: por encima de 30 °C florece antes y rinde menos forraje (Al-Hamdani y Todd 1990, Oklahoma) → `tcalor_c` 30. Centeno: la ventana de siembra de coberturas en maíz-soja de Iowa empieza a mediados de agosto (Iowa State, 2025) → `siembra_inicio` 08-15; como cultivo para grano se cosecha de mediados a fines de julio (Practical Farmers of Iowa) → 07-15 a 07-31; es el cereal más resistente al invierno una vez establecido (UVM; −30 °F ≈ −34 °C, fuera del rango del check, así que `helada_temp_c` quedó vacío). Trébol rojo: la siembra al voleo sobre helada va de mediados de febrero a principios de marzo (Iowa State) → 02-15 a 03-10; fija 150–200 kg N/ha/año en praderas con mucho trébol (Teagasc, Irlanda) → `fija_n_kgha` 150, el límite inferior. Heno: etapas inicial (10 d) y de desarrollo (20 d) de "grass pasture" en la tabla 11 de FAO-56 (las etapas media y final no tienen valor en la tabla); anegamiento `media`, porque FAO 66 dice que las gramíneas forrajeras lo toleran mejor que la alfalfa (`baja`).

**Ronda 4 del día.** Maíz, trigo de invierno y heno: `fija_n` = `no`, porque son gramíneas que "no pueden tomar su propio nitrógeno del aire" (Kenyon College, Farm School). Soja: en la revisión de Salvagiotti et al. (2008, Field Crops Research) la fijación va de 0 a 337 kg N/ha, con promedio de 111 → `fija_n_kgha` 111; el rastrojo tiene C:N 65:1 en la tabla de la guía de fertilidad de Manitoba → `rastrojo_cn` 65. Heno de raigrás: no tolera el calor ni la sequía (Ohio State, ANR-0229) → `tolerancia_sequia` `baja`; el heno en general tiene C:N 22:1 (NDSU, tabla de compostaje) → `rastrojo_cn` 22. Centeno (Yara, principios agronómicos): las plantas establecidas sobreviven hasta −25 °C (`helada_temp_c` −25); la raíz llega a menudo a 2 m (`raiz_max_m` 2); se siembra en septiembre–octubre (`siembra_fin` 10-31); florece en mayo o junio (`critico_inicio` 05-01, `critico_fin` 06-30, la floración como período crítico del grano).

**Ronda 10 (noche 2).** Centeno: FAO-56 no tiene una fila para el centeno, así que se usa la del trigo de invierno, el cereal de invierno más parecido (misma tribu Triticeae, sembrado en octubre): Kc 0,4 / 1,15 / 0,25 ("winter wheat - with frozen soils", tabla 12) y etapas de 160 / 75 / 75 / 25 días (fila de Idaho, sembrado en octubre, tabla 11). Trébol rojo: en 393 accesiones europeas aclimatadas al frío, la LT50 (temperatura que mata al 50 % de las plantas) va de −6,0 a −11,5 °C (Zanotto et al. 2023, Frontiers in Plant Science) → `helada_temp_c` −6, el valor de la accesión menos tolerante.

**Ronda 11 (noche 2).** Avena: la paja estimada en las praderas canadienses (1994–2003) promedia 2,48 t/ha (Sokhansanj et al. 2006, Canadian Biosystems Engineering, tabla 3) → `rastrojo_t_ms_ha` 2.48. Trébol rojo (Kentucky, AGR-33): el primer corte va a ~10 % de floración, "about june 1-15", y el último corte tiene que salir antes del 10–25 de septiembre → `cosecha_inicio` 06-01 y `cosecha_fin` 09-25 (del primer al último corte, como en la alfalfa y el heno); el C:N es "low: 15-20:1" en la tabla de coberturas de Clemson → `rastrojo_cn` 15, el límite inferior. Centeno: la biomasa aérea de la mezcla de cobertura con centeno en primavera, en maíz-soja en Lexington (Illinois), promedió 1,26 Mg/ha en 2015–2018 (Thompson et al. 2020, Agronomy Journal, tabla 4) → `rastrojo_t_ms_ha` 1.26.

**Supuestos.**
- T006: el rango de siete estados es más ancho que el de tres, y los extremos los ponen estados con poca superficie del cultivo (trigo de invierno de Minnesota, 45 mil acres en 2009; avena de Kansas, 35 mil). Para ventanas por estado conviene la tabla por estado de arriba, que no entra en `cultivos.csv` (una fila por cultivo). Las siembras de alfalfa, heno, centeno y trébol siguen saliendo de Iowa State y otras fuentes de Iowa: no encontré en el Handbook 628 fechas de siembra de esos cultivos para OH, NE, MN ni KS (dice "(NA)" o no los lista), así que esas celdas no cambian y quedan sin dato por estado. Crop Progress no se usó acá: da fechas reales por año y va en `fenologia_estado.csv`.
- El Handbook 628 es de 2010 (es la última edición). Crop Progress da fechas reales por año: eso va en `fenologia_estado.csv` del paquete `cultivos`, no acá.
- "Heno" (CDL 37, otro heno) se representa con raigrás para heno (FAO-56), con raigrás perenne (*Lolium perenne*, Wikipedia: familia y valor forrajero) y con la fila "hay, other" del Handbook 628. "Trébol" se representa con berseem en FAO-56 (es el único trébol de la tabla 12) y con trébol rojo en SARE y Wikipedia.
- Las filas de FAO-56 elegidas para la duración de las etapas son las más parecidas al Corn Belt (Idaho, Central USA, 35–45 °N), no mediciones en IA/IL/IN.
- Las categorías de tolerancia (baja/media/alta) son mi lectura de la frase citada.
- Las fechas del período crítico vienen de rangos en palabras ("fines de junio") convertidos con la regla de arriba; son ventanas típicas, no de un año.
- El rastrojo y la helada salen de fuentes de Ontario (Canadá), vecino del Corn Belt; se tomó la "biomasa de paja" como materia seca.
- La siembra de alfalfa y heno es la de primavera en Iowa ("spring hay and pasture seedings ... late February through late April"); la siembra de fines de verano (agosto) queda fuera.
- El tope de GDD de avena y centeno es el genérico de 30 °C, no uno medido para esos cultivos.
- Ronda 20: las fechas en palabras se convirtieron con la misma regla ("mid-august" → 08-15, "mid- to late july" → 07-15/07-31, "mid-february ... early march" → 02-15/03-10). Las fechas de cosecha del centeno son de centeno para grano; como cobertura se termina en primavera, antes de la siembra del cultivo siguiente. El N fijado por el trébol viene de praderas irlandesas con mucho trébol rojo; en una cobertura corta en el Corn Belt puede ser menos. Las etapas del heno son las de "grass pasture" de FAO-56 (California/Idaho), no de heno en IA/IL/IN.
- Ronda 4 del día: el C:N del rastrojo de soja varía mucho entre fuentes (15:1 en K-State, 17 en un ensayo de Queensland, 25–40:1 en Indigo, 65:1 en Manitoba); se usó el de Manitoba porque es una tabla de rastrojos de cosecha de una zona vecina, pero es el extremo alto. El C:N del heno (22:1) es del heno como material para compostar, no del rastrojo que queda en el lote. Los datos del centeno de Yara son de una guía general (Reino Unido/Europa), no del Corn Belt; −25 °C es el valor conservador (UVM y UC Davis dan −34 a −35 °C para plantas bien establecidas). El período crítico del centeno es el de grano (floración); como cobertura se termina antes. El N fijado por la soja es un promedio mundial de la literatura, no de IA/IL/IN.
- Ronda 10 (noche 2): el Kc y las etapas del centeno son los del trigo de invierno de FAO-56 (proxy: no hay fila de centeno); el centeno como cobertura se termina en primavera, así que en la práctica la etapa media y la final no llegan a darse. La helada del trébol es de plantas aclimatadas de germoplasma europeo en cámara, no de lotes del Corn Belt; las plántulas recién emergidas son menos tolerantes.
- Ronda 11 (noche 2): la paja de avena es una estimación (producción de grano × relación paja/grano × 0,88) para Alberta, Saskatchewan y Manitoba, no una medición en IA/IL/IN; se tomó el promedio de las praderas. Las fechas de corte del trébol son de Kentucky, al sur del Corn Belt: en Iowa el primer corte puede atrasarse una o dos semanas. El C:N del trébol es una categoría de una tabla de coberturas del sudeste de EE.UU. (rango 15–20:1); se tomó el límite inferior, como en la helada del trébol y el N fijado. El "rastrojo" del centeno es la biomasa aérea de la cobertura al terminarla en primavera (lo que vuelve al suelo), de una mezcla con centeno en un solo sitio de Illinois; varía mucho con la fecha de siembra y de terminación (los ensayos de Iowa dan de 0,2 a casi 9 t/ha).

Fuentes:
- [Field Crops Usual Planting and Harvesting Dates, Agricultural Handbook 628 (USDA NASS, octubre de 2010)](https://downloads.usda.library.cornell.edu/usda-esmis/files/vm40xr56k/dv13zw65p/w9505297d/planting-10-29-2010.pdf), consultado 2026-11-14 (IA, IL, IN) y 2026-11-15 (OH, NE, MN, KS)
- [FAO-56 Crop evapotranspiration, cap. 6: ETc - single crop coefficient (tablas 11 y 12)](https://www.fao.org/3/x0490e/x0490e0b.htm), consultado 2026-11-14
- [FAO-56 Crop evapotranspiration, cap. 8: ETc under soil water stress conditions (tabla 22)](https://www.fao.org/4/x0490e/x0490e0e.htm), consultado 2026-11-14
- [Growing degree-day (Wikipedia)](https://en.wikipedia.org/wiki/Growing_degree-day), consultado 2026-11-14
- [SARE, Managing Cover Crops Profitably: Cereal Rye](https://www.sare.org/publications/managing-cover-crops-profitably/nonlegume-cover-crops/cereal-rye/), consultado 2026-11-14
- [SARE, Managing Cover Crops Profitably: Oats](https://www.sare.org/publications/managing-cover-crops-profitably/nonlegume-cover-crops/oats/), consultado 2026-11-14
- [SARE, Managing Cover Crops Profitably: Red Clover](https://www.sare.org/publications/managing-cover-crops-profitably/legume-cover-crops/red-clover/), consultado 2026-11-14
- [FAO Irrigation and Drainage Paper 66, Crop yield response to water, cap. 3.4 Herbaceous crops](https://fao.org/4/i2800e/i2800e07.pdf), consultado 2026-11-14
- [Carbon to nitrogen ratios in cropping systems (USDA NRCS, reproducido por UC Davis Soil Health)](https://soilhealth.ucdavis.edu/download_file/view/224/234), consultado 2026-11-14
- [Corn pollination affected by heat and drought (Bayer Crop Science Canadá, 2021)](https://www.cropscience.bayer.ca/articles/2021/corn-pollination-affected-by-heat-and-drought), consultado 2026-11-14
- [Growing Forage Legumes in Rotation (Saskatchewan Forage Council)](https://www.saskforage.ca/s/Growing-Forage-Legumes-in-Rotation.pdf), consultado 2026-11-14
- [Tassel Emergence & Pollen Shed (Purdue University, R.L. Nielsen)](https://agry.purdue.edu/Ext/corn/news/timeless/Tassels.html), consultado 2026-11-14
- [Fight to the Finish for Moisture (Iowa State ICM, 2023)](https://crops.extension.iastate.edu/post/fight-finish-moisture), consultado 2026-11-14
- [Illinois winter wheat enters spring in good condition (farmdoc)](https://farmdoc.illinois.edu/?p=43151), consultado 2026-11-14
- [Managing frost damage in corn and soybeans (Sylvite)](https://sylvite.ca/about-us/insights/managing-frost-damage-in-corn-soybeans/), consultado 2026-11-14
- [Ecozone dynamics of crop residue biomass ... in southern Ontario (Nkoa et al. 2014, FAO AGRIS)](https://agris.fao.org/search/en/records/65dfbdf263b8185d9cae71bb), consultado 2026-11-14
- [When is it too late to plant forages? (Iowa State ICM, 2008)](https://crops.extension.iastate.edu/cropnews/2008/04/when-it-too-late-plant-forages), consultado 2026-11-14
- [Degree-day heat unit calculator (Oklahoma Mesonet)](https://www.mesonet.org/images/site/Degree%20day%20Heat%20Unit%20Calculator%20text%281%29.pdf), consultado 2026-11-14
- [How flooding and soil waterlogging affect corn growth and yield (Purdue Agronomy, 2026)](https://ag.purdue.edu/news/department/agry/kernel-news/2026/06/how-flooding-and-soil-waterlogging-affect-corn-growth-and-yield.html), consultado 2026-11-14
- [Fall and winter grazing of wheat (Arkansas Wheat Production Handbook, cap. 12)](https://www.uaex.uada.edu/publications/pdf/mp404/chapter12wheat.pdf), consultado 2026-11-14
- [Effect of temperature regimes on photosynthesis, respiration, and growth in alfalfa (Al-Hamdani y Todd 1990, Proc. Okla. Acad. Sci.)](https://ojs.library.okstate.edu/osu/index.php/OAS/article/view/5454/5080), consultado 2026-11-14
- [Planning for successful cover crops (Iowa State ICM, 2025)](https://crops.extension.iastate.edu/post/planning-successful-cover-crops), consultado 2026-11-14
- [Frost seeding legumes (Iowa State Extension)](https://crops.extension.iastate.edu/encyclopedia/frosting-seeding-legumes), consultado 2026-11-14
- [Cereal rye variety trial 2020 (Practical Farmers of Iowa)](https://practicalfarmers.org/resources/research-reports/cereal-rye-variety-trial-2020), consultado 2026-11-14
- [Why rye? Winter rye factsheet (University of Vermont)](https://uvm.edu/vtvegandberry/factsheets/winterrye.html), consultado 2026-11-14
- [The benefits of red clover (Teagasc)](https://www.teagasc.ie/news--events/daily/grassland/the-benefits-of-red-clover.php), consultado 2026-11-14
- [Soybeans in the farm ecosystem (Kenyon College, Farm School)](https://www2.kenyon.edu/projects/farmschool/nature/soy.htm), consultado 2026-11-14
- [Nitrogen uptake, fixation and response to fertilizer N in soybeans: a review (Salvagiotti et al. 2008, Field Crops Research)](https://www.mssoy.org/sites/default/files/documents/nebraska-n-review-2008-ok.pdf), consultado 2026-11-14
- [Don't count on nitrogen credits after soybeans in Manitoba (Manitoba Agriculture, 2012)](https://www.gov.mb.ca/agriculture/crops/soil-fertility/pubs/fer01s02.pdf), consultado 2026-11-14
- [Forage species selection for Ohio, ANR-0229 (Ohio State University)](https://ohioline.osu.edu/factsheet/anr-0229), consultado 2026-11-14
- [Composting manure (NDSU Extension)](https://www.ndsu.edu/agriculture/node/5490), consultado 2026-11-14
- [Rye agronomic principles (Yara UK)](https://int.yara.co.uk/crop-nutrition/rye/rye-agronomic-principles/), consultado 2026-11-14
- [A genome-wide association study of freezing tolerance in red clover (Zanotto et al. 2023, Frontiers in Plant Science)](https://public-pages-files-2025.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2023.1189662/text), consultado 2026-11-14
- [Production and distribution of cereal straw on the Canadian prairies (Sokhansanj et al. 2006, Canadian Biosystems Engineering 48)](https://library.csbe-scgab.ca/docs/journal/48/c0556.pdf), consultado 2026-11-14
- [Red clover, AGR-33 (University of Kentucky Cooperative Extension)](https://publications.ca.uky.edu/sites/publications.ca.uky.edu/files/agr33.pdf), consultado 2026-11-14
- [Management practices affecting the nutrient provision capacity of cover crops (Clemson, Land-Grant Press)](https://lgpress.clemson.edu/?p=1843), consultado 2026-11-14
- [Short-run net returns to a cereal rye cover crop mix in a Midwest corn-soybean rotation (Thompson et al. 2020, Agronomy Journal)](https://www.mssoy.org/sites/default/files/documents/thompson-et-al-aj-jan-2020.pdf), consultado 2026-11-14
- Wikipedia (familia botánica, fijación de N, sequía, forraje): [Maize](https://en.wikipedia.org/wiki/Maize), [Soybean](https://en.wikipedia.org/wiki/Soybean), [Common wheat](https://en.wikipedia.org/wiki/Common_wheat), [Oat](https://en.wikipedia.org/wiki/Oat), [Alfalfa](https://en.wikipedia.org/wiki/Alfalfa), [Rye](https://en.wikipedia.org/wiki/Rye), [Trifolium pratense](https://en.wikipedia.org/wiki/Trifolium_pratense), [Lolium perenne](https://en.wikipedia.org/wiki/Lolium_perenne), consultado 2026-11-14

Confianza: media

Impacto: `config/cultivos.csv` (con su evidencia en `docs/research/cultivos_fuentes.csv`). Sirve para las ventanas fenológicas por cultivo (CLAUDE.md §4), para la ETc con Kc en `clima` y `agua` y para los GDD con base y tope por cultivo. Los vacíos (período crítico de avena, alfalfa y heno; calor del centeno; rastrojo en t/ha de alfalfa, heno y trébol; N fijado en kg/ha de los cultivos que no fijan; período crítico, etapas y temperaturas del trébol) quedan para otra ronda o para el humano.

Citas:
> "corn is an example of this: it starts growing at 10 °c and stops at 30 °c, meaning any growing degree-days above 30 °c do not count" — [Growing degree-day (Wikipedia)](https://en.wikipedia.org/wiki/Growing_degree-day)
> "maize, field (grain) (field corn) 1.20 0.60-0.35" — [FAO-56, cap. 6](https://www.fao.org/3/x0490e/x0490e0b.htm)
