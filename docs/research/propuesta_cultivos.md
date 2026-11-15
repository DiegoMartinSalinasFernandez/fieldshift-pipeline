# Propuesta: cultivos nuevos en el esquema (trigo de primavera, durum, cebada, girasol, canola, frijol seco, maíz para silo)

Pregunta: `para_decidir.md` #29 y `cuarta_tanda_decision.md` piden cultivos que el esquema no tiene: maíz para
silo (WI), trigo de primavera y girasol (SD, ND), durum, canola, cebada y frijol seco (ND). Para cada uno, ¿cuáles
son el `commodity_desc` y los `short_desc` exactos de NASS (rendimiento, superficie sembrada y cosechada,
producción) y su unidad, el factor a kg/ha con su fuente, los códigos del CDL, si Crop Progress lo publica y en qué
estados, y en qué estados del Corn Belt (los 10 de `config.yaml` más ND) pesa? ¿Qué cambios exactos harían falta
en `config/config.yaml`, `config/cultivos.csv`, `data/reference/clases_cdl.csv` y `src/common`?

Respuesta corta: **Se pueden sumar los siete**, con estos `short_desc` (tabla de NASS): `CORN, SILAGE - YIELD, MEASURED IN TONS / ACRE`, `WHEAT, SPRING, (EXCL DURUM) - ...`, `WHEAT, SPRING, DURUM - ...`, `BARLEY - ...` (BU / ACRE), `SUNFLOWER, OIL TYPE - ...`, `CANOLA - ...` y `BEANS, DRY EDIBLE, (EXCL CHICKPEAS) - ...` (LB / ACRE; producción en LB o CWT). Factores a kg/ha (AH-697): trigos 67,25, cebada 53,80, los de LB / ACRE 1,12085 y el silo 2.241,7 (tonelada corta por acre, **peso húmedo**). Por condado sirven hasta 2025 sobre todo en **ND** (todos), **MN** (trigo de primavera, cebada, silo), **SD** (trigo de primavera) y **WI** (silo, 851 mil ac, hasta 63 condados). El girasol de SD solo tiene condado hasta 2018 y casi nada tiene condado después de 2018 en NE y KS. Trigos y cebada no tienen 2024. El maíz para silo **no tiene superficie sembrada propia** en NASS ni clase en el CDL. CDL: girasol 6, cebada 21, durum 22, trigo de primavera 23, canola 31, frijol 42. Crop Progress: el reporte nacional tiene trigo de primavera (MN, ND, SD), cebada (MN, ND) y girasol (KS, ND, SD), y Quick Stats suma, desde 2014, canola y durum en ND y frijol en ND, MN y NE. El silo no tiene Crop Progress. Los cambios exactos a `config.yaml`, `src/common/conversiones.py`, `clases_cdl.csv` (vía `GRUPOS_CDL`), `cultivos.csv` y a los esquemas de `produccion_anual.csv`, `rotacion_anual.csv` y `fenologia_estado.csv` están al final. **No se aplicó ninguno.** Los parámetros agronómicos de `cultivos.csv` quedan vacíos porque no los investigué.

Detalle:

## Método

- **NASS por condado y estado.** `docs/research/propuesta_cultivos_items.py` (copia del mecanismo de
  `nass_mi_nd_conteo.py`, sin clave, interfaz web pública de Quick Stats) pidió, para `CORN` (solo `SILAGE`),
  `WHEAT`, `SUNFLOWER`, `CANOLA`, `BARLEY` y `BEANS`, encuesta, anual, `reference_period_desc=YEAR`, 2000–2025:
  - nivel **estado**, superficie sembrada y cosechada, en los 11 estados (los 10 de `config.yaml` + ND);
  - nivel **condado**, las cuatro variables, solo en ND, SD, MN y WI, más KS (girasol) y NE (silo, frijol, girasol).
    En IA, IL, IN, OH y MO no se pidió el condado: esos cultivos ahí casi no tienen superficie (salvo el silo, ver
    abajo). Se pidió así para que entrara en el tiempo de la tarea.
  Salida: `docs/research/propuesta_cultivos_items.csv` (estado, `short_desc`, años con al menos un condado sin
  contar "OTHER COUNTIES", primer y último año, máximo de condados en un año, si falta 2024, y media 2020–2025 de la
  fila de estado). Los CSV crudos (unos 240) quedaron en `/tmp/t103/qs`, fuera del repo.
  ```
  .venv/bin/python -X utf8 docs/research/propuesta_cultivos_items.py /tmp/t103/qs > docs/research/propuesta_cultivos_items.csv
  ```
