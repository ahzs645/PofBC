#!/usr/bin/env python3
"""Deterministic extraction of early official Public Accounts salary tables."""
from pathlib import Path
import re,json,gzip,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'research/salaries/provincial-early-administration'
# Verified physical PDF page, column boundary, and right edges of numeric columns.
CONFIG={'1999-00':[(8,67,[38,48],[103,115,128])],'2000-01':[(9,62,[33,43],[98,110,123])],'2001-02':[(10,61,[29,42,56],[97,109,121]),(11,0,[],[36,48,62])],'2002-03':[(9,88,[44,61,79],[141,159])],'2003-04':[(9,87,[49,65,78],[131,148])],'2004-05':[(11,97,[49,69,87],[159,180])],'2005-06':[(13,97,[49,69,88],[154,174])]}
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def parse_half(line,start,end,edges,page,kind):
 s=line[start:end];m=re.search(r'\s{2,}(?=\d)',s)
 if not m:return None
 name=s[:m.start()].strip()
 if not name or ',' not in name:return None
 name=re.sub(r'(?<=[A-Za-z])([345])$','',name)
 if not re.fullmatch(r"[A-Za-z ,.'’–\-]+",name):raise ValueError('Unexpected name '+repr(name))
 numbers=[None]*len(edges)
 for n in re.finditer(r'\d[\d,]*',s[m.end():]):
  right=start+m.end()+n.end();i=min(range(len(edges)),key=lambda i:abs(edges[i]-right))
  if abs(edges[i]-right)>2 or numbers[i] is not None:raise ValueError((page,kind,name,right,edges))
  numbers[i]=int(n.group().replace(',',''))
 if numbers[0] is None:raise ValueError('No salary '+name)
 return {'name':name,'amounts':numbers,'page':page,'sourceLine':line}
def parse(text,label):
 pages=text.split('\f');records={'ministers':[],'deputies':[]};excerpts=[]
 for page,split,left,right in CONFIG[label]:
  p=pages[page-1];excerpts.append(p)
  for line in p.splitlines():
   if left:
    r=parse_half(line,0,split,left,page,'ministers')
    if r:records['ministers'].append(r)
   r=parse_half(line,split,len(line),right,page,'deputies')
   if r:records['deputies'].append(r)
 for kind,rs in records.items():
  if len({r['name'] for r in rs})!=len(rs):raise ValueError('Duplicate name')
 return records,excerpts
# Printed table totals, independently read from the original table's total lines.
CONTROLS={'1999-00':{'ministers':[789538,844692],'deputies':[4061942,None,697039]},'2000-01':{'ministers':[768678,792826],'deputies':[5081320,None,903201]},'2001-02':{'ministers':[951602,262477,838738],'deputies':[7193569,20505,668338]},'2002-03':{'ministers':[794512,428321,1023155],'deputies':[6150575,937265]},'2003-04':{'ministers':[986514,398305,1103805],'deputies':[6936539,897295]},'2004-05':{'ministers':[973769,294040,1271779],'deputies':[6600412,946931]},'2005-06':{'ministers':[904304,274503,979988],'deputies':[7533730,1089461]}}
def normalize(rs,kind,label):
 rows=[]
 for r in rs:
  a=r['amounts'];salary=a[0];expenses=a[-1]
  if kind=='deputies' and len(a)==3:salary+=a[1] or 0
  if kind=='ministers' and len(a)==3:expenses=sum(x or 0 for x in a[1:]) if any(x is not None for x in a[1:]) else None
  position='Premier or minister · executive salary component' if kind=='ministers' else 'Deputy minister or associate deputy minister'
  if kind=='deputies' and label in ('2002-03','2003-04') and r['name'].startswith('CAMPBELL, D '):position+=' · contracted services paid to D Scott Campbell and Associates Inc'
  rows.append(['provincial-cabinet' if kind=='ministers' else 'public-service',r['name'],position,salary,expenses,r['page']])
 return rows
