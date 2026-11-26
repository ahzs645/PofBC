> Research snapshot. Acquisition totals and unresolved statuses in this working note may precede final integration. The final audit README, report.json and acquisitions.json take precedence. `unbundled/` names identify receipt files omitted from this repository report.

# Commission, public-body and historical identity recovery

Research date: November 26, 2026. Baseline repository commit: `279cba21ce0afd2a6d21e082019f2a736932d0cb`.

## Deliverables

- `findings.json` is frozen at **12 assets: 5 verified native SVGs and 7 historical rasters**.
- `extra-findings.json` has **8 additional assets: 5 verified native SVGs and 3 official rasters**. It is separate so integration of the first manifest can proceed safely.
- Together: **20 source specimens across 15 subjects; 10 native-vector assets across 9 subjects**. These are acquisition counts, not a claim that every asset is a previously unrepresented design. The existing registry should determine exact matching `variantOf` and `preferredVector` relationships.
- Each entry includes a local path, suggested asset metadata, source URL, source locator, vector/raster distinction and SHA256. All export previews have been visually compared with the source.
- `source-checks.json` consolidates actual downloads and failures. Original PDFs and HTML, source-page PDFs, source crops, extraction scripts, receipts and PNG previews remain alongside the manifests.
- No shared gallery registry or git state was changed by this agent.

## Native-vector recoveries

| Subject | Artwork | Source and check |
|---|---|---|
| Provincial Agricultural Land Commission | Green ALC emblem; white emblem with full name | Original official website SVG files, byte-for-byte. All paths/polygon geometry. No image or live text. |
| Forest Appeals Commission | Multicolour radial emblem and green two-line name | Official 2021 annual report cover. Native paths and original embedded-font glyph outlines. Background photograph and report heading removed. |
| Doctors of BC | Teal and dark-grey stacked wordmark | Exact inline `#DoctorsOfBCLogo` from official homepage. Native paths, no fonts or embedded image. |
| Electoral Boundaries Commission | Purple and grey folded-map lockup | Official April 3, 2023 final report, PDF page 263. All 49 visible logo paths preserved. |
| Coast Mountain Bus Company | White emblem and full name | TransLink March 24, 2022 board deck, PDF page 51 footer. 27 original visible paths. Fills a native-vector gap; distinct white colourway. |
| West Coast Express | White train/mountain emblem and wordmark | Same official board deck footer. 3 compound paths. Fills a native-vector gap; keep distinct from dark-colour held specimen. |
| SkyTrain | White swoosh and serif wordmark | Same footer. 11 visible source paths. Check existing colourways before integrating. |
| Metro Vancouver Transit Police | White crest and full-name lockup | Same footer. 299 visible source paths. Check existing colourways before integrating. |
| TransLink | White historic figure/arc wordmark | Same footer. 12 visible source paths. Check existing colourways before integrating. |

All white artwork requires a dark preview; SVG files preserve source white rather than recolouring it. Dark-blue preview backgrounds are not baked into the SVG.

## Authentic raster specimens retained

| Subject | Dated specimen | Result |
|---|---|---|
| Provincial Capital Commission | 2011 service plan cover | Gold dome and bold white full name on purple. Mixed source image/text rendered as a crop, explicitly raster. |
| Provincial Capital Commission | 2013/14 annual report cover | Grey dome and spaced serif full name, lossless embedded bitmap. **Page 2 is the ordinary provincial BC logo and was excluded.** |
| Financial Institutions Commission | Bulletin dated `02/05/2003` | Full-colour provincial-sun emblem with FICOM name, original 520x119 image. Date printed on source is 2003; day/month ambiguous. |
| Electoral Boundaries Commission | February 14, 2008 cover file, PDF page 7 | White provincial-map emblem and serif name on green. Low-resolution original page image; retained without invented detail. |
| Electoral Boundaries Commission | March 26, 2015 report, PDF page 154 | Black/blue compass lockup. Logo includes a small raster cast shadow, so the complete mark is **not** a pure native vector. |
| Medical Services Commission | The Hospital Guardian, May 1972, printed page 6 / PDF page 7 | Circular MSC seal accompanying reproduced 1970 statements. Scanned paper and surrounding rules retained; no cleanup or redraw. |
| BC Human Rights Commission | 2000/01 annual report cover, PDF page 2 | Provincial-sun emblem and full name. Original halftone scan is poor contrast; preserved honestly, no vector claim. |
| BC Utilities Commission | June 5, 2023 attestation letter, PDF page 1 | Orange dot-map and purple name; original 678x265 bitmap from official compensation disclosure. |
| BC Vegetable Marketing Commission | 2024 annual report, PDF page 40 | Green BCVMC acronym and black full name; original 504x152 image. |
| BC Vegetable Marketing Commission | Current official website, observed November 26, 2026 | Green acronym and white full name; original PNG. URL upload year is not treated as adoption evidence. |

## Rejected sources and open leads

This was a targeted source-recovery pass, not an exhaustive historical review of every health/Crown subject in the baseline inventory. `input-inventory.json` is the larger candidate pool and does **not** mean all those subjects were searched.

