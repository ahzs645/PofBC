#!/usr/bin/env python3
"""Reproduce the reviewed InBC 2022/23–2024/25 named employee schedules.

Requires PyMuPDF and Poppler pdftotext. Downloads only official, hash-pinned PDFs.
Does not change the collection registry, compiled records or public outputs.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,re,subprocess,tempfile,urllib.request
from pathlib import Path
from collections import Counter
import fitz
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/sector-crowns'
INDEX='https://inbcinvestment.com/accountability-governance/'
SPEC=[
 {'end':2023,'page':28,'count':9,'controlPay':1298918,'controlExpenses':102273,'payResidual':0,'expenseResidual':0,'sha256':'5c2c91aedda3251af04c9cf83c40a41188c22032c0309419fc70451bab08fa18','url':'https://inbcinvestment.com/wp-content/uploads/2023/12/InBC-Statement-of-Financial-Information-March-31-2023-Signed.pdf'},
 {'end':2024,'page':30,'count':15,'controlPay':2334320,'controlExpenses':105309,'payResidual':1,'expenseResidual':0,'sha256':'0d299af9e848a44091e84e79cf4fe0215c79e471745eb5213e3edb66af7654d2','url':'https://inbcinvestment.com/wp-content/uploads/2025/03/InBC-Statement-of-Financial-Information-March-31-2024-Signed.pdf'},
 {'end':2025,'page':29,'count':17,'controlPay':2874812,'controlExpenses':152072,'payResidual':0,'expenseResidual':1,'sha256':'c6e95c9635d1b42c593e4094d795ff3b74039e5159f238498d87ae415f1277e5','url':'https://inbcinvestment.com/wp-content/uploads/2025/10/FIA-Return-March-31-2025_Final_Chair-signed.pdf'},
]
def sha(data):return hashlib.sha256(data).hexdigest()
def compact(value):return (json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def money(value):
 if not re.fullmatch(r'\d{1,3}(?:,\d{3})*|\d+',value):raise ValueError(f'Invalid money {value!r}')
 return int(value.replace(',',''))
def parse_layout(text):
 """Independent Poppler layout reader; numeric subtotal is never a person."""
 if '2. Employees' not in text:raise ValueError('Missing employee section')
 block=text.split('2. Employees',1)[1].split('3. Total',1)[0]
 rows=[];controls=None
 for line in block.splitlines():
  if not line.strip():continue
  m=re.fullmatch(r'\s*(\S.*?\S)\s{2,}([\d,]+)(?:\s{2,}([\d,]+))?\s*',line)
  if m:
   if re.fullmatch(r'[\d,]+',m[1]):
    if controls is not None:raise ValueError('Duplicate subtotal')
    controls=[money(m[1]),money(m[2])];continue
   if not re.fullmatch(r'[A-Za-z ,.-]+',m[1]):raise ValueError(f'Unexpected employee {m[1]!r}')
   rows.append([m[1],money(m[2]),money(m[3]) if m[3] else None])
  elif re.search(r'\d',line) and not re.search(r'\$75,000',line):
   raise ValueError(f'Unparsed numeric employee line {line!r}')
 if not rows or controls is None:raise ValueError('Missing named rows or subtotal')
 return rows,controls

def parse_positioned(page):
 words=page.get_text('words');ystart=next(w[1] for w in words if w[4]=='Employees')
 yend=next((w[1] for w in words if w[4]=='3.' and w[1]>ystart),page.rect.height)
 groups={}
 for w in words:
  if ystart+20<w[1]<yend:groups.setdefault(round(w[1]),[]).append(w)
 rows=[];evidence=[];control=None
 for y,ww in sorted(groups.items()):
  ww.sort(key=lambda w:w[0]);name=' '.join(w[4] for w in ww if w[0]<350);nums=[w[4] for w in ww if w[0]>=350]
  if not any(re.fullmatch('[0-9,]+',w[4]) for w in ww):continue
  if not nums or len(nums)>2:raise ValueError('Unexpected monetary columns')
  if name:
   row=[name,money(nums[0]),money(nums[1]) if len(nums)>1 else None]
   if not re.fullmatch(r'[A-Za-z ,.-]+',name) or row[1]<=75000:raise ValueError('Unexpected named employee row')
   rows.append(row);evidence.append({'row':row,'words':ww})
  else:
   if control is not None or len(nums)!=2:raise ValueError('Invalid subtotal sequence')
   control=list(map(money,nums))
 return rows,control,evidence

def verify_pdf(data,spec):
 if sha(data)!=spec['sha256']:raise ValueError('Original PDF hash differs; re-review required')
 doc=fitz.open(stream=data,filetype='pdf');cover=doc[0].get_text()
 if f'Year ended March 31, {spec["end"]}' not in cover or 'InBC Investment Corp.' not in cover:raise ValueError('Unexpected source employer or period')
 page=doc[spec['page']-1];text=page.get_text()
 if '2. Employees with renumeration and expenses exceeding $75,000.' not in text:raise ValueError('Unexpected disclosure scope')
 rows,control,evidence=parse_positioned(page)
 with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
  f.write(data);f.flush();layout=subprocess.check_output(['pdftotext','-f',str(spec['page']),'-l',str(spec['page']),'-layout',f.name,'-']).decode()
 independent,independent_control=parse_layout(layout)
 if rows!=independent or control!=independent_control:raise ValueError('Independent readers disagree')
 if len(rows)!=spec['count'] or control!=[spec['controlPay'],spec['controlExpenses']]:raise ValueError('Source row count/control changed')
 totals=[sum(r[1] for r in rows),sum(r[2] for r in rows if r[2] is not None)]
 residual=[totals[0]-control[0],totals[1]-control[1]]
 if residual!=[spec['payResidual'],spec['expenseResidual']]:raise ValueError('Residual differs from reviewed source')
 result=[['inbc',*r[:1],None,*r[1:],spec['page']] for r in rows]
 ev={'originalPdfSha256':sha(data),'pdfPage':spec['page'],'coverText':cover,'approvalPageText':doc[1].get_text(),'scheduleText':text,'popplerLayoutText':layout,'positionedRows':evidence,'namedSubtotals':control,'rowSums':totals,'residuals':residual,'allFieldsAgree':True,'visuallyReviewedAllNamedRows':True,'renderedPageSha256':sha(page.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).tobytes('png'))}
 return result,ev

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cache-dir',type=Path,default=Path('/tmp/sector-crowns'));ap.add_argument('--output-dir',type=Path,default=OUT);ap.add_argument('--verify',action='store_true',help='compare generated files with existing collection without writing');a=ap.parse_args();a.cache_dir.mkdir(parents=True,exist_ok=True)
 outputs={};sources=[]
 for spec in SPEC:
  key=sha(spec['url'].encode())[:16];p=a.cache_dir/(key+'.pdf')
  if not p.exists():
   with urllib.request.urlopen(urllib.request.Request(spec['url'],headers={'User-Agent':'Mozilla/5.0 public source verification'}),timeout=60) as f:p.write_bytes(f.read())
  raw=p.read_bytes();rows,ev=verify_pdf(raw,spec);year=f'{spec["end"]-1}/{str(spec["end"])[-2:]}';stem=f'inbc-{spec["end"]-1}-{str(spec["end"])[-2:]}'
  packed=gzip.compress(compact(rows),mtime=0);outputs[stem+'.json.gzip']=packed;outputs['evidence/'+stem+'.json.gzip']=gzip.compress(compact(ev),mtime=0)
  notes=['Source heading spells remuneration as renumeration. The source-labelled remuneration is imported separately from expenses; component breakdown is not supplied and no base-salary inference is made.','Employee schedule only; board members, supplier payments and below-threshold aggregates are excluded. Fiscal year comes from the cover and statement header; the upload path is not the reporting period.','Source disclosure wording is employees with renumeration and expenses exceeding $75,000. Every accepted remuneration amount independently exceeds $75,000.','Names remain surname and initials exactly as disclosed; no identities or positions are inferred. The 2022/23 source says Deering, D; later schedules say Deering, A. These source spellings are preserved.','Two native-text readers independently agree on every employee field and named subtotal. All named rows were visually reviewed against rendered physical schedule pages.','A separately hash-pinned complete-cohort comparison proves all nine compiled InBC observations labelled 2023/24 are these 2022/23 employee records; the manifest replacement decision corrects that period explicitly. No board or other compiled cohort is removed.']
  warning=None
  if spec['payResidual'] or spec['expenseResidual']:
   warning=f'Published employee cells sum to ${ev["rowSums"][0]:,} remuneration and ${ev["rowSums"][1]:,} disclosed expenses; the printed named subtotals are ${spec["controlPay"]:,} and ${spec["controlExpenses"]:,}. Residuals (rows minus printed): remuneration +${spec["payResidual"]}, expenses +${spec["expenseResidual"]}. Source values are preserved; the cause is unresolved.'
   notes.append(warning)
  if spec['end']==2025:notes.append('Chiew, B. has a blank expense cell, retained as missing (null). The disclosed expense sum includes only the 16 numeric expense cells; the blank is not converted to zero.')
  sources.append({'id':'sector-crowns-'+stem,'employerSlug':'inbc','employerName':'InBC Investment Corp.','sector':'Crown corporations','year':year,'periodType':'fiscal','periodStart':f'{spec["end"]-1}-04-01','periodEnd':f'{spec["end"]}-03-31','title':f'InBC Statement of Financial Information {year}: named employee remuneration and expenses','sourceUrl':spec['url'],'sourceIndexUrl':INDEX,'sha256':spec['sha256'],'pdfBytes':len(raw),'file':stem+'.json.gzip','dataSha256':sha(packed),'category':'employee-remuneration','scope':'named-employees-over-threshold','threshold':75000,'thresholdComparison':'>','currency':'CAD','amountUnit':'dollars','status':'verified','verifiedOn':'2026-10-31','rowCount':len(rows),'totalRemuneration':ev['rowSums'][0],'totalExpenses':ev['rowSums'][1],'pages':[spec['page']],'nameDisclosure':'surname-and-initials','positionDisclosure':'not-published','publicWarning':warning,'notes':notes,'validation':{'originalFingerprintVerified':True,'independentReaders':['PyMuPDF positioned words','Poppler layout text'],'everyRowFieldAgreement':True,'physicalPagesVisuallyReviewed':[spec['page']],'rowsIndependentlyChecked':len(rows),'printedControls':[{'field':field,'printedControl':control,'rowSum':total,'residual':total-control,'basis':'Printed named employee subtotal; numeric cells only, missing values retained'} for field,control,total in zip(['pay','expenses'],ev['namedSubtotals'],ev['rowSums'])],'fieldCorrections':{},'evidenceFile':'evidence/'+stem+'.json.gzip'}})
 # Pin the complete compiled cohort and the exact accepted data bytes. This
 # comparison establishes the source year rather than relying on a same-label
 # authority replacement, which would obscure the compiler's period error.
 baseline_path=ROOT/'research/salaries/compiled-baseline.json.gzip'
 baseline_bytes=baseline_path.read_bytes();baseline=json.loads(gzip.decompress(baseline_bytes))
 compiled=next(e for e in baseline['employers'] if e['slug']=='inbc')
 selected=[r[:4] for r in compiled['rows'] if baseline['years'][r[4]]=='2023/24']
 accepted={source['year']:[row[1:5] for row in json.loads(gzip.decompress(outputs[source['file']]))] for source in sources}
 match_counts={year:sum((Counter(map(tuple,selected)) & Counter(map(tuple,rows))).values()) for year,rows in accepted.items()}
 if len(selected)!=9 or Counter(map(tuple,selected))!=Counter(map(tuple,accepted['2022/23'])) or match_counts['2023/24']!=0:
  raise ValueError('Compiled InBC cohort differs from reviewed complete source-period comparison')
 selected_hash=sha(json.dumps(selected,ensure_ascii=False,separators=(',',':')).encode())
 source=sources[0]
 rule={'employerSlug':'inbc','compiledYear':'2023/24','replacementYear':'2022/23','sourceIds':[source['id']],
       'sourceDataSha256':{source['id']:source['dataSha256']},'retainPositions':[], 'expectedRows':9,'expectedRetainedRows':0,
       'selectedRowsSha256':selected_hash,
       'reason':'Every one of the complete nine-row compiled InBC employee cohort labelled 2023/24 matches the 2022/23 official employee schedule exactly in disclosed name, position (not supplied), remuneration and expenses, with multiplicity. The official cover and statement establish April 1, 2022–March 31, 2023. None of those exact four-field observations matches the independently verified fifteen-row 2023/24 employee schedule. Replace the proved duplicate cohort under its actual 2022/23 fiscal period; there are no separate compiled board observations in this partition.',
       'evidence':'sector-crowns/inbc-overlap.json'}
 overlap={'status':'proved-complete-cohort-period-match','compiledBaselineFile':'research/salaries/compiled-baseline.json.gzip',
          'compiledBaselineSha256':sha(baseline_bytes),'compiledEmployerSlug':'inbc','compiledYear':'2023/24',
          'selectedRows':selected,'selectedRowsSha256':selected_hash,'selectedRowsHashEncoding':'SHA-256 of JSON.stringify-style compact JSON of exact first four baseline row fields in original order; no trailing newline',
          'comparisonMethod':'Exact multiset comparison of disclosed name, position, remuneration and expenses; no punctuation, amount or identity normalization.',
          'officialMatchesByPeriod':match_counts,'verifiedSourceId':source['id'],'verifiedSourcePdfSha256':source['sha256'],
          'verifiedSourceDataSha256':source['dataSha256'],'verifiedPeriodStart':source['periodStart'],'verifiedPeriodEnd':source['periodEnd'],
          'verifiedSourceRows':accepted['2022/23'],'later2023_24SourceRows':accepted['2023/24'],
          'employeeRowsReplaced':9,'boardOrOtherRowsRetained':0,'rule':rule}
 outputs['inbc-overlap.json']=(json.dumps(overlap,indent=2,ensure_ascii=False)+'\n').encode()
 outputs['sources.json']=(json.dumps({'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources,'compiledReplacements':[rule]},indent=2,ensure_ascii=False)+'\n').encode()
 for name,data in outputs.items():
  dest=a.output_dir/name
  if a.verify:
   if not dest.exists() or dest.read_bytes()!=data:raise ValueError(f'Reproduction mismatch: {dest}')
  else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 print(json.dumps({'verified':True,'sources':len(sources),'rows':sum(s['rowCount'] for s in sources),'mode':'verify' if a.verify else 'write','output':str(a.output_dir)}))
if __name__=='__main__':main()
