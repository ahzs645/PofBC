# What to research next

The complete list of what the atlas still needs, as of **21 October 2026** (after the institutional-
history package and its primary-evidence follow-up). Each item says what is missing, what is
already known, the document that would settle it, where to look, and what to hand back. Tick an
item when its evidence is handed back; how to add it is in [`README.md`](README.md).

Rules for every hand-back are the same as before: one claim, one source with a locator; keep the
precision the source gives; say what each date dates (signed, deposited, in force, registered,
opened, observed); unknown stays `null`; a relationship is recorded only where a source states it
for that period.

**Where the atlas stands** (computed from the data across 1871-2026):

| Measure | Now |
|---|---|
| Ministry-years with a minister on record | 1,998 of 2,015 (17 without, all Treasury Department) |
| Body-years with a stated responsible ministry | 2,610 |
| Body-years placed beside a ministry by inference | 98 |
| Body-years with no ministry (excluding the courts, which have none by design) | 648 |
| Sub-agencies with a start date / a dated sighting / neither | 43 / 50 / 158 of 251 |
| Past sub-agency-years whose parent is inferred from today's | 1,609 of 1,641 |
| Bodies whose main source is Wikipedia | 25 |
| Bodies whose start is a year only | 65 |
| Historical bodies with no start at all (listed in lineage only) | 47 |

Priority: **P1** changes what the diagram draws; **P2** corrects or deepens what a panel says;
**P3** completes the record.

---

## A. The regional health system, 1990-2002

Most of this is now drawn from original orders (`reviews/primary-evidence-2026-10-21/`). What is left:

- [ ] **A1 (P1) The seven rural regional health boards of 1995.** West Kootenay-Boundary, East
  Kootenay, Cariboo, Upper Island/Central Coast, North West, Coast Garibaldi and Peace Liard were
  in the twenty-board set of M597/1995 (6 December 1995) and were not continued in 1997. Wanted:
  each board's original designation order and effective day (as found for the other thirteen,
  M199/1994 to M55/1995); every amendment to its designation; its formal end. M45/1999 (Reg. 31/99)
  repealed Reg. 521/95 effective 28 February 1999, but the research warns not to give all seven
  that end without their intervening history (HD006). Also: whether each was succeeded by the
  same-named community health services society of 1997, or only replaced in operation. *Where:* BC
  Laws ministerial-order archive (`mo/hmo/m####_1994` and `_1995`), the 1995-1999 cumulative
  regulation bulletins. *Hand back:* `bodies-*.json` records with `established`, `ended`, `names`.
- [ ] **A2 (P1) The 43 councils folded into boards in 1996-97.** Each has a name and a successor
  (M432, M441, M444/1996) but no start and no end day, so none is drawn. Wanted, for each: its
  original designation order and effective day (the same search that recovered the 34 continuing
  councils), and the day its amalgamation was carried out. The orders act only "on amalgamation";
  the day needs the minister's specification under Reg. 338/96 s. 4, legal correspondence, or the
  council's or board's closing minutes or statements. *Hand back:* `established` and `ended` per
  council, with locators.
- [ ] **A3 (P2) The rest of the 82-council plan.** The 1993-95 framework planned twenty boards and
  82 councils; the 34 continuing and 43 folded councils do not account for every council
  designated. Wanted: the full list of councils ever designated, 1994-1997, with orders. *Where:*
  the 1994-95 ministerial orders already downloaded as leads in the follow-up's
  `evidence/health_designations_raw/`.
- [ ] **A4 (P3) Two unconfirmed days.** Sea to Sky Community Health Council's original effective
  day (M444/1994 pairs an appointment cover with a designation annex), and the date line of M96/1997
  (read as March 1997).