| Subject or source | Actual check | Status / next useful step |
|---|---|---|
| BC Treaty Commission | Official homepage directly links `https://bctreaty.ca/wp-content/uploads/2023/04/BCTC-NoTag-White.svg`; 2018/2024 annual reports and 2016 conference book also located. | Download attempts returned HTTP 403. **SVG located, geometry unverified, not acquired.** This is the strongest remaining source-vector lead. Original conference book describes the mark; 30th-anniversary designer attribution is a separate identity. |
| BCUC | Home, GasPricesBC website, agency case study and official 2022/23 annual report on `docs.bcuc.com` located; direct requests returned 403. | Native vector unresolved. Official compensation disclosure supplied only a raster logo. No drawing from the dots was attempted. |
| ALC governance policy G-01, October 2020 | Cover inspected; logo is a 396x252 embedded image. | Rejected as vector source; official SVGs above supersede this lead for matching artwork. |
| Provincial Land Commission | Official ALC archive: Baxter's April 1, 1974 review downloaded, all scanned page images. | No separate usable mark verified. Scan does not establish a vector source. |
| Forest Appeals 2013 annual report | Cover and page imagery inspected. Cover is a forest photograph plus report typography. | No distinct historical “tree logo” verified; do not treat decorative cover trees as a recovered identity. 2021 source supplied the verified logo. |
| Forest Appeals about brochure | Current radial emblem is embedded raster plus native text. | Rejected as complete native-vector source. |
| Doctors of BC 2024–2029 strategic plan | Cover and last page inspected; entire cover/brand area raster. | Better Together tagline treatment is a possible additional raster variant. Current homepage source SVG acquired. |
| Nechako-Kitamaat Development Fund | Official annual reports 2001/02, 2013/14 and 2024/25 downloaded and covers inspected. | Logos in all checked covers are images, not vector. Existing holdings already have a raster; no distinct new variant promoted without a design comparison. |
| Health Officers Council of BC | Official logo-design page located; homepage download returned HTTP 406. | Current artwork exists in repository as raster. No native vector verified. |
| Simon Fraser Health Region | Dalhousie Medical Journal ad PDF downloaded. | All pages scanned, zero native drawings. No vector recovery. |
| Thompson Health Region | Search located 1998 Merritt agenda with report correspondence. Direct source request returned 404. | Open archival lead only. |
| Coast Garibaldi / East Kootenay health | Targeted source-publication searches performed. | No usable source vector verified in this pass. Not a claim no original exists. |
| Human Rights 2000/01 | ERIC-hosted original publication examined throughout. | Scanned, not vector; cover specimen retained. |
| Law Reform Commission | Successor BCLI catalogue links 1984/85 annual report `https://www.bcli.org/sites/default/files/LRC_80.pdf`. | Download returned 403. Catalogue/source located; no logo acquired. |
| FICOM completion guide | Official successor-hosted PDF inspected; logo uses raster provincial-emblem components. | Rejected as pure vector. 2003 bulletin specimen retained. |
| WCE September 2024 performance report | Cover/contents inspected; WCE logo is embedded raster. | Rejected as native vector. 2022 official white footer logo supplies native geometry. |
| WCE 1995 launch announcement | February 24, 1995 Buzzer downloaded; scanned two-page publication. | Already cited in repository's WCE record; not duplicated as a new historical specimen. |

## Reproduction and validation notes

- `extract_fac.py`, `extract_ebc.py`, `extract_historical_rasters.py`, and `extract_transit.py` retain original source geometry or pixels. Re-running a script can overwrite its own intermediate manifest; use the frozen final manifests for integration.
- Transit path selection uses `translink-board-51-bounds.csv`, generated by Inkscape from the source SVG with temporary IDs. The receipt records selected path indices. Original clipping and transforms remain intact.
- Inkscape was used for SVG visual QA. PyMuPDF's SVG renderer incorrectly displayed the ALC CSS-styled green emblem in black; `alc-logo.png` / `alc-footer.png` are discarded intermediate renders. Use the final manifest SVGs and `*-preview.png` render checks instead.
- Dates describe a published specimen or observation. No inferred adoption date, unsupported identity relationship or later redraw is represented as original art.
- The root agent owns gallery matching, display generation, actual gallery UI QA, and final integration.

## Regional-district follow-up

The root requested a quick follow-up on all six regional-district raster gaps. `regional/README.md` and `regional/source-checks.json` document twelve additional official PDF/AI inspections. `regional/findings.json` adds two native SLRD horizontal colourways, one from a 2016 PDF and one from an editable AI file modified in 2018. These are separate source colourways rather than automatic replacements for the current website PNG. Across all three manifests, the acquisition total is now **22 assets: 12 native SVGs and 10 rasters, across 16 subjects**, before duplicate-design reconciliation during integration.


## Transit duplicate reconciliation

See `integration-mapping.json`. Retain new white CMBC, WCE, SkyTrain and TransLink as source colourways (`variantOf` suggestions supplied), with no `preferredVector` override of differently coloured defaults. Treat the 2022 Transit Police white lockup as an additional dated source (`alsoSeen`) on the existing reversed entry rather than another gallery artwork. It matches the design; source serialization and placement differ, so a claim of byte-exact/path-exact identity is not made. Comparison originals were read from baseline git into `comparison/`; shared repository state was not edited.
