from pathlib import Path
import json,re

B=Path(__file__).resolve().parent
sources={s['id']:s for s in json.loads((B/'sources.json').read_text())}
rhd=json.loads((B/'hospital_districts.json').read_text())
hid=json.loads((B/'hospital_improvement_districts.json').read_text())
claims=json.loads((B/'claims.json').read_text())
def cite(s):
    if isinstance(s,int):s=f'R4R-{s:03d}'
    return f'[{s}]'
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in rows])
def short(name):return name.replace(' Regional Hospital District','')

parts=['''# PofBC — Hospital districts, commencement dates and the people: Round 4

Research cutoff: **21 October 2026**. Repository baseline: `0f1587c5e982135f155ba6660af5192509351511`, branch `claude/compassionate-bohr-octofh`. This is a research and modelling handback. The repository and website have not been changed.

## What the new evidence changes

The health-system history can now include **25 hospital improvement districts with original incorporation instruments**, and **43 distinct regional hospital district identities**. This establishes a substantial local-finance and governance history before the 1990s health boards and the 2001 health-authority restructuring. It also prevents several misleading shortcuts: same-named corporations were sometimes different bodies, powers could be curtailed without dissolution, and one transfer could distribute assets among several recipients.

The regional hospital district register contains **28 original incorporations in 1967–68, 12 new incorporations effective 1 January 1996, and three additional identities**—Fort Nelson-Liard, Fraser Valley and Stuart-Nechako. It is a reviewed set of identities and events, not a claim that every district boundary or every surviving corporation has been exhaustively traced. A blank ending date means that this module has not proved the ending. It does not affirm present survival.

The hospital improvement district register contains all **23 corporations named in the 1969 dissolution/transfer schedule**, plus Fort Nelson and 100 Mile House, whose later orders attach certified board resolutions for onward hospital-society transfers. The earliest original in this set is Creston Valley in **1951**. This is the earliest in the recovered set, not a claim that hospital governance in BC began in that year. [R4R-115][R4R-118][R4R-121][R4R-163][R4R-164]

The underlying model needs separate identities for a **hospital improvement district**, a **regional hospital district**, a **municipal regional district**, a **health board or authority**, a **hospital society**, and a **service or program**. Similar geography, directors, names or functions do not by themselves make them the same legal body. The examples below supply actual transfer and continuation instruments with which to connect them.

## 1. The 25 hospital improvement districts

### All 23 predecessors in the 1969 transfer schedule

**OIC 3082/1969, approved 25 September 1969**, dissolves the 23 listed hospital improvement districts under section 50C of the Regional Hospital Districts Act. It transfers all their real and personal assets, rights, claims, obligations and liabilities to the regional hospital district paired with each in its schedule. The instrument does not merely announce a future reorganization. [R4R-115, operative clause and schedule]

Each start below is supported by the original letters patent. Original witness dates were independently checked against the scans. Names are the original corporate names; where the 1969 schedule uses a later number or abbreviated name, the machine-readable register preserves that observation separately.
''']
dest={r['from_id']:r['to_id'] for r in hid['relationships'] if r['type']=='assets_rights_and_liabilities_transferred_to'}
rby={e['id']:e for e in rhd['entities']}
rows=[]
for h in hid['entities'][:23]:
    rows.append([h['original_name'],h['legal_start'],short(rby[dest[h['id']]]['original_name']),cite(h['start_source_ids'][0])])
