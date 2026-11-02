import json,gzip,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
R=Path('/workspace/PofBC');O=R/'research/salaries/gap-fill-2026-11-02/health_boards/peer-phsa-history';P=O/'independent-complete-cell-census-v2.json.gzip';q=json.loads(gzip.decompress(P.read_bytes()));out={'sourceOnlyParent':{'path':str(P.relative_to(R)),'sha256':hashlib.sha256(P.read_bytes()).hexdigest()},'candidateValuesSeen':False,'method':'Source-specific complete-cell glyph bounds calibrated ONLY from previously locked personally read source-null examples; observed extrema plus onepixel width/height tolerance, aspect/fill bounds retain exact calibration minima. Connected components8 retained per complete-cell tinyglyph. Tall numericglyphs never pass. All blank/multiglyph/out-of-range cases remain explicit challenges, no null from absent OCR.','sources':[],'noOutreach':True}
def cc(mask):
 points={tuple(map(int,p))for p in np.argwhere(mask)};n=0
 while points:
  stack=[points.pop()];n+=1
  while stack:
   y,x=stack.pop()
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     pt=(y+dy,x+dx)
     if pt in points:points.remove(pt);stack.append(pt)
 return n
for s in q['sources']:
 cells=[r for p in s['pages']for r in p['expenseCells']];nulls=[r for r in cells if r.get('personalSourceFirstCalibration',{}).get('expenses','NA')is None];cal={'width':[min(r['glyphWidth']for r in nulls)-1,max(r['glyphWidth']for r in nulls)+1],'height':[max(1,min(r['glyphHeight']for r in nulls)-1),max(r['glyphHeight']for r in nulls)+1],'minAspect':min(r['aspectRatio']for r in nulls),'minFill':min(r['inkFill']for r in nulls),'personalNullSequences':[r['sequence']for r in nulls]};pages=[]
 for p in s['pages']:
  ink=np.asarray(Image.open(p['sourceRasterPath']).convert('L'))<128;rows=[]
  for r in p['expenseCells']:
   row=dict(r);potential=not r['blank']and cal['width'][0]<=r['glyphWidth']<=cal['width'][1]and cal['height'][0]<=r['glyphHeight']<=cal['height'][1]and r['aspectRatio']>=cal['minAspect']and r['inkFill']>=cal['minFill']
   if not r['blank']and r['glyphWidth']<=40 and r['glyphHeight']<=15:
    x0,y0,x1,y1=r['glyphBox'];m=ink[y0:y1,x0:x1];row['glyph8ConnectedComponents']=cc(m);row['packedGlyphMask']=np.packbits(m).tobytes().hex()
   row['sourceCalibratedDashShape']=potential and row.get('glyph8ConnectedComponents')==1
   row['expenseCellClass']='source-calibrated-dash'if row['sourceCalibratedDashShape']else'tall-numeric-ink'if not r['blank']and r['glyphHeight']>=18 else'unresolved-cell-ink'
   rows.append(row)
  pages.append({'physicalPage':p['physicalPage'],'sourceRasterPath':p['sourceRasterPath'],'sourceRasterSha256':p['sourceRasterSha256'],'cells':rows})
 rec={'sourceKey':s['sourceKey'],'sourceSha256':s['sourceSha256'],'calibration':cal,'pages':pages};out['sources'].append(rec);print(s['sourceKey'],cal,'classes',{c:sum(r['expenseCellClass']==c for p in pages for r in p['cells'])for c in ['source-calibrated-dash','tall-numeric-ink','unresolved-cell-ink']});print('unresolved',[(p['physicalPage'],r['sequence'],r.get('glyphWidth'),r.get('glyphHeight'),r.get('inkFill'),r.get('glyph8ConnectedComponents'))for p in pages for r in p['cells']if r['expenseCellClass']=='unresolved-cell-ink']);print('manual disagreements',[r['sequence']for p in pages for r in p['cells']if'personalSourceFirstCalibration'in r and(r['personalSourceFirstCalibration']['expenses']is None)!=r['sourceCalibratedDashShape']])
p=O/'independent-source-calibrated-expense-cells-v1.json.gzip';assert not p.exists();p.write_bytes(gzip.compress((json.dumps(out,indent=2)+'\n').encode(),mtime=0));print(str(p),hashlib.sha256(p.read_bytes()).hexdigest())
