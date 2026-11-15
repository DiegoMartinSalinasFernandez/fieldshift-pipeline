# Fechas de MOD13Q1 que faltan en 2023–2025 (Planetary Computer vs. LP DAAC)

Pregunta: en `vegetacion_16d.csv` hay 22 fechas en 2023, 21 en 2024 y 15 en 2025 (lo normal son 23), en IA/IL/IN
y en OH/NE/MN, y la tesela h09v05 no aparece en 2023–2024. ¿Qué compuestos y teselas faltan? ¿Faltan en la
fuente (LP DAAC, por ejemplo por un problema de Terra) o solo en Planetary Computer? ¿Se pueden bajar de otro
lado sin Earthdata?

Respuesta corta:
- **Faltan 11 compuestos, y faltan solo en Planetary Computer (PC).** LP DAAC publica los 23 compuestos de cada
  año de 2001 a 2025 para las 6 teselas de los 7 estados. En PC faltan:
  - 2023: `A2023049` (18-feb a 5-mar);
  - 2024: `A2024225` (12 a 27-ago) y `A2024353` (18-dic a 2-ene);
  - 2025: `A2025193` a `A2025305`, 8 compuestos seguidos (12-jul a 16-nov).
  Los conteos coinciden exactamente con los del CSV: 22, 21 y 15. De 2000 a 2022 PC y CMR coinciden compuesto por
  compuesto y tesela por tesela (2000 tiene 20 porque MODIS empieza el 18-feb).
- **No es un problema de Terra.** En CMR los gránulos faltantes existen, con fechas de producción normales
  (unas 2–3 semanas después del compuesto, como el resto). En PC faltan **en todo el mundo**, no solo en el Corn
  Belt: es un hueco de ingesta de PC. En 2025 el hueco afecta también a Aqua (`MYD13Q1`, `A2025185` a
  `A2025313`). PC sigue ingiriendo: tiene 2026 completo hasta `A2026289`.
- **h09v05 no falta en 2023–2024.** PC la tiene todos los años (2000–2025) con las mismas fechas que las
  demás teselas. Con los bbox por estado de `download.py` (desde T023), h09v05 solo cae en el bbox de **KS**:
  ni IA/IL/IN, ni OH, ni NE, ni MN la tocan, en ningún año. Si en algún CSV aparece h09v05 en 2000–2022 y no
  en 2023–2024, la diferencia viene de cómo se bajó cada tramo (por ejemplo, el bbox único de los 7 estados de
  antes de T023), no de la fuente. No lo pude confirmar porque esta máquina no tiene los datos crudos.
- **Sí se pueden bajar sin Earthdata:** el servicio web de MODIS de ORNL DAAC
  (`https://modis.ornl.gov/rst/api/v1/`) sirve MOD13Q1 v061 sin login y tiene los 11 compuestos. Tiene
  límites (ventana de ±100 km alrededor de un punto y 10 compuestos por pedido), así que sirve para
  rellenar estos 11 compuestos, no para bajar todo. Las demás vías (LP DAAC Data Pool / Earthdata Cloud,
  OPeNDAP, AppEEARS) piden login de Earthdata. Google Earth Engine (`MODIS/061/MOD13Q1`) pide una
  cuenta de Google con Earth Engine habilitado; no lo verifiqué.

Detalle:

## 1. Cómo se comparó

`docs/research/modis_fechas.py` (solo metadatos, no baja nada) pide para cada año:
- a PC la misma búsqueda STAC que `src/vegetacion/download.py` (colección `modis-13Q1-061`, ítems `MOD13Q1.*`);
- a CMR `granules.json?short_name=MOD13Q1&version=061`, sin login;

las dos con un bbox que cubre los 7 estados (`-104.11, 36.94, -80.47, 49.44`, con el margen de 0,05° de
`download.py`). Cuenta solo los compuestos que empiezan en ese año (la búsqueda temporal también devuelve el
compuesto del 18 o 19 de diciembre del año anterior, que cruza el año). La salida completa de 2000–2025 está
en `docs/research/modis_fechas.txt`.

| Año | Compuestos PC | Compuestos CMR | Teselas (las dos) | Faltan en PC |
|---|---|---|---|---|
| 2000 | 20 | 20 | 6 | — |
| 2001–2022 | 23 | 23 | 6 | — |
| 2023 | 22 | 23 | 6 | A2023049 |
| 2024 | 21 | 23 | 6 | A2024225, A2024353 |
| 2025 | 15 | 23 | 6 | A2025193, 209, 225, 241, 257, 273, 289, 305 |

