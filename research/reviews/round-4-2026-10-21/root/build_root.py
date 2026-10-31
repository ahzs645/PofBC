"""Build the reviewed Round 4 hospital-district / commencement research tables.

This script assembles research; it does not mutate the PofBC repository.
"""
from pathlib import Path
import json, re

BASE = Path(__file__).resolve().parent
claims, entities, relationships, events, conflicts = [], [], [], [], []

def sid(n): return f'R4R-{n:03d}'
def emit(subject, kind, date, statement, sources, locator, items=('A8',), **kw):
    evidence_type = kw.pop('evidence_type_override', 'original_instrument')
    c = dict(id=f'R4RC-{len(claims)+1:03d}', item_ids=list(items), subject=subject,
             event_type=kind, date=date, date_precision='day' if date and len(date)==10 else ('year' if date else None),
             statement=statement, source_ids=[sid(s) if isinstance(s,int) else s for s in sources],
             locator=locator, evidence_type=evidence_type, confidence='high',
             import_status='review_and_convert', **kw)
    claims.append(c); return c['id']

originals = [
 ('alberni-clayoquot','Alberni-Clayoquot','1967-07-07',20),
 ('bulkley-nechako','Bulkley-Nechako','1967-08-22',75),
 ('capital','Capital','1967-10-17',14),
 ('cariboo','Cariboo','1968-07-16',11),
 ('central-fraser-valley','Central Fraser Valley','1967-10-12',25),
 ('central-kootenay','Central Kootenay','1967-07-11',12),
 ('central-okanagan','Central Okanagan','1967-08-24',16),
 ('columbia-shuswap','Columbia-Shuswap','1967-07-07',21),
 ('comox-strathcona','Comox-Strathcona','1967-12-08',8),
 ('cowichan-valley','Cowichan Valley','1967-09-26',61),
 ('dewdney-alouette','Dewdney-Alouette','1967-10-27',24),
 ('east-kootenay','East Kootenay','1967-07-07',18),
 ('fraser-cheam','Fraser-Cheam','1967-09-29',26),
 ('fraser-fort-george','Fraser-Fort George','1967-07-11',13),
 ('greater-vancouver','Greater Vancouver','1967-06-29',7),
 ('kootenay-boundary','Kootenay Boundary','1967-07-13',22),
 ('mount-waddington','Mount Waddington','1968-02-16',65),
 ('nanaimo','Nanaimo','1967-08-24',17),
 ('north-okanagan','North Okanagan','1967-08-24',15),
 ('ocean-falls','Ocean Falls','1968-07-25',66),
 ('okanagan-similkameen','Okanagan-Similkameen','1967-07-07',73),
 ('peace-river','Peace River','1967-10-31',79),
 ('malaspina','Malaspina','1967-12-19',62),
 ('skeena-a','Skeena A','1967-08-17',27),
 ('skeena-b','Skeena B','1967-09-14',28),
 ('squamish-lillooet','Squamish-Lillooet','1968-10-08',23),
 ('sunshine-coast','Sunshine Coast','1968-06-21',69),
 ('thompson-nicola','Thompson-Nicola','1967-11-28',29),
]

def add_entity(short, name, date, source, cohort, approval=None, note=None):
    eid=f'rhd-{short}-{date[:4]}'
    full=name+' Regional Hospital District'
    c=emit(eid,'incorporation',date,f'{full} incorporated by letters patent.',[source],
           'Order cover; letters patent incorporation and witness clauses',
           order_approval_date=approval or date, qualification=note)
    e=dict(id=eid, entity_type='regional_hospital_district', original_name=full,
           legal_start=date, legal_end=None, legal_end_status='not_fully_traced_in_this_module',
           start_source_ids=[sid(source)], cohort=cohort,
           names=[dict(name=full,valid_from=date,source_ids=[sid(source)])], claim_ids=[c])
    entities.append(e); return eid

old={}
for short,name,date,source in originals:
    old[short]=add_entity(short,name,date,source,'original_1967_1968')

new={}
new_names=[('cariboo','Cariboo'),('central-vancouver-island','Central Vancouver Island'),
 ('coast-garibaldi','Coast Garibaldi'),('east-kootenay','East Kootenay'),
 ('northern-interior','Northern Interior'),('north-okanagan','North Okanagan'),
 ('north-west','North West'),('peace-liard','Peace Liard'),
 ('south-okanagan-similkameen','South Okanagan Similkameen'),('thompson','Thompson'),
 ('upper-island-central-coast','Upper Island/Central Coast'),('west-kootenay-boundary','West Kootenay-Boundary')]
