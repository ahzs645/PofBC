# Seven additional school reports, FY2024/25

This worker completes leads003,008,009,011,013,017and025 from the frozen additional-gap inventory. It adds **5,476 named observations** in **14 employee/trustee cohorts**:5,429 employee observations and47 trustee observations. Every original prints a year endingJune30,2025. No message, form, ordinary-record request or FOI application was sent.

| District | Employee observations | Trustee observations | Accepted original |
|---|---:|---:|---|
| SD34 Abbotsford |1,208|7|Ministry published copy, with actual painted native table text|
| SD40 New Westminster |482|7|Ministry published copy, with actual painted native table text|
| SD41 Burnaby |1,771|7|District original; Ministry copy's hidden OCR is unsuitable as a literal reader|
| SD53 Okanagan Similkameen |184|7|District original, scanned remuneration pages7–12|
| SD57 Prince George |841|7|Ministry published copy, with actual painted native table text|
| SD62 Sooke |902|7|Ministry published copy, with actual painted native table text|
| SD84 Vancouver Island West |41|5|District original, scanned remuneration pages54and56|

The earlier discovery labels called all seven native-text processing leads. Refreshing the originals showed thatSD53andSD84 salary sections are scanned, and that the Burnaby Ministry version has a hidden OCR layer. The smaller Burnaby district original has actual visible native text. For example, itsCECH expense is2,852.99 andHAYES expense743.15; the convenience OCR says2,852.77 andFAS.15. The raw convenience text and both source fingerprints remain preserved. No byte-equivalence between the two representations is claimed.

## Source definitions and literal differences

Remuneration and expenses are separate source columns. Named employee schedules use the source75,000-dollar threshold; trustee schedules have separate scopes and include smaller payments. These are fiscal-period payment observations, not annualized salary rates or complete employee rosters. Below-threshold aggregates, employer contributions, suppliers and financial-statement totals are excluded.

All compiled observations are retained, with explicit source metadata and public warnings. No compiled edition is assumed to equal this fiscal year, and no matching name establishes an employee identity.

Source controls reconcile exactly forSD34,SD40,SD41andSD57. Other literal differences remain visible:

| Source scope | Literal named rows | Printed control | Difference |
|---|---|---|---|
| SD53 trustees, expenses |43,932.02|43,923.02|+9.00|
| SD62 employees, pay/expenses |94,036,344 /460,411|94,036,349 /460,412|−5 /−1|
| SD62 trustees, pay/expenses |162,656 /16,297|162,655 /16,296|+1 /+1|
| SD84 employees, pay/expenses |5,231,967.57 /236,827.32|5,231,968 /236,827|−0.43 /+0.32|
| SD84 trustees, pay |84,398|84,397|+1|

No individual amount was balanced to a subtotal and no cause is inferred. SD84 employee rows print cents while their controls print whole dollars; its trustee rows print whole dollars. Fourteen source expense dashes or blanks remain null. SD53 prints actual zeroes, which remain zero.

Ten Abbotsford positions are clipped by the original PDF. Poppler exposes trailing text outside the visible clip; MuPDF respects that clip. Independent actual-source image review selects only the complete visible prefixes. Frost ends at`Senior Manager,Budget & Stude`, andSenft at`Manager, Early Learning & Child`; partially clipped terminal glyphs are excluded. The original longer strings, all initial reader disagreements and exact source crops remain in provenance. A Poppler physical-line break initially hidFrost's numeric fields from the first draft parser; the corrected reader joins those physical text lines without inventing any value. The first draft remains preserved.

## Verification scope

Five native reports have complete independent Poppler/MuPDF field comparisons, painted-text checks and a separate broad payment-row audit that does not require the readers' comma/name/amount predicate. All5,239 observations are accounted for, including the split physical text line. Root independently replayed those readers and source views, personally checked context/control pages and all ten clipped-title targets, and adopted the exact title prefixes in the pinned review receipt. This is bounded personal image review plus complete native corroboration, not a personal transcript of all5,239 rows.

The two scans have retained complete raw Tesseract TSV and independently grouped Paddle/RapidOCR outputs for eight remuneration pages. All46 initial row flags were personally read from original300dpi source crops. Another66 initially agreeing rows with low model scores received personal source-image checks. Twenty deterministic unflagged source holdouts include both trustee and employee scopes; some overlap the confidence-only set. Scores are model values, not accuracy probabilities.

The second reviewer independently transcribed all46 initial flags and20 holdouts, checked source contexts and controls, replayed132 row crops and14 complete/context source views to original pixels, and audited the confidence-only selection/primary-read coverage. That reviewer does not claim a second personal transcript of every confidence-only row. First-reader mistakes and corrections remain additive: currency glyphs recognized as6 do not become pay/expense digits, and actual source spacing separatesLISA A andNIKKI L without adding letters or resolving identities. The earlier primary holdout receipt's whitespace-equivalentNIKKIL reading is preserved and superseded explicitly. Perfect OCR accuracy is not claimed.

## Reproduction

The accepted source manifests and deterministic normalized payloads are under`research/salaries/gap-fill-school-native`. Source PDFs and model caches are outside the repository; the final offline build needs only committed payloads, raw extraction evidence and pinned reviews.

```sh
python3 scripts/gap_school_native_build.py --check
python3 scripts/gap_school_native_coverage.py
python3 -m unittest discover -s scripts -p test_gap_school_native.py
```

To replay native extraction, retrieve the exact official URL/hash in`native-specs.json` into the indicated cache location, then run`python3 scripts/gap_school_native_extract.py --check`. A changed download must be reviewed as a new source version. Native reproduction usesPyMuPDF1.26.6andPoppler.

Image-only reproduction uses`gap_school_native_scan.py` withTesseract5.5andRapidOCR1.4.4/Paddle ONNX models, all inference threads capped at1, and complete physical pages rendered at300dpi. The captured image and source hashes must match before parsing with`gap_school_native_scan_parse.py`. These processing commands require optional OCR tools; offline regression tests require only committed fixtures and the normal project Python environment. No PDF read or render is performed in a PyMuPDF thread pool.

This worker also supplied a separate independent review of three south-school native originals. Its52 first-image transcripts, preserved peer-reading correction, exact executed-parser snapshot and final acceptance are under the`peer-south-native-*` files. They do not add those other workers' records to this collection. Future cross-worker receipts may be appended under`reviews/`; they are outside this worker's seven-source candidate freeze.
