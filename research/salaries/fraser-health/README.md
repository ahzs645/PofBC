# Fraser Health employee remuneration

This collection contains **99,712 named employee records** from ten original Fraser Health schedules, covering fiscal years **2015/16 through 2024/25**. It replaces the three compiled snapshots previously used for this employer and adds seven fiscal years. The accepted rows carry the original PDF URL and physical page number through the salary build.

## Sources and coverage

All URLs were taken from the employer's [financial-reporting index](https://www.fraserhealth.ca/about-us/accountability/financial-reporting), checked on **2026-10-23**. The dates below come from each schedule's internal fiscal heading, which is checked on every physical page. The filename spelling and capitalization vary; the importer uses the exact linked URLs.

| Fiscal year | Original employee schedule | PDF pages | Accepted rows |
| --- | --- | ---: | ---: |
| 2015/16 | [2016EmployeeRenumeration.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2016/2016EmployeeRenumeration.pdf) | 149 | 6,219 |
| 2016/17 | [20171030_employee_remuneration.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2017/20171030_employee_remuneration.pdf) | 158 | 6,606 |
| 2017/18 | [20181031_EE_Remuneration_Schedule.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2018/20181031_EE_Remuneration_Schedule.pdf) | 170 | 6,938 |
| 2018/19 | [2019_11_Summary_of_Remuneration_and_Expenses.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2019/2019_11_Summary_of_Remuneration_and_Expenses.pdf) | 154 | 7,527 |
| 2019/20 | [Employee-remuneration.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2020/Employee-remuneration.pdf) | 166 | 8,080 |
| 2020/21 | [Employee-remuneration.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2021/Employee-remuneration.pdf) | 206 | 10,072 |
| 2021/22 | [Employee_remuneration.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2022/Employee_remuneration.pdf) | 221 | 10,782 |
| 2022/23 | [Employee-remuneration.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2023/Employee-remuneration.pdf) | 231 | 11,289 |
| 2023/24 | [Employee-remuneration.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2024/Employee-remuneration.pdf) | 305 | 14,921 |
| 2024/25 | [Employee_Remuneration.pdf](https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/2025/Employee_Remuneration.pdf) | 353 | 17,278 |
| **Total** | | **2,113** | **99,712** |

The index's 2026 section had executive, board, and consolidated financial reports when checked, but no employee-remuneration schedule was linked there. FY2025/26 employee coverage remains a gap; this check does not establish that no report exists elsewhere. Executive and board reports are separate cohorts and are not substituted for employee schedules.

## What the figures represent

These schedules disclose employee payments **equal to or greater than $75,000**. The threshold is inclusive, recorded as `thresholdComparison: ">="`. The normalized rows exclude under-threshold aggregate payments. Job titles are not supplied, so the position field is `null`.

The source notes describe cash-basis remuneration and expenses that cannot be directly reconciled with accrual-basis financial statements. They exclude employer benefit costs, contracted labour, and physician fees. A disclosed annual payment is not a salary rate. Neither the row counts nor the remuneration sums describe the employer's complete workforce or payroll.

Names retain the printed initials, punctuation, and spelling. Matching names are not proof of a single person. Repeated names remain separate rows; no record is combined with another. There were no exact duplicate name/pay/expense rows in the accepted schedules. A future unexpected exact duplicate causes the importer to stop for review, rather than silently remove it.

Expense cells preserve their source meaning: a dash becomes `null`; an explicit zero becomes `0`; negative amounts remain negative. The printed negative recoveries and sole explicit zero were visually checked:

| Fiscal year | Physical PDF page | Disclosed name | Remuneration | Expenses |
| --- | ---: | --- | ---: | ---: |
| 2017/18 | 22 | CANOSA,SANDEE | $81,287 | −$459 |
| 2018/19 | 64 | JEONG,JANELLE | $82,030 | −$47 |
| 2019/20 | 27 | CHOHAN,GURMANGAL | $97,525 | −$85 |
| 2019/20 | 99 | MCNEIL,ROSEMARY | $100,621 | −$99 |
| 2021/22 | 24 | BRAR,RAMAN | $126,803 | $0 |

The FY2017/18 summary spans pages 169–170, including a final aggregate-only page. Those pages and the FY2024/25 summary on page 353 were also visually checked. The registry distinguishes these targeted visual checks from the coordinate validation applied to every row.

## Extraction and validation

[`scripts/import-fraser-health-salaries.py`](../../../scripts/import-fraser-health-salaries.py) uses Python's standard library and Poppler's `pdftotext`; OCR is unnecessary because all ten PDFs contain native text. It:

