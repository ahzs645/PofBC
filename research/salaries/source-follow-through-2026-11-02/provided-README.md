# Official salary-source expansion after PR #41

Reviewed 2 November 2026, starting from main commit
[`2058e825f643641862792706f100ec425c1f705b`](https://github.com/ahzs645/PofBC/commit/2058e825f643641862792706f100ec425c1f705b).

This pass adds **481 official employee observations**, accepts **11 individually reviewed
Royal Roads source-spelling connections**, and records **61 additional official reports
across 10 employers**. The complete employee schedules from two reports are accepted;
the other 59 reports remain extraction or validation work. This is an additive data
update: all **1,385,021 prior salary observations** remain intact.

## Outcome of the original 3,173-pair review

| Outcome | After PR #41 | After this pass |
| --- | ---: | ---: |
| Verified connections | 130 | 141 |
| Likely connections | 25 | 25 |
| Unresolved pairs, kept separate | 3,018 | 3,007 |

The eleven changed candidate IDs are backed by the individual Royal Roads source receipts.
All prior published connections and confidence are preserved. The separate new Funk lead
is outside this original queue and remains held.

## Published data

| Measure | Before | After | Change |
| --- | ---: | ---: | ---: |
| Salary observations | 1,385,021 | 1,385,502 | +481 |
| Official-source observations | 1,156,657 | 1,157,138 | +481 |
| Retained compiled observations | 228,364 | 228,364 | 0 |
| Employers | 270 | 270 | 0 |
| Accepted employee cohorts in this pass | — | 2 | +2 |

The additions strengthen source provenance and fill an official reporting-period gap.
They are not 481 newly identified people or 481 distinct additional annual payments.
Overlapping compiled records remain available, and exact repeated observations are
handled by the existing presentation rules.

| Employer | Original reporting period | Employee rows | Original physical PDF pages | Remuneration sum | Disclosed expenses sum |
| --- | --- | ---: | --- | ---: | ---: |
| College of New Caledonia | 1 Apr 2020–31 Mar 2021 | 258 | 3–7 | CAD 25,302,809 | CAD 184,800 |
| Royal Roads University | 1 Apr 2021–31 Mar 2022 | 223 | 25–28 | CAD 25,258,361 | CAD 273,994 |

These are the reports' disclosed remuneration measures, which can include taxable
benefits and other payments. They are not inferred annual base salaries. Expenses
remain separate; only numeric disclosed expenses are included in their sums. Board,
supplier, below-threshold aggregate and reconciliation lines are outside these two
employee cohorts.

The machine-readable [release reconciliation](release-validation.json) verifies every
prior employer/year/source group and source definition, the exact two new groups, the
name-link changes, and the source backlog. The [updated pair outcomes](remaining-evidence.md)
and [pair-level overlay](held-pair-outcomes.csv) carry forward the original 3,173-pair review.

## College of New Caledonia: complete original employee schedule

The [original 2020/21 SOFI](https://cnc.bc.ca/docs/public/governance/budgets---financial-statements/statement-of-financial-information/sofi-report-2020-21.pdf?sfvrsn=4d8314a_1)
is linked by CNC's [budgets and financial statements index](https://cnc.bc.ca/about/initiatives/budget).
Its SHA-256 is `2140a55a0289cf9f2d96f7c541545ce3932dc8612e05536be597af33fa94c1a5`.

All 258 employee rows were checked with independent PDF readers and the rendered original.
Three surname cells are visibly clipped in the published PDF: `Chambers-Richard, Tamara`,
`de la Pena Gonzal, Rafael`, and `Montgomery-Hewe, Chris`. The normalized observations
preserve those visible names. Longer strings encoded behind the PDF's clipping boundary
are recorded only as extraction evidence.

The source has **138 dash expense cells**, which remain missing values. Its printed named
employee subtotal exceeds the sum of displayed remuneration cells by **CAD 24**; disclosed
expense cells exceed the printed subtotal by **CAD 1**. A separate grand-total arithmetic
difference of CAD 1 is also recorded. The import preserves every displayed amount and
exposes the discrepancies instead of altering cells to balance the report.

The existing 258-row compiled 2020/21 cohort has the same remuneration/expense multiset.
There are 255 exact name-and-money matches and three name differences corresponding to
the clipped cells. The entire compiled cohort is retained. CNC's six held spelling pairs
in the PR #41 queue involve later 2023/24 observations with different payments; this
2020/21 schedule does not resolve those pairs.

See the [CNC source review](../cnc/README.md), [manifest](../cnc/sources.json),
[compiled comparison](../cnc/compiled-comparison.json), and
[visual receipt](../cnc/visual-review.json).

## Royal Roads: source year and compilation differences

The [original 2021/22 SOFI](https://www.royalroads.ca/sites/default/files/2023-03/SOFI-ATT1-Board-2022Jun16_FINAL-RRUWebsite.pdf)
is linked by Royal Roads' [plans and reports index](https://www.royalroads.ca/about/who-we-are/administration-governance/governance/plans-reports).
Its SHA-256 is `ca0634bec6ffece72903f8dcfb622a6b082526afaf955fadebc80d910ace2258`.

The source heading explicitly ends on **31 March 2022**. Its 223 named employee rows
were independently extracted cell for cell and visually reviewed on all four pages.
The report's below-threshold aggregate is for employees earning less than CAD 75,000;
the accepted named cohort is represented as at least that threshold.

**104 dash cells and three blank expense cells remain missing.** The explicit numeric
zero for Stewart, John stays zero. The blank position for Lang, Kim and the clipped
published title for Thomlinson, Eugene are preserved. Compared with the named totals
implied by the report's combined and below-threshold controls, displayed remuneration
sums are **CAD 4 lower** and disclosed expenses **CAD 2 higher**. These are documented
source discrepancies, not balanced by changing employee amounts.

The compiled dataset labels a related 223-row cohort **2020/21**. A complete occurrence
comparison finds **211 matching remuneration/expense combinations** and **12 unmatched
occurrences on each side**. Compiled remuneration totals CAD 25,267,436 versus the
original's CAD 25,258,361; compiled disclosed expenses total CAD 258,873 versus
CAD 273,994. For example, Janine Hughs/Hughes has CAD 91,461 in the compiled observation
and CAD 81,461 in the original; Lynn Gregg has CAD 114,058 versus CAD 114,958.
The comparison retains every occurrence, including duplicates and missing cells.

These differences prevent a blanket replacement or relabeling. Both sets of observations
and their original labels remain. The university's separately located 2020/21 audited
financial statements contain no named employee remuneration schedule and therefore do
not establish the compiled cohort's reporting period.

### Eleven individual spelling connections

| Compiled spelling | Reviewed original spelling | Original PDF page |
| --- | --- | ---: |
| Mittleman, Robert | Mittelman, Robert | 27 |
| Osterfard, Don | Ostergard, Don | 27 |
| Etmanskl, Catherine | Etmanski, Catherine | 25 |
| Corontca, Paul | Coronica, Paul | 25 |
| Sllck, Jean | Slick, Jean | 27 |
| Kajzer Mltchell, Ingrid | Kajzer Mitchell, Ingrid | 26 |
| Wafal, Hassan | Wafai, Hassan | 27 |
| Burtol, Lorraine | Burtoi, Lorraine | 25 |
| Devonney, Don | Devenney, Don | 25 |
| Issak, Mark | Isaak, Mark | 26 |
| Brlgham, Tim | Brigham, Tim | 25 |

Each correction has an individually reviewed original crop, source and page fingerprints,
complete alias and target observation fingerprints, a unique financial witness in both
cohorts, and an explicit review of the unresolved compilation label. Missing expenses are
not zero; where expenses are missing, remuneration alone must be unique in each cohort.
No raw name, amount, expense, title, reporting label or source observation is rewritten.
The correction verifies this source-copy spelling; it does not establish a lifetime identity.

The extra original records also made the existing heuristic propose `Funk, Scot` →
`Funk, Scott`. That plausible match is explicitly held separately in
[the conservative holds](../name-links/source-expansion-held.json), pending an individual
source-copy review. It is not counted among the eleven adopted corrections.

See the [Royal Roads source review](../royal-roads/README.md),
[full compiled comparison](../royal-roads/compiled-comparison.json),
[parent visual review](visual-name-review.json), [adopted review receipt](source-copy-receipt.json),
and [applied decisions](../name-links/source-expansion-reviewed.json).

## Other official sources found

| Employer | Additional reports | Reporting periods | Status in this pass |
| --- | ---: | --- | --- |
| College of New Caledonia | 7 | 2018/19–2024/25 | 2020/21 employees accepted; six scanned reports pending |
| Royal Roads University | 5 | 2021/22–2025/26 | 2021/22 employees accepted; four later reports pending |
| TransLink | 6 | Calendar 2020–2025 | Downloaded and fingerprinted; entity and employee/board scope review needed |
| Langara College | 3 | 2022/23–2024/25 | Downloaded and fingerprinted; complete employee extraction pending |
| BC Financial Services Authority | 7 | 2019/20–2025/26 | Downloaded and fingerprinted; first partial period and a scan need handling |
| BC Pavilion Corporation | 1 | 2024/25 | Downloaded and fingerprinted; employee/board separation pending |
| Community Living BC | 20 | 2005/06–2024/25 | Downloaded and fingerprinted; two scans and historical period review pending |
| WorkSafeBC | 3 | Calendar 2023–2025 | Downloaded through public form and fingerprinted; employee extraction pending |
| University of Victoria | 3 | 2019/20, 2023/24, 2024/25 | Downloaded and fingerprinted; complete employee extraction pending |
| BC Infrastructure Benefits | 6 | 2019/20–2024/25 | Downloaded and fingerprinted; corporate/project/board scope review pending |
| **Total** | **61** | | **2 accepted employee schedules; 59 reports pending employee validation** |

The [detailed source discovery](additional-sources.md) gives official indexes and handling
requirements for the original 56-document search. [Discovery records](discovered-sources.json)
and [download receipts](download-receipts.json) retain that search as evidence;
[Royal Roads leads](../royal-roads/source-leads.json) record the five additional SOFIs and
one excluded financial-statement document. The [current backlog](../source-backlog.json)
combines all 61 entries with current acceptance state. It preserves the 73 earlier entries.

Fifty-eight of the 61 reports were downloaded and fingerprinted: the original 56, plus
Royal Roads 2021/22 and 2022/23. The last three Royal Roads documents were located on
the official index; their file contents still require download and validation. The excluded
2020/21 audited financial statement is outside the 61-report count.

The newly located sources cover employers responsible for 86 previously unresolved pairs
in the nine-employer search. Their existence alone does not resolve those identities.
The BC Ferries search located executive disclosures and an FOI archive, but no complete
named employee schedule for its 59 held pairs. Earlier health-authority recovery is already
present on main and should not be imported a second time.

## Reproducibility and release safeguards

The live build consumes reviewed, hashed normalized data and requires no source downloads.
Historical receipts remain immutable. A separate isolated reconstruction restores the prior
collection registry, source backlog and name-link builder, reproduces all **1,749 original
published export files byte for byte**, and runs all **15 original historical gates**.
The live release checker independently proves preservation of all original observations
and connections while admitting only the two new source cohorts and reviewed spelling changes.

```sh
npm run build:salaries
npm run check:salaries
node scripts/replay-source-copy-review.mjs --check
python3 scripts/check_salary_source_expansion.py --check
python3 scripts/check_salary_historical_releases.py
npm run preview:salaries -- --build
```

Original PDF re-extraction commands and dependencies are documented in each collection's
README. Parser regression fixtures cover complete rows and pages, missing versus zero
expenses, exact source values, residuals, clipped names, source periods and refusal to
replace the mismatched compilation. Name-review tests reject changed sources, incomplete
histories, ambiguous monetary matches, currency mismatches and unreviewed crop changes.

### Verification performed for this update

- The complete live salary build, export reconciliation and source-copy replay pass.
- All 15 Node salary test files pass, including the new source-copy and historical-evidence guards.
- The broad Python parser run completed 850 tests with five existing skips and no failures;
  the additional 15 live-expansion guard tests also pass.
- Historical reconstruction reproduces 1,749 files byte for byte and passes all 15 prior release gates.
- The salary preview compiles successfully. The connected browser could not reach the workspace
  preview server, so this pass does not claim a completed browser smoke test.

These are local verification results. GitHub Actions results belong to the pull request's
checks and should be read there; the prior PR #41 browser and CI results are not reused as
results for this update.
