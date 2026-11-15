# Precisión del CDL en Michigan y Dakota del Norte (2008–2025)

Pregunta: ¿Qué precisión del productor y del usuario tiene el Cropland Data Layer (CDL) en MI y ND, de 2008 a 2025, para maíz, soja, trigo de invierno, trigo de primavera, avena, alfalfa, otro heno, pastizal/pastura, barbecho, girasol y canola? ¿En qué clases el CDL no sirve para calcular rotaciones? (Research para que el humano decida una cuarta tanda; MI y ND no están en `config/config.yaml`.)

Respuesta corta: **Maíz y soja sirven** en los dos estados (productor y usuario ≥ 81 % todos los años). MI se parece a WI: por debajo de 90 % del productor en 2017–2020 (maíz 86,9–88,9 %, soja 84,8–86,9 %). ND es más débil en maíz: productor 81,2–88,7 % en 2017–2023 (usuario 87,1 % en 2020); la soja de ND tiene productor ≥ 89,0 %, pero usuario 85,7–88,8 % en 2020–2023. **Los cultivos propios de ND sirven:** trigo de primavera (productor 83,9–93,4 %, usuario 82,4–89,7 %), canola (86,9–96,7 % / 92,2–97,3 %) y girasol (71,4–91,7 % / 81,9–94,0 %; < 80 % del productor en 2017, 2018, 2021 y 2023). **No sirven para rotaciones:** trigo de invierno en ND (productor 40,9–84,4 %, < 62 % en 2017–2023 y 2025; se confunde con trigo de primavera), avena en ND (13,1–50,9 %; en 2024 el 39 % de lo que el CDL marca como avena es trigo de primavera), alfalfa en ND (36,2–69,3 %; usuario 40,7 % en 2024), doble cultivo trigo/soja en los dos estados (casi sin píxeles de validación), barbecho en MI (14,9–75,3 %, usuario 16–82 %), otro heno en los dos estados en 2024–2025 (usuario 12,5–52,8 %), y en MI todas las clases que casi no existen ahí: trigo de primavera (0–613 píxeles correctos por año), girasol (8–583) y canola (0–148). Sirven con advertencia: trigo de invierno en MI (≥ 86,9 % / ≥ 86,9 %), alfalfa en MI (74,5–90,0 % / 69,4–87,4 %), avena en MI (34,6–70,7 %: ruidosa), barbecho en ND (31,9–84,1 %: ruidoso). Pastizal/pastura (176) solo tiene precisión desde 2023 (MI 53,9–71,1 %, ND 72,7–86,6 % del productor). Precisión global de cultivos FSA: MI 80,6–92,2 %, ND 73,8–87,2 %. Tabla completa (2 estados × 18 años × 13 clases): `docs/research/cdl_precision_mi_nd.csv`, generada con `docs/research/cdl_precision_mi_nd_extraer.py`.

Detalle:

Fuentes, formato y cortes metodológicos (buffer de 30 m hasta 2016, sin buffer desde 2017, nuevo muestreo y 10 m desde 2024) son los mismos que en `cdl_precision.md` y `cdl_precision_mo_wi_sd.md` y no se repiten. Lo nuevo:

**1. Fuentes y lectura para MI y ND.**
- Los 32 HTML de 2008–2023 (`metadata-mi<aa>`, `metadata-nd<aa>`) están en la ruta de siempre; ninguno dio 404. El script igual prueba la ruta alternativa (`.../metadata/metadata_<st><aa>.htm`, la de WI 2013) si alguno falla.
- El script reusa `cdl_precision_mo_wi_sd_extraer.py` (T064), que a su vez reusa el de T024, y agrega tres clases: girasol (6), trigo de primavera (23) y canola (31). También deja trigo durum (22) afuera de la tabla, pero aparece en las matrices (punto 4).
- Para 2024–2025 hace falta `openpyxl` (no está en `requirements.txt`; se instaló solo en el `.venv` local para esta corrida).
- "—" en las tablas = la clase no tiene fila en la tabla de ese estado y año. "0 / —" = la fila existe con 0 píxeles correctos y "n/a" en el usuario.
  - Doble cultivo (26): MI sin fila en 2010, 2011 y 2013; ND sin fila en 2008–2011, 2015–2020 y 2022–2024.
  - Canola (31) en MI: sin fila en 2008, 2014 y 2018.
  - Pastura/pasto (62, clase vieja): solo fila en 2012, con 0 píxeles, en los dos estados.
  - Pastizal/pastura (176): sin fila en 2008–2022, como en los otros estados (la nota de la tabla excluye "FSA-sampled grass and pasture" y las clases no agrícolas).
