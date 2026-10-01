# PofBC research queue — worked review of the revised archive

**Input:** `pofbc-research-queue(1).zip` · **Review date:** 30 September 2026.

## Verdict

This is a useful, internally consistent research-assignment export, and it is materially safer than the earlier version. It is not yet a self-sufficient, production-validated historical database. The biggest remaining problem is not the number of records: it is preserving the meaning and provenance of each claim all the way from source to selected date, historical relationship and displayed node.

I reviewed the complete 26-file archive, all 23 batch packets and all 238 exported records. I also worked selected primary-source cases, recorded 24 candidate claims for 15 existing records, checked one additional record at function-only scope, and identified three candidates outside the 238-item snapshot. This is not a claim that 238 complete histories were independently researched. The evidence ledger separates newly developed findings from rechecked inherited evidence and preserves unresolved interpretations.

Nothing was imported into the production research database or deployed. The original export is retained unchanged. The patch changes exported documentation only; the absent generator, importer and renderer still require revision-specific work.

## 1. What was checked, and what passed

The archive contains a README, an INDEX, one machine-readable queue and 23 batch Markdown files. All JSON skeletons parse. Their IDs, order, names, kinds and present-day parent IDs match the queue. Each record is assigned to exactly one batch. INDEX totals and priority counts agree with the machine-readable data. No structural inconsistency was found in those checks.

| Measure | Recomputed result |
|---|---:|
| Original files / batches | 26 / 23 |
| Records / unique IDs | 238 / 238 |
| Distinct current-parent IDs | 37 |
| P1 / P2 / P3 | 180 / 19 / 39 |
| Not researched / documented partial / requires reconciliation | 197 / 39 / 2 |
| Selected establishment dates | 39 |
| Selected first-observed values | 10 |
| Records with historical name rows | 14 |
| Records with historical parent rows | 11 |
| Event rows / records containing events | 175 / 53 |
| Events with source URLs | 175 |
| Events with both source URLs and locators | 172 |
| Records without an official_url field | 57 |
| Records with neither a selected start nor a first observation | 191 |

These are coverage and export-shape counts, not a historical quality score. A missing official URL does not mean no official website exists. No exported parent history does not prove that the current parent is wrong. A source URL and locator make a claim traceable, but do not themselves prove the source supports the asserted event.

The complete calculations, per-file SHA-256 hashes and structural results are in `audit/queue-audit.json`. All 238 records have dispositions in `audit/record-triage.json`; every batch has a dedicated Markdown review under `batch-reviews/`.

### Improvements that should be retained

The revised guide correctly treats a negative search as a result within the pages read, not evidence of nonexistence. It retains ambiguous-name and function-only outcomes, distinguishes retrospective testimony from contemporary observation, warns against using budget placement as organizational parentage, and requires independent cessation evidence. It recognizes that following today's surviving bodies backward is not a historical census. The handback is consistently one batch object containing records.

Most importantly, all 175 inherited event rows now retain source URLs. Only three lack locators. These are real improvements; repeating the previous criticism that every event lost its source would be wrong for this upload.

## 2. Remaining high-impact findings

### F01 — Selected dates still lose their original claim objects

The 39 selected establishment values and 10 selected first-observed values are scalars. The export does not preserve the complete original selected claims, their source-specific basis, precision, review history or all competing date claims. An event with the same date is not necessarily the source from which the selected date was chosen.

Six selected starts have no same-date event at all: the container-trucking commissioner, the health-professions regulatory oversight office, Provincial Laboratory Medicine Services, Powerex, Powertech Labs and Columbia Basin Broadband Corporation. That is an export/provenance problem, not proof that the dates are false.

**Repair:** export the selected dated claim itself, including meaning, precision, source and locator, alongside its alternatives and editorial selection decision. Keep stable claim identifiers. Do not reconstruct provenance by matching on the date alone.

### F02 — A date still routes unfinished research away from Track B

Six dated records remain `not_researched` while their queue work is C-only: BC Prosecution Service; the container-trucking commissioner; the health-professions regulatory oversight office; Provincial Laboratory Medicine Services; Powerex; and Columbia Basin Broadband Corporation.

**Repair:** separate scheduling priority from evidence maturity. A selected date does not close founding research. Add a required original-claim review for these six, and preserve the explicit reconciliation states of EAB and Powertech.

