# Carbono del suelo y erosión según la rotación

Pregunta: Para armar reglas con fuente (skill de ML, sección 8) sobre lo que el modelo no predice: (1) ¿qué factores C de RUSLE/RUSLE2 corresponden a maíz continuo, maíz–soja, maíz–soja–trigo y rotaciones con alfalfa, con y sin labranza cero? (2) ¿a qué tasa cambia el carbono orgánico del suelo (t C/ha/año) según la rotación y la labranza en ensayos de largo plazo del Corn Belt? (3) ¿cuánto rastrojo aporta cada cultivo y cómo se relaciona con `config/cultivos.csv` (`rastrojo_t_ms_ha`, `rastrojo_cn`)?

Respuesta corta:

1. **Factor C.** No encontré una tabla de RUSLE2 por rotación para los estados del Corn Belt: RUSLE2 calcula el C con su base de datos de operaciones y clima, no lo publica en tablas. La tabla abierta más útil es la **Tabla 2a-1 del NRCS de Missouri** (eFOTG): C por año de cultivo según el cultivo anterior y la labranza (arado, cincel con 20–70 % de cobertura, siembra directa con 20–90 %). Con ella, el C anual de la rotación (promedio de los años, cuenta mía) da, con arado de otoño: maíz continuo 0,36; maíz–soja 0,41; maíz–soja–trigo 0,30; maíz–maíz–avena–alfalfa 0,18. Con siembra directa (70 % de cobertura en lo que sigue a maíz o trigo, 30 % en el maíz que sigue a soja): maíz continuo 0,06; maíz–soja 0,13; maíz–soja–trigo 0,07. La soja deja menos rastrojo y por eso sube el C del cultivo siguiente. Un ensayo de 7 años en Missouri (Alberts et al. 1985) **midió** factores C 2 a 7 veces más bajos que los del Handbook 537 en que se basan esas tablas, y C de soja ≈ 2 veces el del maíz con cualquier labranza. Conviene usar los C como **valores relativos** entre rotaciones, no como pérdida absoluta.
2. **Carbono del suelo.** La única cifra general con fuente es el metaanálisis global de West y Post (2002): pasar de labranza convencional a siembra directa secuestra **0,57 ± 0,14 t C/ha/año** (pico a los 5–10 años, nuevo equilibrio a los 15–20); complejizar la rotación, **0,20 ± 0,12 t C/ha/año** (equilibrio a los 40–60 años), **salvo pasar de maíz continuo a maíz–soja, que puede no aumentar el carbono**. Los ensayos del Corn Belt que abrí no encontraron efecto de la rotación en el carbono total: Indiana, 24 años (Omonode et al. 2006); Lamberton, Minnesota, 10 años (Huggins et al. 1998, según el resumen); Brookings, Dakota del Sur, 10 años con labranza convencional, incluso con alfalfa (Pikul et al. 2001). La labranza sí pesa: en Indiana, la siembra directa continua tenía 151 t C/ha hasta 1 m contra 108 del cincel continuo después de 24 años (≈ 1,8 t C/ha/año de diferencia, cuenta mía). En Ohio, una cronosecuencia de siembra directa con centeno de cobertura dio 0,59 ± 0,13 t C/ha/año en 0–15 cm (0,47 con masa equivalente), con meseta a los ~15 años.
3. **Rastrojo.** El maíz es el que más aporta: con índice de cosecha de 0,53, deja ≈ 7,5 t/ha de rastrojo seco con 9,8 t/ha de grano (156 bu/ac), igual al 7,5 de `cultivos.csv`. La soja, con índice de 0,46, deja ≈ 2,4 t/ha con 2,3 t/ha de grano (Johnson et al. 2006), y se descompone más rápido (Alberts et al. 1985). Para que el carbono no baje hacen falta ≈ 5,3 t/ha/año de rastrojo de maíz con cincel o siembra directa y 7,6 con arado (maíz continuo); en maíz–soja, 7,9 y 12,5 t/ha en el año de maíz. Una revisión posterior con más sitios dio 3,9 ± 2,2 t/ha/año (sitios con datos suficientes), 6,4 ± 2,2 (sitios de maíz) y 5,7 ± 2,4 (todos), y desaconseja un único valor genérico. No encontré cifras abiertas de aporte de rastrojo de alfalfa, heno ni trébol en t/ha.

