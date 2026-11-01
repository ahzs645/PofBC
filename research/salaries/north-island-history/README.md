# North Island College official salary history

Reviewed **31 October 2026, America/Vancouver**. This collection fills five official-source coverage gaps using North Island College's original Statements of Financial Information (SOFI), independently of SunshineLists. It adds **808 verified employee observations**. The complete FY2023/24 employee schedule replaces **181 compiled observations** under the existing build rules, so the dataset grows by **627 observations**.

| Fiscal period | Named employees | Displayed remuneration | Displayed expenses | Difference from printed named subtotals (pay / expenses) | Physical employee pages |
|---|---:|---:|---:|---:|---|
| 2018/19 | 133 | $12,415,381 | $578,000 | -$10 / +$5 | 7-11 |
| 2021/22 | 138 | $13,907,610 | $154,386 | $0 / $0 | 7-11 |
| 2022/23 | 156 | $16,201,622 | $567,333 | $0 / $0 | 7-11 |
| 2023/24 | 181 | $20,146,497 | $760,596 | $0 / $0 | 8-13 |
| 2024/25 | 200 | $22,139,569 | $923,737 | $0 / $0 | 6-11 |

These are annual remuneration observations above $75,000, not base salaries, unique people or a census of all employees. The source's separate board payments, suppliers, below-threshold aggregates and overall totals are excluded from the individual employee data. An expense dash stays missing (`null`); it is not replaced with a numeric zero. Job titles are retained for the first four cohorts. FY2024/25 does not publish employee titles, so those fields remain missing.

## Official sources

