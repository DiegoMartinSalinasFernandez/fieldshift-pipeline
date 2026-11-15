# Field Shift — data summary (English)

NASA Space Apps Challenge 2026, challenge **"Field Shift: Adapting Farms with NASA Data"**.

This repository downloads, cleans and structures public data into CSV tables so that a separate team can
build a machine-learning model that compares crop rotations in the US Corn Belt. **No models are trained
here.** This page summarizes what data exists, where it comes from and how it is checked. The full
data dictionaries (in Spanish) are in `docs/datasets/<package>.md`; full citations and DOIs are in
`docs/research/citas_nasa.md`.

Column names are in Spanish `snake_case` with the unit at the end (`prec_imerg_mm`, `tmax_c`,
`rend_bu_ac`). A short glossary is at the end of this page.

---

## 1. Study area, spatial and temporal units

| Item | Value |
|---|---|
| Region | US Corn Belt, **all counties of 7 states (666 counties)** |
| First batch | Iowa (IA, FIPS 19), Illinois (IL, 17), Indiana (IN, 18) |
| Second batch (approved 2026-11-14) | Ohio (OH, 39), Nebraska (NE, 31), Minnesota (MN, 27), Kansas (KS, 20) |
| Spatial unit | County, keyed by 5-digit FIPS code (`fips`, text with leading zeros, e.g. `19169` = Story County, IA) |
| Temporal unit | Year (`anio` = calendar year of harvest); monthly (`mes` = `YYYY-MM`), daily or 8/16-day (`fecha` = `YYYY-MM-DD`) files where relevant |
| Period | 2000–2025. Crop-rotation variables from 2008 (first year the Cropland Data Layer covers the whole country). NASA POWER is used from 1981 only as a baseline for SPI, anomalies and trends |
| Crops | Corn, soybean, winter wheat, oats, alfalfa and other hay. Cover crops (cereal rye) only as a practice, from the Census of Agriculture |
| CRS | Vectors in EPSG:4326; USDA rasters and areas in EPSG:5070 (CONUS Albers) |

Each machine of the team processes a subset of states and publishes its CSVs as a GitHub Release; the
coordinating machine merges all states. **Coverage figures quoted below come from each package's data card
and, unless stated otherwise, describe the first batch (IA, IL, IN; 293 counties).** Counts for the full
7-state tables are in the data cards of each release.

Irrigation note: in Nebraska and Kansas a large share of corn and soybean is irrigated. NASS county yields
for `ALL PRODUCTION PRACTICES` mix irrigated and rainfed fields, so they should not be compared directly with
Iowa without accounting for irrigation.

---

## 2. Data sources

### 2.1 NASA products

| Product | Version / ID | Native resolution | Package(s) | Access used |
|---|---|---|---|---|
| NASA POWER (Prediction Of Worldwide Energy Resources), AG community, daily | API, no DOI | MERRA-2 0.5° × 0.625° (meteorology), CERES 1° (radiation) | `clima`, `lotes` | POWER daily point API at each county centroid (and each field centroid) |
| GPM IMERG daily precipitation | Final Run V07 (`GPM_3IMERGDF`) to 2025-09-30, Late Run V07 (`GPM_3IMERGDL`) from 2025-10-01 | 0.1° | `clima`, `lotes` | `IMERG_PRECTOT` parameter of the POWER API |
| SMAP L4 soil moisture | `SPL4SMGP` (V8 certain from 2025-07-04; V7 or reprocessed V8 before) | 9 km | `agua`, `lotes` | Daily layers of the USDA NASS / George Mason University Crop-CASMA service |
| GRACE-DA-DM groundwater and soil-moisture drought indicators (US version) | `GRACEDADM_CLSM0125US_7D` | 0.125°, weekly | `agua` | Public copy at the National Drought Mitigation Center (nasagrace.unl.edu) |
| MODIS Terra vegetation indices | MOD13Q1 V061 | 250 m, 16-day | `vegetacion` | Microsoft Planetary Computer (read at a reduced overview, see §5) |
| MODIS Terra land surface temperature | MOD11A2 V061 | 1 km, 8-day | `vegetacion` | Microsoft Planetary Computer |
| NLDAS-2 Noah land-surface model, monthly | `NLDAS_NOAH0125_M` V2.0 | 0.125°, monthly | `nldas`, `vegetacion` (ET and PET, replacing MOD16A2) | NASA GES DISC via Harmony (Earthdata login) |
| NASADEM elevation | `NASADEM_HGT` V001 | 1 arc-second (~30 m) | `suelo_terreno`, `lotes` | Microsoft Planetary Computer COGs |
| ECOSTRESS Collection 2 | `ECO_L2T_LSTE.002`, `ECO_L3T_JET.002`, `ECO_L4T_ESI.002` | 70 m | `ecostress` | LP DAAC Earthdata Cloud COGs |
| Harmonized Landsat Sentinel-2, Sentinel-2 part | `HLSS30` V2.0 | 30 m | `lotes` | Planetary Computer (2020+) and LP DAAC CMR-STAC (2015–2019) |
| Landsat Collection 2 Level-2 surface reflectance (joint USGS–NASA mission, distributed by USGS EROS) | Landsat 5, 7, 8, 9 C2 L2 | 30 m | `teledeteccion`, `lotes` | Microsoft Planetary Computer |