### F03 — Two range events are flattened to a single endpoint

The Conservation Officer Service has a `year_range` event with date `1909` and a locator referring to `1909-14`, but no explicit upper endpoint. BC Wildfire Service has a `day_range` name-change event dated `2015-05-26`, with only the older-name source in that row. The separate first new-name observation exists in the snapshot but is not linked as the range's other bound.

This can create false precision or lose the uncertainty when a consumer expects a single date. Even an old-name observation followed by a new-name observation does not, without further assumptions, rule out overlapping usage.

**Repair:** preserve each observation and its source separately. Restore explicit bounds where the original claim provides them. Distinguish an inferred change window from a source-stated interval. Do not coerce a range to an exact day/year to make a validator accept it. The included review-ledger validator rejects unsupported single-endpoint range precision; it does not implement a production interval schema.

### F04 — Source-to-locator mapping remains incomplete

Three inherited events lack locators: two BC Parks events and the Wildfire Service's 1912 retrospective-origin claim. I rechecked the official Parks history and supplied two exact event-matched locator proposals. The Wildfire locator remains unresolved because the relevant page content could not be inspected adequately in this session. [PARKS-HISTORY]

Two other events have multiple URLs sharing one locator: Public Guardian and Trustee's 1963 event, and EAO's 1995 event. The locator must be checked for each source individually; an archive authority-record locator does not automatically apply to a news release.

**Repair:** apply the two Parks locator corrections at the original upstream claims, then regenerate. Recover the third locator and split multi-source references into source-specific evidence entries. The exported data in this package are intentionally not rewritten.

### F05 — Observation time, publication time and historical time need separate fields

A current page read on 30 September 2026 can report that an institution began in 1859, and can display a 2025 last-updated date. Those are three different temporal facts. A later history statement is not a contemporary observation of the nineteenth-century institution. Similarly, BC Renal's `continuing_as_of_source` parent row lacks an explicit observation/as-of date.

**Repair:** keep historical effective date and precision, document publication/revision date and its role, and research observation date separately. Do not backdate current relationships to the page's last-updated value. Every “continuing as of source” row needs a source observation date.

### F06 — Current parent, budget location and organizational structure remain easy to conflate

The inventory mixes 82 programmes with divisions, offices, boards, tribunals, agencies and subsidiaries. Some programme records represent accounts, portals, projects, facilities or broad service categories. The `part_of` and `subsidiary_of` choices cannot safely express every relationship in that mix.

The Comptroller General's current page gives a reporting relationship to the Deputy Minister of Finance and separately names Internal Audit & Advisory Services in its service description. That supports more specific observations than simply placing all Finance records at one level, but does not itself establish every direct organizational edge. [OCG]

**Repair:** define entity and relationship semantics before rendering. Keep budget placement, reporting responsibility, administrative support, ownership and organizational membership distinct. An unsupported historical parent should remain unresolved, not be silently replaced by today's parent or used to hide a documented body.

### F07 — The merge and renderer promises cannot be reproduced from this ZIP

The guide documents `research:merge`, `build:government` and `build:research-queue` commands and describes atomic, non-destructive merge behaviour. The inspected public-main package has differently named government build scripts and does not expose those three aliases. There is no pinned commit proving public main matches the uploaded queue. [REPO-PACKAGE]

The ZIP contains no application implementation. A container clone failed on DNS resolution; no npm test, production importer or live Government resolver was executed. This is a revision/access gap, not proof that an implementation does not exist on another branch.

The guide itself says `first_observed` is compiled but not yet used for historical drawing. Collecting observations is therefore necessary evidence work, not a completed display fix. Drawing from the earliest sighting onward also requires an explicit continuity policy and independent name/parent resolution.

**Repair:** pin the revision, include the generator/importer schemas and dependency files, run the real dry run and tests there, then test the historical resolver separately. The included documentation patch replaces unverified runtime guarantees with these acceptance gates.

### F08 — Some documentation still encourages mistaken certainty

The README says regenerated data are “always current,” although this is a dated snapshot. Track A initially describes `listed` as true/false even though the detailed outcome table correctly includes null. One illustrative quotation appears to assert a real Gender Equity Office founding date without an identified source; it should be an unmistakable placeholder. An example source-check scope also risks being copied as if verified.

