"""Full row-by-row peer comparison after immutable independent source transcription."""
from pathlib import Path
import json,gzip,hashlib,re
from decimal import Decimal
ROOT=Path('/workspace/PofBC');AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_native/reviews';C=ROOT/'research/salaries/gap-fill-municipal'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
first=AREA/'municipal-earliest-12-first-source-transcript.json';assert sha(first)=='0ef0222577ead359215a43d22ef04f4ca60463ed8443485a14964fc368f09cf3'
book=json.loads(first.read_text());sources={x['id']:x for x in json.loads((C/'sources.json').read_text())['sources']}
def canon(v):
 if v is None:return None
 if isinstance(v,str):
  if v.lower()=='nil':return Decimal(0)
  if v=='-':return None
  if not re.fullmatch(r'-?[\d,.]+',v):return ' '.join(v.split())
 return Decimal(str(v).replace(',',''))
def name(v):return ' '.join(v.replace('*','').split())
result=[]
for t in book['cohorts']:
 s=sources[t['sourceId']];dp=C/s['file'];ep=C/s['provenanceFile'];assert sha(dp)==s['dataSha256'];assert sha(ep)==s['provenanceSha256']
 payload=json.loads(gzip.decompress(dp.read_bytes()));e=json.loads(gzip.decompress(ep.read_bytes()));literal=e['literalSection']['rows'];assert len(t['rows'])==len(literal)==len(payload)
 mismatches=[];normal=[]
 for i,(a,b,n) in enumerate(zip(t['rows'],literal,payload),1):
  want={'name':a[0],'position':a[1],'remunerationComponent':a[2],'expenses':a[3],**{k:v for k,v in a[4].items() if k in ['taxableBenefits','expenseInclusiveTotal']}}
  for k,v in want.items():
   if canon(v)!=canon(b.get(k)):mismatches.append({'row':i,'field':k,'peerFirst':v,'candidate':b.get(k)})
  pay=canon(a[2]);benefit=a[4].get('taxableBenefits')
  if t['sourceId']=='gap-fill-municipal-city-of-rossland-2016-employee-remuneration':pay+=canon(benefit)
  expected=[s['employerSlug'],name(a[0]),a[1],pay,canon(a[3]),t['physicalPage']]
  for k,(v,w) in enumerate(zip(expected,n)):
   if canon(v)!=canon(w):normal.append({'row':i,'column':k,'peerExpected':str(v) if isinstance(v,Decimal) else v,'candidate':w})
 result.append({'sourceId':s['id'],'sourceSha256':s['sha256'],'dataFile':str(dp.relative_to(ROOT)),'dataSha256':sha(dp),'provenanceFile':str(ep.relative_to(ROOT)),'provenanceSha256':sha(ep),'rowCount':len(payload),'literalMismatches':mismatches,'normalizedMismatches':normal,'candidateSourceMetadata':s})
out={'immutableFirstTranscriptSha256':sha(first),'rowCount':sum(x['rowCount'] for x in result),'literalMismatches':sum(len(x['literalMismatches']) for x in result),'normalizedMismatches':sum(len(x['normalizedMismatches']) for x in result),'cohorts':result}
p=AREA/'municipal-earliest-12-initial-comparison.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for x in result:
 if x['literalMismatches'] or x['normalizedMismatches']:print(x['sourceId'],json.dumps({'literal':x['literalMismatches'],'normalized':x['normalizedMismatches']},ensure_ascii=False))
print('TOTAL',out['rowCount'],out['literalMismatches'],out['normalizedMismatches'])
