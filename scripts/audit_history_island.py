#!/usr/bin/env python3
"""Reconcile the Island archive inventory and normalized remaining-work queue."""
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re
import fitz

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'research/salaries/municipal-history-pass/island'
COLLECTION=ROOT/'research/salaries/municipal-history-island'
CACHE=Path('/tmp/pofbc-history-island')
ROUTES={'processing','public-archive-research','ordinary-records-request','clarification-request','foi-fallback'}

def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def direct(url):return bool(re.search(r'(?i)\.pdf(?:$|\?)|/document/\d+|/media/file/',url))

def main():
    baseline=json.loads((AUDIT.parent/'baseline.json').read_text());base={r['employerSlug']:r for r in baseline['municipalities']}
    prior=json.loads((ROOT/'research/salaries/municipal-next-pass/island/inventory.json').read_text())['entries']
    old={r['employerSlug']:r for r in json.loads((ROOT/'research/salaries/municipal-audit/coverage.json').read_text())['municipalities']}
    current={r['employerSlug']:r for r in json.loads((AUDIT/'index-receipts.json').read_text())}
    receipts=json.loads((AUDIT/'retrieval-receipts.json').read_text());retrieved={r['sourceUrl']:r for r in receipts}
    assessments={r['sourceUrl']:r for r in json.loads((AUDIT/'source-assessments.json').read_text())}
    fresh=json.loads((COLLECTION/'sources.json').read_text())['sources'];accepted=[]
    for collection in json.loads((ROOT/'research/salaries/collections.json').read_text())['collections']:
        if collection=='municipal-history-island':continue
        path=ROOT/'research/salaries'/collection/'sources.json'
        if not path.exists():continue
        raw=json.loads(path.read_text());sources=raw.get('sources',[])if isinstance(raw,dict)else raw
        accepted.extend(sources)
    allsources=accepted+fresh
    byurl=defaultdict(list)
    for source in allsources:
        if source.get('sourceUrl'):byurl[(source.get('employerSlug'),source['sourceUrl'])].append(source)
    queue=[];entries=[];seen_tasks=set()
    def task(slug,suffix,periods,url,status,route,action,reason):
        key='history-island-'+slug+'-'+suffix
        if key in seen_tasks:return
        seen_tasks.add(key);r=base[slug]
        queue.append(dict(id=key,employerSlug=slug,employerName=r['employerName'],sector='Municipalities',reportingPeriods=periods,sourceUrl=url,sourceIndexUrl=r['archiveUrl']if 'archiveUrl'in r else old[slug]['archiveUrl'],status=status,route=route,nextAction=action,reason=reason))
    for prev in prior:
        slug=prev['employerSlug'];r=old[slug];b=base[slug];index=current[slug];links={}
        for l in r['sourceLeads']+index['links']:
            if re.search(r'(?i)sofi|financial.?information',l.get('label','')+' '+l['url'])and direct(l['url']):links.setdefault(l['url'],l)
        for sr in receipts:
            if sr['employerSlug']==slug:links.setdefault(sr['sourceUrl'],dict(label=sr['label'],url=sr['sourceUrl']))
        for sr in allsources:
            if sr.get('employerSlug')==slug and sr.get('sourceUrl')and direct(sr['sourceUrl']):links.setdefault(sr['sourceUrl'],dict(label=sr.get('title',''),url=sr['sourceUrl']))
        docs=[]
        for url,l in links.items():
            rr=retrieved.get(url);ss=byurl[(slug,url)];periods=sorted({str(s['year'])for s in ss});categories=sorted({s.get('category','unknown')for s in ss});both={'employee-remuneration','elected-officials'}.issubset(categories)
            d=dict(label=l.get('label',''),sourceUrl=url,sourceIndexUrl=r['archiveUrl'],indexLabelYearHints=sorted(set(re.findall(r'\b(?:19|20)\d{2}\b',l.get('label','')))),verifiedAcceptedReportingPeriods=periods,acceptedCategories=categories,acceptedSourceIds=[s['id']for s in ss],reportingPeriodStatus='accepted-schedule-period-verified'if ss else'unverified-do-not-infer-from-label-or-upload')
            if rr:
                d['retrieval']=rr
                if rr['status']in ['downloaded','cached-original-reused']:
                    doc=fitz.open(rr['localPdf']);assessment=[]
                    native_profiles={tuple(s.get('pages',[]))for s in fresh if s['employerSlug']==slug and s['sourceUrl']==url}
                    reviewed_pages={n for p in native_profiles for n in p}
                    for n in rr['remunerationPages']:
                        p=doc[n-1];text=p.get_text();maxarea=max([fitz.Rect(x['bbox']).get_area()/p.rect.get_area()for x in p.get_image_info()]+[0])
                        if n in reviewed_pages or(re.search(r'(?i)(?:Position|Name)',text)and re.search(r'(?i)Expenses?',text)and re.search(r'(?i)(?:Total|Consolidated|Aggregate)',text)):
                            assessment.append(dict(physicalPdfPage=n,largestImageAreaFraction=round(maxarea,5),textChars=len(text),classification='scanned-page-with-OCR-overlay'if maxarea>.8 else'native-text-candidate',salaryPageVerified=n in reviewed_pages))
                    d['salaryPageAssessment']=assessment
                    d['textClassification']='verified-accepted-schedule'if both else'no-text-page-localization-and-OCR-needed'if rr['nativeTextChars']==0 else'salary-page-inspection-needed'if not assessment else'candidate-salary-pages-classified-not-yet-row-verified'
            else:d['retrieval']={'status':'located-public-link-not-retrieved-in-this-pass'}
            if url in assessments:
                assessed=assessments[url];assert rr and rr['sha256']==assessed['sha256'];d['additionalRenderedAssessment']=assessed;d['salaryPageAssessment'].append(dict(physicalPdfPage=4,classification=assessed['classification'],textChars=0,salaryPageVerified=False));d['textClassification']='scanned-salary-page-needs-full-row-verification';d['renderedPeriodProof']=assessed['printedPeriod'];d['verifiedReportPeriods']=assessed['reportingPeriods']
            docs.append(d)
            if not both:
                p=periods or(d.get('verifiedReportPeriods')or['unknown']);hint=(', '.join(d['indexLabelYearHints'])or'not stated');rs=d['retrieval']['status'];ocr='OCR and complete image transcription/control verification'if rr and(rr.get('nativeTextChars')==0 or any(a['classification'].startswith('scanned')for a in d.get('salaryPageAssessment',[])))else'source-specific salary-page extraction and complete independent row/control verification'
                missing='Council cohort remains unaccepted; preserve any accepted employee cohort.'if 'employee-remuneration'in categories else'Employee and council cohorts require separate verification; preserve any already accepted cohort.'
                route='public-archive-research'if rs=='retrieval-failed'else'processing'
                task(slug,'document-'+hashlib.sha256(url.encode()).hexdigest()[:10],p,url,'public-report-awaits-'+('retrieval-recovery'if route=='public-archive-research'else'processing'),route,f"Retrieve or reopen this official original, confirm the salary schedule's own period and scope, and complete {ocr}. {missing}",f"Located index label year hint: {hint}. {rs}; labels and upload dates are not accepted salary periods. "+('Existing accepted coverage identifies the report period, but not every category.'if ss else'No named cohort from this original is accepted by this pass.'))
        new=[s for s in fresh if s['employerSlug']==slug]
        entries.append(dict(municipality=r['municipality'],employerSlug=slug,employerName=r['employerName'],regionalDistrict=r['regionalDistrict'],sourceIndexUrl=r['archiveUrl'],indexCheck=index,baselineOfficialEmployeeYears=b['officialEmployeeYears'],baselineOfficialCouncilYears=b['officialCouncilYears'],baselineCompiledEditionLabels=b['compiledUnverifiedEditionLabels'],acceptedThisPass=[dict(id=s['id'],year=s['year'],category=s['category'],rowCount=s['rowCount'],sourceUrl=s['sourceUrl'],sha256=s['sha256'],pages=s['pages'],publicWarning=s.get('publicWarning'))for s in new],locatedSofiDocuments=docs,archiveCompleteness='All retained and freshly located direct SOFI links are inventoried; deeper agenda/archive research and pre-index histories are not exhausted. Index labels are leads unless an accepted schedule establishes the period.'))
        if slug=='shishalh-nation-government-district':
            task(slug,'governance-and-public-records',['unknown'],r['archiveUrl'],'distinct-governance-public-disclosure-review','public-archive-research','Identify the district governance and applicable public-disclosure framework, then locate public remuneration evidence or establish the appropriate records contact.','This is a separate governance case. Do not assume ordinary municipal SOFI production or municipal FOI obligations.')
        else:
            task(slug,'earlier-unindexed-archives',['unknown'],r['archiveUrl'],'earlier-archive-coverage-not-established','public-archive-research','Search older official agenda packages, archived finance pages and linked source workbooks for periods before or between the located reports; verify each printed salary period before declaring a gap.','The checked current index and located documents do not establish complete historical availability or a universal earlier-year missing-report denominator.')
    for s in fresh:
        if s.get('publicWarning'):
            task(s['employerSlug'],'clarify-'+s['year']+'-'+s['category'],[s['year']],s['sourceUrl'],'accepted-published-fields-retained-source-question-open','clarification-request','Seek an existing corrected schedule or issuer explanation for the exact documented source issue; retain the qualified accepted values and warning until new authoritative evidence is verified.',s['publicWarning'])
    # Retain precise earlier clarification work that remains unresolved.
    for t in json.loads((ROOT/'research/salaries/municipal-next-pass/island/work-queue.json').read_text()):
        if t['route']=='clarification-request':
            t=dict(t);t['id']='history-carry-'+t['id'];queue.append(t)
    # Existing electronic copies can be requested without presuming an FOI need.
    for slug,periods in [('town-of-port-mcneill',['2022','2023','2024','2025']),('village-of-alert-bay',['unknown'])]:
        task(slug,'existing-electronic-disclosures',periods,old[slug]['archiveUrl'],'ordinary-acquisition-option-after-targeted-public-search','ordinary-records-request','After the targeted public archive search, ask for existing SOFI employee/council schedules and original electronic spreadsheets for the requested periods, or an inventory of available years when unknown. Escalate to a formal records process only if an ordinary request cannot obtain existing records.','The checked index has no matching standalone named-disclosure link for these requested periods. This does not prove that records do not exist or that a formal FOI request is required.')
    summary=dict(rosterEntriesReviewed=len(entries),municipalEntries=22,distinctGovernanceCases=1,acceptedSources=len(fresh),acceptedRecords=sum(s['rowCount']for s in fresh),acceptedEmployeeRecords=sum(s['rowCount']for s in fresh if s['category']=='employee-remuneration'),acceptedCouncilRecords=sum(s['rowCount']for s in fresh if s['category']=='elected-officials'),acceptedMunicipalities=len({s['employerSlug']for s in fresh}),reportDocumentsRetrieved=sum(r['status']in ['downloaded','cached-original-reused']for r in receipts),directLocatedSofiLinks=sum(len(e['locatedSofiDocuments'])for e in entries),queueTasks=len(queue),externalRequestsSent=0)
    dump(AUDIT/'inventory.json',dict(version=1,asOf='2026-10-31',timezone='America/Vancouver',baselineCommit=baseline['repositoryCommit'],baselineDatasetRecords=baseline['overall']['records'],scope='Island/coast outside Capital and Cowichan;22 municipalities plus distinct shishalh governance case',summary=summary,entries=entries))
    fields={'id','employerSlug','employerName','sector','reportingPeriods','sourceUrl','sourceIndexUrl','status','route','nextAction','reason'}
    assert len({x['id']for x in queue})==len(queue)
    for t in queue:assert set(t)==fields and t['route']in ROUTES and t['reportingPeriods']
    dump(AUDIT/'work-queue.json',queue)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
