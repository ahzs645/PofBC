#!/usr/bin/env python3
"""Independent table parsing of retained Tesseract TSV and Paddle OCR boxes.

Missing OCR expense detections remain UNRESOLVED, never implicit zero/dash.
Whitespace-only comparison preserves each engine's original field transcript.
"""
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
from decimal import Decimal

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_native'
FIELDS=['name','position','remuneration','expenses','pdfPage','category']
MONEY=re.compile(r'(?<!\d)\(?-?\d[\d,]*(?:\.\d{2})?\)?(?!\d)')
SPECS={
    53:{'pages':[7,8,9,10,11,12],'bounds':{7:[1100,1500,2000],'default':[850,1500,2000]},
        'yRanges':{7:[900,1350],8:[350,3200],9:[250,3200],10:[250,3200],11:[250,3200],12:[250,550]}},
    84:{'pages':[54,56],'bounds':{54:[970,1650,2000],56:[1500,1500,1950]},
        'yRanges':{54:[820,2550],56:[920,1190]}},
}


def clean(value):return re.sub(r'\s+',' ',value).strip()


def comparison(value):
    return re.sub(r'\s+','',value) if isinstance(value,str) else value


def amount(value):
    value=clean(value)
    if not value:return 'UNRESOLVED:missing-detection'
    if value in ['-','–','—']:return 'UNRESOLVED:source-dash-needs-image-confirmation'
    # A currency glyph recognized as S supplies no numeric character.
    value=re.sub(r'^[S$]\s*','',value)
    matches=MONEY.findall(value)
    if len(matches)!=1:return 'UNRESOLVED:'+value
    allowed=re.sub(MONEY,'',value).strip()
    if allowed not in ['', '$']:return 'UNRESOLVED:'+value
    return str(Decimal(matches[0].replace(',','').replace('(','-').replace(')','')))


def row_from_cells(cells,page,district,geometry):
    name,title,pay,expense=map(clean,cells)
    # This reader does not invent commas for OCR failures; the target is kept
    # from its source geometry and reviewed even when the name is uncertain.
    if not name or name.upper().startswith(('NAME','TOTAL','SCHEDULE','DETAILED','REMUNERATION')):
        return None
    return {'name':name,'position':title or None,'remuneration':amount(pay),'expenses':amount(expense),
            'pdfPage':page,'category':'school-trustees' if (district==53 and page==7) or (district==84 and page==56) else 'employee-remuneration',
            **geometry,'rawCells':list(cells)}


def tesseract(raw,spec,district):
    number=raw['physicalPage'];bounds=spec['bounds'].get(number,spec['bounds'].get('default'));low,high=spec['yRanges'][number]
    groups={}
    for word in csv.DictReader(io.StringIO(raw['tesseractRawTsv']),delimiter='\t',quoting=csv.QUOTE_NONE):
        if word['level']!='5' or not word['text'].strip():continue
        y=int(word['top'])+int(word['height'])/2
        if not low<y<high:continue
        key=tuple(word[k] for k in ['page_num','block_num','par_num','line_num'])
        groups.setdefault(key,[]).append(word)
    result=[]
    for words in groups.values():
        cells=[[] for _ in range(4)]
        for word in sorted(words,key=lambda x:int(x['left'])):
            cells[sum(int(word['left'])>=b for b in bounds)].append(word['text'])
        row=row_from_cells([' '.join(x) for x in cells],number,district,
                           {'sourceY300dpi':sum(int(w['top'])+int(w['height'])/2 for w in words)/len(words),'sourceTsvWords':words})
        if row:result.append(row)
    return result


def paddle(raw,spec,district):
    number=raw['physicalPage'];bounds=spec['bounds'].get(number,spec['bounds'].get('default'));low,high=spec['yRanges'][number]
    groups=[]
    for box,text,confidence in sorted(raw['rapidOcrRawBoxes'],key=lambda w:sum(p[1] for p in w[0])/4):
        y=sum(p[1] for p in box)/4
        if not low<y<high:continue
        g=next((g for g in reversed(groups[-3:]) if abs(g['y']-y)<20),None)
        if g is None:g={'y':y,'boxes':[]};groups.append(g)
        g['boxes'].append({'box':box,'text':text,'confidence':confidence})
    result=[]
    for group in groups:
        cells=[[] for _ in range(4)]
        for word in sorted(group['boxes'],key=lambda w:min(p[0] for p in w['box'])):
            cells[sum(min(p[0] for p in word['box'])>=b for b in bounds)].append(word['text'])
        row=row_from_cells([' '.join(x) for x in cells],number,district,
                           {'sourceY300dpi':group['y'],'sourcePaddleBoxes':group['boxes']})
        if row:result.append(row)
    return result


def main():
    for district,spec in SPECS.items():
        first=[];second=[];refs=[]
        for number in spec['pages']:
            path=AREA/f'sd{district}-p{number}-dual-ocr.json.gzip';b=path.read_bytes();raw=json.loads(gzip.decompress(b))
            refs.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest()})
            first.extend(tesseract(raw,spec,district));second.extend(paddle(raw,spec,district))
        differences=[]
        for i in range(max(len(first),len(second))):
            a=[first[i][f] for f in FIELDS] if i<len(first) else None
            b=[second[i][f] for f in FIELDS] if i<len(second) else None
            if a is None or b is None or list(map(comparison,a))!=list(map(comparison,b)) or any(isinstance(v,str) and v.startswith('UNRESOLVED:') for v in a+b):
                differences.append({'sequence':i+1,'tesseract':a,'paddle':b})
        out={'districtNumber':district,'spec':spec,'rawProofs':refs,'tesseractRows':first,'paddleRows':second,
             'comparisonOnlyNormalization':'remove whitespace only in strings; original engine strings retained separately',
             'unresolvedDifferences':differences,'acceptedRows':0}
        path=AREA/f'sd{district}-2025-scan-parsed-v1.json.gzip';blob=gzip.compress((json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0)
        path.write_bytes(blob)
        print(json.dumps({'district':district,'counts':[len(first),len(second)],'differences':len(differences),'firstFlags':differences[:5]},ensure_ascii=False))


if __name__=='__main__':main()
