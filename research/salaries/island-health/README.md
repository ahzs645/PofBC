# Island Health employee remuneration: accepted years and held source conflicts

Reviewed **30 October 2026**. Original documents are linked from [Island Health's financial-reports page](https://www.islandhealth.ca/about-us/plans-reports-and-policies/financial-reports). The full extraction covers **69,751 employee rows across ten fiscal years**. **Eight years, containing 50,615 rows, are accepted.** Two years remain staged because their own published controls conflict.

## Source decisions

| Fiscal period | Employee physical PDF pages | Extracted rows | Decision | Monetary controls |
|---|---|---:|---|---|
| 2015/16 | 1–77 | 3,824 | Accepted | Standalone list publishes no named totals or independent count |
| 2016/17 | 1–97 | 4,229 | Accepted | Standalone list publishes no named totals or independent count |
| 2017/18 | 1–99 | 4,413 | Accepted | Standalone list publishes no named totals or independent count; values have cents |
| 2018/19 | 1–112 | 5,022 | Accepted | Standalone list publishes no named totals or independent count |
| 2019/20 | 1–125 | 5,835 | Accepted | Displayed minus printed named subtotals: +$37 remuneration, +$29 expenses |
| 2020/21 | 1–160 | 7,324 | Accepted | +$65 remuneration, +$34 expenses |
| 2021/22 | 1–168 | 7,685 | Accepted | +$56 remuneration, +$8 expenses |
| 2022/23 | 122–290 | 8,252 | **Held** | Narrative declares 8,264 named employees; table contains 12 fewer rows |
| 2023/24 | 127–374 | 10,884 | **Held** | Expenses sum $45,772 below the printed named subtotal |
| 2024/25 | 134–426 | 12,283 | Accepted | Declared count matches; +$74 remuneration, +$1,335 expenses |

For accepted sources with printed controls, the recorded residuals fit the conservative independent whole-dollar rounding bound `(named rows + 1) / 2`. Compatibility does not establish the reason for the discrepancies. Amounts remain unchanged and no exact reconciliation is claimed. For the four earlier standalone PDFs, unpublished totals and counts are explicitly null; acceptance rests on source provenance, all-page coverage and complete agreement between two independent PDF engines.

## Why the two years remain held

**2022/23:** The narrative on physical page 121 declares 8,264 employees above $75,000 and its occupational-group counts also sum to 8,264. The actual employee table on physical pages 122–290 contains **8,252 rows**. Fresh Poppler layout extraction and independent PyMuPDF coordinate reconstruction agree on every row. Displayed remuneration totals $828,394,349, only $54 above the printed $828,394,295; expenses total $7,029,656, $93 above the printed $7,029,563. These monetary controls support the extraction, but they do not explain the conflicting employee count. The candidate file is retained pending an issuer clarification or corrected source; twelve undisclosed rows are not invented.

**2023/24:** The source narrative and complete table agree on **10,884 rows**. Remuneration totals $1,197,885,209, $41 above the printed named subtotal. Expenses total **$14,592,431**, while physical page 374 prints **$14,638,203**. The **-$45,772** residual exceeds the $5,442.50 whole-dollar rounding compatibility bound. Both PDF engines agree on the individual expense cells and the printed total was visually checked. The source needs a corrected report or an issuer reconciliation. No employee value is changed to force the aggregate to match.

The [manifest](sources.json) assigns both years `held-for-review`, `accepted: false`, and `candidateFile` paths under `staging/`. They have no accepted `file` field. They cannot replace the site's existing compiled 2023/24 slice or create an accepted 2022/23 cohort merely because a PDF was found and parsed.

## Complete extraction review

The [importer](../../../scripts/import-island-health-salaries.py) reconstructs all **69,751 names, remuneration values, expense values and physical page numbers** independently with Poppler layout text and PyMuPDF positioned words. The two results match exactly. All **1,548 employee pages** were included. The three full SOFIs were restricted to the explicit employee sections, excluding board remuneration, suppliers, financial statements and the later severance schedules.

The first-page period/scope headings, last employee rows, available aggregate controls, three full-SOFI scope pages, all 27 negative-expense rows, four early rows with mixed precision, and three misencoded monetary cells were visually reviewed. The source fingerprints, expected row counts, exact decimal sums, negative-row controls and explicit transcription decisions are retained in [reviewed-inputs.json](reviewed-inputs.json). Source and normalized-data hashes are also recorded in the manifest.

### Precision and disclosure semantics

- The 2017/18 report publishes numeric amounts to **cents**, all preserved. The 2015/16 source mostly prints whole dollars but four rows include cent-valued cells, including unformatted `83925.79`; those are preserved too. Decimal arithmetic is used for validation.
- A source dash remains missing, not zero. Parenthesized values and separated minus signs remain negative. No source name or repeated-name record is collapsed into a person identity.
- The 2019/20, 2020/21 and 2021/22 reports contradict themselves on threshold wording: their covers say **exceeding $75,000**, while their named subtotals say **equal to or greater than $75,000**. Their manifest records `thresholdComparison: reported-conflict` and the source note. Every listed employee in those reports actually exceeds $75,000, so no row inclusion decision depends on choosing one phrase.
- The full-SOFI scope pages include salaries, wages, retroactive pay, vacation payouts, taxable benefits and retiring allowances. They explicitly exclude amounts paid under severance agreements. These are remuneration records, not annual base-salary rates.
- The standalone 2019/20–2021/22 reports describe cash-basis payments and exclude employer benefit costs, contracted labour and physician fees. Their figures are not directly reconcilable to accrual financial statements.
- None of the employee tables publishes job titles. Unverified compiler positions are not silently attached to official employee rows.

### Narrow PDF text-encoding corrections

The 2024/25 PDF renders three monetary cells normally but extracts some digits as unrelated Unicode characters. Each was visually checked against the rendered source, and only the exact source cell is transcribed:

| Physical page | Cell | Extracted token | Rendered source value |
|---|---|---|---:|
| 295 | `MACNEIL,KATHRYN E`, expenses | `1ϯ,ϭϭϳ` | $13,117 |
| 426 | Named employee expense subtotal | `17,0Ϭϱ,ϬϴϮ` | $17,005,082 |
| 426 | All-employee expense total | `27,5ϴϳ,ϵϯϬ` | $27,587,930 |

This is a correction to extracted text, not a change to the underlying published amounts. Changed source hashes or glyph tokens fail validation. No global Unicode replacement is applied to names or unrelated values.

## Comparison with the retained compiled editions

[compiled-comparison.json](compiled-comparison.json) preserves comparisons against every source period rather than assuming fiscal labels are correct.

- **2017/18:** All **4,413 compiled name/pay records** match the original 2017/18 employee table after comparison-only whole-dollar `ROUND_HALF_UP` rounding. Direct amount comparison matches only 53 because the source reports cents; `ROUND_HALF_EVEN` matches 4,396. The accepted records restore the original source precision. The rounding diagnostics never change accepted values.
- **2020/21:** The compiled slice has 7,280 rows; **7,273 name/pay pairs** match the original 2020/21 table, which has 7,324 rows. Unexplained differences are not resolved through fuzzy names or invented compensation components; the complete official employee table replaces the compiled slice.
- **2023/24:** All **10,400 compiled name/pay pairs** match rows in the original 2023/24 employee table, which contains 10,884 rows. The year stays held because of its expense-control discrepancy; the 484 extra source rows are not yet accepted for publication.

These comparisons support the existing fiscal-period correspondence. Vancouver's calendar-year correction does not apply here. Accepting the eight cleared sources replaces 11,693 compiled rows and adds **38,922 net rows**, including six previously empty fiscal periods. The 19,136 held candidate rows are separate from those totals.

## Reproduction

Requires Python 3, PyMuPDF and Poppler `pdftotext`. Cached originals are named `island-2015-16.pdf` through `island-2024-25.pdf`.

```sh
python3 scripts/import-island-health-salaries.py --cache /path/to/source-pdfs --offline --verified-on 2026-10-30
python3 -m unittest scripts/test_import_island_health.py
```

Omit `--offline` to download missing originals from exact official URLs. Every source must pass its recorded fingerprint and extraction controls; unresolved reviewed discrepancies remain held. Eight focused regression tests protect cents, missing/negative expenses, exact glyph-cell scope, employee-table boundaries and both held-source promotion guards. The offline salary build consumes only accepted normalized gzip paths and needs no PDF or network dependency.
