# PofBC historical health-area comparison data

Prepared 31 October 2026 for the PofBC health-history story. This package makes the **existing PGMaps health boundaries** usable as offline, explicitly modern comparison layers. It supplies a candidate selection for every label in the Auditor General's three 1997/98 administrative maps. It does **not** certify those selections as historical boundary reconstructions.

## Files and locations

| File | Purpose | Coverage |
| --- | --- | --- |
| `public/health-geography/boundary-comparison.json` | Source records, dataset manifest, candidate selections, limitations, and current-data audit summary | 52 map labels: 11 boards, 34 council/related labels, 7 societies |
| `public/health-geography/display-lha.geojson` | Offline modern LHA polygons | 89 features; 1.39 MB |
| `public/health-geography/display-hsda.geojson` | Offline modern HSDA polygons | 16 features; 1.06 MB |
| `public/health-geography/display-ha.geojson` | Offline modern geographic health-authority polygons | 5 features; 0.89 MB |
| `research/health-geography/lha-code-crosswalk-1997-scheme-to-2018.json` | Published old/new LHA number and name correspondence | 89 rows, with PDF page references |
| `research/health-geography/pgmaps-vs-official-current-{lha,hsda,ha}.json` | Per-feature current-data audit details | 89, 16, and 5 measurements |
| `scripts/build_health_boundary_comparison.py` | Download, extraction, display conversion, and optional current-data audit | Python; Shapely, pyproj, PyMuPDF |

The three display geometry files total approximately 3.33 MB. Their feature properties use `id`, `code`, `name`, `layer`, and parent authority/delivery-area codes as applicable. Codes are strings. Every geometry is EPSG:4326.

Large `current-*.geojson` WFS downloads, original `pgmaps-*.json` snapshots, the source PDF, and metadata responses are research inputs kept outside the application assets. The three small audit-detail files are checked in under `research/health-geography`. Filenames in the manifest's `currentDataAudit` records resolve relative to that research directory. Keep those files, the manifest, source URLs, build script, code crosswalk, and display files for provenance and reproducibility.

## What the comparison establishes

The original PGMaps snapshots contain the same 89 LHA, 16 HSDA, and 5 HA features as the current BC WFS service. **All feature properties matched exactly**, including identifiers and names. A projected area comparison also shows close correspondence, with differences compatible with an already simplified display dataset. This verifies that PGMaps provides useful modern comparison geometry; it does not establish its original download date or any pre-2001 equivalence.

| Layer | Feature count | Minimum intersection-over-union | Maximum intersection-over-union |
| --- | ---: | ---: | ---: |
| LHA | 89 | 0.973485 | 0.999897 |
| HSDA | 16 | 0.988342 | 0.999893 |
| HA | 5 | 0.995129 | 0.999723 |

These measurements compare the **stored original PGMaps snapshots against current official WFS geometry**, in BC Albers EPSG:3005. They do not use the additional 200 m display simplification. The manifest labels them as a current-data audit. They should not appear beside historical candidates as historical match percentages.

The official BC catalogue describes its reference data as the **2022 boundary configuration**, with earlier changes including the 2019 code/name update and some health-geography changes. PGMaps' snapshot metadata does not declare its original vintage. This package therefore distinguishes official reference configuration from unknown snapshot date.

## How to interpret historical candidates

There are three different kinds of evidence:

1. The Auditor General's contemporaneous **1997/98 administrative maps** show the 11 boards, 34 council/related labels, and 7 societies. They are vector publication artwork with no supplied geographic coordinates.
2. Statistics Canada's **January 2000 statistical regions** use 20 regional labels. The PHO's 1998 report explains that the analytical system aggregated LHAs and differed from the new administrative system, which involved boundary changes. Its regional labels do not prove equality to board or society service territories.
3. The **modern PGMaps polygons** provide a practical comparison canvas. Candidate selections use historical place names, legal constituent descriptions, the published old/new LHA code correspondence, and limited dated statistical-region correspondence.

No independently reusable georeferenced 1997 administrative polygon dataset was acquired. No historical overlap scores are computed. Every candidate explicitly has `boundaryIdentityVerified: false` and `historicalOverlapMeasured: false`.

The 18 regional candidate selections use 88 current LHAs. Nisga'a LHA 518 is shown separately: the original society map explicitly excludes Nisga'a Health Authority from North West. Neither this division nor using the modern Nisga'a edge certifies the historical legal boundaries. `historicalFeatureCodes` identifies related January 2000 statistical labels only; there is no polygon file in this package keyed by those codes.

The institutional identity of the original map's **Nisga'a Health Authority** remains unresolved against the repository's records. That row deliberately has `bodyId: null`; key it by `mapId` and `sourceLegendNumber` in the UI. It has related modern geography but no fabricated repository identity.

## Geographic findings that matter in the story

| Historical area | Modern candidate | Why automatic name matching fails |
| --- | --- | --- |
| South Cariboo Community Health Council | 100 Mile House LHA 144 | M225/1997, made 23 May 1997, renamed the council from 100 Mile House & District. Modern South Cariboo LHA 148 is a different area. |
| Northern Interior board | Burns Lake 522, Nechako 523, Prince George 524 | Current Northern Interior HSDA 52 also contains Quesnel 521; Quesnel had a separate historical council associated with Cariboo. |
| Cariboo society | 100 Mile House 144, Cariboo/Chilcotin 146, Quesnel 521, Bella Coola 336 | The candidate spans three current health authorities. It cannot be represented by a single current authority or delivery area. |
| Upper Island/Central Coast society | North Vancouver Island LHAs 431–434 plus Central Coast 337 | A Vancouver Island-only selection omits the historical mainland component. |
| North West society | Northwest LHAs except Nisga'a 518 | The original map expressly excludes Nisga'a Health Authority. The whole current Northwest HSDA 51 would wrongly fill that exclusion. |
| North Shore board | North Vancouver 331 and West Vancouver/Bowen Island 332 | Current HSDA 33 is broader. The dated statistical table combines North Shore with Coast Garibaldi; it does not separately validate the LHA 331/332 candidate. |
| North Okanagan board | 135, 136, 139, 141, 142 | The candidate crosses current Okanagan and Thompson Cariboo Shuswap delivery areas. |
| Vancouver/Richmond board | Modern Vancouver HSDA 32 plus Richmond HSDA 31 | The institution amalgamated the predecessor Vancouver and Richmond regional health boards. The two geographic labels remained separate in the 20-region statistical presentation. |
| Simon Fraser/Burnaby board | Current Fraser North HSDA 22 | The combined institution corresponds to two old statistical labels, Simon Fraser and Burnaby. |

