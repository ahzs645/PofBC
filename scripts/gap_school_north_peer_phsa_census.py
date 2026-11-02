"""Independent original pixel row-band census; never reads producer OCR/candidates."""
from pathlib import Path
import json,hashlib
import fitz,numpy as np
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'research/salaries/gap-fill-2026-11-02/school_north/reviews/phsa-history'
def groups(mask):
 ys=np.flatnonzero(mask)
 if not len(ys):return []
 split=np.where(np.diff(ys)>3)[0]; starts=np.r_[0,split+1];ends=np.r_[split,len(ys)-1]
 return [(int(ys[a]),int(ys[z])+1) for a,z in zip(starts,ends)]
def main():
 inv=json.loads((ROOT/'research/salaries/gap-fill-2026-11-02/phsa_history/source-inventory.json').read_text());out=[];scale=4
 for s in inv['sources']:
  if s['key'] not in ['phsa-2011-12','phsa-2012-13']:continue
  assert hashlib.sha256(Path(s['cachePath']).read_bytes()).hexdigest()==s['sourceSha256'];doc=fitz.open(s['cachePath']); pages=[]
  for pg in range(3,91 if s['key']=='phsa-2011-12' else 87):
   pix=doc[pg-1].get_pixmap(matrix=fitz.Matrix(scale,scale),clip=fitz.Rect(435,80,462,710),colorspace=fitz.csGRAY,alpha=False);a=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width);ink=(a<150).sum(axis=1);g=groups(ink>=3);bands=[dict(y0=round(80+lo/scale,2),y1=round(80+hi/scale,2),maxInk=int(ink[lo:hi].max())) for lo,hi in g if hi-lo>=10];pages.append(dict(physicalPage=pg,broadInkBands=bands,broadInkBandCount=len(bands)))
  out.append(dict(sourceKey=s['key'],sourceSha256=s['sourceSha256'],stripPoints=[435,80,462,710],scale=scale,darkThreshold=150,minimumInkPerLine=3,minBandHeightPixels=10,maxGapPixels=3,pages=pages));print(s['key'],[(x['physicalPage'],x['broadInkBandCount']) for x in pages])
 p=BASE/'independent-source-payment-ink-census-raw.json';assert not p.exists();p.write_text(json.dumps(dict(candidateValuesOpened=False,method='Fresh originalPDF pixel projection over narrow last remuneration-digit strip. Broad bands include column headers/summary labels until source-only geometry exclusions are adjudicated; no OCR-derived row starts.',sources=out),indent=2)+'\n')
if __name__=='__main__':main()
