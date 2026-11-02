#!/usr/bin/env python3
"""Refresh bounded public board-source routes and preserve source fingerprints."""
import concurrent.futures
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_boards'
CACHE=Path('/workspace/gap-health-boards-cache')

def digest(b):return hashlib.sha256(b).hexdigest()

def routes():
    old=json.loads((ROOT/'research/salaries/continuation-2026-11-01/health/board-retrieval-receipts.json').read_bytes())
    selected=[r for r in old if r['employer'] in ['island-health','provincial-health-services-authority']]
    selected=[r for r in selected if not any(x in r['url'] for x in ['PHSA%20Board%20Remuneration%20Summary%202024','PHSA%20Board%20Remuneration%20Summary%202025'])]
    selected += [{'employer':'vancouver-coastal-health','url':'https://www.vch.ca/en/media/23716'},
                 {'employer':'vancouver-coastal-health','url':'https://www.vch.ca/en/media/23716/download'},
                 {'employer':'island-health','url':'https://www.islandhealth.ca/about-us/plans-reports-and-policies/financial-reports'},
                 {'employer':'provincial-health-services-authority','url':'https://www.phsa.ca/about/accountability/budget-financials'}]
    return selected

def fetch(route):
    item={k:v for k,v in route.items() if k in ['employer','url','indexUrl','label']}
    item['checkedAtUtc']=datetime.now(timezone.utc).isoformat()
    key=digest(route['url'].encode())[:18]
    try:
        req=urllib.request.Request(route['url'],headers={'User-Agent':'Mozilla/5.0 (compatible; public-disclosure-source-review)'})
        with urllib.request.urlopen(req,timeout=50) as res:
            raw=res.read();item.update(status=res.status,finalUrl=res.url,contentType=res.headers.get('Content-Type'),bytes=len(raw),sha256=digest(raw))
        if raw.startswith(b'%PDF'):
            dest=CACHE/(key+'-'+digest(raw)+'.pdf')
            if dest.exists():assert dest.read_bytes()==raw
            else:dest.write_bytes(raw)
            item['cachePath']=str(dest);item['isPdf']=True
        else:
            dest=AREA/'http-snapshots'/(key+'.bin.gzip');dest.parent.mkdir(exist_ok=True)
            dest.write_bytes(gzip.compress(raw,mtime=0));item['snapshotPath']=str(dest.relative_to(ROOT));item['isPdf']=False
    except urllib.error.HTTPError as err:
        raw=err.read();item.update(status=err.code,error=str(err),bytes=len(raw),responseSha256=digest(raw))
    except Exception as err:item['error']=str(err)
    old=Path(route.get('cachePath','/nonexistent'))
    if old.exists():
        raw=old.read_bytes()
        assert digest(raw)==route['sha256'],old
        item['previousVerifiedReceipt']={'path':route['cachePath'],'sha256':route['sha256'],'retrievedAt':route.get('retrievedAt')}
        if not item.get('isPdf'):
            dest=CACHE/(key+'-'+digest(raw)+'.pdf')
            if dest.exists():assert dest.read_bytes()==raw
            else:dest.write_bytes(raw)
            item['cachePath']=str(dest)
            item['sourceSha256']=route['sha256'];item['sourceIsPreviousVerifiedDownload']=True
        else:item['samePdfAsPreviousVerifiedDownload']=digest(raw)==item['sha256']
    return item

def main():
    CACHE.mkdir(exist_ok=True);AREA.mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:items=list(pool.map(fetch,routes()))
    (AREA/'retrieval-refresh.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{'employer':x['employer'],'status':x.get('status'),'pdf':x.get('isPdf'),'previous':x.get('sourceIsPreviousVerifiedDownload'),'url':x['url']} for x in items],indent=2))

if __name__=='__main__':main()
