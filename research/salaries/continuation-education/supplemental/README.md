# Supplemental postsecondary native schedules

This separate frozen batch adds **5 cohorts /2,078 rows**: North Island2024/25 (200), TRU2022/23 (661) and2024/25 (840), and Emily Carr2023/24 (170) and2024/25 (207). It does not duplicate North Island's accepted2020/21 source. All employee names, remuneration, expenses, physical pages, ordering and multiplicity agree between independent PyMuPDF and Poppler parsers. Positions are not published for these employee tables. Board, supplier and employer-benefit reconciliation scopes remain separate. No negative expenses occur.

North Island and both Emily Carr printed named controls reconcile exactly. TRU has small whole-dollar residuals, retained with exact public warnings. All sources pin original/data SHA-256 hashes, original fiscal headings, row-level offline evidence and control receipts. Original employee rows are native text; the two Emily Carr approval pages are scanned and were rendered and inspected, with visible board/finance signatures.

**TRU qualification:** both publicly posted originals have blank signature/date lines on their approval forms. Neither is claimed to be a signed original. For2022/23, official September29,2023 board minutes at physicalpage6 of the December1 agenda package explicitly approve circulated FIA reporting; the separate approval evidence is hash-pinned in the source validation. For2024/25, independent adoption evidence has not yet been verified. That qualification is visible in the source warning and requires parent publication review. It must not be silently converted into a signed/adopted claim.

Reproduction:

```sh
python scripts/continue_education_supplemental.py --originals
python scripts/continue_education_supplemental.py
python -m unittest discover -s scripts -p test_continue_education.py -v
```

Each source's `visualReviewPdfPages` records the exact rendered approval/first/control pages checked. The parser specifically handles the source typo `Renumeration`, star-marked expense headings and Emily Carr's `Total Renumeration` heading without treating it as an expense-inclusive total. The underlying words and payment definitions remain unchanged.

Frozen original/data hashes and cache paths are in `continuation-2026-11-01/education/supplemental/frozen-batch-2.json`. The supplemental replacement receipt identifies170 compiled Emily Carr2023/24 rows; it has no explicit board/governor title candidates. Parent determines replacement scope. Fresh search retrieval failures are retained honestly in `new-document-receipts.json`: UFV2017/18 returned non-PDF content; Douglas2019/20 and2020/21 and UBC2023/24 indexed URLs returned404. Royal Roads2024/25 was retrieved but its employee schedule still needs image/OCR processing. None of those is counted as accepted coverage.
