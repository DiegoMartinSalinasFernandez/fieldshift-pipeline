# Field Shift — Data quality

NASA Space Apps Challenge 2026, challenge "Field Shift: Adapting Farms with NASA Data".

This page explains how we check the data before it is published, what the quality check of the Ohio, Nebraska
and Minnesota release found, and which problems we know about. It is written for the **Validity** criterion.
Every number is copied from a repository document, named in each row: the QA report of the release
`datos-oh-ne-mn` (`docs/qa/oh_ne_mn.md`, task T073, 2026-11-15), `docs/demo/limitations.md`,
`docs/research/modis_fechas.md` and `docs/datasets/agua.md`. Nothing was recomputed for this page.

Column names are in Spanish (`rend_bu_ac` = yield in bu/ac, `prec_*_mm` = precipitation in mm). The glossary is
at the end of `docs/datasets/README_en.md`.

---

## 1. Checks

Three layers, from the single file to the whole release. None of them changes the data: they only read the CSVs
and report.

| Check | Where it runs | What it controls |
|---|---|---|
| `validar_csv()` (`src/common/validacion.py`) | On every processed CSV, before it is published | Key columns first and well formed (`fips` with 5 digits and present in `condados.csv`, `anio` integer, `fecha` `YYYY-MM-DD`, `mes` `YYYY-MM`, `anio` matching the date); no duplicated keys; decimal point, not comma; no fill codes (−999, −9999, −99.99…); physical ranges (precipitation ≥ 0, NDVI/EVI in −1…1, soil moisture in 0…0.6 m³/m³, percentages in 0…100, corn yield 20–300 bu/ac, soybean 5–100 bu/ac) |
| `scripts/verificar_entrega.py` | On each published zip (or on a merged folder), without downloading anything | Everything `validar_csv()` checks, using the `condados.csv` shipped inside the zip; UTF-8 without BOM, `,` separator, `snake_case` names; missing values written as text (`NaN`, `None`, `(D)`, `(Z)`…) instead of empty cells; one data-card row per non-key column; the zip's `.sha256`. Verdict per package: APTO (pass) / NO APTO (fail) |
| `scripts/qa_release.py` (generalizes `docs/qa/oh_ne_mn_qa.py`) | On a whole release, for any batch of states | Content: missing values per state against the first batch (IA/IL/IN); known extreme events (list in a YAML file, e.g. `docs/qa/eventos_oh_ne_mn.yaml`); ranges; outliers against each county's 6 nearest neighbours; county sums of planted area against NASS state totals |

## 2. Result for Ohio, Nebraska and Minnesota (release `datos-oh-ne-mn`, 268 counties)

Source: `docs/qa/oh_ne_mn.md`.

- **Format:** `verificar_entrega.py` gives 8 of 8 packages APTO, with no problems or warnings. The 8 `.sha256`
  files match. `condados.csv` has 268 counties (OH 88, NE 93, MN 87), the expected total.
- **Verdict:** no package is NO APTO. `cultivos` and `vegetacion` pass with observations (section 4).
  `economia`, `paisaje` and `suelo_terreno` were checked for format only.

### Extreme events visible in the data

Known droughts, floods and heat waves (from `docs/research/eventos_extremos.md` and
`eventos_extremos_nuevos.md`) should show up in independent sources at once: rainfall, soil moisture, NDVI and
yields. State means of county values:

| Event | What the data shows | OK? |
|---|---|---|
| 2002 drought, Ohio | August `spi3` −1.81; July rain 61 mm; July–August `ndvi_anom_z` −1.78; corn 89.0 bu/ac (138.0 in 2001), soybean 32.0 (41.0) | yes |
| 2002 drought, Nebraska | `spi3` −1.18; July rain 35 mm; `ndvi_anom_z` −1.92; corn 128 bu/ac (147 in 2001) | yes |
| 2012 drought, all three | August `spi3` MN −1.26 / NE −2.48 / OH −1.44; NLDAS `sm_0_100cm_anom_z` −1.76 / −2.16 / −1.98; `ndvi_anom_z` −0.66 / −2.12 / −0.77; corn vs. previous 5 years NE −14 %, OH −21 % (120.4 bu/ac), MN +1.4 % | yes (MN barely lost yield in 2012, consistent with NASS: 165 bu/ac) |
| 2019 March flood, Nebraska | March `prec_power_mm` 73 mm (34–50 in 2018 and 2020) | yes |
| 2019 prevented planting, Ohio | County sum of corn planted area 2.43 M ac (3.26 M in 2018, 3.53 M in 2020) | yes |
| 2021 drought, Minnesota | `spi3` −1.00; NLDAS −2.10; SMAP `sm_rootzone_anom_z` −1.49; May+June rain 109 mm (driest in the table); `ndvi_anom_z` −0.22; corn 176.4 bu/ac (−5.8 %) | yes (weak state-level NDVI: the damage was in the north) |
| 2022 summer drought, Nebraska | `spi3` −1.43; NLDAS −1.55; SMAP −1.27; corn −11 %, soybean −18 % | yes |
| 2011 July heat | July `tmin_c` 2011 above 2010 in all three (MN 18.0 / NE 20.8 / OH 19.7 °C) | yes |
| 2013 wet spring, Minnesota | May+June rain 259 mm, the highest for MN in the table | yes |
| 2004 early frost (Aug 20–21), northern Minnesota | **Not visible**: every MN county has `doy_primera_helada` 275–276 (Oct 1–2). POWER's minimum `tmin_c` on 2004-08-20 is 2.4–2.9 °C | expected: the 0.5° POWER cell averages out frost in low spots |