Las 6 teselas son h09v05, h10v04, h10v05, h11v04, h11v05 y h12v04. Cuando falta un compuesto, falta en las 6.

## 2. El hueco es de PC, no de la fuente

- **En CMR los gránulos existen y se produjeron a tiempo.** Por ejemplo:
  `MOD13Q1.A2023049.h10v04.061.2023070134934` (producido el 11-mar-2023),
  `MOD13Q1.A2024225.h10v04.061.2024247122213` (producido el 3-sep-2024),
  `MOD13Q1.A2025225.h10v04.061.2025245173723` (producido el 2-sep-2025). Es el mismo ritmo que los compuestos
  vecinos (`A2023033` se produjo el 23-feb-2023). Un problema del satélite se vería como un compuesto ausente o
  demorado en LP DAAC, y no es el caso.
- **En PC faltan en todo el mundo.** Una búsqueda sin bbox en PC alrededor de cada hueco da:
  - feb–mar 2023: `MOD13Q1.A2023033` y `A2023065` con 294 teselas cada uno; `A2023049` no está;
  - ago–sep 2024: `A2024209` y `A2024241` con 294 teselas; `A2024225` no está;
  - dic 2024: `A2024337` con 274 teselas y `A2024353` con **1** sola tesela (ninguna del Corn Belt);
  - jul–nov 2025: solo `MOD13Q1.A2025177`, `A2025321`, `MYD13Q1.A2025169` y `A2025329`. Faltan los 8
    compuestos de Terra y también los de Aqua en el medio.
- La colección de PC declara extensión temporal `2000-02-18 / abierta` y sigue al día (2026 completo hasta
  `A2026289`). Es decir, PC saltó esos compuestos y no los cargó después.

**Duplicados en PC (aviso, no es un problema hoy).** PC tiene a veces dos o tres versiones de producción del
mismo compuesto y tesela (por ejemplo, `MOD13Q1.A2021257.h11v04.061.2021279212525`, `…2021316084238` y
`…2021320112538`). `download.py` baja todas, pero `process.py` (línea 134) se queda con la más reciente, así
que no se duplican filas. Con el bbox de un estado, los conteos crudos por tesela dan 25 o 26 ítems por año;
no hay que tomarlos como fechas.

## 3. h09v05

Búsqueda STAC de PC con un bbox por estado (aproximado al de `grupos_bbox()`, con margen), compuestos `MOD13Q1`
por tesela:

| Grupo | Teselas que devuelve PC (2020–2025) |
|---|---|
| IA+IL+IN | h10v04, h10v05, h11v04, h11v05 |
| OH | h11v04, h11v05, h12v04 |
| NE | h10v04, h10v05, h11v04 |
| MN | h11v04, h12v04 (h10v04 aparece suelta en 2021 y 2025, por ítems con huellas mal calculadas) |
| KS | **h09v05**, h10v04, h10v05 |

En la proyección sinusoidal, el borde entre h09 y h10 está en unos −104,4° a 40°N y en unos −100,2° a 37°N.
Por eso solo el oeste de Kansas cae en h09v05. NE empieza en 40°N y, a esa latitud, termina antes de −104°.
h09v05 está en PC todos los años con los mismos compuestos que las demás teselas (22, 21 y 15 en 2023–2025).
Entonces la falta de h09v05 en 2023–2024 de un CSV de IA/IL/IN u OH/NE/MN no indica un faltante:
esos estados no la necesitan. Si la máquina de KS ve que le falta h09v05, hay que revisar su `raw/`
o el log de descarga (`data/interim/vegetacion/download.log`), porque en PC está.

## 4. De dónde bajar los 11 compuestos sin Earthdata

