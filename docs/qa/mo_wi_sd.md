# Control de calidad: MO, WI y SD (release `datos-mo-wi-sd`)

Tarea T081 (mismo control que T073, `docs/qa/oh_ne_mn.md`). Fecha: 2026-11-15. Máquina: pro-3.

Se bajaron los 9 zips del release `datos-mo-wi-sd` (base + 8 paquetes) y sus `.sha256` con `curl -L` a
`data/entregas/datos-mo-wi-sd/` (fuera de git), y se descomprimieron en `data/entregas/mo-wi-sd-ext/`. Los
números salen de `scripts/qa_release.py` (T097) con los eventos de `docs/qa/eventos_mo_wi_sd.yaml` (T117), que
solo leen:

```bash
.venv/bin/python -X utf8 scripts/verificar_entrega.py data/entregas/datos-mo-wi-sd/*.zip --salida data/entregas/informes-mo-wi-sd
.venv/bin/python -X utf8 scripts/qa_release.py data/entregas/mo-wi-sd-ext --eventos docs/qa/eventos_mo_wi_sd.yaml \
    --qs data/entregas/nass_qa/qs.crops_20261114.txt.gz > data/entregas/qa_mo_wi_sd.md
```

Los controles puntuales (SMAP en los condados de WI sobre los lagos, Oglala Lakota, cobertura de `ndvi_soja` por
año) se hicieron con pandas sobre los mismos CSV; los números están abajo.

## Resultado por paquete

| paquete | `verificar_entrega.py` | QA de contenido | Veredicto |
|---|---|---|---|
| `base` | APTO | 253 condados (MO 115, SD 66, WI 72), el total esperado | **APTO** |
| `agua` | APTO | SMAP sin faltantes en los 72 condados de WI (también los de los lagos); 2019 visible en MO y SD | **APTO** |
| `clima` | APTO | todos los eventos visibles; sin outliers entre vecinos; rangos dentro del spec | **APTO** |
| `cultivos` | **NO APTO** | 18 rendimientos fuera del rango actual de `validar_csv()`: 12 + 7 son 0 de NASS sin cosecha de grano (T148), 6 son bajos pero reales (problema 1); superficie cierra con NASS sumando la fila 998 | **APTO con observaciones** una vez resuelto T148 o mergeado PR #143 (T145) |
| `economia` | APTO | no se controló el contenido | **APTO** (solo formato) |
| `nldas` | APTO | no se controló el contenido (el YAML de MO/WI/SD no tiene eventos de NLDAS) | **APTO** (solo formato) |
| `paisaje` | APTO | no se controló el contenido | **APTO** (solo formato) |
| `suelo_terreno` | APTO | 253 condados, 1 fila por condado | **APTO** (solo formato) |
| `vegetacion` | APTO | eventos visibles; `ndvi_soja` de WI casi vacío (problema 2) | **APTO con observaciones** |

Nada aparece mal calculado. El NO APTO de `cultivos` viene del rango físico de `validar_csv()` en `main`, no de un
error de proceso: con el rango de PR #143 (T145, pendiente de revisión) las 18 filas pasan.

## 1. `verificar_entrega.py`

- Los 9 `.sha256` coinciden con `sha256sum -c` directo (fin de línea LF; ya no hace falta el `tr -d '\r'` de T073).
- 8 APTO, 1 NO APTO (`cultivos`):
  - `produccion_anual.csv: rend_bu_ac de maiz: 17 valores fuera de 20-300 bu/ac`
  - `produccion_anual.csv: rend_bu_ac de soja: 1 valores fuera de 5-100 bu/ac`
- Detalle de esas 18 filas (todas de SD):

