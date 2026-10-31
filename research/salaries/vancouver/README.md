# Vancouver: calendar years and employee scope

Reviewed 30 October 2026. The accepted source is the **City's official open-data
export**, with 49,742 employee records for calendar years 2008–2025. Each year is
filed under its actual four-digit calendar label, with explicit January 1 and
December 31 dates. It is not assigned to an overlapping fiscal-year label.

## Source and validation

- [Official dataset and definitions](https://opendata.vancouver.ca/explore/dataset/employee-remuneration-and-expenses-earning-over-75000/).
- Exact CSV/JSON URLs, hashes, annual counts and totals are in `sources.json`.
- The complete unchanged CSV and JSON exports and the API annual controls are
  retained compressed under `raw/` for a deterministic offline rerun.
- Every field of every row agrees across CSV and JSON, with multiset comparisons
  preserving multiplicity. All 18 annual record counts and both monetary totals
  agree with the API's independent aggregation, allowing only sub-cent floating
  serialization differences in the API totals.
- These are consistency checks of the same official dataset. **The individual
  annual SOFI PDFs have not been reconciled.** The City's metadata says the
  published SOFI remains authoritative. Its financial-reports page and tested
  report downloads returned HTTP 403 in this environment. This limitation remains
  attached to the accepted open-data source in every year.

The importer preserves source cents, two negative expense entries, 2,410 missing
expense values, explicit zero values, and the published name spellings and
asterisks. The asterisks in 2012 and 2013 mark optional gratuity/vacation payouts;
they are not expanded into invented names. One published 2017 row is exactly
$75,000 despite the dataset's strict-over title. It remains in the import with a
specific exception, without changing the stated disclosure threshold.

## Corrections to the compiler snapshot

| Compiled edition label | Verified employee calendar year | Employee rows replaced | Council rows retained separately |
|---|---:|---:|---:|
| 2017/18 | 2018 | 2,738 | 0 |
| 2020/21 | 2020 | 3,003 | 11 |
| 2023/24 | 2023 | 4,083 | 11 |

The comparisons use the immutable compiled baseline, not whatever happens to be
in the most recent public export. Name case, spaces, ASCII hyphens and comma
spacing are normalized for comparison; pay is rounded using decimal half-even
rounding **for this comparison only**. Exact source names and cents are imported.
All employee name/pay multisets match. See `compiled-period-comparison.json`.

The replacement guards pin the exact 9,824 removed rows and require the matching
official source to be included in the build. The 22 rows whose position is exactly
`Mayor` or `Councillor` remain under their original **unverified compiled edition**
labels, classified as elected officials. A title merely containing "Mayor" (for
example, a member of the mayor's staff) does not reclassify an employee as elected.
The employee match is not proof of the council records' dates, values or identity.
They are neither deleted nor counted as accepted official employee rows.

The [official council dataset](https://opendata.vancouver.ca/explore/dataset/council-budget-and-expenses/)
provides exact CSV/XLS links for 2020 and 2023, but those file downloads also
returned HTTP 403 here. The council dataset mixes salary-related office budgets,
actual expenses and accruals. It must be checked against the council remuneration
report before substituting figures. This remains a source-specific follow-up.

This correction does not relabel other municipalities. Their own source periods
must be verified. The project now displays actual calendar years separately from
fiscal years while retaining clear warnings on unverified compilation labels.

## Reproduce

```bash
python3 scripts/import-vancouver-salaries.py
npm run build:salaries
npm run check:salaries
```

To process a new release, supply `--csv`, `--json` and `--controls` and review its
changes before updating the pinned source hashes. A hash change fails closed.
