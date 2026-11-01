# Island and coast municipal disclosures

This collection adds **219 official observations across seven previously uncovered municipalities**: **179 employee observations** and **40 elected-official observations**. Six original reports cover calendar **2025**; Sayward's scanned report covers calendar **2024**. Employee and council cohorts remain separate. No compiled records are deleted or relabelled.

Reviewed 31 October 2026 America/Vancouver, against the municipal pass baseline `5e5fe01` and 917,420 records.

| Municipality | Year | Employee rows | Council rows | Physical employee / council pages | Official original |
| --- | --- | ---: | ---: | --- | --- |
| Courtenay | 2025 | 99 | 7 | 33–35 / 32 | [SOFI](https://www.courtenay.ca/media/file/2025-statement-financial-information) |
| Cumberland | 2025 | 22 | 5 | 32 / 32 | [SOFI](https://cumberland.ca/wp-content/uploads/2026/06/2025-SOFI.pdf) |
| Gibsons | 2025 | 24 | 5 | 10 / 9 | [SOFI](https://gibsons.ca/wp-content/uploads/2026/07/2025-Statement-of-Financial-Information.pdf) |
| Gold River | 2025 | 5 | 5 | 5 / 5 | [SOFI](https://goldriver.ca/wp-content/uploads/2026/09/2025-SOFI.pdf) |
| Tahsis | 2025 | 8 | 5 | 28 / 28 | [SOFI](https://villageoftahsis.com/wp-content/uploads/2026/06/2025-SOFI-Signed-copy.pdf) |
| Ucluelet | 2025 | 19 | 6 | 30 / 29 | [SOFI](https://ucluelet.ca/wp-content/uploads/2026/10/2025-Statement-of-Financial-Information.pdf) |
| Sayward | 2024 | 2 | 7 | 3 / 3 | [signed SOFI](https://www.sayward.ca/sites/sayward.ca/files/2026-05/2024%20SOFI%20Package%20-%20signed.pdf) |
| Total | | **179** | **40** | | |

Original PDF hashes, normalized/compressed data hashes, actual periods, source index URLs, page provenance, controls and visible warnings are in [sources.json](sources.json). Monetary fields use the source's remuneration and expense columns. Under-threshold aggregates, suppliers, insurance cover amounts and financial-statement totals are not individual salary records. Payments are not base salary rates or complete workforce rosters.

## Extraction and review

[`scripts/import_wave_island.py`](../../../scripts/import_wave_island.py) independently reconstructs all **210 native-text observations** using PyMuPDF positioned words and Poppler layout text. Names, positions, remuneration, expenses, page and row order agree. Both engines read the source controls. All accepted schedule pages were visually inspected, including each Courtenay page boundary, wrapped Cumberland titles, source threshold exceptions and all first/final rows. Approval pages were also rendered and reviewed.

One native-text discrepancy required a guarded image correction: **Wyka, R., Courtenay page 35** has a title visibly clipped at `Manager of Financial Planning, Payroll & Business Perform`. Poppler exposes hidden `Performance` glyphs beyond the visible cell. The accepted title follows the rendered source and PyMuPDF; the full title is not inferred. Both raw readings and the exact correction context remain in supporting evidence.

Blank and dash expenses remain `null`. Explicit zero and negative values retain their source meaning. Gibsons' additional **Total** column includes expenses; it is retained in evidence and never imported as remuneration. Positions remain exactly as disclosed, including abbreviations, clipped text and Tahsis' missing title for John Manson. No cross-year identity inference expands initials or assigns job titles.

Approval evidence:

| Municipality | Approval page | Date / representation |
| --- | ---: | --- |
| Courtenay | 45 | Visible signatures, 24 June 2026 |
| Cumberland | 38 | Published signature notation, 25 May 2026 |
| Gibsons | 1 | Approved council resolution R2026-130, 2 June 2026; visible certification and finance signatures |
| Gold River | 2 | Published `Signed` notation for mayor and CAO; date cells blank |
| Tahsis | 31 | Visible signatures, 2 June 2026 |
| Ucluelet | 3 | Visible signatures, 5 October 2026 |
| Sayward | 7 | Visible CFO/mayor signatures, 6 May 2025 |

## Source limitations retained visibly

The following are row sums minus their relevant source controls. No cell is changed to force agreement, and no rounding cause is assumed.

| Municipality and cohort | Pay residual | Expense residual | Control basis |
| --- | ---: | ---: | --- |
| Courtenay employees | $0 | +$1 | Printed named subtotal |
| Courtenay council | −$3 | +$1 | Printed council subtotal |
| Cumberland employees | $0 | +$1 | Printed all-employee total less printed below-threshold aggregate |
| Gold River employees | +$1 | $0 | Printed all-employee total less printed below-threshold aggregate |
| Gold River council | +$1 | $0 | Printed council subtotal |
| Tahsis employees | −$1 | Not separately controlled | Printed all-employee pay less below-threshold pay; no separate named-expense or below-threshold expense subtotal |
| Ucluelet employees | $0 | +$0.01 | Printed named subtotal, cents preserved |
| Sayward council | $0 | −$1 | Printed council subtotal |

The other accepted cohorts reconcile exactly to their named controls. Each affected source carries a `publicWarning` with its exact discrepancy and unresolved cause. Derived named controls are explicitly distinguished from directly printed named subtotals. Tahsis' named numeric expenses equal the reported all-employee expense total, but its missing below-threshold expense aggregate is not treated as zero.

**Threshold exceptions:** Gibsons discloses Jaswal, Tamara at $74,572 remuneration and $3,252 expenses despite its `Above $75,000` heading. Tahsis discloses Adia Mavrikos ($73,621), Paige Sawyer ($73,633) and Kyle Wilkinson ($72,620) under its `Remuneration over $75,000` heading. Their separate expenses place combined amounts above the threshold, but the source does not establish that as its selection rule. All published named rows are retained and the ambiguity is warned. Cumberland's under-threshold label mentions remuneration **and expenses**; the exact rule is not inferred, and all 22 named remuneration amounts independently exceed $75,000.

## Sayward OCR acceptance

Sayward's eight-page original is entirely scanned. The schedule is physical page 3. Its internally printed **2024** period and visible May 2025 approval take precedence over its 2026 upload directory.

[review/sayward-2024-ocr.json](review/sayward-2024-ocr.json) preserves raw Tesseract 5.5.0 readings at **250 dpi / mode 6** and **300 dpi / mode 3**, their hashes, five guarded image-grounded repairs, and a separate complete manual transcription. The two OCR settings share one engine and are **not independent OCR engines**. All nine names, titles and amounts were independently checked against the complete rendered table by a second reviewer; see the [independent review](../municipal-next-pass/reviews/sayward-ocr.md).

The mode-6 pass omitted small expense cells or read table borders as characters. The mode-3 pass reads all nine rows correctly. Image review establishes each guarded repair, including **77** expenses for Gervais, Keir and explicit **0** expenses for Gilkin, Kohen and Tinsley, Tom. Both corrected readings reproduce the complete manual transcription. Employees reconcile to **$177,668 remuneration / $1,316 expenses**. Council expenses sum to **$16,876** versus the printed **$16,877**; the accepted source retains that unresolved $1 difference.

## Reproduce

Requires Python 3, PyMuPDF and Poppler. Original PDFs are cached under `/tmp/pofbc-wave-island/` and are not committed.

```sh
python scripts/import_wave_island.py --download
python scripts/import_wave_island.py --verify
python -m unittest discover -s scripts -p test_wave_island.py
```

Use `--output /tmp/island-review` to reproduce the complete collection in isolation, or `--inspect` to validate candidates without writing accepted inputs. All outputs are prepared after all source checks pass; gzip output is deterministic. OCR reproduction uses the saved, hashed, reviewed raw readings rather than assuming new OCR software emits identical text. A fresh OCR run or changed source bytes needs another review.

Ten CI-discoverable regressions cover missing/zero/negative/cents distinctions, wrapped-title continuations, expense-inclusive totals, below-threshold source exceptions, clipped-title correction guards, all final employee titles, every Courtenay page boundary, the cent residual, OCR zero/residual preservation, and cohort/period separation.
