# Compuestos de MOD11A2 (LST) que faltan en Planetary Computer, 2000–2025

Pregunta: `docs/research/modis_fechas.md` (T090) encontró 11 compuestos de MOD13Q1 que faltan en Planetary
Computer (PC) en todo el mundo. ¿Pasa lo mismo con MOD11A2 v061 (LST de 8 días, colección `modis-11A2-061`), que
usa `vegetacion` para `lst_dia_c` y `lst_noche_c`? ¿Qué compuestos de 2000–2025 faltan en PC contra CMR de LP
DAAC, para las teselas de los 10 estados? ¿Qué hay que sumar al relleno de T100?

Respuesta corta:
- **Sí, y el hueco es más grande que el de MOD13Q1: faltan 20 compuestos enteros y otros 3 en parte de las
  teselas.** De 2000 a 2021 PC y CMR coinciden compuesto por compuesto y tesela por tesela. Desde 2022 faltan en
  PC (en las 6 teselas, salvo donde se indica):
  - 2022: `A2022273` (h11v04, h11v05, h12v04), `A2022281` (h09v05, h10v04), `A2022297` (h09v05, h10v04, h10v05),
    y enteros `A2022337` y `A2022345`;
  - 2023: `A2023001` y `A2023057`;
  - 2024: `A2024121` y `A2024361`;
  - 2025: `A2025185` a `A2025321`, **18 compuestos seguidos** (4-jul a 24-nov).
  En gránulos: 20 × 6 + 8 = **128 gránulos** (tesela × compuesto) que están en CMR y no en PC.
- **Los huecos son de PC, no de la fuente.** En CMR los gránulos existen, con fechas de producción normales
  (1–3 semanas después del compuesto). En PC faltan o están incompletos **en todo el mundo**, no solo en el Corn
  Belt (sección 2).
- **Huecos que sí son de la fuente (no se pueden rellenar):** `A2000001` a `A2000041` (MODIS empieza el
  18-feb-2000; 2000 tiene 40 compuestos), `A2001169` (falta en todas las teselas; Terra estuvo en modo seguro en
  junio–julio de 2001), `A2001177` (solo en h09v05, h10v04 y h11v04) y `A2022289` (falta en las 6 teselas en
  CMR). PC y CMR coinciden en estos.
- **Coincidencias con MOD13Q1:** el hueco de jul–nov 2025 es el mismo (en los dos productos y también en Aqua,
  `MYD11A2`); los de 2022–2024 son otros compuestos.
- **Para el relleno:** 128 HDF de 4,7 a 8,7 MB (media 7,2 MB, según `granule_size` de CMR): **unos 0,9 GB** para
  los 10 estados, muy por debajo del límite de 5 GB. La API de ORNL DAAC (sin login) también tiene todos los
  compuestos faltantes salvo `A2022289`, que tampoco está en LP DAAC.

Detalle:

## 1. Cómo se comparó

`docs/research/modis_fechas.py` ahora acepta el producto y el bbox (sin cambiar lo que hacía por defecto):

```
.venv/bin/python -X utf8 docs/research/modis_fechas.py 2000 2025 MOD11A2 diez > docs/research/lst_fechas.txt
```

Para cada año pide a PC la búsqueda STAC de `download.py` (colección `modis-11A2-061`, ítems `MOD11A2.*`) y a CMR
`granules.json?short_name=MOD11A2&version=061` (sin login), con un bbox que cubre los 10 estados:
`-104.11, 35.94, -80.47, 49.44` (el de T090 con el sur bajado a 35,94° por el bootheel de Missouri; WI y SD ya
caían dentro). Las teselas son las mismas 6 que en MOD13Q1: h09v05, h10v04, h10v05, h11v04, h11v05 y h12v04.
Cuenta solo los compuestos que empiezan en ese año. Salida completa: `docs/research/lst_fechas.txt`.

