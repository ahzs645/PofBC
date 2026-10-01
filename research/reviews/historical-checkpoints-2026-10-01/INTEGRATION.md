# Integration contract

This is a separate research schema, not a drop-in replacement for PofBC production data. Pin the target repository revision before writing an adapter.

## Acceptance sequence

1. Preserve original observations and source locators in a research namespace.
2. Review each candidate identity. Keep rejected, disputed and unresolved mappings; do not discard their observations.
3. Verify the cited passage and archive its source. Separate review date, publication date and historical event date.
4. Accept typed claims with reviewer and decision reason. A current record ID does not mean the historical identity has already been accepted.
5. Add typed relationships: membership, accountability, funding, budget presentation, administrative support or succession. Do not collapse these into one parent field.
6. Accept lifecycle dates only at supported precision. Keep planned, operational, corporate-form and legal events distinct.
7. Test the production adapter and historical interface. Report actual changed outputs rather than predicting how many nodes will reappear.

## Required behavioral tests

| Fixture | Expected behavior |
|---|---|
| No founding date and no historical evidence | Unknown, not nonexistent |
| Named in a 2002 budget | Supported presentation checkpoint; founding remains unknown |
| Observed in 2002 and 2025 only | No silent continuous interval |
| PSEC listed as a corporate-support recipient | Existence evidence without inferred structural parent |
| Same name in different places | Identity review, not automatic merge |
| Tourism BC prior-year comparative in 2010 budget | Not current-year operating evidence |
| Pacific Carbon Trust residual liabilities | Wind-up context, not normal operations |
| Planned Okanagan closure | Planned only until completion is confirmed |
| Royal BC Museum's 2003 corporate-form change | Older institution histories retained |
| BCTS account versus program | Separate date meanings and identities |
| BCFSA operational day versus dissolution month | Date precision preserved |
| Regulator and appeal tribunal renames | Separate subjects and dates |
| WCAT predecessors and pending medical cases | Predecessors and savings retained |
| Broad child-care transfer | No invented birth dates for every nested record |
| Missing supported parent | Body can remain discoverable with placement unresolved |
| Inherited index-only source | Original review limitation retained |

## Table roles

`observations` stores printed names and typed evidence. `events` stores historical changes. `sources` defines official URLs and reviewed scope. `ministry_snapshots` defines all 120 scoped reviews. `identity_crosswalk` contains candidate matches, never automatic merges. `body_year_matrix` is a 1,428-cell lookup, not an independent census. `unmatched_label_ledger` preserves out-of-baseline and historical candidates. `historical_transition_ledger` keeps predecessor/closure context. `review_queue` and `baseline_record_coverage` record remaining work.

The optional downloader does not change the research, the user’s Library or the repository. New retrievals need content and locator verification.
