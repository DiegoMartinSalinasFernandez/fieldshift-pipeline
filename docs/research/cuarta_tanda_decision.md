# Cuarta tanda: resumen para decidir (MI, ND, KY)

Pregunta: con lo ya investigado, ¿conviene sumar Míchigan, Dakota del Norte y Kentucky, y en qué orden?

Respuesta corta: **orden recomendado: ND → MI → KY.** ND aporta más maíz y soja que MI y KY juntos, pesa
poco y el pipeline lo procesa sin cambiar el código. Le falta solo el esquema de sus cultivos propios. MI entra
sin cambios de código, pero pesa el doble (por los lagos). KY necesita dos cambios de código antes de
procesarlo, tiene el CDL más flojo de todos los estados revisados y ~15–30 condados de montaña casi sin
agricultura. **Los tres pasan los 5 GB de la regla 6: cada uno necesita el OK del humano.**

Es un resumen: no hay datos nuevos. Cada cifra sale del research que se cita entre paréntesis. Los detalles
están ahí.

## Tabla comparativa

| | **ND** (FIPS 38) | **MI** (26) | **KY** (21) |
|---|---|---|---|
| Condados | 53 | 83 | 120 |
| Maíz sembrado, estado (M ac, 2020–2025) | 1,95–4,7 (varía mucho) | 2,3–2,4 | 1,37–1,6 |
| Soja sembrada, estado (M ac, 2020–2025) | 5,7–7,25 | 2,04–2,25 | 1,8–2,05 |
| Maíz + soja, % de los 7 actuales (prom. 2020–24) | 9,2 % | 4,3 % | — (3,2–3,4 M ac/año) |
| Rendimiento de condado, maíz y soja | 2018–2025 con 2024 (antes de 2018 no se contó) | 2018–2025 con 2024 | 2000–2025 con 2024 |
| Condados con maíz grano en 2025 | 31 / 53 (77 % de la sup.) | 44 / 83 (78 %) | 60 / 120 (81 %) |
| Otros cultivos con condado | trigo prim., durum, cebada, avena (sin 2024); canola, girasol, frijol, lino, arveja, **alfalfa y heno hasta 2025** | trigo inv. y avena (sin 2024) | trigo inv. (sin 2024; 59 % de la sup. en 2025); heno y tabaco **solo hasta 2018** |
| Precisión CDL maíz / soja (productor) | maíz 81–89 % (2017–23); soja ≥ 89 % | maíz 87–89 %, soja 85–87 % (2017–20) | ≥ 87 % hasta 2023; **cae en 2024–25** (maíz 81 %, soja 76–78 %) |
| Precisión global CDL (cultivos FSA) | 73,8–87,2 % | 80,6–92,2 % | 70–87 % hasta 2023; **60 % (2024), 56 % (2025)**: la más baja revisada |
| Clases CDL que no sirven para rotaciones | trigo inv., avena, alfalfa, doble cultivo; heno 2024–25 | barbecho, doble cultivo, trigo prim., girasol, canola; heno 2024–25 | trigo inv. solo (va como doble cultivo 26), tabaco, alfalfa, heno, avena, barbecho |
| Cultivos importantes fuera del esquema | **trigo de primavera, durum, canola, girasol, cebada, frijol seco** (juntos superan al maíz) | frijol seco (~0,25 M ac), remolacha (~0,14 M ac): solo condado en 2018 | tabaco (29–46 mil ac); heno ~2,1 M ac sin condado desde 2019 |
| Riego (maíz grano, Censo 2022) | 2,8 % | **13,3 %** (sudoeste arenoso) | no medido |
| Doble cultivo trigo/soja | no publicado | no publicado | **17–41 % de la soja** |
| Peso de descarga | ~4–5 GB | **~8–11 GB** | ~4–5 GB |
| Tiempo de descarga (Max, estimado) | 0,5–0,7 h | 1–1,5 h (hasta 2 h) | 0,5–0,7 h |
| Teselas MODIS nuevas | ninguna | ninguna | ninguna |
| Cambios de código antes de procesar | ninguno | ninguno (opcional: partir el bbox) | **sí, `suelo_terreno` y `clases_cdl.csv`** |
| ERS (economía) | entero Northern Great Plains | entero Northern Crescent | Heartland 26 + Eastern Uplands 94 (sin serie de trigo) |

Además, una vez por máquina: ~5,8 GB de archivos nacionales (NASS y GRACE). Conviene copiarlos de una máquina
que ya los tenga. Los tres juntos suman 16–20 GB de descarga y 2–3 h de proceso. Pesos y tiempos son
escalados, no medidos (`cuarta_tanda.md`, confianza baja en MODIS y paisaje).

## Problemas conocidos por estado

**ND**
- Su agricultura es de trigo de primavera, canola y girasol. Con los 6 cultivos de `config/`, `produccion_anual.csv`
  deja afuera más superficie de la que cubre el maíz. Sumarlos cambia el esquema: decisión del humano (`nass_mi_nd.md`).
- En el CDL hay que juntar los trigos (22 + 23 + 24) para las rotaciones (`cdl_precision_mi_nd.md`).
- Temporada corta: la soja se cosecha hacia el día 277. El maíz de 2020 (1,95 M ac) fue un año raro, sin
  causa investigada.
