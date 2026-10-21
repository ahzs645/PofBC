import json, hashlib, re
from pathlib import Path
from collections import Counter

B=Path(__file__).parent
R=B.parent/'prior/evidence/round3'
sources=[s for s in json.loads((B/'sources.json').read_text()) if s['id'] not in {'R3H-099','R3T-036'}]
by_source={s['id']:s for s in sources}
claims=[]
def add(body,typ,date,precision,meaning,sid,locator,**kw):
    ids=sid if isinstance(sid,list) else [sid]
    c=dict(id=f'R4B-C{len(claims)+1:03d}',body_id=body,type=typ,date=date,precision=precision,meaning=meaning,source_ids=ids,locator=locator,checked='2026-10-21',novelty='new_evidence_not_in_round3_branches',status='documented_partial',full_history_complete=False)
    c.update(kw);claims.append(c);return c['id']
def relation(body,date,precision,rel,obj,meaning,sid,loc,**kw):
    return add(body,'relationship_observation',date,precision,meaning,sid,loc,relation=rel,object_as_printed=obj,**kw)

# New dates and historically bounded relations. None implies continuity through unsampled years.
add('buy-bc','program_launch','1993','year','The government launched the named Buy BC marketing program in 1993. This is retrospective first-party audit evidence, not a branch incorporation.','R4B-018','PDF p6 / printed p4, Buy BC Program History',entity_kind='program',evidence_kind='official_audit_retrospective_history')
relation('buy-bc','2002','year','administered_by','BC Agricultural Council','Government discontinued marketing funding and transferred management and delivery to the industry organization. This is administration, not Crown ownership or ministry membership.','R4B-018','PDF p6 / printed p4')
add('buy-bc','government_program_relaunch','2018','year','The audit identifies a government relaunch starting in 2018, following industry delivery.','R4B-018','PDF p6 / printed p4')
relation('buy-bc','2023-06','month','administered_by','Food and Beverage Branch, Agriculture Resource Division, Ministry of Agriculture and Food','The audit explicitly identifies the delivery branch, division and ministry in its introductory description.','R4B-018','PDF p5 / printed p3',entity_kind='program')
relation('food-and-beverage-branch','2023-06','month','part_of','Agriculture Resource Division, Ministry of Agriculture and Food','Named organizational unit in the audit, with 52 full-time employees; proposed historical observation, not a founding claim.','R4B-018','PDF p5 / printed p3',entity_id_status='proposed_if_not_already_in_repository')
add('bc-training-and-education-savings-program','named_program_regulation_made','2013-03-20','day','OIC173/2013 made the named BCTES Program Regulation, BC Reg132/2013, initially drawing grants from the Children’s Education Fund. It planned an October2014 application date that was superseded before arrival.','R4B-026','PDF pp1–2; regulation s1',entity_kind='program')
add('bc-training-and-education-savings-program','special_account_continued_under_new_name','2014-06-23','day','The Children’s Education Fund special account was continued as the BCTES Program special account by 2014c14 s50. OIC389/2014 was approved20June; the official regulations bulletin records23June2014 commencement.',['R4B-021','R4B-015','R4B-016'],'Act PDF p18, s50 / new s9.4(2); order PDF p1; bulletin entry389/2014',entity_kind='statutory_special_account',predecessor='Children’s Education Fund special account',date_kind='commencement',not_a_separate_corporation=True)
add('bc-training-and-education-savings-program','application_commencement','2015-08-15','day','The original replacement regulation defines the application commencement date as15August2015. This is the application opening date, not the first legal appearance of the program.','R4B-015','PDF p2, regulation s1',entity_kind='program')
add('bc-arts-and-culture-endowment','statutory_special_account_established','2008-03-31','day','Budget Measures Implementation Act2008c10 s113 establishes the named special account, continuing the Olympic Arts Fund as Arts Legacy Fund Subaccount and adding BC150 Cultural Fund Subaccount. Section126 tableitem48 gives retroactive31March2008 commencement.','R4B-022','PDF/printed pp42–43, s113; p50, s126 item48',entity_kind='statutory_special_account',date_kind='retroactive_commencement',not_a_separate_corporation=True)
relation('bc-arts-and-culture-endowment','2008-03-31','day','payments_recommended_by','British Columbia Arts Council','The Act assigns the Arts Council a recommendation role for BC150 payments. Recommendation is not ownership or institutional parentage.','R4B-022','PDF/printed pp42–43, new s9(5)(b); also p1, amendment to Arts Council Act s3(1)(b.1)',entity_kind='statutory_special_account')
add('disaster-financial-assistance','program_established','1995','year','An official2016 bulletin explicitly states the provincial DFA program was established in1995. Do not substitute the1970 start of the federal DFAA.','R4B-042','Main bulletin, paragraph beginning Disaster Financial Assistance has consistently...',entity_kind='program',evidence_kind='official_retrospective_statement')
add('disaster-financial-assistance','regulation_made','1995-03-30','day','OIC310/1995 makes the original Compensation and Disaster Financial Assistance Regulation under Emergency Program Act ss19,20,28. The stamped approval date is30March1995, visually checked.','R4B-043','PDF p1',entity_kind='program',date_kind='order_approved')
add('disaster-financial-assistance','regulation_deposited','1995-03-31','day','BC Reg124/95 was deposited31March1995. Distinguish deposit from the order’s approval on30March and from the year-only retrospective program start.','R4B-069','Consolidation header',entity_kind='program',date_kind='regulation_deposit')
relation('disaster-financial-assistance','2016-07-07','day','administered_by','Emergency Management BC, Ministry of Transportation and Infrastructure','The contemporaneous archived bulletin header identifies EMBC and the ministry; the current news-site navigation uses today’s ministry names and is not historical parent evidence.','R4B-042','Archived release header and main bulletin',historical_parent_source='https://archive.news.gov.bc.ca/releases/news_releases_2013-2017/2016TRAN0185-001237.htm')
add('provincial-treasury','named_in_assented_statute','1985-06-28','day','1985c52 s84 adds Provincial Treasury Division to the public-service employee exclusion provision. This is a legal mention, not proof of the division’s first day or of that amendment’s commencement.','R4B-028','PDF p21 / printed p275, s84; assent on firstpage',date_kind='assent_of_document_containing_name',use_as_founding_date=False)
add('provincial-treasury','existence_sighting','1986-04-10','day','The Auditor General describes officials and several branches within Provincial Treasury. Cover letter is10April1986; filename misleadingly says1985. Use1986as the conservative contemporaneous observation.','R4B-027','Coverletter PDF p3; printed p16 para3.19 and p20 para3.41 / PDF pp22,26',date_kind='report_transmittal')
relation('provincial-treasury','1986-04-10','day','part_of','Ministry of Finance','Auditor General explicitly locates Provincial Treasury within the Ministry of Finance.','R4B-027','Printed p16 para3.19 / PDF p22')
relation('provincial-treasury','1996-07-29','day','part_of','Ministry of Finance and Corporate Relations','Minister Andrew Petter introduces Chris Trumpy as assistant deputy minister of Provincial Treasury during the ministry estimates.','R4B-002','Hansard printed p1077')
add('building-and-safety-standards','existence_sighting','2014-05-20','day','Dated official consultation response explicitly identifies the Building and Safety Standards Branch as the initiative lead.','R4B-030','PDF/printed p3',entity_kind='administrative_branch')
relation('building-and-safety-standards','2014-05-20','day','part_of','Office of Housing and Construction Standards, Ministry of Natural Gas Development and Minister Responsible for Housing','The contact block and accompanying sentence explicitly identify both intervening office and ministry.','R4B-030','PDF/printed p3')
for bid,n in [('community-capital-development','Community Capital Development Division'),('infrastructure-policy-and-partnerships','Infrastructure Policy and Partnerships Division')]:
    add(bid,'existence_sighting','2025-03-17','day',f'{n} is explicitly listed in the Ministry of Infrastructure staff allocations as of17March2025. This is not a backdated18November2024 unit creation claim.','R4B-006','PDF pp17–18; p18 staffing as-of date',entity_kind='administrative_division')
    relation(bid,'2025-03-17','day','part_of','Ministry of Infrastructure',f'The organizational description and staffing table identify {n} as a division of the ministry.','R4B-006','PDF pp17–18')
