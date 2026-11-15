# Precisión del CDL en Missouri, Wisconsin y Dakota del Sur (2008–2025)

Pregunta: ¿Qué precisión del productor y del usuario tiene el Cropland Data Layer (CDL) en MO, WI y SD, de 2008 a 2025, para maíz, soja, trigo de invierno, doble cultivo trigo/soja, avena, alfalfa, otro heno, pastizal/pastura y barbecho? ¿En qué clases y estados el CDL no sirve para calcular rotaciones?

Respuesta corta: **Maíz y soja sirven** en los tres estados (productor y usuario ≥ 82 % en todos los años), pero WI y MO son más débiles que el núcleo del Corn Belt: soja de WI entre 82,0 y 89,8 % del productor en 2017–2025, y maíz de MO por debajo de 90 % del productor en 2017–2022 y 2025 (soja en 2017–2019 y 2024–2025). SD es el más parejo (≥ 89,7 %). **No sirven para rotaciones:** trigo de invierno en MO (productor 28–50 % desde 2017), doble cultivo trigo/soja en WI y SD (casi no hay píxeles de validación; productor 0–56 %), avena en MO (productor 0,1–25 %), alfalfa en MO (10,8–59 %), barbecho en MO y WI (productor casi siempre < 40 %; 0–8 % en 2024–2025) y otro heno en los tres estados en 2024–2025 (usuario 1,4–36,9 %). Sirven con advertencia: trigo de invierno en SD y WI (≥ 72 %), doble cultivo en MO (≥ 76 %, salvo 2017: 52,5 %), alfalfa en WI (≥ 68 %), barbecho en SD (55–89 %). La clase pastizal/pastura (176) **solo tiene precisión publicada desde 2023**; antes no se evalúa (la validación de 2008–2022 la deja fuera, junto con las clases no agrícolas). La matriz de confusión de 2024–2025 muestra que casi todo el error de heno, alfalfa, avena y barbecho es confusión con pastizal (176), y en MO el trigo de invierno se confunde con el doble cultivo (26). Precisión global de cultivos: MO 70,5–92,4 %, WI 74,9–91,5 %, SD 70,3–89,3 %; **MO 2025 (70,5 %) es el valor más bajo de los diez estados** revisados hasta ahora. Tabla completa (3 estados × 18 años × 10 clases): `docs/research/cdl_precision_mo_wi_sd.csv`, generada con `docs/research/cdl_precision_mo_wi_sd_extraer.py`.

Detalle:

Fuentes, formato y cortes metodológicos (buffer de 30 m hasta 2016, sin buffer desde 2017, nuevo muestreo y 10 m desde 2024) son los mismos que en `cdl_precision.md` y no se repiten. Lo nuevo:

**1. Particularidades de las fuentes para MO, WI y SD.**
- `metadata-wi13` da 404. La página de metadatos enlaza otra ruta para WI 2013: `https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/metadata/metadata_wi13.htm` (el script la usa). Los otros 47 HTML de 2008–2023 están en la ruta de siempre.
- Algunas filas tienen 0 píxeles correctos y "n/a" en la precisión del usuario (la clase no se clasificó nunca). El script de T024 no las leía; el de esta tarea sí: quedan con precisión del productor 0 y usuario vacío (MO 2010 alfalfa; SD doble cultivo 2015, 2019, 2023).
- "—" en las tablas de abajo = la clase no tiene fila en la tabla de ese estado y año: otro heno (37) en MO 2010–2011 y WI 2011; doble cultivo (26) en SD 2008, 2017, 2018, 2020–2022. En SD 2024–2025 la fila existe pero con 0 píxeles correctos y sin precisión.
- **Pastizal/pastura (176)**: aparece en las tablas de 2023 (HTML) y de 2024–2025 (xlsx). En 2008–2022 no tiene fila: la nota de las tablas dice que "FSA-sampled grass and pasture" y las clases no agrícolas (62–65, 81–91, 93–199) no entran en la precisión global, y NASS remite al NLCD para su precisión. La clase vieja "Pasture/Grass" (62) tiene fila solo en WI 2010 (60,8 / 77,1) y SD 2012 (0 píxeles).
- Para entender los errores se leyó la hoja "All - Matrix" de los xlsx 2024–2025 de MO, WI y SD. Columnas = referencia (FSA), filas = clase del CDL (comprobado: MO 2024 maíz, 27.293 / suma de columna = 91,6 % = precisión del productor del "Summary Table").

