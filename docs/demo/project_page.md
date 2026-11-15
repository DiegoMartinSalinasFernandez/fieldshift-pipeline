# Field Shift — project page draft (Space Apps 2026 submission form)

Draft text for every field of the project page. The field list comes from the Project Submission Guide 2026, as
summarized in `docs/research/space_apps_criterios.md` §2. Challenge: **"Field Shift: Adapting Farms with NASA
Data"**.

Rules for whoever pastes this into the form:

- **Deadline:** Sunday **2026-11-15, 23:59 local event time**. You can edit and resubmit until then, and judges see
  the last version (`space_apps_criterios.md` §2).
- **Everything in English.** All links must be **public, with no login**. Test them in a private window.
- **No invented numbers.** Each figure has a `[src: ...]` note with the repo file it comes from. Delete those notes
  before pasting, but keep the numbers exactly as written. Anything we do not have yet is marked **[TBD]**.
- **Coverage caveat.** Most data cards and the validation table describe the **first batch: Iowa, Illinois and
  Indiana, 293 counties** (`docs/datasets/base.md`, `clima.md`, `validacion.md`). The 7-state, 666-county scope
  comes from `CLAUDE.md` §2 and `docs/datasets/README_en.md` §1. Before claiming 666 counties as delivered,
  check that the releases for OH, NE, MN and KS are published: `docs/demo/coverage.md` lists the published
  releases with counted numbers. **[TBD: confirm]**
- **Model results.** This repo builds the data only and trains no models (`CLAUDE.md`). Any claim about model
  accuracy or recommended rotations has to come from the ML or frontend team. **[TBD]**
- Field order follows the form. The demo text itself is in `docs/demo/slides.md` (task T056).

---

## 1. Project Name

**[TBD: final name]**. Working title: *Field Shift: Rotations Read from Space*. This is the same working title as
`docs/demo/slides.md`, slide 1.

Team: **[TBD: team name]**. Members (6 at most, all registered in the same local event and listed in the Members
tab): **[TBD]**. Local event: **[TBD]**.

---

## 2. High-Level Project Summary

*(Form prompt: "What did you develop? How does it address the challenge? Why is it important?")*

> Field Shift helps U.S. Corn Belt farmers compare crop-rotation strategies with evidence, so the choice does
> not rest on habit alone. Most cropland in the region runs a corn–soybean rotation. Large studies of farm fields
> show that continuous corn and continuous soybean yield less, and that the loss is larger in dry and low-yield
> years. We built an open, reproducible data pipeline that brings together 26 years (2000–2025) of NASA Earth
> observations, which are the core of the tool: weather and rainfall (NASA POWER, GPM IMERG), soil moisture (SMAP,
> NLDAS-2, GRACE-DA-DM), vegetation and canopy temperature (MODIS, ECOSTRESS, HLS and Landsat) and terrain
> (NASADEM). The pipeline combines them, county by county, with the crops actually grown on every 30 m pixel
> (USDA Cropland Data Layer), county yields, soil surveys (SSURGO) and economics. On top of these tables, the
> tool compares at least three rotations, starting with the farmer's current one. For each rotation it shows
> the evidence, the expected benefits, the risks, the uncertainty and the data gaps. It goes down to individual
> fields, where satellite and terrain data separate dry knolls from wet depressions. The tool supports farmers'
> decisions and local expertise; it does not replace them.

Sources for the numbers: period and states `CLAUDE.md` §2; rotation penalty `docs/research/efecto_rotacion.md` §2
(Seifert et al. 2017). **[TBD: add one sentence on what the user sees, for example a web app or a notebook,
once the frontend or ML team confirms it.]**

---

## 3. Link to Project Demo

**[TBD: public link]** to either a **video of 30 seconds or less** or **up to 7 slides** (title and intro
included), hosted outside the Space Apps site (YouTube, Google Slides, etc.). Going over either limit removes the
project from Global Judging (`space_apps_criterios.md` §2). The draft is in `docs/demo/slides.md`.

---

## 4. Link to Final Project

