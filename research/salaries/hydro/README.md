# BC Hydro group employee remuneration: verified primary-source imports

Verified on **22 October 2026** from the official BC Hydro Financial Information Act returns. These files restore the correct **2020/21** employee disclosures and extend BC Hydro, Powerex and Powertech back to **2012/13**. They also fill the intervening years.

## Sources and scope

[BC Hydro's financial reports index](https://www.bchydro.com/about/accountability_reports/financial_reports.html) lists returns ending in March 2015 through March 2025. Two earlier official PDFs remain available:

- [Year ended 31 March 2013](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/openness-accountability/financial-information-act-return-march-31-2013.pdf).
- [Year ended 31 March 2014](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/openness-accountability/financial-information-act-return-20140331.pdf).

Two further official reports were located but **not imported**, because their employee tables are image-only scans:

- [Year ended 31 March 2011](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/openness-accountability/financial-information-act-return-2011.pdf). Its cover and the rendered employee schedule on PDF page 47 identify 2011, although its contents page mistakenly says 2010. The cover says it was updated in January 2013.
- [Year ended 31 March 2012](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/openness-accountability/financial-information-act-return-2012.pdf). The rendered employee schedule on PDF page 47 confirms 2012. The general notes explain that this return covers **27 pay periods instead of the typical 26**, which matters for comparisons with adjacent years.

These are recorded under `unparsedSources` with hashes and `requires-ocr` status. OCR alone would not be sufficient: the resulting rows still need schedule-date, completeness and aggregate verification before importing them.

The precise URL, SHA-256 hash, fiscal period, threshold, page numbers, row count and reconciliation are recorded for every report in `sources.json`. The document cover **and every selected employee schedule header** must identify the expected fiscal year. The parser checks that all numbered pages of each selected employee section are present once, in order.

The verified inputs contain **63,046 disclosed employee-year rows across 37 employer-years**. Every return for fiscal 2012/13 through 2023/24 contributes all three employers; fiscal 2024/25 contributes Powertech only. The other two 2024/25 schedules are withheld for the reasons below.

These are named employee disclosures above **$75,000**, not full workforces or total payroll. The reports call the amount gross remuneration, which can include base salary, overtime, incentive payments, payouts and other cash payments. Expenses are a separate field. The records do not supply positions or full given names. Board members, suppliers, aggregate totals, severance counts and other subsidiary schedules are excluded.

## The 2020/21 correction

The [official return ending 31 March 2021](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/financial-reports/annual-reports/BCHydro-FIA-F21.pdf) contains:

| Employer | Named rows | Employee schedule PDF pages | Sum of printed remuneration |
|---|---:|---|---:|
| BC Hydro | 5,374 | 76-153 | $679,909,379 |
| Powerex | 157 | 188-191 | $30,143,426 |
| Powertech Labs | 144 | 197-200 | $16,468,375 |

For the specific example **BL Mo**, the Powerex schedule on PDF page **189** gives **$122,528 remuneration and $704 expenses**. The official 2017/18 return, page **179**, gives **$115,833 remuneration and $693 expenses**. The original duplicate compiled row is therefore not the correct 2020/21 observation. The initial-only name is retained; it is not expanded into a guessed identity.

## Verification and rounding

For each employer, the sum of all extracted named rows is compared with:

`printed total - printed consolidated amount for employees at or below $75,000`

Both remuneration and expenses must pass. The source prints whole dollars, and its separately rounded row and aggregate amounts need not sum to exact equality. For `n` named rows, the maximum possible independent rounding difference is `(n + 2) × $0.50`. All actual differences and this bound remain in the manifest. Passing the bound is a reconciliation test; it does not prove that every difference was caused by rounding. No extracted amount is changed to force the totals to agree.

The parser also rejects unexpected monetary leftovers, below-threshold row matches, absent summaries, missing employee sections, wrong fiscal years and missing or repeated section pages. It handles tightly abutting surname/amount text, multiple columns, negative expenses, mixed-case initials and the zero-expense hyphens used in 2024/25. Regression checks exercise those observed failure modes.

Repeated surname/initial combinations are kept as distinct printed rows. They are not safe person identifiers, and equal initials do not justify deleting records or merging their histories.

## Deferred 2024/25 observations

The [official return ending 31 March 2025](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/financial-reports/annual-reports/f2025-financial-information-act-return.pdf) has two aggregate mismatches beyond the rounding bounds:

| Employer and field | Sum of printed named rows | Printed total less under-threshold total | Difference | Maximum rounding difference |
|---|---:|---:|---:|---:|
| BC Hydro expenses | $43,929,456 | $43,933,162 | -$3,706 | $3,455.50 |
| Powerex remuneration | $45,040,659 | $45,136,574 | -$95,915 | $106.50 |

BC Hydro has 6,909 printed named rows and its remuneration sum **does** reconcile within rounding (+$39). Powerex has 211 printed named rows and its expenses **do** reconcile (-$4). Powertech's 179 rows reconcile for both fields and are included.

Independent extraction of the numeric columns using PDF word coordinates reproduced both mismatches. The final Powerex summary page was also rendered and inspected. This establishes a discrepancy between the printed rows and printed aggregates; it does **not** establish the cause or identify a missing employee. No row or amount should be invented to close it.

For now the BC Hydro and Powerex 2024/25 rows are retained in `review/2024-25.json.gzip`, listed under `deferredEmployers`, and excluded from the verified import. A corrected issuer report or a documented explanation is needed before treating these employer-years as fully reconciled.

## Reproduction and file format

From the repository root:

```sh
python scripts/extract-hydro-salaries.py --self-test
python scripts/extract-hydro-salaries.py --cache-dir /tmp/pofbc-hydro-research
```

The Python script uses only the standard library and Poppler's `pdftotext`. It downloads the public source PDFs if they are absent from the cache; `--refresh` fetches them again. PDFs are not checked into the repository. Gzip outputs have a fixed modification time and can be rebuilt deterministically from unchanged source PDFs.

Each imported `.json.gzip` is a JSON array of rows:

```json
["sub-powerex", "Mo, BL", null, 122528, 704, 189]
```

The columns are `employerSlug`, `name`, `position`, `remuneration`, `expenses`, `pdfPage`. Monetary values are dollars exactly as printed, not thousands of dollars. A null position means the employee schedule did not publish it. Page numbers are one-based physical PDF pages, allowing direct verification even where the document's printed pagination differs.

Only files referenced by each source's `file` property are verified import inputs. Files under `review/` are deliberately excluded. Other employee schedules, including Columbia Hydro Constructors in some reports, are recorded as not imported; they require their own scope and employer mapping.
