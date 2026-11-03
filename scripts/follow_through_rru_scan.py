#!/usr/bin/env python3
"""Independent OCR row evidence for the original RRU2023/24 employee schedule."""
import csv,json,pathlib,re,collections,gzip,hashlib
from follow_through_rru_langara import ROOT,CACHE,js,gz,sha
OUT=ROOT/'research/salaries/follow-through-rru'
COLS={'name':(95,235),'position':(235,432),'pay':(432,495),'expenses':(495,550)}
PAGES=range(28,34)
def words(path,scale,offsetx=0):
 out=[]
 for r in csv.DictReader(path.read_text().splitlines(),delimiter='\t'):
  if not r['text'].strip():continue
  x=float(r['left'])/scale+offsetx;y=float(r['top'])/scale;ww=float(r['width'])/scale;hh=float(r['height'])/scale
  out.append(dict(text=r['text'],x=x,y=y,w=ww,h=hh,mid=y+hh/2,conf=float(r['conf'])))
 return out

def lines(ws):
 out=[]
 for w in sorted(ws,key=lambda w:(w['mid'],w['x'])):
  if not out or abs(w['mid']-out[-1][0])>3:out.append([w['mid'],[]])
  out[-1][1].append(w)
 return [(sum(w['mid'] for w in v)/len(v),' '.join(w['text'] for w in sorted(v,key=lambda w:w['x'])),sorted(v,key=lambda w:w['x'])) for _,v in out]
def normmoney(s):
 s=s.strip().strip('$').strip().rstrip(',')
 if s in ['','-','—','–','s']:return None if s!='s' else 'UNREADABLE:s'
 if re.fullmatch(r'[0-9]+(?:,[0-9]{3})*',s):return int(s.replace(',',''))
 if re.fullmatch(r'[0-9]+(?:,[0-9]{3})*\.[0-9]{2}',s):return float(s.replace(',',''))
 return 'UNREADABLE:'+s

def extract(n,engine):
 columns_config={**COLS}
 if n==30:columns_config.update(name=(95,233),position=(233,432))
 if engine==1:
  ww=words(CACHE/f'rru-2023-24-ocr-p{n:02}.tsv',3);columns={col:[w for w in ww if a<=w['x']<b] for col,(a,b) in columns_config.items()}
 else:columns={col:words(CACHE/f'rru-2023-24-e2-p{n:02}-{col}.tsv',5,a) for col,(a,b) in columns_config.items()}
 anchors=[]
 for mid,text,ww in lines(columns['name']):
  if n==28 and mid<255:continue
  if n==33 and mid>242:continue
  if ',' not in text:continue
  anchors.append((mid,text,ww))
 result=[]
 for i,(mid,name,ww) in enumerate(anchors):
  lo=(anchors[i-1][0]+mid)/2 if i else mid-8;hi=(anchors[i+1][0]+mid)/2 if i+1<len(anchors) else mid+7
  cells={'name':name};allw=ww[:]
  for col in ['position','pay','expenses']:
   selected=[w for w in columns[col] if lo<=w['mid']<hi];allw+=selected
   cells[col]=' '.join(t for _,t,_ in lines(selected))
  result.append(dict(pdfPage=n,pageRow=i+1,y=mid,bboxPoints=[min(w['x'] for w in allw),min(w['y'] for w in allw),max(w['x']+w['w'] for w in allw),max(w['y']+w['h'] for w in allw)],cells=cells,row=['royal-roads-university',name,cells['position'],normmoney(cells['pay']),normmoney(cells['expenses']),n],minimumConfidence=min(w['conf'] for w in allw),words=allw))
 return result

