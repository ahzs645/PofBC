# Compiled TransLink entity review

All **12,464** immutable compiled `translink` observations are compared with all 29 accepted official employer/calendar cohorts and the separately held CMBC 2024 candidate cohort. The baseline contains 12,464 unique literal financial tuples across its three edition labels. Its 156 anonymous observations are accounted for and excluded from entity attribution proof.

An exact financial tuple means **published name + remuneration + expenses**, retaining literal spelling, case, null and numeric zero. Position is retained as evidence but omitted from financial matching because compiled titles contain editorial employer/role annotations. Every compiled edition is compared against every actual official calendar period; no year alignment is assumed.

| Compiled edition label | Rows | Exact named financial matches | Uniquely matched entity/period | Distinct accepted entities | Name/pay matches, including exact |
|---|---:|---:|---:|---:|---:|
| 2017/18 | 3,237 | 0 | 0 | 0 | 0 |
| 2020/21 | 4,043 | 4,033 | 4,033 | 4 | 4,035 |
| 2023/24 | 5,184 | 3,137 | 3,137 | 3 | 5,136 |

Exact named financial overlap, grouped by the official employer and source period:

| Compiled edition | Official calendar period | Official entity | Exact tuples |
|---|---|---|---:|
| 2020/21 | 2020 | `british-columbia-rapid-transit-company` | 845 |
| 2020/21 | 2020 | `coast-mountain-bus-company` | 2,628 |
| 2020/21 | 2020 | `translink` | 554 |
| 2020/21 | 2020 | `west-coast-express` | 6 |
| 2023/24 | 2023 | `british-columbia-rapid-transit-company` | 119 |
| 2023/24 | 2023 | `coast-mountain-bus-company` | 2,570 |
| 2023/24 | 2023 | `translink` | 448 |

The 2020/21 compiled label has exact financial tuples from **four** distinct 2020 official entity schedules; the 2023/24 label has exact tuples from **three** distinct 2023 official schedules. These are observed partial overlaps in differently labelled source groups, not an authorization to rename, redate or move the compiled groups. No match was found for the 2017/18 edition within the supplied official 2020–2025 comparison window; that does not establish its underlying source period or entity scope.

Supplemental name-plus-remuneration matching intentionally ignores expenses. Its totals include exact financial matches; the additional matches are weaker overlap evidence and do not count as exact financial equivalence. Expense differences for these supplemental-only matches are:

- 2017/18: {}
- 2020/21: {"otherExpenseDifference": 2}
- 2023/24: {"compiledZeroVersusOfficialNull": 1999}

All official cohort row counts, fingerprints, accepted/held status and grouped match counts are retained in `compiled-entity-review.json`. Its hash-pinned `compiled-entity-observations.json.gzip` retains every one of the 12,464 baseline occurrences and its exact/partial source matches. Anonymous payments, position differences, unmatched rows and expense disagreements remain visible. No original person identity, publication provenance or employment continuity is inferred. The held CMBC 2024 schedule remains held.

**Decision:** retain all original compiled observations, employer labels and edition labels. No reassignment, deletion or blanket redating is performed. Complete source equivalence and each exception would need separate source-backed review before any such decision.

Reproduce with `python scripts/follow_through_translink_bridge.py`. The script reads the fingerprinted immutable baseline and current accepted/held row files, then writes only these bridge comparison artifacts. Its input pins are checked by the TransLink regression tests.
