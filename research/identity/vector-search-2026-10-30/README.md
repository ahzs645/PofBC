> **Integrated into the gallery on 30 October 2026.** The 35 SVG files are in
> `public/identity-collected/<body or program>/`, byte for byte as listed in
> [`source-register.json`](source-register.json). `scripts/build-collected-marks.mjs` reads this
> register beside the 22 October inventory, checks every checksum and the vector validation, and
> adds the 20 files of the 13 inventory bodies to those bodies' collections. The 15 files of the
> one-off programs (WorkBC, WelcomeBC, StrongerBC, Canada Starts Here, Where ideas work) hold seven
> timeline eras that were "sought" (`src/gallery/timelines.js`); WelcomeBC's current arrangement is
> now labelled endorsed rather than stacked, as found here. Not copied into the repository: the two
> StrongerBC artwork ZIPs (`original-artwork-packages/`, on the Province's download page), the
> raster references (`raster-references-only/`) and the validation contact sheets; the research
> scripts, research records and validation JSON are here. The statement below that the gallery
> "has not been changed" describes the package as delivered.

# PofBC — missing vector logo search

**Research date: 30 October 2026**  
Gallery: [Public of British Columbia](https://projects.ahmadjalil.com/PofBC/?view=gallery)

## Results

Recovered **35 verified SVG files covering 18 organizations and program families**. The package provides vector specimens for **13 organizations that previously had only raster artwork**, plus published vector specimens for **seven of the gallery’s 14 explicitly sought timeline entries**.

The files comprise **15 original SVG downloads** and **20 extractions of original vector artwork** from published PDF or combined SVG sources. No raster tracing, replacement lettering, or invented symbols were used. Every preferred SVG was parsed and rendered: all contain real geometry, zero embedded raster images, and zero text elements or external resource dependencies.

The deliverable is a research and asset package. The live gallery and its repository have not been changed.

## Scope and inventory

The audit uses the gallery’s [183-body acquisition inventory](https://github.com/ahzs645/PofBC/blob/79be99835e5752efda584511f822097dc987a959/research/identity/collection-2026-10-22/inventory.json) and [timeline definitions](https://github.com/ahzs645/PofBC/blob/79be99835e5752efda584511f822097dc987a959/src/gallery/timelines.js) at repository commit `79be99835e5752efda584511f822097dc987a959`. The deployed gallery’s data was also checked against these gaps. Five existing, separate logo collections were not incorrectly treated as missing simply because their acquisition-inventory asset arrays were empty.

| Body-level category | Baseline inventory | With supplied vector recoveries |
|---|---:|---:|
| At least one vector specimen | 28 | 41 |
| Raster artwork only | 40 | 27 |
| No acquired artwork in this inventory | 110 | 110 |
| Separate established collection | 5 | 5 |
| **Total bodies** | **183** | **183** |

The last column applies the supplied SVG recoveries to the baseline categories; it does not update the live gallery or count additional raster-only source leads as delivered body assets. A body with one vector specimen can still have missing variants or an incomplete identity history. “No acquired artwork” describes the baseline inventory, not proof that an organization lacked a logo.

The body-level gaps comprised 11 current Crown organizations, three current health organizations, 24 former Crown organizations, and 112 former health organizations. All 38 Crown/current-health gaps were individually researched. All **112 former-health gaps received individual searches**. Query logs and rejected leads are retained. Searches were bounded public-source searches, followed by inspection of promising artwork candidates; they are not a claim to have exhausted every possible archive. The 14 timeline slots are a separate count and are not added to the 183-body total.

## Original SVG downloads

| Organization or program | Files | Sources and variants |
|---|---:|---|
| **WorkBC** | 2 | [Archived 25 January 2016 gold-rule SVG](https://web.archive.org/web/20160125130340id_/https://www.workbc.ca/images/workbc-header-logo.svg) and [current grey-rule SVG](https://www.workbc.ca/themes/custom/workbc/logo.svg). Original bytes retained. |
| **WelcomeBC** | 2 | [Archived 13 April 2016 gold-rule SVG](https://web.archive.org/web/20160413214302id_/http://www.welcomebc.ca/images/welcomebc-header-logo.svg) and [current official SVG](https://www.welcomebc.ca/getmedia/ce0988e3-03e0-4fed-a743-8ace3a34d1ce/WelcomeBC_cmyk_pos_Print.svg). Original bytes retained. |
| **StrongerBC** | 8 | Public endorsed-mark and wordmark packages on the Province’s [Download government marks page](https://www2.gov.bc.ca/gov/content/governments/services-for-government/policies-procedures/bc-visual-identity/download-marks). Each arrangement has RGB positive/reverse and solid positive/reverse variants. The two original ZIPs are included, preserving accompanying EPS/PDF masters. |
| **First Nations Health Authority** | 3 | [Colour logo](https://annualreport.fnha.ca/wp-content/themes/fnhaimpactreport/images/fnha-logo-vector.svg), [white-lettering variant](https://annualreport.fnha.ca/wp-content/themes/fnhaimpactreport/images/fnha-logo-white.svg), and [symbol](https://annualreport.fnha.ca/wp-content/uploads/2024/12/fnha-icon.svg), all from the [official annual-report site](https://annualreport.fnha.ca/). Original bytes retained. |

The current WelcomeBC artwork is a horizontal endorsed arrangement: a compact Province mark on the left, a gold divider, and WelcomeBC to the right. The gallery’s existing “stacked” label should be refined to describe the whole arrangement accurately.

## Original vectors recovered from publications

These assets preserve the original paths and lettering. They are useful published vector specimens, but should retain an “extracted from source” attribution rather than being described as separately supplied master files.

| Organization or program | Files | Source and result |
|---|---:|---|
| **BC Housing** | 2 | Native artwork on the cover of [Community Housing for Resilient Communities](https://www.bchousing.org/publications/Community-Housing-for-Resilient-Communites-Report.pdf): the full Research Centre lockup and its isolated corporate emblem/wordmark component. The report describes April 2019 events; a publication/adoption date is not assumed. |
| **BC Family Maintenance Agency** | 1 | Teal emblem and grey wordmark from page 1 of its [2020/21 annual report](https://www.bcfma.ca/assets/uploads/2025/01/BCFMA-Annual-Service-Plan-Report-2020-2021.pdf). |
| **BC Infrastructure Benefits** | 2 | Reversed horizontal full-name artwork from the [2021/22 report](https://bcib.ca/wp-content/uploads/2023/05/Building-Opportunity-Here-BCIB-Report-21-22.pdf), and reversed “Building Opportunity Here” artwork from the [2024/25 report](https://bcib.ca/wp-content/uploads/BCIB_Building-Opportunity-Here-report-F24-25.pdf), both page 1. |
| **Infrastructure BC** | 2 | Full-colour artwork on PDF page 13 and white reversed artwork on page 1 of the [Spring 2026 brochure](https://www.infrastructurebc.com/download/9249/?tmstv=1780966177), linked from its [official publications page](https://www.infrastructurebc.com/publications/bc-infrastructure-project-brochure/). |
| **Community Living BC** | 2 | Full-colour artwork from the [2023 strategic-plan progress report](https://www.communitylivingbc.ca/wp-content/uploads/CLBC_2023-Strategic-Plan-Report_Nov.-22.pdf) and white reversed artwork from the [2013/14 annual report](https://www.communitylivingbc.ca/wp-content/uploads/2018/02/CLBC-Annual-Report-2013-2014.pdf), both covers. |
| **BC Council for International Education** | 1 | Complete BCCIE/book-and-globe/full-name arrangement from page 1 of its [2022–2025 strategic plan](https://bccie.bc.ca/wp-content/uploads/2022/06/Strategic-Plan-2022-2025.pdf). |
| **Columbia Power** | 1 | Pale reversed corporate artwork from PDF page 77 of its [2024 history book](https://columbiapower.org/wp-content/uploads/2024/05/2024_ColumbiaPowerHistoryBook_reducedsize1.pdf). |
| **Interior Health** | 1 | Blue horizontal artwork from PDF page 22 of its [2023–2028 climate roadmap](https://www.interiorhealth.ca/sites/default/files/PDFS/interior-health-climate-change-sustainability-roadmap-2023-2028.pdf). Seventeen original visible logo paths plus a clip definition; all unrelated page content removed. |
| **Provincial Health Services Authority** | 2 | Black and white PHSA components isolated intact from original combined PHSA/GSC SVGs in the [Genome Sciences Centre branding resources](https://mk.bcgsc.ca/branding/). The source combination files are also included for inspection. |
| **BC Transmission Corporation** | 1 | Native emblem and wordmark on page 1 of its [February 2009 service plan](https://www.bcbudget.gov.bc.ca/2009/sp/pdf/agency/bctc.pdf). |
| **Partnerships British Columbia** | 1 | Blue wordmark and green subtitle on page 1 of its [2012/13 annual report](https://www.bcbudget.gov.bc.ca/annual_reports/2012_2013/pdf/agency/pbc.pdf). |
| **BC Oil and Gas Commission** | 1 | Native corporate artwork on page 1 of its [2014 water-use report](https://www.bc-er.ca/files/reports/Water-Management/2014-annual-report-water-use-oil-and-gas-activityprint-version.pdf). |
| **Canada Starts Here** | 2 | Flat container mark alone and the BC Jobs Plan lockup on PDF page 24 of the [BC Jobs Plan dated 11 September 2012](https://www.amssa.org/wp-content/uploads/2015/05/BC-Jobs-Plan.pdf). This is a government document hosted by AMSSA. |
| **BC Public Service — Where ideas work** | 1 | Reverse endorsed lockup on PDF page 11 of the [2023 corporate plan](https://www2.gov.bc.ca/assets/gov/careers/about-the-bc-public-service/corporate-digital/corporateplan_2023.pdf). |

### Attribution and variant decisions

- **BC Housing:** the standalone corporate component consists of exact emblem and wordmark paths from the Research Centre lockup; the subtitle and divider were removed. Preserve that attribution. The organization’s website file named `logo.svg` is an embedded PNG wrapper and does not itself solve the vector gap.
- **PHSA:** both supplied files are intact PHSA groups from published combined PHSA/GSC artwork. They are component extractions. The source bundle’s July 2026 version date is not the logo’s adoption date.
- **BC Transmission:** the 2009 short-name lettering differs from earlier raster specimens. Add it as a dated variant; do not silently replace an earlier design with it.
- **Canada Starts Here:** the recovered files are flat artwork printed in 2012. They are not a recreation of the three-dimensional container treatment shown in launch photography.
- **Where ideas work:** the supplied file is a reversed 2023 specimen. Equality to the earlier archived 2018 PNG has not been established.
- **PDF colours:** extraction converts print colours into SVG RGB. Infrastructure BC’s affected solid colours and Partnerships BC’s colours were matched to the source PDF’s rendered sRGB appearance, with mappings retained in the evidence logs. Geometry remains unchanged.
- **White/reversed variants:** the dark preview backgrounds are presentation backings. They have not been added to the transparent vector files.

## Timeline coverage

| Gallery slot | Result |
|---|---|
| `workbc-flat-rule` | Original archived 2016 SVG recovered. |
| `workbc-grey-rule` | Original current official SVG recovered. |
| `welcomebc-flat-rule` | Original archived 2016 SVG recovered. |
| `welcomebc-2025` | Original current official SVG recovered; refine the arrangement label. |
| `strongerbc-2022` | Eight official SVG variants recovered from the public artwork packages; package retrieval does not prove the first-use date of every variant. |
| `gateway-starts-here` | Two flat vector specimens from the dated 2012 Jobs Plan. |
| `wiw-later` | Reverse vector specimen from the 2023 corporate plan. |
| `welcomebc-2008` | No vector verified. Archived page references the old logo GIF, but the image capture could not be recovered. |
| `bcstats-1996` | Archived GIF recovered/inspected; no native vector verified. |
| `bcstats-2004` | Archived GIF recovered/inspected; no native vector verified. |
| `bcstats-2012` | Archived PNG and several period reports inspected; actual logo regions are raster. |
| `bcws-oval-crest` | No vector of the specified FLNRO crest verified. A later high-resolution Ministry of Forests crest is raster and a different variant. |
| `bcts-oval-crest` | Exact oval/heavy-green-BCTS arrangement found in a 2017 publication, but it is a 714 × 320 bitmap. |
| `wcb-1968` | Official history describes the worker-protection emblem; no native vector located. |

## Remaining body-level gaps

The search leaves **137 bodies without a newly available vector specimen**: four current Crown organizations, 21 former Crown organizations, and 112 former health organizations. This is a search outcome, not a claim that usable vectors do not exist elsewhere.

| Current organization still unresolved | Finding |
|---|---|
| **BC Railway Company** | No verified vector for the current corporate identity. Historical BC Rail operator marks are different identities. The inspected 2024/25 statements have a text-only cover; another report candidate was unavailable. |
| **Provincial Rental Housing Corporation** | No independently attributable logo identified. BC Housing branding on administrator pages does not establish a separate PRHC mark. |
| **PavCo** | Official site uses a [PNG logo](https://www.bcpavco.com/template/logo.png). Inspected reports did not yield native corporate artwork; similarly named industrial-company vectors were rejected. |
| **Transportation Investment Corporation** | Official website artwork and the inspected strategic-plan corporate logo are raster. The Province’s vector logo on an annual-report cover belongs to a different identity. |

The organization checklist contains one row per body, original inventory category, search status, delivered filenames, and caveats. Historical health records often provide legal or institutional evidence without artwork; successor health-authority logos were not substituted for predecessor councils.

## How to review the package

1. Open `index.html` after extracting the ZIP to inspect all 35 supplied SVGs, including reversed variants on dark backgrounds. The artwork displays locally.
2. Use `asset-index.csv` for a flat list of files, source links, dates, and provenance; `source-register.json` adds hashes and structural verification.
3. Use `organization-inventory.csv` for all 183 bodies, and `timeline-gaps.csv` for all 14 sought timeline entries.
4. Keep the recorded source URL, PDF page or archive capture, and extraction attribution with each gallery asset. Preserve separate dated variants where they differ from the current raster reference.

The `original-artwork-packages` folder preserves the two public StrongerBC source ZIPs with their EPS/PDF assets. `source-artwork` preserves the original combined PHSA/GSC SVGs. `raster-references-only` contains useful BC Stats/BCTS/BCWS references, clearly excluded from the vector total. Detailed query and validation records are in `research` and `validation`.

Full source PDFs are linked rather than all being duplicated in this package. Research records may name intermediate source files under `research-inputs-not-bundled`; those paths document the research process and are not promised package files. The canonical deliverable locations are the `file` fields in `source-register.json`. The `research-scripts` folder retains the extraction and validation code with notes about restoring its source inputs.

## Verification

Each of the 35 preferred SVGs was checked for actual vector geometry, embedded images, text elements, external resources, and file integrity. All were rendered with Inkscape, and the extracted assets were compared with their source regions. Native path selections, source hashes, PDF page numbers, and any source-matched colour conversions are recorded. The report and contact sheet use the same supplied SVGs.

The supplemental Interior Health signage extraction found during research uses CAD hatching. It is excluded from the 35 preferred files and from the body-level delivered-file count; the cleaner blue roadmap specimen is supplied instead.

## Appendix — former Crown organizations still without a verified vector

| Organization | Search finding |
|---|---|
| Pacific Great Eastern Railway Company | New valuable non-vector source: Greg M. Kennelly, Logos of the Pacific Great Eastern Railway, in The Cariboo Issue 3. Discusses and dates multiple early designs, expanding his 1986 Coupler employee-newsletter articles. Do not count a scanned magazine as native vector. |
| British Columbia Power Commission | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| British Columbia Toll Highways and Bridges Authority | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| British Columbia Electric Company (provincially owned) | No verified vector attributable to the Crown-era entity. Earlier private BC Electric Railway artwork is a different period/entity and was not substituted. |
| British Columbia Ferry Authority | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| British Columbia Development Corporation | Search finds Lonsdale Quay/Westminster Quay trademarks owned by the corporation; these are property brands and cannot fill its corporate-logo gap. |
| British Columbia Petroleum Corporation | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| Ocean Falls Corporation | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| British Columbia Steamship Company (1975) Ltd. | Search results mix the Crown company with Canadian Pacific Coast Steamship and the earlier 1944 British Columbia Steamship/Northland Navigation company. Those logos and house flags are not acceptable substitutes. |
| British Columbia Buildings Corporation | Downloaded and inspected official 2004 service plan. Cover logo is a 100 x 274 px raster (vertical lockup); no native vector improvement in that specimen. |
| British Columbia Heritage Trust | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| British Columbia Resources Investment Corporation | New primary brochure source located through UFV SACDA, A share in BCRIC; useful for variant/history research, not verified as vector. |
| British Columbia Systems Corporation | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| Urban Transit Authority | No original UTA vector verified. Commons has newly uploaded BUS and FastBUS SVGs but they belong to the Bureau of Transit Services predecessor, not UTA; uploader says own work, so treat as third-party reconstructions. |
| British Columbia Place Ltd. | Located Canadian Museum of History PDF with original British Columbia Place corporate branding and 1982 newspaper advertisements. These are scan/history leads, not verified vectors; modern stadium branding is not a substitute. |
| Metro Transit Operating Company | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| W.L.C. Developments Ltd. | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| British Columbia Enterprise Corporation | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| British Columbia Assets and Land Corporation | No new genuine vector file verified in this indexed-web pass. Existing raster evidence or unresolved status remains; this is not proof that no logo or vector exists. |
| Land and Water British Columbia Inc. | Downloaded 2003 and 2004 official service plans. Covers contain a typeset corporate title and layout rectangles, not the separately evidenced LWBC symbol. No logo vector claimed from them. |
| British Columbia Harbours Board | Found 1971 Harbours Board Railway timetable listing; useful source route only, not a verified logo or vector. |

## Appendix — additional historical health leads

- **Capital Health Region:** [source lead](https://saltspringarchives.com/driftwood/1999/v41n7Feb17-1999.pdf); archival print lead not vector verified. 
- **Capital Health Region:** [source lead](https://saltspringarchives.com/driftwood/1999/v41n4Jan27-1999.pdf); archival print lead not vector verified. 
- **Vancouver/Richmond Health Board:** [source lead](https://docs.openinfo.gov.bc.ca/Response_Package_HTH-2017-72113.pdf); existing inventory raster source. 
- **Thompson Health Region:** [source lead](https://www.merritt.ca/wp-content/uploads/archives/meetings/1998/1998-11-10%20RC%20agenda.pdf); search indexed source current download 404. 
- **Nicola Valley Health Council:** [source lead](https://www.merritt.ca/wp-content/uploads/archives/meetings/1996/1996-02-13%20RC%20agenda.pdf); search indexed period document lead. 
- **Powell River Community Health Council:** [source lead](https://cewh.ca/wp-content/uploads/2012/05/2004_Advancing-Health-Girls-Women.pdf); bibliographic lead not artwork verified. Bibliography cites Specialized Victim Support Services(2000), Working Together For Women’s Health, Violence Against Women: Improving the Health Care Response, Powell River Community Health Council.
- **Simon Fraser Health Board:** [source lead](https://sacda.ufv.ca/collections/2022_15_03_02_006); downloaded verified raster region specimen. Primary 10 April 1997 Board-chair letter; inspected logo says Simon Fraser Health region.
- **Simon Fraser Health Board:** [source lead](https://sacda.ufv.ca/sites/default/files/2026-09/2022_15_03_02_006.pdf); verified raster different period attribution. Page 1 full-page 3400 × 4677 raster;0 native drawings.
- **Simon Fraser Health Board:** [source lead](https://sacda.ufv.ca/collections/2022_15_03_02_005); verified raster region specimen. Companion 15 April 1997 Region letter; also downloaded and structurally raster.
- **Southern Gulf Islands Community Health Council:** [source lead](https://saltspringarchives.com/driftwood/1995/v36n35August30-1995A.pdf); archival print lead not vector verified. Period 30 August 1995 article discusses designation. Not downloaded for structural inspection; no vector claim.
- **Terrace and Area Health Council:** [source lead](https://fileserver-az.core.ac.uk/download/141716730.pdf); verified raster page no distinct logo. The Terrace Standard,10 November 1999,A 12. Inspected full-page bitmap; council ad has plain typeset title.
- **West Coast Community Health Council:** [source lead](https://www.acrd.bc.ca/district-board-members); historical document lead. Director biography identifies 1994 submission requesting distinct council area; historical-document lead only.
- **Campbell River/Nootka Community Health Council:** [source lead](https://www.wordsonthewater.ca/uploads/3/9/4/2/39427837/wow2002.pdf); . 2002 festival programme p5 visibly attributes a CR/NCHC logo to Campbell River/Nootka Community Health Council. Original URL now 404. Archived original PDF inspected: all 8 pages raster, zero drawings; not a vector source.
- **Campbell River/Nootka Community Health Council:** [source lead](https://web.archive.org/web/20240125023008/https://www.wordsonthewater.ca/uploads/3/9/4/2/39427837/wow2002.pdf); . Public 2024-01-25 archive capture downloaded and structurally/visually inspected. Native PDF is 1,076,391 bytes; all pages contain one raster image each.
- **Kootenay Boundary Community Health Services Society:** [source lead](https://docs.openinfo.gov.bc.ca/Response_Package_TRA-2017-70554.pdf); existing inventory period raster source. 
