"""Data card del paquete seguro (docs/datasets/seguro.md), generado por process.py."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
CARD = REPO / "docs" / "datasets" / "seguro.md"

F_SOB = "USDA RMA Summary of Business (sobtpu)"
F_COL = "USDA RMA Cause of Loss (colsom)"
DESC = {
    "seguro_anual.csv": [
        ("sup_asegurada_ac", "Superficie asegurada neta (Net Reporting Level Amount × participación), solo filas con Reporting Level Type = Acres; suma de planes, coberturas, tipos y prácticas", "acres", F_SOB),
        ("sup_asegurada_secano_ac", "Parte de sup_asegurada_ac en prácticas de secano (Non-Irrigated, Summerfallow, Continuous Cropping y variantes)", "acres", F_SOB),
        ("sup_asegurada_riego_ac", "Parte de sup_asegurada_ac en prácticas con riego (Irrigated, Irr., Limited Irrigation)", "acres", F_SOB),
        ("responsabilidad_usd", "Responsabilidad (liability): monto máximo asegurado, todos los planes (incluidos los endosos de área)", "USD", F_SOB),
        ("prima_total_usd", "Prima total antes de subsidios", "USD", F_SOB),
        ("indemnizacion_usd", "Indemnización total", "USD", F_SOB),
        ("loss_ratio", "indemnizacion_usd / prima_total_usd (vacío si la prima es 0)", "proporción", F_SOB),
        ("loss_cost", "indemnizacion_usd / responsabilidad_usd (vacío si la responsabilidad es 0)", "proporción", F_SOB),
        ("sup_con_perdida_ac", "Superficie con pérdida (Net Determined Quantity), suma de todas las causas", "acres", F_COL),
        ("indem_causas_usd", "Indemnización total del archivo de causas (suma de los grupos)", "USD", F_COL),
        ("indem_sequia_usd", "Indemnización por sequía (causa 11)", "USD", F_COL),
        ("indem_exceso_agua_usd", "Indemnización por exceso de humedad o lluvia e inundación (31, 51)", "USD", F_COL),
        ("indem_calor_usd", "Indemnización por calor y viento caliente (12, 62)", "USD", F_COL),
        ("indem_granizo_usd", "Indemnización por granizo (21)", "USD", F_COL),
        ("indem_helada_usd", "Indemnización por helada, congelamiento e invierno frío (41, 42, 43)", "USD", F_COL),
        ("indem_frio_humedo_usd", "Indemnización por tiempo frío y húmedo (44)", "USD", F_COL),
        ("indem_viento_usd", "Indemnización por viento, ciclón, tornado y huracán (61, 63, 64, 92)", "USD", F_COL),
        ("indem_enfermedad_plagas_usd", "Indemnización por roya asiática, insectos, enfermedades y micotoxinas (09, 71, 81, 82)", "USD", F_COL),
        ("indem_precio_usd", "Indemnización por baja de precio (01; seguros de ingreso). No es clima", "USD", F_COL),
        ("indem_area_usd", "Indemnización de planes de área (55: ARPI, SCO, ECO, STAX, MP...). Sin causa física", "USD", F_COL),
        ("indem_otras_usd", "Indemnización por el resto de las causas (riego 13-15, incendio, fauna, 99, XX 'All Other Causes', códigos no listados)", "USD", F_COL),
        ("frac_indem_clima", "(sequía + exceso de agua + calor + granizo + helada + frío húmedo + viento) / indem_causas_usd; vacío si el total es ≤ 0", "proporción", F_COL),
        ("trigo_frac_invierno", "Solo cultivo = trigo: fracción de sup_asegurada_ac con Type Name = Winter", "proporción", F_SOB),
    ],
    "seguro_mensual.csv": [
        ("indem_sequia_usd", "Indemnización por sequía (11) con pérdida en ese mes", "USD", F_COL),
        ("indem_exceso_agua_usd", "Ídem, exceso de agua (31, 51)", "USD", F_COL),
        ("indem_calor_usd", "Ídem, calor (12, 62)", "USD", F_COL),
        ("indem_granizo_usd", "Ídem, granizo (21)", "USD", F_COL),
        ("indem_helada_usd", "Ídem, helada (41, 42, 43)", "USD", F_COL),
        ("indem_frio_humedo_usd", "Ídem, frío húmedo (44)", "USD", F_COL),
        ("indem_viento_usd", "Ídem, viento (61, 63, 64, 92)", "USD", F_COL),
        ("indem_enfermedad_plagas_usd", "Ídem, enfermedad y plagas (09, 71, 81, 82)", "USD", F_COL),
        ("indem_precio_usd", "Ídem, baja de precio (01)", "USD", F_COL),
        ("indem_area_usd", "Ídem, planes de área (55)", "USD", F_COL),
        ("indem_otras_usd", "Ídem, resto de las causas", "USD", F_COL),
        ("indem_total_usd", "Suma de los grupos", "USD", F_COL),
        ("sup_con_perdida_ac", "Superficie con pérdida en ese mes (Net Determined Quantity)", "acres", F_COL),
    ],
}

CAUSAS = [
    ("01", "Decline in Price", "precio"), ("09", "Asian Soybean Rust", "enfermedad_plagas"),
    ("11", "Drought", "sequia"), ("12", "Heat", "calor"),
    ("13, 14, 15", "Failure of Irrigation Supply / Equipment, Inability to prepare land for irrigation", "otras"),
    ("21", "Hail", "granizo"), ("31", "Excess Moisture/Precipitation/Rain", "exceso_agua"),
    ("41", "Frost", "helada"), ("42", "Freeze", "helada"), ("43", "Cold Winter", "helada"),
    ("44", "Cold Wet Weather", "frio_humedo"), ("51", "Flood", "exceso_agua"),
    ("55", "ARPI/SCO/ECO/STAX/MP/HIP-WI/PACE Crops Only", "area"),
    ("61", "Wind/Excess Wind", "viento"), ("62", "Hot Wind", "calor"), ("63", "Cyclone", "viento"),
    ("64", "Tornado", "viento"), ("71", "Insects", "enfermedad_plagas"),
    ("81", "Plant Disease", "enfermedad_plagas"), ("82", "Mycotoxin", "enfermedad_plagas"),
    ("92", "Hurricane / Tropical Storm", "viento"),
    ("85, 87, 91, 93, 97, 98, 99", "Ordered Destruction, Falling Numbers, Fire, Wildlife, Earthquake, Volcano, Other", "otras"),
    ("XX", "All Other Causes", "otras"), ("cualquier otro", "códigos viejos o nuevos no listados", "otras"),
]

TEXTO = """# Data card — paquete `seguro`