- **Crop Progress.** `docs/research/propuesta_cultivos_cp.py` cuenta, en Quick Stats (`PROGRESS`, `STATE`), años con
  dato por etapa en ND, SD, MN, KS, NE y WI → `propuesta_cultivos_cp.csv`. Además revisé las tablas "Selected States"
  de cuatro reportes nacionales de 2026 (ESMIS `prog1826`, `prog2226`, `prog3226`, `prog4526`).
- **Conversiones.** Peso del bushel y factor lb/ac → kg/ha de USDA ERS, *Agricultural Handbook 697* (AH-697).

## `short_desc` de NASS por cultivo (encuesta, `ALL PRODUCTION PRACTICES`, `Domain = TOTAL`)

Todos siguen la regla de `nass_quickstats.md`: `commodity, class[, util] - estadística[, MEASURED IN unidad]`. La
superficie es `ACRES PLANTED` / `ACRES HARVESTED` (unidad ACRES).

| Cultivo propuesto | `commodity_desc` / `class_desc` | Rendimiento | Producción | Sembrada | Cosechada |
|---|---|---|---|---|---|
| maíz para silo | `CORN` / `ALL CLASSES`, util `SILAGE` | `CORN, SILAGE - YIELD, MEASURED IN TONS / ACRE` | `CORN, SILAGE - PRODUCTION, MEASURED IN TONS` | **no existe** (solo `CORN - ACRES PLANTED`, todos los usos) | `CORN, SILAGE - ACRES HARVESTED` |
| trigo de primavera | `WHEAT` / `SPRING, (EXCL DURUM)` | `WHEAT, SPRING, (EXCL DURUM) - YIELD, MEASURED IN BU / ACRE` | `... - PRODUCTION, MEASURED IN BU` | `WHEAT, SPRING, (EXCL DURUM) - ACRES PLANTED` | `... - ACRES HARVESTED` |
| durum | `WHEAT` / `SPRING, DURUM` | `WHEAT, SPRING, DURUM - YIELD, MEASURED IN BU / ACRE` | `... - PRODUCTION, MEASURED IN BU` | `WHEAT, SPRING, DURUM - ACRES PLANTED` | `... - ACRES HARVESTED` |
| cebada | `BARLEY` / `ALL CLASSES` | `BARLEY - YIELD, MEASURED IN BU / ACRE` | `BARLEY - PRODUCTION, MEASURED IN BU` | `BARLEY - ACRES PLANTED` | `BARLEY - ACRES HARVESTED` |
| girasol (aceitero) | `SUNFLOWER` / `OIL TYPE` | `SUNFLOWER, OIL TYPE - YIELD, MEASURED IN LB / ACRE` | `SUNFLOWER, OIL TYPE - PRODUCTION, MEASURED IN LB` | `SUNFLOWER, OIL TYPE - ACRES PLANTED` | `... - ACRES HARVESTED` |
| canola | `CANOLA` / `ALL CLASSES` | `CANOLA - YIELD, MEASURED IN LB / ACRE` | `CANOLA - PRODUCTION, MEASURED IN LB` | `CANOLA - ACRES PLANTED` | `CANOLA - ACRES HARVESTED` |
| frijol seco | `BEANS` / `DRY EDIBLE, (EXCL CHICKPEAS)` (2019–) y `DRY EDIBLE, INCL CHICKPEAS` (–2018) | `BEANS, DRY EDIBLE, (EXCL CHICKPEAS) - YIELD, MEASURED IN LB / ACRE` | `... - PRODUCTION, MEASURED IN CWT` | `... - ACRES PLANTED` | `... - ACRES HARVESTED` |

