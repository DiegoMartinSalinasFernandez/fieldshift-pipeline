# Field Shift — 30-second demo video script

Shot-by-shot script for the NASA Space Apps Challenge 2026 demo video, challenge **"Field Shift: Adapting Farms
with NASA Data"** (task T096). It replaces the short table at the end of `docs/demo/slides.md` with a full
script: start and end second, what is on screen, on-screen text, subtitle and narration for every shot.

Rules this script follows (`docs/research/space_apps_criterios.md` §1–§2):

- **30 seconds or less, in total.** Going over removes the project from Global Judging. If it does not fit, cut
  words, do not speed up the voice.
- **Everything in English.** Narration may be in Spanish only if the English subtitles are burned in.
- **Only real figures** from `docs/demo/fig/` and **only numbers** from `docs/demo/coverage.md` or the published
  release `datos-oh-ne-mn`. Every number below has its source in the last table. No model results: the shot
  marked **[ML]** is left for the ML team.
- **What is published today:** only Ohio, Nebraska and Minnesota (268 counties, 2000–2025, release
  `datos-oh-ne-mn`). Do **not** say "666 counties" or "7 states" as delivered. All figures are OH/NE/MN only.
- No NASA logos (and no AI-modified logos): credits are plain text. Any AI-generated image or voice carries a
  visible "AI-generated" watermark. No people under 18.

Items in **[TBD]** are for the team: project name and tagline, team name. The open list is in
[`pendientes_humano.md`](pendientes_humano.md).

---

## Overview

| # | Time | Shot | Figure | Judging criterion it serves |
|---|---|---|---|---|
| 1 | 0:00–0:03 | Title, team and study area | `fig0_mapa.png` (on `main` since T094) | Presentation, Impact |
| 2 | 0:03–0:07 | The problem: weather years swing corn yield | `fig5_corn_yield_by_year_oh_ne_mn.png` | Impact |
| 3 | 0:07–0:11 | The rotation farmers actually run | `fig4_corn_after_soy_vs_corn_oh_ne_mn.png` | Relevance (existing rotation), Creativity |
| 4 | 0:11–0:15 | NASA SMAP sees wet springs that delay planting | `fig3_smap_may_vs_planting_oh_ne_mn.png` | Relevance (NASA data core), Impact |
| 5 | 0:15–0:18 | Two NASA rainfall products agree | `fig6_lluvia_oh_ne_mn.png` | Validity |
| 6 | 0:18–0:25 | **[ML]** Three rotations compared, with ranges | to be made by the ML team | Relevance (≥ 3 rotations), Creativity, Validity |
| 7 | 0:25–0:30 | NASA data credits, open data, farmer decides | none (text card) | Relevance, Impact, Presentation |

Total: **30 s**. Narration: **71 words** (about 70 fit in 30 s; see the word count per shot).

---

## Shot 1 — 0:00 to 0:03 · Title and team

- **On screen:** `docs/demo/fig/fig0_mapa.png` (task T094): the counties of the study states, solid where the
  data release is published (OH, NE, MN) and hatched where it is in progress. Title text over a dark band at
  the top. **Re-run `docs/demo/figuras.py --solo-mapa` before the final cut** so the solid/hatched status is
  current. Do not draw a map by hand.
- **On-screen text:**
  - Line 1 (large): **[TBD: project name]**
  - Line 2 (small): *Team [TBD] · NASA Space Apps 2026 · Field Shift: Adapting Farms with NASA Data*
- **Narration (7 words):** "We're team [TBD]. This is [project name]."
- **Subtitle:** `We're team [TBD]. This is [project name].`

## Shot 2 — 0:03 to 0:07 · The problem

- **On screen:** `docs/demo/fig/fig5_corn_yield_by_year_oh_ne_mn.png`. Slow zoom (about 110 %) towards the
  red 2012 box. Keep the bottom caption visible for the first second, or retype a short credit (below).
- **On-screen text** (top right, over the figure): **2012 drought: median county corn yield 138 bu/ac vs 161
  in other years**
- **Small credit** (bottom): *USDA NASS county yields · Ohio, Nebraska, Minnesota · 2000–2025*
- **Narration (11 words):** "One dry summer, like 2012, cuts corn yields across whole states."
- **Subtitle (2 lines):**
  - `One dry summer, like 2012,`
  - `cuts corn yields across whole states.`

## Shot 3 — 0:07 to 0:11 · The existing rotation

- **On screen:** `docs/demo/fig/fig4_corn_after_soy_vs_corn_oh_ne_mn.png`. Cursor or highlight moves from the
  Ohio cluster (bottom right) to the Nebraska cluster (top left).
