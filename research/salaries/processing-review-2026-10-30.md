# Salary source processing — 30 October 2026

## Result and handoff status

The October 30 follow-up is implemented and reconciled on the local branch
`codex/salary-source-processing-2026-10-30`. It builds on the recovered, reviewed
Fraser/BCIT/Transit update at `261b5265595cd4422b079505d31f12aead792936`.
The resulting dataset contains **832,864 disclosure records**, including
**581,925 records attached to official sources**. This pass adds **139,913 net
records**: 180,284 new official-source records replace 40,371 compiled records
and extend coverage into additional periods and employers.

These are disclosure records, not unique people, salary rates, or a census of
employees. No production deployment, GitHub push, merge, email, or records request
has been performed. The processed package contains an incremental patch, Git
bundle, application instructions, normalized sources, scripts, review evidence,
and generated salary exports. Unchanged original documents are provided in two
separate archives.

| Measure | Reviewed preceding update | This processed update |
|---|---:|---:|
| Disclosure records | 692,951 | 832,864 |
| Named disclosure records | 687,712 | 827,625 |
| Records attached to official sources | 401,641 | 581,925 |
| Retained compiled records | 291,310 | 250,939 |
| Employers | 130 | 133 |
| Populated employer/reporting-period combinations | 401 | 445 |
| Accepted normalized source files | 92 | 160 |

The integrated output has 38 distinct period labels: 20 fiscal periods and
18 calendar years. Those are overlapping reporting periods, not 38 elapsed
years. Sixteen employers have accepted official-source records. The audit flags
311 duplicate-looking extra rows without automatically deleting them or assuming
that matching names identify the same person.

## Reporting-period and employer decisions

**Calendar reports use their actual four-digit year, such as `2018`. Fiscal
reports retain their actual `2017/18` form.** A calendar report is not assigned to
whichever fiscal year it overlaps most. Explicit start/end dates accompany the
new calendar sources. Unverified labels inherited from the supplied compilation
remain identified as unverified until that employer's source has been checked.

Vancouver's employee comparison proves a particular correction for Vancouver.
It does not justify shifting every municipality's records. Interior Health's
three existing compiled slices, for example, correspond to the fiscal years
already shown. Year selectors, coverage strips and person views distinguish
period types so that adding calendar data does not create false gaps in a
fiscal-only employer's history.

Employee and elected-official disclosures remain separate categories. Prince
George has separately accepted employee and mayor/council schedules. Vancouver's
22 retained compiled mayor/councillor records remain classified as elected
officials, under their original unverified edition labels, pending original
reports. BCCSS is a separate legal employer from PHSA. Columbia Hydro Constructors
uses its existing subsidiary identifier in the government panel.

## Accepted additions and replacements

| Collection | Accepted periods in this pass | New official-source records | Net additional records |
|---|---|---:|---:|
| Vancouver employees | Calendar 2008–2025, 18 years | 49,742 | 39,918 |
| Interior Health employees | FY2014/15–2024/25, 11 years | 65,364 | 46,510 |
| Provincial OIC/appointees | FY2006/07–2017/18, 12 years | 10,710 | 10,710 |
| Prince George | Calendar 2019–2022, 2024, 2025 | 2,478 | 2,478 |
| BCCSS employees | FY2016/17 and FY2017/18 | 652 | 652 |
| Columbia Hydro Constructors employees | FY2012/13–2016/17 | 723 | 723 |
| Island Health employees | Eight accepted fiscal periods | 50,615 | 38,922 |
| **Total** | **68 additional accepted source files** | **180,284** | **139,913** |

### Vancouver: corrected dates and an official employee series

