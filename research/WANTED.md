# What to research next

In priority order: what would most change what the atlas shows, first. Each item says what is
missing, where to look, and what to hand back. How to add it: [`README.md`](README.md). Numbers are
as of 2026-09-26 (the Coverage card under the Government view's sources measures them live).

**Where the atlas stands:** 1,973 of 1,990 ministry-years have a minister on record (99%, after
round 3); 2,218 of 2,909 body-years have a responsible ministry stated by a source (76%), 89 more are
placed by inference, and **602 have none**; **41 of 238 current sub-agencies** have a start date and
**50 more** a dated sighting (2026-10-01; [`queue/INDEX.md`](queue/INDEX.md) has the live count).

## 1. Sub-agencies — the biggest visible gap

Most of today's sub-agencies have no start date, so they vanish the moment the timeline leaves 2026.
**The work is now organised as a queue: [`queue/README.md`](queue/README.md)** explains what to look
for and how to hand it back, and [`queue/INDEX.md`](queue/INDEX.md) splits every body into batches
that can each go to one researcher or AI assistant. The queue regenerates from the data, so its
numbers are current; the brief ([`sub-agencies/BRIEF.md`](sub-agencies/BRIEF.md)) remains the
by-parent overview.

- **First, sightings.** For each undated body, whether the Estimates or service plan lists it in
  2025, 2020, 2015, 2010, 2005 and 2002. A sighting is cheaper to find than a founding date and says
  the body existed by then (queue track A).
- **Still to settle:** the Environmental Appeal Board — 1981 as collected, 1982 in its own manual;
  the original commencement instrument would settle it (a proposal is in
  `reviews/round-2/decision-recommendations.json`). (WorkBC is settled: 27 April 2007, by decision.)
  Powertech Labs — 1988 as collected, service from 1989 in BC Hydro's account.
- **Parents over time:** almost none is recorded, so past placement is inferred from today's
  parent. The cabinet shuffles of 2001, 2005, 2017, 2020, 2022 and 2024 moved many branches;
  ministry annual reports' organisation charts are the best evidence.
- **Bodies that are gone:** twelve are recorded (nine of them the safety boards dissolved in 2004).
  Most useful are those with a successor still drawn — the Liquor Control and Licensing Branch,
  Emergency Management BC, the Industry Training Appeal Board, BC Ambulance Service, the Provincial
  Game Commissioner, the old Forest Service divisions — and the tribunals folded in the 2002–03 core
  review (queue track D).

## 2. Which ministry answered for a body (602 body-years with none)

These bodies are drawn in the "no ministry established" lane. Largest gaps, in body-years:

| Body | Years with no ministry | Notes |
|---|---|---|
| Workmen's Compensation Board | 57 (1917–1973) | package item R08; appointments and reports are known, a stated minister is not |
| Emergency Health Services Commission | 31 | |
| Civil Service Commission | 26 | the Provincial Secretary is known for 1917–47 only |
| Royal BC Museum Corporation | 23 | |
| BC Games Society | 23 | |
| Employment Standards Tribunal | 22 | two collected parents disagree (Labour, Attorney General) |
| British Columbia Film Commission | 21 | |
| British Columbia Steamship Company (1975) Ltd. | 17 | |
| BC Housing | 16 | |
| British Columbia Railway Company | 15 | package item R07, 1972–2003 |
| First Peoples' Cultural Council | 14 | |
| Liquor Distribution Branch | 13 | |
| Labour Relations Board | 12 | |
| BC Pavilion Corporation | 12 | |

Round 2 could not fetch the BC Archives authority pages for the Workmen's Compensation Board, the
Civil Service Commission and the Emergency Health Services Commission — try them again, or their
PDF finding aids, first. Hand back periods as `responsible-<n>.json` (see README): `{ministry, from, to, source, note}` for
each stated responsibility. Orders in council (BC Laws' historical OIC archive), the Estimates'
vote structure and ministry annual reports are the usual evidence.

**Leads from the BC Forest Service timeline** (`atlas/events-bcfs-timeline.json`, a secondary
compilation): Forestry Innovation Investment was incorporated on 31 March 2003 (the atlas holds no
start for it); Forest Renewal BC was terminated on 14 June 2002 (the atlas says 27 June); the Small
Business Forest Enterprise Program is dated 1979; the Department of Forests to 1976 (the Archives
diagram says 1975). Each wants a primary source — FII's annual report or BC Registries, the Forest
Renewal repeal, the 1978 Forest Act and Ministry of Forests annual reports.

## 3. Ministries and ministers

- **Treasury Department:** 17 ministry-years with no minister matched — the portfolio was styled
  differently (Minister of Finance) in the Executive Council records; confirm which heads matched it.
- **Ministry of Transportation, Communication and Highways (1978):** no minister matched.
- **Deputy ministers before today** (package R12): only the present's are known. The Legislative
  Library's staff directories and the *BC Gazette* appointment notices.
- **Ministers of state and parliamentary secretaries** before today.

## 4. The Legislature (package R10, R11)

Only the 43rd Parliament's members are recorded.

- **MLAs, ridings and by-elections** for earlier Parliaments — Elections BC's *Electoral History of
  British Columbia* and the Statements of Votes; party at election kept apart from later caucus
  changes, as the 43rd's data does.
- **Sessions and committees** — the Assembly's Journals.

## 5. Before 1905 (package R09)

Agencies of the Provincial Secretary and of Lands and Works before 1905 are thin. The Sessional
Papers' annual report series (by department) list them year by year.

## 6. Scale: staffing and spending (package R13)

Staffing runs from 2000/01. Earlier Public Accounts give FTEs (and spending) back decades; keep
budget and actual apart and quote what each statement says it counts.

## 7. Logos (package R05, R14, R17)

- **The five Crown bodies' masters:** ICBC, BCLC, BC Ferries, BC Transit and WorkSafeBC are in the
  gallery now, from research packages (`research/identity/`, 27 September 2026), but every mark is a
  supplied specimen or a reconstruction, not a master. Still missing: WorkSafeBC's 1968 design and
  BC Transit's flag lockups as artwork; dated first uses for most of their eras; and original masters
  from the organisations' media contacts (`package/logo_acquisition.json` has the routes).
- **Dates for the marks we have:** most are "date estimated" or "date unknown" in the gallery;
  adoption announcements or first appearances in annual reports would date them.
- **Permission:** none of the marks has documented permission to be shown.

## Not research — code fixes on our side

- Two Administrators of the Government dated only to the month (Macdonald, 1915 and 1917) are
  dropped by the Lieutenant Governor build.
- Staffing rows for "Officers of the Legislature" and "Other Appropriations" (35 each) and three
  one-off ministry spellings are not matched.
- Some division events have no subject id and are skipped.
