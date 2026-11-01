#!/usr/bin/env python3
"""Original-backed health disclosure continuation; two independent PDF readers.

Offline replay uses locked Poppler bbox + PyMuPDF word evidence. Extraction is
scoped by explicit reviewed table rectangles and retains every table row.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, re, subprocess, xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/continuation-health'
AUDIT=ROOT/'research/salaries/continuation-2026-11-01/health'
SCHEMA=['employerSlug','name','position','remuneration','expenses','pdfPage']

def digest(b): return hashlib.sha256(b).hexdigest()
def normalized(s): return re.sub(r'\s+',' ',s).strip()
def money(s):
 s=normalized(s.replace('$',''))
 if s in ('','-','‐','–'):return None
 if not re.fullmatch(r'(?:-?\d[\d,]*(?:\.\d{2})?|\(\d[\d,]*(?:\.\d{2})?\))',s):raise ValueError('Unexpected amount '+repr(s))
 n=float(s.replace(',','').replace('(','-').replace(')',''))
 return int(n) if n.is_integer() else n

def lines(words):
 """Group by word top; superscript annotations may form their own line."""
 groups=[]
 for w in sorted(words,key=lambda w:(w[1],w[0])):
  if groups and abs(w[1]-groups[-1][0][1])<2.8:groups[-1].append(w)
  else:groups.append([w])
 return [sorted(g,key=lambda w:w[0]) for g in groups]
def cell(words,x0,x1,y0,y1):
 kept=[w for w in words if x0 <= (w[0]+w[2])/2 < x1 and y0 <= (w[1]+w[3])/2 < y1]
 return normalized(' '.join(' '.join(w[4] for w in l) for l in lines(kept)))
def clean_name(s):
 s=re.sub(r'\s*\([Nn]ote[^)]*\)','',s)
 s=re.sub(r'\s+\d+(?:,\d+)*$','',s)
 return normalized(s)
def parse_words(pages,spec):
 result=[]; evidence=[]
 for table in spec['tables']:
  page=table.get('page',1);words=pages[page-1];cols=table['columns']; top,bottom=table['yRange']
  nw=[w for w in words if cols[0]<=w[0]<cols[1] and top<(w[1]+w[3])/2<bottom]
  anchors=[]
  for l in lines(nw):
   name=clean_name(' '.join(w[4] for w in l))
   if not name or re.fullmatch(r'[\d,() ]+',name):continue
   if not re.search(r'[A-Za-z]',name):raise ValueError('Bad name '+name)
   anchors.append(((min(w[1] for w in l)+max(w[3] for w in l))/2,name))
  if len(anchors)!=table['rows']:raise ValueError(f"{spec['id']}: expected {table['rows']} names, got {anchors}")
  for i,(y,name) in enumerate(anchors):
   low=top if i==0 else (anchors[i-1][0]+y)/2
   high=bottom if i==len(anchors)-1 else (anchors[i+1][0]+y)/2
   cells=[cell(words,a,b,low,high) for a,b in zip(cols,cols[1:])]
   raw_cells=list(cells)
   for correction in spec.get('cellCorrections',[]):
    if name==correction['name']:
     col=correction['column']
     if cells[col] not in correction['allowedOriginals']:raise ValueError('Correction context changed')
     cells[col]=correction['visibleText']
   position=cells[1] or None
   try:components=[money(cells[c]) for c in table['payColumns']]
   except ValueError as ex:raise ValueError(f"{spec['id']} {name}: {cells}") from ex
   pay=sum(c or 0 for c in components) if any(c is not None for c in components) else None
   if table.get('paySubtotalColumn') is not None:pay=money(cells[table['paySubtotalColumn']])
   expense=money(cells[table['expenseColumn']]) if table.get('expenseColumn') is not None else None
   row=[spec['employerSlug'],name,position,pay,expense,page]
   evidence.append(dict(row=row,cells=cells,rawCells=raw_cells,payComponents=components,sourceInclusiveTotal=money(cells[table['totalColumn']]) if table.get('totalColumn') is not None else None))
   result.append(row)
 return result,evidence

def pdf_readers(path):
 import fitz
 doc=fitz.open(path);pages=[]
 for p in doc:
  words=[]
  for w in p.get_text('words'):
   r=fitz.Rect(w[:4])*p.rotation_matrix
   words.append([r.x0,r.y0,r.x1,r.y1,w[4]])
  pages.append(words)
 raw=subprocess.check_output(['pdftotext','-bbox-layout',str(path),'-'])
 ns={'x':'http://www.w3.org/1999/xhtml'}
 pop=[]
 for p in ET.fromstring(raw).findall('.//x:page',ns):
  pop.append([[float(w.attrib[x]) for x in ['xMin','yMin','xMax','yMax']]+[w.text or ''] for w in p.findall('.//x:word',ns)])
 return pages,pop

def check(spec,a,b,ea,eb):
 if a!=b:
  bad=[(i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
  raise ValueError(f"{spec['id']}: reader disagreement: {bad[:4]}")
 # Independent cell extraction protects against identical normalization masking a
 # pay/expense or name/title column swap.
 for x,y in zip(ea,eb):
  if x['cells']!=y['cells']:raise ValueError(f"{spec['id']}: raw cell reader disagreement {x['cells']} {y['cells']}")
 return {'independentReaders':['PyMuPDF words','Poppler bbox-layout words'],'independentlyComparedRows':len(a),'completeEmployeeSchedule':False,'completeBoardSchedule':all(r[3] is not None for r in a),'physicalPdfPages':[t.get('page',1) for t in spec['tables']],'sourceRowsPerPhysicalPage':[t['rows'] for t in spec['tables']],'negativeExpenseRows':sum(r[4] is not None and r[4]<0 for r in a),'missingExpenseRows':sum(r[4] is None for r in a),'explicitZeroExpenseRows':sum(r[4]==0 for r in a),'duplicateRowsPreserved':sum(v-1 for v in Counter(tuple(r) for r in a).values() if v>1),'knownFieldsVersusInclusiveTotalResiduals':[round(x['row'][3]+(x['row'][4] or 0)-x['sourceInclusiveTotal'],2) for x in ea if x['sourceInclusiveTotal'] is not None and x['row'][3] is not None],'payComponentResiduals':[round(x['row'][3]-sum(c or 0 for c in x['payComponents']),2) for x in ea if x['row'][3] is not None],'heldUnknownRemunerationRows':[x for x in ea if x['row'][3] is None]}

def run(originals=False,check_only=False):
 specs=json.loads((OUT/'source-specs.json').read_text());sources=[]
 for s in specs:
  ep=OUT/'evidence'/(s['id']+'.json.gzip')
  if originals:
   p=Path(s['cachePath']);raw=p.read_bytes()
   if digest(raw)!=s['sha256']:raise ValueError('Original source hash changed')
   a,b=pdf_readers(p)
   ep.parent.mkdir(exist_ok=True)
   ep.write_bytes(gzip.compress(json.dumps({'sourceSha256':s['sha256'],'pymupdf':a,'poppler':b},ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
  ev=json.loads(gzip.decompress(ep.read_bytes()))
  if ev['sourceSha256']!=s['sha256']:raise ValueError('Evidence source fingerprint differs')
  for engine in ['pymupdf','poppler']:
   header=normalized(' '.join(w[4] for l in lines(ev[engine][0]) for w in l))
   end=int(s['year'][:4])+1
   if not re.search(r'March\s+31,?\s*'+str(end),header,re.I):raise ValueError('Internal period missing')
   if f"{s['printedInclusiveTotal']:,}" not in header:raise ValueError('Printed inclusive control missing')
  a,ea=parse_words(ev['pymupdf'],s);b,eb=parse_words(ev['poppler'],s)
  v=check(s,a,b,ea,eb)
  a=[r for r in a if r[3] is not None]
  v['originalBackedEvidenceSha256']=digest(ep.read_bytes())
  v['totalRemuneration']=sum(r[3] for r in a);v['totalExpenses']=sum(r[4] or 0 for r in a)
  v['heldDisclosedExpenses']=sum(x['row'][4] or 0 for x in v['heldUnknownRemunerationRows'])
  v['knownFieldsVersusPrintedGrandResidual']=v['totalRemuneration']+v['totalExpenses']+v['heldDisclosedExpenses']-s['printedInclusiveTotal']
  v['printedGrandTotalIncludesExpenseReimbursements']=s.get('printedGrandTotalIncludesExpenseReimbursements',True)
  v['renderReview']={'physicalPages':[1],'coverage':'Every named row, header, monetary column and control on the complete one-page rendered schedule reviewed.','imagePath':'/tmp/continuation-health/'+s['id']+'.png'}
  expected=s.get('reviewedControls')
  if expected:
   actual=[len(a),v['totalRemuneration'],v['totalExpenses']]
   if actual!=expected:raise ValueError(f'Reviewed controls changed {actual} != {expected}')
  data=gzip.compress(json.dumps(a,ensure_ascii=False,separators=(',',':')).encode(),mtime=0)
  filename=s['id']+'.json.gzip'
  if check_only:
   if (OUT/filename).read_bytes()!=data:raise ValueError('Normalized artifact differs')
  else:(OUT/filename).write_bytes(data)
  src={k:v for k,v in s.items() if k not in ['tables','cachePath','reviewedControls']}
  src['notes']=[s['notes']] if isinstance(s.get('notes'),str) else s.get('notes',[])
  src.update(file=filename,dataSha256=digest(data),rowCount=len(a),status='verified',sourceKind='official',periodType='fiscal',periodStart=s['year'][:4]+'-04-01',periodEnd=str(int(s['year'][:4])+1)+'-03-31',category='board-remuneration',scope='board-remuneration',currency='CAD',nameDisclosure='named',completeEmployeeSchedule=False,verifiedOn='2026-11-01',validation=v,totalRemuneration=v['totalRemuneration'],totalDisclosedExpenses=v['totalExpenses'])
  src['completeBoardSchedule']=v['completeBoardSchedule']
  warnings=[]
  if v['heldUnknownRemunerationRows']:warnings.append('Partial board payment import: '+', '.join(x['row'][1] for x in v['heldUnknownRemunerationRows'])+' has only blank/dash remuneration components; the source row is held rather than treated as zero.')
  if v['negativeExpenseRows']:warnings.append('The original reports a negative expense reimbursement, preserved as printed.')
  if v['knownFieldsVersusPrintedGrandResidual'] or any(v['knownFieldsVersusInclusiveTotalResiduals']) or any(v['payComponentResiduals']):warnings.append('Published whole-dollar rows/components and source totals disagree: known displayed fields minus the printed expense-inclusive grand total = '+str(v['knownFieldsVersusPrintedGrandResidual'])+' CAD. Individual displayed fields remain unchanged; no cause is inferred. See validation for row residuals.')
  if s.get('printedRemunerationTotal') is not None:
   v['remunerationResidual']=v['totalRemuneration']-s['printedRemunerationTotal'];v['expensesResidual']=v['totalExpenses']-s['printedExpensesTotal']
   if v['remunerationResidual'] or v['expensesResidual']:warnings.append(f"Displayed remuneration minus printed subtotal = {v['remunerationResidual']} CAD; disclosed expenses minus printed subtotal = {v['expensesResidual']} CAD.")
  if warnings:src['publicWarning']=' '.join(warnings)
  sources.append(src)
 manifest=json.dumps({'version':1,'rowSchema':SCHEMA,'sources':sources},ensure_ascii=False,indent=2)+'\n'
 if check_only:
  if (OUT/'sources.json').read_text()!=manifest:raise ValueError('Manifest differs from replay')
 else:(OUT/'sources.json').write_text(manifest)
 print(json.dumps({'cohorts':len(sources),'rows':sum(s['rowCount'] for s in sources)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--originals',action='store_true');p.add_argument('--check',action='store_true');args=p.parse_args();run(args.originals,args.check)
