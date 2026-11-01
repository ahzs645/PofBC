#!/usr/bin/env python3
"""Hash-pinned postsecondary SOFI extraction and offline independent-reader replay.

Primary reader: PyMuPDF positioned numeric anchors and nearest named baselines.
Secondary reader: Poppler physical-layout lines split at column whitespace.
Every source row, including duplicate names, must agree before output is written.
"""
import argparse
import collections
import gzip
import hashlib
import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/continuation-education'
AUDIT = ROOT / 'research/salaries/continuation-2026-11-01/education'
DISCOVERY = ROOT / 'research/salaries/sector-search-2026-10-31/education'
NUM = re.compile(r'^(?:-?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\(\d{1,3}(?:,\d{3})*(?:\.\d{2})?\))$')
MISSING = {'-', '‐', '–', '—', ''}
SLUGS = {
 'douglas-college': 'douglas', 'capilano-university': 'capilano',
 'university-of-the-fraser-valley': 'ufv', 'vancouver-island-university': 'viu',
 'camosun-college': 'camosun', 'okanagan-college': 'okanagan',
}

def money(text):
    text = text.strip().replace('$', '').strip()
    if text in MISSING:
        return None
    assert NUM.fullmatch(text), ('invalid money cell', text)
    n = Decimal(text.replace(',', '').replace('(', '-').replace(')', ''))
    return int(n) if n == int(n) else float(n)

def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def select_pages(doc, slug):
    texts = [re.sub(r'\s+', ' ', p.get_text()) for p in doc]
    if slug == 'douglas-college':
        start = next(i for i,t in enumerate(texts) if 'Schedule 1' in t and 'Name' in t and 'Remuneration' in t)
        end = next(i for i in range(start,len(texts)) if 'Douglas College Board' in texts[i])
    elif slug == 'camosun-college':
        start = next(i for i,t in enumerate(texts) if 'Employee Name' in t and 'Remuneration' in t)
        end = next(i for i in range(start,len(texts)) if re.search(r'Total\s+All\s+Employees',texts[i],re.I))
    elif slug == 'capilano-university':
        start = next(i for i,t in enumerate(texts) if 'Employee Remuneration and Expenses' in t and 'Name' in t and len(re.findall(r'\d{2},\d{3}',t)) > 5)
        end = start
        while end+1 < len(texts) and 'Name' in texts[end+1] and 'Remuneration' in texts[end+1]:end += 1
    elif slug == 'university-of-the-fraser-valley':
        pages = [i for i,t in enumerate(texts) if 'EMPLOYEES SALARIES OVER' in t and 'NAME' in t]
        start,end = min(pages),max(pages)
    elif slug == 'vancouver-island-university':
        pages = [i for i,t in enumerate(texts) if 'Employee Name' in t and ('Employee Remuneration' in t or 'Employee Salaries' in t)]
        start,end = min(pages),max(pages)
    elif slug == 'okanagan-college':
        pages = [i for i,t in enumerate(texts) if 'Employee Name' in t and 'Remuneration' in t]
        start,end = min(pages),max(pages)
    else:raise ValueError(slug)
    return list(range(start+1,end+2))

def layout(first, slug):
    words = first.get_text('words')
    heads = [w for w in words if w[4] in {'Name','NAME'}]
    assert heads
    head = max(heads,key=lambda w:w[1])
    h = [w for w in words if abs(w[1]-head[1])<3]
    pay = next(w for w in h if w[4] in {'Remuneration','SALARIES','Salaries'})
    exp = min([w for w in h if w[4] in {'Expenses','EXPENSES'}],key=lambda w:w[0])
    if slug == 'vancouver-island-university':
        name_end = exp[0]-20
    else:name_end = pay[0]-10
    # Published numeric cells are right aligned, except dashes; partition by headers.
    if pay[0]<exp[0]:
        boundary = (pay[2]+exp[0])/2
        pay_range = (name_end,boundary)
        total = [w for w in h if w[4]=='Total']
        exp_range = (boundary,(exp[2]+total[0][0])/2 if total else first.rect.width)
    else:
        boundary=(exp[2]+pay[0])/2
        exp_range=(name_end,boundary);pay_range=(boundary,pay[2]+15)
    return dict(nameEnd=name_end,payRange=pay_range,expenseRange=exp_range,headerY=head[1])

