# Independent early Public Accounts control review

Reviewer: Crown continuation worker, 2026-11-01. Decision: the seven candidate employee cohorts faithfully reproduce the named original schedules. The three material summary discrepancies below remain unresolved and require exact public warnings; no observation should be changed to force a balance. This is an independent recommendation to the parent, not a publication action.

The author used PyMuPDF and Poppler. This review independently read **all 13,450 named rows**, with multiplicity, using PDFMiner/pdfplumber and a separately implemented cropped-column line parser. Every name, remuneration, disclosed travel amount, blank travel cell and physical page agrees with the candidates. It recovered counts 963, 1,137, 1,706, 1,957, 2,551, 2,525 and 2,611 for 1999/00 through 2005/06. The exact original fingerprints, page lists, sums, row hashes and field comparisons are in `government-early-controls.json`; the independent full page text and rows are retained in `government-early-controls-evidence.json.gzip`.

The original summary rows are explicitly labelled “Other employees—earning $75 thousand or more”, separately under salary and travel. I visually checked original summary physical page 5 for 2000/01 and page 6 for 2002/03; native original evidence also confirms page 6 for 2001/02. These are the matching comparator scopes, and the summary unit is thousands. The named schedule headings explicitly state gross salary of $75,000 or more. Preceding pages in 1999/00–2002/03 contain the separately labelled OIC/appointee schedule; following pages begin grants/transfers. No subtotal, aggregate, supplier or non-person row is imported into the named cohort. All independently recovered salary cells satisfy the disclosed threshold. Printed duplicate observations remain separate.

| Period | Named salary | Summary salary | Residual | Named known travel | Summary travel | Residual |
|---|---:|---:|---:|---:|---:|---:|
| 2000/01 | $95,837,081 | $88,864,000 | +$6,973,081 | $6,767,042 | $6,767,000 | +$42 |
| 2001/02 | $145,459,401 | $145,459,000 | +$401 | $7,817,360 | $7,815,000 | +$2,360 |
| 2002/03 | $171,231,079 | $171,648,000 | −$416,921 | $10,049,544 | $10,068,000 | −$18,456 |

The 2000/01 salary, 2001/02 travel and both 2002/03 residuals exceed the precision of a nearest-thousand comparator. Complete independent extraction did not identify an omitted row, swapped monetary column, accidentally imported subtotal or unintended deduplication. The rendered summaries confirm the printed controls. The source gives no reconciliation explaining these residuals; their cause is **unresolved**. In particular, neither numerical coincidences nor the footnotes establish a cause. The 2002/03 footnote says salary can include base salary, retroactive pay and benefit/vacation payments from current or prior years; it does not explain the summary difference.

For 1999/00 and 2003/04–2005/06 the salary residuals are +$214, +$285, −$234 and +$47, each within the summary's nearest-thousand precision. Travel is supplied in the same row only for 1999/00–2002/03. Later employee salary tables do not disclose same-row travel: all candidate expense fields are null, and this review makes no cross-schedule joins or zero-expense assertion.

I additionally rendered and reviewed 2001/02 physical page 22: `DEWITT-VAN OOSTEN, J M` wraps to the next physical line, and the candidate correctly retains $87,739 salary/$4,946 travel. On the rendered 2004/05 physical page 39 the source literally prints `ST , T`, with $83,080; it is preserved without attempted identity repair.

Reproduce this third-engine review against the cached hash-pinned originals:

```sh
python scripts/continue_crowns_review_government.py
```

The independent reader covers every employee page and column. Visual review here covers the specified summaries and two layout/name hazards; it does not claim a visual review of every salary cell. The matched three native readers support accepting the exact observations with the stated source qualifications. A clarification request for the three unresolved discrepancies remains appropriate as a draft only.