**2. Precisión global de cultivos FSA (%)**

| Estado | 2008 | 2010 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|
| MO | 83,2 | 92,4 | 83,0 | 89,3 | 76,5 | 80,7 | 80,2 | 75,0 | 70,5 |
| WI | 86,6 | 84,4 | 86,8 | 91,5 | 76,7 | 78,2 | 82,1 | 78,1 | 74,9 |
| SD | 83,1 | 72,1 | 74,7 | 89,3 | 81,7 | 78,5 | 82,2 | 73,4 | 75,7 |

Los tres estados quedan por debajo de los siete de `cdl_precision.md` (79,2 a 96,7 % en los años que muestra esa tabla). En SD 2010–2012 la precisión global es baja aun con el buffer (70,3–74,7 %).

**3. Precisión por clase.** Productor / usuario, en %. Productor = de los píxeles que son de esa clase en el terreno, cuántos acierta el CDL; usuario = de los que el CDL marca con esa clase, cuántos lo son. Años elegidos: los dos extremos de cada período metodológico más 2012 y 2020. Todos los años en el CSV.

Maíz (1):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MO | 94,1 / 96,4 | 96,3 / 93,8 | 97,5 / 96,7 | 86,8 / 95,6 | 89,9 / 94,6 | 90,7 / 94,7 | 91,6 / 89,9 | 88,1 / 89,8 |
| WI | 95,6 / 93,9 | 95,2 / 93,9 | 97,2 / 95,5 | 85,3 / 91,6 | 88,2 / 88,7 | 89,8 / 92,3 | 88,8 / 90,3 | 89,7 / 88,1 |
| SD | 95,8 / 97,0 | 94,7 / 93,5 | 96,8 / 96,0 | 92,8 / 92,8 | 91,3 / 92,6 | 93,7 / 94,0 | 92,8 / 92,6 | 93,9 / 92,9 |

Soja (5):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MO | 94,8 / 93,5 | 95,8 / 91,8 | 96,7 / 96,1 | 87,2 / 92,6 | 91,1 / 92,9 | 90,9 / 92,9 | 88,7 / 90,5 | 86,9 / 89,2 |
| WI | 91,8 / 92,5 | 89,3 / 93,3 | 95,0 / 95,9 | 82,0 / 90,7 | 82,5 / 89,5 | 86,2 / 91,1 | 89,8 / 85,1 | 89,2 / 86,7 |
| SD | 96,7 / 97,8 | 94,3 / 94,6 | 97,0 / 96,1 | 93,9 / 93,3 | 92,4 / 92,2 | 93,9 / 94,0 | 92,4 / 92,3 | 94,3 / 92,3 |

Trigo de invierno (24):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MO | 54,4 / 75,7 | 34,3 / 54,0 | 61,3 / 73,4 | 28,3 / 62,5 | 31,0 / 60,1 | 46,5 / 67,3 | 49,8 / 35,1 | 35,2 / 54,7 |
| WI | 90,3 / 92,2 | 91,5 / 91,8 | 93,5 / 90,2 | 72,5 / 87,0 | 73,4 / 83,4 | 86,7 / 89,5 | 88,8 / 84,5 | 85,4 / 84,7 |
| SD | 87,5 / 93,3 | 90,4 / 92,2 | 94,9 / 96,0 | 86,8 / 86,9 | 87,6 / 88,1 | 85,1 / 86,8 | 94,7 / 82,9 | 85,0 / 80,7 |

