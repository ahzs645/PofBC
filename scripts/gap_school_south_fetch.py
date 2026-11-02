#!/usr/bin/env python3
"""Refresh the ten assigned public school originals without issuer contact."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_south'
CACHE=Path('/workspace/gap-school-south-cache')

def download(lead):
    import fitz
    key=lead['sourceUrl'].rsplit('/',1)[-1].removesuffix('.pdf')
    request=urllib.request.Request(lead['sourceUrl'],headers={'User-Agent':'PofBC public salary source audit'})
    with urllib.request.urlopen(request,timeout=90) as response:
        raw=response.read();status=response.status;url=response.url;headers=dict(response.headers)
    assert raw.startswith(b'%PDF-'),(key,raw[:100])
    CACHE.mkdir(exist_ok=True);path=CACHE/(key+'.pdf');path.write_bytes(raw)
    pdf=fitz.open(path)
    text=subprocess.check_output(['pdftotext','-layout',str(path),'-'])
    (AREA/(key+'-poppler.txt.gzip')).write_bytes(gzip.compress(text,mtime=0))
    pages=[]
    for number,page in enumerate(pdf,1):
        native=page.get_text()
        pages.append({'physicalPage':number,'width':page.rect.width,'height':page.rect.height,'nativeChars':len(native),'imageCount':len(page.get_images()),'nativeHead':native[:250]})
    result={'leadId':lead['id'],'key':key,'sourceUrl':lead['sourceUrl'],'retrievedOn':'2026-11-02','httpStatus':status,'finalUrl':url,'httpHeaders':headers,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'cachePath':str(path),'pageCount':len(pdf),'pages':pages}
    (AREA/(key+'-retrieval.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(key,len(pdf),'pages',sum(x['nativeChars'] for x in pages),'nativechars',flush=True)
    return result

if __name__=='__main__':
    leads=json.loads((AREA/'assigned-leads.json').read_text())
    # MuPDF reads stay sequential; independent document objects are not thread-safe.
    results=[download(lead) for lead in leads]
    (AREA/'retrievals.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
