# PofBC research queue — complete archive review

**Reviewed: 2026-09-30. Input: pofbc-research-queue.zip.**

## Verdict

The archive is internally consistent as a work queue, but it is not a completed historical research database or a self-sufficient, verified merge package. Its central distinction between a founding date and a first sighting is useful. Several instructions nevertheless permit unsupported historical inferences, while the export removes enough inherited provenance that those inferences are difficult to catch.

All 26 files and all 238 records were included in the archive/field/assignment audit, and every one of the 23 batch packets was checked. This is not a claim that all 238 complete histories were independently researched. The external research pass consists of six selected Finance checkpoint scopes (72 body-year checks) and targeted checks of identity, placement and independence. Nothing was merged into the repository or deployed.

## 1. Scope and results

| Measure | Result |
|---|---:|
| Files in the original archive | 26 |
| Batches | 23 |
| Body records / distinct current parents | 238 / 37 |
| P1 / P2 / P3 | 180 / 19 / 39 |
| Review status: not researched / partial / reconciliation | 197 / 39 / 2 |
| Selected establishment dates | 39 |
| First-observed values | 10 (8 without establishment) |
| Records with historical name rows / parent rows | 14 / 11 |
| Event rows / records containing events | 175 / 53 |
| Event rows retaining source and locator in this export | 0 |
| Records with no official_url field | 57 |
| Selected Finance checkpoint checks / positive observations | 72 / 30 |
| Finance bodies with proposed positive evidence | 10 of 12 |

These are descriptive coverage counts, not a quality score. A missing official_url is not proof that a body has no official page; a missing held parent history is not proof that its current parent is wrong. A scalar established value does not establish whether its supporting source was ever adequately reviewed. The complete calculations and file hashes are in `audit/queue-audit.json`; per-record flags are in `audit/record-review.json`.

### Structural checks that passed

Every JSON skeleton parses. Every batch number, record ID, name, kind and current-parent field matches the machine-readable queue. Narrative IDs and skeleton IDs have the same order as batch metadata. The batches partition all 238 records exactly once. INDEX row totals and P1/P2/P3 counts agree with the underlying records. These are archive checks, not production merge or timeline tests.

### Important limits

The research files referenced outside queue/ are not included. No upstream commit is recorded. Source documents were opened with the web tool; external PDFs and web pages are not archived in this package. Selected PDF pages were visually checked, but the Finance pass did not read every page of every government Estimates volume. Public-source access and renderer execution are different tests.

## 2. What the queue gets right

The guide explicitly separates first sighting, creation and historical names/parents. It asks for primary sources, page locators, source precision and preservation of disagreements. It warns that a function is not necessarily an organization, that funding and appointments do not establish parentage, and that a record can remain incomplete. The batches provide stable IDs and usable handback skeletons. Those are sound foundations; the proposed changes tighten the points where the operational instructions contradict those principles.

## 3. Findings, evidence and repairs

### F01 — A negative search can incorrectly become a birth boundary (critical)

**Location:** `README.md: Track A, lines 71–72 and 91–92`. **Basis:** archive_instructions.

The guide suggests that repeated non-listings locate a likely start and tells researchers to stop at the first non-listing. Estimates can omit, aggregate, rename or relocate a unit.

**Repair:** Record the actual searched scope, terminology and outcome; continue relevant checkpoints and alternate ministries. Never derive a founding/end date from a negative search.

### F02 — Current ministry lineages are unreliable historical search boundaries (critical)

**Location:** `sub-agencies.json: parent_likely_by_year; README §3C`. **Basis:** ENV-2010; CAWS-2002.

The Climate Action Secretariat’s suggested 2010 ministry disagrees with the 2010 Environment vote. The Fire Commissioner is named under CAWS in 2002.

**Repair:** Retain leads as explicitly unverified. Store the document’s exact ministry label and observation date; search across contemporary rosters.

### F03 — Discovery leads mix abolition, continuation and a still-operating service (critical)

**Location:** `README.md: Track D, lines 129–142`. **Basis:** STBC-ACT; STBC-AR-2023; BCAS-CURRENT.

Industry Training Appeal Board is legally continued under a new name; BC Ambulance Service’s current page describes it operating under BCEHS. These are unsafe gone-body examples, not proven errors in an unseen gone database.

**Repair:** Require explicit cessation evidence. A rename normally stays one identity; a different successor is linked separately; a surviving nested service is not gone.

### F04 — The export loses provenance for inherited claims (high)

