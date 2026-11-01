# Recovered Fraser Health employee histories

Two official originals add **11,494 employee observations**: **5,569 in FY2013/14** and **5,925 in FY2014/15**. The preserved compiled baseline has no Fraser records for either fiscal label, so these sources add records without deleting compiled observations.

| Fiscal period | Original source | SHA-256 | Physical pages | Rows | Remuneration | Numeric expenses |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 2013-04-01–2014-03-31 | [2014EmployeeRemuneration.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2014/2014EmployeeRemuneration.pdf) | `dc651f21a4d8f7e143865c3e6e723a32189c271b90d251511f40e93c94e87f28` | 118 | 5,569 | $514,447,540 | $4,561,219 |
| 2014-04-01–2015-03-31 | [2015EmployeeRemuneration.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2015/2015EmployeeRemuneration.pdf) | `dd902ea484f17717eff18ce0faa9876831d2a513cf34f1e3ac9642e87e4971c0` | 149 | 5,925 | $544,066,029 | $4,513,454 |

Both URLs were found in public search results and downloaded directly from Fraser Health's media storage on 2026-10-31 America/Vancouver. Its [current financial reporting index](https://www.fraserhealth.ca/about-us/accountability/financial-reporting) links employee years FY2015/16–2024/25, so these two earlier originals are historical discoveries rather than currently linked index entries. The guessed analogous 2013 filename redirected to an HTML page-not-found response; that is not proof that FY2012/13 is unavailable.

The source threshold is payments **equal to or greater than $75,000**. These schedules report cash-basis employee remuneration and expenses. Employer benefit costs, contracted labour and physician fees are excluded. Under-threshold aggregates and the FY2013/14 contract-category summary are retained as controls, not individual records. Job titles are absent. Dash expenses remain `null`; no zero is inferred. Repeated names are retained as separate published observations.

## Verification and discrepancies

`sector_health_fraser.py` independently reconstructs every name, remuneration, expense, row order and physical page using **Poppler layout text and PyMuPDF word coordinates**. All **11,494 rows agree exactly**. Every employee-page employer heading, internal fiscal date, table heading and sequential printed footer is checked. No employee lines are skipped. The FY2013/14 cover declares 5,569 named employees, agreeing with the full employee extraction. Exact duplicate name/pay/expense rows are absent.

The first FY2013/14 physical page is a contract-category summary, so the employee schedule starts on physical page 2 while its printed footer says 1. Accepted source links always use the physical page. FY2014/15 prints the column heading `RENUMERATION`; the extractor recognizes that source typo without changing the values.

The printed source amounts disagree with their named subtotals:

| Fiscal year | Displayed pay minus named subtotal | Displayed expenses minus named subtotal | Named plus below-threshold pay minus grand total | Named plus below-threshold expenses minus grand total |
| --- | ---: | ---: | ---: | ---: |
| 2013/14 | +$40 | +$34 | $0 | −$1 |
| 2014/15 | +$104 | +$23 | $0 | $0 |

The cause is unresolved. **No published cell was adjusted**, no rounding explanation is assumed, and exact monetary reconciliation is not claimed. Each manifest entry has a `publicWarning` containing its exact pay and expense residuals so the app can display the limitation.

Rendered originals were inspected for the period/table headers, FY2013/14 count cover, both final summary pages, and the sole negative expense: **LUCKEN,BRENDA A, $91,313 remuneration, −$5 expenses, physical page 64 in FY2013/14**. All other rows receive the two-engine check; this does not claim manual visual inspection of every row.

## Reproduce

Requires Python 3, PyMuPDF and Poppler. From the repository root:

```sh
python research/salaries/sector-health/sector_health_fraser.py
python research/salaries/sector-health/test_sector_health_fraser.py
```

After downloading, use `--offline` to reproduce without network access, or `--output /tmp/sector-health-review` to avoid modifying this collection. Cached originals are `/tmp/sector-health/fraser-2014.pdf` and `fraser-2015.pdf`; PDFs are not checked into the repository. Reviewed source hashes, counts and totals are locked. All outputs are prepared before writing either source. Gzip output uses `mtime=0`.

The six regression tests check missing/zero/negative distinctions, both full originals against the independent engine, rejection of a changed period, rejection of malformed employee text, correct physical page offsets, and preservation of the negative expense and unresolved residuals. Integration tests require the original cached PDFs and explicitly skip when unavailable; they do not download files during a normal offline test run.

`scripts/test_sector_health.py` includes these same six tests exactly once in the standard `python3 -m unittest discover -s scripts -p 'test_*.py'` suite.