parts.append(table(['Original improvement-district name','Incorporated','Recipient on 25 September 1969','Original start'],rows))
parts.append('''
The 1969 schedule adds numbers to several names that did not contain them in the original letters patent. It calls Windermere “Windermere Hospital Improvement District No. 7” where the original includes “District” before “Hospital”; it abbreviates Prince George’s original “and District” name. Those variations are not assigned guessed renaming dates. One bridge has been recovered: **OIC 1976/1955, 6 August 1955**, adds **No. 3** to Castlegar’s name. [R4R-115][R4R-152]

### Fort Nelson and 100 Mile House: two documented onward transfers

| Stage | Fort Nelson | 100 Mile House |
|---|---|---|
| Original improvement district | **7 June 1958**, OIC 1373/1958. [R4R-154] | **4 August 1960**, OIC 1835/1960. [R4R-164] |
| Early governance change | **7 July 1959**, replacement letters patent expressly continue the corporation; five trustees elected at large, and ambulance services added. [R4R-155] | Zones 4 and 5 amended **9 September 1960**; trustees plus a Hospital Act appointee made hospital board **27 September 1960**. [R4R-166][R4R-165] |
| Hospital society incorporated, as reported in later order | **18 October 1971**, Fort Nelson Hospital Society. [R4R-118, p1] | **17 November 1971**, 100 Mile District Hospital Society. [R4R-163, p1] |
| Certified regional-board resolution adopted | **23 May 1972**, with effect on the improvement district’s dissolution. [R4R-118, p4] | **6 April 1972**, with effect on the improvement district’s dissolution. [R4R-163, p3] |
| Improvement district dissolved; first statutory transfer | **13 June 1972** to Peace River-Liard Regional Hospital District. [R4R-118, pp1–2] | **12 May 1972** to Cariboo Regional Hospital District. [R4R-163, pp1–2] |
| Onward transfer under attached resolution | To Fort Nelson Hospital Society, from the same dissolution date, with the stated financial/debt exceptions. | To 100 Mile District Hospital Society, from the same dissolution date, with the stated financial/debt exceptions. |

These cases support two successive relations: **improvement district → regional hospital district**, followed by **regional hospital district → hospital society**. The regional district retains financial functions and long-term debt already assumed. The society receives the operating-property package described by the resolution. The original society registry certificates and separately executed conveyances are not attached; the report therefore identifies the exact evidence as order recitals and certified operative resolutions, respectively.

The 100 Mile House case supplies a further date correction. The 1972 recital says the hospital-board amendment was issued **26 September 1960**. The recovered original OIC 2195/1960 shows the recommendation signed on the 26th but the order approved and ordered on **27 September**. The original approval date is the supported order event. The disagreement is preserved in `conflicts.json`. [R4R-163][R4R-165]

### How these districts connected to electors

The original letters patent usually establish elected trustees through district or zone meetings, but the electorate is qualified by **Canadian citizenship, age 21, provincial-voter eligibility and landownership or a specified representative capacity**. The detailed conditions, trustee numbers and zone allocations are transcribed into `hid-verification.json` and attached to each entity. These are original-date rules; subsequent amendments were not exhaustively traced.

There are important individual variations. Gulf Islands permits proxy voting by otherwise qualified voters whose lands are outside Salt Spring Island. Creston’s candidate wording includes certain spouses without automatically making every spouse a voter. Fort Nelson’s first trustees were named in the 1958 letters patent; later boards were elected. Its original rule excluded practising physicians and hospital employees as trustee candidates, while the 1959 replacement uses a different candidate clause. A universal “all people elect this board” line would erase these distinctions. [R4R-120][R4R-121][R4R-154][R4R-155]

The original instruments also require financial statements and meeting minutes to be filed with the **Comptroller of Water Rights**. That is a records/reporting relation under the Water Act framework. It should not be rendered as proof that a hospital district was simply a Health Ministry branch. [Original letters patent cited in the table; per-body clause locators in `hid-verification.json`.]

## 2. Original regional hospital district incorporations, 1967–68

**OIC 1222/1967, 13 April 1967**, establishes 27 geographic areas for the new framework. It is not the common birthday of all the corporations subsequently incorporated. The 28 original letters-patent corporations recovered here have the following individual dates. [R4R-002]
''')
rows=[]
for e in rhd['entities']:
    if e['cohort']!='original_1967_1968':continue
    later='; '.join(n['name'].replace(' Regional Hospital District','')+' ('+(n.get('valid_from') or 'observed '+n.get('observed_by','date unknown'))+')' for n in e['names'][1:]) or '—'
    rows.append([short(e['original_name']),e['legal_start'],later,cite(e['start_source_ids'][0])])
parts.append(table(['Original corporation','Incorporated','Selected later names','Original source'],rows))
parts.append('''
**OIC 527/1972, 8 February 1972**, amends 28 existing regional hospital districts to align municipal membership, electoral areas and voting units with their corresponding municipal regional districts. It recites the regional-director board arrangements. It is a coordination amendment, not 28 new incorporations. A later recital that calls this the original letters-patent date should not reset the corporation’s start. [R4R-037]

### Later recitals are not always reliable dates

The following disagreements were resolved in favour of the original instrument while retaining the later statement for audit:
''')
rows=[]
for c in rhd['conflicts']:
    label=short(rby[c['subject']]['original_name']) if c['subject'] in rby else next((e['original_name'] for e in hid['entities'] if e['id']==c['subject']),c['subject'])
    rows.append([label,c['later_claim'],c['accepted_date'],cite(c['original_source'])+'; comparison '+cite(c['later_source'])])
