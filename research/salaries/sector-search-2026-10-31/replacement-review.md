# Reviewed fiscal replacements and employer identity

This pass adds original employee disclosures for actual fiscal periods. A complete official fiscal schedule replaces the corresponding unverified compiled partition in the existing salary build. This is an authority and scope decision, not a claim that every compiled cell matches or that every compiler edition label has been proved across all employers. Cross-calendar municipal corrections continue to require their separate hash-pinned complete-match evidence.

## School District No. 42

The district's [official description](https://www.sd42.ca/our-district/) and [financial archive](https://www.sd42.ca/financial-information/) identify School District No. 42 (Maple Ridge–Pitt Meadows). Original report covers and named schedules use that identity. The compiler's Maple Ridge/Pitt Meadows School Board and Ridge-Meadows school district entries refer to this district; the row comparison and shared fiscal disclosures corroborate the identity. The `ridge-meadows-school-district` route now resolves to `maple-ridge-pitt-meadows-school-district`; historical compiler names remain in employer metadata.

The retained deployed baseline contains 635 records labelled 2017/18 (629 employees and six trustees), 755 employee records labelled 2020/21, and 1,030 employee records labelled 2023/24. All **2,420** compiled observations in these partitions are replaced with the original employee **and trustee** schedules. This preserves elected trustee scope, restores the missing employee in 2020/21, and uses source amounts with their cents, negative expenses and missing cells. In particular, a negative $252.96 expense in 2023/24 was positive $253 in the compilation. Compiler surname encoding and enrichments are not copied into the original records.

See [full overlap evidence](schools/sd42-compiled-overlap.json), [original fingerprints and cohort controls](../sector-schools/reviewed-inputs.json), and [independent cross-review](municipal/cross-review-schools.md). Trustees use a distinct `school-trustees` disclosure category in the app.

## Simon Fraser University

The [official annual-report archive](https://www.sfu.ca/finance/publications/annual-reports.html) supplies complete named employee schedules. Accepted FY2017/18 and FY2020/21 schedules replace those two compiled partitions. The existing FY2023/24 compiled data remains because its recovered original has a material unresolved subtotal discrepancy and is held from import.

The FY2017/18 compiler has 1,617 rows, the same count as the original, but includes full-name/title enrichments absent from the original and three conflicting Schmidt names. The public source warning identifies those conflicts; displayed records use the original names. FY2020/21 has 2,072 compiled rows versus 1,980 official employee rows, including 91 exact extra copies and other compiler differences. The official source includes three final employee rows absent from the compiler. Neither reviewed compiled partition contains a separate board-remuneration cohort; below-threshold board schedules remain outside this employee replacement.

See [education review](education/README.md) and its detailed overlap evidence. Original report and immutable compiler snapshot hashes remain available for reproduction. A complete official source superseding incorrect compiled values does not establish a person's expanded identity beyond the source's disclosure.

## Retained overlaps and holds

InBC has a separate proved period correction: all nine compiled observations labelled 2023/24 exactly match the original 2022/23 employee schedule in name, position, remuneration and expenses, with multiplicity. They match none of the fifteen original 2023/24 observations. The [replacement rule](../sector-crowns/sources.json) pins both the accepted source data hash and the exact selected compiled-row hash. This corrects their reporting period without treating the nine rows as additional unique observations.

Pitt Meadows' partial compiled overlaps are retained: a missing initial letter and an omitted official employee prevent a complete match. Metro Vancouver's unverified compiled editions and board observations are retained; nine original employee rows with missing benefits/other remain held, and partial cohorts cannot establish replacement equivalence. Material SFU control discrepancies, the BC Assessment 15-month transition period, incomplete OCR, executive-only disclosures and aggregate-only figures do not become ordinary complete annual employee salary cohorts.