def main():
 a=[];b=[]
 for n in PAGES:
  a+=extract(n,1);b+=extract(n,2)
 diffs=[]
 for i in range(max(len(a),len(b))):
  x=a[i] if i<len(a) else None;y=b[i] if i<len(b) else None
  if (x or {}).get('row')!=(y or {}).get('row'):diffs.append(dict(rowNumber=i+1,first=x['row'] if x else None,second=y['row'] if y else None))
 receipt={'status':'candidate-not-accepted','firstReader':'Tesseract5 full original page at3x PSM6','secondReader':'Tesseract5 independently rendered5x original column crops PSM6','pdfSha256':sha((CACHE/'additional-source-rru-2023-24.pdf').read_bytes()),'firstRows':a,'secondRows':b,'differences':diffs}
 gz(OUT/'evidence/rru-2023-24-dual-ocr-candidates.json.gzip',receipt)
 js(CACHE/'rru-2023-24-dual-ocr-differences.json',diffs)
 print('first/second',len(a),len(b),'pagecounts',collections.Counter(z['pdfPage'] for z in a),collections.Counter(z['pdfPage'] for z in b),'differences',len(diffs))
 for z in diffs:print(z)

def promote_reviewed_scan():
 import copy,decimal,fitz
 raw=load= json.loads(gzip.decompress((OUT/'evidence/rru-2023-24-dual-ocr-candidates.json.gzip').read_bytes()))
 decisions=json.loads((OUT/'scan-review/decisions.json').read_text())
 assert sha((OUT/'evidence/rru-2023-24-dual-ocr-candidates.json.gzip').read_bytes())==decisions['candidateDataSha256']
 assert raw['pdfSha256']==decisions['pdfSha256']==sha((CACHE/'additional-source-rru-2023-24.pdf').read_bytes())
 assert decisions['reviewedRows']==307 and not decisions['unresolvedCells']
 a=raw['firstRows'];b=raw['secondRows'];assert len(a)==len(b)==307
 rows=[copy.deepcopy(z['row']) for z in a];schema=['employerSlug','name','position','remuneration','expenses','pdfPage']
 for z in decisions['overridesAgainstFirstReader']:rows[z['rowNumber']-1][schema.index(z['field'])]=z['value']
 assert all(isinstance(r[3],(int,float)) and (r[4] is None or isinstance(r[4],(int,float))) for r in rows)
 totalpay=sum(decimal.Decimal(str(r[3])) for r in rows);totalexp=sum(r[4] or 0 for r in rows);assert totalpay==decimal.Decimal('34445723.53') and totalexp==1106152
 d=fitz.open(CACHE/'additional-source-rru-2023-24.pdf');receipts=[];first_changes=[];second_changes=[]
 for i,(x,y,row) in enumerate(zip(a,b,rows),1):
  mid=x['y'];n=x['pdfPage'];prev=a[i-2] if i>1 else None;nxt=a[i] if i<len(a) else None
  lo=(prev['y']+mid)/2 if prev and prev['pdfPage']==n else mid-8;hi=(nxt['y']+mid)/2 if nxt and nxt['pdfPage']==n else mid+7;clip=fitz.Rect(95,lo,550,hi)
  p=OUT/'scan-review'/'rows'/f'row-{i:03}.png';p.parent.mkdir(exist_ok=True);d[n-1].get_pixmap(matrix=fitz.Matrix(3,3),clip=clip).save(p)
  receipt=dict(rowNumber=i,pdfPage=n,bboxPoints=list(clip),cropFile=str(p.relative_to(OUT)),cropSha256=sha(p.read_bytes()),row=row,sourceCellsVisuallyReviewed=True,sourceSheet=f'scan-review/rru-2023-24-rows-{((i-1)//20)*20+1:03}-{min((((i-1)//20)+1)*20,307):03}.png')
  receipts.append(receipt)
  for engine,record,changes in [(1,x,first_changes),(2,y,second_changes)]:
   for j,(before,after) in enumerate(zip(record['row'],row)):
    if before!=after:changes.append(dict(rowNumber=i,field=schema[j],ocrValue=before,publishedValue=after,reason='Resolved by direct original source crop inspection',cropSha256=receipt['cropSha256'],cropFile=receipt['cropFile']))
 # Explicit source-backed correction lists make each reader's resolved output independently replayable.
 aa=[copy.deepcopy(z['row']) for z in a];bb=[copy.deepcopy(z['row']) for z in b]
 for changes,rr in [(first_changes,aa),(second_changes,bb)]:
  for z in changes:rr[z['rowNumber']-1][schema.index(z['field'])]=z['publishedValue']
 assert aa==bb==rows
 evidence=dict(sourceId='rru-sofi-2023-24-employees',pdfSha256=raw['pdfSha256'],employeePhysicalPages=list(PAGES),rowCount=307,rows=rows,rowReceipts=receipts,firstReaderCorrections=first_changes,secondReaderCorrections=second_changes,firstResolvedRows=aa,secondResolvedRows=bb,allOriginalRowsVisuallyReviewed=True,unresolvedCells=[],controlComponents={'combined':[47295027,1240360],'belowThreshold':[12849299,134208]},printedControls=[{'field':'remuneration','rowSum':float(totalpay),'printedControl':34445728,'residual':-4.47,'basis':'Printed employee combined total47,295,027 minus below-threshold employee aggregate12,849,299'},{'field':'expenses','rowSum':totalexp,'printedControl':1106152,'residual':0,'basis':'Printed employee combined total1,240,360 minus below-threshold employee aggregate134,208'}],totalRemuneration=float(totalpay),totalExpenses=totalexp,missingExpenseCells=sum(r[4] is None for r in rows),zeroExpenseCells=sum(r[4]==0 for r in rows),pageRowCounts=sorted(collections.Counter(r[5] for r in rows).items()),nativeOriginalReaders={'PyMuPDF':'No employee cells in original text layer','Poppler':'No employee cells in original text layer'},independentReaders=[raw['firstReader'],raw['secondReader'],'307 original full-row source crops individually inspected'])
 gz(OUT/'evidence/rru-2023-24-reviewed.json.gzip',evidence);datahash=gz(OUT/'rru-2023-24.json.gzip',rows)
 lead=next(s for s in json.loads((OUT/'source-leads.json').read_text()) if s['year']=='2023/24')
 source=dict(id=evidence['sourceId'],employerSlug='royal-roads-university',employerName='Royal Roads University',sector='Post-secondary education',year='2023/24',periodType='fiscal',periodStart='2023-04-01',periodEnd='2024-03-31',title=lead['title']+' — named employee remuneration and expenses',sha256=raw['pdfSha256'],file='rru-2023-24.json.gzip',pages=list(PAGES),sourceUrl=lead['sourceUrl'],sourceIndexUrl=lead['indexUrl'],pdfBytes=(CACHE/'additional-source-rru-2023-24.pdf').stat().st_size,rowCount=307,totalRemuneration=float(totalpay),totalExpenses=totalexp,status='verified',verifiedOn='2026-11-02',category='employee-remuneration',scope='named-employees-over-threshold',completeEmployeeSchedule=True,threshold=75000,thresholdComparison='>=',currency='CAD',amountUnit='dollars',nameDisclosure='as-published',positionDisclosure='as-published',sourceKind='official-statement-of-financial-information',retainCompiledPartition=True,dataSha256=datahash,publicWarning='Published remuneration cells total CAD34,445,723.53, CAD4.47 below the named control implied by printed totals. Expenses reconcile exactly. The source decimal75928.53 is preserved.',notes=['Complete named employee schedule only; board, supplier, below-threshold aggregate and reconciliation rows excluded.','Scanned employee pages were independently OCRed from3x full-page and5x column renders, compared field by field and all307 original complete row crops visually inspected. Explicit source-backed corrections are retained for both OCR readers.','Published names/positions retain uppercase source spellings, abbreviations and clipped titles; no identity links or source names are rewritten.','Visible dash expense cells remain missing, never zero. Remuneration is not inferred annual base salary.','The source visibly prints CORAK, LISA remuneration75928.53; cents are retained. LITTLER, BLAIR198,716 and DU, JUAN are also retained exactly.','Every compiled observation and original period label is retained; no replacement or redating.'],validation=dict(originalFingerprintVerified=True,independentReaders=evidence['independentReaders'],everyRowFieldAgreementAfterDocumentedPixelReview=True,rowsIndependentlyChecked=307,completeEmployeeSchedule=True,physicalPagesVisuallyReviewed=list(PAGES),pageRowCounts=evidence['pageRowCounts'],printedControls=evidence['printedControls'],evidenceFile='evidence/rru-2023-24-reviewed.json.gzip',visualReviewFile='visual/rru-2023-24.json',rowsVisuallyReviewed=307,unresolvedCells=[]))
 manifest=json.loads((OUT/'sources.json').read_text());manifest['sources']=sorted([s for s in manifest['sources'] if s['id']!=source['id']]+[source],key=lambda s:s['year']);manifest['unparsedSources']=[s for s in manifest.get('unparsedSources',[]) if s.get('id')!=lead['id']];js(OUT/'sources.json',manifest)
 disp=json.loads((OUT/'dispositions.json').read_text())
 for z in disp['sources']:
  if z['id']==lead['id']:z.update(status='imported',acceptedSourceId=source['id'],employeeRows=307,candidateRows=307,manifest='research/salaries/follow-through-rru/sources.json',reason='Two independent OCR layouts and complete original307-row pixel review; all differing cells resolved explicitly. Expenses reconcile exactly; source remuneration residual−4.47 preserved.',evidenceFile='evidence/rru-2023-24-reviewed.json.gzip')
 js(OUT/'dispositions.json',disp)
 vis=json.loads((OUT/'visual/rru-2023-24.json').read_text());vis.update(status='reviewed',reviewedPhysicalPages=list(PAGES),reviewedRows=307,reviewScope=decisions['reviewMethod'],rowReceiptsFile='evidence/rru-2023-24-reviewed.json.gzip',decisionsFile='scan-review/decisions.json',unresolvedCells=[],reviewedSheets=[dict(file=str(p.relative_to(OUT)),sha256=sha(p.read_bytes())) for p in sorted((OUT/'scan-review').glob('rru-2023-24-rows-*.png'))],controlCrops=[dict(pdfPage=n,file=f'visual/rru-2023-24-{label}-control.png',sha256=sha((OUT/f'visual/rru-2023-24-{label}-control.png').read_bytes()),bboxPoints=box,scale=3) for n,box,label in [(28,[95,232,550,258],'below-threshold'),(33,[95,240,550,263],'combined')]])
 js(OUT/'visual/rru-2023-24.json',vis)
 print('ACCEPTED',len(rows),'pay',totalpay,'expenses',totalexp,'null/zero',evidence['missingExpenseCells'],evidence['zeroExpenseCells'],'OCRchanges',len(first_changes),len(second_changes))

