# Independent SD42 source and replacement review

Reviewed 31 October 2026 by the municipal-history reviewer, separately from the
school importer author. School outputs were treated as read-only. Originals were
read from `/tmp/pofbc-schools`; reproduction was written to
`/tmp/root-cross-school`.

The original-hash verification, complete row/amount/page/order checks and controls
reproduced **32 cohorts and 10,568 observations**, comprising **10,446 employees
and 122 trustees** across 16 fiscal reports. All **66 generated files matched byte
for byte** before the requested source-warning change. Five existing school
regression checks passed. The six OCR-held years were not promoted by this review.

```bash
python3 scripts/sector_schools_sd42.py \
  --cache-dir /tmp/pofbc-schools \
  --output-dir /tmp/root-cross-school
python3 scripts/test_sector_schools.py
```

The review inspected the importer, retained evidence, original fingerprints,
cohort manifest, fiscal boundaries and control residuals. It also inspected the
rendered originals on **11 physical pages**: 2006 p6; 2010 p14; 2014 p47; 2018
p46; 2019 p48; 2024 p65; 2025 p55/p56/p64/p65; and 2026 p56. The complete
10,568 rows were reproduced through the two-reader checks; this review does not
claim a second manual visual reading of all 10,568 rows.

The rendered edge cases agree with the imports:

- The 2006 trustee cells visibly include numeric suffixes such as `23` and
  `0023`. Retaining those printed tokens avoids an unproved name correction.
- The 2014 employee schedule has no position column. Its null positions are
  faithful to the source; positions are not borrowed from another year.
- The 2018 report's physical p46 contains **all six trustees**, with a separate
  trustee total of $126,792.90 and $14,591.34 expenses. The fiscal period is
  2017/18. All six are present under `school-trustees`, without an employee
  threshold.
- The 2019 Clarkson trustee expense cell is blank. It remains missing. The
  election-term asterisks are retained in evidence and removed from display names;
  the 11 named trustee observations are retained.
- Pogrebinsky's 2024 expense visibly reads **(252.96)** and is imported as
  **−$252.96**. It is not the positive rounded $253 in the compiled copy.
- The 2025/2026 long-name boundaries for Do Coito Antunes Mafra, Dos Lima Lloyd,
  Eskandari Aloughreh, Fischer Norman, Peraleda and Rowledge-Toscani agree with
  the explicit parser exceptions. The 2025 `PENACERRADA, CARLO GATCHALI` ending
  is visibly clipped/touching the title and is retained without expanding it.
- Dos Lima Lloyd's separately disclosed recruitment-travel expenses are not
  added to remuneration. The table footnote remains in evidence.
- A higher-resolution crop of 2025 p56 confirms the thin leading digits in
  $112,476 and $112,018; these values are not lost leading-digit transcriptions.

The [central replacement review](../replacement-review.md) is supported. The
original district name and report headers identify SD42 Maple Ridge–Pitt Meadows.
The old `ridge-meadows-school-district` compiler employer is an alias of that
district, corroborated by its fiscal employee disclosures. The current canonical
alias preserves the historical employer-name strings in metadata. The app's
`school-trustees` label is **School trustee remuneration**, separate from municipal
elected officials and employee schedules.

The same-fiscal replacement covers the original scope:

| Compiled partition | Compiled rows | Official employees | Official trustees | Review |
|---|---:|---:|---:|---|
| Maple Ridge/Pitt Meadows 2017/18 | 635 | 629 | 6 | All six compiled trustees are represented in the original trustee cohort |
| Maple Ridge/Pitt Meadows 2020/21 | 755 | 756 | 7 | Official source restores Dana Sirsiris plus the seven separately disclosed trustees |
| Ridge-Meadows 2023/24 | 1,030 | 1,030 | 7 | Complete official employee schedule supersedes compiled cells; official trustee cohort is additional |

An independent diagnostic multiset comparison, rounding source cents half-up and
treating missing expenses as zero **only for the comparison**, found 635/635
2017/18 and 755/755 2020/21 name/pay/expense signatures after removing the
compiler's mechanical `0` tokens at hyphen positions. For 2023/24 it found
1,020/1,030 such signatures: remaining differences include rounding of half-dollar
cells and the sign of Pogrebinsky's expense. These comparison normalizations are
not applied to accepted names or amounts. The authority/scope replacement is not
represented as exact equality of every compiled cell.

Replacing the **2,420 compiled rows** with complete original fiscal employee and
trustee schedules therefore preserves the earlier trustee scope and corrects
source amounts, rather than silently losing council-like records. This conclusion
does not authorize the separate cross-calendar Pitt Meadows municipal partial
match; that compiled group remains retained.

One publication concern was identified: the four 2025/2026 cohorts retain nonzero
source residuals in notes/validation but initially lacked `publicWarning` text.
The reviewer requested visible warnings for 2025 employees **[+17, −5]**, 2025
trustees **[0, +1]**, 2026 employees **[−8, −9]** and 2026 trustees **[−1, −1]**
(remuneration, expenses, CAD). No individual amount should be balanced or changed,
and no unproved rounding explanation should be asserted.

**Resolved:** the author added all four `publicWarning` entries with the exact
signed residuals and an unconfirmed-cause qualification. The reviewer rebuilt
again into `/tmp/root-cross-school`; **all 66 files match the revised collection
byte for byte**, all 10,568 rows remain unchanged, and the five school regression
checks pass. The reproduction emitted nonfatal Poppler font/optional-content
diagnostics, completed successfully and retained the same row evidence. No
remaining blocking concern was found in this cross-review. The quoted review
scope and held OCR years remain unchanged.
