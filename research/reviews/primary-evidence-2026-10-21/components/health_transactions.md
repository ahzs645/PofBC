# PofBC follow-up: actual society lifespans, ministerial accountability, and the remaining amalgamation-date problem

Research date: 21 October 2026. This is an evidence report; no repository or website changes were made.

## What this pass closes

The seven community health services societies can now be given registry-backed corporate lifespans: **registered 13 March 1997; dissolved 15 February 2002**. Each society has its own consecutive registration number, S0036593–S0036599. These dates come from credentials issued by **BC Corporate Registry** through the Province's OrgBook BC service, including the effective dates of converted historical events. The official OrgBook application decodes the relevant event as **“Conversion Society Dissolution”**. This is stronger than assuming that the societies ended on the December 2001 restructuring announcement. It still does not identify the instrument or exact day on which every asset moved. [HT09–HT16]

The full texts of **M298–M305/2001** are recovered. They replace society governors, effective **12 December 2001**, under the societies' bylaws. They do **not** dissolve the societies or convey their assets. That distinction is now directly established by the original documents, rather than left as uncertainty about what those orders might contain. [HT01–HT08]

The Ministry of Health relationship need no longer be a generic inferred placement. There is class-wide statutory evidence for regional boards and community councils, separate individual appointment evidence for every society, and a contemporary Auditor General account of funding agreements covering all three forms. The evidence also identifies two precise changes in the relationship: **25 August 1997**, when the council–board reporting and budget hierarchy was removed from the statute, and **5 June 2001**, when the Ministry of Health became **Health Services**, Health Planning was created, and the Health Authorities Act was expressly assigned to Health Services. [HT17–HT32]

The exact execution days of the **43 council-to-board amalgamation links identified in the previous pass** remain unproved. This pass does clarify what sort of instrument would settle them and why a board resolution or corporate registry certificate is not automatically the correct mechanism for a statutory council. It also finds the 1997 statutory validation of the earlier regulation. [HT29–HT36]

## 1. The seven societies: legal identities and four distinct dates

The following table distinguishes corporate registration, ministerial appointments, transition appointments, and corporate dissolution. The initial appointments all took effect 1 April 1997. That is not the same event as corporate registration on 13 March.

| Society name in 2001 | Registry number | Registered | Initial 1997 appointment order | Transition appointment order, effective 12 Dec 2001 | Registry dissolution |
|---|---|---|---|---|---|
| Cariboo Community Health Services Society | S0036598 | 13 Mar 1997 | M135/1997 | M299/2001 | 15 Feb 2002 |
| Coast Garibaldi Community Health Services Society | S0036596 | 13 Mar 1997 | M136/1997 | M300/2001 | 15 Feb 2002 |
| East Kootenay Community Health Services Society | S0036594 | 13 Mar 1997 | M145/1997 | M301/2001 | 15 Feb 2002 |
| Kootenay Boundary Community Health Services Society | S0036593 | 13 Mar 1997, as **Central Kootenay** | M144/1997, under original name | M302/2001 | 15 Feb 2002 |
| North West Community Health Services Society | S0036597 | 13 Mar 1997 | M137/1997 | M303/2001 | 15 Feb 2002 |
| Peace Liard Community Health Services Society | S0036599 | 13 Mar 1997 | M146/1997 | M304/2001 | 15 Feb 2002 |
| Upper Island/Central Coast Community Health Services Society | S0036595 | 13 Mar 1997 | M138/1997 | M305/2001 | 15 Feb 2002 |

Sources are the seven registry histories [HT09–HT15], event-label definition [HT16], original 1997 appointment orders [HT17–HT23], and December 2001 orders [HT01–HT08]. All primary source URLs and exact fields are in `health_transactions_sources.json`; the event-by-event records are in `health_transactions_claims.json`.

### A previously missing name change: Central Kootenay → Kootenay Boundary

This is one continuous society, **S0036593**, with a dated change of name:

| Effective period | Legal name in Corporate Registry credential | Registry event |
|---|---|---|
| 13 Mar 1997–20 Jan 1998 | CENTRAL KOOTENAY COMMUNITY HEALTH SERVICES SOCIETY | `Event:CONVSCREGI` |
| 21 Jan 1998–14 Feb 2002 | KOOTENAY BOUNDARY COMMUNITY HEALTH SERVICES SOCIETY | `Event:CONVSCNC`, effective 21 Jan 1998 |
| 15 Feb 2002 | Same final name, status becomes Historical | `Event:CONVSDIS` |

The registry supplies both names under the same topic and registration. The 1997 name is independently confirmed by M144/1997 and supplementary M141–M143/1997, which appoint members to Central Kootenay. The exact rename is therefore established by a corporate record, not inferred from similar territories or later lists. [HT12, HT16, HT20]

The Village of Montrose's minutes of 5 May 1998 also contain a notice acknowledging Central Kootenay's change to Kootenay Boundary. That municipal document was located by search at `https://dev.montrose.ca/wp-content/uploads/2024/08/05_may5-1998.pdf`, but its server returned 503 on full retrieval. It is a corroboration lead only; the exact-date claim relies on the retrieved registry history.

### What the converted registry evidence means

Each credential explicitly identifies its issuer as **BC Corporate Registry**, not an independent business directory. The first event carries a registration effective date of 13 March 1997, and the final event carries a status effective date of 15 February 2002. The credentials themselves were ingested much later; **record publication/issuance time must not be confused with historical event effective time**.

The code values are not guessed:

| Raw value | Official OrgBook English label |
|---|---|
| `ACT` | Active |
| `HIS` | Historical |
| `Event:CONVSCREGI` | Conversion Society Registration |
| `Event:CONVSCNC` | Conversion Society Name Change |
| `Event:CONVSDIS` | Conversion Society Dissolution |
| `Event:CONVSAMAL` | Conversion Society Amalgamation |

The labels were recovered from OrgBook's own deployed English language asset. Its source URL, downloaded bytes, and SHA256 are preserved. The distinction between dissolution and amalgamation labels helps avoid treating every Historical record as the same transaction. A dissolution record alone still does not tell us whether an earlier transfer agreement, statutory vesting, or another transaction moved the society's operations and property. [HT16]

**Repository consequence:** give the societies a corporate end date of 15 February 2002 with the precise basis “BC Corporate Registry converted historical dissolution event.” Keep the operational restructuring and replacement governors at 12 December 2001 as separate events. Leave asset-transfer instrument/date fields unknown until a conveyance, consent, audited closing note, or equivalent record is found.

### What M298–M305 actually do

M298 rescinds all appointments to the seven named societies by amending a list of earlier appointment orders. M299–M305 then appoint replacements to each society. The Minister is **Colin Hansen, Minister of Health Services**; the cited authority is the society's **bylaws**. The operative date in every order is **12 December 2001**. The signatures of M298 and M305 were visually checked as **11 December 2001**. The other orders' operative dates are clearly typed; their handwritten signing dates have not been separately assigned in the data. [HT01–HT08]

The replacements include the relevant new authority chairs alongside other members. For example, Alan Dolman appears in the Cariboo, East Kootenay and Kootenay Boundary orders; Harry Gairns appears in North West and Peace Liard. That establishes transitional governance participation, not legal merger of every listed society into the corresponding authority. Cariboo's geography in particular was divided between successors, so a whole-society merger edge into two corporations would need its own evidence.

There is subsequent legislative cleanup: **OIC148/2002**, approved 21 February and deposited as **B.C. Reg.38/2002 on 22 February**, removes the old bodies, including all seven societies, from the Health Care Employers Regulation's designation list and adds the six new health authorities. Publication in the Gazette was 26 February. None of those three dates should replace the registry dissolution date or be called an asset transfer. [HT33]

## 2. The ministry relationship: evidence for each legal form

### Boards and councils: statutory accountability, not ministry departments

The Health Authorities Act defines “board” and “council” by legal designation. Its requirements apply to **every** body in those classes; it is not necessary to find 44 separate annual reports repeating the same statutory obligation. The member of the graph must first be identified as a legally designated board or council. The companion designation research supplies that identity work. [HT25]