Detalle:

## 1. Factores C (erosión hídrica, USLE/RUSLE)

### Tabla 2a-1 del NRCS de Missouri ("C" factors for cropland in Missouri)

Valores por **año de cultivo**, para manejo alto (maíz ≥ 100 bu/ac, soja ≥ 40, trigo ≥ 45, avena ≥ 60, pradera ≥ 3 t/ac; con manejo medio se multiplica por 1,2). "Cincel" es una labranza primaria de otoño más 0–2 secundarias. La pradera de la tabla tiene al menos 50 % de gramíneas; si es sobre todo leguminosa (alfalfa), los valores de "después de pradera" se multiplican por 1,2.

| Cultivo (después de) | Arado otoño | Arado primavera | Cincel 30 % | Cincel 50 % | Siembra directa 70 % | Siembra directa 90 % |
|---|---|---|---|---|---|---|
| Maíz después de maíz | 0,36 | 0,29 | 0,18 | 0,12 | 0,06 | 0,03 |
| Maíz después de cereal de invierno | 0,37 | 0,30 | 0,20 | 0,13 | 0,06 | 0,03 |
| Maíz después de pradera | 0,17 | 0,13 | 0,10 | 0,08 | 0,02 | 0,01 |
| Maíz 2.º año después de pradera | 0,32 | 0,24 | 0,16 | 0,14 | 0,04 | 0,02 |
| Soja (surcos > 20") después de maíz | 0,40 | 0,33 | 0,20 | 0,13 | 0,07 | 0,03 |
| Soja (surcos > 20") después de cereal | 0,43 | 0,34 | 0,23 | 0,14 | 0,06 | 0,03 |
| Soja (surcos > 20") después de pradera | 0,20 | 0,15 | 0,10 | 0,08 | 0,02 | 0,01 |

Para los cultivos que siguen a soja, la tabla usa otras columnas de cobertura (20–50 %, porque la soja deja poco rastrojo):

| Cultivo (después de soja) | Arado otoño | Arado primavera | Siembra directa 20 % | 30 % | 40 % | 50 % | 80 % con cobertura invernal |
|---|---|---|---|---|---|---|---|
| Maíz después de soja | 0,42 | 0,36 | 0,25 | 0,19 | 0,14 | 0,13 | — |
| Maíz después de soja con cultivo de cobertura | 0,41 | 0,30 | 0,17 | 0,13 | 0,12 | 0,10 | 0,07 |
| Soja (> 20") después de soja | 0,48 | 0,41 | 0,26 | 0,20 | 0,16 | 0,15 | — |
| Cereal de invierno después de soja | 0,14 | 0,12 | 0,09 | 0,07 | 0,05 | 0,03 | — |

Otros: cereal de invierno después de maíz, 0,12 con arado de otoño; pradera establecida todo el año, **0,004 (gramínea–leguminosa) y 0,020 (leguminosa)**. Trigo/soja de segunda (doble cultivo): de 0,04 (trigo y soja en siembra directa después de maíz) a 0,28 (todo arado, después de soja).

El texto viene de extraer el PDF con `pdftotext`: las filas con 12 valores se leen sin ambigüedad. La fila "cereal de invierno después de maíz" tiene un valor de más en la zona de siembra directa y no la usé para siembra directa.

### C anual de cada rotación (cuenta mía con la tabla de arriba)

Promedio simple de los años de la rotación. Supuesto: la tabla da un C anual por año de cultivo, así que el C de la rotación es el promedio; el NRCS lo pondera por la erosividad, que acá ya está incluida año a año.

| Rotación | Arado otoño | Siembra directa |
|---|---|---|
| Maíz continuo | 0,36 | 0,06 (70 % cobertura) |
| Maíz–soja | (0,42 + 0,40) / 2 = **0,41** | (0,19 maíz con 30 % + 0,07 soja con 70 %) / 2 = **0,13** |
| Maíz–soja–trigo (maíz después de trigo) | (0,37 + 0,40 + 0,14) / 3 = **0,30** | (0,06 + 0,07 + 0,07) / 3 = **0,07** |
| Maíz–maíz–avena–alfalfa (pradera de leguminosa, ×1,2) | (0,17×1,2 + 0,32×1,2 + 0,12 + 0,020) / 4 = **0,18** | no calculado (fila del cereal ambigua) |

Lectura: con arado, el maíz–soja erosiona algo más que el maíz continuo (la soja deja poco rastrojo). La siembra directa baja el C 3 a 6 veces en todas las rotaciones. Un año de alfalfa o pradera en la rotación lo baja a la mitad con arado.

### Ensayo con medición: Alberts, Wendt y Burwell (1985)

Parcelas de escurrimiento con lluvia natural, suelo con claypan (serie Mexico), centro de Missouri (MLRA 113), 1971–1977. Maíz continuo y soja continua con tres labranzas. Factor C anual **medido** vs. el del Agricultural Handbook 537:

| Labranza | Maíz medido | Maíz AH 537 | Soja medida | Soja AH 537 |
|---|---|---|---|---|
| Convencional (arado) | 0,08 | 0,28 | 0,18 | 0,39 |
| Cultivador de campo | 0,04 | 0,09 | 0,08 | 0,24 |
| Siembra directa | 0,01 | 0,04 | 0,02 | 0,15 |

Ponderados con la distribución de erosividad del AH 537 (área 16), los medidos suben a 0,12 / 0,06 / 0,02 (maíz) y 0,25 / 0,09 / 0,03 (soja). Los autores concluyen que los C del AH 537 son 2 a 7 veces más altos que los medidos y que la soja tiene ≈ 2 veces el C del maíz con cualquier labranza (más rastrojo y descomposición más lenta del maíz).

### Lo que no encontré

- Tablas de C de RUSLE2 para Iowa, Illinois, Indiana, Ohio, Nebraska, Minnesota o Kansas. RUSLE2 calcula el C a partir de plantillas de manejo y de clima por condado; habría que correr el programa (con la base de datos del NRCS) para cada rotación. No lo hice.
- Ninguna fuente abierta con C de rotaciones con alfalfa en siembra directa para el Corn Belt.
- La tabla de Missouri es del eFOTG y tiene la lógica del USLE (AH 537), no de RUSLE2. No dice año de revisión.

## 2. Cambio del carbono orgánico del suelo

| Fuente | Lugar y duración | Comparación | Resultado |
|---|---|---|---|
| West y Post (2002), SSSAJ 66:1930–1946 | Global: 67 ensayos de largo plazo, 276 pares | Labranza convencional → siembra directa | **+57 ± 14 g C/m²/año = 0,57 ± 0,14 t C/ha/año** (sin trigo–barbecho); pico a los 5–10 años, equilibrio a los 15–20 |
| ídem | ídem | Rotación más compleja | **+20 ± 12 g C/m²/año = 0,20 ± 0,12 t C/ha/año**, sin contar maíz continuo → maíz–soja, "which may not result in a significant accumulation of SOC"; equilibrio a los 40–60 años |
| Omonode, Gal, Stott, Abney y Vyn (2006), SSSAJ, doi:10.2136/sssaj2005.0083 | West Lafayette, Indiana (Chalmers, suelo oscuro de pradera mal drenado), 1980–2003 | Maíz continuo vs. soja–maíz; siembra directa vs. cincel vs. arado | Rotación **sin efecto** en el C y N a ninguna profundidad. Hasta 1 m (masa equivalente) a los 24 años: **151 t C/ha con siembra directa continua vs. 108 con cincel continuo**; pasar de arado (17 años) a siembra directa por 6–7 años dio 26 t C/ha más que el cincel |
| Pikul, Schumacher y Vigil (2001), The Scientific World Journal 1:707–713 | Brookings, Dakota del Sur (Barnes), 1990–2000, labranza convencional | Maíz continuo, maíz–soja, maíz–soja–trigo/alfalfa–alfalfa, pasturas | En 0–15 cm el C **bajó 1,7 g/kg en las tres rotaciones, con alfalfa también**; no cambió con caballones (maíz–soja); subió 0,7 g/kg bajo pastura perenne. "No gain in soil C after 10 years regardless of rotation" |
| Khosa et al. (2025), PLoS One 20(5):e0322891 | Fairfield County, centro de Ohio, maíz–soja con centeno de cobertura; lotes con 6, 20 y 35 años de siembra directa y uno con cincel | Cronosecuencia (lotes distintos, no ensayo con repeticiones) | 0–15 cm: **587 ± 134 kg C/ha/año** (profundidad fija) o 468 ± 168 (masa equivalente), con meseta a los ~15 años; 15–30 cm: 192 ± 64 (lineal). C 14–69 % mayor que con cincel |
| Collins et al. (1999), SSSAJ 63:584–591 | 8 sitios del Corn Belt con maíz continuo por 8 a 35 años | Cultivado vs. no cultivado vecino | El carbono de los suelos cultivados es en promedio **68 % menor**; 22–40 % del C actual viene del maíz; tiempo de residencia del C previo de 36 a 108 años en superficie |

Abiertos solo por el resumen (en la búsqueda, sin el texto completo; no usar sin verificar):

- Huggins et al. (1998), SSSAJ: Lamberton, Minnesota, desde 1981; a los 10 años el C total era similar en maíz continuo, soja continua y secuencias maíz–soja.
- Russell, Laird, Parkin y Mallarino (2005), SSSAJ 69:413–422: dos sitios de Iowa con 23 y 48 años; maíz continuo, maíz–soja, maíz–maíz–avena–alfalfa y maíz–avena–alfalfa–alfalfa. El N aumentó el C solo en maíz continuo en un sitio; el C particulado siguió el orden maíz–soja < maíz continuo < maíz–maíz–avena–alfalfa. El repositorio de Iowa State devolvió 403 y no pude leer las cifras.

Lectura para una regla:

- **Labranza:** es el efecto con más respaldo. Usar +0,57 t C/ha/año (± 0,14) los primeros ~15–20 años después de pasar a siembra directa, y 0 después (nuevo equilibrio). En el Corn Belt, Ohio da un valor parecido (0,47–0,59 en 0–15 cm). Ojo con la profundidad: muchos ensayos con muestreo solo superficial no detectan cambios o encuentran redistribución.
- **Rotación:** pasar de maíz continuo a maíz–soja **no** cambia el carbono (West y Post; Omonode en Indiana; Huggins en Minnesota). Agregar trigo o alfalfa: +0,20 ± 0,12 t C/ha/año como promedio mundial, pero el único ensayo del Corn Belt que pude leer con alfalfa (Dakota del Sur, 10 años, arado) no encontró ganancia. La regla tendría que mostrar el rango y una confianza baja.
- **Maíz continuo vs. maíz–soja:** la soja aporta menos rastrojo, pero los ensayos no muestran menos C total en el corto plazo.

## 3. Rastrojo de cada cultivo y relación con `config/cultivos.csv`

| Fuente | Dato |
|---|---|
| Johnson, Reicosky, Allmaras, Archer y Wilhelm (2006), J. Soil Water Conserv. 61(4) | Índice de cosecha del maíz moderno 0,53: con 9,8 t/ha de grano (156 bu/ac) quedan **7,5 t/ha de rastrojo seco**; en la tabla 1, rastrojo ≈ 0,77 × grano (15,5 % de humedad): 6,5 → 5,0; 13,1 → 10,0; 16,3 → 12,5 t/ha. Soja: índice 0,46, **2,4 t/ha de rastrojo seco con 2,3 t/ha de grano** (34,3 bu/ac). Para mantener el C: maíz continuo **7,6 ± 1,0 t/ha/año con arado y 5,3 ± 0,1 con cincel o siembra directa**; maíz–soja **12,5 (arado) y 7,9 (cincel o directa) t/ha en el año de maíz**. En Minnesota oeste, devolver 8,25 t/ha/año por 29 años con arado de otoño no evitó la pérdida de C |
| Johnson, Novak, Varvel et al. (2014), BioEnergy Research 7:481–490 | Corn Stover Regional Partnership: mínimo de rastrojo para mantener el C **3,9 ± 2,18 t/ha/año** en los sitios con datos suficientes; 6,38 ± 2,19 en sitios de maíz (n = 35) y 5,74 ± 2,36 en todos (n = 49). Los autores dicen que ~6 t/ha/año "maybe a useful generic rate" pero que un valor universal no está respaldado |
| Alberts et al. (1985) | Con 7,8 t/ha de maíz y 2,1 t/ha de soja, el maíz produce ≈ 2,5 veces más rastrojo, y se descompone más lento en el primer medio año |

Relación con `config/cultivos.csv`:

- `maiz.rastrojo_t_ms_ha = 7.5` coincide con Johnson et al. (2006) para 156 bu/ac. Como el rastrojo escala con el rendimiento, una regla mejor sería **rastrojo ≈ 0,77 × grano (t/ha a 15,5 %)**, es decir ≈ 0,048 × `rend_bu_ac` en t/ha (cuenta mía: 0,77 × 62,77 kg/ha por bu/ac).
- `soja.rastrojo_t_ms_ha = 3.1` (Ontario) es más alto que el 2,4 t/ha de Johnson (con 34 bu/ac, rendimiento de 2003). Con índice de cosecha 0,46 y 13 % de humedad, el rastrojo ≈ 1,02 × grano: con 55 bu/ac (3,7 t/ha) da ≈ 3,8 t/ha (cuenta mía). Los dos valores son compatibles con distintos rendimientos.
- C:N: no encontré fuentes nuevas abiertas; los valores actuales (`maiz` 57, `soja` 65, `trigo_invierno` 80) siguen siendo los de `cultivos_zona.md`.
- Alfalfa, heno y trébol: siguen sin dato de rastrojo en t/ha. En las tablas de erosión entran como "pradera" con C 0,004–0,020, no por la masa de rastrojo.

Propuesta de regla (para la sección 8 del skill de ML, no aplicada):

1. **Erosión relativa** = C anual de la rotación de la tabla de Missouri (sección 1), mostrada como índice relativo a maíz–soja con arado (0,41 = 1). No multiplicar por R, K y LS para dar t/ha sin correr RUSLE2.
2. **Cambio de C del suelo** = +0,57 t C/ha/año durante 15–20 años si se pasa a siembra directa; +0,20 (rango 0,08–0,32) si se suma trigo, avena o alfalfa a maíz–soja, con confianza baja en el Corn Belt; 0 para maíz continuo ↔ maíz–soja.
3. **Balance de rastrojo** = rastrojo estimado del rendimiento (maíz 0,77 × grano a 15,5 %; soja 1,02 × grano a 13 %) comparado con el mínimo de Johnson et al. (5,3 t/ha con cincel o directa, 7,6 con arado, maíz continuo); avisar si se cosecha rastrojo por debajo de ese mínimo.

Fuentes:

- [Table 2a-1: "C" Factors for Cropland in Missouri, USDA NRCS eFOTG (Table_2a_rev.pdf)](https://efotg.sc.egov.usda.gov/references/public/MO/Table_2a_rev.pdf), consultado 2026-11-15
- [Alberts, Wendt y Burwell (1985). Corn and soybean cropping effects on soil losses and C factors. SSSAJ 49:721–728 (PDF del USDA-ARS)](https://ars.usda.gov/ARSUserFiles/50701000/cswq-t5595-alberts.pdf), consultado 2026-11-15
- [West y Post (2002). Soil organic carbon sequestration rates by tillage and crop rotation: a global data analysis. SSSAJ 66:1930–1946 (registro EPA HERO con el resumen)](https://heronext.epa.gov/reference/4593305), consultado 2026-11-15. El registro del dataset en OSTI ([1389519](https://www.osti.gov/dataexplorer/biblio/dataset/1389519)) dice 14 ± 11 g C/m²/año para la rotación; usé el 20 ± 12 del resumen del artículo
- [Omonode et al. (2006). Short-term versus continuous chisel and no-till effects on soil carbon and nitrogen. SSSAJ (PDF de Purdue)](https://www.agry.purdue.edu/staffbio/SSSAJ_Omonode.pdf), consultado 2026-11-15
- [Pikul, Schumacher y Vigil (2001). The Scientific World Journal 1:707–713 (PMC6084229)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6084229), consultado 2026-11-15
- [Khosa et al. (2025). Long-term continuous no-till corn-soybean systems: examining soil carbon sequestration and nitrogen accumulation across various pools. PLoS One 20(5):e0322891](https://pmc.ncbi.nlm.nih.gov/articles/PMC12064199/), consultado 2026-11-15
- [Collins et al. (1999). Soil carbon dynamics in corn-based agroecosystems: results from carbon-13 natural abundance. SSSAJ 63:584–591](https://mountainscholar.org/bitstream/10217/85544/1/NREL_Paul_Collins_sssaj_63_584-591.pdf), consultado 2026-11-15
- [Johnson, Reicosky, Allmaras, Archer y Wilhelm (2006). A matter of balance: conservation and renewable energy. J. Soil Water Conserv. 61(4) (PDF del USDA-ARS)](https://www.ars.usda.gov/ARSUserFiles/np202/REAPfiles/Johnson%20et%20al%20SWCJ%202006.pdf), consultado 2026-11-15
- [Johnson et al. (2014). Crop residue mass needed to maintain soil organic carbon levels: can it be determined? BioEnergy Research 7:481–490 (PDF del USDA-ARS)](https://www.ars.usda.gov/ARSUserFiles/60820500/Manuscripts/2014/Man942.pdf), consultado 2026-11-15
- Solo por el resumen en la búsqueda: Huggins et al. (1998), SSSAJ ([AGRIS](https://agris.fao.org/search/en/records/65df7fab4c5aef494fe30468)); Russell et al. (2005), SSSAJ 69:413–422 ([Iowa State, 403](https://dr.lib.iastate.edu/entities/publication/2e1ad59f-d37a-4912-9236-13af06327668))

Confianza: **media** para los factores C relativos (tabla oficial del NRCS, pero de Missouri y con la lógica del USLE; medidos más bajos en el único ensayo); **media** para la tasa de siembra directa (metaanálisis global, confirmado en orden de magnitud en Ohio e Indiana); **baja** para el efecto de la rotación en el C del Corn Belt (los ensayos que leí no lo encuentran); **alta** para el rastrojo del maíz y los mínimos de Johnson et al. (fuentes del USDA-ARS del Corn Belt).

Impacto: skill de ML (sección 8, reglas de lo que el modelo no predice: erosión y carbono); la herramienta (comparación de rotaciones). `config/cultivos.csv` no cambia: `maiz.rastrojo_t_ms_ha` (7,5) queda confirmado; `soja.rastrojo_t_ms_ha` (3,1) es compatible con rendimientos actuales. Ningún paquete de datos cambia; `suelo_terreno` ya entrega el factor K de RUSLE y la pendiente, que una regla absoluta de erosión necesitaría junto con R.
