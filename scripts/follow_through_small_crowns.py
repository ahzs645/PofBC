#!/usr/bin/env python3
"""Reconstruct the assigned Crown SOFI employee cohorts from fingerprinted originals.

Two native readers: PyMuPDF coordinate words and Poppler's layout text. OCR scan
has two independent segmentation passes plus source-pixel adjudication, recorded
in evidence/ocr-review.json. No printed amount is inferred or forced to balance.
"""
import argparse, collections, gzip, hashlib, json, pathlib, re, subprocess, urllib.request
import fitz
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/follow-through-small-crowns'
DEFAULT_CACHE=pathlib.Path('/workspace/salary-source-follow-through/cache-small-crowns')
PAGES={'bcfsa-2019-20':[3,3],'bcfsa-2021-22':[7,11],'bcfsa-2022-23':[7,13],'bcfsa-2023-24':[8,14],'bcfsa-2024-25':[8,15],'bcfsa-2025-26':[9,17],'pavco-2024-25':[4,6],'bcib-2019-20':[20,20],'bcib-2020-21':[24,24],'bcib-2021-22':[24,28],'bcib-2022-23':[25,31],'bcib-2023-24':[24,33],'bcib-2024-25':[25,38]}
MONEY=re.compile(r'^-?\d+(?:,\d{3})*(?:\.\d+)?$')
ROW=re.compile(r'^(.+?,.+?)\s{2,}\$?\s*(-?\d[\d,]*)(?:\s+\$?\s*(-?\d[\d,]*|-))?\s*$')
def sha(b):return hashlib.sha256(b).hexdigest()
def norm(s):return re.sub(r'\s+',' ',s).strip()
def amount(s):return None if s in (None,'','-','–','—') else int(s.replace(',',''))
def lines(page):
 groups=[]
 for w in sorted(page.get_text('words'),key=lambda w:(w[1],w[0])):
  dest=next((g for g in reversed(groups[-3:]) if abs(g[0]-w[1])<2),None)
  if dest is None:groups.append([w[1],[w]])
  else:dest[1].append(w)
 return [(y,sorted(ws,key=lambda w:w[0])) for y,ws in groups]
def native_rows(pdf,key,slug):
 d=fitz.open(pdf)
 return coordinate_rows({str(i+1):p.get_text('words') for i,p in enumerate(d)},key,slug)

def coordinate_rows(pages,key,slug):
 a,b=PAGES[key];out=[];markers=[]
 for pn in range(a,b+1):
  class WordPage:
   def get_text(self,kind):return pages[str(pn)]
  groups=lines(WordPage());floor=0
  if pn==a and (key.startswith('bcfsa') or key.startswith('pavco') or key=='bcib-2019-20'):
   candidates=[y for y,ws in groups if norm(' '.join(w[4] for w in ws)) in ['Other Employees','Employees','2. Other Employees','2. Others Employees (excluding those listed in Part 1 above)','Employees who received remuneration of more than $75,000']]
   assert candidates,(key,'no employee boundary');floor=max(candidates)
  ceiling=min([y for y,ws in groups if y>floor and re.match(r'(Consolidated|Paid to employees|Total: employees)',norm(' '.join(w[4] for w in ws)),re.I)]+[9999])
  split=key.startswith('bcib') and key>='bcib-2022-23'
  boundary={'bcib-2022-23':320,'bcib-2023-24':318,'bcib-2024-25':305}.get(key,9999)
  for y,ws in groups:
   if y<=floor or y>=ceiling:continue
   for side in ([0,1] if split else [0]):
    v=[w for w in ws if not split or (w[0]<boundary)==(side==0)]
    if not v:continue
    money=[w for w in v if MONEY.match(w[4]) or w[4]=='-']
    if not money or ',' not in ' '.join(w[4] for w in v if w[0]<money[0][0]):continue
    pay=money[0];namewords=[w for w in v if w[0]<pay[0] and w[4]!='$'];title=None
    if key.startswith('pavco'):
     title=norm(' '.join(w[4] for w in namewords if w[0]>=150)).removesuffix(' *')
     namewords=[w for w in namewords if w[0]<150]
    name=norm(' '.join(w[4] for w in namewords));name=re.sub(r',\s*',', ',name)
    marker=name.endswith('*');name=name.removesuffix('*')
    if not name or not re.search(r'[A-Za-z]',name) or re.search(r'\d',name) or amount(pay[4])<75000:continue
    assert len(money)<=2,(key,pn,name,[w[4] for w in money])
    exp=amount(money[1][4]) if len(money)==2 else None
    out.append([slug,name,title,amount(pay[4]),exp,pn]);markers.append(marker)
 return out,markers

