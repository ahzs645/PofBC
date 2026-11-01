# Health employee recovery checkpoint and board tranche

The useful import candidate is [recovery-health](../../recovery-health/README.md): four previously unprocessed Interior Health board originals, FY2014/15–FY2017/18, **43 rows**, with complete independent row extraction and rendered primary-schedule review. Employee gaps remain open.

PHSA's already downloaded FY2024/25 original contains 284 scanned pages and no native text. This pass independently transcribed every name, remuneration, expense and row boundary on **physical page 1**, producing a guarded 49-row staged fixture. It contains $6,258,067 remuneration, $88,815 disclosed expenses and 18 dash/null expense cells. Those are page sums, not cohort controls. Sixteen complete OCR rows differ from the image transcription, including punctuation/spacing and the shared Tesseract failure for Abia,Jo-Ann: the original expense is $771, while the existing OCR token is `™m`.

The compressed [staged evidence](phsa-2024-25-page-1-staged.json.gzip) retains all 49 manual rows alongside every raw OCR field and exact original/image/text hashes. The [staging receipt](employee-staging-receipt.json) records review scope and blockers. **No employee rows are proposed for import.** The remaining 283 source pages have not passed independent row verification. Two Tesseract modes remain one OCR engine; this checkpoint does not upgrade them into independent readers. The previously drafted request for the existing electronic schedule remains unsent.

Reproduce or replay this checkpoint:

```sh
python scripts/recover_wave_health_employee_staging.py --originals --check
python scripts/recover_wave_health_employee_staging.py --check
```

The original-backed check locks `/tmp/sector-health/phsa-2025.pdf`, the existing 144 dpi physical-page-1 PNG, and the prior raw Tesseract text. It does not claim to rerun a new independent OCR engine. To rerender, use PyMuPDF `Matrix(2,2)` on physical page 1; to reproduce the prior OCR use Tesseract 5.5.0, `-l eng --psm 6`. The staged transcript itself was read from the original image, and every raw mismatch stays visible.

Fresh bounded public-download checks for known official VCH `media/12116` and Providence `media/6981` again returned 403 HTML. An additional guessed VCH 2023 filename also returned 403 and **does not establish that the guessed report exists**. [employee-retrieval-receipts.json](employee-retrieval-receipts.json) hashes the actual response bodies, leaves source hashes null and preserves timestamps/statuses. No further broad archive discovery or exhaustive-absence claim is made. Existing ordinary-copy drafts remain the next acquisition route; no message, records request, FOI or fee was submitted.

The [action queue](work-queue.json) contains only the changed or directly exercised tasks and links old task IDs in its reasons. All other prior acquisition tasks remain unchanged. [handoff.json](handoff.json) freezes candidate counts, IDs, original/cache/data/evidence hashes, complete actual visual coverage and checks.