parts.append(table(['Subject','Later statement','Accepted original date','Evidence'],rows))
parts.append('''
The Skeena-Queen Charlotte example is especially consequential: its 2021 dissolution instrument refers to letters patent dated 8 February 1972, but the original Skeena A incorporation is **17 August 1967**. The 1972 document is supplementary. Similar “continued” and “reissued” wording occurs throughout the district family, making identity-based matching safer than taking every letters-patent date as a new entity.

## 3. The 1995–98 reorganization: restriction, new corporations, then partial reversal

### December 1995 and January 1996

**OIC 1549/1995**, approved 14 December and effective **31 December 1995**, restricts 24 older regional hospital districts to specified capital projects, debt requirements and minister-approved powers. It does not dissolve them. [R4R-003]

The following 12 **new** regional hospital districts begin **1 January 1996** under orders approved 14 December 1995. Their final commencement clauses control. In particular, the new Cariboo, East Kootenay and North Okanagan corporations must remain separate from older corporations with the same names. [R4R-040]–[R4R-051]
''')
rows=[]
for e in rhd['entities']:
    if e['cohort']!='new_1996':continue
    names='; '.join(short(n['name'])+' — '+str(n.get('valid_from')) for n in e['names'][1:]) or 'No rename established here'
    rows.append([short(e['original_name']),names,e['legal_end'] or 'No end proved here',cite(e['start_source_ids'][0])])
