"""Independent source-image-only expense glyph audit; no OCR field values."""
from pathlib import Path
import json,hashlib,fitz,numpy as np
B=Path(__file__).resolve().parent;C=json.loads((B/'latest-two-scan-independent-pixel-census.json').read_text());out=[]
for s in C['sources']:
 key=s['sourceKey'];d=fitz.open('/workspace/gap-phsa-history-cache/'+key+'.pdf');xa,xb=(475,555) if key=='phsa-2013-14' else (460,525);pages={};rs=[]
 for row in s['pixelRows']:
  pn=row['physicalPage']
  if pn not in pages:
   pix=d[pn-1].get_pixmap(matrix=fitz.Matrix(300/72,300/72),colorspace=fitz.csGRAY,alpha=False);pages[pn]=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width)
  a=pages[pn];y0=int((row['y0']-1.25)*300/72);y1=int((row['y1']+1.25)*300/72);crop=a[y0:y1,round(xa*300/72):round(xb*300/72)];variants=[]
  for threshold in [120,160,180]:
   yy,xx=np.where(crop<threshold)
   if not len(xx):cl='no visible ink';box=None
   else:
    h=(yy.max()-yy.min()+1)*72/300;w=(xx.max()-xx.min()+1)*72/300;box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
    if h<=2.5 and 1.5<=w<=7:cl='small horizontal dash-shaped glyph'
    elif h>=4:cl='digit-sized source ink'
    else:cl='requires literal image calibration'
   variants.append({'threshold':threshold,'class':cl,'inkPixels':int(len(xx)),'tightPixelBox':box})
  stable=len({x['class'] for x in variants})==1;rs.append({'sourceKey':key,'sequence':row['sequence'],'physicalPage':pn,'cropPixelBox':[round(xa*300/72),y0,round(xb*300/72),y1],'dpi':300,'classification':variants[1]['class'],'stableAcrossThreeThresholds':stable,'calibrations':variants})
 counts={};flags=[]
 for r in rs:
  counts[r['classification']]=counts.get(r['classification'],0)+1
  if not r['stableAcrossThreeThresholds'] or r['classification'] in ['requires literal image calibration','no visible ink']:flags.append(r)
 out.append({'sourceKey':key,'sourceSha256':s['sourceSha256'],'sourceRows':len(rs),'classCounts':counts,'unresolvedSourceGlyphTargets':flags,'expenseGlyphs':rs,'noNumericValuesReadOrImputed':True})
p=B/'latest-two-scans-source-expense-glyph-calibration.json';p.write_text(json.dumps({'phase':'source-only before OCR field values','scope':'Computational ink-shape calibration only. A dash-shaped source glyph remains unknown, never numeric zero; digit-sized ink requires actual literal OCR/human value. No claim to personally read all expense cells.','sources':out,'noOutreach':True},indent=2)+'\n');print('SHA',hashlib.sha256(p.read_bytes()).hexdigest());print([(s['sourceKey'],s['classCounts'],len(s['unresolvedSourceGlyphTargets'])) for s in out])
