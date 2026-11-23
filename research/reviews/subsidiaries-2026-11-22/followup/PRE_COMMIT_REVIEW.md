# PofBC subsidiary follow-up: decisions before committing

**22 November 2026**

## Recommendation and scope

Keep the subsidiary work in a separate commit, excluding the three BC Enterprise Corporation SVGs and the edits to `collected-display-overrides.json` and `collectedDisplay.js`. Apply the definite corrections in this follow-up before finalizing that commit. The unresolved name variants and uncertain ownership starts can remain clearly marked research items.

The most consequential correction is to the earlier verified package: **Pacific Coach Lines existed and operated in 1978.** Its own accounts distinguish incorporation, the initial Vancouver Island asset takeover, and the later Pacific Stage Lines transfer. The earlier package's claim that 1 April 1979 was its first operational start must be superseded.

This review inspected the public repository's date/observation handling and original historical sources. It did not access the user's uncommitted checkout or `INTEGRATION.md`. The reported 1,141 passes, six skipped tests and one unrelated logo failure are user-reported; no full test suite was independently rerun and no repository files were changed, committed or pushed here.

## 1. Pacific Coach: three separate events, and three legal identities

### Correct the 1978/79 chronology

| Date | Event | Evidence |
|---|---|---|
| **2 August 1978** | Pacific Coach Lines Limited incorporated | Its own notes, Public Accounts 1978/79 F190, note 1; Gazette independently corroborates |
| **31 August 1978** | Purchased Vancouver Island Transportation Company assets, assumed liabilities and commenced operations | F190, note 1 |
| **1 April 1979** | Acquired certain Pacific Stage Lines assets and operating responsibilities | F193, note 9 |