parts.append(table(['New corporation, 1 January 1996','Later names in this register','Express ending recovered','Original source'],rows))
parts.append('''
**OIC 524/1996, 18 April 1996**, supplies twelve sets of supplementary letters patent, revising membership, boundaries and board arrangements. **OIC 416/1997, 3 April 1997**, then renames three continuing 1996 corporations: Cariboo → Cariboo-Coast, East Kootenay → Kootenay East, and North Okanagan → North Okanagan/Columbia Shuswap. These are regional **hospital district** renames; they are not evidence for the separate health-board-to-“Health Region” name changes. [R4R-116][R4R-088]

### The 1998 omnibus order

**OIC 1429/1998, 19 November 1998**, does three different things that the atlas should encode separately. First, it removes the restrictive 1995 clauses from **13 continuing older districts**: Alberni-Clayoquot, Central Coast, Central Okanagan, Comox-Strathcona, Cowichan Valley, Fort Nelson-Liard, Fraser-Fort George, Mount Waddington, Nanaimo, Okanagan-Similkameen, Peace River, Powell River and Sunshine Coast. These are restored powers, not new incorporations. [R4R-106, Schedule A §§1,3,4,7–12,16,18,19,21]

Second, it dissolves five of the 1996 corporations on **31 December 1998**, directing these transfers:

| 1996 corporation dissolved | Recipients of directed transfer | Schedule A |
|---|---|---|
| Central Vancouver Island | Alberni-Clayoquot; Cowichan Valley; Nanaimo; Powell River | §5 |
| Northern Interior | Stuart-Nechako; Fraser-Fort George; Peace River | §15 |
| Peace Liard | Fort Nelson-Liard; Peace River | §17 |
| South Okanagan Similkameen | Central Okanagan; Okanagan-Similkameen | §20 |
| Upper Island/Central Coast | Central Coast; Comox-Strathcona; North West; Mount Waddington | §22 |

The transfer **deadline** is 31 December; the order makes vesting depend on the actual transfer day. The dataset therefore records the deadline and leaves the actual closing day blank. It does not turn the dissolution day into proof of every transfer’s execution. Liquid-asset allocation and fixed-asset agreements are separately specified. [R4R-106]

Third, the order continues two corporations with smaller territory and partial transfers: **Cariboo-Coast becomes Cariboo-Chilcotin**, and **Coast Garibaldi becomes Sea to Sky**, both on **19 November 1998**. It also amends the membership or boundaries of North Okanagan/Columbia Shuswap, North West and West Kootenay-Boundary. **OIC 1430/1998** incorporates **Stuart-Nechako on 19 November 1998**; its first subsequent budget year is not its legal start. [R4R-106, §§2,6,13,14,23][R4R-103]

The source’s apparent internal cross-reference anomalies in §§2(a) and 6(a) are retained as printed, rather than silently rewritten. A reader needing exact parcels or fiscal allocations should use the source schedule. Polygon digitization and the actual executed allocation agreements are outside the recovered evidence.

## 4. Other continuations, splits and legal endings

### Three additional identities

| Corporation | Operative start | What the instrument does |
|---|---|---|
| Fort Nelson-Liard | **31 October 1987**, expressly retroactive from orders approved 19 November | Separately incorporates it while the older Peace River-Liard district continues as Peace River with reduced boundaries and specified debt allocation. [R4R-039][R4R-117] |
| Fraser Valley | **12 December 1995**, order approved 7 December | Dissolves Central Fraser Valley, Dewdney-Alouette and Fraser-Cheam at midnight at the end of 11 December and transfers their assets/rights/liabilities. [R4R-004] |
| Stuart-Nechako | **19 November 1998** | New letters patent, coordinated with the 1998 reorganization. [R4R-103] |

The 1970 order renaming the **municipal** Peace River Regional District to Peace River-Liard is not substituted for the hospital corporation’s missing first renaming order. The hospital-district name is certainly observed in the 1972 Fort Nelson transfer, and the 1987 instrument explicitly changes it back, but the first adoption day remains unresolved. [R4R-078][R4R-118][R4R-117]

### Greater Vancouver: several asset recipients, not one successor

**OIC 1601/1998**, approved 17 December, dissolves Greater Vancouver Regional Hospital District effective **1 January 1999**. The asset directions are specific:

| Recipient | Property / relationship | Conditions in the order |
|---|---|---|
| South Fraser Health Region | Surrey 15-acre parcel, Schedule A | Independent review within three years and possible return under the stated conditions. |
| Vancouver/Richmond Health Board | Tilbury Laundry and adjacent land, Schedule B | Defined property transfer. |
| Vancouver General Hospital | Parkade, Schedule C | Restrictions on health-program funding and Schedule D debt payments; non-compliance triggers transfer and vesting in government. |
| Province | Residual assets and liabilities, including leasehold interests | Residual statutory vesting. |

These are four recipient groups, not a general merger into one health authority. The conditions do not establish that a later reversion actually occurred. [R4R-162, Appendix §§1–6, Schedules A–D]

### Older restricted corporations sometimes survived for decades

The original orders now establish these later legal ends:
''')
rows=[]
for e in rhd['entities']:
    if e['cohort']!='original_1967_1968' or not e['legal_end'] or e['legal_end']<'2000':continue
    current=e['names'][-1]['name']
    rows.append([short(current)+' (original '+e['legal_start'][:4]+' corporation)',e['legal_end'],cite(e['end_source_ids'][0])])
