# Precisión del CDL en Kentucky (2008–2025)

Pregunta: ¿Qué precisión del productor y del usuario tiene el Cropland Data Layer (CDL) en KY, de 2008 a 2025, para maíz, soja, trigo de invierno, doble cultivo trigo/soja, heno, alfalfa, pastizal y tabaco? ¿En qué clases el CDL no sirve para calcular rotaciones? (Research para que el humano decida una cuarta tanda; KY no está en `config/config.yaml`. Ver `docs/research/cuarta_tanda.md`.)

Respuesta corta: **Maíz, soja y doble cultivo trigo/soja sirven**, pero peor que en IA, IL e IN. Maíz: productor 87,2–96,8 % y usuario ≥ 93,2 % hasta 2023; cae a 84,2 / 85,9 % (2024) y 80,8 / 84,7 % (2025). Soja: productor 83,5–87,6 % en 2017–2023 y 78,4 % / 75,7 % en 2024 / 2025 (usuario 82,2 % / 80,1 %). Doble trigo/soja (26): 79,3–94,8 % / 85,4–95,6 %. **No sirven para rotaciones:** trigo de invierno solo (24; productor 4,7–29,0 %: en KY casi todo el trigo es doble cultivo con soja y el CDL lo marca como 26), tabaco (productor 12,0–58,4 %, 27–1.782 píxeles correctos por año; el 58–60 % del tabaco real queda como pastizal en 2024–2025), alfalfa (productor 13,4–42,7 %), otro heno (productor 20,8–65,0 %; usuario 3,1 % en 2024 y 5,1 % en 2025: lo que el CDL marca como heno es pastizal en 78–84 %), avena (0–13 píxeles correctos por año) y barbecho (0–62 %, casi sin validación). Pastizal/pastura (176) solo tiene precisión desde 2023: 65,3 / 57,1 % (2023), 73,2 / 80,2 % (2024), 86,0 / 85,7 % (2025). Precisión global de cultivos FSA: 70,4–87,1 % hasta 2023 y **60,1 % (2024) y 56,3 % (2025)**, la más baja de los estados revisados hasta ahora. Tabla completa (18 años × 11 clases): `docs/research/cdl_precision_ky.csv`, generada con `docs/research/cdl_precision_ky_extraer.py`.

Detalle:

Fuentes, formato y cortes metodológicos (buffer de 30 m hasta 2016, sin buffer desde 2017, nuevo muestreo y 10 m desde 2024) son los mismos que en `cdl_precision.md`, `cdl_precision_mo_wi_sd.md` y `cdl_precision_mi_nd.md`, y no se repiten. Lo nuevo:

**1. Fuentes y lectura para KY.**
- Los 16 HTML de 2008–2023 (`metadata-ky<aa>`) están en la ruta de siempre; ninguno dio 404. Los xlsx de 2024 y 2025 (`NASS_CDL_KY24_accuracy.xlsx`, `NASS_CDL_KY25_accuracy.xlsx`) están en los zip nacionales.
- El script reusa `cdl_precision_mi_nd_extraer.py` (T068), que reusa los de T064 y T024; solo cambia el estado y las clases: agrega tabaco (11) y saca girasol, trigo de primavera y canola.
- Para 2024–2025 hace falta `openpyxl` (no está en `requirements.txt`; se instaló solo en el `.venv` local para esta corrida).
- "—" = la clase no tiene fila en la tabla de ese año. "0 / 0" = fila con 0 píxeles correctos.
  - Otro heno (37): **sin fila en 2011 y 2012** (sí está en la leyenda del archivo). No encontré por qué.
  - Pastura/pasto (62, clase vieja): solo fila en 2010 (46,3 / 73,7 %, 314.807 píxeles correctos). Ese año la precisión global FSA es la más baja hasta 2023 (70,4 %); no verifiqué si la clase 62 entra en ese cálculo (la nota dice códigos 1–61 y 200–255).
  - Avena (28): sin fila en 2018. Barbecho (61) en 2025: fila con 0 píxeles de referencia.
  - Pastizal/pastura (176): sin fila en 2008–2022, como en los otros estados.
- Los píxeles correctos caen en 2015 (maíz: 680.585 en 2014, 178.611 en 2015) y otra vez en 2024 (9.052). Igual que en MI y ND; la causa de 2015 no la verifiqué.

