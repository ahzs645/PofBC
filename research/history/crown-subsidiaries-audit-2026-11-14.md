# Crown corporation subsidiaries audit (2026-11-14)

**Question:** Does the repo include the companies that B.C. Crown corporations own outright, or own in part, both current and historical (1950s to today)?

**Short answer:** No. The repo covers the modern subsidiaries well (`sub-subsidiaries.json`). The historical ones are almost all missing. This audit found 72 subsidiaries, joint ventures and partly-owned holdings. **12 were in the repo and 60 were not** (49 of the missing sourced, 11 leads). None of the British Columbia Development Corporation’s (BCDC) subsidiaries were in the repo.

**Follow-up, same day:** BCDC’s four subsidiary companies are now in `sub-agencies-researched.json` (`gone`), checked against the consolidation notes of its 1983, 1985 and 1986 annual reports and BC Registries’ OrgBook, which gives incorporation dates of 2 Aug 1977 (First Capital City, BC0164330), 29 Nov 1979 (Lonsdale Quay Development, BC0200730) and 15 May 1985 (Westminster Quay Public Market, BC0292596), all now historical companies with no dissolution date. Duke Point Development Limited is not in OrgBook by that name. With British Columbia Ferry Services Inc., which was already a body, that makes **17 in the repo and 55 missing** (45 sourced, 10 leads). Two of the “problems” below were checked and are not errors (see the notes on 1 and 4).

Machine-readable version: `research/history/crown-subsidiaries-audit-2026-11-14.json`. Each record there carries a URL and a page locator for every claim.

## Method and sources

