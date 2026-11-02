#!/usr/bin/env python3
"""Source-first peer extraction. Does not import the producer or read candidates."""
from pathlib import Path
import collections,gzip,hashlib,json,re,subprocess,xml.etree.ElementTree as ET
import fitz
BASE=Path(__file__).resolve().parent
ROOT=Path('/workspace/PofBC')
INVENTORY=ROOT/'research/salaries/gap-fill-2026-11-02/phsa_history/source-inventory.json'
KEYS=['phsa-2006-07','phsa-2007-08','phsa-2008-09']
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,data):
 p=BASE/name;b=(json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode();p.write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gzip') else b);return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
def numeric(s):return bool(re.fullmatch(r'\d{1,3}(?:,\d{3})+|\d+',s))
def canon(s):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s).strip())
def parse(pages,reader):
 rows=[];controls=[];flags=[];census=[]
 for pn,words in enumerate(pages,1):
  heads=[w for w in words if w['text'] in ['Remuneration','Expenses'] and w['x0']>300 and w['y0']<250]
  if pn<3:continue
  assert len(heads)==2,(reader,pn,heads)
  ph=next(w for w in heads if w['text']=='Remuneration');eh=next(w for w in heads if w['text']=='Expenses')
  hy=max(ph['y1'],eh['y1']);split=(ph['x1']+eh['x0'])/2
  anchors=[w for w in words if numeric(w['text']) and 300<w['x0']<split and w['y0']>hy]
  anchors.sort(key=lambda w:(w['y0'],w['x0']))
  for a in anchors:
   ay=(a['y0']+a['y1'])/2
   # Salary body is above the literal statutory/footer and printed page number.
   line=[w for w in words if abs((w['y0']+w['y1'])/2-ay)<3.1]
   names=sorted([w for w in line if w['x0']<300],key=lambda w:w['x0'])
   expense=sorted([w for w in line if w['x0']>=split],key=lambda w:w['x0'])
   rec={'pdfPage':pn,'anchor':a,'nameWords':names,'expenseWords':expense,'sourceRemuneration':a['text']}
   if len(a['text'].replace(',',''))<5:
    rec['classification']='printed footer page number';census.append(rec);continue
   if not names:
    rec['classification']='unnamed printed monetary total';controls.append(rec);census.append(rec);continue
   name=' '.join(w['text'] for w in names)
   eraw=' '.join(w['text'] for w in expense)
   pay=int(a['text'].replace(',',''));e=int(eraw.replace(',','')) if numeric(eraw) else None
   row={'sequence':len(rows)+1,'pdfPage':pn,'name':name,'position':None,'remuneration':pay,'expenses':e,'sourceRemuneration':a['text'],'sourceExpenses':eraw,'box':[min(w['x0'] for w in line),min(w['y0'] for w in line),max(w['x1'] for w in line),max(w['y1'] for w in line)],'nameWordBoxes':names}
   if ',' not in name:flags.append({'sequence':row['sequence'],'reason':'name lacks comma'})
   if eraw!='-' and not numeric(eraw):flags.append({'sequence':row['sequence'],'reason':'non-numeric/non-dash expense','sourceExpenses':eraw})
   if pay<75000:flags.append({'sequence':row['sequence'],'reason':'below printed threshold'})
   if any(w['x1']>300 for w in names):flags.append({'sequence':row['sequence'],'reason':'name reaches next column'})
   rows.append(row);rec['classification']='named employee';rec['sequence']=row['sequence'];census.append(rec)
  # A separate whole-page census of every comma-formatted monetary token, not limited to row window.
  for w in words:
   if re.fullmatch(r'\d{1,3}(?:,\d{3})+',w['text']):
    hits=[r for r in rows if r['pdfPage']==pn and abs((r['box'][1]+r['box'][3])/2-(w['y0']+w['y1'])/2)<3.5]
    totalhits=[c for c in controls if c['pdfPage']==pn and abs((c['anchor']['y0']+c['anchor']['y1'])/2-(w['y0']+w['y1'])/2)<3.5]
    if not hits and not totalhits:flags.append({'pdfPage':pn,'reason':'whole-page unclassified comma-money token','word':w})
 return {'reader':reader,'rows':rows,'controls':controls,'flags':flags,'payAnchorCensus':census}
def main():
 inv=json.loads(INVENTORY.read_text());sources={s['key']:s for s in inv['sources']};out=[]
 for key in KEYS:
  source=sources[key];pdf=Path(source['cachePath']);assert sha(pdf.read_bytes())==source['sourceSha256'];doc=fitz.open(pdf)
  mupages=[[{'x0':w[0],'y0':w[1],'x1':w[2],'y1':w[3],'text':w[4]} for w in page.get_text('words')] for page in doc]
  xml=subprocess.check_output(['pdftotext','-bbox-layout','-enc','UTF-8',str(pdf),'-'])
  xp=ET.fromstring(xml);popages=[]
  for page in xp.findall('.//{*}page'):
   popages.append([{'x0':float(w.attrib['xMin']),'y0':float(w.attrib['yMin']),'x1':float(w.attrib['xMax']),'y1':float(w.attrib['yMax']),'text':w.text or ''} for w in page.findall('.//{*}word')])
  assert len(mupages)==len(popages)==len(doc)
  rawmu=write(key+'-mupdf-words.json.gzip',mupages);rawpo=write(key+'-poppler-words.json.gzip',popages)
  m=parse(mupages,'PyMuPDF positioned words');p=parse(popages,'Poppler bbox-layout positioned words');mp=write(key+'-mupdf-independent-rows.json.gzip',m);pp=write(key+'-poppler-independent-rows.json.gzip',p)
  diffs=[]
  if len(m['rows'])!=len(p['rows']):diffs.append({'reason':'row-count mismatch','mu':len(m['rows']),'poppler':len(p['rows'])})
  for a,b in zip(m['rows'],p['rows']):
   for f in ['pdfPage','name','remuneration','expenses','sourceExpenses']:
    if (canon(a[f]) if isinstance(a[f],str) else a[f])!=(canon(b[f]) if isinstance(b[f],str) else b[f]):diffs.append({'sequence':a['sequence'],'field':f,'mupdf':a[f],'poppler':b[f]})
  out.append({'sourceKey':key,'sourceSha256':source['sourceSha256'],'sourcePages':len(doc),'rowCounts':{'mupdf':len(m['rows']),'poppler':len(p['rows'])},'sumRemuneration':sum(r['remuneration'] for r in m['rows']),'sumKnownExpenses':sum(r['expenses'] or 0 for r in m['rows']),'expenseDashes':sum(r['sourceExpenses']=='-' for r in m['rows']),'controls':[{k:v for k,v in c.items() if k in ['pdfPage','sourceRemuneration','expenseWords']} for c in m['controls']],'readerFlags':{'mupdf':m['flags'],'poppler':p['flags']},'readerDifferences':diffs,'rawPins':[rawmu,rawpo],'parsedPins':[mp,pp]})
 print(json.dumps(out,indent=2,ensure_ascii=False))
 write('native-independent-extraction-summary.json',{'phase':'source-only before producer candidates','sources':out,'noOutreach':True})
if __name__=='__main__':main()
