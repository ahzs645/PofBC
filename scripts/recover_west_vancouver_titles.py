#!/usr/bin/env python3
"""Rebuild a source-proven correction overlay without editing frozen collection inputs."""
import argparse,copy,gzip,hashlib,json,re,subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/salaries/municipal-lower-mainland'
OUT=ROOT/'research/salaries/west-vancouver-title-recovery'
def sha(b):return hashlib.sha256(b).hexdigest()
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()
def gz(path,x):
 b=gzip.compress(compact(x),mtime=0);path.write_bytes(b);return sha(b)
def key(s):return re.sub(r'\s+','',s)
def rebuild():
 catalog=json.loads((BASE/'sources.json').read_text()); corrections=[]; reports=[]
 for source in catalog['sources']:
  if source['employerSlug']!='district-of-west-vancouver' or source['year']=='2025':continue
  year=source['year'];pdf=OUT/'originals'/f'{year}.pdf'
  assert sha(pdf.read_bytes())==source['sha256']
  text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-']).decode().split('\f')
  rows=json.loads(gzip.decompress((BASE/source['file']).read_bytes()))
  evidence=json.loads(gzip.decompress((BASE/source['provenanceFile']).read_bytes()))
  before=copy.deepcopy(rows)
  page_lines={p:Counter(key(l) for l in text[p-1].splitlines()) for p in source['pages']}
  for i,(r,e) in enumerate(zip(rows,evidence['rows'],strict=True)):
   # Always recover from the original source prefix, not a guessed job vocabulary.
   parts=re.split(r'\s{2,}',e['sourcePrefix'].strip());assert len(parts)==2,(year,i,parts)
   name,title=parts; original=key(e['sourcePrefix']+' '+ ' '.join(e['raw']))
   assert page_lines[e['page']][original]>0,(year,i,original)
   page_lines[e['page']][original]-=1
   assert r[1] in (e['sourcePrefix'],name) and r[2] in (None,title)
   r[1],r[2]=name,title;e['name'],e['position']=name,title
   corrections.append({'sourceId':source['id'],'year':year,'employerSlug':source['employerSlug'],'rowIndex':i,'page':r[5],'sourcePrefix':e['sourcePrefix'],'name':name,'position':title,'remuneration':r[3],'expenses':r[4]})
  assert all(a[0]==b[0] and a[3:]==b[3:] for a,b in zip(before,rows))
  source['dataSha256']=gz(OUT/source['file'],rows)
  source['normalizedSha256']=sha(compact(rows))
  source['provenanceSha256']=gz(OUT/source['provenanceFile'],evidence)
  source['validation']['titleRecovery']={'date':'2026-11-06','count':len(rows),'method':'Split original sourcePrefix at printed column whitespace; all original row fields including amount cells match original PDF physical-page text with multiplicity.'}
  source['notes']=[n for n in source['notes'] if not n.startswith('2026-11-06 title recovery:')]+['2026-11-06 title recovery: corrected titles formerly concatenated into names; every observation, amount, expense and physical page is unchanged.']
  (OUT/f'{year}-source.json').write_text(json.dumps(source,indent=2)+'\n')
  reports.append({'year':year,'count':len(rows),'sourceSha256':source['sha256'],'totalRemuneration':sum(r[3] for r in rows),'totalExpenses':sum(r[4] or 0 for r in rows),'amountsPagesMultiplicityUnchanged':True})
 assert len(corrections)==1752
 (OUT/'corrections.json').write_text(json.dumps(corrections,ensure_ascii=False,indent=2)+'\n')
 (OUT/'validation.json').write_text(json.dumps({'correctedRows':len(corrections),'reports':reports,'excludedYear2025':'No job-title column published; remains unchanged.'},indent=2)+'\n')
 return reports
if __name__=='__main__':print(json.dumps(rebuild(),indent=2))
