# Lower Mainland municipal recovery

Reviewed **31 October 2026, America/Vancouver**, against baseline `5e5fe01`.
This collection prepares **1,069 observations: 1,000 employees and 69 elected
officials**, in 23 cohorts from 16 original reports. Five previously uncovered
municipalities gain official records; employee coverage is complete for the
accepted Belcarra/Harrison schedules and explicitly partial for Abbotsford.
Richmond and Port Moody acceptance is council only.

| Municipality | Accepted calendar years | Employees | Council | Qualification |
|---|---|---:|---:|---|
| Abbotsford | 2023–2024 | 950 | 18 | 13 missing/dash benefit-component rows remain held |
| Belcarra | 2010, 2012–2014, 2017–2019, 2023, 2025 | 36 | 15 | Council accepted only for 2019, 2023, 2025 |
| Harrison Hot Springs | 2021–2022 | 14 | 13 | Complete tables; original publishes no named subtotals |
| Port Moody | 2024–2025 | 0 | 14 | Employee schedules remain held |
| Richmond | 2024 | 0 | 9 | Employee schedule remains held |
| **Total** | | **1,000** | **69** | |

[sources.json](sources.json) is the standard six-column normalized manifest:
`[employerSlug, name, position, remuneration, expenses, pdfPage]`.
Each source retains its original/index URL, SHA-256, actual January–December
period, physical pages, normalized/evidence hashes, definitions, control checks
and public warnings. [reviewed-layouts.json](reviewed-layouts.json) fixes row
counts, column boundaries, multiline row bounds, exact controls and review scope.

Every imported row and every retained held row must agree field for field between
PyMuPDF positioned words and Poppler bounding-box words. Complete table layouts,
component definitions, totals, boundary cases and all 13 held benefit-dash rows
were checked against rendered originals. All accepted Belcarra, Harrison and
council rows were visually checked individually. Abbotsford's larger employee
tables received layout/edge review plus complete dual-reader field and component
checks, rather than a claim of a second manual reading of every employee cell.
The manifest lists the actual visual-review pages. Two readers of an embedded OCR
layer are not independent originals; Richmond's nine council rows were therefore
checked individually against the rendered source. No names or titles were expanded
from the compiler or another year.

Independent cross-review caught Richmond's first salary currency symbol assigned
to the Mayor title. The position/salary column boundary was corrected, with no
change to monetary values. A literal `Mayor` regression and currency-token guards
for these reviewed sources now stop that field-assignment error.

The source assumptions are explicit:

- **Abbotsford:** 2023 pay combines the published Remuneration & Payouts and
  numeric Taxable Benefits columns. In 2024 it combines numeric Remuneration and
  Taxable Benefits & Payouts. The source report explains the component definitions
  and its combined group totals corroborate that treatment. Police and elected
  officials are excluded from the employee schedule; council is a separate cohort.
  The 2024 surname/initial disclosures are not expanded using 2023 names.
- **Missing benefit components:** 2023 has 460 source employee rows but 11 benefit
  dashes; 449 numeric-component rows are accepted. 2024 has 503 source rows and two
  holds; 501 are accepted. A dash is not inferred to mean zero, even when known-cell
  sums match a printed subtotal. Held names, positions, known remuneration cells,
  null benefit components, expenses and pages remain in `validation.heldRows` and
  complete component evidence. Both top-level and validation
  `completeEmployeeSchedule` are **false** for these partial cohorts, preventing a
  complete-schedule replacement inference. Public warnings identify the held rows.
- **Controls and subset totals:** `validation.controls` compares all known source
  component cells with printed full named-cohort controls. The source's
  `totalRemuneration` and `totalExpenses` cover the accepted numeric-component
  subset. Those scopes are intentionally distinct; a known-cell control match does
  not validate a missing component.
- **Belcarra:** the separate remuneration column is pay, including taxable benefits
  where specified. Expense-inclusive totals remain evidence only. Earlier council
  expense definitions require review; 2017/2018 explicitly combine expense
  allowance and ordinary expenses, so those earlier council cohorts remain held.
  In 2013, employee expense cells are blank and the source subtotal is a dash;
  records remain null and no numeric expense control is invented.
- **Harrison Hot Springs:** the original complete employee tables have seven rows
  each; council tables have five and eight. No named monetary subtotals are
  published. Counts and every rendered field are verified, with a public warning
  that calculated row sums are not issuer-subtotal reconciliations. Financial
  statement covers on physical p9 explicitly give December 31, 2021/2022; those
  scanned period headings were visually checked and their rendered hashes pinned.
  Only roles explicitly printed in council name cells are separated as positions;
  other positions remain missing.
- **Port Moody/Richmond council:** pay combines Base Salary and numeric Taxable
  Benefits/Benefits & Other. Ordinary expenses remain separate. No employee
  coverage is inferred from council acceptance.

These issuer differences remain unchanged and visible in `publicWarning`:

| Source | Row/known-cell sum minus printed component control, CAD |
|---|---|
| Abbotsford 2023 council | Indemnity +2; expenses −2 |
| Abbotsford 2024 employees | Known remuneration +0.01; benefits/payouts −0.01; expenses exact |
| Abbotsford 2024 council | Two expense-inclusive row totals differ from indemnity plus expenses by −1 and +1; separate pay/expense subtotals are exact |
| Port Moody 2025 council | Base salary +1; benefits −1; expenses +1; combined pay exact |

The cause is unknown; rounding is not asserted as the explanation. No individual
amount is balanced to a subtotal. Missing/dash expenses remain null, explicit zero
stays zero, and the parser preserves negative monetary values. Expense-inclusive
totals, aggregate payroll, employer CPP/EI and supplier payments are not individual
remuneration. All other available component controls reconcile exactly.

Abbotsford's original schedules were publicly recovered in official council-report
attachments despite its finance page saying SOFI is available on request. These
reports are not labelled draft. Their recommendation text is not represented as
proof of an adoption resolution or a signed approval form. Exact source links and
the published schedules remain the evidence for the disclosed payments.

```bash
# Offline source/evidence/data reproduction and policy regressions:
python3 scripts/parse_wave_lower_mainland.py --check-data
python3 scripts/test_wave_lower_mainland.py

# Re-fetch missing pinned originals and reproduce both readers:
python3 scripts/parse_wave_lower_mainland.py --fetch --cache /tmp/pofbc-wave-lower-mainland

# Independent reproduction without altering this collection:
python3 scripts/parse_wave_lower_mainland.py --cache /tmp/pofbc-wave-lower-mainland \
  --output-dir /tmp/cross-wave-lower-mainland

# Rebuild the bounded discovery inventory and task queue offline:
python3 scripts/inventory_wave_lower_mainland.py
```

The [next-pass inventory](../municipal-next-pass/lower-mainland/README.md) covers all
ten assigned municipalities and separates original processing from archive
research and records clarification. No compiled records or employer aliases were
changed; no municipal requests or messages were sent. Shared app registration and
generated exports are handled centrally.
