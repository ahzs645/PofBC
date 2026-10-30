#!/usr/bin/env python3
"""Rebuild the reviewed BCCSS 2017/18 scanned employee schedule.

Requires the original checksum-pinned PDF and the checked-in two-pass OCR evidence.
Explicit page/row corrections are guarded by their complete original text. Changed
OCR, source bytes, row counts, order or totals fail closed. The acceptance reflects
the recorded 2026-10-30 visual review; a rerun does not claim another visual review.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/bccss-ocr'
SLUG='bc-clinical-and-support-services-society'
URL='https://www.phsa.ca/about-site/Documents/2017%2018%20BCCSS%20Employee%20Salary%20and%20Expenses%20exceeding%2075%2c000.pdf'
PDF_SHA='8c74494d2b3fb201f48fa8243af20dd92070fb5cab5750728f86d77976522140'
ROW=re.compile(r'(.+?)\s+(\d[\d,]*)\s+([\d,]+|-)')


def sha(data):return hashlib.sha256(data).hexdigest()


def compact(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()


def parse_money(token):
    if token=='-':return None
    if not re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)',token):raise ValueError(f'Unexpected OCR money token {token!r}')
    return int(token.replace(',',''))


def correct_line(original,page,row,pass_id,corrections):
    matches=[c for c in corrections if c['pass']==pass_id and c['physicalPdfPage']==page and c['rowOnPage']==row]
    if len(matches)>1:raise ValueError('Duplicate review correction')
    if not matches:return original
    correction=matches[0]
    if original!=correction['original']:raise ValueError(f'OCR correction context changed on page{page}, row{row}, pass{pass_id}')
    return correction['corrected']


def parse_pass(evidence,review):
    pages=evidence['pages'];pass_id=evidence['id'];rows=[];total=None;applied=0
    if [p['physicalPdfPage'] for p in pages]!=list(range(1,12)):raise ValueError('Incomplete or duplicate OCR page sequence')
    for page in pages:
        n=page['physicalPdfPage'];text=page['text']
        if sha(text.encode())!=page['textSha256']:raise ValueError('OCR text hash mismatch')
        required=['BC Clinical and Support Services Society','Fiscal Year Ended 31 March 2018']
        if not all(s in text for s in required):raise ValueError('OCR employer/year heading changed')
        if n==1:
            if not re.search(r'346 employees',text) or '$75,000' not in text:raise ValueError('Cover employee count/threshold missing')
            continue
        started=False;finished=False;count=0
        for original in text.splitlines():
            if original.startswith('Name Remuneration Expenses'):
                if started:raise ValueError('Repeated table header within one page')
                started=True;continue
            if original.startswith('This statement'):
                finished=True;break
            if not started or not original.strip():continue
            if original.startswith('Total '):
                if n!=11 or total is not None:raise ValueError('Unexpected employee subtotal')
                m=re.fullmatch(r'Total\s+([\d,]+)\s+([\d,]+)',original)
                if not m:raise ValueError('Unparsed printed subtotal')
                total=tuple(parse_money(m[i]) for i in (1,2));continue
            count+=1
            line=correct_line(original,n,count,pass_id,review['corrections'])
            if line!=original:applied+=1
            m=ROW.fullmatch(line)
            if not m:raise ValueError(f'Unparsed OCR table row on page{n}: {line!r}')
            name,pay,expense=m.groups()
            name=re.sub(r'\s*,\s*',', ',' '.join(name.split()))
            pay,expense=parse_money(pay),parse_money(expense)
            if ',' not in name or re.search(r'\d',name):raise ValueError('Unresolved published name')
            if pay is None or pay<=75000:raise ValueError('Named employee below source threshold; review OCR, never guess an amount')
            rows.append([name,pay,expense,n])
        if not started or not finished or count!=review['expectedRowsByPage'][str(n)]:raise ValueError(f'Incomplete employee table on page{n}')
        if text.rstrip().splitlines()[-1].strip()!=str(n-1):raise ValueError('Printed page number differs from physical-page mapping')
    expected_applied=sum(c['pass']==pass_id for c in review['corrections'])
    if applied!=expected_applied:raise ValueError('Not all reviewed corrections were applied')
    expected=(review['printedNamedRemuneration'],review['printedNamedExpenses'])
    sums=(sum(r[1] for r in rows),sum(r[2] or 0 for r in rows))
    if total!=expected or sums!=expected or len(rows)!=review['printedNamedEmployeeCount']:raise ValueError(f'Employee count/controls do not reconcile: {len(rows)}, {sums}, {total}')
    if rows[-1]!=['Van Gogh, Justin',77598,None,11]:raise ValueError('The final out-of-order employee row was lost or altered')
    return rows


def verify(pdf,evidence,review):
    if sha(pdf.read_bytes())!=PDF_SHA:raise ValueError('Original source PDF fingerprint changed; review required')
    if review['sourcePdfSha256']!=PDF_SHA or evidence['sourcePdfSha256']!=PDF_SHA:raise ValueError('Review/OCR refers to another PDF')
    if review['visuallyReviewedPhysicalPages']!=list(range(1,12)):raise ValueError('Visual review record is incomplete')
    passes=evidence['passes']
    if [(p['id'],p['dpi'],p['tesseractPageSegmentationMode']) for p in passes]!=[('250-psm6',250,6),('300-psm4',300,4)]:raise ValueError('Two reviewed OCR configurations required')
    a,b=[parse_pass(p,review) for p in passes]
    if a!=b:raise ValueError('Corrected OCR passes disagree in row order, names, amounts or pages')
    if sha(compact(a))!=review['reviewedRawRowsSha256']:raise ValueError('Reviewed row fingerprint changed')
    return a


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pdf',type=Path,default=Path('/tmp/pofbc_health_sources/bccss-2017-18.pdf'))
    p.add_argument('--output',type=Path,default=OUT)
    p.add_argument('--offline',action='store_true')
    args=p.parse_args()
    if not args.pdf.exists():
        if args.offline:raise ValueError(f'Missing original PDF: {args.pdf}')
        raw=urllib.request.urlopen(URL,timeout=60).read()
        if not raw.startswith(b'%PDF-'):raise ValueError('Source request did not return a PDF')
        args.pdf.parent.mkdir(parents=True,exist_ok=True);args.pdf.write_bytes(raw)
    review=json.loads((OUT/'review/2017-18-review.json').read_text())
    ocr_raw=(OUT/review['ocrFile']).read_bytes()
    if sha(ocr_raw)!=review['ocrFileSha256']:raise ValueError('OCR evidence gzip fingerprint changed')
    evidence=json.loads(gzip.decompress(ocr_raw));rawrows=verify(args.pdf,evidence,review)
    rows=[[SLUG,name,None,pay,expense,n] for name,pay,expense,n in rawrows]
    normalized=compact(rows);compressed=gzip.compress(normalized,compresslevel=9,mtime=0)
    source={
        'id':'bccss-employee-remuneration-2017-18','employerSlug':SLUG,
        'employerName':'BC Clinical and Support Services Society','sector':'Health authorities',
        'year':'2017/18','slug':'2017-18','periodType':'fiscal','periodStart':'2017-04-01','periodEnd':'2018-03-31',
        'title':'BC Clinical and Support Services Society employee remuneration and expenses, fiscal year ended 31 March 2018',
        'sourceUrl':URL,'sourceIndexUrl':'https://www.phsa.ca/about/accountability/budget-financials',
        'sha256':PDF_SHA,'file':'2017-18.json.gzip','dataSha256':sha(compressed),'normalizedSha256':sha(normalized),
        'status':'verified','verifiedOn':'2026-10-30','category':'employee-remuneration','scope':'named-employees-over-threshold',
        'scopeDescription':'Named BCCSS employees whose remuneration exceeds $75,000; separate from PHSA employee schedules',
        'threshold':75000,'thresholdRule':'over','currency':'CAD','amountUnit':'dollars','amountPrecision':'whole-dollar',
        'nameDisclosure':'published-full-name','positionDisclosure':'not-published','rowCount':len(rows),
        'totalRemuneration':sum(r[3] for r in rows),'totalExpenses':sum(r[4] or 0 for r in rows),'pages':list(range(2,12)),
        'validation':{
            'sourceFormat':'image-only PDF','pdfSha256Verified':True,'sourcePdfPages':11,
            'ocrEvidenceFile':review['ocrFile'],'ocrEvidenceSha256':review['ocrFileSha256'],
            'reviewFile':'review/2017-18-review.json','reviewedOcrConfigurations':[{'dpi':250,'psm':6},{'dpi':300,'psm':4}],
            'ocrEngine':evidence['engine'],'sameEngineLimitation':'Different resolution/segmentation passes can share OCR errors; full-page visual review resolved shared errors.',
            'rowsComparedAcrossCorrectedPasses':len(rows),'correctedPassesEqual':True,
            'explicitCorrectionOccurrences':len(review['corrections']),
            'distinctRowsWithExplicitCorrections':len({(c['physicalPdfPage'],c['rowOnPage']) for c in review['corrections']}),
            'visuallyReviewedPhysicalPages':review['visuallyReviewedPhysicalPages'],
            'rowsByPhysicalPage':review['expectedRowsByPage'],'publishedNamedEmployeeCount':346,
            'publishedRemunerationSubtotal':33202601,'publishedExpensesSubtotal':1352527,
            'remunerationSubtotalExact':True,'expensesSubtotalExact':True,'remunerationResidual':0,'expensesResidual':0,
            'missingExpenseRows':sum(r[4] is None for r in rows),'explicitZeroExpenseRows':sum(r[4]==0 for r in rows),
            'exactDuplicateSourceRows':sum(n-1 for n in Counter(tuple(r[:5]) for r in rows).values()),
            'outOfOrderFinalEmployeePreserved':True},
        'notes':[
            'Separate BCCSS employer; records are not appended to the PHSA employer merely because PHSA hosts the PDF.',
            'The source states a cash-receipts basis: money physically received by or paid on behalf of the employee; remuneration includes salaries/wages, taxable benefits, bonuses and stipends.',
            'This source uses strictly greater than $75,000. The adjacent 2016/17 BCCSS schedule has its own inclusive threshold and must not supply this year\'s rule.',
            'Expense dashes remain missing, not zero. Positions are not published. Names are not unique personal identifiers.',
            'Both OCR passes contain shared recognition errors. Explicit corrections are tied to the original page image and complete before/after row text; no value was chosen to force totals.',
            'The source adds Van Gogh, Justin after the Z names. The final employee row is retained despite its position outside the alphabetical run.'
        ]}
    manifest={'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':[source]}
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'2017-18.json.gzip').write_bytes(compressed)
    (args.output/'sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'remuneration':source['totalRemuneration'],'expenses':source['totalExpenses'],'missingExpenses':source['validation']['missingExpenseRows'],'correctedPassesEqual':True,'subtotalReconciliation':'exact'},indent=2))


if __name__=='__main__':main()
