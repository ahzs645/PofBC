# Northern municipal salary history

Audit date: **2026-10-31, America/Vancouver**. This collection adds **1,349 official payment disclosures across 60 employee/council cohorts** from six municipalities. Three separate manifests keep the reviewed core, small-village additions and council additions independently reviewable.

| Municipality | Calendar years added | Employees | Council |
| --- | --- | ---: | ---: |
| Williams Lake | 2011–2023 | 394 | 100 |
| Northern Rockies Regional Municipality | 2015, 2017, 2019–2023 | 339 | 51 |
| Dawson Creek | 2017, 2019–2023 | 362 | 46 |
| Chetwynd | 2018–2019 | 26 | 17 |
| Hazelton | 2024 | 2 | 6 |
| Port Clements | 2025 | 1 | 5 |
| **Total** | | **1,124** | **225** |

- [Core employee sources](sources.json): 1,121 records / 28 cohorts.
- [Small-village employee supplement](supplemental/sources.json): 3 records / 2 cohorts.
- [Historical council supplement](council/sources.json): 225 records / 30 cohorts.
- [Discovery receipts and remaining work](../municipal-history-pass/north/README.md).

All reports are originals retrieved from municipal publication or council-document archives. The manifest records exact original URLs, index URLs, SHA-256 fingerprints, calendar periods, normalized data hashes, row counts, known-cell sums and printed controls. Council and employee schedules remain distinct. No compiled records are deleted or relabelled.

## Meaning of the records

These are published payment disclosures, not complete workforce rosters or annual base-salary rates. `remuneration` uses the original remuneration/pay column. Expenses remain separate. Port Clements expressly includes taxable benefits in remuneration; its expense-inclusive `Total` is retained only in evidence. Northern Rockies prints **Department**, not position: every normalized position is null, with the original department preserved in evidence.

Williams Lake 2012–2014 does not publish an employee-name column. Its 71 employee records therefore have `name:null` and the exact printed position. The same years' 21 council rows print a Position column with Mayor/councillor labels and sometimes surnames; these complete labels remain in position while name stays null. No identities or reason for omission are inferred. These unnamed disclosures remain useful in employer and position views; the app's people index skips null names.

Printed dashes/blanks stay null, explicit numeric zero stays zero, and negatives are supported. Published initials, capitalization, accents and literal title spellings are preserved. Names and roles do not pass through a global letter or currency-token filter. Wrong currency boundaries fail validation; reviewed geometry assigns dollar symbols to monetary columns.

## Controls and source qualifications

Known individual amounts are never changed to force agreement. Exact residuals are pinned per component, with visible source-specific public warnings whenever controls differ. No unexplained difference is attributed to rounding.

- Williams Lake 2011–2014 has numeric all-employee and under-threshold amounts for both components, so named/position-cohort controls can be derived by subtraction.
- Williams Lake 2015–2023 prints a **blank under-threshold expense cell**. The all-employee expense total cannot become a named-only control by assuming that blank is zero. Evidence retains the broader comparison and `namedExpenseControlAvailable:false`, including years where the two known sums happen to agree.
- Williams Lake 2019 retains all 33 employee rows. Their remuneration sum is $3,153,276, exceeding the valid derived pay control ($8,305,122 − $5,235,081 = $3,070,041) by **$83,235**. That equals the first published pay cell; its cause is unknown. Known named expenses are $100,858 versus a printed **all-employee** $100,855, with under-threshold expenses unknown. No first row is dropped and no formula-error explanation is asserted.
- Other accepted employee pay residuals are Williams Lake 2015 −$2, 2016 +$4, 2018 +$4, 2020–2022 −$1 each, 2023 −$2; Northern Rockies 2019/2020 −$1 each, 2021 +$2, 2022 −$2, 2023 −$1. Northern Rockies named expenses differ by −$1 in 2022 and −$2 in 2023. Complete source scope and faithful cells were checked before qualification.
- Council warnings similarly retain the exact component differences: Williams Lake 2015 expenses −$1; 2018 expenses +$1; 2020 pay −$3 / expenses +$2; 2021 pay −$2; 2022 pay +$2; 2023 pay −$2 / expenses +$1. Northern Rockies 2019/2023 expenses +$1 each and 2022 pay +$2. Hazelton 2024 council expenses +$0.10. Remaining council component sums agree exactly.
- Hazelton's named employee component controls agree exactly. Its broader accounting reconciliation prints a $3,318.41 variance and an employee remuneration-plus-expense reconciliation line $199 above the component totals. These broader lines are disclosed separately and do not change individual values.

## Reproduction

Requirements: Python 3, PyMuPDF, and Poppler `pdftotext`.

```sh
python3 scripts/parse_history_north.py --cache /tmp/pofbc-history-north --fetch
python3 scripts/parse_history_north.py --cache /tmp/pofbc-history-north --fetch --supplemental
python3 scripts/parse_history_north.py --cache /tmp/pofbc-history-north --fetch --council
python3 scripts/parse_history_north.py --check-data
python3 scripts/parse_history_north.py --supplemental --check-data
python3 scripts/parse_history_north.py --council --check-data
python3 scripts/test_history_north.py
```

Original reproduction checks the pinned original fingerprint, actual reporting-period proof, every selected field with both PyMuPDF and Poppler positioned words, all source component controls and reviewed residuals. Only reviewed salary pages are passed to Poppler, avoiding an unrelated invalid XML control character in one financial-statement page. Evidence preserves original row cells in cents and physical PDF page numbers. Offline reproduction validates every data/evidence binary and source manifest. Fourteen regressions cover missing-versus-zero semantics, null names, A initials, departments, wrapped titles, currency boundaries, expense control scope, council scope and the explicitly archived prior metadata amendment.

Rendered table-page fingerprints and checks are in [rendered-review.json](../municipal-history-pass/north/rendered-review.json). Williams Lake 2015's embedded text contains one ink-speck artifact after Hutton's `Planner 1`; a single pinned before/after cell correction is recorded in reviewed-layouts.json and checked against the rendered original. All other text is retained directly.

## Explicit amendment to earlier metadata

This work also corrects **only metadata** for previously accepted Williams Lake 2024/2025 employee expense-control scope. Original PR27 manifests, configuration, parser and README were archived before the authorized edit, with an explicit [correction ledger](../municipal-history-pass/corrections/north-expense-scope/corrections.json). The old named-expense interpretation becomes a broader all-employee comparison with blank under-threshold expenses unknown. All 24 prior data/evidence gzip binaries remain byte-identical, and all 401 earlier North records and monetary amounts are unchanged. No other prior collection is edited by this work.
