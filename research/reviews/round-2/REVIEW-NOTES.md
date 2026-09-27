# PofBC research round 2 — partial tranche

**Research date:** 26 September 2026. **Basis:** the 13 uploaded snapshot files.

## Scope and counts

This package supplies 16 new claim-bearing sub-agency records and additive follow-up on 2 existing records (WorkBC and Powertech Labs). It does not complete the 213-record round-two brief. The full merged file contains 42 records and the original 3 gone bodies. Of the original 213 unreviewed IDs, 197 receive no new research record in this tranche.

The 16 new records include 7 with a sourced establishment value: 6 previously undated in the template and 1 month-level refinement (Mental Health Review Board). The other 9 preserve observations, operational/name events, or unresolved establishment claims instead of manufacturing a start date. WorkBC remains null until an identity-scope decision is accepted.

Twenty new source-catalogue entries are supplied, for 54 total. These counts describe the JSON package only, not the atlas’s rendered historical coverage.

## Decisions and conflicts

**WorkBC.** The official announcement dates the broad WorkBC strategy and website launch to 27 April 2007. A 2008 official backgrounder independently confirms that website-launch date. The 2 April 2012 centres launch remains a separate operational event. The current template mixes the broader website/brand and centres; established stays null until the record’s scope is approved. A 2007 start is proposed for the broader identity, not silently applied.

**Environmental Appeal Board.** The held start is 1981. The Board’s practice manual explicitly says it was established in 1982; its homepage instead names the Environment Management Act (1981). The year of a statute is not necessarily the date of the body. The 1982 claim is recorded, the held 1981 is retained as inherited data, and established is null pending reconciliation. The original commencement instrument still needs checking.

**Powertech Labs.** The held 1988 year and the prior 1989 service-history claim are not reconciled by the current ownership page. The only new exported claim is an ownership observation. No incorporation year is inferred from rounded anniversary wording.

**BC Timber Sales.** The uploaded editorial decision for 20 June 2003 is unchanged. Its competing research claims are retained. The raw research status still says requires_reconciliation; the existing separate decision is what selects the display date.

## Important modelling limits

An observation proves the named body or parent at the stated observation precision; it does not establish continuous existence or placement before/after that observation. A service plan’s three-year planning horizon is not treated as a three-year organizational interval. Existing held events are not represented as newly checked claims.

Renames stay on the same ID. The Industry Training Appeal Board / Skilled Trades BC Appeal Board continuation and the Oil and Gas Appeal Tribunal / Energy Resource Appeal Tribunal continuation do not create extra gone nodes. No new gone bodies are added. The precise later ERAT rename date remains unverified.

The existing parent schema uses ministry_as_printed even for a corporate parent such as BC Hydro. This shape is retained rather than inventing an untested field. Corporate-parent name matching and all graph behaviour still need repository-side tests.

## Responsibility gaps

No new directly stated responsible-ministry interval is exported. The three targeted BC Archives authority pages for the Workmen’s Compensation Board, Civil Service Commission and Emergency Health Services Commission could not be fetched. This is not evidence that the relationships were absent.

The 2003 Health Services plan directly names BC Ambulance Service. It does not, in the inspected passage, name the Emergency Health Services Commission. The operating-service observation is held separately until a sourced identity link and temporal scope are established. responsible-4.json therefore contains an empty records dictionary and explanatory gaps; it is not evidence that the 602 body-year gap has shrunk.

## Record-by-record handback

### WorkBC (`workbc`)

Existing record updated. Establishment: **unresolved / null**. Status: `requires_reconciliation`.

The verified April 2, 2012 event is the Employment Program of BC / WorkBC centres launch. The template also covers the broader WorkBC website and brand. Their identity and earlier history are unresolved; a centres launch is not silently promoted to the birth of everything called WorkBC. Round 2 locates the original WorkBC strategy and website launch on 2007-04-27, independently confirmed in a 2008 backgrounder. The 2012 centres event is retained. established remains null pending an editorial decision on whether this record represents the broad WorkBC identity or specifically the service-centre network. No parent interval is inferred from the minister announcing a cross-government initiative.

