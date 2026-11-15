"""Genera docs/datasets/vegetacion.md a partir de los CSV procesados (desde, hasta y % de faltantes reales).

Uso: python src/vegetacion/data_card.py  (después de process.py)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "data" / "processed" / "vegetacion"
CARD = REPO / "docs" / "datasets" / "vegetacion.md"

V = "MODIS MOD13Q1 v061 (Planetary Computer)"
L = "MODIS MOD11A2 v061 (Planetary Computer)"
E = "NLDAS-2 Noah mensual v2.0 (NASA GES DISC, sustituye a MOD16A2)"
D13 = "Derivada de MOD13Q1"
DL = "Derivada de MOD11A2 + MOD13Q1"

COLS = {
    "vegetacion_16d.csv": [
        ("ndvi", "NDVI medio del condado (compuesto de 16 días; fecha = inicio del compuesto)", "adim.", V, "M01"),
        ("evi", "EVI medio del condado", "adim.", V, "M02"),
        ("ndvi_maiz", "NDVI medio de los píxeles con >= 75 % de maíz (CDL del año)", "adim.", V, "M01"),
        ("ndvi_soja", "NDVI medio de los píxeles con >= 75 % de soja (CDL del año)", "adim.", V, "M01"),
        ("frac_pixeles_validos", "Píxeles que pasan el filtro de calidad sobre los píxeles del condado", "0-1", V, "M03"),
    ],
    "vegetacion_mensual.csv": [
        ("ndvi", "Media de los compuestos de 16 días que empiezan en el mes", "adim.", V, "M01"),
        ("evi", "Media de los compuestos de 16 días que empiezan en el mes", "adim.", V, "M02"),
        ("ndvi_maiz", "Media mensual del NDVI de maíz (CDL >= 75 %)", "adim.", V, "M01"),
        ("ndvi_soja", "Media mensual del NDVI de soja (CDL >= 75 %)", "adim.", V, "M01"),
        ("lst_dia_c", "LST diurna media (compuestos de 8 días que empiezan en el mes)", "°C", L, "M04"),
        ("lst_noche_c", "LST nocturna media", "°C", L, "M05"),
        ("et_mm", "ET real total del mes (Evap de NLDAS-2 Noah, media ponderada del condado)", "mm", E, "M06"),
        ("pet_mm", "ET potencial total del mes (PotEvap de NLDAS-2 Noah, W m-2 × 86400 × días / 2,501e6)", "mm", E, "M07"),
        ("et_pet_ratio", "et_mm / pet_mm", "adim.", E, ""),
        ("ndvi_anom_z", "(ndvi − media del mes calendario) / desvío, por condado, todos los años", "adim.", D13, "F10"),
        ("vci", "VCI = 100 (ndvi − mín) / (máx − mín) del mes calendario, por condado", "0-100", D13, "F11"),
        ("tci", "TCI = 100 (máx − lst_dia_c) / (máx − mín) del mes calendario, por condado", "0-100", DL, "F12"),
        ("vhi", "VHI = 0,5 VCI + 0,5 TCI", "0-100", DL, "F13"),
    ],
    "fenologia_anual.csv": [
        ("doy_inicio", "Día del año en que el NDVI suavizado sube al 50 % de la amplitud del año", "DOY", D13, "F01"),
        ("doy_pico", "Día del año del máximo NDVI suavizado (inicio del compuesto + 8 días)", "DOY", D13, "F02"),
        ("doy_fin", "Día del año en que el NDVI suavizado baja al 50 % de la amplitud", "DOY", D13, "F04"),
        ("ndvi_max", "Máximo del NDVI suavizado del año", "adim.", D13, "F03"),
        ("duracion_dias", "doy_fin − doy_inicio", "días", D13, "F05"),
        ("ndvi_integral", "Integral del NDVI suavizado entre doy_inicio y doy_fin", "NDVI·día", D13, "F06"),
        ("n_ciclos", "Picos del NDVI suavizado con prominencia >= 0,1", "n", D13, "F07"),
        ("ndvi_max_maiz", "Máximo NDVI de maíz del año (compuestos de 16 días)", "adim.", D13, "F03"),
        ("ndvi_max_soja", "Máximo NDVI de soja del año (compuestos de 16 días)", "adim.", D13, "F03"),
        ("dias_ndvi_lt03_invierno", "Días con NDVI diario interpolado < 0,3 entre 1-nov (anio−1) y 31-mar", "días", D13, "F09"),
    ],
}

TEXTO = """
## Fuentes y acceso

