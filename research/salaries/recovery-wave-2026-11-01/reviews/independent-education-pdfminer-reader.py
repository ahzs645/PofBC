#!/usr/bin/env python3
"""Third-engine native review. Reads ORIGINAL PDFs, never author's reader/evidence.

Phase one freezes PDFMiner original rows before phase two opens normalized payloads.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re

from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTChar, LTTextLine

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
SPECS=[
    dict(key='ubc',sourceId='recovery-ubc-sofi-2025-26-employees',slug='university-of-bc',period='2025/26',
         original='/tmp/pofbc-sector-education/0b9387de913e9302.body',sha256='2df95ed199e8e566d670534c8d4e65baacf7f97f19362707933c60723768ebfc',pages=list(range(42,190))),
    dict(key='cm25',sourceId='recovery-coast-mountain-sofi-2024-25-employees',slug='coast-mountain-college',period='2024/25',
         original='/tmp/pofbc-sector-education/d5af412fa1d197a9.body',sha256='13d16deca4cdaa6723b10f844b2927b30451246eb034ca48fae7206e3c656b3f',pages=list(range(34,39))),
    dict(key='cm24',sourceId='recovery-coast-mountain-sofi-2023-24-employees',slug='coast-mountain-college',period='2023/24',
         original='/tmp/pofbc-sector-education/b3961b373f16740e.body',sha256='47ad6017a6b4d354493a99321eea1be2cd70c6b378c287e1f1ac89b0c98e422b',pages=list(range(33,37))),
    dict(key='cm23',sourceId='recovery-coast-mountain-sofi-2022-23-employees',slug='coast-mountain-college',period='2022/23',
         original='/tmp/pofbc-sector-education/61caf40621b659ee.body',sha256='273fbc9428a2639f875573e8051957702ea9822068cd57ac03fa8a610968c422',pages=list(range(34,37)))
]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
    path=Path(path);raw=path.read_bytes()
    return json.loads(gzip.decompress(raw)if path.suffix=='.gzip'else raw)
def save(path,data):
    path=Path(path)
    assert not path.exists(),f'Immutable receipt already exists: {path}'
    raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
    path.write_bytes(gzip.compress(raw,mtime=0)if path.suffix=='.gzip'else raw)
    return sha(path)
def walk_lines(item):
    if isinstance(item,LTTextLine):yield item
    elif hasattr(item,'__iter__'):
        for child in item:yield from walk_lines(child)
def walk_chars(item):
    if isinstance(item,LTChar):yield item
    elif hasattr(item,'__iter__'):
        for child in item:yield from walk_chars(child)
def text(chars):
    return re.sub(r'\s+',' ',''.join(c.get_text() for c in sorted(chars,key=lambda c:c.x0))).strip()
def money(value):
    value=value.replace('$','').replace(',','').strip()
    if not value or value in {'-','—'}:return None
    if re.fullmatch(r'\(\d+\)',value):return -int(value[1:-1])
    assert re.fullmatch(r'-?\d+',value),repr(value)
    return int(value)

def ubc_rows(page,number,spec):
    lines=[line for line in walk_lines(page)if line.get_text().strip()]
    header_y=max(line.y0 for line in lines if line.get_text().strip()=='Remuneration')
    result=[]
    for name_min,pay_min,expense_min,column_end in [(50,170,240,301),(320,435,510,569)]:
        name_lines=sorted([line for line in lines if name_min<=line.x0<pay_min and 80<line.y0<header_y-3],key=lambda line:-line.y0)
        pay_lines=sorted([line for line in lines if pay_min<=line.x0<expense_min and 80<line.y0<header_y-3
                          and re.fullmatch(r'[\d,]+',line.get_text().strip())],key=lambda line:-line.y0)
        expense_lines=[line for line in lines if expense_min<=line.x0<column_end and 80<line.y0<header_y-3]
        previous_y=header_y
        for pay in pay_lines:
            parts=[line.get_text().strip()for line in name_lines if pay.y0-0.2<=line.y0<previous_y-0.2]
            name=' '.join(parts)
            if ',' not in name or name.startswith(('Remuneration','Total')):
                # The last column ends with named/below-threshold/overall controls.
                previous_y=pay.y0
                continue
            expenses=[line.get_text().strip()for line in expense_lines if abs(line.y0-pay.y0)<0.2]
            assert len(expenses)==1,(number,name,expenses)
            result.append(dict(row=[spec['slug'],name,None,money(pay.get_text()),money(expenses[0]),number],
                               originalCells=dict(nameLines=parts,pay=pay.get_text().strip(),expenses=expenses[0],
                                                  payBBox=list(pay.bbox),nameBBoxes=[list(line.bbox)for line in name_lines if pay.y0-0.2<=line.y0<previous_y-0.2])))
            previous_y=pay.y0
    return result

def cm_rows(page,number,spec):
    chars=list(walk_chars(page));lines=list(walk_lines(page))
    if spec['key']=='cm25':
        pay_min,expense_min,total_min=309,395,469
        name_split=None
    elif spec['key']=='cm24':
        pay_min,expense_min,total_min=269,354,425
        name_split=185
    else:
        pay_min,expense_min,total_min=245,357,457
        name_split=146.3
    result=[]
    header_y=max(line.y0 for line in lines if line.get_text().strip()=='Expenses')
    # Monetary LTTextLine elements identify the numeric baselines. Names are then
    # independently rebuilt from PDFMiner characters inside original column bounds.
    anchors=sorted([line for line in lines if pay_min<line.x0<expense_min and 60<line.y0<header_y-3
                    and re.fullmatch(r'[\d,]+',line.get_text().strip())],key=lambda line:-line.y0)
    for pay in anchors:
        y=pay.y0
        strip=[char for char in chars if abs(char.y0-y)<1.2]
        name_chars=[char for char in strip if 60<=char.x0<pay_min-5]
        if name_split:
            surname=text([char for char in name_chars if char.x0<name_split])
            given=text([char for char in name_chars if char.x0>=name_split])
            name=surname+', '+given
        else:name=text(name_chars)
        if name.startswith(('Total','Grand','Carry Forward','Brought Forward')):continue
        assert ',' in name and not name.endswith(', '),(number,name)
        expenses=text([char for char in strip if expense_min<=char.x0<total_min-5])
        combined=text([char for char in strip if total_min<=char.x0<560])
        result.append(dict(row=[spec['slug'],name,None,money(pay.get_text()),money(expenses),number],
                           originalCells=dict(pay=pay.get_text().strip(),expenses=expenses,combinedTotal=combined,
                                              combinedTotalValue=money(combined),payBBox=list(pay.bbox))))
    return result

def extract():
    outputs=[]
    for spec in SPECS:
        assert sha(spec['original'])==spec['sha256']
        output=dict(spec=spec,engine='PDFMiner.six',reader='Independent LTTextLine columns and stateful wrapped names for UBC; independent LTChar cell reconstruction for Coast Mountain',rows=[])
        pages=extract_pages(spec['original'],page_numbers=[p-1 for p in spec['pages']],laparams=LAParams())
        for number,page in zip(spec['pages'],pages,strict=True):
            output['rows']+=(ubc_rows(page,number,spec)if spec['key']=='ubc'else cm_rows(page,number,spec))
        outputs.append(output)
        Path('/tmp/independent-education-'+spec['key']+'-rows.json').write_text(json.dumps(output,ensure_ascii=False))
        print(spec['key'],len(output['rows']),flush=True)
    path=OUT/'independent-education-pdfminer-original-rows-v2.json.gzip'
    digest=save(path,dict(reviewer='/root/recovery_municipal',extractedOn='2026-11-01',readerInputsOnlyOriginalPdfs=True,
                          initialExtractionFrozenBeforeOpeningAuthorPayloads='independent-education-pdfminer-original-rows.json.gzip',
                          initialReaderCorrections=['UBC control threshold contains a comma; explicitly exclude Remuneration/Total labels.',
                                                    'Coast Mountain continuation salary rows extend above fixed first-page cutoff; use each page original Expenses header baseline.'],sources=outputs))
    print(str(path),digest,flush=True)

def compare():
    independent=read(OUT/'independent-education-pdfminer-original-rows-v2.json.gzip')
    manifest_path=ROOT/'research/salaries/recovery-education/sources.json'
    assert sha(manifest_path)=='256c1ee6aac4fdea895f8d10b34acefd2f5b0a02f00bd006e67c0a9f2b004730'
    manifest=read(manifest_path)
    comparisons=[]
    for source in independent['sources']:
        spec=source['spec'];entry=next(s for s in manifest['sources']if s['id']==spec['sourceId'])
        author_path=ROOT/'research/salaries/recovery-education'/entry['file'];assert sha(author_path)==entry['dataSha256']
        mine=[item['row']for item in source['rows']];author=read(author_path)
        diff=[dict(rowOrdinal=i+1,independent=a,author=b)for i,(a,b)in enumerate(zip(mine,author))if a!=b]
        extra_mine=list((Counter(tuple(row)for row in mine)-Counter(tuple(row)for row in author)).elements())
        extra_author=list((Counter(tuple(row)for row in author)-Counter(tuple(row)for row in mine)).elements())
        result=dict(sourceId=spec['sourceId'],originalSha256=spec['sha256'],authorDataSha256=entry['dataSha256'],independentRows=len(mine),authorRows=len(author),
                    allSixFieldsOrderedEqual=mine==author,rowFieldDifferences=diff,independentOnlyMultisetRows=extra_mine,authorOnlyMultisetRows=extra_author,
                    remunerationSum=sum(row[3]for row in mine),knownExpenseSum=sum(row[4]for row in mine if row[4]is not None),
                    negativeExpenseRows=[row for row in mine if row[4]is not None and row[4]<0],
                    duplicateNames={name:count for name,count in Counter(row[1]for row in mine).items()if count>1},pages=spec['pages'])
        comparisons.append(result)
        print(spec['key'],len(mine),len(author),'equal',mine==author,'differences',len(diff),flush=True)
    save(OUT/'independent-education-pdfminer-comparison-v2.json',dict(reviewer='/root/recovery_municipal',reviewedOn='2026-11-01',
        independentOriginalRowsFile='research/salaries/recovery-wave-2026-11-01/reviews/independent-education-pdfminer-original-rows-v2.json.gzip',
        independentOriginalRowsSha256=sha(OUT/'independent-education-pdfminer-original-rows-v2.json.gzip'),manifestSha256=sha(manifest_path),comparisons=comparisons))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--extract',action='store_true');parser.add_argument('--compare',action='store_true');args=parser.parse_args()
    if args.extract:extract()
    if args.compare:compare()
