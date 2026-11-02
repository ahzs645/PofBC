#!/usr/bin/env python3
"""Follow exact public Legislative Library item→ORIGINAL→content relationships."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_boards'
CACHE=Path('/workspace/gap-health-boards-cache')
BASE='https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api'
ITEMS=[('vch','2022/23','a106e529-b28f-4391-bda6-0ca1cc2fd92f'),
       ('island','2018/19','7deb1d69-64d8-4c61-b7d6-16b1945513d7'),
       ('island','2019/20','426d3de1-602a-4d64-a164-c86de1d7b514')]

def main():
    CACHE.mkdir(exist_ok=True);receipts=[];originals=[]
    def get(url):
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PofBC-public-source-review'}),timeout=60) as res:
            raw=res.read();receipts.append({'url':url,'finalUrl':res.url,'status':res.status,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'checkedAtUtc':datetime.now(timezone.utc).isoformat()})
        if raw.startswith(b'%PDF'):return raw
        (AREA/('library-'+hashlib.sha256(url.encode()).hexdigest()[:12]+'.json')).write_bytes(raw)
        return json.loads(raw)
    for issuer,year,item in ITEMS:
        metadata=get(BASE+'/core/items/'+item)
        bundles=get(BASE+'/core/items/'+item+'/bundles')
        for bundle in bundles['_embedded']['bundles']:
            if bundle['name']!='ORIGINAL':continue
            bitstreams=get(bundle['_links']['bitstreams']['href'])['_embedded']['bitstreams']
            for bit in bitstreams:
                url=bit['_links']['content']['href'];raw=get(url)
                assert raw.startswith(b'%PDF'),url
                content_sha=hashlib.sha256(raw).hexdigest()
                path=CACHE/(issuer+'-'+year.replace('/','-')+'-board-'+bit['uuid']+'-'+content_sha+'.pdf')
                if path.exists():assert path.read_bytes()==raw
                else:path.write_bytes(raw)
                originals.append({'issuer':issuer,'year':year,'itemUuid':item,'bitstreamUuid':bit['uuid'],'sourceUrl':url,'cachePath':str(path),'sha256':content_sha,'catalogueSerialIssue':metadata['metadata'].get('local.title.serialissue')})
    (AREA/'library-originals.json').write_text(json.dumps(originals,ensure_ascii=False,indent=2)+'\n')
    (AREA/'library-current-retrieval-receipts.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(originals,indent=2))

if __name__=='__main__':main()
