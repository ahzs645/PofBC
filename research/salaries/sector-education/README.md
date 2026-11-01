# SFU official employee disclosure histories

Six complete fiscal employee schedules add 13,527 official source observations. This collection uses the original [SFU SOFI archive](https://www.sfu.ca/finance/publications/annual-reports.html), with original-PDF, compressed-data and normalized-data SHA-256 fingerprints pinned in `sources.json`.

| Fiscal period | Employee rows | Remuneration sum | Expenses sum | Row sum minus named controls (pay / expenses) |
| --- | ---: | ---: | ---: | ---: |
| 2017/18 | 1,617 | $192,341,425 | $10,024,915 | $0 / $0 |
| 2018/19 | 1,723 | $204,342,067 | $9,535,921 | $0 / $0 |
| 2020/21 | 1,980 | $241,488,783 | $3,812,158 | +$10 / +$25 |
| 2021/22 | 2,366 | $293,064,522 | $4,536,823 | +$11 / +$18 |
| 2024/25 | 2,874 | $387,891,582 | $12,099,065 | $0 / $0 |
| 2025/26 | 2,967 | $402,493,591 | $11,513,016 | +$30 / −$9 |

The three nonzero financial residuals are unresolved and have explicit `publicWarning` fields; their controls are **not** marked reconciled. No published amount was changed. Three larger discrepancies remain held outside this collection: 2019/20, 2022/23 and 2023/24, totaling 7,079 candidate observations. Their complete normalized rows, original fingerprints, controls and third-reader check are preserved in `../sector-search-2026-10-31/education/held/`.

All accepted and held employee cells agree between PyMuPDF and Poppler independently reading the original PDF: disclosed name, missing position, remuneration, expense, physical page, row multiplicity and every named subtotal. Every monetary/name word in the selected table columns must be assigned. Missing and unexpected cells fail extraction. The gross-expense/non-external-recovery footnote is verified only for the held 2023/24 report (physical page 71); no net/gross definition is inferred for accepted 2024/25 or 2025/26. Whole-dollar amounts, negative amounts, numeric zeroes and blank/dash missingness are preserved. Both fiscal headings and the inclusive $75,000 threshold are checked. Reported pay is annual remuneration, not an annual base salary rate.

The employee schedules occupy two parallel columns. Names may wrap before **or after** their money baseline. A name remains within its cell; literal line-ending hyphens join without an inserted space. Regression cases include Aragon Sanchez, Fernando Martin (2020/21), Ackkiniraj Chandrasekar, Angayarkanni (2025/26), Belisle-Pipon, Jean-Christophe (2025/26), Ghai, Sandhya’s −$1,727 expenses, and three distinct Zhang, Lin observations. Wrapped-name inventories accompany each normalized source. Rendered original approval, table/control and representative edge pages were reviewed; the exact page receipts are in each source’s validation object. The 2024/25 and 2025/26 published approval pages show a `[signed]` notation; earlier accepted years show signatures.

## Compiled data replacement and disclosed names

Two accepted periods overlap retained compiled labels. The integration replaces the complete **same-period employee partition by its new official authority**. It is not an exact cross-label duplicate finding. Complete removed compiled partitions and source/baseline hashes are preserved in `compiled-replacement-2017-18.json.gzip`, `compiled-replacement-2020-21.json.gzip` and `compiled-comparison.json`; the immutable original compiler baseline also remains unchanged.

* 2017/18: 1,617 compiled rows versus 1,617 official observations. Every remuneration/expense pair matches when compiled numeric-zero expenses and source blanks are diagnostically coalesced. That comparison does not turn a source blank into a zero. The compiler contains expanded names and job titles absent from the original PDF; those details are not attributed to the PDF. Three names disagree for matching payment cells: official **Schmidt, Michele** ($119,776 / $4,725) versus compiled **Schmidt, Gina**, and official **Schmidt, G** ($81,003 / $6,570) versus compiled **Schmidt, Margaret**, and official **Schmidt, Margaret** ($132,061 / $811) versus compiled **Schmidt, Michele**. Physical PDF page 55 was rendered and checked. The source has an explicit public warning and reproduces the PDF’s names. The first-initial comparison does not detect the third conflict because Margaret and Michele share M.
* 2020/21: 2,072 compiled rows versus 1,980 official observations. Of these, 1,977 surname/first-initial/payment observations match. The compilation omits the final three employee rows (Zuccolo, Zupan and Zwagerman) and has 95 extra copies/variants, including 91 identical extra rows. The exact source rows replace the complete malformed employee partition; candidate name expansion is not guessed.
* No compiled 2018/19, 2021/22, 2024/25 or 2025/26 SFU partition exists. The compiled 2023/24 partition remains while that official candidate is held.

The separate SFU board schedule states no remuneration was paid for board activity and that pay/expenses for employee members appear in the employee schedule. The removed compiled partitions contain no below-threshold or board-remuneration group: 2017/18 has employee job titles, while 2020/21 has no titles and all rows exceed the employee threshold. Separate board expenses and supplier payments are not imported as employee salaries. The rendered 2017/18 board page 42 and 2020/21 board page 43 were checked.

## Reproduce

From repository root:

```sh
python3 scripts/parse_sector_education.py --download --pdf-dir /tmp/pofbc-sector-education --verify
python3 -m unittest discover -s scripts -p 'test_sector_education.py' -v
```

The script requires PyMuPDF and Poppler `pdftotext`. It downloads only missing originals, rejects original-hash changes, checks both reader outputs and named controls, and compares them to the committed normalized bytes. It verifies held candidates without adding them to the accepted manifest. The seven regression tests passed; all nine source reproductions passed. No requests were sent to SFU or any other institution.
