# Independent review: Port Moody 2025 employee disclosure

Reviewed November 1, 2026. **Recommend qualified publication of the 216 rows with numeric remuneration and taxable-benefit components, retaining four benefit-dash rows as held.** The material printed remuneration-control discrepancy remains unresolved and must be a visible warning. This is a source-field fidelity decision, not certification that the issuer's aggregate is correct or that the schedule reconciles financially.

## Original, reporting period and publication

- [Official source index](https://www.portmoody.ca/city-government/plans-reports-and-publications/), [original 2025 SOFI](https://media-002-ca.cdn.govstack.com/portmoody-014-ca/media/yrkh3rw0/edms-674189-v2-2025_statement_of_financial_information_-sofi.pdf).
- Original SHA-256 independently reproduced: `2be6c71b4a1a12bf447fb363f8d3633acec16a55d4072631fb0cc973f8fdc44b`, 1,149,849 bytes, 55 physical pages. The cached original matches the author's receipt; this review does not claim a fresh HTTP retrieval.
- Physical pages 1–2 identify the year ended December 31, 2025. Salary headings and footers consistently say 2025. June 2026 preparation/approval does not change the payment year.
- Physical page 3 visibly bears Paul Rockwood's signature approving all statements and schedules, dated June 23, 2026; page 4 management responsibility is also visibly signed. The report is not marked draft in the reviewed pages.
- The contents and complete document text locate council on page 40, employees on pages 41–47, severance on 48 and suppliers from 49. Council is a separate category and is already covered elsewhere; it is not included in these 220 employee rows.

## Full row inventory and independent readers

All seven complete rendered employee pages were inspected, not just clipped table edges or aggregate cells. Each original name, complete wrapped position and all three monetary columns was compared with the candidate extraction. Rows are consecutively alphabetized from Adams to Zhang. No additional employee subsection, continuation page, aggregate-as-person row, missing salary anchor or omitted page was found.

| Physical page | Original rows | First original name | Last original name | Sum of original Remuneration cells |
|---:|---:|---|---|---:|
| 41 | 31 | Adams, Peter | Brown, Corene | $3,186,375 |
| 42 | 38 | Bucsis, Donna | Finlay, Jeff | $4,435,671 |
| 43 | 37 | Fitzpatrick, Jody | Law, Kim | $4,487,936 |
| 44 | 37 | Leblanc, Paul | Parnell, Angela | $4,654,662 |
| 45 | 37 | Patterson, William | Singh, Harpal | $4,430,177 |
| 46 | 37 | Skopliak, Tyler | Yan, Angela | $4,184,803 |
| 47 | 3 | Zanon, Kate | Zhang, Rong Bing | $430,628 |
| **Total** | **220** | | | **$25,810,252** |

The author's independently positioned PyMuPDF and Poppler readers were rerun against the original. Every extracted field agrees, including wrapped titles, punctuation, benefit dashes and expense dashes. The geometry assigns full multiline cells to their own rows. Examples independently checked include Boechler, Michael's `Lieutenant Community Outreach & Life Safety`, Cornish, Michael's `Deputy Fire Chief, Community Safety and Administration`, Lam, Stephanie's `Corporate Officer & Manager of Legislative Services`, and Zanon, Kate's `Deputy City Manager & General Manager Corporate Services`. These are actual published job titles, not department labels.

A separate **uncropped pypdf layout extraction**, run independently for this review, enumerated every complete source page. Full-page numeric row lines were identified from their three terminal monetary cells, without using the author's table y-ranges, row bounds or salary-anchor inventory. All 220 names and all three monetary cells agree in the same order with the two positioned readers. Counts on each page independently reproduce 31/38/37/37/37/37/3. Aggregate lines were retained as source controls, excluded from names. This third inventory reproduces Remuneration $25,810,252, known Taxable Benefits $437,523 and known Expenses $322,434. It provides no evidence of a $3 million omitted individual component or cohort.

Review work products are in `/tmp/history-review-port-moody/`: full rendered pages `p41.png`–`p47.png`, full pypdf layout text `p41-pypdf-layout.txt`–`p47-pypdf-layout.txt`, and the full two-reader row inventory `two-reader-rows.json`. The parser/config under review are `scripts/parse_history_lower_mainland.py` and `research/salaries/municipal-history-lower-mainland/reviewed-layouts.json`. This reviewer changed neither.

## Actual column definitions and missing values

Page 41 specifically defines **Remuneration** as base salary, acting pay, overtime and retroactive rate increases. It separately defines **Taxable Benefits** as group life insurance and other allowances, including one-time banked vacation/gratuity payments. Numeric components can be combined for normalized remuneration under that table-specific definition. Expenses remain separate. The broader narrative on page 5 groups salary, benefits and contractual payouts more generally; the table-specific definitions and separate actual cells govern this import. Page 6 states that SOFI schedules use amounts paid during the fiscal period, a cash basis. None of these amounts is treated as an annual base salary rate.

The employee heading explicitly says `Staff (Greater than $75,000)`. Three named rows have a Remuneration-column amount below $75,000 but a known combined remuneration above it: Haddon, Brad $74,633 + $867 = $75,500; King, Traci $74,794 + $1,721 = $76,515; Wilde, Andrew $73,728 + $1,717 = $75,445. They are genuine source rows and must not be removed by filtering only the first compensation component.

Four original benefit dashes do not establish zero. Their complete rows remain held because normalized composite remuneration cannot be computed faithfully:

| Name | Position | Page | Known original Remuneration | Benefits | Expenses |
|---|---|---:|---:|---|---|
| Cameron, Matthew | Labourer | 42 | $78,882 | Dash / missing | Dash / missing |
| Dhak, Jaspal | Senior Facilities Maintenance Worker | 42 | $82,724 | Dash / missing | Dash / missing |
| Mohebi, Mohammad | Senior Facilities Maintenance Worker | 44 | $78,143 | Dash / missing | Dash / missing |
| Virgo, Everton | Building Services Worker 1 | 46 | $77,927 | Dash / missing | Dash / missing |

Their known first-column amounts total $317,676, retained in evidence without inventing benefits or composite pay. The 216 known-component rows total normalized remuneration **$25,930,099** and known numeric expenses **$322,434**. The latter is not a claim that missing expenses are zero. There are 23 expense dashes across the complete 220-row source, including the four held rows; no explicit numeric zero or negative expense occurs in these 2025 source rows. The retained original dash, rather than a fabricated zero, must remain reproducible.

## Material control discrepancy: source conflict, cause unproved

Page 47 visibly prints these controls:

| Source control | Remuneration | Taxable Benefits | Expenses |
|---|---:|---:|---:|
| Staff greater than $75,000 | $28,810,242 | $437,511 | $322,435 |
| Staff less than $75,000 | $10,508,868 | $88,956 | $41,584 |
| Grand total staff | $36,319,110 | $526,467 | $364,019 |

The **printed remuneration controls themselves conflict**: $28,810,242 + $10,508,868 = $39,319,110, exactly **$3,000,000 more** than the printed grand total $36,319,110. This conflict exists without any extraction or individual-row assumption. The printed benefits and expenses control equations, in contrast, add exactly to their printed grand totals. These are three separate source columns, not a shifted total or a single compensation-total column.

All 220 published Remuneration cells sum to $25,810,252, **$2,999,990 below** the printed named subtotal $28,810,242. Grand remuneration less the under-threshold aggregate is $25,810,242, which is **$10 below** the row sum. Known benefits are $12 above the printed named benefits control; known expenses are $1 below the printed named expense control. These smaller residuals are also unresolved, and benefit/expense dashes must not be certified as zero to call them complete totals.

Neither the separate $437,511 named benefit control nor the separate council schedule explains a $3 million pay difference. Employer CPP ($1,869,885) and employer EI ($628,906) are separately labelled on page 47 and are not employee remuneration or missing individual cells. The source also explicitly says that this schedule is not reconciled to the Statement of Operations because the formats differ. No general financial-statement payroll figure is substituted for a named cohort control.

The evidence supports a conflicting source aggregate, but **does not prove which control is wrong, a typographical cause, an intended corrected figure, or an explanation for the remaining $10**. No replacement subtotal or per-person adjustment should be created. The material discrepancy must never be described as rounding or as reconciled.

## Publication requirements and conclusion

Qualified publication is supportable because all 220 actual source rows and their columns are accounted for independently, and all 216 accepted composite-pay values use actual numeric components. The aggregate contradiction is preserved rather than converted into individual data. Keep a visible warning with ordinary readable currency amounts, specifically naming the published Remuneration-column mismatch **−$2,999,990**, the internally conflicting $3,000,000 printed aggregate equation, and the unresolved benefits/expense residuals. A scientific-notation amount or a claim that all controls passed would obscure the issue.

Mark the employee schedule incomplete at both source and validation levels; identify all four held names/pages/components. Distinguish the complete 220-row source-component controls from the 216-row accepted subset and its $25,930,099 composite-pay sum. Do not publish the known first-column value as full remuneration for a held row. Retain the raw columns, all original controls, source hash and explicit unresolved reason. Route a corrected worksheet/report or clarification to the remaining queue; no request was sent by this review.

No source-field blocker was found for the 216 known-component rows.

Final generated-source follow-up: the author's frozen 2025 manifest was inspected. It contains 216 accepted / 220 original named rows, all four held names and missing components, `completeEmployeeSchedule:false` at both source and validation levels, readable material/control warnings, the literal printed aggregate controls and their exact conflicting equations, and the independent-review pointer. Its normalized rows exactly match this review's independently reproduced accepted subset in all six fields. The normalized data SHA-256 is `31b37b59a8931c05a4a607c3fcd09449936cfe0c940adffb0e154f8e697e8d6f`; the retained evidence SHA-256 is `24f72527e6aeff9193e5cd9e21acb9b8c1a9bad57e85be2910c0593c733fabf0`. The final warning preserves the full-source −$2,999,990 remuneration mismatch, the printed $3,000,000 aggregate contradiction, the remaining +$10 against grand less under-threshold, and known benefits +$12 / expenses −$1. It explicitly distinguishes those full-source controls from the 216-row accepted composite-pay subset. **Final metadata and normalized-subset checks pass; the qualified-publication recommendation stands.**
