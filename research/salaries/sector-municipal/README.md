# Municipal historical schedules

Reviewed as of **31 October 2026, America/Vancouver**. This collection contains
**411 observations: 360 employee disclosures and 51 elected-official disclosures**,
from seven original municipality-year reports, in 14 cohorts. It adds three
municipalities with no accepted official records in the `96d798e` baseline.

| Municipality | Calendar year | Employees | Council |
|---|---|---:|---:|
| Pitt Meadows | 2013 | 21 | 7 |
| Pitt Meadows | 2019 | 39 | 7 |
| Pitt Meadows | 2020 | 45 | 7 |
| Pitt Meadows | 2021 | 56 | 7 |
| Pitt Meadows | 2022 | 62 | 9 |
| Revelstoke | 2025 | 65 | 7 |
| Parksville | 2025 | 72 | 7 |
| **Total** | | **360** | **51** |

[sources.json](sources.json) contains exact original/index URLs, original and
normalized hashes, physical page references, calendar periods, counts, controls,
definitions and warnings. [reviewed-layouts.json](reviewed-layouts.json) fixes the
displayed table boundaries, row counts, component controls and literal corrections.
The six-column gzip rows follow the other municipal collections:
`[employerSlug, name, position, remuneration, expenses, pdfPage]`.

Every complete rendered table was visually checked. PyMuPDF and Poppler separately
extract positioned words, and every name, title and monetary field must agree after
explicit rendered-source corrections. These readers share the same PDF and any
embedded OCR layer; agreement alone does not establish correct transcription.
Retained word evidence allows offline reproduction. No aggregate payroll or
supplier payment is converted into an individual's compensation.

Pitt Meadows publishes salary/base salary and benefits/other compensation
separately. **Both components form remuneration**; expenses stay separate. Its
named threshold uses salary plus benefits/other, so rows below $75,000 base salary
remain in the disclosed cohort. Revelstoke uses the separate **Remuneration** column;
the employer costs in its financial-statement reconciliation are not added.
Parksville's employee remuneration **already includes taxable benefits**, vacation
payouts and supplemental acting pay. Missing/dash expenses remain missing; numeric
zero stays zero. These are payment disclosures above source-specific thresholds,
not complete staff rosters or annual base salary rates.

Pitt Meadows 2013 has imperfect embedded OCR. Five literal rendered-source fixes
are recorded: Councillor; Deputy CAO; $8,589 expense punctuation; Cheryl Harding's
base salary $102,476; and Business Analyst/IT Coordinator. The importer stops if the
pre-correction text changes. Other published spellings are retained.

Published individual values are not changed to force agreement. These exact
differences remain, shown as **individual row sum minus printed/derived named
control**, in CAD:

| Source/cohort | Remuneration difference | Expense difference |
|---|---:|---:|
| Pitt Meadows 2013 council | +3 | +1 |
| Pitt Meadows 2013 employees | +2 | −1 |
| Pitt Meadows 2021 employees | −2 | +1 |
| Pitt Meadows 2022 council | −1 | +1 |
| Pitt Meadows 2022 employees | −4 | 0 |
| Revelstoke 2025 council | −2 | −1 |
| Revelstoke 2025 employees | −1 | +1 |

Every other normalized pay/expense control is exact. Pitt Meadows 2021 council has
offsetting component differences (salary −$1, benefits +$1) with exact combined
remuneration and expenses. Component-level differences are preserved in the
manifest. Rounding is not asserted as the cause. The listed pay/expense differences
have `publicWarning` text for the app.

Revelstoke's signed approval on physical page 52 is dated June 23, 2026. Its source
form describes a remuneration-and-expense threshold, while its reconciliation
labels the cohort remuneration over $75,000; all 65 named remuneration values
exceed $75,000. The report's separate $143,643 payroll reconciliation variance is
context, not a correction to individual amounts.

Parksville's agenda attachment ends with an unsigned approval form. The official
[June 15, 2026 council minutes](https://parksville.civicweb.net/document/82769/),
resolution **26-129**, approve the 2025 SOFI **as presented**. The retained
[adoption receipt](adoption-evidence.json) and hash-checked HTML evidence establish
that these agenda tables were adopted. The form is not represented as signed.
The separate payroll-to-financial-statements reconciliation explains non-taxable
benefits, cash/accrual differences and City-managed joint ventures; those values
are not distributed among named employees.

No compiled records were removed and no aliases changed. The diagnostic
[overlap comparison](../sector-search-2026-10-31/municipal/compiled-overlap.json)
finds 43 exact employee name/pay/expense signatures between Pitt Meadows 2020 and
the compiled `2020/21` group. The official table has 45 employee rows and the
compiled group 44: one compiled name omits the leading B in Baldridge and Kerrie
Dykeman is absent. This is not complete cohort identity. Council dates are not
inferred from employee matches.

```bash
# Offline reproduction from both retained reader representations:
python3 scripts/parse_sector_municipal.py --check-data
python3 scripts/test_sector_municipal.py

# Fetch missing pinned originals and reproduce both positioned readers:
python3 scripts/parse_sector_municipal.py --fetch --cache /tmp/pofbc-sector-municipal

# Rebuild the findings/diagnostic overlap inventory from retained receipts:
python3 scripts/build_sector_municipal_inventory.py
```

The broader [municipal findings](../sector-search-2026-10-31/municipal/README.md)
cover 24 archive checks, 29 retrieved originals, remaining historical work and
procurement routes. Normal app registration is handled centrally; these files do
not themselves edit the shared collection registry or generated exports.
