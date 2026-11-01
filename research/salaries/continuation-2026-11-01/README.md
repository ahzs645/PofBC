# Salary source continuation — 1 November 2026

This is the historical PR #34 release as merged. Its source inputs and arithmetic are verified with `npm run review:salary-continuation` without rewriting the released totals when later records are added. See the [current coverage comparison](../sunshine-lists/comparison.md) for the latest dataset and the [NIC integration](../north-island-history/README.md) for the subsequent additions.

This pass accepts **94,819 official observations** from **184 original reports**, covering **184 employer-years**. After **10,830 reviewed compiled replacements**, the dataset grows from **926,228 to 1,010,217** (**83,989 net records**).

## Collections

| Collection | Official observations | Accepted cohorts | Original reports |
| --- | ---: | ---: | ---: |
| [continuation-municipal](../continuation-municipal/README.md) | 1,216 | 37 | 20 |
| [continuation-health](../continuation-health/README.md) | 190 | 17 | 17 |
| [continuation-schools](../continuation-schools/README.md) | 10,664 | 73 | 37 |
| [continuation-education](../continuation-education/README.md) | 19,137 | 36 | 36 |
| [continuation-education/supplemental](../continuation-education/supplemental/README.md) | 2,078 | 5 | 5 |
| [continuation-crowns](../continuation-crowns/README.md) | 39,063 | 44 | 44 |
| [continuation-government-police](../continuation-government-police/README.md) | 22,471 | 32 | 25 |

## Coverage

| Sector | Records before | Records after | Official records after | Employers after |
| --- | ---: | ---: | ---: | ---: |
| Crown corporations | 109,942 | 141,328 | 105,013 | 43 |
| Government | 220,106 | 242,158 | 242,158 | 1 |
| Health authorities | 312,616 | 312,806 | 244,148 | 8 |
| Municipal police | 9,232 | 9,374 | 142 | 13 |
| Municipalities | 145,311 | 146,804 | 118,593 | 116 |
| School districts | 55,953 | 66,617 | 21,232 | 34 |
| Universities and colleges | 73,068 | 91,130 | 45,968 | 24 |

Official municipal coverage is **110 of 161 current jurisdictions**, including **107** with employees; **51** still lack accepted official records. Regional districts are outside this municipal denominator. shíshálh is a separate governance case; Okanagan Falls remains pending incorporation on 6 November 2026.

## Source scope and replacement decisions

These are published payments, not complete employee rosters or annual base salary rates. Actual schedule headings determine periods; upload dates and index labels do not. Employee, council/trustee, board and executive-only scopes remain distinct. Monetary columns follow each original definition: expense-inclusive totals are not pay, unknown cells remain null, and disclosed zeros/negative recoveries are preserved. Non-person recipients and aggregate payroll are not turned into individual employees.

Native cohorts compare independently implemented readers row by row. Scanned and hybrid cohorts retain manual original-image transcription and OCR corroboration, with separate peer review. Receipts distinguish full machine agreement from the actual rendered rows and pages visually checked. Material issuer-control disagreements retain exact visible warnings and clarification tasks. No value is adjusted to force a subtotal match, and no numerical coincidence is asserted to explain a residual.

Partial or narrower originals cannot silently erase broader compiled data. Explicitly retained partitions require a public scope warning and a pinned validation reason, with consistent employee completeness flags. Retained official/compiled observations may overlap; grouping names in the interface does not prove identity or authorize deletion. [Reviewed replacements and retained overlaps](replacement-review.md) has a separate reviewed source/scope decision.

## Important source findings

- Provincial histories extend to fiscal 1999/00. Employee and OIC/appointee schedules stay separate; negative salary recoveries and source-control conflicts remain literal and visible. Later salary-only schedules have unknown travel, not zero.
- ICBC 2016/17 is a 15-month transition, January 2016–March 2017, rather than an ordinary 12-month year. Receiver General payments are excluded as non-person recipients; unknown receiver expense cells do not establish an employee-only expense comparator.
- School SD8 fiscal 2018/19 is a complete hybrid schedule of 209 employees: 169 native rows plus 40 manually reviewed scanned rows. Its fiscal 2025/26 employee schedule remains held because one page says 2025 while others say 2026; no typo is assumed.
- Camosun excludes board-member employees and severance from its employee table. Seven unresolved compiled partitions remain alongside official sources, including Museum 2023/24 where the best salary match is an older fiscal original. No guessed fiscal-period correction is made.
- Health additions are board records, not new employee schedules. PHSA employee OCR and VCH/Providence original retrieval remain unresolved. The BCCSS amalgamation evidence prevents creating false standalone employee gaps after its transfer to PHSA.
- TRU 2024/25 is an official published original with an unsigned/undated approval form. That limitation is explicit; no signed or adopted original is claimed. Exact source-control qualifications and copy/clarification tasks remain available.

