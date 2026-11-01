# Postsecondary continuation: original-backed employee schedules

The first frozen batch contains **36 verified cohorts / 19,137 employee observations** from six existing public institutions. It adds Camosun2015/16–2025/26 except held2023/24 (10 cohorts), Capilano2018/19–2024/25 (7), Douglas2021/22–2025/26 (5), UFV2019/20–2025/26 (7), VIU2020/21,2021/22,2024/25 (3), and Okanagan2021/22–2024/25 (4). No accepted SFU,BCIT,UNBC or North Island source is duplicated. No new employer has normalized rows in this batch.

Each source pins the original PDF SHA-256, exact official URL, physical pages, original fiscal period, deterministic normalized gzip hash, row counts and source-specific printed controls/residuals. Originals are cached at each source's `cacheFile`; original discovery receipts live in `sector-search-2026-10-31/education/document-verification.json`. All normalized files are frozen for parent publication review; research, queue and review additions can continue independently.

Two independent PDF engines must agree on every imported name, remuneration, expense, physical page, order and repeated row. PyMuPDF assigns positioned numeric anchors to named baselines; Poppler independently parses physical-layout text lines. Position fields are absent/blank in these schedules and remain null. Monetary blank/dash cells remain null, literal numeric zeroes and all ten negative expenses are preserved. Douglas and older VIU expense-inclusive total columns are excluded from remuneration. Okanagan's remuneration definition includes taxable benefits/deferred income and has severance exclusions described in the original note; audited salary-and-benefit aggregates are not imported as individual pay.

Camosun's employee table expressly excludes employees who are board members and severance. Both `completeEmployeeSchedule` flags are false. Same-label compiled Camosun2017/18 and2020/21 partitions are explicitly retained under the parent-reviewed opt-in guard, with visible overlap/unverified-period warnings. The mixed board table remains a separate processing task: employee-duty pay, student Student Society work and retainers must not be combined or reattributed. UFV's final employee pages sometimes also contain board-only expenses; all named employee rows above that boundary are retained.

Small printed-control residuals remain visible, source-specific warnings. Their cause is not established. Three additional fully extracted cohorts /1,905 rows are in `held/sources.json`, outside the accepted manifest: VIU2023/24 (667 rows; pay−140,098.75, expenses−6,464.53), VIU2022/23 (645; pay−128,314.42, expenses−5,684.75), and Camosun2023/24 (593; pay−4, expenses−506). Full original scope/control review is required before accepting these. Exact values are preserved without forced balancing.

Reproduce from cached originals, then replay without PDF/OCR/network access:

```sh
python scripts/continue_education.py --originals
python scripts/continue_education.py
python -m unittest discover -s scripts -p test_continue_education.py -v
```

The six regression tests cover combined employee/board pages, reversed money columns, expense-inclusive totals, negative and missing amounts, partial/retained-compiled scope guards, duplicate names and a literal source anomaly. `evidence/` retains the exact positioned-word and independent text evidence for every employee page; the review JSON files retain fiscal heading and printed-control receipts. `continuation-2026-11-01/education/visual-review.json` records the precise rendered-page coverage, including every negative-expense row and scanned approval pages. It does not claim all source pages were rendered. The collection contains no OCR-extracted employee rows.

For regenerating the review artifacts before a future freeze, run `--build` followed by `continue_education_review.py`; the latter separates material-control holds. Do not run those mutations during parent publication checks. Current roster, acquisition tasks, replacement review and frozen hash ledger are in `continuation-2026-11-01/education/`.
