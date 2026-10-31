# Proved municipal reporting-period corrections

Reviewed 31 October 2026. Five complete employee cohorts in the immutable compiler
snapshot match official calendar-year disclosures. **1,028 compiled employee
observations are replaced; all 38 separate council observations remain under
their original, unverified edition labels.**

| Municipality | Compiled edition | Official calendar year | Replaced employees | Retained council | Official employee schedule |
|---|---|---:|---:|---:|---:|
| Bowen Island | 2023/24 | 2023 | 15 | 7 | 15 |
| Langley City | 2023/24 | 2023 | 72 | 7 | 73 |
| Maple Ridge | 2020/21 | 2020 | 216 | 7 | 216 |
| New Westminster | 2023/24 | 2023 | 321 | 10 | 321 |
| North Vancouver District | 2020/21 | 2020 | 404 | 7 | 404 |

The comparison requires every selected compiled name/remuneration observation,
with its multiplicity, to appear in exactly one tested accepted calendar-year
cohort. Names use comparison-only NFKC, case and punctuation/whitespace
normalization. Token order is preserved; names and initials are not expanded or
reversed. Comparison remuneration uses JavaScript `Math.round` to whole CAD
dollars, reflecting the compiled snapshot’s precision. Original published cents,
names, expenses, positions and page references remain unchanged on import.

The accepted sources’ actual reporting periods come from their original
schedules, not from the overlap alone. All five are complete employee schedules;
an executive-only or council-only report cannot replace a compiled employee
cohort. Langley’s complete official schedule includes one published below-threshold
observation omitted from the compilation. The other 72 compiled employee rows
match. Bowen’s 15 names, pay and expenses match without normalization or rounding.

`comparison.json` records all 51 tested compiled partitions, candidate matches,
accepted source fingerprints, and the 46 unresolved partitions. Partial overlap
never deletes a row. Its input scope is the four newly accepted municipal
collections; existing Vancouver corrections remain in their original collection.

`sources.json` contains the five build decisions. Each pins the exact selected
baseline row order/hash, expected selected and retained counts, source IDs, and
the official normalized data hashes. The build fails if either side of the proof
changes. Canonical employer grouping combines known spellings before comparison;
Langley City and Langley Township remain distinct.

An independent review reproduced all five name/pay multisets, found no
normalization collisions in those cohorts, verified the official schedules and
dates, and applied the rules to the complete 383,163-row original snapshot. It
confirmed removal of exactly 1,028 rows, classification/preservation of exactly
38 council rows, and no changes to unrelated baseline observations. That review
also identified and prompted the official-source hash guard, so a later update
under the same source ID cannot silently reuse stale replacement evidence.

Regenerate and verify:

```bash
npm run compare:municipal-periods
node --test scripts/salary-data.test.mjs
npm run build:salaries
npm run check:salaries
```