- **On-screen text:** **Corn after corn, 2025 (county median): Ohio 11 % · Minnesota 24 % · Nebraska 46 %**
- **Small credit:** *USDA NASS Cropland Data Layer, 30 m pixels, 2024→2025 · 266 counties*
- **Narration (11 words):** "We map, pixel by pixel, which rotation every county really runs."
- **Subtitle (2 lines):**
  - `We map, pixel by pixel,`
  - `which rotation every county really runs.`
- **Speaker note:** Nebraska's high corn-after-corn share comes with irrigation (`CLAUDE.md` §2). Do not say it
  is a rainfed result.

## Shot 4 — 0:11 to 0:15 · NASA SMAP and wet springs

- **On screen:** `docs/demo/fig/fig3_smap_may_vs_planting_oh_ne_mn.png`. Zoom to the Ohio 2019 point (top
  right, label "19").
- **On-screen text:** **Ohio 2019: wettest May in SMAP (0.38 m³/m³) → half the corn planted only by day 160**
- **Small credit:** *NASA SMAP L4 root-zone soil moisture · USDA NASS Crop Progress · 2015–2025*
- **Narration (9 words):** "NASA's SMAP satellite shows wet springs that delay planting."
- **Subtitle (2 lines):**
  - `NASA's SMAP satellite shows`
  - `wet springs that delay planting.`

## Shot 5 — 0:15 to 0:18 · Checking the data

- **On screen:** `docs/demo/fig/fig6_lluvia_oh_ne_mn.png`, full width, the three panel titles readable.
- **On-screen text:** **Monthly rain by county, GPM IMERG vs NASA POWER: r = 0.94–0.96**
- **Small credit:** *GPM IMERG Final V07 via the NASA POWER API · two NASA products compared with each other,
  not with rain gauges · 83,616 county-months*
- **Narration (9 words):** "We cross-check every source, and say where they differ."
- **Subtitle (2 lines):**
  - `We cross-check every source,`
  - `and say where they differ.`
- **Do not say "validated against gauges"** here: the gauge comparison (PRISM, CoCoRaHS) is for Iowa, Illinois
  and Indiana and is not in a published release yet (`slides.md`, slide 6).

## Shot 6 — 0:18 to 0:25 · [ML] Three rotations compared

**[ML] — this shot is for the ML team. This repo does not train models and puts no model numbers here.**

- **What the ML team should show** (from the challenge text, `space_apps_criterios.md` §3): one example county
  or field, and **at least three strategies**, including the existing one: corn–soybean, continuous corn and a
  diversified rotation (wheat, oats or alfalfa). For each one, a **range** (not a single number), the evidence
  behind it, and its gaps or risks for local review.
- **Placeholder until then:** a three-column card with the rotation names and the text "results: [ML]". Do not
  publish the video with the placeholder.
- **On-screen text:** **[ML: card titles and ranges]**
- **Narration (11 words, keep or adapt):** "Pick a field, compare three rotations, with ranges, evidence and risks."
- **Subtitle (2 lines):**
  - `Pick a field, compare three rotations,`
  - `with ranges, evidence and risks.`
- **Data credit (for the ML team to adjust):** *Model inputs: NASA POWER, GPM IMERG, SMAP, MODIS · USDA NASS ·
  USDA NRCS SSURGO*

## Shot 7 — 0:25 to 0:30 · Credits and closing

- **On screen:** plain-text card, no logos.
- **On-screen text:**
  - **Built on open NASA data:** POWER · GPM IMERG (via POWER) · SMAP · GRACE-DA-DM · MODIS · NLDAS-2 · NASADEM
  - *+ USDA NASS, NRCS, ERS · 268 counties published (OH, NE, MN), 2000–2025*
  - <repo URL> (the public GitHub URL of this repository)
- **Narration (13 words):** "Open NASA data, an open pipeline, and the farmer still makes the call."
- **Subtitle (2 lines):**
  - `Open NASA data, an open pipeline,`
  - `and the farmer still makes the call.`
