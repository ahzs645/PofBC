#!/usr/bin/env python3
"""Follow explicit public Legislative Library item records, never broad URL guesses."""
import json
from finish_salary_acquisition_fetch import fetch
BASE='https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api/core'
def originals(uuid,issuer):
    r=fetch(f'{BASE}/items/{uuid}/bundles','Follow explicit official library item ORIGINAL bundle',issuer)
    if r.get('status')!=200:return []
    a=json.load(open(r['cachePath']));found=[]
    for b in a.get('_embedded',{}).get('bundles',[]):
        if b['name']!='ORIGINAL':continue
        q=fetch(b['_links']['bitstreams']['href'],'Read explicit library ORIGINAL bitstream metadata',issuer)
        if q.get('status')!=200:continue
        c=json.load(open(q['cachePath']))
        for bs in c.get('_embedded',{}).get('bitstreams',[]):
            found.append({'itemUuid':uuid,'bundleUuid':b['uuid'],'bitstreamUuid':bs['uuid'],'name':bs['name'],'storedBytes':bs.get('sizeBytes'),'storedChecksum':bs.get('checkSum'),'contentUrl':bs['_links']['content']['href'],'metadataResponseSha256':q['responseSha256']})
    return found
