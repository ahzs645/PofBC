# PofBC Round 4 source and dataset handoff audit

Reviewed commit: `0dbdb18cfebfb27e5529ce5940850e96eb9a995c`. Prepared 21 October 2026.

## Finding

The consolidated research package already contains the source URLs that the integration notes call missing, together with substantial earlier datasets omitted from the three evidence archives. The immediate problem is an incomplete handoff into integration. Recovering a URL removes that retrieval blocker; it does not settle the separate identity, model, date or legal-instrument questions.

The audit maps **14 explicit missing-URL/dataset hold groups**, covering **82 unique cited claim IDs**. The claim-based groups use **56 distinct source IDs**, and every one has a literal URL in the original consolidated catalogue. The catalogue has **1,492 records, including 1,178 retained prior sources**. No live webpage was re-verified in this mapping audit.

**Thirty-two of the 66 prior structured components have no exact JSON copy anywhere in the repository’s research files.** The 34 retained payloads are exact copies. This is a file-presence result, not a claim that every fact in a missing file is absent from the atlas: D2 and D3, for example, were independently integrated from other carried evidence.

There is also an error in our supplied branch archive: `branches/prior/claims.json` contains the **26 logo claims**, not the **279 branch claims**. The consolidated JSON retains both components correctly. The original prior `handback-importable.json` is also present unchanged in the repository, so its importable records remain recoverable. The filename collision belongs to the research packaging, not the integrator.

The archive README distinguishes the three new evidence volumes from the separate consolidated reports and prior source manifest. The integration notes accurately describe their limited three-archive input, but statements that the entire research handback lacks these sources or datasets are too broad.

## Explicit rejected groups and recovered sources

Each group below preserves the current integration reason and the remaining gates. The JSON companion includes every original claim record and locator, its component path and JSON pointer, and the complete referenced source metadata.

