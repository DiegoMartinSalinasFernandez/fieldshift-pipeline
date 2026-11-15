# Consumo de agua por cultivo y rotación en el Corn Belt

Pregunta: ¿Cuánta agua consumen en la temporada (evapotranspiración, ET) el maíz, la soja, el trigo de invierno, la avena, la alfalfa y el heno en IA, IL, IN, OH, NE, MN y KS, según mediciones (lisímetros, eddy covariance, balances de agua del suelo)? ¿Cuánto varía entre años? ¿Cómo cambia el agua del suelo que cada cultivo le deja al siguiente (por ejemplo, alfalfa antes del maíz)? ¿Cómo se comparan las mediciones con los Kc de FAO-56 que están en `config/cultivos.csv`?

Respuesta corta: Encontré y abrí mediciones de la zona para **maíz, soja, trigo de invierno y alfalfa**, y una de **avena con alfalfa** (avena de cobertura sembrada junto con la alfalfa). Para **heno de gramíneas** no encontré nada medido en los 7 estados.

- **Maíz** (ET de la temporada): 482 mm en secano y 548 mm con riego en Mead (NE), en promedio de 5 años. En Lamberton (MN), en 3 temporadas, el uso de agua fue de 535 mm. En Kansas, con riego, 574–597 mm en 120 días (Colby, 1989–1991; el valor sale de un balance calibrado, no de una medición directa) y 637–640 mm (Tribune, 2013–2016, con riego limitado; balance de agua del suelo).
- **Soja:** 431 mm en secano y 452 mm con riego (Mead), y 484 mm en Lamberton. El maíz usa entre 11 % y 18 % más agua que la soja (Mead).
- **Alfalfa:** 652 mm (Lamberton). Es el valor más alto de todos los cultivos y supera también a la pradera (604 mm).
- **Avena con alfalfa:** 340 mm (Lamberton).
- **Trigo de invierno:** ≈ 508 mm (20,01 in) con 10 in de riego en Tribune (KS, 2013–2016). En un informe de 1977 de Kansas (Manhattan, Ellsworth y Garden City) figura 19,0 in (≈ 483 mm). Ese valor está en una figura que no se lee bien y no queda claro a qué sitio corresponde.

**Kc medidos y FAO-56.** Los Kc de mitad de temporada medidos con eddy covariance en Mead son **más bajos** que los de FAO-56 que usa `config/cultivos.csv`:

| Cultivo | Mead, con riego | Mead, secano | `cultivos.csv` (FAO-56) |
|---|---|---|---|
| Maíz | 1,03 ± 0,07 | 0,84 ± 0,20 | 1,20 |
| Soja | 0,98 ± 0,02 | 0,90 ± 0,13 | 1,15 |

Es decir, Kc × ET₀ con los valores de FAO-56 **sobreestima** la ET de la temporada media entre ~15 % y ~40 %, según el cultivo y si hay riego.

**Variación entre años.** Lo que pude abrir solo da rangos parciales:
- el Kc del maíz de secano tiene un desvío de ±0,20;
- la evaporación fuera de la temporada va de 100 a 172 mm por año, entre el 16 % y el 28 % de la ET anual;
- en Tribune, el efecto del año es significativo (P < 0,001) en todas las variables de agua.

**Agua que queda para el cultivo siguiente.**
- En Lamberton, la alfalfa es la que más seca el perfil: el orden es alfalfa ≥ maíz ≥ avena/alfalfa ≥ soja.
- En Tribune, el maíz que sigue al trigo tuvo el agua del barbecho más larga, pero el barbecho fue el menos eficiente (24 % contra 36–53 %). El trigo sembrado justo después de la cosecha del maíz arranca sin recarga.

**Lo que no encontré o no pude abrir:**
- totales medidos de ET por temporada en IA, IL, IN y OH. Hay series de eddy covariance (Ames, IA y Bondville, IL), pero no abrí ningún paper con los totales;
- heno;
- avena sola;
- alfalfa medida en NE o KS.

