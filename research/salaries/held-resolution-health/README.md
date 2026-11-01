# PHSA complete employee disclosure, fiscal 2024/25

This collection adds the complete 13,906 named employee observations in the officially published Provincial Health Services Authority schedule for April 1, 2024–March 31, 2025. The disclosure covers remuneration exceeding $75,000. It is a threshold schedule, not a workforce census or an annual base-salary table.

Original: [FY2025 Employee Salary and Expenses exceeding 75000](https://www.phsa.ca/about-site/Documents/FY2025-Employee-Salary-and-Expenses-exceeding-75000.pdf), linked from the [official financial index](https://www.phsa.ca/about/accountability/budget-financials). The original is 54,160,556 bytes, SHA256 `809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c`. Its 284 physical PDF pages have no native text. The standalone publication is unsigned and does not independently establish approval or adoption.

Rows use `[employerSlug, name, position, remuneration, expenses, pdfPage]`. Source titles are absent, so positions remain null. Names preserve published letters and word boundaries. Expenses may be paid directly to the employee or to third-party suppliers. The 5,810 explicit expense dashes remain null; this source has no explicit zero or negative expense rows. Expenses are never added to remuneration. Missing compensation components are not inferred as zero, and pay is not annualized. All rows remain under the printed PHSA reporting entity.

Physical pages 1–283 each contain 49 named rows; page 284 contains 39. An independent actual-PDF raster row-band audit verifies every page boundary. The final ruled Total is excluded from employee rows. The employee sums reconcile exactly to printed remuneration **$1,713,046,476** and expenses **$25,171,641**, with residuals $0/$0. The original prints no named employee count and no final-page below-threshold aggregate.

The complete source was read by Tesseract 5.5.0 and the independent PaddleOCR PP-OCRv4 networks through RapidOCR 1.4.4 / ONNX Runtime 1.31.1 CPU. Every engine disagreement or conservative confidence flag was frozen and independently resolved from original row images: 3,157 distinct rows across ten disjoint batches. All 18 image-verified first-page expense dashes established an exact recurring source-pixel template; detector absence does not establish a dash. Every source page, name/pay/expense region and row boundary was separately compared with an actual 300-dpi PDF render. This is geometric source-fidelity verification, not a claim that every agreeing field was manually transcribed.

A real shared-engine `Muir,lan` escape prompted a bounded 47-case additional name audit. Independent actual-PDF readers confirmed 44 exact name-only corrections and three legitimate lowercase names unchanged. Separate root-adopted amendment ledgers apply those exact names after the ordinary reviews. They preserve all amounts, nulls, titles, employer, page and row multiplicity; there is no generic capitalization rule.

The evidence directory contains all 284 compressed raw page outputs and complete row provenance. Provenance retains raw OCR text, boxes and confidence; each original candidate; dash pixels; every ordinary review input; and separate supplemental amendments. See `../held-resolution-2026-11-01/health/` for acquisition/model receipts, immutable batches, overlay ledgers, source controls, final peer closure, work queue and the candidate freeze. Original PDFs, images and optional research OCR models remain in `/tmp`, outside the application dependencies.

Rebuild and check from repository evidence, without OCR packages or network access:

```sh
python -m unittest discover -s scripts -p 'test_resolve_held_health.py' -v
python scripts/resolve_held_health_name_amendments.py --aggregate --check
python scripts/resolve_held_health_finalize.py --status verified --check
```

The source adds employee observations only. Existing same-period PHSA board schedules remain separate. No compiled rows are deleted or re-dated, and no cross-year identity claim is made. The nine earlier indexed employee scans and blocked VCH/Providence originals remain separate work-queue tasks.
