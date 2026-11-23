# Subsidiary research packages, 2026-11-22: integration

Two handbacks, both kept as delivered:

- `package/`: the first (18 files; its `SHA256SUMS.txt` verifies). It added 8 company candidates and
  25 dated events to an earlier 45-record inventory.
- `verified/`: the follow-up that answered the nine questions this integration raised, from original
  accounts, Gazettes and statutes, with 33 integration actions (`data/review_actions.json`). Its
  `prior_research/` folder was byte-identical to `package/` and is not kept twice, so the `prior_research/`
  lines of `verified/SHA256SUMS.txt` will not verify; every other line does.

- `followup/`: answers to the seven questions left after that, chiefly from the 1978/79 Public
  Accounts, the 1979 and 1990 Gazettes, OIC 631/1986 and BC Cellulose's subsidiaries' own notes, with 24
  actions (`data/FOLLOWUP_ACTIONS.json`). Its `prior_package/` zip was the `verified/` package and is not
  kept twice.

This file says what was checked against the original documents, what changed in the atlas, and what
was held back. Where the packages disagree, the later one is applied.

## What was re-read in the original documents

| Claim | Source | Result |
|---|---|---|
| Swan Valley 40% (1977); more shares bought in 1977/78; entire holding ($8,307,751 book value) sold to Standard Brands for $2.2m | Public Accounts 1977/78, B5 (PDF p. 73), B8 (PDF p. 76) | Confirmed |
| Creston Valley Foods bought the plant for a $1.5m debenture, carried by the Province at $1 | Auditor General 1978, para. 8C.15 (PDF p. 31); Court of Appeal, 1 May 1980 | Confirmed: Creston Valley was newly incorporated, owned through Federal Diversiplex by Hardee Farms |
| Standard Brands bought 100% of Swan Valley's shares on 1 December 1977 for $2.2m | Standard Brands Annual Report 1977, note 6 | Confirmed verbatim. The package's locator ("text lines 569-5…") does not work: the PDF is a scan with no text. It is **printed p. 30, PDF p. 33**. Note 5(d) carries the matching $2.0m promissory note |
| Swan Valley continued federally 1978-01-06; amalgamated 1978-04-28 | Corporations Canada 265241 | Confirmed |
| Name of the amalgamated company (the package's open P0 item) | Corporations Canada 298239 | **Resolved: Standard Brands Canada Limited** from 1978-04-28 to 1982-05-12, then Nabisco Brands Canada; itself amalgamated 1987-03-29 |
| Crown Development Corporation wound up; $1,000 written off | Public Accounts 1977/78, B4 (PDF p. 72), B8 | Confirmed, and **wholly owned** ("entire issued capital stock of 10 common shares"), which the package did not say |
| I.O.K. Poultry 100%, 600 shares; "proceeds on dissolution" $600 | Public Accounts 1977/78 B4; 1979/80 B4, B8 (PDF pp. 172, 176) | Confirmed |
| T.S. Holdings: one share; $2,850,538 of advances cleared by a $38,815 return and a $2,811,723 provision | Public Accounts 1979/80, B4, B8 | Confirmed; the share is the **entire issued capital** |
| Pacific Coach Lines: two shares | Public Accounts 1979/80, B4 | Confirmed; **entire issued capital**, held directly. The package's "two shares" undersells this |
| Thompson-Okanagan Transit $50,000 advance, no shares | Public Accounts 1979/80, B4, B8 | Confirmed |
| Chef Ready 33.33%; Kootenay 33.33% then 35.9% plus all Class B; South Peace 27.7%; provisions | Public Accounts 1977/78 B5; 1979/80 B5 (PDF p. 173), B8 | Confirmed |
| Surrey Farm Products Investments (formerly Panco) carried at $1 after a $4,799,999 return of capital | Public Accounts 1979/80, B4, B8 | Confirmed. Also: nonbudgetary revenue of **$14,800,000** from the "Sale of assets of Surrey Farm Products **Ltd.**" (PDF p. 160), a different name form from the shareholding's |
| British Columbia Food Exhibitions Ltd. (formerly Surrey Farm Products Investments), Food Pacific 86; Housing Corporation in voluntary liquidation; Pacific Coach Lines ceased 31 March 1984 | Public Accounts 1984/85 (OAG 1986 appendices), Appendix II (PDF p. 7), notes 9(c), (h), (i) (PDF pp. 20–21) | Confirmed |
| Auditor's report on T.S. Holdings and subsidiary companies tabled | Hansard, 25 January 1977 | Confirmed |
| Dunhill No. 73385 renamed Housing Corporation of BC on 1976-11-18; W.K.P. No. 91003 renamed Dunhill Development Corporation on 1976-11-26 | BC Gazette 1976 (archive.org OCR) | Confirmed, and the notices add **incorporation dates: 17 March 1967 (73385) and 19 December 1969 (91003)** |
| Dissolutions 1990-06-18 (73385) and 1989-06-12 (91003) | BC Gazette 1990 p. 9, 1989 p. 11 | Confirmed; both were **struck off and dissolved under s. 282 of the Company Act**, not dissolved voluntarily |
| BC Hydro's "Other Subsidiaries" | Board Governance Manual, Tab C.4 (PDF p. 44), dated December 2025 | The list has **15**, not 14: the package missed **1597798 BC Ltd.** |
| BC Ferries' Pacific Marine Leasing and Pacific Marine Holdings | BC Ferry Services financial statements 2025/26, note 1 | Confirmed |

Not re-read: the four Statistics Canada publications (publications.gc.ca refuses automated
downloads), the 1974/75 and 1975/76 Public Accounts (read by round 4), the 1979 Auditor General
report, OIC 3282/1976, the BC Hydro 1978/79 annual report and the 2024/25 summary financial
statements. Claims resting on them are marked in the records' locators and notes.

Found in the same schedules but not in the package: **Plateau Mills Ltd.** (97.5%, 8,775 shares,
1977 only), **Westcoast Transmission** (10.6%, 1977 only), the Province's $1,952,000 guarantee of
Kootenay Dehydrators' loans (Auditor General 1978, para. 8C.25), and **British Columbia Cellulose
Company**, wholly owned and listed every year, which has no atlas record.

## The verified follow-up: what was re-read here, and what it changed

Re-read during integration (archive.org text of the volumes, and page images where the text was
ambiguous): T.S. Holdings' subsidiary notes for 31 March **1976 (F176), 1977 (F202), 1978 (F221) and 1979
(F222–F224)**; the Fisher Developments → HCBC Construction notice (Gazette, 16 December 1976, No. 71787);
Crown Development Corporation's incorporation on 26 August 1975 (1975/76 F99); BC Cellulose's note 1 and
its 23 June 1975 purchase of 2.5% of Plateau Mills (1975/76 F8–F9); Panco's purchase on 17 February 1975,
its asset sale of 29 January 1979 and the $14.8 million dividend of 4 May 1979 (1978/79 F215); the
Housing Corporation's wind-up directive of 29 September 1978 and Venture Realty Ltd.'s sale effective
30 November 1978 (1978/79 F154); Crown Lumber's sale on 1 November 1976 (1977/78 F152); the 1984/85
wind-up of Surrey Farm Products Hatchery and Western Feed Co. (G55); and British Columbia Food
Exhibitions' dissolution on 19 June 1992 (Gazette, 9 July 1992, p. 840, checked on the page image).

Found here beyond the verified package: T.S. Holdings' **1976 and 1977** notes name the same three
subsidiaries, with former names (Thompson-Okanagan Transit **formerly Tweed Line Tours Ltd.**; Vancouver
Island Transit **formerly McArthur Transportation Limited**); its 1979 notes record that **on 24 July 1978
V I T Holdings sold its 98.5% of Vancouver Island Transportation Company to the Province**, and list only
the two transit companies by 31 March 1979. BC Cellulose's 1975 statements name its own subsidiaries,
Canadian Cellulose Company, Limited and Kootenay Forest Products Ltd. (acquired 28 February 1974).

Taken from the verified package without re-reading: the Statistics Canada page images (1975, 1976, 1978,
1984, 1985 and 72-007), the 1976/77 F133 and 1978/79 F154 and 1984/85 G247 ownership notes for W.K.P. and
Fisher, the 1976 wind-ups of Dunhill Homes, Dunhill Holdings and Georgia Park Holdings, the BC Hydro
1978/79 annual report, OIC 530/1978, the BC Cellulose statutes and repeal table, and the 1973 Statistics
Canada lead on Plateau Mills (text only, 97% as printed).

Corrections applied from it: HCBC Construction is Fisher Developments renamed, not another company; the
later Dunhill's registered name has no "Ltd."; the Statistics Canada appendix dates (31 December 1986 and
1987) are right, and the second page is 103, not 102; 72-007 vol. 23 no. 1 covers January–March 1981;
the $14.8 million was a dividend, not the sale price; "Surrey Farm Products Ltd." in the revenue schedule
is the same company under a short label.

