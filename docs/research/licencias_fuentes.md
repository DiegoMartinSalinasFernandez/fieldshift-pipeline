# Licenses and attribution of the data sources (Copernicus/Sentinel-2 via HLS and non-NASA sources)

Pregunta: What attribution text do Copernicus / ESA require for Sentinel-2 data when we use it through NASA HLS
(`HLSS30` v2.0)? Do we need to cite anything else to present it as Space Agency Partner data in Space Apps 2026?
And what is the license of each non-NASA source of the pipeline (USDA NASS Quick Stats, CDL, CSB, SSURGO, USGS,
US Census, PRISM, CoCoRaHS): does it require a citation, and with what exact text?

Respuesta corta:

- **Sentinel-2 through HLS:** the EU *Legal notice on the use of Copernicus Sentinel Data and Service
  Information* says that whoever distributes or communicates Sentinel data to the public must name the source, and
  that when the data "have been adapted or modified" the notice is **`Contains modified Copernicus Sentinel data
  [Year]`**. HLS S30 is Sentinel-2 MSI data that NASA re-processed (atmospheric correction, BRDF/NBAR, bandpass
  adjustment, regridding), and we derive NDVI/EVI2/GCVI/NDMI from it. So the notice that applies is the "modified"
  one. Our HLS S30 data covers **2016–2025** (`docs/datasets/lotes.md`, columns `ndvi_max_s2` and
  `n_obs_jul_ago_s2`). Proposed line: **"Contains modified Copernicus Sentinel data 2016–2025, processed by NASA
  (HLS S30 v2.0)."** The year range is our adaptation: the Legal Notice only shows `[Year]`.
- **Also cite the NASA HLS product itself.** Its DOI and citation are already in `citas_nasa.md` §1.10. CMR points to
  the NASA EOSDIS Data Use Policy. Earthdata's guidance says NASA-led mission data are CC0 "unless the content is
  marked with a use restriction or license", and "data users are very strongly urged to cite the data".
- **Space Apps:** the ESA entry on the 2026 Space Agency Partners page and the challenge's "Space Agency Partner
  Resources" (Copernicus Sentinel-2, ERA5) **do not add any citation format of their own**. What Space Apps does
  require (see `space_apps_criterios.md` §1) is the "original work" checkbox: every external resource has to appear in
  the References field. So: put HLS in "NASA Data" with its DOI, and in "Space Agency Partner Data and Other
  References" put ESA Copernicus Sentinel-2 together with the Copernicus line above.
- **Non-NASA sources:** the US federal sources (NASS, CDL, USGS) say on their own pages that their data are
  **public domain**, but they ask for credit. SSURGO, CSB and Census do not state a license on the pages I opened.
  SSURGO and Census do give a citation format; CSB does not. **PRISM** allows free reproduction and distribution but
  requires name, URL and access date, plus a copyright notice on map graphics. **CoCoRaHS** is **CC BY 4.0**. Full
  table in §2.

Detalle:

Method: I downloaded each page with `curl` on 2026-11-15 and extracted the text. The quotes are copied from that
text. The only exceptions are the USGS "Copyrights and Credits" page, which returns HTTP 403 to automated
downloads and was read in its Internet Archive copy of 2026-01-05, and the Space Apps pages, which were read in
Internet Archive copies because of the TLS error already noted in `space_apps_criterios.md`.

## 1. Copernicus Sentinel-2 used through HLS (`HLSS30` v2.0)

### 1.1 What the Copernicus Legal Notice says

Source: European Commission, DG DEFIS, *Legal notice on the use of Copernicus Sentinel Data and Service
Information* (PDF linked from the Copernicus Data Space Ecosystem Terms and Conditions, §3 "Copyrights").

- Access and use: "users shall have a free, full and open access to Copernicus Sentinel Data and Service
  Information without any express or implied warranty". Allowed uses: "(a) reproduction; (b) distribution; (c)
  communication to the public; (d) adaptation, modification and combination with other data and information; (e)
  any combination of points (a) to (d)."
