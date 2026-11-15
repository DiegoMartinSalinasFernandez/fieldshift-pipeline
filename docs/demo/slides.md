# Field Shift — demo draft (7 slides + 30 s video script)

Draft for the NASA Space Apps Challenge 2026 submission, challenge **"Field Shift: Adapting Farms with NASA
Data"**. Built from the demo proposal in `docs/research/space_apps_criterios.md` §6 (order: title and team,
problem, (1) rotation map, (2) rotation comparison, (3) a field inside, (4)+(5) stress and satellite vs ground,
sources). Citations come from `docs/research/citas_nasa.md`.

Rules for whoever finishes this draft:

- **Limits:** at most **7 slides** (title and intro count) **or** a video of **30 s or less**. Going over either
  limit removes the project from Global Judging. Everything in English. Public links, no login.
- **Deadline:** Sunday 2026-11-15, 23:59 local event time.
- **No invented numbers.** Every figure below says where it comes from (`[src: ...]`). Anything we do not have
  yet is marked **[TBD]**. The `[src: ...]` notes are for the team: remove them from the final slides, but keep
  the short data credit under each figure.
- **Coverage caveat.** The data cards in this repo (and so the validation numbers below) describe the first batch:
  **Iowa, Illinois and Indiana, 293 counties** (`docs/datasets/clima.md`, `docs/datasets/validacion.md`). The
  7-state, 666-county scope (adding OH, NE, MN, KS) comes from `CLAUDE.md` §2. Before quoting "666 counties" on
  a slide, confirm the 7-state release is published. **[TBD: confirm]**
- **AI disclosure.** Any AI-generated image or voice needs a visible watermark ("AI-generated"). Do not use or
  modify NASA logos with AI; use plain-text credits (`space_apps_criterios.md` §4 and §6).
- No images, video, audio or likeness of anyone under 18.

---

## Slide 1 — Title and team

**Title:** Field Shift: Rotations Read from Space *(working title — [TBD: final project name and tagline])*

**Text:**
- Team **[TBD: team name]** · **[TBD: members, max. 6]** · **[TBD: local event]**
- NASA Space Apps Challenge 2026 — Challenge: *Field Shift: Adapting Farms with NASA Data*
- A decision-support tool that compares crop rotations for U.S. Corn Belt farms using NASA Earth observations,
  soil and crop data.

**Figure:** background map of the Corn Belt counties (outline only) with the study states highlighted.
- From: `data/reference/condados.gpkg` (US Census Cartographic Boundary Files 2024, 1:500k).

**Data credit:** County boundaries: U.S. Census Bureau, Cartographic Boundary Files 2024.

---

## Slide 2 — The problem

**Title:** One rotation, one risk

**Text:**
- Most Corn Belt cropland runs a corn–soybean rotation. Continuous corn and continuous soybean pay a yield
  penalty, and that penalty grows in dry and low-yield years.
- On farmer fields (748,374 insurance records, 2007–2012), continuous corn yielded **4.3 % less** (rainfed) and
  **1.7 % less** (irrigated); continuous soybean, about **10 % less** (Seifert et al. 2017).
  `[src: docs/research/efecto_rotacion.md, table §2]`
- Farmers need field-level evidence, not a single number, to decide whether a third crop is worth it.

**Figure:** simple bar chart of the rotation penalties above (rainfed vs irrigated, corn and soybean), labelled
"literature, not our model".
- From: `docs/research/efecto_rotacion.md` (Seifert, Roberts & Lobell 2017, Agronomy Journal 109:541–548).

**Data credit:** Seifert et al. (2017), Agronomy Journal 109:541–548.

**Note for the team:** this slide uses published literature, not our CSVs. Say so on the slide.

---

## Slide 3 — The existing rotation, mapped (demo point 1)

**Title:** What farmers actually rotate

**Text:**
- Pixel-by-pixel crop history (30 m, 2008–2025) tells us, for every county, how much corn follows soybean and how
  much corn follows corn.
- 8-year sequences show where the corn–soybean alternation dominates and where continuous corn or small grains
  and alfalfa appear.
- Share of corn after corn, Corn Belt counties, **[TBD: year]**: **[TBD: range or median from
  `rotacion_anual.csv`]**.

