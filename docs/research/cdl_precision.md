# Precisión del CDL por estado y año (2008–2025)

Pregunta: ¿Qué precisión del productor y del usuario tiene el Cropland Data Layer (CDL) para maíz, soja, trigo de invierno, avena, alfalfa y otro heno en IA, IL, IN, OH, NE, MN y KS, al menos en 2008, 2012, 2016, 2020, 2024 y 2025? ¿Dónde están las evaluaciones de precisión (URL y formato), se pueden bajar todas juntas, y qué estados o años conviene anotar en el data card de `cultivos`?

Respuesta corta: Maíz y soja son confiables en los 7 estados y en todos los años (precisión del productor y del usuario entre 85,8 y 99,1 %). Trigo de invierno es aceptable en KS, NE, OH e IN (≥ 73 %) pero malo en IA y MN (14–72 % del productor). Avena, alfalfa y otro heno son ruidosos en todos lados: la avena y el otro heno se subestiman mucho (precisión del productor típica de 10–50 %), y en 2024 el otro heno se sobreclasifica de forma extrema (precisión del usuario 0,6–7,7 %). Los peores estados para maíz y soja son **Kansas** (soja < 90 % en 11 de los 18 años) y **Ohio** (maíz < 90 % en 2017–2020; precisión global de cultivos 79,2 % en 2025). Hay dos cortes metodológicos que impiden comparar años: hasta 2016 la validación usaba polígonos con buffer interno de 30 m (precisión inflada) y desde 2017 sin buffer (caída de unos 5–7 puntos en la precisión global); en 2024 cambió el muestreo de validación (proporcional entre cultivo y no cultivo, y al tamaño del estado). Fuentes: para 2008–2023, los metadatos FGDC de cada estado y año en HTML (`.../cropland/metadata/metadata-<st><aa>`); para 2024 y 2025 ya no hay metadatos por estado y la precisión por estado está solo en `CDL_<año>_accuracy_assessments.zip` (un xlsx por estado, ~75 MB por año), en la página de FAQ del CDL. Hay un zip por año (2008–2025), con todos los estados: se pueden bajar "todos juntos" por año, no hay un único archivo para toda la serie. La tabla completa (7 estados × 18 años × 6 cultivos) está en `docs/research/cdl_precision.csv`, generada con `docs/research/cdl_precision_extraer.py`.

Detalle:

**1. Dónde están y en qué formato.**

| Años | Dónde | Formato | Verificado |
|---|---|---|---|
| 2008–2023 | `https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-<st><aa>` (p. ej. `metadata-ks12`) | HTML (FGDC), tabla de texto "STATEWIDE AGRICULTURAL ACCURACY REPORT" con, por clase: píxeles correctos, precisión del productor, error de omisión, kappa, precisión del usuario, error de comisión, kappa condicional | 112 páginas (7 × 16) bajadas, todas con HTTP 200 |
| 2024–2025 | `https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/CDL_<año>_accuracy_assessments.zip` | zip con un xlsx por estado (`NASS_CDL_<ST><aa>_accuracy.xlsx`); hoja "Summary Table" (productor, omisión, kappa, usuario, comisión, kappa, sesgo), hojas con la matriz de confusión completa ("All - Matrix", "All Crops - Matrix", etc.) | zips de 2024 (74,9 MB) y 2025 (75,4 MB) bajados; se leyeron los 14 xlsx |
| 2008–2025 | mismos zips `CDL_<año>_accuracy_assessments.zip`, enlazados desde la FAQ (`https://www.nass.usda.gov/research-and-science/cropland/sarsfaqs2`) | 59–121 MB por año (2008: 62,2 MB; 2012: 60,0 MB; 2016: 121,4 MB; 2020: 59,6 MB) | tamaños con HEAD; los de 2008–2023 no se abrieron (para esos años se usó el HTML) |

