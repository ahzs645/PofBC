#!/usr/bin/env python3
"""Rebuild employee-only RRU/Langara evidence from fingerprinted original PDFs.
Public originals are downloaded only with --download; no publication/network writes.
"""
import argparse, collections, gzip, hashlib, json, pathlib, re, subprocess, urllib.request
import fitz
ROOT=pathlib.Path(__file__).resolve().parents[1]
CACHE=pathlib.Path('/workspace/salary-source-follow-through/cache-rru-langara')
SCHEMA=['employerSlug','name','position','remuneration','expenses','pdfPage']
CONFIG={
 'rru-2021-22':dict(pages=list(range(25,29)),bands=[200,450,490],startY=128,endY=173,control=[25258365,273992]),
 'rru-2022-23':dict(pages=list(range(25,29)),bands=[190,395,435],startY=251,endY=346,control=[29283375,893900]),
 'rru-2023-24':dict(pages=list(range(28,34)),scan=True),
 'rru-2024-25':dict(pages=list(range(28,34)),bands=[224,460,505],prependTitle=True,startY=299,endY=420,control=[36566652,1301172]),
 'rru-2025-26':dict(pages=list(range(26,32)),bands=[232,465,505],startY=275,endY=259,columnOrderNames=True,control=[38818140,1227026]),
 'langara-2022-23':dict(pages=list(range(31,42)),bands=[163,440,480],startY=138,endY=543,control=[69887454,2132005]),
 'langara-2023-24':dict(pages=list(range(32,43)),scan=True),
 'langara-2024-25':dict(pages=list(range(29,43)),bands=[179,430,480],startY=132,endY=486,control=[101403162,3209860]),
}
def sha(b):return hashlib.sha256(b).hexdigest()
def js(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def gz(p,o):
 b=(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n').encode();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress(b,mtime=0));return sha(p.read_bytes())
def clean(s):return ' '.join(s.split())
def money(s):
 s=s.strip().replace('$','').strip()
 if s=='- 0':return 0
 if s in ['','-','–','—']:return None
 if not re.fullmatch(r'-?[0-9][0-9,]*',s):raise ValueError(s)
 return int(s.replace(',',''))
def word_lines(pg):
 lines=[]
 for w in sorted(pg.get_text('words'),key=lambda w:(w[1],w[0])):
  if not lines or abs(w[1]-lines[-1][0])>3.5:lines.append([w[1],[]])
  lines[-1][1].append(w)
 return [(y,sorted(ws,key=lambda w:w[0])) for y,ws in lines]
def fitz_rows(d,c,slug):
 rows=[];e=[]
 for n in c['pages']:
  a,b,cc=c['bands'];page_rows=[]
  name_queue=[];pending_title=[]
  if c.get('columnOrderNames'):
   for yy,ww in word_lines(d[n-1]):
    nn=clean(' '.join(w[4] for w in ww if w[0]<a))
    if n==c['pages'][0] and yy<c['startY']:continue
    if ',' in nn and not nn.startswith(('Total','Schedule','- ','<$','$')):name_queue.append((nn,yy))
  for y,ws in word_lines(d[n-1]):
   if n==c['pages'][0] and y<c['startY']:continue
   fields=[clean(' '.join(w[4] for w in ws if (0 if j==0 else [a,b,cc][j-1])<=w[0]<(a if j==0 else [b,cc,1000][j-1]))) for j in range(4)]
   name,pos,pay,exp=fields
   if c.get('prependTitle'):
    if not name and pos and not pay and y>80:
     pending_title.extend(ws);continue
    if name and ',' in name and re.fullmatch(r'[0-9][0-9,]*',pay) and pending_title:
     pos=clean(' '.join(w[4] for w in pending_title)+' '+pos);fields[1]=pos;ws=pending_title+ws;pending_title=[]
   if c.get('columnOrderNames'):
    if not pos or not re.fullmatch(r'[0-9][0-9,]*',pay) or pos=='various':continue
    if not name_queue:continue
    name,ny=name_queue.pop(0)
   if not name or ',' not in name or name.startswith(('Total','Schedule','- ','<$','$')):continue
   if not re.fullmatch(r'[0-9][0-9,]*',pay):continue
   row=[slug,name,pos or None,money(pay),money(exp),n];rows.append(row);page_rows.append(row)
   e.append(dict(rowNumber=len(rows),pdfPage=n,bbox=[min(w[0] for w in ws),min(w[1] for w in ws),max(w[2] for w in ws),max(w[3] for w in ws)],publishedCells=fields,row=row))
  # Explicit row ranges protect against board, totals, and financial reconciliation text.
 return rows,e
def poppler_rows(txt,c,slug):
 rows=[];unparsed=[]
 pages=txt.split('\f')
 for n in c['pages']:
  active=n!=c['pages'][0]
  pending=None;pending_title=None
  for line in pages[n-1].splitlines():
   s=line.strip()
   if pending:
    s=pending+'  '+s;pending=None
   if active and ',' in s and len(line)-len(line.lstrip())<20 and len(re.split(r'\s{2,}',s))==1 and not re.search(r'\d',s):
    pending=s;continue
   if s.startswith('Employees') or s.startswith('Employee '):active=True;continue
   if s.startswith(('Employees Earning Less','Total of Employees Earning','Total Remuneration, Employees','Reconciling items')):active=False
   if not active or ',' not in s:continue
   if c.get('prependTitle') and active and len(line)-len(line.lstrip())>=20 and ',' in s and not re.search(r'\d',s):
    pending_title=s;continue
   # trailing monetary tokens are independent of the PDF word-coordinate reader
   parts=re.split(r'\s{2,}',s)
   if len(parts)<2:continue
   try:
    if len(parts)==5 and parts[-2]=='-' and parts[-1]=='0':parts=parts[:3]+['0']
    if len(parts)>=4 and re.fullmatch(r'[\d,]+',parts[-2]) and re.fullmatch(r'[\d,]+|-',parts[-1]):
     name=parts[0];pos=' '.join(parts[1:-2]) or None;pay=money(parts[-2]);exp=money(parts[-1])
    elif len(parts)>=3 and re.fullmatch(r'[\d,]+',parts[-1]):
     name=parts[0];pos=' '.join(parts[1:-1]) or None;pay=money(parts[-1]);exp=None
    elif len(parts)==3 and re.fullmatch(r'[\d,]+',parts[1]) and parts[2]=='-':
     name=parts[0];pos=None;pay=money(parts[1]);exp=None
    else:continue
   except ValueError:unparsed.append([n,line]);continue
   if ',' not in name or name.startswith(('Total','Schedule','- ','<$','$')):continue
   if pending_title:
    pos=pending_title+' '+(pos or '');pending_title=None
   rows.append([slug,name,pos,pay,exp,n])
 return rows,unparsed

PRINTED_COMPONENTS={
 'rru-2021-22':{'combined':[44459689,1078800],'belowThreshold':[19201324,804808]},
 'rru-2022-23':{'combined':[46376272,1880020],'belowThreshold':[17092897,986120]},
 'rru-2024-25':{'combined':[47915752,1397426],'belowThreshold':[11349100,96254]},
 'rru-2025-26':{'combined':[49513684,1317162],'belowThreshold':[10695544,90136]},
}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--download',action='store_true');ap.add_argument('--render',action='store_true');ap.add_argument('--only');args=ap.parse_args()
 leads=sum([json.loads((ROOT/'research/salaries'/('follow-through-'+kind)/'source-leads.json').read_text()) for kind in ['rru','langara']],[])
 manifests={};dispositions={}
 for key,c in CONFIG.items():
  if args.only and key!=args.only:continue
  s=next(s for s in leads if s['id']=='additional-source-'+key);kind=key.split('-')[0];slug=s['employerSlug'];year=s['year'];out=ROOT/'research/salaries'/('follow-through-'+kind)
  q=CACHE/('additional-source-'+key+'.pdf')
  if args.download or not q.exists():
   CACHE.mkdir(parents=True,exist_ok=True)
   for attempt in range(3):
    try:raw=urllib.request.urlopen(s['sourceUrl'],timeout=120).read();break
    except Exception:
     if attempt==2:raise
   assert sha(raw)==s['downloadVerifiedSha256'];q.write_bytes(raw)
  raw=q.read_bytes();fingerprint=sha(raw)
  assert fingerprint==s['downloadVerifiedSha256']
  if s['verification'].get('sha256'):assert s['verification']['sha256']==fingerprint
  d=fitz.open(q);layout=q.with_suffix('.layout.txt');subprocess.run(['pdftotext','-layout',str(q),str(layout)],check=True);txt=layout.read_text()
  source_id=key.replace('rru-','rru-sofi-').replace('langara-','langara-sofi-')+'-employees'
  evidence={'sourceId':source_id,'discoverySourceId':s['id'],'sourceUrl':s['sourceUrl'],'indexUrl':s['indexUrl'],'pdfSha256':fingerprint,'pdfBytes':len(raw),'pdfPageCount':len(d),'employeePhysicalPages':c['pages'],'pymupdfVersion':fitz.VersionBind,'popplerVersion':subprocess.run(['pdftotext','-v'],capture_output=True,text=True).stderr.splitlines()[0],'pageText':[{ 'pdfPage':n,'pymupdfText':d[n-1].get_text(),'popplerLayoutText':txt.split('\f')[n-1]} for n in c['pages']]}
  visual_path=out/'visual'/f'{key}.json'
  previous_review=json.loads(visual_path.read_text()) if visual_path.exists() else {}
  renders=previous_review.get('renders',[])
  if args.render:
   renders=[]
   for n in c['pages']:
    img=out/'images'/f'{key}-p{n:02}.png';img.parent.mkdir(parents=True,exist_ok=True);d[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(img);renders.append({'pdfPage':n,'file':str(img.relative_to(out)),'sha256':sha(img.read_bytes()),'width':918,'height':1188,'scale':1.5})
  reviewed_pages=previous_review.get('reviewedPhysicalPages',[]) if renders==previous_review.get('renders') else []
  if c.get('scan'):
   # A separately reviewed OCR import owns its immutable scan-specific evidence.
   old_manifest=json.loads((out/'sources.json').read_text()) if (out/'sources.json').exists() else {}
   reviewed=next((z for z in old_manifest.get('sources',[]) if z.get('id')==source_id and z.get('status')=='verified'),None)
   if reviewed:
    assert reviewed['sha256']==fingerprint and sha((out/reviewed['file']).read_bytes())==reviewed['dataSha256']
    manifests.setdefault(kind,[]).append(reviewed)
    old_ds=json.loads((out/'dispositions.json').read_text())['sources']
    dispositions.setdefault(kind,[]).append(next(z for z in old_ds if z['id']==s['id']))
    print(key,'retained separately verified OCR cohort',reviewed['rowCount']);continue
   evidence['extractionStatus']='held-scanned-employee-schedule';evidence['reason']='Original employee pages contain no employee text in either PyMuPDF or Poppler. OCR candidates require independent complete cell validation before acceptance.'
   gz(out/'evidence'/f'{key}.json.gzip',evidence)
   dispositions.setdefault(kind,[]).append(dict(id=s['id'],status='held-for-review',acceptedSourceId=None,employeeRows=0,pdfSha256=fingerprint,pages=c['pages'],reason=evidence['reason'],evidenceFile=f'evidence/{key}.json.gzip'))
   js(out/'visual'/f'{key}.json',{'sourceId':source_id,'pdfSha256':fingerprint,'renders':renders,'reviewedPhysicalPages':reviewed_pages,'status':'scanned-schedule-held-pending-cell-validation','reviewScope':previous_review.get('reviewScope')})
   print(key,'HELD scan');continue
  rows,receipts=fitz_rows(d,c,slug);other,unparsed=poppler_rows(txt,c,slug)
  diffs=[]
  for i in range(max(len(rows),len(other))):
   a=rows[i] if i<len(rows) else None;b=other[i] if i<len(other) else None
   if a!=b:diffs.append({'index':i,'pymupdf':a,'poppler':b})
  evidence.update(rowCount=len(rows),rowReceipts=receipts,popplerRows=other,independentReaderDifferences=diffs,popplerUnparsed=unparsed)
  totalpay=sum(r[3] for r in rows);totalexp=sum(r[4] or 0 for r in rows)
  evidence.update(totalRemuneration=totalpay,totalExpenses=totalexp,missingExpenseCells=sum(r[4] is None for r in rows),zeroExpenseCells=sum(r[4]==0 for r in rows),pageRowCounts=sorted(collections.Counter(r[5] for r in rows).items()))
  controls=[]
  for field,total,control in zip(['remuneration','expenses'],[totalpay,totalexp],c.get('control',[])):controls.append({'field':field,'rowSum':total,'printedControl':control,'residual':total-control})
  evidence['printedControls']=controls
  evidence['controlComponents']=PRINTED_COMPONENTS.get(key,{'namedEmployeeSubtotal':c['control']})
  for ctl in controls:ctl['basis']='Printed employee combined total minus separately printed below-$75,000 employee aggregate; board expenses are a separate schedule.' if kind=='rru' else 'Printed Total of Employees Earning > $75,000; board, under-threshold and other aggregates excluded.'
  gz(out/'evidence'/f'{key}.json.gzip',evidence)
  expected={'rru-2021-22':(223,[-4,2]),'rru-2022-23':(256,[8,3]),'rru-2024-25':(321,[-5,-1]),'rru-2025-26':(334,[11,5]),'langara-2022-23':(710,[-8,11]),'langara-2024-25':(950,[-11,16])}[key]
  status='verified' if not diffs and not unparsed and (len(rows),[z['residual'] for z in controls])==expected else 'held-for-review'
  source=dict(id=source_id,employerSlug=slug,employerName='Royal Roads University' if kind=='rru' else 'Langara College',sector='Post-secondary education',year=year,periodType='fiscal',periodStart=year[:4]+'-04-01',periodEnd='20'+year[-2:]+'-03-31',title=s['title']+' — named employee remuneration and expenses',sha256=fingerprint,file=key+'.json.gzip',pages=c['pages'],sourceUrl=s['sourceUrl'],sourceIndexUrl=s['indexUrl'],pdfBytes=len(raw),rowCount=len(rows),totalRemuneration=totalpay,totalExpenses=totalexp,status=status,verifiedOn='2026-11-02',category='employee-remuneration',scope='named-employees-over-threshold',completeEmployeeSchedule=not diffs,threshold=75000,thresholdComparison='>=' if kind=='rru' else '>',currency='CAD',amountUnit='dollars',nameDisclosure='as-published',positionDisclosure='as-published',sourceKind='official-statement-of-financial-information',notes=['Employee schedule only; board, suppliers, below-threshold aggregates, severance/reconciliation lines excluded.','Published remuneration is not an inferred annual base salary. Missing or dash expense cells remain null; printed numeric zero remains zero.','All compiled observations and their original labels are retained.'],validation=dict(originalFingerprintVerified=True,independentReaders=['PyMuPDF positioned words','Poppler layout text'],everyRowFieldAgreement=not diffs,rowsIndependentlyChecked=len(rows) if not diffs else 0,completeEmployeeSchedule=not diffs,pageRowCounts=evidence['pageRowCounts'],printedControls=controls,evidenceFile=f'evidence/{key}.json.gzip',physicalPagesVisuallyReviewed=reviewed_pages))
  source['retainCompiledPartition']=True
  source['publicWarning']='Published employee cells differ from printed named controls by '+str(controls[0]['residual'])+' CAD remuneration and '+str(controls[1]['residual'])+' CAD expenses. Original cells are retained.'
  if kind=='langara':source['notes'].append('The printed named cohort is labelled Total of Employees Earning > $75,000, but some disclosed salary/gross-pay cells are below $75,000. All named schedule rows are retained without inferring a different threshold measure.')
  if key=='rru-2025-26':
   source['notes'].append('The literal published name cell 3361 Zornes, Deborah is preserved, as is the separated minus-sign numeric-zero expense for Hutchison, Michael. The report separately prints a $42,908 financial-statement reconciliation variance; employee extraction is not adjusted to remove it.')
  source['dataSha256']=gz(out/source['file'],rows)
  manifests.setdefault(kind,[]).append(source);dispositions.setdefault(kind,[]).append(dict(id=s['id'],status='imported' if status=='verified' else status,acceptedSourceId=source_id if status=='verified' else None,employeeRows=len(rows) if status=='verified' else 0,candidateRows=len(rows),pdfSha256=fingerprint,manifest='research/salaries/follow-through-'+kind+'/sources.json',reason='Complete independent employee-row agreement.' if status=='verified' else f'{len(diffs)} independent reader differences require review.'))
  js(out/'visual'/f'{key}.json',{'sourceId':source_id,'pdfSha256':fingerprint,'renders':renders,'reviewedPhysicalPages':reviewed_pages,'status':'reviewed' if reviewed_pages else 'rendered-awaiting-pixel-review','reviewScope':previous_review.get('reviewScope')})
  print(key,len(rows),len(other),'diffs',len(diffs),'sums',totalpay,totalexp,'null/0',evidence['missingExpenseCells'],evidence['zeroExpenseCells'],'controls',controls)
  if diffs:print(json.dumps(diffs[:8],ensure_ascii=False))
 for kind,sources in manifests.items():
  path=ROOT/'research/salaries'/('follow-through-'+kind)/'sources.json'
  if args.only and path.exists():sources=sorted([s for s in json.loads(path.read_text())['sources'] if s['id'] not in {z['id'] for z in sources}]+sources,key=lambda s:s['year'])
  js(path,{'version':1,'rowSchema':SCHEMA,'sources':sources})
 for kind,ds in dispositions.items():
  path=ROOT/'research/salaries'/('follow-through-'+kind)/'dispositions.json'
  if args.only and path.exists():ds=sorted([s for s in json.loads(path.read_text())['sources'] if s['id'] not in {z['id'] for z in ds}]+ds,key=lambda s:s['id'])
  js(path,{'version':1,'sources':ds})
if __name__=='__main__':main()