add('community-safety-and-victim-services','existence_sighting','2024','year','The2024 PSSG transition binder executive organizational chart expressly names Community Safety and Victim Services Branch and ADM Taryn Walsh. Unlike a budget line, this is direct organizational evidence.','R4B-038','PDF p6 / ministryprofile printed p4 of6',entity_kind='administrative_branch')
relation('community-safety-and-victim-services','2024','year','part_of','Ministry of Public Safety and Solicitor General','Executive chart places the branch under the Deputy Solicitor General.','R4B-038','PDF p6 / ministryprofile p4of6')
add('community-safety-and-victim-services','existence_sighting','2025','year','2025 estimates binder contains a named branch contents page and its service-delivery notes. No exact rename day from Community Safety and Crime Prevention Branch is proved.','R4B-039','PDF pp149–152',entity_kind='administrative_branch')
add('safe-campuses-bc','named_web_resource_sighting','2019-08-29','day','The official release explicitly links to Safe Campuses BC. This establishes dated use of the named resource, not a branch or Crown corporation.','R4B-008','Learn More section',entity_kind='public_information_resource',integration_gate='Keep as resource/program node; do not assign an administrative founding date')
add('connectivity-in-bc','named_web_resource_sighting','2021-04-07','day','The official release separately links to Connectivity in B.C. and to the Connecting British Columbia grant program. The two names must not be silently equated.','R4B-053','Learn More section',entity_kind='public_information_resource',integration_gate='Date the website/resource, not an inferred branch or the separate Connecting BC program')
add('lets-go-bc','official_mark_publication','2025-04-23','day','CIPO publishes notice of adoption and use of the LET’S GO BC design as an official mark. The graphic was visually checked. This proves brand presence, not first launch or a new government body.','R4B-049','PDF/printed p2673, application928917',entity_kind='campaign_brand',integration_gate='Use as brand sighting only')
relation('lets-go-bc','2025-04-23','day','official_mark_held_by','His Majesty the King in right of British Columbia, represented by Minister of Finance, Government Communications and Public Engagement','The named rights holder is distinct from the delivery ministry; do not infer Finance as the program’s administrative parent.','R4B-049','PDF/printed p2673, application928917')
add('lets-go-bc','campaign_use_sighting','2025-09-19','day','A publicly released TACS email discusses Let’s Go BC scarves for a UBCM presentation, linking the campaign to Tourism, Arts, Culture and Sport activity. It does not establish a new branch.','R4B-050','PDF p4 / releasedrecord p2, email19September2025',entity_kind='campaign_brand')
add('building-bc','program_family_sighting','2018/19','fiscal_year','BC Housing’s2018/19 annual report states that sinceFebruary2018 it initiated four Building BC affordable-housing funding programs. Use the reporting-period observation; this wording does not give all four funds the sameFebruary2018 opening date.','R4B-007','PDF/printed p5',entity_kind='program_family',observed_during={'start':'2018-04-01','end':'2019-03-31'})
relation('building-bc','2018/19','fiscal_year','administered_by','BC Housing','The annual report describes the four Building BC programs as its own achievements. Program administration is distinct from a ministry branch relationship.','R4B-007','PDF/printed p5',entity_kind='program_family')
add('trans-care-bc','program_established','2015','season','PHSA’s April2018 program update expressly states that Trans Care BC was established as a PHSA program in fall2015. Retain season precision; do not invent1October.','R4B-052','PDF/printed p3, What is Trans Care BC?',entity_kind='health_program',date_text='fall 2015',lead_credit='/root/health_round4')
relation('trans-care-bc','2015','season','program_of','Provincial Health Services Authority','The establishment statement identifies PHSA as parent from fall2015.','R4B-052','PDF/printed p3',date_text='fall 2015')
add('bc-mental-health-and-substance-use-services','existence_sighting','2015-12-17','day','Official Riverview release names Lynn Pelletier as vice president of BC Mental Health & Substance Use Services. This proves the current-name service existed, but not the date it changed from BC Mental Health and Addiction Services.','R4B-054','Quotes section, Lynn Pelletier',entity_kind='health_service_program',lead_credit='/root/health_round4')

