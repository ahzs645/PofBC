#!/usr/bin/env python3
"""Audit native text painting, clipping and later opaque overpaint in isolated processes.

Flags are source-review targets; this audit never adjusts names or amounts and
does not establish that a human has read an original image.
"""
import collections,concurrent.futures,gzip,json,pathlib
import fitz
from gap_health_employees_fetch import ROOT,AREA,sha

def area(r):return max(0,r.width)*max(0,r.height)
def one(spec):
    source=pathlib.Path(spec['retrieval']['cachePath']);assert sha(source.read_bytes())==spec['sourceSha256']
    key=spec['item']['employerSlug']+'-'+spec['item']['candidateYear'].replace('/','-');out=AREA/'visibility-v1';out.mkdir(exist_ok=True);dest=out/(key+'.json.gzip')
    if dest.exists():return {'key':key,'sourceSha256':spec['sourceSha256'],'path':str(dest.relative_to(ROOT)),'sha256':sha(dest.read_bytes())}
    doc=fitz.open(source);pages=[]
    for pn,page in enumerate(doc,1):
        visible=page.rect*page.derotation_matrix;traces=page.get_texttrace();log=page.get_bboxlog();drawings=page.get_drawings(extended=True)
        fills=[{'seqno':d.get('seqno',-1),'bbox':d['rect'],'fill':d.get('fill'),'opacity':d.get('fill_opacity',0)} for d in drawings if d.get('fill') is not None and d.get('fill_opacity',0)>=.95]
        images=[{'seqno':n,'bbox':fitz.Rect(entry[1])} for n,entry in enumerate(log) if entry[0]=='fill-image']
        clips=[{'bbox':list(d['scissor']),'level':d.get('level')} for d in drawings if d.get('type')=='clip' and d.get('scissor')]
        flags=[];chars=0;glyphs=collections.defaultdict(list)
        for trace in traces:
            text=''.join(chr(c[0]) for c in trace['chars']);bbox=fitz.Rect(trace['bbox']);seq=trace['seqno']
            if not text.strip():continue
            chars+=len(text)
            if trace['type']==3 or trace['opacity']<.99 or all(c>.95 for c in trace['color']):flags.append({'kind':'unpainted-transparent-or-white-text','seqno':seq,'text':text,'bbox':list(bbox),'type':trace['type'],'opacity':trace['opacity'],'color':trace['color']})
            clipped=[];covered=[]
            for cp,gid,origin,cb in trace['chars']:
                ch=chr(cp)
                if not ch.strip():continue
                cr=fitz.Rect(cb);ca=area(cr)
                if ca and area(cr&visible)<.99*ca:clipped.append({'character':ch,'bbox':list(cr)})
                for later in fills+images:
                    if later['seqno']<=seq:continue
                    if ca and area(cr&fitz.Rect(later['bbox']))>.2*ca:
                        covered.append({'character':ch,'bbox':list(cr),'laterSeqno':later['seqno'],'laterBbox':list(later['bbox']),'laterFill':later.get('fill'),'laterImage':later in images})
                glyphs[(ch,round(cr.x0,1),round(cr.y0,1),round(cr.x1,1),round(cr.y1,1))].append(seq)
            if clipped:flags.append({'kind':'glyph-outside-visible-page','seqno':seq,'text':text,'bbox':list(bbox),'characters':clipped})
            if covered:flags.append({'kind':'later-opaque-fill-or-image-overlap','seqno':seq,'text':text,'bbox':list(bbox),'characters':covered})
        duplicates=[{'character':g[0],'bbox':list(g[1:]),'seqnos':seqs} for g,seqs in glyphs.items() if len(seqs)>1]
        if duplicates:flags.append({'kind':'same-glyph-same-position-painted-multiple-times','characters':duplicates})
        pages.append({'physicalPage':pn,'rotation':page.rotation,'rotationMatrix':list(page.rotation_matrix),'derotationMatrix':list(page.derotation_matrix),'visibleUnrotatedBox':list(visible),'width':page.rect.width,'height':page.rect.height,'textCharacters':chars,'nativeTextTraces':len(traces),'opaqueFilledPaths':len(fills),'images':len(images),'clipScissors':clips,'flags':flags})
    result={'sourceSha256':spec['sourceSha256'],'execution':'One isolated worker process per PDF; no PyMuPDF thread sharing','checks':['all native text painting modes/opacity/color','glyph boxes against visible page','later opaque filled paths and image overlap','same glyph painted at same position','rotation matrices and clip scissors recorded'],'pages':pages}
    raw=gzip.compress(json.dumps(result,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);dest.write_bytes(raw)
    summary={'key':key,'sourceSha256':spec['sourceSha256'],'path':str(dest.relative_to(ROOT)),'sha256':sha(raw),'pages':len(pages),'pagesWithFlags':sum(bool(p['flags']) for p in pages)};print(json.dumps(summary),flush=True);return summary

if __name__=='__main__':
    specs=json.loads((AREA/'recovered-employee-originals-v2.json').read_bytes())
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:result=list(pool.map(one,specs))
    (AREA/'native-visibility-index-v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
