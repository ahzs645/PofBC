#!/usr/bin/env python3
"""Review every metadata result of the bounded2014council exact-phrase query."""
import concurrent.futures,json,re,urllib.parse,urllib.request
from pathlib import Path
AREA=Path(__file__).resolve().parents[1]/'research/salaries/gap-fill-2026-11-02/municipal'
def run(page):
 u='https://rossland.civicweb.net/api/documents/search?'+urllib.parse.urlencode({'all':'2014','exact':'Council Remuneration','page':page,'ordercolumn':'relevance','orderascending':'false'})
 with urllib.request.urlopen(u,timeout=45) as res:r=json.load(res)
 (AREA/'routes'/f'api-2014-council-page{page}.json').write_text(json.dumps({'url':u,'response':r},ensure_ascii=False,indent=2)+'\n');return r
if __name__=='__main__':
 first=json.loads((AREA/'routes/api-2014-council.json').read_bytes())['response']
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:others=list(pool.map(run,range(2,8)))
 rows=first['Results']+[x for r in others for x in r['Results']];assert len(rows)==64
 (AREA/'rossland-2014-council-search-all-results.json').write_text(json.dumps({'queryTotal':64,'all64metadataResultsInspected':True,'noOutreach':True,'results':rows},ensure_ascii=False,indent=2)+'\n')
 for r in rows:
  if re.search('2014|2015|2016|14\.|15\.|16\.',r['TitleHtml']+' '+r['PathHtml']):print(r['Id'],r['TitleHtml'],r['FileSize'])