The statute supplies concrete relation types:

| Relationship | Provision in the 2001 historical consolidation |
|---|---|
| Minister designates regional board; appoints its members | s.4 |
| Board reports on its activities and submits budgets to minister | s.5(1)(a)(v), (b) |
| Minister designates community health council; appoints its members | s.6 |
| Council reports on its activities and submits budgets to minister | s.7(1)(a)(ii), (d) |
| Board/council follows minister's general or special directions | s.7.1 |
| Minister approves board/council bylaws | s.8(2) |
| Minister receives accounts, can inspect financial records, sets report form | s.10(1), (2), (5) |

The corporations are legally distinct from ministry branches. Their capacity, own officers and employees, and the general nonapplication of the Public Service Act are expressly addressed in ss.8 and11. Therefore a graph edge should say, for example, **“reports to the responsible minister,” “minister appoints members,”** or **“funded under provincial agreement”**. It should not imply that a council was an internal Ministry of Health division. [HT25]

The machine-readable file contains individual accountability records for all **44 bodies in the December 2001 statutory schedule**: 11 regional boards and33 councils, including the two transitional health authorities that were legally council designations. Seven society records bring this inventory to51. This is a **2001 constituent inventory**; the 1997 11-board/34-council/7-society roster totals52. Those counts refer to different snapshots.

### Do not apply the post-August 1997 hierarchy backward

The older statute required councils to report to **both the regional board and the minister**, and to submit budgets for regional services to the board. Regional boards likewise reported to councils as well as the minister, and allocated grants among councils. Councils also participated in regional board membership. These were real statutory relationships, not merely lines inferred from a regional map. [HT32]

**SBC1997c23**, ss.5–11, changed this model. Its sections6 and8 remove the interposed reporting requirements; council budgets go directly to the minister; appointments are revised; ministerial approval of bylaws and a general/special direction power are introduced. Assent was **28 July 1997**, but the operative change was **25 August 1997**, under **B.C. Reg.294/97**. The official table of legislative changes records that commencement precisely. [HT30–HT31]

The 1997 Auditor General review concerns administrative processes already operating from 1 April. It therefore complements the legislation rather than allowing us to assume every administrative and statutory change happened on one day. The accurate timeline can represent April funding/operational transfer and August legislative revision separately.

### Societies: direct bylaws appointments and funding agreements

For the seven societies, it would be insufficient to cite board/council provisions as if every “health authority” were legally the same kind of corporation. All seven original appointment orders were recovered:

- M135, M136, M137, M138, M144, M145 andM146/1997 appoint members effective **1 April 1997**.
- Each names **Joy K. MacPhail, Minister of Health and Minister Responsible for Seniors**, as the decision-maker.
- Each invokes the society's **bylaws**. M145 andM146 are visually verified as signed **27 March 1997**. [HT17–HT23]

There is also an unusually direct collective source. The Auditor General explains that the **Funding and Transfer Agreement** is a contract between each individual health authority and the Province, represented by the Minister of Health. The paragraph then expressly distinguishes regional boards, councils and societies and describes the obligations of councils and societies under their agreements. See **printed p.31, PDFp.35**, visually verified. That is evidence of each society's provincial funding/accountability relationship, not just of its presence in a list. [HT24]

The same report, **printed p.34, PDFp.38**, says that Health leads overall funding and contracting, including program funds for the Ministry for Children and Families. Children and Families leads policy for the programs transferred to it; its regional operating officers review the relevant portions of allocation plans, while Health signs off the whole plan. The report records uncertainty in practice about the limits of accountability. A graph should therefore use a program-specific Children and Families policy connection where supported, not replace Health with an exclusive Children and Families parent. [HT24]

Printed p.33 names the program families: public health speech, audiology, nutrition and dental services; public health nursing for children and youth; related forensic psychiatric services; child and youth mental health; infant and child development; and alcohol and drug programs. It describes new relationships particularly with regional boards and community health services societies. The report does not give a program-by-program assignment to every one of the51 historical entities. The machine-readable data therefore preserves this as a **conditional program relationship**, not51 identical program portfolios. OIC565/2001, Appendix A s.41, transfers alcohol, drug and gambling addiction responsibilities back to Health Services on5June2001; that provision does not end every other Children and Families relationship. [HT24, pp.33–34; HT26, s.41]