- [ ] **A5 (P3) When the renamings took effect.** Twenty-three renaming orders of 1995-1999 are dated
  by the day they were made; their deposit or effective days are mostly not recovered. *Where:* the
  1997 and 1998 cumulative regulation bulletins (the 1999 one gave Upper Skeena's).
- [ ] **A6 (P2) The societies' assets.** Registry dissolution on 15 February 2002 is known for all
  seven (S0036593-S0036599); to whom and when their assets, staff and contracts passed is not.
  *Where:* final society filings, transfer agreements, the successor authorities' 2001/02 audited
  statements (notes on restructuring).
- [ ] **A7 (P2) What the councils, boards and societies took over in 1997.** The hospital societies,
  union boards of health and ministry health units whose services they absorbed: per community,
  which institution transferred, under which mechanism (Hospital Transfer Regulation 359/94,
  Designated Corporations Regulation 24/96, Transfer of Union Board Powers and Duties Regulation
  32/97, special resolutions), and when. Start with the largest hospitals and the union boards.
  *Hand back:* bodies for the union boards and health units, events for each transfer.
- [ ] **A8 (P3) The regional hospital districts.** Created under the Hospital District Act; they fund
  hospital capital, distinct from the authorities that run hospitals. Wanted: the list over time,
  each district's creation, and its board (the regional district's). This needs a "funds" relation
  (see G1).
- [ ] **A9 (P3) Health service delivery areas.** Fifteen were announced in December 2001; there are
  sixteen today. When and why the sixteenth came, and the boundary changes of 2003 and 2008
  (Schedule B of B.C. Reg. 293/2001). These are areas, not bodies.
- [ ] **A10 (P2) Nisga'a health governance.** The Nisga'a Valley Health Board (later Authority):
  its creation, legal form, and relationship to the Nisga'a Lisims Government and the Province from
  2000. The 2002 treaty implementation report (official-index only so far, HL23) and later annual
  reports.
- [ ] **A11 (P2) FNHA's governance bodies.** The First Nations Health Society's incorporation
  (registry number and date), the First Nations Health Council and Health Directors Association
  (dates, form), the 2007 Tripartite First Nations Health Plan and 2011 Framework Agreement
  (signatories, dates). So FNHA's partner line can be explained by its own governance.

## B. PHSA and its agencies

- [ ] **B1 (P2) BC Renal:** the December 2001 announcement lists it; its own account says 2002. The
  transfer instrument, or its 2001/02 and 2002/03 reports.
- [ ] **B2 (P2) BC Transplant:** when Pacific Organ Retrieval for Transplantation (PORT, 1986)
  became BC Transplant Society. The registry has "British Columbia Transplant Society" from
  1 April 1986 (S0021154); whether PORT was ever its registered name.
- [ ] **B3 (P2) Children's and Women's:** the parties to the 15 July 1997 amalgamation (S0037131), and
  whether Sunny Hill joined in 1997 or 2000 (its own account says both).
- [ ] **B4 (P2) BCCDC:** the parties to the 2 April 2001 amalgamation (S0042940), and why a second
  society (S0042656) was registered in January 2001.
- [ ] **B5 (P2) The December 2001 branch societies:** which numbered branch society (S0044073-78)
  continued which agency, so each agency's legal line runs unbroken to the 2018 amalgamation.
- [ ] **B6 (P2) Riverview, the BC Mental Health Society and Forensic Psychiatric Services.** Direct
  provincial operation to 1988, the society from 11 December 1987, PHSA from 2001; the Forensic
  Psychiatric Services Commission's statute and dates; Riverview's closure (2012). Keep site,
  hospital, corporation and service apart.
- [ ] **B7 (P2) BCEHS and PHSA.** The Emergency Health Services Commission's 1974 instrument
  (Health Emergency Act commencement), and when and how BCEHS came under PHSA (2010 commitment,
  2013 continuation as a corporation).
- [ ] **B8 (P3) Shared services.** BC Health Authority Shared Services Organization, then Health
  Shared Services BC (2009 supply chain), its 2016 move into a society, PHSA oversight (March
  2018), BC Clinical and Support Services Society (S0054278: when registered), and BCSHS's transfer
  waves after 1 April 2026 (each function and its day).
- [ ] **B9 (P3) Other PHSA programs:** Cardiac Services BC, Correctional Health Services (from
  1 October 2017, out of the Corrections Branch), Provincial Language Services, Perinatal Services
  BC, the Abbotsford Regional Hospital and Cancer Centre company (PHSA 15%, Fraser 85%).

## C. The health ministry and its direct programs

- [ ] **C1 (P2) Every reorganization's transfer schedule.** Which functions moved in 2001 (Health
  Planning: partly known), 2005, 2008 (Healthy Living and Sport), 2011, 2017 (Mental Health and
  Addictions) and 2024 (its return). The orders in council with their appendices are the evidence;
  appointment announcements alone are not.