Seguro agrícola federal de EE.UU. (USDA Risk Management Agency, RMA) por condado, año de cosecha y
cultivo: participación (superficie asegurada, responsabilidad, prima), indemnizaciones y su
causa, y el mes de la pérdida. Implementa la propuesta de `docs/research/rma_causa_perdida.md`
(T016). Generado por `src/seguro/process.py`: no editar a mano, se reescribe en cada corrida.

**Esquema nuevo, pendiente de OK del humano** (`coordinacion/para_decidir.md`, fila 6). No está
en `loop/spec/entregables.yaml` ni en `src/merge.py`.

## Fuentes

| Archivo en `data/raw/seguro/` | Producto | URL |
|---|---|---|
| `colsom_<AAAA>.zip` (2000–2025) | Cause of Loss Summary of Business with Month of Loss | https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/ |
| `sobtpu_<AAAA>.zip` (2000–2025) | Summary of Business por tipo, práctica y estructura de unidad | https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop/ |
| `COL_Summary_of_Business_with_Month_All_Years.pdf`, `Stage_Code_Listing.pdf`, `SOBTPU_External_All_Years.pdf` | diccionarios oficiales | mismos directorios |

Licencia: CC0 1.0 (data.gov). Los zips son nacionales; el filtro por estado
(`FIELDSHIFT_ESTADOS`) y por cultivo se hace al procesar. Formato verificado al bajar: un `.txt`
por zip, separador `|`, **sin encabezado**, 30 columnas (colsom) y 27 (sobtpu), campos de texto
rellenos con espacios; colsom termina las líneas con CRLF y sobtpu con CR solo.

