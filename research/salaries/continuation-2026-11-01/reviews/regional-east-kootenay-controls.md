# East Kootenay employee schedules: independent review

Crown continuation reviewer, 2026-11-01. **Accept the three exact original cohorts with the stated source qualifications.** Every named row and control is unambiguous; the control differences do not justify changing an individual value.

A third native engine, PDFMiner/pdfplumber, independently extracted all **155 observations** using a separate four-point text grid and cell parser. It imports none of the author's parsing functions. Every surname, position, remuneration, numeric/missing expense, physical page and row multiplicity matches the candidate payloads. Counts are 47 (2023), 52 (2024) and 56 (2025). The exact original hashes, field comparison, control values, missing-cell counts and vacation markers are in `regional-east-kootenay-controls.json`; full independent text/rows and source-scope evidence are in `regional-east-kootenay-evidence.json.gzip`.

I rendered and visually reviewed **every named row, control, footnote and separate aggregate** on all six original physical pages: 6–7 for 2023, 7–8 for 2024, and 6–7 for 2025. Original calendar dates come from the covers and the schedules' December 31 labels. The files remain at `/tmp/continuation-government-police/regional-east-kootenay-{2,1,0}.pdf`, respectively.

The original Name field publishes **surnames only**. The candidates do not invent given names, initials or individual identities. Literal spelling/case differences remain source-specific: `DePAOLI` in 2023, `DE PAOLIE` in 2024, and `DE PAOLI*` in 2025. This review makes no cross-year identity equivalence or spelling correction.

Each accepted amount is the source's individual **Employee Gross Earnings (over $75,000)** field, separate from expenses. Every imported remuneration is above that threshold. Below-threshold employee earnings, directors and the separate **Employer Share of Employee Benefits** section are excluded from individual observations. The latter lists Receiver General, health/dental, employer health tax, superannuation and group insurance as aggregates. Neither these amounts nor Gross Payroll are allocated to named employees or substituted for their published gross earnings. No base-salary definition is inferred.

Expense dashes have no zero legend. The candidates correctly retain **18, 19 and 18 null expense cells**, respectively. Numeric cells are preserved; known-cell expense sums do not establish zero expenses for undisclosed cells. The comparator used below is the printed named over-threshold Employee Gross Earnings row, rather than Gross Payroll, all employee earnings or any employer-benefit aggregate.

| Year | Named remuneration sum | Printed named remuneration | Residual | Known expense sum | Printed named expenses | Residual |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | $4,940,051 | $4,940,053 | −$2 | $35,988 | $31,988 | +$4,000 |
| 2024 | $5,606,802 | $5,606,800 | +$2 | $21,374 | $20,998 | +$376 |
| 2025 | $5,958,324 | $5,958,322 | +$2 | $25,067 | $24,942 | +$125 |

Residual means independently summed published individual cells minus the published named control. The rendered originals confirm every listed cell and control, including the 2023 THOMPSON expense of $7,004. The source does not supply a reconciliation resolving these differences. **All causes remain unresolved.** A coincident individual value or the size of a residual is not evidence that a particular employee cell should change. The existing public warnings state these differences accurately.

All three originals print “Includes payout of unused vacation” as an asterisk footnote. In the named rows, only 2025 actually marks six surnames: `DE PAOLI*`, `DUCZEK*`, `HOCKLEY*`, `MATHESON*`, `RONNQUIST*` and `SANDHU*`. Removing the footnote symbol from the normalized surname while preserving the original marker/meaning in evidence is correct. The other surname characters and the entire published remuneration remain unchanged. No vacation-payout amount or affected unmarked employee is inferred.

Reproduce the independent native review against the original cache and retained rendered-page files:

```sh
python scripts/continue_crowns_review_east_kootenay.py
```

This review modified only its own receipts and evidence. Candidate rows, source files, aliases and registration were not edited. Source-control clarification can remain a draft alongside the visible qualifications.
