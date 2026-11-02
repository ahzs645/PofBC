# Langara original SOFI follow-through

Reviewed 2 November 2026. All three official SOFIs were acquired from Langara's public [annual reports index](https://langara.ca/administration/financial-services/annual-reports). Fiscal reporting periods are 1 April through 31 March, verified from the original employee schedule headings. All three complete employee schedules are accepted; the 2023/24 scan was completed using two OCR configurations and full source-cell visual review.

| Fiscal period | Physical employee pages | Accepted rows | Salary / gross pay CAD | Numeric expenses CAD | Missing / zero expenses | Row sums minus printed named controls CAD |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2022/23 | 31–41 | 710 | 69,887,446 | 2,132,016 | 13 / 0 | −8 / +11 |
| 2023/24 | 32–42 | 891 | 94,671,610 | 2,754,209 | 19 / 0 | −6 / +16 |
| 2024/25 | 29–42 | 950 | 101,403,151 | 3,209,876 | 16 / 0 | −11 / +16 |

The accepted total is **2,551 employee observations**. [sources.json](sources.json) supplies six-field deterministic gzip rows; [dispositions.json](dispositions.json) explicitly covers all three supplied source IDs. Source PDFs, byte counts, fingerprints and original fiscal dates are recorded in the manifest and evidence. All compiled observations and their labels are retained.

The source employee schedule is labelled “Total of Employees Earning > $75,000”, and the threshold is recorded literally. Some named salary/gross-pay cells are below that amount; all published named rows remain included, without inventing a threshold calculation. The column label changes from “Salary” in2022/23 to “Gross pay” in2024/25. These are published remuneration measures, not inferred annual base salaries. Positions and repeated names are preserved; repeated names with different roles/pay are separate occurrences. Expense dashes remain missing values, never zeros. Board remuneration, supplier payments, the below-threshold aggregate, severance and financial reconciliation rows remain excluded.

Every accepted native-text field agrees between separate PyMuPDF word-coordinate and Poppler layout-text parsers. For the 2023/24 scan, two Tesseract configurations independently agree on the complete 891-row census and all 1,782 monetary cells; every name, position and monetary cell was also reviewed in source pixels. Evidence retains every normalized row, source coordinates, both raw OCR readings and explicit text corrections. All three sources' displayed row sums differ from printed named controls by the small amounts above; these source residuals are public warnings. No row is changed to force balance.

Original full-page PNGs are in `images/`; `visual/` includes page contact sheets, full employee-cell crops and enlarged control/name crops, with page/image hashes and explicit review scope in JSON receipts. Native-year visual review confirms source periods, employee/board separation, alphabetic continuation, endpoints and printed controls. The scanned 2023/24 cohort additionally received complete row and cell source-pixel review.

The 2023/24 employee pages yield no employee text to either original PDF reader. They are accepted after independent 3×/PSM6 and 4×/PSM4 OCR, review of all 891 rows in 21 full-width employee-table crops, and printed-control reconciliation. Twenty-one text-field corrections are documented, including the shared OCR error `Zanzerl|, Heather`, resolved as the visibly printed `Zanzerl, Heather` in an enlarged crop. All monetary readings agree. The earlier `ocr-unaccepted` file remains historical first-pass evidence and is superseded by accepted `evidence/langara-2023-24.json.gzip`. See [the scan reconstruction](SCAN-2023-24.md) for scope, controls and seven self-contained scan tests. The official 48-page PDF has SHA-256 `74693accc765b5feb0a7e0985c9d8beb39d84bdac24d5bb92c3f78a4536e78c8`.

The saved [official index receipt](official-index-receipt.json) resolves the relative links for all three originals and fingerprints the index HTML. [duplicate-check.json](duplicate-check.json) records the search of registered official manifests; no already-imported official RRU/Langara cohort was found. No outreach, requests, forms, fees or external writes were used.

The parser, reproduction commands, ten passing regression tests and cross-source preservation details are documented in the [Royal Roads reconstruction](../follow-through-rru/README.md). The build consumes committed normalized data without requiring source downloads or OCR.
