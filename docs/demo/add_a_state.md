# How to add a new U.S. state to the Field Shift pipeline

The pipeline is not tied to the first study area. Every script reads the list of states at run time, so a new
state is a configuration change plus a run of the same scripts, not new code. This page lists the steps we
actually used to add Ohio, Nebraska and Minnesota (second batch, tasks T001 and T003), Kansas (T002 and T013)
and Missouri, Wisconsin and South Dakota (third batch, T062). It also gives the sizes and times measured on
those runs, and the checks that still need a person.

All numbers come from files in this repository. Each one cites its source. Times are wall-clock on our own
machines, so treat them as orders of magnitude.

## Steps

1. **Approve the state.** States, period and any download over 5 GB are decisions for a person, not for the
   scripts (`CLAUDE.md` §1, rule 6). Add the state to `config/config.yaml` and assign it to a machine in
   `coordinacion/maquinas.yaml`. That was the whole change for Missouri, Wisconsin and South Dakota: 4 lines in
   `config.yaml`, plus tests that had used those states as "outside" examples (commit `505d82c`).
2. **Select the states on the machine.** Set `FIELDSHIFT_ESTADOS` (for example `FIELDSHIFT_ESTADOS=MO,WI,SD`).
   `src/common/config.py` filters the state list with it, so every script works only on those states
   (`CLAUDE.md` §2, `MAQUINAS.md`). Use a separate working copy per group of states if their areas are far
   apart: MODIS, NLDAS and land cover download a bounding box built from the counties (`T002`).
3. **Base package.** Run `src/base/download.py` and `src/base/process.py`. They write the county polygons and
   table (`data/reference/condados.*`, from the Census 1:500k county file) and the year windows (`anios.csv`).
   For Kansas this gave 105 counties (`T013`).
4. **Downloads, in two parallel lanes** (`CLAUDE.md` §9, `T013`). Each `download.py` is idempotent: files
   already in `data/raw/` are skipped, and each file gets a row in `manifest.csv`.
   - Lane A: `clima` (NASA POWER, then `python src/clima/download.py imerg` for GPM IMERG) → `suelo_terreno` →
     `cultivos` (NASS, Cropland Data Layer, Crop Sequence Boundaries) → `economia` → `validacion`.
   - Lane B: `agua` (SMAP, GRACE-DA-DM) → `vegetacion` (MODIS) → `nldas` → `vegetacion/download_nldas.py` →
     `paisaje`.
   - National files (the full NASS Quick Stats database and GRACE-DA-DM for the U.S.) are copied from a
     machine that already has them, with their `manifest.csv` rows, instead of downloaded again (`T001`,
     `MAQUINAS.md` §4).
5. **Processing.** Run each package's `process.py`, with `cultivos` first, because it writes the crop masks
   from the Cropland Data Layer that `vegetacion` uses (`CLAUDE.md` §9). Every CSV has to pass `validar_csv()`
   (keys, county codes, physical ranges). If a script fails because of an assumption that only held in the
   first states, the fix goes into the code, never into the data (`T013`).
6. **Data cards.** Update `docs/datasets/<package>.md` with the real coverage of the new state: dates, share
   of missing values per column, assumptions and known problems (`CLAUDE.md` §7).
7. **Publish.** `FIELDSHIFT_ESTADOS=MO,WI,SD python scripts/entregar.py` builds one zip per package (CSVs, data
   card, county table, manifest rows) with a `.sha256`, and uploads it to the GitHub release `datos-mo-wi-sd`.
   It refuses to upload if any manifest URL carries an API key (`scripts/entregar.py`).
8. **Check the release.** `python scripts/verificar_entrega.py data/entregas/<release>/*.zip` checks each zip
   against the CSV contract and marks every package APTO (fit) or NO APTO (not fit). Ohio, Nebraska and
   Minnesota passed with 8 packages APTO (`T003`). Then `python scripts/qa_release.py <release> --eventos
   <events>.yaml` looks for missing values by state, known extreme events, ranges, outliers against
   neighboring counties and county totals against NASS (`scripts/qa_release.py`, example in
   `docs/qa/oh_ne_mn.md`).
9. **Join.** `scripts/unir_estados.py` stacks the releases of all groups of states, package by package, and
   checks that no key and no county appears twice. `src/merge.py` then builds the joined annual and monthly
   tables. One coordinating machine does this step (`MAQUINAS.md` §4, `T008`).

## Size and time per state

