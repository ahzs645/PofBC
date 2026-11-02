#!/usr/bin/env python3
"""Recover remuneration originals nested inside public historical council agendas."""
import concurrent.futures,gzip,hashlib,json,re,urllib.request
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/municipal';CACHE=Path('/workspace/gap-municipal-cache')
def fetch(id):
 url=f'https://rossland.civicweb.net/document/{id}/';r={'sourceUrl':url,'sourceIndexUrl':'https://rossland.civicweb.net/filepro/documents/7042/','leadId':'lead-028','employerSlug':'city-of-rossland','agendaId':id,'recoveryMethod':'Official CivicWeb exact phrase Employee Remuneration plus internally relevant reporting-year search, then original agenda download.'}
 with urllib.request.urlopen(url,timeout=90) as response:b=response.read();r.update(httpStatus=response.status,retrievedUrl=response.url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 assert b.startswith(b'%PDF');p=CACHE/f'rossland-agenda-{id}.pdf';p.write_bytes(b);d=fitz.open(p);r.update(cachedOriginal=str(p),originalPages=len(d));pages=[]
 for page in d:
  text=page.get_text();flat=re.sub(r'\s+',' ',text)
  if re.search(r'ELECTED OFFICIALS 201[14]|For the year 201[14], the following|201[14].{0,50}Employee Remuneration|Schedule of Employee Remuneration|Statement of Financial Information Approval',flat,re.I):pages.append({'physicalPage':page.number+1,'text':text})
 out=AREA/f'rossland-agenda-{id}-native-pages.json';out.write_text(json.dumps({'source':r,'pages':pages},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'agenda':id,'pages':len(d),'candidatePages':[x['physicalPage'] for x in pages]}),flush=True);return r
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rs=list(pool.map(fetch,[16961,17018,4297]))
 (AREA/'agenda-recovery-receipts.json').write_text(json.dumps({'noOutreach':True,'sources':rs},ensure_ascii=False,indent=2)+'\n')
