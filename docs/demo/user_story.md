# Field Shift — user stories for the demo

Three short stories of a grower who wants to compare crop rotations before deciding next season's plan.
Each one uses a real county and real numbers from the data we published.

**What is data and what is not.** Every number in the tables below is a value from a published CSV.
Nothing is modeled, detrended, smoothed or filled in. The tables are written by
[`user_story.py`](user_story.py), which reads the release zips and checks their `.sha256`. Do not edit the
tables by hand: re-run the script. Zips read: <!-- zips -->`datos-oh-ne-mn_clima.zip`, `datos-oh-ne-mn_cultivos.zip`, `datos-oh-ne-mn_vegetacion.zip`<!-- /zips -->.
The yield **predictions** and rotation **recommendations** come from the ML team's model, which is not
part of this repo. Where a story says "the tool would show…", that describes the screen. It is not a
result we computed.

`n/a` means the value is missing in the published CSV. The usual reasons are that NASS did not publish it
(hidden as `(D)` or never surveyed) or that too few clean MODIS pixels of that crop were found. We leave
those cells empty and never fill them.

Why no Iowa story: the release for IA, IL and IN (`datos-ia-il-in`) is not public yet. Neither is the KS
one. Every example comes from the OH, NE and MN release. Once the IA release is up, a story about Iowa
in the 2012 drought can be added by putting one more entry in `HISTORIAS` in the script.

---

## Story 1 — "Is my dryland corn worth the risk?" (Boyd County, Nebraska, 2012)

*Dana farms in north-central Nebraska, on land without irrigation. Each spring Dana has to decide how to
split the farm between corn and soybeans, and whether to plant corn again on last year's corn ground.*

Dana opens Field Shift, picks Boyd County and moves the year slider to 2012.

<!-- tabla:boyd -->
**Boyd County, NE** (FIPS 31015)

| Variable — source | 2011 | 2012 | 2013 |
|---|---:|---:|---:|
| Corn yield (bu/ac) — NASS | 127.8 | 72.2 | n/a |
| Soybean yield (bu/ac) — NASS | 44.1 | 17.3 | 45.3 |
| Corn planted (ac) — NASS | 39,700 | 40,000 | n/a |
| Soybean planted (ac) — NASS | 22,300 | 22,900 | 15,600 |
| Corn harvested for grain / planted — NASS | 0.95 | 0.45 | n/a |
| Growing-season rain, Apr–Sep (mm) — POWER | 465 | 275 | 533 |
| July rain (mm) — POWER | 66 | 15 | 71 |
| July mean Tmax (°C) — POWER | 33.1 | 38.4 | 31.0 |
| SPI-3 ending May (Mar–May) — POWER | 0.06 | -0.01 | 0.70 |
| SPI-3 ending July (May–Jul) — POWER | 0.53 | -2.27 | 0.58 |
| Peak NDVI, all cropland — MODIS | 0.705 | 0.581 | 0.719 |
| Peak NDVI, corn pixels — MODIS + CDL | n/a | n/a | 0.879 |
| Peak NDVI, soybean pixels — MODIS + CDL | n/a | n/a | n/a |
| Cropland in corn (%) — CDL | 41.9 | 42.1 | 47.0 |
| Cropland in fallow/idle (%) — CDL | 0.0 | 0.0 | 0.3 |
| Corn pixels that were soybean the year before (%) — CDL | 47.0 | 46.0 | 41.7 |
| Corn pixels that were corn the year before (%) — CDL | 35.2 | 43.3 | 49.2 |

- Irrigated share of cropland, Census of Agriculture (`pct_riego`): 2012: 5.3 %, 2017: 10.3 %, 2022: 2.3 %
- Tile-drained share of cropland, Census of Agriculture (`pct_drenaje_tile`): 2012: n/a %, 2017: n/a %, 2022: 0.3 %
- Day of year when 50 % of the crop was planted, statewide (NE, NASS Crop Progress): corn 2011: 127, 2012: 121, 2013: 133; soybean 2011: 138, 2012: 132, 2013: 143
<!-- /tabla:boyd -->

**What the data show.**
- Boyd is mostly dryland. The Census irrigated share is small in all three census years, so the county
  yield here is close to a dryland yield. Most of Nebraska is different: there, the
  `ALL PRODUCTION PRACTICES` yield mixes irrigated and dryland fields.
- In 2012 the growing season got much less rain than in 2011 or 2013. July was very dry and hot, and
  the SPI-3 ending in July is strongly negative. Spring (SPI-3 ending May) was close to normal, so the
  drought built up during the season, not before planting.
- Corn and soybean yields both fell in 2012, and peak cropland NDVI fell with them.
- Corn harvested for grain per acre planted dropped to under half. NASS counts grain only, so part of
  that gap could be corn chopped for silage or left unharvested. The data can't tell us which.
