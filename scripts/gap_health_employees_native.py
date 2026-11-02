#!/usr/bin/env python3
"""Strict literal native table readers for recovered public health employee histories.

This file prepares candidates only. Full row agreement, original-image review,
source controls, peer closure and root acceptance are separate gates.
"""
from __future__ import annotations
import collections,gzip,json,pathlib,re
from decimal import Decimal
from gap_health_employees_fetch import ROOT,AREA,sha

NUM=r'(?:[−-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?|\((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?\))'
CELL=r'(?:[−‐–—-]?\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?|\((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?\)|[-‐–—]+)'
ROW=re.compile(r'^\s*(?P<name>\S.*?)\s{2,}\$?\s*(?P<pay>'+NUM+r')(?:\s+(?:\$?\s*(?P<expense>'+CELL+r'))?)?\s*$')
CONTROL=re.compile(r'^(?:total|grand total|employer portion|consolidated total|subtotal|sub total|total remuneration|total payments|total greater|total less|payments equal|payments less|payments to|remuneration exceeding|with remuneration less)',re.I)

def load(path):return json.loads(gzip.decompress(pathlib.Path(path).read_bytes()))
def flat(s):return ' '.join(s.split())
def nameclean(s):return re.sub(r'\s*,\s*',',',flat(s))
def amount(s):
    if s is None or not s.strip():return None
    s=re.sub(r'\s|\$','',s).replace('−','-').replace('‐','-').replace('–','-').replace('—','-')
    if re.fullmatch(r'[-‐–—]+',s):return None
    if not re.fullmatch(NUM,s):raise ValueError(('Nonliteral monetary cell',s))
    if s.startswith('('):s='-'+s[1:-1]
    d=Decimal(s.replace(',',''));return int(d) if d==d.to_integral() else float(d)

def selected_page(key,pn,text):
    if pn==1:return False #Official library cover, independently described in the original manifest.
    f=flat(text).lower()
    if re.search(r'(?:board member|board of directors|board remuneration|board members)',f[:1000]):return False
    if key.startswith('providence-health-care-'):
        return bool(re.search(r'last name\s+first name\s+remuneration\s+expenses',f))
    if key in ('island-health-2022-23','island-health-2023-24'):
        return 'each employee' in f and bool(re.search(r'name\s+remuneration\s+expenses',f))
    if key.startswith('vancouver-coastal-health-'):
        if re.search(r'(?:board member|board of directors|board remuneration)',f[:800]):return False
        return bool(re.search(r'(?:employee|name)\s+(?:remunerations?|renumerations?)',f))
    return True

def primary(spec,evidence):
    key=evidence['key'];pages=load(ROOT/evidence['popplerLayout']['path'])['pages'];rows=[];controls=[];flags=[];scopepages=[]
    for pn,page in enumerate(pages,1):
        if not selected_page(key,pn,page):continue
        n_before=len(rows)
        for line in page.splitlines():
            m=ROW.fullmatch(line)
            if not m:
                if ',' in line and re.search(r'\d[\d,.]*\s+(?:[-‐–—]|\d)',line) and not CONTROL.match(line.strip()) and not re.search(r'\b(?:total|year|nurs|employees|remuneration|prepared|the |for |these |over |march |june |july )\b',line,re.I):flags.append({'physicalPage':pn,'kind':'unparsed-potential-named-line','line':line})
                continue
            left=m['name'];pay=amount(m['pay']);exp=amount(m['expense'])
            if re.match(r'^(?:\$?[\d,]+|(?:over|under|less than|greater than)\b)',left.strip(),re.I):continue
            if CONTROL.match(left):controls.append({'physicalPage':pn,'label':flat(left),'remuneration':pay,'expenses':exp,'raw':line});continue
            if pay is None:continue
            if pay<75000 and ',' in left:flags.append({'physicalPage':pn,'kind':'named-pay-below-threshold-requires-review','line':line,'name':nameclean(left)})
            if key.startswith('providence-health-care-'):
                bits=re.split(r'\s{2,}',left.strip())
                if len(bits)!=2:flags.append({'physicalPage':pn,'kind':'split-name-columns','line':line,'fields':bits});continue
                name=nameclean(bits[0]+','+bits[1])
            else:
                if ',' not in left:
                    flags.append({'physicalPage':pn,'kind':'pay-line-without-comma-name','line':line});continue
                name=nameclean(left)
            if any(c.isdigit() for c in name):flags.append({'physicalPage':pn,'kind':'name-digits-require-original-review','line':line,'name':name})
            rows.append({'row':[spec['item']['employerSlug'],name,None,pay,exp,pn],'rawLine':line,'payToken':m['pay'],'expenseToken':m['expense'],'sourceRowOnPage':len(rows)-n_before+1})
        if len(rows)>n_before:scopepages.append(pn)
    return {'rows':rows,'controls':controls,'flags':flags,'employeePages':scopepages}

