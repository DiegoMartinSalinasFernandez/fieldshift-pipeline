# Fechas de siembra y cosecha de Dakota del Norte (ND)

Pregunta: Igual que T009 (`config/cultivos_estado.csv`), para ND: fechas habituales de siembra y cosecha de maíz,
soja, trigo de primavera y de invierno, avena, alfalfa y heno (USDA Agricultural Handbook 628 y Crop Progress de
ND, promedio de 5 años), y ventanas de floración del maíz y llenado de la soja. Proponer las filas para
`config/cultivos_estado.csv` sin aplicarlas.

Respuesta corta: La tabla de **North Dakota del Handbook 628 (pág. 44)** trae los 7 cultivos que se pidieron. Para
alfalfa y heno da solo el primer y el último corte, y la siembra figura como "(NA)", igual que en los otros 7 estados. Abajo van
las 7 filas propuestas. Seis usan códigos de cultivo que ya existen. La de **trigo de primavera necesita un código
nuevo (`trigo_primavera`)**, que hoy no está en `config/cultivos.csv`: lo decide el humano. Crop Progress, con el promedio
**2021–2025** de los reportes de 2026, coincide con el Handbook en la siembra (dentro de unos días). En la cosecha
de maíz va **más adelantado**: 50 % cosechado el 23 de octubre, 75 % el 5 de noviembre. El Handbook pone el
período más activo del 8 de octubre al 19 de noviembre. **ND no aparece en las tablas de trigo de invierno de Crop
Progress**: para ese cultivo solo está el Handbook. Ventanas: la **floración del maíz (25–75 % *silking*) va del
20 de julio al 4 de agosto** (50 % el 27 de julio, día 208). Es entre 5 y 14 días más tarde que en los 7 estados
del Corn Belt, cuya mediana del 50 % va del día 194 al 203 (`ventanas_por_estado.md`), y deja en julio solo el 75 %
de la ventana. El **llenado de la soja (50 % *setting pods* → 25 % *dropping leaves*) va del 2 de agosto al 5 de
septiembre** (35 días, el 87 % en agosto).

Detalle:

**1. Handbook 628 (NASS, *Field Crops Usual Planting and Harvesting Dates*, octubre de 2010), tabla "Usual Planting and
Harvesting Dates by Crop – North Dakota", página impresa 44.** Comprobé el número en el pie de la página del
PDF, que dice "44 … Field Crops Usual Planting and Harvesting Dates (October 2010)", y coincide con el índice. Las filas
usadas son las mismas que en T009, más el trigo de primavera. Copio el texto tal cual (`pdftotext -layout`):

```
                                       2009      Usual planting dates               Usual harvesting dates
                                    Harvested   Begin   Most active      End     Begin   Most active      End
                                  (1,000 acres)
Corn for grain .................      1,740     Apr 26  May 2 - May 28   Jun 4   Sep 28  Oct 8 - Nov 19   Dec 6
Hay, alfalfa ...................      1,780     (NA)    (NA)             (NA)    Jun 10  (NA)             Sep 6
Hay, other .....................      1,180     (NA)    (NA)             (NA)    Jun 19  (NA)             Sep 2
Oats, spring ...................        165     Apr 19  Apr 26 - May 25  Jun 3   Jul 28  Aug 5 - Sep 5    Sep 18
Soybeans .......................      3,870     May 7   May 14 - Jun 3   Jun 11  Sep 17  Sep 24 - Oct 21  Nov 5
Wheat, spring ..................      6,300     Apr 16  Apr 24 - May 25  Jun 3   Aug 1   Aug 8 - Sep 13   Sep 25
Wheat, winter ..................        545     Sep 6   Sep 10 - Sep 25  Oct 2   Jul 15  Jul 20 - Jul 29  Aug 10
```

La tabla trae además cebada, frijol seco, maíz para silo, lino, papa, remolacha, girasol y trigo durum. No van a
`cultivos_estado.csv` porque no son cultivos del proyecto. El durum (1,57 M acres en 2009) es un trigo de primavera
aparte: no lo sumé a `trigo_primavera`.

**2. Filas propuestas para `config/cultivos_estado.csv`** (no aplicadas: ND no está en `config/config.yaml`).
Mismo criterio que T009: la primera fecha del período más activo va a `*_activa_inicio` y la segunda a
`*_activa_fin`. "(NA)" queda vacío. En alfalfa y heno, la cosecha va del primer al último corte.