| fips | condado | años | cultivo | rend_bu_ac | sup. cosechada | lectura |
|---|---|---|---|---|---|---|
| 46063 | Harding | 2000, 2002, 2005, 2006 | maíz | 0,0 | vacía | NASS: sin cosecha para grano (silo). T148 |
| 46081 | Lawrence | 2000–2006 | maíz | 0,0 | vacía | idem |
| 46117 | Stanley | 2002 | maíz | 0,0 | vacía | idem |
| 46055 | Haakon | 2003, 2006 | maíz | 17,5; 18,3 | 400; 600 ac | real (sequía, secano) |
| 46102 | Oglala Lakota | 2003, 2004 | maíz | 17,1; 13,3 | 1.400; 600 ac | real |
| 46103 | Pennington | 2002 | maíz | 4,5 | 1.100 ac | real |
| 46103 | Pennington | 2003 | soja | 2,9 | 2.100 ac | real |

- Además (no lo marca `verificar_entrega.py` porque no tiene rango de avena): 7 filas de avena con
  `rend_bu_ac` = 0 y sin superficie cosechada en 46033 (Custer), 46081 (Lawrence) y 46095 (Mellette), 2002–2004.
  Es el mismo patrón de T148; esa tarea ya pide revisar los otros cultivos.

## 2. Eventos extremos

Medias de condado por estado (tablas completas: salida de `qa_release.py`). Esperado según
`docs/research/eventos_extremos_mo_wi_sd.md`.

| Evento | Esperado | Se ve | ¿OK? |
|---|---|---|---|
| SD 2002 | maíz ≈ 95 bu/ac | rendimiento implícito 95,0 (109 en 2001, 111 en 2003) | sí |
| SD 2006, sequía | `spi3` jun–ago < 0, lluvia baja, maíz −14 % | `spi3` −1,66; `prec_temporada_mm` 353 (460 y 452 en los años vecinos); maíz −13,7 % | sí |
| SD 2022 | maíz −11 % | −12,4 % | sí |
| MO 2007, helada de Pascua | marzo cálido, heladas en abril, trigo −19 %, maíz no cae | `anom_tmed_c` mar +4,09 °C; `dias_tmin_le0` abr 8,3 (1,4 en 2006); `dias_tmin_le_m2` 5,6 (0 en 2006); trigo −18,4 % | sí |
| WI 2008, inundaciones de junio | `prec_max5d_mm` jun alto; soja −8 % | 97,9 mm (38,7 y 45,0 en los vecinos); `dias_lluvia_gt50` 0,60 (0 y 0,03); soja −8,3 %; `ratio_cosechada` estatal no se mueve (0,98) | sí (el ratio se diluye a nivel estado, como avisa el YAML) |
| MO 2011, dique de Birds Point (29133) | `ratio_cosechada` y superficie baja | maíz: ratio 0,83 (0,96 en 2010 y 2012), sembrada 37,8 mil ac (66,3 y 76,0); trigo: ratio 0,69 (0,90 y 0,95) | sí |
| 2012, sequía (los 3) | `spi3` jul < 0, calor, NDVI y VHI bajos; maíz MO −44 %, SD −25 %, WI −19 % | `spi3` MO −2,53 / SD −1,21 / WI −0,48; `dias_tmax_gt35` 14,9 / 9,9 / 2,3; `ndvi_anom_z` −2,49 / −1,59 / −1,35; `vhi` 4,9 / 17,7 / 22,8; maíz −43,5 / −24,2 / −19,2 %; soja −23,5 / −20,3 / −1,5 % | sí (los rendimientos coinciden con NASS al punto) |
| SD 2017, sequía relámpago | `spi` may–jul muy negativo, trigo −19 % | `spi1` −0,68, `spi3` −0,97; `ndvi_anom_z` −0,36; trigo −16,0 % | sí, más débil a nivel estado (el research dice que el daño fue al oeste del Missouri) |
| MO 2018, sequía en el norte | `spi3` < 0; maíz −12 % | `spi3` −0,74; maíz −10,9 % | sí |
| MO 2019, Atchison y Holt | lluvia de marzo, `sm_rootzone_anom_z` alto, superficie baja | `prec_power_mm` mar 91 mm (37 y 56); SMAP `sm_rootzone_anom_z` mar–may +2,14; **superficie y `ratio_cosechada` de 2019 vacíos** | sí en clima y SMAP; **en NASS no se puede ver** (ver nota) |
| SD 2019, siembra prevenida récord | lluvia abr–jun alta, siembra tardía, superficie muy baja | lluvia abr–jun 311 mm (244 y 184); SMAP +1,73; `prec_max5d_mm` sep 81 mm; `doy_50_sembrado` maíz 155 (138 y 131); maíz sembrado (suma de condados) 2,11 M ac (4,44 y 4,79); soja 1,71 M ac (5,01 y 4,86) | sí (la suma de condados exagera la caída: ver sección 5) |
| WI 2019, primavera húmeda | lluvia de mayo alta, siembra tardía | `prec_power_mm` may 148 (131 y 111); `doy_50_sembrado` 148 (138 y 129); superficie de maíz (suma de condados) 3,45 M ac (3,40 en 2018, 3,94 en 2020) | sí en clima y fenología; la superficie no baja contra 2018 (2018 tiene pocos condados publicados en WI, sección 5) |
| SD 2021, sequía | `spi3` < 0, maíz −13 %, trigo −26 % | `spi3` −1,21; `ndvi_anom_z` −0,27; maíz −16,9 %; trigo −29,9 % | sí |
| WI 2023, sequía de primavera sin caída de rendimiento | `spi1` may–jun < 0, déficit jun; maíz sin caída | `spi1` −1,48; `spi3` −0,67; `deficit_mm` jun −73,8 (−39,1 y +64,4); maíz +1,0 % | sí |

