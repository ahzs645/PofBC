#!/usr/bin/env python3
"""Persist public retrieval evidence for the November health-history gap pass."""
from __future__ import annotations
import base64,datetime,gzip,hashlib,json,pathlib,urllib.request,urllib.error

ROOT=pathlib.Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_employees'
CACHE=pathlib.Path('/workspace/gap-health-employees-cache')

def sha(raw):return hashlib.sha256(raw).hexdigest()

def fetch(url,purpose='Refresh public source',issuer='health-authorities'):
    receipts=AREA/'retrievals';receipts.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    key=sha(url.encode())[:24];rp=receipts/(key+'.json');bp=CACHE/(key+'.body')
    if rp.exists():
        r=json.loads(rp.read_bytes())
        if bp.exists() and sha(bp.read_bytes())==r.get('responseSha256'):return r
    at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        try:response=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (public salary-source research)'}),timeout=45)
        except urllib.error.HTTPError as e:response=e
        body=response.read();headers=dict(response.headers);bp.write_bytes(body)
        lower={k.lower():v for k,v in headers.items()};decl=lower.get('content-length');decl=int(decl) if decl and decl.isdigit() else None
        archive=lower.get('x-archive-orig-content-length');archive=int(archive) if archive and archive.isdigit() else None
        truncated=bool(archive and archive>len(body)) or 'truncat' in lower.get('warning','').lower()
        pdf=body.startswith(b'%PDF-');eof=body.rstrip().endswith(b'%%EOF') if pdf else False
        r={'url':url,'finalUrl':response.geturl(),'purpose':purpose,'issuer':issuer,'retrievedAtUtc':at,'status':response.code,'contentType':lower.get('content-type'),'bytes':len(body),'responseSha256':sha(body),'cachePath':str(bp),'isPdf':pdf,'hasPdfEof':eof,'explicitTruncation':truncated,'candidateOriginal':response.code==200 and pdf and eof and not truncated and (decl is None or decl==len(body)),'headers':headers,'sourceAccepted':False}
        if not pdf:
            sp=AREA/'http-snapshots'/(key+'.json.gzip');sp.parent.mkdir(exist_ok=True)
            snap={'url':url,'finalUrl':response.geturl(),'status':response.code,'headers':headers,'bodyBase64':base64.b64encode(body).decode(),'bodySha256':sha(body)}
            sp.write_bytes(gzip.compress(json.dumps(snap,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
            r.update(snapshotPath=str(sp.relative_to(ROOT)),snapshotSha256=sha(sp.read_bytes()))
    except (urllib.error.URLError,TimeoutError,OSError) as e:
        r={'url':url,'purpose':purpose,'issuer':issuer,'retrievedAtUtc':at,'status':None,'error':str(e),'sourceAccepted':False}
    rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');return r

def read(r):return pathlib.Path(r['cachePath']).read_bytes()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('--issuer',default='health-authorities');p.add_argument('--purpose',default='Refresh public source');a=p.parse_args()
    print(json.dumps(fetch(a.url,a.purpose,a.issuer),ensure_ascii=False,indent=2))
