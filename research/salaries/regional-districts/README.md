# Regional district SOFI schedules (2023–2025)

Official Statement of Financial Information (SOFI) schedules for four B.C. regional districts, calendar years 2023, 2024 and 2025: employee remuneration (named cohort above $75,000, with expenses) and board directors/alternates. Sector: Municipalities (as for the existing regional districts).

## Method

- Each PDF was downloaded from the regional district's own site; SHA-256 below is of the file as downloaded.
- Every schedule has a native text layer (no OCR). Rows were extracted twice, independently: poppler `pdftotext -layout` (cells split on runs of 2+ spaces) and pdfplumber word geometry (numeric cells assigned to columns by clustering printed right edges per page). Both agree row-for-row on page, name, position, footnote markers and every cell; every other line inside each table is listed in the evidence file.
- Names, positions and amounts are kept as printed. Footnote asterisks are removed from the normalized name/position and kept in evidence. Expense dashes become `null`. A row whose remuneration is a dash is held out of the data file (kept in evidence) rather than treated as zero.
- Where a schedule prints component columns (TNRD Operational/Emergency Response; RDN Base/Emergency/Other), the imported remuneration is the printed Total Remuneration; components stay in evidence.
- Named row sums are reconciled to the printed named subtotal and, where printed, to the total less the consolidated under-threshold line. Tolerance: whole-dollar rounding (0.5 × rows). No cell is changed to balance.
- Regional District of North Okanagan: the signed PDFs contain a duplicate Helvetica text overlay. pdfplumber ran on the original with Helvetica characters filtered out; pdftotext ran on a derived copy with only those overlay text objects removed (`tools/strip_overlay.py`). The derived-file hash is in each evidence file. RDNO's covering staff report gives employee counts above $75,000 (40, 48, 62), which match the row counts.
- `tools/` holds the extraction scripts and per-schedule configs (the absolute paths in them point to the original scratch download folder).

## Sources

