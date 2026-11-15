# Rangos físicos de los checks para los estados nuevos (OH, NE, MN, KS)

Pregunta: Los rangos de `validar_csv()` (`src/common/validacion.py`) y de `loop/spec/entregables.yaml` se
pensaron para IA, IL e IN. ¿Dejan afuera datos reales de OH, NE, MN y KS entre 2000 y 2025 (rendimiento de
condado de maíz, soja, trigo de invierno y avena; lluvia, temperaturas extremas y GDD)? ¿Qué rangos conviene usar?

Respuesta corta: **Sí, en el rendimiento; casi nada en el clima.** El mínimo de maíz de `validar_csv()` (20 bu/ac)
queda pegado a datos reales: con el Censo Agropecuario 2012, el rendimiento implícito de condado (producción /
superficie cosechada, todas las prácticas, condados con ≥ 500 ac) llega a **21,7 bu/ac en Osage, KS** y a
**21,1 en Clay, IL**; la encuesta (SURVEY) por condado y, sobre todo, el maíz de **secano** de KS y NE (si se
agregan las columnas `*_secano_*` de `riego_nass.md`) van a caer por debajo de 20. En soja, el Censo 2022 da
**7,2 bu/ac en Chautauqua, KS** (mínimo actual 5): el secano de KS en 2012 o 2022 puede quedar debajo. Trigo de
invierno y avena no tienen rango propio en `validar_csv()`. Los máximos (maíz 300, soja 100) sobran. En el clima,
con POWER en los rincones más extremos de los 4 estados, todos los valores entran en el spec; el único margen
chico es la **tmin diaria** de Minnesota: −48,0 °C en St. Louis (2-2-1996) contra un mínimo de −50. Propuesta:
bajar el mínimo de maíz a 5 bu/ac y el de soja a 2, agregar trigo de invierno (5–130) y avena (10–200), y bajar la
tmin diaria a −55 °C y la tmed diaria a −50 °C. Ningún cambio está aplicado: lo decide el humano.

## Tabla de la propuesta

