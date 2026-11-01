# Salary recovery wave — 1 November 2026

This wave accepts **13,070 official observations** from **25 original reports** and **35 separate cohorts**. **1,129 reviewed compiled observations** are replaced; the dataset grows by **11,941 net records** to **1,022,585**. All **777,862 previously official observations** remain exactly unchanged.

| Collection | Added observations | Cohorts |
| --- | ---: | ---: |
| [recovery-municipal](../recovery-municipal/README.md) | 115 | 13 |
| [recovery-health](../recovery-health/README.md) | 43 | 4 |
| [recovery-schools](../recovery-schools/README.md) | 234 | 6 |
| [recovery-education](../recovery-education/README.md) | 9,987 | 4 |
| [recovery-crowns](../recovery-crowns/README.md) | 2,691 | 8 |

## What changed

The app now contains **790,932 official observations** and **231,653 retained compiled observations**, across **245 employers**. Official municipal coverage is **113/161**, including **110** employee jurisdictions; **48** still lack accepted official records. Regional districts remain outside this municipal denominator.

- UBC contributes 9,633 named FY2025/26 employee observations with exact source controls. Repeated names and eleven negative expense cells remain literal, without assumed identities or causes.
- Coast Mountain adds three complete employee schedules. Salary Plus Benefits is remuneration; the expense-inclusive Total is supporting evidence. Exact small control differences, the unsigned FY2022/23 form and its clipped literal surname remain qualified.
- BC Assessment adds calendar 2020 and FY2021/22–2024/25; FY2021/22 actually covers fifteen months. Earlier T4 Box 14 definitions differ from later FIR remuneration definitions. CPP/EI and broader payroll totals are excluded from named remuneration/expenses.
- BCER adds FY2023/24–2025/26 complete employee schedules. Former Oil and Gas Commission identity/history remains a separate unresolved canonicalization and processing task.
- McBride, Midway and Sooke add employee histories and separate council scopes. Signed Midway minutes establish adoption. McBride’s contradictory-period council attachment remains held; its separately verified employee schedule is accepted with a warning.
- Revelstoke, Central Coast and Gulf Islands add separate employee/trustee scopes. Complete image transcription and independent review cover the small scans; Gulf Islands employees have complete independent native readers. Published control differences remain visible, with no balancing changes.
- Health additions are 43 Interior Health board observations, not new employee coverage. PHSA’s first 49 employee rows remain staged only; the rest of the original is unverified. VCH and Providence original retrieval remains blocked.

## Replacement and verification decisions

The [four reviewed replacement decisions](replacement-decisions.json) pin exact original/data and baseline row fingerprints. BC Assessment’s full 362-row compiled FY2020/21 label matches the original calendar 2020 cohort. The 394 BC Assessment, 249 BCER and 124 Coast Mountain same-fiscal groups also match completely. Source null expenses replace compiler zeros; null/zero equivalence is comparison-only, not a claim that the original expenses were zero. No unmatched council or board observations are removed.

The baseline fingerprint gate checks every original employer/year/source row multiset, including literal names, titles, cents, nulls, physical pages and multiplicity. Every newly imported row must equal its normalized source. Source warning, period, scope and evidence hashes must match published metadata. No previously official row is deleted or edited.

Independent reviews distinguish all-field machine agreement from the exact original pages visually checked. Native readers use independently implemented Poppler, PyMuPDF and PDFMiner paths. Small scanned schedules have full independent image transcription; two Tesseract settings are not called independent OCR. Matching totals alone do not establish acceptance.

## Remaining work and source copies

The [changed-task queue](work-queue.csv) contains **24 open tasks** for this bounded wave; **13 integration tasks** are completed in [the disposition ledger](task-dispositions.json). The [copy/clarification list](acquisition-list.md) contains **18 unsent candidates**. Earlier [six-sector queues](../continuation-2026-11-01/work-queue.csv) and the [current source-catalog comparison](../sunshine-lists/comparison.md) remain available; lists overlap and must not be added as unique missing-report counts.

NIC FY2019/20 needs a complete original: printed employee pages 1, 3 and 5 are missing from the public nine-page file, so OCR alone cannot complete it. CNC FY2020/21 remains held for hidden-versus-rendered surname disagreement. Arrow Lakes remains held for contradictory declaration years. All exact source-control clarifications stay unresolved; no cause is inferred from a numerical coincidence.

No public body was contacted, no request or FOI submitted, and no fee incurred. Public native reports and complete adopted originals are preferred; source discovery and staged OCR are not published employee coverage.

## Review receipts

Use final handoffs and comparison receipts for acceptance. Initial raw reviewer transcripts and first-pass extraction differences are immutable review records; reviewer-only corrections are explicitly reconciled in the final comparisons. They are not alternative accepted datasets.

- [independent crowns compiled overlap decision](reviews/independent-crowns-compiled-overlap-decision.json)
- [independent crowns pdfminer comparison and controls](reviews/independent-crowns-pdfminer-comparison-and-controls.json)
- [independent education compiled partition review](reviews/independent-education-compiled-partition-review.json)
- [independent education component controls](reviews/independent-education-component-controls.json)
- [independent education metadata amendment addendum](reviews/independent-education-metadata-amendment-addendum.json)
- [independent education pdfminer comparison v2](reviews/independent-education-pdfminer-comparison-v2.json)
- [independent education pdfminer comparison](reviews/independent-education-pdfminer-comparison.json)
- [independent education review handoff](reviews/independent-education-review-handoff.json)
- [independent manual interior board comparison](reviews/independent-manual-interior-board-comparison.json)
- [independent manual mcbride comparison](reviews/independent-manual-mcbride-comparison.json)
- [independent manual mcbride normalized payloads](reviews/independent-manual-mcbride-normalized-payloads.json)
- [independent manual review handoff](reviews/independent-manual-review-handoff.json)
- [independent manual schools normalized payloads](reviews/independent-manual-schools-normalized-payloads.json)
- [independent manual sd19 2025 comparison](reviews/independent-manual-sd19-2025-comparison.json)
- [independent manual sd49 2025 comparison](reviews/independent-manual-sd49-2025-comparison.json)
- [independent manual sd64 2025 trustees comparison](reviews/independent-manual-sd64-2025-trustees-comparison.json)
- [independent municipal native comparison](reviews/independent-municipal-native-comparison.json)
- [independent municipal native pdfminer original extraction](reviews/independent-municipal-native-pdfminer-original-extraction.json)

## Reproduce

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
npm run audit:sunshine
npm run preview:salaries -- --build
```

Each collection guide documents original-backed and offline replay. Former releases remain validated with their frozen inputs and totals.