Planned but **not used**: MOD16A2 (replaced by NLDAS-2 Noah ET/PET), MCD12Q1 (the agricultural mask comes
from the CDL) and the global GRACE-DA-DM (`GRACEDADM_CLSM025GL_7D`; the higher-resolution US version was used).

### 2.2 Non-NASA sources

| Source | Agency | Package(s) | Used for |
|---|---|---|---|
| NASS Quick Stats (SURVEY, county) | USDA NASS | `cultivos`, `economia` | Yield, planted and harvested area, production, prices received |
| NASS Crop Progress (state, weekly) | USDA NASS | `cultivos` | Planting, emergence, silking/blooming and harvest dates |
| Census of Agriculture 2012, 2017, 2022 | USDA NASS | `cultivos`, `lotes` | Cover crops, no-till, tile drainage, irrigation |
| Cropland Data Layer (CDL), 30 m (10 m in 2024–2025) | USDA NASS | `cultivos`, `vegetacion`, `teledeteccion`, `ecostress`, `lotes` | Crop shares, crop transitions, agricultural / corn / soybean masks |
| Crop Sequence Boundaries (CSB) 2018–2025 | USDA NASS | `lotes` | Polygons of the 10 demonstration fields. (County-level 8-year sequences in `cultivos` are computed directly from CDL pixels, see §3.2) |
| SSURGO tabular data via Soil Data Access | USDA NRCS | `suelo_terreno`, `lotes` | Soil properties. The gSSURGO 10 m raster and its `Valu1` table were **not** used (see `suelo_terreno.md`) |
| 3D Elevation Program (3DEP), bare-earth DEM, requested at 10 m | USGS | `lotes` (approved extra) | Field-scale terrain |
| Annual NLCD Collection 1 | USGS | `paisaje` | Land cover shares and imperviousness |
| Commodity Costs and Returns | USDA ERS | `economia` | Costs and returns per planted acre |
| Cartographic Boundary Files 2024, 1:500k | US Census Bureau | `base` | County polygons, centroids, areas |
| PRISM (monthly, 4 km) and CoCoRaHS (rain gauges) | Oregon State Univ.; Colorado Climate Center | `validacion` | Ground reference to validate POWER and IMERG only |
| AgTile-US (Valayamkunnath et al. 2020) | Academic (CC BY 4.0) | `lotes` | Modeled tile-drainage map |

---

## 3. Packages and main columns

Every table starts with its keys (`fips`, `anio`, and `fecha` or `mes` when applicable). Only the main
columns are listed; the complete dictionary, coverage (from/to) and % missing per column are in each data card.

### 3.1 `clima` — weather (NASA POWER + GPM IMERG)

Files: `clima_diario.csv`, `clima_mensual.csv`, `clima_anual.csv`. POWER is sampled at the county centroid;
IMERG is the simple mean of the 0.1° cells whose centre falls in the county.