for i,(short,name) in enumerate(new_names,40):
    new[short]=add_entity(short,name,'1996-01-01',i,'new_1996',approval='1995-12-14',
        note='The final commencement clause expressly says 1 January 1996. Do not use the approval date as incorporation, or merge this identity with an older same-named district.')

fort=add_entity('fort-nelson-liard','Fort Nelson-Liard','1987-10-31',39,'additional',approval='1987-11-19',
    note='Express retroactive operative date; subsequent statutory validation is a separate matter.')
fraser=add_entity('fraser-valley','Fraser Valley','1995-12-12',4,'additional',approval='1995-12-07',
    note='Use the express date in the letters patent. The predecessor dissolutions occur at midnight 11 December.')
stuart=add_entity('stuart-nechako','Stuart-Nechako','1998-11-19',103,'additional')
byid={e['id']:e for e in entities}

def rename(eid,name,date,source,loc):
    full=name+' Regional Hospital District'
    c=emit(eid,'rename',date,'Continued corporation takes the name '+full+'.',[source],loc)
    byid[eid]['names'].append(dict(name=full,valid_from=date,source_ids=[sid(source)],claim_id=c))
    byid[eid]['claim_ids'].append(c)

def end(eid,date,source,loc,**kw):
    c=emit(eid,'dissolution',date,'Letters patent rescinded and corporation dissolved.',[source],loc,**kw)
    byid[eid].update(legal_end=date,legal_end_status='express_dissolution',end_source_ids=[sid(source)])
    byid[eid]['claim_ids'].append(c)

rename(old['malaspina'],'Powell River','1969-02-03',63,'Supplementary letters patent, name and witness clauses')
rename(old['malaspina'],'qathet','2024-02-26',64,'Supplementary letters patent, name clause')
rename(old['ocean-falls'],'Central Coast','1975-05-29',67,'Supplementary letters patent, name and witness clauses; board resolution 18 April is not the operative name date')
rename(old['skeena-a'],'Skeena-Queen Charlotte','1973-05-18',38,'Supplementary letters patent; cover/date visually checked (OCR misreads 1718 and 18 May)')
rename(old['skeena-b'],'Kitimat-Stikine','1970-05-12',74,'Supplementary letters patent, name and witness clauses')
rename(old['peace-river'],'Peace River','1987-10-31',117,'Supplementary letters patent, paragraph 1; prior Peace River-Liard name is established here but its first adoption date remains untraced')
byid[old['peace-river']]['names'].insert(1,dict(name='Peace River-Liard Regional Hospital District',valid_from=None,
    observed_by='1972-06-13',source_ids=[sid(118)],qualification='Do not substitute the municipal regional district renaming order 3028/1970 for this corporation’s missing name-change instrument.'))

for key,name in [('north-okanagan','North Okanagan/Columbia Shuswap'),('east-kootenay','Kootenay East'),('cariboo','Cariboo-Coast')]:
    rename(new[key],name,'1997-04-03',88,'Attached supplementary letters patent; order and witness dates visually checked')
rename(new['cariboo'],'Cariboo-Chilcotin','1998-11-19',106,'Schedule A, section 2(c)(i); immediate effect in enacting letters patent')
rename(new['coast-garibaldi'],'Sea to Sky','1998-11-19',106,'Schedule A, section 6(c)(i); immediate effect in enacting letters patent')

for key in ['central-fraser-valley','fraser-cheam','dewdney-alouette']:
    end(old[key],'1995-12-11',4,'Letters patent, dissolution/transfer paragraphs',time_qualification='midnight at the end of 11 December; successor begins 12 December')
    relationships.append(dict(from_id=old[key],to_id=fraser,type='assets_and_liabilities_transferred_to',effective_date='1995-12-12',source_ids=[sid(4)],locator='Letters patent, transfer and incorporation clauses'))

for key,date,source in [('bulkley-nechako','2000-06-01',36),('thompson-nicola','2014-03-31',30),
 ('kootenay-boundary','2016-07-04',5),('squamish-lillooet','2016-07-04',5),
 ('columbia-shuswap','2016-07-04',6),('north-okanagan','2016-07-04',6),
 ('central-kootenay','2019-12-09',31),('skeena-a','2021-05-21',32),
 ('east-kootenay','2024-04-08',34),('skeena-b','2025-03-17',33)]:
    end(old[key],date,source,'Operative dissolution clause; attached letters patent where applicable')
