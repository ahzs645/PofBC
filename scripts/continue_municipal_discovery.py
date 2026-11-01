#!/usr/bin/env python3
"""Bounded official archive recheck of every municipal roster jurisdiction.
Retrieval is read-only; candidate link labels are never treated as verified periods.
"""
import concurrent.futures as cf, datetime, gzip, hashlib, json, re
from pathlib import Path
from urllib.parse import urljoin, urlparse
import httpx
from html.parser import HTMLParser
class Links(HTMLParser):
 def __init__(self):super().__init__();self.items=[];self.href=None;self.label=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.href=dict(attrs).get('href');self.label=[]
 def handle_data(self,data):
  if self.href:self.label.append(data)
 def handle_endtag(self,tag):
  if tag=='a' and self.href:self.items.append((self.href,' '.join(self.label)));self.href=None
import fitz
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/continuation-2026-11-01/municipal'
CACHE=Path('/tmp/continuation-municipal')
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def retrieve(task):
 slug,url,kind=task
 rcp={'employerSlug':slug,'url':url,'kind':kind,'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  r=httpx.get(url,timeout=45,follow_redirects=True,headers={'User-Agent':'Mozilla/5.0 public financial disclosure research'})
  b=r.content;rcp.update(httpStatus=r.status_code,finalUrl=str(r.url),sha256=sha(b),bytes=len(b),contentType=r.headers.get('Content-Type'))
  if r.status_code!=200:return rcp
  if b[:4]==b'%PDF':
   p=CACHE/(slug+'-'+sha(b)[:14]+'.pdf');p.write_bytes(b);d=fitz.open(stream=b,filetype='pdf')
   pp=[]
   for i,page in enumerate(d):
    txt=page.get_text()
    if re.search(r'remuneration|employee.{0,20}(75,000|75000)|council.{0,20}expenses',txt,re.I):pp.append({'physicalPage':i+1,'textCharacters':len(txt),'preview':txt[:1500]})
   rcp.update(cachePath=str(p),pages=len(d),textCharacters=sum(len(p.get_text()) for p in d),salaryTextCandidates=pp)
  else:
   p=OUT/'index-snapshots'/(slug+'-'+sha(b)[:14]+'.html.gzip');p.write_bytes(gzip.compress(b,mtime=0));rcp['snapshotFile']=str(p.relative_to(OUT))
   soup=Links();soup.feed(r.text);links=[]
   for href,label in soup.items:
    u=urljoin(str(r.url),href)
    if re.search(r'sofi|statement.{0,25}financial|annual.{0,12}report|remuneration',label+' '+u,re.I) and u.startswith(('https://','http://')) and not re.search('facebook|twitter|linkedin|mailto',u,re.I):links.append({'url':u,'label':label,'periodVerified':False})
   rcp['candidates']=list({a['url']:a for a in links}.values())
 except Exception as e:rcp['error']=str(e)
 return rcp

def main():
 OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
 cov=json.loads((ROOT/'research/salaries/municipal-audit/coverage.json').read_text())
 sources=[]
 for coll in json.loads((ROOT/'research/salaries/collections.json').read_text())['collections']:
  p=ROOT/'research/salaries'/coll/'sources.json'
  for s in json.loads(p.read_text())['sources']:sources.append(dict(s,collection=coll))
 inv=[];tasks=[]
 for m in cov['municipalities']:
  accepted=[s for s in sources if s.get('employerSlug')==m['employerSlug']]
  entry={k:m.get(k) for k in ['employerSlug','employerName','municipality','status','website','archiveUrl','regionalDistrict']}
  entry.update(baselineOfficialEmployeeYears=sorted({str(s['year']) for s in accepted if s.get('category')=='employee-remuneration'}),baselineOfficialCouncilYears=sorted({str(s['year']) for s in accepted if s.get('category')=='elected-officials'}),baselineOfficialRows=sum(s.get('rowCount',0) for s in accepted),baselineAcceptedCohorts=[{'id':s['id'],'collection':s['collection'],'year':s['year'],'category':s.get('category'),'rowCount':s.get('rowCount')} for s in accepted],compiledEditionLabels=m.get('compiledUnverifiedEditionLabels',[]),historicalCompletenessEstablished=False)
  inv.append(entry)
  if m['status']!='pending-incorporation':
   urls=[m['archiveUrl'] or m['website']]
   # Every current uncovered jurisdiction receives a fresh direct official retrieval.
   # Add direct named-schedule links previously recorded, bounded to avoid unrelated annual reports.
   urls += [s['url'] for s in m.get('sourceLeads',[]) if not m['officialRecords'] and re.search(r'sofi|statement.{0,25}financial|remuneration',s['url']+' '+s.get('label',''),re.I)][:4]
   for u in dict.fromkeys(urls):
    if u:tasks.append((m['employerSlug'],u,'uncovered-official-recheck' if not m['officialRecords'] else 'historical-archive-recheck'))
 dump(OUT/'inventory.json',{'version':1,'asOf':'2026-11-01','baselineCommit':'c1cdde042f2d256e562ae027a5cfcac5808cc626','jurisdictions':inv,'scopeNotes':cov['scopeNotes']})
 prior=json.loads((OUT/'archive-receipts.json').read_text()) if (OUT/'archive-receipts.json').exists() else []
 known={(r['employerSlug'],r['url']):r for r in prior}
 missing=[t for t in tasks if (t[0],t[1]) not in known]
 with cf.ThreadPoolExecutor(max_workers=12) as pool:extra=list(pool.map(retrieve,missing))
 known.update({(r['employerSlug'],r['url']):r for r in extra})
 receipts=[known[(t[0],t[1])] for t in tasks]
 dump(OUT/'archive-receipts.json',receipts)
 print(json.dumps({'jurisdictions':len(inv),'uncoveredCurrentChecked':len({r['employerSlug'] for r in receipts}),'retrievals':len(receipts),'pdfs':sum('pages'in r for r in receipts),'candidateLinks':sum(len(r.get('candidates',[])) for r in receipts)}))
if __name__=='__main__':main()