## The follow-up: what was re-read here, and what it changed

Re-read during integration: Pacific Coach Lines' note 1 (1978/79 F190: incorporated **2 August 1978**,
inactive until **31 August 1978**, when it bought Vancouver Island Transportation's assets and began
operating); V I T Holdings' liquidation on **22 January 1979** (F224); the Gazette of 8 March 1979, p. 386
(**Panco Poultry → Surrey Farm Products Investments** and **Pacific Hatchery → Surrey Farm Products
Hatchery**, both **14 February 1979**, Nos. 63265 and 64184); the Gazette of 2 August 1990 (No. 178561
renamed 178561 B.C. Ltd. on 19 July 1990; Royal Victorian Holdings, No. 362538, took the name Pacific Coach
Lines Ltd.; No. 273925 Pacific Coach Lines (1984) Ltd. became numbered); OIC 631/1986 (BC Cellulose's
Repeal Act in force **31 March 1986**); and Kootenay Forest Products' note 1 (1975/76 F128: all shares
bought effective **1 March 1974**).

Taken from it without re-reading: the Gazette of 10 May 1979 (Venture Realty Ltd., No. 83729, renamed
Venture Realty Consultants Ltd. on 11 April 1979); Canadian Cellulose's 79 per cent from 29 June 1973 (F9,
F94); the dividend of BC Cellulose's holdings to the Province and the 81 per cent figure (1977/78 B5, B8);
the Finance Minister's 10 April 1978 statement dating the BCRIC transfer **9 March 1978**; Pacific Coach's
F193 note 9 and the 31 March 1979 shareholding (B4); and BCRIC's 1980 report (the 31 December 1980
amalgamation into a new Canadian Cellulose Company, Limited).

