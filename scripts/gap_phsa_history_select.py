#!/usr/bin/env python3
"""Provisional selection from actual-image receipts or explicitly guarded agreement.

This does not publish or mark a cohort verified. Peer source-first evidence,
original-page census and source definitions must close before export.
"""
import argparse,collections,gzip,hashlib,json,re
from pathlib import Path
from gap_phsa_history_fetch import AREA
from gap_phsa_history_scan import namekey
def sha(b):return hashlib.sha256(b).hexdigest()
def same(x,y):return namekey(x)==namekey(y) if isinstance(x,str) and isinstance(y,str) else x==y
def run(key,revision,selectedrev,write=True):
 cp=AREA/f'{key}-scan-candidate-{revision}.json.gzip';d=json.loads(gzip.decompress(cp.read_bytes()));receipts=[];manual={};packets={sha(p.read_bytes()):json.loads(p.read_text()) for p in (AREA/'source-only-packets').glob(f'{key}-{revision}*/packet.json')}
 for p in sorted((AREA/'primary-image-readings').glob(f'{key}-{revision}-batch*.json')):
  doc=json.loads(p.read_text());packet=packets[doc['sourceOnlyPacketSha256']];assert packet['candidateSnapshotSha256']==sha(cp.read_bytes()),('stale packet candidate',str(p));assert doc.get('candidateSha256',sha(cp.read_bytes()))==sha(cp.read_bytes()),('stale primary candidate',str(p));receipts.append({'path':str(p.relative_to(Path.cwd())),'sha256':sha(p.read_bytes())})
  packetrows={r['sequence']:r for r in packet['targets']}
  for r in doc['rows']:
   assert r['sequence'] not in manual
   target=packetrows[r['sequence']];assert r['pdfPage']==target['physicalPage'] and r['sourceCropSha256']==target['sourceCropSha256']
   assert sha((Path.cwd()/r['sourceCropPath']).read_bytes())==r['sourceCropSha256'],('stale original crop',r['sequence'])
   manual[r['sequence']]=r
 for p in sorted((AREA/'primary-image-readings').glob(f'{key}-{revision}-additive*.json')):
  doc=json.loads(p.read_text());assert doc['candidateSha256']==sha(cp.read_bytes());assert sha((Path.cwd()/doc['priorReceipt']).read_bytes())==doc['priorReceiptSha256'];assert sha((Path.cwd()/doc['sourceImage']).read_bytes())==doc['sourceImageSha256'];receipts.append({'path':str(p.relative_to(Path.cwd())),'sha256':sha(p.read_bytes())})
  for amendment in doc['amendments']:
   seq=amendment['sequence'];assert seq in manual
   for field,value in amendment['priorSelected'].items():assert manual[seq][field]==value,(seq,field,'stale additive correction')
   manual[seq]={**manual[seq],**amendment['actualSourceSelected']}
 targets=json.loads((AREA/'source-only-packets'/f'{key}-{revision}'/'packet.json').read_text())['targets'];assert {r['sequence'] for r in targets}<=set(manual),('Personal packet reads unfinished',key)
 floor={};bench={}
 for who in ['tesseract','rapid']:
  for field,sc in [('name','nameConfidence'),('remuneration','payConfidence'),('expenses','expenseConfidence')]:
   good=[]
   for seq,m in manual.items():
    a=d['rows'][seq-1][who]
    if a is None:continue
    v=a['name'] if field=='name' else a['pay' if field=='remuneration' else 'expense']['value']
    if a.get(sc) is not None and same(v,m[field]):good.append((a[sc],seq))
   if good:floor[who+'.'+sc]=min(good)[0];bench[who+'.'+sc]=[q for q in good if q[0]==min(good)[0]]
 glyphs=[d['rows'][seq-1]['expenseFullCellInk'] for seq,m in manual.items() if m['expenses'] is None and d['rows'][seq-1]['expenseFullCellInk'].get('connectedInkComponents')==1]
 assert glyphs
 calib={'widthRange':[min(g['glyphWidth'] for g in glyphs),max(g['glyphWidth'] for g in glyphs)],'heightRange':[min(g['glyphHeight'] for g in glyphs),max(g['glyphHeight'] for g in glyphs)],'minimumAspectRatio':min(g['aspectRatio'] for g in glyphs),'minimumInkFill':min(g['inkFill'] for g in glyphs),'knownMasks':sorted({g['maskSha256'] for g in glyphs}),'connectedInkComponents':1,'allCellInkRequired':True,'personallyReadSourceDashRows':[seq for seq,m in manual.items() if m['expenses'] is None]}
 result=[];pending=[];corrections=[]
 for r in d['rows']:
  seq=r['sequence'];a=r['tesseract'];b=r['rapid'];reasons=[]
  if seq in manual:
   selected={k:manual[seq][k] for k in ['name','remuneration','expenses','pdfPage']};basis='Primary actual original-image personal reading; independent peer pending';changed=[]
   if a:
    for field,x in [('name',a['name']),('remuneration',a['pay']['value']),('expenses',a['expense']['value'])]:
     if not same(selected[field],x):changed.append({'field':field,'tesseract':x,'actualSourceSelected':selected[field]})
   if changed:corrections.append({'sequence':seq,'fields':changed})
  else:
   selected={**r['selected']} if r['selected'] else None;basis='Two independent original-raster readers agree within the new-source benchmarked finite guards; not an all-row personal transcription'
   if not a or not b:reasons.append('row-reader-cardinality')
   else:
    if namekey(a['name'])!=namekey(b['name']):reasons.append('name-disagreement')
    for col in ['pay','expense']:
     if a[col]['kind']=='number' or b[col]['kind']=='number':
      if a[col]['kind']!='number' or b[col]['kind']!='number' or a[col]['value']!=b[col]['value']:reasons.append(col+'-not-identical-numeric')
     elif col=='pay':reasons.append('remuneration-must-be-numeric')
     elif a[col]['kind'] not in ['explicit-dash','not-recognized'] or b[col]['kind'] not in ['explicit-dash','not-recognized']:reasons.append('expense-unparsed')
    for who,raw in [('tesseract',a),('rapid',b)]:
     for sc in ['nameConfidence','payConfidence','expenseConfidence']:
      if sc=='expenseConfidence' and raw['expense']['kind']!='number':continue
      if raw.get(sc) is None or raw[sc]<floor.get(who+'.'+sc,float('inf')):reasons.append(who+'-'+sc+'-outside-personally-verified-score-range')
    if re.search(r'^l[A-Za-z]|[, ](?:[l|!]\w|[|!])|Mcl|Mcint|[*!|]',a['name']):reasons.append('adaptive-confusable-name-glyph')
    if a['pay']['value'] is not None and a['pay']['value']<=75000:reasons.append('amount-at-or-below-stated-disclosure-threshold')
    glyph=r['expenseFullCellInk']
    if a['expense']['kind']!='number':
     okay=(not glyph.get('blank') and glyph.get('connectedInkComponents')==1 and calib['widthRange'][0]<=glyph.get('glyphWidth',0)<=calib['widthRange'][1] and calib['heightRange'][0]<=glyph.get('glyphHeight',0)<=calib['heightRange'][1] and glyph.get('aspectRatio',0)>=calib['minimumAspectRatio'] and glyph.get('inkFill',0)>=calib['minimumInkFill'])
     if not okay:reasons.append('outside-source-personally-calibrated-full-cell-dash-ink')
    elif glyph.get('connectedInkComponents')==1 and glyph.get('glyphHeight',99)<=calib['heightRange'][1]:reasons.append('numeric-expense-over-small-source-glyph')
  if reasons:pending.append({'sequence':seq,'physicalPage':r['physicalPage'],'reasons':sorted(set(reasons))})
  result.append({'sequence':seq,'selected':selected,'basis':basis,'pending':sorted(set(reasons))})
 out={'key':key,'candidateRevision':revision,'candidateSha256':sha(cp.read_bytes()),'sourceSha256':d['source']['sourceSha256'],'rows':result,'pending':pending,'primaryPersonalReceipts':receipts,'primaryPersonallyReadRows':len(manual),'initialConfidenceFlagsPreservedInCandidate':True,'finiteSourceGuard':{'confidenceFloorsPersonallyCorroborated':floor,'lowestSourceVerifiedBenchmarks':bench,'dashCalibration':calib,'limit':'These finite benchmarks and agreement guards reduce known failure modes; they do not establish infallible OCR or a statistical accuracy rate. All original alternatives, first exceptions and personally reviewed corrections are preserved.'},'literalComputedTotals':[sum(r['selected'][field] or 0 for r in result if r['selected']) for field in ['remuneration','expenses']],'primaryCorrections':corrections,'acceptedRows':0,'noOutreach':True}
 if write:
  dest=AREA/f'{key}-scan-selected-{selectedrev}.json.gzip';assert not dest.exists();dest.write_bytes(gzip.compress((json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0));print(json.dumps({'key':key,'rows':len(result),'manual':len(manual),'pending':len(pending),'reasonCounts':dict(collections.Counter(x for r in pending for x in r['reasons'])),'totals':out['literalComputedTotals'],'corrections':len(corrections)}),flush=True)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--key',action='append',required=True);p.add_argument('--revision',default='v4');p.add_argument('--selected-revision',default='v1');a=p.parse_args()
 for k in a.key:run(k,a.revision,a.selected_revision)
