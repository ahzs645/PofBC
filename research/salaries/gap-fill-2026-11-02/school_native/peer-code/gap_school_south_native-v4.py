#!/usr/bin/env python3
"""Independent physical-line and word-geometry readers of three district originals.

No Ministry hidden text is used. Candidate agreement is not acceptance: actual
rendered-source visibility and source-specific controls receive separate review.
"""
import argparse,collections,gzip,hashlib,json,re,subprocess,xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path
import fitz
from gap_school_south_fetch import AREA,CACHE

FIELDS=('name','position','department','remuneration','expenses','pdfPage','category')
SPECS={
37:{'kind':'department','pages':list(range(54,70)),'bounds':[156,298,430,504],'trusteeEnd':250},
39:{'kind':'separate-names','pages':list(range(56,112)),'bounds':[138,219,436,503],'trusteeEnd':315},
45:{'kind':'ordinary','pages':list(range(53,60)),'bounds':[218,434,497],'trusteeEnd':225},
75:{'kind':'ordinary','pages':list(range(8,14)),'bounds':[264,484,567],'trusteeEnd':250,'rowTolerance':3},
}
NUM=re.compile(r'^-?\d[\d,]*(?:\.\d{2})?$')

def clean(s):return ' '.join(s.split())
def sha(b):return hashlib.sha256(b).hexdigest()
def money(s):
    s=clean(s).replace('$','').replace(',','').strip()
    if s in ('-','–','—',''):return None
    if s.startswith('(') and s.endswith(')'):s='-'+s[1:-1]
    if not NUM.fullmatch(s):raise ValueError('Unparsed literal amount '+repr(s))
    return str(Decimal(s))

def record(cells,n,page,category,extra=None):
    c=SPECS[n]
    if c['kind']=='separate-names':
        surname,given,title,pay,expense=cells;name=surname+', '+given;department=None
        provenance={'sourceSurname':surname,'sourceGivenNames':given,'nameJoin':'Explicit source surname and given-name cells, joined with comma and space'}
    elif c['kind']=='department':
        name,title,department,pay,expense=cells;provenance={}
    else:name,title,pay,expense=cells;department=None;provenance={}
    if not name or not re.match(r'^[A-Za-zÀ-ž]',name) or re.search(r'\d',name):return None
    if name.upper() in ('TOTAL','CONSOLIDATED') or name.upper().startswith(('TOTAL ','CONSOLIDATED ','EMPLOYEE','ELECTED ','NAME','LAST NAME','DETAILED ')):return None
    if not NUM.fullmatch(pay.replace(',','').replace('$','').strip()):return None
    expense_literal=expense
    if n==45 and expense.rstrip().endswith('*'):
        expense=expense.rstrip()[:-1].rstrip()
        provenance['expenseFootnoteMarker']='*'
        provenance['expenseFootnoteMeaning']='Includes travel expenses for International Student Recruitment'
    return {'name':name,'position':title or None,'department':department,'remuneration':money(pay),'expenses':money(expense),'sourceCellTexts':cells,'sourceExpenseLiteral':expense_literal,'pdfPage':page,'category':category,**provenance,**(extra or {})}

def lines_reader(text,n):
    spec=SPECS[n];out=[];flags=[];controls=[]
    for number in spec['pages']:
        mode='school-trustees' if number==spec['pages'][0] else 'employee-remuneration'
        for line in text.split('\f')[number-1].splitlines():
            stripped=clean(line);upper=stripped.upper()
            if re.search(r'(?:DETAILED EMPLOYEES|EMPLOYEES WITH REMUNERATION EXCEEDING)',upper):mode='employee-remuneration'
            if upper.startswith(('TOTAL ','CONSOLIDATED ')):
                controls.append({'physicalPage':number,'line':line});continue
            stripped_without_cash=line.replace('$','')
            parts=[clean(x) for x in re.split(r'\s{2,}',stripped_without_cash.strip())]
            expected=4 if spec['kind']=='ordinary' else 5
            if len(parts)==expected:
                r=record(parts,n,number,mode,{'sourceLine':line})
                if r is not None:out.append(r);continue
            # Wrapped native position continuation: no name/pay fields appear.
            if len(parts)==1 and stripped and out and out[-1]['pdfPage']==number and len(line)-len(line.lstrip())>=12 and not re.search(r'\d',stripped):
                out[-1]['position']=clean((out[-1]['position'] or '')+' '+stripped)
                out[-1].setdefault('positionContinuationLines',[]).append(line)
            elif re.search(r'\b\d{2,3},\d{3}\b',line) and not upper.startswith(('TOTAL ','CONSOLIDATED ','EMPLOYEES','DETAILED ')):
                flags.append({'physicalPage':number,'sourceLine':line,'parts':parts,'reason':'money-bearing line not parsed as a named row'})
    return out,flags,controls