The Auditor General also expressly identifies **local communities** as an accountability audience on printedp.1. That provides a source-backed public-accountability connection relevant to putting the people served at the centre of the graph. The boards and councils' statutory public-meeting rule in s.8(3) supplies a concrete participation mechanism. Neither source means that every governor was directly elected by the public. [HT24–HT25, HT32]

### The exact 2001 split: Health Services and Health Planning

**OIC565/2001, approved 5 June 2001**, makes the legal distinction precise:

| Provision | What changes |
|---|---|
| Appendix A s.37 | Establishes Ministry of Health Planning |
| Appendix A s.38 | Transfers planning, policy/program development, resource allocation/capital planning, evaluation and delivery-monitoring functions to Planning |
| Appendix A s.39 | Transfers Provincial Health Officer and Legislation and Professional Regulation Branch to Planning |
| Appendix A s.40 | Renames Ministry of Health as Ministry of Health Services |
| Schedule B s.12 | Assigns **Health Authorities Act** administration to **Minister of Health Services** |

The first provisions are on PDFpp.4–5. ScheduleB s.12 is printedp.20, PDFp.27 and was visually checked. ScheduleB s.11 is Planning's Act list and does not assign the Health Authorities Act to it. [HT26]

The two 2001/02 annual reports explain the complementary implementation roles. Services supplies funding and operational direction and monitors authorities; Planning sets system expectations, policy and standards; authorities manage and deliver services. This supports a functional Planning connection beside the statutory Services connection, not collapsing them into a single undifferentiated parent. [HT27, printedpp.9,11; HT28, printedp.4]

For statutory boards/councils the legal administrator boundary is directly proved on **5 June**. For societies, the ministry rename and transfer of Health's continuing responsibilities supports continuity, and the **12 December orders individually prove Health Services exercising the bylaws appointment power**. The data explicitly identifies this reasoning rather than pretending the HAA's board definition applies to societies.

## 3. The 1996 council mergers: what was established and what remains missing

The predecessor groups remain those in M432, M441 andM444/1996. The original orders make rescission conditional **on an amalgamation**. Some application language appears within those conditional clauses themselves. Neither a document's signing date nor a later schedule listing only the successor is independent proof that the legal merger happened on a particular day. [HT34–HT36]

Three different legal mechanisms need to be kept separate:

| Type of transaction | Historical mechanism | What would settle an exact date |
|---|---|---|
| Two or more old councils → a new council | Reg338/96 s.3: geographic containment and appointment of new council members | The first effective new-council appointment, read with the designation and scope of s.3 |
| Council(s) → a regional board | Reg338/96 s.4, added by Reg361/96: containment and minister specifies application; assets vest without further act/deed | An operative ministerial specification or contemporaneous implementation record establishing when the conditional order took effect |
| A designated corporation, such as a hospital society → board/council | HAA s.16: corporation and board/council consents, minister consent; special corporate resolution; certified evidence; Registrar notification | Consent/certificate and stated effective date, or the registrar's corresponding record |

The first two are not automatically governed by the third procedure. Asking only for corporate merger certificates could miss the relevant evidence for statutory councils. Conversely, identifying a Society Act corporation with the same words in its name is not enough to identify the statutory council. [HT25, s.16; HT29, ss.3–4]

There is valuable later confirmation: **SBC1997c23 s.18, printed/PDFp.12**, validates Reg338/96 effective **29 November 1996** and its Reg361/96 amendment effective **13 December 1996**. It also validates the amalgamations referred to by the regulation. It does **not** enumerate the individual councils' completion dates. This closes a question about legislative validation of the mechanism, not the user's requested day-by-day execution list. [HT30]

The Auditor General's timeline on printedp.28 includes a planned March1997 amalgamation milestone. It is explicitly a ministry implementation schedule. Treating that planned day as a completed transaction for all councils would overstate the evidence. The same report's confirmed April/October operational devolution dates describe service responsibility, not every legal council merger. [HT24]

