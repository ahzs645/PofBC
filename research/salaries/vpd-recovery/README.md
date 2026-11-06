# Vancouver Police recovery, 6 November 2026

**1,237 additive observations**, not the 1,324 gross rows in the three originals:

| Accepted cohort | Rows | Source |
|---|---:|---|
| 2009 unnamed residual | 1,125 | Complete 1,212-row anonymous schedule less the 87 named overlaps |
| 2009 publicly named OIPC subset | 87 | Two-page response to OIPC Order F10-22 |
| 2025 executives | 25 | One-page executive remuneration and expenses release |

The official index links both 2009 releases side by side, posted July 29, 2010. The anonymous PDF explicitly reports January 1–December 31, 2009; the named original explicitly reports 2009. Neither the website upload date nor release date determines the payment year.

Every named remuneration/expense pair occurs exactly once in the full anonymous schedule. The named rows are imported from their own public source; the matching monetary observations are excluded from the anonymous additive cohort. No name is assigned to an anonymous source row and no undisclosed identity is inferred. The overlap ledger records both physical pages and ordinals. The complete anonymous original extraction remains separate evidence, **not an additional import**. Both the sum of remuneration and the sum of known expenses are conserved exactly to cents.

Two independent extraction paths, Poppler layout lines and PyMuPDF words grouped by coordinates, agree on all 1,212 original anonymous rows, including page and null expenses. All 87 named scan rows and 25 executive scan rows were visually compared with their original rendered pages. Reviewed transcriptions and original PDF SHA-256s are pinned by the offline importer. OCR alone was not accepted: examples of OCR mistakes corrected from the image include NELMES's leading digit, ROBINSON's expenses, STEWART's initial and remuneration, and USUI's remuneration. Each named monetary tuple independently agrees with the native anonymous source.

There are no printed aggregate totals in these releases; validation reports computed sums honestly as computed, not independently printed controls. Expense dashes stay null, not zero. Thresholded disclosures are not a workforce census. The executive cohort is explicitly executive-only and must not be described as whole-workforce coverage.

## Reproduce and integrate

1. Run `python scripts/recover_vpd_salaries.py` from the repository root. Requires Poppler and PyMuPDF, no network.
2. Run `python -m unittest discover -s scripts -p test_recover_vpd_salaries.py -v`.
3. Add `vpd-recovery` to `research/salaries/collections.json`, then run the standard salary build and validation. This worker did not modify shared collections or generated exports.

Original URLs, byte lengths, hashes, totals and page counts are in `validation.json`; accepted provenance and qualifications are in `sources.json`. `evidence/overlap-ledger.json.gzip` explains the non-additive overlap. `evidence/2009-anonymous-complete.json.gzip` retains all original monetary rows. `originals/2009-city-sofi.pdf` is a downloaded discovery lead only, not an import or evidence supporting these rows.
