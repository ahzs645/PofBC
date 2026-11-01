# Independent review: northern municipal wave

Decision: **passes after the corrections below**, under the existing policy that small unresolved source-control differences retain published cells and explicit public warnings. Reviewed 12 cohorts / 401 observations: 373 employee and 28 council observations, across eight original PDFs. No collection, parser, registry or generated export was edited by this reviewer.

Reviewed manifest: `research/salaries/municipal-wave-north/sources.json`, SHA-256 `304697fcec31f9d3527eeba6d2e0af7543084afab19124ce67b9d944811bc1b6`.

## Findings corrected by the source author

1. **Dawson Creek 2024 last title included a subtotal label.** Young, T was incorrectly extracted as `Corporate Officer Consolidated total of employees with remuneration and`. On physical PDF page 37, the actual title is **Corporate Officer** at y 642.65; the separate subtotal label begins at y 653.57. The former section cutoff 655 admitted that label even though both text readers and monetary totals agreed. The author changed the cutoff to 653 and regenerated the evidence, normalized data and manifest. I rechecked the rendered original and final row. Corrected data SHA-256: `db3295165ba90e47294f14e0b6debaf57d1cee707138c749f0806329d983ef89`. This finding shows why correct totals and reader agreement do not replace row-boundary review.
2. **Chetwynd threshold equality wording was not explicit.** Both 2024/2025 reports label the named subsection `Other Employees` and the aggregate `Employees less than $75,000`. All named remuneration exceeds $75,000, but the printed equality boundary is not stated. The author set both employee `thresholdComparison` values to null and added the source wording, rather than attributing a statutory convention to the printed heading. No salary rows changed.

## Original periods, scope and columns

All original PDF hashes match their pinned manifests. Internal report/schedule headings identify calendar years, with December 31 year ends: Dawson Creek 2024; Williams Lake 2024/2025; Chetwynd 2024/2025; Taylor 2022; Northern Rockies 2024/2025. Upload years and archive filenames were not used to override these headings. No `draft` label was found in the original native text.

Rendered schedule/edge/control pages checked: Dawson Creek physical 36–37; Williams Lake 2024 physical 28–29 and 2025 physical 29, with 2025 definitions read on physical 30; Chetwynd 2024/2025 physical 4; Taylor 2022 physical 10; Northern Rockies 2024/2025 physical 4–6, with summary controls/definitions checked on physical 7/2. Council sections stay separate from the named employee cohorts. Below-threshold, supplier, severance and overall aggregate rows are excluded.

* Dawson Creek uses published Remuneration and separate Expenses with cents. Its threshold label refers to remuneration **and expenses** exceeding $75,000; every accepted named employee also has remuneration above $75,000, and the source-specific note retains that wording.
* Williams Lake definitions include wages, overtime, vacation payouts, taxable benefits and EOC pay. Expenses are separate. Named remuneration controls are derived from printed Total Other Employees minus the below-threshold remuneration aggregate; expense controls are printed directly. The 2025 report’s definition continues on physical 30.
* Chetwynd employees are correctly selected from the employee subsection of a page titled **Schedule of Council Remuneration and Expenses**. Wrapped titles remain attached to their own names, including Public Works Lead Hand Supervisor, Corporate Officer/Human Resources Manager and Director of Financial Administration.
* Taylor’s pay column is **Remuneration and Benefits**; Travel, Conference and Expenses remain separate. The combined name/title column is split at its printed delimiter, and the elected-official schedule is excluded from the 12 employee rows.
* Northern Rockies’ second employee column is **Department**, not job title. All 114 normalized employee positions remain null; supporting evidence retains the 11 actual department values. The 2025 name **ESTATE OF RYAN KERR** is preserved as published. The 2024/2025 source definitions both allow retroactive pay, vacation payouts, EOC payments and taxable benefits, and warn that reported amounts are not salary rates or take-home pay.
* Northern Rockies named controls sum the Management, IAFF, CUPE and Non-Unionized cohorts. The printed overall expense totals also appear to incorporate council expenses; they are not substituted for the named employee control.

## Controls and monetary semantics

Residuals below are **row sums minus printed/derived named controls**. All six cohorts with nonzero residuals have public warnings, without asserting rounding as their cause.

| Cohort | Rows | Pay residual | Expense residual |
| --- | ---: | ---: | ---: |
| Dawson Creek 2024 employees |89|$0|$0|
| Williams Lake 2024 employees |51|$0|+$1|
| Williams Lake 2025 employees |61|+$3|$0|
| Chetwynd 2024 employees |23|$0|$0|
| Chetwynd 2025 employees |23|$0|$0|
| Taylor 2022 employees |12|+$1|−$1|
| Northern Rockies 2024 employees |55|+$3|+$1|
| Northern Rockies 2025 employees |59|−$1|+$1|
| Dawson Creek 2024 council |7|$0|$0|
| Chetwynd 2024 council |7|$0|$0|
| Northern Rockies 2024 council |7|$0|$0|
| Northern Rockies 2025 council |7|$0|+$1|

Explicit zero expenses and missing cells remain different:401 rows contain 43 explicit zero expense cells and 62 missing expense cells. Northern Rockies 2024 prints numeric zeroes, whereas many 2025 cells are dashes; these were not normalized to the same value. Chetwynd 2025 Jones,Jean and Lajeunesse,David each have explicit zero expenses. Taylor Lafleur,T’s expense dash remains missing. No accepted row in this wave contains a negative pay/expense amount; no meaning for hypothetical negative cells is inferred.

## Reproduction

The reviewer independently hash-checked all eight original PDFs, called the parser’s read-only `read_original` for all 12 cohorts, compared every name/title-or-department/pay/expense/page cell with retained evidence, checked data fingerprints, and verified that no subtotal label remains attached to a position. This repeats both native readers after the Dawson Creek correction without writing collection files.

```sh
python3 scripts/parse_wave_north.py --cache /tmp/pofbc-wave-north --check-data
```

This read-only data check passed with 12 sources / 401 rows / 373 employees / 28 council observations. The unresolved financial residuals remain visible acceptance caveats; this review does not claim those printed controls reconcile exactly.