Corrections applied: **1 April 1979 is not Pacific Coach's start** (it is the Pacific Stage Lines
takeover); Panco is labelled Surrey Farm Products Investments from 14 February 1979; the asset sale of
29 January 1979 is under Panco's name; V I T Holdings ends on its liquidation; BC Cellulose ends on
31 March 1986, keeping the Accounts' 1 April as a separate assertion; Plateau Mills and Kootenay leave
public hands on 9 March 1978, by way of the Province, not directly from BC Cellulose.

## Four decisions after the follow-up

- **Swan Valley Foods is a body.** The Province owned all of it from a day after 31 March 1977 until it
  sold every share on 1 December 1977. Its start is kept to the year, "1977", which is what the evidence
  supports and invents no day. The diagram shows each year at 31 December, and Swan Valley stood at no
  year end, so it is not drawn there; it is in search, the timeline and the panels, and its events
  compile.
- **Panco's second rename has a window.** A body's name row may now carry `changedAfter`: the last day
  the old name is printed. The row's `from` is the latest day the rename had happened. Panco is
  "Surrey Farm Products Investments" from 14 February 1979, "British Columbia Food Exhibitions" from 17
  June 1985 (its statements under that name, audited that day), and between 31 March 1980 and then the
  panel says the rename's day is unknown (`nameTransition` in `snapshot.js`). The record carries its
  last name, as every body record does.
- **The spelling pairs are merged, as marked inferences** (`identity_review_required`). Panco's own
  statements list exactly two wholly owned subsidiaries, Pacific Hatchery Ltd. and Western Feed Co. Ltd.,
  in 1976, 1977, 1978 and 1979, so Statistics Canada's "Pacific Hatching" and "Western Feeds" are taken as
  those. The Housing Corporation's 1976 notes list "Venture Realty Ltd." among subsidiaries "all 100%
  owned", with "formerly" beside every renamed company and none beside it, so the 1974 "Ventures" is
  taken as the same company. Venture Realty now ends at its sale on 30 November 1978. B.C. Testing Farms
  never appears in Panco's statements and is left as printed.
- **BC Cellulose's dividend has a day.** Its own 1977 statements (note 10, subsequent events, 1977/78
  F23) say it declared the specie dividend of all its Canadian Cellulose, Kootenay and Plateau shares to
  the Province on 9 March 1978, the day of the BCRIC transfer. Kootenay's parent period ends that day.

Also from the same reading: United Provincial Investments is not among the seven companies the Housing
Corporation consolidated at 31 October 1975, so it left the group within its first year; and Dunhill
Homes, Dunhill Holdings and Georgia Park Holdings were wound up in 1976 (1976/77 F133, re-read).

## What changed

