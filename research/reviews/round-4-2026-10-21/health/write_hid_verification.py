from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parent
R=B.parent/'root'
sources={s['id']:s for s in json.loads((R/'sources.json').read_text())}
# id, exact original name (punctuation normalized), date, witness page(s), name page,
# governance page, trustees, zones, allocation, annual voter pages, authority profile, later label, transferee
raw=[
(119,'Omineca and Nechako Valley Hospital Improvement District No. 32','1961-10-24',[12],4,8,7,7,'One trustee from each zone.',[10],'s53_1960',None,'Bulkley-Nechako Regional Hospital District'),
(120,'Gulf Islands Hospital Improvement District No. 9','1955-05-14',[6],2,2,5,None,'Five elected trustees; no more than two from Salt Spring Island.',[4,5],'s50_1953',None,'Capital Regional Hospital District'),
(121,'Creston Valley Hospital Improvement District','1951-08-07',[5],3,3,3,None,'Three elected trustees, initially staggered through 1952, 1953 and 1954.',[4],'s50_1951','Creston Valley Hospital Improvement District No. 1','Central Kootenay Regional Hospital District'),
(142,'Castlegar Hospital Improvement District','1954-05-12',[6],2,3,5,3,'Two trustees each from zones 1 and 2; one from zone 3.',[4,5],'s50_1953','Castlegar Hospital Improvement District No. 3','Central Kootenay Regional Hospital District'),
(123,'Kootenay Valley Hospital Improvement District','1954-05-28',[10],2,8,7,6,'Two trustees from Industrial Zone 6; one from each other zone.',[9],'s50_1953','Kootenay Valley Hospital Improvement District No. 4','Central Kootenay Regional Hospital District'),
(124,'Kelowna and District Hospital Improvement District No. 36','1964-04-23',[10],4,7,8,4,'Two trustees from each zone.',[9],'s53_1960',None,'Central Okanagan Regional Hospital District'),
(150,'Shuswap Lake Hospital Improvement District No. 14','1956-05-29',[10],3,7,7,6,'Two trustees from zone 3; one from each other zone.',[8,9],'s50_1953',None,'Columbia-Shuswap Regional Hospital District'),
(126,'Revelstoke Hospital Improvement District No. 26','1959-09-04',[9,10],3,6,5,4,'Two trustees from zone 3; one from each other zone.',[8],'s50_1953',None,'Columbia-Shuswap Regional Hospital District'),
(127,'Ladysmith and District Hospital Improvement District No. 33','1962-05-17',[9],3,5,5,4,'Two trustees from zone 1; one from each other zone.',[7],'s53_1960',None,'Cowichan Valley Regional Hospital District'),
(160,'Windermere District Hospital Improvement District','1954-08-11',[7],2,4,6,6,'One trustee from each zone.',[5,6],'s50_1953','Windermere Hospital Improvement District No. 7','East Kootenay Regional Hospital District'),
(144,'Selkirk Hospital Improvement District No. 12','1956-02-21',[6],2,3,5,5,'One trustee from each zone.',[5],'s50_1953',None,'East Kootenay Regional Hospital District'),
(130,'Prince George and District Hospital Improvement District No. 10','1955-10-04',[8],2,4,5,4,'Two trustees from zone 4; one from each other zone.',[6,7],'s50_1953','Prince George Hospital Improvement District No. 10','Fraser-Fort George Regional Hospital District'),
(161,'Boundary Hospital Improvement District No. 29','1960-11-10',[10],4,6,5,4,'Two trustees from zone 3; one from each other zone.',[8,9],'s50_1948',None,'Kootenay Boundary Regional Hospital District'),
(132,'Lower Columbia Hospital Improvement District No. 34','1963-12-23',[8],3,5,6,3,'Two trustees from each zone.',[7],'s53_1960',None,'Kootenay Boundary Regional Hospital District'),
(159,'South Central Vancouver Island Hospital Improvement District No. 20','1958-06-02',[13],3,9,7,7,'One trustee from each zone.',[11,12],'s50_1953',None,'Nanaimo Regional Hospital District'),
(134,'North Peace Hospital Improvement District No. 13','1956-05-08',[7],2,4,7,5,'Three trustees from zone 4; one from each other zone.',[5,6],'s50_1953',None,'Peace River Regional Hospital District'),
(135,'Garibaldi Hospital Improvement District No. 23','1959-02-18',[10],3,7,5,5,'One trustee from each zone.',[8,9],'s50_1953',None,'Squamish-Lillooet Regional Hospital District'),
(136,'Lillooet Hospital Improvement District No. 11','1955-12-09',[8],3,5,5,4,'Two trustees from zone 3; one from each other zone.',[6,7],'s50_1953',None,'Squamish-Lillooet Regional Hospital District'),
(137,'Sunshine Coast Hospital Improvement District No. 31','1961-03-14',[10],3,7,7,4,'Zone 1 elects one; zone 2 three; zone 3 two; zone 4 one.',[9],'s53_1960',None,'Sunshine Coast Regional Hospital District'),
(147,'Thompson Valleys Hospital Improvement District No. 27','1960-05-31',[9],3,5,7,5,'Three trustees from zone 4; one from each other zone.',[7],'s50_1948',None,'Thompson-Nicola Regional Hospital District'),
(151,'Fraser Canyon Hospital Improvement District','1955-01-28',[7],3,4,5,3,'Two trustees from Hope (zone 1), two from Yale/Spuzzum (zone 2), one from Flood (zone 3).',[6],'s50_1953','Fraser-Canyon Hospital Improvement District No. 8','Fraser-Cheam Regional Hospital District'),
(148,'Cariboo Hospital Improvement District','1953-03-31',[6],2,3,5,4,'Two trustees from Quesnel (zone 1); one from each other zone.',[4,5],'s50_1951','Cariboo Hospital Improvement District No. 2','Cariboo Regional Hospital District'),
(149,'Central Cariboo Hospital Improvement District No. 22','1958-12-16',[13],4,9,7,6,'Two trustees from Williams Lake (zone 6); one from each other zone.',[11],'s50_1953',None,'Cariboo Regional Hospital District')
]
authorities={
's53_1960':{'statute':'Water Act','citation':'RSBC 1960, c.405','section':'53'},
's50_1948':{'statute':'Water Act','citation':'RSBC 1948, c.361','section':'50','note':'Original order states section 50 of the 1948 Act without separately reciting the amendment in the authority clause.'},
's50_1951':{'statute':'Water Act','citation':'RSBC 1948, c.361','section':'50','amendment_as_recited':'Water Act Amendment Act, 1951, SBC 1951, c.88, s.7'},
's50_1953':{'statute':'Water Act','citation':'RSBC 1948, c.361','section':'50','amendment_as_recited':'Section 5 of the Water Act Amendment Act, 1953 (Second Session). Most orders also give SBC 1953 (Second Session), c.38.'}
}
franchise={
'id':'original_lp_annual_voters_21_citizen_land',
'conditions':['Canadian citizen','At least 21 years old','Eligible to register as a voter under the Provincial Elections Act','Owner of land within the relevant district or electoral zone, or authorized agent of a board/corporation that owns such land, or a specified legal representative of a landowner'],
'legal_representatives_as_described':'Representatives of an owner who has died, become insolvent, or been adjudged within the historical mental-incapacity wording of the instrument.',
'candidate_rule_default':'Qualified voters are also eligible trustee candidates, subject to instrument-specific exceptions below.',
'limits':'This is the rule in each original Letters Patent at its date. Later amendments were not exhaustively reviewed. It is not a universal provincial-population electorate. Provincial-voter eligibility is a cross-reference, not an independent reconstruction of all residence or franchise exclusions.'
}
entries=[]
for n,name,dt,wp,np,gp,nt,nz,alloc,vp,ap,later,trans in raw:
 sid=f'R4R-{n:03}';s=sources[sid]
 annual_clause=8 if n==121 else 10 if n==151 else 9
 gov_clause=4 if n in [120,121] else 5
 voter_first_clause=5 if n in [120,121] else 6
 row={
 'source_id':sid,'source_url':s['url'],'source_local_file':f'../root/raw/{sid}.pdf','source_sha256':s['sha256'],
 'original_corporate_name':name,'name_pinpoint':f'PDF p.{np}, Letters Patent clause 2',
 'incorporation_date':dt,'date_precision':'day','order_approval_date':dt,'letters_patent_witness_date':dt,
 'date_basis':'Operative incorporation in the attached Letters Patent, dated in the witness clause; date agrees with the order cover. Not a petition, plebiscite, later reissue, or retrospective annotation date.',
 'date_pinpoint':{'pdf_pages':wp,'clause':'Letters Patent witness clause'},'date_verification':'visually_verified_original_witness_clause','witness_image':f'hid-review/{sid}-witness.png',
 'statutory_authority':authorities[ap],'authority_pinpoint':'PDF pp.1–2, recommendation and Letters Patent preamble',
 'governance':{'trustee_count':nt,'zone_count':nz,'selection':'Elected by qualified district/zone electors at general meetings.','seat_allocation':alloc,'board_pinpoint':f'PDF p.{gp}, clause {gov_clause}','elector_profile':franchise['id'],'first_election_clause':voter_first_clause,'annual_elector_clause':annual_clause,'annual_elector_pinpoint':{'pdf_pages':vp},'minutes_and_financial_reports_filed_with':'Comptroller of Water Rights'},
 'objects_summary':'Financial assistance for hospital development, equipment, operation and related purposes; exact objects vary. This is not by itself proof that the district directly operated a hospital.',
 'later_1969_name':later or name,'name_bridge_status':'later_label_differs_no_rename_instrument_recovered' if later else 'same_substantive_name',
 'dissolution':{'date':'1969-09-25','date_basis':'OIC 3082/1969 operative dissolution and transfer, approved 25 September 1969; no future commencement date stated.','source_id':'R4R-115','pinpoint':'PDF pp.1–2, operative recommendation and schedule','successor_transferee_as_printed':trans,'relationship':'assets_rights_claims_obligations_liabilities_transferred_to'},
 'review_status':'confirmed_original_incorporation',
 'limitations':['Geographic boundary descriptions were not independently geospatially checked.','Original governance rules are dated observations, not a claim that no subsequent amendments occurred.']
 }
 if later: row['limitations'].append('Retain the original name and later source label separately. Do not invent the date or instrument adding a district number or changing wording.')
 if n==120:
  row['governance']['specific_rules']=['Voters whose lands are outside Salt Spring Island may vote by proxy (clauses 5 and 9; PDF pp.3,5).','Trustees normally hold until the next annual general meeting (clause 4; PDF p.2).']
  row['visual_checks']=['Handwritten witness date: 14 May 1955.','Proxy wording at PDF p.5 visually checked.']
 if n==121:
  row['governance']['specific_rules']=['Trustee candidate qualification extends to the wife or husband of a qualified voter; this does not itself give the spouse a vote (clauses 5 and 8; PDF pp.3–4).','First-election voter clause lists owners; annual voter clause expressly includes authorized corporate agents and specified personal representatives.']
  row['formation_note']='Order cover reports petition support from 45% of landowners and an express Minister of Health and Welfare recommendation to incorporate nonetheless (PDF p.1).'
  row['visual_checks']=['Witness date and annual spouse-candidate wording visually checked.']
 if n==160: row['visual_checks']=['Original name and witness date visually checked.']
 if n==130: row['visual_checks']=['Original name includes and District; handwritten witness date is 4 October 1955, visually checked.']
 if n==134: row['limitations'].append('R4R-115 prints Peace River Regional Hospital District. Do not silently expand to Peace River-Liard or infer a rename without supporting evidence.')
 entries.append(row)
