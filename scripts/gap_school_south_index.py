#!/usr/bin/env python3
"""Locate schedules in scanned school originals; index OCR is not salary data."""
import argparse,concurrent.futures,gzip,hashlib,json,os,subprocess
from pathlib import Path
from gap_school_south_fetch import AREA,CACHE

def page_ocr(task):
    import fitz
    key,page_number=task
    doc=fitz.open(CACHE/(key+'.pdf'));page=doc[page_number-1]
    image=CACHE/(key+f'-index-p{page_number}.png')
    page.get_pixmap(dpi=150).save(image)
    env={**os.environ,'OMP_THREAD_LIMIT':'1','OMP_NUM_THREADS':'1'}
    txt=subprocess.check_output(['tesseract',str(image),'stdout','--psm','6'],env=env,stderr=subprocess.DEVNULL).decode()
    out={'key':key,'physicalPage':page_number,'dpi':150,'purpose':'source-discovery-index-only','tesseractText':txt,'imageSha256':hashlib.sha256(image.read_bytes()).hexdigest()}
    dest=AREA/'index-ocr';dest.mkdir(exist_ok=True)
    (dest/(key+f'-p{page_number}.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    image.unlink()
    print(key,page_number,'indexed',flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path);args=ap.parse_args()
    specs=json.loads((AREA/'retrievals.json').read_text())
    tasks=json.loads(args.plan.read_text()) if args.plan else [(s['key'],p) for s in specs for p in range(1,min(8,s['pageCount'])+1)]
    # PyMuPDF rendering is process-sequential; earlier threaded discovery files
    # are only search hints and never supply accepted salary transcriptions.
    for task in tasks:page_ocr(task)
