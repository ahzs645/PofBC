# Royal Roads original SOFI follow-through

Reviewed 2 November 2026. All five official reports for fiscal years 2021/22–2025/26 were downloaded from the university's public [plans and reports index](https://www.royalroads.ca/about/who-we-are/administration-governance/governance/plans-reports). All five complete employee schedules are accepted, including the fully reviewed2023/24 scan. Every reporting period runs from 1 April to 31 March; website upload dates do not determine the reporting year.

| Fiscal period | Physical employee pages | Accepted rows | Remuneration CAD | Numeric expenses CAD | Missing / zero expenses | Row sums minus printed named controls CAD |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2021/22 | 25–28 | 223 | 25,258,361 | 273,994 | 107 / 1 | −4 / +2 |
| 2022/23 | 25–28 | 256 | 29,283,383 | 893,903 | 107 / 1 | +8 / +3 |
| 2023/24 | 28–33 | 307 | 34,445,723.53 | 1,106,152 | 155 / 0 | −4.47 / 0 |
| 2024/25 | 28–33 | 321 | 36,566,647 | 1,301,171 | 142 / 0 | −5 / −1 |
| 2025/26 | 26–31 | 334 | 38,818,151 | 1,227,031 | 161 / 1 | +11 / +5 |

The accepted total is **1,441 employee observations**. [sources.json](sources.json) is the build manifest; [dispositions.json](dispositions.json) accounts for every supplied source ID. The eight-source reconstruction is shared with [Langara](../follow-through-langara/README.md).

The source threshold is represented as at least CAD75,000 because its excluded employee aggregate is explicitly “less than $75,000”. Remuneration is the report's disclosed measure, not an inferred annual base salary. The schedules separately reconcile salary accruals, severance, externally funded/capitalized employees, non-taxable benefits and pension/benefit contributions with financial statements. Board schedules, vendor payments, below-threshold employee aggregates and all reconciliation rows are excluded from normalized employee observations. Position cells remain as published, including typos, abbreviations, blank and clipped text.

Every text-readable six-field row agrees between independently parsed PyMuPDF positioned words and Poppler `pdftotext -layout`; the readers do not consume each other's outputs. The scanned307-row2023/24 schedule is independently OCRed and completely reviewed against individual original row crops as detailed below. Per-row coordinates, exact reader text, page counts, independent rows and printed control components are in `evidence/*.json.gzip`. Employee counts by physical page are in each source manifest. Full-page PNGs and contact sheets are retained in `images/` and `visual/`, with fingerprints and a precise review scope in `visual/*.json`. This visual review confirms periods, table boundaries, continuation and controls; it does not claim a manual pixel audit of every employee cell. Small printed-control residuals are preserved and surfaced as warnings. No cells are changed to balance a subtotal.

The2023/24 employee pages are images despite text elsewhere in the PDF. All307 rows were separately read from3x original full-page OCR and5x original column OCR, then every complete source row was inspected in16 readable sheets. The307 individual original row crops and all sheet fingerprints are retained in `scan-review/`. Explicit original-pixel decisions resolve25 fields in the first OCR output and55 in the second, including shared OCR mistakes; both corrected readings replay to the same complete six-field rows. [scan-review/decisions.json](scan-review/decisions.json) and `evidence/rru-2023-24-reviewed.json.gzip` retain the decisions, raw/resolved readings, per-row crop hashes/coordinates and exact controls. No source ambiguity remains. Expenses match the named control exactly. The source visibly prints CORAK, LISA remuneration75928.53; its cents are retained, producing the small−4.47 remuneration residual. LITTLER, BLAIR198,716, DU, JUAN and the clipped PETE, SHAUNEEN title are also retained without speculative correction. Initial OCR evidence remains labelled unaccepted; only the separately reviewed normalized payload enters the build.

For 2021/22, PDF SHA256 `ca0634bec6ffece72903f8dcfb622a6b082526afaf955fadebc80d910ace2258` and all223 independent original rows exactly match the original occurrences in the supplied [complete compiled comparison](compiled-comparison.json). The related compiled223-row cohort retains its **2020/21** label. Twelve financial occurrences differ on each side and the compiled remuneration/expense totals differ. No compiled observation is replaced, removed or redated. [compiled-comparison-reconstruction.json](compiled-comparison-reconstruction.json) records that check.

All104 dashes and three blank 2021/22 expense cells remain null. Stewart, John's explicit0 remains numeric0. Lang, Kim has a blank position. Thomlinson, Eugene's title ends visibly at `Managemen`. Six wrapped 2024/25 position cells are reconstructed across both printed lines; no line of a title is discarded. In 2025/26, the printed name cell `3361 Zornes, Deborah` and Hutchison, Michael's separated minus-sign numeric0 are preserved. The latter report separately prints a CAD42,908 financial-statement reconciliation variance; the employee schedule is not modified to remove that source variance.

Twelve individual 2021/22 source crops—the eleven supplied spelling cases and Funk, Scot/Scott—are in `name-crops/`, with PDF/crop/full-page hashes and point coordinates in [name-crops/receipts.json](name-crops/receipts.json). These are inputs for the root review; this collection makes no identity-link changes. Official index HTML is retained with a fingerprint and resolved original links in [official-index-receipt.json](official-index-receipt.json). [duplicate-check.json](duplicate-check.json) records the existing registered official collection search; no pre-existing official RRU/Langara cohort was found.

Rebuild with Python3, PyMuPDF and Poppler installed:

```sh
python3 scripts/follow_through_rru_langara.py --download --render
python3 scripts/follow_through_rru_langara_receipts.py
python3 scripts/follow_through_rru_scan.py --ocr --promote-reviewed
python3 -m unittest discover -s scripts -p test_follow_through_rru_langara.py -v
```

Original PDFs cache under `/workspace/salary-source-follow-through/cache-rru-langara/`; normalized deterministic gzip files are the offline build inputs. Source-lead URLs and exact PDF fingerprints are committed here. Raw OCR evidence is never imported directly; reviewed source-pixel decisions generate the scanned cohort. Ten native-parser regression tests and ten RRU scan tests cover full fields/counts/controls, original comparison preservation, missing versus zero, complete wrapped titles, displaced name lines, literal source prefixes, individual crop fingerprints, deterministic payload hashes and all eight source dispositions.

The Langara scan has seven additional tests in `test_follow_through_langara_scan.py`. Run the RRU scan tests with `python3 -m unittest discover -s scripts -p test_follow_through_rru_scan.py -v`. All27 RRU/Langara native and scan tests pass.
