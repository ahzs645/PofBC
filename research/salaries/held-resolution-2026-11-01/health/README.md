# Held health employee source resolution, November 1, 2026

The complete PHSA fiscal 2024/25 employee original is recovered in `../../held-resolution-health/`. Its 284 pages contain 13,906 named rows, with exact printed controls $1,713,046,476 remuneration and $25,171,641 expenses. All 3,157 raw conflict rows are covered exactly once by the ten frozen batches and ordinary overlays. The separate 47-case source-name audit adds 44 exact name-only amendments and preserves three legitimate lowercase names. No earlier frozen source, raw page, batch or reviewer transcript was rewritten.

`complete-raw-page-manifest.json` pins the 284 raw evidence files. `manual-overlay-001.json` through `010.json` pin reviewer resolutions and their requested field scope. `supplemental-name-amendment-001-muir.json`, `002-additional.json` and their aggregate ledger pin independent original-image confirmation and root adoption. Muir appears once. The ordinary money corrections, including Henry,Laura $55,479→$95,479 and null-candidate expenses read from the original, remain explicit overlays rather than modifications to raw OCR. Ordinary review changed 142 name fields, 10 pay fields and 9 expense fields.

The independent source-fidelity audit at `../reviews/independent-phsa-render-source-fidelity.json` checks all 284 actual `page.get_pixmap(dpi=300, alpha=False)` renders, 13,906 row boundaries and 41,718 name/pay/expense regions. All regions pass two-way ink correspondence within one pixel; exact RGB identity is not asserted. An earlier reviewer alert about a missing initial and extra name was retracted after checking unchanged individual crops and actual PDF renders: it was a viewing/first-pass reading error, not an established source discrepancy. Raw images and review history were retained.

The native-image acquisition paints embedded 300-dpi source strips in display order without resampling. Tesseract 5.5.0 eng/PSM6 and RapidOCR 1.4.4 using independent PaddleOCR PP-OCRv4 detection/recognition networks read every page. `independent-ocr-engine-receipt.json` records wheel/model acquisition URLs, SHA256 and Apache-2.0 license evidence; `ocr-installed-package-receipt.json` records exact installed packages. The optional environment `/tmp/held-health-ocr/venv` uses ONNX Runtime 1.31.1 CPU. It adds no application, global or CI dependency. English-model/per-cell trials were exploratory and were not used as an extra independent reader; full-page results were retained. Multiple configurations of one engine do not count as independent engines.

`ocr-execution-profile-002.json` records the bounded thread change after 152 completed pages. Later execution used three workers, one ONNX thread per worker, OpenCV one thread and single-thread OpenMP/BLAS caps. Completed outputs stayed immutable. The retained page evidence records all raw text, confidence and geometry. The 9×2/18-black-pixel expense-dash template was validated against all 18 manually read first-page dashes. An unrecognized cell never becomes zero or a dash merely because an OCR detector omitted it.

Offline reproduction uses the repository's frozen evidence and standard Python libraries:

```sh
python -m unittest discover -s scripts -p 'test_resolve_held_health.py' -v
python scripts/resolve_held_health_name_amendments.py --aggregate --check
python scripts/resolve_held_health_audit.py --offline
python scripts/resolve_held_health_finalize.py --status verified --check
```

The seven regressions cover the original 49-row fixture, every fixture dash, unrecognized/null/zero/negative distinctions, source-name letters and word boundaries, real name and monetary repairs, guarded field scope, and the shared-engine Muir escape with exact supplemental names and the three unchanged lowercase names.

Re-running original OCR requires the pinned PDF at `/tmp/sector-health/phsa-2025.pdf`, Tesseract and the optional pinned environment. Existing raw pages are resumed, never overwritten. `scripts/resolve_held_health_ocr.py --help` describes the research run; this is unnecessary for an offline accepted-data replay.

`native-retrieval-receipts.json` records bounded public routes: PHSA same-stem XLSX/XLS/CSV requests returned 404; the official finance index returned 200; the alternate official VCH path returned 403 HTML. These response hashes are not PDF source hashes. The earlier Providence/VCH blockers remain unresolved; no outreach or procurement request was sent. The FY2024/25 PHSA recovery does not resolve the nine earlier employee scans or silently expand a board cohort.

`handoff.json`, `work-queue.json` and `candidate-freeze.json` provide the final integration contract. The freeze uses repository-relative paths and exact SHA256 values for the complete collection, provenance, raw page evidence, processing scripts, regression tests, review receipts, queue and handoff. Root owns registry/generated-output integration and publication.
