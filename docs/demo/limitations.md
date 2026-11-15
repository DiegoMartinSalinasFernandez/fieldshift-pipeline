# Field Shift — Limitations and known issues

NASA Space Apps Challenge 2026, challenge "Field Shift: Adapting Farms with NASA Data".

This page lists the limitations we know about in the Field Shift data pipeline. Judges score
**Validity** ("scientifically sound and technically feasible"), so we state them openly. Each line names the
package, the file it affects and the repository document it comes from. We did not estimate anything new for this
page: every number is copied from a data card (`docs/datasets/<package>.md`), a research note
(`docs/research/*.md`) or the list of pending decisions (`coordinacion/para_decidir.md`). Items the team still
has to fill in are marked **[TBD]**.

Status: 2026-11-15. Column names are in Spanish (`rend_bu_ac` = yield in bu/ac). The glossary is at the end of
`docs/datasets/README_en.md`.

---

## 0. Scope of the numbers on this page

| # | Limitation | Package · file | Source |
|---|---|---|---|
| 0.1 | The data cards were written for the first batch of states (Iowa, Illinois and Indiana, 293 counties). Unless a line says otherwise, coverage, missing-value percentages and validation statistics refer to those three states. | all · `docs/datasets/*.md` | data cards (e.g. `clima.md`, header) |
| 0.2 | On 2026-11-15 the only published data release is `datos-oh-ne-mn` (Ohio, Nebraska, Minnesota; 268 counties, 2000–2025; [`coverage.md`](coverage.md)). Iowa, Illinois, Indiana and Kansas have no published release yet. Which of the 7 states (666 counties) are in the final delivery: **[TBD]**. | all · per-state releases | `coordinacion/tareas/T003-*.md`, `T013-*.md` |
| 0.3 | The seven states have not been merged into one table yet (task T008 is open). | `merge` · `tabla_anual.csv`, `tabla_mensual.csv` | `coordinacion/tareas/T008-*.md` |
| 0.4 | This repository only prepares data. No model is trained here, so this page says nothing about model accuracy: **[TBD]** by the ML team. | — | `CLAUDE.md` |

## 1. Missing data and gaps

