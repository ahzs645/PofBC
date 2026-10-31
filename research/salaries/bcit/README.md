# BCIT employee disclosure recovery

Reviewed **23 October 2026**. The accepted inputs now contain **10,624 employee-year
records in nine official financial-information returns**. Eight of these source
schedules are newly recovered; 2017/18 was already imported and now has physical
PDF page provenance and independent checks of every name and monetary cell.

| Fiscal period | Named records | Physical employee pages | Displayed remuneration | Displayed expenses | Remuneration residual | Expense residual |
|---|---:|---|---:|---:|---:|---:|
| 2014/15 | 861 | 34–53 | $84,091,597 | $2,568,961 | −$2 | +$2 |
| 2016/17 | 923 | 36–55 | $90,826,723 | $2,828,037 | −$34 | $0 |
| 2017/18 | 970 | 36–57 | $96,590,156 | $3,409,363 | +$19 | +$3 |
| 2018/19 | 1,024 | 37–59 | $103,138,199 | $3,734,020 | +$55 | +$3 |
| 2020/21 | 1,246 | 36–63 | $131,006,879 | $1,390,476 | +$8 | +$11 |
| 2021/22 | 1,272 | 38–65 | $136,025,146 | $919,314 | +$15 | +$19 |
| 2022/23 | 1,298 | 39–67 | $136,392,204 | $3,285,595 | +$41 | +$18 |
| 2023/24 | 1,435 | 40–71 | $163,782,820 | $3,861,310 | −$28 | +$8 |
| 2024/25 | 1,595 | 39–73 | $179,398,741 | $4,671,865 | +$5 | −$9 |

These are disclosed remuneration records at or above $75,000, not total employees
or base annual salary rates. Positions are not published in these schedules.
Exhibit B employee records are separated from board members in Exhibit C, suppliers
in Exhibit D, and the below-threshold and grand-total rows.

## Source evidence

The [official financial-report index](https://www.bcit.ca/financial-services/financial-reports/)
links the five returns ending in 2021–2025. The older 2015, 2017, 2018 and 2019
returns remain at official `bcit.ca/files/financialservices/pdf/` URLs. Exact links,
PDF SHA-256 hashes, reporting dates, every physical/printed page, counts and data
hashes are recorded in [sources.json](sources.json). Each report's signed Exhibit H
approval page was rendered and visually checked; observed approval dates are
recorded in the manifest. The general-purpose parser accepts only fingerprints
and schedule checks reviewed in [reviewed-inputs.json](reviewed-inputs.json).

The three older backlog URLs for 2014, 2015 and 2017 returned actual PDFs in this
review. The previous HTML response therefore no longer blocks access to those
documents. The 2014 report is an image-only scan and remains **unparsed**: its
cover confirms 31 March 2014, but the employee pages, rows and totals still require
OCR and independent verification. Its fingerprint and retrieval result are saved
under `unparsedSources`, with no salary rows accepted from it.

The current index has consolidated financial statements ending in 2026, but its
financial-information section still ends in 2025. An audited balance sheet is not
an employee disclosure, so it does not fill 2025/26. BCIT 2015/16, 2019/20 and
2025/26 employee schedules remain unlocated in this recovery; this is not a claim
that they were never published.

## Observed source defects and parser safeguards

**2020/21 truncates names in the original document.** On physical PDF page 39, for
example, the printed strings include `Chavoshi Jolfae`, `Castillo, Jorda`, and
`Chapin, Nathani`. Thirteen records lack a surname/given-name comma because the
disclosed text ends inside the surname. Many other names also end early. The
import retains those strings exactly, labels the source `published-truncated-names`,
and never fills them using a later year's names. These records cannot establish
unique identities. The 2014/15 source also has one name without a comma;
its published order is retained.

**2020/21 resets the last printed employee page to Page1.** Physical PDF pages
36–62 are printed as 6–32, but physical page 63 is printed as 1. The final page
contains the last four employee rows and both aggregates. The parser checks this
exact reviewed sequence, all 28 contiguous physical pages, and every per-page row
count. Other sequence changes fail validation. It does not infer a missing page
from this demonstrated numbering defect.

**2014/15 splits a numeric word inside an aggregate.** One PDF text method splits
`73,371,238` into `7` and `3,371,238`. The independent extractor joins adjacent
numeric glyph groups only when their physical gap is under 1.5 points and both
lie in the monetary area. Salary and expense columns stay separate. The final
aggregate was visually checked against the page image.

**Amounts preserve their printed meaning.** Expense dashes remain null; numeric
zeroes remain zero; parenthesized negative expense recoveries remain negative.
No missing job title or full given name is invented. The normalized sixth column
is the one-based physical PDF page, including for the formerly imported 2017/18
source. The monetary/name values of that existing source are unchanged.

## Reconciliation and its limits

The remuneration residual compares the sum of displayed named rows plus the
displayed below-threshold aggregate against the displayed employee total. The
expense residual compares displayed named expenses against the printed expense
total. The below-threshold expense cell is a dash, so it remains missing and is
not represented as a measured zero.

All residuals fit the maximum independent whole-dollar rounding bound,
`(named rows + 2) × $0.50`. This establishes compatibility with rounding, not the
cause of a discrepancy. The original values are preserved, and no schedule is
described as exactly reconciled when its printed amounts differ.

Every row and both aggregate cells were compared between Poppler's layout text
and an independent extraction assembled from positioned PDF words. The checks
also cover source hash, cover year, employee-section year, section boundaries,
physical page count, exact printed page sequence, each page's row count, disclosure
threshold, number of name-boundary omissions, negative expense count, and all
unparsed lines. The parser completes validation for every selected source before
writing accepted inputs.

## Reproduction

```sh
python scripts/import-bcit-salaries.py --cache /tmp/pofbc-salary-sources
python scripts/import-bcit-salaries.py --cache /tmp/pofbc-salary-sources --offline --check-only
python scripts/import-bcit-salaries.py --years 2024 2025 --cache /tmp/pofbc-salary-sources --offline
python scripts/test_import_bcit.py
```

`--years` takes the fiscal year **end**; omitted years mean all reviewed sources.
A subset refresh preserves the other accepted source entries. `--check-only`
validates without changing inputs. The normal offline salary build consumes the
checked-in gzip files; only source extraction needs `pdftotext` and `pdfplumber`.
Gzip outputs use a fixed timestamp. PDFs, extracted text and review images stay in
the download cache, not in the repository.

Nine focused regression tests cover the demonstrated numeric-fragment issue,
aggregate exclusion, clipped-name preservation, zero/null/negative expenses,
wrong fiscal headings, missing rows or pages, repeated totals, unexpected monetary
text, below-threshold rows, and out-of-bound subtotal differences.
