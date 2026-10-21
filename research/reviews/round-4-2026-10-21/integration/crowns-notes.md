# Round 4, crowns module: integration notes (21 October 2026)

Read the report, all 46 claims, sources, relationships, coverage and QA, and checked the surprising
claims against the raw originals (the key OICs of 1962-1985, the UTA Act, the 1966 schedule, Hydro's
1964 report, the Harbour Board Repeal Act, the 1993 Hansard, MO 5/2004); all match. Subject ids,
source URLs and claim ids are validated; proposal.json parses.

## Applied (32 events, 8 body changes, 1 new body, 5 event corrections)

**Transit.**
- UTA starts 20 July 1978, when s. 2 came into force (OIC 1931/1978); the old 1979 was
  bctransit.com's year. It ends 12 August 1982 under the name UTA only: the corporation continues as
  BC Transit through becameId.
- UTA ministry: Municipal Affairs and Housing from the body's start (OIC 1930/1978, made 13 July),
  then Municipal Affairs from the 5 December 1978 cabinet change until OIC 1535/1982. This replaces a
  period inferred from recommending ministers.
- BC Transit starts 12 August 1982 (OIC 1534/1982 and the consolidation's note). The pre-rename
  Municipal Affairs row moves off BC Transit.
- MTOC starts 18 January 1980 (OIC 29/1980); the old 31 July 1979 was the assent. Its property,
  rights, obligations and employees passed to BC Transit on 1 June 1985, the day a new MTOC board was
  appointed, so it was not amalgamated. Proposed: becameId null, serviceSuccessorIds [bc-transit],
  ended 1985-06-01, with an endedMeaning saying this is the end of operations, not a legal end.
  **Reviewer's choice:** the alternative, ended null, draws an empty shell to 2026.
- Board-appointment provisions (G3) for the UTA (from elected municipal office-holders) and MTOC are
  events, not drawn lines.

**Hydro.**
- BC Hydro starts 30 March 1962, the proclamation day under OIC 839/1962. BC Archives' 31 March is
  kept as a `conflicts` entry.
- Lineage events: the 1962 first directors and co-chairs; the 29 July 1963 ultra vires finding (from
  Hydro's own annual report; the judgment was not retrieved); the 27 September 1963 settlement; the
  20 March 1964 Acquisition Act, retroactive to 1 August 1961; OIC 2386/1965; the amalgamation at
  5 p.m. on 20 August 1965, with share cancellation (s. 5); BC Electric's formal dissolution by OIC
  2387/1965 on 23 August 1965.
- The 1964 Act in force on 23 March 1964 is a `legal_basis_change`, not a second start. Crown
  agency, Finance as fiscal agent and Cabinet appointment of directors are typed facts in it; fiscal
  agency is not a ministry period.
- **Correction:** BC Electric and the BC Power Commission now end on 20 August 1965, not 31 March
  1962. The 1962 amalgamation was invalid, and the 1966 Act's agreement ends their separate
  existence on the 1965 date. They will be drawn beside BC Hydro in 1962-65, which is the legal
  position; the descriptions say they operated together under the Hydro name. **Reviewer's
  choice:** for an operational picture, keep 30 March 1962 and carry 1965 in endedMeaning. Not
  recommended: an invalid merger is not an ending.

**Liquor.**
- The LDB keeps its 1973 start (the Liquor Administration Branch). Its establishedMeaning now gives
  the statutory establishment of the LDB name on 31 December 1976 (OIC 3494/1976).
- LDB ministry: Consumer and Corporate Affairs from 31 December 1976 (OIC 3495/1976). The end is
  NOT known. **Integrator:** cap it at the next assignment, or mark it start_documented_end_unknown;
  do not let null read as "continuing".
- Events: the assignment order, the commencement, and the 1 April 1977 budget split (Hansard).
- The Liquor Control Board gets the 31 December 1976 repeal of the Government Liquor Act as an
  event. Its 1973 end is unchanged: a repeal is not a dissolution.

**Housing, steamship, rail.**
- PRHC: the Housing Fund held all three Pemco shares at 31 March 1975 and 1976 (an observation).
  The 12 April 1976 name-change resolution is added, separate from the 7 May certificate in use.
- BC Steamship is incorporated 5 May 1975 (was 1975). Events: its Washington subsidiary (acquired 15
  May 1975) and its ownership through five directors in right of the Province.
- BC Railway Company: the Vancouver Wharves purchase, complete on or before 30 March 1993 (Hansard;
  the buyer could be the Company or BC Rail Ltd.); and MO 5/2004, signed 30 December 2003, approving
  transfer of BC Rail Ltd.'s 75% partnership interest (an approval, not a closing).

**New body `bc-harbours-board`.** Ends 30 May 1985 (OIC 1061/1985, confirmed by the Public Accounts).
No established date; firstSeen is the 23 September 1983 repeal Act, since the repository's "est.
1967" has no source here. Services passed to BC Development Corporation and BC Railway Company.
Check its kind (crown-corporation) against the Harbour Board Act.

**Event corrections** (no deletions): atlas:uta-created-1979 becomes a `retrospective_origin_claim`;
four assent events' "proclamation date not found" notes now point to their in-force events.

## Not applied (8 entries)

- **Dunhill and its subsidiaries:** no atlas body, and none proposed. Round 4 dates the Crown
  milestones (25 January, 22 May and 7 June 1974) but not the end or identity, so a body would be
  drawn to 2026; W.K.P./Dunhill (1976) must not be merged on name alone. proposal.json gives the
  record to create once an end is found.
- **LCLB:** no body or sub-agency holds it; the bridge to the Liquor and Cannabis Regulation Branch
  is unsourced.
- **MTOC 1991 HR heading:** an observation after the drawn end (OIC 29/1980's signer is no assignment).
- **Already held:** the 1961 vesting; BC Transit's Education and HR periods (responsible-1.json).
- **Vancouver Wharves:** C043 is a medium-confidence reprint with no body; C044 (25 March 1993) is
  marked hold.
- **Harbours Board railway assets:** a lead, not a claim (exchange for BCR shares in fiscal 1983/84).

## Open questions, rewritten

- **E1 (ministries).** Missing: who administered the Liquor Distribution Act and the MTOC Act in
  1979-1991, and the first minister for BC Steamship and PRHC. Document: the statute-assignment OICs
  after each swearing-in (December 1978, 1979, August and November 1986, November 1991), in BC Laws
  arc_oic, searched by Act title. Hand back: dated responsible rows citing each OIC.
- **E9 (LDB name).** Missing: when "Liquor Administration Branch" became "Liquor Distribution
  Branch", between 1973 and 31 December 1976. Document: the 1973/74-1976/77 Public Accounts and
  Estimates (archive.org scans), reading the Attorney General's and Consumer Services' votes. Hand
  back: name observations by fiscal year, with pages.
- **E9 (MTOC legal end).** Missing: the Act or order that repealed the MTOC Act or dissolved the
  company after 1991. Document: the BC Laws table of repealed public statutes (M) and later Transit
  Act amendments. Hand back: the repeal citation and in-force date.
- **E10 (Harbours Board).** Missing: the original Harbour Board Act (1967?) and its commencement,
  and the ss. 4-5 transfer orders. Where: BC Laws hstats 1967; arc_oic 1983-85. Hand back: the start
  with its meaning, and each transfer's date and recipient.
- **E10 (Dunhill).** Missing: how and when the original parent ended (wind-up, amalgamation or
  sale), and whether the 1976 W.K.P./Dunhill company is the same entity. Document: Dunhill notes in
  the Public Accounts from 1976/77; the BC Registry files for both. Hand back: an end event and an
  identity statement.
- **E3 (PRHC).** The 1973 purchase day, instrument and first minister: Public Accounts 1973/74
  Housing Fund schedule, 1973 Housing Act OICs, the company 52129 file.
- **E11 (Wharves).** The 1993 closing day, buyer and partnership chain: BC Rail's 1993 annual
  report, MO 5/2004 Schedule A closings, registry nos. 44407, 59694, 176504, 1282745, 284435.
- **F5 (LCLB).** Missing: the order or Act that renamed the Liquor Control and Licensing Branch,
  joining its 1976 start to today's branch. Hand back: a gone-body record with names[].
- **G3.** Each remaining Crown corporation's board section (UTA, MTOC and Hydro 1964 are done here).

## Summary

32 events, 8 body changes, 1 new body (BC Harbours Board), 5 event corrections, 8 not-applied
entries; all 46 claims accounted for. No blockers. Three reviewer choices: MTOC's ended on its
transfer day; the 1965 ends that draw BC Electric and the Power Commission beside Hydro in 1962-65;
and the open end of the LDB's Consumer and Corporate Affairs period.
