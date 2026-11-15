# Ventanas críticas por estado: floración del maíz y llenado de la soja

Pregunta: Con 7 estados, ¿siguen sirviendo las ventanas fijas de CLAUDE.md, julio para la floración del maíz y
agosto para el llenado de la soja? ¿O conviene usar ventanas por estado? Para cada estado: ventana de floración
del maíz (25 % a 75 % *silking*) y de llenado de la soja, en días del año, con la mediana 2008–2025 y el rango.
¿Qué columnas de `clima_anual.csv` cambiarían?

Respuesta corta: **Entre estados, la diferencia es chica. Entre años, es grande.** La mediana del 50 %
*silking* va del día 194 (IL, 13 de julio) al 203 (OH, 22 de julio). Kansas (195) y Minnesota (202) están a
**una semana**, no a varias. En cambio, dentro de un mismo estado el 50 % se mueve de 14 a 24 días según el año.
Los años que se salen son siempre los mismos: 2012, adelantado, y 2019, atrasado. La ventana 25–75 % de
*silking* cae entera en julio en la mediana de los 7 estados. Queda menos del 80 % dentro de julio solo en 8 de
126 estado-años (OH e IN en 2019; IL y KS en 2012; IA en 2008 y 2013; IL en 2018; OH en 2011). El llenado de la soja va del
50 % *setting pods* (R3–R4) al 25 % *dropping leaves* (R7). Empieza a fin de julio (días 210–221), termina a
mediados de septiembre (253–257) y dura de 37 a 46 días. Agosto queda casi siempre adentro, pero cubre solo
dos tercios de la ventana: falta la primera quincena de septiembre.
**Recomendación:** no cambiar "julio" y "agosto" por ventanas fijas por estado, porque casi no ganan nada.
Sí agregar, como columnas nuevas y sin borrar las de mes fijo, ventanas **por estado y año** que salgan de
`fenologia_estado.csv`. Eso cambia el esquema de `clima_anual.csv`, así que lo decide el humano.

Detalle:

**Cómo se midió.** En esta máquina no hay datos de Quick Stats (`qs.crops_*`) ni `fenologia_estado.csv`, y no
se leyó `.env`. Por eso se usó la publicación semanal *Crop Progress* de NASS (ESMIS), que es la fuente de esos
mismos datos. `docs/research/ventanas_por_estado.py` hace tres cosas:

1. Baja a una carpeta fuera del repo los 381 reportes de junio a octubre de 2008–2025.
2. De cada tabla "Corn Silking / Dough / Dented" y "Soybeans Blooming / Setting Pods / Dropping Leaves -
   Selected States" toma el valor de la semana actual. En el formato anterior a 2010 son las tablas
   "Corn: Percent Silking".
3. Interpola linealmente el día del año en que se cruza el 25, el 50 y el 75 %.

La semana se fecha en el domingo de cierre: el domingo anterior al día de publicación. El parser comprueba que
la columna "esta semana" tenga el año del reporte. El resultado son los 756 cruces de
`docs/research/ventanas_por_estado.csv`: estado, etapa, año, `doy25/50/75` y `gap*`, que son los días entre las
dos semanas usadas para interpolar.

Calidad de los cruces:
- 2.252 de los 2.256 cruces se interpolaron entre semanas seguidas (7 días). Los 4 restantes saltan 21 días por
  el hueco de octubre de 2025 (cierre del gobierno), y caen todos en *dropping leaves* de 2025.
- Faltan 11 cruces del 25 %, porque el primer reporte del año ya venía en 25 % o más. Son *setting pods* (IA
  2008 y 2009, IN y NE 2014), *dough* (IL y KS) y *dented* (KS 2020). Falta 1 cruce del 75 % (KS
  *dropping leaves* 2025).
- De *silking* no falta ningún cruce: 18 años × 7 estados.

Contraste con `crop_progress_estados_nuevos.md`, que da la mediana 2000–2018 del 50 % *silking*: OH 201, NE 198,
MN 202, KS 192. Acá, con 2008–2025, sale OH 203, NE 198, MN 202, KS 195. La diferencia entra en lo esperable
por el cambio de período.

