#!/usr/bin/env python3
"""New official postsecondary recovery wave; independent readers + pinned replay.

PyMuPDF words are read by geometric numeric anchors. Poppler layout is read by
textual column boundaries and a name continuation state machine. Neither reader
consumes rows produced by the other. All rows/order/pages/multiplicity must agree.
"""
import argparse, collections, gzip, hashlib, json, re, subprocess
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/recovery-education'
AUDIT=ROOT/'research/salaries/recovery-wave-2026-11-01/education'
CACHE=Path('/tmp/pofbc-sector-education')
NUM=r'(?:-?\d[\d,]*(?:\.\d{2})?|\(\d[\d,]*(?:\.\d{2})?\))'
TOKEN=re.compile('^(?:'+NUM+r'|-|–|—)$')
CONFIG=[('university-of-bc','2025/26','0b9387de913e9302.body','ubc',list(range(42,190))),('coast-mountain-college','2024/25','d5af412fa1d197a9.body','coast-mountain',list(range(34,39))),('coast-mountain-college','2023/24','b3961b373f16740e.body','coast-mountain',list(range(33,37))),('coast-mountain-college','2022/23','61caf40621b659ee.body','coast-mountain',list(range(34,37)))]
def sha(b):return hashlib.sha256(b).hexdigest()
def dumps(d):return json.dumps(d,ensure_ascii=False,separators=(',',':')).encode()
def writejson(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def money(s):
 s=s.replace('$','').strip()
 if s in ['', '-', '–', '—']:return None
 assert re.fullmatch(NUM,s),s
 v=float(s.replace(',','').replace('(','-').replace(')',''))
 return int(v) if v==int(v) else v

def joinwords(words):
 return ' '.join(w[4] for w in sorted(words,key=lambda w:(round(w[1],1),w[0])))
def primary_ubc(words,page):
 headers=sorted([w for w in words if w[4]=='Name'],key=lambda w:w[0]);assert len(headers)==2,(page,headers)
 rows=[];proof=[]
 for col,h in enumerate(headers):
  x=h[0];hy=h[1];paylo=x+115;payhi=x+187;exphi=x+250
  anchors=sorted([w for w in words if paylo<=w[0]<payhi and w[1]>hy+5 and re.fullmatch(NUM,w[4])],key=lambda w:w[1]);prev=hy+5
  for a in anchors:
   names=[w for w in words if x-2<=w[0]<paylo and prev+2<w[1]<=a[1]+2]
   name=joinwords(names)
   ex=[w for w in words if payhi<=w[0]<exphi and abs(w[1]-a[1])<2 and TOKEN.fullmatch(w[4])]
   assert len(ex)==1,(page,name,a,ex)
   if name.startswith(('Remuneration','Total')) or ',' not in name:
    assert name.startswith(('Remuneration','Total')),(page,col,name)
    break
   assert money(a[4])>75000,(page,name,a)
   rows.append([name,None,money(a[4]),money(ex[0][4]),page]);proof.append(dict(physicalPage=page,column=col+1,name=name,remunerationToken=a[4],expenseToken=ex[0][4],baseline=round(a[1],4)))
   prev=a[1]
 return rows,proof

def secondary_ubc(text,page):
 lines=text.splitlines();heads=[(i,list(re.finditer(r'\bName\s+Remuneration\s+Expenses\*',line))) for i,line in enumerate(lines) if len(re.findall(r'\bName\s+Remuneration\s+Expenses\*',line))==2]
 assert len(heads)==1,(page,heads)
 idx,head=heads[0];split=head[1].start()-1
 rows=[];proof=[]
 for col in range(2):
  pending=[]
  for line in lines[idx+1:]:
   cell=(line[:split] if col==0 else line[split:]).strip()
   if not cell:continue
   if cell.startswith('Page |'):continue
   m=re.fullmatch(r'(.*?)\s{2,}('+NUM+r')\s{2,}('+NUM+r'|-)\s*',cell)
   if m:
    name=' '.join(pending+[m[1].strip()]);pending=[]
    if ',' not in name:
     assert name.startswith(('Remuneration','Total')),(page,col,name)
     break
    rows.append([name,None,money(m[2]),money(m[3]),page]);proof.append(cell)
   else:
    if cell.startswith(('Remuneration','Total')):break
    pending.append(cell)
  assert not pending,(page,col,pending)
 return rows,proof

def primary_college(words,page,kind,year):
 heads=[w for w in words if w[4] in ['Benefits','Remuneration']]
 if kind=='cnc':
  hy=max(w[1] for w in heads);paylo=370;payhi=460;exphi=560;name_end=370;firstx=155
 else:
  h=max([w for w in heads if w[4]=='Benefits'],key=lambda w:w[1]);hy=h[1];paylo=h[0]-30
  eh=next(w for w in words if w[4]=='Expenses' and abs(w[1]-hy)<3);th=next(w for w in words if w[4]=='Total' and abs(w[1]-hy)<3)
  payhi=(h[2]+eh[0])/2;exphi=(eh[2]+th[0])/2;name_end=paylo
  firstx=190 if year=='2023/24' else 149
 rows=[];proof=[]
 anchors=sorted([w for w in words if paylo<w[0]<payhi and w[1]>hy+5 and re.fullmatch(NUM,w[4])],key=lambda w:w[1])
 for a in anchors:
  names=[w for w in words if w[0]<name_end and abs(w[1]-a[1])<3 and w[4]!='$']
  if not names:raise AssertionError((page,a,'no name'))
  whole=joinwords(names)
  if any(whole.startswith(z) for z in ['Brought Forward','Carry Forward','Total','Grand Total']):continue
  if kind=='cnc' or year!='2024/25':
   last=joinwords([w for w in names if w[0]<firstx-1]);first=joinwords([w for w in names if w[0]>=firstx-1]);assert last and first,(page,whole)
   name=last+', '+first
  else:name=whole
  ex=[w for w in words if payhi<=w[2]<exphi and abs(w[1]-a[1])<3 and TOKEN.fullmatch(w[4])]
  assert len(ex)<=1,(page,name,ex)
  assert money(a[4])>75000,(page,name,a)
  total=[w for w in words if exphi<=w[2] and abs(w[1]-a[1])<3 and TOKEN.fullmatch(w[4])] if kind!='cnc' else []
  assert kind=='cnc' or len(total)==1,(page,name,total)
  rows.append([name,None,money(a[4]),money(ex[0][4]) if ex else None,page]);proof.append(dict(physicalPage=page,name=name,remunerationToken=a[4],expenseToken=ex[0][4] if ex else '',publishedExpenseInclusiveTotalToken=total[0][4] if total else None,baseline=round(a[1],4)))
 return rows,proof

def secondary_college(text,page,kind,year):
 lines=text.splitlines();rows=[];proof=[]
 # Physical column positions are learned only from Poppler's header line.
 head=max(i for i,line in enumerate(lines) if ('Name' in line and ('Expenses' in line or kind=='cnc' and 'First Name' in line)))
 # CNC two-line headings: the line with Last/First/Remuneration is definitive.
 h=lines[head];paystart=h.index('Remuneration') if kind=='cnc' else h.index('Benefits')-4
 expstart=h.index('Expenses');totalstart=h.index('Total',expstart) if kind!='cnc' else len(h)+10
 splits=[]
 for line in lines[head+1:]:
  m=re.search(r'\s{2,}'+NUM,line.replace('$',' '))
  if m:
   gap=re.search(r'\s{2,}',line[:m.start()].strip())
   if gap:splits.append(gap.end())
 name_split=collections.Counter(splits).most_common(1)[0][0] if splits else None
 for line in lines[head+1:]:
  if not line.strip():continue
  # Use large column whitespace, preserving name words and separate surname/given cells.
  cells=re.split(r'\s{2,}',line.replace('$',' ').strip())
  if not cells or cells[0].startswith(('Total','Grand Total','Carry Forward','Brought Forward','CMTN','Coast Mountain','Schedule','For the','Reconcilliation','Employee expenses','paid by','bonuses,','year being','agreement.','Schedule 1,','Income Tax','Cabinet,')):continue
  m=re.search(r'\s{2,}('+NUM+r'|-)(?:\s{2,}('+NUM+r'|-))?(?:\s{2,}('+NUM+r'|-))?\s*$',line.replace('$',' '))
  if not m:continue
  namepart=line[:m.start()].strip();ns=re.split(r'\s{2,}',namepart)
  if kind=='cnc' or year!='2024/25':
   split=name_split
   last=namepart[:split].strip();first=namepart[split:].strip();assert last and first,(page,last,first,line)
   name=last+', '+first
  else:
   assert len(ns)==1,(page,ns,line)
   name=ns[0]
  if not re.search(r'[A-Za-z]',name):continue
  vals=[money(t) if t is not None else None for t in m.groups()]
  if kind!='cnc' and m[3] is None:
   # A visibly blank expense leaves only remuneration and expense-inclusive total.
   vals=[vals[0],None,vals[1]]
  assert vals[0]>75000,(page,name,vals)
  rows.append([name,None,vals[0],vals[1],page]);proof.append(dict(rawLine=line,publishedExpenseInclusiveTotal=vals[2] if kind!='cnc' else None))
 return rows,proof

def controls_primary(words,page,kind):
 out=[]
 if kind=='ubc':
  hs=sorted([w for w in words if w[4]=='Name'],key=lambda w:w[0]);h=hs[1];x=h[0];hy=h[1];paylo=x+115;payhi=x+187;exphi=x+250;prev=hy+5
 else:
  h=max([w for w in words if w[4]=='Benefits'],key=lambda w:w[1]);hy=h[1];x=0;paylo=h[0]-30
  eh=next(w for w in words if w[4]=='Expenses' and abs(w[1]-hy)<3);th=next(w for w in words if w[4]=='Total' and abs(w[1]-hy)<3)
  payhi=(h[2]+eh[0])/2;exphi=(eh[2]+th[0])/2
 anchors=sorted([w for w in words if paylo<=w[0]<payhi and w[1]>hy+5 and re.fullmatch(NUM,w[4])],key=lambda w:w[1])
 for a in anchors:
  ns=[w for w in words if x-2<=w[0]<paylo and w[4]!='$' and (prev+2<w[1]<=a[1]+2 if kind=='ubc' else abs(w[1]-a[1])<3)]
  name=joinwords(ns);prev=a[1]
  if not name.startswith(('Remuneration','Total','Grand Total','Carry Forward','Brought Forward')):continue
  ex=[w for w in words if payhi<=w[2]<exphi and abs(w[1]-a[1])<3 and TOKEN.fullmatch(w[4])];assert len(ex)==1,(page,name,ex)
  vals=[money(a[4]),money(ex[0][4])]
  if kind!='ubc':
   total=[w for w in words if exphi<=w[2] and abs(w[1]-a[1])<3 and TOKEN.fullmatch(w[4])];assert len(total)==1;vals+=[money(total[0][4])]
  out.append(dict(physicalPage=page,label=name,values=vals))
 return out

def controls_secondary(text,page,kind):
 lines=text.splitlines();out=[]
 if kind=='ubc':
  idx=next(i for i,l in enumerate(lines) if len(re.findall(r'\bName\s+Remuneration\s+Expenses\*',l))==2);h=lines[idx];split=list(re.finditer(r'\bName\s+Remuneration\s+Expenses\*',h))[1].start()-1
  parts=[l[split:].strip() for l in lines[idx+1:]]
 else:parts=[l.replace('$',' ').strip() if not l.strip().startswith(('Total -','Grand Total','Carry Forward','Brought Forward')) else l.strip() for l in lines]
 pending=[]
 for line in parts:
  if not line or line.startswith('Page |'):continue
  # Dollar signs marking columns are removed only after the label has been separated.
  m=re.search(r'\s{2,}\$?\s*('+NUM+r')\s+\$?\s*('+NUM+r'|-)(?:\s+\$?\s*('+NUM+r'))?\s*$',line)
  if m:
   label=' '.join(pending+[line[:m.start()].strip()]);pending=[]
   if not label.startswith(('Remuneration','Total','Grand Total','Carry Forward','Brought Forward')):continue
   vals=[money(m[1]),money(m[2])]
   if kind!='ubc':assert m[3] is not None;vals.append(money(m[3]))
   out.append(dict(physicalPage=page,label=label,values=vals))
  elif kind=='ubc':pending.append(line)
 return out

def extract(pdf,kind,year,pages):
 doc=fitz.open(pdf);pop=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,text=True,check=True).stdout.split('\f')
 ev=[];rows=[]
 for p in pages:
  words=[list(w[:5]) for w in doc[p-1].get_text('words')]
  a,ap=primary_ubc(words,p) if kind=='ubc' else primary_college(words,p,kind,year)
  b,bp=secondary_ubc(pop[p-1],p) if kind=='ubc' else secondary_college(pop[p-1],p,kind,year)
  assert a==b,(kind,year,p,'independent reader mismatch',len(a),len(b),[(x,y) for x,y in zip(a,b) if x!=y][:5],a[-2:],b[-2:])
  ca=controls_primary(words,p,kind);cb=controls_secondary(pop[p-1],p,kind);assert ca==cb,(kind,year,p,'control readers mismatch',ca,cb)
  if kind!='ubc':assert [money(x['publishedExpenseInclusiveTotalToken']) for x in ap]==[x['publishedExpenseInclusiveTotal'] for x in bp],(kind,year,p,'printed total component mismatch')
  rows+=a;ev.append(dict(physicalPage=p,words=words,popplerLayout=pop[p-1],rowEvidence=ap,publishedControls=ca))
 semantic_pages=([1,2,3,40,41,42,189,190] if kind=='ubc' else [1,2,3,pages[0],pages[-1],pages[-1]+1,pages[-1]+2])
 scope=[]
 for n in sorted(set(semantic_pages)):
  scope.append(dict(physicalPage=n,words=[list(w[:5]) for w in doc[n-1].get_text('words')],popplerLayout=pop[n-1]))
 assert f'March 31, {int(year[:4])+1}' in ' '.join(e['popplerLayout'] for e in scope) or f'MARCH 31, {int(year[:4])+1}' in ' '.join(e['popplerLayout'] for e in scope)
 assert not any(re.search(r'\bdraft\b',p.get_text(),re.I) for p in doc)
 return rows,dict(kind=kind,year=year,pages=pages,pageEvidence=ev,scopeEvidence=scope)

