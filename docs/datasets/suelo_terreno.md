# Data card — suelo_terreno

Paquete `suelo_terreno` de Field Shift (CLAUDE.md §6.5): suelo (SSURGO) y terreno (NASADEM) por condado del Corn Belt.

## Diccionario de columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
| suelo_terreno_estatico.csv | aws0_100_mm | Agua disponible 0–100 cm (muaggatt.aws0100wta × 10), media ponderada por superficie | mm | SSURGO muaggatt vía Soil Data Access | L12 |  |  | 0.0 |
| suelo_terreno_estatico.csv | aws0_150_mm | Agua disponible 0–150 cm (muaggatt.aws0150wta × 10) | mm | SSURGO muaggatt vía Soil Data Access | L12 |  |  | 0.0 |
| suelo_terreno_estatico.csv | soc0_30_gm2 | Carbono orgánico 0–30 cm: Σ espesor · MO · 0,58 · densidad aparente · (1 − fragmentos) | g C/m² | SSURGO chorizon vía Soil Data Access | L10 |  |  | 0.0 |
| suelo_terreno_estatico.csv | soc0_100_gm2 | Carbono orgánico 0–100 cm (mismo cálculo) | g C/m² | SSURGO chorizon vía Soil Data Access | L04 |  |  | 0.0 |
| suelo_terreno_estatico.csv | nccpi_general | NCCPI 3.0 general (cointerp.interphr) | 0-1 | SSURGO cointerp (NCCPI 3.0) vía Soil Data Access | L15 |  |  | 0.0 |
| suelo_terreno_estatico.csv | nccpi_maiz | NCCPI 3.0, submodelo maíz (Corn Submodel I) | 0-1 | SSURGO cointerp (NCCPI 3.0) vía Soil Data Access | L15 |  |  | 0.0 |
| suelo_terreno_estatico.csv | nccpi_soja | NCCPI 3.0, submodelo soja (Soybeans Submodel I) | 0-1 | SSURGO cointerp (NCCPI 3.0) vía Soil Data Access | L15 |  |  | 0.0 |
| suelo_terreno_estatico.csv | prof_raices_cm | Profundidad de raíces: mín(restricción que limita raíces, fondo del perfil, 150 cm) | cm | SSURGO vía Soil Data Access (USDA NRCS) |  |  |  | 0.0 |
| suelo_terreno_estatico.csv | clase_drenaje | Clase de drenaje del componente dominante (muaggatt.drclassdcd) con más superficie en el condado | clase | SSURGO muaggatt vía Soil Data Access | L17 |  |  | 0.0 |
| suelo_terreno_estatico.csv | grupo_hidrologico | Grupo hidrológico dominante (muaggatt.hydgrpdcd) con más superficie | clase | SSURGO muaggatt vía Soil Data Access |  |  |  | 0.0 |
| suelo_terreno_estatico.csv | napa_min_cm | Profundidad mínima anual de la napa (muaggatt.wtdepannmin), media de las unidades con napa < 200 cm | cm | SSURGO muaggatt vía Soil Data Access |  |  |  | 0.0 |
| suelo_terreno_estatico.csv | arcilla_pct | Arcilla total 0–30 cm (claytotal_r), media ponderada por espesor, componente y superficie | % | SSURGO chorizon vía Soil Data Access | L01 |  |  | 0.0 |
| suelo_terreno_estatico.csv | arena_pct | Arena total 0–30 cm (sandtotal_r) | % | SSURGO chorizon vía Soil Data Access | L02 |  |  | 0.0 |
| suelo_terreno_estatico.csv | limo_pct | Limo total 0–30 cm (silttotal_r) | % | SSURGO chorizon vía Soil Data Access | L03 |  |  | 0.0 |
| suelo_terreno_estatico.csv | materia_organica_pct | Materia orgánica 0–30 cm (om_r) | % | SSURGO chorizon vía Soil Data Access | L04 |  |  | 0.0 |
| suelo_terreno_estatico.csv | ph_agua | pH en agua 1:1, 0–30 cm (ph1to1h2o_r) | pH | SSURGO chorizon vía Soil Data Access | L06 |  |  | 0.0 |
| suelo_terreno_estatico.csv | clase_textural_usda | Clase textural USDA de la arena/limo/arcilla media del condado | clase | SSURGO chorizon vía Soil Data Access | L11 |  |  | 0.0 |
| suelo_terreno_estatico.csv | factor_k_rusle | Factor K (kwfact) del horizonte superficial | t·ha·h/(ha·MJ·mm) (adim. NRCS) | SSURGO chorizon vía Soil Data Access | L13 |  |  | 0.0 |
| suelo_terreno_estatico.csv | elevacion_media_m | Elevación media de los píxeles de 1" del condado | m | NASADEM v001 (Planetary Computer) | T01 |  |  | 0.0 |
| suelo_terreno_estatico.csv | elevacion_desvio_m | Desvío estándar de la elevación | m | NASADEM v001 (Planetary Computer) | T01 |  |  | 0.0 |
| suelo_terreno_estatico.csv | pendiente_media_pct | Pendiente media a 3" (~90 m, media de 3 × 3 píxeles), diferencias centradas | % | NASADEM v001 (Planetary Computer) | T02 |  |  | 0.0 |
| suelo_terreno_estatico.csv | pendiente_gt2_pct | % de píxeles de 3" con pendiente > 2 % | % | NASADEM v001 (Planetary Computer) | T02 |  |  | 0.0 |
| suelo_terreno_estatico.csv | twi_medio | Índice topográfico de humedad ln(a / tan β) a 3" (~90 m), media | adim. | NASADEM v001 (Planetary Computer) | T06 |  |  | 0.0 |
| suelo_terreno_estatico.csv | twi_decil_sup_pct | % del área con TWI en el decil superior de toda la zona de estudio | % | NASADEM v001 (Planetary Computer) | T06 |  |  | 0.0 |