## Cultivos

| `cultivo` | Código RMA | Nota |
|---|---|---|
| `maiz` | 0041 CORN | todos los tipos (Grain, High Amylose, White, Waxy...); no incluye 0042 sweet corn, 0043 popcorn ni 0062 semilla híbrida |
| `soja` | 0081 SOYBEANS | |
| `trigo` | 0011 WHEAT | **invierno y primavera juntos**: el archivo de causas no tiene tipo. `trigo_frac_invierno` (de sobtpu) dice qué parte de la superficie asegurada es de invierno |
| `avena` | 0016 OATS | poco asegurada: muchos condados sin filas |

## Archivos y columnas

Claves: `fips, anio, cultivo` (anual) y `fips, anio, mes, cultivo` (mensual).

| Archivo | Columna | Descripción | Unidad | Fuente | Desde | Hasta | % faltantes |
|---|---|---|---|---|---|---|---|
{tabla}

## Causas → grupos

Códigos del Exhibit 10 del manual FCIC-25010 (2026). Se agrupa por el código (columna 12), no
por la descripción.

| Código | Causa (RMA) | Grupo (`indem_<grupo>_usd`) |
|---|---|---|
{causas}

Códigos de causa que aparecieron en los datos procesados, con su indemnización total:

| Código | Descripción en los datos | Grupo | Filas | Indemnización (USD) |
|---|---|---|---|---|
{causas_datos}

## Cobertura de esta corrida

- Estados: {estados}.
- Filas: `seguro_anual.csv` {n_anual} (grilla completa condado × año × cultivo), de las cuales
  {n_con_datos} tienen participación o pérdidas; `seguro_mensual.csv` {n_mensual}.
- Años con datos: {anios}.
- Archivos que faltaban en raw: {faltan}.

Condados con superficie asegurada > 0, por estado, cultivo y algunos años:

| Estado | Cultivo | {cab_anios} |
|---|---|{sep_anios}|
{cobertura}

Comparación entre las dos fuentes (indemnización total de los estados procesados, todos los años):
sobtpu {indem_sob}, colsom {indem_col}.

## Condados que no están en `condados.csv`

RMA usa códigos FIPS de estado y condado. Las filas cuyo `fips` no está en
`data/reference/condados.csv` se **descartan** (no hay a qué condado asignarlas). Son sobre todo
el código 999 "All Other Counties" (agrupa condados con poca actividad, como el 998 de NASS).
Lo descartado en esta corrida:

| Archivo | fips | Condado (RMA) | Filas | Indemnización (USD) |
|---|---|---|---|---|
{fuera}

## Faltantes y ceros

- Celda vacía = no hay dato (CLAUDE.md §4).
- En `seguro_anual.csv`, si el condado no tiene filas en sobtpu **ni** en colsom para ese año y
  cultivo, toda la fila queda vacía (sin participación en el seguro).
- **Excepción al "nunca 0"**: si el condado tiene filas en sobtpu o en colsom, la indemnización de
  los grupos de causa sin filas es **0**. Es un dato real (no hubo pérdidas por esa causa), no un
  relleno: el archivo de causas solo lista las combinaciones que existen. Lo mismo para
  `sup_con_perdida_ac`.
- `sup_asegurada_*`, `responsabilidad_usd`, `prima_total_usd` e `indemnizacion_usd` quedan vacías
  cuando no hay filas en sobtpu (aunque haya pérdidas en colsom).
- `loss_ratio`, `loss_cost` y `frac_indem_clima` quedan vacías cuando el denominador es 0 o
  vacío. `trigo_frac_invierno` está vacía salvo en `trigo`.
