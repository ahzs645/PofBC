#!/usr/bin/env python3
"""Original page raster replay and full-page payment-row census, separate from table windows."""
import gzip,json,hashlib,re
from decimal import Decimal
from pathlib import Path
from gap_school_south_fetch import AREA,CACHE
from gap_school_south_scan import SPECS,tesseract,paddle

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def numeric(v):
 try:Decimal(v);return True
 except Exception:return False

def run(n):
 import fitz
 source=json.loads((AREA/f'sd{n}-sofi-2025-retrieval.json').read_text());pdf=CACHE/f'sd{n}-sofi-2025.pdf';assert sha(pdf.read_bytes())==source['sha256'];doc=fitz.open(pdf);candidate=load(AREA/f'sd{n}-scan-parsed-v9.json.gzip');pageproofs=[];unexplained=[]
 for p in SPECS[n]['pages']:
  path=AREA/'raw-ocr'/f'sd{n}-sofi-2025-p{p}.json.gzip';raw=load(path);assert raw['sourceSha256']==source['sha256'];pix=doc[p-1].get_pixmap(dpi=300);actual=sha(pix.tobytes('png'));assert actual==raw['imageSha256'],(n,p,'original raster mismatch')
  ranges=SPECS[n].get('ranges',{});default=SPECS[n]['defaultRange'];SPECS[n]['ranges']={};SPECS[n]['defaultRange']=[0,10000]
  try:wide=[tesseract(raw,n),paddle(raw,n)]
  finally:SPECS[n]['ranges']=ranges;SPECS[n]['defaultRange']=default
  extras=[];rowcounts=[]
  for name,ws in zip(['tesseractRows','paddleRows'],wide):
   selected=[r for r in candidate[name] if r['pdfPage']==p];ys={r['sourceY300dpi'] for r in selected};outside=[r for r in ws if r['sourceY300dpi'] not in ys and numeric(r['remuneration'])];observed=[]
   for r in outside:
    aggregate=n==78 and p==56 and r['name'].startswith('Paid to each employee was $75,000.00 or less')
    employer_control=(n==70 and p==60 and re.sub(r'\s+','',r['name']).upper().startswith('TOTALEMPLOYERPREMIUMFORCPP/EI') and r['remuneration']=='2692549.75') or (n==79 and p==69 and r['name']=='Receiver General of Canada' and r['expenses']=='5396794.95')
    item={'reader':name,'physicalPage':p,'sourceY300dpi':r['sourceY300dpi'],'name':r['name'],'remuneration':r['remuneration'],'expenses':r['expenses'],'disposition':'source-labelled-below-threshold-aggregate-excluded' if aggregate else ('source-labelled-employer-CPP-EI-control-excluded' if employer_control else 'UNEXPLAINED-MONEY-BEARING-ROW')};observed.append(item)
    if not aggregate and not employer_control:unexplained.append(item)
   extras.extend(observed);rowcounts.append({'reader':name,'selectedRows':len(selected),'fullPageCandidateRows':len(ws),'outsideMoneyRows':len(observed)})
  pageproofs.append({'physicalPage':p,'originalCompletePagePngSha256':actual,'rawProofSha256':sha(path.read_bytes()),'readers':rowcounts,'outsideWindowMoneyRowDecisions':extras})
 result={'district':n,'sourceSha256':source['sha256'],'method':'Sequential fresh complete original300dpi raster replay for every salarypage, plus each independent reader rerun over the whole page without its table Y window. All monetary candidate rows outside selected windows explicitly classified. Control-label recognition stays separate from named payment rows. Agreement and this finite census do not establish infallibility.','pages':pageproofs,'unexplainedMoneyRows':unexplained,'pass':not unexplained,'sixRecoveredRowsHistory':'SD78 four payment rows and SD79 two payment rows were found outside previous v7 windows, recovered from full original pages, and retained in v9/v12. Earlier candidates stay preserved.','noOutreach':True}
 (AREA/f'sd{n}-complete-page-census-and-original-replay.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'district':n,'salaryPages':len(pageproofs),'originalPngReplays':len(pageproofs),'unexplainedMoneyRows':len(unexplained)}),flush=True)
 assert not unexplained
if __name__=='__main__':
 for n in [35,38,69,70,78,79]:run(n)