Nota sobre MO 2019 (Atchison y Holt): `produccion_anual.csv` no tiene superficie de maíz ni de soja para esos dos
condados en 2019 (NASS no los publicó por condado; MO 2019 es el año con menos condados, sección 6). No es un
error del proceso.

## 3. Rangos

| cultivo | MO (mín–máx bu/ac) | SD | WI |
|---|---|---|---|
| maíz | 22,3–223,1 | **0,0**–223,8 | 49,0–217,9 |
| soja | 8,9–63,2 | **2,9**–66,9 | 16,0–67,6 |
| trigo de invierno | 18,6–104,5 | 11,7–84,2 | 22,0–94,7 |
| avena | 33,6–85,5 | **0,0**–121,3 | 21,0–115,0 |

- Los 0 son los de T148 (sección 1). Sin ellos, el mínimo de maíz de SD es 4,5 (Pennington 2002) y el de avena,
  el que quede después de T148.
- Con los rangos de PR #143 (maíz 2–300, soja 2–100, trigo 5–130, avena 2–200, y el 0 aceptado solo sin
  superficie cosechada ni producción) todos los valores pasan. Si T148 deja los 0 vacíos, también pasan.
- Clima diario: `tmin_c` mín −42,4 °C (55119 Taylor WI, 31-1-2019), `tmax_c` máx 47,5 °C (46123 Tripp SD,
  16-7-2006), `prec_power_mm` máx 174 mm/día (29035, 18-3-2008), `prec_imerg_mm` máx 174 mm/día (29119,
  27-12-2015). Dentro del spec.
- Mensual: lluvia ≤ 414 mm, `gdd_10_30` ≤ 540, `tmin_c` ≥ −25,1. Dentro del spec.
- Lluvia anual IMERG / POWER (mediana): MO 1,09, SD 1,09, WI 1,08 (OH 1,18, NE y MN 1,07 en T073). Sin sesgo
  raro.

## 4. Outliers por condado (contra sus 6 vecinos más cercanos)

Mismo puntaje robusto que T073.

- `prec_temporada_mm` y `gdd_temporada` (|z| > 4): **ninguno**. Ningún condado con lluvia media 2000–2025 a
  más de 25 % de la de sus vecinos.
