# North school source evidence

This folder owns the work on leads 001, 002, 012, 014, 015, 016, 023 and 024: eight public fiscal 2024/25 school SOFI reports. The normalized collection and detailed qualifications are in [the collection guide](../../gap-fill-school-north/README.md).

`refreshed-originals.json` and `ocr-plan.json` pin the successfully refreshed Ministry copies and complete salary page ranges. `raw-ocr/` preserves both OCR readers on each of 47 original 300 dpi pages. Quesnel's additional source layout capture is retained in `extra-tesseract/`; it does not replace the original capture. The `*-discovery-*` files are 125 dpi discovery output and are not acceptance evidence.

`sdNN-raw-reader-rows.json.gzip`, `original-expense-cell-pixels.json.gzip` and `sdNN-pixel-candidate.json.gzip` keep each processing stage distinct. The source-pixel classifier handles only bounded visible empty or isolated dash cells, never invents zero, and was checked against every recognized numeric expense as a negative control. Its threshold/component rules are in `scripts/gap_school_north_pixels.py`. Other ink requires source review.

`source-image-targets.json` is the original fixed image-review selection; `additional-source-image-targets.json` retains newly flagged cases from revised geometry. `source-image-packet-index.json` supplies exact original pixel coordinates and hashes. For SD82 use `sd82-source-field-packet-index-v2.json` instead: the first full-row sheets clipped some monetary glyphs because of the source's slope. `name-spacing-image-index.json` preserves the expanded 142-case word-boundary audit; `uppercase-names-image-index.json` adds a complete producer reread of all 406 names in SD28, SD54 and SD81. Name normalization ignores comma layout only, preserving internal word boundaries. `own-image-review.json` records finite literal corrections, name qualifications and the exact parent-directed two-case SD58 name-unavailable adoption. Raw OCR is never rewritten to hide a correction.

`source-context-image-index.json`, `context-images/` and `source-context-review.json` preserve the actual declaration, scope, monetary definitions and printed controls. `additional-issuer-original-retrievals.json`, `sd58-district-original-retrieval.json` and `issuer-ministry-page-comparison.json` retain additional official copies and the limits of the cross-copy comparison.

`sdNN-image-reviewed-candidate.json.gzip` and `candidate-handoff.json` retain candidate stage history; `review-adoption.json` supplies the completed independent acceptance overlay. Independent review scopes are stated precisely: distinct OCR passes cover every literal row, the producer personally reviewed the finite flagged/holdout source cases, a second agent independently transcribed seventy source-first holdouts and reviewed seven report contexts, another reviews SD59's full employee list, and a third corroborated three specific SD58/SD60 payment rows. A bounded benchmark is not described as a human transcription of every row.

Reproduction from the preserved readers:

```sh
python scripts/gap_school_north_parse.py
python scripts/gap_school_north_pixels.py
python scripts/gap_school_north_candidates.py
python scripts/gap_school_north_finalize.py
python scripts/gap_school_north_finalize.py --check
python -m unittest discover -s scripts -p test_gap_school_north.py -v
```

The pixel stage requires the exact original PDFs at the paths in `ocr-plan.json`. To refresh originals use `python scripts/gap_school_north_discovery.py --refresh`; verify the newly retrieved byte hashes before using them with historical raw captures. Full OCR uses `scripts/gap_school_north_ocr.py --plan research/salaries/gap-fill-2026-11-02/school_north/ocr-plan.json` in the runtime recorded in `ocr-runtime.json`; raw capture files are write-once. No outreach is authorized or performed.

The final producer freeze deliberately excludes the reserved `reviews/` subtree and later peer scripts. Disjoint peer work for other workers can therefore continue without changing the accepted north producer inputs.
