#!/usr/bin/env python3
"""Render actual first/last salary contexts for independent source-definition review."""
import concurrent.futures,hashlib,json,pathlib
import fitz
from gap_health_employees_fetch import ROOT,AREA,sha

def one(pair):
    spec,context=pair;raw=pathlib.Path(spec['retrieval']['cachePath']).read_bytes();assert sha(raw)==spec['sourceSha256'];doc=fitz.open(stream=raw,filetype='pdf');key=context['key'];out=AREA/'source-review-contexts';out.mkdir(exist_ok=True)
    requested={context['employeePhysicalPages'][0]:'first employee page/internal period and column definitions',context['employeePhysicalPages'][1]:'last employee page/controls/source-specific reconciliation notes'}
    if key=='interior-health-2003-04':requested[6]='actual Hasselback row; matching residual magnitude is not an explanation'
    images=[]
    for pn,purpose in requested.items():
        pix=doc[pn-1].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False);p=out/(key+f'-p{pn:03}.png');pix.save(p)
        images.append({'physicalPage':pn,'purpose':purpose,'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'dpi':144,'method':'Unmodified complete original PDF page; no crop or resampling','rawPixelSha256':sha(pix.samples)})
    return {'key':key,'sourceSha256':spec['sourceSha256'],'images':images}

if __name__=='__main__':
    specs={x['sourceSha256']:x for x in json.loads((AREA/'recovered-employee-originals-v2.json').read_bytes())};contexts=json.loads((AREA/'source-context-review-packet.json').read_bytes())['sources']
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:images=list(pool.map(one,[(specs[x['sourceSha256']],x) for x in contexts]))
    packet={'status':'awaiting-independent-context-image-review','candidateValuesPresent':True,'reviewScope':'All65internally printed periods/definitions and actual first/last salary-page images. This is separate from field-by-field image correction and not a claim of manual reading of every row.','noOutreach':True,'contextTextPacket':{'path':str((AREA/'source-context-review-packet.json').relative_to(ROOT)),'sha256':sha((AREA/'source-context-review-packet.json').read_bytes())},'sources':images}
    p=AREA/'source-context-image-index.json';p.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'packet':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'sources':len(images),'images':sum(len(x['images']) for x in images)}))
