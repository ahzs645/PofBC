#!/usr/bin/env python3
"""Capture independent native-reader outputs without accepting any salary source."""
import concurrent.futures,gzip,json,pathlib,subprocess
import fitz
from gap_health_employees_fetch import ROOT,AREA,sha

def one(spec):
    source=pathlib.Path(spec['retrieval']['cachePath']);assert sha(source.read_bytes())==spec['sourceSha256']
    key=spec['item']['employerSlug']+'-'+spec['item']['candidateYear'].replace('/','-')
    out=AREA/'reader-output-v2';out.mkdir(exist_ok=True)
    lp=out/(key+'-poppler-layout.json.gzip');wp=out/(key+'-mupdf-words.json.gzip')
    if not lp.exists():
        text=subprocess.check_output(['pdftotext','-layout','-enc','UTF-8',str(source),'-']).decode()
        raw=gzip.compress(json.dumps({'sourceSha256':spec['sourceSha256'],'method':'Poppler pdftotext -layout -enc UTF-8','pages':text.split('\f')[:-1]},ensure_ascii=False,separators=(',',':')).encode(),mtime=0);lp.write_bytes(raw)
    if not wp.exists():
        d=fitz.open(source);pages=[];probes=[]
        for n,p in enumerate(d):
            flags=[]
            for trace in p.get_texttrace():
                text=''.join(chr(c[0]) for c in trace['chars'])
                if text.strip() and (trace['type']==3 or trace['opacity']<.99 or all(v>.95 for v in trace['color'])):flags.append({'type':trace['type'],'opacity':trace['opacity'],'color':trace['color'],'text':text,'bbox':trace['bbox']})
            pages.append({'physicalPage':n+1,'width':p.rect.width,'height':p.rect.height,'words':[list(w) for w in p.get_text('words')],'unpaintedWhiteOrTransparentText':flags})
            text=p.get_text();probes.append({'physicalPage':n+1,'textLength':len(text),'text':text})
        raw=gzip.compress(json.dumps({'sourceSha256':spec['sourceSha256'],'method':'MuPDF positioned word rectangles with painting guards','pages':pages},ensure_ascii=False,separators=(',',':')).encode(),mtime=0);wp.write_bytes(raw)
        ep=AREA/'native-text-probes-v2'/(spec['sourceSha256']+'.json.gzip');ep.parent.mkdir(exist_ok=True);ep.write_bytes(gzip.compress(json.dumps({'sourceSha256':spec['sourceSha256'],'pages':probes},ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    ep=AREA/'native-text-probes-v2'/(spec['sourceSha256']+'.json.gzip');probes=json.loads(gzip.decompress(ep.read_bytes()))['pages']
    summary={'key':key,'sourceSha256':spec['sourceSha256'],'execution':'Each PDF accessed within an isolated worker process; no shared-process PyMuPDF threads','popplerLayout':{'path':str(lp.relative_to(ROOT)),'sha256':sha(lp.read_bytes())},'mupdfWords':{'path':str(wp.relative_to(ROOT)),'sha256':sha(wp.read_bytes())},'textProbe':{'path':str(ep.relative_to(ROOT)),'sha256':sha(ep.read_bytes())},'nativeCharacters':sum(p['textLength'] for p in probes),'imageOnlyPages':[p['physicalPage'] for p in probes if p['textLength']<30]}
    print(json.dumps(summary),flush=True);return summary

if __name__=='__main__':
    specs=json.loads((AREA/'recovered-employee-originals.json').read_bytes())
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:result=list(pool.map(one,specs))
    (AREA/'native-reader-evidence-index-v2.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    by={x['sourceSha256']:x for x in result};corrected=[]
    for spec in specs:
        ev=by[spec['sourceSha256']];probe=json.loads(gzip.decompress((ROOT/ev['textProbe']['path']).read_bytes()))['pages'];c=dict(spec)
        c.update(textEvidencePath=ev['textProbe']['path'],textEvidenceSha256=ev['textProbe']['sha256'],nativeCharacters=ev['nativeCharacters'],imageOnlyPages=ev['imageOnlyPages'],nativeFirstPages=[p['text'][:800] for p in probe[:3]],nativeLastPage=probe[-1]['text'][-1200:],execution=ev['execution'])
        corrected.append(c)
    (AREA/'recovered-employee-originals-v2.json').write_text(json.dumps(corrected,ensure_ascii=False,indent=2)+'\n')