Detalle:

## 1. Mediciones encontradas (abiertas)

| Cultivo | Lugar (estado) | Años | Método | ET o uso de agua de la temporada | Fuente |
|---|---|---|---|---|---|
| Maíz, secano | Mead (NE) | primeros 5 años desde 2001 | Eddy covariance, todo el año | 482 mm (media) | Suyker y Verma 2009 |
| Maíz, con riego | Mead (NE) | ídem | ídem | 548 mm (media) | Suyker y Verma 2009 |
| Soja, secano | Mead (NE) | ídem | ídem | 431 mm (media) | Suyker y Verma 2009 |
| Soja, con riego | Mead (NE) | ídem | ídem | 452 mm (media) | Suyker y Verma 2009 |
| Maíz | Lamberton (MN) | 3 temporadas (años no indicados en el resumen) | Balance de agua del suelo (humedad a 0,1–2,0 m) | 535 mm | Garcia y Garcia y Strock 2018 |
| Soja | Lamberton (MN) | ídem | ídem | 484 mm | ídem |
| Alfalfa | Lamberton (MN) | ídem | ídem | 652 mm | ídem |
| Avena/alfalfa (año de implantación) | Lamberton (MN) | ídem | ídem | 340 mm | ídem |
| Pradera (control) | Lamberton (MN) | ídem | ídem | 604 mm | ídem |
| Maíz con riego por goteo subterráneo, tratamientos bien regados (75–125 % de la ET) | Colby (KS) | 1989–1991 | ET **calculada** (Kcb × ET de referencia, corregida por agua disponible), contrastada con sonda de neutrones hasta 2,4 m | 574 / 588 / 597 mm (1989 / 1990 / 1991) en 120 días (15-may a 11-sep), con 100 % de la ET | Lamm et al. 1995, Tabla 1 |
| Maíz, 25 % de la ET | Colby (KS) | 1989–1991 | ídem | 506 / 459 / 517 mm | Lamm et al. 1995, Tabla 1 |
| Maíz, riego limitado a 10 in/año | Tribune (KS) | 2013–2016 | Balance: agua del suelo a la siembra − a la cosecha (hasta 8 ft) + lluvia + riego | 25,16 in (639 mm) en maíz continuo; 25,08 in (637 mm) tras trigo; 25,19 in (640 mm) tras sorgo | Schlegel 2017, Tabla 4 |
| Trigo de invierno, riego limitado | Tribune (KS) | 2013–2016 | ídem | 20,01 in (508 mm) | Schlegel 2017, Tabla 4 |
| Trigo de invierno, riego limitado | Tribune (KS) | 2016 (año húmedo) | ídem | 19,59 in (498 mm); maíz 26,75–28,72 in (679–729 mm) | Schlegel 2017, Tabla 3 |
| Trigo de invierno | Manhattan, Ellsworth y Garden City (KS) | ca. 1976 | No se lee en el texto (figura con ET y PET por etapa) | La Fig. 4 dice "ET = 19.0 inches" (≈ 483 mm), sin que quede claro el sitio. Manhattan tuvo la ET más alta y Garden City la más baja. En el oeste de Kansas, el trigo necesita ≈ 6 in (≈ 152 mm) después del encañado | Kanemasu 1977 |