**Repair:** mark the snapshot date, preserve the outcome tri-state, and label examples as examples. Require original-date review even for C-only records and prohibit interpolating periods between sightings. These changes are included in the 24-file documentation patch.

## 3. Primary-source cases actually worked

### Education: a useful legal commencement checkpoint

The Teachers Act distinguishes the council, the commissioner and the disciplinary board. Section 9 supplies the council's establishment provision; section 26 supplies the board's. The commencement instrument, B.C. Reg. 239/2011 / OIC 620/2011, brings the relevant framework into force on **9 January 2012**. The legislative-changes table corroborates commencement. The November 2011 Royal Assent date is a different milestone. [TEACHERS-ACT; TEACHERS-COMMENCE; TEACHERS-TLC]

The ledger records candidate legal-commencement evidence for the council and board, and the commissioner's framework separately from any first actual appointment. It does not infer first meetings, full staffing or first operations from the commencement order. The current consolidated statute's wording is not wholesale backdated to 2012.

Three discovery candidates follow from the same transition: the British Columbia College of Teachers' dissolution; the director of certification framework; and the Teachers Act Special Account. They are outside this 238-item snapshot, not necessarily absent from the full atlas. Their candidate keys are not production IDs, and no successor/parent edges are automatically created. [TEACHERS-ACT; TEACHERS-COMMENCE]

### StrongStart: announcement is not every centre's opening

The government release dated **14 December 2006** announces the StrongStart early-learning-centre initiative and prospective centre openings. This supplies a programme-launch announcement milestone. It does not show that all centres opened that day, or establish every later form of the programme as the same unchanged entity. [STRONGSTART-2006]

### Trans Care BC: planned and reported-actual transitions

A release dated **30 October 2014** described a planned April 2015 transfer of provincial coordination responsibility to PHSA. PHSA's retrospective programme description says it took responsibility in **fall 2015**. Both are retained, with different event meanings. The ledger does not invent 1 April or 1 September as an operational start, and preserves “fall” as a qualifier on year precision. [TRANS-2014; TRANS-PHSA]

This is exactly the kind of case in which taking the earliest date mentioned would create a false founding date. The next evidence should establish the actual administrative transfer and the programme's own operational/name milestones.

### Powertech, Powerex and Columbia Hydro Constructors

BC Hydro's current subsidiaries page identifies all three as wholly owned subsidiaries. These are observations of a current page on the review date, not evidence that ownership began on that date or remained unchanged from incorporation onward. The CHC section reports formation in **1962**. [HYDRO-SUBS]

Powerex's own description says it has been active since **1988**; that is operations/history testimony, not an incorporation certificate. The rechecked 2009 BC Hydro release says Powertech had served customers since **1989**. That does not disprove a distinct incorporation milestone in 1988. The original selected 1988 claim must be recovered before editorial reconciliation. [POWEREX-ABOUT; POWERTECH-2009]

### Environmental Appeal Board: keep the original 1981 basis unresolved

The Board's practice manual, visually checked at PDF page 8, explicitly reports establishment in **1982**. Its home page uses “1981” as part of the Act reference. The homepage alone is not an equally explicit statement that the Board was established in 1981. [EAB-MANUAL; EAB-HOME]

This strengthens a reconciliation case; it does not authorize silently overwriting the inherited selected date. The missing original 1981 claim and the relevant commencement material still need to be examined. This source check also shows why claim wording matters more than simply counting dates on pages.

### BC Parks: two traceability repairs, not a new founding decision

The official Parks history supports the **1 March 1911** Strathcona legislation milestone and a separate **1957** Parks Branch organizational milestone. The ledger supplies source-section locators for both previously unlocated events. It does not reclassify the first park's legislation as the founding of every later Parks organization. [PARKS-HISTORY]

### Climate and Environment: a scoped historical observation

The 2010/11 Estimates were visually checked at PDF page 110 / printed page 100. Climate Action Secretariat is a named sub-vote under Environment. Sustainable Environment Fund Special Account is named in the Environmental Protection description. Water licensing is described as a function, which was not accepted as proof of identity for the current Water Licensing and Rights record. [EST-2010-ENV]

