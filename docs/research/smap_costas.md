# SMAP de Crop-CASMA en condados con costa de lago (MN, OH; comparación con MI e IN)

Pregunta: las celdas de SMAP (Crop-CASMA, capa `SUB`) de hasta 0,89 m³/m³ que encontró `cuarta_tanda.md`
en MI, ¿son agua de los Grandes Lagos? En MN (lago Superior) y OH (lago Erie), ¿las medias de condado del
release `datos-oh-ne-mn` se acercan al límite físico de 0,6 de §7? ¿Hace falta enmascarar agua en
`src/agua/process.py` antes de promediar?

Respuesta corta:
- **No hace falta una máscara de agua.** El agua abierta ya viene como nodata (`-9999`) en los GeoTIFF de
  Crop-CASMA: de las celdas que tocan el estado y tienen menos de 50 % de tierra, son nodata 61 de 62 en MN,
  27 de 27 en OH y 227 de 232 en MI.
- **Las celdas > 0,6 no son de costa.** Son siempre las mismas celdas, todos los días, y casi todas
  están tierra adentro: turberas del norte de MN (Koochiching, St. Louis, Beltrami, Aitkin, Itasca, Lake of
  the Woods), el sur agrícola de MN (Le Sueur, Hennepin, Waseca), el oeste de OH (Shelby, Auglaize, Darke,
  Allen) y el NE de IN. Ningún condado de OH sobre el Erie tiene celdas > 0,6.
- **En el release las medias de condado no pasan de 0,52.** El máximo de `sm_rootzone_m3m3` diario es 0,512
  (Paulding, OH) y el de `sm_surface_m3m3`, 0,521 (Ottawa, OH). Ningún día de ningún condado queda vacío. La
  razón: `process.py` ya descarta celda por celda los valores fuera de 0–0,60 (`SM_MAX`) antes de promediar.
- **El problema real es otro: el filtro de 0,6 saca mucha área en algunos condados.** En 46 de los 87 condados
  de MN se excluye alguna celda. En Koochiching se excluye el 65 % del área, en Le Sueur el 49 % y en Aitkin
  el 46 %. Las celdas excluidas son las más húmedas, así que la media de esos condados sale hasta
  0,25–0,40 m³/m³ más baja que la media con todas las celdas. Esto no se arregla con una máscara de agua.
  Queda como propuesta para el humano (abajo).

Detalle:

## 1. Medias de condado del release `datos-oh-ne-mn`

`datos-oh-ne-mn_agua.zip` (sha256 `ed498e7a…590cac`, coincide con el `.sha256` del release) trae
`agua_diario.csv` con 1.052.704 filas de 2015-03-31 a 2025-12-31 para NE, OH y MN. Lo bajé con `curl -L` a
`data/interim/t082/` (fuera de git).

| Condado | Lago | media root | p99 root | máx root | máx surf | días vacíos |
|---|---|---|---|---|---|---|
| St. Louis (27137) | Superior | 0,201 | 0,265 | 0,287 | 0,383 | 0 |
| Lake (27075) | Superior | 0,220 | 0,279 | 0,328 | 0,402 | 0 |
| Cook (27031) | Superior | 0,207 | 0,259 | 0,296 | 0,343 | 0 |
| Carlton (27017) | estuario del St. Louis | 0,160 | 0,241 | 0,257 | 0,375 | 0 |
| Lake of the Woods (27077) | Lake of the Woods | 0,231 | 0,372 | 0,403 | 0,445 | 0 |
| Lucas (39095) | Erie | 0,297 | 0,368 | 0,386 | 0,430 | 0 |
| Ottawa (39123) | Erie | 0,401 | 0,493 | 0,511 | 0,521 | 0 |
| Sandusky (39143) | bahía de Sandusky | 0,357 | 0,440 | 0,452 | 0,483 | 0 |
| Erie (39043) | Erie | 0,322 | 0,399 | 0,410 | 0,438 | 0 |
| Lorain (39093) | Erie | 0,336 | 0,408 | 0,427 | 0,440 | 0 |
| Cuyahoga (39035) | Erie | 0,349 | 0,418 | 0,434 | 0,434 | 0 |
| Lake (39085) | Erie | 0,211 | 0,269 | 0,282 | 0,378 | 0 |
| Ashtabula (39007) | Erie | 0,329 | 0,419 | 0,428 | 0,447 | 0 |

(root = `sm_rootzone_m3m3`, surf = `sm_surface_m3m3`, en m³/m³)

Los condados costeros no se destacan. Los condados con máximos más altos de cada estado son agrícolas del
interior: Pipestone, Faribault y Rock en MN (máx. 0,45), y Paulding, Ottawa y Putnam en OH (0,51). Ottawa es el
único condado sobre el Erie entre los de máximos más altos, y sus celdas están todas por debajo de 0,6 (sección 3).
Con el filtro actual las medias no pueden pasar de 0,6. La pregunta útil es cuánta área saca ese filtro.