Notas sobre las mediciones:
- En Mead, la evaporación fuera de la temporada de crecimiento fue de 100 a 172 mm. Representa entre el 16 % y el 28 % de la ET anual en los sistemas con maíz y entre el 24 % y el 26 % en los de soja. El rastrojo en superficie explica el 71 % de la variación de esa evaporación. **Ojo:** "ET de la temporada" no es el consumo anual del lote.
- El balance de Tribune incluye ~10 in (254 mm) de riego. No es un valor de secano y **no se puede comparar directamente** con IA, IL o IN.
- En Colby, el clima es semiárido (474 mm de lluvia al año). Por encima de 328 mm de uso de agua, el rendimiento del maíz subió 0,048 Mg/ha por cada mm (Lamm et al. 1995, resumen).
- Kanemasu (1977, Manhattan, 1976, año seco y sin riego) informa que en julio los cultivos de verano usan ≈ 0,25 in/día (≈ 6,4 mm/día). Los picos de consumo ocurren en floración: panojamiento-estigmas del maíz, plena floración de la soja.
- Las tres temporadas de Lamberton son de un ensayo de rotaciones de 4 años (avena/alfalfa – alfalfa – maíz – soja), con insumos orgánicos o convencionales, y una rotación maíz-soja. Solo pude leer el resumen. No sé si los valores son por temporada o por año calendario.

## 2. Comparación con los Kc de FAO-56 (`config/cultivos.csv`)

Valores en `cultivos.csv`, tomados de la Tabla 12 de FAO-56 según `docs/research/cultivos_fuentes.csv`:

| Cultivo | kc_ini | kc_med | kc_fin | Medido en la zona |
|---|---|---|---|---|
| maíz | 0,30 | 1,20 | 0,35 | Kc de mitad de temporada en Mead: **1,03 ± 0,07** con riego y **0,84 ± 0,20** en secano (ET/ET₀) |
| soja | 0,40 | 1,15 | 0,50 | Mead: **0,98 ± 0,02** con riego y **0,90 ± 0,13** en secano |
| trigo de invierno | 0,40 | 1,15 | 0,25 | Sin Kc medido en la zona. Kanemasu (1977): la ET iguala a la PET solo en Manhattan, entre el encañado y la espigazón, lo que sugiere Kc ≈ 1 respecto de esa PET. No es comparable sin saber cómo se calculó la PET |
| avena | 0,30 | 1,15 | 0,25 | Sin Kc medido. Solo hay uso de agua de avena/alfalfa (340 mm, MN) |
| alfalfa | 0,40 | 0,95 | 0,90 | Sin Kc medido en la zona. Es el uso de agua más alto de la rotación (652 mm, MN) |
| heno | 0,95 | 1,05 | 1,00 | Nada medido |

Por qué los Kc medidos dan más bajos:
1. En el resumen de Suyker y Verma no figura qué ET₀ usaron (pasto u otra referencia). Si fuera ET₀ de pasto (FAO-56), la diferencia con 1,20 y 1,15 es real. Si fuera otra referencia, puede ser en parte un efecto de escala. **No lo pude verificar.**
2. La Tabla 12 de FAO-56 es, textualmente, para "non stressed, well-managed crops in subhumid climates (RHmin ≈ 45%, u2 ≈ 2 m/s) for use with the FAO Penman-Monteith ETo", y en "standard conditions" ("achieving maximum crop yield"). Para otro RHmin o u2, el Kc de mitad de temporada se ajusta con la ecuación 62 (en función de u2, RHmin y la altura del cultivo h), y el Kc final con la 65 (solo si el Kc final de la tabla es mayor que 0,45). Los ejemplos de FAO-56 muestran cuánto mueve el ajuste. En el Recuadro 14, el trigo (1,15; h = 1 m) da 1,05 en clima húmedo con u2 = 2 m/s. En el Ejemplo 27, el maíz (1,20; h = 2 m) da 1,07 con u2 = 1,3 m/s y RHmin = 75 %. El Corn Belt del este (IA, IL, IN, OH) tiene veranos húmedos, así que la ecuación 62 ya baja el Kc del maíz a algo cercano a lo medido en Mead. **`cultivos.csv` guarda los valores de la tabla sin ajustar.**
3. En secano hay estrés (Kc 0,84 en maíz), y el desvío (±0,20) muestra cuánto cambia entre años.

