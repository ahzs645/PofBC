# Historical health recovery — 1 November 2026

This candidate collection adds **four Interior Health board remuneration cohorts, FY2014/15–FY2017/18, containing 43 named rows**. These are new board scopes; all four same-year employee schedules were already accepted. The registered collection and employer index were checked in [baseline-check.json](../recovery-wave-2026-11-01/health/baseline-check.json). No existing employee or board cohort is reimported or replaced.

| Printed fiscal year | Rows | Remuneration | Physical PDF page | Printed control |
| --- | ---: | ---: | ---: | --- |
| 2014/15 | 11 | $160,689 | 2 | No aggregate printed on primary summary |
| 2015/16 | 9 | $172,969 | 2 | No aggregate printed on primary summary |
| 2016/17 | 10 | $176,284 | 1 | Agrees with $176,284 |
| 2017/18 | 13 | $169,627 | 1 | Printed $169,625; literal rows exceed control by $2 |

The source URL, original SHA-256, exact source-byte length, cached original path and parsing geometry are retained in `source-specs.json`. These are the four officially hosted originals already retrieved by the preceding continuation pass; their exact bytes were reverified before processing. All primary schedules visibly state their March 31 fiscal year end. The primary schedules are unsigned; no formal adoption or signature is asserted. No draft text appears in complete native extraction.

Remuneration preserves each published annual remuneration field. The FY2016/17 and FY2017/18 tables separately disclose retainers, meeting fees and significant-travel per diem fees; those fees form remuneration. **None of these schedules publishes expense reimbursements. Every expense value is null**, with a visible public warning on every source. `totalExpenses:0` and `totalDisclosedExpenses:0` are empty known-value sums, not published zero expense controls. No missing expense is inferred to be zero.

FY2014/15 reports Debra Cannon as an explicit $0. Its note excludes $1,250 retainer and $500 meeting fees earned that year but paid FY2015/16. FY2015/16 also explicitly excludes those previously reported meeting payments. Both originals remain literal; neither year receives an adjustment. The FY2014/15 primary summary spells the remuneration recipient Debra Cannon, whereas the attendance page uses Deborah Cannon; the primary pay schedule supplies the imported name. David Goldsmith's printed `$ 21, 594` becomes numeric 21594 with the original typography preserved in evidence.

FY2017/18 has a **$2 published control discrepancy**. Every displayed row and component remains unchanged. `publicWarning` gives the exact residual, and the new [action queue](../recovery-wave-2026-11-01/health/work-queue.json) records an unsent clarification task. No cause is inferred from this arithmetic difference.

Two independently implemented row readers compare every name, title, remuneration, expense-null scope, physical page and row boundary: PyMuPDF coordinate-word rectangles and Poppler `pdftotext -layout` fixed-width text. Both readers also compare every separately disclosed pay component for the wide schedules. A complete manual transcription of all 43 primary rendered rows supplies a third lock. The wrapped Findlay (Frank) Quinn and Dennis Rounsville names remain single rows. The one guarded Poppler character-grid correction joins its split `Tammy Tugnum Dire` / `ctor` cells back into the visibly separate name and title; the complete raw context stays in the evidence.

`evidence/*-rows.json.gzip` contains row-level provenance with raw independent cells/text, pay components, physical page and PyMuPDF rectangle. `evidence/*.json.gzip` retains both original-backed reader inputs for offline replay. Original PDF and rendered image bytes stay under `/tmp`. The handoff reports exactly which original pages were visually reviewed: p2 of the two earlier multi-page originals and the complete p1 schedules of the later two. It does not claim rendered review of secondary attendance/component pages.

Run from the repository root:

```sh
python scripts/recover_wave_health.py --originals --check
python scripts/recover_wave_health.py --check
python -m unittest discover -s scripts -p 'test_recover_wave_health*.py'
```

The original-backed check needs the locked `/tmp/continuation-health` PDFs and PyMuPDF/Poppler. Offline replay needs only checked-in evidence. Six regression tests cover the complete frozen replay, wrapped names/per diem fees, source zero/superscripts, independent-reader mutation rejection, the literal control discrepancy and held PHSA OCR evidence.

Employee recovery remains unresolved. A fully image-transcribed **49-row PHSA FY2024/25 page** is separately staged outside this accepted-candidate collection; 283 source pages still need complete row verification. Fresh bounded VCH/Providence public retrieval attempts still returned 403 HTML. See the [wave health handoff](../recovery-wave-2026-11-01/health/handoff.json). No PHSA, VCH or Providence employee cohort is accepted here, and no compiled partition is replaced.