- [ ] **C2 (P3) The 1977 statutory titles.** The proclamation itself (authorized 21 October 1977),
  not only the order authorizing it.
- [ ] **C3 (P2) The Provincial Health Officer.** The office as an office: the 1892 appointment, the
  1893 Provincial Board of Health, the statutory office (Health Act, then the Public Health Act
  2008), and annual reporting from 1993. Apart from BCCDC.
- [ ] **C4 (P3) Programs.** BC Hospital Insurance Service (1949 start, 1959 absorption), the Medical
  Services Plan's start apart from the Commission's (1 July 1968), PharmaCare's 1974 instrument
  under Human Resources and the 1987 transfer order, Health Insurance BC (2005).
- [ ] **C5 (P2) Health profession regulators.** Each college's creation and every merger: the two
  nursing amalgamations (2018, 2020), the four oral-health colleges (2022), the eleven into two
  (June 2024), and the 2026 framework's commencement (not each college's founding). These connect
  through regulation of professions, not service delivery.

## D. Other ministries and their functions

- [ ] **D1 (P1) Reorganization schedules for all ministries.** As C1, for every cabinet change since
  1976: 1979, 1986, 1991, 1996, 2001, 2005, 2008, 2009, 2011, 2012, 2013, 2017, 2020, 2022, 2024.
  Each order's appendix lists the functions moved; this is what turns "renamed" into "these
  branches moved". OIC 3199/1976 is the model (now in the atlas).
- [ ] **D2 (P2) The Treasury Department's ministers.** 17 ministry-years have no minister matched;
  the portfolio was styled "Minister of Finance" in the Executive Council records. Confirm which
  heads matched it.
- [ ] **D3 (P3) The Ministry of Transportation, Communication and Highways (1978):** no minister
  matched.
- [ ] **D4 (P3) Deputy ministers, ministers of state and parliamentary secretaries** before today
  (Gazette appointment notices, Legislative Library directories).

## E. Crown corporations, agencies and their relations

- [ ] **E1 (P1) Which ministry answered for these bodies, by period** (body-years with none in
  brackets): Provincial Rental Housing Corporation (54), Workmen's Compensation Board 1917-1973 (57),
  Emergency Health Services Commission (31), Civil Service Commission (26), Royal BC Museum (23), BC
  Games Society (23), Employment Standards Tribunal (22; Labour and Attorney General disagree), BC
  Film Commission (21), BC Steamship Company (1975) (17), BC Housing (16), BC Railway Company
  1972-2003 (16), First Peoples' Cultural Council (14), Liquor Distribution Branch (13, and 39 more
  inferred), BC Pavilion Corporation (12), WLC Developments (12), Labour Relations Board (11), Open
  Learning Agency (10), Coal and Petroleum Control Board (9), Science Council of BC (23 inferred), the
  Homeowner Protection Office after June 2001 (9 inferred). The Workers' Compensation Review Board,
  Appeal Division and WCAT (61 together) and BC Cancer and BC Transplant before PHSA (42) are also
  unplaced. *Where:* orders in council assigning statutes, the Estimates' votes, annual reports.
  BC Archives authority pages for WCB, the Civil Service Commission and EHSC failed in round 2; try
  them first. *Hand back:* `responsible-*.json`.
- [ ] **E2 (P1) Ownership, administration and control, typed.** For each Crown corporation: who holds
  its shares (or that it has none), who appoints its board (statute and section), who administers
  it under agreement, and from when. Known so far, as events only: BCTFA owns BC Railway Company
  (2010) and TI Corp (2018); the B.C. Ferry Authority is the sole voting shareholder of BC Ferry
  Services, with the Province's preferred shares; BC Housing administers PRHC and has controlled it
  since 26 January 2024; BCSHS is a member of HEABC. Needs the line types in G1.
- [ ] **E3 (P2) PRHC.** The 1973 acquisition (day and instrument: share purchase, order in council or
  statute), the 1961 incorporation certificate, the start of BC Housing's administration, and
  which minister answered for it from 1973.
- [ ] **E4 (P2) The modern ferry structure.** The coastal ferry services contract (first contract and
  renewals), the Province's preferred shares (instrument, date), the BC Ferries Commissioner (2003
  start, statute), and BC Ferry Services Inc.'s 2 April 2003 conversion.