- **MOD13Q1 v061** (Terra, índices de vegetación 16 días, 250 m) y **MOD11A2 v061** (Terra, LST 8 días,
  1 km), COGs públicos de Microsoft Planetary Computer (colecciones `modis-13Q1-061` y
  `modis-11A2-061`), firmados con el token SAS anónimo. Teselas h10v04, h10v05, h11v04, h11v05.
- `src/vegetacion/download.py` lee solo la ventana de cada tesela que cubre los condados y la guarda
  tal cual en `data/raw/vegetacion/<producto>/<anio>/<item>.tif` (una fila por archivo en `manifest.csv`).
- `src/vegetacion/process.py` rasteriza los condados en la grilla sinusoidal de cada tesela, filtra
  calidad y promedia por condado (suma de todas las teselas que tocan el condado).
- **NLDAS-2 Noah mensual v2.0** (`NLDAS_NOAH0125_M`, NASA GES DISC, 0,125°, CMR
  `C1887990023-GES_DISC`), variables `Evap` (kg m-2, suma del mes) y `PotEvap` (W m-2, media del mes),
  recortadas al rectángulo de los condados con Harmony (`harmony.earthdata.nasa.gov`, login Earthdata).
  `src/vegetacion/download_nldas.py` guarda un NetCDF por mes en `data/raw/vegetacion/nldas_noah_m/<anio>/`.

## Supuestos

- Sin credencial de Earthdata no se usó AppEEARS: se usaron los mismos productos v061 desde
  Planetary Computer (acceso público sin login).
- **Resolución reducida.** La tesela completa a 250 m baja a ~1 MB/s y el período completo pasaría de
  5 GB, así que MOD13Q1 se lee del overview 1 del COG (factor 4, ~927 m) y MOD11A2 del overview 0
  (factor 2, ~2 km). Los overviews los genera Planetary Computer remuestreando la banda (no es
  vecino más cercano): la media del condado es comparable, pero el filtro de calidad es aproximado.
- **Filtro de calidad MOD13Q1:** NDVI y EVI dentro del rango válido (−2000 a 10000), pixel reliability
  remuestreado igual a 0 (bueno) o 1 (marginal), y el píxel no toca (vecindad 3x3) ningún píxel sin
  dato o fuera de rango (los bordes del remuestreo dejan artefactos). `frac_pixeles_validos` es la
  fracción de píxeles del condado que pasan el filtro.
- **Filtro de calidad MOD11A2:** LST día y noche >= 7500 (valid_range, escala 0,02 K) en el mismo
  píxel, con la misma erosión 3x3. No se bajaron las bandas QC (en el overview no son interpretables).
- `ndvi`/`evi` son la media de todo el condado (no se aplicó `mascara_agricola.tif`).
- **NDVI de maíz y soja** (desde 2008): con `data/reference/mascara_<cultivo>_<anio>.tif` (CDL, 30 m,
  EPSG:5070) se calcula la fracción exacta del cultivo en bloques de 8x8 (240 m) y se reproyecta con
  promedio a la grilla MODIS de cada tesela. Un píxel MODIS cuenta si >= 75 % de su área es del
  cultivo de ese año (umbral pedido para 250 m, aplicado al píxel del overview de ~927 m). Cache en
  `data/interim/vegetacion/frac_cultivos/` (se regenera si falta).
- `ndvi_max_maiz`/`ndvi_max_soja`: máximo de los compuestos del año que pasan el filtro (sin
  suavizar), solo si hay >= 10 compuestos con dato en el año.
- `anio` es el año calendario de la fecha (16d) o del mes (mensual). La fecha del compuesto es su
  primer día. En el mensual, cada compuesto se asigna al mes de su primer día.
- Anomalía z, VCI y TCI usan como referencia todos los años disponibles del mismo condado y mes.
- Fenología: serie de 16 días del año calendario, huecos interpolados linealmente, Savitzky-Golay
  (ventana 5, orden 2); inicio y fin = cruce del 50 % de la amplitud (mín. a máx. del año) antes y
  después del pico; se exige >= 15 compuestos válidos en el año. `n_ciclos` = picos con prominencia
  >= 0,1. `dias_ndvi_lt03_invierno`: NDVI diario interpolado entre compuestos (centro = inicio + 8 d),
  umbral 0,3, solo si la serie cubre todo el invierno previo.
- Umbral para NDVI de maíz/soja (cuando se calcule): un píxel cuenta si >= 75 % de su área es del
  cultivo según la máscara del CDL de ese año.
