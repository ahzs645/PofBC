# Bounded school recovery handoff

The candidate collection is [recovery-schools](../../recovery-schools/README.md). [handoff.json](handoff.json) pins the exact original/data/evidence hashes, test and replay results, actual worker visual coverage, peer receipts and integration status. [original-receipts.json](original-receipts.json) records all accepted-candidate original URLs/cache paths and rendered page hashes. [work-queue.json](work-queue.json) carries eleven-key actions and links the earlier task IDs in `reason`.

Three originals produce six worker-verified cohorts and 234 observations. None was registered or published by this worker. SD19 and SD49 received complete independent image comparison, with every field on all 117 scan rows confirmed; SD64's 117 rows agree between independently implemented Poppler and MuPDF readers, and its seven trustee rows also received full independent image comparison. The independent peer evidence status is recorded separately, so a successful OCR replay is never confused with peer image review.

Exact completed independent image review coverage:

| Original | Physical page | Image path | Row scope |
|---|---:|---|---|
| SD19 | 50 | `/tmp/recovery-schools/sd19-p50.png` | Five trustees and 37 employees, all fields |
| SD19 | 51 | `/tmp/recovery-schools/sd19-p51.png` | Forty employees and printed controls, all fields |
| SD49 | 53 | `/tmp/recovery-schools/sd49-p53.png` | Five trustees and thirty employees, all fields |
| SD64 | 52 | `/tmp/recovery-schools/sd64-p52.png` | Seven trustee rows and printed trustee control qualification; native reader comparison covers all 117 rows |

The scan transcripts [sd19-2025-manual.tsv](sd19-2025-manual.tsv) and [sd49-2025-manual.tsv](sd49-2025-manual.tsv) preserve blank expenses as empty TSV fields. Their hashes are included in every corresponding compressed evidence file. Peer review files are independent receipts under the sibling `reviews/` directory; do not rewrite them.

Arrow Lakes is held with zero imported rows. [held-originals.json](held-originals.json) records original hash `f0029c4db8be4330e92324ca4d72544719d2391b47bdc9a697f9e7e54cc758c7`. Physical p3's declaration says the attached report is for the year ended **June 30, 2024**, while the page header, year field and remuneration pp47–48 identify **2025**. The visible date is December 18, 2025. Neither a template error nor a reporting year is inferred. It needs a corrected official source or explicit source-specific explanation. Physical p3 image `/tmp/recovery-schools/sd10-p3.png` shows the contradiction directly.

Haida Gwaii remains deferred, with zero imported rows. Keyword OCR locates salary schedules on physical pp8–9 despite native financial text elsewhere in the file. [deferred-located-originals.json](deferred-located-originals.json) preserves that precise processing lead; no full source-image row review or period acceptance is claimed.

The new queue supersedes the exact FY2024/25 processing tasks for SD19, SD49 and SD64 when root accepts the candidates. It preserves the Arrow Lakes processing task as a period-clarification hold and adds precise issuer-control clarification actions. Earlier archive/history discovery tasks remain unchanged; this tranche does not claim complete historical runs. The existing SD8 ending-2026 mixed-year employee hold is untouched.
