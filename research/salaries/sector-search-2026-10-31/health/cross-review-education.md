# Independent SFU employee-source review

Health-history reviewer, 31 October 2026 America/Vancouver. This review was read-only for the education collection, parser, replacement evidence and registry. Issues were sent to root and the education author for correction.

The six accepted fiscal sources contain **13,527 employee observations**. `python scripts/parse_sector_education.py --verify` independently reproduced all nine accepted/held originals against pinned source hashes, full two-reader row comparisons, control readings, normalized hashes and compressed input hashes. All seven `test_sector_education.py` regressions pass.

**Final decision: the six accepted cohorts and their documented same-period authority replacements are clear for integration. The three material-discrepancy years remain held.** Review corrections below changed documentation and warnings, not official employee cells.

## Accepted source periods, scope and controls

Original covers and employee headers identify Simon Fraser University and their March 31 year ends. The cohort is the complete named **employee remuneration and expenses** schedule, with an inclusive **$75,000** earnings threshold. Board expenses, suppliers, under-threshold aggregates and grand totals are excluded from individual records. No employee positions are published; all accepted position cells remain missing.

| Fiscal year | Accepted rows | Physical employee pages | Printed named remuneration | Printed named expenses | Row-minus-control residuals: pay / expenses | Missing expenses |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| 2017/18 | 1,617 | 43–58 | $192,341,425 | $10,024,915 | $0 / $0 | 145 |
| 2018/19 | 1,723 | 44–60 | $204,342,067 | $9,535,921 | $0 / $0 | 219 |
| 2020/21 | 1,980 | 44–64 | $241,488,773 | $3,812,133 | +$10 / +$25 | 457 |
| 2021/22 | 2,366 | 44–67 | $293,064,511 | $4,536,805 | +$11 / +$18 | 521 |
| 2024/25 | 2,874 | 47–77 | $387,891,582 | $12,099,065 | $0 / $0 | 498 |
| 2025/26 | 2,967 | 52–78 | $402,493,561 | $11,513,025 | +$30 / −$9 | 585 |

All six final control pages were inspected as freshly rendered originals. FY2020/21 physical page 64 contains the final three named employees before the controls; they are correctly retained. The three source residual warnings state exact differences and unresolved cause. No row was changed to balance a printed subtotal, and no rounding explanation was assumed.

Blanks and dashes remain `null`. No numeric zero expense is invented; these accepted schedules contain no explicit zero expenses. The sole negative expense, **Ghai, Sandhya, $124,849 remuneration and −$1,727 expenses, FY2025/26 physical page 60**, was verified against a rendered crop. The refund-netting footnotes for FY2020/21 page 64 and FY2021/22 page 67 were visually confirmed.

Representative wrapped names were inspected on FY2020/21 page 44, FY2024/25 page 47 and FY2025/26 page 52. Names that continue below or before their amount baseline remain one cell; their continuation is not attached to the preceding employee. Examples include `Aragon Sanchez, Fernando Martin` and `Ackkiniraj Chandrasekar, Angayarkanni`. Repeated names and distinct payment rows remain separate observations.

## Compiled replacement review

The immutable compiled-baseline SHA-256 is `410bcae27c9755e387c473ab44d62081a50b46e7330f4d6d5c0b74979d392760`. Both complete replacement evidence files reproduce exactly the corresponding baseline employee partitions in original order and multiplicity; their hashes and official-source/normalized hashes match the comparison manifest.

| Fiscal label | Compiled rows replaced | Official employee rows | Surname/first-initial/payment matches after diagnostic zero/missing coalescing |
| --- | ---: | ---: | ---: |
| 2017/18 | 1,617 | 1,617 | 1,615 |
| 2020/21 | 2,072 | 1,980 | 1,977 |

The diagnostic zero/missing coalescing is limited to comparison. Accepted expense missingness is preserved. Same-labelled complete employee partitions are replaced by new official authority; the comparison is not proof that every compiled enriched name, position or individual identity agrees with the original source.

FY2017/18 compiled and official remuneration sums both equal $192,341,425. The compiled partition has employment job titles, no below-threshold payments and no separate board remuneration cohort. Official Board of Governors schedules explicitly state that no remuneration is paid for board activity and that employee board-member remuneration belongs in the employee schedule. Removing this employee partition therefore does not remove a distinct paid-board cohort.

For FY2020/21, 91 extra identical compiled rows and malformed/wrapped name cells explain part of the discrepancy; the complete official original also has three final employees absent from compilation: Zuccolo, Valerie; Zupan, Kenneth; and Zwagerman, Sean Michael, all on physical page 64. The original 2,072-row compiled partition and its unreconciled details remain in the immutable baseline and replacement receipt. No fuzzy identity reconstruction is used to create accepted source names.

### Three Schmidt source-name conflicts

Rendered FY2017/18 physical page 55 and the preserved compiled partition establish **three** conflicting name/payment associations:

| Official disclosed name | Compiled name at the same payment pair | Remuneration | Expenses |
| --- | --- | ---: | ---: |
| Schmidt, Michele | Schmidt, Gina | $119,776 | $4,725 |
| Schmidt, G | Schmidt, Margaret | $81,003 | $6,570 |
| Schmidt, Margaret | Schmidt, Michele | $132,061 | $811 |

Independent review caught the third conflict: both given names begin with M, so a first-initial comparison counted it as a match. That metric remains correctly labelled but cannot establish agreement of full disclosed names. The author updated the source public warning, conflict count, comparison/receipt evidence and regression to include all three. The original PDF names remain unchanged. No person identity or compiled job-title assignment is asserted.

The author also corrected stale accepted-source notes that had said no compiled replacement was made; they now describe same-period authority replacement and preservation of original evidence.

## Held years remain excluded

The accepted manifest lists exactly the six sources above. The three held employee sources have separate files under `sector-search-2026-10-31/education/held`, status `held`, and are absent from the accepted collection registry:

| Held fiscal year | Candidate rows | Pay residual | Expense residual |
| --- | ---: | ---: | ---: |
| 2019/20 | 1,848 | +$47 | −$6,018 |
| 2022/23 | 2,398 | −$25 | +$5,108 |
| 2023/24 | 2,833 | +$876,155 | +$10,365 |

Their successful reproducibility checks do not accept them into the app. Existing compiled coverage for held periods remains subject to the separate retained-data policy.

## Expense-definition claim corrected

Review found the gross-expense/non-external-recovery footnote in the **held FY2023/24 original, physical page 71**. Accepted notes had incorrectly extended that definition through FY2024/25. The author corrected the claim to the supported FY2023/24 only; accepted FY2024/25 and FY2025/26 now explicitly retain their own published cells without an inferred net/gross or external-recovery definition. Generic references to negative “recoveries” were also corrected to negative “amounts.” Employee values remain unchanged. No review issue remains open.
