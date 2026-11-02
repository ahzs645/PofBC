from pathlib import Path
import json,gzip,re,hashlib
from decimal import Decimal
R=Path('/workspace/PofBC');A=Path(__file__).resolve().parent;H=R/'research/salaries/gap-fill-2026-11-02/health_other_history';P=H/'native-primary-candidate-index.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)=='73d65edac78257ec45fa8d28c062357b45844f8fef3723e4cfc3ed67fc8f3b18'
index={x['key']:x for x in json.loads(P.read_text())};rows=json.loads((A/'independent-first247-source-transcript.json').read_text())['rows'];cache={};out=[]
norm=lambda s:re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s).strip())
num=lambda v:None if v is None else Decimal(str(v))
for r in rows:
 k=r['sourceKey'];s=index[k]
 if k not in cache:
  assert sha(R/s['file'])==s['sha256'];assert sha(R/s['secondaryFile'])==s['secondarySha256']
  cache[k]=(json.loads(gzip.decompress((R/s['file']).read_bytes())),json.loads(gzip.decompress((R/s['secondaryFile']).read_bytes())))
 primary,secondary=cache[k];matches=[x for x in primary['rows']if x['row'][5]==r['physicalPage']and x['sourceRowOnPage']==r['sourceRowOnPage']]
 result={'id':r['id'],'sourceKey':k,'physicalPage':r['physicalPage'],'sourceRowOnPage':r['sourceRowOnPage'],'primarySnapshotSha256':s['sha256'],'secondarySnapshotSha256':s['secondarySha256']}
 if r['sourceRowOnPage']is None:
  assert not matches;result.update({'status':'primary-row-missing-comma-grammar-flag-source-transcript-supplies-literal','independentSourceReading':{k:r[k]for k in ['literalName','remuneration','expenses']},'secondaryFlags':secondary['flags']})
 else:
  assert len(matches)==1,(r['id'],len(matches));c=matches[0];v=c['row'];differences=[]
  if norm(r['literalName'])!=norm(v[1]):differences.append({'field':'name','independentFirst':r['literalName'],'candidate':v[1]})
  if num(r['remuneration'])!=num(v[3]):differences.append({'field':'remuneration','independentFirst':r['remuneration'],'candidate':v[3]})
  if num(r['expenses'])!=num(v[4]):differences.append({'field':'expenses','independentFirst':r['expenses'],'candidate':v[4]})
  result.update({'status':'exact-fields-match'if not differences else'differences-requiring-fresh-source-reread','candidateRow':v,'candidateRawLine':c['rawLine'],'differences':differences})
 out.append(result)
result={'firstTranscriptSha256':sha(A/'independent-first247-source-transcript.json'),'candidateIndexSha256':sha(P),'normalization':'Trim and repeated-space collapse, comma-adjacent spacing only; internal word boundaries/punctuation otherwise exact. Decimal value comparisons; dash null distinct from printed zero.','targets':out,'counts':{'targets':247,'matches':sum(x['status']=='exact-fields-match'for x in out),'differences':sum(x['status']=='differences-requiring-fresh-source-reread'for x in out),'missingPrimaryRows':sum(x['sourceRowOnPage']is None for x in out)},'noOutreach':True}
p=A/'first247-candidate-comparison.json';assert not p.exists();p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(result['counts']);print(json.dumps([x for x in out if x.get('differences')],ensure_ascii=False,indent=2))