Notas:
- **Girasol:** `SUNFLOWER` (todas las clases) solo tiene condado **2000–2008**. Después, por condado, solo hay
  `OIL TYPE` y `NON-OIL TYPE` (confitero). Por eso se propone el aceitero.
- **Frijol seco:** cambia de `Data Item` en 2019 (`INCL CHICKPEAS` → `(EXCL CHICKPEAS)`), igual que en `nass_mi_nd.md`.
  Hay también clases por tipo (pinto, navy, black, great northern…) que se descartan.
- **Trigo:** `WHEAT` sin clase solo tiene condado en 2000–2007; en ND hay que usar las clases.
- Ningún valor de condado entre paréntesis en las filas contadas (el condado oculto no tiene fila), como en los
  research anteriores.

## Cobertura de condado y peso de cada estado

"Condado" = años con al menos un condado con rendimiento (de 26 posibles, 2000–2025) y máximo de condados en un año.
"Estado" = superficie media 2020–2025 de la fila de estado, en miles de acres (sembrada; en el silo, cosechada).
"—" = NASS no publica fila de estado en 2020–2025.

| Cultivo | ND | SD | MN | WI | NE | KS | IA | IL | IN | OH | MO |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Maíz para silo, estado | 209 | 455 | 402 | **851** | 288 | 297 | 327 | 97 | 117 | 175 | 103 |
| Maíz para silo, condado | 26 años (51) | 2000–2008 | 26 años (79) | 26 años (63) | 2000–2007 | no pedido | no pedido | no pedido | no pedido | no pedido | no pedido |
| Trigo de primavera, estado | **5.417** | 720 | 1.260 | — | — | — | — | — | — | — | — |
| Trigo de primavera, condado | 25 (53), sin 2024 | 25 (62), sin 2024 | 25 (55), sin 2024 | — | — | — | | | | | |
| Durum, estado | **969** | — | — | — | — | — | — | — | — | — | — |
| Durum, condado | 25 (51), sin 2024 | 2000–2008 (6) | solo 2002 (1) | — | | | | | | | |
| Cebada, estado | **558** | 35 | 54 | 15 | — | 13 | — | — | — | — | — |
| Cebada, condado | 25 (53), sin 2024 | 2000–2008 | 25 (30), sin 2024 | 2000–2008 | | | | | | | |
| Girasol (todos), estado | **567** | **504** | 64 | — | 42 | 36 | — | — | — | — | — |
| Girasol aceitero, condado | 25 (53) | 2000–2018 (43) | 2000–2017 | — | 2000–2017 | 2005–2017 | | | | | |
| Canola, estado | **1.825** | — | 81 | — | — | 7 | — | — | — | — | — |
| Canola, condado | 26 (49) | — | 2000–2007 | — | | | | | | | |
| Frijol seco, estado | **648** | — | 252 | — | 123 | — | — | — | — | — | — |
| Frijol seco, condado | 2000–2018 + 2020–2025 (38) | — | 2000–2018 | — | 2000–2018 | — | | | | | |

Para comparar: maíz + soja de ND suman unos 9,7 M acres (`cuarta_tanda_decision.md`). En ND, trigo de primavera +
durum + canola + cebada + girasol + frijol ≈ 10 M acres.

En resumen, **dónde sirven como cultivo con rendimiento por condado hasta 2025:**
- **ND:** todos (trigo de primavera, durum, cebada, girasol aceitero, canola, frijol seco, silo). Trigos y cebada sin 2024.
- **MN:** trigo de primavera, cebada (sin 2024) y silo. Girasol, canola y frijol solo hasta 2007–2018.
- **SD:** trigo de primavera (sin 2024). El girasol, que en SD pesa (504 mil ac), solo tiene condado hasta 2018;
  el silo, hasta 2008.
