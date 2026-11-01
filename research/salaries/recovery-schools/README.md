# School SOFI recovery, November 1, 2026

This bounded tranche contains three previously unaccepted FY2024/25 original district SOFIs, six separate employee/trustee cohorts and 234 observations. It is staged for independent review and root integration; the global collection registry has not been edited.

| District | Original physical schedule pages | Employee rows | Trustee rows | Literal control qualifications |
|---|---:|---:|---:|---|
| 19, Revelstoke | 50–51 | 77 | 5 | Employee expense rows total $150,762; printed employee expense control is $148,744, a $2,018 difference. |
| 49, Central Coast | 53 | 30 | 5 | Trustee remuneration rows total $63,095; printed trustee control is $63,096, a $1 difference. |
| 64, Gulf Islands | 52–54 | 110 | 7 | Trustee remuneration rows total $126,052; printed trustee control is $126,054, a $2 difference. |

All other named-schedule component controls reconcile exactly. Each discrepancy has its own exact `publicWarning` and clarification action. No row or published control was changed to balance, and no cause is inferred. Complete employee schedules remain complete despite separate trustee qualifications. Aggregate payroll below the disclosure threshold, supplier payments, CPP/EI employer premiums and other financial totals are excluded.

Each original schedule explicitly says year ended June 30, 2025. The fiscal period is July 1, 2024 through June 30, 2025. Remuneration and expenses remain separate reported payments rather than annual base salary rates. Source names, titles, initials, punctuation and unusual capitalization are preserved. Central Coast publishes no positions; those fields are null. Blank and dash expenses are null, and explicit zeros remain zero.

The three district originals are hosted by the Ministry as convenience copies. Approval declarations are visually checked on SD19 p2, SD49 p3 and SD64 p3. The SD19 and SD49 date fields read December 19, 2025 and November 19, 2025 respectively, with signatures redacted. SD64 has a June 30, 2025 declaration, redacted signature area and blank adjacent date fields. No signature or adoption date is inferred from redacted areas.

Gulf Islands has true native schedule text. Independent readers use Poppler lexical role delimiters and MuPDF baseline grouping with fixed geometric columns. Every name, title, remuneration, expense, page, row order and multiplicity agrees across all 117 rows. All three rendered schedule pages were reviewed for headings, scope, columns and controls; row-level native comparison covers every field.

Revelstoke is a scanned report with an OCR overlay, despite its substantial extracted text. Central Coast's schedule is also scanned. The worker fully transcribed every rendered row and compared it to the original OCR overlay or fresh Tesseract PSM6, retaining the raw machine text and explicit image-verified corrections. This is not described as two independent native readers. An independent peer subsequently transcribed the complete original image pages before opening either frozen candidate and confirmed all 117 scan rows and fields; the peer also independently transcribed Gulf Islands' seven trustee rows and its discrepant control. These hash-pinned receipts are linked in each relevant source's validation and the research handoff. No full independent manual review of Gulf Islands employees is claimed; all 110 rows agree between the two native readers. The literal source title `Speech language Patholoigist` and name capitalization `Jeremy WEddell` are intentionally preserved.

The six-field gzip schema is `[employerSlug, name, position, remuneration, expenses, pdfPage]`. Each source has its own original, normalized-data and compressed-evidence SHA256. Evidence contains complete rows, independent rows, row-level native words or OCR source lines, raw OCR text, explicit corrections, manual transcript hashes, printed controls and rendered image hashes. Originals and images stay under `/tmp`; no PDFs or images are committed.

Reproduce from committed evidence without network, PDF or OCR dependencies:

```sh
python3 scripts/recover_wave_schools.py
python3 -m unittest discover -s scripts -p 'test_recover_wave_schools.py'
```

Replay against pinned originals under `/tmp/pofbc-schools` with Poppler and PyMuPDF; rerun fresh Central Coast OCR with Tesseract:

```sh
python3 scripts/recover_wave_schools.py --originals --rerun-ocr
```

`--build` reconstructs the candidate manifest and evidence from the pinned originals and committed manual transcripts. Do not use it to mutate a hash-frozen review release. No district contact, request, fee, FOI submission, branch change, commit, push or publication occurred in this worker tranche.

See [the recovery research handoff](../recovery-wave-2026-11-01/schools/README.md) for the exact remaining review pages, unresolved Arrow Lakes declaration conflict, source receipts, existing-task reconciliation and action queue. These three districts have no compiled employer partitions in the frozen sixty-district inventory, and no previously registered original shares their period/scope. No compiled replacement or alias correction is proposed.
