# BC Transit 2020/21 employee disclosure

This collection fills the missing 2020/21 BC Transit employee year with **385
named employees** from the official Statement of Financial Information. The
compiled baseline contains no BC Transit rows for this year.

- [Official report](https://www.bctransit.com/wp-content/uploads/9/159/2021-07-30-FY2021-Statement-of-Financial-Information-Final-with-FS-Image.pdf)
- [Official financial reports index](https://www.bctransit.com/about/corporate-reports/financial/)
- Source SHA-256: `f9d752695330689e2f2e20d37f13a16be9473c0ccf5c6c77d576765cf4279409`
- Reporting period: April 1, 2020–March 31, 2021; employee schedule starts on PDF page 6.
- Employee pages: 6–13; board payments on page 5 and all aggregate/supplier rows are excluded.

The source PDF is image-only. Its 300 dpi RGB OCR was compared with a 400 dpi
grayscale OCR pass, and all eight employee pages were visually reviewed.
Explicit reviewed corrections are stored with the original OCR text under
`review/`. The primary pass needed two repairs: the missing thousands comma in
Hamilton, Daryl's `$94,846`, and the capital `I` in Rowden, Ian. The second pass
had additional recognition errors; each accepted correction refers to the
rendered source page. No monetary value was inferred from a difference in a
total.

| Measure | Sum of named rows | Printed named subtotal | Rows minus printed |
|---|---:|---:|---:|
| Remuneration | $36,243,255 | $36,243,253 | +$2 |
| Expenses | $320,215 | $320,208 | +$7 |

All source amounts are printed in whole dollars. These variances are within the
conservative independent-rounding bound of `$0.50 × (385 rows + 1 subtotal) =
$193` per column. That is a permissible bound, not proof of the publisher's
rounding method. The individual printed amounts are preserved without balancing
adjustments. The printed named and below-threshold subtotals exactly add to the
printed all-employee totals in both columns.

Names follow the publication, including initials and capitalization. Positions
are absent in the source and remain `null`. Expense dashes mean zero. Every
normalized row includes its physical PDF page. The schedule states that 2021
remuneration uses **27 pay periods, versus 26 in 2020**, and includes gross pay,
taxable benefits and banked-time payouts; it is not a salary-rate comparison.

## Reproduce

Install PyMuPDF and Tesseract; the reviewed run used PyMuPDF 1.26.6 and Tesseract
5.3.4. From the repository root:

```sh
python scripts/extract-bc-transit-salaries.py
```

This downloads the pinned official PDF if absent, rerenders and OCRs both
passes, and checks the complete transcription before writing accepted files.
An already downloaded PDF can be supplied with `--pdf /path/to/report.pdf`.
`--reviewed-ocr` replays the hash-checked saved OCR evidence while retaining the
source PDF, year, threshold, page, row, output-hash and subtotal checks.

The importer rejects unexpected rows and changed row values even when a total
would still fall within the rounding allowance. Focused validation confirmed
that it rejects a changed fiscal year, a one-dollar pay error, a missing employee
row and an added row. Any changed source PDF or unreviewed OCR variation must be
reviewed before its accepted hashes or corrections are updated.