fort={
 'original_incorporation':{
  'source_id':'R4R-154','source_url':sources['R4R-154']['url'],'original_corporate_name':'Fort Nelson Hospital Improvement District No. 21',
  'incorporation_date':'1958-06-07','date_precision':'day','date_basis':'Letters Patent witness clause, PDF p.8, visually verified; later 1959 and 1972 instruments expressly corroborate issuance on 7 June 1958.',
  'name_pinpoint':'PDF p.3, clause 2','statutory_authority':authorities['s50_1953'],'authority_pinpoint':'PDF pp.1–2',
  'governance':{'trustee_count':5,'zone_count':4,'seat_allocation':'Two trustees for zone 3; one for each other zone.','initial_selection':'Five first trustees named in the Letters Patent, clause 6; initial board was appointed, not elected.','subsequent_selection':'Elections at annual zone meetings; clause 8.','board_pinpoint':'PDF p.5, clauses 5–7','elector_profile':franchise['id'],'elector_pinpoint':'PDF pp.6–7, clause 8','candidate_exception':'Hospital employees and physicians actively practising medicine were disqualified as trustee candidates; this clause does not by itself remove a qualified person’s vote.','hospital_board':'Trustees plus the Hospital Act s.5 appointee constitute the hospital board of management.','hospital_board_pinpoint':'PDF p.5, clause 7'},
  'objects':'Hospital services, acquisition, ownership, maintenance and operation of a hospital and related land; clause 3, PDF p.3.',
  'visual_checks':['Witness date (p.8)','Candidate exception (p.7)']
 },
 'replacement_letters_patent':{
  'source_id':'R4R-155','source_url':sources['R4R-155']['url'],'date':'1959-07-07','date_precision':'day','date_basis':'Witness clause at PDF p.6, visually checked; cover approved 7 July 1959.',
  'event_type':'continuation_and_replacement_of_letters_patent','not_new_incorporation':True,
  'continuation_pinpoint':'PDF p.2, clause 1 expressly continues incorporation.','statutory_authority':{'statute':'Water Act','citation':'RSBC 1948, c.361','section':'51'},
  'change':'Five trustees elected from the district as a whole; zonal allocation removed. Ambulance services added to objects.','pinpoints':['PDF p.1 recitals','PDF p.3 clauses 4–7'],
  'governance':{'trustee_count':5,'zone_count':None,'elector_profile':franchise['id'],'elector_pinpoint':'PDF p.4, clause 7, visually checked.','candidate_rule':'All qualified voters eligible; the prior instrument’s employee/physician candidate exception is absent from this replacement clause.','hospital_board':'Trustees plus Hospital Act s.5 appointee constitute hospital board of management (PDF p.3, clause 6).'},
  'limitation':'This verifies the replacement clause, not the effect of any separately applicable disqualification in another statute.'
 },
 'dissolution_and_transfer':{
  'source_id':'R4R-118','source_url':sources['R4R-118']['url'],'order':'OIC 2251/1972','order_approval_date':'1972-06-13','effective_date':'1972-06-13','date_basis':'Operative clause expressly makes dissolution effective on the date of the order.','statutory_authority':'Regional Hospital Districts Act, s.50C','pinpoint':'PDF pp.1–2',
  'direct_transferee':'Peace River-Liard Regional Hospital District',
  'onward_transfer':{'to':'Fort Nelson Hospital Society','resolution_date':'1972-05-23','effective_trigger':'As and from the date of dissolution of the improvement district.','effective_date_from_trigger':'1972-06-13','pinpoint':'PDF p.4, certified RHD resolution','exception':'Fundraising, disbursement and long-term debt obligations previously assumed by the regional hospital district remain with it.','caution':'Attached resolution authorizes appropriate conveyances. The actual signed deeds are not attached.'},
  'society_registration_date_reported':'1971-10-18','society_registration_basis':'Order recital, PDF p.1; not an independently retrieved registry certificate.',
  'ambulance_resolution':{'date':'1972-03-23','pinpoint':'PDF p.3, hospital society board resolution','effect':'Accepts ambulance-service responsibility as ancillary hospital operation; includes insurance commitments and incorporates 26 May 1970 agreement; resolution expires 31 March 1973.'}
 }
}
conflicts=[
 {'type':'original_name_vs_later_label','affected_source_ids':['R4R-121','R4R-142','R4R-123','R4R-160','R4R-130','R4R-151','R4R-148'],'finding':'Seven original names differ from the 1969 schedule. Six original letters omit the later district number. Windermere also uses Windermere District Hospital; Prince George uses and District. Fraser Canyon later appears hyphenated and numbered.','action':'Store dated source labels and leave any intervening renaming/numbering date unproved. These differences are not evidence of a separate incorporation.'},
 {'type':'recipient_label_variation','source_ids':['R4R-115','R4R-118'],'finding':'The 1969 North Peace transfer row prints Peace River Regional Hospital District; the 1972 Fort Nelson transfer names Peace River-Liard Regional Hospital District.','action':'Preserve source wording; do not infer a formal rename from these labels alone.'},
 {'type':'handwritten_OCR_dates','affected_source_ids':['R4R-120','R4R-130','R4R-136'],'finding':'Handwritten witness dates read 14 May 1955, 4 October 1955 and 9 December 1955 respectively. Text extraction is unreliable for these entries.','action':'Use visually verified witness readings.'},
 {'type':'original_vs_reissued_letters','source_ids':['R4R-154','R4R-155','R4R-118'],'finding':'Fort Nelson began 7 June 1958. Its 7 July 1959 letters expressly continued the incorporation; they did not start a new entity.','action':'Represent a continuation/governance change, then the 13 June 1972 dissolution and transfer.'},
 {'type':'historical_governance_scope','finding':'Landowner and representative voting qualifications, spouse candidate provisions and occupation-based candidate exceptions differ across instruments.','action':'Do not collapse these into a modern universal electorate or treat candidate exclusions as voter exclusions.'}
]
result={'prepared_on':'2026-10-21','reviewer':'health_round4','purpose':'Independent verification requested by root of existing R4R source originals. Root owns A8 source catalogue and integration; this file does not allocate duplicate R4H claims.','method':'Read original PDFs and text. Visually checked all 23 original Letters Patent witness clauses, plus Fort Nelson 1958 and 1959; visually checked material name/governance ambiguities and the 1969 transfer schedule. The PDF boundaries were read as legal descriptions but not mapped.','counts':{'originals_in_1969_schedule':23,'fort_nelson_originals_and_reissue':2,'dissolution_sources':2,'original_witness_dates_visually_verified':25,'original_name_variations_against_1969_schedule':7},'common_elector_profile':franchise,'incorporations':entries,'fort_nelson':fort,'conflicts_and_cautions':conflicts,'source_catalogue_untouched':True}
(B/'hid-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# Hospital improvement district verification','', 'All 23 original incorporation dates below were visually verified against the Letters Patent witness clauses. Sources are existing root R4R records; no duplicate source IDs were created. These districts are the 23 dissolved/transferred by OIC 3082/1969 on 25 September 1969.','', '| Original name | Original LP date | Source |','|---|---|---|']
for x in entries: lines.append(f"| {x['original_corporate_name']} | {x['incorporation_date']} | {x['source_id']} |")
lines+=['','## Findings affecting interpretation','','Seven original names differ from the 1969 schedule. Keep the original names: Creston Valley, Castlegar, Kootenay Valley, Fraser Canyon and Cariboo initially lack their later numbers; Windermere initially is **Windermere District Hospital Improvement District**; Prince George initially includes **and District**. The exact intervening rename/numbering instruments are not established by this review.','','These are Water Act improvement districts with elected landowner governance. The original voter rules require Canadian citizenship, age 21+, eligibility under the Provincial Elections Act, and land ownership or authorized representation. The JSON supplies each district’s trustee count, zonal allocation, clause and page. It does not treat this electorate as all residents or infer a ministry-parent edge merely from a minister’s signature.','','Three specific rules matter: Gulf Islands permits proxies for qualified voters with land outside Salt Spring Island; Creston extends trustee candidacy to qualified voters’ spouses without thereby enfranchising them; Fort Nelson’s 1958 letters appoint the first trustees and bar hospital employees and practising physicians from later trustee candidacy.','','Fort Nelson begins **7 June 1958**, is continued by replacement letters on **7 July 1959**, and ends **13 June 1972**. The 1959 letters move to district-wide elections and include ambulance service. The 1972 order transfers the district’s assets and liabilities to Peace River-Liard RHD; its attached 23 May 1972 resolution provides an onward transfer to the hospital society on dissolution, with specified debt/fundraising obligations retained. The signed conveyances are not attached.','','The 1969 North Peace row instead labels its transferee **Peace River Regional Hospital District**. Preserve this source variation unless a formal naming bridge is available.','','Full findings, provenance, pinpoints and limitations: `hid-verification.json`.']
(B/'hid-verification.md').write_text('\n'.join(lines)+'\n')
print('Wrote 23 original incorporations, Fort Nelson chronology and 5 conflict/caution groups.')
