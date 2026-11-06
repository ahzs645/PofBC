# West Vancouver title recovery, 6 November 2026

Exactly **1,752 original observations** had their printed title incorrectly concatenated into the name, leaving position null: 349 in 2019, 426 in 2022, 479 in 2023 and 498 in 2024. The 2025 report has no title column and is intentionally unchanged.

Original public PDFs were retrieved afresh and match the hashes recorded in the accepted historical sources. For every row, original physical-page text contains the complete name/title and component-value tuple with the required multiplicity. Splitting only the source's two-column whitespace produces the disclosed name and title; no external title inference or modern job-history lookup is used.

The original accepted collection, source manifests and review receipts remain byte-identical. The corrected gzip copies here are review artifacts, **not an additional collection**. Do not add this directory to collections.json. The full exact correction ledger is `corrections.json`; totals and unchanged amount/page controls are in `validation.json`.

## Reproduce

- `python scripts/recover_west_vancouver_titles.py` regenerates separate review artifacts from frozen inputs and original PDFs. Requires `pdftotext`.
- `node --test scripts/west-vancouver-title-recovery.test.mjs` checks all other fields, count, strict mismatch rejection and exact inverse restoration.

## Integration

Import `applyWestVancouverTitleRecovery` from `scripts/lib/west-vancouver-title-recovery.mjs` in the salary build. Immediately after the complete official-source import loop and before merging or sorting, set `official = applyWestVancouverTitleRecovery(official, corrections)`, loading this directory's `corrections.json`.

For immutable historical validation, use `reverseWestVancouverTitleRecovery(packedRows, index, corrections)` before constructing baseline shards. It recognizes the exact corrected source/year/employer/name/title/pay/expense/page tuple, requires one use of every correction, and restores only the previous combined name and null title. It does not change source definitions, amounts, observations or original receipts.

Ordinary build transformation validates each exact original source row and ordinal, with all 1,752 entries required. Both helpers fail closed if source rows, amounts, pages, counts or identities change. The transformation is deliberately not idempotent: an accidental second application must be rejected.
