# What Round 4 changed, and what it left

Each module (and the Round 3 evidence the package carried, as a fifth, `carried`) was read against the repository, claim by claim, and turned into the history's own
shapes: one reviewed proposal per module in `integration/<module>.json`, with the reasoning in
`<module>-notes.md`. Every claim of the handback is either applied or listed under `not_applied` with
its reason. Editorial changes made after review are listed in each proposal's `editorial` field.

Run from the repository root, in this order:

```sh
python3 -I research/reviews/round-4-2026-10-21/convert.py
python3 -I research/reviews/institutional-history-2026-10-21/convert.py
npm run build:government
```

`convert.py` writes `atlas/events-round4.json` and `history/bodies-round4.json`, makes the corrections
to hand-kept files in place (each only if the file still holds the value it corrects), appends the
decision to `decisions.json`, and writes `overrides.json` for the corrections to files the
institutional-history converter owns (`bodies-health-lineage.json`, `events-institutional-history.json`).
That converter applies them, so each generator still owns the files it writes. Re-running either
changes nothing. The sub-agency records went in once, through the house merge, which checks the
evidence rules:

```sh
npm run research:merge -- research/reviews/round-4-2026-10-21/integration/branches-sub-agency-batch.json
npm run research:merge -- research/reviews/round-4-2026-10-21/integration/health-sub-agency-batch.json
npm run research:merge -- research/reviews/round-4-2026-10-21/integration/carried-sub-agency-batch.json
# the earlier branch batch, adapted so it keeps the newer review metadata on 35 records
# (research/reviews/integration-review-2026-10-21/README.md):
npm run research:merge -- research/reviews/integration-review-2026-10-21/integration/prior-branch-preserving-batch.json
```

Bodies can now say what their end was (`endedMeaning`, beside `establishedMeaning`), and the panel
gives both: "The end is the day it was renamed British Columbia Transit …".

## Applied

**106 events** (`atlas/events-round4.json`), **65 body corrections**, **1 new body**, **8 event
corrections**, **3 decisions**, **27 sub-agency records**, **10 minister terms corroborated**, and a fix
to the minister matching.

