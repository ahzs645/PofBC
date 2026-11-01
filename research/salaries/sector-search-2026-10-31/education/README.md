# Postsecondary salary source and history search

Audit date: **2026-10-31, America/Vancouver**. This review covers all **24** universities/colleges already represented in the application. It found **102 indexed or search-located candidate documents**, retrieved and fingerprinted **93 PDFs**, and distinguished **9 unsuccessful/non-PDF retrievals**. Locating a report is not acceptance of its employee rows or exhaustive discovery of its institution’s history.

`findings.json` is the employer inventory. `document-verification.json` records exact original URLs, resolved URLs, bytes, SHA-256 fingerprints, native-text availability, first-page period evidence and candidate remuneration pages. `work-queue.json` is the normalized follow-up queue with processing, archive, ordinary request and conditional clarification routes. The page-discovery JSON files retain checked endpoints, failed paths, extracted original links and page fingerprints. Raw search responses are leads only.

Six fully extracted SFU employee cohorts / **13,527 observations** are ready in [the accepted collection](../../sector-education/README.md). Three SFU cohorts / **7,079 observations** remain in `held/` because of material named-control differences. No other discovered cohort has been promoted into accepted data in this pass.

| Employer | SOFI histories located in this pass | Processing or acquisition finding |
| --- | --- | --- |
| BCIT | Nine previously accepted periods remain; current archive retrieval challenged | HTTP 200 JavaScript bot challenge, not a report page; earlier scanned 2013/14 and fiscal gaps need further work |
| Camosun | 2015/16–2025/26 | 11 native-text PDFs; fiscal labels printed on report covers |
| Capilano | 2018/19–2024/25 | Seven native-text PDFs; 2025/26 audited statements/executive attestation do not establish a 2025/26 SOFI |
| Coast Mountain | 2022/23–2024/25 | Three native PDFs; newest filename says financial statements but contains employee **Salary Plus Benefits**, separate Expenses and expense-inclusive Total |
| College of New Caledonia | Indexed 2019/20–2025/26 | Seven PDFs; six image-dominant, 2020/21 native text; indexed periods are not substituted for unread internal headings |
| College of the Rockies | No complete employee SOFI located | Official board financial page has audited statements, board remuneration and executives; obtain ordinary employee schedules |
| Douglas | 2021/22–2025/26 | Five native PDFs |
| Emily Carr | 2023/24 and 2025/26 | Two native PDFs; search earlier board/media archives |
| Justice Institute | No complete employee SOFI located | Reports page has board honoraria/executive disclosures and audited statements; request full employee schedules |
| KPU | 2017/18–2024/25 | Eight PDFs; 2018/19 image-dominant and needs OCR |
| Langara | 2022/23–2024/25 | Three PDFs; one image-dominant and needs OCR |
| North Island | 2018/19 and 2020/21–2024/25 | Six PDFs; existing 2020/21 coverage overlaps; one image-dominant; 2019/20 not linked in retrieved index |
| Northern Lights | No complete employee SOFI located | Audited statements and board/executive reports are separate scopes; ordinary release or archive request needed |
| Okanagan | 2020/21–2024/25 | Five native PDFs; separate executive series extends further back |
| Royal Roads | 2022/23 | Exact signed original PDF has employee names/positions; broader historical SOFI index still needs discovery |
| Selkirk | No complete employee SOFI located | Financial statements 2018/19–2025/26 and executive disclosure found; obtain full employee SOFI |
| SFU | 2017/18–2025/26 | Nine native PDFs; six accepted, three materially discrepant held |
| TRU | 2024/25 | Exact standalone native SOFI found; additional 2021/22–2023/24 board-package search leads remain to retrieve/verify |
| UBC | 2025/26 | Exact latest native SOFI found; current redesigned reporting index does not expose a complete older SOFI series |
| UNBC | 2024/25 | Rediscovered accepted source; pre-existing board-package historical leads need retrieval and final/adoption checks |
| UFV | 2019/20–2025/26 | Seven native PDFs |
| UVic | 2012/13 and 2018/19–2025/26 | Nine native PDFs; the old standalone 2012/13 attachment is genuinely linked; intervening periods need archive research |
| VCC | Search-located 2015 attachment only | Exact attachment returned HTML, not PDF; current page lists grids, statements and executive reports; adopted board archives/request route needed |
| VIU | Indexed 2010/11–2024/25 | Seven newer native PDFs retrieved; eight older links returned 503 and are **not verified documents** |

## Assumptions and procurement

A fiscal or calendar label is accepted only from the actual original schedule. Upload folders, link text and search snippets remain discovery evidence until checked. The inventory distinguishes native report headings from indexed years; a confirmed report cover still does not substitute for complete employee-table/period validation. Missing links are not proof an institution had no employees or never published a report.

Board honoraria, executive compensation disclosures, supplier schedules, salary grids and financial-statement aggregates are separate evidence. They are not silently promoted into complete employee salary histories. When a source has salary plus benefits, taxable benefits, or expense-inclusive totals, each component needs source-specific treatment. Ordinary source expenses remain missing where the original cell is blank/dash.

The immediate ordinary-records request candidates are **College of the Rockies, Justice Institute, Northern Lights and Selkirk**. Ask for complete adopted employee remuneration/expense SOFIs and original electronic schedules, including the three retained compiled labels (2017/18, 2020/21, 2023/24), the latest two fiscal years and available earlier archives. These are acquisition priorities, not assertions that those records are missing. Broader public archive research remains the first action for other historical gaps. A focused FOI request is a fallback if ordinary release fails. No municipality or institution was contacted.

The material SFU cases need scope/control review and, if unresolved, an issuer explanation or corrected original. A **third full independent engine** (pdfplumber/pdfminer) agrees with every candidate name/payment/page and row multiplicity for all three held cohorts; `held/third-reader-review.json` preserves that result. This does not establish the cause of their discrepancies, and they remain held. The complete rendered scope/control review and explanation are still outstanding.

## Reproduction and limitations

The SFU reproduction command and regression tests are documented in the accepted collection. Other PDFs are discovery receipts, not ready imports: candidate pages may include board/summary mentions, and native-text status alone does not establish a complete employee schedule. A processing task must verify internal fiscal headings, every name/title boundary, all monetary columns, page coverage, threshold/scope, signatures/adoption, row multiplicity and named/overall totals before import. The source bytes cached in `/tmp/pofbc-sector-education/` can be matched to each receipt’s `cacheFile` and SHA-256; use the recorded original URL if the temporary cache is absent. Guessed paths returning 404 and challenge pages are retained as failed research, not successful archive evidence.
