# Análogos climáticos: qué provincia argentina se parece más al Corn Belt

Pregunta: ¿en qué provincia argentina se pueden usar los modelos entrenados con los 919 condados del Corn Belt
(IA, IL, IN, OH, NE, MN, MO, WI, SD y KS) sin extrapolar el clima ni el suelo, y qué dan ahí los rendimientos?

Respuesta corta: **Buenos Aires**, con una advertencia sobre los rendimientos.

- **Clima.** Sigue siendo la única provincia con varios departamentos dentro del dominio climático: 12 de 135 en
  todas las variables y 105 con a lo sumo 2 fuera de rango. Lo que entra es el **sur bonaerense**.
- **Kansas** suma Tornquist en Buenos Aires y Hucal y Utracán en La Pampa. Santa Fe y Entre Ríos pasan a tener
  análogos en Kansas, pero la zona núcleo **sigue afuera**: octubres y noviembres más cálidos y marzos más
  lluviosos que cualquier condado.
- **Suelo** (SoilGrids, la misma fuente en los dos lados): casi no cambia el dominio. Los 12 departamentos del sur bonaerense siguen
  adentro con clima + suelo, y en La Pampa quedan 2 de 3. Sus suelos son más arenosos y menos ácidos que los de
  sus condados análogos: 39 % de arena contra 17 % y pH 7,1 contra 5,6. Pero están dentro del rango de los 919
  condados.
- **Rendimientos (MAGyP).**
  - En el sur bonaerense, el que entra por clima, se cosecha **la mitad que en sus condados análogos**: 0,52 en
    maíz y 0,49 en soja.
  - En la zona núcleo, que queda afuera por clima, se cosecha lo mismo que en los suyos (Missouri y Kansas): 0,95
    en maíz y 1,16 en soja.

  Parecerse en clima no alcanza para predecir el rendimiento.
- **Clima por campaña.** `clima_anual_ba.csv` trae los 135 departamentos de Buenos Aires de 2000 a 2025, con las
  mismas columnas que `clima_anual.csv` y la temporada corrida 6 meses. Casi todas caen dentro del rango de los
  condados. Las de helada no:
  - el período libre de heladas es de 291 días contra 180;
  - en 10 a 20 % de los años no hay helada.

  Un modelo que use las variables de helada extrapola en toda la provincia.

Detalle:

## Método

### Clima (similitud)

- **Fuente única**: NASA POWER mensual, comunidad AG, de 2001 a 2024. Se bajó en el centroide de los 529
  departamentos argentinos (API Georef de datos.gob.ar, con el código INDEC) y en el de los 919 condados (los de
  `unido_10_estados`). Se usa la misma fuente y el mismo período en los dos lados, para comparar sin sesgo de
  producto.
- **Temporada alineada por hemisferio**: abril a septiembre en EE.UU. se compara con octubre a marzo en
  Argentina. El mes 4 es julio en EE.UU. y enero en Argentina, la floración del maíz. El invierno previo es
  noviembre a marzo en EE.UU. y mayo a septiembre en Argentina.
- **16 variables de similitud**, elegidas entre las que usan los modelos de rendimiento:
  - temperatura media y lluvia de cada mes de temporada (12);
  - máxima absoluta del mes de floración;
  - lluvia del invierno previo;
  - desvío entre años de la lluvia de la temporada y de la máxima de la temporada.
- **Dos variables quedan fuera de la distancia**, porque en la región pampeana están fuera de rango casi siempre:
  la radiación y la mínima absoluta del primer mes. Se informan aparte como diferencia contra el condado análogo
  (`dif_rad_temporada`, `dif_tmin_abs_t1`).
- **Medidas**:
  - `d_vecino`: distancia RMS, en desvíos de los condados, al condado más parecido.
  - `mahal`: Mahalanobis a la nube de condados, en 5 componentes principales (95 % de la varianza).
  - `n_fuera_rango`: cuántas de las 16 variables quedan fuera del mínimo y el máximo de los condados. Los
    modelos de árboles no extrapolan fuera de ese rango.
  - **Dentro del dominio** = ninguna variable fuera de rango y `mahal` ≤ el percentil 99 de los condados (4,04).

### Suelo