- `metadata-<st>24` y `metadata-<st>25` dan 404 para los 7 estados. La página de metadatos lo dice: "Beginning in 2024, metadata is only available at the national-level. State-level accuracy assessments can still be found on our FAQs webpage."
- Los metadatos nacionales de 2024 y 2025 (`metadata-cdl24-fgdc-std-001-1998`, `metadata-cdl25-...`) traen una tabla nacional (precisión global de cultivos FSA: 77,5 % en 2024 y 75,43 % en 2025), no por estado.
- En los xlsx los valores son fórmulas con el resultado guardado en caché; `openpyxl` con `data_only=True` lee los números (sin openpyxl se pueden leer igual con pandas + openpyxl, no hace falta Excel).
- Para un script: el HTML pesa ~110 kB por estado y año, así que bajar las 112 páginas es más liviano que los 16 zips de 2008–2023 (~1 GB).

**2. Cortes metodológicos (no comparar años entre sí sin tenerlos en cuenta).**
- **2008–2016:** validación con polígonos de la FSA con buffer interno de 30 m (no se evalúan los bordes de lote). La FAQ admite "modestly inflated accuracy measures". En 2016 NASS publicó las dos versiones; el HTML de 2016 no menciona la versión sin buffer y sus valores (precisión global 95–97 %) son del mismo nivel que 2013–2015, así que **supongo** que la tabla del HTML de 2016 es la con buffer (no lo verifiqué en el zip de 2016).
- **2017–2023:** validación sin buffer. La precisión global de cultivos cae ~6–7 puntos de 2016 a 2017 en todos los estados (IA 96,4 → 89,4 %; OH 95,9 → 84,2 %; KS 91,2 → 82,4 %). Es un cambio de método, no un CDL peor.
- **2024 en adelante:** CDL a 10 m (con versión de 30 m) y nuevo muestreo de validación: proporcional entre cultivo y no cultivo y proporcional al tamaño del estado ("the individual state statistics can be summed together to easily generate multi-state assessment statistics"). Por eso cambia mucho la cantidad de píxeles de validación (IA maíz: 340.138 en 2023, 140.137 en 2024).

**3. Precisión global de cultivos FSA (%) por estado y año** (códigos 1–61, 66–80, 92 y 200–255; columna `global_cultivos_fsa_pct` del CSV).

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| IA | 93,2 | 93,6 | 96,4 | 89,4 | 91,5 | 90,5 | 90,8 | 88,1 |
| IL | 93,8 | 92,8 | 96,7 | 89,0 | 90,2 | 90,2 | 90,8 | 88,0 |
| IN | 94,2 | 91,2 | 95,7 | 87,3 | 88,0 | 89,6 | 89,0 | 84,5 |
| OH | 91,7 | 87,4 | 95,9 | 84,2 | 84,9 | 87,1 | 83,8 | 79,2 |
| NE | 92,5 | 90,9 | 96,4 | 89,0 | 90,5 | 90,1 | 87,9 | 86,9 |
| MN | 94,6 | 93,9 | 95,4 | 88,7 | 90,1 | 90,3 | 88,5 | 87,0 |
| KS | 87,3 | 88,4 | 91,2 | 82,4 | 84,1 | 81,5 | 79,8 | 79,3 |

**4. Precisión por cultivo.** Cada celda: precisión del productor / precisión del usuario, en %. Productor = 1 − omisión (de los píxeles que en el terreno son ese cultivo, cuántos el CDL acierta); usuario = 1 − comisión (de los píxeles que el CDL dice que son ese cultivo, cuántos lo son). "—" = la clase no aparece en la tabla de ese estado y año. Los demás años (2009–2011, 2013–2015, 2017–2019, 2021–2023) están en el CSV.

Maíz (código 1):

| Estado | 2008 | 2012 | 2016 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| IA | 96,9 / 98,6 | 96,6 / 98,3 | 98,5 / 98,8 | 95,3 / 97,5 | 95,4 / 96,4 | 95,8 / 94,2 |
| IL | 97,4 / 98,8 | 97,7 / 96,0 | 98,4 / 98,6 | 93,0 / 96,7 | 94,4 / 95,8 | 94,1 / 94,2 |
| IN | 97,3 / 98,0 | 96,3 / 94,3 | 97,9 / 97,5 | 91,4 / 94,4 | 93,3 / 94,8 | 92,5 / 92,0 |
| OH | 95,6 / 97,5 | 93,8 / 91,8 | 97,3 / 97,7 | 88,0 / 92,9 | 91,9 / 90,2 | 90,7 / 89,4 |
| NE | 97,5 / 97,8 | 96,9 / 96,6 | 99,1 / 98,3 | 95,7 / 96,3 | 95,0 / 95,9 | 96,0 / 94,1 |
| MN | 98,1 / 98,8 | 97,4 / 98,0 | 98,2 / 98,2 | 94,5 / 96,8 | 95,0 / 95,0 | 95,9 / 93,5 |
| KS | 93,0 / 95,3 | 93,2 / 94,6 | 96,4 / 96,4 | 92,0 / 93,6 | 91,7 / 92,2 | 92,6 / 91,8 |

