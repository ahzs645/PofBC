# Vancouver Island and coastal municipal remuneration

Reviewed on **2026-10-31**. This collection contains **10,967 named annual records in 33 cohorts for eight employers**, supported by 29 distinct primary PDF or CSV releases. It includes 10,939 employee records and 28 elected-official records. These are accepted source records; the number of net additions to the existing compiled dataset must be determined during integration.

The broader discovery inventory covers **42 municipalities** and **229 official source/archive links**. Discovery links may lead to archives, agenda attachments or reports that still need inspection. They are not treated as accepted salary records. Eleven specifically attempted sources are held with reasons in `reviewed-inputs.json` and `sources.json`.

## Accepted coverage

| Employer | Employee years | Employee records | Elected-official records |
| --- | --- | ---: | ---: |
| City of Victoria | 2012–2014, 2016–2025 | 5,544 | 0 |
| City of Nanaimo | 2019, 2021–2025 | 2,579 | 0 |
| District of Saanich | 2021–2025 | 2,525 | 0 |
| City of Duncan | 2024 | 20 | 7 (2024) |
| District of Sechelt | 2024 | 36 | 7 (2024) |
| District of North Cowichan | 2024 | 130 | 0 |
| District of Central Saanich | 2024 | 65 | 7 (2024) |
| Town of Comox | 2024 | 40 | 7 (2024) |
| **Total** | | **10,939** | **28** |

Every period is a calendar year, January 1 through December 31. Employee and elected-official cohorts use distinct supported categories. Police-board schedules are not silently merged with municipal employee schedules. A missing year or council cohort is a coverage gap, not evidence that no disclosure exists. Victoria 2015 was not found in the reviewed employee CSV catalog.

## Files and source traceability

- `sources.json` is the collection manifest. Each accepted source has its original URL, index URL, SHA-256 of source bytes, physical PDF pages, output hashes, row count, totals, disclosure details, and validation results.
- `reviewed-inputs.json` pins the exact reviewed files, page boundaries, expected counts and totals, layout repairs, and hold reasons. Changes to source bytes fail before extraction.
- `*.json.gzip` contain compact normalized rows in the manifest's explicit schema: `employerSlug, name, position, remuneration, expenses, pdfPage`.
- `raw/` retains the exact official Victoria CSVs and the official ArcGIS catalog response. The catalog establishes the `CityOfVictoriaBC` owner and the year/scope of each CSV item. Primary PDFs are downloaded on reproduction and checked against pinned hashes.
- `review/` retains Victoria's separate remuneration, taxable-benefit/payout and expense columns, including physical page references.
- `validation.json` retains per-cohort checks, page counts, missing and negative expense counts, printed controls, source residuals and CSV/PDF differences.
- `discovery.json` records the searched official index for every jurisdiction in scope, candidate URLs, observed access limitations, acceptance status and remaining work.

