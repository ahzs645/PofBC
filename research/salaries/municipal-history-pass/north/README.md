# Northern municipal historical-source continuation

Audit date **2026-10-31 America/Vancouver**. The accepted [collection](../../municipal-history-north/README.md) contains **1,349 disclosures: 1,124 employee and 225 council**, across 60 cohorts and 6 municipalities. Hazelton and Port Clements provide new accepted official jurisdictions; the other additions extend actual historical calendar years.

[discovery-receipts.json](discovery-receipts.json) pins 36 retrieved historical originals, their URLs, final retrieval URLs, original hashes, bytes, physical pages, native-text amounts and salary-page discovery. Twenty-eight originals supply accepted employee and council cohorts. The eight other originals are available publicly and remain processing tasks. Three further processing tasks retain the separate council tables in already accepted Williams Lake 2024/2025 and Taylor 2022 reports; the historical council supplement covers Williams Lake 2011–2023. [supplemental-receipts.json](supplemental-receipts.json) pins Hazelton and Port Clements originals. The accepted manifests also retain every exact official document/index URL and calendar-period proof.

[work-queue.json](work-queue.json) contains 49 normalized tasks: 15 processing, 31 public-archive-research and 3 clarification-request. Available scanned PDFs are classified as processing. Archive research remains unexhausted for the other northern municipalities and earlier years; this bounded pass does not assert that missing links require FOI. No municipality was contacted, no request was sent and no fee committed.

The most concrete next processing work is:

| Municipality | Public original years still needing work | Next step |
| --- | --- | --- |
| Chetwynd |2017,2020,2021|Image-only original: OCR, then independently verify every cell/control/period.|
| Northern Rockies Regional Municipality |2016,2018|Scanned salary pages: OCR and complete row verification.|
| Dawson Creek |2015,2016,2018,2025|2015native schedule still needs full review; others need source-layout/OCR review.|
|100 Mile House|2023|Public scanned original already retrieved; verify actual date and complete schedules.|
|Fraser Lake|2023|Public image-only original already retrieved.|
|Houston|2025|Native-looking text is an OCR layer; all surname-only table rows still need rendered verification.|

Hazelton 2024 and Port Clements 2025 are accepted, so their remaining tasks are earlier public history searches. Chetwynd's publication page does not show 2022/2023 in the links inspected; search agendas/archives before considering an ordinary records request. Taylor's inspected page links 2022; more historical publication/agenda research is still needed. Other small municipalities remain explicit archive leads rather than assumed FOI cases.

Clarifications are separated from procurement:

- Williams Lake 2019 has a faithful complete 33-row table but a+$83,235pay-control difference. The source values are accepted with warning while the cause remains unknown.
- Williams Lake 2015–2025 has blank under-threshold expense cells. A named-only expense control requires issuer clarification; blank is not treated as zero.
- Chetwynd 2025 council prints `15.344` for three councillors where other amounts use `15,344`. This monetary separator ambiguity remains held; employee records are separately accepted.

When a public archive search is exhausted, an ordinary request for the **existing annual SOFI PDF or original spreadsheet**, specifying the exact missing calendar years and employee/council schedules, is the useful next acquisition route. Formal FOI is a fallback if the ordinary public-record route fails. The queue does not manufacture procurement tasks before those facts are established.

Rendered full table pages were checked for row boundaries, first/last rows, names, roles/departments, component meanings, controls and source missing values. [rendered-review.json](rendered-review.json) pins core page renders; supplemental proofs are in each reviewed configuration. PyMuPDF and Poppler agree on every accepted row field. The parser and 14 meaningful regression tests reproduce all 60 cohorts. Main core and village supplement remain separate from the later council supplement so independent review can pin each manifest.

An explicitly authorized earlier Williams Lake 2024/2025 **metadata-only** scope amendment is preserved in [corrections/north-expense-scope](../corrections/north-expense-scope/corrections.json), with original manifests/parser/configuration archived before edits, old/new warnings and source metadata hashes. All prior normalized/evidence data binaries are unchanged.
