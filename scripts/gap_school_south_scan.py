#!/usr/bin/env python3
"""Independent OCR row readers, retaining every original field and unresolved cell.

These outputs remain candidates. OCR absence never establishes a source dash.
"""
import argparse,csv,gzip,hashlib,io,json,re
from decimal import Decimal
from pathlib import Path
from gap_school_south_fetch import AREA

FIELDS=['name','position','remuneration','expenses','pdfPage','category']
SPECS={
35:{'pages':list(range(63,93)),'bounds':[880,1530,1830],'firstTrusteeEnd':1000,'ranges':{63:[560,3150],92:[400,1320]},'defaultRange':[400,3150],'uniformUppercaseNamesAndTitles':True},
38:{'pages':list(range(60,95)),'bounds':[600,1550,1920],'boundsByPage':{60:[840,1280,1560,1840]},'ranges':{60:[650,1300]},'defaultRange':[650,3100],'trusteePages':[60],'uniformUppercaseNamesAndTitles':True},
69:{'pages':list(range(45,52)),'bounds':[1040,1670,2010],'boundsByPage':{45:[1170,1560,2010]},'ranges':{45:[800,1150]},'defaultRange':[620,3150],'trusteePages':[45],'uniformUppercaseNamesAndTitles':True},
70:{'pages':list(range(54,61)),'bounds':[1080,1810,2180],'firstTrusteeEnd':1000,'ranges':{54:[410,3150],60:[300,1900]},'defaultRange':[300,3150]},
78:{'pages':list(range(52,57)),'bounds':[1680,1680,2000],'boundsByPage':{52:[1300,1690,2040]},'ranges':{52:[650,1080],53:[650,2860],54:[250,2860],55:[200,2860],56:[200,1140]},'defaultRange':[250,2800],'trusteePages':[52]},
79:{'pages':list(range(59,70)),'bounds':[820,1550,2020],'firstTrusteeEnd':1600,'ranges':{59:[1060,3150],69:[250,760]},'defaultRange':[250,3150]},
}
MONEY=re.compile(r'^\(?-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?\)?$')

def clean(s):return ' '.join(s.split())
def amount(s):
    s=clean(s)
    if s in ('-','–','—'):return 'UNRESOLVED:source-dash-needs-pixel-proof'
    if not s:return 'UNRESOLVED:missing-detection'
    s=re.sub(r'^[S$]\s*','',s)
    if not MONEY.fullmatch(s):return 'UNRESOLVED:'+s
    return str(Decimal(s.replace(',','').replace('(','-').replace(')','')))

def row(cells,district,page,y,evidence):
    spec=SPECS[district];name,title,pay,expense=map(clean,cells[:4]);extra=cells[4:]
    upper=name.upper()
    compact=upper.replace(' ','')
    if not name or upper in ('NAME','TOTAL') or upper.startswith(('TOTAL ','CONSOLIDATED ','SCHEDULE ','DETAILED ','ELECTED ','LIST ','REMUNERATION ','A. LIST','B. REMUNERATION','C. REMUNERATION','SCHOOL DISTRICT','SCHOOL! DISTRICT','PAGE |','FISCAL YEAR ENDED','STATEMENT OF FINANCIAL')) or compact.startswith(('TOTALELECTEDOFFICIALS','TOTALDETAILEDEMPLOYEES','TOTALEMPLOYEES','CONSOLIDATEDTOTAL')):return None
    if not re.search('[A-Za-zÀ-ž]',name):return None
    category='school-trustees' if page in spec.get('trusteePages',[]) or (page==spec['pages'][0] and y<spec.get('firstTrusteeEnd',0)) else 'employee-remuneration'
    raw_expense=expense;footnotes=[];layout_revisions=[]
    split_boundary=600 if district==38 else 820
    spanning_name_title_box=any(min(p[0] for p in w['box'])<split_boundary<max(p[0] for p in w['box']) for w in evidence.get('paddleBoxes',[]))
    if district in (38,79) and not title and spanning_name_title_box:
        # Only a source-specific closed vocabulary may separate a Paddle box
        # spanning adjacent name/title cells. Both original box/text are kept.
        roles={38:['DIRECTOR OF INSTRUCTION - LEARNING SERVICES','ASSISTANT SECRETARY-TREASURER','MANAGER - FINANCIAL SERVICES','MANAGER - INFORMATION SERVICES','COORDINATOR - HUMAN RESOURCES','COMPUTER SYSTEMS TECHNOLOGIST','APPLICATION DEV/DATABASE ADMINISTRATION','PEST CONTROL TECHNICIAN','DISTRCT ADMINISTRATOR','EXECUTIVE ASSISTANT','TRADES FOREPERSON','HVAC TECHNICIAN','BUSINESS ASSISTANT','VICE PRINCIPAL','SUPERINTENDENT','COUNSELLOR','PRINCIPAL','PLUMBER','PAINTER','TEACHER'],79:['Teachers, Admin Officer','Teachers, Admin Offi','Business Admin, CUPE','Business Admin, USW','Educational Admin','Admin Officer','Business Admin','CUPE 12','Teachers','CUPE','USW']}
        for role in roles[district]:
            if name.endswith(' '+role):
                layout_revisions.append({'kind':'source-specific-merged-name-title-box','before':[name,None],'after':[name[:-len(role)].rstrip(),role]})
                name=name[:-len(role)].rstrip();title=role;break
    if district==79:
        marker=re.search(r'\s*(\*{1,2})$',expense)
        if marker:footnotes.append(marker.group(1));expense=expense[:marker.start()].rstrip()
    if district==38 and category=='school-trustees':
        # A Paddle box can cover both the numeric expense and a separate term
        # column. Keep its whole text, and only parse the explicitly leading cell.
        term=re.match(r'^(\$?\s*\d[\d,]*)(?:\s+)((?:July|November).*)$',expense,re.I)
        if term:expense=term.group(1);extra=[term.group(2),*extra]
    return {'name':name,'position':title or None,'remuneration':amount(pay),'expenses':amount(expense),'pdfPage':page,'category':category,'sourceY300dpi':y,'rawCells':cells,'sourceExpenseLiteral':raw_expense,'sourceExpenseFootnotes':footnotes,'sourceSpecificLayoutRevisions':layout_revisions,'supportingExtraCells':extra,**evidence}

