# Crown salary recovery: InBC employee history

41 newly verified official employee observations from InBC Investment Corp., fiscal years 2022/23 (9), 2023/24 (15), and 2024/25 (17). This collection is ready for the central registry review. Board members, suppliers and aggregate-only figures are excluded. A hash-pinned complete-cohort comparison replaces nine proved duplicate compiled observations labelled 2023/24 with their actual 2022/23 official period; the net dataset increase from this collection is 32 records.

The source is InBC's [accountability archive](https://inbcinvestment.com/accountability-governance/). Each source record pins the original PDF hash, exact reporting dates, physical schedule page, normalized file hash, independent row comparison and named-subtotal controls. The cover and signed approval pages establish employer and fiscal period. Files uploaded in December 2023 or March 2025 retain their stated fiscal year.

The three complete employee tables were compared field by field using PyMuPDF positioned words and Poppler layout text and visually checked against rendered physical PDF pages 28, 30 and 29, respectively. Surname and initials remain exactly as disclosed; there are no published employee job titles. In particular, the 2022/23 source says `Deering, D`, and later schedules say `Deering, A`. No identity inference changes those cells.

The source calls its monetary field “Renumeration.” That source-labelled amount is used as remuneration; a base salary or detailed component breakdown is not supplied. Expenses remain separate. The heading describes employees with remuneration and expenses exceeding $75,000; all accepted remuneration amounts themselves exceed $75,000.

| Fiscal year | Rows | Row remuneration | Printed named remuneration | Disclosed expense sum | Printed named expenses | Residual pay / expenses |
|---|---:|---:|---:|---:|---:|---:|
| 2022/23 | 9 | $1,298,918 | $1,298,918 | $102,273 | $102,273 | $0 / $0 |
| 2023/24 | 15 | $2,334,321 | $2,334,320 | $105,309 | $105,309 | +$1 / $0 |
| 2024/25 | 17 | $2,874,812 | $2,874,812 | $152,073 | $152,072 | $0 / +$1 |

Residuals are rows minus printed named subtotals. The cause of the two $1 differences is unresolved. Original cells are unchanged, and the two source records carry public warnings. In 2024/25 Chiew, B.'s expense cell is blank, retained as `null`; its disclosed expense sum includes the other 16 numeric cells. No missing cell is converted to zero and no amount is altered to force a total.

The 2021/22 original, physical page 27, explicitly reports no employees receiving more than $75,000 from InBC during the period, and a $232,304 below-threshold aggregate. It explains the ministry secondments and hiring starting in December 2021. This evidence is retained in the sector audit, not fabricated into individual salary rows. The 2020/21 report's financial-statement note describes ministry-supported operating costs; it has no named employee remuneration schedule. It is not imported as a complete employee roster.

Reproduce from original hash-pinned PDFs with PyMuPDF and Poppler available:

```sh
python scripts/import_sector_crowns.py --cache-dir /tmp/sector-crowns --verify
python -m unittest discover -s scripts -p test_sector_crowns.py
```

Omit `--verify` to regenerate this collection. `--output-dir` supports an isolated reproduction. Downloads and writes are restricted to the chosen cache and output directory; the script does not register collections or remove compiled records. The `evidence/` files retain both extracted schedule readings, positioned row evidence, cover and approval text, original hashes and exact controls. Original PDFs can be re-fetched from the pinned URLs in `sources.json`.

The complete compiled InBC partition contains nine employee rows labelled `2023/24`, all with no disclosed positions. Every exact name, position, remuneration and expense tuple matches the complete official **2022/23** employee schedule, including multiplicity. None matches the later fifteen-row official **2023/24** schedule or the 2024/25 schedule. No normalization is required. [inbc-overlap.json](inbc-overlap.json) retains both compared cohorts, the original baseline fingerprint, the exact ordered compiled-row hash and accepted-source fingerprints. The manifest’s `compiledReplacements` rule explicitly records `2023/24 → 2022/23`, expected removal 9, retained 0. There are no separate compiled board rows in that partition. This prevents the build from obscuring the compiler’s reporting-period error through an ordinary same-label replacement.
