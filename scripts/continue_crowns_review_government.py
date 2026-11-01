#!/usr/bin/env python3
"""Independent PDFMiner review of early Public Accounts controls for parent."""
import collections,gzip,hashlib,json,re
from pathlib import Path
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/continuation-2026-11-01/reviews'
def sha(b):return hashlib.sha256(b).hexdigest()
def packed(x):return gzip.compress((json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0)
R=[];E=[]
for c in json.loads((ROOT/'research/salaries/continuation-government-police/config.json').read_text())['sources']:
 if c['parser']!='pa-employees' or c['fiscalEnd']>2006:continue
 f=Path('/tmp/continuation-government-police')/c['cacheFile'];assert sha(f.read_bytes())==c['sha256']
 rows=[];page_ev=[]
 with pdfplumber.open(f) as d:
  for pn in c['pages']:
   page=d.pages[pn-1];pr=[];texts=[]
   for col,left in enumerate(c['columnStarts']):
    right=c['columnStarts'][col+1]-2 if col+1<len(c['columnStarts']) else 611
    t=page.crop((left-1,110 if pn==c['pages'][0] else 65,right,750)).extract_text(x_tolerance=2,y_tolerance=2) or '';texts.append(t);pending=[]
    for line in t.splitlines():
     m=re.fullmatch(r"(.+?)\s+(-?\d[\d,]*)(?:\s+(-?\d[\d,]*))?",line)
     if m and (pending or ',' in m[1]):
      name=' '.join(pending+[m[1]]);pending=[];pay=int(m[2].replace(',',''));exp=int(m[3].replace(',','')) if m[3] else None
      if pay<75000:raise ValueError((c['id'],pn,line))
      row=[c['employerSlug'],name,None,pay,exp,pn];rows.append(row);pr.append(row)
     elif ',' in line and not re.search('[0-9$]',line):pending.append(line)
    if pending:raise ValueError(('unclosed',c['id'],pn,pending))
   page_ev.append({'pdfPage':pn,'pdfminerColumnTexts':texts,'rows':pr})
 normalized=json.loads(gzip.decompress((ROOT/'research/salaries/continuation-government-police'/f"{c['id']}.json.gzip").read_bytes())) if (ROOT/'research/salaries/continuation-government-police'/f"{c['id']}.json.gzip").exists() else None
 if normalized is None:
  s=next(s for s in json.loads((ROOT/'research/salaries/continuation-government-police/sources.json').read_text())['sources'] if s['id']==c['id']);normalized=json.loads(gzip.decompress((ROOT/'research/salaries/continuation-government-police'/s['file']).read_bytes()))
 a=collections.Counter(map(tuple,rows));b=collections.Counter(map(tuple,normalized));diff=list((a-b).elements());diff2=list((b-a).elements())
 sums=[sum(r[3] for r in rows),sum(r[4] for r in rows if r[4] is not None) if any(r[4] is not None for r in rows) else None]
 r={'sourceId':c['id'],'year':c['year'],'originalSha256':c['sha256'],'localPath':str(f),'pages':c['pages'],'independentEngine':'PDFMiner via pdfplumber 0.11.x; cropped column extraction and a separate line parser','independentRowCount':len(rows),'independentSums':sums,'everyRowMatchesCandidateWithMultiplicity':not diff and not diff2,'independentOnly':diff[:10],'candidateOnly':diff2[:10],'printedControls':c['printedControls'],'namedRowsHash':sha(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode())};R.append(r);E.append({'receipt':r,'pages':page_ev});print(json.dumps(r))
OUT.mkdir(parents=True,exist_ok=True);(OUT/'government-early-controls.json').write_text(json.dumps({'reviewer':'crowns-continuation','date':'2026-11-01','sources':R},indent=2,ensure_ascii=False)+'\n');(OUT/'government-early-controls-evidence.json.gzip').write_bytes(packed(E))