- Los píxeles correctos bajan de golpe en 2015 (p. ej. maíz de ND: 1.102.620 en 2014, 65.197 en 2015) y otra vez en 2024. El corte de 2024 es el nuevo muestreo; el de 2015 no lo explica la página de metadatos que leí (no verificado). Con muestras chicas, los porcentajes de las clases raras saltan mucho de un año a otro.

**2. Precisión global de cultivos FSA (%)**

| Estado | 2008 | 2010 | 2011 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| MI | 90,1 | 86,9 | 90,9 | 88,4 | 92,2 | 85,0 | 84,3 | 87,8 | 83,0 | 80,6 |
| ND | 80,7 | 80,5 | 73,8 | 80,1 | 87,2 | 76,8 | 76,8 | 77,5 | 75,7 | 77,1 |

MI queda entre WI y los estados del núcleo. ND es de los más bajos de los doce estados revisados (como MO y SD), aun con el buffer hasta 2016; su mínimo es 2011 (73,8 %).

**3. Precisión por clase.** Productor / usuario, en %. Productor = de los píxeles que son de esa clase en el terreno, cuántos acierta el CDL; usuario = de los que el CDL marca con esa clase, cuántos lo son. Entre paréntesis, píxeles correctos cuando son pocos. Años: los extremos de cada período metodológico más 2012 y 2020. Todos los años en el CSV.

Maíz (1):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | 95,4 / 94,6 | 94,5 / 94,1 | 95,7 / 95,6 | 87,9 / 92,5 | 88,9 / 89,9 | 91,2 / 94,2 | 92,2 / 91,6 | 92,5 / 89,7 |
| ND | 94,0 / 96,8 | 90,3 / 92,3 | 94,6 / 95,6 | 84,4 / 90,5 | 81,2 / 87,1 | 86,9 / 89,0 | 91,6 / 90,7 | 92,8 / 91,4 |

Soja (5):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | 94,5 / 94,8 | 92,5 / 94,4 | 95,0 / 95,0 | 86,9 / 93,5 | 86,5 / 92,0 | 91,3 / 92,2 | 90,3 / 91,4 | 92,8 / 88,4 |
| ND | 96,4 / 96,8 | 92,6 / 93,6 | 96,6 / 94,6 | 89,6 / 90,7 | 89,3 / 87,3 | 90,5 / 85,7 | 89,0 / 92,5 | 91,8 / 91,3 |

Trigo de primavera (23):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | 60,0 / 60,0 (18) | 49,8 / 90,7 (613) | 23,2 / 59,4 (19) | 13,6 / 45,0 (18) | 26,3 / 78,9 (30) | 0,0 / 0,0 | 50,0 / 100 (1) | 0,0 / 0,0 |
| ND | 90,5 / 85,4 | 90,7 / 86,4 | 93,3 / 87,7 | 87,4 / 82,4 | 90,6 / 84,5 | 91,1 / 84,4 | 83,9 / 89,7 | 88,7 / 85,5 |

Trigo de invierno (24):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | 95,1 / 95,0 | 96,6 / 93,8 | 97,5 / 96,4 | 88,7 / 94,4 | 86,9 / 94,2 | 92,8 / 95,1 | 92,4 / 91,4 | 92,5 / 90,2 |
| ND | 60,0 / 86,9 | 81,5 / 89,1 | 83,3 / 92,0 | 61,5 / 82,0 | 44,8 / 82,3 (583) | 57,1 / 83,4 | 75,8 / 70,3 | 56,4 / 68,6 |

En ND el productor del trigo de invierno es < 62 % en 2008, 2013, 2015, 2017–2023 y 2025 (mínimo 40,9 % en 2018).

