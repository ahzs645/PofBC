# SunshineLists reference snapshots

This directory contains **partial secondary-source observations**, not a complete
SunshineLists employer database or imported salary rows. The initial
`observed-snapshot.json` records three individually reviewed employer-page
summaries. It preserves the published totals and displayed year ranges without
inventing annual counts for the years between the displayed endpoints.

## Initial evidence

| Employer | Total records across years | Unique individuals | Displayed years present |
| --- | ---: | ---: | --- |
| [Core Government](https://www.sunshinelists.ca/british-columbia/employers/core-government) | 179,103 | 36,901 | 2007–2025 |
| [Fraser Health Authority](https://www.sunshinelists.ca/british-columbia/employers/fraser-health-authority) | 111,202 | 25,991 | 2014–2025 |
| [Provincial Health Services Authority](https://www.sunshinelists.ca/british-columbia/employers/provincial-health-services-authority) | 103,411 | 23,739 | 2005–2025 |

The [employer search page](https://www.sunshinelists.ca/british-columbia/employers)
advertises BC data for 2005–2025, but its initial HTML shows only three popular
employer links. Its autocomplete requires a search term. That page does not
establish the number of employers or complete annual coverage for any employer.
The employer summaries expose totals; the annual tables are loaded separately.

[SunshineLists Terms of Use](https://www.sunshinelists.ca/terms) restrict automated
or systematic extraction without prior written permission. These tools operate
on supplied or authorized local files and make **no network requests**.

## Import a local snapshot

```bash
node scripts/import-sunshine-snapshot.mjs \
  --input supplied-snapshot.json \
  --out research/salaries/sunshine-lists/normalized-snapshot.json \
  --csv research/salaries/sunshine-lists/normalized-snapshot.csv
```

For a CSV, provide provenance separately:

```bash
node scripts/import-sunshine-snapshot.mjs \
  --input supplied-employers.csv \
  --metadata supplied-source.json \
  --out research/salaries/sunshine-lists/normalized-snapshot.json
```

For an authorized saved employer HTML page, use `--format html` and put
`employerName` in the metadata file. It must match the page's observed employer
`h3` heading after entity and whitespace normalization; legal qualifiers and
other name differences are preserved. The parser reads only the block after
that heading and before the next `h3`. Missing/mismatched identities and a
summary under another employer heading are rejected. The HTML parser extracts only explicit
`Total Records: … across … unique individuals` and `Years Present: …` summary
text. It rejects unrecognized/loading-only HTML instead of creating empty
coverage evidence. A single employer HTML page is always an incomplete
directory snapshot.

## Canonical JSON format

```json
{
  "version": 1,
  "source": {
    "url": "https://www.sunshinelists.ca/british-columbia/employers",
    "retrievedAt": "2026-11-01T06:00:00Z",
    "collectionMethod": "authorized-snapshot",
    "complete": false,
    "expectedEmployerCount": null,
    "notes": []
  },
  "employers": [
    {
      "name": "Example Employer",
      "url": "https://www.sunshinelists.ca/british-columbia/employers/example-employer",
      "years": [
        {
          "year": "2024",
          "recordCount": 123,
          "periodType": "unknown"
        }
      ]
    }
  ]
}
```

The example is synthetic. Do not treat it as an observed employer.

Each annual entry supports `year`, `recordCount`, `periodType`, `periodStart`,
`periodEnd`, `scope`, `threshold`, `thresholdComparison`, and `countBasis`. The
threshold comparison must be `>` or `>=`; an omitted comparison remains unknown.
Keep the year label as
published. A four-digit year has `periodType: "unknown"` unless source evidence
establishes calendar or fiscal reporting. Both dates must be present together.
Contradictory calendar labels/dates and malformed fiscal labels are rejected.

`recordCount: null` means an annual count is unknown; `0` means a known zero.
An employer without annual evidence has `years: []`. Neither is absence proof.

An employer may also carry:

```json
{
  "aggregate": {
    "recordCount": 12345,
    "uniqueIndividuals": 1234,
    "yearRangeLabel": "2007–2025",
    "yearMin": 2007,
    "yearMax": 2025
  }
}
```

Aggregate records and unique individuals describe different quantities. An
aggregate range never generates individual annual entries. A source-level
`countBasis` is one of `records`, `named-records`, `unique-individuals`, or
`unknown`. Use the source notes for further definitions. Counts with different
bases need review before comparison; omission remains unknown.

`source.countBasis`, when supplied, is preserved as source-level metadata.
Normalization does not infer annual bases from aggregate totals or copy the
source value into annual observations. Supply each annual entry's `countBasis`
explicitly when it is known; a unique-individual count is never relabelled as
a salary-record count.

### Long-form CSV

Required columns are `name,url,year,recordCount`. Optional columns are
`periodType,periodStart,periodEnd,scope,threshold,thresholdComparison,countBasis,aggregateRecordCount,
uniqueIndividuals,yearRangeLabel,yearMin,yearMax`.

A blank year preserves an employer-only observation. Annual values on a row
without a year are rejected. Aggregate columns may be present without a year.
Quoted commas and line breaks are supported. Duplicate employer-year entries,
conflicting names for the same URL, truncated input, unknown columns, and
malformed counts fail validation.

### Completeness evidence

`complete: true` is accepted only with `expectedEmployerCount` and a
`source.completenessEvidence` object:

```json
{
  "kind": "paginated-directory",
  "pageCount": 1,
  "reportedTotal": 1,
  "pages": [
    {
      "page": 1,
      "url": "https://example.org/authorized-directory-export",
      "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "employerUrls": [
        "https://www.sunshinelists.ca/british-columbia/employers/example-employer"
      ]
    }
  ]
}
```

This is a synthetic shape example, not actual completeness evidence. A supplied
one-file export can use one receipt; a paginated source needs one receipt for
every page. Page numbers must form the complete sequence, the reported total
must match both the normalized employer count and receipt URL count, and every
employer URL must occur exactly once. The SHA-256 values identify the retained
receipt bytes and must be valid digest strings.

The importer checks the consistency of supplied receipts; it does not fetch
or independently authenticate their contents. Its output labels this basis
`internally-reconciled-page-receipts`. Even a complete employer directory does
not prove complete annual records, matching salary thresholds, compatible
reporting periods, or person-by-person parity with PofBC.

## Validation and reproducibility

```bash
node --test scripts/sunshine-lists.test.mjs
```

The importer hashes the exact input bytes into `source.inputSha256`, validates
all content before replacing output, and writes files atomically. It rejects
outputs that would overwrite the supplied source or metadata. JSON and CSV
exports retain the annual/aggregate distinction. Employer identity mapping and
PofBC coverage comparison are separate from this source-normalization step.
