# What this round changed, and what it left

The package is kept as delivered. `convert.py` (run from the repository root with `python3 -I`) is
the only route from it into the history.

## Applied

- **Health-authority predecessors.** `history/bodies-health-lineage.json` replaces the single
  `regional-health-boards-1997` record (removed from `bodies.json` and `responsible-2.json`):
  - the 44 Schedule A constituents of B.C. Reg. 293/2001, each `becameId` its authority, ending
    12 December 2001 (deposited that day; signed 11 December);
  - the seven community health services societies, which are not in Schedule A: their services
    passed on (`serviceSuccessorIds`), ending as independent bodies when M298–M305/2001 replaced
    their boards. Their dissolution is not dated;
  - the 43 councils that M432, M441 and M444/1996 provided would amalgamate into a board, ending in
    1997 (rescinded only "on amalgamation"), and the Simon Fraser, Burnaby and Richmond boards.
  No start is guessed. Prince George's council (24 March 1995) and Simon Fraser/Burnaby (16 December
  1996) have one; the rest are drawn from the first day a source shows them (`firstSeen`) or, with
  neither, are listed in their successor's lineage without being drawn.
- **The five authorities and PHSA** now start on 12 December 2001. PHSA has no regional
  predecessors; its description gives its founding agencies and the 2018 branch amalgamation.
- **Wording.** BCSHS is a member of HEABC, not within it; BCTFA was established under the Build BC
  Act, not the Transportation Act.
- **Events** (`atlas/events-health-lineage.json`, `atlas/events-institutional-history.json`): New
  Directions (February 1993), the 1993 Act, Better Teamwork (1996), the 1997 devolution, Nisga'a
  (1999), each authority's amalgamation, the March 2002 Central Coast transfer; BCCDC 1955–2001,
  BC Women's 1927–1994, PHSA 2001 and its branch societies, BCSHS's incorporation, MSC 1968,
  PharmaCare 1974 and 1987, the 1946 and 1959 departments, the 2004 and 2010 function transfers,
  BCTFA's legal basis and its two subsidiaries, the 2010 HPO split, the 1974 sheriff amalgamation.
  FNHA's 2013 transfers and BC Cancer's 1938/1974 were already held and are not repeated.
- **Path to the people** (`pathToPeople` in `src/government/snapshot.js`): the diagram and panel
  show the whole accountability line for a chosen body; the people's description no longer equates
  the people with the electors, and years before 1949 name who the franchise excluded.

## Not applied yet

- **Typed Crown relations** (owned by, administered by, member of, board appointed by). The
  ownership facts are recorded as events; drawing them needs a relation kind the diagram does not
  yet have, kept apart from "answers for".
- **Bodies the diagram does not hold**: the Homeowner Protection Office, Provincial Rental Housing
  Corporation, the modern B.C. Ferry Authority, HSSBC/BCCSS, the professional-regulator mergers,
  the Open Learning/TRU and school-district families, and the 20-entry service-plan exemption list.
- **Scrutiny and remedy routes** (Auditor General, Ombudsperson, complaints, judicial review), which
  the research says must be sourced body by body.
- Everything in `research_backlog.md`.
