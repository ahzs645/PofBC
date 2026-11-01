# Metro Vancouver employee history, reviewed October 31, 2026

Four official calendar-year employee schedules add **6,495 accepted observations**. The [official index](https://metrovancouver.org/about-us/budgets-and-financial-plans) links all four originals. These belong to the regional district and do not change the denominator of 161 current municipal jurisdictions. The existing app sector label, `Municipalities`, is retained for this pass.

| Calendar year | Employee observations | Physical PDF pages | Salary-payment subtotal residual | Benefits/other subtotal residual | Expense subtotal residual |
| --- | ---: | --- | ---: | ---: | ---: |
| 2022 | 1,391 | 55–84 | +$10 | +$6 | +$18 |
| 2023 | 1,634 | 64–104 | +$33 | −$3 | −$3 |
| 2024 | 1,694 | 71–113 | +$13 | +$1 | −$17 |
| 2025 | 1,776 | 73–117 | +$21 | $0 | −$13 |

These are partial accepted cohorts in 2022, 2024 and 2025: respectively 3, 2 and 4 original named rows have an undisclosed benefits/other component and remain held. The full originals contain 6,504 rows; all nine held names, known salary payments and pages remain in `sources.json` and supporting component evidence. `completeEmployeeSchedule` is false for those three cohorts.

Residuals are full-original known-cell sums minus the printed named-employee subtotals, including held rows. They are not comparisons of accepted-subset sums with full-source controls. Published dashes lack a zero legend: 9 benefits/other cells and 376 expense cells remain missing, and their semantics are unresolved. Individual whole-dollar published cells are unchanged. Their disagreement with the printed subtotals remains unresolved; rounding is not asserted as an explanation. Every source has a concise `publicWarning` with these exact residuals. In 2022, the printed salary subtotal plus the below-threshold aggregate is also $1 below the printed all-employee salary total. None of those aggregate rows becomes an individual record.

Remuneration is the sum of `Salary Payments` (`Base Salary Payments` in 2022–2023) and `Taxable Benefits and Other`. Schedule 3 explicitly combines those components in its employee remuneration reconciliation. Supporting evidence retains both source columns separately. The rendered 2025 footnote describes benefits and one-time payments including overtime, banked vacation and retroactive payments. Thus these amounts include the source's published benefits/other component and are not annual base salary rates. Expenses are separate. Job titles are absent from the employee schedule and remain missing.

The complete employee tables have exact row-for-row agreement between PyMuPDF's positioned words and Poppler's layout text: names, each of the three monetary components including missing dashes, PDF page and sequence. Original SHA-256 hashes, internal years, continuous page ranges, named row counts, threshold scope and source controls are pinned in the parser and manifest. Rendered first/last/control pages were additionally inspected to confirm scope, footer definitions and aggregate boundaries; this is not a claim of complete visual inspection of all 6,504 rows.

The old compiled groups retain their unverified fiscal-looking labels. No replacement or deletion is inferred from a calendar-year source alone. Schedule 1 contains directors and standing committee members, including non-elected appointees. It is retained as a separate processing candidate and has not been mislabeled as an elected-official employee cohort.

Reproduce from the pinned originals with:

```sh
python3 scripts/parse_sector_government_police.py --cache /tmp/pofbc-sector-government-police --fetch
python3 scripts/parse_sector_government_police.py --check-data
python3 -m unittest scripts/test_sector_government_police.py
```

The first command verifies original hashes and repeats both complete native-text extractions. It needs PyMuPDF and Poppler. The second verifies retained normalized files and component/control evidence without fetching originals. `sources.json` is ready for central build registration and independent review; this collection itself does not modify shared registries or generated app files.
