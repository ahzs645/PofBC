# Southern Interior municipal disclosure expansion

This collection adds **299 official observations across nine new municipal jurisdictions**: **233 employees and 66 elected officials**, in **21 cohorts / 11 municipality-years**. Calendar periods and source definitions come from the originals. Compiled records, aliases and other collections are untouched by this importer.

| Municipality | Calendar years | Employee rows | Council rows |
| --- | --- | ---: | ---: |
| Barriere | 2023 | 5 | 7 |
| Clearwater | 2023, 2025 | 20 | 14 |
| Coldstream | 2021 | 19 | 7 |
| New Denver | 2025 | 1 | 5 |
| Princeton | 2023 | 19 | 5 |
| Rossland | 2025 | 33 | 7 |
| Sparwood | 2024–2025 | 61 | 14 |
| Summerland | 2023 | 60 | 7 |
| Sun Peaks | 2024 | 15 | — |

`reviewed-layouts.json` pins original PDF fingerprints, printed period evidence, complete row counts, table geometry, exact component controls and observed residuals. `sources.json` exposes each accepted cohort separately. Rows use `[employerSlug, name, position, remuneration, expenses, physicalPdfPage]`; source evidence retains both independently positioned PDF readings and all monetary columns. Expense-inclusive totals never become remuneration.

Reproduce from the current cache:

```sh
python3 scripts/wave_interior.py --cache-dir /tmp/wave-interior
python3 -m unittest discover -s scripts -p 'test_wave_interior.py'
```

Use `--fetch` for missing originals and `--output-dir /tmp/rebuilt-interior` for an isolated comparison. Python, PyMuPDF and Poppler `pdftotext` are required. Changed PDF hashes, reporting-period evidence, row counts, reader fields or pinned control residuals stop the rebuild. Eight offline regressions cover both reader reconstructions, fields at page boundaries, missing versus zero/negative values, published threshold exceptions, corrected recognition glyphs, expense-inclusive totals and changed originals.

All accepted pages were visually reviewed, including each first/last row and wrapped title boundary. [`edge-review.json`](../municipal-next-pass/interior/edge-review.json) records those checks. Some originals have recognition layers; rendered source glyphs establish the explicit corrections for Clearwater titles, Sun Peaks' McDougall name and several Sparwood 2024 names. Summerland's two employee pages retain all 60 published rows, accents and titles; row numbers and footnote asterisks are not names.

Names, initials, titles, amounts, source spelling and disclosure scope remain as published. Blank or dash expenses stay null, explicit zero remains zero, and negative amounts remain negative. These are payment disclosures rather than annual base salary rates or complete workforce rosters. Named remuneration and council schedules are separate; under-threshold aggregates, suppliers and employer contributions are not individual records.

## Qualified source controls

Nonzero source residuals have visible `publicWarning` text with exact amounts and an unconfirmed cause. No published amount was adjusted to force reconciliation.

- **Princeton 2023:** every field of all 19 employee rows agrees with both PDF readers, the rendered original and an independent review. Remuneration reconciles exactly. Known expense cells total **$70,697.11**, **$44.78 below** the **$70,741.89** control derived from all employees minus the under-threshold aggregate. Two published expense dashes remain null; the difference cannot be assigned to either cell or asserted to be solely a subtotal error. Two named employees with remuneration below $75,000 remain included as published exceptions; no general below-threshold coverage is inferred.
- **Coldstream 2021:** all 19 remuneration rows reconcile exactly. Individual expenses sum to **$23,794.17**, **$300 below** the **$24,094.17** subtotal. Expense-inclusive row totals likewise sum to **$1,849,000.21**, **$300 below** the **$1,849,300.21** subtotal. All expense cells are numeric and each printed row total equals pay plus expenses. The original arithmetic inconsistency remains disclosed without guessing which source amount is wrong.
- **Rossland 2025:** employee row sums minus printed named controls are **+$1 remuneration / +$5 expenses / $0 expense-inclusive totals**; council differences are **−$2 / −$1 / −$1**. The published employee schedule includes one below-threshold remuneration exception.
- **New Denver 2025 council:** **+$1 remuneration / −$1 expenses**. **Sun Peaks 2024 employees:** **−$1 remuneration / $0 expenses**.
- **Clearwater 2025:** the source prints a complete named employee remuneration subtotal but no named expense subtotal. Every individual expense was independently read and checked against the rendered page. No expense control was invented.

Princeton and Coldstream were qualified after [independent full-row review](../municipal-next-pass/north/cross-review-interior-held.md) and explicit central approval. Their complete named employee schedules have `completeEmployeeSchedule: true`; Princeton separately discloses partial expense information. Existing records are preserved without imputation or rescaling. Their unresolved controls remain clarification tasks in the follow-up queue.

The [follow-up inventory](../municipal-next-pass/interior/README.md) retains additional original histories, scans, unsuccessful retrievals and outstanding work. No request, email or other message was sent to a municipality.
