# Legislative Assembly administration staff recovery

743 named staff observations recovered from five official annual administration employee compensation reports: 92 (2021/22), 119 (2022/23), 144 (2023/24), 178 (2024/25), 210 (2025/26).

## Scope and money meaning

The reports disclose cash-basis payments of $75,000 or greater, including salary, overtime and vacation payouts. Salary includes taxable benefits and other salary-related payments. Values are not annual salary rates. Expenses are not disclosed and remain null. The cohort excludes caucus staff, constituency office staff, and elected MLAs. Executive-only reports overlap these reports and have not been added. Earlier administration employee schedules remain a coverage gap; candidate 2018/19–2020/21 URLs returned 404.

Each source manifest entry links its official PDF and records its original hash, normalized hash, fiscal dates and physical PDF pages. The public www.leg.bc.ca links returned HTML rather than PDF during acquisition; the corresponding official lims.leg.bc.ca/pdms/file URLs returned PDFs.

## Reproduction and checks

Run `python scripts/recover-assembly-staff.py`, then `python scripts/test-assembly-staff-recovery.py` from the repository root. Requires Python pdfplumber and Poppler pdftotext. Generation is offline from committed originals; gzip timestamps are fixed at zero.

PDF word coordinates recover names and titles. An independent Poppler layout extraction checks every total-column payment in row order. Checks assert nonempty names/titles, threshold, unique names within each report, full row counts, hashes and sums. Original whole-dollar figures are unchanged. Reconciliation residuals (sum of named published payments minus printed grand total) are -$2, +$4, $0, $0 and -$5 respectively. These small residuals are within whole-dollar rounding tolerances; no records are adjusted to force balancing.

Visual inspection of the 2024/25 last page confirms the surname is printed as “Nezhad”, not “Zangeneh Nezhad” as in adjacent years. Preserve it as published; do not infer or silently repair identity.

## Integration

Add `assembly-staff-recovery` to the salary collections list. `sources.json` and the five normalized `.json.gzip` files conform to the existing six-column salary source schema. The dedicated employer slug is `legislative-assembly-staff` in sector `Government`; never merge it into an elected MLA employer. No shared catalog, build file or generated public export was changed by this recovery.
