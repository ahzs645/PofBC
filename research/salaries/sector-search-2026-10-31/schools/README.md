# School district salary sources and histories

Audit date: **October 31, 2026, America/Vancouver**. The official provincial directory contains 60 districts; its number/name roster was cross-checked against all 60 reports on the [Ministry's FY2024/25 SOFI index](https://www2.gov.bc.ca/gov/content/education-training/k-12/administration/financial-management/school-district-financial-reporting/statement-of-financial-information). All 60 current reports were retrieved and fingerprinted. The prior app's 15 compiler employer entries represent 14 districts, because SD42 appears under two names.

The main deliverable is an actual [SD42 official collection](../../sector-schools/README.md): **10,568 observations**, comprising **10,446 employees and 122 trustees**, from **16 fiscal years / 32 cohorts**. Source originals, physical pages, reporting periods, monetary columns and controls are pinned. The importer does not change employer aliases or remove compiled data; central integration handles reviewed replacement decisions.

Start with:

- [`findings.json`](findings.json): all 60 district identities, existing compiler coverage, current original-source leads, located historical ranges, verified versus indexed periods, blockers and next actions.
- [`work-queue.json`](work-queue.json): normalized processing, public archive research and ordinary request tasks. OCR and parsing remain processing tasks.
- [`source-receipts.json`](source-receipts.json): exact original/index links, retrieved document hashes, table/text status, period evidence and row-control status. A retrieved report is not an accepted employee cohort.
- [`index-receipts.json`](index-receipts.json): district archive retrievals, relevant links and unsuccessful old URLs.
- [`district-roster.json`](district-roster.json): official district numbers/names and the provincial CSV receipt.
- [`sd42-identity-evidence.json`](sd42-identity-evidence.json) and [`sd42-compiled-overlap.json`](sd42-compiled-overlap.json): primary SD42 identity and category-specific compiled overlap evidence.

The Ministry explicitly says a district original should be considered representative if it disagrees with a Ministry convenience copy. Several district originals also have useful native text where their Ministry convenience copies are scans. Checking district originals can avoid unnecessary OCR or requests.

## Located histories

These are archive link ranges, **not** claims that every period has accepted rows. Fiscal years end June 30. Exact gaps, downloaded reports and verified headings are recorded separately in the inventory.

| District | Located fiscal years, by ending year |
| --- | --- |
| Maple Ridge–Pitt Meadows (42) | 2005–2026 |
| Vancouver (39) | 2009–2025 |
| West Vancouver (45) | 2013–2025 |
| Nanaimo–Ladysmith (68) | 2015–2025 |
| Chilliwack (33), Langley (35) | 2018–2025 |
| Surrey (36), Sooke (62), Gulf Islands (64) | 2019–2025 |
| Coquitlam (43), North Vancouver (44), Greater Victoria (61) | 2020–2025 |
| Abbotsford (34), Burnaby (41), New Westminster (40), Richmond (38) | 2021–2025 |
| Delta (37) | 2023–2025 |
| Southeast Kootenay (5) | 2024–2025 on the retrieved current archive |
| Mission (75) | Current Ministry 2025; district 2024 original recovered; two older original URLs returned 404 |

Richmond's current page reports eight files but initially exposes five; earlier pagination needs further review. Search snippets suggesting a longer SD5 archive were not substituted for the retrieved current page's two original links. Nanaimo's `/document/*.pdf` URLs are HTML wrappers: the original PDF is the embedded iframe, which was followed and fingerprinted separately. Several websites have migrated, so old URL failures are retained without treating them as proof of missing reports.

All current districts have an official FY2024/25 source lead. Deeper archive research remains incomplete for many of the other districts and for years earlier than these located sets. District numbers are discovery keys; historical employer identity and renamed districts still require review. Neither an index link nor an audited financial statement alone establishes accepted individual salary coverage.

## OCR completed as discovery; acceptance still pending

All six scanned SD42 originals (ending 2007–2009 and 2011–2013) received OCR across **296 physical pages**. **95 candidate pages** mentioning remuneration, employees or trustees have a second layout pass. [`ocr-staging/index.json`](ocr-staging/index.json) records source hashes, page lists and evidence files; each compressed evidence file retains the first-pass page text and second-pass candidate text.

No OCR candidate has been imported. Two layout modes of one Tesseract engine are discovery evidence. Next work is to identify the complete employee/trustee boundaries, compare every name, title, amount, sign and missing value against rendered originals, obtain an independent reading and reconcile full named-cohort controls.

Reproduce:

```sh
python3 scripts/sector_schools_ocr.py --cache-dir /tmp/pofbc-schools --workers 4
```

For a fresh cache use `--download`. The script verifies pinned originals before rendering. The native accepted collection has its own reproduction command and six regression checks in its README. Current working PDF cache: `/tmp/pofbc-schools`; a fresh environment can retrieve exact document links from the manifests/receipts and verify their SHA256 values. PDFs are not copied into Git.

## What needs procurement or further research

No current FY2024/25 district SOFI requires procurement simply because its tables need processing. The Ministry says the **BC Legislative Library retains previous years' SOFIs**, and districts may also provide copies. For every district, the queue therefore distinguishes processing a located report from finding earlier originals.

**Abbotsford** explicitly offers signed versions and years earlier than its online five-year set through its Finance Department. Its pre-2020/21 history is an ordinary records request candidate, after checking available library records. **Mission's 2021/22 and 2022/23 original URLs** returned 404; search migrated district attachments or library copies before requesting replacements. Other earlier histories remain public archive research tasks until those routes are checked.

A useful request, if needed, would seek existing annual SOFI employee and trustee schedules, original spreadsheets or accessible PDFs, the exact fiscal period and existing explanatory/reconciliation notes. Requesting existing records informally comes before considering an FOI fallback. No blanket claim is made that unavailable web links require FOI. No requests, emails or other messages were sent.

## Acceptance assumptions

School fiscal years run July 1–June 30; headings establish periods. Employee named schedules commonly disclose remuneration above $75,000, but each source must establish its threshold and compensation columns. Trustee remuneration is a separate scope. Cash-basis payment disclosures can include taxable benefits and leave or retirement payments and differ from accrual financial-statement salary expenses. Suppliers, aggregate payroll and executive-only summaries must not be converted into broad employee cohorts.

The SD42 records preserve source names, titles, missing expenses, negative amounts and source-specific residuals. Four whole-dollar cohorts carry explicit public warnings for their exact row-sum-minus-control differences. Matching a financial total is one control; names, row boundaries, periods, complete scope and independent source readings are also required.