**2. Precisión global de cultivos FSA (%)**

| 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 77,0 | 77,9 | 70,4 | 87,1 | 86,3 | 78,9 | 84,1 | 85,0 | 86,7 | 73,7 | 75,7 | 75,1 | 76,9 | 75,4 | 74,7 | 75,3 | 60,1 | 56,3 |

En la hoja "Summary Table" de 2024, la clase "Forage" tiene 3,4 % de precisión (209 correctos de 6.210 píxeles de referencia) y "Principal Crops" 72,3 %: buena parte de la caída de 2024–2025 viene de las forrajeras, que pesan mucho en KY. Como referencia, IA, IL e IN tienen 84,5–90,8 % en 2024–2025 (`cdl_precision.csv`).

**3. Precisión por clase.** Productor / usuario, en %. Entre paréntesis, píxeles correctos cuando son pocos. Todos los años en el CSV.

| Clase (código) | 2008 | 2012 | 2016 | 2017 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| Maíz (1) | 93,7 / 95,5 | 91,6 / 95,6 | 96,8 / 96,7 | 87,4 / 94,1 | 90,6 / 94,4 | 90,9 / 93,4 | 84,2 / 85,9 | 80,8 / 84,7 |
| Soja (5) | 87,9 / 90,9 | 85,9 / 93,4 | 93,8 / 95,4 | 83,5 / 92,7 | 87,6 / 91,7 | 86,7 / 91,6 | 78,4 / 82,2 | 75,7 / 80,1 |
| Doble trigo/soja (26) | 88,3 / 85,4 | 92,4 / 94,4 | 94,8 / 91,2 | 84,4 / 90,6 | 88,9 / 90,2 | 90,3 / 91,4 | 81,1 / 89,3 | 79,3 / 87,9 |
| Trigo de invierno (24) | 17,6 / 66,0 (2.638) | 5,4 / 42,3 (300) | 8,4 / 33,6 (120) | 7,7 / 58,3 (169) | 11,8 / 45,5 (239) | 12,1 / 53,8 (250) | 7,7 / 10,4 (11) | 12,1 / 26,1 (29) |
| Tabaco (11) | 14,4 / 65,9 (472) | 21,7 / 82,7 (996) | 58,4 / 80,2 (858) | 37,4 / 69,1 (632) | 48,1 / 69,1 (749) | 52,4 / 72,8 (529) | 12,7 / 87,1 (27) | 17,8 / 69,7 (46) |
| Alfalfa (36) | 25,2 / 69,1 | 13,4 / 86,8 | 40,8 / 64,8 | 26,9 / 67,9 | 28,6 / 54,2 | 29,1 / 62,6 | 15,9 / 17,6 (38) | 19,3 / 45,6 (113) |
| Otro heno (37) | 54,2 / 79,7 | — | 65,0 / 72,6 | 49,5 / 73,8 | 56,7 / 65,0 | 46,3 / 60,2 | 35,6 / 3,1 (171) | 20,8 / 5,1 (306) |
| Avena (28) | 0,7 / 4,4 (4) | 0 / 0 | 66,7 / 60,0 (6) | 0 / 0 | 0 / 0 | 11,6 / 71,4 (5) | 0 / 0 | 4,2 / 25,0 (1) |
| Barbecho (61) | 25,8 / 63,9 | 0,6 / 50,0 (1) | 38,5 / 79,2 (664) | 35,0 / 56,2 (712) | 35,1 / 73,7 | 45,3 / 97,2 (139) | 14,3 / 100 (1) | 0 píxeles de referencia |
| Pastizal/pastura (176) | — | — | — | — | — | 65,3 / 57,1 | 73,2 / 80,2 | 86,0 / 85,7 |

Rangos 2008–2025: maíz 80,8–96,8 / 84,7–97,2; soja 75,7–93,8 / 80,1–95,5; doble trigo/soja 79,3–94,8 / 85,4–95,6; trigo de invierno 4,7–29,0 / 10,4–78,4 (91–2.638 píxeles correctos); tabaco 12,0–58,4 / 51,4–87,1 (27–1.782); alfalfa 13,4–42,7 / 17,6–95,4; otro heno 20,8–65,0 / 3,1–84,0; barbecho 0–62,3 (el máximo, 2019, con 5.761 píxeles correctos; como en MI, MO, WI y SD, el barbecho sube en 2019, sin causa verificada).