def main():
 sources=[]
 for label in CONFIG:
  original=BASE/'originals'/(label+'.pdf');b=original.read_bytes();text=subprocess.check_output(['pdftotext','-layout',str(original),'-']).decode();records,excerpts=parse(text,label)
  (BASE/(label+'.tables.txt')).write_text('\f'.join(excerpts));dump(BASE/(label+'.audit.json'),records)
  for kind,rs in records.items():
   sums=[sum((r['amounts'][i] or 0) for r in rs) for i in range(len(rs[0]['amounts']))]
   for i,n in enumerate(CONTROLS[label][kind]):
    expected_delta=([-1,2,-4] if kind=='ministers' else [1,-1])[i] if label=='2003-04' else 0
    if n is not None and sums[i]-n!=expected_delta:raise ValueError((label,kind,'Unreviewed printed total discrepancy',sums,CONTROLS[label][kind]))
   rows=normalize(rs,kind,label);stem=label+'-'+kind;payload=gzip.compress(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);(BASE/(stem+'.json.gzip')).write_bytes(payload)
   first=int(label[:4]);year=f'{first}/{label[-2:]}'
   notes=['Payments for the stated fiscal year, not annual salary rates. Published initials and spelling are preserved; no cross-source identity joins.','Travel and capital city allowances are expenses, not salary. Missing expense amounts remain null.']
   if label=='2003-04':notes.append('The sum of displayed rows differs slightly from printed totals: cabinet columns by -1, +2, -4 dollars; deputy columns by +1, -1 dollars. Every row was independently checked against raw PDF extraction. Displayed amounts are retained without balancing adjustments. This is the published errata page, including corrected Joyce Murray salary of $38,717.')
   if kind=='ministers':notes.append('Executive salary component only; member compensation is additional and not included here.')
   elif first<=2001:notes.append('Remuneration includes salary plus the separately disclosed deferred compensation column. Columns are retained separately in the audit.')
   if kind=='deputies' and first in (2002,2003):notes.append('D Scott Campbell compensation was paid to his corporation for contracted interim deputy/CIO services, as explicitly footnoted in the report; it is not employee payroll.')
   sources.append(dict(id='provincial-early-'+stem,employerSlug=rows[0][0],employerName='Premier and ministers' if kind=='ministers' else 'Provincial government',sector='Government',year=year,periodType='fiscal',periodStart=f'{first}-04-01',periodEnd=f'{first+1}-03-31',file=stem+'.json.gzip',originalFile='originals/'+label+'.pdf',auditFile=label+'.audit.json',title=f'Public Accounts {year}: '+('Premier and ministers executive salary' if kind=='ministers' else 'Deputy and associate deputy salary and compensation'),sourceUrl=f'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/{label}/pa-{label}-crf-detailed-schedules-of-payments.pdf',sha256=sha(b),dataSha256=sha(payload),rowCount=len(rows),totalRemuneration=sum(r[3] for r in rows),totalDisclosedExpenses=sum(r[4] or 0 for r in rows),category='minister-executive-salary' if kind=='ministers' else 'deputy-minister-remuneration',scope='minister-executive-salary' if kind=='ministers' else 'deputy-minister-remuneration',threshold=None,currency='CAD',status='verified',verifiedOn='2026-11-06',completeEmployeeSchedule=False,notes=notes,validation={'physicalPdfPages':sorted({r[5] for r in rows}),'publishedColumnTotals':CONTROLS[label][kind],'parsedColumnTotals':sums,'allPublishedColumnTotalsReconciled':label!='2003-04','publishedTotalDeltas':[None if n is None else sums[i]-n for i,n in enumerate(CONTROLS[label][kind])]}))
 dump(BASE/'sources.json',{'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'coverageNotes':['Early official salary tables 1999/00–2005/06 only. No overlap with existing 2006/07+ catalogue imports.','Cabinet executive salary and administration deputy compensation are separate scopes; neither is the complete public-service employee population.'],'sources':sources})
 print([(s['year'],s['category'],s['rowCount']) for s in sources]);print('Total',sum(s['rowCount'] for s in sources))
if __name__=='__main__':main()