All five originals are linked from the [college's institutional reporting page](https://www.nic.bc.ca/about/leadership-and-governance/institutional-reporting.html). Each fiscal period is verified from the employee schedule itself, with signed source approvals separately rendered and reviewed. All retrieved bytes match fingerprints already recorded during the earlier postsecondary source discovery pass.

| Original SOFI | SHA-256 | Signed approval date / physical page |
|---|---|---|
| [2018/19](https://www.nic.bc.ca/_resources/pdf/statement-of-financial-information-2018-19.pdf) | `8042d90554896de2c310d93bde9f4247757f092213b6038398e1a365257711b0` | 2019-09-27 / 2 |
| [2021/22](https://www.nic.bc.ca/_resources/pdf/statement-of-financial-information-2021-22.pdf) | `90fedb56a99c010064a67db18370578ecd6e33326bac04998b2d5458a3740afd` | 2022-10-06 / 3 |
| [2022/23](https://www.nic.bc.ca/_resources/pdf/statement-of-financial-information-2022-23.pdf) | `08b65aa51ae42b99125ffcbd5d59d27331ab775d989795051032197ea12bbcff` | 2023-09-28 / 3 |
| [2023/24](https://www.nic.bc.ca/_resources/pdf/statement-of-financial-information-2023-24.pdf) | `598caa417c3963e40a48af17d05ab860c02ae75cc901727ad092fa5ca98e762a` | 2024-10-03 / 3 |
| [2024/25](https://www.nic.bc.ca/_resources/pdf/statement-of-financial-information-2024-25.pdf) | `13ba3ce3742b8487ffedb14a945f340eaf09f27d9f94bbe084d9162546445b8e` | 2025-10-02 / 3 |

## Validation and source disagreements

The importer checks every name, published title, remuneration amount, expense cell and physical page using two independent PDF engines: Poppler layout extraction and PyMuPDF positioned words. It also independently checks the printed named subtotals, exact employee-section page counts, every page's row count, fiscal headings, source fingerprints and board/named/below-threshold reconciliation to the printed grand totals. Unexpected rows, missing columns, changed fingerprints or changed controls fail before normalized outputs are written.

Rendered source pages were reviewed for signed approval, first and final employee sections and printed controls. The name/title columns touch for `Paquet-Combe, Marie-France` in FY2021/22, FY2022/23 and FY2023/24. Those three exact boundaries were inspected at higher resolution. The parser restores only the field boundary; no name letters, title letters or monetary values change. Both complete extractions agree on the underlying printed text.

For **FY2018/19**, the rendered final employee page prints **$12,415,391 remuneration and $577,995 expenses**. Every displayed employee cell agrees between the two readers, and those cells sum to **$12,415,381 and $578,000**. The source discrepancy is **-$10 and +$5**. Its cause is unconfirmed. The accepted data reproduces the displayed values and carries a `publicWarning`; no balancing adjustment is made. The other four cohorts reconcile exactly to both named controls.

[sources.json](sources.json) contains all source and normalized-data hashes, actual reporting dates, validation details, excluded controls, missing-cell counts and source warnings. The compressed normalized cohorts are deterministic (`gzip` mtime zero).

## FY2023/24 compiled replacement

The official schedule has the same **181** observations and exactly the same pay/expense multiset as the retained compilation labelled FY2023/24. Normalizing only name punctuation and letter case gives **179 exact name/pay/expense matches**. Two compiled rows have job-title text in the name field:

| Compiled name / title | Official name / title | Original physical page |
|---|---|---:|
| Lawrence, Jeffrey Instructor / Humanities | Lawrence, Jeffrey / Instructor, Humanities | 11 |
| Lowey Mackenzie, Kerri Inst / Human Services | Lowey Mackenzie, Kerri / Inst, Human Services | 11 |

The full original employee scope and fiscal dates justify replacing the complete same-period compiled cohort. Payment-only equality is not used to infer personal identity. [compiled-period-comparison.json](compiled-period-comparison.json) retains the baseline hash, matched counts and every candidate with equal payment values. Compiled zero expenses and source dashes are treated as equivalent only for this overlap check; imported original dashes remain `null`.

## Reproduce and test

Requirements for source re-extraction: Python 3, Poppler `pdftotext`, and PyMuPDF (`fitz`). No PDF or network dependency is added to the normal JavaScript salary build.

```sh
python scripts/import-north-island-history.py --verified-on 2026-10-31
python scripts/import-north-island-history.py --offline --verify --verified-on 2026-10-31
python -m unittest discover -s scripts -p test_north_island_history.py
```

The default cache directory is `/tmp/pofbc-nic-history`; each original is named `nic-YYYY-YY.pdf`. Use `--cache-dir` to select another directory. `--offline` never downloads, and `--verify` compares all reproduced data and manifests with the committed outputs without writing. A changed original requires renewed review; the program does not update accepted fingerprints automatically.

After registering this collection in `research/salaries/collections.json`, run `npm run build:salaries` and `npm run check:salaries` to reconcile all published exports. This importer does not change the collection registry, compiled baseline or published app files itself.

## Remaining college history

FY2020/21 is already accepted in the separate [North Island collection](../north-island/); this pass does not duplicate it. The index currently points both its FY2019/20 and FY2020/21 labels at [the same scanned original](https://www.nic.bc.ca/_resources/pdf/statement-of-financial-information-2019-20.pdf). That nine-page document's rendered cover explicitly states **year ended March 31, 2020**, confirming FY2019/20 despite the duplicate FY2020/21 link label. Its SHA-256 is `43fd43a1d642fd6ad49efa92b8428d8663a4a410eec74d2d615b30fecb7e661d`, matching the earlier discovery receipt.

The manifest retains this genuine FY2019/20 document in `unparsedSources` with status `requires-ocr`, the exact shared index target, both observed link labels and the cover-period evidence. It contributes **zero imported observations**. Complete OCR, employee-section period/scope review, row verification and printed-control reconciliation remain necessary. Cover review alone cannot establish those checks. The genuine FY2020/21 file was recovered separately in the earlier correction. FY2017/18 remains compiled-only, and this collection does not establish complete earlier history or a new FY2025/26 employee schedule.
