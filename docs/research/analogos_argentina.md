# Análogos climáticos: qué provincia argentina se parece más al Corn Belt

Pregunta: ¿en qué provincia argentina se pueden usar los modelos entrenados con los 814 condados del Corn Belt
(IA, IL, IN, OH, NE, MN, MO, WI, SD) sin extrapolar el clima?

Respuesta corta: **Buenos Aires**.

- Es la única provincia con departamentos dentro del dominio climático de los condados: 11 de 135 en todas las
  variables, y 104 de 135 con a lo sumo 2 variables fuera de rango.
- Lo que entra es el **sur bonaerense**: Tres Arroyos, Necochea, Lobería, Adolfo Gonzales Chaves, Coronel
  Pringles, Coronel Suárez, Coronel Dorrego, San Cayetano, Saavedra, Puán y Bahía Blanca, además de Guatraché en
  La Pampa. Sus condados análogos están en el este de Ohio.
- La zona núcleo (norte de Buenos Aires, sur de Santa Fe, sureste de Córdoba y Entre Ríos) **no** entra. Tiene
  octubres y noviembres más cálidos y marzos más lluviosos que cualquier condado. Su análogo más cercano es
  Missouri.
- Dos diferencias valen para toda la región pampeana:
  - **más radiación**: unos +2 a +4 MJ/m²/día en la temporada;
  - **primaveras sin heladas fuertes**: la mínima absoluta del primer mes es unos 7 °C más alta.

  Un modelo que use esas variables extrapola en toda la región.

Detalle:

## Método

- **Fuente única**: NASA POWER mensual, comunidad AG, de 2001 a 2024. Se bajó en el centroide de los 529
  departamentos argentinos (API Georef de datos.gob.ar, con el código INDEC) y en el de los 814 condados (los de
  `unido_9_estados`). Se usa la misma fuente y el mismo período en los dos lados, para comparar sin sesgo de
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
  - **Dentro del dominio** = ninguna variable fuera de rango y `mahal` ≤ el percentil 99 de los condados (4,09).

## Resultados por provincia (núcleo agrícola)

| Provincia | Departamentos | Dentro del dominio | Con ≤ 2 fuera de rango | Fuera de rango (mediana) | Estado análogo más común | Δ radiación (MJ/m²/día) | Δ mín. abs. mes 1 (°C) |
|---|---|---|---|---|---|---|---|
| Buenos Aires | 135 | 11 | 104 | 2 | MO (85), OH (35) | +2,99 | +6,81 |
| La Pampa | 22 | 1 | 11 | 2,5 | OH (9), NE (8) | +3,80 | +6,57 |
| Córdoba | 26 | 0 | 0 | 4 | MO (20) | +3,01 | +7,51 |
| Santa Fe | 19 | 0 | 0 | 5 | MO (19) | +2,39 | +8,52 |
| Entre Ríos | 17 | 0 | 0 | 6 | MO (17) | +2,13 | +7,88 |

Fuera de estas cinco, solo San Luis (mediana de 3) y la Ciudad de Buenos Aires (2, no agrícola) tienen una
mediana menor que 6 variables fuera de rango. La tabla completa, con las 24 jurisdicciones, está en `data/processed/analogos/analogos_provincia.csv`. El mapa está en
`fig/analogos_argentina.png`.

Variables que más quedan fuera de rango (% de departamentos de cada provincia):

- **Buenos Aires**: lluvia de marzo (88 %) y temperatura de octubre (64 %).
- **Córdoba**: temperatura de octubre (100 %), lluvia de marzo (88 %), temperatura de noviembre (85 %) y lluvia de
  enero (65 %).
- **Santa Fe y Entre Ríos**: temperatura de octubre y de noviembre y lluvia de marzo (100 %), más la
  variabilidad de la lluvia de la temporada.

## Qué implica para los modelos

1. **Provincia para la demo: Buenos Aires.** Con el sur bonaerense como zona donde el modelo se usa sin
   extrapolar el clima, y el resto de la provincia con 1 o 2 variables fuera de rango, marcadas.
2. Si el modelo se va a aplicar en Argentina, conviene entrenarlo sin la radiación ni las variables de helada de
   primavera, o con esas variables recortadas al rango del Corn Belt, y decirlo.
3. La zona núcleo se parece más a Missouri que al resto. Kansas, que se está procesando (T013), puede ampliar el
   dominio hacia primaveras más cálidas: conviene repetir este análisis cuando esté.
4. Falta el suelo y el rendimiento. El próximo paso es comparar suelos con la misma fuente en los dos lados
   (SoilGrids) y validar contra rendimientos por departamento del MAGyP.

## Limitaciones

- Cada departamento y cada condado se representa por el punto de POWER de su centroide, en una grilla de
  0,5° × 0,625°. En el 71 % de los condados, el condado más parecido tiene clima idéntico porque cae en la misma
  celda. Por eso no se usa la distancia al vecino como umbral.
- Hay departamentos grandes y heterogéneos (Patagonia, Chaco) que un solo punto no representa bien. En la región
  pampeana, los departamentos son de tamaño parecido a los condados.
- `T2M_MAX` y `T2M_MIN` de POWER mensual son la máxima y la mínima absolutas del mes, no la media de las
  máximas.
- Es clima de 2001 a 2024, no un año en particular. Para correr los modelos por campaña hace falta el clima
  diario de cada año (mismo paquete `clima`).

Fuentes:

- [NASA POWER API, temporal monthly](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/), consultado
  2026-11-15
- [API Georef, departamentos](https://apis.datos.gob.ar/georef/api/departamentos), consultado 2026-11-15
- Código: `src/analogos/download.py` y `src/analogos/process.py`. Los datos quedan en `data/raw/analogos/`, fuera
  de git.

Confianza: **alta** en el ranking climático (una sola fuente, medida); **media** en lo que implica para el
rendimiento, porque faltan suelo y validación con rendimientos argentinos.

Impacto: ninguno en `config/`. Define la provincia de la demo de escalabilidad (Buenos Aires) y el próximo paso
del paquete argentino (suelo SoilGrids, rendimientos MAGyP y clima diario).
