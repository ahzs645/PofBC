# Independent cross-review: Metro Vancouver and InBC

Reviewer: health-history agent, 31 October 2026 America/Vancouver. Review was read-only for both collections; only this report was written. Root separately reviews the health agent's Fraser sources.

## InBC: ready for integration

The three official source PDFs match their pinned hashes. `python scripts/import_sector_crowns.py --cache-dir /tmp/sector-crowns --verify` reproduced every normalized file, evidence file and manifest byte-for-byte. All six `test_sector_crowns.py` tests passed.

All 41 employee rows were independently inspected against rendered physical source pages 28 (FY2022/23), 30 (FY2023/24) and 29 (FY2024/25). Cover and approval text establish the correct fiscal periods; later upload directory dates do not change the year. The source title, employee section and separate board/below-threshold sections are consistent with the imported cohort. No employee positions are supplied, and surname/initial disclosures remain intact. The 2022/23 `Deering, D` versus later `Deering, A.` spellings are present in the respective originals and were correctly retained.

The FY2024/25 `Chiew, B.` expense cell is visibly blank and correctly remains `null`. All other numeric employee amounts match the rendered originals. The first source reconciles exactly. FY2023/24's +$1 remuneration residual and FY2024/25's +$1 expense residual are source discrepancies, explicitly retained in public warnings. No balancing adjustment or asserted rounding cause was found.

No blocking issue found in InBC.

## Metro Vancouver: revised partial cohorts are ready

The four PDFs match their pinned SHA-256 hashes. The offline `--check-data` verification passes. Separately calling `extract()` on each original reproduces all 6,504 accepted observations using the two native-text readers, without writing to the collection. Names, three component columns, physical pages and row order agree.

Rendered original pages inspected:

- 2022: physical pages 55 (first employee page, definitions), 84 (named controls), 85 (Schedule 3 reconciliation).
- 2023: physical page 104 (named controls and definitions).
- 2024: physical page 113 (named controls and definitions).
- 2025: physical pages 73 (first employee page, definitions), 117 (named controls), 118 (Schedule 3 reconciliation).

Calendar periods are correctly taken from internal December 31 headings. The imported source is Schedule 2, employees. Schedule 1 board/standing-committee rows and below-threshold aggregates are excluded. Schedule 3 explicitly combines salary payments with taxable benefits/other as remuneration, while expenses remain separate. Positions are absent. Metro remains identified as a regional district and excluded from the current-municipality denominator. Retained compiled fiscal-looking labels are not assumed equivalent to these calendar sources.

The named source controls and retained row-minus-control residuals agree with the originals:

| Calendar year | Employee rows | Salary residual | Taxable benefits/other residual | Expense residual |
| --- | ---: | ---: | ---: | ---: |
| 2022 | 1,394 | +$10 | +$6 | +$18 |
| 2023 | 1,634 | +$33 | −$3 | −$3 |
| 2024 | 1,696 | +$13 | +$1 | −$17 |
| 2025 | 1,780 | +$21 | $0 | −$13 |

The public warnings correctly describe unresolved residuals and unchanged published amounts. Financial totals do not eliminate the separate cell-semantics issue below.

**Initial issue, subsequently corrected:** `amount('-')` originally returned numeric zero for every source dash. This converted 376 printed expense dashes to explicit zeros. Nine taxable-benefit/other dashes were likewise converted to zero. No numeric zero token is printed in these source columns.

| Year | Printed expense dashes converted to zero | Printed benefits/other dashes converted to zero |
| --- | ---: | ---: |
| 2022 | 118 | 3 |
| 2023 | 89 | 0 |
| 2024 | 79 | 2 |
| 2025 | 90 | 4 |

Examples visually confirmed: `Archer, Gordon` has a dash expense in 2022 physical page 55; `Zimmer, Glen` has a dash expense in 2025 physical page 117. The first-page footnotes define compensation and expense categories, but do not establish a dash-equals-zero rule. Those footnotes are raster content and are not present in ordinary native text, making rendered review necessary.

Preserve expense dashes as `null` unless issuer evidence establishes zero. Preserve the raw dash tokens for component evidence and explicitly determine the salary-plus-other treatment when the other component is a dash; do not silently represent a missing source component as a published numeric zero. If the source's accounting convention supports a nil component, document that basis and distinguish the displayed raw token from the calculation convention. Re-run the original extraction and hash checks after the author/root resolves the mapping.

The issue was reported directly to root and the author. No files in either reviewed collection or its parser were edited by this reviewer.

### Revised extraction independently checked

The author changed all source dashes to `null`, preserved all 6,504 original rows in component evidence, and held the nine rows whose composite remuneration has an undisclosed benefits/other component. Those names, known salaries, expenses and physical pages remain in the manifest and full-source evidence. Remaining accepted remuneration uses two numeric components only; no missing component is added as zero.

| Year | Accepted employee rows | Held for missing pay component | Missing accepted expense cells | Complete source employee cohort |
| --- | ---: | ---: | ---: | --- |
| 2022 | 1,391 | 3 | 117 | No |
| 2023 | 1,634 | 0 | 89 | Yes |
| 2024 | 1,694 | 2 | 79 | No |
| 2025 | 1,776 | 4 | 89 | No |
| Total | **6,495** | **9** | **374** | |

Fresh read-only extraction from every hash-pinned original agrees exactly with the revised accepted inputs. Data-file hashes, row counts, accepted remuneration/known-expense sums and held-row counts match the revised manifests. Every printed expense dash remains missing; no accepted explicit zero expense is invented. `completeEmployeeSchedule` is false for 2022, 2024 and 2025 and true for 2023.

The public warning now identifies each partial cohort and held count. Full-original known-cell sums and their missing-cell counts are explicitly distinguished from accepted-subset totals, preserving the unresolved issuer residuals without treating missing cells as known zero. The offline `--check-data` check and all three `test_sector_government_police.py` regressions pass after the correction.

The initial blocking issue is resolved. The revised **6,495-row partial/full source collection is ready for integration**, with the nine missing-component rows retained for clarification and the published warnings visible in the app.
