# Research guide: a time-aware atlas of B.C. government

**Snapshot: 25 September 2026.** This research supports an interface that answers four questions: what existed on a date, who held the relevant roles, how organizations and functions changed, and what visual identity is actually evidenced for the period. Recommendations below are design proposals; factual additions identify their sources.

## 1. Findings that can improve the data immediately

### Replace the Wikipedia-only Lieutenant Governors source

The Legislative Library publishes a sourced, 19-page list, updated January 2025, with commission dates, effective-appointment information, swearing-in dates and term ends. Wendy Cocchia is numbered 31 and is recorded as sworn in on 30 January 2025, after a commission dated 19 December 2024. Government House independently identifies her as the current incumbent. Reconcile the project’s reported total of 32: it could reflect a duplicate, an administrator, a colonial office or a different term-counting convention. Do not delete a record on the strength of the total alone. [S07, S08]

**Interface effect:** a person can be appointed or commissioned before assuming office. Keep these events separate. Display the source’s revision date rather than silently treating an old PDF as continuously updated.

### BC Parks needs more than one “founding date”

BC Parks records legislation establishing Strathcona Park on 1 March 1911. Its history separately identifies the 1957 Parks Branch within the Department of Recreation and Conservation, independent of the Forest Service. The first event concerns the parks system; the second concerns an administrative organization. [S10]

**Interface effect:** allow “Origins,” “Organization established,” “Operations began” and “Current name adopted” to be distinct fields/events. For 1920, show the evidenced parks function and its historical administrator—not an invented present-day BC Parks unit.

### BC Wildfire Service has an official 1912 origin claim

The official governance page explicitly traces the service’s formation to 1912. Its present-day about page describes six regional fire centres and links to their details. [S11, S12]

**Interface effect:** 1912 can be retained as an attributed lineage/origin event. It does not establish that the name “BC Wildfire Service,” its present organization chart or its modern patch existed in 1912. Historical organizational and identity episodes remain separate research tasks.

### WorkSafeBC is a strong pilot for identity plus administrative history

Its official chronology dates logo changes to 1968 and 1983, the change from Workmen’s to Workers’ Compensation Board to 1974, and adoption of the WorkSafeBC operating name to 2005. It explicitly says Workers’ Compensation Board remains the legal name. The same history gives historical CEO appointments: Ralph McGinn in 1998, David Anderson effective 15 December 2003, and Diana Miles effective 9 December 2014. [S13–S15]

**Interface effect:** one entity can have multiple legal-name, operating-name, logo and executive episodes that do not change simultaneously. These records can test the interface before a province-wide extraction. They do not yet fill the responsible-minister gap from 1917 to 1974.

### Treat the 2026 election as a sequence

Elections BC reports writ day on 22 September; nominations closing at 1 p.m. Pacific time on 3 October; advance voting 16–21 October; Final Voting Day 24 October; planned final count 6–10 November; and Return Day 18 November. It states that 93 MLAs will be elected. [S01]

**Interface effect:** keep election called, scheduled voting, preliminary results, final results, returned writs and subsequent government formation distinct. Do not populate future winners, equate election day with appointment of a premier, or make provisional seat totals look certified.

### FNHA requires a different relationship model

FNHA describes a First Nations governance structure involving the First Nations Health Council, First Nations Health Directors Association and Tripartite Committee, working with government partners rather than replacing the Ministry of Health or regional authorities. Its transfer chronology separates policy/planning and headquarters functions on 2 July 2013 from regionally delivered programs on 1 October 2013. [S31–S33]

**Interface effect:** health bodies can be visible together without being depicted as seven equivalent ministry subsidiaries. Use explicit partnership, governance and function-transfer relationships.

## 2. The highest-yield source collections

### Legislative Library: people and publication discovery

The official publications page links fact-checked lists of premiers, opposition leaders, Speakers, Lieutenant Governors, other presiding officers, Sergeants-at-Arms and women MLAs. It also links cabinet appointment/termination lists, historical Executive Council appointments with errata, and three electoral-history volumes covering 1871–1986, 1987–2001 and 2002–2013. Its government-publications portal and catalogue are important report-discovery routes. [S06, S09, S37]

