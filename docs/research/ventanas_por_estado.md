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

**Revisión del parser (T116).** El bloque de cada tabla solo se cortaba en la fila de totales ("18 States") y
solo después de haber encontrado alguno de los estados. Si ninguno de los estados figuraba en una tabla, el
parser seguía leyendo hasta la tabla siguiente y le asignaba esa fila: el mismo error que T113 corrigió en
`fechas_nd_cp.py`. Probado con Colorado y Texas, que no están en las tablas de soja, la versión vieja sacaba 175
filas de soja falsas en 1998–2009 (por ejemplo, "CO soja *blooming* 1998-07-19 = 90", que es el trigo de
invierno cosechado de la tabla siguiente). Ahora el bloque también se corta en el título de la tabla siguiente.
**Los números de esta respuesta no cambian:** los 7 estados están en todas las tablas de maíz y soja, y con los
1.119 reportes de ESMIS la serie semanal de la versión nueva es idéntica a la de la vieja, y los 756 cruces
coinciden con `ventanas_por_estado.csv` (diferencias de redondeo de 0,05 días).

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
