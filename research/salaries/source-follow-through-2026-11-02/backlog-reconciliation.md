# Reconciliation of all 134 provided backlog entries

The current accepted manifests and seven new follow-through collections support **110 complete employee entries and 1 partially accepted report**. **23 original entries remain unaccepted**. All 134 IDs are mapped in the JSON companion, with actual source IDs, manifests, payload paths, hashes, row counts and match bases.

The original 73 comprise 50 already accepted employee schedules and 23 unresolved items. Twenty original pending statuses are stale: PHSA 2015/16–2024/25 and Island Health 2015/16–2024/25 are accepted in current main. The 61 additions comprise 60 complete employee reports and TransLink 2024 with four accepted entity cohorts and CMBC held. The seven new collections contain 84 accepted cohorts / 55,477 observations. Across this 134-entry reconciliation, 134 distinct accepted employee payloads contain 333,100 observations; this is source inventory, not a count of new rows or distinct people.

Every mapped compressed payload hash and row count was verified. Uploaded statuses and manifest pointers were not treated as acceptance evidence. The uploaded CNC 2020/21 and RRU 2021/22 accepted pointers do not resolve in current main; both now have actual reconstructed files in the new follow-through collections.

## Original 23 unresolved entries

| Backlog ID | Remaining blocker | Current evidence / useful progress |
| --- | --- | --- |
| `bc-transit-sofi-2024-25` | ocr-and-source-validation | Fresh official PDF re-download matches the supplied SHA-256; employee-page native text is absent. Complete OCR and source-row/control verification remain unperformed. |
| `bc-transit-sofi-2023-24` | ocr-and-source-validation | Fresh official PDF re-download matches the supplied SHA-256; employee-page native text is absent. Complete OCR and source-row/control verification remain unperformed. |
| `bc-transit-sofi-2022-23` | ocr-and-source-validation | Fresh official PDF re-download matches the supplied SHA-256; employee-page native text is absent. Complete OCR and source-row/control verification remain unperformed. |
| `bc-transit-sofi-2021-22` | ocr-and-source-validation | Fresh official PDF re-download matches the supplied SHA-256; employee-page native text is absent. Complete OCR and source-row/control verification remain unperformed. |
| `bc-transit-sofi-2018-19` | ocr-and-source-validation | Fresh official PDF re-download matches the supplied SHA-256; employee-page native text is absent. Complete OCR and source-row/control verification remain unperformed. |
| `bc-transit-sofi-2017-18` | ocr-and-source-validation | Fresh official PDF re-download matches the supplied SHA-256; employee-page native text is absent. Complete OCR and source-row/control verification remain unperformed. |
| `bc-transit-sofi-2014-15` | ocr-and-source-validation | Fresh official PDF re-download matches the supplied SHA-256; employee-page native text is absent. Complete OCR and source-row/control verification remain unperformed. |
| `bc-transit-sofi-2013-14` | ocr-and-source-validation | Fresh official PDF re-download matches the supplied SHA-256; employee-page native text is absent. Complete OCR and source-row/control verification remain unperformed. |
| `bc-transit-sofi-2012-13` | ocr-and-source-validation | Fresh official PDF re-download matches the supplied SHA-256; employee-page native text is absent. Complete OCR and source-row/control verification remain unperformed. |
| `bc-transit-sofi-2011-12` | ocr-and-source-validation | Fresh official PDF re-download matches the supplied SHA-256; employee-page native text is absent. Complete OCR and source-row/control verification remain unperformed. |
| `unbc-board-sofi-2017-18` | document-procurement-and-final-approval | Official native table observed via web reader on physical pages 10–14; period ends 2018-03-31. Binary 403; final approval not verified. |
| `unbc-board-sofi-2021-22` | document-procurement-and-final-approval | Official native table observed via web reader on physical pages 11–17; period ends 2022-03-31. Binary 403; final approval not verified. |
| `unbc-board-sofi-2025-26` | document-procurement-and-final-approval | Official native table observed via web reader on physical pages 37–45; period ends 2026-03-31. Binary 403; final approval not verified. |
| `bcit-sofi-2013-14` | ocr-and-source-validation | Exact original re-downloaded; 67 pages, no native text. Employee Exhibit B located on physical 33–48; cover 32 and summary 48 inspected. Separate board cover 49. The duplicate unparsed-source record is the same underlying item. |
| `bc-pension-employee-history` | employee-document-not-located | Publication index refreshed; annual-report links found, no full employee SOFI located in this check. Nonpublication is not asserted. |
| `bci-executive-scope` | scope-currency-and-measure | Official 125-page PDF downloaded and fingerprinted. Physical 67 contains five current-period executives: four CAD and one USD; no full employee roster. |
| `public-accounts-before-2006-07` | document-selection-and-historical-scope | Accepted employee schedules begin 2006/07; requested 1999/2000–2005/06 remain open. Current archive fetch 503, web reader 502. |
| `historical-public-accounts-legislative-library` | historical-ocr-and-scope | Primary library index refreshed; payment-volume links remain available. No selected historical salary cohort has been accepted. |
| `bci-executives-2025-26` | scope-currency-and-measure | Reviewed 5-row component staging exists; acceptedForEmployeeBuild=false. |
| `bci-executives-2017-18` | scope-currency-and-measure | Reviewed 5-row component staging exists; acceptedForEmployeeBuild=false. |
| `bc-pension-executives-2025-26` | scope-currency-and-measure | Reviewed 7-row component staging exists; acceptedForEmployeeBuild=false. |
| `vancouver-council-source-2020-21` | compiled-year-scope-and-document-procurement | Official calendar 2020 SOFI council table located, 11 rows and four monetary components. Source PDF binary403; compiled fiscal label remains unverified. |
| `vancouver-council-source-2023-24` | compiled-year-scope-and-document-procurement | Official calendar 2023 SOFI council table located, 11 rows and four monetary components. Source PDF binary403; compiled fiscal label remains unverified. |

