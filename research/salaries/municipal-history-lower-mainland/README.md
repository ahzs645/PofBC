# Lower Mainland municipal history: Port Moody and Richmond

This collection adds **2,501 original disclosure observations**: 2,468 employees and 33 council observations, from eight official SOFI reports and twelve separately scoped cohorts. Port Moody employee years are 2019–2025 and newly added council years are 2020–2023; Richmond adds calendar 2024 employees. Already accepted council cohorts are not repeated. No compiled records or employer aliases are changed here.

| Calendar year | Source named employees | Accepted employees | Held benefit-dash rows | Newly accepted council |
|---|---:|---:|---:|---:|
| 2019 | 145 | 144 | 1 | Allowance definition held |
| 2020 | 151 | 150 | 1 | 7 |
| 2021 | 163 | 163 | 0 | 7 |
| 2022 | 164 | 163 | 1 | 12 |
| 2023 | 164 | 163 | 1 | 7 |
| 2024 | 242 | 238 | 4 | Already accepted elsewhere |
| 2025 | 220 | 216 | 4 | Already accepted elsewhere |

Richmond's 2024 source names 1,233 employees; 1,231 have numeric Base Salary and Benefits and Other components. Duncan, Scott (physical p54) and Young, Jim (p74) have a Base Salary dash and numeric Benefits and Other of $98,718/$94,619. They have no published numeric individual remuneration total and remain held. Both source and validation mark the employee schedule incomplete. Known benefits are retained in evidence, not published as composite pay. The source supplies no job titles, so every Richmond position stays null.

The source employee column **Remuneration** includes salary, acting pay and overtime; 2024/2025 explicitly include retroactive rate increases. The separate Tax Benefits & Payouts / Taxable Benefits column includes group life, allowances and one-time banked vacation/gratuity payments. Numeric components are summed for normalized remuneration. Council Base Salary plus numeric Taxable Benefits is normalized separately. Ordinary expenses are never added to remuneration. These are cash-payment disclosures, not annual salary rates or complete employee rosters.

Twelve Port Moody named employees have an explicit benefit dash. Their full names, titles, known Remuneration cells, expense cells and physical pages are retained in evidence and `validation.heldRows`; they are held from composite-pay publication. With Richmond's two missing-base rows, **fourteen named employees remain held**. Dash/blank expenses remain null, numeric zero remains zero, eight printed negative Port Moody 2024 expenses and one 2019 negative expense remain negative. Each partial employee source has `completeEmployeeSchedule: false` at both source and validation levels. The only complete employee cohort in this collection is Port Moody 2021. The 2022 council schedule separately discloses Meghan Lahti as Mayor and Councilor; both role rows remain intact. Port Moody 2019 council has a separate Tax Free Allowance whose classification is held for review; it is not imported alongside employees. That employee year's benefit definition explicitly includes MSP.

## Qualified source controls

All known original component cells are compared with the printed complete named-cohort controls. Source component controls are distinct from accepted-subset remuneration/expense sums. Small published component residuals are retained with explicit source warnings and an unknown cause, rather than changing any value to force reconciliation.

**Port Moody 2025 has a material unresolved source contradiction.** All 220 original Remuneration cells sum to $25,810,252, which is **$2,999,990 below** printed named remuneration $28,810,242. Printed named remuneration plus under-threshold $10,508,868 exceeds printed grand remuneration $36,319,110 by **$3,000,000**. The known row sum is $10 above printed grand less under-threshold. Known benefits are $12 above their named control and known expenses are $1 below. The source does not prove which control is incorrect or why. No inferred corrected subtotal or per-person allocation is created.

Qualified publication of its 216 numeric-component rows follows [independent full-page review](../municipal-history-pass/reviews/port-moody-2025.md) and a third uncropped pypdf inventory. All seven salary pages, all 220 names/titles and all three monetary cells were accounted for; no omitted page, employee cohort or compensation column explains the conflict. Signed approval is on physical page 3 and the cash-basis note on page 6. The prominent `publicWarning` retains the material discrepancy and four held names/pages. The 216 accepted rows sum to $25,930,099 composite remuneration; this differs in scope from the 220-row source controls.

