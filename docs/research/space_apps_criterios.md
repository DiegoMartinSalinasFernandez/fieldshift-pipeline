# Criterios de evaluación de Space Apps 2026 y cómo mostrar nuestros datos

Pregunta: ¿Qué evalúan los jueces de NASA Space Apps Challenge 2026 y qué pide el desafío "Field Shift: Adapting
Farms with NASA Data"? ¿Qué hay que entregar, en qué formato y hasta cuándo? ¿Qué partes de nuestros datos conviene
mostrar en la demo y cómo se citan?

Respuesta corta:

- **Plazo: domingo 15 de noviembre de 2026 a las 23:59, hora local del evento local del equipo** (en el Universal
  Event, hora local del Team Owner). Es **hoy**. Después de esa hora no se puede guardar ni enviar, y lo que se
  envíe tarde no entra en la evaluación.
- Hay **cinco criterios**, cada uno puntuado de 1 a 5 en todas las etapas: **Impact, Creativity, Validity,
  Relevance y Presentation**. Relevance pide que los datos de la NASA sean "a core component", no "a superficial
  addition". La guía pide darle a Presentation el mismo peso que a los otros cuatro.
- **Se entrega** la página del proyecto en el sitio, toda en inglés: nombre, resumen, link a la demo, link al
  proyecto final, descripción detallada, uso de SI (IA), datos de la NASA y otras referencias. La **demo es un
  video de 30 segundos o menos** (se puede hablar en otro idioma con subtítulos en inglés) **o hasta 7
  diapositivas** (en inglés). **Si se pasa de esos límites, el proyecto queda fuera del Global Judging.** Los links
  tienen que ser públicos, sin login.
- Para competir por un premio global hay que usar **al menos un dato o recurso de la NASA**. También se recomienda
  usar datos de las agencias socias: el desafío propone **ESA Sentinel-2** y **ERA5**. Nuestro HLS S30 sale de
  Sentinel-2 (ver §5).
- **Fechas siguientes:** Global Nominees el 3 de diciembre de 2026, Global Finalists el 17 de diciembre de 2026 y
  Global Winners el 26 de enero de 2027.
- **Para la demo** conviene mostrar cinco cosas: (1) el mapa del Corn Belt con la rotación real (CDL y CSB), (2)
  la comparación de al menos 3 rotaciones con su incertidumbre, (3) un lote con sus sectores (`lotes`), (4) la
  validación satélite contra superficie (`validacion`) y (5) una lámina de fuentes con los productos de la NASA y
  sus DOI (`citas_nasa.md`). Detalle en §6.

Detalle:

Método. El sitio oficial (`www.spaceappschallenge.org`) no se pudo abrir desde esta máquina: la verificación del
certificado TLS falla ("unable to get local issuer certificate") y el fetcher web da el mismo error. Por eso leí
las **copias de Internet Archive** de las tres páginas, tomadas el 2026-11-13 y el 2026-11-14 (fechas en la URL de
cada fuente), y extraje el texto del HTML. Las dos guías dicen "November 12, 2026" como fecha de actualización.
La página del desafío trae `lastPublishedAt: 2026-11-13T03:53:29Z` en sus metadatos. Las citas textuales en inglés
están copiadas de esas copias. Si el sitio cambió después del 2026-11-14, esto no lo refleja.

## 1. Criterios de evaluación (Judging & Awards Guide 2026)

"At every level of judging, from Local and Universal Events to Executive Judging, your project will be evaluated on
a scale of 1-to-5, in each of the following criteria". Lo que define cada criterio y qué pide para un 5:

| Criterio | Qué mide | Para un 5 | Qué tenemos para eso |
|---|---|---|---|
| **Impact** | Si el problema que ataca es chico o grande, y a cuánta gente llega o inspira | "addressing a significant problem [...] Its reach is extensive [...] benefits a large audience" | 666 condados de 7 estados del Corn Belt; el riesgo de la rotación maíz–soja (ver `efecto_rotacion.md`, `eventos_extremos.md`) |
| **Creativity** | Originalidad: una idea nueva o una mejora real de lo que ya existe | "groundbreaking approach that has never been attempted before" | Rotaciones reales por píxel (CDL y CSB) cruzadas con clima, suelo y satélite; sectores dentro del lote |
| **Validity** | Base científica y factibilidad técnica; usabilidad | "scientifically sound and technically feasible [...] fully developed [...] highly usable and user-friendly" | Pipeline reproducible, `validar_csv()`, data cards, validación contra PRISM y CoCoRaHS, ML sin fugas |
| **Relevance** | Que responda al desafío y que los datos de la NASA sean centrales | "NASA data is integral to the project's success" | 12 productos de la NASA con DOI más POWER (`citas_nasa.md`); casi todos están en la lista del desafío |
| **Presentation** | Comunicación y storytelling; se evalúan la demo **y** el proyecto completo | "well-structured and compelling presentation [...] polished" | Video o láminas (skill `field-shift-video`) |

La guía advierte: "remember to pay equal attention to the final criterion: presentation". La de entrega agrega:
"the majority of judges' evaluation will be based on your project submission. Note: a strong project demo can
increase the potential for a high score in the Presentation category".

**Etapas** (misma guía):
1. **Jueces locales** (o de expertos en el Universal Event). Eligen a los **Global Nominees**, que se anuncian el
   **3 de diciembre de 2026**. Los premios locales van por separado.
2. **Global Judging**: jueces expertos eligen a los **Global Finalists**, que se anuncian el **17 de diciembre de
   2026**, junto con las Honorable Mentions.
3. **Executive Judging**: lo hacen la NASA y las agencias socias. Hay **10 premios globales**, que se anuncian el
   **26 de enero de 2027**. Los que mejor nos calzan son:
   - **Best Use of Data**: "best makes space data accessible or leverages it to a unique application";
   - **Best Use of Science**: "best and most valid use of the scientific method";
   - **Local Impact**: "greatest potential for making a difference in their local community";
   - **Galactic Impact**: "most potential to improve life on Earth".

   Los otros seis son Best Use of Technology, Best Mission Concept, Most Inspirational, Best Storytelling, Global
   Connection y Art & Technology.

**Requisitos para pasar al Global Judging** (resumen de la guía):
- responder a un desafío oficial (los "Create Your Own Challenge" no entran);
- todos los integrantes registrados en el mismo evento local, que figuren en la pestaña Members, con 6 personas como
  máximo (y al menos 2 en el Universal Event);
- completar todos los campos obligatorios;
- una demo dentro de los límites;
- todo en inglés;
- enviar antes del plazo;
- marcar las dos casillas: la de términos y la de "original work", que dice que todo recurso externo (código, texto
  e imágenes, aunque sean abiertos) figura en el campo References;
- la revisión de la política de NASA sobre China.

## 2. Qué se entrega (Project Submission Guide 2026)

Campos de la página del proyecto, que es "the page that the judges will review":

| Campo | Qué pide | Nota para nosotros |
|---|---|---|
| Project Name | Nombre del proyecto | |
| High-Level Project Summary | "What did you develop? How does it address the challenge? Why is it important?" | |
| Link to Project Demo | Video de ≤ 30 s **o** hasta 7 diapositivas (con la de título y la de intro), en un sitio externo y con link público | No se pueden subir videos ni documentos al sitio |
| Link to Final Project | Link público al proyecto: web, repo, Drive, etc. | El repo es público. Los datos están en los Releases (`scripts/entregar.py`) |
| Detailed Project Description | Qué hace, cómo funciona, beneficios, objetivos, herramientas y lenguajes | |
| Use of Super Intelligence (SI) | Si se usaron herramientas de IA y cómo | Ver §4 |
| NASA Data | "Provide specific details about what NASA data and resources you used. To be eligible for a Global Award, you must use at least one NASA data or resource." | §1 de `citas_nasa.md` |
| Space Agency Partner Data and Other References | Todos los datos, recursos y herramientas, incluido código, texto e imágenes abiertos | §2 de `citas_nasa.md` y §5 de este archivo |

Otros puntos de la guía:
- La página admite imágenes (JPG, PNG o GIF de hasta 10 MB), pero no videos ni documentos.
- El envío abre el sábado 14 a las 9:00 y cierra el **domingo 15 a las 23:59**, ambos en hora local del evento.
  Se puede editar y reenviar hasta el cierre; los jueces ven el último envío.