- **The regional health system (health).** 51 councils now start on the effective day of their
  original designation order: 42 of the 43 the 1996 orders folded into boards (M273/1994 to
  M393/1995; Prince George was already held) and the nine the four new 1997 councils combined. Each
  is drawn from that day, answering to the minister under the 1993 Act, as the others are. The
  **Capital Health Board starts 8 September 1994**, not 1 September (an explicit supersession), and
  Sea to Sky on 16 December 1994 (M441/1994; the archived annexes of M441 and M444 are swapped).
  Events: the 13 July 1995 FOIPPA "health care body" class; PORT as a program of the Transplant
  Society (funded 1987, initiated 1988, part of the society 1991; the minister's "1985" kept as his);
  Oak Bay Lodge (2004); B.C. Reg. 8/2003 and the 2008 Burnaby parcel; the registry histories and
  15 July 1997 dissolutions of the Children's, Sunny Hill and Women's corporations; EHSC's finances to
  PHSA (2011); BCCSS's society (2008, 2016, 2018); the Provincial Health Officer of 1892 and the 1893
  Health Act's 1895 commencement; and FNHA's registry line (2009-2012) with the Health Directors
  Association (2010).
- **Crown corporations (crowns).** Starts and ends from the instruments, replacing year-only or
  website dates: the **Urban Transit Authority 20 July 1978** (not 1979) to its 12 August 1982 rename,
  so **BC Transit starts 12 August 1982** as the same corporation (MTOC is no longer its
  predecessor); **MTOC 18 January 1980 to 1 June 1985**, when its property and employees passed to BC
  Transit (its services, not an amalgamation; its legal end is unknown, and the end note says so);
  **BC Hydro 30 March 1962** (the proclamation; BC Archives' 31 March kept as a conflict), with BC
  Electric and the Power Commission standing to **20 August 1965**, when the amalgamation the 1963
  judgment had undone took effect; BC Steamship 5 May 1975; the Liquor Distribution Branch's
  statutory start (31 December 1976) and its first stated ministry. The UTA's ministry periods come
  from the assignment orders instead of the ministers who recommended its orders. New body: the
  **British Columbia Harbours Board**, dissolved 30 May 1985 (its start is not in this research, so
  it is drawn from the 1983 Repeal Act). Events: board-appointment and Crown-agent provisions, the
  Hydro sequence 1962-1965, the liquor statutes and 1977 budget split, PRHC's shareholding,
  BC Steamship's subsidiary, BC Rail's Vancouver Wharves.
- **Branches (branches).** The **Medical Services Commission was constituted on 24 March 1967**
  (OIC 964/1967; members appointed the same day), not 1 July 1968, which is Medicare's start: a
  decision records why, and the 1968 event is retyped a retrospective claim. Starts or first
  sightings for 22 sub-agencies (Buy BC 1993, Disaster Financial Assistance 1995, the Arts and Culture
  Endowment 2008, the Training and Education Savings Program 2013, Provincial Treasury 1986, BC Parks
  1 April 1957, the Conservation Officer Service 18 September 1980, and others). The sheriffs'
  statutory chain, 1860-2011, as thirteen events. The Game Commission ends 1 April 1957.
- **Hospital districts and the 1977 titles (root).** Eleven events on the ministry that recommended
  each order: the 27 hospital-district areas (1967), the dissolution of 23 hospital improvement
  districts (1969), the 1972 membership alignment, the 1995 restriction and twelve new districts,
  the 1998 reorganization and five dissolutions, Greater Vancouver's dissolution and division of
  assets (1 January 1999), and the 1977 titles proclamation order and its in-force date.

- **Round 3 evidence the package carried (carried).** The rest of what Round 3 left ready, re-read
  against its sources (`integration/carried.json`). **The Treasury Department's ministers:** until
  June 1916 the Executive Council styled the portfolio "Minister of Finance and Agriculture", which
  the alias in `scripts/build-government-history.mjs` did not match; it now lists both styles, and
  no ministry-year is left without a minister (18 Public Accounts signatures, 1899-1916, recorded as
  corroboration on the terms, not as tenures). **The 1978 Ministry of Transportation,
  Communications and Highways** takes its plural title (OIC 3018/1978; `episodes.js` SPELLING), which
  changes its id. Decisions settle **the Environmental Appeal Board on 1 January 1982** (OIC
  2603/1981) and **Powertech's company on 29 September 1988**. BC Place Ltd. starts 25 March 1980,
  its registration; BC Enterprise Corporation's 1989 end is a cessation (it was dissolved in 2023);
  the BC Games Society's names, the Provincial Museum's opening (1886) and Creative BC's society.

  These reconstructed source URLs from the ids the claims carry (UBC item ids, OrgBook topics),
  because the round-3 source register was not repackaged; each was re-fetched and read.

## Editorial choices

- **Ends that are not legal ends.** MTOC ends on the day it was emptied, with a note that it was not
  dissolved then; BC Electric and the Power Commission end in 1965, drawn beside BC Hydro from 1962,
  which is the legal position after 1963. Left open, MTOC would be drawn to 2026.
- **The Liquor Distribution Branch's first ministry** (Consumer and Corporate Affairs, from
  31 December 1976) ends in 1986 with that ministry; who answered for the branch until 2025 is open.
- **Hospital districts are not drawn.** They are local corporations (a regional district's directors
  are the board; improvement districts were Water Act bodies) and no source puts them under a
  ministry. Their provincial acts are events on the ministry; a register for the districts
  themselves is proposed in `integration/root.json` (`local_register_proposal`), not built.
- **Entity types.** Several sub-agencies are programs, services, web resources or a brand (Trans
  Care BC, four PHSA service nodes, Connectivity in B.C., Safe Campuses BC, Let's Go BC): dated as
  sightings and flagged, not drawn as founding dates.

## Not applied

- **The seven rural regional health boards (A1).** Their original designation days are recovered,
  but no end is: with no end they would be drawn to 2026. Draft records are in
  `integration/health.json`.
- **Relations the atlas cannot draw yet** (G1): administration, ownership, funding, official marks,
  appointment as a line. Kept as events or notes.
- **Bodies the atlas does not hold**: Dunhill Development Corporation and its subsidiaries (no end),
  the Liquor Control and Licensing Branch (no link to today's branch), the Nisga'a Valley Health
  Board, the health profession colleges (a regulators layer is needed), the hospital districts.
- **Claims without a public URL** in the handback, mostly carried round-3 health claims whose source
  register was not repackaged (SSO Administration Society, Forensic Psychiatric Services Commission,
  Provincial Language Services, Health Insurance BC, the 2007 and 2011 FNHA instruments).
- **Claims the handback itself holds back** (an `import_status` or `atlas_import` gate, a "hold", a
  medium-confidence reprint), and the franchise claims, which need a franchise data file.

The questions all of this leaves are in `research/WANTED.md`, rewritten after this round.