- **WI:** silo, 2000–2025 en hasta 63 condados (el cultivo de la lechería).
- **NE, KS:** nada después de 2018 (el silo de NE hasta 2007, el girasol hasta 2017).
- **IA, IL, IN, OH, MO:** solo silo a nivel estado (97–327 mil ac); no se contó su cobertura de condado.

## Conversión a kg/ha

AH-697 da el peso del bushel: trigo **60 lb**, cebada **48 lb** (y el "48-pound bushel of barley"); y "One pound per
acre equals 1.120 85 kilograms per hectare". El girasol (24–32 lb) y la colza/canola (50–60 lb) tienen bushels
variables en AH-697, pero NASS ya los publica en LB / ACRE, así que no hace falta el bushel. El frijol "Other, dry"
pesa 60 lb por bushel, pero NASS da LB / ACRE y la producción en CWT (100 lb). La tonelada corta es 2.000 lb
(AH-697, tabla de pesos).

| Cultivo | Unidad NASS del rendimiento | Factor a kg/ha | Cálculo |
|---|---|---|---|
| trigo de primavera, durum | BU / ACRE | 67,25 | 60 × 1,12085 |
| cebada | BU / ACRE | 53,80 | 48 × 1,12085 |
| girasol, canola, frijol seco | LB / ACRE | 1,12085 | AH-697 |
| maíz para silo | TONS / ACRE (corta, húmedo) | 2.241,7 (2,2417 t/ha) | 2.000 × 1,12085 |

El silo es **peso húmedo**: AH-697 no da una humedad estándar para el silo y no la supongo.

## Crop Progress

Dos fuentes, que no dicen lo mismo:

- **Reporte nacional semanal** (ESMIS, `prog*.txt`). Revisé cuatro de 2026 (semanas 18, 22, 32 y 45). Tablas
  "Selected States" de los cultivos propuestos: trigo de primavera (ID, **MN**, MT, **ND**, **SD**, WA), cebada
  (ID, **MN**, MT, **ND**, WA) y girasol (CO, **KS**, **ND**, **SD**). **No hay** tablas de canola, durum, frijol
  seco ni maíz para silo, igual que en `nass_mi_nd.md` y `nass_mo_wi_sd.md`.
- **Quick Stats** (`statisticcat_desc=PROGRESS`, `agg_level_desc=STATE`), que suma los reportes estatales. Ahí **sí
  hay** canola, durum y frijol seco en ND, y frijol en MN y NE. Años con dato, 2000–2025
  (`propuesta_cultivos_cp.csv`, de `propuesta_cultivos_cp.py`):

| Cultivo | Estado | Sembrado / cosechado | Emergido | Espigado o floración |
|---|---|---|---|---|
| Trigo de primavera | ND, SD, MN | 2000–2025 (26 años) | 2000–2025 | HEADED 2000–2025 |
| Durum | ND | 2014–2025 (12) | 2014–2025 | HEADED 2014–2025 |
| Cebada | ND, MN | 2000–2025 (26) | 2000–2025 | HEADED 2000–2025 |
| Cebada | SD | 2014–2017 (4) | 2014–2017 | 2014–2017 |
| Girasol | ND, SD, KS | 2000–2025 (26) | ND 2014–2025, SD 2014–2025 (7 años), KS 2014–2017 | BLOOMING: ND 2014–2025, SD 7 años, KS 2014–2017 |
| Girasol | MN | 2014–2025 (12) | — | — |
| Canola | ND | 2014–2025 (12) | 2014–2025 | BLOOMING 2014–2025 |
| Frijol seco | ND, MN, NE | `INCL CHICKPEAS` 2014–2018 (NE 2014–2017) y `(EXCL CHICKPEAS)` 2019–2025 | igual | BLOOMING, igual |
| Maíz para silo | — | no hay | — | — |

En WI, IA, IL, IN, OH, MO no hay Crop Progress de ninguno de estos cultivos en Quick Stats (no se consultaron IA,
IL, IN, OH y MO: ninguno aparece en las tablas nacionales; WI y NE sí se consultaron). El hueco de octubre–noviembre
de 2025 (`nass_mi_nd.md`) afecta también a la cosecha de girasol, canola y frijol.

