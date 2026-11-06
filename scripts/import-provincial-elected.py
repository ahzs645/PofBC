#!/usr/bin/env python3
"""Offline deterministic provincial elected CSV normalization. Never downloads at build time."""
import csv, gzip, hashlib, io, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/salaries/provincial-elected'
def digest(b): return hashlib.sha256(b).hexdigest()
def decode(b):
 try: return b.decode('utf-8-sig')
 except UnicodeDecodeError: return b.decode('cp1252')
def amount(s):
 s=s.strip().replace(',','').replace('$','')
 if s in ('','-','–','—','#N/A'): return None
 if re.fullmatch(r'\(\d+(?:\.\d{1,2})?\)',s): s='-'+s[1:-1]
 if not re.fullmatch(r'-?\d+(?:\.\d{1,2})?',s): raise ValueError('Invalid amount: '+repr(s))
 return round(float(s),2)
def total(xs): return round(sum(x or 0 for x in xs),2)
def parse_mla(b):
 raw=list(csv.reader(io.StringIO(decode(b))));hi=next(i for i,r in enumerate(raw) if r and r[0].strip()=='Member');head=[x.strip() for x in raw[hi]]
 pay=next(i for i,h in enumerate(head) if 'Compensation' in h or h=='Amount');const=head.index('Constituency');allow=head.index('Allowance') if 'Allowance' in head else None
 liv=next((i for i,h in enumerate(head) if 'Living Allowance' in h),None);travel=next((i for i,h in enumerate(head) if h=='Travel'),None)
 people={};components=[];unattributed=[];current=None
 for i,r in enumerate(raw[hi+1:],hi+2):
  r += ['']*(len(head)-len(r));name=r[0].strip()
  if not name:
   if any(x.strip() for x in r): unattributed.append({'csvRecord':i,'fields':r})
   continue
  role=r[allow].strip() if allow is not None else ''
  if name.startswith('Allowance as '):
   if allow is not None or not current: raise ValueError('Unexpected continuation allowance')
   role=name;name=current
  elif ',' not in name: raise ValueError('Unexpected member: '+name)
  else: current=name
  p=amount(r[pay]);l=amount(r[liv]) if liv is not None else None;t=amount(r[travel]) if travel is not None else None
  if p is None and l is None and t is None:
   unattributed.append({'csvRecord':i,'fields':r,'reason':'Published named row with no numeric payments'});continue
  entry=people.setdefault(name,{'constituencies':[],'pay':[],'expenses':[]})
  if r[const].strip() and r[const].strip() not in entry['constituencies']:entry['constituencies'].append(r[const].strip())
  entry['pay'].append(p)
  if l is not None or t is not None:entry['expenses'].append(total([l,t]))
  components.append({'csvRecord':i,'name':name,'allowance':role or None,'compensation':p,'capitalCityLivingAllowance':l,'travel':t})
 rows=[['legislative-assembly-members',n,'Member of the Legislative Assembly'+(' · '+ ' / '.join(v['constituencies']) if v['constituencies'] else ''),total(v['pay']),total(v['expenses']) if v['expenses'] else None] for n,v in people.items() if any(x is not None for x in v['pay'])]
 # The 2021 CSV has a printed total followed by stray, unlabelled spreadsheet cells.
 printed=next((r for r in unattributed if amount(r['fields'][pay])==total(c['compensation'] for c in components)),None)
 if printed:
  for idx,key in [(liv,'capitalCityLivingAllowance'),(travel,'travel')]:
   if idx is not None and abs((amount(printed['fields'][idx]) or 0)-total(c[key] for c in components))>.01: raise ValueError('Printed expense control mismatch')
 return rows,{'components':components,'unattributedCellsExcluded':unattributed,'publishedTotalControl':printed,'componentCount':len(components),'distinctMemberCount':len(rows)}
