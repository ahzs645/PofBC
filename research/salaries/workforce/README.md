# BC Public Service workforce companion

The curated input is `PSA-2024-42006.json`. The official source is [FOI release PSA-2024-42006](https://docs.openinfo.gov.bc.ca/Response_Package_PSA-2024-42006.pdf).

The first and third PDF pages contain the all-employees and Victoria-office tables. Pages 2 and 4 repeat the corresponding values alongside charts; they do not add observations. The input contains exactly 16 population/year observations and 32 transcribed measure values. The tables and chart pages were checked visually. Each population retains its exact source description and page references.

Run `node scripts/build-workforce.mjs` to produce the separate public JSON and CSV downloads. Run `node scripts/build-workforce.mjs --check` to check that the checked-in downloads match the input. Generation does not fetch the PDF and does not include timestamps, so the artifacts are reproducible. Tests pin the transcribed values, provenance and material limitations.

## Interpretation

- Preserve the labels **Average HeadCount** and **Average Salary**. Calculation methods have not been established; Average Salary must not be relabelled as actual earnings, annualized salary or an average of PofBC payment records.
- Preserve the source's year labels without assuming calendar or fiscal reporting periods. Period type is `unverified`; period start and end are `null`. No associated request metadata establishing these definitions was located during review.
- This is the **BC Public Service**, not the whole BC public sector. Victoria-office employees are a subset of all employees. The populations must never be summed.
- The 2019 Victoria Average HeadCount is **21,405**, as shown on both pages 3 and 4. Its rise and subsequent fall remain unexplained. Keep the printed value; do not interpolate or silently correct it.
- The PDF uses a dollar symbol. CAD is inferred from the British Columbia government context, and the currency field records that basis explicitly.
- These observations are not named individual records. They remain outside salary payment indices, rankings, totals, threshold coverage and record counts. The existing government fiscal-year FTE series is also a distinct measure.
- The statistics can supply broader workforce context, but do not establish how many employees are missing from any threshold-based disclosure list. A rising disclosure count alone does not establish headcount growth.

The CSV includes both populations, exact measure labels, the unknown method and period fields, inferred-currency basis, source URL and PDF pages. Blank period boundaries mean unknown, not a zero-length interval.

## Questions to resolve before comparing with annual payments

1. What start date, end date and extraction date apply to each year label? Does 2024 represent a complete period or a partial period?
2. How is **Average HeadCount** calculated: daily or monthly snapshots, pay-period averages, unique people or another method? How are employees with multiple appointments counted?
3. Which employee groups and employment statuses are included, including regular, auxiliary, part-time and leave statuses? Are these definitions constant across the series?
4. Does **Average Salary** use annualized salary rates, actual payroll earnings or another amount? What numerator, denominator and weighting are used, and how are part-time employment, overtime, allowances and benefits treated?
5. What office-location definition produces the Victoria population? How are transfers, remote work and changes in office assignment handled?
6. What explains the Victoria headcount of 21,405 in 2019 and its subsequent decrease? Are revised values or newer releases available under the same definitions?

Until these definitions are established, the series can be displayed under its
original labels but should not be used to estimate missing payment records, calculate
total payroll by multiplying the two averages, or replace fiscal-year FTE statistics.
