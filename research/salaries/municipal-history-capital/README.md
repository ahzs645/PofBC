# Capital and Cowichan historical salary recovery

**797 official observations in 34 accepted cohorts across 18 report-years and six municipalities:** 670 employee and 127 elected-official observations. Oak Bay gains its first accepted official employee schedule. The collection authors no compiled replacements and changes neither the source registry nor public app files.

| Municipality | Accepted calendar years and categories | Employees | Elected officials |
|---|---|---:|---:|
| Colwood | 2012, 2016, 2018, 2021 employees/council; 2017 council only | 132 | 39 |
| Langford | 2010 and 2021 employees/council | 84 | 14 |
| North Saanich | 2020, 2021, 2023 employees/council | 85 | 22 |
| Ladysmith | 2021–2023 employees/council | 106 | 22 |
| Sidney | 2021–2024 employees/council | 165 | 30 |
| Oak Bay | 2024 employees only; council held | 98 | 0 |

[sources.json](sources.json) is the standard `{version,rowSchema,sources}` manifest, with original and data hashes, actual dates, physical PDF pages, exact controls, scope and public warnings. [reviewed-layouts.json](reviewed-layouts.json) pins source geometry, literal rendered first/last rows, complete scanned-source transcriptions and the narrow artifact exception described below. Evidence gzip files retain all published fields and source controls, including fields not used as remuneration.

Thirty-two accepted native cohorts use independent PyMuPDF and Poppler positioned-word readings, with every field compared and the original schedule pages reviewed. Actual salary pages determine modality: scanned financial statements elsewhere do not make a native appended salary schedule an OCR task. There are 42 reviewed page/cohort boundaries including the held Oak Bay council table and two scanned Langford cohorts. All 35 salary pages were rendered; 34 pages contain accepted observations and one contains held council observations.

Langford 2010 is **scanned**, and its two PDF text extractors are not described as independent OCR. All 31 rows were transcribed from enlarged rendered originals, checked field by field, and corroborated by new **Tesseract 5.5.0, PSM 6, 300 dpi PyMuPDF renders** and the city-provided searchable layer. Both raw text readings are retained under [evidence/ocr](evidence/ocr); each disagreement and its original-image adjudication is retained with the row. Examples include new OCR reading Mahovlich’s $104,148.46 as $404,148.46 and Palmer’s $1,399 expense as $4,399. Neither incorrect OCR value enters the data. **Barber, Jennfier** is the original printed spelling and is preserved. Fletcher, Lorne is resolved by independent enlarged-image glyph reviews; both retained machine readings say Lome, and neither is claimed to corroborate that manual correction. The schedule spelling Tement, Steve is retained with a public note that the same original’s approval page 3 prints Steve Ternent; no alias substitution is made. Published employee/council pay, expenses, supplementary totals and council budgets reconcile exactly. These fields are individual observations of payments, not annual salary rates or a complete employee roster.

Blank/dash cells remain `null`; printed numeric zero, negatives and cents retain their meaning. Numeric remuneration TOTAL columns in Colwood and Sidney are used directly, with gross/benefit components retained rather than reconstructed by treating missing benefits as zero. Colwood 2016 Carlsen has a blank benefit cell but an explicit numeric remuneration TOTAL. Expense-inclusive totals and council budgets are supporting evidence, never remuneration. Unprinted offices remain missing.

Colwood’s employee control explicitly says **$75,000 OR MORE** (`>=`). Langford 2021, Ladysmith, North Saanich and Oak Bay have explicit strict comparisons. Sidney and Langford 2010 retain `thresholdComparison: null`: their separate other-employee labels do not supply a printed comparison in the named heading. Oak Bay explicitly excludes its police department. It publishes both departments and positions; neither is substituted for the other. Its surname and given-name fields are retained separately in evidence and joined with one space for the app, without adding a surname comma or changing identity.

The exact nonzero residuals below are accepted row sums minus printed named controls. Original cells remain unchanged, the cause remains unresolved, and each accepted source carries a public warning.

