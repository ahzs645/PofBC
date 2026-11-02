#!/usr/bin/env python3
"""Replay public CivicWeb's own GET search API for missing historical originals."""
import concurrent.futures,json,urllib.parse,urllib.request
from pathlib import Path
AREA=Path(__file__).resolve().parents[1]/'research/salaries/gap-fill-2026-11-02/municipal'
def query(s):
 key,params=s;u='https://rossland.civicweb.net/api/documents/search?'+urllib.parse.urlencode({**params,'page':1,'ordercolumn':'relevance','orderascending':'false'})
 with urllib.request.urlopen(u,timeout=45) as res:r=json.load(res)
 (AREA/'routes'/('api-'+key+'.json')).write_text(json.dumps({'url':u,'response':r},ensure_ascii=False,indent=2)+'\n')
 print(key,r['Total'],[(x['Id'],x['TitleHtml']) for x in r['Results']],flush=True);return key,params,r
if __name__=='__main__':
 specs=[('2014-employee',{'all':'2014','exact':'Employee Remuneration'}),('2011-employee',{'all':'2011','exact':'Employee Remuneration'}),('2014-sofi',{'exact':'SOFI 2014'}),('2011-sofi',{'exact':'SOFI 2011'})]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rs=list(pool.map(query,specs))
 (AREA/'rossland-search-api-summary.json').write_text(json.dumps([{'key':k,'params':p,'total':r['Total'],'results':r['Results']} for k,p,r in rs],ensure_ascii=False,indent=2)+'\n')