- Rendimiento de maíz (|z| > 5): 29 condado-años; de soja: 13. **Casi todos en el oeste de SD** (Butte 46019,
  Bennett 46007, Todd 46121, Fall River 46047, Buffalo 46017, Lawrence 46081, Pennington 46103, Lyman, Hughes,
  Perkins). Son condados con poco maíz y soja, mezcla de riego (Butte tiene riego del Belle Fourche) y secano, y
  vecinos con muy pocas filas: es el mismo patrón de Boyd (NE) en T073 y el problema conocido de
  `ALL PRODUCTION PRACTICES` (T004). Fuera de SD: Webster MO 2023, Wayne MO 2007 (soja); Bayfield WI 2010 y
  Milwaukee WI 2000 (soja, condados con muy poca soja). No se abre tarea nueva.
- **Oglala Lakota (46102)**: está en los 16 CSV con `fips` con el código nuevo y **no aparece 46113** (el código viejo de
  Shannon) en ningún archivo. `produccion_anual.csv` tiene sus filas de NASS de 2000 en adelante (maíz
  2000–2025, 12 años) bajo 46102: la recodificación funciona. Sus rendimientos de maíz bajos de 2003–2004
  (17,1 y 13,3) tienen superficie cosechada: son reales.

## 5. Faltantes por estado

Columnas donde algún estado supera en más de 15 puntos al data card de `main` (IA/IL/IN); al lado, el valor de
OH/NE/MN de T073.

| archivo | columna | IA/IL/IN % | MO % | SD % | WI % | OH / NE / MN % (T073) |
|---|---|---|---|---|---|---|
| practicas_censo.csv | pct_drenaje_tile | 34,2 | 41,7 | **55,1** | 41,2 | 33,3 / 62,0 / 38,3 |
| fenologia_anual.csv | ndvi_max_maiz | 38,5 | **70,3** | 44,2 | **69,2** | 66,4 / 40,2 / 51,6 |
| fenologia_anual.csv | ndvi_max_soja | 38,6 | **61,3** | 53,1 | **90,4** | 59,7 / 60,1 / 52,5 |
| vegetacion_16d.csv | ndvi_maiz | 43,4 | **72,0** | 53,2 | **76,0** | 70,0 / 43,9 / 61,8 |
| vegetacion_16d.csv | ndvi_soja | 43,7 | 62,9 | 60,9 | **92,7** | 63,2 / 63,2 / 63,2 |
| vegetacion_mensual.csv | ndvi_maiz | 40,7 | **70,9** | 50,3 | **74,3** | 68,2 / 42,7 / 59,7 |
| vegetacion_mensual.csv | ndvi_soja | 41,0 | 61,7 | 58,4 | **92,1** | 61,6 / 62,1 / 61,0 |

- `pct_drenaje_tile` en SD: como NE, el Censo no publica el dato en muchos condados del oeste. Esperable.
- `ndvi_maiz` / `ndvi_soja`: 2000–2007 faltan siempre (no hay CDL nacional). De 2008 en adelante, % de
  condado-meses con dato por año (`vegetacion_mensual.csv`):

  | estado | `ndvi_maiz` | `ndvi_soja` |
  |---|---|---|
  | MO | 34–52 % | 41–63 % |
  | SD | 55–88 % | 44–76 % |
  | WI | 28–49 % | **4–20 %** |

  **WI `ndvi_soja` es el peor de los diez estados:** solo 27 de los 72 condados tienen algún mes con dato en
  2008–2025. Con el umbral de 75 % de soja en el píxel de 250 m, los lotes chicos de WI casi nunca dan píxeles
  puros. Es consecuencia del umbral documentado, no un error, pero para el modelo `ndvi_soja` de WI es casi
  inutilizable (problema 2).
- SMAP en los condados de WI sobre los lagos Michigan y Superior (Door, Kewaunee, Manitowoc, Sheboygan, Ozaukee,
  Milwaukee, Racine, Kenosha, Douglas, Bayfield, Ashland, Iron): **0 % de faltantes** en `agua_diario.csv`; en
  `agua_mensual.csv` el 0,8 % es el mismo para los 253 condados (un mes de borde de la serie), no algo de los
  lagos.
- Todas las demás columnas de los 8 paquetes quedan a menos de 15 puntos de IA/IL/IN.

## 6. Superficie sembrada: suma de condados contra NASS a nivel estado

