# Dosis de N para maíz y crédito de N de la rotación (7 estados del Corn Belt)

Pregunta: ¿Cuál es la dosis económica de N para maíz tras soja y maíz tras maíz en IA, IL, IN, OH, NE, MN y KS,
con qué relación de precios; cuánto N acreditan la soja, la alfalfa y los cultivos de cobertura al maíz
siguiente; y de qué año es cada recomendación?

Respuesta corta: hay dos familias de guías.

- **Estados MRTN** (IL, IN, MN, OH; IA hasta 2024): la dosis sale de ensayos de respuesta a N por rotación, ya
  separada en "maíz tras soja" y "maíz tras maíz". **El efecto de la soja ya está incluido: no se resta un
  crédito aparte.** La diferencia típica maíz/maíz − maíz/soja es de unas 35–45 lb N/ac.
- **Estados con fórmula de rendimiento esperado** (NE, KS): N = f(rendimiento esperado, materia orgánica,
  nitrato residual…) y después se **resta un crédito por cultivo previo** (KS: soja −40 lb N/ac; NE: soja
  según textura, 35 lb N/ac en suelos gruesos).
- Iowa dejó la calculadora regional MRTN y desde febrero de 2025 recomienda su propia herramienta, **N-FACT**
  (Iowa Nitrogen Initiative). No pude abrirla ni obtener sus valores.

Detalle: abajo, una sección por estado y la tabla resumen al final.

---

## La calculadora regional (Corn Nitrogen Rate Calculator, MRTN)

- Sitio: https://www.cornnratecalc.org (el viejo `cnrc.agron.iastate.edu` ya no responde con certificado
  propio). Consultado 2026-11-15.
- Estados disponibles en el formulario hoy: **IL, IN, MI, MN, OH, WI**. **Iowa ya no está** en la lista
  (el contacto de Iowa aparece oculto en la página).
- Valores por defecto del formulario: N a **0,40 USD/lb N** y maíz a **4,00 USD/bu** → relación de precios
  **0,10** (USD por lb de N / USD por bu de maíz). El Illinois Agronomy Handbook dice que la relación real "se
  mantuvo cerca de" 0,1 a lo largo del tiempo. Rotaciones: `cc` (maíz tras maíz) y `cs` (maíz tras soja).
- No hay API pública. No corrí la calculadora para cada estado (su endpoint interno no es para uso
  automatizado), así que los valores de abajo salen de las guías publicadas por cada universidad.
- Las dosis MRTN son **totales** para la rotación: la propia calculadora dice que no se ajustan además por el
  cultivo previo (o sea, no se resta crédito de soja encima).

---

## Iowa (IA)

- **Herramienta actual:** N-FACT (Nitrogen Fertilizer Application Consultation Tool), de la Iowa Nitrogen
  Initiative (Iowa State). Presentada el 4 de febrero de 2025; usa ensayos en campos de productores y
  pide ubicación, rotación, clima, fecha de siembra y precios. Se presenta como sucesora del MRTN.
  - Fuentes secundarias (no abrí `n-fact.ag`): nota de prensa de Clean Water Iowa (IDALS) y Iowa Soybean
    Association. **Valores de dosis por rotación de N-FACT: no encontrados.**
- **Último MRTN de Iowa abierto** (Mallarino, Iowa State, "Soil Fertility: Current Topic", 12-abr-2022; la
  calculadora se actualizó en abril de 2022 con 30 sitios-año nuevos; la anterior era de 2019). Maíz a
  6,50 USD/bu y anhidro a 1400 USD/t (≈0,85 USD/lb N → relación **≈0,13**, calculada por mí):

  | Región de la calculadora | Maíz tras soja | Maíz tras maíz |
  |---|---|---|
  | "Main" (la mayor parte de Iowa) | 137 (127–147) | 180 (171–189) |
  | Sudeste de Iowa (SEIA) | 146 (137–156) | 196 (183–208) |

  Desde 2025 Iowa ya no figura en la calculadora regional; estos valores son **anteriores a N-FACT**.