This rechecks the earlier Climate Action Secretariat finding rather than claiming to discover it again. The three search outcomes are limited to this inspected page; they are not a census of the whole volume. Neither positive observation becomes a founding date or a structural-parent edge automatically.

### King's Printer: preserve colonial scope

The BC Laws FAQ reports an **1859** institutional origin. That is useful retrospective testimony, but does not date the current King's Printer name, establish a particular post-1871 ministry relationship, or resolve continuity across every administrative reorganization. [PRINTER-FAQ]

## 4. Important inherited questions that remain unresolved

The following are findings about the snapshot's claims, not new independent historical determinations:

- **BC Timber Sales:** selected start 20 June 2003; earlier name observation 29 May 2003; another succession milestone 1 April 2003. Determine what each dates.
- **BC Corrections:** inherited 1950 and 1951 establishment descriptions. Source access failed this session, so neither was selected as correct.
- **Civil Resolution Tribunal:** repeated milestones and differing 1 July / 15 July 2019 jurisdiction-expansion dates. Do not deduplicate by text or collapse separate legal/operating milestones.
- **BC Wildfire and Conservation Officer Service:** recover the range bounds and distinguish functional history, organizational history and operating-name evidence.
- **BC Cancer, BC Children's, BC Renal and WorkBC:** separate institutions/facilities/components, legal/brand changes, historical placement and programme phases rather than imposing one uninterrupted identity.

The batch reviews retain targeted follow-up for these and other records. The access log distinguishes failed opens and leads from completed source reads. An unsuccessful fetch is not evidence that the organization, source or event does not exist.

## 5. All 23 batches: what the packet provides

Each batch has a tailored review, an appropriate next source set, and a record-by-record disposition with inherited dates, event/name/parent counts, export flags, original questions, next actions and any candidate evidence IDs. The searchable HTML exposes all 238 records, not only the worked examples.

The batch sequence covers: Attorney General and tribunals (01–02); Finance (03); Citizens' Services (04); Education and child care (05); Health (06); Public Safety (07); MCFD (08); post-secondary/immigration/training (09); water/resource services (10); PHSA (11); climate/energy (12); social assistance (13); tourism/culture/sport (14); agriculture (15); emergency management/housing (16); Environment/Parks (17); transport projects/Indigenous relations (18); mining/power companies (19); forestry/business/housing programmes (20); FII/infrastructure/labour (21); transport/Hydro/venues (22); and retail/archives/investment holdings (23).

Batch-specific notes are hypotheses and work instructions unless linked to the explicit evidence ledger. A complete disposition is not equivalent to a completed history. The original P1/P2/P3 values and statuses remain untouched so the review does not make progress appear more complete than it is.

## 6. Implementation contract for the actual repository

The next code work needs three separate, testable layers.

**Export and evidence layer.** Retain full dated claims, alternative claims, source-specific locators, source publication/revision metadata, observation dates and explicit uncertainty. Include the upstream revision and dependency hashes. Preserve access failures and scoped negatives without allowing them to become lifecycle boundaries. Original claims must round-trip without loss.

**Import and editorial layer.** Validate the complete handback against the real schema, not this review's sidecar format. A dry run should distinguish accepted additions, unchanged evidence, competing claims, unresolved identities and rejected rows. Invalid batches must not partly write. Repeated application must not duplicate evidence. An editorial winner must retain alternatives and a decision record. These are requirements; no production importer behaviour was tested here.

**Temporal resolver and display layer.** Resolve existence, name and relationship independently at the selected date. Observation-only evidence should be visibly distinguished from a documented interval. A current name must not overwrite an earlier identity, and a present-day parent must not be projected backward. Support unknown-start and unresolved-parent states. A renamed but continued body is not necessarily abolished; an overlapping successor does not establish its predecessor's end.

Required renderer fixtures should include an undated body observed historically; predecessor-only naming; a continued tribunal; an independent body in a ministry budget; a programme/account/project; an uncertain name-change window; overlapping predecessor and successor; retrospective testimony; a scoped negative search; and an otherwise documented child with no resolved parent. The site should not silently drop evidence in any of those cases.

## 7. Included repairs, tests and limits

`patches/queue-review-safeguards.patch` changes the README and common instructions in all 23 exported batches: **24 documentation files**. It applies to `research/queue/` containing the exact uploaded snapshot. `proposed-queue/` contains the resulting full export for inspection; its `sub-agencies.json` is byte-identical to the original. The patch does not change the generator, importer, renderer, production dates or relationships. Regeneration will overwrite exported-document changes until the upstream generator receives equivalent fixes.

