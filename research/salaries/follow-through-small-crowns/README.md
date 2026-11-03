# Official employee schedules reconstructed on 2026-11-02

All **14 assigned reports** have accepted complete employee cohorts: **4,255 observations** across three distinct employers. These records were reconstructed from the official originals; the supplied discovery list was used only for URLs, expected PDF fingerprints and report assignment. No earlier unsaved normalized rows were used.

| Employer | Disclosure | Employee rows | Named pay / expense residual¹ |
| --- | --- | ---: | ---: |
| BC Financial Services Authority | 2019/20 | 6 | 0 / +1² |
| BC Financial Services Authority | 2020/21 | 112 | −3 / −3 |
| BC Financial Services Authority | 2021/22 | 161 | 0 / 0 |
| BC Financial Services Authority | 2022/23 | 237 | 0 / 0 |
| BC Financial Services Authority | 2023/24 | 257 | 0 / 0 |
| BC Financial Services Authority | 2024/25 | 286 | 0 / 0 |
| BC Financial Services Authority | 2025/26 | 307 | 0 / 0 |
| BC Infrastructure Benefits Inc. | 2019/20 | 13 | 0 / 0 |
| BC Infrastructure Benefits Inc. | 2020/21 | 28 | +1 / +1 |
| BC Infrastructure Benefits Inc. | 2021/22 | 185 | +6 / +2 |
| BC Infrastructure Benefits Inc. | 2022/23 | 558 | +2 / +2 |
| BC Infrastructure Benefits Inc. | 2023/24 | 805 | +3 / +3 |
| BC Infrastructure Benefits Inc. | 2024/25 | 1,122 | 0 / 0 |
| B.C. Pavilion Corporation | 2024/25 | 178 | +6 / +2 |

¹ CAD whole dollars: sum of every published named row minus printed total employees less printed below-threshold employees. Seven reports carry public qualifications. Every row amount is unchanged; the causes of small printed-source differences are unknown. They are not labelled rounding errors.

² BCFSA 2019/20 also prints a direct named subtotal. Named remuneration is $539,126, $1 below its printed direct subtotal of $539,127. Named expenses are $82,978, equal to the direct subtotal but $1 above the amount implied by total employees less below-threshold employees. Both independent control comparisons survive in the receipt.

BCFSA's first report explicitly covers **November 1, 2019 (commencement of operations) through March 31, 2020**. It is a partial fiscal period. Every subsequent assigned source covers the year ended March 31 of the indicated end year, with April 1 start dates.

## What is retained

`sources.json` is a standard source manifest. Each deterministic gzip contains exactly six fields per observation:

```text
[employerSlug, name, position|null, remuneration, expenses|null, physicalPdfPage]
```

The remuneration column keeps the publisher's definition. BCIB explicitly includes base salary and other compensation, with travel or living-out expenses described separately. BCFSA and PavCo's table labels are retained without interpreting remuneration as base salary. BCFSA's regular-salary definition of “Compensation” belongs to the severance statement and is not substituted for employee remuneration. Source definitions and reconciliation context remain in the evidence.

Only PavCo publishes employee positions. No positions or expanded given names are inferred elsewhere. Source names and repeated names remain distinct observations; comma spacing is normalized. Numeric zero expenses remain zero, and dashes or blank cells remain null. BCFSA 2020/21 prints three zero expense cells and two negative adjustments: Courtney Drury −$298 and David Sherwood −$822. All are preserved.

BCIB's legal employer remains separate from the other employers. Its employee schedules include the workforce named by the report. The 2024/25 source marks **1,066** named employees with an asterisk identifying unionized skilled trades workers on selected provincial infrastructure projects; **56** named employees are unmarked. The receipt retains the marked row indexes and the source definition. Asterisks are removed from normalized names. No individual corporate/project category is inferred in earlier reports or for unmarked staff. The earlier aggregate “95%” statement is preserved as context only.

Board/director schedules, suppliers, totals, below-threshold aggregates, unnamed records, and financial-statement reconciliation items are excluded. Separate board schedules remain unaccepted scopes in `dispositions.json`; this collection makes no board-cohort claim. Existing compiled partitions are explicitly retained.

## Evidence and reconstruction

All 14 PDF byte counts, page counts and SHA-256 hashes match the assigned originals. All 14 PDF links were found again in the three official report indexes. `evidence/duplicate-check.json` records the check of other source manifests for assigned employer slugs or original hashes; none matched.

The 13 native employee schedules have **4,143** rows. Each row was independently reconstructed using PyMuPDF positioned words and Poppler layout text. Every name, position, monetary cell and physical page agrees as a complete multiset. Retained `.words.json.gzip` and `.layout.txt` files allow tests to replay both readers without downloading PDFs. Printed controls were located in both readers and reviewed in original pixels. Ambiguous layout/glyph cases were also rendered. The encoded lowercase `l` in `Bandila, l` is retained, with inspected source crops.

BCFSA 2020/21 is an original scan with **112** named employee rows on physical pages 7–10. Full-page Tesseract automatic-layout OCR was compared with separate name, remuneration and expense column OCR. The second pass removes detected table rules before segmentation. Every employee source row and the printed controls were additionally read in the unmodified source pixels. One column pass read the comma in `83,616` as a period; the original source and independent full-page pass establish the comma. Whitespace in `108 ,444` was also normalized. The reviewed OCR snapshots, precise decisions, source row pixel rectangles, explicit zeros, negative adjustments and complete control arithmetic are retained under `evidence/ocr*` and `evidence/bcfsa-2020-21.rows.json.gzip`.

Each report has a receipt at `evidence/<report>.json` containing original fingerprints, covered dates, complete per-page row/monetary counts, independent-reader agreement, the literal printed controls, direct and implied residuals, null/zero/negative expense counts, excluded scopes, public warnings, and hashes of its supporting evidence. The `.controls.png` images are original-PDF crops of the printed employee controls. PDF originals and full-resolution renderings remain in the external cache rather than the repository.

Run from the repository root:

```sh
python scripts/follow_through_small_crowns.py --cache /workspace/salary-source-follow-through/cache-small-crowns
python -m unittest discover -s scripts -p 'test_follow_through_small_crowns*.py' -v
```

Missing originals are fetched from the recorded public URLs and must match the recorded hashes before extraction. Native readers require PyMuPDF and `pdftotext`. Add `--refresh-ocr` to independently regenerate the reviewed scan passes; it additionally requires Tesseract, Pillow and NumPy. OCR subprocesses run sequentially with `OMP_THREAD_LIMIT=1` and `OMP_NUM_THREADS=1`. Regeneration must match the retained OCR snapshots; changed OCR requires source-pixel review before replacing evidence.

The 11 regression tests cover all source-backed reader replays, employee boundaries, the tightly spaced BCIB two-column layout, PavCo's first row and positions, null/zero/negative expenses, repeated names, source cohort markers, partial-period dates, immutable printed residuals, fingerprints, deterministic payloads, and every final disposition.
