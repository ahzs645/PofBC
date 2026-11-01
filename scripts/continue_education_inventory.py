#!/usr/bin/env python3
"""Reconcile all 25 public institution identities and the remaining acquisition queue."""
import collections
import gzip
import json
import re
from continue_education import ROOT,OUT,AUDIT,DISCOVERY,dump

def main():
    old=json.loads((DISCOVERY/'findings.json').read_text())
    accepted=json.loads((OUT/'sources.json').read_text())['sources']
    if (OUT/'supplemental/sources.json').exists():accepted+=json.loads((OUT/'supplemental/sources.json').read_text())['sources']
    held=json.loads((OUT/'held/sources.json').read_text())['sources']
    base=json.loads((AUDIT/'accepted-baseline.json').read_text())
    indexes=json.loads((AUDIT/'current-index-receipts.json').read_text())
    inventory=[]
    for e in old['employers']:
        slug=e['employerSlug'];a=[s for s in accepted if s['employerSlug']==slug];h=[s for s in held if s['employerSlug']==slug];b=[s for s in base if s['employerSlug']==slug]
        inventory.append(dict(employerSlug=slug,employerName=e['employerName'],sector='Universities and colleges',identityStatus='existing-application-employer',baselineOfficialSources=b,newVerifiedSources=[dict(id=s['id'],year=s['year'],rows=s['rowCount'],completeEmployeeSchedule=s['completeEmployeeSchedule'],sourceUrl=s['sourceUrl']) for s in a],heldCandidates=[dict(id=s['id'],year=s['year'],rows=s['rowCount'],reason=s['reason']) for s in h],existingCompiled=e.get('existingCompiled'),checkedCurrentIndexes=[dict(url=i['url'],status=i.get('status'),error=i.get('error'),locatedLinks=len(i.get('links',[]))) for i in indexes if i['employerSlug']==slug],historicalSearchIncomplete=True,priorPassFinding=e.get('status')))
    inventory.append(dict(employerSlug='nicola-valley-institute-of-technology',employerName='Nicola Valley Institute of Technology',sector='Universities and colleges',identityStatus='missing-public-institution-in-current-application',identitySourceUrl='https://www2.gov.bc.ca/gov/content/education-training/post-secondary-education/institution-resources-administration/mandate-letters',sourceIndexUrl='https://www.nvit.ca/about-us/governance/transparency/',baselineOfficialSources=[],newVerifiedSources=[],heldCandidates=[],historicalSearchIncomplete=True,coverageFinding='25th public institution confirmed from provincial mandate-letter roster; current official transparency page retrieved; no complete employee SOFI found in public search. Audited financial statements/executives remain separate scopes.'))
    dump(AUDIT/'inventory.json',dict(verifiedOn='2026-11-01',publicInstitutionCount=25,existingEmployersChecked=24,newPublicInstitutionIdentities=1,employers=inventory))
    oldqueue=json.loads((DISCOVERY/'work-queue.json').read_text());queue=[]
    accepted_keys={(s['employerSlug'],s['year'],s['sourceUrl']) for s in accepted}|{(s['employerSlug'],s['year'],s['sourceUrl']) for s in base}
    for i,t in enumerate(oldqueue):
        if any((t['employerSlug'],y,t['sourceUrl']) in accepted_keys for y in t['reportingPeriods']):continue
        t=dict(t);t['id']=f'continuation-education-prior-{i+1:03}'
        matches=[s for s in held if s['employerSlug']==t['employerSlug'] and s['year'] in t['reportingPeriods'] and s['sourceUrl']==t['sourceUrl']]
        if matches:t.update(status='held-material-source-control-discrepancy',route='processing',nextAction='Independently review the complete original named rows, board scope and summary controls; retain exact residual warning; do not infer its cause.',reason=matches[0]['reason'])
        queue.append(t)
    for s in accepted+held:
        if s['employerSlug']!='camosun-college':continue
        queue.append(dict(id='continuation-education-'+s['id']+'-board-employee-duty-subcohort',employerSlug=s['employerSlug'],employerName=s['employerName'],sector=s['sector'],reportingPeriods=[s['year']],sourceUrl=s['sourceUrl'],sourceIndexUrl=s['sourceIndexUrl'],status='public-original-requires-mixed-scope-extraction',route='processing',nextAction='Extract disjoint employee-duty pay and expenses from physical board-table page7; preserve retainers separately and exclude elected-student Student Society work from College employee scope. Import board remuneration only as its own scope. Severance remains excluded; retain partial flags.',reason='The employee schedule explicitly excludes board-member employees. Latest2025/26 board table has five College employee-duty remuneration rows and separate retainers; student remuneration is expressly Student Society work.'))
    queue.append(dict(id='continuation-education-nvit-public-employee-history',employerSlug='nicola-valley-institute-of-technology',employerName='Nicola Valley Institute of Technology',sector='Universities and colleges',reportingPeriods=['2017/18','2020/21','2023/24','2024/25','2025/26','earlier available history'],sourceUrl=None,sourceIndexUrl='https://www.nvit.ca/about-us/governance/transparency/',status='missing-inventory-employer-public-history-unresolved',route='public-archive-research',nextAction='Search official board packages and former nvit.ca document paths for complete adopted employee remuneration/expense SOFIs; then prepare an ordinary-copy request draft if public archives fail. Do not send any request.',reason='Provincial roster confirms public institution absent from application. Public search and current transparency page did not locate complete employee schedules; audited statements and executive reports do not substitute.'))
    if (AUDIT/'new-document-receipts.json').exists():
        for i,d in enumerate(json.loads((AUDIT/'new-document-receipts.json').read_text())):
            if any(s['sourceUrl']==d['url'] for s in accepted):continue
            employer=next(e for e in old['employers'] if e['employerSlug']==d['employerSlug'])
            pdf=d.get('pdfStatus') in ['native-text-candidate','period-review-required']
            queue.append(dict(id=f'continuation-education-new-discovery-{i+1:02}',employerSlug=d['employerSlug'],employerName=employer['employerName'],sector='Universities and colleges',reportingPeriods=[d['candidateReportingPeriod']] if d.get('candidateReportingPeriod') else [],sourceUrl=d['url'],sourceIndexUrl=d['indexUrl'],status='new-original-requires-processing' if pdf else 'search-indexed-original-not-successfully-retrieved',route='processing' if pdf else 'public-archive-research',nextAction='Extract all employee pages with independent engines/OCR as needed; check internal periods, monetary columns and source controls.' if pdf else 'Find current official mirror or archival original for the exact indexed lead; do not treat returned HTML or404 as a verified PDF.',reason=d.get('error') or ('Retrieved original fingerprint and cache are in new-document-receipts.json; a located PDF is not accepted coverage.' if pdf else 'Retrieval returned non-PDF content.')))
    dump(AUDIT/'work-queue.json',queue)
    snapshot=json.loads(gzip.decompress((ROOT/'research/salaries/compiled-baseline.json.gzip').read_bytes()));replacements=[]
    for s in accepted:
        e=next((e for e in snapshot['employers'] if e['slug']==s['employerSlug']),None)
        if e is None or s['year'] not in snapshot['years']:continue
        yi=snapshot['years'].index(s['year']);rows=[r for r in e['rows'] if r[4]==yi];board=[r for r in rows if re.search(r'(?i)(board|governor|trustee|honorari)',r[1] or '')];execs=[r for r in rows if re.search(r'(?i)(president|vice.president|vp|chief|executive|provost)',r[1] or '')]
        replacements.append(dict(sourceId=s['id'],employerSlug=s['employerSlug'],year=s['year'],completeEmployeeSchedule=s['completeEmployeeSchedule'],officialRows=s['rowCount'],compiledRows=len(rows),retainCompiledPartition=s.get('retainCompiledPartition',False),boardOrGovernorTitleRows=board,executiveTitleRowCount=len(execs),boardOrGovernorTitleRowCount=len(board),titleCaution='Titles identify review candidates, not independently established category or period.',allAffectedCompiledRows=rows))
    dump(AUDIT/'compiled-replacement-review.json',replacements)
    print(f'Inventoried {len(inventory)} public institutions; {len(queue)} unresolved tasks; {len(accepted)} verified cohorts / {sum(s["rowCount"] for s in accepted)} rows; {len(held)} held cohorts')

if __name__=='__main__':main()