**Location:** `sub-agencies.json: items[].held`. **Basis:** archive_data.

All 175 event rows contain only date/type/title; none include source or locator. Selected start dates and sightings are also flattened scalars.

**Repair:** Export full dated claims, claim IDs, locators, precision, alternative claims and editorial decisions, or include the exact upstream research files at a pinned revision.

### F05 — Dated does not mean the start has been reviewed (high)

**Location:** `sub-agencies.json: priority/tracks/review_status`. **Basis:** archive_data.

Six C-only records still say not_researched; two C-only records explicitly require reconciliation. Date presence determines routing more strongly than evidence maturity.

**Repair:** Track research completeness and reconciliation independently of timeline priority. Existing date claims must remain reviewable.

### F06 — Retrospective testimony is being confused with contemporary observation (high)

**Location:** `README.md: Track A; selected held names/first_observed rows`. **Basis:** archive_data.

A later history statement can support existed-by testimony but is not necessarily a founding statement or a contemporaneous sighting. Several held observations originate in later annual reports/about pages.

**Repair:** Store claim effective date, source publication/observation date, date precision and testimony type separately. Do not turn all “since” statements into establishment claims.

### F07 — First-sighting work is not yet connected to timeline behaviour (high)

**Location:** `README.md: lines 331–334`. **Basis:** archive_instructions.

The guide explicitly says the diagram does not use first_observed to draw historical bodies. Collecting data alone will not resolve disappearance.

**Repair:** Implement and test an evidence-aware resolver with historical names and parents, unknown-start labels and non-continuity safeguards. Do not claim the renderer is fixed by this packet.

### F08 — Budget placement is not a universal organizational-parent relation (high)

**Location:** `README.md: rules and parents field`. **Basis:** FIN-2025; FERRY-CURRENT.

Only part_of/subsidiary_of are offered, while the queue contains independent bodies, programmes, accounts, facilities and projects. Budget chapters also group functions for appropriation purposes.

**Repair:** Preserve budget placement as its own fact. Expand typed relationships only with schema/runtime support and appropriate evidence, rather than forcing a misleading parent.

### F09 — The handoff is not reproducible against an identified code revision (high)

**Location:** `README.md: maintenance commands; source dependencies`. **Basis:** REPO-PACKAGE.

The archive lacks the build/merge code and several linked research files. The public main package inspected has differently named scripts and no research:merge or build:government alias.

**Repair:** Pin the upstream commit and include the complete dependency set, schemas, generator and tests. Do not run unsupported merge commands against an unidentified checkout.

### F10 — The batch handback instruction contradicts its own skeleton (medium)

**Location:** `All 23 batch Markdown files, handback paragraph`. **Basis:** archive_instructions.

Every batch says one JSON object per body, but its skeleton and README specify one object per batch containing records.

**Repair:** Correct the generated boilerplate and its generator. The included documentation patch fixes the exported copies only.

### F11 — Succession does not establish an exclusive end date (high)

**Location:** `README.md: ended field`. **Basis:** archive_instructions.

The parenthetical describes the end as the day the successor began. Distinct bodies can overlap; transferred functions do not by themselves prove closure.

**Repair:** Require independent cessation evidence and an explicit interval convention. Keep cessation, transfer and successor commencement as separate claims.

### F12 — A 2026-survivor queue is not a historical government census (high)

**Location:** `README.md: current-source collection and Track D`. **Basis:** archive_scope.

The 238-item inventory starts with present-day bodies. It cannot discover every abolished, absorbed or otherwise absent historical unit by following survivors backward.

**Repair:** Add period-specific roster extraction, then resolve entities and relations. Keep discovered candidates separate until identity and evidence checks pass.

### F13 — Some selected events exceed the certainty of their descriptions (high)

**Location:** `Held histories: Timber Sales, Wildfire, Corrections, CRT, Parks`. **Basis:** archive_data.

The snapshot contains bounded name changes, competing date descriptions, function origins and repeated milestones. Source-free flattening makes automatic selection unsafe.

**Repair:** Restore claim provenance; use bounded temporal claims and milestone types; do not assign an exact day to an observation interval or erase disagreements.

### F14 — A fiscal document is not a year-long organization chart (medium)

**Location:** `Checkpoint method and Estimates presentation`. **Basis:** FIN-2002; FIN-2005; FIN-2025.

Earlier-year comparison columns are restated to the current presentation. Cabinet changes within one year also make a ministry label year-dependent.