## CDL

Los códigos ya están en `data/reference/clases_cdl.csv` (salen de los metadatos oficiales, `cdl_csb.md`), hoy con
grupo `otro`: girasol **6**, cebada **21**, durum **22**, trigo de primavera **23**, canola **31**, frijol seco
**42**. El maíz para silo no tiene clase: va dentro de maíz (1). Dobles cultivos con cebada: 233, 235, 237, 254.

Precisión (del productor / del usuario), de los research de precisión de este repo:

- **ND** (`cdl_precision_mi_nd.md`): trigo de primavera 83,9–93,4 % / 82,4–89,7 %; canola 86,9–96,7 % /
  92,2–97,3 %; girasol 71,4–91,7 % / 81,9–94,0 % (< 80 % del productor en 2017, 2018, 2021 y 2023). Se confunden
  trigo de primavera ↔ durum (3,9–7,4 % del de primavera queda como durum en 2024–2025) y avena ↔ cebada.
- **MI**: trigo de primavera, girasol y canola casi no existen y la precisión no sirve.
- **Sin medir en este repo:** durum (22), cebada (21) y frijol seco (42) en cualquier estado, y trigo de primavera y
  girasol en SD y MN. Antes de usar `pct_cebada`, `pct_trigo_durum` o `pct_frijol_seco` conviene sacarlos de los
  metadatos con `cdl_precision_mi_nd_extraer.py` agregando esas clases.

## Cambios propuestos (sin aplicar)

Son cambios de esquema: los decide el humano (CLAUDE.md §1.6) y `src/common/` y `config/` van en su propia
tarea con PR (MAQUINAS.md §5). Nada de esto está aplicado en este PR.

### 1. `config/config.yaml`

```yaml
cultivos:
  maiz: Maíz
  soja: Soja
  trigo_invierno: Trigo de invierno
  avena: Avena
  alfalfa: Alfalfa
  heno: Heno (otros)
  # Propuesta T103 (cultivos del norte y de la lechería)
  maiz_silo: Maíz para silo
  trigo_primavera: Trigo de primavera (sin durum)
  trigo_durum: Trigo durum
  cebada: Cebada
  girasol: Girasol aceitero
  canola: Canola
  frijol_seco: Frijol seco (sin garbanzo)

conversiones:
  # bu/ac -> kg/ha = peso del bushel (lb) × 1,12085 (AH-697: 1 lb/ac = 1,12085 kg/ha)
  bu_ac_a_kgha: {maiz: 62.77, soja: 67.25, trigo_invierno: 67.25, avena: 35.87,
                 trigo_primavera: 67.25, trigo_durum: 67.25, cebada: 53.80}
  lb_ac_a_kgha: 1.12085      # girasol, canola y frijol seco (NASS los da en LB / ACRE)
  ton_ac_a_tha: 2.2417       # maíz para silo: tonelada corta (2.000 lb) por acre -> t/ha, peso húmedo
  acre_a_ha: 0.4047
```

Los factores de bushel salen de AH-697: trigo 60 lb, cebada 48 lb (ver "Conversión"). 60 × 1,12085 = 67,25 y
48 × 1,12085 = 53,80. La tonelada corta es 2.000 lb = 907,18 kg; 907,18 / 0,404687 ha = 2.241,7 kg/ha = 2,2417 t/ha.

Una alternativa sin tocar la lista de `cultivos`: una segunda lista `cultivos_norte` que solo usen ND, SD, MN y WI.
No la recomiendo: el filtro por estado ya lo hace NASS (si no hay filas, no hay filas) y una sola lista es más simple
para `merge.py`.

### 2. `src/common/conversiones.py`

Hoy `bu_ac_a_kgha(cultivo)` solo sirve para bushels. Propuesta: una función por unidad de NASS, sin romper la actual.