Doble cultivo trigo de invierno/soja (26):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | 62,0 / 92,4 (315) | 0 / — | 36,1 / 47,0 (39) | 2,1 / 1,6 (1) | 23,4 / 60,3 (41) | 0,0 / 0,0 | 22,2 / 10,0 (4) | 68,0 / 72,9 (51) |
| ND | — | 26,7 / 68,6 (48) | — | — | — | — | — | 36,0 / 90,0 (9) |

Avena (28):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | 43,3 / 68,4 | 39,1 / 57,4 | 69,9 / 48,4 | 56,5 / 46,6 | 61,1 / 35,8 | 39,5 / 65,2 | 65,3 / 58,6 | 42,5 / 73,2 |
| ND | 13,1 / 51,9 | 13,8 / 47,1 | 30,3 / 65,2 | 14,5 / 39,5 | 25,8 / 44,9 | 25,9 / 47,9 | 50,9 / 22,5 | 49,4 / 52,3 |

Canola (31):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | — | 90,0 / 56,3 (18) | 0 / — | 66,7 / 80,0 (8) | 76,1 / 96,2 (51) | 68,4 / 94,5 (52) | 78,9 / 71,4 (15) | 84,2 / 69,6 (16) |
| ND | 94,5 / 96,8 | 94,8 / 96,3 | 96,7 / 96,9 | 86,9 / 92,2 | 91,6 / 95,5 | 90,2 / 93,7 | 95,1 / 92,2 | 94,3 / 92,3 |

Girasol (6):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | 30,5 / 63,4 (429) | 20,0 / 47,8 (159) | 30,5 / 48,5 (32) | 19,8 / 54,8 (34) | 15,3 / 66,7 (20) | 26,9 / 90,3 (28) | 36,7 / 57,9 (11) | 18,2 / 72,7 (8) |
| ND | 91,7 / 93,5 | 89,0 / 94,1 | 89,7 / 92,3 | 75,1 / 81,9 | 83,6 / 89,7 | 78,7 / 91,2 | 91,6 / 86,6 | 89,3 / 90,7 |

Alfalfa (36):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | 81,4 / 85,6 | 83,7 / 71,9 | 86,7 / 86,0 | 80,3 / 83,8 | 80,0 / 83,7 | 82,1 / 80,9 | 80,3 / 70,6 | 74,5 / 69,4 |
| ND | 36,2 / 69,9 | 46,2 / 64,3 | 69,3 / 79,8 | 52,6 / 69,3 | 56,5 / 65,9 | 54,3 / 66,1 | 67,0 / 40,7 | 52,1 / 58,4 |

Otro heno / no alfalfa (37):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | 57,1 / 76,1 | 59,5 / 55,6 | 63,9 / 73,6 | 65,1 / 82,8 | 56,8 / 74,6 | 57,9 / 71,1 | 48,0 / 35,5 | 32,1 / 52,8 |
| ND | 25,8 / 71,9 | 36,5 / 51,9 | 64,3 / 78,2 | 49,7 / 80,4 | 44,3 / 58,8 | 46,8 / 60,4 | 48,4 / 12,5 | 38,9 / 26,5 |

Barbecho / tierra de cultivo ociosa (61):

| Estado | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| MI | 14,9 / 59,1 | 19,7 / 29,2 | 38,6 / 22,4 | 35,3 / 30,5 | 49,2 / 30,9 | 17,6 / 55,9 (119) | 27,1 / 25,0 (19) | 23,5 / 48,0 (36) |
| ND | 31,9 / 77,2 | 43,9 / 72,2 | 40,0 / 77,7 | 35,5 / 70,4 | 84,1 / 84,7 | 37,5 / 65,0 | 44,8 / 33,9 | 43,5 / 57,4 |

El barbecho supera 65 % del productor solo en algunos años: MI 2019 (75,3 / 82,1, con 62.076 píxeles correctos frente a 100–3.000 en los demás años desde 2015); ND 2009 (75,8), 2019 (67,7), 2020 (84,1) y 2022 (77,6). No verifiqué la causa; en MO, WI y SD también sube en 2019.