- Los links tienen que ser públicos: "If judges can't access your project, it can't be evaluated or judged".
  Conviene probarlos en una ventana privada.
- Si el proyecto es un sitio web nuevo, se sugiere (no es obligatorio) pedir la clasificación de FortiGuard Web
  Filter para que los jueces no lo encuentren bloqueado.
- No puede haber imágenes, video, audio ni semejanza de menores de 18 años.

**Guion sugerido para el video de 30 s** (textual de la guía):
- [0:00] Presentarse: nombre y nombre del equipo.
- [0:02] Qué desafío ataca el proyecto y por qué lo eligieron.
- [0:05] Título y tagline del proyecto.
- [0:10] Cómo funciona: imágenes o prototipo, la experiencia del usuario y "how using NASA's free and open data and
  Space Agency Partner data made your proposed solution possible".
- [0:20–0:30] El futuro: qué puede hacer la solución por la gente y por el mundo.

**Láminas:** que muestren el proyecto y la experiencia del usuario, cómo los datos de la NASA y de las agencias
socias hacen posible la solución, el nombre del equipo, sus integrantes y el desafío elegido.

## 3. Qué pide el desafío Field Shift

Página: `2026/challenges/adapting-farms-with-nasa-data`, niveles Intermediate y Advanced. Lo central:
- "create a decision‑support tool that uses NASA Earth observations along with local soil information, crop
  characteristics, and farmer priorities to help farmers explore rotation strategies that could strengthen soil
  health and adapt their farms to changing conditions".
- "You may compare at least three rotation strategies, including the existing rotation. For each strategy, you may
  explain why it was suggested, what evidence supports it, what benefits it may offer, where information gaps
  exist, and any risks that would need local review".
- "a supportive tool [...] does not replace farmer judgment or local agricultural expertise".
- Sugerencias (no obligatorias):
  - explicar términos (ET, anomalías de humedad, NDVI, riesgo de helada, balance hídrico);
  - "Clarify how satellite observations differ from ground‑based measurements";
  - explicar la incertidumbre del modelo;
  - armonizar resoluciones;
  - mostrar períodos de suelo desnudo y momentos de estrés;
  - mapas de vulnerabilidad a nivel lote (erosión, estrés hídrico, heladas);
  - dejar que el productor cargue sus prioridades.

**Datos que propone el desafío y cuáles usamos:**

| Recurso del desafío | ¿Lo usamos? | Dónde |
|---|---|---|
| SMAP | sí (L4, vía Crop-CASMA) | `agua` |
| GPM IMERG | sí (vía POWER) | `clima` |
| Landsat / MODIS (VIIRS no) | sí: Landsat C2 L2, MOD13Q1, MOD11A2 | `teledeteccion`, `vegetacion`, `lotes` |
| NASA POWER | sí | `clima`, `lotes` |
| SRTM / elevación NASA | sí (NASADEM, el SRTM reprocesado) | `suelo_terreno`, `lotes` |
| ECOSTRESS | sí (LST, ET, ESI, 2025) | `ecostress` |
| GRACE / GRACE-FO | sí (GRACE-DA-DM EE.UU.) | `agua` |
| NLDAS/GLDAS | sí (NLDAS-2 Noah) | `nldas` |
| Web Soil Survey / SSURGO | sí (SSURGO vía Soil Data Access) | `suelo_terreno`, `lotes` |
| CDL (CropScape) | sí | `cultivos`, máscaras, `lotes` |
| PRISM | sí, para validar | `validacion` |
| CoCoRaHS | sí, para validar | `validacion` |
| USDA NASS QuickStats | sí | `cultivos`, `economia` |
| USGS NLCD | sí (Annual NLCD) | `paisaje` |
| GEDI, NAIP, NWIS, OpenET, LANDFIRE, GAEZ, AMS Market News, Ag Data Commons | no | — |
| ESA Sentinel-2 (agencia socia) | indirecto: HLS S30 = Sentinel-2 armonizado por la NASA | `lotes` |
| ERA5 (ECMWF, en "Space Agency Partner Resources") | no | — |

