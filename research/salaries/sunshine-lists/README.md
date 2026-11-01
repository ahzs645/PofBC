# Repeatable Sunshine Lists comparison

This package compares a saved, supplied or authorized employer/year reference with
every published PofBC salary export. It also produces a consolidated processing
queue from the repository's existing original-source catalogue. It does not import
secondary-site salary rows into the official collections.

Run the current comparison:

```sh
npm run test:sunshine
npm run audit:sunshine
```

No dependency installation or network connection is needed for those commands.
Read [comparison.md](comparison.md) for the result, [comparison.json](comparison.json)
for every decision and input fingerprint, [repository-employers.csv](repository-employers.csv)
for all PofBC employers, and [work-queue.csv](work-queue.csv) for source follow-up.

## What the committed reference establishes

The reference is an explicitly **partial** snapshot of the three popular employer
pages linked by the [BC directory](https://www.sunshinelists.ca/british-columbia/employers):
Core Government, Fraser Health Authority and Provincial Health Services Authority.
Those page summaries provide employer-wide counts and year ranges. They do not
provide annual counts or verified reporting dates in the captured text. The
snapshot therefore has three employers and **zero annual observations**; ranges
are never expanded into invented yearly coverage.

Consequently the current report is **incomplete-reference**, not a finding that
PofBC matches every employer or year on Sunshine Lists. All local employer files
are still checked and reconciled independently of that external limitation.

The directory is an interactive employer search, not a published paginated export.
Its [Terms of Use](https://www.sunshinelists.ca/terms) restrict automated or
systematic extraction without prior written permission. The delivered importer
works offline. An authorized export or saved evidence can be supplied to complete
the reference; this project does not start a crawler or scheduled network job.
Sunshine Lists also [describes its source cleaning](https://www.sunshinelists.ca/about)
and advises verification against originating public bodies. Use original reports
to add or replace accepted salary observations.

## Import a new reference

The importer accepts normalized JSON, long-form CSV, and saved employer-page HTML.
See [snapshot-schema.md](snapshot-schema.md) for fields, examples and completeness
receipts. Keep the original input separately; the importer refuses to overwrite it.

```sh
# JSON carries source provenance alongside employers and years.
npm run import:sunshine -- \
  --input /path/to/authorized-export.json \
  --out /tmp/sunshine-snapshot.json

# CSV needs a separate source metadata JSON object.
npm run import:sunshine -- \
  --input /path/to/authorized-employer-years.csv \
  --metadata /path/to/source-metadata.json \
  --out /tmp/sunshine-snapshot.json

# Compare without replacing the committed reviewed snapshot or report.
npm run audit:sunshine -- \
  --snapshot /tmp/sunshine-snapshot.json \
  --out /tmp/sunshine-audit
```

Saved employer HTML only yields the visible aggregate summary. It cannot recover
annual tables that were absent from the saved page. The parser rejects malformed
counts, conflicting repeated years, invalid dates, duplicate employer URLs and
unsupported CSV columns. Blank annual counts remain unknown; numeric zero remains
zero. It preserves record counts and the site's claimed unique-individual counts
as different measures.

`complete: true` requires internally reconciled employer totals and complete page
receipts with URLs and hashes. These are provenance supplied by the collector,
not independent proof that the source omitted nothing. A complete employer roster
still does not establish a complete annual series. To require directory completeness:

```sh
npm run audit:sunshine -- \
  --snapshot /tmp/sunshine-snapshot.json \
  --out /tmp/sunshine-audit \
  --require-complete
```

That command writes the report and returns exit code 2 for incomplete reference
coverage. An ordinary audit returns successfully when an honest incomplete report
is generated; success means the computation ran, not that the data is complete.

## Matching and comparisons

Employer names use normalized exact matches and the repository's existing identity
rules. [aliases.json](aliases.json) contains explicit reviewed exceptions with
reasons. Similar names are not automatically merged. City versus district, parent
versus subsidiary, and renamed legal entities may require separate review.

Every published employer file is read. The loader checks actual rows against its
published period counts, source IDs and official/compiled totals. It preserves
source scope, threshold, reporting dates, warnings and the SHA-256 of all inputs.
Official employee records, council/board records and compiled editions stay distinct.

An annual count is comparable only when the reporting dates, declared scope,
record-count basis and threshold rule agree. Calendar years can be resolved from
an explicit calendar type. A fiscal year needs its actual start/end dates; a bare
2024 label is only a candidate for review. Unknown source fields produce review
tasks. Multiple potentially overlapping cohorts, partial disclosures and source
warnings also require review before aggregate parity is reported.

`aggregate-count-match` means the compared metadata and number of observations
agree. It does not verify individual names, payment values, unique people or
employment completeness. Higher/lower comparable counts are investigation leads,
not automatic replacement decisions.

The processing queue includes existing original-source leads as well as external
comparison findings. A PDF link, OCR task or archive lead is not an accepted import.
Keep the source's recorded next action; use the existing collection-specific
parsers, full-page review, source controls and salary build gates to accept records.

## Check what changed

Keep a previous report, update the input, then compare:

```sh
npm run audit:sunshine -- \
  --snapshot /tmp/new-sunshine-snapshot.json \
  --previous /path/to/previous-comparison.json \
  --out /tmp/updated-sunshine-audit
```

The new JSON records added/removed/changed tasks, accepted employee periods added
or removed, record-count change, and whether the reference snapshot itself changed.
Reports generated from the same reference, aliases and salary files are byte-stable.
Commit a deliberately reviewed snapshot and regenerated reports when updating this
repository; external changes do not silently rewrite accepted official salary data.

## Run in GitHub

Open **Actions → Compare salary coverage with a saved reference → Run workflow**.
Select the branch and the path to its committed authorized JSON snapshot. The
optional **require_complete** input rejects partial employer-directory coverage.
The run publishes a readable summary and a downloadable `salary-coverage-comparison`
artifact containing the JSON and CSV reports. It has read-only repository permission.

Pull requests and main-branch changes to the relevant salary files automatically
run the offline tests, regenerate the reports and check them against the committed
versions. This detects stale comparison output whenever PofBC's data changes.
There is no automatic scrape, salary import, merge, deployment or outside message.

## Filling verified gaps

This work also adds original North Island College reports through a separate,
reproducible [official-source history collection](../north-island-history/README.md).
Its source controls and replacement review are independent of the partial Sunshine
Lists snapshot. The current numbers are generated in [comparison.md](comparison.md),
so documentation does not have to duplicate changing dataset totals.

The [release reconciliation](release.json) uses the merged PR #34 dataset as its baseline. Four new NIC cohorts add 608 official observations and replace 181 compiled observations, for 427 net records. The 200 FY2024/25 observations independently verified here are already published by PR #34 and are counted once. The earlier municipal and six-sector additions remain in the baseline.

The comparison's queue covers the published source catalog and supplied reference. The broader [six-sector processing and archive queue](../continuation-2026-11-01/work-queue.csv) remains separate; queues overlap and their totals must not be added.