| Vía | ¿Login? | ¿Tiene los 11? | Notas |
|---|---|---|---|
| ORNL DAAC MODIS Web Service (`modis.ornl.gov/rst/api/v1/MOD13Q1/subset`) | No | Sí (`/dates` lista `A2023049`, `A2024225`, `A2024353`, `A2025193`…`A2025305`; probé un pixel en Story, IA: `A2023049` da NDVI 2775 ×0,0001, y `A2025193`…`A2025305` dan 7767, 7739, 7562, 6977, 5003, 5295, 5752 y 5230, tesela h11v04, con fechas de producción iguales a las de LP DAAC) | Máximo ±100 km alrededor de un punto y 10 compuestos por pedido (los dos límites se comprobaron: la API devuelve error si se pasan). Una banda por pedido. Devuelve JSON con valores en la grilla sinusoidal nativa (231,66 m) |
| LP DAAC Data Pool / Earthdata Cloud (`data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/…`) | Sí, Earthdata | Sí | Es la fuente oficial (HDF4). Los enlaces salen en CMR |
| OPeNDAP de Earthdata | Sí | Sí | |
| AppEEARS | Sí | Sí | Además va en cola |
| Google Earth Engine `MODIS/061/MOD13Q1` | Cuenta de Google con Earth Engine | No verificado | |

Con ORNL, cada condado se cubre con un pedido centrado en su centroide (los condados del Corn Belt miden
menos de 200 km de lado). Serían 11 compuestos × 3 bandas (NDVI, EVI, pixel reliability) por condado: unos
2 pedidos por banda y condado, es decir, unos 6 por condado. Para los 666 condados son unos 4.000 pedidos
chicos. Otra opción, más simple porque usa el mismo `download.py`, es usar Earthdata en una máquina que ya
tenga `~/.netrc` (ver "Impacto").

## Propuesta (para decidir)

1. **Rellenar los 11 compuestos desde LP DAAC con Earthdata**: un modo de `download.py` que, para los
   compuestos que CMR tiene y PC no, baje el HDF de `lp-prod-protected` (con `~/.netrc`) y lo recorte igual
   que a los COG de PC. Es la opción más fiel (mismo producto y versión). Volumen: 11 compuestos × 6 teselas
   = 66 HDF de unos 100–200 MB, o sea unos 7–13 GB en total. **Supera los 5 GB: necesita el OK del humano.**
   Se puede bajar a la mitad haciéndolo por máquina, solo con sus teselas.
2. **Sin Earthdata**: rellenar desde la API de ORNL por condado (pedidos de ±100 km). Es más lento y cambia
   la grilla de lectura (JSON en sinusoidal en lugar de COG), así que conviene una función aparte en
   `src/vegetacion/` y anotarlo en el data card.
3. **Mientras tanto**, anotar en `docs/datasets/vegetacion.md` (Problemas conocidos) los 11 compuestos que
   faltan y que el hueco de jul–nov 2025 deja sin datos de la temporada de crecimiento de 2025 a `ndvi_max`,
   `doy_pico`, `doy_fin`, `ndvi_integral` y las medias mensuales de jul–nov 2025.
4. Volver a correr `modis_fechas.py` antes de rellenar: si PC carga los compuestos más adelante, alcanza con
   volver a correr `download.py` (es idempotente y baja solo lo que falta).

Fuentes:
- [Planetary Computer STAC, colección modis-13Q1-061](https://planetarycomputer.microsoft.com/api/stac/v1/collections/modis-13Q1-061), consultado 2026-11-15
- [NASA CMR, búsqueda de gránulos (MOD13Q1 v061, sin login)](https://cmr.earthdata.nasa.gov/search/granules.json?short_name=MOD13Q1&version=061), consultado 2026-11-15
- [ORNL DAAC MODIS Web Service](https://modis.ornl.gov/data/modis_webservice.html) (API `https://modis.ornl.gov/rst/api/v1/`), consultado 2026-11-15
- [LP DAAC, MOD13Q1 v061 (DOI 10.5067/MODIS/MOD13Q1.061)](https://doi.org/10.5067/MODIS/MOD13Q1.061), consultado 2026-11-15
- Salida completa: `docs/research/modis_fechas.txt` (de `docs/research/modis_fechas.py`)

Confianza: alta sobre qué compuestos faltan y que faltan solo en PC (comparación directa de catálogos, que
coincide con los conteos del CSV). Media sobre el origen de la observación de h09v05 (no tengo los datos
crudos de las otras máquinas). Baja sobre el tamaño de los HDF (estimado, no medido).

Impacto: `src/vegetacion/download.py` (relleno desde LP DAAC u ORNL), `docs/datasets/vegetacion.md`
(problemas conocidos) y, después de rellenar, `vegetacion_16d.csv`, `vegetacion_mensual.csv` y
`fenologia_anual.csv` de 2023–2025 en todos los estados.
