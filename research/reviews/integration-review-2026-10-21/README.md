# PofBC complete integration handoff — 21 October 2026

This package repairs the incomplete handoff behind the integration review of commit `0dbdb18cfebfb27e5529ce5940850e96eb9a995c` on `claude/vibrant-cori-gy5e6w`.

Start with `PofBC-integration-review-2026-10-21.md`. The complete earlier and Round 4 research is in `datasets/`, with **103 components** and a **1,492-entry source catalogue**. Every original nested component path is preserved. In particular, `datasets/branches/claims.json` contains the 279 branch claims and `datasets/branches/logos/claims.json` contains the 26 logo claims; neither overwrites the other.

## What this package changes

The original three Round 4 evidence ZIPs were supplementary archives. They omitted the complete earlier catalogue and some earlier structured datasets. This package supplies the full structured handoff in one place, with the integration audit and the source-recovery crosswalk. It does not resend all large source-original archives. Original URLs, archive references, retrieval status, checksums and claim locators are retained.

The research still contains explicitly unresolved questions. Catalogue entries include failed retrievals and screened candidates. Review-only election, session and relationship tables must retain their gates. A source URL becoming available does not by itself approve a new entity, prove legal continuity or make a date exact.

## Import the earlier branch batch while preserving newer review metadata

`integration/prior-branch-preserving-batch.json` retains the original batch's **144 records and 118 sources**, with unchanged historical facts. On the 35 records already held at the reviewed commit, it omits older incoming scope/reviewer/unresolved-question metadata and retains the existing completeness Boolean. The original remains in `datasets/branches/handback-importable.json`; the complete transformation is in `integration/prior-branch-preserving-preparation.json`.

From a checkout of the reviewed repository, with this archive extracted beside it under the directory name `pofbc-handoff`:

```sh
node scripts/merge-research.mjs ../pofbc-handoff/integration/prior-branch-preserving-batch.json --dry-run
node scripts/merge-research.mjs ../pofbc-handoff/integration/prior-branch-preserving-batch.json
npm run build:government
node scripts/measure-government.mjs
```

At the reviewed head, the isolated build changes the 251-record tally from **48 starts / 65 sightings / 138 undated** to **51 starts / 176 sightings / 24 undated**. It adds dates for 114 previously undated records. The full test/build and preservation results are in `audit/` and `validation.json`.

The derived batch is based on a specific head. If newer work changes those records, compare their review metadata before reuse. The batch preserves dated observations; it does not establish full lifecycles or fill every intervening parent year. Correct the existing subsidiary-to-accountability conversion and review the C&E Collaborative's entity type before presenting those relationships as resolved.

## Reconnect the held evidence

`audit/source-recovery.json` and `.md` map all 14 explicit missing-source/dataset groups to components, claim IDs, locators and URLs. They cover 82 distinct claim IDs; all 56 distinct claim-source IDs resolve. Each entry retains independent identity, date, model and legal-instrument gates.

`component-index.json` lists the exact preserved paths. Use `sources.json` as the complete catalogue rather than only a module's 48 or 81 new-source rows. Do not infer that a dataset missing from the old ZIP was absent from the research. Conversely, an exact payload missing from the repository does not prove that none of its individual facts were integrated elsewhere.

## Model decisions supported by the review

1. Keep the Treasury alias and plural 1978 ministry title; preserve the old ministry ID as a compatibility alias.
2. Separate legal ending, operational ending, name succession and dated observation. A missing end is not evidence of current survival or proof that an ending occurred.
3. Admit the seven rural boards as searchable historical identities without inventing endings. A shared presence resolver must serve search, snapshots, timelines, navigation and panels.
4. Keep ownership, administration, funding, appointment, membership and ministerial responsibility separate. Ownership alone cannot create a path to the People node.
5. Admit local hospital districts into a shared identity register with an optional local/regional layer; no forced ministry parent is required. Use actual dated governance and electorate rules.
6. Preserve event subjects/participants and field-level source provenance. An asset recipient is not automatically a legal or service successor.

`audit/model.*`, `audit/crowns.*` and `audit/code.*` contain precise code locations and acceptance checks. No model patch or public-branch mutation is claimed by this handoff.

## Files

| Path | Purpose |
|---|---|
| `PofBC-integration-review-2026-10-21.md` | Main review and concrete decisions |
| `PofBC-integration-review-2026-10-21.json` | Machine-readable review summary and component audits |
| `sources.json` | Full source catalogue with status and evidence references |
| `datasets/` | All 103 components, preserving original nested paths |
| `component-index.json` | Component paths, counts and checksums |
| `supersessions.json` | Explicit supersession map; retain the original source conflicts |
| `coverage.json`, `statistics.json`, `prior_statistics.json` | Original research scope/counts; these are not the current repository's coverage metrics |
| `integration/` | Derived import batch, preparation manifest and proposed WANTED reconciliation |
| `audit/` | Independent reviews, source mappings, simulation metrics, test/build logs and remaining undated records |
| `original-research-validation.json` | Validation of the earlier consolidated research package |
| `validation.json` | Validation of this complete handoff and its derived batch |
| `files.sha256` | Checksums for every other file in this archive |

All original date meanings, confidence/status fields, held candidates and source locators remain intact. No batch import should turn a sighting into a foundation, a deadline into execution, an approval into commencement, or current law into an unbounded historical relationship.