| Column | Description | Unit | Source |
|---|---|---|---|
| `tmax_c`, `tmin_c`, `tmed_c` | Daily max / min / mean 2 m air temperature (monthly: mean of daily values) | °C | NASA POWER |
| `prec_power_mm` | Corrected precipitation (PRECTOTCORR); monthly = sum | mm | NASA POWER |
| `prec_imerg_mm` | IMERG precipitation, county mean of 0.1° cells; monthly = sum | mm | GPM IMERG via POWER |
| `rad_mj_m2` | All-sky surface shortwave radiation | MJ/m² (per day or per month) | NASA POWER |
| `hr_pct`, `viento_ms` | 2 m relative humidity, 2 m wind speed (daily file) | %, m/s | NASA POWER |
| `gwettop`, `gwetroot`, `gwetprof` | Surface, root-zone and profile soil wetness | 0–1 | NASA POWER |
| `eto_pm_mm` | FAO-56 Penman–Monteith reference evapotranspiration | mm | Derived from POWER |
| `deficit_mm` | `prec_power_mm − eto_pm_mm` | mm | Derived from POWER |
| `gdd_10_30` | Growing degree days, corn method (base 10 °C, cap 30 °C) | °C·day | Derived from POWER |
| `dias_tmax_gt30`, `dias_tmax_gt35` | Days with Tmax > 30 °C / > 35 °C | days | Derived from POWER |
| `dias_tmin_le0`, `dias_tmin_le_m2` | Days with Tmin ≤ 0 °C / ≤ −2 °C | days | Derived from POWER |
| `prec_max1d_mm`, `prec_max5d_mm`, `dias_lluvia_gt50`, `racha_seca_max_dias` | Rx1day, Rx5day, days > 50 mm, longest dry spell | mm, days | Derived from POWER |
| `spi1`, `spi3`, `spi6` | Standardized Precipitation Index (gamma fit per county and month, 1981–2025) | dimensionless | Derived from POWER |
| `anom_tmed_c` | Mean temperature anomaly vs 1991–2020 | °C | Derived from POWER |
| `doy_ultima_helada`, `doy_primera_helada`, `periodo_libre_heladas_dias` | Last spring frost, first fall frost (Tmin ≤ 0 °C), frost-free period | day of year, days | Derived from POWER |
| `prec_temporada_mm`, `gdd_temporada`, `deficit_temporada_mm` | Season totals, April–September | mm, °C·day | Derived from POWER |
| `prec_invierno_previo_mm` | Precipitation, November of previous year to March | mm | Derived from POWER |
| `prec_jul_mm`, `tmax_jul_c`, `dias_tmax_gt30_jul`, `prec_ago_mm` | Critical months: July (corn silking) and August (soybean pod fill) | mm, °C, days | Derived from POWER |
| `tend_prec_mm_decada`, `tend_tmed_c_decada` | OLS trend over the 30 years ending in `anio` (no future years) | mm/decade, °C/decade | Derived from POWER |

Coverage (data card): 2000–2025, 0 % missing in every column.

### 3.2 `cultivos` — crops, rotations and practices (USDA NASS, CDL)

Files: `produccion_anual.csv` (long format, one row per county, year and crop), `rotacion_anual.csv`,
`rotacion_secuencia.csv`, `practicas_censo.csv`, `fenologia_estado.csv` (keyed by `fips_estado`).

| Column | Description | Unit | Source |
|---|---|---|---|
| `rend_bu_ac` | Yield (corn: grain). Empty for alfalfa and hay (measured in tons) | bu/ac | NASS Quick Stats |
| `rend_kgha` | Yield converted with the bushel weight of each crop | kg/ha | Derived from NASS |
| `sup_sembrada_ac`, `sup_cosechada_ac` | Planted and harvested area | acres | NASS Quick Stats |
| `produccion_bu` | Production | bu | NASS Quick Stats |
| `ratio_cosechada` | Harvested / planted area | fraction | Derived from NASS |
| `flag_nass` | Original NASS code when the value is withheld, e.g. `(D)` | text | NASS Quick Stats |
| `pct_maiz`, `pct_soja`, `pct_trigo`, `pct_alfalfa`, `pct_heno`, `pct_doble_trigo_soja`, `pct_barbecho` | Share of the county's cropland in each crop | % | CDL 30 m |
| `pct_maiz_tras_soja`, `pct_maiz_tras_maiz`, `pct_soja_tras_maiz`, `pct_soja_tras_soja` | Pixel-level transitions between CDL of year − 1 and year | % | CDL 30 m |
| `pct_maiz_soja_alternado`, `pct_maiz_continuo`, `pct_soja_continua`, `pct_rotacion_trigo`, `pct_rotacion_alfalfa` | 8-year sequence classes per county and window (2008–2015 … 2018–2025) | % | CDL 30 m (per-pixel, CSB-like) |
| `cultivos_por_anio`, `diversidad_shannon` | Crops per year and Shannon diversity of the 8-year sequence | crops/yr, index | CDL 30 m |
| `pct_cobertura`, `pct_labranza_cero`, `pct_drenaje_tile`, `pct_riego` | Cover crops, no-till, tile drainage, irrigation (share of cropland) | % | Census of Agriculture |
| `doy_50_sembrado`, `doy_50_emergido`, `doy_50_floracion`, `doy_50_cosechado` | Day when 50 % of the state's crop is planted / emerged / silking-blooming / harvested (corn and soybean) | day of year | NASS Crop Progress |

