# Independent Museum and BC Housing review

**Pass: all 690 assigned named employee rows match an independently implemented PDFMiner/pdfplumber fixed-cell reader exactly**, including spelling, punctuation, monetary values, null expenses, order, multiplicity and physical pages. No Crown worker parsing function is imported. Original and normalized data hashes are pinned in the accompanying JSON. No source manifest or normalized payload was modified.

| Source | Rows | Pay sum | Named pay residual | Disclosed expense sum | Same-scope expense residual |
|---|---:|---:|---:|---:|---:|
| Museum FY2024/25 | 76 | $7,483,585 | −$3 | $86,571 | +$2 |
| Museum FY2023/24 | 55 | $5,336,378 | +$2 | $151,292 | +$1 |
| Museum FY2022/23 | 33 | $3,339,826.80 | −$0.20 | $77,222 | Unavailable |
| Museum FY2021/22 | 36 | $3,583,820 | −$1 | $9,691 | Unavailable |
| BC Housing FY2023/24 | 490 | $49,236,111 | +$3 | $1,045,195 | +$4 |

All seven Museum employee/control pages were reviewed at full size, including all 200 named rows, internal fiscal headings and printed controls: FY2024/25 physical 42–44; FY2023/24 physical 41–42; FY2022/23 physical 42; FY2021/22 physical 40. The FY2021/22 raster cover was also rendered and confirms March 31, 2022. The native row readers alone are not asserted to corroborate raster-only headings.

Museum named remuneration comparators are explicitly derived from `Total - All Employees` less numeric `under $75,000` remuneration. FY2024/25 expenses similarly use $264,438 minus $177,869 = $86,569; FY2023/24 use $197,376 minus $46,085 = $151,291. Those derivations preserve employee scope and do not include financial-statement benefits/accrual adjustments. FY2022/23 under-threshold expenses are a dash; FY2021/22 they are blank. Neither is treated as zero, so the all-employee expense totals are not asserted as named-expense controls.

Museum FY2024/25 physical page 42 explicitly prints `(311)` for **Hardie,Colin** expenses. The normalized −311 and visible source warning are correct. All small residuals remain literal source disagreements with no invented cause. FY2022/23 salary cents remain cents despite whole-dollar aggregate remuneration controls.

For BC Housing, all ten employee-page layouts (physical 10–19) were viewed in a rendered contact sheet. Detailed full-size checks covered physical 10, 11 and 19, including `Celligoi R G` without a comma ($79,207 pay / $498 expenses), the final `de Vos, E` row and the printed `TOTAL>$75,000` controls. This does not claim individual visual transcription of every one of the 490 Housing rows; complete machine comparison covers them all. Physical page 9 establishes the March 31, 2024 schedule date and separate board scope, and page 20 contains employee aggregates/reconciliation excluded from named observations.

The Housing named controls are $49,236,108 remuneration and $1,045,191 expenses. The +$3/+4 row differences match the manifest warnings. No board pay, under-threshold aggregate, supplier payment or financial reconciliation is imported as a named employee.

Reproduce with `python scripts/continue_health_review_crown_small.py` using original cache paths from `crowns-museum-housing.json`. No acceptance blocker found beyond the already visible source-control qualifications.