# Prior evidence that repairs the branch ledger, not new archival discoveries.
ps=json.loads((R/'health/sources.json').read_text())
old=next(x for x in ps if x.get('source_id')=='R3H-099')
sources.append(dict(id='R3H-099',title=old['title'],url=old['url'],retrieval_status='previous_package_original_reused',local_file='../prior/evidence/round3/health/originals/hs_2009_10_report.pdf',sha256=old['sha256'],novelty='prior_cross_module_integration'))
for bid,name in [('bc-centre-for-disease-control','BC Centre for Disease Control'),('bc-childrens-hospital','BC Children’s Hospital and Sunny Hill Health Centre for Children'),('bc-womens-hospital','BC Women’s Hospital and Health Centre'),('perinatal-services-bc','Perinatal Services BC')]:
    add(bid,'existence_sighting','2009/10','fiscal_year',f'The ministry report expressly lists {name} among the agencies through which PHSA delivers selected province-wide health programs. This is a service-node observation, distinct from prior society registration dates.','R3H-099','PDF/printed p9',novelty='prior_cross_module_integration',observed_during={'start':'2009-04-01','end':'2010-03-31'})
    relation(bid,'2009/10','fiscal_year','program_delivered_through_phsa','Provincial Health Services Authority',f'{name} is in the report’s explicit PHSA agency list.','R3H-099','PDF/printed p9',novelty='prior_cross_module_integration')
sources.append(dict(id='R3T-036',title='OIC367/2024 audit-hearings committee appointment',url='https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0367_2024',retrieval_status='previous_package_original_reused',local_file='../prior/evidence/round3/tribunals/raw/R3T-036.pdf',novelty='prior_cross_module_integration'))
add('health-care-practitioners-special-committee-for-audit-hearings','existence_sighting','2024-06-30','day','Previously recovered appointment order effective30June2024 identifies the named statutory committee. It proves existence by this date, not first establishment.','R3T-036','PDF p1',novelty='prior_cross_module_integration',prior_claim_ids=['R3T-C053','R3T-C054'])

# Historical branch families beyond the33-record undated set.
add('parks-and-recreation-division','division_established','1948','year','The1957 departmental report says the Parks and Recreation Division was established in1948 within the Forest Service predecessor administration.','R4B-013','Provincial Parks history, between sectioncover atII21 and photographs beforeII24; exactpageimage inaccessible',entity_id_status='proposed_historical_node',evidence_kind='original_report_library_fulltext')
add('bc-parks','administrative_transfer_and_rename','1957-04-01','day','The same report explicitly says the Parks and Recreation Division entered the newly established Department of Recreation and Conservation on1April1957 and became the Provincial Parks Branch. The signed implementing instrument remains unfound.','R4B-013','Provincial Parks Branch History, paragraph immediately before OkanaganLakephotographs andII24',prior_name='Parks and Recreation Division',new_name='Provincial Parks Branch',instrument_found=False,evidence_kind='original_annual_report_statement')
relation('bc-parks','1957-04-01','day','part_of','Department of Recreation and Conservation','Exact effective transfer date stated in the contemporary departmental annual report.','R4B-013','Provincial Parks Branch History; introduction printedII7')
add('fish-and-game-branch','administrative_transfer_and_rename','1957-04-01','day','The report’s branch history says the Game Commission became part of Recreation and Conservation on1April1957 and the present title was Fish and Game Branch.','R4B-013','Fish and Game Branch History, sectionbeginningII9 beforeII12; introductionII7',prior_name='British Columbia Game Commission',prior_parent='Department of the Attorney-General',new_parent='Department of Recreation and Conservation',entity_id_status='proposed_historical_node')
relation('photographic-branch','1957-04-01','day','part_of','Department of Recreation and Conservation','The Photographic Branch report explicitly says it became a separate unit effective1April1957; history says it had been part of the BC Government Travel Bureau.','R4B-013','PrintedII42 and precedinghistory',entity_id_status='proposed_historical_node',prior_parent='British Columbia Government Travel Bureau')
add('conservation-officer-service','administrative_separation_observed','1980-04/1980-05','issue_period','A contemporary DFO staff newsletter article by BC conservation officer Andy Ackerman reports that COS had been removed from Fish and Wildlife Branch and become a separate enforcement agency for the entire Ministry of Environment. This bounds observation to the April–May issue; it is not an exact separation instrument.','R4B-003','VolumeVIII no3 April–May1980, printedpp10–11 / boundPDFpp46–47; issuecoverPDFp37',prior_parent='Fish and Wildlife Branch',new_parent='Ministry of Environment',instrument_found=False)
relation('conservation-officer-service','1980-09-18','day','part_of','Ministry of Environment','OIC2085/1980 confers statutory officer powers on listed regular employees of COS, Ministry of Environment. It is a powers/designation regulation, not the1980 reorganization instrument.','R4B-051','PDF pp1–2, regulation s1',date_kind='order_approved')
relation('conservation-officer-service','1980/81','reporting_period','part_of','Regional Operations Division, Ministry of Environment','Original extended-period annual report places Conservation Officer Service within Regional Operations Division.','R4B-014','Printedpp57–58; reportperiod1January1980–31March1981',observed_during={'start':'1980-01-01','end':'1981-03-31'})

