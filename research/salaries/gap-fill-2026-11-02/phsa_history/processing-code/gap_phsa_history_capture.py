#!/usr/bin/env python3
"""Two independent OCR readers of every original PHSA history body page."""
import os
for key in ['OMP_THREAD_LIMIT','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import argparse,concurrent.futures,gzip,hashlib,json,subprocess,time
from pathlib import Path
from gap_phsa_history_fetch import AREA,CACHE,ROOT
SOURCES={};DOCS={};ENGINE=None
ENMODEL=Path('/tmp/held-health-ocr/english-models/en_PP-OCRv4_rec_mobile.onnx')
ENDICT=Path('/tmp/held-health-ocr/english-models/en_dict.txt')

def sha(b):return hashlib.sha256(b).hexdigest()
def initialize():
 global SOURCES,ENGINE
 from rapidocr_onnxruntime import RapidOCR
 SOURCES={s['key']:s for s in json.loads((AREA/'source-inventory.json').read_text())['sources']}
 ENGINE=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1,max_side_len=4096,rec_model_path=str(ENMODEL),rec_keys_path=str(ENDICT))

def capture(task):
 import fitz
 key,pn=task;source=SOURCES[key];out=AREA/'raw-ocr'/f'{key}-p{pn:03d}.json.gzip';out.parent.mkdir(exist_ok=True)
 if out.exists():
  d=json.loads(gzip.decompress(out.read_bytes()));assert d['sourceSha256']==source['sourceSha256'];return {'key':key,'page':pn,'cached':True}
 if key not in DOCS:
  path=Path(source['cachePath']);assert sha(path.read_bytes())==source['sourceSha256'];DOCS[key]=fitz.open(path)
 page=DOCS[key][pn-1];pix=page.get_pixmap(dpi=300,alpha=False);images=CACHE/'images';images.mkdir(exist_ok=True);image=images/f'{key}-p{pn:03d}.png';pix.save(image);start=time.monotonic();tsv=subprocess.check_output(['tesseract',str(image),'stdout','-l','eng','--psm','6','tsv'],stderr=subprocess.DEVNULL).decode();raw,elapsed=ENGINE(str(image));raw=[] if raw is None else raw
 d={'key':key,'physicalPage':pn,'sourceSha256':source['sourceSha256'],'sourceImageSha256':sha(image.read_bytes()),'sourceImageCachePath':str(image),'renderer':'Sequential within each isolated worker process: whole original page.get_pixmap(dpi=300,alpha=False). No crop/alteration.','imageWidth':pix.width,'imageHeight':pix.height,'dpi':300,'threadCaps':1,'readers':['Tesseract5.5.0 English PSM6 TSV','RapidOCR/Paddle PP-OCRv4 English4096 ONNX independent boxes'],'modelProfile':{'recognizerSha256':sha(ENMODEL.read_bytes()),'dictionarySha256':sha(ENDICT.read_bytes()),'maxSideLength':4096},'tesseractRawTsv':tsv,'rapidOcrRaw':raw,'rapidOcrElapsedSeconds':elapsed,'acceptedRows':0};out.write_bytes(gzip.compress((json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0));return {'key':key,'page':pn,'seconds':round(time.monotonic()-start,2),'cached':False}

def run(workers):
 sources=json.loads((AREA/'source-inventory.json').read_text())['sources'];scan=[s for s in sources if s['imageOnlyPages']];jobs=[(s['key'],p) for s in sorted(scan,key=lambda s:s['key']) for p in range(2,s['pageCount']+1)];plan={'sources':[s['key'] for s in scan],'jobs':[{'key':k,'physicalPage':p} for k,p in jobs],'excludedPhysicalPages':[{'key':s['key'],'physicalPage':1,'reason':'Added official Library catalogue cover, not original remuneration source body.'} for s in scan],'ocrProfile':'English4096 ONNX +Tesseract EnglishPSM6 on whole original300dpi page; scores are prioritization signals, not accuracy probabilities.','noOutreach':True};(AREA/'full-scan-capture-plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'queuedBodyPages':len(jobs),'workers':workers,'threadCaps':1}),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=workers,initializer=initialize) as pool:
  for i,result in enumerate(pool.map(capture,jobs,chunksize=1),1):print(json.dumps({'completed':i,'planned':len(jobs),**result}),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,choices=[1,2],default=2);a=p.parse_args();run(a.workers)