Otras diferencias con la Tabla 12 de FAO-56 que importan para `cultivos.csv`:
- **Trigo de invierno:** `cultivos.csv` usa la fila "with frozen soils" (kc_ini 0,4). FAO-56 tiene otra fila, "with non-frozen soils", con kc_ini **0,7**, el mismo kc_med (1,15) y kc_fin 0,25–0,4. En el sur de Kansas el suelo no siempre se congela todo el invierno. Habría que decidir qué fila usar en cada estado; no encontré una medición que lo resuelva.
- **Alfalfa:** la fila "averaged cutting effects" (0,40 / 0,95 / 0,90), que es la de `cultivos.csv`, promedia todo el ciclo de cortes. Para cada período de corte, la tabla da 0,40 / **1,20** / 1,15. El texto de FAO-56 dice "the averaged, full-season Kc mid is 1.05", lo que no coincide con el 0,95 de la tabla. Es una inconsistencia del documento original. El uso de agua medido en Lamberton (652 mm, el mayor de la rotación) es coherente con un Kc alto entre cortes.
- **Maíz:** el kc_fin de la tabla es 0,60–0,35 (0,60 si se cosecha con el grano húmedo, 0,35 si se seca en el campo). `cultivos.csv` usa 0,35.
- **Heno:** el 0,95 / 1,05 / 1,00 de `cultivos.csv` es la fila "Rye Grass hay, averaged". FAO-56 también tiene "Rotated Grazing" (0,40 / 0,85–1,05 / 0,85).

## 3. Agua que deja cada cultivo para el siguiente

- **Alfalfa → maíz (MN).** En Lamberton, la alfalfa agotó más agua del perfil que todos los demás cultivos, pradera incluida. El orden de agotamiento y de uso de agua fue el mismo en todas las rotaciones y con ambos tipos de insumos: "alfalfa ≥ corn ≥ oat/alfalfa ≥ soybean" (Garcia y Garcia y Strock 2018, resumen). El resumen no cuantifica cuánta agua queda para el maíz siguiente.
- **Alfalfa → maíz (guías de extensión).** Los resultados del buscador citan a la Universidad de Minnesota ("soil moisture following alfalfa can be limiting in areas of low precipitation or low soil water-holding capacity"; recomienda terminar la alfalfa antes si se espera poca humedad). También citan un trabajo en un franco del noreste de Iowa: la alfalfa puede bajar el rendimiento del maíz siguiente en años secos si el perfil no se recarga en otoño o primavera. **No pude abrir ninguna de las dos fuentes** (la página de UMN devolvió 403 y la de Iowa es un resumen de terceros). Lo dejo como pista, no como dato.
- **Trigo → maíz y maíz → trigo (KS, Tribune, 2013–2016, Tabla 4).**
  - El agua disponible en el perfil a la siembra del maíz fue de 13,71 in (348 mm) después del trigo, 13,68 in (347 mm) en maíz continuo y 11,89 in (302 mm) después del sorgo.
  - Lo que se acumuló en el barbecho fue de 3,62 in (92 mm), 3,17 in (81 mm) y 2,68 in (68 mm), respectivamente.
  - Pero la eficiencia del barbecho (fracción de la lluvia que queda en el suelo) fue la más baja después del trigo: **24 %**, contra 36 % en maíz continuo y 53 % después del sorgo. El trigo se cosecha en julio y el barbecho largo pierde mucho por evaporación.
  - El trigo sembrado después del maíz arrancó con 10,41 in (264 mm) y sin acumulación de barbecho: se siembra apenas se cosecha el maíz.
  - El uso de agua del maíz fue el mismo en las tres rotaciones (≈ 25,1–25,2 in), y el rendimiento del maíz después del trigo o del sorgo fue mayor que en maíz continuo (184 y 183 bu/a contra 170 bu/a, Tabla 2).
- **Fuera de la temporada (NE).** Entre cosecha y siembra se pierden de 100 a 172 mm por evaporación. Cuanto más rastrojo, menos se pierde (Suyker y Verma 2009). Esto es lo que se pierde de la recarga invernal antes de cada cultivo de verano.

