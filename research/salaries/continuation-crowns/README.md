# Crown salary source continuation

**44 original-backed cohorts; 39,063 observations: 39,041 employees and 22 board members.** This new collection is ready for parent review/integration. It does not edit the shared collection registry, aliases, compiled baseline, app or public outputs.

| Employer | Scope | Cohorts | Rows | Actual periods |
|---|---|---:|---:|---|
| ICBC | Named employee remuneration/expenses | 12 | 29,348 | Calendar 2014, 2015; 15-month January 2016–March 2017 transition; fiscal 2017/18–2025/26 |
| BCLC | Named employee remuneration/expenses | 15 | 8,857 | Fiscal 2010/11–2025/26, excluding held 2022/23 |
| Royal BC Museum | Named employee remuneration/expenses | 4 | 200 | 2021/22–2024/25 |
| BC Housing Management Commission | Named employee remuneration/expenses | 1 | 490 | 2023/24 |
| British Columbia Railway Company | Named employee remuneration including taxable benefits/expenses | 8 | 146 | 2017/18–2022/23, 2024/25–2025/26 |
| BC Family Maintenance Agency | Board remuneration only | 4 | 22 | 2022/23–2025/26 |

BC Railway and BCFMA are new employer candidates absent from the baseline Crown identities. BCFMA board data does not establish all-staff salary coverage. Its published Name (Location/Region) field and position footnote markers are retained. No board expenses are published: every expense and the source expense total remain null. Explicit zero remuneration for Kevin Jardine remains zero.

Every normalized row is independently reproduced from PyMuPDF positioned words and Poppler text. Original URLs, actual reporting dates, SHA-256 fingerprints, physical pages, category, definitions, controls, residuals and visible qualifications are in `sources.json`. Exact source page words, text, independent text, row boundaries and monetary fields are retained in deterministic evidence gzips. Original PDFs are cached under `/tmp/continuation-crowns`; exact paths/hashes are in [the handoff](../continuation-2026-11-01/crowns/handoff.json).

Names, initials, punctuation, repeated names, decimal cells, numeric zero and missing cells are preserved. No position is invented when the employee schedule omits it. Expense values are never included in remuneration. BCLC defines remuneration to include salary/wages, vacation payouts, allowances, bonuses where stated and taxable benefits; it excludes severance-agreement amounts. BC Railway explicitly includes taxable benefits. ICBC/Housing/Museum source remuneration is retained without an inferred base salary breakdown.

The ICBC 2016/17 schedule is explicitly **15 months, 2016-01-01–2017-03-31**. The normalized value is the published 15-month remuneration TOTAL. The separately disclosed 2016 Jan–Dec and 2017 Jan–Mar components remain in row evidence; every pair of known components agrees with its published total. No amount is annualized. ICBC controls separately include a Receiver General non-person payment: each named remuneration comparator deducts that exact published payment, rather than inventing an employee. In 2016/17–2020/21 that non-person row has a dash expense. Those printed expense controls compare known numeric disclosed cells within a broader printed table scope; a zero Receiver expense and a strict employee-only expense comparator are not inferred. Source warnings and validation state this limit.

All Museum, Railway and BCFMA named schedules were visually reviewed completely. All ambiguous layouts/fields were rendered and reviewed: Housing's literal `Celligoi R G` without comma; ICBC 2018/19 physical page 93's Poppler-split `SANDHU S.`; BCLC 2019/20 physical page 99's native column-baseline drift; BCLC 2020/21 physical page 104's Unicode negative expense; and BCLC 2025/26 physical page 74's literal $156.76 expense. Every imported page and field also passes both complete native readers. Specific visual page coverage is recorded; this collection does not claim a full visual cell-by-cell review of all 39,041 large-schedule employee observations.

Source disagreements remain visible. Housing named cells exceed controls by $3 remuneration/$4 expenses. Museum sources have small printed differences, preserve cents in 2022/23 and preserve Hardie,Colin's −$311 expense in 2024/25. BCLC historical differences range up to $16; 2025/26 known expenses sum to $4,125,994.76 versus printed $4,125,995. ICBC 2014 expenses are $27 below the printed comparator. Railway 2021/22 known expenses are $1 below its comparator. No cause is inferred or cell changed. Under-threshold expense dashes/blanks are unknown; Museum 2021/22 and 2022/23 therefore have no asserted same-scope named-expense control. Other explicit negative expenses remain qualified in their source warnings, including BCLC's −$738 for SUTHERLAND, TAMMY and −$704 for TURNER, TRICIA.

Compiled replacement is a separate parent decision. [The eight same-label receipts](../continuation-2026-11-01/crowns/compiled-overlap-review.json) enumerate exact source periods and compiled scopes without guessing calendar/fiscal equivalence. The parent retains three unresolved compiled partitions using `retainCompiledPartition`: ICBC 2017/18 (1,681 of 1,709 compiled name/pay observations matched, including 13 unresolved explicitly board-labelled observations), BCLC 2017/18 (478 of 481 matched), and Museum 2023/24 (33 of 33 match the actual 2022/23 source only after whole-dollar rounding, while actual 2023/24 has 55 named employees). Each source keeps truthful complete employee flags and a visible retained-partition/possible-overlap warning with a validation reason. No period correction is made in this pass. Other parent full-multiset comparisons support their separate fiscal replacement decisions.

Reproduce from original official PDFs (missing originals may be fetched only at the pinned URLs/hashes):

```sh
python scripts/continue_crowns.py --fetch --verify
```

Offline evidence replay and parser/source regression checks require no network, PDF engine or OCR engine:

```sh
python scripts/continue_crowns.py --offline --verify
python -m unittest discover -s scripts -p test_continue_crowns.py
```

All 10 tests pass and offline replay reproduces every normalized payload byte exactly. [Frozen-payloads](../continuation-2026-11-01/crowns/frozen-payloads.json) pins all 88 normalized/evidence files. No outbound contact, records request, FOI submission or fee payment occurred.