- Crédito de soja: incluido en la dosis MRTN (no se resta aparte).
- Alfalfa y cultivos de cobertura: no verificado en una fuente de Iowa abierta en esta tarea.

## Illinois (IL)

- **Guía:** MRTN con datos propios de Illinois, en tres regiones (norte, centro, sur) y dos rotaciones.
  Fuente principal: Nafziger, *Nitrogen Management for Corn*, capítulo 9 del **Illinois Agronomy Handbook**
  (PDF de abril de 2022). La guía dice que se use el MRTN y que **no** se use más la recomendación por
  rendimiento esperado (la vieja regla de 1,2 lb N/bu menos un crédito de soja de 40 lb N/ac).
- **MRTN maíz tras soja (Handbook 2022, relación 0,10):** sur **200**, centro **181**, norte **171** lb N/ac.
  Maíz tras maíz: unas **35 lb más** en el norte, **20 lb más** en el centro y **casi igual** en el sur.
  Los MRTN "subieron en cada región en los últimos cinco años" al sumar ensayos.
- **Valores más recientes abiertos (farmdoc daily, 31-mar-2026, centro de Illinois):**

  | Rotación | Precios otoño 2025 | Precios primavera 2026 |
  |---|---|---|
  | Maíz tras soja | 178 lb N/ac | 172 lb N/ac |
  | Maíz tras maíz | 194 lb N/ac | 186 lb N/ac |

  Precios usados: maíz 4,15 USD/bu (otoño) y 4,50 USD/bu (primavera); N 0,48 USD/lb (anhidro 787 USD/t)
  y 0,61 USD/lb (anhidro 1000 USD/t). Relación calculada por mí: **0,116** (otoño) y **0,136** (primavera).
- **Crédito de soja:** ya incluido (son bases de datos separadas por rotación).
- **Alfalfa:** restar **125 a 150 lb N/ac** al MRTN de maíz tras soja si el stand era bueno, hasta 0 si
  quedaban pocas plantas.
- **Cultivos de cobertura:**
  - centeno con más de 1 t/ac de materia seca al secarlo → usar el MRTN de **maíz tras maíz**;
  - leguminosa (trébol) secada varias semanas antes de sembrar → extremo bajo del rango del MRTN maíz/soja,
    y restar **20–30 lb** si ya se está descomponiendo al sembrar; si se secó cerca de la siembra → el MRTN;
  - tras trigo u otro cereal de invierno → MRTN de maíz tras soja.

## Indiana (IN)

- **Guía:** Camberato y Nielsen, *Nitrogen Management Guidelines for Corn in Indiana*, Purdue, **actualizada
  en abril de 2022** (166 ensayos desde 2006). Es una tabla de EONR propia de Purdue (no la calculadora),
  por región y por precios.
- **Maíz tras soja, EONR (lb N/ac)** a algunas relaciones de precio:

  | Región (Purdue) | AONR | 0,60 USD/lb, 6,00 USD/bu (0,10) | 0,75 USD/lb, 5,00 USD/bu (0,15) | 1,00 USD/lb, 5,00 USD/bu (0,20) |
  |---|---|---|---|---|
  | Centro | 232 | 205 | 192 | 178 |
  | Noreste y centro-este | 254 | 225 | 210 | 195 |
  | Resto (NC, NO, SC, SE, SO, OC y arenas sin riego) | 211 | 185 | 172 | 159 |

  (Las columnas 0,10 y 0,15 salen de las tablas 2–4; la de 0,20 de la figura 2.)
- **Maíz tras maíz:** no hay tabla; la guía dice que en ensayos pareados 2007–2010 el AONR de maíz/maíz fue
  **44 lb N/ac mayor** que el de maíz/soja (y el rendimiento 18 bu/ac menor). Regla vieja: 1 lb N/bu
  (maíz/soja) y 1,2 lb N/bu (maíz/maíz o maíz/trigo).
- Crédito de soja: implícito en las tablas de maíz tras soja.

## Ohio (OH)