| Variable | Dónde | Rango actual | Rango propuesto | Valor real que lo justifica |
|---|---|---|---|---|
| `rend_bu_ac` maíz | `validar_csv()` (`RENDIMIENTO_BU_AC`) | 20–300 | **5–300** | Censo 2012: Osage KS 21,7; Clay IL 21,1 (todas las prácticas, ≥ 500 ac). Secano y encuesta por condado: más bajo (sin cifra propia, ver Detalle) |
| `rend_bu_ac` soja | `validar_csv()` | 5–100 | **2–100** | Censo 2022: Chautauqua KS 7,2; Censo 2012: Ellsworth KS 10,2; mapa NASS KS 2023: 8,6 |
| `rend_bu_ac` trigo de invierno | `validar_csv()` | (sin rango) | **5–130** | Censo: mín. 15,3 (Kimball NE 2022), máx. 100,7 (Bartholomew IN 2022); mapa NASS KS 2023: 16,4–79,9 |
| `rend_bu_ac` avena | `validar_csv()` | (sin rango) | **10–200** | Censo: mín. 15,2 (Keith NE 2022), máx. 138,3 (Nobles MN 2017) |
| `rend_bu_ac` (todos) | spec `cultivos`, `produccion_anual` | 0–320 | sin cambio | máx. Censo 226,8 (maíz, Grundy IA 2022) |
| `rend_kgha` | spec | 0–20000 | sin cambio | 300 bu/ac de maíz = 18.831 kg/ha |
| `rend_secano_bu_ac` y `rend_riego_bu_ac` (si se aprueban, `riego_nass.md`) | `validar_csv()` | "iguales al total" | **los mismos de arriba**, con maíz desde 5 | el secano es el que cae en las sequías (NE 2012: 59 bu/ac estatal de secano, `eventos_extremos.md`) |
| `tmin_c` diario | spec `clima_diario` | −50–40 | **−55–40** | POWER −48,0 °C (St. Louis MN, 2-2-1996); −45,5 en Kittson MN el mismo día |
| `tmed_c` diario | spec `clima_diario` | −45–45 | **−50–45** | POWER −40,6 °C (St. Louis y Kittson MN, 1996) |
| `tmax_c` diario | spec `clima_diario` | −40–50 | sin cambio | POWER máx. 45,5 °C (Cherokee KS, 2-8-2011); mín. −34,2 (MN) |
| `prec_*_mm` diario | spec | 0–500 | sin cambio | POWER máx. 102,9 mm/día (Cherokee KS, 20-5-2019) |
| `prec_*_mm` mensual | spec `clima_mensual` | 0–1500 | sin cambio | POWER máx. 419,2 mm (Cherokee KS, mayo 2019) |
| `tmax_c` / `tmin_c` mensual | spec | −30–45 / −40–35 | sin cambio | POWER: tmax media mensual 39,4 (Morton KS, jul 2011); tmin media −27,1 (Kittson MN, ene 2014) |
| `gdd_10_30` mensual | spec | 0–650 | sin cambio | POWER máx. 550,1 (Cherokee KS, jul 2011) |
| `dias_tmax_gt35` mensual | spec | 0–31 | sin cambio | 30 días (Morton KS, jul 2011) |
| `prec_temporada_mm` | spec `clima_anual` | 0–2500 | sin cambio | POWER 160,6 (Morton KS 2011) a 1220,9 (Cherokee KS 2019) |
| `gdd_temporada` | spec `clima_anual` | 0–4000 | sin cambio | POWER 930 (St. Louis MN 2014) a 2372 (Cherokee KS 2024) |
| `tmax_jul_c` | spec `clima_anual` | 10–45 | sin cambio | POWER 22,1 (St. Louis MN 2009) a 39,4 (Morton KS 2011) |
| Lluvia anual (no está en el spec) | — | — | — | POWER 224,5 mm (Kimball NE 2012) a 1723,8 mm (Cherokee KS 2019) |

Nada más del spec de clima quedó cerca del borde. Las demás variables (suelo, terreno, vegetación, `pct_*`,
`doy_*`) no las revisé con datos de los estados nuevos (ver "Lo que no se hizo").

Detalle:

**De dónde salen los rendimientos.** No pude usar la encuesta (SURVEY) de Quick Stats: la API devuelve 401 sin
clave, esta máquina no tiene `NASS_API_KEY` a mano y el índice de la base completa
(`https://www.nass.usda.gov/datasets/`) no devolvió la lista de archivos (lo mismo dice `eventos_extremos.md`).
Usé dos fuentes que sí abrí:

1. **Censo Agropecuario 2012, 2017 y 2022**, de los archivos completos que ya estaban en
   `data/raw/cultivos/nass/qs.census<año>.txt.gz` (solo lectura). El script
   `docs/research/rangos_estados_nuevos_censo.py` calcula producción / superficie cosechada por condado
   (`CORN, GRAIN`, `SOYBEANS`, `WHEAT, WINTER`, `OATS`; `DOMAIN_DESC=TOTAL`; sin `county_code` 998; condados con
   ≥ 500 ac cosechados) y da mínimo, p01, mediana y máximo por estado, cultivo y año. La salida está en
   `docs/research/rangos_estados_nuevos_censo.csv`. Con umbral 1 ac (corrida aparte, no guardada) cambia solo el
   mínimo de maíz de MN 2012 (57,5 en St. Louis) y aparecen unos pocos condados más; los mínimos de KS e IL no
   cambian. El Censo no trae producción con riego por condado, así que **no da rendimiento de secano**.
2. **Mapas de rendimiento por condado de NASS Kansas, 2023** (los únicos años que la oficina de Kansas tiene en
   la web): maíz 55,0 (Russell) a 211,1 (Meade); soja 8,6 a 61,6; trigo de invierno 16,4 a 79,9; avena 62,9 a 96,7.
   Son de la encuesta, todas las prácticas.

