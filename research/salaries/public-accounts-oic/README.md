# Recovered provincial OIC/appointee schedules, 2006/07–2017/18

Verified **30 October 2026**. This collection recovers the twelve missing appointee cohorts from the original Public Accounts Detailed Schedules of Payments. The DataBC resources incorrectly labelled as OIC for these years remain excluded in the existing `public-accounts` collection; their byte-identical ordinary-employee data are not imported again.

The twelve PDFs contain **10,759 named source rows**. Both extraction paths agree on every name, published position, remuneration cell and physical PDF page. Four rows have blank remuneration cells; 45 rows in 2011/12 overlap the specialized deputy schedule and have explicit table-preference decisions. The normalized collection therefore supplies **10,710 additional paid disclosure records**, totalling **$1,050,505,173**. These are payment records across twelve years, not unique people or a workforce census.

## Annual coverage

| Fiscal period | Printed OIC rows | Accepted paid records | Physical PDF pages | Printed pages | Accepted remuneration |
|---|---:|---:|---|---|---:|
| 2006/07 | 1,176 | 1,176 | 15–23 | 13–21 | $97,325,022 |
| 2007/08 | 1,040 | 1,040 | 15–22 | 13–20 | $92,329,244 |
| 2008/09 | 1,015 | 1,015 | 15–30 | 13–28 | $99,890,284 |
| 2009/10 | 921 | 921 | 15–29 | 13–27 | $96,556,663 |
| 2010/11 | 892 | 892 | 15–28 | 13–26 | $94,089,774 |
| 2011/12 | 995 | 949 | 15–30 | 13–28 | $100,144,493 |
| 2012/13 | 958 | 958 | 15–29 | 13–27 | $97,280,771 |
| 2013/14 | 566 | 563 | 15–23 | 13–21 | $44,789,909 |
| 2014/15 | 706 | 706 | 15–25 | 13–23 | $75,982,217 |
| 2015/16 | 780 | 780 | 11–22 | 13–24 | $81,018,187 |
| 2016/17 | 758 | 758 | 11–22 | 13–24 | $80,784,395 |
| 2017/18 | 952 | 952 | 12–26 | 13–27 | $90,314,214 |

## Original sources and reproducibility

Every exact download URL, original government URL, archive URL, PDF SHA-256, byte count, physical page range, printed-page mapping, row count and normalized hash is recorded in [sources.json](sources.json). The original PDFs total **64,114,295 bytes**. They are retrieved into a cache and are not required by the offline website build.

The [reviewed input controls](reviewed-inputs.json) pin the original files and every permitted exceptional decision. The [complete extraction evidence](review/source-extraction.json.gzip) retains all 10,759 published source rows, including the blank-pay and overlapping rows excluded from the new payment files. It also records independent-reader hashes, page counts, cross-schedule name overlaps and controls.

The 2006/07–2016/17 original files were retrieved through Internet Archive captures of the Province’s own financial-report URLs. The final missing report was located through the archive index under the newer government asset path, and the [2017/18 original PDF](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2017-18/pa-2017-18-crf-detailed-schedules-of-payments.pdf) was downloaded directly from the current official government site. Archive catalog hits were followed by full PDF retrieval and inspection; none is accepted from metadata alone.

```bash
python3 scripts/import-archived-oic-salaries.py --cache /tmp/pofbc-oic-processing --offline
python3 -m unittest discover -s scripts -p test_import_archived_oic.py -v
```

Omit `--offline` to download missing originals from the pinned source URLs. A changed hash stops the importer. The importer requires Poppler’s `pdftotext` and PyMuPDF. It validates all twelve sources before replacing any normalized output. `--output` can direct an independent reproduction to a separate directory.

## Extraction and boundary checks

The first reader uses Poppler content-stream text with strict one-line name/pay rows in 2006/07–2007/08 and alternating name/position-and-pay lines from 2008/09 onward. The second reader uses MuPDF word coordinates, derives each page’s column gutter from the currency headings, and reads money only from its actual right-aligned column. Every source row must match in order, including multiplicity and page provenance. This independent monetary-column check also prevents a numeric position label from becoming a false salary.

Both columns are checked on every page. The gutter must move with the alternating-page layout in 2015/16 and 2016/17; a fixed x coordinate would merge a right-column name into the left column. The importer checks each OIC heading, fiscal period, printed/physical page mapping, expected row count and the following Other Employees section. The single final row on physical page 29 of 2009/10 is retained. No supplier, minister, legislative-member or ordinary-employee rows enter this collection.

Selected page images were inspected for headers, table boundaries, shifted columns, blank and negative cells, and duplicate evidence. The exact visually inspected physical pages are recorded per source. This is not a claim that a human visually retyped all 10,759 rows; all source rows were independently checked through the two PDF extraction paths.

Names, punctuation, positions and published whole-dollar precision are retained, with whitespace collapsed. The two earliest reports do not publish positions, so their position fields stay null. The OIC schedules have **no $75,000 filter**. Negative remuneration is retained: −$242 in 2010/11 and −$355 in 2015/16. Source composition changes also remain visible: the 2013/14 OIC schedule has no judge-titled rows, unlike adjacent years. It is not a directly comparable workforce series.

## Monetary controls and the 2007/08 discrepancy

The reports’ summary controls are expressed in thousands of dollars. The table below compares the complete source schedule before any deputy overlap exclusions with that rounded summary. No source amount is adjusted to force agreement.

