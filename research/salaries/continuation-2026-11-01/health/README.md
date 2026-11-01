# Health source search and continuation — 1 November 2026

All eight existing health reporting employers were reviewed against every registered collection: **40 accepted employee cohorts** at the start. This pass adds **17 board cohorts / 190 observations / 17 original PDFs**, with no new employer and no new employee cohort. All originals are native text. The accepted candidate collection is [continuation-health](../../continuation-health/README.md).

| Employer | Employee coverage already accepted | Continuation result and remaining coverage |
|---|---|---|
| Fraser Health | FY2013/14–2024/25 | Current financial index returns 403 here; the prior successful index is retained in the old search dossier. Searches did not recover FY2012/13 or earlier originals. No historical absence claim. |
| Interior Health | FY2014/15–2024/25 | Eight new board cohorts FY2018/19–2025/26. Earlier four indexed board originals downloaded but not yet imported. Earlier employee history remains unresolved. |
| Northern Health | FY2020/21–2024/25 | Six new board cohorts FY2020/21–2025/26. Older employee filename tests return 404; current web-search retrieval is robots-restricted. Existing archived employee copies remain needed. |
| Island Health | FY2015/16–2024/25 | Both FY2022/23 and FY2023/24 employee cohorts are already accepted with source warnings. Their issuer-control clarification tasks remain open. Nine native board originals downloaded; two current board links return 404. |
| PHSA | No accepted full employee cohort | Two new board cohorts with 27 known-pay observations and four held unknown-pay rows. Ten scanned employee originals FY2015/16–2024/25 remain OCR processing / existing electronic-table acquisition tasks. The prior OCR pilot is not promoted to accepted data. |
| BCCSS | FY2016/17–2017/18 | New complete FY2017/18 board schedule, 23 named rows. FY2018/19 original note confirms June 29, 2018 amalgamation into PHSA. Later standalone years are not automatically classified as missing. |
| Providence | None | Eight known fiscal employee-year leads still require raw original retrieval; current endpoints return 403. Newly located `/en/media/6981` confirms another FY2023/24 employee endpoint. FY2018/19 employee section remains unconfirmed. |
| Vancouver Coastal Health | None | Known FY2018/19–2020/21 employee originals still return 403. Current `/en/media/29876` indexed employee heading confirms FY2023/24, replacing the prior tentative year label. New `/en/media/23716` confirms FY2022/23 board scope only. Other employee histories remain unresolved. |

The large VCH/Providence native histories remain valuable, but indexed text and screenshots do not expose original-file bytes. No source SHA is invented from indexed text. Public `www`, non-`www`, direct-file/media/download variants and official alternate subdomains were attempted; CloudFront 403 persisted. The old VCH `prod-careers` copy returns 404. Public archive CDX attempts returned 503; this is a retrieval limitation, not evidence of no archived report.

The BCCSS FY2018/19 original supplies the previously missing successor evidence: note 1 says board remuneration is paid/disclosed by PHSA, and note 2 states the June 29, 2018 amalgamation with PHSA as continuing entity. Its all-dash remuneration rows are not imported as zero payments. The exact original hash and rendered evidence receipt are in `bccss-successor-evidence.json`.

Files retained here:

- `inventory.json`: eight employers, accepted baseline coverage, new board candidates and unresolved history.
- `baseline-inventory.json`: all 40 registered accepted health cohort identities checked before import.
- `index-receipts.json`: current primary-index retrieval outcomes and remuneration links.
- `board-retrieval-receipts.json`: 65 attempted board downloads, 63 valid PDFs, including failed links and cached-original fingerprints. PHSA, BCEHS and FPSC remain separate reporting scopes; the originating index label is not an employer identity assignment.
- `retrieval-receipts.json`: explicit VCH/Providence/alternate/archive attempts with timestamps and response hashes/statuses.
- `work-queue.json`: 37 remaining tasks, each using the required eleven-key schema and permitted acquisition route.

The work queue includes concrete **unsent ordinary-copy requests** for published VCH and Providence PDFs and existing spreadsheets, and the existing PHSA electronic-table request. Public scanned PDFs remain processing tasks, not automatic FOI cases. Regional earlier histories remain archive research with existing-copy acquisition as the next route if public recovery fails. No external messages, requests, contact or fee submission occurred.

The 17 source candidates and their exact data/original hashes are in `../../continuation-health/sources.json`; original cache paths are in `../../continuation-health/source-specs.json`. Full original-backed replay and six parser regression tests pass. Northern's 61 observations received independent peer review. Other candidates retain exact row-level two-reader evidence and full small-schedule rendered review for parent cross-review.

No employee partition is replaced: every new source is `board-remuneration` and `completeEmployeeSchedule:false`. No council, trustee, executive or supplier record is silently lost. Accepted normalized files are frozen; the search remains incomplete for older reports and unresolved employer/year gaps.
