# Crown, utility and transport salary source search

Audit date: **2026-10-31, America/Vancouver**. All **41 Crown-sector employer entries** present in the app at baseline `96d798e` received an official-source discovery check. This includes two predecessor/successor pairs and three Hydro subsidiaries; it is not a complete roster of every provincial public agency.

The pass retrieved and hashed **79 unique original PDFs** and recorded **266 distinct candidate financial-disclosure URLs** from official indexes. These counts measure discovery and retrieval, not salary observations accepted into the app. Only **41 InBC employee observations across three fiscal years** completed full row, period, scope and source-control review in this pass. They are in [the proposed collection](../../sector-crowns/README.md), with the collection registry left to central integration. Nine proved duplicate compiled InBC observations labelled 2023/24 are explicitly replaced under their actual 2022/23 period through a hash-pinned rule; other compiled observations remain retained.

Start with [work-queue.json](work-queue.json): 42 actionable tasks, with separate routes for processing, public archive research and ordinary records requests. [findings.json](findings.json) contains the 41 employer findings and document diagnostics. [discovery.json](discovery.json) retains index retrieval URLs, HTTP results, hashes and relevant links; [pdf-receipts.json](pdf-receipts.json) records original PDF URLs/hashes, native text per physical page and cover-level period evidence. Index labels remain discovery labels until the original schedule is reviewed. A usable text layer somewhere in a report does not establish that its salary table can be parsed without OCR.

## Located histories to process

The ranges below describe **official index labels or retrieved documents**, as specified. They do not assert that every intervening report was retrieved or every year has been accepted. Each exact URL and individual label is retained in the inventory.

| Employer/archive | Evidence recovered | Remaining work |
|---|---|---|
| ICBC | Index labels 2014, 2015, 2016/17–2025/26; latest two originals retrieved and hashed | Complete employee rows, component definitions, thresholds and source controls; preserve changes in calendar/fiscal reporting |
| BCLC | Official financial-information archive labels extend from 2009/10 to 2025/26; latest two originals retrieved | Separate employee remuneration from board, supplier and aggregate schedules; verify the actual period of each original |
| WorkSafeBC | Calendar 2023, 2024 and 2025 originals retrieved; first-page checklists confirm December 31 year ends | Parse all employee tables; recover pre-2023 download routes or obtain historical originals |
| TransLink | Index labels 2020–2025; 2024 and 2025 original reports retrieved | Preserve separate parent and operating-company cohorts, including Transit Police; independently verify all columns and controls |
| BC Housing | Latest 2024/25 original is image-only; 2023/24 original has native employee table text | Complete the staged OCR work described below; parse and verify historical official schedules |
| BC Assessment | Originals retrieved for calendar 2020; a **15-month** period ending March 31, 2022; and 2022/23–2024/25 | The transition report must retain January 1, 2021–March 31, 2022; do not treat it as an ordinary twelve-month salary year |
| BC Infrastructure Benefits | Official index labels 2019/20–2024/25; latest two originals retrieved | Extract entire administrative/construction employee scope as disclosed, independently review rows and verify controls |
| Infrastructure BC / Partnerships BC | Official archive labels 2005/06–2024/25; 2016/17 and 2024/25 originals retrieved | Verify period, entity name and all employee schedules for each original |
| First Peoples’ Cultural Council | All 19 original SOFI files labelled 2008–2026 retrieved | Establish actual dates and scope from each table; older reports can mix native financial-statement text with scanned schedules |
| Innovate BC / BC Innovation Council | Eight SOFI originals linked under 2017/18–2024/25 archive sections retrieved | Independently extract and verify complete employee schedules, including changes in source naming |
| BC Financial Services Authority | Official index labels 2019/20–2025/26; latest two originals retrieved | Preserve the initial partial period and later disclosure scope; parse complete employee tables |
| BC Energy Regulator / Oil and Gas Commission | Shared official FIA archive and latest two originals retrieved | Review predecessor/successor identity centrally and avoid duplicating the shared source files |
| SkilledTradesBC / Industry Training Authority | Shared FIA archive; latest two originals retrieved | Review identity centrally and retain exact employer/period evidence from each source |
| Royal BC Museum | Official archive labels 2013/14–2025/26; latest two originals retrieved | Verify employee scope, actual years and all source controls |
| Columbia Basin Trust | Current original SOFI linked from a paginated official publications archive retrieved and hashed | Parse the source’s legal-entity and employee schedule scope; deeper historical indexing remains |
| Columbia Power | 2025/26 SOFI original retrieved | Verify employee versus board/contractor scope and obtain older files through the official archive |
| Knowledge Network | 2025/26 and 2024/25 originals retrieved; attempted legacy 2023/24 URL returned a non-PDF body | Parse the retrieved employee schedules and recover the historical original at a current/archived official route |
| Community Living BC, Legal Aid BC, BCSC, LDB and TI Corp | Official financial-disclosure indexes and representative original reports retrieved | Source-specific employee parsing, period and component checks, full row verification and monetary controls |
| Hydro, Powerex, Powertech, CHC and BC Transit | Existing accepted collections and official current archive routes identified | Compare exact registered source IDs and process only uncovered periods; do not import already registered schedules again |