Soja (código 5):

| Estado | 2008 | 2012 | 2016 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| IA | 96,0 / 97,9 | 95,6 / 97,0 | 98,0 / 98,4 | 94,5 / 96,2 | 95,1 / 95,2 | 94,9 / 93,7 |
| IL | 95,7 / 96,3 | 96,4 / 94,7 | 97,7 / 97,9 | 92,2 / 95,2 | 93,9 / 94,8 | 93,8 / 92,5 |
| IN | 97,1 / 97,3 | 95,6 / 94,0 | 97,4 / 97,7 | 90,7 / 94,7 | 93,5 / 94,5 | 92,5 / 91,0 |
| OH | 97,5 / 96,8 | 94,4 / 93,6 | 98,0 / 98,1 | 91,1 / 92,9 | 91,5 / 93,6 | 91,1 / 91,1 |
| NE | 96,6 / 96,7 | 94,0 / 96,0 | 98,0 / 98,6 | 93,5 / 96,4 | 95,2 / 94,0 | 95,7 / 92,8 |
| MN | 98,3 / 97,9 | 97,3 / 96,9 | 98,0 / 97,0 | 94,9 / 94,3 | 93,4 / 94,5 | 94,7 / 93,4 |
| KS | 91,6 / 92,6 | 89,9 / 90,6 | 94,4 / 95,0 | 89,4 / 91,9 | 90,2 / 88,3 | 91,0 / 87,2 |

Trigo de invierno (código 24):

| Estado | 2008 | 2012 | 2016 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| IA | 14,1 / 53,4 | 51,9 / 74,4 | 21,7 / 53,1 | 28,5 / 47,0 | 69,5 / 69,1 | 47,5 / 69,7 |
| IL | 63,8 / 78,9 | 60,2 / 73,7 | 70,8 / 78,4 | 51,8 / 74,8 | 76,8 / 63,7 | 62,7 / 82,0 |
| IN | 84,9 / 88,8 | 83,3 / 83,3 | 89,9 / 89,4 | 76,4 / 78,8 | 78,2 / 76,2 | 79,1 / 77,7 |
| OH | 93,9 / 91,6 | 89,3 / 86,6 | 97,3 / 94,1 | 85,1 / 83,7 | 80,4 / 78,5 | 78,9 / 73,7 |
| NE | 89,4 / 95,5 | 94,7 / 94,2 | 96,7 / 96,8 | 86,9 / 88,7 | 89,1 / 84,0 | 86,7 / 82,5 |
| MN | 71,7 / 91,3 | 67,4 / 86,3 | 34,1 / 77,7 | 16,8 / 59,5 | 39,5 / 49,0 | 42,0 / 76,3 |
| KS | 94,0 / 94,3 | 95,4 / 94,5 | 95,9 / 95,2 | 91,1 / 90,4 | 89,3 / 88,8 | 90,2 / 86,8 |

Avena (código 28):

| Estado | 2008 | 2012 | 2016 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| IA | 8,0 / 61,7 | 42,7 / 63,2 | 30,3 / 54,6 | 40,9 / 66,3 | 74,7 / 56,8 | 53,2 / 73,2 |
| IL | 14,5 / 89,3 | 15,7 / 56,8 | 25,3 / 69,5 | 37,6 / 67,7 | 75,4 / 69,9 | 54,8 / 77,8 |
| IN | 0,4 / 11,6 | 8,2 / 50,0 | 37,0 / 96,0 | 23,6 / 73,2 | 38,7 / 48,0 | 22,6 / 63,2 |
| OH | 34,4 / 79,8 | 19,6 / 54,7 | 63,9 / 80,7 | 26,0 / 54,8 | 52,2 / 54,5 | 19,0 / 66,7 |
| NE | 27,6 / 72,4 | 31,1 / 72,9 | 74,8 / 83,3 | 31,1 / 47,6 | 58,6 / 36,9 | 51,0 / 69,0 |
| MN | 15,3 / 47,6 | 20,2 / 44,0 | 19,5 / 40,8 | 24,2 / 53,4 | 61,2 / 29,3 | 51,6 / 67,6 |
| KS | 6,2 / 68,5 | 19,8 / 60,0 | 27,6 / 65,4 | 27,7 / 54,8 | 68,0 / 47,2 | 50,9 / 68,5 |

