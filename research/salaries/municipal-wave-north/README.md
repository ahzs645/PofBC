# Northern municipal employee schedules

Reviewed October 31, 2026, America/Vancouver. This collection adds **373 employee observations and 28 separately scoped council observations**, across **five municipalities** that previously lacked accepted employee records.

| Municipality | Calendar year | Employees | Council | Employee pay residual | Employee expense residual |
| --- | --- | ---: | ---: | ---: | ---: |
| Dawson Creek | 2024 | 89 | 7 | $0 | $0 |
| Williams Lake | 2024 | 51 | — | $0 | +$1 |
| Williams Lake | 2025 | 61 | — | +$3 | $0 |
| Chetwynd | 2024 | 23 | 7 | $0 | $0 |
| Chetwynd | 2025 | 23 | — | $0 | $0 |
| Taylor | 2022 | 12 | — | +$1 | −$1 |
| Northern Rockies | 2024 | 55 | 7 | +$3 | +$1 |
| Northern Rockies | 2025 | 59 | 7 | −$1 | +$1 |

For Williams Lake, the expense column in the table above is a broader comparison rather than a named-only residual: printed expenses cover all employees, while the under-threshold expense cell is blank. Its named expense control is unavailable. Known named expenses and the printed all-employee control are retained without treating the blank as zero. The pay control is printed total employee remuneration minus the numeric below-threshold aggregate. Other listed residuals compare known named cells with the specified source controls. Northern Rockies' controls are the named employee subtotal, covering all four published employment groups. Every nonzero residual has a visible `publicWarning`; published individual values were not changed and the causes remain unresolved. Northern Rockies' 2025 council expense sum also exceeds its printed subtotal by $1 and has a separate warning. All other imported council controls match.

Every accepted name, title or department, remuneration amount, expense cell and page agrees between PyMuPDF positioned words and Poppler's independent bbox extraction. Source hashes, normalized-file hashes, internal December 31 reporting dates, named counts, reviewed layouts and exact controls are pinned. Rendered table edges and control pages were checked, including wrapped Chetwynd titles, Williams Lake's aggregate boundary, and Northern Rockies' mixed-font `ESTATE OF RYAN KERR` label. Regression guards protect those cases. This is native-text verification, not an OCR acceptance claim.

Definitions matter. Williams Lake includes salary, wages, overtime, vacation payouts, taxable benefits and incremental Emergency Operations Center pay. Taylor explicitly publishes remuneration **and benefits**. Northern Rockies describes retroactive pay, unused-vacation payouts, emergency operations payments and taxable benefits; its second column is **Department**, so normalized position remains missing and departments remain in evidence. Its estate-pay label is preserved as published. Expenses stay separate throughout. Dawson Creek's printed threshold wording includes remuneration and expenses; each of the accepted 2024 named employees also has remuneration above $75,000.

Expense dashes remain missing. Explicit printed zero stays zero, including Chetwynd 2025 and Northern Rockies 2024. Supporting evidence retains the source's department/title values and integer-cent monetary cells. No names, titles or payment periods were inferred, no police or regional-district records were added, and no compiled records were relabeled or deleted.

The Chetwynd 2025 council subsection is held separately: three remuneration values print `15.344`, while other councillors print `15,344`. Its employee subsection is independently verified and unaffected. Dawson Creek 2025 has noisy OCR text and remains in the processing queue. The 100 Mile House 2023 and Fraser Lake 2023 originals are image-only and also remain unimported.

Reproduce using:

```sh
python3 scripts/parse_wave_north.py --cache /tmp/pofbc-wave-north --fetch
python3 scripts/parse_wave_north.py --check-data
python3 -m unittest scripts/test_wave_north.py
```

The first command verifies pinned originals and repeats both complete text-reader extractions. The second verifies retained evidence and normalized data offline. The parser needs PyMuPDF and Poppler. Original binaries remain in the temporary cache and can be fetched from manifest URLs. Central build registration and generated app files are left to the integrating agent.

An explicit metadata amendment corrects Williams Lake 2024/2025 expense-control scope. The original PR27 sources/config/parser/guide are archived under `../municipal-history-pass/corrections/north-expense-scope/pr27-original/`; the amendment ledger retains old/new warnings, hashes and source-page proof. All 401 normalized observations, source amounts and retained binary evidence are unchanged.