## Partially accepted additional report

`additional-source-translink-2024` maps to four accepted source files, totaling 2,198 observations: TransLink 799, BCRTC 1,129, Transit Police 264 and West Coast Express 6. CMBC 2024 remains held with 3,896 candidates (3,894 named and 2 anonymous). Both native readers agree, but row sums minus printed controls are salary payments +$3,859, Other −$3,212, total remuneration +$647 and expenses −$12. The source provides no explanation. Preserve the four accepted legal-entity cohorts and the held cohort independently.

## Scope and duplicate handling

- All original PHSA and Island Health employee pending claims are no longer gaps; accepted board sources are listed separately and were not used to close employee coverage.
- `bcit-sofi-2013-14` and `bcit-sofi-2013-14-ocr-review` refer to one exact-hash original; count one unresolved employee report.
- The three UNBC IDs contain “board” because the SOFI is inside a board package. Their requested scope is employee remuneration. Locating the table does not establish final board approval or complete row validation.
- Existing BCI / BC Pension executive-component staging is retained research, not accepted employee pay. BCI 2023/24 also has a USD executive row; do not combine currencies.
- Vancouver mayor/councillor source documents use calendar years. The compiled labels 2020/21 and 2023/24 remain unverified until the actual council rows are independently matched. Discretionary expense budgets include political-staff pay.
- Acceptance of employee tables in mixed reports does not certify separate board/director tables. The JSON retains those scope limits.
- No compiled rows were removed, no unreviewed salary rows accepted, and no requests or paid retrieval were made.

## Complete 134-ID map

Actual payload links below correspond to the full current source IDs in `backlog-reconciliation.json`. All referenced payload hashes and row counts passed.