- **Guía:** MRTN de la calculadora regional eligiendo Ohio. **Datos nuevos agregados en abril de 2025**
  (ensayos hasta 2024: 273 sitios de maíz tras soja y 83 de maíz tras maíz; C.O.R.N. Newsletter 2025-13).
  Revisión anterior grande: 2018.
- **Maíz tras soja (C.O.R.N. Newsletter 2026-06, UAN 28 %, maíz 4,50 USD/bu):**
  - UAN 400 USD/t → relación **0,158** → MRTN **160 lb N/ac** (rango a ±1 USD: 146–172);
  - UAN 450 USD/t → relación **0,178** → MRTN **152 lb N/ac** (139–165).
- **Maíz tras maíz:** el artículo no da el valor. **No encontrado.**
- Crédito de soja: incluido en el MRTN. Alfalfa y cobertura: no verificado en una fuente de Ohio.

## Nebraska (NE)

- **Guía:** Iqbal, Ferguson, Maharjan y Thompson, *Nutrient Management Suggestions for Corn* (EC117),
  **revisada en diciembre de 2023**, publicada con la herramienta web nueva en mayo de 2024
  (https://cropwatch.unl.edu/nitrogen-tool). Ya no es MRTN: es la ecuación de la UNL pasada a una herramienta.
- La ecuación usa rendimiento esperado (≈105 % del promedio de 5 años), nitrato residual 0–4 ft
  (−8 lb N/ac por ppm), materia orgánica, créditos de leguminosa, estiércol y agua de riego, y dos factores:
  - **Precio:** `Priceadj = 0,263 + 0,1256·(maíz:N) − 0,00421·(maíz:N)²`, con la relación **maíz:N** (USD/bu
    dividido USD/lb N; ojo, es la inversa de la de MRTN) limitada a 4–12. "Lo más común es alrededor de 8:1"
    (= 0,125 en la escala MRTN).
  - **Momento de aplicación** (`Timingadj`): 1,05 para aplicación de otoño, menor para fraccionada (tabla II).
- **Crédito de soja:** se resta (tabla I). El texto dice: **35 lb N/ac en suelos gruesos** (revisión por
  ensayos en Holt County), salvo que la soja haya rendido menos de 30 bu/ac, en cuyo caso el crédito es
  1 lb N por bu cosechado. El valor para suelos medios/finos y los de alfalfa y otras leguminosas están en la
  tabla I, que en el PDF es una imagen: **no pude leerlos.**
- Riego: el agua de riego aporta N (1 ppm de nitrato por pie de agua efectiva ≈ crédito); importa en NE.
- No hay dosis única por rotación: depende del rendimiento esperado del campo.

## Minnesota (MN)

- **Guía:** MRTN de la Universidad de Minnesota (Kaiser y col.), **actualizada en septiembre de 2025** con los
  ensayos de 2022, 2023 y 2024. Subió unas **10 lb N/ac** en ambas rotaciones. Aplica a maíz sin riego al sur
  de la I-94; el Red River Valley sigue la guía de NDSU; los suelos arenosos regados no cambiaron
  (tabla 2 de *Fertilizing Corn in Minnesota*).

  | Relación N:maíz | Maíz tras maíz MRTN (rango) | Maíz tras soja MRTN (rango) |
  |---|---|---|
  | 0,075 | 200 (180–220) | 155 (145–170) |
  | 0,100 | 185 (170–200) | 150 (135–160) |
  | 0,125 | 175 (160–190) | 140 (130–155) |
  | 0,150 | 165 (150–175) | 135 (125–145) |

- **Alfalfa (UMN, según el resumen del buscador; no abrí la tabla vigente):** con ≥4 plantas/ft²,
  150 lb N/ac el primer año de maíz y 75 lb N/ac el segundo; menos con stands más ralos.
- Cultivos de cobertura: no encontré un crédito publicado.

## Kansas (KS)

- **Guía:** Ruiz Diaz, *Soil Test Interpretations and Fertilizer Recommendations in Kansas*, MF2586,
  **enero de 2024**. Fórmula de rendimiento esperado, sin relación de precios:

  `N (lb/ac) = (ie/fe)·EY − se·N_perfil − (%MO × 20) − N_estiércol − otros + ajuste_cultivo_previo`

  - `ie` (lb N/bu): 0,84 regado, 0,88 secano. `fe`: 0,65 inyectado o fraccionado, 0,55 al voleo/otoño.
  - `se`: 1,0 (textura media u oeste de KS) o 0,7 (textura gruesa o este de KS). N de perfil por defecto 30 lb/ac.
  - Máximo 230 lb N/ac en secano y 300 en riego; mínimo 30.
- **Ajuste por cultivo previo para maíz (cultivos de verano):**
  - maíz, trigo, sorgo, girasol: 0; **soja: −40 lb N/ac**; barbecho sin test de perfil: −20;
  - **alfalfa:** stand excelente (>5 plantas/ft²) −120, bueno (2–5) −80, regular (1–2) −40, pobre (<1) 0;
  - trébol rojo: −80 / −40 / 0; trébol de olor (sweet clover): −110 / −60 / 0;
  - con siembra directa (sin labranza que destruya el stand) el crédito de leguminosa se reduce al 50 %.
- Cultivos de cobertura: la guía no trae un crédito específico.
- Ejemplo (mío, solo para ilustrar la fórmula): maíz de secano, EY = 150 bu/ac, fe = 0,55, se = 1,
  N de perfil 30, MO 2,5 %: (0,88/0,55)·150 − 30 − 50 = 160 lb N/ac tras maíz; 120 lb N/ac tras soja.

---

## Tabla resumen por estado

| Estado | Guía vigente (año) | Método | Maíz tras soja (lb N/ac) | Maíz tras maíz (lb N/ac) | Relación N:maíz usada | Crédito soja | Crédito alfalfa | Crédito cobertura | Cambió hace poco |
|---|---|---|---|---|---|---|---|---|---|
| IA | N-FACT (feb 2025); último MRTN abr 2022 | N-FACT: ensayos en campo por sitio; antes MRTN | MRTN 2022: Main 137 (127–147), SE 146 (137–156); N-FACT: no encontrado | MRTN 2022: Main 180 (171–189), SE 196 (183–208) | ≈0,13 (2022); N-FACT: la elige el usuario | incluido | no verificado | no verificado | sí: dejó el MRTN regional en 2025 |
| IL | MRTN (Handbook 2022; farmdoc mar 2026) | MRTN por región | N 171 / C 181 / S 200 a 0,10 (2022); centro 178 / 172 (2026) | N +35, C +20, S ≈ igual (2022); centro 194 / 186 (2026) | 0,10 (2022); 0,116 / 0,136 (2026) | incluido | −125 a −150 con buen stand | centeno >1 t/ac → usar MRTN maíz/maíz; trébol: −20 a −30 | sí: MRTN sube al sumar ensayos |
| IN | Purdue (abr 2022) | EONR propia por región | 159–225 según región y precio (central 192 a 0,15) | ≈ +44 sobre maíz/soja (AONR) | 0,10–0,20 en tablas | incluido | no verificado | no verificado | 2022 |
| OH | MRTN (datos nuevos abr 2025) | MRTN | 160 (146–172) a 0,158; 152 (139–165) a 0,178 | no encontrado | 0,158–0,178 | incluido | no verificado | no verificado | sí: ensayos hasta 2024 agregados en 2025 |
| NE | EC117 (dic 2023) + herramienta web (may 2024) | fórmula rendimiento esperado × precio × momento | depende del campo | depende del campo | maíz:N 4–12 (típico 8 ≈ 0,125) | se resta; 35 en suelos gruesos | en tabla I (no legible) | no encontrado | sí: herramienta web 2024 |
| MN | UMN MRTN (sep 2025) | MRTN | 150 (135–160) a 0,10 | 185 (170–200) a 0,10 | 0,075–0,15 | incluido | 150 (1.er año), 75 (2.º) con ≥4 pl/ft² (no confirmado) | no encontrado | sí: +10 lb en 2025 |
| KS | MF2586 (ene 2024) | fórmula rendimiento esperado | fórmula − 40 | fórmula | ninguna | −40 | −120 / −80 / −40 / 0 según stand | no trae | revisión 2024 |

---

Fuentes:
- [Corn Nitrogen Rate Calculator (página y formulario)](https://www.cornnratecalc.org/calculator/?mode=single), consultado 2026-11-15
- [Nafziger, Nitrogen Management for Corn, Illinois Agronomy Handbook cap. 9 (PDF abr-2022)](https://extension.illinois.edu/sites/default/files/iah_-_nitrogen_management_for_corn_v4.pdf), consultado 2026-11-15
- [OSU C.O.R.N. Newsletter 2025-13, MRTN calculator updated](https://agcrops.osu.edu/newsletter/corn-newsletter/2025-13/corn-n-recommendations-maximum-return-n-calculator-updated), consultado 2026-11-15
- [OSU C.O.R.N. Newsletter 2026-06, Rising nitrogen prices](https://agcrops.osu.edu/newsletter/corn-newsletter/2026-06/rising-nitrogen-prices-and-implications-corn-fertility-decisions), consultado 2026-11-15
- [Mallarino, Considerations for Spring Preplant N Application for Corn with High Fertilizer Prices, Iowa State, 12-abr-2022](https://www.agronext.iastate.edu/soilfertility/currenttopics/Spring2022Nfertilization4-12-2022.pdf), consultado 2026-11-15
- [farmdoc daily, "High Fertilizer Prices Suggest Reconsidering Application Rates", 31-mar-2026](https://farmdocdaily.illinois.edu/2026/03/high-fertilizer-prices-suggest-reconsidering-application-rates.html), consultado 2026-11-15
- [Camberato y Nielsen, Nitrogen Management Guidelines for Corn in Indiana, Purdue, abr-2022](https://www.agry.purdue.edu/Ext/corn/news/timeless/NitrogenMgmt.pdf), consultado 2026-11-15
- [UMN Crop News, "Updated corn nitrogen rates: what are we...", 26-sep-2025](https://blog-crop-news.extension.umn.edu/2025/09/updated-corn-nitrogen-rates-what-are-we.html), consultado 2026-11-15
- [UNL EC117, Nutrient Management Suggestions for Corn, rev. dic-2023](https://extensionpubs.unl.edu/publication/ec117/na/pdf/view), consultado 2026-11-15
- [UNL CropWatch, "Nitrogen Management Suggestions for Corn Updated in EC117, EC155, and EC2008", 9-may-2024](https://cropwatch.unl.edu/2024/nitrogen-management-suggestions-corn-updated-ec117-ec155-and-ec2008), consultado 2026-11-15
- [K-State MF2586, Soil Test Interpretations and Fertilizer Recommendations in Kansas, ene-2024](https://bookstore.ksre.ksu.edu/pubs/MF2586.pdf), consultado 2026-11-15
- Solo por resultados de búsqueda (no abiertos): [Clean Water Iowa, N-FACT, 4-feb-2025](https://www.cleanwateriowa.org/news-releases/2025/2/6/02-04-2025-secretary-naig-encourages-farmers-to-use-n-fact-tool-to-calculate-optimal-nitrogen-application-rates); [UMN, Fertilizing corn in Minnesota](https://extension.umn.edu/crop-specific-needs/fertilizing-corn-minnesota)

Confianza: alta para KS, IN, IL, MN y la ecuación de NE (documentos abiertos); media para OH (solo maíz tras
soja, sin maíz tras maíz); media para IA (MRTN 2022 abierto, pero la guía vigente es N-FACT y no pude ver sus valores) y para los créditos de alfalfa de
MN y de leguminosas de NE (no leídos en la fuente).

Impacto: `config/cultivos.csv` (columna de fijación de N / crédito al cultivo siguiente) y el modelo de
comparación de rotaciones (regla de costo de N por rotación). Ningún paquete de datos de `src/` cambia.
