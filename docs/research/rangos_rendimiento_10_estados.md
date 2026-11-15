# Rangos de rendimiento para los 10 estados (T145)

Pregunta: ¿los rangos de rendimiento propuestos en `para_decidir.md` #24 (maíz 5–300, soja 2–100, trigo de
invierno 5–130, avena 2–200 bu/ac) dejan afuera algún rendimiento real de condado de los 10 estados de
`config.yaml` (IA, IL, IN, OH, NE, MN, KS, MO, WI, SD) entre 2000 y 2025?

Respuesta corta: **Casi todo entra; hay dos excepciones, las dos en SD.** (1) El maíz de **Pennington, SD, 2002**
tiene 4,5 bu/ac, debajo del mínimo propuesto de 5: propongo **maíz 2–300**. (2) NASS publica **rendimiento 0**
en 19 filas de condado (maíz y avena de SD, 2000–2006: Lawrence, Harding, Custer, Stanley, Mellette) que no
tienen superficie cosechada ni producción de grano (todo fue a silo o a forraje). Propongo aceptar el 0 solo en
esas condiciones (sin `sup_cosechada_ac` ni `produccion_bu`, o con 0). Soja, trigo de invierno y avena entran
en los rangos propuestos, incluido el riego y el secano.

## Extremos reales (encuesta NASS por condado, 2000–2025, sin `county_code` 998)

Fuente: base completa de Quick Stats `data/raw/cultivos/nass/qs.crops_20261114.txt.gz` (bajada el 2026-11-14,
solo lectura), con los filtros de `src/cultivos/process.py` (`CORN`/`GRAIN`, `SOYBEANS`, `WHEAT`/`WINTER`,
`OATS`; `source_desc=SURVEY`, `agg_level_desc=COUNTY`, `unit_desc=BU / ACRE`). Scripts:
`rangos_rendimiento_10_estados.sh` y `rangos_rendimiento_10_estados_resumen.py`.

| Cultivo | Práctica | n | mín. | mín. > 0 | máx. | Rango propuesto |
|---|---|---|---|---|---|---|
| maíz | todas | 20.013 | 0 (19 filas, SD) | **4,5** (Pennington SD 2002); 13,3 (Oglala Lakota SD 2004); 18,0 (Russell KS 2002) | 253,6 (Stark IL 2025) | **2–300** (era 5–300) |
| maíz | riego | 2.402 | 0 (SD 2000) | — | 234,3 (Buffalo NE 2018) | |
| maíz | secano | 2.551 | 0 (SD, NE, KS) | — | 209,0 (Doniphan KS 2014) | |
| soja | todas | 19.149 | 2,9 (Pennington SD 2003) | 2,9 | 80,4 (Sangamon IL 2018) | 2–100 |
| soja | riego / secano | 1.384 / 1.338 | 15,0 / 0 (KS 2002–2003) | — | 74,3 / 62,4 | |
| trigo de invierno | todas | 12.044 | 8,7 (Kimball NE 2022) | 8,7 | 117,8 (Bureau IL 2024) | 5–130 |
| trigo de invierno | riego / secano | 939 / 2.116 | 13,0 / 7,2 (Morton KS 2013) | — | 99,0 / 80,0 | |
| avena | todas | 6.104 | 0 (7 filas, SD 2002–2004) | 5,0 (Dundy NE 2000) | 133,6 (Hamilton IA 2023) | 2–200 |

El 0 de riego y secano también aparece (maíz y soja de secano de KS y NE). `produccion_anual.csv` hoy solo trae
`ALL PRODUCTION PRACTICES`, pero si se agregan columnas de secano (`riego_nass.md`) la misma regla del 0 sin
cosecha las cubre.

Ejemplo, SD Lawrence 2003 (maíz): `CORN, GRAIN - YIELD` = 0, sin `ACRES HARVESTED` ni `PRODUCTION` de grano;
`CORN, SILAGE - ACRES HARVESTED` = 500. No es un relleno: es un condado sin cosecha de grano.

## MO, WI, SD, ND, MI y KY (research previos)

- `eventos_extremos_mo_wi_sd.md` y su CSV: solo rendimientos **estatales** (mín. maíz 75 bu/ac, MO 2012);
  todo entra. Los de condado de MO, WI y SD salen de la tabla de arriba.
- `nass_mo_wi_sd.md`: no tiene rendimientos, solo conteos de condados.
- `eventos_extremos_mi_nd.md`, `eventos_extremos_ky.md`: ND, MI y KY no están en `config.yaml`; sus cifras son
  estatales o de prensa (KY trigo 2007: 30–70 bu/ac) y entran en los rangos. No calculé sus condados.

## Antes y después con los releases

No pude bajar los releases (sin acceso a `gh` ni a la API de GitHub en esta corrida). Usé las copias locales:

| Archivo | Antes (`main`) | Después |
|---|---|---|
| `fieldshift_datos_v1.3/condado/tabla_anual.csv` (IA, IL, IN) | `rend_bu_ac de maiz: 1 valores fuera de 20-300` (Marion IL 17121, 2012: 19,0 bu/ac, dato real de NASS) | sin errores de rendimiento |
| `datos-oh-ne-mn_cultivos.zip` → `produccion_anual.csv` (OH, NE, MN) | sin errores de rendimiento | sin errores de rendimiento (avena mín. 5,0 y trigo mín. 8,7 ahora se chequean y entran) |
| `data/demo_zips/ex/.../produccion_anual.csv` | sin errores de rendimiento | sin errores de rendimiento |

El otro error que aparece en los tres ("fips que no están en condados.csv") se debe a que el `condados.csv`
local de esta máquina tiene solo NE y KS; es igual antes y después. Falta correrlo con los releases de KS y de
MO, WI y SD.

Confianza: alta para los extremos (valores finales de NASS leídos de la base completa); media para la regla
del 0 (es una decisión de diseño).
Impacto: `src/common/validacion.py` (`RENDIMIENTO_BU_AC`, `SIN_COSECHA`) y `loop/spec/entregables.yaml`
(check `consistencia_rendimiento`, `tmin_c`/`tmed_c` diarios); lo aprueba el humano (para_decidir #24).