Mínimos y máximos del Censo (bu/ac, todas las prácticas, ≥ 500 ac):

| Estado | Maíz 2012 | Maíz 2022 | Soja 2012 | Soja 2022 | Trigo inv. (3 censos) | Avena (3 censos) |
|---|---|---|---|---|---|---|
| OH | 66,3–158,9 | 120,0–204,0 | 30,4–54,1 | 30,2–60,5 | 36,3–91,3 | 40,8–95,9 |
| NE | 60,6–193,7 | 53,6–220,0 | 20,5–60,8 | 26,3–65,2 | 15,3–75,0 | 15,2–78,4 |
| MN | 90,0–184,7 | 91,4–220,2 | 17,8–54,3 | 23,1–63,1 | 34,1–73,8 (1–14 condados) | 32,7–138,3 |
| KS | 21,7–178,6 | 28,0–196,2 | 10,2–51,6 | 7,2–62,8 | 21,9–63,3 | 18,4–78,9 |
| IA (control) | 42,2–173,4 | 116,1–226,8 | 23,5–54,9 | 35,4–68,1 | 27,8–88,3 | 43,2–125,0 |
| IL (control) | 21,1–167,1 | 139,0–233,3 | 22,5–55,5 | 42,1–69,9 | 38,9–97,4 | 56,9–98,9 |

**Por qué bajar el mínimo de maíz a 5 y no a 15.** El Censo cuenta todas las explotaciones y promedia riego y
secano: en Osage (KS) 2012 ya da 21,7. La encuesta por condado puede dar menos (otra muestra), y el maíz de secano
de KS y NE en 2012 (59 bu/ac de promedio estatal en NE, según `eventos_extremos.md`) seguramente tiene condados más
bajos que ese promedio (supuesto, no verificado). No encontré la cifra de condado de secano de KS 2012 en una fuente que haya podido abrir:
el número exacto sale de Quick Stats con `prodn_practice_desc=NON-IRRIGATED` (ver "Cómo verificar"). Un check
físico debería rechazar errores (unidades, relleno, coma decimal), no años malos: 5 bu/ac sigue atrapando un `0`
mal convertido. Si el humano prefiere 10, cubre todo lo visto en el Censo; el riesgo es el secano de 2012.

**Soja.** El Censo 2022 ya está a 2,2 bu/ac del mínimo actual (Chautauqua, KS, 7,2). En sequía el secano de KS
puede bajar de 5. Propongo 2.

**Trigo de invierno y avena** no tienen rango en `validar_csv()`, solo el general del spec (0–320). Los rangos
propuestos dejan margen sobre lo visto en el Censo (trigo 15–101, avena 15–138) y sobre el trigo de KS 2014
(28 bu/ac de promedio estatal, el peor desde 1995, `eventos_extremos.md`).

**Clima.** El script `docs/research/rangos_estados_nuevos_power.py` pide a la API diaria de NASA POWER (comunidad
`AG`, `T2M`, `T2M_MAX`, `T2M_MIN`, `PRECTOTCORR`, 1981–2025) la serie de 9 puntos elegidos por ser extremos
(SO y SE de KS, O y SE de NE, NO y NE de MN, S y NE de OH, y Story IA como control) y calcula las variables con
las definiciones del paquete `clima` (GDD 10/30 recortando tmax y tmin, temporada abril–septiembre). Salida en
`docs/research/rangos_estados_nuevos_power.csv`. Los extremos diarios se tomaron de 1981–2025 porque la diaria se
usa desde 1981 para SPI y climatologías; los mensuales y anuales, de 2000–2025. Son puntos (celda de POWER de
0,5° × 0,625°), no medias de condado: la media del condado es igual o menos extrema que la celda, salvo que el
condado cruce celdas más extremas que el punto elegido. Por eso el margen de la tmin diaria (−48,0 contra −50)
se toma como insuficiente.