| Source | Status | Rows | Remuneration | Expenses | Reconciliation (rows − printed) |
|---|---|---:|---:|---:|---|
| Cowichan Valley Regional District 2023 elected-officials | accepted | 27 | 648,164.31 | 65,797.36 | remuneration +0.00 vs (unlabelled total line); expenses +0.00 vs (unlabelled total line) |
| Cowichan Valley Regional District 2023 employee-remuneration | accepted | 135 | 14,106,162.79 | 155,293.70 | remuneration +0.00 vs Subtotal; expenses +0.00 vs Subtotal; remuneration +0.00 vs printed total less consolidated under-threshold line; expenses +0.00 vs printed total less consolidated under-threshold line |
| Cowichan Valley Regional District 2024 elected-officials | held-for-review | 29 | 662,228.36 | 81,342.90 | remuneration -309.26 vs (unlabelled total line); expenses +0.00 vs (unlabelled total line) |
| Cowichan Valley Regional District 2024 employee-remuneration | accepted | 146 | 15,457,056.32 | 158,953.36 | remuneration +0.00 vs Subtotal; expenses +0.00 vs Subtotal; remuneration +0.00 vs printed total less consolidated under-threshold line; expenses +0.00 vs printed total less consolidated under-threshold line |
| Cowichan Valley Regional District 2025 elected-officials | accepted | 28 | 677,838.26 | 94,236.19 | remuneration +0.00 vs (unlabelled total line); expenses +0.00 vs (unlabelled total line) |
| Cowichan Valley Regional District 2025 employee-remuneration | accepted | 175 | 18,489,073.24 | 305,432.02 | remuneration +0.00 vs Subtotal; expenses +0.00 vs Subtotal; remuneration +0.00 vs printed total less consolidated under-threshold line; expenses +0.00 vs printed total less consolidated under-threshold line |
| Thompson-Nicola Regional District 2023 elected-officials | accepted | 38 | 659,549.00 | 226,001.00 | remuneration +0.00 vs Consolidated total, elected officals; expenses +0.00 vs Consolidated total, elected officals |
| Thompson-Nicola Regional District 2023 employee-remuneration | accepted | 53 | 5,452,632.00 | 222,370.00 | remuneration +0.00 vs Total, employees earning $75,000 or more; expenses +0.00 vs Total, employees earning $75,000 or more; remuneration +0.00 vs printed total less consolidated under-threshold line; expenses +0.00 vs printed total less consolidated under-threshold line |
| Thompson-Nicola Regional District 2024 elected-officials | accepted | 36 | 754,605.00 | 179,686.00 | remuneration +0.00 vs Consolidated total, elected officals; expenses +0.00 vs Consolidated total, elected officals |
| Thompson-Nicola Regional District 2024 employee-remuneration | accepted | 69 | 7,242,858.00 | 248,642.00 | remuneration +0.00 vs Total, employees earning $75,000 or more; expenses +0.00 vs Total, employees earning $75,000 or more; remuneration +0.00 vs printed total less consolidated under-threshold line; expenses +0.00 vs printed total less consolidated under-threshold line |
| Thompson-Nicola Regional District 2025 elected-officials | accepted | 36 | 773,135.00 | 201,828.00 | remuneration +3.00 vs Consolidated total, elected officals; expenses +2.00 vs Consolidated total, elected officals |
| Thompson-Nicola Regional District 2025 employee-remuneration | accepted | 72 | 7,856,896.00 | 214,907.00 | remuneration -1.00 vs Total, employees earning $75,000 or more; expenses -1.00 vs Total, employees earning $75,000 or more; remuneration -1.00 vs printed total less consolidated under-threshold line; expenses -1.00 vs printed total less consolidated under-threshold line |
| Regional District of Nanaimo 2023 elected-officials | accepted | 27 | 804,568.18 | 73,378.99 | remuneration +0.00 vs Total Remuneration and Expenses; expenses +0.00 vs Total Remuneration and Expenses |
| Regional District of Nanaimo 2023 employee-remuneration | accepted | 269 | 27,025,503.59 | 402,803.99 | remuneration +0.00 vs Total Individual Remuneration Paid over; expenses +0.00 vs Total Individual Remuneration Paid over; remuneration +0.00 vs printed total less consolidated under-threshold line; expenses +0.00 vs printed total less consolidated under-threshold line |
| Regional District of Nanaimo 2024 elected-officials | accepted | 26 | 809,405.97 | 76,367.90 | remuneration +0.00 vs Total Remuneration and Expenses; expenses +0.00 vs Total Remuneration and Expenses |
| Regional District of Nanaimo 2024 employee-remuneration | accepted | 282 | 28,812,966.41 | 496,338.23 | remuneration +0.00 vs Total Individual Remuneration Paid over; expenses +0.00 vs Total Individual Remuneration Paid over; remuneration +0.00 vs printed total less consolidated under-threshold line; expenses +0.00 vs printed total less consolidated under-threshold line |
| Regional District of Nanaimo 2025 elected-officials | accepted | 24 | 797,917.95 | 70,858.83 | remuneration +0.00 vs Total Remuneration and Expenses; expenses +0.00 vs Total Remuneration and Expenses |
| Regional District of Nanaimo 2025 employee-remuneration | accepted | 341 | 36,137,212.74 | 615,338.14 | remuneration +0.00 vs Total Individual Remuneration Paid over; expenses +0.00 vs Total Individual Remuneration Paid over; remuneration +0.00 vs printed total less consolidated under-threshold line; expenses +0.00 vs printed total less consolidated under-threshold line |
| Regional District of North Okanagan 2023 elected-officials | accepted | 26 | 421,705.00 | 30,930.00 | remuneration +1.00 vs Total; expenses +0.00 vs Total |
| Regional District of North Okanagan 2023 employee-remuneration | accepted | 40 | 4,416,859.00 | 144,330.00 | remuneration +0.00 vs SUBTOTAL; expenses +0.00 vs SUBTOTAL; remuneration +0.00 vs printed total less consolidated under-threshold line |
| Regional District of North Okanagan 2024 elected-officials | accepted | 26 | 435,385.00 | 30,486.00 | remuneration +0.00 vs Total; expenses +0.00 vs Total |
| Regional District of North Okanagan 2024 employee-remuneration | accepted | 48 | 5,317,471.00 | 111,756.00 | remuneration +0.00 vs SUBTOTAL; expenses +0.00 vs SUBTOTAL; remuneration +0.00 vs printed total less consolidated under-threshold line; expenses +0.00 vs printed total less consolidated under-threshold line |
| Regional District of North Okanagan 2025 elected-officials | accepted | 25 | 444,312.00 | 41,368.00 | remuneration +0.00 vs Total; expenses +0.00 vs Total |
| Regional District of North Okanagan 2025 employee-remuneration | accepted | 62 | 6,788,589.00 | 109,957.00 | remuneration +0.00 vs SUBTOTAL; expenses +0.00 vs SUBTOTAL; remuneration +0.00 vs printed total less consolidated under-threshold line; expenses +0.00 vs printed total less consolidated under-threshold line |

## Documents

- Cowichan Valley Regional District 2023: https://cvrd.ca/wp-content/uploads/2025/09/Clean-signed-2023-SOFI-report_202406271216203550.pdf  
  SHA-256 `d9054b86803358a47cdfb0f716e4231fc25cc3c1e4a1c844a5b7d43495840f5a`; index: https://cvrd.ca/government-administration/finance/financial-statements/statements-of-financial-information/
- Cowichan Valley Regional District 2024: https://cvrd.ca/wp-content/uploads/2026/05/2024-SOFI-Report-FINAL.pdf  
  SHA-256 `1d1ea7b4e54cbf9245745896e9733306b35dd768d94f38e9d8c165bbdcd52767`; index: https://cvrd.ca/government-administration/finance/financial-statements/statements-of-financial-information/
- Cowichan Valley Regional District 2025: https://cvrd.ca/wp-content/uploads/2026/06/2025-Final-SOFI-Report.pdf  
  SHA-256 `9068cf19b9c13332df4047738798c42cf2e7735f88facca586b21b2657787134`; index: https://cvrd.ca/government-administration/finance/financial-statements/statements-of-financial-information/
