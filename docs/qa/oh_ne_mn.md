# Control de calidad: OH, NE y MN (release `datos-oh-ne-mn`)

Tarea T073 (parte de T007, sin Kansas). Fecha: 2026-11-15. Máquina: pro-1.

Se bajaron los 8 zips del release `datos-oh-ne-mn` y sus `.sha256` con `curl -L` a `data/entregas/` (fuera de
git). Los números de este informe salen de `docs/qa/oh_ne_mn_qa.py` (solo lee):

```bash
.venv/bin/python -X utf8 scripts/verificar_entrega.py data/entregas/datos-oh-ne-mn/*.zip --salida data/entregas/informes-oh-ne-mn
# descomprimir cada zip en data/entregas/oh-ne-mn-ext/<nombre del zip sin .zip>/
.venv/bin/python -X utf8 docs/qa/oh_ne_mn_qa.py data/entregas/oh-ne-mn-ext [data/entregas/nass_qa/qs.crops_<fecha>.txt.gz]
```

## Resultado por paquete

| paquete | `verificar_entrega.py` | QA de contenido | Veredicto |
|---|---|---|---|
| `agua` | APTO | señales de 2021 (MN) y 2022 (NE) en `sm_rootzone_anom_z`; sin problemas | **APTO** |
| `clima` | APTO | eventos visibles; sin outliers entre vecinos; rangos dentro del spec | **APTO** (con una nota sobre heladas) |
| `cultivos` | APTO | ver problemas 1 y 2 | **APTO con observaciones** |
| `economia` | APTO | no se controló el contenido (no hay referencia en las fuentes de la tarea) | **APTO** (solo formato) |
| `nldas` | APTO | `sm_0_100cm_anom_z` reproduce 2002, 2012, 2021 y 2022 | **APTO** |
| `paisaje` | APTO | no se controló el contenido | **APTO** (solo formato) |
| `suelo_terreno` | APTO | 268 condados (88 + 93 + 87), 1 fila por condado | **APTO** (solo formato) |
| `vegetacion` | APTO | eventos visibles; más faltantes en `ndvi_maiz` / `ndvi_soja` que IA/IL/IN (problema 3) | **APTO con observaciones** |

Ningún paquete es NO APTO: no apareció nada que esté mal calculado. Los problemas de abajo son de cobertura de
la fuente (NASS por condado) y de documentación.

## 1. `verificar_entrega.py`

- Los 8 `.sha256` coinciden (`sha256sum -c`). **Ojo:** los `.sha256` del release tienen fin de línea CRLF
  (se armaron en Windows) y `sha256sum -c` los rechaza tal cual ("No such file or directory" por el `\r`); hay que
  quitar el `\r` (`tr -d '\r'`). `verificar_entrega.py` sí los lee bien (usa `split()`).
- 8 APTO, 0 NO APTO, sin problemas ni avisos.
- `condados.csv` del zip: 268 condados (OH 88, NE 93, MN 87), el total esperado.

## 2. Eventos extremos

Medias de condado por estado (tablas completas: salida del script). Fuentes de lo esperado:
`docs/research/eventos_extremos.md` y `docs/research/eventos_extremos_nuevos.md`.

