# Finite financial-original appendix audit

All **28 financial originals / 789 pages** in the captured catalogue exception list were downloaded and inspected. Every page was viewed in a complete rendered index; full native text and OCR of all **235 image or sparse-text pages** are retained. No named employee or board remuneration appendix was observed in these files. No financial total was converted to individual salary data.

The [complete source-scope receipt](complete-source-scope-audit.json) gives every original URL, actual response hash, printed period, complete page census, source-image index, text evidence and personal finding. The ten priority originals without other located salary counterparts were reviewed first. The other eighteen financial files were also inspected; separate salary reports for their years are handled by the salary producers.

The financial notes contain aggregate compensation, salary accruals, pension or benefit liabilities, and Mental Health Plan costs. Actual contents pages and the final financial-note sequences were checked alongside the full page indexes. These findings describe these exact files; they do not establish that separate historical salary publications never existed.

All downloads followed the official catalogue item's explicit `ORIGINAL` bundle and content relation. The returned PDFs have pinned SHA256 values. In all 28 cases the response byte count and MD5 differ from stored DSpace metadata; both observed sets of values are preserved, and the stored checksums are not claimed to identify the downloaded bytes. The returned library cover is retained. No cause is inferred.

One bounded OCR error illustrates why page images were checked: PHSA 2007/08 physical page 24 prints note **16**, while OCR reads 18. The [source-heading image](phsa2007-08-compensation-note-heading-source.png) and original OCR remain available. It changes no source-scope finding.

To replay the pinned receipt with the downloaded originals and raster cache present:

```sh
python3 scripts/gap_fill_financial_catalogue_close.py
```

The fetch, inspect and OCR helpers beside that script describe reconstruction. Fetching again creates a new observation; the initial input snapshot's earlier `rootPriority13` discovery field is preserved, while the final audit uses the corrected ten-item priority list. Do not treat live re-fetches as evidence for previously pinned bytes.

No emails, requests, forms, FOI submissions or payments were sent.