- Thompson-Nicola Regional District 2023: https://wpcdn.tnrd.ca/wp-content/uploads/2024/06/21115159/TNRD-Statements-and-Schedules-of-Financial-Information-2023.pdf  
  SHA-256 `dd7b96f184934ff5c46b45d7bda7f38c22600ae16a1885fd8503d5983069bdf2`; index: https://www.tnrd.ca/services/budget-finance/annual-financial-reports/
- Thompson-Nicola Regional District 2024: https://wpcdn.tnrd.ca/wp-content/uploads/2025/08/15101915/TNRD-Statements-and-Schedules-of-Financial-Information-2024-signed-revised.pdf  
  SHA-256 `ca8218f894b739fad6f1128137549d7dc27fee9e5bcca31e081be1ab2495e17f`; index: https://www.tnrd.ca/services/budget-finance/annual-financial-reports/
- Thompson-Nicola Regional District 2025: https://wpcdn.tnrd.ca/wp-content/uploads/2026/07/08092006/TNRD-2025-Statement-of-Financial-Information-Signed.pdf  
  SHA-256 `c6087941b9db43a140f6f21965757aaf697580cbbf9ef3ebc354b1409a4e6b74`; index: https://www.tnrd.ca/services/budget-finance/annual-financial-reports/
- Regional District of Nanaimo 2023: https://rdn.bc.ca/sites/default/files/inline-files/2023%20Statement%20of%20Financial%20Information%281%29.pdf  
  SHA-256 `04df753ef8a92126e73c08ad731e800378dc4ac083347615ec9f0010cc3f5bfa`; index: https://rdn.bc.ca/financial-reports
- Regional District of Nanaimo 2024: https://rdn.bc.ca/sites/default/files/inline-files/2024%20Statement%20of%20Financial%20Information_0.pdf  
  SHA-256 `73178b625d157d7e802a73030d4c6c4a6611ee42dd87dc59f3ceefedcc86423a`; index: https://rdn.bc.ca/financial-reports
- Regional District of Nanaimo 2025: https://rdn.bc.ca/sites/default/files/2025%20Statement%20of%20Financial%20Information.pdf  
  SHA-256 `8d69b470d80a6f7710a41328c2adc46aecd0ed51f6a93abf0d2556d4c62a3c3b`; index: https://rdn.bc.ca/financial-reports
- Regional District of North Okanagan 2023: https://www.rdno.ca/sites/default/files/2024-06/240619_RPT_SOFI_signed.pdf  
  SHA-256 `52670126f6597e2d862ff970124c47f8194c45532abd5bee2d651b377fd9ca4b`; index: none found (direct link)
- Regional District of North Okanagan 2024: https://www.rdno.ca/sites/default/files/2025-06/250618_RPT_SOFI_2024_signed.pdf  
  SHA-256 `8e145105f9f5190447bb7de076f4cd299825ff96ababf10bfe7dbc0981395066`; index: none found (direct link)
- Regional District of North Okanagan 2025: https://www.rdno.ca/sites/default/files/2026-06/260617_RPT_SOFI_2025_signed.pdf  
  SHA-256 `4cafa9fed14841bb8d190ae0b6b28c534cf1212566f2189a0f716b51d53063af`; index: none found (direct link)

## Held and qualified items

- **regional-districts-cowichan-valley-regional-district-2024-elected-officials**: held for review. named rows do not reconcile to the printed control: remuneration rows sum 662,228.36 vs printed 662,537.62 (residual -309.26, beyond whole-dollar rounding). Both engines read the same rows and printed total; no missing, hidden or unclassified row was found, so the cause is not determinable from the document and no row or amount is inferred.
- regional-districts-cowichan-valley-regional-district-2023-elected-officials: 1 named row(s) print a dash for remuneration (Iannidinardo, L.); held from normalized payments and kept in evidence; their expenses are counted in the expense reconciliation.
- regional-districts-regional-district-of-nanaimo-2024-employee-remuneration: 4 row(s) print components that do not sum to the printed total; the printed total is imported unchanged (see evidence).
- regional-districts-regional-district-of-nanaimo-2025-elected-officials: 1 named row(s) print a dash for remuneration (Ringwald, J.); held from normalized payments and kept in evidence; their expenses are counted in the expense reconciliation.

## Not covered

- Not imported in this pass: Capital Regional District, Fraser Valley RD (2024/2025 SOFI not located on fvrd.ca; only a 2023 Public Bodies Report), Regional District of Central Okanagan and Comox Valley RD (current SOFI PDFs not located; comoxvalleyrd.ca/media/9746 is the 2007 SOFI).
- Regional District of North Okanagan PDFs carry a duplicate Helvetica text overlay; extraction used the original text layer only (see each evidence file).

## Integration

- `research/salaries/collections.json` (if present) must list `regional-districts` for the build to read this manifest; it was not edited here.