Doble cultivo trigo de invierno/soja (26):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MO | 87,2 / 83,8 | 89,8 / 85,2 | 87,2 / 86,0 | 52,5 / 76,4 | 77,8 / 82,5 | 84,0 / 84,8 | 81,6 / 84,0 | 76,3 / 84,8 |
| WI | 11,3 / 90,0 | 22,0 / 89,5 | 26,4 / 82,3 | 0,0 / 0,0 | 16,2 / 52,4 | 32,3 / 82,5 | 7,7 / 14,3 | 15,2 / 71,4 |
| SD | — | 13,9 / 12,7 | 3,3 / 100,0 | — | — | 0,0 / — | 0 px | 0 px |

Avena (28):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MO | 0,5 / 15,8 | 0,7 / 4,2 | 8,6 / 53,6 | 3,7 / 40,0 | 6,5 / 35,0 | 6,8 / 33,3 | 20,0 / 5,0 | 25,2 / 60,7 |
| WI | 54,9 / 65,5 | 42,1 / 61,3 | 47,7 / 69,1 | 25,0 / 64,0 | 43,6 / 56,7 | 34,7 / 60,6 | 58,1 / 42,4 | 35,0 / 68,8 |
| SD | 21,0 / 57,2 | 32,3 / 59,1 | 50,2 / 62,6 | 33,7 / 56,7 | 50,2 / 60,9 | 47,7 / 64,4 | 73,9 / 47,4 | 62,1 / 69,4 |

Alfalfa (36):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MO | 21,1 / 68,1 | 22,0 / 56,3 | 24,1 / 64,6 | 13,0 / 61,8 | 21,5 / 55,5 | 29,3 / 57,5 | 59,0 / 13,3 | 26,7 / 54,9 |
| WI | 86,1 / 86,4 | 82,9 / 85,9 | 90,8 / 86,2 | 68,6 / 79,1 | 74,4 / 75,2 | 77,2 / 82,4 | 81,7 / 74,3 | 76,0 / 71,7 |
| SD | 56,3 / 72,3 | 54,0 / 65,3 | 72,3 / 80,2 | 65,3 / 75,6 | 71,1 / 76,9 | 71,5 / 74,6 | 83,1 / 51,1 | 63,4 / 66,0 |

Otro heno / no alfalfa (37):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MO | 45,6 / 83,9 | 39,4 / 55,6 | 54,5 / 70,1 | 35,0 / 70,2 | 47,9 / 64,5 | 41,0 / 59,2 | 57,9 / 1,4 | 31,2 / 16,8 |
| WI | 36,8 / 59,5 | 30,0 / 58,4 | 40,2 / 61,7 | 27,2 / 57,5 | 31,9 / 50,9 | 33,5 / 52,8 | 56,7 / 10,9 | 26,7 / 36,9 |
| SD | 49,1 / 77,6 | 53,1 / 33,8 | 73,9 / 81,7 | 58,5 / 72,6 | 63,7 / 72,0 | 62,6 / 68,2 | 68,3 / 8,8 | 39,6 / 30,6 |

Barbecho / tierra de cultivo ociosa (61):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MO | 49,9 / 77,8 | 15,2 / 60,9 | 11,6 / 55,2 | 36,8 / 65,6 | 48,3 / 76,7 | 8,1 / 71,4 | 0,0 / 0,0 | 2,6 / 14,3 |
| WI | 8,5 / 42,6 | 4,8 / 44,1 | 18,1 / 59,0 | 37,9 / 58,9 | 31,8 / 49,4 | 5,1 / 55,6 | 8,3 / 20,0 | 2,2 / 11,1 |
| SD | 67,4 / 84,0 | 65,8 / 74,5 | 74,5 / 82,1 | 61,9 / 72,4 | 80,2 / 79,0 | 55,4 / 68,8 | 76,9 / 44,6 | 59,8 / 61,9 |

