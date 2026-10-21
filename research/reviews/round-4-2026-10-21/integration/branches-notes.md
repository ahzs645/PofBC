# Round 4, branches module: what to apply and why
Files: `proposal.json` (batch embedded) and `sub-agency-batch.json` (23 records, 35 sources; the
merge dry run passes with no errors or warnings). Generator: `scratchpad/r4-branches-work/build.py`.

## Where things go

- **Sub-agency dates, names and parents → the batch.** Its `research_events` compile to events
  (`sub:<id>:event-n`), so none of them is repeated in `proposal.events`.
- **`proposal.events` holds only the sheriff chain** (subject `sub-bc-sheriff-services`, matching
  the 1973 roster and 1974 events already there): predecessor offices that are not BC Sheriff
  Services itself, so they are lineage events, not a start or a first sighting.
- **No new bodies.** County sheriff offices have no start dates (1888 is a continuation, not a
  creation), so they stay events, as the primary-evidence integration left them.

## Applied (batch)

| Record | Date | What the date dates |
|---|---|---|
| medical-services-commission | established 1967-03-24 | s. 3 in force on the day OIC 964/1967 fixed; members appointed from that day (OIC 965); staff 25 March (OIC 967); assent 23 March; staff added 15 May 1968; Commission notice 6 June 1968 |
| bc-arts-and-culture-endowment | established 2008-03-31 | special account created by 2008 c. 10 s. 113, retroactive commencement; assent 1 May 2008 (read from p. 1) |
| buy-bc | established 1993 | program launch, stated in a 2023 audit; 2002 handover to BC Agricultural Council and 2018 relaunch as events |
| disaster-financial-assistance | established 1995 | program start stated in a 2016 bulletin; regulation made 30 March, deposited 31 March 1995 as events |
| trans-care-bc | established 2015 | "fall 2015" PHSA program; season kept in the meaning, no month inferred |
| bc-training-and-education-savings-program | first seen 2013-03-20 | program regulation made; account continued 23 June 2014; applications scheduled 15 August 2015 |
| provincial-treasury | first seen 1986-04-10 | AG report transmittal; 1985 statute mention kept as an event (commencement unclear); Finance 1986, FCR 1996 |
| building-and-safety-standards | first seen 2014-05-20 | branch named, in Office of Housing and Construction Standards, Natural Gas Development/Housing |
| community-capital-development, infrastructure-policy-and-partnerships | first seen 2025-03-17 | staff table, Ministry of Infrastructure |
| community-safety-and-victim-services | first seen 2024 | 2024 transition-binder chart, PSSG |
| connectivity-in-bc | first seen 2021-04-07 | the web resource, not the Connecting BC program |
| lets-go-bc | first seen 2025-04-23 | official-mark notice (brand); September 2025 campaign use as an event |
| bc-mental-health-and-substance-use-services | first seen 2015-12-17 | current name only, not the rename |
| building-bc | first seen 2019 | 2018/19 report's year end; "since February 2018" kept as a retrospective event |
| 4 PHSA service nodes | first seen 2010 | 2009/10 health annual report (R3H-099, prior module) |
| health-care-practitioners-special-committee-for-audit-hearings | first seen 2024-06-30 | OIC 367/2024 (R3T-036, prior module) |
| bc-parks | first seen 1957-04-01 | Provincial Parks Branch enters Recreation and Conservation; name and parent from that day; 1948 retrospective kept |
| conservation-officer-service | first seen 1980-09-18 | OIC 2085/1980; separation observed April-May 1980 (held at year); Regional Operations 1980/81; Fish and Game Branch 1 April 1957 |