| # | Limitation | Package · file | Source |
|---|---|---|---|
| 1.1 | NASS does not publish every county every year. Hidden values (`(D)`, `(Z)`, `(NA)`) are left empty, with the original code kept in `flag_nass`. In the first batch, 24.2 % of `rend_bu_ac` cells are empty. | `cultivos` · `produccion_anual.csv` | `cultivos.md` (Supuestos; column table) |
| 1.2 | At county level NASS rarely writes `(D)`: it drops the confidential county and adds its area to an "OTHER (COMBINED) COUNTIES" row (`county_code` 998), which we exclude because it is not a county. That row holds up to 51 % of the state's planted corn area (Kansas 2025). | `cultivos` · `produccion_anual.csv` | `docs/research/nass_2024_2025.md` |
| 1.3 | County coverage drops in recent years. Corn yield is reported for 92 % of the 666 counties in 2020, 68 % in 2024 and 65 % in 2025; soybean for 87 %, 63 % and 61 %. In 2025 Nebraska and Kansas have corn yields for 49 % and 50 % of counties (soybean: 39 % and 46 %). | `cultivos` · `produccion_anual.csv` | `docs/research/nass_2024_2025.md` |
| 1.4 | Winter wheat and oats in 2024 exist only for Illinois (oats: 8 counties). There is no county winter wheat estimate for Iowa or Minnesota in any year. | `cultivos` · `produccion_anual.csv` | `docs/research/nass_2024_2025.md` |
| 1.5 | The file only has the rows NASS publishes, not the full `fips × anio × cultivo` grid. A full grid with empty cells is a pending proposal. | `cultivos` · `produccion_anual.csv` | `para_decidir.md` #7 |
| 1.6 | NASS stopped many county oat and hay surveys, so those series have large gaps. | `cultivos` · `produccion_anual.csv` | `cultivos.md` (Problemas conocidos) |
| 1.7 | Alfalfa and hay are measured in tons, not bushels: `produccion_bu`, `rend_bu_ac` and `rend_kgha` are empty for them. NASS does not publish planted area of hay. | `cultivos` · `produccion_anual.csv` | `cultivos.md` (Supuestos) |
| 1.8 | The 2012 Census file has no cover crop, no-till or tile drainage data by county, so those columns are empty for 2012. | `cultivos` · `practicas_censo.csv` | `cultivos.md` (Problemas conocidos) |
| 1.9 | SMAP L4 starts on 2015-03-31, so soil-moisture columns are empty before 2015-04. March 2015 is left out. | `agua` · `agua_diario.csv`, `agua_mensual.csv`; `merge` · `tabla_mensual.csv` | `agua.md`, `merge.md` |
| 1.10 | SMAP is missing on 2016-12-15 (the Crop-CASMA service returns "bad request"). Monthly values need every day, so December 2016 is empty. | `agua` · `agua_diario.csv`, `agua_mensual.csv` | `agua.md` (Problemas conocidos) |
| 1.11 | SMAP cells above 0.60 m³/m³ (up to ~0.92) are removed before averaging. This affects ~1.5 % of daily rows, mostly organic soils in northeastern Indiana and DuPage County (IL). | `agua` · `agua_diario.csv` | `agua.md` |
| 1.12 | GRACE-DA-DM starts in 2003-01: 2002 was dropped to stay under the 5 GB raw-data limit. | `agua` · `agua_semanal.csv` | `agua.md` (Supuestos) |
| 1.13 | Some MODIS composites from mid-2025 are missing at the source (Planetary Computer): MOD13Q1 between A2025193 and A2025305, and MOD11A2 between A2025185 and A2025321 (checked 2026-11-14). | `vegetacion` · `vegetacion_16d.csv`, `vegetacion_mensual.csv` | `vegetacion.md` |
| 1.14 | In winter, snow and clouds leave months with no valid MODIS pixels, so `ndvi` and `lst_*` are empty. | `vegetacion` · `vegetacion_mensual.csv` | `vegetacion.md` |
| 1.15 | `ndvi_maiz` and `ndvi_soja` are empty in counties with small or mixed fields (no ~927 m pixel that is at least 75 % one crop). | `vegetacion` · `vegetacion_16d.csv`, `fenologia_anual.csv` | `vegetacion.md` |
| 1.16 | ECOSTRESS covers only April–October and was downloaded starting with the most recent months. For the demo it covers 2025-04 to 2025-10. Final coverage: **[TBD]**. | `ecostress` · `ecostress_mensual.csv` | `ecostress.md`; `docs/research/space_apps_criterios.md` §6 |
| 1.17 | The Landsat 30 m package is partial: recent years were downloaded first, so earlier years may have no rows. Years with one scene per period use that scene's value. | `teledeteccion` · `teledeteccion_anual.csv` | `teledeteccion.md` |
| 1.18 | Annual NLCD ends in 2024, so 2025 has no rows. | `paisaje` · `paisaje_anual.csv` | `paisaje.md` |
| 1.19 | Crop rotation from the CDL starts in 2008 (first year of national CDL coverage), so rotation columns are empty for 2000–2007. | `cultivos` · `rotacion_anual.csv`; `merge` · `tabla_anual.csv` | `merge.md` |
| 1.20 | Crop Progress has no reports from October to early November 2025 because of the government shutdown, the same weeks as the corn and soybean harvest. `fenologia_estado.csv` only has corn and soybean. | `cultivos` · `fenologia_estado.csv` | `para_decidir.md` #8; `merge.md` |
| 1.21 | ERS oat costs start in 2005 (2000–2004 empty). NASS stopped publishing the winter wheat price for Iowa after 2019 and the oat price for Indiana after 2015. ERS has no cost data for alfalfa or hay. | `economia` · `economia_anual.csv`, `economia_forrajes_anual.csv` | `economia.md` |
| 1.22 | PRISM monthly values for 2025 may still be provisional. CoCoRaHS starts in 2008 and only counts stations with at least 25 reports in the month. | `validacion` · `validacion_mensual.csv` | `validacion.md` |

