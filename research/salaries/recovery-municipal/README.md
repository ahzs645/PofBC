# Municipal recovery, 1 November 2026

This bounded tranche adds **115 named observations, 13 cohorts and six original reports** for three previously uncovered official employee jurisdictions. It follows the existing municipal audit and continuation queues. It does not repeat province-wide discovery or establish complete historical coverage.

| Employer | Printed calendar periods | Accepted employee rows | Accepted council rows | Physical salary pages |
| --- | --- | ---: | ---: | --- |
| Village of McBride | 2022 | 3 | 8 | 40; 39 |
| Village of McBride | 2023 | 3 | 6 | 45; 44 |
| Village of McBride | 2024 | 5 | 5 | 46; 45 |
| Village of McBride | 2025 | 5 | — | 43 |
| Village of Midway | 2023; 2024 | 4; 4 | 5; 5 | 9; 11 in one agenda original |
| District of Sooke | 2025 | 55 | 7 | 37–38; 37 |

The totals are **79 employee rows in seven complete named employee schedules** and **36 elected-official rows in six separate schedules**. All employee schedules disclose individuals over $75,000; completeness means the complete named threshold schedule, not all employees. No council-only jurisdiction is counted as newly covered for employees. Every employer has zero compiled baseline observations, and the registered source/period/scope check finds no overlap. Other original URLs and historical tasks remain open.

`sources.json` pins the official original URL/hash, actual printed calendar period, physical PDF pages, six-field normalized gzip hash, complete schedule scope, retained evidence hash and caveats. `evidence/` contains original-backed reader inputs or full manual component transcription. Names, initials and printed titles are preserved; absent 2024/25 McBride employee titles remain null. Blank/dash expense cells remain null. No below-threshold aggregates, suppliers, employer payroll costs or expense-inclusive combined totals become individual remuneration.

McBride's originals are scanned pages with OCR overlays. Discovery text was not accepted as independent extraction. All seven included salary pages were completely transcribed from original images, including every name, title or missing title, separate pay, separate expense, printed combined total, row boundary and control. A peer independently transcribed the pages **before opening the candidate**, independently re-rendered the images from hash-pinned PDF pages and then compared all 35 rows exactly. The immutable [peer comparison](../recovery-wave-2026-11-01/reviews/independent-manual-mcbride-comparison.json) links the earlier independent transcript. `manual-transcription.json` is frozen at SHA256 `2965b3106fcc67d6129f7344cf12c705566eb90a49412218d13abc21b04e9200`.

Midway and Sooke contain native salary tables. Two separately implemented readers process every field: Poppler fixed-width lines with a state machine for wrapped titles and displaced cells, and PyMuPDF positioned words with name anchors and independent column/band boundaries. All **80 native rows** agree exactly. Full original-image review also covers all four native salary pages. Sooke's Mills expense is the visible off-baseline **33**, distinct from footer **34**; both readers independently retain it. Native reader inputs are compressed for offline replay.

There are three explicit source caveats and corresponding unsent clarification tasks:

- McBride 2022 is an official original with an **unsigned** approval page and blank dates. Adoption is not claimed. Its council separate controls agree with individual rows: $34,965.00 remuneration and $24,087.83 known expenses. The printed combined total is $55,812.83, while the separate controls sum to $59,052.83. No cause or adjustment is inferred.
- McBride's 2025 employee page and cover both explicitly identify 2025. The adjacent council page 42 explicitly identifies **2024**, with values different from the separate 2024 original. All five council rows from that page remain held; they are neither imported nor relabelled. The complete coherent 2025 employee schedule is included with a public warning. The 2024 employee reconciliation explanatory prose also refers to 2023; its 2024 cover and named-schedule heading are preserved with that note.
- Sooke's 55 employee rows sum to $6,874,288 remuneration and $110,428 known expenses, against printed named controls of $6,874,287 and $110,474: residuals **+$1 and −$46**. The page 37 council controls are $172,062/$26,266, while page 38 carries $172,064 in both council columns and prints overall controls $8,634,739/$282,537. Literal values and discrepancies remain public; null expenses are not imputed. No residual cause is asserted.

McBride 2023–25 originals have visible approval signatures; the reviewed 2022 original does not. Sooke has visible signed approval on page 2. Midway's original agenda contains revised schedules; freshly retrieved, signed official June 9, 2025 minutes approve both revisions on physical page 2, printed page 6952, motions **025-2025** and **026-2025**. The [adoption evidence](../recovery-wave-2026-11-01/municipal/adoption-evidence.json) pins its URL, SHA256, cache, exact motions and signature-page review. No draft marker was visible on the reviewed cover, salary or approval pages; there is no claim that every report page was visually examined.

Sooke defines remuneration as salary, wages and taxable benefits paid during the year, on a cash basis. Expenses cover travel, memberships, tuition, relocation, vehicle leases, extraordinary hiring, registration and similar amounts outside remuneration. McBride imports the distinct printed Wages/Indemnity/Remuneration columns; its separate combined Total includes expenses. Midway imports the separate Remuneration and Expenses columns; its financial-statement reconciliation and employer CPP/EI/benefit costs are excluded from person rows.

Reproduce offline checks from the repository root:

```sh
python scripts/recover_wave_municipal.py --verify
python -m unittest discover -s scripts -p 'test_recover_wave_municipal*.py'
```

`--build --verify` re-reads the hash-pinned originals listed in the parser and rebuilds only this collection and its municipal recovery report. PyMuPDF and Poppler are needed for that original replay. `--verify` and regression tests use retained evidence and need no PDFs or network. Regression fixtures cover complete independent extraction, a rejected altered cell, title wraps, off-baseline expenses, nulls, peer transcript hashes, held council scope and unchanged published control discrepancies.

The [handoff](../recovery-wave-2026-11-01/municipal/handoff.json) records original/data/evidence hashes, exact periods, per-original visual coverage and approval evidence. The [action queue](../recovery-wave-2026-11-01/municipal/work-queue.json) and [prior-task reconciliation](../recovery-wave-2026-11-01/municipal/resolved-prior-tasks.json) link inherited task IDs without changing frozen queues. Original PDFs and rendered images remain under `/tmp`. No existing source collection, global registry, public export, branch or commit was changed; no contacts or requests were sent.