Entity types: programs, a special account, a web resource and a brand are dated as what they are,
in each meaning and note. `established` is used only where a source says the thing itself was
created (an Act, or a program launch the program's own audit or bulletin states). The 2002 Buy BC
handover is not drawn as an end. Kind corrections to propose to the queue: trans-care-bc and the
four PHSA nodes are programs or services (kind `agency` today); connectivity-in-bc and
safe-campuses-bc are web resources; lets-go-bc is a brand. Connectivity in B.C.'s queue
description describes the connectivity program, a different entity.

## Corrections to existing data

1. `atlas:institutional-history-msc-1968`: `legal_establishment` → `retrospective_origin_claim`,
   with a new title and notes. Its source is a 2002 financial statement; the 1967 Act and orders are
   contemporary. The decision `msc-established-1967-03-24` gives the reason and sets 1968 aside.
   Caveat: I did not check whether a 1968 "Medical Service Act" re-constituted the Commission.
2. `atlas:parks-branch-1957-03-28`: keep it, add a `conflicts` note. The department's 1957 report
   dates the Act to 28 March and the division's entry, as the Provincial Parks Branch, to 1 April.
3. `atlas:institutional-history-sheriffs-1974`: notes updated. The nine offices are known from the
   1973 roster, and the Police Act 1974 has been ruled out.
4. Body `game-commission`: `ended` "1957" → "1957-04-01". This matches its own responsible interval,
   and the 1957 report states the day.

## Checked against raw and set aside

- **Safe Campuses BC.** The handback says the 2019 release links to the named resource. In the raw
  release the link label reads "Preventing sexualized violence on B.C. campuses", and the name
  appears only in the URL. I recorded it as `related_label_identity_unresolved`, not as a sighting.
- **OIC 241/1893.** The OCR gives the year as 1897. The scan (`R4B-064-verify.png`) reads "3d July,
  189?", and LG Dewdney served until 1897, so the scan alone is ambiguous. The order number and the
  cancelled 1892 acting appointment support 1893, so I kept it and noted the reading.
- **Medical Services Commission, Parks/Fish and Game 1957, the 1888 continuation and the COS article**
  were checked word for word in the raw text.
- **Not applied** (see `not_applied`): the conflicting 1968 statement; the Financial Administration
  Act "as though a division" rule; appointment, audit, administration, rights-holder and
  recommendation relations (these wait for G1 line types); the Food and Beverage Branch,
  Photographic Branch and Parks and Recreation Division as separate nodes (none has an id); the
  two archival leads (the 1977 reports and the 1890 Gazette roster); the rejected Police Act
  candidate; the 2026 Disaster Resilience Division sighting; the 12 undated records.
- **Possible overlap.** The four PHSA sightings and the audit-hearings committee use Round 3
  health and tribunal evidence. If another Round 4 module hands back the same rows, merge
  de-duplicates identical rows, but a different `first_observed` would compete (the earliest wins).

## WANTED items, rewritten as questions

- **F1 (narrowed).** Thirteen records are still undated. For the three IRR divisions and the EMCR
  Disaster Resilience Division: on what day did the 2025-26 reorganisations create them, and from
  which predecessor divisions? Look in the ministries' FOI-released transition binders and estimates
  notes (docs.openinfo.gov.bc.ca) and in reorganisation memos. Hand back the chart or memo with its
  date. For Safe Campuses BC: find the earliest Wayback capture of
  www2.gov.bc.ca/gov/content/safe-campuses-bc whose title prints the name, and hand back the capture
  date. For the umbrella and web-category records: the editors must first decide the entity type.
- **F2 (narrowed).** Which Minister was designated under the Medical Services Act in 1967? Look for
  an OIC of March-April 1967 designating the "Minister" under s. 2 (bclaws arc_oic). Hand back the
  OIC number, date and minister.
- **F3 (narrowed).** What instrument consolidated the nine offices in 1974, and on what day? Look in
  the Attorney General's 1974/75 annual report, Hodgson's Task Force on Sheriff Services (May 1977)
  and Dogherty's Sheriff Services Program Inventory and Review (September 1977), at BC Archives
  (Court Services records) or the Legislative Library. For each county office: who was the first
  appointee, and when? Use the July Gazette rosters required from 1890 and the Gazette proclamations
  of 1880, 1892, 1895 and 1905.
- **F4 (narrowed).** What directive separated the COS from Fish and Wildlife in early 1980, and on
  what day? Look in Ministry of Environment records and news releases, January-May 1980 (BC Archives
  and the Legislative Library). What OIC, if any, moved the Parks and Recreation Division between 28
  March and 1 April 1957 (bclaws arc_oic 1957)? The Wildfire rename and the Surveyor General's 2019
  division are unchanged.
- **F5 (narrowed, Game Commission only).** The other F5 bodies belong to another module.
- **C4 (narrowed).** Was the Medical Services Act proclaimed for 24 March 1967 (BC Gazette,
  March-April 1967)? Did a 1968 Medical Service Act re-constitute the Commission on 1 July 1968
  (bclaws hstats, 1968 volume)? Hand back each instrument's words on the Commission.
- **G3 (narrowed, MSC only).** For every other board: which statute section governs appointment, and
  from what date?
- **H3 (unchanged).** Only the adjacent sheriff evidence was found. The Provincial Secretary and
  Lands and Works reports, 1872-1905, are on UBC bcsessional.

## Summary

The proposal has 13 events (the sheriff chain), 3 corrections to existing events, 1 body change
(game-commission end), 0 new bodies, 1 decision (MSC established 1967-03-24) and a 23-record
sub-agency batch. The batch gives 5 records a start and 17 a first sighting. Safe Campuses BC gets
only a checked-source row. The batch also carries 21 research events, which compile to events.
17 entries are not applied, and 8 WANTED items have a status. There are no blockers. The MSC
decision and the event retype should go together, and the "1968 Medical Service Act" question is
the one caveat on the 1967 start.
