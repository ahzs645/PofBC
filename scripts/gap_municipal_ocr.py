#!/usr/bin/env python3
"""Two independent OCR engines on complete actual-original salary pages."""
import os
for k in ['OMP_THREAD_LIMIT','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
import argparse,gzip,hashlib,json,subprocess,time
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/municipal';CACHE=Path('/workspace/gap-municipal-cache')
def sha(b):return hashlib.sha256(b).hexdigest()
def run():
 from rapidocr_onnxruntime import RapidOCR
 import importlib.metadata
 engine=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1)
 sel=json.loads((AREA/'salary-page-selection.json').read_bytes());rs=json.loads((AREA/'refreshed-originals.json').read_bytes())['sources'];out=[]
 for source in sel['sources']:
  s=next(r for r in rs if r.get('sha256','').startswith(source['sourceShaPrefix']));key=s['employerSlug']+'-'+s['sha256'][:12];doc=fitz.open(s['cachedOriginal']);assert sha(Path(s['cachedOriginal']).read_bytes())==s['sha256']
  for pn in source['pages']:
   p=AREA/'ocr'/f'{key}-p{pn:02d}.json.gzip';p.parent.mkdir(exist_ok=True)
   if p.exists():continue
   start=time.time();pix=doc[pn-1].get_pixmap(dpi=300,alpha=False);image=CACHE/f'{key}-p{pn:02d}-300dpi.png';pix.save(image);prefix=image.with_suffix('')
   subprocess.run(['tesseract',str(image),str(prefix),'--psm','6','txt','tsv'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   raw,elapsed=engine(str(image))
   record={'sourceSha256':s['sha256'],'sourceUrl':s['sourceUrl'],'sourceKey':key,'physicalPage':pn,'render':{'method':'Actual PDF page.get_pixmap(dpi=300,alpha=False), no external image substitution','pymupdfVersion':fitz.VersionBind,'dpi':300,'width':pix.width,'height':pix.height,'pageWidth':doc[pn-1].rect.width,'pageHeight':doc[pn-1].rect.height,'imageSha256':sha(image.read_bytes())},'engines':{'tesseract':subprocess.check_output(['tesseract','--version'],text=True).splitlines()[0],'psm':6,'rapidocr':importlib.metadata.version('rapidocr_onnxruntime'),'model':'Bundled Paddle OCR ONNX models'},'tesseractRawText':prefix.with_suffix('.txt').read_text(),'tesseractRawTsv':prefix.with_suffix('.tsv').read_text(),'rapidocrRaw':raw or []}
   p.write_bytes(gzip.compress(json.dumps(record,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));print(json.dumps({'key':key,'page':pn,'seconds':round(time.time()-start,2),'rawSha256':sha(p.read_bytes())}),flush=True)
if __name__=='__main__':run()