- Eventos para el control de calidad: siembra prevenida récord en 2011 (≈5–6 M ac), 2013 y 2022, y sequías
  en 2017 y 2021 (`eventos_extremos_mi_nd.md`).

**MI**
- El bbox (las dos penínsulas) es 3,2 veces su superficie de tierra. MODIS y paisaje bajan todo el lago.
  Partir el bbox en dos (`grupos_bbox()`, `ventanas_estado()`) ahorraría descarga, pero no está medido cuánto
  (`cuarta_tanda.md`).
- SMAP da celdas de costa con hasta 0,89 m³/m³ (> 0,6). Hay que enmascararlas o documentarlas.
- Frijol seco y remolacha: solo CDL (clases 42 y 41) o Censo. Riego del 13 % en el maíz.
- Eventos: sequía de 2012, siembra récord de lenta en 2019 (`eventos_extremos_mi_nd.md`).

**KY**
- **SSURGO:** 39 de las 84 áreas de levantamiento juntan varios condados. Con el `fips_de_area()` de hoy,
  **75 de los 120 condados quedarían sin suelo**. Hay que repartir por `laoverlap`/`muaoverlap` antes, en su
  propia tarea (`suelo_ky.md`).
- **CDL:** el trigo va casi todo como doble cultivo (26). El grupo "trigo" tiene que ser 24 + 26 + 225, y la
  225 está en el grupo `otro` de `clases_cdl.csv`. El heno marcado por el CDL es pastizal en un 78–84 % en
  2024–25 (`cdl_precision_ky.md`).
- **15 condados** sin rendimiento de maíz ni soja en ningún año de 2020–2025, y 32 con menos de 1.000 ac. Son
  casi todos del este, en la montaña (`nass_ky.md`).
- Crop Progress nacional: solo maíz y soja, no trigo. La siembra de maíz va ~2 semanas antes que en Iowa: las
  ventanas fijas de abril a septiembre cortan menos bien.
- Presupuestos de UK: solo 2025–2027 en línea. ERS no tiene trigo en Eastern Uplands (`presupuestos_ky.md`).

Común a los tres: sin 2024 de granos chicos por condado, hueco de Crop Progress del 28-09 al 16-11-2025 y
una sola fila "OTHER COUNTIES" desde 2020 (se descarta). NASS no trae `(D)` en maíz y soja.

## Orden recomendado y por qué

1. **ND primero.** Es el que más suma: 9,7 M ac de maíz y soja, más que MO o WI y que MI + KY juntos. Agrega un
   clima que hoy no está, el norte frío con temporada corta y mucho exceso de agua en primavera. El CDL sirve
   para maíz, soja y sus cultivos propios. Pesa ~5 GB y entra sin cambios de código. Con los 6 cultivos de hoy
   se puede procesar ya. Sus cultivos propios se pueden sumar después, si el humano cambia el esquema.
2. **MI segundo.** Pesa más de lo que aporta (4,3 % de maíz + soja con el doble de descarga), pero no requiere
   ningún cambio para procesarlo y el CDL es bueno. Si se aprueba partir el bbox antes, conviene esperar ese
   cambio.
3. **KY último, o solo el oeste.** Es el que más trabajo previo pide: el reparto de SSURGO y el grupo de trigo
   en `clases_cdl.csv`. Además tiene el CDL más flojo en 2024–25 y un tercio de condados casi sin cultivos.
   Lo que aporta (sur cálido con doble cultivo trigo/soja) está concentrado en los 26 condados de Heartland
   (Midwestern + Purchase, ~2/3 del maíz y la soja).

## Para decidir (humano)

1. OK de la regla de los 5 GB para cada estado que entre (ND y KY quedan justo en el borde, MI pasa con
   claridad).
2. Qué máquina toma cada estado (`coordinacion/maquinas.yaml`) y sumar los estados a `config/config.yaml`.
3. ND: ¿se suman trigo de primavera, durum, canola, girasol y cebada a `config/cultivos.csv` y al esquema de
   `produccion_anual.csv`, o se queda con los 6 cultivos?
4. MI: ¿tarea aparte para partir el bbox antes de bajarlo?
5. KY: ¿entra entero, solo los 26 condados de Heartland o no entra? Si entra, antes hacen falta dos tareas:
   el reparto de SSURGO por `laoverlap` y el grupo de trigo (225) en `clases_cdl.csv`.

Fuentes: `docs/research/cuarta_tanda.md`, `nass_mi_nd.md`, `nass_ky.md`, `cdl_precision_mi_nd.md`,
`cdl_precision_ky.md`, `eventos_extremos_mi_nd.md`, `eventos_extremos_ky.md`, `presupuestos_mi_nd.md`,
`presupuestos_ky.md`, `suelo_ky.md` y `proximos_estados.md` (riego y % de los 7), de este repo. Consultados
el 2026-11-15.

Confianza: la misma que la de cada research. Alta en condados, NASS, precisión del CDL y SSURGO de KY. Baja en
pesos y tiempos (escalados). El orden es una recomendación mía, a partir de esas cifras.

Impacto: ninguno hoy. Si el humano aprueba: `config/config.yaml`, `coordinacion/maquinas.yaml` y, según el
estado, `config/cultivos.csv` (ND), `src/vegetacion/download.py` y `src/paisaje/download.py` (MI),
`src/suelo_terreno/` y `data/reference/clases_cdl.csv` (KY).
