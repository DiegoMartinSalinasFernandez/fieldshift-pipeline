# Comparar OH/NE/MN con IA/IL/IN: qué cambia para el modelo

Pregunta: ¿Qué cambia entre la primera tanda (IA, IL, IN) y la segunda (OH, NE, MN) en rendimiento, lluvia de
temporada, GDD, riego, fechas de siembra, suelos y proporción de maíz tras maíz? Una tabla por variable con
mediana y percentiles 10 y 90 por grupo. Solo describir: sin modelos ni tendencias.

Respuesta corta: **OH/NE/MN quedan completos; IA/IL/IN, solo en parte.** El release `datos-oh-ne-mn` alcanza para
todas las tablas del grupo nuevo. Para IA/IL/IN **no hay un release publicado** (el único release del repo es
`datos-oh-ne-mn`) y los data cards (`docs/datasets/*.md`, `merge.md`) solo traen cobertura y % de faltantes, no
distribuciones. Por eso, en IA/IL/IN, solo se pueden comparar con datos reales el **rendimiento del Censo** (2012,
2017, 2022) y la **fecha de floración** (Crop Progress, 2008–2025), que ya están en `docs/research/`. El resto de
las columnas de IA/IL/IN queda vacío hasta que se publique `datos-ia-il-in`; el script ya las llena si se le pasa
esa carpeta.

Lo que más le importa a ML:
1. **Nebraska es otro sistema productivo.** Riego mediano de 33–35 % de la tierra de cultivo por condado (p90:
   69–74 %), contra ~0–2 % en OH y MN. Además tiene el mayor déficit de temporada (mediana −427 mm contra −101 en
   OH) y la mayor proporción de maíz tras maíz (mediana 44 % contra 14 % en OH). Con riego, lluvia baja no implica
   rendimiento bajo: la relación clima → rendimiento aprendida en Iowa no se traslada.
2. **Minnesota es más fresco.** GDD de temporada con mediana 1.459 °C·día (p10: 1.206), unos 280 menos que OH y
   400 menos que NE, y 158 días libres de heladas. Además tiene suelos con mucha más materia orgánica (mediana
   8,5 %, p90 20 %: condados con turba). Estos valores caen fuera de lo visto en IA/IL/IN: el punto de Story (IA)
   va de 1.499 a 1.956 °C·día entre 2000 y 2025.
3. **El rendimiento del grupo nuevo es más bajo en años normales y menos golpeado en 2012.** En el Censo, la
   mediana de condado de maíz en 2017 y 2022 fue de 180–202 bu/ac en IA/IL/IN y de 163–188 en OH/NE/MN. En 2012
   fue al revés: 92–128 en IA/IL/IN contra 123–149 en OH/NE/MN.
4. **Ohio rota distinto:** tiene más soja tras soja (mediana 31 %) que maíz tras maíz (14 %), más trigo (4 % del
   área agrícola) y suelos más ácidos (pH 6,0) y menos drenados (28 de 88 condados "somewhat poorly drained").
5. **Las fechas de floración casi no cambian entre grupos** (maíz: mediana del día 198 contra 201; soja: 196
   contra 198). Ohio siembra más tarde y con más variación (maíz: mediana del día 134, p90 146).

## Cómo se calculó

- Script: `docs/research/comparar_grupos.py`. Uso:
  `python docs/research/comparar_grupos.py <carpeta_release_oh_ne_mn> [<carpeta_release_ia_il_in>]`.
- Datos: zips `datos-oh-ne-mn_{cultivos,clima,suelo_terreno}.zip` del release `datos-oh-ne-mn`, bajados con
  `curl -L` el 2026-11-15 a `data/releases/` (fuera de git). Los tres `.sha256` coinciden.
- Para IA/IL/IN, sin release, se usan `docs/research/rangos_estados_nuevos_censo.csv` (rendimiento implícito del
  Censo = producción / superficie cosechada, condados con ≥ 500 ac) y `docs/research/ventanas_por_estado.csv`
  (día del 50 % de floración, Crop Progress).
- Unidades: condado-año (clima, rendimiento, rotación), condado-censo (riego), estado-año (fenología) y condado
  (suelo). **Sin ponderar por superficie**: un condado de Nebraska occidental con poco maíz pesa lo mismo que uno
  del Des Moines Lobe. Percentiles con `pandas.quantile` (interpolación lineal). Se descartan las celdas vacías.