En 2019 el barbecho sube en los tres estados (MO 75,5 / 83,1; WI 69,1 / 69,8; SD 89,4 / 86,1), el año de la siembra prevenida masiva: hubo mucha más superficie ociosa para validar.

Pastizal/pastura (176), solo 2023–2025:

| Estado | 2023 | 2024 | 2025 |
|---|---|---|---|
| MO | 79,7 / 69,7 | 77,0 / 86,9 | 88,0 / 87,1 |
| WI | 66,5 / 47,5 | 57,9 / 67,8 | 72,5 / 64,8 |
| SD | 93,0 / 88,4 | 84,2 / 96,3 | 92,1 / 91,6 |

**4. Con qué se confunde (matrices 2024–2025).** Porcentajes sobre la columna (referencia) o la fila (CDL):
- **Pastizal (176) absorbe casi todo el error de las clases forrajeras.** De los píxeles que el CDL marca como otro heno, son pastizal en el terreno: MO 91,0 % (2024) y 69,3 % (2025), SD 81,9 % y 52,3 %, WI 49,1 % y 29,2 %. Lo mismo con alfalfa en MO (78,0 % de lo marcado como alfalfa en 2024 es pastizal), barbecho (MO, WI, SD: 13–67 % de lo marcado como barbecho es pastizal) y avena en MO (85 % en 2024, pero con 40 píxeles). En WI, el otro heno también se confunde con alfalfa (26 % en 2024).
- **Trigo de invierno en MO ↔ doble cultivo.** Del trigo de invierno real, el CDL marca como doble cultivo trigo/soja el 21,1 % (2024) y 15,2 % (2025), y como pastizal el 12,8 % y 32,0 %. Del que el CDL marca como trigo de invierno, el 29,7 % (2024) es doble cultivo. Para rotaciones conviene **sumar 24 + 26** en MO como "trigo" y no separar trigo solo de doble cultivo.
- **Soja de WI ↔ maíz.** De lo que el CDL marca como soja en WI, 7,3 % (2024) y 4,1 % (2025) es maíz. Es justo la confusión que genera transiciones falsas maíz-maíz o soja-soja.
- **Avena de SD ↔ trigo de primavera (23)**: 15,7 % de lo marcado como avena en 2024 es trigo de primavera.
- En MO, 3,9–7,3 % del maíz y la soja reales quedan como pastizal en 2024–2025.

**5. Dónde el CDL no sirve para rotaciones (para el data card de `cultivos` y `rotacion_*.csv`).**

| Clase | MO | WI | SD |
|---|---|---|---|
| Maíz | sirve; < 90 % del productor en 2017–2022 y 2025 | sirve; < 90 % del productor en 2017–2025 | sirve |
| Soja | sirve; < 90 % en 2017–2019 y 2024–2025 | sirve con advertencia: productor 82,0–87,1 % en 2017–2023, usuario 85,1–86,7 % en 2024–2025 | sirve |
| Trigo de invierno | **no sirve solo** (productor 28–50 % desde 2017); usar 24 + 26 juntos | sirve (≥ 72 %) | sirve (≥ 79 %) |
| Doble trigo/soja | sirve con advertencia (≥ 76 %; 2017: 52,5 %) | **no sirve** (productor 0–56 %, pocos píxeles) | **no sirve** (0–22 %, 0 píxeles de validación en la mayoría de los años) |
| Avena | **no sirve** (productor 0,1–25 %; 1–135 píxeles correctos) | ruidosa (25–61 %) | ruidosa (19–74 %) |
| Alfalfa | **no sirve** (10,8–59 %; usuario 13,3 % en 2024) | sirve con advertencia (69–91 %) | ruidosa (43–83 %) |
| Otro heno | ruidosa hasta 2023; **no sirve en 2024–2025** | ruidosa (27–42 % hasta 2023); **no sirve en 2024–2025** | ruidosa; **no sirve en 2024–2025** (usuario 8,8 y 30,6 %) |
| Barbecho | **no sirve** (0–76 %, muy variable; 0 / 0 en 2024) | **no sirve** (2–69 %, < 20 % en 14 de 18 años) | sirve con advertencia (55–89 %) |
| Pastizal (176) | sin precisión antes de 2023 | sin precisión antes de 2023; 58–73 % en 2023–2025 | sin precisión antes de 2023; ≥ 84 % en 2023–2025 |

