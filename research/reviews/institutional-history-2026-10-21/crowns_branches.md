# Crown corporations and non-health institutional histories: research for PofBC

Research date: 20–21 October 2026 (20 October in Vancouver; 21 October UTC). Repository inspected read-only at commit `112b352ebbd032c28e35b12036d5199ec97584e2` in `pofbc-review`. Source identifiers below resolve in `crowns_branches_sources.json`. Dates on annual reports denote the reporting period, not necessarily the date that an organizational change happened. No repository changes were made.

## 1. Principal finding

PofBC already has substantial Crown and ministry history. The strongest extension is to make different institutional relationships explicit, extend selected branches with earlier evidence, and reconcile the current-body inventory against several official universes. It would be inaccurate to describe the ministry history diagram, BC Hydro's two principal predecessors, or the Urban Transit Authority/Metro Transit Operating Company as newly discovered missing history: those are already represented.

The current file contains 29 entries classified as Crown corporations. These match the 2026 Budget service-plan directory's 30 entries after excluding the Liquor Distribution Branch, which the repository correctly describes as a government branch. However, the service-plan directory is not the complete universe of provincial public bodies. There is a separate list of 20 service-plan-exempt entries, a much larger Public Accounts reporting entity, and statutory bodies with their own governance arrangements. [CB-004](https://www.bcbudget.gov.bc.ca/2026/crownserviceplans/), [CB-005](https://www.bcbudget.gov.bc.ca/2026/crown_exempt/), [CB-007](https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/financial-statements)

Particularly actionable gaps are:

- **BCTFA ownership:** B.C. Transportation Financing Authority owns B.C. Railway Company and Transportation Investment Corporation. These are corporate ownership relationships, separate from each organization's responsible minister. Both dates are explicit in 2025/26 audited statements: 1 April 2010 and 1 April 2018 respectively. These entities already continue into the current map through historical data; the missing ownership and current accountability edges are the problem. [CB-008](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/bc-transportation-financing-authority-fs-2025-26.pdf), [CB-009](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/bc-railway-company-fs-2025-26.pdf)
- **Post-2003 ferries:** The historical ferry corporation points to `bc-ferry-services-inc`, but that successor node is absent. The modern B.C. Ferry Authority created in 2003 is also absent and must not be conflated with the identically named Crown operator of 1964–1977. [CB-010](https://www.bcferries.com/our-company/leadership)
- **Homeowner Protection Office:** The former body is missing although BC Housing's licensing/consumer-protection division is represented. Its 2010 functions split between BC Housing and Finance; representing this as one simple rename would lose the history. [CB-014](https://archive.news.gov.bc.ca/releases/news_releases_2009-2013/2010hsd0024-000212.htm), [CB-015](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/98031_pit)
- **Lower-level branches:** Sheriff Service, Conservation Officer Service, BC Parks, Wildfire Service, and Surveyor General histories offer well-supported examples of consolidation, renaming, parent changes, and function splits far earlier than the present branch records. [CB-023](https://ltsa.ca/professionals/surveyor-general/history-of-the-surveyor-general/), [CB-024](https://bcparks.ca/about/our-mission-responsibilities/history/), [CB-025](https://news.gov.bc.ca/files/COS_110Anniversary_booklet.pdf), [CB-026](https://news.gov.bc.ca/releases/2024AG0027-000679), [CB-027](https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/wildfire-status/governance/bcws_strategic_plan_2012_17.pdf), [CB-028](https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/emergency-preparedness-response-recovery/provincial-emergency-planning/bc-provincial-coord-plan-for-wuifire_revised_july_2016.pdf)
- **Pension and investment entities:** BCI and B.C. Pension Corporation already continue through historical records with no end date. Current legislation can strengthen their distinctive ownership, client and board relationships. The repository's `current:false` flag means that a record is not duplicated in `CURRENT_BODIES`, not that the organization is inactive. [CB-020](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/99044_01)

## 2. What a Crown corporation is in this map

The Province's taxonomy distinguishes commercial Crown corporations, service-delivery Crown corporations, health and education bodies, advisory boards, and tribunals. Separate incorporation, legal Crown-agency status, funding, accountability, and accounting classification are different questions. A node should not inherit a single generic category merely because its report appears in a Crown service-plan directory. [CB-001](https://www2.gov.bc.ca/gov/content/governments/services-for-government/public-sector-management/public-sector-organizations)

Recommended entity fields, as a design inference from the evidence:

| Question | Suggested representation | Example |
|---|---|---|
| What is the legal person? | `legal_form`, enabling statute, incorporation/continuation events | BCTFA is a separate corporation; LDB is a branch |
| Is it a Crown agent? | Dated statutory assertion with exceptions | LTSA generally is not; BCI and Pension Corporation are |
| Who owns voting shares? | `owned_by` with voting/nonvoting rights | Modern Ferry Authority owns BC Ferries' sole voting share |
| Who is politically accountable? | `minister_responsible_for`, with dates | Current responsible ministry, separately from owner |
| Who appoints whom? | `appoints_to`, director role and appointing authority | Pension-plan boards appoint directors of BCI/Pension Corporation |
| Who runs daily operations? | Board/CEO employment and delegation relationships | Ministerial responsibility does not mean daily management |
| How is it financed/accounted for? | Annual accounting classification and funding links | BCRC is self-supported; TI Corp taxpayer-supported |
| Who provides a service or regulates it? | `serves`, `contracts_with`, `regulated_by` | Ferries' service contract differs from ferry regulation |
| What happened historically? | Typed event and affected function | Transfer of operations can leave the original legal person alive |

Official governance guidance describes the Legislature as representing the public interest and authorizing legislation and public funds; Cabinet sets policy and mandates; the responsible minister is the principal governmental link; the board oversees performance and the CEO manages daily operations. This supports a meaningful path from people through representative institutions to public bodies, while separately showing service relationships back to residents. It does not support an ownership arrow from a ministry to every public body. [CB-002](https://www2.gov.bc.ca/gov/content/governments/services-for-government/public-sector-management/pso-government/public-sector-management-roles-responsibilities)

The Province's 2014 accountability announcement explicitly discusses government acting for citizens as shareholder and explicitly excludes TransLink from the provincial Crown category. It is helpful context, but each organization's contemporary statute and audited notes should prevail when implementing exact edges. [CB-041](https://news.gov.bc.ca/releases/2014PREM0055-000805)

## 3. A reproducible inventory beyond the 29 current Crowns

Use three complementary starting lists, each preserving its own scope and reference date:

1. **2026 Crown Agency Service Plans:** the usual service-plan cohort, already substantially covered. [CB-004](https://www.bcbudget.gov.bc.ca/2026/crownserviceplans/)
2. **2026 service-plan exemptions:** additional bodies omitted from that cohort. An entry proves inclusion on the published exemption list, not necessarily current activity, an identical legal status, or unbroken existence under its name. [CB-005](https://www.bcbudget.gov.bc.ca/2026/crown_exempt/)
3. **Public Accounts 2025/26 financial-statement index:** audited reporting entity and its accounting classifications, extending into education, health, employers' associations, and other bodies. The live page is for the year ended 31 March 2026, although search snippets sometimes still describe 2025. [CB-006](https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts), [CB-007](https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/financial-statements)

The financial-statement index lists six self-supported organizations on the modified-equity basis: BC Hydro, LDB, BCLC, BCRC, Columbia Power, and ICBC. This is an accounting list, and its inclusion of LDB is a useful demonstration that it is not identical to a list of legally incorporated Crowns. The index separately groups taxpayer-supported government organizations. [CB-007](https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/financial-statements)

### All 20 names in the 2026 exemption list

Names reproduce the official list as lookup keys. Repository comparison is a triage result from ID/name inspection, not a completed legal-status audit. [CB-005](https://www.bcbudget.gov.bc.ca/2026/crown_exempt/)

| Official-list entry | Repository observation / next work |
|---|---|
| 552513 British Columbia Ltd. | No corresponding entity located; establish legal purpose, ownership, and activity |
| BC Transportation Financing Authority | Continuing historical record exists; add dated subsidiary ownership edges |
| BCIF Management Ltd. | No corresponding entity located; trace investment-fund relationship |
| BC PNP Fast Track Fund Ltd. | No corresponding entity located; distinguish fund manager, fund and program |
| British Columbia Enterprise Corporation | Historical record says operations ceased 1989; current list creates a reconciliation task |
| British Columbia Public School Employers' Association | No corresponding entity located; employer governance distinct from school districts |
| British Columbia Railway Company and its subsidiaries | Continuing company and BCR Properties subsidiary exist; add current ownership/accountability edges |
| British Columbia Trade and Invest Ltd. | No corresponding entity located; examine historical corporate shell and successor operations |
| Canadian Blood Services | No corresponding entity located; joint provincial/territorial governance requires different edges |
| Community Social Services Employers' Association of British Columbia | No corresponding entity located; association and bargaining role |
| Creston Valley Wildlife Management Authority | No corresponding entity located; reconcile authority/trust names against audited reports |
| Crown Corporations Employers Association | No corresponding entity located; not the central Crown Agencies Secretariat |
| Health Employers Association of British Columbia | No corresponding entity located; employer association is distinct from a health authority |
| Leading Edge Endowment Fund | No corresponding entity located; check legal vehicle, distributions, and current activity |
| Nechako-Kitamaat Development Fund Society | No corresponding entity located; society and regional funding mandate |
| Organized Crime Agency of British Columbia | No corresponding entity located; identify relationship to CFSEU-BC and participating police forces |
| Provincial Rental Housing Corporation | No corresponding entity located; BC Housing administration and property ownership are different edges |
| Rapid Transit Project 2000 Ltd. | No corresponding entity located; date project/company operations, residual assets and corporate status separately |
| Real Estate Foundation of British Columbia | No corresponding entity located; statutory foundation and governance |
| The Post-Secondary Employers' Association | No corresponding entity located; distinguish from ministry, individual colleges, and bargaining councils |

This is a useful controlled queue, not a recommendation to add 20 unqualified active Crown nodes. The British Columbia Enterprise Corporation example is especially instructive: the repository records cessation of operations on 30 September 1989, the 2026 exemption directory still names it, and its enabling Act was repealed effective 13 March 2023. These can refer to different legal/operational events or source lag. Establish dissolution/continuation from the repealing Act, corporate registry evidence or audited statements before changing the node's lifespan. [CB-018](https://www.bclaws.gov.bc.ca/civix/document/id/consol44/consol44/96035_pit)

## 4. High-value Crown and affiliated-body histories

### 4.1 Transportation ownership: BCTFA, BC Rail and TI Corp

BCTFA's 2025/26 audited Note 1 supplies unusually direct evidence: established in 1993 under the **Build BC Act**, with the **Transportation Act** replacing that legislative basis on 31 December 2004. The repository's description currently attributes its 1993 founding to the Transportation Act and should be corrected. The same note dates BCRC becoming a wholly owned subsidiary to 1 April 2010 and TI Corp to 1 April 2018. These form nested current relationships rather than three unrelated organizations reporting to a ministry. [CB-008](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/bc-transportation-financing-authority-fs-2025-26.pdf)

BCRC's own 2025/26 Note 1 confirms that it remains a Crown corporation, owned through BCTFA, holding railway/port assets including the corridor used by CN; Note 3 identifies BCR Properties Ltd. as its subsidiary. The 2004 transfer of freight operations therefore must not be rendered as BCRC's dissolution or total succession by CN. [CB-009](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/bc-railway-company-fs-2025-26.pdf)

The existing private PGE 1912 / public takeover 1918 / BCRC 1972 / BC Rail operations 1984 history is mostly present. The 2003 service plan and a 2001 Environmental Appeal Board decision offer primary documentary cross-checks. Do not overwrite 1 April 1972 in the repository with the decision's 30 March 1972 reference without checking whether those refer to enactment and effective dates. [CB-034](https://www.bcbudget.gov.bc.ca/2003/sp/crowncorps/bcrail.pdf), [CB-035](https://www.bceab.ca/app/uploads/sites/717/2020/04/2000was018b.pdf)

### 4.2 Ferries after the Crown-corporation era

BC Ferries' governance page explains the 2003 structure: BC Ferry Services Inc. is an independent regulated company; the modern B.C. Ferry Authority is a corporation without shares holding the company's voting share; the Province holds nonvoting preferred shares; service obligations are contractual; the Commissioner is a separate regulator. [CB-010](https://www.bcferries.com/our-company/leadership)

Add the missing modern company and authority with distinct IDs from the 1964–1977 authority. Connect the already-present Ferry Commission by regulation, the Province by the service contract and preferred-share interest, and the modern Authority by voting ownership and board appointments. Preserve the 2003 Crown-to-company transition as a dated legal-status change. A generic `under Ministry of Transportation` path would hide precisely what the user wants to understand.

### 4.3 BC Hydro and transit: preserve partial-function transfers

BC Hydro's official history confirms BC Electric Railway origins in 1897, the Power Commission in 1945, and their 1962 combination. These principal predecessors are already in PofBC. The better extension is the business/function trail: electric supply and public transit followed different paths later. Distinguish the 1961 acquisition from the 1962 corporate combination, and keep enactment dates separate from effective dates. [CB-011](https://www.bchydro.com/toolbar/about/who_we_are/history.html), [CB-033](https://www.bchydro.com/news/press_centre/news_releases/2012/affordable_hydro_power.html)

BC Transit's official history traces 1890 Victoria electric transit, BC Electric, BC Hydro, the Urban Transit Authority in 1979, the 1982 BC Transit name, and Metro Vancouver's 1999 transfer to TransLink. The repository already includes UTA and Metro Transit Operating Company. Its current file's 1998 establishment value conflicts with the historical record's 1982, but the history layer apparently supplies the effective displayed value; normalize source data without claiming the lineage was wholly absent. [CB-012](https://www.bctransit.com/about/history/)

### 4.4 BC Housing, PRHC, and the Homeowner Protection Office

BC Housing's organization page distinguishes the Housing Management Commission, established in 1967, from Provincial Rental Housing Corporation, created in 1961 and administered by BC Housing. Add the PRHC legal person and an `administered_by` relationship; this evidence does not alone establish BC Housing as its shareholder. [CB-013](https://www.bchousing.org/about/our-organization)

The 3 March 2010 official bulletin specifies a split effective 1 April: residential-builder/envelope-renovator licensing, owner-builder authorization, research and education moved to BC Housing; Reconstruction Program administration moved to Finance. The Homeowner Protection Act's change history confirms repeal of the former Part 2 governing the office on that effective date. [CB-014](https://archive.news.gov.bc.ca/releases/news_releases_2009-2013/2010hsd0024-000212.htm), [CB-015](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/98031_pit)

A former HPO node plus two scoped `function_transferred_to` edges would connect the existing licensing division to its predecessor and avoid turning the entire predecessor into a department of BC Housing. The 2009/10 HPO accounts and 2012 BC Housing service plan are retained as further legal/operational corroboration leads; the audited PDF fetch was intermittent. [CB-016](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2009-10/sup-e/homeowner-protection-office-fs-2009-10.pdf), [CB-017](https://www.bcbudget.gov.bc.ca/2012/sp/pdf/agency/bchm.pdf)

### 4.5 BCI and Pension Corporation: public ownership is not ownership of client assets

The current Public Sector Pension Plans Act establishes both corporations as government agents and assigns each one's single share to Finance on behalf of government. Their boards have pension-plan representation, and their functions are different: pension administration versus funds management. Section 18.1 continues investment portfolios and transfers their holding from Finance/the chief investment officer into BCI on 1 January 2000. This adds an operational transfer to the existing 1999 incorporation date. [CB-020](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/99044_01)

For the visualization, distinguish the corporation's owner from the beneficiaries and pension funds whose assets it manages. Do not imply that government owns all pension assets just because it owns the investment-management corporation. Plan/client relationships, trustee appointments, and public accountability should coexist as separately labeled paths.

### 4.6 Other taxonomy/date checks

| Body | What is already present / what to improve | Evidence |
|---|---|---|
| LDB | Correctly a government branch. Historical 1921 Liquor Control Board and 1973 branch succession exist; verify the 1973 split and later administrative name using statutes/records. 1921 first-store operation is distinct from branch identity. | CB-036, CB-037 |
| ICBC | 1973 incorporation is already present. Separate its legal creation from insurance-service commencement rather than replacing one with the other. | CB-038 |
| BCLC | Repository dates legal establishment to 25 October 1984; public corporate accounts often start the operational story in 1985. Reconcile the milestones; do not automatically overwrite 1984. Western Canada Lottery Foundation functions are a targeted next archival query. | CB-039 |
| WorkSafeBC | WCB/Workers' Compensation Board histories already exist and continue. Keep legal name, public brand, statutory independence and financing separate; the official origin history reaches 1917. | CB-040 |
| LTSA | A publicly accountable statutory corporation with specific statutory exceptions to government-agent status; not automatically another conventional Crown. | CB-021, CB-022 |
| Royal BC Museum | Repo dates institutional origin to 1886 while its current kind is Crown. Legal-status history should not make that classification retroactive to every earlier year. Confirm the later Crown conversion with its statute before implementation. | Repository observation; targeted research lead |
| Columbia Basin Trust / Columbia Power / other existing Crowns | Both are already current bodies. Their different purpose, statutory authority, subsidiaries and asset/joint-venture relationships merit targeted audited-note work; do not infer that the shared Columbia name means common identity. | CB-004, CB-007; further body-specific work needed |

## 5. Five strong non-health branch expansions

### Conservation Officer Service

The official 1905–2015 anniversary booklet separates four milestones that should not collapse into one `established` date: a first provincial Game and Forest Warden in 1905; game wardens renamed conservation officers in 1961; a distinct ministry branch in 1980; legislative establishment in 2002. It also documents Environmental Enforcement Units in 1989. The existing modern sub-agency record currently has a 2015 budget sighting, no establishment date and no parent chronology. Earlier Game Conservation Board/Commissioner/Commission records already exist elsewhere in the data and can be connected after verifying the exact function transfers. [CB-025](https://news.gov.bc.ca/files/COS_110Anniversary_booklet.pdf)

### Sheriff Service

The Province's 2024 fiftieth-anniversary bulletin explicitly says nine county sheriff offices were amalgamated in 1974, while the first sheriff appointment occurred in 1857. The existing `sub-bc-sheriff-services` record has no establishment date or historical relationships. This is a particularly clear non-health example of regional bodies becoming a provincewide service. Add the 1974 event now with an aggregate predecessor group; enumerate the nine county offices only after locating the contemporary order or annual report. [CB-026](https://news.gov.bc.ca/releases/2024AG0027-000679)

### Parks

BC Parks' official history records Strathcona Park's creation in 1911, fragmented early administration, increasing Forest Service responsibility, and the independent Parks Branch in the Department of Recreation and Conservation in 1957. The Park Act followed in 1965. The first park's date must not become the modern branch's legal creation date. This fills history before the repository's earliest observed 2015 budget entry, while preserving historical parent and function changes. [CB-024](https://bcparks.ca/about/our-mission-responsibilities/history/)

### Wildfire

The Wildfire Management Branch 2012–2017 strategic plan traces wildfire protection to the Forest Service in 1912 and locates the contemporary branch in the Integrated Resource Operations Division of FLNRO, created in 2011. A 2016 provincial wildfire coordination plan's revision table records replacement of the term Wildfire Management Branch with BC Wildfire Service on 6 June 2015. That is a document-revision date, not sufficient proof of the precise legal or administrative renaming date. Add the older branch and the observed transition, leaving the exact effective-date claim explicitly unresolved. [CB-027](https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/wildfire-status/governance/bcws_strategic_plan_2012_17.pdf), [CB-028](https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/emergency-preparedness-response-recovery/provincial-emergency-planning/bc-provincial-coord-plan-for-wuifire_revised_july_2016.pdf)

### Surveyor General and land records

LTSA's official office history supplies a long sequence: 1851 company surveyor; 1858 colonial office; separation from Chief Commissioner in 1873; survey-function split in 1976; changing branch configurations in 1979, 1981 and 1985; a 2005 transfer to LTSA; and policy/operations separation in 2019. This is unusually strong material for demonstrating that an office, its host branch and its functions are not interchangeable entities. The early colonial chronology should preserve Vancouver Island/mainland distinctions. [CB-023](https://ltsa.ca/professionals/surveyor-general/history-of-the-surveyor-general/)

The Land Title and Survey Authority Act defines LTSA as a nonprofit corporation without share capital and generally not a government agent, except for executing Crown grants or express written agreements. Its position beside the Province, its regulated functions and its agreement with government should therefore be visible without forcing it into a ministry-subdivision hierarchy. [CB-021](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/00_04066_01), [CB-022](https://ltsa.ca/about-ltsa/governance/)

### Additional lead: emergency-management continuity

The Emergency and Disaster Management Act's transitional section 177 continues the prior Provincial Emergency Program director as the provincial administrator. That provides a legal continuity edge between statutory roles across the replacement legislation. It should be paired with the older program's actual organizational records before drawing a complete PEP → EMBC → EMCR chain; a ministry creation date is not the program's origin. [CB-029](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/23037)

## 6. How to extend this systematically

The BC Archives ministry-history diagram is already ingested in PofBC. Its distinction between whole-body continuation and transfer of some functions is a valuable model, but calling the diagram itself a new discovery would misdescribe the repository. [CB-030](https://bcarchives.ca/wp-content/uploads/sites/2/2026/01/BC-Government-Ministry-History-Diagram.pdf)

For each branch or Crown, use the following evidence ladder:

1. Enabling/repealing legislation and commencement orders for legal existence and exact effective dates.
2. Audited financial statements' first notes for legal nature, ownership, subsidiaries, mandate and operations transferred.
3. Contemporary annual reports/service plans before and after the change for staff, assets, functions and organization charts.
4. BC Archives authority records and operational records classification schedules for administrative history, earlier names, and records provenance.
5. Official organizational histories for older chronology and leads back to primary documents.
6. Contemporary official announcements to distinguish proposed, announced and implemented changes.

Public Accounts archive, ministry transition binders, and ORCS schedules are reusable source collections. Each can expand the existing six-checkpoint budget sightings with organizational evidence. Neither a budget presentation under a ministry nor an archival records-transfer date by itself proves a legal parent relationship or a founding date. [CB-031](https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/archive), [CB-032](https://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/open-government/open-information/government-information-regularly-released/corporate-and-ministry-transition-binders), [CB-042](https://www2.gov.bc.ca/gov/content/data/information-management/information-schedules/orcs/records-schedules)

For every historical event retain `announced_on`, `enacted_on`, `effective_on`, `first_observed_on`, date precision, source locator, and whether the event changed a legal person, a name, an operational function, a territorial responsibility, or a public brand. These are design recommendations derived from the examples, not claims that all such dates are currently known.

## 7. Confidence and limits

The sources support immediate documentation of BCTFA's ownership chain, the modern ferries gap, HPO's split, and the five branch histories above. The inventory expansion is confidently sourced at the directory level; many of the 20 exempt entries still require an individual legal-status review. Cessation of operations, disappearance from a directory, and dissolution are not equivalent.

The current publication snapshot is stronger than a 2025-only review: the live Public Accounts index and two transportation audited statements concern the year ended March 2026, and the pension statute was current to 13 October 2026. Ministerial assignments can still change after a report's period; a current ministry roster should be dated and checked against the government's most recent responsibility orders before it becomes a permanent edge.

This research does not claim complete coverage of all subsidiaries, project companies, employer associations, tribunals, school districts, health providers, or colonial boards. It identifies the official enumerating sources and separates already-held history, supported additions, data reconciliation, and further leads so the next ingestion pass can be audited.