## Tablas

`n` = cantidad de observaciones con dato. "—" = sin datos de ese grupo en el repo.

### Rendimiento de maíz (`rend_bu_ac`, encuesta NASS, todas las prácticas)

| Grupo / estado | Período | n | p10 | mediana | p90 |
|---|---|---|---|---|---|
| **IA/IL/IN** | 2000–2025 | — | — | — | — |
| **OH/NE/MN** | 2000–2025 | 5.987 | 115,0 | 160,0 | 195,0 |
| OH | 2000–2025 | 2.051 | 114,6 | 155,2 | 187,6 |
| NE | 2000–2025 | 2.069 | 117,4 | 163,2 | 199,0 |
| MN | 2000–2025 | 1.867 | 113,7 | 163,0 | 197,2 |

### Rendimiento de soja (`rend_bu_ac`, encuesta NASS, todas las prácticas)

| Grupo / estado | Período | n | p10 | mediana | p90 |
|---|---|---|---|---|---|
| **IA/IL/IN** | 2000–2025 | — | — | — | — |
| **OH/NE/MN** | 2000–2025 | 5.548 | 33,6 | 47,8 | 59,0 |
| OH | 2000–2025 | 1.952 | 35,6 | 47,8 | 56,4 |
| NE | 2000–2025 | 1.732 | 38,3 | 52,0 | 63,6 |
| MN | 2000–2025 | 1.864 | 30,0 | 43,0 | 55,7 |

### Rendimiento del Censo, comparable entre grupos (mediana de condados, mín.–máx., bu/ac)

La única fuente de rendimiento por condado de IA/IL/IN en el repo. No es la encuesta que va en
`produccion_anual.csv`: el Censo cuenta todas las explotaciones. Sirve para comparar los dos grupos entre sí.

| Cultivo | Estado | 2012 | 2017 | 2022 |
|---|---|---|---|---|
| maíz | IA | 128,2 (42,2–173,4) | 199,4 (113,8–222,1) | 199,8 (116,1–226,8) |
| maíz | IL | 95,9 (21,1–167,1) | 192,2 (116,2–236,5) | 202,1 (139,0–233,3) |
| maíz | IN | 92,3 (35,4–166,9) | 179,7 (141,2–206,4) | 191,3 (146,1–215,7) |
| maíz | OH | 122,9 (66,3–158,9) | 167,6 (109,2–200,1) | 177,2 (120,0–204,0) |
| maíz | NE | 130,7 (60,6–193,7) | 178,6 (82,5–226,1) | 162,7 (53,6–220,0) |
| maíz | MN | 149,1 (90,0–184,7) | 187,5 (118,3–217,6) | 178,4 (91,4–220,2) |
| soja | IA | 43,9 (23,5–54,9) | 55,3 (36,8–63,8) | 58,0 (35,4–68,1) |
| soja | IL | 41,0 (22,5–55,5) | 55,8 (33,9–67,7) | 60,5 (42,1–69,9) |
| soja | IN | 40,2 (26,5–59,4) | 52,3 (43,4–62,7) | 56,9 (42,2–64,9) |
| soja | OH | 43,3 (30,4–54,1) | 48,3 (33,2–55,9) | 52,0 (30,2–60,5) |
| soja | NE | 40,9 (20,5–60,8) | 55,7 (37,0–66,5) | 48,5 (26,3–65,2) |
| soja | MN | 41,1 (17,8–54,3) | 46,9 (25,3–58,2) | 46,7 (23,1–63,1) |

Como control de que Censo y encuesta dan órdenes de magnitud parecidos: en OH/NE/MN, la encuesta en 2012, 2017 y
2022 da una mediana de 168,4 bu/ac de maíz (p10 114,6, p90 200,8) y 48,6 de soja (36,1–59,5).

### Lluvia de temporada, abril–septiembre (`prec_temporada_mm`, POWER, 2000–2025)

| Grupo / estado | n | p10 | mediana | p90 |
|---|---|---|---|---|
| **IA/IL/IN** | — | — | — | — |
| **OH/NE/MN** | 6.968 | 364 | 514 | 676 |
| OH | 2.288 | 455 | 539 | 668 |
| NE | 2.418 | 303 | 477 | 653 |
| MN | 2.262 | 386 | 509 | 706 |

