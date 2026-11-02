#!/usr/bin/env python3
"""Prepare source-only row targets affected by actual native clipping differences."""
import gzip,json,pathlib
import fitz
from gap_health_employees_fetch import ROOT,AREA,sha

def main():
    specs=json.loads((AREA/'recovered-employee-originals-v2.json').read_bytes());by={x['sourceSha256']:x for x in specs};prior=json.loads((AREA/'source-review-packets/reader-disagreements-001/packet.json').read_bytes())['targets'];previous={}
    for x in prior:
        scale=x['image']['wholePageDpi']/72;y0=x['image']['integerCropPixelBox'][1];a,b=x['image']['targetRowVerticalPixelRange'];cy=(y0+(a+b)/2)/scale;previous.setdefault((x['sourceKey'],x['physicalPage']),[]).append(cy)
    targets=[]
    for source in json.loads((AREA/'native-clip-pixel-audit-index-v2.json').read_bytes()):
        audit=json.loads(gzip.decompress((ROOT/source['path']).read_bytes()))
        for page in audit['pages']:
            for row in page['rowsWithPixelChanges']:
                bbox=row['bbox'];cy=(bbox[1]+bbox[3])/2
                if any(abs(cy-y)<2.5 for y in previous.get((source['key'],page['physicalPage']),[])):continue
                targets.append({'sourceKey':source['key'],'sourceSha256':source['sourceSha256'],'physicalPage':page['physicalPage'],'sourceRowOnPage':row['sourceRowOnPage'],'bbox':bbox,'changedPixelsAt144Dpi':row['changedPixels'],'auditPath':source['path'],'auditSha256':source['sha256']})
    targets.sort(key=lambda x:(x['sourceKey'],x['physicalPage'],x['bbox'][1]));out=AREA/'source-review-packets/clip-effects-001';out.mkdir(parents=True,exist_ok=True);docs={};entries=[];lastpage=None;pix=None
    for n,t in enumerate(targets,1):
        spec=by[t['sourceSha256']];key=t['sourceKey'];pn=t['physicalPage']
        if key not in docs:docs[key]=fitz.open(spec['retrieval']['cachePath'])
        page=docs[key][pn-1]
        if lastpage!=(key,pn):pix=page.get_pixmap(matrix=fitz.Matrix(4,4),alpha=False);lastpage=(key,pn)
        cy=(t['bbox'][1]+t['bbox'][3])/2;bounds=fitz.IRect(40*4,max(0,int((cy-18)*4)),int((page.rect.width-20)*4),min(pix.height,int((cy+18)*4)));crop=fitz.Pixmap(pix.colorspace,bounds,False);crop.copy(pix,bounds);p=out/f'target-{n:03}.png';crop.save(p)
        entries.append({**{k:v for k,v in t.items() if k!='bbox'},'id':f'health-clip-001-{n:03}','sourceUrl':spec['url'],'sourceCachePath':spec['retrieval']['cachePath'],'candidateValuesWithheld':True,'requestedFields':['name','remuneration','expenses'],'image':{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'wholePageRawPixelSha256':sha(pix.samples),'wholePageDpi':288,'integerCropPixelBox':list(bounds),'targetRowVerticalPixelRange':[round(t['bbox'][1]*4-bounds.y0),round(t['bbox'][3]*4-bounds.y0)]}})
    packet={'status':'awaiting-independent-original-image-transcription','candidateValuesWithheld':True,'noOutreach':True,'purpose':'Read the original visible target row. Actual original-vs-declipped pixels differ in its native-reader field region; even tiny changes remain explicit review targets. Do not infer extra hidden letters or balance money. Report finite ambiguity or literal visible clipping.','sourceRendering':'Unmodified complete original PDF page at288dpi, then integer crop; no PDF clip or resampling. Target center row identified by vertical pixel range; adjacent rows are context.','priorPacketTargetsExcluded':len(prior),'targets':entries};p=out/'packet.json';p.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'packet':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'targets':len(entries)}))

if __name__=='__main__':main()
