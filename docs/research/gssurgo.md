# gSSURGO: columnas de Valu1 y muaggatt, y geodatabase por estado vs Soil Data Access

Pregunta: gSSURGO: nombres de columnas de Valu1 y muaggatt (NCCPI, agua disponible, drenaje), y si conviene el file geodatabase por estado o Soil Data Access.

Respuesta corta: En `Valu1` las columnas son `aws0_100` y `aws0_150` (agua disponible, mm), `soc0_30` y `soc0_100` (carbono orgánico, g C/m²), `nccpi3corn`, `nccpi3soy`, `nccpi3sg`, `nccpi3cot` y `nccpi3all` (NCCPI v3, de 0,01 a 0,99), `rootznemc` (profundidad de raíces, cm) y `rootznaws` (agua disponible en la zona radicular, mm), unidas al raster de 10 m por `mukey`. En `muaggatt`: `aws0100wta` y `aws0150wta` (agua disponible, **en cm**, no en mm), `drclassdcd` (clase de drenaje dominante), `drclasswettest`, `hydgrpdcd` (grupo hidrológico dominante), `wtdepannmin` y `wtdepaprjunmin` (napa mínima, cm). **Valu1 no está en Soil Data Access** (SDA devuelve `Invalid object name 'valu1'`), así que para NCCPI, `aws0_100` ponderado y profundidad de raíces hace falta el geodatabase (gSSURGO por estado o gNATSGO) o su copia pública en Planetary Computer. SDA sirve para `muaggatt`, `component`, `chorizon` y NCCPI vía `cointerp`, con un tope de 100.000 filas por consulta. Recomendación: usar el raster MUKEY + Valu1 (por la máscara agrícola y la ponderación por píxel) y SDA solo como complemento tabular.

Detalle:

**Valu1** (tabla "Value Added Look Up" de gSSURGO/gNATSGO, una fila por `mukey`). Nombres y definiciones según el STAC de gNATSGO en Planetary Computer (snapshot de julio de 2020):

| Columna | Qué es | Unidad |
|---|---|---|
| `mukey` | clave de la unidad cartográfica; une Valu1 con `MapUnitRaster_10m` | — |
| `aws0_100`, `aws0_150` | agua disponible almacenable 0–100 y 0–150 cm, media ponderada de todos los componentes | mm |
| `aws0_5` … `aws150_999` | lo mismo por zonas estándar (0–5, 0–20, 0–30, 20–50, 50–100, 100–150, 150–999) | mm |
| `soc0_30`, `soc0_100` | carbono orgánico del suelo 0–30 y 0–100 cm | g C/m² |
| `nccpi3corn` | NCCPI v3 para maíz, media ponderada de componentes principales "earthy" | 0,01–0,99 |
| `nccpi3soy` | NCCPI v3 para soja | 0,01–0,99 |
| `nccpi3sg`, `nccpi3cot` | NCCPI v3 para cereales de invierno (small grains) y algodón | 0,01–0,99 |
| `nccpi3all` | el mayor entre maíz/soja, small grains y algodón | 0,01–0,99 |
| `rootznemc` | profundidad de la zona radicular para cultivos de commodities | cm |
| `rootznaws` | agua disponible dentro de la zona radicular | mm |
| `droughty` | 1 = paisaje vulnerable a sequía (RZAWS ≤ 152 mm), 0 = no | — |
| `pwsl1pomu` | % de la unidad que cumple el criterio de humedal potencial (PWSL v1) | % |
| `musumcpct`, `musumcpcta`, `musumcpcts` | suma de `comppct_r` usada en los cálculos (metadato) | % |

Ojo con los nombres: el CLAUDE.md habla de "NCCPI maíz/soja y general". En Valu1 v3 no hay una columna única "maíz y soja": hay `nccpi3corn` y `nccpi3soy` por separado, y `nccpi3all` es el máximo entre los submodelos. En el raster de gNATSGO de Planetary Computer estas columnas también vienen ya pintadas como COG de 10 m (`nccpi3corn`, `aws0_100`, `rootznemc`, etc., `nodata` = -9999).

**muaggatt** (atributos agregados por unidad cartográfica, una fila por `mukey`, está en SSURGO, gSSURGO y SDA):

| Columna | Qué es | Unidad |
|---|---|---|
| `aws0100wta`, `aws0150wta` | agua disponible 0–100 y 0–150 cm, media ponderada | **cm** (multiplicar × 10 para comparar con `aws0_100` de Valu1) |
| `drclassdcd` | clase de drenaje natural dominante (por % de composición) | texto ("Well drained", "Moderately well drained", "Poorly drained", …) |
| `drclasswettest` | la clase más húmeda entre componentes ≥ 15 % | texto |
| `hydgrpdcd` | grupo hidrológico dominante | texto (A, B, C, D, A/D, B/D, C/D) |
| `wtdepannmin` | profundidad mínima a la napa en el año, componentes ≥ 15 % | cm |
| `wtdepaprjunmin` | profundidad mínima a la napa abril–junio | cm |

Prueba hecha en esta ronda (2026-11-14) contra SDA, condado de Story, Iowa (`areasymbol = 'IA169'`): `muaggatt` devuelve `aws0100wta = 19.24`, `drclassdcd = 'Well drained'`, `hydgrpdcd = 'B'`; `SELECT TOP 1 mukey, nccpi3corn FROM valu1` devuelve HTTP 400 `Invalid object name 'valu1'`.

