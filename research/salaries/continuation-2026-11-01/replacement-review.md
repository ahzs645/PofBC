# Reviewed compiled replacements and retained overlaps

New source schedules do not silently establish the reporting dates, scope or identities in older compiled data. The full comparison preserves multiplicity, order of name tokens and every given name/initial; case/punctuation and whole-dollar pay normalization are comparison-only. Source amounts, expenses, titles and names are never rounded or enriched in the accepted data.

## Same-fiscal-year employee replacements

These eleven complete cohorts match every compiled name/pay observation in the actual corresponding fiscal original. Counts and scope agree; no unmatched board observations are discarded. A compiler title or missing/rounded expense is not carried into an official record without original support. Original/data hashes and immutable baseline export hashes are pinned in the JSON.

| Employer | Verified fiscal year | Compiled records replaced |
| --- | --- | ---: |
| bc-housing | 2023/24 | 490 |
| bclc | 2020/21 | 657 |
| bclc | 2023/24 | 970 |
| capilano-university | 2020/21 | 370 |
| capilano-university | 2023/24 | 436 |
| icbc | 2020/21 | 2427 |
| icbc | 2023/24 | 3133 |
| okanagan-college | 2023/24 | 536 |
| university-of-the-fraser-valley | 2020/21 | 511 |
| university-of-the-fraser-valley | 2023/24 | 673 |
| vancouver-island-university | 2020/21 | 627 |

Total reviewed replacements: **10,830**.

## Compiled partitions retained alongside qualified originals

| Employer | Compiled label | Retained compiled records | Same-label name/rounded-pay matches |
| --- | --- | ---: | ---: |
| bclc | 2017/18 | 481 | 478 |
| icbc | 2017/18 | 1709 | 1681 |
| royal-bc-museum | 2023/24 | 33 | 0 |
| douglas-college | 2023/24 | 678 | 676 |
| camosun-college | 2017/18 | 438 | 420 |
| camosun-college | 2020/21 | 496 | 491 |
| emily-carr-university | 2023/24 | 170 | 169 |

ICBC 2017/18 includes thirteen explicit compiled Board of Directors rows and other unmatched observations; generic employee Director job titles are not treated as board membership. Camosun employee tables explicitly omit board-member employees and severance, and their compiled scope remains broader/unverified. Douglas, Emily Carr and BCLC each retain unmatched observations despite matching headline counts.

The Museum’s compiled 2023/24 partition has 33 rows matching the actual 2022/23 original only after whole-dollar normalization; the actual 2023/24 original has 55 different rows. That is a strong period-overlap lead, but this pass makes no compiler-period repair and retains the unverified compiled partition with a visible warning. It does not declare its expense missingness or reporting dates proved from salary matching.

Retained partitions contain **4,005** compiled observations across **7** employer-periods. All are still available in the app; grouped name cards do not authorize deleting them. The builder requires an explicit public warning and retention validation reason, with consistent partial-schedule flags.

Reproduce the comparison from the immutable baseline Git commit with `node scripts/review-continuation-compiled.mjs` (the baseline commit must be available locally). CI verifies every adopted source/data hash, partition count and explicit decision without needing a network fetch.

CI verifies the exact selected compiled row multisets against the immutable compiled snapshot, as well as the accepted original and normalized source hashes. The row fingerprints preserve literal names, positions, cents, null expenses and multiplicity; see `compiledRowsSha256` and the method in [the decision ledger](replacement-review.json).
