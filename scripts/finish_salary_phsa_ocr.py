#!/usr/bin/env python3
"""Immutable independent raw OCR of actual PDF-painted historical PHSA pages.

All interpretation, source-specific geometry and image-review overlays are later
steps. This acquisition never emits accepted salary rows or invents a dash.
"""
import os
for _key in ['OMP_THREAD_LIMIT','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:
    os.environ[_key]='1'
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
DOC=ENGINE=SOURCE=None


def sha(raw):return hashlib.sha256(raw).hexdigest()


def encode(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()


def initialize():
    global ENGINE
    import cv2
    from rapidocr_onnxruntime import RapidOCR
    cv2.setNumThreads(1)
    ENGINE=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1)


def page_job(task):
    global DOC,SOURCE
    import fitz
    source,pn=task;key=source['id']
    folder=CACHE/key;rawpath=folder/'raw'/f'p{pn:03d}.json.gzip'
    if rawpath.exists():
        old=json.loads(gzip.decompress(rawpath.read_bytes()))
        if old['sourceSha256']!=source['sourceSha256'] or old['physicalPage']!=pn:
            raise ValueError('Cached original identity changed')
        return {'source':key,'page':pn,'cached':True,'seconds':0}
    started=time.perf_counter()
    if SOURCE!=key:
        if DOC is not None:DOC.close()
        pdf=Path(source['cachePath'])
        if sha(pdf.read_bytes())!=source['sourceSha256']:raise ValueError('Original source hash changed')
        DOC=fitz.open(pdf);SOURCE=key
    page=DOC[pn-1]
    if page.get_text().strip():raise ValueError('Unexpected native-text source; inspect original reader scope')
    pix=page.get_pixmap(dpi=300,alpha=False)
    imagepath=folder/'images'/f'p{pn:03d}.png';imagepath.parent.mkdir(parents=True,exist_ok=True)
    pix.save(imagepath)
    prefix=folder/'tesseract'/f'p{pn:03d}';prefix.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['tesseract',str(imagepath),str(prefix),'-l','eng','--psm','6','txt','tsv'],
                   check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    rapid,elapsed=ENGINE(str(imagepath))
    if rapid is None:raise ValueError('No independent RapidOCR output')
    out={'version':1,'sourceId':key,'sourceSha256':source['sourceSha256'],'yearFromInventory':source['year'],
         'physicalPage':pn,'physicalPdfPages':source['pdfPages'],
         'renderer':{'engine':'PyMuPDF','version':fitz.VersionBind,'invocation':'page.get_pixmap(dpi=300,alpha=False)',
                     'actualPdfPaintedRendering':True,'dpi':300,'imageDimensions':[pix.width,pix.height]},
         'sourceImagePath':str(imagepath),'sourceImageSha256':sha(imagepath.read_bytes()),
         'tesseractRawText':prefix.with_suffix('.txt').read_text(),'tesseractRawTsv':prefix.with_suffix('.tsv').read_text(),
         'rapidocrRaw':rapid,'rapidocrElapsed':elapsed,'wallSeconds':time.perf_counter()-started,
         'acquisitionScriptSha256':sha(Path(__file__).read_bytes()),
         'interpretation':'Raw independent engines only. No presumed fiscal year, row count, dash template, threshold or source controls is accepted from the file label.'}
    rawpath.parent.mkdir(parents=True,exist_ok=True)
    rawpath.write_bytes(gzip.compress(encode(out),mtime=0))
    return {'source':key,'page':pn,'cached':False,'seconds':round(out['wallSeconds'],2)}


def sources():
    selected=[]
    for p in sorted(AREA.glob('phsa-*-inventory.json')):
        e=json.loads(p.read_text())
        selected.append(e)
    return selected


def run(workers=2,benchmark=False,only=None):
    if workers not in [1,2,3]:raise ValueError('Machine maximum is three allocated OCR workers')
    CACHE.mkdir(parents=True,exist_ok=True)
    lock=(CACHE/'phsa-ocr-pool.lock').open('a+')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    selected=[s for s in sources() if only is None or s['id'] in only]
    if not selected:raise ValueError('No hash-verified source inventory')
    jobs=[]
    for s in selected:
        page_numbers=sorted({1,2,s['pdfPages']//2,s['pdfPages']}) if benchmark else range(1,s['pdfPages']+1)
        for pn in page_numbers:
            if not (CACHE/s['id']/'raw'/f'p{pn:03d}.json.gzip').exists():jobs.append((s,pn))
    print(json.dumps({'queuedPages':len(jobs),'workers':workers,'benchmark':benchmark,
                      'sourceIds':[s['id'] for s in selected]}),flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,initializer=initialize) as pool:
        for i,result in enumerate(pool.map(page_job,jobs,chunksize=1),1):
            print(json.dumps({'completedThisRun':i,'queuedThisRun':len(jobs),**result}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=2)
    p.add_argument('--benchmark',action='store_true');p.add_argument('--source',action='append')
    a=p.parse_args();run(a.workers,a.benchmark,a.source)