def build():
 docs=json.loads((ROOT/'research/salaries/sector-search-2026-10-31/education/document-verification.json').read_text())['documents'];sources=[]
 for slug,year,filename,kind,pages in CONFIG:
  d=next(d for d in docs if d['cacheFile']==filename);p=CACHE/filename;assert sha(p.read_bytes())==d['sha256']
  rows,ev=extract(p,kind,year,pages);rows=[[slug]+r for r in rows];sid=f'recovery-{kind}-sofi-{year.replace("/","-")}-employees'
  payload=dumps(rows);data=gzip.compress(payload,mtime=0);evdata=gzip.compress(dumps(ev),mtime=0)
  (OUT/(sid+'.json.gzip')).write_bytes(data);(OUT/'evidence'/(sid+'.json.gzip')).write_bytes(evdata)
  s=dict(id=sid,employerSlug=slug,employerName={'ubc':'University of B.C. (UBC)','cnc':'College of New Caledonia','coast-mountain':'Coast Mountain College'}[kind],sector='Universities and colleges',year=year,slug=year.replace('/','-'),file=sid+'.json.gzip',title=f'{slug} Statement of Financial Information {year}: employee remuneration and expenses',sourceUrl=d['url'],sourceIndexUrl=d['indexUrl'],sha256=d['sha256'],dataSha256=sha(data),normalizedSha256=sha(payload),periodType='fiscal',periodStart=year[:4]+'-04-01',periodEnd=str(int(year[:4])+1)+'-03-31',currency='CAD',category='employee-remuneration',scope='employee-remuneration',sourceKind='official',status='verified',verifiedOn='2026-11-01',nameDisclosure='as-published; separate surname/given columns joined with comma where applicable',positionDisclosure='not-published',completeEmployeeSchedule=True,rowCount=len(rows),pages=pages,totalRemuneration=sum(r[3] for r in rows),totalExpenses=sum(r[4] or 0 for r in rows),notes=['Complete named employee schedule; below-threshold aggregates, board honorariums, suppliers and employer contributions are excluded. Names with identical spelling retain separate source rows. Blank/dash expenses remain null; literal negative expense amounts are retained. Annual remuneration as published, not base annual salary.'],validation=dict(sourceFingerprintLocked=True,completeEmployeeSchedule=True,allNamesAndMonetaryCellsIndependentlyVerified=True,independentMethod='PyMuPDF geometric numeric anchors and name-region reader versus independently implemented Poppler physical-layout column and continuation-state reader; exact ordered row/name/amount/page/multiplicity equality.',rowCountsByPdfPage=dict(collections.Counter(r[5] for r in rows)),expenseDashesOrBlankRetainedAsMissing=sum(r[4] is None for r in rows),explicitZeroExpenseRows=sum(r[4]==0 for r in rows),negativeExpenseRows=sum(r[4] is not None and r[4]<0 for r in rows),evidenceFile='evidence/'+sid+'.json.gzip',evidenceSha256=sha(evdata)),cacheFile=str(p))
  controls=[c for e in ev['pageEvidence'] for c in e['publishedControls']];s['validation']['publishedControls']=controls
  named=next(c for c in controls if c['label'] in ['Remuneration exceeding $75,000','Total - earnings over $75,000'])
  residual=[s['totalRemuneration']-named['values'][0],s['totalExpenses']-named['values'][1]]
  s['validation']['namedControlResidualRowSumMinusPrinted']=residual
  s['validation']['namedControlExactlyReconciled']=residual==[0,0]
  below=next(c for c in controls if c['label'] in ['Remuneration of $75,000 or less','Total - earnings under $75,000'])
  grand=next(c for c in controls if c['label'] in ['Total','Grand Total'])
  arithmetic=[a+b-c for a,b,c in zip(named['values'],below['values'],grand['values'])]
  s['validation']['printedNamedPlusBelowMinusGrandTotal']=arithmetic
  if residual!=[0,0]:
   s['publicWarning']=f"The published named employee rows sum to ${s['totalRemuneration']:,} remuneration and ${s['totalExpenses']:,} expenses; the printed named subtotal is ${named['values'][0]:,} and ${named['values'][1]:,}. Row sums minus printed subtotals are ${residual[0]:+,.0f} and ${residual[1]:+,.0f}. Published amounts are retained; the cause is unresolved."
  if any(arithmetic):s['publicWarning']+=f" Printed named-plus-below-threshold remuneration also differs from the printed grand total by ${arithmetic[0]:+,.0f}; it is retained literally."
  if kind=='ubc':
   s['notes']+=['Schedule states cash fiscal-year payments. Expenses are gross, unadjusted for external cost recoveries. Board schedule says employment remuneration/expenses of President/faculty/staff/students who are board members are included in employee schedule.','Employee schedule is expressly unaudited. The consolidated management statement has literal [signed] labels dated June 24, 2026, rather than autograph images; no separate signed employee-schedule approval was identified.']
   s['validation']['approvalReview']='Official university-hosted SOFI; consolidated statement displays [signed] labels, June 24, 2026. Employee schedule unaudited; no separate autograph approval identified.'
  if kind=='coast-mountain':
   s['notes']+=['Remuneration is the published Salary Plus Benefits column. The separate Total column includes expenses and is not used as remuneration. Reconciliation separately lists employer portion of benefits; it is not added to individual remuneration.']
   s['validation']['approvalReview']=('Autograph signature of Adelle Cober, Chair, on physical page 3; September '+str(int(year[:4])+1)) if year!='2022/23' else 'Physical page 3 contains Board approval wording, typed Shannon McPhail, Acting Chair, September 2023, with a blank signature line. Genuine official original is unsigned; adoption is not independently established.'
   comps=[(e['physicalPage'],r['name'],money(r['remunerationToken'])+(money(r['expenseToken']) or 0)-money(r['publishedExpenseInclusiveTotalToken'])) for e in ev['pageEvidence'] for r in e['rowEvidence']]
   s['validation']['expenseInclusiveTotalComponentResiduals']=[dict(physicalPage=p,name=n,remunerationPlusExpensesMinusPublishedTotal=v) for p,n,v in comps if v]
   s['notes']+=['Some published expense-inclusive row totals differ from the sum of the two published component cells by one dollar. All three source cells are independently compared and retained in evidence; no adjustment or explanation is inferred.']
   carry=[]
   for c in controls:
    if c['label'] not in ['Carry Forward Total','Brought Forward Total']:continue
    rr=[r for r in rows if r[5]<c['physicalPage'] or c['label']=='Carry Forward Total' and r[5]==c['physicalPage']]
    expected=[sum(r[3] for r in rr),sum(r[4] or 0 for r in rr)]
    carry.append(dict(physicalPage=c['physicalPage'],label=c['label'],rowSumRemunerationExpenses=expected,publishedValues=c['values'],rowSumMinusPublished=[a-b for a,b in zip(expected,c['values'])]))
   s['validation']['carryControlComparisons']=carry
   if year=='2022/23':
    s['notes']+=['Approval page is unsigned (typed Acting Chair and September 2023 date). The surname field of Helfensteller dos, Vito on physical page 34 is visibly clipped; the common native-reader text is retained literally, without completing a surname.']
    s['publicWarning']+=' The original approval page has a blank signature line. One surname field (Helfensteller dos, Vito) is visibly clipped and is retained as exposed by both text readers.'
  if kind=='cnc':s['notes']+=['Remuneration definition includes salary, wages, bonuses, gratuities, taxable benefits and trust/income deferral payments, excluding severance agreements. Expenses include College purchasing-card amounts paid on employees behalf.']
  sources.append(s);print(sid,len(rows),s['totalRemuneration'],s['totalExpenses'],flush=True)
 writejson(OUT/'sources.json',dict(version=1,rowSchema=['employerSlug','name','position','remuneration','expenses','pdfPage'],sources=sources))