# Sheriff statutes: office powers, territorial definitions, appointments and unit history are different events.
add('bc-sheriff-services','colonial_statutory_predecessor','1860-03-08','day','The Sheriff’s Act1860 proclamation regulates the High Sheriff of mainland British Columbia and temporary judicial appointments. It names Charles Samuel Nicol as late and Peter O’Reilly as present High Sheriff. It does not create nine county offices or divide both colonies into nine counties.','R4B-041','PDF pp1–2, especiallyss1–4 and issuance clause',historical_scope='Colony of British Columbia',use_as_modern_service_founding=False)
add('bc-sheriff-services','predecessor_appointment_authority','1873-02-21','day','Sheriffs Act1873 authorizes appointments for Vancouver Island, City of New Westminster and Cariboo. The recovered text is an official later historical compilation, not the original annual-chapter scan. The printed21February date was visually verified.','R4B-061','Compiledchapter146, printedp648 / PDFp1, s1',office_names=['Sheriff for Vancouver Island','Sheriff for the City of New Westminster','Sheriff for Cariboo'],date_kind='statutory_assent',not_actual_appointment_dates=True)
relation('historical-bc-sheriffs','1873-02-21','day','financial_accounts_reported_to','Minister of Finance and Agriculture','Section16 requires monthly sworn accounts of fines, penalties and forfeitures. This is a financial reporting duty, not proof of the sheriff’s full administrative parent.','R4B-061','Compiledchapter146, printedpp651–652 / PDFpp4–5, s16',entity_id_status='proposed_collective_historical_subject')
add('bc-sheriff-services','additional_predecessor_appointment_authority','1878-04-10','day','1878c17 authorizes distinct Nanaimo, Kootenay and Cassiar sheriffs and adjusts Vancouver Island and New Westminster jurisdiction. Authority to appoint is not evidence of the first actual appointment.','R4B-062','PDF p1 / printedp75, ss1–2',office_names=['Sheriff for Nanaimo','Sheriff for Kootenay','Sheriff for Cassiar'],date_kind='statutory_assent')
add('sheriff-clinton-judicial-district','conditional_statutory_authority','1880-05-08','day','1880c24 authorizes Clinton Judicial District sheriff and withdraws the district from New Westminster and Cariboo bailiwicks, butss1,2,4,5,7 require proclamation unders8. This is assent only; proclamation was not recovered.','R4B-063','PDFpp1–2 / printedpp71–72, ss1,7,8',entity_id_status='proposed_historical_node',commencement_unresolved=True)
for prior,current in [('Vancouver Island','County of Victoria'),('City of New Westminster','County of Westminster'),('Clinton Judicial District','County of Yale'),('Kootenay','County of Kootenay'),('Nanaimo','County of Nanaimo'),('Cariboo','County of Cariboo')]:
    add('sheriff-'+current.lower().replace('county of ','').replace(' ','-'),'office_continued_and_renamed','1888-04-28','day',f'1888c33 s2 explicitly continues the Sheriff for {prior} as Sheriff for the {current} on passage, subject to public-service appointment/removal law.','R4B-058','PDFp2 / printedp104, s2',prior_name='Sheriff for '+prior,new_name='Sheriff for the '+current,entity_id_status='proposed_historical_node',not_first_sheriff_in_region=True)
