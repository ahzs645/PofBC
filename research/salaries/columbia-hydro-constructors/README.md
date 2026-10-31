# Columbia Hydro Constructors: original-PDF verification completed

Reviewed 30 October 2026. The five named schedules contain **723 payment records**.
The employer maps to the existing atlas entity `sub-columbia-hydro-constructors`;
these records are not BC Hydro employee records.

| Fiscal period | Named records | Remuneration | Expenses | Pay / expense residual |
|---|---:|---:|---:|---:|
| 2012/13 | 190 | $19,718,574 | $1,089,407 | $1 / $0 |
| 2013/14 | 226 | $23,588,724 | $1,369,304 | $3 / -$2 |
| 2014/15 | 239 | $25,533,054 | $1,370,304 | -$3 / $2 |
| 2015/16 | 63 | $6,651,654 | $394,765 | $3 / -$3 |
| 2016/17 | 5 | $485,097 | $30,673 | -$1 / $1 |

Residuals compare the named-row sum with the printed total less the printed
at-or-below-$75,000 aggregate. They are preserved, fit the stated hypothetical
whole-dollar rounding bound, and have no proved cause. No individual amount was
adjusted to make a control total agree.

The original six BC Hydro Financial Information Act returns were downloaded from
the source URLs in [sources.json](sources.json). Every SHA-256 matched the earlier
staging package. All 723 named rows, including their physical pages, were compared
as multisets using two different extraction paths: Poppler's layout text and
PyMuPDF words selected by the monetary-column coordinates. All 19 employee and
summary pages were visually inspected; the five aggregate columns were checked
against their actual rendered locations. The sheet sequence and employer/year
headings are also validated on every selected page.

The **2017/18** one-sheet schedule contains no named rows. Its $208,410 remuneration
and $12,021 expenses are entirely in the at-or-below-threshold aggregate. That is
verified aggregate-only coverage, not evidence of no staff or no payroll. It is
kept in `aggregateOnlySources` and creates no named salary records.

Names are the published surname and initials, reordered into `Surname, INITIALS`
without expanding them or claiming unique identities. Source rows remain separate.
Positions are not published. The employer CPP/EI payment is a separate aggregate,
not employee remuneration, and is not imported.

A second, separate check on the same day (the comparator `scripts/check_chc_pdf.py`, page
coordinates and a review of all 19 rendered pages, recorded in
[`../chc-recovery/pdf-verification/`](../chc-recovery/pdf-verification/review.json)) produced
rows identical to these, record for record.

Reproduce the byte, extraction and arithmetic checks:

```sh
python3 scripts/verify-columbia-hydro-salaries.py --cache /path/to/pdfs --offline
```

The cache uses filenames `2012-13.pdf` through `2017-18.pdf`. Without `--offline`,
missing sources are downloaded from the exact recorded URLs. The reviewed inputs
pin PDF bytes and the earlier staging multiset. Changed bytes or discrepancies
fail before writing new normalized outputs. A rerun verifies the locked reviewed
inputs; it does not claim a new visual review.
