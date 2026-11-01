# School District 42 original fiscal salary histories

Reviewed October 31, 2026 (America/Vancouver). This collection contains **10,568 published observations**: 10,446 employees and 122 elected trustees, in 32 separately scoped cohorts from 16 original district reports. Fiscal years end June 30; their start is July 1 of the preceding year.

| Fiscal years, by ending year | Employee observations | Trustee observations |
| --- | ---: | ---: |
| 2005, 2006, 2010 | 607 | 24 |
| 2014–2026 | 9,839 | 98 |
| Total | 10,446 | 122 |

The official [district finance archive](https://www.sd42.ca/financial-information/) links every ending year 2005–2026. All 22 originals were retrieved and fingerprinted. Ending years 2007–2009 and 2011–2013 are scans: OCR discovery now covers all their 296 physical pages, but their rows are held until complete source and control review. Discovery evidence is under [the schools inventory](../sector-search-2026-10-31/schools/README.md).

`reviewed-inputs.json` pins original hashes, exact cohort counts, component sums, printed controls and residuals. `sources.json` contains app-compatible source metadata; each cohort has deterministic compressed rows and source evidence. Records use `[employerSlug, name, position, remuneration, expenses, physicalPdfPage]`. The `school-trustees` category is separate from `employee-remuneration`; no employee disclosure threshold is applied to trustees.

Reproduce with the existing cache:

```sh
python3 scripts/sector_schools_sd42.py --cache-dir /tmp/pofbc-schools
python3 -m unittest discover -s scripts -p 'test_sector_schools.py'
```

For a fresh cache, use `--download`; use `--output-dir /tmp/rebuilt-schools` for a comparison without changing the collection. Dependencies are Python, PyMuPDF and Poppler `pdftotext`. A changed original fingerprint, unexpected period, row mismatch, unparsed row, cohort count, monetary sum or printed control causes the rebuild to stop. A second build and independent reviewer reproduced every generated file exactly.

Every complete source row, amount, order, multiplicity and physical page is corroborated against independently grouped PyMuPDF word coordinates. Table layouts and joined name/title cases were checked against rendered original pages. The source preserves remuneration separately from expenses; negative expenses remain negative, explicit zero remains zero, and dashes or blanks remain null. Disclosed names, initials and titles are retained. These are payments rather than annual base rates or a complete workforce roster.

Specific source details:

- Employee schedules ending 2014–2017 omit job titles; positions remain null.
- Some name cells in 2006 and 2010 include printed numeric tokens, such as `23` or `11`. Those tokens are retained; no identity correction is inferred.
- Footnote asterisks remain in evidence and are removed from display names. Long name/title boundaries in 2025–2026 are explicit reviewed cases in the importer. The clipped 2025 name `PENACERRADA, CARLO GATCHALI` is retained as disclosed, without expanding its ending.
- The 2024 Pogrebinsky expense is **−$252.96**, as printed in parentheses. A positive compiled amount does not override it.
- All pre-2025 named-cohort remuneration and expense controls agree exactly. For 2025 employee rows, sum minus printed controls is **+$17 / −$5**; trustees **$0 / +$1**. For 2026 employees it is **−$8 / −$9**; trustees **−$1 / −$1**. These four sources carry public warnings. Published amounts are retained without adjustment, and no cause is asserted for the differences.

The original definition includes salary, wages, taxable benefits and certain other compensation. Supporting notes distinguish cash-basis SOFI payments from accrual financial statements; some employee remuneration includes leave payouts or retirement allowances. Under-threshold aggregate payroll, employer premiums and supplier payments are excluded from individual rows.

The importer uses `maple-ridge-pitt-meadows-school-district` for new sources. It does not modify either compiled employer slug or delete compiled rows. [Primary identity evidence](../sector-search-2026-10-31/schools/sd42-identity-evidence.json) connects the separate Ridge-Meadows compiler label to the SD42 employee schedule; [the overlap report](../sector-search-2026-10-31/schools/sd42-compiled-overlap.json) records category-specific cautions for central replacement review.
