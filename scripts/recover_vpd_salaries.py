#!/usr/bin/env python3
"""Offline reproducible VPD recovery; originals and reviewed transcriptions pinned."""
import csv,gzip,hashlib,json,re,subprocess
from collections import Counter,defaultdict
from decimal import Decimal
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/vpd-recovery'
PIN={'2009-anonymous.pdf':'a63fbd8b8541b1ad60f2bf4a985b8d4b564dbe30b6a7ae4854d69abf9937e8dd','2009-names.pdf':'41031612c9bb869a7a31da9050940bb312079594abc1e21cfa9fbd4fef102e9c','2025-executive.pdf':'07159ec47dcd33f2f3d4579bd9d4707497af3d67388e6d66a355d0b23e6c3375'}
URL={'2009-anonymous.pdf':'https://vpd.ca/wp-content/uploads/2021/06/foi-vpd-salaries-all-75000-and-above-1.pdf','2009-names.pdf':'https://vpd.ca/wp-content/uploads/2021/06/foi-2009-remuneration-and-expenses-names-1.pdf','2025-executive.pdf':'https://vpd.ca/wp-content/uploads/2026/05/foi-2025-vpd-executive-remuneration.pdf'}
def sha(b):return hashlib.sha256(b).hexdigest()
def money(x):return None if x=='-' else float(Decimal(x.replace(',','')))
def total(rows,at):return float(sum((Decimal(str(r[at])) for r in rows if r[at] is not None),Decimal(0)))
def write_json(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def write_gz(path,obj):
 data=(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode();b=gzip.compress(data,mtime=0);path.write_bytes(b);return sha(b)
def parse_anonymous():
 p=OUT/'originals/2009-anonymous.pdf';text=subprocess.check_output(['pdftotext','-layout',str(p),'-']).decode();assert '2009 - December 31, 2009' in text
 rows=[]
 for page,t in enumerate(text.split('\f'),1):
  for line in t.splitlines():
   m=re.fullmatch(r'\s*([\d,]+\.\d\d)\s+([\d,]+\.\d\d|-)\s*',line)
   if m:rows.append(['vancouver-police',None,None,money(m[1]),money(m[2]),page])
 # Independent coordinate grouping, not the same text line segmentation.
 alternate=[]
 for page,pg in enumerate(fitz.open(p),1):
  groups=defaultdict(list)
  for w in pg.get_text('words'):
   if re.fullmatch(r'[\d,]+\.\d\d|-',w[4]):groups[round(w[1],1)].append(w)
  for y,words in sorted(groups.items()):
   words=sorted(words,key=lambda w:w[0])
   if len(words)==1 and words[0][4]=='-':continue # year-range header dash
   assert len(words)==2,(page,words)
   alternate.append(['vancouver-police',None,None,money(words[0][4]),money(words[1][4]),page])
 assert rows==alternate;assert len(rows)==1212
 return rows

def remove_named_overlap(anonymous,named):
 locations=defaultdict(list)
 for i,r in enumerate(anonymous):locations[tuple(r[3:5])].append(i)
 excluded=set();ledger=[]
 for n,r in enumerate(named):
  matches=locations[tuple(r[3:5])]
  assert len(matches)==1,('Ambiguous or missing named overlap',r,matches)
  i=matches[0];assert i not in excluded;excluded.add(i)
  ledger.append({'anonymousRowIndex':i,'anonymousPage':anonymous[i][5],'namedRowIndex':n,'namedPage':r[5],'publishedName':r[1],'remuneration':r[3],'expenses':r[4],'decision':'Import named release row once; exclude matching anonymous monetary observation from additive cohort.'})
 return [r for i,r in enumerate(anonymous) if i not in excluded],ledger

def build():
 for file,pin in {'2009-names-transcription.tsv':'2a6c2d1d05be00220aa5e77f8fdf7a196a306652efc87705ccd87a112d084dae','2025-executive-transcription.json':'018eb0a0616a09fc46f1766568dfdb95f00239b4f3c4926227e658ed3fb35d40'}.items():assert sha((OUT/file).read_bytes())==pin,file
 for file,pin in PIN.items():assert sha((OUT/'originals'/file).read_bytes())==pin,file
 anonymous=parse_anonymous();named=[]
 for r in csv.DictReader((OUT/'2009-names-transcription.tsv').read_text().splitlines(),delimiter='\t'):
  named.append(['vancouver-police',r['name'],r['position'],money(r['remuneration']),money(r['expenses']),int(r['page'])])
 assert len(named)==87
 residual,ledger=remove_named_overlap(anonymous,named);assert len(residual)==1125
 for at in [3,4]:assert total(anonymous,at)==round(total(residual,at)+total(named,at),2)
 executives=[['vancouver-police',*r,1] for r in json.loads((OUT/'2025-executive-transcription.json').read_text())['rows']];assert len(executives)==25
 overlap_hash=write_gz(OUT/'evidence/overlap-ledger.json.gzip',ledger)
 all_hash=write_gz(OUT/'evidence/2009-anonymous-complete.json.gzip',anonymous)
 sources=[]
 for label,year,rows,original,category,scope in [('2009-anonymous-residual','2009',residual,'2009-anonymous.pdf','employee-remuneration','Anonymous employee remuneration over $75,000 after removing 87 observations separately disclosed by name'),('2009-named','2009',named,'2009-names.pdf','employee-remuneration','87 publicly named employees disclosed in response to OIPC Order F10-22; subset of full anonymous schedule'),('2025-executives','2025',executives,'2025-executive.pdf','executive-only','Published executive remuneration and expenses only')]:
  file=label+'.json.gzip';data_hash=write_gz(OUT/file,rows)
  sources.append({'id':'vpd-recovery-'+label,'employerSlug':'vancouver-police','employerName':'Vancouver Police','sector':'Municipal police','year':year,'periodType':'calendar','periodStart':year+'-01-01','periodEnd':year+'-12-31','category':category,'scope':scope,'completeEmployeeSchedule':False,'title':'Vancouver Police '+label.replace('-',' '),'sourceUrl':URL[original],'sourceIndexUrl':'https://vpd.ca/about-the-vpd/published-freedom-of-information-requests/','sha256':PIN[original],'originalFile':'originals/'+original,'file':file,'dataSha256':data_hash,'rowCount':len(rows),'totalRemuneration':total(rows,3),'totalExpenses':total(rows,4),'totalKnownExpenses':total(rows,4),'totalExpensesComplete':all(r[4] is not None for r in rows),'pages':sorted(set(r[5] for r in rows)),'status':'verified','sourceKind':'official-pdf','verifiedOn':'2026-11-06','currency':'CAD','amountUnit':'dollars','threshold':75000 if year=='2009' else None,'notes':['Published expense dashes remain null, not zero. Remuneration is a disclosed payment amount, not an annual base salary rate.','2009 full anonymous schedule and named OIPC subset overlap: 87 exact unique remuneration/expense tuple matches are imported only from named release; unmatched anonymous rows retain null names. No redacted identity is inferred.' if year=='2009' else 'Executive-only disclosure; not a complete sworn or civilian workforce schedule. Original heading says Salary; its composition is not further defined.'],'validation':{'method':'Independent Poppler layout and PyMuPDF coordinate extraction agree on all 1,212 original anonymous rows; complete visual review of 87 named scan rows and 25 executive scan rows.','printedAggregateControls':None,'aggregateControlAvailability':'No printed sum is present; computed sums are not represented as source totals.','missingExpenses':sum(r[4] is None for r in rows),'overlapLedger':'evidence/overlap-ledger.json.gzip','overlapLedgerSha256':overlap_hash}})
 manifest={'version':1,'reviewed':'2026-11-06','rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'coverageNotes':['1,237 net additive observations: 1,125 anonymous and 87 named in 2009, plus 25 executives in 2025. The 1,324 gross source rows contain 87 duplicate monetary disclosures.'],'sources':sources}
 write_json(OUT/'sources.json',manifest)
 write_json(OUT/'validation.json',{'grossSourceRows':1324,'overlappingNamedRows':87,'netAcceptedRows':1237,'anonymous2009Rows':1212,'remainingAnonymous2009Rows':1125,'named2009Rows':87,'executives2025Rows':25,'fullAnonymousEvidenceSha256':all_hash,'full2009Remuneration':total(anonymous,3),'full2009KnownExpenses':total(anonymous,4),'net2009Remuneration':total(residual+named,3),'net2009KnownExpenses':total(residual+named,4),'rowsByAnonymousPhysicalPage':dict(Counter(r[5] for r in anonymous)),'sourceReceipts':[{'url':URL[f],'file':'originals/'+f,'sha256':pin,'bytes':(OUT/'originals'/f).stat().st_size,'retrievedOn':'2026-11-06'} for f,pin in PIN.items()]})
 return manifest
if __name__=='__main__':print(json.dumps({s['id']:s['rowCount'] for s in build()['sources']},indent=2))