| Source | Cohort | Pay difference | Expense difference |
|---|---|---:|---:|
| Colwood 2012 | Employees | −$47.55 | No printed control |
| Colwood 2016 | Council | $0 | −$0.02 |
| Colwood 2016 | Employees | $0 | +$0.01 |
| Colwood 2018 | Employees | $0 | +$0.01 |
| Colwood 2021 | Council | +$2 | +$1 |
| Colwood 2021 | Employees | +$1 | +$5 |
| Ladysmith 2021 | Council | $0 | −$1 |
| Ladysmith 2021 | Employees | $0 | +$1 |
| Ladysmith 2022 | Council | $0 | +$1 |
| Ladysmith 2022 | Employees | $0 | +$5 |
| Sidney 2021 | Council | $0 | +$1 |
| Sidney 2021 | Employees | −$1 | $0 |
| Sidney 2022 | Council | $0 | −$3 |
| Sidney 2022 | Employees | +$1 | $0 |
| Sidney 2023 | Council | $0 | +$1 |
| Sidney 2023 | Employees | +$2 | −$1 |
| Oak Bay 2024 | Employees | +$5 | −$4 |

Other source limitations remain explicit. Colwood 2012 council publishes no subtotal and no individual offices; its complete seven-row rendered transcription is pinned. Langford 2021 council expense cells and the printed expense subtotal are dashes, so no numeric expense control or nil expense claim is created. Sidney 2021 and 2022 all-employee remuneration controls are $1 below their printed named-plus-other components; Sidney 2022 council TOTAL is $1 above gross plus benefits. Oak Bay’s all-employee control is $1 below named plus other employees. Colwood 2021 has 13 individual published remuneration TOTAL/component differences of ±$1, each named and quantified in evidence. No cause is assigned and no field is balanced to an aggregate.

**Oak Bay 2024 council is held in full:** seven candidate rows, zero accepted. Listed expenses sum $25,202 against printed $25,472 (−$270); pay sums $222,362 against $222,360 (+$2). Watson, Lesley’s pay $26,689 plus expenses $3,256 conflicts with printed expense-inclusive Total $26,689 (−$3,256), and Murdoch’s Total differs from its component sum by −$1. [Held evidence](evidence/district-of-oak-bay-2024-elected-officials-held.json.gzip) retains every original field. An amended report or source clarification is needed; the independently verified employee cohort is accepted separately.

A regression also caught a **hidden underlying `3.5` token** in Oak Bay’s physical page 52 text layer that both PDF readers had attached to Laktin Marilyn’s title. The rendered title is “Manager Financial Operations”. The parser excludes only that exact token at its reviewed source coordinates, with an expected-count guard and original hash pin; legitimate letters and numerical text elsewhere are retained. The final parsed 98-row employee table was rechecked against all three rendered originals after this correction. Literal row boundaries and wrapped department/title regressions guard the final result.

Reproduce from the repository root:

```sh
python scripts/parse_history_capital.py --verify
python -m unittest discover -s scripts -p test_history_capital.py
```

**21 regression tests pass**, and a fresh full `--verify` reproduces every generated output byte. An [independent complete image review of Langford 2010](../municipal-history-pass/reviews/langford-2010-ocr.md) checked all 31 manual rows and supplementary totals; its two requested name/evidence notes are incorporated without monetary changes. Missing originals download to `/tmp/history-capital`; `--cache-dir` and `--output-dir` support isolated reproduction. PyMuPDF and Poppler are required. The scanned cohorts reproduce from their hash-pinned originals, reviewed literal transcriptions and retained raw OCR readings; regenerated OCR from another version must receive a fresh disagreement review. No OCR correction is inferred from financial totals alone.

The [archive inventory and remaining work](../municipal-history-pass/capital/README.md) distinguish public documents awaiting processing from archive searches and clarification requests. No external messages, ordinary records requests or FOI submissions were sent.
