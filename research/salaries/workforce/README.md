# BC Public Service workforce sources

This data is independent of named compensation disclosures. No rows in these files
are employee payment records, and none enter salary rankings, payment totals,
named-earner counts, identity linkage or employer disclosure completeness estimates.

## FOI average headcount and salary

Official source: https://docs.openinfo.gov.bc.ca/Response_Package_PSA-2024-42006.pdf

The original four-page PDF is retained beside its transcription. SHA-256:
`46ae5c7fbbbd1db9e3eac581cd89685ce14d9718b94a24d2ee943677bb4989dc`.
All four pages were rendered and visually inspected on November 6, 2026. The PDF
has image-only tables; text extraction alone is insufficient to verify its values.

- Page 1: all-employees Average HeadCount and Average Salary, 2017–2024.
- Page 2: all-employees telework schedules, 2022–2024.
- Page 3: Victoria-office Average HeadCount and Average Salary, 2017–2024.
- Page 4: Victoria-office telework schedules, 2022–2024.

Pages 2 and 4 are **not duplicate headcount/salary tables**. They are not imported
into the headcount/salary series. The previous draft's complete Victoria series
was incorrect. In particular, 2019 headcount is **13,972.25**, not 21,405, and 2024
headcount is **17,564.38**. All Victoria headcount and salary decimals are retained.

The search cutoff has not been independently verified from request metadata. The
PDF does not state reporting-period boundaries. Do not label 2024 as a complete
calendar year.
The release does not explain calculation methods, calendar/fiscal periods, extraction
dates, annualized versus earned salary, weighting, employee statuses or office assignment
rules. Original measure names are retained; currency CAD is inferred from context.
Do not multiply average headcount by average salary to estimate payroll. Victoria is
included in all employees, so these populations must not be added. FTE is another measure.

Rebuild and test offline:

```
node scripts/build-workforce.mjs
node scripts/build-workforce.mjs --check
node --test scripts/workforce.test.mjs src/salaries/workforce.test.js
```

## BC Stats Workforce Profiles archive

Official catalogue: https://catalogue.data.gov.bc.ca/dataset/bc-public-service-workforce-profiles

`profiles/manifest.json` identifies the exact 30 public CSVs, source URLs, resource IDs,
row counts and SHA-256 digests. `profiles/raw/` contains their unmodified bytes as
retrieved November 6, 2026. There are **10,435 source rows**, of which **111 are ministry
lookup rows**, leaving 10,324 aggregate profile rows. These are not 10,435 employees.
The catalogue has an additional empty-URL entry for WP2024_Ind_Progress; it is not a
second source and is excluded. Editions: 2018 (6 tables), 2020, 2022 and 2024 (8 each).

Tables cover employee counts, population/workforce representation comparators,
Indigenous/protected-group progress, leadership, occupation and region representation,
hiring, flows and ministry keys. The original columns and string values are preserved;
S, NA and blanks are not zero and are never reconstructed. Source years are edition
labels; historical comparison columns refer to other years. Different measures and
groups have different or overlapping denominators. Ministry keys are edition-specific.
The archive is not harmonized across reorganizations. The viewer deliberately shows
source tables and explicit labels rather than computing unsupported totals or rankings.

The catalogue describes demographics gathered in BC Stats corporate surveys and
comparators from federal reports. Consult its linked official methodology before
interpreting representation, shortfalls or counts. These profile employee counts
must not be substituted for the FOI average headcounts, fiscal-year FTE or payment lists.

The public JSON preserves source rows and provenance per table. The viewer offers
filtering, 25-row pages, official CSV links and the complete JSON download, separately
from FOI downloads. Raw CSV files are not regenerated or spreadsheet-sanitized: they
are the official original files. Any future generated CSV should escape formula cells.

```
node scripts/build-workforce-profiles.mjs
node scripts/build-workforce-profiles.mjs --check
node --test scripts/workforce-profiles.test.mjs
```

Both builds are deterministic and use only the committed public-source snapshots.
The profile build verifies all source digests before parsing and rejects changed source
counts or malformed row widths. A future refresh must deliberately update the manifest,
expected coverage, review and tests; do not silently mix editions or reinterpret symbols.
