#!/usr/bin/env python3
"""Read-only diagnostics/source packets for the exact nine-history extension."""
import concurrent.futures,json,gzip,pathlib,hashlib
from decimal import Decimal
from gap_health_other_history import ROOT,AREA,dump,sha

def clip_worker(pair):
 import gap_health_employees_clip_audit as frozen
 frozen.AREA=AREA
 return frozen.one(pair)

def context_worker(pair):
 import gap_health_employees_context as frozen
 frozen.AREA=AREA
 return frozen.one(pair)

def main():
 specs=json.load(open(AREA/'recovered-employee-originals-v2.json'));idx=json.load(open(AREA/'native-primary-candidate-index.json'));by={x['sourceSha256']:x for x in idx};ev={x['sourceSha256']:x for x in json.load(open(AREA/'native-reader-evidence-index-v2.json'))}
 with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:clips=list(pool.map(clip_worker,[(s,by[s['sourceSha256']]) for s in specs]))
 dump(AREA/'native-clip-pixel-audit-index-v2.json',clips)
 contexts=[]
 for s in specs:
  c=by[s['sourceSha256']];e=ev[s['sourceSha256']];p=json.loads(gzip.decompress((ROOT/e['popplerLayout']['path']).read_bytes()))['pages'];native=json.loads(gzip.decompress((ROOT/c['file']).read_bytes()));rows=native['rows'];a,b=c['firstPage'],c['lastPage'];contexts.append({'key':c['key'],'sourceSha256':c['sourceSha256'],'sourceUrl':s['url'],'indexUrl':s['item']['discoveryUrl'],'expectedDiscoveryYearNotAcceptanceEvidence':s['item']['candidateYear'],'employeePhysicalPages':[a,b],'physicalPages':s['pdfPages'],'firstSalaryPage':{'physicalPage':a,'layoutText':p[a-1]},'lastSalaryPage':{'physicalPage':b,'layoutText':p[b-1]},'surroundingPages':[{'physicalPage':n,'layoutText':p[n-1]} for n in sorted(set([max(2,a-1),min(len(p),b+1)]))],'allPrintedControls':native['controls'],'candidateRows':len(rows),'literalRemunerationSum':str(sum(Decimal(str(r['row'][3])) for r in rows)),'knownExpenseSum':str(sum(Decimal(str(r['row'][4])) for r in rows if r['row'][4] is not None)),'noMissingAmountsInferred':True})
 dump(AREA/'source-context-review-packet.json',{'status':'awaiting actual-original independent period/definition/control review','sources':contexts,'noOutreach':True})
 with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:images=list(pool.map(context_worker,[(s,next(c for c in contexts if c['sourceSha256']==s['sourceSha256'])) for s in specs]))
 dump(AREA/'source-context-image-index.json',{'sources':images,'noOutreach':True,'physicalPageCount':sum(s['pdfPages'] for s in specs)})
 print(json.dumps({'sources':9,'candidateRows':sum(c['rows'] for c in idx),'rowsWithClipEffects':sum(c['candidateRowsWithPixelChanges'] for c in clips),'contextImages':sum(len(c['images']) for c in images)}))
if __name__=='__main__':main()
