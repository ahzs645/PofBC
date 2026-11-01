#!/usr/bin/env python3
"""SD10 explicit salary-year qualified recovery; offline two-engine replay.

The source declaration conflict is preserved. OCR corrections are explicit and
image-verified, never balancing adjustments or inference from upload filenames.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import json
import os
import re
import subprocess
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT/'research/salaries/held-resolution-schools'
RESEARCH = ROOT/'research/salaries/held-resolution-2026-11-01/schools'
CACHE = Path('/tmp/held-resolution-schools')
PDF = CACHE/'sd10-district-sofi-2025.pdf'
ORIGINAL_SHA = '193808051072d321077d9f2dd0fc57af454ffccf8010a2690ad04b6fff1a767a'
MANUAL_SHA = '389af426c61df6549513cf626ff6dd9e8c626961e2b2a0a0cbc55a9c81e543a0'
SOURCE_URL = 'https://sd10.bc.ca/wp-content/uploads/2026/01/SD10-2024-2025-SOFI-sv-1.pdf'
INDEX_URL = 'https://sd10.bc.ca/board-of-education/financial-information-budgets/'
FIELDS = ['name','position','remuneration','expenses','pdfPage','category']
MONEY = re.compile(r'\$\s*\d[\d,]*\.\d{2}')
CONTROLS = {'school-trustees': ['69248.51','12525.55'],
            'employee-remuneration': ['6036402.68','89295.97']}
WARNING = ('The remuneration schedules on physical pages 47–48 explicitly state the fiscal year ended June 30, 2025; '
           'these observations are assigned to 2024/25 on that basis. The same package\'s declaration on page 3 certifies '
           'the year ended June 30, 2024 despite a 2024–2025 year field and signatures dated December 18, 2025. '
           'The management report on page 5 prints December 18, 2024 beneath a June 30, 2025 header. '
           'These contradictions remain unresolved; approval/adoption of the 2025 SOFI is not established by these pages. '
           'No cause or typo is inferred.')
PEER_REVIEW={'file':'research/salaries/held-resolution-2026-11-01/reviews/independent-sd10-comparison.json',
             'sha256':'e0d7aaf9f23b29c4f9db4fb414018f3c5cdb15192ca529b8a461500fa5fb7aab'}


def sha(data): return hashlib.sha256(data).hexdigest()


def clean(s): return re.sub(r'\s+', ' ', s).strip()


def amount(s):
    s = s.replace('$','').replace(',','').strip()
    if s in ['', '-', '–', '—']: return None
    return str(Decimal(s))


def packed(value):
    raw = json.dumps(value, ensure_ascii=False, separators=(',',':')).encode()
    return gzip.compress(raw, mtime=0), raw


def fields(rows): return [[r[k] for k in FIELDS] for r in rows]


def totals(rows):
    return [str(sum((Decimal(r[k]) for r in rows if r[k] is not None), Decimal(0)))
            for k in ['remuneration','expenses']]


def manual_rows():
    path = RESEARCH/'sd10-2025-manual.tsv'
    assert sha(path.read_bytes()) == MANUAL_SHA
    with path.open() as f:
        return [{'name':r['name'],'position':r['position'] or None,
                 'remuneration':amount(r['remuneration']),'expenses':amount(r['expenses']),
                 'pdfPage':int(r['pdfPage']),'category':r['category']}
                for r in csv.DictReader(f, delimiter='\t')]


def tesseract_rows(page_texts):
    """Reader one: lexical OCR lines and first explicit currency components."""
    rows = []
    for page,text in sorted(page_texts.items()):
        for line in text.splitlines():
            matches = list(MONEY.finditer(line))
            if len(matches) != 2: continue
            prefix = line[:matches[0].start()].rstrip()
            pos = re.search(r'(?:[‘\x27])?(?:TRUSTEES|TEACHERS|ADMIN|EXCLUDED|CUPE)\b', prefix)
            if not pos: continue
            rows.append({'name':clean(prefix[:pos.start()]),'position':clean(prefix[pos.start():]),
                         'remuneration':amount(matches[0].group()),'expenses':amount(matches[1].group()),
                         'pdfPage':int(page),'category':'school-trustees' if int(page)==47 else 'employee-remuneration',
                         'rawSourceLine':line})
    return rows


def rapid_rows(page_results):
    """Reader two: independently inferred Paddle boxes, geometric row/columns."""
    rows = []
    for page,results in sorted(page_results.items()):
        page = int(page)
        groups = []
        for box,text,confidence in sorted(results, key=lambda r:(sum(p[1] for p in r[0])/4,min(p[0] for p in r[0]))):
            y = sum(p[1] for p in box)/4
            if not ((320 < y < 460) if page==47 else (270 < y < 1312)): continue
            g = next((g for g in groups[-3:] if abs(g['y']-y)<5),None)
            if g is None:
                g={'y':y,'boxes':[]};groups.append(g)
            g['boxes'].append({'box':box,'text':text,'confidence':confidence})
        for group in groups:
            columns = [[] for _ in range(4)]
            boundaries = [450,755,930] if page==47 else [450,800,950]
            for box in sorted(group['boxes'],key=lambda b:min(p[0] for p in b['box'])):
                column = sum(min(p[0] for p in box['box'])>=bound for bound in boundaries)
                columns[column].append(box['text'])
            name,position,pay,expense = [clean(' '.join(c)) for c in columns]
            assert all([name,position,pay,expense]), (page,group)
            rows.append({'name':name,'position':position,'remuneration':amount(pay),'expenses':amount(expense),
                         'pdfPage':page,'category':'school-trustees' if page==47 else 'employee-remuneration',
                         'rawPaddleBoxes':group['boxes']})
    return rows


def correct_rows(rows, corrections, engine):
    out = [dict(r) for r in rows]
    for correction in [c for c in corrections if c['engine']==engine]:
        row = out[correction['sequence']-1]
        assert row['pdfPage']==correction['pdfPage']
        assert row[correction['field']]==correction['before'], correction
        assert correction['reviewMethod']=='complete original-image field review'
        row[correction['field']]=correction['after']
    return out


def render_original():
    import fitz
    assert sha(PDF.read_bytes())==ORIGINAL_SHA
    doc=fitz.open(PDF);images=[]
    for p in [47,48]:
        path=CACHE/f'sd10-district-sofi-2025-p{p}.png'
        doc[p-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(path)
        images.append({'pdfPage':p,'path':str(path),'sha256':sha(path.read_bytes()),'renderScale':2})
    return images


def machine_inputs(rerun_tesseract=False, rerun_rapid=False):
    images=render_original();texts={};rapid={}
    for image in images:
        page=image['pdfPage'];path=Path(image['path'])
        if rerun_tesseract or not path.with_suffix('.txt').exists():
            text=subprocess.check_output(['tesseract',str(path),'stdout','--psm','6'],stderr=subprocess.DEVNULL,
                                         env={**os.environ,'OMP_THREAD_LIMIT':'1'}).decode()
        else: text=path.with_suffix('.txt').read_text()
        texts[str(page)]=text
        rapid_path=path.with_suffix('.rapid.json')
        if rerun_rapid:
            code=('import json,sys;from rapidocr_onnxruntime import RapidOCR;'
                  'e=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1);'
                  'r,_=e(sys.argv[1]);print(json.dumps(r))')
            results=json.loads(subprocess.check_output(['/tmp/held-health-ocr/venv/bin/python','-c',code,str(path)]))
        elif rapid_path.exists():
            raw=json.loads(rapid_path.read_text());assert raw['imageSha256']==image['sha256'];results=raw['results']
        else:
            proof_path=COLLECTION/'sd10-2025-trustees-evidence.json.gzip'
            prior=json.loads(gzip.decompress(proof_path.read_bytes()))
            assert prior['sourceSha256']==ORIGINAL_SHA
            assert next(r['sha256'] for r in prior['renderedPages'] if r['pdfPage']==page)==image['sha256']
            results=prior['rawRapidPageResults'][str(page)]
        rapid[str(page)]=results
    return images,texts,rapid


def normalized(source, rows):
    return [[source['employerSlug'],r['name'],r['position'],float(r['remuneration']),
             None if r['expenses'] is None else float(r['expenses']),r['pdfPage']] for r in rows]


def build():
    images,texts,rapid=machine_inputs()
    manual=manual_rows();corrections=json.loads((RESEARCH/'sd10-2025-ocr-corrections.json').read_text())
    first=correct_rows(tesseract_rows(texts),corrections,'Tesseract')
    second=correct_rows(rapid_rows(rapid),corrections,'RapidOCR')
    assert fields(manual)==fields(first)==fields(second)
    assert len(manual)==58
    sources=[]
    context_bytes=(RESEARCH/'sd10-period-and-approval-evidence.json').read_bytes()
    context=json.loads(context_bytes)
    for category in ['school-trustees','employee-remuneration']:
        suffix='trustees' if category=='school-trustees' else 'employees';key=f'sd10-2025-{suffix}'
        rows=[r for r in manual if r['category']==category]
        proof={'version':1,'sourceSha256':ORIGINAL_SHA,'manualTranscriptSha256':MANUAL_SHA,
               'rows':rows,'tesseractRows':[r for r in first if r['category']==category],
               'rapidRows':[r for r in second if r['category']==category],
               'rawTesseractPageTexts':texts,'rawRapidPageResults':rapid,
               'explicitImageVerifiedCorrections':corrections,'renderedPages':images,
               'printedControlTotals':CONTROLS[category],'periodAndApprovalEvidence':context,
               'periodAndApprovalEvidenceSha256':sha(context_bytes)}
        data,raw=packed(normalized({'employerSlug':'school-district-10'},rows));evidence,_=packed(proof)
        (COLLECTION/f'{key}.json.gzip').write_bytes(data)
        (COLLECTION/f'{key}-evidence.json.gzip').write_bytes(evidence)
        computed=totals(rows);assert computed==CONTROLS[category]
        source={'id':f'held-resolution-schools-{key}','employerSlug':'school-district-10',
                'employerName':'School District No. 10 (Arrow Lakes)','sector':'School districts',
                'year':'2024/25','slug':'2024-25','periodType':'fiscal','periodStart':'2024-07-01','periodEnd':'2025-06-30',
                'title':f'School District No. 10 (Arrow Lakes), salary schedule year ended June 30, 2025: {suffix}',
                'sourceUrl':SOURCE_URL,'sourceIndexUrl':INDEX_URL,'sha256':ORIGINAL_SHA,
                'file':f'{key}.json.gzip','dataSha256':sha(data),'normalizedSha256':sha(raw),
                'provenanceFile':f'{key}-evidence.json.gzip','provenanceSha256':sha(evidence),
                'category':category,'scope':category,'currency':'CAD','amountUnit':'dollars','amountPrecision':'cents',
                'scopeDescription':'Complete published elected trustee table' if suffix=='trustees' else 'Complete published employee remuneration table over $75,000; below-threshold aggregates excluded',
                'nameDisclosure':'published-name-as-disclosed','positionDisclosure':'published-visible-text-only',
                'pages':sorted({r['pdfPage'] for r in rows}),'rowCount':len(rows),
                'totalRemuneration':float(computed[0]),'totalExpenses':float(computed[1]),
                'status':'verified','sourceKind':'official','verifiedOn':'2026-11-01','publicWarning':WARNING,
                'notes':[
                    'The salary tables explicitly print fiscal year ended June 30, 2025. The observation period uses those table headings; conflicting declaration/management signoff years remain literal and do not establish 2025 approval.',
                    'The original says remuneration/expense schedules are on a cash basis while financial-statement salaries and benefits use accrual accounting. These are reported payments, not annual base salary rates; remuneration and expenses remain separate.',
                    'Published names, initials, punctuation and visibly clipped position fragments are preserved. No invisible completion or inferred full title is added. Explicit expense zero remains zero; blank/dash values would remain null.',
                    'Only named employee or trustee payments are imported. Under-threshold aggregates, CPP/EI employer premiums, suppliers and financial-statement totals are excluded.',
                    'Complete original-image transcription is compared with independent Tesseract LSTM and Paddle PP-OCR neural engines. Every disagreement is retained as an explicit image-verified correction; raw OCR text, boxes and confidence remain in evidence.',
                    'The district-hosted original and Ministry copy have pixel-identical salary pages. Actual 2024 salary rows/amounts are distinct. Neither comparison is treated as proof that the conflicting declaration is a typo.',
                ],
                'validation':{'originalFingerprintVerified':True,'independentReaders':['Tesseract 5.5.0 PSM6','RapidOCR 1.4.4 Paddle PP-OCR ONNX'],
                              'completeOriginalImageTranscript':True,'rowsIndependentlyChecked':len(rows),
                              'completeRowTextAmountsOrderAndMultiplicityAgreeAfterExplicitImageCorrections':True,
                              'rowsByPhysicalPage':dict(collections.Counter(str(r['pdfPage']) for r in rows)),
                              'printedControlTotals':CONTROLS[category],'computedComponentTotals':computed,'controlResiduals':['0.00','0.00'],
                              'summaryReconciles':True,'allPublishedNamedControlsExact':True,'allPrintedComponentControlsExact':True,
                              'knownExpenseValueCount':sum(r['expenses'] is not None for r in rows),
                              'reportingPeriodBasis':'Explicit remuneration schedule headings on physical pages47–48, with qualified conflicting approval documents',
                              'salarySchedulePrintedPeriodEnd':'2025-06-30','conflictingDeclarationPeriodEnd':'2024-06-30',
                              'approvalFor2025Established':False,'declarationSignatureDatesPrinted':'2025-12-18','managementReportSignoffDatesPrinted':'2024-12-18',
                              'periodEvidenceFile':'research/salaries/held-resolution-2026-11-01/schools/sd10-period-and-approval-evidence.json',
                              'periodEvidenceSha256':sha(context_bytes),'completeIndependentPeerImageReviewPending':False,
                              'independentOriginalImagePeerReview':PEER_REVIEW}}
        if category=='employee-remuneration':source['completeEmployeeSchedule']=True;source['validation']['completeEmployeeSchedule']=True
        sources.append(source)
    (COLLECTION/'sources.json').write_text(json.dumps({'version':1,'reviewed':'2026-11-01',
        'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources},ensure_ascii=False,indent=2)+'\n')


def verify_source(source, proof):
    assert proof['sourceSha256']==source['sha256']==ORIGINAL_SHA
    assert proof['manualTranscriptSha256']==MANUAL_SHA
    assert fields(proof['rows'])==fields(proof['tesseractRows'])==fields(proof['rapidRows'])
    assert totals(proof['rows'])==proof['printedControlTotals']==source['validation']['computedComponentTotals']
    assert len(proof['rows'])==source['rowCount']
    assert source['publicWarning']==WARNING
    assert not source['validation']['approvalFor2025Established']
    assert [r for r in manual_rows() if r['category']==source['category']]==proof['rows']
    corrections=proof['explicitImageVerifiedCorrections']
    first=correct_rows(tesseract_rows(proof['rawTesseractPageTexts']),corrections,'Tesseract')
    second=correct_rows(rapid_rows(proof['rawRapidPageResults']),corrections,'RapidOCR')
    assert fields([r for r in first if r['category']==source['category']])==fields(proof['rows'])
    assert fields([r for r in second if r['category']==source['category']])==fields(proof['rows'])
    context=(RESEARCH/'sd10-period-and-approval-evidence.json').read_bytes()
    assert sha(context)==proof['periodAndApprovalEvidenceSha256']==source['validation']['periodEvidenceSha256']
    data,raw=packed(normalized(source,proof['rows']))
    assert sha(data)==source['dataSha256'] and sha(raw)==source['normalizedSha256']
    assert data==(COLLECTION/source['file']).read_bytes()
    review=(ROOT/PEER_REVIEW['file']).read_bytes();assert sha(review)==PEER_REVIEW['sha256']
    peer=json.loads(review);assert peer['original']['sha256']==source['sha256']
    assert peer['candidateTranscript']['sha256']==MANUAL_SHA
    checked=next(r for r in peer['normalizedComparisons'] if r['sourceId']==source['id'])
    assert checked['dataSha256']==source['dataSha256'] and checked['allSixFieldsExact']
    assert checked['rowsCompared']==source['rowCount']


def main():
    p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');p.add_argument('--originals',action='store_true')
    p.add_argument('--rerun-rapid',action='store_true');args=p.parse_args()
    if args.build:build()
    sources=json.loads((COLLECTION/'sources.json').read_text())['sources']
    replay=None
    for source in sources:
        data=(COLLECTION/source['provenanceFile']).read_bytes();assert sha(data)==source['provenanceSha256']
        proof=json.loads(gzip.decompress(data))
        if source['id']=='held-resolution-schools-sd08-2026-employees':
            import resolve_held_schools_sd08 as native
            native.verify_source(source,proof,args.originals)
            continue
        verify_source(source,proof)
        if args.originals:
            if replay is None:replay=machine_inputs(True,args.rerun_rapid)
            images,texts,rapid=replay;assert images==proof['renderedPages']
            corrections=proof['explicitImageVerifiedCorrections']
            assert fields(correct_rows(tesseract_rows(texts),corrections,'Tesseract'))==fields(manual_rows())
            assert fields(correct_rows(rapid_rows(rapid),corrections,'RapidOCR'))==fields(manual_rows())
    print(f'Verified {len(sources)} qualified school cohorts / {sum(s["rowCount"] for s in sources)} rows'+(' against original OCR inputs' if args.originals else ' by offline evidence replay'))


if __name__=='__main__':main()