- **Code:** **[TBD: public GitHub repository URL]**. The repo is public (`CLAUDE.md` §1, rule 8).
- **Data:** processed CSVs are published as GitHub Releases, one per group of states (`datos-<states>`, made by
  `scripts/entregar.py`), plus a separate field-level release (`fieldshift_lotes_v1`, `CLAUDE.md` §6.6).
  What is published today, with states, counties, years and rows counted from the zips:
  `docs/demo/coverage.md` (refresh with `docs/demo/coverage.py`). **[TBD: release URLs]**
- **English documentation for judges:** `docs/datasets/README_en.md` (data summary, sources, quality control,
  limitations). **[TBD: link]**
- **Tool / frontend:** **[TBD: link, if there is one]**.

---

## 5. Detailed Project Description

### What it does

Field Shift is a decision-support tool for crop rotations in the U.S. Corn Belt. The study area is every county
of Iowa, Illinois, Indiana, Ohio, Nebraska, Minnesota and Kansas, 666 counties in total, for 2000–2025
`[src: CLAUDE.md §2]`. For a given county or field, the tool compares at least three rotation strategies,
including the current one, as the challenge asks. These are the corn–soybean rotation, continuous corn and
rotations that add a small grain or alfalfa. For each strategy it reports:

- why it was suggested and what evidence supports it;
- the benefits it may bring, the risks that need local review, and where information is missing;
- the uncertainty, shown as a range rather than a single number.

### How it works

1. **Data pipeline (this repository).** Python scripts download public data, clean them and write CSV tables
   with one common contract. Every table is keyed by a 5-digit county FIPS code and year, month or date. Missing
   values are empty cells, never 0 or -999. Original U.S. units are kept, and conversions go to separate columns.
   Each package checks keys and physical ranges with `validar_csv()` before delivery, and raw files are never
   modified `[src: docs/datasets/README_en.md §5]`.
2. **County tables.** Each package produces daily, monthly or annual tables: weather (`clima`), crops,
   rotations and practices (`cultivos`), vegetation (`vegetacion`), soil moisture and groundwater (`agua`,
   `nldas`), ECOSTRESS (`ecostress`), Landsat bare soil and winter cover (`teledeteccion`), soil and terrain
   (`suelo_terreno`), land cover (`paisaje`) and prices and costs (`economia`). `src/merge.py` joins them into one
   annual table and one monthly table. For the first batch these have **25,070 rows × 73 columns** and **91,416
   rows × 48 columns** `[src: docs/datasets/merge.md, run of 2026-11-14]`.
3. **The real rotation.** Crop transitions are computed pixel by pixel from the 30 m Cropland Data Layer, as
   corn after soybean, corn after corn, and so on, from 2008 on. The pipeline also builds 8-year sequence classes
   for each county `[src: docs/datasets/cultivos.md]`.
4. **Field level.** For 10 demonstration fields (Crop Sequence Boundaries polygons of 30–120 ha, in counties where less than 5 % of cropland is irrigated),
   the pipeline delivers the data of every 30 m pixel. That includes NASADEM and USGS 3DEP terrain, Landsat and
   HLS clear observations, SSURGO soils, crop history and field weather. With it, the field can be split into
   management zones such as dry knoll, mid-slope and wet depression. The fields are in Iowa (Des Moines Lobe and
   loess hills), Illinois and Indiana `[src: docs/datasets/README_en.md §3.12, docs/datasets/lotes.md]`.
5. **Satellite vs ground.** We checked NASA rainfall and temperature against ground data, as the challenge
   suggests. Monthly rainfall from POWER matched PRISM with Pearson r = 0.944 and from IMERG with r = 0.932.
   Against CoCoRaHS rain gauges, r was 0.907 for POWER and 0.890 for IMERG. POWER temperatures matched PRISM with
   r ≥ 0.996 `[src: docs/datasets/validacion.md, IA/IL/IN, county-months 2000–2025]`.
6. **Model and interface.** A separate machine-learning team trains the yield and rotation models on these
   tables. To avoid leaking future information, trends and normalization are computed inside each training
   fold. **[TBD: describe the model, its validation and the user interface, with their own numbers.]**