**Repair:** Use the actual document and as-of date. Do not read a restated prior-year column as historical parentage, or a checkpoint year as a full documented span.

### F15 — INDEX timeline counts are upstream assertions, not reproducible here (medium)

**Location:** `INDEX.md: Where things stand`. **Basis:** archive_data.

The reported counts are 23 for 2010 and 8 for 2000. A simple selected-start-year filter yields 25 and 13. This is not proof of a renderer bug: parent/lifecycle rules are absent.

**Repair:** Reproduce the actual resolver at the pinned revision and explain every inclusion/exclusion. Keep archive counts distinct from renderer regression tests.

### F16 — Record kinds mix organizations with programmes and delivery objects (medium)

**Location:** `sub-agencies.json: kind (82 programmes plus other kinds)`. **Basis:** archive_data.

A general-purpose public-sector atlas can include programmes and assets, but a uniform agency/daughter node implies relationships that evidence may not support.

**Repair:** Define display semantics by entity kind and relationship; do not remove programmes solely because they are not legal persons.

## 4. Completed Finance checkpoint pass

Twelve records were checked in each of 2002, 2005, 2010, 2015, 2020 and 2025. The selected scopes are the Finance vote descriptions, not every ministry, every supplementary estimate, every organization chart or every service plan. The 2005 scope includes Votes 22 and 23 but not Vote 24. Scope and locators accompany every result, including negative and ambiguous results. [FIN-2002–FIN-2025]

The 30 positives are named observations in contemporaneous budget presentation. They support neither an exact operational start nor an uninterrupted interval from that year to the present. The PSEC 2005 reference is contextual: the document names the council and its secretariat. It is not inserted as a formal alias called simply “Council Secretariat.” [FIN-2005]

| Present-day record | Earliest positive in this limited pass | What remains open |
|---|---:|---|
| Internal Audit & Advisory Services | 2002 [FIN-2002] | Founding, continuity and complete name/parent history |
| Office of the Comptroller General | 2002 [FIN-2002] | Founding, continuity and complete name/parent history |
| Treasury Board Staff | 2002 [FIN-2002] | Founding, continuity and complete name/parent history |
| Public Sector Employers' Council Secretariat | 2005 [FIN-2005] | Founding, continuity and complete name/parent history |
| Revenue Division | 2015 [FIN-2015] | Founding, continuity and complete name/parent history |
| Crown Agencies and Board Resourcing Office | 2020 [FIN-2020] | Founding, continuity and complete name/parent history |
| Gender Equity Office | 2020 [FIN-2020] | Founding, continuity and complete name/parent history |
| Anti-Money Laundering Secretariat | 2025 [FIN-2025] | Founding, continuity and complete name/parent history |
| Crown Agencies Secretariat | 2025 [FIN-2025] | Founding, continuity and complete name/parent history |
| Property Assessment Review Panels | 2025 [FIN-2025] | Founding, continuity and complete name/parent history |

**Government Chief Risk Office:** no accepted exact-name result from the six selected Finance scopes. The 2005 service plan’s Risk Management Branch is an explicit research lead, not an accepted identity match. **Provincial Treasury:** related budget headings are present, but their identity relationship to the current record is left unresolved rather than silently equated. [FIN-PLAN-2005; FIN-2002; FIN-2005; FIN-2010]

CABRO is named in the 2020 Finance presentation and Crown Agencies Secretariat in 2025. That alone does not establish whether the organizations are parallel, one replaced the other, one became a component, or the current queue duplicates a historical identity. Both original IDs are preserved. [FIN-2020; FIN-2025]

### Reading the checkpoint matrix

`found_name` is a named match; `found_contextual_name` is an unambiguous contextual naming; `related_label_identity_unresolved` preserves a potentially related name; `function_only` does not establish a named unit; `not_found_in_scope` is only a scoped search outcome. For ambiguous/function-only cases, `listed` is null rather than a misleading false. Every row explicitly sets global_absence_inferred to false.

The proposed JSON uses year precision, leaves established and ended null, keeps every new name row observation-only, supplies no inferred structural-parent edges, and marks every result documented_partial with full_history_complete false. It is intentionally not presented as a successfully imported production batch. Its richer search outcomes require validation against the actual importer.

## 5. Targeted historical and relationship checks

