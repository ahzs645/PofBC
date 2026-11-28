# Finance research: transfers, statement breakdowns, estimates against actual

Research, 27 November 2026. These folders feed the atlas's Money card (`src/government/Money.jsx` and
`MoneyParts.jsx`) through `scripts/build-finance.mjs` (`npm run build:finance`, `npm run check:finance`).
The earlier stages (statement links and the Adjusted Net Income table) are in
[`public-accounts-23-1/`](public-accounts-23-1/README.md); its `proposal.md` sets out the plan these
three stages follow ("Staged plan", stages 2 to 4).

Downloaded files live in `cache/`, which is not committed. Every source URL is in the tables.

## A. From ministries: Government Transfers

**Source.** *CRF Detailed Schedules of Payments – Government Transfers*, BC Data Catalogue
([dataset](https://catalogue.data.gov.bc.ca/dataset/903c41c4-09c7-4af9-a43c-af3b6ff5c705), Open
Government Licence – British Columbia). One CSV per fiscal year, FYE 2007 to FYE 2026 (20 files): payee,
paying ministry and amount for every payee that received $25,000 or more from the Consolidated Revenue
Fund in the year. Rows under $25,000 appear when the payee's total for the year passes $25,000. A lone
dash is read as nil.

| File | What it is |
|---|---|
| `transfers/alias-decisions.csv` | Decisions made by hand: a payee spelling and the body it is, or a blank body to keep the payee out. |
| `aliases.csv` | Every payee spelling matched to a site body (287 spellings; 281 matched, 6 kept out by decision), with the rule, first and last year seen, rows and the spellings as printed. Decisions that keep a payee out are listed with a blank body. |
| `transfers/fye<YYYY>.csv` | The matched rows of each year, as printed. |
| `transfers/totals.csv` | Each file's row count and total, and how much of it is matched. FYE 2025: 16,648 rows, $66,243,987,195; 434 rows and $46.7 billion matched to 148 bodies. |

**Matching** (`scripts/build_transfers.py`), in order: the hand decisions; school districts by
number ("SCHOOL DISTRICT NO 5 …", "BOARD OF EDUCATION OF SCHOOL DISTRICT NO. 91 …"); then a payee whose
words equal one of a body's names, with "British Columbia" read as "BC" and Ltd./Inc./Corporation/Society
ignored. A spelling that names more than one body is kept out. **Unmatched payees and every individual
are kept out**: only matched rows are written, and the raw files stay in the cache.

Reproduce:

    node research/finance/scripts/dump_bodies.mjs research/finance/cache/bodies.json
    python3 -I research/finance/scripts/build_transfers.py research/finance/cache/transfers research/finance/cache/bodies.json research/finance

## B. Revenue by source and expense by function

**Source.** Each body's own audited statement of operations: the Public Accounts' `sup-e` PDFs, and the
ministry's page for universities and colleges (`public-accounts-23-1/inventory.csv`,
`post-secondary-statements.csv`).

| File | What it is |
|---|---|
| `statements/index.csv` | One row per transcribed statement: body, fiscal year, URL, unit, title, PDF page, printed page, method, date checked, note. |
| `statements/<body>/<year>.csv` | Every revenue and expense line as printed, the printed totals and the year's result, each with its PDF page and printed page; each revenue line has a category from the fixed vocabulary (`province`, `federal`, `own-source`, `other-entity`, `investment`, `deferred-capital-amortization`, `other`). |

**Method.** `scripts/statement_text.py` fetches the PDF and keeps its text page by page (the PDF is then
deleted). `scripts/transcribe_statement.py` reads the statement-of-operations page, takes the
current-year column, and writes the CSV only when the revenue lines add to the printed revenue total,
the expense lines to the printed expense total, and revenue less expense to the printed result. Every
page was also read in full, and the current-year column checked. Pages with no text layer were read
from the page image (`scripts/record_statement.py`, same checks); for those, each figure was also
checked against the comparative column of the next year's statement where one is transcribed. The
categories are this site's grouping; the statement's own label is kept beside every line. Where a line
mixes sources (UBC's "Government grants and contributions"; BCNET's grants), it stays `other`, with a
note.

**Done: 63 statements, current five years (2021-22 to 2025-26).**

| Body | Years |
|---|---|
| Fraser Health, Interior Health, Island Health, Northern Health, Provincial Health Services Authority, Vancouver Coastal Health | all five |
| BCNET | all five |
| UBC, University of Victoria, UNBC, BCIT, Justice Institute of BC | all five |
| Simon Fraser University | 2022-23, 2024-25, 2025-26 |

