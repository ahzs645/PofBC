#!/usr/bin/env python3
"""Measure literal empty/dash expense cells on original full-page pixels.

This bounded corroboration never treats a missed OCR detection as a source dash.
Numeric-looking or other ink is unresolved. The algorithm's calibration and an
independent sample review are required before its results can be adopted.
"""
import collections,gzip,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_north'
ROI={8:[405,448],28:[523,544],60:[475,535],81:[470,525],82:[500,606]}
def sha(b):return hashlib.sha256(b).hexdigest()
def components(width,height,raw,threshold=180):
 ink={(i%width,i//width) for i,v in enumerate(raw) if v<threshold};total=len(ink);out=[]
 while ink:
  todo=[ink.pop()];pts=[]
  while todo:
   x,y=todo.pop();pts.append((x,y))
   for q in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if q in ink:ink.remove(q);todo.append(q)
  xs,ys=zip(*pts);out.append({'pixels':len(pts),'x0':min(xs),'x1':max(xs),'y0':min(ys),'y1':max(ys),'width':max(xs)-min(xs)+1,'height':max(ys)-min(ys)+1})
 return total,sorted(out,key=lambda c:c['pixels'],reverse=True)
def classify(width,height,raw):
 total,cc=components(width,height,raw)
 ignored=[c for c in cc if c['width']>width*.3 and c['height']<=3 and (c['y0']<=1 or c['y1']>=height-2)]
 big=[c for c in cc if c['pixels']>=4 and c not in ignored]
 effective=total-sum(c['pixels'] for c in ignored)
 if not big and effective<=10:status='visibly-empty-source-cell'
 elif len(big)==1 and 4<=big[0]['width']<=36 and 1<=big[0]['height']<=7 and big[0]['width']/big[0]['height']>=1.8 and big[0]['pixels']>=6 and effective-big[0]['pixels']<=10:status='isolated-horizontal-source-dash'
 else:status='other-source-ink-requires-review'
 return {'classification':status,'threshold':180,'foregroundPixels':total,'effectiveForegroundPixels':effective,'ignoredLongThinCellBoundaryComponents':ignored,'components':cc}
def main():
 import fitz
 results=[]
 specs=json.loads((AREA/'ocr-plan.json').read_text())
 for spec in specs:
  n=spec['number'];proof=AREA/f'sd{n:02}-raw-reader-rows.json.gzip'
  if not proof.exists() or n not in ROI:continue
  r=json.loads(gzip.decompress(proof.read_bytes()));doc=fitz.open(spec['path']);pagepix={}
  #Probe every expense cell, including detected numeric zeros as negative controls.
  for seq,row in enumerate(r['readers']['tesseract'],1):
   p=row['pdfPage']
   if p not in pagepix:pagepix={p:doc[p-1].get_pixmap(dpi=300,colorspace=fitz.csGRAY,alpha=False)}
   pix=pagepix[p];x0,x1=ROI[n]
   if n==8:x0,x1=([400,445] if p==51 else [415,450] if p in [54,58,59] else [440,475])
   y=row['sourceYPoints'];bbox=[math.floor(x0*300/72),math.floor((y-5.2)*300/72),math.ceil(x1*300/72),math.ceil((y+5.2)*300/72)]
   data=pix.samples;xs,ys,xe,ye=bbox;raw=b''.join(data[yy*pix.stride+xs:yy*pix.stride+xe] for yy in range(ys,ye))
   metric=classify(xe-xs,ye-ys,raw)
   results.append({'number':n,'sequence':seq,'physicalPage':p,'sourceSha256':spec['sha256'],'sourceYPoints':y,'sourceName':row['name'],'preferredRawExpense':row['rawMoneyCells'][1],'preferredParsedExpense':row['expenses'],'originalPageRenderDpi':300,'roiPoints':[x0,y-5.2,x1,y+5.2],'roiPixels':bbox,'roiGrayscaleSha256':sha(raw),**metric})
   if seq%100==0:print(n,seq,flush=True)
  print('done',n,flush=True)
 out={'method':'Exact integer crop of whole original page300dpi gray; foreground threshold180; four-neighbor components. Source empty/dash classifications are corroboration, never a source-accuracy probability. Numeric positive/zero rows are negative controls.','rows':results,'acceptedRows':0}
 path=AREA/'original-expense-cell-pixels.json.gzip';path.write_bytes(gzip.compress((json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0));print(collections.Counter(x['classification'] for x in results))
if __name__=='__main__':main()
