# Independent current Crown source review

Reviewed 1 November 2026 by the health continuation worker. **All 4,700 assigned normalized rows match an independently implemented PDFMiner/pdfplumber reader exactly**, including names/initials, remuneration, null versus numeric expense values, multiplicity and physical pages. The review script imports none of the Crown worker parser. Original and data hashes, per-page counts and repeated-name counts are retained in `crowns-current.json`.

Reproduce: `python scripts/continue_health_cross_review_crowns.py` using the locked original cache paths in that JSON.

| Candidate | Independent rows | Original period and scope | Controls |
|---|---:|---|---|
| ICBC FY2025/26 | 3,625 | Cover and physical employee pages75–109 explicitly end31March2026; named employee schedule, board starts physical110. Names are published surname/initials. | Printed over-threshold remuneration415,313,973 minus separately printed non-person Receiver General32,520,826 equals382,793,147 exactly; expense sum3,815,244 agrees. Published zero expenses remain zero. |
| BCLC FY2024/25 | 1,075 | Cover and employee pages68–99 explicitly end31March2025; schedule marked **Unaudited**. Board is separate on physical67; physical99 contains controls only. | Named pay120,089,308 and expenses5,080,259 both agree exactly. Receiver General7,311,378 is a separate aggregate and excluded. |

All35 ICBC employee pages and all32 BCLC employee/control pages were viewed in rendered contact sheets for stable layout, panels, scope transitions and truncated/wrapped row hazards. Detailed full-size checks covered ICBC75 and109, BCLC68,94 and99. This does **not** claim individual visual transcription of every row. Full-field machine agreement covers every row.

The ICBC images confirm repeated initials represent separate source rows, rather than duplicates to discard; source positions are unpublished. The final-page Receiver General control adjustment is justified by the exact separately printed amount, not a guessed residual explanation.

BCLC page94 explicitly prints `(738)` for SUTHERLAND, TAMMY expenses. The normalized−738 is correct; a visible negative-expense source warning was requested. BCLC remuneration includes salaries/wages, vacation payouts, bonuses, perquisite allowances and other taxable benefits, with severance agreements excluded as the original states; it is not labelled base salary. Expense dashes remain unknown/null. No other acceptance blockers found in these two candidates.