### Four 1997 council mergers: exact member-appointment triggers recovered

The later council-to-council consolidations have a more explicit statutory trigger: appointment of the new council members. The designation researcher recovered the original appointment orders, and this pass visually verified every signing date and the typed **effective immediately** instruction.

| New council | Predecessor councils | First new-member order and effective date | Companion designation |
|---|---|---|---|
| Houston/Smithers | Houston; Smithers and Area | M49/1997 — **31 January 1997** | M52/1997, order s.2 and regulation s.2 |
| Chetwynd/Peace River South East/Tumbler Ridge | Chetwynd; Peace River South East; Tumbler Ridge | M50/1997 — **31 January 1997** | M52/1997, order s.4 and regulation s.4 |
| Fort St. John/Hudson's Hope | Fort St. John and District; Hudson's Hope | M51/1997 — **31 January 1997** | M52/1997, order s.3 and regulation s.3 |
| Campbell River/Nootka | Campbell River and Area; Nootka | M98/1997 — **4 March 1997** | M96/1997, order s.2 and new regulation s.27 |

Each appointment order also rescinds the old councils' member appointments. Under historical Reg338/96 s.3, the appointment is the merger trigger when the predecessor areas are contained in the designated new-council area. These dates are therefore strong candidate amalgamation dates, supported by a specific legal trigger rather than a generic operational milestone. [HT29, HT37–HT42]

One remaining condition prevents presenting them as unconditional legal completion dates: the companion designation regulation's deposit/commencement must be confirmed. M52 is signed/stamped31January1997; M96's handwritten dating has ambiguous4/11March indications. The records now distinguish the **proved appointment date** from the **conditional amalgamation inference**. These four1997council-to-council transactions do not close the separate43council-to-board links in the1996orders. No certificate has been manufactured or assumed necessary for the regulation's appointment-trigger mechanism.

### Remaining search targets and public-access limits

The most useful remaining records are the Ministry of Health's 1996–97 legal implementation correspondence, original ministerial specifications, successor board closing/opening statements, and board/council minutes that identify the precise statutory merger date. For actual hospital or society transfers under s.16, seek the written consents, certified proof and Registrar notification. For the seven 2002 society asset handovers, seek asset-transfer agreements, final audited notes and dissolution filings using the exact S-numbers above.

Public OrgBook searches for representative council/board names did not identify the statutory entities needed to close the 1996 dates. They did expose separate societies, including a **Revelstoke Community Health Council** society registered10December1991 and dissolved21July1995, and a **Capital Health Council Society**. These are leads for earlier local organizing history; they have not been equated with the statutory successors.

The official CIVIX GazettePartI catalog exposed in this pass starts in2003; the Corporate Registry societies/firms notice catalog starts in2011. An Internet Archive `bcgazette` collection query returned no2002issues. Thus failure to retrieve a February2002Gazette notice is an identified coverage gap, not proof that no notice exists. The registry evidence now resolves society dissolution despite that gap. The 1996 statutory council execution days remain the principal unresolved item in this part of the research.

## Deliverables and source handling

- `health_transactions_sources.json`: 42 source entries HT01–HT42, with exact sections/pages/fields, source URLs, reviewed status, and raw-file checksums where files were downloaded.
- `health_transactions_claims.json`: seven society lifespans and full registry event chains; 51 individual accountability records; dated statutory changes; four1997new-council appointment triggers; explicit unresolved asset-transfer and1996execution fields.
- `orgbook_legacy_society_event_labels.json`: official legacy society event-label extract for reuse in the Crown/PHSA inventory.
- `health_transactions_raw/`: original ministerial orders, registry histories, reports, Gazette amendment and visual-check images.

The primary changes to make from this evidence are precise society dates and aliases, explicit ministerial relation types with temporal changes, and the correction that M298–M305 are governance orders. The remaining nulls are deliberate: the absence of exact transfer or statutory execution evidence is preserved rather than replaced by a plausible date.
