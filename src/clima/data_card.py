"""Genera docs/datasets/clima.md a partir de los CSV procesados (desde, hasta y % de faltantes reales).

Uso: python src/clima/data_card.py  (después de process.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.clima.celdas import resumen_celdas  # noqa: E402
from src.zona_texto import lista_estados, unir  # noqa: E402
OUT = REPO / "data" / "processed" / "clima"
CARD = REPO / "docs" / "datasets" / "clima.md"

P = "NASA POWER daily (AG)"
D = "Derivada de NASA POWER"
CP = "NASS Crop Progress (Quick Stats, nivel estado)"
DV = "Derivada de NASA POWER y NASS Crop Progress"
IM = "GPM IMERG vía NASA POWER (IMERG_PRECTOT, 0,1°)"

COLS = {
    "clima_diario.csv": [
        ("tmed_c", "Temperatura media diaria a 2 m (T2M)", "°C", P, "C01"),
        ("tmax_c", "Temperatura máxima diaria a 2 m (T2M_MAX)", "°C", P, "C02"),
        ("tmin_c", "Temperatura mínima diaria a 2 m (T2M_MIN)", "°C", P, "C03"),
        ("prec_power_mm", "Precipitación corregida (PRECTOTCORR)", "mm/día", P, "C08"),
        ("prec_imerg_mm", "Precipitación IMERG diaria (día UTC), media de las celdas de 0,1° del condado", "mm/día", IM, "P01"),
        ("hr_pct", "Humedad relativa media a 2 m (RH2M)", "%", P, "C06"),
        ("viento_ms", "Viento medio a 2 m (WS2M)", "m/s", P, "C07"),
        ("rad_mj_m2", "Radiación solar global en superficie (ALLSKY_SFC_SW_DWN)", "MJ/m²/día", P, "C09"),
        ("gwettop", "Humedad relativa del suelo superficial (GWETTOP)", "0-1", P, "C11"),
        ("gwetroot", "Humedad relativa de la zona radicular (GWETROOT)", "0-1", P, "C12"),
        ("gwetprof", "Humedad relativa del perfil (GWETPROF)", "0-1", P, "C13"),
        ("eto_pm_mm", "ETo Penman-Monteith FAO-56 (G=0, ea desde HR media)", "mm/día", D, "D01"),
    ],
    "clima_mensual.csv": [
        ("prec_imerg_mm", "Lluvia total del mes IMERG (suma diaria; vacía si falta algún día)", "mm", IM, "P01"),
        ("prec_power_mm", "Lluvia total del mes (suma de PRECTOTCORR diario)", "mm", P, "C08"),
        ("tmax_c", "Media mensual de la máxima diaria", "°C", P, "C02"),
        ("tmin_c", "Media mensual de la mínima diaria", "°C", P, "C03"),
        ("tmed_c", "Media mensual de T2M", "°C", P, "C01"),
        ("rad_mj_m2", "Radiación total del mes", "MJ/m²", P, "C09"),
        ("eto_pm_mm", "ETo FAO-56 total del mes", "mm", D, "D01"),
        ("deficit_mm", "prec_power_mm − eto_pm_mm", "mm", D, "D04"),
        ("dias_tmax_gt30", "Días con tmax > 30 °C", "días", D, "D09"),
        ("dias_tmax_gt35", "Días con tmax > 35 °C", "días", D, "D10"),
        ("dias_tmin_le0", "Días con tmin <= 0 °C", "días", D, "D11"),
        ("dias_tmin_le_m2", "Días con tmin <= −2 °C", "días", D, "D11"),
        ("gdd_10_30", "Grados-día método maíz (base 10 °C, tope 30 °C; 50/86 °F)", "°C·día", D, "D08"),
        ("gdd_base0", "Grados-día base 0 °C (T2M)", "°C·día", D, "D08"),
        ("dias_lluvia_ge1", "Días con lluvia >= 1 mm", "días", D, "D18"),
        ("prec_max1d_mm", "Lluvia máxima en 1 día (Rx1day)", "mm", D, "D16"),
        ("prec_max5d_mm", "Lluvia máxima en 5 días consecutivos que terminan en el mes (Rx5day)", "mm", D, "D16"),
        ("dias_lluvia_gt50", "Días con lluvia > 50 mm", "días", D, "D15"),
        ("racha_seca_max_dias", "Racha más larga de días con lluvia < 1 mm dentro del mes", "días", D, "D17"),
        ("spi1", "SPI 1 mes (gamma por condado y mes, POWER 1981-2025)", "adim.", D, "D06"),
        ("spi3", "SPI 3 meses", "adim.", D, "D06"),
        ("spi6", "SPI 6 meses", "adim.", D, "D06"),
        ("anom_tmed_c", "tmed_c menos la media del mismo mes 1991-2020", "°C", D, "D23"),
        ("gwettop", "Media mensual de GWETTOP", "0-1", P, "C11"),
        ("gwetroot", "Media mensual de GWETROOT", "0-1", P, "C12"),
        ("gwetprof", "Media mensual de GWETPROF", "0-1", P, "C13"),
    ],
    "clima_anual.csv": [
        ("doy_ultima_helada", "Último día (ene-jul) con tmin <= 0 °C", "día del año", D, "D12"),
        ("doy_primera_helada", "Primer día (ago-dic) con tmin <= 0 °C", "día del año", D, "D13"),
        ("periodo_libre_heladas_dias", "doy_primera_helada − doy_ultima_helada − 1", "días", D, "D14"),
        ("prec_temporada_mm", "Lluvia abril-septiembre", "mm", D, "D19"),
        ("gdd_temporada", "gdd_10_30 acumulado abril-septiembre", "°C·día", D, "D08"),
        ("prec_invierno_previo_mm", "Lluvia noviembre del anio−1 a marzo del anio", "mm", D, "D20"),
        ("prec_jul_mm", "Lluvia de julio", "mm", D, "D19"),
        ("tmax_jul_c", "Media de la tmax diaria de julio", "°C", D, "D10"),
        ("dias_tmax_gt30_jul", "Días de julio con tmax > 30 °C", "días", D, "D10"),
        ("prec_ago_mm", "Lluvia de agosto", "mm", D, "D19"),
        ("deficit_temporada_mm", "Suma abril-septiembre de prec_power_mm − eto_pm_mm", "mm", D, "D04"),
        ("tend_prec_mm_decada", "Pendiente MCO de la lluvia anual en los 30 años que terminan en anio (mín. 20)", "mm/década", D, "D24"),
        ("tend_tmed_c_decada", "Pendiente MCO de la temperatura media anual en los 30 años que terminan en anio (mín. 20)", "°C/década", D, "D24"),
        # T128: ventanas por estado y año (src/clima/ventanas.py)
        ("doy_ini_floracion_maiz", "Día del año del 25 % de silking del maíz en el estado (Crop Progress, interpolado y redondeado)", "día del año", CP, "CT05"),
        ("doy_fin_floracion_maiz", "Día del año del 75 % de silking del maíz en el estado", "día del año", CP, "CT05"),
        ("prec_floracion_maiz_mm", "Lluvia de doy_ini a doy_fin de floración del maíz, ambos inclusive", "mm", DV, "D19"),
        ("tmax_floracion_maiz_c", "Media de la tmax diaria en la floración del maíz", "°C", DV, "D10"),
        ("dias_tmax_gt30_floracion_maiz", "Días con tmax > 30 °C en la floración del maíz", "días", DV, "D10"),
        ("dias_tmax_gt35_floracion_maiz", "Días con tmax > 35 °C en la floración del maíz", "días", DV, "D10"),
        ("doy_ini_llenado_soja", "Día del año del 50 % de setting pods de la soja en el estado", "día del año", CP, "CT05"),
        ("doy_fin_llenado_soja", "Día del año del 25 % de dropping leaves de la soja en el estado", "día del año", CP, "CT05"),
        ("prec_llenado_soja_mm", "Lluvia de doy_ini a doy_fin del llenado de la soja, ambos inclusive", "mm", DV, "D19"),
        ("tmax_llenado_soja_c", "Media de la tmax diaria en el llenado de la soja", "°C", DV, "D10"),
        ("deficit_llenado_soja_mm", "Suma de prec_power_mm − eto_pm_mm en el llenado de la soja", "mm", DV, "D04"),
        ("prec_ago_sep15_mm", "Lluvia del 1 de agosto al 15 de septiembre (sin fenología)", "mm", D, "D19"),
    ],
}
TIEMPO = {"clima_diario.csv": "fecha", "clima_mensual.csv": "mes", "clima_anual.csv": "anio"}

TEXTO = """# Data card — clima

