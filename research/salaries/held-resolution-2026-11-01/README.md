# Held health OCR, missing pages and conflicting periods

This follow-up continues the specifically held cases from the [previous recovery](../recovery-wave-2026-11-01/README.md), starting at main commit `52864e2f743d90650d23436943bd9fb5207cda04`. The [release reconciliation](release.md) gives accepted additions and exact before/after counts. The [changed-task queue](work-queue.csv) and [unsent acquisition list](acquisition-list.md) distinguish processing from records that still need another source or issuer clarification.

## Assumptions and source decisions

- **Arrow Lakes, FY2024/25:** use the reporting year explicitly printed on both remuneration tables. The original 2024 tables are different. Conflicting declaration and management signoff dates are disclosed in the app; they do not establish 2025 approval/adoption or prove a typo. All 58 employee/trustee observations receive complete original-image transcription and independent review.
- **Kootenay Lake, FY2025/26:** a separately published September 2026 board agenda dates every employee table to June 30, 2026, including the page that the finance version labels 2025. Use the consistently dated agenda and disclose the conflicting finance copy. An information item in adopted meeting minutes is not claimed to be a SOFI adoption motion. Previously accepted trustees remain unchanged.
- **North Island College, FY2019/20:** recover 136 employee and 15 Board observations from the complete five-page salary schedule in a historical official board attachment. The archived package itself is truncated. Independent visible-field comparisons, all 72 surviving signed-scan employee rows and separate Board approval minutes support acceptance of the complete salary scopes. The current nine-page scan genuinely lacks printed salary pages 1, 3 and 5. No complete board-package recovery is claimed; invisible job-title strings remain excluded. The request for a complete original stays unsent.
- **PHSA, FY2024/25:** accept the complete 13,906-row published employee schedule after two independent OCR engines, original-image resolution of all 3,157 flagged rows, 44 additional explicitly adopted name corrections and independent verification against every rendered PDF page. All 284 page boundaries and reporting-year headings pass. Named remuneration of $1,713,046,476 and known expenses of $25,171,641 reconcile exactly to the printed controls. All 5,810 source expense dashes remain null; none becomes zero. Original row boundaries, raw text, confidence values and review corrections stay in the evidence. Nine earlier public PHSA scans remain in the processing queue.
- **McBride council:** package adoption is now established by signed minutes, but the council tables explicitly say 2024. Keep the five disputed rows held pending a corrected table or precise issuer clarification. A 2025 cover, upload path or package adoption cannot independently establish the council rows' period.

Amounts remain payment disclosures under each source's definitions. No annualization, invented full names or titles, balancing adjustments, assumed cause of discrepancies, or speculative year repairs are permitted. Explicit expense zero remains zero; source dashes stay null. Each employee, council or trustee scope stays separate.

## Evidence and independent review

Each worker area retains the exact original URL/hash, bounded retrieval history, all-field extraction comparison, rendered-page review, controls, next actions and handoff. The [review folder](reviews/) preserves independent transcripts and final comparisons. Earlier frozen releases and files stay unchanged. Current public metadata must preserve source warnings and each earlier source's period, scope and identity.

Raw OCR and first-pass reviewer transcripts deliberately retain their original readings. Explicit image corrections and final comparison receipts distinguish those readings from accepted values. Review receipts state which fields were personally inspected and which agreed between independent readers; a review of flagged rows is not described as a manual reading of the entire source.

PHSA also receives a targeted check for name ambiguities shared by both OCR engines. A suspicious spelling only creates a review candidate. Any additional correction requires rendered-source confirmation and a separate explicit name amendment; legitimate lowercase particles remain literal. The original OCR, confidence flags and earlier review batches stay unchanged.

The immutable baseline contains 1,022,585 observations grouped by employer, actual period and source. The new reconciliation checks every baseline multiset, including repeated rows, literal names/titles, cents, nulls and physical pages, before accepting additions. There are no compiled replacements in this follow-up.

## Requests and reproduction

No municipality, college, school district or health authority has been contacted. No request or FOI has been submitted, and no fee incurred. The acquisition list contains drafts and precise existing-record needs, not sent requests.

Prepared drafts cover [the complete NIC original](education/complete-copy-request-draft.md), [McBride's council period](municipal/existing-record-period-clarification-draft.md), and [the two school source clarifications](school-clarification-drafts.md).

```sh
npm run compare:municipal-periods
npm run build:salaries
npm run check:salaries
npm run audit:municipal-salaries
npm run follow-up:municipal-salaries
npm run review:sector-salaries
npm run review:municipal-wave
npm run review:municipal-history
npm run review:salary-continuation
npm run review:salary-recovery
npm run review:salary-held-resolution
npm run audit:sunshine
npm run preview:salaries -- --build
```

Each area's collection guide documents source processing and offline replay. Heavy OCR models and original scans stay outside the application and ordinary CI dependencies. Only reviewed source rows enter the app; staged candidates remain outside published salary exports.
