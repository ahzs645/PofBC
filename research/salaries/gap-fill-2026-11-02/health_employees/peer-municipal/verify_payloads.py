import pathlib,json,gzip,hashlib,decimal,re
root=pathlib.Path('/workspace/PofBC'); a=root/'research/salaries/gap-fill-2026-11-02/health_employees/peer-municipal'; base=root/'research/salaries/gap-fill-municipal'; manifest=base/'sources.json'; source={s['id']:s for s in json.load(open(manifest))['sources']}; comp=json.load(open(a/'comparison-first-v1.json')); rowsVerified=0; out=[]
def num(v): return None if v in (None,'','-') else decimal.Decimal(str(v).replace(',',''))
def txt(v): return None if v is None else ' '.join(v.replace('*','').split())
for c in comp['comparisons']:
 s=source[c['sourceId']]; b=json.load(open(c['book'])); section=next(v for v in b['sections'] if v['sourceShaPrefix']==s['sha256'][:12] and v['scope']==s['scope']); data=json.load(gzip.open(base/s['file'],'rt')); assert len(data)==len(section['rows']); provenance=json.load(gzip.open(base/s['provenanceFile'],'rt'))
 for i,(r,literal) in enumerate(zip(data,section['rows']),1):
  expectedPay=num(literal['remunerationComponent'])
  if section.get('payIsSumOfRemunerationAndTaxableBenefits') and section.get('payRepresentation') != 'remuneration-column-excluding-separately-published-taxable-benefits':
   benefit=num(literal.get('taxableBenefits')); assert expectedPay is not None and benefit is not None; expectedPay+=benefit
  assert r[0]==s['employerSlug'] and r[1]==txt(literal['name']) and r[2]==txt(literal.get('position')),(s['id'],i,'identity',r,literal)
  assert num(r[3])==expectedPay and num(r[4])==num(literal.get('expenses')),(s['id'],i,'money',r,literal)
  assert r[5]==literal.get('physicalPage',section['physicalPage']),(s['id'],i,'page')
  rowsVerified+=1
 assert s['year']==section['year'] and s['periodStart']==section['year']+'-01-01' and s['periodEnd']==section['year']+'-12-31'
 assert s['validation']['compiledPartitionRetained'] is True
 out.append({'sourceId':s['id'],'rows':len(data),'payRule':'sum remuneration plus numeric separate taxable benefits' if section.get('payIsSumOfRemunerationAndTaxableBenefits') and section.get('payRepresentation') != 'remuneration-column-excluding-separately-published-taxable-benefits' else 'literal remuneration column only','numericZerosPreserved':sum(r[4]==0 for r in data),'missingExpensesPreserved':sum(r[4] is None for r in data),'dataSha256':s['dataSha256'],'provenanceSha256':s['provenanceSha256'],'periodChecked':True,'compiledRetained':True})
f=a/'normalized-payload-verification.json'; f.write_text(json.dumps({'manifestSha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'rowsVerified':rowsVerified,'sources':out,'errors':[],'noBalancing':True,'noOutreach':True},indent=2)+'\n'); print(rowsVerified,len(out),hashlib.sha256(f.read_bytes()).hexdigest())