Coverage (data card): production 2000–2025; rotations 2008–2025 (transitions from 2009); census practices
2017 and 2022 (irrigation also 2012). Yield trend is **not** removed here: the ML team does it inside each fold
to avoid leaking future information.

### 3.3 `vegetacion` — MODIS vegetation and land surface temperature

Files: `vegetacion_16d.csv`, `vegetacion_mensual.csv`, `fenologia_anual.csv`.

| Column | Description | Unit | Source |
|---|---|---|---|
| `ndvi`, `evi` | County-mean NDVI / EVI after quality filtering | dimensionless | MODIS MOD13Q1 V061 |
| `ndvi_maiz`, `ndvi_soja` | NDVI of MODIS pixels ≥ 75 % corn / soybean in that year's CDL (from 2008) | dimensionless | MOD13Q1 + CDL masks |
| `frac_pixeles_validos` | Share of county pixels passing the quality filter | 0–1 | MOD13Q1 |
| `lst_dia_c`, `lst_noche_c` | Day / night land surface temperature | °C | MODIS MOD11A2 V061 |
| `et_mm`, `pet_mm`, `et_pet_ratio` | Evapotranspiration, potential ET and their ratio | mm, mm, dimensionless | NLDAS-2 Noah (replaces MOD16A2) |
| `ndvi_anom_z`, `vci`, `tci`, `vhi` | NDVI z-anomaly, Vegetation / Temperature Condition and Vegetation Health indices | dimensionless, 0–100 | Derived from MOD13Q1 and MOD11A2 |
| `doy_inicio`, `doy_pico`, `doy_fin`, `duracion_dias` | Green-up, peak and senescence dates (Savitzky–Golay smoothed series) | day of year, days | Derived from MOD13Q1 |
| `ndvi_max`, `ndvi_integral`, `n_ciclos` | Peak NDVI, seasonal integral, number of cycles (detects double cropping) | dimensionless, NDVI·day, count | Derived from MOD13Q1 |
| `ndvi_max_maiz`, `ndvi_max_soja` | Peak NDVI of corn / soybean pixels | dimensionless | Derived from MOD13Q1 + CDL |
| `dias_ndvi_lt03_invierno` | Days with NDVI < 0.3 in the previous winter (proxy for lack of winter cover) | days | Derived from MOD13Q1 |

Coverage (data card): 2000-02 to 2025-12; corn and soybean NDVI from 2008.

### 3.4 `agua` — soil moisture and groundwater (SMAP L4, GRACE-DA-DM)

Files: `agua_diario.csv`, `agua_mensual.csv`, `agua_semanal.csv`.

| Column | Description | Unit | Source |
|---|---|---|---|
| `sm_surface_m3m3`, `sm_rootzone_m3m3` | Surface and root-zone volumetric soil moisture, area-weighted county mean | m³/m³ | SMAP L4 (Crop-CASMA) |
| `sm_surface_min_m3m3`, `sm_rootzone_min_m3m3` | Monthly minimum of the daily county means | m³/m³ | SMAP L4 |
| `sm_rootzone_anom_z` | Root-zone z-anomaly per county and calendar month | dimensionless | Derived from SMAP L4 |
| `dias_sm_saturado` | Days with root-zone moisture ≥ 0.40 m³/m³ (provisional threshold; spring excess water delays planting) | days | Derived from SMAP L4 |
| `gws_pctl`, `rtzsm_pctl`, `sfsm_pctl` | Groundwater, root-zone and surface soil-moisture drought percentiles (weekly) | percentile 0–100 | GRACE-DA-DM US |

Coverage (data card): SMAP 2015-03-31 to 2025-12-31; GRACE-DA-DM 2003-01-06 to 2025-12-29.

### 3.5 `nldas` — NLDAS-2 Noah land-surface model

File: `nldas_mensual.csv`. Complements SMAP, which starts only in 2015.

