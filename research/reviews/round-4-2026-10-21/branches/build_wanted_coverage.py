import json
from pathlib import Path

BASE = Path('/workspace/scratch/a5ca1a8fd90b/round4/branches')
claims = json.loads((BASE/'claims.json').read_text())
claim_index = {c['id']: c for c in claims}
coverage = json.loads((BASE/'coverage.json').read_text())

def ids(*numbers):
    return [f'R4B-C{n:03d}' for n in numbers]

def entry(item, title, status, findings, claim_ids, remaining, **extra):
    return dict(item=item, title=title, status=status, new_findings=findings,
                claim_ids=claim_ids,
                source_ids=sorted({s for k in claim_ids for s in claim_index[k]['source_ids']}),
                remaining=remaining, **extra)

f1_claims = ids(*range(1,47), *range(76,87))
f2_claims = [c['id'] for c in claims if c['type'] in {
    'relationship_observation','administrative_transfer_and_rename','administrative_separation_observed'}]
f2_claims += ids(79,80,86)
items = [
    entry('F1','Sub-agency starts and sightings','substantial_partial',[
        '16 of the 33 previously undated records receive new dated evidence. Five other records can use evidence already obtained by the Round 3 health and tribunal modules; those five are integrations, not new discoveries.',
        'Medical Services Commission original 1967 Act and Orders in Council establish initial appointments on 24 March 1967 and staff establishment on 25 March 1967. The later July 1968 retrospective creation statement cannot replace these original dates.',
        'The new records include programs, a special account, information resources, a campaign brand and a program family. They require correct entity types; their dates are not automatically branch founding dates.'
    ],f1_claims,[
        {'body_id':r['body_id'],'reason':r['reason']} for r in coverage['rows']
        if r['disposition']=='still_no_accepted_pre2026_date'
    ], count_reconciliation={
        'round3_remaining':33,'new_dated_evidence':16,'prior_cross_module_integrations':5,
        'dated_after_combining_modules':21,'still_without_accepted_pre2026_date':12,
        'equation':'33 - 16 - 5 = 12',
        'original_158_after_all_integrations':{'dated':146,'remaining':12},
        'complete_lifecycles_claimed':0
    }, new_dated_ids=coverage['new_dated_ids'],
       prior_cross_module_ids=coverage['cross_module_ids'],
       precise_record_dispositions='coverage.json'),
    entry('F2','Sub-agency parents over time','additional_dated_observations',[
        'Adds dated organizational or program-administration observations for Buy BC, Provincial Treasury, Building and Safety Standards, two Infrastructure divisions, Community Safety and Victim Services, Building BC and Trans Care BC; four PHSA service-node parents reuse the 2009/10 health report.',
        'Separately records Arts Council payment recommendation, official-mark ownership, MSC Crown-agent and reporting provisions, and MSC deemed ministry membership for Financial Administration Act purposes only. These meanings must remain distinct from ordinary ministry hierarchy.',
        'Adds explicit Parks/Game/Photographic changes effective 1 April 1957, COS observations in 1980/81 and sheriffs under the Director of Court Services in 1978.'
    ],sorted(set(f2_claims)),[
        'No continuous parent history is inferred between checkpoints, and the baseline 1,609 inferred sub-agency-years has not been recomputed.',
        'The named minister designated to administer the original 1967 Medical Services Act has not been identified; a signature on the OIC is not treated as a designation.',
        'Three current Indigenous Relations and Reconciliation division identities remain unbridged to the older structure named on 29 April 2025.'
    ]),
    entry('F3','The sheriffs','substantial_predecessor_evidence_merger_open',[
        'Adds the mainland High Sheriff statutory predecessor in 1860, three-district appointment authority in 1873, additional districts in 1878 and conditional Clinton authority in 1880.',
        'The 1888 Act continues and renames six offices; Vancouver receives separate conditional authority in 1892, an acting appointment on 26 October 1892, and a permanent appointment on 3 July 1893.',
        'Dates county-territory changes in 1895 and 1905 and the 1920 Atlin-to-Prince Rupert change. Keeps appointment authority, actual appointment and territorial change distinct.',
        'Adds a 1978 Court Services parent observation, a statutory annual Gazette roster lead from 1890 and specific archival descriptions for sheriff files. The 1974 Police Act candidate does not establish the merger.'
    ],ids(*range(55,75),87,88),[
        'The administrative instrument combining nine offices in 1974 remains unfound; previously established milestones are not recounted as a new exact merger date.',
        'The original appointment or founding instrument for every county office is not complete; conditional statutory powers alone do not establish that an office began operating.',
        'The 1857 colonial appointment evidence and the exact pre-1873 office lineage remain open.'
    ]),
    entry('F4','Enforcement and lands branches','additional_primary_observations_instruments_open',[
        'The official Recreation and Conservation report dates Parks and Recreation Division to 1948 and the transfer/rename to Parks Branch, Department of Recreation and Conservation, to 1 April 1957.',
        'Contemporary April–May 1980 staff reporting documents COS separation. OIC 2085/1980 on 18 September supplies a Ministry of Environment powers/relationship checkpoint; 1980/81 organization reporting supplies Regional Operations placement.'
    ],ids(*range(47,55)),[
        'The exact separate administrative instrument creating or renaming Parks Branch in 1957 has not been recovered.',
        'The exact 1980 COS separation instrument and day remain unresolved; the contemporary period is retained without a fabricated day.',
        'No new Wildfire Management Branch rename order or Surveyor General split instrument was found in this continuation.',
        'Earlier 1905, 1961 and 2002 COS evidence remains in the prior package and is not counted again.'
    ]),
    entry('F5','Bodies that are gone, with a successor still drawn','limited_predecessor_transfer_additions',[
        'Adds the Parks and Recreation Division to Parks Branch transition and the Game Commission from Attorney General to Fish and Game Branch in Recreation and Conservation, both effective 1 April 1957.',
        'Separately records the Photographic Branch administrative change and the 1980 COS separation observation; these permit historical units and their changes to be represented without extending current labels backward.'
    ],ids(*range(47,55)),[
        'No new complete lifecycle is supplied here for the Liquor Control and Licensing Branch, Emergency Management BC, Industry Training Appeal Board, BC Ambulance Service, old Forest Service divisions generally, or tribunals folded in 2002–03.',
        'The 1957 Game Commission relationship and rename do not settle every earlier Provincial Game Commissioner office identity or later endpoint.',
        'BC Mental Health and Substance Use Services has a current-name sighting on 17 December 2015 (R4B-C037), but the exact rename from Mental Health and Addiction Services is still unproved.'
    ]),
    entry('C4','MSP, PharmaCare and hospital insurance','medical_services_commission_new_originals',[
        'Finds the 23 March 1967 Medical Services Act, commencement authorizations for 24 and 25 March, initial Commission appointments on 24 March, staff establishment on 25 March and the later 15 May 1968 increase.',
        'A contemporary 6 June 1968 Commission announcement treats 1 July 1968 as a forthcoming coverage event. It must not replace the earlier Commission constitution and appointment dates.',
        'Records the original statutory accountability scheme and the 2003/04 Financial Administration Act-only deemed membership, while preserving the conflict in the later retrospective July 1968 establishment statement.'
    ],ids(*range(76,87)),[
        'The Commission is institutionally distinct from the Medical Services Plan program and its coverage start.',
        'No new complete PharmaCare or hospital-insurance chronology is supplied by this branch module.',
        'The 1967 Act-administration minister designation and any executed proclamation beyond the recovered authorizing OIC remain unlocated.'
    ]),
    entry('H3','Before 1905: Provincial Secretary and Lands and Works agencies','adjacent_evidence_only',[
        'The sheriff statutes and appointments supply additional pre-1905 provincial administrative evidence, including required financial returns to Finance and Agriculture in 1873.'
    ],ids(*range(55,72),87),[
        'These sheriff records do not complete the requested Provincial Secretary or Lands and Works agency survey.',
        'A statutory financial-reporting relationship is not treated as a ministry-parent assignment.',
        'No H3 baseline item is marked complete from this adjacent evidence.'
    ]),
    entry('G3','Who appoints each board','medical_services_commission_specific_answer',[
        'The original 1967 statute states that the Lieutenant Governor in Council appoints Commission members; OIC 965/1967 supplies the initial appointments on 24 March 1967.',
        'Sheriff appointment powers and actual appointments are available as adjacent office-head evidence in F3. They are not board appointment rules.'
    ],ids(76,78,84),[
        'This supplies one Commission rule and initial appointment event, not a complete board-appointment inventory.',
        'The audit-hearings committee date is a prior tribunal-module integration; its appointment powers should be imported from that module rather than called new branch research.'
    ])
]
result = {
    'schema':'pofbc-wanted-coverage/1','checked':'2026-10-21',
    'repository_baseline':'0f1587c5e982135f155ba6660af5192509351511',
    'scope':'Round 4 incremental branch findings only: F1–F5, C4, H3 and G3; preserve all other baseline item dispositions.',
    'merge_policy':'Merge these incremental findings into the existing 59-item coverage. Do not replace baseline findings or close an item merely because a new checkpoint exists.',
    'all_needed_information_claimed':False,'new_research_in_this_synthesis':True,
    'claims_file':'claims.json','sources_file':'sources.json',
    'evidence_manifest':'evidence-manifest.json',
    'source_and_locator_policy':'Each claim supplies source IDs and exact locators. The evidence manifest maps accepted originals and page extracts, with SHA-256 hashes; screened candidates are not counted as accepted sources.',
    'items':items
}
(BASE/'wanted-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
assert len(items)==8
assert set(i['item'] for i in items)=={'F1','F2','F3','F4','F5','C4','H3','G3'}
assert all(k in claim_index for i in items for k in i['claim_ids'])
assert len(coverage['new_dated_ids'])==16 and len(coverage['cross_module_ids'])==5 and len(coverage['remaining_undated_ids'])==12
print('Wrote wanted-coverage.json:',len(items),'incremental item records; all claim references valid.')
