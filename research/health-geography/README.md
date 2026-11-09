# Historical health geography

## Current boundaries (November 2026)

The health-map page (`?view=health-map`) now shows one boundary per organization on five maps: the 11 regional boards, 34 community councils and 7 service societies of 1997, the 20 Statistics Canada regions of 2000, and the five health authorities as they stood on 12 December 2001. They are built by one script:

```sh
python3 -m venv /tmp/pofbc-boundaries
/tmp/pofbc-boundaries/bin/pip install -r research/health-geography/requirements-boundaries.txt
/tmp/pofbc-boundaries/bin/python scripts/build_health_boundaries.py
node --test src/health/*.test.js
```

1. **Georectification.** Each printed map panel — the three OAG exhibits, both panels of the board inset, and the Statistics Canada map and its inset — is registered to the modern LHA linework (coast, provincial border and LHA edges). Seeds in [georectification-settings.json](georectification-settings.json) (provincial corners, printed city dots, two Lower Mainland landmarks) only give a starting position. An iterative closest-point fit then matches every sampled printed boundary point to the nearest modern edge and fits an affine, quadratic and cubic polynomial, plus a smoothed thin-plate spline on the main maps. Held-out median error, measured on map blocks left out of the fit, is 0.2–0.7 km per panel, against 1.0–1.8 km for the earlier three-corner affine.
2. **LHA snap.** Every LHA at least half inside a registered printed region belongs to it. [boundary-decisions.json](boundary-decisions.json) records the only two exceptions (New Westminster in Simon Fraser; the Southern Gulf Islands in Capital), each with its legal evidence.
3. **Checks.** Nothing in the method forces it, but the boards plus councils cover all 89 LHAs exactly once, the 20 statistical regions do too, and each society equals the union of its councils. The 2001 authorities are the union of the boards and councils whose lineage records name them as successor, which keeps Bella Coola in Interior and the Central Coast in Vancouver Island until their 2002 transfers.

