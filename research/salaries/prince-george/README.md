# City of Prince George: seven calendar years recovered

Reviewed 30 October 2026. These reports add **2,420 employee payment records** and
**58 elected-official payment records**. Each record uses its actual January to
December year, its source cents and its physical PDF page. The two cohorts have
separate source IDs/files/categories under `city-of-prince-george`.

**Update, 31 October 2026:** the original 2023 attachment has now been recovered.
Its **404 employee records and nine elected-official records** are accepted in the
[municipal-north collection](../municipal-north/README.md), with exact component
controls and independent PDF readers. Combined with this six-report collection,
Prince George now has 2,824 employee observations and 67 elected-official
observations across calendar 2019–2025. The table below includes the recovered year.

| Calendar year | Employee records | Employee remuneration | Employee expenses | Elected-official records |
|---|---:|---:|---:|---:|
| 2019 | 344 | $35,960,514.18 | $737,419.19 | 9 |
| 2020 | 383 | $39,783,531.91 | $295,107.17 | 9 |
| 2021 | 330 | $33,727,467.86 | $403,652.77 | 9 |
| 2022 | 365 | $39,114,631.12 | $469,638.76 | 13 |
| 2023 | 404 | $42,084,726.65 | $569,397.71 | 9 |
| 2024 | 467 | $51,605,355.75 | $785,536.69 | 9 |
| 2025 | 531 | $57,720,981.90 | $756,747.67 | 9 |

The [official financial-report index](https://www.princegeorge.ca/finance) supplies
the links retained in [sources.json](sources.json). The official 2023 eScribe
attachment's earlier HTTP 403 hold was resolved on 31 October. Its accepted
source IDs, original fingerprint and physical pages are recorded in
[the northern manifest](../municipal-north/sources.json); the resolved lead remains
documented in this collection's manifest.

## Extraction and controls

Every employee and elected-official row was compared as a multiset between
Poppler layout text and a separate parser using PyMuPDF's positioned words. The
check covers names, titles, all compensation/expense components, physical pages
and repeated-row multiplicity. PDF rotations are handled explicitly. Every
employee page has its actual January–December heading checked; source section
bounds and full document hashes are pinned. Named employee counts exactly equal
the source-declared counts. Every named component subtotal and every elected
component subtotal reconcile exactly in integer cents.

The review includes rendered first/last employee pages, all elected schedules,
all negative-expense rows, and the one merged text boundary. The precise inspected
pages are recorded per source. This is not a claim that every page was manually
read row by row; every row was checked by the two independent extraction paths.

Raw monetary components, in integer CAD cents, are retained in `audit/`. Source
blanks/dashes remain null in those component files. Numeric expense zero would
remain zero. Seven negative employee expenses remain negative. Employee records
are disclosures above the remuneration threshold, not a complete workforce census.

## Pay definitions and separate cohorts

For **2019–2021**, the source already prints total remuneration alongside base,
overtime, vacation and other compensation. The import uses that total once and
checks it against the component sum for every row. It does not add the total to
its components.

For **2022–2025**, the source publishes base pay and all other
compensation in separate columns. Their exact sum is the remuneration field;
expenses remain separate. The footnote defines other compensation to include
vacation, overtime, shift premiums, sick gratuity and sick-bank payouts. Base pay
alone can be below $75,000 even when total remuneration exceeds the threshold.

Library employees appear within the combined 2019 schedule and in an explicit
Library group in 2020–2023. The 2024–2025 employee schedules contain no Library
group. The import preserves the City report's actual cohort rather than assuming
all years cover the same organization boundary.

Elected officials use the report's `S.168(1)(a)` remuneration total, including the
vehicle allowance once. Their separate benefit amounts are retained in the audit
and are not silently added to remuneration. They have no employee $75,000 filter.
The 2022 table publishes 13 payment records, including outgoing and incoming
officeholders; it is not reduced to the number of simultaneous council seats.
Footnote markers are not treated as part of personal names.

## Source defects preserved or repaired from direct evidence

**2019 PDF glyph mapping.** The embedded `FranklinGothicBook` glyph 16 renders a
hyphen but extracts as a comma. The actual comma uses glyph 15. Thirty-nine field
occurrences are repaired from the glyph identity, including compound names and
titles; ordinary commas are retained. Each change is recorded in
`validation.glyphCorrections`. This is not a global punctuation replacement.
Physical page 18 also joins the final name initial to the beginning of the job
title in extracted text. Separate source text spans and the rendered page establish
`Rubadeau-Tkachuk, Jennifer A` / `Civic Events Coordinator`; no amount changed.

**2025 grand-total inconsistency.** The printed all-employees other-compensation
grand total is $3,293,593.88, but its printed named and below-threshold subtotals
($2,930,049.95 and $467,608.80) sum to $3,397,658.75. The difference is
**-$104,064.87**. All 531 named rows exactly match their own named subtotals.
The inconsistent grand total is disclosed and is not used to modify those rows.

## Reproduction

```sh
python3 scripts/import-prince-george-salaries.py --cache /path/to/pdfs --offline
python3 -m unittest scripts/test_prince_george_import.py
```

Cache filenames are `prince-george-2019.pdf`, `prince-george-2020.pdf`,
`prince-george-2021.pdf`, `prince-george-2022.pdf`, `prince-george-2024.pdf` and
`prince-george-2025.pdf`. Without `--offline`, missing sources are downloaded from
the pinned URLs. Any changed source fingerprint, unexpected row boundary,
reader disagreement, missing named row or subtotal mismatch fails before new
normalized files are written. A rerun checks the reviewed byte fingerprints and
does not imply a new visual review.