end(old['greater-vancouver'],'1999-01-01',162,'Order, paragraphs1–2',order_approval_date='1998-12-17')
emit(old['greater-vancouver'],'assets_and_liabilities_transfer','1999-01-01',
     'Specified assets vest in South Fraser Health Region, Vancouver/Richmond Health Board and Vancouver General Hospital; the residual assets and liabilities vest in the Province.',[162],
     'Appendix ss.1–6 and SchedulesA–D',qualification='Surrey land and VGH parkade transfers are subject to the express review, funding and debt conditions. This is not a general merger into one health authority.')
for label,loc,condition in [
    ('South Fraser Health Region','Appendix1–2; ScheduleA','Surrey15-acre parcel; independent review within3years and possible reversion'),
    ('Vancouver/Richmond Health Board','Appendix3; ScheduleB','Tilbury Laundry and adjacent land'),
    ('Vancouver General Hospital','Appendix4–5; SchedulesC–D','Parkade; operating-funding restrictions and specified debt obligations. Appendix5(3) provides transfer and vesting in government upon failure to comply with either condition; no later breach or reversion is proved here.'),
    ('Province of British Columbia','Appendix6','Residual assets and liabilities, including leasehold interests')]:
    relationships.append(dict(from_id=old['greater-vancouver'],to_label=label,type='assets_transferred_to',effective_date='1999-01-01',source_ids=[sid(162)],locator=loc,conditions=condition))

emit('regional-hospital-areas','geographic_framework','1967-04-13',
     'OIC 1222 creates 27 geographic areas for the regional-hospital-district system; the individual corporations are established later by their own letters patent.',[2],'Order and schedule',
     qualification='Area creation is not a common incorporation date for all 28 districts documented here.')
emit('original-regional-hospital-districts','boundary_and_governance_coordination','1972-02-08',
     'OIC 527 amends 28 existing corporations so municipal membership, electoral areas and voting units follow the corresponding municipal regional districts.',[37],'Recitals and Schedule A',items=('A8','G3'),
     qualification='Not the incorporation of 28 new corporations. Recitals describe corresponding regional directors; consult each original letter for the initial board constitution.')
emit('transitional-regional-hospital-districts','powers_restricted','1995-12-31',
     'OIC 1549 limits 24 existing districts to approved capital projects, debt repayment/requisition and other minister-approved powers.',[3],'Schedule A; operative date',
     order_approval_date='1995-12-14',qualification='Restriction of powers is not dissolution.')

restorations=[('alberni-clayoquot',1),('ocean-falls',3),('central-okanagan',4),('comox-strathcona',7),
 ('cowichan-valley',8),('FORT',9),('fraser-fort-george',10),('mount-waddington',11),('nanaimo',12),
 ('okanagan-similkameen',16),('peace-river',18),('malaspina',19),('sunshine-coast',21)]
for key,section in restorations:
    eid=fort if key=='FORT' else old[key]
    c=emit(eid,'restrictive_powers_clause_repealed','1998-11-19',
       'The restrictive paragraph inserted by the 1995 transitional order is repealed; existing corporation continues.',[106],f'Schedule A, section {section}',
       qualification='Restoration of powers, not a new incorporation.')
    byid[eid]['claim_ids'].append(c)

transfers=[
 ('central-vancouver-island',5,[old[x] for x in ['alberni-clayoquot','cowichan-valley','nanaimo','malaspina']]),
 ('northern-interior',15,[stuart,old['fraser-fort-george'],old['peace-river']]),
 ('peace-liard',17,[fort,old['peace-river']]),
 ('south-okanagan-similkameen',20,[old['central-okanagan'],old['okanagan-similkameen']]),
 ('upper-island-central-coast',22,[old['ocean-falls'],old['comox-strathcona'],new['north-west'],old['mount-waddington']]),
]
for key,section,recipients in transfers:
    end(new[key],'1998-12-31',106,f'Schedule A, section {section}(c)')
    emit(new[key],'transfer_directed_with_deadline','1998-11-19',
       'Transfer to the specified recipients must be completed by 31 December 1998. Liquid assets are apportioned by assessment; fixed assets by agreement; vesting occurs on the actual transfer date.',[106],f'Schedule A, section {section}(a)–(b)',
       deadline='1998-12-31',actual_transfer_date=None,recipient_ids=recipients)
    for rec in recipients:
        relationships.append(dict(from_id=new[key],to_id=rec,type='assets_transfer_directed',
          order_effective_date='1998-11-19',deadline='1998-12-31',actual_transfer_date=None,
          source_ids=[sid(106)],locator=f'Schedule A, section {section}(a)–(b)',
          qualification='Directed transfer; the deadline is not evidence of the actual closing day.'))
