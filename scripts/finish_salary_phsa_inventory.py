#!/usr/bin/env python3
"""Retrieve and fingerprint the nine official historical PHSA employee scans."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import datetime

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
CACHE=Path('/tmp/queue-completion-phsa')
PRIOR=ROOT/'research/salaries/requests/downloaded-health-sources-2026-10-30.json'


def digest(raw):return hashlib.sha256(raw).hexdigest()


def acquire(source):
    import fitz
    year=source['year'];key='phsa-'+year.replace('/','-')
    path=CACHE/'originals'/(key+'.pdf');path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        raw=path.read_bytes();acquisition='existing-cache'
    else:
        with urllib.request.urlopen(source['sourceUrl'],timeout=120) as response:
            raw=response.read()
        if not raw.startswith(b'%PDF'):raise ValueError('Not an original PDF: '+key)
        path.write_bytes(raw);acquisition='official-public-download'
    if digest(raw)!=source['sha256'] or len(raw)!=source['bytes']:
        raise ValueError('Official original differs from previously pinned source: '+key)
    doc=fitz.open(path)
    pages=[]
    for n,p in enumerate(doc,1):
        infos=p.get_image_info(xrefs=True)
        pages.append({'physicalPage':n,'pageSize':list(p.rect),'nativeTextChars':len(p.get_text()),
                      'fontCount':len(p.get_fonts()),'images':[{'xref':i['xref'],'bbox':list(i['bbox']),
                                                             'width':i['width'],'height':i['height'],
                                                             'xres':i['xres'],'yres':i['yres']} for i in infos]})
    samples=[]
    for n in sorted({1,len(doc)//2,len(doc)}):
        image=CACHE/'inventory-images'/f'{key}-p{n:03d}-actual300.png';image.parent.mkdir(parents=True,exist_ok=True)
        doc[n-1].get_pixmap(dpi=300,alpha=False).save(image)
        samples.append({'physicalPage':n,'path':str(image),'sha256':digest(image.read_bytes())})
    out={'id':key,'year':year,'sourceUrl':source['sourceUrl'],
         'sourceIndexUrl':'https://www.phsa.ca/about/accountability/budget-financials',
         'sourceSha256':digest(raw),'pdfBytes':len(raw),'pdfPages':len(doc),'cachePath':str(path),
         'priorOriginalSha256':source['sha256'],'originalMatchesPriorPin':True,
         'priorDownloadManifest':str(PRIOR.relative_to(ROOT)),
         'acquisition':acquisition,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'nativeTextChars':sum(p['nativeTextChars'] for p in pages),'allPageGeometry':pages,
         'actual300DpiInventoryImages':samples,'retainCompiledPartition':True}
    receipt=AREA/(key+'-inventory.json');receipt.parent.mkdir(parents=True,exist_ok=True)
    if receipt.exists():
        old=json.loads(receipt.read_text())
        for k in ['acquisition','checkedAt']:out[k]=old[k]
        if old!=out:raise ValueError('Pinned original inventory changed: '+key)
    else:receipt.write_text(json.dumps(out,indent=2)+'\n')
    return out


def run():
    selected=[s for s in json.loads(PRIOR.read_text()) if s['id'].startswith('phsa-') and s['year']!='2024/25']
    if len(selected)!=9:raise ValueError('Expected precisely nine earlier PHSA originals')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        sources=list(pool.map(acquire,selected))
    manifest={'sourceCount':9,'pdfPages':sum(s['pdfPages'] for s in sources),
              'sources':[{k:s[k] for k in ['id','year','sourceUrl','sourceIndexUrl','sourceSha256','pdfBytes',
                                          'pdfPages','cachePath','nativeTextChars','retainCompiledPartition']} for s in sources]}
    path=AREA/'source-inventory.json';raw=(json.dumps(manifest,indent=2)+'\n').encode()
    if path.exists() and path.read_bytes()!=raw:raise ValueError('Source inventory changed')
    path.write_bytes(raw)
    print(json.dumps(manifest))


if __name__=='__main__':run()
