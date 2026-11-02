# Official-source follow-through, 2 November 2026

This release reconstructs the implementation described in the supplied attachments from the official originals. It accepts **55,477 additional employee payment observations from 61 reports and 84 separate employer/period cohorts**. The dataset grows from **1,385,021 to 1,440,498 observations**: **1,212,134 official** and **228,364 retained compiled** observations, across **273 employers**. All original observations, including anonymous records, remain unchanged.

The supplied 481-row CNC/Royal Roads proposal is included within this larger release. Its code was unavailable, so new importers, independent readings, original-page review receipts and repeatable checks were built from the official PDFs. The `provided-*` files preserve supplied background material; they describe the earlier proposal and are not the validation results of this release.

| Collection | Reports | Accepted cohorts | Added observations |
| --- | ---: | ---: | ---: |
| [Community Living BC](../follow-through-clbc/README.md) | 20 | 20 | 3,218 |
| [College of New Caledonia](../follow-through-cnc/README.md) | 7 | 7 | 1,895 |
| [Royal Roads University](../follow-through-rru/README.md) | 5 | 5 | 1,441 |
| [Langara College](../follow-through-langara/README.md) | 3 | 3 | 2,551 |
| [BCFSA, BCIB and PavCo](../follow-through-small-crowns/README.md) | 14 | 14 | 4,255 |
| [TransLink and subsidiaries](../follow-through-translink/README.md) | 6 | 29 | 27,402 |
| [WorkSafeBC and UVic](../follow-through-worksafe-uvic/README.md) | 6 | 6 | 14,715 |
| **Total** | **61** | **84** | **55,477** |

These are payment observations, not unique people, complete employee rosters or annual base salary rates. The additions include **981 individually disclosed withheld-name payments**; each remains a separate anonymous observation. Aggregate payroll, suppliers, board and executive component tables are not converted into employee rows.

## Decisions and assumptions

- Reporting periods follow the original schedule. CLBC's first period covers nine months, July 2005–March 2006. BCFSA's first period covers November 2019–March 2020. Fiscal labels do not imply twelve months of remuneration.
- Each source's remuneration and expense definitions are retained. Blank/dash expenses remain unknown, numeric zero remains zero, and negative recoveries remain negative. Royal Roads' published `75,928.53` decimal is preserved.
- Native schedules were compared field by field using PyMuPDF and Poppler. Scans use separate OCR readings followed by complete source-row pixel review; two Tesseract readings are explicitly described as readings of the same engine. Collection guides distinguish this from independent OCR engines.
- Reproduced differences between individual published cells and printed subtotals are disclosed, with original values unchanged. Their cause is not assumed to be rounding. No payment was adjusted to make a total agree.
- The **2024 Coast Mountain Bus Company employee cohort remains held**: its 3,896 candidate rows disagree with printed controls by +3,859 salary, −3,212 other remuneration, +647 total remuneration and −12 expenses. Independent native readers agree on the cells, but the source does not explain those differences. The other four entities in that same report are accepted. [Held evidence and next action](../follow-through-translink/README.md).
- Official Transit Police policy explicitly establishes TransLink Security Management Ltd. as the entity employing Transit Police personnel. Its six new cohorts use the existing `transit-police` employer. The three new employers are BCRTC, Coast Mountain Bus Company and West Coast Express. [Pinned employer bridge](../follow-through-translink/employer-bridge/policy-bridge-receipt.json).
- Older compiled `translink` observations include payments matching several subsidiaries. Their legal-employer attribution and edition years are not silently rewritten. The [complete comparison](../follow-through-translink/employer-bridge/compiled-entity-review.md) accounts for all 12,464 compiled observations and distinguishes unknown expenses from zero.
- Every existing compiled observation remains available. The Royal Roads comparison supports 211 matching financial occurrences out of 223, with twelve unmatched occurrences on each side; it does not establish complete-copy equivalence. Compiled and official pay/expense totals differ. [Supplied comparison](provided-compiled-comparison.json).

## Source-backed name connections

