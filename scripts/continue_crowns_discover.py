#!/usr/bin/env python3
"""Inventory official Crown employer histories and retain fresh source receipts."""
import concurrent.futures,datetime,hashlib,json,pathlib,urllib.request
from urllib.parse import urljoin
ROOT=pathlib.Path(__file__).resolve().parents[1]
OLD=ROOT/'research/salaries/sector-search-2026-10-31/crowns'
OUT=ROOT/'research/salaries/continuation-2026-11-01/crowns'
CACHE=pathlib.Path('/tmp/continuation-crowns')
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def fetch(t):
 p=CACHE/(sha(t['url'].encode())[:16]+'.pdf')
 try:
  if not p.exists():
   with urllib.request.urlopen(urllib.request.Request(t['url'],headers={'User-Agent':'Mozilla/5.0 public salary source research'}),timeout=50) as r:b=r.read();p.write_bytes(b)
  b=p.read_bytes(); d={**t,'localPath':str(p),'sha256':sha(b),'bytes':len(b),'retrievedOn':'2026-11-01','pdf':b.startswith(b'%PDF')}
  if d['pdf']:
   import fitz
   doc=fitz.open(p);d['pages']=len(doc);d['coverText']=doc[0].get_text();d['employeePages']=[i+1 for i,page in enumerate(doc) if any(s in page.get_text().lower() for s in ['employee name','behalf of each employee','employees with remuneration over'])]
  return d
 except Exception as ex:return {**t,'error':str(ex),'retrievedOn':'2026-11-01'}
def main():
 CACHE.mkdir(exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 old=json.loads((OLD/'discovery.json').read_text());tasks=[];seen=set()
 for e in old['employers']:
  if e['employerSlug'] not in ['icbc','bclc','royal-bc-museum']:continue
  for r in e['retrievals']:
   for l in r.get('links',[]):
    if l['url'] in seen:continue
    good=(e['employerSlug']=='icbc' and 'financial' in l['url'].lower() and 'executive' not in l['url'].lower()) or (e['employerSlug']=='bclc' and 'Financial Information Act Report' in l['label']) or (e['employerSlug']=='royal-bc-museum' and ('Financial Information' in l['label']))
    if good:
     seen.add(l['url']);tasks.append({'employerSlug':e['employerSlug'],'employerName':e['employerName'],'label':l['label'],'url':l['url'],'indexUrl':r['url']})
 receipts=list(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(fetch,tasks));dump(OUT/'pdf-receipts.json',receipts)
 accepted=[]
 for name in json.loads((ROOT/'research/salaries/collections.json').read_text())['collections']:
  d=json.loads((ROOT/'research/salaries'/name/'sources.json').read_text())
  accepted.extend([{k:s.get(k) for k in ['id','employerSlug','year','category','periodType','periodStart','periodEnd','rowCount','sourceUrl']}|{'collection':name} for s in d['sources']])
 inventory=[]
 for e in old['employers']:
  inventory.append({'employerSlug':e['employerSlug'],'employerName':e['employerName'],'sector':e['sector'],'compiledBaselineRows':e['baselineRows'],'officialAcceptedCohorts':[s for s in accepted if s['employerSlug']==e['employerSlug']],'priorDiscoveryIndexes':[{'url':r['url'],'httpStatus':r.get('httpStatus'),'error':r.get('error')} for r in e['retrievals']],'continuationOriginals':[r for r in receipts if r['employerSlug']==e['employerSlug']],'coverageStatus':'official periods listed explicitly; all unlisted histories unresolved; prior discovery is not accepted coverage'})
 dump(OUT/'employer-inventory.json',{'version':1,'date':'2026-11-01','existingEmployerEntries':len(inventory),'employers':inventory})
 print(json.dumps({'originals':len(receipts),'pdfs':sum(r.get('pdf',False) for r in receipts),'failures':[r for r in receipts if not r.get('pdf')]}))
if __name__=='__main__':main()
