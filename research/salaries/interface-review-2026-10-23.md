# Salary interface and source recovery — 23 October 2026

This follow-up is based on main commit
[`cc3539464d22f0c195f3cc0d486573120841302d`](https://github.com/ahzs645/PofBC/commit/cc3539464d22f0c195f3cc0d486573120841302d).
The earlier recovery was already merged there. The figures below measure this follow-up against
that commit, rather than counting the earlier Hydro and Public Accounts recovery again.

## Result

The rebuilt exports contain **692,951 disclosure records**, **76,508 more** than the starting
commit. Official-source provenance now covers **401,641 rows**. The remaining **291,310 rows
(42.0%)** still come from compiled disclosures and are labelled accordingly.

| Measure | Starting main | This follow-up |
|---|---:|---:|
| All disclosure records | 616,443 | 692,951 |
| Named records | 611,204 | 687,712 |
| Official-source records | 290,520 | 401,641 |
| Compiled records awaiting primary-source review | 325,923 | 291,310 |
| Canonical employers | 130 | 130 |
| Populated employer/year cells | 384 | 401 |
| Accepted normalized source files | 70 | 92 |
| Employers with at least one accepted official schedule | 9 | 10 |
| Duplicate-looking extra rows retained and flagged | 311 | 311 |

Counts are disclosure rows, not verified headcounts. Reporting periods, payment definitions,
thresholds, missing names and the scope of the source still matter when comparing years.

The exact totals and all 130 employer histories can be checked in
[coverage.json](../../public/salaries/coverage.json), the
[coverage inventory](coverage-inventory.md), and the generated
[source inventory](source-inventory.md).

## Interface findings and changes

| Finding | Resulting behavior |
|---|---|
| The landing headline counted only named records while calling them all disclosed records | The headline sums all employer records, including anonymous records |
| A name entered in the default position view could yield no results because only position labels were searched | Position groups search both employee names and titles; the matching group shows the filtered count and pay range |
| Surnames with spaces could be mistaken for surname plus given names | Surname-first search considers compound-surname boundaries; a comma selects the explicit surname/given-name boundary |
| Zero expenses were hidden by a truthiness check | A disclosed zero displays as $0; missing values and negative recoveries retain their meanings |
| The selected employer year and search filters did not survive a shared URL | Links preserve fiscal-year labels, sector and employer year; labels stay stable if older years are added |
| Empty years could look alike even when a report had been found or held | The UI distinguishes official sources, compiled data, located reports awaiting extraction, held reports and missing imports |
| Located reports were buried in research metadata | Employer/year disclosure details expose pending report links and the next validation step |
| Source links led only to the document | Every available physical PDF page reference survives employer, person and government exports and opens that page |
| A failed person-data shard could obscure valid employer search results | The name-search failure is local to the person results and includes a retry action |
| A long row of fiscal-year controls was awkward on small screens | A compact year dropdown is available on narrow screens, with wrapping and grid sizing corrections |
| Inclusive $75,000 thresholds were labelled “over $75,000” | Fraser and BCIT display “at least $75,000”; strict or unspecified comparisons retain their separate meanings |
| A truncated source name could look complete on the person page | Person pages explicitly warn when a contributing report publishes truncated names |

Name searches do not establish identity. Person grouping keys preserve all disclosed given names
and initials; the compound-surname search change does not merge different grouping keys. The
chart explains when it shows a year's highest individual record among several rows, rather than
an inferred total paid to one person.

## Newly accepted sources

### Fraser Health: ten annual employee schedules

The [official financial-reporting index](https://www.fraserhealth.ca/about-us/accountability/financial-reporting)
links the ten employee schedules for 2015/16–2024/25. These now provide **99,712 official rows**
across **2,113 physical PDF pages**. They replace 31,932 compiled rows in three snapshots and add
seven intervening or earlier periods, producing **67,780 net additional records**.

The new [Fraser importer](../../scripts/import-fraser-health-salaries.py) validates locked PDF
fingerprints, fiscal headings, page numbering, every employee line, reviewed row counts and
subtotals, and a second reconstruction from positioned PDF words. Both text representations use
Poppler, a shared decoding dependency documented in the collection methodology. Targeted page
images confirm negative expenses, explicit zeroes and summary edge cases.

The threshold is inclusive. Printed names, repeated names, dash expense cells, four negative
recoveries and the explicit zero remain as published. Displayed rows do not sum exactly to the
printed named totals; residuals fit the documented whole-dollar compatibility bound, but their
cause is not asserted and no amount is adjusted. The [collection README](fraser-health/README.md)
lists every source, yearly counts, residuals and reproduction commands.

### BCIT: eight more annual schedules

BCIT now has **10,624 official records** in nine accepted years: 2014/15, 2016/17–2018/19 and
2020/21–2024/25. Eight schedules are newly imported; the existing 970-row 2017/18 schedule gains
page provenance without changes to its names or monetary values. The published dataset grows by
**6,973 net records** after replacing the compiled snapshots.

The [BCIT importer](../../scripts/import-bcit-salaries.py) supports the observed report layouts
and compares every accepted name/pay/expense cell with PDF coordinates. The 2020/21 report
truncates many names and resets printed page numbering on its final employee page. Those source
limitations are recorded; physical PDF page numbers remain unambiguous. The inclusive threshold
and source residuals are preserved. See the [BCIT methodology](bcit/README.md) and
[official report index](https://www.bcit.ca/financial-services/financial-reports/).

The 2013/14 report was successfully retrieved, replacing the previous HTML-response blocker.
It is a 67-page image-only PDF. Its cover period is checked; employee extraction remains pending.

### BC Transit: four more years, including 2025/26

The [BC Transit extractor](../../scripts/extract-bc-transit-salaries.py) now accepts four further
years from the [official report index](https://www.bctransit.com/about/corporate-reports/financial/).

| New fiscal year | Rows | Sum of remuneration | Sum of disclosed expenses | Rows minus printed named totals: pay / expenses |
|---|---:|---:|---:|---:|
| 2015/16 | 177 | $16,304,943 | $507,681 | $0 / $0 |
| 2016/17 | 219 | $19,961,793 | $637,388 | −$4 / $0 |
| 2019/20 | 359 | $33,190,139 | $820,227 | $0 / $0 |
| 2025/26 | 1,000 | $102,154,713 | $1,134,613 | $0 / $0 |

That is **1,755 new records**. Together with the unchanged 385-row 2020/21 import, the accepted
collection contains 2,140 records. Scanned schedules retain two OCR passes, complete employee-page
image review and explicit corrections. The native 2016/17 schedule is checked against a separate
coordinate extraction. Source rounding residuals remain visible.

The latest PDF has a stale “DRAFT” string in internal metadata. Its official index link and signed
management and board approval pages, dated 24 July 2026, establish why this version was accepted.
See the [Transit review](bc-transit/README.md) and
[all-15-report survey](bc-transit/source-survey-2026-10-23.json).

## Source and build safeguards

Accepted manifests and the handwritten source backlog now feed one generated source register.
Its employer/period/document key lets a shared PDF be accepted for one employer while held for
another. An old handwritten “imported” label cannot certify a source without an accepted manifest.
Source-only periods enter the coverage year list even before rows are accepted. Held reports
retain their held state whether the manifest names one employer or an employer list.

Every accepted source must declare its disclosure scope. A partial executive-only source cannot
silently replace an existing employee partition; an exceptional replacement requires an explicit
reviewed decision with a reason and every affected source ID. The build checks both remuneration
and disclosed-expense sums, source hashes, row counts and physical page values before replacing
published output. The immutable compiler snapshot is unchanged.

The complete export checker compares row multisets, including page provenance and duplicate
multiplicity, across normalized source inputs, employer histories, person shards and atlas files.
The appended physical-page field changes employer/person export metadata to schema version 2:

| Export | Row fields |
|---|---|
| Employer history | name, position, remuneration, expenses, year index, source ID, physical PDF page or null |
| Person shard | name, position, remuneration, expenses, employer index, year index, source ID, physical PDF page or null |
| Atlas employer/year | name, position, remuneration, expenses, source ID, physical PDF page or null |

The [salary CI workflow](../../.github/workflows/salaries.yml) tests parser fixtures and salary
behavior, rebuilds the committed inputs offline, reconciles the exports, rejects stale generated
files and builds the salary interface. Live PDF downloads and OCR are separate reviewed tasks.

## Remaining work

- **PHSA and Island Health:** 20 exact employee-report links, ten years each (2015/16–2024/25),
  are recorded from their official indexes. Their rows are not yet accepted. Verify report periods,
  scope, thresholds, all employee cells and subtotals before import.
- **BC Transit:** ten linked periods remain unaccepted. Every PDF has been downloaded and hashed;
  employee schedules generally require OCR even where appended financial statements have text.
- **BC Hydro and Powerex 2024/25:** the previously documented discrepancies remain held. Neither
  employee data nor balancing adjustments were invented. Powertech's accepted schedule stays separate.
- **Hydro 2010/11–2011/12 and BCIT 2013/14:** scanned sources remain OCR work. The source register
  now includes explicit BC Hydro mapping for the reviewed older Hydro employee headings, without
  assigning unverified subsidiary coverage.
- **Fraser 2025/26, additional BCIT/UNBC years, BCI and BC Pension employee schedules:** still require
  the appropriate employee source and validation. Executive or board tables cannot stand in for them.
- **The other employers:** 120 of 130 employers still lack an accepted official schedule. Their
  compiled records remain visible with the review-pending label. A new employer with no existing
  rows also needs an explicit employer inventory entry; source discovery alone does not create one.

The [central research report](README.md) retains the earlier findings, historical archive leads,
source-specific limitations and prioritized follow-up work.

## Verification and how to inspect

The final dataset reconciles **692,951 rows, 165 atlas files, 461 person shards and 92 accepted
source files**. A repeated offline build produced identical hashes for all **761 generated files**.
The complete JavaScript suite passes **47 test files**; Python parser regression tests pass
**38 cases**, including with third-party site packages disabled. The salary production preview
build succeeds.

```sh
npm run build:salaries
npm run check:salaries
npm test
python3 -S -m unittest discover -s scripts -p 'test_*.py'
npm run preview:salaries -- --build
npm run preview:salaries
```

The preview serves the actual salary components and the committed data at `http://localhost:4173/`.
Use `/mobile.html` for its 390-pixel viewport. It does not deploy the site and does not require
the unrelated licensed artwork-font build.

The existing public salary interface was inspected in a browser. This environment's cloud browser
could not reach the local revised preview (connection refused for localhost; blocked client access
for the workspace network address). Therefore live interaction and narrow-screen visual QA of the
revised branch remain unverified; passing unit tests and a bundle build are not substitutes for
that check. The full site build was not run because its required licensed macOS Helvetica source
is absent from this Linux environment. The salary-only build avoids that unrelated dependency.
