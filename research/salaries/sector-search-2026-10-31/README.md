# Salary histories and source follow-up

Reviewed 31 October 2026 (America/Vancouver). Six research agents searched municipalities, health, schools, postsecondary institutions, Crown corporations, government, police and regional districts. This is a source-discovery and verified-import pass; it does not establish complete historical coverage.

This release accepts **42,536 official observations**, replaces **6,118 compiled observations** through reviewed fiscal replacements and a hash-pinned InBC period correction, and adds **36,418 net records**. The dataset grows from **881,002 to 917,420**. Exact cross-calendar municipal replacement decisions remain separately hash-pinned; partial overlaps are retained.

| Collection | Official records added | Cohorts |
| --- | ---: | ---: |
| [sector-municipal](../sector-municipal/README.md) | 411 | 14 |
| [sector-health](../sector-health/README.md) | 11,494 | 2 |
| [sector-schools](../sector-schools/README.md) | 10,568 | 32 |
| [sector-education](../sector-education/README.md) | 13,527 | 6 |
| [sector-crowns](../sector-crowns/README.md) | 41 | 3 |
| [sector-government-police](../sector-government-police/README.md) | 6,495 | 4 |

## Start here

- [Acquisition and clarification list](acquisition-list.md): specific routine-copy and explanation candidates; no requests sent.
- [Complete processing and historical research queue](work-queue.csv): one row per actionable task, with source links, periods and next action.
- [Machine-readable release reconciliation](release.json): every accepted cohort, original/data hashes, warnings and baseline comparison.
- [Municipality coverage](../municipal-audit/coverage.md) and [existing municipal requests](../municipal-audit/follow-up.md): province-wide municipal roster and deeper source tasks.

## Coverage and assumptions

A linked document is a lead until its internal reporting period, named schedule, rows and monetary definitions have been checked. School, health and university fiscal periods differ from calendar municipal periods. Upload dates and archive labels do not establish salary years. These are payment disclosures, not annual base salary rates or complete employee rosters.

Employee, trustee, council, board and executive scopes stay distinct. Printed dashes and blanks remain missing; numeric zeros and negative expenses remain as disclosed. Metro Vancouver remuneration combines salary with benefits/other compensation. Nine Metro rows with an undisclosed component remain held, and the partial cohorts carry visible warnings. Small unresolved published subtotal residuals are retained and disclosed; no balancing edits or rounding explanation is inferred.

Official SFU and SD42 complete fiscal schedules replace the corresponding compiled partitions after scope review. SD42 includes trustee schedules, and the two compiler spellings are joined under the official district identity. Compiler name/title enrichments are not carried into official records without source support. Three SFU years with material source-control discrepancies remain held. See [replacement review](replacement-review.md).

The municipal denominator remains 161 current jurisdictions, excluding regional districts. 104 still lack accepted official records. Metro Vancouver is a regional district. New school and regional-district discovery inventories are broader than the employers with records in the app.

## Research areas

- [municipal findings and receipts](municipal/README.md) — 53 follow-up tasks.
- [health findings and receipts](health/README.md) — 32 follow-up tasks.
- [schools findings and receipts](schools/README.md) — 139 follow-up tasks.
- [education findings and receipts](education/README.md) — 123 follow-up tasks.
- [crowns findings and receipts](crowns/README.md) — 42 follow-up tasks.
- [government-police findings and receipts](government-police/README.md) — 55 follow-up tasks.

## Reproduce

Use each collection README to download/re-extract hash-pinned original reports. The application build itself is offline:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
node --test scripts/salary-data.test.mjs src/salaries/*.test.js src/government/salaries.test.js
npm run compare:municipal-periods
npm run build:salaries
npm run check:salaries
npm run audit:municipal-salaries
npm run follow-up:municipal-salaries
npm run review:sector-salaries
npm run preview:salaries -- --build
```

Original extraction, rendered review, independent-reader agreement and source residuals are retained per collection. Queue CSV files are generated from the six normalized handoffs. The frozen baseline is the previously deployed main commit; rebuilds assert that official additions, compiled replacements and the total change reconcile.