- `seguro_mensual.csv` solo tiene los meses con alguna pérdida registrada; un mes que no está
  significa que no hubo indemnizaciones con pérdida en ese mes.

## Supuestos

- `anio` (anual) = Commodity Year de RMA, el año de cosecha de la póliza.
- En `seguro_mensual.csv`, `mes` = Year of Loss + Month of Loss y `anio` es el año de ese mes. Si
  un mes recibe pérdidas de dos años de cosecha (trigo de invierno dañado en otoño), se suman. Se
  descartaron las filas sin mes o sin año de pérdida válidos ({sin_mes} filas, {indem_sin_mes}
  USD). En los años de cosecha {anios_sin_anio} el archivo de RMA trae el mes pero deja vacío el
  Year of Loss en todas las filas: esos años no tienen filas en el mensual (no se adivina el año
  de un mes que puede ser del otoño anterior). También se descartaron las que tienen un
  año de pérdida a más de un año del de cosecha ({lejanas} filas, {indem_lejanas} USD; p. ej.
  trigo de 2023 con pérdida en 2003, errores evidentes de carga). En el anual sí cuentan.
- La superficie asegurada suma todos los planes; los endosos y planes de área (SCO, ECO, MP...)
  vienen con 0 acres en sobtpu y no la duplican, pero su responsabilidad, prima e indemnización
  sí se suman.
- Práctica → riego/secano por el nombre (Practice Name), no por el código: "Non-Irr..." es
  secano, "...Irr..." es riego, "Summerfallow" y "Continuous Cropping" (trigo de las Grandes
  Llanuras) son secano; "No Practice Specified" y otras quedan solo en el total. Por eso
  riego + secano puede ser menor que el total.
- Las columnas de participación del archivo de causas (17, 19–27) no se usan: el denominador sale
  de sobtpu (research T016).
- No se quita la tendencia de la participación ni se calculan percentiles o z-scores (lo decide
  ML).

## Problemas conocidos

- El archivo de causas no separa riego de secano: en NE y KS la indemnización por sequía de un
  condado se diluye en una responsabilidad que incluye superficie regada.
- `trigo` junta invierno y primavera (en MN es sobre todo trigo de primavera).
- RMA revisa los años recientes (2022–2026 se actualizaron el 2026-11-09); la fecha
  Last-Modified de cada zip queda en `manifest.csv`. Para tomar una revisión nueva, borrar el zip
  de `data/raw/seguro/` y volver a bajar.
- Montos en dólares corrientes, sin deflactar.
- La participación en el seguro creció mucho desde 2000: comparar entre años con `loss_cost` o
  con `sup_con_perdida_ac / sup_asegurada_ac`, no con montos absolutos.