Referencia en IA (un solo punto, no media de condado, `rangos_estados_nuevos_power.csv`): en Story, IA, de 370 mm
(2012) a 1.003 mm (2010).

### GDD 10/30 de temporada (`gdd_temporada`, °C·día, 2000–2025)

| Grupo / estado | n | p10 | mediana | p90 |
|---|---|---|---|---|
| **IA/IL/IN** | — | — | — | — |
| **OH/NE/MN** | 6.968 | 1.359 | 1.701 | 1.953 |
| OH | 2.288 | 1.552 | 1.738 | 1.922 |
| NE | 2.418 | 1.646 | 1.843 | 2.025 |
| MN | 2.262 | 1.206 | 1.459 | 1.666 |

Referencia en IA (un punto): Story, de 1.499 (2009) a 1.956 (2012).

### Déficit de temporada, lluvia − ETo (`deficit_temporada_mm`) y período libre de heladas

| Grupo / estado | déficit p10 | déficit mediana | déficit p90 | libre de heladas p10 | mediana | p90 (días) |
|---|---|---|---|---|---|---|
| **IA/IL/IN** | — | — | — | — | — | — |
| **OH/NE/MN** | −568 | −192 | 30 | 147 | 172 | 201 |
| OH | −230 | −101 | 70 | 163 | 184 | 210 |
| NE | −750 | −427 | −128 | 156 | 177 | 201 |
| MN | −394 | −168 | 93 | 139 | 158 | 180 |

### Riego (`pct_riego`, % de la tierra de cultivo regada, Censo)

| Grupo / estado | Censo | n | p10 | mediana | p90 |
|---|---|---|---|---|---|
| **IA/IL/IN** | 2012–2022 | — | — | — | — |
| **OH/NE/MN** | 2012 | 252 | 0,1 | 1,8 | 53,2 |
| OH | 2012 | 85 | 0,0 | 0,2 | 1,5 |
| NE | 2012 | 93 | 7,9 | 35,3 | 73,7 |
| MN | 2012 | 74 | 0,0 | 1,0 | 9,3 |
| **OH/NE/MN** | 2017 | 250 | 0,1 | 2,2 | 51,2 |
| OH | 2017 | 83 | 0,1 | 0,3 | 1,3 |
| NE | 2017 | 93 | 8,6 | 35,2 | 73,4 |
| MN | 2017 | 74 | 0,1 | 1,4 | 12,5 |
| **OH/NE/MN** | 2022 | 255 | 0,2 | 2,3 | 48,8 |
| OH | 2022 | 86 | 0,1 | 0,5 | 2,0 |
| NE | 2022 | 93 | 7,6 | 33,3 | 68,7 |
| MN | 2022 | 76 | 0,1 | 1,2 | 13,3 |

IA/IL/IN: no hay `pct_riego` en el repo. La única pista es la fracción de maíz regado de los condados extremos del
Censo (`rangos_estados_nuevos_censo.csv`): de 0 a 18 % (Tazewell, IL, 2022). `riego_nass.md` da para NE una
mediana de 64–66 % del **maíz** sembrado con riego (2000–2018), más que el 33–35 % de la tierra de cultivo de
arriba porque el riego se concentra en el maíz y la soja.

### Drenaje con caños (`pct_drenaje_tile`, Censo 2017 y 2022)

| Grupo / estado | n | p10 | mediana | p90 |
|---|---|---|---|---|
| **IA/IL/IN** | — | — | — | — |
| **OH/NE/MN** | 443 | 0,7 | 15,7 | 69,0 |
| OH | 176 | 5,4 | 38,6 | 68,8 |
| NE | 106 | 0,2 | 1,7 | 14,5 |
| MN | 161 | 1,9 | 25,1 | 73,2 |

IA/IL/IN, solo por estado (`drenaje_tile.md`, Censo 2017): IA 5,71 Mha drenadas, IL 3,83, IN 2,57; OH 2,18, MN
3,27, NE 0,22.

### Fechas de siembra (`doy_50_sembrado`, día del año, estado-año 2000–2025)

