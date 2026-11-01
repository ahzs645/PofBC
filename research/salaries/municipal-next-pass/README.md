# Filling the remaining municipal salary gaps

This pass starts from merged PR #25 (917,420 records; 57 of 161 current municipalities with accepted official records). Five research agents worked on different regions, prioritizing municipalities with no accepted official records and retaining historical source leads.

Accepted **2,535 official observations**, replaced **0 proved compiled observations**, and added **2,535 net records**. The app contains **919,955 records**. Official municipal coverage is now **92 of 161**, with **69** still lacking accepted official records.

## Newly covered municipalities

| Municipality | Employee calendar years | Council calendar years | Official records now |
| --- | --- | --- | ---: |
| City of Abbotsford | 2023, 2024 | 2023, 2024 | 968 |
| District of Barriere | 2023 | 2023 | 12 |
| Village of Belcarra | 2010, 2012, 2013, 2014, 2017, 2018, 2019, 2023, 2025 | 2019, 2023, 2025 | 51 |
| District of Chetwynd | 2024, 2025 | 2024 | 53 |
| District of Clearwater | 2023, 2025 | 2023, 2025 | 34 |
| District of Coldstream | 2021 | 2021 | 26 |
| City of Colwood | 2025 | — | 74 |
| City of Courtenay | 2025 | 2025 | 106 |
| Village of Cumberland | 2025 | 2025 | 27 |
| City of Dawson Creek | 2024 | 2024 | 96 |
| Township of Esquimalt | 2025 | 2025 | 93 |
| Town of Gibsons | 2025 | 2025 | 29 |
| Village of Gold River | 2025 | 2025 | 10 |
| Village of Harrison Hot Springs | 2021, 2022 | 2021, 2022 | 27 |
| District of Highlands | 2024 | 2024 | 11 |
| Town of Ladysmith | 2025 | 2025 | 46 |
| Town of Lake Cowichan | 2023, 2025 | 2023, 2024, 2025 | 34 |
| City of Langford | 2025 | 2025 | 137 |
| Village of New Denver | 2025 | 2025 | 6 |
| Northern Rockies Regional Municipality | 2024, 2025 | 2024, 2025 | 128 |
| District of North Saanich | 2025 | 2025 | 51 |
| City of Port Moody | — | 2024, 2025 | 14 |
| Town of Princeton | 2023 | 2023 | 24 |
| City of Richmond | — | 2024 | 9 |
| City of Rossland | 2025 | 2025 | 40 |
| Village of Sayward | 2024 | 2024 | 9 |
| Town of Sidney | 2025 | 2025 | 60 |
| District of Sparwood | 2024, 2025 | 2024, 2025 | 75 |
| District of Summerland | 2023 | 2023 | 67 |
| Sun Peaks Mountain Resort Municipality | 2024 | — | 15 |
| Village of Tahsis | 2025 | 2025 | 13 |
| District of Taylor | 2022 | — | 12 |
| District of Ucluelet | 2025 | 2025 | 25 |
| Town of View Royal | 2025 | 2025 | 41 |
| City of Williams Lake | 2024, 2025 | — | 112 |

## Source collections

| Region | Official records added | Cohorts |
| --- | ---: | ---: |
| [lower-mainland](lower-mainland/README.md) | 1,069 | 23 |
| [capital](capital/README.md) | 547 | 20 |
| [island](island/README.md) | 219 | 14 |
| [north](north/README.md) | 401 | 12 |
| [interior](interior/README.md) | 299 | 21 |

## Remaining work

The [complete queue](work-queue.csv) contains 166 tasks across this pass. The [copy/clarification candidates](acquisition-list.md) identify 15 actions that may need an existing electronic file, an adopted report, or an explanation. These can overlap the [detailed province-wide follow-up list](../municipal-audit/follow-up.md); do not add their counts.

See the [full 161-jurisdiction coverage table](../municipal-audit/coverage.md) for every remaining municipality, source links, accepted calendar years and retained unverified compiled editions. Regional districts are outside that denominator; Okanagan Falls is pending incorporation on November 6, 2026.

Named employee and council schedules remain separate. Reporting years come from the schedule, not upload dates. Remuneration follows source column definitions; expenses stay separate. Blank/dash amounts remain missing and explicit zeros/negative amounts remain as printed. Original values are never changed to balance a subtotal. Source residuals have visible warnings; unverified OCR and ambiguous rows remain held.

No requests or messages were sent. Check public archives and council attachments first, then request an existing adopted schedule or spreadsheet routinely; formal FOI remains a fallback after checking the relevant access route.

## Reproduce

Each collection README describes original retrieval and row-level verification. The offline publication checks are:

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
npm run preview:salaries -- --build
```