| Column | Description | Unit | Source |
|---|---|---|---|
| `sm_0_10cm_m3m3`, `sm_0_100cm_m3m3` | Volumetric soil moisture 0–10 cm and 0–100 cm | m³/m³ | NLDAS-2 Noah |
| `sm_0_100cm_anom_z` | z-anomaly of 0–100 cm moisture, baseline 1991–2020 | dimensionless | NLDAS-2 Noah |
| `et_nldas_mm` | Total monthly evapotranspiration (same variable as `et_mm` in `vegetacion`: do not use both) | mm | NLDAS-2 Noah |
| `escorrentia_nldas_mm` | Surface + subsurface runoff | mm | NLDAS-2 Noah |
| `swe_nldas_mm` | Snow water equivalent, monthly mean | mm | NLDAS-2 Noah |

Coverage (data card): 2000-01 to 2025-12, 0 % missing.

### 3.6 `ecostress` — ECOSTRESS 70 m

File: `ecostress_mensual.csv`. A sample window of 2.24 km × 2.24 km of agricultural pixels per county, not the
whole county.

| Column | Description | Unit | Source |
|---|---|---|---|
| `lst_ecostress_c` | Land surface temperature, monthly mean of daytime passes | °C | ECO_L2T_LSTE.002 |
| `et_ecostress_mm_dia` | Daily evapotranspiration | mm/day | ECO_L3T_JET.002 |
| `esi_ecostress` | Evaporative Stress Index (ET/PET) | dimensionless | ECO_L4T_ESI.002 |
| `n_pasadas_ecostress` | Passes in the month with ≥ 10 valid agricultural pixels | passes | ECOSTRESS |

Coverage (data card): April–October only; the current CSV covers 2025-04 to 2025-10 and grows as the download
continues (target 2018-08 to 2025-10).

### 3.7 `suelo_terreno` — soil and terrain (static, one row per county)

File: `suelo_terreno_estatico.csv`.

| Column | Description | Unit | Source |
|---|---|---|---|
| `aws0_100_mm`, `aws0_150_mm` | Available water storage 0–100 / 0–150 cm | mm | SSURGO (muaggatt) |
| `soc0_30_gm2`, `soc0_100_gm2` | Soil organic carbon 0–30 / 0–100 cm | g C/m² | SSURGO (chorizon) |
| `nccpi_general`, `nccpi_maiz`, `nccpi_soja` | National Commodity Crop Productivity Index 3.0 (overall, corn, soybean) | 0–1 | SSURGO (cointerp) |
| `prof_raices_cm` | Rooting depth (min of root-limiting layer, profile bottom, 150 cm) | cm | SSURGO |
| `clase_drenaje`, `grupo_hidrologico` | Dominant drainage class and hydrologic group | class | SSURGO (muaggatt) |
| `napa_min_cm` | Minimum annual water-table depth | cm | SSURGO (muaggatt) |
| `arcilla_pct`, `arena_pct`, `limo_pct`, `materia_organica_pct`, `ph_agua` | Clay, sand, silt, organic matter and pH, 0–30 cm | %, pH | SSURGO (chorizon) |
| `clase_textural_usda`, `factor_k_rusle` | USDA texture class; RUSLE K factor | class, NRCS units | SSURGO (chorizon) |
| `elevacion_media_m`, `elevacion_desvio_m` | Mean and SD of elevation | m | NASADEM |
| `pendiente_media_pct`, `pendiente_gt2_pct` | Mean slope (at ~90 m) and % of area with slope > 2 % | % | NASADEM |
| `twi_medio`, `twi_decil_sup_pct` | Mean Topographic Wetness Index; % of area in the top TWI decile of the study area | dimensionless, % | NASADEM |

### 3.8 `teledeteccion` — Landsat 30 m (bare soil and winter cover)

File: `teledeteccion_anual.csv`. Two 1.2 km × 1.2 km windows of agricultural pixels per county.

| Column | Description | Unit | Source |
|---|---|---|---|
| `pct_suelo_desnudo_abr_may`, `pct_suelo_desnudo_oct_nov` | Sampled agricultural pixels with median NDVI < 0.25 in Apr–May / Oct–Nov | % | Landsat C2 L2 |
| `pct_cobertura_verde_mar_abr` | Sampled agricultural pixels with median NDVI ≥ 0.3, 15 Mar–30 Apr (green winter cover) | % | Landsat C2 L2 |
| `bsi_abr_may` | Bare Soil Index, April–May | dimensionless | Landsat C2 L2 |
| `ndvi_max_30m` | Peak April–September NDVI at 30 m | dimensionless | Landsat C2 L2 |
| `n_escenas_validas`, `frac_pixeles_validos` | Valid scenes and clear-observation fraction | scenes, fraction | Landsat C2 L2 |

Coverage (data card): 2019–2025 so far (partial download, recent years first).

