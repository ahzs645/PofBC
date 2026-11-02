#!/usr/bin/env python3
"""Follow explicit official serial records and ORIGINAL bundles for health gaps."""
import json,concurrent.futures,urllib.parse
from gap_health_employees_fetch import fetch,read,AREA
BASE='https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api'
SERIES={'Fraser Health':'362749','Interior Health':'362725','Northern Health':'361528','Providence Health Care':'167440','Provincial Health Services Authority':'363248','Vancouver Coastal Health':'361866','Vancouver Island Health':'362722'}

def originals(item):
    r=fetch(f"{BASE}/core/items/{item['uuid']}/bundles",'Follow explicit ORIGINAL bundle',item['issuer'])
    found=[]
    if r.get('status')!=200:return found
    for b in json.loads(read(r)).get('_embedded',{}).get('bundles',[]):
        if b['name']!='ORIGINAL':continue
        q=fetch(b['_links']['bitstreams']['href'],'Read explicit ORIGINAL bitstream metadata',item['issuer'])
        if q.get('status')!=200:continue
        for bs in json.loads(read(q)).get('_embedded',{}).get('bitstreams',[]):
            found.append({'item':item,'name':bs['name'],'bitstreamUuid':bs['uuid'],'storedBytes':bs.get('sizeBytes'),'storedChecksum':bs.get('checkSum'),'url':bs['_links']['content']['href'],'bundleMetadataSha256':q['responseSha256']})
    return found

def catalogue():
    def one(pair):
        issuer,key=pair;u=f'{BASE}/discover/search/objects?'+urllib.parse.urlencode({'f.controlkey':key+',equals','size':100})
        r=fetch(u,'Refresh exact official serial catalogue',issuer);out=[]
        if r.get('status')!=200:return out
        result=json.loads(read(r))['_embedded']['searchResult']
        objects=list(result.get('_embedded',{}).get('objects',[]))
        for page in range(1,result['page']['totalPages']):
            extra=fetch(u+'&page='+str(page),'Complete explicit serial catalogue pagination',issuer)
            if extra.get('status')!=200:raise ValueError(('Catalogue page unavailable',issuer,page))
            objects.extend(json.loads(read(extra))['_embedded']['searchResult'].get('_embedded',{}).get('objects',[]))
        for o in objects:
            ob=o['_embedded']['indexableObject'];md=ob.get('metadata',{})
            out.append({'issuer':issuer,'uuid':ob['uuid'],'title':ob['name'],'handle':ob['handle'],'metadata':md,'discoveryUrl':u,'discoveryResponseSha256':r['responseSha256'],'serialIssue':[v['value'] for v in md.get('local.title.serialissue',[])]})
        return out
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as p:out=[v for sub in p.map(one,SERIES.items()) for v in sub]
    (AREA/'exact-serial-catalogue.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    return out

if __name__=='__main__':
    c=catalogue()
    for issuer in SERIES:
        relevant=[x for x in c if x['issuer']==issuer and any(w in ' '.join(x['serialIssue']).lower() for w in ['employee','remuneration','financial information']) and 'board' not in ' '.join(x['serialIssue']).lower()]
        print(issuer,len([x for x in c if x['issuer']==issuer]),[(x['uuid'],x['serialIssue']) for x in relevant])