**Floración del maíz: *silking* 25 % → 75 %** (día del año, mediana 2008–2025 y [mín–máx], n = 18 en todos)

| Estado | 25 % | 50 % | 75 % | Ventana típica (mediana 25–75 %) | Duración (días) | Fracción de la ventana en julio |
|---|---|---|---|---|---|---|
| KS | 185 [176–192] | 195 [185–200] | 205 [199–213] | 4 jul – 24 jul | 20 [15–26] | 1,00 [0,69–1,00] |
| IL | 188 [178–200] | 194 [184–206] | 201 [189–214] | 7 jul – 20 jul | 12 [10–17] | 1,00 [0,56–1,00] |
| IN | 192 [181–203] | 200 [188–212] | 207 [196–222] | 11 jul – 26 jul | 14 [11–19] | 1,00 [0,54–1,00] |
| NE | 193 [183–198] | 198 [190–204] | 204 [199–211] | 12 jul – 23 jul | 13 [10–16] | 1,00 [1,00–1,00] |
| IA | 193 [185–204] | 198 [191–210] | 205 [197–218] | 12 jul – 24 jul | 12 [9–15] | 1,00 [0,67–1,00] |
| OH | 196 [187–206] | 203 [192–215] | 211 [199–225] | 15 jul – 30 jul | 14 [10–20] | 1,00 [0,38–1,00] |
| MN | 197 [187–207] | 202 [192–211] | 209 [197–215] | 16 jul – 28 jul | 10 [8–16] | 1,00 [0,88–1,00] |

Las fechas de la columna "ventana típica" son de año no bisiesto: día 185 = 4 de julio y día 211 = 30 de julio.
La duración y la fracción en julio se calcularon por estado y año, y la tabla muestra su mediana y rango.

Para el llenado del grano de maíz como contexto: el 50 % *dough* (R4) cae entre los días 215 (KS) y 224 (MN), y
el 50 % *dented* (R5) entre 234 (KS) y 245 (OH).

**Llenado de la soja: *setting pods* 50 % → *dropping leaves* 25 %** (día del año, mediana y [mín–máx])

Crop Progress no informa R5 (comienzo de llenado de semilla) ni R6. Se toma como inicio el 50 % de
*setting pods* (R3, mayoría de lotes en formación de vainas; R5 llega aproximadamente 1 a 2 semanas después) y como fin el 25
% de *dropping leaves* (comienzo de R7, madurez fisiológica). La ventana incluye la formación de vainas (R3–R4),
que también es crítica por agua. Si se quiere solo el llenado de la semilla, una alternativa es arrancar en el
75 % de *setting pods* (columna incluida). Esta definición es un supuesto de esta propuesta.

| Estado | *Blooming* 50 % | *Setting pods* 50 % | *Setting pods* 75 % | *Dropping leaves* 25 % | Ventana típica | Duración (días) | Fracción de la ventana en agosto | Fracción de agosto dentro de la ventana |
|---|---|---|---|---|---|---|---|---|
| KS | 203 [193–213] | 221 [211–227] | 236 [225–239] | 257 [248–265] | 9 ago – 14 sep | 37 [29–46] | 0,64 [0,46–0,86] | 0,75 [0,54–1,00] |
| NE | 196 [187–205] | 212 [205–220] | 223 [217–229] | 253 [244–263] | 31 jul – 10 sep | 41 [33–50] | 0,74 [0,57–0,93] | 1,00 [0,80–1,00] |
| IL | 195 [184–209] | 212 [198–224] | 223 [209–236] | 257 [246–268] | 31 jul – 14 sep | 44 [38–50] | 0,67 [0,46–0,81] | 1,00 [0,63–1,00] |
| IN | 198 [188–214] | 213 [202–230] | 225 [216–243] | 253 [244–265] | 1 ago – 10 sep | 39 [29–46] | 0,75 [0,40–0,89] | 1,00 [0,45–1,00] |
| OH | 200 [191–214] | 215 [207–229] | 225 [218–240] | 253 [247–264] | 3 ago – 10 sep | 38 [34–45] | 0,75 [0,43–0,90] | 0,94 [0,50–1,00] |
| IA | 195 [189–206] | 210 [205–222] | 221 [214–232] | 257 [252–266] | 29 jul – 14 sep | 46 [44–50] | 0,65 [0,51–0,71] | 1,00 [0,72–1,00] |
| MN | 197 [188–205] | 213 [205–221] | 221 [214–232] | 257 [247–262] | 1 ago – 14 sep | 43 [37–47] | 0,67 [0,60–0,80] | 0,99 [0,74–1,00] |

