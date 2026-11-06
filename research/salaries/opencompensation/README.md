# OpenCompensation and PofBC: coverage and measure comparison

Reviewed 4 November 2026 against PofBC main commit
[`7399fde`](https://github.com/ahzs645/PofBC/commit/7399fde18d2b278f5e99e2e201b915adadc7a8e2).
The generated [comparison](comparison.md), [JSON](comparison.json) and
[CSV](comparison.csv) contain the full captured directory and reproducible results.

## What is being compared

[OpenCompensation](https://www.opencompensation.org/) is useful as an external
discovery and consistency reference. Its current B.C. salary coverage statement
identifies 2023–2024 as the latest included historical snapshot, with 171,863 records,
varying employer coverage and newer releases not yet included. Its national headline
includes other provinces and physician-payment datasets and is not a B.C. workforce
count. The [B.C. employer directory](https://www.opencompensation.org/british-columbia/employer)
also contains earlier labels, including 2017–2018 and 2020–2021. The current
[B.C. jobs methodology page](https://www.opencompensation.org/british-columbia/jobs)
explicitly lists three indexed datasets: **2017–2018, 2020–2021 and 2023–2024**.
This is not a continuous annual series. That page identifies remuneration and
expenses as separate indexed fields and cautions that expenses are not salary.

The directory's 158 entries are **published employer names with at least 15 positive
compensation records in each name's latest included period**. Historical names can
appear separately: the directory has several UBC name variants, for example. An
employer below the minimum, an executive-only entry, or a different published name
can be absent from this directory while still occurring elsewhere on the site.
The complete captured table therefore remains a filtered reference, not the site's
entire employer or record inventory.

The comparator maps names using PofBC's existing identity rules and retained aliases.
An unresolved or ambiguous name remains unresolved. It records each official,
compiled, employee, executive, appointee and board source group separately. It
reconciles all published employer files against the repository's coverage controls
before calculating any comparison.

At the reviewed main revision, PofBC contains 1,440,498 disclosure observations,
including 1,212,134 from official sources and 228,364 retained compiled observations,
across 273 employers and 1,187 populated employer/periods. Those multi-period totals
cannot be subtracted from OpenCompensation's latest-snapshot total to estimate missing
employees. The generated report recalculates them from the files on each run.

## Compensation does not always mean remuneration

The retrieved employer pages use the label **Compensation**. For several examples,
their record count, rounded average and highest amount reproduce PofBC's original
compilation when its separately stored expenses are added to remuneration:

| Employer and external edition label | Records | Average remuneration in PofBC's compilation | Average remuneration plus expenses | OpenCompensation average |
| --- | ---: | ---: | ---: | ---: |
| [BC Infrastructure Benefits, 2023–2024](https://www.opencompensation.org/british-columbia/employer/b-c-infrastructure-benefits) | 805 | $125,203 | $131,043 | $131,043 |
| [BC Financial Services Authority, 2023–2024](https://www.opencompensation.org/british-columbia/employer/b-c-financial-services-authority) | 257 | $120,109 | $123,446 | $123,446 |
| [Vancouver Police, 2023–2024](https://www.opencompensation.org/british-columbia/employer/vancouver-police) | 1,672 | $143,921 | $145,563 | $145,563 |

The highest amounts also reproduce: $407,956, $438,313 and $523,074 respectively.
For BCIB the compiled remuneration total is $100,788,239 and the expense total is
$4,701,607; their sum divided by 805 gives $131,043.29. All expense cells in these
three compiled groups are numeric. This is a reproducible arithmetic finding,
not a claim that the site's entire processing pipeline has been independently
inspected. It does not turn expenses into salary or establish that the same
individual rows are present.

The accepted original BCIB schedule separately identifies remuneration and expenses,
and explains that most expenses relate to travel and living-out allowances. The
[official-source reconstruction](../follow-through-small-crowns/README.md) retains
those definitions and original-report links. In its accepted original rows, 603
BCIB expense cells and 22 BCFSA expense cells are unknown, while their compiled
counterparts are numeric. The diagnostic preserves that distinction: it can add
**known** expense values without declaring the unknown cells zero.

The generated report tests both remuneration alone and remuneration plus known
expenses for every available candidate source group and original compilation
group. A third diagnostic selects only positive-remuneration rows before adding
known expenses. This reproduces five additional 2017–2018 entries (UBC, Providence
Health, Okanagan College, Vancouver Community College and Emily Carr), where
expense-only rows otherwise change the denominator. Matching a count, a rounded
mean and a maximum is aggregate similarity.
It does not establish common provenance, independent corroboration, individual
identity or row-level parity. Where both definitions match because the input
expenses are zero, the report says so rather than choosing a definition.

Of the 158 captured names, 154 reproduce all three displayed aggregates under at
least one diagnostic. In 152 of those, remuneration alone does not match. The four
remaining original-compilation comparisons require source review:

| Published name and external label | External count | Original-compilation count | Review issue |
| --- | ---: | ---: | --- |
| Provincial government, 2023–2024 | 20,515 | 20,505 | Count and average differ; an aggregate comparison cannot identify the individual records. |
| BC Hydro and Power Authority, 2017–2018 | 4,892 | 4,672 | The original compilation and current official group have different counts from the external summary. |
| Powerex Corporation, 2020–2021 | 127 | Not available | This historical compiled group was held out and is absent from the preserved baseline. The current official group has 157 rows. |
| Powertech Labs Inc, 2020–2021 | 106 | Not available | This historical compiled group was held out and is absent from the preserved baseline. The current official group has 144 rows. |

These are unresolved aggregate comparisons, not newly identified missing employees.
An external match cannot justify restoring a previously held group.

## Larger PofBC counts can reflect retained evidence

Two clear source-group examples for the displayed 2023/24 label are:

| Employer | Official employee rows | Retained compiled rows | Combined published observations |
| --- | ---: | ---: | ---: |
| BC Financial Services Authority | 257 | 257 | 514 |
| BC Infrastructure Benefits | 805 | 805 | 1,610 |

These official sources explicitly carry `retainCompiledPartition` qualifications.
The compilation has not passed the repository's full source-compatible replacement
review. Adding the groups describes stored observations, not twice as many employees.
This comparison does not delete the compiled evidence to make a count match.

Similarly, PofBC's public-service 2023/24 group contains 20,373 employee records,
48 deputy-minister records and 938 appointee records. Its 21,359 observations have
different category coverage from OpenCompensation's 20,515-record provincial-government
entry. Neither the difference nor an employer-wide average establishes missing pay
records without an exact source and scope reconciliation.

For Northern Health, PofBC has 3,645 official employee records plus 10 board records
for fiscal 2023/24; the external entry reports 3,285 under its 2023–2024 label.
The distinct definitions and unresolved external reporting period remain visible.
No difference is converted into a missing-employee claim.

## Source tracing and the boundary of this review

The site's [About page](https://www.opencompensation.org/about) describes importing
machine-readable official releases, digitizing source PDFs and checking totals.
The examined static B.C. employer pages' **Official source** links lead to the
general [B.C. Public Accounts page](https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts).
That link alone does not identify the exact employer PDF, page, reporting period or
included fields. Individual record pages require JavaScript; this saved-directory
comparison is not a complete audit of those interactive record pages.

The new audit is entirely offline. It consumes the saved directory, checks its
stated filtered-table count and records SHA-256 fingerprints for the input,
aliases, every published employer file and immutable compilation. It does not
automatically crawl the external site or import its rows as official evidence.
Future evidence should be deliberately captured and reviewed before replacing
the snapshot. An API/export licence or complete row-level data delivery is not
assumed by this implementation.

The next useful acceptance step for a discrepancy is to locate the original
employer disclosure, establish exact dates and the measure definition, and
reconcile the complete source group. That work can use the existing
[source inventory](../source-inventory.md) and collection-specific validation gates.

## How the FOI series fits

The separate [workforce companion](../workforce/README.md) adds PSA-2024-42006's
2017–2024 all-employee and Victoria-office aggregates. It preserves **Average
HeadCount** and **Average Salary** as source labels, with unverified period boundaries
and calculation methods. These are aggregate observations, not named pay records.

PofBC's existing [staffing evidence](../../atlas/staffing.json) uses fiscal-year FTE
paid directly by the General Fund (and earlier Consolidated Revenue Fund wording).
FTE, the FOI headcount, the FOI salary measure and threshold-selected remuneration
records remain distinct. Victoria is an office-location subset of the all-employee
population and must never be added to it. The new series is not a census of all B.C.
public-sector employers such as health authorities, municipalities and Crown bodies.

The FOI's Victoria 2019 value of 21,405 is preserved from the original pixels on
pages 3 and 4, with its unexplained spike identified. The chart pages repeat the
table observations and are not imported a second time.

## Reproduce or update

```sh
npm run audit:opencompensation
npm run check:opencompensation
npm run build:workforce
npm run check:workforce
```

To compare another deliberately reviewed saved directory without overwriting the
committed report:

```sh
node scripts/audit-opencompensation.mjs \
  --snapshot /path/to/observed-snapshot.json \
  --aliases research/salaries/opencompensation/aliases.json \
  --out /tmp/opencompensation-comparison
```

The snapshot schema is exemplified by [observed-snapshot.json](observed-snapshot.json).
It contains one observation per displayed employer name, preserving its raw period
label, positive-record count, average, maximum and source link. Only candidate labels
are normalized; reporting dates are never inferred. The workflow
**Compare saved OpenCompensation coverage** checks deterministic reports when relevant
data changes. Its success means the saved comparison reproduces, not that the
workforce or external database is complete.