## Fuentes y acceso

- **DOI:** NASADEM Merged DEM Global 1 arc second V001 (`NASADEM_HGT`, LP DAAC):
  https://doi.org/10.5067/MEASURES/NASADEM/NASADEM_HGT.001. SSURGO (USDA NRCS) no tiene DOI: se cita como
  pide Soil Data Access.
- Citas completas: `docs/research/citas_nasa.md`.

- **SSURGO** (USDA NRCS) por **Soil Data Access** (`https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest`,
  sin login). `src/suelo_terreno/download.py` consulta por estado las tablas `mapunit` + `muaggatt`,
  `component`, `chorizon` (+ suma de `chfrags.fragvol_r`), `corestrictions` y `cointerp` (NCCPI 3.0) y
  las guarda tal cual en `data/raw/suelo_terreno/sda/<tabla>_<estado>.csv`.
- **NASADEM HGT v001** (1 arcsec, ~30 m), teselas de 1° en COG de Microsoft Planetary Computer
  (`nasademeuwest.blob.core.windows.net/nasadem-cog/v001/`, token SAS anónimo), en
  `data/raw/suelo_terreno/nasadem/`.
- `src/suelo_terreno/process.py` agrega suelo por condado y llama a `terreno.py` para el DEM.

## Supuestos

- **No se usó el raster gSSURGO de 10 m ni la tabla Valu1.** Soil Data Access no tiene `Valu1`
  (la consulta `SELECT TOP 2 * FROM valu1` devuelve error) y bajar las geodatabases por estado
  implicaba varios GB por Box. Se usó la parte tabular de SSURGO por SDA:
  - Agua disponible de `muaggatt` (`aws0100wta`, `aws0150wta`, en cm → × 10 = mm).
  - NCCPI de `cointerp` (reglas `NCCPI - National Commodity Crop Productivity Index (Ver 3.0)`,
    `NCCPI - NCCPI Corn Submodel (I)` y `NCCPI - NCCPI Soybeans Submodel (I)`, valor `interphr`),
    equivalentes a `nccpi3all`, `nccpi3corn` y `nccpi3soy` de Valu1.
  - SOC calculado desde `chorizon`: MO (%) × 0,58 × `dbthirdbar_r` × espesor × (1 − fragmentos/100)
    × 10⁴; se deja vacío en el componente si algún horizonte de la capa no tiene dato o el perfil no
    llega al fondo de la capa.
  - Profundidad de raíces: mínimo entre la primera restricción de `corestrictions` que limita raíces
    (roca lítica o paralítica, material dénsico, fragipán, duripán, horizontes cementados, capa
    manufacturada), el fondo del perfil y 150 cm (tope del `rootznemc` de Valu1). Las restricciones
    por "cambio textural abrupto" no se cuentan como límite.
