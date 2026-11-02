# PHSA historical employee schedules

This recovery covers all nine fiscal schedules from 2015/16 through 2023/24. The already published 2024/25 schedule is separate and unchanged. The nine distinct official scans contain 1,480 physical pages, including six narrative covers, and 64,912 named salary observations on 1,474 salary pages. Source hashes, URLs, byte lengths and actual periods are in [source-inventory.json](source-inventory.json).

The full machine capture, source-row staging and field reviews are complete for all nine schedules. Exact selected candidates retain every original row and have zero pending fields. Publication additionally requires the final independent replay and explicit root acceptance of the complete nine-source set. Immutable held candidates remain review evidence until that gate closes.

| Fiscal period | Physical pages | Salary observations |
| --- | ---: | ---: |
| 2015/16 | 128 | 4,545 |
| 2016/17 | 144 | 5,118 |
| 2017/18 | 139 | 5,072 |
| 2018/19 | 111 | 6,041 |
| 2019/20 | 121 | 6,913 |
| 2020/21 | 148 | 7,941 |
| 2021/22 | 188 | 8,270 |
| 2022/23 | 217 | 9,104 |
| 2023/24 | 284 | 11,908 |

## Evidence and interpretation

Every input is an actual PDF-painted RGB render at 300 dpi, using PyMuPDF 1.26.6. No extracted image-strip composition or invisible text is used. Complete independent source-render hashes, original remuneration-ink anchors, bidirectional name coverage and staged-row boundaries establish the source geometry. Page counts alone do not establish source identity: the two 284-page schedules for 2023/24 and 2024/25 have distinct hashes, dates, layouts and employee observations.

Tesseract LSTM and PaddleOCR/ONNX are independent readers. The [runtime receipt](ocr-execution-receipt.json) records versions, model hashes, canonical acquisition URLs and licenses. Three OCR workers with one thread each were the maximum machine allocation. Large originals, models and full rendered-page caches remain under `/tmp`; no OCR dependency was added to the application or CI.

Each source has a separate processing profile. Full-page row counts vary by layout; no 49-row template is imposed. Original source dashes require source-specific single-horizontal-glyph geometry or literal image review. Blank cells and missing detections never imply null or zero. All 205 image-transcribed first-table dash cells pass the nine independently checked profiles, while all 200 numeric expenses fail dash classification.

The raw per-page evidence retains both complete OCR streams, confidence scores, source/render/model/profile hashes and every original flag. Complete first-table image-first fixtures cover 405 names and 810 monetary fields. Ordinary packets freeze their exact requested fields before review; narrow name/pay/expense views preserve native source pixels and retain full-row context. Reviewers freeze source-only transcripts before opening machine alternatives. All corrections are separate immutable overlays, applied by field rather than replacing unrelated columns.

The [paired-reader policy](paired-reader-field-policy-002.json) permits only otherwise guarded, unreserved, confidence-only fields with exact independent agreement. It never treats a score as an error probability, discards an original flag, revokes a frozen review, changes a salary value, or resolves a genuine disagreement. Strict positive-integer type checks apply to both readers and the candidate; names retain punctuation, word-boundary and source-case guards. Dash proof is a separate route. The deterministic predeclared holdout covers 90 rows and 222 fields across all nine layouts; all final source readings match. Four root first-pass name reading errors are transparently retained and corrected through fresh source rereads/peer evidence. This finite check does not mean every cell was personally transcribed.

Visually identical I/l readings use exact peer/root-adopted contextual qualifications with all visible alternatives retained. The separate [rn/m policy](source-name-segmentation-review-policy-002.json) permits only explicitly declared finite joins/splits after two original-image readers and root case adoption. Neither is a generic name-repair, dictionary or identity rule. Any other finite ambiguity needs its own exact pinned root authority. Monetary and period uncertainty is never waived.

Every final manual monetary value that matches neither parsed reader receives a fresh source-only human check. Missing numeric parses remain distinct from source dashes. The fresh reader freezes actual-image readings before seeing author values; any first-pass mistake is preserved with an explicit source reread and amended overlay when necessary. Derived confirmation ledgers replay the exact source-only target set, both frozen histories, original crop hashes and effective field-limited overlay. Source totals are never used to choose a digit. Qualified name preferences can differ between readers; the exact finite alternatives and any preference disagreement remain visible in root adoption and provenance.

