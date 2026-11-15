# Fechas de siembra y cosecha de Michigan (MI) y Kentucky (KY)

Pregunta: Igual que T108 (`fechas_nd.md`), para MI y KY. Se piden las fechas habituales de siembra y cosecha de los
cultivos del proyecto según las tablas de cada estado del USDA Agricultural Handbook 628, copiadas tal cual y con su
página impresa. También se piden las filas propuestas para `config/cultivos_estado.csv`, sin aplicarlas, y la
comparación con el promedio de 5 años de Crop Progress de cada estado, usando `docs/research/fechas_nd_cp.py` con el
estado como argumento.

Respuesta corta: Las tablas están en el **Handbook 628, pág. 39 (Kentucky) y pág. 40 (Michigan)**. **MI** trae los
6 cultivos del proyecto: maíz, soja, trigo de invierno, avena, alfalfa y heno. **KY** trae 5, porque **no tiene
avena**. A diferencia de ND, en los dos estados la alfalfa y el heno traen también el período más activo de corte.
Hay 11 filas propuestas con códigos que ya existen (6 de MI y 5 de KY). Hay además 4 filas que necesitan códigos de
la propuesta T103 (`docs/research/propuesta_cultivos.md`, PR #104): **`maiz_silo`** en MI y KY, y **`cebada`** y
**`frijol_seco`** en MI. Esas filas solo van si el humano aprueba T103.

Crop Progress da el promedio **2021–2025** que publica NASS en los reportes de 2026. En MI y KY tiene maíz y soja
con todas las etapas. **MI está también en trigo de invierno y KY no**. **MI no está en avena**. La siembra coincide
con el Handbook dentro de una semana. La cosecha de maíz de MI va **más adelantada**: el 50 % se cosecha el 29 de
octubre, mientras que el período más activo del Handbook va del 10 de octubre al 25 de noviembre. La de KY coincide:
50 % el 30 de septiembre. Ventanas:

- **Floración del maíz (25–75 % *silking*):** en MI va del 16 de julio al 1 de agosto (50 % el 23 de julio). En KY
  va del 1 al 23 de julio (50 % el 10 de julio). Las dos caen casi enteras en julio (0,99).
- **Llenado de la soja (50 % *setting pods* → 25 % *dropping leaves*):** en MI va del 1 de agosto al 8 de
  septiembre (0,82 en agosto). En KY va del 3 de agosto al 11 de septiembre (0,74 en agosto).

De paso, se corrigió un error del script: cuando el estado no figuraba en una tabla, tomaba la fila del estado de la
tabla siguiente. La salida de ND no cambia con la corrección.

Detalle:

**1. Handbook 628 (NASS, *Field Crops Usual Planting and Harvesting Dates*, octubre de 2010).** Es el mismo PDF que
en T009 y T108. Texto copiado tal cual con `pdftotext -layout`.

*"Usual Planting and Harvesting Dates by Crop – Kentucky", página impresa 39.* La tabla termina justo antes del pie
"Field Crops Usual Planting and Harvesting Dates (October 2010) … 39". El índice también dice 39.

```
                                                          2009                   Usual planting dates                     Usual harvesting dates
                      State                             Harvested
                                                          acres          Begin       Most active          End     Begin        Most active           End

                                                       (1,000 acres)
Corn for grain ..................................            1,150     Apr 6     Apr 14 - May 24        Jun 8    Sep 1    Sep 9 - Oct 24           Nov 10
Corn for silage ................................                60     Apr 20    May 1 - Jun 10         Jun 25   Aug 20   Aug 25 - Sep 30          Oct 10
Hay, alfalfa .....................................             220     (NA)      (NA)                   (NA)     May 5    May 15 - Sep 1           Sep 15
Hay, other .......................................           2,300     (NA)      (NA)                   (NA)     May 15   Jun 1 - Sep 1            Oct 10
Soybeans .......................................             1,420     May 4     May 16 - Jun 27        Jul 7    Sep 25   Oct 10 - Nov 14          Nov 25
Tobacco, Class 2 1 ..........................                    9.1   May 11    May 17 - Jun 15        Jun 28   Aug 11   Aug 17 - Sep 25          Oct 5
Tobacco, Class 3A 2 .......................                     75.0   May 9     May 17 - Jun 17        Jun 28   Aug 10   Aug 16 - Sep 26          Oct 4
Tobacco, Class 3B 3 .......................                      4.6   May 11    May 17 - Jun 15        Jun 28   Aug 11   Aug 17 - Sep 25          Oct 5
Wheat, winter ..................................               390     Sep 27    Oct 6 - Nov 12         Nov 21   Jun 10   Jun 15 - Jul 4           Jul 10
(NA) Not available.
```

*"Usual Planting and Harvesting Dates by Crop – Michigan", página impresa 40.* La página comparte espacio con
Louisiana y Maryland. La tabla termina justo antes del pie "40 … Field Crops Usual Planting and Harvesting Dates
(October 2010)". El índice también dice 40.

```
                                                          2009                  Usual planting dates                         Usual harvesting dates
                      State                             Harvested
                                                          acres         Begin       Most active          End        Begin         Most active           End

                                                       (1,000 acres)
Barley, spring .................................                11     Apr 10   Apr 13 - May 20        May 27    Jul 26       Aug 3 - Aug 19          Aug 31
Beans, dry edible ...........................                  195.0   May 29   Jun 3 - Jun 17         Jun 28    Sep 3        Sep 12 - Oct 12         Oct 24
Corn for grain .................................             2,090     Apr 21   May 1 - May 27         Jun 6     Sep 5        Oct 10 - Nov 25         Dec 10
Corn for silage ...............................                220     Apr 21   May 1 - May 27         Jun 6     Aug 26       Sep 7 - Oct 10          Oct 20
Hay, alfalfa .....................................             700     (NA)     (NA)                   (NA)      May 31       Jun 15 - Sep 11         Oct 14
Hay, other ......................................              290     (NA)     (NA)                   (NA)      May 31       Jul 28 - Sep 11         Oct 14
Oats, spring ...................................                55     Apr 10   Apr 13 - May 14        May 22    Jul 19       Jul 28 - Aug 24         Sep 2
Potatoes, fall ..................................               43.5   Apr 16   Apr 24 - May 31        Jun 8     Jul 24       Aug 8 - Oct 19          Oct 28
Soybeans .......................................             1,990     May 2    May 11 - Jun 9         Jun 18    Sep 25       Oct 3 - Nov 3           Nov 13
Sugarbeets ....................................                136.0   Apr 7    Apr 10 - May 11        May 16    Sep 26       Oct 13 - Nov 3          Nov 11
Wheat, winter .................................                560     Sep 13   Sep 22 - Oct 22        Nov 1     Jul 6        Jul 11 - Jul 29         Aug 5
(NA) Not available.
```

Las notas 1 a 3 del tabaco de KY dicen: "Includes fire-cured types 21-23", "Includes light air-cured types 31-32" e
"Includes dark air-cured types 35-37". El tabaco, la papa y la remolacha no son cultivos del proyecto ni de la
propuesta T103, así que no tienen fila.

**2. Filas propuestas para `config/cultivos_estado.csv`.** No se aplicaron porque MI y KY no están en
`config/config.yaml`. El criterio es el mismo que en T009 y T108: la primera fecha del período más activo va a
`*_activa_inicio` y la segunda a `*_activa_fin`, y "(NA)" queda vacío. En alfalfa y heno, la cosecha va del primer
al último corte. Como acá el Handbook da el período más activo de corte, se completa igual que en IA, IL, OH y KS.

Con los códigos actuales (11 filas):

```
maiz,MI,04-21,05-01,05-27,06-06,09-05,10-10,11-25,12-10,"USDA NASS, Agricultural Handbook 628 (2010)",40
soja,MI,05-02,05-11,06-09,06-18,09-25,10-03,11-03,11-13,"USDA NASS, Agricultural Handbook 628 (2010)",40
trigo_invierno,MI,09-13,09-22,10-22,11-01,07-06,07-11,07-29,08-05,"USDA NASS, Agricultural Handbook 628 (2010)",40
avena,MI,04-10,04-13,05-14,05-22,07-19,07-28,08-24,09-02,"USDA NASS, Agricultural Handbook 628 (2010)",40
alfalfa,MI,,,,,05-31,06-15,09-11,10-14,"USDA NASS, Agricultural Handbook 628 (2010)",40
heno,MI,,,,,05-31,07-28,09-11,10-14,"USDA NASS, Agricultural Handbook 628 (2010)",40
maiz,KY,04-06,04-14,05-24,06-08,09-01,09-09,10-24,11-10,"USDA NASS, Agricultural Handbook 628 (2010)",39
soja,KY,05-04,05-16,06-27,07-07,09-25,10-10,11-14,11-25,"USDA NASS, Agricultural Handbook 628 (2010)",39
trigo_invierno,KY,09-27,10-06,11-12,11-21,06-10,06-15,07-04,07-10,"USDA NASS, Agricultural Handbook 628 (2010)",39
alfalfa,KY,,,,,05-05,05-15,09-01,09-15,"USDA NASS, Agricultural Handbook 628 (2010)",39
heno,KY,,,,,05-15,06-01,09-01,10-10,"USDA NASS, Agricultural Handbook 628 (2010)",39
```

**KY no tiene fila de avena** porque la tabla no la trae. No completé esa fila con otra fuente.

Con códigos nuevos (4 filas, **solo si se aprueba T103**: `maiz_silo`, `cebada` y `frijol_seco` son los nombres de
la propuesta T103 para `config/config.yaml` y `config/cultivos.csv`):

```
maiz_silo,MI,04-21,05-01,05-27,06-06,08-26,09-07,10-10,10-20,"USDA NASS, Agricultural Handbook 628 (2010)",40
cebada,MI,04-10,04-13,05-20,05-27,07-26,08-03,08-19,08-31,"USDA NASS, Agricultural Handbook 628 (2010)",40
frijol_seco,MI,05-29,06-03,06-17,06-28,09-03,09-12,10-12,10-24,"USDA NASS, Agricultural Handbook 628 (2010)",40
maiz_silo,KY,04-20,05-01,06-10,06-25,08-20,08-25,09-30,10-10,"USDA NASS, Agricultural Handbook 628 (2010)",39
```

El frijol de MI pesa bastante: 195 mil acres en 2009. Pero según `nass_mi_nd.md` solo tiene datos de condado en 2018.
La cebada de MI es chica (11 mil acres). Si se aplican, cada celda lleva su cita en
`docs/research/cultivos_fuentes.csv`, como en T009. La cita es la línea copiada arriba.

Comparación con los estados actuales:

- **KY** es el estado más temprano y más largo de todos. Su maíz empieza a sembrarse el 04-06, ocho días antes que
  IL (04-14), y termina el 06-08. Su soja tiene la siembra más larga: del 05-04 al 07-07, porque incluye la soja de
  segunda después del trigo. El trigo de invierno es el más tardío en la siembra (09-27 a 11-21) y el más temprano en
  la cosecha (06-10). El primer corte de alfalfa (05-05) es el más temprano de todos.
- **MI** se parece a MN y ND en la siembra: maíz del 04-21 al 06-06. La cosecha de maíz es la más tardía y la más
  larga de todas: termina el 12-10, más tarde incluso que ND (12-06), y el período más activo va del 10-10 al 11-25.

**3. Crop Progress de MI y KY, promedio de 5 años.** Usé `docs/research/fechas_nd_cp.py` con el estado como tercer
argumento:

```
.venv/bin/python -X utf8 docs/research/fechas_nd_cp.py /tmp/t113/cp 2026 Michigan > docs/research/fechas_mi_cp.csv
.venv/bin/python -X utf8 docs/research/fechas_nd_cp.py /tmp/t113/cp 2026 Kentucky > docs/research/fechas_ky_cp.csv
```

Hice dos cambios en el script:

- El estado va como tercer argumento opcional. Sin ese argumento, el script sigue usando North Dakota.
- Corregí un error. Antes, la búsqueda de la fila del estado cortaba solo en la próxima tabla de un cultivo de la
  lista y miraba hasta 60 líneas. Si el estado no figuraba en una tabla, tomaba su fila de la tabla siguiente, por
  ejemplo "Barley Condition" o "Pasture and Range Condition". Así salían para KY un trigo de invierno con 49 → 36 %
  emergido, y para MI una "cebada". Ahora la búsqueda corta en el título de cualquier tabla ("… - Selected States").

Para comprobar que ND no cambia, corrí ND con los mismos 31 reportes antes y después de la corrección, y las dos
salidas son idénticas. Contra el `fechas_nd_cp.csv` que está en el repo hay una sola diferencia: la siembra del trigo
de primavera tiene una semana más al principio (2026-04-05, 1 %). Los cruces del 10 al 90 % no cambian. La diferencia
viene de los reportes bajados, no del código.

Promedio **2021–2025** (columna "2021-2025 Average" de los reportes de 2026), cruces interpolados con fechas de un
año no bisiesto. "—" quiere decir que el promedio no cruzó ese umbral mientras el cultivo estuvo en la tabla.

*Michigan*

| Cultivo | Etapa | 10 % | 25 % | 50 % | 75 % | 90 % | Handbook 628 (inicio · activo · fin) |
|---|---|---|---|---|---|---|---|
| Maíz | sembrado | 04-30 | 05-08 | 05-16 | 05-25 | 06-03 | 04-21 · 05-01–05-27 · 06-06 |
| Maíz | cosechado | 10-01 | 10-13 | 10-29 | — (66 % el 11-08) | — | 09-05 · 10-10–11-25 · 12-10 |
| Soja | sembrado | 04-30 | 05-09 | 05-18 | 05-29 | 06-07 | 05-02 · 05-11–06-09 · 06-18 |
| Soja | cosechado | 09-24 | 10-05 | 10-17 | 11-03 | — (82 % el 11-08) | 09-25 · 10-03–11-03 · 11-13 |
| Trigo de invierno | sembrado | 09-19 | 09-30 | 10-12 | 10-26 | 11-07 | 09-13 · 09-22–10-22 · 11-01 |
| Trigo de invierno | cosechado | 07-06 | 07-12 | 07-19 | 07-27 | 08-05 | 07-06 · 07-11–07-29 · 08-05 |
| Avena | — | MI no está en las tablas de avena | | | | | 04-10 · 04-13–05-14 · 05-22 (siembra) |
| Alfalfa, heno | — | Crop Progress no tiene cortes por estado | | | | | 05-31 a 10-14 (los dos) |

*Kentucky*

| Cultivo | Etapa | 10 % | 25 % | 50 % | 75 % | 90 % | Handbook 628 (inicio · activo · fin) |
|---|---|---|---|---|---|---|---|
| Maíz | sembrado | 04-14 | 04-23 | 05-05 | 05-21 | 06-03 | 04-06 · 04-14–05-24 · 06-08 |
| Maíz | cosechado | — (11 % el 09-06) | 09-15 | 09-30 | 10-18 | 11-06 | 09-01 · 09-09–10-24 · 11-10 |
| Soja | sembrado | 04-21 | 05-02 | 05-20 | 06-08 | — (80 % el 06-14) | 05-04 · 05-16–06-27 · 07-07 |
| Soja | cosechado | 09-18 | 10-01 | 10-19 | 11-08 | — (75 % el 11-08) | 09-25 · 10-10–11-14 · 11-25 |
| Trigo de invierno | — | KY no está en las tablas | | | | | 09-27 · 10-06–11-12 · 11-21 (siembra) |
| Avena | — | ni en el Handbook ni en Crop Progress | | | | | — |
| Alfalfa, heno | — | Crop Progress no tiene cortes por estado | | | | | 05-05 a 09-15; 05-15 a 10-10 |

Lectura:

- **Siembra.** En los dos estados, el período más activo del Handbook cae cerca del tramo del 25 al 75 % de Crop
  Progress, como en ND. En MI, el 10 % de 2021–2025 llega unos 9 días después del "begin" del Handbook. En KY, el
  maíz empieza a sembrarse ahora una semana más tarde (10 % el 04-14 contra el 04-06), y la soja empieza dos semanas
  antes (04-21 contra 05-04). En la soja de KY, la tabla nacional deja de publicarse a mediados de junio con el 80 %
  sembrado. El resto es soja de segunda, que el Handbook estira hasta el 07-07.
- **Cosecha.** En el maíz de MI, Crop Progress va más adelantado que el Handbook: el 50 % llega el 10-29, cerca del
  centro del período más activo, que va del 10-10 al 11-25. La última semana publicada, el 11-08, tiene el 66 %. En
  KY, el maíz coincide con el Handbook (25–75 % del 09-15 al 10-18, contra un período activo del 09-09 al 10-24). La
  cosecha de soja coincide en los dos estados dentro de una semana. En MI, el trigo de invierno coincide casi exacto.

No cambié las filas propuestas por esto. Mismo criterio que en T108: el formato de `cultivos_estado.csv` es el del
Handbook, y mezclar las dos fuentes en una fila rompería la comparación con los otros estados.

**4. Ventanas críticas de MI y KY** (promedio 2021–2025 de Crop Progress, con las definiciones de
`ventanas_por_estado.md`). La fracción en el mes se calcula con días continuos: julio es [182, 213) y agosto es
[213, 244).

| Estado | Ventana | Inicio | 50 % | Fin | Duración | Fracción en el mes fijo |
|---|---|---|---|---|---|---|
| MI | Floración del maíz: *silking* 25 → 75 % | 07-16 (196,8) | 07-23 (204,4) | 08-01 (213,2) | 16 días | 0,99 en julio |
| KY | Floración del maíz: *silking* 25 → 75 % | 07-01 (181,7) | 07-10 (191,2) | 07-23 (203,5) | 22 días | 0,99 en julio |
| MI | Llenado de la soja: 50 % *setting pods* → 25 % *dropping leaves* | 08-01 (212,9) | — | 09-08 (250,8) | 38 días | 0,82 en agosto |
| KY | Llenado de la soja: 50 % *setting pods* → 25 % *dropping leaves* | 08-03 (214,7) | — | 09-11 (254,1) | 39 días | 0,74 en agosto |

Para referencia, el 50 % de floración de la soja (*blooming*) cae el 07-17 en MI y el 07-20 en KY. El maíz llega al
50 % de *dough* el 08-14 en MI y el 08-06 en KY, y al 50 % de *dented* el 09-03 y el 08-19.

- **MI** florece en el día 204 (50 %). Es como OH (203) y MN (202) y una semana antes que ND (208). Julio capta la
  floración tan bien como en el resto de los estados.
- **KY** florece en el día 191 (50 %), antes que IL (194), que es el más temprano de los 7 estados. Su ventana dura
  22 días, más que KS (20), y empieza el 1 de julio. Con un año un poco adelantado, como 2012, parte de la floración
  caería en junio. Esto es una inferencia mía: no lo calculé año por año. La soja de KY es la que peor cae en agosto
  (0,74), parecido a KS (0,64) e IL (0,67), porque termina tarde por la soja de segunda.

Nota sobre `fechas_nd.md`: con esta convención, la fracción de julio de la floración de ND da **0,82** y no 0,75. La
de la soja sí coincide (0,87). Parece que T108 usó 212 como límite de julio en el maíz. No lo corregí porque está
fuera de esta tarea.

**Supuestos y límites**

- El promedio de 5 años es el que publica NASS en los reportes de 2026 (2021–2025). No calculé un promedio propio. El
  hueco de octubre y noviembre de 2025, cuando no hubo reportes por el cierre del gobierno, puede afectar el promedio
  de cosecha. No verifiqué cómo lo trató NASS.
- Usé 31 reportes de 2026, de la semana 14 a la 45. Falta la semana 38 (`prog3826`), que no aparece en el listado de
  ESMIS, igual que en T108. En esas dos semanas la interpolación es una recta.
- El Handbook 628 es de 2010 y no tiene una edición posterior. Las superficies de 2009 que trae (maíz: MI 2,09 M
  acres, KY 1,15 M) son algo menores que las actuales (MI unos 2,3 M, KY 1,37–1,6 M sembrados; `nass_mi_nd.md` y
  `nass_ky.md`).
- No miré los reportes estatales (*Michigan Crop Progress* y *Kentucky Crop Progress & Condition*). Podrían traer
  trigo de invierno en KY, avena en MI y cortes de heno, pero no lo verifiqué.
- Los scripts anteriores que leen Crop Progress por estado (`nass_ky_crop_progress.py`, `nass_mi_nd_crop_progress.py`
  y otros) podrían tener el mismo error que corregí acá. No los revisé. Sus conclusiones sobre en qué tablas está
  cada estado coinciden con lo de acá (KY no está en trigo de invierno y MI no está en avena).
  Revisado en T116: los tres `nass_*_crop_progress.py` no tienen el error (cierran la tabla en cualquier título
  "- Selected States"); `ventanas_por_estado.py` sí lo tenía, pero sin efecto en sus 7 estados (ver
  `ventanas_por_estado.md`).

Fuentes:
- [USDA NASS, Field Crops Usual Planting and Harvesting Dates, Agricultural Handbook 628 (octubre de 2010), págs. 39 y 40](https://downloads.usda.library.cornell.edu/usda-esmis/files/vm40xr56k/dv13zw65p/w9505297d/planting-10-29-2010.pdf), consultado 2026-11-15
- [USDA NASS, Crop Progress (reportes semanales de 2026, archivo ESMIS)](https://esmis.nal.usda.gov/publication/crop-progress), consultado 2026-11-15
- `docs/research/fechas_nd.md`, `ventanas_por_estado.md`, `nass_ky.md`, `nass_mi_nd.md` y `propuesta_cultivos.md`
  (rama de T103) en este repo, para comparar y para los códigos nuevos

Confianza: alta en las filas del Handbook, copiadas de las págs. 39 y 40. Alta en los cruces de Crop Progress, que
son una interpolación directa del promedio publicado y salen de tablas en las que se verificó que el estado figura.
Media en las comparaciones de cosecha, por el hueco de 2025 y la semana 38 que falta.

Impacto: `config/cultivos_estado.csv` (11 filas propuestas, más 4 con códigos de T103, sin aplicar),
`config/cultivos.csv` y `config/config.yaml` (solo a través de T103), `docs/research/cultivos_fuentes.csv` (las citas,
al aplicar) y las ventanas de `clima_anual.csv` si MI o KY entran al proyecto. `docs/research/fechas_nd_cp.py`
cambió: ahora acepta el estado y corrige la lectura de tablas en las que el estado no figura. La salida de ND no
cambia.
