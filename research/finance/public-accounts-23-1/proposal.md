# "Where the money goes": feasibility and proposal

Research note, 27 November 2026. Every source below was opened on that date unless stated otherwise.
The figures in the worked example are read straight from the cited pages.

## Recommendation in one paragraph

Start with a **Money card in the atlas panel**, built the same way as the existing Salaries card.
A small generated index ships with the page, and per-body detail loads when the panel opens. Feed it
first from three sources that are cheap to extract and reliable.

1. The statement links already inventoried in `inventory.csv` and `post-secondary-statements.csv`.
   These need no extraction.
2. The Public Accounts **"Adjusted Net Income of Crown Corporations, Agencies and the SUCH Sector"**
   table. It gives revenue, expense, net income, adjustments and dividends for every Crown and
   agency in one place, and SUCH by sub-sector, for every year back to at least 2008-09.
3. The **CRF Detailed Schedules of Payments – Government Transfers** CSVs on the BC Data Catalogue.
   They give what each ministry paid each recipient of $25,000 or more, from FYE 2007 to FYE 2026.

Revenue by source and expense by function come from each body's own statements. Add them in a
second stage, body by body, with page citations. A separate flows view (ministry → body → function)
should wait until the ministry side and an elimination rule are in place. That view is where double
counting bites.

## Sources

