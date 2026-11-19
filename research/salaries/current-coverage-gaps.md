# Current salary coverage and next imports

Use [the generated report](current-coverage-gaps.json) for the current counts and rosters.
Refresh it after the public employer index changes with `node scripts/build-current-salary-gaps.mjs`.
Use `--check` to check for drift or `--as-of=YYYY-MM-DD` to reproduce a roster cut-off.
The November 9 roadmap and the municipal audit remain dated snapshots.

The generator counts years with published rows from an official source. A compiled row,
an aggregate-only schedule, or a source lead is not an official observation. Municipal
employee coverage is separate from council and other disclosures. Okanagan Falls enters
the current roster on 6 November 2026; the report does not create missing pre-incorporation
salary years. These counts describe the published dataset, not the full workforce.

## Source-ready and held work

| Employer / period | Category | State and next action |
| --- | --- | --- |
| SD57 Prince George, 2022/23 | Employees | Signed official [69-page SOFI](https://22.files.edl.io/ecb5/11/15/24/222817-489f5533-61fe-4897-9dbc-86cbb8fb2362.pdf) verified, SHA-256 `4804bb7e254313a4d3626862da291b78870124be65cbcd983a9ece09dec05616`. Extract physical pp. 51–64, separating trustees on p. 51. On p. 64 the over-threshold remuneration and expenses controls are $71,496,307.59 and $862,050.36. Independently verify every row and reconcile before import. |
| UNBC, 2025/26 | Employees | Draft board package located; employee schedule pp. 37–45. The [Board index](https://www.unbc.ca/university-secretary/board-governors/meeting-dates-agendas-and-minutes) does not establish approval of this copy; the [Finance index](https://www.unbc.ca/finance/financial-statements) lists consolidated 2025/26 statements, not a final 2025/26 SOFI. Hold the edition. |
| UNBC, 2017/18 | Employees | Compiled edition retained. Verify the complete, approved official schedule first. |
| BC Transit, 2011/12–2014/15, 2017/18–2018/19, 2021/22–2024/25 | Employees | Original schedules located; OCR and independently reconcile. |
| BCIT, 2013/14; North Island College, 2019/20 | Employees | Original schedules located; extract, verify and reconcile. |
| Kamloops 2016–2023 and 2025; Kelowna 2019 and 2021–2025; Prince Rupert, Quesnel and Smithers 2025 | Council | Verify the 18 council cohorts separately from the already-imported employee schedules. |
| Island Health, 2022/23 and 2023/24 | Employees | Legislative Library copies published with qualifications. The original website copies are still held; do not re-import the cohorts. |
| BC Hydro and Powerex, 2024/25 | Employees | Held. Keep separate from the Island Health disposition. |

See the [collection-priority register](../audits/evidence-reconciliation-2026-11-12/collection-priorities.json) and [source inventory](source-inventory.md) for source-specific blockers. No compensation rows are added by the report.
