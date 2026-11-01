# Alberni-Clayoquot employee controls: independent review

Crown continuation reviewer, 2026-11-01. **Accept the five exact named employee cohorts, with the existing source-specific qualifications.** No row correction is justified by the control differences.

A third native engine, PDFMiner/pdfplumber, independently extracted all **122 rows** from the original hash-pinned PDFs using a separate fixed-density page grid and parser. Every name, wrapped title, remuneration, expense, physical page and row multiplicity matches the proposed normalized payloads. Counts are 15 (2019), 14 (2020), 26 (2023), 31 (2024) and 36 (2025). Full independently extracted page text/rows and receipts are retained in `regional-acrd-evidence.json.gzip` and `regional-acrd-controls.json`.

I visually reviewed every named row and all controls on original physical pages 27 (2019), 28 (2020), 34 (2023), 32–33 (2024), and 35–36 (2025). Published table scope is “Other Employees (excluding those listed in Part 1 above)”. Elected/alternate director payments are separate and excluded. The **Total Other Employees** control includes the separately published consolidated employees at $75,000 or less. Therefore named cells must be compared to that total **less the same table's under-threshold aggregate**, not directly to total payroll or to elected officials plus employees.

| Period | Named pay | Under-threshold pay | Printed employee total | Pay residual | Named expenses | Under-threshold expenses | Printed employee expense total | Expense residual |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 1,518,257 | 984,621 | 2,502,878 | 0 | 64,044 | 20,687 | 84,730 | +1 |
| 2020 | 1,455,308 | 1,156,710 | 2,612,019 | −1 | 31,000 | 19,653 | 50,596 | +57 |
| 2023 | 2,728,410 | 1,303,986 | 4,032,396 | 0 | 84,470 | 42,607 | 127,077 | 0 |
| 2024 | 3,398,703 | 1,265,748 | 4,664,451 | 0 | 114,516 | 39,646 | 154,162 | 0 |
| 2025 | 3,839,079 | 984,006 | 4,823,083 | +2 | 147,368 | 28,756 | 176,442 | −318 |

Residual means named rows plus the printed under-threshold aggregate minus the printed employee total. All values are dollars. Every named cell is unambiguous in the rendered originals and is preserved. The 2019, 2020 and 2025 source-control differences are unresolved; neither a cause nor an affected individual can be inferred. The “Reconciliation” section repeats the employee total rather than reconciling individual rows, and does not resolve these differences.

The review specifically includes 2025's wrapped `Hallberg Dodds, Charity`, the two employee rows continuing onto physical page 36, multi-line General Manager/Inspector titles, and the 2025 source remuneration cell `75493` without a thousands comma. Monetary formatting does not alter its numeric value. All named pay independently exceeds the threshold. Calendar periods are supported by the original SOFI covers; no compiled fiscal-looking label is mapped or replaced on that basis.

Reproduce against cached originals:

```sh
python scripts/continue_crowns_review_acrd.py
```

This review writes only its own receipts. No candidate source, normalized row, alias or registry was modified. A clarification request for the unresolved totals can remain a draft alongside the visible source warnings.
