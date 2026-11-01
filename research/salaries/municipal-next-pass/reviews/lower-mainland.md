# Lower Mainland independent cross-review

**Pass after two corrections. No outstanding blocker found in the reviewed collection.** Reviewed manifest SHA-256: `ee8cbcd5e67906c61cb2a2f82e65367644c61e0616f736b520da876fac62338c`.

The final collection contains **1,069 observations in 23 cohorts from 16 original reports**: 1,000 employee observations and 69 separately scoped council observations. I independently reproduced the originals into `/tmp/root-cross-lower-mainland-final`, verified all original/data/evidence fingerprints, and obtained byte-identical normalized files, supporting evidence and manifest. Offline reproduction and all **10 regression tests** pass. Author files were not edited by this review.

Rendered review covered Abbotsford's first and last employee pages and component controls for both years, all 13 held benefit-dash rows, both council tables, Belcarra's older employee/council separation and current table, both complete seven-row Harrison employee tables, Port Moody's council components and Richmond's full nine-row council table. This bounded review does not claim a new visual inspection of every Abbotsford employee row; full independent-reader agreement was reproduced for all rows.

## Corrections raised and independently cleared

1. **Abbotsford partial-cohort completeness flags were missing.** The author now sets `completeEmployeeSchedule=false` at both source and validation levels for both employee cohorts. This matters because the central compiled-period comparison treats absence of `false` as eligible for complete-group comparison. The warnings and held-row evidence were already present; the flags now make the replacement guard explicit.
2. **Richmond's first position contained a salary-column currency symbol.** `Brodie, Malcolm` previously had `Mayor $`; the rendered position is `Mayor`. The author corrected the reviewed column boundary so the currency token belongs to salary, regenerated evidence/data/hashes, and added a regression that rejects the old boundary. The final row is `['city-of-richmond','Brodie, Malcolm','Mayor',234800,1814,46]`. Counts and monetary values are unchanged. No other currency or summary-heading leakage was found in the 1,069 normalized name/position fields.

## Abbotsford components and partial coverage

| Calendar year | Original named employees | Accepted composite-pay rows | Held missing-benefit rows | Separate council rows |
| --- | ---: | ---: | ---: | ---: |
| 2023 | 460 | 449 | 11 | 9 |
| 2024 | 503 | 501 | 2 | 9 |

The 2023 pay mapping is published **Remuneration & Payouts plus numeric Taxable Benefits**; 2024 uses **Remuneration plus numeric Taxable Benefits & Payouts**. The explanatory memo distinguishes those components, and Schedule G's remuneration reconciliation supports combining them. Expenses and expense-inclusive council totals stay separate. Both employee headings explicitly exclude Police and Elected Officials and give the year ended December 31. The 2023 full names and 2024 surname/initial forms remain as published.

Every held row has a known remuneration-column amount, an actual published benefit dash and `pay=null` in full-source component evidence. All 13 raw dashes were checked against rendered originals; none becomes zero or a complete composite remuneration value. The accepted 950 rows each satisfy pay = the two disclosed numeric pay components. Held names/pages are retained and public warnings identify partial scope.

Full-original component controls use the complete 460/503-row evidence, not the accepted subsets. Accepted remuneration/expense totals independently equal their 449/501 normalized subsets. Control descriptions explicitly distinguish these scopes. Known 2023 salary, benefits and expense cells match their full named controls. Known 2024 salary cells differ by +$0.01 and benefits by −$0.01, with expenses exact; the warning preserves these residuals without adjusting published cells or claiming a cause. These full-original known-cell comparisons do not establish that missing benefits are zero.

The 2023 council indemnity/expense residuals (+$2/−$2) are warned separately. In 2024, two council expense-inclusive totals differ by −$1/+ $1 from indemnity plus expenses; separate pay/expense controls match, the discrepancies remain in evidence, and expense-inclusive totals do not become pay.

## Other scope and control checks

- **Belcarra:** 36 employee observations across nine calendar years. Pre-2019 council rows remain unimported pending treatment of expense allowances versus ordinary expenses; accepted employee cohorts are independently separated. The 2013 employee expense cells remain missing, and a printed dash is not used as a zero expense control. Later council cohorts remain separate. Explicit taxable-benefit inclusion is preserved where the source states it; expense-inclusive totals are supporting evidence.
- **Harrison Hot Springs:** seven employees in each of 2021 and 2022. The complete rendered tables contain no named employee subtotal. Both sources therefore have empty issuer-control lists, `namedControlUnavailable=true`, and public warnings that totals are calculated from disclosed rows rather than reconciled to an issuer subtotal. Wrapped positions, explicit zero expenses and the first/last rows match the normalized records. Calendar-year headings and separately pinned rendered financial-statement date evidence were reproduced. Council cohorts are distinct, with missing roles left missing where not explicitly printed.
- **Port Moody and Richmond:** this collection adds **council only**—seven rows for each Port Moody year and nine Richmond 2024 rows. It does not establish new employee coverage for either city. Base salary and numeric benefits/other are combined as the published pay components; expenses remain separate. Port Moody 2025's +$1 salary/−$1 benefits/+ $1 expense control residuals have an explicit warning. Richmond's component controls match, and its blank expense cell stays missing.

Reproduction used:

```sh
python3 scripts/parse_wave_lower_mainland.py --cache /tmp/pofbc-wave-lower-mainland --output-dir /tmp/root-cross-lower-mainland-final
python3 scripts/parse_wave_lower_mainland.py --check-data
python3 scripts/test_wave_lower_mainland.py
```
