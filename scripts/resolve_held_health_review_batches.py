#!/usr/bin/env python3
"""Freeze a bounded original-image conflict batch while full OCR keeps running."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CACHE=Path('/tmp/held-health-ocr/full')
OUT=ROOT/'research/salaries/held-resolution-2026-11-01/health'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--batch',type=int,default=1)
    parser.add_argument('--limit',type=int,default=100)
    parser.add_argument('--prioritize-disagreements',action='store_true')
    args=parser.parse_args()
    target=OUT/f'review-batch-{args.batch:03d}.json'
    if target.exists():
        raise ValueError('Frozen review batch already exists; use a new batch id')
    previous=set()
    for path in OUT.glob('review-batch-*.json'):
        for r in json.loads(path.read_text())['rows']:
            previous.add((r['physicalPage'],r['sourceRowOnPage']))
    rows=[]
    for path in sorted((CACHE/'pages').glob('p*.json.gzip')):
        e=json.loads(gzip.decompress(path.read_bytes()))
        for r in e['rowEvidence']:
            key=(e['physicalPage'],r['sourceRowOnPage'])
            if not r['conflicts'] or key in previous:
                continue
            image=Path(r['conflictImagePath'])
            fields=[]
            for label in ['name','remuneration','expenses']:
                if any((label=='name' and 'name' in c) or
                       (label=='remuneration' and ('pay' in c or 'remuneration' in c)) or
                       (label=='expenses' and 'expense' in c) for c in r['conflicts']):
                    fields.append(label)
            rows.append({'physicalPage':e['physicalPage'],'sourceRowOnPage':r['sourceRowOnPage'],
                         'reviewTargetFields':fields,'conflicts':r['conflicts'],
                         'candidateRow':r['candidateRow'],'rawTesseract':r['tesseract'],
                         'rawRapidOcr':r['rapidocr'],'cropPath':str(image),
                         'cropSha256':sha(image.read_bytes()),'fullPageImagePath':e['imagePath'],
                         'fullPageImageSha256':e['imageSha256'],'completePageEvidencePath':str(path),
                         'completePageEvidenceSha256':sha(path.read_bytes())})
    if args.prioritize_disagreements:
        rows.sort(key=lambda r:(not any('disagreement' in c or 'boundary' in c for c in r['conflicts']),
                                r['physicalPage'],r['sourceRowOnPage']))
    rows=rows[:args.limit]
    if len(rows)<args.limit:
        raise ValueError(f'Only {len(rows)} new conflicts available; requested {args.limit}')
    # A review contact sheet contains unchanged original row crops. Labels are
    # outside the crop, and individual/full-page hashes remain the source truth.
    from PIL import Image,ImageDraw
    sheets=[]
    for offset in range(0,len(rows),10):
        group=rows[offset:offset+10]
        sheet=Image.new('RGB',(2020,75*len(group)),'white')
        draw=ImageDraw.Draw(sheet)
        for j,r in enumerate(group):
            draw.text((2,j*75+2),f"p{r['physicalPage']:03d} row{r['sourceRowOnPage']:02d} | "+', '.join(r['reviewTargetFields']),fill='black')
            crop=Image.open(r['cropPath']).convert('RGB')
            sheet.paste(crop,(0,j*75+20))
        path=CACHE/'conflicts'/f"batch-{args.batch:03d}-sheet-{offset//10+1:02d}.png"
        sheet.save(path)
        sheets.append({'path':str(path),'sha256':sha(path.read_bytes()),
                       'rows':[[r['physicalPage'],r['sourceRowOnPage']] for r in group]})
    result={'frozen':True,'date':'2026-11-01','batch':args.batch,'rowsToReview':len(rows),
            'sourceUrl':'https://www.phsa.ca/about-site/Documents/FY2025-Employee-Salary-and-Expenses-exceeding-75000.pdf',
            'sourceSha256':'809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c',
            'instructions':'Inspect each unchanged original row crop and transcribe the target field literally. Keep all raw alternatives and original-image provenance. Do not expand initials, infer letters from common names, alter a monetary value to match a total, or convert a dash/blank to0. Mark genuinely ambiguous source glyphs unresolved. Return NEW review receipts only; this batch is frozen. Full original page images and complete raw two-engine page evidence are linked for context.',
            'contactSheets':sheets,'rows':rows,'acceptedRows':0}
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    image_only={k:result[k] for k in ['frozen','date','batch','rowsToReview','sourceUrl','sourceSha256','instructions','contactSheets','acceptedRows']}
    image_only['fullBatchPath']=str(target.relative_to(ROOT))
    image_only['fullBatchSha256']=sha(target.read_bytes())
    image_only['rows']=[{k:r[k] for k in ['physicalPage','sourceRowOnPage','reviewTargetFields','cropPath',
                                         'cropSha256','fullPageImagePath','fullPageImageSha256',
                                         'completePageEvidencePath','completePageEvidenceSha256']} for r in rows]
    image_only_path=OUT/f'review-batch-{args.batch:03d}-images.json'
    image_only_path.write_text(json.dumps(image_only,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'path':str(target.relative_to(ROOT)),'sha256':sha(target.read_bytes()),
                      'imageOnlyPath':str(image_only_path.relative_to(ROOT)),'imageOnlySha256':sha(image_only_path.read_bytes()),
                      'rows':len(rows),'sheets':len(sheets),'first':[rows[0]['physicalPage'],rows[0]['sourceRowOnPage']],
                      'last':[rows[-1]['physicalPage'],rows[-1]['sourceRowOnPage']]}))


if __name__=='__main__':
    main()
