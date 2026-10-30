# PofBC: source-gap recovery, 23 October 2026

> **Accepted 30 October 2026.** The original PDFs were downloaded from bchydro.com and match the
> recorded hashes; `scripts/check_chc_pdf.py` found every named row in both readers with nothing
> missing or extra; the summary columns were settled from page coordinates; and all 19 schedule
> pages were rendered and reviewed. The record is in [`pdf-verification/`](pdf-verification/review.json).
> The 723 rows for 2012/13–2016/17 are published as the accepted collection
> [`../columbia-hydro-constructors/`](../columbia-hydro-constructors/README.md), built by
> `scripts/verify-columbia-hydro-salaries.py`. A separate check made the same day, recorded here,
> produced byte-identical rows. 2017/18 names nobody and is shown as aggregate-only. The
> staging below is kept as the record of how the rows were captured; its "not accepted" statements
> describe the state on 23 October. The comparator files in `pdf-verification/` report
> `acceptedForPublication: false` because the comparator never accepts anything itself.

## Delivered result

**723 real employee-payment candidate rows** have been captured and parsed from Columbia Hydro Constructors Ltd. schedules embedded in BC Hydro's official Financial Information Act returns. The captures cover all named rows in the web-reader text for 2012/13–2016/17. The sixth period, 2017/18, has an aggregate-only employee schedule. It is not represented as an empty workforce.

**Accepted imports: 0. Published records added: 0. Nothing pushed, merged or deployed.** These candidates are deliberately outside the production collections. The original PDF byte-level and visual checks remain pending; the build is not allowed to infer that a successful arithmetic check is approval.

## Recovery and reconciliation

| Period | Named rows | Named remuneration | Named expenses | Remuneration residual | Expense residual |
|---|---:|---:|---:|---:|---:|
| 2012/13 | 190 | $19,718,574 | $1,089,407 | $+1 | $+0 |
| 2013/14 | 226 | $23,588,724 | $1,369,304 | $+3 | $-2 |
| 2014/15 | 239 | $25,533,054 | $1,370,304 | $-3 | $+2 |
| 2015/16 | 63 | $6,651,654 | $394,765 | $+3 | $-3 |
| 2016/17 | 5 | $485,097 | $30,673 | $-1 | $+1 |
| 2017/18 | 0 | $0 | $0 | $+0 | $+0 |

Residual means extracted named-row sum minus (overall aggregate minus below-threshold aggregate). Employer CPP/EI is a separate disclosure and was not put into employee rows or subtracted from this reconciliation. All residuals are left unchanged. The residuals fit a hypothetical whole-dollar independent-rounding bound, but this does not prove their cause. **The column assignment of summary values is still provisional pending rendered-PDF review.** No exact reconciliation is claimed for the five named-row years.

The named rows sum to **$75,977,103 remuneration and $4,254,453 expenses** across all five periods. These are source-defined payments, not annual salary rates, unique people, or a workforce census. Eighteen explicit zero-expense records remain zero; positions remain null. The source publishes initials, which are not expanded into invented given names.

There are two different `JW Anderson` rows in 2014/15, at $146,855 and $93,162 remuneration. Both remain. Neither shared initials nor the same name establishes identity; the parser does not merge them.

## What was actually read

The official publisher PDFs were accessible through web-reader text. All 19 physical schedule pages across six periods are represented in the capture metadata, including six summary pages. The row text was manually transferred from those web-reader results into attributed capture files and parsed locally. It is **not** a direct download of the original PDFs, a visual transcription, or two independent PDF-engine extractions. Page-boundary `Report ID` text appended to the last row by the web reader was separated from that row; names and amounts were not changed.

The `sourceTextLine` values are locators in the web reader's current text extraction, not official printed line numbers. `pdfPage` is a one-based physical PDF page. Each candidate carries its official URL and page link. Expected original-PDF hashes were copied from the earlier salary recovery's Hydro manifest; they were not recomputed from local PDF bytes in this pass.

Web screenshot attempts for all six source PDFs failed. Consequently, the last step needed before acceptance is explicit rather than silently waived. Primary sources:

- [2012/13 official PDF](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/openness-accountability/financial-information-act-return-march-31-2013.pdf) — physical schedule pages 172–175.
- [2013/14 official PDF](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/openness-accountability/financial-information-act-return-20140331.pdf) — physical schedule pages 163–167.
- [2014/15 official PDF](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/openness-accountability/financial-information-act-return-march-31-2015.pdf) — physical schedule pages 167–171.
- [2015/16 official PDF](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/openness-accountability/financial-information-act-return-march-31-2016.pdf) — physical schedule pages 169–170.
- [2016/17 official PDF](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/financial-reports/annual-reports/BC-Hydro-FIA-F17.pdf) — physical schedule pages 170–171.
- [2017/18 official PDF](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/financial-reports/annual-reports/bch-fia-f18.pdf) — physical schedule pages 175–175.

## Why this is a separate gap

The earlier Hydro source manifest explicitly listed `COLUMBIA HYDRO CONSTRUCTORS LTD.` under `otherEmployeeSchedulesNotImported`. This pass extracts that omitted sub-schedule; it does not append duplicates to BC Hydro, Powerex or Powertech. A relevant excerpt of the earlier manifest is included. The proposed employer slug is not yet mapped into PofBC's canonical employer/government model.

The 2017/18 schedule contains no named employee rows, with $208,410 remuneration and $12,021 expenses represented by the below-threshold aggregate. The candidate register gives it an **aggregate-only** state. It must not say no employees existed, show payroll as $0, or place the aggregate into a fake anonymous person record.

## Scan and health-report findings

A remote diagnostic run successfully obtained PHSA's 2024/25 PDF (54,160,556 bytes; 284 pages), Island Health's 2017/18 PDF (299,935 bytes; 99 pages), and BC Transit's 2011/12 PDF (2,398,260 bytes; 51 pages). No extractable text was returned from the inspected first and last pages of the PHSA and Transit PDFs. Island's inspected text was nonempty. This is boundary-page evidence, not an inspection of every page. PHSA and Transit hashes from that diagnostic are preserved in `scan-triage.json`.

A subsequent cloud execution request was declined. It was not retried. The remote originals could not be transferred into the local parser; no subsequent OCR or full-source health extraction was completed. Local network downloads also failed. The original PDFs are not bundled here.

BC Transit 2012/13 and 2013/14 reports were also located and opened in the web reader (48 and 49 pages respectively), but yielded no parsed text. Their links are saved for a scoped employee-table OCR pass. The 20 PHSA/Island source definitions have been carried forward with per-source statuses; they have not all been re-downloaded or certified.

## Code and validation

`stage_chc_recovery.py` parses the attributed capture files, validates source/year headers, page sequences, strict whole-dollar monetary syntax and disclosure thresholds, and emits CSV, JSON, deterministic gzip, and reconciliation reports. It preserves repeated rows and has no publication command. It rejects unknown rows rather than guessing amounts or dropping them.

`check_chc_pdf.py` is the next-step local-PDF comparator. It checks the original PDF hash, reads selected pages through PyMuPDF and Poppler, reconstructs two side-by-side table blocks, and compares exact row multisets with the candidates. Both readers share the reconstruction code. This helper has unit-tested reconstruction logic but **has not been executed against an original CHC PDF in this pass**. Even a successful comparison leaves visual and aggregate-column review pending.

Thirty tests passed. They include assertions over these real source-text captures, negative/malformed-input cases, duplicate/zero handling, and two byte-identical builds of all 26 candidate output files. A second right-split parsing path independently reconciled every exported CSV tuple with the captures. Those are transformation checks, not independent verification of original PDF glyphs. The complete PofBC build and browser interface were not tested.

## Next acceptance steps

Obtain the six original PDFs using the saved official URLs, run the local comparator for each, render and inspect the 19 schedule pages, settle aggregate columns and any flagged names/amounts, and approve the separate CHC employer mapping. Then use the existing reviewed normalized-source/collection workflow and rerun employer/person/atlas reconciliation. Do not register these staging JSON files as accepted inputs directly.

The next large source task remains PHSA/Island Health. The original PHSA 2024/25 scan and Island Health reports uploaded as conversation attachments would permit local full-PDF/OCR processing without repeating the blocked cloud-execution path.
