#!/usr/bin/env python3
"""Exact247 source-only image targets: all246 clip effects plus one comma-free line."""
import json,gzip,pathlib,fitz
from gap_health_other_history import ROOT,AREA,dump,sha

def main():
 specs={s['sourceSha256']:s for s in json.load(open(AREA/'recovered-employee-originals-v2.json'))};targets=[]
 for c in json.load(open(AREA/'native-clip-pixel-audit-index-v2.json')):
  a=json.loads(gzip.decompress((ROOT/c['path']).read_bytes()))
  for page in a['pages']:
   for row in page['rowsWithPixelChanges']:targets.append({'sourceKey':c['key'],'sourceSha256':c['sourceSha256'],'physicalPage':page['physicalPage'],'sourceRowOnPage':row['sourceRowOnPage'],'bbox':row['bbox'],'reason':'Original versus syntactically declipped field pixels differ; all effects retained as targets regardless of size.','auditPath':c['path'],'auditSha256':c['sha256']})
 for c in json.load(open(AREA/'native-primary-candidate-index.json')):
  q=json.loads(gzip.decompress((ROOT/c['secondaryFile']).read_bytes()))
  for f in q['flags']:
   if f['kind']!='pay-anchor-without-comma-name':continue
   words=f['words'];bbox=[min(w[0] for w in words),min(w[1] for w in words),max(w[2] for w in words),max(w[3] for w in words)];targets.append({'sourceKey':c['key'],'sourceSha256':c['sourceSha256'],'physicalPage':f['physicalPage'],'sourceRowOnPage':None,'bbox':bbox,'reason':'Native readers flag a monetary row with no comma in its source name field. Read complete actual visible literal; no name/amount supplied.'})
 assert len(targets)==247;targets.sort(key=lambda t:(t['sourceKey'],t['physicalPage'],t['bbox'][1]));area=AREA/'source-review-packets/employee-exceptions-001';area.mkdir(exist_ok=True,parents=True);docs={};last=None;entries=[]
 for i,t in enumerate(targets,1):
  s=specs[t['sourceSha256']];key=t['sourceKey'];pn=t['physicalPage'];path=pathlib.Path(s['retrieval']['cachePath']);assert sha(path.read_bytes())==s['sourceSha256']
  if key not in docs:docs[key]=fitz.open(path)
  page=docs[key][pn-1]
  if last!=(key,pn):pix=page.get_pixmap(matrix=fitz.Matrix(4,4),alpha=False);last=(key,pn)
  cy=(t['bbox'][1]+t['bbox'][3])/2;bounds=fitz.IRect(0,max(0,int((cy-18)*4)),pix.width,min(pix.height,int((cy+18)*4)));crop=fitz.Pixmap(pix.colorspace,bounds,False);crop.copy(pix,bounds);p=area/f'target-{i:03d}.png';crop.save(p)
  entries.append({**{k:v for k,v in t.items() if k!='bbox'},'id':f'health-other-source-001-{i:03d}','sourceUrl':s['url'],'sourceCachePath':str(path),'candidateValuesWithheld':True,'image':{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'wholePageRawPixelSha256':sha(pix.samples),'wholePageDpi':288,'integerCropPixelBox':list(bounds),'targetRowVerticalPixelRange':[round(t['bbox'][1]*4-bounds.y0),round(t['bbox'][3]*4-bounds.y0)]}})
 packet={'candidateValuesWithheld':True,'noOutreach':True,'scope':'Exact246clipping-effect candidate rows plus one additional actual monetary line omitted by comma-only name grammar. Complete original page renders at288dpi, then exact integer full-page-width row crops; no source clipping/resampling. Read central target row only; adjacent rows are context. No threshold, subtotal or candidate value supplies a missing field.','targets':entries};p=area/'packet.json';dump(p,packet);print(json.dumps({'targets':len(entries),'packet':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}))
if __name__=='__main__':main()
