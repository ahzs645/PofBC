# Independent review of the small-municipality collection

Reviewed **2026-10-31** by a separate task agent after extraction and before final integration. **No unresolved acceptance-blocking defect remains in this collection after the two documented corrections below.** This review covers 17 accepted cohorts and 192 records from nine original PDFs. It does not certify unparsed sources as imported data.

## Review performed

I read the parser, its source-pinned layout configuration, the accepted manifest, and the offline tests. I compared the accepted rows with the rendered original schedules, including names, wrapped titles, remuneration/expense column meanings, reporting-year headings and printed controls. Twelve physical schedule/control pages were inspected, plus a higher-resolution crop of the Valemount council names:

| Municipality | Actual calendar year | Physical PDF pages inspected | Accepted rows |
| --- | --- | --- | ---: |
| Golden | 2024 | 52 | 34 |
| Burns Lake | 2022 | 5 | 14 |
| Cache Creek | 2025 | 5, 6 | 11 |
| Hudson's Hope | 2022 | 7 | 23 |
| Montrose | 2023 | 33 | 5 |
| Nakusp | 2024 | 3 | 12 |
| Valemount | 2024 | 4 | 11 |
| Mackenzie | 2025 | 30, 31 | 42 |
| Peachland | 2025 | 3, 4 | 40 |

All nine cached original PDF fingerprints agree with the pinned review configuration. The six final offline tests pass: `python3 scripts/test_municipal_small.py`. Those tests reproduce every accepted normalized row from each retained reader's positioned word extraction and verify output hashes and monetary controls. Agreement between two PDF readers does not, by itself, establish correct table-row association or correct OCR text; visual comparison was also necessary and identified the issues below.

## Defects found and resolved

1. **Mackenzie wrapped job title, 2025, physical page 31.** Nearest-pay-anchor grouping assigned `Deputy Emergency Program &` to the preceding Stedeford row. The corrected source-pinned outputs are `Stedeford, Ron — LH Equipment Operator` and `Taylor, Micaiah — Deputy Emergency Program & Firesmart Coordinator`. The parser now requires the reviewed original before-values for both corrections and fails if either target disappears or changes. A dedicated regression test checks both final titles. Remuneration and expenses were already mapped correctly and were not altered.
2. **Valemount published name casing, 2024, physical page 4.** A high-resolution rendering confirms `MacLean, Donnie`; the OCR text had `Maclean, Donnie`. The source-specific correction is recorded and the regenerated accepted row has the published capital L. No identity was inferred from external information.

I reopened the regenerated data and confirmed both corrections after the final six-test run.

## Monetary, period and hold decisions checked

- **Mackenzie:** imported remuneration is the published base pay plus other compensation. The displayed Total includes expenses, so it is correctly excluded as a remuneration input. Blank expenses remain missing.
- **Valemount:** the employee column is explicitly `Expenses & Taxable Benefits`. Its component values are retained in evidence; the normalized expense field remains missing for all six employees and the combined column is not added to remuneration. Individual council titles are absent in the schedule and remain missing.
- **Montrose:** employee expenses visibly sum to $6,503.65; the employee total less the under-threshold aggregate implies $6,539.65. The unexplained $36 difference is real. Holding those three employee rows while accepting the separately reconciled council cohort is supported by the original. Four explicit council `nil` amounts correctly become zero.
- **Year assignment:** Golden 2024, Hudson's Hope 2022, Montrose 2023, Nakusp 2024 and Valemount 2024 are supported by the displayed schedule headings despite misleading upload paths, index labels or cache filenames. No year was assigned from a URL alone.
- **Residuals:** the reviewed small whole-dollar residuals remain recorded as differences between displayed row sums and printed controls. Individual values are unchanged; rounding is not asserted as a proven explanation. The larger Montrose cent-precision discrepancy remains held.
- **Missing values and source boundaries:** absent titles and expense dashes/blanks remain missing, explicit nil remains zero, and supplier/aggregate rows do not enter the selected named cohorts. Source hashes, bounded page regions, counts, controls and the retained evidence provide reproducible acceptance gates.

Primary URLs, original hashes, component rows, exact controls and explicit corrections are recorded in [sources.json](sources.json), [reviewed-layouts.json](reviewed-layouts.json), and the cohort evidence files. The reviewed output fingerprints below identify the final accepted version.

| Reviewed file | SHA-256 |
| --- | --- |
| `sources.json` | `2f56e6c800e34b9b19799fb23423163a1763eb72c272d48ba686b0926e875a1a` |
| `reviewed-layouts.json` | `a42e28a6e35d57162566100a99b3ad5fa414c38b6e4b1c816c3db142c6d5ed0b` |