## 2. Qué dice la documentación sobre la máscara de agua

- **Crop-CASMA** (metadata de NASS y la página de referencias del User's Guide de GMU): describe las capas
  `SMAPSurface 9km` y `SMAPRootzone 9km` (diarias y semanales) como derivadas de SMAP L4 cada 3 horas. Dice
  que son humedad volumétrica, con profundidades de 5 cm y ~1 m. **No menciona máscara de agua ni de tierra,
  nodata, lagos, turba ni ningún reescalado de la humedad.** Tampoco aclara si la capa diaria es una media de
  las 3-horarias (queda abierto, como ya dice `docs/datasets/agua.md`).
- **SMAP L4 (`SPL4SMGP`), NSIDC:** la versión 7 (retirada; hoy está la 8) incorpora "the PEATCLSM hydrology
  module for peatlands and ... an updated global map of peatland distribution". La página no menciona
  porosidad ni cómo se excluye el agua abierta. **No pude confirmar** en la documentación que las celdas > 0,6
  sean las de turba de PEATCLSM. No leí el User Guide ni el ATBD de L4. El patrón medido es consistente con
  eso, pero es una inferencia: las celdas son fijas en el tiempo, caen en las turberas de MN y del
  Upper Peninsula de MI, nunca bajan de ~0,62 y llegan a 0,93, que es una porosidad típica de turba.
- **Lo que sí se midió:** la máscara de agua ya está aplicada en los GeoTIFF. Las celdas que son
  mayormente lago vienen con `-9999`, y `process.py` ya las descarta (`a != nd`).

## 3. Celdas > 0,6 en un día de muestra (WPS `GetFileByFips`)

Pedí al WPS las capas `SUB` y `TOP` del 2023-07-15 (verano seco) y del 2019-05-01 (primavera húmeda) para MN
(27) y OH (39). Para comparar, pedí el 2023-07-15 de MI (26) e IN (18). Usé los mismos parámetros que
`src/agua/download.py` y guardé los archivos en `data/interim/t082/smap/`. Crucé las celdas con
`cb_2023_us_county_500k` del Census, que tiene la costa recortada: la fracción de tierra de cada celda de 9 km
sale de rasterizar los condados a 900 m.

| Archivo | Celdas válidas | > 0,6 | Máximo |
|---|---|---|---|
| SUB 2019-05-01 MN | 2.658 | 384 | 0,925 |
| SUB 2023-07-15 MN | 2.658 | 384 | 0,823 |
| TOP 2019-05-01 MN | 2.658 | 355 | 0,813 |
| TOP 2023-07-15 MN | 2.658 | 0 | 0,495 |
| SUB 2019-05-01 OH | 1.305 | 23 | 0,930 |
| SUB 2023-07-15 OH | 1.305 | 23 | 0,890 |
| TOP 2019-05-01 OH | 1.305 | 23 | 0,879 |
| TOP 2023-07-15 OH | 1.305 | 1 | 0,619 |
| SUB 2023-07-15 MI | 1.809 | 288 | 0,895 |
| TOP 2023-07-15 MI | 1.809 | 14 | 0,667 |
| SUB 2023-07-15 IN | 1.149 | 67 | 0,901 |
| TOP 2023-07-15 IN | 1.149 | 11 | 0,675 |

- **Las celdas son fijas.** En `SUB` son exactamente las mismas 384 celdas en MN y 23 en OH los dos días,
  con 4 años y estaciones distintas de por medio. Su mínimo en los dos días es 0,621 en MN y 0,815 en OH. En
  `TOP` dependen del día: en un verano seco casi desaparecen.
- **Dónde están (SUB, MN):** Koochiching 63 celdas, St. Louis 49, Beltrami 37, Itasca 32, Aitkin 31,
  Lake of the Woods 22, Otter Tail 20, Cass 15, Pine 13, Roseau 13, Hennepin 9, Le Sueur 8 y otras en 26
  condados más. Sobre el lago Superior, Lake tiene 2 y Cook ninguna. Solo 4 de las 384 celdas tienen menos
  de 95 % de tierra, y las 4 están sobre Lake of the Woods.
- **Dónde están (SUB, OH):** Shelby 5, Darke 4, Auglaize 3, Allen 2, Hardin 2, Union 2, y 1 en Fulton,
  Logan, Mercer, Miami y Williams. Ninguna está sobre el Erie. Una sola celda tiene menos de 95 % de tierra.
- **MI, para comparar:** de 288 celdas, 20 tienen menos de 95 % de tierra. Esas sí son de costa: Chippewa,
  Mackinac, Delta, Alger, Iosco y Muskegon. La mayoría cae en las turberas del Upper Peninsula: Delta 28,
  Menominee 30, Schoolcraft 29, Chippewa 27 y Luce 23. Las 5 celdas válidas con más de 50 % de agua
  llegan a 0,80 en `SUB`. Son la única evidencia de "costa" en sentido estricto, y son pocas.

### Efecto del filtro de 0,6 en la media de condado (SUB, 2023-07-15)

| Condado | Área excluida | Media publicada (sin > 0,6) | Media con todas las celdas − publicada |
|---|---|---|---|
| Koochiching (27071) | 64,7 % | 0,229 | +0,338 |
| Le Sueur (27079) | 48,5 % | 0,247 | +0,241 |
| Aitkin (27001) | 46,3 % | 0,158 | +0,245 |
| Hennepin (27053) | 44,3 % | 0,190 | +0,243 |
| Lake of the Woods (27077) | 42,2 % | 0,214 | +0,219 |
| St. Louis (27137) | 23,1 % | 0,181 | +0,128 |
| Shelby (39149) | 34,2 % | 0,311 | +0,190 |
| Auglaize (39011) | 27,9 % | 0,318 | +0,152 |
| Condados de OH sobre el Erie | 0 % | — | 0 |

Mi media "sin > 0,6" coincide al cuarto decimal con `agua_diario.csv` del release (Koochiching 0,2290;
Le Sueur 0,2467; Shelby 0,3106; Ottawa 0,3665 en surf). Así confirmé que el release aplica el filtro como lo
leí en el código. Con este cálculo de pesos ningún condado de MN ni OH queda sin celdas válidas.

## 4. Conclusión y propuesta (no se cambió `process.py`)

1. **No agregar una máscara de agua.** Crop-CASMA ya trae los lagos como nodata, y en MN y OH las celdas
   costeras con dato tienen valores normales: la mediana de las celdas con 50–95 % de tierra es 0,21–0,45.
2. **El filtro `0 ≤ v ≤ 0,60` cumple §7, pero tiene un sesgo.** En los condados con turba o suelos
   orgánicos saca siempre las mismas celdas, que son las más húmedas. `sm_rootzone_m3m3` queda bajo en
   esos condados, y `dias_sm_saturado` (umbral 0,40) cuenta de menos. Opciones, a decidir por el humano
   (cambian el esquema o el contrato):
   - (a) dejarlo como está y documentar en `docs/datasets/agua.md` que en MN el filtro saca hasta el 65 %
     del área de un condado, con la lista de la sección 3. No cambia el esquema. **Es mi recomendación**,
     junto con (b).
   - (b) agregar una columna `frac_celdas_excluidas` (fracción del área del condado con celdas > 0,6). Es
     estática, así que podría ir en un `agua_estatico.csv` y no en el diario. Cambia el esquema: necesita OK.
   - (c) para la zona radicular, subir el rango físico de `SM_MAX` a ~0,95 (porosidad de turba) y marcar esas
     celdas aparte. Cambia el rango de §7 y de `validar_csv()` (`src/common/`): necesita OK.
3. Si se suma MI (cuarta tanda), aplica lo mismo: las 0,89 de `cuarta_tanda.md` son sobre todo turberas del
   Upper Peninsula, no lago. Solo ~7 % de las celdas > 0,6 de MI son de costa, y ya se excluyen con el
   filtro actual.

Reproducir: `docs/research/smap_costas_celdas.py <dir_tifs> <cb_2023_us_county_500k.zip>` (los tifs se
piden con los parámetros de `src/agua/download.py`).

Fuentes:
- Release `datos-oh-ne-mn`, `datos-oh-ne-mn_agua.zip` (página de releases del repo), consultado 2026-11-15
- [Crop-CASMA WPS `GetFileByFips`](https://cloud.csiss.gmu.edu/smap_service), capas `SMAP-9KM-DAILY-{SUB,TOP}_{2019.05.01,2023.07.15}_013000`, FIPS 18, 26, 27 y 39, consultado 2026-11-15
- [Crop-CASMA metadata (USDA NASS)](https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_cropcasma.htm), consultado 2026-11-15
- [Crop-CASMA User's Guide, referencias (GMU)](https://nassgeo.csiss.gmu.edu/Crop-CASMA-User/user/references/), consultado 2026-11-15
- [NSIDC SPL4SMGP versión 7](https://nsidc.org/data/spl4smgp/versions/7), consultado 2026-11-15
- [US Census Cartographic Boundary `cb_2023_us_county_500k`](https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip), consultado 2026-11-15

Confianza: alta en lo medido (lagos como nodata, celdas fijas > 0,6, medias del release, efecto del filtro).
Media en que las celdas > 0,6 sean turba o suelo orgánico del modelo L4 (PEATCLSM): la documentación no lo
dice explícitamente.

Impacto: `docs/datasets/agua.md` (documentar el área excluida por condado). Si el humano aprueba las opciones
(b) o (c), cambian `src/agua/process.py`, el esquema de `agua` o el rango de `validar_csv()` en `src/common/`.
No hace falta máscara de agua en `src/agua/process.py`.