### 3.9 `paisaje` — land cover (USGS Annual NLCD)

File: `paisaje_anual.csv`.

| Column | Description | Unit | Source |
|---|---|---|---|
| `pct_cultivos_nlcd`, `pct_pasturas_heno_nlcd` | Cultivated crops (class 82), pasture/hay (81) | % of county | Annual NLCD |
| `pct_bosque_nlcd`, `pct_humedales_nlcd`, `pct_urbano_nlcd`, `pct_agua_nlcd` | Forest, wetlands, developed, open water | % of county | Annual NLCD |
| `impermeable_pct` | Mean impervious surface | % | Annual NLCD |

Coverage (data card): 2000–2024 (2025 not yet published by USGS).

### 3.10 `economia` — prices, costs and returns (state level)

Files: `economia_anual.csv` (corn, soybean, winter wheat, oats) and `economia_forrajes_anual.csv` (alfalfa,
hay). Keyed by `fips_estado`, because the data only exist by state (NASS) or by ERS region.

| Column | Description | Unit | Source |
|---|---|---|---|
| `precio_usd_bu` / `precio_usd_ton` | Price received by farmers, marketing-year average | USD/bu, USD/short ton | NASS Quick Stats |
| `valor_produccion_usd_ac` | Gross value of production per planted acre | USD/ac | USDA ERS, regions weighted by planted area |
| `costo_operativo_usd_ac`, `costo_total_usd_ac` | Operating costs and total listed costs per planted acre | USD/ac | USDA ERS |
| `margen_operativo_usd_ac` | Value of production less operating costs | USD/ac | USDA ERS |
| `flag_nass` | Original NASS code when the price is withheld | text | NASS Quick Stats |

Coverage (data card): 2000–2025 for all 7 states; ERS oats start in 2005; ERS has no costs for alfalfa or hay.

### 3.11 `validacion` — ground reference (not NASA)

File: `validacion_mensual.csv` with `prec_prism_mm`, `tmax_prism_c`, `tmin_prism_c`, `tmed_prism_c`
(PRISM 4 km) and `prec_cocorahs_mm`, `n_estaciones_cocorahs` (CoCoRaHS gauges, from 2008). Used only to
validate POWER and IMERG (§5.3).

### 3.12 `lotes` — 30 m pixels in 10 demonstration fields (separate delivery)

Requested by the ML team to split fields into management zones (dry knoll, wet depression, mid-slope).
Published separately (`fieldshift_lotes_v1`) and **not** merged into the annual or monthly tables.

- **Fields:** CSB 2018–2025 polygons, 30–120 ha, corn or soybean in at least 6 of 8 years, county irrigation
  < 5 %: 3 in the Des Moines Lobe (Hamilton, IA), 3 on loess hills (Crawford and Shelby, IA), 2 controls in
  Champaign (IL) and 2 in Tippecanoe (IN). Keys: `fips`, `id_lote` (`<fips>_<CSBID>`), `px_id`, plus
  `anio`/`fecha`; soils use `mukey`.
- **Grid:** the 30 m grid of the agricultural mask (EPSG:5070).

| File | Main columns (English description) | Source |
|---|---|---|
| `lotes.csv`, `pixeles.csv` | Field area, compactness, pixel counts, relief; pixel coordinates, distance to edge, interior flag | CSB, project grid |
| `terreno_px.csv` | Elevation, slope, aspect, plan/profile curvature, TPI (90 m, 300 m), TWI, depression depth; same from 3DEP at 10 m (`*_3dep*`) | NASADEM; USGS 3DEP |
| `cultivo_px_anual.csv`, `lotes_anual.csv` | CDL class and crop group per pixel and year; main crop and purity per field | CDL (30 m; 10 m in 2024–2025), CSB |
| `suelo_px.csv`, `suelo_mukey.csv` | Map-unit fraction per pixel; available water, SOC, NCCPI, drainage, hydrologic group, water table, texture, OM, pH, K factor per map unit | SSURGO |
| `vegetacion_px_obs.csv` | Clear observations: blue, green, red, NIR, SWIR1, SWIR2 reflectance, NDVI, EVI2, GCVI, NDMI, SLC-off flag, raw QA | Landsat C2 L2; HLS S30 V2.0 |
| `vegetacion_px_anual.csv` | Annual peak NDVI/EVI2 and its date, July–August mean NDVI, clear-observation counts, HLS peak NDVI | Landsat C2 L2; HLS S30 |
| `suelo_desnudo_px*.csv` | Bare-soil median reflectance and NBR2 (NDVI < 0.25, spring and fall; per year and multi-year composite) | Landsat C2 L2 |
| `clima_lote_diario.csv`, `clima_lote_anual.csv` | Field-centroid weather (POWER), IMERG precipitation, SMAP soil moisture, ETo, GDD and seasonal totals | NASA POWER, GPM IMERG, SMAP L4 |
| `drenaje_px.csv` | Tile-drained pixel flag (modeled) | AgTile-US |

