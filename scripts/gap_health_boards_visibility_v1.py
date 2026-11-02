#!/usr/bin/env python3
"""Inspect original board-page paint, glyph overlap, field edges and visible ink.

These are source diagnostics, not proof that a native transcript matches pixels.
Human source-layout and bounded literal readings remain separately recorded.
"""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_boards'
OUT=ROOT/'research/salaries/gap-fill-health-boards'

def main():
    import fitz
    specs=json.loads((AREA/'source-specs.json').read_bytes());reports=[]
    for spec in specs:
        raw=Path(spec['cachePath']).read_bytes();assert hashlib.sha256(raw).hexdigest()==spec['sha256']
        doc=fitz.open(stream=raw,filetype='pdf');page=doc[spec['page']-1]
        top,bottom=spec['yRange'];pixel=page.get_pixmap(dpi=200,colorspace=fitz.csGRAY,alpha=False);samples=pixel.samples
        invisible=[];nonblack=[];replacement=[];duplicate=defaultdict(list);characters=[]
        for span in page.get_texttrace():
            for char in span['chars']:
                code,glyph,origin,bounds=char
                if code==32:continue
                box=fitz.Rect(bounds)*page.rotation_matrix;cx,cy=(box.x0+box.x1)/2,(box.y0+box.y1)/2
                if not top<=cy<bottom:continue
                relevant=[field for field,(left,right) in spec['fields'].items() if left<=cx<right]
                if not relevant:continue
                entry={'character':chr(code),'bbox':list(box),'fields':relevant,'type':span['type'],'opacity':span['opacity'],'color':span['color'],'sequence':span['seqno']}
                characters.append(entry)
                if span['type']==3 or span['opacity']<0.99:invisible.append(entry)
                if all(v>.94 for v in span['color']):nonblack.append(entry)
                if code==65533:replacement.append(entry)
                duplicate[(code,*[round(v,2) for v in box])].append(entry)
        overprints=[v for v in duplicate.values() if len(v)>1]
        conflicting=[]
        groups=defaultdict(list)
        for c in characters:
            x0,y0,x1,y1=c['bbox'];groups[(round((x0+x1)/2),round((y0+y1)/2))].append(c)
        for group in groups.values():
            if len({c['character'] for c in group})<2:continue
            for i,a in enumerate(group):
                for b in group[i+1:]:
                    if a['character']==b['character']:continue
                    ra,rb=fitz.Rect(a['bbox']),fitz.Rect(b['bbox']);minimum=min(ra.get_area(),rb.get_area())
                    if minimum>0 and (ra & rb).get_area()/minimum>.65:conflicting.append([a,b])
        ink=[];boundary=[];words=0
        for w in page.get_text('words'):
            box=fitz.Rect(w[:4])*page.rotation_matrix;cx,cy=(box.x0+box.x1)/2,(box.y0+box.y1)/2
            if not top<=cy<bottom:continue
            fields=[(name,limits) for name,limits in spec['fields'].items() if limits[0]<=cx<limits[1]]
            if not fields:continue
            if w[4] in spec.get('excludedNameTokens',[]):continue
            words+=1
            for name,(left,right) in fields:
                if box.x0<left-.6 or box.x1>right+.6:boundary.append({'word':w[4],'bbox':list(box),'field':name,'limits':[left,right]})
            scale=200/72;left=max(0,math.floor(box.x0*scale));right=min(pixel.width,math.ceil(box.x1*scale));upper=max(0,math.floor(box.y0*scale));lower=min(pixel.height,math.ceil(box.y1*scale))
            pixels=[samples[y*pixel.stride+x] for y in range(upper,lower) for x in range(left,right)]
            if not pixels or min(pixels)>200:ink.append({'word':w[4],'bbox':list(box),'pixelArea':len(pixels),'minimumGray':min(pixels) if pixels else None})
        entry={'sourceId':spec['id'],'sourceSha256':spec['sha256'],'physicalPage':spec['page'],'pageRotation':page.rotation,'diagnosticRegion':{'yRange':spec['yRange'],'fields':spec['fields']},'nativeCharactersExamined':len(characters),'nativeWordsExamined':words,'ignoredOrLowOpacityCharacters':invisible,'nearWhiteCharacters':nonblack,'unicodeReplacementCharacters':replacement,'identicalGlyphOverprints':overprints,'conflictingGlyphOverprints':conflicting,'nativeWordsCrossingReviewedFieldEdges':boundary,'nativeWordsWithoutDarkRenderedInk':ink,'grayscaleRender':{'dpi':200,'width':pixel.width,'height':pixel.height,'pixelSampleSha256':hashlib.sha256(samples).hexdigest()},'limitation':'Paired native readers can share missing/overprinted text. Paint, overlap, pixel-ink and field-edge diagnostics only identify review targets and do not establish every glyph or row value. Human source-view coverage is recorded separately.'}
        path=AREA/(spec['id']+'-visibility.json');path.write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n');reports.append({'sourceId':spec['id'],'sourceSha256':spec['sha256'],'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'flags':{k:len(entry[k]) for k in ['ignoredOrLowOpacityCharacters','nearWhiteCharacters','unicodeReplacementCharacters','identicalGlyphOverprints','conflictingGlyphOverprints','nativeWordsCrossingReviewedFieldEdges','nativeWordsWithoutDarkRenderedInk']}})
    (AREA/'visibility-manifest.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(reports,indent=2))

if __name__=='__main__':main()
