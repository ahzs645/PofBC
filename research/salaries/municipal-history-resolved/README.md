# Qualified recovery of two held municipal disclosures

Reviewed on November 1, 2026. This collection accepts **60 observations** in three cohorts from two original calendar-year reports:

| Municipality / period | Category | Rows | Remuneration | App expenses |
|---|---|---:|---:|---:|
| Merritt 2025 | Employees | 46 | $4,779,040.10 | Missing: expense definition unresolved |
| Merritt 2025 | Council | 7 | $186,501.50 | Missing: expense definition unresolved |
| Lake Cowichan 2024 | Employees, partial | 7 of 8 | $729,610.84 | $15,015.40 |

Every original named row and monetary component agrees between PyMuPDF and Poppler, then against the complete rendered salary page. Both original PDFs were freshly retrieved; their fingerprints match the earlier held sources. Names, spelling, positions, calendar years, footnote markers, column boundaries, source controls and publication evidence were reviewed. Reporting periods come from the original headings, not upload dates. These are threshold payment disclosures, not complete employee rosters or base salary rates.

## Merritt: remuneration accepted, expenses qualified

[Official source index](https://www.merritt.ca/government/annual-reports-and-financial-statements/) → [2025 original SOFI](https://www.merritt.ca/wp-content/uploads/2026/09/2025-SOFI.pdf), physical page 4. Original SHA-256: `887d8b9ec8fcb72288485f0b77ae8b3a4e09751bb69fa2b991bd392acdebf0ce`.

All 46 named employee payments sum exactly to the printed named remuneration subtotal, $4,779,040.10. All seven council payments sum exactly to $186,501.50. The printed **Total Employees (B)** is $7,842,227.42. The observed arithmetic is:

`$4,779,040.10 named employees + $2,876,685.82 under75k aggregate + $186,501.50 council = $7,842,227.42`.

The expense columns show the same inclusion of council: named employee **Expenses** $86,560.18 plus council $29,645.85 equals printed B $116,206.03; named employee **Grant Funded Expenses** $47,565.44 plus council $576.49 equals printed B $48,141.93. This establishes numerical identities, without certifying the intended issuer label or treating unreported below-threshold expense cells as zero.

The report does not define whether the two expense columns overlap or form an additive total. Every app expense field is therefore **null**. Both actual source columns, including missing cells, remain in row evidence. Neither component is added to remuneration or presented as a complete expense amount. `expensesNote`, `publicWarning` and `completeExpensesDisclosure:false` explain this publicly. `totalExpenses:null` means unknown, not a zero-expense claim.

The employee cohort contains all 46 named remuneration rows, so its named-pay completeness flags are true. Single asterisks denote POC and provincial deployment remuneration; double asterisks denote vacation payout. These source explanations and markers are preserved. Wendy Charney's council position annotation `(incl ESS $5,497.77)` is retained literally and is not interpreted as an extra payment. Source spelling such as `Building Offical I` and `Court Liasion/Foreperson` is preserved.

The official site publishes this report without a draft mark. Physical page 2 has approval wording but blank signature and date lines. The warning discloses this, and no signed adoption is claimed. The separately posted 68-page 2025 annual report supplies no remuneration schedule or expense-column clarification. The official agenda landing page links the council archive, but no meeting-level adoption decision was verified in this bounded pass.

## Lake Cowichan: seven rows accepted, one held

[Official finance index](https://lakecowichan.ca/finance.php) → [2024 original SOFI](https://lakecowichan.ca/dl/2024%20SOFI.pdf), physical page 31 / printed page 26. Original SHA-256: `e909d34599f0a3d2f8a1ebbdb706bb1139e9fecccbbd9cf04b12b96ffc4d7c46`.

The separate **Financial Compensation** column supplies remuneration; **Travel, Conferences and Other** supplies expenses. The expense-inclusive **Totals** column is never pay. The seven accepted rows each agree exactly with their own compensation-plus-expense total. Their names, positions and all three amounts were checked in the full rendered page. Council 2024 remains solely in `municipal-wave-capital` and is not duplicated.

**Jessica May, Fire Risk Officer, remains withheld.** The source shows compensation $92,354.93, expense $5,429.75 and Total $92,784.68. The first two sum to $97,784.68, a $5,000.00 conflict. No cell is corrected, selected as the presumed error, or inferred from another year. All original fields and both readers are retained in this collection's evidence.

Before withholding the row, the complete eight-row compensation sum $821,965.77 and expense sum $20,445.15 agree exactly with printed all-staff amounts less the separately printed all-other-employees aggregate. This verifies extraction but does not resolve the conflicting individual Total. The aggregate's own expense-inclusive Total is $0.09 below its two components, also retained and warned about. The all-staff component sum itself agrees with the printed all-staff Total.

Both source and validation levels explicitly set **`completeEmployeeSchedule:false`** and **`completeNamedCohort:false`**. They state eight source rows, seven accepted and one withheld. Partial sums are labelled separately from full-cohort controls. The visible warning names the omitted row and both discrepancies. Approval on physical page 27 visibly bears the Mayor's and Finance Director's signatures, dated June 24, 2025. The separately published 58-page 2024 annual report contains no corrected remuneration schedule.

## Reproduce

From the repository root:

```sh
python scripts/parse_history_resolved.py --cache-dir /tmp/history-resolved --verify
python scripts/test_history_resolved.py
```

The first command downloads missing originals, requires exact original hashes, checks actual reporting headings, independently reads every source cell and control, compares all rows with the pinned rendered-page transcription, and reproduces every normalized/evidence gzip and the manifest byte for byte. Use `--output-dir /tmp/history-resolved-rebuild` without `--verify` for a separate rebuild. Ten regressions protect the actual source conflicts, missing-value semantics, raw expense components, markers and source spellings, incomplete flags, hashes and absence of duplicate council scope.

Layouts, complete reviewed rows, index snapshots, retrieval receipts, public search limits and remaining clarification tasks are in [the resolution audit](../municipal-history-pass/resolved/README.md). No municipality was contacted, and no request or FOI was sent.
