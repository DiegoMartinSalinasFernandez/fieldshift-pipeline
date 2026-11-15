# Índice de los research

Resumen de los documentos de `docs/research/`, agrupados por tema. Cada fila resume la pregunta y la respuesta
corta en una línea; el detalle, las fuentes y las citas están en cada archivo. La columna **Para decidir** enlaza
al número de la propuesta en [`coordinacion/para_decidir.md`](../../coordinacion/para_decidir.md) cuando el
documento dejó algo pendiente del humano.

Confianza: la que declara cada documento. Si da varias, se resume como "alta / media / baja" con lo principal
primero.

Armado el 2026-11-15 (tarea T037), sobre los 24 documentos `.md` que había. Este índice no cambia ningún documento: si uno se
actualiza, hay que actualizar su fila.

## Cultivos y fechas

| Archivo | Pregunta | Respuesta corta | Confianza | Impacta | Para decidir |
|---|---|---|---|---|---|
| [cultivos_zona.md](cultivos_zona.md) | Parámetros por cultivo para el Corn Belt (siembra, cosecha, Kc, GDD, raíces, N, rastrojo, tolerancias), incluidos los de cobertura | `config/cultivos.csv` quedó completo en parte: 194 celdas con cita (`cultivos_fuentes.csv`); fechas del Handbook 628, Kc de FAO-56. Quedan vacíos (período crítico de avena, alfalfa y heno; trébol; etc.) | media | `config/cultivos.csv`, ventanas por cultivo, ETc en `clima`/`agua`, GDD | Vacíos "para otra ronda o para el humano" (sin número en la lista) |
| [crop_progress_estados_nuevos.md](crop_progress_estados_nuevos.md) | Qué etapas de Crop Progress hay en OH, NE, MN y KS, desde cuándo y con qué huecos | Maíz y soja completos 2000–2026 en los 4 estados; trigo de invierno en OH, NE y KS; avena en OH, NE y MN. Hueco de oct–nov de 2025 (cierre del gobierno) | alta (cobertura) / media (días típicos) / baja (año del trigo de otoño) | `cultivos`: `fenologia_estado.csv` | [#8](../../coordinacion/para_decidir.md): avena, trigo (HEADED), año del trigo de otoño, marca de calidad |
| [sorgo.md](sorgo.md) | ¿Sumar el sorgo granífero a los cultivos? | En KS es grande (2,6–3,6 M ac/año); en NE chico y en el resto casi nada. NASS publica pocos condados después de 2017. Recomienda sumarlo solo como clase de rotación en KS | alta / media (bushel, rotaciones) | `config/`, `clases_cdl.csv`, `src/common/`, `cultivos` (todo pendiente) | [#11](../../coordinacion/para_decidir.md) |

Auxiliares: [cultivos_fuentes.csv](cultivos_fuentes.csv) (cita por celda de `config/cultivos.csv`),
[sorgo_conteo.py](sorgo_conteo.py).

## NASS y Censo

| Archivo | Pregunta | Respuesta corta | Confianza | Impacta | Para decidir |
|---|---|---|---|---|---|
| [nass_quickstats.md](nass_quickstats.md) | `short_desc` de rendimiento, superficie y producción; condados combinados, `(D)`; ¿hay 2024 y 2025? | `short_desc` = concatenación de 6 campos; rendimiento y sembrada verificados, el resto por regla. Filtrar `county_code` 998. Condado 2024 repuesto para maíz y soja; cereales finos desde 2025 | media (alta para 998, `(D)` y 2024–2025) | `cultivos`: `download.py`, `process.py`, `produccion_anual.csv` | — |
| [nass_2024_2025.md](nass_2024_2025.md) | Cobertura por condado 2020–2025 en los 7 estados (maíz, soja, trigo, avena), `(D)` y combinados | Hay datos hasta 2025. Trigo y avena de 2024 solo en IL. La cobertura cae: rendimiento de maíz en 92 % de los condados en 2020 y ~65–68 % en 2024–2025. El faltante es una fila ausente, no un `(D)` | alta (conteos) / media (causa) | `cultivos`: `produccion_anual.csv`, data card | [#7](../../coordinacion/para_decidir.md): grilla completa `fips × anio × cultivo` |
| [censo_agropecuario.md](censo_agropecuario.md) | `short_desc` del Censo para cobertura, labranza cero, tile y riego por condado (2012/2017/2022); y lo mismo para OH, NE, MN y KS | Los 4 `short_desc` existen por condado en 2017 y 2022; de 2012 solo riego (el resto, Tabla 41 en PDF). Sirven igual para los estados nuevos; tile vacío en ~45–50 % de los condados de NE y KS | alta / media (2012 por Tabla 41) | `cultivos`: `practicas_censo.csv` | [#2](../../coordinacion/para_decidir.md): `pct_maiz_regado`, `pct_soja_regada`, `pct_cosechado_regado` |
| [cdl_csb.md](cdl_csb.md) | Clases oficiales del CDL, descarga por estado, precisión y campos del CSB | Los códigos del CLAUDE.md coinciden con la tabla oficial (0 = sin dato). CropScape fue reemplazado por CroplandCROS (ImageServer sin login). CDL a 10 m desde 2024 | alta / media (CropScape) | `cultivos`: `clases_cdl.csv`, `download.py`, `rotacion_secuencia.csv` | Sugiere sumar 0, 27 (centeno) y 58 (trébol) a `clases_cdl.csv` (sin número) |
| [cdl_precision.md](cdl_precision.md) | Precisión del CDL por estado, año y cultivo (2008–2025) | Maíz y soja confiables (85,8–99,1 %); trigo malo en IA y MN; avena, alfalfa y otro heno ruidosos (otro heno 2024 muy sobreclasificado). Peores estados para maíz/soja: KS y OH | alta (valores) / baja (causa en KS) | data card de `cultivos`, `rotacion_anual.csv`, `rotacion_secuencia.csv` | [#13](../../coordinacion/para_decidir.md): `cdl_precision.csv` como referencia y `openpyxl` |

Auxiliares: [cdl_precision.csv](cdl_precision.csv), [cdl_precision_extraer.py](cdl_precision_extraer.py),
[nass_2024_2025_conteo.py](nass_2024_2025_conteo.py).

## Riego

| Archivo | Pregunta | Respuesta corta | Confianza | Impacta | Para decidir |
|---|---|---|---|---|---|
| [riego_nass.md](riego_nass.md) | Datos `IRRIGATED` / `NON-IRRIGATED` de NASS por condado en NE y KS | Maíz y soja 2000–2018 y trigo de invierno 2000–2019; después NASS dejó de publicarlos (RMA retiró la financiación). Sin `(D)`: lo oculto va a los combinados 998. Después de 2018, solo el Censo | alta / media (RMA) | `cultivos`: `produccion_anual.csv`, `practicas_censo.csv` | [#1](../../coordinacion/para_decidir.md): 11 columnas de riego y secano |
| [riego_mascaras.md](riego_mascaras.md) | Productos de área regada por píxel o condado en NE y KS | LANID-US: único anual, 30 m y nacional (1997–2017, 1,8 GB). AIM-HPA solo el acuífero (1984–2017). No hay serie abierta después de 2017 | alta (LANID, AIM-HPA) / media / baja (productos de NE) | `cultivos` (`riego_anual.csv`), `mascara_riego_max.tif`, `vegetacion` | [#9](../../coordinacion/para_decidir.md): bajar LANID |
| [riego_ne_ks.md](riego_ne_ks.md) | ¿Qué fuente usar para `frac_riego` anual por condado y cómo separar rendimiento de riego y secano? | LANID 30 m anual 1997–2017 (Zenodo) + 2018–2020 (USGS, nuevo): cubre los 7 estados. Censo, MIrAD y USGS Water Use (`IR-IrTot`, 1985–2015) son quinquenales. Rendimiento por práctica solo NASS hasta 2018/2019 | alta (LANID, USGS) / media / sin verificar (NASS fuera de NE y KS) | `cultivos` (`riego_anual.csv`, columnas en `produccion_anual.csv`) | `frac_riego_lanid` y columnas de riego/secano (sin número) |

Relacionados: [censo_agropecuario.md](censo_agropecuario.md) (riego por cultivo del Censo, propuesta #2) y
[efecto_rotacion.md](efecto_rotacion.md) (el efecto rotación con riego es menor).

## Suelo y drenaje

| Archivo | Pregunta | Respuesta corta | Confianza | Impacta | Para decidir |
|---|---|---|---|---|---|
| [gssurgo.md](gssurgo.md) | Columnas de `Valu1` y `muaggatt`; ¿geodatabase por estado o Soil Data Access? | `Valu1`: `aws0_100`, `aws0_150` (mm), `soc0_30`, `soc0_100`, `nccpi3corn/soy/all`, `rootznemc`. `muaggatt`: `drclassdcd`, `hydgrpdcd`, `wtdepannmin`; ojo, `aws0100wta` está en cm | alta (columnas) / media (recomendación) | `suelo_terreno`: `download.py`, `process.py`, data card | — |
| [drenaje_tile.md](drenaje_tile.md) | Mapas de drenaje con caños por píxel en los 7 estados | Hay 4 mapas de 30 m; 3 reparten el área del Censo (no observan). Solo SEETileDrain (Landsat, 2024) observa: ~3,1 GB | alta (métodos) / media (uso en `lotes`) | `lotes` (opcional) | [#5](../../coordinacion/para_decidir.md): sumar SEETileDrain |

## Productos de la NASA

| Archivo | Pregunta | Respuesta corta | Confianza | Impacta | Para decidir |
|---|---|---|---|---|---|
| [productos_nasa.md](productos_nasa.md) | Nombres exactos de SMAP L4, GRACE-DA-DM e IMERG en Earth Engine | SMAP `SPL4SMGP` v008 desde 2015-03-31 (`sm_surface`, `sm_rootzone`); GRACE-DA-DM EE.UU. `GRACEDADM_CLSM0125US_7D` (0,125°, desde 2002-04) mejor que la global; IMERG `GPM_3IMERGDF` V07 o `NASA/GPM_L3/IMERG_V07` en EE | alta / media (elección de GRACE EE.UU.) | `agua`, `clima` | — |

## Economía

| Archivo | Pregunta | Respuesta corta | Confianza | Impacta | Para decidir |
|---|---|---|---|---|---|
| [precios_margenes.md](precios_margenes.md) | Precios recibidos de NASS, costos y retornos del ERS, presupuestos de ISU o farmdoc | Precios por estado en Quick Stats (`PRICE RECEIVED`, año comercial y mensual); costos ERS por región; farmdoc 2025 por región de IL. Ag Decision Maker no se pudo leer | alta / media (región de IA, IL, IN) / baja (ISU) | paquete `economia` (entonces nuevo) | Propuesta en `loop/notes/decisiones.md`, que no está en este repo (ver Contradicciones) |
| [regiones_ers.md](regiones_ers.md) | ¿En qué región del ERS cae cada estado y condado? | IA, IL, IN: Heartland; KS: Prairie Gateway; OH, NE y MN se reparten en 3 regiones. Se pondera por área sembrada (implementado en T005) | alta (regiones) / media (ponderación) | `economia`: `process.py` | Costos por condado: cambia el esquema, lo decide el humano (sin número) |
| [presupuestos_estados_nuevos.md](presupuestos_estados_nuevos.md) | Presupuestos de OSU, UNL, UMN/FINBIN y K-State; ¿sirven frente al ERS? | Cada estado tiene fuente propia pero no son comparables (proyectados vs. reales, con o sin riego). Seguir solo con ERS y usar los presupuestos como referencia | alta / media / baja (UMN, KFMA) | `economia` (sin cambios) | Propuestas (a) tabla de riego en `docs/` y (b) FINBIN/KFMA (sin número) |

## Reglas de rotación (N, cobertura, carbono, agua, efecto rotación)

| Archivo | Pregunta | Respuesta corta | Confianza | Impacta | Para decidir |
|---|---|---|---|---|---|
| [efecto_rotacion.md](efecto_rotacion.md) | ¿Cuánto rinde menos el maíz tras maíz y la soja tras soja; cuánto suman trigo, avena o alfalfa? | Maíz rotado +9–15 % en ensayos y 4,3 % (secano) / 1,7 % (riego) en lotes comerciales; soja tras soja ≈ −10 %; con forrajes, maíz +6–8 % sobre maíz–soja. Mayor en ambientes secos | alta (signo) / media (valores) / baja (por estado) | reglas de la herramienta; `rotacion_anual.csv`, `rotacion_secuencia.csv` (sin cambios) | — |
| [nitrogeno.md](nitrogeno.md) | Dosis económica de N para maíz tras soja y tras maíz por estado; créditos de soja, alfalfa y cobertura | Estados MRTN (IL, IN, MN, OH; IA hasta 2024): la dosis ya incluye la soja, maíz/maíz ≈ +35–45 lb N/ac. NE y KS: fórmula con crédito de soja (−35 a −40 lb). IA pasó a N-FACT (sin valores) | alta (KS, IN, IL, MN, NE) / media (OH, IA) | `config/cultivos.csv` (crédito de N), regla de costo de N | Columna de crédito de N en `config/cultivos.csv` (sin número) |
| [cobertura_rendimiento.md](cobertura_rendimiento.md) | Efecto del centeno (y avena o trébol) de cobertura en el rendimiento siguiente, agua, erosión y nitrato | Maíz tras centeno 0 a −6 %, depende de la fecha de terminación; soja casi sin efecto; nitrato lixiviado baja en Iowa; en el oeste de KS el trigo pierde −19 % | media / alta (nitrato) / baja (norte–sur, semiárido) | reglas de ML (sección 8); ningún paquete | — |
| [carbono_erosion.md](carbono_erosion.md) | Factor C de RUSLE por rotación y labranza; tasa de cambio del carbono; rastrojo por cultivo | No hay tabla RUSLE2 publicada: se usa la de NRCS Missouri. Siembra directa +0,57 t C/ha/año, rotación más compleja +0,20 (global), pero los ensayos del Corn Belt no ven efecto de la rotación. Rastrojo de maíz confirmado | media / baja (C por rotación) / alta (rastrojo) | reglas de ML; `config/cultivos.csv` sin cambios | [#15](../../coordinacion/para_decidir.md) y [#16](../../coordinacion/para_decidir.md) |
| [agua_por_cultivo.md](agua_por_cultivo.md) | ET medida de cada cultivo en la zona, variación entre años, agua que deja al siguiente y comparación con Kc de FAO-56 | Maíz 482 mm (secano) / 548 mm (riego) en Mead, soja 431/452 mm; el maíz usa 11–18 % más. Los Kc de FAO-56 sobreestiman la ET medida ~15–45 %. Sin datos de heno | alta (mediciones) / media (sobreestimación) / baja (trigo, avena, heno) | `config/cultivos.csv`, regla de agua, `clima` | [#12](../../coordinacion/para_decidir.md): Kc medidos o factor de corrección |

## Riesgo (RMA, siembra prevenida, eventos extremos)

| Archivo | Pregunta | Respuesta corta | Confianza | Impacta | Para decidir |
|---|---|---|---|---|---|
| [rma_causa_perdida.md](rma_causa_perdida.md) | Dónde y cómo bajar Cause of Loss y Summary of Business del RMA por condado | `colsom_<año>.zip` 1989–2026 (causa, mes); `sobcov`/`sobtpu` como denominador (`sobtpu` separa riego). CC0, sin `(D)`. Normalizar con `loss cost`. No se bajaron los datos | alta (formatos) / media / baja (completitud) | paquete nuevo `seguro` o archivo en `cultivos` | [#6](../../coordinacion/para_decidir.md): paquete `seguro` |
| [siembra_prevenida.md](siembra_prevenida.md) | Siembra prevenida por condado y cultivo (FSA) y qué agrega el RMA | FSA Crop Acreage Data 2009–2025 por condado; 2019 récord (4,73 M ac de maíz en los 7 estados). Algunos códigos de condado de FSA no son FIPS. RMA agrega causa y mes (r = 0,99 con FSA en 2019). Propone `frac_prevenida` | alta (archivos, 2019 y 2025) / media | `siembra_prevenida_anual.csv` (nuevo), `requirements.txt` | [#17](../../coordinacion/para_decidir.md) |
| [eventos_extremos.md](eventos_extremos.md) | Eventos climáticos 2000–2025 que movieron rendimiento o siembra en los 7 estados | Tabla de 13 eventos (sequías 2002, 2012, 2022; inundaciones 2008, 2011, 2019; derecho 2020; etc.) con la variable de nuestros CSV donde debería verse | media (alta para eventos, media a baja para cifras) | T007 (control de calidad), años raros para ML | — |
| [rangos_estados_nuevos.md](rangos_estados_nuevos.md) | ¿Los rangos físicos de `validar_csv()` y del spec dejan afuera datos reales de OH, NE, MN y KS? | Sí en rendimiento: el Censo 2012 da maíz 21,7 bu/ac (Osage KS) y 2022 soja 7,2 (Chautauqua KS). Clima de POWER dentro del spec salvo margen chico de tmin diaria (−48 °C en MN). Propone maíz 5–300, soja 2–100, trigo 5–130, avena 10–200, tmin diaria −55 | media (rendimiento, sin encuesta ni secano) / alta (clima) | `src/common/validacion.py`, `loop/spec/entregables.yaml` | Cambiar los rangos (sin número) |

Auxiliar: [eventos_extremos_rend_estado.py](eventos_extremos_rend_estado.py) (rendimiento por estado contra el
promedio de 5 años; probado solo con un archivo sintético).

## Contradicciones

Diferencias entre documentos que conviene tener en cuenta. Ninguna se corrigió acá.

1. **Kc de FAO-56.** [cultivos_zona.md](cultivos_zona.md) carga en `config/cultivos.csv` los Kc de FAO-56 sin
   ajustar; [agua_por_cultivo.md](agua_por_cultivo.md) mide que en la zona sobreestiman la ET ~15–45 % (un solo
   sitio, Mead). Las dos cosas conviven hasta que se decida la propuesta
   [#12](../../coordinacion/para_decidir.md).
2. **Siembra prevenida de 2019.** [eventos_extremos.md](eventos_extremos.md) da OH 1,49 M, IL 1,50 M e IN
   0,94 M acres (FSA, agosto de 2019, todos los cultivos) y pone a OH, IL e IN como los estados del evento;
   [siembra_prevenida.md](siembra_prevenida.md) da, para maíz en el archivo final, IL 1,15 M, **MN 1,00 M** y
   OH 0,93 M. No es un error (cultivos y fecha de corte distintos), pero MN no aparece entre los afectados en
   `eventos_extremos.md` y sí es el segundo en maíz. Para T007 conviene usar los números de FSA final.
3. **Acceso a la base completa de Quick Stats.** [eventos_extremos.md](eventos_extremos.md) dice que el índice
   `https://www.nass.usda.gov/datasets/` dio 404 el 2026-11-15 y que no pudo bajarla;
   [nass_2024_2025.md](nass_2024_2025.md), [riego_nass.md](riego_nass.md), [sorgo.md](sorgo.md) y
   [precios_margenes.md](precios_margenes.md) usan `qs.crops_20261114.txt.gz`, bajado el día anterior. Por eso
   los rendimientos de `eventos_extremos.md` salen de prensa y no de NASS: hay que confirmarlos con su script.
4. **Carbono y rotación.** Dentro de [carbono_erosion.md](carbono_erosion.md): la tasa global de West y Post
   (+0,20 t C/ha/año por complejizar la rotación) no se ve en los ensayos del Corn Belt que se abrieron (Indiana,
   Lamberton). Las reglas de ML no deberían usar +0,20 sin aclararlo (propuesta
   [#15](../../coordinacion/para_decidir.md)).
5. **Región ERS de IA, IL e IN.** [precios_margenes.md](precios_margenes.md) la da como Heartland con confianza
   media ("no citado"); [regiones_ers.md](regiones_ers.md) lo confirma con la tabla oficial `reglink.xls`. No
   hay contradicción en el valor, pero la confianza de `precios_margenes.md` quedó vieja.
6. **Cobertura de estados en `precios_margenes.md`.** Habla de precios para IA, IL e IN y de un paquete
   `economia` "que hoy no está en el CLAUDE.md"; después se sumaron OH, NE, MN y KS y `src/economia/` ya
   existe. Además remite a `loop/notes/decisiones.md`, que no está en este repo: la propuesta de economía no
   figura en `coordinacion/para_decidir.md`.
7. **`(D)` en NASS por condado.** [nass_quickstats.md](nass_quickstats.md) pide mapear `(D)`/`(Z)` a vacío con
   `flag_nass`; [riego_nass.md](riego_nass.md) y [nass_2024_2025.md](nass_2024_2025.md) encontraron que en la
   encuesta por condado no aparece ningún `(D)` (lo oculto va a los combinados 998). No se contradicen: la regla
   sigue haciendo falta para el Censo, donde sí hay `(D)`, pero en `produccion_anual.csv` el faltante es una fila
   ausente (propuesta [#7](../../coordinacion/para_decidir.md)).