The Nelson/Area, Arrow Lakes/Upper Slocan, Bulkley Valley, Terrace/Area, Snow Country, and Stikine councils are marked `scope-review-needed`. Their modern selections are starting points for comparison, not confirmed complete aggregates. Neither the Snow Country/Telegraph Creek union nor the Stikine candidate has been verified against the legal northern subdivisions.

## Published old/new LHA crosswalk

The Ministry of Health's 2019 Greater Nanaimo LHA profile includes **“Crosswalk of Old (1997) to New (2018) LHA Names and Numbers”**, Appendix C, printed pages 73–75 / PDF pages 75–77. The script extracts all 89 rows and records the source PDF SHA-256 and page for each row.

Source: <https://divisionsbc.ca/sites/default/files/53401/lha-profile-greater-nanaimo_2019.pdf#page=75>

The table supports identifiers and names, including old code 025 → 144 (100 Mile House), 030 → 148 (South Cariboo), 028 → 521 (Quesnel), 051 → 511 (Snow Country), 087 → 516 (Stikine), and 094 → 519 (Telegraph Creek). Its “1997” title identifies the older coding scheme. A table published in 2019 is not evidence that all listed subdivisions existed with unchanged geometry in calendar 1997.

The `HISTORICAL_LOCAL_HLTH_AREA` attribute in both downloaded modern sources is null for every LHA; it cannot supply this crosswalk.

## Reproduction

From the repository root, install the three Python dependencies into your interpreter environment:

```bash
python -m pip install shapely pyproj pymupdf
python scripts/build_health_boundary_comparison.py --fetch --audit-current
```

The script defaults to `research/health-geography/map-area-index.json`, writes the four application assets to `public/health-geography`, and writes the extracted code crosswalk to `research/health-geography`. Large source downloads stay in a system temporary cache; use `--cache-dir /path/to/stored/sources` to retain or reuse them. The script also writes the small audit-detail files from that cache into the research directory. The `--output-dir`, `--research-dir`, and `--map-index` flags can override the defaults. A build without `--fetch` reuses stored sources; a build without `--audit-current` reuses existing audit details. Downloading current upstream data later can change results and hashes.

Display conversion projects source polygons to EPSG:3005, applies 200 m Douglas–Peucker simplification with **per-feature topology preservation**, transforms to EPSG:4326, and rounds coordinates to six decimals when that preserves validity. It does not assert shared-edge topology after the extra simplification, so small seams may occur. Original PGMaps metadata reports shared-topology simplification at 50 m for LHAs, 75 m for HSDAs, and 100 m for HAs. Use the originals if their shared edges are preferred over the smaller transfer size.

The build verifies all 52 candidate rows, every selected LHA identifier, and the absence of historical-certainty flags. It also verifies that the 18 regional illustration groups select 88 distinct modern LHAs and leave Nisga'a 518 to its separate map label. These are consistency checks, not validation of historical geography.

## Primary source links

- Existing PGMaps index: <https://pgmaps.ahmadjalil.com/data/boundaries/BCMoH/index.json>
- Existing LHA geometry: <https://pgmaps.ahmadjalil.com/data/boundaries/BCMoH/simplified/local_health_areas.json>
- Existing HSDA geometry: <https://pgmaps.ahmadjalil.com/data/boundaries/BCMoH/simplified/health_service_delivery_areas.json>
- Existing HA geometry: <https://pgmaps.ahmadjalil.com/data/boundaries/BCMoH/simplified/health_authorities.json>
- Official LHA catalogue: <https://catalogue.data.gov.bc.ca/dataset/local-health-area-boundaries>
- Official HSDA catalogue: <https://catalogue.data.gov.bc.ca/dataset/health-service-delivery-area-boundaries>
- Official HA catalogue: <https://catalogue.data.gov.bc.ca/dataset/health-authority-boundaries>
- Auditor General administrative maps, PDF pages 28–30: <https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf#page=28>
- PHO 1998 Appendix G, especially printed G-2: <https://www2.gov.bc.ca/assets/gov/health/about-bc-s-health-care-system/office-of-the-provincial-health-officer/reports-publications/annual-reports/phoannual1998.pdf>
- Dated January 2000/June 2002 statistical-region correspondence: <https://www150.statcan.gc.ca/n1/pub/82-221-x/01002/4061979-eng.htm>
- 1996 board boundaries: <https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0432_1996>, <https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0441_1996>, <https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0444_1996>
- 1997 council continuation and boundary schedules (Appendix 21 retains 100 Mile House & District): <https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0087_1997>
- South Cariboo rename, M225/1997 made 23 May 1997: <https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0225_1997>
- Original December 2001 amalgamation regulation: <https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001>

Official current BC layers carry the **Open Government Licence – British Columbia** in the retrieved catalogue metadata. Preserve source attribution. The historical publication maps are separately cited; this package does not transfer restricted historical GIS data.