- The list has the 7 NASA product families inside the published release (`coverage.md`, "NASA products in the
  data"; GPM IMERG Final and Late count as one). Add ECOSTRESS and HLS only if their releases are published
  before submitting.

---

## Narration, full text (71 words)

> We're team [TBD]. This is [project name]. One dry summer, like 2012, cuts corn yields across whole states. We
> map, pixel by pixel, which rotation every county really runs. NASA's SMAP satellite shows wet springs that
> delay planting. We cross-check every source, and say where they differ. Pick a field, compare three
> rotations, with ranges, evidence and risks. Open NASA data, an open pipeline, and the farmer still makes the
> call.

## Subtitles (`demo_en.srt` draft)

At most 7 words per line, at least 2 s on screen. Replace `[TBD]` before burning them in.

```
1
00:00:00,000 --> 00:00:03,000
We're team [TBD].
This is [project name].

2
00:00:03,000 --> 00:00:07,000
One dry summer, like 2012,
cuts corn yields across whole states.

3
00:00:07,000 --> 00:00:11,000
We map, pixel by pixel,
which rotation every county really runs.

4
00:00:11,000 --> 00:00:15,000
NASA's SMAP satellite shows
wet springs that delay planting.

5
00:00:15,000 --> 00:00:18,000
We cross-check every source,
and say where they differ.

6
00:00:18,000 --> 00:00:25,000
Pick a field, compare three rotations,
with ranges, evidence and risks.

7
00:00:25,000 --> 00:00:30,000
Open NASA data, an open pipeline,
and the farmer still makes the call.
```

Burn them in (from the `field-shift-video` skill):

```
ffmpeg -i demo.mp4 -vf subtitles=demo_en.srt -c:v libx264 -preset veryfast -crf 20 -c:a copy demo_final.mp4
```

## How each judging criterion shows up

| Criterion | Where in the video |
|---|---|
| **Impact** | Shot 2 (a drought year cuts yields across three states), shot 4 (wet springs delay planting), shot 7 (farmers decide) |
| **Creativity** | Shot 3 (real rotations read pixel by pixel from 30 m crop maps), shot 6 [ML] |
| **Validity** | Shot 5 (two independent NASA rainfall products agree, r = 0.94–0.96, and we say where they differ), shot 6 ranges |
| **Relevance** | Shots 4, 5 and 7 (NASA SMAP, GPM IMERG, POWER at the core); shot 3 (the existing rotation); shot 6 (≥ 3 rotations, as the challenge asks) |
| **Presentation** | 7 shots, one idea each, ≤ 30 s, subtitles ≤ 7 words per line |

## Production notes

- 1920×1080, 30 fps, H.264 MP4. The PNGs are wide (fig6 is 3 panels): fit to width and zoom only where the
  script says so. Move the cursor slowly.
- Keep each figure's own caption (it says "Only Ohio, Nebraska and Minnesota") visible for at least one second,
  or keep the short credit line from the script on screen for the whole shot.
- Royalty-free music only, quiet under the voice. Credit it in the project page References.
- Check the final cut on a phone, then upload to a public link (YouTube, Vimeo or Drive) and open it in a
  private window.
- Backup shots, if one of the above does not read well on a phone: `fig2_ndvi_max_vs_yield_oh_ne_mn.png`
  (MODIS peak NDVI vs yield, for shot 4 or 5) and `fig1_corn_yield_july_rain_oh_ne_mn.png` (yield vs July rain
  from NASA POWER, for shot 2).
- If the IA/IL/IN, Kansas or `fieldshift_lotes_v1` releases are published before submitting, redo the numbers
  with all states (`docs/demo/coverage.py`, `docs/demo/figuras.py`) and update shots 2, 3, 4 and 7.

## Sources for every number

All numbers were recounted on 2026-11-15 from the zips (the yield, rotation, planting-date and IMERG–POWER
numbers were checked again by pro-3; the SMAP May value comes from fig3, because the `agua` zip was not local) of the published release `datos-oh-ne-mn` (in
`data/demo_zips/`, SHA-256 checked by `coverage.py`).

| Number | Where it comes from |
|---|---|
| Study-area map, solid = published release | `docs/demo/fig/fig0_mapa.png` (T094), checked 2026-11-15: only `datos-oh-ne-mn` published |
| 268 counties (OH, NE, MN), 2000–2025; 83,616 county-months in `clima_mensual.csv` | `docs/demo/coverage.md`, release table |
| 7 NASA product families in the published release | `docs/demo/coverage.md`, "NASA products in the data" (packages `clima`, `agua`, `vegetacion`, `nldas`, `suelo_terreno`) |
| Median county corn yield 138.4 bu/ac in 2012 (238 counties) vs 160.6 bu/ac in the other years (5,987 county-years in total), not detrended | `produccion_anual.csv`, `cultivo = maiz`, `rend_bu_ac`; figure fig5 |
| Corn after corn 2025, county median: OH 11.0 %, MN 23.9 %, NE 46.5 %; 266 counties | `rotacion_anual.csv`, `anio = 2025`, `pct_maiz_tras_maiz`, median by state; figure fig4 |
| Ohio 2019: May root-zone soil moisture 0.380 m³/m³ (highest of OH 2015–2025), 50 % of corn planted on day 160.0 (vs 129.1 in 2015) | `agua_mensual.csv` (`sm_rootzone_m3m3`, May, unweighted mean of Ohio counties) and `fenologia_estado.csv` (`doy_50_sembrado`, corn, `fips_estado = 39`); figure fig3 |
| IMERG vs POWER monthly rain: r = 0.95 (MN), 0.96 (NE), 0.94 (OH) | figure fig6 panel titles (`docs/demo/fig/README.md`, T095) |