add('sheriff-cassiar','pending_process_transferred','1888-04-28','day','1888c33 s3 assigns pending process held by Sheriff for Cassiar to Sheriff for Nanaimo. This proves transfer of specified work; use together with the replacementbailiwickscheme, not as an unsupported asset-transfer certificate.','R4B-058','PDFp2 / printedp104, s3',successor_for_specified_work='Sheriff for Nanaimo',entity_id_status='proposed_historical_node')
add('sheriff-vancouver','conditional_statutory_authority','1892-04-23','day','1892c41 ss2–3 removes the newly defined County of Vancouver from Westminster sheriff jurisdiction and authorizes a Vancouver sheriff. Sections5 requires a commencement OIC; assent is not that commencement.','R4B-066','PDFpp1–2 / printedpp237–238, ss2–5',commencement_unresolved=True,entity_id_status='proposed_historical_node')
add('sheriff-vancouver','acting_sheriff_appointed','1892-10-26','day','OIC427/1892 appoints Thomas Joseph Armstrong acting Sheriff for County of Vancouver. OIC241/1893 explicitly identifies the earlier approval as26October1892; this is at-least-by operational office evidence.',['R4B-067','R4B-064'],'OIC427 pp1,4; OIC241 p1 cross-reference',entity_id_status='proposed_historical_node',not_first_appointment_proved=True)
add('sheriff-vancouver','sheriff_appointed','1893-07-03','day','OIC241/1893 appoints James Deacon Hall and cancels Armstrong’s acting appointment. Signed operative order date3July1893 visually verified; OCR incorrectly prints1897.','R4B-064','PDFp3',entity_id_status='proposed_historical_node')
add('historical-bc-counties','territorial_replacement_commencement_authorized','1895-10-01','day','OIC346/1895 approved2September1895 directs proclamation for1October1895 commencement of CountiesDefinitionAct1895. Actss5,8 replace separate court/sheriff districts with seven common counties and continue officers without further appointment. Gazette proclamation itself not recovered.',['R4B-059','R4B-046'],'OICpp1–2; ActPDFpp3–4 / printedpp33–34, ss5,8,10',entity_id_status='proposed_historical_territorial_scheme',not_sheriff_office_creation=True,proclamation_publication_not_retrieved=True)
add('county-atlin','territory_separated_from_vancouver','1905-03-08','day','1903–04c13 defines County of Atlin by removing territory from County of Vancouver; commencement is delayed until proclamation. OIC121/1905 directs a proclamation bringing the Act into force8March1905. This is county creation, not a sheriff appointment.',['R4B-055','R4B-068'],'ActPDFpp1–2, ss2–4; OICp1',entity_id_status='proposed_historical_territorial_node',proclamation_publication_not_retrieved=True)
add('county-prince-rupert','statutory_name_change','1920-04-17','day','1920c20 s2 makes all statutory, contractual and OIC references to County of Atlin references to County of Prince Rupert; s3 replaces relevant boundaries. This is a county-name bridge, not a first PrinceRupert sheriff appointment.','R4B-060','PDFp1 / printedp75, ss1–2',prior_name='County of Atlin',new_name='County of Prince Rupert',entity_id_status='proposed_historical_territorial_node',date_kind='assent_no_delayed_commencement_clause_in_act')
add('bc-sheriff-services','archival_target_identified','1977','year','A BC task-force report identifies FrankHodgson etal, Report of the Task Force on Sheriff Services (May1977), and JohnDogherty etal, Sheriff Services Program Inventory and Review (September1977), as source reports. These are concrete archival targets, not recovered consolidation instruments.','R4B-035','Appendix12 printedpp352–353 / PDFp239',not_a_substantive_merger_date=True,original_target_documents_retrieved=False)
add('bc-sheriff-services','rejected_instrument_candidate','1974-06-06','day','Attorney General expressly says Police Act Bill 91 has nothing to do with the new sheriff service. Do not use the 1974 Police Act as the sheriff-consolidation instrument.','R4B-011','Hansard printed p3809, Attorney General Macdonald response',instrument_status='rejected_false_lead')
add('bc-sheriff-services','heraldic_grant','2011-08-15','day','Governor General’s public register records arms, supporters, flag and badge granted15August2011; announcement in CanadaGazette24March2012. Grant and publication dates are distinct.','R4B-020','Public register project2209, volVIp64',work_item='H6',not_a_founding_date=True)