for key,section,recipients in [('cariboo',2,[old['ocean-falls']]),('coast-garibaldi',6,[old['malaspina'],old['sunshine-coast']])]:
    emit(new[key],'partial_transfer_directed_with_deadline','1998-11-19',
       'Boundary reduction accompanied by a partial asset transfer to the specified recipients, due by 31 December 1998; corporation continues under its new name.',[106],f'Schedule A, section {section}(a)–(c)',
       deadline='1998-12-31',actual_transfer_date=None,recipient_ids=recipients)
    for rec in recipients:
        relationships.append(dict(from_id=new[key],to_id=rec,type='partial_assets_transfer_directed',order_effective_date='1998-11-19',deadline='1998-12-31',actual_transfer_date=None,source_ids=[sid(106)],locator=f'Schedule A, section {section}'))
for key,section in [('north-okanagan',13),('north-west',14),('west-kootenay-boundary',23)]:
    emit(new[key],'membership_and_boundary_amendment','1998-11-19',
       'The continuing district’s membership and boundaries are replaced; no dissolution is ordered.',[106],f'Schedule A, section {section}')

emit('1996-hospital-districts','membership_boundary_and_board_amendments','1996-04-18',
     'OIC 524 issues twelve sets of supplementary letters patent, including revised membership/boundaries and clauses linking directors and alternates to corresponding municipal regional boards.',[116],
     'Order cover; operative clauses of each attached letter',items=('A8','G3'),
     qualification='Individual metes-and-bounds polygons have not been digitized in this module.')
emit(old['skeena-a'],'asset_transfer','2021-04-21',
     'The remaining $53,519.57 is transferred to North West Regional Hospital District one month before the old Skeena-Queen Charlotte corporation is dissolved.',[32],'Operative transfer and dissolution clauses',recipient_id=new['north-west'],amount_cad=53519.57)
relationships.append(dict(from_id=old['skeena-a'],to_id=new['north-west'],type='assets_transferred_to',effective_date='2021-04-21',amount_cad=53519.57,source_ids=[sid(32)]))
emit(old['peace-river'],'separation_and_debt_allocation','1987-10-31',
     'Peace River-Liard continues under the Peace River name with reduced boundaries; Fort Nelson-Liard is separately incorporated, with relief and debt allocation specified.',[39,117],'Both attached letters patent, boundaries and debts clauses',
     order_approval_date='1987-11-19',recipient_id=fort)

emit('regional-hospital-district-governance','current_statutory_roles','2026-10-21',
     'Hospital District Act sections 8, 17, 32 and 45 separately govern board composition, administrative staff/audit, capital bylaws and ministerial inspection/reporting.',[1],
     'Hospital District Act, ss.8,17,32,45',items=('A8','G1','G2','G3','G4'),
     evidence_type_override='current_consolidation',qualification='Current-law checkpoint only. This does not establish that identical rules applied in earlier years or that a district is a Ministry of Health branch.')

conflicts.extend([
 dict(subject=old['cariboo'],later_source=sid(3),later_claim='16 July 1967',original_source=sid(11),accepted_date='1968-07-16'),
 dict(subject=old['comox-strathcona'],later_source=sid(3),later_claim='8 December 1968',original_source=sid(8),accepted_date='1967-12-08',also_appears_in=sid(106)),
 dict(subject=old['central-kootenay'],later_source=sid(3),later_claim='24 August 1967',original_source=sid(12),accepted_date='1967-07-11',also_appears_in=sid(37)),
 dict(subject=old['cowichan-valley'],later_source=sid(3),later_claim='28 September 1967',original_source=sid(61),accepted_date='1967-09-26'),
 dict(subject=old['thompson-nicola'],later_source=sid(3),later_claim='21 November 1967',original_source=sid(29),accepted_date='1967-11-28'),
 dict(subject=old['dewdney-alouette'],later_source=sid(37),later_claim='27 October 1968',original_source=sid(24),accepted_date='1967-10-27'),
 dict(subject=old['skeena-a'],later_source=sid(32),later_claim='Incorporation by letters patent dated 8 February 1972',original_source=sid(27),accepted_date='1967-08-17',explanation='OIC527/1972 is a supplementary amendment; do not reset the original corporation’s start.'),
])

# Exact commencement instruments requested by G2 and G5.
emit('Election Amendment Act, 1987 (SBC1988 c2)','royal_assent','1988-03-11',
     'Act receives assent; section 23 reserves commencement to regulation.',[59],'Printed p.17 and s.23',items=('G5',))
emit('Election Amendment Act, 1987 (SBC1988 c2)','commencement','1988-03-28',
     'Entire amendment Act comes into force under OIC548/1988, B.C. Reg.101/88. The order was approved 25 March; the official statute table states effective 28 March.',[59,70,80,81],
     'OIC548 operative clause; 1994 Table of Statutes, Election Act entry, printed pp.979–981',items=('G5',),order_approval_date='1988-03-25',supersedes_prior_claim='R3G-F027')
