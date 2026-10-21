# Crown relationships and sheriff history — follow-up evidence

Research completed: 21 October 2026. This is a source-led research deliverable, not a repository patch. Source IDs resolve to `crowns_sheriffs_sources.json`. Original Gazette pages and material statutory/financial-note pages were visually checked against the scans.

## What the evidence now changes

| Subject | Finding that can be used now | Remaining limit |
|---|---|---|
| Nine sheriff offices | A statutory Gazette roster names all nine offices, their officers, addresses and bailiwicks. There were eight counties, with Cariboo split into two sheriff jurisdictions. | Exact administrative instrument/day joining the offices in 1974 remains unlocated. |
| Sheriff jurisdiction | Province-wide jurisdiction commenced on **20 June 1974** under SBC 1974 c. 87, s. 35. | This must not be relabelled the administrative merger date. |
| Modern B.C. Ferry Authority | Established **1 April 2003**, under the Coastal Ferry Act, ss. 2 and 89. | The operator converted the following day; the two entities need different events. |
| Homeowner Protection Office | Statutory establishment **21 September 1998**; office opened **1 October 1998**. | Original OIC 1188/1998 obtained and verified; OIC 1146/1998 also proves the initial ministerial connection. |
| Provincial Rental Housing Corporation | Same corporate identity from **Pemco Holdings Ltd., 13 December 1961**, through two exact name changes in 1976. | The underlying incorporation certificate was not obtained; the Registrar's contemporary Gazette notice was. |
| PRHC relationship changes | Province acquisition in **1973**; BC Housing gained control **26 January 2024**, with accounting consolidation from **31 March 2024**. | Exact 1973 transaction date/instrument and a 2024 share transfer are not established. |

## 1. All nine sheriff offices before the 1974 reorganization

**Original source:** *British Columbia Gazette*, 5 July 1973, printed p. 2616, middle column (PDF page 14). The notice itself is dated **21 February 1972**. It was republished in July 1973 under the annual reporting requirement of the Sheriffs Act. Treat this as a dated roster, not as nine office-creation notices. [CS01, CS02]

| Gazette bailiwick | Sheriff named | Office address as published |
|---|---|---|
| County of Westminster | G. K. Herbert | Courthouse, 653 Clarkson Street, New Westminster |
| County of Cariboo, **except the Peace River Electoral District as constituted on 1 June 1953** | A. W. Davis | Courthouse, 1600 Third Avenue, Prince George |
| County of Kootenay | T. G. C. Fox | Courthouse, 320 Ward Street, Nelson |
| County of Victoria | W. A. Lee | Law Courts, 850 Burdett Avenue, Victoria |
| County of Nanaimo | L. F. Hodgson | Courthouse, Front Street, Nanaimo |
| County of Yale | E. E. Allen | Courthouse, 166 Seymour Street, Kamloops |
| County of Vancouver | E. W. Wells | Courthouse, 800 West Georgia Street, Vancouver 1 |
| County of Prince Rupert | J. Needham | Courthouse, Market Street, Prince Rupert |
| **Portion of the County of Cariboo embraced in the North and South Peace River Electoral Districts** | D. W. Sutton | Courthouse, 5107–50th Avenue, Pouce Coupe |

The roster resolves the apparent numerical problem: **nine sheriff offices did not require nine counties**. A dataset should not invent an Atlin office or split Kootenay into East and West merely to reach nine. The two Cariboo bailiwicks should retain the qualifications given in the source. The addresses and officeholders are attributes at the source date; they should not become timeless labels. [CS01]

The Sheriffs Act, RSBC 1960 c. 355, s. 4 required Gazette publication during July of the names of sheriffs, office locations and bailiwick limits. Publication by the Deputy Provincial Secretary is not itself evidence of departmental reporting to the Provincial Secretary. [CS02]

### 1974: separate the organizational event from the jurisdictional statute

The government's sheriff history dates amalgamation of the nine county sheriff offices into the provincial service to **1974**. [CS03]

A precise legal reform is now identified: **Statute Law Amendment Act, 1974, SBC 1974 c. 87, s. 35**, printed p. 547. It amended s. 3 of the Sheriffs Act to give each sheriff jurisdiction throughout the Province. Section 42(1), printed p. 550, brought s. 35 into force on Royal Assent, **20 June 1974**, recorded on the Act's first page. [CS04]