### NASS totals close

County sums of planted area (`AREA PLANTED`, SURVEY, `ALL PRODUCTION PRACTICES`) were compared with NASS state
totals from the full Quick Stats database. Median 2000–2025: 98.3–99.0 % for corn and soybean in the three
states. In some recent years the county sum drops (down to 52–54 % in Nebraska 2025) because NASS publishes fewer
counties and groups the rest in "OTHER (COMBINED) COUNTIES" (`county_code` 998), which we exclude on purpose
because it is not a county. **Adding the 998 row back, the state total closes in every year** (MN corn
99.6–100.0 %, MN soybean 99.0–100.0, NE corn 100.0–100.5, NE soybean 96.2–100.0, OH 100.0), and the number of
counties per year matches NASS. The `cultivos` processing loses nothing.

### Ranges and outliers

- Yield ranges (min–max bu/ac): corn OH 43.5–222.1, NE 32.5–240.5, MN 49.0–226.7; soybean OH 19.4–66.9,
  NE 15.0–75.5, MN 7.0–67.4. All inside the `validar_csv()` limits.
- Daily weather extremes: `tmin_c` −45.5 °C (Lake of the Woods, MN, 2019-01-30), `tmax_c` 46.4 °C (Dundy, NE,
  2012-06-27), daily rain up to 113 mm (POWER) and 153 mm (IMERG). All inside the spec.
- Neighbour outliers: no county's 2000–2025 growing-season rain or GDD is an outlier (|z| > 4). Yield outliers
  (|z| > 5) are mostly Boyd County, NE, and western Nebraska counties: the known irrigated/rainfed mix of
  `ALL PRODUCTION PRACTICES`, not a processing error.

## 3. Known problems we do not hide

| Problem | Effect | Source |
|---|---|---|
| NASS county coverage falls in recent years | NE counties with corn planted area: 91 (2000) → 55 (2021) → 46 (2025); NE soybean 79 → 36. State totals or means built from counties are biased in those years; the CDL (`rotacion_anual.csv`) is the area reference | `docs/qa/oh_ne_mn.md` problem 1; `limitations.md` 1.2–1.3 |
| Yields mix irrigated and rainfed fields | Median irrigated-minus-rainfed corn gap 81 bu/ac (NE) and 103 bu/ac (KS); no irrigation mask yet | `limitations.md` 4.1–4.3 |
| Low oat and wheat yields in Nebraska | Oats down to 5.0 bu/ac (winter wheat down to 8.7). Oats fall below the range proposed by research (10–200 bu/ac), which is not yet in `validar_csv()`; if adopted as is, NE oats would fail. Soybean in MN reaches 7.0, close to the current minimum of 5 | `docs/qa/oh_ne_mn.md` §3, problem 2 |
| `ndvi_maiz` / `ndvi_soja` much sparser outside IA/IL/IN | Missing in 66–70 % of OH corn rows and ~60–63 % of soybean rows in all three states (IA/IL/IN: ~40 %). 2000–2007 is always empty (no national CDL) and the 75 % crop-purity threshold leaves few pure pixels in small or mixed fields | `docs/qa/oh_ne_mn.md` §5, problem 3; `limitations.md` 1.15, 2.7 |
| 11 MODIS MOD13Q1 composites missing | Missing only on Planetary Computer, worldwide (a gap in its ingestion, not a Terra problem): 1 in 2023, 2 in 2024 and 8 in a row from 2025-07-12 to 2025-11-16. NASA LP DAAC has all 23 per year. The 2025 gap leaves `ndvi_max`, `doy_pico`, `doy_fin`, `ndvi_integral` and the Jul–Nov 2025 monthly means without data from the 2025 growing season. Refill from LP DAAC (needs Earthdata, ~7–13 GB) or ORNL DAAC is proposed, not done | `docs/research/modis_fechas.md` |
| SMAP cells above 0.60 m³/m³ removed | The filter always removes the same cells (organic soils and peat): 384 in MN and 23 in OH (values 0.62–0.93). It touches 46 of 87 MN counties (65 % of Koochiching's area, 49 % of Le Sueur, 46 % of Aitkin). In those counties `sm_rootzone_m3m3` is up to 0.25–0.40 m³/m³ lower than with all cells, and `dias_sm_saturado` undercounts. No county is left without valid cells. Open water is already nodata and is not affected | `docs/datasets/agua.md`; `limitations.md` 1.11 |
| `doy_primera_helada` misses local frosts | See the 2004 event above: POWER's 0.5° cell is too coarse for frost in low spots | `docs/qa/oh_ne_mn.md` problem 5 |
| IMERG vs POWER rainfall | Median annual ratio IMERG / POWER: MN 1.07, NE 1.07, OH 1.18. Not an error, but a larger bias between the two sources in Ohio | `docs/qa/oh_ne_mn.md` §3 |
| One false positive in `validar_csv()` | A real `deficit_mm` of −99.99 mm (FIPS 18065, 2011-07) looks like a fill code. The value was kept | `limitations.md` 3.14 |

The full list of limitations (substituted sources, reduced resolution, biases, what is not merged yet) is in
[`limitations.md`](limitations.md).