parts.append(table(['Old corporation','Dissolved','Source'],rows))
parts.append('''
The Skeena-Queen Charlotte order separately transfers **$53,519.57 on 21 April 2021** to North West, before dissolution on **21 May**. Keeping those two events separate prevents a month-long error in the transfer chronology. The old East Kootenay corporation’s **2024** dissolution must not end the distinct 1996 corporation renamed Kootenay East. The latter’s letters patent are amended by the adjacent 2024 order. [R4R-032][R4R-034][R4R-035]

The original **1968 Cariboo corporation’s ultimate legal end remains untraced**. The register deliberately does not infer an end from the creation or later name changes of the distinct 1996 corporation.

## 5. Governance, freedom of information and treaty-government membership

### Regional hospital districts are not simply ministry branches

The current **Hospital District Act** separates board constitution (§8), staffing/accounts/audit arrangements (§17), capital bylaws (§32) and ministerial inspection/reporting powers (§45). The original letters patent and later membership amendments supply the historical versions for particular districts. A ministerial approval power, local representative board and capital-finance role can coexist. Each should be a typed relationship. The current Act is used as a dated checkpoint, not projected back unchanged to 1967. [R4R-001]

### FOIPPA coverage is partly class-based

**OIC 1356/1994 / B.C. Reg. 400/94** was approved **2 November 1994**, with the official statute tables recording commencement **3 November**. It brings the local-public-body machinery into force, including the educational-body, health-care-body and local-government-body definitions added by the 1993 amendment. The health-care definition expressly includes **regional hospital districts and their boards**. Absence from the individual names in Schedule 2 is therefore not proof that a district was outside FOIPPA. [R4R-071][R4R-072, §28(c)][R4R-080, printed 1009–1010]

**Regional health boards and community health councils enter the health-care-body definition on 13 July 1995**, under **SBC 1995 c.53, section 14**. The assent/commencement provisions and official 1995 table establish that exact date. Apply this class rule no earlier than both the statutory date and the particular body's own designation. It does not establish the coverage of the separately incorporated community health services societies. [R4H-015][R4H-018][R4R-081, printed 1165 and 1244]

The professional-governing-body **Schedule 3** begins **6 November 1995**, B.C. Reg. 451/95, under the newly recovered original **OIC 1321/1995**, approved 2 November. The 1995 table corroborates it. The **RS1996 FOIPPA Supplement**, section 1(h), by contrast, changes the Schedule 2 label **Medical Appeal Board** to **Hospital Appeal Board**. Its initially ordered 15 April date was corrected retrospectively to **21 April 1997**, as recorded in the official 1998 table. Neither April date is the regional-health-board/council class start or, by itself, the tribunal's creation date. [R4H-019][R4R-081][R4H-016][R4H-020][R4R-086]

These additions improve the previous body-by-body scrutiny crosswalk. They do not complete every entity’s first-coverage date, all later exclusions, every appeal route, or all Ombudsperson/Auditor General jurisdiction changes. A class rule needs an evidenced match to the body being displayed.

### First Nations participate as governments

**OIC 191/2012**, approved 29 March and expressly effective **1 April 2012**, changes Alberni-Clayoquot’s regional hospital district membership clause to include treaty lands of participating treaty First Nations. Its recitals identify **Huu-ay-aht First Nations and Ucluelet First Nation** joining the corresponding regional district from that date. This is a dated membership relation, not the creation of either Nation and not a ministry hierarchy. [R4R-167]

**OIC 811/2015, 17 December 2015**, adds a financial qualification: the specified borrowing repayments for decisions made before a Maa-nulth First Nation became a member must not be included in that Nation’s requisition. The membership and fiscal conditions belong on separate edges or event details. [R4R-009, added §12]

The **26 February 2024** Powell River-to-qathet letters-patent amendment also has Tla’amin membership provisions. This module uses the actual order for the name event; full treaty and membership histories remain in the broader G7 work. [R4R-064]

## 6. The exact 1988 franchise amendment is now identified

The **Election Amendment Act, 1987**, actually **SBC 1988 c.2**, received assent **11 March 1988**. Section 23 leaves commencement to regulation. **OIC 548/1988**, approved **25 March**, brings it into force; the official 1994 and 1995 statute tables specify **28 March 1988**, **B.C. Reg. 101/88**. That day replaces the former year-only placeholder in claim **R3G-F027**. [R4R-059][R4R-070][R4R-080, printed 979–981][R4R-081]

The relevant changes include an exception to the indictable-offence disqualification for a person released on probation or parole who is not in custody; removal of the twelve-month Canadian-residence phrase; permitting age qualification to be met on polling day; and protection of provincial residence for the specified Crown-service absences and accompanying family. These are the statutory conditions, not a blanket enfranchisement of all imprisoned people or removal of every BC residence requirement. [R4R-059, §§2–4]

The wider franchise chronology from the earlier package remains necessary. This closes the specific 1988 amending-instrument gap; it does not complete every colonial qualification interval or every litigation-related practical voting change.

## 7. The 1977 ministry-title proclamation: stronger corroboration, still a document gap

The previously recovered **OIC 3240/1977** authorizes the title-change proclamation. The 1994 official statute table now supplies corroboration: the 1977 c.75 amendments to Hospital Corporations Act §§2,5,10 and West Coast National Park Act §7 are recorded as proclaimed effective **21 October 1977**. [R4R-010][R4R-080, printed 1022/PDF90 and printed 1198/PDF266]

The **actual proclamation** and a direct Health-title entry have not been recovered here. The dates of those specific amendments should not be promoted into blanket proof for every provision of the titles Act. The decisive next document is the relevant Gazette proclamation or the 1979 statute table’s direct departmental entry. This is distinct from the **1946 Health and Welfare proclamation**, already recovered in the prior package.

## 8. What this means for the People of British Columbia at the centre

The examined repository already adds a `people-of-british-columbia` node and an `elects` edge to the Assembly. Its description uses a present-tense “every adult citizen” formulation. The remaining problem is the accuracy and meaning of the connections for each historical date, not the absence of a People node in this baseline. [Repository `src/government/snapshot.js`](https://github.com/ahzs645/PofBC/blob/0f1587c5e982135f155ba6660af5192509351511/src/government/snapshot.js)

The research supports these model changes:

1. **Keep the whole population and the eligible electorate distinct.** Use dated provincial qualifications on electoral edges, and separate qualifications for improvement-district elections. People who could not vote still belonged to the population served or governed.
2. **Represent each legal or administrative entity by its own identity and dated names.** A continuing rename is different from a newly incorporated same-named district; a program is different from its corporate operator.
3. **Type the relationship.** Ownership, board appointment, statute administration, funding, service delivery, financial reporting, audit jurisdiction, complaints, local membership and asset transfers answer different questions.
4. **Allow more than one route back to the public.** Electoral representation, ministerial responsibility and legislative scrutiny can be shown alongside audits, information rights, complaint mechanisms and courts, each with its actual scope. No ownership or funding edge should automatically imply an electoral-accountability path.
5. **Give ministers their office nodes and tenure intervals where the evidence supports them.** A statute assigned to a minister is a different fact from every activity of a corporation being directly commanded by a ministry.
6. **Display evidence dates honestly.** Keep made, effective, observed, deadline and actual-execution dates separate. Unknown dates remain unknown; a year, reporting period or season should not become 1 January.

These are recommendations for later implementation. The handback supplies the underlying events and relation evidence; it does not silently turn every finding into a live atlas edge.

## 9. What remains unresolved in this module

| Missing record or work | Why it still matters |
|---|---|
| Old 1968 Cariboo RHD’s ultimate ending instrument | Avoids assigning the 1996 successor-family dates to the old corporation. |
| First hospital-district adoption of the Peace River-Liard name | The municipal order alone cannot prove the hospital corporation’s rename. |
| Executed 1998 district asset-allocation agreements and closing dates | The omnibus order supplies recipients and deadlines, but not every actual transfer day. |
| Separately executed 1972 hospital-society conveyances and original society certificates | Certified resolutions and order recitals are preserved; they are not the same documents. |
| Remaining hospital improvement districts outside the recovered 25 | The 1969 schedule plus two later transfers is not a province-wide census of every Water Act hospital body. |
| Full boundary histories and parcel/polygon conversion | Metes-and-bounds text was read for identity/context, not converted to GIS. |
| Every historical board appointment and franchise amendment | Original rules and selected amendments do not constitute continuous all-year governance coverage. |
| Full statutory scrutiny and remedy history, body by body | Class commencement dates improve G2 but do not close the whole item. |
| The actual 1977 ministry-title proclamation | Compilation corroboration is retained with its exact scope. |

The separate health report retains the still-missing **43 council amalgamation execution days**, rural-board legal endings, society asset/conveyance records and the unproved PHSA legal-operator links. The hospital-district discoveries must not be used to fill those unrelated gaps by analogy.

## Evidence and review

`claims.json` contains the structured findings; `hospital_districts.json` and `hospital_improvement_districts.json` preserve identities and typed transfers; `conflicts.json` records original-versus-later-date disagreements. `hid-verification.json` supplies the independent scan checks and per-body governance locators. `check-rhd-1998.json` independently checks the high-impact 1998 orders and their transfer conditions.

The source catalogue includes screened candidates as well as accepted evidence. The evidence manifest states each record’s role; a downloaded or indexed PDF is not automatically a positive finding. Original downloads are hashed. Where a long statutory table is supplied as selected pages, the manifest supplies original and excerpt hashes and a page map. The original unmodified file remains separately retained.

''')
hs={s['id']:s for s in json.loads((B.parent/'health/sources.json').read_text())}
parts.append('## Root and cross-module source references\n\n'+'\n\n'.join(f'[{s}]: {v["url"]}' for s,v in sorted({**sources,**hs}.items())))
report='\n\n'.join(parts)+'\n'
report=re.sub(r'\[(R4[RHEB]-\d{3}), ([^\]]+)\]',r'[\1] (\2)',report)
(B/'report.md').write_text(report)
print('root report words',len((B/'report.md').read_text().split()))
