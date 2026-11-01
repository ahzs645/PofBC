#!/usr/bin/env python3
"""Fresh official-index check for every existing Crown-sector identity."""
import concurrent.futures,hashlib,json,pathlib,urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/continuation-2026-11-01/crowns';CACHE=pathlib.Path('/tmp/continuation-crowns')
class Links(HTMLParser):
 def __init__(self):super().__init__();self.cur=None;self.out=[]
 def handle_starttag(self,t,a):
  if t=='a':self.cur=[dict(a).get('href'),[]]
 def handle_data(self,d):
  if self.cur:self.cur[1].append(d)
 def handle_endtag(self,t):
  if t=='a' and self.cur:
   if self.cur[0]:self.out.append({'url':self.cur[0],'label':' '.join(''.join(self.cur[1]).split())})
   self.cur=None

def one(e):
 candidates=[]
 for r in e['retrievals']:
  if r.get('httpStatus')==200 and r.get('format')=='html':candidates.append(r['url'])
 if not candidates:candidates=[e.get('searchIndex') or e['website']]
 receipts=[]
 for u in list(dict.fromkeys(candidates))[:2]:
  try:
   req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 public salary source research'})
   with urllib.request.urlopen(req,timeout=25) as r:b=r.read();status=r.status;final=r.url;ctype=r.headers.get('Content-Type','')
   digest=hashlib.sha256(b).hexdigest();p=CACHE/('index-'+digest[:16]+'.html');p.write_bytes(b);parser=Links();parser.feed(b.decode(errors='replace'))
   links=[{'url':urljoin(final,l['url']),'label':l['label']} for l in parser.out if any(s in (l['url']+' '+l['label']).lower() for s in ['financial','sofi','compensation','remuneration','governance','corporate-report'])]
   receipts.append({'url':u,'finalUrl':final,'httpStatus':status,'contentType':ctype,'bytes':len(b),'sha256':digest,'localPath':str(p),'relevantLinks':links,'retrievedOn':'2026-11-01'})
  except Exception as ex:receipts.append({'url':u,'error':str(ex),'retrievedOn':'2026-11-01'})
 return {'employerSlug':e['employerSlug'],'employerName':e['employerName'],'receipts':receipts,'scope':'Fresh official-index check; indexed labels and URLs are discovery leads, not verified salary observations. Unlisted historical periods remain unresolved.'}

def main():
 old=json.loads((ROOT/'research/salaries/sector-search-2026-10-31/crowns/discovery.json').read_text())['employers'];rs=list(concurrent.futures.ThreadPoolExecutor(max_workers=7).map(one,old));(OUT/'fresh-index-receipts.json').write_text(json.dumps({'date':'2026-11-01','employerEntriesChecked':len(rs),'employers':rs},indent=2,ensure_ascii=False)+'\n');print(json.dumps({'employers':len(rs),'successfulEntries':sum(any(r.get('httpStatus')==200 for r in e['receipts']) for e in rs),'failedEntries':[e['employerSlug'] for e in rs if not any(r.get('httpStatus')==200 for r in e['receipts'])]}))
if __name__=='__main__':main()
