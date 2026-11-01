#!/usr/bin/env python3
"""Reconcile retained Interior public-source leads against accepted historical cohorts."""
import gzip
import hashlib
import json
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import re
import fitz

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/salaries/municipal-history-pass/interior'
COLLECTION=ROOT/'research/salaries/municipal-history-interior'
CACHE=Path('/tmp/wave-interior')

def load(path):return json.loads(path.read_text())
def save(name,value):(BASE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def fingerprint(raw):return hashlib.sha256(raw).hexdigest()

def main():
    receipts=load(BASE/'original-source-receipts.json')['sources'];indexes=load(BASE/'archive-index-receipts.json')
    manifest=load(COLLECTION/'sources.json');current=manifest['sources'];aggregate_only=manifest.get('aggregateOnlySources',[]);prior=load(ROOT/'research/salaries/municipal-wave-interior/sources.json')['sources'];all_sources=current+prior
    by_hash=defaultdict(list)
    for source in all_sources:by_hash[source['sha256']].append(source)
    names={s['employerSlug']:s['employerName'] for s in all_sources}
    names.update({'city-of-merritt':'City of Merritt','village-of-radium-hot-springs':'Village of Radium Hot Springs'})
    index_by_slug={q['employerSlug']:q['sourceIndexUrl'] for q in load(ROOT/'research/salaries/municipal-next-pass/interior/work-queue.json')}
    def find_index(receipt):
        matches=[r['sourceUrl'] for r in indexes if r['employerSlug']==receipt['employerSlug'] and any(link.get('url','').rstrip('/')==receipt['sourceUrl'].rstrip('/') for link in r.get('links',[]))]
        return matches[0] if matches else index_by_slug.get(receipt['employerSlug'],receipt['sourceUrl'])
    inventory=[];unique={};queue=[];reviewed={s['id']:s for s in current}
    def task(slug,tag,periods,url,index,status,route,action,reason):
        queue.append(dict(id=f'history-interior-{slug}-{tag}',employerSlug=slug,employerName=names.get(slug,slug.replace('-',' ').title()),sector='Municipalities',reportingPeriods=periods,sourceUrl=url,sourceIndexUrl=index,status=status,route=route,nextAction=action,reason=reason))
    for lead in receipts:
        raw=(CACHE/lead['cacheFile']).read_bytes()
        assert fingerprint(raw)==lead['sha256'] and len(raw)==lead['bytes'],lead['sourceUrl']
        accepted=by_hash[lead['sha256']]
        doc=fitz.open(stream=raw,filetype='pdf');table_pages=[]
        for n in lead.get('remunerationCandidatePhysicalPages',[]):
            page=doc[n-1]
            coverages=[sum(rect.get_area() for rect in page.get_image_rects(image[0]))/page.rect.get_area() for image in page.get_images()]
            table_pages.append(dict(physicalPage=n,textCharacters=len(page.get_text()),images=len(page.get_images()),largestImageCoverage=round(max(coverages,default=0),3),isVerifiedSalaryPage=any(n in s.get('pages',[]) for s in accepted)))
        periods=sorted({s['year'] for s in accepted})
        entry=dict(employerSlug=lead['employerSlug'],employerName=names.get(lead['employerSlug'],lead['employerSlug'].replace('-',' ').title()),sector='Municipalities',sourceUrl=lead['sourceUrl'],sourceIndexUrl=find_index(lead),retrievedUrl=lead['retrievedUrl'],httpStatus=lead['httpStatus'],bytes=len(raw),sha256=lead['sha256'],cacheFile=lead['cacheFile'],originalHashReverified=True,indexLabels=lead.get('indexLabels',[]),indexedReportingPeriods=lead.get('indexedReportingYears',[]),verifiedReportingPeriods=periods,originalPages=len(doc),textCharacters=sum(len(page.get_text()) for page in doc),candidatePageStructure=table_pages,acceptedPriorCohorts=[dict(sourceId=s['id'],year=s['year'],category=s['category'],rows=s['rowCount']) for s in accepted if s not in current],acceptedNewCohorts=[dict(sourceId=s['id'],year=s['year'],category=s['category'],rows=s['rowCount'],publicWarning=s.get('publicWarning')) for s in accepted if s in current],status='accepted-see-specific-cohort-scopes' if accepted else 'retrieved-awaiting-period-scope-and-complete-row-review')
        if lead['employerSlug']=='city-of-merritt':entry['status']='assigned-to-dedicated-source-ambiguity-review-agent-no-duplicate-work'
        if lead['employerSlug']=='village-of-lytton' and lead.get('indexedReportingYears')==['2022']:
            entry['verifiedReportingPeriods']=['2022'];entry['status']='verified-aggregate-only-employees-official-scope-held';entry['aggregateOnlySourceId']=aggregate_only[0]['id'];entry['zeroNamedEmployeeEvidence']=dict(physicalPage=4,periodText='For the Fiscal Year 2022',heading='Employees over $75,000',publishedEntry='None',scope='No named above-threshold employee rows in this official schedule; not a claim of no employees.',verification='Native original and full rendered page reviewed. No zero-valued synthetic employee record is created.')
        if lead['employerSlug']=='village-of-lytton' and lead.get('indexedReportingYears')==['2022']:entry['heldOfficialScope']='Only the two Mayor roles are explicit in the published 2022 group; other individual elected/employment roles and the combined subtotal need source clarification.'
        if lead['employerSlug']=='village-of-lytton' and lead.get('indexedReportingYears')==['2023']:entry['heldOfficialScope']='Seven explicit council/former-council rows are accepted separately; three explicitly named fire-chief rows remain in supporting evidence pending employee/volunteer category scope review.'
        if lead['sha256']=='963a9c8569e7' or lead['cacheFile']=='city-of-rossland-963a9c8569e7.pdf':entry['periodConflict']='Two archive labels (SOFI2013 and SOFI2014) retrieve the same exact original. The schedule memorandum date and report year need explicit original-scope review before accepting either salary period.'
        inventory.append(entry);unique.setdefault(lead['sha256'],entry)
        doc.close()
    for original in unique.values():
        slug=original['employerSlug'];year=original['verifiedReportingPeriods'] or original['indexedReportingPeriods'];periods=year or ['Original reporting heading not yet verified; filename/upload year is only a lead']
        url,index=original['sourceUrl'],original['sourceIndexUrl'];accepted=original['acceptedNewCohorts']+original['acceptedPriorCohorts']
        if slug=='city-of-merritt':continue
        if not accepted:
            status='retrieved-original-processing-needed';route='processing';action='Locate the original remuneration table and printed reporting period; extract native text where usable, otherwise OCR rendered originals. Verify all row names, titles, monetary components, missing cells and physical-page boundaries with independent corroboration, then assess controls without balancing.'
            reason='Official original already retrieved and SHA256-locked. Extraction/OCR is processing, not procurement. Index and URL years are not verified salary periods.'
            if original.get('periodConflict'):
                periods=['Indexed2013 and indexed2014; the same original is returned, actual salary period unresolved'];status='duplicate-archive-label-period-review-needed';action='Review the SOFI fiscal-year checklist, remuneration memorandum and adjacent schedule pages together. Locate a distinct2014 original or earlier reporting-period statement through the official archive before assigning a salary year.';reason=original['periodConflict']
            if slug=='village-of-lytton' and original['indexedReportingPeriods']==['2022']:
                periods=['2022'];status='zero-named-employee-schedule-verified-official-scope-held';route='clarification-request';action='Clarify the scope of the published Elected Officials cohort and its inconsistent combined subtotal; identify elected roles versus fire/staff payments before importing the mixed group. An existing corrected report or native table is useful; no named above-threshold employee rows are missing from the printed schedule.';reason='The original explicitly says Employees over$75,000: None. The officials group contains role ambiguities; do not invent employee records or infer all people are councillors.'
            task(slug,'source-'+original['sha256'][:12],periods,url,index,status,route,action,reason)
        if slug=='village-of-lytton' and original['indexedReportingPeriods']==['2023']:
            task(slug,'2023-fire-service-scope',['2023'],url,index,'employees-and-council-accepted-fire-service-category-held','clarification-request','Clarify employment/volunteer status and the appropriate disclosure category for Kyle Parker, Dion Moody and Jason Phillips, whose printed roles are fire-service positions. All three rows are retained in supporting evidence; seven explicit council/former-council rows and three above-threshold employees are already accepted.','The table headed Elected Officials explicitly mixes council and fire chiefs. Printed fire-service pay is retained as evidence and is not relabelled as Mayor/council or assumed to establish salaried employment. This is a scope clarification, not an employee OCR gap.')
        if slug=='sun-peaks-mountain-resort-municipality' and accepted:
            task(slug,'2024-council-scope-review',['2024 council, employee schedule already accepted'],url,index,'employee-cohort-accepted-council-not-reviewed','processing','Review the remainder of the retained original for a separately named council schedule and its physical pages. If present, transcribe and independently verify it; do not repeat accepted employee rows.','Only the named employee cohort is currently accepted from this retained original; unreviewed source scope does not imply that a report needs procuring.')
        warned=[s for s in all_sources if s['sha256']==original['sha256'] and s.get('publicWarning')]
        if warned:
            task(slug,'clarify-controls-'+original['sha256'][:12],sorted({s['year'] for s in warned}),url,index,'faithful-records-accepted-with-visible-source-qualification','clarification-request','Seek an explanation, existing native table or corrected/adopted schedule for the exact published row/control differences recorded in source metadata. Preserve accepted source values and missing cells until an authoritative amendment establishes a change.',' | '.join(s['year']+' '+s['category']+': '+s['publicWarning'] for s in warned))
    for slug in sorted({s['employerSlug'] for s in inventory} - {'city-of-merritt'}):
        entries=[s for s in inventory if s['employerSlug']==slug];index=entries[0]['sourceIndexUrl'];known=sorted({y for s in entries for y in s['indexedReportingPeriods']+s['verifiedReportingPeriods']})
        task(slug,'additional-history-archive', ['Earlier/later or intervening archive years not yet located; exact missing periods not established'],index,index,'archive-discovery-incomplete','public-archive-research','Follow the official finance/report index and older council attachment archives to establish additional reporting periods. Record exact original links and actual printed periods, compare against accepted employee/council coverage, and request an existing copy routinely only after public retrieval routes are exhausted.','This bounded pass retained '+str(len({s['sha256'] for s in entries}))+' distinct originals. Located index/verified periods: '+(', '.join(known) if known else 'period labels require original review')+'. This is not a claim that every historical report has been found or that unlocated reports require FOI.')
    source_counts=Counter(s['category'] for s in current);row_counts=Counter()
    for s in current:row_counts[s['category']]+=s['rowCount']
    save('source-inventory.json',dict(version=1,asOf='2026-10-31',timezone='America/Vancouver',receiptOrigin='Retained exact public retrieval and official index receipts from initial Interior audit; original byte hashes reverified during this continuation.',cacheDirectory=str(CACHE),sourceLeads=len(inventory),distinctOriginals=len(unique),sources=inventory))
    save('work-queue.json',sorted(queue,key=lambda q:(q['employerName'],q['route'],q['id'])))
    employers=[]
    for slug in sorted({s['employerSlug'] for s in inventory}):
        sources=[s for s in inventory if s['employerSlug']==slug];new=[s for s in current if s['employerSlug']==slug];old=[s for s in prior if s['employerSlug']==slug]
        employers.append(dict(employerSlug=slug,employerName=names.get(slug,slug.replace('-',' ').title()),sector='Municipalities',acceptedPriorYears=sorted({s['year'] for s in old}),acceptedNewEmployeeYears=sorted({s['year'] for s in new if s['category']=='employee-remuneration'}),acceptedNewCouncilYears=sorted({s['year'] for s in new if s['category']=='elected-officials'}),verifiedAggregateOnlyYears=sorted({s['year'] for s in aggregate_only if s['employerSlug']==slug}),newRecords=sum(s['rowCount'] for s in new),sourceIndexUrls=sorted({s['sourceIndexUrl'] for s in sources}),archiveIndexedPeriods=sorted({y for s in sources for y in s['indexedReportingPeriods']}),sourceCandidates=[dict(sourceUrl=s['sourceUrl'],sourceIndexUrl=s['sourceIndexUrl'],indexedReportingPeriods=s['indexedReportingPeriods'],verifiedReportingPeriods=s['verifiedReportingPeriods'],status=s['status'],sha256=s['sha256'],cacheFile=s['cacheFile']) for s in sources]))
    save('findings.json',dict(version=1,asOf='2026-10-31',timezone='America/Vancouver',newRecords=sum(row_counts.values()),employeeObservations=row_counts['employee-remuneration'],electedObservations=row_counts['elected-officials'],newCohorts=len(current),originalReportsAccepted=len({s['sha256'] for s in current}),verifiedAggregateOnlyReports=len(aggregate_only),municipalityYears=len({(s['employerSlug'],s['year']) for s in current}),sourceLeadCount=len(inventory),distinctRetrievedOriginals=len(unique),queueTasks=len(queue),queueByRoute=dict(Counter(q['route'] for q in queue)),noExternalRequestsSent=True,employers=employers))
    print(len(current),'cohorts',sum(row_counts.values()),'records',len(queue),'tasks',Counter(q['route'] for q in queue))

if __name__=='__main__':main()
