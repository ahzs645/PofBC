#!/usr/bin/env python3
"""Reproduce reviewed Capital/Cowichan original salary-table cohorts.

Pinned sources and reviewed table geometry are in reviewed-layouts.json. PyMuPDF
and Poppler independently read every field. No registry or app output is edited.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,re,subprocess,tempfile,urllib.request,xml.etree.ElementTree as E
from decimal import Decimal
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'research/salaries/municipal-wave-capital';CACHE=Path('/tmp/wave-capital')
def sha(x):return hashlib.sha256(x).hexdigest()
def compact(x):return (json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def money(s):
 s=s.replace('$','').replace(' ','').strip()
 if s in ['','-','–','—']:return None
 if not re.fullmatch(r'-?\d[\d,]*(?:\.\d{1,2})?|\(\d[\d,]*(?:\.\d{1,2})?\)',s):raise ValueError(f'Unexpected money {s!r}')
 if s.startswith('('):s='-'+s[1:-1]
 v=Decimal(s.replace(',',''));return int(v) if v==int(v) else float(v)
def cents(v):return int(Decimal(str(v or 0))*100)
def val(c):return int(c//100) if c%100==0 else float(Decimal(c)/100)
def pdf_words(page):return [{'x':w[0],'y':w[1],'right':w[2],'bottom':w[3],'t':w[4]} for w in page.get_text('words')]
def poppler_words(path,pages):
 raw=subprocess.check_output(['pdftotext','-bbox-layout','-f',str(min(pages)),'-l',str(max(pages)),str(path),'-'])
 root=E.fromstring(raw);ps=root.findall('.//{*}page');out={}
 for n,p in enumerate(ps,start=min(pages)):
  out[n]=[{'x':float(w.attrib['xMin']),'y':float(w.attrib['yMin']),'right':float(w.attrib['xMax']),'bottom':float(w.attrib['yMax']),'t':w.text or ''} for w in p.findall('.//{*}word')]
 return out

def read_table(words,layout):
 cols=layout['columns'];roles=layout['roles'];anchor=roles.index('pay');lo,hi=cols[anchor:anchor+2];ylo,yhi=layout['yRange']
 anchors=sorted([w for w in words if lo<=w['x']<hi and ylo<=w['y']<=yhi and re.fullmatch(r'\$?-?\d[\d,]*(?:\.\d{1,2})?',w['t'])],key=lambda w:w['y'])
 if len(anchors)!=layout['rows']:raise ValueError(f"Physical page{layout['page']}: expected{layout['rows']} pay anchors, found{len(anchors)}")
 rows=[];ev=[]
 for n,a in enumerate(anchors):
  lower=ylo-3 if n==0 else (anchors[n-1]['y']+a['y'])/2
  upper=yhi+1 if n==len(anchors)-1 else (a['y']+anchors[n+1]['y'])/2
  ww=[w for w in words if lower<=w['y']<upper and cols[0]<=w['x']<cols[-1]]
  cells=[]
  for i,role in enumerate(roles):
   cw=sorted([w for w in ww if cols[i]<=w['x']<cols[i+1]],key=lambda w:(round(w['y']/2)*2,w['x']))
   t=' '.join(w['t'] for w in cw).strip()
   if role not in ['pay','expenses','gross','benefits','total'] and '$' in t:raise ValueError('Currency marker assigned to a textual field; review column boundary')
   cells.append(money(t) if role in ['pay','expenses','gross','benefits','total'] else t or None)
  record=dict(zip(roles,cells))
  if not record.get('name') or record['pay'] is None:raise ValueError('Missing name or pay')
  if re.search(r'\btotal\b|employees|remuneration',record['name'],re.I):raise ValueError('Aggregate/header treated as name')
  rows.append(record);ev.append({'values':record,'words':ww,'anchorY':a['y']})
 if layout.get('renderedEdgeChecks'):
  e=layout['renderedEdgeChecks']
  for row,expected in [(rows[0],e['first']),(rows[-1],e['last'])]:
   if any(row.get(k)!=value for k,value in expected.items()):raise ValueError(f'Rendered source edge changed: {row} != {expected}')
 return rows,ev

def read_control(words,c):
 ww=[w for w in words if abs(w['y']-c['y'])<4]
 values=[]
 for lo,hi in c['columns']:
  s=' '.join(w['t'] for w in sorted(ww,key=lambda w:w['x']) if lo<=w['x']<hi);values.append(money(s))
 if values!=c['values']:raise ValueError(f"Printed control differs at page{c['page']}:{c['y']}: {values} != {c['values']}")
 return values

def extract(spec,path):
 raw=path.read_bytes()
 if sha(raw)!=spec['sha256']:raise ValueError('Original hash changed; full renewed source review required')
 doc=fitz.open(path)
 if spec.get('publicationEvidence'):
  e=spec['publicationEvidence']
  if e['statement'] not in ' '.join(doc[e['pdfPage']-1].get_text().split()):raise ValueError('Explicit source approval evidence changed')
 period_page=spec['periodEvidence'].get('page')
 if period_page and spec['year'] not in doc[period_page-1].get_text():raise ValueError('Schedule does not show the reviewed reporting year')
 if not re.search(r'December\s+31[,.]?\s*,?\s*'+re.escape(spec['year']), ' '.join(p.get_text() for p in doc), re.I):raise ValueError('Original does not establish the reviewed December31 year end')
 pages=sorted(set(l['page'] for c in spec['cohorts'] for l in c['layouts'])|set(c['page'] for c in spec['controls']))
 pp=poppler_words(path,pages);pw={p:pdf_words(doc[p-1]) for p in pages};controls={}
 for c in spec['controls']:
  first=read_control(pw[c['page']],c);second=read_control(pp[c['page']],c)
  if first!=second:raise ValueError('Independent controls disagree')
  controls[c['id']]=first
 out=[]
 for c in spec['cohorts']:
  allrows=[];ev=[]
  for l in c['layouts']:
   rows,first=read_table(pw[l['page']],l);other,second=read_table(pp[l['page']],l)
   if rows!=other:raise ValueError(f"Independent row readers disagree: {spec['employerSlug']} {spec['year']} p{l['page']}")
   for row,a,b in zip(rows,first,second):
    if 'nameParts' in c:
     row['name']=', '.join(row.pop(k) for k in c['nameParts'])
    allrows.append([spec['employerSlug'],row['name'],row.get('position'),row['pay'],row.get('expenses'),l['page']]);ev.append({'page':l['page'],'fields':row,'pymupdf':a,'poppler':b})
  nums=[sum(cents(r[3]) for r in allrows),sum(cents(r[4]) for r in allrows if r[4] is not None)]
  calc=c['controlFormula'];expected=list(controls[calc['total']][:2])
  if calc.get('subtract'):
   expected=[None if a is None or b is None else val(cents(a)-cents(b)) for a,b in zip(expected,controls[calc['subtract']][:2])]
  residual=[None if b is None else val(a-cents(b)) for a,b in zip(nums,expected)]
  if c.get('residuals') is not None and residual!=c['residuals']:raise ValueError(f'Unreviewed source residual {residual}')
  out.append({'config':c,'rows':allrows,'evidence':ev,'sum':[val(x) for x in nums],'printedNamedControl':expected,'residuals':residual,'controls':controls})
 return out

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--verify',action='store_true');ap.add_argument('--preview',action='store_true');ap.add_argument('--cache-dir',type=Path,default=CACHE);ap.add_argument('--output-dir',type=Path,default=BASE);a=ap.parse_args();cfg=json.loads((BASE/'reviewed-layouts.json').read_text());outputs={};sources=[]
 for spec in cfg['reports']:
  p=a.cache_dir/spec['cacheFile']
  if not p.exists():
   a.cache_dir.mkdir(parents=True,exist_ok=True)
   with urllib.request.urlopen(urllib.request.Request(spec['sourceUrl'],headers={'User-Agent':'Mozilla/5.0 public source verification'}),timeout=60) as f:p.write_bytes(f.read())
  results=extract(spec,p)
  for result in results:
   c=result['config'];rows=result['rows'];print(spec['employerSlug'],spec['year'],c['category'],len(rows),rows[0][1],rows[-1][1],result['sum'],result['printedNamedControl'],result['residuals'])
   if a.preview:continue
   if c.get('status','').startswith('held'):
    stem=spec['employerSlug']+'-'+spec['year']+'-'+c['category']
    held={'status':c['status'],'reason':c['holdReason'],'originalSha256':spec['sha256'],'sourceUrl':spec['sourceUrl'],'individualRowsAccepted':0,'candidateRows':result['evidence'],'sourceControls':result['controls'],'rowSums':result['sum'],'residuals':result['residuals']}
    outputs['evidence/'+stem+'-held.json.gzip']=gzip.compress(compact(held),mtime=0)
    continue
   if c.get('residuals') is None:raise ValueError('Residual review not pinned')
   stem=spec['employerSlug']+'-'+spec['year']+'-'+c['category'];data=gzip.compress(compact(rows),mtime=0);outputs[stem+'.json.gzip']=data
   evidence={'originalSha256':spec['sha256'],'periodEvidence':spec['periodEvidence'],'rows':result['evidence'],'sourceControls':result['controls'],'printedNamedControl':result['printedNamedControl'],'rowSums':result['sum'],'residuals':result['residuals'],'layout':c,'scopeNotes':spec['notes'],'publicationEvidence':spec.get('publicationEvidence')};outputs['evidence/'+stem+'.json.gzip']=gzip.compress(compact(evidence),mtime=0)
   warning=None
   if any(result['residuals']):warning=f"Published row amounts minus printed named-cohort controls differ by remuneration ${result['residuals'][0]:,.2f} and expenses ${result['residuals'][1]:,.2f}. Original values are preserved; the cause is unresolved. Disclosed numeric expenses alone are summed; missing expense cells remain missing."
   if spec.get('additionalPublicWarning'):warning=' '.join(x for x in [warning,spec['additionalPublicWarning']] if x)
   sources.append({'id':'municipal-wave-capital-'+stem,'employerSlug':spec['employerSlug'],'employerName':spec['employerName'],'sector':'Municipalities','year':spec['year'],'periodType':'calendar','periodStart':spec['year']+'-01-01','periodEnd':spec['year']+'-12-31','title':spec['employerName']+' '+spec['year']+' SOFI: '+c['category'],'sourceUrl':spec['sourceUrl'],'sourceIndexUrl':spec['sourceIndexUrl'],'sha256':spec['sha256'],'file':stem+'.json.gzip','dataSha256':sha(data),'category':c['category'],'scope':'elected-officials' if c['category']=='elected-officials' else 'named-employees-over-threshold','threshold':None if c['category']=='elected-officials' else 75000,'thresholdComparison':None if c['category']=='elected-officials' else c.get('thresholdComparison','>'),'currency':'CAD','amountUnit':'dollars','status':'verified','verifiedOn':'2026-10-31','rowCount':len(rows),'totalRemuneration':result['sum'][0],'totalExpenses':result['sum'][1],'pages':sorted(set(r[5] for r in rows)),'publicWarning':warning,'nameDisclosure':'as-published','positionDisclosure':'published' if any('position' in l['roles'] for l in c['layouts']) else 'not-published','notes':spec['notes']+c.get('notes',[])+([warning] if warning else []),'validation':{'originalFingerprintVerified':True,'publicationEvidence':spec.get('publicationEvidence'),'independentReaders':['PyMuPDF positioned words','Poppler bbox-layout positioned words'],'everyRowFieldAgreement':True,'physicalPagesVisuallyReviewed':c['visuallyReviewedPages'],'rowsIndependentlyChecked':len(rows),'sourceControls':result['controls'],'printedControls':[{'field':field,'printedControl':v,'rowSum':total,'residual':None if v is None else val(cents(total)-cents(v)),'basis':c['controlFormula']} for field,v,total in zip(['pay','expenses'],result['printedNamedControl'],result['sum'])],'evidenceFile':'evidence/'+stem+'.json.gzip'}})
 if a.preview:return
 outputs['sources.json']=(json.dumps({'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources},indent=2,ensure_ascii=False)+'\n').encode()
 for name,data in outputs.items():
  p=a.output_dir/name
  if a.verify:
   if not p.exists() or p.read_bytes()!=data:raise ValueError(f'Reproduction differs: {p}')
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 print(json.dumps({'sources':len(sources),'rows':sum(s['rowCount'] for s in sources),'verify':a.verify}))
if __name__=='__main__':main()