| Año | Compuestos PC | Compuestos CMR | Gránulos PC / CMR | Faltan en PC |
|---|---|---|---|---|
| 2000 | 40 | 40 | 240 / 240 | — |
| 2001 | 45 | 45 | 267 / 267 | — (A2001169 y 3 teselas de A2001177 faltan también en CMR) |
| 2002–2021 | 46 | 46 | 276 / 276 | — |
| 2022 | 43 | 45 | 250 / 270 | A2022337, A2022345 enteros; A2022273, A2022281, A2022297 en parte (A2022289 falta también en CMR) |
| 2023 | 44 | 46 | 264 / 276 | A2023001, A2023057 |
| 2024 | 44 | 46 | 264 / 276 | A2024121, A2024361 |
| 2025 | 28 | 46 | 168 / 276 | A2025185, 193, 201, 209, 217, 225, 233, 241, 249, 257, 265, 273, 281, 289, 297, 305, 313, 321 |

## 2. Los huecos son de PC

- **CMR tiene los gránulos, producidos a tiempo.** Por ejemplo, en h11v04:
  `MOD11A2.A2022273.h11v04.061.2022282041653` (producido el 9-oct-2022),
  `MOD11A2.A2022337.h11v04.061.2022352040034` (18-dic-2022),
  `MOD11A2.A2023001.h11v04.061.2023014235629` (14-ene-2023),
  `MOD11A2.A2024121.h11v04.061.2024132011326` (11-may-2024),
  `MOD11A2.A2025249.h11v04.061.2025258205950` (15-sep-2025).
- **En PC faltan en todo el mundo.** Búsqueda sin bbox en PC (ítems por compuesto; un compuesto completo tiene
  317 teselas):
  - sep–oct 2022: `MOD11A2.A2022265` 130, `A2022273` 147, `A2022281` 57, `A2022289` 65, `A2022297` 125, mientras
    que `MYD11A2` (Aqua) tiene 317 en todos. El Corn Belt tuvo suerte con `A2022265` (completo) y mala suerte con
    `A2022289` (que en LP DAAC tampoco está para estas teselas);
  - dic 2022: `MOD11A2.A2022337` y `A2022345` no están; Aqua tiene `A2022337` pero tampoco `A2022345`;
  - ene–mar 2023: `MOD11A2.A2023001` y `A2023057` no están (Aqua `A2023001` sí);
  - abr–may 2024: `MOD11A2.A2024121` con 244 de 317 (ninguna del Corn Belt);
  - dic 2024: `MOD11A2.A2024361` con 166 (ninguna del Corn Belt);
  - jul–nov 2025: solo `A2025169`, `A2025177`, `A2025329` completos y `A2025321` con 7 teselas (ninguna del Corn
    Belt), en Terra y en Aqua.
- Como en MOD13Q1, PC sigue ingiriendo (la colección está al día en 2026), pero no volvió a cargar estos huecos.

## 3. Qué deja sin datos en `vegetacion_mensual.csv`

`process.py` promedia por mes los compuestos de 8 días según su fecha de inicio (`lst_dia_c`, `lst_noche_c`) y
de `lst_dia_c` saca `tci` y `vhi`. Sin relleno:
- **jul, ago, sep y oct de 2025 quedan sin LST** (y sin `tci` ni `vhi`), en los 10 estados; nov 2025 queda con un
  solo compuesto (`A2025329`) y jun 2025 no pierde nada (`A2025177` empieza el 26-jun y está).
- dic 2022 queda con 2 de 4 compuestos; ene 2023, feb 2023, abr 2024 (`A2024121` empieza el 30-abr) y dic 2024
  pierden uno cada uno; oct 2022 pierde 1 o 2 según la tesela (además de `A2022289`, que falta en la fuente).
- Como `tci` usa el mínimo y el máximo de cada mes en toda la serie, los meses vacíos no lo deforman, pero los
  meses con menos compuestos tienen medias más ruidosas.

No lo comprobé contra un CSV real: esta máquina no tiene `data/raw/vegetacion/mod11a2/`.

## 4. Qué sumar al relleno de T100