## 4. Lo que no se encontró o no se pudo abrir

- **IA, IL, IN y OH: no tengo totales de ET de la temporada medidos.**
  - Hatfield y Prueger (USDA-ARS, Ames) tienen eddy covariance continua sobre maíz y soja en el centro de Iowa desde 2004, y Dold et al. (2019) informan una ET anual de 589 a 610 mm en rotaciones maíz-soja. Ese último dato **solo lo vi en el texto del buscador**: DOAJ y el catálogo devolvieron 403.
  - AmeriFlux US-Bo1 (Bondville, IL, maíz-soja en siembra directa desde 1986) tiene los datos crudos. Habría que bajarlos y procesarlos (no se hizo).
- **Ohio:** las referencias a los lisímetros de pesada de Coshocton (Harrold y Dreibelbis) aparecen solo citadas en documentos de terceros. El PDF de Iowa de 1958 que las cita devolvió 403.
- **Guía de UMN sobre la rotación alfalfa-maíz** (extension.umn.edu): 403.
- **Alfalfa en NE y KS:** hay mediciones con lisímetro en Mead de los años 60 y 70 (las vi solo en resultados del buscador; core.ac.uk y scilit devolvieron 403). La circular EC765 de UNL trata de la ET de referencia de alfalfa, no de la ET del cultivo, y su PDF devolvió 403.
- **Avena sola, heno de gramíneas, trébol y centeno de cobertura:** sin mediciones abiertas en la zona.
- **Variación de la ET de la temporada año por año en Mead:** el resumen solo da medias y desvíos del Kc. Para la serie completa hay que leer el paper (Agric. For. Meteorol. 149: 443–452) o procesar los datos de AmeriFlux US-Ne1, US-Ne2 y US-Ne3.
- Tabla del trigo de Kanemasu 1977: la figura no se lee bien en el PDF escaneado.

## 5. Propuesta de regla para la herramienta (no aplicada)

Para estimar el agua que consume una rotación en un condado:

1. `ET_temporada(cultivo, año) = Σ Kc(día) × ET₀(día)`, con `eto_pm_mm` de `clima_diario.csv` y las etapas de `cultivos.csv`.
2. **Corregir el Kc de mitad de temporada** con un factor medido en la zona, en lugar de usar el de FAO-56 sin ajustar:
   - maíz: 1,03/1,20 ≈ 0,86 con riego y 0,84/1,20 ≈ 0,70 en secano;
   - soja: 0,98/1,15 ≈ 0,85 con riego y 0,90/1,15 ≈ 0,78 en secano (Mead).
   - Antes hay que confirmar la referencia de ET₀ en el texto completo de Suyker y Verma 2009.
3. Sumar la evaporación fuera de la temporada: 100–172 mm por año en Mead, menos cuanto más rastrojo.
4. Agua que queda para el cultivo siguiente: usar como regla cualitativa el orden de agotamiento de Lamberton (alfalfa ≥ maíz ≥ avena/alfalfa ≥ soja), y en el oeste (KS, NE) las mediciones de barbecho de Tribune. No hay un valor en mm por condado que se pueda generalizar.
5. Verificar contra los totales medidos de la sección 1: maíz de 480 a 550 mm en NE y MN en secano, soja de 430 a 490 mm, alfalfa ≈ 650 mm.

