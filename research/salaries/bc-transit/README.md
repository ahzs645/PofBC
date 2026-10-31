# BC Transit employee disclosures

This collection contains **2,140 named employee rows across five fiscal years**
from official BC Transit Statements of Financial Information (SOFI). The
2026-10-23 recovery added **1,755 rows** for 2015/16, 2016/17, 2019/20 and
2025/26 to the existing 385-row 2020/21 import.

The [official financial reports index](https://www.bctransit.com/about/corporate-reports/financial/)
links 15 SOFI publications labelled 2012 through 2026. The label is the fiscal
year's **ending** year: the 2026 employee schedule covers April 1, 2025 through
March 31, 2026. A report being linked or downloaded does not mean its employee
schedule has been accepted into this collection.

## Accepted sources

All amounts below are Canadian dollars. Page numbers are physical PDF pages,
including the approval sheets.

| Fiscal year | Named rows | Employee pages | Sum of remuneration | Sum of expenses | Source and extraction |
|---|---:|---|---:|---:|---|
| 2015/16 | 177 | 7–11 | $16,304,943 | $507,681 | [Official PDF](https://www.bctransit.com/wp-content/uploads/110/41/BC-Transit-2015-16-Approved-Statement-of-Financial-Information.pdf); two OCR passes and complete employee-page review |
| 2016/17 | 219 | 6–10 | $19,961,793 | $637,388 | [Official PDF](https://www.bctransit.com/wp-content/uploads/101/576/1_FIR0.pdf); native layout text independently checked against positioned PDF words |
| 2019/20 | 359 | 6–12 | $33,190,139 | $820,227 | [Official PDF](https://www.bctransit.com/wp-content/uploads/419/1002/Statement-of-FInancial-Information-2020-PDF-a7eaf646-0e84-4977-8c34-4f96f13e96fb.pdf); two OCR passes and complete employee-page review |
| 2020/21 | 385 | 6–13 | $36,243,255 | $320,215 | [Official PDF](https://www.bctransit.com/wp-content/uploads/9/159/2021-07-30-FY2021-Statement-of-Financial-Information-Final-with-FS-Image.pdf); two OCR passes and complete employee-page review |
| 2025/26 | 1,000 | 7–26 | $102,154,713 | $1,134,613 | [Official PDF](https://www.bctransit.com/wp-content/uploads/2026/09/BC-Transit-Statement-of-Financial-Information-2026-Final-with-Financial-Statements.pdf); two OCR passes and complete employee-page review |

The 2025/26 PDF has signed management and board approval sheets, both dated
July 24, 2026. Its employee schedule explicitly states the year ended March 31,
2026. Its internal PDF title contains an old draft label; the accepted file is
the final report linked by BC Transit's official index, with signed approvals.

`sources.json` contains each original URL, source PDF hash, normalized-data
hash, compressed-file hash, fiscal dates, disclosure threshold, page list,
counts, totals and verification results. Every normalized row retains its
source PDF page. Board payments, supplier payments and aggregate-only rows are
excluded. The employee disclosure threshold is remuneration **over $75,000**;
these rows do not represent the full workforce.

## Validation and reconciliation

For scanned employee schedules, a 300 dpi RGB OCR pass is compared with a
separate 400 dpi grayscale OCR pass. All employee pages have been visually
reviewed, including cases where both OCR passes agreed on an incorrect value.
Every correction is explicit and tied to a source page and original OCR line
in `review/annual-reviews.json`, or the existing
`review/2020-21-ocr-review.json`. The original OCR text is retained in the
compressed files under `review/`.

For example, both 2019/20 passes misread several digits, including Minty,
Casey's remuneration as $16,245 rather than the printed $76,245 and Loughran,
Elizabeth's expenses as $2,158 rather than $2,758. These were corrected from
the page images. Agreement between OCR passes, or a small total difference,
is not sufficient evidence of a correct transcription.

The 2016/17 schedule contains usable native text. Every employee row extracted
with Poppler's layout text is independently compared with names and amounts
read from positioned PDF words using PyMuPDF. The complete set of employee
pages must agree with the reviewed page list.

| Fiscal year | Printed named remuneration subtotal | Rows minus printed | Printed named expenses subtotal | Rows minus printed |
|---|---:|---:|---:|---:|
| 2015/16 | $16,304,943 | $0 | $507,681 | $0 |
| 2016/17 | $19,961,797 | −$4 | $637,388 | $0 |
| 2019/20 | $33,190,139 | $0 | $820,227 | $0 |
| 2020/21 | $36,243,253 | +$2 | $320,208 | +$7 |
| 2025/26 | $102,154,713 | $0 | $1,134,613 | $0 |

For every year, the printed named and below-threshold subtotals exactly add to
the printed all-employee totals in both columns. All source amounts are printed
in whole dollars. The 2016/17 and 2020/21 residuals lie within the conservative
independent-rounding bound of `$0.50 × (number of rows + 1 subtotal)` per
column: $110 and $193, respectively. This bound does **not** establish the
publisher's rounding method or explain the residual. Individual printed amounts
are preserved without balancing adjustments.

Names follow the publication, including initials and capitalization. The
2025/26 source prints `Parminder Singh` without a comma; that name is retained
as printed and is an explicit reviewed exception. The importer does not invent
a surname boundary. Positions are absent in these schedules and remain
`null`. Printed expense dashes are recorded as zero.

These are remuneration disclosures, not annual salary rates. The schedules
include gross pay, taxable benefits and banked-time payouts. Their published
pay-period notes also limit comparisons:

| Fiscal year | Pay periods stated in the source | Prior year's pay periods stated in the same note |
|---|---:|---:|
| 2015/16 | 27 | 26 |
| 2016/17 | 26 | 27 |
| 2019/20 | 26 | 26 |
| 2020/21 | 27 | 26 |
| 2025/26 | No count verified in the remuneration note | No count verified in the remuneration note |

## Reproduce

Install PyMuPDF, Tesseract and Poppler's `pdftotext`. The reviewed environment
used PyMuPDF 1.26.6 and Tesseract 5.3.4. From the repository root:

```sh
# Download the pinned source if necessary and rerender/OCR a selected year.
python scripts/extract-bc-transit-salaries.py --year 2025-26

# Rebuild all five accepted years from their official PDFs and saved OCR evidence.
# The native-text source is always re-extracted from the PDF.
python scripts/extract-bc-transit-salaries.py --all-reviewed --reviewed-ocr

# Exercise evidence replay and intentional corruption cases.
python scripts/test_extract_bc_transit.py
```

The default year remains `2020-21` for compatibility. `--year` accepts either
`YYYY-YY` or `YYYY/YY`. An already downloaded report can be supplied with
`--pdf /path/to/report.pdf` for one year; `--cache-dir` changes the download and
render cache. `--all-reviewed` without `--reviewed-ocr` reruns both OCR passes
for every scanned accepted year. Reimporting one year preserves the other
years in `sources.json`.

Every run verifies the PDF hash, reporting year, threshold, page set, individual
rows, per-page boundaries/counts/sums, complete output hash and printed
subtotals before writing that year's accepted data. Saved OCR replay also
checks the evidence hash and requires every reviewed correction to be used.
A changed source PDF or unreviewed OCR variation must be reviewed before
updating its accepted hashes or corrections. A one-dollar error is rejected
even if it would fall inside the aggregate rounding allowance.

The focused suite contains ten tests covering retained OCR agreement, fiscal
scope, missing pages or rows, changed values and printed subtotals, stale
corrections, the reviewed name exception, and preservation of other years.
Both the all-year evidence replay and a fresh 2025/26 two-pass OCR extraction
passed on 2026-10-23.

## Remaining source gaps

`source-survey-2026-10-23.json` records all 15 official SOFI files, their
downloaded hashes and page counts, the accepted years, and employee-page ranges
where located. Ten linked periods remain unaccepted: **2011/12, 2012/13,
2013/14, 2014/15, 2017/18, 2018/19, 2021/22, 2022/23, 2023/24 and 2024/25**.

Several PDFs contain text in their appended audited financial statements but
scanned employee schedules. Testing only whether the PDF contains any text
would misclassify these sources. Each remaining employee schedule needs its
own complete extraction and review. The survey preserves source leads; it
does not claim that the unaccepted years were parsed or validated.