- **Ponderación por superficie, sin máscara agrícola.** El valor del condado es la media ponderada
  por `muacres` de las unidades cartográficas del área de relevamiento del condado (en IA, IL e IN
  `areasymbol` = estado + código de condado: IA169 → 19169), y dentro de cada unidad por
  `comppct_r` de los componentes con dato. Sin el raster de MUKEY no se pudo cruzar con
  `data/reference/mascara_agricola.tif`: incluye superficie no agrícola.
- **Áreas de levantamiento que no son un condado** (en KY, 39 de 84: `KY601`–`KY645` juntan dos o
  tres condados, `KY646`/`KY647` tienen código propio y `KY648`/`KY709` son áreas especiales como
  Mammoth Cave): se reparten con `laoverlap` (`areatypename = 'County or Parish'`) y `muaoverlap` de
  SDA (tabla `solape_<estado>.csv`). En esas áreas cada unidad pesa por `areaovacres`, su superficie
  dentro de cada condado, en lugar de `muacres`; un condado partido entre dos áreas (Barren, Edmonson,
  Hart, Whitley en KY) junta las unidades de ambas. Se supone que la superficie tabular de SDA
  representa bien la del raster (no se contó en píxeles). Las áreas `XX` + código de condado y las de
  MN siguen igual que antes: en OH, NE, MN y KS se comparó contra SDA el reparto viejo y el nuevo (2026-11-15)
  y dan idéntico. Un área sin condado ni solape queda afuera con un aviso.
- Horizontes 0–30 cm: media ponderada por el espesor de cada horizonte dentro de la capa. La textura
  usa solo horizontes con arena, limo y arcilla que suman 100 ± 3 (quedan fuera los horizontes
  orgánicos, por ejemplo los suelos muck del norte de Indiana, donde la textura no está definida).
- Clase textural: triángulo USDA aplicado a la media de arena/limo/arcilla del condado (no a la
  clase dominante).
- Factor K: `kwfact` del horizonte más superficial del componente (vacío en horizontes orgánicos).
- `clase_drenaje` y `grupo_hidrologico`: la clase con más superficie en el condado (`drclassdcd` y
  `hydgrpdcd` son la clase del componente dominante de cada unidad), en inglés como viene en SSURGO.
- `napa_min_cm`: `wtdepannmin` vacío significa napa a más de 200 cm; la media es solo de las unidades
  con dato (no se rellena con 200).
- **Terreno:** NASADEM en lugar de SRTM GL1 (mismo producto reprocesado). Estadísticas sobre todos
  los píxeles del condado (sin máscara agrícola), sin ponderar por área del píxel (varía < 1 % dentro
  de un condado). Pendiente calculada a 3" (~90 m, media de bloques de 3 × 3 píxeles de 1") con el tamaño real
  del píxel en metros: a 1" el ruido de NASADEM daba > 70 % del área con pendiente > 2 % aun en
  condados llanos como Champaign (IL). Umbral de pendiente: 2 %. La última fila y columna de cada
  tesela (repiten el borde de la vecina) se descartan.
- TWI = ln(a / tan β) a 3" (~90 m, media de 3 × 3 píxeles), con relleno de depresiones, flujo D8 y
  acumulación de pysheds dentro de cada tesela de 1° (el área aportante se corta en los bordes de
  tesela); tan β ≥ 0,001. Decil superior: percentil 90 del TWI de todos los píxeles de la zona.

## Problemas conocidos

- Sin máscara agrícola: los promedios de suelo y terreno incluyen bosque, urbano y agua.
- Aun a 90 m, el ruido de NASADEM (y la vegetación, porque es un modelo de superficie) puede inflar
  la pendiente en zonas planas: `pendiente_gt2_pct` probablemente sobreestima el área con pendiente.
- El TWI subestima el área aportante cerca de los bordes de tesela (ríos grandes que cruzan teselas).
- Unidades sin `muacres` o componentes sin dato quedan fuera de la media.