| Grupo / estado | maíz p10 | maíz mediana | maíz p90 | soja p10 | soja mediana | soja p90 |
|---|---|---|---|---|---|---|
| **IA/IL/IN** | — | — | — | — | — | — |
| **OH/NE/MN** (n = 78) | 119,5 | 127,6 | 139,1 | 129,8 | 139,8 | 147,7 |
| OH | 119,2 | 133,7 | 145,6 | 131,8 | 142,6 | 152,4 |
| NE | 122,2 | 125,3 | 131,7 | 130,4 | 137,3 | 143,2 |
| MN | 118,2 | 123,2 | 136,7 | 128,1 | 139,1 | 147,6 |

Cosecha (50 %), OH/NE/MN: maíz mediana del día 297,5 (p10 288,9, p90 308,8); soja 283,4 (276,0–291,7).

### Floración (día del 50 %, `ventanas_por_estado.csv`, estado-año 2008–2025): la única fecha con los dos grupos

| Grupo / estado | maíz silking p10 | mediana | p90 | soja blooming p10 | mediana | p90 |
|---|---|---|---|---|---|---|
| **IA/IL/IN** (n = 54) | 189,7 | 197,8 | 205,8 | 191,2 | 196,1 | 206,3 |
| IA | 194,8 | 198,4 | 206,1 | 190,2 | 195,3 | 201,5 |
| IL | 185,4 | 193,8 | 202,6 | 191,7 | 195,5 | 207,8 |
| IN | 189,3 | 199,7 | 205,2 | 192,4 | 197,7 | 207,0 |
| **OH/NE/MN** (n = 54) | 194,3 | 200,7 | 207,8 | 189,2 | 197,8 | 203,3 |
| OH | 193,3 | 202,9 | 208,7 | 194,2 | 199,8 | 206,0 |
| NE | 195,3 | 198,1 | 202,3 | 188,9 | 195,8 | 201,4 |
| MN | 197,2 | 202,2 | 208,1 | 188,9 | 197,2 | 203,1 |

`fenologia_estado.csv` de OH/NE/MN da lo mismo para 2000–2025 (maíz: mediana 200,6; soja: 196,9). Las ventanas
fijas de julio (floración del maíz) y agosto (llenado de la soja) siguen sirviendo en los dos grupos.

### Suelo y terreno (`suelo_terreno_estatico.csv`, por condado)

| Variable | IA/IL/IN | OH/NE/MN p10 | mediana | p90 | OH mediana | NE mediana | MN mediana |
|---|---|---|---|---|---|---|---|
| `aws0_150_mm` | — | 154 | 225 | 283 | 182 | 259 | 255 |
| `nccpi_maiz` | — | 0,216 | 0,522 | 0,702 | 0,596 | 0,447 | 0,515 |
| `nccpi_soja` | — | 0,219 | 0,529 | 0,667 | 0,496 | 0,545 | 0,545 |
| `soc0_30_gm2` | — | 3.201 | 5.600 | 10.780 | 5.466 | 4.305 | 10.108 |
| `materia_organica_pct` | — | 1,5 | 2,6 | 11,2 | 2,6 | 1,8 | 8,5 |
| `arcilla_pct` | — | 9,6 | 23,2 | 29,8 | 24,3 | 22,4 | 22,0 |
| `arena_pct` | — | 14,4 | 26,4 | 63,2 | 22,3 | 27,1 | 35,5 |
| `ph_agua` | — | 5,60 | 6,50 | 7,20 | 5,96 | 6,85 | 6,64 |
| `pendiente_media_pct` | — | 1,63 | 2,94 | 7,44 | 3,48 | 3,46 | 2,27 |
| `twi_medio` | — | 8,67 | 9,46 | 10,05 | 9,34 | 9,29 | 9,72 |
| `elevacion_media_m` | — | 257 | 347 | 798 | 283 | 619 | 342 |

p10 y p90 por estado: en la salida del script. Lo que más se sale: arena en NE (p90 87,6 %: Sandhills), materia
orgánica en MN (p90 20,4 %) y pendiente en OH (p90 11,2 %: sureste, Apalaches).

Clase de drenaje dominante (cantidad de condados):

| Estado | Excesivo | Bien drenado | Moderadamente bien | Algo pobre | Pobre | Muy pobre |
|---|---|---|---|---|---|---|
| OH | 0 | 43 | 6 | 28 | 1 | 10 |
| NE | 18 | 67 | 7 | 1 | 0 | 0 |
| MN | 1 | 32 | 5 | 6 | 32 | 11 |

### Maíz tras maíz (`pct_maiz_tras_maiz`, % del maíz con maíz el año anterior, CDL 2009–2025)