Base completa de Quick Stats (`qs.crops_20261114.txt.gz`, en `data/entregas/nass_qa/`, fuera de git).
`AREA PLANTED`, SURVEY, `ALL PRODUCTION PRACTICES`.

| estado | cultivo | % mín (año) | % mediana 2000–2025 | % máx |
|---|---|---|---|---|
| MO | maíz | 45,3 (2019) | 89,8 | 99,8 |
| MO | soja | 54,7 (2019) | 95,1 | 100,0 |
| SD | maíz | 48,4 (2019) | 96,1 | 100,0 |
| SD | soja | 48,9 (2019) | 96,6 | 100,0 |
| WI | maíz | 87,3 (2018) | 99,5 | 99,9 |
| WI | soja | 74,8 (2018) | 99,2 | 100,0 |

- **Sumando "OTHER (COMBINED) COUNTIES" (998), cierra:** MO y WI 100,0 % en todos los años; SD maíz
  96,5–100,0 %, SD soja 95,1–100,0 %. El proceso de `cultivos` no pierde nada: lo que falta es lo que NASS juntó
  en 998, que se deja afuera a propósito (CLAUDE.md §6.2). Los 3–5 puntos que faltan en SD (2015, 2017 y 2019)
  no se investigaron.
- 39 años con la suma de condados por debajo de 85 %. **MO es el peor de los diez estados:** maíz por debajo de
  85 % en 11 de los últimos 13 años (mediana 89,8 %; 44 condados publicados en 2025 de 115). SD 2019 (24
  condados de maíz y 20 de soja) es el año más pobre del release.
- Para el modelo: en MO y SD, desde 2013, una fracción grande de la superficie no tiene rendimiento de condado.

## 7. Precisión del CDL (`docs/research/cdl_precision_mo_wi_sd.md`)

- Maíz y soja sirven en los tres estados (≥ 82 %); WI soja (82–90 % del productor) y MO maíz (< 90 % en
  2017–2022 y 2025) son los más débiles. Ojo con `pct_maiz_tras_maiz` y `pct_soja_tras_soja` de WI: la
  confusión soja ↔ maíz del CDL (4–7 % en 2024–2025) genera transiciones falsas.
- **No sirven:** trigo de invierno en MO (productor 28–50 % desde 2017), doble cultivo en WI y SD, avena y
  alfalfa en MO, barbecho en MO y WI, otro heno en 2024–2025. Las columnas `pct_doble_trigo_soja`,
  `pct_alfalfa`, `pct_heno` y `pct_barbecho` de esos estados no deberían usarse para MO/WI/SD sin advertencia.
- Lo bueno: `pct_trigo` ya suma CDL 24 + 26 (lo que recomienda el research para MO).
- **El data card de `cultivos` del zip no menciona la precisión del CDL de MO/WI/SD** (problema 3).

## Problemas

1. **Rendimientos 0 de NASS sin cosecha de grano en SD** (12 de maíz, 7 de avena). Es lo que hace NO APTO a
   `cultivos` en `verificar_entrega.py` de `main`. Ya hay tareas: **T148** (dejarlos vacíos con `flag_nass`) y
   **T145 / PR #143** (rangos nuevos). Las dos se pisan en la decisión (vaciar el 0 o aceptarlo): ver "Para
   decidir". No se abre tarea nueva.
2. **`ndvi_soja` de WI casi vacío** (4–20 % por año desde 2008; 45 de 72 condados sin ningún dato). No es un
   error de código sino del umbral de 75 %. Propuesta (decisión del humano, cambia el contenido de una columna
   del contrato): probar un umbral de 50 % en WI y MO, o agregar una columna con el NDVI ponderado por la
   fracción del cultivo. No se abre tarea sin esa decisión.
3. **Data card de `cultivos`: falta la precisión del CDL de MO/WI/SD** en "Problemas conocidos" (qué columnas
   de `rotacion_anual.csv` y `rotacion_secuencia.csv` no sirven por estado, según la tabla de la sección 7). Es
   documentación del paquete; tarea propuesta abajo.
