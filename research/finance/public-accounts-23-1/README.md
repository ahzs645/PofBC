# Public Accounts: financial statements of government organizations

Research, 27 November 2026. The research pass changed nothing under `src/` or `scripts/`; the same day the
missing bodies and the atlas's Money card were built from it (see "Built from this research" at the end).

The Province publishes the audited financial statements of the organizations in the government
reporting entity with each year's Public Accounts. The statements sit under
`…/public-accounts/<year>/sup-e/<slug>-fs-<year>.pdf`. Universities, colleges and school districts
are only linked from the list; their statements are hosted on ministry pages.

Section 23.1 of the Budget Transparency and Accountability Act is the **accounting basis** the
statements are prepared on. It is not what puts a body on the list. All three statements read for
the worked example say so:
- BCNET's management report and BDO's audit opinion: "in accordance with the accounting
  requirements of Section 23.1 of the Budget Transparency and Accountability Act";
- the audit opinions for Northern Health and CNC: "the financial reporting provisions of Section 23.1".

The list itself is the government reporting entity: the index page calls the statements those "of
all public sector organizations and agencies that are included in the government reporting entity
for the past fiscal year".

## Files

| File | What it is |
|---|---|
| `inventory.csv` | One row per organization and fiscal year: 1,797 rows, 143 organizations, FY 1999-2000 to 2025-26. 31 rows were added from Wayback (`found_via` = `wayback`); see "Gaps closed" below. |
| `holes.csv` | The 58 single-year holes, each with what the year's index page shows and any archived copy. |
| `pre-1999.csv` | The scanned Public Accounts volumes before FY 1999-2000, with links and sizes. Not transcribed. |
| `post-secondary-statements.csv` | The ministry's own list of university, college and institute statements: 300 PDFs (25 institutions × 2014-15 to 2025-26). It fills the years when the Public Accounts only link to that page. |
| `crosswalk.csv` | Each organization matched to atlas IDs, related-body IDs and identity-register IDs. |
| `missing.csv` | The 55 organizations the site does not have as a node, with a recommendation for each. |
| `proposal.md` | Part 3: a "where the money goes" design, sources, data model, risks and a worked example. |
| `sources/archive-search-hits.jsonl` | All 1,549 results of the gov.bc.ca Public Accounts archive search, as harvested. |
| `sources/index-page-links.jsonl` | Links parsed from the live index page and 21 Wayback captures. |
| `sources/site-match-candidates.json` | The fuzzy-match candidates behind `crosswalk.csv`. |
| `scripts/` | The parsers and builders (Python, standard library only). See "Reproducing" below. |

### `inventory.csv` columns