**Lectura.**
1. **Maíz, julio sigue sirviendo.** En la mediana, julio contiene la ventana 25–75 % entera en los 7 estados.
   La distancia entre el estado más temprano y el más tardío es de 9 días (IL 194 y OH 203). Una ventana fija
   por estado correría julio menos de una semana y no arreglaría los años que fallan: 2012 adelantado (IL y KS
   empiezan el 25 % a fin de junio, días 176–178) y 2019 atrasado (OH e IN terminan el 75 % a mitad de
   agosto, días 221–225). Esos desvíos son del año, no del estado.
2. **Kansas es distinto por el ancho, no por la fecha.** Su ventana dura 20 días, contra 10–14 en el resto,
   porque mezcla maíz de riego y de secano con siembras escalonadas (CLAUDE.md, §2). Su 25 % llega antes
   (185) y su 75 % igual que en los demás (205). El dato de estado sirve menos para un condado puntual de
   Kansas.
3. **Soja, agosto es el núcleo pero no alcanza.** El llenado va de fin de julio a mediados de septiembre, y
   agosto cubre de 64 a 75 % de la ventana. La primera quincena de septiembre (R6, llenado activo de la semilla) queda afuera de `prec_ago_mm`.
4. **Kansas tiene la soja más tardía**, del orden de una semana en *setting pods* (221 contra 210–215). Puede
   ser en parte la soja de segunda tras trigo, que en Kansas es común y entra en el mismo porcentaje estatal.
   No lo verifiqué: Crop Progress no separa primera y segunda.
5. **Temporada abril–septiembre:** no se analizó en detalle, pero con estos números no hace falta moverla. El
   50 % de *dented* termina antes del día 245 (2 de septiembre) en todos los estados, y el 25 % de *dropping
   leaves* cae a mediados de septiembre.

**Propuesta concreta para el humano** (cambia el esquema de `clima_anual.csv`; no se tocó código):

- **Mantener** `prec_jul_mm`, `tmax_jul_c`, `dias_tmax_gt30_jul` y `prec_ago_mm` como están: son comparables
  entre estados y no dependen de otro paquete.
- **Agregar** ventanas por estado y año, calculadas desde los cruces de `fenologia_estado.csv`. Eso exigiría
  que `fenologia_estado.csv` tenga el 25 y el 75 % además del 50 %, y sumar *setting pods* y *dropping leaves*
  de la soja. Es otro cambio de esquema, del paquete `cultivos`.

  | Columna actual | Columna nueva propuesta | Ventana |
  |---|---|---|
  | `prec_jul_mm` | `prec_floracion_maiz_mm` | *silking* 25 % → 75 % del estado y año |
  | `tmax_jul_c` | `tmax_floracion_maiz_c` | ídem |
  | `dias_tmax_gt30_jul` | `dias_tmax_gt35_floracion_maiz` (y/o `_gt30_`) | ídem; 35 °C, como `dias_tmax_gt35` de `clima_mensual.csv` |
  | `prec_ago_mm` | `prec_llenado_soja_mm` | *setting pods* 50 % → *dropping leaves* 25 % |
  | — | `deficit_llenado_soja_mm`, `tmax_llenado_soja_c` | ídem |
  | — | `doy_ini_floracion_maiz`, `doy_fin_floracion_maiz`, `doy_ini_llenado_soja`, `doy_fin_llenado_soja` | para que ML vea la ventana usada |

- Como la ventana se fija con datos de ese año y estado, el valor solo se conoce al final de la floración.
  Para un modelo de pronóstico **dentro de la temporada**, la alternativa sin fuga es la mediana 2008–2025
  del estado (tabla de arriba), o la mediana de los años anteriores al `anio`. Lo decide ML.
