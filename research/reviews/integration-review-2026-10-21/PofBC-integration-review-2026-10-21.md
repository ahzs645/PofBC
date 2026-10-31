# PofBC: integration review and corrected research handoff

**Reviewed:** 21 October 2026.  
**Repository:** [ahzs645/PofBC](https://github.com/ahzs645/PofBC).  
**Exact head reviewed:** [`0dbdb18cfebfb27e5529ce5940850e96eb9a995c`](https://github.com/ahzs645/PofBC/commit/0dbdb18cfebfb27e5529ce5940850e96eb9a995c), branch `claude/vibrant-cori-gy5e6w`.  
**Research comparison baseline:** `0f1587c5e982135f155ba6660af5192509351511`.

## Result

Keep the supported Treasury, ministry-title and historical-date corrections. The pushed government data reproduces, and the reported 421 passing tests can be reproduced. The next substantial improvement comes from reconnecting already recovered research to the integration, then correcting how the diagram represents uncertainty and relationships.

The three evidence archives were not a complete replacement for the consolidated research JSON. Thirty-two of its 66 earlier structured components have no exact copy in the repository's research files. Fourteen groups held for missing sources or datasets can be mapped back to the complete handoff: the claim-based groups cover 82 distinct claim IDs and 56 source IDs, all with literal URLs in the catalogue. Some facts from missing files were independently integrated, so file absence must not be equated with complete absence of their subject matter.

There was also an error in my earlier branch archive. Its `prior/claims.json` contains the 26 logo claims rather than the 279 branch claims. Both original components survive correctly in the consolidated JSON. The corrected handoff preserves complete nested paths, including `branches/claims.json` and `branches/logos/claims.json`; it never flattens both to the same filename.

The existing prior branch import batch gives the clearest measure of the handoff gap. In a separate checkout of the reviewed commit, importing it changes the atlas from **48 starts / 65 sightings / 138 undated** to **51 starts / 176 sightings / 24 undated**, out of 251 sub-agencies. That supplies dates for **114 previously undated records**. A derived batch preserves newer review metadata that the unmodified older batch would overwrite. The historical claims remain unchanged.

This review and its simulations did not change or push the public branch. The complete deliverable includes the report, machine-readable audits, source mappings, all 103 structured research components, the 1,492-entry source catalogue, and the derived branch batch. It does not claim that every original research question has been answered.

## 1. Verification of the pushed integration

| Check | Result | Practical meaning |
|---|---|---|
| Full test invocation after ordinary dependency and capability setup | 435 tests discovered: **421 pass, 0 fail, 14 skipped** | The skipped cases require generated current-mark artwork or font outlines. They are not government-history tests. |
| Government drift check | **Byte-for-byte reproduction** | The tracked government outputs reproduce from the committed inputs. |
| Both research converters followed by the government build, repeated | **No tracked changes** | The pushed converter/build sequence is idempotent at this commit. |
| Minister coverage, 1871–2026 inclusive | **0 missing heads across 2,015 ministry-year snapshots** | Confirms annual snapshot coverage; not a day-by-day tenure audit. |
| Prior branch batch validation | **0 errors, 0 warnings, no competing established/end dates** | The batch passes the repository's schema and conflict checks. Semantic qualifications still matter. |
| Derived branch simulation: government, evidence-integrity and merge tests | **91 pass, 0 fail, 0 skipped** | Focused tests remain green after the larger branch import. |
| Derived branch batch imported and rebuilt a second time | **94 checked files byte-identical** | Review metadata as well as generated history remains stable. |

The test command used Node's in-process test isolation option so the result counted individual tests rather than only subprocess test-file wrappers in this runtime. The normal repository generators supplied the empty optional Garamond extension, the capability manifest and the pinned share-link dependency. No licensed font was fetched or substituted.

The zero-missing-minister result is real, but `scripts/measure-government.mjs` does not currently calculate or print it. The WANTED table attributes this row to that command. Add the missing metric and a focused Treasury alias regression. The existing broad coverage test accepts more than 95% coverage and would not protect the new zero result. [Code reviewed](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/scripts/measure-government.mjs); [existing test](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/src/government/government.test.js#L150-L161).

## 2. Recover the already supplied branch history

The repository already contains this unchanged prior batch:

```text
research/reviews/round-4-2026-10-21/branches/prior/handback-importable.json
```

It contains 144 records and 118 source records. The integration instructions list three later merge batches but omit this larger earlier one. Its name-bearing observations and selected starts are already supported by the previous research, not newly invented dates. [Current integration instructions](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/research/reviews/round-4-2026-10-21/INTEGRATION.md).

### Measured change in an isolated rebuild

| Measure | Pushed branch | After prior branch claims | Change |
|---|---:|---:|---:|
| Sub-agencies with an establishment date | 48 | 51 | +3 |
| Sub-agencies with a dated sighting but no establishment | 65 | 176 | +111 |
| Sub-agencies with neither | 138 | 24 | −114 |
| Past sub-agency-years | 1,940 | 3,015 | +1,075 |
| Past sub-agency-years using today's parent by inference | 1,879 | 2,918 | +1,039 |

The last two rows are essential context. More dates reveal more history, but most new historical placements still lack a proved parent at that date. Forty-seven incoming parent rows are observations, not continuous intervals: 41 `part_of` and six `subsidiary_of`. Do not stretch a checkpoint across intervening years or convert the subsidiary observations into responsibility lines.

The three added establishment claims are Connected Services BC on 1 October 2025, the Compliance and Enforcement Collaborative in 2012, and the Drought Information Portal in spring 2015, retained at year precision. The Collaborative is an inter-agency working group; its supporting Secretariat is a different administrative role. Preserve that distinction rather than using the Secretariat's host ministry as responsibility for all Collaborative members. Detailed source checks and locators are in `audit/prior-batch-review.*` in the complete handoff.

The remaining 24 undated records comprise 14 records without the generated `gone` flag and 10 with it. This is the actual current atlas population. It must not be confused with the previous report's 12-record residual cohort or the integrator's 13 after holding Safe Campuses BC. The package includes the complete measured 24-record list.

### Preserve newer review work during import

The unmodified older batch overwrites `review.unresolved_fields` on 35 already held records. Examples include Powertech's operational-start question, Finance-unit identity continuity, and specific Round 4 questions for BC Parks, the Conservation Officer Service and Buy BC. Replaying it also duplicates combined reviewer/scope strings even when the merge log says nothing changed. Its research facts and generated runtime outputs remain stable, but its review metadata is not byte-idempotent.

The derived `integration/prior-branch-preserving-batch.json` removes only the older `review.scope`, `review.by` and `review.unresolved_fields` fields on records already present at the reviewed commit, and carries forward their existing completeness flag. It retains dates, observations, source checks, notes, historical relationships, sources and all 144 records. Original review metadata remains in the unmodified component and the preparation manifest. This is a targeted adaptation for the reviewed commit, not a replacement for the original research.

The six subsidiary observations and the Collaborative classification still require the relationship/type treatment described below. Mechanical validation is not evidence that every current graph consumer preserves those meanings.

## 3. Reconnect sources before reopening research questions

The complete catalogue contains **1,492 source records**, including 1,178 retained earlier records. This count includes screened candidates, failed retrievals and guards as well as accepted evidence. Its retrieval/review status fields are preserved; it is not a claim that all 1,492 entries are usable sources or independent discoveries.

The source-recovery audit maps every explicit missing-URL/dataset hold group to the original component, claim ID, locator and source URL. It also preserves the independent reason a claim may still need to be held: a missing entity identity, an area or regulator layer, a current-law checkpoint, an unresolved effective date or an unproved legal succession.

Examples of material that is already available:

| Subject | Recovered material | What still needs care |
|---|---|---|
| SSO Administration Society / HSSBC | Audited 2010/11 statements, R3H-082 | Separate the society, the PHSA division, operations and the executed transfer. |
| Forensic Psychiatric Services Commission | Audited 2002/03 statements, R3H-086; 1998 appointment order, R3H-091 | A reconstituted board is not creation of the Commission. Funding through PHSA does not establish ordinary ministry parentage. |
| Provincial Language Services | PHSA institutional history, R3H-087 | A program needs its own identity; preserve year precision. |
| Health Insurance BC | 2004/05 Health Services annual report, R3H-100 | Administrative contract/program identity differs from incorporation. |
| Health profession regulators | All 25 distinct cited source IDs for the 32 held claims | Regulator identities and their merger/commencement meanings still need review. |
| Ministry reorganizations | 657 extracted clauses from 17 orders | These are reviewed schedule/assignment data, not 657 automatically valid parent edges. |
| Education | 37 claims, 15 school-merger rows, four boundary-order rows and 18 relationship rows | Preserve merger, renumbering, boundary change and commencement as different facts. |
| Legislature, elections and deputy ministers | Complete earlier review datasets and their source mappings | Candidate extraction/review tables are not automatically complete or approved historical rosters. |

Thirty-two earlier components are absent as exact payloads: 19 root components, five tribunal components, four education components, three legislature components and the 279-claim branch component. Some relevant facts, including the Treasury and 1978 title, were already integrated from other carried material. Use the component inventory rather than assuming either total absence or total completion.

### Three questions that should be narrowed or closed now

**Forest Renewal BC's statutory end is 27 June 2002.** The current body record already uses it. The Act's section 8 repeals the Forest Renewal Act; section 28 dissolves the corporation on that repeal. OIC 517 was approved on 26 June, and B.C. Reg. 158/2002 was deposited on 27 June. The Gazette issue is dated 2 July. These are distinct events. Close the 14-versus-27-June statutory-end question in E11; an independently sourced operational milestone would be a separate claim. [Act](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1944924325); [Gazette regulation](https://www.bclaws.gov.bc.ca/civix/document/id/bcgaz2/bcgaz2/v45n12_158-2002); `R3E-C048`.

**The LCLB–LCRB identity bridge exists.** The provincial bulletin of 5 July 2018 explicitly identifies the Liquor and Cannabis Regulation Branch as the former Liquor Control and Licensing Branch and says it has been renamed. That proves continuity and a rename by that day. It does not, by itself, establish the exact effective renaming day. Keep the latter question open without calling the identity bridge absent. [Official bulletin](https://news.gov.bc.ca/releases/2018AG0053-001343); `R3F-C-0204`, `R3F-C-0265`, source `R3F-EXT-058`.

**The Industry Training Appeal Board continues under its new name.** Section 42 of the Skilled Trades BC Act continues it as the Skilled Trades BC Appeal Board. OIC 650/2022 brought the Act into force on 1 December 2022. This is continuation, not an unsupported dissolved-and-recreated pair. [Act, s 42](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/22004#section42); [OIC 650/2022](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0650_2022); `R3T-E001`.

### A useful health sequence already in the recovered source

The SSO statements distinguish incorporation on **15 October 2008**, operating commencement on **1 April 2009**, and transfer of net assets to PHSA's HSSBC division on **17 September 2010**. They also distinguish member and PHSA approvals from the transfer itself. These are ready to reconnect to the health/shared-services history once the identities are admitted. [2010/11 financial statements, note 1, PDF p. 7](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2010-11/sup-e/shared-services-organization-fs-2010-11.pdf).

## 4. Decisions on the seven rural boards and unknown ends

**Import the historical identities and their proved designation dates. Represent their later status as untraced.** Do not require an invented closing day before the historical record can be searched, and do not let a null end imply survival to 2026.

| Original designation name | Effective designation date | Instrument |
|---|---|---|
| West Kootenay-Boundary Regional Health Board | 14 October 1994 | M306/1994 |
| East Kootenay Regional Health Board | 28 October 1994 | M328/1994 |
| Cariboo Regional Health Board | 3 November 1994 | M339/1994 |
| Upper Island and Mid-Coast Regional Health Board | 23 November 1994 | M366/1994 |
| North West Regional Health Board | 12 December 1994 | M422/1994 |
| Coast Garibaldi Regional Health Board | 16 December 1994 | M448/1994 |
| Peace River-Liard Regional Health Board | 2 February 1995 | M74/1995 |

These are claims `R3HC-001`–`R3HC-007`, with original URLs and locators in `datasets/health/rural_board_starts.json` and the source catalogue. No legal end follows merely from a later regulation's repeal, a similar society name, or an unsuccessful search.

The minimum useful lifecycle model separates four things: legal ending, operational ending, dated evidence of presence, and current confirmation. An ending may be known, positively known to have occurred but undated, or untraced. The seven boards currently belong in the last category. A bounded interval also needs evidence for its bounds.

A historical identity should remain searchable even when the selected year's diagram cannot assert its presence. Evidence points or supported intervals can appear in an optional history/uncertainty layer. If the normal snapshot means standing on 31 December, an observation earlier that year should be labelled documented during that year rather than silently treated as proof of year-end existence.

This requires one shared presence resolver across search, jump navigation, snapshots, timeline and panel. Changing only `stands()` leaves the current “Since”, “last year” and timeline-to-present assumptions intact. [Snapshot code](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/src/government/snapshot.js#L312-L315); [search consumer](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/src/government/GovernmentView.jsx#L99-L105).

The 43 folded councils reconcile correctly as 42 newly dated plus Prince George already dated. Their exact amalgamation-execution days remain open. Preserve a supported year-level transition as year precision; an internal conversion of `1997` to 1 January for year-end rendering must never become a claim that the legal transaction occurred on 1 January.

## 5. MTOC, Hydro, Harbours and LDB

### MTOC: keep the transfer, change what the diagram calls it

The operational cutoff of **1 June 1985** is useful for a service-delivery view. It cannot serve as a generic corporate end. OIC 1096/1985 appoints an MTOC board effective that very day; the transfer instruments establish movement of assets, obligations and employees, not dissolution. [OIC 1096](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1096_1985); [OIC 1093](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1093_1985); [OIC 1094](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1094_1985); [OIC 1095](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1095_1985).

The panel's end note recognizes this, but the snapshot loses that distinction and the 1984–1985 comparison lists MTOC under **Bodies that closed**. Keep an operational end and an unknown legal end separately; label the change operations transferred. Preserve the entity's searchable legal record after operations leave. The health societies already demonstrate why both dates matter: services pass in 2001 while their registry dissolution is in February 2002.

### Hydro: retain the dates and distinguish the legal identities

Keep **30 March 1962** for the original scheme's commencement, **23 March 1964** for the new statutory corporation, and **20 August 1965** for the amalgamation ending the separate existence of BC Electric and the Power Commission. BC Electric's formal 23 August cancellation remains a separate event. A public-facing Hydro lineage can span these events, but that is not a finding of one unchanged legal corporation since 1962. [OIC 839/1962](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0839_1962); [OIC 773/1964](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0773_1964); [Power Measures Act 1966](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/815001869).

The 1963 court event is already qualified as a statement in Hydro's contemporary annual report; the full judgment and any appellate disposition were not recovered. Keep that qualification. The later ratified agreement independently supports the 1965 amalgamation dates.

A concrete citation fix is needed: the displayed 30 March 1962 lifespan claim still links to the Archives entry that the record itself says gives 31 March. Attach the original order to the corrected date. Starts, ends and first sightings need their own sources, locators, date kinds and qualifications rather than inheriting one general body citation.

### Harbours: keep first-seen semantics and repair the consumers

The new Harbours record correctly leaves establishment unknown and uses **23 September 1983** as a first sighting, with dissolution on **30 May 1985**. Search nevertheless assumes establishment exists, producing `NaN` and `null–1985`. Use first-seen for navigation and label the history known by 1983; start unknown. Do not repair the UI by making 1983 a founding date. [Repeal Act](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/881646216); [dissolution OIC 1061/1985](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1061_1985).

Also retain the conditions on its asset-transfer provisions. An Act authorizing a transfer on separately fixed dates is not evidence that every transfer was executed. A reported railway-asset exchange is an asset relationship, not automatically service succession. The preserved Public Accounts says the Board had no assets, liabilities or operations in 1984/85, yet it remains drawn until legal dissolution—another reason to use one explicit legal/operating model consistently. [Auditor General 1986 appendices reproducing Public Accounts](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf), source R4E-017 and locators in the Crown audit.

### LDB: expose the inferred endpoint

Keep statutory establishment on **31 December 1976** separately from the older administrative lineage. The first ministerial assignment is sourced. Capping it at **1986**, when the named ministry episode ends, is a model inference; the 1976 order does not establish the 1986 transfer or prove uninterrupted responsibility until then. The current build drops the explanatory note and presents the entire period as source-stated. Carry endpoint basis and qualification into the generated evidence. [OIC 3495/1976](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/3495_1976); [builder projection](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/scripts/build-government-history.mjs#L181-L225).

## 6. Local bodies and the People connection

### Approve a local register that can be used by the atlas

Keep regional hospital districts and hospital improvement districts as their own entity types. Their lack of a provincial ministry parent does not justify suppressing their histories. The register should feed shared identity lookup, search, panels, events and an optional local/regional layer. A register that no diagram consumer can read is an interim storage milestone.

The existing proposal correctly keeps similarly named old and new corporations separate and distinguishes asset recipients from automatic successors. Preserve those choices. The 68 district identities in the research are useful regardless of whether every one appears in the default provincial view.

Two proposed generalizations need revision. “Neither runs a hospital” is too categorical: the Fort Nelson and 100 Mile House instruments assign hospital board-of-management roles to district trustees plus a Hospital Act appointee. This does not by itself identify the corporate hospital operator. Record the actual governance power body by body. Fort Nelson's first trustees were appointed and later boards elected, so even the electoral description needs dates. [OIC 1373/1958, PDF p. 5, cls 5–7](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1373_1958); [OIC 2195/1960, cl 5A](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/2195_1960).

Likewise, ministers should not appear only as recommending ministers. The evidence includes specific approval, appointment and inspection roles. Record them with dates and scope; none automatically creates a ministry responsibility line. Do not backdate a 2026 consolidated statutory provision to a district's 1967 foundation.

Hospital-district events should name the actual local corporate subjects even when their nodes are hidden. The current builder drops `related_subject_ids`, including recipients in the Greater Vancouver transfer event. Preserve subject and participant roles so the event can be found from both the transferring district and its recipients. [Event builder](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/scripts/build-government-events.mjs#L115-L138).

### The People node is present; relationship meaning is the urgent correction

The current view already puts the People node at the centre. The review reproduced a complete, uninferred accountability path for Powertech because its sourced `subsidiary_of` relationship becomes the generic `part` edge. That edge is then accepted by `pathToPeople`. Ownership evidence alone is therefore doing work the user's G1 rule expressly excludes. [Edge conversion](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/src/government/snapshot.js#L570-L594).

Preserve ownership, membership, administration, board appointment, funding, regulation, audit, complaints, service provision and ministerial responsibility as distinct relationships. Rendering a line and allowing it to count as political accountability are separate decisions. In particular, ordinary board appointments must not reuse the current traversable Premier-appointment edge type.

Local democratic routes need the actual historical electorate and representative institutions. Some improvement-district instruments use landowner qualifications; the whole population cannot be substituted for eligible electors. A services view can show residents, patients or ratepayers without implying a vote. Treaty First Nations governments belong alongside the Province as governments in their own right, linked by the evidenced treaties or agreements.

## 7. Other decisions to keep or tighten

- **Treasury:** keep the Finance and Agriculture alias and existing date-overlap filter. All 19 carried corroborations match their intended existing minister terms; they do not create new tenure boundaries.
- **1978 ministry:** keep the plural Communications title and corrected event ID. Add a legacy alias for the old singular ID so existing links still select the ministry. Its 1978–1979 span is consistent; absence in 1980 is expected.
- **EAB and Powertech:** keep the explicit dated decisions. EAB starts 1 January 1982. Powertech's company incorporation is 29 September 1988 and the naming event is 6 January 1989; neither supplies its unresolved operating-start date.
- **Decision replay:** currently stored decisions match their proposals. The converter replaces whole decision objects, so future manual decision edits must be made in the authoritative proposals or protected by a divergence check.
- **End events:** the sub-agency event generator currently labels every end `dissolved`. Use the documented event kind for rename, replacement, operational cessation and dissolution.
- **Ferry contract:** the recovered original starts 1 April 2003 for an initial 60-year term. Performance terms are separate: five years first, then four-year periods. The full catalogue has the original, the 2024 consolidation and 18 amendments. Two operative clauses additionally checked here give amendments 17 and 18 an effective date of 1 April 2024. Remaining work concerns particular clause-level changes, the executed 2003 corporate/share documents and the first Commissioner's personal appointment/report. [Original contract](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/passenger/coastal-ferries/coastal_ferry_services_contract.pdf), ss 1.01, 3.01–3.04; [amendment 17](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/passenger/coastal-ferries/cfs_contract_amend_agreement_no-17.pdf), cl 3.11; [amendment 18](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/passenger/coastal-ferries/cfs_contract_amend_agreement_no-18.pdf), cl 3.11.

## 8. Integration order and remaining research

First restore the complete source catalogue and component paths, preserving the supersession map. Then import the derived branch batch with the current review metadata protected. Correct the ownership traversal and entity-type issues as part of exposing its historical relationships. Reconsider the held source groups with their actual remaining gates, rather than clearing every hold merely because a URL is now available.

Next add structured lifespan/event meanings and field-level provenance. These are what allow the rural-board identities and local register to become visible without false survival, false dissolution or fabricated ministry chains. Repair the Harbours first-seen consumer, event participant indexing and the 1978 legacy-ID link. Finally regenerate all outputs, run the focused checks, and update WANTED from that state—including the missing minister-coverage metric.

The following remain genuine research questions after this reconciliation: the seven rural boards' legal endings or proved continuations; exact execution days of the 43 council amalgamations; remaining society asset transactions; the 1974 sheriff-consolidation instrument and earlier appointment/creation details; particular historical parent transfers; MTOC's eventual legal end; the full Hydro judgment/appellate record; Harbours' original creation and some transfer instruments; and the specific filing or organizational-identity questions retained in the component coverage files. No missing document has been converted into an invented date or relationship.

WANTED should distinguish **evidence not recovered**, **evidence supplied but not integrated**, **model support required**, and **specific editorial decision required**. These categories lead to different work. The complete handoff provides the claim/source mappings and preservation checks needed to make that distinction without repeating the research already done.

## Contents of the accompanying complete handoff

- `README.md`: exact package scope and import instructions.
- `sources.json`: all 1,492 catalogue entries with original retrieval/review status and preserved evidence references.
- `datasets/`: all 103 structured components, including 66 earlier components and 37 Round 4 components, with their exact nested names.
- `component-index.json`, `supersessions.json` and coverage files: path, checksum and review context.
- `integration/prior-branch-preserving-batch.json`: derived batch for the reviewed head; original batch preserved under `datasets/branches/`.
- `audit/`: code, Crown, model, source-recovery, branch-preservation and Forest Renewal/ferry reviews, plus machine-readable results and relevant test/build logs.
- `validation.json`: package integrity and simulation results.

The archive is a complete structured handoff and review. It does not resend every large source-original archive. Original URLs, retained archive paths and checksums remain in the catalogue, and selected exact locators remain attached to the claims. Source availability and import eligibility are separate fields throughout.