emit('Provincial franchise: people released on probation or parole','qualification_exception','1988-03-28',
     'Election Act s.3(3) excepts from the indictable-offence disqualification a person released on probation or parole who is not in custody.',[59,70,80],
     '1988c2 s.3, printedp17; 1994 statute table',items=('G5',),
     qualification='Use the statutory conditions. Do not broaden this to enfranchisement of everyone in prison or every convicted person.')
emit('Provincial franchise: residence','qualification_change','1988-03-28',
     'Section 2 removes the twelve-month Canadian-residence phrase from Election Act s.2(1)(c), and permits the age qualification to be met on polling day.',[59,70,80],
     '1988c2 s.2, printedp17; 1994 statute table',items=('G5',),
     qualification='This does not remove all British Columbia residence requirements.')
emit('Provincial franchise: Crown service absences','residence_preservation','1988-03-28',
     'The substituted residence rule protects a Crown servant absent outside the province and an accompanying spouse or child from losing residence for that reason alone.',[59,70,80],
     '1988c2 s.4, printedp17',items=('G5',))
emit('Local public bodies under FOIPPA','statutory_class_coverage_begins','1994-11-03',
     'OIC1356/1994, B.C.Reg400/94, commences the educational-body, health-care-body, local-government-body and local-public-body definitions and related access machinery.',[71,72,80,81],
     'OIC1356 paragraphs(a)–(d); 1993c46 s.28(a)–(c),(f),(g); 1994 table printed1009–1010',items=('G2',),
     order_approval_date='1994-11-02',qualification='Class-based coverage does not require every body to be individually named in Schedule2. Applying a class definition to a particular body still requires a matching legal identity and existence interval.')
emit('Regional hospital districts and boards under FOIPPA','statutory_class_coverage_begins','1994-11-03',
     'The commenced definition of health care body expressly includes a regional hospital district and regional hospital district board under the Hospital District Act.',[71,72,80],
     '1993c46 s.28(c), paragraph(c) of health care body, printed412; OIC1356(a); statute table1009–1010',items=('A8','G2'))
emit('FOIPPA professional-governing-body schedule','schedule_commencement','1995-11-06',
     'OIC1321/1995 expressly commences1993c46 sections30 and32 on6November1995; section30 adds the professional-governing-body Schedule3. The official1995table corroborates B.C.Reg451/95.',[81,72,'R4H-019'],
     'Original OIC1321/1995 p1;1993c46 ss30,32;1995 Table of Statutes, printed1244',items=('G2',),
     order_approval_date='1995-11-02',qualification='Original commencement order recovered by health follow-up. Apply the Schedule3 list and its amendments to each body individually; not a universal date for all professions or all health bodies.')

emit('Ministerial Titles Amendment Act,1977','corroborated_proclamation_date','1977-10-21',
     'The official 1994 statute table records the 1977c75 amendments to Hospital Corporations Act ss.2,5,10 and West Coast National Park Act s.7 as proclaimed effective21October1977.',[10,80],
     'OIC3240/1977; 1994 Table of Statutes printed1022/PDF90 and printed1198/PDF266',items=('C2',),
     evidence_type_override='authorization_plus_official_compilation',qualification='The actual proclamation and a direct table entry for the Health-title amendment remain unretrieved; this is corroboration of identified amendments, not blanket proof for every provision.')

