import json,gzip,pathlib,hashlib,re,decimal
root=pathlib.Path('/workspace/PofBC'); a=root/'research/salaries/gap-fill-2026-11-02/health_employees/peer-municipal'; m=root/'research/salaries/gap-fill-2026-11-02/municipal'; manifest=root/'research/salaries/gap-fill-municipal/sources.json'; booknames=['transcripts-middle-v2.json','transcripts-rossland-additional.json','transcripts-clearwater-2011-and-2017-2020.json','transcripts-final.json','transcripts-recovered-originals.json','transcripts-abbotsford-known-column.json']; books=[(n,json.load(open(m/n))) for n in booknames]; sources=json.load(open(manifest))['sources']; pin=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
idx=a/'first-transcript-index.json'; x=json.load(open(idx)); allDiffs=[]; comparisons=[]
def normal(v,key):
 if v in ('','-',None): return None
 if key not in ['name','position','expenseInclusiveTotalRawVisible']:
  try: return str(decimal.Decimal(str(v).replace(',','')).normalize())
  except: pass
 return re.sub(r'\s*,\s*',',',' '.join(str(v).split()))
for t in x['firstTranscripts']:
 f=root/t['path']; assert pin(f)==t['sha256']; first=json.load(open(f)); n=first['reportNumber']; sha=first['sourceSha256']
 for group,scope in [('council','elected-officials'),('employees','employee-remuneration')]:
  if not first.get(group): continue
  matches=[(bn,s) for bn,b in books for s in b['sections'] if s['sourceShaPrefix']==sha[:12] and s['scope']==scope]; assert len(matches)==1,(n,scope,len(matches)); bn,s=matches[0]
  rows=first[group]; assert len(rows)==len(s['rows'])
  if n<=4: keys=['name','position','remunerationComponent','taxableBenefits','expenses','expenseInclusiveTotal']
  elif n==6 and group=='employees': keys=['name','position','operationalRemuneration','emergencyResponseRemuneration','remunerationComponent','expenses']
  elif n in [12,13]: keys=['name','remunerationComponent','expenses','expenseInclusiveTotal']
  elif n==16: keys=['name','position','remunerationComponent','taxableBenefits','expenses']
  else: keys=['name','position','remunerationComponent','expenses']+(['expenseInclusiveTotalRawVisible'] if n==5 and group=='council' else ['expenseInclusiveTotal'] if n in [5,14] else [])
  local=[]
  for ri,(r,c) in enumerate(zip(rows,s['rows']),1):
   assert len(keys)==len(r),(n,group,len(keys),len(r))
   for k,v in zip(keys,r):
    if normal(v,k)!=normal(c.get(k),k): local.append({'row':ri,'field':k,'sourceFirst':v,'candidate':c.get(k)})
  source=[v for v in sources if v['sha256']==sha and v['scope']==scope]; assert len(source)==1
  z=source[0]; base=manifest.parent
  for field,hkey in [('file','dataSha256'),('provenanceFile','provenanceSha256')]: assert pin(base/z[field])==z[hkey]
  item={'reportNumber':n,'scope':scope,'sourceId':z['id'],'rowsCompared':len(rows),'fieldsCompared':keys,'firstTranscriptSha256':t['sha256'],'book':str(m/bn),'bookSha256':pin(m/bn),'payload':str(base/z['file']),'payloadSha256':z['dataSha256'],'provenance':str(base/z['provenanceFile']),'provenanceSha256':z['provenanceSha256'],'literalFieldDifferences':local}
  comparisons.append(item); allDiffs.extend([dict(reportNumber=n,scope=scope,**d) for d in local])
out={'firstIndexSha256':pin(idx),'manifestSha256':pin(manifest),'normalization':'trim/collapse repeated whitespace and comma-adjacent spaces only for text; decimal numeric formatting; blank/dash/null all missing for normalized fields with originals retained in immutable first transcripts. No internal word boundaries deleted.','comparisons':comparisons,'differences':allDiffs,'totalRows':sum(v['rowsCompared'] for v in comparisons)}
(a/'comparison-first-v1.json').write_text(json.dumps(out,indent=2)+'\n'); print('rows',out['totalRows'],'cohorts',len(comparisons),'diffs',len(allDiffs)); print(json.dumps(allDiffs,indent=2))
