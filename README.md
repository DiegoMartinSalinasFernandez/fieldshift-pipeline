# Field Shift — data pipeline

Data pipeline for **Field Shift**, our project for the NASA Space Apps Challenge 2026, challenge
*"Field Shift: Adapting Farms with NASA Data"*. Field Shift is a decision-support tool that helps farmers compare
crop-rotation strategies using NASA Earth observations, soil information and crop statistics. It supports, and
does not replace, the farmer's own judgment.

**What this repository does:** it downloads, cleans and joins public NASA and USDA data **by county and year**
for the US Corn Belt, and writes them as CSV tables ready for the team that builds the machine-learning model.
**This repository does not train any model.**

| | |
|---|---|
| Area | 7 Corn Belt states, all counties (666): IA, IL, IN, OH, NE, MN, KS (`config/config.yaml`). A third batch (MO, WI, SD) was approved on 2026-11-15 and is in progress (no published release yet on 2026-11-15, see [`docs/demo/coverage.md`](docs/demo/coverage.md)) |
| Period | 2000–2025; crop rotations from 2008 (first year the Cropland Data Layer covers the whole US) |
| Units | County (5-digit FIPS) × year; monthly, daily and 8/16-day files where relevant |
| Crops | Corn, soybean, winter wheat, oats, alfalfa, other hay; cover crops as a practice (Census of Agriculture) |
| Extra delivery | `lotes`: 30 m pixels inside 10 demonstration fields, for within-field zones (separate release `fieldshift_lotes_v1`) |

**NASA data used** (full list, versions and DOIs in [`docs/research/citas_nasa.md`](docs/research/citas_nasa.md)):
NASA POWER, GPM IMERG, SMAP L4, GRACE-DA-DM, MODIS MOD13Q1 and MOD11A2, NLDAS-2 Noah, NASADEM, ECOSTRESS,
HLS (Sentinel-2 part, derived from ESA Copernicus Sentinel-2) and Landsat Collection 2 (USGS–NASA).
Non-NASA sources: USDA NASS (Quick Stats, Crop Progress, Census, Cropland Data Layer, Crop Sequence Boundaries),
USDA ERS, USDA NRCS SSURGO, USGS 3DEP and Annual NLCD, US Census boundaries, and PRISM and CoCoRaHS (only to
validate NASA rain and temperature against ground data).

## Where to find things

- **English data summary** (sources, columns, quality control, limitations):
  [`docs/datasets/README_en.md`](docs/datasets/README_en.md).
- **Processed data:** not stored in git. They are published as zip files in the [Releases](../../releases),
  one release per group of states (`datos-<states>`, e.g. `datos-ks`), one zip per package with its `.sha256`,
  data card and `manifest.csv` (one row per downloaded file: source, product, version, date, query).
  Published so far (2026-11-15): [`datos-oh-ne-mn`](../../releases/tag/datos-oh-ne-mn) (Ohio, Nebraska,
  Minnesota; 268 counties, 2000–2025). The other groups of states are in progress. Counted rows, columns and
  years per file: [`docs/demo/coverage.md`](docs/demo/coverage.md).
- **Data cards** (column dictionary, units, real coverage, % missing, assumptions, known problems; in Spanish):
  [`docs/datasets/<package>.md`](docs/datasets). Merged tables: [`docs/datasets/merge.md`](docs/datasets/merge.md)
  (run of 2026-11-14, first batch IA/IL/IN: `tabla_anual.csv` 25,070 rows × 73 columns, `tabla_mensual.csv`
  91,416 rows × 48 columns). Sizes for all 7 states: [TBD].
- **Satellite vs ground validation:** [`docs/datasets/validacion.md`](docs/datasets/validacion.md) (summary
  table in §5.3 of `README_en.md`).
- **Citations:** [`docs/research/citas_nasa.md`](docs/research/citas_nasa.md). NASA POWER has no DOI; please
  cite it as: *"The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research
  Center's Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science
  Division."*
- **Research notes** behind each decision: [`docs/research/`](docs/research).

## How to run

