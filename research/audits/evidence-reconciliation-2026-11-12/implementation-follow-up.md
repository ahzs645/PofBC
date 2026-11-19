# Evidence audit implementation and remaining work

This pass changes how PofBC presents the evidence it already has. It does not certify that the
salary catalogue, historical relationships, or identity catalogue is complete.

- **Salary disclosures:** distinguish material source qualifications from editorial notes and board,
  council and employee coverage. See the [generated current view](../../salaries/current-coverage-gaps.json)
  and [source-ready work](../../salaries/current-coverage-gaps.md).
- **Identity:** distinguish source specimens from reconstructed artwork, including in the collection
  summary and downloads. The Wildfire Service naming event is not the crest's first verified image.
- **Government:** distinguish Columbia Power management and graph placement from documented joint
  ownership. Do not extrapolate current shares into earlier Waneta periods.

## Follow-up order and acceptance criteria

1. **Source-ready salary cohorts.** Start with the signed SD57 2022/23 PDF. Require a verified edition,
   independently checked rows, reporting scope, and reconciled source controls before publishing.
   Keep employer, reporting period, category and source copy separate. A held copy is not evidence
   that the employer-period is missing. Keep UNBC 2025/26 on hold pending a confirmed approved edition.
2. **Historical relationships.** Review the
   [extracted reorganization clauses](../../reviews/integration-review-2026-10-21/datasets/root/ministry_transfer_clauses.json)
   against the original orders. Classify statutory administration, function transfer, accountability,
   ownership and management before mapping them to dated edges. Use the
   [Crown holdings audit](../../history/crown-subsidiaries-audit-2026-11-14.md) to prioritize BC Rail,
   BC Hydro, Columbia Basin Trust and other documented holdings. Keep unresolved start/end dates
   and inferred parentage explicit rather than filling them from today's chart.
3. **Artwork acquisition.** Start with the documented source leads for BCRTC, SeaBus, Vancouver,
   Kelowna and Kitimat, and with the three located BC Stats raster eras in the gallery timeline.
   Record the original specimen, issuer, date and page or URL before promotion. Keep dated imagery,
   source vectors, raster captures and reconstructed vectors separate.
4. **Patch fidelity.** Revisit stale reviews against the exact current Patcher hashes, with a
   source comparison for each update. A changed hash is not evidence that the prior finding was fixed.
   Treat the candidate and museum lists as overlapping rather than additive.

These are open evidence tasks, not accepted imports or promoted artwork.
