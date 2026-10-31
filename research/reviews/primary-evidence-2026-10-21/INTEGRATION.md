# What this follow-up changed, and what it left

The package is kept as delivered, without its `evidence/` folder: 159 MB of original orders,
Gazettes and registry records, each listed with its hash in `evidence_manifest.json` and cited by
URL in the source register. Two converters bring it in (run from the repository root with
`python3 -I`):

- `research/reviews/institutional-history-2026-10-21/convert.py` reads this package as well as its
  own and writes `history/bodies-health-lineage.json`, so one generator owns the health bodies;
- `convert.py` here writes `atlas/events-primary-evidence.json` and `history/bodies-primary-evidence.json`.

## Applied

- **Designations replace stand-ins.** All 11 boards and 29 of the 30 continued councils start on the
  effective day of their original designation order (M273/1994 to M393/1995). Sea to Sky starts in
  1994 (its day is unconfirmed); the four councils created in 1997 start on their member-appointment
  trigger (M49-M51/1997 on 31 January; Campbell River/Nootka in March 1997). Northern Interior starts
  on 17 November 1994 (M357/1994): the 13 October 1994 composition order (HL20) is no longer read as
  its start. The three 1994 boards folded in 1996-97 (Simon Fraser, Burnaby, Richmond) are dated too.
- **Names over time.** A body now carries `names` periods, and is drawn under the name it had that
  year: Upper Fraser Valley Health Board (1994) → Fraser Valley Regional Health Board (1995) → Fraser
  Valley Health Region (1997); North Okanagan's interim Columbia Shuswap name; the Simon Fraser
  board's short-lived intermediate name; Central Kootenay → Kootenay Boundary (21 January 1998);
  twelve council renamings. Each is dated by the day its order was made; deposit dates are mostly
  not recovered, and the evidence card says so.
- **The 1997 roster.** 1997 draws 52 bodies (11 + 34 + 7), 2000 draws 51. The Nisga'a council
  (1995-1999) is added, ending with the removal of its designation, not the end of Nisga'a health
  services. The nine councils the four 1997 councils combined are added as their predecessors.
- **Ministries stated, not inferred.** Every board, council and society answers to the Ministry of
  Health and, from 5 June 2001, Health Services, from the follow-up's intervals (statute for boards
  and councils, appointment orders and funding agreements for societies). The 1994-96 bodies answer
  under the 1993 Act. No health body before 2001 is placed by inference any more.
- **Societies.** Registered 13 March 1997; governors replaced 12 December 2001; dissolved
  15 February 2002, per the registry. They stand until the dissolution.
- **Events** (48): the 1995 twenty-board designation, the 25 August 1997 hierarchy change, the
  Children and Families program role, the 5 June 2001 Health Services/Health Planning split, the
  society appointments and dissolutions; the 1893 Health Act, the 1934 Social Welfare Section, the
  1946 commencement (1 October) and transfer orders, the 1947 reversal, the 1959 split, the 1973 and
  1977 renamings and the 17 names of OIC 3199/1976; PHSA's two 2018 amalgamations and the registry
  identities of its agencies' societies; the nine sheriff bailiwicks and the 1974 jurisdiction
  statute; the 2003 B.C. Ferry Authority; BC Housing's 1999 ministry change.
- **Bodies.** The Homeowner Protection Office (21 September 1998 to 1 April 2010, under Municipal
  Affairs; its services passed to BC Housing, its loans to Finance) and the Provincial Rental
  Housing Corporation (provincial from 1973; Pemco Holdings Ltd. until 1976). PRHC has no stated
  ministry and is drawn in the lane for bodies with none.

## Not applied

- The seven rural regional health boards of the 1995 twenty-board set (West Kootenay-Boundary, East
  Kootenay, Cariboo, Upper Island/Central Coast, North West, Coast Garibaldi, Peace Liard): their formal end is open
  (HD006), and the research warns against a common 1999 end.
- The 43 earlier councils' execution days, the societies' asset transfers, and the 1974 sheriff
  amalgamation instrument: still open, as the report lists.
- Typed relations beyond "answers for": PRHC's ownership, BC Housing's administration and 2024
  control, and Health Planning's policy role beside Health Services are events, not drawn lines.