- **Fuente**: ISRIC SoilGrids v2.0, la misma en los dos lados. Es la versión agregada a 1 km
  (`data_aggregated/1000m`, proyección Homolosine). Se usaron arcilla, arena, carbono orgánico y pH en agua, a
  0–5, 5–15 y 15–30 cm.
- **Qué se bajó**: solo la ventana de cada región (pampa y Corn Belt) de los GeoTIFF oficiales, sin cambiar
  valores. Son 24 archivos y 62 MB.
- **Media por polígono**: se promedia cada capa en el polígono y después se pondera por espesor de 0 a 30 cm:
  (5 × [0–5] + 10 × [5–15] + 15 × [15–30]) / 30. Un píxel va al polígono que contiene su centro.
  - Departamentos: los de Buenos Aires, La Pampa, Córdoba, Santa Fe y Entre Ríos, con los polígonos de Georef.
  - Condados: los 919, con los polígonos del Census (Cartographic Boundary 1:500k, 2023).
- **Columnas** (`suelo_sg.csv`): `arcilla_sg_pct`, `arena_sg_pct`, `soc_sg_g_kg` y `ph_sg`. El sufijo `_sg`
  las separa de las de gSSURGO del paquete `suelo_terreno`, que son otra fuente con otros valores.
- **Clima + suelo**: las 16 variables de clima más las 4 de suelo, con las mismas medidas. Hay 7 componentes
  principales y el límite de Mahalanobis (percentil 99) es 4,48. Las columnas llevan el sufijo `_cs`; el
  clima solo no cambia.

### Rendimientos

- **Fuente**: Estimaciones agrícolas del MAGyP, el CSV consolidado (`estimaciones-agricolas-2026-03.csv`, de
  datos.magyp.gob.ar). Es por departamento y campaña, con superficie sembrada y cosechada, producción y
  rendimiento.
- **Qué se usa**: maíz, "soja total" (1.ª más 2.ª) y "trigo total", campañas 2000/01 a 2024/25. Son 19.351
  filas de 338 departamentos.
- **`anio`** = año de cosecha = el segundo año de la campaña (2023/2024 → 2024). Es el mismo corrimiento que el
  clima.
- **Ceros**: los rendimientos 0 (213, casi todos con superficie cosechada 0) van vacíos, con `flag_magyp` =
  `0_sin_cosecha`. Es la regla de NASS (T148).
- **Comparación con EE.UU.**: para cada departamento y cultivo, la mediana 2001–2024 del MAGyP contra la
  distribución de rendimientos de NASS 2001–2024 (`rend_kgha`) de sus 3 condados análogos de clima. El trigo se
  compara con el trigo de invierno.

### Clima por campaña (Buenos Aires)

- **Fuente**: NASA POWER diario, comunidad AG, de 1981 a 2025, con los mismos 10 parámetros que el paquete
  `clima`. Se bajó en el centroide de los 135 departamentos.
- **Cálculo**: el mismo código que el paquete `clima` (ETo FAO-56, GDD 10–30 °C, umbrales), importado de
  `src/clima/process.py`.
- **Corrimiento de 6 meses**: cada mes real se cuenta como el que está 6 lugares después, y julio a diciembre
  pasan al año siguiente. Con `anio` = 2024:

  | Columna (nombre de EE.UU.) | Meses reales en Argentina |
  |---|---|
  | temporada (`prec_temporada_mm`, `gdd_temporada`, `deficit_temporada_mm`) | octubre de 2023 a marzo de 2024 |
  | invierno previo (`prec_invierno_previo_mm`) | mayo a septiembre de 2023 |
  | `prec_jul_mm`, `tmax_jul_c`, `dias_tmax_gt30_jul` (floración del maíz) | enero de 2024 |
  | `prec_ago_mm` (llenado de la soja) | febrero de 2024 |
  | `doy_ultima_helada`, `doy_primera_helada` | día 1 = 1 de julio de 2023 |
  | tendencias por década | años de julio a junio |

- **Diferencia de días**: un `doy` corrido difiere de 0 a 3 días de uno de EE.UU. Julio a diciembre suman 184
  días; enero a junio, 181 o 182.

## Resultados

### Clima: por provincia (núcleo agrícola), con Kansas

