#!/usr/bin/env python3
"""Run the complete nine-source queue with frozen source-specific OCR profiles."""
import os
for key in ['OMP_THREAD_LIMIT','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse
import concurrent.futures
import fcntl
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
CACHE=Path('/tmp/queue-completion-phsa')
SOURCES=PROFILES=None
DOC=DOC_KEY=None
ENGINES={}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def initialize():
    global SOURCES,PROFILES
    import cv2
    cv2.setNumThreads(1)
    SOURCES={s['id']:s for s in json.loads((AREA/'source-inventory.json').read_text())['sources']}
    PROFILES={}
    for pin in json.loads((AREA/'processing-profile-index-001.json').read_text())['sourceProfiles']:
        path=ROOT/pin['path']
        if sha(path.read_bytes())!=pin['sha256']:raise ValueError('Frozen per-source processing profile changed')
        PROFILES[pin['sourceId']]=(json.loads(path.read_text()),pin)


def capture(task):
    global DOC,DOC_KEY
    import fitz
    from rapidocr_onnxruntime import RapidOCR
    key,pn=task;source=SOURCES[key];profile,profile_pin=PROFILES[key];config=profile['chosenRapidConfiguration']
    outpath=CACHE/key/'raw-selected'/f'p{pn:03d}.json.gzip'
    if outpath.exists():return {'source':key,'page':pn,'cached':True}
    started=time.perf_counter();baseline_path=CACHE/key/'raw'/f'p{pn:03d}.json.gzip'
    if baseline_path.exists():
        raw=json.loads(gzip.decompress(baseline_path.read_bytes()))
        if raw['sourceSha256']!=source['sourceSha256']:raise ValueError('Baseline source identity changed')
        image_path=Path(raw['sourceImagePath'])
        if sha(image_path.read_bytes())!=raw['sourceImageSha256']:raise ValueError('Actual rendered baseline changed')
    else:
        if DOC_KEY!=key:
            if DOC is not None:DOC.close()
            pdf=Path(source['cachePath'])
            if sha(pdf.read_bytes())!=source['sourceSha256']:raise ValueError('Official original changed')
            DOC=fitz.open(pdf);DOC_KEY=key
        page=DOC[pn-1]
        if page.get_text().strip():raise ValueError('Unexpected native source overlay')
        pix=page.get_pixmap(dpi=300,alpha=False)
        image_path=CACHE/key/'images'/f'p{pn:03d}.png';image_path.parent.mkdir(parents=True,exist_ok=True);pix.save(image_path)
        prefix=CACHE/key/'tesseract-selected'/f'p{pn:03d}';prefix.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['tesseract',str(image_path),str(prefix),'-l','eng','--psm','6',
                        '--tessdata-dir','/usr/share/tesseract-ocr/5/tessdata',
                        '-c','tessedit_create_txt=1','-c','tessedit_create_tsv=1'],
                       check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        raw={'version':2,'sourceId':key,'sourceSha256':source['sourceSha256'],'yearFromInventory':source['year'],
             'physicalPage':pn,'physicalPdfPages':source['pdfPages'],
             'renderer':{'engine':'PyMuPDF','version':fitz.VersionBind,'invocation':'page.get_pixmap(dpi=300,alpha=False)',
                         'actualPdfPaintedRendering':True,'dpi':300,'imageDimensions':[pix.width,pix.height]},
             'sourceImagePath':str(image_path),'sourceImageSha256':sha(image_path.read_bytes()),
             'tesseractRawText':prefix.with_suffix('.txt').read_text(),'tesseractRawTsv':prefix.with_suffix('.tsv').read_text()}
    trial=CACHE/key/(config+'.json')
    if config=='baseline-default' and baseline_path.exists():pass
    elif pn==profile['firstSalaryPhysicalPage'] and trial.exists():
        alt=json.loads(trial.read_text())
        if alt['sourceImageSha256']!=raw['sourceImageSha256']:raise ValueError('Benchmark source raster differs')
        raw['rapidocrRaw']=alt['rapidocrRaw'];raw['rapidocrElapsed']=alt['elapsed']
    else:
        if config not in ENGINES:
            args={'intra_op_num_threads':1,'inter_op_num_threads':1}
            if config!='baseline-default':args['max_side_len']=4096
            if config=='english-4096':
                args.update(rec_model_path='/tmp/held-health-ocr/english-models/en_PP-OCRv4_rec_mobile.onnx',
                            rec_keys_path='/tmp/held-health-ocr/english-models/en_dict.txt')
            ENGINES[config]=RapidOCR(**args)
        raw['rapidocrRaw'],raw['rapidocrElapsed']=ENGINES[config](str(image_path))
        if raw['rapidocrRaw'] is None:raise ValueError('Independent neural reader returned no text')
    raw['sourceSpecificProfile']=profile_pin
    raw['selectedRapidConfiguration']=config
    raw['selectedTesseractConfiguration']=profile['chosenTesseractConfiguration']
    raw['captureScriptSha256']=sha(Path(__file__).read_bytes())
    raw['captureWallSeconds']=time.perf_counter()-started
    if baseline_path.exists():raw['originalBaselineEvidence']={'cachePath':str(baseline_path),'sha256':sha(baseline_path.read_bytes())}
    outpath.parent.mkdir(parents=True,exist_ok=True)
    outpath.write_bytes(gzip.compress(json.dumps(raw,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    return {'source':key,'page':pn,'cached':False,'seconds':round(raw['captureWallSeconds'],2),'configuration':config}


def run(workers=3):
    if workers not in [1,2,3]:raise ValueError('Only allocated machine OCR slots may be used')
    lock=(CACHE/'phsa-ocr-pool.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    initialize();jobs=[(s['id'],pn) for s in SOURCES.values() for pn in range(1,s['pdfPages']+1)
                       if not (CACHE/s['id']/'raw-selected'/f'p{pn:03d}.json.gzip').exists()]
    print(json.dumps({'queuedPages':len(jobs),'workers':workers,'sourceCount':len(SOURCES)}),flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,initializer=initialize) as pool:
        for i,result in enumerate(pool.map(capture,jobs,chunksize=1),1):
            print(json.dumps({'completedThisRun':i,'queuedThisRun':len(jobs),**result}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=3);run(p.parse_args().workers)
