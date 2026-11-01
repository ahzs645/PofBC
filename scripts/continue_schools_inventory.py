#!/usr/bin/env python3
"""Reconcile all sixty school identities, reviewed cohorts and acquisition tasks."""
import collections
import json
import re
from pathlib import Path

import continue_schools as s

def read(path):return json.loads(path.read_text())

def period_label(year):return f'{year-1}/{str(year)[-2:]}'

def main():
    old=read(s.ROOT/'research/salaries/sector-search-2026-10-31/schools/findings.json')
    current=read(s.COLLECTION/'sources.json')['sources'];held=read(s.INVENTORY/'held-candidates.json')
    registered=[]
    for collection in read(s.ROOT/'research/salaries/collections.json')['collections']:
        if collection=='continuation-schools':continue
        for src in read(s.ROOT/'research/salaries'/collection/'sources.json')['sources']:
            if src.get('sector')=='School districts':registered.append(src)
    indexes=read(s.INVENTORY/'district-index-receipts.json')
    new_receipts=read(s.INVENTORY/'new-district-source-receipts.json')
    history=read(s.INVENTORY/'ministry-history-receipts.json')
    old_hashes={r.get('sha256') for e in old['employers'] for r in e['sourceCandidates'] if r.get('sha256')}
    employers=[];queue=[];identities=[]
    for e in old['employers']:
        n=e['districtNumber'];slug=e['slug'];accepted=[r for r in current if r['employerSlug']==slug];baseline=[r for r in registered if r['employerSlug']==slug];pending=[r for r in held if r['employerSlug']==slug]
        ii=[r for r in indexes if r['districtNumber']==n];rr=[r for r in new_receipts if r['districtNumber']==n]
        candidates=list(e['sourceCandidates'])+rr
        indexed=set(e['archiveRange']['indexedFiscalYears'])
        for r in rr:
            # Report headings establish these periods; arbitrary URL years do not.
            if r.get('headingEvidence'):
                y=int(r['headingEvidence'][0]['text'][-4:]);indexed.add(period_label(y))
        located_links=[l for r in ii for l in r.get('relevantLinks',[])]
        coverage=[{'id':r['id'],'year':r['year'],'category':r['category'],'rows':r['rowCount'],'sourceUrl':r['sourceUrl'],'publicWarning':r.get('publicWarning'),'summaryReconciles':r.get('validation',{}).get('summaryReconciles')} for r in baseline+accepted]
        missing_current=[cat for cat in ['employee-remuneration','school-trustees'] if not any(r['year']=='2024/25' and r['category']==cat for r in baseline+accepted)]
        current_source=next(r for r in e['sourceCandidates'] if r['id']==f'ministry-sd{n:02}-2025')
        employers.append({'districtNumber':n,'employerSlug':slug,'employerName':e['name'],'directoryName':e['directoryName'],'sector':'School districts',
                          'identityStatus':e['slugStatus'],'existingCompiledSlugs':e['existingCompilerSlugs'],'compiledCoverage':e['compiledCoverage'],
                          'acceptedCohorts':coverage,'heldCohorts':[{'id':r['id'],'year':r['year'],'category':r['category'],'status':r['status'],'reason':r['publicWarning']} for r in pending],
                          'currentFiscal2024_25MissingCategories':missing_current,'currentOfficialSource':current_source,
                          'knownPeriodLabelsFromPriorIndexOrNewHeadings':sorted(indexed),'newArchiveIndexReceipts':ii,'districtArchiveLinks':located_links,
                          'sourceCandidates':candidates,'historicalEndpointReceipts':[r for r in history if r['districtNumber']==n],
                          'historyCompleteness':'Not established. Located/indexed files are distinguished from accepted individual schedules; earlier district and Legislative Library records remain to be checked.',
                          'nextAction':('Process current '+', '.join(missing_current)+'; ' if missing_current else '')+'Process located unaccepted native/scan schedules and check district board packages plus Legislative Library holdings for earlier annual SOFI employee/trustee schedules.'})
        def task(suffix,periods,url,index,status,route,action,reason):
            queue.append({'id':f'continuation-schools-sd{n:02}-{suffix}','employerSlug':slug,'employerName':e['name'],'sector':'School districts','reportingPeriods':periods,'sourceUrl':url,'sourceIndexUrl':index,'status':status,'route':route,'nextAction':action,'reason':reason})
        if missing_current:
            task('2025-processing',['2024/25'],current_source['sourceUrl'],current_source['sourceIndexUrl'],'located-unaccepted-current-scope','processing','Review the complete original named schedule, scope, exact period, all monetary columns and independent extraction; preserve separate employee/trustee scopes.','Current source already retrieved in the prior search; still missing accepted '+', '.join(missing_current)+'. OCR is processing, not a procurement or FOI gap.')
        for h in pending:
            task(h['id'].replace('continuation-schools-','')+'-held',[h['year']],h['sourceUrl'],h['sourceIndexUrl'],h['status'],'clarification-request' if 'period' in h['status'] else 'processing','Independently review the complete original scope/control and visible warning. For a conflicting source year, seek an existing corrected public schedule or draft a clarification request; do not infer a typo or alter rows to balance.',h['publicWarning'])
        for accepted_source in accepted:
            residuals=accepted_source['validation']['controlResiduals']
            if any(value is not None and float(value)!=0 for value in residuals):
                task(accepted_source['id'].replace('continuation-schools-','')+'-issuer-clarification',[accepted_source['year']],accepted_source['sourceUrl'],accepted_source['sourceIndexUrl'],'accepted-observations-unresolved-issuer-controls','clarification-request','Keep the accepted faithful observations and their exact public warning. Draft an unsent request for an existing explanatory reconciliation or corrected annual schedule; do not change a row or infer a cause while awaiting issuer evidence.',accepted_source['publicWarning'])
        known_missing=sorted(p for p in indexed if not all(any(r['year']==p and r['category']==cat for r in baseline+accepted) for cat in ['employee-remuneration','school-trustees']))
        if known_missing or located_links:
            link=next((l for l in located_links if not l['url'].startswith('https://www2.gov.bc.ca/gov/')),None)
            task('located-history-processing',known_missing,link['url'] if link else current_source['sourceUrl'],ii[0]['url'] if ii else e['archiveRange']['indexUrls'][0] if e['archiveRange']['indexUrls'] else old['centralIndexUrl'],'located-history-unaccepted-scopes','processing','Process exact located annual employee/trustee schedules that are not already accepted. Confirm headings, file identity and original scope before parsing; scanned or OCR-overlay files need independent rendered reading.','A source link or extracted native text is discovery evidence, not an accepted historical cohort. Misleading labels and migrated URLs are retained in receipts.')
        task('earlier-archive-research',[],current_source['sourceUrl'],ii[0]['url'] if ii else old['centralIndexUrl'],'earlier-period-discovery-incomplete','public-archive-research','Search district finance archives, board agendas/attachments, old domain migrations and BC Legislative Library SOFI holdings for specific unaccepted earlier periods. If public routes fail, draft an ordinary request for existing accessible schedules before considering FOI.','The complete earlier annual run has not been established. Six Ministry historical endpoint probes per district returned retrieval errors; those responses do not establish that the records do not exist.')
        if accepted or pending:
            identities.append({'districtNumber':n,'manifestSlug':slug,'employerName':e['name'],'slugStatus':e['slugStatus'],'existingCompiledSlugs':e['existingCompilerSlugs'],'compiledSameLabelReplacementCandidate':bool(e['existingCompilerSlugs']),'compiledBoardOrExecutiveLossIdentified':False,'integrationAction':'Parent to review employer identity and choose aliases/canonical naming. Worker made no alias, registry or compiled-data changes.','acceptedSourceIds':[r['id'] for r in accepted],'heldSourceIds':[r['id'] for r in pending]})
    summary={'rosterDistricts':len(employers),'currentOfficialSourcesInventoried':60,'registeredPriorCohorts':len(registered),'newVerifiedCohorts':len(current),'newVerifiedRows':sum(r['rowCount'] for r in current),'newVerifiedEmployers':len({r['employerSlug'] for r in current}),'heldCohorts':len(held),'heldRows':sum(r['rowCount'] for r in held),'publicIndexesRetrievedOrAttempted':len(indexes),'indexLinksLocated':sum(len(r.get('relevantLinks',[])) for r in indexes),'newDistrictPDFReceipts':len(new_receipts),'distinctNewDistrictHashesNotInPriorReceipts':len({r['sha256'] for r in new_receipts if r.get('sha256') and r['sha256'] not in old_hashes}),'ministryHistoryEndpointAttempts':len(history),'routeCounts':dict(collections.Counter(r['route'] for r in queue))}
    (s.INVENTORY/'inventory.json').write_text(json.dumps({'auditDate':'2026-11-01','sector':'School districts','summary':summary,'employers':employers},ensure_ascii=False,indent=2)+'\n')
    (s.INVENTORY/'work-queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
    (s.INVENTORY/'identity-and-compiled-review.json').write_text(json.dumps(identities,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary))

if __name__=='__main__':main()