- When the notice is mandatory: "Where the user communicates to the public or distributes Copernicus Sentinel Data
  and Service Information, he/she shall inform the recipients of the source of that Data and Information by using
  the following notice: (1) 'Copernicus Sentinel data [Year]' for Sentinel data".
- Modified data: "Where the Copernicus Sentinel Data and Service Information have been adapted or modified, the user
  shall provide the following notice: (1) 'Contains modified Copernicus Sentinel data [Year]' for Sentinel data".
- Legal basis (footnotes of the notice): Regulation (EU) No 377/2014 and Commission Delegated Regulation (EU) No
  1159/2013, Art. 8 for the notice.

The Copernicus Data Space Ecosystem Terms and Conditions (§3) send all use of Sentinel data back to this Legal
Notice: "The access and use of Copernicus Sentinel data is available on a free, full and open basis [...] and shall
be governed by the Legal Notice on the use of Copernicus Sentinel Data and Service". The same section says the
*other* contents of the portal (texts, images of the website) are for non-commercial use only. That does not affect
us: we do not use content from the portal.

### 1.2 Why the "modified" notice applies to us

- CMR describes HLSS30 as "derived from Sentinel-2A, Sentinel-2B, and Sentinel-2C MSI data products". It also says
  the HLS algorithms apply "atmospheric correction, cloud and cloud-shadow masking, spatial co-registration and
  common gridding, illumination and view angle normalization, and spectral bandpass adjustment". That is adapted /
  modified Sentinel data.
- On top of that, the `lotes` package computes indices (`ndvi`, `evi2`, `gcvi`, `ndmi`) and annual summaries
  (`ndvi_max_s2`, `n_obs_jul_ago_s2`) from it (`docs/datasets/lotes.md`).
- We **distribute** it (Release `fieldshift_lotes_v1`) and **communicate it to the public** (demo, slides, project
  page). So the notice is mandatory, not just recommended.

Which years: in `docs/datasets/lotes.md` the HLS S30 columns `ndvi_max_s2` and `n_obs_jul_ago_s2` run from
**2016** to **2025**. Raw observations in `vegetacion_px_obs.csv` have rows with `producto = hls_s30` (1,474,898
rows, same data card). The data card also says that CMR-STAC has no S30 scenes from March to November 2015 in the
area. The Legal Notice shows a single `[Year]` and says nothing about ranges, so writing "2016–2025" is our
adaptation.

### 1.3 What HLS / NASA ask for

- CMR (`C2021957295-LPCLOUD`): `UseConstraints` → "Data Use Policy",
  https://earthdata.nasa.gov/earth-observation-data/data-use-policy. Citation (CMR `CollectionCitations`): Neigh,
  C., Ju, J., Roger, J.-C., Skakun, S., Vermote, E., Claverie, M., Dungan, J., Yin, Z., Freitag, B., & Justice, C.
  (2021). *HLS Sentinel-2 Multi-spectral Instrument Surface Reflectance Daily Global 30m v2.0*. NASA Land
  Processes Distributed Active Archive Center. https://doi.org/10.5067/HLS/HLSS30.002. This is the same as
  `citas_nasa.md` §1.10.
