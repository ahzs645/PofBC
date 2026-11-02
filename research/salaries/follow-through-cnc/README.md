# College of New Caledonia: seven original employee schedules

Reviewed 2 November 2026. This reconstruction accepts **1,895 employee observations** from all seven official SOFIs for **2018/19–2024/25**. Each period follows the original schedule heading, from 1 April through 31 March. The normalized rows retain the original physical PDF page, displayed names and displayed monetary cells.

| Original period | Employee rows | Physical PDF pages | Displayed remuneration | Numeric disclosed expenses | Pay residual | Expense residual |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| 2018/19 | 205 | 3–7 | 18,764,318 | 904,392 | -5 | -1 |
| 2019/20 | 236 | 2–6 | 21,952,824 | 702,019 | +13 | +3 |
| 2020/21 | 258 | 3–7 | 25,302,809 | 184,800 | -24 | +1 |
| 2021/22 | 268 | 3–7 | 26,633,524 | 171,414 | -44 | 0 |
| 2022/23 | 278 | 3–7 | 27,591,196 | 362,719 | -10 | +2 |
| 2023/24 | 312 | 3–7 | 34,077,874 | 524,866 | -5 | +11 |
| 2024/25 | 338 | 2–8 | 36,413,531 | 550,459 | -27 | +1 |
| **Total** | **1,895** | | **190,736,076** | **3,400,669** | | |

Amounts are CAD. Residuals are displayed named-row sums minus the printed named-employee subtotal. Each row was checked against original rendered pixels. The displayed cells remain unchanged where their sums differ from printed controls. [Reviewed controls](reviewed-controls.json) retain the original named, below-threshold, employee, board and reconciliation totals; [extraction evidence](extraction-evidence.json) computes their separate arithmetic discrepancies.

The reports define remuneration to include salary, wages, bonuses, gratuities, taxable benefits, payments into trust and income deferrals paid to or on behalf of the employee during the fiscal year, excluding amounts payable under a severance agreement. Expenses include amounts paid on College purchasing cards on employees' behalf. The employee schedules publish no positions, so every position remains null. The separately printed Board of Governors, suppliers and aggregate/reconciliation lines are outside this employee import. All seven board cohorts remain available for a separately scoped review.

The original named subtotal is labelled “remuneration over $75,000.” Some individual displayed remuneration cells fall below that figure, including Esau, Darrell at $48,128 remuneration and $32,353 expenses in 2024/25. Every displayed named employee row is retained. The manifest records a source-labelled threshold with no inferred numeric comparison; it does not filter rows by remuneration alone.

## Original acquisition and period evidence

[Download receipts](download-receipts.json) confirm that all seven PDFs match the exact SHA-256 fingerprints in the supplied [discovery inventory](source-discovery.json). Each accepted employee page prints the actual April–March period. CNC's [current official index](https://cnc.bc.ca/about/initiatives/budget) links the six reports from 2019/20 onward. Its older 2018/19 link is no longer present there; the supplied official CNC PDF URL remains accessible and matches its original fingerprint.

The accepted [manifest](sources.json) contains the official URLs, original hashes and byte lengths, actual periods, normalized gzip hashes, complete page counts, missing-cell counts, source-definition notes and residuals. [Dispositions](dispositions.json) provide a concrete outcome for every one of the seven discovery IDs. Existing compiled observations are retained; this collection makes no blanket replacement, relabelling or identity decision.

## Reading and visual review

Six originals are image-only scans. Each employee page was rendered losslessly at 300 dpi and read separately with Tesseract 5.5.0 in page-segmentation modes 4 and 6. Those are separate layout readings of **one OCR engine**, with correlated recognition errors; they are not claimed as independent OCR engines. Full visual reading of all employee rows and controls supplied the additional check. [Visual receipts](visual-review.json) identify every reviewed page and the original/render fingerprints. The retained compressed TSVs preserve both complete OCR inputs.

The parser follows source column geometry and adjusts the surname/first-name boundary for the visibly skewed scans. It preserves source order and refuses malformed monetary cells. [Reviewed corrections](reviewed-corrections.json) contain 53 exact candidate replacements or restored rows, each with its original candidate, displayed value, reason, physical page and fingerprinted original-PDF crop. Examples include OCR reading a leading 1 as 4, interpreting a dash as `z`, `~` or punctuation, and splitting `97,341` into two tokens. Corrections follow visible cells. The independent-layout comparison explicitly lists omitted rows requiring visual completion and reports no unresolved disagreements.

The 2020/21 native document was independently read with PyMuPDF word rectangles and Poppler bbox words, then compared with both rendered-page OCR readings. All 258 monetary rows and their order agree. Exactly three encoded Poppler surnames extend beyond the visible column boundary. [Native clipping receipts](native-clipping-review.json) retain the visible names `Chambers-Richard, Tamara`, `de la Pena Gonzal, Rafael` and `Montgomery-Hewe, Chris`; longer hidden strings remain extraction evidence only. This independently reproduces the supplied README's 258 rows, $25,302,809 remuneration, $184,800 expenses, 138 dashes and -$24/+ $1 named-subtotal residuals.

| Period | Dash expense cells | Blank expense cells | Explicit numeric zero cells |
| --- | ---: | ---: | ---: |
| 2018/19 | 40 | 0 | 0 |
| 2019/20 | 48 | 0 | 0 |
| 2020/21 | 138 | 0 | 0 |
| 2021/22 | 120 | 14 | 0 |
| 2022/23 | 119 | 0 | 0 |
| 2023/24 | 114 | 0 | 0 |
| 2024/25 | 136 | 0 | 0 |

Both blank and dash expenses normalize to null; the row-level evidence preserves their distinct source states. The 14 blank 2021/22 expense cells are individually identified. In 2024/25, the first-name cell beside `Ramandeep` is visibly blank; the accepted name is the single published name `Ramandeep`, with no invented first name. The employee files contain no explicit zero expense cells.

## Reproduction

The live salary build consumes the reviewed deterministic gzip files without downloading PDFs or running OCR. Rebuild and validate this collection from its retained reader evidence:

```sh
python scripts/follow_through_cnc.py --build
python scripts/follow_through_cnc.py --check
python -m unittest discover -s scripts -p 'test_follow_through_cnc.py' -v
```

Re-extract all originals using `curl`, PyMuPDF, Poppler `pdftotext` and Tesseract 5.5.0:

```sh
python scripts/follow_through_cnc.py --cache /tmp/cnc-originals --extract --check
```

The extraction command verifies original fingerprints, renders only the accepted employee pages, runs one OCR child at a time with `OMP_THREAD_LIMIT=1` and `OMP_NUM_THREADS=1`, and compares both resulting row readings with the reviewed fixtures. Native PyMuPDF/Poppler rows must also reproduce the retained evidence. A changed original, altered row or changed reader result fails explicitly; no new OCR result automatically changes published observations.

All 18 focused tests and the original-source replay pass. Tests cover malformed OCR cells, missing versus zero expenses, source order, physical-page completeness, exact correction witnesses, clipped versus hidden names, the original 2020/21 controls, the single-name disclosure, threshold exceptions, exposed OCR omissions, deterministic gzip output and crop fingerprints.