## 2. Substituted sources and reduced resolution

Several products were accessed through other routes because Earthdata Login was not available when the first
batch was built.

| # | Limitation | Package · file | Source |
|---|---|---|---|
| 2.1 | GPM IMERG comes from the NASA POWER API (`IMERG_PRECTOT`), not from `GPM_3IMERGDF` on GES DISC. The API does not say which IMERG run each date comes from. | `clima` · `clima_diario.csv`, `clima_mensual.csv` | `clima.md` |
| 2.2 | **IMERG Late Run at the end of 2025.** The Final Run V07 ends on 2025-09-30, so from 2025-10-01 to 2025-12-31 `prec_imerg_mm` is Late Run data (climatological gauge adjustment, not the monthly GPCC one). These values will change when the data is downloaded again after the Final Run covers 2025. No column records the run. | `clima` · `clima_diario.csv`, `clima_mensual.csv`, `clima_anual.csv` | `clima.md` (Problemas conocidos) |
| 2.3 | IMERG days are UTC, while the other POWER variables use local solar days. `prec_imerg_mm` and `prec_power_mm` for the same date cover windows about 6 h apart. | `clima` · `clima_diario.csv` | `clima.md` |
| 2.4 | SMAP L4 comes from the daily 9 km layers of USDA Crop-CASMA, not from the 3-hourly `SPL4SMGP` granules. We have not confirmed whether the layer is a daily mean or the 01:30 UTC field. | `agua` · `agua_diario.csv`; `lotes` | `agua.md`, `lotes.md` |
| 2.5 | GRACE-DA-DM is the US-only 0.125° version from nasagrace.unl.edu, not the global 0.25° product from GES DISC. Averaging percentiles across cells gives an index, not a true percentile. The model's reference period has not been verified. | `agua` · `agua_semanal.csv` | `agua.md` |
| 2.6 | **MODIS at reduced resolution.** To fit the 5 GB limit, MOD13Q1 is read from overview 1 (~927 m instead of 250 m) and MOD11A2 from overview 0 (~2 km instead of 1 km). The overviews are resampled, so the pixel-quality filter is only approximate. | `vegetacion` · `vegetacion_16d.csv`, `vegetacion_mensual.csv`, `fenologia_anual.csv` | `vegetacion.md` |
| 2.7 | The 75 % crop-purity threshold for `ndvi_maiz` and `ndvi_soja` was planned for 250 m pixels but is applied to ~927 m pixels. | `vegetacion` · `vegetacion_16d.csv` | `vegetacion.md` |
| 2.8 | ET and PET come from NLDAS-2 Noah (a land-surface model), not from MOD16A2 (satellite). Noah PET is usually higher than MOD16 PET, so `et_pet_ratio` is lower. `et_mm` (vegetacion) and `et_nldas_mm` (nldas) are the same variable: do not use both as features. | `vegetacion` · `vegetacion_mensual.csv`; `nldas` · `nldas_mensual.csv` | `vegetacion.md`, `nldas.md`, `docs/research/merge_faltantes.md` |
| 2.9 | MCD12Q1 was not downloaded (the CDL mask replaces it). | `vegetacion` | `vegetacion.md` |
| 2.10 | Soil uses tabular SSURGO through Soil Data Access, not the 10 m gSSURGO raster and `Valu1` table. NCCPI comes from `cointerp` and SOC is computed from `chorizon`. | `suelo_terreno` · `suelo_terreno_estatico.csv` | `suelo_terreno.md` |
| 2.11 | The county-level Landsat package uses Landsat C2 L2 only (no HLS, no Sentinel-2) and samples 2 windows per county (~2.9 km²), not the whole county. | `teledeteccion` · `teledeteccion_anual.csv` | `teledeteccion.md` |
| 2.12 | ECOSTRESS uses one 32 × 32 pixel window (2.24 km wide) per county, centered on cropland. It is a local sample, not a county mean. Monthly LST mixes passes at different times of day. | `ecostress` · `ecostress_mensual.csv` | `ecostress.md` |
| 2.13 | Crop sequences use 8-year windows computed pixel by pixel from the CDL, not the Crop Sequence Boundaries (the national CSB zips total 44 GB and need approval). | `cultivos` · `rotacion_secuencia.csv` | `cultivos.md`; `para_decidir.md` #26 |
| 2.14 | The agricultural mask comes from the official CDL 2025 Cultivated Layer (cropland in 2021–2025), not from "crop in any year 2008–2025" as planned. The yearly national CDL files did not fit the 5 GB limit. | `cultivos` · `data/reference/mascara_agricola.tif` | `cultivos.md` |
| 2.15 | NASA POWER is sampled at the county centroid on a 0.5° × 0.625° grid. Neighbouring counties in the same cell have identical series. | `clima` · all files | `clima.md` |
| 2.16 | NASA POWER solar radiation (CERES) starts in 1984, so there is no ETo before 1984. Other weather variables start in 1981. | `clima` · `clima_diario.csv` | `clima.md` |