Pastizal/pastura (176), solo 2023–2025:

| Estado | 2023 | 2024 | 2025 |
|---|---|---|---|
| MI | 59,6 / 54,5 | 53,9 / 54,9 | 71,1 / 68,3 |
| ND | 86,6 / 78,5 | 72,7 / 85,5 | 83,8 / 84,1 |

**4. Con qué se confunde (hoja "All - Matrix" de los xlsx 2024–2025).** Filas = clase del CDL, columnas = referencia (FSA); comprobado: MI 2024 maíz, 29.719 / suma de la columna (32.221) = 92,2 % = productor del "Summary Table". Porcentajes sobre la fila (lo que el CDL marca) o sobre la columna (lo que es en el terreno):
- **ND: trigo de invierno ↔ trigo de primavera.** Del trigo de invierno real, el CDL marca como trigo de primavera el 5,1 % (2024) y el 20,2 % (2025). De lo que marca como trigo de invierno, el 10,0 % y el 14,8 % es trigo de primavera. Como en la muestra de validación de ND el trigo de primavera es ~50 veces más abundante (63.710 contra 1.210 píxeles en 2024), para rotaciones conviene **sumar 22 + 23 + 24 como "trigo"** en ND.
- **ND: trigo de primavera ↔ durum (22).** Del trigo de primavera real, el 7,4 % (2024) y el 3,9 % (2025) queda como durum. Otro motivo para juntar los trigos.
- **ND: avena ↔ trigo de primavera y cebada (21).** De lo que el CDL marca como avena, es trigo de primavera el 39,2 % (2024) y el 15,6 % (2025); es pastizal el 17,9 % y el 6,9 %. De la avena real, el 13,9 % y el 5,8 % queda como cebada. En MI la avena se confunde sobre todo con pastizal (10 % de la real en 2024, 19,7 % en 2025) y alfalfa (5,5 % y 8,3 %).
- **Pastizal (176) absorbe el error de las forrajeras, como en MO y SD.** De lo que el CDL marca como otro heno, es pastizal: ND 68,2 % (2024) y 49,0 % (2025), MI 38,4 % y 26,9 %; como alfalfa: ND 44,7 % y 22,3 %, MI 14,8 % y 13,3 %; como barbecho: ND 44,8 % y 19,2 %, MI 30,3 % y 20,0 %. En los dos estados el otro heno y la alfalfa también se confunden entre sí (5–17 %).
- **Maíz ↔ soja.** En MI, 2,5–3,9 % de lo marcado como maíz es soja y 2,9–3,1 % de lo marcado como soja es maíz. En ND la confusión de maíz y soja se reparte entre ellos y pastizal (2,2–3,3 %).
- **Girasol en ND** casi no se confunde (≤ 4,8 % con pastizal o soja). **Canola en ND**: ≤ 2,6 %.
- **Las clases raras en MI** (trigo de primavera, girasol, canola) tienen 1 a 44 píxeles de referencia en 2024–2025: la matriz no dice nada útil. Lo que el CDL marca como canola en MI es trigo de invierno en 17–19 %.

**5. Dónde el CDL no sirve para rotaciones.**