def primary(words, page, config, first=False, slug=None):
    lo,hi = config['payRange'];elo,ehi=config['expenseRange']
    low = config['headerY']+3 if first or slug!='camosun-college' else -1
    # Continuation headers may be above the first-page heading.
    if not first and slug!='camosun-college':
        hs=[w[1] for w in words if w[4] in {'Name','NAME'}]
        if hs:low=max(hs)+3
    anchors=sorted([w for w in words if lo<w[0]<hi and w[1]>low and NUM.fullmatch(w[4]) and 50000 <= money(w[4]) < 1000000],key=lambda w:w[1])
    rows=[];evidence=[]
    for a in anchors:
        # A numeric anchor alone is insufficient: require an actual published name.
        names=sorted([w for w in words if w[0]<config['nameEnd'] and abs(w[1]-a[1])<3 and w[4]!='$'],key=lambda w:w[0])
        name=' '.join(w[4] for w in names)
        if ',' not in name:continue
        assert not any(z in name for z in ['Total','Salaries','Employee','employees']), (page,name)
        ex=[w for w in words if elo<w[0]<ehi and abs(w[1]-a[1])<3 and (NUM.fullmatch(w[4]) or w[4] in MISSING)]
        assert len(ex)<=1,(page,name,ex)
        rows.append([name,None,money(a[4]),money(ex[0][4]) if ex else None,page])
        evidence.append(dict(name=name,payToken=a[4],expenseToken=ex[0][4] if ex else '',physicalPage=page,baseline=round(a[1],3)))
    return rows,evidence

def secondary(text,page,slug):
    rows=[];raw=[]
    for line in text.splitlines():
        cells=re.split(r'\s{2,}',line.replace('$',' ').strip())
        if len(cells)<2 or ',' not in cells[0] or not re.search(r'[A-Za-z]',cells[0]):continue
        cells=[c.replace('$','').strip() for c in cells]
        if any(z in cells[0] for z in ['Total','Salaries','Employee','employees']):continue
        if not NUM.fullmatch(cells[1]) and cells[1] not in MISSING:continue
        numeric=[money(c) for c in cells[1:]]
        pay,exp=(numeric[1],numeric[0]) if slug=='vancouver-island-university' and len(numeric)>=2 else (numeric[0],numeric[1] if len(numeric)>1 else None)
        if pay is None or not 50000<=pay<1000000:continue
        if slug=='douglas-college':
            assert len(numeric)==3,(page,line)
            assert abs(pay+(exp or 0)-numeric[2])<.011,(page,line,'expense-inclusive total differs')
        rows.append([cells[0],None,pay,exp,page]);raw.append(line)
    return rows,raw

def extract(pdf,slug):
    doc=fitz.open(pdf);pages=select_pages(doc,slug);config=layout(doc[pages[0]-1],slug)
    pop=subprocess.run(['pdftotext','-layout',str(pdf),'-'],check=True,capture_output=True,text=True).stdout.split('\f')
    rows=[];evidence=[];page_evidence=[]
    for p in pages:
        a,ev=primary(doc[p-1].get_text('words'),p,config,p==pages[0],slug)
        b,raw=secondary(pop[p-1],p,slug)
        assert a==b,(slug,p,'reader disagreement',a[:3],b[:3],len(a),len(b),[(x,y) for x,y in zip(a,b) if x!=y][:4])
        rows.extend(a);evidence.extend(ev)
        page_evidence.append(dict(physicalPage=p,words=[list(w[:5]) for w in doc[p-1].get_text('words')],popplerLayout=pop[p-1]))
    named_pages=sorted(set(r[4] for r in rows))
    return rows,dict(parserLayout=config,pages=named_pages,rows=evidence,pageEvidence=[p for p in page_evidence if p['physicalPage'] in named_pages])

