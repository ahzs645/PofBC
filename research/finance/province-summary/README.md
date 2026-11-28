# Province of British Columbia: revenue by source and expense by function

Research, 27 November 2026. Source for the government view's Budget mode
(`?view=government&mode=budget&fy=2024-25`).

Each year's Public Accounts include the Province's **Summary Financial Statements**. Their
**Consolidated Statement of Operations** (titled "Statement of Operations" to 2004-05) gives total
revenue by source and total expense by function, in $ millions. These are consolidated figures for the
whole government reporting entity, after inter-entity eliminations, in nominal dollars.

    https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/
        public-accounts/<yyyy-yy>/pa-<yyyy-yy>-summary-financial-statements.pdf

All 27 fiscal years from 1999-00 to 2025-26 were downloaded on 27 November 2026 (HTTP 200 for each) and
all have a text layer. No year is missing. Earlier years are outside this URL pattern; the Public
Accounts archive sends them to the Legislative Library's scanned volumes, and they were not read.

## Files

| File | What it is |
|---|---|
| `extract_statement_of_operations.py` | The extractor: standard-library Python plus `pdftotext` (poppler). `--fetch` downloads any PDF missing from `cache/`. |
| `statement-of-operations.csv` | 572 lines, every line of the statement as printed for each year: revenue items and total, expense items and total, the items between the totals and the result (forecast allowance, pension settlement, restructuring), and each "Surplus (deficit)" line. |
| `statement-of-operations-footnotes.csv` | The statement's own footnotes (1999-00 only). |
| `cache/` | The PDFs. Not committed (`.gitignore`); they can be fetched again with `--fetch`. |

### `statement-of-operations.csv` columns

`fiscal_year`, `fy_end`, `section` (`revenue`, `expense`, `result`), `line` (order on the page), `kind`
(`item`, `total`, `adjustment`, `result`), `heading` (the printed label without note references or
footnote marks), `label_as_printed`, `footnotes`, `estimate`, `actual`, `prior_year` (the previous
year as restated in this year's statement), `unit`, `source_url`, `pdf_page`, `printed_page`,
`table_title`.

The 1999-00 statement has two columns (actual and prior year). Every later year has three: Estimates,
actual and prior year. Figures are placed in columns by their printed position, not by count, so a
line printed only in the Estimates column (the forecast allowance) stays there.

## The headings

The Province's own headings are kept, as printed each year:

- Revenue: Taxation; Contributions from the federal government; Fees and licences ("Fees and licenses"
  2013-14 to 2019-20); Natural resources; Net earnings of self-supported Crown corporations and
  agencies; Investment earnings (to 2004-05) / Investment income; Miscellaneous; Recoveries (1999-00 and
  2000-01 only, after which recoveries were netted against expense; the 2001-02 statement restates
  2000-01 without the line).
- Expense: Health; Education; Social services; Protection of persons and property; Transportation;
  Natural resources and economic development; General government; Interest; Other. The statement
  says "Interest". "Debt servicing" is the heading of the sector supplementary statement, not of this
  statement, and is not used.

`scripts/build-budget.mjs` gives each heading a stable key (`taxation`, `health` …) so a line keeps its
colour across years; the heading shown is always the printed one.

## Checks

`npm run check:budget` fails unless, for every year and every printed column:

- the revenue lines add exactly to the revenue total, and the expense lines to the expense total;
- revenue less expense, plus or minus each line between them ("Less:" lines are taken away), equals
  each "Surplus (deficit)" line printed below.

All 27 years reconcile exactly, with no rounding allowance needed: the Province rounds its lines so
that the printed totals add.

Two cross-checks are in `scripts/budget.test.mjs`: spot figures read by hand from the PDFs, and the
"Net earnings of self-supported Crown corporations and agencies" line against the Supplementary
Information table's "Net impact of self-supported Crown corporations and agencies" (equal in every
year from 2018-19; before that the two publications differ by consolidation adjustments, most in
2017-18).

## Restatements

190 lines (items and totals) differ between a year's own statement and the next year's prior-year
column. The Budget mode shows each year as first published and gives the restated figure beside it.

## Bodies under each function

The bodies come from `../public-accounts-23-1/`:

- Crown corporations and agencies: their rows in `adjusted-net-income.csv` (gross, before
  eliminations), placed under a function by the sector heading the Public Accounts' financial
  statements list gives them (`inventory.csv`, `sector`). Three rows have no sector in that list:
  Vancouver Trade and Convention Centre Authority (2000-01), Shared Services Organization
  Administration Society (2009-10) and Transportation Investment Corporation (2017-18). They are shown
  under "Not under a sector heading".
- SUCH sector rows: School Districts, Universities, and Colleges and Institutes under Education; Health
  Authorities and Hospital Societies under Health (from 2004-05, when the table first prints them).
- The bodies counted in those rows: Health and Education organizations with a statement that year and
  no row of their own (`inventory.csv`, `post-secondary-statements.csv`). The table gives no figure for
  each, so none is shown; each links to its page where the site has one.
- Self-supported Crown corporations: under "Net earnings of self-supported Crown corporations and
  agencies", with their net income.

Site ids come from `public/finance/<id>.json` (written by `scripts/build-finance.mjs`), then an exact
name match against the atlas and related bodies. Run `npm run build:finance` before
`npm run build:budget` when either changes.

## Reproducing

    python3 -I research/finance/province-summary/extract_statement_of_operations.py --fetch
    npm run build:budget
    npm run check:budget

## Open

- Revenue detail (Note: taxation by tax, natural resources by resource) and expense by function in
  more detail are in the notes of the same PDFs; they were not extracted.
- Years before 1999-00.
- Ministry transfers to each body, which would let a flow go from function to body without double
  counting, need the elimination rules in `../public-accounts-23-1/proposal.md`.