# The Water Act corporations are separate predecessors, not early names of RHDs.
hid_review=json.loads((BASE.parent/'health/hid-verification.json').read_text())
hid_entities=[]
hid_relationships=[]
destination_by_name={e['original_name']:e['id'] for e in entities if e['cohort']=='original_1967_1968'}
for h in hid_review['incorporations']:
    stem=h['original_corporate_name'].split(' Hospital Improvement District')[0]
    short=re.sub('[^a-z0-9]+','-',stem.lower()).strip('-')
    eid=f'hid-{short}-{h["incorporation_date"][:4]}'
    c1=emit(eid,'incorporation',h['incorporation_date'],
        h['original_corporate_name']+' incorporated under the Water Act.',[h['source_id']],
        h['name_pinpoint']+'; witness clause PDF p.'+','.join(map(str,h['date_pinpoint']['pdf_pages'])),
        items=('A8','G3'),original_name=h['original_corporate_name'],statutory_authority=h['statutory_authority'])
    c2=emit(eid,'dissolution','1969-09-25','Hospital improvement district dissolved under Regional Hospital Districts Act section 50C.',[115],
        'Order operative clause and Schedule column A')
    destination=destination_by_name[h['dissolution']['successor_transferee_as_printed']]
    c3=emit(eid,'assets_rights_and_liabilities_transferred','1969-09-25',
        'All real and personal assets, rights, claims, obligations and liabilities transferred to '+h['dissolution']['successor_transferee_as_printed']+'.',
        [115],'Order operative clause and paired Schedule columns A–B',recipient_id=destination)
    e=dict(id=eid,entity_type='hospital_improvement_district',original_name=h['original_corporate_name'],
        legal_start=h['incorporation_date'],legal_end='1969-09-25',start_source_ids=[h['source_id']],end_source_ids=[sid(115)],
        names=[dict(name=h['original_corporate_name'],valid_from=h['incorporation_date'],source_ids=[h['source_id']])],
        governance_at_incorporation=h['governance'],statutory_authority=h['statutory_authority'],
        claim_ids=[c1,c2,c3],objects_summary=h['objects_summary'])
    if h['later_1969_name']!=h['original_corporate_name']:
        e['names'].append(dict(name=h['later_1969_name'],valid_from=None,observed_on='1969-09-25',source_ids=[sid(115)],
            qualification='Later label observed; formal intervening name-change day not proved except where separately stated.'))
    hid_entities.append(e)
    hid_relationships.append(dict(from_id=eid,to_id=destination,type='assets_rights_and_liabilities_transferred_to',effective_date='1969-09-25',
        source_ids=[sid(115)],claim_id=c3))

castlegar=next(e for e in hid_entities if e['original_name']=='Castlegar Hospital Improvement District')
c=emit(castlegar['id'],'rename','1955-08-06','Number 3 is added to the Castlegar corporate name.',[152],
       'OIC1976/1955 operative amendment to Letters Patent clause2')
castlegar['names'].insert(1,dict(name='Castlegar Hospital Improvement District No. 3',valid_from='1955-08-06',source_ids=[sid(152)],claim_id=c))
castlegar['claim_ids'].append(c)
emit('Hospital improvement district electorates','original_letters_patent_governance',None,
     'The 23 original instruments use a restricted district or zone electorate: Canadian citizenship, age21, provincial-voter eligibility and a landowner or specified representative qualification. Their trustee arrangements differ by instrument.',
     [h['source_id'] for h in hid_review['incorporations']],
     'Per-district board, first-election and annual-elector clauses in hid-verification.json',items=('A8','G3','G5'),
     qualification='These are dated original rules, not a claim about every later year. Gulf Islands proxy arrangements and Creston trustee-candidate rules need their specific qualifications; do not equate this electorate with all provincial residents.')
claims[-1]['import_status']='context_only_use_per_entity_dated_rules'

fn=hid_review['fort_nelson']; fneid='hid-fort-nelson-1958'
fnclaims=[]
fnclaims.append(emit(fneid,'incorporation','1958-06-07','Fort Nelson Hospital Improvement District No.21 incorporated.',[154],
    'Letters Patent clauses1–3 and witness clause, PDFp8',items=('A8','G3')))
fnclaims.append(emit(fneid,'continuation_and_replacement_letters_patent','1959-07-07',
    'The existing corporation is continued under replacement Letters Patent: five trustees elected at large, with ambulance services added to its objects.',[155],
    'PDFpp2–4, clauses1 and4–7; witnessp6',items=('A8','G3'),qualification='Not a new incorporation. The original appointed first board and later elected boards are separate governance events.'))
fnclaims.append(emit(fneid,'dissolution','1972-06-13','The improvement district is dissolved, effective on the order date.',[118],
    'PDFpp1–2, operative recommendation'))
fnclaims.append(emit(fneid,'assets_rights_and_liabilities_transferred','1972-06-13',
    'All assets, rights, claims, obligations and liabilities pass forthwith to Peace River-Liard Regional Hospital District.',[118],
    'PDFp2, operative recommendation',recipient_id=old['peace-river']))
fnclaims.append(emit('Fort Nelson Hospital Society','incorporation_recital','1971-10-18',
    'The 1972 order reports that the hospital society was incorporated on18October1971.',[118],
    'PDFp1, society recital',evidence_type_override='later_primary_order_recital',qualification='Original registry certificate not retrieved.'))
fnclaims.append(emit(old['peace-river'],'certified_board_transfer_resolution','1972-06-13',
    'The regional board resolution transfers the former Fort Nelson improvement-district property and obligations to Fort Nelson Hospital Society from the dissolution date, except financial/debt functions already assumed by the RHD.',[118],
    'PDFp4, certified resolution adopted23May1972',resolution_date='1972-05-23',recipient_label='Fort Nelson Hospital Society',
    qualification='An operative certified resolution is attached; separately executed conveyances and separate completed ministerial approval are not.'))