- The rotation mix barely moved: about the same share of corn followed soybeans in all three years.
  Planting decisions were made before the drought showed up.

**What the tool would show Dana.** A side-by-side view of "corn after soybean" and "corn after corn"
for Boyd. It would show the model's expected yield range for each under dry, normal and wet seasons,
and it would mark 2012 as the dry case in the historical record. The model output is not available
yet, so this repo shows no number for it.

---

## Story 2 — "The spring it never stopped raining" (Defiance County, Ohio, 2019)

*Sam grows corn and soybeans on tile-drained ground in northwest Ohio. In 2019 the planting window
never opened. Sam wants to know how a wet spring changes the choice between corn and soybeans.*

<!-- tabla:defiance -->
**Defiance County, OH** (FIPS 39039)

| Variable — source | 2018 | 2019 | 2020 |
|---|---:|---:|---:|
| Corn yield (bu/ac) — NASS | 176.1 | 160.0 | 136.0 |
| Soybean yield (bu/ac) — NASS | 53.9 | n/a | 41.1 |
| Corn planted (ac) — NASS | 50,000 | 12,000 | 54,800 |
| Soybean planted (ac) — NASS | 108,500 | n/a | 105,500 |
| Corn harvested for grain / planted — NASS | 0.92 | 0.58 | 0.93 |
| Growing-season rain, Apr–Sep (mm) — POWER | 544 | 685 | 423 |
| July rain (mm) — POWER | 72 | 111 | 58 |
| July mean Tmax (°C) — POWER | 27.6 | 28.2 | 30.1 |
| SPI-3 ending May (Mar–May) — POWER | 0.54 | 1.49 | 0.45 |
| SPI-3 ending July (May–Jul) — POWER | 0.36 | 1.00 | -0.66 |
| Peak NDVI, all cropland — MODIS | 0.856 | 0.692 | 0.755 |
| Peak NDVI, corn pixels — MODIS + CDL | 0.908 | n/a | 0.896 |
| Peak NDVI, soybean pixels — MODIS + CDL | 0.904 | 0.868 | 0.801 |
| Cropland in corn (%) — CDL | 25.3 | 6.0 | 26.8 |
| Cropland in fallow/idle (%) — CDL | 0.1 | 49.7 | 0.0 |
| Corn pixels that were soybean the year before (%) — CDL | 84.3 | 70.3 | 48.5 |
| Corn pixels that were corn the year before (%) — CDL | 8.7 | 21.8 | 4.3 |

- Irrigated share of cropland, Census of Agriculture (`pct_riego`): 2012: 0.0 %, 2017: 0.5 %, 2022: 0.6 %
- Tile-drained share of cropland, Census of Agriculture (`pct_drenaje_tile`): 2012: n/a %, 2017: 48.1 %, 2022: 46.2 %
- Day of year when 50 % of the crop was planted, statewide (OH, NASS Crop Progress): corn 2018: 132, 2019: 160, 2020: 136; soybean 2018: 140, 2019: 168, 2020: 143
<!-- /tabla:defiance -->

**What the data show.**
- Spring 2019 was wet: the SPI-3 ending in May is clearly positive, and the growing season got more
  rain than in 2018 or 2020.
- Statewide, Ohio got to 50 % corn planted about four weeks later than in 2018. Soybeans were just as
  late.
- In Defiance, NASS planted corn acres collapsed in 2019 compared with the years on either side. The
  CDL shows the same thing from space: the corn share of cropland dropped and roughly half the cropland
  was mapped as fallow/idle. This is consistent with prevented planting, but our CSVs have no
  prevented-planting variable (that is FSA/RMA data, which we did not download). Treat it as an
  inference, not a measurement.
- The corn that did get planted came in later, and its yield was lower than in 2018. The 2019 soybean
  yield is missing (`n/a`) in the NASS county data we published.
- Peak cropland NDVI in 2019 was well below 2018 and 2020. With half the cropland idle, that is the
  expected result.
- Drainage tile covers a large share of the county's cropland (Census `pct_drenaje_tile`, in
  `practicas_censo.csv`). Even so, 2019 was too wet to plant.

**What the tool would show Sam.** For a wet-spring scenario, the tool would put the expected outcome of
staying with corn (late planting) next to switching those acres to soybeans. It would use the
historical wet springs, 2019 among them, as reference years. Again, the expected outcomes would come
from the ML team's model. The table above is only the record of what happened.

---

## Story 3 — "Does rotation soften a drought?" (Butler County, Ohio, 2012)

*Alex farms in southwest Ohio, where most corn is planted after soybeans. Alex wants to see what a
drought year looked like in a county that already rotates heavily.*