def secondary(spec,evidence):
    """Reconstruct rows from MuPDF positions and literal header columns only.

    No primary row count, name, payment, expense or table-page list is read.
    """
    key=evidence['key'];pages=load(ROOT/evidence['mupdfWords']['path'])['pages'];transforms=json.loads((AREA/'native-page-transforms.json').read_bytes())[spec['sourceSha256']];texts=load(ROOT/evidence['textProbe']['path'])['pages'];rows=[];flags=[];geometries=[]
    carried=None
    for page,probe,transform in zip(pages,texts,transforms):
        pn=page['physicalPage']
        if not selected_page(key,pn,probe['text']):continue
        words=page['words'];width=page['width']
        if transform['rotation']:
            a,b,c,d,e,f=transform['rotationMatrix'];converted=[]
            for word in words:
                points=[(a*x+c*y+e,b*x+d*y+f) for x in [word[0],word[2]] for y in [word[1],word[3]]];xs,ys=zip(*points);converted.append([min(xs),min(ys),max(xs),max(ys),*word[4:]])
            words=converted
        heads=[w for w in words if w[0]>.32*width and re.fullmatch(r'(?:remunerations?|renumerations?|wages)',w[4],re.I)]
        if not heads and carried is None:
            if any(',' in w[4] for w in words):flags.append({'physicalPage':pn,'kind':'no-independent-pay-header'})
            continue
        if not heads:
            header=carried['payHeader'];left,right=carried['salaryCenterBounds'];bodytop=0;firstx=carried['firstNameStart'];geom={'physicalPage':pn,'payHeader':header,'salaryCenterBounds':[left,right],'bodyAfter':0,'firstNameStart':firstx,'headerInheritedFromPhysicalPage':carried['physicalPage']}
            geometries.append(geom)
        else:
            # Table headers are right of the name field. The leftmost valid header
            # is the monetary-column title; page-wide schedule captions are excluded.
            header=max(heads,key=lambda w:w[0])
            # A source caption can contain REMUNERATION above the true table header.
            strong=[]
            for h in heads:
                near=[w for w in words if abs(w[1]-h[1])<1.5]
                if any(re.fullmatch(r'EXPENSES',w[4],re.I) and w[0]>h[2] for w in near) and any(re.fullmatch(r'NAME|EMPLOYEE|FIRST',w[4],re.I) and w[0]<h[0] for w in near):strong.append(h)
            if strong:header=max(strong,key=lambda w:w[0])
            if any(w[4].upper()=='WAGES' for w in heads):header=next(w for w in heads if w[4].upper()=='WAGES')
            left=header[0]-20;right=header[2]+40;bodytop=header[1]+2
            # FIRST NAME's visible position supplies Providence's source split.
            firsts=[w[0] for w in words if w[4].upper()=='FIRST' and abs(w[1]-header[1])<2]
            firstx=min(firsts) if firsts else None
            geom={'physicalPage':pn,'payHeader':header[:5],'salaryCenterBounds':[left,right],'bodyAfter':bodytop,'firstNameStart':firstx};geometries.append(geom);carried=geom
        anchors=[]
        for w in words:
            if w[1]<bodytop or not left<((w[0]+w[2])/2)<right:continue
            try:v=amount(w[4])
            except ValueError:continue
            if v is None:continue
            anchors.append((w,v))
        anchors.sort(key=lambda pair:(pair[0][1],pair[0][0]))
        used_y=[];pagecount=0
        for w,pay in anchors:
            if any(abs(w[1]-y)<1 for y in used_y):continue
            same=sorted([q for q in words if abs(q[1]-w[1])<2.1],key=lambda q:q[0])
            namewords=[q for q in same if q[0]<w[0]-2 and q[4]!='$'];name=nameclean(' '.join(q[4] for q in namewords))
            if not name or re.match(r'^(?:Prepared under|FOR THE |Financial |STATEMENT |SCHEDULE )',name,re.I) or CONTROL.match(name) or re.match(r'^(?:\$?[\d,]+|(?:over|under|less than|greater than)\b)',name,re.I):continue
            if key.startswith('providence-health-care-'):
                if firstx is None:flags.append({'physicalPage':pn,'kind':'missing-visible-first-name-column'});continue
                last=nameclean(' '.join(q[4] for q in namewords if q[0]<firstx-1));first=nameclean(' '.join(q[4] for q in namewords if q[0]>=firstx-1));name=last+','+first
            elif ',' not in name:
                if pay>=75000:flags.append({'physicalPage':pn,'kind':'pay-anchor-without-comma-name','name':name,'pay':pay,'words':same})
                continue
            exwords=[q for q in same if q[0]>w[2]+1 and q[4]!='$'];expraw=' '.join(q[4] for q in exwords)
            try:expense=amount(expraw)
            except ValueError:
                flags.append({'physicalPage':pn,'kind':'nonliteral-independent-expense','name':name,'raw':expraw,'words':same});continue
            used_y.append(w[1]);pagecount+=1
            rows.append({'row':[spec['item']['employerSlug'],name,None,pay,expense,pn],'sourceRowOnPage':pagecount,'y':w[1],'nameWords':[q[:5] for q in namewords],'remunerationWord':w[:5],'expenseWords':[q[:5] for q in exwords]})
    return {'rows':rows,'flags':flags,'pageGeometries':geometries}

