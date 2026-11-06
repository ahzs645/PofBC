# Provincial elected compensation recovery

Offline reproduction: `python scripts/import-provincial-elected.py`.
Tests: `python -m unittest discover -s tests -p 'test_provincial_elected.py'`.

The manifest imports 2,428 observations from 39 official CSVs: 1,796 member-year records and 632 executive-salary records. Original CSV bytes and catalogue API metadata are preserved in `originals/`. Source hashes, normalized hashes, fiscal scope, counts, and numeric sums are pinned in the manifest and `controls.json`. Controls are regression checks, not independently published totals. Where a published total exists (FYE2021 members), compensation and both expense columns reconcile independently.

MLA role allowances are combined only under the exact published member name in the same source and period. Per-line amounts, negative corrections, constituency labels and source CSV record numbers remain in each audit. FYE2023 places allowance descriptions in the name column: these explicitly labelled continuation rows belong to the preceding named member. No fuzzy identity joins are used. No cross-source or cross-year names are merged. Hon., initials, capitalization and source spelling remain unchanged.

`legislative-assembly-members` covers member compensation and role allowances. `provincial-cabinet` covers the separate executive salary component. They are complementary disclosures, not two estimates of a person's total compensation. Annual rates, full-year service and combined total compensation are not inferred. The two employers must remain distinct from provincial administration and Legislative Assembly staff.

Capital city living allowances and travel are expenses, not salary. Missing values and #N/A remain null. Rows with no numeric salary remain in audits but are excluded from remuneration exports. Negative corrections are retained. FYE2021 contains a published total followed by stray unlabelled spreadsheet cells; these are preserved in the audit and never treated as people. FYE2023 minister salaries repeat FYE2022 values even though the heading and expenses differ; the source is retained with an explicit warning, not repaired speculatively.

The member dataset supplies FYE2007 and FYE2009–2026; FYE2008 is missing. Minister sources cover FYE2007–2026. Catalogue fiscal-year labels are used when a CSV omits its heading. Every source retains its resource URL.
