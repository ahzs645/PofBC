#!/usr/bin/env python3
"""Independent Poppler bbox reader for Government OIC peer review.

Does not import or call the author parser. Numeric right-edge clusters establish
salary/travel columns; name fragments establish row groups before joining wraps.
"""
import argparse
import collections
import gzip
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COL=ROOT/'research/salaries/continuation-government-police'
REVIEW=ROOT/'research/salaries/continuation-2026-11-01/reviews'
CACHE=Path('/tmp/continuation-government-police')
NUM=re.compile(r'^-?\d{1,3}(?:,\d{3})*$')

def number(t):return int(t.replace(',',''))
def digest(b):return hashlib.sha256(b).hexdigest()

def poppler(pdf):
    data=subprocess.check_output(['pdftotext','-bbox',str(pdf),'-'])
    data=re.sub(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]',b'',data)
    tree=ET.fromstring(data);ns={'h':'http://www.w3.org/1999/xhtml'}
    return [[dict(x0=float(w.attrib['xMin']),y0=float(w.attrib['yMin']),x1=float(w.attrib['xMax']),y1=float(w.attrib['yMax']),text=w.text or '') for w in p.findall('.//h:word',ns)] for p in tree.findall('.//h:page',ns)]

def parse_column(words,pno,start,end,with_travel,first_format):
    min_y=100 if end-start>240 else 45
    ws=[w for w in words if start-.5<=w['x0']<end-.5 and min_y<w['y0']<746]
    if first_format:range_lo,range_hi=start+85,start+133
    elif with_travel:raise ValueError('unexpected travel layout')
    elif end-start>240:range_lo,range_hi=start+180,start+245
    else:range_lo,range_hi=start+100,start+165
    possible=[w for w in ws if NUM.fullmatch(w['text']) and range_lo<w['x0']<range_hi]
    if not possible:return [],[]
    right=collections.Counter(round(w['x1'],1) for w in possible).most_common(1)[0][0]
    pays=[w for w in possible if abs(w['x1']-right)<.6]
    if not pays:return [],[]
    ymin=min(w['y0'] for w in pays)-13;ymax=max(w['y0'] for w in pays)+12
    ws=[w for w in ws if ymin<=w['y0']<=ymax]
    lines=[]
    for w in sorted(ws,key=lambda w:(w['y0'],w['x0'])):
        same=next((g for g in reversed(lines[-3:]) if abs(g['y']-w['y0'])<1.4),None)
        if same is None:same=dict(y=w['y0'],words=[]);lines.append(same)
        same['words'].append(w)
    lines.sort(key=lambda g:g['y'])
    groups=[];cur=None
    for line in lines:
        ordered=sorted(line['words'],key=lambda w:w['x0'])
        ps=[w for w in ordered if w in pays]
        ex=[w for w in ordered if with_travel and w['x0']>right+8 and NUM.fullmatch(w['text'])]
        letters=[w for w in ordered if not NUM.fullmatch(w['text']) and w['text']!='$']
        frag=' '.join(w['text'] for w in letters).strip()
        if not frag and not ps and not ex:continue
        is_new=bool(re.search(r'[A-Za-zÀ-ž][^,]*,',frag)) or frag.startswith('DELAUNAY-BELLEVILLE')
        if is_new:
            if cur is not None:groups.append(cur)
            cur=dict(fragments=[],pay=[],expense=[],words=[])
        elif cur is None:
            # The only non-row characters allowed within the numeric extent are
            # column $ markers; arbitrary text must not silently be discarded.
            assert not frag and not ps and not ex,(pno,start,'unassigned line',frag,ps,ex)
            continue
        if frag:cur['fragments'].append(dict(y=line['y'],text=frag))
        cur['pay']+=ps;cur['expense']+=ex;cur['words']+=ordered
    if cur is not None:groups.append(cur)
    rows=[];wrapped=[]
    for g in groups:
        assert len(g['pay'])==1 and len(g['expense'])<=1,(pno,start,g)
        name=' '.join(f['text'] for f in g['fragments'])
        assert re.search(r'[A-Za-z]',name),(pno,'nameless row',g)
        row=['public-service',name,None,number(g['pay'][0]['text']),number(g['expense'][0]['text']) if g['expense'] else None,pno]
        rows.append(row)
        if len(g['fragments'])>1:wrapped.append(dict(row=row,columnStart=start,fragments=g['fragments'],salaryY=g['pay'][0]['y0']))
        # All monetary cells in the row are classified; no unnamed amount dropped.
        numeric=[w for w in g['words'] if NUM.fullmatch(w['text'])]
        assert len(numeric)==len(g['pay'])+len(g['expense']),(pno,name,'unassigned numeric cell',numeric)
    assert len(rows)==len(pays),(pno,start,'unassigned pay anchors',len(rows),len(pays))
    return rows,wrapped

def extract(source,pages):
    end_year=int(source['periodEnd'][:4]);travel=end_year<=2003
    if travel:starts=[63,243,423,612]
    elif end_year==2004:starts=[56,228,409,612]
    else:starts=[69.5,321.5,612]
    out=[];wrapped=[]
    for pn in source['pages']:
        for start,end in zip(starts,starts[1:]):
            rows,wrap=parse_column(pages[pn-1],pn,start,end,travel,travel);out+=rows;wrapped+=wrap
    return out,wrapped

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');args=parser.parse_args()
    sources=[s for s in json.loads((COL/'sources.json').read_text())['sources'] if s['category']=='appointee-remuneration'];results=[]
    proof_path=REVIEW/'government-oic-poppler-evidence.json.gzip'
    stored=json.loads(gzip.decompress(proof_path.read_bytes())) if args.offline else []
    proof=[]
    for source in sources:
        pdf=CACHE/('pa-'+source['year'].replace('/','-')+'.pdf')
        if args.offline:pages=next(x['pages'] for x in stored if x['sourceId']==source['id'])
        else:
            assert digest(pdf.read_bytes())==source['sha256'];pages=poppler(pdf)
        rows,wrapped=extract(source,pages);candidate=json.loads(gzip.decompress((COL/source['file']).read_bytes()))
        if rows!=candidate:
            mismatches=[dict(index=i,independent=a,candidate=b) for i,(a,b) in enumerate(zip(rows,candidate)) if a!=b]
            print(json.dumps(dict(id=source['id'],rows=len(rows),expected=len(candidate),mismatches=mismatches[:12]),indent=2));raise AssertionError('independent Poppler mismatch')
        assert digest((COL/source['file']).read_bytes())==source['dataSha256']
        result=dict(sourceId=source['id'],originalSha256=source['sha256'],dataSha256=source['dataSha256'],rowCount=len(rows),salarySum=sum(r[3] for r in rows),knownTravelSum=sum(r[4] for r in rows if r[4] is not None),nullTravelRows=sum(r[4] is None for r in rows),negativeSalaryRows=[r for r in rows if r[3]<0],wrappedNameRows=wrapped,rowsByPhysicalPage=dict(collections.Counter(r[5] for r in rows)),allFieldsOrderAndMultiplicityEqual=True)
        results.append(result);proof_pages=[ws if i+1 in source['pages'] else [] for i,ws in enumerate(pages)];proof.append(dict(sourceId=source['id'],originalSha256=source['sha256'],pages=proof_pages,rows=rows));print(source['year'],len(rows),'all rows equal; wraps',len(wrapped))
    if not args.offline:
        proof_path.write_bytes(gzip.compress(json.dumps(proof,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));(REVIEW/'government-oic-poppler-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print('Independent Poppler verified',sum(x['rowCount'] for x in results),'rows')

if __name__=='__main__':main()
