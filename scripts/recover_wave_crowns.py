#!/usr/bin/env python3
"""Original-backed Crown employee schedules with independent positioned and layout readers."""
from __future__ import annotations
import argparse,collections,gzip,hashlib,json,re,subprocess
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/recovery-crowns'
REVIEW=ROOT/'research/salaries/recovery-wave-2026-11-01/crowns'
NUMBER=r'(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?'
AMOUNT=rf'(?:[-−]?{NUMBER}|\({NUMBER}\)|[-‐–—])'
MONEY=re.compile('^'+AMOUNT+'$')
EXCLUDED=('Accruals,','in 15 months,','and therefore,','British Columbia','Schedule ','For the ','Please note','Consolidated','Employees earning','Total','Subtotal','Employer portion','Employee Name','Employee (','The schedule','C.P.P','E.I.')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def amount(value):
 value=value.strip().replace('$','').replace('−','-')
 if value in ['', '-', '‐', '–', '—']:return None
 if not MONEY.fullmatch(value):raise ValueError('Invalid currency cell '+repr(value))
 negative=value.startswith('(');number=Decimal(value.strip('()').replace(',',''))
 if negative:number=-number
 return int(number) if number==number.to_integral() else float(number)
def total(values):return float(sum((Decimal(str(v)) for v in values if v is not None),Decimal(0)))
def person(label):return ',' in label and not label.startswith(EXCLUDED)

def parse_layout(text,transition=False):
 """Read row boundaries from Poppler's independently inferred text columns."""
 cells=4 if transition else 2
 pattern=re.compile(r'^\s*(.+?)\s{2,}'+r'\s+'.join(r'\$?\s*('+AMOUNT+r')' for _ in range(cells))+r'\s*$')
 rows=[];components=[]
 for line in text.splitlines():
  match=pattern.fullmatch(line)
  if not match:continue
  name=' '.join(match[1].split())
  if not person(name):continue
  values=[amount(v) for v in match.groups()[1:]]
  pay,expense=values[-2:]
  if pay is None:raise ValueError('Missing disclosed remuneration: '+name)
  rows.append([name,pay,expense]);components.append(values)
 return rows,components

def parse_words(words,transition=False):
 """Use word geometry, without Poppler lines or their text-column boundaries."""
 lines=[]
 for word in sorted(words,key=lambda w:(w[1],w[0])):
  if not lines or abs(word[1]-lines[-1][0])>1.8:lines.append([word[1],[word]])
  else:lines[-1][1].append(word)
 rows=[];proof=[];expected=4 if transition else 2
 for y,line in lines:
  line.sort(key=lambda w:w[0]);tokens=[w[4] for w in line if w[4]!='$']
  numbers=[n for n,t in enumerate(tokens) if MONEY.fullmatch(t.replace('$',''))]
  if not numbers:continue
  name=' '.join(tokens[:numbers[0]])
  if not person(name):continue
  if len(numbers)!=expected or numbers!=list(range(len(tokens)-expected,len(tokens))):raise ValueError('Unexpected row columns '+repr(tokens))
  values=[amount(t) for t in tokens[-expected:]];pay,expense=values[-2:]
  if pay is None:raise ValueError('Missing remuneration '+name)
  if transition and all(v is not None for v in values[:3]) and values[0]+values[1]!=values[2]:raise ValueError('Transition components conflict '+name)
  rows.append([name,pay,expense]);proof.append({'y':y,'words':line,'componentsAndExpenses':values})
 return rows,proof

def extract(spec,fetch=False):
 import fitz
 p=Path(spec['localPath'])
 if not p.exists() and fetch:
  import urllib.request
  request=urllib.request.Request(spec['sourceUrl'],headers={'User-Agent':'Mozilla/5.0 PofBC official source verification'})
  with urllib.request.urlopen(request,timeout=45) as response:raw=response.read()
  if not raw.startswith(b'%PDF-') or sha(raw)!=spec['sha256']:raise ValueError('Fetched original changed; renewed review required')
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 raw=p.read_bytes()
 if sha(raw)!=spec['sha256']:raise ValueError('Original changed '+spec['id'])
 d=fitz.open(p);pages=[]
 for pn in spec['pages']:
  page=d[pn-1]
  layout=subprocess.check_output(['pdftotext','-f',str(pn),'-l',str(pn),'-layout',str(p),'-']).decode()
  pages.append({'pdfPage':pn,'text':page.get_text(),'words':page.get_text('words'),'popplerLayoutText':layout})
 return {'sourceId':spec['id'],'sourceSha256':sha(raw),'pdfPages':len(d),'pages':pages}