**Skilled Trades BC Appeal Board.** Section 42(1) continues the Industry Training Appeal Board. The board’s annual report gives 1 December 2022 as the rename date. The queue already holds a rename event; the correction here is to the generic ceased-body framing, not discovery of a previously unknown transition. Royal Assent and the rename’s effective date should not be conflated. [STBC-ACT; STBC-AR-2023]

**BC Ambulance Service.** The official BCEHS page describes the service as operating under BCEHS. Its appearance in the guide’s gone-discovery list is therefore unsafe. This check establishes a current description, not its complete historical lifecycle. [BCAS-CURRENT]

**Climate Action Secretariat.** The 2010 Estimates name it under Environment at printed page 100 / PDF page 110. This contradicts the queue’s 2010 Energy search lead, demonstrating why a modern ministry lineage cannot be used as a historical search boundary. [ENV-2010]

**Office of the Fire Commissioner.** The 2002 CAWS Estimates name the Office in Vote 19(g). The finding is a budget placement, not an inferred creation or an all-years parent relationship. [CAWS-2002]

**BC Ferry Commission.** Its own website emphasizes independence. Ministerial accountability, budget support and legal/structural inclusion are different relationships. The current parent field should not automatically be rendered as organizational subordination without examining what it means. [FERRY-CURRENT]

## 6. Specific inherited claims needing recovery

These are issues found in the uploaded snapshot, not newly verified resolutions of the underlying history. The event export omits the source locators needed to settle them.

**BC Timber Sales:** Held first observation 2003-05-29 precedes selected establishment 2003-06-20; other held succession evidence mentions 2003-04-01. Recover each source and distinguish planned listing, programme transition, launch and legal creation before selecting a date.

**BC Corrections:** Held events contain both 1950 and 1951 establishment descriptions. They need provenance and milestone reconciliation; documented_partial alone does not expose this issue.

**Civil Resolution Tribunal:** Held event rows repeat some milestones and give different July 2019 jurisdiction-expansion dates. Preserve source-level competing claims; do not collapse distinct milestones or deduplicate by text alone.

**BC Wildfire Service:** Held operating-name change is described as bounded by observations (last old name 2015-05-26, first new name 2015-07-02). An observation bound is not an exact rename date. Historical fire-protection law is a function origin, not the current unit’s creation.

**BC Parks:** The held sequence mixes the first park, earlier sections/divisions/branches and later reorganizations. Classify functional, organizational and naming events before proposing one continuous identity.

**Conservation Officer Service:** The held history contains abolition, restoration, amalgamation and separation of related functions/units. Do not turn a game-protection function into uninterrupted present-day agency existence.

**Environmental Appeal Board:** Already marked requires_reconciliation. Distinguish the 1981 legal/Act date from the competing 1982 establishment account; original supporting claims are not included in full here.

**Powertech Labs Inc.:** Already marked requires_reconciliation. A 1988 corporate milestone and operations since 1989 may date different things rather than conflict. Recover the actual claim wording.

**Energy Resource Appeal Tribunal:** The founding/in-force and historical-name statement sourced to a later multi-year annual report must be distinguished from a contemporaneous 2010 observation.

**Hospital Appeal Board:** The Medical Appeal Board name attributed to 1973 comes from a later about page. Preserve it as retrospective historical testimony, not a webpage captured in 1973.

**BC Cancer:** Separate the earlier treatment centre, 1974 agency identity, subsequent names/branding and society amalgamation. A current historical timeline is retrospective evidence even when it gives an exact day.

**BC Renal:** The parent row continuing_as_of_source needs the source observation/as-of date. A retrospective start and a current webpage observation are separate temporal facts.

**WorkBC:** Held 2007 strategy/website and 2012 service-centre events have different subjects. Do not choose one as the founding of every WorkBC component.

**BC Bid:** A held 1996 observation shows that stopping at 2002 can miss useful evidence. Establish the relationship between earlier procurement branding and the current service.

## 7. All 23 batches: tailored review

The following are review priorities, not claims that every indicated event, transfer or relationship has been newly verified. The searchable HTML and record-review JSON include every body and its existing questions.

### Batch 01 — Ministry of Attorney General (1 of 2) (14 records)

**Focus: Tribunal independence and legal milestones.** Separate administrative support, appointments and budget responsibility from organizational membership. Check creation, in-force provisions, initial appointments and first hearing dates separately. The Ferry Commission needs an independence-aware relationship model. Court Services and Sheriff Services also require pre-2002 rosters, rather than only modern tribunal pages.

### Batch 02 — Ministry of Attorney General (2 of 2) (13 records)