## OCR work completed and pending

BC Housing’s 2024/25 SOFI is a 42-page image-only original. This pass produced a first Tesseract reading at 201.6 dpi for the cover, contents, approval and the complete remuneration-schedule section, **22 physical pages in total**. The source fingerprint is pinned in [ocr_sector_crowns.py](/workspace/PofBC/scripts/ocr_sector_crowns.py).

The first reading identifies **physical page 9 as board members**, **pages 10–26 as named employees**, and **page 27 as remuneration controls**. The OCR evidence is in [ocr-stage/bc-housing-2024-25-first-ocr.json.gzip](ocr-stage/bc-housing-2024-25-first-ocr.json.gzip). It records the source URL/hash, exact physical-page links, render and OCR-text hashes and pending verification. **No OCR employee rows are accepted.** A second independent reading, complete row and name review, treatment of missing/dash cells, source monetary definitions and printed-control checks remain.

Forestry Innovation Investment’s retrieved 2024/25 official SOFI is also image-only, 31 pages. The retrieved BCCIE 2022/23 audited financial statements are image-only, 19 pages; this does not establish a named employee salary schedule. Older FPCC documents need page-specific text-layer assessment before deciding which salary schedules need OCR.

## Records to obtain

[procurement-candidates.json](procurement-candidates.json) lists five ordinary records-request candidates. It is a preparation list; **no requests, FOI submissions or messages were sent**.

| Employer | Evidence gap | Useful request |
|---|---|---|
| BCCIE | Corporate and financial reports found; named employee SOFI schedule not located | Existing historical employee remuneration/expense schedules and native spreadsheets, with actual reporting dates |
| BC Pension Corporation | Annual and executive reports found; all-employee schedules not located | Existing FIA employee schedules and historical native files, distinct from executive disclosures |
| Forest Enhancement Society | Checked financial-statement note gives aggregate employee/secondment/contractor remuneration | Existing named schedules, separately identifying employees, secondments and contractors |
| BC Ferries | Annual/executive disclosures found; no all-employee schedule located | Existing publicly releasable historical named remuneration disclosures and the appropriate records-access route |
| BCI | Executive disclosures found and some already staged separately; no all-employee schedule located | Existing publicly releasable named remuneration disclosures, with any executive-only scope retained separately |