- [ ] **E5 (P2) Pensions and land titles.** BCI and the BC Pension Corporation: corporate ownership
  apart from the pension boards and the assets they manage (Public Sector Pension Plans Act ss.
  5-8, 16-20). LTSA (2005): a non-share corporation, government agent only for specified purposes.
- [ ] **E6 (P2) The 2026 service-plan exemption list (20 entries) and the Public Accounts'
  reporting-entity list.** For each entry: its statute, legal form, registry status and whether it
  still exists. Includes PRHC, the employer associations, Rapid Transit Project 2000 and Canadian
  Blood Services. BC Enterprise Corporation: ceased, continued elsewhere, or a stale listing (its
  Act was repealed 13 March 2023).
- [ ] **E7 (P2) Primary sources for the 25 bodies that rest on Wikipedia:** Liquor Distribution
  Branch, BC Ferry Services Inc., BC Electric (Crown), BC Games Society, BC Film Commission, First
  Peoples' Cultural Council, Columbia Basin Trust, BC Arts Council, Tourism BC, BC Human Rights
  Commission, TransLink (both), Oil and Gas Commission, BCI, BC Pension Corporation, Partnerships BC,
  BC Transmission Corporation, Royal BC Museum, Industry Training Authority, BC Innovation Council,
  Community Living BC, TI Corp, Creative BC, Innovate BC, SkilledTradesBC. Enabling Acts, their
  commencement, and BC Archives authority records.
- [ ] **E8 (P3) Day-level starts for the 65 bodies dated to a year.** The enabling Act's commencement
  or the incorporation day.
- [ ] **E9 (P2) Open questions already recorded in `history/bodies.json`:** the Merit Commissioner's
  dissolution in-force day (2026); OGC to BC Energy Regulator in-force day (2023); when the Liquor
  Administration Branch became the Liquor Distribution Branch; BC Transit's start (1982 rename or
  1983 merger) and MTOC's end; BC Hydro 1961 or 1962; Pacific Carbon Trust's wind-up day; Land and
  Water BC's end (2005); the Provincial Capital Commission's dissolution (2014?); Legal Aid BC's
  operating-name date; Expo 86 Corporation's dates.
- [ ] **E10 (P3) Bodies left out for want of a date:** the Environmental Assessment Office (1995
  Act or 2002), Law Reform Commission (end), Alcohol and Drug Commission (end), BC Harbours Board
  (end), Land Settlement Board (1917, end), BC Housing Corporation, Dunhill Development Corporation,
  Southern Interior Development Initiative Trust, BC Film + Media, BC Council for International
  Education, BC Family Maintenance Agency, Forest Enhancement Society, Forestry Innovation
  Investment (incorporated 31 March 2003 per the Forest Service timeline: confirm), BC
  Infrastructure Benefits.
- [ ] **E11 (P3) Older Crown histories:** BC Rail Ltd. (1984 operating subsidiary), BCR Properties
  Ltd., Vancouver Wharves; Forest Renewal BC's end (14 or 27 June 2002).

## F. Branches and sub-agencies

- [ ] **F1 (P1) Sub-agency starts and sightings.** 158 of 251 have neither, so they vanish before
  2026. Cheapest first: whether the Estimates or service plans list each body in 2025, 2020, 2015,
  2010, 2005 and 2002 (a sighting). The queue (`queue/INDEX.md`, regenerated from the data) splits
  them into batches with a guide each.
- [ ] **F2 (P1) Sub-agency parents over time.** 1,609 of 1,641 past sub-agency-years place a body
  under today's parent by inference. Ministry annual reports' organisation charts for each
  reorganization year (2001, 2005, 2017, 2020, 2022, 2024 first) would date the moves.