def build(cache):
    documents=json.loads((DISCOVERY/'document-verification.json').read_text())['documents']
    employers={e['employerSlug']:e for e in json.loads((DISCOVERY/'findings.json').read_text())['employers']}
    baseline=json.loads((AUDIT/'accepted-baseline.json').read_text())
    sources=[];held=[]
    for d in documents:
        slug=d['employerSlug']
        if slug not in SLUGS or d.get('pdfStatus')!='native-text-candidate':continue
        year=d['candidateReportingPeriod']
        if any(s['employerSlug']==slug and s['year']==year and s['category']=='employee-remuneration' for s in baseline):continue
        pdf=cache/d['cacheFile'];assert sha(pdf.read_bytes())==d['sha256']
        sid=f'{SLUGS[slug]}-sofi-{year.replace("/","-")}-employees'
        try:rows,ev=extract(pdf,slug)
        except Exception as ex:
            held.append(dict(id=sid,cacheFile=str(pdf),reason=str(ex)));continue
        rows=[[slug]+r for r in rows]
        payload=json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode();gz=gzip.compress(payload,mtime=0)
        filename=sid+'.json.gzip';(OUT/filename).write_bytes(gz)
        dump(OUT/'evidence'/f'{sid}.json',ev)
        start=int(year[:4]);end=start+1
        source=dict(id=sid,employerSlug=slug,employerName=employers[slug]['employerName'],sector='Universities and colleges',year=year,slug=year.replace('/','-'),file=filename,title=employers[slug]['employerName']+' Statement of Financial Information '+year+': employee remuneration and expenses',sourceUrl=d['url'],sourceIndexUrl=d['indexUrl'],sha256=d['sha256'],dataSha256=sha(gz),normalizedSha256=sha(payload),periodType='fiscal',periodStart=f'{start}-04-01',periodEnd=f'{end}-03-31',currency='CAD',category='employee-remuneration',scope='employee-remuneration',sourceKind='official-pdf',status='verified',verifiedOn='2026-11-01',nameDisclosure='as-published',positionDisclosure='not-published',completeEmployeeSchedule=slug!='camosun-college',rowCount=len(rows),pages=ev['pages'],totalRemuneration=float(sum(Decimal(str(r[3])) for r in rows)),totalDisclosedExpenses=float(sum(Decimal(str(r[4] or 0)) for r in rows)),notes=['Complete published named employee schedule; source blanks and dashes are null. Separate board, supplier and aggregate scopes excluded. Annual remuneration as published, not base annual salary.'],validation=dict(sourceFingerprintLocked=True,completeEmployeeSchedule=slug!='camosun-college',allNamesAndMonetaryCellsIndependentlyVerified=True,independentMethod='PyMuPDF positioned pay anchors and nearest named baselines versus Poppler physical-layout line parser; exact row/order/page/multiplicity equality required.',rowCountsByPdfPage=dict(collections.Counter(r[5] for r in rows)),expenseDashesOrBlankRetainedAsMissing=sum(r[4] is None for r in rows),negativeExpenseRows=sum(r[4] is not None and r[4]<0 for r in rows),evidenceFile=f'evidence/{sid}.json',controlsReviewPending=True),cacheFile=str(pdf))
        if slug=='camosun-college':
            source['notes'].append('The original expressly excludes employees who are board members and severance amounts from this employee schedule; it is incomplete for all employees. Board-related employee amounts remain in the separate source board scope.')
            source['publicWarning']='This employee schedule excludes employees who are board members and amounts paid under severance agreements. Board remuneration is a separate disclosure.'
        sources.append(source)
    dump(OUT/'sources.json',dict(version=1,rowSchema=['employerSlug','name','position','remuneration','expenses','pdfPage'],sources=sources))
    dump(AUDIT/'parser-holds.json',held)
    print(json.dumps(dict(sources=len(sources),rows=sum(s['rowCount'] for s in sources),held=held),indent=2))

def verify(cache,originals):
    sources=json.loads((OUT/'sources.json').read_text())['sources']
    for s in sources:
        ev=json.loads((OUT/s['validation']['evidenceFile']).read_text());rows=[]
        for page in ev['pageEvidence']:
            p=page['physicalPage'];a,_=primary(page['words'],p,ev['parserLayout'],p==ev['pages'][0],s['employerSlug']);b,_=secondary(page['popplerLayout'],p,s['employerSlug']);assert a==b,(s['id'],p);rows.extend([[s['employerSlug']]+r for r in a])
        data=(OUT/s['file']).read_bytes();assert sha(data)==s['dataSha256'];assert json.loads(gzip.decompress(data))==rows
        if originals:
            pdf=Path(s['cacheFile']);assert sha(pdf.read_bytes())==s['sha256'];actual,_=extract(pdf,s['employerSlug']);assert rows==[[s['employerSlug']]+r for r in actual]
    print(f'Verified {len(sources)} sources / {sum(s["rowCount"] for s in sources)} rows ({"originals" if originals else "offline evidence replay"})')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',action='store_true');p.add_argument('--originals',action='store_true');p.add_argument('--cache',type=Path,default=Path('/tmp/pofbc-sector-education'));args=p.parse_args()
    if args.build:build(args.cache)
    else:verify(args.cache,args.originals)

if __name__=='__main__':main()
