# Eight school district fiscal 2024/25 disclosures

The normalized collection stages 1,884 individual payment observations from eight refreshed official SOFI reports. It contains 1,827 employee observations and 57 elected trustee observations. The independent acceptance overlay closes all sixteen cohorts with its exact source and payload pins. No earlier accepted observation or compiled partition is removed.

| District | Employee observations | Trustee observations | Physical salary pages |
| --- | ---: | ---: | --- |
| 8 — Kootenay Lake | 345 | 9 | 51–59 |
| 28 — Quesnel | 210 | 7 | 49–53 |
| 54 — Bulkley Valley | 127 | 7 | 48–51 |
| 58 — Nicola-Similkameen | 153 | 7 | 50–52 |
| 59 — Peace River South | 248 | 7 | 53–59; aggregate overview on 52 |
| 60 — Peace River North | 397 | 7 | 53–61 |
| 81 — Fort Nelson | 50 | 5 | 50–51 |
| 82 — Coast Mountains | 297 | 8 | 52–57; aggregate continuation on 58 |

The explicit schedule/declaration period ends June 30, 2025. These are payment disclosures, not annual salary rates or complete employee rosters. Employee schedules are labelled above $75,000; every literal disclosed row is preserved, including a published below-cutoff SD58 employee. Trustee schedules are separate. SD8 publishes whole dollars; the other reports publish cents. Expenses stay separate from remuneration. Dashes and visibly empty expense cells stay null, while printed numeric zero remains zero.

All source URLs and original PDF hashes are in [sources.json](sources.json). The Ministry copies were refreshed successfully; additionally recovered district originals for SD58, SD59 and SD82 are recorded in the [research evidence](../gap-fill-2026-11-02/school_north/). For SD59 and SD82 the PDF byte hashes differ between copies, but the compared salary page pixels agree. No native text layer is treated as proof of a visible source cell.

Names, positions, punctuation, clipped text and spelling follow the source. For example, SD82 actually prints `Teahcers (Terrace)` and clipped titles such as `CUPE 2052 12 MONTH (`. These are not expanded from job knowledge. Explicit I/l name qualifications remain in provenance. Two SD58 source surnames contain damaged glyphs in both public originals. Exactly those two observations retain their known positions, remuneration and explicit zero expenses with `name=null`; literal fragments `Hodd?r, Allison` and `Sigur?sson, Lara` and the source crops remain in evidence. They were disclosed names damaged in the source, not anonymous employee aggregates. No missing letters are guessed from another year's list or a directory.

The SD81 approval form's generic YEAR box says 2024, while the declaration and remuneration headings explicitly say the year ended June 30, 2025. The explicit salary period is used and the conflict is disclosed. SD82's public copies redact the signature block and leave approval dates blank. They are published official filings; signature glyphs and approval dates cannot be verified from those copies, and no draft status is inferred.

Thirteen of the sixteen named cohort controls reconcile exactly. The following literal source residuals remain visible and are never balanced by changing an amount or manufacturing a person:

| Cohort | Remuneration: rows minus printed control | Known expenses: rows minus printed control |
| --- | ---: | ---: |
| SD8 trustees | $0 | +$1 |
| SD8 employees | +$4 | −$1 |
| SD59 employees | −$504,385.57 | −$580.00 |

The cause is not established. The small SD8 differences do not prove rounding. SD59 has a complete visible 248-row employee listing; page 53 contains trustees only. The printed aggregate is retained as a control, not a synthetic employee. Publication of qualified residual cohorts depends on the independent source review recorded in the acceptance overlay.

The base collection was checked against the pinned pre-expansion salary baseline. None of these eight employer-period pairs already had an accepted 2024/25 cohort. Existing compiled observations stay under their earlier unverified edition labels, with explicit public warnings and `validation.compiledPartitionRetained`. Root owns any later duplicate decisions.

Raw full-page OCR from Tesseract and RapidOCR is preserved separately. A Quesnel ruled-layout Tesseract revision also stays separate from the failed original layout capture. The readers use different OCR models; agreement and confidence are not guarantees of source accuracy. The parser preserves unresolved fields until a bounded source-pixel check or documented original-image reading resolves them. All actual disagreement and low-confidence cases, plus ten preselected image holdouts per source, were reviewed against original pixels. A subsequent audit read all 142 raw reader name word-boundary disagreements and all 406 names in the other three uppercase layouts. The complete independent SD59 transcript caught six shared OCR initial-space errors; all were corrected from source pixels, with initial readings preserved. The initial fixed holdout selection is retained through later geometry corrections; it is not silently resampled. SD82's sloped columns require version 2 source-field sheets, which copy integer source pixels without resampling; earlier SD82 sheets that clipped glyphs are not acceptance evidence.

Offline replay and real-source regressions:

```sh
python scripts/gap_school_north_accept.py
python scripts/gap_school_north_finalize.py --check
python scripts/gap_school_north_handoff.py --check
python -m unittest discover -s scripts -p test_gap_school_north.py -v
```

The research folder retains raw readers, the OCR runtime and model hashes, source image coordinates/hashes, finite image corrections, source-context pages, retrieval history, independent transcripts and exact final input pins. Original PDF refresh and full OCR reproduction require the recorded public URLs and the pinned OCR runtime; they do not send any request to an official records office. No outreach, form submission, FOI application, paid acquisition or contact request was made.
