# Council-pay time-series expansion

Reviewed November 4, 2026. This follow-up adds **148 office observations and 203 named payment rows** to the first reviewed collection. The complete companion now contains **578 office observations, 385 named payments and 54 source records**. All figures are nominal CAD.

## Newly added office years

The two measure columns remain separate. A comparative survey does not establish an adopted annual-rate schedule; represented years do not imply that every day or every source edition is covered.

| Municipality | Annual-rate years added | Comparative-survey years added | Added observations |
| --- | --- | --- | ---: |
| Abbotsford | 2007–2015 | 2018, 2025 | 24 |
| Chilliwack | — | 2017–2018, 2025 | 6 |
| Coquitlam | — | 2015, 2023, 2025 | 6 |
| Delta | — | 2015, 2017–2018, 2023, 2025 | 10 |
| Kamloops | — | 2017–2018, 2023, 2025 | 8 |
| Kelowna | — | 2015, 2017–2018, 2023, 2025 | 10 |
| Langley Township | — | 2015, 2017–2018, 2023, 2025 | 10 |
| Maple Ridge | — | 2015, 2018, 2023, 2025 | 8 |
| Nanaimo | 2003 | 2015, 2017–2018, 2023, 2025 | 12 |
| New Westminster | — | 2015, 2018, 2023, 2025 | 8 |
| North Vancouver City | 2022 | — | 2 |
| North Vancouver District | — | 2017–2018, 2023, 2025 | 8 |
| Prince George | — | 2017 | 2 |
| Richmond | — | 2015 | 2 |
| Saanich | — | 2015, 2017–2018, 2023, 2025 | 10 |
| Surrey | — | 2015 | 2 |
| Vancouver | 2016–2018 | — | 6 |
| Victoria | 2022, 2024 | 2017–2018, 2023, 2025 | 12 |
| West Vancouver | — | 2023 | 2 |

Abbotsford's 2007–2011 additions are ten calendar-year slices of two annual rates expressly stated to apply from January 1, 2007 through November 30, 2011. They retain the original interval and $100 published precision. The separately recorded December 1, 2011 rates preserve that transition. No CPI back-calculation or payroll proration was used.

Vancouver's councillor annual-rate coverage is now continuous by year from **1995–2026**; its mayor-rate history still has earlier gaps. The 2016 bylaw expressly sets the mayor rate at $161,308.02 and councillor rate at $80,028.80. The mayor multiplier begins in 2017, so it must not be used to recalculate the stated 2016 amount. The annual supplement and one-time payments remain separate.

The [additional municipal source notes](official-additional-timeseries-notes.md) identify the original source tables, source-year versus publication-date distinctions, reported precision, acting-pay estimates, tax-treatment qualifications and excluded comparisons. The adopted-rate coverage for Victoria remains 2022 and 2024; its survey observations for other years are not substituted into that series. North Vancouver City and District remain distinct.

## Vancouver named payments

The new schedules cover every year **2004–2019**, with **104 rows for 2004–2011** and **99 rows for 2012–2019**. Combined with the existing schedules, named-payment coverage is **1994–1995 and 1997–2025**, a continuous 29-year span from 1997. The erroneous 1996 report remains held; years before 1994 remain unfilled.

Source rows are not a count of unique people. Sullivan has separate mayor and councillor rows in 2005, and the 2018 report prints two council-term subtables with separate totals. Names and source spellings remain unchanged; no new identity link is inferred. From 2004–2015, local expenses, transportation allowance and travel/conferences are separately printed and are each counted once. Later tables include transportation in local expenses and publish discretionary office budgets separately; those budgets are excluded from personal remuneration and the displayed expense sum.

Detailed evidence: [2004–2011 notes](vancouver-2004-2011-source-notes.md), [2004–2011 transcription](vancouver-2004-2011-payments-transcription.json), and [2012–2019 transcription](vancouver-2012-2019-payments-transcription.json).

## Source precision and reconciliation

The expanded collection has **129 printed numeric column controls**: **114 exact** and **15 with documented whole-dollar differences**. The original 61 exact controls remain exact. A qualified difference is never corrected by altering a source cell. The validator requires explicit evidence, integer-dollar cells and a bound of `(disclosed rows + 1) × $0.50`. That bound tests consistency with independent rounding and does not prove a source is free of other errors. The 2006 rounding interpretation remains explicitly an inference.

The 2004 SOFI supplies cent-precision values and exact totals. All 44 individual values in the alternate annual report match nearest-dollar rounding, but its travel aggregate differs by $1 from the rounded SOFI total; both editions are documented. The 2010 and 2011 travel appendices independently validate 22 exact-cent person totals and their published rounded equivalents. These appendix figures remain validation evidence, not extra payments.

The generated [validation receipt](validation.json) records printed totals, disclosed sums, differences, bounds, qualification reasons, independent precision checks, input/output hashes and the prior-record preservation check. The [coverage file](coverage.json) contains separate municipality/role/measure series and their internal year gaps.

## Preservation and review

All **430 prior office observations and 182 prior named payments** retain protected amounts, components, roles, years, source assignments and IDs; all 25 earlier primary source URLs remain intact. Existing main salary records, name links, indexes and disclosure evidence are outside the companion writes. The [expansion baseline](timeseries-expansion-baseline.json) pins the previous companion commit and its protected field digest.

The reproducible builder and 42 focused data/interface/navigation tests pass locally. The regular GitHub salary workflow reruns the full salary suites, frozen historical gates, current-export reconciliation and preview build on the published commit. The earlier desktop/phone visual-review limitation remains: browser connections could not reach the scratch preview. Successful compilation is not a claim of interactive visual verification.

## Remaining time-series gaps

- Recover the rest of CBC 2019 and other province-wide survey editions.
- Extend Prince George, Richmond, Surrey, Burnaby and the other municipalities with their own dated schedules and annual SOFI tables. New comparative observations provide anchors but do not establish full annual histories.
- Find the corrected Vancouver 1996 schedule and records before 1994.
- Resolve source-specific conflicts, including Saanich's 2021 survey/rate difference and Nanaimo's $35,438 versus $35,447 figures, without replacing either source silently.