| Group | Current hold | Claims | Source IDs | Remaining decision |
|---|---|---:|---:|---|
| SR-health-09 | Health service delivery areas (A9): sixteen by June 2002; Vancouver Island changes June 2003 | 3 | 2 | HSDAs are statistical/service geography, not corporate bodies; an area model is still needed. |
| SR-health-10 | Providence Health Care, Bella Coola General Hospital, R.W. Large Memorial Hospital "affiliated with" Vancouver Coastal Health (2005) | 3 | 1 | The affiliated hospitals are not present atlas bodies; any new identities require review. |
| SR-health-11 | Abbotsford (Regional) Hospital and Cancer Centre Inc.: incorporated 2 September 2003, owned by Partnerships BC; shares to Fraser Health (85%) and PHSA (15%) on 6 May 2008 | 4 | 2 | The company requires a reviewed identity/node and dated ownership edges. |
| SR-health-12 | Nisga'a Valley Health Board / Authority (A10) | 5 | 2 | Nisga’a institutions must not be placed beneath a provincial ministry; governance and model review remain. |
| SR-health-13 | SSO Administration Society 2009-2010: operations from 1 April 2009, member and PHSA approvals (30 March, 12 April 2010), assets to PHSA/HSSBC 17 September 2010 | 5 | 1 | Review SSO Administration Society, PHSA and HSSBC as distinct identities and legal/program forms. |
| SR-health-14 | Forensic Psychiatric Services Commission (B6): resources from the Ministry 1 April 1999; funded through PHSA 2002/03; board reconstituted by OIC 1424/1998 (19 November 1998) | 3 | 2 | The Commission needs an admitted identity and its statutory creation/commencement evidence. |
| SR-health-15 | Provincial Language Services (2003) and Perinatal Services BC (2009/10) | 2 | 2 | Provincial Language Services lacks a current atlas ID; preserve the stated year precision. |
| SR-health-16 | Health Insurance BC administrative services from 1 April 2005 (C4) | 1 | 1 | Health Insurance BC is an administrative contract/program name, not a newly incorporated public body. |
| SR-health-17 | Health profession colleges (C5): HPA designations, six mergers 2018-2024, HPOA commencement 1 April 2026 | 32 | 25 | A regulator layer or reviewed agency identities are still required; regulation is not service delivery. |
| SR-health-19 | FNHA governance (A11): the 2011 Framework Agreement, the 2007 plan, the First Nations Health Council (2007) and the FNHDA secretariat model | 8 | 4 | Keep First Nations governance and accountability distinct from provincial ministry hierarchy. |
| SR-carried-01 | Provincial Elections Act 1939 in force 1 April 1940 (RSBC 1936 c. 84 repealed); 1872 voters Act reserved-bill assent proclaimed 26 October 1872 (G5) | 4 | 2 | The franchise needs a dated data model and legal-event subjects; these are not new administrative bodies. |
| SR-carried-05 | regulator_designation_crosswalk.json (16 colleges), regulator_merger_crosswalk.json (6 mergers) | 32 | 25 | Duplicate of the health regulator hold; same identity, regulator-layer and date-meaning gates remain. |
| SR-carried-08 | Other carried E4/E7 claims (BCFS Inc. 2003-04-02, PavCo 2008 amalgamation, BCFSA, ITA 2 January 2004, FPCC operations 1 April 1991, CLBC 1 July 2005, the modern B.C. Ferry Authority and Commissioner 1 April 2003, the services contract) | 12 | 12 | Several claims in this group were already held; source recovery must not duplicate them. |
| SR-carried-09 | D4 deputy ministers (root/deputy_minister_checkpoints.json), H1 MLAs (root/elected_candidates_*.json), H2 sessions (legislature/*.json), H5 education (education/*.json), D3's root/transportation_1978.json | 0 | 80 | These are review datasets, not a ready-to-import completed historical roster. |

### SR-health-09: Health service delivery areas (A9): sixteen by June 2002; Vancouver Island changes June 2003

Integration reference: `research/reviews/round-4-2026-10-21/integration/health.json` at `/not_applied/9` (subject line 2520).

**Existing reason:** HSDAs are areas, not bodies, and the atlas has no area layer. The Statistics Canada sources (R3H-064, R3H-065) have no URL in the handback. Keep for an area model; month precision only.

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-063` | [R3H-064](https://www150.statcan.gc.ca/n1/pub/82-221-x/2004002/4150352-eng.htm) | Health region changes table, BC row |
| `health/claims.json` — `R3HC-064` | [R3H-064](https://www150.statcan.gc.ca/n1/pub/82-221-x/2004002/4150352-eng.htm) | Health region changes table, BC row |
| `health/claims.json` — `R3HC-065` | [R3H-065](https://www150.statcan.gc.ca/n1/pub/82-221-x/01002/4061979-eng.htm) | Correspondence table |

**Gates that remain:**

- HSDAs are statistical/service geography, not corporate bodies; an area model is still needed.
- The recovered sources establish June 2002/June 2003 checkpoints at month precision; they do not supply the exact day or full rationale for the fifteenth-to-sixteenth area change.

### SR-health-10: Providence Health Care, Bella Coola General Hospital, R.W. Large Memorial Hospital "affiliated with" Vancouver Coastal Health (2005)

Integration reference: `research/reviews/round-4-2026-10-21/integration/health.json` at `/not_applied/10` (subject line 2529).

**Existing reason:** None is an atlas body, and "affiliated" is a relation type the diagram does not draw. The 2004/05 VCH statements (R3H-070) have no URL in the handback. Do not turn affiliation into amalgamation.

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-073` | [R3H-070](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2004-05/sup-e/vancouver-coastal-health-authority-fs-2004-05.pdf) | PDFp7 note1 |
| `health/claims.json` — `R3HC-074` | [R3H-070](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2004-05/sup-e/vancouver-coastal-health-authority-fs-2004-05.pdf) | PDFp7 note1 |
| `health/claims.json` — `R3HC-075` | [R3H-070](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2004-05/sup-e/vancouver-coastal-health-authority-fs-2004-05.pdf) | PDFp7 note1 |

**Gates that remain:**

- The affiliated hospitals are not present atlas bodies; any new identities require review.
- Affiliation is not amalgamation, legal ownership or ministerial accountability; use a typed affiliation edge.

### SR-health-11: Abbotsford (Regional) Hospital and Cancer Centre Inc.: incorporated 2 September 2003, owned by Partnerships BC; shares to Fraser Health (85%) and PHSA (15%) on 6 May 2008

Integration reference: `research/reviews/round-4-2026-10-21/integration/health.json` at `/not_applied/11` (subject line 2539).

**Existing reason:** A company the atlas does not hold, needing an "owned by" relation that is not drawn. Ready as a new body when ownership edges exist: incorporation is verified in PHSA 2004/05 note 5 (https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2004-05/sup-e/provincial-health-services-authority-fs-2004-05.pdf, PDF p. 12). The 2008 share transfer source (R3H-092, Fraser 2008/09) has no URL in the handback.

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-086` | [R3H-071](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2004-05/sup-e/provincial-health-services-authority-fs-2004-05.pdf) | PDFp12 note5 |
| `health/claims.json` — `R3HC-087` | [R3H-071](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2004-05/sup-e/provincial-health-services-authority-fs-2004-05.pdf) | PDFp12 note5 |
| `health/claims.json` — `R3HC-142` | [R3H-092](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2008-09/sup-e/fraser-health-authority-fs-2008-09.pdf) | Note2, first paragraph |
| `health/claims.json` — `R3HC-143` | [R3H-092](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2008-09/sup-e/fraser-health-authority-fs-2008-09.pdf) | Note2, first paragraph |

**Gates that remain:**

- The company requires a reviewed identity/node and dated ownership edges.
- Keep incorporation, ownership and the 2008 share transaction separate; the current integration already recovered the 2003 incorporation source.

### SR-health-12: Nisga'a Valley Health Board / Authority (A10)

Integration reference: `research/reviews/round-4-2026-10-21/integration/health.json` at `/not_applied/12` (subject line 2550).

**Existing reason:** Not an atlas body. It is a Nisga'a institution, and the model keeps First Nations governments as governments, so adding it is an editorial decision. Ready draft: registry S0019586 (https://orgbook.gov.bc.ca/api/v4/topic/2140035/credential-set, re-read): Nisga'a Valley Health Board registered 1984-10-16; renamed Nisga'a Valley Health Authority 2004-08-31. The Nisga'a history page (R3H-089: 25 April 1984 resolution, 21 March 1988 clinic opening, 11 May 2000 jurisdiction) has no URL in the handback. Its "formally created 1986" is not substituted for the registry date.

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-114` | [R3H-081](https://orgbook.gov.bc.ca/api/v4/topic/2140035/credential-set) | Credential 3105169 |
| `health/claims.json` — `R3HC-115` | [R3H-081](https://orgbook.gov.bc.ca/api/v4/topic/2140035/credential-set) | Credential 3105266 |
| `health/claims.json` — `R3HC-134` | [R3H-089](https://nisgaahealth.bc.ca/about/our-history/) | 1980s entry |
| `health/claims.json` — `R3HC-135` | [R3H-089](https://nisgaahealth.bc.ca/about/our-history/) | 1980s entry |
| `health/claims.json` — `R3HC-136` | [R3H-089](https://nisgaahealth.bc.ca/about/our-history/) | 2000 Treaty entry |

**Gates that remain:**

- Nisga’a institutions must not be placed beneath a provincial ministry; governance and model review remain.
- The institutional history is a historical account, not the requested original 2000 enactment/agreement. Its 1986 narrative must not replace the 1984 registry incorporation.

### SR-health-13: SSO Administration Society 2009-2010: operations from 1 April 2009, member and PHSA approvals (30 March, 12 April 2010), assets to PHSA/HSSBC 17 September 2010

Integration reference: `research/reviews/round-4-2026-10-21/integration/health.json` at `/not_applied/13` (subject line 2561).

**Existing reason:** Source R3H-082 (SSO 2010/11 statements) has no URL in the handback, and none was recovered (a Public Accounts guess returned 404). Ready once the URL is found; HSSBC is not an atlas body.

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-116` | [R3H-082](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2010-11/sup-e/shared-services-organization-fs-2010-11.pdf) | PDFp7 note1 |
| `health/claims.json` — `R3HC-117` | [R3H-082](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2010-11/sup-e/shared-services-organization-fs-2010-11.pdf) | PDFp7 note1 |
| `health/claims.json` — `R3HC-118` | [R3H-082](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2010-11/sup-e/shared-services-organization-fs-2010-11.pdf) | PDFp7 note1 |
| `health/claims.json` — `R3HC-119` | [R3H-082](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2010-11/sup-e/shared-services-organization-fs-2010-11.pdf) | PDFp7 note1 |
| `health/claims.json` — `R3HC-120` | [R3H-082](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2010-11/sup-e/shared-services-organization-fs-2010-11.pdf) | PDFp7 note1 |

**Gates that remain:**

- Review SSO Administration Society, PHSA and HSSBC as distinct identities and legal/program forms.
- Separate operations start, member approval, PHSA approval and executed transfer; these are not all incorporation dates.

### SR-health-14: Forensic Psychiatric Services Commission (B6): resources from the Ministry 1 April 1999; funded through PHSA 2002/03; board reconstituted by OIC 1424/1998 (19 November 1998)

Integration reference: `research/reviews/round-4-2026-10-21/integration/health.json` at `/not_applied/14` (subject line 2570).

**Existing reason:** Not an atlas body or sub-agency id. The FPSC 2002/03 statements (R3H-086) have no URL in the handback. OIC 1424/1998 was re-read (https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1424_1998, approved 19 November 1998): it rescinds and makes appointments to an existing commission, so it is not its creation. Add with the commission when the crowns module supplies its statute.

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-125` | [R3H-086](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2002-03/sup-e/forensic-psychiatric-services-commission-fs-2002-03.pdf) | PDFp7 note1 |
| `health/claims.json` — `R3HC-126` | [R3H-086](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2002-03/sup-e/forensic-psychiatric-services-commission-fs-2002-03.pdf) | PDFp7 note1 |
| `health/claims.json` — `R3HC-141` | [R3H-091](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1424_1998) | Operative paragraphs 1–5 |

**Gates that remain:**

- The Commission needs an admitted identity and its statutory creation/commencement evidence.
- The 1998 order reconstitutes appointments to an existing body; funding through PHSA is not ordinary ministry parentage.

### SR-health-15: Provincial Language Services (2003) and Perinatal Services BC (2009/10)

Integration reference: `research/reviews/round-4-2026-10-21/integration/health.json` at `/not_applied/15` (subject line 2578).

**Existing reason:** PLS has no atlas id, and its history page (R3H-087) has no URL in the handback. Perinatal Services BC's 2009/10 checkpoint (R3H-099) was handed to the branches module, which owns it (health coverage F1).

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-127` | [R3H-087](https://www.phsa.ca/our-services/programs-services/provincial-language-services) | History section |
| `health/claims.json` — `R3HC-152` | [R3H-099](https://www.bcbudget.gov.bc.ca/Annual_Reports/2009_2010/hs/hs.pdf) | Description of sixth health authority and agency list |

**Gates that remain:**

- Provincial Language Services lacks a current atlas ID; preserve the stated year precision.
- Perinatal’s 2009/10 observation was already assigned to the branch integrator and must be deduplicated.

### SR-health-16: Health Insurance BC administrative services from 1 April 2005 (C4)

Integration reference: `research/reviews/round-4-2026-10-21/integration/health.json` at `/not_applied/16` (subject line 2585).

**Existing reason:** Source R3H-100 has no URL in the handback. HIBC is a contract program name, not a body. When the URL is found, file it as a program event under sub-medical-services-plan and sub-bc-pharmacare.

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-153` | [R3H-100](https://www.bcbudget.gov.bc.ca/annual_reports/2004_2005/hs/appendix_a_-_report_on_performance.htm) | Passage beginning April1,2005 |

**Gates that remain:**

- Health Insurance BC is an administrative contract/program name, not a newly incorporated public body.
- The integration proposal itself identifies program events under MSP and PharmaCare as the appropriate route.

### SR-health-17: Health profession colleges (C5): HPA designations, six mergers 2018-2024, HPOA commencement 1 April 2026

Integration reference: `research/reviews/round-4-2026-10-21/integration/health.json` at `/not_applied/17` (subject line 2594).

**Existing reason:** No college is an atlas body or sub-agency, and the regulators connect through regulation, not service delivery, so they need a new layer (or new_bodies of kind agency). None of the 30 sources (R3H-088, R3H-096 to R3H-098, R3H-107 to R3H-127) has a URL in the handback. The designation dates are designation-regime events, not first foundings. Their deposit and effective days are kept apart in the claims (for example Dental Hygienists: deposited 16 December 1994, effective 1 March 1995). Ready for a regulators pass once the URLs are recovered.

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-128` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s7(1)–(2) |
| `health/claims.json` — `R3HC-129` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s8(1)–(2) |
| `health/claims.json` — `R3HC-130` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s9(1)–(2) |
| `health/claims.json` — `R3HC-131` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s10(1)–(2) |
| `health/claims.json` — `R3HC-132` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s11(1)–(2) |
| `health/claims.json` — `R3HC-133` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s12(1)–(2) |
| `health/claims.json` — `R3HC-148` | [R3H-096](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v68n12_126-2025) | Opening order and paragraph(a) |
| `health/claims.json` — `R3HC-149` | [R3H-097](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v69n04_19-2026) | Operative paragraph and subparagraphs(a)(i)–(iii) |
| `health/claims.json` — `R3HC-150` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit); [R3H-098](https://news.gov.bc.ca/releases/2024HLTH0092-001030) | Opening paragraphs/backgrounder |
| `health/claims.json` — `R3HC-151` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit); [R3H-098](https://news.gov.bc.ca/releases/2024HLTH0092-001030) | Opening paragraphs/backgrounder |
| `health/claims.json` — `R3HC-165` | [R3H-107](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/362581293) | ss15(1)–(4),16(1) |
| `health/claims.json` — `R3HC-166` | [R3H-107](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/362581293) | s17(2)–(3) |
| `health/claims.json` — `R3HC-167` | [R3H-108](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/486_94_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-168` | [R3H-109](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/509_95_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-169` | [R3H-110](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/68_2000_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-170` | [R3H-111](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/296_2002_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-171` | [R3H-112](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/71_96_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-172` | [R3H-113](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/484_94_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-173` | [R3H-114](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/103_95_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-174` | [R3H-115](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/449_99_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-175` | [R3H-116](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/233_2005_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-176` | [R3H-117](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/432_98_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-177` | [R3H-118](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/487_94_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-178` | [R3H-119](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/485_94_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-179` | [R3H-120](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/442_99_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-180` | [R3H-121](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/115_99_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-181` | [R3H-122](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/385_2000_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-182` | [R3H-123](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/413_2008_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-183` | [R3H-124](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v61n09_093-2018) | Opening effective clause; Schedules1–3 college-name sections |
| `health/claims.json` — `R3HC-184` | [R3H-125](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v63n12_167-2020) | Opening effective clause; Schedules1–4 college-name sections |
| `health/claims.json` — `R3HC-185` | [R3H-126](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v65n14_172-2022) | Opening effective clause; Schedules1–4 college-name sections |
| `health/claims.json` — `R3HC-186` | [R3H-127](https://cchpbc.ca/for-professionals/traditional-chinese-medicine-and-acupuncturists/) | History section |

**Gates that remain:**

- A regulator layer or reviewed agency identities are still required; regulation is not service delivery.
- Designation-regime dates are not necessarily first corporate foundings; preserve deposit and express effective dates separately.
- Current/revised HPOA text and commencement provisions are dated checkpoints, not permission to backdate current governance.

### SR-health-19: FNHA governance (A11): the 2011 Framework Agreement, the 2007 plan, the First Nations Health Council (2007) and the FNHDA secretariat model

Integration reference: `research/reviews/round-4-2026-10-21/integration/health.json` at `/not_applied/19` (subject line 2616).

**Existing reason:** No URL in the handback for these claims. The registry events for FNHA and FNHDA are applied (the coordinator admitted the FNHA diagram id, which existing events already use).

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-137` | [R3H-090](https://www.canada.ca/content/dam/hc-sc/migration/hc-sc/fniah-spnia/alt_formats/pdf/pubs/services/tripartite/framework-accord-cadre-eng.pdf) | Cover; s15 |
| `health/claims.json` — `R3HC-138` | [R3H-090](https://www.canada.ca/content/dam/hc-sc/migration/hc-sc/fniah-spnia/alt_formats/pdf/pubs/services/tripartite/framework-accord-cadre-eng.pdf) | ss1.1(11),2.4,4.4 |
| `health/claims.json` — `R3HC-139` | [R3H-090](https://www.canada.ca/content/dam/hc-sc/migration/hc-sc/fniah-spnia/alt_formats/pdf/pubs/services/tripartite/framework-accord-cadre-eng.pdf) | s4.6(1),(3) |
| `health/claims.json` — `R3HC-140` | [R3H-090](https://www.canada.ca/content/dam/hc-sc/migration/hc-sc/fniah-spnia/alt_formats/pdf/pubs/services/tripartite/framework-accord-cadre-eng.pdf) | s4.2(1); Schedule4 |
| `health/claims.json` — `R3HC-144` | [R3H-093](https://www.canada.ca/content/dam/hc-sc/migration/hc-sc/fniah-spnia/alt_formats/pdf/pubs/services/tripartite/vision-eng.pdf) | How do we get there? First Nations Health Council paragraph |
| `health/claims.json` — `R3HC-145` | [R3H-093](https://www.canada.ca/content/dam/hc-sc/migration/hc-sc/fniah-spnia/alt_formats/pdf/pubs/services/tripartite/vision-eng.pdf) | How do we get there? Provincial Advisory Committee paragraph |
| `health/claims.json` — `R3HC-146` | [R3H-094](https://fnhda.ca/wp-content/uploads/FNHDA-strategic-Plan-Feb-2012-with-sticker.pdf) | Current FNHDA Secretariat model, points1–6 |
| `health/claims.json` — `R3HC-147` | [R3H-095](https://www.canada.ca/en/news/archive/2007/06/canada-new-government-signs-first-nations-health-agreement-b-c-first-nations-leadership-council.html) | Opening paragraphs |

**Gates that remain:**

- Keep First Nations governance and accountability distinct from provincial ministry hierarchy.
- The 2011 agreement distinguishes advice from direction; FNHC/FNHDA do not direct FNHA.
- The recovered 2007 official announcement/vision documents are not by themselves the requested signed original 2007 Plan; original-instrument gaps remain where explicitly requested.

### SR-carried-01: Provincial Elections Act 1939 in force 1 April 1940 (RSBC 1936 c. 84 repealed); 1872 voters Act reserved-bill assent proclaimed 26 October 1872 (G5)

Integration reference: `research/reviews/round-4-2026-10-21/integration/carried.json` at `/not_applied/1` (subject line 917).

**Existing reason:** Statutes, not bodies: no atlas subject holds them, and the franchise needs its own data file (WANTED G5). The sources (R3H-174, R3H-175: Gazette scans archive.org governmentgazett80nogove_v1h4 and governmentgazettv11ngove_c6g4) have no URL in the handback; the identifiers would let a franchise file cite them.

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/elections_followup/claims.json` — `R3HC-238` | [R3H-174](https://archive.org/download/governmentgazett80nogove_v1h4/governmentgazett80nogove_v1h4.pdf) | Printed p.472, right column, notice1081-mh28; PDF p.2 |
| `health/elections_followup/claims.json` — `R3HC-239` | [R3H-174](https://archive.org/download/governmentgazett80nogove_v1h4/governmentgazett80nogove_v1h4.pdf) | Printed p.472, right column, notice1081-mh28; PDF p.2 |
| `health/elections_followup/claims.json` — `R3HC-240` | [R3H-175](https://archive.org/download/governmentgazettv11ngove_c6g4/governmentgazettv11ngove_c6g4.pdf) | Printed p.2, upper left column; PDF p.2 |
| `health/elections_followup/claims.json` — `R3HC-241` | [R3H-175](https://archive.org/download/governmentgazettv11ngove_c6g4/governmentgazettv11ngove_c6g4.pdf) | Printed p.2, upper left column; PDF p.2 |

**Gates that remain:**

- The franchise needs a dated data model and legal-event subjects; these are not new administrative bodies.
- Keep proclamation date, publication date and operative commencement distinct.

### SR-carried-05: regulator_designation_crosswalk.json (16 colleges), regulator_merger_crosswalk.json (6 mergers)

Integration reference: `research/reviews/round-4-2026-10-21/integration/carried.json` at `/not_applied/5` (subject line 951).

**Existing reason:** Same as the health module's not_applied for the colleges: no college is an atlas body, the regulators need their own layer, the designation dates are regime events rather than foundings, and the sources (R3H-088, R3H-107 to R3H-127) have no URL in the handback.

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `health/claims.json` — `R3HC-128` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s7(1)–(2) |
| `health/claims.json` — `R3HC-129` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s8(1)–(2) |
| `health/claims.json` — `R3HC-130` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s9(1)–(2) |
| `health/claims.json` — `R3HC-131` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s10(1)–(2) |
| `health/claims.json` — `R3HC-132` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s11(1)–(2) |
| `health/claims.json` — `R3HC-133` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit) | Former regulation s12(1)–(2) |
| `health/claims.json` — `R3HC-148` | [R3H-096](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v68n12_126-2025) | Opening order and paragraph(a) |
| `health/claims.json` — `R3HC-149` | [R3H-097](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v69n04_19-2026) | Operative paragraph and subparagraphs(a)(i)–(iii) |
| `health/claims.json` — `R3HC-150` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit); [R3H-098](https://news.gov.bc.ca/releases/2024HLTH0092-001030) | Opening paragraphs/backgrounder |
| `health/claims.json` — `R3HC-151` | [R3H-088](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/270_2008_pit); [R3H-098](https://news.gov.bc.ca/releases/2024HLTH0092-001030) | Opening paragraphs/backgrounder |
| `health/claims.json` — `R3HC-165` | [R3H-107](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/362581293) | ss15(1)–(4),16(1) |
| `health/claims.json` — `R3HC-166` | [R3H-107](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/362581293) | s17(2)–(3) |
| `health/claims.json` — `R3HC-167` | [R3H-108](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/486_94_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-168` | [R3H-109](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/509_95_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-169` | [R3H-110](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/68_2000_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-170` | [R3H-111](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/296_2002_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-171` | [R3H-112](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/71_96_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-172` | [R3H-113](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/484_94_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-173` | [R3H-114](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/103_95_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-174` | [R3H-115](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/449_99_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-175` | [R3H-116](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/233_2005_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-176` | [R3H-117](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/432_98_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-177` | [R3H-118](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/487_94_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-178` | [R3H-119](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/485_94_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-179` | [R3H-120](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/442_99_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-180` | [R3H-121](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/115_99_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-181` | [R3H-122](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/385_2000_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-182` | [R3H-123](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/413_2008_pit) | Header; designation/college-name section |
| `health/claims.json` — `R3HC-183` | [R3H-124](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v61n09_093-2018) | Opening effective clause; Schedules1–3 college-name sections |
| `health/claims.json` — `R3HC-184` | [R3H-125](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v63n12_167-2020) | Opening effective clause; Schedules1–4 college-name sections |
| `health/claims.json` — `R3HC-185` | [R3H-126](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v65n14_172-2022) | Opening effective clause; Schedules1–4 college-name sections |
| `health/claims.json` — `R3HC-186` | [R3H-127](https://cchpbc.ca/for-professionals/traditional-chinese-medicine-and-acupuncturists/) | History section |

**Gates that remain:**

- Duplicate of the health regulator hold; same identity, regulator-layer and date-meaning gates remain.

### SR-carried-08: Other carried E4/E7 claims (BCFS Inc. 2003-04-02, PavCo 2008 amalgamation, BCFSA, ITA 2 January 2004, FPCC operations 1 April 1991, CLBC 1 July 2005, the modern B.C. Ferry Authority and Commissioner 1 April 2003, the services contract)

Integration reference: `research/reviews/round-4-2026-10-21/integration/carried.json` at `/not_applied/8` (subject line 977).

**Existing reason:** Either already in the atlas (BCFS Inc. 2003-04-02, PavCo 2008-04-01, BCFSA 2019-06-04/11-01, CLBC 2005-07-01 are held as bodies or events) or without a URL in the handback (R3E-013, R3E-039, R3E-103, R3E-131, R3E-146/147 have no source register in the package). The modern Authority and the Commissioner's office have no atlas node; the Authority is outside the diagram's scope like BC Ferry Services Inc. (OMIT).

**Recovered mapping:**

| Prior component / claim | Source and literal URL | Locator |
|---|---|---|
| `crowns/claims.json` — `R3E-C047` | [R3E-083](https://orgbook.gov.bc.ca/api/v4/topic/687729/credential-set); [R3E-125](https://orgbook.gov.bc.ca/assets/en-DOUkjW9H.js) | BC Corporate Registry credential 1032082; effective_date; reason_description=Event:CONVICORP; entity_status=ACT |
| `crowns/claims.json` — `R3E-C052` | [R3E-016](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/bc-pavilion-corporation-fs-2025-26.pdf) | 2025/26 financial statements PDF p11, Note 1 |
| `crowns/claims.json` — `R3E-C054` | [R3E-029](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/bc-financial-services-authority-fs-2025-26.pdf) | 2025/26 financial statements PDF p10, Note 1 |
| `crowns/claims.json` — `R3E-C055` | [R3E-029](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/bc-financial-services-authority-fs-2025-26.pdf) | PDF p10, Note 1 |
| `crowns/claims.json` — `R3E-C056` | [R3E-029](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/bc-financial-services-authority-fs-2025-26.pdf) | PDF p10, Note 1 |
| `crowns/claims.json` — `R3E-C057` | [R3E-013](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/skilledtradesbc-fs-2025-26.pdf) | 2025/26 financial statements PDF p9, Note 1; current Skilled Trades BC Act s2 expressly continues ITA |
| `crowns/claims.json` — `R3E-C058` | [R3E-039](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/sup-e/first-peoples-heritage-fs-2025-26.pdf) | 2025/26 financial statements PDF p10 / printed p8, Note 1 |
| `crowns/claims.json` — `R3E-C069` | [R3E-093](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/00_04060_01); [R3E-170](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v48n14_231-2005) | BC Reg 231/2005 / OIC 469: paragraph (a) brings ss1–32 and other provisions into force; corporate establishment is s2. |
| `crowns/claims.json` — `R3E-C070` | [R3E-103](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/00_03014_01) | Coastal Ferry Act, SBC 2003 c14, ss2–3 and express commencement s89. |
| `crowns/claims.json` — `R3E-C071` | [R3E-103](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/00_03014_01) | Coastal Ferry Act ss35,38,89. |
| `crowns/claims.json` — `R3E-C072` | [R3E-131](https://www.bcferryauthority.com/wp-content/uploads/2021/04/BCFA-Annual-Report-2004-05.pdf) | BC Ferry Authority/BC Ferries 2004/05 annual report, PDF pp56–58 (company printed pp54–56), Notes8(a)–(b),14; Authority PDF p73, Note4. |
| `crowns/claims.json` — `R3E-C073` | [R3E-146](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/passenger/coastal-ferries/coastal_ferry_services_contract.pdf); [R3E-147](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/passenger/coastal-ferries/unofficial-consolidated-contract-effective-2024-04-01.pdf) | Original agreement effective-date recital and s3.01; unofficial consolidation effective 1 April 2024, s3.01. |

**Gates that remain:**

- Several claims in this group were already held; source recovery must not duplicate them.
- The modern Ferry Authority and Commissioner require scope/identity decisions; authority, operator and regulator are distinct.
- The first Commissioner appointment, executed memorandum/share registers and some corporate transaction originals remain separate evidence requests.
- Later financial-statement recitals and current-law observations need their stated dates and evidence class preserved.

### SR-carried-09: D4 deputy ministers (root/deputy_minister_checkpoints.json), H1 MLAs (root/elected_candidates_*.json), H2 sessions (legislature/*.json), H5 education (education/*.json), D3's root/transportation_1978.json

Integration reference: `research/reviews/round-4-2026-10-21/integration/carried.json` at `/not_applied/9` (subject line 982).

**Existing reason:** The files coverage-59-items.json cites are Round 3 files not repackaged in Round 4 (README-round4: 'Earlier full Round 3 source archives are not repackaged'); no claim or source with a URL is in the package. D3 was re-established from the BC Laws originals (OICs 3018 and 3019/1978) instead.

**Recovered mapping:**

- `root/deputy_minister_checkpoints.json`
- `root/transportation_1978.json`
- `root/elected_candidates_1871_1986_review.json`
- `root/elected_candidates_1987_2013_review.json`
- `root/elected_candidates_2017_2020.json`
- `root/by_elections_2013_2023.json`
- `legislature/sessions_combined_review.json`
- `legislature/later_sessions_review.json`
- `legislature/committee_source_map.json`
- `education/claims.json`
- `education/typed_relationships.json`
- `education/school_mergers_1996.json`
- `education/school_boundary_orders_1996.json`

The component inventory and JSON companion map all source IDs and record pointers for these datasets. The principal public-source links are listed in the dataset section below.

**Gates that remain:**

- These are review datasets, not a ready-to-import completed historical roster.
- Elections need person/riding/tenure reconciliation; session endpoints need event-type verification; school districts are local bodies.
- Deputy-minister appointments are checkpoints with incomplete ends; D3 was independently integrated and must not be duplicated.
- The Reg. 14/88 Gazette deposit and executed OLA–TRU transfer agreement remain genuine document gaps.

## Previously supplied material that WANTED understates or reopens

These are coverage corrections, not instructions to mark every item complete. The JSON companion retains the consolidated package’s own remaining-record lists.

| WANTED | Material already supplied | What still needs review |
|---|---|---|
| C1 / D1 | 657 operative clauses from 17 main ministry reorganization orders, 1996–2024; requested health changes are included. | Map legal entities/programs/enactments, verify flagged OCR and italicized Act titles, close historical intervals. Earlier and amending schedules are not complete. |
| D4 | 18 appointment checkpoints (16 deputy and 2 associate appointments) plus 3 rescissions on 5 November 1991. | Complete officeholder identity and tenure ends; handwritten annotations are not ending instruments. |
| E1 / E2 / E5 | 9 bounded responsibility records and 126 typed Crown relations, including Pension Corporation, BCI and LTSA legal distinctions. | Do not turn statute administration, ownership, funding or nominee rights into ordinary ministry parentage. E5 commencement and original agreement gaps remain. |
| E11 | R3E-C048 settles Forest Renewal BC dissolution on 27 June 2002, with original Act, order and Gazette regulation. | Other Rail/Wharves identities and conveyance documents remain incomplete; do not merge assent, order approval and commencement dates. |
| F1 / F2 | The earlier importable batch has 144 touched records; 48 structural-parent observations and 42 separately typed relationships are preserved. | Parent simulation measured 24 undated of 251 after that batch (10 gone, 14 not gone). This differs from the Round 4 residual cohort; no complete historical-parent chronology is claimed. |
| F4 | Original 1905, 1961 and 2002 COS legislation; the first warden report; 1957 department Act; 1965 Park Act. | The 1980 separation directive, Parks Branch implementing instrument, wildfire rename order and exact Surveyor General splits remain open. |
| F5 | The 5 July 2018 release expressly bridges LCLB to LCRB; R3T-E001 continues ITAB as Skilled Trades BC Appeal Board on 1 December 2022. | LCLB’s exact rename day remains unknown; other disappeared branches and core-review tribunal lifecycles remain incomplete. |
| G2 | 473-ID scrutiny crosswalk; 201 current FOIPPA entries and 221 changes; 614 named Ombudsperson observations; 16 remedy families. | Match legal identities, distinguish class from named coverage, derive first coverage from historical law, and distinguish audit plans from completed audits. |
| G3 / G4 | 35 tribunal/office appointment and mandate-population observations, plus Crown and branch/program evidence. | Current provisions are dated observations, not historical intervals; service recipients, regulated persons and electors are different sets. |
| G5 | 32 franchise events plus the original 1872/1940 Gazette findings. | Preserve the Round 4 supersession of R3G-F027 by R4RC-106; colonial intervals and litigation versus statutory repeal distinctions remain. |
| G7 | Four effective treaty agreements covering eight Nations, 16 partner edges and five pending/non-effective situations, with Westbank and shíshálh distinguished. | These are governments in their own right. Effective treaty dates are not Nation creation dates; the inventory is not exhaustive. |
| H1 | 2,380 retained candidate/election-event rows in the deduplicated review union through 2023. | They are not 2,380 accepted MLA tenures. Reconcile identities, overturned returns, election versus caucus party, and remaining review flags. |
| H2 | 172 sessions across 42 Parliaments, 42 dissolution dates; 15 later sessions checked in original Journals; committee source map. | 140 older unlabelled endpoints still need Journal verification before being called prorogations; committee membership/terms remain incomplete. |
| H5 | 37 claims, 18 relations, all 15 final 1996 merger orders, four boundary orders and the OLI–OLA–TRU/Knowledge Network distinction. | School districts are local bodies. Reg. 14/88 Gazette deposit and the executed 2005 OLA–TRU transfer agreement remain missing. |

### Exact source mappings for four concrete regressions

**REOPEN-E11-FOREST** — Forest Renewal BC statutory end was resolved in the earlier claim but is again listed as 14 versus 27 June 2002.

- `crowns/claims.json` / `R3E-C048`: [R3E-001](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1944924325); [R3E-002](https://www.bclaws.gov.bc.ca/civix/document/id/bcgaz2/bcgaz2/v45n12_158-2002); [R3E-128](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0517_2002). Locator: Budget Measures Implementation Act, 2002 SBC c7: s8 repeals Forest Renewal Act; s28 effects dissolution and vesting. OIC 517 approved 26 June; Reg 158 deposited 27 June.

- Remaining: Preserve assent (28 March), order approval (26 June), and deposit/commencement/dissolution (27 June 2002) separately. Other E11 corporate histories remain incomplete.

**REOPEN-F4-STATUTES** — The original 1905, 1961 and 2002 COS instruments and 1965 Park Act were already supplied; they should not be requested again as wholly unfound.

- `branches/claims.json` / `R3F-C-0238`: [R3F-EXT-030](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/318868896). Locator: Game Protection Amendment Act 1905 c25 s17 adding ss30–34; PDFpp4–5
- `branches/claims.json` / `R3F-C-0239`: [R3F-EXT-033](https://www.llbc.leg.bc.ca/public/pubdocs/bcdocs2016_2/346798/1st_report_1905.pdf). Locator: First report, PDFp5 / printedD5, opening paragraph
- `branches/claims.json` / `R3F-C-0240`: [R3F-EXT-031](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1982484672). Locator: Game Act Amendment Act 1961 c21, title/assent and s2; PDFp1
- `branches/claims.json` / `R3F-C-0242`: [R3F-EXT-043](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1203260726); [R3F-EXT-048](https://www.bclaws.gov.bc.ca/civix/document/id/rs/rs/96238_01). Locator: Environment Management Amendment Act 2002 c27 s2 adding s8.1; PDFp1
- `branches/claims.json` / `R3F-C-0243`: [R3F-EXT-044](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1525674329). Locator: Department of Recreation and Conservation Act 1957 c53 ss3,5–8; PDFpp1–2
- `branches/claims.json` / `R3F-C-0245`: [R3F-EXT-045](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1960750738). Locator: Park Act 1965 c31, title, s33(1)–(2); PDFpp1,9

- Remaining: The 1980 administrative separation directive, 1957 Parks Branch implementing instrument, wildfire rename order and exact Surveyor General intermediate splits remain open.
- Remaining: Assent, statutory enforcement-program establishment and an older administrative branch origin have different meanings.

**REOPEN-F5-LCLB** — The full branch claims include an express identity bridge from LCLB to LCRB, contradicting the claim that no such bridge was supplied.

- `branches/claims.json` / `R3F-C-0204`: [R3F-EXT-058](https://news.gov.bc.ca/releases/2018AG0053-001343). Locator: Named section described in note
- `branches/claims.json` / `R3F-C-0265`: [R3F-EXT-058](https://news.gov.bc.ca/releases/2018AG0053-001343). Locator: Release of 5 July 2018, opening paragraph and Quick Facts

- Remaining: Continuity and rename-by 5 July 2018 are supported; the exact rename day remains unproved.
- Remaining: Do not infer ministry parentage from the release issuer alone.

**REOPEN-F5-ITAB** — The earlier tribunal supplement already gives the Industry Training Appeal Board continuation under the Skilled Trades BC Appeal Board name.

- `tribunals/historical-supplement.json` / `R3T-E001`: [R3T-016](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/22004); [R3T-038](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0650_2022). Locator: See evidence fields in JSON

- Remaining: Review against the held identity and avoid duplicate bodies; the continuation preserves appointments.
- Remaining: Other core-review tribunal endings remain incomplete.


## Components absent as complete payloads

Canonical JSON hashes were compared with every JSON file under repository `research/`. The list contains 19 root components, five tribunal components, four education components, three legislature components and the branch-claims component. It does not mean all individual assertions are new or safe to import.

| Component | Shape / record counts | Referenced catalogue sources |
|---|---|---|
| `education/claims.json` | {"records": 37} | 35 |
| `education/typed_relationships.json` | {"records": 18} | 8 |
| `education/school_mergers_1996.json` | {"records": 15} | 15 |
| `education/school_boundary_orders_1996.json` | {"records": 4} | 4 |
| `branches/claims.json` | {"records": 279} | 113 |
| `tribunals/claims.json` | {"records": 71} | 38 |
| `tribunals/current-observations.json` | {"records": 35} | 38 |
| `tribunals/historical-supplement.json` | {"records": 3} | 4 |
| `tribunals/ombudsperson-class-review.json` | {"methodology": 10, "records": 35} | 45 |
| `tribunals/ombudsperson-authority-observations.json` | {"temporal_cautions": 6, "observations": 614, "aggregate_rows": 32, "non_data_lines_reviewed": 19} | 2 |
| `root/ministry_transfer_clauses.json` | {"critical_corrections": 3, "orders": 17, "clauses": 657, "extraction_notes": 4} | 17 |
| `root/transfer_parse_summary.json` | {"order_sections": 17} | 17 |
| `root/treasury_alias_and_holders.json` | {"portfolio_aliases": 2, "tenure_rows": 16, "dated_alias_observations": 18, "limits": 4} | 19 |
| `root/transportation_1978.json` | {"source_ids": 4, "locators": 4} | 4 |
| `root/deputy_minister_checkpoints.json` | {"appointments": 18, "rescissions": 3} | 3 |
| `root/model_recommendations.json` | {"wanted_items": 4, "source_ids": 7, "views": 4, "entities_to_keep_distinct": 12, "edge_types": 20, "edge_required_fields": 13, "safeguards": 11} | 7 |
| `root/complete_inventory.json` | {"records": 484} | 0 |
| `root/scrutiny_body_crosswalk.json` | {"rows": 473, "additional_subjects": 2} | 73 |
| `root/ombudsperson_coverage.json` | {"current_schedule": 41, "history_events": 17, "specific_exceptions": 3, "general_limits": 2} | 10 |
| `root/foippa_designations.json` | {"current_schedule_2": 201, "schedule_history_events": 221, "limitations": 5} | 2 |
| `root/auditor_general_coverage.json` | {"plans": 2, "interpretation": 5} | 2 |
| `root/remedy_routes.json` | {"routes": 16} | 21 |
| `root/service_populations.json` | {"verified_service_or_remedy_populations": 16} | 21 |
| `root/franchise_chronology.json` | {"events": 32, "critical_model_rules": 6, "remaining": 4} | 33 |
| `root/first_nations_governments.json` | {"in_force_agreements": 4, "ratification_or_uncommenced_agreements": 5, "other_self_government_frameworks": 2, "typed_relationships": 16, "model_rules": 5} | 17 |
| `root/elected_candidates_1871_1986_review.json` | {"cautions": 6, "records": 1701, "service_notes_to_review": 130, "unassigned_lines_to_review": 3, "official_seat_total_comparison": 34, "errata_application_summary": 2} | 2 |
| `root/elected_candidates_1987_2013_review.json` | {"rows": 499, "summary": 2, "official_seat_and_party_comparison": 6, "candidate_notes": 43, "earlier_2001_election_affiliation_cross_references": 3, "potential_duplicate_event_rows_after_corrections": 0, "return_crosscheck_unmatched": 0, "rules": 8, "resolved_printed_anomalies": 6, "remaining_review": 4} | 2 |
| `root/elected_candidates_2017_2020.json` | {"validation": 2, "elected_rows": 174, "all_candidate_rows": 701, "not_included": 2} | 2 |
| `root/by_elections_2013_2023.json` | {"rows": 9} | 10 |
| `legislature/sessions_combined_review.json` | {"sources": 23, "supersession_rules": 3, "parliaments": 42, "sessions": 172, "superseded_session_observations": 4, "limits": 6} | 23 |
| `legislature/later_sessions_review.json` | {"sessions": 15, "dissolutions": 3, "limits": 3} | 18 |
| `legislature/committee_source_map.json` | {"election_committee_entries": 22, "cumulative_index_leads": 13, "adjacent_commission_leads": 15, "notes": 5} | 4 |

### Principal dataset sources

The JSON companion contains the complete source-to-component map, including the 657 transfer-clause identifiers. These links give direct entry points for the omitted datasets.

| Dataset | Source | Public URL |
|---|---|---|
| Ministry transfer orders | `R3R-015` — OIC 565/2001 government organization candidate | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0565_2001](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0565_2001) |
| Ministry transfer orders | `R3R-016` — OIC 450/2005 government organization candidate | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0450_2005](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0450_2005) |
| Ministry transfer orders | `R3R-017` — OIC 430/2008 government organization candidate | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0430_2008](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0430_2008) |
| Ministry transfer orders | `R3R-018` — OIC 281/2009 government organization candidate | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0281_2009](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0281_2009) |
| Ministry transfer orders | `R3R-019` — OIC 62/2011 government organization candidate | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0062_2011](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0062_2011) |
| Ministry transfer orders | `R3R-021` — OIC 594/2012 government organization candidate | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0594_2012](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0594_2012) |
| Ministry transfer orders | `R3R-022` — OIC 233/2013 government organization candidate | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0233_2013](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0233_2013) |
| Ministry transfer orders | `R3R-023` — OIC 213/2017 government organization candidate | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0213_2017](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0213_2017) |
| Ministry transfer orders | `R3R-025` — OIC 658/2022 government organization candidate | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0658_2022](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0658_2022) |
| Ministry transfer orders | `R3R-026` — OIC 596/2024 government organization candidate | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0596_2024](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0596_2024) |
| Ministry transfer orders | `R3R-032` — OIC602/2020 replacementgovernmentstructureorder | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0602_2020](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0602_2020) |
| Ministry transfer orders | `R3R-231` — OIC 241/2000: February 2000 reorganization | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0241_2000](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0241_2000) |
| Ministry transfer orders | `R3R-233` — OIC 897/1999: July 1999 reorganization | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0897_1999](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0897_1999) |
| Ministry transfer orders | `R3R-235` — OIC 652/2010: October 2010 reorganization | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0652_2010](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0652_2010) |
| Ministry transfer orders | `R3R-236` — OIC 37/2004: Health Planning and economic development reorganization | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0037_2004](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0037_2004) |
| Ministry transfer orders | `R3R-238` — OIC 177/1998: February 1998 reorganization | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0177_1998](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0177_1998) |
| Ministry transfer orders | `R3R-239` — OIC 1069/1996: Children and Families creation September 1996 | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1069_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1069_1996) |
| Deputy appointments | `R3R-063` — OIC 1384_1991 candidate reorganization instrument | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1384_1991](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1384_1991) |
| Deputy appointments | `R3R-064` — OIC 1385_1991 candidate reorganization instrument | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1385_1991](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1385_1991) |
| Deputy appointments | `R3R-237` — OIC 651/2010: Ministers of state and parliamentary secretaries October 2010 | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0651_2010](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0651_2010) |
| Election histories and corrections | `R3R-007` — Electoral History of British Columbia1871-1986 | [https://elections.bc.ca/docs/rpt/1871-1986_ElectoralHistoryofBC.pdf](https://elections.bc.ca/docs/rpt/1871-1986_ElectoralHistoryofBC.pdf) |
| Election histories and corrections | `R3R-028` — Electoral History1871-1986 Errata updated21Aug2025 | [https://elections.bc.ca/docs/rpt/ElectoralHistoryofBritishColumbia1871-1986Errata.pdf](https://elections.bc.ca/docs/rpt/ElectoralHistoryofBritishColumbia1871-1986Errata.pdf) |
| Election histories and corrections | `R3R-029` — Electoral History1987-2001 | [https://elections.bc.ca/docs/rpt/1987-2001-ElectionHistory.pdf](https://elections.bc.ca/docs/rpt/1987-2001-ElectionHistory.pdf) |
| Election histories and corrections | `R3R-030` — Electoral History2002-2013 | [https://elections.bc.ca/docs/rpt/2002-2013-ElectionHistory.pdf](https://elections.bc.ca/docs/rpt/2002-2013-ElectionHistory.pdf) |
| Election histories and corrections | `R3R-185` — Elections BC 2020 Statement of Votes | [https://elections.bc.ca/docs/rpt/statement-of-votes-2020-provincial-general-election.pdf](https://elections.bc.ca/docs/rpt/statement-of-votes-2020-provincial-general-election.pdf) |
| Election histories and corrections | `R3R-194` — 2017 results by candidate | [https://elections.bc.ca/docs/rpt/2017-election-report/pdf/results-by-candidate.pdf](https://elections.bc.ca/docs/rpt/2017-election-report/pdf/results-by-candidate.pdf) |
| Election histories and corrections | `R3R-255` — Elections BC2016by-election report | [https://elections.bc.ca/docs/rpt/2016-CEO-CQB-VMP-By-election-report.pdf](https://elections.bc.ca/docs/rpt/2016-CEO-CQB-VMP-By-election-report.pdf) |
| Election histories and corrections | `R3R-276` — Final report on2022Vancouver-Quilchena andSurreySouth by-elections | [https://elections.bc.ca/docs/rpt/2022-vancouver-quilchena-surrey-south-by-elections-report.pdf](https://elections.bc.ca/docs/rpt/2022-vancouver-quilchena-surrey-south-by-elections-report.pdf) |
| Original Journals and session review | `R3R-007` — Electoral History of British Columbia1871-1986 | [https://elections.bc.ca/docs/rpt/1871-1986_ElectoralHistoryofBC.pdf](https://elections.bc.ca/docs/rpt/1871-1986_ElectoralHistoryofBC.pdf) |
| Original Journals and session review | `R3R-029` — Electoral History1987-2001 | [https://elections.bc.ca/docs/rpt/1987-2001-ElectionHistory.pdf](https://elections.bc.ca/docs/rpt/1987-2001-ElectionHistory.pdf) |
| Original Journals and session review | `R3R-030` — Electoral History2002-2013 | [https://elections.bc.ca/docs/rpt/2002-2013-ElectionHistory.pdf](https://elections.bc.ca/docs/rpt/2002-2013-ElectionHistory.pdf) |
| Original Journals and session review | `R3R-273` — Journals1872–1971 cumulative index: Church Reserve to Computers | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/2139268911](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/2139268911) |
| Original Journals and session review | `R3R-274` — Journals1872–1971 cumulative index: Legislation to Lyttle | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/773679538](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/773679538) |
| Original Journals and session review | `R3H-178` — Journals, Legislative Assembly of BC 2014, Volume CLII: Feb 11, 2014 to Oct 6, 2014 [pp 1 to 106] | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/205141735](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/205141735) |
| Original Journals and session review | `R3H-179` — Journals, Legislative Assembly of BC 2014 to 2015, Volume CLIII: October 6, 2014 to February 10, 2015 [pp. 1 to 47] | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/04_october%206%2C%202014%20to%20february%2010%2C%202015%20%5Bpp.%201%20to%20%2047%5D](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/04_october%206%2C%202014%20to%20february%2010%2C%202015%20%5Bpp.%201%20to%20%2047%5D) |
| Original Journals and session review | `R3H-180` — Journals, Legislative Assembly of BC 2015 to 2016, Volume CLIV: February 10, 2015 to February 9, 2016[pp. 1 to 155] | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/7759](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/7759) |
| Original Journals and session review | `R3H-181` — Journals, Legislative Assembly of BC 2016 to 2017, Volume CLV: February 9, 2016 to February 14, 2017 [pp 1 to 109] | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/journals_clv](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/journals_clv) |
| Original Journals and session review | `R3H-182` — Journals, Legislative Assembly of BC 2017, Volume CLVI: February 14, 2017 to March 16, 2017 [pp 1 to 42] | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/journals_clvi](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/journals_clvi) |
| Original Journals and session review | `R3H-183` — Journals, Legislative Assembly of BC 2017, Volume CLVII: June 22, 2017 to September 8, 2017 [pp 1 to 27] | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201%20to%2027_clvii](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201%20to%2027_clvii) |
| Original Journals and session review | `R3H-184` — Journals, Legislative Assembly of BC 2017, Volume CLVIII: September 8, 2017 to February 13, 2018 | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-88_clviii](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-88_clviii) |
| Original Journals and session review | `R3H-185` — Journals, Legislative Assembly of BC 2018, Volume CLIX: February 13, 2018 to February 12, 2019 | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-172_clix](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-172_clix) |
| Original Journals and session review | `R3H-186` — Journals, Legislative Assembly of BC 2019, Volume CLX: February 12, 2019 to February 11, 2020 | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-165_clx](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-165_clx) |
| Original Journals and session review | `R3H-187` — Journals, Legislative Assembly of BC 2020, Volume CLXI: February 11, 2020 - August 14, 2020 | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-97_clxi](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-97_clxi) |
| Original Journals and session review | `R3H-188` — Journals, Legislative Assembly of BC 2020 to 2021, Volume CLXII: December 7, 2020 - April 12, 2021 | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-60_clxii](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-60_clxii) |
| Original Journals and session review | `R3H-189` — Journals, Legislative Assembly of BC 2021, Volume CLXIII: April 12, 2021 - February 8, 2022 | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-138_clxiii](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-138_clxiii) |
| Original Journals and session review | `R3H-190` — Journals, Legislative Assembly of BC 2022, Volume CLXIV: February 8, 2022 to February 6, 2023 | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-157_clxiv](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-157_clxiv) |
| Original Journals and session review | `R3H-191` — Journals, Legislative Assembly of BC 2023, Volume CLXV: February 6, 2023 to February 20, 2024 | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-210_clxv](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-210_clxv) |
| Original Journals and session review | `R3H-192` — Journals, Legislative Assembly of BC 2024, Volume CLXVI: February 20, 2024 to May 16, 2024 | [https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-126_clxvi](https://archives.leg.bc.ca/civix/document/id/leg_archives/legarchives/pp%201-126_clxvi) |
| Education orders and legal chain | `R3ED-001` — OIC 1429/1978 — designation of the Open Learning Institute | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1429_1978](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1429_1978) |
| Education orders and legal chain | `R3ED-003` — OIC 25/1988 — OLA Act commencement and predecessor transfer date | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0025_1988](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0025_1988) |
| Education orders and legal chain | `R3ED-006` — Open Learning Agency Repeal Act, SBC 2002 c73, original annual statute | [https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1737390750](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1737390750) |
| Education orders and legal chain | `R3ED-009` — BC Reg 201/2005 — TRU Act commencement, Gazette Part II | [https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v48n07_201-2005](https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v48n07_201-2005) |
| Education orders and legal chain | `R3ED-014` — BC Reg 187/2008 — Knowledge Network commencement, Gazette Part II | [https://www.bclaws.gov.bc.ca/civix/document/id/bcgaz2/bcgaz2/v51n13_187-2008](https://www.bclaws.gov.bc.ca/civix/document/id/bcgaz2/bcgaz2/v51n13_187-2008) |
| Education orders and legal chain | `R3ED-022` — OIC 861/1996 — creates School District 5 (Southeast Kootenay) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0861_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0861_1996) |
| Education orders and legal chain | `R3ED-023` — OIC 862/1996 — creates School District 6 (Rocky Mountain) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0862_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0862_1996) |
| Education orders and legal chain | `R3ED-024` — OIC 970/1996 — creates School District 8 (Kootenay Lake) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0970_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0970_1996) |
| Education orders and legal chain | `R3ED-025` — OIC 971/1996 — creates School District 20 (Kootenay-Columbia) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0971_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0971_1996) |
| Education orders and legal chain | `R3ED-026` — OIC 867/1996 — creates School District 51 (Boundary) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0867_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0867_1996) |
| Education orders and legal chain | `R3ED-027` — OIC 868/1996 — creates School District 53 (Okanagan Similkameen) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0868_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0868_1996) |
| Education orders and legal chain | `R3ED-028` — OIC 869/1996 — creates School District 58 (Nicola-Similkameen) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0869_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0869_1996) |
| Education orders and legal chain | `R3ED-029` — OIC 870/1996 — creates School District 67 (Okanagan Skaha) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0870_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0870_1996) |
| Education orders and legal chain | `R3ED-030` — OIC 871/1996 — creates School District 73 (Kamloops/Thompson) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0871_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0871_1996) |
| Education orders and legal chain | `R3ED-031` — OIC 872/1996 — creates School District 74 (Gold Trail) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0872_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0872_1996) |
| Education orders and legal chain | `R3ED-032` — OIC 873/1996 — creates School District 78 (Fraser-Cascade) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0873_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0873_1996) |
| Education orders and legal chain | `R3ED-033` — OIC 874/1996 — creates School District 79 (Cowichan Valley) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0874_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0874_1996) |
| Education orders and legal chain | `R3ED-034` — OIC 875/1996 — creates School District 82 (Coast Mountains) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0875_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0875_1996) |
| Education orders and legal chain | `R3ED-035` — OIC 876/1996 — creates School District 83 (North Okanagan-Shuswap) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0876_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0876_1996) |
| Education orders and legal chain | `R3ED-036` — OIC 877/1996 — creates School District 91 (Nechako Lakes) | [https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0877_1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0877_1996) |

## Handoff and integration actions

1. Provide the integrator the consolidated JSON with its complete source catalogue and original component names; treat the three ZIP files as evidence volumes, not as the entire research dataset.
2. Restore the 279-record branch claims under a non-colliding path and keep the 26 logo claims under `branches/logos/claims.json`. Preserve the already valid prior importable branch batch.
3. Re-review the 14 mapped holds with these URLs. Retain every independent identity, model and legal-instrument gate listed above; deduplicate facts already held.
4. Correct WANTED and the integration notes to distinguish recovered evidence awaiting model/identity review from genuinely missing documents. In particular, remove the repeated source requests for SSO, FPSC, HIBC and the 25-source regulator set; do not mark their whole subject histories complete.
5. Carry the omitted root, tribunal, education and legislature payloads as review data with their original cautions. Applying candidate rows, session endpoints, current legal classes or transfer clauses directly to historical accountability would erase those cautions.
6. Preserve the franchise supersession `R3G-F027` → `R4RC-106` when creating the dated franchise file. The obsolete year-only event remains in the retained prior component for provenance; the supersession is the instruction that prevents reusing it.

## Audit limits

This audit recovered links and data already present in the supplied package. It did not re-fetch external sources, certify legal conclusions, modify the repository, or authorize importing review-only records. Exact-copy absence is a payload-preservation observation, not proof that every related datum is absent from the live atlas. Parent-agent build, test and merge-simulation checks are separate from this audit.

Companion: `source-recovery.json`. Consolidated input SHA-256: `82dcde468a2d93758f183729fa34df25ed52fcfe0ff5080719e1f52779620a8e`.