Outputs in `public/health-geography/`: `historical-boundaries.geojson` (all 77, for analysis), `boundaries/*.geojson` (display, per map, with organization lineage), `rectified/*.geojson` (the printed maps warped onto modern geography), and `georectification.json` (panel accuracy and every region's LHA shares). The script also writes `src/health/healthBoundaries.generated.js`.

The georectified snap corrected two earlier working choices: Statistics Canada region 08 Simon Fraser contains New Westminster and region 17 is Burnaby alone (the earlier statistical illustration had them swapped), and Snow Country, Stikine and Upper Skeena now resolve cleanly to LHAs 511, 516 + 519 and 513.

### Inputs

| File | Role |
| --- | --- |
| `public/health-geography/maps/*.pdf` | The OAG excerpt (Exhibits 3–5) and the Statistics Canada map; checksums in `georectification-settings.json` |
| `public/health-geography/display-lha.geojson` | The 89 modern LHAs used as building blocks and registration reference. Its `metadata` records the PGMaps source URL, checksum and simplification |
| `georectification-settings.json` | Map panels, clip areas, seeds, inset drawing ids and the StatCan legend swatches |
| `rectification-controls.json` | Which printed paths make up each board and society region |
| `council-tracing.json` | Seeds that separate the 34 council areas on Exhibit 4 |
| `boundary-decisions.json` | The two reviewed exceptions to the LHA snap |
| `map-area-index.json`, `../history/bodies-health-lineage.json` | Printed labels and their organizations; `npm run build:health-map` turns them into `public/health-geography/catalogue.json` |
| `statcan-2000-map.json` | StatCan map provenance, licence and region legend |

`1995-twenty-board-boundaries.json`, `1996-regional-board-boundaries.json`, `boundary-definition-evidence.json` and `lha-code-crosswalk-1997-scheme-to-2018.json` index the legal boundary descriptions and LHA code changes cited by the decisions.

### Removed in November 2026

The first, exploratory pipeline was removed once the georectified boundaries replaced it. Everything is recoverable from git history (the last commit containing it is the parent of the removal commit). It comprised:

- **Three-corner affine registration** (`scripts/rectify_health_maps.py`, `rectification.json`, `registered-source-*.geojson`, `rectification-README.md`): superseded by the many-point fit, which cut typical error from 1.0–1.8 km to 0.2–0.7 km and made the hand-applied 5 km Vancouver/Richmond shift (`vancouver-richmond-*`, `adjusted-source-traces.geojson`) unnecessary.
- **Working estimates** (`scripts/build_health_estimates.py`, `best-estimates.geojson`, `source-drawn-estimates.geojson`, `statistical-region-estimates.geojson`, `estimates-index.json`, `estimate-catalogue.csv`, `estimate-decisions.json`, `estimate-results.json`, `boundary-estimates.md`): superseded by `historical-boundaries.geojson`. The old statistical layer had New Westminster and Burnaby swapped.
- **Modern comparison layers and audit** (`scripts/build_health_boundary_comparison.py`, `boundary-comparison.json`, `display-ha/hsda/municipalities/regional-districts/school-districts.geojson`, `pgmaps-vs-official-current-*.json`, `boundary-comparison-README.md`). That audit found the PGMaps LHA snapshot matches the official 2022-configuration WFS (minimum per-LHA IoU 0.973) with identical codes and names.
- **GeoLibre review package** (`scripts/build_health_geolibre.py`, `import_health_gcps.py`, `health-geolibre-controls.mjs`, `public/health-geography/geolibre/`, the 8 MB `health-geolibre-review.zip`, `vendor/geolibre-georeference`, `geolibre-workflow.md`).
- **Comparison viewer** (`scripts/build-health-comparisons.mjs`, `comparisons.html`, `comparison-examples.*`).
- **Evidence review and records list** (`scripts/health-map-research.mjs`, `evidence-plan.json`, `research-plan.json`, `records-to-obtain.md`): unsent request drafts for historical GIS and society schedules.
- **Page artwork and story frame**: SVG exports of the four maps (the PDFs remain), the six-chapter story components and the `vendor/geo-toolkit` submodule they used.

## Original map sources and dates

The principal source is the BC Auditor General's *A Review of Governance and Accountability in the Regionalization of Health Services*, **1997/98 Report 3, published March 1998**. The maps credit the Ministry of Health and Ministry Responsible for Seniors. The current website's `2024/08` upload path is not the report's publication date.

| Map | Original location | Coverage | Repository copy (`public/health-geography/maps/`) |
| --- | --- | --- | --- |
| Regional Health Boards, Exhibit 3 | [PDF page 28 / printed page 24](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf#page=28) | 11 labels | `BC-health-area-maps-1997-98.pdf`, page 1 |
| Community Health Councils, Exhibit 4 | [PDF page 29 / printed page 25](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf#page=29) | 34 council and related-area labels | `BC-health-area-maps-1997-98.pdf`, page 2 |
| Community Health Services Societies, Exhibit 5 | [PDF page 30 / printed page 26](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf#page=30) | 7 labels | `BC-health-area-maps-1997-98.pdf`, page 3 |
| Twenty statistical health regions | [Statistics Canada, one-page PDF](https://www150.statcan.gc.ca/n1/pub/82-221-x/00401/images/pdf/4195184-eng.pdf) | 20 analytical regions | `statcan-bc-health-regions-2000-map.pdf` |

The OAG maps describe the 1997 restructuring as published in 1998. They are not verified snapshots of every boundary immediately before the December 2001 consolidation. Later amendments have not been exhaustively reconciled with their artwork.

The Statistics Canada map is linked from [*Health Indicators*, April 2001](https://www150.statcan.gc.ca/n1/pub/82-221-x/00401/4149085-eng.htm). **Use “Twenty statistical health regions — published April 2001” as its caption.** The map itself prints no boundary date. Its `2000` filename identifies the historical statistical framework; it does not establish an exact January 2000 legal-board boundary date. The [2002 statistical correspondence table](https://www150.statcan.gc.ca/n1/pub/82-221-x/01002/4061979-eng.htm) independently identifies January 2000 and June 2002 statistical vintages.

[PHO Annual Report 1998, Appendix G](https://www2.gov.bc.ca/assets/gov/health/about-bc-s-health-care-system/office-of-the-provincial-health-officer/reports-publications/annual-reports/phoannual1998.pdf) explains why those twenty analytical regions differ from the reorganized administrative system. They aggregate local health areas and roughly correspond to former health units. Vancouver/Richmond and Simon Fraser/Burnaby each remained two labels in the statistical presentation after their predecessor boards were combined.

## Legal definitions are separate evidence

The earlier twenty-board structure is indexed in [1995-twenty-board-boundaries.json](1995-twenty-board-boundaries.json). [M597/1995](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0597_1995), made 6 December 1995, lists the twenty boards on PDF page 2 and gives written boundary descriptions on pages 3–58. These are legal descriptions, not twenty separately recovered maps. Similar names in the later statistical map do not prove identical legal territories.

The eleven reorganized board definitions are indexed, with page locators, in [1996-regional-board-boundaries.json](1996-regional-board-boundaries.json):

| Original order | Board definitions covered |
| --- | --- |
| [M432/1996](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0432_1996) | North Shore; Simon Fraser/Burnaby; South Okanagan Similkameen |
| [M441/1996](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0441_1996) | Fraser Valley; South Fraser Valley; Thompson; Central Vancouver Island; Vancouver/Richmond; Capital |
| [M444/1996](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0444_1996) | Northern Interior; North Okanagan |

Order-made dates, deposit dates, publication dates, and effective dates answer different questions. Preserve that distinction. For example, the OAG North Okanagan footnote gives 12 September 1997 for a rename, while the repository records M315/1997's made date as 3 September and says its deposit date is unrecovered. The index retains this discrepancy rather than substituting one date for the other.

## Coverage and identity

[map-area-index.json](map-area-index.json) preserves **52 source labels: 11 boards, 34 council/related labels, and 7 societies**. It links **51 labels to confirmed institutional identities** in `research/history/bodies-health-lineage.json`. The remaining label, **Nisga'a Health Authority**, has related geography but unresolved equivalence to the repository's institutional records; its `repoBodyId` remains null.

An identity match connects a historical name or alias to a continuing institution. It does **not** confirm its boundary, establish unchanged geography through 2001, or validate a modern polygon. Keep original legend numbers and labels alongside repository IDs. Councils and societies administered different services and their territories overlap; do not dissolve all three map categories into mutually exclusive authorities.

The PDFs and SVGs preserve the published maps, including insets and historical names. Their original vector paths use page coordinates, not a geographic projection. No independently reusable historical administrative GIS dataset was acquired. The follow-up registration measures approximate publication-drawing overlap separately, without establishing historical legal-boundary identity. Legal reconstruction still requires tracing dated descriptions against appropriate geographic evidence and checking intervening amendments.

## Geographic traps to preserve in the interface

| Area | Interpretation required |
| --- | --- |
| South Cariboo council | [M225/1997](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0225_1997), made 23 May 1997, renamed **100 Mile House & District** to South Cariboo Community Health Council. Its boundary is modern 100 Mile House LHA 144; modern South Cariboo LHA 148 belongs to a different comparison. M87/1997 continues the old name and is not the rename instrument. |
| North West society | Exhibit 5 explicitly **excludes Nisga'a Health Authority**. The comparison excludes modern Nisga'a LHA 518 and does not select the whole Northwest HSDA. That modern exclusion is still not a verified historical edge. |
| Northern Interior | The boundary uses Burns Lake, Nechako and Prince George. The current HSDA also includes Quesnel, which had a separate historical council associated with Cariboo. |
| Cariboo | Its boundary includes 100 Mile House, Cariboo/Chilcotin, Quesnel and Bella Coola; those modern LHAs span three current authorities. |
| Upper Island/Central Coast | The source includes a mainland component. North Vancouver Island alone omits it. |
| North Shore and North Okanagan | North Shore's boundary includes Bowen Island but is narrower than today's North Shore/Coast Garibaldi HSDA. North Okanagan's boundary spans today's Okanagan and Thompson Cariboo Shuswap HSDAs. |
| Northern and Kootenay councils | Snow Country, Stikine, Terrace, Bulkley Valley, Nelson and Arrow Lakes selections retain explicit scope-review notes. Modern names are insufficient to confirm all historical subdivisions. |

The [2019 LHA code/name crosswalk](lha-code-crosswalk-1997-scheme-to-2018.json) supports identifier translation. Its title's “Old (1997)” describes the coding scheme; a 2019 table does not prove unchanged boundaries or subdivision existence in calendar 1997.
