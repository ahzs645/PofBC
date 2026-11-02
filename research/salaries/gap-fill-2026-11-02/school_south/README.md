# Southern school source queue: ten originals closed

All ten assigned fiscal 2024/25 leads have complete accepted employee and trustee cohorts: **9,845 observations in 20 cohorts**, comprising 9,773 employee payments and 72 trustee observations. They are registered in [the normalized collection](../../gap-fill-school-south/sources.json). Existing compiled data is retained. No issuer was contacted and no form, FOI request or fee was submitted.

| Lead | District | Employees | Trustees | Original used |
| --- | --- | ---: | ---: | --- |
| 004 | 35 Langley | 1,631 | 7 | Ministry published scan |
| 005 | 37 Delta | 1,049 | 7 | Recovered district original PDF |
| 006 | 38 Richmond | 1,592 | 10 | Ministry published scan |
| 007 | 39 Vancouver | 3,360 | 11 | Recovered district original PDF |
| 010 | 45 West Vancouver | 413 | 6 | Recovered district original PDF |
| 018 | 69 Qualicum | 304 | 5 | Ministry published scan |
| 019 | 70 Pacific Rim | 290 | 7 | Ministry published scan |
| 020 | 75 Mission | 444 | 5 | Recovered district original PDF |
| 021 | 78 Fraser-Cascade | 137 | 7 | Ministry published scan |
| 022 | 79 Cowichan Valley | 553 | 7 | Ministry published scan |

These are payment disclosures above each source's employee disclosure threshold, not base salary rates or complete employee rosters. Trustee scope is separate and has no employee threshold applied. Richmond's repeated trustee names represent distinct printed role/service-period observations and remain separate.

## Source fidelity and qualifications

Native district PDFs are read independently by Poppler and MuPDF. Scans retain Tesseract TSV and RapidOCR/Paddle boxes from complete original 300 dpi pages. All 95 scan salary pages replay to the exact original PNG fingerprints. A separate full-page payment census bypasses table windows. It recovered four Fraser-Cascade rows and two Cowichan rows omitted by the first windows; earlier snapshots remain preserved.

Every remaining true field disagreement, recovered row and low-score agreement case received a personal original-image reading. Independent peers read the flagged rows, preselected source-only agreement benchmarks, complete trustee tables/context and calibrated expense cells, and audited the broader source/reader/census evidence. This is a finite, guarded verification policy, not a claim of two personal transcriptions of every row or infallible OCR. Model scores prioritize image review; they are not accuracy probabilities.

All source dashes remain null, explicit zero remains zero and Vancouver's printed negative expense is retained. A model-recognized numeric 7 was incorrectly copied into two early Langley personal receipts despite source dashes. Independent review caught both; the additive correction and all thirteen low single-digit expense cases are retained. The finalizer rejects a numeric expense that contradicts calibrated original dash ink, and rejects a low-score row lacking a pinned personal image receipt. Blank or absent OCR alone never proves a dash or zero.

Whole-dollar source residuals remain literal, with causes unestablished:

| District and scope | Computed remuneration / known expenses | Printed remuneration / expenses | Computed minus printed |
| --- | --- | --- | --- |
| 35 employees | 166,850,947 / 902,007 | 166,850,934 / 902,000 | +13 / +7 |
| 35 trustees | 236,810 / 23,783 | 236,812 / 23,782 | -2 / +1 |
| 37 employees | 114,425,760 / 579,807 | 114,425,758 / 579,812 | +2 / -5 |
| 37 trustees | 247,662 / 17,193 | 247,664 / 17,194 | -2 / -1 |
| 38 employees | 167,465,154 / 1,018,508 | 167,465,170 / 1,018,479 | -16 / +29 |
| 38 trustees | 228,629 / 23,957 | 228,630 / 23,957 | -1 / 0 |
| 45 employees | 44,364,345 / 258,403 | 44,364,330 / 258,403 | +15 / 0 |
| 45 trustees | 133,244 / 1,797 | 133,243 / 1,798 | +1 / -1 |

All other cohort component totals agree exactly. No row value was changed to balance a subtotal. Qualification appears in public source metadata and evidence.

Delta source cell masks clip some trailing name text. Visible fragments are retained without hidden PDF overflow. One payment on physical page 67 retains $90,486 remuneration/$42 expenses with `name=null`; the exact visible fragment `STEWART-HIBBELN, BRIANN` remains supporting evidence. The partly clipped next glyph is not inferred. Independent primary and peer reading mistakes on wide Delta images are preserved and corrected by narrow original-image rereads.

Expense meanings stay source-specific. Langley/West Vancouver starred expenses include international recruitment travel. Richmond's numbered notes disclose program travel and reimbursements; no netting is inferred. Cowichan's expense column includes international recruitment (*) and some teacher remedy payments above $5,000 (**); these amounts are retained in their original columns with the qualification exposed. Pacific Rim has visibly truncated position groups; Fraser-Cascade employee and Mission/Pacific Rim trustee positions are not published and remain null.

## Review and reproduction

The acceptance map is [selected-source-acceptance.json](selected-source-acceptance.json). Native Vancouver/West Vancouver/Mission acceptance is pinned in `school_native/peer-south-native-final-review.json`; complete Delta acceptance is under `reviews/delta-root/`; scan peer receipts are under `school_native/reviews/south-scans/`, `school_north/reviews/south35-38/` and `municipal/reviews/school-south/`. Payload/provenance hashes are in the normalized source manifest.

Offline checks use committed fixtures, standard Python and PyMuPDF; they do not require cached PDFs, network access, OCR models, Pillow or NumPy:

```sh
python3 -m unittest discover -s scripts -p test_gap_school_south.py
python3 scripts/gap_school_south_finalize_scans.py --check
python3 scripts/gap_school_south_build.py --check
python3 scripts/gap_school_south_expand.py --activate --check
python3 scripts/gap_school_south_freeze.py --check
```

Optional original processing requires the pinned public PDFs and OCR dependencies. `gap_school_south_fetch.py` fetches the ten assigned Ministry originals sequentially; independent district originals and public-index snapshots are retained in retrieval receipts. `gap_school_south_capture.py` renders complete pages sequentially, pins source/image hashes and saves both raw readers. `gap_school_south_scan.py` replays the frozen readers; `gap_school_south_census.py` independently widens the payment census and replays original rasters. Source manual readings and their first errors are data, never regenerated from a candidate to assert source agreement. PyMuPDF is not used concurrently in threads. The initial threaded metadata probe is superseded explicitly by `sequential-original-pdf-probes.json`.

## Remaining acquisition or clarification

No named scope in these ten assigned originals remains held. Optional issuer clarification could explain the eight literal component residuals above or provide an unclipped Delta name field. These do not authorize outreach; all remain repository notes.

The Mission finance index also exposes additional public archive links for 2012/13–2023/24 and 2025/26, including duplicate labelled-year links. They are retained in [the archive-link inventory](mission-additional-public-archive-links.json), without representing their contents as accepted records. They extend beyond the assigned 2024/25 lead and can be tried through public URLs without an issuer request. No claim is made that all historical reports have been found or imported.
