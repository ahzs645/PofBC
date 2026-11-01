# Independent final integration audit

The final row, metadata, scope and replacement audit **passes**. No unresolved integration or data-loss concern was found. This is a read-only audit of the actual published exports and frozen inputs, independent of rerunning the already passed test commands. No frozen source or prior review file was modified.

| Measure | Independently counted |
|---|---:|
| Published observations | 1,010,217 |
| Official observations | 777,254 |
| Retained compiled observations | 232,963 |
| New official observations | 94,819 |
| Previously official observations deleted | 0 |
| Reviewed compiled observations removed | 10,830 across 11 partitions |
| Unresolved same-period compiled observations retained | 4,005 across 7 partitions |
| Employer entries | 239 |
| Accepted normalized source files | 960 |
| New accepted source cohorts | 244 across 7 registered collections |
| Named person-index observations | 1,004,886 |

Every new normalized row was compared exactly with the employer exports, including employer identity, name, position, pay, expense null/value, reporting-period label, source ID, physical page and multiplicity. All 244 new sources agree on expected row counts; their data/evidence fingerprints and accepted source metadata were checked. No previously accepted official employer/year/category was reimported under a new source ID.

The previous release's actual employer exports were read from baseline Git commit `c1cdde042f2d256e562ae027a5cfcac5808cc626`. Every previously official row remains present exactly. The only compiled-row removals are the 11 listed in `replacement-review.json`; each removed count and frozen baseline-export/source fingerprint agrees. An independent complete multiset comparison reproduces all 11 same-year normalized-name/whole-dollar-pay matches while preserving multiplicity. This is comparison evidence for the reviewed replacement decision, not an individual identity claim or a new inferred reporting period.

All seven flagged unresolved partitions retain their exact prior compiled rows, fields, period labels, source IDs and multiplicity. They total 4,005 rows. The opt-in flags, public warnings, validation reasons and both partial employee flags agree with published source metadata. The Museum's ambiguous compiled year remains unverified; matching another year's rows was not used to delete or relabel it.

All 1,004,886 named rows in the person shards match employer-export row multiset fingerprints. Employer coverage arrays exactly agree with those exported in the people index. All source notes are arrays or absent; all 17 new health sources have note arrays and both employee-completeness flags false.

Scope checks confirm:

- All ten new Vancouver Police sources / 142 observations publish `executive-only`, with both partial employee flags false.
- Health's 17 sources / 190 observations remain `board-remuneration`; they do not establish full employee schedules.
- Eight available board-only employer-years return `limited-disclosure`, displayed as **Limited group disclosed**, with an explicit message that board/elected records do not establish employee coverage.
- Eleven available executive-only employer-years return **Only executives disclosed**, with the corresponding employment-absence qualification.
- The new source totals retain employee (85,439), appointee (8,602), board (212), elected (141), executive-only (142) and trustee (283) observations separately. They sum to 94,819.

Two presentation findings were sent to the parent and adopted for the final rebuild:

1. A generic executive-only coverage note said **only five** executive positions even for Vancouver Police 2024's 13 rows. The parent replaced it with count-neutral wording.
2. The generated continuation narrative claimed native-reader comparison for every accepted row, including scanned/OCR/manual municipal cohorts. The parent added wording that distinguishes native extraction from OCR/manual corroboration. The source-specific OCR metadata was already accurate.

The final rebuild clears every source metadata mismatch. All 244 accepted sources match both published indexes on reporting dates, source/data hashes, scope, notes, warnings, validation and retention/completeness flags. Both presentation fixes are verified in the final outputs. The generated JavaScript source, coverage, body and year indexes agree with the public indexes.

All 712 reviewed employer/person row files remain byte-identical after the metadata rebuild; none was added or removed. All 244 normalized payload hashes and all 184 original-source SHA-256 values agree with the actual cached bytes. Original-report and employer-year counts independently reproduce 184 and 184.

The accompanying JSON records exact counts, all 11 removal and 7 retention receipts, initial/final input hashes, all seven final manifest hashes, 244 normalized hashes, 184 original fingerprint receipts and 712 reviewed public row-file hashes. No already passed test command was duplicated for this audit. The frozen source payloads and prior reviews were left unchanged.