That statute does **not** expressly abolish or combine nine administrative offices. Recommended events are therefore:

- `organizational_amalgamation`, date `1974`, precision `year`, supported by official institutional history;
- `jurisdiction_expanded`, date `1974-06-20`, precision `day`, instrument `SBC 1974 c87 s35`.

Contemporary Hansard is useful corroboration, not a substitute for an unlocated administrative instrument. On 6 June 1974 the Attorney General described the new service, its first trained class and expansion plans. On 20 June the debate explained cross-county jurisdiction and court-security/prisoner-transport duties. [CS05, CS06]

**Still open:** a cabinet order, Treasury Board decision, departmental reorganization memorandum or contemporary annual report that explicitly records the administrative combination and its effective day. The scanned statute supplies a legal milestone; it does not close that separate gap.

## 2. Modern B.C. Ferry Authority: exact creation and distinct relationships

The **Coastal Ferry Act, SBC 2003 c. 14**, received Royal Assent on **27 March 2003**. Section 2(1) establishes the B.C. Ferry Authority; s. 89 brings the Act into force on **1 April 2003**. The Authority has no share capital under s. 2(4). Its statutory role and ownership of the voting share connect it to the operator. [CS07]

The regulator's history dates conversion of **British Columbia Ferry Corporation** into **British Columbia Ferry Services Inc.** to **2 April 2003**. This is a different entity/event from the Authority's establishment on 1 April. Section 20(3) of the Act ties the end of the operator's Crown-agency status to conversion. [CS07, CS08]

Recommended representation:

| Entity/event | Date | Event type |
|---|---|---|
| Coastal Ferry Act assented to | 2003-03-27 | legislation_assented |
| Modern B.C. Ferry Authority established | 2003-04-01 | statutory_establishment |
| Ferry operator converted to British Columbia Ferry Services Inc. | 2003-04-02 | corporate_conversion |
| Operator's Crown-agency status ceased | On conversion | legal_status_change |

Keep the **modern 2003 Authority** distinct from the similarly named **1964–1977 ferry operator authority**. Likewise, separate voting-share ownership/oversight, government contracts/subsidies and independent regulation rather than using one generic parent link. Initial 2003 board mechanics should be sourced from the contemporary Act, not assumed from the current amended consolidation. [CS07, CS08]

## 3. PRHC: original incorporation, two name changes, Crown acquisition and control

### Corporate identity is now proved by three original Gazette notices

| Effective date | Name / event | Original source |
|---|---|---|
| **1961-12-13** | **Pemco Holdings Ltd.** incorporated under the Companies Act, company No. **52129** | Gazette, 21 December 1961, p. **2290**, right column, PDF p. 50. [CS12] |
| **1976-05-07** | Renamed **British Columbia Housing Corporation** | Gazette, 27 May 1976, p. **715**, right column, PDF p. 17. [CS13] |
| **1976-12-21** | Renamed **Provincial Rental Housing Corporation** | Gazette, 13 January 1977, p. **42**, middle column, PDF p. 14. [CS14] |

All three notices use company No. 52129; both name-change notices repeat the 13 December 1961 incorporation date. They establish **one continuing corporation with successive names**, not three mergers or separate bodies. The present BC Corporate Registry credentials for **BC0052129** independently corroborate the date sequence. [CS12–CS15]

The 1961 notice is the original Registrar's published incorporation evidence. It is not a special PRHC Act and does not show that the later name existed in 1961. A legal-record field should identify `Companies Act incorporation, company No. 52129`, with the Gazette notice as evidence; it should not invent a special founding Order in Council. The underlying certificate remains a distinct document that could be requested from the registry. [CS12]

### Acquisition by the Province must be a separate event

The Auditor General's 1999/2000 Social Housing report identifies **1973** as the Province's acquisition year (printed p. 60). Thus the 1961 incorporation date must not automatically start a provincial ownership edge. The same report records a change in ministerial responsibility for both BC Housing and PRHC on **21 July 1999**, from Employment and Investment to Social Development and Economic Security (printed p. 35). Neither the exact 1973 acquisition day nor its transaction instrument is supplied. [CS16]