The [City's employee-remuneration dataset](https://opendata.vancouver.ca/explore/dataset/employee-remuneration-and-expenses-earning-over-75000/)
supplies 49,742 records for calendar 2008–2025. The exact CSV, alternate JSON,
annual API controls, source metadata, hashes and comparison evidence are retained.
Every field and repeated-row multiplicity agrees across CSV and JSON. All 18
annual counts and remuneration/expense totals agree with the API aggregation,
allowing only sub-cent floating serialization differences in the controls.

| Previous compiled label | Verified employee period | Compiled employee records replaced |
|---|---|---:|
| 2017/18 | Calendar 2018 | 2,738 |
| 2020/21 | Calendar 2020 | 3,003 |
| 2023/24 | Calendar 2023 | 4,083 |

All 9,824 compiled employee name/pay pairs match after documented comparison-only
normalization. The import retains original names and cents. It also preserves
two negative expense entries, 2,410 blank expense values as missing, explicit
zeros, and 556 published asterisk annotations. One 2017 record is exactly $75,000
despite the dataset's strict-over title; that source exception is documented.
The importer validates the complete candidate collection before publishing it,
and fails closed if source fingerprints or controls change.

**Limit:** CSV, JSON and API totals are consistency checks of the same City
dataset. They are not independent reconciliation to all 18 SOFI PDFs. The City
identifies the published SOFI as authoritative. Tested financial-report downloads
returned HTTP 403 here. The [council dataset](https://opendata.vancouver.ca/explore/dataset/council-budget-and-expenses/)
identified the 2020 and 2023 archive links, but those downloads also returned
403. Office budgets, expenses and accruals cannot automatically substitute for
council remuneration. The 22 council records were not moved to calendar years
based solely on an employee-table match.

Evidence: `vancouver/README.md`, `sources.json`,
`compiled-period-comparison.json`, and `raw/`.

### Interior Health: eleven complete employee schedules

The [official financial-reporting index](https://www.interiorhealth.ca/about-ih/accountability/financial-reporting)
provides eleven reports for FY2014/15–2024/25. All **65,364 employee rows** agree
between Poppler text extraction and an independent PyMuPDF coordinate extraction
across 1,521 schedule pages. Source row counts, page coverage, monetary controls
and residuals are recorded by year. Sixty-seven negative-expense rows received
visual checks; 28,518 dash expense values remain missing rather than zero.

The three existing compiled slices use the correct fiscal periods. Replacing
18,854 compiled rows and adding the other periods produces 46,510 net records.
An exact-$75,000 record in FY2020/21 is a narrowly documented source exception.
Printed-control residuals are retained; no individual's pay or expense was changed
to make a total balance.

Evidence: `interior-health/README.md`, `sources.json`, and annual review files.

### Provincial OIC schedules: the known twelve-year hole is filled

Original Detailed Schedules of Payments were recovered from the
[provincial Public Accounts archive](https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/archive)
and the [Legislative Library collection](https://www.llbc.leg.bc.ca/public/pubdocs/bcdocs2015_2/164239/index.htm).
They restore **10,710 paid appointee records** for FY2006/07–2017/18. The previously
mislabelled catalogue CSV resources remain excluded because they duplicate the
ordinary-employee schedules. Their exclusion no longer implies the original
appointee reports are missing.

Both extraction engines agree on 10,759 original observations. Four blank-pay
observations remain in review evidence rather than becoming fabricated zero
payments. A further 45 FY2011/12 observations overlap the separately imported
deputy-minister table. Their exclusion from the added OIC cohort is a documented,
source-specific preference for the existing deputy table: 41 amounts match
exactly and four differ by $1; ten names use shorter given-name forms. This is a
reviewed inference from the full cohort, roles and amounts, **not** an instruction
in an explicit provincial overlap footnote. All original observations remain
available for inspection.

The accepted FY2007/08 row sum is $92,329,244, which is $1,244 above the summary
amount expressed in thousands. The difference is unexplained. Each displayed
row was checked with both extractors and no value was adjusted to force the
summary to balance. Appointee schedules retain below-$75,000 and negative
payments; the ordinary-employee threshold does not apply to this category.

Recovery also invalidated one earlier inferred travel join. A newly recovered
appointee payment makes the disclosed name non-unique across cohorts. The
previous $16,000 travel assignment on one FY2017/18 employee record is now
missing, with an exact, guarded audit decision. It was not reassigned to either
salary record without further evidence.

Evidence: `public-accounts-oic/README.md`, `sources.json`, `review/`, and the
generated `travelJoinCorrections` audit.

### Prince George: total remuneration and council kept distinct

Six SOFIs linked from [City finance](https://www.princegeorge.ca/finance) supply
**2,420 employee rows and 58 elected-official rows** for calendar 2019, 2020,
2021, 2022, 2024 and 2025. Each category has its own accepted source identity.
Two independent extractions agree on the rows and components, and all named
employee/council controls reconcile to cents.

For 2019–2021 the import uses the printed total once. For 2022 onward it combines
the published base-pay and other-compensation columns once. It does not add a
base amount to an already inclusive total. Seven negative expense values remain
as printed. A 2019 font-encoding defect received 39 narrow, field-specific
corrections verified against the page images.

The 2025 all-employees other-compensation grand total differs from the component
subtotals by $104,064.87. The 531 named employee rows reconcile exactly to their
own controls, so those rows were accepted with the aggregate inconsistency
preserved. The [2023 attachment](https://pub-princegeorge.escribemeetings.com/filestream.ashx?DocumentId=26123)
remains unavailable here with HTTP 403; no 2023 candidate was imported.

Evidence: `prince-george/README.md`, `sources.json`, and per-year review evidence.

### BCCSS: two years, a separate employer

The original reports hosted on [PHSA's financial page](https://www.phsa.ca/about/accountability/budget-financials)
identify BCCSS as a separate society that began operations on April 1, 2016
with transferred PHSA services. It is represented separately in the data.
Employment history or similar names do not authorize automatic cross-employer
deduplication.

FY2016/17 contains **306 rows**, $28,855,034 remuneration and $958,981 expenses,
matching the printed named controls exactly. Both text engines agree and all
six employee pages plus the legal-entity note were visually reviewed. Its
published threshold is $75,000 or greater.

FY2017/18 contains **346 rows**, $33,202,601 remuneration and $1,352,527 expenses,
also matching the printed controls exactly. The scanned report required two OCR
configurations and a complete review of all eleven pages. Twenty-one explicit
correction occurrences across seventeen rows are documented, including mistakes
shared by both OCR passes. Both passes use Tesseract, so agreement alone is not
independent-engine proof; visual review supplies the additional check. The
published threshold is strictly above $75,000. Fifty-nine dash expense values
remain missing, and the final employee printed after the Z names is retained.

Evidence: `bccss/` and `bccss-ocr/`, including the complete compressed OCR output,
correction contexts, page references and validation results.

### Columbia Hydro Constructors: original-PDF hold resolved

Six unchanged [BC Hydro FIA returns](https://www.bchydro.com/about/accountability_reports/financial_reports.html)
match the original staged fingerprints. All **723 named rows** for
FY2012/13–2016/17 agree between the two extraction methods and with the staged
observations; all nineteen employee/summary pages were visually reviewed.
These five schedules are now accepted under the existing CHC subsidiary id.

FY2017/18 contains no named employee rows. Its verified schedule reports aggregate
remuneration of **$208,410** and expenses of **$12,021**. It is represented as
verified aggregate-only coverage. Zero named rows does not mean no employees or
no payroll, and aggregate totals do not become invented people.

Evidence: `columbia-hydro-constructors/README.md`, `sources.json`, and
`reviewed-inputs.json`.

### Island Health: eight imports, two specific holds

Ten originals were obtained from [Island Health financial reports](https://www.islandhealth.ca/about-us/plans-reports-and-policies/financial-reports).
Eight schedules are accepted: FY2015/16, 2016/17, 2017/18, 2018/19, 2019/20,
2020/21, 2021/22 and 2024/25, totalling **50,615 rows**. The two extraction methods
agree on all 69,751 observed rows across all ten candidate schedules and 1,548
employee pages. Acceptance still depends on the annual source controls.

| Held period | What remains unresolved | Treatment |
|---|---|---|
| FY2022/23 | 8,252 extracted employees versus 8,264 declared: 12 missing from the stated count | Candidate retained, no accepted import |
| FY2023/24 | Displayed expenses sum $14,592,431 versus $14,638,203 printed: $45,772 difference | Candidate retained, prior compiled data kept |

The first four accepted reports do not publish named-employee control totals or
counts. That absence is recorded as missing controls; two-reader reconstruction
and page completeness are not relabelled as a nonexistent total reconciliation.
For FY2019/20–2021/22 the report's cover and subtotal wording disagree about
whether exactly $75,000 is included; the source conflict remains visible.
FY2024/25 required narrow visual glyph corrections, and its remaining $74
remuneration/$1,335 expense residuals are preserved. Compatibility with a
whole-dollar rounding bound does not prove rounding caused a difference.

Evidence: `island-health/README.md`, `sources.json`, `review/`, and the two held
files under `staging/`. Held sources have no accepted `file` field and cannot
replace a published partition.

## Remaining sources and how to obtain them

### PHSA: originals downloaded; request spreadsheets first

All ten official employee reports for FY2015/16–2024/25 are included in the
separate PHSA archive. They contain **1,764 scanned pages**, total **277,510,838
uncompressed bytes**, and have no extractable text. They are downloaded source
documents, not accepted OCR imports. Reports that include BC Emergency Health
Services must not later be combined with a separate BCEHS series without a
documented overlap review.

A ready-to-send request asks for the existing Excel/CSV files, corrections,
counts, named subtotals and entity-scope notes. The published route is
[PHSA freedom of information requests](https://www.phsa.ca/about/accountability/freedom-of-information-requests),
**foi@phsa.ca**. No request has been sent. If spreadsheets cannot be obtained,
the next processing step is complete OCR, page review and reconciliation of each
annual schedule, rather than assuming OCR output is ready to import.

### Executive-only evidence: structured and protected from employee replacement

Three reports yield **17 reviewed executive records** in `executive-staging/`:
five from BCI 2017/18, five from BCI 2025/26, and seven from BC Pension 2025/26.
All three compensation tables were visually inspected; values are checked
against their pinned source pages. These staged records add zero rows to the
accepted employee build.

BCI's latest table includes four CAD rows and one USD row. Its incentive notes
distinguish performance years from later disbursement. Published component-total
residuals remain intact. BC Pension publishes base salary and employer pension
contributions, with additional components described in a footnote but no complete
per-person remuneration amount. Its `totalRemuneration` therefore remains missing.

The [BCI reports](https://www.bci.ca/investments/performance/reports/) and
[BC Pension publications](https://www.bcpensioncorp.ca/publications) pages remain
the primary sources. Their contact routes can be used to ask whether a separate
all-employee schedule exists. Executive tables cannot replace the retained
full-employee compilation slices.

### Earlier provincial archives

The original October 30 source packet retains 27 historical document references,
including 25 Internet Archive records and two original text PDFs. Those are
documents and sometimes alternate representations of the same year, not 27
accepted annual imports. Earlier OCR/sample-page checks establish useful leads;
they do not establish a verified row-level dataset.

The new general archive includes FY2005/06 as historical context and FY2006/07
once, deduplicated against the recovered OIC original. No 1960s–1990s employee
rows are newly accepted in this pass. The [Legislative Library collection](https://www.llbc.leg.bc.ca/public/pubdocs/bcdocs2015_2/164239/index.htm)
and the exact archive URLs in the original packet are the next sources. The
request draft identifies remaining 1998/99, 1999/2000 and accessible 2001/02
originals as follow-ups. Each year's scope, thresholds, report period and salary
versus travel tables must be read from that report before an import.

### Follow-up request file

`requests/source-requests-2026-10-30.md` contains the PHSA draft, Vancouver SOFI
and council draft, Island Health control-clarification draft, and the historical
and executive source routes. `requests/downloaded-health-sources-2026-10-30.json`
records exact URLs, hashes, page counts and text availability. No email was sent
and no fee-bearing process was started.

## Validation and practical limits

- The full JavaScript suite passed: **47 test files, zero failures**.
- Python importer/verification tests passed: **78 cases, zero failures**.
- The integrated salary build and independent export reconciliation passed for
  all **832,864 rows**, all **160 accepted normalized source files**, 184 atlas
  files and 464 person shards. Reconciliation checks row multiplicity, source
  identity, period, page and money across the exported views.
- A second offline build into a separate directory is compared byte-for-byte
  against the published data tree and generated salary module; its result is
  retained in `validation-2026-10-30.json`.
- The standalone salary preview production build passed. Interactive browser
  review could not run because the originating connected browser session was
  unavailable. This is not a claim of visual or end-to-end browser approval.
- Original-source archives passed PDF signature/readability checks, expected
  hash checks, ZIP CRC checks, and full stored-member hash verification. They
  contain unchanged source bytes, not modified PDFs or error-page substitutes.

Different checks answer different questions. Two text readers agreeing does not
resolve a contradictory published count. An official API agreeing with its CSV
does not independently validate the original SOFI. A rounded subtotal residual
is kept visible even when the accepted printed rows are complete. Thresholds,
partial-year payments, names represented only by initials, missing expenses,
negative amounts and disclosure categories remain source-specific.

## Deliverable map

| File | Contents |
|---|---|
| `PofBC-salary-source-packet-2026-10-30.zip` | Original findings, official Vancouver CSV, comparison script, source register and historical leads |
| `PofBC-salary-processed-2026-10-30.zip` | Incremental code/data update, Git bundle, application instructions, complete processing review, validation, current source register and request drafts |
| `PofBC-original-salary-sources-2026-10-30.zip` | 55 unique unchanged original files: 51 PDFs and four Vancouver data/API files; 56 source references |
| `PofBC-PHSA-original-reports-2026-10-30.zip` | Ten unchanged scanned PHSA reports, clearly marked unaccepted for employee import |
| `PofBC-salary-processing-review-2026-10-30.md` | Standalone copy of this review |

The processed update is incremental to the reviewed preceding update. A repository
that already has that update should apply only the new commit or patch. Do not
reset a working branch or reapply the earlier salary package. `APPLY.md` gives
the base commit, exact update commit, prerequisites and verification commands.