F190 is PDF page 508; F193 is PDF page 511 of the [1978/79 Public Accounts](https://archive.org/download/britishcolumbiap01brit_13/britishcolumbiap01brit_13.pdf). Both original page images were inspected. The previous Hydro report remains evidence for the later combined-service change, but cannot establish the company's first incorporation or first operation.

The Province's ownership of its entire two issued common shares is independently shown at **31 March 1979**, Public Accounts B4, PDF 34. Keep that ownership checkpoint distinct from incorporation: the incorporation note alone does not identify the original subscriber.

The known **31 March 1984 cessation of Crown-company operations** remains separate from legal dissolution. A further Gazette source proves that the original legal entity remained available for a later rename.

### Do not merge the later operators by name alone

The [2 August 1990 Gazette](https://free.bcpublications.ca/civix/document/id/bcgaz1/hbcgaz1/429109206), printed 1083–1084 / PDF 11–12, distinguishes:

| Registry number as printed | Earlier name and incorporation | Verified rename |
|---|---|---|
| **178561** | Pacific Coach Lines Limited; incorporated 2 August 1978 | **178561 B.C. Ltd.**, effective **19 July 1990** |
| **273925** | Pacific Coach Lines (1984) Ltd.; incorporated 7 February 1984 | **273925 B.C. Ltd.**, effective **17 July 1990** |
| **362538** | Royal Victorian Holdings Corporation; incorporated 29 March 1989 | **Pacific Coach Lines Ltd.**, effective **19 July 1990** |

These are three legal entities. The notices prove identity and rename events, not the ownership or privatization history of each. Keep unproved sale/asset-successor links qualified. The original Crown company's 1990 rename must not be interpreted as proof of continuous Crown ownership until 1990.

## 2. T.S. Holdings and the V I T group

The 31 March 1976 accounts explicitly identify **Thompson-Okanagan Transit Ltd. as formerly Tweed Line Tours Ltd.** and **Vancouver Island Transit Ltd. as formerly McArthur Transportation Limited**. These are identity links; they do not supply exact rename days. The 1976 and 1977 statements support the three wholly owned T.S. subsidiaries at those dated checkpoints.

The percentages in the five-company V I T group changed:

| Statement date | Interest reported as held directly or through a subsidiary |
|---|---:|
| 31 March 1976 | **98.24%** |
| 31 March 1977 | **98.4%** |
| 31 March 1978 | **98.5%** |

Use the reported percentage for its own observation date. Avoid rounding the historical series to 98% or treating every date as 98.5%.

Two exact events change the parent graph:

- **24 July 1978:** V I T Holdings sold its **98.5% holding in Vancouver Island Transportation Company Limited to the Province**.
- **22 January 1979:** V I T Holdings was **liquidated**.

The sources are T.S.'s 1978/79 notes at F223–F224 / PDF 541–542. F222 / PDF 540 names **only Thompson-Okanagan Transit and Vancouver Island Transit** as the remaining wholly owned consolidated subsidiaries at 31 March 1979. Do not show V I T Holdings as a continuing consolidated subsidiary at that 1979 year-end, or extend its Transportation shareholding past 24 July 1978. A liquidation event is not automatically a proven registry dissolution date.

### Should the five companies appear?

They can be retained as sourced group interests with dated percentages and qualified ownership paths. **Vancouver Island Transportation has explicit evidence of V I T Holdings' holding**, including the 1978 sale. For the other four companies, the collective 'directly or through a subsidiary' wording does not establish each immediate parent.

For the current commit, keep unsupported direct-parent edges absent. If the renderer has no separate group/indirect relationship type, retain those rows in the roster and research data. A subsequent display improvement can show known companies with a qualified group association and unknown immediate parent. Do not encode an indirect group assertion in a normal direct-parent field merely to make it draw.

Detailed sources, page locators and observations are in the transit workstream files.

## 3. Panco: the first rename is now exact

The [8 March 1979 Gazette, printed p.386](https://archive.org/details/governmentgazett0119gove_d9a2) records:

| Registry number | Earlier name | Later name | Effective date |
|---|---|---|---|
| **63265** | Panco Poultry Ltd. | Surrey Farm Products Investments Ltd. | **14 February 1979** |
| **64184** | Pacific Hatchery Ltd. | Surrey Farm Products Hatchery Ltd. | **14 February 1979** |

The original page image was inspected. It also identifies Panco's **amalgamation on 1 February 1965** and Pacific Hatchery's **incorporation on 12 April 1965**. These are private legal-history events; Panco's public acquisition remains **17 February 1975**.

The 29 January 1979 asset-sale event precedes the rename: its event-time legal name is Panco Poultry Ltd., although the later accounts describe it under their Surrey title. The 4 May 1979 dividend occurred after the rename.

This directly supersedes the earlier package's unresolved first-rename date. Replace the graph's persistent Panco label with the exact Surrey name change from 14 February 1979.

The second change to **British Columbia Food Exhibitions Ltd.** remains without an exact effective day. Its conservative rename bounds are after 14 February 1979 and by the authenticated audit dated 17 June 1985, and its final Gazette dissolution is already linked to company no.63265. Do not label the company Panco throughout 1992. Show the later name wherever supported by a dated observation, and explicitly identify any uncertain transition. An audit signature or financial year-end must not be turned into a rename day.

The search log documents which Gazette issues were searched and which were unavailable. Archive coverage gaps are not proof that the rename occurred inside one particular missing interval.

## 4. The three spelling pairs

Retain the distinction between printed-name variants and proven legal name changes:

- **Venture / Ventures Realty:** a new Gazette notice identifies the singular-name company as **no.83729**, incorporated **30 December 1968**, and renamed **Venture Realty Consultants Ltd. on 11 April 1979**. This is after the verified sale on 30 November 1978. It is a strong registry lead, but does not independently prove that the earlier plural spelling is the same numbered company.
- **Pacific Hatching / Hatchery:** the 1979 notice proves **Pacific Hatchery no.64184 → Surrey Farm Products Hatchery**. It does not establish a separate Hatching-to-Hatchery rename or place the earlier Hatching wording under that number without an additional identity bridge.
- **Western Feeds / Feed:** no decisive company-number bridge was recovered in this follow-up.

Preserve those source spellings and the suspected equivalence in the research record. A financial statement's explicit 'formerly' clause can establish a name chain without a registry number, but similarity alone should not be converted into a legal event. See the identity workstream for complete URLs and the remaining retrieval gaps.

## 5. Swan Valley: do not start ownership at the sale

For the present dated graph, leave the unsupported continuous ownership interval off. The **1 December 1977 sale date is an end of provincial ownership**, not its start. Full ownership began after 31 March 1977 and on or before that sale; its exact start remains unknown.

Keep the historical company and ownership/sale evidence in the research catalogue. A suitable future graph representation is a qualified transaction marker or a bounded uncertain-start interval. Do not fabricate a one-day ownership period to satisfy an event test.

The additional Corporations Canada lead identifies federal no.026524-1, continued from British Columbia on **6 January 1978** and amalgamated on **28 April 1978**. It supplies a possible post-sale identity continuation, not the missing public-acquisition day. Retain the provincial registry match as a separate check. Sources and model implications are in `SWAN_AND_MODEL_REVIEW.md`.

## 6. BC Cellulose's legal endpoint

The original [Order in Council 631/1986](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0631_1986), approved **19 March 1986**, expressly brings the Repeal Act into force effective **31 March 1986**. Its original page image was inspected. The official [archived consolidation](https://www.bclaws.gov.bc.ca/civix/document/id/94consol18/94consol18/83002) independently identifies **B.C. Reg. 49/86** and the same effective date. Section 2 dissolves BC Cellulose upon repeal. This resolves the earlier missing-commencement-instrument problem.

Use **31 March 1986 for the legal endpoint**, retaining the accounts' **1 April 1986** statement as a separate source assertion. Do not erase that accounting wording or claim the two documents print the same day. The order supplies no midnight provision or explanation for the accounts' next-day wording. The 1983 assent date and the 19 March 1986 approval date remain distinct from commencement.

## 7. Canadian Cellulose and Kootenay Forest Products

Both deserve separate entity records with correctly typed ownership. Canadian Cellulose belongs in a majority-controlled or partly owned category; Kootenay qualifies as wholly owned. If the current graph admits only wholly publicly owned companies, add Kootenay now and keep Canadian Cellulose in the qualified holdings layer until that distinction can be displayed:

| Company | BC Cellulose interest | Date meaning |
|---|---:|---|
| **Canadian Cellulose Company, Limited** | **79%** in the 1975 accounts | Majority interest acquired **29 June 1973**; retain the dated holding, not a 100% claim |
| **Kootenay Forest Products Ltd.** | **100%** | Its own accounts say all shares purchased effective **1 March 1974** |

Kootenay's note is Public Accounts 1975/76 F128 / PDF 514. It distinguishes the corporate share purchase from the acquisition of assets/liabilities of Eddy Match's operating divisions. An asset purchase or a division name must not create a duplicate corporation.

The Province received BC Cellulose holdings as dividends before the BCRIC transfer. For Canadian Cellulose, its separate 278,100-share investment was combined with the holding-company dividend, producing the 81% interest transferred to BCRIC. Do not change BC Cellulose's earlier 79% observation into 81%. The Finance Minister's 10 April 1978 statement dates the actual transfer to BCRIC to 9 March 1978; preserve the earlier dividend as a separately bounded event. The detailed sources and share counts are in the cellulose workstream.

The later BCRIC evidence matters for their endpoints and successors. In 1980, Canadian Cellulose, Kootenay Forest Products and Plateau Mills amalgamated into a **new company also named Canadian Cellulose Company, Limited**, effective **31 December 1980**. Preserve that as a separate successor identity, not a rename of BC Cellulose or a merger with the provincial holding company. This is a post-transfer legal event; it does not extend Crown ownership to the amalgamation date.

The cellulose workstream supplies the transfer-to-BCRIC evidence and the limits on public-ownership continuity. Apply ownership observations and public-ownership endpoints separately from the companies' later private legal histories.

## 8. What to verify before the scoped commit

The verified historical sources do not all need to be reopened merely because some were checked in another review. Carry forward their exact locators and confidence notes. However, the Pacific Coach finding demonstrates why conflicting or broader date meanings should be reconciled against the company's own notes.

For this commit:

1. Apply the definite date/identity corrections above; keep unresolved records explicit.
2. Stage an explicit file list for subsidiary research, data, necessary tests and generated government output.
3. Check that the three BC Enterprise SVGs and both display files are excluded, without modifying the other session's work.
4. Validate the proposed staged tree in an isolated local checkout/export with the existing test suite and `npm run check:government`. This tests the content intended for the commit without the unrelated working-tree logo failure. No GitHub runner is needed.
5. Record the actual results, including skips. A reproducible government build and an unrelated working-tree failure are separate facts; neither should be described as a fully passing test suite.

The follow-up package is a research deliverable and semantic integration guide. It is not a patch against the unavailable local checkout and does not claim the resulting graph or commit has been independently approved.