Fuera de la lista del desafío, también usamos el CSB (USDA NASS), los costos y retornos de USDA ERS, USGS 3DEP y
AgTile-US.

## 4. Uso de IA ("Super Intelligence", SI)

Lo que dice la guía de entrega:
- Las herramientas de SI están permitidas, pero "SI should not be used to (come up with your idea of how to solve
  the challenge)".
- Hay que indicar dónde y cómo se usaron. Imágenes y videos: "Must include a visible watermark to indicate SI
  generation". Código y datos: "Must acknowledge SI generation in descriptive text and metadata".
- El contenido generado no puede usar ni modificar logos ni elementos de marca de la NASA.
- La respuesta del formulario no la ven los jueces. Sí ven las marcas, textos y metadatos del proyecto.

**Para nosotros:** gran parte del código del pipeline y de los data cards se escribió con agentes de Claude. Hay
que declararlo en el campo SI y en el README del repo: qué partes se hicieron con IA y que los datos se bajan de
las fuentes, no los genera la IA. Si el video usa imágenes o voz generadas, llevan marca de agua visible. La idea
de la herramienta tiene que ser del equipo.

## 5. Datos de agencias socias

Las agencias socias 2026 son 17. Entre ellas están **ESA** y la **Comisión Nacional de Actividades Espaciales
(CONAE) de Argentina** ("National Space Activities Commission of Argentina"). En sus recursos, el desafío solo
propone **Copernicus Sentinel-2 (ESA)** y **ERA5**. Lo que tenemos:
- **HLS S30 V2.0** (en `lotes`) es reflectancia de **Sentinel-2 MSI**, armonizada por la NASA. Se puede declarar
  como "NASA HLS, derived from ESA Copernicus Sentinel-2". La cita de HLS está en `citas_nasa.md` §1.10. **No
  verifiqué** el texto de atribución que pide Copernicus ("contains modified Copernicus Sentinel data [año]"):
  queda para revisar.
- ERA5 no lo usamos. No es indispensable: la guía lo recomienda, no lo exige.

## 6. Qué mostrar en la demo (propuesta)

