# Independent SD52 employee/control review

**The 156 named employee rows are independently corroborated, but the printed employee controls do not reconcile and are not explicitly a combined trustee/employee control.**

The original PDF SHA-256 is `2fecb9155bd14fa68439947713730d0f1fe9716c332cb0aa3b6b341478e919d9`, cached at `/tmp/pofbc-schools/ministry-sd52-2025.pdf`. Physical pages 53–55 are the complete three-page remuneration schedule for the year ended June 30, 2025. Each complete page was rendered and every named employee/trustee row, column, page boundary and control was visually reviewed.

A separately implemented PDFMiner/pdfplumber reader, importing none of the school worker parser, exactly matches every employee name, title, remuneration, null versus numeric expense, ordering, multiplicity and physical page. Counts are 65 employees on page 53, 76 on page 54 and 15 on page 55, totaling 156. Seven elected officials are separate source rows on page 53. No omitted complete employee rows were found.

| Comparator | Remuneration | Expenses |
|---|---:|---:|
| Employee row sums | $16,901,344.89 | $161,620.27 |
| Printed `TOTAL EMPLOYEES PAID AT LEAST $75,000` | $17,009,720.61 | $182,940.38 |
| Employee sums minus printed controls | −$108,375.72 | −$21,320.11 |
| Separate `TOTAL ELECTED OFFICIALS` | $108,375.72 | $21,320.11 |

Page 53 visibly labels the employee section `SCHEDULE OF EMPLOYEES PAID AT LEAST $75,000`, separately from `ELECTED OFFICIALS` and its subtotal. Page 55 visibly labels the disputed subtotal `TOTAL EMPLOYEES PAID AT LEAST $75,000`. No explicit note says that subtotal combines elected officials and employees. The matching differences are exact arithmetic, but they do not establish the issuer's reason. Subtracting trustee totals and reporting employee controls as reconciled would infer an unpublished comparator.

The rows can be considered as source-faithful candidates under the project's documented source-control policy, with visible exact residuals and no adjusted cells or inferred explanation. Alternatively retain the existing hold pending issuer clarification. Parent makes the acceptance decision. Keep trustee and employee scopes distinct; the trustee blank expense for Pucci remains unknown, not zero.

The accompanying JSON retains exact hashes, counts, sums, review coverage and a concrete unsent issuer clarification draft. Reproduce the third-reader comparison with `python scripts/continue_health_cross_review_sd52.py`. No external request or message was sent.
