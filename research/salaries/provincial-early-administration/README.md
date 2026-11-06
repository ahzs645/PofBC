# Early provincial salary recovery

Reproduce offline: `python scripts/import-provincial-early.py`.
Test: `python -m unittest discover -s tests -p 'test_provincial_early.py'`.
Requires Poppler `pdftotext`; no network calls occur in either command.

Seven original official Public Accounts PDFs support 14 schedules for fiscal 1999/00–2005/06: 310 deputy/associate-deputy observations and 242 cabinet executive-salary observations. These do not overlap the existing 2006/07+ catalogue imports. Exact official source URLs and PDF hashes are in `sources.json`. Only selected compensation-table pages are retained as readable extracted text. Full original PDFs remain unchanged. Each normalized row points to its physical PDF page.

Minister executive salary is a separate component in `provincial-cabinet`, additional to MLA member compensation, and is not represented as total compensation. Deputy schedules remain in `public-service` with their own scope, separate from general employees and OIC appointees. These small cohorts do not replace compiled whole-employee partitions.

For 1999/00–2001/02, separately disclosed deferred compensation is included in remuneration, with salary and deferred amounts preserved independently in audit files. Travel and capital city living allowance remain expenses. Missing expense figures remain null. Published initials and spelling are preserved without identity joins. The 1999 table spells one name “Underleider”; this is not silently changed to later “Ungerleider.”

Published deputy schedules include D Scott Campbell corporate contract payments in 2002/03 and 2003/04. Their position labels and source notes explicitly identify contracted services paid to D Scott Campbell and Associates Inc, not employee payroll.

Numeric controls compare each column to printed table totals. Six years reconcile exactly. The 2003/04 published errata page has small differences between displayed rows and printed totals: minister salary/living/travel -$1/+$2/-$4, deputy remuneration/travel +$1/-$1. Every one of its 80 named rows was checked independently using raw PDF extraction, and the page was visually reviewed. No balancing adjustments were made. The published Joyce Murray correction to $38,717 is retained. These exact discrepancies are pinned and tested rather than covered by a permissive tolerance.

Overlap check: existing `continuation-government-police` imports the same years' Other Employees and OIC/appointee schedules, not these deputy or cabinet tables. Comparing every new observation against those existing cohorts found no name-and-remuneration duplicates and no deputy-name candidates. Four cabinet name-similarity candidates have different amounts and remain unlinked; short initials do not establish identity. Detailed diagnostics are in `overlap-check.json`. The deputy employer slug `public-service` is identical to existing later deputy imports.