1. **Repo check.** I extracted every `id`/`name` pair from `src/government/historyData.js` (549 nodes; subsidiaries use the `sub-` prefix), `src/government/currentData.js` and `src/gallery/collectingData.js`. I also grepped `research/history/*.json` for each candidate name before marking it missing. Where a company is named only in a gaps note or in prose, it is marked **missing** and the note says so.
2. **BCDC annual reports** on archive.org (PDFs run through `pdftotext -layout`; "PDF p." means the page of the PDF file):
   - 9th annual report, FY ending 1983-03-31: [micro_IA40243510_1434](https://archive.org/details/micro_IA40243510_1434)
   - 10th annual report, FY 1984: [micro_IA40243512_1344](https://archive.org/details/micro_IA40243512_1344)
   - 11th annual report, FY 1985: [micro_IA40243514_1461](https://archive.org/details/micro_IA40243514_1461)
   - Annual report 1985-86: [micro_IA40243211_0084](https://archive.org/details/micro_IA40243211_0084)

   Note 1 ("Consolidation") of each report names the subsidiaries.
3. **BC Ombudsman Special Report No. 9** ([PDF](https://bcombudsperson.ca/wp-content/uploads/2025/08/Special-Report-No-09-Supreme-Court-of-Canada-Judgment.pdf)), PDF p.24, 26 and 48. It is the source for First Capital City's incorporation date and its wholly-owned status.
4. **OAG 1986 report, part 2 appendices** ([PDF](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf)):
   - Appendix II (PDF p.7) lists the public bodies the Auditor General audits.
   - The 1984/85 Public Accounts notes on investments in Crown corporations are at PDF p.19-21 and p.79-80.
   - Subsequent events are at PDF p.87.

   These appendices list Crown corporations, not each Crown's subsidiaries. The exception is BC Rail's.
5. **BC Enterprise Corporation records schedule (ORCS 170469)** ([PDF](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/information-management-technology/records-management/orcs/bcec_orcs_170469.pdf)). PDF p.4 confirms that BCEC took over BCDC's and BC Place Ltd.'s "various subsidiary organizations". PDF p.5 and p.14 name the land projects: Lonsdale Quay, Westminster Quay, Whistler, Songhees, Duke Point and Tilbury.
6. **Crown annual reports on archive.org** (OCR `_djvu.txt` files):
   - BC Hydro: 1963, 1965, 1970, 1975, 1979, 1981, 1990, 2008 and 2013
   - BC Rail: 1978, 1980, 1987, 1991, 2000 and 2003
   - BCRIC: 1980 (the 1982 and 1984 reports were downloaded but not read)
   - ICBC: 1975, 1980, 1984, 1985 and 1987
   - BC Ferries: 1982-83, 1988-89 and 2001-02
   - BC Buildings Corporation (BCBC): 1986, 1990-91 and 2001-02
   - BC Petroleum Corporation: 1987-88
   - BCLC: 1987 and 1999-2000
   - BC Systems: 1988-89
   - PavCo: 1988-89 and 2000-01

   Exact item ids are in the JSON.
7. **2024/25 Public Accounts supplementary financial statements** (`www2.gov.bc.ca/.../public-accounts/2024-25/sup-e/<crown>-fs-2024-25.pdf`) for:
   - Columbia Basin Trust (CBT)
   - Columbia Power Corporation (CPC)
   - BC Hydro
   - BC Transit
   - PavCo
   - BC Housing
   - Knowledge Network
   - Forestry Innovation Investment (FII)
   - InBC (scanned; no text layer)
8. **Other sources:**
   - North Shore News texts (nsdl.arcabc.ca), 1979 and 1983
   - The CIPO trademark database
   - UNBC archives

Out of scope: the investee holdings of BCI and pension funds, and ICBC's 63 nominee property-holding companies. These are investment holdings, not operating subsidiaries.

## BCDC (British Columbia Development Corporation, 1973-1987; repo id `bc-development-corporation`)

| Name | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|
| The First Capital City Development Company Limited | wholly-owned | 1977-08-02 | `sub-first-capital-city-development-company` (added 2026-11-14) | sourced | [1](https://bcombudsperson.ca/wp-content/uploads/2025/08/Special-Report-No-09-Supreme-Court-of-Canada-Judgment.pdf) PDF p.24 ('its wholly owned subsidiary, First Capital City Development Company Limited'); PDF p.26 ('August 2, 1977, First Capital was incorporated'); PDF p.48; [2](https://archive.org/details/micro_IA40243510_1434) PDF p.11, Summary of accounting policies, Consolidation; [3](https://archive.org/details/micro_IA40243514_1461) PDF p.13 (Westminster Quay 'implemented by a subsidiary ... as a cooperative venture' with the City of New Westminster); [4](https://archive.org/details/micro_IA40243211_0084) PDF p.16 (in partnership with the City of New Westminster); PDF p.18 Consolidation Note: Developer of Westminster Quay, New Westminster. Passed to BC Enterprise Corporation with BCDC's other subsidiaries on 1987-03-31 (BCEC ORCS p.4 speaks of BCDC's 'various subsidiary organizations'); end date not found. |
| Lonsdale Quay Development Company Limited | wholly-owned | 1979 | `sub-lonsdale-quay-development-company` (added 2026-11-14) | sourced | [1](https://nsdl.arcabc.ca/_flysystem/repo-service/2025-04/165995-Extracted%20Text.txt) North Shore News, 8 May 1983, p.B4: 'a wholly owned subsidiary of the British Columbia Development Corporation, was set up in 1979'; [2](https://archive.org/details/micro_IA40243510_1434) PDF p.11 Consolidation; PDF p.20 ('Lonsdale Quay Development Company (a sub[sidiary])'); [3](https://archive.org/details/micro_IA40243512_1344) PDF p.17 Consolidation; [4](https://archive.org/details/micro_IA40243514_1461) PDF p.15 Consolidation; [5](https://archive.org/details/micro_IA40243211_0084) PDF p.18 Consolidation Note: Developer of the 25-acre Lonsdale Quay site, North Vancouver. End date not found. |
| Duke Point Development Limited | wholly-owned (consolidated subsidiary; percentage not stated) | not found | `sub-duke-point-development` (added 2026-11-14) | sourced | [1](https://archive.org/details/micro_IA40243510_1434) PDF p.11 Consolidation; [2](https://archive.org/details/micro_IA40243512_1344) PDF p.17 Consolidation; [3](https://archive.org/details/micro_IA40243514_1461) PDF p.15 Consolidation; [4](https://archive.org/details/micro_IA40243211_0084) PDF p.18 Consolidation; PDF p.16 (Duke Point Industrial Park, Nanaimo, developed 1975-1982) Note: Industrial park and shipping terminal near Nanaimo. Incorporation and end dates not found. |
| Westminster Quay Public Market Ltd. | joint-venture (subsidiary in 1985; joint venture with Laing Properties Ltd. by 1986 (shares not stated)) | c.1984-85 | `sub-westminster-quay-public-market` (added 2026-11-14) | sourced | [1](https://archive.org/details/micro_IA40243514_1461) PDF p.13: 'Westminster Quay Public Market Ltd, a new Development Corporation subsidiary, is scheduled to begin construction in 1985'; 'will ultimately be privatized'; [2](https://archive.org/details/micro_IA40243211_0084) PDF p.17: market 'being built and operated on a joint venture basis with Laing Properties Ltd.'; 'Laing Properties has agreed to purchase our remaining interest' Note: Not listed in the consolidation note, so probably held as an investment. Market opened mid-July 1986. |
| British Columbia Museum of Transportation, Science and Industry | administered | not found | missing | sourced | [1](https://archive.org/details/micro_IA40243512_1344) PDF p.16: 'a non-profit society administered by the Development Corporation' Note: Collected historic vehicles for display at Expo 86. Society incorporation date not found. |
| British Columbia Film Centre / The Bridge Studios | administered | 1987 | missing | sourced | [1](https://ised-isde.canada.ca/cipo/trademark-search/0569716) CIPO 0569716 THE BRIDGE: owner British Columbia Development Corporation; filed 1986-09-22, registered 1987-11-06 (TMA333795), cancelled by owner 1990-07-13; [2](https://ised-isde.canada.ca/cipo/trademark-search/0903009) CIPO 0903009 BRITISH COLUMBIA FILM CENTRE & Design: official mark s.9(1)(n)(iii), requested by British Columbia Development Corporation, 1987; [3](https://archive.org/details/micro_IA40243211_0084) PDF p.7 (plans for a studio facility for motion-picture production); [4](https://cinemacanada.athabascau.ca/index.php/cinema/article/download/3452/3491.pdf) Cinema Canada c.1985-86 (BCDC involvement in the studio project); lead Note: A BCDC-owned project and brand. No separate company was found. Later held by BCEC and then PavCo (lead). |
| Lonsdale Quay Market (Lonsdale Quay Market Corporation) | partly-owned (BCDC 'retains a financial interest'; nature and size unstated) | 1984-85 | missing | lead | [1](https://archive.org/details/micro_IA40243514_1461) PDF p.14: 'Another private sector developer, Lonsdale Quay Market Corporation, began construction of an integrated public market, entertainment, and hotel complex'; [2](https://archive.org/details/micro_IA40243211_0084) PDF p.17: 'developed by Intrawest Properties ... We retain a financial interest in the project'; [3](https://nsdl.arcabc.ca/_flysystem/repo-service/2025-03/5404-Extracted%20Text.txt) Lonsdale Quay bulletin vol.1 no.3 (Intrawest Properties Ltd. to develop the market) Note: Not a BCDC subsidiary: a private developer (Intrawest). The 1990 trademark assignment named in the brief was not checked. |
| Pacific Isotopes and Pharmaceuticals Ltd. | partly-owned (interest of unstated size) | ended by 1983-03-31 | missing | sourced | [1](https://archive.org/details/micro_IA40243510_1434) PDF p.11: 'During the year, the Corporation transferred its interest in Pacific Isotopes and Pharmaceuticals Ltd. to The Terry Fox Medical Research Foundation' |

Other BCDC items that are not separate companies:
- **Property from the BC Harbours Board, FY1983-84.** BCDC received $12,087,952 of land and buildings and issued 121,183 shares to the Province in exchange ([BCDC 1984](https://archive.org/details/micro_IA40243512_1344) PDF p.21 and 23). The repo already links `bc-harbours-board` to BCDC through `serviceSuccessorIds`, so this is covered.
- **Facilities and projects BCDC ran directly:**
  - Marine Technology Centre, Sidney ([BCDC 1985-86](https://archive.org/details/micro_IA40243211_0084) PDF p.16)
  - Tilbury Industrial Park, Delta
  - Prince Rupert industrial park
- **Assets passed on.** All BCDC subsidiaries passed to `bc-enterprise-corporation` on 1987-03-31. The Westminster Quay lots were sold in 1988 (Hansard, 20 Apr 1989; lead).

## BC Hydro

| Name | Parent | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|---|
| British Columbia Electric Railway Company Limited | bc-electric-company-crown | wholly-owned | not found | missing | sourced | [1](https://archive.org/details/McGillLibrary-632604-27827) BC Hydro 1964/65 annual report, financial statements Note 5 (Taxes on income): 'British Columbia Electric Company Limited and its wholly-owned subsidiary British Columbia Electric Railway Company Limited' Note: Held by BC Electric after the 1961 takeover and so by the Crown; folded into BC Hydro's operations. Dates not established here. |
| International Power and Engineering Consultants Limited | bc-hydro | wholly-owned | not found | missing | sourced | [1](https://archive.org/details/McGillLibrary-632608-27821) BC Hydro 1962/63 annual report, balance sheet: 'Shares of International Power and Engineering Consultants Limited, at cost ... 1,200,000'; [2](https://archive.org/details/McGillLibrary-632593-27842) BC Hydro 1969/70 annual report, Construction: 'International Power and Engineering Consultants, Limited, a wholly owned subsidiary of B.C. Hydro' Note: Design and construction engineering subsidiary. Formation and end dates not found. |
| Powertech Labs Inc. | bc-hydro | wholly-owned | 1989 | `sub-powertech-labs` | sourced | [1](https://archive.org/details/McGillLibrary-632592-27884) BC Hydro 1989/90 annual report, 'Subsidiary revenue': 'In 1989, Powertech Labs, Westech Information Systems and Western Integrated Technologies were established as subsidiaries'; consolidation note Note: The repo gives 1988; the 1990 annual report says it was established as a subsidiary in 1989. |
| Westech Information Systems Inc. | bc-hydro | wholly-owned | 1989 | missing | sourced | [1](https://archive.org/details/McGillLibrary-632592-27884) 1989/90 annual report, Subsidiary revenue; Consolidation note |
| Western Integrated Technologies Inc. | bc-hydro | wholly-owned | 1989 | missing | sourced | [1](https://archive.org/details/McGillLibrary-632592-27884) 1989/90 annual report, Subsidiary revenue; Consolidation note |
| British Columbia Power Export Corporation (Powerex Corp.) | bc-hydro | wholly-owned | 1988 | `sub-powerex` | sourced | [1](https://archive.org/details/McGillLibrary-632592-27884) 1989/90 Consolidation note; [2](https://archive.org/details/micro_IA40244213_0843) 2012/13 annual report, note 1 (Powerex) |
| British Columbia Hydro International Limited | bc-hydro | wholly-owned | not found | missing | sourced | [1](https://archive.org/details/McGillLibrary-632592-27884) 1989/90 Consolidation note: 'Principal subsidiaries ... all of which are wholly-owned' |
| Columbia Estate Company, Limited | bc-hydro | wholly-owned | not found | missing | sourced | [1](https://archive.org/details/McGillLibrary-632592-27884) 1989/90 Consolidation note |
| Columbia Hydro Constructors Ltd. | bc-hydro | wholly-owned | not found | `sub-columbia-hydro-constructors` | sourced | [1](https://archive.org/details/micro_IA40244213_0843) 2012/13 annual report, note 1: 'principal wholly-owned operating subsidiaries Powerex, Powertech Labs Inc., and Columbia Hydro Constructors Ltd.' |
| Waneta Dam and Generating Facility (interest) | bc-hydro | joint-venture (one-third (joint operation with Teck)) | not found | missing | sourced | [1](https://archive.org/details/micro_IA40244213_0843) 2012/13 annual report, note 1: 'BC Hydro's one third interest in the Waneta Dam and Generating Facility (Waneta), a joint operation' Note: An asset interest, not a company. Lead, unverified: BC Hydro bought Teck's two-thirds in 2018. |
| BCHPA Captive Insurance Company Ltd. | bc-hydro | wholly-owned | not found | `sub-bchpa-captive-insurance` | sourced | `research/history/sub-subsidiaries.json` existing repo record |
| Tongass Power and Light Company | bc-hydro | wholly-owned | not found | `sub-tongass-power-and-light` | sourced | `research/history/sub-subsidiaries.json` existing repo record |

## BC Rail

| Name | Parent | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|---|
| BC Rail Ltd. | bc-railway-company | wholly-owned (common shares 100% in the group (25% BCR, 75% BCR Properties); public preferred shares from 1984) | 1984 to 2004-07-14 | missing | sourced | [1](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf) PDF p.20 (Public Accounts 1984/85 p.B16): June 1984 issue of Series A preferred shares; 'common shares of BC Rail Ltd. are owned 25% by the Railway and 75% by BCR Properties Ltd.'; [2](https://archive.org/details/micro_IA40243217_0622) BC Rail 1987 annual report: group structure and Consolidation note Note: The operating railway company. The end date (sale to CN) is from the repo's own bc-railway-company description. Named only in the bodies.json gaps note. |
| BCR Properties Ltd. | bc-railway-company | wholly-owned | not found | `sub-bcr-properties` | sourced | [1](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf) PDF p.20: 'The Railway holds 100% of the common shares of BCR Properties Ltd.' |
| BCR Marine Ltd. | bc-railway-company | wholly-owned (operating business of the group; percentage not stated) | not found | missing | sourced | [1](https://archive.org/details/micro_IA40243304_1242) BCR Group 2000 annual report: group structure; directors' list 'BCR Marine Ltd. and ... Wharves Limited Partnership' Note: Grouped Canadian Stevedoring, Casco Terminals and Vancouver Wharves. |
| Vancouver Wharves (Vancouver Wharves Limited Partnership) | bc-railway-company | wholly-owned (percentage not stated) | not found | missing | sourced | [1](https://archive.org/details/micro_IA40243304_1242) 2000 annual report: BCR Marine 'its first full year of operating Canadian Stevedoring, Casco Terminals and Vancouver Wharves'; directors' list Note: Named in the bodies.json gaps note but has no node. |
| Canadian Stevedoring Company Limited | bc-railway-company | wholly-owned | acquired c.1999 | missing | sourced | [1](https://archive.org/details/micro_IA40243304_1242) 2000 annual report: cash-flow line 'Acquisition of Canadian Stevedoring Company Limited'; its own board listed |
| Casco Terminals | bc-railway-company | wholly-owned (percentage not stated) | not found | missing | lead | [1](https://archive.org/details/micro_IA40243304_1242) 2000 annual report, BCR Marine section |
| Finlay Navigation Limited Partnership | bc-railway-company | partly-owned (50% until 2000-09-01, then 100%) | not found | missing | sourced | [1](https://archive.org/details/micro_IA40243304_1242) 2000 annual report, note: 'Effective September 1, 2000, the Company acquired the remaining 50% interest in Finlay Navigation Limited Partnership to increase its interest to 100%' |
| BCR Ventures Inc. | bc-railway-company | wholly-owned | 1996 | missing | sourced | [1](https://archive.org/details/micro_IA40243304_1242) 2000 annual report: 'a joint venture investment company, BCR Ventures Inc.'; 'Established in 1996' Note: Took joint-venture stakes in resource projects along the line. |
| BC Rail Partnership (BCR Partnership) | bc-railway-company | partly-owned | ended 2004-07-14 | missing | lead | `src/government/historyData.js` bc-railway-company description: 'CN acquired the BC Rail Ltd. operating subsidiary and BCR Partnership units at closing on 14 July 2004' |

## BCRIC and the 1970s forest holdings

| Name | Parent | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|---|
| British Columbia Cellulose Company | Province of British Columbia | wholly-owned | 1973 | missing | sourced | [1](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf) PDF p.19 note 9 (Crown corporation investment); PDF p.20 note 9(b): British Columbia Cellulose Company Repeal Act passed in 1983/84, not yet in force; [2](https://lims.leg.bc.ca/hdms/file/Debates/30th2nd/30p_02s_730416a.htm) Hansard 16 Apr 1973: second reading of the British Columbia Cellulose Company Act Note: A Crown holding company for the Province's Canadian Cellulose shares (about 79%, lead). It has no node in the repo. |
| Canadian Cellulose Company, Limited | bc-resources-investment-corporation | partly-owned (Province (through BC Cellulose Co.) 1973-79; BCRIC 81% in 1979, 100% from 1980) | 1973 | missing | sourced | [1](https://nsdl.arcabc.ca/_flysystem/repo-service/2025-06/36475-Extracted%20Text.txt) North Shore News, Jan 1979, p.20: BCRIC assets '9,888,203 shares, or 81 per cent' of CanCel; [2](https://archive.org/details/McGillLibrary-637355-28052) BCRIC 1980 annual report: remaining 19% bought, '100 per cent'; [3](https://search.nbca.unbc.ca/index.php/columbia-cellulose-limited) UNBC archives: taken over by the Province in 1973, becoming Canadian Cellulose; renamed BC Timber Ltd. in 1981 |
| Kootenay Forest Products Ltd. | bc-resources-investment-corporation | wholly-owned | ended 1980 | missing | sourced | [1](https://nsdl.arcabc.ca/_flysystem/repo-service/2025-06/36475-Extracted%20Text.txt) Jan 1979 p.20: '100 per cent of the common shares'; [2](https://archive.org/details/McGillLibrary-637355-28052) 1980 annual report: amalgamated with Plateau Mills and CanCel Note: Provincially owned before 1979; the acquisition date was not found. |
| Plateau Mills Ltd. | bc-resources-investment-corporation | wholly-owned | ended 1980 | missing | sourced | [1](https://nsdl.arcabc.ca/_flysystem/repo-service/2025-06/36475-Extracted%20Text.txt) Jan 1979 p.20: '100 per cent of the common shares of Plateau Mills Ltd.'; [2](https://archive.org/details/McGillLibrary-637355-28052) 1980 annual report: amalgamated into CanCel |
| Westcoast Transmission Company Limited (stake) | bc-resources-investment-corporation | partly-owned (10% (1979); 9.6% (1980)) | not found | missing | sourced | [1](https://nsdl.arcabc.ca/_flysystem/repo-service/2025-06/36475-Extracted%20Text.txt) Jan 1979 p.20: '3,471,375 shares, or 10 per cent'; [2](https://archive.org/details/McGillLibrary-637355-28052) 1980 annual report: 9.6 per cent |
| B.C. Coal Ltd. (formerly Kaiser Resources Ltd.) | bc-resources-investment-corporation | partly-owned (66%) | 1980-10 | missing | sourced | [1](https://archive.org/details/McGillLibrary-637355-28052) 1980 annual report: 66 per cent acquired October 1980; Japanese shareholders keep one-third |
| Westshore Terminals Ltd. | bc-resources-investment-corporation | partly-owned (indirect, through 66%-owned B.C. Coal) | not found | missing | sourced | [1](https://archive.org/details/McGillLibrary-637355-28052) 1980 annual report: 'B.C. Coal's wholly-owned subsidiary, Westshore Terminals Ltd.' |
| MacMillan Bloedel Limited (stake) | bc-resources-investment-corporation | partly-owned (20%) | 1980 | missing | sourced | [1](https://archive.org/details/McGillLibrary-637355-28052) 1980 annual report: 20 per cent interest acquired |

## ICBC

| Name | Parent | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|---|
| Canadian Northern Shield Insurance Company | icbc | wholly-owned | 1984 to 1985-02-18 | missing | sourced | [1](https://archive.org/details/McGillLibrary-634107-40025) ICBC 1984 annual report, Report of the Board: 'the Corporation chartered a wholly-owned subsidiary, Canadian Northern Shield Insurance Company'; sold to The Cumis Group on 18 Feb 1985; [2](https://archive.org/details/McGillLibrary-634108-40028) ICBC 1985 annual report, notes: general insurance assets 'transferred to a subsidiary company which was sold February 18, 1985' Note: Took over ICBC's General Insurance Division in January 1985. |

## BC Petroleum Corporation

| Name | Parent | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|---|
| British Columbia Gas Corporation | bc-petroleum-corporation | wholly-owned (consolidated subsidiary; percentage not stated) | not found | missing | sourced | [1](https://archive.org/details/micro_IA40243217_1258) BC Petroleum Corporation 1987/88 annual report, Note 2 Consolidation: 'the Corporation's subsidiary, British Columbia Gas Corporation'; Note 5 |

## BCLC

| Name | Parent | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|---|
| B.C. Lottotech International Inc. | bclc | wholly-owned | not found | `sub-bc-lottotech-international` | sourced | [1](https://archive.org/details/micro_IA40243304_1664) BCLC 1999/2000 annual report, note 1(a)(ii): 'a wholly owned subsidiary' |
| Inter-Provincial Lottery Corporation (provincial interest) | bclc | partly-owned (one of several provincial members) | not found | missing | lead | [1](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf) PDF p.20 note 9(d): BCLC 'represents the interest of the Province in the Inter-Provincial Lottery Corporation games' |
| Western Canada Lottery Foundation (provincial membership) | Province of British Columbia | joint-venture | ended 1985-03-29 | missing | sourced | [1](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf) PDF p.20 note 9(d): Province withdrew by agreement of 29 Mar 1985 Note: Named in the bodies.json gaps note but has no node. |

## Columbia Basin Trust and Columbia Power

| Name | Parent | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|---|
| CBT Commercial Finance Corp. | columbia-basin-trust | wholly-owned | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) 2024/25 FS, PDF p.12 note 2(i): 'wholly owned and controlled by the Trust and are fully consolidated' |
| CBT Arrow Lakes Power Development Corp. | columbia-basin-trust | wholly-owned | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) 2024/25 FS, PDF p.12 note 2(i): 'wholly owned and controlled by the Trust and are fully consolidated' |
| CBT Brilliant Expansion Power Corp. | columbia-basin-trust | wholly-owned | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) 2024/25 FS, PDF p.12 note 2(i): 'wholly owned and controlled by the Trust and are fully consolidated' |
| CBT Power Corp. | columbia-basin-trust | wholly-owned | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) 2024/25 FS, PDF p.12 note 2(i): 'wholly owned and controlled by the Trust and are fully consolidated' |
| CBT Property Corp. | columbia-basin-trust | wholly-owned | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) 2024/25 FS, PDF p.12 note 2(i): 'wholly owned and controlled by the Trust and are fully consolidated' |
| CBT Waneta Expansion Power Corp. | columbia-basin-trust | wholly-owned | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) 2024/25 FS, PDF p.12 note 2(i): 'wholly owned and controlled by the Trust and are fully consolidated' |
| CBT Real Estate Investment Corp. | columbia-basin-trust | wholly-owned | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) 2024/25 FS, PDF p.12 note 2(i): 'wholly owned and controlled by the Trust and are fully consolidated' |
| Columbia Basin Development Corporation | columbia-basin-trust | wholly-owned | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) 2024/25 FS, PDF p.12 note 2(i): 'wholly owned and controlled by the Trust and are fully consolidated' |
| Columbia Basin Broadband Corporation | columbia-basin-trust | wholly-owned | 2011 | `sub-columbia-basin-broadband-corporation` | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) PDF p.12 note 2(i) |
| Arrow Lakes Power Corporation | columbia-power | joint-venture (50% Columbia Power / 50% CBT (through a CBT subsidiary)) | not found | `sub-arrow-lakes-power-corporation` | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-power-corporation-fs-2024-25.pdf) 2024/25 FS, PDF p.16-17 note 4: 'All four corporations are jointly owned on a 50/50 basis by Columbia Power and the Trust'; [2](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) PDF p.12, 22 Note: The repo models this as a Columbia Power subsidiary only; it is a 50/50 joint venture with CBT. |
| Brilliant Power Corporation | columbia-power | joint-venture (50% Columbia Power / 50% CBT (through a CBT subsidiary)) | not found | `sub-brilliant-power-corporation` | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-power-corporation-fs-2024-25.pdf) 2024/25 FS, PDF p.16-17 note 4: 'All four corporations are jointly owned on a 50/50 basis by Columbia Power and the Trust'; [2](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) PDF p.12, 22 Note: The repo models this as a Columbia Power subsidiary only; it is a 50/50 joint venture with CBT. |
| Brilliant Expansion Power Corporation | columbia-power | joint-venture (50% Columbia Power / 50% CBT (through a CBT subsidiary)) | not found | `sub-brilliant-expansion-power-corporation` | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-power-corporation-fs-2024-25.pdf) 2024/25 FS, PDF p.16-17 note 4: 'All four corporations are jointly owned on a 50/50 basis by Columbia Power and the Trust'; [2](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) PDF p.12, 22 Note: The repo models this as a Columbia Power subsidiary only; it is a 50/50 joint venture with CBT. |
| Waneta Expansion Power Corporation | columbia-power | joint-venture (50% Columbia Power / 50% CBT (through a CBT subsidiary)) | 2019-04-17 | `sub-waneta-expansion-power-corporation` | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-power-corporation-fs-2024-25.pdf) 2024/25 FS, PDF p.16-17 note 4: 'All four corporations are jointly owned on a 50/50 basis by Columbia Power and the Trust'; [2](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) PDF p.12, 22 Note: The repo models this as a Columbia Power subsidiary only; it is a 50/50 joint venture with CBT. |
| Waneta Expansion Limited Partnership | columbia-power | partly-owned (Columbia Power 32.5%, CBT 16.5%, Fortis Inc. 51%) | ended 2019-04-17 | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-power-corporation-fs-2024-25.pdf) PDF p.16 note 4: Fortis 51%, Columbia Power 32.5%, Trust 16.5%; Fortis's 51% bought 17 Apr 2019 and replaced by WEPC Note: Named in repo text only; no node. |
| Mount St. Francis | columbia-basin-trust | joint-venture (50%) | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) PDF p.12 'Real estate - 50% interest'; PDF p.17, p.21 (Nelson housing facility) |
| Red Mountain Hostel | columbia-basin-trust | partly-owned (75%, reduced in FY2025) | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/columbia-basin-trust-fs-2024-25.pdf) PDF p.13 '(75% interest) is a GBE'; PDF p.20: partner's contributions lowered the Trust's share in FY2025 |

## Other current Crowns

| Name | Parent | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|---|
| Vancouver Convention Centre Expansion Project Ltd. | Province of British Columbia | wholly-owned | ended 2008-04-01 | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/bc-pavilion-corporation-fs-2024-25.pdf) 2024/25 FS note 1: PavCo formed 2008-04-01 by amalgamating the former B.C. Pavilion Corporation and VCCEP Note: Amalgamated into bc-pavilion-corporation. Named in repo text only. Its ownership before 2008 was not checked. |
| Knowledge-West Communications Corporation | knowledge-network | wholly-owned | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/knowledge-network-corporation-fs-2024-25.pdf) 2024/25 FS: 'wholly-owned subsidiary, Knowledge-West' / '100% owned subsidiary, KWCC' Note: Left out on purpose as inactive (sub-subsidiaries.json gaps). |
| 0939031 B.C. Ltd. | forestry-innovation-investment | wholly-owned | not found | missing | sourced | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/forestry-innovation-investment-fs-2024-25.pdf) 2024/25 FS note 1 Note: Left out on purpose as non-operating; it is the co-owner of FII India. |
| Unnamed consolidated subsidiary of BC Housing | bc-housing | wholly-owned | not found | missing | lead | [1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/bc-housing-management-commission-fs-2024-25.pdf) 2024/25 FS, auditor's report PDF p.4: 'British Columbia Housing Management Commission and its subsidiary' Note: The text layer does not name it (scanned notes). Identify it. |

## BC Ferries and transit

| Name | Parent | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|---|
| Catamaran Ferries International Inc. | bc-ferry-corporation | wholly-owned | not found | missing | lead | [1](https://www.marinelink.com/amp/news/maritime/catamaran-ferries-international) MarineLink news: BC Ferries' wholly owned subsidiary that built the PacifiCats; wound up c.2000 |
| British Columbia Ferry Services Inc. | bc-ferry-authority | wholly-owned | 2003-04-02 | `bc-ferry-services-inc` (body) | lead | `src/government/historyData.js` bc-ferry-corporation.becameId = 'bc-ferry-services-inc', which has no node; [2](https://www.courthouselibrary.ca/node/1752) BC Ferries corporate history Note: BC Ferry Authority holds the voting share (lead). This is the dangling id. |
| British Columbia Rapid Transit Company Ltd. | bc-transit | wholly-owned | c.1985 | missing | lead | [1](https://free.bcpublications.ca/civix/document/id/consol9/consol9/98030_01) Greater Vancouver Transportation Authority Act (1998): lists BCRTC among the authority's subsidiaries after transfer; [2](https://www.translink.ca/about-us/about-translink/operating-companies/british-columbia-rapid-transit-company) TransLink: operates SkyTrain and West Coast Express Note: Founded 1985 per company profiles (unverified). It went to the GVTA (TransLink) around 1999 and so left the provincial reporting entity. |
| West Coast Express Ltd. | bc-transit | wholly-owned | c.1995 | missing | lead | [1](https://www.translink.ca/about-us/about-translink/operating-companies/british-columbia-rapid-transit-company) TransLink page (now operated by BCRTC) |
| Rapid Transit Project 2000 Ltd. | Province of British Columbia | wholly-owned | not found | missing | lead | [1](https://en.wikipedia.org/wiki/History_of_the_SkyTrain) History of the SkyTrain: RTP 2000, a Crown corporation that built the Millennium Line; [2](https://council.vancouver.ca/001017/present1.htm) City of Vancouver 17 Oct 2000: responsible for Millennium Line design and construction Note: Parent (BC Transit or the Province) not confirmed. |

## Province-held companies (1985 Public Accounts) with no node

| Name | Parent | Relationship | Dates | In repo? | Conf. | Sources / notes |
|---|---|---|---|---|---|---|
| British Columbia Food Exhibitions Ltd. (formerly Surrey Farm Products Investments Ltd.) | Province of British Columbia | wholly-owned | not found | missing | sourced | [1](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf) PDF p.7 Appendix II; PDF p.19-20 note 9(c): organizing 'Food Pacific 86'; PDF p.80 |
| Housing Corporation of British Columbia | Province of British Columbia | wholly-owned | not found | missing | sourced | [1](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf) PDF p.21 note 9(h): in voluntary liquidation, carried at $1 Note: The bodies.json gaps note calls it 'BC Housing Corporation'. |
| Pacific Coach Lines Limited | Province of British Columbia | wholly-owned | 1979-04-01 to 1984-03-31 | missing | sourced | [1](https://archive.org/details/McGillLibrary-632602-27869) BC Hydro 1978/79 annual report: new company replacing Pacific Stage Lines and Vancouver Island Coach Lines, operating from 1 Apr 1979; [2](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf) PDF p.21 note 9(i): operations ceased 31 Mar 1984, wind-up in progress |
| Vancouver Island Coach Lines | Province of British Columbia | wholly-owned | ended 1979-04-01 | missing | sourced | [1](https://archive.org/details/McGillLibrary-632602-27869) 1978/79 annual report: 'Vancouver Island Coach Lines, a company owned and operated by the Provincial Government' |
| Dunhill Development Corporation | Province of British Columbia | wholly-owned | not found | missing | lead | `research/history/bodies.json` gaps[9]: left out for lack of dates |

## Summary counts

| Group | In repo | Missing (sourced) | Missing (lead) |
|---|---|---|---|
| BCDC | 4 | 3 | 1 |
| BC Hydro | 5 | 7 | 0 |
| BC Rail | 1 | 6 | 2 |
| BCRIC and the 1970s forest holdings | 0 | 8 | 0 |
| ICBC | 0 | 1 | 0 |
| BC Petroleum Corporation | 0 | 1 | 0 |
| BCLC | 1 | 1 | 1 |
| Columbia Basin Trust and Columbia Power | 5 | 11 | 0 |
| Other current Crowns | 0 | 3 | 1 |
| BC Ferries and transit | 1 | 0 | 4 |
| Province-held companies (1985 Public Accounts) with no node | 0 | 4 | 1 |
| **Total** | **17** | **45** | **10** |

### Problems found in existing repo records

1. **`metro-transit-operating-company` has `ended: null`.** The 1984/85 Public Accounts say the British Columbia Transit Amendment Act (No. 2), 1985 merged it into BC Transit effective **1 June 1985** ([OAG 1986 appendices](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf) PDF p.87, note 19(e)).
   *Checked 2026-11-14: not an error. The record deliberately leaves the company’s legal end untraced; its description already says its property, obligations and employees passed to BC Transit on 1 June 1985. A “merger” in the Public Accounts note is the transfer, not a dissolution date.*
2. **`sub-powertech-labs` has `established: 1988`.** The BC Hydro 1989/90 annual report says Powertech, Westech and Western Integrated Technologies "were established as subsidiaries" in 1989 ([McGillLibrary-632592-27884](https://archive.org/details/McGillLibrary-632592-27884)).
3. **The four power corporations are modelled wrongly.** `sub-arrow-lakes-power-corporation`, `sub-brilliant-power-corporation`, `sub-brilliant-expansion-power-corporation` and `sub-waneta-expansion-power-corporation` appear as plain subsidiaries of `columbia-power`. They are **50/50 joint ventures** of Columbia Power and CBT, which holds its half through wholly-owned CBT subsidiaries (CPC 2024/25 FS note 4; CBT 2024/25 FS note 2).
4. **`bc-ferry-corporation.becameId = "bc-ferry-services-inc"` points at a missing node.** No node has that id.
   *Checked 2026-11-14: not an error. `bc-ferry-services-inc` is a body in `research/history/bodies.json` (established 2003-04-02) and is in `historyData.js`.*
5. **Several companies are named only in the bodies.json gaps note** (`research/history/bodies.json` `gaps[9]`) and have no node: BC Rail Ltd., Vancouver Wharves, Western Canada Lottery Foundation, BC Housing Corporation and Dunhill Development Corporation.

## Ten most important missing companies

1. **The First Capital City Development Company Limited.** BCDC, wholly owned, incorporated 2 Aug 1977 (Westminster Quay).
2. **Lonsdale Quay Development Company Limited.** BCDC, wholly owned, 1979.
3. **Duke Point Development Limited.** BCDC subsidiary, 1983-86 statements.
4. **BC Rail Ltd.** The 1984-2004 operating railway: 25% held by BCR and 75% by BCR Properties, with public preferred shares.
5. **Canadian Cellulose Company, Limited.** Provincially controlled from 1973, then BCRIC (81%, later 100%); renamed BC Timber Ltd. in 1981. Also its Crown holding company, **British Columbia Cellulose Company**.
6. **Pacific Coach Lines Limited** (1979-1984), and its predecessor **Vancouver Island Coach Lines**. Both were provincially owned.
7. **International Power and Engineering Consultants Limited.** BC Hydro's wholly-owned engineering subsidiary in the 1960s and 1970s.
8. **BCR Marine group.** BCR Marine Ltd., Vancouver Wharves, Canadian Stevedoring, Casco Terminals and Finlay Navigation LP, 1999-2004.
9. **Canadian Northern Shield Insurance Company.** ICBC's wholly-owned general-insurance company, 1984-85.
10. **Westminster Quay Public Market Ltd.** A BCDC subsidiary, then a joint venture with Laing (1985-86). Also the **BC Museum of Transportation, Science and Industry**, the society BCDC administered.

## Gaps and next sources

- **BCDC before 1983.** The 1st to 8th annual reports (1974-1982) were not found on archive.org. They may name earlier subsidiaries; Duke Point and Lonsdale Quay probably predate 1983. Next steps:
  - Search LLBC/LDP for "Development Corporation annual report".
  - Check the BC Archives GR series for BCDC.
- **BCEC 1987-89.** BCEC took over BC Place Ltd. and BCDC subsidiaries. Its annual reports and the BCEC Loan Privatization Act 1989 would give their end dates.
- **BC Place Ltd., Expo 86 Corporation and the 1980s B.C. Pavilion Corporation.** Not checked for subsidiaries. The PavCo 1988-89 OCR had no subsidiary note.
- **Ocean Falls Corporation, BC Steamship (1975), BC Systems and BCBC.** No subsidiaries were found in the reports checked (BCBC 1986, 1990-91, 2001-02; BC Systems 1984-85, 1988-89). The Wiens 1982 study of B.C. Crown corporations ([egwald.ca](https://www.egwald.ca/government/BC_crown_corporations.pdf)) is scanned. OCR of it could give a full 1982 list of Crown holdings.
- **BC Hydro, 1975-1988.** Not checked:
  - The rail and gas divisions sold in 1988 were divisions, not subsidiaries.
  - Pacific Stage Lines was a division.
  - Hudson's Hope Canadian Utilities system: acquired in 1962.

  The 1990 report lists Hydro's subsidiaries at that date. Hydro reports from 1991 to 2007 were not found on archive.org, so the later fate of Westech, WIT, BC Hydro International and Columbia Estate is unknown.
- **BC Ferries before 2003.** The text layer of the 2001-02 report is poor. Catamaran Ferries International rests on a trade-press lead.
- **BC Transit.** The ownership of BCRTC and West Coast Express before 1999, and the parent of RTP 2000, need the BC Transit annual reports for 1986-1999.
- **BCRIC after 1980.** Its holdings after BCRIC became mostly privately held are outside the Crown's control and are probably out of scope. BCRIC itself is in the repo; the Province held 20% at the start.
- **BC Housing** (the subsidiary name is in the scanned notes) and **InBC** (scanned FS). Both need OCR.
- **Not attempted:** WorkSafeBC, BC Assessment, Destination BC, the health authorities' foundations, and BC Petroleum's BC Gas Corporation (dates).
