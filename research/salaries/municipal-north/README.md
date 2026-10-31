# Northern and Interior municipal salary expansion

Reviewed 31 October 2026. This collection adds **8,806 named disclosure rows from 24 original PDFs**, separated into **30 employee or elected-official cohorts across 11 municipalities**. It also records official archives and unresolved sources for all 19 municipalities assigned to this research group.

These are calendar-year remuneration disclosures, not base-salary estimates, a complete workforce census, or verified unique-person identities. Names, initials, positions, negative adjustments, and missing expense cells remain as the source publishes them. The same individual can appear in several years.

## Accepted coverage

| Municipality | Calendar years added here | Employee rows | Elected-official rows |
| --- | --- | ---: | ---: |
| Castlegar | 2025 | 57 | 7 |
| Cranbrook | 2025 | 123 | 7 |
| Fort St. John | 2025 | 180 | 7 |
| Kamloops | 2016–2023, 2025 | 3,517 | 0 |
| Kelowna | 2019, 2021–2025 | 3,848 | 0 |
| Nelson | 2025 | 128 | 7 |
| Penticton | 2025 | 250 | 8 |
| Prince George | 2023 | 404 | 9 |
| Prince Rupert | 2025 | 133 | 0 |
| Quesnel | 2025 | 78 | 0 |
| Smithers | 2025 | 43 | 0 |
| **Total** | | **8,761** | **45** |

Zero elected-official rows means that cohort has not been imported here, not that the report has no council disclosure. Those outstanding cohorts are explicitly listed in `sources.json` under `unparsedSources`. Other Prince George years remain in the existing `prince-george` collection.

## What remuneration means in each source

| Source | Normalized remuneration | Other columns retained in the audit |
| --- | --- | --- |
| Prince George 2023 employees | Base pay plus all other compensation | Both components and expenses |
| Prince George 2023 council | Published remuneration, including vehicle allowance once | Taxable non-expense portion, vehicle allowance, printed remuneration, expenses, benefits |
| Fort St. John 2025 | Published remuneration | Expenses and remuneration-plus-expenses total |
| Kamloops | Published **Remuneration** column | For 2017–2023, taxable benefits/payouts and Total Income; for 2025, taxable benefits; expenses separately |
| Kelowna through 2023 | Published remuneration | Expenses |
| Kelowna 2024–2025 | Published **Total Remuneration** | Normal-operations and EOC-deployment remuneration, with expenses separately |
| Penticton 2025 | Published remuneration | Expenses and remuneration-plus-expenses total |
| Cranbrook 2025 | Published total remuneration, including taxable benefits | Expenses; separate employer-share benefit aggregates are excluded from individual rows |
| Nelson 2025 | Published remuneration | Expenses |
| Castlegar 2025 | Published 2025 Payroll | Expenses; the source includes wages, overtime, accrued-time payouts, retroactive adjustments, allowances and taxable benefits in remuneration |
| Prince Rupert 2025 | Published **Total Remuneration** | Remuneration/taxable benefits, other remuneration, expenses; the source says other remuneration includes retirement allowances and tax-free payments |
| Quesnel 2025 | Published **Remuneration** column | Taxable Benefits and Total Income remain separate; expenses are separate |
| Smithers 2025 | Published remuneration and taxable benefits | Expenses and remuneration-plus-expenses total |

These definitions differ. Do not silently compare Kamloops or Quesnel's remuneration column with another municipality's broader total without consulting the component audit. In this collection, **267 published employee rows have remuneration at or below $75,000** while appearing in the source's named schedule. They remain included: the parser preserves the disclosed cohort and does not re-filter it using one selected component. Castlegar explicitly uses an inclusive $75,000 threshold.

There are **1,867 missing expense cells and six negative expense amounts**. A blank or dash becomes `null`; a printed zero remains zero; a negative remains negative. The published negative Penticton employee and council adjustments are covered by regression tests. No position is invented where the report omits it.

## Evidence and validation

`reviewed-inputs.json` pins each original PDF's SHA-256, source and archive URL, actual calendar year, physical table pages, expected row counts, column definitions, and reviewed layout exceptions. The generic table parser requires the reporting year on explicitly identified remuneration-table pages. Kamloops and Fort St. John require it in each parsed schedule page. Prince George uses the repository's existing strict importer.

Every accepted normalized row is checked against a separately read representation of the original PDF: Poppler layout text is compared with PyMuPDF positioned words. Name, title, component amounts, page and row multiplicity must agree. Complete original text spans or character coordinates resolve a small number of font, clipping and overlap defects; those exceptions are logged per row in the validation metadata. They are not inferred from another person's record or another year. Representative rendered pages and all specifically recovered 2023 Kelowna text defects were inspected visually; `visuallyReviewedPhysicalPages` records only inspected pages, not a claim that every page received a separate visual inspection.

Named employee or council subtotals are checked for each report. For Kelowna, the published all-employee total less the consolidated below-threshold amount gives the named-employee control. Cent-precision reports reconcile exactly. Several whole-dollar reports have small discrepancies between the sum of published rows and published controls. The parser bounds these differences, records the exact residual for every component, and never changes an individual amount to force a match. The largest component residual in accepted sources is $30. No cause is assumed for those differences.

The source manifest contains compressed-file and normalized-data hashes, row counts, physical-page counts, remuneration and expense totals, missing/zero/negative counts, and component reconciliation evidence. Each accepted cohort has a separate compressed audit under `audit/`; component amounts use integer CAD cents. Normalized data uses the repository's six-field schema:

```text
employerSlug, name, position, remuneration, expenses, pdfPage
```

Supplier tables, employer benefit aggregates, and unnamed employee totals are never converted into named employee records. Accepted data and its audit files are written only after all requested reports pass validation.

## Discovery and unfinished work

`discovery.json` records **117 report-year links across 19 municipalities**, as observed on their official sites. An archive label is a lead, not proof of a report's actual period. Downloaded PDFs have fingerprints and page counts where available. **105 outstanding report/cohort entries** are carried in the source manifest; 18 concern council schedules whose employee schedule was accepted, and 87 concern reports not imported here. The province-wide roster and other municipal collections handle the rest of British Columbia.

| Municipality or report | Current finding and next step |
| --- | --- |
| Prince George 2023 | The original [eScribe PDF](https://pub-princegeorge.escribemeetings.com/filestream.ashx?DocumentId=26123) now downloads successfully. Its 404 employee and nine elected-official rows are verified here. The earlier HTTP 403 hold can be resolved using this same URL and the pinned hash. |
| Kamloops 2024 | Official report downloaded. Wrapped titles and additional retroactive-pay columns still require a dedicated mapping and independent reconciliation. All other indexed 2016–2025 employee schedules were imported. |
| Kelowna 2020 | Original PDF is image-only. OCR and visual verification remain required; 2019 and 2021–2025 employee schedules were imported. |
| Terrace 2017–2025 | Nine official report links recorded; downloaded image-only reports require OCR and subtotal verification. |
| Vernon 2025 | The archive links a corrected signed PDF. Employee schedules are image-based; physical page 5 was visually confirmed. Use the corrected version for OCR work. |
| West Kelowna 2025 | The official index links a filename containing `draft`; the report's approval page is unsigned. A reviewed recipe reconciles 191 employees and seven elected officials, but no rows are accepted pending confirmation of the adopted/final report. The held recipe is in `reviewed-but-held-inputs.json`. |
| Salmon Arm 2025 | The [archive's 2025 SOFI link](https://www.salmonarm.ca/Archive.aspx?ADID=1286) returned a 38-page **Financial Statements** document with no named remuneration schedules. Obtain the actual 2025 SOFI schedules. This is a wrong/incomplete linked-document issue, not evidence that salaries do not exist. The 2023 and 2024 SOFI PDFs are also downloaded and await extraction. |
| Quesnel 2023 | The official 2023 label links back to its financial-statements index. No original report was obtained from that link. The 2025 employee schedule is imported; 2018–2022 and 2024 reports remain leads. |
| Dawson Creek | [Official archive](https://dawsoncreek.civicweb.net/filepro/documents/135340/) enumerated for 2015–2025, including direct document links. Extraction pending. |
| Williams Lake | [Official SOFI archive](https://williamslake.ca/Archive.aspx?AMID=49) enumerated for 2011–2025. Extraction pending. |
| Nelson | Official archive lists 2011–2025. The 2025 employee and council schedules are imported; historical reports remain leads. |
| Prince Rupert | Official archive lists 2016–2025. The 2025 employee schedule is imported; historical reports and council extraction remain outstanding. |
| Kitimat | The 2024 SOFI is item 10 in the [23 June 2025 official special-meeting agenda](https://www.kitimat.ca/en/municipal-hall/resources/Documents/Council-Meetings-and-Agendas/Agendas/2025-Agendas/2025_06_23_SPEC-agenda-final.pdf). Extract and verify the report attachment; the 7 July agenda contains approval minutes. |
| Trail | Official reports page lists 2021–2024 SOFI titles as text, but retrieved HTML supplied no corresponding report hyperlinks. Resolve through the financial-statements page or council attachments. |
| Other historical reports | Penticton, Cranbrook, Castlegar, Quesnel and Smithers prior-year links are preserved in discovery rather than counted as imports. The separately linked Smithers Public Library report is explicitly excluded from Town employee assumptions. |

## Reproduction and focused checks

Requirements are Python 3, Poppler's `pdftotext`, and PyMuPDF (`pymupdf`). The original PDFs are cached under ignored `tmp/municipal-north/`; they are not duplicated in the committed collection. The input manifest has exact original URLs and expected fingerprints. A changed source must be reviewed rather than accepted under an old fingerprint.

From the repository root:

```bash
# Download missing originals, require every fingerprint, and reproduce the collection.
python3 scripts/parse_municipal_north.py

# Reproduce using only already-cached originals.
python3 scripts/parse_municipal_north.py --offline

# Write an isolated reproduction for a byte comparison.
python3 scripts/parse_municipal_north.py --offline --output /tmp/municipal-north-reproduction

# No network or original PDFs needed for these focused regression checks.
python3 scripts/test_parse_municipal_north.py
```

The five offline tests cover missing/zero/negative precision, duplicate-row multiplicity, stopping before supplier rows, exclusion of separate benefit columns from remuneration, retention of disclosed below-threshold rows, incorrect-period and incorrect-control rejection, every accepted normalized/audit file hash, calendar periods, row totals, source-component selection, and known negative expenses. Full reproduction independently rechecks all 8,806 rows against the original PDFs.

The collection must be registered in `research/salaries/collections.json` to participate in the global salary build. This directory does not relabel older compiled periods or delete overlapping historical records; any reconciliation with those records belongs in the reviewed global integration.
