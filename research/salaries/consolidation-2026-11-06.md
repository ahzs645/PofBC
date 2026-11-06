# Salary and Workforce Profile consolidation

This consolidates the employer-insight and poster-flow changes from PR #47 and the corrected workforce/OpenCompensation work from PR #48. The baseline is main commit `7399fde18d2b278f5e99e2e201b915adadc7a8e2`. Nothing is merged or deployed by this change.

## Recovered compensation

The current exports contain **1,445,458 observations**, including **4,960 additions**, across 276 employers and 1,240 populated employer/period cells. All 1,440,498 original observations remain; 1,752 West Vancouver observations have exact, source-proven name/title splits with every amount, expense, period and source preserved.

- 2,670 elected observations: 1,796 MLA member-years and 874 cabinet executive-salary components. Components remain separately scoped and are not represented as complete annual compensation.
- 1,053 administration observations: 310 early deputy/associate-deputy records and 743 Assembly staff records. The existing 919 later deputy records were independently checked against official CSVs and were not imported again.
- 1,237 VPD observations: 1,125 anonymous and 87 named records for 2009, plus 25 executives for 2025. All 87 named records uniquely overlap the complete 1,212-row anonymous source, so the overlapping anonymous copies are not added twice. Original evidence and the full overlap ledger remain available.

See [elected compensation](provincial-elected/README.md), [early Public Accounts](provincial-early-administration/README.md), [Assembly staff](assembly-staff-recovery/README.md), [VPD](vpd-recovery/README.md), and [West Vancouver title recovery](west-vancouver-title-recovery/README.md).

## Workforce data

The original PSA-2024-42006 PDF corrects all 16 Victoria numeric values, preserves decimal headcounts, and establishes that pages 2 and 4 are telework tables. The unsupported 2019 anomaly and duplicate-page claims are removed. Reporting-period boundaries and calculation methods remain unverified.

The Workforce view also exposes 30 official Workforce Profile CSV tables from the 2018, 2020, 2022 and 2024 releases, containing 10,435 source rows, including 111 ministry lookup rows. Original column labels, suppression markers, NA and blanks are retained. These tables remain separate from named compensation, employee rankings and fiscal-year FTE data. See [workforce provenance](workforce/README.md).

## Qualifications retained

- MLA FYE2008 is absent from the official catalogue. Earlier Assembly staff years remain uncovered.
- The FYE2023 cabinet CSV repeats the prior year's salary vector despite different headings and expenses; the explicit source warning remains visible.
- The 2003/04 Public Accounts errata table has exact $1–$4 differences between displayed rows and printed controls. Assembly staff reports also have small whole-dollar residuals. Displayed values are retained without balancing adjustments.
- Contracted interim-deputy payments are labelled as contracts, and deferred compensation is distinguished from travel/living expenses.
- Anonymous observations, unknown expenses, held sources, currency qualifications, and existing duplicate-looking records remain explicit. A disclosure count is not employee headcount.
- MSP account-payment research is excluded.

## Validation

- Salary export reconciliation passes: 1,421 accepted source files, 1,445,458 rows, 276 employers.
- The [preservation gate](current-preservation-2026-11-06/README.md) preserves 34,284 original research files, all 228,364 compiled observations and all 461 source-backed name decisions. Exactly two previously automatic identity links are reduced from verified to likely under pinned new evidence; no different identity is asserted.
- All 16 frozen historical release gates pass and reproduce 1,749 byte-identical exports.
- JavaScript suite: 816 passing tests and eight existing asset-related skips. Salary Python suite: 985 tests successful, including six skips. Separate elected, early-administration and Assembly parser tests also pass.
- Workforce and OpenCompensation deterministic checks pass. Production and salary-preview builds pass.
- Interactive browser review is incomplete: the available browser could not reach the local preview. No visual QA pass is claimed.

Run `npm run build:salaries`, `npm run check:salaries`, `npm run check:salary-preservation`, `npm run check:opencompensation`, and the CI source/historical checks before merging.