The provincial [executive disclosure guidance](https://www2.gov.bc.ca/gov/content/governments/services-for-government/public-sector-management/compensation/executive-compensation-disclosures) explicitly distinguishes BC Ferries and BCI from the ordinary FIA requirement. This audit does not establish that FOI applies to either organization. Begin with available publications and ordinary access; assess a formal FOI fallback only if the relevant existing records and access route require it.

Three other entries first need deeper public archive work: **BC Utilities Commission** (official site/index returned HTTP 403), **Insurance Council of BC** (financial, board and executive reports found, employee schedule not located) and **Technical Safety BC** (annual/governance reports found, employee schedule not located). Their queue entries retain those specific blockers. Unsuccessful retrieval does not prove a report is absent.

WorkSafeBC’s pre-2023 history is a separate archive task. Predictable official URL probes for 2014–2022 returned 404, and targeted searches did not recover those originals. The retrieved 2023–2025 schedules are processing tasks. Earlier originals may require former download-route recovery, archived copies or an ordinary request before any formal FOI fallback.

## Scope, overlap and identity

TransLink’s 2025 original has separate TransLink Security Management Ltd. employee pages 214–220; the corresponding 2024 pages are 196–202. The organizational chart describes the policing subsidiary as Transit Police. [translink-police-scope.json.gzip](translink-police-scope.json.gzip) retains both original hashes, contents evidence, physical-page links, native-text and rendered-page fingerprints. These are inventory leads; the employee rows were not fully verified. Both existing compiled Transit Police aliases and their unverified period labels remain untouched, pending complete-group comparison.

The [BCER timeline](https://www.bc-er.ca/stories/twenty-five-year-staff-profiles/) describes the Oil and Gas Commission’s renaming in 2023. The [SkilledTradesBC announcement](https://skilledtradesbc.ca/introducing-skilledtradesbc) states that ITA transitioned to SkilledTradesBC on December 1, 2022. These primary identity leads support central review; this pass changes no canonical employer mappings.

Only the three InBC schedules received complete field, row, source-period, scope and control review. Two $1 source residuals remain explicit public warnings; no cause is inferred and no cell is changed. [inbc-aggregate-only-period.json](inbc-aggregate-only-period.json) records the explicit 2021/22 statement that no employees received more than $75,000 from InBC and the $232,304 below-threshold aggregate. It creates no individual salary observations. Executive-only compensation, board payments, suppliers and aggregate payroll are never substituted for a named employee schedule. The exact nine-row compiled InBC employee cohort labelled 2023/24 matches the complete 2022/23 original in every name, position, pay and expense cell, with multiplicity; none matches the later fifteen-row 2023/24 original. [The overlap evidence](../../sector-crowns/inbc-overlap.json) pins the baseline, selected rows and accepted source bytes and encodes that explicit period correction.

## Reproduction

The inventory records exact official index/document URLs, retrieval results and SHA-256 fingerprints. Raw downloaded originals and HTML pages are cached under `/tmp/sector-crowns`; they can be re-fetched from the recorded URLs and checked against those fingerprints. Hash changes require renewed source review. Failed URL probes and non-PDF retrievals are retained explicitly. Native text diagnostics identify candidate schedule pages; they do not assert full table verification.

Reproduce the accepted InBC collection and its seven regression checks:

```sh
python scripts/import_sector_crowns.py --cache-dir /tmp/sector-crowns --verify
python -m unittest discover -s scripts -p test_sector_crowns.py
```

Reproduce the first BC Housing OCR reading (PyMuPDF, Tesseract and English OCR data required):

```sh
OMP_THREAD_LIMIT=1 python scripts/ocr_sector_crowns.py --cache-dir /tmp/sector-crowns
```

The OCR command writes evidence only and emits zero normalized salary records. The import command cannot change the collection registry, compiled baseline or public app outputs; its manifest encodes the reviewed nine-row replacement decision for central integration.

## Every employer entry

| Employer | Baseline rows | Retrieved originals | Next route |
|---|---:|---:|---|
| B.C. Assessment | 1052 | 5 | processing |
| B.C. Council for International Education | 13 | 1 | ordinary-records-request |
| B.C. Energy Regulator | 249 | 2 | processing |
| B.C. Ferries | 5176 | 0 | ordinary-records-request |
| B.C. Financial Services Authority | 369 | 2 | processing |
| B.C. Housing | 1101 | 2 | processing |
| BC Hydro and Power Authority | 59732 | 0 | public-archive-research |
| B.C. Infrastructure Benefits | 833 | 2 | processing |
| B.C. Investment Management Corporation (BCI) | 368 | 0 | ordinary-records-request |
| B.C. Pavilion Corporation | 245 | 1 | processing |
| B.C. Pension Corp. | 182 | 0 | ordinary-records-request |
| B.C. Securities Commission | 332 | 1 | processing |
| B.C. Transit | 3328 | 0 | public-archive-research |
| B.C. Utilities Commission | 46 | 0 | public-archive-research |
| B.C. Lottery Corporation (BCLC) | 2108 | 2 | processing |
| Columbia Basin Trust | 419 | 1 | processing |
| Columbia Power Corporation | 8 | 1 | processing |
| Community Living B.C. | 909 | 2 | processing |
| Destination B.C. | 109 | 2 | processing |
| First Peoples’ Heritage, Language and Culture Council | 38 | 19 | processing |
| Forest Enhancement Society of B.C. | 9 | 1 | ordinary-records-request |
| Forestry Innovation Investsment | 87 | 1 | processing |
| ICBC | 7269 | 2 | processing |
| InBC Investment Corp. | 9 | 5 | public-archive-research |
| Industry Training Authority of B.C. | 60 | 2 | processing |
| Infrastructure B.C. | 73 | 2 | processing |
| Innovate B.C. | 21 | 8 | processing |
| Insurance Council of B.C. | 5 | 0 | public-archive-research |
| Knowledge Network | 52 | 2 | processing |
| Legal Services Society | 180 | 2 | processing |
| Liquor Distribution Branch | 987 | 2 | processing |
| B.C. Oil and Gas Commission | 356 | 2 | processing |
| Royal B.C. Museum | 105 | 2 | processing |
| Skilled Trades B.C. | 98 | 2 | processing |
| Columbia Hydro Constructors Ltd. | 723 | 0 | public-archive-research |
| Powerex Corporation | 1763 | 0 | public-archive-research |
| Powertech Labs. Inc. | 1551 | 0 | public-archive-research |
| Technical Safety B.C. | 426 | 0 | public-archive-research |
| Translink | 12464 | 2 | processing |
| Transportation Investment Corporation | 207 | 2 | processing |
| Worksafe B.C. | 6848 | 3 | processing |