```
maiz,ND,04-26,05-02,05-28,06-04,09-28,10-08,11-19,12-06,"USDA NASS, Agricultural Handbook 628 (2010)",44
soja,ND,05-07,05-14,06-03,06-11,09-17,09-24,10-21,11-05,"USDA NASS, Agricultural Handbook 628 (2010)",44
trigo_invierno,ND,09-06,09-10,09-25,10-02,07-15,07-20,07-29,08-10,"USDA NASS, Agricultural Handbook 628 (2010)",44
avena,ND,04-19,04-26,05-25,06-03,07-28,08-05,09-05,09-18,"USDA NASS, Agricultural Handbook 628 (2010)",44
alfalfa,ND,,,,,06-10,,,09-06,"USDA NASS, Agricultural Handbook 628 (2010)",44
heno,ND,,,,,06-19,,,09-02,"USDA NASS, Agricultural Handbook 628 (2010)",44
trigo_primavera,ND,04-16,04-24,05-25,06-03,08-01,08-08,09-13,09-25,"USDA NASS, Agricultural Handbook 628 (2010)",44
```

Si se aplican, cada celda lleva su cita en `docs/research/cultivos_fuentes.csv`, como en T009. La cita es la línea de
la tabla de arriba. No las agregué ahora porque la tarea pide no aplicar nada. La fila `trigo_primavera` solo va si
el humano crea ese código en `config/cultivos.csv`. Si no, queda afuera.

Comparación con los 7 estados actuales: el maíz de ND se siembra una semana más tarde que en IA (04-26 contra
04-19) y su cosecha termina más tarde que en cualquier otro estado (12-06; el siguiente es OH con 12-01). La soja se
siembra más tarde que en todos (05-07) y se cosecha antes que en IA (09-17 contra 09-21). En el trigo de invierno,
la siembra (09-06 a 10-02) cae entre la de MN y la de NE. La primera cosecha de alfalfa (06-10) y de heno (06-19)
es la más tardía de todos los estados.

**3. Crop Progress de ND, promedio de 5 años.** `docs/research/fechas_nd_cp.py` baja de ESMIS los 31 reportes
semanales de texto de 2026, a una carpeta fuera del repo. De cada tabla "<Cultivo> <Etapa> - Selected States" toma
la fila de North Dakota y la columna **"2021-2025 Average"**, que es el promedio que publica NASS, no uno calculado
acá. Después interpola linealmente el día en que ese promedio cruza el 10, 25, 50, 75 y 90 %. Los días se cuentan
sobre el calendario de 2026, que no es bisiesto. Las fechas de la tabla nacional son la semana que termina el
domingo. El resultado está en `docs/research/fechas_nd_cp.csv`. Las celdas vacías corresponden a umbrales que el
promedio no llegó a cruzar mientras el cultivo estuvo en la tabla. Por ejemplo, la avena sale de la tabla de
siembra con el 66 %, así que su 75 % y su 90 % quedan sin dato.

| Cultivo | Etapa | 10 % | 25 % | 50 % | 75 % | 90 % | Handbook 628 (inicio · activo · fin) |
|---|---|---|---|---|---|---|---|
| Maíz | sembrado | 05-04 | 05-12 | 05-20 | 05-29 | 06-06 | 04-26 · 05-02–05-28 · 06-04 |
| Maíz | cosechado | 10-04 | 10-13 | 10-23 | 11-05 | — | 09-28 · 10-08–11-19 · 12-06 |
| Soja | sembrado | 05-09 | 05-16 | 05-26 | 06-05 | 06-13 | 05-07 · 05-14–06-03 · 06-11 |
| Soja | cosechado | 09-21 | 09-30 | 10-09 | 10-19 | 10-31 | 09-17 · 09-24–10-21 · 11-05 |
| Trigo de primavera | sembrado | 04-22 | 05-04 | 05-15 | 05-26 | 06-04 | 04-16 · 04-24–05-25 · 06-03 |
| Trigo de primavera | cosechado | 08-09 | 08-16 | 08-27 | 09-05 | — | 08-01 · 08-08–09-13 · 09-25 |
| Avena | sembrado | 04-28 | 05-07 | 05-17 | — | — | 04-19 · 04-26–05-25 · 06-03 |
| Avena | cosechado | 08-07 | 08-15 | 08-25 | 09-04 | — | 07-28 · 08-05–09-05 · 09-18 |
| Trigo de invierno | — | ND no está en las tablas | | | | | 09-06 · 09-10–09-25 · 10-02 (siembra) |
| Alfalfa, heno | — | Crop Progress no tiene cortes por estado | | | | | 06-10 a 09-06; 06-19 a 09-02 |