Ojo con heno, alfalfa y tabaco antes de 2023: la validación de 2008–2022 no incluye pastizal como clase de referencia (la nota de las tablas excluye "FSA-sampled grass and pasture"), así que la precisión del usuario de esos años no ve la confusión con pastizal. En 2024–2025, con pastizal en la referencia, el usuario de otro heno cae de 60–84 % a 3–5 %. Lo más probable es que los valores de antes de 2023 sobreestimen la calidad de las forrajeras (inferencia, no verificada con la matriz de esos años, que el HTML no trae).

**4. Con qué se confunde (hoja "All - Matrix" de los xlsx 2024–2025).** Filas = clase del CDL, columnas = referencia (FSA); comprobado: maíz 2024, 9.052 / suma de la columna (10.749) = 84,2 % = productor del "Summary Table". Porcentajes sobre la fila (lo que el CDL marca) o sobre la columna (lo que es en el terreno):
- **Maíz y soja ↔ pastizal (176).** Es la confusión principal en KY, más que maíz ↔ soja. Del maíz real, el CDL marca como pastizal el 8,8 % (2024) y el 11,4 % (2025), y como soja el 2,8 % y el 2,3 %. De la soja real, el 12,0 % y el 15,2 % queda como pastizal, y el 3,2 % y el 3,1 % como maíz. De lo que el CDL marca como maíz, es pastizal el 6,3 % y el 6,2 %; de lo marcado como soja, el 9,1 % y el 7,5 %.
- **Trigo de invierno (24) ↔ doble trigo/soja (26).** De lo que el CDL marca como trigo de invierno (106 y 111 píxeles), es doble cultivo el 39,6 % y el 35,1 %. Del trigo de invierno real (143 y 240 píxeles), el CDL marca como doble cultivo el 23,8 % y el 37,1 %, y como pastizal el 28,7 % y el 28,3 %. En la muestra, el doble cultivo es 15–25 veces más abundante (3.494 y 3.519 píxeles de referencia). El doble cultivo real se confunde poco: 7,7 % como pastizal y 6,2–6,4 % como soja. Existe también doble trigo/maíz (225; 26,5 / 65,5 % en 2008, 30,3 / 70,7 % en 2023).
- **Tabaco ↔ pastizal.** Del tabaco real (212 y 258 píxeles), el CDL marca como pastizal el 58,5 % y el 60,1 %, y como soja, maíz o pasto el resto. Lo que el CDL sí marca como tabaco suele serlo (usuario 69,7–87,1 %), pero encuentra solo una parte.
- **Heno y alfalfa ↔ pastizal.** De lo que el CDL marca como otro heno (5.514 y 6.052 píxeles), es pastizal el 83,5 % y el 77,5 %. De lo marcado como alfalfa, el 75,0 % y el 44,4 %. De la alfalfa real, el 61,5 % y el 63,9 % queda como pastizal y el 17,2 % y el 12,3 % como otro heno. Del otro heno real, el 57,1 % y el 70,9 % queda como pastizal. En la muestra hay 10–40 veces más pastizal que heno, por eso la precisión del usuario del heno se hunde.
- **Avena y barbecho:** 23–24 píxeles de referencia de avena y 0–7 de barbecho por año; la matriz no dice nada útil.

**5. Dónde el CDL no sirve para rotaciones.**

| Clase | KY |
|---|---|
| Maíz | sirve con advertencia: productor 87–91 % en 2017–2023, 80,8–84,2 % en 2024–2025; el error se va a pastizal |
| Soja | sirve con advertencia: productor 83,5–87,6 % en 2017–2023, 75,7–78,4 % en 2024–2025 |
| Doble trigo/soja (26) | sirve (≥ 79,3 % / ≥ 85,4 %); es la forma normal del trigo en KY |
| Trigo de invierno (24) | **no sirve solo** (productor 4,7–29,0 %); sumar 24 + 26 (+ 225) como "trigo" |
| Tabaco (11) | **no sirve** (productor 12–58 %, < 30 % en 2008–2013 y 2024–2025; pocas decenas a cientos de píxeles) |
| Alfalfa (36) | **no sirve** (productor 13,4–42,7 %; usuario 17,6 % en 2024) |
| Otro heno (37) | **no sirve** (productor 20,8–65,0 %; usuario 3,1 y 5,1 % en 2024–2025; sin fila en 2011–2012) |
| Avena (28) | **no sirve** (0–13 píxeles correctos por año) |
| Barbecho (61) | **no sirve** (0–62 %, casi sin validación) |
| Pastizal (176) | sin precisión antes de 2023; 65–86 % en 2023–2025 |