These sources should be harvested by document family, preserving revision dates and errata. An electoral winner roster alone will not establish later party switches, resignations, deaths, vacancies or committee membership. No comprehensive ready-made deputy-minister list was verified; ask the Library about indexes and relevant official directories instead of presuming one exists.

### Elections BC: Legislature and geography

The results index supplies Statements of Votes and links to structured data, with Excel files for some earlier elections. The GIS page points to district boundaries, voting areas and conversion/assignment tables through the BC Data Catalogue. Current GIS coverage verified here includes resources for 2024 and 2020, not a complete historical map series. [S03–S05]

Election geography should carry a boundary-version identifier. A reused riding name is not proof of unchanged boundaries. Retain the electoral system and number of members returned as explicit fields. The historical overview records the first election across October–December 1871, and identifies 1903 as the first election with candidates running on party lines. [S02]

### Budget archive: historical scale and administrative structure

The official archive lists budgets back to 1995, ministry plans from 2002 and annual service-plan reports from 2001/02. Modern materials include Estimates, Supplements, ministry service plans and Crown agency plans. [S29, S30]

Use these to locate staffing/resource tables, organization sections, letters of accountability and responsibility lists. Extract the fiscal period, whether a value is budget or actual, the unit, and whether reporting scope has changed. Availability of a report does not prove that every desired field appears in it. Historical headcount, FTE, funded positions and seasonal workers must not be combined into one unlabeled series.

### BC Archives: pre-1905 sources and administrative change

The Guides, Indexes and Inventories page links the ministry history diagram, Sessional Papers index, city directories and other finding aids. The 119-page Sessional Papers index is particularly useful for identifying report titles and page references. Its introduction explains the wider colonial and provincial paper series, and warns that the session year can differ from the year of the report’s content. [S24–S26]

The Library also links Marjorie C. Holmes’s bibliography of government publications for 1871–1947, arranged by department. The PDF itself exceeded the browsing tool’s size limit in this pass; use the catalogue description as a discovery lead, not as if all pages had been inspected. [S06, S27]

The UBC digital-collection route exposed only an application shell here. No claim of verified downloadable coverage is made for it. [S36]

### BC Laws: dates and instruments

Orders in Council and the applicable historical legislation should be used to verify legal creation, appointments and responsibility transfers. Record the instrument number and the operative provision, distinguishing document, filing and effective dates. The search route was located, but the target historical instruments were not harvested. [S28]

## 3. How to approach the unattached periods

The BC Rail 1972–2003 and WCB 1917–1974 gaps remain unresolved. Treat them as records to investigate rather than blank spaces to fill by intuition.

Start with a dated annual report’s transmittal or governance statement. Identify whether it says a minister tables the report, is responsible under a statute, exercises a power of appointment, or actually controls administration. These are different relationships. Search the relevant instruments and adjacent reports around known changes. Retain an observation as an observation until continuous coverage is supported.

For BC Rail, distinguish the operating business, the legal company, property-holding entities and corridor ownership. The Province’s current BCRC page describes a continuing corridor/port-land role and infrastructure leased to CN. This is a reason to model the legal entities carefully, not evidence of who answered for them in earlier decades. [S23]

For pre-1905 bodies, search by historical report title and function as well as modern organization name. The departmental bibliography and Sessional Papers index offer a more targeted starting point than an unrestricted search for every current agency. [S25–S27]

An organization with unknown ministerial responsibility should still appear in a clearly labeled “Responsibility not yet established” lane. Lack of an edge is not evidence of independence, and lack of a founding date is not evidence that the body did not exist.

## 4. Priority logo acquisition

The five priority records are in `logo_acquisition.json`. BC Transit explicitly provides a corporate-logo request route at media@bctransit.com. ICBC has a newsroom and approved editorial image gallery; BCLC has a media centre and imagery terms; BC Ferries has an official media library and media@bcferries.com; WorkSafeBC supplies especially useful historical chronology. [S14–S22]