Lectura: en la siembra, el período más activo del Handbook queda muy cerca del rango del 25 al 75 % de Crop
Progress, dentro de unos 5 días. La cosecha de maíz es la que más se aleja. En 2021–2025, a mediados de noviembre ya
estaba cosechado más del 75 %, y la última semana publicada (8 de noviembre) marca el 80 %. El Handbook, en cambio,
extiende el período más activo hasta el 19 de noviembre. El trigo de primavera y la avena también se cosechan más
cerca del centro del período más activo que de sus extremos. No cambié las filas propuestas por esto: el formato de
`cultivos_estado.csv` es el del Handbook (inicio, período más activo, fin), y mezclar las dos fuentes en una fila
rompería la comparación con los otros 7 estados.

**4. Ventanas críticas de ND** (promedio 2021–2025 de Crop Progress; mismas definiciones que
`ventanas_por_estado.md`)

| Ventana | Inicio | 50 % | Fin | Duración | Fracción en el mes fijo |
|---|---|---|---|---|---|
| Floración del maíz: *silking* 25 % → 75 % | 07-20 (día 200,6) | 07-27 (208,1) | 08-04 (215,8) | 15 días | 0,75 en julio |
| Llenado de la soja: 50 % *setting pods* → 25 % *dropping leaves* | 08-02 (214,0) | — | 09-05 (248,5) | 35 días | 0,87 en agosto |

Para referencia, la floración de la soja (50 % *blooming*) cae el 07-18 (día 198,5), y el maíz llega a 50 %
*dough* el 08-18 y a 50 % *dented* el 09-06.

Comparado con los 7 estados (`ventanas_por_estado.md`, mediana 2008–2025 del 50 % *silking*: de 194 en IL a 203
en OH), **ND florece 5 días después que OH y 2 semanas después que IL**. En la mediana de los otros estados, la ventana
25–75 % cae entera en julio. En ND, en cambio, un cuarto cae en los primeros días de agosto. Si ND entra al
proyecto, `prec_jul_mm`, `tmax_jul_c` y `dias_tmax_gt30_jul` captan peor la floración de lo que la captan en el
resto. Esto refuerza la propuesta de `ventanas_por_estado.md` de agregar ventanas por estado y año desde
`fenologia_estado.csv`, una decisión del humano porque cambia el esquema. El llenado de la soja empieza dentro del rango
de los demás (días 210–221), pero termina antes (allí, días 253–257), y por eso cae mejor en agosto.

**Supuestos y límites**

- El promedio de 5 años es el que publica NASS en los reportes de 2026: es **2021–2025**. No calculé un promedio
  propio. No verifiqué cómo trató NASS las semanas de octubre y noviembre de 2025, sin reportes por el cierre del
  gobierno. Ese hueco puede afectar el promedio de cosecha de maíz y soja.
- Bajaron 31 reportes de 2026, de la semana 14 a la 45. Falta la semana 38 (`prog3826`), que no aparece en el
  listado de ESMIS, y no la busqué por otra vía. Si falta de verdad, la interpolación cubre esas dos semanas con una
  recta.
- Los días del año y las fechas MM-DD salen de interpolar entre semanas consecutivas (7 días; 14 donde falta la
  semana 38). Son fechas de un año "promedio", no las de un año real.
- El Handbook 628 es de 2010 y no tiene una edición posterior. Las superficies de 2009 que trae (maíz, 1,74 M acres)
  son muy distintas de las actuales, de 3,95 a 4,7 M acres en 2021–2025 (`nass_mi_nd.md`).
- No miré el reporte estatal *North Dakota Crop Progress & Condition*. Podría traer cortes de alfalfa o heno y la
  siembra de trigo de invierno, pero no lo verifiqué.

Fuentes:
- [USDA NASS, Field Crops Usual Planting and Harvesting Dates, Agricultural Handbook 628 (octubre de 2010), pág. 44](https://downloads.usda.library.cornell.edu/usda-esmis/files/vm40xr56k/dv13zw65p/w9505297d/planting-10-29-2010.pdf), consultado 2026-11-15
- [USDA NASS, Crop Progress (reportes semanales de 2026, archivo ESMIS)](https://esmis.nal.usda.gov/publication/crop-progress), consultado 2026-11-15
- `docs/research/ventanas_por_estado.md` y `docs/research/nass_mi_nd.md` (este repo), para comparar

Confianza: alta en las filas del Handbook, copiadas de la tabla de la pág. 44, y en los cruces de Crop Progress,
que son una interpolación directa del promedio publicado. Media en la comparación de la cosecha, por el hueco de
2025 y la semana 38 que falta.

Impacto: `config/cultivos_estado.csv` (7 filas propuestas, sin aplicar), `config/cultivos.csv` (código nuevo
`trigo_primavera`, si el humano lo aprueba), `docs/research/cultivos_fuentes.csv` (las citas, al aplicar) y
ventanas de `clima_anual.csv` si ND entra al proyecto.