| Producto | Compuesto | Teselas que faltan en PC |
|---|---|---|
| MOD11A2 | A2022273 | h11v04, h11v05, h12v04 |
| MOD11A2 | A2022281 | h09v05, h10v04 |
| MOD11A2 | A2022297 | h09v05, h10v04, h10v05 |
| MOD11A2 | A2022337, A2022345 | las 6 |
| MOD11A2 | A2023001, A2023057 | las 6 |
| MOD11A2 | A2024121, A2024361 | las 6 |
| MOD11A2 | A2025185 a A2025321 (18, cada 8 días) | las 6 |

Para cada máquina alcanza con sus teselas (las de cada grupo de estados están en la sección 3 de
`modis_fechas.md`; por la geometría sinusoidal, calculada a mano y sin consultar PC por estado: SD cae en h10v04, WI en h11v04 y MO sobre todo en h10v05, con bordes en h10v04 y h11v05). Lo más simple es que la lógica de T100
no tenga una lista fija sino que calcule "CMR menos PC" por producto, tesela y compuesto, como hace
`modis_fechas.py`: así cubre MOD13Q1 y MOD11A2 a la vez, y deja de bajar lo que PC cargue más adelante.

Lectura del HDF: las capas `LST_Day_1km`, `LST_Night_1km`, `QC_Day` y `QC_Night` tienen la misma escala que los
COG de PC (×0,02 K; `process.py` línea 186). `download.py` usa la overview 0 del COG (~2 km): el HDF viene a 1 km
y habría que remuestrearlo igual para no mezclar resoluciones.

Alternativa sin Earthdata: la API de ORNL DAAC (`https://modis.ornl.gov/rst/api/v1/MOD11A2/dates`, probada en un
punto de Story, IA) lista todos los compuestos faltantes de la tabla, hasta `A2026297`; no lista `A2022289`.
Tiene los mismos límites que para MOD13Q1 (±100 km y 10 compuestos por pedido).

## Propuesta (para decidir)

1. Ampliar T100 a MOD11A2 con la tabla de la sección 4 (o, mejor, con la diferencia CMR − PC calculada en el
   momento). Volumen: ~0,9 GB para los 10 estados; no necesita OK por tamaño.
2. Mientras tanto, anotar en `docs/datasets/vegetacion.md` (Problemas conocidos) que `lst_dia_c`, `lst_noche_c`,
   `tci` y `vhi` no tienen datos de jul–oct 2025 y que los meses de la sección 3 tienen menos compuestos.
3. `A2001169`, `A2001177` (3 teselas), `A2022289` y ene–feb 2000 faltan en LP DAAC: no hay de dónde rellenarlos.

Fuentes:
- [Planetary Computer STAC, colección modis-11A2-061](https://planetarycomputer.microsoft.com/api/stac/v1/collections/modis-11A2-061), consultado 2026-11-15
- [NASA CMR, búsqueda de gránulos (MOD11A2 v061, sin login)](https://cmr.earthdata.nasa.gov/search/granules.json?short_name=MOD11A2&version=061), consultado 2026-11-15
- [ORNL DAAC MODIS Web Service](https://modis.ornl.gov/data/modis_webservice.html) (API `https://modis.ornl.gov/rst/api/v1/`), consultado 2026-11-15
- [LP DAAC, MOD11A2 v061 (DOI 10.5067/MODIS/MOD11A2.061)](https://doi.org/10.5067/MODIS/MOD11A2.061), consultado 2026-11-15
- Salida completa: `docs/research/lst_fechas.txt` (de `docs/research/modis_fechas.py`)

Confianza: alta sobre qué gránulos faltan y que faltan solo en PC (comparación directa de catálogos). Alta sobre
el volumen (tamaños declarados en CMR). Media sobre el efecto en los meses (deducido del código de `process.py`,
no comprobado contra un CSV). La explicación del hueco de junio de 2001 (modo seguro de Terra) es de memoria, no
la verifiqué.

Impacto: tarea T100 y `src/vegetacion/download.py` (relleno también de MOD11A2), `docs/datasets/vegetacion.md`
(problemas conocidos) y, después de rellenar, `lst_dia_c`, `lst_noche_c`, `tci` y `vhi` de
`vegetacion_mensual.csv` de 2022–2025 en todos los estados.
