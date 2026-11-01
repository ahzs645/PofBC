#!/usr/bin/env python3
"""Summarize retained Southern Interior discovery receipts and unresolved work."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import urllib.request

import fitz

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/salaries/municipal-next-pass/interior'
COLLECTION=ROOT/'research/salaries/municipal-wave-interior'


def build(cache,fetch=False):
    municipalities=json.loads((BASE/'baseline-leads.json').read_text())
    receipts=json.loads((BASE/'discovery-receipts.json').read_text())
    sources=json.loads((COLLECTION/'sources.json').read_text())['sources']
    held=json.loads((BASE/'held-cohorts.json').read_text())
    app=json.loads((ROOT/'public/salaries/employers/index.json').read_text())
    existing={e['slug']:e for e in app['employers']}
    labels={}
    for receipt in receipts:
        for anchor in receipt.get('links',[]):labels.setdefault(anchor['url'].rstrip('/').casefold(),[]).append(anchor['text'])
    for municipality in municipalities:
        for lead in municipality['sourceLeads']:
            labels.setdefault(lead['url'].replace('http:','https:').rstrip('/').casefold(),[]).append(lead.get('label',''))
    accepted_by_sha={}
    for source in sources:accepted_by_sha.setdefault(source['sha256'],[]).append(source)
    docs=[]
    for receipt in receipts:
        if 'cacheFile' not in receipt:continue
        record={k:v for k,v in receipt.items() if k!='links'}
        record['indexLabels']=sorted(set(labels.get(receipt['sourceUrl'].rstrip('/').casefold(),[])))
        years=sorted(set(re.findall(r'20\d{2}',' '.join(record['indexLabels']))))
        record['indexedReportingYears']=years
        record['indexedYearIsVerifiedPeriod']=False
        path=cache/receipt['cacheFile']
        if not path.exists() and fetch:
            cache.mkdir(parents=True,exist_ok=True)
            with urllib.request.urlopen(urllib.request.Request(receipt['sourceUrl'],headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as response:path.write_bytes(response.read())
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest()!=receipt['sha256']:raise ValueError('Original changed: '+str(path))
            with fitz.open(path) as doc:
                texts=[page.get_text() for page in doc];record['pdfPages']=len(doc);record['textChars']=sum(map(len,texts));record['remunerationCandidatePhysicalPages']=[i+1 for i,text in enumerate(texts) if re.search(r'remuneration|renumeration',text,re.I) and re.search(r'employee|council|elected',text,re.I)]
                record['textStatus']='text-layer-present-source-layout-and-any-OCR-errors-require-review' if record['textChars']>1000 else 'scan-or-text-unavailable-needs-OCR'
        accepted=accepted_by_sha.get(receipt['sha256'],[])
        record['acceptedCohorts']=[{k:s[k] for k in ['id','year','category','rowCount','pages','publicWarning']} for s in accepted]
        record['status']='accepted-in-part-or-full-see-cohort-scopes' if accepted else 'retrieved-processing-needed'
        record['rowControlsReviewed']=bool(accepted)
        record['nextAction']='Preserve accepted source evidence; process only remaining employee/council scopes or periods.' if accepted else 'Locate actual calendar heading and complete named cohorts; prefer usable text layers, then OCR scans, verify all row fields against originals, and reconcile all printed components.'
        docs.append(record)
    queue=[];findings=[]
    for municipality in municipalities:
        slug=municipality['employerSlug'];name=municipality['employerName'];selected=[d for d in docs if d['employerSlug']==slug];accepted=[s for s in sources if s['employerSlug']==slug]
        prior_employee=[];prior_council=[]
        if slug in existing:
            for index,coverage in enumerate(existing[slug]['coverage']):
                for source_id in coverage.get('sourceIds',[]):
                    if source_id.startswith('wave-interior-'):continue
                    source=app['sources'][source_id]
                    if source.get('sourceKind')=='compiled':continue
                    (prior_council if source.get('scope')=='elected-officials' else prior_employee).append(app['years'][index])
        item={'employerSlug':slug,'employerName':name,'sector':'Municipalities','regionalDistrict':municipality['regionalDistrict'],'statusInRoster':municipality['status'],'officialEmployeeYearsBeforeWave':sorted(set(prior_employee)),'officialCouncilYearsBeforeWave':sorted(set(prior_council)),'newAcceptedEmployeeYears':sorted({s['year'] for s in accepted if s['category']=='employee-remuneration'}),'newAcceptedCouncilYears':sorted({s['year'] for s in accepted if s['category']=='elected-officials'}),'archiveUrl':municipality['archiveUrl'],'website':municipality['website'],'boundedDiscoveryStatus':'original-reports-retrieved' if selected else 'prior-audit-leads-retained-not-completely-researched-this-wave','sources':selected,'sourceLeads':municipality['sourceLeads']}
        findings.append(item)
        if municipality['status']!='current':continue
        pending=[d for d in selected if not d['acceptedCohorts']]
        if pending and slug!='city-of-merritt':
            first=pending[0];periods=sorted({year for d in pending for year in d['indexedReportingYears']})
            queue.append({'id':'wave-interior-'+slug+'-located-history-processing','employerSlug':slug,'employerName':name,'sector':'Municipalities','reportingPeriods':periods or ['Located reports; actual periods await original heading review'],'sourceUrl':first['sourceUrl'],'sourceIndexUrl':municipality['archiveUrl'],'status':'official-originals-retrieved-not-yet-accepted','route':'processing','nextAction':'Process each exact original listed in source-inventory.json, validating calendar periods, complete employee/council scope, all row fields and printed controls. Prefer native text or useful text layers before OCR; correct text recognition only from rendered originals.','reason':str(len({d['sha256'] for d in pending}))+' distinct official PDFs are already retrieved and fingerprinted. Processing is not procurement.'})
        if not prior_employee and not item['newAcceptedEmployeeYears'] and not selected:
            queue.append({'id':'wave-interior-'+slug+'-employee-source-discovery','employerSlug':slug,'employerName':name,'sector':'Municipalities','reportingPeriods':['Prioritize2025, then establish actual historical availability'],'sourceUrl':municipality['archiveUrl'],'sourceIndexUrl':municipality['archiveUrl'],'status':'prior-official-audit-lead-needs-deeper-search','route':'public-archive-research','nextAction':'Follow retained official finance/council leads and locate the original named employee SOFI. Check current and older board/council attachments; if unavailable publicly, request existing reports or spreadsheets informally before considering an FOI fallback.','reason':'This bounded wave prioritized retrievable originals for new employee coverage. No complete history or public unavailability has been established for this municipality.'})
        if selected:
            years=sorted({year for d in selected for year in d['indexedReportingYears']})
            queue.append({'id':'wave-interior-'+slug+'-older-archive-research','employerSlug':slug,'employerName':name,'sector':'Municipalities','reportingPeriods':['Earlier than located archive range; exact missing years not established'],'sourceUrl':municipality['archiveUrl'],'sourceIndexUrl':municipality['archiveUrl'],'status':'historical-discovery-incomplete','route':'public-archive-research','nextAction':'Follow the recorded official archive and older meeting packages to establish earlier available SOFI periods. Read original period headings, retain original links/hashes, and request existing copies only after public retrieval routes are checked.','reason':'Located index labels include '+(', '.join(years) if years else 'unverified periods')+'. An index range is not a claim that all older reports have been located or require FOI.'})
    for item in held:
        report=item['report'];cohort=item['cohort'];slug=report['employerSlug'];queue.append({'id':'wave-interior-'+slug+'-'+report['year']+'-held-employee-controls','employerSlug':slug,'employerName':report['employerName'],'sector':'Municipalities','reportingPeriods':[report['year']],'sourceUrl':report['sourceUrl'],'sourceIndexUrl':report['indexUrl'],'status':'accepted-qualified-unresolved-expense-control','route':'clarification-request','nextAction':'Seek an explanation or amended original expense control when practical. The complete published employee schedule is already accepted with visible qualification; preserve all source values and any missing expense cells. No external request has been sent.','reason':item['reason']+' Exact row-sum-minus-control residuals in cents: '+json.dumps(cohort['reviewedResidualsCents'])})
    merritt=next(d for d in docs if d['employerSlug']=='city-of-merritt')
    queue.append({'id':'wave-interior-city-of-merritt-2025-components-review','employerSlug':'city-of-merritt','employerName':'City of Merritt','sector':'Municipalities','reportingPeriods':['2025'],'sourceUrl':merritt['sourceUrl'],'sourceIndexUrl':'https://www.merritt.ca/government/annual-reports-and-financial-statements/','status':'grant-expenses-and-aggregate-scope-held','route':'processing','nextAction':'Read the full current named cohort independently, map ordinary and grant-funded expense columns separately, and resolve the scope of the printed Total Employees aggregate before proposing an import. Seek clarification if the original does not resolve these definitions.','reason':'Named remuneration subtotal4,779,040.10 plus under-threshold2,876,685.82 is7,655,725.92; the printed Total Employees(B)7,842,227.42 is186,501.50 higher, exactly the separately printed council remuneration. Individual grant expense definitions still need full source review; nothing imported.'})
    summary={'scopedRosterEntries':len(findings),'originalPdfUrlReceipts':len(docs),'distinctOriginalPdfHashes':len({d['sha256'] for d in docs}),'newAcceptedRecords':sum(s['rowCount'] for s in sources),'newAcceptedEmployeeRecords':sum(s['rowCount'] for s in sources if s['category']=='employee-remuneration'),'newAcceptedCouncilRecords':sum(s['rowCount'] for s in sources if s['category']=='elected-officials'),'acceptedCohorts':len(sources),'newOfficialJurisdictions':len({s['employerSlug'] for s in sources}),'jurisdictionsWithNewEmployeeSchedules':len({s['employerSlug'] for s in sources if s['category']=='employee-remuneration'}),'heldEmployeeCohorts':sum(h.get('status','').startswith('held') for h in held),'qualifiedEmployeeCohorts':sum(h.get('status','').startswith('accepted-qualified') for h in held),'workQueue':len(queue),'workByRoute':dict(Counter(q['route'] for q in queue))}
    (BASE/'source-inventory.json').write_text(json.dumps({'version':1,'asOf':'2026-11-01','cacheDirectory':str(cache),'sources':docs},ensure_ascii=False,indent=2)+'\n')
    (BASE/'findings.json').write_text(json.dumps({'version':1,'asOf':'2026-11-01','summary':summary,'acceptedCollection':'research/salaries/municipal-wave-interior/sources.json','receiptFile':'discovery-receipts.json','inventoryFile':'source-inventory.json','heldEvidenceFile':'held-cohorts.json','edgeReviewFile':'edge-review.json','requestStatus':'No requests, emails or other external messages were sent.','municipalities':findings},ensure_ascii=False,indent=2)+'\n')
    (BASE/'work-queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cache-dir',type=Path,default=Path('/tmp/wave-interior'));parser.add_argument('--fetch',action='store_true');args=parser.parse_args();build(args.cache_dir,args.fetch)


if __name__=='__main__':main()
