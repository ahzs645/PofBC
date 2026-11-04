# BC municipal council pay and historical source recovery

Reviewed November 4, 2026. **578 office observations, 385 named payments, 160 municipalities and 54 source records.** This collection adds the requested CBC survey and supported history as a separately sourced companion to the salary search.

Open the **Council pay** tab, or use `?view=salaries&browse=council`. Office observations and named payments have separate tabs. Municipality, source/name search, year and role filters are shareable in the URL. Source definitions, effective dates, supplements, reported precision, council-term labels and remaining gaps stay with the figures. Selected municipalities also show coverage separately by office and measure. The view fetches one compact companion file and does not request the main people or employer indexes.

## What is included

| Collection | Coverage | Records and meaning |
| --- | --- | --- |
| CBC 2021 survey | 160 municipalities | 320 office observations: 318 for 2021; Port Hardy's two are explicitly 2020. Councillor statistic is the most common reported amount. |
| CBC 2019 extract | 17 southern Vancouver Island municipalities | 20 exact values: 17 mayor amounts and three councillor amounts. Partial recovery; other bars without numeric labels were not estimated. Councillor statistic was the mean where payments differed. |
| Official annual rates | Vancouver councillor 1995–2026 and selected mayor years; Abbotsford 2007–2015; Saanich 2018–2026; Mackenzie 2015–2023; Kamloops 2022–2026; Kelowna 2025; Nanaimo 2003 and councillor 2016; North Vancouver City 2022; Victoria 2022 and 2024 | 124 annual-rate observations, including the Vancouver 2020 editions and calendar-year slices of the explicit Abbotsford 2007–2011 interval. These are scheduled rates, not independent payroll measurements. |
| Additional official comparative surveys | Selected municipalities in 2015, 2017, 2018, 2023 and 2025 | 114 office-pay observations. Survey vintage, $100 precision where applicable, and estimated acting pay remain explicit; these do not fill gaps in adopted-base-rate histories. |
| Vancouver named payment schedules | 1994–1995 and every year from 1997–2025 | 385 source-specific payments. Of 129 printed column controls, 114 reconcile exactly and 15 preserve documented whole-dollar differences within explicit precision bounds. Election-term groups and role changes remain distinct. |

The [time-series expansion report](timeseries-expansion.md) explains the additional 148 office observations and 203 named payment rows, with a municipality/year matrix and precision controls. The generated [coverage.json](coverage.json) gives exact current counts, observed years and municipality coverage. The public downloads are [JSON](../../../public/salaries/council-pay.json) and [CSV](../../../public/salaries/council-pay.csv). Neither download is a complete annual history of all municipalities.

## Three distinct measures

- `reported-office-pay`: an office-level survey result with the survey's statistic and source year. It is not assigned to a named officeholder.
- `annual-base-rate`: a published annual rate at a specified time. A midyear change is not treated as twelve months of actual earnings. Separate supplements and additional duties are not added automatically.
- `actual-remuneration`: an amount reported for a named official in an annual schedule. The name is kept as printed, including initials and source spelling. No new cross-year identity link is inferred.

All amounts are nominal Canadian dollars. The interface does not produce combined remuneration totals, interpolate missing years, annualize partial terms or calculate growth between incompatible measures. An absent figure is unknown, not zero.

## Source exceptions that affect interpretation

**Port Hardy:** CBC's two figures are from 2020. The publication's 2021 survey label never overwrites the reference year.

**Saanich:** CBC reports $49,423 for a councillor in 2021; the official annual-rate table reports $49,242.57. The difference remains unresolved and both source-specific observations remain visible. Saanich adjusts its annual schedule on the first pay date in June; the table does not supply the exact day.

**Vancouver survey versus base rate:** CBC's 2021 figures match the actual SOFI remuneration schedule. The councillor figure $96,442 is the mode of the ten councillor payments; additional duties can be included. The annual base salary schedule is retained separately. Vancouver's 2022–2026 schedules also list a $3,048 annual supplement and monthly rates for additional duties; these are not silently folded into the base amount.

**Vancouver 1994–1995:** the municipal officers allowance was the formerly non-taxable portion of remuneration. The normalized remuneration equals printed income plus that allowance, with both components retained. It is not classified as an expense reimbursement.

**Older transportation allowances and role changes:** the 2004–2015 tables list transportation separately, so expense sums include local expenses, transportation and travel once. Later tables include transportation within local expenses. Sullivan’s two 2005 roles remain separate source rows, and the two 2018 council groups retain their own printed subtotals.