**NCCPI en SDA** (sin Valu1): está en `cointerp`, con `mrulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)'` y reglas `NCCPI - NCCPI Corn Submodel (I)` y `NCCPI - NCCPI Soybeans Submodel (I)`, valor en `interphr` por componente (confirmado en la ronda 010 de `suelo_terreno`, ver `loop/notes/suelo_terreno.md`). Para llevarlo a la unidad cartográfica hay que ponderar por `comppct_r` y filtrar componentes principales, que es lo que Valu1 ya trae hecho.

**Geodatabase por estado vs SDA, para este proyecto:**

- El paquete `suelo_terreno` pide promediar por condado **solo los píxeles agrícolas** (máscara del CDL) ponderando por `MUKEY`. Eso necesita el raster MUKEY de 10 m, que SDA no da (SDA tiene polígonos por WFS, con extensión limitada por pedido). Con el raster + Valu1 se resuelve agua disponible, carbono, NCCPI y raíces; `muaggatt`, `component` y `chorizon` vienen en el mismo geodatabase.
- SDA conviene para lo tabular por `areasymbol` (un área de levantamiento por condado, p. ej. `IA169`): `muaggatt`, `component`, `chorizon` y `cointerp`, sin login y sin bajar GB. Límite: 100.000 filas por respuesta, así que hay que pedir por condado o por estado en partes.
- Ruta pública sin login para el raster: gNATSGO en Planetary Computer (`gnatsgo-rasters` con el asset `mukey` y columnas de Valu1 como COG de 10 m; `gnatsgo-tables` con `valu1`, `muaggatt`, `component`, `chorizon` en parquet, licencia CC0-1.0). Es un snapshot de julio de 2020; gSSURGO del NRCS se actualiza cada año fiscal, así que los valores pueden diferir algo de la versión vigente. En los estados del Corn Belt gNATSGO es casi todo SSURGO (STATSGO2 solo rellena huecos).
- Recomendación: raster MUKEY + Valu1 (gSSURGO por estado si se puede bajar del NRCS; si no, gNATSGO de Planetary Computer leyendo solo las teselas que tocan IA/IL/IN) y SDA para chorizon/component o para validar. No pude abrir hoy la página del NRCS (`nrcs.usda.gov` no respondió en 40 s), así que no verifiqué el tamaño actual del geodatabase por estado ni la versión vigente.

Fuentes: [gNATSGO Tables — item valu1 (Microsoft Planetary Computer STAC)](https://planetarycomputer.microsoft.com/api/stac/v1/collections/gnatsgo-tables/items/valu1), consultado 2026-11-14; [gNATSGO Tables — item muaggatt (Microsoft Planetary Computer STAC)](https://planetarycomputer.microsoft.com/api/stac/v1/collections/gnatsgo-tables/items/muaggatt), consultado 2026-11-14; [gNATSGO Rasters — colección (Microsoft Planetary Computer STAC)](https://planetarycomputer.microsoft.com/api/stac/v1/collections/gnatsgo-rasters), consultado 2026-11-14; [Soil Data Access Web Service Help (USDA NRCS)](https://sdmdataaccess.nrcs.usda.gov/WebServiceHelp.aspx), consultado 2026-11-14; consulta directa a `https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest`, consultado 2026-11-14.

Confianza: alta para los nombres y unidades de columnas (vienen de las descripciones oficiales de las tablas y se probaron en SDA); media para la recomendación (depende de si el geodatabase del NRCS se puede bajar sin login y de su tamaño, que no se verificó).

Impacto: paquete `suelo_terreno` (`src/suelo_terreno/download.py` y `process.py`): usar `nccpi3corn`, `nccpi3soy`, `nccpi3all`, `aws0_100`, `aws0_150`, `soc0_30`, `soc0_100`, `rootznemc` de Valu1 unidos por `mukey` al raster MUKEY; `drclassdcd`, `hydgrpdcd`, `wtdepannmin` de muaggatt; convertir `aws0100wta` de cm a mm si se usa en lugar de Valu1. Documentar en `docs/datasets/suelo_terreno.md` el uso de gNATSGO (julio 2020) si se reemplaza a gSSURGO.

Citas:
> "National Commodity Crop Productivity Index for Corn (weighted average) for major earthy components. Values range from .01 (low productivity) to .99 (high productivity)." — [gNATSGO Tables — item valu1](https://planetarycomputer.microsoft.com/api/stac/v1/collections/gnatsgo-tables/items/valu1)
> "This column displays the dominant drainage class for the map unit, based on composition percentage of each map unit component." — [gNATSGO Tables — item muaggatt](https://planetarycomputer.microsoft.com/api/stac/v1/collections/gnatsgo-tables/items/muaggatt)
> "Available water storage estimate (AWS) in standard zone 4 (0-100 cm depth), expressed in mm." — [gNATSGO Tables — item valu1](https://planetarycomputer.microsoft.com/api/stac/v1/collections/gnatsgo-tables/items/valu1)
> "Use this column to join the Component table to the Mapunit table and the valu1 table to the MapUnitRaster_10m raster map layer to map valu1 themes." — [gNATSGO Tables — item valu1](https://planetarycomputer.microsoft.com/api/stac/v1/collections/gnatsgo-tables/items/valu1)
> "A maximum of 100,000 rows may be returned." — [Soil Data Access Web Service Help](https://sdmdataaccess.nrcs.usda.gov/WebServiceHelp.aspx)