def main():
    specs=json.loads((AREA/'recovered-employee-originals-v2.json').read_bytes());idx=json.loads((AREA/'native-reader-evidence-index-v2.json').read_bytes());by={x['sourceSha256']:x for x in idx};out=[]
    target=AREA/'native-candidates';target.mkdir(exist_ok=True)
    for spec in specs:
        ev=by[spec['sourceSha256']];r=primary(spec,ev);r.update(sourceSha256=spec['sourceSha256'],key=ev['key'])
        raw=gzip.compress(json.dumps(r,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);p=target/(ev['key']+'-poppler-primary.json.gzip');p.write_bytes(raw)
        item={'key':ev['key'],'sourceSha256':spec['sourceSha256'],'file':str(p.relative_to(ROOT)),'sha256':sha(raw),'rows':len(r['rows']),'pages':len(r['employeePages']),'firstPage':min(r['employeePages']) if r['employeePages'] else None,'lastPage':max(r['employeePages']) if r['employeePages'] else None,'flags':len(r['flags']),'controlRows':r['controls'],'remuneration':str(sum(Decimal(str(x['row'][3])) for x in r['rows'])),'expenses':str(sum(Decimal(str(x['row'][4] or 0)) for x in r['rows']))}
        other=secondary(spec,ev);other.update(sourceSha256=spec['sourceSha256'],key=ev['key']);oraw=gzip.compress(json.dumps(other,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);op=target/(ev['key']+'-mupdf-secondary.json.gzip');op.write_bytes(oraw)
        a=[tuple(x['row']) for x in r['rows']];b=[tuple(x['row']) for x in other['rows']];ca=collections.Counter(a);cb=collections.Counter(b)
        item.update(secondaryFile=str(op.relative_to(ROOT)),secondarySha256=sha(oraw),secondaryRows=len(b),secondaryFlags=len(other['flags']),rowsExactlyEqual=a==b,onlyPrimary=list((ca-cb).elements()),onlySecondary=list((cb-ca).elements()))
        out.append(item);print(json.dumps({k:v for k,v in item.items() if k not in ('onlyPrimary','onlySecondary')}|{'onlyPrimaryCount':len(item['onlyPrimary']),'onlySecondaryCount':len(item['onlySecondary'])}),flush=True)
    (AREA/'native-primary-candidate-index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