**Requirements:** Git and Python 3.11 (3.12 also works for the tests and package 0). No system GDAL is needed:
`rasterio`, `pyogrio` and `pyproj` install as wheels that bundle it. On Ubuntu/Debian the command is `python3`
(there is no `python`) and `venv` may need `sudo apt install python3-venv`; with [uv](https://docs.astral.sh/uv/)
you can get 3.11 without touching the system Python. The install takes about 1 GB on disk and takes a
couple of minutes.

**Quick check (no credentials, ~12 MB download):** tests and package 0 for one state.

```bash
git clone <this repository URL> fieldshift-pipeline && cd fieldshift-pipeline
python3.11 -m venv .venv               # or: uv venv --python 3.11
.venv/bin/pip install -r requirements.txt   # or: uv pip install -r requirements.txt
.venv/bin/python -m pytest tests/      # ~10 s, no network
export FIELDSHIFT_ESTADOS=IN           # one state; without it, every state in config/config.yaml
.venv/bin/python -X utf8 src/base/download.py   # US Census counties -> data/raw/base/
.venv/bin/python -X utf8 src/base/process.py    # -> data/reference/condados.csv (92 rows), anios.csv
```

On Windows use `.venv\Scripts\python` instead of `.venv/bin/python`, `set FIELDSHIFT_ESTADOS=IN` (cmd) or
`$env:FIELDSHIFT_ESTADOS="IN"` (PowerShell), and keep `-X utf8`: without it the Spanish console messages break.
Run everything from the repository root. `FIELDSHIFT_ESTADOS` only accepts states listed in
`config/config.yaml` (two-letter codes, comma-separated).

**Full pipeline.** Credentials are needed only from here on: a free
[NASA Earthdata](https://urs.earthdata.nasa.gov) login in `~/.netrc` (`_netrc` on Windows) for the packages
that read from Earthdata (`nldas`, `ecostress`, `lotes`; `clima` and `agua` do not need it); other keys (e.g. the optional `NASS_API_KEY`) in `.env`, which is git-ignored.
Some packages download several GB per state and take hours; the processed results are already in the Releases.

```bash
.venv/bin/python -X utf8 src/<package>/download.py   # clima, cultivos, agua, vegetacion, suelo_terreno, nldas, ...
.venv/bin/python -X utf8 src/<package>/process.py    # -> data/processed/<package>/*.csv
.venv/bin/python -X utf8 src/merge.py                # -> tabla_anual.csv, tabla_mensual.csv
.venv/bin/python -X utf8 scripts/entregar.py <package>  # team only: publishes to a Release (needs `gh` with write access)
```

Downloads are idempotent (files already in `data/raw/` are not downloaded again) and `data/raw/` is never
modified. Every processed CSV passes `validar_csv()` (`src/common/`): unique keys, valid FIPS, physical ranges,
missing values as empty cells (never 0 or −9999). Rules and the CSV contract are in [`CLAUDE.md`](CLAUDE.md)
(Spanish).

## Use of AI

Most of the code in this repository, the data cards and the research notes were written by AI agents (Anthropic
Claude, through Claude Code), working on tasks defined and reviewed by the team (see
[`MAQUINAS.md`](MAQUINAS.md) and [`coordinacion/`](coordinacion)). **The data are not generated by AI**: every
value is downloaded from the original NASA, USDA and USGS sources listed above, and each downloaded file is
recorded in `manifest.csv`. Agents are instructed never to fill gaps with assumed values; missing data stay
empty and are documented in the data cards. The idea of the tool comes from the team.

---

# fieldshift-pipeline (castellano)

Pipeline de datos de **Field Shift** para NASA Space Apps Challenge 2026, desafío *"Field Shift: Adapting
Farms with NASA Data"*. Baja, limpia y estructura en CSV datos de la NASA y del USDA por condado y año para el
Corn Belt de EE.UU. (Iowa, Illinois, Indiana, Ohio, Nebraska, Minnesota y Kansas, 2000–2025), listos para que
el equipo de machine learning compare rotaciones de cultivos. Este repo no entrena modelos.

Viene del repo ResearchAgent, donde se armó la primera tanda (Iowa, Illinois e Indiana). Acá trabajan varias
máquinas a la vez, cada una con sus estados y sus tareas.

- **Para sumarte o trabajar:** [MAQUINAS.md](MAQUINAS.md).
- **Reglas, contrato de los CSV y paquetes:** [CLAUDE.md](CLAUDE.md).
- **Qué hay que hacer:** `python scripts/tareas.py listar`, o la carpeta [coordinacion/tareas](coordinacion/tareas).
- **Datos procesados:** en los [Releases](../../releases), uno por grupo de estados.

Las fuentes son de dominio público (NASA POWER, GPM IMERG, MODIS, SMAP, GRACE-DA-DM, NLDAS, ECOSTRESS, USDA
NASS, Cropland Data Layer, SSURGO, NASADEM, Annual NLCD, ERS). Cada data card en `docs/datasets/` dice de
dónde sale cada columna.

## Uso de IA

La mayor parte del código de este repositorio, los data cards y las notas de research los escribieron agentes de
IA (Anthropic Claude, mediante Claude Code), trabajando en tareas definidas y revisadas por el equipo (ver
[`MAQUINAS.md`](MAQUINAS.md) y [`coordinacion/`](coordinacion)). **Los datos no los genera la IA**: cada valor se
baja de las fuentes originales de la NASA, el USDA y el USGS listadas arriba, y cada archivo bajado queda
registrado en `manifest.csv`. Los agentes tienen la instrucción de no rellenar huecos con valores supuestos: los
faltantes quedan vacíos y se documentan en los data cards. La idea de la herramienta es del equipo.