Lo que agrega a los research anteriores:
- KY tiene el CDL más débil de los estados revisados (global FSA 56,3–60,1 % en 2024–2025), por el peso de heno y pastizal en el paisaje. En maíz y soja el problema no es maíz ↔ soja sino cultivo ↔ pastizal: las transiciones `pct_maiz_tras_soja` etc. salen bien, pero los porcentajes de área de maíz y soja pueden quedar cortos (productor 76–84 % en 2024–2025) y una parte del área agrícola se pierde en "pastizal".
- Si se suma KY, en `rotacion_anual.csv` y `rotacion_secuencia.csv` el grupo "trigo" tendría que ser 24 + 26 + 225, y el doble cultivo es la rotación típica (maíz → trigo/soja doble). En `data/reference/clases_cdl.csv`, la 225 (doble trigo/maíz) está en el grupo `otro`; habría que pasarla a un grupo de trigo.
- Para tabaco, heno, alfalfa y pastura conviene la superficie de NASS (Quick Stats o Censo) y no el CDL, como en los otros estados. El tabaco tampoco es un cultivo de `config/config.yaml`.
- La máscara agrícola de KY (§6.2: "cultivo agrícola en al menos un año del CDL") va a tener ruido de píxeles de pastizal marcados como maíz o soja algún año (6–9 % de lo marcado como maíz o soja es pastizal en 2024–2025).

Fuentes: [2008–2023 CDL state metadata (USDA NASS), páginas `metadata-ky<aa>`](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ky08), consultado 2026-11-15 (16 páginas); [CDL_2024_accuracy_assessments.zip (USDA NASS)](https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/CDL_2024_accuracy_assessments.zip), consultado 2026-11-15 (xlsx de KY; hojas "Summary Table" y "All - Matrix"); [CDL_2025_accuracy_assessments.zip (USDA NASS)](https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/CDL_2025_accuracy_assessments.zip), consultado 2026-11-15 (ídem).

Confianza: alta para los valores (extraídos por script de las tablas oficiales; 16 HTML y 2 xlsx); alta para que la clase 176 no tiene precisión antes de 2023; media para la lectura de las matrices (orientación comprobada con un valor; solo 2024–2025); media para que las forrajeras de antes de 2023 están sobreestimadas (inferencia a partir de la nota de las tablas y de 2024–2025); baja para la causa de la falta de fila de otro heno en 2011–2012 y de la caída de píxeles en 2015 (no verificadas).

Impacto: decisión del humano sobre una cuarta tanda con KY (`config/config.yaml`); si entra, `data/reference/clases_cdl.csv` (pasar 225 del grupo `otro` a uno de trigo), el grupo "trigo" de `rotacion_anual.csv` y `rotacion_secuencia.csv` (24 + 26 + 225), y el data card `docs/datasets/cultivos.md` (Problemas conocidos: tabla de la sección 5 y la caída de 2024–2025). Opcional: sumar `cdl_precision_ky.csv` a la tabla de referencia de precisión para ML. No cambia `config/` ahora.

Citas:
> "Winter Wheat                       24      2638     17.6%     82.4%     0.175     66.0%     34.0%     0.658" — [2008 Kentucky CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ky08)
> "Dbl Crop WinWht/Soybeans           26    224212     88.3%     11.7%     0.869     85.4%     14.6%     0.838" — [2008 Kentucky CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ky08)
> "Tobacco                         11       858     58.41%    41.59%   0.584     80.19%     19.81%    0.802" — [2016 Kentucky CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ky16)
> "Other Hay/Non Alfalfa            37     40,002      46.3%      53.7%      0.425      60.2%      39.8%      0.564" — [2023 Kentucky CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ky23)
> "Grassland/Pasture               176     72,706      65.3%      34.7%      0.602      57.1%      42.9%      0.518" — [2023 Kentucky CDL metadata (USDA NASS)](https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-ky23)