"""


def _fmt_usd(x: float) -> str:
    return f"{x:,.0f}"


def escribir(anual, mensual, col_fuera, sob_fuera, descartes, faltan, col_ok, sob_ok, estados) -> None:
    filas = []
    for archivo, df in (("seguro_anual.csv", anual), ("seguro_mensual.csv", mensual)):
        for nombre, desc, unidad, fuente in DESC[archivo]:
            s = df[nombre] if nombre in df else pd.Series(dtype=float)
            falt = 100 * s.isna().mean() if len(s) else 100.0
            llenos = df.loc[s.notna(), "anio"] if len(s) else pd.Series(dtype=int)
            desde = str(llenos.min()) if len(llenos) else ""
            hasta = str(llenos.max()) if len(llenos) else ""
            filas.append(f"| {archivo} | {nombre} | {desc} | {unidad} | {fuente} | {desde} | {hasta} | {falt:.1f} |")
    causas = "\n".join(f"| {c} | {d} | {g} |" for c, d, g in CAUSAS)

    from src.seguro.process import grupo_causa, _num  # noqa: E402
    if len(col_ok):
        cd = col_ok.assign(indem=_num(col_ok["indemnizacion"]))
        cd["causa"] = cd["causa"].str.replace('"', "", regex=False).str.replace("`", "", regex=False)
        cd = cd.groupby("cod_causa").agg(
            causa=("causa", lambda x: "; ".join(sorted({v for v in x if v}))),
            filas=("indem", "size"), indem=("indem", "sum")).reset_index()
        causas_datos = "\n".join(f"| {r.cod_causa} | {r.causa} | {grupo_causa(r.cod_causa)} | {r.filas} | {_fmt_usd(r.indem)} |"
                                 for r in cd.itertuples())
    else:
        causas_datos = "| | | | | |"

    con = anual[anual["indem_causas_usd"].notna() | anual["sup_asegurada_ac"].notna()]
    anios_datos = sorted(con["anio"].unique())
    muestra = [a for a in (2000, 2005, 2010, 2015, 2020, 2024, 2025) if a in anios_datos] or anios_datos[:7]
    alfa = {e["fips"]: k for k, e in estados.items()}
    cob = anual[anual["sup_asegurada_ac"] > 0].assign(estado=lambda d: d["fips"].str[:2].map(alfa))
    tabla_cob = []
    for (est, cult), g in cob.groupby(["estado", "cultivo"]):
        cuenta = g.groupby("anio")["fips"].nunique()
        tabla_cob.append(f"| {est} | {cult} | " + " | ".join(str(int(cuenta.get(a, 0))) for a in muestra) + " |")

    fuera = []
    for nombre, df in (("colsom", col_fuera), ("sobtpu", sob_fuera)):
        if len(df):
            g = df.assign(indem=_num(df["indemnizacion"])).groupby(["fips", "cty_nombre"]).agg(
                filas=("indem", "size"), indem=("indem", "sum")).reset_index()
            fuera += [f"| {nombre} | {r.fips} | {r.cty_nombre} | {r.filas} | {_fmt_usd(r.indem)} |" for r in g.itertuples()]

    indem_sob = _num(sob_ok["indemnizacion"]).sum() if len(sob_ok) else 0.0
    indem_col = _num(col_ok["indemnizacion"]).sum() if len(col_ok) else 0.0
    texto = (TEXTO.replace("{tabla}", "\n".join(filas))
             .replace("{causas}", causas)
             .replace("{causas_datos}", causas_datos)
             .replace("{estados}", ", ".join(sorted(estados)))
             .replace("{n_anual}", f"{len(anual):,}")
             .replace("{n_con_datos}", f"{len(con):,}")
             .replace("{n_mensual}", f"{len(mensual):,}")
             .replace("{anios}", f"{anios_datos[0]}–{anios_datos[-1]}" if anios_datos else "ninguno")
             .replace("{faltan}", ", ".join(faltan) if faltan else "ninguno")
             .replace("{cab_anios}", " | ".join(str(a) for a in muestra))
             .replace("{sep_anios}", "|".join("---" for _ in muestra))
             .replace("{cobertura}", "\n".join(tabla_cob) or "| | |")
             .replace("{indem_sob}", _fmt_usd(indem_sob) + " USD")
             .replace("{indem_col}", _fmt_usd(indem_col) + " USD")
             .replace("{fuera}", "\n".join(fuera) or "| — | — | ninguna fila descartada en esta corrida | 0 | 0 |")
             .replace("{sin_mes}", str(descartes["filas_sin_mes"]))
             .replace("{anios_sin_anio}", ", ".join(map(str, descartes["anios_sin_anio_perdida"])) or "(ninguno)")
             .replace("{indem_sin_mes}", _fmt_usd(descartes["indem_sin_mes_usd"]))
             .replace("{lejanas}", str(descartes["filas_anio_perdida_lejano"]))
             .replace("{indem_lejanas}", _fmt_usd(descartes["indem_anio_perdida_lejano_usd"])))
    CARD.parent.mkdir(parents=True, exist_ok=True)
    CARD.write_text(texto, encoding="utf-8", newline="\n")