**Figure:** two side-by-side county maps:
- Left: `pct_maiz_tras_maiz` for the latest year, from `rotacion_anual.csv` (package `cultivos`) — USDA data.
- Right (required, so Relevance does not rest only on USDA data): a NASA layer for the same counties, e.g.
  July `ndvi_maiz` from `vegetacion_mensual.csv` (MODIS MOD13Q1) or the July `sm_rootzone_anom_z` from
  `agua_mensual.csv` (SMAP L4).
- Alternative left map: `pct_maiz_soja_alternado` for window 2018–2025, from `rotacion_secuencia.csv`.

**Data credit:** USDA NASS Cropland Data Layer and Crop Sequence Boundaries · NASA MODIS MOD13Q1 V061
(doi:10.5067/MODIS/MOD13Q1.061) *or* NASA SMAP L4 V8 (doi:10.5067/T5RUATAQREF8).

---

## Slide 4 — Comparing three rotations (demo point 2)

**Title:** Three strategies, with their evidence and their gaps

**Text:**
- For each county the tool compares at least three strategies: the current **corn–soybean**, **continuous
  corn**, and a **diversified rotation** with wheat, oats or alfalfa.
- Each one shows why it was suggested, the evidence behind it, expected benefits, data gaps and risks that need
  local review — as a **range, not a single number**.
- Field trials behind the diversified option: corn +4 % and soybean +16 % vs corn–soybean in 3–4-year rotations
  at Marsden Farm, Iowa, with 86–91 % less mineral N; and 14 %–90 % smaller yield losses in drought years across
  11 long-term trials (Bowles et al. 2020). `[src: docs/research/efecto_rotacion.md]`
- *This tool supports, and does not replace, farmer judgment and local agronomic expertise.*

**Figure:** a three-column card (one per rotation) for one example county: predicted yield range, margin range
and risk notes.
- From: model outputs built on `data/processed/tabla_anual.csv` (NASS yield + POWER/IMERG climate + SSURGO
  soil + CDL rotation + MODIS phenology), plus `economia_anual.csv` for margins.
- **[TBD: model results and uncertainty ranges from the ML team.** This repo does not train models; do not put
  numbers on this card until the ML team delivers them.]

**Data credit:** NASA POWER · NASA GPM IMERG V07 (doi:10.5067/GPM/IMERGDF/DAY/07) · NASA MODIS MOD13Q1 V061 ·
USDA NASS Quick Stats · USDA NRCS SSURGO · USDA ERS Commodity Costs and Returns.

---

## Slide 5 — Inside one field (demo point 3)

**Title:** Dry knolls and wet swales, pixel by pixel

**Text:**
- 10 demonstration fields (Iowa, Illinois, Indiana), each split into 30 m pixels with terrain, soil, crop
  history and every clear Landsat / Sentinel-2 observation since 2000.
  `[src: docs/datasets/lotes.md, field table]`
- Relief inside a field ranges from about **4 m** (flat Champaign control fields) to **31 m** (loess hills)
  in NASADEM. `[src: docs/datasets/lotes.md, "Relieve" table]`
- NASA HLS (Sentinel-2) and Landsat agree on the same pixel: mean NDVI difference **−0.017** (s.d. 0.048) over
  343,925 pairs within 3 days. `[src: docs/datasets/lotes.md, "Coherencia Landsat–Sentinel-2"]`
- **[TBD: sector map (dry knoll / mid-slope / wet swale) from the ML team.** This repo only delivers the
  pixels.]

**Figure:** one loess-hills field (e.g. `19165_191825002368896`, Shelby County, IA): left, NASADEM elevation
(`terreno_px.csv`, `elevacion_m`); middle, July NDVI per pixel (`vegetacion_px_obs.csv` or
`vegetacion_px_anual.csv`); right, SSURGO map units (`suelo_px.csv`). Release `fieldshift_lotes_v1`.

**Data credit:** NASA NASADEM V001 (doi:10.5067/MEASURES/NASADEM/NASADEM_HGT.001) · NASA HLS S30 V2.0, derived
from ESA Copernicus Sentinel-2 (doi:10.5067/HLS/HLSS30.002) · USGS Landsat Collection 2 Level-2 · USDA NRCS
SSURGO · USDA NASS CSB and CDL.

---

## Slide 6 — Stress in the season, and satellite vs ground (demo points 4 + 5)

**Title:** Seeing stress — and checking it on the ground

**Text:**
- Left: root-zone soil moisture from **SMAP** (2015–2025) and evaporative stress from **ECOSTRESS** (2025,
  April–October), with July (corn silking) highlighted. Wet springs delay planting; dry Julys cut yield.