| Provincia | Departamentos | Dentro del dominio | Con ≤ 2 fuera de rango | Fuera de rango (mediana) | Estado análogo más común | Δ radiación (MJ/m²/día) |
|---|---|---|---|---|---|---|
| Buenos Aires | 135 | 12 (antes 11) | 105 (104) | 2 | MO (87), OH (34) | +2,92 |
| La Pampa | 22 | 3 (1) | 12 (11) | 2 (2,5) | OH (9), KS (8) | +3,67 |
| Córdoba | 26 | 0 | 0 | 4 | MO (16), KS (5) | +2,90 |
| Santa Fe | 19 | 0 | 0 | 5 | KS (14), MO (5) | +2,37 |
| Entre Ríos | 17 | 0 | 0 | 6 | KS (16) | +1,99 |

- Entre paréntesis, el valor sin Kansas, de la versión anterior.
- **Entran por Kansas**: Tornquist (Buenos Aires; análogo Thomas, KS), Hucal (análogo Gove, KS) y Utracán (La
  Pampa).
- **Lo que deja afuera a la zona núcleo**: Kansas no tiene octubres tan cálidos ni marzos tan lluviosos. La
  temperatura de octubre queda fuera de rango en el 100 % de los departamentos de Córdoba, Santa Fe y Entre
  Ríos, y la lluvia de marzo en el 88–100 %. En Buenos Aires, la lluvia de marzo queda afuera en el 88 % y la
  temperatura de octubre en el 64 %.
- Tabla completa: `data/processed/analogos/analogos_provincia.csv`. Mapa: `fig/analogos_argentina.png`.

### Suelo

| Provincia | Con suelo | Dentro del dominio, clima | Dentro, clima + suelo | Con ≤ 2 fuera de rango, clima + suelo | Con alguna variable de suelo fuera de rango |
|---|---|---|---|---|---|
| Buenos Aires | 134 de 135 | 12 | 12 | 102 | 3 |
| La Pampa | 22 | 3 | 2 | 12 | 7 |
| Córdoba | 26 | 0 | 0 | 0 | 0 |
| Santa Fe | 19 | 0 | 0 | 0 | 0 |
| Entre Ríos | 17 | 0 | 0 | 0 | 1 |

- **Vicente López** (urbano) no tiene dato de SoilGrids.
- **Fuera de rango por suelo**: sobre todo en La Pampa, con pH más alto (7 departamentos) y menos carbono (5).
  En Buenos Aires son pocos. Utracán (La Pampa) sale del dominio por la distancia de Mahalanobis, no por una
  variable fuera de rango.
- **Rango de los condados**: arcilla de 8,7 a 52,2 %, arena de 2,6 a 74,1 %, carbono de 8,3 a 51,0 g/kg y pH de
  5,0 a 7,7.
- **Comparación con el condado análogo de clima** (medianas):

  | Departamentos de Buenos Aires | Arena AR / análogo | pH AR / análogo | Carbono AR / análogo (g/kg) |
  |---|---|---|---|
  | 0 fuera de rango | 39 % / 17 % | 7,1 / 5,6 | 23 / 24 |
  | 1–2 fuera de rango | 32 % / 12 % | 7,0 / 5,9 | 24 / 16 |
  | 3 o más (zona núcleo) | 19 % / 11 % | 6,5 / 6,1 | 19 / 16 |

  Cuanto más al sur, más se aleja el suelo del de su análogo de clima.

### Rendimientos: MAGyP contra los condados análogos

Mediana por departamento de la razón entre el rendimiento argentino y el de sus condados análogos (mediana
2001–2024 de cada lado):

| Provincia | Maíz | Soja | Trigo |
|---|---|---|---|
| Buenos Aires | 0,88 | 0,99 | 1,03 |
| La Pampa | 0,51 | 0,62 | 0,63 |
| Córdoba | 0,80 | 0,92 | 0,68 |
| Santa Fe | 1,00 | 1,37 | 0,87 |
| Entre Ríos | 0,90 | 1,33 | 0,96 |

En Buenos Aires, según cuántas variables de clima quedan fuera de rango:

