# Province-wide municipal salary expansion — 31 October 2026

**Follow-up:** [Import assumptions and acquisition list](follow-up.md) now
documents three additional employee cohorts accepted as faithful transcriptions
with unresolved source subtotals and visible app warnings. The current app
contains **880,436 records**, including **630,525 official-source records**.
Montrose now has three accepted employee observations as well as council.
The figures and hold decisions below describe the original PR #23 baseline;
use [current generated coverage](coverage.md) and [the complete follow-up CSV](follow-up.csv)
for the subsequent state. Requests remain unsent.

This review expands PofBC’s official municipal salary histories and provides a
source inventory for every jurisdiction on the reviewed provincial roster. It
starts from repository commit
[`280e80817ec3f94827cd97b02e87c93d9b368d17`](https://github.com/ahzs645/PofBC/commit/280e80817ec3f94827cd97b02e87c93d9b368d17).

**46,779 official disclosure records are added. Five proved compiled employee
cohorts are replaced, removing 1,028 duplicate observations and preserving 38
separate council observations. The net increase is 45,751 records.**

This is a completed province-wide discovery and validated import pass. It is not
a claim that all municipal historical records have been obtained or transcribed.
There are still **114 current jurisdictions without accepted official records**.

## Results

| Measure | Before this pass | After this pass |
|---|---:|---:|
| All salary disclosure rows | 832,864 | 878,615 |
| Official-source rows, all sectors | 581,925 | 628,704 |
| Retained compiled rows, all sectors | 250,939 | 249,911 |
| Employers with published salary rows, all sectors | 133 | 159 |
| Municipal jurisdictions with any salary rows | 30 | 56 |
| Municipal jurisdictions with accepted official records | 2 | 47 |
| Accepted normalized source cohorts, all sectors | 160 | 303 |
| Populated employer/period cells, all sectors | 445 | 570 |

The 47 municipal jurisdictions comprise **46 with employee records** and
**Montrose with council-only records**. Across existing and newly accepted
municipal collections, there are **98,999 official municipal observations**.
Another **24,054 municipal observations remain compiled and unverified**. These
are disclosure rows, not distinct people: repeat appearances across years,
initial-only names and separate employee/council schedules cannot be treated as
unique person identifiers.

The added data consists of **143 cohorts**, covering **125 municipality-years in
46 municipalities**: 46,648 employee observations and 131 elected-official
observations. Prince George was already covered in other years; Vancouver’s
existing official history is retained without a duplicate import.

| New collection | Municipalities | Municipality-years | Employee records | Council records | Total |
|---|---:|---:|---:|---:|---:|
| [Lower Mainland](../municipal-lower-mainland/README.md) | 18 | 63 | 26,814 | 0 | 26,814 |
| [Island and coast](../municipal-island/README.md) | 8 | 29 | 10,939 | 28 | 10,967 |
| [Northern and Interior cities](../municipal-north/README.md) | 11 | 24 | 8,761 | 45 | 8,806 |
| [Smaller Interior and northern municipalities](../municipal-small/README.md) | 9 | 9 | 134 | 58 | 192 |
| **Total** | **46** | **125** | **46,648** | **131** | **46,779** |

The collection names describe research assignments; they do not constitute a
new official regional classification. Each municipality appears once in the
province-wide roster.

## Start here to go through the records

1. **[All jurisdictions and their coverage](coverage.md).** The table includes
   official archive links, accepted employee and council years, current record
   counts, retained compiled counts, and a next action for each jurisdiction.
2. **[Full machine-readable audit](coverage.json).** Use this for filtering,
   follow-up scripts or another review. Each municipality retains its accepted
   source IDs and hashes, source caveats, explicit holds, discovery receipts and
   candidate URLs. A located report is kept separate from an accepted schedule.
3. **The four collection READMEs above.** Each contains its exact accepted-year
   table, monetary column definitions, discrepancies and reproduction commands.
4. **[Reporting-period corrections](../municipal-corrections/README.md).** This
   explains the five corrected compiled cohorts and why partial overlaps remain
   unresolved.
5. **[Validation record](validation.json).** This records reconciliation, parser
   tests, deterministic build checks and the environment used for this pass.

Individual accepted records continue through the existing employer, person,
position and government-atlas exports. This update does not create employee
records from search snippets, aggregate payroll or supplier payments.

## Substantial histories recovered

| Municipality | Newly accepted employee years | Employee observations |
|---|---|---:|
| Burnaby | 2021–2025 | 6,457 |
| Surrey | 2021–2024 | 5,545 |
| Victoria | 2012–2014, 2016–2025 | 5,544 |
| Kelowna | 2019, 2021–2025 | 3,848 |
| North Vancouver District | 2017, 2019–2025 | 3,535 |
| Kamloops | 2016–2023, 2025 | 3,517 |
| Nanaimo | 2019, 2021–2025 | 2,579 |
| Saanich | 2021–2025 | 2,525 |
| West Vancouver | 2019, 2022–2025 | 2,279 |
| Maple Ridge | 2016, 2019–2025 | 2,066 |
| New Westminster | 2021–2025 | 1,841 |
| North Vancouver City | 2023–2025 | 1,061 |
| Port Coquitlam | 2021, 2023–2025 | 1,028 |
| Whistler | 2021, 2023–2025 | 849 |

Additional accepted employee schedules cover Anmore, Bowen Island, Burns Lake,
Cache Creek, Castlegar, Central Saanich, Comox, Coquitlam, Cranbrook, Delta,
Duncan, Fort St. John, Golden, Hudson’s Hope, Langley City, Lions Bay, Mackenzie,
Nakusp, Nelson, North Cowichan, Peachland, Pemberton, Penticton, Prince George,
Prince Rupert, Quesnel, Sechelt, Smithers, Squamish, Valemount and White Rock.
Montrose’s council schedule is accepted separately from its held employee table.

## Roster and source-search scope

[roster.json](roster.json) crosswalks the Province’s legal-name/incorporation
workbook with the official websites listed in the CivicInfo directory. Original
roster inputs are retained in `inputs/`.

As of 31 October 2026, the denominator is **161 current jurisdictions**. It
includes shíshálh Nation Government District as an explicitly separate governance
case; the audit does not assume ordinary municipal SOFI or FIPPA requirements
apply to it. Northern Rockies is a regional municipality and is included. Metro
Vancouver is a regional district and is excluded from this municipal denominator,
even though the existing application classifies it in its Municipalities sector.

CivicInfo already lists Okanagan Falls. The Province’s
[24 June 2026 release](https://news.gov.bc.ca/releases/2026HMA0069-000747) states
that incorporation takes effect on **6 November 2026**, so it is the 162nd roster
entry but remains pending for this audit date. Earlier municipal salary years are
not counted as missing. Jumbo Glacier was dissolved in December 2021 and is
outside the current roster; any historical records would need a separate former
employer entry.

Every roster entry received a bounded traversal of links on its official
website, with request receipts retained under `discovery/`. That pass follows at
most two link hops and nine pages per jurisdiction. Regional review also examined
finance/report indexes, open-data catalogs and council systems. Supplemental
official-domain searches are recorded under `searches/`, with selected links in
`reviewed-leads.json`.

Candidate links include annual reports, audited financial statements, finance
pages and policies as well as SOFI documents. They are not all salary schedules.
An unsuccessful request or a bounded search with no SOFI link does not prove
absence of records. The earliest year in an archive, a URL path or the shared
catalog does not establish a municipality’s creation date or its salary-history
coverage. Catalog labels 2002–2007 are currently discovery-only; accepted calendar
records still begin with Vancouver 2008.

## What changed in data handling

### Preserve actual periods and employer identities

Original cover and schedule headings establish the calendar year. Upload dates,
directory labels and compiler edition names do not. For example, Golden’s
accepted original is 2024, Hudson’s Hope is 2022, Montrose is 2023 and Nakusp is
2024 despite later upload paths. A New Hazelton attachment named 2023 begins with
a remuneration schedule headed 2022, so it remains held.

Known aliases join Bowen Island Municipality to the existing Bowen Island
employer, Township of Langley to Langley Township, and the older district names
for Mission and Delta to their established city records. Langley City and Langley
Township remain separate employers.

The five compiled corrections require a complete name/pay multiset match, not
just a similar total or partial overlap. Every chosen baseline row and accepted
source file is hash-pinned. The build rejects a changed source under the same ID.
The [comparison evidence](../municipal-corrections/comparison.json) retains all
51 compared partitions; 46 remain unresolved. Existing Vancouver corrections
are preserved in their original collection.

### Keep remuneration, benefits and expenses interpretable

Amounts are published remuneration during a reporting year. They may include
overtime, retroactive pay, taxable benefits, leave payouts, allowances or other
compensation; they are not annual base salary rates. Columns differ by source.

- Mackenzie’s employee remuneration is base pay plus other compensation. Its
  printed total includes expenses and is not used as pay. Expense-inclusive total
  columns in New Westminster, Langley City and Port Coquitlam are likewise not
  used as remuneration.
- Valemount combines employee expenses and taxable benefits. That component
  remains in audit evidence, while employee expenses stay missing.
- Kamloops and Quesnel use their published Remuneration column with separately
  disclosed benefit amounts retained separately. Kelowna 2024–2025 and Prince
  Rupert use their published Total Remuneration column. Source-specific notes
  must accompany comparisons across these series.
- Victoria’s original PDFs and its official CSV releases disagree in some
  years. The accepted PDF-backed years use the original PDF values and retain
  the differences. Victoria 2012–2014 are accepted official CSV releases with
  explicit disclosure that original-PDF reconciliation is incomplete.
- Published threshold exceptions remain present. The northern collection alone
  includes 267 disclosed employee rows with the selected remuneration at or below
  $75,000; the importer does not silently remove a row that the official table
  discloses. Blank/dash expenses remain missing, while explicit zero and negative
  adjustments remain as published.

### Preserve disagreements without forcing agreement

Each accepted source records its printed controls and exact observed residuals.
Small whole-dollar residuals and Maple Ridge’s five-cent 2025 expense residual are
documented rather than repaired by changing a person’s amount. Rounding may be a
possible explanation but is not asserted as proven reconciliation.

Independent text readers can agree because both read the same imperfect OCR layer.
Rendered-page review therefore remains necessary. A second review of the small
collection found a wrapped Mackenzie title assigned across adjacent rows and a
Valemount capitalization error. Both are corrected from the original, pinned and
tested; see its [independent review](../municipal-small/independent-review.md).

## Outstanding work, organized by the blocker

| Priority | Source or municipality | What remains | Acceptance gate |
|---|---|---|---|
| 1 | Surrey 2025 | 1,543 candidate employee rows agree between readers, but expenses exceed the printed named subtotal by $473 | Resolve the source discrepancy or obtain an amended report |
| 1 | North Vancouver City 2022 | $143 expense-subtotal discrepancy | Explain or correct the discrepancy before accepting the cohort |
| 1 | Montrose 2023 employees | Three rows total $6,503.65 in expenses versus $6,539.65 implied by printed aggregates | Resolve the $36 difference; council is independently accepted |
| 1 | West Kelowna 2025 | Employee and council rows reconcile, but the linked document is labelled draft and its approval page is unsigned | Obtain or verify the adopted/final original |
| 1 | Salmon Arm 2025 | The link labelled SOFI retrieves financial statements without named remuneration schedules | Locate the actual SOFI schedules |
| 1 | Abbotsford | Official page indicates SOFI is available on request | Obtain the public report or original spreadsheet; no request sent |
| 2 | Terrace 2017–2025; Vernon 2025; Kelowna 2020; Mission; several smaller communities | Image-based originals | OCR plus complete independent row, page and control review |
| 2 | Nanaimo 2020 | OCR extraction does not satisfy controls | Correct and independently recheck the complete schedule |
| 2 | Port Moody 2022–2023; Kamloops 2024; Richmond 2024; other held layouts | Wrapped titles/names, multiple pay components, or OCR/text inconsistencies | Review all cells and inter-row fragments, not totals alone |
| 2 | New Hazelton attachment labelled 2023 | First schedule says 2022 | Resolve period evidence before importing |
| 3 | Historical municipal archives and remaining council schedules | Located reports have not all been parsed | Verify each period and category before adding rows |
| 3 | Current jurisdictions with only a general official site or finance page | Direct SOFI discovery remains incomplete | Inspect council archives or obtain the public report |

This queue is practical work to continue; no email or record request was sent to
a municipality. A useful request would ask for the adopted SOFI, named employee
and council remuneration/expense schedules, the original spreadsheet or CSV if
available, any amendments, and the explanation of a specified control discrepancy.
Existing public records and official export formats should be used first.

## Other public records located alongside salaries

The same official report archives commonly include council remuneration,
supplier payments, grants, financial statements, debt and guarantee schedules,
and severance-agreement summaries. The
[Prince George finance page](https://www.princegeorge.ca/finance) explicitly
describes these SOFI categories and links the original reports. Its source index
also links capital-plan amendments and council documents. Victoria’s
[SOFI page](https://www.victoria.ca/city-government/resources/statement-financial-information)
links both PDFs and its open-data catalog.

Those documents are preserved as source leads where encountered. Supplier and
grant payments are not imported into the salary tables, and aggregate severance
figures do not become named employee payments. A subsequent expenditure review
can reuse the same official documents with a separate record schema.

## Reproduction and verification

The ordinary build is offline and uses only registered, normalized, hash-checked
sources. Collection parsers provide explicit commands to re-fetch pinned
originals; live downloads do not run inside the normal salary build or CI.

```bash
npm ci --ignore-scripts
python3 -m unittest discover -s scripts -p 'test_*.py'
node --test scripts/salary-data.test.mjs src/salaries/*.test.js src/government/salaries.test.js
npm run compare:municipal-periods
npm run build:salaries
npm run check:salaries
npm run audit:municipal-salaries
npm run preview:salaries -- --build
```

The export reconciler consumes every official source observation against all
published employer/person/position and atlas views, checks counts and monetary
representations, and detects missing or unindexed files. A source lead for a
municipality with no accepted rows is allowed only if its identity is in the
reviewed roster and it is not marked imported; no empty employee dataset is
invented. Precise hold reasons are preserved alongside next actions.

CI regenerates the compiled comparison, salary exports, source/coverage
inventories and municipality audit, then requires no generated-file differences.
The salary-only preview avoids the repository’s separate licensed artwork font
dependencies. Validation for this data change does not claim a new browser
usability review or an audit of every unrelated logo/artwork feature.
