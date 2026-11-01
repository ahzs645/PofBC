# Independent compiled-retention integration review

**Pass: no data-loss defect found** in the opt-in retention helper, builder integration or two new tests. Reviewed 1 November 2026 by the health continuation worker. Root implementation and source manifests were not modified.

The helper requires literal `retainCompiledPartition:true`, a nonblank public warning, `validation.compiledPartitionRetained:true` and a nonblank validation reason. If either completeness flag is false, both the source and validation completeness flags must be false. A complete employee source may also opt in when the compiled partition's broader board scope remains unresolved; it still requires the visible warning and validation reason.

The builder exports the opt-in flag and source warning into source metadata, validates the scope before producing output, and preserves only the flagged employer/year compiled partition alongside official rows. It continues applying explicit exclusions after retention. Existing fingerprint-pinned cross-period corrections still act before the final compiled filter; retention does not override a separately reviewed, exactly pinned correction. No new deduplication or unsupported period inference is introduced.

Validation completed:

- `node --test scripts/salary-data.test.mjs`: **21/21 pass**, including both new tests and existing replacement/exclusion/provenance tests.
- Independent completeness matrix: all nine combinations of absent/true/false source and validation flags. Five valid combinations pass; all four one-sided or contradictory partial combinations reject.
- Missing/blank public warning, missing/false retained validation, and missing/blank retention reason reject. An unqualified partial source without the opt-in still cannot erase a compiled employee partition.
- Eight independent CLI build fixtures, executed from `/tmp/continuation-health/review-compiled-retention.mjs`, verify the outcomes below. Failure cases preserve a pre-existing published-output sentinel.

| CLI scenario | Compiled rows retained | Official rows | Outcome |
|---|---:|---:|---|
| Default complete source, no opt-in | 0 | 1 | Prior full replacement behavior |
| Qualified partial source with both false flags | 1 | 1 | Both scopes coexist |
| Qualified complete source with unresolved broader compiled scope | 1 | 1 | Both scopes coexist |
| Explicit exclusion plus qualified retention | 0 | 1 | Exclusion keeps precedence |
| Contradictory source/validation partial flags | — | — | Reject; prior output preserved |
| Partial source without retention or reviewed replacement decision | — | — | Reject; prior output preserved |
| Explicit reviewed partial-scope replacement | 0 | 1 | Prior reviewed replacement behavior |
| Exactly pinned cross-period replacement plus qualified retention | 0 | 1 | Prior pinned correction behavior |

The two added repository tests substantively cover validation and publication: the integration fixture checks employer counts, atlas rows, person-index metadata, visible warning propagation and official/legacy audit counts. No actionable acceptance blocker or destructive edge was reproduced.

Reviewed byte fingerprints:

- `scripts/lib/salary-data.mjs` SHA-256 `e635fa72dc30e321dc8d54fffb443c2c9844ce3286ebb80622485d500497336c`
- `scripts/build-salaries.mjs` SHA-256 `8d4d9ed734ccb01738b8b723c1f239d4e201acdd1fa197f42f9d2a533da1b5f0`
- `scripts/salary-data.test.mjs` SHA-256 `670b0324c5043ec780ced74b5b78f2b4098a8bdbb38593e79e843a2dca646066`