def poppler_rows(pdf,key,slug):
 raw=subprocess.check_output(['pdftotext','-layout',str(pdf),'-']).decode()
 return layout_rows(raw,key,slug),raw

def layout_rows(raw,key,slug):
 pages=raw.split('\f');a,b=PAGES[key];out=[]
 for pn in range(a,b+1):
  ls=pages[pn-1].splitlines();floor=0
  if pn==a and (key.startswith('bcfsa') or key.startswith('pavco') or key=='bcib-2019-20'):
   floor=max(i for i,s in enumerate(ls) if norm(s) in ['Other Employees','Employees','2. Other Employees','2. Others Employees (excluding those listed in Part 1 above)','Employees who received remuneration of more than $75,000'])
  split=key.startswith('bcib') and key>='bcib-2022-23'
  cut=None
  if split:
   header=next(s for s in ls if s.count('Name')==2);cut=header.index('Name',header.index('Name')+4)
  for s in ls[floor+1 if floor else 0:]:
   if re.match(r'(Consolidated|Paid to employees|Total: employees)',s.strip(),re.I):break
   name_starts=[m.start(1) for m in re.finditer(r"(?:^|\s)([A-Za-z][A-Za-z .’'–-]*,\s*[A-Za-z][A-Za-z .’'*-]*?)\s{2,}\$?\s*\d",s)] if split else []
   pieces=[s[name_starts[i]:name_starts[i+1] if i+1<len(name_starts) else len(s)] for i in range(len(name_starts))] if split else [s]
   for v in pieces:
    v=v.strip();title=None
    if key.startswith('pavco'):
     parts=re.split(r'\s{2,}',v.replace('$',' '))
     if len(parts)!=4 or ',' not in parts[0]:continue
     name,title,pay,exp=parts;pay=pay.replace('$','').strip();exp=exp.replace('$','').strip();title=title.removesuffix(' *')
     if not MONEY.match(pay):continue
    else:
     m=ROW.match(v)
     if not m:continue
     name,pay,exp=m.groups()
    name=re.sub(r',\s*',', ',norm(name)).removesuffix('*')
    if re.search(r'\d',name) or amount(pay)<75000:continue
    out.append([slug,name,title,amount(pay),amount(exp),pn])
 return out

def json_bytes(value,compact=False):
 return (json.dumps(value,ensure_ascii=False,separators=(',',':') if compact else None,indent=None if compact else 2)+'\n').encode()
