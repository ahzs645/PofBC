#!/usr/bin/env python3
"""Independent native readers for three newly recovered PHSA salary originals."""
import argparse,collections,gzip,hashlib,json,re,subprocess,xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path
import fitz
from gap_phsa_history_fetch import AREA,ROOT
FIELDS=['name','position','remuneration','expenses','pdfPage']
SPECS={'phsa-2006-07':{'bounds':[310,430],'printedCount':1280,'printedTotals':['151608222','4448009']},'phsa-2007-08':{'bounds':[320,470],'printedCount':1271,'printedTotals':['154793761','4014218']},'phsa-2008-09':{'bounds':[310,430],'printedCount':1544,'printedTotals':['185412331','5289671']}}
MONEY=re.compile(r'^\(?-?\d[\d,]*(?:\.\d{2})?\)?$')

def sha(b):return hashlib.sha256(b).hexdigest()
def clean(s):return ' '.join(s.split())
def amount(s):
 s=clean(s).replace('$','')
 if s in ['-','–','—','']:return None
 assert MONEY.fullmatch(s),repr(s)
 v=Decimal(s.replace(',','').replace('(','-').replace(')',''))
 return '0' if v==0 else str(v)
def row(cells,p,y,proof):
 name,pay,expense=map(clean,cells)
 if not name or ',' not in name or not MONEY.fullmatch(pay):return None
 marker='*' if name=='Cranston,Lynda*' else None
 return {'name':name[:-1] if marker else name,'sourceFootnoteMarker':marker,'position':None,'remuneration':amount(pay),'expenses':amount(expense),'pdfPage':p,'sourceY':y,'sourceCellTexts':cells,**proof}
def mupdf_rows(doc,spec):
 out=[];pages=[]
 for p in range(3,len(doc)+1):
  gs=[]
  for w in sorted(doc[p-1].get_text('words'),key=lambda w:((w[1]+w[3])/2,w[0])):
   cy=(w[1]+w[3])/2;g=next((g for g in gs[-3:] if abs(g['y']-cy)<3.2),None)
   if g is None:g={'y':cy,'words':[]};gs.append(g)
   g['words'].append(w)
  moneyanchors=[]
  for g in gs:
   cells=[[],[],[]]
   for w in sorted(g['words'],key=lambda w:w[0]):cells[sum(w[0]>=b for b in spec['bounds'])].append(w[4])
   texts=[' '.join(c) for c in cells];r=row(texts,p,g['y'],{'mupdfWords':[list(w[:5]) for w in g['words']]})
   if r:out.append(r)
   if MONEY.fullmatch(clean(texts[1])):moneyanchors.append({'sourceY':g['y'],'sourceCells':texts,'parsedNamedRow':r is not None,'sourceWords':[list(w[:5]) for w in g['words']]})
  pages.append({'physicalPage':p,'wordCount':len(doc[p-1].get_text('words')),'imageCount':len(doc[p-1].get_images()),'fontCount':len(doc[p-1].get_fonts()),'moneyAnchors':moneyanchors,'invisibleOrWhiteTraces':[{'type':t['type'],'color':t['color'],'bbox':list(t['bbox'])} for t in doc[p-1].get_texttrace() if t['type']!=0 or (t['color'] and min(t['color'])>.95)]})
 return out,pages
def poppler_rows(text,count):
 out=[];flags=[];totals=[]
 for p in range(3,count+1):
  for line in text.split('\f')[p-1].splitlines():
   parts=[clean(c) for c in re.split(r'\s{2,}',line.strip())]
   if len(parts)==3:
    r=row(parts,p,None,{'sourceLine':line})
    if r:out.append(r);continue
   if len(parts)==2 and all(MONEY.fullmatch(c) for c in parts):totals.append({'physicalPage':p,'literalTexts':parts})
   elif re.search(r'\b\d{2,3},\d{3}\b',line):flags.append({'physicalPage':p,'sourceLine':line,'parts':parts})
 return out,flags,totals
def run(key):
 inventory=json.loads((AREA/'source-inventory.json').read_text())['sources'];source=next(s for s in inventory if s['key']==key);pdf=Path(source['cachePath']);assert sha(pdf.read_bytes())==source['sourceSha256'];doc=fitz.open(pdf);text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-']).decode();one,flags,totals=poppler_rows(text,len(doc));two,pages=mupdf_rows(doc,SPECS[key]);diffs=[]
 for i in range(max(len(one),len(two))):
  a=[one[i][f] for f in FIELDS] if i<len(one) else None;b=[two[i][f] for f in FIELDS] if i<len(two) else None
  if a!=b:diffs.append({'sequence':i+1,'poppler':a,'mupdf':b})
 computed=[str(sum(Decimal(r[f] or '0') for r in two)) for f in ['remuneration','expenses']];expected=SPECS[key]['printedTotals'];d={'key':key,'source':source,'spec':SPECS[key],'fields':FIELDS,'readers':['Independent Poppler physical-layout lines','Independent MuPDF word geometry, 3.2pt center tolerance'],'popplerRows':one,'mupdfRows':two,'fieldDifferences':diffs,'popplerUnparsedMoneyLines':flags,'printedTotalLines':totals,'nativePageEvidence':pages,'literalComputedTotals':computed,'literalPrintedTotals':expected,'residuals':[str(Decimal(a)-Decimal(b)) for a,b in zip(computed,expected)],'noPublishedPositionColumn':True,'acceptedRows':0,'noOutreach':True,'revision':'v2; prior v1 retained; native source 2008 Christensen name/pay centers differ 2.88pt; increased grouping tolerance from 2.5 to 3.2pt. Explicit printed (0) canonicalized to 0. Cranston superscript marker separated only after actual rendered-page reading.'};dest=AREA/(key+'-native-candidate-v2.json.gzip');assert not dest.exists();dest.write_bytes(gzip.compress((json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0));print(json.dumps({'key':key,'rows':[len(one),len(two)],'differences':len(diffs),'printedCount':SPECS[key]['printedCount'],'computed':computed,'residuals':d['residuals'],'firstDifferences':diffs[:6],'unparsedMoneyLines':len(flags)},ensure_ascii=False),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--key',action='append',choices=list(SPECS));a=p.parse_args()
 for k in a.key or SPECS:run(k)
