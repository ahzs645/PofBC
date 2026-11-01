#!/usr/bin/env python3
"""Hash-pinned Crown salary extraction with two independent native PDF readers.

--offline replays retained positioned-word and Poppler text evidence, without
network or PDF/OCR dependencies. --verify compares with committed payload bytes.
"""
from __future__ import annotations
import argparse,collections,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/continuation-crowns'
RESEARCH=ROOT/'research/salaries/continuation-2026-11-01/crowns'
NUM=r'(?:\(?[-‐−]?\d[\d,]*(?:\.\d{2})?\)?|[-‐–—])'
CELL=re.compile(r'^'+NUM+r'$')
ROW=re.compile(r'^\s*(.+?)\s{2,}\$?\s*('+NUM+r')\s+\$?\s*('+NUM+r')\s*$')
EXCLUDED=['RECEIVER GEN. OF CANADA','RECEIVER GENERAL FOR CANADA']
def sha(b):return hashlib.sha256(b).hexdigest()
def compact(d):return (json.dumps(d,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def money(s):
 s=s.replace('$','').strip()
 if s in ['','-','‐','–','—']:return None
 if not CELL.fullmatch(s):raise ValueError('Invalid money: '+repr(s))
 neg=s.startswith('(');s=s.strip('()').replace(',','').replace('‐','-').replace('−','-');v=float(s) if '.' in s else int(s)
 return -v if neg else v

def valid_name(n,slug):
 if n.upper() in EXCLUDED:return False
 if re.search(r'\d|\$|[:;]',n):return False
 if slug=='bc-railway-company':return bool(re.match(r'[A-Z][a-zA-Z-]+ [A-Z]',n)) and not n.startswith(('Total ','British '))
 if slug in ['icbc','bclc']:return n.upper()==n and bool(re.search('[A-Z]',n)) and not n.startswith(('TOTAL','OTHER UNDER','GRAND TOTAL'))
 return (',' in n or n=='Celligoi R G') and not n.lower().startswith(('under ','total ','prepared '))

def parse_words(words,slug,two_columns=False,width=612,y_tolerance=1.6,transition=False):
 """Coordinate clustering, independent of PDF text-reading order."""
 result=[];evidence=[]
 panels=[(0,width/2),(width/2,width+1)] if two_columns else [(0,width+1)]
 for panel,(lo,hi) in enumerate(panels):
  groups=[]
  for w in sorted([w for w in words if lo<=w[0]<hi],key=lambda w:(w[1],w[0])):
   if not groups or abs(w[1]-groups[-1][0])>y_tolerance:groups.append([w[1],[w]])
   else:groups[-1][1].append(w)
  for y,ws in groups:
   ws.sort(key=lambda w:w[0]);tokens=[w[4] for w in ws if w[4] not in ['$','\x08']]
   # A row has a published name followed by exactly two monetary cells.
   inds=[i for i,t in enumerate(tokens) if CELL.fullmatch(t)]
   if len(inds)<2:continue
   first=inds[0];name=' '.join(tokens[:first]).strip()
   if not valid_name(name,slug):continue
   expected=4 if transition else 2
   if len(inds)!=expected or inds!=list(range(len(tokens)-expected,len(tokens))):raise ValueError(f'Unexpected monetary columns: {tokens!r}')
   row=[name,money(tokens[-2]),money(tokens[-1])]
   if row[1] is None or row[1]<=75000:raise ValueError(f'Employee threshold or column failure {row}')
   result.append(row);ev={'panel':panel,'y':y,'row':row,'words':ws}
   if transition:
    values=[money(v) for v in tokens[-4:]];ev.update({'calendar2016':values[0],'janToMar2017':values[1],'fifteenMonthTotal':values[2],'componentResidual':values[2]-values[0]-values[1] if all(v is not None for v in values[:3]) else None})
   evidence.append(ev)
 return result,evidence

def parse_layout(text,slug,two_columns=False,transition=False):
 """Poppler line/whitespace reader; does not use positioned-word coordinates."""
 result=[]
 lines=text.splitlines();split=None
 if two_columns:
  # Poppler prints the two table headings on one physical line.
  heads=[line for line in lines if line.count('EMPLOYEE NAME')==2]
  if not heads:
   if sum('EMPLOYEE NAME' in line for line in lines)!=1:raise ValueError('Employee heading absent')
   split=max(map(len,lines))+1
  else:split=heads[0].index('EMPLOYEE NAME',heads[0].index('EMPLOYEE NAME')+1)
 for panel in range(2 if two_columns else 1):
  for line in lines:
   part=(line[:split] if panel==0 else line[split:]) if two_columns else line
   pattern=re.compile(r'^\s*(.+?)\s{2,}('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s*$') if transition else ROW
   m=pattern.fullmatch(part)
   if not m:continue
   name=' '.join(m[1].split())
   if not valid_name(name,slug):continue
   row=[name,money(m[4]),money(m[5])] if transition else [name,money(m[2]),money(m[3])]
   if row[1] is None or row[1]<=75000:raise ValueError(f'Unexpected remuneration {row}')
   result.append(row)
 return result

def parse_board_words(words,name_end,position_end):
 rows=[];control=None;evidence=[]
 anchors=[w for w in words if w[0]<name_end and w[4].startswith('(') and w[4].endswith(')')]
 for anchor in sorted(anchors,key=lambda w:w[1]):
  line=sorted([w for w in words if abs(w[1]-anchor[1])<1.6],key=lambda w:w[0])
  amounts=[money(w[4]) for w in line if re.fullmatch(r'\$[\d,]+',w[4])]
  if len(amounts)<3:continue
  name=' '.join(w[4] for w in line if w[0]<name_end)
  position=' '.join(w[4] for w in line if name_end<=w[0]<position_end)
  if sum(amounts[:-1])!=amounts[-1]:raise ValueError('Board remuneration component mismatch')
  row=[name,position,amounts[-1]];rows.append(row);evidence.append({'row':row,'monetaryComponentsAndTotal':amounts,'words':line})
 for anchor in [w for w in words if w[4]=='Total' and w[0]<name_end]:
  line=sorted([w for w in words if abs(w[1]-anchor[1])<1.6],key=lambda w:w[0])
  if 'Total Board Member Remuneration' in ' '.join(w[4] for w in line):
   values=[money(w[4]) for w in line if re.fullmatch(r'\$[\d,]+',w[4])];control=values[-1]
 return rows,control,evidence

def parse_board_layout(text):
 rows=[];control=None
 for line in text.splitlines():
  amounts=[money(v) for v in re.findall(r'\$[\d,]+',line)]
  if line.strip().startswith('Total Board Member Remuneration'):
   control=amounts[-1];continue
  m=re.fullmatch(r'\s*(.+?\))\s{2,}(.+?)\s{2,}(.+)',line)
  if m and len(amounts)>=3:
   if sum(amounts[:-1])!=amounts[-1]:raise ValueError('Independent board component mismatch')
   rows.append([' '.join(m[1].split()),' '.join(m[2].split()),amounts[-1]])
 return rows,control

def extract(spec,offline=False,fetch=False):
 if offline:return json.loads(gzip.decompress((OUT/spec['evidenceFile']).read_bytes()))
 import fitz
 p=Path(spec['localPath'])
 if not p.exists() and fetch:
  import urllib.request
  with urllib.request.urlopen(urllib.request.Request(spec['url'],headers={'User-Agent':'Mozilla/5.0 public salary source verification'}),timeout=60) as response:download=response.read()
  if sha(download)!=spec['sha256']:raise ValueError('Fetched original changed; re-review required')
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(download)
 raw=p.read_bytes()
 if sha(raw)!=spec['sha256']:raise ValueError('Original bytes changed: '+spec['id'])
 doc=fitz.open(p);pages=[]
 for pn in spec['pages']:
  pg=doc[pn-1];layout=subprocess.run(['pdftotext','-f',str(pn),'-l',str(pn),'-layout',str(p),'-'],capture_output=True,check=True).stdout.decode()
  pages.append({'pdfPage':pn,'width':pg.rect.width,'text':pg.get_text(),'words':pg.get_text('words'),'popplerLayoutText':layout})
 return {'sourceId':spec['id'],'originalPdfSha256':sha(raw),'pdfBytes':len(raw),'periodEvidence':spec['periodEvidence'],'pages':pages}

def replay(spec,ev):
 if ev['originalPdfSha256']!=spec['sha256']:raise ValueError('Evidence source fingerprint differs')
 rows=[];page_counts=[]
 for p in ev['pages']:
  board=spec.get('parser')=='bcfma-board'
  if board:a,control,proof=parse_board_words(p['words'],spec['nameBoundary'],spec['positionBoundary'])
  else:a,proof=parse_words(p['words'],spec['employerSlug'],spec.get('twoColumns',False),p['width'],spec.get('wordYTolerance',1.6),spec.get('transition',False))
  layout=p['popplerLayoutText']
  for correction in spec.get('layoutCorrections',[]):
   if correction['pdfPage']==p['pdfPage']:
    if correction['before'] not in layout:raise ValueError('Reviewed layout correction no longer matches')
    layout=layout.replace(correction['before'],correction['after'])
  if board:
   b,independent_control=parse_board_layout(layout)
   if control!=independent_control or control!=spec['controls'][0]:raise ValueError('Board control readers disagree')
  else:b=parse_layout(layout,spec['employerSlug'],spec.get('twoColumns',False),spec.get('transition',False))
  if a!=b:
   diff=list((collections.Counter(map(tuple,a))-collections.Counter(map(tuple,b))).elements());diff2=list((collections.Counter(map(tuple,b))-collections.Counter(map(tuple,a))).elements())
   raise ValueError(f"Independent disagreement {spec['id']} p{p['pdfPage']}: {len(a)} vs {len(b)} {diff[:5]} {diff2[:5]}")
  rows.extend([[spec['employerSlug'],r[0],r[1],r[2],None,p['pdfPage']] if board else [spec['employerSlug'],r[0],None,r[1],r[2],p['pdfPage']] for r in a]);page_counts.append([p['pdfPage'],len(a)])
  p['rowEvidence']=proof
 sums=[round(sum(r[3] for r in rows),2),round(sum(r[4] for r in rows if r[4] is not None),2) if any(r[4] is not None for r in rows) else None]
 if 'rowCount' in spec and len(rows)!=spec['rowCount']:raise ValueError('Row count changed')
 controls=spec.get('controls')
 residual=None
 if controls:
  residual=[round(v-c,2) if c is not None else None for v,c in zip(sums,controls)]
  if residual!=spec.get('residuals',[0,0]):raise ValueError(f"Controls fail {spec['id']}: count {len(rows)} sums {sums} controls {controls} residual {residual}")
 ev.update({'rowCount':len(rows),'rowSums':sums,'pageRowCounts':page_counts,'controls':controls,'residuals':residual,'everyRowFieldAgreement':True})
 return rows,ev

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--offline',action='store_true');ap.add_argument('--fetch',action='store_true',help='retrieve missing official hash-pinned originals');ap.add_argument('--verify',action='store_true');ap.add_argument('--diagnose',action='store_true');args=ap.parse_args()
 specs=json.loads((RESEARCH/'source-specs.json').read_text());outputs={};sources=[]
 for spec in specs:
  if spec.get('reviewStatus')=='pending' and not args.diagnose:continue
  try:rows,ev=replay(spec,extract(spec,args.offline,args.fetch))
  except Exception as ex:
   if args.diagnose:print(spec['id'],str(ex));continue
   raise
  if args.diagnose:print(spec['id'],len(rows),ev['rowSums']);continue
  packed=gzip.compress(compact(rows),mtime=0);outputs[spec['file']]=packed;outputs[spec['evidenceFile']]=gzip.compress(compact(ev),mtime=0)
  source={k:v for k,v in spec.items() if k not in ['parser','nameBoundary','positionBoundary','transition','reviewStatus','wordYTolerance','layoutCorrections','compiledRetentionReason','localPath','twoColumns','controls','residuals','periodEvidence','evidenceFile','renderReviewPages']}
  source.update({'sourceUrl':spec['url'],'sourceIndexUrl':spec['indexUrl'],'dataSha256':sha(packed),'pdfBytes':ev['pdfBytes'],'rowCount':len(rows),'totalRemuneration':ev['rowSums'][0],'totalExpenses':ev['rowSums'][1],'status':'verified','verifiedOn':'2026-11-01','category':'employee-remuneration','scope':'named-employees-over-threshold','completeEmployeeSchedule':True,'threshold':75000,'thresholdComparison':'>','currency':'CAD','amountUnit':'dollars','nameDisclosure':'surname-and-initials' if spec['employerSlug']=='icbc' else 'as-published','positionDisclosure':'not-published','sourceKind':'official-statement-of-financial-information','validation':{'originalFingerprintVerified':True,'independentReaders':['PyMuPDF positioned words','Poppler layout text'],'everyRowFieldAgreement':True,'rowsIndependentlyChecked':len(rows),'completeEmployeeSchedule':True,'physicalPagesVisuallyReviewed':spec.get('renderReviewPages',[]),'pageRowCounts':ev['pageRowCounts'],'printedControls':[{'field':f,'printedControl':c,'rowSum':v,'residual':r,'basis':spec['controlBasis']} for f,c,v,r in zip(['pay','expenses'],spec['controls'],ev['rowSums'],ev['residuals']) if c is not None],'evidenceFile':spec['evidenceFile']}})
  if spec.get('parser')=='bcfma-board':
   source.update({'category':'board-remuneration','scope':'named-board-members','completeEmployeeSchedule':False,'completeBoardSchedule':True,'positionDisclosure':'as-published','sourceKind':'official-board-remuneration-disclosure'})
   source['validation']['completeEmployeeSchedule']=False
   source['validation']['completeBoardSchedule']=True
   source.pop('threshold');source.pop('thresholdComparison')
  if spec.get('unknownReceiverExpense'):
   source['validation'].update({'employeeOnlyExpenseComparatorAvailable':False,'expenseComparatorIncludesNonPersonUnknownCell':True})
   for control in source['validation']['printedControls']:
    if control['field']=='expenses':control.update({'comparatorScope':'Printed over-threshold table, including excluded Receiver General with a dash/unknown expense cell','basis':'Known disclosed employee expense cells compared to printed table total; no zero Receiver General expense or strict employee-only expense comparator inferred.'})
  if spec.get('retainCompiledPartition'):
   source['validation'].update({'compiledPartitionRetained':True,'compiledPartitionRetentionReason':spec['compiledRetentionReason']})
  source.pop('url');source.pop('indexUrl');source.pop('controlBasis',None);sources.append(source)
 if args.diagnose:return
 outputs['sources.json']=(json.dumps({'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources},indent=2,ensure_ascii=False)+'\n').encode()
 for name,data in outputs.items():
  p=OUT/name
  if args.verify:
   if p.read_bytes()!=data:raise ValueError('Reproduction mismatch '+str(p))
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 print(json.dumps({'sources':len(sources),'rows':sum(s['rowCount'] for s in sources),'mode':'verified' if args.verify else 'written'}))
if __name__=='__main__':main()
