#!/usr/bin/env python3
"""Values-withheld original-pixel PHSA review packets; candidates separate."""
import argparse,collections,gzip,hashlib,json,math,statistics
from pathlib import Path
from gap_phsa_history_fetch import AREA
def sha(b):return hashlib.sha256(b).hexdigest()
def make(key,revision,supplement=None,sequences=None):
 from PIL import Image,ImageDraw
 cp=AREA/f'{key}-scan-candidate-{revision}.json.gzip';d=json.loads(gzip.decompress(cp.read_bytes()));out=AREA/'source-only-packets'/f'{key}-{revision}{"-adaptive-"+supplement if supplement else ""}';out.mkdir(parents=True,exist_ok=True);assert not (out/'packet.json').exists();rows=d['rows'];reasons=collections.defaultdict(set)
 true=[r for r in rows if any(not s.startswith('low-') for s in r['reasons'])]
 for r in true:reasons[r['sequence']].add('source-field-or-geometry-review')
 # Lowest individual reader scores plus stratified score ranges are finite
 # policy challenges, not accuracy claims or a silent dismissal of prior flags.
 for who,field in [('tesseract','nameConfidence'),('rapid','nameConfidence'),('tesseract','payConfidence'),('rapid','payConfidence'),('tesseract','expenseConfidence'),('rapid','expenseConfidence')]:
  eligible=[r for r in rows if r[who] and r[who].get(field) is not None and not any(not s.startswith('low-') for s in r['reasons'])]
  eligible.sort(key=lambda r:(r[who][field],r['sequence']))
  for r in eligible[:5]:reasons[r['sequence']].add('source-confidence-minimum-challenge')
  for q in [.05,.15,.3,.5,.7,.85,.95]:
   if eligible:reasons[eligible[min(len(eligible)-1,int(len(eligible)*q))]['sequence']].add('source-confidence-range-challenge')
 lowglyph=[r for r in rows if r['expenseFullCellInk'].get('connectedInkComponents')==1 and r['expenseFullCellInk'].get('glyphHeight',99)<=12]
 for r in sorted(lowglyph,key=lambda r:(r['expenseFullCellInk']['aspectRatio'],r['sequence']))[:12]:reasons[r['sequence']].add('source-dash-shape-calibration')
 for r in sorted(lowglyph,key=lambda r:sha((d['source']['sourceSha256']+str(r['sequence'])).encode()))[:12]:reasons[r['sequence']].add('source-dash-shape-holdout')
 digits=[r for r in rows if r['tesseract'] and r['tesseract']['expense']['kind']=='number' and abs(r['tesseract']['expense']['value'])<=9]
 for r in digits[:20]:reasons[r['sequence']].add('source-numeric-zero-or-single-digit-challenge')
 for r in sorted(rows,key=lambda r:sha((d['source']['sourceSha256']+'withheld'+str(r['sequence'])).encode()))[:20]:reasons[r['sequence']].add('deterministic-withheld-source-benchmark')
 if sequences is not None:
  assert supplement,'Custom source-only challenge needs a separate immutable supplement label'
  reasons=collections.defaultdict(set)
  for sequence in sequences:reasons[sequence].add('explicit-source-glyph-or-layout-challenge')
 elif supplement:
  selected=loadselected=AREA/f'{key}-scan-selected-{supplement}.json.gzip';pending=json.loads(gzip.decompress(selected.read_bytes()))['pending'];reasons=collections.defaultdict(set)
  for r in pending:reasons[r['sequence']].update(r['reasons'])
 targets=[];ims={};sourcepages={p['physicalPage']:p for p in d['pages']}
 for seq,tags in sorted(reasons.items()):
  r=rows[seq-1];p=r['physicalPage'];pg=sourcepages[p];raw=json.loads(gzip.decompress((Path.cwd()/pg['rawPath']).read_bytes()));path=Path(raw['sourceImageCachePath'])
  if p not in ims:assert sha(path.read_bytes())==raw['sourceImageSha256'];ims[p]=Image.open(path).convert('RGB')
  band=r['sourceNameBand'];pitch=pg['geometry']['rowPitchPixels'];left=0;right=ims[p].width;top=max(pg['geometry']['bodyTop'],math.floor(band['center']-pitch*.7));bottom=min(pg['geometry']['bodyBottom'],math.ceil(band['center']+pitch*.7));box=[left,top,right,bottom];dest=out/f'seq{seq:05d}-p{p:03d}.png';ims[p].crop(box).save(dest)
  targets.append({'sequence':seq,'physicalPage':p,'rowOnPage':r['rowOnPage'],'reviewReasons':sorted(tags),'sourceSha256':d['source']['sourceSha256'],'wholeOriginalPageRasterSha256':raw['sourceImageSha256'],'cropBoxOriginalPixels':box,'sourceCropPath':str(dest.relative_to(Path.cwd())),'sourceCropSha256':sha(dest.read_bytes())})
 sheets=[]
 for n in range(0,len(targets),12):
  chunk=targets[n:n+12];crops=[Image.open(Path.cwd()/t['sourceCropPath']).convert('RGB') for t in chunk];width=max(im.width for im in crops);height=sum(im.height+28 for im in crops);sheet=Image.new('RGB',(width,height),'#eeeeee');dr=ImageDraw.Draw(sheet);y=0
  for t,im in zip(chunk,crops):dr.text((5,y+3),f"seq {t['sequence']} | physical {t['physicalPage']} | source row {t['rowOnPage']}",fill='black');sheet.paste(im,(0,y+28));y+=im.height+28
  dest=out/f'contact-{n//12+1:03d}.png';sheet.save(dest);sheets.append({'sequences':[t['sequence'] for t in chunk],'path':str(dest.relative_to(Path.cwd())),'sha256':sha(dest.read_bytes()),'method':'Unmodified actual original-page pixel row crops with separate locator-only margins; no expected fields.'})
 packet={'key':key,'source':d['source'],'candidateSnapshotSha256':sha(cp.read_bytes()),'candidateRevision':revision,'valuesWithheld':True,'targetCount':len(targets),'targets':targets,'contactSheets':sheets,'initialConfidenceOnlyFlagsRetained':sum(bool(r['reasons']) and all(s.startswith('low-') for s in r['reasons']) for r in rows),'fullCensusLocators':[{'physicalPage':p['physicalPage'],'sourceRasterSha256':p['sourceImageSha256'],'paymentBandCount':len(p['rows']),'sourcePaymentBands':p['geometry']['nameBands'],'paymentColumnControlRuleY':p['geometry'].get('paymentColumnControlRuleY')} for p in d['pages']],'noOutreach':True};(out/'packet.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'key':key,'sourceFieldReviewRows':len(true),'targets':len(targets),'sheets':len(sheets),'path':str(out/'packet.json')}),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--key',action='append',required=True);p.add_argument('--revision',default='v4');p.add_argument('--supplement');p.add_argument('--sequences');a=p.parse_args()
 for k in a.key:make(k,a.revision,a.supplement,[int(s) for s in a.sequences.split(',')] if a.sequences else None)