Va ordenado según el guion de 30 s y los criterios. Cada punto dice de qué archivo sale y qué cita lleva. En las
láminas, cada imagen lleva su fuente abreviada abajo (p. ej. "Data: NASA SMAP L4 V8 (doi:10.5067/T5RUATAQREF8), USDA
NASS CDL"), y la lista completa va en la lámina final y en el campo NASA Data.

1. **Mapa del Corn Belt con la rotación real.** Muestra el % de maíz tras maíz, o de maíz–soja alternado, por
   condado. Responde a Impact y a "existing rotation".
   - Datos: `rotacion_anual.csv` y `rotacion_secuencia.csv` (paquete `cultivos`).
   - Cita: USDA NASS CDL y CSB (§2 de `citas_nasa.md`). No es dato de la NASA, así que **al lado tiene que haber
     una capa NASA**, para que Relevance no dependa del USDA.
2. **Comparación de 3 o más rotaciones**: la actual (maíz–soja), maíz continuo y una con trigo, avena o alfalfa.
   Cada una lleva su evidencia, beneficios, faltantes y riesgos, tal como pide el desafío.
   - Datos: `tabla_anual.csv` (rendimiento NASS + clima POWER/IMERG + suelo SSURGO), `efecto_rotacion.md` y
     `economia`.
   - Mostrar la **incertidumbre** (rango, no un número solo) y la frase de que no reemplaza el criterio del
     productor. Pesa en Validity y Relevance.
3. **Un lote por dentro.** Sectores de loma seca y bajo húmedo con relieve NASADEM, NDVI de Landsat/HLS y suelo
   SSURGO por píxel. Es lo más visual y lo más original (Creativity); responde a "field‑level vulnerabilities".
   - Datos: paquete `lotes` (entrega `fieldshift_lotes_v1`).
   - Citas: NASADEM (`10.5067/MEASURES/NASADEM/NASADEM_HGT.001`), HLS S30 y Landsat C2 L2 (USGS).
4. **Estrés en la temporada.** Una serie de humedad del suelo SMAP y otra de ESI de ECOSTRESS, con julio (floración
   del maíz) marcado.
   - Datos: `agua_mensual.csv`, `ecostress_mensual.csv` y `clima_mensual.csv`.
   - Así se ven dos satélites de la NASA "en acción" (Relevance, Best Use of Data). Ojo: ECOSTRESS solo cubre
     2025-04 a 2025-10.
5. **Satélite contra superficie.** Un gráfico de dispersión de la lluvia mensual IMERG/POWER contra PRISM y
   CoCoRaHS, con sesgo y correlación (tabla en `docs/datasets/validacion.md`). Responde a la sugerencia "satellite
   vs ground" y suma a Validity y Best Use of Science.
6. **Lámina o cierre de fuentes.** Los logos de misión no se pueden modificar con IA; mejor usar solo texto.
   - Lista de productos de la NASA con su DOI (§1 de `citas_nasa.md`).
   - El texto de reconocimiento de POWER, obligatorio porque no tiene DOI.
   - La línea "HLS (derived from ESA Copernicus Sentinel-2)".
   - El link al repo y a los Releases.

En 30 segundos no entran las seis. En el **video**, conviene 1 → 2 → 3, más una línea final de fuentes. En las
**7 láminas**: título y equipo, problema, (1), (2), (3), (4)+(5) y fuentes.

**Cómo citar en la entrega:**
- **Campo "NASA Data"**: un renglón por producto con nombre oficial, versión, DOI y para qué lo usamos, copiado
  de `citas_nasa.md` §1. Lo central es lo que usamos: POWER, IMERG, SMAP, MODIS, NASADEM, ECOSTRESS, HLS,
  GRACE-DA-DM y NLDAS-2.
- **Campo "Space Agency Partner Data and Other References"**:
  - HLS/Sentinel-2;
  - las fuentes USDA, USGS, PRISM y CoCoRaHS de `citas_nasa.md` §2;
  - las librerías principales (pandas, geopandas, rasterio, xarray, etc.);
  - las herramientas de IA usadas.
- Dejar en claro las versiones pendientes que marca `citas_nasa.md`: SMAP V8 y GRACE-DA-DM V4.0.

Fuentes:
- [Judging & Awards Guide 2026 (copia de Internet Archive del 2026-11-13)](https://web.archive.org/web/20261113172313/https://www.spaceappschallenge.org/resources/judging-awards-guide/),
  consultado 2026-11-15. Original: https://www.spaceappschallenge.org/resources/judging-awards-guide/ (no abrió
  por un error de certificado TLS).
- [Project Submission Guide 2026 (copia de Internet Archive del 2026-11-13)](https://web.archive.org/web/20261113172248/https://www.spaceappschallenge.org/resources/project-submission-guide/),
  consultado 2026-11-15.
- [Field Shift: Adapting Farms with NASA Data, detalles y recursos (copia de Internet Archive del 2026-11-14)](https://web.archive.org/web/20261114231258/https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/),
  consultado 2026-11-15.
- Repo: `docs/research/citas_nasa.md`, `docs/research/efecto_rotacion.md`, `docs/datasets/*.md`.
- No abrí la página de los ganadores 2025 (ejemplos de demos), las Terms & Conditions ni la página de las agencias
  socias. La lista de agencias sale de la guía de entrega.

Confianza:
- **Alta** para los criterios, los límites de la demo, los campos del formulario, el plazo y las fechas de anuncio:
  son texto textual de las guías oficiales de 2026 (actualizadas el 2026-11-12), leídas en copias del 2026-11-13.
  Riesgo: un cambio posterior a esas copias.
- **Alta** para el texto del desafío y su lista de recursos (copia del 2026-11-14, posterior a su última
  publicación del 2026-11-13).
- **Media** para la propuesta de demo (§6): es una recomendación nuestra, no un requisito.
- **Baja / sin verificar** para la atribución exacta que pide Copernicus para Sentinel-2.

Impacto:
- No cambia `config/` ni `src/`.
- Sirve para el video y las láminas (skill `field-shift-video`), para el frontend (`field-shift-frontend`: paneles de
  fuentes, 3 rotaciones, incertidumbre) y para completar el formulario de Space Apps.
- **Urgente: el envío cierra hoy, 2026-11-15, a las 23:59 hora local del evento del equipo.**
