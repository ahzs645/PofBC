#!/usr/bin/env python3
"""Append immutable actual-image primary row readings, never OCR completion."""
import argparse,hashlib,json,sys
from pathlib import Path
from gap_phsa_history_fetch import AREA
def save(key,revision,batch,body):
 packet=AREA/'source-only-packets'/f'{key}-{revision}'/'packet.json';d=json.loads(packet.read_text());targets={t['sequence']:t for t in d['targets']};rows=[]
 for ln in body.strip().splitlines():
  seq,name,pay,exp=ln.split('|');seq=int(seq);t=targets[seq];rows.append({'sequence':seq,'name':None if name=='[unknown]' else name,'remuneration':int(pay.replace(',','')),'expenses':None if exp=='-' else int(exp.replace(',','')),'pdfPage':t['physicalPage'],'sourceCropSha256':t['sourceCropSha256'],'sourceCropPath':t['sourceCropPath']})
 out=AREA/'primary-image-readings';out.mkdir(exist_ok=True);p=out/f'{key}-{revision}-batch{batch:03d}.json';assert not p.exists();p.write_text(json.dumps({'key':key,'sourceOnlyPacketSha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'method':'Primary personally viewed unaltered original-pixel contact sheets and compared OCR alternatives; explicitly candidate-aware, not a blind independent transcript. Exact visible names/numeric amounts/dashes recorded; peer source-first reading remains separate.','rows':rows,'noOutreach':True},ensure_ascii=False,indent=2)+'\n');print(str(p))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--key',required=True);p.add_argument('--revision',default='v4');p.add_argument('--batch',required=True,type=int);a=p.parse_args();save(a.key,a.revision,a.batch,sys.stdin.read())
