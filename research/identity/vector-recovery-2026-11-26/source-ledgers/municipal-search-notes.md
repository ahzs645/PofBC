> Research snapshot. Acquisition totals and unresolved statuses in this working note may precede final integration. The final audit README, report.json and acquisitions.json take precedence. `unbundled/` names identify receipt files omitted from this repository report.

# Municipal native-vector recovery — 26 November 2026

## Verified deliverables

`findings.json` is final: **26 municipal native-vector assets**, plus **3 related Tourism Radium variants** held separately. Exact source files, native-source SHA256 values, SVG paths, source locators and extraction recipes are recorded. Source-only extractions preserve lettering and colours; none were traced.

| Municipality | Recovered | Relationship to existing gallery |
|---|---|---|
| Sparwood | 8 official Brand Book variants | Blue unbounded matches website family; other source colourways and bounded slogans retained separately. |
| Sooke | Horizontal Pantone EPS master and SVG derivative | Genuine27-path vector; vertical EPS download is actually JPEG and was rejected. |
| Tofino | 6 official guide variants | Stacked colour matches existing2023 bylaw logo; horizontal, wordmark, semi-reverse, black and white documented. |
| North Cowichan | Corporate wordmark and2023 150th mark | Wordmark matches website family; anniversary is a distinct commemorative design. |
| Colwood | Charcoal one-colour2022 source | Additional official colourway; municipality already had native vectors. |
| Nakusp | Stacked colour and horizontal black,2023 | Separate source layouts/colourways. Existing horizontal colour raster still needs exact vector. |
| Radium Hot Springs | 6 variants from2012 guide | Wonder·Land and community lockups; current website has different relative word sizes. Three Tourism Radium guide options are recorded separately. |

Radium provenance is unusually strong: the9 March2026 council memo on agenda pp42–43 explicitly dates the guide to2012, explains that Wonder·Land was subsequently played down, and says purple became more prominent. The source guide appears at agenda pp44–50.

## Coverage and practical limits

The canonical baseline contains73 municipal subjects with no native vector. The source-page crawl attempted71 of their official homepages:69 succeeded, Enderby returned406 and Salmo timed out. The2 artwork-missing subjects received targeted searches. Another25 municipal homepages were checked before canonical acquisition deduplication. A total56 report/brand landing pages were also inspected; some belong to already-covered municipalities.

`search-coverage.json` contains one record for every canonical gap, exact checked URLs, page ranges, fetch failures and next action. Records marked **homepage inspected only** have not had an exhaustive historical publication search. Native tables or other artwork elsewhere in a PDF were never counted as a logo vector.

## Named priorities

- **Enderby:** official homepage and annual-report downloads blocked406. The regional housing brochure stores Enderby within a merged raster logo strip. Still unresolved.
- **Fort St James:** existing symbol vector does not resolve the whole wordmark. Three checked official/regional publications use embedded bitmap lockups.
- **Fraser Lake:**2024 annual-report current landscape logo and older seal are raster in inspected occurrences; strategic-plan cover is also raster.
- **Clinton:** canonical baseline already has native historical walking-tour/title/slogan/investment forms. Do not duplicate those as newly found.
- **Chetwynd:** canonical landscape/chainsaw-map vectors already held; coat of arms remains a separate raster gap.
- **Williams Lake:** coat-of-arms vector already held; modern place badge remains separate and should not be satisfied by reconstructed artwork.
- **Daajing Giids / Queen Charlotte:** current and historical vector gap remains. A fresh primary designer lead documents a new March–July2026 identity project: [Cinnamon Toast case study](https://cinnamontoast.ca/work/village-of-daajing-giids). This new identity needs comparison against the interim lettering and archival Queen Charlotte forms; no master geometry was inspected.

## Rejected or blocked leads

- Armstrong official graphic standards manual: all9 pages scanned (one image/zero paths per page).
- North Vancouver mobile SVG and Port McNeill inline SVG: bitmap wrappers, not native vectors.
- Sooke vertical file labelled EPS/vector: JPEG bytes; horizontal companion is genuine EPS.
- Rossland Group309 SVG: newspaper UI icon, not logo. Spallumcheen pinned-tab SVG URL returned an HTML block page.
- Sidney2025, Oliver2024, Golden2024, Pemberton2025 and Peachland2024 inspected logo occurrences were raster.
- Vancouver2025 annual report and Lake Country2023 profile were verified official leads but binary downloads returned403; geometry remains unverified. Kelowna search-indexed guide URLs returned404.
- The Okanagan Falls district had no logo as of4 November2026 according to local reporting; no official native source identified. This does not establish absence after that date. shíshálh district-specific artwork remains unverified; do not silently substitute nation artwork.

No municipal or designer emails were sent. A future master-file request should ask for the exact unresolved signature, historical date/lockup and native EPS/SVG/PDF/AI, using the gap record rather than accepting an unrelated alternate logo.