| States | Counties | Raw download | Download time | Processing time | Published zips | Source |
|---|---|---|---|---|---|---|
| OH + NE + MN (measured) | 268 | 21 GB, 35,486 files | 3 h 04 min | 2 h 43 min, including a second CDL download and two code fixes | 91.0 MB, 8 packages | [T001](../../coordinacion/tareas/T001-crudos-oh-ne-mn.md), [T003](../../coordinacion/tareas/T003-procesar-estados-nuevos.md), [coverage](coverage.md) |
| KS (measured) | 105 | 11 GB | ≤ 1 h 32 min, run at the same time as OH + NE + MN | not logged | not published yet | [T002](../../coordinacion/tareas/T002-crudos-ks.md), [T013](../../coordinacion/tareas/T013-kansas-punta-a-punta.md) |
| KS, `clima` package only (measured) | 105 | 385 MB (POWER for 105 counties, IMERG for 2,193 cells) | ~20 min | | | [T013](../../coordinacion/tareas/T013-kansas-punta-a-punta.md) |
| MO + WI + SD | | not logged yet | not logged yet | not logged yet | not published yet | [T062](../../coordinacion/tareas/T062-mo-wi-sd.md) (in progress) |
| MI (estimate) | 83 | 8–11 GB | 1–1.5 h (up to 2 h) | | | [cuarta_tanda.md](../research/cuarta_tanda.md) |
| ND (estimate) | 53 | 4–5 GB | 0.5–0.7 h | | | [cuarta_tanda.md](../research/cuarta_tanda.md) |
| KY (estimate) | 120 | 4–5 GB | 0.5–0.7 h | | | [cuarta_tanda.md](../research/cuarta_tanda.md) |

Rules of thumb from the same research ([cuarta_tanda.md](../research/cuarta_tanda.md) §5.1 and §6):

- The national files (NASS 1.1 GB and GRACE-DA-DM ~4.7 GB, about 5.8 GB together) are downloaded once per
  machine. The rest grows with the bounding box of the state's counties: about **0.019–0.023 GB per
  1,000 km²** of box, fitted on the two measured runs.
- Download speed was about **6–9 minutes per GB** on one machine with the two lanes.
- No new MODIS tiles were needed for Michigan, North Dakota or Kentucky: all fall on tiles we already download
  for the 7 current states.
- A state with large lakes inside its box (Michigan) costs more than its land area suggests, because MODIS and
  land cover download the whole box.

The processed output is small next to the raw data: 21 GB of raw files for Ohio, Nebraska and Minnesota became
91.0 MB of published zips.

## What still needs a person

The scripts run the same way in every state, but each state's sources have their own gaps. For each new state
we run short research tasks before processing. The Kentucky set (T077–T080) is the model:

- **NASS coverage** ([nass_ky.md](../research/nass_ky.md), T077): which crops and years exist at county level,
  how many counties are hidden in "OTHER COUNTIES", what Crop Progress publishes. In Kentucky, corn yields have
  county data in 60 of 120 counties in 2025, and hay and tobacco have county data only until 2018.
- **Cropland Data Layer accuracy** ([cdl_precision_ky.md](../research/cdl_precision_ky.md), T078): which crop
  classes are good enough for rotations. In Kentucky corn, soybean and double-crop wheat/soybean are usable.
  Winter wheat alone, tobacco, alfalfa and other hay are not.
- **Known extreme events** ([eventos_extremos_ky.md](../research/eventos_extremos_ky.md), T079): droughts,
  late frosts, heat and floods by region and year, with the signal we expect in our CSVs. The QA step (8) checks
  the release against this list.
- **Budgets and prices** ([presupuestos_ky.md](../research/presupuestos_ky.md), T080): crop budgets from the
  state university, NASS prices received and the USDA ERS region of each county.
- **Soil survey** ([suelo_ky.md](../research/suelo_ky.md)): SSURGO is complete in Kentucky, but its survey
  areas do not match counties, so the code that maps survey areas to counties needs a change before processing.
- **Size approval:** each of Michigan, North Dakota and Kentucky is above the 5 GB limit that needs a person's
  approval ([cuarta_tanda.md](../research/cuarta_tanda.md)).
- **Irrigation:** in Nebraska and Kansas much corn and soybean is irrigated, and NASS yields mix irrigated and
  dryland fields. Keep this in mind before comparing those states with Iowa (`CLAUDE.md` §2).

The same research exists for Missouri, Wisconsin and South Dakota
([nass_mo_wi_sd.md](../research/nass_mo_wi_sd.md), [cdl_precision_mo_wi_sd.md](../research/cdl_precision_mo_wi_sd.md),
[eventos_extremos_mo_wi_sd.md](../research/eventos_extremos_mo_wi_sd.md),
[presupuestos_mo_wi_sd.md](../research/presupuestos_mo_wi_sd.md)).
