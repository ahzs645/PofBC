from pathlib import Path
import json,hashlib,collections
B=Path(__file__).resolve().parent
DATE='2026-10-21'
def out(name,data):
 (B/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def source(id,title,url,kind,files=(),locator=None,**kw):
 d={'id':id,'title':title,'url':url,'source_type':kind,'retrieved_on':DATE,'local_files':list(files)}
 if locator:d['pinpoint']=locator
 d.update(kw);return d
sources=[
source('R4H-001','Health Authority Performance Management ORCS, schedule 122352','https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/information-management-technology/records-management/orcs/health-authority-performance.pdf','official_records_schedule', ['raw/health-authority-performance.pdf','raw/health-authority-performance.txt','raw/orcs_p51.png','raw/orcs_p56.png','raw/orcs_p57.png'],'PDF pp.51, 56–57 / section 1 pp.25, 30–31; secondary 25440-40. Related executive-records route: PDF p.33 / section 1 p.7.',document_date='2005-02-21',date_note='Date printed on relevant schedule pages; file also contains later administrative revisions.',verification='Original PDF read; relevant p.57 visually verified.',newness='New record-series target; actual underlying agreements not retrieved.'),
source('R4H-002','Hansard, 27 April 1987, afternoon sitting — Organ Donor Awareness Week','https://lims.leg.bc.ca/hdms/file/Debates/34th1st/34p_01s_870427p.htm','contemporaneous_official_debate',['raw/hansard_1987_04_27.html','raw/hansard_1987_04_27.txt'],'Printed p.787, statement of Minister Dueck.',document_date='1987-04-27',newness='New dated PORT funding and operating observation.'),
source('R4H-003','Hansard, 27 April 1988, afternoon sitting — Organ Donor Awareness Week','https://lims.leg.bc.ca/hdms/file/Debates/34th2nd/34p_02s_880427p.htm','contemporaneous_official_debate',['raw/hansard_1988_04_27.html','raw/hansard_1988_04_27.txt'],'Printed p.4096, statement of Minister Dueck.',document_date='1988-04-27',newness='New explicit account that the Transplant Society initiated PORT; historical 1985 establishment assertion kept separate from registration.'),
source('R4H-004','Hansard, 9 June 1988, morning sitting — Ministry of Health estimates','https://lims.leg.bc.ca/hdms/file/Debates/34th2nd/34p_02s_880609a.htm','contemporaneous_official_debate',['raw/hansard_1988_06_09.html','raw/hansard_1988_06_09.txt'],'Printed p.4951, statement of Minister Dueck.',document_date='1988-06-09',newness='New ministerial account dates the Pacific organ retrieval program to 1985.',caution='HTML renders the acronym PORF. Preserve the literal source anomaly; clearer PORT expansion comes from R4H-002/003.'),
source('R4H-005','A. M. J. Buchan, Effect of Sympathomimetics on Gastrin Secretion from Antral G Cells in Culture, J Clin Invest 87 (1991), 1382–1386','https://www.jci.org/articles/view/115143/files/pdf','original_research_article',['raw/buchan1991.pdf','raw/buchan1991.txt','raw/buchan_p1.png'],'PDF p.1 / printed p.1382, Methods—Cell isolation.',document_date='1991-04',doi='10.1172/JCI115143',alternative_url='https://dm5migu4zj3pb.cloudfront.net/manuscripts/115000/115143/JCI91115143.pdf',verification='Original PDF paragraph visually verified.',newness='New explicit description of the Pacific Organ Retrieval for Transplantation System as part of the British Columbia Transplant Society.'),
source('R4H-006','Courthouse Libraries BC catalogue — The British Columbia Gazette. Part II: regulations','https://www.courthouselibrary.ca/catalogue-item?cid=8998','official_library_catalogue',['raw/gazette_part2_catalogue.html'],'Holdings for volume 20 (1977), part 2; call number KP36.5.',newness='Physical-volume location lead for missing 1977 proclamation, not a proclamation source.'),
source('R4H-007','BC Laws ministerial orders — 2001 XML catalogue','https://www.bclaws.gov.bc.ca/civix/content/mo/hmo/558283955/','official_instrument_catalogue',['raw/mo_index_2001.xml'],'M1–M332/2001; all 332 retrieved and first two pages, or all pages if shorter, screened.',newness='Systematic negative-search coverage. Individual PDF URLs are in the scan ledgers.'),
source('R4H-008','BC Laws ministerial orders — 2002 XML catalogue','https://www.bclaws.gov.bc.ca/civix/content/mo/hmo/975619104/','official_instrument_catalogue',['raw/mo_index_2002.xml'],'M1–M110/2002 screened. Later 2002 orders were not part of this pass.',newness='Systematic negative-search coverage. Individual PDF URLs are in the scan ledgers.'),
source('R4H-009','BC Centre for Disease Control Society financial statements, year ended 31 March 2016','https://www.phsa.ca/about-site/Documents/BC%20Centre%20for%20Disease%20Control.pdf','audited_financial_statements',['raw/bccdc_2016.pdf','raw/bccdc_2016.txt'],'PDF p.8 / printed p.5, note 1.',newness='Corroboration only; describes the 31 December 2001 continuation but supplies no numbered-to-named participant mapping.'),
source('R4H-010','BC Laws historical statutes — 1978 chapter index','https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/hstat1978htm','official_statute_index',[],newness='Negative route: chapter index did not supply a commencement table.'),
source('R4H-011','Alan F. J. Artibise, A Worthy, if Unlikely, Enterprise: The Labour Relations Board and the Evolution of Labour Policy and Practice in British Columbia, 1973–1980, BC Studies 56 (Winter 1982–83)','https://ojs.library.ubc.ca/index.php/bcstudies/article/download/1138/1182/4741','secondary_historical_article',[],'Indexed appendix table, printed p.40.',alternative_url='https://citeseerx.ist.psu.edu/document?doi=68ac6dd1912873c04d406d204052c19eec519eee&repid=rep1&type=pdf',retrieval_status='Search-index text located; publisher PDF returned HTTP 502 and alternate copies were not retrieved.',newness='Supplementary 21 October 1977 proclamation lead only. Not used for an accepted commencement claim.',caution='Table layout not visually verified. Government compilation R4R-080 is stronger corroboration for identified amendments.'),
source('R4H-012','BC Archives — government records research guidance','https://bcarchives.ca/government-records/','official_archive_guidance',[],newness='Access guidance only; no accession number for the ORCS binders was established.'),
source('R4H-013','Internet Archive metadata query: British Columbia Gazette Part II','https://archive.org/advancedsearch.php?q=title%3A%28British%20Columbia%20Gazette%20Part%20II%29&fl%5B%5D=identifier&fl%5B%5D=year&fl%5B%5D=title&rows=200&output=json','repository_catalogue_query',['raw/c2_route_2'],'121 returned records; all dated 1958–1962.',newness='Bounded catalogue search; no 1977 Part II volume in this result set. This does not prove that none is digitized elsewhere.'),
source('R4H-014','BC Laws annual statutes — 1979 XML catalogue','https://www.bclaws.gov.bc.ca/civix/content/hstats/hstats/747879843/','official_statute_catalogue',['raw/year-1979.xml'],'Chapter index plus 14 alphabetic statute folders.',newness='Negative route: no Table of Statutes or front-matter entry exposed in this catalogue.')
]
out('sources.json',sources)

def claim(id,item,text,src,loc,**kw):
 d={'id':id,'work_item':item,'claim':text,'source_ids':src,'pinpoint':loc,'new_in_round4':True}
 d.update(kw);return d
claims=[
claim('R4HC-001',['A6','A7'],'Schedule 122352 identifies society-amalgamation files under secondary 25440-40, with correspondence, consents and agreements; it describes three binders and requires full archival retention.',['R4H-001'],'PDF pp.51,56–57 / section 1 pp.25,30–31',claim_type='research_record_series_target',confidence='high',atlas_import=False,record_series='122352 / 25440-40',responsible_office_in_schedule='Societies Section',made_date=None,effective_date=None,observed_record_description_date='2005-02-21',remaining='No accession number or underlying consent/agreement retrieved. Scope is society amalgamation, not proof that all 43 council mergers are in these binders.'),
claim('R4HC-002',['B2','G1'],'The Pacific Organ Retrieval for Transplantation program was operating and funded by the Ministry of Health on 27 April 1987.',['R4H-002'],'Printed p.787',claim_type='dated_relationship_observation',subject_label='Pacific Organ Retrieval for Transplantation program',predicate='funded_by',object_label='Ministry of Health',observed_on='1987-04-27',date_precision='day',relationship_start=None,relationship_end=None,made_date=None,effective_date=None,confidence='high',atlas_import=True,import_rule='Add a funding edge observation; do not infer a corporate parent or accountability edge from funding.'),
claim('R4HC-003',['B2','G1'],'On 27 April 1988 the Health minister described PORT as a program initiated by the B.C. Transplant Society and responsible for coordinating organ retrieval across the province.',['R4H-003'],'Printed p.4096',claim_type='dated_relationship_observation',subject_label='Pacific Organ Retrieval for Transplantation program',predicate='initiated_by',object_label='B.C. Transplant Society',observed_on='1988-04-27',relationship_start=None,relationship_end=None,made_date=None,effective_date=None,confidence='high',atlas_import=True,import_rule='Use as program history and evidence of the program–society relationship. It does not establish a corporate renaming or incorporation date.'),
claim('R4HC-004',['B2','G1'],'An April 1991 original research article identifies the Pacific Organ Retrieval for Transplantation System as part of the British Columbia Transplant Society.',['R4H-005'],'PDF p.1 / printed p.1382, Methods—Cell isolation',claim_type='dated_relationship_observation',subject_label='Pacific Organ Retrieval for Transplantation System',predicate='part_of',object_label='British Columbia Transplant Society',observed_on='1991-04',date_precision='month',relationship_start=None,relationship_end=None,made_date=None,effective_date=None,confidence='high',atlas_import=True,import_rule='Add a program affiliation observation. This is not evidence that PORT was an earlier registered corporate name.'),
claim('R4HC-005',['B2'],'On 9 June 1988 the Health minister dated the establishment of the Pacific organ retrieval program to 1985.',['R4H-004'],'Printed p.4951',claim_type='retrospective_reported_establishment',subject_label='Pacific Organ Retrieval for Transplantation program',reported_event_date='1985',date_precision='year',observed_on='1988-06-09',made_date=None,effective_date=None,confidence='high for the reported year; exact legal or operational start day not supplied',atlas_import=True,import_rule='May support an attributed year-level program origin; do not turn it into a day or the Society’s legal registration date.',source_anomaly='The online Hansard spells the acronym PORF in this passage; the expanded program identity is corroborated by R4H-002/003.'),
claim('R4HC-006',['B2'],'On 27 April 1988 the Health minister said that the provincial government and medical community had established the B.C. Transplant Society in 1985.',['R4H-003'],'Printed p.4096',claim_type='retrospective_historical_account',subject_label='B.C. Transplant Society',reported_event_date='1985',date_precision='year',observed_on='1988-04-27',made_date=None,effective_date=None,confidence='high for what the minister reported; not legal incorporation evidence',atlas_import='narrative_only',import_rule='Preserve alongside the previously recovered Corporate Registry registration of 1 April 1986. Treat reported establishment and registration as different event types, with no assumed exact relationship.')
]
out('claims.json',claims)
coverage=[
{'work_item':'A1','status':'unchanged_unresolved_end_dates','new_findings':'No legal end date was proved for any of the seven rural boards. Prior exact designation dates remain intact.','remaining':'Seven express termination or redesignation instruments, certificates, or contemporaneous board records that establish the operative end.','avoid':'Do not infer dissolution from the repeal of a regulation, from replacement society incorporation, or from an administrative roster.','claim_ids':[],'source_ids':['R4H-007','R4H-008']},
{'work_item':'A2','status':'unchanged_unresolved_execution_dates','new_findings':'No carried-out amalgamation day was proved for any of the 43 councils. Prior designation dates and conditional merger authorizations remain intact.','remaining':'Dated resolutions by the relevant councils/boards, execution agreements or certificates, and ministerial correspondence documenting completion under the 1996 scheme.','archive_route':'Executive Records schedule 102906 is a possible ministerial correspondence route; ORCS 25440-40 is specific to society amalgamations and cannot be assumed to cover council-to-board mergers.','claim_ids':[],'source_ids':['R4H-001','R4H-007','R4H-008']},
{'work_item':'A5','status':'unchanged_unresolved_deposit_dates','new_findings':'No additional 1997–2001 renaming deposit/effective day proved.','remaining':'Gazette Part II annual indexes and the filed regulations/certified deposit records for the previously identified orders.','claim_ids':[],'source_ids':['R4H-006']},
{'work_item':'A6','status':'new_specific_archive_target_no_transaction_closure','new_findings':'ORCS 122352, secondary 25440-40 identifies three binders of amalgamation consents and agreements for full archival retention.','remaining':'Individual seven-society asset and staff transfer agreements, closing certificates and effective dates. The prior 15 February 2002 dissolutions are not transfer dates.','claim_ids':['R4HC-001'],'source_ids':['R4H-001','R4H-007','R4H-008']},
{'work_item':'A7','status':'new_specific_archive_target','new_findings':'The same binder series expressly covers society amalgamations with pre-2001 boards/councils and post-2001 authorities.','remaining':'Retrieve the underlying documents and build the local hospital/community-society successor register. Neither the binder contents nor the completeness of coverage for each local society has been established.','claim_ids':['R4HC-001'],'source_ids':['R4H-001']},
{'work_item':'B2','status':'strengthened_program_society_relationship','new_findings':'New dated PORT funding observation in 1987, Society-initiated program description in 1988, explicit part-of relationship in 1991, and a ministerial retrospective program start year of 1985.','remaining':'Exact operational start day and any legal instrument establishing or renaming a corporation. The prior Society registration date of 1 April 1986 is preserved.','claim_ids':['R4HC-002','R4HC-003','R4HC-004','R4HC-005','R4HC-006'],'source_ids':['R4H-002','R4H-003','R4H-004','R4H-005']},
{'work_item':'B4','status':'unchanged_unresolved_participant_certificate','new_findings':'No certified participant list for the BCCDC amalgamation of 2 April 2001 recovered.','remaining':'Certified amalgamation filing/certificate for resultant S0042940, with participating society numbers and names; examine predecessor files S0037212 and S0042656. Coincident event dates alone do not prove a complete participant list.','claim_ids':[],'source_ids':['R4H-007','R4H-009']},
{'work_item':'B5','status':'unchanged_unresolved_number_mapping','new_findings':'No mapping of the five 21 December 2001 numbered societies to the five 31 December 2001 named successors recovered.','remaining':'31 December 2001 amalgamation applications, agreements and certificates naming each participant. Number order is not a mapping rule.','claim_ids':[],'source_ids':['R4H-007','R4H-009']},
{'work_item':'C2','status':'partial_official_commencement_corroboration_from_root','new_findings':'Root source R4R-080, official 1994 Table of Statutes, records 21 October 1977 proclamation effectiveness for 1977 c.75 amendments to Hospital Corporations Act ss.2,5,10 and West Coast National Park Act s.7. Health agent visually checked PDF p.90 / printed p.1022.','remaining':'The actual proclamation, or a direct official table entry for the Ministry/Department of Health title provision. The 1979 bound Table of Statutes is the narrow next target because later official guides point pre-August-1979 history there.','claim_ids':[],'source_ids':['R4H-006','R4H-010','R4H-011','R4H-013','R4H-014'],'external_source_ids':['R4R-080'],'external_source_url':'https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/331277289','counting_policy':'Root owns R4R-080 and its new claims. Artibise indexed text remains only a supplementary lead, not a separately accepted effective-date claim.'},
{'work_item':'F1_health_service_nodes','status':'cross_module_handoff','new_findings':'Trans Care BC 2018 report supplied to branches agent, which retrieved p.3 and owns the new fall-2015 PHSA program-origin finding. Prior R3H-099 p.9 supplied four 2009/10 PHSA service-node observations to branches for integration.','remaining':'BC Mental Health and Substance Use Services formal name bridge was not established by this module.','claim_ids':[],'source_ids':[],'counting_policy':'Do not count branch-owned Trans Care research or the four prior-source integrations again in this module.'}
]
out('coverage.json',coverage)
scans=json.loads((B/'early2001_order_scan.json').read_text())+json.loads((B/'restructuring_order_scan.json').read_text())
out('order_scan_manifest.json',{'prepared_on':DATE,'unique_instruments':len(scans),'successful_downloads':sum(x['status']=='success' for x in scans),'pages_screened':sum(x.get('pages_inspected',0) for x in scans),'scope':[{'year':2001,'first_order':1,'last_order':332,'count':332},{'year':2002,'first_order':1,'last_order':110,'count':110}],'method':'Downloaded original PDFs. Extracted embedded text from first two pages; used Tesseract OCR when a page had fewer than 100 extracted characters. Searched resulting text for health entities, amalgamation and transfer terms; reviewed relevant candidates. Not a visual review of every page. Later pages and later 2002 orders are outside scope. OCR can miss text.','finding':'No requested council execution certificate, rural society conveyance agreement, BCCDC participant certificate or PHSA numbered-to-named mapping identified. This is a bounded negative search, not proof that such a record does not exist.','records':scans})
prior=json.loads((B/'prior/prior_package_carryforward.json').read_text())
socs=next(x['societies'] for x in prior['items'] if x['carryforward_key']=='Q4_seven_society_events')
boards=json.loads((B/'prior/rural_board_starts.json').read_text());councils=json.loads((B/'prior/council_starts.json').read_text())
out('unresolved_transaction_targets.json',{'prepared_on':DATE,'purpose':'Prior identities and dates carried forward solely to identify unresolved document requests; zero new designation or dissolution findings.','new_research_claims':0,'rural_boards':[{**x,'round4_legal_end_found':False,'target':'Express legal termination/redesignation or completed successor transfer instrument; original board minutes and Ministry executive correspondence.'} for x in boards],'folded_councils':[{**x,'round4_execution_day_found':False,'target':'Dated completed amalgamation resolution/certificate/agreement with the named successor under the 1996 reconstitution scheme.'} for x in councils],'rural_societies':[{'name':x['name'],'registration_number':x['registration_number'],'registration_date_carried_forward':x['registration_date'],'dissolution_date_carried_forward':x['dissolution_date'],'asset_transfer_date':None,'asset_transfer_instrument':None,'prior_citations':x['citations'],'target':'Executed asset/staff transfer agreement and closing schedule, especially December 2001–February 2002; examine registry file and ORCS 122352 / 25440-40 if applicable.'} for x in socs],'bccdc_participant_targets':[{'registration_number':n,'role':r} for n,r in [('S0037212','earlier BCCDC society'),('S0042656','coincident 2001 predecessor; complete participant role still requires certificate'),('S0042940','resultant 2 April 2001 BCCDC amalgamation society')]],'phsa_numbered_societies':[{'name':n,'registration_number':r,'registered':'2001-12-21','historical_end':'2001-12-31','successor_mapping':None} for n,r in [('PHSA Society ONE','S0044050'),('PHSA Society TWO','S0044051'),('PHSA Society THREE','S0044052'),('PHSA Society FOUR','S0044053'),('PHSA Society FIVE','S0044054')]],'phsa_named_resultants':[{'label':n,'registration_number':r,'registered':'2001-12-31','numbered_predecessor':None} for n,r in [('BC Cancer','S0044073'),('BC Centre for Disease Control','S0044074'),('BC Mental Health','S0044076'),('BC Transplant','S0044077'),("Children’s and Women’s",'S0044078')]],'registry_label_note':'PHSA labels in this request index are short research labels. Use the exact registered names from certified files before creating new legal-entity records.'})
report='''# Health history — fourth research pass

Research date: 21 October 2026. This module continues the expanded package against PofBC baseline `0f1587c5e982135f155ba6660af5192509351511`. It makes no repository changes.

## What this pass adds

The strongest new result is a specific archival route for the missing transfer paperwork: an official records schedule identifies **three binders of society-amalgamation consents and agreements**. The pass also supplies primary evidence distinguishing the **Pacific Organ Retrieval for Transplantation (PORT) program from the B.C. Transplant Society**, with dated funding and organizational observations in 1987, 1988 and 1991.

**None of the seven rural-board legal ends, 43 council execution days, seven rural-society asset-transfer dates, BCCDC participant certificates, or PHSA numbered-to-named mappings was proved in this pass.** Their unknown fields should stay unknown. A systematic screen covered 442 ministerial-order PDFs, but it did not identify those missing instruments. This handback gives the search boundaries and precise remaining document targets.

This module has six claim records: one archive-series finding and five PORT/Society historical or relationship observations. Three are directly useful dated relationship observations; one is an attributed program-origin year; one preserves the minister’s historical account without changing the Society’s legal registration date. The source register has 14 records, including catalogues and unsuccessful source leads; that is not a count of 14 substantive discoveries.

## 1. A6–A7: the missing agreements now have a specific record-series target

The Ministry’s **Health Authority Performance Management ORCS**, schedule **122352**, identifies secondary **25440-40**, *Society amalgamations with health authorities files*. The described records include consents and agreements. They cover society mergers with earlier boards/councils and with the post-2001 authorities; the schedule describes three binders and prescribes full archival retention. The default responsible office for this primary is the **Societies Section**. [R4H-001](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/information-management-technology/records-management/orcs/health-authority-performance.pdf), PDF pp.51, 56–57, section 1 pp.25, 30–31.

This is a narrow retrieval target. It does not establish a current accession number, confirm present custody, or prove which individual societies appear. In particular, the series concerns **society** amalgamations; it cannot be assumed to contain all 43 **council-to-board** executions. A related route for ministerial correspondence is Executive Records schedule **102906**, referenced on PDF p.33. Seek the actual documents before dating any transaction.

For the seven rural societies, request executed transfer agreements, schedules identifying assets, liabilities and staff, ministerial consents, and completion or closing records. Preserve the prior registry dissolutions of **15 February 2002** as dissolution events. The known December 2001 appointment orders do not become conveyances merely because they replaced directors.

## 2. B2: PORT and the Transplant Society can be connected more accurately

| Observation | Evidence | What it supports |
|---|---|---|
| 27 April 1987 | Health minister Dueck described PORT as operating and funded by the Ministry of Health. | A dated `funded_by` observation and existence checkpoint for the program. |
| 27 April 1988 | Dueck said the B.C. Transplant Society had subsequently initiated PORT, which coordinated organ retrieval across the province. | Program history and an explicit Society–program relationship, without assuming a corporate rename. |
| 9 June 1988 | Dueck dated establishment of the Pacific organ retrieval program to 1985. | An attributed year-level program origin. |
| April 1991 | An original research paper identified the Pacific Organ Retrieval for Transplantation System as part of the British Columbia Transplant Society. | A second, independent program-affiliation observation. |

The first two observations are in official Hansard, [27 April 1987, p.787 (R4H-002)](https://lims.leg.bc.ca/hdms/file/Debates/34th1st/34p_01s_870427p.htm) and [27 April 1988, p.4096 (R4H-003)](https://lims.leg.bc.ca/hdms/file/Debates/34th2nd/34p_02s_880427p.htm). The retrospective program year is in [9 June 1988, p.4951 (R4H-004)](https://lims.leg.bc.ca/hdms/file/Debates/34th2nd/34p_02s_880609a.htm). That online passage renders the acronym as “PORF”; the fuller name and PORT spelling are clear in the other debates.

The independent observation is A. M. J. Buchan’s original research article, [J Clin Invest 87 (April 1991), p.1382, Methods—Cell isolation (R4H-005)](https://www.jci.org/articles/view/115143/files/pdf). Its first page was visually checked. Use publication month as the observation precision; the manuscript’s earlier submission dates do not establish an exact organizational start.

The April 1988 statement also says the government and medical community established the Society in **1985**. Keep that reported establishment year alongside the **1 April 1986 Corporate Registry registration** recovered previously. Those are different event types. The sources support a program within or initiated by the Society; they do **not** show that PORT was an earlier registered corporate name, that a legal rename occurred in 1985, or the exact date the program commenced.

Recommended atlas treatment: add a distinct PORT program identity if the model supports programs, with an attributed 1985 origin, an existence/funding checkpoint in 1987, and program-to-Society observations in 1988 and 1991. A funding edge should remain separate from ownership or ministerial accountability.

## 3. The requested transaction gaps remain open

| Target | Current evidence boundary | Next exact document |
|---|---|---|
| Seven rural boards (A1) | Their original designations were proved in round 3; no new legal end was found here. | Express termination/redesignation instrument or original successor completion record. |
| Forty-three councils (A2) | Their starts are proved. Conditional 1996 authorizations still do not establish the day each amalgamation was carried out. | Dated council/board resolutions, certificates, executed agreement, or ministerial completion correspondence. |
| Renaming orders (A5) | Known made dates remain distinct from unproved filing/effective dates. | Relevant Part II Gazette entry or certified deposit record. |
| Seven rural societies (A6) | Registry dissolution and director replacement are known; assets/staff transaction dates are not. | Executed conveyance or amalgamation agreement, transfer schedules and completion date. |
| BCCDC on 2 April 2001 (B4) | Coincident predecessor endings and resultant registration are known. | Certified participant certificate/application for resultant S0042940, with S0037212 and S0042656 files. |
| PHSA on 31 December 2001 (B5) | The five numbered and five named societies have known registrations and ends. | The five amalgamation filings naming the specific participants; ordinal numbering is not a mapping rule. |

The complete 43-council and seven-board names, prior source references, seven society registry numbers, and PHSA/BCCDC file targets are in `unresolved_transaction_targets.json`. That file is explicitly carryforward material and introduces **zero new start/end claims**.

## 4. Scope of the unsuccessful online searches

### Ministerial orders

Both BC Laws XML catalogues and original PDFs were retrieved. The scan covered **M1–M332/2001 (all 332)** and **M1–M110/2002 (110)**: **442 unique instruments**, all downloads successful, **506 pages screened**. Original PDFs and extracted/OCR text are preserved. See [2001 catalogue (R4H-007)](https://www.bclaws.gov.bc.ca/civix/content/mo/hmo/558283955/) and [2002 catalogue (R4H-008)](https://www.bclaws.gov.bc.ca/civix/content/mo/hmo/975619104/).

The method extracted the first two pages of each order, or all pages if shorter; it used OCR when embedded text was sparse. Relevant text hits were reviewed. It was **not** a visual review of every page, and later pages and orders after M110/2002 were outside scope. OCR can miss text. Known appointments and boundary orders appeared, but no requested execution certificate, society conveyance, BCCDC participant list or PHSA mapping was identified. This is evidence of a bounded unsuccessful search, not proof that no such instrument exists.

The scan is reproducible from `scan_early2001_orders.py` and `scan_restructuring_orders.py`; `order_scan_manifest.json` combines the two detailed ledgers.

### Financial, legal, archival and registry routes

Targeted public searches included the society names/numbers, amalgamation and transfer terminology, legal decisions, audited statements, Gazette entries and archival descriptions. Later accounts corroborated the restructuring without supplying the missing participant documents. For example, the [2016 BCCDC financial statements, PDF p.8 / printed p.5 (R4H-009)](https://www.phsa.ca/about-site/Documents/BC%20Centre%20for%20Disease%20Control.pdf) describe the December 2001 corporate continuation but do not map the numbered societies. They do not close B4 or B5.

Eighteen attempts at predictable early Public Accounts statement URLs returned HTTP 503. Those failures are recorded in `financial_retrievals.json`; they are **access failures**, not evidence that the reports never existed. The Northern Health 2004/05 statements and later BCCDC accounts were retrievable but did not identify the required transaction instruments.

The BC Archives government-records guidance was accessible; attempted catalogue searches did not yield an accession for the binders, and the legacy catalogue returned 503 on attempted routes. No request was sent to an archive or registry, no paid registry filing was ordered, and no absent record was inferred from a search failure.

## 5. C2: 1977 commencement — stronger corroboration, actual proclamation still missing

Root recovered **R4R-080**, the official [1994 Table of Statutes](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/331277289). The health agent visually verified **PDF p.90 / printed p.1022**: the entries for Hospital Corporations Act ss.2, 5 and 10 associate their amendments by **1977 c.75** with proclamation effectiveness on **21 October 1977**. PDF p.266 / printed p.1198 similarly records the West Coast National Park Act s.7 amendment. These are official compilation evidence for the identified amendments, stronger than the secondary historical lead below. Root owns that source and any corresponding claims; it is not counted again here.

This still does not put the actual proclamation, or a direct table entry for the Health-title provision, in this module. The 1994 table’s introduction points pre-August-1979 proclamation history to the **1979 bound Table of Statutes**. That volume is now the best narrow target, alongside the original proclamation in **Gazette Part II, volume 20 (1977), part 2**.

The [Courthouse Libraries catalogue (R4H-006)](https://www.courthouselibrary.ca/catalogue-item?cid=8998), call number **KP36.5**, lists physical 1977 Part II holdings. An Internet Archive Part II query returned 121 records, all from 1958–1962, and therefore did not supply 1977. The separate 1977 Gazette result set consisted of Part I issues; the 15 Part I issues previously checked were not re-read. Internet Archive title/year searches found no 1977 or 1978 statute volume in those result sets.

The BC Laws [1978 chapter index (R4H-010)](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/hstat1978htm) did not supply the commencement table. The [1979 annual-statutes catalogue (R4H-014)](https://www.bclaws.gov.bc.ca/civix/content/hstats/hstats/747879843/) exposes the chapter index and alphabetic statute folders, without a front-matter/Table of Statutes item.

An indexed appendix in Alan F. J. Artibise’s BC Studies article also points to 21 October 1977. Its publisher PDF returned 502 and an alternate copy was not retrieved; the table layout was not visually checked. **R4H-011 remains a supplementary lead, not an accepted commencement source.** None of these findings should be described as recovery of the actual proclamation.

## 6. Cross-module results and counting

The new Trans Care BC 2018 report was handed to the branches researcher, who retrieved and verified its p.3 statement that the PHSA program was established in **fall 2015**. That claim belongs to the branches module and is not duplicated here.

The already recovered 2009/10 Health Services annual report, **R3H-099 p.9**, was supplied for four dated PHSA service-node observations: BC Children’s, BC Women’s, BCCDC and Perinatal Services BC. Those are integrations of prior evidence, not new research discoveries. Distinguish service identities from earlier hospital corporations. A formal predecessor-name bridge for the present BC Mental Health and Substance Use Services label was not established here.

## Files

- `sources.json`: 14 source, catalogue and lead records, with retrieval status and pinpoints.
- `claims.json`: six new records, with explicit type, confidence and import limits.
- `coverage.json`: ten work-item statuses, including cross-module ownership.
- `unresolved_transaction_targets.json`: prior identities and precise outstanding document targets.
- `records_request_targets.md`: a reviewable request specification; nothing has been sent.
- `order_scan_manifest.json`, the two scan ledgers and two scripts: bounded 442-order audit.
- `search_ledger.md`: routes, outcomes and limitations.
- `raw/`: retrieved originals, extracts and evidence images.
- `sha256_manifest.json`: file integrity information.
'''
(B/'report.md').write_text(report)
req='''# Narrow document targets — not sent

Prepared 21 October 2026. These are retrieval specifications, not evidence that every listed document exists or is held by a particular office.

## 1. Ministry society-amalgamation binders

Ask the government records custodian to identify the accession, file list and access route for **Health Authority Performance Management ORCS schedule 122352, secondary 25440-40**, titled *Society amalgamations with health authorities files*. The official schedule, section 1 pp.30–31, describes three binders with consents, agreements and correspondence, covering society amalgamations before and after the 2001 restructuring. It assigns full archival retention. The primary identifies the Societies Section as default responsible office. Request the binder/file index first, then relevant complete agreements, schedules, consents and certificates.

For the seven rural community health services societies listed in `unresolved_transaction_targets.json`, seek executed asset/staff transfer and closing records around December 2001–February 2002, including the effective date, transferee, allocation of liabilities and disposition of employees. Their registry dissolution date alone cannot answer those questions.

## 2. Forty-three council amalgamations and seven rural boards

Use the exact names and original order references in `unresolved_transaction_targets.json`. Seek board/council resolutions, certificates of amalgamation, final executed agreements and Ministry confirmation that the amalgamation had been carried out. Relevant ministerial letters or executive reports may be in **Executive Records schedule 102906**, which the Health Authority Performance Management schedule identifies as the retained route for ministerial/executive records. This is a route to investigate, not a confirmed file accession.

For each of the seven rural boards, seek an express legal termination/redesignation instrument or completed transfer record establishing when the board ceased. Do not treat replacement society registration or repeal of a regulation as a common legal end without operative wording.

## 3. BCCDC corporate registry filing — 2 April 2001

Request the certified amalgamation application, agreement, certificate and participant schedule for **S0042940**, registered by amalgamation on 2 April 2001. Cross-reference files **S0037212** and **S0042656**. Ask for the exact registered participant names and numbers and operative date/time. Coincident predecessor endings alone do not establish the complete list.

## 4. Five PHSA amalgamations — 31 December 2001

Request each certified amalgamation filing for named resultant societies **S0044073, S0044074, S0044076, S0044077 and S0044078**. Ask which numbered participant, if any, appears in each: **S0044050, S0044051, S0044052, S0044053 or S0044054**, registered 21 December 2001. Request all participants, not just the numbered shell, and the effective date/time. Do not infer mappings from ordinal or registration-number order.

## 5. 1977 Ministry titles commencement

First request the **1979 Statutes of British Columbia, Table of Statutes**, specifically the entries for the Department/Ministry of Health Act and **Ministerial Titles Amendment Act, SBC 1977 c.75**, with all commencement/proclamation annotations. The 1994 official table and later official guides direct earlier proclamation history to this 1979 table.

Also request the actual proclamation under the 1977 Act’s commencement provision, associated with **OIC 3240, approved 21 October 1977**, and the relevant Gazette Part II entry/index. **The British Columbia Gazette, Part II, volume 20 (1977), part 2**, call number **KP36.5**, is catalogued at Courthouse Libraries BC. The official 1994 table independently records 21 October 1977 proclamation effectiveness for identified amendments made by this Act; the original proclamation remains the desired primary instrument.
'''
(B/'records_request_targets.md').write_text(req)
ledger='''# Health round 4 — search ledger and boundaries

Date: 21 October 2026. This is a route-level ledger reconstructed from this research session; it does not purport to reproduce every search-engine query verbatim. Both search engines were used for niche and authoritative coverage. Raw originals and machine-readable scans are preserved.

| Route | Scope / result | Interpretation |
|---|---|---|
| Prior-package review | Read expanded report, claims, coverage, search ledger and relevant original evidence; extracted 43 council starts, seven board starts and prior carryforward registry records. | Avoided recounting existing starts/dissolutions as new. |
| Ministerial orders 2001 | All M1–M332; 332 original PDFs downloaded. | First two pages screened, not every page visually reviewed. |
| Ministerial orders 2002 | M1–M110; 110 original PDFs downloaded. | Later 2002 orders not included. |
| Combined order text/OCR | 442 instruments, 506 pages; health names, society, amalgamation and transfer terms screened; relevant candidates read. | No requested transaction certificate or mapping found. OCR limitations remain. |
| Registry/transaction searches | BCCDC participant numbers, PHSA numbered/named societies, amalgamation and conveyance terminology, legal decisions, later accounts. | No certified participant mapping recovered; dates alone not substituted. |
| Early Public Accounts URLs | 18 predictable report URLs for early authority financial statements returned 503. | Access failure; not an absence finding. Exact URLs in financial_retrievals.json. |
| Later audited accounts | Northern Health 2004/05, BCCDC 2016, prior PHSA accounts and restructuring descriptions. | Corroboration without target agreements/certificates; BCCDC original retained. |
| Archival record schedules | Located ORCS 122352 / 25440-40, describing three retained binders. | New precise retrieval lead; no accession confirmed. |
| BC Archives catalogue | Government-records guidance accessible; attempted legacy catalogue routes returned 503; no indexed binder accession identified. | Do not infer destruction/non-existence or claim confirmed current custody. |
| PORT institutional history | Official Hansard 1987 and 1988; original JCI research 1991. | Program and Society distinguished; retrospective year separate from registry incorporation. |
| 1977 Gazette | Physical Part II catalogue located; previous Part I searches not repeated. | Actual proclamation not retrieved. |
| Internet Archive Part II | Exact metadata query in raw/c2_route_2; all 121 results retrieved, dated 1958–1962. | No 1977 item in this result set; not a claim about all repositories. |
| Internet Archive statutes | title:(statutes British Columbia) AND year:1977; same for 1978; both zero. Broader title query returned 23. | Bound volume not recovered. Query metadata is preserved in each JSON. |
| 1978/1979 BC Laws catalogues | 1978 chapter index and 1979 annual-statute XML catalogue. | No direct commencement table/front matter found. |
| Secondary Artibise appendix | Search-index text points to 21 October 1977; publisher PDF 502, alternate 404/403. | Layout unverified; lead only, superseded in evidential strength by root R4R-080. |
| Root 1994 Table of Statutes | R4R-080 p.90/printed1022 visually cross-checked; p.266/printed1198 text checked. | Official proclamation-effectiveness corroboration for identified amendments, not actual proclamation recovered. |
| Branch handoff | Trans Care BC 2018 p.3; prior R3H-099 p.9 PHSA services. | Branch researcher owns new Trans Care claim; prior observations are integrations. |

## Search terms / identity families considered

The session searched the legal and common names of the seven rural societies and boards; community health council amalgamations; BCCDC’s S0037212, S0042656 and S0042940 sequence; PHSA’s five numbered and five named society identities; amalgamation certificates, consents, asset/staff transfers and audited-account notes; Ministry records schedules; PORT/Pacific Organ Retrieval/BC Transplant Society; and Ministerial Titles Amendment Act 1977 proclamation/commencement variants. This is a description of search topics, not an invented exact-query log.

## Why the negative results do not close the gaps

A conditional authorization is not an executed amalgamation. Director replacement is not asset conveyance. Dissolution is not necessarily a transfer day. Coincident registry events are not a complete participant certificate. Search failures and HTTP errors are not proof of absence. Preserve these distinctions in any atlas import.
'''
(B/'search_ledger.md').write_text(ledger)
# Hash originals and all current module data, excluding this generated manifest itself.
manifest=[]
for p in sorted(B.rglob('*')):
 if p.is_file() and p.name!='sha256_manifest.json':
  manifest.append({'path':str(p.relative_to(B)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out('sha256_manifest.json',{'prepared_on':DATE,'files':manifest})
print('Wrote',len(sources),'sources,',len(claims),'claims,',len(coverage),'coverage items;',len(manifest),'hashed files.')