## 3. Known biases and data quality

| # | Limitation | Package · file | Source |
|---|---|---|---|
| 3.1 | **CDL 2024–2025 bias.** These years were published at 10 m and resampled to 30 m by nearest neighbour (1 of every 9 pixels). Their field edges do not match the 30 m series. With the old definition, the median share of corn that followed corn or soybean fell from 96.9 % (2023) to 91.3 % (2024). With the corrected denominator it is 98.0 %, as in 2015–2023 (97.3–98.5 %). Crop-area shares (`pct_maiz`, `pct_soja`, …) and the 2024–2025 crop masks are not corrected. | `cultivos` · `rotacion_anual.csv`, `mascara_maiz_<anio>.tif`, `mascara_soja_<anio>.tif` | `cultivos.md` (Supuestos; Problemas conocidos) |
| 3.2 | 2020 stays lower with both definitions: 94.4 % of corn followed corn or soybean. | `cultivos` · `rotacion_anual.csv` | `cultivos.md` |
| 3.3 | CDL accuracy differs by crop, state and year. Corn and soybean accuracy is 85.8–99.1 %. Kansas soybean is below 90 % in 11 of 18 years, and Ohio corn is below 90 % in 2017–2020. Oats and other hay are often 10–50 % (producer accuracy). Winter wheat is poor in Iowa and Minnesota. The validation method changed in 2017 and again in 2024, so accuracies from different periods are not comparable. | `cultivos` · `rotacion_anual.csv`, `rotacion_secuencia.csv` | `docs/research/cdl_precision.md`, `cdl_precision.csv` |
| 3.4 | Satellite rainfall compared with the ground (first batch, county-months). IMERG vs PRISM: bias +5.62 mm/month, RMSE 20.81, r 0.932. POWER vs PRISM: −3.54, 18.65, r 0.944. IMERG vs CoCoRaHS: +7.63, 27.08, r 0.890. POWER temperature vs PRISM: r ≥ 0.996. The differences include point-vs-area representativeness. | `validacion` · `validacion_mensual.csv`; `clima` | `validacion.md` (validation table) |
| 3.5 | CoCoRaHS monthly totals underestimate rainfall at stations with 25–30 reports, because missing days are not filled. | `validacion` · `validacion_mensual.csv` | `validacion.md` |
| 3.6 | `dias_sm_saturado` uses a fixed, provisional threshold of 0.40 m³/m³. It counts more days in high-porosity soils than in sandy soils. | `agua` · `agua_mensual.csv` | `agua.md` |
| 3.7 | NASADEM noise can inflate slope on flat land, so `pendiente_gt2_pct` probably overestimates the sloped area. In one Champaign control field, relief is 4.0 m with NASADEM and 1.6 m with USGS 3DEP. | `suelo_terreno` · `suelo_terreno_estatico.csv`; `lotes` | `suelo_terreno.md`, `lotes.md` |
| 3.8 | TWI underestimates the contributing area near DEM tile edges, where large rivers cross tiles. | `suelo_terreno` · `suelo_terreno_estatico.csv` | `suelo_terreno.md` |
| 3.9 | `twi_decil_sup_pct` uses the 90th percentile of the states each machine processed, so the column is not comparable across states until a common threshold is chosen. | `suelo_terreno` · `suelo_terreno_estatico.csv` | `para_decidir.md` #3 |
| 3.10 | Soil, terrain, county NDVI/EVI, SMAP, GRACE, NLDAS and NLCD values are averages over the whole county, not only cropland: they include forest, urban land and water. | `suelo_terreno`, `vegetacion`, `agua`, `nldas`, `paisaje` | data cards (Supuestos) |
| 3.11 | NLDAS-2 Noah does not simulate irrigation or tile drainage. In heavily drained or irrigated counties, modeled soil moisture and runoff may differ from reality. | `nldas` · `nldas_mensual.csv`; `vegetacion` (`et_mm`) | `nldas.md` |
| 3.12 | FAO-56 crop coefficients overestimate the ET measured in the region. Whether to correct the Kc values for corn and soybean is still open. | `config/cultivos.csv` | `para_decidir.md` #12; `docs/research/agua_por_cultivo.md` |
| 3.13 | SPI is fitted on the full 1981–2025 POWER record, including years after the row (standard SPI convention). The ML team should consider this when building forecasting features. | `clima` · `clima_mensual.csv` | `clima.md` |
| 3.14 | `validar_csv()` flags one real `deficit_mm` value of −99.99 mm (FIPS 18065, 2011-07) as a fill code. It is a false positive and the value was kept. | `clima` · `clima_mensual.csv` | `clima.md` |
| 3.15 | `lst_noche_c <= lst_dia_c` fails in < 0.1 % of rows. A few NLDAS values are out of range (ET/PET down to −0.5 mm, PET > 500 mm in July 2012). Both are kept as delivered by the source. | `vegetacion` · `vegetacion_mensual.csv` | `vegetacion.md` |
| 3.16 | County boundaries come from the generalized 1:500k Census file (2024 vintage). They are not exact at 30 m. | `base` · `data/reference/condados.gpkg` | `base.md` |