| Evento | Esperado | Se ve | ¿OK? |
|---|---|---|---|
| 2002, sequía en OH | `spi3` jul–ago < 0, `prec_jul_mm` bajo, maíz ≈ 88 bu/ac, soja ≈ 30 | `spi3` ago −1,81; `prec_jul_mm` 61 mm; `ndvi_anom_z` jul–ago −1,78; maíz 89,0 bu/ac (138,0 en 2001); soja 32,0 (41,0) | sí |
| 2002, sequía en NE | idem | `spi3` −1,18; `prec_jul_mm` 35 mm; `ndvi_anom_z` −1,92; maíz 128 (147 en 2001) | sí |
| 2012, sequía (los 3) | todo negativo; NE el peor; OH ≈ 126 bu/ac | `spi3` ago MN −1,26 / NE −2,48 / OH −1,44; NLDAS `sm_0_100cm_anom_z` −1,76 / −2,16 / −1,98; `ndvi_anom_z` −0,66 / −2,12 / −0,77; maíz NE −14 %, OH −21 % (120,4 bu/ac) contra los 5 años previos; MN +1,4 % | sí (MN casi no perdió rendimiento en 2012, coherente con NASS: 165 bu/ac) |
| 2019, inundación de marzo en NE | lluvia de marzo alta | `prec_power_mm` de marzo 73 mm (34–50 en 2018 y 2020) | sí |
| 2019, siembra prevenida en OH | superficie sembrada de maíz baja | suma de condados 2,43 M ac (3,26 M en 2018, 3,53 M en 2020); maíz −4 % | sí |
| 2021, sequía en MN | `spi3` jul–ago < 0, `ndvi_anom_z` < 0, maíz ≈ 178 | `spi3` −1,00; NLDAS −2,10; SMAP `sm_rootzone_anom_z` −1,49; `prec_jul_mm` 57; may+jun 109 mm (el más seco de la tabla); `ndvi_anom_z` −0,22; maíz 176,4 (−5,8 %) | sí (NDVI débil a nivel estado, como dice research: el daño fue en el norte) |
| 2022, sequía de verano en NE | negativo | `spi3` −1,43; NLDAS −1,55; SMAP −1,27; maíz −11 %, soja −18 % | sí |
| 2011, calor de julio | `tmin_c` de jul alto | `tmin_c` jul 2011 > 2010 en los tres (MN 18,0 / NE 20,8 / OH 19,7); 2012 aún más alto | sí |
| 2013, primavera húmeda en MN | lluvia may–jun alta | may+jun 259 mm, el más alto de MN en la tabla | sí |
| 2004, helada temprana del 20–21 de agosto en el norte de MN | `doy_primera_helada` en agosto en el norte | **no se ve**: todos los condados de MN tienen 275–276 (1–2 de octubre). POWER da `tmin_c` mínima de 2,4–2,9 °C el 20-8-2004 en Kittson, Koochiching y St. Louis | **esperable** (ver nota) |

Nota sobre 2004: no es un error del proceso. La celda de POWER (0,5°) promedia la helada de los bajos y queda
por encima de 0 °C; `eventos_extremos_nuevos.md` ya advierte que puede no verse. Se deja anotado para el data
card de `clima` (limitación de `doy_primera_helada` con POWER).

## 3. Rangos

Contra `docs/research/rangos_estados_nuevos.md`:

| cultivo | OH (mín–máx bu/ac) | NE | MN |
|---|---|---|---|
| maíz | 43,5–222,1 | 32,5–240,5 | 49,0–226,7 |
| soja | 19,4–66,9 | 15,0–75,5 | 7,0–67,4 |
| trigo de invierno | 23,6–110,6 | 8,7–85,0 | 23,0–67,0 |
| avena | 38,4–107,9 | **5,0**–106,0 | 25,0–126,0 |

- Maíz y soja quedan dentro del rango actual de `validar_csv()` (20–300 y 5–100). Soja de MN llega a 7,0, cerca
  del mínimo de 5: se refuerza la propuesta de research de bajarlo a 2.
- Avena de NE llega a 5,0 bu/ac y trigo de invierno de NE a 8,7: por debajo de los rangos que propone research
  (avena 10–200, trigo 5–130). **Si se aprueba esa propuesta tal cual, la avena de NE no pasaría.** Conviene
  avena desde 5 (ver "Para decidir").
- Clima diario: `tmin_c` mín −45,5 °C (Lake of the Woods, 30-1-2019), `tmax_c` máx 46,4 °C (Dundy NE,
  27-6-2012), `prec_power_mm` máx 113 mm/día, `prec_imerg_mm` máx 153 mm/día. Todo dentro del spec.
- Mensual: lluvia ≤ 403 mm, `gdd_10_30` ≤ 516, `tmin_c` ≥ −27,6. Dentro del spec.
- Lluvia anual IMERG / POWER (mediana por condado-año): MN 1,07, NE 1,07, **OH 1,18**. OH tiene un sesgo mayor
  entre las dos fuentes; no es un error, pero conviene anotarlo en el data card de `clima`.

## 4. Outliers por condado (contra sus 6 vecinos más cercanos)

Puntaje robusto: (valor − mediana de los vecinos) / max(1,48 × MAD, 10 % de la mediana).

- `prec_temporada_mm` y `gdd_temporada` (|z| > 4): **ninguno**. Ningún condado tiene una lluvia media
  2000–2025 a más de 25 % de la de sus vecinos.
- Rendimiento de maíz (|z| > 5): 11 condado-años, 7 de ellos de **Boyd, NE (31015)** (58–91 bu/ac contra
  164–199 de sus vecinos). Rendimiento de soja: 4 de 6 son de Boyd (17–18 bu/ac contra 46–54). Los demás:
  Kimball NE 2017, Lincoln NE 2021, Dawes NE 2013, Banner NE 2000 (maíz); Deuel NE 2020 y Athens OH 2018 (soja).