- Planetary Computer, collection `hls2-s30` (where 2020–2025 came from): `"license": "proprietary"`, with a link
  `rel=license` to "LP DAAC - Data Citation and Policies"
  (https://lpdaac.usgs.gov/data/data-citation-and-policies/). That URL now redirects to the Earthdata page "Data
  Use and Citation Guidance". The page says: "Unless the content is marked with a use restriction or license, data
  provided from a NASA-led mission are licensed as Creative Commons Zero (CC0). While there are no restrictions on
  the use of these data, data users are very strongly urged to cite the data used in their work products." and
  "NASA should be acknowledged as the source of the material."
- HLS User Guide v2.0 (LP DAAC PDF): I searched the text for "Copernicus", "legal notice", "cite", "citation",
  "acknowledg" and "policy". Copernicus only shows up in URLs of the Sentinel-2 spectral response functions. **The
  guide does not give any attribution text for Sentinel-2.** So the Copernicus requirement comes from the EU Legal
  Notice (§1.1), not from NASA. The NASA documents neither repeat it nor waive it.

Note on "proprietary": in the STAC spec, `proprietary` only means "see the link". The license that the link points
to is the NASA one (CC0 unless marked). The Copernicus notice is not "a use restriction" in the NASA sense: it is an
EU-law obligation that travels with Sentinel data. My reading is that **both apply**: cite NASA HLS (DOI) and add
the Copernicus notice.

### 1.4 What Space Apps asks for partner data

- Challenge page "Field Shift: Adapting Farms with NASA Data" (Internet Archive copy of 2026-11-14), section "Space
  Agency Partner Resources": "ESA (European Space Agency) Copernicus Sentinel-2: ESA: Sentinel‑2 provides freely
  accessible 10–20‑meter multispectral imagery at high revisit frequency. [...] Its higher spatial resolution
  complements Landsat and MODIS for field‑level assessments." Then ERA5. **It does not give a citation format.**
- "2026 Space Agency Partners" page (Internet Archive copy of 2026-11-10): the ESA entry only describes the agency
  ("ESA strives to make its data and discoveries accessible to all [...]") and links to esa.int. **There is no
  citation requirement there either.**
- What does apply comes from the Space Apps guides (`space_apps_criterios.md` §1 and §2): the "original work"
  checkbox (every external resource in the References field) and the "Space Agency Partner Data and Other
  References" field.
- I did not open the Space Apps Terms & Conditions (`space_apps_criterios.md` did not open them either). **[TBD]**
  for the team: check them if the project uses ESA logos. The Legal Notice only covers data, not logos.

Is it legitimate to present HLS S30 as "Space Agency Partner data"? The challenge suggests "Copernicus Sentinel-2"
and HLS S30 is Sentinel-2 MSI data (CMR: "MSI aboard Europe's Copernicus Sentinel-2A, Sentinel-2B, and
Sentinel-2C satellites"). It is fair to declare it as Sentinel-2 data **harmonized by NASA**, as long as the text
does not say we downloaded Level-1C/L2A products from ESA, because we did not. The wording below says it that way.

### 1.5 Ready-to-paste text

**Field "NASA Data"** (one line, next to the other products from `citas_nasa.md` §1):

> HLS Sentinel-2 Multi-spectral Instrument Surface Reflectance Daily Global 30m v2.0 (HLSS30), NASA LP DAAC,
> doi:10.5067/HLS/HLSS30.002 — 30 m surface reflectance for the 10 demonstration fields (`lotes` package), years
> 2016–2025.

**Field "Space Agency Partner Data and Other References":**

> ESA Copernicus Sentinel-2 MSI, used through NASA's Harmonized Landsat Sentinel-2 product (HLSS30 v2.0,
> doi:10.5067/HLS/HLSS30.002). Contains modified Copernicus Sentinel data 2016–2025.

**Slides / video / map figures that show HLS-derived pixels** (short credit line under the image):

> Contains modified Copernicus Sentinel data 2016–2025 · NASA HLS S30 v2.0

**Data card / Release `fieldshift_lotes_v1`:** the same line ("Contains modified Copernicus Sentinel data
2016–2025") in the README of the zip. This is a **proposal** for the team (it is not this task's job to touch
`docs/datasets/lotes.md` or `scripts/entregar.py`).

## 2. Licenses of the non-NASA sources

Only pages I opened on 2026-11-15. "Requires citation" distinguishes three cases: **mandatory** (the text says
"shall", "must" or makes it a condition), **requested** ("we ask", "it is requested") and **not stated**.

| Source (organization) | License / status, as the page says it | Requires citation? | Exact text the source gives | Page opened |
|---|---|---|---|---|
| **USDA NASS Quick Stats** (SURVEY and CENSUS; includes Crop Progress and Census of Agriculture) | "Most of the information available from this site is within the public domain. Public domain information on the National Agricultural Statistics Service (NASS) Web pages may be freely downloaded and reproduced." | **Requested**: "it is requested that in any subsequent use of this work, USDA-NASS be given appropriate acknowledgment." | NASS does not give a format. Proposal (ours): "USDA National Agricultural Statistics Service, Quick Stats, https://quickstats.nass.usda.gov, accessed 2026-11-DD." (the same as `citas_nasa.md` §2). The Quick Stats API also requires agreeing to the "NASS Terms of Service" to get a key. I did not open that ToS page | [NASS Citation Request](https://www.nass.usda.gov/Data_and_Statistics/Citation_Request/index.php) (last modified 05/04/2018); [Quick Stats API](https://quickstats.nass.usda.gov/api) |
| **Cropland Data Layer (CDL)** (USDA NASS) | "The USDA NASS Cropland Data Layer is considered public domain and free to redistribute." Use_Constraints: "provided to the public as is and is considered public domain and free to redistribute. The USDA NASS does not warrant any conclusions drawn from these data." Access_Constraints: none | Not mandatory. The metadata gives a citation ("How might this data set be cited?") and NASS asks for acknowledgment in general (row above) | "United States Department of Agriculture (USDA) National Agricultural Statistics Service (NASS), 20260227, Cropland Data Layer: USDA NASS, USDA NASS Marketing and Information Services Office, Washington, D.C." Online Links: https://croplandcros.scinet.usda.gov/ | [CDL metadata / FAQ](https://www.nass.usda.gov/Research_and_Science/Cropland/sarsfaqs2.php) |
| **Crop Sequence Boundaries (CSB)** (USDA NASS with ERS) | **Not stated** on the CSB page. It says it "is open source" and that it "does not contain personal identifying information" | **Not stated** | The NASS page gives no citation. `citas_nasa.md` §2 proposes the Zenodo code citation (Hunt & Beeson 2024, doi:10.5281/zenodo.14004209); I did not reopen Zenodo in this task. The NASS Citation Request request (row 1) applies because it is a NASS product | [NASS CSB](https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php) |
| **SSURGO** via Soil Data Access (USDA NRCS) | **Not stated** on the Citation page | Format given (the page is titled "Citation"; it does not say "must") | "Soil Survey Staff, Natural Resources Conservation Service, United States Department of Agriculture. Soil Survey Geographic (SSURGO) Database. Available online at https://sdmdataaccess.sc.egov.usda.gov. Accessed [month/day/year]." | [SDA Citation](https://sdmdataaccess.sc.egov.usda.gov/Citation.htm) |
| **USGS** (Landsat C2 L2, 3DEP, NLCD, NASADEM distribution) | "USGS-authored or produced data and information are considered to be in the U.S. Public Domain." Warning: "not all information, illustrations, or photographs on our site are" | **Requested**: "When using information from USGS information products, publications, or websites, we ask that proper credit be given." | "Credit: U.S. Geological Survey" (or "Department of the Interior/USGS"). For each dataset, use the DOI citations already in `citas_nasa.md` §2 (Landsat C2 L2, NLCD) | [USGS Copyrights and Credits](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits) (Internet Archive copy of 2026-01-05; the original returns HTTP 403) |
| **US Census Bureau** (Cartographic Boundary Files 2024) | **Not stated** on the citation page (no "public domain" or "copyright" in the text) | Requested in general terms: "Data users who create their own estimates using data from disseminated tables and other data should cite the Census Bureau as the source of the original data only." "Use the suggested citation if one is provided with the publication, data, code, or tool." | No example for boundary files. Components the page lists for data: author ("If no author names are attached, the U.S. Census Bureau [...] should be listed as the Author/s"), title, table or file name, date of release, persistent identifier, vintage, URL, date accessed. The analogy with TIGER/Line stays as in `citas_nasa.md` §2 | [Census, Citing our Data](https://www.census.gov/about/policies/citation.html) |
| **PRISM** (Oregon State University) | "All data (gridded, polygon, tabular, graphical) retrieved from this website or otherwise provided on the website may be freely reproduced and distributed." The same page also says: "All data and information presented through this website are protected by United States copyright laws and applicable international copyright treaties." | **Required by the Terms of Use** (worded as "should"): "When the data are used, any description should clearly and prominently state, at a minimum, our name, URL, and the date of data access." On maps: "Map graphics may be freely reproduced and distributed, as long as the PRISM Group copyright notice, URL, and the date of map creation are reproduced in full." | Data: "PRISM Group, Oregon State University, https://prism.oregonstate.edu, accessed 16 Dec 2025." (the page's example; use our access date). Maps: "Copyright ©<year>, PRISM Group, Oregon State University, https://prism.oregonstate.edu, map created <date>." | [PRISM Terms of Use](https://prism.oregonstate.edu/terms/) |
| **CoCoRaHS** (Colorado Climate Center) | "Unless otherwise noted, all CoCoRaHS content and data are released under a Creative Commons Attribution 4.0 License." | **Mandatory** under CC BY 4.0 (attribution is a condition of the license). The page also asks: "we ask that everyone who uses CoCoRaHS data to please acknowledge its source when displaying it." | No fixed format. Proposal (ours): "Community Collaborative Rain, Hail and Snow Network (CoCoRaHS), Colorado Climate Center, https://www.cocorahs.org, accessed 2026-11-DD. Licensed under CC BY 4.0." | [CoCoRaHS Data Usage Policy](https://www.cocorahs.org/content.aspx?page=datausagepolicy) |

Notes on the table:

- **PRISM and the demo:** if the satellite-vs-ground scatter plot (`space_apps_criterios.md` §6, point 5) shows
  PRISM values, the caption needs "PRISM Group, Oregon State University, https://prism.oregonstate.edu, accessed
  [date]". The "map graphics" copyright line only applies if we reuse a PRISM map image; we make our own figures
  from the data.
- **CoCoRaHS and CC BY 4.0:** this is the only source with a formal license that has conditions. Besides the
  attribution, CC BY 4.0 asks you to link the license and say whether changes were made. Our monthly aggregation
  (`validacion_mensual`) is a change. Suggested: "Data: CoCoRaHS (CC BY 4.0), aggregated to county-month by the
  team."
- **Federal sources and the public repo:** NASS, CDL and USGS can be redistributed in the Releases with no
  restriction. SSURGO, CSB and Census do not state a license on the pages I opened. They are US government works,
  and I am not adding a "public domain" claim beyond what each page says. That is a reading, not a quote.
- **Access dates:** the formats ask for the access date. Use the `fecha_descarga` of `manifest.csv` for each
  package. **[TBD]** for the team: I did not look up those dates in this task.

## 3. Summary for the submission form

Credit lines that are **mandatory** in figures or the demo when that source appears:
1. HLS S30 / Sentinel-2: "Contains modified Copernicus Sentinel data 2016–2025" (EU Legal Notice).
2. PRISM: name, URL and access date.
3. CoCoRaHS: credit + CC BY 4.0.

**Requested** (not legally required, but needed for the "original work" checkbox anyway): USDA NASS (Quick Stats,
CDL, CSB), USDA NRCS (SSURGO), USGS, US Census Bureau. Texts in §2.

Fuentes:
- [European Commission, Legal notice on the use of Copernicus Sentinel Data and Service Information (PDF)](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice), consultado 2026-11-15
- [Copernicus Data Space Ecosystem, Terms and Conditions](https://dataspace.copernicus.eu/terms-and-conditions), consultado 2026-11-15
- [CMR, HLSS30 v2.0 (`C2021957295-LPCLOUD`, UMM-JSON)](https://cmr.earthdata.nasa.gov/search/concepts/C2021957295-LPCLOUD.umm_json), consultado 2026-11-15
- [Planetary Computer STAC, collection `hls2-s30`](https://planetarycomputer.microsoft.com/api/stac/v1/collections/hls2-s30), consultado 2026-11-15
- [LP DAAC Data Citation and Policies → Earthdata "Data Use and Citation Guidance"](https://lpdaac.usgs.gov/data/data-citation-and-policies/), consultado 2026-11-15
- [HLS User Guide v2.0 (LP DAAC, PDF)](https://lpdaac.usgs.gov/documents/1698/HLS_User_Guide_V2.pdf), consultado 2026-11-15
- [Field Shift: Adapting Farms with NASA Data (Internet Archive copy of 2026-11-14)](https://web.archive.org/web/20261114231258/https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/), consultado 2026-11-15
- [2026 Space Agency Partners (Internet Archive copy of 2026-11-10)](https://web.archive.org/web/20261110231535/https://www.spaceappschallenge.org/2026/space-agency-partners/), consultado 2026-11-15
- [USDA NASS, Citation Request](https://www.nass.usda.gov/Data_and_Statistics/Citation_Request/index.php), consultado 2026-11-15
- [USDA NASS, Quick Stats API](https://quickstats.nass.usda.gov/api), consultado 2026-11-15
- [USDA NASS, Cropland Data Layer metadata / FAQ](https://www.nass.usda.gov/Research_and_Science/Cropland/sarsfaqs2.php), consultado 2026-11-15
- [USDA NASS, Crop Sequence Boundaries](https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php), consultado 2026-11-15
- [USDA NRCS, Soil Data Access — Citation](https://sdmdataaccess.sc.egov.usda.gov/Citation.htm), consultado 2026-11-15
- [USGS, Copyrights and Credits (Internet Archive copy of 2026-01-05)](https://web.archive.org/web/20260105204047/https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits), consultado 2026-11-15
- [US Census Bureau, Citing our Data, Tools, Technical Documents and Research](https://www.census.gov/about/policies/citation.html), consultado 2026-11-15
- [PRISM, Terms of Use](https://prism.oregonstate.edu/terms/), consultado 2026-11-15
- [CoCoRaHS, Data Usage Policy](https://www.cocorahs.org/content.aspx?page=datausagepolicy), consultado 2026-11-15
- Repo: `docs/datasets/lotes.md` (HLS S30 years and row counts), `docs/research/citas_nasa.md`, `docs/research/space_apps_criterios.md`
- Not opened: Space Apps Terms & Conditions, the NASS Terms of Service of the Quick Stats API, the Zenodo record of CSB (taken from `citas_nasa.md`), and the CC BY 4.0 legal code (the conditions in §2 notes are the well-known terms of that license, not quoted from it).

Confianza:
- **Alta** for the Copernicus notice text and when it is mandatory: copied from the EU Legal Notice PDF.
- **Alta** for the license texts of NASS, CDL, SSURGO, USGS, PRISM and CoCoRaHS: copied from their pages (USGS
  from an archive copy of 2026-01-05).
- **Media** for applying the "modified" notice with the range "2016–2025": the notice is clear about modified data,
  but the year range is our adaptation, and the years come from the `lotes` data card.
- **Media** for "no extra citation required by Space Apps for partner data": the two Space Apps pages I read do not
  ask for one, but I did not read the Terms & Conditions.
- **Baja** for the license status of CSB and Census boundary files: their pages do not state one.

Impacto:
- No change to `config/` or `src/`.
- Space Apps form: "NASA Data" and "Space Agency Partner Data and Other References" fields (§1.5 and §3).
- Demo / slides (`field-shift-video` skill) and frontend: credit lines under figures with HLS, PRISM or CoCoRaHS.
- Proposal: add the Copernicus line to `docs/datasets/lotes.md` and to the README of the `fieldshift_lotes_v1`
  Release, and the CC BY 4.0 note to `docs/datasets/validacion.md`. Done in another task.
- Closes the "not verified" item of `space_apps_criterios.md` §5 and §Confianza on the Copernicus attribution.