| Source | What it holds | Format | Years | Extraction |
|---|---|---|---|---|
| **Organization financial statements** (sup-e PDFs; ministry page for post-secondary). Inventory in `inventory.csv` and `post-secondary-statements.csv`. | Audited statement of operations (revenue by source, expense by function), expense by object in the notes, government transfers in notes, related-party notes, budget column. | PDF, one per body and year. Text layer from about 2010; many 1999-2010 files are image-only scans. | sup-e 1999-00 to 2025-26; post-secondary 2014-15 to 2025-26 on the ministry page. | **Hard to automate, easy to do by hand.** Line labels differ by body and year; units differ (BCNET in dollars, health authorities and colleges in $000). `pdftotext -layout` reads the modern PDFs cleanly. About 80 bodies a year; one operations page plus one or two notes each. |
| **Supplementary Information: Adjusted Net Income of Crown Corporations, Agencies and the SUCH Sector**. `…/public-accounts/<yyyy-yy>/pa-<yyyy-yy>-supplementary-information.pdf` | Per Crown and agency: revenue, expense, net income, adjustments, dividends, adjusted net income ($ millions). SUCH appears only as School Districts / Universities / Colleges and Institutes / Health Authorities / Hospital Societies. Self-supported enterprises are listed separately. Also a SUCH statement of operations by sub-sector and the Consolidated Staff Utilization (FTEs). | PDF, 8-10 pages. Text layer present. | Checked 2008-09, 2015-16, 2024-25 and 2025-26. The file exists for every year in between under the same URL pattern (HEAD-checked 2008-09, 2012-13, 2015-16, 2017-18, 2020-21, 2024-25). | **Easy.** About 50 rows a year. `pdftotext -raw` gives one line per body; check that the rows sum to the published subtotals. Older layouts wrap values onto the next line, so a per-year review is needed. |
| **CRF Detailed Schedules of Payments – Government Transfers**. [Catalogue dataset](https://catalogue.data.gov.bc.ca/dataset/903c41c4-09c7-4af9-a43c-af3b6ff5c705) (Open Government Licence – BC) | Payee name, paying ministry and amount for every transfer of $25,000 or more from the Consolidated Revenue Fund. FYE 2025: 16,648 rows totalling $66.2 billion. | CSV (also inside the 772-page Detailed Schedules of Payments PDF). Title lines before the header. Amounts are text with commas. Some characters are mis-encoded (an en dash shows as `�`). | FYE 2007 to FYE 2026 (20 files). | **Easy to parse, moderate to join.** Payee names are upper-case free text (e.g. `THE CANADIAN BLOOD SERVICES`, `SCHOOL DISTRICT NO 05 SOUTHEAST KOOTENAY`), so an alias table to atlas IDs is needed. Many payees are **individuals** (foster and care providers), so only keep payees matched to a body. |
| **CRF Detailed Schedules of Payments – Other Supplier Payments**. [Catalogue dataset](https://catalogue.data.gov.bc.ca/dataset/f6bad1d5-d1dc-4fdd-a076-650f55cc3fbc) | Supplier and amount for payments of $25,000 or more. The FYE 2024 file has `Name, Amount` only, with no ministry column. | CSV (FYE 2025 resource is labelled CSV but is `.xlsx`). | FYE 2007 to FYE 2026. | Easy, but of limited use for bodies. It shows what ministries buy from Crowns (e.g. Northern Health Authority, $115,848 in FYE 2024), not what bodies spend. |
| **CRF Supplementary Schedules**. `pa-<yyyy-yy>-crf-supplementary-schedules.pdf`, 129 pages for 2025-26 | Schedule of Net Revenue by Source; Expense by Function; Expense by Group Account Classification; other schedules. | PDF. | Each year with the Public Accounts. | Moderate. This is the ministry-side actuals counterpart to the Estimates. |
| **Estimates and the Supplement to the Estimates** (Budget) | Voted appropriations by ministry, vote and sub-vote; the Supplement breaks each sub-vote down by standard object (salaries, grants, operating costs). | Estimates: PDF (e.g. [`2025_Estimates.pdf`](https://www.bcbudget.gov.bc.ca/2025/pdf/2025_Estimates.pdf)). Supplement: **CSV/XLSX** on the catalogue (Treasury Board Staff datasets `budget-2012-supplement-to-the-estimates` … `budget-2026-supplement-to-the-estimates-`). The 2025 file has 9,240 rows and three years (2026-2028) keyed by the chart-of-accounts segments. | Budget 2012 to Budget 2026 as CSV; PDFs earlier. | Easy for the CSV. It is a **plan**, not an actual, and it is organized by vote, not by recipient body. |
| **Statements of Financial Information (SOFI)** under the Financial Information Act | Each Crown, health authority, college, university and school district publishes schedules of remuneration of $75,000 or more, expenses, and **payments to suppliers of $25,000 or more**. | PDF on each body's own site; there is no central index. | Varies by body. | Hard (one source per body). The site's salaries research has already found and cited many SOFIs for the employee schedules (`research/salaries/`, `scripts/build-salaries.mjs`), so the supplier schedules in the same files are the cheapest place to start if body-level outflows are ever wanted. |

**What is not available as data.** The Province publishes no machine-readable version of the
organizations' financial statements. The only cross-body numbers in a table are the Supplementary
Information figures above, in millions and with SUCH aggregated.

## What the site already has that can be reused

- `src/government/Salaries.jsx` and `src/government/salaries.js`. This is the pattern to copy: a
  generated `salaryIndex.js` holds totals per body and year; detail rows are fetched from
  `public/salaries/<year>/<key>.json` when the panel opens and cached for the visit. A year picker
  shows the years with no data as gaps. Source and coverage notes travel with each year
  (`DisclosureSummary`, `SourceLink`, `coverageStatus`).
- `src/salaries/money.js` (`formatMoney`), `src/salaries/inflation.js` (CPI adjustment, already backed
  by `research/salaries/cpi`), `src/salaries/exportCsv.js`, `src/salaries/DataTable.jsx`, and
  `YearPicker` in `src/salaries/parts.jsx`.
- `src/government/FundingHistory.jsx`. This renders period / organizations / role / note / source
  rows, so a "Received from ministries" list can be fed as rows without a new component.
- The salaries research also holds Public Accounts FTE series (see `research/salaries/README.md`).
  The Consolidated Staff Utilization in the same Supplementary Information PDF would extend it.

## Proposed design

### Where

1. **Atlas panel: a "Money" card** for any body that has data. It shows:
   - a headline: revenue, expense and surplus or deficit for the year on screen (nearest available
     year, like Salaries), with a link to the audited statement PDF and page;
   - **revenue by source** as one stacked bar: provincial transfers, federal, own-source (fees,
     tuition, sales), other government-entity bodies, and other;
   - **expense by function** as a second bar, labelled as the body labels it, with expense by object
     available on expand;
   - **"From ministries"**: the transfer rows from the Government Transfers CSV for that fiscal year
     (ministry, amount), with a note that they are cash payments of $25,000 or more and need not
     equal the revenue the body recognizes;
   - a small trend line of revenue and expense across years, with an inflation toggle reusing
     `inflation.js`.
   Bodies with only a document link (most years) show the "Audited statements" list alone.
2. **Later, a separate `?view=money` page.** It would hold a table of every body for one year (sortable
   by revenue, expense or provincial share) and a flows diagram: ministry → body → function. Build it
   only after the elimination rules below are written down.

### Staged plan

| Stage | Work | Data | Effort |
|---|---|---|---|
| 0 | "Audited statements" list in the panel. | `inventory.csv` + `post-secondary-statements.csv` joined via `crosswalk.csv`. | Small: no extraction. |
| 1 | Revenue, expense, net income and dividends per Crown and agency, every year from 2008-09. Sector totals for SUCH. | Supplementary Information table. | About 18 PDFs × about 50 rows; semi-automatic with subtotal checks. |
| 2 | "From ministries" per body. | Government Transfers CSV FYE 2007-2026 plus an alias table (payee name → atlas ID). | The alias table is the work: about 150 bodies plus 60 school districts. Keep unmatched and personal payees out. |
| 3 | Revenue by source and expense by function from the body's own statement, current five years first: health authorities, the 25 post-secondary institutions, and the larger Crowns. | Statements in Part 1. | About 80 bodies × 5 years, mostly hand-checked transcription with page references. |
| 4 | Ministry side: Estimates (plan) vs CRF actuals by ministry and vote. | Supplement to the Estimates CSV; CRF Supplementary Schedules. | Moderate. |
| 5 | `?view=money` table and flows. | All of the above, plus the elimination rules. | Design-heavy. |

### Data model

Generated JSON, following the Salaries split: an index that ships with the page, and detail that
is fetched on demand.

```js
// src/government/financeIndex.js (generated; totals only)
export const FINANCE_YEARS = [{ slug: '2024-25', fyEnd: '2025-03-31' }, …]
export const FINANCE_INDEX = {
  'northern-health': { '2024-25': { revenue: 1672372000, expense: 1688433000, unit: 'CAD',
      sources: ['pa-sup-e:northern-health-authority-fs-2024-25'], level: 'statement' } },
  'bcnet':           { '2024-25': { revenue: 27743998, expense: 27702483, level: 'statement' } },
  'bc-housing':      { '2025-26': { revenue: 2671e6, expense: 2574e6, level: 'pa-summary-table' } },
}
```

```js
// public/finance/<body-id>.json (fetched when the panel opens)
{
  "body": "bcnet",
  "years": {
    "2024-25": {
      "statement": { "url": "…/2024-25/sup-e/bcnet-fs-2024-25.pdf", "periodEnd": "2025-03-31",
                     "basis": "BTAA s. 23.1", "unitInSource": 1, "auditor": "BDO Canada LLP" },
      "revenue": [ { "label": "Operating revenue", "amount": 13765085, "category": "own-source",
                     "page": { "pdf": 7, "printed": 6 } }, … ],
      "expenseByFunction": [ { "label": "Shared Services & Technology", "amount": 15296622, "page": {…} }, … ],
      "expenseByObject":  [ { "label": "Staffing", "amount": 6041731, "page": { "pdf": 17, "printed": 16 } }, … ],
      "provincialFunding": { "recognized": 2360940, "receivedCash": 3928611, "page": {…},
                             "note": "Notes 3 and 4: provincial capital and operating grants" },
      "transfersReceived": [ { "ministry": "Post-Secondary Education and Future Skills", "amount": 6028610,
                               "source": "catalogue:fye25-govt-transfers.csv" } ],
      "fromOtherEntityBodies": { "amount": 24163555, "label": "Revenue from members (note 10)" },
      "restated": false,
      "extraction": { "method": "pdftotext -layout, hand-checked", "checked": "2026-11-27" }
    }
  }
}
```

Supporting tables live in `research/finance/`:
- `transfers/<fye>.csv`: the normalized catalogue file, with `payee_raw`, `ministry`, `amount`,
  `body_id` (blank if unmatched), and `match_rule`;
- `aliases.csv`: payee spelling → body ID, with first and last year seen;
- `pa-summary/<year>.csv`: the Supplementary Information rows, with `name_raw`, `body_id`,
  `revenue_m`, `expense_m`, `net_income_m`, `adjustments_m`, `dividends_m`, `adjusted_m`, `page`.

Revenue `category` should use a fixed vocabulary: `province`, `federal`, `own-source`,
`other-entity` (from another government-reporting-entity body), `investment`,
`deferred-capital-amortization`, `other`. Keep the source's own label beside it every time.

## Risks and how to handle them

- **Double counting transfers between government bodies.** The Province's money is counted again
  when it moves on. A ministry pays a health authority, and the health authority pays another
  authority or a hospital society. Northern Health shows "Recoveries from other health
  authorities and BC government reporting entities" of $27.7M in revenue and $6.05M paid to
  them. BCNET earns $24.2M "from members", the universities and colleges, which are themselves in
  the entity. The Summary Financial Statements remove these as inter-entity eliminations;
  per-body statements do not. **Rule:** a body's card shows its own gross figures, labelled as such.
  Any sum across bodies must subtract `other-entity` revenue (or use the Supplementary Information
  sector totals) and say so on screen. Never add ministry transfers and recipient expenses
  together.
- **Cash versus recognized revenue.** The transfers CSV records cash paid in the year. The
  statements are prepared under section 23.1 of the BTAA and recognize revenue on an accrual
  basis. Capital contributions are deferred and amortized; each statement has an "amortization of
  deferred capital contributions/grants" line. In the worked example the gap runs from about 10%
  (CNC: $57.1M paid, $52.0M ministry revenue recognized) to more than double (BCNET: $6.03M paid,
  $2.36M provincial revenue recognized). Show the two side by side with that explanation, and do not
  reconcile one into the other.
- **Fiscal-year alignment.** The Province's year ends on 31 March, and most bodies match. Some
  bodies end their year on other dates:
  - School districts end on 30 June.
  - Older statements in the inventory end on other dates: Victoria Line Ltd. (31 May 2002),
    British Columbia Trade Development Corporation (30 September 2003) and the Pacific National
    Exhibition (31 December 2003).
  - Wind-up statements cover part years, e.g. BC Health Research Foundation to 17 October 2002 and
    Leading Edge Endowment Fund to 10 December 2012.

  Store `periodEnd` from the statement itself, label any year that is not April–March, and never
  put such a year in the same column as an April–March year without a marker.
- **Restated figures.** Each statement's comparative column can restate the prior year after an
  accounting change or a reorganization. Likely candidates include changes of reporting framework
  among SUCH bodies, the asset retirement obligations standard (PS 3280), the financial
  instruments standards, and ICBC's move to IFRS 17. None of these was checked statement by
  statement in this pass. **Rule:** store both the original and the
  comparative figure when they differ, set `restated: true`, and show the latest published figure
  with a footnote. The diff is mechanical once two consecutive years are transcribed.
- **Units and rounding.** Sources come in dollars (BCNET), thousands (Northern Health, CNC) and
  millions (Supplementary Information). Store whole dollars, keep `unitInSource`, and round only
  for display.
- **Renames and boundary changes.** Legal Services Society became Legal Aid BC, and the Supplementary
  Information still says "Legal Services Society" in 2025-26. Other examples are ITA becoming
  SkilledTradesBC, the Oil and Gas Commission becoming the BC Energy Regulator, and the Real Estate
  Council being amalgamated into BCFSA. Use the `org_key` joins from `inventory.csv`, and the
  atlas's own predecessor links, for trends.
- **Self-supported enterprises** (BC Hydro, ICBC, BCLC, LDB, Columbia Power) are recorded on a
  modified-equity basis. Their revenue is mostly commercial, and their dividends flow back to the
  CRF. Show net income and dividends, not "funding".
- **Personal data in the transfers file.** Thousands of payees are individuals. Publish only
  matched organization payees. Do not ship the raw file in `public/`.
- **Scans.** Before about 2010 many statements are image-only. Keep those years at the
  Supplementary Information level unless someone transcribes them by hand.

## Worked example (FY 2024-25, year ended 31 March 2025)

PDF page numbers count from the first page of the file; "printed" is the folio on the page.

### BCNET (amounts in dollars)

Source: <https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/bcnet-fs-2024-25.pdf>
(21 pages; auditor BDO Canada LLP).

Statement of Operations (PDF p. 7, printed 6):

| Revenue | 2025 | 2024 |
|---|---:|---:|
| Operating revenue (note 9) | 13,765,085 | 13,639,761 |
| Operating grants (note 4) | 2,256,069 | 1,966,547 |
| Capital grants (note 3) | 1,322,873 | 863,881 |
| Pass through services | 10,399,971 | 9,638,794 |
| **Total** | **27,743,998** | **26,108,983** |

| Expense by function | 2025 | 2024 |
|---|---:|---:|
| Cybersecurity & Identity Management | 1,195,539 | 1,720,083 |
| General & Administration | 3,569,238 | 2,715,652 |
| Network Services | 6,673,084 | 6,530,882 |
| Professional Development & Training | 105,522 | 215,664 |
| Procurement | 862,478 | 666,937 |
| Shared Services & Technology | 15,296,622 | 14,203,442 |
| **Total** | **27,702,483** | **26,052,660** |
| Annual surplus | 41,515 | 56,323 |

Revenue by source, from the notes:
- **Provincial operating grants** recognized: $1,389,498 (note 4, PDF p. 16, printed 15). Provincial
  cash received in the year was $2,769,611.
- **Provincial capital grants** amortized: $971,442; $1,159,000 received (note 3, PDF p. 15, printed 14).
- Federal (CANARIE) amounts are $341,571 operating and $317,633 capital; other sources are $525,000
  operating and $33,798 capital.
- **Province in total, recognized: $2,360,940 (8.5% of revenue).**
- Operating revenue by line (note 9, PDF p. 17, printed 16): Network Services $4,420,502; Shared Technology
  Solutions $4,736,240; Core Services $2,631,336; Interest and Other $937,256; Conference $444,173;
  Cybersecurity Services $595,578.
- **Revenue from members** (universities and colleges, themselves in the government entity):
  $24,163,555 (note 10, PDF p. 18, printed 17). That is 87% of revenue, and it is the double-counting
  case in miniature.
- Expense by object (note 8, PDF p. 17, printed 16): cost of services $8,013,593; staffing $6,041,731;
  operating $1,125,707; amortization $2,372,250; pass-through $10,149,202.

Cross-checks:
- **Transfers CSV FYE 2025**: `BCNET`, Post-Secondary Education and Future Skills, **$6,028,610**.
  The statements show $3,928,611 received as provincial grants, so $2.1M is unexplained by the
  grant notes. It may be payment for services, booked as operating or pass-through revenue.
- **Supplementary Information 2024-25** (PDF p. 3): BCNET revenue 28, expense (28), adjustments 4
  ($ millions). This agrees with the statement.

### Northern Health Authority (amounts in $000)

Source: <https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/northern-health-authority-fs-2024-25.pdf>
(37 pages).

Statement of Operations and Accumulated Deficit (PDF p. 7, printed 2):

| Revenue | 2025 budget | 2025 | 2024 |
|---|---:|---:|---:|
| Ministry of Health contributions | 1,343,900 | 1,319,628 | 1,133,360 |
| Medical Services Plan | 140,300 | 149,938 | 126,543 |
| Amortization of deferred capital contributions | 55,500 | 72,287 | 54,171 |
| Patients, clients and residents | 53,500 | 53,357 | 54,585 |
| Other contributions | 16,800 | 18,613 | 23,107 |
| Recoveries from other health authorities and BC government reporting entities | 18,300 | 27,732 | 23,764 |
| Investment income | 10,200 | 9,061 | 12,468 |
| Other revenues | 15,100 | 21,756 | 18,405 |
| **Total** | **1,653,600** | **1,672,372** | **1,446,403** |

| Expense by function | 2025 | 2024 |
|---|---:|---:|
| Acute | 940,624 | 778,900 |
| Community care | 260,435 | 226,043 |
| Long term care | 197,367 | 187,020 |
| Mental health and substance use | 92,356 | 83,977 |
| Population health and wellness | 50,171 | 45,351 |
| Corporate | 147,480 | 120,417 |
| **Total** | **1,688,433** | **1,441,708** |
| Annual operating deficit | (16,061) | 4,695 surplus |

Province share of revenue (Ministry of Health contributions plus MSP): 1,469,566, or 87.9%.

Expense by object (note 14(d), PDF pp. 31-32, printed 26-27), totalling 1,688,433:

| Object | 2025 |
|---|---:|
| Compensation | 1,227,702 |
| … of which purchased physician services | 181,611 |
| Supplies | 123,486 |
| Referred-out and contracted services | 103,152 |
| … of which paid to other health authorities and BC government reporting entities | 6,050 |
| Amortization | 66,881 |
| Equipment and building services | 109,353 |
| Sundry | 53,023 |
| Interest on debt | 4,465 |
| Loss on disposal | 371 |

Transfers CSV FYE 2025 for `NORTHERN HEALTH AUTHORITY`:

| Ministry | Amount ($) |
|---|---:|
| Health | 1,634,729,019 |
| Infrastructure | 11,637,654 |
| Children and Family Development | 704,244 |
| Public Safety and Solicitor General | 540 |

The Health payment is about $165M more than the Ministry of Health and MSP revenue recognized. This
is consistent with capital contributions, which are deferred rather than recognized, but the
statements do not reconcile it line by line.

### College of New Caledonia (amounts in $000)

Source: <https://www2.gov.bc.ca/assets/gov/education/post-secondary-education/institution-resources-administration/financial-reporting/audited-financial-statements/24-25/cnc_fs_2425_signed.pdf>
(30 pages; linked from the Public Accounts index, hosted by the ministry).

Statement of Operations and Accumulated Surplus (PDF p. 7, printed 2):

| Revenue | 2025 budget | 2025 | 2024 |
|---|---:|---:|---:|
| Ministry of Post-Secondary Education and Future Skills | 51,381 | 52,033 | 50,050 |
| Tuition | 28,791 | 30,851 | 26,780 |
| Other | 9,145 | 7,722 | 8,745 |
| Amortization of deferred capital grants | 5,019 | 4,952 | 5,142 |
| Ancillary services | 3,228 | 3,216 | 3,213 |
| Specific projects | 133 | 2,592 | 1,910 |
| **Total** | **97,697** | **101,366** | **95,840** |

| Expense by function | 2025 | 2024 |
|---|---:|---:|
| Instruction | 52,864 | 53,733 |
| Student and institutional support | 25,210 | 21,306 |
| Facilities operations, maintenance and infrastructure | 8,620 | 7,345 |
| Amortization | 6,402 | 6,415 |
| Ancillary services | 3,156 | 3,111 |
| Specific projects | 3,910 | 2,098 |
| **Total** | **100,162** | **94,008** |
| Surplus before endowment items | 1,204 | 1,832 |
| Annual surplus, after $1,150 endowment donations and matching grants | 2,354 | 2,203 |

Expense by object (note 17, PDF p. 29, printed 24):

| Object | 2025 |
|---|---:|
| Salaries and benefits | 73,229 (73% of expense) |
| Supplies and services | 7,421 |
| Contract and professional services | 5,488 |
| Cost of goods sold | 1,427 |
| Utilities | 1,547 |
| Facility infrastructure maintenance | 2,477 |
| Interest | 116 |
| Scholarships and bursaries | 2,055 |
| Amortization | 6,402 |

The ministry provides 51% of revenue and tuition 30%.

Transfers CSV FYE 2025 for `COLLEGE OF NEW CALEDONIA`:

| Ministry | Amount ($) |
|---|---:|
| Post-Secondary Education and Future Skills | 57,138,623 |
| Infrastructure | 2,296,325 |
| Children and Family Development | 9,754 |

The post-secondary payment is about $5.1M more than the ministry revenue recognized, again
consistent with deferred capital grants.

### What the example shows

- The **statement of operations alone** is enough for a useful card, and every figure in it has a
  page reference. Line labels are body-specific, so the category mapping has to be done by hand
  for each body; after the first year it carries forward.
- **Provincial share differs widely**: 8.5% for BCNET, 51% for CNC and 88% for Northern Health. That
  contrast is the story a "where the money goes" card can tell.
- **The transfers CSV and the statements never match exactly.** Show both, labelled "paid in the
  year" and "recognized as revenue".
- **BCNET** shows why a cross-body total needs eliminations: most of its revenue is other
  government-entity money already counted at the universities and colleges.