- **ET y PET de NLDAS-2 Noah en lugar de MOD16A2 (sustitución de fuente).** MOD16A2 (8 días, 500 m)
  no está en Planetary Computer, a 500 m el período completo no entra en el límite de 5 GB del paquete
  (que ya usa ~4,7 GB) y el OPeNDAP de GES DISC está retirado (410). NLDAS-2 es un modelo de superficie
  (Noah) forzado con observaciones, no una estimación satelital: `et_mm` es la ET total simulada y
  `pet_mm` la evaporación potencial de Noah (Penman, típicamente más alta que la PET de MOD16, por eso
  `et_pet_ratio` es más bajo que con MOD16). No mezclar con valores de MOD16A2. Resolución 0,125°
  (~12 km): la media del condado pondera cada celda por su fracción dentro del condado (supermuestreo
  10x de la grilla); se exige que >= 50 % del área del condado tenga dato. Conversión de PET:
  mm/mes = W m-2 × 86400 × días del mes / 2,501e6 J/kg. Media de todo el condado (sin máscara agrícola).
  `anio` = año calendario del mes. Se bajaron 2000–2025 (el contrato pide ET desde 2001).
  Ojo: el paquete `nldas` (si se arma) entrega `et_nldas_mm` del mismo modelo; en la tabla unida las dos
  columnas serían redundantes (no usar ambas como variables independientes en ML).

## Problemas conocidos

- NDVI de maíz/soja vacío en condados sin píxeles de ~927 m con >= 75 % del cultivo (zonas de
  lotes chicos o mezclados).
- Invierno: nieve y nubes dejan meses sin píxeles que pasen el filtro (faltantes en `ndvi`, `lst_*`).
- La regla `lst_noche_c <= lst_dia_c` falla en < 0,1 % de las filas (meses de invierno con pocos
  compuestos válidos); los valores se dejan como vienen.
- `et_mm`, `pet_mm` y `et_pet_ratio` no son MOD16A2 sino NLDAS-2 Noah (ver Supuestos). Para tener
  MOD16A2 hace falta AppEEARS (Earthdata) y liberar espacio: a 500 m no entra en 5 GB. Rutas probadas
  para MOD16A2: Planetary Computer (solo MOD16A3GF anual) y el MODIS Web Service de ORNL DAAC
  (`modis.ornl.gov/rst/api/v1`, ~57 s por pedido de 10 fechas y por punto, errores 502: inviable).
- NLDAS trae valores fuera del rango del contrato en muy pocas filas y se dejan como vienen: ET y PET
  apenas negativas (hasta −0,5 mm) en enero de 2006 en el noroeste de Iowa (condensación/escarcha neta
  en el modelo) y PET > 500 mm en julio de 2012 (sequía) en 5 condados (visto en la primera tanda,
  IA, IL e IN). `et_pet_ratio` queda vacío
  cuando `pet_mm` <= 1 mm.- MCD12Q1 no se bajó (la máscara agrícola del CDL ya existe).
- 2025 incompleto en origen: Planetary Computer no tiene los compuestos de mediados de 2025
  (MOD13Q1 entre A2025193 y A2025305; MOD11A2 entre A2025185 y A2025321; revisado el 2026-11-14).
  Todos los demás compuestos que lista el STAC para la zona están bajados.
"""


def main() -> None:
    lineas = ["# Data card — vegetacion", "",
              "Paquete `vegetacion` de Field Shift (CLAUDE.md §6.3): MODIS por condado del Corn Belt.", "",
              "## Diccionario de columnas", "",
              "| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |",
              "|---|---|---|---|---|---|---|---|---|"]
    for arch, cols in COLS.items():
        df = pd.read_csv(OUT / arch, dtype={"fips": str})
        tcol = "fecha" if "fecha" in df else ("mes" if "mes" in df else "anio")
        for c, desc, u, f, idc in cols:
            s = df[c]
            ok = df.loc[s.notna(), tcol].astype(str)
            desde, hasta = (ok.min(), ok.max()) if len(ok) else ("", "")
            falt = 100 * s.isna().mean()
            lineas.append(f"| {arch} | {c} | {desc} | {u} | {f} | {idc} | {desde} | {hasta} | {falt:.1f} |")
    CARD.parent.mkdir(parents=True, exist_ok=True)
    CARD.write_text("\n".join(lineas) + "\n" + TEXTO, encoding="utf-8")


if __name__ == "__main__":
    main()