No downloadable vector master was verified in this pass. Do not substitute “official media page located” for “original SVG obtained.” Request the master file, permitted uses, required attribution, variant names and adoption/retirement evidence together.

For every acquired asset record: the organization and variant; original URL or supplied-file provenance; actual format and whether it contains raster images or text; first/last observed use; documented adoption/retirement if known; reconstruction status; font substitution; rights restrictions; and a reference application against which to compare it.

The provincial-symbol page provides a further warning: the 1960 flag adoption and 15 October 1987 arms grant are dates for symbols, not automatically dates for government identity programs. It also sets out restrictions and directs symbol-use inquiries to protocol@gov.bc.ca. [S34]

Keep a historically evidenced gallery separate from the arbitrary-name generator. A modern ministry style applied to a historical name should be labeled a generated interpretation, not an archival logo. Keep contemporary neutral fallback labels available where artwork, dates or permissions are unknown. Do not redistribute font files.

## 5. Interface structure recommended

Use one synchronized date context, a clear active scope and a persistent evidence drawer across several views:

**Government on a date:** separate constitutional/administrative lanes; expandable ministries and dated agency relationships; unknown-responsibility lane. Distinguish “observed on this date” from a fully established interval.

**Organization history:** legal entity and name episodes, function transfers, predecessor/successor relationships, people and logo evidence. A merger, renaming, split and transfer of one function should look different.

**Compare dates:** additions, closures, name changes, changed relationships, role-holder changes and comparable measures. Keep unchanged items visually stable instead of rearranging the entire graph.

**People and Legislature:** people linked to roles and service periods; Parliament and session selectors; ridings with boundary vintages; party elected under versus current caucus; vacancies and by-elections. Do not equate a person, an office and a ministry.

**Identity gallery:** organization/era/asset-status filters; original application beside reconstruction; date confidence and rights status visible; generator outputs clearly distinguished from actual marks.

**Sources and coverage:** claim-level evidence, original-versus-reviewed text, conflicting claims and missingness by category. This extends the project’s existing Map/Records/Review-decisions approach instead of hiding its audit work.

Provide a keyboard-accessible searchable table alternative to the graph, persistent links encoding the selected date and entity, readable mobile detail panels and reduced-motion transitions. These are proposed acceptance requirements, not tested features of the existing interface.

## 6. Build/research order

First establish the data distinctions: legal entity versus name, relationship types, source observations versus intervals, date precision, and original versus reconstructed identity. Reconcile the LG count and map the supplied event seeds. Prepare—but do not invent results for—the election update.

In parallel, request the five corporate logo families. Then do focused historical passes on high-use sub-agencies and the longest unattached periods. Next add MLAs and districts, followed by committee history, deputy ministers and fiscal measures. Keep universities, school boards, TransLink, post-government successors and municipalities as explicit optional scope layers rather than silently treating them all as Crown subsidiaries.

The strongest result is not the densest organization chart. It is a chart where every name, edge, date and image has a clear meaning and an inspectable source.

## Suggested archive/artwork inquiry

Subject: Historical B.C. government identity and organizational records — research inquiry

Hello,

I am based in Prince George and am researching an interactive historical atlas of British Columbia’s government organizations and visual identities. I am looking for [specific organization/manual/report title and date range].

Could you advise whether you hold original artwork or identity guidelines, dated adoption or replacement instructions, and records identifying the organization’s responsible minister or parent department during this period? Catalogue identifiers, archival series/file references and relevant report pages would also be very helpful.

Where available, I would appreciate digital scans or original vector artwork, along with any reproduction conditions, attribution requirements and information about fees. The project needs to distinguish authentic historical material from newly generated reconstructions, so first-use evidence and version dates are particularly valuable.

Thank you for your guidance.

[Name]

## Sources

The numbered source records, exact URLs, review statuses, locators and limitations are in `sources.json` and the Source register in `index.html`. References such as [S10] in this guide point to those records. This guide is not a claim that all linked documents, institution histories or current office-holders were audited exhaustively.