The ML team asked that nothing is normalized, smoothed, gap-filled or thresholded within fields: those steps
are done inside each training fold.

---

## 4. How the annual table is built

`src/merge.py` reads only `data/processed/` and is deterministic (same md5 in two runs).

- **`tabla_anual.csv`** — keys `fips, anio, cultivo`. Left join on the rows of `produccion_anual.csv`
  (one row per county, year and crop with NASS data), adding:
  - `clima_anual`, `rotacion_anual` and `fenologia_anual` by `fips, anio`;
  - `fenologia_estado` by state (`fips[:2]`), `anio` and `cultivo` (corn and soybean only);
  - `suelo_terreno_estatico` by `fips`.

  Weather, rotation, phenology and soil values are repeated across the crop rows of the same county and year.
  Years or counties without a NASS row do not appear. Rotation columns are empty before 2008.
- **`tabla_mensual.csv`** — keys `fips, anio, mes`. Outer join of `clima_mensual`, `vegetacion_mensual`
  and `agua_mensual`; SMAP columns are empty before 2015-04.
- Files with another granularity stay separate: `rotacion_secuencia.csv` (8-year windows),
  `practicas_censo.csv` (census years) and the `lotes` delivery.
- Column names do not change when merging, so the data card of each package is the dictionary of the merged
  tables. Each state's CSVs are merged by the first two digits of `fips`.

Size reported in `merge.md` (run of 2026-11-14): `tabla_anual.csv` 25,070 rows × 73 columns;
`tabla_mensual.csv` 91,416 rows × 48 columns.

### Common windows for annual variables

| Window | Definition |
|---|---|
| Growing season | April–September of `anio` |
| Previous winter | November of `anio − 1` to March of `anio` |
| Critical months | July (corn silking) and August (soybean pod fill) |

---

## 5. Quality control

### 5.1 CSV contract (`validar_csv()` in `src/common/`)

Every processed CSV must pass:

- UTF-8, comma separator, dot as decimal mark, header in the first row; keys first and well formatted
  (5-digit `fips` with leading zeros, `YYYY-MM-DD` / `YYYY-MM`).
- No duplicate keys (including `cultivo` when present); every `fips` exists in `data/reference/condados.csv`;
  `anio` consistent with `fecha` / `mes`.
- **Missing values are empty cells** — never 0, −999 or −9999. Source fill values (e.g. POWER −999) are
  converted to empty. NASS withheld values `(D)` and `(Z)` are empty, with the original code in `flag_nass`.
- Physical ranges: precipitation ≥ 0, NDVI between −1 and 1, volumetric soil moisture 0–0.6, corn yield
  20–300 bu/ac, soybean yield 5–100 bu/ac, among others.
- US units are kept as published (`rend_bu_ac`, `sup_sembrada_ac`, `produccion_bu`); conversions go to
  separate columns (corn 1 bu/ac = 62.77 kg/ha; soybean and wheat 67.25; oats 35.87; 1 acre = 0.4047 ha).

### 5.2 Per-package quality filters (from the data cards)

- **MODIS:** only pixels with MOD13Q1 pixel reliability good or marginal, valid range, and not touching
  no-data pixels; day and night LST above the valid minimum in the same pixel. `frac_pixeles_validos` reports the valid fraction.
- **Landsat / HLS:** QA_PIXEL (Landsat) or Fmask (HLS) removes fill, cloud, dilated cloud, cirrus, shadow,
  snow and water; reflectance outside the valid range is dropped.
- **ECOSTRESS:** QC bits best or nominal, cloud = 0, values within physical ranges; at least 10 valid
  agricultural pixels per pass.
- **SMAP:** cells outside 0–0.60 m³/m³ excluded before averaging; months with any missing day are left empty.
- **NASS:** "OTHER (COMBINED) COUNTIES" rows (county code 998) are dropped; yield trend is not removed.
- **Lotes:** per-field checks of pixel counts, crop purity per year, CSB–CDL agreement, NASADEM vs 3DEP
  relief, clear-observation counts, Landsat–Sentinel-2 NDVI consistency and SSURGO coverage (tables in
  `lotes.md`).