# Commission, plan operation, statutory commencement and staffing are distinct events.
add('medical-services-commission','enabling_act_assented','1967-03-23','day','Medical Services Act 1967 c24, s3 constitutes a Medical Services Commission. Section13 delays commencement of the substantive provisions to proclamation. Royal assent alone is therefore not the Commission’s effective creation date.','R4B-070','PDF p1 / printed p111, s3; PDF p5 / printed p115, s13',date_kind='statutory_assent',entity_kind='statutory_commission',use_as_founding_date=False)
add('medical-services-commission','statutory_commencement_authorized','1967-03-24','day','OIC964/1967, approved23March1967, directs a proclamation bringing all Medical Services Act provisions except s9 into force24March1967. This includes the constituting provision s3. The separate Gazette proclamation has not been retrieved.','R4B-072','PDF p1',date_kind='authorized_proclamation_effective_date',proclamation_publication_not_retrieved=True)
add('medical-services-commission','initial_members_appointed','1967-03-24','day','OIC965/1967 appoints Geoffrey Alexander Stewart as member and chairman, and Peter John Banks and Gerald Stewart Bryson as members. The order expressly comes into operation24March1967. The date and names were visually checked against the scan.','R4B-071','PDF p1',entity_kind='statutory_commission',date_kind='appointment_order_effective',recommended_first_observed='1967-03-24')
add('medical-services-commission','staff_transfer_provision_commencement_authorized','1967-03-25','day','OIC966/1967 separately directs a proclamation bringing s9 into force25March1967. That section provides managerial and administrative services for specified medical-insurance carriers and transfers their staff to the Commission. The order is distinct from the24March constituting provisions.',['R4B-073','R4B-070'],'OIC PDF p1; Act PDF p3 / printed p113, s9',date_kind='authorized_proclamation_effective_date',proclamation_publication_not_retrieved=True)
add('medical-services-commission','organizational_staff_establishment_effective','1967-03-25','day','OIC967/1967 expressly establishes the Commission’s listed civil-service positions effective25March1967. This is direct evidence of an operating administrative establishment well before the later1968 Medicare milestone.','R4B-078','PDF p1',date_kind='staff_establishment_order_effective',do_not_infer_minister_from_signature=True)
add('medical-services-commission','staff_establishment_increased','1968-05-15','day','OIC1518/1968 adds a Clerk-Stenographer2, Audit Accountant3 and Administrative Officer3 to the Commission’s organization effective15May1968. This corroborates the Commission’s existence before1July1968.','R4B-074','PDF p1',date_kind='staff_establishment_order_effective')
add('medical-services-commission','contemporary_public_announcement_sighting','1968-06-06','day','A full-page announcement issued in the name of the Medical Services Commission and chairman G.A.Stewart describes upcoming BC-Canada Medicare coverage on1July1968. The Commission itself was already issuing public instructions before that operational date.','R4B-075','Printed p11 / PDF p11',entity_kind='statutory_commission',source_authorship='Commission announcement in contemporaneous newspaper')
add('medical-services-commission','later_retrospective_date_conflict','2003/04','fiscal_year','The Commission’s financial-statement note says it was established1July1968. This later shorthand conflicts with the direct1967 commencement, appointment and staffing orders if treated as the first legal or organizational existence. Preserve it as a conflicting source statement; do not replace the dated1967 orders with it.','R4B-076','PDF/printed p6, note1',asserted_date='1968-07-01',status='conflicting_retrospective_statement',recommended_for_start_field=False)
relation('medical-services-commission','1967-03-24','day','members_appointed_by','Lieutenant Governor in Council','The constituting statute assigns appointment to Cabinet and the first appointment order exercises that power effective24March1967. This appointment relationship is separate from ministerial administration.',['R4B-070','R4B-071'],'Act PDF p1 / printed p111, s3; OIC PDF p1')
relation('medical-services-commission','2003/04','fiscal_year','deemed_division_for_financial_administration','Ministry of Health Services','Financial-statement note1 says the Financial Administration Act applies to the Commission as though it were a division of the Ministry of Health Services. This is a statute-specific accounting treatment, not proof that the Commission is an ordinary administrative branch.','R4B-076','PDF/printed p6, note1',not_general_organizational_parent=True)
add('medical-services-commission','original_statutory_accountability_scheme','1967-03-24','day','The original Act makes the Commission a Crown agent, permits Finance inspection, requires a Comptroller-General audit, and directs annual reporting through the designated minister to the Legislature. These are separate accountability relationships. The1967 ministerial designation itself remains unfound.',['R4B-070','R4B-072'],'Act PDF p2 / printed p112, ss6–8; OIC PDF p1',date_kind='authorized_commencement_date',unresolved_minister_designation=True)
add('historical-bc-sheriffs','annual_gazette_roster_statutory_lead','1890-04-26','day','Sheriffs Amendment Act1890 c45 s6 requires annual July Gazette publication of every sheriff’s name, post-office address and bailiwick limits. Section7 requires a commencement order. The provision identifies a promising roster series; neither its commencement nor the yearly rosters are recovered here.','R4B-065','PDF p2 / printed p244, ss6–7',date_kind='statutory_assent',entity_id_status='proposed_collective_historical_subject',commencement_unresolved=True)
relation('bc-sheriff-services','1978-07','month','administered_by','Director of Court Services','The municipal-policing task force’s contemporary program review says Sheriff Services is one of three services administered by the Director of Court Services. It describes six justice regions, each administered by a regional manager; regional sheriffs report to that manager. This is a bounded organizational observation from the1978 review, not the missing1974 consolidation order.','R4B-035','PDF p242 / printed p356, Appendix12 sectionD Administration',evidence_kind='contemporaneous_task_force_program_review')

# Make prose fields readable while preserving machine identifiers and source paths.
def prose(s):
    replacements={
        'CanadaGazette':'Canada Gazette', 'MedicalServicesPlan':'Medical Services Plan',
        'MarineBranch':'Marine Branch', 'WaterRightsBranch':'Water Rights Branch',
        'WaterManagementBranch':'Water Management Branch', 'ChiefRiskOfficer':'Chief Risk Officer',
        'TomasErnst':'Tomas Ernst', 'ContemporaneousMCFD':'Contemporaneous MCFD',
        'County of PrinceRupert':'County of Prince Rupert', 'PrinceRupert':'Prince Rupert',
        'CountiesDefinitionAct':'Counties Definition Act', 'FrankHodgson':'Frank Hodgson',
        'JohnDogherty':'John Dogherty', 'etal':'et al.', 'sectioncover':'section cover',
        'exactpageimage':'exact page image', 'OkanaganLakephotographs':'Okanagan Lake photographs',
        'sectionbeginning':'section beginning', 'precedinghistory':'preceding history',
        'replacementbailiwickscheme':'replacement bailiwick scheme', 'beforephotos':'before photos',
        'firstpage':'first page', 'Coverletter':'Cover letter', 'reportperiod':'report period',
        'issuecover':'issue cover', 'boundPDF':'bound PDF', 'Compiledchapter':'Compiled chapter',
        'webcategory/programfamily':'web category/program family', 'policyamendmentlog':'policy amendment log',
        'oldstructure':'old structure', 'newstructure':'new structure', 'tableitem':'table item',
        'G.A.Stewart':'G. A. Stewart', 'atII':'at II', 'beforeII':'before II',
        'andII':'and II', 'introductionII':'introduction II', 'VolumeVIII':'Volume VIII',
        'volVIp':'vol. VI p', 'ministryprofile':'ministry profile', 'publicationsfollowing':'publications following'
    }
    for a,b in replacements.items():s=s.replace(a,b)
    s=re.sub(r'\b(OIC)(?=\d)',r'\1 ',s)
    s=re.sub(r'\b(\d{4})c(\d+)',r'\1 c. \2',s)
    s=re.sub(r'(?<=[a-z])(?=\d)', ' ', s)
    s=re.sub(r'(?<=\d)(?=[A-Z])', ' ', s)
    s=re.sub(r'(?<=\d)(?=(?:as|is|was|are|were|year|years|date|dates|name|names|old|new|policy|agenda|budget|report|force|commencement)\b)', ' ', s)
    s=re.sub(r'(?<![A-Za-z])s(?=\d)', 's ', s)
    s=re.sub(r'\bPDF(?=p)', 'PDF ', s)
    s=re.sub(r'\b(printed|Printed)(?=pp?|II)',r'\1 ',s)
    s=re.sub(r'\b(pp?|ss?)(?=\d)',r'\1 ',s)
    return s