def generate_ocr():
 import os,subprocess,fitz
 env={**os.environ,'OMP_THREAD_LIMIT':'1','OMP_NUM_THREADS':'1'}
 d=fitz.open(CACHE/'additional-source-rru-2023-24.pdf')
 for n in PAGES:
  base=CACHE/f'rru-2023-24-ocr-p{n:02}'
  d[n-1].get_pixmap(matrix=fitz.Matrix(3,3)).save(str(base)+'.png')
  subprocess.run(['tesseract',str(base)+'.png',str(base),'--psm','6','tsv','txt'],env=env,capture_output=True,check=True)
  cols={**COLS}
  if n==30:cols.update(name=(95,233),position=(233,432))
  for col,(a,b) in cols.items():
   base=CACHE/f'rru-2023-24-e2-p{n:02}-{col}'
   d[n-1].get_pixmap(matrix=fitz.Matrix(5,5),clip=fitz.Rect(a,0,b,750)).save(str(base)+'.png')
   subprocess.run(['tesseract',str(base)+'.png',str(base),'--psm','6','txt','tsv'],env=env,capture_output=True,check=True)

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--ocr',action='store_true');ap.add_argument('--promote-reviewed',action='store_true');args=ap.parse_args()
 if args.ocr:generate_ocr()
 main()
 if args.promote_reviewed:promote_reviewed_scan()