- Right: satellite rainfall vs ground gauges, monthly by county (IA, IL, IN, 2000–2025, 91,416 county-months):
  NASA POWER vs PRISM, r = **0.944**, bias **−3.5 mm/month**; GPM IMERG vs PRISM, r = **0.932**, bias
  **+5.6 mm/month**; against CoCoRaHS volunteer gauges, r = **0.907** (POWER) and **0.890** (IMERG).
  `[src: docs/datasets/validacion.md, validation table]`
- Satellites see every county every day; gauges are points. We show both, and their difference.

**Figure:**
- Left: monthly time series for one county (e.g. Story County, IA, fips 19169): `sm_rootzone_m3m3` from
  `agua_mensual.csv`, `esi_ecostress` from `ecostress_mensual.csv`, and `prec_imerg_mm` from
  `clima_mensual.csv`; July shaded. ECOSTRESS covers 2025-04 to 2025-10 only — label it.
- Right: scatter of monthly `prec_power_mm` / `prec_imerg_mm` (`clima_mensual.csv`) vs `prec_prism_mm`
  (`validacion_mensual.csv`), 1:1 line, r and bias printed.

**Data credit:** NASA SMAP L4 V8 (doi:10.5067/T5RUATAQREF8), via USDA NASS Crop-CASMA · NASA ECOSTRESS L4T_ESI
V002 (doi:10.5067/ECOSTRESS/ECO_L4T_ESI.002) · NASA POWER · NASA GPM IMERG V07 · PRISM Group, Oregon State
University · CoCoRaHS.

---

## Slide 7 — NASA data and sources

**Title:** Built on open NASA data

**Text (plain text, no logos):**
- **NASA data (12 products with DOI + POWER):**
  - NASA POWER, Daily API, AG community (no DOI; acknowledgement below)
  - GPM IMERG Final Daily V07 — doi:10.5067/GPM/IMERGDF/DAY/07 (Late Run V07 for 2025-10 to 2025-12 —
    doi:10.5067/GPM/IMERGDL/DAY/07), via POWER
  - SMAP L4 SPL4SMGP V8 — doi:10.5067/T5RUATAQREF8, via Crop-CASMA
  - GRACE-DA-DM U.S. V4.0 — doi:10.5067/UH653SEZR9VQ
  - MODIS MOD13Q1 V061 — doi:10.5067/MODIS/MOD13Q1.061 · MOD11A2 V061 — doi:10.5067/MODIS/MOD11A2.061
  - NLDAS-2 Noah Monthly V2.0 — doi:10.5067/WB224IA3PVOJ
  - NASADEM V001 — doi:10.5067/MEASURES/NASADEM/NASADEM_HGT.001
  - ECOSTRESS V002: L2T_LSTE — doi:10.5067/ECOSTRESS/ECO_L2T_LSTE.002 · L3T_JET —
    doi:10.5067/ECOSTRESS/ECO_L3T_JET.002 · L4T_ESI — doi:10.5067/ECOSTRESS/ECO_L4T_ESI.002
  - HLS S30 V2.0 (derived from ESA Copernicus Sentinel-2) — doi:10.5067/HLS/HLSS30.002
- **POWER acknowledgement (required):** "The data was obtained from National Aeronautics and Space
  Administration (NASA) Langley Research Center's Prediction Of Worldwide Energy Resources (POWER) project funded
  through the NASA Earth Science Division." **[TBD: add "The data was obtained from the POWER Project's Daily
  2.x.x version on YYYY/MM/DD" with the exact API version and access date.]**
- **Other sources:** USGS Landsat C2 L2, 3DEP and Annual NLCD · USDA NASS (Quick Stats, Crop Progress, Census,
  CDL, CSB, Crop-CASMA) · USDA ERS · USDA NRCS SSURGO · U.S. Census Bureau · PRISM (Oregon State University) ·
  CoCoRaHS · AgTile-US.
- **Open pipeline:** **[TBD: public repo URL]** · data in the GitHub Releases **[TBD: release URL]**.
- AI disclosure line: "Pipeline code and documentation were written with the help of AI coding agents (Claude);
  all data are downloaded from the cited sources, not generated by AI." **[TBD: team confirms wording.]**

**Figure:** none (text only). Optional: a small diagram "NASA data → county / field tables → rotation
comparison".

