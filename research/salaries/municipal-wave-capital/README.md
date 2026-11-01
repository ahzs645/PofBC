# Capital and Cowichan salary recovery

**547 verified official observations, 20 separate cohorts, nine newly covered municipalities.** The collection contains **483 employee** and **64 elected-official** observations. Employee and council disclosures remain separate. No compiled records are removed.

| Municipality | Calendar years | Employees | Elected officials |
|---|---|---:|---:|
| Colwood | 2025 | 74 | Council image table pending |
| Esquimalt | 2025 | 86 | 7 |
| Highlands | 2024 | 4 | 7 |
| Ladysmith | 2025 | 39 | 7 |
| Lake Cowichan | 2023, 2024, 2025 | 8 in 2023; 11 in 2025 | 5 each year |
| Langford | 2025 | 130 | 7 |
| North Saanich | 2025 | 44 | 7 |
| Sidney | 2025 | 53 | 7 |
| View Royal | 2025 | 34 | 7 |

[sources.json](sources.json) pins original and normalized-data hashes, calendar dates, scope, physical PDF pages, source definitions, exact monetary controls and public warnings. [reviewed-layouts.json](reviewed-layouts.json) records the reviewed geometry and **29 literal first/last name-and-title checks transcribed from rendered originals**. PyMuPDF and Poppler independently read every accepted field. All schedule pages and controls were rendered and reviewed. Evidence retains both positioned readings, original controls and supporting source columns.

Blank/dash expenses remain `null`; only a printed numeric zero becomes zero. Expense-inclusive total columns are retained as supporting evidence and never substituted for remuneration. Colwood and Sidney publish a numeric remuneration TOTAL; that amount is used directly, without reconstructing missing benefit components as zero. Esquimalt publishes departments rather than employee job titles; departments remain supporting evidence and employee positions are `null`.

The printed threshold wording does not establish a precise comparison for Highlands 2024 employees or Lake Cowichan 2023 staff. Those sources retain `thresholdComparison: null`, with their exact wording/reporting context explained; all accepted named amounts exceed $75,000. Highlands’ below-threshold expense aggregate is also a dash. No named expense control is derived by treating it as zero: known named numeric expenses sum $10,391, while the separately printed all-employee expense total is $10,391.

The following small source residuals remain unchanged and carry public warnings. Differences are accepted row sums minus printed named-cohort controls; no cause is inferred.

| Source/cohort | Remuneration difference | Expense difference |
|---|---:|---:|
| View Royal 2025 council | −$3 | $0 |
| View Royal 2025 employees | +$2 | −$2 |
| Langford 2025 council | +$1 | $0 |
| Langford 2025 employees | +$2 | −$1 |
| Sidney 2025 employees | $0 | −$1 |
| Colwood 2025 employees | $0 | +$1 |

Independent review also checked the supporting row equations. View Royal employee Hynes, Bryan has a printed expense-inclusive total of $102,169 versus remuneration $99,907 plus expenses $2,263 ($102,170), a −$1 source difference. The published remuneration and expenses are preserved; the unused total remains in evidence.

Colwood’s employee pages retain **DRAFT watermarks**. The same original’s physical page 4 explicitly records Council approval of **all statements and schedules** at the June 29, 2026 special meeting, with the Finance Director’s and Mayor’s signatures. The management report on page 5 is signed too. That approval evidence is preserved and checked by the parser; the public warning explains the remaining watermark. Finality is supported by the approval evidence, rather than the filename.

**Lake Cowichan 2024 employees are held despite exact aggregate reconciliation.** Jessica May’s remuneration $92,354.93 plus expenses $5,429.75 equals $97,784.68, but the printed expense-inclusive total is $92,784.68: a $5,000 conflict. The below-threshold total also differs from its component sum by $0.09. Both readers agree on the original cells. [The held evidence](evidence/town-of-lake-cowichan-2024-employee-remuneration-held.json.gzip) preserves all eight candidate rows, with zero accepted employee observations. The independent council cohort is accepted. An explanation or amended source is needed; no amount is adjusted to force agreement.

Reproduce with PyMuPDF and Poppler installed:

```sh
python scripts/parse_wave_capital.py --verify
python -m unittest discover -s scripts -p test_wave_capital.py
```

The parser downloads missing hash-pinned originals to `/tmp/wave-capital`; `--cache-dir` and `--output-dir` support isolated reproduction. Thirteen regression tests cover cent/negative/missing amounts, original fingerprints, independent fields, text/monetary boundaries, rendered row edges, departments, explicit remuneration totals, unknown controls, visible residuals, Colwood approval and the material held conflict. The command changes neither the collection registry nor public app outputs.

The broader twelve-municipality search and remaining tasks are documented in [the pass inventory](../municipal-next-pass/capital/README.md). No records requests, FOI submissions or external messages were sent.
