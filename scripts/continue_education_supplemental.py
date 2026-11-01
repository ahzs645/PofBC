#!/usr/bin/env python3
"""Separate supplemental native employee histories; never mutates frozen batch one."""
import argparse
import collections
import copy
import gzip
import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path
import fitz
import continue_education as core

OUT=core.OUT/'supplemental'
AUDIT=core.AUDIT/'supplemental'
SHORT={'thompson-rivers-university':'tru','emily-carr-university':'ecu','north-island-college':'north-island'}

def words(page):
    values=[]
    for w in page.get_text('words'):
        w=list(w[:5]);w[4]={'Renumeration':'Remuneration','Expenses*':'Expenses'}.get(w[4],w[4]);values.append(w)
    return values

def extract(pdf,slug):
    doc=fitz.open(pdf);texts=[re.sub(r'\s+',' ',p.get_text()) for p in doc]
    if slug=='north-island-college':pages=[i+1 for i,t in enumerate(texts) if re.search(r'B\.\s+Other Employees\s+>\s+\$75,000',t)]
    elif slug=='thompson-rivers-university':pages=[i+1 for i,t in enumerate(texts) if 'Name' in t and 'Renumeration' in t and 'Expenses' in t]
    elif slug=='emily-carr-university':
        start=next(i for i,t in enumerate(texts) if 'Employees' in t and 'Name' in t and 'Renumeration' in t)
        end=next(i for i in range(start,len(doc)) if re.search(r'Total Remuneration for Employee',texts[i]));pages=list(range(start+1,end+2))
    else:raise ValueError(slug)
    assert pages
    class Header:
        rect=doc[pages[0]-1].rect
        def get_text(self,kind):return [w for w in words(doc[pages[0]-1]) if w[4]!='Total']
    config=core.layout(Header(),slug)
    # First page contains a separate board table. Its repeated final Name header
    # establishes the employee region. Continuation pages can start above it.
    if slug=='emily-carr-university':
        employee_y=next(w[1] for w in words(doc[pages[0]-1]) if w[4]=='Employees')
        config['headerY']=employee_y
    pop=subprocess.run(['pdftotext','-layout',str(pdf),'-'],check=True,capture_output=True,text=True).stdout.split('\f')
    out=[];evrows=[];pev=[]
    for pn in pages:
        conf=dict(config)
        if pn!=pages[0]:conf['headerY']=-1
        a,ev=core.primary(words(doc[pn-1]),pn,conf,pn==pages[0],slug)
        b,_=core.secondary(pop[pn-1],pn,slug)
        assert a==b,(slug,pn,'independent reader disagreement',len(a),len(b),[(x,y) for x,y in zip(a,b) if x!=y][:3])
        out+=a;evrows+=ev;pev.append(dict(physicalPage=pn,words=words(doc[pn-1]),popplerLayout=pop[pn-1]))
    return out,dict(parserLayout=config,pages=sorted(set(r[4] for r in out)),rows=evrows,pageEvidence=pev)