1. Downloads an exact source URL when it is absent from the cache, and requires the reviewed SHA-256 fingerprint before extraction.
2. Parses the layout text, requiring a matching employer and fiscal heading, one employee table header, and a sequential printed footer on every page. Unexpected employee lines cause failure.
3. Separately reconstructs every employee row from positioned PDF words. The two algorithms must agree on the complete name, remuneration, expense amount, physical page, row order, and row count. Both use Poppler's underlying text decoding, so this is a second reconstruction method rather than a second PDF engine.
4. Requires reviewed page counts, row counts, displayed amount sums, and printed named-employee subtotals. It records missing, zero, and negative expenses, repeated names, and per-page counts.
5. Extracts the named, below-threshold, and all-employee summary totals. It records exact differences and checks their compatibility with whole-dollar rounding without altering any amount.
6. Prepares all ten accepted inputs in memory and writes outputs only after every source passes. Gzip output is deterministic (`mtime=0`).

`sources.json` records the original PDF hashes, normalized/gzip data hashes, threshold, reporting dates, source scope, validation counts, and discrepancies. The row format is:

```text
[employerSlug, name, position, remuneration, expenses, pdfPage]
```

The accepted employer slug is `fraser-health`. The page is the physical PDF page, starting at 1, suitable for a `#page=N` source link.

### Subtotal differences are retained

The employee amounts are published as whole dollars. Their sums differ slightly from the printed named-employee subtotals in every year:

| Fiscal year | Displayed remuneration sum | Sum minus printed remuneration subtotal | Displayed expense sum | Sum minus printed expense subtotal |
| --- | ---: | ---: | ---: | ---: |
| 2015/16 | $575,856,593 | +$78 | $4,542,045 | +$9 |
| 2016/17 | $622,509,766 | +$149 | $4,606,903 | +$163 |
| 2017/18 | $656,117,414 | +$105 | $5,070,506 | +$49 |
| 2018/19 | $721,267,111 | +$82 | $4,973,596 | +$50 |
| 2019/20 | $793,671,551 | +$110 | $5,089,367 | +$58 |
| 2020/21 | $1,022,135,521 | +$20 | $5,243,498 | −$6 |
| 2021/22 | $1,114,704,375 | +$31 | $5,726,328 | +$60 |
| 2022/23 | $1,174,137,118 | +$239 | $6,165,257 | +$14 |
| 2023/24 | $1,715,733,845 | +$44 | $21,092,362 | +$425 |
| 2024/25 | $2,009,600,438 | +$312 | $19,619,483 | −$722 |

All residuals fit the maximum independent whole-dollar rounding bound of `(named row count + 1) / 2`. This is a compatibility check, not proof that rounding explains every discrepancy. No row is changed to force reconciliation, and `summaryTotalReconciled` remains false. The displayed-expense sum includes only numeric cells; missing cells are not imputed.

The printed named and below-threshold subtotals also differ from their printed grand total by a dollar in some schedules. The exact residuals are recorded, and the importer accepts at most the $1.50 mathematical bound for three independently rounded aggregates. FY2017/18's one-dollar remuneration difference was visually confirmed on pages 169–170.

### Comparison with the preserved compiled baseline

The original compiled input remains in `research/salaries/compiled-baseline.json.gzip`. The importer compares the overlapping three fiscal labels using names stripped of case, spacing, and punctuation plus exact remuneration, preserving multiplicities. This is a name/pay comparison, not identity resolution or fuzzy matching.

| Fiscal label | Compiled rows | Official rows | Matched name/pay pairs | Compiled pairs absent from official | Official pairs absent from compiled |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2017/18 | 6,952 | 6,938 | 6,749 | 203 | 189 |
| 2020/21 | 10,072 | 10,072 | 10,066 | 6 | 6 |
| 2023/24 | 14,908 | 14,921 | 14,896 | 12 | 25 |

These differences are retained in each source's validation metadata. They can reflect spelling or payment-basis differences and should not all be described as missing employees. The ten official schedules replace 31,932 compiled rows with 99,712 source rows: **67,780 net additional records**.

## Reproduce

From the repository root, with Python 3 and Poppler installed:

```sh
python scripts/import-fraser-health-salaries.py --verified-on 2026-10-23
python scripts/test_import_fraser_health.py
```

To rerun the complete verification without network access after the PDFs have been cached:

```sh
python scripts/import-fraser-health-salaries.py --cache /tmp/pofbc-fraser --offline --verified-on 2026-10-23
```

Use `--output /path/to/collection` for a separate review output. Source PDFs are cached as `<fiscal-end-year>.pdf`; they are not checked into this repository. The ordinary salary build consumes the accepted gzip inputs and registry without downloading or parsing PDFs.

The six parser regression tests cover inclusive thresholds, missing/zero/negative expenses, malformed monetary text, incorrect fiscal headings and page footers, repeated-row preservation, printed-total residuals, missing-row rejection, and coordinate mismatches. Changed source bytes, new layouts, years outside the reviewed set, or new exact duplicates require a fresh review and updated locks before they can be published.
