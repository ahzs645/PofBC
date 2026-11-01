# Municipal historical disclosure continuation

This document records PR #28 at merge `0f6952b`. Later additions have their own release reviews. `npm run review:municipal-history` now verifies these frozen source inputs and their original reconciliation, preserving this historical snapshot when the live dataset grows.

This pass accepts **6,273 official observations** from **119 original reports**, covering **119 municipality-years**. It replaces **0 proved compiled observations**, for **6,273 net additional records**. The dataset grows from **919,955 to 926,228**.

Official municipal coverage is **101 of 161**, including **100** with employee schedules. **60** current jurisdictions still lack accepted official records. Historical additions extend coverage at previously represented municipalities as well as filling new jurisdictions.

## Histories added

| Municipality | New employee calendar years | New council calendar years | Added observations |
| --- | --- | --- | ---: |
| City of Colwood | 2012, 2016, 2018, 2021 | 2012, 2016, 2017, 2018, 2021 | 171 |
| City of Courtenay | 2020, 2021, 2022, 2023, 2024 | 2020, 2021, 2022, 2023, 2024 | 475 |
| City of Dawson Creek | 2017, 2019, 2020, 2021, 2022, 2023 | 2017, 2019, 2020, 2021, 2022, 2023 | 408 |
| City of Langford | 2010, 2021 | 2010, 2021 | 98 |
| City of Merritt | 2025 | 2025 | 53 |
| City of Port Moody | 2019, 2020, 2021, 2022, 2023, 2024, 2025 | 2020, 2021, 2022, 2023 | 1,270 |
| City of Richmond | 2024 | — | 1,231 |
| City of Rossland | 2015, 2021, 2022, 2024 | 2015, 2021, 2022, 2024 | 106 |
| City of Trail | 2022, 2023, 2024 | 2022, 2023, 2024 | 157 |
| City of Williams Lake | 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 | 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 | 494 |
| District of Chetwynd | 2018, 2019 | 2018, 2019 | 43 |
| District of Clearwater | 2024 | 2024 | 17 |
| District of Lantzville | 2018, 2019, 2020, 2025 | 2018, 2019, 2020, 2025 | 50 |
| District of North Saanich | 2020, 2021, 2023 | 2020, 2021, 2023 | 107 |
| District of Oak Bay | 2024 | — | 98 |
| District of Sparwood | 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 | 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 | 311 |
| District of Tofino | 2012, 2013, 2021 | 2012, 2013, 2021 | 43 |
| District of Ucluelet | 2023, 2024 | 2023, 2024 | 43 |
| Northern Rockies Regional Municipality | 2015, 2017, 2019, 2020, 2021, 2022, 2023 | 2015, 2017, 2019, 2020, 2021, 2022, 2023 | 390 |
| Town of Gibsons | 2021, 2022, 2023, 2024 | 2021, 2022, 2023, 2024 | 86 |
| Town of Ladysmith | 2021, 2022, 2023 | 2021, 2022, 2023 | 128 |
| Town of Lake Cowichan | 2024 | — | 7 |
| Town of Port McNeill | 2021 | 2021 | 8 |
| Town of Princeton | 2022 | 2022 | 25 |
| Town of Sidney | 2021, 2022, 2023, 2024 | 2021, 2022, 2023, 2024 | 195 |
| Village of Cumberland | 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 176 |
| Village of Hazelton | 2024 | 2024 | 8 |
| Village of Lytton | 2021, 2023 | 2021, 2023 | 16 |
| Village of Port Clements | 2025 | 2025 | 6 |
| Village of Sayward | 2021, 2022 | 2021, 2022 | 17 |
| Village of Tahsis | 2019, 2020, 2021, 2022, 2023 | 2019, 2020, 2021, 2022, 2023 | 36 |

Verified aggregate-only periods: Village of Lytton 2022. The source explicitly reports no named employee cohort; aggregate payroll is not converted into individual records.

## Source decisions and corrections

The new inputs contain 5,483 employee and 790 elected-official observations. 92 records have no separately published name field; their actual printed positions or labels and payments remain available without inventing a name or joining identities across years.

Periods come from the named schedule and original report, not the upload URL or meeting date. Each accepted source has original and normalized hashes, physical pages, row-level corroboration and rendered review. PDF OCR overlays are distinguished from native tables; two configurations of one OCR engine are not called independent engines. Missing or malformed expense amounts remain null with exact source evidence. Source columns determine remuneration; expense-inclusive totals are not pay, and undefined benefits/grant components are not silently added.

Faithful published rows can carry unresolved source-control qualifications. Each such source has a visible warning identifying known sums, printed controls, scope differences and missing components. No amounts are changed to balance totals; an unknown component is not assigned zero. Partial employee cohorts have explicit completeness=false flags and cannot silently replace compiled partitions.

This pass also restores 8 published initials dropped by an old text filter and corrects 2 prior source-control scope descriptions. Counts and monetary cells in those earlier inputs remain unchanged. [Archived originals, exact amendments and independent review](corrections/interior-initials/central-review.md) and [control-scope review](corrections/north-expense-scope/central-review.md) preserve what PR27 originally published; the frozen release validator verifies the archival bytes and exact permitted repairs.

## Regional and independent reviews

- [lower-mainland sources, histories and remaining blockers](lower-mainland/README.md)
- [capital sources, histories and remaining blockers](capital/README.md)
- [island sources, histories and remaining blockers](island/README.md)
- [north sources, histories and remaining blockers](north/README.md)
- [interior sources, histories and remaining blockers](interior/README.md)
- [resolved sources, histories and remaining blockers](resolved/README.md)
- [Independent interior qualified history review](reviews/interior-qualified-history.md)
- [Independent island native review](reviews/island-native.md)
- [Independent langford 2010 ocr review](reviews/langford-2010-ocr.md)
- [Independent lantzville 2025 ocr review](reviews/lantzville-2025-ocr.md)
- [Independent north history review](reviews/north-history.md)
- [Independent port moody 2025 review](reviews/port-moody-2025.md)
- [Independent resolved payment scopes review](reviews/resolved-payment-scopes.md)
- [Independent richmond 2024 pages 47 53 review](reviews/richmond-2024-pages-47-53.md)
- [Independent richmond 2024 pages 54 61 review](reviews/richmond-2024-pages-54-61.md)
- [Independent richmond 2024 pages 62 75 review](reviews/richmond-2024-pages-62-75.md)
- [Independent williams lake 2019 review](reviews/williams-lake-2019.md)

## What remains

The [remaining queue](work-queue.csv) contains 308 tasks in this pass; the [copy/clarification list](acquisition-list.md) contains 73 candidates. These may overlap older lists: do not add their counts. Use the [current province-wide coverage table](../municipal-audit/coverage.md) for all 161 jurisdictions and exact accepted years. Located archive years remain leads until each original and cohort is verified; this review does not claim every historical report has been found.

No municipality was contacted and no FOI request or fee was submitted. Search public finance pages and council attachments first; request an existing adopted report or native table routinely if retrieval fails, with formal access as a fallback. Regional districts remain outside the municipal denominator, shíshálh is a separate governance case, and Okanagan Falls is pending incorporation on November 6, 2026.

## Reproduce

Use each collection guide for pinned-original extraction. Offline publication checks:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
node --test scripts/salary-data.test.mjs src/salaries/*.test.js src/government/salaries.test.js
npm run compare:municipal-periods
npm run build:salaries
npm run check:salaries
npm run audit:municipal-salaries
npm run follow-up:municipal-salaries
npm run review:sector-salaries
npm run review:municipal-wave
npm run review:municipal-history
npm run preview:salaries -- --build
```
