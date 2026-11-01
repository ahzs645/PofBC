#!/usr/bin/env python3
"""Stage complete PHSA OCR with two engines and exact original-image conflicts.

Research-only runtime: /tmp/held-health-ocr/venv/bin/python. No accepted rows are
emitted by this acquisition/staging script. Unresolved names or money require
original-image review before a complete source can be proposed for import.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/tmp/sector-health/phsa-2025.pdf')
SOURCE_SHA = '809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c'
CACHE = Path('/tmp/held-health-ocr/full')
AUDIT = ROOT/'research/salaries/held-resolution-2026-11-01/health'
FIXTURE = ROOT/'research/salaries/recovery-wave-2026-11-01/health/phsa-2024-25-page-1-staged.json.gzip'
DASH_MASK_SHA = '884ce82070908630f6df09c8521a1968c09d3350f26e4136c697f86f59974f64'
DOC = ENGINE = None


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def name_comparison(value):
    """Root-authorized typography comparison; never join words or change letters."""
    return re.sub(r'\s*,\s*', ',', re.sub(r'\s+', ' ', value).strip())


def money_token(raw):
    token = re.sub(r'\s+', '', raw)
    if token in ('-', '–', '—'):
        return {'kind':'explicit-dash', 'value':None, 'raw':raw}
    if not token:
        return {'kind':'not-recognized', 'value':None, 'raw':raw}
    if re.fullmatch(r'(?:\d{1,3}(?:,\d{3})+|\d+)', token):
        return {'kind':'number', 'value':int(token.replace(',', '')), 'raw':raw}
    if re.fullmatch(r'\((?:\d{1,3}(?:,\d{3})+|\d+)\)', token):
        return {'kind':'number', 'value':-int(token[1:-1].replace(',', '')), 'raw':raw}
    if re.fullmatch(r'-(?:\d{1,3}(?:,\d{3})+|\d+)', token):
        return {'kind':'number', 'value':int(token.replace(',', '')), 'raw':raw}
    return {'kind':'unparsed', 'value':None, 'raw':raw}


def native_image(page, document):
    """Paint original 300-dpi tiles in PDF display order, without resampling."""
    from PIL import Image
    scale = 300/72
    canvas = Image.new('RGB', (round(page.rect.width*scale),round(page.rect.height*scale)), 'white')
    placements = []
    for info in page.get_image_info(xrefs=True):
        b = info['bbox']
        im = Image.open(io.BytesIO(document.extract_image(info['xref'])['image'])).convert('RGB')
        target = (round((b[2]-b[0])*scale),round((b[3]-b[1])*scale))
        if im.size != target:
            raise ValueError(f'Original tile requires resampling: {im.size} vs {target}')
        xy = (round(b[0]*scale),round(b[1]*scale))
        canvas.paste(im, xy)
        placements.append({'xref':info['xref'],'bbox':b,'pixelSize':list(im.size),'pasteAt':list(xy)})
    if page.get_text().strip():
        raise ValueError('Unexpected native text/overlay; review the changed original')
    return canvas, placements


def rapid_rows(raw, width, height):
    def center(r):
        return sum(p[0] for p in r[0])/4, sum(p[1] for p in r[0])/4
    headers = [r for r in raw if r[1].strip().lower()=='name' and center(r)[0]<width*.60]
    if len(headers) != 1:
        raise ValueError('RapidOCR table name header count differs from one')
    top = max(p[1] for p in headers[0][0])
    body = [r for r in raw if top<center(r)[1]<height*.93]
    names = sorted([r for r in body if center(r)[0]<width*.60],key=lambda r:center(r)[1])
    rows, controls = [], []
    for name in names:
        x,y = center(name)
        if re.match(r'^total\b',name[1].strip(),re.I):
            controls.append(name)
            continue
        fields = []
        for left,right in [(width*.60,width*.77),(width*.77,width*.88)]:
            hits = [r for r in body if left<center(r)[0]<right and abs(center(r)[1]-y)<14]
            fields.append(hits[0] if len(hits)==1 else None)
        rows.append({'name':name[1], 'nameConfidence':name[2], 'nameBox':name[0],
                     'y':y, 'pay':fields[0], 'expenses':fields[1]})
    return rows, controls


def tess_rows(tsv, width, height):
    groups = {}
    for word in csv.DictReader(io.StringIO(tsv),delimiter='\t'):
        if word['level']!='5' or not word.get('text','').strip():
            continue
        key = tuple(word[k] for k in ['page_num','block_num','par_num','line_num'])
        groups.setdefault(key,[]).append(word)
    lines = []
    for words in groups.values():
        words.sort(key=lambda w:float(w['left']))
        y = sum(float(w['top'])+float(w['height'])/2 for w in words)/len(words)
        lines.append((y,words))
    headers = [(y,w) for y,w in lines if w[0]['text'].strip().lower()=='name']
    if len(headers)!=1:
        raise ValueError('Tesseract table name header count differs from one')
    top = headers[0][0]+14
    rows, controls = [], []
    for y,words in sorted(lines):
        if not top<y<height*.93:
            continue
        fields=[]
        for left,right in [(0,width*.60),(width*.60,width*.77),(width*.77,width*.88)]:
            kept=[w for w in words if left<float(w['left'])+float(w['width'])/2<right]
            fields.append({'raw':' '.join(w['text'] for w in kept),
                           'confidence':min(float(w['conf']) for w in kept) if kept else None,
                           'words':kept})
        if not fields[0]['raw']:
            continue
        if re.match(r'^total\b',fields[0]['raw'],re.I):
            controls.append({'y':y,'fields':fields})
            continue
        rows.append({'name':fields[0]['raw'],'nameConfidence':fields[0]['confidence'],
                     'y':y,'pay':fields[1],'expenses':fields[2],'nameWords':fields[0]['words']})
    return rows,controls


def expense_image_evidence(image, y):
    import numpy as np
    width,height=image.size
    top,bottom=round(y-22),round(y+22)
    left,right=round(width*1990/2550),round(width*2175/2550)
    crop=np.asarray(image)[top:bottom,left:right]
    mask=np.any(crop<128,axis=2)
    yy,xx=np.where(mask)
    if not len(xx):
        return {'kind':'blank-original-cell','rectangle':[left,top,right,bottom],
                'templateMatched':False,'isExplicitDash':False}
    glyph=mask[yy.min():yy.max()+1,xx.min():xx.max()+1]
    packed=np.packbits(glyph).tolist()
    digest=sha(encode([int(glyph.shape[1]),int(glyph.shape[0]),packed]))
    return {'rectangle':[left,top,right,bottom],
            'inkRectangle':[int(left+xx.min()),int(top+yy.min()),int(left+xx.max()+1),int(top+yy.max()+1)],
            'glyphWidth':int(glyph.shape[1]),'glyphHeight':int(glyph.shape[0]),
            'blackPixels':int(glyph.sum()),'packedMask':packed,'maskSha256':digest,
            'templateMatched':digest==DASH_MASK_SHA,'isExplicitDash':digest==DASH_MASK_SHA,
            'basis':'Exact binary glyph identity with all 18 independently image-reviewed first-page dash cells; never detector absence.'}


def compare_page(pn, image, rrows, trows):
    proof=[];page_conflicts=[]
    if len(rrows)!=len(trows):
        page_conflicts.append({'kind':'independent-row-count','rapidRows':len(rrows),'tesseractRows':len(trows)})
    used=set()
    for index,tess in enumerate(trows):
        choices=[(abs(r['y']-tess['y']),j,r) for j,r in enumerate(rrows) if j not in used and abs(r['y']-tess['y'])<16]
        rapid=None
        if len(choices)==1:
            _,j,rapid=choices[0];used.add(j)
        conflicts=[]
        if rapid is None:
            conflicts.append('independent-row-boundary')
        elif name_comparison(rapid['name'])!=name_comparison(tess['name']):
            conflicts.append('name-disagreement')
        if tess['nameConfidence'] is None or tess['nameConfidence']<85:
            conflicts.append('tesseract-name-confidence-below-85')
        if rapid and rapid['nameConfidence']<.98:
            conflicts.append('rapid-name-confidence-below-0.98')
        pay=money_token(tess['pay']['raw']);expense=money_token(tess['expenses']['raw'])
        rapid_pay=money_token(rapid['pay'][1] if rapid and rapid['pay'] else '')
        rapid_exp=money_token(rapid['expenses'][1] if rapid and rapid['expenses'] else '')
        if pay['kind']!='number' or rapid_pay['kind']!='number' or pay['value']!=rapid_pay['value']:
            conflicts.append('remuneration-disagreement-or-unparsed')
        if tess['pay']['confidence'] is None or tess['pay']['confidence']<90:
            conflicts.append('tesseract-pay-confidence-below-90')
        if rapid and rapid['pay'] and rapid['pay'][2]<.98:
            conflicts.append('rapid-pay-confidence-below-0.98')
        glyph=expense_image_evidence(image,tess['y'])
        expense_resolution=None
        if glyph['isExplicitDash']:
            expense_resolution='explicit-original-dash-exact-reviewed-image-template'
            expense_value=None
        elif expense['kind']=='number' and rapid_exp['kind']=='number' and expense['value']==rapid_exp['value']:
            expense_value=expense['value']
            expense_resolution='two-independent-OCR-numeric-agreement'
            if tess['expenses']['confidence'] is None or tess['expenses']['confidence']<90:
                conflicts.append('tesseract-expense-confidence-below-90')
            if rapid and rapid['expenses'] and rapid['expenses'][2]<.98:
                conflicts.append('rapid-expense-confidence-below-0.98')
        else:
            expense_value=expense['value']
            conflicts.append('expense-disagreement-unparsed-or-unreviewed-glyph')
        row=['provincial-health-services-authority',name_comparison(tess['name']),None,pay['value'],expense_value,pn]
        crop_path=None
        if conflicts:
            crop_path=CACHE/'conflicts'/f'p{pn:03d}-r{index+1:02d}.png'
            crop_path.parent.mkdir(exist_ok=True)
            y=round(tess['y']);image.crop((190,max(0,y-25),2210,min(image.height,y+25))).save(crop_path)
        proof.append({'physicalPage':pn,'sourceRowOnPage':index+1,'candidateRow':row,
                      'status':'held-for-image-review' if conflicts else 'independent-fields-agree',
                      'conflicts':conflicts,'conflictImagePath':str(crop_path) if crop_path else None,
                      'tesseract':tess,'rapidocr':rapid,'payToken':pay,'rapidPayToken':rapid_pay,
                      'expenseToken':expense,'rapidExpenseToken':rapid_exp,
                      'expenseOriginalImage':glyph,'expenseResolution':expense_resolution})
    if len(used)!=len(rrows):
        page_conflicts.append({'kind':'unmatched-rapid-name-rows','rows':[r for j,r in enumerate(rrows) if j not in used]})
    return proof,page_conflicts


def init_worker():
    global DOC,ENGINE
    import fitz
    import cv2
    from rapidocr_onnxruntime import RapidOCR
    cv2.setNumThreads(1)
    DOC=fitz.open(SOURCE)
    ENGINE=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1)


def process_page(pn):
    page_path=CACHE/'pages'/f'p{pn:03d}.json.gzip'
    if page_path.exists():
        old=json.loads(gzip.decompress(page_path.read_bytes()))
        return {'page':pn,'rows':len(old['rowEvidence']),'conflictRows':sum(bool(r['conflicts']) for r in old['rowEvidence']),'pageConflicts':old['pageConflicts'],'cached':True}
    started=time.perf_counter()
    image,placements=native_image(DOC[pn-1],DOC)
    image_path=CACHE/'images'/f'p{pn:03d}.png';image.save(image_path)
    prefix=CACHE/'tesseract'/f'p{pn:03d}'
    subprocess.run(['tesseract',str(image_path),str(prefix),'-l','eng','--psm','6','txt','tsv'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    tess_text=prefix.with_suffix('.txt').read_text();tess_tsv=prefix.with_suffix('.tsv').read_text()
    raw,elapsed=ENGINE(str(image_path))
    if raw is None:
        raise ValueError(f'No RapidOCR result for physical page {pn}')
    rapid,rc=rapid_rows(raw,*image.size);tess,tc=tess_rows(tess_tsv,*image.size)
    rows,conflicts=compare_page(pn,image,rapid,tess)
    evidence={'sourceSha256':SOURCE_SHA,'physicalPage':pn,'imagePath':str(image_path),
              'imageSha256':sha(image_path.read_bytes()),'imageDimensions':list(image.size),
              'imageMode':'original 300-dpi tile stitching, no resampling','imagePlacements':placements,
              'rapidocrRaw':raw,'rapidocrElapsed':elapsed,'tesseractRawText':tess_text,
              'tesseractRawTsv':tess_tsv,'rowEvidence':rows,'pageConflicts':conflicts,
              'controlEvidence':{'rapidocr':rc,'tesseract':tc},'wallSeconds':time.perf_counter()-started,
              'acceptedRows':0,'completeEmployeeScheduleVerified':False}
    page_path.write_bytes(gzip.compress(encode(evidence),mtime=0))
    return {'page':pn,'rows':len(rows),'conflictRows':sum(bool(r['conflicts']) for r in rows),
            'pageConflicts':conflicts,'wallSeconds':evidence['wallSeconds'],'evidenceSha256':sha(page_path.read_bytes())}


def check_fixture():
    path=CACHE/'pages/p001.json.gzip'
    e=json.loads(gzip.decompress(path.read_bytes()));fixture=json.loads(gzip.decompress(FIXTURE.read_bytes()))['rows']
    assert len(e['rowEvidence'])==len(fixture)==49
    pay=expense=name=0;accepted_without_conflict=0;masked_bad=[]
    for r,f in zip(e['rowEvidence'],fixture):
        candidate=r['candidateRow'];name+=candidate[1]==f[1];pay+=candidate[3]==f[3];expense+=candidate[4]==f[4]
        if not r['conflicts']:
            accepted_without_conflict+=1
            if candidate!=f:masked_bad.append({'candidate':candidate,'fixture':f})
    if masked_bad:
        raise ValueError('Fixture error escaped conflict flags: '+repr(masked_bad))
    dash=[r for r,f in zip(e['rowEvidence'],fixture) if f[4] is None]
    assert len(dash)==18 and all(r['expenseOriginalImage']['isExplicitDash'] for r in dash)
    result={'rows':49,'literalCandidateNameMatches':name,'remunerationMatches':pay,'expenseMatches':expense,
            'all18ImageVerifiedDashesMatchExactTemplate':True,'rowsWithoutConflict':accepted_without_conflict,
            'heldRows':49-accepted_without_conflict,'fixtureErrorsEscapingConflictFlags':0,
            'acceptedRows':0,'evidenceSha256':sha(path.read_bytes()),'fixtureSha256':sha(FIXTURE.read_bytes())}
    (AUDIT/'first-page-two-engine-benchmark.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


def summarize():
    pages=[];conflicts=[];rows=[]
    for path in sorted((CACHE/'pages').glob('p*.json.gzip')):
        e=json.loads(gzip.decompress(path.read_bytes()));pn=e['physicalPage']
        pages.append({'physicalPage':pn,'rows':len(e['rowEvidence']),'file':str(path),'sha256':sha(path.read_bytes()),'pageConflicts':e['pageConflicts']})
        rows.extend(e['rowEvidence'])
        conflicts.extend({'physicalPage':pn,'sourceRowOnPage':r['sourceRowOnPage'],'candidateRow':r['candidateRow'],
                          'conflicts':r['conflicts'],'imagePath':r['conflictImagePath'],
                          'rawTesseractName':r['tesseract']['name'],
                          'rawRapidName':r['rapidocr']['name'] if r['rapidocr'] else None}
                         for r in e['rowEvidence'] if r['conflicts'])
    summary={'sourceUrl':'https://www.phsa.ca/about-site/Documents/FY2025-Employee-Salary-and-Expenses-exceeding-75000.pdf',
             'sourceSha256':SOURCE_SHA,'physicalPdfPages':284,'processedPages':len(pages),
             'stagedRows':len(rows),'acceptedRows':0,'completeEmployeeScheduleVerified':False,
             'conflictRows':len(conflicts),'pagesWithBoundaryConflicts':sum(bool(p['pageConflicts']) for p in pages),
             'candidateRemunerationSum':sum(r['candidateRow'][3] or 0 for r in rows),
             'candidateKnownExpenseSum':sum(r['candidateRow'][4] or 0 for r in rows),
             'exactReviewedDashTemplateRows':sum(r['expenseOriginalImage']['isExplicitDash'] for r in rows),
             'pages':pages,'conflicts':conflicts,
             'scope':'Entire processed original pages staged. Conflicts/uncertainties require original-image review; no arbitrary page-slice import.'}
    (AUDIT/'complete-ocr-staging-progress.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['processedPages','stagedRows','acceptedRows','conflictRows','pagesWithBoundaryConflicts','candidateRemunerationSum','candidateKnownExpenseSum','exactReviewedDashTemplateRows']}),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pages',default='1')
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--fixture-check',action='store_true')
    parser.add_argument('--summarize',action='store_true')
    args=parser.parse_args()
    AUDIT.mkdir(parents=True,exist_ok=True)
    for folder in ['pages','images','tesseract','conflicts']:
        (CACHE/folder).mkdir(parents=True,exist_ok=True)
    if args.fixture_check:
        check_fixture();return
    if args.summarize:
        summarize();return
    if sha(SOURCE.read_bytes())!=SOURCE_SHA:
        raise ValueError('Original PDF fingerprint changed')
    pages=[]
    for part in args.pages.split(','):
        if '-' in part:
            first,last=map(int,part.split('-'));pages.extend(range(first,last+1))
        else:
            pages.append(int(part))
    if not all(1<=p<=284 for p in pages):
        raise ValueError('Invalid physical PDF page')
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers,initializer=init_worker) as pool:
        futures={pool.submit(process_page,p):p for p in pages}
        for future in concurrent.futures.as_completed(futures):
            try:
                print(json.dumps(future.result()),flush=True)
            except Exception as ex:
                print(json.dumps({'page':futures[future],'error':str(ex)}),flush=True)
    summarize()


if __name__=='__main__':
    main()