Read from page images (no text layer): Northern Health 2021-22 and 2023-24, Interior Health 2022-23
and 2023-24, BCNET 2023-24. UNBC 2025-26: the published PDF prints four revenue figures with no label;
the labels in [brackets] were supplied from the 2024-25 statement, where the same figures (the 2025
comparatives) carry them. The note says so.

**Open.**
- Simon Fraser University 2021-22 and 2023-24: the page's lines do not add to its printed total as
  read (a footnote mark is read as a figure); not transcribed.
- First Nations Health Authority and the Nisga'a Valley Health Authority; the other 19 universities and
  colleges; the larger Crowns (BC Housing, BC Transit, Community Living BC, TI Corp, BCTFA and others).
- Restatements: a later statement's comparative column can restate a year (BCNET 2023-24, noted; PS 3280
  adoption in 2022-23). Each year shows its own statement as first published.
- Expense by object (the notes) is not transcribed.

## C. Estimates against actual, by ministry and vote

**Source.** The Public Accounts' *Consolidated Revenue Fund Supplementary Schedules*, "Schedule of Voted
Appropriations by Ministry" (`pa-<yyyy-yy>-crf-supplementary-schedules.pdf`), 2010-11 to 2025-26: per vote
and per ministry or office that accessed it, the Estimates as voted, other authorizations, total
appropriation, total actual expense and variance, in $ thousands. Cross-checked against the
*Supplement to the Estimates* CSVs (BC Data Catalogue, Treasury Board Staff), Budget 2013 to Budget 2026.

| File | What it is |
|---|---|
| `estimates/votes.csv` | 964 rows, 16 fiscal years, each with its PDF and printed page. |
| `estimates/vote-totals.csv` | The printed total of every vote more than one ministry accessed, and each year's "Total Voted Expense". |
| `estimates/checks.csv` | Every printed total against the sum of its rows: all exact. |
| `estimates/supplement.csv` | Each Budget's Supplement summed to ministry, sub-vote and voted/statutory, operating expense, first fiscal year. |
| `estimates/ids.csv` | Offices joined to atlas ids (Auditor General, Elections BC, the Legislative Assembly, the Premier's office …) and one printed typo. |

**Checks.** Each year's rows add exactly to the printed vote totals and to the Total Voted Expense. The
Supplement's voted operating expense equals the printed Estimates total exactly for 2013-14 (the June
2013 update), 2014-15 to 2016-17 and 2018-19 to 2025-26 (12 years). 2017-18 differs: the Budget was
updated in September 2017 and no catalogue file of that update's Supplement was found.

**Joining.** A ministry is joined to its atlas episode by its name, the one standing at the fiscal year's
end, else at its start. Every ministry row is joined except "Public Safety and Solicitor General" in
2015-16, where the atlas has no episode. Not joined (no atlas node): the Merit Commissioner, the
Environmental Appeal Board and Forest Appeals Commission, the Auditor General for Local Government, the
Electoral Boundaries Commission, the combined "Officers of the Legislature" vote (2019-20, 2020-21), and
the Province-wide votes (Management of Public Funds and Debt, Contingencies, Capital Funding, Tax
Transfers and others).

Reproduce:

    python3 -I research/finance/scripts/extract_voted_appropriations.py research/finance/cache/crf research/finance/estimates
    python3 -I research/finance/scripts/summarize_supplement.py research/finance/cache/supplement research/finance/estimates

The CRF PDFs are fetched to `cache/crf/` from
`https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/<yyyy-yy>/pa-<yyyy-yy>-crf-supplementary-schedules.pdf`.

**Open.** Votes only: statutory appropriations and special accounts are not in this schedule. Sub-vote
actuals (the ministry pages of the same PDF) are not extracted. 2009-10 and earlier are not read.

## On the card

- **Budget and actual** (ministries and offices): a year's votes, with estimates, appropriation, actual
  and variance; a vote shared after a reorganization shows only that ministry's row.
- **Revenue and expense**: two stacked bars, revenue coloured by category, expense by the statement's
  own lines, each line listed as printed with its unit and page.
- **From ministries**: a year's payments by ministry, with the note that these are cash payments to
  payees paid $25,000 or more and need not equal the revenue the body recognizes.
- Figures are never added across bodies: money moving between government bodies is counted by each.