**Focus: Identity continuity and inherited date claims.** Reconcile the Environmental Appeal Board claim; distinguish legislation, opening and expanded jurisdiction for the Civil Resolution Tribunal. The Industry Training Appeal Board is continued, not abolished, under the Skilled Trades BC Act. Reclassify retrospective history statements currently represented as contemporary name observations. An existing date does not make Track B complete.

### Batch 03 — Ministry of Finance (12 records)

**Focus: Finance checkpoint evidence and unresolved identities.** This review checked 72 body-year combinations in selected Finance vote descriptions. Thirty positive observations cover ten bodies. Government Chief Risk Office remains unresolved; Risk Management Branch is a 2005 lead. Provincial Treasury Operations and Treasury remain related labels requiring an identity bridge. Do not merge CABRO and Crown Agencies Secretariat merely because budget headings change.

### Batch 04 — Ministry of Citizens’ Services (11 records)

**Focus: Service channels, long-lived offices and old names.** Service BC, BC Stats and BC Bid need predecessor and name histories extending before the oldest checkpoint. Search Queen’s Printer as well as King’s Printer. Distinguish the BC Services Card, BC OnLine and portals from the offices delivering them. Do not equate a historical government-agent function with the creation of the Service BC brand.

### Batch 05 — Ministry of Education and Child Care (10 records)

**Focus: Child-care transfers and different education institutions.** Treat the current Education parent as a search lead only, especially for earlier child-care services. Check the Early Childhood Educator Registry, centres and ministry programmes independently. The Teachers’ Council, Commissioner and disciplinary board need separate statutory identities. Feeding Futures, erase and StrongStart are programme histories, not necessarily histories of distinct offices.

### Batch 06 — Ministry of Health (13 records)

**Focus: Programmes, statutory offices and health governance.** Keep the Medical Services Plan and PharmaCare distinct from the Medical Services Commission and other governing bodies. The Provincial Health Officer requires appointment, statutory office and continuation dates as separate milestones. Review the newly named regulatory oversight office’s date despite its C-only routing. Portals and registries need programme-level evidence and historical delivery relationships.

### Batch 07 — Ministry of Public Safety and Solicitor General (12 records)

**Focus: Conflicting early dates and moved safety functions.** The queue contains different BC Corrections establishment years that need original citations. The Office of the Fire Commissioner is named in the 2002 CAWS vote, so searching only the present-day ministry line is insufficient. For gambling regulation, obtain the transfer instrument and distinguish functions transferred, old body ended and new office commenced. Do not derive these from a single press-release heading.

### Batch 08 — Ministry of Children and Family Development (8 records)

**Focus: Service categories versus named bodies.** Determine which records represent actual units, facilities, service networks or delivery functions. Maples is not interchangeable with the whole youth mental-health service. Child protection reporting, adoption, foster care and youth justice need programme and administrative-unit histories kept distinct. Search contemporary rosters before projecting current service labels into earlier ministry structures.

### Batch 09 — Ministry of Post-Secondary Education and Future Skills (8 records)

**Focus: Immigration, training regulation and branded platforms.** For private training, establish continuity or succession between earlier regulators and the current branch. Distinguish StudentAid and BC PNP programmes from administrative offices. The credential-recognition office and newer newcomer programmes need explicit launch/authority sources. EducationPlannerBC is not automatically a ministry branch merely because its service is relevant to that ministry.

### Batch 10 — Ministry of Water, Land and Resource Stewardship (8 records)

**Focus: Natural-resource transfers and portal identity.** River Forecast Centre, FrontCounter BC and resource programmes may cross several historical ministries. Reconstruct these at the source date, not from the current Water ministry’s lineage. The drought portal and Mineral/Water permitting interfaces are service products unless a source establishes a corresponding organizational unit. A programme’s policy origins are not its current-name start.

### Batch 11 — Provincial Health Services Authority (12 records)

**Focus: Health agencies, hospitals, networks and amalgamations.** Separate hospital/facility opening, society incorporation, operating agency formation, branding and PHSA placement. Cancer, Renal and Transplant already contain evidence that needs this distinction. Provincial Laboratory Medicine Services still has an unresolved review despite an existing date. BC Ambulance Service is not a safe gone-body example: its official page describes it operating under BCEHS.

### Batch 12 — Ministry of Energy and Climate Solutions (8 records)