| Grupo / estado | n | p10 | mediana | p90 |
|---|---|---|---|---|
| **IA/IL/IN** | — | — | — | — |
| **OH/NE/MN** | 4.532 | 7,9 | 26,9 | 61,0 |
| OH | 1.496 | 6,1 | 14,1 | 40,4 |
| NE | 1.581 | 15,7 | 44,3 | 71,7 |
| MN | 1.455 | 10,0 | 25,7 | 49,4 |

Complemento: soja tras soja, OH/NE/MN: mediana 12,1 % (p10 2,1, p90 41,3); OH 31,0, NE 4,2, MN 11,5. Maíz
como % del área agrícola: OH 35,3, NE 53,1, MN 47,0 (p10 de MN 6,2: el norte casi no tiene maíz). Trigo: OH 4,0,
NE 0,8 (p90 21,7: oeste), MN 0,0.

## Qué implica para el modelo (descripción, no recomendación de método)

- **Rango del target.** El p10–p90 de maíz de OH/NE/MN (115–195 bu/ac) y el del Censo de IA/IL/IN en años normales
  se solapan, pero las colas no: IA/IL/IN tiene medianas más altas en 2017 y 2022 y el peor 2012. Un modelo
  entrenado en un grupo extrapola en el otro tanto en el promedio como en los años extremos.
- **Riego.** En NE, `rend_bu_ac` mezcla riego y secano (CLAUDE.md, §2). La lluvia y el déficit de temporada
  explican menos en los condados regados. `pct_riego` existe solo para años de censo, y la serie por práctica de
  NASS se corta en 2018 (`riego_nass.md`).
- **Clima fuera del rango de entrenamiento.** El GDD de MN (p10 1.206) y el déficit de NE (p10 −750 mm) están por
  debajo de lo que muestra el punto de Story, IA (GDD mínimo 1.499; lluvia de temporada mínima 370 mm en 2012). Sin
  `clima_anual.csv` de IA/IL/IN no se puede decir cuántos condado-año del grupo nuevo quedan fuera del rango.
- **Rotación.** El maíz continuo es mucho más común en NE y la soja tras soja en OH. Si el modelo usa
  `pct_maiz_tras_maiz` como variable de rotación, el grupo nuevo amplía su rango hacia arriba (p90 72 % en NE).
- **Suelos.** Los suelos orgánicos de MN y arenosos de NE amplían los rangos de `materia_organica_pct`,
  `soc0_30_gm2` y `arena_pct`. El NCCPI de maíz de NE (mediana 0,45) es bajo justamente donde el riego compensa.

## Lo que no se hizo / no encontré

- **Distribuciones de IA/IL/IN** de rendimiento de encuesta, clima, riego, siembra, suelo y rotación: no hay
  release `datos-ia-il-in` ni CSV procesados en esta máquina, y los data cards no traen percentiles. Cuando se
  publique, correr `python docs/research/comparar_grupos.py <oh_ne_mn> <ia_il_in>` y completar las filas "—".
- Kansas (KS) no entra en la comparación: no está en `datos-oh-ne-mn`.
- No se ponderó por superficie sembrada ni se separaron períodos. Tampoco se calcularon tendencias (las pide la
  tarea así).

Fuentes:
- Release `datos-oh-ne-mn` de este repo (zips `cultivos`, `clima`, `suelo_terreno`, verificados con `.sha256`),
  consultado 2026-11-15
- `docs/research/rangos_estados_nuevos_censo.csv` y `rangos_estados_nuevos_power.csv` (Censo Agropecuario NASS
  2012, 2017, 2022 y NASA POWER), `docs/research/ventanas_por_estado.csv` (NASS Crop Progress),
  `docs/research/riego_nass.md`, `docs/research/drenaje_tile.md`, de este repo, consultados 2026-11-15

Confianza: **alta** para OH/NE/MN (cálculo directo sobre el release); **media** para la comparación de rendimiento
y floración con IA/IL/IN (Censo y Crop Progress reales, pero no los mismos CSV); **sin dato** para el resto de
IA/IL/IN.

Impacto: ninguno en `config/` ni en los paquetes. Lo usa el equipo de ML. Para completar la comparación hace falta
publicar el release de IA/IL/IN (`scripts/entregar.py` en la máquina que tiene esos datos).