| Departamentos | n | Maíz AR / EE.UU. (kg/ha) | Razón | Soja AR / EE.UU. | Razón | Trigo AR / EE.UU. | Razón |
|---|---|---|---|---|---|---|---|
| 0 (dentro del dominio) | 12 | 4.625 / 9.205 | 0,52 | 1.550 / 3.218 | 0,49 | 2.764 / 4.052 | 0,75 |
| 1–2 | 66 | 7.125 / 8.474 | 0,83 | 2.716 / 2.858 | 0,96 | 3.650 / 3.514 | 1,04 |
| 3 o más (zona núcleo) | 25 | 8.150 / 8.374 | 0,95 | 3.252 / 2.816 | 1,16 | 3.950 / 3.416 | 1,15 |

- **El sur bonaerense rinde la mitad que sus análogos** del este de Ohio y del oeste de Kansas. Lo más probable
  es que la diferencia venga de lo que la similitud de clima no mide:
  - más demanda de agua: más radiación y viento, con un déficit de temporada mediano de −295 mm contra −150 mm
    en los condados;
  - suelos con tosca;
  - menos insumos.

  Es una hipótesis, no está medida acá.
- **La zona núcleo** rinde lo mismo que sus análogos de Missouri y Kansas, aunque está fuera del dominio
  climático.
- Archivos: `rendimiento_ar.csv` (19.351 filas) y `rendimiento_comparacion.csv` (por departamento y cultivo,
  con p10, mediana y p90 de los condados y el percentil del rendimiento argentino en esa distribución).

### Clima por campaña de Buenos Aires contra los condados

`clima_anual_ba.csv`: 3.510 filas (135 departamentos × 26 años). Comparación 2001–2024 contra los 919 condados:

| Columna | Mediana EE.UU. | p1–p99 EE.UU. | Mediana Buenos Aires | % de años de BA dentro de p1–p99 |
|---|---|---|---|---|
| `prec_temporada_mm` | 561 | 250–970 | 599 | 95 |
| `gdd_temporada` | 1.802 | 1.104–2.308 | 1.936 | 99 |
| `prec_invierno_previo_mm` | 214 | 39–607 | 269 | 100 |
| `prec_jul_mm` | 89 | 17–224 | 96 | 97 |
| `tmax_jul_c` | 29,9 | 24,0–38,3 | 31,3 | 99 |
| `prec_ago_mm` | 85 | 17–233 | 103 | 95 |
| `deficit_temporada_mm` | −150 | −897 a 320 | −295 | 98 |
| `doy_ultima_helada` | 113 | 70–141 | 54 | 18 |
| `doy_primera_helada` | 294 | 271–326 | 347 | 10 |
| `periodo_libre_heladas_dias` | 180 | 137–234 | 291 | 4 |

- Hay años sin helada: `doy_ultima_helada` queda vacío en el 10 % de los años y `doy_primera_helada` en el
  18 %. En los condados no pasa nunca.
- Las tendencias del anio 2000 van vacías. El primer año corrido completo es 1982 (julio de 1981 a junio de
  1982), así que al 2000 le faltan años para llegar al mínimo de 20 de la ventana.

## Qué implica para los modelos

1. **Provincia para la demo: Buenos Aires.** Pero conviene mostrar la zona núcleo y el sur por separado.
   - En el sur el clima entra en el dominio, pero el rendimiento es la mitad. Un modelo entrenado en el Corn
     Belt lo sobreestimaría si no tiene variables de suelo y de demanda de agua.
   - En la zona núcleo el rendimiento coincide con el de sus análogos, pero el clima está 3 a 5 variables fuera
     de rango.
2. **Variables que no conviene usar en Argentina**, o que hay que recortar al rango del Corn Belt:
   - las de helada (`doy_*_helada`, `periodo_libre_heladas_dias`);
   - la radiación.
3. **El suelo de SoilGrids no saca a nadie del dominio**, pero en el sur bonaerense es más arenoso que el de
   sus análogos de clima. SoilGrids no tiene la profundidad de la tosca, que es la limitante conocida del
   sudeste y el sudoeste bonaerense.
4. **Para correr un modelo por campaña** en Buenos Aires ya están el clima anual (`clima_anual_ba.csv`) y el
   suelo (`suelo_sg.csv`). Los rendimientos del MAGyP (`rendimiento_ar.csv`) sirven como validación.
   - Las columnas de clima tienen los mismos nombres que en EE.UU.
   - El suelo es de SoilGrids, no de gSSURGO. Un modelo que quiera usar el suelo en los dos lados tiene que
     entrenarse con las columnas `_sg` de los condados, que también están en `suelo_sg.csv`.

