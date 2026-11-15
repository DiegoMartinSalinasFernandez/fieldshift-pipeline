<!-- generado por src/seguro/fsa_process.py: no editar a mano -->
## Siembra prevenida (FSA Crop Acreage Data) — `siembra_prevenida_anual.csv`

Fuente: USDA Farm Service Agency, Crop Acreage Data, archivo final de cada año (2009–2025), hoja por condado. Research: `docs/research/siembra_prevenida.md` (T032). Código: `src/seguro/fsa_download.py` y `src/seguro/fsa_process.py`. **Esquema nuevo: espera el OK de `coordinacion/para_decidir.md` #17.**

### Columnas

| Columna | Descripción | Unidad | Fuente |
|---|---|---|---|
| `fips`, `anio`, `cultivo` | condado (FIPS del Census), año de cosecha (crop year del archivo), cultivo (`maiz`, `soja`, `trigo_invierno`, `avena`) | | |
| `sup_sembrada_fsa_ac` | superficie sembrada declarada a FSA, todos los usos, riego + secano | acres | FSA `Planted Acres` |
| `sup_prevenida_ac` | superficie con siembra prevenida | acres | FSA `Prevented Acres` |
| `sup_fallida_ac` | superficie sembrada y perdida | acres | FSA `Failed Acres` |
| `sup_prevenida_riego_ac`, `sup_prevenida_secano_ac` | prevenida con `Irrigation Practice` I / N (2011: columnas Irrigated / Nonirrigated; vacío en 2009–2010) | acres | FSA |
| `pct_prevenida` | 100 × prevenida / (sembrada + prevenida); vacío si el denominador es 0 | % | cálculo |

### Archivos leídos

| anio | xlsx | filas_estados | con_riego | filas_csv |
|---|---|---|---|---|
| 2009 | 2009_fsa_acres_detail_final_7.xlsx | 23692 | no | 1437 |
| 2010 | 2010_fsa_acres_detail_final_5.xlsx | 22266 | no | 1434 |
| 2011 | 2011_fsa_acres_detail_jan2012.xlsx | 25067 | sí | 1412 |
| 2012 | 2012_fsa_acres_jan_2013.xlsx | 28555 | sí | 1422 |
| 2013 | 2013_fsa_acres_jan_2014.xlsx | 28973 | sí | 1413 |
| 2014 | 2014_fsa_acres_jan2014.xlsx | 29552 | sí | 1415 |
| 2015 | 2015_fsa_acres_01052016.xlsx | 31439 | sí | 1424 |
| 2016 | 2016_fsa_acres_010417.xlsx | 31950 | sí | 1411 |
| 2017 | 2017_fsa_acres_010418.xlsx | 28438 | sí | 1400 |
| 2018 | 2018_fsa_acres_012819.xlsx | 28853 | sí | 1397 |
| 2019 | 2019_fsa_acres_web_010220.xlsx | 32638 | sí | 1401 |
| 2020 | 2020_fsa_acres_web_010521.xlsx | 32405 | sí | 1397 |
| 2021 | 2021_fsa_acres_web_010322.xlsx | 32066 | sí | 1416 |
| 2022 | 2022_fsa_acres_web_010323.xlsx | 31450 | sí | 1392 |
| 2023 | 2023_fsa_acres_web_010224.xlsx | 31657 | sí | 1401 |
| 2024 | 2024_fsa_acres_010225.xlsx | 31424 | sí | 1399 |
| 2025 | 2025_fsa_acres_web_010526.xlsx | 32046 | sí | 1392 |

### % de faltantes por columna

| columna | pct_faltante |
|---|---|
| sup_sembrada_fsa_ac | 0 |
| sup_prevenida_ac | 0 |
| sup_fallida_ac | 0 |
| sup_prevenida_riego_ac | 12 |
| sup_prevenida_secano_ac | 12 |
| pct_prevenida | 0 |

### Códigos de condado de FSA convertidos a FIPS

Con `data/reference/fsa_condados_admin.csv` (condados partidos en dos oficinas de FSA; la correspondencia es una inferencia por el nombre, confianza media). Acres que se sumaron:

| codigo | fips | cultivo | sembrada | prevenida | anios |
|---|---|---|---|---|---|
| 27112 | 27111 | avena | 37,007 | 22 | 17 |
| 27112 | 27111 | maiz | 1,576,449 | 10,279 | 17 |
| 27112 | 27111 | soja | 1,841,167 | 6,032 | 17 |
| 27112 | 27111 | trigo_invierno | 1,241 | 0 | 6 |
| 27120 | 27119 | avena | 20,815 | 29 | 17 |
| 27120 | 27119 | maiz | 985,170 | 68,692 | 17 |
| 27120 | 27119 | soja | 3,195,212 | 18,038 | 17 |
| 27120 | 27119 | trigo_invierno | 15,610 | 0 | 16 |
| 27138 | 27137 | avena | 2,540 | 126 | 16 |
| 27138 | 27137 | maiz | 1,626 | 248 | 17 |
| 27138 | 27137 | soja | 152 | 0 | 4 |
| 27138 | 27137 | trigo_invierno | 42 | 0 | 3 |
| 39094 | 39095 | maiz | 51,810 | 5,015 | 17 |
| 39094 | 39095 | soja | 194,895 | 6,824 | 17 |
| 39094 | 39095 | trigo_invierno | 17,206 | 1,992 | 17 |

### Condados sin ninguna fila

Condados de condados.csv sin maíz, soja, trigo de invierno ni avena en ningún año de FSA: 27031, 27075.

### Códigos sin FIPS (quedan afuera del CSV)

Ninguno: todos los códigos de los estados pedidos se convirtieron.

### Totales de 2019 por estado (control contra el research)

| estado | cultivo | sup_sembrada_fsa_ac | sup_prevenida_ac |
|---|---|---|---|
| 20 | avena | 98,357 | 42 |
| 20 | maiz | 6,205,608 | 224,007 |
| 20 | soja | 4,498,939 | 163,728 |
| 20 | trigo_invierno | 6,725,810 | 187,876 |
| 27 | avena | 157,885 | 351 |
| 27 | maiz | 7,624,334 | 996,679 |
| 27 | soja | 6,774,620 | 161,246 |
| 27 | trigo_invierno | 6,723 | 0 |
| 31 | avena | 104,679 | 413 |
| 31 | maiz | 10,010,908 | 342,826 |
| 31 | soja | 4,822,110 | 71,958 |
| 31 | trigo_invierno | 1,004,193 | 1,584 |
| 39 | avena | 19,126 | 93 |
| 39 | maiz | 2,708,457 | 923,123 |
| 39 | soja | 4,239,101 | 629,815 |
| 39 | trigo_invierno | 411,643 | 6,057 |

### Supuestos

- Maíz sin pochoclo, dulce ni ornamental; soja sin edamame; trigo solo de invierno (tipo con `WINTER`). El research sumó todos los tipos, así que sus totales de maíz son algo mayores.
- Se suman todos los usos (grano, silo, semilla, forraje...) salvo `Grazing` en trigo y avena, que FSA cuenta dos veces desde 2019 cuando el mismo acre se pastorea y se cosecha.
- Riego y secano sumados en las columnas de superficie; la prevenida además por práctica.
- 0 es un 0 real: el condado declaró el cultivo y no tuvo siembra prevenida. Un condado sin filas del cultivo no aparece.
- Se toma el archivo final de cada año; FSA no dice si los revisa después de publicarlos.

### Problemas conocidos

- La siembra prevenida depende también de reglas del seguro (fecha final de siembra, regla 1 de 4) y de los precios, no solo del clima. En KS una parte es por sequía (para separarla: RMA, etapas P2/PF/PT y causa).
- El encabezado cambia entre años: 2010 llama `State` al código de estado, 2011 viene en formato ancho (`Planted Total`, `Prevented Irrigated`...), 2012 dice `Failded Acres`. El lector busca las columnas por nombre y falla con un mensaje claro si falta alguna.
- En 2012 hay un uso `Grain/Graze` (un solo acre con los dos usos): se cuenta una vez.
