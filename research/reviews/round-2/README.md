# PofBC — round 2 research handback

**26 September 2026 · Partial tranche · No repository changes made**

This package extends the uploaded research snapshot with **16 newly reviewed sub-agency records**, adds evidence to **WorkBC and Powertech Labs**, and retains every existing record and all 3 gone bodies. It leaves **197 of the original 213 unreviewed IDs without a new research record**. Full lifecycle research is incomplete for the reviewed records too.

## Files to review first

`REVIEW-NOTES.md` explains the findings, unresolved identities, dates, and source locators. `validation-report.json` contains the executed local checks.

| File | Purpose |
|---|---|
| `sub-agencies-researched.json` | Full merged research file: 42 records, 3 gone; uses the supplied `sub-agencies-research/1.0-additive` shape. |
| `sub-agencies-sources.json` | Full source catalogue: 54 sources, including 20 new entries. |
| `round2-records.json` | Alternative delta: 16 inserts and 2 replacements. Do not load alongside the full merged file. |
| `round2-sources.json` | Alternative source delta for a newer checkout. |
| `decision-recommendations.json` | Unapplied WorkBC and EAB proposals. Not a replacement for `research/decisions.json`. |
| `responsible-4.json` | Empty verified-period set plus gap notes. No responsibility coverage gain is claimed. |
| `responsibility-observations.json` | Noncompiled BC Ambulance Service observation; Commission identity mapping still needed. |
| `remaining-work.json` | The 197 template IDs without a new research record. |
| `research-limitations.json` | Retrieval failures, incomplete leads and repository-test limits. |
| `input-manifest.json` | SHA-256 and byte size of each of the 13 uploaded originals. |
| `baseline-qa.json` | Local preservation/delta checks against the supplied snapshot. |
| `validate.py` | Standalone, standard-library structural validator. |

## Integrating into the repository

For the exact uploaded baseline, review the full merged research and catalogue files as replacements for `research/history/sub-agencies-researched.json` and `research/history/sub-agencies-sources.json`.

For a checkout that has changed since that snapshot, use the two delta files and merge **by record/source ID**, preserving newer edits. WorkBC and Powertech are replacements containing their earlier claims, not append-only duplicate records. Do not automatically overwrite a newer checkout with this full snapshot.

Keep `decision-recommendations.json`, the holding observation, the remaining-work queue and audit reports outside the repository's auto-loaded research inputs unless you deliberately add support for them. There are no new verified periods to install from `responsible-4.json`.

The existing **BC Timber Sales** decision remains unchanged. Accepting a WorkBC or EAB recommendation is a separate editorial action. For EAB, obtain the original commencement instrument before choosing the display date.

After merging accepted research, run the supplied project's documented commands from the repository root:

```sh
npm run build:government-history
npm run build:government-events
npm run build:government-atlas
npm run build:research-brief
npm test
```

These commands **were not run here**. Inspect unmatched-parent output, duplicate-ID warnings and the affected Evidence cards. In particular, test corporate-parent matching for `BC Hydro`, the `observation_only` rows, and whether null establishment values fall back to inherited dates. A year or month has not been padded to an artificial day.

## Local validation

Python 3.9+ is sufficient; no external packages or network requests are needed:

```sh
python validate.py
```

This validates package structure and claim provenance. It does not re-fetch sources, certify historical truth, reproduce repository builds, or establish complete coverage.
