# Municipal salary continuation — 1 November 2026

This collection contains **1,216 verified observations**: **1,075 employee** and **141 elected-official** disclosures from **20 original reports**, **37 separate cohorts**, and **10 employers**. Nine employers previously had no accepted official records. The bounded continuation raises municipal official coverage from **101 to 110 of 161** current jurisdictions and employee coverage from **100 to 107**. **51 current jurisdictions still lack an accepted official cohort.** Historical completeness is not established.

| Employer | Calendar years added | Employee rows | Council rows |
|---|---|---:|---:|
| Campbell River | 2016–2022 | 710 | 55 |
| Salmon Arm | 2022, 2024 | 76 | 15 |
| Port Edward | 2024, 2025 | 0 | 10 |
| Metchosin | 2025 | 11 | 5 |
| Fraser Lake | 2023 | 8 | 5 |
| Wells | 2020 council only | 0 | 5 |
| Grand Forks | 2024 | 34 | 7 |
| Lake Country | 2025 | 81 | 7 |
| Elkford | 2022 | 18 | 11 |
| Revelstoke | 2021, 2023, 2024 | 137 | 21 |

[sources.json](sources.json) is the only publication manifest. Every cohort pins the original SHA256, deterministic normalized-gzip SHA256, source/index links, true calendar period, physical pages, scope, pay definition and review evidence. [reviewed-layouts.json](reviewed-layouts.json) pins exact row boundaries, columns, literal corrections, controls and residuals. The normalized six-column schema is `employerSlug,name,position,remuneration,expenses,pdfPage`.

Native schedules were independently read with PyMuPDF and Poppler and every accepted rendered row was reviewed. Metchosin, Fraser Lake and Wells have image salary tables: one Tesseract transcription was compared against complete independent manual image transcription; this is not a claim of two independent OCR engines. Elkford has an issuer-provided OCR overlay, compared in two PDF readers and checked completely against its original image. [rendered-review.json](rendered-review.json) records every reviewed page and image fingerprint. Raw word-level evidence remains in `evidence/`; no text-layer or normalized value was changed to force a subtotal to balance.

Source qualifications remain visible in the manifest:

- Campbell River preserves exact whole-dollar source residuals. Council pay differences are −3 (2016), +2 (2017), −1 (2018), +1 (2021), and −1 CAD (2022). Employee pay/expense residuals are −1/0 (2016), +1/+3 (2017), −1/+3 (2018), +4/+3 (2019), +2/+1 (2020), 0/0 (2021), and +6/+3 CAD (2022). The complete 2020 employee control is on physical page 9, retained in supporting control evidence in addition to its salary pages 6–8. Causes remain unknown.
- Salmon Arm 2024 council pay/expense differences are −2/+1 CAD; employees are +1/+1 CAD. Council pay uses the chosen Remuneration field, excluding its separately disclosed Life & Health Benefit. A merged `ChelseaChief` text-layer token is split into the printed name and title; original clipped titles are retained. The invisible Poppler-only `Engineer` glyph run beyond Wilson’s visible `Coordinator/City` title is excluded with an exact token/rectangle guard. Frese’s clipped visible title ends `Plan`.
- Port Edward 2025 council expenses sum to 41,436 versus the printed 41,437 CAD control. Its employee pages remain held: missing Other Remuneration cells and a field labelled Total Remuneration that includes expenses require clarification. Expense-inclusive totals are never used as pay.
- Metchosin separately displays Taxable Benefits while its note defines Remuneration as including taxable benefits. The normalized measure retains the source’s chosen Remuneration column without a second addition; that interpretation is stated publicly and separate components remain in evidence. All known original controls agree. Dunlop’s unpublished expense is null; under-threshold `n/a` components are not zero.
- Wells council has its own explicit 2020 heading and four printed zero expenses. The same original’s employee subsection says `Staff 2018` beneath a 2020 schedule heading; that employee is held without assigning a year. Council dates do not resolve employee dates.
- Grand Forks faithfully retains Klein, Tanis at 74,917 remuneration despite the over-75,000 cohort label; its expense-inclusive total is 75,490. Council Remuneration excludes separate general Benefits, matching the source reconciliation measure. Every named control agrees.
- Lake Country uses Taxable Remuneration and the named employee expense subtotal. Employer EI/CPP in the broader expense grand total is outside that comparator. All named controls agree.
- Elkford retains council pay −2/expenses +1 CAD and employee pay +1 CAD relative to the exact printed/derived named controls. Four OCR-overlay comma spaces and one office slash spacing were restored from the rendered original with strict raw-text guards; `Kliment,E` stays compressed as visibly printed. Counts and amounts are unchanged.
- Revelstoke’s three historical employee and council cohorts each reconcile exactly to their own named controls. Office prefixes inside council Name cells are separated into the normalized position field. Misspellings such as `Utilties` are retained.

Blank/dash expenses remain null; literal zeros remain zero. All imported employee cohorts cover the complete published named schedule, not all employees on payroll. Aggregate payroll and suppliers are never converted to people. Every accepted employer has **zero compiled baseline records**, so these imports neither replace compiled partitions nor remove council/board/executive observations. No alias or old-source changes are made.

The [province-wide continuation inventory](../continuation-2026-11-01/municipal/README.md) retains all 161 fresh primary-archive checks, all 60 uncovered-jurisdiction web searches, exact original receipts, historical leads and draft acquisition/clarification tasks. Okanagan Falls remains pending incorporation on 6 November 2026; shíshálh Nation Government District remains a separate governance/employer case. No outreach, formal request or fee commitment was made.

## Reproduce

```sh
python3 scripts/continue_municipal.py --cache /tmp/continuation-municipal --fetch
python3 scripts/continue_municipal.py --check-data
python3 -m unittest discover -s scripts -p 'test_continue_municipal.py'
```

Original-backed extraction requires PyMuPDF, Poppler and Tesseract for the small scanned schedules. Offline evidence replay requires no PDFs, network or OCR process. It guards all payload/evidence bytes, exact source controls, scoped residuals, row multiplicity, literal corrections and manual transcripts. The 13 regression tests cover wrapped titles, row ambiguity, missing-versus-zero values, expense-inclusive totals, clipped-glyph guards, original correction context, exact overlay spacing, offline replay and acquisition schema.

Exploratory `*-layouts.json` files and configuration helper scripts preserve candidate preparation stages. Publication and validation read only `reviewed-layouts.json` and `sources.json`. [freeze.json](freeze.json) pins final accepted inputs, scripts and payloads for independent review and integration.
