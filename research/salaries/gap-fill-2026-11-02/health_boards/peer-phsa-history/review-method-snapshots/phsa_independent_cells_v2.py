import json,hashlib,gzip,statistics
from pathlib import Path
import numpy as np
from PIL import Image
R=Path('/workspace/PofBC');A=R/'research/salaries/gap-fill-2026-11-02';O=A/'health_boards/peer-phsa-history';P=A/'phsa_history/first-two-scans-source-only-layout-guide.json';guide=json.loads(P.read_bytes());result={'sourceOnlyGuide':{'path':str(P.relative_to(R)),'sha256':hashlib.sha256(P.read_bytes()).hexdigest()},'candidateValuesSeen':False,'method':'Independent raster-only horizontal projection and complete expense-cell ink measurement. No imports of producer readers/pixel module, OCR rows, names or monetary values. Body header/control locators from source-only guide. Two distinct remuneration-column strips independently counted using threshold128, >=4ink pixels per scanline, gap<=4, >=18px height (all six12px first-header descender bands retained in v1 diagnostic and excluded after actual header views), >=90ink area. Full expense cell between independent pay-band midpoints; source-dash examples are personal source-first null observations, preserving all other ink as non-dash/uncertain. Never null from OCR absence.','sources':[],'noOutreach':True}
def groups(ys):
 out=[]
 for y in ys:
  if out and y-out[-1][-1]<=4:out[-1].append(int(y))
  else:out.append([int(y)])
 return out
for s in guide['sources']:
 key=s['key'];profile=s['profile'];pages=[];seq=0;manual={}
 for p in sorted((O/key).glob('first-transcript-???.json')):
  for r in json.loads(p.read_bytes())['observations']:manual[r['sequence']]=r
 for addon in [key+'-v4-adaptive-v1',key+'-v4-adaptive-v3']:
  p=O/addon/'first-transcript.json'
  if p.exists():
   for r in json.loads(p.read_bytes())['observations']:manual[r['sequence']]=r
 for p in s['pages']:
  page=p['physicalPage'];g=p['geometry'];raster=Path('/workspace/gap-phsa-history-cache/images')/(key+'-p%03d.png'%page);raw=raster.read_bytes();assert hashlib.sha256(raw).hexdigest()==p['sourceImageSha256'];im=Image.open(raster).convert('L');ink=np.asarray(im)<128;top=g['bodyTop'];bottom=g['censusColumnBox'][3];cuts=([1568,1860],[1645,1845])if key=='phsa-2009-10'else([1760,2125],[1840,2105]);reads=[]
  for x0,x1 in cuts:
   projection=ink[top:bottom,x0:x1].sum(axis=1);bands=[]
   for ys in groups(np.flatnonzero(projection>=4)):
    mass=int(projection[ys[0]:ys[-1]+1].sum())
    if ys[-1]-ys[0]+1>=18 and mass>=90:bands.append({'top':top+ys[0],'bottom':top+ys[-1]+1,'center':top+(ys[0]+ys[-1])/2,'inkPixels':mass})
   reads.append(bands)
  bands=reads[0];centers=[b['center']for b in bands];pitch=statistics.median([b-a for a,b in zip(centers,centers[1:])])if len(bands)>1 else profile['sourceFirstTableRowPitchPixels'];cells=[]
  for i,b in enumerate(bands):
   seq+=1;y0=int((centers[i-1]+b['center'])//2)if i else max(top,int(b['center']-pitch/2));y1=int((centers[i+1]+b['center'])//2)if i+1<len(bands)else min(bottom,int(b['center']+pitch/2));x0=profile['payExpenseBoundary'];x1=2550;mask=ink[y0:y1,x0:x1];ys,xs=np.nonzero(mask);row={'sequence':seq,'rowOnPage':i+1,'sourceExpenseCellBox':[x0,y0,x1,y1],'blackPixels':int(len(xs)),'blank':not len(xs)}
   if len(xs):
    l,r,t,bx=int(xs.min()),int(xs.max())+1,int(ys.min()),int(ys.max())+1;h=bx-t;w=r-l;row.update({'glyphBox':[x0+l,y0+t,x0+r,y0+bx],'glyphWidth':w,'glyphHeight':h,'aspectRatio':w/h,'inkFill':len(xs)/(w*h),'shortHorizontalShape':2<=w<=40 and 1<=h<=15 and w/h>=2 and len(xs)/(w*h)>=.5})
   if seq in manual:row['personalSourceFirstCalibration']={'expenses':manual[seq]['expenses'],'nameLiteral':manual[seq]['nameLiteral'],'targetOrdinal':manual[seq].get('targetOrdinal')}
   cells.append(row)
  pages.append({'physicalPage':page,'sourceRasterPath':str(raster),'sourceRasterSha256':p['sourceImageSha256'],'bodyY':[top,bottom],'alternatePayStripBoxes':[[*cuts[0][:1],top,cuts[0][1],bottom],[*cuts[1][:1],top,cuts[1][1],bottom]],'firstPayBands':reads[0],'secondPayBands':reads[1],'bandCountsAgree':len(reads[0])==len(reads[1]),'producerLocatorBandCount':len(g['nameBands']),'independentBandCount':len(bands),'locatorCountAgrees':len(bands)==len(g['nameBands']),'expenseCells':cells})
 result['sources'].append({'sourceKey':key,'sourceSha256':s['source']['sourceSha256'],'pages':pages,'independentPaymentBandCount':seq,'allAlternateBandCountsAgree':all(p['bandCountsAgree']for p in pages),'allLocatorCountsAgree':all(p['locatorCountAgrees']for p in pages)})
p=O/'independent-complete-cell-census-v2.json.gzip';assert not p.exists();p.write_bytes(gzip.compress((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0));print(str(p),hashlib.sha256(p.read_bytes()).hexdigest())
for s in result['sources']:
 print(s['sourceKey'],s['independentPaymentBandCount'],s['allAlternateBandCountsAgree'],s['allLocatorCountsAgree']);print('badpages',[(p['physicalPage'],p['independentBandCount'],len(p['secondPayBands']),p['producerLocatorBandCount'])for p in s['pages']if not p['bandCountsAgree']or not p['locatorCountAgrees']]);cells=[r for p in s['pages']for r in p['expenseCells']];print('cells',len(cells),'blank',sum(r['blank']for r in cells),'dashShape',sum(r.get('shortHorizontalShape',False)for r in cells));print('personal null shape conflicts',[r['sequence']for r in cells if r.get('personalSourceFirstCalibration',{}).get('expenses','NA')is None and not r.get('shortHorizontalShape')]);print('personalnumeric shortshape',[r['sequence']for r in cells if r.get('personalSourceFirstCalibration',{}).get('expenses','NA')not in ['NA',None] and r.get('shortHorizontalShape')])