def replay(spec,evidence):
 if evidence['sourceSha256']!=spec['sha256']:raise ValueError('Evidence source changed')
 if [p['pdfPage'] for p in evidence['pages']]!=spec['pages']:raise ValueError('Employee page set changed')
 rows=[];counts=[]
 for page in evidence['pages']:
  a,proof=parse_words(page['words'],spec.get('transition',False));b,components=parse_layout(page['popplerLayoutText'],spec.get('transition',False))
  if a!=b:
   only_a=list((collections.Counter(map(tuple,a))-collections.Counter(map(tuple,b))).elements());only_b=list((collections.Counter(map(tuple,b))-collections.Counter(map(tuple,a))).elements())
   raise ValueError(f"{spec['id']} p{page['pdfPage']}: readers disagree {len(a)}/{len(b)} {only_a[:3]} / {only_b[:3]}")
  rows.extend([[spec['employerSlug'],name,None,pay,expense,page['pdfPage']] for name,pay,expense in a]);counts.append([page['pdfPage'],len(a)])
  page['rowEvidence']=proof
 if not rows:raise ValueError('Empty employee cohort')
 if spec.get('rowCount') is not None and len(rows)!=spec['rowCount']:raise ValueError('Changed employee row count')
 sums=[total(r[3] for r in rows),total(r[4] for r in rows)]
 if spec.get('sums') is not None and sums!=spec['sums']:raise ValueError('Changed disclosed sums')
 return rows,{'rowCountsByPdfPage':counts,'namedRemunerationSum':sums[0],'knownNamedExpensesSum':sums[1],'missingExpenseRows':sum(r[4] is None for r in rows),'explicitZeroExpenseRows':sum(r[4]==0 for r in rows),'completeEmployeeSchedule':True,'independentReaderAgreement':True,'controls':spec.get('controls'),'controlDefinitions':spec.get('controlDefinitions'),'residuals':[float(Decimal(str(s))-Decimal(str(c))) if c is not None else None for s,c in zip(sums,spec.get('controls',[None,None]))]}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--offline',action='store_true');parser.add_argument('--verify',action='store_true');parser.add_argument('--fetch',action='store_true',help='Retrieve missing originals only, requiring pinned PDF hashes');args=parser.parse_args()
 specs=json.loads((REVIEW/'source-specs.json').read_text());sources=[];outputs={}
 for spec in specs:
  evidence=json.loads(gzip.decompress((OUT/spec['evidenceFile']).read_bytes())) if args.offline else extract(spec,args.fetch)
  rows,validation=replay(spec,evidence)
  source={k:spec[k] for k in ['id','employerSlug','employerName','year','periodType','periodStart','periodEnd','sourceUrl','sourceIndexUrl','sha256','file','evidenceFile']}
  data=gzip.compress(encode(rows),mtime=0);ev=gzip.compress(encode(evidence),mtime=0)
  source.update(sourceKind='official',sector='Crown corporations',category='employee-remuneration',scope='named-employees-over-threshold',threshold=75000,thresholdComparison='>',title=spec['title'],rowCount=len(rows),dataSha256=sha(data),evidenceSha256=sha(ev),totalRemuneration=validation['namedRemunerationSum'],totalExpenses=validation['knownNamedExpensesSum'],status=spec.get('status','held-for-peer-review'),verifiedOn='2026-11-01',completeEmployeeSchedule=True,notes=spec['notes'],validation=validation,nameDisclosure='published-initials' if spec['year']=='2020' else 'published-full-name',positionDisclosure='not-published',currency='CAD')
  if spec.get('approvalEvidence'):validation['originalApprovalAndControls']=spec['approvalEvidence']
  if spec.get('publicWarning'):source['publicWarning']=spec['publicWarning']
  if spec.get('retainCompiledPartition'):
   source['retainCompiledPartition']=True;validation.update(compiledPartitionRetained=True,compiledPartitionRetentionReason=spec['compiledPartitionRetentionReason'])
  sources.append(source);outputs[spec['file']]=data;outputs[spec['evidenceFile']]=ev
  print(json.dumps({'id':spec['id'],'rows':len(rows),'sums':spec.get('sums') or [validation['namedRemunerationSum'],validation['knownNamedExpensesSum']],'residuals':validation['residuals']}),flush=True)
 rule_path=REVIEW/'calendar-replacement.json'
 rules=[json.loads(rule_path.read_text())] if rule_path.exists() else []
 outputs['sources.json']=(json.dumps({'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources,'compiledReplacements':rules},ensure_ascii=False,indent=2)+'\n').encode()
 for name,raw in outputs.items():
  path=OUT/name
  if args.verify:
   if path.read_bytes()!=raw:raise ValueError('Committed output changed '+name)
  else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)

if __name__=='__main__':main()
