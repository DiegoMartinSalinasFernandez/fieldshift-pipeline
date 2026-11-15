"""Arma docs/datasets/glosario_en.csv: glosario en inglés de las columnas de los data cards.

Lee las tablas `| archivo | columna | descripcion | unidad | fuente | id_catalogo | ...` de cada
`docs/datasets/*.md` y escribe una fila por columna con la descripción traducida.

La traducción va en los diccionarios de abajo, con la descripción en castellano como clave. Si un data
card cambia una descripción y la clave ya no está, la fila sale con `[SIN TRADUCCION]` + el texto original
(y el script avisa por pantalla): hay que agregar la traducción acá y volver a correrlo.
Las descripciones que no se entienden del todo llevan `[UNCLEAR]` al principio.

Correr:  .venv/bin/python -X utf8 docs/datasets/glosario_en.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
SALIDA = DIR / "glosario_en.csv"
COLUMNAS = ["paquete", "archivo", "columna", "descripcion_en", "unidad", "fuente", "id_catalogo"]
SIN_TRADUCCION = "[SIN TRADUCCION]"
UNCLEAR = "[UNCLEAR]"

ENCABEZADO = re.compile(r"^\|\s*archivo\s*\|\s*columna\s*\|\s*descripcion\s*\|")  # solo diccionarios, no otras tablas con archivo|columna
SEPARADOR = re.compile(r"^\|[\s:|-]+\|\s*$")


def leer_data_card(ruta: Path) -> list[dict]:
    """Filas de las tablas de diccionario de columnas de un data card."""
    filas = []
    en_tabla = False
    nombres: list[str] = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if ENCABEZADO.match(linea):
            en_tabla = True
            nombres = [c.strip() for c in linea.strip().strip("|").split("|")]
            continue
        if not en_tabla:
            continue
        if not linea.startswith("|"):
            en_tabla = False
            continue
        if SEPARADOR.match(linea):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) != len(nombres):
            raise ValueError(f"{ruta.name}: fila con {len(celdas)} celdas, se esperaban {len(nombres)}: {linea}")
        fila = dict(zip(nombres, celdas))
        fila["paquete"] = ruta.stem
        filas.append(fila)
    return filas


def leer_todos(directorio: Path = DIR) -> list[dict]:
    filas = []
    for ruta in sorted(directorio.glob("*.md")):
        filas.extend(leer_data_card(ruta))
    return filas


def traducir(texto: str, tabla: dict[str, str]) -> str | None:
    return tabla.get(texto)


def armar(filas: list[dict]) -> tuple[list[dict], list[str]]:
    salida, faltan = [], []
    for f in filas:
        desc = traducir(f["descripcion"], DESCRIPCIONES)
        if desc is None:
            faltan.append(f"{f['paquete']}/{f['archivo']}/{f['columna']}: {f['descripcion']}")
            desc = f"{SIN_TRADUCCION} {f['descripcion']}"
        salida.append({
            "paquete": f["paquete"],
            "archivo": f["archivo"],
            "columna": f["columna"],
            "descripcion_en": desc,
            "unidad": UNIDADES.get(f["unidad"], f["unidad"]),
            "fuente": FUENTES.get(f["fuente"], f["fuente"]),
            "id_catalogo": f.get("id_catalogo", ""),
        })
    return salida, faltan


def main() -> int:
    salida, faltan = armar(leer_todos())
    with open(SALIDA, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS, lineterminator="\n")
        w.writeheader()
        w.writerows(salida)
    print(f"{SALIDA.name}: {len(salida)} filas")
    for x in faltan:
        print(f"  sin traducción: {x}")
    return 0


# ---------------------------------------------------------------------------------------------------
# Unidades (las que no están se copian tal cual)
# ---------------------------------------------------------------------------------------------------
UNIDADES = {
    "adim.": "dimensionless",
    "adimensional": "dimensionless",
    "días": "days",
    "día": "day",
    "percentil 0-100": "percentile 0-100",
    "código": "code",
    "texto": "text",
    "grados": "degrees",
    "año": "year",
    "años": "years",
    "fecha YYYY-MM-DD": "date YYYY-MM-DD",
    "mm/día": "mm/day",
    "MJ/m²/día": "MJ/m²/day",
    "°C·día": "°C·day",
    "día del año": "day of year",
    "mm/década": "mm/decade",
    "°C/década": "°C/decade",
    "fracción": "fraction",
    "cultivos/año": "crops/year",
    "índice": "index",
    "USD/ton corta": "USD/short ton",
    "pasadas": "overpasses",
    "píxeles": "pixels",
    "lotes": "fields",
    "reflectancia": "reflectance",
    "obs": "observations",
    "clase": "class",
    "t·ha·h/(ha·MJ·mm) (adim. NRCS)": "t·ha·h/(ha·MJ·mm) (dimensionless in NRCS)",
    "escenas": "scenes",
    "estaciones": "stations",
    "NDVI·día": "NDVI·day",
}

# ---------------------------------------------------------------------------------------------------
# Fuentes (solo las que tienen palabras en castellano; el resto se copia tal cual)
# ---------------------------------------------------------------------------------------------------
FUENTES = {
    "NASA SMAP L4 SPL4SMGP 9 km, capas diarias de Crop-CASMA (USDA NASS / GMU)":
        "NASA SMAP L4 SPL4SMGP 9 km, Crop-CASMA daily layers (USDA NASS / GMU)",
    "Derivada de SMAP L4 (Crop-CASMA)": "Derived from SMAP L4 (Crop-CASMA)",
    "config/config.yaml + STATEFP del Census": "config/config.yaml + Census STATEFP",
    "US Census CB 2024 1:500k (cálculo propio)": "US Census CB 2024 1:500k (own calculation)",
    "config/config.yaml (periodo)": "config/config.yaml (period)",
    "config/config.yaml (ventanas)": "config/config.yaml (windows)",
    "GPM IMERG vía NASA POWER (IMERG_PRECTOT, 0,1°)": "GPM IMERG via NASA POWER (IMERG_PRECTOT, 0.1°)",
    "Derivada de NASA POWER": "Derived from NASA POWER",
    "USDA NASS Quick Stats (SURVEY, condado)": "USDA NASS Quick Stats (SURVEY, county)",
    "Derivada de NASS Quick Stats": "Derived from NASS Quick Stats",
    "USDA NASS Quick Stats Crop Progress (SURVEY, estado)": "USDA NASS Quick Stats Crop Progress (SURVEY, state)",
    "USDA NASS Censo Agropecuario (Quick Stats CENSUS)": "USDA NASS Census of Agriculture (Quick Stats CENSUS)",
    "USDA NASS Quick Stats (volcado qs.crops)": "USDA NASS Quick Stats (qs.crops bulk file)",
    "NASA JPL ECOSTRESS colección 2 (LP DAAC), 70 m, ECO_L2T_LSTE.002":
        "NASA JPL ECOSTRESS Collection 2 (LP DAAC), 70 m, ECO_L2T_LSTE.002",
    "NASA JPL ECOSTRESS colección 2 (LP DAAC), 70 m, ECO_L3T_JET.002":
        "NASA JPL ECOSTRESS Collection 2 (LP DAAC), 70 m, ECO_L3T_JET.002",
    "NASA JPL ECOSTRESS colección 2 (LP DAAC), 70 m, ECO_L4T_ESI.002":
        "NASA JPL ECOSTRESS Collection 2 (LP DAAC), 70 m, ECO_L4T_ESI.002",
    "NASA JPL ECOSTRESS colección 2 (LP DAAC), 70 m": "NASA JPL ECOSTRESS Collection 2 (LP DAAC), 70 m",
    "grilla mascara_agricola.tif": "mascara_agricola.tif grid",
    "USDA NASS Censo (practicas_censo.csv)": "USDA NASS Census of Agriculture (practicas_censo.csv)",
    "este paquete": "this package",
    "USDA NASS CDL y CSB": "USDA NASS CDL and CSB",
    "USGS/NASA Landsat C2 L2 y NASA HLS v2 S30 (Planetary Computer)":
        "USGS/NASA Landsat C2 L2 and NASA HLS v2 S30 (Planetary Computer)",
    "NASA POWER (AG), en el centroide del lote": "NASA POWER (AG), at the field centroid",
    "GPM IMERG Final vía POWER (IMERG_PRECTOT)": "GPM IMERG Final via POWER (IMERG_PRECTOT)",
    "NASA SMAP L4 vía USDA Crop-CASMA (paquete agua)": "NASA SMAP L4 via USDA Crop-CASMA (agua package)",
    "NLDAS-2 Noah mensual v2.0 (NLDAS_NOAH0125_M, NASA GES DISC por Harmony)":
        "NLDAS-2 Noah monthly v2.0 (NLDAS_NOAH0125_M, NASA GES DISC via Harmony)",
    "SSURGO muaggatt vía Soil Data Access": "SSURGO muaggatt via Soil Data Access",
    "SSURGO chorizon vía Soil Data Access": "SSURGO chorizon via Soil Data Access",
    "SSURGO cointerp (NCCPI 3.0) vía Soil Data Access": "SSURGO cointerp (NCCPI 3.0) via Soil Data Access",
    "SSURGO vía Soil Data Access (USDA NRCS)": "SSURGO via Soil Data Access (USDA NRCS)",
    "Landsat C2 L2 (USGS/NASA) vía Planetary Computer": "Landsat C2 L2 (USGS/NASA) via Planetary Computer",
    "CoCoRaHS daily reports (export público)": "CoCoRaHS daily reports (public export)",
    "NLDAS-2 Noah mensual v2.0 (NASA GES DISC, sustituye a MOD16A2)":
        "NLDAS-2 Noah monthly v2.0 (NASA GES DISC, replaces MOD16A2)",
    "Derivada de MOD13Q1": "Derived from MOD13Q1",
    "Derivada de MOD11A2 + MOD13Q1": "Derived from MOD11A2 + MOD13Q1",
}

# ---------------------------------------------------------------------------------------------------
# Descripciones: castellano del data card -> inglés
# ---------------------------------------------------------------------------------------------------
DESCRIPCIONES = {
    # agua
    "Humedad volumétrica del suelo superficial (0-5 cm), media del condado ponderada por área":
        "Surface volumetric soil moisture (0-5 cm), area-weighted county mean",
    "Humedad volumétrica de la zona radicular (0-100 cm), media del condado ponderada por área":
        "Root-zone volumetric soil moisture (0-100 cm), area-weighted county mean",
    "Media mensual de sm_surface diaria (solo meses completos)":
        "Monthly mean of daily sm_surface (complete months only)",
    "Media mensual de sm_rootzone diaria (solo meses completos)":
        "Monthly mean of daily sm_rootzone (complete months only)",
    "Mínimo mensual de sm_surface diaria": "Monthly minimum of daily sm_surface",
    "Mínimo mensual de sm_rootzone diaria": "Monthly minimum of daily sm_rootzone",
    "(sm_rootzone del mes − media del mes calendario) / desvío, por condado, 2015-2025":
        "(month's sm_rootzone − calendar-month mean) / standard deviation, per county, 2015-2025",
    "Días del mes con sm_rootzone diaria del condado >= 0,40 m3/m3":
        "Days in the month with daily county sm_rootzone >= 0.40 m3/m3",
    "Percentil de almacenamiento de agua subterránea (media ponderada por área del condado)":
        "Groundwater storage percentile (area-weighted county mean)",
    "Percentil de humedad del suelo en la zona radicular (media ponderada por área)":
        "Root-zone soil moisture percentile (area-weighted mean)",
    "Percentil de humedad del suelo superficial (media ponderada por área)":
        "Surface soil moisture percentile (area-weighted mean)",
    # base
    "Código FIPS del condado: 2 dígitos del estado + 3 del condado, texto con ceros a la izquierda":
        "County FIPS code: 2 state digits + 3 county digits, text with leading zeros",
    "Código postal de dos letras del estado, según config.yaml":
        "Two-letter state postal code, as in config.yaml",
    "Nombre del condado (campo NAME del Census)": "County name (Census NAME field)",
    "Latitud del centroide del polígono, calculado en EPSG:5070 y llevado a EPSG:4326":
        "Latitude of the polygon centroid, computed in EPSG:5070 and converted to EPSG:4326",
    "Longitud del centroide del polígono, calculado en EPSG:5070 y llevado a EPSG:4326":
        "Longitude of the polygon centroid, computed in EPSG:5070 and converted to EPSG:4326",
    "Área total del polígono (tierra + agua interior) en Albers CONUS (EPSG:5070)":
        "Total polygon area (land + inland water) in Albers CONUS (EPSG:5070)",
    "Año de la cosecha": "Harvest year",
    "Inicio de la temporada de crecimiento (1 de abril del anio)":
        "Start of the growing season (April 1 of anio)",
    "Fin de la temporada de crecimiento (30 de septiembre del anio)":
        "End of the growing season (September 30 of anio)",
    "Inicio del invierno previo (1 de noviembre del anio − 1)":
        "Start of the preceding winter (November 1 of anio − 1)",
    "Fin del invierno previo (31 de marzo del anio)": "End of the preceding winter (March 31 of anio)",
    # clima
    "Temperatura media diaria a 2 m (T2M)": "Daily mean air temperature at 2 m (T2M)",
    "Temperatura máxima diaria a 2 m (T2M_MAX)": "Daily maximum air temperature at 2 m (T2M_MAX)",
    "Temperatura mínima diaria a 2 m (T2M_MIN)": "Daily minimum air temperature at 2 m (T2M_MIN)",
    "Precipitación corregida (PRECTOTCORR)": "Bias-corrected precipitation (PRECTOTCORR)",
    "Precipitación IMERG diaria (día UTC), media de las celdas de 0,1° del condado":
        "Daily IMERG precipitation (UTC day), mean of the county's 0.1° cells",
    "Humedad relativa media a 2 m (RH2M)": "Mean relative humidity at 2 m (RH2M)",
    "Viento medio a 2 m (WS2M)": "Mean wind speed at 2 m (WS2M)",
    "Radiación solar global en superficie (ALLSKY_SFC_SW_DWN)":
        "All-sky surface shortwave downward solar radiation (ALLSKY_SFC_SW_DWN)",
    "Humedad relativa del suelo superficial (GWETTOP)": "Surface soil wetness (GWETTOP)",
    "Humedad relativa de la zona radicular (GWETROOT)": "Root-zone soil wetness (GWETROOT)",
    "Humedad relativa del perfil (GWETPROF)": "Profile soil wetness (GWETPROF)",
    "ETo Penman-Monteith FAO-56 (G=0, ea desde HR media)":
        "FAO-56 Penman-Monteith reference ET (G=0, ea from mean RH)",
    "Lluvia total del mes IMERG (suma diaria; vacía si falta algún día)":
        "IMERG monthly total precipitation (sum of daily values; empty if any day is missing)",
    "Lluvia total del mes (suma de PRECTOTCORR diario)": "Monthly total precipitation (sum of daily PRECTOTCORR)",
    "Media mensual de la máxima diaria": "Monthly mean of daily maximum temperature",
    "Media mensual de la mínima diaria": "Monthly mean of daily minimum temperature",
    "Media mensual de T2M": "Monthly mean of T2M",
    "Radiación total del mes": "Monthly total solar radiation",
    "ETo FAO-56 total del mes": "Monthly total FAO-56 reference ET",
    "prec_power_mm − eto_pm_mm": "prec_power_mm − eto_pm_mm (water balance)",
    "Días con tmax > 30 °C": "Days with tmax > 30 °C",
    "Días con tmax > 35 °C": "Days with tmax > 35 °C",
    "Días con tmin <= 0 °C": "Days with tmin <= 0 °C",
    "Días con tmin <= −2 °C": "Days with tmin <= −2 °C",
    "Grados-día método maíz (base 10 °C, tope 30 °C; 50/86 °F)":
        "Growing degree days, corn method (base 10 °C, cap 30 °C; 50/86 °F)",
    "Grados-día base 0 °C (T2M)": "Growing degree days base 0 °C (T2M)",
    "Días con lluvia >= 1 mm": "Days with precipitation >= 1 mm",
    "Lluvia máxima en 1 día (Rx1day)": "Maximum 1-day precipitation (Rx1day)",
    "Lluvia máxima en 5 días consecutivos que terminan en el mes (Rx5day)":
        "Maximum 5-consecutive-day precipitation ending in the month (Rx5day)",
    "Días con lluvia > 50 mm": "Days with precipitation > 50 mm",
    "Racha más larga de días con lluvia < 1 mm dentro del mes":
        "Longest run of days with precipitation < 1 mm within the month",
    "SPI 1 mes (gamma por condado y mes, POWER 1981-2025)":
        "1-month Standardized Precipitation Index (gamma fit per county and month, POWER 1981-2025)",
    "SPI 3 meses": "3-month Standardized Precipitation Index",
    "SPI 6 meses": "6-month Standardized Precipitation Index",
    "tmed_c menos la media del mismo mes 1991-2020": "tmed_c minus the 1991-2020 mean of the same month",
    "Media mensual de GWETTOP": "Monthly mean of GWETTOP",
    "Media mensual de GWETROOT": "Monthly mean of GWETROOT",
    "Media mensual de GWETPROF": "Monthly mean of GWETPROF",
    "Último día (ene-jul) con tmin <= 0 °C": "Last day (Jan-Jul) with tmin <= 0 °C (last spring frost)",
    "Primer día (ago-dic) con tmin <= 0 °C": "First day (Aug-Dec) with tmin <= 0 °C (first fall frost)",
    "doy_primera_helada − doy_ultima_helada − 1": "doy_primera_helada − doy_ultima_helada − 1 (frost-free period)",
    "Lluvia abril-septiembre": "April-September precipitation",
    "gdd_10_30 acumulado abril-septiembre": "gdd_10_30 accumulated April-September",
    "Lluvia noviembre del anio−1 a marzo del anio": "Precipitation from November of anio−1 to March of anio",
    "Lluvia de julio": "July precipitation",
    "Media de la tmax diaria de julio": "Mean daily tmax in July",
    "Días de julio con tmax > 30 °C": "July days with tmax > 30 °C",
    "Lluvia de agosto": "August precipitation",
    "Suma abril-septiembre de prec_power_mm − eto_pm_mm": "April-September sum of prec_power_mm − eto_pm_mm",
    "Pendiente MCO de la lluvia anual en los 30 años que terminan en anio (mín. 20)":
        "OLS slope of annual precipitation over the 30 years ending in anio (min. 20 years)",
    "Pendiente MCO de la temperatura media anual en los 30 años que terminan en anio (mín. 20)":
        "OLS slope of annual mean temperature over the 30 years ending in anio (min. 20 years)",
    # cultivos
    "Superficie sembrada (AREA PLANTED, todos los usos)": "Planted area (AREA PLANTED, all utilizations)",
    "Superficie cosechada (AREA HARVESTED; maíz: grano)": "Harvested area (AREA HARVESTED; corn: grain)",
    "Producción (PRODUCTION en BU; maíz: grano). Alfalfa y heno se miden en toneladas: vacía":
        "Production (PRODUCTION in BU; corn: grain). Empty for alfalfa and hay, which are measured in tons",
    "Rendimiento (YIELD en BU / ACRE; maíz: grano). Alfalfa y heno: vacía":
        "Yield (YIELD in BU / ACRE; corn: grain). Empty for alfalfa and hay",
    "rend_bu_ac × factor de config.yaml (bu_ac_a_kgha)": "rend_bu_ac × conversion factor from config.yaml (bu_ac_a_kgha)",
    "sup_sembrada_ac × 0,4047 (acres_a_ha)": "sup_sembrada_ac × 0.4047 (acres_a_ha)",
    "sup_cosechada_ac / sup_sembrada_ac": "sup_cosechada_ac / sup_sembrada_ac (harvested/planted ratio)",
    "Código original de NASS cuando el valor está oculto: (D), (Z), (NA)… (separados por ;)":
        "Original NASS code when the value is withheld: (D), (Z), (NA)… (separated by ;)",
    "Día del año en que se cruza el 50 % sembrado (PCT PLANTED, interpolado)":
        "Day of year when 50 % planted is reached (PCT PLANTED, interpolated)",
    "Día del año en que se cruza el 50 % emergido (PCT EMERGED)":
        "Day of year when 50 % emerged is reached (PCT EMERGED)",
    "Día del año del 50 % en floración (maíz PCT SILKING, soja PCT BLOOMING)":
        "Day of year of 50 % flowering (corn PCT SILKING, soybeans PCT BLOOMING)",
    "Día del año del 50 % cosechado (maíz: grano)": "Day of year of 50 % harvested (corn: grain)",
    "% del área agrícola del condado con maíz (CDL 1)": "% of the county's cropland in corn (CDL 1)",
    "% del área agrícola con soja (CDL 5)": "% of cropland in soybeans (CDL 5)",
    "% del área agrícola con trigo de invierno, solo o en doble cultivo con soja (CDL 24 y 26)":
        "% of cropland in winter wheat, alone or double-cropped with soybeans (CDL 24 and 26)",
    "% del área agrícola con alfalfa (CDL 36)": "% of cropland in alfalfa (CDL 36)",
    "% del área agrícola con otro heno (CDL 37)": "% of cropland in other hay (CDL 37)",
    "% del área agrícola con doble cultivo trigo/soja (CDL 26)": "% of cropland in double-crop wheat/soybeans (CDL 26)",
    "% del área agrícola en barbecho (CDL 61)": "% of cropland in fallow (CDL 61)",
    "% de los píxeles de maíz del anio que tenían soja en anio−1 (sobre los que en anio−1 tenían clase agrícola)":
        "% of anio corn pixels that were soybeans in anio−1 (out of those with a crop class in anio−1)",
    "% de los píxeles de maíz del anio que tenían maíz en anio−1 (sobre los que en anio−1 tenían clase agrícola)":
        "% of anio corn pixels that were corn in anio−1 (out of those with a crop class in anio−1)",
    "% de los píxeles de soja del anio que tenían maíz en anio−1 (sobre los que en anio−1 tenían clase agrícola)":
        "% of anio soybean pixels that were corn in anio−1 (out of those with a crop class in anio−1)",
    "% de los píxeles de soja del anio que tenían soja en anio−1 (sobre los que en anio−1 tenían clase agrícola)":
        "% of anio soybean pixels that were soybeans in anio−1 (out of those with a crop class in anio−1)",
    "% de los píxeles agrícolas los 8 años con maíz y soja alternados todos los años":
        "% of pixels cropped all 8 years with corn and soybeans alternating every year",
    "% de los píxeles agrícolas los 8 años con maíz 3 o más años seguidos":
        "% of pixels cropped all 8 years with corn 3 or more years in a row",
    "% de los píxeles agrícolas los 8 años con soja 3 o más años seguidos":
        "% of pixels cropped all 8 years with soybeans 3 or more years in a row",
    "% de los píxeles agrícolas los 8 años con trigo (solo o en doble cultivo) al menos un año":
        "% of pixels cropped all 8 years with wheat (alone or double-cropped) in at least one year",
    "% de los píxeles agrícolas los 8 años con alfalfa (CDL 36) al menos un año":
        "% of pixels cropped all 8 years with alfalfa (CDL 36) in at least one year",
    "N° de cultivos de la secuencia / 8 años (doble cultivo = 2, barbecho = 0), media de los píxeles":
        "Number of crops in the sequence / 8 years (double crop = 2, fallow = 0), pixel mean",
    "Índice de Shannon (ln) sobre las clases del CDL de la secuencia de 8 años, media de los píxeles":
        "Shannon index (ln) over the CDL classes of the 8-year sequence, pixel mean",
    "COVER CROP PLANTED, (EXCL CRP) / AG LAND, CROPLAND × 100":
        "Cover crop planted area (excl. CRP) / cropland × 100 (Census short_desc COVER CROP PLANTED, (EXCL CRP) / AG LAND, CROPLAND)",
    "CONSERVATION TILLAGE, NO-TILL / AG LAND, CROPLAND × 100":
        "No-till area / cropland × 100 (Census short_desc CONSERVATION TILLAGE, NO-TILL / AG LAND, CROPLAND)",
    "DRAINED BY TILE / AG LAND, CROPLAND × 100":
        "Tile-drained area / cropland × 100 (Census short_desc DRAINED BY TILE / AG LAND, CROPLAND)",
    "AG LAND, IRRIGATED / AG LAND, CROPLAND × 100":
        "Irrigated land / cropland × 100 (Census short_desc AG LAND, IRRIGATED / AG LAND, CROPLAND)",
    # economia
    "Precio recibido por el productor, promedio del año comercial (NASS PRICE RECEIVED, MARKETING YEAR, estado)":
        "Price received by farmers, marketing-year average (NASS PRICE RECEIVED, MARKETING YEAR, state level)",
    "Valor bruto de la producción por acre sembrado (ERS 'Total, gross value of production', regiones ponderadas por área sembrada)":
        "Gross value of production per planted acre (ERS 'Total, gross value of production', regions weighted by planted area)",
    "Costos operativos por acre sembrado (ERS 'Total, operating costs', regiones ponderadas por área sembrada)":
        "Operating costs per planted acre (ERS 'Total, operating costs', regions weighted by planted area)",
    "Costos totales listados por acre sembrado (ERS 'Total, costs listed', regiones ponderadas por área sembrada)":
        "Total listed costs per planted acre (ERS 'Total, costs listed', regions weighted by planted area)",
    "Valor de la producción menos costos operativos (ERS 'Value of production less operating costs', regiones ponderadas por área sembrada)":
        "Value of production less operating costs (ERS 'Value of production less operating costs', regions weighted by planted area)",
    "Código original de NASS cuando el precio no se publica ((D), (S), (NA)); vacío si hay valor":
        "Original NASS code when the price is not published ((D), (S), (NA)); empty when there is a value",
    # ecostress
    "Temperatura de superficie (ECO_L2T_LSTE.002 capa LST) media del mes: promedio de las pasadas con datos, cada una la media de los píxeles agrícolas de buena calidad y sin nube de la ventana de 2,24 km del condado":
        "Monthly mean land surface temperature (ECO_L2T_LSTE.002, LST layer): average over overpasses with data, each the mean of good-quality, cloud-free cropland pixels in the county's 2.24 km window",
    "Evapotranspiración diaria (ECO_L3T_JET.002 capa ETdaily) media del mes, mismas pasadas y píxeles que la LST":
        "Monthly mean daily evapotranspiration (ECO_L3T_JET.002, ETdaily layer), same overpasses and pixels as the LST",
    "Índice de estrés evaporativo (ECO_L4T_ESI.002 capa ESI, ET/PET) medio del mes, mismas pasadas y píxeles que la LST":
        "Monthly mean Evaporative Stress Index (ECO_L4T_ESI.002, ESI layer, ET/PET), same overpasses and pixels as the LST",
    "Pasadas diurnas del mes con al menos 10 píxeles agrícolas válidos de LST en la ventana del condado (0 si todas nubladas, sin dato o sin pasada sobre la ventana)":
        "Daytime overpasses in the month with at least 10 valid cropland LST pixels in the county window (0 if all cloudy, no data or no overpass over the window)",
    # lotes
    "paisaje del plan (depresiones, lomas_loess, llanura_control, indiana)":
        "Landscape stratum from the sampling plan (depresiones = depressions, lomas_loess = loess hills, llanura_control = control plain, indiana)",
    "ventana de 8 años del CSB de donde sale el polígono": "8-year CSB window the polygon comes from",
    "superficie del polígono (EPSG:5070)": "Polygon area (EPSG:5070)",
    "superficie del polígono": "Polygon area",
    "latitud del centroide": "Centroid latitude",
    "longitud del centroide": "Centroid longitude",
    "Polsby-Popper 4πA/P²": "Polsby-Popper compactness 4πA/P²",
    "píxeles de 30 m con centro dentro del lote": "30 m pixels whose center falls inside the field",
    "píxeles con centro dentro del lote achicado 30 m": "Pixels whose center falls inside the field shrunk inward by 30 m",
    "años de la ventana CSB con maíz o soja (CDL<año> del CSB)":
        "Years of the CSB window with corn or soybeans (CSB CDL<year> fields)",
    "% de tierras de cultivo con riego, censo más reciente": "% of cropland irrigated, most recent Census",
    "máxima menos mínima de elevacion_3dep_m en los píxeles del lote":
        "Maximum minus minimum elevacion_3dep_m over the field's pixels",
    "máxima menos mínima de NASADEM (bilineal en la grilla de 30 m) dentro del lote":
        "Maximum minus minimum NASADEM elevation (bilinear on the 30 m grid) within the field",
    "regla de selección y puesto": f"{UNCLEAR} Selection rule and rank of the field (why it was chosen)",
    "polígonos que cumplían todos los criterios en ese paisaje":
        "Polygons that met all selection criteria in that landscape",
    "x del centro del píxel (EPSG:5070)": "x of the pixel center (EPSG:5070)",
    "y del centro del píxel (EPSG:5070)": "y of the pixel center (EPSG:5070)",
    "longitud del centro": "Longitude of the pixel center",
    "latitud del centro": "Latitude of the pixel center",
    "distancia del centro al borde del polígono": "Distance from the pixel center to the polygon edge",
    "1 si el centro cae en el lote achicado 30 m": "1 if the pixel center falls inside the field shrunk inward by 30 m",
    "fracción del píxel de 30 m dentro del polígono": "Fraction of the 30 m pixel inside the polygon",
    "elevación NASADEM (sin suavizar), bilineal a 30 m": "NASADEM elevation (unsmoothed), bilinear to 30 m",
    "pendiente sobre el DEM suavizado (gauss sigma 1 celda)": "Slope on the smoothed DEM (Gaussian, sigma 1 cell)",
    "dirección de máxima bajada desde el norte, horario; vacío con pendiente 0":
        "Direction of steepest descent, clockwise from north; empty where slope is 0",
    "curvatura en planta (Zevenbergen y Thorne)": "Plan curvature (Zevenbergen and Thorne)",
    "curvatura de perfil (Zevenbergen y Thorne)": "Profile curvature (Zevenbergen and Thorne)",
    "elevación menos la media en un radio de 90 m": "Elevation minus mean elevation within a 90 m radius (TPI)",
    "elevación menos la media en un radio de 300 m": "Elevation minus mean elevation within a 300 m radius (TPI)",
    "ln(área específica aportante / tan pendiente), D8 en ventana lote + 2,5 km":
        "Topographic wetness index ln(specific catchment area / tan slope), D8 over the field window + 2.5 km",
    "elevación USGS 3DEP (10 m, media de 3 × 3 celdas en el píxel de 30 m)":
        "USGS 3DEP elevation (10 m, mean of 3 × 3 cells within the 30 m pixel)",
    "pendiente 3DEP a 10 m (gauss sigma 10 m), media en el píxel de 30 m":
        "3DEP slope at 10 m (Gaussian, sigma 10 m), mean within the 30 m pixel",
    "elevación menos la media a <= 90 m, 3DEP 10 m, media en el píxel":
        "Elevation minus mean elevation within <= 90 m (TPI), 3DEP 10 m, mean within the pixel",
    "TWI D8 sobre 3DEP 10 m en ventana lote + 2,52 km, media en el píxel":
        "D8 topographic wetness index on 3DEP 10 m over the field window + 2.52 km, mean within the pixel",
    "relleno priority-flood menos DEM, 3DEP 10 m, media en el píxel":
        "Priority-flood filled DEM minus DEM (depression depth), 3DEP 10 m, mean within the pixel",
    "DEM con depresiones rellenas (priority-flood) menos DEM":
        "Depression-filled DEM (priority-flood) minus DEM (depression depth)",
    "grupo de cultivo más frecuente en los píxeles interiores": "Most frequent crop group among interior pixels",
    "clase CDL más frecuente dentro del grupo principal": "Most frequent CDL class within the main crop group",
    "% de píxeles interiores con el grupo principal": "% of interior pixels in the main crop group",
    "1 si pct_px_cultivo_principal < 90": "1 if pct_px_cultivo_principal < 90 (split field)",
    "grupo del cultivo que el CSB asigna al lote ese año (solo 2018-2025)":
        "Crop group the CSB assigns to the field that year (2018-2025 only)",
    "% de píxeles interiores cuya clase CDL es la del CSB": "% of interior pixels whose CDL class matches the CSB class",
    "clase CDL del píxel (teselas de 30 m de data/raw/cultivos)": "CDL class of the pixel (30 m tiles from data/raw/cultivos)",
    "grupo de la clase según data/reference/clases_cdl.csv": "Crop group of the class according to data/reference/clases_cdl.csv",
    "fracción del píxel con la clase mayoritaria (CDL de 10 m, 2024-2025)":
        "Fraction of the pixel covered by the majority class (10 m CDL, 2024-2025)",
    "fracción de las 9 subceldas de 10 m del píxel con ese mukey (polígonos SSURGO rasterizados)":
        "Fraction of the pixel's 9 sub-cells of 10 m with that mukey (rasterized SSURGO polygons)",
    "nombre de la unidad cartográfica": "Map unit name",
    "agua disponible 0-100 cm (aws0100wta × 10)": "Available water storage 0-100 cm (aws0100wta × 10)",
    "agua disponible 0-150 cm (aws0150wta × 10)": "Available water storage 0-150 cm (aws0150wta × 10)",
    "carbono orgánico 0-30 cm: Σ espesor · MO · 0,58 · densidad · (1 − fragmentos), media por comppct_r":
        "Soil organic carbon 0-30 cm: Σ thickness · OM · 0.58 · bulk density · (1 − rock fragments), weighted by comppct_r",
    "NCCPI v3 general, media por comppct_r": "NCCPI v3 overall, weighted by comppct_r",
    "NCCPI submodelo maíz, media por comppct_r": "NCCPI corn submodel, weighted by comppct_r",
    "NCCPI submodelo soja, media por comppct_r": "NCCPI soybean submodel, weighted by comppct_r",
    "clase de drenaje del componente dominante (drclassdcd)": "Drainage class of the dominant component (drclassdcd)",
    "clase de drenaje más húmeda (drclasswettest)": "Wettest drainage class (drclasswettest)",
    "grupo hidrológico dominante (hydgrpdcd)": "Dominant hydrologic soil group (hydgrpdcd)",
    "% de componentes hídricos (hydclprs)": "% of hydric components (hydclprs)",
    "% de componentes con encharcamiento (pondfreqprs)": "% of components with ponding (pondfreqprs)",
    "frecuencia de inundación dominante (flodfreqdcd traducida)": "Dominant flooding frequency (flodfreqdcd, translated)",
    "profundidad mínima anual de la napa (wtdepannmin)": "Annual minimum water table depth (wtdepannmin)",
    "pendiente del componente dominante (slopegraddcp)": "Slope of the dominant component (slopegraddcp)",
    "pendiente media ponderada de los componentes (slopegradwta)": "Component-weighted mean slope (slopegradwta)",
    "clase de erosión (erocl) del componente dominante": "Erosion class (erocl) of the dominant component",
    "comppct_r del componente dominante": "comppct_r of the dominant component (its % of the map unit)",
    "materia orgánica 0-30 cm (por espesor y comppct_r)": "Organic matter 0-30 cm (weighted by thickness and comppct_r)",
    "arcilla 0-30 cm": "Clay 0-30 cm",
    "arena 0-30 cm": "Sand 0-30 cm",
    "limo 0-30 cm": "Silt 0-30 cm",
    "pH 1:1 en agua 0-30 cm": "pH 1:1 in water 0-30 cm",
    "factor K (kwfact) del horizonte superficial": "K factor (kwfact) of the surface horizon",
    "landsat_c2_l2 o hls_s30": "landsat_c2_l2 or hls_s30",
    "L5, L7, L8, L9, S2A, S2B o S2C": "L5, L7, L8, L9, S2A, S2B or S2C",
    "reflectancia azul": "Blue surface reflectance",
    "reflectancia verde": "Green surface reflectance",
    "reflectancia roja": "Red surface reflectance",
    "reflectancia NIR (Landsat nir08, HLS B8A)": "NIR surface reflectance (Landsat nir08, HLS B8A)",
    "reflectancia SWIR 1,6 µm": "SWIR 1.6 µm surface reflectance",
    "reflectancia SWIR 2,2 µm": "SWIR 2.2 µm surface reflectance",
    "(nir − red) / (nir + red)": "NDVI = (nir − red) / (nir + red)",
    "2,5 (nir − red) / (nir + 2,4 red + 1)": "EVI2 = 2.5 (nir − red) / (nir + 2.4 red + 1)",
    "nir / green − 1": "GCVI = nir / green − 1",
    "(nir − swir1) / (nir + swir1)": "NDMI = (nir − swir1) / (nir + swir1)",
    "1 si Landsat 7 desde 2003-05-31": "1 if Landsat 7 from 2003-05-31 on (SLC-off)",
    "valor crudo de QA_PIXEL (Landsat) o Fmask (HLS)": "Raw QA_PIXEL (Landsat) or Fmask (HLS) value",
    "NDVI máximo del año (Landsat, mar-nov)": "Annual maximum NDVI (Landsat, Mar-Nov)",
    "día del año del NDVI máximo": "Day of year of maximum NDVI",
    "EVI2 máximo del año (Landsat)": "Annual maximum EVI2 (Landsat)",
    "día del año del EVI2 máximo": "Day of year of maximum EVI2",
    "NDVI medio de las observaciones de julio-agosto (Landsat)": "Mean NDVI of July-August observations (Landsat)",
    "observaciones despejadas Landsat de marzo a noviembre": "Clear Landsat observations from March to November",
    "observaciones despejadas Landsat de mayo-junio": "Clear Landsat observations in May-June",
    "observaciones despejadas Landsat de julio-agosto": "Clear Landsat observations in July-August",
    "NDVI máximo del año con HLS S30": "Annual maximum NDVI from HLS S30",
    "observaciones despejadas HLS S30 de julio-agosto": "Clear HLS S30 observations in July-August",
    "mediana de refl_blue con NDVI < 0,25, 15 mar-15 may (Landsat)":
        "Median refl_blue of observations with NDVI < 0.25, Mar 15-May 15 (Landsat; bare soil)",
    "mediana de refl_red con NDVI < 0,25, 15 mar-15 may (Landsat)":
        "Median refl_red of observations with NDVI < 0.25, Mar 15-May 15 (Landsat; bare soil)",
    "mediana de refl_nir con NDVI < 0,25, 15 mar-15 may (Landsat)":
        "Median refl_nir of observations with NDVI < 0.25, Mar 15-May 15 (Landsat; bare soil)",
    "mediana de refl_swir1 con NDVI < 0,25, 15 mar-15 may (Landsat)":
        "Median refl_swir1 of observations with NDVI < 0.25, Mar 15-May 15 (Landsat; bare soil)",
    "mediana de refl_swir2 con NDVI < 0,25, 15 mar-15 may (Landsat)":
        "Median refl_swir2 of observations with NDVI < 0.25, Mar 15-May 15 (Landsat; bare soil)",
    "(swir1 − swir2)/(swir1 + swir2) de las medianas, 15 mar-15 may":
        "NBR2 = (swir1 − swir2)/(swir1 + swir2) of the medians, Mar 15-May 15",
    "observaciones con NDVI < 0,25, 15 mar-15 may": "Observations with NDVI < 0.25, Mar 15-May 15",
    "mediana de refl_blue con NDVI < 0,25, oct-nov (Landsat)":
        "Median refl_blue of observations with NDVI < 0.25, Oct-Nov (Landsat; bare soil)",
    "mediana de refl_red con NDVI < 0,25, oct-nov (Landsat)":
        "Median refl_red of observations with NDVI < 0.25, Oct-Nov (Landsat; bare soil)",
    "mediana de refl_nir con NDVI < 0,25, oct-nov (Landsat)":
        "Median refl_nir of observations with NDVI < 0.25, Oct-Nov (Landsat; bare soil)",
    "mediana de refl_swir1 con NDVI < 0,25, oct-nov (Landsat)":
        "Median refl_swir1 of observations with NDVI < 0.25, Oct-Nov (Landsat; bare soil)",
    "mediana de refl_swir2 con NDVI < 0,25, oct-nov (Landsat)":
        "Median refl_swir2 of observations with NDVI < 0.25, Oct-Nov (Landsat; bare soil)",
    "(swir1 − swir2)/(swir1 + swir2) de las medianas, oct-nov":
        "NBR2 = (swir1 − swir2)/(swir1 + swir2) of the medians, Oct-Nov",
    "observaciones con NDVI < 0,25, oct-nov": "Observations with NDVI < 0.25, Oct-Nov",
    "mediana multianual (todos los años) de refl_blue con NDVI < 0,25 en ambas ventanas":
        "Multi-year median (all years) of refl_blue with NDVI < 0.25 in both windows",
    "mediana multianual (todos los años) de refl_red con NDVI < 0,25 en ambas ventanas":
        "Multi-year median (all years) of refl_red with NDVI < 0.25 in both windows",
    "mediana multianual (todos los años) de refl_nir con NDVI < 0,25 en ambas ventanas":
        "Multi-year median (all years) of refl_nir with NDVI < 0.25 in both windows",
    "mediana multianual (todos los años) de refl_swir1 con NDVI < 0,25 en ambas ventanas":
        "Multi-year median (all years) of refl_swir1 with NDVI < 0.25 in both windows",
    "mediana multianual (todos los años) de refl_swir2 con NDVI < 0,25 en ambas ventanas":
        "Multi-year median (all years) of refl_swir2 with NDVI < 0.25 in both windows",
    "NBR2 de las medianas multianuales": "NBR2 of the multi-year medians",
    "observaciones de suelo desnudo de todos los años": "Bare-soil observations across all years",
    "precipitación PRECTOTCORR": "Precipitation (PRECTOTCORR)",
    "temperatura máxima a 2 m": "Maximum air temperature at 2 m",
    "temperatura mínima a 2 m": "Minimum air temperature at 2 m",
    "temperatura media a 2 m": "Mean air temperature at 2 m",
    "humedad relativa a 2 m": "Relative humidity at 2 m",
    "viento a 2 m": "Wind speed at 2 m",
    "radiación global ALLSKY_SFC_SW_DWN": "All-sky surface shortwave radiation (ALLSKY_SFC_SW_DWN)",
    "ETo FAO-56 Penman-Monteith": "FAO-56 Penman-Monteith reference ET",
    "precipitación IMERG de la celda de 0,1° del centroide": "IMERG precipitation of the 0.1° cell containing the centroid",
    "SMAP L4 zona radicular, celda de 9 km del centroide": "SMAP L4 root-zone soil moisture, 9 km cell containing the centroid",
    "SMAP L4 superficial, celda de 9 km del centroide": "SMAP L4 surface soil moisture, 9 km cell containing the centroid",
    "lluvia abril-septiembre": "April-September precipitation",
    "lluvia de abril": "April precipitation",
    "lluvia de mayo": "May precipitation",
    "lluvia de julio": "July precipitation",
    "lluvia de agosto": "August precipitation",
    "Σ (prec − ETo) abril-septiembre": "Σ (precipitation − ETo) April-September",
    "días de julio con tmax > 30 °C": "July days with tmax > 30 °C",
    "tmax media de julio": "Mean July tmax",
    "grados día 10/30 °C abril-septiembre": "Growing degree days 10/30 °C, April-September",
    "lluvia noviembre del año anterior a marzo": "Precipitation from November of the previous year to March",
    "días de abril-mayo con lluvia > 50 mm": "April-May days with precipitation > 50 mm",
    "lluvia IMERG abril-septiembre": "IMERG precipitation, April-September",
    "lluvia IMERG de abril": "IMERG precipitation, April",
    "lluvia IMERG de mayo": "IMERG precipitation, May",
    "lluvia IMERG de julio": "IMERG precipitation, July",
    "lluvia IMERG de agosto": "IMERG precipitation, August",
    "días de abril-mayo con IMERG > 50 mm": "April-May days with IMERG precipitation > 50 mm",
    "SMAP zona radicular media abril-septiembre, celda de 9 km del centroide":
        "SMAP root-zone soil moisture, April-September mean, 9 km cell containing the centroid",
    "1 si la celda AgTile-US que contiene el centro del píxel está drenada con caños":
        "1 if the AgTile-US cell containing the pixel center is tile-drained",
    # nldas
    "Humedad volumétrica 0-10 cm: SoilM_0_10cm (kg m-2) / 100 mm, media ponderada del condado":
        "Volumetric soil moisture 0-10 cm: SoilM_0_10cm (kg m-2) / 100 mm, weighted county mean",
    "Humedad volumétrica 0-100 cm: SoilM_0_100cm (kg m-2) / 1000 mm, media ponderada del condado":
        "Volumetric soil moisture 0-100 cm: SoilM_0_100cm (kg m-2) / 1000 mm, weighted county mean",
    "Anomalía z de sm_0_100cm_m3m3 por condado y mes calendario, base 1991-2020":
        "z-score anomaly of sm_0_100cm_m3m3 per county and calendar month, 1991-2020 baseline",
    "Evapotranspiración total del mes (Evap, suma mensual)": "Monthly total evapotranspiration (Evap, monthly sum)",
    "Escorrentía total del mes: superficial (Qs) + subsuperficial (Qsb)":
        "Monthly total runoff: surface (Qs) + subsurface (Qsb)",
    "Equivalente en agua de la nieve, media del mes (SWE)": "Snow water equivalent, monthly mean (SWE)",
    # paisaje
    "% del área del condado en Cultivated Crops (clase NLCD 82)": "% of county area in Cultivated Crops (NLCD class 82)",
    "% del área del condado en Pasture/Hay (clase NLCD 81)": "% of county area in Pasture/Hay (NLCD class 81)",
    "% del área del condado en bosque (clases NLCD 41, 42 y 43)": "% of county area in forest (NLCD classes 41, 42 and 43)",
    "% del área del condado en humedales (clases NLCD 90 y 95)": "% of county area in wetlands (NLCD classes 90 and 95)",
    "% del área del condado en desarrollo urbano (clases NLCD 21 a 24)":
        "% of county area in developed land (NLCD classes 21 to 24)",
    "% del área del condado en agua abierta (clase NLCD 11)": "% of county area in open water (NLCD class 11)",
    "Superficie impermeable media del condado (media de Annual NLCD FctImp, 0-100 % por píxel)":
        "Mean county impervious surface (mean of Annual NLCD FctImp, 0-100 % per pixel)",
    # suelo_terreno
    "Agua disponible 0–100 cm (muaggatt.aws0100wta × 10), media ponderada por superficie":
        "Available water storage 0–100 cm (muaggatt.aws0100wta × 10), area-weighted mean",
    "Agua disponible 0–150 cm (muaggatt.aws0150wta × 10)": "Available water storage 0–150 cm (muaggatt.aws0150wta × 10)",
    "Carbono orgánico 0–30 cm: Σ espesor · MO · 0,58 · densidad aparente · (1 − fragmentos)":
        "Soil organic carbon 0–30 cm: Σ thickness · OM · 0.58 · bulk density · (1 − rock fragments)",
    "Carbono orgánico 0–100 cm (mismo cálculo)": "Soil organic carbon 0–100 cm (same calculation)",
    "NCCPI 3.0 general (cointerp.interphr)": "NCCPI 3.0 overall (cointerp.interphr)",
    "NCCPI 3.0, submodelo maíz (Corn Submodel I)": "NCCPI 3.0, corn submodel (Corn Submodel I)",
    "NCCPI 3.0, submodelo soja (Soybeans Submodel I)": "NCCPI 3.0, soybean submodel (Soybeans Submodel I)",
    "Profundidad de raíces: mín(restricción que limita raíces, fondo del perfil, 150 cm)":
        "Rooting depth: min(root-restrictive layer, bottom of profile, 150 cm)",
    "Clase de drenaje del componente dominante (muaggatt.drclassdcd) con más superficie en el condado":
        "Drainage class of the dominant component (muaggatt.drclassdcd) covering the largest area in the county",
    "Grupo hidrológico dominante (muaggatt.hydgrpdcd) con más superficie":
        "Dominant hydrologic soil group (muaggatt.hydgrpdcd) covering the largest area",
    "Profundidad mínima anual de la napa (muaggatt.wtdepannmin), media de las unidades con napa < 200 cm":
        "Annual minimum water table depth (muaggatt.wtdepannmin), mean over map units with water table < 200 cm",
    "Arcilla total 0–30 cm (claytotal_r), media ponderada por espesor, componente y superficie":
        "Total clay 0–30 cm (claytotal_r), weighted by thickness, component and area",
    "Arena total 0–30 cm (sandtotal_r)": "Total sand 0–30 cm (sandtotal_r)",
    "Limo total 0–30 cm (silttotal_r)": "Total silt 0–30 cm (silttotal_r)",
    "Materia orgánica 0–30 cm (om_r)": "Organic matter 0–30 cm (om_r)",
    "pH en agua 1:1, 0–30 cm (ph1to1h2o_r)": "pH in water 1:1, 0–30 cm (ph1to1h2o_r)",
    "Clase textural USDA de la arena/limo/arcilla media del condado":
        "USDA texture class of the county's mean sand/silt/clay",
    "Factor K (kwfact) del horizonte superficial": "K factor (kwfact) of the surface horizon",
    'Elevación media de los píxeles de 1" del condado': 'Mean elevation of the county\'s 1" pixels',
    "Desvío estándar de la elevación": "Standard deviation of elevation",
    'Pendiente media a 3" (~90 m, media de 3 × 3 píxeles), diferencias centradas':
        'Mean slope at 3" (~90 m, mean of 3 × 3 pixels), central differences',
    '% de píxeles de 3" con pendiente > 2 %': '% of 3" pixels with slope > 2 %',
    'Índice topográfico de humedad ln(a / tan β) a 3" (~90 m), media':
        'Topographic wetness index ln(a / tan β) at 3" (~90 m), mean',
    "% del área con TWI en el decil superior de toda la zona de estudio":
        "% of area with TWI in the top decile of the whole study area",
    # teledeteccion
    "% de píxeles agrícolas muestreados con mediana de NDVI < 0,25 en abril–mayo":
        "% of sampled cropland pixels with median NDVI < 0.25 in April–May (bare soil)",
    "% de píxeles agrícolas muestreados con mediana de NDVI < 0,25 en octubre–noviembre":
        "% of sampled cropland pixels with median NDVI < 0.25 in October–November (bare soil)",
    "% de píxeles agrícolas muestreados con mediana de NDVI >= 0,3 del 15-03 al 30-04":
        "% of sampled cropland pixels with median NDVI >= 0.3 from Mar 15 to Apr 30 (green cover)",
    "Media de la mediana por píxel del Bare Soil Index de abril–mayo":
        "Mean of the per-pixel median Bare Soil Index in April–May",
    "Media de los píxeles del NDVI máximo de abril–septiembre (30 m)":
        "Pixel mean of the April–September maximum NDVI (30 m)",
    "Escenas leídas con al menos 10 % de los píxeles agrícolas muestreados despejados":
        "Scenes read with at least 10 % of the sampled cropland pixels clear",
    "Observaciones despejadas / observaciones de píxeles agrícolas leídas en el año":
        "Clear observations / cropland pixel observations read in the year",
    # validacion
    "Lluvia total del mes, media de las celdas PRISM de 4 km cuyo centro cae en el condado":
        "Monthly total precipitation, mean of the 4 km PRISM cells whose center falls in the county",
    "Temperatura máxima media del mes, media por condado": "Monthly mean maximum temperature, county mean",
    "Temperatura mínima media del mes, media por condado": "Monthly mean minimum temperature, county mean",
    "Temperatura media del mes (tmean de PRISM = (tmax + tmin) / 2), media por condado":
        "Monthly mean temperature (PRISM tmean = (tmax + tmin) / 2), county mean",
    "Lluvia del mes: media entre las estaciones del condado con al menos 25 reportes diarios en el mes (suma de los días reportados, pulgadas × 25,4)":
        "Monthly precipitation: mean over the county's stations with at least 25 daily reports in the month (sum of reported days, inches × 25.4)",
    "Estaciones CoCoRaHS del condado con al menos 25 reportes diarios en el mes (0 = ninguna; vacío antes de 2008)":
        "County CoCoRaHS stations with at least 25 daily reports in the month (0 = none; empty before 2008)",
    # vegetacion
    "NDVI medio del condado (compuesto de 16 días; fecha = inicio del compuesto)":
        "County mean NDVI (16-day composite; fecha = composite start date)",
    "EVI medio del condado": "County mean EVI",
    "NDVI medio de los píxeles con >= 75 % de maíz (CDL del año)": "Mean NDVI of pixels with >= 75 % corn (same-year CDL)",
    "NDVI medio de los píxeles con >= 75 % de soja (CDL del año)": "Mean NDVI of pixels with >= 75 % soybeans (same-year CDL)",
    "Píxeles que pasan el filtro de calidad sobre los píxeles del condado":
        "Pixels passing the quality filter / all county pixels",
    "Media de los compuestos de 16 días que empiezan en el mes": "Mean of the 16-day composites starting in the month",
    "Media mensual del NDVI de maíz (CDL >= 75 %)": "Monthly mean corn NDVI (CDL >= 75 %)",
    "Media mensual del NDVI de soja (CDL >= 75 %)": "Monthly mean soybean NDVI (CDL >= 75 %)",
    "Como ndvi_maiz, con umbral de pureza de 50 %: píxeles con >= 50 % de maíz (CDL del año)":
        "Like ndvi_maiz, with a 50 % purity threshold: pixels with >= 50 % corn (same-year CDL)",
    "Como ndvi_soja, con umbral de pureza de 50 %: píxeles con >= 50 % de soja (CDL del año)":
        "Like ndvi_soja, with a 50 % purity threshold: pixels with >= 50 % soybeans (same-year CDL)",
    "Media mensual del NDVI de maíz (CDL >= 50 %)": "Monthly mean corn NDVI (CDL >= 50 %)",
    "Media mensual del NDVI de soja (CDL >= 50 %)": "Monthly mean soybean NDVI (CDL >= 50 %)",
    "Como ndvi_max_maiz, desde ndvi_maiz_p50 (CDL >= 50 %)": "Like ndvi_max_maiz, from ndvi_maiz_p50 (CDL >= 50 %)",
    "Como ndvi_max_soja, desde ndvi_soja_p50 (CDL >= 50 %)": "Like ndvi_max_soja, from ndvi_soja_p50 (CDL >= 50 %)",
    "LST diurna media (compuestos de 8 días que empiezan en el mes)":
        "Mean daytime land surface temperature (8-day composites starting in the month)",
    "LST nocturna media": "Mean nighttime land surface temperature",
    "ET real total del mes (Evap de NLDAS-2 Noah, media ponderada del condado)":
        "Monthly total actual ET (NLDAS-2 Noah Evap, weighted county mean)",
    "ET potencial total del mes (PotEvap de NLDAS-2 Noah, W m-2 × 86400 × días / 2,501e6)":
        "Monthly total potential ET (NLDAS-2 Noah PotEvap, W m-2 × 86400 × days / 2.501e6)",
    "et_mm / pet_mm": "et_mm / pet_mm (actual/potential ET ratio)",
    "(ndvi − media del mes calendario) / desvío, por condado, todos los años":
        "(ndvi − calendar-month mean) / standard deviation, per county, all years",
    "VCI = 100 (ndvi − mín) / (máx − mín) del mes calendario, por condado":
        "Vegetation Condition Index VCI = 100 (ndvi − min) / (max − min) for the calendar month, per county",
    "TCI = 100 (máx − lst_dia_c) / (máx − mín) del mes calendario, por condado":
        "Temperature Condition Index TCI = 100 (max − lst_dia_c) / (max − min) for the calendar month, per county",
    "VHI = 0,5 VCI + 0,5 TCI": "Vegetation Health Index VHI = 0.5 VCI + 0.5 TCI",
    "Día del año en que el NDVI suavizado sube al 50 % de la amplitud del año":
        "Day of year when smoothed NDVI rises to 50 % of the year's amplitude (start of season)",
    "Día del año del máximo NDVI suavizado (inicio del compuesto + 8 días)":
        "Day of year of maximum smoothed NDVI (composite start + 8 days)",
    "Día del año en que el NDVI suavizado baja al 50 % de la amplitud":
        "Day of year when smoothed NDVI falls to 50 % of the amplitude (end of season)",
    "Máximo del NDVI suavizado del año": "Annual maximum of smoothed NDVI",
    "doy_fin − doy_inicio": "doy_fin − doy_inicio (season length)",
    "Integral del NDVI suavizado entre doy_inicio y doy_fin": "Integral of smoothed NDVI between doy_inicio and doy_fin",
    "Picos del NDVI suavizado con prominencia >= 0,1": "Peaks of smoothed NDVI with prominence >= 0.1 (growth cycles)",
    "Máximo NDVI de maíz del año (compuestos de 16 días)": "Annual maximum corn NDVI (16-day composites)",
    "Máximo NDVI de soja del año (compuestos de 16 días)": "Annual maximum soybean NDVI (16-day composites)",
    "Días con NDVI diario interpolado < 0,3 entre 1-nov (anio−1) y 31-mar":
        "Days with interpolated daily NDVI < 0.3 between Nov 1 (anio−1) and Mar 31",
}


if __name__ == "__main__":
    sys.exit(main())
