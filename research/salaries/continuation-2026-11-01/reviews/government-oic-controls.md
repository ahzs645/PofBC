# Independent Government OIC source, row and control review

**Recommendation: accept-qualified all seven 1999/00–2005/06 cohorts /8,602 faithfully displayed rows**, retaining exact source-control and literal-negative warnings. The salary-only2003/04–2005/06 source metadata has been corrected from `totalExpenses:0` to unavailable/null; every normalized row already correctly had expense null. The final metadata correction and unchanged payload/evidence hashes were independently confirmed. No author payload was changed by this review.

Reviewer: `/root/education_continuation`, November1,2026. Exact original, payload and author-evidence hashes, per-source page coverage and independently derived sums are recorded in `government-oic-controls.json`. Originals are `/tmp/continuation-government-police/pa-YYYY-YY.pdf` and all fingerprints were checked against the manifest.

A **separately implemented Poppler bbox reader** reproduced every name, case, initial, punctuation, salary, travel/null cell, physical page, order and repeated observation for all8,602 rows on57 salary-table pages. The author parser was neither imported nor called. This provides a third PDF engine alongside the author's reported PyMuPDF and PDFMiner agreement; another invocation of PDFMiner is not claimed as independent. The peer parser identifies salary columns by numeric right-edge clusters, creates name-fragment row groups, joins wraps and rejects unassigned monetary cells. It retains malformed names rather than repairing them. Poppler's plain bbox word output resolves the layout-text spacing problem for the two DELAUNAY variants without a value/name substitution.

Independent whole-volume header inventories exactly match the source page ranges:9–16,10–17,12–19,10–17,11–17,13–21 and15–23 respectively. The published heading identifies Order-in-Council, Other Appointees and Employees not Appointed under the Public Service Act. This is a complete named table of that particular scope, with no individual threshold, and remains distinct from ministers, deputy ministers and the Other Employees workforce. `completeEmployeeSchedule:false` correctly avoids asserting complete core-workforce coverage. No individual position/title column is published.

All seven summary/control pages were rendered and inspected in full: physical5,5,6,6,6,7,7. All seven first-table scope/fiscal headers were inspected as rendered crops. The complete final salary pages for the three material cases were also rendered and inspected:1999/00p16,2001/02p19,2003/04p17. All four negative rows and all seven multi-line name groups were inspected in high-resolution original crops. This is **not a whole-volume visual census**; all57 salary pages instead have complete independent cell/row comparisons. Exact full-page versus crop coverage is recorded separately in the JSON.

| Fiscal period | Rows | Salary sum | Printed salary control | Salary residual | Known travel sum | Printed travel control | Travel residual |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1999/00 |1,341|74,063,235|74,063,000|+235|5,033,718|5,047,000|−13,282|
| 2000/01 |1,318|74,550,784|74,551,000|−216|4,845,746|4,846,000|−254|
| 2001/02 |1,351|76,691,830|76,692,000|−170|3,941,901|3,935,000|+6,901|
| 2002/03 |1,339|81,951,415|81,951,000|+415|4,200,290|4,200,000|+290|
| 2003/04 |1,075|75,398,888|75,505,000|−106,112|unavailable|unavailable|n/a|
| 2004/05 |1,083|78,637,177|78,637,000|+177|unavailable|unavailable|n/a|
| 2005/06 |1,095|80,373,799|80,374,000|−201|unavailable|unavailable|n/a|

The summary units are explicitly **thousands of dollars, unaudited**. Small residuals remain visible at that summary precision; no cause is inferred. The material1999/00 travel−13,282,2001/02 travel+6,901 and2003/04 salary−106,112 differences remain unexplained. Complete table coverage, all monetary-cell assignments, section boundaries and printed summary labels were checked; no extraction omission or alternate OIC summary definition resolves them. Blank same-row travel cells remain unknown. Known-cell sums must not imply blank values are zero.

The literal negative salary cells are2000/01 Carroll,P−984 and Davis,B D−2,410 onp11;2001/02 CULLEN,A F−1,334 with travel3,833 onp13 and SONDHEIM,D−5,193 onp18. All signs, names and payment columns match the originals. No correction or explanation is invented.

Seven wrapped names are source-backed:2001/02 BASARAB-OSTRANDER,S(p12), `DELAUNAY-BELLEVILLE , K A`(p13) and LLEWELLYN-THOMAS,M(p16);2002/03 BASARAB-OSTRANDER,S(p10), `DELAUNAY-BELLEVILLE K A`(p11, **no comma**), HODKINSON,C MARILYN(p12), and LLEWELLYN-THOMAS,M(p13). The original comma on the next line in the first DELAUNAY case and its absence in the second were checked visually. No cross-year name repair or deduplication was applied.

For2003/04 onward the salary table has no travel column; the later travel schedules combine OIC and non-OIC scopes. Those lists must not be joined to salary rows by name. The2002/03–2005/06 salary footnotes explicitly allow base salary, retroactive pay, benefits and prior/current-year vacation payments. Separate benefits/accrual aggregates must not be added to individual salaries. General cash/accrual reporting notes do not establish the cause of an internal OIC control difference.

Reproduce and replay independently:

```sh
python scripts/continue_education_review_oic.py
python scripts/continue_education_review_oic.py --offline
```

The committed `government-oic-poppler-evidence.json.gzip` permits standard-library offline replay without originals, network, PDFMiner, PyMuPDF or OCR. It pins original fingerprints and exact Poppler salary-page word evidence. Both full-original and offline comparisons passed for all8,602 rows.