**Lo que no se hizo / no encontré.**
- Rendimiento de encuesta (SURVEY) por condado de los 4 estados, 2000–2025, y el de secano/riego de NE y KS:
  sin clave de NASS ni base completa en esta máquina. Lo de abajo lo deja listo.
- Temperaturas extremas de estaciones NOAA: no busqué; los checks se aplican a POWER, que es lo que entra en
  los CSV.
- Lluvia de IMERG y PRISM: no revisada (los rangos del spec, 0–500 diario y 0–1500 mensual, tienen mucho margen
  sobre POWER).
- `lat_centroide` [35, 50], `lon_centroide` [−105, −80] y `area_km2` [1, 20000] del spec de `base`: no pude
  verificarlos porque `data/reference/condados.csv` no está en esta máquina. Por los límites de los estados
  deberían entrar (MN llega a ~49,4° N; NE a ~−104,05°; OH a ~−80,5°), pero el condado más grande de los 7
  estados (St. Louis, MN, con mucha agua) puede acercarse a 20.000 km²: conviene correr `validar_csv()` sobre
  `condados.csv` y mirar el máximo.
- Suelo, terreno, vegetación y agua: no revisados con datos de los estados nuevos. Elevación: el oeste de NE
  pasa de 1.500 m, dentro de [−10, 2000].

**Cómo verificar el rendimiento de encuesta** (en una máquina con `NASS_API_KEY` o con
`qs.crops_*.txt.gz`): filtrar `source_desc=SURVEY`, `agg_level_desc=COUNTY`, `statisticcat_desc=YIELD`,
`unit_desc=BU / ACRE`, `commodity_desc` en `CORN` (`util_practice_desc=GRAIN`), `SOYBEANS`, `WHEAT`
(`class_desc=WINTER`), `OATS`, `state_alpha` en `OH, NE, MN, KS`, `year` 2000–2025, sin `county_code` 998, y
`prodn_practice_desc` en `ALL PRODUCTION PRACTICES`, `IRRIGATED`, `NON-IRRIGATED`. Contar cuántas filas caen
fuera de los rangos actuales y de los propuestos. Con la API, son 4 estados × 4 cultivos = 16 consultas, cada una
muy por debajo de las 50.000 filas.

Fuentes:
- [NASS Quick Stats, Censo Agropecuario 2012, 2017 y 2022 (archivos completos `qs.census2012.txt.gz`, `qs.census2017.txt.gz`, `qs.census2022.txt.gz`)](https://quickstats.nass.usda.gov/), copias locales en `data/raw/cultivos/nass/` bajadas el 2026-11-15, consultado 2026-11-15
- [NASS Kansas, County Estimates (mapas 2023 de maíz, soja, trigo de invierno y avena: `23KScorn.pdf`, `23KSsoy.pdf`, `23KSww.pdf`, `23KSoats.pdf`)](https://www.nass.usda.gov/Statistics_by_State/Kansas/Publications/County_Estimates/index.php), consultado 2026-11-15
- [NASA POWER, API diaria por punto (comunidad AG)](https://power.larc.nasa.gov/api/temporal/daily/point), consultado 2026-11-15
- `docs/research/eventos_extremos.md` y `docs/research/riego_nass.md` de este repo (rendimientos estatales de secano y cobertura por práctica)

Confianza: **media** para el rendimiento (datos reales del Censo, pero no de la encuesta que va en
`produccion_anual.csv`, y sin el secano); **alta** para el clima (POWER directo, mismas definiciones que el
paquete), con la salvedad de que son puntos y no medias de condado.

Impacto: `src/common/validacion.py` (`RENDIMIENTO_BU_AC`: maíz, soja, y agregar `trigo_invierno` y `avena` con
los nombres de cultivo que use `produccion_anual.csv`) y `loop/spec/entregables.yaml` (`clima_diario`: `tmin_c` y
`tmed_c`). Paquetes `cultivos` y `clima` de OH, NE, MN y KS. Requiere el OK del humano (CLAUDE.md, regla 4).