Source for `first_observed`: [r2-workbc-launch-2007](https://archive.news.gov.bc.ca/releases/news_releases_2005-2009/2007ECD0021-000529.htm) — Dateline and opening paragraph.

Source for `research_events`: [r2-workbc-launch-2007](https://archive.news.gov.bc.ca/releases/news_releases_2005-2009/2007ECD0021-000529.htm) — Dateline, opening paragraph, and website-unveiling paragraph.

Source for `research_events`: [r2-workbc-achievements-2008](https://archive.news.gov.bc.ca/releases/news_releases_2005-2009/2008ecd0023-000692-attachment1.htm) — Strategic area 4; WorkBC.ca launch sentence.

Source for `date_claims`: [r2-workbc-launch-2007](https://archive.news.gov.bc.ca/releases/news_releases_2005-2009/2007ECD0021-000529.htm) — Opening paragraph and website-unveiling paragraph.

### Columbia Hydro Constructors Ltd. (`columbia-hydro-constructors`)

New reviewed record. Establishment: **1962**. Status: `documented_partial`.

The corporate parent explicitly states formation in 1962. No incorporation instrument, exact day, earlier names, or continuous ownership interval was established.

Source for `established`: [r2-hydro-subsidiaries](https://www.bchydro.com/toolbar/about/who_we_are/subsidiaries.html) — Columbia Hydro Constructors Ltd. section, opening sentence.

### Powertech Labs Inc. (`powertech-labs`)

Existing record updated. Establishment: **unresolved / null**. Status: `requires_reconciliation`.

The uploaded founding year 1988 was not independently substantiated in this pass. BC Hydro describes service delivery since 1989, which may differ from incorporation. The held 1988 value is preserved, and neither year is silently treated as proof of the other event. Round 2 rechecks current ownership but finds no incorporation evidence resolving 1988 versus the existing 1989 service-history statement. Undated descriptions of 30 or 35 years of experience are not converted into a founding year.

Source for `parents`: [r2-hydro-subsidiaries](https://www.bchydro.com/toolbar/about/who_we_are/subsidiaries.html) — Powertech Labs section, opening sentence.

### Energy Resource Appeal Tribunal (`energy-resource-appeal-tribunal`)

New reviewed record. Establishment: **2010-10-04**. Status: `documented_partial`.

A continuing tribunal under a changed name, not two invented predecessor/successor bodies. The precise effective date of the later rename was not established in this pass. No ministry parent is inferred from the regulated industry or ministers receiving reports.

Source for `established`: [r2-ogat-first-report](https://www.bcerat.ca/app/uploads/sites/847/2020/07/OGAT_AR_2010_2013.pdf) — PDF page 10 / printed page 8, About the Tribunal.

Source for `legal_basis`: [r2-energy-resource-act](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/08036_01) — Section 19(1), continuation as Energy Resource Appeal Tribunal.

### Forest Appeals Commission (`forest-appeals-commission`)

New reviewed record. Establishment: **1995**. Status: `documented_partial`.

The report ties creation to the Forest Practices Code, effective 1995-06-15. Year-level establishment is retained; the exact statutory commencement is separately typed rather than overstating an independently verified section-specific start. Full parent and jurisdiction history remains incomplete.

Source for `established`: [r2-fac-report-2001](https://www.bcfac.ca/app/uploads/sites/837/2020/07/fac_ar01.pdf) — PDF page 6 / printed page 5, Introduction.

### Mental Health Review Board (`mental-health-review-board`)

New reviewed record. Establishment: **2005-04**. Status: `documented_partial`.

Refines the held 2005 year to April 2005. Earlier review-panel arrangements are not equated with this board. Exact day and administrative parent history remain unknown.

Source for `established`: [r2-mhrb-home](https://www.bcmhrb.ca/) — Welcome to the Mental Health Review Board, opening sentence.

Source for `legal_basis`: [r2-mhrb-home](https://www.bcmhrb.ca/) — Welcome, opening sentence.

### Environmental Appeal Board (`environmental-appeal-board`)

New reviewed record. Establishment: **unresolved / null**. Status: `requires_reconciliation`.

The held 1981 establishment year is not independently confirmed. The Board manual expressly states establishment in 1982; the homepage instead identifies the Environment Management Act (1981). An Act citation year is not a body commencement date. Both readings are preserved for editorial review; established is null here rather than silently replacing the held value.

Source for `legal_basis`: [r2-eab-manual](https://www.bceab.ca/uploads/2021/04/eab_proc_manual.pdf) — PDF page 8 / printed page 8, Introduction.

Source for `research_events`: [r2-eab-home](https://www.bceab.ca/) — Welcome, opening paragraph.

Source for `date_claims`: [r2-eab-manual](https://www.bceab.ca/uploads/2021/04/eab_proc_manual.pdf) — PDF page 8 / printed page 8, Introduction, first paragraph.

### Office of the Seniors Advocate (`office-of-the-seniors-advocate`)

New reviewed record. Establishment: **2014**. Status: `documented_partial`.

The office explicitly dates its creation to 2014. Royal Assent on 2013-03-14 and the first advocate taking up the role on 2014-03-31 are separate events, not substitutes for an unverified exact office-creation day. No ministry parent is inferred from annual-report delivery.

Source for `established`: [r2-osa-history](https://www.seniorsadvocatebc.ca/annual-report-of-the-office-of-the-seniors-advocate/) — Annual Report, opening paragraph.

Source for `legal_basis`: [r2-osa-act](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/13015_01) — Sections 2–5; section 12 (commencement by regulation).

Source for `research_events`: [r2-osa-act](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/13015_01) — Act heading and assent line.

Source for `research_events`: [r2-osa-appointment](https://archive.news.gov.bc.ca/releases/news_releases_2013-2017/2014HLTH0023-000333.htm) — Paragraph specifying when Isobel Mackenzie will take up the role.

### BC Bid (`bc-bid`)

New reviewed record. Establishment: **unresolved / null**. Status: `documented_partial`.

Hansard documents a functioning B.C. Bid website in 1996 and identifies B.C. Buy Smart as the earlier name. It does not date the original launch or the rename. This observation is not an establishment date and does not assert uninterrupted naming since 1996.

Source for `first_observed`: [r2-bcbid-hansard-1996](https://api.lims.leg.bc.ca/hdms/file/Debates/36th1st/19960730pm1-Hansard-v2n9.htm) — Printed page 1156; exchange between P. Reitsma and A. Petter on B.C. Buy Smart / B.C. Bid.

Source for `names`: [r2-bcbid-hansard-1996](https://api.lims.leg.bc.ca/hdms/file/Debates/36th1st/19960730pm1-Hansard-v2n9.htm) — Printed page 1156; response beginning The program is now known.

Source for `research_events`: [r2-bcbid-hansard-1996](https://api.lims.leg.bc.ca/hdms/file/Debates/36th1st/19960730pm1-Hansard-v2n9.htm) — Printed page 1156; B.C. Buy Smart exchange.

### Court Services Branch (`court-services-branch`)

New reviewed record. Establishment: **unresolved / null**. Status: `documented_partial`.

The 2003 service plan expressly names the Court Services Branch and places Court Services within the Ministry of Attorney General. This is a historical name and parent observation, not the founding year or proof of continuous placement throughout the three-year planning horizon.

Source for `first_observed`: [r2-ag-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/ag/ag.pdf) — PDF page 17 / printed page 11, Judiciary paragraph.

Source for `names`: [r2-ag-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/ag/ag.pdf) — PDF page 17 / printed page 11, Judiciary.

Source for `parents`: [r2-ag-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/ag/ag.pdf) — PDF pages 16–17 / printed pages 10–11, Core Business Areas and Judiciary.

### BC Corrections (`bc-corrections`)

New reviewed record. Establishment: **unresolved / null**. Status: `documented_partial`.

A named ministry unit is documented in the 2003 service plan. This supports a 2003 observation only; the establishment date and earlier/later transfers remain unverified. The plan horizon is not treated as a continuous parent interval. Earlier held events, where present, remain leads rather than newly verified dates.

Source for `first_observed`: [r2-pssg-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/pssg/pssg.pdf) — PDF page 13 / printed page 7, Core Business Areas — Corrections.

### BC Coroners Service (`bc-coroners-service`)

New reviewed record. Establishment: **unresolved / null**. Status: `documented_partial`.

A named ministry unit is documented in the 2003 service plan. This supports a 2003 observation only; the establishment date and earlier/later transfers remain unverified. The plan horizon is not treated as a continuous parent interval. Earlier held events, where present, remain leads rather than newly verified dates.

Source for `first_observed`: [r2-pssg-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/pssg/pssg.pdf) — PDF pages 13–14 / printed pages 7–8, Policing and Community Safety.

### Commercial Vehicle Safety and Enforcement (`commercial-vehicle-safety-and-enforcement`)

New reviewed record. Establishment: **unresolved / null**. Status: `documented_partial`.

A named ministry unit is documented in the 2003 service plan. This supports a 2003 observation only; the establishment date and earlier/later transfers remain unverified. The plan horizon is not treated as a continuous parent interval. Earlier held events, where present, remain leads rather than newly verified dates.

Source for `first_observed`: [r2-pssg-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/pssg/pssg.pdf) — PDF pages 14–15 / printed pages 8–9, Compliance and Consumer Services divisions.

### Skilled Trades BC Appeal Board (`skilled-trades-bc-appeal-board`)

New reviewed record. Establishment: **unresolved / null**. Status: `documented_partial`.

The 2022/23 report explicitly documents a rename on 2022-12-01 and statutory continuation, so the earlier Industry Training Appeal Board is not a separate gone body. The inaugural report dates the start of operations to 2006. The exact legal establishment/commencement date was not located; established stays null. The April 1 reporting boundary is not promoted to an opening day.

Source for `first_observed`: [r2-itab-first-report](https://www.stbcab.ca/app/uploads/sites/771/2020/01/ITAB_AR_2006-2017.pdf) — PDF page 5 / printed page 5, Appeals during Reporting Period.

Source for `legal_basis`: [r2-stbcab-rename](https://www.stbcab.ca/app/uploads/sites/771/2023/08/STBCAB_AR_2022-23.pdf) — PDF page 5 / printed page 5, Mandate, statutory continuation quotation.

Source for `names`: [r2-itab-first-report](https://www.stbcab.ca/app/uploads/sites/771/2020/01/ITAB_AR_2006-2017.pdf) — PDF page 5 / printed page 5, Message from the Chair.

Source for `names`: [r2-stbcab-rename](https://www.stbcab.ca/app/uploads/sites/771/2023/08/STBCAB_AR_2022-23.pdf) — PDF page 3 / printed page 3, opening paragraph.

Source for `research_events`: [r2-itab-first-report](https://www.stbcab.ca/app/uploads/sites/771/2020/01/ITAB_AR_2006-2017.pdf) — PDF page 5 / printed page 5, Message from the Chair — Appeals during Reporting Period.

Source for `research_events`: [r2-stbcab-rename](https://www.stbcab.ca/app/uploads/sites/771/2023/08/STBCAB_AR_2022-23.pdf) — PDF page 3 / printed page 3, Message from the Chair, opening paragraph.

### Intimate Images Protection Service (`intimate-images-protection-service`)

New reviewed record. Establishment: **2024-01-29**. Status: `documented_partial`.

The service launch and commencement of the Intimate Images Protection Act coincide in the announcement but are separately typed. Joint issuing ministries and collaboration with the CRT are not treated as administrative parenthood. Full parent history remains unverified.

Source for `established`: [r2-iips-launch](https://archive.news.gov.bc.ca/releases/news_releases_2020-2024/2024AG0004-000096.htm) — Dateline, opening launch paragraph and paragraph beginning To ensure that victims.

Source for `legal_basis`: [r2-iips-launch](https://archive.news.gov.bc.ca/releases/news_releases_2020-2024/2024AG0004-000096.htm) — Opening and service-launch paragraphs.

Source for `research_events`: [r2-iips-launch](https://archive.news.gov.bc.ca/releases/news_releases_2020-2024/2024AG0004-000096.htm) — Opening paragraph.

### Civil Forfeiture Office (`civil-forfeiture-office`)

New reviewed record. Establishment: **2005**. Status: `documented_partial`.

The page explicitly says the office was established in 2005. This is not assumed to be the date of statutory commencement or of the first proceeding. The ministry and internal branch placement are documented only as a present-day observation; no continuous 2005–present interval is invented.

Source for `established`: [r2-cfo-about](https://www2.gov.bc.ca/gov/content/safety/crime-prevention/civil-forfeiture-office) — Opening paragraph.

Source for `parents`: [r2-cfo-about](https://www2.gov.bc.ca/gov/content/safety/crime-prevention/civil-forfeiture-office) — Second paragraph, explicit part-of statement.

### BC PharmaCare (`bc-pharmacare`)

New reviewed record. Establishment: **unresolved / null**. Status: `documented_partial`.

The 2003 ministry mandate explicitly includes operating this provincial service plan. This adds an observed historical administrative placement, not the program start. Later versions of the program and the full parent chronology remain unverified.

Source for `first_observed`: [r2-health-services-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/hs/hs.pdf) — PDF page 17 / printed page 11, Ministry of Health Services Mandate box.

Source for `names`: [r2-health-services-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/hs/hs.pdf) — PDF page 17 / printed page 11, mandate box.

Source for `parents`: [r2-health-services-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/hs/hs.pdf) — PDF page 17 / printed page 11, Operate the two provincial service plans.

### Medical Services Plan (`medical-services-plan`)

New reviewed record. Establishment: **unresolved / null**. Status: `documented_partial`.

The 2003 ministry mandate explicitly includes operating this provincial service plan. This adds an observed historical administrative placement, not the program start. Later versions of the program and the full parent chronology remain unverified.

Source for `first_observed`: [r2-health-services-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/hs/hs.pdf) — PDF page 17 / printed page 11, Ministry of Health Services Mandate box.

Source for `names`: [r2-health-services-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/hs/hs.pdf) — PDF page 17 / printed page 11, mandate box.

Source for `parents`: [r2-health-services-plan-2003](https://www.bcbudget.gov.bc.ca/2003/sp/hs/hs.pdf) — PDF page 17 / printed page 11, Operate the two provincial service plans.

## Validation and what was not tested

Local checks cover JSON parsing, unique record/source IDs, source-catalogue resolution, required claim provenance, date format/precision, observation boundaries, baseline record preservation and matching delta/full outputs. See validation-report.json for actual results.

The repository was not checked out or modified. Its build scripts, npm tests, ministry-name matcher, event rendering and Evidence cards were not run. This package is a research handback, not a certified production build. Follow the README integration checks before treating it as an updated atlas.

Failed retrievals and unpromoted leads are summarized in research-limitations.json. The absence of a new record is not a conclusion that no history exists.
