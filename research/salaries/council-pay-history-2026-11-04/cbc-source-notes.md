# CBC municipal council pay: source and extraction notes

Retrieved 2026-11-04.

## 2021 survey

- Original article: https://www.cbc.ca/news/canada/british-columbia/bc-mayors-councillors-salaries-2021-1.6518877
- Official preserved copy: https://pub-creston.escribemeetings.com/filestream.ashx?DocumentId=4399
- Observation file: `cbc-office-pay.json`.
- Factual transcription evidence: `cbc-2021-transcription-evidence.json`.

All **160 municipality rows / 320 amounts** were independently recovered from eight search-indexed table blocks of the preserved Creston attachment. Each block contains 20 rows. The eight blocks were parsed and every amount was reconciled with the observation file; all 160 employer slugs and all 320 observation IDs are unique. These counts are derived from the recovered rows, not the earlier conversation's claimed totals.

Table-page labels 1, 2, 4 and 8 were visible in the returned source text. Other blocks use their first and last municipality as locators. The `tableBlock` value is an extraction-order identifier, not a physical PDF page number. The preserved page carries a July 18, 2022 print timestamp; this is not treated as the article's publication date.

Direct original-article access was unavailable, and direct preserved-PDF retrieval returned HTTP 403. The 2021 extraction therefore relies on the indexed official attachment; no downloaded-original hash or direct visual verification is claimed.

### Definition and year handling

CBC describes its inputs as financial disclosures and municipal staff responses. The councillor statistic is the **most common** payment within each municipality. The dataset stores these observations as `reported-office-pay`, not as named-person earnings or verified annual base rates.

**Port Hardy:** the footer expressly uses 2020 because of staffing issues. Its mayor amount is $29,067 and its councillor amount is $14,324. Both observations have `year: 2020`. The remaining 318 observations have `year: 2021`.

### Verified discrepancies

**Saanich:** CBC reports a councillor figure of $49,423. The municipality's official 2021 annual-rate table gives $49,242.57. The $180.43 difference is unresolved; the CBC observation is retained with a note. CBC's mayor figure of $124,602 is the rounded official rate of $124,601.96. Saanich states that adjustments take effect on the first pay date in June, so an annual rate is not necessarily calendar-year remuneration.

Official source: https://www.saanich.ca/EN/main/local-government/mayor-council/council-remuneration-and-expenses.html

**Vancouver:** CBC's $178,473 mayor figure exactly matches the 2021 SOFI remuneration amount. CBC's $96,442 councillor figure appears for Christine Boyle, Colleen Hardwick and Michael Wiebe, making it the mode of the ten councillor amounts. The SOFI's notes say remuneration includes extra-duty payments. These values therefore should not be presented as Vancouver's annual base salary schedule.

- Actual payments: https://vancouver.ca/files/cov/2021-statement-of-financial-information.pdf — physical PDF page 78, printed SOFI page 4.
- Annual rates: https://vancouver.ca/files/cov/12-10-2020-2021-remuneration.pdf — 2021 schedule gives mayor $178,800.41 and councillor $88,515.05; expense allowance and additional duties are separate.

The source-specific observations are preserved without merging annual rates and actual payments.

## 2019 historical survey: partial recovery

- Original article: https://www.cbc.ca/news/canada/british-columbia/local-politics-salaries-revelstoke-victoria-mayors-councillors-1.5365662
- Official preserved chart extract: https://www.viewroyal.ca/assets/Home/Whats~New/2021/2021%2010%2027%20Council%20Size%20Report.pdf
- Observation file: `cbc-2019-office-pay.json`.

The View Royal report identifies the CBC article as published November 21, 2019. Physical PDF pages **16–17** reproduce its southern Vancouver Island charts (Schedule 2, March 23, 2021 report, printed pages 4–5 of 6).

This extraction contains **20 exact observations for 17 municipalities**: 17 mayor values printed inside the chart bars, and three councillor values stated in the report prose (Sooke $12,500, Duncan $15,862, View Royal $15,216). The other 14 councillor bars lack numeric labels and are excluded; no values are estimated from bar lengths.

The chart footer says most figures refer to 2019 and an asterisk marks 2018. The included labels have no asterisks, so the 20 observations use 2019. Where individual councillor payments varied, the 2019 survey used their **mean**, unlike the 2021 survey's most-common value. Direct percentage-change comparisons should retain this distinction.

The official PDF was downloaded and its two chart pages rendered and inspected. Its SHA-256 is `914c82077914ef35a701b38ab6c75e463561303a0300ae52eed0b8944592ef2d`. The public source URL and hash are retained. The downloaded PDF and chart renders are held outside the repository for independent review; the repository contains factual transcriptions and source notes. Coverage remains explicitly **partial**: the full province-wide 2019 survey was not recovered.

## Historical source leads

These are evidence leads, not a claim of complete historical coverage.

- Saanich's official remuneration page provides annual rates for 2018–2026, with its June effective-date caveat.
- Vancouver's December 2020 remuneration memo preserves 2019, original and amended 2020, and 2021 rate schedules. All eight mayor/councillor observations are included in `vancouver-2019-2021-rates.json`. By-law 12700 confirms May 12, 2020 as the amended edition's effective date. The amendment changes annual remuneration for 2020, so these edition dates do not establish actual payroll timing or justify prorating the two rates. The 2021 adjustment uses the original January 2020 schedule.
- Vancouver's official council-pay directory links salary schedules and SOFI payment records: https://vancouver.ca/your-government/city-council-salaries-expenses.aspx
- Vancouver's July 22, 1997 council minutes explicitly record errors in the report of 1996 council payments and request a corrected final report: https://council.vancouver.ca/970722/regmin.htm . A 1996 table should not be treated as validated merely because an early report is accessible.
- Mackenzie's official remuneration report gives a 2015–2023 annual-rate history: https://pub-mackenziebc.escribemeetings.com/filestream.ashx?DocumentId=1898 . Its discussion distinguishes SOFI amounts, which can include benefits and other payments, from base rates. These values were not added by this extraction.

## Delivered data scope

CBC additions total **340 office-pay observations**: 320 from the 2021 survey (including Port Hardy's two 2020 figures), and 20 from the partial 2019 extract. No named individual salary record was created from these office-level figures.
