#!/usr/bin/env python3
"""Bounded public-source retrieval receipts; no contact or submission functions."""
from __future__ import annotations
import argparse,base64,datetime,gzip,hashlib,json,pathlib
import urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/acquisition'
CACHE=pathlib.Path('/tmp/salary-queue-acquisition')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def classification(status,headers,body):
    is_pdf=body.startswith(b'%PDF-')
    length=headers.get('Content-Length') or headers.get('content-length')
    declared=int(length) if length and length.isdigit() else None
    warning=headers.get('Warning') or headers.get('warning')
    lower={k.lower():v for k,v in headers.items()}
    archive_length=lower.get('x-archive-orig-content-length')
    archive_declared=int(archive_length) if archive_length and archive_length.isdigit() else None
    truncated=bool(warning and 'truncat' in warning.lower()) or bool(archive_declared and archive_declared>len(body))
    eof=body.rstrip().endswith(b'%%EOF') if is_pdf else False
    # A magic header alone never proves completeness, scope or source acceptance.
    return {'isPdf':is_pdf,'candidateOriginal':status==200 and is_pdf and eof and not truncated and (declared is None or declared==len(body)),
            'hasPdfEof':eof,'explicitArchiveTruncation':truncated,'archiveReportedOriginalLength':archive_declared,
            'declaredResponseLength':declared,'lengthMatchesDeclaredResponse':declared==len(body) if declared is not None else None,
            'warning':warning,'sourceAccepted':False}
def fetch(url,purpose,issuer):
    AREA.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    p=AREA/'retrievals.json';arr=json.loads(p.read_text()) if p.exists() else []
    previous=next((r for r in arr if r['url']==url),None)
    if previous:return previous
    key=sha(url.encode())[:20];body_path=CACHE/(key+'.body');at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        try:
            response=urllib.request.urlopen(url,timeout=45)
        except urllib.error.HTTPError as exc:
            response=exc
        body=response.read();headers=dict(response.headers);body_path.write_bytes(body)
        r={'url':url,'finalUrl':response.geturl(),'purpose':purpose,'issuer':issuer,'retrievedAt':at,'status':response.code,
           'contentType':response.headers.get('Content-Type'),'bytes':len(body),'responseSha256':sha(body),'cachePath':str(body_path),
           'headers':headers,**classification(response.code,headers,body)}
        if not r['isPdf']:
            snapshot={'url':url,'finalUrl':response.url,'status':response.code,'headers':headers,'bodyBase64':base64.b64encode(body).decode(),'bodySha256':sha(body)}
            raw=(json.dumps(snapshot,ensure_ascii=False,separators=(',',':'))+'\n').encode();sp=AREA/'http-snapshots'/(key+'.json.gzip');sp.parent.mkdir(exist_ok=True);sp.write_bytes(gzip.compress(raw,mtime=0));r['snapshotPath']=str(sp.relative_to(ROOT));r['snapshotSha256']=sha(sp.read_bytes())
    except (urllib.error.URLError,TimeoutError,OSError) as exc:
        r={'url':url,'purpose':purpose,'issuer':issuer,'retrievedAt':at,'status':None,'error':str(exc),'sourceAccepted':False}
    arr.append(r);p.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n');return r
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('--purpose',required=True);p.add_argument('--issuer',required=True);a=p.parse_args();r=fetch(a.url,a.purpose,a.issuer);print(json.dumps({k:v for k,v in r.items() if k!='headers'},ensure_ascii=False))
