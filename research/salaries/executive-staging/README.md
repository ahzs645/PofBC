# Executive components kept separate from employee remuneration

This directory contains **17 reviewed executive rows**, separate from the
accepted employee build:

| Source | Current-period rows | What is disclosed |
|---|---:|---|
| BCI 2017/18, physical page 46 | 5 | Base pay, annual/long-term incentives, pension, benefits, published total |
| BCI 2025/26, physical page 53 | 5 | The same components; four CAD rows and one USD row |
| BC Pension 2025/26, physical page 56 | 7 | Base salary and employer pension contributions, without a complete remuneration total |

Exact source URLs, hashes and page references are retained in each JSON and in
`staging-manifest.json`. The original PDFs accompany the source archive. All
three tables were visually inspected, and every transcribed numeric value is
checked against text extracted from the pinned page by
`scripts/stage-executive-salaries.py`.

These are structured research records, **not accepted employee-schedule rows**.
They cannot replace full employee data. No CAD/USD aggregation or exchange-rate
conversion is performed. The BCI incentive notes attribute payments to performance
years even where disbursement falls in a later fiscal year. Printed component
sums can differ from the published total by a dollar; those differences remain
visible in `componentSumMinusPublishedTotal`.

BC Pension's table identifies additional benefit/allowance/leave components in
its footnote without giving a complete amount per person. `totalRemuneration`
therefore remains `null`. The listed base salary is not relabelled as full pay.
For Renee Bilodeau the published prorating note is retained.

Historical comparative rows displayed beside BCI's current executives are not
treated as a complete executive roster for those earlier years. The separate
2017/18 report supplies its own five current-period rows. Neither report supplies
an all-employee roster comparable to the retained 363-row 2017/18 compiler slice.

Reproduce with the three original files named as below:

```bash
python3 scripts/stage-executive-salaries.py --source-dir /path/to/originals
# bci-2017-18.pdf, bci-2025-26.pdf, bcpc-2025-26.pdf
```