Original rendered rows and unique financial witnesses support twelve Royal Roads spelling connections and six CNC connections. Fifteen concern candidates in the original 3,173-case queue; Funk, Cornelis and Thorne are three additional source-copy cases. Names as disclosed, amounts, source pages and original compiled reporting labels remain stored unchanged. A connection does not verify a compiled year or establish that two observations are distinct payments.

Each new connection pins both complete live name histories, both complete comparison cohorts, original PDF/data hashes, specific physical pages, inspected crop/full-page hashes and exact financial witnesses. Where an expense is unknown, remuneration must be unique in both complete cohorts; unknown expenses are never equated with zero. CNC's Maides/Maldes and Rourke variants remain held because their remuneration occurs 45 times in each cohort and expenses are unknown in the official source.

[RRU reviewed connections](name-review-rru.csv), [CNC individual review](cnc-name-review.json), and the current [original queue outcomes](held-pair-outcomes.csv) retain the individual decisions. Existing verified and likely confidence levels remain distinct. Pittman's source-established USD amount remains excluded from CAD rankings and aggregates.

The original 3,173-case queue now has **145 verified connections, 25 likely connections and 3,003 unconnected pairs**. Fifteen original cases gained individual source evidence in this release; the three extra connections remain outside that denominator.

## Remaining work and acquisition

[All 134 supplied source leads](backlog-reconciliation.md) were reconciled against current accepted payloads and their hashes. **110 entries are fully accepted for employee scope, one report is partially accepted, and 23 older entries remain unresolved.** Twenty old PHSA/Island Health pending labels and two prepared-implementation manifest pointers were stale and have been corrected in the [live source backlog](../source-backlog.json).

The 23 older entries comprise eleven scanned source/validation tasks, three UNBC document/approval tasks, a Pension Corporation employee-document gap, four executive scope/currency questions, two historical archive tasks and two Vancouver compiled-year/scope questions. The reconciliation gives each source, actual blocker, accepted unrelated scopes and next action. The ten held BC Transit originals were freshly downloaded and fingerprinted; BCIT 2013/14 employee pages were located at physical pages 33–48. These findings do not constitute accepted employee extractions.

Existing NIC, McBride, SD8 and SD10 request drafts remain recorded in the earlier acquisition outbox. **No public-body request, message, form submission or fee authorization was sent.**

## Reproduction and release checks

Run from the repository root:

```sh
npm run build:salaries
npm run check:salaries
python3 scripts/review_follow_through_names.py --check
python3 scripts/check_salary_source_follow_through.py
python3 scripts/check_salary_historical_releases.py
npm run preview:salaries -- --build
```

Each collection guide documents original-PDF download/extraction commands and the complete artifact checks. Normal app builds and CI consume committed normalized evidence without fetching mutable public reports or running OCR. The original-PDF extraction paths remain available for a separate source reproduction.

The current release verifier checks every original observation, every new normalized observation, all 61 document dispositions, held-row exclusion, source fingerprints, missing/zero/negative values, compiled preservation, old identity graph connections and currency separation. `--write` records its successful result in [release-validation.json](release-validation.json).

Two combined builds reproduce **2,061 generated files identically**, including 273 employer-specific name-link exports (152 empty where no names are joined). The [determinism receipt](determinism.json) records the comparison. The [browser receipt](browser-validation.json) covers narrow and desktop layouts, source evidence, old name URLs, accepted/held cohorts and USD separation.

Concurrent changes from main are preserved, including the employer-page treatment of repeated payments and the owner's separately requested Martineau spelling connection. The [concurrent-main capsule](concurrent-main.json) pins that single additional legacy review while preserving the original four decisions. The current verifier checks each employer-specific link file against the complete published graph.

Earlier release receipts remain immutable. Their sixteen historical gates run using exact baseline code and pinned inputs in an isolated directory, reproducing **1,749 original exports byte for byte**. The historical reader adapter supplies only their original byte pins; all 461 earlier adopted identity decisions are still semantically checked against current live observations. This prevents a new source from silently extending an outdated name review.