Lo que agrega a `cdl_precision.md`:
- Las transiciones por píxel (`pct_maiz_tras_soja`, etc.) en WI y MO tienen más ruido que en IA, IL o MN: con ~86–90 % de acierto cada año, solo ~75–80 % de los píxeles tienen bien los dos años. En SD el ruido es como el de IA.
- "Maíz o soja continuos" en WI pueden estar inflados por la confusión soja ↔ maíz.
- Para heno, alfalfa y pastura, como en los otros estados, conviene la superficie de NASS (Quick Stats o Censo) y no el CDL. En MO y SD la confusión principal es con pastizal, que es mucho más abundante que el heno; por eso la precisión del usuario del heno se derrumba en 2024.
- Si `rotacion_anual.csv` tiene un % de pastizal, no hay precisión publicada para validarlo en 2008–2022.

Fuentes: [2008–2023 CDL state metadata (USDA NASS), páginas `metadata-<st><aa>` de MO, WI y SD](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-mo08), consultado 2026-11-15; [CDL Metadata (USDA NASS), índice con el enlace de WI 2013](https://www.nass.usda.gov/research-and-science/cropland/metadata/meta), consultado 2026-11-15; [2013 Wisconsin CDL metadata (USDA NASS)](https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/metadata/metadata_wi13.htm), consultado 2026-11-15; [CDL_2024_accuracy_assessments.zip (USDA NASS)](https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/CDL_2024_accuracy_assessments.zip), consultado 2026-11-15 (xlsx de MO, WI y SD; hojas "Summary Table" y "All - Matrix"); [CDL_2025_accuracy_assessments.zip (USDA NASS)](https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/CDL_2025_accuracy_assessments.zip), consultado 2026-11-15 (ídem).

Confianza: alta para los valores (extraídos por script de las tablas oficiales; 48 HTML y 6 xlsx); alta para que la clase 176 no tiene precisión antes de 2023 (no hay fila en 2008–2022 y la nota de la tabla la excluye); media para la lectura de las matrices (orientación comprobada con un valor; solo 2024–2025); baja para la explicación del barbecho en 2019 (coincidencia con el año de siembra prevenida, no verificada en la fuente).

Impacto: data card `docs/datasets/cultivos.md` de los estados MO, WI y SD (Problemas conocidos: tabla de la sección 5); `rotacion_anual.csv` y `rotacion_secuencia.csv` de esos estados (en MO sumar trigo 24 + 26; advertencias sobre avena, alfalfa, heno, barbecho y doble cultivo); opcional, sumar `cdl_precision_mo_wi_sd.csv` a la tabla de referencia de precisión para ML. No cambia `config/`.

Citas:
> "**The Overall Accuracy represents only the FSA row crops and annual fruit and vegetables (codes 1-61, 66-80, 92 and 200-255). FSA-sampled grass and pasture. Non-agricultural and NLCD-sampled categories (codes 62-65, 81-91 and 93-199) are not included in the Overall Accuracy." — [2008 Missouri CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-mo08)
> "Grassland/Pasture               176    133,063      79.7%      20.3%      0.750      69.7%      30.3%      0.638" — [2023 Missouri CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-mo23)
> "Winter Wheat                       24     95915     54.4%     45.6%     0.536     75.7%     24.3%     0.751" — [2008 Missouri CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-mo08)
