# Municipal OCR recovery

Follow-up to merged PR #23, reviewed 31 October 2026. The accepted recovery adds
**566 observations: 468 employees and 98 elected officials**, in 30 page/cohort
files from 15 original reports and seven municipalities. Originals and all accepted
OCR passes were reproduced again before publication; no cell is changed to force
agreement with a control.

| Municipality | Calendar years | Employees | Council |
|---|---|---:|---:|
| Terrace | Every year 2017–2025 | 435 | 69 |
| Clinton | 2024 | 3 | 5 |
| Logan Lake | 2025 | 16 | 7 |
| Telkwa | 2023 | 5 | 5 |
| Salmo | 2024 | 2 | 5 |
| Fruitvale | 2023 | 7 | Not imported |
| Creston | 2024 | Held | 7 |
| **Total** | | **468** | **98** |

## What was processed

The broader scan/layout queue contains **98 official reports and 3,518 physical
pages**. All originals were retrieved and fingerprinted. Initial text checks found
52 reports with essentially no usable text, 20 with mixed text/images and 26 with
existing text requiring layout work. Every page received discovery screening using
its embedded text or 110-dpi OCR; 1,035 keyword candidate pages received 250-dpi
PSM 6 and 300-dpi PSM 3 OCR. There were **zero processing errors**.

The retained candidate pages include incidental financial notes, checklists and
supplier schedules. They are **not 1,035 accepted salary pages**. Keyword discovery
can miss a table: page discovery completion is not proof of exhaustive salary-table
identification. The 83 reports without accepted cohorts still need source-specific
row, period, scope and control review. Fifteen reports have reviewed imports;
Creston's acceptance covers council only.

- [Complete original fingerprints and text availability](originals.json)
- [Every report, candidate page and processing receipt](ocr-register.json)
- `staging/*.json.gzip`: discovery text and both detailed OCR text/TSV outputs,
  fingerprinted per report. These files are candidate evidence, outside the salary build.
- [Accepted layout/field decisions](reviewed-layouts.json), [accepted source manifest](sources.json)
  and `evidence/`: exact rendered-page bounds, original fingerprints, both OCR word
  representations, literal corrections, named counts and fixed controls.
- [Specific additional requests](additional-requests.json) and the
  [combined acquisition spreadsheet](../municipal-audit/follow-up.csv).

## Acceptance and source differences

Every accepted rendered table was visually checked. Two Tesseract passes are
different readings of the same image using the **same OCR engine**; they are not
independent originals. Their agreement complements complete visual review and
monetary controls. A fixed correction records its reader, row, field, observed
input and reviewed output. If that input changes, reproduction stops.

The review corrected omitted/misread title numerals, a dollar sign read as a
leading 5 in Logan Lake's $991.05 expense cell, and source-specific name/punctuation
errors. A visibly clipped Terrace 2020 title remains truncated rather than being
expanded from another year. Terrace's 2025 published ID column stays in evidence;
its OCR spellings are not verified identifiers, not imported, and not used to join
people. All imported names, titles and monetary columns must agree after the
explicit visual corrections. Blank expenses remain missing; numeric zero stays zero.

Terrace uses **Total Earnings** as remuneration, with wages and taxable benefits/
other compensation retained separately. Its expense-inclusive **Total** is never
used as remuneration. Early council tax splits are components of remuneration,
not amounts to add to it a second time.

These observed issuer differences remain disclosed:

- **Terrace 2022 employees:** remuneration and expenses reconcile exactly. The
  printed expense-inclusive grand total is $582,015.69 below the sum of its
  individual cells. The app uses the separate remuneration column and shows a warning.
- **Terrace 2018 council:** tax-exempt components sum $0.02 above their control and
  taxable components $0.02 below. Remuneration, expenses and combined totals are exact.
- **Clinton 2024 council:** remuneration rows total $2 above the printed subtotal.
- **Salmo 2024 employees:** remuneration rows total $1 below their printed subtotal.
- **Creston 2024 council:** expense rows total $1 above the printed subtotal.

The material published-value qualifications appear on employer/person pages.
Rounding is not asserted as an explanation and nobody's amount is adjusted.

**Creston's 27 employee candidates remain held.** Remaining glyph ambiguities and
candidate remuneration/expense sums have not established a validated transcription
or a proved issuer discrepancy. Request the existing spreadsheet or a clearer
original, then recheck all fields. Do not choose a digit to make the totals agree.
New Hazelton's conflicting schedule/attachment year likewise remains a period
review, despite completed OCR. No municipal messages or requests were sent.

## Reproduce

Accepted OCR uses Tesseract **5.5.0**, PyMuPDF and grayscale page rendering. Normal
builds and CI are offline and read only registered, hash-checked normalized files.

```bash
# All accepted records, retained word evidence, controls and normalized hashes:
python3 scripts/parse_municipal_ocr.py --check-data
python3 scripts/test_municipal_ocr.py

# Re-fetch missing pinned originals and reproduce every accepted OCR word:
python3 scripts/parse_municipal_ocr.py --cache /tmp/pofbc-ocr --fetch --verify-ocr

# Re-run the complete 98-report discovery/candidate batch and archive receipts:
python3 scripts/ocr_municipal_sources.py --cache /tmp/pofbc-ocr --fetch --workers 4

# Rebuild the app and the current acquisition list:
npm run compare:municipal-periods
npm run build:salaries
npm run check:salaries
npm run audit:municipal-salaries
npm run follow-up:municipal-salaries
```

Re-running candidate OCR does not authorize new salary imports. A new acceptance
requires reviewed layouts, complete table review, literal cell corrections and
fixed control evidence. The full app now contains **881,002 records**, including
**631,091 official-source observations** from 336 accepted page/cohort files.
There are **54 municipal jurisdictions with official records**, 53 with employee
schedules and Creston with council only; 107 current jurisdictions still lack
accepted official records.