<!-- tabla:butler -->
**Butler County, OH** (FIPS 39017)

| Variable — source | 2011 | 2012 | 2013 |
|---|---:|---:|---:|
| Corn yield (bu/ac) — NASS | 127.6 | 64.5 | 167.5 |
| Soybean yield (bu/ac) — NASS | 37.6 | 28.1 | 45.3 |
| Corn planted (ac) — NASS | 30,000 | 30,800 | 31,000 |
| Soybean planted (ac) — NASS | 33,700 | 34,200 | 32,900 |
| Corn harvested for grain / planted — NASS | 0.97 | 0.92 | 0.97 |
| Growing-season rain, Apr–Sep (mm) — POWER | 842 | 473 | 500 |
| July rain (mm) — POWER | 73 | 76 | 114 |
| July mean Tmax (°C) — POWER | 30.0 | 33.3 | 27.6 |
| SPI-3 ending May (Mar–May) — POWER | 2.43 | -0.63 | -0.75 |
| SPI-3 ending July (May–Jul) — POWER | 0.38 | -1.22 | -0.18 |
| Peak NDVI, all cropland — MODIS | 0.734 | 0.663 | 0.763 |
| Peak NDVI, corn pixels — MODIS + CDL | n/a | n/a | 0.928 |
| Peak NDVI, soybean pixels — MODIS + CDL | n/a | n/a | n/a |
| Cropland in corn (%) — CDL | 48.0 | 47.6 | 44.0 |
| Cropland in fallow/idle (%) — CDL | 0.0 | 0.0 | 0.0 |
| Corn pixels that were soybean the year before (%) — CDL | 76.6 | 69.6 | 72.0 |
| Corn pixels that were corn the year before (%) — CDL | 20.4 | 25.1 | 24.1 |

- Irrigated share of cropland, Census of Agriculture (`pct_riego`): 2012: 0.3 %, 2017: 0.3 %, 2022: 1.1 %
- Tile-drained share of cropland, Census of Agriculture (`pct_drenaje_tile`): 2012: n/a %, 2017: 34.8 %, 2022: 31.4 %
- Day of year when 50 % of the crop was planted, statewide (OH, NASS Crop Progress): corn 2011: 155, 2012: 118, 2013: 133; soybean 2011: 159, 2012: 135, 2013: 140
<!-- /tabla:butler -->

**What the data show.**
- In Butler, about three quarters of the corn pixels were soybean the year before. That share stays
  high in all three years.
- 2012 was dry from spring onward: the SPI-3 ending in May and in July are both negative. July was also
  hotter than in 2011 and 2013. Planting was early that year (statewide, Ohio reached 50 % corn
  planted well before the other two years).
- Corn yield fell by roughly half compared with 2011. The soybean yield also fell, but by a smaller
  share. In Boyd (Story 1), soybeans fell by a larger share than corn. The same drought year hit the two
  crops differently in the two counties. That is exactly the kind of comparison the tool is meant to
  make visible.
- Almost all planted corn was still harvested for grain, unlike in Boyd.
- These are county averages. They don't show whether corn after soybeans did better than corn after
  corn *within* Butler in 2012. That needs field-level data, which is the job of the `lotes` package
  and the ML model, not of these tables.

**What the tool would show Alex.** A county view with the 2012 yields next to the rotation shares, and
the model's estimate of how much of the yield drop each rotation would have avoided. That estimate is
not in this repo.

---

## Sources

| Variable | Product | CSV in the release |
|---|---|---|
| Yields, planted acres, harvested/planted | USDA NASS Quick Stats, county survey, `ALL PRODUCTION PRACTICES` | `cultivos/produccion_anual.csv` |
| Irrigated share | USDA NASS Census of Agriculture (2012, 2017, 2022) | `cultivos/practicas_censo.csv` |
| 50 % planted date (state) | USDA NASS Crop Progress | `cultivos/fenologia_estado.csv` |
| Crop shares, corn after soybean / corn | USDA NASS Cropland Data Layer, 30 m, pixel transitions | `cultivos/rotacion_anual.csv` |
| Season and July rain, July Tmax | NASA POWER (AG community, daily, county centroid) | `clima/clima_anual.csv` |
| SPI-3 | Derived from NASA POWER precipitation, 1981 baseline | `clima/clima_mensual.csv` |
| Peak NDVI (all cropland, corn, soybean) | NASA MODIS MOD13Q1 250 m, with CDL crop masks | `vegetacion/fenologia_anual.csv` |

Column definitions, coverage and known issues are in the data cards that ship inside each zip
(`docs/datasets/<package>.md`).

To refresh the numbers:

```bash
.venv/bin/python -I -X utf8 docs/demo/user_story.py
```