def build():
    OUT.mkdir(exist_ok=True);(OUT/'evidence').mkdir(exist_ok=True);AUDIT.mkdir(exist_ok=True)
    old=json.loads((core.DISCOVERY/'document-verification.json').read_text())['documents'];new=json.loads((core.AUDIT/'new-document-receipts.json').read_text());employers={e['employerSlug']:e for e in json.loads((core.DISCOVERY/'findings.json').read_text())['employers']}
    documents=[]
    for d in old:
        if (d['employerSlug']=='thompson-rivers-university' or d['employerSlug']=='emily-carr-university' and d.get('candidateReportingPeriod')=='2023/24' or d['employerSlug']=='north-island-college' and d.get('candidateReportingPeriod')=='2024/25'):
            d=dict(d);d['cacheFile']='/tmp/pofbc-sector-education/'+d['cacheFile'];documents.append(d)
    for d in new:
        if d['employerSlug']=='emily-carr-university' and d.get('pdfStatus')=='native-text-candidate':documents.append(d)
        if d['employerSlug']=='thompson-rivers-university' and d.get('cacheFile'):
            d=dict(d);d['candidateReportingPeriod']='2022/23';documents.append(d)
    sources=[];holds=[]
    for d in documents:
        slug=d['employerSlug'];year=d['candidateReportingPeriod'];sid=f'{SHORT[slug]}-sofi-{year.replace("/","-")}-employees';pdf=Path(d['cacheFile']);assert core.sha(pdf.read_bytes())==d['sha256']
        try:rows,ev=extract(pdf,slug)
        except Exception as ex:holds.append(dict(id=sid,cacheFile=str(pdf),reason=str(ex)));continue
        rows=[[slug]+r for r in rows];body=json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode();packed=gzip.compress(body,mtime=0);filename=sid+'.json.gzip';(OUT/filename).write_bytes(packed);core.dump(OUT/'evidence'/f'{sid}.json',ev)
        start=int(year[:4]);end=start+1
        s=dict(id=sid,employerSlug=slug,employerName=employers[slug]['employerName'],sector='Universities and colleges',year=year,slug=year.replace('/','-'),file=filename,title=employers[slug]['employerName']+' Statement of Financial Information '+year+': employee remuneration and expenses',sourceUrl=d['url'],sourceIndexUrl=d['indexUrl'],sha256=d['sha256'],dataSha256=core.sha(packed),normalizedSha256=core.sha(body),periodType='fiscal',periodStart=f'{start}-04-01',periodEnd=f'{end}-03-31',currency='CAD',category='employee-remuneration',scope='employee-remuneration',sourceKind='official-pdf',status='verified',verifiedOn='2026-11-01',nameDisclosure='as-published',positionDisclosure='not-published',completeEmployeeSchedule=True,rowCount=len(rows),pages=ev['pages'],totalRemuneration=float(sum(Decimal(str(r[3])) for r in rows)),totalDisclosedExpenses=float(sum(Decimal(str(r[4] or 0)) for r in rows)),cacheFile=str(pdf),notes=['Complete named employee schedule as published; separate board and aggregate scopes excluded. Blank/dash expenses remain null. Annual payments are not base annual salary. No published individual title is inferred from a separate board listing.'],validation=dict(sourceFingerprintLocked=True,completeEmployeeSchedule=True,allNamesAndMonetaryCellsIndependentlyVerified=True,independentMethod='PyMuPDF positioned pay anchors versus Poppler physical-layout row parser; exact name/payment/expense/page/order/multiplicity equality.',rowCountsByPdfPage=dict(collections.Counter(r[5] for r in rows)),expenseDashesOrBlankRetainedAsMissing=sum(r[4] is None for r in rows),negativeExpenseRows=sum(r[4] is not None and r[4]<0 for r in rows),evidenceFile=f'evidence/{sid}.json',controlsReviewPending=True))
        sources.append(s)
    core.dump(OUT/'sources.json',dict(version=1,rowSchema=['employerSlug','name','position','remuneration','expenses','pdfPage'],sources=sources));core.dump(AUDIT/'parser-holds.json',holds)
    print(json.dumps(dict(sources=len(sources),rows=sum(s['rowCount'] for s in sources),holds=holds),indent=2))

def verify(originals):
    ss=json.loads((OUT/'sources.json').read_text())['sources']
    for s in ss:
        ev=json.loads((OUT/s['validation']['evidenceFile']).read_text());rows=[]
        for p in ev['pageEvidence']:
            cfg=dict(ev['parserLayout']);first=p['physicalPage']==ev['pages'][0]
            if not first:cfg['headerY']=-1
            a,_=core.primary(p['words'],p['physicalPage'],cfg,first,s['employerSlug']);b,_=core.secondary(p['popplerLayout'],p['physicalPage'],s['employerSlug']);assert a==b;rows.extend([[s['employerSlug']]+r for r in a])
        data=(OUT/s['file']).read_bytes();assert core.sha(data)==s['dataSha256'];assert json.loads(gzip.decompress(data))==rows
        if originals:
            assert core.sha(Path(s['cacheFile']).read_bytes())==s['sha256'];actual,_=extract(s['cacheFile'],s['employerSlug']);assert rows==[[s['employerSlug']]+r for r in actual]
    print(f'Verified supplemental {len(ss)} sources / {sum(s["rowCount"] for s in ss)} rows'+(' from originals' if originals else ' offline'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');p.add_argument('--review',action='store_true');p.add_argument('--originals',action='store_true');args=p.parse_args()
    if args.build:build()
    elif args.review:
        import continue_education_review as review
        review.OUT=OUT;review.AUDIT=AUDIT;review.review()
    else:verify(args.originals)

if __name__=='__main__':main()
