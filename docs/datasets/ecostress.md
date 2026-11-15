# Data card — ecostress

Paquete `ecostress` de Field Shift: temperatura de superficie, evapotranspiración y estrés evaporativo de ECOSTRESS por condado y mes.

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| ecostress_mensual.csv | lst_ecostress_c | Temperatura de superficie (ECO_L2T_LSTE.002 capa LST) media del mes: promedio de las pasadas con datos, cada una la media de los píxeles agrícolas de buena calidad y sin nube de la ventana de 2,24 km del condado | °C | NASA JPL ECOSTRESS colección 2 (LP DAAC), 70 m, ECO_L2T_LSTE.002 | X01 | 2025-04 | 2025-10 | 9.5 |
| ecostress_mensual.csv | et_ecostress_mm_dia | Evapotranspiración diaria (ECO_L3T_JET.002 capa ETdaily) media del mes, mismas pasadas y píxeles que la LST | mm/día | NASA JPL ECOSTRESS colección 2 (LP DAAC), 70 m, ECO_L3T_JET.002 | X02 | 2025-04 | 2025-10 | 9.5 |
| ecostress_mensual.csv | esi_ecostress | Índice de estrés evaporativo (ECO_L4T_ESI.002 capa ESI, ET/PET) medio del mes, mismas pasadas y píxeles que la LST | adim. | NASA JPL ECOSTRESS colección 2 (LP DAAC), 70 m, ECO_L4T_ESI.002 | X03 | 2025-04 | 2025-10 | 9.5 |
| ecostress_mensual.csv | n_pasadas_ecostress | Pasadas diurnas del mes con al menos 10 píxeles agrícolas válidos de LST en la ventana del condado (0 si todas nubladas, sin dato o sin pasada sobre la ventana) | pasadas | NASA JPL ECOSTRESS colección 2 (LP DAAC), 70 m |  | 2025-04 | 2025-10 | 0.0 |

## Fuentes y acceso

- **DOI de los productos de la NASA (colección 2, V002, LP DAAC):**
  - ECO_L2T_LSTE: https://doi.org/10.5067/ECOSTRESS/ECO_L2T_LSTE.002
  - ECO_L3T_JET: https://doi.org/10.5067/ECOSTRESS/ECO_L3T_JET.002
  - ECO_L4T_ESI: https://doi.org/10.5067/ECOSTRESS/ECO_L4T_ESI.002
- Citas completas: `docs/research/citas_nasa.md`.

- **ECOSTRESS colección 2, productos en teselas MGRS de 70 m** de LP DAAC (Earthdata Cloud):
  `ECO_L2T_LSTE.002` (capas `LST`, `QC`, `cloud`), `ECO_L3T_JET.002` (capa `ETdaily`) y
  `ECO_L4T_ESI.002` (capa `ESI`). Nombres de producto y capa verificados en la API de productos de
  AppEEARS (`/api/product/<producto>`) y en los nombres de archivo de CMR.
- `src/ecostress/download.py` busca en CMR las pasadas de `ECO_L3T_JET` de cada mes sobre el bbox de
  IA, IL e IN, empareja cada una con la LSTE y la ESI de la misma órbita, escena y tesela, y lee de
  los COG (lectura por rango HTTP con token de Earthdata, sin bajar la tesela entera) una ventana de
  32x32 píxeles alrededor del punto agrícola de cada condado. Guarda por condado y pasada el número de
  píxeles agrícolas, de píxeles válidos y la media de LST, ETdaily y ESI en
  `data/raw/ecostress/ecostress_extraccion_<AAAA-MM>.csv` (un archivo por mes, se mueve a raw solo
  cuando el mes está completo; el mes en curso queda en `data/interim/ecostress/`).
- `src/ecostress/process.py` une los meses, saca pasadas duplicadas por solape de teselas y promedia
  por condado y mes.

## Supuestos

- **Acceso directo a LP DAAC en lugar de AppEEARS.** La API de AppEEARS pide un login propio con
  usuario y contraseña; el token de Earthdata da 403. Se leen los COG de LP DAAC directo.
- **Ventana de muestra, no el condado entero.** Las teselas completas de 2018 a 2025 son cientos de
  miles de archivos (CMR: ~221 000 granulos LSTE y ~81 000 JET/ESI sobre el bbox) y pasarían de lejos
  los 5 GB. Por condado se usa una ventana de 32x32 píxeles de 70 m (2,24 km de lado) centrada en el
  píxel agrícola (máscara `data/reference/mascara_agricola.tif`, CDL) más cercano al centroide de los
  píxeles agrícolas del condado (`data/interim/ecostress/puntos_condados.csv`). Dentro de la ventana
  solo cuentan los píxeles de 70 m cuyo centro cae en un píxel agrícola de la máscara (muestreo por
  vecino más cercano). Es una muestra local, no la media de todo el condado.
- **Calidad:** cuentan los píxeles con bits 0-1 de `QC` en 00 (mejor calidad) o 01 (nominal), `cloud`
  = 0 y valor finito en rango físico (LST 200-350 K, ETdaily 0-30, ESI 0-2). La máscara de nube y
  calidad de la LSTE se aplica también a ETdaily y ESI de la misma pasada (misma grilla).
- **Pasadas:** solo las escenas con producto JET (pasadas diurnas con ET); ECOSTRESS pasa a horas
  variables (incluye pasadas de madrugada, ~11 UTC), así que la LST mensual mezcla horas distintas.
  Una pasada cuenta si tiene al menos 10 píxeles agrícolas válidos; la media mensual es el promedio
  simple de las pasadas (cada pasada pesa igual).
- **ETdaily en mm/día:** la API de AppEEARS lista la unidad de `ETdaily` como W/m², pero los valores
  (0-6 en julio sobre maíz y soja) son de mm/día, la unidad de la guía de usuario de L3T JET.
- **Meses:** solo abril a octubre (sin nieve y con más pasadas despejadas), de 2018-08 a 2025-10,
  empezando por los más recientes. Los meses de noviembre a marzo no se bajaron.

## Problemas conocidos

- La descarga es larga (~100 pasadas/min con 40 hilos; un mes tiene de ~100 a ~750 pasadas sobre los
  condados): la cobertura crece ronda a ronda. Solo están los meses que aparecen en `data/raw/ecostress/`.
- Condados con poca superficie agrícola cerca del punto tienen pocas píxeles válidos o ninguno.
- El orden de los meses y el bbox de CMR salen de `download.py`, no de `config/config.yaml`.
- **Oeste de Iowa (corregido en r007).** En r005-r006 el bbox de CMR era `-91.6,37.0,-84.8,43.5` y dejaba
  afuera las teselas del oeste de Iowa (83 condados nunca tenían pasada). El bbox ahora es
  `-96.7,37.0,-84.7,43.6`. Los meses bajados con el bbox angosto (2025-04 a 2025-10) se completan con
  `ecostress_extraccion_<AAAA-MM>_oeste.csv` (solo las escenas que faltaban); mientras un mes no tenga su
  suplemento, los condados que no aparecen en su extracción quedan con `n_pasadas_ecostress` vacío (no 0).