**Published rounding:** source cells are never changed to force equality. The validator records the difference between disclosed rows and each printed total. A nonzero difference is accepted only with recorded source evidence, whole-dollar cells and a bound of half a dollar per disclosed row plus half a dollar for the total. This shows consistency with rounding, not proof that the source is error-free. The 2006 explanation remains an inference. Independent cent-level appendices and the 2004 alternate report are checked separately.

**Missing expense cells:** Sullivan's 1998 and 1999 auto-allowance cells are unstated. The normalized expense total is null; `knownExpenses` sums only disclosed components. The separately disclosed $1,563.65 paid in 1998 for 1997 auto allowance remains its own component, outside the regular table sum.

**Modern Vancouver budgets:** the discretionary-expense column can include office and political staff costs. It is kept in `components`, excluded from remuneration and from the displayed local-plus-travel expense total. Mayoral travel figures may themselves include staff travel, which is disclosed. Conference/travel amounts are net of recoveries. Election and resignation years can contain partial terms and deferred remuneration.

**Retained compiled editions:** 22 existing Vancouver compiled rows have candidate matches by municipality, surname, role and remuneration to official 2020 and 2023 schedules. They remain distinct source editions; no salary index or name-link group is changed. The compiled 2020/21 Wiebe expenses are $6,929; the official calendar-2020 schedule's local-plus-travel amount is $7,109. [The comparison](existing-source-comparison.json) preserves both. It does not establish that a compiled edition label is a verified calendar reporting period.

## Evidence and reproducibility

The source JSON files preserve factual numeric tables and primary URLs. [CBC source notes](cbc-source-notes.md) explain the survey extraction in detail. The 2021 Creston attachment was recovered from eight search-indexed table blocks because direct access returned HTTP 403. No downloaded-original hash or visual verification is claimed for that source. The 2019 View Royal PDF was downloaded, fingerprinted and its two chart pages visually checked; its original-file hash is recorded. Other files identify table transcription and source locations without claiming original-file hashes that were not obtained.

The [validation receipt](validation.json) hashes every data input, generated output and the existing Vancouver export used for source-edition reconciliation. These transcription/output hashes are not hashes of external original reports. The builder checks every CBC 2021 figure against the wide-table transcription, validates source and observation identities, recomputes all Vancouver printed column controls, checks both sides of the compiled comparisons and preserves missing cells.

```bash
npm run build:council-pay
npm run check:council-pay
node --test scripts/council-pay.test.mjs src/salaries/councilPay.test.js src/salaries/viewState.test.js src/site/browserHistory.test.js
```

The regular `build:salaries` command recreates the companion after the existing atomic salary export replacement. `check:salaries` also verifies companion freshness and its data tests. Existing historical release replayers continue to use their archived, pinned package and source code.

## Preservation and review boundary

[preservation-baseline.json](preservation-baseline.json) records the pre-change Git tree and every existing entry under `public/salaries`. The publishing step starts from current main and adds the companion files, source package, builder/tests and interface changes. Existing salary data, people, positions, name links, disclosure annotations, original evidence and historical receipts retain their object IDs. This companion's 385 payments are not appended to or double-counted in the pre-existing main salary total.

The [expansion baseline](timeseries-expansion-baseline.json) additionally protects all prior 430 office observations, 182 named payments and their 25 primary source URLs.

All 42 focused data, interface and navigation tests pass, and both JSX components compile in this checkout. A broader salary-test attempt is limited by missing main index/shard fixtures in this sparse environment. Full repository rebuild gates run in GitHub CI. Desktop and phone browser review is not claimed: both available browser connections refused the scratch localhost preview. The responsive layout is implemented and the source/URL/filter behavior is covered by focused tests; visual review remains a PR check.

## Remaining historical work

1. Recover the rest of CBC's 2019 province-wide data and exact councillor labels for the fourteen other southern Island bars. Keep the mean-versus-mode distinction when comparing with 2021.
2. Obtain each municipality's earlier remuneration bylaws, amendments, council schedules and annual SOFI reports. A current roster helps discover sites; it does not establish historical municipal existence or annual coverage.
3. Locate the corrected Vancouver 1996 council-payment report. The [July 22, 1997 minutes](https://council.vancouver.ca/970722/regmin.htm) acknowledge errors and request a corrected final report. The uncorrected figures are held, not published.
4. Extend Vancouver named schedules earlier than 1994. The 2004–2019 gap is now filled; annual-rate history still does not fill a named-payment gap. The city points to archival paper records for reports before the online council archive.
5. Extend scheduled rates into currently missing years, preserving versions and exact effective dates. A recommended or projected rate is not proof that it was enacted or paid.
6. Reconcile source differences with further official evidence. Do not choose a number just because it appears in the newer publication, and do not send records requests without separate authorization.