hid_entities.append(dict(id=fneid,entity_type='hospital_improvement_district',original_name=fn['original_incorporation']['original_corporate_name'],
    legal_start='1958-06-07',legal_end='1972-06-13',start_source_ids=[sid(154)],end_source_ids=[sid(118)],
    names=[dict(name=fn['original_incorporation']['original_corporate_name'],valid_from='1958-06-07',source_ids=[sid(154)])],
    governance_at_incorporation=fn['original_incorporation']['governance'],governance_1959=fn['replacement_letters_patent']['governance'],claim_ids=fnclaims))
hid_relationships.extend([
    dict(from_id=fneid,to_id=old['peace-river'],type='assets_rights_and_liabilities_transferred_to',effective_date='1972-06-13',source_ids=[sid(118)],locator='PDFp2'),
    dict(from_id=old['peace-river'],to_label='Fort Nelson Hospital Society',type='onward_transfer_by_board_resolution',effective_date='1972-06-13',resolution_date='1972-05-23',source_ids=[sid(118)],locator='PDFp4',qualification='Excludes financial/debt functions already retained by the RHD; separately executed deeds not retrieved.')])

hmeid='hid-100-mile-house-1960'; hmclaims=[]
hmclaims.append(emit(hmeid,'incorporation','1960-08-04','100 Mile House Hospital Improvement District No.28 incorporated under the Water Act.',[164],
    'Letters Patent clauses1–2 and witness clause PDFp12, visually checked',items=('A8','G3')))
hmclaims.append(emit(hmeid,'electoral_zone_boundary_amendment','1960-09-09','Descriptions of zones4 and5 replaced.',[166],
    'Operative amendment to Letters Patent clause4',items=('A8','G3')))
hmclaims.append(emit(hmeid,'hospital_board_constitution','1960-09-27',
    'District trustees together with a Hospital Act section5 appointee constitute the hospital board of management.',[165],
    'OIC2195/1960, added clause5A; cover27September visually checked',items=('A8','G3'),
    qualification='The recommendation was signed26September; the order was approved27September. The later1972 recital gives26September.'))
hmclaims.append(emit(hmeid,'dissolution','1972-05-12','Improvement district dissolved effective on the date of the order.',[163],
    'PDFp2 operative recommendation'))
hmclaims.append(emit(hmeid,'assets_rights_and_liabilities_transferred','1972-05-12',
    'All assets, rights, claims, obligations and liabilities transferred forthwith to Cariboo Regional Hospital District.',[163],
    'PDFp2 operative recommendation',recipient_id=old['cariboo']))
hmclaims.append(emit('100 Mile District Hospital Society','incorporation_recital','1971-11-17',
    'The1972 order reports the society incorporated17November1971 to operate and maintain the100Mile District General Hospital.',[163],
    'PDFp1, society recital',evidence_type_override='later_primary_order_recital',qualification='Original registry certificate not retrieved.'))
hmclaims.append(emit(old['cariboo'],'certified_board_transfer_resolution','1972-05-12',
    'Certified board resolution transfers the former100Mile House improvement-district property and obligations to100Mile District Hospital Society from the dissolution date, except financial/debt functions already assumed by the RHD.',[163],
    'PDFp3, certified resolution adopted6April1972',resolution_date='1972-04-06',recipient_label='100 Mile District Hospital Society',
    qualification='Operative certified resolution is attached; separately executed conveyances and separate completed ministerial approval are not.'))
hid_entities.append(dict(id=hmeid,entity_type='hospital_improvement_district',original_name='100 Mile House Hospital Improvement District No. 28',
    legal_start='1960-08-04',legal_end='1972-05-12',start_source_ids=[sid(164)],end_source_ids=[sid(163)],
    names=[dict(name='100 Mile House Hospital Improvement District No. 28',valid_from='1960-08-04',source_ids=[sid(164)])],
    governance_at_incorporation=dict(trustee_count=5,zone_count=5,seat_allocation='One elected trustee per zone.',
        elector_profile=hid_review['common_elector_profile']['id'],locator='Letters Patent clauses5–9, PDFpp8–11',source_ids=[sid(164)]),claim_ids=hmclaims))
