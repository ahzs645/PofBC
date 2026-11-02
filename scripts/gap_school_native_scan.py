#!/usr/bin/env python3
"""Capture two independent OCR engines for image-only SD53 and SD84 schedules."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_native'
CACHE=Path('/workspace/gap-school-native-cache')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    for key in ['OMP_THREAD_LIMIT','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        os.environ[key]='1'
    import fitz
    from rapidocr_onnxruntime import RapidOCR
    engine=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1,max_side_len=4096)
    plan={53:[7,8,9,10,11,12],84:[54,56]}
    (AREA/'images').mkdir(exist_ok=True)
    for district,pages in plan.items():
        receipt=json.loads((AREA/f'sd{district}-2025-district-http.json').read_bytes())
        path=Path(receipt['cachePath']);assert sha(path.read_bytes())==receipt['sha256']
        doc=fitz.open(path)
        for number in pages:
            destination=AREA/f'sd{district}-p{number}-dual-ocr.json.gzip'
            if destination.exists():
                print('existing',district,number,flush=True);continue
            page=doc[number-1]
            image_path=AREA/'images'/f'sd{district}-p{number}-300dpi.png'
            page.get_pixmap(dpi=300).save(image_path)
            tsv=subprocess.check_output(['tesseract',str(image_path),'stdout','--psm','6','tsv'],stderr=subprocess.DEVNULL).decode()
            text=subprocess.check_output(['tesseract',str(image_path),'stdout','--psm','6'],stderr=subprocess.DEVNULL).decode()
            boxes,elapsed=engine(str(image_path))
            result={'districtNumber':district,'sourceUrl':receipt['url'],'sourceSha256':receipt['sha256'],
                    'physicalPage':number,'pageRect':list(page.rect),'dpi':300,'renderMethod':'PyMuPDF entire physical page at300dpi; no PDF clip or resampling',
                    'imagePath':str(image_path.relative_to(ROOT)),'imageSha256':sha(image_path.read_bytes()),
                    'readerNames':['Tesseract5.5 PSM6 native TSV','RapidOCR1.4.4 Paddle PP-OCR ONNX'],
                    'tesseractRawTsv':tsv,'tesseractRawText':text,'rapidOcrRawBoxes':boxes,'rapidOcrElapsed':elapsed,
                    'threadCaps':1,'acceptedRows':0}
            destination.write_bytes(gzip.compress((json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
            print('captured',district,number,sha(destination.read_bytes()),flush=True)


if __name__=='__main__':main()
