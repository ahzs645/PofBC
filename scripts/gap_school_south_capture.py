#!/usr/bin/env python3
"""Preserve two independently implemented OCR outputs from full PDF renders."""
import argparse,gzip,hashlib,json,os,subprocess,time
from pathlib import Path
from gap_school_south_fetch import AREA,CACHE

def sha(raw):return hashlib.sha256(raw).hexdigest()

def capture(plan):
    for name in ['OMP_THREAD_LIMIT','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        os.environ[name]='1'
    import fitz
    from rapidocr_onnxruntime import RapidOCR
    engine=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1,max_side_len=4096)
    dest=AREA/'raw-ocr';dest.mkdir(exist_ok=True)
    specs={x['key']:x for x in json.loads((AREA/'retrievals.json').read_text())}
    docs={}
    for item in plan:
        key,page_number=item['key'],item['physicalPage'];output=dest/(key+f'-p{page_number}.json.gzip')
        if output.exists():
            saved=json.loads(gzip.decompress(output.read_bytes()))
            assert saved['sourceSha256']==specs[key]['sha256'] and saved['physicalPage']==page_number
            print(key,page_number,'existing',flush=True);continue
        if key not in docs:
            assert sha((CACHE/(key+'.pdf')).read_bytes())==specs[key]['sha256']
            docs[key]=fitz.open(CACHE/(key+'.pdf'))
        page=docs[key][page_number-1]
        image=CACHE/(key+f'-capture-p{page_number}-300dpi.png')
        pix=page.get_pixmap(dpi=300);pix.save(image)
        started=time.monotonic()
        tsv=subprocess.check_output(['tesseract',str(image),'stdout','--psm','6','tsv'],stderr=subprocess.DEVNULL).decode()
        paddle,elapsed=engine(str(image))
        result={'key':key,'physicalPage':page_number,'sourceSha256':specs[key]['sha256'],
                'imageSha256':sha(image.read_bytes()),'pageWidthPoints':page.rect.width,'pageHeightPoints':page.rect.height,
                'imageWidth':pix.width,'imageHeight':pix.height,'dpi':300,
                'renderMethod':'Unclipped complete original PDF page.get_pixmap(dpi=300); no image alteration',
                'readers':['Tesseract 5.5.0 PSM6 TSV','RapidOCR Paddle PP-OCR ONNX'],
                'tesseractRawTsv':tsv,'rapidOcrRaw':paddle,'rapidOcrElapsedSeconds':elapsed,
                'threadCaps':1,'acceptedRows':0}
        output.write_bytes(gzip.compress((json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
        image.unlink()
        print(key,page_number,'captured',round(time.monotonic()-started,2),'seconds',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);args=ap.parse_args()
    capture(json.loads(args.plan.read_text()))
