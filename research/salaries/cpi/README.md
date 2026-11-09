# B.C. consumer price index for inflation-adjusted salaries

`bc-cpi-all-items-annual.csv` is the annual average **All-items** consumer price index for
**British Columbia** (2002=100), 1995–2025, from Statistics Canada,
[Table 18-10-0005-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000501)
(vector v41694760), downloaded 9 November 2026 as
`https://www150.statcan.gc.ca/n1/tbl/csv/18100005-eng.zip`
(SHA-256 `9b52900a2fc26b7e11ac22d819b3164678fe9a2a5ff241c5db085816a5fe8e0a`). Statistics Canada
Open Licence.

`src/salaries/inflation.js` carries the same values; `src/salaries/inflation.test.js` checks that the
two agree. When a new annual average is published, add the year to both.

How a disclosure period is priced:

- A calendar year (`2024`) uses that year's average.
- A fiscal year (`2024/25`, April to March, or July to June for school districts) uses three quarters
  of the first year's average and one quarter of the next year's. This is an approximation; monthly
  CPI would be more exact for July–June years.
- A period after the latest published annual average uses the latest one, so the most recent
  periods are shown at roughly their own prices rather than projected forward.

Inflation-adjusted figures are a reading aid: they say what an amount would buy at the base year's
prices across all goods and services in B.C., not what the job would pay today.