| # | Provided backlog ID | Current disposition | Accepted employee payload(s) |
| ---: | --- | --- | --- |
|1|`bc-transit-sofi-2025-26`|employee-scope-accepted|[bc-transit-sofi-2026](../bc-transit/2025-26.json.gzip) (1,000)|
|2|`bc-transit-sofi-2024-25`|not-accepted|None; see precise blocker above.|
|3|`bc-transit-sofi-2023-24`|not-accepted|None; see precise blocker above.|
|4|`bc-transit-sofi-2022-23`|not-accepted|None; see precise blocker above.|
|5|`bc-transit-sofi-2021-22`|not-accepted|None; see precise blocker above.|
|6|`bc-transit-sofi-2020-21`|employee-scope-accepted|[bc-transit-sofi-2021](../bc-transit/2020-21.json.gzip) (385)|
|7|`bc-transit-sofi-2019-20`|employee-scope-accepted|[bc-transit-sofi-2020](../bc-transit/2019-20.json.gzip) (359)|
|8|`bc-transit-sofi-2018-19`|not-accepted|None; see precise blocker above.|
|9|`bc-transit-sofi-2017-18`|not-accepted|None; see precise blocker above.|
|10|`bc-transit-sofi-2016-17`|employee-scope-accepted|[bc-transit-sofi-2017](../bc-transit/2016-17.json.gzip) (219)|
|11|`bc-transit-sofi-2015-16`|employee-scope-accepted|[bc-transit-sofi-2016](../bc-transit/2015-16.json.gzip) (177)|
|12|`bc-transit-sofi-2014-15`|not-accepted|None; see precise blocker above.|
|13|`bc-transit-sofi-2013-14`|not-accepted|None; see precise blocker above.|
|14|`bc-transit-sofi-2012-13`|not-accepted|None; see precise blocker above.|
|15|`bc-transit-sofi-2011-12`|not-accepted|None; see precise blocker above.|
|16|`northern-health-sofi-2020-21`|employee-scope-accepted|[northern-health-sofi-2020-21](../northern-health/2020-21.json.gzip) (2,500)|
|17|`northern-health-sofi-2021-22`|employee-scope-accepted|[northern-health-sofi-2021-22](../northern-health/2021-22.json.gzip) (2,755)|
|18|`northern-health-sofi-2022-23`|employee-scope-accepted|[northern-health-sofi-2022-23](../northern-health/2022-23.json.gzip) (2,842)|
|19|`northern-health-sofi-2023-24`|employee-scope-accepted|[northern-health-sofi-2023-24](../northern-health/2023-24.json.gzip) (3,645)|
|20|`northern-health-sofi-2024-25`|employee-scope-accepted|[northern-health-sofi-2024-25](../northern-health/2024-25.json.gzip) (4,379)|
|21|`unbc-sofi-2024-25`|employee-scope-accepted|[unbc-sofi-2024-25-employees](../unbc/2024-25.json.gzip) (457)|
|22|`unbc-board-sofi-2017-18`|not-accepted|None; see precise blocker above.|
|23|`unbc-board-sofi-2021-22`|not-accepted|None; see precise blocker above.|
|24|`unbc-board-sofi-2025-26`|not-accepted|None; see precise blocker above.|
|25|`bcit-sofi-2013-14`|not-accepted|None; see precise blocker above.|
|26|`bcit-sofi-2014-15`|employee-scope-accepted|[bcit-sofi-2014-15-employees](../bcit/2014-15-employees.json.gzip) (861)|
|27|`bcit-sofi-2016-17`|employee-scope-accepted|[bcit-sofi-2016-17-employees](../bcit/2016-17-employees.json.gzip) (923)|
|28|`bc-pension-employee-history`|not-accepted|None; see precise blocker above.|
|29|`bci-executive-scope`|not-accepted|None; see precise blocker above.|
|30|`public-accounts-before-2006-07`|not-accepted|None; see precise blocker above.|
|31|`historical-public-accounts-legislative-library`|not-accepted|None; see precise blocker above.|
|32|`bcit-sofi-2017-18-employees`|employee-scope-accepted|[bcit-sofi-2017-18-employees](../bcit/2017-18-employees.json.gzip) (970)|
|33|`bcit-sofi-2018-19-employees`|employee-scope-accepted|[bcit-sofi-2018-19-employees](../bcit/2018-19-employees.json.gzip) (1,024)|
|34|`bcit-sofi-2020-21-employees`|employee-scope-accepted|[bcit-sofi-2020-21-employees](../bcit/2020-21-employees.json.gzip) (1,246)|
|35|`bcit-sofi-2021-22-employees`|employee-scope-accepted|[bcit-sofi-2021-22-employees](../bcit/2021-22-employees.json.gzip) (1,272)|
|36|`bcit-sofi-2022-23-employees`|employee-scope-accepted|[bcit-sofi-2022-23-employees](../bcit/2022-23-employees.json.gzip) (1,298)|
|37|`bcit-sofi-2023-24-employees`|employee-scope-accepted|[bcit-sofi-2023-24-employees](../bcit/2023-24-employees.json.gzip) (1,435)|
|38|`bcit-sofi-2024-25-employees`|employee-scope-accepted|[bcit-sofi-2024-25-employees](../bcit/2024-25-employees.json.gzip) (1,595)|
|39|`fraser-health-sofi-2015-16`|employee-scope-accepted|[fraser-health-sofi-2015-16](../fraser-health/2015-16.json.gzip) (6,219)|
|40|`fraser-health-sofi-2016-17`|employee-scope-accepted|[fraser-health-sofi-2016-17](../fraser-health/2016-17.json.gzip) (6,606)|
|41|`fraser-health-sofi-2017-18`|employee-scope-accepted|[fraser-health-sofi-2017-18](../fraser-health/2017-18.json.gzip) (6,938)|
|42|`fraser-health-sofi-2018-19`|employee-scope-accepted|[fraser-health-sofi-2018-19](../fraser-health/2018-19.json.gzip) (7,527)|
|43|`fraser-health-sofi-2019-20`|employee-scope-accepted|[fraser-health-sofi-2019-20](../fraser-health/2019-20.json.gzip) (8,080)|
|44|`fraser-health-sofi-2020-21`|employee-scope-accepted|[fraser-health-sofi-2020-21](../fraser-health/2020-21.json.gzip) (10,072)|
|45|`fraser-health-sofi-2021-22`|employee-scope-accepted|[fraser-health-sofi-2021-22](../fraser-health/2021-22.json.gzip) (10,782)|
|46|`fraser-health-sofi-2022-23`|employee-scope-accepted|[fraser-health-sofi-2022-23](../fraser-health/2022-23.json.gzip) (11,289)|
|47|`fraser-health-sofi-2023-24`|employee-scope-accepted|[fraser-health-sofi-2023-24](../fraser-health/2023-24.json.gzip) (14,921)|
|48|`fraser-health-sofi-2024-25`|employee-scope-accepted|[fraser-health-sofi-2024-25](../fraser-health/2024-25.json.gzip) (17,278)|
|49|`provincial-health-services-authority-2024-25-employee-source`|employee-scope-accepted|[held-resolution-phsa-2024-25-employees](../held-resolution-health/phsa-2024-25-employees.json.gzip) (13,906)|
|50|`provincial-health-services-authority-2023-24-employee-source`|employee-scope-accepted|[queue-completion-phsa-2023-24-employees](../queue-completion-phsa/phsa-2023-24-employees-v3.json.gzip) (11,908)|
|51|`provincial-health-services-authority-2022-23-employee-source`|employee-scope-accepted|[queue-completion-phsa-2022-23-employees](../queue-completion-phsa/phsa-2022-23-employees-v4.json.gzip) (9,104)|
|52|`provincial-health-services-authority-2021-22-employee-source`|employee-scope-accepted|[queue-completion-phsa-2021-22-employees](../queue-completion-phsa/phsa-2021-22-employees-v4.json.gzip) (8,270)|
|53|`provincial-health-services-authority-2020-21-employee-source`|employee-scope-accepted|[queue-completion-phsa-2020-21-employees](../queue-completion-phsa/phsa-2020-21-employees-v4.json.gzip) (7,941)|
|54|`provincial-health-services-authority-2019-20-employee-source`|employee-scope-accepted|[queue-completion-phsa-2019-20-employees](../queue-completion-phsa/phsa-2019-20-employees-v4.json.gzip) (6,913)|
|55|`provincial-health-services-authority-2018-19-employee-source`|employee-scope-accepted|[queue-completion-phsa-2018-19-employees](../queue-completion-phsa/phsa-2018-19-employees-v4.json.gzip) (6,041)|
|56|`provincial-health-services-authority-2017-18-employee-source`|employee-scope-accepted|[queue-completion-phsa-2017-18-employees](../queue-completion-phsa/phsa-2017-18-employees-v3.json.gzip) (5,072)|
|57|`provincial-health-services-authority-2016-17-employee-source`|employee-scope-accepted|[queue-completion-phsa-2016-17-employees](../queue-completion-phsa/phsa-2016-17-employees-v4.json.gzip) (5,118)|
|58|`provincial-health-services-authority-2015-16-employee-source`|employee-scope-accepted|[queue-completion-phsa-2015-16-employees](../queue-completion-phsa/phsa-2015-16-employees-v4.json.gzip) (4,545)|
|59|`island-health-2024-25-employee-source`|employee-scope-accepted|[island-health-sofi-2024-25](../island-health/2024-25.json.gzip) (12,283)|
|60|`island-health-2023-24-employee-source`|employee-scope-accepted|[gap-health-employees-island-health-2023-24](../gap-fill-health-employees/island-health-2023-24-employees.json.gzip) (10,884)|
|61|`island-health-2022-23-employee-source`|employee-scope-accepted|[gap-health-employees-island-health-2022-23](../gap-fill-health-employees/island-health-2022-23-employees.json.gzip) (8,252)|
|62|`island-health-2021-22-employee-source`|employee-scope-accepted|[island-health-sofi-2021-22](../island-health/2021-22.json.gzip) (7,685)|
|63|`island-health-2020-21-employee-source`|employee-scope-accepted|[island-health-sofi-2020-21](../island-health/2020-21.json.gzip) (7,324)|
|64|`island-health-2019-20-employee-source`|employee-scope-accepted|[island-health-sofi-2019-20](../island-health/2019-20.json.gzip) (5,835)|
|65|`island-health-2018-19-employee-source`|employee-scope-accepted|[island-health-sofi-2018-19](../island-health/2018-19.json.gzip) (5,022)|
|66|`island-health-2017-18-employee-source`|employee-scope-accepted|[island-health-sofi-2017-18](../island-health/2017-18.json.gzip) (4,413)|
|67|`island-health-2016-17-employee-source`|employee-scope-accepted|[island-health-sofi-2016-17](../island-health/2016-17.json.gzip) (4,229)|
|68|`island-health-2015-16-employee-source`|employee-scope-accepted|[island-health-sofi-2015-16](../island-health/2015-16.json.gzip) (3,824)|
|69|`bci-executives-2025-26`|not-accepted|None; see precise blocker above.|
|70|`bci-executives-2017-18`|not-accepted|None; see precise blocker above.|
|71|`bc-pension-executives-2025-26`|not-accepted|None; see precise blocker above.|
|72|`vancouver-council-source-2020-21`|not-accepted|None; see precise blocker above.|
|73|`vancouver-council-source-2023-24`|not-accepted|None; see precise blocker above.|
|74|`additional-source-cnc-2018-19`|employee-scope-accepted|[cnc-sofi-2018-19-employees](../follow-through-cnc/2018-19.json.gzip) (205)|
|75|`additional-source-cnc-2019-20`|employee-scope-accepted|[cnc-sofi-2019-20-employees](../follow-through-cnc/2019-20.json.gzip) (236)|
|76|`additional-source-cnc-2020-21`|employee-scope-accepted|[cnc-sofi-2020-21-employees](../follow-through-cnc/2020-21.json.gzip) (258)|
|77|`additional-source-cnc-2021-22`|employee-scope-accepted|[cnc-sofi-2021-22-employees](../follow-through-cnc/2021-22.json.gzip) (268)|
|78|`additional-source-cnc-2022-23`|employee-scope-accepted|[cnc-sofi-2022-23-employees](../follow-through-cnc/2022-23.json.gzip) (278)|
|79|`additional-source-cnc-2023-24`|employee-scope-accepted|[cnc-sofi-2023-24-employees](../follow-through-cnc/2023-24.json.gzip) (312)|
|80|`additional-source-cnc-2024-25`|employee-scope-accepted|[cnc-sofi-2024-25-employees](../follow-through-cnc/2024-25.json.gzip) (338)|
|81|`additional-source-translink-2025`|employee-scope-accepted|[follow-through-translink-2025-translink-employees](../follow-through-translink/translink-2025.json.gzip) (906)<br>[follow-through-translink-2025-british-columbia-rapid-transit-company-employees](../follow-through-translink/british-columbia-rapid-transit-company-2025.json.gzip) (1,222)<br>[follow-through-translink-2025-coast-mountain-bus-company-employees](../follow-through-translink/coast-mountain-bus-company-2025.json.gzip) (4,340)<br>[follow-through-translink-2025-transit-police-employees](../follow-through-translink/transit-police-2025.json.gzip) (266)<br>[follow-through-translink-2025-west-coast-express-employees](../follow-through-translink/west-coast-express-2025.json.gzip) (6)|
|82|`additional-source-translink-2024`|employee-report-partially-accepted|[follow-through-translink-2024-translink-employees](../follow-through-translink/translink-2024.json.gzip) (799)<br>[follow-through-translink-2024-british-columbia-rapid-transit-company-employees](../follow-through-translink/british-columbia-rapid-transit-company-2024.json.gzip) (1,129)<br>[follow-through-translink-2024-transit-police-employees](../follow-through-translink/transit-police-2024.json.gzip) (264)<br>[follow-through-translink-2024-west-coast-express-employees](../follow-through-translink/west-coast-express-2024.json.gzip) (6)|
|83|`additional-source-translink-2023`|employee-scope-accepted|[follow-through-translink-2023-translink-employees](../follow-through-translink/translink-2023.json.gzip) (654)<br>[follow-through-translink-2023-british-columbia-rapid-transit-company-employees](../follow-through-translink/british-columbia-rapid-transit-company-2023.json.gzip) (1,029)<br>[follow-through-translink-2023-coast-mountain-bus-company-employees](../follow-through-translink/coast-mountain-bus-company-2023.json.gzip) (3,504)<br>[follow-through-translink-2023-transit-police-employees](../follow-through-translink/transit-police-2023.json.gzip) (233)<br>[follow-through-translink-2023-west-coast-express-employees](../follow-through-translink/west-coast-express-2023.json.gzip) (6)|
|84|`additional-source-translink-2022`|employee-scope-accepted|[follow-through-translink-2022-translink-employees](../follow-through-translink/translink-2022.json.gzip) (578)<br>[follow-through-translink-2022-british-columbia-rapid-transit-company-employees](../follow-through-translink/british-columbia-rapid-transit-company-2022.json.gzip) (893)<br>[follow-through-translink-2022-coast-mountain-bus-company-employees](../follow-through-translink/coast-mountain-bus-company-2022.json.gzip) (2,874)<br>[follow-through-translink-2022-transit-police-employees](../follow-through-translink/transit-police-2022.json.gzip) (238)<br>[follow-through-translink-2022-west-coast-express-employees](../follow-through-translink/west-coast-express-2022.json.gzip) (7)|
|85|`additional-source-translink-2021`|employee-scope-accepted|[follow-through-translink-2021-translink-employees](../follow-through-translink/translink-2021.json.gzip) (604)<br>[follow-through-translink-2021-british-columbia-rapid-transit-company-employees](../follow-through-translink/british-columbia-rapid-transit-company-2021.json.gzip) (857)<br>[follow-through-translink-2021-coast-mountain-bus-company-employees](../follow-through-translink/coast-mountain-bus-company-2021.json.gzip) (2,496)<br>[follow-through-translink-2021-transit-police-employees](../follow-through-translink/transit-police-2021.json.gzip) (229)<br>[follow-through-translink-2021-west-coast-express-employees](../follow-through-translink/west-coast-express-2021.json.gzip) (7)|
|86|`additional-source-translink-2020`|employee-scope-accepted|[follow-through-translink-2020-translink-employees](../follow-through-translink/translink-2020.json.gzip) (557)<br>[follow-through-translink-2020-british-columbia-rapid-transit-company-employees](../follow-through-translink/british-columbia-rapid-transit-company-2020.json.gzip) (847)<br>[follow-through-translink-2020-coast-mountain-bus-company-employees](../follow-through-translink/coast-mountain-bus-company-2020.json.gzip) (2,635)<br>[follow-through-translink-2020-transit-police-employees](../follow-through-translink/transit-police-2020.json.gzip) (210)<br>[follow-through-translink-2020-west-coast-express-employees](../follow-through-translink/west-coast-express-2020.json.gzip) (6)|
|87|`additional-source-langara-2024-25`|employee-scope-accepted|[langara-sofi-2024-25-employees](../follow-through-langara/langara-2024-25.json.gzip) (950)|
|88|`additional-source-langara-2023-24`|employee-scope-accepted|[langara-sofi-2023-24-employees](../follow-through-langara/langara-2023-24.json.gzip) (891)|
|89|`additional-source-langara-2022-23`|employee-scope-accepted|[langara-sofi-2022-23-employees](../follow-through-langara/langara-2022-23.json.gzip) (710)|
|90|`additional-source-bcfsa-2025-26`|employee-scope-accepted|[follow-through-bcfsa-2025-26-employees](../follow-through-small-crowns/bcfsa-2025-26.json.gzip) (307)|
|91|`additional-source-bcfsa-2024-25`|employee-scope-accepted|[follow-through-bcfsa-2024-25-employees](../follow-through-small-crowns/bcfsa-2024-25.json.gzip) (286)|
|92|`additional-source-bcfsa-2023-24`|employee-scope-accepted|[follow-through-bcfsa-2023-24-employees](../follow-through-small-crowns/bcfsa-2023-24.json.gzip) (257)|
|93|`additional-source-bcfsa-2022-23`|employee-scope-accepted|[follow-through-bcfsa-2022-23-employees](../follow-through-small-crowns/bcfsa-2022-23.json.gzip) (237)|
|94|`additional-source-bcfsa-2021-22`|employee-scope-accepted|[follow-through-bcfsa-2021-22-employees](../follow-through-small-crowns/bcfsa-2021-22.json.gzip) (161)|
|95|`additional-source-bcfsa-2020-21`|employee-scope-accepted|[follow-through-bcfsa-2020-21-employees](../follow-through-small-crowns/bcfsa-2020-21.json.gzip) (112)|
|96|`additional-source-bcfsa-2019-20`|employee-scope-accepted|[follow-through-bcfsa-2019-20-employees](../follow-through-small-crowns/bcfsa-2019-20.json.gzip) (6)|
|97|`additional-source-pavco-2024-25`|employee-scope-accepted|[follow-through-pavco-2024-25-employees](../follow-through-small-crowns/pavco-2024-25.json.gzip) (178)|
|98|`additional-source-clbc-2024-25`|employee-scope-accepted|[additional-source-clbc-2024-25-employees](../follow-through-clbc/2024-25.json.gzip) (521)|
|99|`additional-source-clbc-2023-24`|employee-scope-accepted|[additional-source-clbc-2023-24-employees](../follow-through-clbc/2023-24.json.gzip) (453)|
|100|`additional-source-clbc-2022-23`|employee-scope-accepted|[additional-source-clbc-2022-23-employees](../follow-through-clbc/2022-23.json.gzip) (299)|
|101|`additional-source-clbc-2021-22`|employee-scope-accepted|[additional-source-clbc-2021-22-employees](../follow-through-clbc/2021-22.json.gzip) (302)|
|102|`additional-source-clbc-2020-21`|employee-scope-accepted|[additional-source-clbc-2020-21-employees](../follow-through-clbc/2020-21.json.gzip) (306)|
|103|`additional-source-clbc-2019-20`|employee-scope-accepted|[additional-source-clbc-2019-20-employees](../follow-through-clbc/2019-20.json.gzip) (175)|
|104|`additional-source-clbc-2018-19`|employee-scope-accepted|[additional-source-clbc-2018-19-employees](../follow-through-clbc/2018-19.json.gzip) (137)|
|105|`additional-source-clbc-2017-18`|employee-scope-accepted|[additional-source-clbc-2017-18-employees](../follow-through-clbc/2017-18.json.gzip) (139)|
|106|`additional-source-clbc-2016-17`|employee-scope-accepted|[additional-source-clbc-2016-17-employees](../follow-through-clbc/2016-17.json.gzip) (108)|
|107|`additional-source-clbc-2015-16`|employee-scope-accepted|[additional-source-clbc-2015-16-employees](../follow-through-clbc/2015-16.json.gzip) (93)|
|108|`additional-source-clbc-2014-15`|employee-scope-accepted|[additional-source-clbc-2014-15-employees](../follow-through-clbc/2014-15.json.gzip) (108)|
|109|`additional-source-clbc-2013-14`|employee-scope-accepted|[additional-source-clbc-2013-14-employees](../follow-through-clbc/2013-14.json.gzip) (93)|
|110|`additional-source-clbc-2012-13`|employee-scope-accepted|[additional-source-clbc-2012-13-employees](../follow-through-clbc/2012-13.json.gzip) (91)|
|111|`additional-source-clbc-2011-12`|employee-scope-accepted|[additional-source-clbc-2011-12-employees](../follow-through-clbc/2011-12.json.gzip) (81)|
|112|`additional-source-clbc-2010-11`|employee-scope-accepted|[additional-source-clbc-2010-11-employees](../follow-through-clbc/2010-11.json.gzip) (83)|
|113|`additional-source-clbc-2009-10`|employee-scope-accepted|[additional-source-clbc-2009-10-employees](../follow-through-clbc/2009-10.json.gzip) (68)|
|114|`additional-source-clbc-2008-09`|employee-scope-accepted|[additional-source-clbc-2008-09-employees](../follow-through-clbc/2008-09.json.gzip) (64)|
|115|`additional-source-clbc-2007-08`|employee-scope-accepted|[additional-source-clbc-2007-08-employees](../follow-through-clbc/2007-08.json.gzip) (53)|
|116|`additional-source-clbc-2006-07`|employee-scope-accepted|[additional-source-clbc-2006-07-employees](../follow-through-clbc/2006-07.json.gzip) (40)|
|117|`additional-source-clbc-2005-06`|employee-scope-accepted|[additional-source-clbc-2005-06-employees](../follow-through-clbc/2005-06.json.gzip) (4)|
|118|`additional-source-worksafebc-2023`|employee-scope-accepted|[worksafebc-2023-sofi-employees](../follow-through-worksafe-uvic/worksafebc-2023-employees.json.gzip) (2,794)|
|119|`additional-source-worksafebc-2024`|employee-scope-accepted|[worksafebc-2024-sofi-employees](../follow-through-worksafe-uvic/worksafebc-2024-employees.json.gzip) (3,058)|
|120|`additional-source-worksafebc-2025`|employee-scope-accepted|[worksafebc-2025-sofi-employees](../follow-through-worksafe-uvic/worksafebc-2025-employees.json.gzip) (3,142)|
|121|`additional-source-uvic-2024-25`|employee-scope-accepted|[uvic-2024-25-sofi-employees](../follow-through-worksafe-uvic/uvic-2024-25-employees.json.gzip) (2,227)|
|122|`additional-source-uvic-2023-24`|employee-scope-accepted|[uvic-2023-24-sofi-employees](../follow-through-worksafe-uvic/uvic-2023-24-employees.json.gzip) (2,072)|
|123|`additional-source-uvic-2019-20`|employee-scope-accepted|[uvic-2019-20-sofi-employees](../follow-through-worksafe-uvic/uvic-2019-20-employees.json.gzip) (1,422)|
|124|`additional-source-bcib-2024-25`|employee-scope-accepted|[follow-through-bcib-2024-25-employees](../follow-through-small-crowns/bcib-2024-25.json.gzip) (1,122)|
|125|`additional-source-bcib-2023-24`|employee-scope-accepted|[follow-through-bcib-2023-24-employees](../follow-through-small-crowns/bcib-2023-24.json.gzip) (805)|
|126|`additional-source-bcib-2022-23`|employee-scope-accepted|[follow-through-bcib-2022-23-employees](../follow-through-small-crowns/bcib-2022-23.json.gzip) (558)|
|127|`additional-source-bcib-2021-22`|employee-scope-accepted|[follow-through-bcib-2021-22-employees](../follow-through-small-crowns/bcib-2021-22.json.gzip) (185)|
|128|`additional-source-bcib-2020-21`|employee-scope-accepted|[follow-through-bcib-2020-21-employees](../follow-through-small-crowns/bcib-2020-21.json.gzip) (28)|
|129|`additional-source-bcib-2019-20`|employee-scope-accepted|[follow-through-bcib-2019-20-employees](../follow-through-small-crowns/bcib-2019-20.json.gzip) (13)|
|130|`additional-source-rru-2021-22`|employee-scope-accepted|[rru-sofi-2021-22-employees](../follow-through-rru/rru-2021-22.json.gzip) (223)|
|131|`additional-source-rru-2022-23`|employee-scope-accepted|[rru-sofi-2022-23-employees](../follow-through-rru/rru-2022-23.json.gzip) (256)|
|132|`additional-source-rru-2023-24`|employee-scope-accepted|[rru-sofi-2023-24-employees](../follow-through-rru/rru-2023-24.json.gzip) (307)|
|133|`additional-source-rru-2024-25`|employee-scope-accepted|[rru-sofi-2024-25-employees](../follow-through-rru/rru-2024-25.json.gzip) (321)|
|134|`additional-source-rru-2025-26`|employee-scope-accepted|[rru-sofi-2025-26-employees](../follow-through-rru/rru-2025-26.json.gzip) (334)|
