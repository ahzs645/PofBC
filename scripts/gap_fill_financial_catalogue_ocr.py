#!/usr/bin/env python3
"""Actual sparse-page OCR for scope assessment; never a salary-data acceptance parser."""
from pathlib import Path
import json,gzip,hashlib,subprocess,concurrent.futures,os
R=Path('/workspace/PofBC');A=R/'research/salaries/gap-fill-2026-11-02/reviews/financial-catalogue-audit';CACHE=Path('/workspace/gap-financial-catalogue-cache');sha=lambda b:hashlib.sha256(b).hexdigest()
def page_ocr(task):
 import fitz
 uid,pdf,num=task;d=fitz.open(pdf);pix=d[num-1].get_pixmap(dpi=150,alpha=False);png=pix.tobytes('png');im=CACHE/f'{uid}-p{num}-150dpi.png';im.write_bytes(png);env={**os.environ,'OMP_THREAD_LIMIT':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'};proc=subprocess.run(['tesseract',str(im),'stdout','--psm','3','-l','eng'],capture_output=True,env=env,check=True);data={'itemUuid':uid,'physicalPage':num,'method':'Actual pinned original PDF page rendered150dpi; Tesseract5.5 PSM3 full-page text for scope review only. OCR is not a salary extraction or acceptance guarantee.','pngSha256':sha(png),'pngCachePath':str(im),'text':proc.stdout.decode('utf-8','replace'),'stderr':proc.stderr.decode('utf-8','replace')};p=A/uid/f'page-{num}-ocr.json.gzip';p.write_bytes(gzip.compress((json.dumps(data,ensure_ascii=False)+'\n').encode(),mtime=0));return uid,num,len(data['text'])
if __name__=='__main__':
 j=json.loads((A/'all28-actual-source-page-index.json').read_text());tasks=[(x['itemUuid'],x['cachePdf'],p)for x in j['items']for p in x['nativeSparsePages']if not(A/x['itemUuid']/f'page-{p}-ocr.json.gzip').exists()];print('Sparse original pages scheduled:',len(tasks),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=3)as pool:
  for i,r in enumerate(pool.map(page_ocr,tasks),1):
   if i%15==0 or i==len(tasks):print(i,'/',len(tasks),r,flush=True)