def geometry_reader(doc,n):
    spec=SPECS[n];out=[];flags=[];pages=[]
    for number in spec['pages']:
        page=doc[number-1];groups=[]
        for word in sorted(page.get_text('words'),key=lambda w:((w[1]+w[3])/2,w[0])):
            y=(word[1]+word[3])/2
            group=next((g for g in groups[-3:] if abs(g['y']-y)<spec.get('rowTolerance',1.6)),None)
            if group is None:group={'y':y,'words':[]};groups.append(group)
            group['words'].append(word)
        for group in groups:
            words=sorted(group['words'],key=lambda w:w[0]);cells=[[] for _ in range(len(spec['bounds'])+1)]
            for w in words:
                if w[4]=='$':continue
                cells[sum(w[0]>=bound for bound in spec['bounds'])].append(w[4])
            values=[clean(' '.join(c)) for c in cells]
            category='school-trustees' if number==spec['pages'][0] and group['y']<spec['trusteeEnd'] else 'employee-remuneration'
            r=record(values,n,number,category,{'sourceY':group['y'],'sourceWordBoxes':[list(w[:5]) for w in words]})
            if r is not None:
                out.append(r)
            else:
                title_index=2 if spec['kind']=='separate-names' else 1
                if not any(values[i] for i in range(title_index)) and values[title_index] and not any(values[title_index+1:]) and out and out[-1]['pdfPage']==number and group['y']-out[-1]['sourceY']<18:
                    out[-1]['position']=clean((out[-1]['position'] or '')+' '+values[title_index]);out[-1].setdefault('positionContinuationWords',[]).extend([list(w[:5]) for w in words])
        traces=page.get_texttrace()
        bad=[{'type':t['type'],'color':list(t['color']),'bbox':list(t['bbox']),'font':t['font']} for t in traces if t['type']!=0 or (t['color'] and min(t['color'])>.95)]
        pages.append({'physicalPage':number,'wordCount':len(page.get_text('words')),'imageCount':len(page.get_images()),'textTraceCount':len(traces),'nonPaintedOrWhiteTextTraces':bad,'pageWidth':page.rect.width,'pageHeight':page.rect.height})
    return out,flags,pages

def poppler_geometry_reader(xml,n):
    """Poppler's independent bbox extractor also preserves crowded source cells.

    The physical-line diagnostic above deliberately flags glued columns. Bbox
    words use the published column starts, without splitting a person's name
    using a title dictionary or borrowing MuPDF's recognized strings.
    """
    tree=ET.fromstring(xml);ns={'x':'http://www.w3.org/1999/xhtml'}
    source_pages=tree.findall('.//x:page',ns);spec=SPECS[n];out=[]
    for number in spec['pages']:
        groups=[]
        for word in sorted(source_pages[number-1].findall('.//x:word',ns),key=lambda w:((float(w.attrib['yMin'])+float(w.attrib['yMax']))/2,float(w.attrib['xMin']))):
            y=(float(word.attrib['yMin'])+float(word.attrib['yMax']))/2
            g=next((g for g in groups[-3:] if abs(g['y']-y)<spec.get('rowTolerance',1.6)),None)
            if g is None:g={'y':y,'words':[]};groups.append(g)
            g['words'].append(word)
        for g in groups:
            words=sorted(g['words'],key=lambda w:float(w.attrib['xMin']));cells=[[] for _ in range(len(spec['bounds'])+1)]
            for w in words:
                if w.text=='$':continue
                cells[sum(float(w.attrib['xMin'])>=bound for bound in spec['bounds'])].append(w.text or '')
            values=[clean(' '.join(c)) for c in cells]
            cat='school-trustees' if number==spec['pages'][0] and g['y']<spec['trusteeEnd'] else 'employee-remuneration'
            rec=record(values,n,number,cat,{'sourceY':g['y'],'popplerWordBoxes':[dict(w.attrib,text=w.text) for w in words]})
            if rec is not None:out.append(rec)
            else:
                title_index=2 if spec['kind']=='separate-names' else 1
                if not any(values[i] for i in range(title_index)) and values[title_index] and not any(values[title_index+1:]) and out and out[-1]['pdfPage']==number and g['y']-out[-1]['sourceY']<18:
                    out[-1]['position']=clean((out[-1]['position'] or '')+' '+values[title_index]);out[-1].setdefault('positionContinuationWords',[]).extend([dict(w.attrib,text=w.text) for w in words])
    return out

def run(n):
    spec=json.loads((AREA/f'sd{n}-issuer-retrieval.json').read_text());path=Path(spec['cachePath'])
    assert sha(path.read_bytes())==spec['sha256'];doc=fitz.open(path)
    rawtext=subprocess.check_output(['pdftotext','-layout',str(path),'-'])
    line_rows,af,controls=lines_reader(rawtext.decode(),n)
    bbox=subprocess.check_output(['pdftotext','-bbox-layout',str(path),'-'])
    (AREA/f'sd{n}-issuer-poppler-bbox.xml.gzip').write_bytes(gzip.compress(bbox,mtime=0))
    a=poppler_geometry_reader(bbox,n);b,bf,pages=geometry_reader(doc,n)
    diffs=[]
    for i in range(max(len(a),len(b))):
        av=[a[i].get(k) for k in FIELDS] if i<len(a) else None;bv=[b[i].get(k) for k in FIELDS] if i<len(b) else None
        if av!=bv:diffs.append({'sequence':i+1,'poppler':av,'mupdf':bv})
    out={'district':n,'source':spec,'spec':SPECS[n],'fields':FIELDS,'readers':['Poppler independent bbox-layout word geometry','MuPDF independent word geometry'],'popplerRows':a,'mupdfRows':b,'differences':diffs,'physicalLineDiagnosticRows':line_rows,'popplerPhysicalLineFlags':af,'mupdfFlags':bf,'controls':controls,'nativeVisibility':pages,'acceptedRows':0}
    (AREA/f'sd{n}-native-candidate-v4.json.gzip').write_bytes(gzip.compress((json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
    print(json.dumps({'district':n,'rows':[len(a),len(b)],'differences':len(diffs),'popplerFlags':len(af),'categories':dict(collections.Counter(x['category'] for x in a)),'firstDifferences':diffs[:8],'flags':af[:5]},ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--district',type=int,choices=list(SPECS),action='append');args=ap.parse_args()
    for n in args.district or SPECS:run(n)