def tesseract(raw,district):
    spec=SPECS[district];page=raw['physicalPage'];bounds=spec.get('boundsByPage',{}).get(page,spec['bounds']);lo,hi=spec.get('ranges',{}).get(page,spec['defaultRange']);groups={}
    for w in csv.DictReader(io.StringIO(raw['tesseractRawTsv']),delimiter='\t',quoting=csv.QUOTE_NONE):
        if w['level']!='5' or not w['text'].strip():continue
        # Only exclude the scanned page-edge rule channel. Logical control
        # labels must remain intact before they are recognized as controls.
        data_left,data_right=20,2470
        if not data_left<=int(w['left'])<data_right:continue
        y=int(w['top'])+int(w['height'])/2
        if not lo<y<hi:continue
        groups.setdefault(tuple(w[k] for k in ['page_num','block_num','par_num','line_num']),[]).append(w)
    rows=[]
    for ws in groups.values():
        cs=[[] for _ in range(len(bounds)+1)]
        for w in sorted(ws,key=lambda w:int(w['left'])):cs[sum(int(w['left'])>=b for b in bounds)].append(w['text'])
        y=sum(int(w['top'])+int(w['height'])/2 for w in ws)/len(ws)
        r=row([' '.join(c) for c in cs],district,page,y,{'tesseractWords':ws})
        if r is not None:rows.append(r)
    return rows

def paddle(raw,district):
    spec=SPECS[district];page=raw['physicalPage'];bounds=spec.get('boundsByPage',{}).get(page,spec['bounds']);lo,hi=spec.get('ranges',{}).get(page,spec['defaultRange']);groups=[]
    for box,text,score in sorted(raw['rapidOcrRaw'],key=lambda w:sum(p[1] for p in w[0])/4):
        y=sum(p[1] for p in box)/4
        data_left,data_right=20,2470
        if not data_left<=min(p[0] for p in box)<data_right:continue
        if not lo<y<hi:continue
        g=next((g for g in groups[-3:] if abs(g['y']-y)<18),None)
        if g is None:g={'y':y,'boxes':[]};groups.append(g)
        g['boxes'].append({'box':box,'text':text,'confidence':score})
    rows=[]
    for g in groups:
        cs=[[] for _ in range(len(bounds)+1)]
        for w in sorted(g['boxes'],key=lambda w:min(p[0] for p in w['box'])):cs[sum(min(p[0] for p in w['box'])>=b for b in bounds)].append(w['text'])
        r=row([' '.join(c) for c in cs],district,page,g['y'],{'paddleBoxes':g['boxes']})
        if r is not None:rows.append(r)
    return rows

def comparison(value,field,district):
    if not isinstance(value,str):return value
    v=re.sub(r'\s+','',value)
    if field in ('name','position') and SPECS[district].get('uniformUppercaseNamesAndTitles'):v=v.upper()
    return v

def run(n):
    first=[];second=[];refs=[];pagecounts=[]
    for p in SPECS[n]['pages']:
        file=AREA/'raw-ocr'/f'sd{n}-sofi-2025-p{p}.json.gzip'
        if not file.exists():raise FileNotFoundError(file)
        b=file.read_bytes();raw=json.loads(gzip.decompress(b));a=tesseract(raw,n);c=paddle(raw,n);first+=a;second+=c;refs.append({'path':str(file),'sha256':hashlib.sha256(b).hexdigest()});pagecounts.append({'physicalPage':p,'readerOneRows':len(a),'readerTwoRows':len(c)})
    diffs=[]
    for i in range(max(len(first),len(second))):
        a=[first[i][f] for f in FIELDS] if i<len(first) else None;b=[second[i][f] for f in FIELDS] if i<len(second) else None
        if a is None or b is None or [comparison(x,f,n) for x,f in zip(a,FIELDS)]!=[comparison(x,f,n) for x,f in zip(b,FIELDS)] or any(isinstance(x,str) and x.startswith('UNRESOLVED:') for x in (a or [])+(b or [])):
            diffs.append({'sequence':i+1,'tesseract':a,'paddle':b})
    result={'district':n,'spec':SPECS[n],'rawProofs':refs,'tesseractRows':first,'paddleRows':second,'pageCounts':pagecounts,'initialFieldDifferences':diffs,'acceptedRows':0,'comparisonOnlyRule':'Remove whitespace. Only sources35/38/69 have an explicit independently image-checked uppercase typography convention for names/titles; case-only comparisons preserve both raw transcripts. No other letter/digit/punctuation normalization.'}
    (AREA/f'sd{n}-scan-parsed-v9.json.gzip').write_bytes(gzip.compress((json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
    print(json.dumps({'district':n,'counts':[len(first),len(second)],'differences':len(diffs),'pageCountDifferences':[x for x in pagecounts if x['readerOneRows']!=x['readerTwoRows']],'firstDifferences':diffs[:6]},ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--district',type=int,action='append',choices=list(SPECS));args=ap.parse_args()
    for n in args.district or SPECS:run(n)
