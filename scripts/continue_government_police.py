#!/usr/bin/env python3
"""Original-backed native salary history extraction, plus offline evidence replay.

No expense cross-schedule joins are made. Public Accounts 1999/00--2002/03
publish travel in each employee row; later salary-only tables leave expenses null.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/continuation-government-police'
CONFIG_PATH = OUT / 'config.json'
SCHEMA = ['employerSlug','name','position','remuneration','expenses','pdfPage']
MONEY = r'-?\d[\d,]*(?:\.\d{2})?'
PA_LINE = re.compile(r"([A-Za-zÀ-ž][A-Za-zÀ-ž ,()'.–—\-]*?,[A-Za-zÀ-ž ,()'.–—\-]*?)\s{2,}("+MONEY+r")(?:\s{2,}("+MONEY+r"))?(?=\s|$)")

def sha(b): return hashlib.sha256(b).hexdigest()
def encoded(x): return (json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def packed(x): return gzip.compress(encoded(x),mtime=0)
def clean(s): return ' '.join(s.split())
def amount(s):
    if s is None or s.strip() in ('','-','‐','—','–'):return None
    f=float(s.replace(',','').replace('$','').strip())
    return int(f) if f.is_integer() else f

def expense_totals(rows):
    """An unavailable expense field has no reported total, including zero."""
    known=[r[4] for r in rows if r[4] is not None]
    return {
        'totalExpenses':sum(known) if known else None,
        'totalKnownExpenses':sum(known),
        'totalExpensesComplete':len(known)==len(rows),
    }

def parse_pa_words(words, cfg, physical_page):
    """PyMuPDF coordinates: comma-bearing names anchor potentially wrapped rows."""
    result=[]
    for left,right in zip(cfg['columnStarts'],cfg['columnStarts'][1:]+[10000]):
        col=[w for w in words if left-2 <= w[0]<right-2]
        anchors=[]
        for w in col:
            if abs(w[0]-left)>=3 or not re.search('[A-Za-z]',w[4]):continue
            if cfg.get('parser')=='pa-appointees' and re.fullmatch(r"[A-Z][A-Z'-]{15,}",w[4]) and ',' not in w[4]:anchors.append(w);continue
            line=[v for v in col if abs(v[1]-w[1])<1]
            if any(',' in v[4] and (re.search('[A-Za-z]',v[4]) or v[4]==',') for v in line):anchors.append(w)
        for comma in col:
            if comma[4]==',' and abs(comma[0]-left)<3:
                prior=[v for v in col if abs(v[0]-left)<3 and re.search('[A-Za-z]',v[4]) and 10<comma[1]-v[1]<14]
                if prior and prior[-1] not in anchors:anchors.append(prior[-1])
        anchors.sort(key=lambda w:w[1])
        for i,a in enumerate(anchors):
            end=anchors[i+1][1]-1 if i+1<len(anchors) else a[1]+13
            cells=sorted([w for w in col if a[1]-1 <= w[1] < end],key=lambda w:(round(w[1]),w[0]))
            nums=[w for w in cells if re.fullmatch(MONEY,w[4])]
            if len(nums) not in ([1,2] if cfg['travelInRow'] else [1]):raise ValueError(('PA row cells',physical_page,cells))
            if cfg['travelInRow'] and nums[0][0] > left+130:raise ValueError(('Missing salary; travel alone must not become remuneration',physical_page,cells))
            name=clean(' '.join(w[4] for w in cells if w[0]<nums[0][0] and not re.fullmatch(MONEY,w[4])))
            result.append([cfg['employerSlug'],name,None,amount(nums[0][4]),amount(nums[1][4]) if len(nums)==2 else None,physical_page])
    return result

def parse_pa_layout(layout,cfg,physical_page):
    """Poppler fixed-pitch text: split printed columns and collect wrapped names."""
    result=[]
    cuts=[int(x/cfg.get('layoutPitch',3)) for x in cfg['columnStarts']]+[10000]
    for left,right in zip(cuts,cuts[1:]):
        pending=[];started=False
        for line in layout.splitlines():
            fragment=line[left:right].strip()
            if not fragment:continue
            m=re.match(r'^(.+?)\s{2,}(' + MONEY + r')(?:\s{2,}('+MONEY+r'))?\s*$',fragment)
            if m:
                if pending or (',' in m[1] and re.search('[A-Za-z]',m[1])):
                    name=clean(' '.join(pending+[m[1]]));pending=[];started=True
                    if m[3] is not None and not cfg['travelInRow']:raise ValueError(('unexpected travel',physical_page,fragment))
                    result.append([cfg['employerSlug'],name,None,amount(m[2]),amount(m[3]),physical_page])
            elif ',' in fragment and re.search('[A-Za-z]',fragment) and not re.search(r'[0-9$]',fragment) and started:
                if pending:raise ValueError(('unpaid row / unresolved boundary',physical_page,pending,fragment))
                pending=[fragment]
            elif pending:pending.append(fragment)
            elif started and re.fullmatch(r"[A-Z][A-Z'-]{15,}",fragment):pending=[fragment]
        if pending:raise ValueError(('unclosed row',physical_page,pending))
    return result

def parse_oic_column(text,cfg,pno):
    rows=[];pending=[];started=False
    for line in text.splitlines():
        t=clean(line);m=re.match(r'^(.+?)\s+('+MONEY+r')(?:\s+('+MONEY+r'))?$',t)
        if m and not re.search('[0-9]',m[1]) and (pending or ',' in m[1]):
            name=clean(' '.join(pending+[m[1]]));pending=[];started=True
            rows.append([cfg['employerSlug'],name,None,amount(m[2]),amount(m[3]),pno])
        elif ',' in t and re.search('[A-Za-z]',t) and not re.search('[0-9$]',t) and started:pending=[t]
        elif pending:pending.append(t)
        elif started and re.fullmatch(r"[A-Z][A-Z'-]{15,}",t):pending=[t]
    if pending:raise ValueError(('OIC unclosed PDFMiner row',pno,pending))
    return rows

OIC_PDFMINER_DOCS={}
def oic_pdfminer_page(path,cfg,pno):
    import pdfplumber
    texts=[];rows=[]
    key=str(path)
    if key not in OIC_PDFMINER_DOCS:OIC_PDFMINER_DOCS[key]=pdfplumber.open(path)
    p=OIC_PDFMINER_DOCS[key].pages[pno-1]
    for left,right in zip(cfg['columnStarts'],cfg['columnStarts'][1:]+[p.width+2]):
        text=p.crop((left-2,0,right-2,p.height)).extract_text(x_tolerance=1,y_tolerance=2) or ''
        texts.append(text);rows.extend(parse_oic_column(text,cfg,pno))
    return rows,texts

def extract_pa(path,cfg):
    import fitz
    doc=fitz.open(path)
    layout=subprocess.run(['pdftotext','-fixed',str(cfg.get('layoutPitch',3)),str(path),'-'],check=True,capture_output=True,text=True).stdout.split('\f')
    first=clean(doc[cfg['pages'][0]-1].get_text())
    assert re.search(rf"Fiscal Year Ended March 31,? {cfg['fiscalEnd']}",first),first[:300]
    if cfg['parser']=='pa-employees':assert 'gross salary of $75,000 or more' in first
    else:assert 'Appointees' in first
    rows=[];evidence=[]
    for pno in cfg['pages']:
        page=doc[pno-1];text=page.get_text();assert ('Other Employees' if cfg['parser']=='pa-employees' else 'Appointees') in text
        a=parse_pa_words(page.get_text('words'),cfg,pno)
        texts=None
        if cfg['parser']=='pa-appointees':b,texts=oic_pdfminer_page(path,cfg,pno)
        else:b=parse_pa_layout(layout[pno-1],cfg,pno)
        if a!=b:
            raise ValueError(f"{cfg['id']} page {pno}: native readers disagree {len(a)}/{len(b)}; primary-only {[r for r in a if r not in b][:3]}; secondary-only {[r for r in b if r not in a][:3]}")
        assert a
        if cfg['parser']=='pa-employees':assert all(r[3]>=75000 for r in a)
        rows.extend(a);evidence.append({'pdfPage':pno,'nativeText':text,'popplerLayout':layout[pno-1],'nativeWords':page.get_text('words'),'rows':a,'bothReadersAgree':True})
        if texts is not None:evidence[-1]['independentColumnTexts']=texts
    if cfg.get('expectedCount') is not None:assert len(rows)==cfg['expectedCount']
    if str(path) in OIC_PDFMINER_DOCS:OIC_PDFMINER_DOCS.pop(str(path)).close()
    return rows,evidence

VPD_LINE=re.compile(r'^\s*(\*?\s*[^,]+,.+?)\s{2,}(.+?)\s{2,}\$?\s*('+MONEY+r')\s+\$?\s*('+MONEY+r'|-)\s*$')
def parse_vpd_layout(text,cfg,pno):
    result=[]
    for line in text.splitlines():
        m=VPD_LINE.match(line)
        if m:result.append([cfg['employerSlug'],clean(m[1]).removeprefix('* ').strip(),clean(m[2]),amount(m[3]),amount(m[4]),pno])
    return result

def parse_vpd_words(words,cfg,pno):
    posx=min(w[0] for w in words if w[4] in ['Chief','Deputy','Superintendent','Senior'])
    anchors=[w for w in words if ',' in w[4] and re.search('[A-Za-z]',w[4]) and w[0]<posx]
    rows=[]
    for a in sorted(anchors,key=lambda w:w[1]):
        line=sorted([w for w in words if abs(w[1]-a[1])<2.1],key=lambda w:w[0])
        nums=[w for w in line if re.fullmatch(MONEY+'|-',w[4])]
        if len(nums)!=2:raise ValueError(('VPD values',cfg['id'],line))
        name=clean(' '.join(w[4] for w in line if w[0]<posx-2 and w[4]!='*'))
        title=clean(' '.join(w[4] for w in line if posx-2 <= w[0] < nums[0][0] and w[4]!='$'))
        rows.append([cfg['employerSlug'],name,title,amount(nums[0][4]),amount(nums[1][4]),pno])
    return rows

def extract_vpd(path,cfg):
    import fitz
    doc=fitz.open(path);assert len(doc)==1
    page=doc[0];txt=page.get_text();assert re.search(rf"For the Year Ended December 31, {cfg['year']}",clean(txt))
    layout=subprocess.run(['pdftotext','-layout',str(path),'-'],check=True,capture_output=True,text=True).stdout
    a=parse_vpd_words(page.get_text('words'),cfg,1);b=parse_vpd_layout(layout,cfg,1)
    if a!=b:raise ValueError(f"{cfg['id']}: native readers disagree {a} vs {b}")
    assert a and len(a)==cfg['expectedCount']
    return a,[{'pdfPage':1,'nativeText':txt,'nativeWords':page.get_text('words'),'popplerLayout':layout,'rows':a,'bothReadersAgree':True}]

def parse_acrd_words(words,cfg,pno):
    titlex=226;payx=cfg['payColumnLeft'];expx=470
    anchors=sorted([w for w in words if 108<w[0]<titlex and ',' in w[4] and re.search('[A-Za-z]',w[4]) and w[1]>130],key=lambda w:w[1]);rows=[]
    stop=min([w[1] for w in words if w[4]=='Consolidated']+[10000])
    anchors=[w for w in anchors if w[1]<stop]
    for i,a in enumerate(anchors):
        end=anchors[i+1][1]-1 if i+1<len(anchors) else stop-1
        cells=sorted([w for w in words if a[1]-1<=w[1]<end],key=lambda w:(round(w[1]),w[0]))
        name=clean(' '.join(w[4] for w in cells if 108<w[0]<titlex))
        title=clean(' '.join(w[4] for w in cells if titlex<=w[0]<payx))
        salary=[w[4] for w in cells if payx<=w[0]<expx and re.fullmatch(r'\$?'+MONEY,w[4])]
        expense=[w[4] for w in cells if w[0]>=expx and re.fullmatch(r'\$?'+MONEY,w[4])]
        if len(salary)!=1 or len(expense)!=1:raise ValueError(('ACRD values',cfg['id'],pno,cells))
        rows.append([cfg['employerSlug'],name,title,amount(salary[0]),amount(expense[0]),pno])
    return rows

def parse_acrd_layout(text,cfg,pno):
    cuts=[36,75,round(cfg['payColumnLeft']/3),157,10000];rows=[];current=None
    def finish(row):
        if not row:return
        if len(row[2])!=1 or len(row[3])!=1:raise ValueError(('ACRD incomplete row',row))
        rows.append([cfg['employerSlug'],clean(' '.join(row[0])),clean(' '.join(row[1])),amount(row[2][0]),amount(row[3][0]),pno])
    for line in text.splitlines():
        cells=[line[a:b].strip() for a,b in zip(cuts,cuts[1:])]
        if cells[0].startswith('Consolidated'):finish(current);current=None;break
        if ',' in cells[0] and not re.search('[0-9]',cells[0]):finish(current);current=[[],[],[],[]]
        if current:
            for i,c in enumerate(cells):
                if c:current[i].append(c)
    finish(current)
    return rows

def extract_acrd(path,cfg):
    import fitz
    doc=fitz.open(path);assert re.search(rf"PERIOD ENDED DECEMBER 31, {cfg['year']}",clean(doc[0].get_text()))
    layout=subprocess.run(['pdftotext','-fixed','3',str(path),'-'],check=True,capture_output=True,text=True).stdout.split('\f');rows=[];pages=[]
    for pno in cfg['pages']:
        p=doc[pno-1];t=p.get_text();assert 'Other Employees' in t
        a=parse_acrd_words(p.get_text('words'),cfg,pno);b=parse_acrd_layout(layout[pno-1],cfg,pno)
        if a!=b:raise ValueError(f"{cfg['id']} page{pno}: native readers disagree {a} vs {b}")
        rows.extend(a);pages.append({'pdfPage':pno,'nativeText':t,'nativeWords':p.get_text('words'),'popplerLayout':layout[pno-1],'rows':a,'bothReadersAgree':True})
    assert len(rows)==cfg['expectedCount'];assert all(r[3]>75000 for r in rows)
    return rows,pages

EKO_LINE=re.compile(r'^\s*(\S.+?)\s{2,}(.+?)\s{2,}\$?\s*('+MONEY+r')\s+\$?\s*('+MONEY+r'|[-‐–—])\s*\$?\s*$')
def parse_eko_layout(text,cfg,pno):
    rows=[]
    for line in text.splitlines():
        if 'Employee Gross Earnings' in line:break
        m=EKO_LINE.match(line)
        if m:
            if amount(m[3])<=75000:raise ValueError(('EKO below threshold',line))
            rows.append([cfg['employerSlug'],clean(m[1]).rstrip('*'),clean(m[2]),amount(m[3]),amount(m[4]),pno])
    return rows

def parse_eko_words(words,cfg,pno):
    stop=min([w[1] for w in words if w[4]=='Employee' and w[0]<30 and any(v[4]=='Gross' and abs(v[1]-w[1])<2 for v in words)]+[10000])
    anchors=sorted([w for w in words if 410<w[0]<500 and re.fullmatch(MONEY,w[4]) and w[1]<stop],key=lambda w:w[1]);rows=[]
    for a in anchors:
        line=sorted([w for w in words if abs(w[1]-a[1])<2.1],key=lambda w:w[0])
        name=clean(' '.join(w[4] for w in line if w[0]<115)).rstrip('*')
        title=clean(' '.join(w[4] for w in line if 115<=w[0]<410 and w[4]!='$'))
        exp=[w[4] for w in line if w[0]>=500 and re.fullmatch(MONEY+r'|[-‐–—]',w[4])]
        if not name or not title or len(exp)!=1:raise ValueError(('EKO boundary',line))
        rows.append([cfg['employerSlug'],name,title,amount(a[4]),amount(exp[0]),pno])
    return rows

def extract_eko(path,cfg):
    import fitz
    doc=fitz.open(path);assert re.search(rf"year ended December 31, {cfg['year']}",clean(doc[0].get_text()),re.I)
    layout=subprocess.run(['pdftotext','-layout',str(path),'-'],check=True,capture_output=True,text=True).stdout.split('\f');rows=[];pages=[]
    for pno in cfg['pages']:
        p=doc[pno-1];t=p.get_text();assert 'Employee Remuneration and Expenses' in clean(t) or 'Employee Gross Earnings' in clean(t)
        a=parse_eko_words(p.get_text('words'),cfg,pno);b=parse_eko_layout(layout[pno-1],cfg,pno)
        if a!=b:raise ValueError(f"{cfg['id']} page{pno}: native readers disagree {a} vs {b}")
        rows.extend(a);pages.append({'pdfPage':pno,'nativeText':t,'nativeWords':p.get_text('words'),'popplerLayout':layout[pno-1],'rows':a,'bothReadersAgree':True})
    assert rows
    if cfg.get('expectedCount') is not None:assert len(rows)==cfg['expectedCount']
    return rows,pages

def build(cache,fetch=False,check=False,refresh_metadata=False,verify_originals=False):
    config=json.loads(CONFIG_PATH.read_text());sources=[]
    for cfg in config['sources']:
        evidence_name='evidence/'+cfg['id']+'.json.gzip';evpath=OUT/evidence_name
        if check:
            ev=json.loads(gzip.decompress(evpath.read_bytes()));assert ev['originalSha256']==cfg['sha256'];rows=ev['rows']
            if cfg['parser']=='pa-appointees':
                replay=[r for p in ev['pages'] for col in p['independentColumnTexts'] for r in parse_oic_column(col,cfg,p['pdfPage'])]
                assert rows==replay
                assert rows==[r for p in ev['pages'] for r in parse_pa_words(p['nativeWords'],cfg,p['pdfPage'])]
            elif cfg['parser']=='pa-employees':
                replay=[r for p in ev['pages'] for r in parse_pa_layout(p['popplerLayout'],cfg,p['pdfPage'])]
                assert rows==replay
                assert rows==[r for p in ev['pages'] for r in parse_pa_words(p['nativeWords'],cfg,p['pdfPage'])]
            elif cfg['parser']=='eko-employees':
                assert rows==[r for p in ev['pages'] for r in parse_eko_layout(p['popplerLayout'],cfg,p['pdfPage'])]
                assert rows==[r for p in ev['pages'] for r in parse_eko_words(p['nativeWords'],cfg,p['pdfPage'])]
            elif cfg['parser']=='acrd-employees':
                assert rows==[r for p in ev['pages'] for r in parse_acrd_layout(p['popplerLayout'],cfg,p['pdfPage'])]
                assert rows==[r for p in ev['pages'] for r in parse_acrd_words(p['nativeWords'],cfg,p['pdfPage'])]
            elif cfg['parser']=='vpd-executives':
                assert rows==[r for p in ev['pages'] for r in parse_vpd_layout(p['popplerLayout'],cfg,p['pdfPage'])]
                assert rows==[r for p in ev['pages'] for r in parse_vpd_words(p['nativeWords'],cfg,p['pdfPage'])]
            assert all(p['bothReadersAgree'] for p in ev['pages'])
        else:
            path=cache/cfg['cacheFile']
            if fetch and not path.exists():
                req=urllib.request.Request(cfg['sourceUrl'],headers={'User-Agent':'Mozilla/5.0'})
                path.write_bytes(urllib.request.urlopen(req,timeout=60).read())
            assert sha(path.read_bytes())==cfg['sha256'],str(path)+' fingerprint changed'
            if cfg['parser'] in ['pa-employees','pa-appointees']:rows,pages=extract_pa(path,cfg)
            elif cfg['parser']=='vpd-executives':rows,pages=extract_vpd(path,cfg)
            elif cfg['parser']=='acrd-employees':rows,pages=extract_acrd(path,cfg)
            elif cfg['parser']=='eko-employees':rows,pages=extract_eko(path,cfg)
            else:raise ValueError(cfg['parser'])
            context=[]
            import fitz
            doc=fitz.open(path)
            for pno in cfg.get('contextPages',[]):context.append({'pdfPage':pno,'nativeText':doc[pno-1].get_text()})
            ev={'originalSha256':cfg['sha256'],'rows':rows,'pages':pages,'contextPages':context,'method':('Independent PyMuPDF coordinate rows and PDFMiner cropped-column rows agree on every field, boundary, page, and multiplicity.' if cfg['parser']=='pa-appointees' else 'Independent PyMuPDF coordinate rows and Poppler layout rows agree on every field, boundary, page, and multiplicity.')}
            if verify_originals:assert evpath.read_bytes()==packed(ev),cfg['id']+' original extraction changed'
            else:evpath.write_bytes(packed(ev))
        data=packed(rows);filename=cfg['id']+'.json.gzip'
        if check or verify_originals:assert (OUT/filename).read_bytes()==data
        else:(OUT/filename).write_bytes(data)
        source={k:v for k,v in cfg.items() if k not in ['parser','cacheFile','columnStarts','travelInRow','fiscalEnd','expectedCount','acceptanceStatus','contextPages','payColumnLeft','independentReviews','renderedReview','layoutPitch']}
        source.update(file=filename,dataSha256=sha(data),rowCount=len(rows),totalRemuneration=sum(r[3] for r in rows),status=cfg.get('acceptanceStatus','verified'),sourceKind='official-pdf',verifiedOn='2026-11-01',currency='CAD',amountUnit='dollars',**expense_totals(rows))
        if source['totalExpenses'] is None:
            assert not any(c['field']=='expenses' for c in cfg.get('printedControls',[])), 'Unavailable expenses cannot have an expense comparator'
        for control in cfg.get('printedControls',[]):
            col=3 if control['field']=='remuneration' else 4
            row_sum=sum(r[col] for r in rows if r[col] is not None)
            assert row_sum==control.get('rowSum',control.get('namedRowSum')), (cfg['id'],control)
            if 'publishedUnderThreshold' in control:assert control['residualDollars']==row_sum+control['publishedUnderThreshold']-control['publishedTotal']
            else:assert control['residualDollars']==row_sum-control['publishedDollars']
        source['validation']={'method':ev['method'],'bothReadersAgree':True,'completeEmployeeSchedule':source['completeEmployeeSchedule'],'evidenceFile':evidence_name,'evidenceSha256':sha(evpath.read_bytes()),'rowCount':len(rows),'missingExpenses':sum(r[4] is None for r in rows),'duplicateNameRows':sum(n-1 for n in Counter(r[1] for r in rows).values() if n>1),'exactDuplicateRows':sum(n-1 for n in Counter(tuple(r) for r in rows).values() if n>1),'independentReviews':cfg.get('independentReviews',[]),'renderedReview':cfg.get('renderedReview'),'negativeRemunerationRows':sum(r[3]<0 for r in rows),'negativeExpensesRows':sum(r[4] is not None and r[4]<0 for r in rows),'printedControls':cfg.get('printedControls',[])}
        source['validation']['expenseComparatorAvailability']='unavailable' if source['totalExpenses'] is None else 'published' if any(c['field']=='expenses' for c in cfg.get('printedControls',[])) else 'not-published'
        sources.append(source)
    manifest={'version':1,'rowSchema':SCHEMA,'sources':sources};content=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    if (check and not refresh_metadata) or verify_originals:assert (OUT/'sources.json').read_bytes()==content
    else:(OUT/'sources.json').write_bytes(content)
    print(json.dumps({'sources':len(sources),'rows':sum(s['rowCount'] for s in sources),'verifiedRows':sum(s['rowCount'] for s in sources if s['status']=='verified'),'heldRows':sum(s['rowCount'] for s in sources if s['status']!='verified'),'checks':'original-backed verification without writes' if verify_originals else 'offline evidence replay' if check else 'original-backed dual readers'},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,default=Path('/tmp/continuation-government-police'));ap.add_argument('--fetch',action='store_true');ap.add_argument('--check-data',action='store_true');ap.add_argument('--refresh-metadata',action='store_true');ap.add_argument('--verify-originals',action='store_true');a=ap.parse_args();build(a.cache,a.fetch,a.check_data or a.refresh_metadata,a.refresh_metadata,a.verify_originals)