- `history/bodies-subsidiaries-2026-11-22.json`: nine Crown-corporation bodies:
  - **Housing Corporation of British Columbia** (Dunhill No. 73385): 1974–1990, two names, wind-up
    directive 1978.
  - **T.S. Holdings**: incorporated 1975 (year); last seen 1980.
  - **Pacific Coach Lines Limited** (No. 178561): incorporated 2 August 1978, operating 31 August 1978,
    Pacific Stage Lines taken over 1 April 1979; operations ceased 31 March 1984; last seen 1985; renamed
    178561 B.C. Ltd. in 1990.
  - **Panco Poultry / British Columbia Food Exhibitions**: bought 17 February 1975; renamed Surrey Farm
    Products Investments 14 February 1979 and British Columbia Food Exhibitions by 17 June 1985; dissolved
    19 June 1992.
  - **I.O.K. Poultry**: seen 1977; dissolved by 31 March 1980.
  - **Crown Development Corporation**: incorporated 26 August 1975; wound up by 31 March 1978.
  - **British Columbia Cellulose Company**: incorporated 15 March 1973 as British Columbia Cellulose
    Limited, renamed by its Act on 18 April 1973; dissolved 31 March 1986 (OIC 631/1986).
  - **Plateau Mills**: 97.5% Province and 2.5% BC Cellulose; seen 1975; to BCRIC on 9 March 1978.
  - **Swan Valley Foods**: wholly provincial from a day in 1977 until its sale on 1 December 1977.
- `history/sub-agencies-researched.json`, `gone`, 16 records:
  - Dunhill's eight 1974 subsidiaries: W.K.P. Construction / Dunhill Development Corporation and
    Fisher Developments / HCBC Construction, each observed under their parent at every year end read;
    Crown Lumber, sold 1976; Dunhill Homes, Dunhill Holdings and Georgia Park Holdings, wound up 1976;
    Ventures Realty, `requires_reconciliation`.
  - Panco's three 1975 subsidiaries.
  - T.S. Holdings' three: V I T Holdings (liquidated 22 January 1979), Thompson-Okanagan Transit and
    Vancouver Island Transit, 1976–1979.
  - Kootenay Forest Products, under BC Cellulose from 1 March 1974 to the BCRIC transfer.
  - Peace Power Constructors, under BC Hydro in 1986 and 1987.
- `atlas/events-subsidiaries-2026-11-22.json`: 67 events.
- `censuses/crown-subsidiaries-2026-11-22.json`: 15 source rosters, 124 rows, including T.S. Holdings'
  1978 consolidation note and BC Cellulose's 1975 holdings. The roster card (`src/government/AtlasCards.jsx`) shows a census's and roster's
  own title.
- `identity/collection-2026-10-22/inventory.json`: the eight bodies, as `unresolved` (no logo search yet).

## What was held

- **Chef Ready, Kootenay Dehydrators and South Peace** (minority investments): census rows; their
  events are in `held-events.json`.
- **Canadian Cellulose Company, Limited**: 79 per cent, a majority, not wholly owned. A census row
  and events on BC Cellulose.
- **The five companies 98.24–98.5% owned by V I T Holdings** (Vancouver Island Transportation, Vancouver
  Island Coach Lines, Gray Line & Empress, Imperial Charter, BC Parlour Car Tours): "directly or through
  a subsidiary", so no direct parent can be drawn. Census rows and event notes.
- **Techwest, Duke Point Terminals and the Discovery companies**: their parents are not drawn or not
  settled. Census rows.
- **BC Hydro's other subsidiaries, BC Ferries' and the universities'**: as before, census rows.

## Known limits of what is drawn

- Panco is labelled Surrey Farm Products Investments from 1980 to 1984 with the rename's window shown,
  since either name may be right in those years.
- A subsidiary observed only at year ends is drawn under its parent in those years and apart in the
  years between.
- None of the eight bodies has a responsible ministry, so all are drawn in the lane for bodies with none.

## Checking the change on its own

Other sessions were editing this checkout at the same time (BC Enterprise, SuperHost, parties, tourism,
and `GovernmentPanel.jsx`). The subsidiary change was checked apart from them: HEAD exported, only the
subsidiary files copied in (with just the four-line `nameTransition` notice applied to HEAD's
`GovernmentPanel.jsx`), the government, collecting and collected-marks builds run, then the tests and
`check:government`. Result: 1,148 tests, 1,141 passed, 6 skipped, 1 failed: the school-district roster
test, which runs `git ls-tree` and fails only because an export is not a git repository; it passes in
the checkout. `check:government` reproduces byte-for-byte. Every generated government file and
`collectingData.js` are byte-identical to the checkout's; `src/gallery/collectedData.js` differs, because
the checkout's also carries the other sessions' SuperHost specimens, so a subsidiary-only commit needs the
clean build of that one file, and only the notice hunk of `GovernmentPanel.jsx`.