Hansard of 29 June 1976 gives useful contemporary context: Hugh Curtis discussed the previously inactive Pemco company and its new housing-finance role under the British Columbia Housing Corporation name. [CS17]

### BC Housing management, common control and 2024 control are different links

The 2022 PRHC financial statements identify PRHC as wholly owned by the Province and a Crown agent; BC Housing was related through common provincial control and managed the rental properties. This supports separate ownership and management relationships. [CS18]

The audited **2023/24 BC Housing** financial statements, note 1, printed p. 10 / PDF p. 43, provide an exact later boundary: a change in governance and board appointment arrangements gave BC Housing **control of PRHC on 26 January 2024**. The Commission elected to consolidate PRHC from **31 March 2024**. Note 20 explains the consolidation. [CS19]

Use `controlled_by` from **2024-01-26** and a separate accounting-consolidation event dated **2024-03-31**. These audited words do **not** prove that the Province transferred its shares on either date. A description such as “subsidiary” in later financial reporting cannot, by itself, substitute for the share register or transfer instrument. [CS19]

## 4. Homeowner Protection Office: three dates with different meanings

| Date | Meaning | Evidence |
|---|---|---|
| **1998-07-30** | Royal Assent to Homeowner Protection Act, SBC 1998 c. 31 | Act header. [CS09] |
| **1998-09-21** | Section 3 establishing the Office came into force, among original ss. 1–13 | Original **OIC 1188/1998**, approved 16 September 1998; legislative-change table identifies **B.C. Reg. 309/98**. [CS10, CS21] |
| **1998-10-01** | Office opened | HPO's 2003 service plan, printed p. 3. [CS11] |

A founding date should use **21 September 1998** for statutory establishment, with **1 October 1998** retained as opening/operations. The service plan's reference to passage on 28 July is not Royal Assent; the Act itself supplies 30 July. Also distinguish later commencement of the full builder-licensing/warranty regime from creation of the Office. [CS09–CS11]

**Original instruments now obtained:** OIC **1188/1998**, approved **16 September 1998**, explicitly brings ss. 1–13 (including the Office-creation provision), 19, 24–29, 31–36 and 38 into force on **21 September 1998**. OIC **1146/1998**, approved the same day, assigns administration of the Homeowner Protection Act to the **Minister of Municipal Affairs** under Constitution Act s. 10. Both one-page signed originals were downloaded from BC Laws and visually checked. These close the original-instrument and initial-ministerial-link gaps. [CS21, CS22]

The 2010 functions divide matters for a historical graph: HPO regulatory, research and education responsibilities moved to BC Housing from **1 April 2010**, while reconstruction-loan responsibilities moved to Finance. A single all-functions-successor edge would conceal the split. [CS20]

## 5. Evidence and implementation rules arising from these findings

1. Store the same body's historical names as dated labels; use succession edges only when a distinct body succeeds another.
2. Keep event precision explicit: a verified year must not become 1 January of that year.
3. Separate legislative assent, statutory commencement, incorporation, operational opening and accounting consolidation.
4. Distinguish ownership, board appointment/control, property management, funding, ministerial accountability and statutory regulation.
5. Attach an as-of date to officeholder and address observations.
6. Record remaining gaps as specific missing instruments, without weakening the facts already established by original evidence.

## Search coverage and unresolved items

This follow-up checked original historical statutes, contemporary Hansard, official legislative-change tables, statutory Gazette rosters and company notices, Corporate Registry credentials, Auditor General governance work, audited financial notes, and official institutional histories. Internet Archive's scanned Gazette issues supplied original documents not reliably discoverable through general web search. Relevant original pages were visually checked because OCR sometimes misread names, dates or page numbers.

The remaining material gaps are the **1974 administrative sheriff amalgamation instrument/day**, the **exact 1973 provincial acquisition instrument/day for Pemco**, and the **underlying 1961 incorporation certificate** (the contemporary Gazette incorporation notice is obtained). The HPO original commencement order and contemporaneous assignment of statutory administration were located and verified. A bounded catalog scan of OICs 1100–1299/1998 returned the two relevant instruments with no failed downloads.
