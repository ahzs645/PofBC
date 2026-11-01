# Health disclosure continuation inputs

Seventeen original-backed **board remuneration** cohorts provide **190 observations** across Northern Health, Interior Health, PHSA and BCCSS. No employee schedule is reimported and no compiled partition is replaced. The eight-employer search inventory and remaining acquisition tasks are in [the research dossier](../continuation-2026-11-01/health/README.md).

| Employer | New board periods | Accepted observations | Scope qualifications |
|---|---|---:|---|
| Northern Health | FY2020/21–2025/26 | 61 | All named board rows. The FY2021/22 Nyce expense is explicitly −309. FY2024/25 and FY2025/26 have published whole-dollar control differences. |
| Interior Health | FY2018/19–2025/26 | 79 | Two source rows with only blank/dash remuneration are held: Halpenny in FY2023/24 and Roundsville in FY2022/23. These two cohorts have `completeBoardSchedule:false`. |
| PHSA | FY2024/25–2025/26 | 27 | Three unknown-pay appointee rows held in FY2024/25 and Tiffany Ma held in FY2025/26. Published expense reimbursements include source-defined travel fees; these are not reassigned to pay. |
| BCCSS | FY2017/18 | 23 | All named source rows, including 15 explicit zero payments. The source excludes out-of-pocket reimbursements; every expense field is null, and the expense comparator is marked unavailable. Travel per diem fees form part of the source's remuneration definition. |

`source-specs.json` locks original SHA-256 values and cache paths, reviewed table rectangles, source row counts, monetary columns, source controls and one guarded glyph correction. `sources.json` is the standard collection manifest. Each deterministic normalized gzip uses the six-column row schema in that manifest. The original bytes are in `/tmp/continuation-health/`; originals are not embedded in the repository.

All **196 named source rows**, including the six held rows, agree across independently implemented PyMuPDF and Poppler positioned-word extraction. All 17 complete one-page schedules were rendered and every named row, header, monetary column and printed control was visually reviewed. Northern Health's six cohorts also received independent complete visual review by the municipal continuation worker; see `../continuation-2026-11-01/reviews/health-northern-boards.*`.

The single native glyph disagreement is Interior FY2021/22 Rounsville's position: PyMuPDF returns `CommiƩee` and Poppler returns `Commi ee`. The rendered original says `Committee`. The correction accepts only the two exact complete original cells and retains both unmodified reader word streams.

Pay uses the separately printed remuneration subtotal when present; otherwise it sums published remuneration components. It never uses an expense-inclusive total as remuneration. Monetary blanks/dashes remain unknown. All-unknown remuneration rows are retained in validation evidence and held from normalized payments. Source footer totals and arithmetic differences are preserved, with exact row and grand residuals and source-specific public warnings. No cause is inferred for those differences.

Interior FY2024/25 and FY2025/26 explicitly use cash-based retainers/expenses but meeting fees based on meetings attended, including payments made the following month. Their manifest notes preserve that mixed timing basis. Sources do not assert adoption, finalization or audit status beyond the original headings.

Reproduce from cached, fingerprint-locked originals:

```sh
python scripts/continue_health.py --originals --check
```

Replay offline without network, PDF libraries or OCR engines:

```sh
python scripts/continue_health.py --check
python scripts/test_continue_health.py
```

All six regression tests and original/offline replay pass. Evidence gzip files retain both independent positioned-word readers and the original fingerprint; the manifest retains evidence hashes. Normalized payloads and source decisions are frozen for parent publication checks.