`research/locator-corrections.json` contains two exact-event-matched BC Parks locator proposals. They are not automatically applied to the source data. `research/evidence-ledger.json` is a review-specific, source-linked sidecar, not a claimed production-compatible batch. It has 24 claims, 16 source records, three scoped source checks and three discovery candidates.

**35 local unit tests pass.** They cover audit reproducibility, full archive counts, patch application and exact proposed-file matching, original-data preservation, source references and locators, calendar/precision checks, unsupported range rejection, tri-state search outcomes, candidate safeguards and retention of important milestone distinctions. They validate the review artifacts and explicit invariants, not historical truth, production import or the live Government diagram. The test log is `verification/tests.txt`.

The HTML includes the complete report, all claims, all batch dispositions and all 238 searchable records. Twelve browser checks passed for the generated review HTML: record/batch/claim/source counts, search, filters, expansion, desktop/mobile overflow and JavaScript errors. Results are in `verification/browser-check.json`. The browser rendered the generated HTML content directly because file navigation was blocked by environment policy; these are not Government application tests.

The source documents were read through web tools; the two selected PDF pages were visually checked. External source bytes are not archived. URLs, read scopes, document-date roles and locators are included to make the work inspectable, but source-content reproducibility still requires dated captures or local source artifacts. The upstream commit remains unknown. The original input and output files are hashed in the manifest.

## 8. Recommended order of work

First restore original selected claims and pin the repository revision. At the same time, apply equivalent documentation safeguards to the actual generator so parallel research does not reproduce the same mistakes.

Next review the concrete candidate evidence: the Teachers Act transition, StrongStart launch, Trans Care planned-versus-actual transfer, corporate milestone distinctions, EAB wording, the two Parks locators and scoped Environment observations. Add facts as separate claims before selecting dates or inventing relationships. De-duplicate the three discovery candidates against the full atlas.

Then implement and test the evidence-preserving export/import contract and the temporal resolver independently. Do not enable a simple minimum-of-start-and-first-observation shortcut.

Finally expand historical coverage through contemporary rosters and financial-statement subsidiary lists, including bodies that did not survive to 2026. Work the remaining batches using explicit source scopes and identity checks. More nodes should be the outcome of supported historical discovery, not a substitute for it.

## 9. Primary-source register

The source IDs above refer to the documents below. Read scopes do not imply complete-volume review. URLs are provided for use outside this chat.

### TEACHERS-ACT — Teachers Act, SBC 2011, c. 19 — current consolidation

https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/11019_01

**Inspected scope:** Sections 2, 6, 8, 9, 26, 85, 87 and 99; assent header. Current wording is not backdated wholesale. **Read:** 2026-09-30. **Document date:** 2026-09-22; consolidation current to. External source bytes are not archived.

### TEACHERS-COMMENCE — B.C. Reg. 239/2011, OIC 620/2011

https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v54n24_239-2011

**Inspected scope:** Opening order and clause (a); approved 2011-12-13, deposited 2011-12-14, effective 2012-01-09. **Read:** 2026-09-30. **Document date:** 2011-12-31; Gazette issue date. External source bytes are not archived.

### TEACHERS-TLC — Teachers Act — Table of Legislative Changes, 2nd Edition

https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/e2tlc11019

**Inspected scope:** Rows for sections 1–29, 36–85, 86–97 and 99(2); corroborates commencement, not a substitute for the instrument. **Read:** 2026-09-30. **Document date:** 2013-12-31; table coverage end, not publication date. External source bytes are not archived.

### STRONGSTART-2006 — Province launches StrongStart early learning centres

https://archive.news.gov.bc.ca/releases/news_releases_2005-2009/2006EDU0131-001512.htm

**Inspected scope:** Dateline, title and opening paragraphs; new programme announcement and prospective centre openings. **Read:** 2026-09-30. **Document date:** 2006-12-14; news release dateline. External source bytes are not archived.

### TRANS-2014 — Programs and services for transgender community to be strengthened

https://news.gov.bc.ca/releases/2014HLTH0119-001650

