# BC municipal council pay and historical source recovery

Reviewed November 4, 2026. **430 office observations, 182 named payments, 160 municipalities and 25 primary source records.** This collection adds the requested CBC survey and supported history as a separately sourced companion to the salary search.

Open the **Council pay** tab, or use `?view=salaries&browse=council`. Office observations and named payments have separate tabs. Municipality, source/name search, year and role filters are shareable in the URL. Source definitions, effective dates, supplements, reporting exceptions and remaining gaps stay with the figures. The view fetches one compact companion file and does not request the main people or employer indexes.

## What is included

| Collection | Coverage | Records and meaning |
| --- | --- | --- |
| CBC 2021 survey | 160 municipalities | 320 office observations: 318 for 2021; Port Hardy's two are explicitly 2020. Councillor statistic is the most common reported amount. |
| CBC 2019 extract | 17 southern Vancouver Island municipalities | 20 exact values: 17 mayor amounts and three councillor amounts. Partial recovery; other bars without numeric labels were not estimated. Councillor statistic was the mean where payments differed. |
| Official annual rates | Saanich 2018–2026; Vancouver 1995–2015 and 2019–2026; Mackenzie 2015–2023; Kamloops 2022–2026; Kelowna 2025; Nanaimo councillor 2016 | 90 published office rates, including two distinct Vancouver 2020 editions; effective dates and additional duties stay separate. |
| Vancouver named payment schedules | 1994–1995, 1997–2003, 2020–2025 | 182 source-specific payments. All 61 printed numeric component totals reconcile exactly. These are actual reported payments, including partial terms, rather than full-year base salaries. |

The generated [coverage.json](coverage.json) gives exact current counts, observed years and municipality coverage. The public downloads are [JSON](../../../public/salaries/council-pay.json) and [CSV](../../../public/salaries/council-pay.csv). Neither download is a complete annual history of all municipalities.

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

[preservation-baseline.json](preservation-baseline.json) records the pre-change Git tree and every existing entry under `public/salaries`. The publishing step starts from current main and adds the companion files, source package, builder/tests and interface changes. Existing salary data, people, positions, name links, disclosure annotations, original evidence and historical receipts retain their object IDs. This companion's 182 payments are not appended to or double-counted in the pre-existing main salary total.

All 32 focused data, interface and navigation tests pass, and both JSX components compile in this checkout. A broader salary-test attempt is limited by missing main index/shard fixtures in this sparse environment. Full repository rebuild gates run in GitHub CI. Desktop and phone browser review is not claimed: both available browser connections refused the scratch localhost preview. The responsive layout is implemented and the source/URL/filter behavior is covered by focused tests; visual review remains a PR check.

## Remaining historical work

1. Recover the rest of CBC's 2019 province-wide data and exact councillor labels for the fourteen other southern Island bars. Keep the mean-versus-mode distinction when comparing with 2021.
2. Obtain each municipality's earlier remuneration bylaws, amendments, council schedules and annual SOFI reports. A current roster helps discover sites; it does not establish historical municipal existence or annual coverage.
3. Locate the corrected Vancouver 1996 council-payment report. The [July 22, 1997 minutes](https://council.vancouver.ca/970722/regmin.htm) acknowledge errors and request a corrected final report. The uncorrected figures are held, not published.
4. Extract Vancouver named schedules for 2004–2019 and earlier than 1994. Annual-rate history does not fill a named-payment gap. The city points to archival paper records for reports before the online council archive.
5. Extend scheduled rates into currently missing years, preserving versions and exact effective dates. A recommended or projected rate is not proof that it was enacted or paid.
6. Reconcile source differences with further official evidence. Do not choose a number just because it appears in the newer publication, and do not send records requests without separate authorization.