## Supuestos

- Cada departamento y cada condado se representa por el punto de POWER de su centroide, en una grilla de
  0,5° × 0,625°. Eso vale para la similitud y para el clima por campaña.
- El `anio` del MAGyP es el segundo año de la campaña también para el trigo, aunque la cosecha del trigo cae
  entre noviembre y enero. Así el anio es el mismo en los tres cultivos y coincide con el invierno previo
  (mayo a septiembre del anio − 1).
- Chascomús viene en el MAGyP con el código 06217, anterior a la creación de Lezama (2009). Se recodificó a
  06218, el código de Georef, con `flag_magyp` = `codigo_06217`: su área incluye a Lezama.
- Las filas del MAGyP "sin definir" (código terminado en 000) no son un departamento y quedan afuera.
- El trigo argentino se compara con el trigo de invierno de NASS. Los dos se siembran en otoño o invierno y se
  cosechan al comienzo del verano.
- El suelo se representa con la media 0–30 cm de SoilGrids a 1 km.
  - SoilGrids no informa la profundidad efectiva ni la tosca.
  - En los partidos urbanos del Gran Buenos Aires, 28 departamentos tienen menos del 80 % de los píxeles con dato
    (Vicente López, ninguno). Lo mismo pasa en algunos condados urbanos de EE.UU., como St. Louis City, Cook y
    Milwaukee. La media usa solo los píxeles con dato; `frac_pixeles_validos` lo indica.

## Limitaciones

- En el 69 % de los condados, el condado más parecido tiene un clima idéntico porque cae en la misma celda de
  POWER. Por eso no se usa la distancia al vecino como umbral.
- Hay departamentos grandes y heterogéneos (Patagonia, Chaco) que un solo punto no representa bien. En la región
  pampeana, los departamentos son de tamaño parecido a los condados.
- `T2M_MAX` y `T2M_MIN` de POWER mensual son la máxima y la mínima absolutas del mes, no la media de las
  máximas.
- El clima por campaña no tiene IMERG: la lluvia es la de POWER (`PRECTOTCORR`). En EE.UU., `prec_temporada_mm`
  también sale de POWER.
- La comparación de rendimientos es de niveles, no una validación de un modelo. El rendimiento depende también
  del manejo, la genética, la fecha de siembra y los precios, y NASS y el MAGyP los estiman con métodos
  distintos.

Fuentes:

- [NASA POWER API, temporal monthly y daily](https://power.larc.nasa.gov/docs/services/api/), consultado
  2026-11-15
- [API Georef, departamentos y departamentos.geojson](https://apis.datos.gob.ar/georef/api/departamentos),
  consultado 2026-11-15
- [MAGyP, Estimaciones agrícolas (datos abiertos)](https://datos.magyp.gob.ar/dataset/estimaciones-agricolas),
  CSV `estimaciones-agricolas-2026-03.csv`, consultado 2026-11-15
- [ISRIC SoilGrids v2.0, data_aggregated 1000 m](https://files.isric.org/soilgrids/latest/data_aggregated/),
  CC-BY 4.0, consultado 2026-11-15
- [US Census Bureau, Cartographic Boundary Files 2023, counties 1:500k](https://www2.census.gov/geo/tiger/GENZ2023/shp/),
  consultado 2026-11-15
- Código: `src/analogos/` (`download.py`, `process.py`, `suelo.py`, `rendimiento.py`, `clima_ba.py`, `figura.py`).
  Los datos quedan en `data/raw/analogos/` y `data/processed/analogos/`, fuera de git.

Confianza:

- **alta** en el ranking climático y en el clima por campaña: una sola fuente, el mismo código que el paquete
  `clima`;
- **alta** en los rendimientos del MAGyP, que es el dato oficial;
- **media** en la comparación de rendimientos, por los métodos distintos y porque falta el manejo;
- **media** en el suelo: SoilGrids es un modelo global a 1 km, con errores conocidos a escala de lote,
  aunque la fuente es la misma en los dos lados.

Impacto: ninguno en `config/`. Define la provincia de la demo de escalabilidad (Buenos Aires, sur y zona núcleo
por separado). Deja listos el clima anual por campaña, el suelo y los rendimientos de Buenos Aires para correr
y validar los modelos.
