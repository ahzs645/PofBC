# McBride council-period resolution check

**No new rows are accepted. Five council rows remain held.** This pass concerns only the contradictory council heading in the 2025 McBride SOFI; existing employee and 2022–24 council cohorts remain untouched.

The current official SOFI is byte-identical to the earlier reviewed original. Its council page 42 says **2024 FINANCIAL INFORMATION**. The newly located, adopted 2025 SOFI presentation attachment also says 2024 on its council page 44. The separately published 2025 Annual Report repeats the same five amounts under **VILLAGE COUNCIL 2024** on page 9. Its agenda attachment repeats that table on page 10 with a visible **DRAFT** watermark. The draft reproduction is labelled explicitly and is not accepted as a source.

New [signed June 30, 2026 special minutes](https://mcbride.civicweb.net/document/46177), page 3, motion **090630.26**, establish approval of the 2025 SOFI as presented; page 4 has Mayor and Corporate Officer signatures. This resolves package adoption. The motion does not correct or specifically date the council rows. The annual-report reception motion, June 23, 2026 **080623.26**, only receives that report for information.

The five council names, roles and remuneration agree with the accepted 2024 SOFI, but every expense amount differs. Held known expenses total **$42,578.05**, compared with **$60,151.87** in the accepted 2024 original, a difference of **−$17,573.82**. Both tables' individual rows agree with their separate printed controls. Expense-inclusive combined totals are not remuneration. Identical membership and pay do not establish the year of the different expense cells.

`sources.json` has an empty accepted `sources` list. The six-field gzip in `held/` retains the original five rows and page 42 only as staging evidence; it carries no inferred reporting year. The report includes exact accepted 2022–24 council rows and hashes, literal roles, missing-value semantics and the complete five-person 2024 comparison. No existing observation is replaced or duplicated.

The native Annual Report table was independently read with a Poppler fixed-width parser and a separately implemented PyMuPDF positioned-cell reader; all five names and all 15 monetary cells agree exactly with each other and the previously independent original-image transcription of the held SOFI page. The old image transcription is read and hash-checked, never edited. The new presentation and annual table images were reviewed completely, including headings, rows, controls and the draft watermark. Exactly 16 cover, role, table, staff-approval and minutes pages were visually inspected; no full-report visual review or independent OCR is claimed.

The bounded public archive check covered the finance, SOFI, annual-report and council folders, directly linked relevant original reports/minutes, and all **24** public 2026 regular/special HTML agenda links exposed by the two year folders. No corrected or independently dated council disclosure was found. Four CivicWeb keyword queries displayed a sign-in page; no login was attempted, and those responses are not reported as zero search results. Three official-domain web queries returned no results. This is a bounded check, not proof that no further record exists.

Reproduce from the repository root:

```sh
python scripts/resolve_held_municipal.py --verify
python -m unittest discover -s scripts -p 'test_resolve_held_municipal.py'
```

`--build --verify` regenerates only this collection and its new held-resolution report from the pinned `/tmp/held-resolution-municipal/` originals and acquisition receipts. Offline `--verify` replays retained native inputs, held rows, prior accepted payload hashes and deterministic HTML snapshots. Original PDFs and images stay under `/tmp`.

[Decision and row comparison](../held-resolution-2026-11-01/municipal/decision-and-year-comparison.json), [originals and status](../held-resolution-2026-11-01/municipal/originals-and-status.json), [handoff](../held-resolution-2026-11-01/municipal/handoff.json), [changed-task queue](../held-resolution-2026-11-01/municipal/work-queue.json), and [focused existing-record clarification draft](../held-resolution-2026-11-01/municipal/existing-record-period-clarification-draft.md). The draft has not been sent. No request, contact, fee, FOI, registry edit or earlier frozen-file edit occurred.
