# Southern Interior historical salary schedules

This collection adds **632 official observations: 454 employee and 178 council/former-council payments**, in 46 cohorts from 23 original reports. One additional Lytton 2022 original is verified as an explicitly empty named employee schedule with aggregate payroll only; it creates no person records. Audit date: October 31, 2026, America/Vancouver; verification completed November 1 UTC.

| Municipality | Newly accepted calendar years | Employee rows | Council rows |
| --- | --- | ---: | ---: |
| Sparwood | 2012–2023 | 215 | 96 |
| Trail | 2022–2024 | 131 | 26 |
| Rossland | 2015,2021,2022,2024 | 73 | 33 |
| Clearwater | 2024 | 10 | 7 |
| Princeton | 2022 | 20 | 5 |
| Lytton | 2021,2023 | 5 | 11 |
| Total | 23 municipality-years | 454 | 178 |

The [manifest](sources.json) identifies each exact official original/index URL, SHA 256, original physical page, normalized data/provenance hash, printed period, source controls and public warning. [Reviewed layouts](reviewed-layouts.json) pin complete row boundaries and column meanings. The [audit guide](../municipal-history-pass/interior/README.md), [inventory](../municipal-history-pass/interior/source-inventory.json) and [remaining queue](../municipal-history-pass/interior/work-queue.json) distinguish accepted periods from unverified archive labels and processing tasks. Existing compiled records and employer identities are untouched by this collection.

## Source decisions

Every row agrees field by field between independently positioned PyMuPDF and Poppler words. Rendered originals establish headings, period, scopes, employee edges, wrapped text and monetary controls; full council tables and residual-bearing employee tables were reviewed. Employee job titles remain missing when only council has a Position column. Standalone initials, publisher spellings and clipped titles are retained, including Rossland's printed `Manager of Operations &` and `Bylaw Officier`. Missing/dash expenses stay null; explicit zeros remain zero. Expense-inclusive totals never become pay.

Rossland 2021 publishes remuneration and taxable benefits separately. Both components are known for every accepted row; their sum is remuneration. The published expense-inclusive total remains supporting evidence. Printed component subtotals are retained independently; no missing component becomes zero. Rossland 2015's SOFI checklist explicitly states fiscal year end 2015; its June 2016 memorandum/submission dates do not change the reporting period. For schedules stating only an annual fiscal year, [Community Charter section 164](../municipal-history-pass/interior/calendar-period-authority.json) establishes that municipal fiscal years are calendar years.

All nonzero row-sum-minus-control differences have visible exact public warnings; their cause is unconfirmed. This includes small Rossland/Trail differences and the independently reviewed Sparwood 2018 council(+55,310 remuneration), Sparwood 2022 employees(+190 known expenses), Sparwood 2023 employees(+232,018 remuneration/+6,089 known expenses), and Princeton 2022 employees(+13,775 remuneration/−9,340.53 expenses). No cells were altered or omitted to balance a subtotal. [Independent review](../municipal-history-pass/reviews/interior-qualified-history.md) records the four larger decisions. Princeton's nonstandard dotted amounts retain every digit and the final two cents; the wrapped `PARSLEY, MARUEEN M` title is `ESS Supervisor & Recovery Manager`. Published below-threshold rows remain intact.

Lytton 2023's published officials table mixes seven explicit Mayor/Councillor/former-council payments with three fire chiefs. Only the seven explicit council roles are accepted here; all ten original rows and the three excluded fire-service rows remain in the council evidence. The employee/volunteer category of those three payments remains held. The Lytton 2022 employee section explicitly says `None`; its under-threshold remuneration 181,393.87/expenses 10,611.11 are retained as aggregates, without synthetic individuals. The separately ambiguous 2022 officials group remains held.

These payment disclosures are threshold schedules, not complete employee rosters or annual base salary rates. Source selection rules and definitions still matter when comparing employers. An explicit `over` comparison is recorded only where the source prints it.

## Reproduce

Use the retained originals in `/tmp/wave-interior`, or pass `--fetch` to retrieve exact official URLs into another cache. Changed original hashes fail before extraction. Reproducing source interpretation requires PyMuPDF and Poppler's `pdftotext`; no OCR is used for these accepted cohorts.

```sh
python 3 scripts/history_interior.py --cache-dir /tmp/wave-interior
python 3 scripts/history_interior.py --cache-dir /tmp/wave-interior --output-dir /tmp/history-interior-rebuild --render-review-dir /tmp/history-interior-renders
python 3 -m unittest discover -s scripts -p 'test_history_interior*.py'
python 3 scripts/history_interior_inventory.py
```

A separate rebuild produced identical bytes across all 95 generated manifest/data/provenance files. Fourteen historical/correction regression tests passed, alongside nine prior Interior tests. Tests cover complete independent-reader reproduction, original/data/provenance hashes, calendar/category uniqueness, literal initials, boundaries, source spellings, zero versus missing values, remuneration components, mixed-group selection, the explicit empty schedule, and approved residuals. The previous PR 27 initial repair has its own [unaltered archival snapshot and exact amendments](../municipal-history-pass/corrections/interior-initials/README.md); it changes eight published name initials and zero monetary cells or record counts.

No municipality was contacted and no FOI request was submitted.