Paquete `clima` (CLAUDE.md §6.1): NASA POWER diario (comunidad AG) en el centroide de cada
condado de {estados} ({n_condados} condados), 1981-2025 en `data/raw/clima/power/` (un CSV por condado,
tal cual lo devuelve la API), y GPM IMERG diario 2000-2025 servido por la misma API de POWER
(`IMERG_PRECTOT`), una consulta por celda de 0,1° en `data/raw/clima/imerg_power/` ({n_celdas} celdas).
Los CSV procesados cubren el período de `config.yaml` (2000-2025);
1981-1999 se usa solo como base de SPI, anomalías y tendencias.

- Bajada: `python src/clima/download.py` (reanudable, registra en `manifest.csv`).
- Proceso: `python src/clima/process.py`.
- Este data card: `python src/clima/data_card.py`.

## Columnas

| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |
|---|---|---|---|---|---|---|---|---|
{tabla}

## Fuentes

- **NASA POWER** (API diaria por punto, comunidad AG; sin DOI). Cita pedida por POWER: "The data was
  obtained from National Aeronautics and Space Administration (NASA) Langley Research Center's
  Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science
  Division." (https://power.larc.nasa.gov/docs/referencing/).
  Versión de la API: `v2.10.3` el 2026-11-15. Cada bajada nueva guarda la que devuelve la API (encabezado HTTP
  `x-app-version`) en la columna `version` de `manifest.csv` (`POWER API v2.10.3`); las filas anteriores a
  T123 dicen `v2 (API)` (meteorología) o `POWER API v2.10.3` (IMERG), escrito fijo en el código. Para saber
  la vigente: pedir cualquier punto con `format=JSON` y leer `header.api.version`
  (ver `docs/research/power_version.md`).
