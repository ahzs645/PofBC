#!/usr/bin/env python3
"""Resolve only the28 captured financial items through explicit ORIGINAL relations."""
from pathlib import Path
import json,hashlib,urllib.request,concurrent.futures,time
ROOT=Path('/workspace/PofBC');AREA=ROOT/'research/salaries/gap-fill-2026-11-02/reviews/financial-catalogue-audit';CACHE=Path('/workspace/gap-financial-catalogue-cache');AREA.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
INPUT=ROOT/'research/salaries/gap-fill-2026-11-02/health_employees/financial-originals-not-yet-assessed-for-named-scope.json';API='https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api';sha=lambda b:hashlib.sha256(b).hexdigest()
def fetch(url,kind,item):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 salary-source-research','Accept':'application/json'if kind!='original-pdf'else'application/pdf'})
 try:
  with urllib.request.urlopen(req,timeout=90)as r:data=r.read();status=r.status;final=r.url;headers=dict(r.headers)
 except Exception as e:return {'url':url,'kind':kind,'itemUuid':item,'error':str(e),'status':getattr(e,'code',None)},None
 digest=sha(data);suffix='.pdf'if data.startswith(b'%PDF-')else'.json';path=CACHE/f'{item}-{digest[:20]}{suffix}'
 if not path.exists():path.write_bytes(data)
 else:assert path.read_bytes()==data
 receipt={'url':url,'kind':kind,'itemUuid':item,'status':status,'finalUrl':final,'headers':headers,'bytes':len(data),'sha256':digest,'cachePath':str(path)}
 return receipt,data

def resolve(record):
 uid=record['itemUuid'];events=[];receipt,data=fetch(f'{API}/core/items/{uid}/bundles','captured-item-bundles',uid);events.append(receipt);originals=[]
 if data is not None:
  for bundle in json.loads(data).get('_embedded',{}).get('bundles',[]):
   if bundle.get('name')!='ORIGINAL':continue
   url=bundle['_links']['bitstreams']['href'];r,b=fetch(url,'explicit-original-bundle-bitstream-metadata',uid);events.append(r)
   if b is None:continue
   for stream in json.loads(b).get('_embedded',{}).get('bitstreams',[]):
    u=stream['_links']['content']['href'];r,body=fetch(u,'original-pdf',uid);events.append(r);originals.append({'bitstreamUuid':stream['uuid'],'name':stream['name'],'metadataSizeBytes':stream.get('sizeBytes'),'metadataChecksum':stream.get('checkSum'),'sourceUrl':u,'retrieval':r,'isPdf':body is not None and body.startswith(b'%PDF-'),'metadataReceiptSha256':sha(b)})
 out={**record,'scopeAssessmentStatus':'actual-original-not-yet-inspected','cataloguePeriodIsNotAcceptanceEvidence':True,'originals':originals,'retrievalEvents':events,'noOutreach':True};(AREA/f'{uid}-retrieval.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out
if __name__=='__main__':
 records=json.loads(INPUT.read_text());assert len(records)==28 and len({r['itemUuid']for r in records})==28
 # The complete label audit resolved three Island salary counterparts, leaving10 priority originals.
 priorities=json.loads((INPUT.parent/'metadata-only-financial-priority.json').read_text());priority_ids={r['itemUuid']for r in priorities};assert len(priority_ids)==10
 def priority(r):return r['itemUuid']in priority_ids
 ordered=sorted(records,key=lambda r:(not priority(r),records.index(r)));(AREA/'input-items.json').write_text(json.dumps({'inputFile':str(INPUT.relative_to(ROOT)),'inputSha256':sha(INPUT.read_bytes()),'items':[{**r,'priorityWithoutLocatedSalaryCounterpart':priority(r)}for r in ordered],'scope':'Exactly28captured financial items. No external discovery. Title does not establish salary absence.','noOutreach':True},ensure_ascii=False,indent=2)+'\n');assert sum(priority(r)for r in records)==10
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
  for result in pool.map(resolve,ordered):print(result['itemUuid'],result['employerSlug'],result['catalogueYearDiscoveryOnly'],[(a['name'],a['retrieval'].get('status'),a['retrieval'].get('bytes'))for a in result['originals']],flush=True)
