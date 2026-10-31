# Reviewed small municipal schedules

Reviewed 31 October 2026. This collection adds **192 named observations in 17
employee/council cohorts from nine original municipal PDFs**. Each accepted
schedule has a pinned original SHA-256, a verified calendar year, physical PDF
page provenance, retained extraction evidence, and reviewed monetary controls.

| Municipality | Calendar year | Employee rows | Council rows |
|---|---:|---:|---:|
| Golden | 2024 | 27 | 7 |
| Burns Lake | 2022 | 8 | 6 |
| Cache Creek | 2025 | 6 | 5 |
| Hudson’s Hope | 2022 | 12 | 11 |
| Montrose | 2023 | Held | 5 |
| Nakusp | 2024 | 7 | 5 |
| Valemount | 2024 | 6 | 5 |
| Mackenzie | 2025 | 35 | 7 |
| Peachland | 2025 | 33 | 7 |
| **Total** | | **134** | **58** |

## Validation and interpretation

`reviewed-layouts.json` records the inspected page, table boundaries, column
meanings, heading text, original fingerprint, expected count, printed controls,
and the exact accepted residual for every schedule. The parser reads every cell
with both PyMuPDF positioned words and Poppler bbox-layout words. Both extractions
must produce identical rows. Coordinates account for page rotation. A changed
document, missing pay anchor, unassigned table text, changed control residual, or
reader disagreement stops regeneration before writing accepted outputs.

The two text readers are not independent evidence that every embedded OCR glyph
is correct: they can read the same imperfect text layer. All accepted table pages
were therefore rendered and visually reviewed. A second reviewer checked the
small schedules and caught a two-line Mackenzie position assigned across adjacent
rows, plus the capital L in Valemount’s MacLean. Explicit source-specific
corrections retain their reviewed inputs and outputs; regression checks prevent
their reappearance. No first names, initials, or job titles are inferred from
outside the published schedules.

Named employee disclosures here are generally above $75,000; Peachland’s heading
uses an inclusive threshold. These are amounts paid during a reporting year, not
annual base salary rates or complete employee rosters. Council is a separate
category. Supplier payments and under-threshold aggregate payroll do not become
individual employee rows. Blank and dash expenses remain `null`; an explicit
numeric zero or “nil” remains zero.

## Decisions that affect comparison

- **Use the year in the schedule.** Golden’s accepted document is 2024,
  Hudson’s Hope is 2022, Montrose is 2023, and Nakusp is 2024. Later upload paths
  or labels do not move those observations into a later year.
- **Mackenzie:** remuneration is base pay plus “Other Compensation”. The printed
  total also includes expenses and is not remuneration. Both remuneration
  component subtotals reconcile exactly. Individual expenses total $70,221
  against the printed $70,220 subtotal; that $1 source residual is preserved.
- **Valemount employees:** the second monetary column combines expenses and
  taxable benefits. It remains in the component evidence and is not published as
  expenses. Employee expense values are therefore missing, not zero. The six
  remuneration rows have a $1 residual against the subtotal inferred from total
  payroll less the under-threshold aggregate. The combined component has a $1
  residual as well. Council expenses have a $1 residual.
- **Golden:** published remuneration includes base salary, per diems, taxable
  benefits and vacation payouts. The employee pay/expense residuals are +$1/+$2;
  council residuals are −$2/−$2. Surname-only names remain surname-only.
- **Burns Lake:** employee and council remuneration each sum $1 above their
  printed subtotals. Expenses reconcile exactly.
- **Montrose employees are held:** the three printed rows have $6,503.65 in
  expenses, while the printed employee total less its under-threshold aggregate
  implies $6,539.65. The $36 difference is unresolved. The five council records
  reconcile exactly and are accepted separately.

Small disclosed residuals are recorded source discrepancies. Rounding can be a
possible explanation for whole-dollar reports, but is not asserted as a proven
reconciliation. Individual cells are never altered to make a subtotal match.

## Remaining originals

The manifest also retains exact URLs, original hashes and follow-up actions for
scanned Creston 2024, Fruitvale 2023, Clinton 2024, Logan Lake 2025, Salmo 2024 and
Telkwa 2023 PDFs. Their covers were visually checked, but their named tables are
not accepted. A New Hazelton attachment named “SOFI 2023” begins with a remuneration
schedule headed “SOFI 2022”; its period needs review before OCR can establish
accepted records. These holds do not establish that a municipality has no salary
records or that its latest available year is the year of the downloaded report.

## Reproduce

Requires Python 3, PyMuPDF, and Poppler’s `pdftotext`. The committed word evidence
supports the offline regression suite without downloading PDFs:

```bash
python3 scripts/test_municipal_small.py
```

To obtain hash-pinned originals and reproduce normalized data and retained word
evidence in a fresh cache:

```bash
python3 scripts/parse_municipal_small.py --cache /tmp/pofbc-municipal-small --fetch
```

To reuse the originals reviewed in this session:

```bash
python3 scripts/parse_municipal_small.py --cache /tmp/pofbc-municipal/small
```

`sources.json` describes accepted rows and holds. `original-verification.json`
records the nine originals. Files in `evidence/` retain both positioned text
extractions, parsed component cells, the original fingerprint and all controls.
Only accepted normalized files participate in the ordinary offline salary build.