```python
def rend_a_kgha(cultivo: str, unidad_nass: str) -> float:
    """Factor del rendimiento de NASS -> kg/ha según su UNIT_DESC.

    BU / ACRE   -> bu_ac_a_kgha(cultivo) (peso del bushel de cada cultivo)
    LB / ACRE   -> lb_ac_a_kgha (girasol, canola, frijol seco)
    TONS / ACRE -> ton_ac_a_tha * 1000 (maíz para silo, peso húmedo)
    """
    conv = cargar_config()["conversiones"]
    if unidad_nass == "BU / ACRE":
        return bu_ac_a_kgha(cultivo)
    if unidad_nass == "LB / ACRE":
        return float(conv["lb_ac_a_kgha"])
    if unidad_nass == "TONS / ACRE":
        return float(conv["ton_ac_a_tha"]) * 1000
    raise KeyError(f"sin factor a kg/ha para la unidad '{unidad_nass}' ({cultivo})")
```

Y en `validacion.py`, rangos físicos nuevos de `rend_kgha` (o de la unidad original). No los propongo con números:
habría que sacarlos de la serie real de cada cultivo una vez bajada, no suponerlos.

### 3. Esquema de `produccion_anual.csv`

Hoy: `fips, anio, cultivo, sup_sembrada_ac, sup_cosechada_ac, produccion_bu, rend_bu_ac, rend_kgha, sup_sembrada_ha,
ratio_cosechada, flag_nass`. Con girasol, canola, frijol y silo, `produccion_bu` y `rend_bu_ac` no alcanzan. Propuesta
(formato largo, mismas claves, columnas nuevas vacías donde no corresponden):

| Columna nueva | Unidad | Cultivos |
|---|---|---|
| `rend_lb_ac` | lb/acre | girasol, canola, frijol seco |
| `produccion_lb` | lb | girasol, canola |
| `produccion_cwt` | cwt (100 lb) | frijol seco |
| `rend_ton_ac` | tonelada corta/acre, húmedo | maíz para silo |
| `produccion_ton` | tonelada corta, húmedo | maíz para silo |

`rend_kgha` sigue siendo la columna común (con `rend_a_kgha`). En el maíz para silo es **peso húmedo**: hay que
decirlo en el data card, porque no es comparable con el grano. Para el silo, `sup_sembrada_ac` queda vacía: NASS da
la superficie sembrada de maíz para todos los usos, no la del silo (ver tabla de NASS). Alternativa más chica: dos
columnas genéricas `rend_valor` y `rend_unidad`; es menos cómoda para ML, por eso no la recomiendo.

En `src/cultivos/process.py` (no es `src/common`, pero lo anoto para la tarea que lo aplique), `NASS_CULTIVOS`
sumaría estas entradas (commodity, class, util de cosecha y producción), que salen de los `Data Item` de la tabla:

```python
"maiz_silo": ("CORN", "ALL CLASSES", "SILAGE"),
"trigo_primavera": ("WHEAT", "SPRING, (EXCL DURUM)", "ALL UTILIZATION PRACTICES"),
"trigo_durum": ("WHEAT", "SPRING, DURUM", "ALL UTILIZATION PRACTICES"),
"cebada": ("BARLEY", "ALL CLASSES", "ALL UTILIZATION PRACTICES"),
"girasol": ("SUNFLOWER", "OIL TYPE", "ALL UTILIZATION PRACTICES"),  # ALL CLASSES de condado termina en 2008
"canola": ("CANOLA", "ALL CLASSES", "ALL UTILIZATION PRACTICES"),
"frijol_seco": ("BEANS", "DRY EDIBLE, (EXCL CHICKPEAS)", "ALL UTILIZATION PRACTICES"),  # 2019–
# y para 2000–2018 la clase "DRY EDIBLE, INCL CHICKPEAS" (NASS_CULTIVOS tendría que aceptar dos clases por cultivo)
```

y `variables` tendría que aceptar más de una unidad por variable (`BU / ACRE`, `LB / ACRE`, `TONS / ACRE`; `BU`, `LB`,
`CWT`, `TONS`). En el girasol se propone `OIL TYPE` porque `ALL CLASSES` (aceitero + confitero) solo tiene condado
hasta 2008; el confitero (`NON-OIL TYPE`) queda afuera y el data card lo tiene que decir.

