# Handoff to the next researcher or developer

## Start from the frozen input

Read `START_HERE.md`, `FULL_REVIEW.md`, and the relevant batch review. Confirm the queue-data SHA-256 against `MANIFEST.json`. The date represented by the queue is 2026-09-30; no upstream commit was provided or recovered. Current ministry assignments in the snapshot were not all independently validated.

Do not recreate a selected date's provenance from a same-date event. Obtain the original selected dated claims, competing date claims, legal basis, relations and review records from the matching repository revision. Six selected starts have no same-date exported event, and six dated records remain not_researched/C-only; these are related but not identical sets.

## What was actually done

All 26 export files, 23 skeletons and 238 records were covered by structural/field/assignment checks. `audit/record-triage.json` retains a disposition for every record. Its generated next actions are work instructions, not newly verified history. The original priorities and review statuses were not changed.

The evidence ledger contains 24 source-backed candidate claims for 15 IDs. It includes legal authority/commencement, programme announcements, planned and retrospective actual transfers, current ownership/reporting observations, historical testimony, and two locator repairs. Some findings recheck inherited evidence; do not count them again as entirely new research.

The 2010 Environment pass inspected one specific page, not the whole Estimates. It produced two named observations and one function-only outcome. No new six-checkpoint Finance pass was performed here. Earlier Finance work in the previous review should be recovered as its own ledger with its own scope, not inferred from this package.

## Decisions still required

Teachers Act commencement supports legal milestones, not first appointments/meetings. The three discovery candidates must be de-duplicated against the full atlas before ID assignment. The College of Teachers should not be equated to a renamed council merely because they appear in one transition.

EAB's explicit 1982 testimony and inherited 1981 selected date still require original-claim reconciliation. Powertech's 1988 scalar and 1989 operations account may describe different milestones. Trans Care's planned April and reported fall 2015 transitions should remain separate claims. BC Timber Sales' three 2003 dates, BC Corrections' 1950/1951 accounts and CRT's jurisdiction dates need original sources and exact event meanings.

The Wildfire and Conservation Officer Service range rows must not be flattened. Preserve both observations/bounds and identify whether a change window is inferred. Current source-page content and page-update dates must not be silently treated as historical observations.

## Safe implementation order

1. Pin repository revision and source-file hashes; recover original claims and production schemas.
2. Port the documentation safeguards into the upstream generator and README.
3. Adapt accepted candidate facts to the production claim model without losing evidence or meaning. Apply the two Parks locator repairs to the source claims, not only the export.
4. Test atomic rejection, idempotency and competing-claim preservation in the real importer.
5. Test existence, name and parent resolution separately in the actual Government view. Observation mode needs distinct unknown-start and unresolved-parent states; continuity must be an explicit policy.
6. Expand period rosters and subsidiary lists to discover non-surviving bodies, then resolve identity before adding nodes.

## Verification scope

`verification/tests.txt`: 35 local unit tests, including exact patch application, hash/audit reproducibility and review-ledger safeguards. `verification/browser-check.json`: 12 tests of the generated review interface. These are not npm, production merge, historical resolver or source-truth tests. The browser rendered generated local HTML via `set_content`; direct file navigation was blocked by environment policy.

Source bytes were not archived. The source register supplies URLs, scopes, date roles and locators. A future reproducible research pipeline should retain permissible dated source captures/content hashes with stable claim-to-source links. Failed opens in the access log do not prove source or body absence.

## Rebuilding review artifacts

The authored disposition logic and specific notes are in `scripts/build_review_artifacts.py`; the authored full narrative is `FULL_REVIEW.md`; candidate claims and source metadata are in `research/evidence-ledger.json`. The source register is a copy of the ledger's `sources` array. Do not edit one without keeping the other in sync.

`make_documentation_patch.py` rebuilds `proposed-queue/` and the documentation patch from `original/queue/`. It intentionally replaces the generated proposed directory, not the original data. After editing the report or disposition notes, run `build_review_artifacts.py`, the unit tests and the browser check again. Regenerate the manifest last so hashes reflect the delivered files.