- Si se prefiere no depender de `fenologia_estado.csv`, la versión mínima es **una ventana fija por estado**
  con las medianas de arriba. Por la lectura 1, se gana poco con eso en el maíz. En la soja, sumar la primera
  quincena de septiembre (`prec_ago_sep15_mm`) captura casi lo mismo sin pasar por la fenología.
- Lo mismo vale para `ndvi_media_jul_ago` (paquete `lotes` / teledetección), que usa una ventana fija de julio
  y agosto. No lo analicé.

Fuentes:
- [Crop Progress – publicación semanal (USDA NASS, archivo ESMIS)](https://esmis.nal.usda.gov/publication/crop-progress),
  consultado 2026-11-15. Se usaron los 381 reportes en texto de junio a octubre de 2008–2025, por ejemplo:
  - [Crop Progress 28-07-2008](https://esmis.nal.usda.gov/sites/default/release-files/8336h188j/g732db28c/76537283z/CropProg-07-28-2008_revision.txt), formato viejo;
  - [prog3220.txt, 03-08-2020](https://esmis.nal.usda.gov/sites/default/release-files/8336h188j/70795w747/z890sg57f/prog3220.txt), formato nuevo.
- `docs/research/crop_progress_estados_nuevos.md` (etapas por estado, hueco de 2025, medianas 2000–2018).
- `config/cultivos_estado.csv` (Handbook 628): da siembra y cosecha, no floración, así que sirvió solo como
  contexto. Por ejemplo, Kansas siembra el maíz antes (siembra activa desde el 15 de abril, contra el 25 en IA)
  y la soja después (hasta el 20 de junio).
- `src/clima/process.py` (líneas 250–260, columnas de julio y agosto), leído 2026-11-15.
- Etapas de la soja (R3 formación de vainas, R5 comienzo de llenado, R7 madurez fisiológica) y relación de
  *dropping leaves* con R7: definiciones de las etapas de Crop Progress de NASS. La equivalencia exacta entre
  *setting pods* / *dropping leaves* y las etapas R es **aproximada**.

Confianza:
- **Alta** para las fechas de *silking*, *setting pods* y *dropping leaves* por estado y año: salen de los
  reportes originales, con interpolación entre semanas seguidas.
- **Media** para la definición de "llenado de la soja" (de *setting pods* 50 % a *dropping leaves* 25 %): es un
  supuesto razonable, no un estándar.
- **Baja** para la explicación del ancho de Kansas (riego y secano) y para el papel de la soja de segunda:
  son hipótesis, no se verificaron.

Impacto:
- **`clima_anual.csv` (paquete `clima`):** columnas nuevas propuestas, sin borrar las de julio y agosto. Es un
  cambio de esquema que decide el humano.
- **`fenologia_estado.csv` (paquete `cultivos`):** para armar las ventanas habría que sumar 25 y 75 % de
  *silking* y las etapas *setting pods* y *dropping leaves* de la soja. También es cambio de esquema.
- **CLAUDE.md §4 ("Meses críticos"):** si se aprueba, se agrega la definición de las ventanas por estado y año.
- `docs/research/ventanas_por_estado.csv` y `.py`: datos y script reproducibles de esta respuesta.

---

# Ventanas críticas en MO, WI, SD, ND, MI y KY (T114)

Pregunta: Con el mismo método de la sección anterior, ¿cuáles son las ventanas de floración del maíz (25–75 %
*silking*) y de llenado de la soja (50 % *setting pods* → 25 % *dropping leaves*) en Missouri, Wisconsin,
Dakota del Sur, Dakota del Norte, Michigan y Kentucky (mediana 2008–2025 y rango)? ¿En cuántos estado-años la
ventana cae menos del 80 % dentro de julio o de agosto? ¿Cambia la recomendación de ventanas fijas de mes contra
ventanas por estado y año?

Respuesta corta: **Con estos estados, la diferencia entre estados deja de ser chica.** La mediana del 50 %
*silking* va ahora del día 191 (MO y KY, 10 de julio) al 208 (ND, 27 de julio): 17 días, contra 9 entre los 7
primeros estados. Los cuatro estados del norte (WI, ND, SD, MI) terminan el 75 % *silking* entre el 29 de julio
y el 3 de agosto en la mediana, así que la ventana se sale de julio por el final. La ventana de floración cae
menos del 80 % dentro de julio en **30 de 106** estado-años de los estados nuevos (WI 9, ND 7, MO 4, SD 4, KY 3,
MI 3), contra 8 de 126 en los 7 primeros; en total, **38 de 232**. En la soja, la ventana cae menos del 80 % dentro
de agosto en **79 de 101** estado-años nuevos (112 de 126 en los primeros, 191 de 227 en total): agosto nunca
alcanza a cubrir el llenado entero, en ningún estado. MO y KY tienen la soja más tardía (fin el 15–19 de
septiembre, agosto cubre 56–65 % de la ventana); SD y ND, la más corta (34–38 días, termina el 5–7 de
septiembre).
**Recomendación:** se mantiene la de la sección anterior (dejar las columnas de mes fijo y agregar ventanas por
estado y año desde `fenologia_estado.csv`), pero **se refuerza**: con 13 estados, julio fijo pierde la última
semana de floración en el norte en la mitad de los años de WI y en 7 de 18 años de ND. La alternativa mínima de
una ventana fija por estado, que antes casi no ganaba nada, ahora sí gana en WI, ND, SD y MI.

Detalle:

**Cómo se midió.** Igual que en la sección anterior. A `docs/research/ventanas_por_estado.py` solo se le
agregaron los 6 estados al diccionario `ST` (el parser ya leía los nombres de dos palabras, como "North
Dakota", y los códigos del formato viejo). Se volvieron a bajar los 381 reportes de junio a octubre de
2008–2025 de ESMIS a una carpeta fuera del repo. No se usó la clave de NASS: Crop Progress de ESMIS es público.
**Control:** la corrida nueva reproduce exactamente (al décimo de día) los 756 cruces ya publicados de los 7
primeros estados, y las fracciones en julio y agosto de esos estados coinciden con las tablas de arriba
(8 de 126 estado-años bajo 0,8 en julio). Se agregaron a `ventanas_por_estado.csv` las 648 filas nuevas
(6 estados × 6 etapas × 18 años), sin tocar las 756 que ya estaban.

Cálculo de las fracciones: julio = días 182–212 y agosto = 213–243 (un día más en años bisiestos). La fracción
es la parte de la ventana [inicio, fin] que cae dentro del mes. "Fracción de agosto dentro de la ventana" es la
parte de los 31 días de agosto que la ventana cubre.

Calidad de los cruces de los estados nuevos:
- 1.893 de los 1.899 cruces se interpolaron entre semanas seguidas. Los 6 restantes saltan 21 días y caen en
  *dropping leaves* de 2013 (KY, MI, MO, WI), por el cierre del gobierno de octubre de 2013.
- Falta el 25 % *silking* de **MO y KY en 2019**: el primer reporte del año con la tabla ya venía por encima del
  25 %. Por eso tienen n = 17 en la floración.
- Falta el 25 % *dropping leaves* (fin de la ventana de la soja) en **ND 2013, 2015, 2018 y 2019, SD 2008 y
  2013, y KY 2019**: el primer valor publicado de *dropping leaves* ya pasaba el 25 %. Esos estado-años quedan sin
  ventana de soja (n = 14 en ND, 16 en SD, 17 en KY). No se rellenaron.
- Falta el 25 % *setting pods* de MI y ND en 2008 (no afecta: la ventana usa el 50 %) y algunos 75 % de
  *dropping leaves* (KY 2021, 2022, 2025; MO 2019, 2025; WI 2025), que tampoco se usan.

**Floración del maíz: *silking* 25 % → 75 %** (día del año, mediana 2008–2025 y [mín–máx])

| Estado | 25 % | 50 % | 75 % | Ventana típica (mediana 25–75 %) | Duración (días) | Fracción de la ventana en julio | Estado-años < 0,8 en julio |
|---|---|---|---|---|---|---|---|
| KY | 182 [174–191] | 191 [184–202] | 203 [195–213] | 1 jul – 22 jul | 19 [15–25] | 1,00 [0,61–1,00] | 3 de 17 (2012, 2017, 2018) |
| MO | 184 [172–193] | 191 [181–201] | 199 [189–209] | 3 jul – 18 jul | 15 [11–21] | 1,00 [0,40–1,00] | 4 de 17 (2012, 2016, 2018, 2024) |
| MI | 199 [191–210] | 205 [196–218] | 213 [203–227] | 18 jul – 1 ago | 13 [10–19] | 1,00 [0,15–1,00] | 3 de 18 (2009, 2019, 2023) |
| SD | 200 [191–210] | 205 [196–217] | 210 [203–226] | 19 jul – 29 jul | 12 [10–18] | 1,00 [0,22–1,00] | 4 de 18 (2008, 2009, 2011, 2019) |
| WI | 201 [194–208] | 207 [200–215] | 215 [206–225] | 20 jul – 3 ago | 14 [11–20] | 0,85 [0,31–1,00] | 9 de 18 (2008, 2009, 2013, 2014, 2017, 2019, 2022, 2023, 2024) |
| ND | 202 [193–213] | 208 [198–218] | 215 [202–225] | 21 jul – 3 ago | 12 [9–16] | 0,85 [0,03–1,00] | 7 de 18 (2008, 2009, 2011, 2014, 2019, 2022, 2024) |

Fechas de año no bisiesto, como arriba. Contexto del llenado del grano de maíz: el 50 % *dough* va de 212 (MO) a
231 (ND) y el 50 % *dented* de 230 (MO) a 250 (ND, 7 de septiembre).

**Llenado de la soja: *setting pods* 50 % → *dropping leaves* 25 %** (mismo supuesto que arriba)

| Estado | *Blooming* 50 % | *Setting pods* 50 % | *Setting pods* 75 % | *Dropping leaves* 25 % | Ventana típica | Duración (días) | Fracción de la ventana en agosto | Fracción de agosto dentro de la ventana |
|---|---|---|---|---|---|---|---|---|
| MO | 204 [193–217] | 222 [213–234] | 235 [227–248] | 262 [253–272] | 10 ago – 19 sep | 39 [33–47] | 0,56 [0,30–0,78] | 0,72 [0,32–0,99] |
| KY | 204 [192–214] | 218 [211–228] | 235 [225–242] | 258 [246–263] | 6 ago – 15 sep | 38 [31–43] | 0,65 [0,46–0,95] | 0,84 [0,53–1,00] |
| WI | 201 [190–210] | 216 [208–226] | 226 [216–239] | 259 [253–265] | 4 ago – 16 sep | 43 [36–49] | 0,64 [0,48–0,78] | 0,90 [0,57–1,00] |
| MI | 199 [195–213] | 215 [206–231] | 224 [215–242] | 254 [249–263] | 3 ago – 11 sep | 41 [30–46] | 0,74 [0,43–0,83] | 0,94 [0,41–1,00] |
| SD | 199 [191–207] | 215 [208–225] | 226 [218–238] | 248 [239–263] | 3 ago – 5 sep | 34 [28–41] | 0,86 [0,50–1,00] | 0,92 [0,62–1,00] |
| ND | 199 [191–206] | 213 [202–222] | 222 [208–237] | 250 [241–262] | 1 ago – 7 sep | 38 [31–42] | 0,78 [0,57–0,94] | 1,00 [0,76–1,00] |

n de la ventana de soja: 18, salvo ND (14), SD (16) y KY (17). Estado-años con fracción en agosto < 0,8:
79 de 101 (todos los de MO y WI; la mayoría en KY y MI; menos en SD y ND, donde la ventana es más corta).

**Lectura.**
1. **Maíz: el gradiente norte-sur ya es de más de dos semanas.** MO y KY florecen a principios de julio (50 %
   el día 191), antes que IL (194). WI, ND, SD y MI florecen a fines de julio (205–208), después que MN (202).
   En los cuatro del norte el 75 % cae entre el 29 de julio y el 3 de agosto. Ahí `prec_jul_mm` y `tmax_jul_c`
   pierden el final de la floración en los años tardíos (2008, 2009, 2019 aparecen en casi todos).
2. **Los años que fallan siguen siendo del año, no solo del estado.** En el sur fallan por adelanto (MO y KY
   en 2012, con el 25 % a fin de junio). En el norte fallan por atraso (2008, 2009, 2019). El rango del 50 %
   dentro de un estado es de 18 a 22 días (por ejemplo ND 198–218), más que la distancia entre estados. Una
   ventana fija por estado corrige el corrimiento medio del norte, pero no los años extremos.
3. **Kentucky se parece a Kansas por el ancho**: 19 días de mediana entre el 25 y el 75 % (MO 15), contra
   12–14 en el norte. Posibles causas: siembras escalonadas y maíz de siembra temprana y tardía. No se verificó.
4. **Soja: agosto queda corto en todos lados, pero por distinto lado.** En MO y KY la ventana termina a mitad de
   septiembre (15–19) y agosto cubre solo 56–65 % de ella; en MO, además, la ventana arranca el 10 de agosto y
   no llega a cubrir todo agosto (0,72). En SD y ND la ventana es corta (34–38 días) y termina el 5–7 de
   septiembre: ahí agosto es una buena aproximación (0,78–0,86). Parte de la soja tardía de MO y KY puede ser
   soja de segunda tras trigo, como se supuso para KS. No se verificó: Crop Progress no la separa.
5. **Temporada abril–septiembre:** sigue alcanzando. El 50 % *dented* más tardío es ND (250, 7 de septiembre)
   y el 25 % *dropping leaves* más tardío es MO (262, 19 de septiembre), los dos antes de fin de septiembre.

**¿Cambia la recomendación?** No en lo principal, sí en el énfasis:
- Sigue en pie **mantener** `prec_jul_mm`, `tmax_jul_c`, `dias_tmax_gt30_jul` y `prec_ago_mm`, y **agregar** las
  ventanas por estado y año propuestas arriba (cambio de esquema de `clima_anual.csv` y de
  `fenologia_estado.csv`; lo decide el humano). Con 13 estados es la única opción que sigue los años
  extremos y además el gradiente norte-sur.
- La **versión mínima de ventana fija por estado** (con las medianas de las tablas) ahora sí gana algo: para
  WI, ND, SD y MI correr la ventana del maíz unos 10 días (por ejemplo, 18 de julio – 5 de agosto) en lugar de
  julio calendario. Para MO y KY, julio queda bien.
- Para la soja, la alternativa sin fenología `prec_ago_sep15_mm` (agosto + primera quincena de septiembre)
  sirve para los 13 estados salvo MO y KY, donde la ventana llega al 15–19 de septiembre. Hasta el 20 de
  septiembre las cubriría a todas, con el costo de sumar días después del R7 en SD y ND.

Fuentes:
- [Crop Progress – publicación semanal (USDA NASS, archivo ESMIS)](https://esmis.nal.usda.gov/publication/crop-progress),
  consultado 2026-11-15. Los mismos 381 reportes en texto de junio a octubre de 2008–2025 de la sección
  anterior, bajados de nuevo.
- `docs/research/ventanas_por_estado.py` (con los 6 estados agregados) y `docs/research/ventanas_por_estado.csv`
  (filas de MO, WI, SD, ND, MI y KY).
- Sección anterior de esta página (método, definición de la ventana de la soja, propuesta de columnas).

Confianza:
- **Alta** para las fechas de *silking*, *setting pods* y *dropping leaves* por estado y año: salen de los
  reportes originales y el mismo código reproduce exactamente los cruces ya publicados.
- **Media** para la definición de "llenado de la soja", igual que arriba.
- **Baja** para las explicaciones del ancho de KY y de la soja tardía de MO y KY (siembra escalonada, soja de
  segunda): son hipótesis.

Impacto:
- **`clima_anual.csv` (paquete `clima`)** y **`fenologia_estado.csv` (paquete `cultivos`):** las mismas columnas
  propuestas arriba; con estos estados el argumento a favor es más fuerte. Cambio de esquema: decide el humano.
- Si se suman MO, WI, SD, ND, MI y KY a `config.yaml` (decisión del humano), las columnas de julio fijo van a
  medir peor la floración en el norte que en los 7 estados actuales.
- `docs/research/ventanas_por_estado.csv`: 648 filas nuevas.