**Open points to check before publishing** (`citas_nasa.md`):
- SMAP version: Crop-CASMA does not state it; V8 is certain from 2025-07-04 onwards and is the recommended
  citation.
- GRACE-DA-DM: files say `030`, CMR lists V4.0; cite V4.0.
- Copernicus attribution text for Sentinel-2 ("contains modified Copernicus Sentinel data [year]") is
  **not verified**. **[TBD]**

---

## 30-second video script

Use this if the team submits a video instead of slides (only one of the two is needed; either one must stay
within its limit). Structure follows the Project Submission Guide timeline (`space_apps_criterios.md` §2).
Narration can be in another language with English subtitles. ~12–14 words per 5 s.

| Time | What is on screen | What is said (EN) |
|---|---|---|
| 0:00–0:05 | Team name, member names **[TBD]**, then the challenge title "Field Shift: Adapting Farms with NASA Data" | "We're team [TBD]. We chose Field Shift because rotations decide farm risk." |
| 0:05–0:10 | Project name and tagline **[TBD]** over the Corn Belt map of corn-after-corn share (`rotacion_anual.csv`) fading into a NASA layer (MODIS NDVI or SMAP) | "[Project name]: comparing crop rotations with NASA satellites, for every Corn Belt county." |
| 0:10–0:15 | Three rotation cards (corn–soybean, continuous corn, diversified) with ranges **[TBD: from ML team]** | "Pick your field and compare three rotations — with ranges, evidence and open risks." |
| 0:15–0:20 | One loess-hills field: NASADEM relief → per-pixel NDVI from Landsat and HLS (`lotes`) | "Inside each field, NASA elevation and imagery separate dry knolls from wet swales." |
| 0:20–0:25 | SMAP root-zone moisture with July highlighted, then the IMERG/POWER vs PRISM scatter (r = 0.93–0.94) | "SMAP, ECOSTRESS and GPM show stress; we check them against ground gauges." |
| 0:25–0:30 | Text credits: "Data: NASA POWER, GPM IMERG, SMAP, MODIS, ECOSTRESS, NASADEM, HLS, NLDAS, GRACE · USDA" + repo link **[TBD]** | "Open NASA data, an open pipeline — and the farmer still makes the call." |

Video checks: ≤ 30 s total (trim, do not speed up); English subtitles if narrated in Spanish; watermark on any
AI-generated image or voice; no NASA logos modified; hosted on a public link (YouTube/Vimeo/Drive) and tested in a
private window.

---

## Sources for every number in this draft

| Number | Where it comes from |
|---|---|
| 4.3 % / 1.7 % continuous-corn penalty, ~10 % continuous-soybean penalty, 748,374 records | `docs/research/efecto_rotacion.md` (Seifert, Roberts & Lobell 2017) |
| Marsden +4 % corn, +16 % soybean, −86 % to −91 % mineral N | `docs/research/efecto_rotacion.md` (ISU Marsden Farm; Davis et al. 2012) |
| 14 %–90 % smaller drought losses, 11 trials | `docs/research/efecto_rotacion.md` (Bowles et al. 2020) |
| 10 fields; relief 4.00–31.03 m (NASADEM) | `docs/datasets/lotes.md`, field and relief tables |
| NDVI Landsat − HLS: −0.0173 ± 0.0477, 343,925 pairs | `docs/datasets/lotes.md`, "Coherencia Landsat–Sentinel-2" |
| Rainfall r and bias (POWER, IMERG vs PRISM and CoCoRaHS), 91,416 county-months | `docs/datasets/validacion.md`, validation table |
| SMAP 2015-03-31 to 2025-12-31; ECOSTRESS 2025-04 to 2025-10 | `docs/datasets/agua.md`, `docs/datasets/ecostress.md` |
| 12 NASA products with DOI + POWER; all DOIs | `docs/research/citas_nasa.md` §1 |
| 293 counties (IA, IL, IN); 666 counties in 7 states | `docs/datasets/clima.md`; `CLAUDE.md` §2 |
| Demo limits, deadline, criteria | `docs/research/space_apps_criterios.md` §1–§2 |

Still **[TBD]**: project name and tagline, team name and members, local event, corn-after-corn summary numbers
(compute from the published `rotacion_anual.csv`), model results and uncertainty ranges (ML team), sector maps
(ML team), repo and release URLs, POWER API version and access date, Copernicus attribution wording,
confirmation that the 7-state release is published.