def write_json(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(json_bytes(value))
def sums(rows):return [sum(r[3] for r in rows),sum(r[4] or 0 for r in rows)]
def counter(rows):return collections.Counter(tuple(r) for r in rows)
def scan_rows(evidence=OUT/'evidence'):
 """Independently parse retained OCR passes; only pixel-adjudicated punctuation is fixed."""
 full=[];columns=[]
 def val(s):return int(s.replace(',','').replace('(','-').replace(')',''))
 for pn,n in [(7,21),(8,43),(9,43),(10,5)]:
  raw=(evidence/'ocr'/f'p{pn:02}-psm3.txt').read_text().replace('108 ,444','108,444')
  if pn==7:raw=raw.split('Other Employees')[1]
  if pn==10:raw=raw.split('Consolidated total')[0]
  a=[]
  for line in raw.splitlines():
   m=re.match(r'^(.+?,.+?)\s+(\d[\d,]*)\s+(\(?[\d,]+\)?)$',line)
   if m:a.append(['bc-financial-services-authority',m[1],None,val(m[2]),val(m[3]),pn])
  cols=[[s.strip() for s in (evidence/'ocr'/f'p{pn:02}-{col}.txt').read_text().splitlines() if s.strip()] for col in ['name','pay','expense']]
  assert len(a)==n and all(len(c)==n for c in cols),(pn,[len(c) for c in cols])
  b=[]
  for name,pay,expense in zip(*cols):
   if pn==10 and name=='Zhai, Xuetong':
    assert pay=='83.616';pay='83,616'  # Reviewed in original pixels; see ocr-review.json.
   b.append(['bc-financial-services-authority',name,None,val(pay),val(expense),pn])
  assert a==b,(pn,'independent OCR disagreement')
  full+=a;columns+=b
 return full,columns

def refresh_ocr(pdf,cache):
 """Regenerate both source OCR passes, sequentially and with bounded CPU threads."""
 import os
 import numpy as np
 from PIL import Image
 out=cache/'bcfsa-2020-21-ocr';out.mkdir(exist_ok=True)
 env={**os.environ,'OMP_THREAD_LIMIT':'1','OMP_NUM_THREADS':'1'}
 doc=fitz.open(pdf)
 for pn,y0,y1 in [(7,1707,2831),(8,531,2844),(9,534,2845),(10,531,791)]:
  base=out/f'p{pn:02}';doc[pn-1].get_pixmap(dpi=300).save(str(base)+'.png')
  subprocess.run(['tesseract',str(base)+'.png',str(base)+'-psm3','--psm','3'],env=env,check=True,stdout=subprocess.DEVNULL)
  pixels=np.array(Image.open(str(base)+'.png').convert('L'))
  ys=np.where((pixels[:,350:2150]<140).sum(axis=1)>1300)[0]
  for y in ys:pixels[max(0,y-3):y+4,:]=255
  for col,x0,x1 in [('name',355,1450),('pay',1472,1840),('expense',1860,2140)]:
   target=out/f'p{pn:02}-{col}';Image.fromarray(pixels[y0:y1,x0:x1]).save(str(target)+'.png')
   subprocess.run(['tesseract',str(target)+'.png',str(target),'--psm','6'],env=env,check=True,stdout=subprocess.DEVNULL)
  # Refresh is a verification step. Keep reviewed snapshots immutable.
  for col in ['psm3','name','pay','expense']:
   expected=(OUT/'evidence/ocr'/f'p{pn:02}-{col}.txt').read_text()
   observed=(out/f'p{pn:02}-{col}.txt').read_text()
   assert observed==expected,(pn,col,'OCR changed; review original pixels before replacing snapshot')

def signed_money(value):
 return ('+' if value>=0 else '−')+'$'+f'{abs(value):,}'

def warning_for(key,rows,spec):
 warnings=[];observed=sums(rows);implied=[a-b for a,b in zip(spec['totalEmployees'],spec['belowThreshold'])]
 residual=[a-b for a,b in zip(observed,implied)]
 if key=='bcfsa-2019-20':
  warnings.append('This disclosure covers November 1, 2019 (commencement of operations) through March 31, 2020, a partial fiscal year. Published named remuneration rows sum to $539,126 versus the printed named subtotal $539,127; named expenses total $82,978 versus $82,977 implied by total less below-threshold controls. Values are unchanged; causes unknown.')
 elif any(residual):
  warnings.append(f"Published named rows sum to ${observed[0]:,} remuneration and ${observed[1]:,} expenses, differing from the printed {'named subtotal' if spec['directNamedSubtotal'] else 'total less below-threshold controls'} by {signed_money(residual[0])} and {signed_money(residual[1])}. Original row values are retained; causes unknown.")
 negatives=[(r[1],r[4]) for r in rows if r[4] is not None and r[4]<0]
 if negatives:warnings.append('The source publishes negative expense adjustments: '+', '.join(f'{n} ({signed_money(v)})' for n,v in negatives)+'. These remain negative; printed numeric zeros remain 0.')
 return ' '.join(warnings) or None

def source_pages(key):
 a,b=PAGES[key];pages=list(range(a,b+1))
 if key.startswith('bcib'):
  if key!='bcib-2019-20':pages.append(a-1)
  if key in ['bcib-2019-20','bcib-2020-21','bcib-2022-23','bcib-2023-24']:pages.append(b+1)
 return sorted(set(pages))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache',type=pathlib.Path,default=DEFAULT_CACHE);p.add_argument('--refresh-ocr',action='store_true');args=p.parse_args();cache=args.cache
 leads=json.loads((OUT/'leads.json').read_text());specs=json.loads((OUT/'control-spec.json').read_text());sources=[];dispositions=[]
 for lead in sorted(leads,key=lambda v:v['id']):
  key=lead['id'].removeprefix('additional-source-');pdf=cache/(lead['id']+'.pdf');cache.mkdir(parents=True,exist_ok=True)
  if not pdf.exists():
   with urllib.request.urlopen(lead['sourceUrl'],timeout=90) as r:pdf.write_bytes(r.read())
  original=pdf.read_bytes();assert sha(original)==lead['verification']['sha256'],key
  doc=fitz.open(pdf);assert len(doc)==lead['verification']['pdfPages'],key
  spec=specs[key];slug=lead['employerSlug'];scan=key=='bcfsa-2020-21'
  if scan:
   if args.refresh_ocr:refresh_ocr(pdf,cache)
   rows,other=scan_rows();markers=[False]*len(rows);selected=[7,8,9,10]
   readers=['Tesseract5 PSM3 full original scan','Tesseract5 PSM6 independent column crops']
   rowproof=[]
   scan_review=json.loads((OUT/'evidence/ocr-review.json').read_text())
   for pn in selected:
    page_rows=[r for r in rows if r[5]==pn]
    boundaries=scan_review['rowBoundaryPixelsByPhysicalPage'][str(pn)]
    cells=[[s.strip() for s in (OUT/'evidence/ocr'/f'p{pn:02}-{col}.txt').read_text().splitlines() if s.strip()] for col in ['name','pay','expense']]
    for i,r in enumerate(page_rows):
     rowproof.append({'normalized':r,'physicalPage':pn,'sourceRowNumberOnPage':i+1,'original300DpiPixelRect':[341,boundaries[i],2152,boundaries[i+1]],'independentColumnOcrCells':[c[i] for c in cells],'allFieldsVisuallyReviewedAgainstOriginal':True})
   rowproof_file='evidence/bcfsa-2020-21.rows.json.gzip'
   (OUT/rowproof_file).write_bytes(gzip.compress(json_bytes(rowproof,True),mtime=0))
   evidence_files=[rowproof_file,'evidence/ocr-review.json']+[f'evidence/ocr/p{pn:02}-{col}.txt' for pn in selected for col in ['psm3','name','pay','expense']]
   control_text=(OUT/'evidence/ocr/p10-psm3.txt').read_text()
   period_text=(OUT/'evidence/ocr/p07-psm3.txt').read_text()
  else:
   rows,markers=native_rows(pdf,key,slug);other,raw=poppler_rows(pdf,key,slug);selected=source_pages(key)
   readers=['PyMuPDF positioned words','Poppler pdftotext -layout']
   rawpages=raw.split('\f');extracted='\f'.join(rawpages[i-1] if i in selected else '' for i in range(1,len(doc)+1))
   (OUT/'evidence'/f'{key}.layout.txt').write_text(extracted)
   words={str(pn):doc[pn-1].get_text('words') for pn in selected}
   (OUT/'evidence'/f'{key}.words.json.gzip').write_bytes(gzip.compress(json_bytes(words,True),mtime=0))
   evidence_files=[f'evidence/{key}.layout.txt',f'evidence/{key}.words.json.gzip']
   control_text=rawpages[spec['controlPhysicalPage']-1]
   period_text=raw
   # The original PDF's table controls are also located independently in PyMuPDF text.
   native_control=doc[spec['controlPhysicalPage']-1].get_text()
   for v in spec['totalEmployees']+spec['belowThreshold']+(spec['directNamedSubtotal'] or []):
    assert f'{v:,}' in native_control,(key,'PyMuPDF control',v)
  for v in spec['totalEmployees']+spec['belowThreshold']+(spec['directNamedSubtotal'] or []):
   assert f'{v:,}' in control_text,(key,'layout/OCR control',v)
  endyear=int(lead['year'][:4])+1
  assert re.search(r'March\s+31,?\s+'+str(endyear),period_text),(key,'period end')
  if key=='bcfsa-2019-20':assert re.search(r'November\s+1,\s+2019',period_text)
  assert counter(rows)==counter(other),(key,'independent native field disagreement')
  assert len(rows)==spec['expectedRowCount'],key
  observed=sums(rows);implied=[a-b for a,b in zip(spec['totalEmployees'],spec['belowThreshold'])];residual=[a-b for a,b in zip(observed,implied)]
  assert residual==spec['expectedImpliedNamedResidual'],(key,observed,implied,residual)
  assert all(len(r)==6 and r[0]==slug and r[3]>=75000 for r in rows)
  normalized=json_bytes(rows,True);compressed=gzip.compress(normalized,mtime=0);filename=key+'.json.gzip';(OUT/filename).write_bytes(compressed)
  warning=warning_for(key,rows,spec);source_id='follow-through-'+key+'-employees'
  notes=['Complete named employee schedule; board/director, supplier, unnamed, aggregate and reconciliation rows excluded. Source names/initials retained without name expansion or identity inference; comma spacing normalized. Repeated names remain distinct observations.', 'The reported remuneration column is preserved as published and is not assumed to be base salary. Expenses remain separate. Printed dash/blank expense cells are null; printed numeric zeros remain 0. No amount is changed to reconcile controls.']
  definition=None;severance=None
  if key.startswith('bcib'):
   definition=f"Note 1: Remuneration includes base salary and other compensation for {lead['year']}."
   note2='Note 2: Majority of expenses are related to '+('travel to work sites.' if key<'bcib-2022-23' else 'employee travel and living out allowances.')
   notes+=[definition,note2,'All named employees in this legal employer’s published employee table are included. Earlier reports do not identify an individual employee’s corporate/project cohort; no category or title is inferred.']
   if key=='bcib-2023-24':notes.append('Note 3: 95% of remuneration are for CBA employees. This is an aggregate statement, not an individual employee classification.')
   if key=='bcib-2024-25':notes.append('The original asterisk denotes unionized skilled trades workers working on select provincial infrastructure projects and collectively representing 95% of total remuneration paid by BCIB. Asterisks are preserved by row index in the evidence receipt and removed from normalized name strings; unmarked employees are not assigned an inferred role.')
  elif key.startswith('bcfsa'):
   notes.append('No separate base-salary definition is imposed on the Remuneration column. Pension/other benefits, employer CPP/EI, accruals and other reconciliation items are not allocated to individual employees.')
   if key!='bcfsa-2019-20':severance='"Compensation" means regular salary excluding benefits.';notes.append('The regular-salary definition of Compensation appears in the severance statement; it is retained as context and is not substituted for the table’s Remuneration label.')
  else:notes.append('Source footnote: "* expenses includes travel related to business development". Marker is removed from normalized position text; original titles and marker context remain in the source layout evidence.')
  pagecounts=collections.Counter(r[5] for r in rows);visual=[7,8,9,10] if scan else [spec['controlPhysicalPage']]
  if key in ['bcib-2022-23','bcib-2023-24']:visual=sorted(set(visual+[PAGES[key][0]]));evidence_files.append(f'evidence/{key}-bandila.png')
  direct=spec['directNamedSubtotal'];directres=[a-b for a,b in zip(observed,direct)] if direct else None
  control_image=f'evidence/{key}.controls.png'
  cp=doc[spec['controlPhysicalPage']-1]
  if scan:clip=fitz.Rect(75,185,525,245)
  else:
   ys=[y for y,ws in lines(cp) if re.match(r'(Consolidated|Paid to employees|Total: employees)',norm(' '.join(w[4] for w in ws)),re.I)]
   assert ys,(key,'control image boundary')
   y=min(ys);clip=fitz.Rect(35,max(0,y-40 if key=='bcfsa-2019-20' else y-10),580,min(cp.rect.height,y+115))
  cp.get_pixmap(dpi=180,clip=clip).save(OUT/control_image)
  evidence_files.append(control_image)
  receipt={'version':1,'sourceId':source_id,'leadId':lead['id'],'sourceUrl':lead['sourceUrl'],'sourceIndexUrl':lead['indexUrl'],'checkedOn':'2026-11-02','originalSha256':sha(original),'originalBytes':len(original),'originalPdfPageCount':len(doc),'period':{'start':'2019-11-01' if key=='bcfsa-2019-20' else lead['year'][:4]+'-04-01','end':str(endyear)+'-03-31','partial':key=='bcfsa-2019-20','evidence':'Original schedule year-ended header; first BCFSA schedule explicitly gives commencement date and period end.'},'employeePhysicalPages':sorted(pagecounts),'retainedSourceEvidencePages':selected,'readerNames':readers,'primaryRowCount':len(rows),'independentRowCount':len(other),'everyRowFieldMultisetEqual':True,'primaryNormalizedSha256':sha(normalized),'independentRowMultisetSha256':sha(json_bytes(sorted(other,key=lambda r:(r[5],r[1],r[3],str(r[4]))),True)),'pageControls':[{'physicalPage':pn,'rowCount':pagecounts[pn],'remuneration':sums([r for r in rows if r[5]==pn])[0],'expenses':sums([r for r in rows if r[5]==pn])[1]} for pn in sorted(pagecounts)],'controls':{'physicalPage':spec['controlPhysicalPage'],'printedTotalEmployees':spec['totalEmployees'],'printedBelowThreshold':spec['belowThreshold'],'printedDirectNamedSubtotal':direct,'impliedNamedControl':implied,'observedAllNamedRows':observed,'residualNamedMinusImplied':residual,'residualNamedMinusDirect':directres,'units':'CAD whole dollars','residualCause':'Unknown; preserved as printed.' if any(residual) or (directres and any(directres)) else None},'physicalPagesVisuallyReviewed':visual,'sourceRowReview':'Every native employee row compared field-for-field between independent PDF readers; source-pixel review of printed control totals and ambiguous glyph/layout cases. Every scan employee row and control additionally visually reviewed.','explicitZeroExpenseRows':sum(r[4]==0 for r in rows),'nullExpenseRows':sum(r[4] is None for r in rows),'negativeExpenseRows':[{'rowIndex':i,'name':r[1],'value':r[4],'physicalPage':r[5]} for i,r in enumerate(rows) if r[4] is not None and r[4]<0],'repeatedDisclosedNames':{n:v for n,v in collections.Counter(r[1] for r in rows).items() if v>1},'exactDuplicateSixFieldRows':len(rows)-len(counter(rows)),'excludedScopes':['board-director-remuneration','suppliers','below-threshold-aggregate','reconciliation-adjustments','employer-tax-benefit-aggregates'],'remunerationDefinitionVerbatim':definition,'severanceCompensationDefinitionContext':severance,'publicWarning':warning,'rawEvidenceFiles':[{'file':f,'sha256':sha((OUT/f).read_bytes())} for f in evidence_files]}
  if key=='bcib-2024-25':receipt['sourceCohortMarkers']={'definition':'* Denotes unionized skilled trades workers working on select provincial infrastructure projects, and collectively represents 95% of total remuneration paid by BCIB.','markedNamedEmployees':sum(markers),'unmarkedNamedEmployees':len(markers)-sum(markers),'markedRowIndexes':[i for i,m in enumerate(markers) if m]}
  if key in ['bcib-2022-23','bcib-2023-24']:receipt['glyphReview']='Bandila, l: the source encodes the initial as lowercase l; both independent text readers agree and the printed glyph was inspected. No expansion or case inference is made.'
  evidence=f'evidence/{key}.json';write_json(OUT/evidence,receipt)
  employer={'bcfsa':'BC Financial Services Authority','bcib':'BC Infrastructure Benefits Inc.','pavco':'B.C. Pavilion Corporation'}[key.split('-')[0]]
  source={'id':source_id,'employerSlug':slug,'employerName':employer,'sector':'Crown corporations','year':lead['year'],'periodType':'fiscal','periodStart':receipt['period']['start'],'periodEnd':receipt['period']['end'],'title':f'{employer}: named employee remuneration and expenses, {lead["year"]}','sourceUrl':lead['sourceUrl'],'sourceIndexUrl':lead['indexUrl'],'sha256':sha(original),'pdfBytes':len(original),'file':filename,'dataSha256':sha(compressed),'normalizedSha256':sha(normalized),'rowCount':len(rows),'totalRemuneration':observed[0],'totalExpenses':observed[1],'pages':sorted(pagecounts),'status':'verified','verifiedOn':'2026-11-02','category':'employee-remuneration','scope':'named-employees-over-threshold','completeEmployeeSchedule':True,'threshold':75000,'thresholdComparison':'>=' if key.startswith('pavco') else '>','currency':'CAD','amountUnit':'dollars','amountPrecision':'whole-dollar','nameDisclosure':'as-published','positionDisclosure':'published' if key.startswith('pavco') else 'not-published','sourceKind':'official-statement-of-financial-information','retainCompiledPartition':True,'notes':notes,'provenanceFile':evidence,'provenanceSha256':sha((OUT/evidence).read_bytes()),'validation':{'originalFingerprintVerified':True,'sourcePdfPageCount':len(doc),'independentReaders':readers,'everyRowFieldAgreement':True,'rowsIndependentlyChecked':len(rows),'completeEmployeeSchedule':True,'physicalPagesVisuallyReviewed':visual,'pageRowCounts':[[pn,pagecounts[pn]] for pn in sorted(pagecounts)],'sourceControls':receipt['controls'],'printedControls':[{'field':f,'printedControl':c,'rowSum':v,'residual':v-c,'basis':'total employees minus below-threshold aggregate'} for f,c,v in zip(['pay','expenses'],implied,observed)],'compiledPartitionRetained':True,'evidenceFile':evidence}}
  if warning:source['publicWarning']=warning
  sources.append(source)
  dispositions.append({'leadId':lead['id'],'employerSlug':slug,'year':lead['year'],'status':'accepted-official-with-public-qualifications' if warning else 'accepted-official','sourceId':source_id,'rowCount':len(rows),'normalizedPayload':filename,'dataSha256':sha(compressed),'originalSourceSha256':sha(original),'actualPeriodStart':receipt['period']['start'],'actualPeriodEnd':receipt['period']['end'],'acceptedScope':'employee-remuneration','excludedScopes':receipt['excludedScopes'],'unacceptedNamedScopes':[{'scope':'board-director-remuneration','reason':'Separate board schedule intentionally excluded from authorized employee cohort import.'}],'blockers':[],'evidence':evidence,'publicWarning':warning,'compiledRowsDeleted':0})
  print(key,len(rows),observed,'residual',residual,flush=True)
 write_json(OUT/'sources.json',{'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources})
 write_json(OUT/'dispositions.json',{'version':1,'checkedOn':'2026-11-02','assignedReports':14,'acceptedEmployeeReports':len(sources),'acceptedEmployeeRows':sum(s['rowCount'] for s in sources),'heldEmployeeReports':0,'dispositions':dispositions})
 print('Accepted',len(sources),'employee schedules;',sum(s['rowCount'] for s in sources),'rows.')
if __name__=='__main__':main()
