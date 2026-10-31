# Lower Mainland municipal remuneration collection

Reviewed on 2026-10-31. This collection adds **26,814 employee records in 63 official report-years across 18 municipalities**. The source discovery register covers **30 municipalities and 184 dated report links**; **121 report links remain explicitly held or unparsed**. Vancouver’s existing open-data series remains in its separate collection.

## Accepted coverage

| Municipality | Calendar years | Named employee records |
| --- | --- | ---: |
| Bowen Island Municipality | 2023, 2024, 2025 | 60 |
| City of Burnaby | 2021, 2022, 2023, 2024, 2025 | 6,457 |
| City of Coquitlam | 2025 | 816 |
| City of Delta | 2025 | 608 |
| City of Langley | 2023, 2024 | 168 |
| City of Maple Ridge | 2016, 2019, 2020, 2021, 2022, 2023, 2024, 2025 | 2,066 |
| City of New Westminster | 2021, 2022, 2023, 2024, 2025 | 1,841 |
| City of North Vancouver | 2023, 2024, 2025 | 1,061 |
| City of Port Coquitlam | 2021, 2023, 2024, 2025 | 1,028 |
| City of Surrey | 2021, 2022, 2023, 2024 | 5,545 |
| City of White Rock | 2024, 2025 | 230 |
| District of North Vancouver | 2017, 2019, 2020, 2021, 2022, 2023, 2024, 2025 | 3,535 |
| District of Squamish | 2025 | 173 |
| District of West Vancouver | 2019, 2022, 2023, 2024, 2025 | 2,279 |
| Resort Municipality of Whistler | 2021, 2023, 2024, 2025 | 849 |
| Village of Anmore | 2023 | 3 |
| Village of Lions Bay | 2024 | 9 |
| Village of Pemberton | 2020, 2021, 2022, 2023, 2025 | 86 |

## What the numbers mean

These are disclosed calendar-year remuneration payments. They can contain overtime, retroactive increases, taxable benefits, leave payouts and other compensation. They are not contracted annual salary rates. Different municipal source schedules report different components; each reviewed input explicitly identifies the columns used for remuneration and expenses. In particular, the New Westminster, Langley City and Port Coquitlam total columns include expenses and are never used as remuneration.

Names, initials, surnames and available job titles are retained as the municipality disclosed them. No full names or occupations are inferred. The District of North Vancouver explicitly identifies `F` as Firefighter in its 2022–2024 schedules; that published indicator is mapped to the stated title. Missing expense cells and dashes remain null, explicit zero remains zero, and negative payments remain negative. Where two reported remuneration components are combined, a dash contributes no reported amount; original component strings are retained.

The records preserve the official report’s scope. Whistler’s consolidated schedules include housing-authority and other municipal subsidiary employees. New Westminster’s employee schedule excludes sworn police. Published threshold exceptions are retained and counted in validation metadata. Names and initials alone do not reliably identify unique people across years.

Only the named employee schedules are imported here. Elected-official remuneration, aggregate under-threshold payroll, employer pension/insurance contributions and supplier payments remain outside these employee files. Finding an annual financial statement or a payment to a supplier is not evidence of a named employee salary.

## Source and validation files

- `sources.json`: accepted import manifest, original PDF hashes, physical pages, period dates, data hashes, component totals, residuals and explicit held reports.
- `reviewed-inputs.json`: pinned source URLs, original hashes, allowed component mapping, exact expected counts, row counts by page, control totals, residuals and normalized record hashes.
- `*-employees.json.gzip`: six-column normalized arrays in the manifest row schema.
- `*-components.json.gzip`: source names, positions, raw monetary component strings, exact text keys and physical PDF page for every accepted row.
- `discovery.json`: jurisdiction-by-jurisdiction source inventory and per-year import/hold status.
- `discovery-seeds.json`: jurisdiction identifiers and official archive/index references.

The importer verifies the original PDF hash before extraction. Poppler layout rows are checked against independently grouped PyMuPDF word coordinates. pypdf corroborates exact published text for the documented clipped/wrapped DNV names. Every inter-row character inside accepted page tables must belong to an extracted row; this check caught complete-pay-but-truncated-position records and blocked their publication. Fixed component sums, printed controls, row counts, page counts and normalized hashes must match the reviewed input exactly. A changed source or result fails closed.

Whole-dollar disclosures sometimes have small differences between the sum of individually rounded rows and their printed subtotals. Those exact residuals are retained, not hidden by altering records. **Maple Ridge 2025 has a reviewed five-cent expense discrepancy:** the 386 published expense cells total CAD 659,177.00, while the named subtotal says CAD 659,177.05. Both PDF readers agree on the cells, and the discrepancy is described in that source’s notes.

## Reproduce and check

Requires Python 3, Poppler `pdftotext`, PyMuPDF (`fitz`) and `pypdf`. Commands run from the repository root. Original PDFs are fetched into a disposable cache and are not committed.

```bash
python3 scripts/test_municipal_lower_mainland.py
python3 scripts/parse_municipal_lower_mainland.py --check-data
python3 scripts/parse_municipal_lower_mainland.py --cache /tmp/pofbc-lower --fetch
```

The first command runs eight focused regression tests for observed PDF failure modes. The second verifies all retained hashes, schemas, totals and raw-component normalization without network or PDF originals. The third downloads missing pinned official originals and fully revalidates extraction. Add `--write` to reproduce normalized/audit files after all checks pass. To inspect one report, add `--source north-vancouver-district-2022` (repeatable). Downloads are only from the reviewed official URLs; no new source is automatically promoted.

## Explicit remaining work

- **Surrey 2025:** all 1,543 candidate rows agree between readers, but their expense sum is CAD 473 above the printed named subtotal. This year is held for resolution.
- **North Vancouver City 2022:** the expense cells differ from the printed subtotal by CAD 143. Earlier files often need OCR or font recovery.
- **Port Moody:** wrapped position fragments remain unparsed in 2022–2023 even where pay controls match; other recent layouts also need complete multiline reconstruction.
- **Port Coquitlam 2022 and Bowen Island 2022:** crowded name/title boundaries need source-specific review.
- **Pemberton 2024:** a stray period occupies an expense cell and one row needs reviewed extraction before the year can be accepted.
- **Richmond 2024:** inconsistent OCR/text and missing schedule-page matches prevent independent complete extraction.
- **Mission and many older reports:** scans, unusual fonts or unsupported layouts require OCR and original-page verification.
- **Belcarra:** official archives were obtained; multiline titles still need a reviewed parser. Anmore, Lions Bay and other villages have additional years to search or parse.
- **Abbotsford:** the official finance page says SOFI is available on request. No request was sent. Chilliwack, Hope, Kent and Langley Township still need stronger direct report discovery; an index or secondary lead is not treated as a completed salary import.

All report-specific states remain in `discovery.json` and `sources.json`. This is a verified expansion with a reproducible follow-up queue; it does not claim every municipality, report year or employee is now covered. No compiled reporting year is relabelled by this collection.