Alfalfa (código 36):

| Estado | 2008 | 2012 | 2016 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| IA | 30,7 / 81,4 | 62,3 / 68,1 | 63,1 / 72,3 | 48,0 / 66,3 | 74,9 / 54,4 | 50,5 / 63,5 |
| IL | 23,5 / 80,3 | 30,5 / 59,6 | 52,1 / 69,1 | 34,5 / 59,7 | 70,6 / 44,2 | 42,8 / 63,9 |
| IN | 45,1 / 80,7 | 45,1 / 62,3 | 56,4 / 71,9 | 50,0 / 66,1 | 67,5 / 40,6 | 46,9 / 58,3 |
| OH | 48,2 / 75,7 | 43,7 / 63,9 | 74,4 / 83,3 | 46,7 / 62,8 | 74,1 / 37,4 | 46,0 / 56,4 |
| NE | 77,1 / 93,8 | 64,8 / 89,0 | 88,2 / 92,1 | 76,2 / 78,4 | 86,5 / 63,0 | 76,1 / 73,3 |
| MN | 62,9 / 88,4 | 76,7 / 69,3 | 80,0 / 82,9 | 67,7 / 73,9 | 77,9 / 63,3 | 65,2 / 65,7 |
| KS | 81,1 / 94,9 | 75,4 / 88,8 | 86,8 / 91,3 | 76,4 / 82,7 | 88,7 / 60,3 | 81,1 / 80,8 |

Otro heno / no alfalfa (código 37):

| Estado | 2008 | 2012 | 2016 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| IA | 3,1 / 45,9 | 50,0 / 26,2 | 13,8 / 39,9 | 11,1 / 40,1 | 41,1 / 0,6 | 19,0 / 14,1 |
| IL | 4,7 / 59,5 | 7,0 / 35,3 | 15,5 / 54,1 | 9,6 / 34,3 | 47,5 / 1,2 | 17,5 / 21,0 |
| IN | 16,4 / 69,2 | 12,7 / 35,8 | 22,6 / 53,1 | 19,8 / 45,9 | 44,4 / 2,1 | 19,6 / 18,5 |
| OH | 27,1 / 66,1 | 19,1 / 43,4 | 46,4 / 83,4 | 33,3 / 50,2 | 52,8 / 1,0 | 26,8 / 22,3 |
| NE | 10,9 / 79,2 | 19,8 / 84,4 | 43,5 / 77,8 | 21,5 / 50,4 | 45,3 / 1,3 | 27,2 / 20,3 |
| MN | 20,9 / 66,8 | 37,6 / 29,8 | 24,1 / 45,0 | 20,7 / 39,0 | 31,1 / 7,7 | 19,4 / 24,8 |
| KS | 28,1 / 87,5 | — / — | 39,1 / 71,2 | 34,9 / 65,5 | 65,8 / 4,3 | 39,2 / 26,3 |

La clase 37 tampoco aparece en las tablas HTML de NE y KS 2010, e IN, OH, NE y KS 2011 (el nombre está en la leyenda de la página, pero no hay fila de precisión).