| Clase | MI | ND |
|---|---|---|
| Maíz | sirve; < 90 % del productor en 2017–2020 | sirve con advertencia: productor 81,2–88,7 % en 2017–2023 |
| Soja | sirve; < 90 % del productor en 2017–2020 y 2022 | sirve; usuario 85,7–88,8 % en 2020–2023 |
| Trigo de primavera | **no sirve** (casi no hay: 0–613 píxeles correctos; 0 en 2010, 2019, 2021, 2023 y 2025) | sirve (≥ 83,9 % / ≥ 82,4 %); se confunde algo con durum |
| Trigo de invierno | sirve (≥ 86,9 %) | **no sirve solo** (40,9–84,4 %); usar 22 + 23 + 24 juntos |
| Doble trigo/soja | **no sirve** (0–68 %, 0–315 píxeles) | **no sirve** (casi sin validación: fila solo en 5 años, 0–1.098 píxeles, productor 0–36 %) |
| Avena | ruidosa (34,6–70,7 % / 35,8–73,2 %) | **no sirve** (13,1–50,9 %; se confunde con trigo de primavera y cebada) |
| Canola | **no sirve** (casi no hay: 0–148 píxeles) | sirve (≥ 86,9 % / ≥ 92,2 %) |
| Girasol | **no sirve** (15–73 %, 8–583 píxeles) | sirve con advertencia (71,4–91,7 %; < 80 % en 2017, 2018, 2021, 2023) |
| Alfalfa | sirve con advertencia (74,5–90,0 %; usuario ~70 % en 2024–2025) | **no sirve** (36,2–69,3 %; usuario 40,7 % en 2024) |
| Otro heno | ruidosa (54–73 % hasta 2023); **no sirve en 2024–2025** | ruidosa (25,8–64,3 %); **no sirve en 2024–2025** (usuario 12,5 y 26,5 %) |
| Barbecho | **no sirve** (14,9–75,3 %, < 40 % en 14 de 18 años) | ruidosa (31,9–84,1 %, < 50 % en 14 de 18 años) |
| Pastizal (176) | sin precisión antes de 2023; 54–71 % en 2023–2025 | sin precisión antes de 2023; ≥ 72,7 % en 2023–2025 |

Lo que agrega a los research anteriores:
- Si se suma ND, `config/config.yaml` y `data/reference/clases_cdl.csv` tendrían que incluir trigo de primavera (23), durum (22), canola (31) y girasol (6): son los cultivos de rotación de ND y el CDL los clasifica bien. Para rotaciones, en ND el grupo "trigo" debería ser 22 + 23 + 24 (+ 26 si aparece).
- Las transiciones por píxel en ND tienen más ruido que en IA: maíz con productor ~81–89 % en 2017–2023 deja solo ~70–80 % de píxeles con los dos años bien.
- MI se comporta como WI: maíz, soja, trigo de invierno y alfalfa usables; el resto no.
- Para heno, alfalfa y pastura conviene la superficie de NASS (Quick Stats o Censo) y no el CDL, como en los otros estados.

Fuentes: [2008–2023 CDL state metadata (USDA NASS), páginas `metadata-mi<aa>` y `metadata-nd<aa>`](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-nd08), consultado 2026-11-15 (32 páginas); [CDL_2024_accuracy_assessments.zip (USDA NASS)](https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/CDL_2024_accuracy_assessments.zip), consultado 2026-11-15 (xlsx de MI y ND; hojas "Summary Table" y "All - Matrix"); [CDL_2025_accuracy_assessments.zip (USDA NASS)](https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/CDL_2025_accuracy_assessments.zip), consultado 2026-11-15 (ídem).

Confianza: alta para los valores (extraídos por script de las tablas oficiales; 32 HTML y 4 xlsx); alta para que la clase 176 no tiene precisión antes de 2023; media para la lectura de las matrices (orientación comprobada con un valor; solo 2024–2025); baja para cualquier explicación de los saltos del barbecho y de la caída de píxeles en 2015 (no verificadas).

Impacto: decisión del humano sobre una cuarta tanda con MI y ND (`config/config.yaml`); si entra ND, `data/reference/clases_cdl.csv` y el grupo "trigo" de `rotacion_anual.csv` y `rotacion_secuencia.csv` (sumar 22 + 23 + 24), y el data card `docs/datasets/cultivos.md` (Problemas conocidos: tabla de la sección 5). Opcional: sumar `cdl_precision_mi_nd.csv` a la tabla de referencia de precisión para ML. No cambia `config/` ahora.

Citas:
> "Spring Wheat                       23   3902170     90.5%      9.5%     0.863     85.4%     14.6%     0.795" — [2008 North Dakota CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-nd08)
> "Sunflower                           6    646208     91.7%      8.3%     0.913     93.5%      6.5%     0.932" — [2008 North Dakota CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-nd08)
> "Winter Wheat                        24         583       44.8%       55.2%       0.447       82.3%       17.7%       0.823" — [2020 North Dakota CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-nd20)
> "Grassland/Pasture               176      9,491      59.6%      40.4%      0.588      54.5%      45.5%      0.537" — [2023 Michigan CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-mi23)