The official archive pages are linked individually in each source record. The main histories come from the [Victoria SOFI archive](https://www.victoria.ca/city-government/resources/statement-financial-information), [Nanaimo financial reports](https://www.nanaimo.ca/your-government/budget-finance/annual-financial-reports/finance-division), and [Saanich financial reports](https://www.saanich.ca/EN/main/local-government/departments/finance-department/financial-reports.html). Victoria's CSV item URLs are preserved exactly; each item is corroborated against the official catalog, not a third-party salary database.

## Meaning of the amounts

`remuneration` preserves the column published by the municipality. It is **annual remuneration**, which can include overtime, taxable benefits, payouts or partial-year employment according to the source. It is not a standardized full-time base salary. Municipal figures are consequently not automatically comparable on a like-for-like basis.

Victoria publishes remuneration separately from taxable benefits and payouts. This collection preserves the remuneration field and stores the separate component in the review ledger. It does not add that component silently. The disclosed cohort threshold can consider both columns, so some individual Victoria remuneration amounts below $75,000 are valid source rows. Central Saanich expressly labels its cohort "$75,000 or More"; its threshold rule is recorded as `at-least`. Published surname/initial forms remain initials; no names or missing job titles are guessed.

Expense dashes and blanks remain `null`; an explicit numeric zero remains zero. Five negative expense amounts are retained as published. There are 2,515 missing expense cells across the accepted collection. These conventions are covered by offline tests. Names and initials are source labels, not unique person identifiers.

## Validation and material discrepancies

For Nanaimo, Saanich and the five smaller municipalities, Poppler layout extraction is checked independently against PyMuPDF's positioned monetary cells **and their associated names**. This detects an amount attached to the wrong person even when a page's total would still match. Source names and titles must also appear in the independent extraction. All named subtotals and row counts are pinned. Representative schedules and the additional small-municipality control pages were rendered for visual review.

Saanich contains wrapped names, nicknames and positions. Those continuations are retained, including `Jonnalagadda, Sai Sashank`. The 2025 Blick McStravick row places its expense above the salary line; the explicitly pinned repair is corroborated by the original positioned PDF block. Source group headings such as `Exempt` are excluded from names.

For Victoria 2016–2025, each named CSV identity and role is matched to the original PDF, subject to explicitly reviewed title differences and three clipped initials in the 2023 PDF. The PDF monetary values take precedence. All three monetary columns are summed and checked against the reviewed PDF controls. Every discrepancy with the companion official CSV remains in `validation.json` rather than being concealed.

Two material examples are:

- **Victoria 2022:** original-PDF named expenses total **$449,361.17**, whereas the companion CSV totals **$458,934.21**; the difference is **$9,573.04**. The PDF values are retained.
- **Victoria 2023:** original-PDF remuneration totals **$60,220,822.36**, compared with **$60,174,227.02** in the CSV. The **$46,595.34** difference is offset by the separate benefit/payout column. The collection retains the PDF's published column allocation.

Victoria 2012–2014 are official machine-readable releases with verified catalog ownership, year, schema, row counts and monetary totals. **Original-PDF reconciliation has not been completed for those three early releases.** Their validation metadata explicitly distinguishes that basis from the later PDF-backed cohorts.

Individually displayed values sometimes do not sum exactly to a printed subtotal. No balancing rows or adjusted salary amounts are invented. Residuals are stored as extracted row sum minus printed named subtotal:

| Cohort | Remuneration residual | Expense residual | Source display |
| --- | ---: | ---: | --- |
| Victoria 2018 employees | +$0.01 | $0.00 | Cents |
| Victoria 2020 employees | $0.00 | +$0.01 | Cents |
| Victoria 2024 employees | −$13.00 | +$8.00 | Whole dollars |
| Victoria 2025 employees | −$9.00 | +$17.00 | Whole dollars |
| Sechelt 2024 employees | +$1.00 | +$1.00 | Whole dollars |
| Sechelt 2024 council | +$2.00 | $0.00 | Whole dollars |
| North Cowichan 2024 employees | +$3.00 | +$1.00 | Whole dollars |
| Comox 2024 employees | −$1.63 | +$3.95 | Mixed cents/whole dollars |
| Comox 2024 council | $0.00 | +$1.33 | Mixed cents/whole dollars |

All other accepted PDF cohorts reconcile exactly to the reviewed named remuneration and expense controls. Residuals in Victoria's separate benefit/payout column are also retained in the component audit. Display rounding is consistent with small residuals in whole-dollar tables; the file retains the observed differences rather than asserting an unverified cause.

## Held sources and next work

The eleven explicit holds are:

| Source | Reason |
| --- | --- |
| Nanaimo 2020 | OCR/text extraction fails the printed monetary controls; no rows accepted |
| Campbell River, Gold River, Lantzville, Metchosin, Sayward 2024 | Scanned originals require positioned OCR and full control checks |
| Cumberland 2024 | Wrapped name/title and monetary layout needs a separate validated profile |
| North Saanich 2024 | Mixed scanned/text document needs complete schedule extraction and checks |
| Lake Cowichan 2024 | Distinct remuneration/expenses/total layout not yet validated |
| Tahsis and Gibsons 2024 | Original report requests returned HTTP 403 |

Other candidate years and municipalities remain in discovery status. Several official archives are extensive, including Tofino, Colwood, Langford, Lantzville and North Cowichan. These are recorded follow-up opportunities; no unparsed PDF is promoted to accepted data. Access failures reflect this review session, not a claim that records are legally unavailable or permanently inaccessible. The shíshálh Government District is outside this municipal collection's governance scope and is handled separately in the broader project.

## Reproduce and test

The parser uses Python, PyMuPDF (`fitz`) and Poppler's `pdftotext`. The reviewed run used Python 3.12.14, PyMuPDF 1.26.6 and Poppler 24.02.0. From the repository root:

```sh
python scripts/parse_municipal_island.py --source-dir /tmp/municipal-island --fetch
python scripts/test_parse_municipal_island.py
```

`--fetch` downloads only exact pinned URLs when files are absent. Retained CSV/catalog snapshots can also populate a missing cache. A changed source hash, ambiguous layout, wrong period, unexpected identity, missing row, mismatched monetary cell or changed total aborts the run. It never silently approves a newly changed PDF. To reproduce entirely offline, supply the original PDF files listed in `reviewed-inputs.json` in the source directory.

The six focused tests cover scope boundaries, missing/zero/negative expenses, Saanich wrapped names and expense placement, Victoria's separate benefit column and source precedence, source-byte changes, per-person monetary association, and generated collection hashes/counts/totals. Extraction builds all outputs in memory and writes the collection only after every accepted cohort passes validation. The parser does not delete or replace any compiled dataset partition; source integration and comparison with existing records are separate project-level steps.
