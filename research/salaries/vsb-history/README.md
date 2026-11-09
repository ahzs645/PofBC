# VSB (School District No. 39, Vancouver) SOFI employee schedules, 2017/18–2023/24

Official Statement of Financial Information (SOFI) schedules of remuneration and expenses for named employees paid over $75,000. All PDFs come from the VSB financial information index, https://www.vsb.bc.ca/financial-information, and were downloaded on 2026-11-09. Each accepted source replaces the compiled third-party partition for `vancouver-school-district` in the same year. `retainCompiledPartition` is not set.

Employer slug: `vancouver-school-district`. Fiscal years run from July 1 to June 30. Threshold: remuneration `>` $75,000. Elected officials, the under-threshold line and CPP/EI are not imported.

## Method

- **Engine A:** poppler `pdftotext -layout -fixed 2` (version 24.02.0). The text is split into cells using character-grid column positions, which are worked out separately for each page.
- **Engine B:** `pdfplumber` 0.11.10. Cells are split using word and character x-geometry, with column starts worked out separately for each page.
- **Comparison:** the two engines were compared row by row on page, surname, given names, position, remuneration and expense literal.
- **Reconciliation:** named rows were reconciled to the printed control line, "Total ... exceeding $75,000". The residual bound is 0.5 × rows. No value was adjusted.
- **Names:** names are `Surname, Given` exactly as printed. Asterisk markers for travel on international student recruitment are kept as printed.
- **Expenses:** an expense printed as "-" is stored as null.
- **Tools:** the scripts are in `tools/` (`extract.py`, `compare.py`, `build.py`). They were run from a scratch directory, so their paths are absolute.

## Years

| Year | Status | PDF SHA-256 | Pages | Rows | Remuneration | Expenses | Printed control | Residual |
|---|---|---|---|---|---|---|---|---|
| 2017/18 | accepted | 389da14245de322fab5ff482357d4b906a97ed0aabbfbe0f9199192307718db8 | 7–41 | 2,301 | 203,714,938.43 | 364,150.92 | 203,714,938.43 / 364,150.92 | 0.00 / 0.00 |
| 2018/19 | held-for-review | 51d011ee324c12f27c2d67e8a94b7183a145df6b414843b6e66a3a6a42eb0b59 | 54–91 | – | – | – | – | – |
| 2019/20 | accepted | 3644db61aff3d0964883d9b1974d4799c0d28562f3ed44c062ddd786f7275dd1 | 55–103 | 2,534 | 235,816,019 | 562,361 | 235,816,019 / 562,361 | 0 / 0 |
| 2020/21 | held-for-review | 3ffdd428bace127f7e9d6b9fd6d45caabb615eade37baed69a237858b28ce47e | 54–99 | – | – | – | – | – |
| 2021/22 | held-for-review | 15797f73407622a8a97f786d4cc3a720e1932d544462e37aef5456a6acd626c6 | 55–105 | – | – | – | – | – |
| 2022/23 | accepted | e4b6ee05cbce8c2238f1e54ffb594e8a66208d7e9beda465917db0a14ac66f34 | 57–109 | 2,869 | 283,483,461 | 933,849 | 283,483,416 / 933,842 | +45 / +7 (bound 1,434.5) |
| 2023/24 | accepted | 7125cea36b6eca79cfe5ac54e1d0b0c9c1d6f56eec451c7f7c7ca3628c277470 | 55–105 | 3,187 | 329,468,990 | 1,044,624 | 329,468,990 / 1,044,624 | 0 / 0 |

### Source URLs

- 2017/18: https://media.vsb.bc.ca/media/Default/medialib/2017-2018-statement-of-financial-information.f3b9a327108.pdf
- 2018/19: https://media.vsb.bc.ca/media/Default/medialib/2018-2019-statement-of-financial-information.b5249027109.pdf
- 2019/20: https://media.vsb.bc.ca/media/Default/medialib/2019-2020-statement-of-financial-information.5f153127110.pdf
- 2020/21: https://media.vsb.bc.ca/media/Default/medialib/2020-2021-statement-of-financial-information.0b3b2c27111.pdf
- 2021/22: https://media.vsb.bc.ca/media/Default/medialib/2021-2022-statement-of-financial-information.7d0e5060749.pdf
- 2022/23: https://media.vsb.bc.ca/media/Default/medialib/2022-2023-statement-of-financial-information.69747169697.pdf
- 2023/24: https://media.vsb.bc.ca/media/Default/medialib/2023-2024-statement-of-financial-information.784fac77630.pdf

## Notes per year

### 2017/18

- Native text, with amounts printed in cents.
- The two engines agree on every row.
- The rows reconcile exactly.
- The printed "Total ... (including Elected Officials)", 407,636,602.61, equals the named subtotal plus the under-threshold line only; elected officials are not included in it. This is recorded as printed.

### 2019/20

- Native text. The printed control is an unlabelled subtotal line.
- Cross-check: 235,816,019 + 197,171,526 + 265,864 (elected officials) = 433,253,409, which matches the printed total.
- In 6 rows the surname runs into the given-name cell without a space, for example `Nishi-BeckinghamTeresa`. One of these is a visibly truncated surname, "Mesropian De Gon".
  - pdfplumber splits these rows at the printed column x-position.
  - The pdftotext grid splits them with a recorded rule: either at a single lower-to-upper case change, or by taking the last token.
  - Both engines give identical results. The rules used are listed in `validation.pdftotextBoundaryRules`.

### 2022/23

- Native text. The two engines agree on every row.
- The named rows exceed the printed control by $45 in remuneration and $7 in expenses. This is within the bound. The cause is not established.
- The printed summary lines cross-foot to the printed total, except that the printed expense total is $1 over.

### 2023/24

- Native text. The rows reconcile exactly.
- There is one disagreement about where a cell boundary falls, on physical page 89, `Orr`.
  - The pdftotext grid cannot separate "Kim Margaret Ramona" from "Teacher Secondary".
  - Poppler `-bbox` word geometry was used as a third reader. It confirms the pdfplumber split: "Teacher" starts at x = 219.72, the start of the position column.
  - The characters and amounts are identical in all readers. The adjudication is recorded in `validation.cellBoundaryAdjudications`.

### 2018/19, 2020/21 and 2021/22 (held)

- The schedule pages are scanned images, from a Canon iR-ADV scanner, with an invisible OCR text layer.
- The OCR layer contains errors, for example `90,t82`, `I 8,53 I`, `94,51t`, `529,98t` and `t04`.
- Both engines read the same OCR layer, so they are not independent and they cannot meet the bar for native text.
- These sources need an image-based transcription with an independent review.

## Integration notes

- Root `research/salaries/collections.json` lists the collections explicitly. `vsb-history` must be added to it before the build will read this manifest.
- Data hashes are `sha256` of the gzip bytes. The files are written with gzip `mtime=0`.