| Fiscal period | Full source salary sum | Summary, converted from thousands | Source rows minus summary |
|---|---:|---:|---:|
| 2006/07 | $97,325,022 | $97,325,000 | $+22 |
| 2007/08 | $92,329,244 | $92,328,000 | $+1,244 |
| 2008/09 | $99,890,284 | $99,890,000 | $+284 |
| 2009/10 | $96,556,663 | $96,557,000 | $-337 |
| 2010/11 | $94,089,774 | $94,090,000 | $-226 |
| 2011/12 | $108,540,622 | $108,541,000 | $-378 |
| 2012/13 | $97,280,771 | $97,281,000 | $-229 |
| 2013/14 | $44,789,909 | $44,790,000 | $-91 |
| 2014/15 | $75,982,217 | $75,982,000 | $+217 |
| 2015/16 | $81,018,187 | $81,018,000 | $+187 |
| 2016/17 | $80,784,395 | $80,784,000 | $+395 |
| 2017/18 | $90,314,214 | $90,314,000 | $+214 |

All differences except 2007/08 fit the simple bound from nearest-dollar row rounding and nearest-thousand summary rounding. That compatibility does not establish the source’s reason for each difference. The 2013/14 summary is image-based; its $44,790 thousand control was read from physical page 7 and checked visually. The salary table itself is text-based.

**2007/08 remains an explicitly disclosed source discrepancy.** Its 1,040 named rows sum to $92,329,244, while physical page 7, marked “Restated July 9, 2009,” reports $92,328 thousand. The $1,244 difference exceeds the simple $1,020 rounding bound. Every row on physical pages 15–22 agrees between the two extraction paths. The last page, its final names, and the rounded summary were visually inspected; the following Other Employees section establishes the boundary. A CDX query found one distinct archived digest for this exact document URL. The table records are accepted as printed, with the discrepancy attached; exact reconciliation and a cause for the discrepancy are not claimed.

## The 2011/12 deputy overlap

All **45** records in the specialized Deputy Ministers and Associate Deputy Ministers table on physical page 13 also occur in the OIC table. The complete specialized table was extracted again and compared with the already accepted deputy data: all names, remuneration and travel values agree, and its printed subtotals reconcile exactly to $8,396,127 salary/other compensation and $828,501 travel.

The OIC overlap includes 35 exact normalized full-name matches and ten shortened given-name forms. Those ten were reviewed as specific table overlaps using published names, roles and unique annual amounts; the mapping is not applied to any other person record. Forty-one OIC amounts equal the deputy amount; four differ by one dollar. The reviewed input lists every original OIC name, role, amount and page, alongside the retained deputy name, amount, travel and source ID.

The importer retains each specialized deputy record and its directly reported travel once. It excludes the 45 OIC observations from the additional payment files, preserving all of them in the review evidence. The four one-dollar differences remain documented source differences; they are not treated as additional payments or silently rounded away. This explicit preference is preferable to adding both annual amounts to the published total.

The printed notes on physical pages 7 and 13 describe remuneration components but do not explicitly state that these two tables overlap. The exclusions are reviewed table preferences supported by the common fiscal period, the complete 45-row cohort comparison, published roles and annual amounts. They are not an explicit deduplication instruction from the Province. [The source-note review](review/2011-12-overlap-notes.json) records that limitation and the relevant page references.

## Blank remuneration and travel attribution

One 2011/12 appointment and three 2013/14 appointments have genuinely blank remuneration cells, confirmed in the source page images. They remain in complete review evidence and are excluded from paid records. Blank does not become zero. The expected names, positions and pages are pinned, so any new blank cell stops acceptance for review.

The OIC salary tables do not themselves contain travel amounts. These recovered records therefore leave expenses null; the source note explains that separate travel has not been attributed. The existing deputy records keep directly disclosed travel.

The new OIC cohort also invalidates one earlier inferred travel join. The 2017/18 ordinary-employee record `Davidson,Heather` has $77,906 salary and had been assigned $16,000 from the separate travel schedule. The OIC table also discloses `DAVIDSON,HEATHER`, $152,771, on physical page 14. The full name is no longer unique across that year’s salary cohorts. [The manifest](sources.json) contains an `invalidatedTravelJoins` decision with exact old values and both source IDs; the build must clear the inferred employee travel assignment, preserving the original source inputs and recording the correction. The evidence does not establish that either disclosed name uniquely identifies the traveller.

## Integration and remaining limits

Add `public-accounts-oic` to the salary collection registry. Its six-column row schema is `[employerSlug, name, position, remuneration, expenses, pdfPage]`; its scope is `appointee-remuneration`, employer `public-service`, and its reporting periods are fiscal. These records add to the existing employee and deputy cohorts. The old wrong-schedule CSV exclusions remain as evidence. Existing statements that these OIC years are still wholly absent should be updated when the collection reaches the build.

Nine regression tests cover sparse and negative payments, shifted two-column pages, numeric position labels, invalid amounts, unreviewed cross-schedule overlaps, stale retained-deputy decisions, truncation, original-file hash changes and published-name preservation. A second offline reproduction is compared byte-for-byte with all generated collection outputs.

Outstanding limits are specific: the 2007/08 aggregate discrepancy is unexplained; four 2011/12 overlapping annual amounts differ by one dollar; appointee travel is not separately attributed; blank-paid appointments are not salary records; and source-year composition is not a workforce census. The source names do not establish unique personal identities. No source values were inflated, normalized to a threshold, or invented to fill those limits.