### 4. `data/reference/clases_cdl.csv`

Cambiar solo la columna `grupo` (el código y el nombre son los oficiales y no cambian):

| codigo | nombre | grupo hoy | grupo propuesto |
|---|---|---|---|
| 6 | Sunflower | otro | girasol |
| 21 | Barley | otro | cebada |
| 22 | Durum Wheat | otro | trigo_durum |
| 23 | Spring Wheat | otro | trigo_primavera |
| 31 | Canola | otro | canola |
| 42 | Dry Beans | otro | frijol_seco |

El maíz para silo **no tiene clase propia**: en el CDL va como maíz (1). No se puede separar del grano por píxel.
Los dobles cultivos con cebada (233, 235, 237, 254) siguen como `otro`. Como `clases_cdl.csv` se genera con
`clases_cdl()` desde `GRUPOS_CDL` en `src/cultivos/process.py`, el cambio real va ahí:

```python
GRUPOS_CDL = {1: "maiz", 5: "soja", 6: "girasol", 21: "cebada", 22: "trigo_durum", 23: "trigo_primavera",
              24: "trigo_invierno", 26: "doble_trigo_soja", 28: "avena", 31: "canola", 36: "alfalfa",
              37: "heno", 42: "frijol_seco", 61: "barbecho", 176: "pastizal"}
```

Y en `rotacion_anual.csv`, columnas nuevas de `PCT_CLASES` (cambia el esquema): `pct_trigo_primavera: [23]`,
`pct_trigo_durum: [22]`, `pct_cebada: [21]`, `pct_girasol: [6]`, `pct_canola: [31]`, `pct_frijol_seco: [42]`.
Además, `pct_trigo` hoy es `[24, 26]`; en ND conviene que sea todo el trigo, `[22, 23, 24, 26]`
(`cdl_precision_mi_nd.md`: el CDL confunde trigo de invierno, primavera y durum). Las clases ya están dentro de
`AGRICOLA` (1–61), así que la máscara agrícola no cambia.

### 5. `config/cultivos.csv`

Siete filas nuevas con la clave y el nombre. **El resto de los parámetros no los completo**: son agronómicos (FAO-56,
Handbook 628, etc.) y no los investigué en esta tarea; ponerlos sin fuente sería inventar. Propongo una tarea de
research como la #1 de la cola (§8) para llenarlos.

```csv
maiz_silo,Maíz para silo,,,,,,,,,,,,,,,,,,,,,,,,,,,,
trigo_primavera,Trigo de primavera (sin durum),,,,,,,,,,,,,,,,,,,,,,,,,,,,
trigo_durum,Trigo durum,,,,,,,,,,,,,,,,,,,,,,,,,,,,
cebada,Cebada,,,,,,,,,,,,,,,,,,,,,,,,,,,,
girasol,Girasol aceitero,,,,,,,,,,,,,,,,,,,,,,,,,,,,
canola,Canola,,,,,,,,,,,,,,,,,,,,,,,,,,,,
frijol_seco,Frijol seco (sin garbanzo),,,,,,,,,,,,,,,,,,,,,,,,,,,,
```

Para `maiz_silo` la mayoría de los parámetros son los del maíz (misma planta), salvo la cosecha (antes, con la
planta verde) y el Kc final y el rastrojo (casi no queda). Eso también lo tiene que confirmar research.

### 6. `fenologia_estado.csv`

Columnas iguales (`doy_50_sembrado, doy_50_emergido, doy_50_floracion, doy_50_cosechado`), filas nuevas por cultivo.
Los `Data Item` de Quick Stats (`statisticcat_desc=PROGRESS`, `agg_level_desc=STATE`):