for c in claims:
    for k in ['meaning','locator']:
        c[k]=prose(c[k])
    c['evidence_role']={
        'rejected_instrument_candidate':'negative_evidence',
        'archival_target_identified':'archival_lead',
        'annual_gazette_roster_statutory_lead':'archival_lead',
        'later_retrospective_date_conflict':'conflicting_source_statement'
    }.get(c['type'],'substantive_historical_finding')

# No new claim is made for already settled EAB/Powertech or the prior GCRO October2012 policy-log statement.
(B/'claims.json').write_text(json.dumps(claims,indent=2,ensure_ascii=False))
for s in sources:
    used=[c['id'] for c in claims if s['id'] in c['source_ids']]
    s['claim_ids']=used
    s['used_for_accepted_claims']=any(c['id'] in used and c['evidence_role']=='substantive_historical_finding' for c in claims)
    s['evidence_roles']=sorted(set(c['evidence_role'] for c in claims if c['id'] in used)) or ['screened_candidate_not_used']
    if s['id']=='R4B-061':s['title']='Sheriffs Act1873 in official historical compilation, chapter146'
    if s['id']=='R4B-072':s['title']='OIC964/1967 authorizing Medical Services Act commencement except section9'
    if s['id']=='R4B-073':s['title']='OIC966/1967 authorizing Medical Services Act section9 commencement'
    if s['id']=='R4B-078':s['title']='OIC967/1967 Medical Services Commission organizational establishment'
    if s['id']=='R4B-076':s['title']='Medical Services Commission financial statement for year ended31March2004'
    s['title']=prose(s['title'])
    if s.get('local_file'):
        f=B/s['local_file']
        if f.is_file():
            s['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
            s['bytes']=f.stat().st_size
(B/'sources.json').write_text(json.dumps(sources,indent=2,ensure_ascii=False))

baseline=json.loads((B/'prior/remaining-undated.json').read_text())
dated={
 'buy-bc':('1993','program_launch','program'),
 'bc-training-and-education-savings-program':('2013-03-20','named_program_regulation_made','program_and_distinct_special_account'),
 'disaster-financial-assistance':('1995','program_established','program'),
 'provincial-treasury':('1986-04-10','existence_sighting','administrative_division'),
 'building-and-safety-standards':('2014-05-20','existence_sighting','administrative_branch'),
 'community-capital-development':('2025-03-17','existence_sighting','administrative_division'),
 'infrastructure-policy-and-partnerships':('2025-03-17','existence_sighting','administrative_division'),
 'community-safety-and-victim-services':('2024','existence_sighting','administrative_branch'),
 'safe-campuses-bc':('2019-08-29','named_web_resource_sighting','public_information_resource'),
 'connectivity-in-bc':('2021-04-07','named_web_resource_sighting','public_information_resource'),
 'lets-go-bc':('2025-04-23','official_mark_publication','campaign_brand'),
 'bc-arts-and-culture-endowment':('2008-03-31','statutory_special_account_established','statutory_special_account'),
 'building-bc':('2018/19','program_family_sighting','program_family'),
 'trans-care-bc':('fall 2015','program_established','health_program'),
 'bc-mental-health-and-substance-use-services':('2015-12-17','existence_sighting','health_service_program'),
 'medical-services-commission':('1967-03-24','initial_members_appointed','statutory_commission'),
}
old_dated={x:('2009/10','health_service_program') for x in ['bc-centre-for-disease-control','bc-childrens-hospital','bc-womens-hospital','perinatal-services-bc']}
old_dated['health-care-practitioners-special-committee-for-audit-hearings']=('2024-06-30','statutory_committee')
unresolved={
 'bc-agriculture-insurance-and-income-protection':'The label is a collection of insurance/income programs. Histories of individual schemes do not establish one umbrella organization; no dated organizational identity found.',
 'children-and-youth-with-support-needs':'ContemporaneousMCFD service references are function descriptions; named organizational unit and any rename from special needs remain to be verified.',
 'mcfd-adoption-services':'Earlier reports describe adoption services, but a distinct branch matching the repository node has not been established. Classify as a service or locate an organization chart.',
 'foster-caregiving-and-kinship-care':'Current webcategory/programfamily; no historical administrative unit with this exact identity proved.',
 'disaster-resilience-division':'20April2026Hansard names ADM TomasErnst and this division. This does not establish existence before2026; predecessor Disaster Risk Management/Recovery division mapping is unresolved.',
 'government-chief-risk-office':'The October 2012 policy amendment log was already in Round 3 as a retrospective statement. A 2016 agenda names the Chief Risk Officer but does not prove identity/creation of a separate Office. No new accepted historical-office sighting.',
 'government-to-government-and-community-relations-division':'29April2025Hansard still lists Negotiations and Regional Operations, Reconciliation Transformation and Strategies, and Strategic Initiatives and Partnerships. Current2026names cannot be backdated using restated2025budget columns.',
 'policy-intergovernmental-relations-and-legislation-division':'Same2025oldstructure/2026newstructure problem; a dated reorganization chart or transfer directive remains needed.',
 'programs-and-partnerships-division':'Same2025oldstructure/2026newstructure problem; do not equate an old unit just because functions are similar.',
 'inland-ferries':'Service network is distinct from its MarineBranch manager. Historic ferry operation dates are not a single branch founding date.',
 'water-licensing-and-rights':'Website service category is not proved to be a standalone unit; WaterRightsBranch/WaterManagementBranch history requires an explicit identity bridge.',
 'planning-in-partnership':'Modern land-use-policy dates do not prove the named website/resource start or a separate administrative body.',
}
rows=[]
for old in baseline:
    bid=old['id'];row={'body_id':bid,'name':old['name'],'baseline_start':None,'baseline_first_observed':None,'full_history_complete':False}
    if bid in dated:
        d,t,k=dated[bid];row.update(disposition='new_dated_evidence',recommended_date=d,date_meaning=t,entity_kind=k,claim_ids=[c['id'] for c in claims if c['body_id']==bid])
        row['integration_gate']='Preserve correct entity kind and date meaning; no perpetual parent inferred'
        if k in ['public_information_resource','campaign_brand','statutory_special_account','program_family']:
            row['integration_gate']='Requires resource/account/program-family type; do not draw as a ministry branch'
    elif bid in old_dated:
        d,k=old_dated[bid];row.update(disposition='prior_cross_module_date_integration',recommended_date=d,entity_kind=k,claim_ids=[c['id'] for c in claims if c['body_id']==bid],integration_gate='Reuse cited previous-package evidence; do not count as new archival discovery')
    else:
        row.update(disposition='still_no_accepted_pre2026_date',reason=prose(unresolved[bid]))
    rows.append(row)
coverage={'baseline':'Round3 remaining-undated.json,33records from held59itemWANTED baseline','baseline_count':len(rows),'counts':dict(Counter(x['disposition'] for x in rows)),'new_dated_ids':[x['body_id'] for x in rows if x['disposition']=='new_dated_evidence'],'cross_module_ids':[x['body_id'] for x in rows if x['disposition']=='prior_cross_module_date_integration'],'remaining_undated_ids':[x['body_id'] for x in rows if x['disposition']=='still_no_accepted_pre2026_date'],'claim_count':len(claims),'claim_counts_by_novelty':dict(Counter(c['novelty'] for c in claims)),'historical_parent_policy':'A dated observation supports only the stated checkpoint or explicit effective change, not all intervening years. Statutory reporting, program administration, legal ownership and ministry membership are separate relations.','rows':rows,'unresolved_instruments':['1974 sheriff administrative consolidation instrument','first actual appointment for every county sheriff office, especiallyCariboo split','1880Clinton commencement proclamation','1892Vancouver sheriff amendment commencement OIC','Gazette proclamation publications followingOIC346/1895 andOIC121/1905','1957ParksBranch signed implementing instrument (effective transferdate1April1957 now documented)','1980COS separation directive (contemporaryApril–May1980observation now documented)','WildfireManagementBranch administrative rename order (prior6June2015date remains documentedit only)','SurveyorGeneral2019 exact dated internal split instrument'], 'saturation_statement':'Targeted public-source pass with original statutes, OICs, contemporary newsletters, audited reports, transition binders and both search engines. Missing instruments remain explicitly open; not a claim of exhaustive archival search.'}
coverage['baseline']='Round 3 remaining-undated.json: 33 records from the held 59-item WANTED baseline'
coverage['counts_note']='21 of the 33 records now have dated evidence: 16 new findings and 5 integrations of evidence already held in other prior-package modules. These are not 21 newly discovered branch founding dates. Twelve remain without an accepted pre-2026 date.'
coverage['claim_counts_by_evidence_role']=dict(Counter(c['evidence_role'] for c in claims))
coverage['unresolved_instruments']=[
    '1974 sheriff administrative consolidation instrument',
    'First actual appointment for every county sheriff office, especially the Cariboo split',
    '1880 Clinton commencement proclamation',
    '1890 annual sheriff-roster provision commencement order and annual Gazette rosters',
    '1892 Vancouver sheriff amendment commencement OIC',
    'Gazette proclamation publications following OIC346/1895 and OIC121/1905',
    '1957 Parks Branch signed implementing instrument; effective transfer date1April1957 is now documented',
    '1980 COS separation directive; a contemporary April–May1980 observation is now documented',
    'Wildfire Management Branch administrative rename order; prior6June2015 date remains documented without the order',
    'Surveyor General2019 exact dated internal split instrument',
    'Medical Services Act1967 Gazette proclamations following OIC964/1967 and OIC966/1967; appointment and staffing orders are recovered',
    'Medical Services Act1967 initial ministerial designation'
]
coverage['unresolved_instruments']=[prose(x) for x in coverage['unresolved_instruments']]
(B/'coverage.json').write_text(json.dumps(coverage,indent=2,ensure_ascii=False))
(B/'remaining-undated.json').write_text(json.dumps([x for x in rows if x['disposition']=='still_no_accepted_pre2026_date'],indent=2,ensure_ascii=False))
print(json.dumps({'claims':len(claims),'coverage':coverage['counts'],'sources':len(sources)},indent=2))
