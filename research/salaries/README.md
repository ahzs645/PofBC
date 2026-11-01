# Salary audit, source recovery and remaining gaps

For the latest municipal work, start with [import assumptions and the acquisition
list](municipal-audit/follow-up.md), including a spreadsheet of all remaining
source tasks and uncovered jurisdictions. The app exports now contain **881,002
records**, including [566 verified OCR observations](municipal-ocr/README.md).
Three further municipal employee cohorts retain their published amounts with
visible source-subtotal warnings. No records requests have been sent.

Updated **31 October 2026**. Original audit baseline: commit
[`eabe55708952f945cf2b0733230db31d48146d88`](https://github.com/ahzs645/PofBC/commit/eabe55708952f945cf2b0733230db31d48146d88).

The original salary setup contained three compiled editions, not a continuous annual history.
This recovery replaces demonstrably incorrect employer/years with official schedules, adds earlier
and intervening years, and makes the remaining uncertainty visible in the search, employer and
government-atlas views. **A populated year is a set of disclosed payment records, not a verified
workforce census.** The catalog contains 20 fiscal period labels and 24 calendar labels. Six early calendar
labels (2002–2007) currently contain source leads only; imported calendar records begin in 2008.
These overlapping labels are not elapsed years of complete coverage. Coverage differs
substantially by employer.

## Where to inspect the results

- [October 31 municipal expansion](municipal-audit/README.md): new accepted records, source caveats, validation and review priorities.
- [All municipal jurisdictions](municipal-audit/coverage.md): province-wide coverage table, official archive links, missing schedules and next steps.
- [Municipal machine-readable audit](municipal-audit/coverage.json): all 162 roster entries, accepted cohorts, held sources, and discovered links.

- [October 30 processing review](processing-review-2026-10-30.md): accepted imports, reporting-period
  decisions, unresolved controls, originals, request drafts and implementation status.
- [October 30 validation](validation-2026-10-30.json): previous-pass counts, baseline differences, tests,
  deterministic rebuild, archive integrity and browser-review limitation.
- [Every employer and its coverage](coverage-inventory.md): a complete inventory of all employer
  histories, current counts for the three original edition labels, accepted official years and remaining review flags.
- [Machine-readable coverage and audit](../../public/salaries/coverage.json): all employer/years,
  source collections, corrections, held sources, duplicate flags and import totals.
- [All accepted and pending sources](source-inventory.md): generated source register with employer, period, acceptance state and next action.
- [Official-source backlog](source-backlog.json): exact source URLs, verification status and the next
  extraction or scope check. Finding a document and importing its employee schedule are separate
  statuses.
- [Original snapshot audit](baseline-audit-2026-10-22.json): findings before any replacement or backfill.
- [Baseline manifest](baseline-manifest.json) and `compiled-baseline.json.gzip`: the immutable,
  hash-checked retained exports from the starting commit. The original external compiler CSVs were
  not committed. Already excluded Hydro-group 2020/21 input rows cannot be reconstructed from this
  snapshot; their saved exclusion counts remain available.

<!-- SUMMARY:START -->
| Measure | Original retained dataset | Current recovered dataset |
|---|---:|---:|
| Catalog period labels | 3 | 44 (20 fiscal + 24 calendar; six lead-only years) |
| Disclosure rows | 383,163 | 878,615 |
| Named disclosure rows | 378,068 | 873,376 |
| Official-source rows with attached provenance | 0 | 628,704 |
| Retained compiled rows still requiring primary-source review | 383,163 | 249,911 |
| Canonical employers | 131 | 159 |
| Populated employer/period cells | 330 | 570 |
| Duplicate-looking extra rows flagged | 456 | 311 |

The recovery adds **495,452 net disclosure rows** relative to the immutable original snapshot,
after replacements and proved duplicate corrections. Its **303 accepted normalized source
files** cover **61 employers**; **98 employers** still have no accepted original-source schedule.
Approximately **28.4% of published rows remain compiled and unverified**.
The municipal audit also includes current jurisdictions that have no salary export at all.
<!-- SUMMARY:END -->

## Follow-up: municipal expansion, 31 October 2026

This pass starts at `280e80817ec3f94827cd97b02e87c93d9b368d17`. It adds **46,779 official
observations** in **143 employee/council cohorts**, covering **125 municipality-years** in
**46 municipalities**. Five fully matched compiled employee cohorts are replaced under their
proved calendar years, removing **1,028 duplicate compiled observations** while preserving all
**38 separate council observations**. The net increase is **45,751 rows**.

Accepted official municipal coverage grows from **2 to 47 municipalities**: 46 with employee
records and one with council-only records. **114 current jurisdictions still lack accepted official
records.** The audit covers 161 current jurisdictions, including shíshálh Nation Government District
as a distinct governance case, and records Okanagan Falls separately as pending incorporation.
Metro Vancouver remains a regional district outside this municipal denominator.

The four accepted collections are [Lower Mainland](municipal-lower-mainland/README.md),
[Island and coast](municipal-island/README.md), [North and Interior](municipal-north/README.md),
and [smaller municipalities](municipal-small/README.md). The [comparison report](municipal-corrections/README.md)
explains every replaced cohort. The [complete municipal review](municipal-audit/README.md)
documents source disagreements, scanned reports, unsigned drafts, actual-year checks, provenance,
independent reviews and reproduction. Original source values and known residuals remain explicit.

## Historical follow-up: source processing, 30 October 2026

**This section records the preceding pass. Its incremental counts and then-pending source and
publication status are historical; current results appear above.**

This pass builds on the reviewed Fraser/BCIT/Transit update at
`261b5265595cd4422b079505d31f12aead792936`: 692,951 rows, 401,641 official-source rows,
291,310 compiled rows, 130 employers and 92 accepted source files. It adds **180,284 official-source
rows**, replaces **40,371 compiled rows**, and adds **139,913 net disclosure rows**. It is a local,
reviewable update; no push, merge, deployment or source request has been sent.

| Collection | Accepted official rows in this pass | Periods and treatment |
|---|---:|---|
| [Vancouver](vancouver/README.md) | 49,742 | Calendar 2008–2025; replaces 9,824 wrongly labelled compiled employee rows |
| [Interior Health](interior-health/README.md) | 65,364 | All eleven fiscal years, 2014/15–2024/25; existing compiled periods were correct |
| [Provincial OIC](public-accounts-oic/README.md) | 10,710 | Missing appointee schedules for 2006/07–2017/18 recovered from original PDFs |
| [Prince George](prince-george/README.md) | 2,478 | 2,420 employees and 58 elected officials; calendar 2019–2022, 2024 and 2025 |
| [BCCSS](bccss/README.md) and [its OCR report](bccss-ocr/README.md) | 652 | Fiscal 2016/17 and 2017/18; separate employer from PHSA |
| [Columbia Hydro Constructors](columbia-hydro-constructors/README.md) | 723 | Five named schedules, 2012/13–2016/17; 2017/18 verified aggregate-only |
| [Island Health](island-health/README.md) | 50,615 | Eight accepted years; 2022/23 count and 2023/24 expense controls remain held |

Calendar reports now use their actual `YYYY` labels; fiscal reports retain `YYYY/YY`. The correction
does not automatically shift other municipalities. Vancouver's 22 compiled mayor/councillor records
remain separately classified under their original **unverified** edition labels until the council
reports are obtained. Its official employee CSV/JSON/API checks agree, but reconciliation to every
authoritative SOFI PDF remains outstanding because tested downloads returned HTTP 403.

The CHC original-PDF hold is resolved. BCCSS's second report passed complete OCR/page review and
exact named controls. PHSA's ten originals are downloaded but remain scanned, unaccepted sources;
the spreadsheet request is drafted. Seventeen BCI/BC Pension executive records are structured in
[executive staging](executive-staging/README.md), outside the employee build. One inferred employee
travel join is cleared after the recovered OIC cohort makes the disclosed name non-unique.
See the [full review](processing-review-2026-10-30.md) for source-specific exceptions and residuals,
and [request drafts](requests/source-requests-2026-10-30.md) for the remaining acquisition routes.

## Historical follow-up: interface and source recovery, 23 October 2026

**This section records the preceding October 23 pass. Its incremental counts and then-pending
source status are historical; the current October 30 results appear above.**

This follow-up starts from main commit
[`cc3539464d22f0c195f3cc0d486573120841302d`](https://github.com/ahzs645/PofBC/commit/cc3539464d22f0c195f3cc0d486573120841302d),
which already contained the Hydro, Public Accounts, Northern Health, North Island, UNBC and initial
BCIT/Transit recovery described below. It adds **76,508 net records**, not a second recovery of
those earlier changes. See [the interface and source review](interface-review-2026-10-23.md).

| Collection extended | Accepted source history now | Official rows in that history | Net additional published rows in this follow-up |
|---|---|---:|---:|
| [Fraser Health](fraser-health/README.md) | Every year, 2015/16–2024/25 | 99,712 | 67,780 |
| [BCIT](bcit/README.md) | 2014/15, 2016/17–2018/19, 2020/21–2024/25 | 10,624 | 6,973 |
| [BC Transit](bc-transit/README.md) | 2015/16, 2016/17, 2019/20, 2020/21, 2025/26 | 2,140 | 1,755 |

The three importers retain physical PDF pages, published names, missing/zero/negative expense
semantics and source residuals. Fraser and BCIT include exactly $75,000; their UI threshold now
says **at least $75,000**. BCIT's truncated 2020/21 names remain truncated and carry a caveat.

The interface now supports compound-surname searches and finding names within position groups,
persists year and sector choices in links, offers a compact year selector on narrow screens,
shows disclosed zero expenses, and distinguishes accepted, compiled, located, held and missing
data. Employer, person and atlas records link to the actual PDF page where available. The
headline includes anonymous records instead of silently counting only named people.

The [source inventory](source-inventory.md) is generated from accepted manifests and the
[backlog](source-backlog.json). It includes **20 additional exact employee-report links** from
PHSA and Island Health, with extraction still pending, and correctly records the earlier Hydro
and BCIT scans as needing OCR. Finding a PDF never certifies its employee records.


The employer count changes from 131 to 130 because **“Langley City” and “City of Langley” are merged
as aliases of the same municipality**, preserving the old slug as an alias. The [City's official
site](https://www.langleycity.ca/) uses both forms. This is not a dropped employer.

## Confirmed errors and their replacements

### 1. Restore the Hydro-group 2020/21 year from the actual report

The original notice said that the later files repeated the earlier year “name for name and dollar
for dollar.” The repository's preserved diagnostic does not establish a literal 100% match:

| Compiled employer | Later rows reported by the old build | Matched name/pay pairs | Match share |
|---|---:|---:|---:|
| BC Hydro | 4,672 | 4,575 | 97.9% |
| Powerex | 127 | 126 | 99.2% |
| Powertech Labs | 106 | 105 | 99.1% |

Those numbers come from the [baseline manifest](baseline-manifest.json), not a new examination of
the missing original CSVs. The old detector excluded a year when at least 80% of named records
matched an adjacent catalog year; its message overstated what the heuristic proved.

The [official return for the year ended 31 March 2021](https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/financial-reports/annual-reports/BCHydro-FIA-F21.pdf)
provides an independently dated replacement:

| Employer | Verified 2020/21 records | Physical PDF pages |
|---|---:|---|
| BC Hydro | 5,374 | 76–153 |
| Powerex | 157 | 188–191 |
| Powertech Labs | 144 | 197–200 |

**BL Mo belongs to the Powerex schedule.** Its 2017/18 record is $115,833 remuneration and $693
expenses; its 2020/21 record is $122,528 and $704. The difference in published remuneration is
$6,695. This is a comparison of the disclosed name/initials, not proof of a uniquely identified
person. The display can render the initials as “B. L. Mo,” but no given names are invented.

The imports also replace incomplete retained Hydro snapshots: 2017/18 increases from 4,672 to
4,841 records, and 2023/24 from 6,066 to 6,405. Earlier and intervening reports give continuous
Hydro/Powerex/Powertech coverage from 2012/13 through 2023/24; Powertech also has accepted 2024/25
records. See [Hydro methodology and yearly sources](hydro/README.md).

### 2. The public-service “2020/21” partition is actually 2019/20

All **10,633** compiled name/pay pairs match the official **2019/20 ordinary-employee CSV**.
Only six pairs match the actual 2020/21 ordinary-employee CSV. The exact source hashes and overlap
evidence are in [`public-accounts/sources.json`](public-accounts/sources.json), under
`compiledYearCorrection`.

The replacement draws from separately sourced ordinary-employee, deputy/associate-deputy and
appointee schedules. The verified 2020/21 union contains **13,273 payment records**: 12,444 ordinary
employees, 47 deputies/associate deputies and 782 appointee payments. The full import contains
**220,106 rows across all 20 fiscal years from 2006/07 through 2025/26**, in 60 accepted source
schedules: the preceding 209,396 rows/48 schedules plus 10,710 rows/12 recovered OIC PDFs.
The [Province's Public Accounts archive](https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/archive),
DataBC resource URLs and archived originals are recorded in the two collection manifests.

The sources themselves have defects that must not be propagated:

- Twelve purported appointee resources for years ending 2007–2018 serve byte-identical copies of
  the ordinary-employee CSV. They remain excluded resources, not imported twice. The corresponding
  early appointee cohorts have now been recovered from original PDFs in `public-accounts-oic/`.
- The 2018/19 appointee CSV has a 2018 heading. All 815 name/position/pay records were corroborated
  in the actual 2018/19 detailed-payments PDF before acceptance.
- One 2023/24 Associate Deputy Minister payment appears in both deputy and appointee schedules.
  The reviewed duplicate is excluded from the appointee import; the deputy record and the
  travel reported in that deputy schedule remain. Other unexplained cross-schedule duplicates fail
  validation.

The ordinary-employee disclosure threshold is $75,000. Deputy and appointee schedules use
different coverage rules and are labelled separately. Ministers and MLAs belong to separate
schedules; they are **not** silently classified as public-service employees. The compiled baseline
included some such records, which remain preserved in the baseline but are not carried into the
new public-service employee union. A properly sourced legislature cohort is still a separate gap.

### 3. North Island College 2020/21 contains a duplicated block

The compiled partition contains **290 rows: exactly two copies of each of 145 records**.
The [actual 2020/21 SOFI](https://nic.bc.ca/_resources/pdf/statement-of-financial-information-2020-21.pdf)
has **145 employee records** on physical PDF pages 8–12. Both extracted subtotals reconcile exactly:
**$14,487,889 remuneration** and **$149,323 expenses**.

The institution's reporting index incorrectly links its 2020/21 entry to the 2019/20 report; the
actual 2020/21 PDF remains accessible at the URL above. The cover and every employee-schedule
header confirm 31 March 2021. Two compiler transcription errors are corrected from the page
images: “Diane Dean” becomes “Diane” with “Dean” retained in the position, and “Lindsa” becomes
“Lindsay.” All 145 corrected primary name/pay/expense triples match the 145 distinct compiled
records. See [`north-island/sources.json`](north-island/sources.json).

### 4. Recover missing and incomplete institutional disclosures

**BCIT 2017/18**, formerly absent, now has **970 named employee records** from the
[official 2018 financial-information return](https://www.bcit.ca/files/financialservices/pdf/financial-information-2018.pdf),
physical PDF pages 36–57. Displayed remuneration totals $96,590,156. The employee/under-threshold
aggregate comparison leaves a $19 salary residual, and expenses leave a $3 residual. These are
compatible with individually rounded whole-dollar figures, but the source does not state their
cause. Individual values are preserved, one negative expense recovery remains negative, and the
manifest does not claim exact reconciliation. See [`bcit/sources.json`](bcit/sources.json).

<!-- ADDITIONAL_IMPORTS:START -->
**Northern Health 2020/21–2024/25** contributes **16,121 accepted employee records**, including three
new annual periods. Its 2023/24 snapshot increases from **3,285 to 3,645**: after one reviewed
shortened-name correction, **360 actual employee rows were missing** from the compiler. The five
official PDFs were checked row by row using both layout text and positioned PDF words, with every
page covered. Small whole-dollar residuals are recorded without altering individual values.
Its 2020/21 count stays at 2,500, but six compiled role-labelled executive entries differ from the
employee SOFI; the cause and original compensation basis remain unverified. The replacement uses
the actual employee schedule. See [`northern-health/sources.json`](northern-health/sources.json).

**UNBC 2024/25** adds **457 employees with positions**, from physical pages 31–37 of the final
[official SOFI](https://www.unbc.ca/sites/default/files/sections/finance/unbc-sofi-2025-final-submission-be-uploaded-website.pdf).
Every monetary cell was independently checked using PDF character coordinates. Disclosed expenses
sum exactly to $2,588,416.01. Displayed remuneration totals $55,345,679.32, **one cent above** the
printed subtotal; the unexplained source residual is preserved and exact reconciliation is not
claimed. Ninety-nine expense dashes remain missing. The interface now displays source cents rather
than rounding all values to whole dollars. See [`unbc/sources.json`](unbc/sources.json).

**BC Transit 2020/21**, formerly absent, now has **385 employee records** recovered from the
[official scanned report](https://www.bctransit.com/wp-content/uploads/9/159/2021-07-30-FY2021-Statement-of-Financial-Information-Final-with-FS-Image.pdf).
All eight employee pages were visually reviewed and two independently rendered OCR passes compared
row by row. Explicit corrections and OCR evidence are retained. Displayed remuneration totals
$36,243,255 and expenses $320,215, respectively $2 and $7 above the printed named subtotals; both
fit the documented whole-dollar rounding bound. The report says the year includes **27 pay
periods**, versus 26 in the preceding year. See [the extraction and review record](bc-transit/README.md).
<!-- ADDITIONAL_IMPORTS:END -->

## Gaps in the whole salary setup

The original audit found **383,163 disclosure rows**, of which 378,068 had a name; 5,095 were
anonymous; 185,741 lacked positions; 456 were exact duplicate-looking extra rows; and 5,750 names
lacked a verified comma separating surname and given names. These are baseline counts, not the
current regenerated totals. They are reproducible from the preserved snapshot.

The remaining gaps fall into different categories and need different fixes:

| Gap | What has changed | What still needs work |
|---|---|---|
| Only three edition snapshots | Annual official history is imported where recovered; the catalog has 20 fiscal and 18 calendar labels | Most employers still have only the retained compiled editions; use the inventory rather than assuming all employers have annual coverage |
| Wrong or unverified reporting periods | Verified sources carry actual start/end dates; known wrong years are replaced | Remaining compiler edition labels need checking against each employer's cover and employee schedule |
| Unknown source provenance | Accepted official rows have a source ID, URL, actual reporting period and content hashes | Retained compiled rows still lack an attached employer-issued report and remain labelled unverified |
| Mixed disclosure scope | Employee, elected-official, deputy, appointee, executive-only, aggregate-only and compiled scopes are visible | Historical source cohorts and thresholds must be reviewed before comparing totals |
| Executive lists presented alongside workforce lists | BCI 2023/24 is explicitly labelled executive-only: five records | Its 363-record 2017/18 cohort is not a comparable workforce-pay series; a full later employee disclosure has not been located |
| Repeated rows and copied years | Source-proven block duplication is fixed; remaining duplicate-looking rows are flagged | Same-name, same-pay observations can be distinct people; they cannot be deleted automatically |
| Name-only person linking | All given-name tokens are preserved in grouping; conflicting middle initials no longer merge | Exact names still do not establish identity; initials and incomplete names remain suggestions, not confirmed career histories |
| Anonymous rank identifiers | 144 numbered transit-police labels are retained as unnamed position records | Those records cannot provide named person histories |
| Names with unknown ordering | The interface warns about unverified surname/given-name boundaries | Much of the issue is UBC surname-first text, while other employers use given-name-first text; no global reversal is safe |
| Missing positions | Source-specific disclosure notes distinguish absent positions | Hydro's employee schedules publish initials and pay, not job titles; titles cannot be reconstructed from this source |
| Expense semantics | Public-service travel is separately linked and labelled; missing and zero remain distinct | The travel schedule has its own $5,000 threshold and cannot be treated as all expenses |

The former first-given-name grouping produced **923 employer/year groups with differing fuller
given-name strings**. That is a count of risky grouping collisions, not 923 proven different
people. The new grouping retains the full disclosed given-name tokens, avoids joining incompatible
middle initials, and states that even exact-name histories are not independently verified identity
matches. Automatic percentage-change claims have been removed from those uncertain histories.

Dollar amounts describe the remuneration or compensation in each source. They are not necessarily
base salary, annual salary rates or a full twelve months of work. A change can reflect overtime,
leave payouts, incentives, partial-year employment, source definitions or disclosure thresholds.
The numbers are nominal dollars; this work does not inflation-adjust or normalize them for FTE.

## Earlier sources and the next recovery work

The backlog records exact URLs and distinguishes accepted imports, downloaded sources awaiting
extraction, indexed sources awaiting validation, and schedules not yet located. The most useful
remaining work is:

1. **Resolve BC Hydro and Powerex 2024/25 discrepancies.** The published Hydro named-expense sum
   differs from its aggregate-derived subtotal by **−$3,706**, beyond the maximum independent
   whole-dollar rounding bound of $3,455.50. Powerex remuneration differs by **−$95,915**, against a
   $106.50 bound. A second extraction using PDF coordinates reproduces these discrepancies. The
   source may need correction or an explanation; the cause is unknown. Review rows are preserved
   under `hydro/review/`, and both employer/years remain held. Powertech 2024/25 passes and is
   imported. Do not invent a missing person or alter an amount to force a balance.
2. **Extend the Hydro group to 2010/11 and 2011/12.** Official reports were downloaded and their
   employee periods inspected, but the tables are image-only. They need OCR, ambiguous-row review
   and full reconciliation. The 2011/12 report also covers 27 pay periods rather than the typical
   26, so year comparisons need that qualification. See `hydro/sources.json` → `unparsedSources`.
3. **Complete BC Transit's annual series.** The [official financial-report index](https://www.bctransit.com/about/corporate-reports/financial/)
   links SOFIs for years ending 2012 through 2026. Exact URLs are in the backlog. Each employee
   schedule must be separated from board members, suppliers and aggregates and checked against
   the actual report period. The inventory shows which recovered years have been accepted.
4. **Obtain PHSA spreadsheets and resolve Island Health's two held controls.** All ten PHSA
   originals for 2015/16–2024/25 are downloaded scans (1,764 pages). The existing-tabular-file
   request is drafted; otherwise complete OCR/page review is required. Eight Island Health
   schedules are accepted. Its 2022/23 employee count is 12 below the declaration and its 2023/24
   expense sum is $45,772 below the printed control. Both candidates remain held.
5. **Extend BCIT and UNBC beyond the accepted reports.** Older BCIT leads and UNBC board packages
   are recorded. A board agenda containing a draft SOFI is not automatically a final approved
   disclosure. The [UNBC financial index](https://www.unbc.ca/finance/financial-statements) also
   distinguishes consolidated statements from the fuller SOFI containing employee names.
6. **Locate full employee disclosures for BC Pension and BCI.** Finding an annual report with
   executive compensation does not fill a workforce disclosure gap. The backlog uses “employee
   schedule not yet located,” not “unavailable.”
7. **Extend provincial public-service history before 2006/07.** The [official Public Accounts
   archive](https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/archive) has
   searchable digital reports from 1999/2000. The 1999/2000–2005/06 detailed-payment PDFs are the
   next practical source series. Earlier thresholds and categories require year-specific checks.
8. **Review older historical payment volumes.** The [Legislative Library's official archive](https://www.llbc.leg.bc.ca/public/pubdocs/bcdocs2015_2/164239/index.htm)
   indexes earlier accounts, including explicit Schedule of Payments volumes for
   [1984/85](https://www.llbc.leg.bc.ca/public/PubDocs/bcdocs2015_2/164239/Public_accounts/164239_PA_1984_1985_v2.pdf)
   and [1978/79](https://www.llbc.leg.bc.ca/public/PubDocs/bcdocs2015_2/164239/Public_accounts/164239_PA_1978_79_v2.pdf).
   These large scans are source leads, not imported employee data. They need schedule selection,
   fiscal-calendar review, OCR and validation. The existence of nineteenth-century accounts in
   the archive does not by itself establish a comparable named-salary dataset.

Columbia Hydro Constructors now has its own verified schedules under the existing subsidiary id:
723 rows for 2012/13–2016/17 from [`columbia-hydro-constructors/`](columbia-hydro-constructors/README.md),
with 2017/18 as verified aggregate-only coverage. Two independent original-PDF checks produced
identical rows: the one in that collection, and the one recorded in `chc-recovery/pdf-verification/`.
Other Hydro subsidiaries, including Powertech USA where present, still need source-specific
employer mappings and schedule reviews. A suppliers-only subsidiary schedule is not
an employee disclosure. The current atlas links 45 employer bodies; salary employers outside its
model remain searchable without inventing a government relationship.

## Build, validation and user-facing behaviour

The default salary build is now reproducible **offline**, using the immutable compiled snapshot
plus the accepted normalized source collections listed in [`collections.json`](collections.json).
Each required collection must exist. Each accepted gzip must match its recorded hash, contain valid
money and reporting-period values, use an allowed employer, and agree with its declared row count and
remuneration and disclosed-expense sums before any published output is changed. Accepted sources
must declare their disclosure scope; an unclassified schedule cannot default to employee coverage.

An accepted official source normally replaces the entire legacy employer/period partition.
Vancouver's cross-period employee correction is a separate, exact-hash/count-guarded rule that
preserves council records and requires the matching accepted employee source. Multiple reviewed
source cohorts, such as public-service employees and deputies, are combined explicitly. A future
partial executive-only import must not replace a fuller employee partition without a separate
reviewed scope decision. The compiler snapshot remains unchanged for provenance and comparison.

All four public representations are rebuilt together: employer histories, surname-sharded person
records, government-atlas summaries, and a position-title index (`public/salaries/positions/`).
Row-level source IDs remain attached throughout. Normalized PDF input rows retain physical page
numbers through all exports, and row links open those pages where extracted. Money retains cents and published
negative recoveries; null is not converted to zero. Anonymous records stay with their employer and
do not appear as named people.

The repeat detector checks earlier populated years when both contain at least 20 named records,
retains multiplicity, ignores anonymous names and preserves cents. An overlap of at least 80% of
the later year's records triggers a review flag. Smaller cohorts and lower-overlap defects still
require source checks. The detector does not automatically erase a
year. Only explicit reviewed source decisions can quarantine data. Suspicious identical rows stay
flagged unless an original schedule establishes the correction, as at North Island College.

Output generation is staged and swapped only after successful validation. A normal failure during
publication restores the prior data directory. This protects against corrupt or missing inputs;
it is not a claim of a transactional filesystem across process crashes or machine failure.

The interface shows source links, source scope, reporting dates, thresholds, duplicate flags and
why a year is missing or held. It defaults to the most recent available employer year. Year and
sector filters apply to employer lists, while selecting a name preserves the full disclosed name
history rather than hiding records under the search filters. Failed requests display a retry
state rather than an empty-data claim. A compact year dropdown supplements the desktop year buttons
on narrow screens. Shared links retain year labels, sector filters and the selected employer year.

A typed name without a comma is read surname first, then surname last, then as a longer surname;
the search shows the first reading that finds a full name, says so when it is not the first, and
offers the others. Within a reading, full names rank before names that only begin as typed, and
names disclosed with initials alone are listed apart as possible matches.

Position titles are grouped by `src/salaries/positions.js`: capitals, stops, plurals, a short list
of unambiguous abbreviations (Sr, Asst, Mgr …), bracketed notes and the department the compiled
records append after " · " are set aside, and nothing more. "Teacher" and "Teacher Elementary"
remain two titles; the title page lists the second as a related title instead of merging it. The
index gives each title's records, mean, median and range by employer and year; the mean is shown
to the dollar because it is computed, not disclosed. `check:salaries` reconciles every cell with
the positioned rows of the employer files. Shared titles do not establish that two employers'
jobs are the same.

### Reading the salary pages

These notes used to be repeated on the pages themselves; they apply to every record shown.

- **What pay means.** Pay is the reported remuneration or compensation for the period, not a
  salary rate. Thresholds, reporting periods and the scope of each disclosure differ; each record
  links to the document it comes from, at its page where the parser recorded one.
- **Periods.** Calendar reports use their actual year (for example, 2023); fiscal reports keep
  their fiscal label (2023/24). A period filter can be one period or a range of them.
- **Compiled records.** Records still from the supplied pssdb compilation (the retained export
  snapshot of 22 October 2026) show no source summary. Their edition labels are not verified
  employer reporting periods, and their completeness and disclosure categories have not been
  checked against the employers' own reports. The coverage inventory lists which employer/years
  they are.
- **Missing years.** A year without a record for a name is a statement about coverage, not about
  the person. Where no usable records are imported for the associated employers in a period, that
  gap does not establish whether the person was employed or paid. Each gap on a person's page
  gives its reason on hover.
- **Names.** A typed name is read surname first, then the other way round; a comma fixes where
  given names begin ("Van der Meer, J"). A shared name is not proof of one person, and missing
  records do not establish whether someone was employed or paid.
- **Highest paid across employers.** The People view before a search lists each period's 500
  highest-paid named records across every employer (`public/salaries/people/top.json.gzip`);
  `check:salaries` rebuilds that list from the person index and compares it.
- **How pay moved.** Two measures are shown wherever a position, a title or an employer spans
  years (`src/salaries/growth.js`). *Average growth* compares a series' average in its first and
  last periods with 5 or more records, 3 or more years apart, as a compound rate a year; across
  employers each employer's own series is measured and the rates are weighed by records, so a
  title does not grow because a better-paying employer began disclosing it. It still moves when
  who is on the list changes, since only records above the threshold appear. *Typical raise* is
  the median yearly change for the same disclosed name under the same title at the same employer
  (for an employer as a whole, under any title) between two disclosures up to 3 years apart; a
  name with two records in one period is left out of that period. A shared name is not proof of
  one person, and a part year shows as a jump, which is why the median is used. The position
  index carries both for every title (`public/salaries/positions/index.json.gzip`); ranking by
  either lists only titles with 10 or more records or raises behind it.
- **An employer's trends.** *New to the list* and *off the list* compare each period's names with
  the employer's previous period of the same kind (fiscal or calendar). Crossing the disclosure
  threshold counts as either, so they are not hires and departures. An employer's charts follow
  its main kind of period; the year-by-year table lists every period.

### Reproduce and check the published dataset

```sh
npm run build:salaries
npm run check:salaries
npm test
python3 -m unittest discover -s scripts -p 'test_*.py'
python scripts/extract-hydro-salaries.py --self-test
```

`check:salaries` independently reconciles every named employer record with the person shards,
every positioned record with the title index, every atlas row and total with the employer exports, and every accepted official record with its
normalized source file, preserving multiplicities. It verifies year indices, source IDs, coverage
counts, duplicate flags, physical page references and orphan files, then refreshes
`coverage-inventory.md` and `source-inventory.md`.

Use `npm run preview:salaries` to inspect the actual salary components and the committed data
without the separate artwork/font build. `/mobile.html` embeds a 390-pixel viewport for narrow-screen
review. `npm run preview:salaries -- --build` produces a static verification bundle under the ignored
`dist-salaries/` directory. This preview is local and does not deploy the site. The existing full
site build still requires its licensed macOS Helvetica source.

The salary CI workflow runs parser fixtures, salary behavior tests, an offline rebuild, complete
export reconciliation and a salary-interface bundle build. It rejects stale generated exports.
Original PDF downloads and OCR remain explicit source-review tasks rather than CI network inputs.

Source extractors live under `scripts/`. Their manifests record source URLs and SHA-256 hashes;
reviewed scripts include fiscal-header checks, column/page completeness checks and reconciliation
details. Download caches and page images are temporary. PDFs are not bundled in the repository.
Only accepted normalized rows and durable provenance/review evidence are build inputs. Re-running
a source extractor may require Poppler, a Python PDF library or Tesseract as documented by that
extractor. It is unnecessary for a normal offline salary rebuild.

Public Accounts CSVs often do not contain an independent printed subtotal, so their manifests do
not claim one was reconciled. Whole-dollar PDF rows and aggregates may have small residuals:
rounding compatibility is recorded as a bound, not as proof of the cause. Cent-level discrepancies
are preserved and explained. Extraction never changes a published row to make an aggregate agree.

### Verification limits

The [recorded verification results](verification.json) include **44 passing JavaScript test files**,
**13 passing Python regression tests**, the Hydro extraction checks, the source-to-export
reconciliation, and a second offline build that reproduced all **749 generated files byte for
byte**. The salary-only production bundle also passed.

The repository's complete production build requires a licensed macOS Helvetica source at
`/System/Library/Fonts/Helvetica.ttc`, which this Linux environment does not contain. The salary-only
production bundle can be built and tested independently. This does not certify the unrelated
font-dependent logo pipeline. A browser rendering check could not be completed because the
connected browser could not reach the workspace preview server. These limits are separate from
the source/row reconciliation and automated tests.

## Suggested replacement for the original data notice

> **Salary data corrected and expanded.** The compiled Hydro-group records labelled 2020/21 have
> been replaced with the actual employee disclosures for the year ended 31 March 2021. That year
> is now available again for BC Hydro, Powerex and Powertech, with links to the original report.
> Powerex's “BL Mo” is listed at $122,528 in 2020/21 and $115,833 in 2017/18. Earlier and intervening
> years have also been added. Similar name/pay patterns now trigger review; source evidence
> determines whether a year is corrected or withheld.

This notice describes the data in this change. It should replace the old notice when this branch
is reviewed and deployed; it does not imply that an unmerged branch is already live.