## 4. Irrigation in Nebraska and Kansas

| # | Limitation | Package · file | Source |
|---|---|---|---|
| 4.1 | The yields we deliver are NASS `ALL PRODUCTION PRACTICES`, which mixes irrigated and rainfed fields. Median irrigated-minus-rainfed corn yield gap (2008–2018 sample): 103 bu/ac in Kansas and 81 bu/ac in Nebraska. Soybean: 26 and 17. Winter wheat: 14 and 24. Comparing NE and KS yields with Iowa without separating them mixes two production systems. | `cultivos` · `produccion_anual.csv` | `docs/research/riego_nass.md`; `para_decidir.md` #1 |
| 4.2 | NASS published county yields by irrigation practice only through 2018 (winter wheat through the 2019 harvest). After that, only the Census gives irrigated area by crop, without yield (7–28 % `(D)`). | `cultivos` · `produccion_anual.csv`, `practicas_censo.csv` | `docs/research/riego_nass.md`; `para_decidir.md` #2 |
| 4.3 | There is no irrigation mask yet. LANID (2000–2020) is proposed but not downloaded, and no open annual product covers 2021–2025. `ndvi_secano` (rainfed NDVI) cannot be computed. | `cultivos`, `vegetacion` | `docs/research/riego_ne_ks.md`, `riego_mascaras.md`; `para_decidir.md` #9, #28 |
| 4.4 | ERS costs are regional and do not separate irrigated from rainfed production in Nebraska. | `economia` · `economia_anual.csv` | `economia.md` |