`fiscal_year` (e.g. `2024-25`), `fy_end` (the 31 March that ends the Province's fiscal year; the
statement's own year end can differ, see proposal.md), `organization` (the name as published),
`org_key` (one key across renames, e.g. `legal-aid-bc` covers Legal Services Society),
`file_slug`, `sector` (the index-page heading, or the archive's "Organization Type" mapped to the
same headings), `reporting_basis` (taxpayer-supported, consolidated / self-supported GBE, modified
equity), `hosted` (sup-e PDF / ministry page), `document_url`, `found_via` (archive-search,
index-page, both, or wayback), `index_capture` (the index page or Wayback capture used), `name_source`,
`url_status`, `note` (rename notes).

## How each year was found

1. **Live index page** (FY 2025-26):
   <https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/financial-statements>,
   fetched 27 Nov 2026 ("last updated November 23, 2026"). It lists organizations by sector heading:
   Health, Education, Natural resources and economic development, Transportation, Protection of persons and
   property, Social services and Other. These are under "Taxpayer-Supported Crown Corporations & Agencies
   (Government Organizations) Recorded on a Consolidated Basis". A separate list holds "Self-Supported
   Crown Corporations & Agencies (Government Business Enterprises) Recorded on a Modified Equity Basis".
   The page has a "Consolidated Revenue Fund" heading with no entries under it.
2. **Wayback captures of the same page**: one capture per fiscal year for FY 2017-18, 2018-19,
   2019-20, 2020-21, 2022-23, 2023-24 and 2024-25. The latest capture for each year is used. The capture
   timestamps are in `index_capture`.
3. **The Public Accounts archive search** is the main source for every year. It is linked from the index
   page as "Public Accounts Archive: Government Organizations & Enterprises":
   `https://www2.gov.bc.ca/gov/search?q=financial+statements%2Binmeta%3AfinPA_infoSchd%3D5.+Crowns+%26+Agencies+Financial+Statements&id=4DE45087F6C34BEC999322346A28BDDC&tab=1&page=N`.
   The results are server-rendered in the page's `__NEXT_DATA__`, 10 per page. All 155 pages gave
   1,549 unique PDFs with "Fiscal Year" and "Organization Type" for FY 1999-2000 to 2025-26.
4. **Pre-2000** documents are outside this source. The archive page sends older years to the
   [Legislative Library](http://www.llbc.leg.bc.ca/public/pubdocs/bcdocs2015_2/164239/index.htm) and the
   [Internet Archive](https://archive.org/search.php?query=British+Columbia+Public+Accounts). They are
   scanned whole volumes, not per-organization files. `pre-1999.csv` lists them; see "Gaps closed" below.

Names come from the index pages where a capture exists (644 rows). Otherwise they come from the
same file slug's name on another year's index page (709 rows). For the rest the name was read from
the statement's title page (269 rows), or expanded from the file slug where the scan has no text
layer (144 rows). `name_source` records which method was used for each row.

## Counts per year

| Fiscal year | sup-e statements | Listed, hosted elsewhere | Organizations | Found via |
|---|---|---|---|---|
| 1999-00 | 54 | – | 54 | archive |
| 2000-01 | 27 | – | 27 | archive |
| 2001-02 | 28 | – | 28 | archive |
| 2002-03 | 22 | – | 22 | archive |
| 2003-04 | 44 | – | 44 | archive |
| 2004-05 | 63 | – | 63 | archive |
| 2005-06 | 71 | – | 70 | archive |
| 2006-07 | 53 | – | 53 | archive |
| 2007-08 | 73 | – | 73 | archive |
| 2008-09 | 73 | – | 73 | archive |
| 2009-10 | 76 | – | 76 | archive |
| 2010-11 | 56 | – | 56 | archive |
| 2011-12 | 86 | – | 86 | archive |
| 2012-13 | 86 | – | 86 | archive |
| 2013-14 | 84 | – | 84 | archive |
| 2014-15 | 56 | – | 56 | archive |
| 2015-16 | 57 | – | 57 | archive |
| 2016-17 | 55 | – | 55 | archive |
| 2017-18 | 56 | 26 | 82 | archive + index |
| 2018-19 | 54 | 26 | 80 | archive + index |
| 2019-20 | 53 | 26 | 78 | archive + index |
| 2020-21 | 57 | 26 | 82 | archive + index |
| 2021-22 | 57 | – | 57 | archive only (no index capture) |
| 2022-23 | 54 | 26 | 80 | archive + index |
| 2023-24 | 55 | 26 | 81 | archive + index |
| 2024-25 | 54 | 26 | 80 | archive + index |
| 2025-26 | 54 | 26 | 80 | archive + index |

The "hosted elsewhere" rows are 25 post-secondary institutions plus one "School Districts" link.
Health authorities appear from 2004-05. Universities and colleges were filed in sup-e from 2005-06
to 2013-14 (JIBC and NVIT to 2014-15). After that the ministry page holds their statements (see
`post-secondary-statements.csv`).

## Coverage gaps and anomalies

- **No index page for FY 2021-22, nor for 2016-17 and earlier.** Wayback has no capture of the index
  between August 2022 (still 2020-21) and September 2023 (2022-23). Those years rely on the archive
  alone, so the post-secondary and school-district links are not recorded for them. Their
  statements are in `post-secondary-statements.csv` from 2014-15 on.
- **Index links the archive lacks** (all HEAD-checked 200 on 27 Nov 2026): InBC and Infrastructure
  BC 2020-21 (the latter under slug `infrastructure-bc-inc`); BCCIE and BC Family Maintenance Agency
  2024-25; and BC Assessment, BCCIE, BC Energy Regulator, BC Family Maintenance Agency and BCFSA
  2025-26. The archive search is a few weeks behind the index for the newest year.
- **Archive rows the index lacks:** Provincial Rental Housing Corporation 2023-24 is in the archive
  but not on the December 2024 capture of the index.
- **Single-year holes**: 58 cases where an organization appears in the years before and after
  but not that year. All 58 sup-e URLs return 404. The second pass (below) explains each one in
  `holes.csv`: 31 were on the ministry's page and are now in the inventory, and most of the rest are
  listed on that year's index with no link. The
  largest are 2010-11, when 28 bodies are missing (nearly every university and college, plus BC
  Securities Commission, BC Enterprise Corporation and Mount St. Mary), and 2006-07, with 9. The
  full list can be rebuilt from `inventory.csv`.
- **A broken link on an older capture.** The September 2023 capture linked
  `legal-services-society-fs-2022-23.pdf`, which returns 404. The later capture and the archive use
  `legal-aid-bc-fs-2022-23.pdf`.
- **Scans without text.** Many 1999-2010 PDFs are image-only, so 144 names come from file slugs
  and are marked as such.
- **Renames** are joined by `org_key` and explained in `note`. Each was checked against a statement
  or the atlas. For example, InBC's 2020-21 statements, note 1: "created on September 17, 2020 by
  renaming the BC Immigrant Investment Fund Ltd.". Infrastructure BC's 2020-21 statements read
  "(formerly Partnerships British Columbia Inc.)".

## Matching to the site (Part 2)

The atlas and register were read with `node --input-type=module` on 27 Nov 2026:

| Data | Count |
|---|---|
| `HISTORICAL_BODIES` | 245 |
| `CURRENT_BODIES` | 51 |
| `SUB_AGENCIES` | 271 |
| `LOCAL_BODIES` | 68 |
| `RELATED_BODIES` | 178 |
| `buildSearchIndex()` | 2,108 |
| `IDENTITY_COVERAGE` | 863 |

Other agents are editing `src/` right now, so these counts may move. Matching used exact and
normalized names first ("British Columbia" equated with "BC", and corporate suffixes stripped),
then a difflib ratio above 0.86. All 143 organizations were then reviewed by hand. The `src/` tree
was also searched for each unmatched name, to find bodies the site mentions without giving them a
node.

| Result | Organizations |
|---|---|
| Matched to an atlas, related-body or register entry | 88 (2 under another name: Victoria Line → `bc-steamship-company`, First Peoples' Heritage… Council → `first-peoples-cultural-council`) |
| Matched, but only as related bodies or register subjects, with no atlas node | 26 (all 25 public post-secondary institutions, plus the Nechako-Kitamaat Development Fund Society); school districts are related bodies |
| Missing: mentioned in `src/` text or research data only | 11 |
| Missing: not on the site at all | 44 |

`missing.csv` recommends:

| Recommendation | Count |
|---|---|
| Add as atlas body | 22 (20 at first; two changed, see below) |
| Add as related body | 25 |
| Out of scope | 8 |

The bodies most worth adding:

- **The five Public Sector Employers Act employers' associations**: BCPSEA, CSSEA, HEABC, PSEA and
  CCEA. Each has been consolidated every year since 2010-11, and each is a statutory body.
- **Organized Crime Agency of BC**, listed every year 1999 to 2026.
- **Creston Valley Wildlife Management Authority.** The atlas already tracks its Act's ministerial
  moves.
- **Private Career Training Institutions Agency** and its predecessor, the **Private Post-Secondary
  Education Commission**.
- **Vancouver Convention Centre Expansion Project Ltd.**, which the atlas describes in PavCo's text
  but has no node to link.
- **BCNET**, as a related body of the post-secondary family. It is a members' society, not a Crown.
- **The affiliated and denominational hospital societies** (Providence, Mount St. Mary, Louis Brier,
  Menno, St. Michael's, St. Joseph's, and the three United Church hospitals), as related bodies
  of the health family. The salaries index already holds Providence disclosures.

## Reproducing

The working files were built in a scratch directory. Each step can be rerun from these scripts:

1. Fetch the index page and Wayback captures, then run `scripts/parse_index.py <html…>`, which
   writes JSON lines.
2. Fetch the 155 archive search pages, then run `scripts/hits.py page_*.html`, which writes JSON
   lines (saved as `sources/archive-search-hits.jsonl`).
3. Run `scripts/build_inventory.py <dir with search/hits.jsonl and parsed.jsonl> inventory.csv`.
   It uses `scripts/names.py` for the manual names and renames.
4. From the repository root, run
   `node research/finance/public-accounts-23-1/scripts/dump_site.mjs site.json`. This dumps the
   site data to `site.json`.
5. Run `scripts/match.py inventory.csv site.json matches.json`, then
   `scripts/build_missing.py matches.json .`, which uses the manual decisions in
   `scripts/decisions.py`.

Downloaded PDFs were not committed. Every URL is in the CSVs.

## Built from this research (27 November 2026)

### Bodies added to the site

Every body was re-checked against its own statements, the statute that made or ended it, and BC
Registries ([OrgBook BC](https://orgbook.gov.bc.ca/)) for societies and companies. Dates are given only
where one of those says them.

- **Atlas bodies (22)**, at their source in `research/history/bodies-public-accounts-2026-11-27.json`
  (built into `src/government/historyData.js` by `npm run build:government`): the five Public Sector
  Employers Act associations (BCPSEA, CSSEA, HEABC, PSEA, CCEA), Organized Crime Agency of BC, Creston
  Valley Wildlife Management Authority, BC Racing Commission, Okanagan Valley Tree Fruit Authority,
  Forensic Psychiatric Services Commission, BC Health Research Foundation, Private Post-Secondary
  Education Commission → Private Career Training Institutions Agency, Leading Edge Endowment Fund, Fraser
  Region Interim Aboriginal Authority, Vancouver Island Aboriginal Transition Authority, B.C. Community
  Financial Services Corporation, Fisheries Renewal BC, Rapid Transit Project 2000 Ltd., Vancouver
  Convention Centre Expansion Project Ltd. (→ PavCo, 1 April 2008), Discovery Enterprises Inc. and BCIF
  Management Ltd. Their instrument decisions are in `research/legislation/instrument-decisions.json`.
- **Related bodies (25)**, in `src/government/publicAccountsBodies.js`: the affiliated and
  denominational hospital societies (Providence, Mount St. Mary, Louis Brier, Menno, St. Michael's,
  St. Joseph's, Bella Coola, RW Large, Wrinch), Nisga'a Valley Health Authority, Canadian Blood
  Services, BC Clinical and Support Services Society, BC Health Services Purchasing Organization, BC
  Health Care OHS Society, BC Academic Health Council, B.C. Health Care Risk Management Society, Health
  Facilities Association of BC, BCNET, Trades Training Consortium, Institute of Indigenous Government,
  Real Estate Foundation, Vancouver Trade and Convention Centre Authority, PNE, B.C. Festival of the
  Arts Society and the BC Society for the Distribution of Gaming Revenue to Charities.
- **Recommendations changed:** Discovery Enterprises Inc. and BCIF Management Ltd. became atlas bodies:
  their statements show both wholly owned by the Province (Discovery Enterprises from 1 April 1994).
  Two reasons were corrected without changing the recommendation: the Vancouver Trade and Convention
  Centre *Authority* was the 1998 federal not-for-profit set up to build an expanded centre (cancelled
  5 October 1999), not the original centre's operator; the Health Facilities Association of BC was a
  conduit for capital contributions, not HEABC's predecessor. `missing.csv` and `scripts/decisions.py`
  carry the corrections.
- **Left out (8), as recommended:** the five numbered companies (552513, 577315, 580440, 632121, 634349
  British Columbia Ltd.), the Power Project Planning Joint Venture, PCTIA's Student Training Completion
  Fund and the Science and Community Environmental Knowledge Fund.
- Twenty public universities and colleges have statements here but no site record yet (only UBC, SFU,
  UVic, UNBC, BCIT and JIBC do), so their statements are not shown anywhere.

### The Adjusted Net Income table (stage 2)

`scripts/extract_adjusted_net_income.py` reads the Supplementary Information table from each year's
PDF (cached under `cache/`, which is not committed) and writes:

| File | What it is |
|---|---|
| `adjusted-net-income.csv` | 1,557 rows, every year from 1999-00 to 2025-26 (27 years), 6,084 figures, in $ millions as printed, each with its source PDF, PDF page and printed page where read. Blank cells stay blank. |
| `adjusted-net-income-columns.csv` | Each year's column headings. The fifth column is "Equity Adjustments" to 2003-04, "Contributions Paid to the Consolidated Revenue Fund" 2004-05 to 2011-12, "Dividends" from 2012-13; the fourth is "Policy Adjustments" to 2006-07. |
| `adjusted-net-income-footnotes.csv` | The footnotes, by year. A row's `footnotes` gives its marks (`cN:M` for a mark on column N). |
| `adjusted-net-income-checks.csv` | All 755 printed subtotals against the sum of the rows above them: all within rounding. |

The table has no prior-year or restated columns; footnotes that qualify a year (stub periods, a
reclassification, a rename) travel with the rows. SUCH sector rows stay sector totals.

### The Money card

`scripts/build-finance.mjs` (`npm run build:finance`, `npm run check:finance`) joins the statements and
table rows to site ids through `crosswalk.csv`, corrected and extended by `site-ids.csv`, and writes
`src/government/financeIndex.js` and `public/finance/<id>.json` (120 bodies). The card is
`src/government/Money.jsx`, shown in the atlas panel and on related-body pages. Tests:
`scripts/finance.test.mjs`.

## Gaps closed (second pass, 27 November 2026)

### The 58 single-year holes

The www2 sup-e URLs have no Wayback captures. Before about 2014 the statements were on
`www.fin.gov.bc.ca/ocg/pa/<yy_yy>/Sup E/`, so that path was searched instead. The Internet Archive's
CDX server was down; the Library and Archives Canada web archive's CDX endpoint
(`https://bac-lac.wayback.archive-it.org/web/timemap/cdx?url=www.fin.gov.bc.ca/ocg/pa/&matchType=prefix`)
returned the same index. The yearly Sup E index pages (`e1e.htm`) are captured for 2002-03 to 2015-16,
except 2011-12 and 2012-13. Each hole was then read against that year's index page.

| Finding | Holes | What it means |
|---|---|---|
| Found on Wayback (ministry page) | 31 | The index linked the Ministry of Advanced Education's page (`aved.gov.bc.ca/gre/financial.htm`), not a sup-e PDF. The ministry's PDFs are captured: 6 in 2006-07, VIU in 2008-09 and 24 universities, colleges and institutes in 2010-11. Added to `inventory.csv` with `found_via` = `wayback`. |
| Listed, no statement linked | 16 | The name is on the index without a link, so no statement was published with the Public Accounts that year. For example: BC Securities Commission and Mount St. Mary 2010-11 and 2019-20; BC Enterprise Corporation and Leading Edge Endowment Fund 2010-11; Bella Coola, Menno and R.W. Large 2006-07. Provincial Rental Housing Corporation 2002-03 carries footnote 4: it changed sectors that year. |
| Linked to an outside report | 1 | First Peoples' Heritage, Language and Culture Council 2002-03 links an annual report on gov.bc.ca. Its only capture is from December 2006, so it may be a later report. Not added. |
| Linked, not captured | 1 | Canadian Blood Services 2014-15. |
| Not listed | 1 | Canadian Blood Services 2022-23 is not on the June 2024 capture of the index. |
| No index capture | 8 | 2000-01 (5), 2001-02 (1), 2012-13 (Douglas College) and 2016-17 (BC Enterprise Corporation). |

Other things seen on the way:

- The 2010-11 index still lists the Institute of Indigenous Government, with a link to the ministry
  page. That page's 2010/11 list does not include it.
- The NVIT file for 2008-09 in the archive (`nicola-valley-institute-of-technology-fs-2008-09.pdf`)
  is byte-identical to the 2007-08 file. It is a 2008 scan of the 2007-08 statements.

### Years before 1999

`pre-1999.csv` has 171 rows. It records links and sizes. No volume was downloaded.

- **Legislative Library of BC.** The library page the Province still links
  (`www.llbc.leg.bc.ca/public/pubdocs/bcdocs2015_2/164239/index.htm`) and its files return 404 as of
  27 November 2026. The list comes from its
  [February 2020 capture](https://web.archive.org/web/20200220102039/http://www.llbc.leg.bc.ca:80/public/pubdocs/bcdocs2015_2/164239/index.htm):
  Public Accounts for every year from 1880-81 to 1950-51, except 1934-35 (listed with no link), and
  the earlier statements of expenditure (1874-75 to 1881). Wayback holds only one of the PDFs, the
  1939-40 volume (260 MB), under a later file name.
- **Internet Archive.** 85 volumes from 1917-18 to 1998-99, with the PDF link and size of each. Most
  were scanned from the University of Alberta Libraries. From 1978-79 the years come in two or three
  volumes. Volume 3, "Trust funds, Crown corporations and agencies", holds the organizations'
  statements from 1980-81 to 1988-89 (Volume 2 in 1989-90). Some years have two scans.
- **fin.gov.bc.ca.** The 1997-98 Volume 3 Section E is captured as HTML, one set of pages per
  organization (586 pages, captured 2001). The 1998-99 contents page is captured, but its Sup-E
  statements are not.
- **Not covered:** 1951-52 to 1959-60. UBC Open Collections' BC Sessional Papers hold the Public
  Accounts as tabled; the 1953-54 and 1954-55 volumes were found and are listed. The rest of that
  collection was not inventoried.

### St. Michael's Centre

Two societies run St. Michael's Centre in Burnaby and file one set of combined statements. Note 1 of
the [2024-25 statements](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/st-michaels-centre-fs-2024-25.pdf):
"The St. Michael's Centre Hospital Society and St. Michael's Centre Intermediate Care Society operate
a hospice and an extended care facility located in Burnaby under the name St. Michael's Centre". Both
are registered under the Societies Act: [S0014480](https://orgbook.gov.bc.ca/entity/S0014480) and
[S0014481](https://orgbook.gov.bc.ca/entity/S0014481), both registered on 16 February 1979. The
Hospital Society is a registered charity. Fraser Health is the principal funding agency. The record in
`src/government/publicAccountsBodies.js` now names both.

### The two interim Aboriginal authorities

[B.C. Reg. 58/2009](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/58_2009_pit),
deposited 4 March 2009 and effective 31 March 2009, transferred the cash, receivables, capital assets,
net assets, records and liabilities of the Fraser Region Interim Aboriginal Authority and the Vancouver
Island Aboriginal Transition Authority to the government. Its note says it repeals
[B.C. Reg. 277/2007](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/277_2007_pit),
which had established both. Both atlas records now end on 31 March 2009. BC Laws' point-in-time page
for B.C. Reg. 277/2007 also says it was repealed by B.C. Reg. 147/2011, effective 25 July 2011. That
text was not found, so the 2009 repeal stands.

### The Institute of Indigenous Government and NVIT

NVIT's [2007-08 statements](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2007-08/sup-e/nicola-valley-institute-of-technology-fs-2007-08.pdf)
are a scan without a text layer, so they were read by eye. Note 1: "The Institute commenced operations
at its Vancouver campus on July 1, 2007". Note 12, Subsequent events: "NVIT is currently finalizing an
agreement to transfer the assets of the Institute of Indigenous Government ("IIG"), now operating as
the Vancouver campus of NVIT, which is expected to complete in 2009." So IIG's operations became NVIT
Vancouver on 1 July 2007. When the asset transfer closed, and whether IIG was formally dissolved or
de-designated, were not found. The record in `src/government/publicAccountsBodies.js` says so.