**5. Qué anotar en el data card de `cultivos` (Problemas conocidos).**
- **Maíz y soja: confiables.** En los 7 estados y los 18 años, precisión del productor y del usuario ≥ 85,8 %. Por debajo de 90 % solo hay: soja de KS en 2012, 2014, 2017–2023 y usuario en 2024–2025 (mínimo 85,8 % del productor en 2018); maíz de OH en 2017–2020 (mínimo 86,5 % en 2019) y usuario en 2025 (89,4 %); maíz de KS 2017, 2018 y 2022; maíz y soja de IN 2019; soja de IL e IN 2017. En KS la confusión probable es con sorgo y cultivos de verano en secano (supuesto, no verificado en la matriz).
- **Transiciones por píxel (`pct_maiz_tras_soja`, etc.):** el error de dos años se acumula. Con 95 % de acierto cada año, un píxel tiene ~90 % de probabilidad de tener bien los dos años; en OH y KS (~88–91 %) baja a ~80 %. Esto genera transiciones falsas "maíz tras maíz" o "soja tras soja" en los bordes y sobrestima el monocultivo. Anotarlo y, si se puede, comparar con NASS.
- **Trigo de invierno: usar con cuidado en IA y MN** (precisión del productor 14–72 %; MN 2020: 16,8 %). En IA y MN el trigo de invierno es escaso, así que el porcentaje de área es chico pero relativamente muy errado. En KS, NE, OH e IN es aceptable (≥ 73 %; los peores son OH e IN en 2024–2025).
- **Avena, alfalfa y otro heno: ruidosos en todos los estados y años.** La avena se subestima (productor 0,4–75 %; IN 2008: 0,4 %). El otro heno se subestima hasta 2023 (productor 3–53 %) y en 2024 se sobreclasifica: de los píxeles que el CDL 2024 marca como "otro heno", solo 0,6–7,7 % lo son. Las columnas de % de alfalfa y heno de `rotacion_anual.csv` y las rotaciones con alfalfa de `rotacion_secuencia.csv` no deberían usarse sin advertencia; para heno y alfalfa conviene la superficie de NASS (Quick Stats o Censo).
- **Serie con saltos:** la precisión de 2008–2016 está inflada por el buffer de 30 m y no se compara con 2017+; 2024–2025 tienen otro muestreo y otra resolución nativa (10 m). Una caída de la precisión no implica un cambio real en los cultivos.
- **Estados más débiles en general:** KS (precisión global de cultivos 79–91 %) y OH (79–96 %; 79,2 % en 2025, el valor más bajo de la tabla junto con KS 2025, 79,3 %). Los mejores: IA, IL, MN y NE.

Fuentes: [2008–2023 CDL state metadata (USDA NASS), páginas `metadata-<st><aa>` para IA, IL, IN, OH, NE, MN y KS](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ia08), consultado 2026-11-15; [CDL Metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/meta), consultado 2026-11-15; [2024 CDL national metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-cdl24-fgdc-std-001-1998), consultado 2026-11-15; [2025 CDL national metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-cdl25-fgdc-std-001-1998), consultado 2026-11-15; [CDL FAQs (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/sarsfaqs2), consultado 2026-11-15; [CDL_2024_accuracy_assessments.zip (USDA NASS)](https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/CDL_2024_accuracy_assessments.zip), consultado 2026-11-15; [CDL_2025_accuracy_assessments.zip (USDA NASS)](https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/CDL_2025_accuracy_assessments.zip), consultado 2026-11-15.

Confianza: alta para los valores (extraídos por script de las tablas oficiales; IA 2023 coincide con lo ya publicado en `cdl_csb.md`) y para las URL y formatos; media para que la tabla HTML de 2016 sea la versión con buffer (inferido por los valores, no verificado en el zip de 2016); baja para la causa de los errores de KS (no se miró la matriz de confusión).

Impacto: data card `docs/datasets/cultivos.md` (Problemas conocidos: los puntos de la sección 5); `rotacion_anual.csv` y `rotacion_secuencia.csv` (advertencias sobre trigo en IA/MN, avena, alfalfa y heno, y transiciones en OH/KS); opcional, sumar `cdl_precision.csv` como tabla de referencia para que ML pondere o filtre por precisión. No cambia `config/`.

Citas:
> "Beginning in 2024, metadata is only available at the national-level. State-level accuracy assessments can still be found on our FAQs webpage." — [CDL Metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/meta)
> "Beginning with the 2016 CDL season we are creating CDL accuracy assessments using unbuffered validation data." — [CDL FAQs (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/sarsfaqs2)
> "Beginning with the 2024 CDL, the accuracy assessment methodology has changed." — [CDL FAQs (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/sarsfaqs2)
> "Corn 1 7415470 96.9% 3.1% 0.932 98.6% 1.4% 0.969" — [2008 Iowa CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ia08)