def verify(originals=False):
 ss=json.loads((OUT/'sources.json').read_text())['sources']
 for s in ss:
  p=OUT/s['validation']['evidenceFile'];assert sha(p.read_bytes())==s['validation']['evidenceSha256'];ev=json.loads(gzip.decompress(p.read_bytes()));rows=[]
  for e in ev['pageEvidence']:
   p=e['physicalPage'];a,ap=primary_ubc(e['words'],p) if ev['kind']=='ubc' else primary_college(e['words'],p,ev['kind'],ev['year']);b,bp=secondary_ubc(e['popplerLayout'],p) if ev['kind']=='ubc' else secondary_college(e['popplerLayout'],p,ev['kind'],ev['year']);assert a==b;rows += [[s['employerSlug']]+r for r in a]
   assert ap==e['rowEvidence']
   if ev['kind']!='ubc':assert [money(x['publishedExpenseInclusiveTotalToken']) for x in ap]==[x['publishedExpenseInclusiveTotal'] for x in bp]
   assert controls_primary(e['words'],p,ev['kind'])==controls_secondary(e['popplerLayout'],p,ev['kind'])==e['publishedControls']
  data=(OUT/s['file']).read_bytes();assert sha(data)==s['dataSha256'];assert sha(gzip.decompress(data))==s['normalizedSha256'];assert rows==json.loads(gzip.decompress(data));assert len(rows)==s['rowCount'];assert sum(r[3] for r in rows)==s['totalRemuneration'];assert sum(r[4] or 0 for r in rows)==s['totalExpenses']
  assert [c for e in ev['pageEvidence'] for c in e['publishedControls']]==s['validation']['publishedControls']
  if originals:
   pdf=Path(s['cacheFile']);assert sha(pdf.read_bytes())==s['sha256'];actual,_=extract(pdf,ev['kind'],ev['year'],ev['pages']);assert [[s['employerSlug']]+r for r in actual]==rows
 print('Verified',len(ss),'sources /',sum(s['rowCount'] for s in ss),'rows', 'with originals' if originals else 'offline evidence replay')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',action='store_true');p.add_argument('--originals',action='store_true');a=p.parse_args();build() if a.build else verify(a.originals)