- Lectura: Boyd es casi todo secano y está en el borde norte del estado (sus vecinos más cercanos dentro del
  release son condados de NE con mucho riego, y los de Dakota del Sur no están). El resto son condados del
  oeste de NE donde el rendimiento de `ALL PRODUCTION PRACTICES` depende de la mezcla riego/secano de ese año.
  Es el problema de mezcla de riego ya conocido (`docs/research/riego_ne_ks.md`, tarea T004), no un error de
  proceso. No se abre tarea nueva.

## 5. Faltantes por estado contra IA/IL/IN

Solo las columnas donde algún estado nuevo supera en más de 15 puntos al `faltantes_pct` del data card de
`main` (IA/IL/IN). En todas las demás columnas de los 8 paquetes la diferencia es menor.

| archivo | columna | IA/IL/IN % | OH % | NE % | MN % |
|---|---|---|---|---|---|
| practicas_censo.csv | pct_drenaje_tile | 34,2 | 33,3 | **62,0** | 38,3 |
| fenologia_anual.csv | ndvi_max_maiz | 38,5 | **66,4** | 40,2 | 51,6 |
| fenologia_anual.csv | ndvi_max_soja | 38,6 | **59,7** | **60,1** | 52,5 |
| vegetacion_16d.csv | ndvi_maiz | 43,4 | **70,0** | 43,9 | **61,8** |
| vegetacion_16d.csv | ndvi_soja | 43,7 | **63,2** | **63,2** | **63,2** |
| vegetacion_mensual.csv | ndvi_maiz | 40,7 | **68,2** | 42,7 | 59,7 |
| vegetacion_mensual.csv | ndvi_soja | 41,0 | 61,6 | 62,1 | 61,0 |

- `pct_drenaje_tile` en NE: el drenaje con caños casi no existe en NE y el Censo no publica el dato en muchos
  condados. Esperable.
- `ndvi_maiz` / `ndvi_soja`: 2000–2007 faltan siempre (no hay CDL nacional; 8 de 26 años ≈ 31 %). De 2008 en
  adelante la cobertura por año es: OH maíz 30–49 %, MN maíz 47–69 %, NE maíz 73–88 %; soja 41–66 % en los tres.
  Con el umbral de 75 % del píxel de 250 m, los lotes chicos de OH y la soja en todo el oeste quedan con pocos
  píxeles puros. Es una consecuencia del umbral documentado, no un error; pero el modelo va a tener mucho menos
  `ndvi_maiz` en OH que en IA. Ver problema 3.

## 6. Superficie sembrada: suma de condados contra NASS a nivel estado

(Se completa abajo con la base completa de Quick Stats.)

## Problemas

1. **Cobertura de condados de NASS que baja en los últimos años, sobre todo en NE.** Condados con
   `sup_sembrada_ac` de maíz: NE 91 (2000) → 55 (2021) → 46 (2025); soja de NE: 79 → 36 (2025). MN maíz: 58 en
   2018 y 60 en 2019 (contra 71–77 los otros años). La suma de condados de maíz de NE en 2021 es 5,9 M ac
   (9,9 M en 2020). Es NASS el que no publica esos condados (los junta en "OTHER (COMBINED) COUNTIES", que el
   proceso deja afuera como pide CLAUDE.md), no el proceso. Consecuencia: cualquier total o promedio por estado
   hecho con los condados (rendimiento implícito, superficie) está sesgado en esos años, y `rotacion_anual.csv`
   (CDL) es la referencia de superficie. → tarea nueva para documentarlo en el data card de `cultivos` con la
   tabla de condados por año.
2. **Avena de NE con 5 bu/ac y trigo de invierno de NE con 8,7** quedan fuera de los rangos que propone
   `rangos_estados_nuevos.md`. → anotado en "Para decidir" (no es código).
3. **`ndvi_maiz` / `ndvi_soja` con muchos más faltantes en OH (y soja en los tres)** que en IA/IL/IN. → tarea
   nueva para que el data card de `vegetacion` muestre la cobertura por estado y año, y para evaluar con el
   humano si conviene un umbral más bajo (por ejemplo 50 %) solo como columna aparte.
4. **`.sha256` con CRLF** en el release: `sha256sum -c` falla en Linux. → tarea nueva chica para
   `scripts/entregar.py` (escribir el `.sha256` con `\n`).
5. **`doy_primera_helada` no ve la helada del 20-8-2004 en el norte de MN** (límite de la celda de POWER). → nota
   para el data card de `clima`, en la misma tarea de documentación que el punto 1.