Richmond's known original named cells sum to Base Salary **$124,813,470**, Benefits and Other **$23,773,412**, and Expenses **$577,933**, with source component residuals **+$30, −$28 and +$40** respectively. Their full known remuneration components sum to $148,586,882, **$3 above** printed combined named remuneration $148,586,879. Separately, printed component subtotals $124,813,440 + $23,773,440 exceed that printed combined total by **$1**. These are unresolved source differences, with no asserted cause or adjusted cell. The 1,231 accepted rows sum to $148,393,545 composite remuneration. A signed/adopted-report claim is supported by retained official June 23, 2025 Council minutes, resolution R25/12-12. Its source-specific Benefits and Other definition includes taxable benefits and lump-sum payouts, including leave balances, union gratuities and union overtime; expenses remain separate.

## Richmond scan and independent OCR

Physical pages 47–75 contain the complete original employee schedule: 44 rows each on pages 47–73, 40 on page 74 and five on page 75. The retained original has an existing OCR layer with visible errors; merely using two PDF text libraries would repeat that OCR. A separate Tesseract 5 reading was run from the original 300-dpi ink, independently by actual name/monetary columns. Every field is compared with both positioned PDF readers after **48 exact rendered-cell adjudications** (38 name and ten monetary disagreements), frozen separately for each reader in the layout config. Names and initials are never passed through the monetary character restriction. Source-reported names are not enriched from compiled records. Whitespace around existing commas is normalized. All raw TSVs, word coordinates and full component rows remain in hashed evidence; an additional uncropped full-page OCR inventory and the exact rendered-cell decision ledger are retained in the follow-up directory.

Independent full-image review passes cover **all 1,233 names and all three source monetary fields**: [pages 47–53, 308 rows](../municipal-history-pass/reviews/richmond-2024-pages-47-53.md), [pages 54–61, 352 rows](../municipal-history-pass/reviews/richmond-2024-pages-54-61.md), and [pages 62–75, 573 rows](../municipal-history-pass/reviews/richmond-2024-pages-62-75.md). The retained manual transcriptions corroborate every original field, both held base-pay rows and all 1,231 accepted six-field normalized observations. No further cell corrections were needed. Original/data/evidence hashes are unchanged by adding final review pointers. Qualified publication retains the unresolved residuals explicitly and both partial-schedule flags false.

## Reproduction

Original SHA-256, actual calendar headings, physical pages, frozen row bounds, source column definitions, controls and reviewed residuals are pinned in `reviewed-layouts.json`. SHA-256 also pins each normalized file and retained word/component evidence in `sources.json`. Source URLs and index URLs are recorded per source. Port Moody 2019/2020 originals were freshly downloaded from discovered modern official eDocs URLs; Port Moody 2021–2025 and Richmond 2024 originals were rehashed from the preceding pass, without claiming a new HTTP retrieval. See [retrieval receipts and remaining queue](../municipal-history-pass/lower-mainland/README.md).

```sh
python3 scripts/parse_history_lower_mainland.py --fetch
python3 scripts/parse_history_lower_mainland.py --check-data
python3 -m unittest discover -s scripts -p 'test_history_lower_mainland.py' -v
```

The parser uses the same original independently through PyMuPDF positioned words and Poppler bbox-layout words, requiring exact agreement of every name, full position and monetary field; Richmond additionally requires the independent ink OCR described above. Native content order was used only during Port Moody layout review to establish complete geometric row bounds; it is not used to copy reader output into the other reader. Names, initials, apostrophes and ampersands are preserved. No global alphabetic-token filter is used. First/last tables, wrapped-title edges, period headings, source definitions, held dashes, printed controls and all negative cells were checked against rendered pages. Full Port Moody 2025 page/name/monetary review is additionally recorded independently. Twelve regression checks cover original fingerprints, retained-reader reproduction, material aggregate equations, full-versus-partial scopes, both kinds of missing pay components, literal initials/wrapped titles, pinned OCR adjudications, negative expenses and distinct council office observations. Fresh original/ink reproduction requires PyMuPDF, Poppler, Tesseract 5 and Pillow; offline evidence reproduction does not invoke OCR or make network requests.
