# WorkSafeBC and University of Victoria: original-source follow-through

All six discovery IDs are accepted as complete **published named employee** cohorts: **14,715 observations**. These are actual calendar/fiscal reporting periods, not compiled edition labels. Separate board/committee, executive component, supplier, severance and below-threshold aggregate disclosures are excluded. No public-body correspondence, contact forms or fees were used.

| Official source period | Employee rows | Physical PDF pages | Row remuneration | Known expenses | Rows minus printed named controls, remuneration / expenses |
|---|---:|---|---:|---:|---:|
| WorkSafeBC calendar 2023 | 2,794 | 92–154 | $314,770,541 | $8,978,370 | +$12 / +$16 |
| WorkSafeBC calendar 2024 | 3,058 | 83–155 | $352,595,961 | $9,350,896 | −$1 / −$9 |
| WorkSafeBC calendar 2025 | 3,142 | 76–144 | $364,916,358 | $9,418,862 | +$11 / +$2 |
| UVic FY2019/20 | 1,422 | 46–61 | $173,318,599 | $7,395,619 | $0 / $0 |
| UVic FY2023/24 | 2,072 | 49–71 | $271,654,816 | $9,443,940 | −$1 / $0 |
| UVic FY2024/25 | 2,227 | 48–71 | $290,029,647 | $9,990,395 | −$1 / $0 |

Every original PDF exactly matches the discovery inventory SHA-256. UVic originals are direct official-domain PDF downloads. WorkSafeBC resource URLs return HTML on GET; the publicly available **Download PDF** control returns the original PDF through a POST containing the page's anti-forgery token and public media-item identifier. The reproducible script performs only that resource download action. Cached originals are under `/workspace/salary-source-follow-through/cache-worksafe-uvic/`; they are not embedded in the repository.

Each complete native schedule is independently extracted with **PyMuPDF original PDF word coordinates** and **Poppler `pdftotext -layout`**. Every name, remuneration, expense, duplicate occurrence and physical PDF page agrees across both readers. Every employee page has a locked row census and internally printed period heading. Scope boundaries are established by the separate preceding board page and following supplier/severance page. No OCR or glyph corrections are used.

The evidence gzip for each report retains original word/bounding-box receipts for every name and monetary cell, the independent complete layout pages and rows, and neighboring scope pages. Controls retain complete final-page source text, printed named/below/grand amounts, per-page counts, differences, unknown/zero/negative counts, exact source fingerprints and provenance. Readable first/last employee and neighboring scope pages are retained as PNGs; every employee page also appears in rendered page-sequence sheets. These are visual layout/sequence receipts; row-by-row verification is the complete independent native extraction.

WorkSafeBC remuneration includes salary, overtime, taxable benefits and other like amounts paid during the year, rounded to the nearest dollar. The financial-statement reconciliation separates employer-paid staff benefits from employee SOFI remuneration. Executive total compensation is a different disclosure and is not substituted. Surnames plus initials and genuine repeated published name strings remain separate source observations; they do not establish unique identities. Positions are unpublished and remain null.

UVic reimbursement of work-related expenses includes travel, memberships, tuition, relocation, vehicle expenses, extraordinary hiring expenses, registration fees and similar amounts. Both remuneration and expenses include grants and contracts administered by the University. The financial-statement reconciliation describes taxable benefits, deferred income and exclusion of severance payments. FY2019/20 additionally defines salary/wages, services above regular duties and retirement-related payments. Footnote markers remain in evidence rather than employee names.

The source subtotal labels say `over/> $75,000`, which is preserved in threshold metadata. Four rows are displayed at exactly $75,000 within those published named schedules: Mallari, E (WorkSafeBC 2023, physical page 126), Hiles, Clayton (UVic FY2019/20, page 52), Sui, Pang-Chieh (UVic FY2023/24, page 68), and Rakhshan, Rezvan (UVic FY2024/25, page 65). These rows are retained without inferring their unrounded values. Readable original-row crops for all four and all 18 parenthesized expense recoveries are included in the visual receipts.

Printed dashes remain **null**, explicit numeric zeroes remain **zero**, and parenthesized expense recoveries remain **negative**. A sum of known expenses does not resolve unknown cells. No source row or cell is modified to force financial controls. Small residuals are fully reproduced after complete two-reader comparison and are carried as source-specific `publicWarning` text. WorkSafeBC explicitly says its display is rounded to the nearest dollar; rounding bounds are supplied only as comparisons and do not establish the cause. UVic FY2023/24 also has a separately documented $1 difference between printed named-plus-below remuneration and the printed grand total. All other printed aggregate arithmetic reconciles.

`sources.json` is the standard six-field collection manifest; `dispositions.json` covers all six discovery IDs. `duplicate-check.json` records the accepted original manifests examined before import, excluding this collection on replay. No existing accepted WorkSafeBC/UVic original employee source overlaps these cohorts; compiled coverage is separate.

Reproduce original checks, or rebuild the complete collection and visual receipts:

```sh
python scripts/follow_through_worksafe_uvic.py
python scripts/follow_through_worksafe_uvic.py --write
python scripts/test_follow_through_worksafe_uvic.py
```

The parser needs PyMuPDF and Poppler; artifact rendering additionally needs Pillow. Frozen-evidence tests replay every row from retained independent original-reader evidence, validate financial residuals and source page census, preserve missing/zero/negative meanings, and verify deterministic gzip and artifact fingerprints.