### Benefits

- Compares rotations with what farmers actually grow, read from 30 m crop maps, not with an assumed rotation.
- Puts NASA observations of water stress, heat, vegetation and terrain at the center of the comparison.
- Works at two scales: the county for the regional picture, the field for management zones.
- Open and reproducible: public data, public code and a data card for every package that lists sources,
  coverage, missing data, assumptions and known problems.

### Goals

**[TBD by the team: short- and long-term goals, e.g. more states, farmer-entered priorities, field-level
vulnerability maps.]**

### Tools, languages and hardware

- **Language:** Python 3.11.
- **Libraries:** pandas, numpy, geopandas, rasterio, rasterstats, xarray, scipy, pyproj, pysheds, h5py,
  h5netcdf, requests, pyyaml, xlrd and pytest for the tests `[src: requirements.txt]`.
- **Data access:** NASA POWER API, NASA Earthdata (GES DISC via Harmony, LP DAAC, CMR-STAC), Microsoft Planetary
  Computer (MODIS, NASADEM, Landsat and HLS), USDA NASS Quick Stats, Crop-CASMA, USDA NRCS Soil Data Access
  `[src: docs/datasets/README_en.md §2]`.
- **Coordination:** several computers working on one public GitHub repository through a task board
  (`coordinacion/`) and GitHub Releases for the data.
- **AI:** Claude agents (Anthropic). See section 6.
- **Frontend / ML stack:** **[TBD]**.

---

## 6. Use of Super Intelligence (SI)

> We used AI extensively, and we want to be clear about where. **Much of the data pipeline was written by
> Claude agents (Anthropic), coordinated by our team.** Several computers each ran a Claude agent. They took tasks
> from a shared task board in the repository, wrote code on separate branches and submitted it as pull requests.
> Team members set the tasks and the rules, approved changes to the shared code and configuration, and made the
> decisions: states, period, schemas and downloads over 5 GB. Specifically:
>
> - **Code:** most download and processing scripts (`src/`), the merge script, the tests and the coordination
>   scripts were written by Claude agents and reviewed through the task board and pull requests.
> - **Documentation:** the data cards (`docs/datasets/`), the research notes (`docs/research/`) and this page's
>   draft were written by Claude agents. Where research notes quote sources, they link them.
> - **Data:** **the AI generated none of the data values.** Every number in our CSV tables is downloaded from the
>   original public sources (NASA, USDA, USGS, PRISM, CoCoRaHS) or computed from them by scripts that anyone can
>   re-run. The agents worked under explicit rules: never invent or fill in data, never modify raw downloads, and
>   record every assumption in the data card.
> - **The idea:** the concept of the tool and how it answers the challenge came from our team, not from the AI.
> - **Images and video:** **[TBD: state whether any image, voice or video in the demo is AI-generated. If so, it
>   carries a visible "AI-generated" watermark.]** No AI was used to create or modify NASA logos or brand
>   elements.
>
> This statement is repeated in the repository README and in the metadata of the published data releases.
> **[TBD: make sure that is true before submitting]**

Rules behind this text are in `space_apps_criterios.md` §4: code and data generated with SI "must acknowledge SI
generation in descriptive text and metadata", images and video need a visible watermark, and SI must not be used
to come up with the idea.

---

## 7. NASA Data

*(Form prompt: "Provide specific details about what NASA data and resources you used.")*

The list below has only the products that actually appear in our processed CSVs, each with its version, its DOI
and what it gives us. Sources: `docs/research/citas_nasa.md` §1 and the data cards in `docs/datasets/`. The
county coverage dates are those of the data cards (first batch, IA/IL/IN).