### 5.3 Validation of NASA precipitation and temperature against ground data

From `validacion.md` (monthly, county level, IA/IL/IN; bias = NASA source − ground reference):

| Comparison | Unit | n (county-months) | Mean bias | RMSE | Pearson r |
|---|---|---|---|---|---|
| Rain POWER vs PRISM | mm/month | 91,416 | −3.54 | 18.65 | 0.944 |
| Rain IMERG vs PRISM | mm/month | 91,416 | 5.62 | 20.81 | 0.932 |
| Rain POWER vs CoCoRaHS | mm/month | 42,798 | −1.50 | 24.02 | 0.907 |
| Rain IMERG vs CoCoRaHS | mm/month | 42,798 | 7.63 | 27.08 | 0.890 |
| Tmax POWER vs PRISM | °C | 91,416 | −0.07 | 0.96 | 0.996 |
| Tmin POWER vs PRISM | °C | 91,416 | 0.41 | 0.93 | 0.996 |
| Tmean POWER vs PRISM | °C | 91,416 | 0.06 | 0.74 | 0.998 |

### 5.4 Reproducibility

- `data/raw/` is never modified; transformations go to `data/interim/` and `data/processed/`.
- Download scripts are idempotent and resumable; each downloaded file gets a row in `manifest.csv`
  (package, file, source, product, version, download date, query or URL, without API keys).
- Every assumption and known problem is written in the data card of its package.

---

## 6. Known limitations (summary)

- **IMERG** comes through the POWER API (no Earthdata access for GES DISC at the time); from 2025-10-01 the
  values are the Late Run, not the Final Run.
- **SMAP L4** comes from Crop-CASMA daily layers, not the 3-hourly `SPL4SMGP` granules; it is not confirmed
  whether the layer is a daily mean or the 01:30 UTC field. One day (2016-12-15) is missing.
- **MODIS** is read from reduced-resolution overviews (~927 m for MOD13Q1, ~2 km for MOD11A2), so the quality
  filter is approximate; mid-2025 composites are missing at the source.
- **ET/PET** come from NLDAS-2 Noah instead of MOD16A2; `et_mm` and `et_nldas_mm` are the same variable.
- **Soil** is the tabular SSURGO weighted by map-unit area, without the agricultural mask (includes forest,
  urban and water). NASADEM noise may inflate slope in flat areas.
- **POWER** is a point value at the county centroid on a coarse grid: neighbouring counties may share identical
  series.
- **ECOSTRESS** and **Landsat** (`teledeteccion`) use sample windows per county and are still partial.
- **CDL 2024–2025** are 10 m products resampled to 30 m by nearest neighbour.
- **Irrigation:** NASS `ALL PRODUCTION PRACTICES` yields mix irrigated and rainfed fields (relevant in NE and KS).

---

## Glossary of Spanish column terms

| Spanish | English | Spanish | English |
|---|---|---|---|
| `anio`, `mes`, `fecha` | year, month, date | `maiz`, `soja`, `trigo`, `avena`, `heno` | corn, soybean, wheat, oats, hay |
| `prec` | precipitation | `barbecho` | fallow |
| `tmax`, `tmin`, `tmed` | max, min, mean temperature | `rend` | yield |
| `rad` | solar radiation | `sup_sembrada`, `sup_cosechada` | planted area, harvested area |
| `viento`, `hr` | wind, relative humidity | `produccion` | production |
| `dias` | days | `rotacion`, `tras` | rotation, after (e.g. corn after soybean) |
| `helada` | frost | `cobertura`, `labranza_cero`, `riego` | cover crop, no-till, irrigation |
| `lluvia`, `racha_seca` | rain, dry spell | `drenaje` | drainage |
| `temporada`, `invierno_previo` | growing season, previous winter | `suelo`, `terreno` | soil, terrain |
| `tend`, `decada` | trend, decade | `arcilla`, `arena`, `limo` | clay, sand, silt |
| `anom` | anomaly | `materia_organica` | organic matter |
| `inicio`, `pico`, `fin` | start, peak, end | `napa` | water table |
| `pendiente`, `elevacion` | slope, elevation | `prof_raices` | rooting depth |
| `escorrentia` | runoff | `lote`, `px` | field, pixel |
| `precio`, `costo`, `margen` | price, cost, margin | `estatico` | static |