def parse_ministers(b):
 raw=list(csv.reader(io.StringIO(decode(b))));hi=next(i for i,r in enumerate(raw) if any(x.strip()=='Salary' for x in r));head=[x.strip() for x in raw[hi]];pay=head.index('Salary');travel=next((i for i,h in enumerate(head) if 'Travel' in h),None);liv=next((i for i,h in enumerate(head) if 'Living Allowance' in h),None)
 rows=[];audit=[]
 for i,r in enumerate(raw[hi+1:],hi+2):
  r+=['']*(len(head)-len(r));name=r[0].strip()
  if not name:continue
  if ',' not in name: raise ValueError('Unexpected minister '+repr(name))
  p=amount(r[pay]);t=amount(r[travel]) if travel is not None else None;l=amount(r[liv]) if liv is not None else None
  if p is None:
   audit.append({'csvRecord':i,'name':name,'salary':None,'capitalCityLivingAllowance':l,'travel':t,'excludedReason':'Expense-only record; no numeric salary disclosed'});continue
  rows.append(['provincial-cabinet',name,'Premier or minister · executive salary component',p,total([l,t]) if l is not None or t is not None else None]);audit.append({'csvRecord':i,'name':name,'salary':p,'capitalCityLivingAllowance':l,'travel':t})
 return rows,{'components':audit,'componentCount':len(audit)}
def write_json(p,j):p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n')
def main():
 sources=[]
 for catalog,kind,parser,employer in [('catalogue.json','members',parse_mla,'Members of the Legislative Assembly'),('ministers-catalogue.json','ministers',parse_ministers,'Premier and ministers')]:
  for r in sorted(json.loads((BASE/'originals'/catalog).read_text())['result']['resources'],key=lambda r:r['name']):
   end=int(re.search(r'20\d\d',r['name'])[0]);year=f'{end-1}/{str(end)[2:]}';stem=f'{end-1}-{str(end)[2:]}-{kind}';original='originals/'+r['url'].split('/')[-1];b=(BASE/original).read_bytes();rows,audit=parser(b)
   payload=gzip.compress(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);(BASE/(stem+'.json.gzip')).write_bytes(payload);write_json(BASE/(stem+'.audit.json'),audit)
   note='Member compensation includes role allowances; exact published names are aggregated within this schedule only. Negative adjustments are retained. Minister executive salary is disclosed separately and is not included.' if kind=='members' else 'Executive salary component only, in addition to member compensation. These records must not be presented as complete annual compensation or merged across names heuristically.'
   sources.append(dict(id='provincial-elected-'+stem,employerSlug=rows[0][0],employerName=employer,sector='Government',year=year,periodType='fiscal',periodStart=f'{end-1}-04-01',periodEnd=f'{end}-03-31',file=stem+'.json.gzip',originalFile=original,auditFile=stem+'.audit.json',title=f'{employer}: {year} '+('member compensation' if kind=='members' else 'executive salary'),sourceUrl=r['url'],sha256=digest(b),dataSha256=digest(payload),rowCount=len(rows),totalRemuneration=total(x[3] for x in rows),totalDisclosedExpenses=total(x[4] for x in rows),scope='elected-member-compensation' if kind=='members' else 'minister-executive-salary',category='elected-member-compensation' if kind=='members' else 'minister-executive-salary',threshold=None,currency='CAD',status='verified',verifiedOn='2026-11-06',completeEmployeeSchedule=False,notes=[note,'Fiscal payments, not annual salary rates. Missing expense values remain null.'],expensesNote='Disclosed capital city living allowance plus travel. Excluded from remuneration; missing amounts are not inferred as zero.',validation={'componentCount':audit['componentCount'],'sourceRowsPreservedInAudit':True,'publishedTotalReconciled':bool(audit.get('publishedTotalControl')),'normalization':'Exact-name within-source aggregation; no cross-source identity joins.'}))
 for source in sources:
  if source['id']=='provincial-elected-2022-23-ministers':
   source['notes'].append('Published salary amounts repeat the preceding fiscal-year salary vector while living allowances and travel differ. The original CSV explicitly states March 31, 2023; repetition is flagged, not silently corrected.')
   source['publicWarning']='Published executive salary values repeat 2021/22 despite a different reporting-year heading and expenses. Verify against the detailed PDF before drawing salary-change conclusions.'
 write_json(BASE/'sources.json',{'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses'],'coverageNotes':['Provincial elected compensation is separate from administration, appointee and Assembly employee disclosures.','Member catalogue has no FYE2008 resource; this gap is not silently filled.','Two complementary salary components use separate employers and sources, not combined total compensation.'], 'sources':sources})
 print(len(sources),'sources',sum(s['rowCount'] for s in sources),'observations')
if __name__=='__main__':main()