**Focus: Historical climate placement and programme/account types.** The 2010 Estimates place Climate Action Secretariat under Environment, not the queue’s suggested Energy route. CleanBC is a plan/programme, while funds, pricing systems, standards and an advisory council have different legal and organizational meanings. Do not use a policy launch as a ministry or office creation date; preserve source-specific placement and the type of each relationship.

### Batch 13 — Ministry of Social Development and Poverty Reduction (8 records)

**Focus: WorkBC scope and independence of appeals.** Separate WorkBC strategy/website, employment-services delivery model and physical centres. Record assistance and bus-pass programme histories separately from delivery units and My Self Serve. The appeal tribunal, accessibility committee and directorate should not be assigned one uniform relationship to the minister simply because they occur in the same budget chapter.

### Batch 14 — Ministry of Tourism, Arts, Culture and Sport (7 records)

**Focus: Special accounts are not organizational departments.** Review whether the arts endowment and sports fund are statutory accounts, programmes or separate bodies. For Heritage and Mountain Resorts, use historical branch rosters and transfer instruments. Community Gaming Grants may move independently of gaming regulation. A promotional campaign such as Let’s Go BC needs campaign/programme semantics rather than an inferred office.

### Batch 15 — Ministry of Agriculture and Food (7 records)

**Focus: Within-year ministry changes and programme phases.** The 2005 checkpoint must use the ministry name printed in the specific document, not a later shuffle in the same calendar year. BCFIRB’s combined tribunal requires its earlier boards as separate predecessors where supported. Liquor/cannabis regulation moves independently of agricultural programmes. Investigate, rather than assume, continuity across Buy BC programme phases; distinguish the Animal Health Centre facility from the ministry’s entire animal-health function.

### Batch 16 — Ministry of Emergency Management and Climate Readiness and Ministry of Housing and Municipal Affairs (12 records)

**Focus: Emergency-management reorganizations and housing programmes.** Emergency Management BC and the newer ministry are not automatically a simple rename. Establish the old organization’s continuation, absorption or end from instruments. Housing and municipal records need histories independent of their current grouped batch: tenancy services, public libraries and University Endowment Lands are unlike the new housing-targets programme. Separate public portals, assistance programmes and statutory offices.

### Batch 17 — Ministry of Environment and Parks (7 records)

**Focus: Long functional lineages versus the current body.** Parks and conservation enforcement contain function, branch, amalgamation and separation milestones. Do not create a continuous present-day body stretching back to the first park or earliest game law. The Environmental Assessment Office needs legal and operational milestones distinguished. Park Enhancement and Sustainable Environment funds require special-account semantics, not automatically an agency node.

### Batch 18 — Transportation Investment Corporation and Ministry of Indigenous Relations and Reconciliation (12 records)

**Focus: Capital projects and Indigenous-relations units.** The six transportation projects are not six companies. Store project announcement, delivery responsibility, construction and opening separately. For Indigenous-relations divisions, use dated organization charts rather than guessing continuity from similar functions. First Citizens Fund is an account/programme question, and the advisory council and Declaration Act Secretariat need their own relationships and authority evidence.

### Batch 19 — Ministry of Mining and Critical Minerals and Columbia Power Corporation (9 records)

**Focus: Mining services and corporate ownership chains.** Separate the Geological Survey, development offices, permitting portals and regulatory functions. The critical-minerals office needs a specific formation source. For Columbia Power subsidiaries, use contemporaneous financial-statement notes to establish legal ownership, joint ventures and effective dates; a generating asset, power project and company can share a name without being the same entity.

### Batch 20 — Ministry of Forests and 2 more (14 records)

**Focus: Forestry date conflicts and programme/office distinctions.** BC Timber Sales has an observation before its selected start and competing succession milestones; classify these rather than overwrite one. The Wildfire Service’s name-change boundary is bounded by observations, not established as an exact day. Distinguish the Chief Forester’s office from the broader forestry function. Housing and business programmes in this batch should remain programme nodes, not automatically corporate subsidiaries.

### Batch 21 — Forestry Innovation Investment Ltd. and 2 more (11 records)

**Focus: Foreign subsidiaries, capital functions and labour offices.** Use corporate notes for the FII entities in China, India and Vietnam, preserving legal names rather than only trading brands. Capital/real-property functions need source-dated units. Workers’ and employers’ advisers need an independence/support model separate from WorkSafeBC membership. Labour tribunals require statutory continuity and parent/accountability evidence by period.

### Batch 22 — Ministry of Transportation and Transit and 3 more (14 records)

