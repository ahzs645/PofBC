#!/usr/bin/env python3
"""Independent PDFMiner page-grid review of ACRD employee source cohorts."""
import collections,gzip,hashlib,json,re
from pathlib import Path
import pdfplumber
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/continuation-2026-11-01/reviews';BASE=ROOT/'research/salaries/continuation-government-police'
def sha(b):return hashlib.sha256(b).hexdigest()
def amount(s):return int(s.replace('$','').replace(',',''))
RECEIPTS=[];E=[]
for c in json.loads((BASE/'config.json').read_text())['sources']:
 if c['parser']!='acrd-employees':continue
 file=Path('/tmp/continuation-government-police')/c['cacheFile'];assert sha(file.read_bytes())==c['sha256'];rows=[];pages=[]
 with pdfplumber.open(file) as pdf:
  for pn in c['pages']:
   t=pdf.pages[pn-1].extract_text(layout=True,x_density=5,y_density=6);current=None;started=(pn!=c['pages'][0]);cuts=[21,45,round(c['payColumnLeft']/5),94,10000]
   def finish(row):
    if row is None:return
    if len(row[2])!=1 or len(row[3])!=1:raise ValueError((c['id'],pn,'cells',row))
    rows.append([c['employerSlug'],' '.join(' '.join(row[0]).split()),' '.join(' '.join(row[1]).split()),amount(row[2][0]),amount(row[3][0]),pn])
   for line in t.splitlines():
    if all(word in line for word in ['Name','Position','Remuneration','Expenses']):started=True;continue
    if not started:continue
    cells=[line[l:r].strip() for l,r in zip(cuts,cuts[1:])]
    if cells[0].startswith('Consolidated'):finish(current);current=None;break
    if ',' in cells[0] and not re.search('[0-9]',cells[0]):finish(current);current=[[],[],[],[]]
    if current:
     for i,cell in enumerate(cells):
      if cell:current[i].append(cell)
   finish(current);pages.append({'pdfPage':pn,'pdfminerLayout':t})
 src=next(s for s in json.loads((BASE/'sources.json').read_text())['sources'] if s['id']==c['id']);expected=json.loads(gzip.decompress((BASE/src['file']).read_bytes()));a=collections.Counter(map(tuple,rows));b=collections.Counter(map(tuple,expected));diff=list((a-b).elements());other=list((b-a).elements())
 sums=[sum(r[3] for r in rows),sum(r[4] for r in rows)];receipt={'sourceId':c['id'],'year':c['year'],'originalSha256':c['sha256'],'localPath':str(file),'pages':c['pages'],'independentEngine':'PDFMiner/pdfplumber, independent fixed-density text grid and separate row parser','rowCount':len(rows),'rowSums':sums,'everyRowFieldAndMultiplicityAgrees':not diff and not other,'independentOnly':diff,'candidateOnly':other,'controls':c['printedControls']};RECEIPTS.append(receipt);E.append({'receipt':receipt,'rows':rows,'pages':pages});print(json.dumps(receipt))
OUT.mkdir(parents=True,exist_ok=True);(OUT/'regional-acrd-controls.json').write_text(json.dumps({'reviewer':'Crown continuation worker','date':'2026-11-01','sources':RECEIPTS},indent=2)+'\n');(OUT/'regional-acrd-evidence.json.gzip').write_bytes(gzip.compress((json.dumps(E,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
