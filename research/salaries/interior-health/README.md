# Interior Health: eleven original employee schedules

Reviewed **30 October 2026** against the reports linked from [Interior Health's financial-reporting index](https://www.interiorhealth.ca/about-ih/accountability/financial-reporting).
The accepted normalized schedules contain **65,364 disclosure rows for every fiscal year from 2014/15 through 2024/25**. The dates are April 1–March 31; these are not calendar-year reports.

## Coverage and controls

| Fiscal period | PDF pages | Named employee rows | Displayed remuneration | Remuneration minus printed named subtotal | Expenses minus printed named subtotal |
|---|---:|---:|---:|---:|---:|
| 2014/15 | 65 | 3,408 | $311,631,916 | $40 | $50 |
| 2015/16 | 78 | 3,538 | $324,074,781 | $25 | $56 |
| 2016/17 | 93 | 4,233 | $398,638,133 | $58 | $79 |
| 2017/18 | 90 | 4,084 | $380,402,777 | -$1 | $79 |
| 2018/19 | 98 | 4,447 | $416,996,644 | $31 | $126 |
| 2019/20 | 112 | 5,125 | $485,458,710 | $9 | $120 |
| 2020/21 | 138 | 6,320 | $616,614,075 | $15 | $177 |
| 2021/22 | 145 | 6,611 | $655,762,847 | $17 | $118 |
| 2022/23 | 158 | 7,222 | $722,913,933 | $62 | $202 |
| 2023/24 | 208 | 9,540 | $1,044,940,648 | $55 | $241 |
| 2024/25 | 236 | 10,836 | $1,209,331,334 | $37 | -$267 |

The printed tables report whole dollars. The listed residuals are compatible with the conservative bound `(named rows + 1) / 2` for independently rounded employee cells and a subtotal. That is a compatibility check, not proof of the publisher's rounding method or cause of the differences. Individual amounts remain unchanged and exact reconciliation is not claimed. The manifest also retains the separate under-threshold and all-employee controls, including their occasional $1 discrepancies.

## Verification and source semantics

The [importer](../../../scripts/import-interior-health-salaries.py) reads fresh Poppler layout text, then reconstructs every row independently from PyMuPDF word coordinates. All **65,364 names, remuneration values, expense values and physical page references** agree between the two PDF engines. It checks every one of the **1,521 pages**, sequential printed footers, source period headings, table boundaries, source hashes, parsed row counts and monetary controls before writing any accepted output. Source and deterministic normalized-file hashes are in [sources.json](sources.json).

The issuer logo, period heading, first employee row, last employee row and aggregate controls were visually reviewed for all eleven PDFs. All 67 negative-expense rows and the one displayed threshold-boundary row were also visually checked. Names and payment records retain their published multiplicity; 72 repeated-name groups across the source years are not merged into person identities. No exact duplicate name/pay/expense row was detected within a year.

- The source calls the named cohort **greater than $75,000**. One 2020/21 row, `BAXTER,LOUISE M` on physical page 8, prints exactly `$75,000`. That source value is preserved as a narrowly checked exception. The undisclosed underlying cents are unknown; the report's threshold is not relabelled inclusive.
- Early negative expenses appear as a separated minus sign, while later reports use parentheses with an asterisk. Both remain negative. The 2019/20 and later reports say negative expenses can reflect the timing of third-party reimbursements in a cash-basis report.
- **28,518 dash expense cells remain null**, distinct from explicit zero. None of these reports prints an explicit zero expense in a named row.
- The source does not publish job titles. The imports do not carry unverified compiler titles into the official schedules. Remuneration should not be described as annual base salary or twelve months of work.
- Final-page named subtotals, under-threshold aggregates, grand totals and footnotes are excluded from employee rows.

## What the compiled editions contained

[compiled-comparison.json](compiled-comparison.json) compares each of the three immutable compiled slices against all eleven official periods with multiset comparisons, preserving duplicates and exact amounts. Names are compared after case, punctuation and whitespace normalization while retaining the surname/given-name boundary. No fuzzy matching or person-identity inference is applied.

| Compiled label | Compiled rows | Same fiscal-period official rows | Initial normalized name/pay matches | Finding |
|---|---:|---:|---:|---|
| 2017/18 | 3,683 | 4,084 | 3,594 | All 3,683 match after replacing the compiler's digit-zero-for-hyphen name error for comparison only; 401 official rows were absent |
| 2020/21 | 6,275 | 6,320 | 6,270 | Five role-labelled executive amounts differ from the employee schedule; the official employee cohort replaces the compiled cohort |
| 2023/24 | 8,896 | 9,540 | 8,894 | Two compiled names differ from source name/pay pairs; accepted names come directly from the original PDF |

These three slices strongly match the fiscal periods already used. There is no support here for applying Vancouver's calendar-year correction to Interior Health. Replacing the 18,854 compiled rows with all eleven official schedules adds **46,510 net disclosure rows** and eight previously empty fiscal periods.

The 2017/18 comparison-only substitution does not modify the preserved baseline or add a general name-repair rule. The accepted names retain the original PDF's hyphens and punctuation. The cause of the five executive amount differences and two later name differences is not established by the comparison and is not invented.

## Reproduce

Requires Python 3, PyMuPDF and Poppler `pdftotext`. Cached originals use filenames `interior-health-2015.pdf` through `interior-health-2025.pdf`.

```sh
python3 scripts/import-interior-health-salaries.py --cache /path/to/source-pdfs --offline --verified-on 2026-10-30
python3 -m unittest scripts/test_import_interior_health.py
```

Omit `--offline` to download missing originals from the exact official URLs. Changed source bytes fail before acceptance and require a fresh review. The build needs neither network nor PDF dependencies because it consumes the committed normalized gzip files. The eight focused regression tests exercise missing-versus-zero expenses, negative conventions, threshold exceptions, aggregate exclusion, wrong periods, page omissions and corrupt totals. The complete original-source import also passed with both PDF engines.