- [ ] **F3 (P2) The sheriffs.** The administrative instrument that combined the nine offices in 1974
  (Attorney General's 1974/75 annual report, an order in council); and each county sheriff's office
  from 1857 (Sheriffs Act, county creation).
- [ ] **F4 (P2) Enforcement and lands branches.** Conservation Officer Service (the 1905, 1961, 1980
  and 2002 instruments); BC Parks (the 1957 Parks Branch instrument, the 1965 Park Act); BC Wildfire
  Service (the order renaming the Wildfire Management Branch); the Surveyor General (each split,
  the 2005 move to LTSA, the 2019 division).
- [ ] **F5 (P2) Bodies that are gone, with a successor still drawn:** the Liquor Control and
  Licensing Branch, Emergency Management BC, the Industry Training Appeal Board, BC Ambulance
  Service, the Provincial Game Commissioner, the old Forest Service divisions, and the tribunals
  folded in the 2002-03 core review.
- [ ] **F6 (P3) Still to settle:** the Environmental Appeal Board's start (1981 or 1982: the
  commencement instrument; a proposal is in `reviews/round-2/decision-recommendations.json`);
  Powertech Labs (1988, or service from 1989).

## G. Accountability, services and the people (model work, and the evidence it needs)

- [ ] **G1 (P1, our side) New line types.** Owned by, administered by, member of, board appointed
  by, funded by, regulated by, oversees: each drawn differently from "answers for", and none of
  them treated as a path to the people. Needs E2's evidence to be worth drawing.
- [ ] **G2 (P1) Scrutiny and remedy routes, body by body.** Which bodies the Auditor General audits,
  which the Ombudsperson can investigate (the Ombudsperson Act schedule, and when each body was
  added), which are under freedom-of-information law (FOIPPA Schedule 2, by date), and each body's
  appeal or judicial-review route and complaints process. These are lines from the officers of the
  Legislature to the bodies, and back to the people through their reports.
- [ ] **G3 (P2) Who appoints each board.** The statute and section for each Crown corporation,
  agency, tribunal and authority (Cabinet, a minister, a member body, an election), dated.
- [ ] **G4 (P2) Who each body serves.** The population a body serves (patients in a region,
  licensees, students, ratepayers), for a services view beside the accountability path.
- [ ] **G5 (P2) The franchise in detail.** The atlas names four exclusions before 1949 (women to
  1917, Chinese and South Asian Canadians to 1947, Japanese Canadians and First Nations people to
  1949). Wanted from Elections BC's electoral history and the Provincial Elections Acts: the exact
  year each exclusion began and ended, other exclusions (Doukhobors, Mennonites, Hutterites and any
  others), property and residence qualifications, and the voting age over time.
- [ ] **G6 (P3, our side) Ministers as their own points**, so a path runs through the minister, as
  civlab's runs through each body's head.
- [ ] **G7 (P3) First Nations governments and treaties.** Modern-treaty governments (Nisga'a 2000,
  Tsawwassen 2009, Maa-nulth 2011 and later) and their agreements with the Province, as governments
  in their own right, not ministry bodies.

## H. The Legislature, the early province, scale and marks (carried over)

- [ ] **H1 (P2) MLAs, ridings and by-elections** for every Parliament before the 43rd (Elections BC's
  *Electoral History of British Columbia*, the Statements of Votes); party at election apart from
  later caucus changes.
- [ ] **H2 (P3) Sessions and committees** (the Assembly's Journals).
- [ ] **H3 (P3) Before 1905:** the agencies of the Provincial Secretary and of Lands and Works, from
  the Sessional Papers' annual reports.
- [ ] **H4 (P3) Staffing and spending before 2000/01** from earlier Public Accounts, budget and actual
  kept apart.
- [ ] **H5 (P3) Education families:** the final 1996 school-district merger orders and dates; the
  Open Learning Institute (1978), Open Learning Agency (1988) and Thompson Rivers University (2005)
  chain.
- [ ] **H6 (P3) Logos:** masters, first-use dates and permission for the ICBC, BCLC, BC Ferries, BC
  Transit and WorkSafeBC marks; WorkSafeBC's 1968 design and BC Transit's flag lockups as artwork;
  dates for the marks marked "date estimated" or "date unknown".

## Not research: fixes on our side

- Two Administrators of the Government dated only to the month (Macdonald, 1915 and 1917) are
  dropped by the Lieutenant Governor build.
- Staffing rows for "Officers of the Legislature" and "Other Appropriations" (35 each) and three
  one-off ministry spellings are not matched.
- Some division events have no subject id and are skipped.
- The seven rural boards (A1) and the 43 folded councils (A2) are ready to draw the moment they have
  dates: the converter already carries their names and successors.
