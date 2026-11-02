# Closure of the 65 additional salary research leads

This pass works through every entry in the [previous additional-gap inventory](../queue-completion-2026-11-01/additional-gap-inventory.md). The [65 original leads](input-leads.json) have stable identifiers and six separate assignments. A lead can cover several years or overlap coverage added by an earlier tranche; 65 counts research items, not missing reports.

All 65 leads have been reviewed to an explicit public-evidence outcome. The nine accepted, frozen collections add **259,336 official payment observations across 227 cohorts**, with **zero compiled observations removed**. Every normalized source file's hash and row count was independently checked against its final manifest. This finishes the finite processing queue; unlocated publications and the records still useful to obtain are listed separately below.

Those 227 cohorts reference **157 distinct source-PDF hashes**; employee and board schedules can share an original PDF. Cohorts and original files are different counts.

The [65-lead outcome table](lead-dispositions.json) retains overlapping grouped leads without counting their observations twice. App reconciliation and publication status are recorded separately in the [release review](release.json).

The baseline is merged PR #37, commit `de42c55e98e42b8001f07e4ecbd210f892ab2716`: **1,125,685 payment disclosures**, comprising **897,321 official** and **228,364 retained compiled** observations, across **254 employers**. The preserved baseline includes prior source metadata and exact employer/period/source row multiplicity, physical pages and monetary cents.

The actual rebuilt **proposed dataset** contains **1,385,021 payment disclosures**: **1,156,657 official** and the same **228,364 compiled** observations, across **270 employers**. It has **51 reporting labels, 1999/00–2025/26**. These are confirmed build results; the proposal remains separate from merge and deployment status.

| Work area | Leads | Research and verification |
| --- | ---: | --- |
| School sources, native and two recovered scans | 7 | [Final worker report](school_native/README.md) · [handoff](school_native/handoff.json) |
| Northern school districts | 8 | [Final worker report](school_north/README.md) · [handoff](school_north/handoff.json) |
| Southern school districts | 10 | [Final worker report](school_south/README.md) · [handoff](school_south/handoff.json) |
| Municipal archives | 8 | [Final worker report](municipal/README.md) · [handoff](municipal/handoff-final.json) |
| Health employee disclosures | 29 | [Final worker report](health_employees/README.md) · [handoff](health_employees/handoff.json) |
| Health board histories | 3 | [Final worker report](health_boards/README.md) · [handoff](health_boards/handoff.json) |
| Total | 65 | Every input lead belongs to exactly one assignment |

A [further board supplement](health_board_supplement/handoff.json), [PHSA's FY2006/07–2014/15 employee history](phsa_history/handoff.json) and [nine other health salary histories](health_other_history/handoff.json) are accepted within existing health leads. The latter adds Northern FY2003/04–2007/08 and FY2014/15, plus Island FY2009/10–2011/12. The separate Fraser FY2010/11 contract detail was compared and retained as supporting evidence; its 492 literal entries produced no extra salary rows or inferred job titles.

| Final collection | Numeric-pay cohorts | Payment observations added |
| --- | ---: | ---: |
| Native school sources and two recovered scans | 14 | 5,476 |
| Northern school districts | 16 | 1,884 |
| Southern school districts | 20 | 9,845 |
| Municipal archives | 52 | 411 |
| Health employee disclosures | 65 | 207,001 |
| Health board histories | 23 | 266 |
| Additional health board scopes | 19 | 186 |
| PHSA earlier employee history | 9 | 22,796 |
| Northern and Island earlier employee history | 9 | 11,471 |
| **Total** | **227** | **259,336** |

The board collections also retain **65 nonnumeric-pay observations** as supporting evidence. These are not numeric salary records, and no zero remuneration was invented. All discovered public salary scopes assigned within these leads have finished extraction and source review; missing originals and unavailable source cells have explicit dispositions.

The [financial-original appendix audit](reviews/financial-catalogue-audit/README.md) inspected all 28 catalogue exception originals and every one of their 789 pages, including OCR of 235 image or sparse-text pages. No named employee or board remuneration appendix was observed in those exact financial statements and notes. This bounded finding creates no individual salary rows and does not establish that separate historical schedules never existed.

The outcome table distinguishes records added, already covered periods, unlocated publications, missing original schedules and accepted records with unresolved source qualifications. Completing public extraction does not resolve every issue in a publisher's document. For example, PHSA's FY2006/07 narrative says 1,280 employees while its complete named table has 1,267; FY2009/10 retains a contradictory 2009 narrative alongside the repeatedly printed 2010 salary-table period. Six PHSA cohorts retain literal unexplained control differences. These qualifications remain visible without invented employees, balancing corrections or an assumed cause.

[Remaining acquisition and clarification work](remaining-acquisition.md) keeps **17 existing held/acquisition/component items**, **10 earlier remuneration-schedule availability questions** and **88 qualified-source notes** separate from finished processing. Its [machine-readable version](remaining-acquisition.json) preserves exact periods, source evidence, next useful records and sending restrictions. The earlier NIC, McBride, SD10 and SD8 requests remain **ON HOLD by user direction**; no message, form, FOI application or paid request has been sent.

The earlier availability questions concern actual audited financial years: PHSA FY2002/03–2005/06, Northern FY2001/02–2002/03, Fraser FY2002/03–2003/04 and Vancouver Coastal FY2003/04–2004/05. Those financial files contain no observed named remuneration appendix, and accepted employee coverage does not include those exact periods. **Whether a separate named schedule exists is unestablished**; financial statements do not establish missing employee rows or a salary publication. Of the 28 audited financial originals, the other 18 have accepted employee counterparts. Island has no additional uncovered primary year in that audit, and no Providence financial original was among those 28.

Root [adopted all ten availability questions](reviews/root-ten-earlier-schedule-availability-questions.json) into the existing lead notes. This adds no salary records or public extraction tasks.

The imports preserve the actual reporting periods and compensation columns. Expenses, aggregate payroll and employer pension/insurance contributions are not invented as individual salary. A printed zero stays zero; an unread, blank or dash cell stays unknown. Literal source residuals remain disclosed, with no balancing corrections or inferred employees. Independent reviewers inspect actual rendered originals as well as reader agreement, controls, row boundaries and complete page coverage.

All earlier official observations remain preserved. Existing compiled observations remain unless a complete source-compatible and period-compatible duplicate-copy comparison separately proves replacement. A matching name or rounded amount alone is insufficient.

The [release verification](release.json) reconciles all **1,125,685 earlier rows and source metadata**, plus all 227 new cohorts and 259,336 additions. The full test runs passed **798 Python tests and 87 Node tests**; four additional release-gate and PHSA-promotion tests also passed. These checks establish the reviewed proposal's integrity; merge and deployment status remain separate.

This is a finite review of the 65 input leads. It does not establish that every BC municipality, sector or historical reporting year is covered. These records are disclosed payments, not complete workforce rosters or annual base salary rates.

The South school handoff also inventories additional public Mission archive links outside its assigned FY2024/25 source. Those links are discovery evidence for a later historical pass; they are not accepted records in this release or missing reports requiring a request.
