#!/usr/bin/env python3
"""Preserve bounded recognition trials against blind full-page image fixtures."""
import os
for key in ['OMP_THREAD_LIMIT','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import concurrent.futures
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import time
import finish_salary_phsa_rows as readers

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
REVIEWS=ROOT/'research/salaries/queue-completion-2026-11-01/reviews'
CACHE=Path('/tmp/queue-completion-phsa')
ENGINES={}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def benchmark(task):
    import cv2
    from rapidocr_onnxruntime import RapidOCR
    cv2.setNumThreads(1)
    source,config=task;key=source['id'];year=source['year'].replace('/','-')
    fixture_path=REVIEWS/f'independent-phsa-history-batches-benchmark-{year}-original-transcript.tsv'
    fixture=list(csv.DictReader(fixture_path.open(),delimiter='\t'));pn=int(fixture[0]['physicalPage'])
    rp=CACHE/key/'raw'/f'p{pn:03d}.json.gzip';raw=json.loads(gzip.decompress(rp.read_bytes()))
    profile=readers.source_profile(raw,fixture)
    path=CACHE/key/(config+'.json')
    if config=='baseline-default':results=raw['rapidocrRaw'];elapsed=raw['rapidocrElapsed']
    elif path.exists():e=json.loads(path.read_text());results=e['rapidocrRaw'];elapsed=e['elapsed']
    else:
        if config not in ENGINES:
            args={'intra_op_num_threads':1,'inter_op_num_threads':1,'max_side_len':4096}
            if config=='english-4096':
                args.update(rec_model_path='/tmp/held-health-ocr/english-models/en_PP-OCRv4_rec_mobile.onnx',
                            rec_keys_path='/tmp/held-health-ocr/english-models/en_dict.txt')
            ENGINES[config]=RapidOCR(**args)
        results,elapsed=ENGINES[config](raw['sourceImagePath'])
        path.write_text(json.dumps({'sourceSha256':source['sourceSha256'],'sourceImageSha256':raw['sourceImageSha256'],
                                    'configuration':config,'rapidocrRaw':results,'elapsed':elapsed},ensure_ascii=False)+'\n')
    parsed,_,issues=readers.read_rapid(raw,profile,results)
    tess,_,tissues=readers.read_tesseract(raw,profile)
    comparison=[]
    for i,f in enumerate(fixture):
        r=parsed[i] if i<len(parsed) else None;t=tess[i] if i<len(tess) else None
        comparison.append({'sourceRowOnPage':i+1,'literalFixtureName':f['name'],
                           'rapidName':r['name'] if r else None,'tesseractName':t['name'] if t else None,
                           'rapidNameMatch':bool(r) and readers.name_comparison(r['name'])==readers.name_comparison(f['name']),
                           'tesseractNameMatch':bool(t) and readers.name_comparison(t['name'])==readers.name_comparison(f['name']),
                           'rapidPayMatch':bool(r) and r['pay']['value']==readers.money(f['remunerationLiteral'])['value'],
                           'rapidNumericExpenseMatch':f['expensesLiteral']!='-' and bool(r) and r['expense']['value']==readers.money(f['expensesLiteral'])['value'],
                           'rapidNameConfidence':r['nameConfidence'] if r else None})
    return {'sourceId':key,'configuration':config,'fixtureSha256':sha(fixture_path.read_bytes()),
            'sourceProfile':profile,'fixtureRows':len(fixture),'rapidRows':len(parsed),'tesseractRows':len(tess),
            'rapidNameMatches':sum(r['rapidNameMatch'] for r in comparison),
            'tesseractNameMatches':sum(r['tesseractNameMatch'] for r in comparison),
            'rapidPayMatches':sum(r['rapidPayMatch'] for r in comparison),
            'rapidNumericExpenseMatches':sum(r['rapidNumericExpenseMatch'] for r in comparison),
            'numericExpenseFixtureRows':sum(f['expensesLiteral']!='-' for f in fixture),
            'readerIssues':issues+tissues,'perRowComparison':comparison,'elapsed':elapsed}


def run(output='first-table-ocr-benchmark-trials.json'):
    sources=json.loads((AREA/'source-inventory.json').read_text())['sources']
    tasks=[(s,config) for config in ['baseline-default','chinese-4096','english-4096'] for s in sources]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        results=[]
        for result in pool.map(benchmark,tasks,chunksize=1):
            results.append(result)
            print(json.dumps({k:result[k] for k in ['sourceId','configuration','fixtureRows','rapidRows','rapidNameMatches','tesseractNameMatches','rapidPayMatches','rapidNumericExpenseMatches','numericExpenseFixtureRows']}),flush=True)
    out=AREA/output
    if out.exists():raise ValueError('Benchmark output frozen; use a new trial receipt')
    out.write_text(json.dumps({'results':results,'purpose':'Per-source quality calibration against all independently image-transcribed literal fields; no uncertain source value automatically accepted.'},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='first-table-ocr-benchmark-trials.json')
    run(p.parse_args().out)