hid_relationships.extend([
    dict(from_id=hmeid,to_id=old['cariboo'],type='assets_rights_and_liabilities_transferred_to',effective_date='1972-05-12',source_ids=[sid(163)],locator='PDFp2'),
    dict(from_id=old['cariboo'],to_label='100 Mile District Hospital Society',type='onward_transfer_by_board_resolution',effective_date='1972-05-12',resolution_date='1972-04-06',source_ids=[sid(163)],locator='PDFp3',qualification='Excludes financial/debt functions already retained by the RHD; separately executed deeds not retrieved.')])
conflicts.append(dict(subject=hmeid,later_source=sid(163),later_claim='26September1960 amendment',original_source=sid(165),accepted_date='1960-09-27',
    explanation='26September is the ministerial recommendation/Executive Council signature day. Original order cover says approved and ordered27September1960.'))

emit(old['alberni-clayoquot'],'treaty_land_membership_amendment','2012-04-01',
    'The membership clause is amended to include treaty lands of treaty First Nations listed in the corresponding regional district Letters Patent; recitals identify Huu-ay-aht and Ucluelet participation from1April2012.',[167],
    'Letters Patent preamble and replacement section3; PDFpp2–3',items=('A8','G3','G7'),order_approval_date='2012-03-29',
    qualification='A dated intergovernmental membership relation, not placement of a First Nation under a ministry. This is not the Maa-nulth treaty commencement date.')
emit(old['alberni-clayoquot'],'pre_membership_debt_requisition_limitation','2015-12-17',
    'Added section12 prohibits including in a Maa-nulth First Nation requisition the specified borrowing repayments for decisions made before that First Nation became a member.',[9],
    'Letters Patent, added section12, PDFp3',items=('A8','G7'),
    qualification='The provision qualifies the financial relationship; it is not a new district incorporation or a new treaty commencement.')

data = dict(schema='pofbc.round4.hospital-district-register.v1', research_cutoff='2026-10-21',
    purpose='Research handback; no automatic repository import',
    identity_policy='Municipal regional districts, regional hospital districts, hospital improvement districts, health boards and hospital societies are separate legal/administrative types.',
    entities=entities,relationships=relationships,conflicts=conflicts,
    qualifications=[
      'A null legal_end is an unresolved field, not positive evidence of present-day survival.',
      'The 1996 districts sharing names with older corporations require distinct IDs.',
      'The 1998 transfer deadline must not be converted into an actual transfer date.',
      'Original letters patent control over inaccurate dates in later recitals.',
      'The old Cariboo district’s final legal end and the first Peace River-Liard hospital-district renaming remain untraced.',
      'Current-law governance is a dated checkpoint, not a historical backfill.'
    ])

def readable_strings(value,key=None):
    if isinstance(value,dict): return {k:readable_strings(v,k) for k,v in value.items()}
    if isinstance(value,list): return [readable_strings(v,key) for v in value]
    if isinstance(value,str) and key in {'statement','qualification','qualifications','locator','conditions','explanation','purpose','title'}:
        value=re.sub(r'(?<=[a-z])(?=\d)', ' ',value)
        value=re.sub(r'(?<=\d)(?=[A-Za-z])', ' ',value)
        value=re.sub(r'\b(PDF|printed)\s*p\.?\s*(?=\d)',r'\1 p. ',value)
        value=re.sub(r'\b(Schedule|Appendix)(?=[A-Z0-9])',r'\1 ',value)
    return value

def save(name,data): (BASE/name).write_text(json.dumps(readable_strings(data),ensure_ascii=False,indent=2)+'\n')
save('hospital_districts.json',data)
save('hospital_improvement_districts.json',dict(schema='pofbc.round4.hospital-improvement-district-register.v1',
    research_cutoff='2026-10-21',entities=hid_entities,relationships=hid_relationships,
    original_elector_profile=hid_review['common_elector_profile'],
    qualifications=['All25starts rest on original incorporation instruments;23ends/transfers are in OIC3082/1969; two later cases have certified onward-transfer resolutions.',
      'The corporations are distinct from hospital societies, regional hospital districts, and later health authorities.',
      'Do not turn an observed later label into a proven renaming date.',
      'Landowner electorates and original trustee rules must not be replaced with a universal provincial electorate.']))
save('claims.json',claims)
save('conflicts.json',conflicts)
save('root_summary.json',dict(regional_hospital_district_identities=len(entities),
 original_1967_1968_incorporations=len(originals),new_1996_incorporations=len(new),
 powers_restored_1998=len(restorations),districts_dissolved_1998_omnibus=len(transfers),hospital_improvement_district_identities=len(hid_entities),
 hid_original_dates_verified=25,hid_1969_dissolutions=23,formal_claims=len(claims)))
print(json.dumps(json.loads((BASE/'root_summary.json').read_text()),indent=2))