**Inspected scope:** Release body: planned April 2015 provincial coordination transfer to PHSA; excludes present-day sidebar. **Read:** 2026-09-30. **Document date:** 2014-10-30; news release dateline. External source bytes are not archived.

### TRANS-PHSA — Trans Care BC — Who We Are (PHSA archive site)

https://www.phsa.ca/transcarebc-archive/about/who-we-are

**Inspected scope:** Transgender/trans health steering committee; Program progress. Publication date not provided. **Read:** 2026-09-30. **Document date:** not stated; no publication date asserted. External source bytes are not archived.

### HYDRO-SUBS — BC Hydro — Subsidiaries

https://www.bchydro.com/toolbar/about/who_we_are/subsidiaries.html

**Inspected scope:** Powerex, Powertech Labs and Columbia Hydro Constructors Ltd. sections. **Read:** 2026-09-30. **Document date:** not stated; no publication date asserted. External source bytes are not archived.

### POWERTECH-2009 — Powertech awarded Shell contract for high capacity hydrogen fuelling station

https://www.bchydro.com/news/press_centre/news_releases/2009/powertech_hydrogen_station.html

**Inspected scope:** Dateline, opening paragraph and About Powertech. **Read:** 2026-09-30. **Document date:** 2009-09-09; news release dateline. External source bytes are not archived.

### POWEREX-ABOUT — Powerex — 24×7 Clean Load Service

https://clean24x7.powerex.com/

**Inspected scope:** About Powerex paragraph only: active since 1988; undated retrospective account. **Read:** 2026-09-30. **Document date:** not stated; no publication date asserted. External source bytes are not archived.

### EAB-MANUAL — Environmental Appeal Board — Practice and Procedure Manual

https://www.bceab.ca/uploads/2021/04/eab_proc_manual.pdf

**Inspected scope:** PDF page 8 of 65, sections 1.0 and beginning of 2.0. **Read:** 2026-09-30. **Document date:** 2019-04; revision shown in page footer. External source bytes are not archived.

### EAB-HOME — Environmental Appeal Board — official home page

https://www.bceab.ca/

**Inspected scope:** Opening paragraph; the parenthesized 1981 is attached to the Act title. **Read:** 2026-09-30. **Document date:** not stated; no publication date asserted. External source bytes are not archived.

### PARKS-HISTORY — History of BC Parks

https://bcparks.ca/about/our-mission-responsibilities/history/

**Inspected scope:** Very first provincial park; Distinction between park and forest management. Retrospective narrative. **Read:** 2026-09-30. **Document date:** not stated; no publication date asserted. External source bytes are not archived.

### OCG — Office of the Comptroller General

https://www2.gov.bc.ca/gov/content/governments/organizational-structure/ministries-organizations/central-government-agencies/office-of-the-comptroller-general

**Inspected scope:** Opening reporting relationship and Internal audits / Internal Audit & Advisory Services section. **Read:** 2026-09-30. **Document date:** 2025-11-24; page last updated; NOT an observation date. External source bytes are not archived.

### PRINTER-FAQ — BC Laws — FAQ displayed with Teachers Act legislative-history directory

https://www.bclaws.gov.bc.ca/civix/content/complete/statreg/1089244767/170718998/398788026/?xsl=/templates/browse.xsl

**Inspected scope:** FAQ question What is the Queen’s Printer?, answer describing King’s Printer origins in 1859. Preserve colonial/institutional scope. **Read:** 2026-09-30. **Document date:** not stated; no publication date asserted. External source bytes are not archived.

### EST-2010-ENV — 2010/11 Estimates — Environment vote descriptions

https://www.bcbudget.gov.bc.ca/2010/estimates/2010_Estimates.pdf

**Inspected scope:** PDF page 110 / printed page 100 only: Climate Action Secretariat, Sustainable Environment Fund Special Account and water-licensing function. **Read:** 2026-09-30. **Document date:** 2010; edition year, exact publication day not checked. External source bytes are not archived.

### REPO-PACKAGE — PofBC public main package.json — unpinned observed revision

https://raw.githubusercontent.com/ahzs645/PofBC/main/package.json

**Inspected scope:** Scripts object. This is not demonstrated to match the uploaded queue. **Read:** 2026-09-30. **Document date:** not stated; no publication date asserted. External source bytes are not archived.

