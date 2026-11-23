# PofBC: verification and integration corrections

**22 November 2026**

## Recommendation

Apply the identity and ownership corrections below before committing the integrated graph. The main changes are substantive: HCBC is an existing company's new name; two held transit companies have a documented parent; Plateau was wholly publicly owned through two holdings; and BC Cellulose has a separate legal history. The Statistics Canada appendix dates themselves are correct.

This review answers the nine requested checks using original publications, corporate accounts and registry notices. It does not certify the user's uncommitted diff, reproduce the reported 1,148 tests, or reverify every entry in the 111-company roster. The local integration file was unavailable in this workspace. No commit or push was performed.

## 1. Statistics Canada claims and the transit ownership breakthrough

### T.S. Holdings

Retain **1975 at year precision**, described as the incorporation year reported by Statistics Canada. The decisive table is the 1976 volume, printed p. 22, PDF p. 24; the 1975 volume also prints 1975 on p. 22. The 1975 volume's p. 27 describes its bus-holding activities but does not itself give the incorporation year. [Sources: S75, S76 in `SOURCE_INDEX.md`.]

### Panco acquisition

The 1975 federal volume, p. 27, confirms February 1975, CAD 4.8 million, all issued common and preferred shares, and three wholly owned subsidiaries: B.C. Testing Farms, Pacific Hatching and Western Feeds. The company's later audited accounts improve the acquisition date to **17 February 1975**. See section 3 for the exact transaction chronology. An acquisition date must not become the private company's incorporation date. [S75; Public Accounts 1978/79, F215, note 3.]

### Venture Realty

The 1978 federal volume, p. 26, confirms the sale as printed. The more precise Housing Corporation accounts give **30 November 1978** as the effective sale date, and **29 September 1978** as the directive to wind up operations. The sale is a subsequent event in statements for the year ended 31 October 1978; that explains why a date after the statement year-end appears there. These accounts call the company **Venture Realty Ltd.** The identity bridge to the 1974 roster's **Ventures Realty Ltd.** remains unresolved; keep that spelling discrepancy explicit. [S78; Public Accounts 1978/79, F154, note 1, PDF p. 472.]

### Vancouver Island Transit and Thompson-Okanagan

Catalogue 72-007, vol. 23 no. 1 covers **January–March 1981**, published **September 1981**. Vancouver Island Transit appears on printed p. 37, PDF p. 39. That roster alone does not identify its parent. [S81Q1.]

The parent is now established by a better source: **T.S. Holdings' notes at 31 March 1978**, in Public Accounts 1977/78, **F220–F221**, PDF pp. 648–649. They identify three wholly owned subsidiaries:

| Parent | Subsidiary | Verified ownership observation |
|---|---|---|
| T.S. Holdings Ltd. | V I T Holdings Ltd. | 100%, 31 March 1978 |
| T.S. Holdings Ltd. | Thompson-Okanagan Transit Ltd. | 100%, 31 March 1978 |
| T.S. Holdings Ltd. | Vancouver Island Transit Ltd. | 100%, 31 March 1978 |

**Integration:** remove the parent-unresolved hold for Vancouver Island Transit at this checkpoint. Replace the blanket loan-only classification of Thompson-Okanagan with both its documented ownership and its separately sourced funding relationship. The earlier loan entry was insufficient ownership evidence; these consolidated statements supply the missing evidence.

The same note identifies a 98.5% interest held by V I T Holdings, directly or through a subsidiary, in five other companies: Vancouver Island Transportation Company Limited; Vancouver Island Coach Lines Limited; Gray Line & Empress Taxi & Sightseeing Company Limited; Imperial Charter Service Company Limited; and British Columbia Parlour Car Tours Limited. Preserve the percentage and the unresolved immediate ownership path for each. Note 1(d) separately identifies Vancouver Island Transportation as V I T Holdings' subsidiary. **Vancouver Island Transit and Vancouver Island Transportation are distinct names listed separately in the same accounts.** [See `review_workstreams/TRANSIT_FINDINGS.*`.]

## 2. Peace Power, HCBC and the federal appendix dates

| Financial reference year | Actual publication | Roster heading | Relevant BC pages |
|---|---|---|---|
| 1984 | May 1987 | As at 31 December 1986 | Printed 143–144; PDF 145–146 |
| 1985 | June 1988 | As at 31 December 1987 | **Printed 103**, PDF 105 |

The newer appendix dates are printed on the original scans. Retain them. Correct the second page locator from 102 to **103**. Both appendices list Peace Power under Hydro and Dunhill/HCBC under Housing. These establish reported roster observations, not incorporation dates. [S84, S85.]

Legal identity must be resolved before adding nodes: **HCBC is Fisher Developments renamed**, and the later Dunhill is W.K.P. renamed; see section 5. Techwest and the Discovery names can retain the correctly dated source observations. The Discovery special-fund headings and inconsistent hierarchy around Ocean Falls/First Capital/Duke Point require separate parentage evidence.