| # | NASA product | Version | DOI | What we use it for (package: columns) | Coverage in our CSVs |
|---|---|---|---|---|---|
| 1 | **NASA POWER** (Prediction Of Worldwide Energy Resources), AG community, daily point API | Daily 2.x **[TBD: exact version]** | no DOI (acknowledgement below) | `clima`: temperature, precipitation, humidity, wind, radiation, soil wetness, plus FAO-56 ETo, GDD, frost dates, SPI and anomalies; `lotes`: field-centroid weather | 2000–2025 (1981 on, as the SPI and anomaly baseline) |
| 2 | **GPM IMERG Final** Precipitation L3 1 day 0.1° (`GPM_3IMERGDF`), through POWER | V07 | [10.5067/GPM/IMERGDF/DAY/07](https://doi.org/10.5067/GPM/IMERGDF/DAY/07) | `clima`, `lotes`: `prec_imerg_mm` | to 2025-09-30 |
| 3 | **GPM IMERG Late** Precipitation L3 1 day 0.1° (`GPM_3IMERGDL`), through POWER | V07 | [10.5067/GPM/IMERGDL/DAY/07](https://doi.org/10.5067/GPM/IMERGDL/DAY/07) | same column, months not yet covered by the Final Run | 2025-10-01 to 2025-12-31 |
| 4 | **SMAP L4** Global 3-hourly 9 km Surface and Root Zone Soil Moisture (`SPL4SMGP`), daily layers from Crop-CASMA | V8 (cited; Crop-CASMA does not state the version, and V8 is certain from 2025-07-04) | [10.5067/T5RUATAQREF8](https://doi.org/10.5067/T5RUATAQREF8) | `agua`: surface and root-zone soil moisture, anomalies, saturated days; `lotes`: field soil moisture | 2015-03-31 to 2025-12-31 |
| 5 | **GRACE-DA-DM** Groundwater and Soil Moisture Conditions from GRACE and GRACE-FO Data Assimilation L4 7-days 0.125° U.S. (`GRACEDADM_CLSM0125US_7D`) | V4.0 (CMR) | [10.5067/UH653SEZR9VQ](https://doi.org/10.5067/UH653SEZR9VQ) | `agua`: groundwater, root-zone and surface drought percentiles (weekly) | 2003-01-06 to 2025-12-29 |
| 6 | **MODIS/Terra Vegetation Indices** 16-Day L3 Global 250 m (MOD13Q1) | V061 | [10.5067/MODIS/MOD13Q1.061](https://doi.org/10.5067/MODIS/MOD13Q1.061) | `vegetacion`: NDVI, EVI, corn- and soybean-only NDVI, VCI, phenology (green-up, peak, end, number of cycles) | 2000-02 to 2025-12 |
| 7 | **MODIS/Terra Land Surface Temperature/Emissivity** 8-Day L3 Global 1 km (MOD11A2) | V061 | [10.5067/MODIS/MOD11A2.061](https://doi.org/10.5067/MODIS/MOD11A2.061) | `vegetacion`: day and night LST, TCI, VHI | 2000-02 to 2025-12 |
| 8 | **NLDAS-2 Noah** Land Surface Model L4 Monthly 0.125° (`NLDAS_NOAH0125_M`) | V2.0 | [10.5067/WB224IA3PVOJ](https://doi.org/10.5067/WB224IA3PVOJ) | `nldas`: soil moisture 0–10 and 0–100 cm, ET, runoff, snow; `vegetacion`: ET and PET | 2000-01 to 2025-12 |
| 9 | **NASADEM** Merged DEM Global 1 arc second (`NASADEM_HGT`) | V001 | [10.5067/MEASURES/NASADEM/NASADEM_HGT.001](https://doi.org/10.5067/MEASURES/NASADEM/NASADEM_HGT.001) | `suelo_terreno`: elevation, slope, TWI per county; `lotes`: per-pixel terrain (slope, curvature, TPI, TWI, depressions) | static |
| 10 | **ECOSTRESS** Tiled Land Surface Temperature and Emissivity L2 70 m (ECO_L2T_LSTE) | V002 | [10.5067/ECOSTRESS/ECO_L2T_LSTE.002](https://doi.org/10.5067/ECOSTRESS/ECO_L2T_LSTE.002) | `ecostress`: `lst_ecostress_c` | 2025-04 to 2025-10 |
| 11 | **ECOSTRESS** Tiled Evapotranspiration L3 70 m (ECO_L3T_JET) | V002 | [10.5067/ECOSTRESS/ECO_L3T_JET.002](https://doi.org/10.5067/ECOSTRESS/ECO_L3T_JET.002) | `ecostress`: `et_ecostress_mm_dia` | 2025-04 to 2025-10 |
| 12 | **ECOSTRESS** Tiled Evaporative Stress Index PT-JPL L4 70 m (ECO_L4T_ESI) | V002 | [10.5067/ECOSTRESS/ECO_L4T_ESI.002](https://doi.org/10.5067/ECOSTRESS/ECO_L4T_ESI.002) | `ecostress`: `esi_ecostress` | 2025-04 to 2025-10 |
| 13 | **HLS Sentinel-2** MSI Surface Reflectance Daily Global 30 m (HLSS30) | V2.0 | [10.5067/HLS/HLSS30.002](https://doi.org/10.5067/HLS/HLSS30.002) | `lotes`: per-pixel clear observations (reflectance, NDVI, EVI2, GCVI, NDMI) and annual summaries | 2015–2025 (March–November; 2015–2019 from LP DAAC, 2020 on from Planetary Computer) |

Short version for the form, if the table does not paste well:

> NASA POWER daily API (AG community; no DOI) · GPM IMERG Final Daily V07, doi:10.5067/GPM/IMERGDF/DAY/07, and
> Late Daily V07, doi:10.5067/GPM/IMERGDL/DAY/07, both through POWER · SMAP L4 SPL4SMGP V8,
> doi:10.5067/T5RUATAQREF8, through Crop-CASMA · GRACE-DA-DM U.S. V4.0, doi:10.5067/UH653SEZR9VQ · MODIS MOD13Q1
> V061, doi:10.5067/MODIS/MOD13Q1.061 · MODIS MOD11A2 V061, doi:10.5067/MODIS/MOD11A2.061 · NLDAS-2 Noah Monthly
> V2.0, doi:10.5067/WB224IA3PVOJ · NASADEM V001, doi:10.5067/MEASURES/NASADEM/NASADEM_HGT.001 · ECOSTRESS
> ECO_L2T_LSTE, ECO_L3T_JET and ECO_L4T_ESI V002, doi:10.5067/ECOSTRESS/ECO_L2T_LSTE.002, …/ECO_L3T_JET.002,
> …/ECO_L4T_ESI.002 · HLS S30 V2.0, doi:10.5067/HLS/HLSS30.002.

**Required POWER acknowledgement** (POWER has no DOI; text from POWER Referencing, via `citas_nasa.md` §1.1):

> "The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research Center's
> Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science Division."
> "The data was obtained from the POWER Project's Daily 2.x.x version on **[TBD: YYYY/MM/DD]**."

**Landsat Collection 2 Level-2** is a joint USGS–NASA mission distributed and cited by USGS. It is listed under
References (section 8), not here, following `citas_nasa.md` §2. **[TBD: the team may also mention it here as
"USGS/NASA Landsat".]**

**Not in our CSVs, so not listed:** MOD16A2 (replaced by NLDAS-2 Noah ET/PET), MCD12Q1 (the crop mask comes from
the CDL), the global GRACE-DA-DM and HLS L30 (`citas_nasa.md` §1.11 and §1.10).

**Open version questions** (`citas_nasa.md`): Crop-CASMA does not report the SMAP version, so we cite V8, which
is certain from 2025-07-04. The GRACE-DA-DM files carry `030` in the name, but `version=040` inside, and CMR
lists V4.0.

---

## 8. Space Agency Partner Data and Other References

*(The form asks for every data source, resource and tool, including open code, text and images.)*

### Space agency partner data

- **ESA Copernicus Sentinel-2**, through **NASA HLS S30 V2.0** (Sentinel-2 MSI reflectance harmonized by NASA),
  doi:10.5067/HLS/HLSS30.002. Used in `lotes`. **[TBD: add the Copernicus attribution text once task T060
  verifies it (e.g. "contains modified Copernicus Sentinel data [year]").]**
- ERA5 (ECMWF) was not used (`space_apps_criterios.md` §3).

### Other data (non-NASA)

Citations from `docs/research/citas_nasa.md` §2.

- **USGS / EROS, Landsat Collection 2 Level-2**: Landsat 4-5 TM doi:10.5066/P9IAXOVV; Landsat 7 ETM+
  doi:10.5066/P9C7I13B; Landsat 8-9 OLI/TIRS doi:10.5066/P9OGBGM6. Used in `teledeteccion` and `lotes`.
- **USGS 3D Elevation Program (3DEP)**, bare-earth DEM at 10 m. No DOI; cite the U.S. Geological Survey with
  product title and access date. Used in `lotes`.
- **USGS Annual NLCD Collection 1** (ver. 1.2), doi:10.5066/P94UXNTS. Used in `paisaje`.
- **USDA NASS Quick Stats**: survey yields, area, production, prices, Crop Progress and Census of Agriculture
  2012, 2017 and 2022 (https://quickstats.nass.usda.gov). Used in `cultivos`, `economia` and `lotes`.
- **USDA NASS Cropland Data Layer (CDL)**, 30 m (10 m in 2024–2025). Public domain. Used for crop shares,
  transitions and crop masks.
- **USDA NASS Crop Sequence Boundaries (CSB) 2018–2025**. Code: Hunt & Beeson (2024), Zenodo,
  doi:10.5281/zenodo.14004209. Used for the field polygons.
- **USDA ERS, Commodity Costs and Returns.** Used in `economia`.
- **USDA NRCS SSURGO**, through Soil Data Access (https://sdmdataaccess.sc.egov.usda.gov). Used in
  `suelo_terreno` and `lotes`.
- **U.S. Census Bureau, Cartographic Boundary Files 2024, 1:500k** (county boundaries).
- **Crop-CASMA** (USDA NASS and George Mason University CSISS): Zhang et al. (2022), *Int. J. Appl. Earth Obs.
  Geoinf.* 112, 102902, doi:10.1016/j.jag.2022.102902. This is the SMAP L4 service we used.
- **PRISM**, Oregon State University (https://prism.oregonstate.edu): monthly 4 km, for validation only.
- **CoCoRaHS**, Colorado Climate Center (https://www.cocorahs.org), CC BY 4.0: rain gauges, for validation only.
- **AgTile-US**: Valayamkunnath et al. (2020), figshare, doi:10.6084/m9.figshare.11825742. Modeled tile
  drainage in `lotes`.

### Literature

- Seifert, C. A., Roberts, M. J., & Lobell, D. B. (2017). Continuous corn and soybean yield penalties across
  hundreds of thousands of fields. *Agronomy Journal* 109:541–548. It supports the rotation-penalty statement in
  the summary (`docs/research/efecto_rotacion.md`). **[TBD: add any other papers used in the demo or the tool.]**
- FAO Irrigation and Drainage Paper 56 (Allen et al. 1998), the FAO-56 Penman–Monteith method behind
  `eto_pm_mm`.

### Software and tools

- Python 3.11 and the open-source libraries listed in section 5 (`requirements.txt`).
- Microsoft Planetary Computer (STAC access to MODIS, NASADEM, Landsat and HLS) and NASA Earthdata (Harmony,
  CMR-STAC).
- GitHub (code, task board and Releases).
- Claude (Anthropic) agents, which wrote much of the pipeline code and documentation (section 6).
- **[TBD: frontend, ML and video or slide tools, and any open images or icons used in the demo.]**

---

## Checklist before submitting

- [ ] Project name, team and members filled in (section 1).
- [ ] Demo link public, ≤ 30 s video **or** ≤ 7 slides, in English (section 3).
- [ ] Repo, release and tool links public, tested in a private window (section 4).
- [ ] Every `[TBD]` and `[src: ...]` removed or resolved.
- [ ] 666 counties claimed only if the 7-state releases are published.
- [ ] SI statement also in the README and release metadata (section 6).
- [ ] POWER acknowledgement with the access date (section 7).
- [ ] Copernicus attribution checked (section 8, task T060).
- [ ] Both checkboxes ticked: terms and "original work".