- **GPM IMERG Final V07** (`GPM_3IMERGDF`), hasta el 2025-09-30: https://doi.org/10.5067/GPM/IMERGDF/DAY/07
- **GPM IMERG Late V07** (`GPM_3IMERGDL`), desde el 2025-10-01 (ver Problemas conocidos):
  https://doi.org/10.5067/GPM/IMERGDL/DAY/07
- Citas completas: `docs/research/citas_nasa.md`.

## Supuestos

- **IMERG sin Earthdata:** no hay credencial de Earthdata para `GPM_3IMERGDF` en GES DISC, así
  que `prec_imerg_mm` sale del parámetro `IMERG_PRECTOT` de la API diaria de NASA POWER (sin
  login), que sirve IMERG a su resolución nativa de 0,1°. Según la documentación de POWER
  (https://power.larc.nasa.gov/docs/methodology/, consultada 2026-11-14): "IMERG Precipitation
  0.1° (~10 km), daily UTC June 1, 1998 Near Real Time". Según la página de metodología
  meteorológica de POWER, usa la Final Run y, después de su última fecha, la Late Run
  (GPM_3IMERGDF V07 en CMR llega a 2025-09-30; ver Problemas conocidos). Ruta que cumple el plan: GPM_3IMERGDF por GES DISC
  con Earthdata.
- IMERG solo existe en días UTC (POWER rechaza la hora solar local para esta fuente), mientras
  que el resto de POWER está en días de hora solar local: `prec_imerg_mm` y `prec_power_mm`
  del mismo día cubren ventanas desplazadas unas 6 h.
- Media del condado de IMERG: promedio simple (sin ponderar por área ni por máscara agrícola)
  de las celdas de 0,1° cuyo centro cae dentro del polígono del condado (`src/clima/celdas.py`;
  entre {min_celdas} y {max_celdas} celdas por condado). Si un condado no tiene ningún centro adentro se usa
  la celda de su centroide: {sin_centro}. No se agrega `frac_pixeles_validos` porque la
  columna no está en el esquema de clima.
- Las variables derivadas de lluvia (SPI, días de lluvia, Rx1day, rachas, déficit) siguen
  usando POWER (PRECTOTCORR), que existe desde 1981 y da la base larga que necesita el SPI.

- POWER se consulta en el centroide del condado (`data/reference/condados.csv`), no como media
  areal: la grilla de POWER (MERRA-2 0,5° × 0,625°; CERES 1°) es más gruesa que la mayoría de
  los condados, y varios condados vecinos comparten celda y tienen valores idénticos.
- El valor de relleno de POWER (−999) se convierte a vacío.
- ETo FAO-56 (ec. 6) con G = 0, presión atmosférica desde la elevación MERRA-2 que informa el
  encabezado de POWER, ea desde la HR media (ec. 19), Rso = (0,75 + 2·10⁻⁵ z)·Ra, Rs/Rso ≤ 1.
  Los valores negativos (posibles en invierno) se llevan a 0. Sin radiación (antes de 1984) no hay ETo.
- Los totales mensuales de radiación y ETo quedan vacíos si al mes le falta algún día de radiación.
- `gdd_10_30`: método del maíz, tmax tope 30 °C y tmin piso 10 °C, GDD = (tmax* + tmin*)/2 − 10.
  `gdd_base0` = max(T2M, 0).
- Día de lluvia: >= 1 mm. Racha seca: días consecutivos con < 1 mm, cortada al mes calendario.
- `prec_max5d_mm`: suma móvil de 5 días cuyo último día cae en el mes (puede incluir los
  últimos días del mes anterior).
- SPI: distribución gamma ajustada (máxima verosimilitud, loc = 0) por condado y mes calendario
  con todo el registro POWER 1981-2025, con probabilidad mixta para ceros; recortado a ±5.
  Usa años posteriores al de la fila para ajustar la distribución (convención estándar del SPI).
- `anom_tmed_c`: base 1991-2020 (`config.yaml`, `anomalias_base`).
- Helada: tmin <= 0 °C (32 °F). Última helada de primavera = último día de enero a julio;
  primera de otoño = primer día de agosto a diciembre. Si en el año no hay helada en esa
  ventana, la celda queda vacía.
- Tendencias: pendiente de MCO × 10 sobre los años calendario completos `anio−29..anio`
  (mínimo 20 años), sin usar años posteriores al de la fila.
- Los CSV se escriben con decimales fijos (2 en el diario, 3 en mensual y anual), así un
  valor real como −99 se escribe `-99.000` y no se confunde con un código de relleno.
- Ventanas anuales según `config.yaml`: temporada abril-septiembre, invierno previo
  noviembre del anio−1 a marzo del anio, julio y agosto.
- **Ventanas por estado y año (T128, propuesta de T038; `src/clima/ventanas.py`).** Floración del maíz:
  del 25 % al 75 % de *silking*; llenado de la soja: del 50 % de *setting pods* al 25 % de *dropping
  leaves* (supuesto de `docs/research/ventanas_por_estado.md`: incluye R3-R4 y termina en el comienzo de
  R7). El día de cada cruce se interpola linealmente entre las dos semanas de Crop Progress que lo rodean
  (semana fechada en su domingo de cierre) y se redondea al entero (mitades al par, como `round` de
  pandas); los días de la ventana van de `doy_ini` a `doy_fin`, ambos inclusive. La ventana es la del
  **estado** (Crop Progress no tiene condados) y se aplica a todos sus condados.
- Si el primer reporte del año ya está en el porcentaje buscado o más, o nunca se llega, ese estado-año no
  tiene cruce: las columnas de esa ventana quedan vacías. Nunca se usa la ventana de otro año ni la mediana.
  Si a la ventana le falta algún día de lluvia (o de tmax, o de ETo para el déficit), esa columna queda vacía.
- Fuente de los cruces: la base completa de Quick Stats (`data/raw/cultivos/nass/qs.crops_*.txt.gz`,
  `PCT SILKING`, `PCT SETTING PODS`, `PCT DROPPING LEAVES`) si está bajada; si no, los cruces de
  `docs/research/ventanas_por_estado.csv` (reportes de ESMIS, **solo 2008-2025**: antes de 2008 las columnas
  quedan vacías). La copia usada queda en `data/interim/clima/ventanas_estado.csv`, con la columna `fuente`.
- **Fuga de información:** la ventana del mismo año se conoce recién cuando termina. Para pronosticar
  dentro de la temporada, ML debería usar la mediana de los años anteriores (lo decide ML).
- `prec_ago_sep15_mm` (1 ago - 15 sep) es la versión mínima sin fenología: suma el llenado activo de la
  primera quincena de septiembre que `prec_ago_mm` no cubre. Vacía si falta algún día.

## Problemas conocidos

- **GPM IMERG viene de POWER, no de GES DISC** (sin credencial de Earthdata): la respuesta de la
  API no dice qué corrida de IMERG trae cada fecha (ver Supuestos).
- **Los últimos meses de `prec_imerg_mm` son IMERG Late, no Final.** POWER usa la Final Run hasta
  donde llega y la Late Run desde ahí ("IMERG Late Run | End of IMERG Final Run | Near Real Time",
  https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/, consultada 2026-11-15). En
  CMR, la Final V07 termina el 2025-09-30, así que en esta bajada **del 2025-10-01 al 2025-12-31
  los datos son de la Late Run**: ajuste climatológico con pluviómetros (no el mensual de GPCC) y
  posibles pasadas de microondas faltantes. POWER recomienda cortar los análisis de tendencia 3,5 meses antes del
  presente. Si se vuelve a bajar cuando la Final cubra 2025, esos días cambian. Las filas no
  tienen columna de corrida: cambiarlo tocaría el esquema y lo decide el humano.
- PRISM (opcional, validación) no se bajó.
- La radiación de POWER (CERES) empieza en 1984; el resto de la meteorología en 1981.
- `validar_csv()` (src/common) marca `deficit_mm` de `clima_mensual.csv` porque hay un valor
  real de −99,99 mm (en la primera tanda: fips 18065, 2011-07: lluvia − ETo), que coincide con su lista de códigos de
  relleno. Es un falso positivo: el valor sale del cálculo y no se modifica. Propuesta en
  `loop/notes/decisiones.md`.
- POWER en un punto: condados vecinos dentro de la misma celda MERRA-2 tienen series idénticas.
"""


def fmt(v, temporal):
    return str(v)


def textos(texto: str) -> str:
    """Completa los datos de la zona (estados de config.yaml y celdas de IMERG de condados.gpkg)."""
    cond = pd.read_csv(REPO / "data" / "reference" / "condados.csv", dtype={"fips": str})
    r = resumen_celdas()
    sin = (f"{len(r['sin_centro'])} condado(s) ({unir(r['sin_centro'])})" if r["sin_centro"]
           else "no le pasa a ninguno")
    for k, v in {"estados": lista_estados(), "n_condados": len(cond), "n_celdas": f"{r['n_celdas']:,}".replace(",", "."),
                 "min_celdas": r["min"], "max_celdas": r["max"], "sin_centro": sin}.items():
        texto = texto.replace("{" + k + "}", str(v))
    return texto


def main():
    filas = []
    for archivo, cols in COLS.items():
        df = pd.read_csv(OUT / archivo, dtype={"fips": str})
        t = df[TIEMPO[archivo]].astype(str)
        for nombre, desc, unidad, fuente, cid in cols:
            s = df[nombre]
            falt = 100 * s.isna().mean()
            llenos = t[s.notna()]
            desde = llenos.min() if len(llenos) else ""
            hasta = llenos.max() if len(llenos) else ""
            filas.append(f"| {archivo} | {nombre} | {desc} | {unidad} | {fuente} | {cid} | {desde} | {hasta} | {falt:.1f} |")
    CARD.parent.mkdir(parents=True, exist_ok=True)
    CARD.write_text(textos(TEXTO).replace("{tabla}", "\n".join(filas)), encoding="utf-8", newline="\n")
    print(f"escrito {CARD.relative_to(REPO).as_posix()} ({len(filas)} columnas)")


if __name__ == "__main__":
    main()