## Employer histories added

| Employer | Newly accepted periods | Added observations |
| --- | --- | ---: |
| Alberni-Clayoquot Regional District | 2019, 2020, 2023, 2024, 2025 | 122 |
| BC Clinical and Support Services Society | 2017/18 | 23 |
| BC Family Maintenance Agency | 2022/23, 2023/24, 2024/25, 2025/26 | 22 |
| British Columbia Housing Management Commission | 2023/24 | 490 |
| British Columbia Railway Company | 2017/18, 2018/19, 2019/20, 2020/21, 2021/22, 2022/23, 2024/25, 2025/26 | 146 |
| British Columbia Lottery Corporation | 2010/11, 2011/12, 2012/13, 2013/14, 2014/15, 2015/16, 2016/17, 2017/18, 2018/19, 2019/20, 2020/21, 2021/22, 2023/24, 2024/25, 2025/26 | 8,857 |
| Camosun College | 2015/16, 2016/17, 2017/18, 2018/19, 2019/20, 2020/21, 2021/22, 2022/23, 2024/25, 2025/26 | 4,934 |
| Capilano University | 2018/19, 2019/20, 2020/21, 2021/22, 2022/23, 2023/24, 2024/25 | 2,733 |
| City of Campbell River | 2016, 2017, 2018, 2019, 2020, 2021, 2022 | 765 |
| City of Grand Forks | 2024 | 41 |
| City of Revelstoke | 2021, 2023, 2024 | 158 |
| City of Salmon Arm | 2022, 2024 | 91 |
| District of Elkford | 2022 | 29 |
| District of Lake Country | 2025 | 88 |
| District of Metchosin | 2025 | 16 |
| District of Port Edward | 2024, 2025 | 10 |
| District of Wells | 2020 | 5 |
| Douglas College | 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 3,359 |
| Emily Carr | 2023/24, 2024/25 | 377 |
| Insurance Corporation of British Columbia | 2014, 2015, 2016/17, 2017/18, 2018/19, 2019/20, 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 29,348 |
| Interior Health | 2018/19, 2019/20, 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 79 |
| North Island College | 2024/25 | 200 |
| Northern Health | 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 61 |
| Oakanagan College | 2021/22, 2022/23, 2023/24, 2024/25 | 1,999 |
| Provincial Health Services Authority | 2024/25, 2025/26 | 27 |
| Government of British Columbia | 1999/00, 2000/01, 2001/02, 2002/03, 2003/04, 2004/05, 2005/06 | 22,052 |
| Regional District of East Kootenay | 2023, 2024, 2025 | 155 |
| Royal British Columbia Museum Corporation | 2021/22, 2022/23, 2023/24, 2024/25 | 200 |
| School District No. 6 (Rocky Mountain) | 2024/25 | 256 |
| School District No. 8 (Kootenay Lake) | 2018/19, 2019/20, 2020/21, 2021/22, 2022/23, 2025/26 | 1,254 |
| School District No. 20 (Kootenay-Columbia) | 2024/25 | 285 |
| School District No. 46 (Sunshine Coast) | 2024/25 | 256 |
| School District No. 47 (qathet) | 2024/25 | 205 |
| School District No. 48 (Sea to Sky) | 2024/25 | 368 |
| School District No. 51 (Boundary) | 2024/25 | 108 |
| School District No. 52 (Prince Rupert) | 2024/25 | 163 |
| School District No. 63 (Saanich) | 2024/25 | 517 |
| School District No. 67 (Okanagan Skaha) | 2024/25 | 403 |
| School District No. 71 (Comox Valley) | 2018/19, 2019/20, 2020/21, 2021/22, 2023/24, 2024/25 | 2,939 |
| School District No. 72 (Campbell River) | 2024/25 | 403 |
| School District No. 74 (Gold Trail) | 2024/25 | 93 |
| School District No. 83 (K̓wsaltktnéws ne Secwepemcúl’ecw) | 2024/25 | 465 |
| School District No. 85 (Vancouver Island North) | 2024/25 | 111 |
| School District No. 87 (Stikine) | 2020/21, 2022/23, 2023/24, 2024/25 | 134 |
| School District No. 91 (Nechako Lakes) | 2024/25 | 297 |
| School District No. 92 (Nisga'a) | 2024/25 | 44 |
| School District No. 93 (Conseil scolaire francophone) | 2019/20, 2020/21, 2022/23, 2023/24, 2024/25 | 1,933 |
| School District No. 5 (Southeast Kootenay) | 2024/25 | 430 |
| Thompson Rivers University | 2022/23, 2024/25 | 1,501 |
| University of the Fraser Valley | 2019/20, 2020/21, 2021/22, 2022/23, 2023/24, 2024/25, 2025/26 | 4,176 |
| Vancouver Island University | 2020/21, 2021/22, 2024/25 | 1,936 |
| Vancouver Police | 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 142 |
| Village of Fraser Lake | 2023 | 13 |

## Research and next actions

- [municipal inventory, findings and verification](municipal/README.md)
- [health inventory, findings and verification](health/README.md)
- [schools inventory, findings and verification](schools/README.md)
- [education inventory, findings and verification](education/README.md)
- [crowns inventory, findings and verification](crowns/README.md)
- [government-police inventory, findings and verification](government-police/README.md)
- [Independent compiled retention guard review](reviews/compiled-retention-guard.md)
- [Independent crowns current review](reviews/crowns-current.md)
- [Independent crowns museum housing review](reviews/crowns-museum-housing.md)
- [Independent education replacement scopes review](reviews/education-replacement-scopes.md)
- [Independent final integration review](reviews/final-integration.md)
- [Independent government control acceptance review](reviews/government-control-acceptance.md)
- [Independent government early controls review](reviews/government-early-controls.md)
- [Independent government oic acceptance review](reviews/government-oic-acceptance.md)
- [Independent government oic controls review](reviews/government-oic-controls.md)
- [Independent health northern boards review](reviews/health-northern-boards.md)
- [Independent health other boards review](reviews/health-other-boards.md)
- [Independent municipal campbell river review](reviews/municipal-campbell-river.md)
- [Independent municipal small and layouts review](reviews/municipal-small-and-layouts.md)
- [Independent regional acrd acceptance review](reviews/regional-acrd-acceptance.md)
- [Independent regional acrd controls review](reviews/regional-acrd-controls.md)
- [Independent regional east kootenay acceptance review](reviews/regional-east-kootenay-acceptance.md)
- [Independent regional east kootenay controls review](reviews/regional-east-kootenay-controls.md)
- [Independent school kootenay lake 2022 controls review](reviews/school-kootenay-lake-2022-controls.md)
- [Independent school kootenay lake scan review](reviews/school-kootenay-lake-scan.md)
- [Independent school material control acceptance review](reviews/school-material-control-acceptance.md)
- [Independent school sd46 controls review](reviews/school-sd46-controls.md)
- [Independent school sd52 controls review](reviews/school-sd52-controls.md)
- [Independent school small controls review](reviews/school-small-controls.md)
- [Independent school stikine review](reviews/school-stikine.md)
- [Independent tru unsigned original review](reviews/tru-unsigned-original.md)

The [remaining queue](work-queue.csv) has **1694 tasks**; the [copy and clarification list](acquisition-list.md) contains **131 draft candidates**. Old pass lists may overlap and their totals must not be added. Source discovery is not a claim that every historical report has been found. Each sector inventory records accepted, located, held and unsuccessful retrievals separately.

No institution or municipality was contacted. No FOI request was submitted and no fee incurred. Public archives and ordinary access to existing adopted reports or native tables come before formal access fallback. Existing public scans requiring extraction are processing tasks.

## Reproduce

Use collection guides for original-backed reproduction and offline evidence replay. Publication checks:

```sh
node --test scripts/salary-data.test.mjs src/salaries/*.test.js src/government/salaries.test.js
npm run compare:municipal-periods
npm run build:salaries
npm run check:salaries
npm run audit:municipal-salaries
npm run follow-up:municipal-salaries
npm run review:sector-salaries
npm run review:municipal-wave
npm run review:municipal-history
npm run review:salary-continuation
npm run preview:salaries -- --build
```