**Focus: Facilities, portals and Crown corporate milestones.** BC Place and the convention centre are venues as well as operated assets; distinguish opening from ownership/operation. PlayNow is not automatically a corporation. Powerex and Powertech need original date sources; incorporation in one year and operations in another can both be true. CVSE’s historic ministry placement must be checked independently from the current transportation lineage.

### Batch 23 — Liquor Distribution Branch and 5 more (8 records)

**Focus: Retail brands, archives, venues and investment ownership.** BCLIQUOR and BC Cannabis Stores need retail-brand/programme histories distinct from the Liquor Distribution Branch. BC Archives needs institutional continuity and the Royal BC Museum relationship by date. IMAX is a venue/operation, not necessarily a subsidiary. Corporate records for BCR Properties, broadband, Renaissance and QuadReal need legal ownership and operating milestones, without treating brand launch as incorporation.

## 8. Implementation contract before historical rendering

The existing documentation acknowledges that first_observed is not yet driving the historical display. A safe implementation needs more than selecting min(established, first_observed). That shortcut can apply a current name to an earlier predecessor, attach a unit to a ministry that did not yet exist, and draw an unproven uninterrupted interval.

An observation-only mode should display the dated evidence as evidence, with “start unknown” and “parent unresolved” states where appropriate. A continuity mode needs an explicit, reviewable continuity rule. Names and relationships must be resolved independently at the selected date. A documented end prevents later display; a name change does not automatically end the identity. Unresolved identity must remain visible rather than silently disappearing or merging.

Before release, test: an undated body with a 2002 observation; a current name with only an older predecessor observation; a renamed/continued tribunal; an independent commission appearing in a ministry budget; a project and an account; an end without a successor; overlapping predecessor and successor periods; a bounded rename; a retrospective history statement; a negative selected-section search; and a dated child whose historically valid parent is unresolved.

Import validation must reject unsourced lifecycle dates, missing precision, invalid source references, unsupported parent relations and full-history assertions inconsistent with review scope. A dry run should identify additions, competing claims, unchanged claims and rejected rows separately. Failed validation must not leave partial writes; retries should be idempotent. These are proposed acceptance criteria, not claims about code tested in this session.

## 9. Deliverables, verification and application

`audit/queue-audit.json` and `audit/record-review.json` cover all original records. `research/finance-checkpoints.json` records 72 scoped checks; `research/finance-proposed-observations.json` supplies ten candidate record updates; `research/identity-leads.json` preserves unresolved matches. `research/targeted-corrections.json` holds the five verified case checks. `research/source-register.json` identifies every primary source used for those outputs.

`patches/queue-methodology.patch` is a documentation patch against research/queue/ at the exact uploaded snapshot. It changes the README and the common wording in all 23 batch exports. It does not modify the generator, importer, research database, resolver or UI. Because batches are generated, the actual generator must receive the same wording changes at the matching repository revision or regeneration will overwrite the patch.

The proposed document copies are included for inspection. A local patch application check is recorded separately. Twenty local unit tests passed, including isolated patch application. A separate Chromium smoke test checked the 238-row display, search, batch/evidence filters, expanded details and mobile overflow (see `audit/browser-verification.json`). These checks validate the review artifacts, not production application behaviour. The local tests validate this review’s inventory, source references, evidence invariants and patch applicability; they do not run npm test, reproduce the Government diagram, validate all historic source claims or prove production importer compatibility. See `audit/verification.txt` for the actual test output.

Public main was inspected through its raw files. Its package contains build:government-history/build:government-events/build:government-atlas, but not the research:merge/build:government interfaces documented in this archive. This is a revision/reproducibility mismatch, not proof that the private or unshared upstream implementation does not exist. A container Git clone failed because the host could not be resolved. Some current government webpages also could not be opened in this session; those access failures are not claims that the sites are down. [REPO-PACKAGE]

### Recommended order

First pin the source revision and recover full inherited claims. Fix the research instructions before parallel research expands the same mistakes. Import verified observations only after adapting/validating the real schema. Add temporal identity and typed-placement tests before enabling first-observation rendering. Then work across contemporary historical rosters to capture non-surviving bodies; extend the remaining batches with the same explicit source scopes and unresolved-identity handling.

## 10. Source register

All sources below were opened during this review. The locators define the checked portions; a citation to a large PDF is not a claim that its complete contents were examined. URLs are included here so the review remains usable outside this chat.

### FIN-2002 — 2002/03 Estimates — Ministry of Finance