Final name assurance uses native 300-dpi source context and integer crops from complete 600-dpi original-page renders. The bounded review covers qualified names and additional direct readings identified by the declared quality rules; it is not a new personal transcription of every row. Earlier partial high-resolution views and reading mistakes remain in their original receipts. Unsupported alternatives are withdrawn through exact root-authorized revisions, while supported finite families and honest preferred-reading differences remain explicit. Supersession chains select new immutable overlays and preserve every preceding review, name family and monetary proof. Small source and observer-history crop files are archived with their exact original references so independent replay does not depend on temporary reviewer directories.

## Source qualifications

The original remuneration column is a fiscal payment disclosure above $75,000, not an annual salary rate or workforce census. No job titles are printed, so positions remain null. Expenses can include direct reimbursements and third-party supplier payments. The unsigned standalone publications do not independently establish board adoption. Earlier covers enumerate cash remuneration components; later schedules are not assigned that enumeration without source evidence.

The 2015/16 final-page Zulfiqar payment of $481,982 includes a printed explanation of $333,272 salary, $19,724 MOCAP/retroactive pay, and a $128,986 correction of 2014/15 unpaid-leave coding reported in 2015/16. Preserve the complete payment, source marker and note; do not subtract, annualize or move it between years.

The 2017/18 cover categories sum to 5,073 while its headline and actual schedule contain 5,072 observations. The 2018/19 actual schedule contains 6,041 observations; the cover headline says 6,042 and its categories sum to 6,025. These literal discrepancies do not authorize manufactured rows. Printed financial controls are independently transcribed and every final residual must be reported without balancing or an invented cause.

Final literal row sums differ from printed controls by +$31 remuneration and +$28 known expenses in 2015/16; $0 and −$5 in 2016/17; and +$5,220 and $0 in 2019/20. Both controls reconcile in the other six schedules. These residuals are retained without an established cause. The final early-2019 money review corrected exactly three source cells, preserving the original sparse first transcript and every reviewer correction; it did not adjust any amount to force reconciliation.

All repeated names and observations remain. For example, 2023/24 physical page 142 contains two Lee,Cassandra observations with distinct amounts. Original physical-page references are retained. Every new source defaults to `retainCompiledPartition:true`; only root can adopt an exact independently proved compiled replacement.

## Offline replay

The committed raw/evidence, fixtures, overlays and small justified review images support field replay without installing OCR models or accessing `/tmp` originals:

```sh
python -m unittest discover -s scripts -p test_finish_salary_phsa.py
python scripts/finish_salary_phsa_supplements.py --check
python scripts/finish_salary_phsa_ledger.py
for source in phsa-2017-18 phsa-2023-24; do
  python scripts/finish_salary_phsa_finalize.py --source "$source" --revision 3 --check
done
for source in phsa-2015-16 phsa-2016-17 phsa-2018-19 phsa-2019-20 phsa-2020-21 phsa-2021-22 phsa-2022-23; do
  python scripts/finish_salary_phsa_finalize.py --source "$source" --revision 4 --check
done
```

The commands select explicit final revisions: v3 for 2017/18 and 2023/24, and v4 for the other seven schedules. Earlier v3 evidence remains unchanged. The finalizer verifies immutable inventory/profile pins, replays every derived overlay byte-for-byte, checks exact field scope/types/order/multiplicity, requires all nine passed holdouts and refuses pending fields. The separate promoter requires a hash-pinned root adoption of all nine independently closed sources before creating the active verified collection manifest. Candidate and evidence bytes stay unchanged; the active manifest records the root and peer acceptance pins. The PHSA candidate freeze excludes that later active manifest and parent release artifacts to avoid a circular hash dependency.

Recomputing OCR or independent actual-source raster checks additionally requires downloading the exact original hashes and using the separately recorded research environment. Negative name-column/model trials and the predeclared [money-column trial](money-column-trial-001-comparison.json) remain evidence: the dense 2019/20 numeric trial worsened, so no broad reprocess/profile change was adopted from it.