## 5. Not merged or not included yet

| # | Limitation | Package · file | Source |
|---|---|---|---|
| 5.1 | `merge.py` joins 6 annual or static files and 3 monthly files. Not merged yet: `economia_anual`, `economia_forrajes_anual`, `paisaje_anual`, `teledeteccion_anual`, and the monthly `validacion`, `ecostress` and `nldas` files. | `merge` · `tabla_anual.csv`, `tabla_mensual.csv` | `docs/research/merge_faltantes.md`; `para_decidir.md` #27 |
| 5.2 | Name collision: `flag_nass` appears in production and in both economics files. The current renaming would produce `economia_flag_nass_x` and `economia_flag_nass_y`. | `merge` · `tabla_anual.csv` | `docs/research/merge_faltantes.md` |
| 5.3 | `tabla_anual.csv` is a left join on `produccion_anual.csv`, so county-years without NASS production rows drop out. Weather, rotation, phenology and soil values repeat on every crop row of the same county and year. | `merge` · `tabla_anual.csv` | `merge.md` |
| 5.4 | `rotacion_secuencia.csv` (8-year windows) and `practicas_censo.csv` (Census years) are kept apart because they have a different time grain. How to join them is still open. | `merge` | `merge.md`; `para_decidir.md` #27 |
| 5.5 | Not included, pending a team decision: grain sorghum in Kansas (rotation class only), crop-insurance causes of loss (USDA RMA), prevented planting (FSA/RMA), tile drainage per pixel (SEETileDrain), state-specific critical windows (silking, soybean pod fill), and AmeriFlux ET validation. | — | `para_decidir.md` #5, #6, #11, #17, #18, #23 |
| 5.6 | Annual windows are fixed for all states (July = corn flowering, August = soybean filling), not crop windows per state. | `clima` · `clima_anual.csv` | `CLAUDE.md` §4; `para_decidir.md` #23 |
| 5.7 | Yield detrending is left to the ML team on purpose, to avoid leaking information from the future. | `cultivos` · `produccion_anual.csv` | `CLAUDE.md` §6.2 |

## 6. Field-level package (`lotes`)

| # | Limitation | Package · file | Source |
|---|---|---|---|
| 6.1 | The Landsat and HLS download is partial: the clearest scene of each field-year came first. Observation counts and bare-soil composites will grow as more scenes are downloaded. | `lotes` · `vegetacion_px_*.csv` | `lotes.md` |
| 6.2 | HLS S30 on Planetary Computer starts in 2020 for these fields. 2015–2019 comes from LP DAAC and is partial. | `lotes` | `lotes.md` |
| 6.3 | USGS 3DEP was requested at 10 m, not 1 m lidar, so sub-meter detail is lost. | `lotes` | `lotes.md` |
| 6.4 | Tile drainage (AgTile-US) is a modeled map, not a field observation. It is a hint, not ground truth. | `lotes` | `lotes.md` |
| 6.5 | There are 10 demonstration fields, chosen by a rule plus manual choices (Tippecanoe County, IN; compactness threshold 0.6). They show the method and are not a statistical sample of the Corn Belt. | `lotes` · `lotes.csv` | `lotes.md` (Supuestos) |

---

## For the team: to fill in before submission

- **[TBD]** Final list of states and counties in the delivered release (see 0.2).
- **[TBD]** Final ECOSTRESS and `teledeteccion` coverage, in years and counties.
- **[TBD]** Missing-value percentages for the seven-state merged tables, after T008.
- **[TBD]** Model performance and uncertainty (ML team).
