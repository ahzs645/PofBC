#!/usr/bin/env python3
"""Record candidate-aware personal source-image confirmation and corrections."""
import argparse,gzip,hashlib,json
from pathlib import Path
from gap_phsa_history_fetch import AREA
def confirm(key,rev,sheets,overrides,batch,supplement=None):
 packet=AREA/'source-only-packets'/f'{key}-{rev}{"-adaptive-"+supplement if supplement else ""}'/'packet.json';p=json.loads(packet.read_text());cp=AREA/f'{key}-scan-candidate-{rev}.json.gzip';d=json.loads(gzip.decompress(cp.read_bytes()));rows=[];targets={r['sequence']:r for r in p['targets']};ods={int(k):v for k,v in overrides.items()}
 for sheet in sheets:
  for seq in p['contactSheets'][sheet-1]['sequences']:
   a=d['rows'][seq-1]['tesseract'];v={'name':a['name'],'remuneration':a['pay']['value'],'expenses':a['expense']['value']} if a else {'name':None,'remuneration':None,'expenses':None};v.update(ods.pop(seq,{}));assert v['remuneration'] is not None,(seq,'Personal literal pay needed');t=targets[seq];rows.append({'sequence':seq,**v,'pdfPage':t['physicalPage'],'sourceCropSha256':t['sourceCropSha256'],'sourceCropPath':t['sourceCropPath']})
 assert not ods,ods
 out=AREA/'primary-image-readings';out.mkdir(exist_ok=True);dest=out/f'{key}-{rev}-batch{batch:03d}.json';assert not dest.exists();dest.write_text(json.dumps({'key':key,'sourceOnlyPacketSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'candidateSha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'method':'Primary personally viewed every listed unaltered original-pixel contact-sheet row and confirmed the selected name, remuneration and expense values against preserved OCR candidates, with explicit actual-source corrections. Candidate-aware confirmation, not a blind transcript. Independent peer source-first readings are separate.','contactSheetsPersonallyViewed':sheets,'rows':rows,'noOutreach':True},ensure_ascii=False,indent=2)+'\n');print(dest)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--key',required=True);p.add_argument('--revision',default='v4');p.add_argument('--sheets',required=True);p.add_argument('--batch',type=int,required=True);p.add_argument('--overrides',default='{}');p.add_argument('--supplement');a=p.parse_args();confirm(a.key,a.revision,[int(n) for n in a.sheets.split(',')],json.loads(a.overrides),a.batch,a.supplement)
