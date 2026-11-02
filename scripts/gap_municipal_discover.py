#!/usr/bin/env python3
"""Refresh eight bounded municipal leads and inventory exact original salary pages."""
import concurrent.futures,gzip,hashlib,json,re,subprocess,time,urllib.request
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/municipal';CACHE=Path('/workspace/gap-municipal-cache');CACHE.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def save(path,r):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(gzip.compress(json.dumps(r,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
def run():
 assigned=json.loads((AREA/'assigned-leads.json').read_bytes());seeds=[]
 slugs={'City of Abbotsford':'city-of-abbotsford','City of Port Moody':'city-of-port-moody','City of Rossland':'city-of-rossland','City of Trail':'city-of-trail','District of 100 Mile House':'district-of-100-mile-house','District of Barriere':'district-of-barriere','District of Clearwater':'district-of-clearwater','District of Lantzville':'district-of-lantzville'}
 for a in assigned:seeds.append({'leadId':a['id'],'employerSlug':slugs[a['employer']],'sourceUrl':a['sourceUrl'],'sourceIndexUrl':a['sourceIndexUrl'],'primaryLead':True})
 old=json.loads((ROOT/'research/salaries/municipal-history-pass/interior/source-inventory.json').read_bytes())
 for s in old['sources']:
  if s['employerSlug'] not in ['city-of-rossland','city-of-trail','district-of-clearwater','district-of-barriere']:continue
  a=next(a for a in assigned if slugs[a['employer']]==s['employerSlug'])
  seeds.append({'leadId':a['id'],'employerSlug':s['employerSlug'],'sourceUrl':s['sourceUrl'],'sourceIndexUrl':s['sourceIndexUrl'],'oldSha256':s['sha256'],'oldCacheFile':str(Path('/tmp/wave-interior')/s['cacheFile'])})
 unique={s['sourceUrl']:s for s in seeds};seeds=list(unique.values())
 index=json.loads((ROOT/'public/salaries/employers/index.json').read_bytes());sources=index['sources'];known={}
 for sid,s in sources.items():
  if s.get('sha256'):known.setdefault(s['sha256'],[]).append({'sourceId':sid,'year':s.get('year'),'scope':s.get('scope'),'rows':s.get('rowCount')})
 def fetch(s):
  receipt=dict(s);start=time.time();key=s['employerSlug']+'-'+sha(s['sourceUrl'].encode())[:12]
  try:
   request=urllib.request.Request(s['sourceUrl'],headers={'User-Agent':'PofBC source audit; public records verification'})
   with urllib.request.urlopen(request,timeout=45) as res:raw=res.read();receipt.update(httpStatus=res.status,retrievedUrl=res.url,contentType=res.headers.get('Content-Type'))
   receipt.update(bytes=len(raw),sha256=sha(raw),oldHashUnchanged=sha(raw)==s.get('oldSha256'),cachedOriginal=str(CACHE/(key+('.pdf' if raw.startswith(b'%PDF') else '.html'))))
   Path(receipt['cachedOriginal']).write_bytes(raw)
   if not raw.startswith(b'%PDF'):receipt['status']='retrieved-non-pdf';return receipt
   doc=fitz.open(stream=raw,filetype='pdf');receipt.update(originalPages=len(doc),acceptedScopes=known.get(sha(raw),[]));pages=[]
   for p in doc:
    txt=p.get_text();d={'physicalPage':p.number+1,'nativeCharacters':len(txt),'text':txt}
    hits=re.findall(r'.{0,70}(?:remuneration|employee|council|75,000|salary).{0,120}',txt,re.I)
    d['hits']=hits;pages.append(d)
   save(AREA/'native'/f'{key}.json.gzip',{'sourceSha256':sha(raw),'pages':pages})
   receipt.update(status='accepted-current-exact-original' if receipt['acceptedScopes'] else 'original-needs-complete-review',nativeEvidence=f'native/{key}.json.gzip',nativeTextCharacters=sum(p['nativeCharacters'] for p in pages),candidatePages=[{'physicalPage':p['physicalPage'],'nativeCharacters':p['nativeCharacters'],'hits':p['hits'][:12]} for p in pages if p['hits']])
  except Exception as e:receipt.update(status='retrieval-failed',error=type(e).__name__+': '+str(e))
  receipt['seconds']=round(time.time()-start,2);print(json.dumps({k:receipt.get(k) for k in ['leadId','employerSlug','sha256','status','originalPages','nativeTextCharacters']}),flush=True);return receipt
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:receipts=list(pool.map(fetch,seeds))
 out={'refreshedOn':'2026-11-02','noOutreach':True,'sources':receipts};(AREA/'refreshed-originals.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'sources':len(receipts),'originals':len({r.get('sha256') for r in receipts if r.get('originalPages')}),'out':str(AREA/'refreshed-originals.json')}))
if __name__=='__main__':run()