Fuentes:
- [Suyker, A. E. y Verma, S. B. (2009). Evapotranspiration of irrigated and rainfed maize–soybean cropping systems. Agricultural and Forest Meteorology, 149: 443–452 (resumen en el registro de manuscript.isc.ac)](https://manuscript.isc.ac/Inventory/10/959858.htm), consultado 2026-11-15. El PDF de core.ac.uk devolvió 403.
- [Suyker y Verma, "Evapotranspiration of irrigated and rainfed maize and soybean", 28th Conf. on Agricultural and Forest Meteorology (AMS), 2008 (resumen sin números)](https://ams.confex.com/ams/28Hurricanes/webprogram/Paper139091.html), consultado 2026-11-15.
- [Garcia y Garcia, A. y Strock, J. S. (2018). Soil water content and crop water use in contrasting cropping systems. Transactions of the ASABE 61(1): 75–86, doi:10.13031/trans.12118 (resumen)](https://experts.umn.edu/en/publications/soil-water-content-and-crop-water-use-in-contrasting-cropping-sys/), consultado 2026-11-15. También en [AGRIS](https://agris.fao.org/search/en/records/65df597bb766d82b18015cd2).
- [Lamm, F. R., Manges, H. L., Stone, L. R., Khan, A. H. y Rogers, D. H. (1995). Water requirement of subsurface drip-irrigated corn in northwest Kansas. Transactions of the ASAE 38(2): 441–448](https://www.milab.ksu.edu/sites/milab/files/Trans%20of%20ASAE%2038-2%20Corn%20Water%20Req.pdf), consultado 2026-11-15 (PDF completo, Tabla 1).
- [Schlegel, A. (2017). Alternative Cropping Systems with Limited Irrigation. Kansas Agricultural Experiment Station Research Reports 3(5), doi:10.4148/2378-5977.7396](https://ksu.janeway.systems/kaesrr/article/6345/galley/6289/download), consultado 2026-11-15 (PDF completo, Tablas 1–4).
- [Kanemasu, E. T. (1977). Evapotranspiration from Corn, Sorghum, Soybean, and Winter Wheat. Kansas Agricultural Experiment Station Research Reports, Keeping up with Research, doi:10.4148/2378-5977.7277](https://journals.newprairiepress.org/kaesrr/article/7470/galley/7401/download/), consultado 2026-11-15 (PDF escaneado; las figuras se leen mal).
- [Irmak, S. (2009). Magnitude and Trends of Reference Evapotranspiration Rates in South Central Nebraska. UNL Extension EC765 (solo la página de resumen)](https://digitalcommons.unl.edu/biosysengfacpub/460), consultado 2026-11-15. Es ET de referencia, no de cultivo.
- [Allen, R. G., Pereira, L. S., Raes, D. y Smith, M. (1998). FAO Irrigation and Drainage Paper 56, cap. 6 (Tabla 12, ecuaciones 62 y 65, Recuadro 14, Ejemplo 27)](https://www.fao.org/4/x0490e/x0490e0b.htm), consultado 2026-11-15.
- `config/cultivos.csv` y `docs/research/cultivos_fuentes.csv` (Kc de la Tabla 12 de FAO-56), en el repo.

Confianza:
- **alta** para los números de Mead, Colby y Tribune: son mediciones o balances publicados, leídos en el resumen o en el texto completo;
- **media** para la conclusión de que los Kc de FAO-56 sobreestiman en la zona: viene de un solo sitio (Mead), y no confirmé la referencia de ET₀;
- **baja** para trigo, avena, heno y para el efecto de la alfalfa sobre el maíz siguiente: hay pocos datos, son viejos, de fuera del este del Corn Belt o solo cualitativos.

Impacto:
- `config/cultivos.csv`: proponer columnas nuevas, como `kc_med_medido`, `et_temporada_mm_medida` y `fuente_et`, o un factor de corrección del Kc de mitad de temporada para maíz y soja. Requiere el OK del humano porque cambia `config/`.
- Regla de agua de la herramienta (skill de ML, sección 8).
- Paquete `clima`: `eto_pm_mm` y `deficit_mm` ya sirven de insumo.
- Pendiente para otra tarea: procesar los datos de AmeriFlux (US-Ne1, US-Ne2, US-Ne3, US-Bo1 y los sitios de Iowa) para tener la ET de la temporada año por año en la zona.
