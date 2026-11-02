#!/usr/bin/env python3
"""Explicit source-image peer reading replay; no implicit latest-file selectors."""
import json,pathlib,gzip,hashlib,re
from decimal import Decimal
ROOT=pathlib.Path('/workspace/PofBC'); AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_employees'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def name(v):return re.sub(r'\s*,\s*',',',' '.join(v.split())) if v is not None else None
def money(v):return None if v is None else Decimal(str(v))
def main():
 ip=ROOT/'research/salaries/gap-fill-2026-11-02/health_boards/peer-health-employees/clip-effects-001/first-transcript-index.json'; assert sha(ip)=='c1f66ab64d9e07ffeb834fcf60dbc4dfcb9e65c94b9c4f8e0e7823cded0fcd1f'; idx=json.load(open(ip)); packet=ROOT/idx['packet']['path'];assert sha(packet)==idx['packet']['sha256']; targets={r['id']:r for r in json.load(open(packet))['targets']}; peer={}
 for batch in idx['batches']:
  p=ROOT/batch['path'];assert sha(p)==batch['sha256'];b=json.load(open(p));assert b['candidateValuesSeen'] is False
  for r in b['observations']:
   assert r['id'] not in peer;peer[r['id']]=(r,p,batch['sha256'])
 assert peer.keys()==targets.keys(); candidates={}
 for x in json.load(open(AREA/'native-primary-candidate-index.json')):
  p=ROOT/x['file'];assert sha(p)==x['sha256']; candidates[x['key']]={(r['row'][5],r['sourceRowOnPage']):r['row'] for r in json.load(gzip.open(p,'rt'))['rows']}
 out=[];diff=[]
 for tid,t in targets.items():
  r,p,h=peer[tid]; assert r['sourceSha256']==t['sourceSha256'] and r['physicalPage']==t['physicalPage'] and r['sourceRowOnPage']==t['sourceRowOnPage'];v=candidates[t['sourceKey']][(t['physicalPage'],t['sourceRowOnPage'])][1:5];expected=[v[0],v[2],v[3]];actual=[r.get('nameLiteral'),r['remuneration'],r['expenses']]; fields=[name(expected[0])==name(actual[0]),money(expected[1])==money(actual[1]),money(expected[2])==money(actual[2])];item={'id':tid,'sourceKey':t['sourceKey'],'physicalPage':t['physicalPage'],'sourceRowOnPage':t['sourceRowOnPage'],'primaryValues':expected,'peerValues':actual,'peerUncertainty':r.get('uncertainty',[]),'peerNote':r.get('note'),'fieldEquality':dict(zip(['name','remuneration','expenses'],fields)),'peerReceiptPath':str(p.relative_to(ROOT)),'peerReceiptSha256':h};out.append(item)
  if not all(fields):diff.append(item)
 result={'peerFirstIndex':{'path':str(ip.relative_to(ROOT)),'sha256':sha(ip)},'packetSha256':sha(packet),'candidateIndexSha256':sha(AREA/'native-primary-candidate-index.json'),'normalization':'Trim and collapse repeated whitespace; comma-adjacent spacing only. Preserve all internal name word boundaries. Decimal monetary formatting only.','total':len(out),'allThreeEqual':sum(all(v['fieldEquality'].values()) for v in out),'differences':diff,'observations':out,'sourceAccepted':False}
 p=AREA/'peer-comparisons/clip-effects-001-comparison-v1.json'; p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('total',result['total'],'differences',len(diff),'sha',sha(p));print(json.dumps(diff,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