The 1981-Q1 employment publication already lists Duke Point Terminals as a consolidated subsidiary in the BCDC grouping and names Discovery Park Industries on printed p. 36. This is an earlier observation, not a proven corporate birth or a bridge between differently named Discovery entities. [S81Q1.]

**Roster accuracy limitation:** the 31 December 1986 list still contains BC Cellulose despite the statutory/accounting evidence of its termination earlier in 1986. It also retains inactive poultry-company names. Preserve what was printed, but do not use roster inclusion to override direct legal or audited evidence.

## 3. Panco names, transaction amounts and later dissolution

The documented name sequence is **Panco Poultry Ltd. → Surrey Farm Products Investments Ltd. → British Columbia Food Exhibitions Ltd.** The first link is explicit in the 1978/79 corporate statements; the second is explicit in the 1984/85 provincial accounts. The exact registration days of the two renames were not recovered. Use dated name observations and leave legal effective dates unresolved. A statement year-end is not automatically a name-change date, especially where the auditor signed later.

| Event | Verified date | Amount and meaning |
|---|---|---|
| Province acquired all Panco shares | **17 February 1975** | CAD 4.8 million; federal account corroborates month and amount |
| Surrey Farm Products Investments sold its business and assets | **29 January 1979** | **CAD 12,076,253 gross proceeds** |
| Net proceeds after disbursements/adjustments | Same sale | CAD 11,724,660 |
| Dividend transferred to Minister of Finance | **4 May 1979** | **CAD 14.8 million** |

The transaction notes are on **F215, notes 2–4, PDF p. 533** of the 1978/79 Public Accounts. The asset sale and the dividend are separate events. Do not label CAD 14.8 million the sale price.

The shorter **Surrey Farm Products Ltd.** label in the provincial revenue schedules is explicitly connected there with former Panco. It is not evidence of a separate buyer. Preserve it as an as-printed source label; a separate-company assertion would need an independent legal identifier.

Food Exhibitions appears in the **9 July 1992 Gazette, p. 840**, company **63265**, under dissolutions dated **19 June 1992**. This supplies a legal end event under the later name. The evidence does not independently certify uninterrupted Crown ownership through every intervening year. [Gazette source ID in identity findings.]

Two subsidiary refinements are also documented: the 1979 accounts describe **Surrey Farm Products Hatchery Ltd. as formerly Pacific Hatchery Ltd.**; the 1984/85 Food Exhibitions accounts report that this company and **Western Feed Co. Ltd.** were wound up during that fiscal year. Preserve the Hatchery/Hatching and Feed/Feeds printed-name distinctions pending registry matching to the original roster entries. A winding-up statement is not an exact registry dissolution day.

## 4. Pacific Coach Lines

**1 April 1979 is confirmed as an operational start.** The original BC Hydro 1978/79 annual report, printed p. 10, PDF p. 12, says Pacific Coach began operations that day after the replacement plan for Pacific Stage Lines and Vancouver Island Coach Lines was announced on 5 September 1978. It does not give the new company's incorporation date. [BC Hydro original report and accessible OCR in Pacific Coach findings.]

The 1984/85 provincial accounts, B16 note 9(i), confirm operations ceased **31 March 1984** and winding up remained in progress. Retain an operations-ceased event; do not convert it into an exact legal dissolution. The 1985/86 accounts further describe the remaining asset-disposal process. [OAG 1986 appendices; OAG 1987, A12.]

## 5. W.K.P., the two Dunhills, and Fisher/HCBC

| Company number as printed | Earlier name | Verified change | Later name |
|---|---|---|---|
| **73385** | Dunhill Development Corporation Ltd. | **18 November 1976** | Housing Corporation of British Columbia |
| **91003** | W.K.P. Construction Ltd. | **26 November 1976** | Dunhill Development Corporation |
| **71787** | Fisher Developments Ltd. | **26 November 1976** | HCBC Construction Ltd. |

The Gazette notices independently connect the names and company numbers: 9 December 1976, p. 1629, and 16 December 1976, p. 1664. Note that the later Dunhill's registered name in the notice has **no “Ltd.” suffix**. The older parent's earlier name does. Its use in the previous package for both legal entities needs correction.

The notices also report private incorporation dates of 17 March 1967, 19 December 1969 and 17 November 1966 respectively. Those dates do not move the public-ownership start back from the documented 1974 acquisition.

Direct corporate statements now provide ownership observations after 1974:

- **31 October 1975:** Public Accounts 1975/76, F103, PDF p. 489, lists W.K.P. and Fisher among Dunhill's 100%-owned subsidiaries.
- **31 October 1976:** Public Accounts 1976/77, F133, notes 1 and 2(a), gives the rename sequence and full ownership. The renames are subsequent to the statement date.
- **31 October 1977 and 1978:** Housing statements list Dunhill and HCBC as wholly owned (1977/78 F152; 1978/79 F154).
- **31 October 1984:** Housing's 1984/85 accounts, G247, again identify both as wholly owned.
- **31 December 1986 and 1987:** the federal rosters provide later reported observations.

**Integration:** attach these to the existing W.K.P. and Fisher legal entities. They replace the blanket “no parent after 1974” assumption with explicit checkpoints. Do not manufacture a continuous relationship for unobserved dates if the project's observation policy requires separate evidence.

The same accounts add useful exits: Crown Lumber was sold **1 November 1976**; Dunhill Homes, Dunhill Holdings and Georgia Park Holdings were wound up in **1976**. Preserve year precision for those windups. [1977/78 F152; 1976/77 F133.]

## 6. Swan Valley Foods

**Include its documented wholly public phase if the graph can represent an unknown or bounded start.** Standard Brands' original 1977 annual report, printed p. 30, note 6, confirms acquisition from the Province of all shares and certain debentures on **1 December 1977** for **CAD 2.2 million**. The provincial accounts show 40% at 31 March 1977 and further share acquisitions before disposal.

Accordingly, full ownership was attained **after 31 March 1977 and on or before 1 December 1977**. It is established immediately before the sale, but a duration of several months is not established. If the renderer cannot show that uncertainty, keep the continuous interval held instead of inventing a start. [OWN-C01–02.]

## 7. Plateau Mills

The direct provincial holding of **97.5%** is correct, but incomplete. BC Cellulose's own accounts show it acquired the remaining **2.5% (225 shares) on 23 June 1975**. Combined with the Province's direct stake, this establishes **100% ultimate public ownership** in the audited 31 December 1975 ownership snapshot; the minority purchase itself is dated 23 June. Record two owners, not a 100% direct provincial edge. [Public Accounts 1975/76, F9 note 2; OWN-C03.]

The 1977/78 accounts reconcile all 9,000 shares transferred to BCRIC, including the 225 received as a BC Cellulose dividend. OIC 530/1978 approves the agreement dated **9 March 1978**; the accounts confirm transfer by 31 March. Preserve approval/agreement and completed-by evidence separately. Later BCRIC privatization must not be assumed to leave its subsidiaries under Crown control. [OWN-C04.]

The 1973 federal volume supplies an earlier majority-acquisition lead, with **97% as printed**. Do not silently normalize that to the later 97.5% figure. The detailed ownership review distinguishes its text-only verification from the later visually checked accounts.

## 8. British Columbia Cellulose Company

Add the missing holding-company node. It was incorporated **15 March 1973** as **British Columbia Cellulose Limited**, and continued under the statutory name **British Columbia Cellulose Company on 18 April 1973**. The scheduled agreement dated 2 April 1973 already identifies the earlier-name company as wholly Crown-owned. It is a separate legal entity from Canadian Cellulose/Columbia Cellulose. [1975/76 F8; 1973 Act, sections 1–2 and scheduled agreement; OWN-C06–08.]

Use **1986 at year precision** for its end while retaining the source disagreement: the official repeal table gives **31 March 1986**, while the 1985/86 accounts report dissolution effective **1 April 1986**. The repeal statute ties dissolution to repeal, but the original commencement regulation was not recovered to reconcile the day boundary. The 1983 assent date is not the dissolution date. [OWN-C09.]

## 9. Crown Development Corporation

Move beyond an earlier first-seen observation: the company's own note gives **26 August 1975** as its incorporation date and identifies the Attorney-General as holding its capital for the Crown. The decisive source is **1975/76 Public Accounts F99**, PDF p. 485; F84–F85 are related-company context. Preserve “wound up by **31 March 1978**” as a bound, not an exact legal dissolution day. [OWN-C10–12.]

## Applying and checking the changes

The machine-readable actions are semantic instructions for the existing records, not an executable patch against the unavailable local tree. Apply exact-name/registry matches first, then date and ownership observations. This prevents HCBC and the later Dunhill from being added twice.

After integration, rerun the repository's existing tests and government build check. Review the drawn graph at the relevant historical checkpoints, especially Fisher/HCBC, both Dunhills, the three T.S. subsidiaries, Plateau's two owners, and BC Cellulose's 1986 endpoint. Keep the original source roster available alongside resolved legal entities, and ensure held events remain held only where identity, date representation or policy actually requires it.

Remaining targeted retrievals: the exact two Panco rename days; a registry bridge for Venture/Ventures Realty and the poultry subsidiary spelling variants; Swan Valley's exact full-ownership start; BC Cellulose's commencement regulation; and the immediate ownership paths and lifecycle dates of the 98.5%-owned transit group. These gaps do not require undoing the verified findings above.