https://www.bcbudget.gov.bc.ca/2002/Estimates/html/MINISTRY_OF_FINANCE.htm

**Checked scope:** Vote 26, classification by sub-vote and vote description (HTML). **Checked:** 2026-09-30.

### FIN-2005 — 2005/06 Estimates — Ministry of Finance

https://www.bcbudget.gov.bc.ca/2005/est/22-23_Finance.pdf

**Checked scope:** Votes 22 and 23; PDF pages 3–5 / printed pages 81–83. Vote 24 is outside this checkpoint scope.. **Checked:** 2026-09-30.

### FIN-2010 — 2010/11 Estimates — Ministry of Finance

https://www.bcbudget.gov.bc.ca/2010/estimates/2010_Estimates.pdf

**Checked scope:** Finance Vote 32 descriptions; PDF pages 119–121 / printed pages 109–111. **Checked:** 2026-09-30.

### FIN-2015 — 2015/16 Estimates — Ministry of Finance

https://www.bcbudget.gov.bc.ca/2015/estimates/2015_Estimates.pdf

**Checked scope:** Finance Vote 23 descriptions; PDF pages 97–99 / printed pages 87–89. **Checked:** 2026-09-30.

### FIN-2020 — 2020/21 Estimates — Ministry of Finance

https://www.bcbudget.gov.bc.ca/2020/pdf/2020_Estimates.pdf

**Checked scope:** Finance Vote 25 descriptions; PDF pages 97–99 / printed pages 89–91. **Checked:** 2026-09-30.

### FIN-2025 — 2025/26 Estimates — Ministry of Finance

https://www.bcbudget.gov.bc.ca/2025/pdf/2025_Estimates.pdf

**Checked scope:** Finance Vote 26 descriptions; PDF pages 101–103 / printed pages 91–93. **Checked:** 2026-09-30.

### FIN-PLAN-2005 — 2005/06–2007/08 Finance Service Plan — Ministry overview and core business areas

https://www.bcbudget.gov.bc.ca/2005/sp/fin/Ministry_Overview_and_Core_Business_Areas.htm

**Checked scope:** Core business areas: Treasury and Executive and Support Services. **Checked:** 2026-09-30.

### STBC-ACT — Skilled Trades BC Act, SBC 2022, c. 4

https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/22004

**Checked scope:** Section 42(1), continuation of the appeal board. **Checked:** 2026-09-30.

### STBC-AR-2023 — Skilled Trades BC Appeal Board — Annual Report 2022–2023

https://www.stbcab.ca/app/uploads/sites/771/2023/08/STBCAB_AR_2022-23.pdf

**Checked scope:** PDF page 3, transmittal letter; PDF page 5, continuation under section 42. **Checked:** 2026-09-30.

### BCAS-CURRENT — BC Emergency Health Services — BC Ambulance Service

https://www.bcehs.ca/about/who-we-are/bc-ambulance-service

**Checked scope:** Main body: service description and operation under BCEHS. **Checked:** 2026-09-30.

### FERRY-CURRENT — BC Ferry Commission — official home page

https://www.bcferrycommission.ca/

**Checked scope:** Statement of independence from the Province, BC Ferry Authority and BC Ferries. **Checked:** 2026-09-30.

### ENV-2010 — 2010/11 Estimates — Ministry of Environment

https://www.bcbudget.gov.bc.ca/2010/estimates/2010_Estimates.pdf

**Checked scope:** Climate Action Secretariat; PDF page 110 / printed page 100. **Checked:** 2026-09-30.

### CAWS-2002 — 2002/03 Estimates — Ministry of Community, Aboriginal and Women’s Services

https://www.bcbudget.gov.bc.ca/2002/Estimates/html/MINISTRY_OF_COMMUNITY.htm

**Checked scope:** Vote 19, paragraph (g), Safety and Standards: Office of the Fire Commissioner. **Checked:** 2026-09-30.

### REPO-PACKAGE — PofBC public main — package.json, observed 2026-09-30

https://raw.githubusercontent.com/ahzs645/PofBC/main/package.json

**Checked scope:** scripts object; public main is not pinned to uploaded queue revision. **Checked:** 2026-09-30.

### REPO-HISTORY-BUILDER — PofBC public main — build-government-history.mjs, observed 2026-09-30

https://raw.githubusercontent.com/ahzs645/PofBC/main/scripts/build-government-history.mjs

**Checked scope:** Compiler structure and exported agency fields; not executed locally. **Checked:** 2026-09-30.

