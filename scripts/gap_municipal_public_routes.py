#!/usr/bin/env python3
"""Bounded official public archive searches for the remaining source questions."""
import concurrent.futures,hashlib,html,json,re,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/municipal'
def fetch(pair):
 key,url=pair;out={'key':key,'url':url}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PofBC municipal source review'}),timeout=40) as res:raw=res.read();out.update(status=res.status,resolvedUrl=res.url,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  (AREA/'routes').mkdir(exist_ok=True);p=AREA/'routes'/(key+'.html');p.write_bytes(raw);out['snapshot']=str(p.relative_to(ROOT));s=raw.decode(errors='replace');out['documentLinks']=[]
  for a,b in re.findall(r'<a\b[^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>(.*?)</a>',s,re.I|re.S):
   a=html.unescape(a);b=html.unescape(re.sub('<[^>]+>',' ',b)).strip()
   if '/document/' in a:out['documentLinks'].append({'label':b,'url':urllib.parse.urljoin(url,a)})
  out['resultCountText']=re.findall(r'.{0,80}(?:results found|documents found|No results|No Results|Results).*',s)[:6]
 except Exception as e:out.update(error=type(e).__name__+': '+str(e))
 return out
if __name__=='__main__':
 queries=['SOFI 2014','SOFI 2011','2014 remuneration','2011 remuneration','2014 financial information','2011 financial information']
 tasks=[('rossland-search-'+str(i+1),'https://rossland.civicweb.net/filepro/documents/search?'+urllib.parse.urlencode({'keywords':q})) for i,q in enumerate(queries)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:r=list(pool.map(fetch,tasks))
 (AREA/'public-route-search-receipts.json').write_text(json.dumps({'performedOn':'2026-11-02','queries':queries,'noOutreach':True,'searches':r},ensure_ascii=False,indent=2)+'\n')
 for x in r:print(json.dumps({'key':x['key'],'status':x.get('status'),'links':x.get('documentLinks'),'error':x.get('error')},ensure_ascii=False))
