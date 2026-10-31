# Historical health geography

This directory records the evidence behind PofBC's health-history story and its links between published map labels, institutional records, and modern comparison areas. The original maps remain source artwork; the selectable PGMaps polygons are modern geographic candidates. See [boundary-comparison-README.md](boundary-comparison-README.md) for the detailed geometry method, source manifest, audit, and reconstruction limits.

## Original map sources and dates

The principal source is the BC Auditor General's *A Review of Governance and Accountability in the Regionalization of Health Services*, **1997/98 Report 3, published March 1998**. The maps credit the Ministry of Health and Ministry Responsible for Seniors. The current website's `2024/08` upload path is not the report's publication date.

| Map | Original location | Coverage | Repository asset |
| --- | --- | --- | --- |
| Regional Health Boards, Exhibit 3 | [PDF page 28 / printed page 24](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf#page=28) | 11 labels | `regional-health-boards-1997-98.svg` |
| Community Health Councils, Exhibit 4 | [PDF page 29 / printed page 25](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf#page=29) | 34 council and related-area labels | `community-health-councils-1997-98.svg` |
| Community Health Services Societies, Exhibit 5 | [PDF page 30 / printed page 26](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf#page=30) | 7 labels | `community-health-services-societies-1997-98.svg` |
| Twenty statistical health regions | [Statistics Canada, one-page PDF](https://www150.statcan.gc.ca/n1/pub/82-221-x/00401/images/pdf/4195184-eng.pdf) | 20 analytical regions | `statcan-bc-health-regions-2000-map.svg` |

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

The PDFs and SVGs preserve the published maps, including insets and historical names. Their vector paths use page coordinates, not a geographic projection. No independently reusable historical administrative GIS dataset was acquired, no historical polygon intersections were measured, and no historical overlap percentages are claimed. Legal reconstruction would require tracing the dated descriptions against appropriate geographic evidence and checking intervening amendments.

## Geographic traps to preserve in the interface

| Area | Interpretation required |
| --- | --- |
| South Cariboo council | [M225/1997](https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0225_1997), made 23 May 1997, renamed **100 Mile House & District** to South Cariboo Community Health Council. Modern 100 Mile House LHA 144 is the candidate; modern South Cariboo LHA 148 belongs to a different comparison. M87/1997 continues the old name and is not the rename instrument. |
| North West society | Exhibit 5 explicitly **excludes Nisga'a Health Authority**. The comparison excludes modern Nisga'a LHA 518 and does not select the whole Northwest HSDA. That modern exclusion is still not a verified historical edge. |
| Northern Interior | The candidate uses Burns Lake, Nechako and Prince George. The current HSDA also includes Quesnel, which had a separate historical council associated with Cariboo. |
| Cariboo | Its candidate includes 100 Mile House, Cariboo/Chilcotin, Quesnel and Bella Coola; those modern LHAs span three current authorities. |
| Upper Island/Central Coast | The source includes a mainland component. North Vancouver Island alone omits it. |
| North Shore and North Okanagan | North Shore's candidate includes Bowen Island but is narrower than today's North Shore/Coast Garibaldi HSDA. North Okanagan's candidate spans today's Okanagan and Thompson Cariboo Shuswap HSDAs. |
| Northern and Kootenay councils | Snow Country, Stikine, Terrace, Bulkley Valley, Nelson and Arrow Lakes selections retain explicit scope-review notes. Modern names are insufficient to confirm all historical subdivisions. |

The [2019 LHA code/name crosswalk](lha-code-crosswalk-1997-scheme-to-2018.json) supports identifier translation. Its title's “Old (1997)” describes the coding scheme; a 2019 table does not prove unchanged boundaries or subdivision existence in calendar 1997.

## Files and regeneration

Source indexes and legal locators live here. Public source artwork and the three-page OAG excerpt live in `public/health-geography/maps/`. Modern display GeoJSON and `boundary-comparison.json` live in `public/health-geography/`. Keep source attribution visible: Statistics Canada material uses its [Open Licence](https://www.statcan.gc.ca/en/terms-conditions/open-licence); modern BC source data use the Open Government Licence – British Columbia. Source artwork is not relicensed by the toolkit's software licence.

To reproduce the map artwork, download the official OAG PDF linked above as `/tmp/oag-1998.pdf`, install PyMuPDF, and run this from the repository root. The source PDF SHA-256 is retained in `map-area-index.json`; verify it before replacing assets. These exports retain the complete original pages, with printed text converted to vector paths; do not redraw boundaries or remove source notes.

```python
from pathlib import Path
import fitz

out = Path('public/health-geography/maps')
out.mkdir(parents=True, exist_ok=True)
names = ['regional-health-boards', 'community-health-councils',
         'community-health-services-societies']
with fitz.open('/tmp/oag-1998.pdf') as original:
    for page_index, name in zip(range(27, 30), names):
        svg = original[page_index].get_svg_image(text_as_path=True)
        (out / f'{name}-1997-98.svg').write_text(svg, encoding='utf-8')
    excerpt = fitz.open()
    excerpt.insert_pdf(original, from_page=27, to_page=29)
    excerpt.save(out / 'BC-health-area-maps-1997-98.pdf')
with fitz.open(out / 'statcan-bc-health-regions-2000-map.pdf') as original:
    svg = original[0].get_svg_image(text_as_path=True)
    (out / 'statcan-bc-health-regions-2000-map.svg').write_text(svg, encoding='utf-8')
```

The Statistics Canada original PDF, source URL, checksum, licence, and conversion description are recorded in [statcan-2000-map.json](statcan-2000-map.json). Re-exporting with a different PyMuPDF version can change SVG serialization; render and compare the complete pages before accepting regenerated artwork. Do not interpret regenerated path coordinates as longitude/latitude.

After editing the source-name index or institutional lineage, run:

```sh
node scripts/build-health-map-catalogue.mjs
```

This writes `src/health/healthAreas.generated.js` and `public/health-geography/catalogue.json`, validates referenced institutional IDs, and reports the 52 source areas and 51 confirmed identity matches. Edit the research inputs rather than those generated files. Rebuilding modern geometry is a separate operation documented in [boundary-comparison-README.md](boundary-comparison-README.md), using `scripts/build_health_boundary_comparison.py`; its current-data audit compares PGMaps with current provincial data only.

## Relationship to PGMaps and the story toolkit

`src/health/StoryFrame.jsx` uses the pinned `vendor/geo-toolkit` story sidecar, chapter navigation, and workspace context, also used by [PGMaps](https://github.com/ahzs645/PGMaps). PofBC owns the historical evidence, identity crosswalk, selected candidate codes, and attribution. The toolkit supplies the presentation components; it does not authenticate a historical geographic match. See the [toolkit README](../../vendor/geo-toolkit/README.md) and keep the historical source artwork visually distinguishable from modern comparison geometry.