| cultivo | commodity / class | sembrado | emergido | floración (columna) | cosechado |
|---|---|---|---|---|---|
| trigo_primavera | `WHEAT, SPRING, (EXCL DURUM)` | PCT PLANTED | PCT EMERGED | PCT HEADED (espigado) | PCT HARVESTED |
| trigo_durum | `WHEAT, SPRING, DURUM` | PCT PLANTED | PCT EMERGED | PCT HEADED | PCT HARVESTED |
| cebada | `BARLEY` | PCT PLANTED | PCT EMERGED | PCT HEADED | PCT HARVESTED |
| girasol | `SUNFLOWER` | PCT PLANTED | PCT EMERGED | PCT BLOOMING | PCT HARVESTED |
| canola | `CANOLA` | PCT PLANTED | PCT EMERGED | PCT BLOOMING | PCT HARVESTED |
| frijol_seco | `BEANS, DRY EDIBLE, (EXCL CHICKPEAS)` (2019–) e `INCL CHICKPEAS` (2014–2018) | PCT PLANTED | PCT EMERGED | PCT BLOOMING | PCT HARVESTED |

En los cereales, "floración" sería en realidad el espigado (HEADED): conviene documentarlo o renombrar la columna a
`doy_50_floracion_o_espigado` (cambio de esquema). El maíz para silo no tiene Crop Progress propio.

## Lo que no cubre

- La cobertura de condado del silo en IA, IL, IN, OH, MO y KS (no se pidió).
- La precisión del CDL para durum, cebada y frijol, y para trigo de primavera y girasol en SD y MN.
- Los parámetros agronómicos de `cultivos.csv` (Kc, GDD, fechas, raíces, etc.) de los siete cultivos.
- Las prácticas `IRRIGATED` / `NON-IRRIGATED` (el frijol y el silo de NE se riegan en parte).
- Los conteos son del 2026-11-15 y cambian si NASS revisa.

Fuentes:
- [USDA NASS Quick Stats, interfaz web](https://quickstats.nass.usda.gov/), consultas del 2026-11-15 con `propuesta_cultivos_items.py` y `propuesta_cultivos_cp.py`.
- [Crop Progress (USDA NASS, archivo ESMIS)](https://esmis.nal.usda.gov/publication/crop-progress), reportes [prog1826](https://esmis.nal.usda.gov/sites/default/release-files/795893/prog1826.txt), [prog2226](https://esmis.nal.usda.gov/sites/default/release-files/795928/prog2226.txt), [prog3226](https://esmis.nal.usda.gov/sites/default/release-files/796012/prog3226.txt) y [prog4526](https://esmis.nal.usda.gov/sites/default/release-files/796141/prog4526.txt), consultados 2026-11-15.
- [Weights, Measures, and Conversion Factors for Agricultural Commodities and Their Products, AH-697 (USDA ERS)](https://www.ers.usda.gov/media/7780/ah-697.pdf), consultado 2026-11-15.
- `docs/research/nass_mi_nd.md`, `nass_mo_wi_sd.md`, `nass_quickstats.md`, `cdl_csb.md`, `cdl_precision_mi_nd.md`, `cuarta_tanda_decision.md`, de este repo.

Confianza:
- **Alta:** `short_desc`, unidades, años y condados (salen directo de Quick Stats), factores de AH-697, códigos del CDL, tablas de Crop Progress.
- **Media:** el peso por estado (media 2020–2025 de la fila de estado; el silo usa la cosechada).
- **Es recomendación mía, no un dato:** el diseño de columnas nuevas y la elección del girasol aceitero.

Impacto: ninguno hasta que decida el humano. Si se aprueba: `config/config.yaml` (cultivos y conversiones),
`src/common/conversiones.py` (`rend_a_kgha`) y `validacion.py` (rangos), `src/cultivos/process.py` (`NASS_CULTIVOS`,
`GRUPOS_CDL`, `PCT_CLASES`, etapas de Crop Progress) → `data/reference/clases_cdl.csv`, `config/cultivos.csv` (filas
nuevas + research de parámetros), y el esquema de `produccion_anual.csv`, `rotacion_anual.csv` y `fenologia_estado.csv`.

